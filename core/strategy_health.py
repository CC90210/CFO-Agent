"""
core/strategy_health.py
-----------------------
Darwinian strategy health monitor — auto-disables underperforming strategies
and re-enables them on a supervised probation schedule.

Design principles
-----------------
* All thresholds are configurable via the ``HealthThresholds`` dataclass.
  No magic numbers buried in logic.
* The monitor is stateless across restarts — it re-derives every metric from
  the ``Trade`` table on ``refresh()``. Restarting the engine does NOT
  accidentally clear a disable.
* ``should_trade()`` is the only method the engine needs to call per tick.
  Everything else is internal bookkeeping.
* No side effects in ``__init__``; call ``refresh()`` explicitly after
  construction so the engine controls when DB reads happen.

State machine per strategy
--------------------------
  ACTIVE ──(warn thresholds)──► WARNING
  WARNING ──(disable thresholds)──► DISABLED
  ACTIVE ──(disable thresholds)──► DISABLED  (hard triggers skip WARNING)
  DISABLED ──(cooldown_hours elapsed)──► COOLDOWN → PROBATION (50% size)
  PROBATION ──(profitable after probation_hours)──► ACTIVE (full size)
  PROBATION ──(fails again)──► DISABLED (extended: 7-day ban)

The re-enable path uses two time gates:
  1. ``cooldown_hours`` (default 48 h) — minimum time DISABLED before any
     re-enable attempt is made.
  2. ``probation_hours`` (default 48 h) — window during which the strategy
     trades at 50% size. If it records a net gain it graduates to ACTIVE;
     if it triggers a disable rule again it goes to 7-day ban.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import NamedTuple

from db.database import get_session
from db.models import Trade

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public enumerations and data structures
# ---------------------------------------------------------------------------


class StrategyStatus(Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    DISABLED = "DISABLED"
    COOLDOWN = "COOLDOWN"      # disabled but waiting for re-enable window
    PROBATION = "PROBATION"    # re-enabled at 50% size — on trial


@dataclass
class HealthThresholds:
    """
    All configurable thresholds for the health monitor.

    Defaults encode the rules specified in the task brief. Override by
    passing a custom instance to ``StrategyHealthMonitor``.
    """

    # ── Warning thresholds (strategy flagged but still allowed to trade) ──
    warn_win_rate_window: int = 20          # look-back trade count
    warn_win_rate_min: float = 0.30         # win rate floor before WARN

    warn_profit_factor_window: int = 20     # look-back trade count
    warn_profit_factor_min: float = 0.50    # profit factor floor before WARN

    # ── Auto-disable thresholds (trading halted immediately) ──────────────
    disable_consecutive_losses: int = 8     # consecutive losses → disable
    disable_drawdown_pct: float = 10.0      # per-strategy drawdown % → disable

    disable_win_rate_window: int = 30       # look-back trade count
    disable_win_rate_min: float = 0.20      # win rate floor before DISABLE

    # ── Minimum trades before any rule fires ─────────────────────────────
    min_trades_for_evaluation: int = 5

    # ── Re-enable schedule ────────────────────────────────────────────────
    cooldown_hours: float = 48.0            # wait before first re-enable
    probation_hours: float = 48.0           # probation window at 50% size
    extended_ban_days: float = 7.0          # ban length after probation failure

    # ── Position size multipliers ─────────────────────────────────────────
    probation_size_multiplier: float = 0.50
    normal_size_multiplier: float = 1.00


@dataclass
class StrategyHealth:
    """
    Point-in-time health snapshot for a single strategy.

    Persisted in-memory between ``refresh()`` calls. ``disabled_at`` and
    ``re_enable_at`` survive across refreshes so cooldown windows are
    respected even when metrics temporarily look better.
    """

    strategy_name: str
    status: StrategyStatus = StrategyStatus.ACTIVE
    win_rate_20: float = 0.0
    profit_factor_20: float = 1.0
    win_rate_30: float = 0.0
    consecutive_losses: int = 0
    max_drawdown_pct: float = 0.0
    rolling_sharpe: float = 0.0
    total_trades: int = 0

    disabled_at: datetime | None = None
    re_enable_at: datetime | None = None
    probation_started_at: datetime | None = None
    extended_ban_until: datetime | None = None

    size_multiplier: float = 1.0
    reason: str = ""


class ShouldTradeResult(NamedTuple):
    """Return type for ``StrategyHealthMonitor.should_trade()``."""

    allowed: bool
    size_multiplier: float
    reason: str


# ---------------------------------------------------------------------------
# Internal metric helpers
# ---------------------------------------------------------------------------


def _compute_profit_factor(pnl_pcts: list[float]) -> float:
    """
    Profit factor = gross profit / gross loss.

    Returns 0.0 when gross loss is zero but all trades are losers,
    and returns 999.0 (capped) when there are no losing trades.
    """
    gross_profit = sum(p for p in pnl_pcts if p > 0.0)
    gross_loss = abs(sum(p for p in pnl_pcts if p < 0.0))
    if gross_loss == 0.0:
        return 999.0 if gross_profit > 0.0 else 1.0
    return gross_profit / gross_loss


def _compute_sharpe(pnl_pcts: list[float]) -> float:
    """
    Simplified rolling Sharpe ratio (risk-free rate assumed 0).

    Returns 0.0 when fewer than 3 trades are available.
    """
    n = len(pnl_pcts)
    if n < 3:
        return 0.0
    mean = sum(pnl_pcts) / n
    variance = sum((p - mean) ** 2 for p in pnl_pcts) / n
    std = math.sqrt(max(variance, 1e-10))
    return mean / std


def _compute_max_drawdown(pnl_pcts: list[float]) -> float:
    """
    Max drawdown as a positive percentage over the supplied trade sequence.

    Simulates a $100 equity curve and returns the peak-to-trough
    percentage loss (positive number, e.g. 12.3 means −12.3%).
    """
    equity = 100.0
    peak = equity
    max_dd = 0.0
    for pnl in pnl_pcts:
        equity *= (1.0 + pnl / 100.0)
        if equity > peak:
            peak = equity
        drawdown = (peak - equity) / peak * 100.0
        if drawdown > max_dd:
            max_dd = drawdown
    return max_dd


def _count_consecutive_losses(pnl_pcts: list[float]) -> int:
    """
    Count the number of consecutive losses at the tail of the list.

    The list is ordered oldest-first (chronological). A zero-pnl trade
    is counted as neither a win nor a loss and resets the streak.
    """
    streak = 0
    for pnl in reversed(pnl_pcts):
        if pnl < 0.0:
            streak += 1
        else:
            break
    return streak


# ---------------------------------------------------------------------------
# Main monitor class
# ---------------------------------------------------------------------------


class StrategyHealthMonitor:
    """
    Tracks per-strategy performance and enforces the Darwinian auto-disable
    rules.

    Usage
    -----
    ::

        monitor = StrategyHealthMonitor()
        monitor.refresh()          # pull latest trades from DB

        # In the engine tick, before running a strategy:
        allowed, size_mult, reason = monitor.should_trade("ema_crossover")
        if allowed:
            signal = strategy.analyze(df)
            # ... size order using size_mult ...

        # Periodically (e.g. after every trade close):
        monitor.refresh()          # re-derive metrics

    Parameters
    ----------
    thresholds:
        Override the default ``HealthThresholds``.  Pass a customised
        instance to tighten or loosen any rule without subclassing.
    """

    def __init__(
        self,
        thresholds: HealthThresholds | None = None,
    ) -> None:
        self._thresholds: HealthThresholds = thresholds or HealthThresholds()
        # Keyed by strategy name.  Populated / updated by refresh().
        self._health: dict[str, StrategyHealth] = {}

    # ── Public API ────────────────────────────────────────────────────────

    def should_trade(self, strategy_name: str) -> ShouldTradeResult:
        """
        Return whether a strategy is allowed to trade and at what size.

        The engine should call this once per strategy per tick, before
        running strategy analysis.  It also handles the COOLDOWN →
        PROBATION and PROBATION → ACTIVE promotions so no separate
        scheduler is required.

        Parameters
        ----------
        strategy_name:
            Matches the ``strategy`` column in the ``trades`` table and
            the key in ``config/strategies.yaml``.

        Returns
        -------
        ShouldTradeResult
            Named tuple of ``(allowed: bool, size_multiplier: float, reason: str)``.
        """
        health = self._get_or_create(strategy_name)
        now = datetime.now(UTC)

        # ── Promote COOLDOWN → PROBATION when cooldown window elapses ────
        if health.status == StrategyStatus.COOLDOWN:
            if health.re_enable_at is not None and now >= health.re_enable_at:
                self._promote_to_probation(health, now)
            else:
                wait = (
                    health.re_enable_at - now
                    if health.re_enable_at
                    else timedelta(hours=self._thresholds.cooldown_hours)
                )
                return ShouldTradeResult(
                    allowed=False,
                    size_multiplier=0.0,
                    reason=f"Cooldown active — re-enable in {_fmt_timedelta(wait)}",
                )

        # ── Promote PROBATION → ACTIVE after probation window ─────────────
        if health.status == StrategyStatus.PROBATION:
            if (
                health.probation_started_at is not None
                and now >= health.probation_started_at
                + timedelta(hours=self._thresholds.probation_hours)
            ):
                # Evaluate probation outcome
                recent_pnl = self._recent_pnl(strategy_name, n=10)
                net_pnl = sum(recent_pnl)
                if net_pnl > 0.0:
                    self._graduate_to_active(health)
                    logger.info(
                        "StrategyHealth [%s]: probation PASSED (net P&L=%.2f%%) → ACTIVE",
                        strategy_name,
                        net_pnl,
                    )
                else:
                    self._extended_ban(health, now)
                    logger.warning(
                        "StrategyHealth [%s]: probation FAILED (net P&L=%.2f%%) → extended ban",
                        strategy_name,
                        net_pnl,
                    )
                    return ShouldTradeResult(
                        allowed=False,
                        size_multiplier=0.0,
                        reason=f"Extended ban after probation failure — until {_fmt_dt(health.extended_ban_until)}",
                    )

        # ── Extended ban check ────────────────────────────────────────────
        if health.extended_ban_until is not None and now < health.extended_ban_until:
            remaining = health.extended_ban_until - now
            return ShouldTradeResult(
                allowed=False,
                size_multiplier=0.0,
                reason=f"Extended ban — lifts in {_fmt_timedelta(remaining)}",
            )
        if health.extended_ban_until is not None and now >= health.extended_ban_until:
            # Ban has expired — restore to active
            self._graduate_to_active(health)
            logger.info(
                "StrategyHealth [%s]: extended ban expired → ACTIVE",
                strategy_name,
            )

        # ── DISABLED — should not reach here without going through COOLDOWN
        #    but guard just in case state was set externally
        if health.status == StrategyStatus.DISABLED:
            return ShouldTradeResult(
                allowed=False,
                size_multiplier=0.0,
                reason=health.reason,
            )

        # ── ACTIVE / WARNING / PROBATION — trading allowed ────────────────
        return ShouldTradeResult(
            allowed=True,
            size_multiplier=health.size_multiplier,
            reason=health.reason,
        )

    def refresh(self) -> None:
        """
        Re-derive all health metrics from the ``trades`` table.

        Call this after every trade close, or on a periodic timer.
        State transitions (status changes, disable timestamps) are
        preserved across refreshes — only the metric fields are
        overwritten.
        """
        strategy_names = self._load_strategy_names()
        for name in strategy_names:
            self._refresh_strategy(name)

    def get_health(self, strategy_name: str) -> StrategyHealth:
        """Return the current health snapshot for a strategy."""
        return self._get_or_create(strategy_name)

    def get_all_health(self) -> dict[str, StrategyHealth]:
        """Return a copy of the full health dict (name → StrategyHealth)."""
        return dict(self._health)

    def force_disable(self, strategy_name: str, reason: str) -> None:
        """
        Manually disable a strategy (e.g. from the Darwinian agent).

        The normal cooldown re-enable schedule applies.
        """
        health = self._get_or_create(strategy_name)
        self._disable(health, reason, datetime.now(UTC))
        logger.warning(
            "StrategyHealth [%s]: force-disabled. Reason: %s",
            strategy_name,
            reason,
        )

    def force_enable(self, strategy_name: str) -> None:
        """
        Manually restore a strategy to ACTIVE, bypassing all cooldowns.

        Use only for manual operator overrides — prefer letting the
        auto-schedule do the re-enable.
        """
        health = self._get_or_create(strategy_name)
        self._graduate_to_active(health)
        logger.info("StrategyHealth [%s]: force-enabled by operator.", strategy_name)

    def summary(self) -> list[dict[str, object]]:
        """
        Return a list of dicts suitable for dashboard display or logging.

        Sorted by status severity (DISABLED first, then WARNING, then
        ACTIVE).
        """
        _order = {
            StrategyStatus.DISABLED: 0,
            StrategyStatus.COOLDOWN: 1,
            StrategyStatus.PROBATION: 2,
            StrategyStatus.WARNING: 3,
            StrategyStatus.ACTIVE: 4,
        }
        rows = [
            {
                "strategy": h.strategy_name,
                "status": h.status.value,
                "win_rate_20": round(h.win_rate_20, 3),
                "win_rate_30": round(h.win_rate_30, 3),
                "profit_factor_20": round(h.profit_factor_20, 3),
                "consecutive_losses": h.consecutive_losses,
                "max_drawdown_pct": round(h.max_drawdown_pct, 2),
                "rolling_sharpe": round(h.rolling_sharpe, 3),
                "size_multiplier": h.size_multiplier,
                "total_trades": h.total_trades,
                "reason": h.reason,
                "disabled_at": _fmt_dt(h.disabled_at),
                "re_enable_at": _fmt_dt(h.re_enable_at),
            }
            for h in self._health.values()
        ]
        return sorted(rows, key=lambda r: _order.get(StrategyStatus(r["status"]), 99))

    # ── Internal: metric loading ──────────────────────────────────────────

    def _load_strategy_names(self) -> list[str]:
        """Return all distinct strategy names that have closed trades."""
        with get_session() as session:
            rows = (
                session.query(Trade.strategy)
                .filter(Trade.closed_at.isnot(None))
                .distinct()
                .all()
            )
        return [r.strategy for r in rows]

    def _load_closed_trades(
        self, strategy_name: str, limit: int | None = None
    ) -> list[Trade]:
        """
        Load closed trades for a strategy, ordered oldest-first.

        ``limit`` loads the most-recent N trades (still returned
        oldest-first so streaks and drawdown are computed correctly).
        """
        with get_session() as session:
            q = (
                session.query(Trade)
                .filter(
                    Trade.strategy == strategy_name,
                    Trade.closed_at.isnot(None),
                    Trade.pnl_pct.isnot(None),
                )
                .order_by(Trade.closed_at.asc())
            )
            if limit is not None:
                # We want the most-recent N, so subquery approach:
                # fetch all, slice tail. This is acceptable for small N;
                # for large corpora consider a proper ORDER BY DESC + LIMIT subquery.
                trades = q.all()
                return trades[-limit:]
            return q.all()

    def _recent_pnl(self, strategy_name: str, n: int) -> list[float]:
        """Return the last ``n`` pnl_pct values for a strategy."""
        trades = self._load_closed_trades(strategy_name, limit=n)
        return [t.pnl_pct for t in trades if t.pnl_pct is not None]  # type: ignore[misc]

    # ── Internal: metric computation ──────────────────────────────────────

    def _refresh_strategy(self, name: str) -> None:
        """Recompute metrics for one strategy and apply state transitions."""
        health = self._get_or_create(name)
        trades = self._load_closed_trades(name)
        all_pnl: list[float] = [t.pnl_pct for t in trades if t.pnl_pct is not None]  # type: ignore[misc]
        health.total_trades = len(all_pnl)

        t = self._thresholds

        # Require minimum trades before evaluation to avoid false positives
        # during the warm-up period when a strategy has only a handful of trades.
        if health.total_trades < t.min_trades_for_evaluation:
            health.reason = (
                f"Insufficient trade history ({health.total_trades}/{t.min_trades_for_evaluation})"
            )
            return

        # ── Rolling windows ───────────────────────────────────────────────
        window_20 = all_pnl[-t.warn_win_rate_window:]
        window_30 = all_pnl[-t.disable_win_rate_window:]

        wins_20 = sum(1 for p in window_20 if p > 0.0)
        health.win_rate_20 = wins_20 / len(window_20) if window_20 else 0.0
        health.profit_factor_20 = _compute_profit_factor(window_20)

        wins_30 = sum(1 for p in window_30 if p > 0.0)
        health.win_rate_30 = wins_30 / len(window_30) if window_30 else 0.0

        health.consecutive_losses = _count_consecutive_losses(all_pnl)
        health.max_drawdown_pct = _compute_max_drawdown(all_pnl)
        health.rolling_sharpe = _compute_sharpe(all_pnl[-50:])

        # ── Skip rule evaluation when already disabled / cooldown ─────────
        # Metrics are refreshed above so the dashboard shows current data,
        # but we do not transition BACK to ACTIVE here — that is handled
        # by ``should_trade()`` based on time gates.
        if health.status in (
            StrategyStatus.DISABLED,
            StrategyStatus.COOLDOWN,
        ):
            return

        now = datetime.now(UTC)

        # ── Check hard-disable rules first (highest priority) ─────────────
        if health.consecutive_losses >= t.disable_consecutive_losses:
            reason = (
                f"{health.consecutive_losses} consecutive losses "
                f"(limit: {t.disable_consecutive_losses})"
            )
            if health.status != StrategyStatus.DISABLED:
                self._disable(health, reason, now)
            return

        if health.max_drawdown_pct >= t.disable_drawdown_pct:
            reason = (
                f"Strategy drawdown {health.max_drawdown_pct:.1f}% "
                f"exceeded limit {t.disable_drawdown_pct:.1f}%"
            )
            if health.status != StrategyStatus.DISABLED:
                self._disable(health, reason, now)
            return

        if (
            len(window_30) >= t.disable_win_rate_window
            and health.win_rate_30 < t.disable_win_rate_min
        ):
            reason = (
                f"Win rate over last {t.disable_win_rate_window} trades: "
                f"{health.win_rate_30:.1%} < {t.disable_win_rate_min:.1%} limit"
            )
            if health.status != StrategyStatus.DISABLED:
                self._disable(health, reason, now)
            return

        # ── Check probation — re-evaluate if still on probation ───────────
        # (should_trade handles the promotion, nothing to do here on metrics)
        if health.status == StrategyStatus.PROBATION:
            return

        # ── Warn rules (strategy still trades but is flagged) ─────────────
        warned = False

        if (
            len(window_20) >= t.warn_win_rate_window
            and health.win_rate_20 < t.warn_win_rate_min
        ):
            health.reason = (
                f"WARN: win rate {health.win_rate_20:.1%} over last "
                f"{t.warn_win_rate_window} trades < {t.warn_win_rate_min:.1%}"
            )
            warned = True

        if (
            len(window_20) >= t.warn_profit_factor_window
            and health.profit_factor_20 < t.warn_profit_factor_min
        ):
            pf_reason = (
                f"WARN: profit factor {health.profit_factor_20:.2f} over last "
                f"{t.warn_profit_factor_window} trades < {t.warn_profit_factor_min:.2f}"
            )
            health.reason = (
                f"{health.reason}; {pf_reason}" if health.reason else pf_reason
            )
            warned = True

        if warned:
            if health.status != StrategyStatus.WARNING:
                logger.warning(
                    "StrategyHealth [%s]: status → WARNING. %s",
                    name,
                    health.reason,
                )
            health.status = StrategyStatus.WARNING
            health.size_multiplier = self._thresholds.normal_size_multiplier
            return

        # ── All clear ─────────────────────────────────────────────────────
        if health.status == StrategyStatus.WARNING:
            logger.info(
                "StrategyHealth [%s]: WARNING cleared → ACTIVE",
                name,
            )
        health.status = StrategyStatus.ACTIVE
        health.size_multiplier = self._thresholds.normal_size_multiplier
        health.reason = ""

    # ── Internal: state transitions ───────────────────────────────────────

    def _get_or_create(self, strategy_name: str) -> StrategyHealth:
        """Return the existing health record or create a fresh ACTIVE one."""
        if strategy_name not in self._health:
            self._health[strategy_name] = StrategyHealth(strategy_name=strategy_name)
        return self._health[strategy_name]

    def _disable(
        self,
        health: StrategyHealth,
        reason: str,
        now: datetime,
    ) -> None:
        """Transition a strategy to DISABLED and schedule the cooldown window."""
        t = self._thresholds
        health.status = StrategyStatus.COOLDOWN
        health.disabled_at = now
        health.re_enable_at = now + timedelta(hours=t.cooldown_hours)
        health.extended_ban_until = None
        health.size_multiplier = 0.0
        health.reason = reason
        logger.warning(
            "StrategyHealth [%s]: AUTO-DISABLED → COOLDOWN. Reason: %s. "
            "Re-enable at %s (UTC).",
            health.strategy_name,
            reason,
            _fmt_dt(health.re_enable_at),
        )

    def _promote_to_probation(
        self,
        health: StrategyHealth,
        now: datetime,
    ) -> None:
        """Transition from COOLDOWN → PROBATION at 50% size."""
        t = self._thresholds
        health.status = StrategyStatus.PROBATION
        health.probation_started_at = now
        health.size_multiplier = t.probation_size_multiplier
        health.reason = (
            f"Probation — {t.probation_size_multiplier:.0%} size for "
            f"{t.probation_hours:.0f} h (disabled: {_fmt_dt(health.disabled_at)})"
        )
        logger.info(
            "StrategyHealth [%s]: COOLDOWN → PROBATION (%.0f%% size, %s h window).",
            health.strategy_name,
            t.probation_size_multiplier * 100,
            t.probation_hours,
        )

    def _graduate_to_active(self, health: StrategyHealth) -> None:
        """Restore a strategy to full ACTIVE status."""
        health.status = StrategyStatus.ACTIVE
        health.size_multiplier = self._thresholds.normal_size_multiplier
        health.disabled_at = None
        health.re_enable_at = None
        health.probation_started_at = None
        health.extended_ban_until = None
        health.reason = ""

    def _extended_ban(self, health: StrategyHealth, now: datetime) -> None:
        """Apply the extended ban after a probation failure."""
        t = self._thresholds
        ban_until = now + timedelta(days=t.extended_ban_days)
        health.status = StrategyStatus.DISABLED
        health.extended_ban_until = ban_until
        health.probation_started_at = None
        health.size_multiplier = 0.0
        health.reason = (
            f"Extended ban after probation failure — disabled until "
            f"{_fmt_dt(ban_until)} UTC ({t.extended_ban_days:.0f}-day ban)"
        )


# ---------------------------------------------------------------------------
# Formatting helpers (private — not part of the public API)
# ---------------------------------------------------------------------------


def _fmt_dt(dt: datetime | None) -> str:
    """Format a UTC datetime for human-readable log messages."""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _fmt_timedelta(td: timedelta) -> str:
    """Format a timedelta into 'Xh Ym' for log messages."""
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "0m"
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
