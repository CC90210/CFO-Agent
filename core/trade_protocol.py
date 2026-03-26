"""
core/trade_protocol.py
-----------------------
Atlas Trade Protocol — the step-by-step decision framework every trade must pass
through before execution. This is the "brain" of Atlas's trading discipline.

NO trade executes without completing ALL protocol steps.
NO shortcut exists. Even in fast-moving markets, the protocol runs.

Protocol Steps
--------------
1. REGIME CHECK     — What market are we in? (Bull/Bear/Choppy/HighVol)
2. SIGNAL GATHER    — Collect signals from all active strategies
3. CONFLUENCE CHECK — Do multiple independent signals agree?
4. RISK GATE        — Does this trade pass all risk controls?
5. SIZING           — How large should this position be?
6. ENTRY TIMING     — Where exactly should we enter?
7. EXIT PLAN        — Pre-define stop, target, and trailing stop BEFORE entry
8. EXECUTION        — Place the order
9. MONITOR          — Track the trade with trailing stops
10. POST-MORTEM     — After close, update performance and learn

This module provides the TradeProtocol class that orchestrates all steps
and produces a complete audit trail.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import pandas as pd

from core.regime_detector import MarketRegime, RegimeDetector, RegimeResult

logger = logging.getLogger("atlas.protocol")


class ProtocolStep(str, Enum):
    REGIME_CHECK = "REGIME_CHECK"
    SIGNAL_GATHER = "SIGNAL_GATHER"
    CONFLUENCE_CHECK = "CONFLUENCE_CHECK"
    RISK_GATE = "RISK_GATE"
    SIZING = "SIZING"
    ENTRY_TIMING = "ENTRY_TIMING"
    EXIT_PLAN = "EXIT_PLAN"
    EXECUTION = "EXECUTION"
    MONITOR = "MONITOR"
    POST_MORTEM = "POST_MORTEM"


class ProtocolVerdict(str, Enum):
    PROCEED = "PROCEED"
    SKIP = "SKIP"           # No signal — nothing to do
    REJECT_REGIME = "REJECT_REGIME"       # Regime too dangerous
    REJECT_CONFLUENCE = "REJECT_CONFLUENCE"  # Not enough agreement
    REJECT_RISK = "REJECT_RISK"           # Risk limits breached
    REJECT_SIZING = "REJECT_SIZING"       # Position too small to be meaningful
    REJECT_TIMING = "REJECT_TIMING"       # Bad entry timing


@dataclass
class ProtocolResult:
    """Complete audit trail for a single protocol run."""
    symbol: str
    verdict: ProtocolVerdict
    steps_completed: list[str] = field(default_factory=list)
    regime: MarketRegime | None = None
    regime_confidence: float = 0.0
    signals_count: int = 0
    confluence_score: float = 0.0
    risk_score: float = 0.0
    position_size_pct: float = 0.0
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    trailing_stop_method: str = ""
    reasoning: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_ms: float = 0.0

    def summary(self) -> str:
        """One-line summary for logging."""
        if self.verdict == ProtocolVerdict.PROCEED:
            return (
                f"{self.symbol} TRADE | {self.regime.value if self.regime else '?'} regime | "
                f"confluence={self.confluence_score:.2f} risk={self.risk_score:.1f} "
                f"size={self.position_size_pct:.2f}% | "
                f"entry={self.entry_price:.2f} stop={self.stop_loss:.2f} "
                f"target={self.take_profit:.2f}"
            )
        return f"{self.symbol} {self.verdict.value} after {self.steps_completed[-1] if self.steps_completed else 'start'}"


@dataclass
class ExitPlan:
    """Pre-defined exit strategy — set BEFORE entering any trade."""
    stop_loss: float
    take_profit: float
    trailing_stop_method: str = "chandelier"  # chandelier, atr, parabolic
    trailing_stop_atr_mult: float = 3.0
    break_even_trigger_atr: float = 1.0  # Move stop to break-even after this much profit in ATR
    max_hold_bars: int = 0  # 0 = no time limit
    scale_out_levels: list[dict[str, float]] = field(default_factory=list)

    def __post_init__(self):
        if not self.scale_out_levels:
            # Default: take 50% at 2:1 R:R, let 50% run with trailing stop
            risk = abs(self.take_profit - self.stop_loss) if self.stop_loss else 0
            if risk > 0:
                self.scale_out_levels = [
                    {"pct": 0.50, "target_rr": 2.0},  # Close 50% at 2:1
                    {"pct": 0.50, "target_rr": 0.0},   # Let rest run with trailing
                ]


class TradeProtocol:
    """
    The master protocol that every trade must pass through.

    Usage:
        protocol = TradeProtocol()
        result = protocol.evaluate(
            symbol="BTC/USDT",
            df=ohlcv_dataframe,
            signals=list_of_strategy_signals,
            current_equity=10000,
            open_positions=2,
            daily_pnl_pct=-1.5,
        )
        if result.verdict == ProtocolVerdict.PROCEED:
            execute_trade(result)
    """

    def __init__(
        self,
        min_confluence: float = 0.15,  # 2026-03-25: Lowered from 0.4 — engine adaptive threshold already gates quality
        max_risk_score: float = 7.0,
        min_position_pct: float = 0.001,
        regime_detector: RegimeDetector | None = None,
    ) -> None:
        self.min_confluence = min_confluence
        self.max_risk_score = max_risk_score
        self.min_position_pct = min_position_pct
        self._regime_detector = regime_detector or RegimeDetector()

    def evaluate(
        self,
        symbol: str,
        df: pd.DataFrame,
        signals: list[dict[str, Any]],
        current_equity: float,
        open_positions: int = 0,
        daily_pnl_pct: float = 0.0,
        max_drawdown_pct: float = 0.0,
    ) -> ProtocolResult:
        """
        Run the full protocol for a potential trade.

        Parameters
        ----------
        symbol         : Trading pair (e.g., "BTC/USDT")
        df             : Recent OHLCV DataFrame (50+ bars recommended)
        signals        : List of signal dicts from strategies
                         Each must have: direction, conviction, strategy_name,
                         stop_loss, take_profit
        current_equity : Portfolio equity in quote currency
        open_positions : Number of currently open positions
        daily_pnl_pct  : Today's realised P&L as percentage
        max_drawdown_pct: Current drawdown from peak as percentage

        Returns
        -------
        ProtocolResult with full audit trail.
        """
        import time
        start = time.monotonic()
        result = ProtocolResult(symbol=symbol, verdict=ProtocolVerdict.SKIP)

        # ── Step 1: REGIME CHECK ──────────────────────────────────────
        regime_result = self._step_regime_check(df)
        result.regime = regime_result.regime
        result.regime_confidence = regime_result.confidence
        result.steps_completed.append(ProtocolStep.REGIME_CHECK.value)
        result.reasoning.append(
            f"Regime: {regime_result.regime.value} "
            f"(conf={regime_result.confidence:.2f}, "
            f"Sharpe={regime_result.rolling_sharpe:.2f}, "
            f"vol_ratio={regime_result.volatility_ratio:.2f})"
        )

        # In HIGH_VOL regime with high confidence, reduce activity
        if regime_result.regime == MarketRegime.HIGH_VOL and regime_result.confidence > 0.8:
            result.verdict = ProtocolVerdict.REJECT_REGIME
            result.reasoning.append("HIGH_VOL regime with >80% confidence — sitting out")
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        # ── Step 2: SIGNAL GATHER ─────────────────────────────────────
        if not signals:
            result.verdict = ProtocolVerdict.SKIP
            result.steps_completed.append(ProtocolStep.SIGNAL_GATHER.value)
            result.reasoning.append("No signals from any strategy")
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        result.signals_count = len(signals)
        result.steps_completed.append(ProtocolStep.SIGNAL_GATHER.value)

        # Apply regime weights to signal convictions
        strategy_weights = regime_result.strategy_weights()
        for sig in signals:
            weight = strategy_weights.get(sig.get("strategy_name", ""), 1.0)
            sig["regime_adjusted_conviction"] = sig.get("conviction", 0) * weight

        result.reasoning.append(
            f"Gathered {len(signals)} signals, applied {regime_result.regime.value} weights"
        )

        # ── Step 3: CONFLUENCE CHECK ──────────────────────────────────
        confluence = self._step_confluence_check(signals)
        result.confluence_score = confluence["score"]
        result.steps_completed.append(ProtocolStep.CONFLUENCE_CHECK.value)

        if abs(confluence["score"]) < self.min_confluence:
            result.verdict = ProtocolVerdict.REJECT_CONFLUENCE
            result.reasoning.append(
                f"Confluence {confluence['score']:.2f} below "
                f"threshold {self.min_confluence} — no trade"
            )
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        result.reasoning.append(
            f"Confluence: {confluence['score']:+.2f} "
            f"({confluence['bulls']} bulls, {confluence['bears']} bears, "
            f"{confluence['neutrals']} neutral)"
        )

        # ── Step 4: RISK GATE ─────────────────────────────────────────
        risk = self._step_risk_gate(
            current_equity, open_positions, daily_pnl_pct, max_drawdown_pct
        )
        result.risk_score = risk["score"]
        result.steps_completed.append(ProtocolStep.RISK_GATE.value)

        if risk["vetoed"]:
            result.verdict = ProtocolVerdict.REJECT_RISK
            result.reasoning.append(f"Risk gate vetoed: {risk['reason']}")
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        result.reasoning.append(f"Risk gate passed (score={risk['score']:.1f}/10)")

        # ── Step 5: SIZING ────────────────────────────────────────────
        size_pct = self._step_sizing(
            confluence["score"], risk["score"],
            regime_result.size_multiplier(), current_equity
        )
        result.position_size_pct = size_pct
        result.steps_completed.append(ProtocolStep.SIZING.value)

        if size_pct < self.min_position_pct:
            result.verdict = ProtocolVerdict.REJECT_SIZING
            result.reasoning.append(f"Position size {size_pct:.4f}% too small")
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        result.reasoning.append(f"Position sized at {size_pct:.3f}% of equity")

        # ── Step 6: ENTRY TIMING ──────────────────────────────────────
        entry_price = float(df["close"].iloc[-1])
        result.entry_price = entry_price
        result.steps_completed.append(ProtocolStep.ENTRY_TIMING.value)
        result.reasoning.append(f"Entry at current close: {entry_price:.2f}")

        # ── Step 7: EXIT PLAN ─────────────────────────────────────────
        best_signal = max(signals, key=lambda s: abs(s.get("regime_adjusted_conviction", 0)))
        result.stop_loss = best_signal.get("stop_loss", 0)
        result.take_profit = best_signal.get("take_profit", 0)
        result.trailing_stop_method = "chandelier"
        result.steps_completed.append(ProtocolStep.EXIT_PLAN.value)
        result.reasoning.append(
            f"Exit plan: stop={result.stop_loss:.2f}, "
            f"target={result.take_profit:.2f}, trailing=chandelier"
        )

        # ── FINAL: PROCEED ────────────────────────────────────────────
        result.verdict = ProtocolVerdict.PROCEED
        result.steps_completed.append("APPROVED")
        result.duration_ms = (time.monotonic() - start) * 1000

        logger.info("Protocol APPROVED: %s", result.summary())
        return result

    # ------------------------------------------------------------------
    # Protocol step implementations
    # ------------------------------------------------------------------

    def _step_regime_check(self, df: pd.DataFrame) -> RegimeResult:
        return self._regime_detector.detect(df)

    def _step_confluence_check(self, signals: list[dict[str, Any]]) -> dict[str, Any]:
        """Score how well signals agree with each other."""
        bulls = [s for s in signals if s.get("direction") == "LONG"]
        bears = [s for s in signals if s.get("direction") == "SHORT"]
        neutrals = [s for s in signals if s.get("direction") not in ("LONG", "SHORT")]

        # Weighted consensus using regime-adjusted convictions
        total_weight = 0.0
        weighted_sum = 0.0
        for sig in signals:
            conv = sig.get("regime_adjusted_conviction", sig.get("conviction", 0))
            if sig.get("direction") in ("LONG", "SHORT"):
                weight = 1.0
                weighted_sum += conv * weight
                total_weight += weight

        score = weighted_sum / total_weight if total_weight > 0 else 0.0
        return {
            "score": max(-1.0, min(1.0, score)),
            "bulls": len(bulls),
            "bears": len(bears),
            "neutrals": len(neutrals),
        }

    def _step_risk_gate(
        self,
        equity: float,
        open_positions: int,
        daily_pnl_pct: float,
        max_drawdown_pct: float,
    ) -> dict[str, Any]:
        """Hard and soft risk checks."""
        score = 0.0
        reasons = []

        # Hard vetoes (non-negotiable)
        if max_drawdown_pct <= -15.0:
            return {"vetoed": True, "score": 10.0, "reason": "Max drawdown >= 15% — ALL TRADING HALTED"}
        if daily_pnl_pct <= -5.0:
            return {"vetoed": True, "score": 10.0, "reason": "Daily loss >= 5% — halted for the day"}
        if open_positions >= 5:
            return {"vetoed": True, "score": 8.0, "reason": "Max 5 open positions reached"}

        # Soft scoring
        if max_drawdown_pct <= -10.0:
            score += 3.0
            reasons.append("DD approaching limit")
        elif max_drawdown_pct <= -7.0:
            score += 1.5

        if daily_pnl_pct <= -3.0:
            score += 2.0
            reasons.append("Daily loss approaching limit")
        elif daily_pnl_pct <= -2.0:
            score += 1.0

        score += open_positions * 0.5  # More positions = more risk

        if score > self.max_risk_score:
            return {"vetoed": True, "score": score, "reason": f"Risk score {score:.1f} > {self.max_risk_score}"}

        return {"vetoed": False, "score": score, "reason": ""}

    def _step_sizing(
        self,
        confluence: float,
        risk_score: float,
        regime_multiplier: float,
        equity: float,
    ) -> float:
        """Calculate position size as % of equity."""
        # Base size: 1.5% of equity (max per-trade risk)
        base_pct = 0.015

        # Scale by conviction strength
        conviction_scalar = min(abs(confluence), 1.0)

        # Scale by risk inverse (higher risk = smaller size)
        risk_scalar = max(0.2, 1.0 - risk_score / 10.0)

        # Scale by regime
        final_pct = base_pct * conviction_scalar * risk_scalar * regime_multiplier

        # Hard cap at 1.5% of equity
        return min(final_pct, 0.015)
