"""
core/parameter_tuner.py
-----------------------
Atlas Parameter Tuner — Self-adapting strategy configuration engine.

Reads closed-trade history from the database, evaluates per-strategy
performance metrics, and adjusts parameters in config/strategies.yaml
when performance falls outside acceptable thresholds.

WARNING: This module writes to config/strategies.yaml using yaml.safe_dump.
PyYAML does not preserve comments. The first write will strip all inline
comments from strategies.yaml. If comment preservation is required, install
ruamel.yaml and replace the _load_yaml / _save_yaml methods accordingly.

Safety bounds are hard-coded and cannot be exceeded regardless of the
number of consecutive adjustments applied. All changes are recorded in a
TuningRecord and logged before being written to disk. Use dry_run=True to
preview changes without modifying any file.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import and_

from db.database import get_session
from db.models import Trade

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent.parent
_STRATEGIES_YAML = _ROOT / "config" / "strategies.yaml"

# ─────────────────────────────────────────────────────────────────────────────
#  Safety bounds — hard limits that can NEVER be exceeded
# ─────────────────────────────────────────────────────────────────────────────

_BOUNDS: dict[str, tuple[float, float]] = {
    "atr_stop_mult":  (1.0, 5.0),
    "rr_ratio":       (1.5, 6.0),
    "rr_min":         (1.5, 6.0),   # some strategies use rr_min instead of rr_ratio
    "risk_per_trade": (0.5, 1.5),
    # conviction_threshold is not a YAML field — it maps to min_conviction in the
    # engine and is tracked per-strategy in a synthetic key for tuning purposes.
    "conviction_threshold": (0.2, 0.7),
}

# Step sizes for each adjustment direction
_STEP: dict[str, float] = {
    "atr_stop_mult":        0.5,
    "rr_ratio":             0.5,
    "rr_min":               0.5,
    "risk_per_trade":       0.25,
    "conviction_threshold": 0.05,
}

# ─────────────────────────────────────────────────────────────────────────────
#  Tuning thresholds
# ─────────────────────────────────────────────────────────────────────────────

_WIN_RATE_LOW:         float = 0.25   # below → widen stops
_RR_RATIO_LOW:        float = 1.5    # avg_win / avg_loss below → increase RR target
_TRADE_COUNT_HIGH:    int   = 50     # trades/month above + low WR → tighten conviction
_TRADE_COUNT_LOW:     int   = 3      # trades/month below → loosen conviction
_MAX_DRAWDOWN_THRESH: float = 8.0    # % — above → reduce risk_per_trade
_MIN_TRADES_TO_TUNE:  int   = 5      # minimum closed trades before any adjustment


# ─────────────────────────────────────────────────────────────────────────────
#  Data structures
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class StrategyMetrics:
    """Computed performance metrics for a single strategy over the look-back window."""

    strategy_name: str
    trade_count: int
    win_rate: float           # 0.0 – 1.0
    avg_win_pct: float        # mean P&L % of winning trades
    avg_loss_pct: float       # mean abs P&L % of losing trades (always >= 0)
    trades_per_month: float
    max_drawdown_pct: float   # peak-to-trough drawdown across the window (positive number)


@dataclass
class TuningRecord:
    """A single parameter adjustment decision."""

    strategy_name: str
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __str__(self) -> str:
        return (
            f"[{self.timestamp.isoformat(timespec='seconds')}] "
            f"{self.strategy_name}.{self.parameter_name}: "
            f"{self.old_value:.4g} → {self.new_value:.4g} | {self.reason}"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  ParameterTuner
# ─────────────────────────────────────────────────────────────────────────────


class ParameterTuner:
    """
    Reads closed trade history and automatically adjusts strategy parameters
    in config/strategies.yaml based on performance rules.

    Parameters
    ----------
    dry_run:
        When True the tuner computes all adjustments and logs them but does
        NOT write any changes to strategies.yaml. Safe to use in CI or for
        previewing what would change.
    lookback_days:
        Number of calendar days of closed-trade history to evaluate.
        Defaults to 30 (approximately one month).
    """

    def __init__(self, dry_run: bool = False, lookback_days: int = 30) -> None:
        self.dry_run = dry_run
        self.lookback_days = lookback_days

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def tune_all(self) -> list[TuningRecord]:
        """
        Main entry point. Runs the full tuning cycle:

        1. Load strategies.yaml
        2. Query the last ``lookback_days`` of closed trades per strategy
        3. Compute performance metrics
        4. Apply tuning rules to produce TuningRecord objects
        5. Write adjusted parameters back to YAML (unless dry_run)
        6. Return all TuningRecord objects (empty list if nothing changed)
        """
        yaml_config = self._load_yaml()
        strategies: dict[str, Any] = yaml_config.get("strategies", {})

        all_records: list[TuningRecord] = []
        cutoff = datetime.now(UTC) - timedelta(days=self.lookback_days)

        # Process each strategy independently
        for strategy_name in strategies:
            trades = self._fetch_closed_trades(strategy_name, cutoff)
            if len(trades) < _MIN_TRADES_TO_TUNE:
                logger.debug(
                    "ParameterTuner | %s: only %d closed trades in window, skipping.",
                    strategy_name,
                    len(trades),
                )
                continue

            metrics = self._compute_metrics(strategy_name, trades, cutoff)
            records = self._apply_rules(strategies[strategy_name], metrics)
            all_records.extend(records)

        if not all_records:
            logger.info("ParameterTuner | tune_all complete — no parameters adjusted.")
            return all_records

        # Log every change before touching disk
        for rec in all_records:
            logger.info("ParameterTuner | %s", rec)

        if self.dry_run:
            logger.info(
                "ParameterTuner | dry_run=True — %d change(s) NOT written to disk.",
                len(all_records),
            )
        else:
            self._save_yaml(yaml_config)
            logger.info(
                "ParameterTuner | %d parameter change(s) written to %s.",
                len(all_records),
                _STRATEGIES_YAML,
            )

        return all_records

    # ------------------------------------------------------------------ #
    #  Database queries                                                    #
    # ------------------------------------------------------------------ #

    def _fetch_closed_trades(
        self,
        strategy_name: str,
        cutoff: datetime,
    ) -> list[Trade]:
        """
        Return all closed trades for ``strategy_name`` on or after ``cutoff``.
        A closed trade has a non-null ``closed_at`` and a non-null ``pnl_pct``.
        """
        with get_session() as session:
            trades: list[Trade] = (
                session.query(Trade)
                .filter(
                    and_(
                        Trade.strategy == strategy_name,
                        Trade.closed_at.isnot(None),
                        Trade.pnl_pct.isnot(None),
                        Trade.closed_at >= cutoff,
                    )
                )
                .order_by(Trade.closed_at.asc())
                .all()
            )
            # Detach from session so they can be used after the context exits.
            # We only need primitive-typed attributes so expunge is sufficient.
            session.expunge_all()
            return trades

    # ------------------------------------------------------------------ #
    #  Metrics computation                                                 #
    # ------------------------------------------------------------------ #

    def _compute_metrics(
        self,
        strategy_name: str,
        trades: list[Trade],
        cutoff: datetime,
    ) -> StrategyMetrics:
        """
        Derive win rate, average win/loss, trade frequency, and max drawdown
        from a list of closed Trade ORM objects.
        """
        pnl_pcts: list[float] = [t.pnl_pct for t in trades]  # type: ignore[misc]
        # pnl_pct is guaranteed non-null by the query filter above.

        wins  = [p for p in pnl_pcts if p > 0.0]
        losses = [p for p in pnl_pcts if p <= 0.0]

        win_rate   = len(wins) / len(pnl_pcts) if pnl_pcts else 0.0
        avg_win    = sum(wins) / len(wins) if wins else 0.0
        avg_loss   = abs(sum(losses) / len(losses)) if losses else 0.0

        # Approximate trades-per-month based on the actual window used
        days_in_window = max(
            1.0,
            (datetime.now(UTC) - cutoff).total_seconds() / 86_400,
        )
        trades_per_month = len(trades) / days_in_window * 30.0

        max_drawdown = self._compute_max_drawdown(pnl_pcts)

        return StrategyMetrics(
            strategy_name=strategy_name,
            trade_count=len(trades),
            win_rate=win_rate,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            trades_per_month=trades_per_month,
            max_drawdown_pct=max_drawdown,
        )

    @staticmethod
    def _compute_max_drawdown(pnl_pcts: list[float]) -> float:
        """
        Compute peak-to-trough max drawdown across the ordered sequence of
        trade P&L percentages using a cumulative equity curve approach.

        Returns a positive number representing the worst drawdown magnitude.
        """
        if not pnl_pcts:
            return 0.0

        equity = 100.0  # start from a normalised base
        peak   = equity
        max_dd = 0.0

        for pct in pnl_pcts:
            equity *= 1.0 + pct / 100.0
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100.0
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd

    # ------------------------------------------------------------------ #
    #  Tuning rules                                                        #
    # ------------------------------------------------------------------ #

    def _apply_rules(
        self,
        strategy_config: dict[str, Any],
        metrics: StrategyMetrics,
    ) -> list[TuningRecord]:
        """
        Evaluate all tuning rules against ``metrics`` and return the list of
        TuningRecord objects representing every parameter that changed.

        The strategy_config dict is mutated in-place so the caller can
        serialise the updated YAML in a single pass.
        """
        records: list[TuningRecord] = []
        params: dict[str, Any] = strategy_config.get("parameters", {})

        # ── Rule A: low win rate → widen stops ───────────────────────────
        if metrics.win_rate < _WIN_RATE_LOW:
            rec = self._adjust_parameter(
                strategy_config=strategy_config,
                params=params,
                param_key="atr_stop_mult",
                delta=+_STEP["atr_stop_mult"],
                reason=(
                    f"win rate {metrics.win_rate:.1%} < {_WIN_RATE_LOW:.0%} threshold "
                    f"— widening ATR stop multiplier to reduce premature stop-outs"
                ),
                strategy_name=metrics.strategy_name,
            )
            if rec:
                records.append(rec)

        # ── Rule B: poor risk-reward ratio → increase RR target ──────────
        rr_actual = (
            metrics.avg_win_pct / metrics.avg_loss_pct
            if metrics.avg_loss_pct > 0.0
            else None
        )
        if rr_actual is not None and rr_actual < _RR_RATIO_LOW:
            # Adjust whichever RR key exists in the parameters block
            for rr_key in ("rr_ratio", "rr_min"):
                if rr_key in params:
                    rec = self._adjust_parameter(
                        strategy_config=strategy_config,
                        params=params,
                        param_key=rr_key,
                        delta=+_STEP[rr_key],
                        reason=(
                            f"avg win/loss ratio {rr_actual:.2f} < {_RR_RATIO_LOW} "
                            f"— increasing {rr_key} to demand higher reward per unit risk"
                        ),
                        strategy_name=metrics.strategy_name,
                    )
                    if rec:
                        records.append(rec)

        # ── Rule C: overtrading with poor results → tighten conviction ────
        if (
            metrics.trades_per_month > _TRADE_COUNT_HIGH
            and metrics.win_rate < _WIN_RATE_LOW
        ):
            rec = self._adjust_conviction_threshold(
                strategy_config=strategy_config,
                delta=+_STEP["conviction_threshold"],
                reason=(
                    f"{metrics.trades_per_month:.0f} trades/month > {_TRADE_COUNT_HIGH} "
                    f"with win rate {metrics.win_rate:.1%} — raising conviction threshold "
                    f"to filter marginal entries"
                ),
                strategy_name=metrics.strategy_name,
            )
            if rec:
                records.append(rec)

        # ── Rule D: undertrading → loosen conviction ─────────────────────
        elif metrics.trades_per_month < _TRADE_COUNT_LOW:
            rec = self._adjust_conviction_threshold(
                strategy_config=strategy_config,
                delta=-_STEP["conviction_threshold"],
                reason=(
                    f"only {metrics.trades_per_month:.1f} trades/month < {_TRADE_COUNT_LOW} "
                    f"— lowering conviction threshold to allow more entries"
                ),
                strategy_name=metrics.strategy_name,
            )
            if rec:
                records.append(rec)

        # ── Rule E: excessive drawdown → reduce per-trade risk ────────────
        if metrics.max_drawdown_pct > _MAX_DRAWDOWN_THRESH:
            old_risk = float(strategy_config.get("risk_per_trade", 1.0))
            new_risk = self._clamp(
                old_risk - _STEP["risk_per_trade"],
                "risk_per_trade",
            )
            if new_risk != old_risk:
                strategy_config["risk_per_trade"] = new_risk
                records.append(
                    TuningRecord(
                        strategy_name=metrics.strategy_name,
                        parameter_name="risk_per_trade",
                        old_value=old_risk,
                        new_value=new_risk,
                        reason=(
                            f"max drawdown {metrics.max_drawdown_pct:.1f}% > "
                            f"{_MAX_DRAWDOWN_THRESH}% threshold — reducing risk per trade"
                        ),
                    )
                )

        return records

    # ------------------------------------------------------------------ #
    #  Parameter adjustment helpers                                        #
    # ------------------------------------------------------------------ #

    def _adjust_parameter(
        self,
        strategy_config: dict[str, Any],
        params: dict[str, Any],
        param_key: str,
        delta: float,
        reason: str,
        strategy_name: str,
    ) -> TuningRecord | None:
        """
        Apply ``delta`` to ``param_key`` inside ``params``, clamping to safety
        bounds. Returns a TuningRecord if the value actually changed, else None.
        """
        if param_key not in params:
            return None

        old_val = float(params[param_key])
        raw_new = old_val + delta
        new_val = self._clamp(raw_new, param_key)

        if new_val == old_val:
            logger.debug(
                "ParameterTuner | %s.parameters.%s already at bound (%.4g), no change.",
                strategy_name,
                param_key,
                old_val,
            )
            return None

        params[param_key] = new_val
        return TuningRecord(
            strategy_name=strategy_name,
            parameter_name=f"parameters.{param_key}",
            old_value=old_val,
            new_value=new_val,
            reason=reason,
        )

    def _adjust_conviction_threshold(
        self,
        strategy_config: dict[str, Any],
        delta: float,
        reason: str,
        strategy_name: str,
    ) -> TuningRecord | None:
        """
        Adjust the per-strategy conviction threshold stored under
        ``strategy_config["conviction_threshold"]``.

        This key is optional in the YAML (it supplements the global
        min_conviction from settings). If it does not yet exist, it is
        initialised from the midpoint of the allowed range (0.3) before
        the delta is applied.
        """
        key = "conviction_threshold"
        lo, hi = _BOUNDS[key]
        midpoint = round((lo + hi) / 2.0, 2)

        old_val = float(strategy_config.get(key, midpoint))
        new_val = self._clamp(old_val + delta, key)

        if new_val == old_val:
            logger.debug(
                "ParameterTuner | %s.conviction_threshold already at bound (%.4g).",
                strategy_name,
                old_val,
            )
            return None

        strategy_config[key] = new_val
        return TuningRecord(
            strategy_name=strategy_name,
            parameter_name=key,
            old_value=old_val,
            new_value=new_val,
            reason=reason,
        )

    @staticmethod
    def _clamp(value: float, param_key: str) -> float:
        """
        Clamp ``value`` to the safety bounds defined for ``param_key``.
        Returns ``value`` unchanged if ``param_key`` has no registered bounds.
        """
        if param_key not in _BOUNDS:
            return value
        lo, hi = _BOUNDS[param_key]
        return round(max(lo, min(hi, value)), 4)

    # ------------------------------------------------------------------ #
    #  YAML I/O                                                            #
    # ------------------------------------------------------------------ #

    def _load_yaml(self) -> dict[str, Any]:
        """
        Load strategies.yaml and return the parsed dict.
        Raises FileNotFoundError if the file is missing.
        """
        if not _STRATEGIES_YAML.exists():
            raise FileNotFoundError(
                f"strategies.yaml not found at {_STRATEGIES_YAML}"
            )
        with _STRATEGIES_YAML.open("r", encoding="utf-8") as fh:
            data: dict[str, Any] = yaml.safe_load(fh) or {}
        return data

    def _save_yaml(self, config: dict[str, Any]) -> None:
        """
        Write the (modified) config dict back to strategies.yaml.

        NOTE: yaml.safe_dump does not preserve comments. All inline comments
        in the original file will be lost after the first write. If comment
        preservation is critical, install ruamel.yaml and swap this method.
        """
        with _STRATEGIES_YAML.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(
                config,
                fh,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=88,
            )

    # ------------------------------------------------------------------ #
    #  Reporting helpers                                                   #
    # ------------------------------------------------------------------ #

    def report(self, records: list[TuningRecord]) -> str:
        """
        Format a human-readable summary of all tuning changes.
        Suitable for sending via Telegram alert or writing to a log file.
        """
        if not records:
            return "ParameterTuner: no parameter changes applied."

        lines = [
            f"ParameterTuner — {len(records)} adjustment(s) "
            f"({'DRY RUN' if self.dry_run else 'APPLIED'}):",
        ]
        for rec in records:
            lines.append(
                f"  {rec.strategy_name}.{rec.parameter_name}: "
                f"{rec.old_value:.4g} → {rec.new_value:.4g}"
                f"\n    Reason: {rec.reason}"
            )
        return "\n".join(lines)
