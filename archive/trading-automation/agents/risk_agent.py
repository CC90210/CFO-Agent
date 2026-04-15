"""
agents/risk_agent.py
---------------------
Risk Manager Agent — the only agent with VETO POWER over trade decisions.

Veto conditions (automatic, no Claude required):
  1. Portfolio drawdown exceeds MAX_DRAWDOWN_PCT
  2. Daily loss exceeds DAILY_LOSS_LIMIT_PCT
  3. Single trade risk exceeds PER_TRADE_RISK_PCT
  4. More than 3 correlated long/short positions in same direction
  5. ATR spike > 3x the rolling average ATR (volatility regime change)

Claude is used for complex risk scenarios that don't trigger automatic vetoes
but warrant deeper assessment (risk score > 5 from rules → Claude validates).

Risk score scale: 0 (safe) → 10 (maximum risk). Trades with score > 7 are vetoed.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction
from config.settings import settings

logger = logging.getLogger(__name__)


class VetoReason(str, Enum):
    """Enumeration of all automatic veto triggers."""

    MAX_DRAWDOWN = "MAX_DRAWDOWN_EXCEEDED"
    DAILY_LOSS = "DAILY_LOSS_LIMIT_EXCEEDED"
    POSITION_SIZE = "POSITION_SIZE_TOO_LARGE"
    CORRELATION = "TOO_MANY_CORRELATED_POSITIONS"
    VOLATILITY_SPIKE = "VOLATILITY_SPIKE_DETECTED"
    RISK_SCORE_HIGH = "RISK_SCORE_ABOVE_THRESHOLD"
    NO_VETO = "NO_VETO"


@dataclass
class RiskAssessment:
    """Full risk assessment output from the RiskAgent."""

    vetoed: bool
    veto_reason: VetoReason
    risk_score: float        # 0–10
    recommended_size_pct: float  # 0–1 (fraction of max allowed size)
    reasoning: str
    portfolio_exposure_pct: float
    daily_pnl_pct: float
    max_drawdown_pct: float
    warnings: list[str]


class RiskAgent(BaseAnalystAgent):
    """
    Portfolio risk manager with hard stop rules and soft Claude assessment.

    Expected market_data shape (also serves as the risk context):
        {
            "portfolio": {
                "equity": float,
                "peak_equity": float,
                "daily_start_equity": float,
                "positions": [
                    {
                        "symbol": str,
                        "direction": "LONG" | "SHORT",
                        "size_usd": float,
                        "unrealised_pnl_pct": float,
                    }
                ]
            },
            "proposed_trade": {
                "symbol": str,
                "direction": "LONG" | "SHORT",
                "size_usd": float,
                "signal_conviction": float,
            },
            "market_conditions": {
                "current_atr": float,
                "average_atr": float,   # rolling 20-bar average
            }
        }
    """

    @property
    def name(self) -> str:
        return "RiskAgent"

    # ------------------------------------------------------------------
    # Main implementation
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        assessment = await self.assess_risk(symbol, market_data, context)

        direction = Direction.NEUTRAL if assessment.vetoed else Direction.LONG
        conviction = 0.0 if assessment.vetoed else (1.0 - assessment.risk_score / 10.0)

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=assessment.reasoning,
            confidence=0.95,  # Risk rules are deterministic — high confidence
            metadata={"risk_assessment": assessment.__dict__},
        )

    # ------------------------------------------------------------------
    # Core risk assessment (public method used directly by orchestrator)
    # ------------------------------------------------------------------

    async def assess_risk(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> RiskAssessment:
        """
        Perform full risk assessment. Returns RiskAssessment with veto decision.
        This method is called directly by the Orchestrator — not via analyze().
        """
        portfolio = market_data.get("portfolio", {})
        trade = market_data.get("proposed_trade", {})
        conditions = market_data.get("market_conditions", {})
        warnings: list[str] = []

        equity = float(portfolio.get("equity", 100_000))
        peak_equity = float(portfolio.get("peak_equity", equity))
        daily_start = float(portfolio.get("daily_start_equity", equity))
        positions = portfolio.get("positions", [])

        trade_size_usd = float(trade.get("size_usd", 0))
        trade_direction = str(trade.get("direction", "LONG")).upper()
        signal_conviction = float(trade.get("signal_conviction", 0.5))

        # ── Computed metrics ───────────────────────────────────────────
        drawdown_pct = ((peak_equity - equity) / peak_equity * 100) if peak_equity > 0 else 0.0
        daily_pnl_pct = ((equity - daily_start) / daily_start * 100) if daily_start > 0 else 0.0
        portfolio_exposure_pct = (trade_size_usd / equity * 100) if equity > 0 else 0.0

        total_open_usd = sum(float(p.get("size_usd", 0)) for p in positions)
        total_exposure_pct = (total_open_usd / equity * 100) if equity > 0 else 0.0

        current_atr = float(conditions.get("current_atr", 0))
        avg_atr = float(conditions.get("average_atr", current_atr or 1))
        atr_ratio = current_atr / avg_atr if avg_atr > 0 else 1.0

        # Correlated positions in same direction
        same_direction_positions = [
            p for p in positions if p.get("direction", "").upper() == trade_direction
        ]

        # ── Hard veto checks ───────────────────────────────────────────
        if drawdown_pct >= settings.risk.max_drawdown_pct:
            return RiskAssessment(
                vetoed=True,
                veto_reason=VetoReason.MAX_DRAWDOWN,
                risk_score=10.0,
                recommended_size_pct=0.0,
                reasoning=(
                    f"HALT: Portfolio drawdown {drawdown_pct:.1f}% >= "
                    f"max allowed {settings.risk.max_drawdown_pct:.1f}%. "
                    "All trading suspended until drawdown recovers."
                ),
                portfolio_exposure_pct=portfolio_exposure_pct,
                daily_pnl_pct=daily_pnl_pct,
                max_drawdown_pct=drawdown_pct,
                warnings=["MAX_DRAWDOWN_HALT"],
            )

        if daily_pnl_pct <= -settings.risk.daily_loss_limit_pct:
            return RiskAssessment(
                vetoed=True,
                veto_reason=VetoReason.DAILY_LOSS,
                risk_score=10.0,
                recommended_size_pct=0.0,
                reasoning=(
                    f"STOP: Daily loss {abs(daily_pnl_pct):.1f}% >= "
                    f"daily limit {settings.risk.daily_loss_limit_pct:.1f}%. "
                    "No new trades for the rest of the day."
                ),
                portfolio_exposure_pct=portfolio_exposure_pct,
                daily_pnl_pct=daily_pnl_pct,
                max_drawdown_pct=drawdown_pct,
                warnings=["DAILY_LOSS_HALT"],
            )

        if portfolio_exposure_pct > settings.risk.per_trade_risk_pct:
            return RiskAssessment(
                vetoed=True,
                veto_reason=VetoReason.POSITION_SIZE,
                risk_score=8.0,
                recommended_size_pct=settings.risk.per_trade_risk_pct / portfolio_exposure_pct,
                reasoning=(
                    f"REJECT: Trade size {portfolio_exposure_pct:.1f}% of equity exceeds "
                    f"per-trade risk limit of {settings.risk.per_trade_risk_pct:.1f}%."
                ),
                portfolio_exposure_pct=portfolio_exposure_pct,
                daily_pnl_pct=daily_pnl_pct,
                max_drawdown_pct=drawdown_pct,
                warnings=["SIZE_OVER_LIMIT"],
            )

        if len(same_direction_positions) >= 3:
            return RiskAssessment(
                vetoed=True,
                veto_reason=VetoReason.CORRELATION,
                risk_score=7.5,
                recommended_size_pct=0.0,
                reasoning=(
                    f"REJECT: {len(same_direction_positions)} existing "
                    f"{trade_direction} positions — correlation limit of 3 reached."
                ),
                portfolio_exposure_pct=portfolio_exposure_pct,
                daily_pnl_pct=daily_pnl_pct,
                max_drawdown_pct=drawdown_pct,
                warnings=["CORRELATION_LIMIT"],
            )

        # ── Soft rule scoring ──────────────────────────────────────────
        risk_score = self._soft_risk_score(
            drawdown_pct=drawdown_pct,
            daily_pnl_pct=daily_pnl_pct,
            portfolio_exposure_pct=portfolio_exposure_pct,
            total_exposure_pct=total_exposure_pct,
            atr_ratio=atr_ratio,
            signal_conviction=signal_conviction,
            warnings=warnings,
        )

        # Volatility spike: reduce recommended size but don't auto-veto
        recommended_size_pct = 1.0
        if atr_ratio > 3.0:
            recommended_size_pct = 0.5
            warnings.append(f"ATR_SPIKE: current ATR is {atr_ratio:.1f}x average — size halved")

        # Hard score veto
        if risk_score > 7.0:
            # Attempt Claude validation before full veto
            try:
                risk_score, reasoning = await self._claude_risk_review(
                    symbol, portfolio, trade, conditions, risk_score, context or {}
                )
                if risk_score > 7.0:
                    return RiskAssessment(
                        vetoed=True,
                        veto_reason=VetoReason.RISK_SCORE_HIGH,
                        risk_score=risk_score,
                        recommended_size_pct=0.0,
                        reasoning=reasoning,
                        portfolio_exposure_pct=portfolio_exposure_pct,
                        daily_pnl_pct=daily_pnl_pct,
                        max_drawdown_pct=drawdown_pct,
                        warnings=warnings,
                    )
            except Exception as exc:
                logger.warning("%s: Claude risk review failed: %s", self.name, exc)
                if risk_score > 7.0:
                    return RiskAssessment(
                        vetoed=True,
                        veto_reason=VetoReason.RISK_SCORE_HIGH,
                        risk_score=risk_score,
                        recommended_size_pct=0.0,
                        reasoning=f"Risk score {risk_score:.1f}/10 exceeds threshold. Claude unavailable for review.",
                        portfolio_exposure_pct=portfolio_exposure_pct,
                        daily_pnl_pct=daily_pnl_pct,
                        max_drawdown_pct=drawdown_pct,
                        warnings=warnings,
                    )

        reasoning = (
            f"Risk score {risk_score:.1f}/10. "
            f"Drawdown: {drawdown_pct:.1f}%, daily P&L: {daily_pnl_pct:+.1f}%, "
            f"trade size: {portfolio_exposure_pct:.1f}% of equity. "
            f"Recommended size multiplier: {recommended_size_pct:.2f}."
        )
        if warnings:
            reasoning += f" Warnings: {', '.join(warnings)}."

        return RiskAssessment(
            vetoed=False,
            veto_reason=VetoReason.NO_VETO,
            risk_score=risk_score,
            recommended_size_pct=recommended_size_pct,
            reasoning=reasoning,
            portfolio_exposure_pct=portfolio_exposure_pct,
            daily_pnl_pct=daily_pnl_pct,
            max_drawdown_pct=drawdown_pct,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # Soft risk scoring (rules-based, no Claude)
    # ------------------------------------------------------------------

    def _soft_risk_score(
        self,
        drawdown_pct: float,
        daily_pnl_pct: float,
        portfolio_exposure_pct: float,
        total_exposure_pct: float,
        atr_ratio: float,
        signal_conviction: float,
        warnings: list[str],
    ) -> float:
        """
        Score risk 0–10 using weighted rules.
        Each factor contributes proportionally to its danger level.
        """
        score = 0.0

        # Drawdown proximity to limit (0–3 points)
        dd_fraction = drawdown_pct / settings.risk.max_drawdown_pct
        score += dd_fraction * 3.0
        if dd_fraction > 0.7:
            warnings.append(f"DRAWDOWN_WARNING: {drawdown_pct:.1f}% of {settings.risk.max_drawdown_pct:.1f}% limit")

        # Daily P&L proximity to limit (0–2 points)
        if daily_pnl_pct < 0:
            dl_fraction = abs(daily_pnl_pct) / settings.risk.daily_loss_limit_pct
            score += dl_fraction * 2.0

        # Total portfolio exposure (0–2 points)
        if total_exposure_pct > 50:
            score += 2.0
        elif total_exposure_pct > 30:
            score += 1.0

        # ATR volatility regime (0–2 points)
        if atr_ratio > 2.0:
            score += min(2.0, (atr_ratio - 2.0) * 1.5)

        # Low conviction = higher risk (0–1 point)
        if abs(signal_conviction) < 0.3:
            score += 1.0
        elif abs(signal_conviction) < 0.5:
            score += 0.5

        return min(10.0, score)

    # ------------------------------------------------------------------
    # Claude risk review
    # ------------------------------------------------------------------

    async def _claude_risk_review(
        self,
        symbol: str,
        portfolio: dict[str, Any],
        trade: dict[str, Any],
        conditions: dict[str, Any],
        initial_risk_score: float,
        context: dict[str, Any],
    ) -> tuple[float, str]:
        """
        Ask Claude to assess complex risk scenarios.
        Returns (revised_risk_score, reasoning).
        """
        system_prompt = (
            "You are a conservative portfolio risk manager at a professional hedge fund. "
            "Assess the risk of executing a proposed trade given the current portfolio "
            "state and market conditions. Risk score: 0 = safe, 10 = maximum risk. "
            "Score above 7 triggers a veto. Be conservative. "
            "Respond ONLY with valid JSON."
        )

        positions_summary = [
            f"  {p.get('symbol')}: {p.get('direction')} ${p.get('size_usd', 0):,.0f} "
            f"({p.get('unrealised_pnl_pct', 0):+.1f}%)"
            for p in portfolio.get("positions", [])
        ]

        user_message = f"""Risk review for proposed trade on {symbol}.

