"""
agents/portfolio_manager.py
-----------------------------
Portfolio Manager — converts a debate verdict and risk assessment into a
concrete trade specification including position size, entry, stop, and target.

Sizing methodology:
  Half-Kelly:  f = 0.5 * (win_rate * avg_win - loss_rate * avg_loss) / avg_win
  Conviction scaling: size *= abs(conviction)   — low conviction → smaller size
  Risk scaling:       size *= risk_multiplier   — from RiskAssessment
  Hard cap:           size <= per_trade_risk_pct of equity

The portfolio manager also tracks running portfolio state (equity, daily P&L,
open positions) and generates end-of-day performance summaries.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction
from agents.debate import DebateVerdict
from agents.risk_agent import RiskAssessment
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class PositionSizing:
    """
    The output specification for a single trade entry.

    All USD amounts are denominated in the portfolio's base currency.
    size_usd = the actual notional of the trade (may be less than max allowed).
    """

    symbol: str
    direction: Direction
    size_usd: float
    size_pct_equity: float   # fraction of portfolio equity
    entry_price: float       # current mid-price (filled by exchange)
    stop_loss_price: float
    take_profit_price: float
    risk_reward_ratio: float
    kelly_fraction: float    # raw Half-Kelly output
    conviction_scalar: float # |conviction| applied to kelly size
    reasoning: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DailyPnLSummary:
    """End-of-day or on-demand P&L report."""

    date: str
    starting_equity: float
    current_equity: float
    realised_pnl: float
    unrealised_pnl: float
    total_pnl_pct: float
    trade_count: int
    win_count: int
    loss_count: int
    win_rate: float
    best_trade_pct: float
    worst_trade_pct: float


class PortfolioManager(BaseAnalystAgent):
    """
    Translates signals into executable trade specifications.

    The portfolio manager maintains mutable state (equity, positions) that
    must be updated by the orchestrator after each trade execution.
    """

    def __init__(self, initial_equity: float = 10_000.0) -> None:
        super().__init__()
        self.equity: float = initial_equity
        self.peak_equity: float = initial_equity
        self.daily_start_equity: float = initial_equity
        self.positions: list[dict[str, Any]] = []
        self.closed_trades: list[dict[str, Any]] = []
        self._daily_trade_count: int = 0

    @property
    def name(self) -> str:
        return "PortfolioManager"

    # ------------------------------------------------------------------
    # Primary public method (called by orchestrator)
    # ------------------------------------------------------------------

    def size_position(
        self,
        symbol: str,
        verdict: DebateVerdict,
        risk_assessment: RiskAssessment,
        current_price: float,
        historical_stats: dict[str, float] | None = None,
    ) -> PositionSizing | None:
        """
        Calculate position sizing given the debate verdict and risk assessment.
        Returns None if the trade should not be executed.
        """
        if risk_assessment.vetoed:
            logger.info(
                "%s: Trade vetoed for %s — %s", self.name, symbol, risk_assessment.veto_reason
            )
            return None

        if verdict.direction == Direction.NEUTRAL:
            logger.info("%s: Neutral verdict for %s — no trade", self.name, symbol)
            return None

        stats = historical_stats or {}
        win_rate = stats.get("win_rate", 0.50)
        avg_win_pct = stats.get("avg_win_pct", 2.0)
        avg_loss_pct = stats.get("avg_loss_pct", 1.5)

        # Half-Kelly position size as fraction of equity
        kelly_f = self._half_kelly(win_rate, avg_win_pct, avg_loss_pct)

        # Scale by conviction × confidence — high conviction with low confidence
        # should produce smaller sizes than high conviction with high confidence
        conviction_scalar = abs(verdict.conviction) * max(verdict.confidence, 0.1)
        risk_multiplier = risk_assessment.recommended_size_pct

        # Short positions carry higher tail risk — reduce by 15%
        direction_scalar = 0.85 if verdict.direction == Direction.SHORT else 1.0

        raw_size_pct = kelly_f * conviction_scalar * risk_multiplier * direction_scalar

        # Hard cap: never risk more than per_trade_risk_pct
        max_pct = settings.risk.per_trade_risk_pct / 100.0
        size_pct = min(raw_size_pct, max_pct)

        # Minimum meaningful trade
        if size_pct < 0.001:
            logger.info(
                "%s: Computed size %.3f%% too small — skipping %s",
                self.name, size_pct * 100, symbol,
            )
            return None

        size_usd = self.equity * size_pct

        # Stop loss / take profit based on ATR with adaptive R:R
        atr_pct = stats.get("atr_pct", 1.5)
        stop_pct = atr_pct * 1.5   # 1.5x ATR for stop

        # Adaptive R:R — lower win rate demands higher reward per trade
        if win_rate < 0.40:
            rr_target = 3.5   # Need big wins to compensate for frequent losses
        elif win_rate < 0.50:
            rr_target = 3.0   # Standard conservative R:R
        elif win_rate < 0.60:
            rr_target = 2.0   # Can afford tighter targets
        else:
            rr_target = 1.5   # High win rate — take profits faster

        target_pct = atr_pct * rr_target * 1.5  # ATR × R:R × stop multiplier

        if verdict.direction == Direction.LONG:
            stop_price = current_price * (1 - stop_pct / 100)
            target_price = current_price * (1 + target_pct / 100)
        else:  # SHORT
            stop_price = current_price * (1 + stop_pct / 100)
            target_price = current_price * (1 - target_pct / 100)

        stop_distance = abs(current_price - stop_price)
        target_distance = abs(current_price - target_price)
        rr_ratio = target_distance / stop_distance if stop_distance > 0 else 1.0

        reasoning = (
            f"Half-Kelly={kelly_f:.3f} × conviction={conviction_scalar:.2f} × "
            f"risk_mult={risk_multiplier:.2f} → size={size_pct * 100:.2f}% of equity "
            f"(${size_usd:,.2f}). R/R={rr_ratio:.2f}:1. "
            f"Stop at {stop_price:.4f}, target at {target_price:.4f}."
        )

        self._daily_trade_count += 1

        return PositionSizing(
            symbol=symbol,
            direction=verdict.direction,
            size_usd=size_usd,
            size_pct_equity=size_pct,
            entry_price=current_price,
            stop_loss_price=stop_price,
            take_profit_price=target_price,
            risk_reward_ratio=rr_ratio,
            kelly_fraction=kelly_f,
            conviction_scalar=conviction_scalar,
            reasoning=reasoning,
            metadata={
                "win_rate_used": win_rate,
                "avg_win_pct": avg_win_pct,
                "avg_loss_pct": avg_loss_pct,
                "debate_conviction": verdict.conviction,
                "debate_confidence": verdict.confidence,
                "risk_score": risk_assessment.risk_score,
            },
        )

    # ------------------------------------------------------------------
    # Portfolio state management
    # ------------------------------------------------------------------

    def update_equity(self, new_equity: float) -> None:
        """Update equity after a mark-to-market or trade close."""
        self.equity = new_equity
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity

    def open_position(self, sizing: PositionSizing) -> None:
        """Record an opened position in portfolio state."""
        self.positions.append(
            {
                "symbol": sizing.symbol,
                "direction": sizing.direction.value,
                "size_usd": sizing.size_usd,
                "entry_price": sizing.entry_price,
                "stop_loss": sizing.stop_loss_price,
                "take_profit": sizing.take_profit_price,
                "opened_at": sizing.timestamp.isoformat(),
                "unrealised_pnl_pct": 0.0,
            }
        )

    def close_position(self, symbol: str, exit_price: float) -> dict[str, Any] | None:
        """
        Close the first matching position for symbol, compute P&L,
        and record in closed_trades.
        """
        for i, pos in enumerate(self.positions):
            if pos["symbol"] == symbol:
                entry = pos["entry_price"]
                direction = pos["direction"]
                size_usd = pos["size_usd"]

                if direction == "LONG":
                    pnl_pct = (exit_price - entry) / entry * 100
                else:
                    pnl_pct = (entry - exit_price) / entry * 100

                pnl_usd = size_usd * pnl_pct / 100
                self.equity += pnl_usd
                if self.equity > self.peak_equity:
                    self.peak_equity = self.equity

                trade_record = {
                    **pos,
                    "exit_price": exit_price,
                    "pnl_pct": pnl_pct,
                    "pnl_usd": pnl_usd,
                    "closed_at": datetime.now(UTC).isoformat(),
                }
                self.closed_trades.append(trade_record)
                self.positions.pop(i)
                return trade_record

        logger.warning("%s: No open position found for %s", self.name, symbol)
        return None

    def mark_to_market(self, symbol: str, current_price: float) -> None:
        """Update unrealised P&L for an open position."""
        for pos in self.positions:
            if pos["symbol"] == symbol:
                entry = pos["entry_price"]
                direction = pos["direction"]
                if direction == "LONG":
                    pos["unrealised_pnl_pct"] = (current_price - entry) / entry * 100
                else:
                    pos["unrealised_pnl_pct"] = (entry - current_price) / entry * 100
                break

    def reset_daily(self) -> None:
        """Call at the start of each trading day."""
        self.daily_start_equity = self.equity
        self._daily_trade_count = 0

    # ------------------------------------------------------------------
    # P&L reporting
    # ------------------------------------------------------------------

    def daily_summary(self) -> DailyPnLSummary:
        """Generate current-day P&L summary."""
        closed_today = [
            t for t in self.closed_trades
            if t.get("closed_at", "")[:10] == datetime.now(UTC).strftime("%Y-%m-%d")
        ]
        unrealised = sum(
            p.get("unrealised_pnl_pct", 0) * p.get("size_usd", 0) / 100
            for p in self.positions
        )
        realised = sum(t.get("pnl_usd", 0) for t in closed_today)
        total_pnl_pct = (
            (self.equity - self.daily_start_equity) / self.daily_start_equity * 100
            if self.daily_start_equity > 0 else 0.0
        )
        wins = [t for t in closed_today if t.get("pnl_pct", 0) > 0]
        losses = [t for t in closed_today if t.get("pnl_pct", 0) <= 0]
        pnl_pcts = [t.get("pnl_pct", 0) for t in closed_today]

        return DailyPnLSummary(
            date=datetime.now(UTC).strftime("%Y-%m-%d"),
            starting_equity=self.daily_start_equity,
            current_equity=self.equity,
            realised_pnl=realised,
            unrealised_pnl=unrealised,
            total_pnl_pct=total_pnl_pct,
            trade_count=len(closed_today),
            win_count=len(wins),
            loss_count=len(losses),
            win_rate=len(wins) / len(closed_today) if closed_today else 0.0,
            best_trade_pct=max(pnl_pcts) if pnl_pcts else 0.0,
            worst_trade_pct=min(pnl_pcts) if pnl_pcts else 0.0,
        )

    def build_portfolio_state(self) -> dict[str, Any]:
        """Build the portfolio state dict expected by RiskAgent."""
        return {
            "equity": self.equity,
            "peak_equity": self.peak_equity,
            "daily_start_equity": self.daily_start_equity,
            "positions": self.positions,
        }

    # ------------------------------------------------------------------
    # Half-Kelly calculation
    # ------------------------------------------------------------------

    @staticmethod
    def _half_kelly(
        win_rate: float,
        avg_win_pct: float,
        avg_loss_pct: float,
    ) -> float:
        """
        Half-Kelly fraction.

        f* = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
        half-Kelly = f* / 2

        Clipped to [0.01, 0.25] to prevent extremes.
        """
        loss_rate = 1.0 - win_rate
        if avg_win_pct <= 0:
            return 0.01

        kelly = (win_rate * avg_win_pct - loss_rate * avg_loss_pct) / avg_win_pct
        half = kelly / 2.0
        return max(0.01, min(0.25, half))

    # ------------------------------------------------------------------
    # Required by ABC (not typically called for this agent)
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        """Thin wrapper for use via the standard analyze() interface."""
        summary = self.daily_summary()
        return AgentSignal(
            agent_name=self.name,
            direction=Direction.NEUTRAL,
            conviction=0.0,
            reasoning=(
                f"Portfolio equity: ${self.equity:,.2f}. "
                f"Daily P&L: {summary.total_pnl_pct:+.2f}%. "
                f"Open positions: {len(self.positions)}."
            ),
            confidence=1.0,
            metadata={"daily_summary": summary.__dict__},
        )
