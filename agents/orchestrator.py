"""
agents/orchestrator.py
-----------------------
Agent Orchestrator — the top-level coordinator for the Atlas trading
intelligence framework.

Execution flow:
  1. Run all analyst agents in parallel (asyncio.gather)
  2. Apply Darwinian weights to signals
  3. If signals are in strong agreement → skip debate, proceed directly
  4. If signals conflict → run Bull/Bear debate via DebateEngine
  5. Submit proposed trade to RiskAgent for approval / veto
  6. If approved → PortfolioManager computes position sizing
  7. Return final TradeDecision with full audit chain

All decisions are logged for the Darwinian evolution system to use.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction
from agents.darwinian import DarwinianEvolutionEngine
from agents.debate import DebateEngine, DebateVerdict
from agents.fundamentals_analyst import FundamentalsAnalyst
from agents.news_analyst import NewsAnalyst
from agents.portfolio_manager import PortfolioManager, PositionSizing
from agents.risk_agent import RiskAgent, RiskAssessment
from agents.sentiment_analyst import SentimentAnalyst
from agents.technical_analyst import TechnicalAnalyst

logger = logging.getLogger(__name__)

# When the absolute value of the consensus conviction exceeds this threshold,
# skip the debate and go straight to risk assessment.
_SKIP_DEBATE_THRESHOLD = 0.75


@dataclass
class TradeDecision:
    """
    Final output of the orchestrator for a single analysis cycle.

    Fields
    ------
    execute:        Whether to proceed with the trade
    symbol:         Ticker or pair analysed
    signal:         The final AgentSignal from the debate verdict
    sizing:         Position sizing specification (None if vetoed / neutral)
    risk_score:     0–10 scale from the risk agent
    vetoed:         True if the risk agent blocked the trade
    reasoning_chain: Full ordered list of reasoning steps (for audit)
    agent_scores:   Individual signal summary per agent
    debate_verdict: Full debate output (None if debate was skipped)
    timestamp:      UTC time of decision
    """

    execute: bool
    symbol: str
    signal: AgentSignal
    sizing: PositionSizing | None
    risk_score: float
    vetoed: bool
    reasoning_chain: list[str]
    agent_scores: list[dict[str, Any]]
    debate_verdict: DebateVerdict | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """
    Top-level coordinator.

    Instantiate once and call ``run(symbol, market_data)`` for each
    analysis cycle. The orchestrator owns the portfolio state and
    all agent instances.
    """

    def __init__(
        self,
        initial_equity: float = 10_000.0,
        extra_analysts: list[BaseAnalystAgent] | None = None,
    ) -> None:
        # Core analyst agents
        self.technical = TechnicalAnalyst()
        self.sentiment = SentimentAnalyst()
        self.fundamentals = FundamentalsAnalyst()
        self.news = NewsAnalyst()

        # Additional pluggable analysts
        self._extra_analysts: list[BaseAnalystAgent] = extra_analysts or []

        # Infrastructure agents
        self.risk_agent = RiskAgent()
        self.debate_engine = DebateEngine()
        self.portfolio_manager = PortfolioManager(initial_equity=initial_equity)
        self.darwinian = DarwinianEvolutionEngine()

        # Register all analysts with the Darwinian engine
        for agent in self._all_analysts():
            self.darwinian.register_agent(agent)

        self._decision_log: list[TradeDecision] = []

    # ------------------------------------------------------------------
    # Primary public interface
    # ------------------------------------------------------------------

    async def run(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> TradeDecision:
        """
        Run a full multi-agent analysis cycle for ``symbol``.

        Parameters
        ----------
        symbol:      The trading pair or ticker (e.g. "BTC/USDT", "AAPL")
        market_data: Dict containing all data needed by all agents.
                     See individual agent docstrings for the exact shape.
                     Keys: "ohlcv", "timeframe", "asset_class", "portfolio",
                           "proposed_trade", "market_conditions", etc.
        context:     Optional extra context (macro environment, regime, etc.)

        Returns
        -------
        TradeDecision with full audit trail.
        """
        ctx = context or {}
        reasoning_chain: list[str] = []

        # ── Step 1: Parallel analyst execution ───────────────────────
        reasoning_chain.append(
            f"Step 1: Running {len(self._all_analysts())} analyst agents in parallel"
        )

        raw_signals = await self._gather_signals(symbol, market_data, ctx)

        # Remove NEUTRAL signals from non-fundamental agents for debate
        # but keep all for the audit log
        all_signals = raw_signals
        reasoning_chain.append(
            f"Step 2: Collected {len(all_signals)} signals. "
            f"Bulls={sum(1 for s in all_signals if s.direction == Direction.LONG)}, "
            f"Bears={sum(1 for s in all_signals if s.direction == Direction.SHORT)}, "
            f"Neutral={sum(1 for s in all_signals if s.direction == Direction.NEUTRAL)}"
        )

        # ── Step 2: Apply Darwinian weights to signals ─────────────
        weighted_signals = self._apply_agent_weights(all_signals)
        consensus = self._weighted_consensus(weighted_signals)
        reasoning_chain.append(
            f"Step 3: Weighted consensus conviction: {consensus:+.3f}"
        )

        # ── Step 3: Debate or fast-path ────────────────────────────
        debate_verdict: DebateVerdict | None = None
        if abs(consensus) >= _SKIP_DEBATE_THRESHOLD:
            # Strong agreement — skip debate
            reasoning_chain.append(
                f"Step 4: Consensus {consensus:+.2f} >= {_SKIP_DEBATE_THRESHOLD} threshold "
                "— debate skipped (strong agreement)"
            )
            final_direction = Direction.LONG if consensus > 0 else Direction.SHORT
            final_conviction = consensus
            final_confidence = min(0.9, abs(consensus))
            final_reasoning = (
                f"Strong {final_direction.value} consensus across {len(weighted_signals)} agents. "
                "Debate skipped."
            )
        else:
            # Conflicting signals — run debate
            reasoning_chain.append(
                "Step 4: Signals conflict — running Bull/Bear debate"
            )
            debate_verdict = await self.debate_engine.run_debate(
                symbol, weighted_signals, ctx
            )
            final_direction = debate_verdict.direction
            final_conviction = debate_verdict.conviction
            final_confidence = debate_verdict.confidence
            final_reasoning = " | ".join(debate_verdict.reasoning_chain)
            reasoning_chain.append(
                f"Step 4b: Debate verdict — {final_direction.value} "
                f"conviction={final_conviction:+.2f} confidence={final_confidence:.2f}"
            )

        # Build final composite signal
        final_signal = AgentSignal(
            agent_name="Orchestrator",
            direction=final_direction,
            conviction=final_conviction,
            reasoning=final_reasoning,
            confidence=final_confidence,
            metadata={
                "consensus": consensus,
                "debate_used": debate_verdict is not None,
            },
        )

        # ── Step 4: Risk assessment ─────────────────────────────────
        current_price = self._extract_current_price(market_data)
        proposed_trade_size = self._compute_proposed_size(final_conviction, current_price)

        risk_market_data = {
            "portfolio": self.portfolio_manager.build_portfolio_state(),
            "proposed_trade": {
                "symbol": symbol,
                "direction": final_direction.value,
                "size_usd": proposed_trade_size,
                "signal_conviction": final_conviction,
            },
            "market_conditions": market_data.get("market_conditions", {}),
        }

        risk_assessment = await self.risk_agent.assess_risk(symbol, risk_market_data, ctx)
        reasoning_chain.append(
            f"Step 5: Risk assessment — score={risk_assessment.risk_score:.1f}/10, "
            f"vetoed={risk_assessment.vetoed} ({risk_assessment.veto_reason.value})"
        )

        # ── Step 5: Position sizing ─────────────────────────────────
        sizing: PositionSizing | None = None
        if not risk_assessment.vetoed and final_direction != Direction.NEUTRAL:
            historical_stats = self._build_historical_stats(symbol)
            sizing = self.portfolio_manager.size_position(
                symbol=symbol,
                verdict=debate_verdict or self._mock_verdict(final_signal),
                risk_assessment=risk_assessment,
                current_price=current_price,
                historical_stats=historical_stats,
            )
            if sizing:
                reasoning_chain.append(
                    f"Step 6: Position sized — ${sizing.size_usd:,.2f} "
                    f"({sizing.size_pct_equity * 100:.2f}% equity), "
                    f"stop={sizing.stop_loss_price:.4f}, "
                    f"target={sizing.take_profit_price:.4f}"
                )

        # ── Step 6: Build final decision ───────────────────────────
        execute = (
            not risk_assessment.vetoed
            and sizing is not None
            and final_direction != Direction.NEUTRAL
        )

        agent_scores = self._build_agent_scores(all_signals)

        decision = TradeDecision(
            execute=execute,
            symbol=symbol,
            signal=final_signal,
            sizing=sizing,
            risk_score=risk_assessment.risk_score,
            vetoed=risk_assessment.vetoed,
            reasoning_chain=reasoning_chain,
            agent_scores=agent_scores,
            debate_verdict=debate_verdict,
            metadata={
                "risk_assessment": risk_assessment.__dict__,
                "consensus_conviction": consensus,
            },
        )

        self._decision_log.append(decision)

        logger.info(
            "Orchestrator: %s — execute=%s direction=%s conviction=%+.2f risk=%.1f",
            symbol,
            execute,
            final_direction.value,
            final_conviction,
            risk_assessment.risk_score,
        )

        # ── Step 7: Trigger weekly Darwinian review if due ─────────
        if self.darwinian.should_run_weekly_review():
            asyncio.create_task(self._run_darwinian_review())

        return decision

    # ------------------------------------------------------------------
    # Post-trade callbacks (call from your execution layer)
    # ------------------------------------------------------------------

    def record_trade_close(
        self,
        symbol: str,
        exit_price: float,
        entry_price: float,
    ) -> None:
        """
        Notify the orchestrator that a trade has closed.
        Updates portfolio state and triggers Darwinian weight adjustment.
        """
        # Find contributing signals from the most recent decision for this symbol
        contributing = []
        for dec in reversed(self._decision_log):
            if dec.symbol == symbol and dec.execute:
                contributing = [
                    AgentSignal(
                        agent_name=s["agent_name"],
                        direction=Direction(s["direction"]),
                        conviction=s["conviction"],
                        reasoning=s["reasoning"],
                        confidence=s["confidence"],
                    )
                    for s in dec.agent_scores
                ]
                break

        if contributing:
            self.darwinian.record_trade_outcome(
                symbol, exit_price, entry_price, contributing
            )

        self.portfolio_manager.close_position(symbol, exit_price)

    # ------------------------------------------------------------------
    # Signal gathering
    # ------------------------------------------------------------------

    async def _gather_signals(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> list[AgentSignal]:
        """
        Run all analyst agents concurrently.
        Any agent that raises an exception returns a NEUTRAL signal — it never
        crashes the orchestrator.
        """
        analysts = self._all_analysts()
        tasks = [agent.analyze(symbol, market_data, context) for agent in analysts]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        signals: list[AgentSignal] = []
        for agent, result in zip(analysts, results):
            if isinstance(result, Exception):
                logger.error(
                    "Orchestrator: %s raised %s — using NEUTRAL fallback",
                    agent.name,
                    result,
                )
                signals.append(AgentSignal.neutral(agent.name, reason=str(result)))
            else:
                signals.append(result)  # type: ignore[arg-type]

        return signals

    def _all_analysts(self) -> list[BaseAnalystAgent]:
        """Return the full list of registered analyst agents (not the infra agents)."""
        core = [self.technical, self.sentiment, self.fundamentals, self.news]
        return core + self._extra_analysts

    # ------------------------------------------------------------------
    # Weighting and consensus
    # ------------------------------------------------------------------

    def _apply_agent_weights(self, signals: list[AgentSignal]) -> list[AgentSignal]:
        """
        Inject Darwinian agent weights into signal metadata so the debate
        engine and consensus calculator can use them.
        """
        weighted: list[AgentSignal] = []
        for sig in signals:
            agent = self.darwinian.agents.get(sig.agent_name)
            weight = agent.weight if agent else 1.0
            # Store weight in metadata for downstream consumers
            enriched_metadata = {**sig.metadata, "agent_weight": weight}
            enriched = AgentSignal(
                agent_name=sig.agent_name,
                direction=sig.direction,
                conviction=sig.conviction,
                reasoning=sig.reasoning,
                confidence=sig.confidence,
                timestamp=sig.timestamp,
                metadata=enriched_metadata,
            )
            weighted.append(enriched)
        return weighted

    def _weighted_consensus(self, signals: list[AgentSignal]) -> float:
        """
        Compute Darwinian-weight-adjusted consensus conviction.
        Neutral signals contribute 0 to the sum but their weight still
        dilutes the final average (they suppress strong directional bets).
        """
        total_weight = 0.0
        weighted_sum = 0.0
        for sig in signals:
            agent_weight = float(sig.metadata.get("agent_weight", 1.0))
            effective = agent_weight * sig.confidence
            weighted_sum += sig.conviction * effective
            total_weight += effective
        if total_weight == 0:
            return 0.0
        return max(-1.0, min(1.0, weighted_sum / total_weight))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_current_price(self, market_data: dict[str, Any]) -> float:
        """Extract the most recent closing price from market_data."""
        ohlcv = market_data.get("ohlcv", [])
        if ohlcv:
            return float(ohlcv[-1].get("close", 0))
        return float(market_data.get("current_price", 0))

    def _compute_proposed_size(self, conviction: float, current_price: float) -> float:
        """
        Quick preliminary size estimate (actual sizing happens in PortfolioManager).
        Used only to give the RiskAgent a ballpark figure.
        """
        from config.settings import settings
        max_risk_usd = self.portfolio_manager.equity * settings.risk.per_trade_risk_pct / 100
        conviction_scalar = abs(conviction)
        return max_risk_usd * conviction_scalar

    def _build_historical_stats(self, symbol: str) -> dict[str, float]:
        """
        Compute historical win rate and avg win/loss from closed trades for a symbol.
        Falls back to conservative defaults if insufficient history.
        """
        relevant = [
            t for t in self.portfolio_manager.closed_trades
            if t.get("symbol") == symbol
        ]
        if len(relevant) < 5:
            # Insufficient history — use conservative defaults
            return {"win_rate": 0.50, "avg_win_pct": 2.0, "avg_loss_pct": 1.5}

        wins = [t["pnl_pct"] for t in relevant if t.get("pnl_pct", 0) > 0]
        losses = [abs(t["pnl_pct"]) for t in relevant if t.get("pnl_pct", 0) <= 0]
        win_rate = len(wins) / len(relevant)
        avg_win = sum(wins) / len(wins) if wins else 2.0
        avg_loss = sum(losses) / len(losses) if losses else 1.5

        return {
            "win_rate": win_rate,
            "avg_win_pct": avg_win,
            "avg_loss_pct": avg_loss,
        }

    def _build_agent_scores(self, signals: list[AgentSignal]) -> list[dict[str, Any]]:
        """Compact agent score summary for the audit log."""
        return [
            {
                "agent_name": s.agent_name,
                "direction": s.direction.value,
                "conviction": s.conviction,
                "confidence": s.confidence,
                "reasoning": s.reasoning[:200],  # truncate for log
                "agent_weight": s.metadata.get("agent_weight", 1.0),
            }
            for s in signals
        ]

    def _mock_verdict(self, signal: AgentSignal) -> DebateVerdict:
        """Build a minimal DebateVerdict from a single signal (debate-skipped path)."""
        from agents.debate import DebateVerdict

        return DebateVerdict(
            direction=signal.direction,
            conviction=signal.conviction,
            confidence=signal.confidence,
            reasoning_chain=[signal.reasoning],
            dissenting_view="",
            bull_strength=max(0.0, signal.conviction),
            bear_strength=max(0.0, -signal.conviction),
            signal_count=1,
            participating_agents=[signal.agent_name],
        )

    async def _run_darwinian_review(self) -> None:
        """Background task for weekly Darwinian review."""
        try:
            result = await self.darwinian.run_weekly_review()
            logger.info("Orchestrator: Darwinian weekly review — %s", result)
        except Exception as exc:
            logger.error("Orchestrator: Darwinian review failed — %s", exc)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_decision_log(self) -> list[TradeDecision]:
        """Return the full decision history (most recent last)."""
        return list(self._decision_log)

    def get_agent_leaderboard(self) -> list[dict[str, Any]]:
        """Return Darwinian performance leaderboard."""
        return self.darwinian.get_leaderboard()
