"""
agents/debate.py
-----------------
Bull/Bear Debate Engine — synthesises all analyst signals into a structured
three-round debate moderated by Claude, producing a final verdict.

Round structure:
  Round 1 (Thesis)  : Bull case presents strongest evidence
  Round 2 (Rebuttal): Bear case counters + introduces its own thesis
  Round 3 (Final)   : Claude moderates and delivers verdict

If Claude is unavailable, a weighted-average consensus fallback is used.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction

logger = logging.getLogger(__name__)


@dataclass
class DebateVerdict:
    """
    Final output of the Bull/Bear Debate Engine.

    conviction:      weighted final conviction [-1.0, 1.0]
    confidence:      reliability of the verdict [0.0, 1.0]
    reasoning_chain: full multi-round argument chain for audit
    dissenting_view: strongest opposing argument (risk awareness)
    """

    direction: Direction
    conviction: float
    confidence: float
    reasoning_chain: list[str]
    dissenting_view: str
    bull_strength: float     # 0–1: strength of bull arguments
    bear_strength: float     # 0–1: strength of bear arguments
    signal_count: int
    participating_agents: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class DebateEngine(BaseAnalystAgent):
    """
    Moderates a structured bull/bear debate across all analyst signals.

    This agent does not analyse market data directly — it synthesises
    the outputs of all other agents. The orchestrator calls
    ``run_debate(signals)`` instead of ``analyze()``.
    """

    @property
    def name(self) -> str:
        return "DebateEngine"

    # ------------------------------------------------------------------
    # Primary entry point for the orchestrator
    # ------------------------------------------------------------------

    async def run_debate(
        self,
        symbol: str,
        signals: list[AgentSignal],
        context: dict[str, Any] | None = None,
    ) -> DebateVerdict:
        """
        Run a full three-round bull/bear debate on the provided signals.
        Falls back to weighted consensus if Claude is unavailable.
        """
        if not signals:
            return self._empty_verdict()

        bull_signals = [s for s in signals if s.direction == Direction.LONG]
        bear_signals = [s for s in signals if s.direction == Direction.SHORT]
        neutral_signals = [s for s in signals if s.direction == Direction.NEUTRAL]

        # Build argument cases
        bull_case = self._build_case(bull_signals, "BULL")
        bear_case = self._build_case(bear_signals, "BEAR")
        neutral_note = self._build_neutral_note(neutral_signals)

        # Consensus baseline (used as fallback)
        consensus_conviction = self._weighted_consensus(signals)

        try:
            verdict = await self._claude_debate(
                symbol=symbol,
                bull_case=bull_case,
                bear_case=bear_case,
                neutral_note=neutral_note,
                consensus_conviction=consensus_conviction,
                signals=signals,
                context=context or {},
            )
        except Exception as exc:
            logger.warning(
                "%s: Claude debate unavailable (%s), using consensus", self.name, exc
            )
            verdict = self._consensus_verdict(signals, consensus_conviction)

        return verdict

    # ------------------------------------------------------------------
    # Required by ABC (not used directly — orchestrator calls run_debate)
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        """
        Thin wrapper: if called via analyze(), treat market_data["signals"]
        as the input and run the debate.
        """
        signals = market_data.get("signals", [])
        verdict = await self.run_debate(symbol, signals, context)
        return AgentSignal(
            agent_name=self.name,
            direction=verdict.direction,
            conviction=verdict.conviction,
            reasoning=" | ".join(verdict.reasoning_chain[-1:]),
            confidence=verdict.confidence,
            metadata={"debate_verdict": verdict.__dict__},
        )

    # ------------------------------------------------------------------
    # Case building
    # ------------------------------------------------------------------

    def _build_case(self, signals: list[AgentSignal], side: str) -> str:
        """Compile the bull or bear case from matching signals."""
        if not signals:
            return f"No {side} arguments presented."
        lines = [f"{side} CASE — {len(signals)} analyst(s):"]
        for s in sorted(signals, key=lambda x: abs(x.conviction), reverse=True):
            lines.append(
                f"  [{s.agent_name}] conviction={s.conviction:+.2f} "
                f"conf={s.confidence:.2f}: {s.reasoning}"
            )
        return "\n".join(lines)

    def _build_neutral_note(self, signals: list[AgentSignal]) -> str:
        if not signals:
            return ""
        names = ", ".join(s.agent_name for s in signals)
        return f"NEUTRAL signals from: {names}. These agents see no clear directional edge."

    # ------------------------------------------------------------------
    # Weighted consensus (no Claude)
    # ------------------------------------------------------------------

    def _weighted_consensus(self, signals: list[AgentSignal]) -> float:
        """
        Compute the conviction-weighted average signal across all agents.
        Uses agent.weight (Darwinian) if available via signal.metadata.
        """
        total_weight = 0.0
        weighted_sum = 0.0
        for sig in signals:
            # Agent weight may be stored in metadata by the orchestrator
            agent_weight = float(sig.metadata.get("agent_weight", 1.0))
            effective_weight = agent_weight * sig.confidence
            weighted_sum += sig.conviction * effective_weight
            total_weight += effective_weight

        if total_weight == 0:
            return 0.0
        return max(-1.0, min(1.0, weighted_sum / total_weight))

    def _consensus_verdict(
        self, signals: list[AgentSignal], conviction: float
    ) -> DebateVerdict:
        """Build a verdict using pure weighted consensus (Claude fallback)."""
        direction = self._direction_from_conviction(conviction)

        bull_signals = [s for s in signals if s.direction == Direction.LONG]
        bear_signals = [s for s in signals if s.direction == Direction.SHORT]
        bull_strength = sum(abs(s.conviction) * s.confidence for s in bull_signals)
        bear_strength = sum(abs(s.conviction) * s.confidence for s in bear_signals)
        total = bull_strength + bear_strength or 1.0

        return DebateVerdict(
            direction=direction,
            conviction=conviction,
            confidence=min(0.75, abs(conviction)),
            reasoning_chain=[
                f"Weighted consensus across {len(signals)} agents: conviction={conviction:+.2f}",
                f"Bull strength: {bull_strength / total:.1%}, Bear strength: {bear_strength / total:.1%}",
                "Claude moderator unavailable — using statistical consensus",
            ],
            dissenting_view=(
                self._build_case(bear_signals if direction == Direction.LONG else bull_signals, "OPPOSING")
            ),
            bull_strength=bull_strength / total,
            bear_strength=bear_strength / total,
            signal_count=len(signals),
            participating_agents=[s.agent_name for s in signals],
            metadata={"mode": "consensus_fallback"},
        )

    # ------------------------------------------------------------------
    # Three-round Claude debate
    # ------------------------------------------------------------------

    async def _claude_debate(
        self,
        symbol: str,
        bull_case: str,
        bear_case: str,
        neutral_note: str,
        consensus_conviction: float,
        signals: list[AgentSignal],
        context: dict[str, Any],
    ) -> DebateVerdict:
        system_prompt = (
            "You are an impartial debate moderator for a sophisticated trading firm. "
            "You will moderate a three-round bull/bear debate about a trading opportunity. "
            "Your job is to weigh evidence quality, recency, and reliability — not to "
            "be contrarian or artificially balance. Follow the data. "
            "Respond ONLY with valid JSON."
        )

        macro_note = ""
        if context.get("macro_environment"):
            macro_note = f"\nMarket regime / macro context: {context['macro_environment']}"

        # Round 1 — present cases
        round1_message = f"""ROUND 1 — OPENING ARGUMENTS for {symbol}.{macro_note}

