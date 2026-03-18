"""
backtesting/engine.py — Core event-driven backtesting engine for Atlas.

Design principles
-----------------
- No look-ahead bias: at candle N, only data[:N+1] is visible to the strategy.
- Realistic fills: slippage scales with volume; fill prices are clamped to the
  candle's high/low range so the engine never fills at prices that didn't trade.
- Commission: charged on both entry and exit as a percentage of trade value.
- All state is local to BacktestEngine.run() — the engine is stateless between
  calls so it can be reused by WalkForwardValidator without side-effects.

Usage
-----
    from backtesting.engine import BacktestEngine
    from strategies.technical.ema_crossover import EmaCrossoverStrategy

    engine = BacktestEngine(initial_capital=10_000, commission_pct=0.001)
    result = engine.run(df, EmaCrossoverStrategy())
    print(result.summary())
    engine.plot_equity_curve(result)
"""

from __future__ import annotations

import csv
import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from core.regime_detector import RegimeDetector
from core.trailing_stop import TrailingStopManager
from strategies.base import BaseStrategy, Direction, Signal

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SLIPPAGE_MIN = 0.0005   # 0.05 % — tight markets / high-liquidity candles
_SLIPPAGE_MAX = 0.0015   # 0.15 % — illiquid candles
_SLIPPAGE_VOL_THRESHOLD = 1.0  # volume z-score above which slippage is minimised
_ANNUALISATION_FACTOR = 252     # trading days per year (equity); swap to 365 for crypto


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class TradeLog:
    """
    Complete record of a single round-trip trade (entry + exit).

    All prices are fill prices (after slippage). pnl is in quote currency,
    net of commissions on both legs.
    """

    trade_id: int
    symbol: str
    strategy: str
    side: Direction
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    size: float           # units of base asset
    gross_pnl: float      # before commissions
    commission_paid: float
    net_pnl: float        # gross_pnl - commission_paid
    pnl_pct: float        # net_pnl / entry_value * 100
    duration: timedelta
    exit_reason: str      # "take_profit" | "stop_loss" | "signal_exit" | "end_of_data"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BacktestResult:
    """
    Full results container returned by BacktestEngine.run().

    All percentage values are in plain float form, e.g. 0.15 = 15 %.
    """

    # Core P&L
    initial_capital: float
    final_equity: float
    total_return: float           # (final - initial) / initial
    annualized_return: float

    # Risk-adjusted returns
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float           # annualised_return / abs(max_drawdown)

    # Drawdown
    max_drawdown: float           # worst peak-to-trough as negative fraction
    max_drawdown_duration: int    # calendar days of worst drawdown period

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float               # winning_trades / total_trades
    avg_win: float                # average net PnL of winning trades
    avg_loss: float               # average net PnL of losing trades (negative)
    profit_factor: float          # gross_profit / abs(gross_loss)
    expectancy: float             # expected net PnL per trade
    avg_trade_duration: timedelta

    # Equity curve (indexed by candle timestamp)
    equity_curve: pd.Series

    # Individual trade log
    trades: list[TradeLog] = field(default_factory=list)

    # Metadata
    strategy_name: str = ""
    symbol: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    commission_pct: float = 0.001

    # ------------------------------------------------------------------

    def summary(self) -> str:
        """Return a formatted multi-line performance report."""
        lines = [
            "=" * 60,
            f"  Atlas Backtest Report — {self.strategy_name}",
            f"  Symbol: {self.symbol}",
            (
                f"  Period: {self.start_date:%Y-%m-%d} → {self.end_date:%Y-%m-%d}"
                if self.start_date and self.end_date
                else "  Period: N/A"
            ),
            "=" * 60,
            "",
            "  P&L",
            f"    Initial capital   : ${self.initial_capital:>12,.2f}",
            f"    Final equity      : ${self.final_equity:>12,.2f}",
            f"    Total return      : {self.total_return * 100:>+.2f}%",
            f"    Annualised return : {self.annualized_return * 100:>+.2f}%",
            "",
            "  Risk-adjusted",
            f"    Sharpe ratio      : {self.sharpe_ratio:>8.3f}",
            f"    Sortino ratio     : {self.sortino_ratio:>8.3f}",
            f"    Calmar ratio      : {self.calmar_ratio:>8.3f}",
            "",
            "  Drawdown",
            f"    Max drawdown      : {self.max_drawdown * 100:>+.2f}%",
            f"    Drawdown duration : {self.max_drawdown_duration} days",
            "",
            "  Trades",
            f"    Total trades      : {self.total_trades}",
            f"    Win rate          : {self.win_rate * 100:.1f}%",
            f"    Winning trades    : {self.winning_trades}",
            f"    Losing trades     : {self.losing_trades}",
            f"    Avg win           : ${self.avg_win:>10,.2f}",
            f"    Avg loss          : ${self.avg_loss:>10,.2f}",
            f"    Profit factor     : {self.profit_factor:.3f}",
            f"    Expectancy / trade: ${self.expectancy:>10,.2f}",
            f"    Avg trade duration: {self.avg_trade_duration}",
            "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class BacktestEngine:
    """
    Event-driven backtesting engine.

    Parameters
    ----------
    initial_capital : float
        Starting portfolio equity in quote currency.
    commission_pct : float
        Round-trip commission per side as a fraction (0.001 = 0.1 %).
        Applied on both entry and exit.
    risk_per_trade_pct : float
        Fraction of current equity risked per trade (default 1.5 %).
        Used to compute position size when the strategy does not specify it.
    slippage_enabled : bool
        Whether to simulate slippage (default True).
    log_dir : Path | None
        Where to save equity curve PNGs and CSV exports. Defaults to
        ``<project_root>/logs/``.
    scale_out_tiers : list[tuple[float, float]]
        Ordered list of (rr_multiple, fraction_of_original_size_to_close) pairs.
        Default is [(1.0, 0.30), (2.0, 0.30)] meaning:
          - Tier 1: close 30 % of original size at 1× risk-reward
          - Tier 2: close 30 % of original size at 2× risk-reward
          - Remainder (40 %) rides the trailing stop or full stop/signal exit
        Pass an empty list to disable scale-out entirely (all-or-nothing behaviour).
        After tier 1 hits, the stop for the remaining position is promoted to
        break-even (entry price) to make the trade risk-free.
    """

    def __init__(
        self,
        initial_capital: float = 10_000.0,
        commission_pct: float = 0.001,
        risk_per_trade_pct: float = 0.015,
        slippage_enabled: bool = True,
        log_dir: Path | None = None,
        regime_filter: bool = True,
        trailing_stops: bool = False,  # Disabled by default — too aggressive for trend-followers; needs per-strategy tuning
        scale_out_tiers: list[tuple[float, float]] | None = None,
    ) -> None:
        if initial_capital <= 0:
            raise ValueError("initial_capital must be positive")
        if not 0.0 <= commission_pct <= 0.05:
            raise ValueError("commission_pct must be between 0 and 5 %")

        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.risk_per_trade_pct = risk_per_trade_pct
        self.slippage_enabled = slippage_enabled
        self.log_dir = log_dir or (Path(__file__).resolve().parent.parent / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.regime_filter = regime_filter
        self.trailing_stops = trailing_stops
        self._regime_detector = RegimeDetector() if regime_filter else None
        self._trailing_stop_mgr = TrailingStopManager(method="chandelier") if trailing_stops else None
        # Default two-tier scale-out: 30 % at 1R, 30 % at 2R, 40 % rides stop
        self.scale_out_tiers: list[tuple[float, float]] = (
            scale_out_tiers if scale_out_tiers is not None else [(1.0, 0.30), (2.0, 0.30)]
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, df: pd.DataFrame, strategy: BaseStrategy) -> BacktestResult:
        """
        Simulate ``strategy`` on ``df`` bar by bar.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV DataFrame with columns open, high, low, close, volume.
            Index must be a DatetimeIndex (UTC preferred).
        strategy : BaseStrategy
            Any concrete strategy implementing analyze() / should_enter() /
            should_exit().

        Returns
        -------
        BacktestResult
        """
        self._validate_dataframe(df)
        df = df.copy().sort_index()

        equity = self.initial_capital
        equity_curve: list[tuple[Any, float]] = []
        trades: list[TradeLog] = []
        trade_id = 0

        # Volume z-score for slippage scaling
        vol_mean = df["volume"].mean()
        vol_std = df["volume"].std()
        if vol_std == 0 or math.isnan(vol_std):
            vol_std = 1.0

        # Active position state
        in_position = False
        position_side: Direction = Direction.FLAT
        entry_price = 0.0
        entry_time: datetime = df.index[0]
        position_size = 0.0          # original full size at entry
        remaining_size = 0.0         # units still open after partial exits
        entry_commission = 0.0       # commission on the original full entry
        entry_signal: Signal | None = None

        # Scale-out state (reset on every new entry)
        # tier_hit[k] is True once the k-th tier target has been reached
        tier_hit: list[bool] = []
        # Computed target prices for each tier (set at entry)
        tier_targets: list[float] = []
        # break-even stop: promoted to entry price after tier 1 hits
        breakeven_stop: float = 0.0

        # Trailing stop state (per-position)
        highest_since_entry = 0.0
        lowest_since_entry = float("inf")

        # Regime detection cache (recomputed every 20 bars to avoid overhead)
        _regime_check_interval = 20
        _last_regime_weight: float = 1.0
        _regime_size_mult: float = 1.0

        for i in range(len(df)):
            bar = df.iloc[i]
            timestamp = df.index[i]

            # Only show the strategy data up to and including this bar
            visible_df = df.iloc[: i + 1]

            if in_position:
                # ── Update trailing stop state ──
                highest_since_entry = max(highest_since_entry, bar["high"])
                lowest_since_entry = min(lowest_since_entry, bar["low"])

                # ── Compute dynamic trailing stop ──
                # Start from the signal stop or the break-even stop (whichever is
                # more protective after tier 1 has been hit).
                base_stop = entry_signal.stop_loss if entry_signal else 0.0
                active_stop = max(base_stop, breakeven_stop) if position_side == Direction.LONG \
                    else (min(base_stop, breakeven_stop) if breakeven_stop > 0 else base_stop)

                if self._trailing_stop_mgr and entry_signal:
                    from strategies.technical.indicators import atr as atr_fn
                    if len(visible_df) >= 16:
                        atr_series = atr_fn(visible_df, 14)
                        current_atr = float(atr_series.iloc[-1])
                        if current_atr > 0:
                            ts_result = self._trailing_stop_mgr.update(
                                current_price=bar["close"],
                                current_atr=current_atr,
                                direction=position_side.value,
                                entry_price=entry_price,
                                highest_since_entry=highest_since_entry,
                                lowest_since_entry=lowest_since_entry,
                            )
                            # Ratchet stop: only tighten, never loosen
                            if position_side == Direction.LONG:
                                active_stop = max(active_stop, ts_result.stop_price)
                            else:
                                active_stop = min(active_stop, ts_result.stop_price)

                # ── Scale-out tier processing ──
                # Evaluate each configured tier on this bar before checking full exit.
                # Partial closes generate their own TradeLog entries and reduce
                # remaining_size. After tier 1 hits the stop is promoted to break-even.
                vol_z_so = (bar["volume"] - vol_mean) / vol_std

                for k, (rr_mult, orig_fraction) in enumerate(self.scale_out_tiers):
                    if tier_hit[k]:
                        continue

                    # Target price for this tier
                    target = tier_targets[k]
                    if target <= 0:
                        continue

                    tier_reached = (
                        (position_side == Direction.LONG and bar["high"] >= target) or
                        (position_side == Direction.SHORT and bar["low"] <= target)
                    )
                    if not tier_reached:
                        continue

                    # Size to close for this tier (fraction of the *original* full size)
                    close_size = position_size * orig_fraction
                    # Never close more than what is still open
                    close_size = min(close_size, remaining_size)
                    if close_size <= 0:
                        continue

                    fill_tier = self._apply_slippage(
                        float(np.clip(target, bar["low"], bar["high"])),
                        position_side, vol_z_so, is_exit=True,
                    )

                    # Commission is prorated: entry_commission was on full size,
                    # so each partial exit pays its proportional share of entry fees.
                    tier_entry_comm = entry_commission * (close_size / position_size)
                    tier_exit_comm = fill_tier * close_size * self.commission_pct

                    if position_side == Direction.LONG:
                        tier_gross = (fill_tier - entry_price) * close_size
                    else:
                        tier_gross = (entry_price - fill_tier) * close_size

                    tier_net = tier_gross - tier_entry_comm - tier_exit_comm
                    tier_entry_val = entry_price * close_size
                    tier_pnl_pct = tier_net / tier_entry_val * 100.0 if tier_entry_val else 0.0

                    equity += tier_net
                    remaining_size -= close_size
                    tier_hit[k] = True

                    trades.append(TradeLog(
                        trade_id=trade_id,
                        symbol=strategy.name,
                        strategy=strategy.name,
                        side=position_side,
                        entry_time=entry_time,
                        entry_price=entry_price,
                        exit_time=timestamp,
                        exit_price=fill_tier,
                        size=close_size,
                        gross_pnl=tier_gross,
                        commission_paid=tier_entry_comm + tier_exit_comm,
                        net_pnl=tier_net,
                        pnl_pct=tier_pnl_pct,
                        duration=timestamp - entry_time,
                        exit_reason=f"scale_out_t{k + 1}",
                    ))
                    trade_id += 1

                    # After tier 1 hits: promote stop to break-even so the
                    # remaining position becomes risk-free.
                    if k == 0:
                        if position_side == Direction.LONG:
                            breakeven_stop = max(breakeven_stop, entry_price)
                            active_stop = max(active_stop, breakeven_stop)
                        else:
                            # For SHORT, break-even is a ceiling (stop above entry is tighter)
                            breakeven_stop = entry_price
                            active_stop = min(active_stop, breakeven_stop) if active_stop > 0 else breakeven_stop

                    logger.debug(
                        "Scale-out tier %d hit: closed %.6f units at %.4f "
                        "(rr=%.1f×, remaining=%.6f)",
                        k + 1, close_size, fill_tier, rr_mult, remaining_size,
                    )

                    # If nothing remains after this tier, close the position fully
                    if remaining_size <= 0:
                        in_position = False
                        entry_signal = None
                        break

                if not in_position:
                    # Position was fully consumed by scale-out tiers this bar
                    equity_curve.append((timestamp, equity))
                    continue

                # ── Check full exits (stop-loss / take-profit hit intrabar) ──
                exit_reason = self._check_intrabar_exits(
                    bar, position_side,
                    active_stop,
                    entry_signal.take_profit if entry_signal else 0.0,
                )

                if exit_reason is None:
                    # Check strategy's own exit signal
                    from strategies.base import Position as StratPosition
                    pos = StratPosition(
                        symbol=strategy.name,
                        side=position_side,
                        entry_price=entry_price,
                        size=remaining_size,
                        stop_loss=entry_signal.stop_loss if entry_signal else 0.0,
                        take_profit=entry_signal.take_profit if entry_signal else 0.0,
                        entry_time=entry_time,
                        strategy=strategy.name,
                        metadata={"mark_price": bar["close"]},
                    )
                    if strategy.should_exit(visible_df, pos):
                        exit_reason = "signal_exit"

                if exit_reason is not None:
                    # Determine fill price
                    if exit_reason == "stop_loss":
                        raw_exit_price = active_stop if active_stop > 0 else bar["close"]
                        raw_exit_price = float(np.clip(raw_exit_price, bar["low"], bar["high"]))
                    elif exit_reason == "take_profit":
                        raw_exit_price = entry_signal.take_profit if entry_signal else bar["close"]
                        raw_exit_price = float(np.clip(raw_exit_price, bar["low"], bar["high"]))
                    else:
                        raw_exit_price = bar["close"]

                    vol_z = (bar["volume"] - vol_mean) / vol_std
                    fill_exit = self._apply_slippage(
                        raw_exit_price, position_side, vol_z, is_exit=True
                    )

                    # P&L on the remaining open size only.
                    # Entry commission is prorated to whatever fraction is left.
                    remaining_entry_comm = entry_commission * (remaining_size / position_size)
                    if position_side == Direction.LONG:
                        gross_pnl = (fill_exit - entry_price) * remaining_size
                    else:
                        gross_pnl = (entry_price - fill_exit) * remaining_size

                    exit_commission = fill_exit * remaining_size * self.commission_pct
                    net_pnl = gross_pnl - remaining_entry_comm - exit_commission
                    entry_value = entry_price * remaining_size
                    pnl_pct = net_pnl / entry_value * 100.0 if entry_value else 0.0

                    equity += net_pnl

                    trade_log = TradeLog(
                        trade_id=trade_id,
                        symbol=strategy.name,
                        strategy=strategy.name,
                        side=position_side,
                        entry_time=entry_time,
                        entry_price=entry_price,
                        exit_time=timestamp,
                        exit_price=fill_exit,
                        size=remaining_size,
                        gross_pnl=gross_pnl,
                        commission_paid=remaining_entry_comm + exit_commission,
                        net_pnl=net_pnl,
                        pnl_pct=pnl_pct,
                        duration=timestamp - entry_time,
                        exit_reason=exit_reason,
                    )
                    trades.append(trade_log)
                    trade_id += 1

                    in_position = False
                    entry_signal = None

            if not in_position:
                # ── Regime detection (every _regime_check_interval bars) ──
                if self._regime_detector and i % _regime_check_interval == 0 and len(visible_df) >= 30:
                    regime_result = self._regime_detector.detect(visible_df)
                    strategy_weights = regime_result.strategy_weights()
                    _last_regime_weight = strategy_weights.get(strategy.name, 1.0)
                    _regime_size_mult = regime_result.size_multiplier()

                # ── Regime gate: skip if strategy is heavily penalised ──
                if _last_regime_weight <= 0.5:
                    pass  # Skip entry — regime suppresses this strategy
                elif strategy.should_enter(visible_df):
                    signal = strategy.analyze(visible_df)

                    if (
                        signal is not None
                        and signal.direction != Direction.FLAT
                        and abs(signal.conviction) >= 0.3
                    ):
                        # Scale conviction by regime weight
                        signal.conviction = signal.conviction * _last_regime_weight

                        vol_z = (bar["volume"] - vol_mean) / vol_std
                        fill_entry = self._apply_slippage(
                            bar["close"], signal.direction, vol_z, is_exit=False
                        )

                        # Position sizing: risk fixed % of equity, scaled by regime
                        stop_dist = abs(fill_entry - signal.stop_loss)
                        if stop_dist > 0:
                            risk_amount = equity * self.risk_per_trade_pct * _regime_size_mult
                            position_size = risk_amount / stop_dist
                        else:
                            position_size = 0.0

                        if position_size > 0:
                            entry_commission = fill_entry * position_size * self.commission_pct
                            in_position = True
                            position_side = signal.direction
                            entry_price = fill_entry
                            entry_time = timestamp
                            entry_signal = signal
                            # Reset trailing stop state for new position
                            highest_since_entry = bar["high"]
                            lowest_since_entry = bar["low"]
                            # Initialise scale-out state for this new position
                            remaining_size = position_size
                            breakeven_stop = 0.0
                            tier_hit = [False] * len(self.scale_out_tiers)
                            # Pre-compute target prices from entry and stop distance
                            _risk = abs(fill_entry - signal.stop_loss)
                            if position_side == Direction.LONG:
                                tier_targets = [
                                    fill_entry + rr * _risk
                                    for rr, _ in self.scale_out_tiers
                                ]
                            else:
                                tier_targets = [
                                    fill_entry - rr * _risk
                                    for rr, _ in self.scale_out_tiers
                                ]

            equity_curve.append((timestamp, equity))

        # Close any open position at end of data (applies to remaining_size only)
        if in_position and entry_signal is not None:
            last_bar = df.iloc[-1]
            last_ts = df.index[-1]
            fill_exit = last_bar["close"]
            if position_side == Direction.LONG:
                gross_pnl = (fill_exit - entry_price) * remaining_size
            else:
                gross_pnl = (entry_price - fill_exit) * remaining_size

            # Prorate the original entry commission to the fraction still open
            remaining_entry_comm = entry_commission * (remaining_size / position_size) if position_size > 0 else 0.0
            exit_commission = fill_exit * remaining_size * self.commission_pct
            net_pnl = gross_pnl - remaining_entry_comm - exit_commission
            entry_value = entry_price * remaining_size
            pnl_pct = net_pnl / entry_value * 100.0 if entry_value else 0.0
            equity += net_pnl

            trades.append(
                TradeLog(
                    trade_id=trade_id,
                    symbol=strategy.name,
                    strategy=strategy.name,
                    side=position_side,
                    entry_time=entry_time,
                    entry_price=entry_price,
                    exit_time=last_ts,
                    exit_price=fill_exit,
                    size=remaining_size,
                    gross_pnl=gross_pnl,
                    commission_paid=remaining_entry_comm + exit_commission,
                    net_pnl=net_pnl,
                    pnl_pct=pnl_pct,
                    duration=last_ts - entry_time,
                    exit_reason="end_of_data",
                )
            )
            equity_curve.append((last_ts, equity))

        equity_series = pd.Series(
            [e for _, e in equity_curve],
            index=[t for t, _ in equity_curve],
            name="equity",
            dtype=float,
        )
        # De-duplicate index (multiple events on same candle) — keep last
        equity_series = equity_series[~equity_series.index.duplicated(keep="last")]

        result = self._compute_metrics(
            initial_capital=self.initial_capital,
            final_equity=equity,
            equity_curve=equity_series,
            trades=trades,
            strategy_name=strategy.name,
            symbol=strategy.name,
            start_date=df.index[0].to_pydatetime() if hasattr(df.index[0], "to_pydatetime") else df.index[0],
            end_date=df.index[-1].to_pydatetime() if hasattr(df.index[-1], "to_pydatetime") else df.index[-1],
            commission_pct=self.commission_pct,
        )
        return result

    # ------------------------------------------------------------------

    def plot_equity_curve(self, result: BacktestResult, filename: str | None = None) -> Path:
        """
        Save an equity curve PNG to log_dir.

        Returns the path to the saved file.
        """
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError as exc:
            raise ImportError(
                "matplotlib is required for plot_equity_curve(). "
                "Install with: pip install matplotlib"
            ) from exc

        fig, axes = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1]})
        ax_eq, ax_dd = axes

        eq = result.equity_curve
        ax_eq.plot(eq.index, eq.values, linewidth=1.5, color="#2196F3", label="Equity")
        ax_eq.axhline(result.initial_capital, linewidth=0.8, color="grey", linestyle="--")
        ax_eq.set_title(
            f"{result.strategy_name} — Equity Curve "
            f"(Return: {result.total_return * 100:+.2f}%, Sharpe: {result.sharpe_ratio:.2f})"
        )
        ax_eq.set_ylabel("Portfolio Value ($)")
        ax_eq.legend()
        ax_eq.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        # Drawdown subplot
        rolling_max = eq.cummax()
        drawdown = (eq - rolling_max) / rolling_max
        ax_dd.fill_between(drawdown.index, drawdown.values, 0, alpha=0.4, color="#F44336")
        ax_dd.set_ylabel("Drawdown")
        ax_dd.set_xlabel("Date")
        ax_dd.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        fig.autofmt_xdate()
        fig.tight_layout()

        if filename is None:
            ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"equity_{result.strategy_name}_{ts}.png"
        out_path = self.log_dir / filename
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info("Equity curve saved to %s", out_path)
        return out_path

    def export_trades(self, result: BacktestResult, filename: str | None = None) -> Path:
        """
        Export the trade log to a CSV file in log_dir.

        Returns the path to the saved file.
        """
        if filename is None:
            ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"trades_{result.strategy_name}_{ts}.csv"
        out_path = self.log_dir / filename

        fieldnames = [
            "trade_id", "symbol", "strategy", "side",
            "entry_time", "entry_price",
            "exit_time", "exit_price",
            "size", "gross_pnl", "commission_paid", "net_pnl",
            "pnl_pct", "duration_seconds", "exit_reason",
        ]
        with open(out_path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for t in result.trades:
                writer.writerow(
                    {
                        "trade_id": t.trade_id,
                        "symbol": t.symbol,
                        "strategy": t.strategy,
                        "side": t.side.value,
                        "entry_time": t.entry_time.isoformat(),
                        "entry_price": f"{t.entry_price:.6f}",
                        "exit_time": t.exit_time.isoformat(),
                        "exit_price": f"{t.exit_price:.6f}",
                        "size": f"{t.size:.6f}",
                        "gross_pnl": f"{t.gross_pnl:.4f}",
                        "commission_paid": f"{t.commission_paid:.4f}",
                        "net_pnl": f"{t.net_pnl:.4f}",
                        "pnl_pct": f"{t.pnl_pct:.4f}",
                        "duration_seconds": t.duration.total_seconds(),
                        "exit_reason": t.exit_reason,
                    }
                )

        logger.info("Trades exported to %s (%d rows)", out_path, len(result.trades))
        return out_path

    def generate_report(self, result: BacktestResult) -> str:
        """Return the formatted performance summary string."""
        return result.summary()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_dataframe(df: pd.DataFrame) -> None:
        required = {"open", "high", "low", "close", "volume"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"DataFrame is missing columns: {missing}")
        if len(df) < 2:
            raise ValueError("DataFrame must contain at least 2 rows")
        if not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError("DataFrame index must be a DatetimeIndex")

    def _apply_slippage(
        self,
        price: float,
        direction: Direction,
        vol_z: float,
        is_exit: bool,
    ) -> float:
        """
        Calculate a realistic fill price with slippage.

        Slippage is smaller when volume is high (tight spread) and larger
        on thin candles. Entry slippage is adverse; exit slippage is also
        adverse (you pay a wider spread either way).
        """
        if not self.slippage_enabled:
            return price

        # Map volume z-score to slippage fraction: high vol → low slip
        alpha = max(0.0, min(1.0, (vol_z + 1.0) / (2.0 * _SLIPPAGE_VOL_THRESHOLD)))
        slip_pct = _SLIPPAGE_MAX - alpha * (_SLIPPAGE_MAX - _SLIPPAGE_MIN)

        # Adverse direction: entry longs pay more, entry shorts sell less;
        # exits also suffer — slippage is always against the trader.
        if direction == Direction.LONG:
            return price * (1.0 + slip_pct) if not is_exit else price * (1.0 - slip_pct)
        else:
            return price * (1.0 - slip_pct) if not is_exit else price * (1.0 + slip_pct)

    @staticmethod
    def _check_intrabar_exits(
        bar: pd.Series,
        side: Direction,
        stop_loss: float,
        take_profit: float,
    ) -> str | None:
        """
        Check whether stop-loss or take-profit was hit within this bar.

        Returns "stop_loss", "take_profit", or None.
        We assume worst-case ordering: stop is checked first.
        """
        if stop_loss <= 0 or take_profit <= 0:
            return None

        if side == Direction.LONG:
            if bar["low"] <= stop_loss:
                return "stop_loss"
            if bar["high"] >= take_profit:
                return "take_profit"
        elif side == Direction.SHORT:
            if bar["high"] >= stop_loss:
                return "stop_loss"
            if bar["low"] <= take_profit:
                return "take_profit"

        return None

    @staticmethod
    def _compute_metrics(
        initial_capital: float,
        final_equity: float,
        equity_curve: pd.Series,
        trades: list[TradeLog],
        strategy_name: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        commission_pct: float,
    ) -> BacktestResult:
        """Compute all performance metrics from the equity curve and trade log."""

        total_return = (final_equity - initial_capital) / initial_capital

        # Annualised return using CAGR formula
        n_days = max(1, (end_date - start_date).days)
        n_years = n_days / 365.0
        if n_years > 0:
            annualized_return = (1.0 + total_return) ** (1.0 / n_years) - 1.0
        else:
            annualized_return = 0.0

        # Daily returns from equity curve
        daily_returns = equity_curve.resample("D").last().ffill().pct_change().dropna()

        # Sharpe ratio (annualised, risk-free = 0 for simplicity)
        if len(daily_returns) > 1 and daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * math.sqrt(
                _ANNUALISATION_FACTOR
            )
        else:
            sharpe_ratio = 0.0

        # Sortino ratio (only downside volatility)
        negative_returns = daily_returns[daily_returns < 0]
        if len(negative_returns) > 1 and negative_returns.std() > 0:
            sortino_ratio = (daily_returns.mean() / negative_returns.std()) * math.sqrt(
                _ANNUALISATION_FACTOR
            )
        else:
            sortino_ratio = 0.0

        # Max drawdown
        rolling_max = equity_curve.cummax()
        drawdown_series = (equity_curve - rolling_max) / rolling_max
        max_drawdown = float(drawdown_series.min())  # negative number

        # Max drawdown duration (longest continuous underwater period)
        underwater = drawdown_series < 0
        max_dd_duration = 0
        current_streak = 0
        dd_start: datetime | None = None

        for ts, is_under in underwater.items():
            if is_under:
                if dd_start is None:
                    dd_start = ts
                current_streak = (ts - dd_start).days
                max_dd_duration = max(max_dd_duration, current_streak)
            else:
                dd_start = None
                current_streak = 0

        # Calmar ratio
        if max_drawdown != 0:
            calmar_ratio = annualized_return / abs(max_drawdown)
        else:
            calmar_ratio = float("inf") if annualized_return > 0 else 0.0

        # Trade statistics
        total_trades = len(trades)
        if total_trades == 0:
            return BacktestResult(
                initial_capital=initial_capital,
                final_equity=final_equity,
                total_return=total_return,
                annualized_return=annualized_return,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_drawdown,
                max_drawdown_duration=max_dd_duration,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                profit_factor=0.0,
                expectancy=0.0,
                avg_trade_duration=timedelta(0),
                equity_curve=equity_curve,
                trades=[],
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                commission_pct=commission_pct,
            )

        winning = [t for t in trades if t.net_pnl > 0]
        losing = [t for t in trades if t.net_pnl <= 0]

        win_rate = len(winning) / total_trades
        avg_win = sum(t.net_pnl for t in winning) / len(winning) if winning else 0.0
        avg_loss = sum(t.net_pnl for t in losing) / len(losing) if losing else 0.0

        gross_profit = sum(t.net_pnl for t in winning)
        gross_loss = abs(sum(t.net_pnl for t in losing))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        expectancy = sum(t.net_pnl for t in trades) / total_trades

        total_seconds = sum(t.duration.total_seconds() for t in trades)
        avg_trade_duration = timedelta(seconds=total_seconds / total_trades)

        return BacktestResult(
            initial_capital=initial_capital,
            final_equity=final_equity,
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_dd_duration,
            total_trades=total_trades,
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            expectancy=expectancy,
            avg_trade_duration=avg_trade_duration,
            equity_curve=equity_curve,
            trades=trades,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            commission_pct=commission_pct,
        )
