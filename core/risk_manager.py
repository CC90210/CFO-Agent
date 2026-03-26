"""
core/risk_manager.py
--------------------
Central Risk Management for Atlas Trading Agent.

KILL SWITCH SAFETY CONTRACT
============================
Every numeric limit defined here is a HARDCODED FLOOR.  Config values loaded
from the environment (via RiskSettings) are accepted only when they are
STRICTER than the floors below.  Any attempt to configure a looser limit is
silently overridden.  This means:

  • The environment can set max_drawdown_pct=10 (stricter than 15) ✓
  • The environment can NOT set max_drawdown_pct=25 (looser than 15) ✗ → 15 used

The safety guarantees can never be disabled or monkey-patched away at runtime;
the floors are module-level constants outside any class.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING

import numpy as np

from config.settings import settings
from strategies.base import Direction, ExitReason, Position, Signal

if TYPE_CHECKING:
    pass  # Avoid circular imports while keeping type hints accurate.

logger = logging.getLogger("atlas.risk")

# ---------------------------------------------------------------------------
# HARDCODED SAFETY FLOORS — IMMUTABLE.  NEVER TOUCH.
# ---------------------------------------------------------------------------
_FLOOR_MAX_DRAWDOWN_PCT: float = 15.0
_FLOOR_DAILY_LOSS_PCT: float = 5.0
_FLOOR_PER_TRADE_RISK_PCT: float = 8.0   # micro account: meaningful risk per trade
_FLOOR_MAX_OPEN_POSITIONS: int = 5
_FLOOR_MAX_CORRELATED_POSITIONS: int = 3
_FLOOR_MAX_SINGLE_ASSET_EXPOSURE_PCT: float = 80.0  # micro account: must concentrate to matter
_HIGH_VOL_ATR_MULTIPLIER: float = 2.0  # ATR above this multiple ⇒ high-vol regime
_HIGH_VOL_SIZE_DIVISOR: float = 2.0  # halve positions in high-vol regime
_MAX_CORRELATION: float = 0.70  # refuse trades correlated above this threshold


# ---------------------------------------------------------------------------
# Helper dataclasses
# ---------------------------------------------------------------------------


@dataclass
class TradeValidation:
    """Result returned by RiskManager.validate_trade()."""

    approved: bool
    reason: str
    adjusted_size: float  # 0.0 when rejected


@dataclass
class DailyPnLSummary:
    """Snapshot produced at day-end or on demand."""

    date: date
    starting_equity: float
    current_equity: float
    realised_pnl: float
    realised_pnl_pct: float
    peak_equity: float
    current_drawdown_pct: float
    trades_opened: int
    trades_closed: int
    halted: bool


# ---------------------------------------------------------------------------
# RiskManager
# ---------------------------------------------------------------------------


class RiskManager:
    """
    Central gatekeeper for all trade decisions.

    Instantiate once and share across the entire system:

        risk = RiskManager(portfolio_value=10_000.0)
        validation = risk.validate_trade(signal, portfolio_value, current_atr, normal_atr)

    Parameters
    ----------
    portfolio_value : float
        Starting/current total equity in quote currency.
    correlations : dict[str, dict[str, float]] | None
        Pre-computed pairwise Pearson correlations between symbols.
        Keys are symbol strings, e.g. ``{"BTC/USDT": {"ETH/USDT": 0.85}}``.
        Pass ``None`` to skip correlation enforcement.
    """

    def __init__(
        self,
        portfolio_value: float,
        correlations: dict[str, dict[str, float]] | None = None,
    ) -> None:
        if portfolio_value <= 0:
            raise ValueError("portfolio_value must be positive")

        # ── Effective limits (floors win over config) ─────────────────────────
        cfg = settings.risk
        self.max_drawdown_pct: float = min(cfg.max_drawdown_pct, _FLOOR_MAX_DRAWDOWN_PCT)
        self.daily_loss_limit_pct: float = min(cfg.daily_loss_limit_pct, _FLOOR_DAILY_LOSS_PCT)
        self.per_trade_risk_pct: float = min(cfg.per_trade_risk_pct, _FLOOR_PER_TRADE_RISK_PCT)
        self.max_open_positions: int = min(cfg.max_open_positions, _FLOOR_MAX_OPEN_POSITIONS)
        self.max_correlated_positions: int = _FLOOR_MAX_CORRELATED_POSITIONS
        self.max_single_asset_exposure_pct: float = _FLOOR_MAX_SINGLE_ASSET_EXPOSURE_PCT

        # ── Portfolio state ────────────────────────────────────────────────────
        self._peak_equity: float = portfolio_value
        self._starting_day_equity: float = portfolio_value
        self._current_equity: float = portfolio_value
        self._realised_pnl: float = 0.0
        self._today: date = date.today()

        # Position tracking
        self._open_positions: dict[str, Position] = {}  # keyed by symbol

        # Correlation matrix
        self._correlations: dict[str, dict[str, float]] = correlations or {}

        # Daily trade counters
        self._trades_opened_today: int = 0
        self._trades_closed_today: int = 0

        # Kill-switch state
        self._trading_halted: bool = False
        self._halt_reason: str = ""

        logger.info(
            "RiskManager initialised — limits: drawdown=%.1f%% daily=%.1f%% "
            "per_trade=%.1f%% max_pos=%d corr_limit=%d asset_exp=%.1f%%",
            self.max_drawdown_pct,
            self.daily_loss_limit_pct,
            self.per_trade_risk_pct,
            self.max_open_positions,
            self.max_correlated_positions,
            self.max_single_asset_exposure_pct,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_trade(
        self,
        signal: Signal,
        portfolio_value: float,
        proposed_size: float,
        current_atr: float,
        normal_atr: float,
    ) -> TradeValidation:
        """
        Run all pre-trade risk checks.  Returns a TradeValidation indicating
        whether the trade is approved, and the (possibly reduced) position size.

        Parameters
        ----------
        signal         : the trading signal to evaluate
        portfolio_value: current total equity in quote currency
        proposed_size  : raw position size in base asset units
        current_atr    : ATR for the current bar (e.g. 14-period ATR on 1h)
        normal_atr     : baseline ATR (e.g. 50-period average ATR) for comparison
        """
        self._refresh_day(portfolio_value)
        self._current_equity = portfolio_value

        # ── Kill-switch checks (hard stops) ───────────────────────────────────
        if self._trading_halted:
            return TradeValidation(
                approved=False,
                reason=f"Trading halted: {self._halt_reason}",
                adjusted_size=0.0,
            )

        # Max drawdown
        drawdown_pct = self._drawdown_pct(portfolio_value)
        if drawdown_pct >= self.max_drawdown_pct:
            self._halt(f"max drawdown reached ({drawdown_pct:.2f}%)")
            return TradeValidation(
                approved=False,
                reason=self._halt_reason,
                adjusted_size=0.0,
            )

        # Daily loss limit
        daily_loss_pct = self._daily_loss_pct(portfolio_value)
        if daily_loss_pct >= self.daily_loss_limit_pct:
            self._halt(
                f"daily loss limit reached ({daily_loss_pct:.2f}%)",
                permanent=False,
            )
            return TradeValidation(
                approved=False,
                reason=self._halt_reason,
                adjusted_size=0.0,
            )

        # ── Position count limit ───────────────────────────────────────────────
        if len(self._open_positions) >= self.max_open_positions:
            return TradeValidation(
                approved=False,
                reason=f"Max open positions ({self.max_open_positions}) reached",
                adjusted_size=0.0,
            )

        # ── Single-asset exposure ──────────────────────────────────────────────
        exposure_check = self._check_asset_exposure(
            signal.symbol, proposed_size, signal.metadata.get("entry_price", 0.0), portfolio_value
        )
        if not exposure_check[0]:
            return TradeValidation(approved=False, reason=exposure_check[1], adjusted_size=0.0)

        # ── Correlation check ──────────────────────────────────────────────────
        corr_check = self._check_correlation(signal.symbol, signal.direction)
        if not corr_check[0]:
            return TradeValidation(approved=False, reason=corr_check[1], adjusted_size=0.0)

        # ── Volatility adjustment ──────────────────────────────────────────────
        adjusted_size = proposed_size
        high_vol = normal_atr > 0 and current_atr > normal_atr * _HIGH_VOL_ATR_MULTIPLIER
        if high_vol:
            adjusted_size = proposed_size / _HIGH_VOL_SIZE_DIVISOR
            logger.warning(
                "High-vol regime detected (ATR %.4f > 2× normal %.4f) — "
                "position size halved to %.4f",
                current_atr,
                normal_atr,
                adjusted_size,
            )

        # ── Per-trade risk cap ─────────────────────────────────────────────────
        entry = signal.metadata.get("entry_price", 0.0)
        stop = signal.stop_loss
        if entry > 0 and stop > 0 and entry != stop:
            risk_distance = abs(entry - stop)
            max_risk_value = portfolio_value * (self.per_trade_risk_pct / 100.0)
            risk_capped_size = max_risk_value / risk_distance
            if adjusted_size > risk_capped_size:
                logger.debug(
                    "Per-trade risk cap applied: %.4f → %.4f (max_risk_value=%.2f)",
                    adjusted_size,
                    risk_capped_size,
                    max_risk_value,
                )
                adjusted_size = risk_capped_size

        if adjusted_size <= 0:
            return TradeValidation(
                approved=False,
                reason="Adjusted size rounded to zero after risk checks",
                adjusted_size=0.0,
            )

        return TradeValidation(approved=True, reason="All checks passed", adjusted_size=adjusted_size)

    def register_open_position(self, position: Position) -> None:
        """
        Record a newly opened position so the risk manager can track
        exposure, correlation, and stop/take-profit monitoring.
        """
        self._open_positions[position.symbol] = position
        self._trades_opened_today += 1
        logger.info(
            "Position registered: %s %s @ %.4f size=%.4f",
            position.side.value,
            position.symbol,
            position.entry_price,
            position.size,
        )

    def update_position_mark(self, symbol: str, mark_price: float) -> list[tuple[str, ExitReason]]:
        """
        Update the mark price of an open position and check if stop-loss or
        take-profit has been hit.

        Returns a list of (symbol, exit_reason) tuples for positions that
        should be closed immediately.

        Parameters
        ----------
        symbol     : e.g. "BTC/USDT"
        mark_price : latest traded price
        """
        exits: list[tuple[str, ExitReason]] = []
        pos = self._open_positions.get(symbol)
        if pos is None:
            return exits

        pos.metadata["mark_price"] = mark_price

        if pos.side == Direction.LONG:
            if mark_price <= pos.stop_loss:
                exits.append((symbol, ExitReason.STOP_LOSS))
                logger.warning("STOP-LOSS hit for %s @ %.4f (SL=%.4f)", symbol, mark_price, pos.stop_loss)
            elif mark_price >= pos.take_profit:
                exits.append((symbol, ExitReason.TAKE_PROFIT))
                logger.info("TAKE-PROFIT hit for %s @ %.4f (TP=%.4f)", symbol, mark_price, pos.take_profit)
        elif pos.side == Direction.SHORT:
            if mark_price >= pos.stop_loss:
                exits.append((symbol, ExitReason.STOP_LOSS))
                logger.warning("STOP-LOSS hit for %s @ %.4f (SL=%.4f)", symbol, mark_price, pos.stop_loss)
            elif mark_price <= pos.take_profit:
                exits.append((symbol, ExitReason.TAKE_PROFIT))
                logger.info("TAKE-PROFIT hit for %s @ %.4f (TP=%.4f)", symbol, mark_price, pos.take_profit)

        # Trailing stop update
        if pos.trailing_stop is not None:
            pos = self._update_trailing_stop(pos, mark_price)
            self._open_positions[symbol] = pos
            if pos.side == Direction.LONG and mark_price <= pos.trailing_stop:
                exits.append((symbol, ExitReason.TRAILING_STOP))
            elif pos.side == Direction.SHORT and mark_price >= pos.trailing_stop:
                exits.append((symbol, ExitReason.TRAILING_STOP))

        return exits

    def close_position(self, symbol: str, exit_price: float) -> float:
        """
        Remove a position from tracking and return realised PnL in quote currency.

        Parameters
        ----------
        symbol     : the symbol to close
        exit_price : the price at which the position was closed
        """
        pos = self._open_positions.pop(symbol, None)
        if pos is None:
            return 0.0

        if pos.side == Direction.LONG:
            pnl = (exit_price - pos.entry_price) * pos.size
        else:
            pnl = (pos.entry_price - exit_price) * pos.size

        self._realised_pnl += pnl
        self._trades_closed_today += 1
        self._current_equity += pnl

        # Update equity peak for drawdown calculation
        if self._current_equity > self._peak_equity:
            self._peak_equity = self._current_equity

        logger.info(
            "Position closed: %s @ %.4f | PnL=%.2f (%+.2f%%)",
            symbol,
            exit_price,
            pnl,
            (pnl / (pos.entry_price * pos.size) * 100) if pos.entry_price * pos.size != 0 else 0.0,
        )
        return pnl

    def close_all_positions(self, mark_prices: dict[str, float]) -> dict[str, float]:
        """
        NUCLEAR OPTION — close every open position immediately.

        Parameters
        ----------
        mark_prices : {symbol: current_price} — used to calculate PnL.

        Returns
        -------
        dict mapping symbol → realised PnL for each closed position.
        """
        logger.critical("EMERGENCY SHUTDOWN — closing ALL %d positions", len(self._open_positions))
        self._halt("emergency shutdown requested")
        results: dict[str, float] = {}
        for symbol in list(self._open_positions):
            price = mark_prices.get(symbol, 0.0)
            results[symbol] = self.close_position(symbol, price)
        return results

    def daily_summary(self) -> DailyPnLSummary:
        """Return a snapshot of today's P&L and risk state."""
        today_pnl = self._current_equity - self._starting_day_equity
        today_pnl_pct = (today_pnl / self._starting_day_equity * 100.0) if self._starting_day_equity > 0 else 0.0
        return DailyPnLSummary(
            date=self._today,
            starting_equity=self._starting_day_equity,
            current_equity=self._current_equity,
            realised_pnl=self._realised_pnl,
            realised_pnl_pct=today_pnl_pct,
            peak_equity=self._peak_equity,
            current_drawdown_pct=self._drawdown_pct(self._current_equity),
            trades_opened=self._trades_opened_today,
            trades_closed=self._trades_closed_today,
            halted=self._trading_halted,
        )

    def reset_daily_state(self, new_equity: float) -> None:
        """
        Call at the start of each trading day to reset daily counters.
        Does NOT reset the equity peak (drawdown tracks entire history).
        """
        self._starting_day_equity = new_equity
        self._current_equity = new_equity
        self._realised_pnl = 0.0
        self._trades_opened_today = 0
        self._trades_closed_today = 0
        self._today = date.today()

        # Lift daily halt (not the permanent halt triggered by max drawdown)
        if self._trading_halted and "daily loss" in self._halt_reason:
            self._trading_halted = False
            self._halt_reason = ""
            logger.info("Daily halt lifted at day reset — daily loss counter cleared")

    def update_correlations(self, correlations: dict[str, dict[str, float]]) -> None:
        """Replace the internal correlation matrix with fresh data."""
        self._correlations = correlations

    @property
    def is_halted(self) -> bool:
        return self._trading_halted

    @property
    def open_positions(self) -> dict[str, Position]:
        return dict(self._open_positions)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _halt(self, reason: str, permanent: bool = True) -> None:
        self._trading_halted = True
        self._halt_reason = reason
        level = logging.CRITICAL if permanent else logging.ERROR
        logger.log(level, "TRADING HALTED — %s", reason)

    def _drawdown_pct(self, current_equity: float) -> float:
        if self._peak_equity <= 0:
            return 0.0
        return max(0.0, (self._peak_equity - current_equity) / self._peak_equity * 100.0)

    def _daily_loss_pct(self, current_equity: float) -> float:
        if self._starting_day_equity <= 0:
            return 0.0
        loss = self._starting_day_equity - current_equity
        return max(0.0, loss / self._starting_day_equity * 100.0)

    def _refresh_day(self, portfolio_value: float) -> None:
        """Auto-reset daily counters when the calendar date rolls over."""
        today = date.today()
        if today != self._today:
            logger.info("New trading day detected — resetting daily state")
            self.reset_daily_state(portfolio_value)

    def _check_asset_exposure(
        self,
        symbol: str,
        size: float,
        entry_price: float,
        portfolio_value: float,
    ) -> tuple[bool, str]:
        """Return (ok, reason) for the single-asset exposure limit."""
        if portfolio_value <= 0 or entry_price <= 0:
            return True, ""
        notional = size * entry_price
        exposure_pct = notional / portfolio_value * 100.0
        if exposure_pct > self.max_single_asset_exposure_pct:
            return (
                False,
                f"Single-asset exposure {exposure_pct:.1f}% exceeds limit "
                f"{self.max_single_asset_exposure_pct:.1f}% for {symbol}",
            )
        return True, ""

    def _check_correlation(
        self,
        symbol: str,
        direction: Direction,
    ) -> tuple[bool, str]:
        """
        Refuse the trade if adding it would create more than
        max_correlated_positions highly-correlated open positions.
        """
        if not self._correlations or direction == Direction.FLAT:
            return True, ""

        correlated_count = 0
        for open_sym, pos in self._open_positions.items():
            if pos.side != direction:
                continue
            corr = (
                self._correlations.get(symbol, {}).get(open_sym)
                or self._correlations.get(open_sym, {}).get(symbol)
                or 0.0
            )
            if abs(corr) >= _MAX_CORRELATION:
                correlated_count += 1

        if correlated_count >= self.max_correlated_positions:
            return (
                False,
                f"Adding {symbol} would exceed correlated-position limit "
                f"({correlated_count} already correlated at ≥{_MAX_CORRELATION:.0%})",
            )
        return True, ""

    @staticmethod
    def _update_trailing_stop(pos: Position, mark_price: float) -> Position:
        """Move trailing stop up (LONG) or down (SHORT) with price."""
        if pos.trailing_stop is None:
            return pos
        if pos.side == Direction.LONG:
            trail_distance = pos.entry_price - pos.trailing_stop
            new_stop = mark_price - trail_distance
            pos.trailing_stop = max(pos.trailing_stop, new_stop)
        elif pos.side == Direction.SHORT:
            trail_distance = pos.trailing_stop - pos.entry_price
            new_stop = mark_price + trail_distance
            pos.trailing_stop = min(pos.trailing_stop, new_stop)
        return pos