Statistical consensus conviction: {consensus_conviction:+.3f}

{bull_case}

{bear_case}

{neutral_note}

Respond with a JSON object for Round 1 only:
{{
  "round": 1,
  "bull_initial_strength": <float 0.0-1.0>,
  "bear_initial_strength": <float 0.0-1.0>,
  "key_bull_evidence": ["<point1>", "<point2>"],
  "key_bear_evidence": ["<point1>", "<point2>"],
  "preliminary_lean": "BULL" | "BEAR" | "NEUTRAL"
}}"""

        raw1 = await self.call_claude(system_prompt, round1_message, max_tokens=600)
        r1 = self._parse_json_response(raw1)

        if "raw" in r1:
            return self._consensus_verdict(signals, consensus_conviction)

        # Round 2 — rebuttals
        bull_strength_r1 = float(r1.get("bull_initial_strength", 0.5))
        bear_strength_r1 = float(r1.get("bear_initial_strength", 0.5))
        preliminary_lean = r1.get("preliminary_lean", "NEUTRAL")

        round2_message = f"""ROUND 2 — REBUTTALS for {symbol}.

Round 1 assessment:
  Bull strength: {bull_strength_r1:.2f}
  Bear strength: {bear_strength_r1:.2f}
  Preliminary lean: {preliminary_lean}