Portfolio state:
  Equity: ${portfolio.get('equity', 0):,.2f}
  Drawdown from peak: {((portfolio.get('peak_equity', 1) - portfolio.get('equity', 1)) / portfolio.get('peak_equity', 1) * 100):.1f}%
  Daily P&L: {((portfolio.get('equity', 1) - portfolio.get('daily_start_equity', 1)) / portfolio.get('daily_start_equity', 1) * 100):+.1f}%
  Open positions:
{chr(10).join(positions_summary) if positions_summary else "  None"}

Proposed trade:
  Symbol: {symbol}
  Direction: {trade.get('direction')}
  Size: ${trade.get('size_usd', 0):,.0f}
  Signal conviction: {trade.get('signal_conviction', 0.5):+.2f}

Market conditions:
  ATR: {conditions.get('current_atr', 'N/A')} (avg: {conditions.get('average_atr', 'N/A')})

Rules-based initial risk score: {initial_risk_score:.1f}/10

Macro context: {context.get('macro_environment', 'Not provided')}

Respond with this exact JSON:
{{
  "risk_score": <float 0.0 to 10.0>,
  "veto": <bool>,
  "key_risks": ["<risk1>", "<risk2>"],
  "reasoning": "<2-4 sentence assessment>"
}}"""

        raw = await self.call_claude(system_prompt, user_message, max_tokens=512)
        parsed = self._parse_json_response(raw)

        if "raw" in parsed:
            return initial_risk_score, f"Claude parse failed. Using rules-based score: {initial_risk_score:.1f}/10"

        risk_score = float(parsed.get("risk_score", initial_risk_score))
        reasoning = str(parsed.get("reasoning", ""))
        return risk_score, reasoning