Bull key evidence: {r1.get('key_bull_evidence', [])}
Bear key evidence: {r1.get('key_bear_evidence', [])}

Now consider the counterarguments:
- If leaning BULL: what are the 2 strongest bear rebuttals?
- If leaning BEAR: what are the 2 strongest bull rebuttals?
- Are there any confirmation biases in Round 1?

Respond with JSON for Round 2:
{{
  "round": 2,
  "rebuttal_impact": <float 0.0-1.0>,
  "rebuttal_direction": "STRENGTHENS_BULL" | "STRENGTHENS_BEAR" | "NEUTRAL",
  "strongest_rebuttal": "<one paragraph>",
  "lean_after_rebuttal": "BULL" | "BEAR" | "NEUTRAL"
}}"""

        raw2 = await self.call_claude(system_prompt, round2_message, max_tokens=500)
        r2 = self._parse_json_response(raw2)

        if "raw" in r2:
            return self._consensus_verdict(signals, consensus_conviction)

        rebuttal_direction = r2.get("rebuttal_direction", "NEUTRAL")
        lean_after_rebuttal = r2.get("lean_after_rebuttal", preliminary_lean)

        # Round 3 — final verdict
        round3_message = f"""ROUND 3 — FINAL VERDICT for {symbol}.

After three rounds:
  Initial lean: {preliminary_lean}
  After rebuttal: {lean_after_rebuttal}
  Rebuttal impact: {r2.get('rebuttal_impact', 0.5):.2f}
  Rebuttal strengthened: {rebuttal_direction}

Statistical consensus: {consensus_conviction:+.3f}
Strongest rebuttal: {r2.get('strongest_rebuttal', 'N/A')}

Deliver your FINAL VERDICT considering:
1. Which side had stronger, more reliable evidence?
2. What is the current market regime (risk-on / risk-off)?
3. What does the statistical consensus say?
4. Are any signals conflicted or likely stale?

Respond with JSON for the final verdict:
{{
  "round": 3,
  "direction": "LONG" | "SHORT" | "NEUTRAL",
  "conviction": <float -1.0 to 1.0>,
  "confidence": <float 0.0 to 1.0>,
  "bull_final_strength": <float 0.0-1.0>,
  "bear_final_strength": <float 0.0-1.0>,
  "final_reasoning": "<3-5 sentence verdict>",
  "dissenting_view": "<1-2 sentence strongest opposing argument>"
}}"""

        raw3 = await self.call_claude(system_prompt, round3_message, max_tokens=600)
        r3 = self._parse_json_response(raw3)

        if "raw" in r3:
            return self._consensus_verdict(signals, consensus_conviction)

        direction_str = str(r3.get("direction", "NEUTRAL")).upper()
        try:
            direction = Direction(direction_str)
        except ValueError:
            direction = Direction.NEUTRAL

        conviction = float(r3.get("conviction", consensus_conviction))
        confidence = float(r3.get("confidence", 0.7))
        bull_final = float(r3.get("bull_final_strength", bull_strength_r1))
        bear_final = float(r3.get("bear_final_strength", bear_strength_r1))

        reasoning_chain = [
            f"Round 1 — Preliminary lean: {preliminary_lean} "
            f"(bull={bull_strength_r1:.2f}, bear={bear_strength_r1:.2f})",
            f"Round 2 — Rebuttal: {rebuttal_direction} → lean shifted to {lean_after_rebuttal}",
            f"Round 3 — Final verdict: {direction.value} conviction={conviction:+.2f} "
            f"confidence={confidence:.2f}",
            str(r3.get("final_reasoning", "")),
        ]

        return DebateVerdict(
            direction=direction,
            conviction=conviction,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            dissenting_view=str(r3.get("dissenting_view", "")),
            bull_strength=bull_final,
            bear_strength=bear_final,
            signal_count=len(signals),
            participating_agents=[s.agent_name for s in signals],
            metadata={
                "mode": "claude_3_round",
                "preliminary_lean": preliminary_lean,
                "lean_after_rebuttal": lean_after_rebuttal,
                "consensus_conviction": consensus_conviction,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _empty_verdict(self) -> DebateVerdict:
        return DebateVerdict(
            direction=Direction.NEUTRAL,
            conviction=0.0,
            confidence=0.0,
            reasoning_chain=["No analyst signals provided to debate engine"],
            dissenting_view="",
            bull_strength=0.0,
            bear_strength=0.0,
            signal_count=0,
            participating_agents=[],
        )
