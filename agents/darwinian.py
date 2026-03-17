"""
agents/darwinian.py
--------------------
Darwinian Evolution Engine — inspired by ATLAS self-improvement loops.

After each trade closes, every contributing agent's weight is updated:
  Correct prediction  → weight *= 1.05  (max cap 2.5)
  Wrong prediction    → weight *= 0.95  (min floor 0.3)

Weekly review:
  The worst-performing agent (by Sharpe or win rate) has its system prompt
  rewritten by Claude. If the rewrite improves performance over the next week,
  it is permanently adopted. Otherwise the previous prompt is restored
  (git-style version control on prompts).

Prompt versioning:
  Stored as {agent_name: [{version, prompt_text, sharpe, created_at}, ...]}
  Keyed by agent name in self._prompt_versions.

All agent performance history and prompt versions should be persisted to the
database by the orchestrator — this class keeps an in-memory record only.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction

logger = logging.getLogger(__name__)

# Darwinian update constants
_WIN_MULTIPLIER = 1.05
_LOSS_MULTIPLIER = 0.95
_MAX_WEIGHT = 2.5
_MIN_WEIGHT = 0.3

# Weekly review threshold — rewrite the worst agent's prompt if its
# rolling Sharpe falls below this value
_REWRITE_SHARPE_THRESHOLD = 0.2


@dataclass
class AgentPerformanceRecord:
    """Rolling performance record for a single agent."""

    agent_name: str
    trade_count: int = 0
    win_count: int = 0
    total_pnl_pct: float = 0.0
    squared_pnl_sum: float = 0.0    # for Sharpe calculation
    current_weight: float = 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    @property
    def win_rate(self) -> float:
        return self.win_count / self.trade_count if self.trade_count else 0.5

    @property
    def avg_pnl_pct(self) -> float:
        return self.total_pnl_pct / self.trade_count if self.trade_count else 0.0

    @property
    def sharpe_ratio(self) -> float:
        """Simplified rolling Sharpe (assumes 0 risk-free rate)."""
        if self.trade_count < 3:
            return 0.0
        variance = (
            self.squared_pnl_sum / self.trade_count
            - (self.total_pnl_pct / self.trade_count) ** 2
        )
        std = math.sqrt(max(variance, 1e-10))
        return self.avg_pnl_pct / std


@dataclass
class PromptVersion:
    """A versioned snapshot of an agent's system prompt."""

    version: int
    prompt_text: str
    sharpe_at_creation: float
    created_at: datetime
    performance_after: float | None = None   # Sharpe measured one week later
    active: bool = True


class DarwinianEvolutionEngine(BaseAnalystAgent):
    """
    Manages agent weight evolution and prompt self-improvement.

    Usage:
        engine = DarwinianEvolutionEngine(agents_dict)
        # After trade closes:
        engine.record_trade_outcome(symbol, exit_price, entry_price, signals)
        # Weekly:
        await engine.run_weekly_review()
    """

    def __init__(self, agents: dict[str, BaseAnalystAgent] | None = None) -> None:
        super().__init__()
        self.agents: dict[str, BaseAnalystAgent] = agents or {}
        self._performance: dict[str, AgentPerformanceRecord] = {}
        self._prompt_versions: dict[str, list[PromptVersion]] = {}
        self._last_weekly_review: datetime | None = None

    @property
    def name(self) -> str:
        return "DarwinianEvolutionEngine"

    def register_agent(self, agent: BaseAnalystAgent) -> None:
        """Register an agent for Darwinian tracking."""
        self.agents[agent.name] = agent
        if agent.name not in self._performance:
            self._performance[agent.name] = AgentPerformanceRecord(
                agent_name=agent.name,
                current_weight=agent.weight,
            )

    # ------------------------------------------------------------------
    # Post-trade weight update
    # ------------------------------------------------------------------

    def record_trade_outcome(
        self,
        symbol: str,
        exit_price: float,
        entry_price: float,
        contributing_signals: list[AgentSignal],
    ) -> None:
        """
        Update agent weights after a trade closes.

        Parameters
        ----------
        symbol:               The traded asset
        exit_price:           Trade exit price
        entry_price:          Trade entry price
        contributing_signals: All AgentSignals that contributed to the decision
        """
        trade_pnl_pct = (exit_price - entry_price) / entry_price * 100.0
        trade_was_profitable = trade_pnl_pct > 0

        for sig in contributing_signals:
            agent_name = sig.agent_name
            agent = self.agents.get(agent_name)

            if agent is None:
                continue

            # Was this agent's direction prediction correct?
            if sig.direction == Direction.NEUTRAL:
                # Neutral agents are not penalised or rewarded
                continue

            predicted_long = sig.direction == Direction.LONG
            agent_correct = (predicted_long and trade_was_profitable) or (
                not predicted_long and not trade_was_profitable
            )

            # Update weight
            if agent_correct:
                new_weight = min(_MAX_WEIGHT, agent.weight * _WIN_MULTIPLIER)
            else:
                new_weight = max(_MIN_WEIGHT, agent.weight * _LOSS_MULTIPLIER)

            old_weight = agent.weight
            agent.weight = new_weight

            # Update performance record
            record = self._performance.setdefault(
                agent_name,
                AgentPerformanceRecord(agent_name=agent_name, current_weight=old_weight),
            )
            record.trade_count += 1
            record.current_weight = new_weight
            record.last_updated = datetime.now(UTC)

            # Attribute P&L to agent (proportional to conviction used)
            attributed_pnl = trade_pnl_pct * abs(sig.conviction)
            if agent_correct:
                record.win_count += 1
                record.total_pnl_pct += attributed_pnl
            else:
                record.total_pnl_pct -= abs(attributed_pnl)
            record.squared_pnl_sum += attributed_pnl ** 2

            # Update the agent's own performance attributes
            agent.win_rate = record.win_rate
            agent.sharpe_ratio = record.sharpe_ratio

            logger.info(
                "%s: %s weight %s %.3f → %.3f (trade P&L: %+.2f%%)",
                self.name,
                agent_name,
                "up" if agent_correct else "down",
                old_weight,
                new_weight,
                trade_pnl_pct,
            )

            # Also resolve prediction on the agent's own history
            agent.resolve_prediction(symbol, exit_price, entry_price)

    # ------------------------------------------------------------------
    # Weekly review and prompt rewriting
    # ------------------------------------------------------------------

    async def run_weekly_review(self) -> dict[str, Any]:
        """
        Review all agent performance and rewrite the worst agent's prompt.
        Should be called once per week by the scheduler.

        Returns a summary dict for logging.
        """
        now = datetime.now(UTC)
        self._last_weekly_review = now

        # Agents with enough trade history
        eligible = [
            rec for rec in self._performance.values()
            if rec.trade_count >= 5
        ]

        if not eligible:
            return {"status": "insufficient_data", "agents_evaluated": 0}

        # Find worst-performing agent by Sharpe ratio
        worst_record = min(eligible, key=lambda r: r.sharpe_ratio)
        worst_agent = self.agents.get(worst_record.agent_name)

        if worst_agent is None:
            return {"status": "agent_not_found", "agent": worst_record.agent_name}

        if worst_record.sharpe_ratio > _REWRITE_SHARPE_THRESHOLD:
            return {
                "status": "all_agents_healthy",
                "worst_agent": worst_record.agent_name,
                "worst_sharpe": worst_record.sharpe_ratio,
                "threshold": _REWRITE_SHARPE_THRESHOLD,
            }

        logger.info(
            "%s: Weekly review — rewriting prompt for %s (Sharpe=%.2f)",
            self.name,
            worst_record.agent_name,
            worst_record.sharpe_ratio,
        )

        current_version = self._get_current_prompt_version(worst_record.agent_name)
        new_prompt = await self._rewrite_prompt(worst_agent, worst_record, current_version)

        if new_prompt is None:
            return {"status": "rewrite_failed", "agent": worst_record.agent_name}

        # Store the new version (probationary — will be evaluated after 1 week)
        self._store_prompt_version(
            agent_name=worst_record.agent_name,
            prompt_text=new_prompt,
            sharpe_at_creation=worst_record.sharpe_ratio,
        )

        return {
            "status": "prompt_rewritten",
            "agent": worst_record.agent_name,
            "old_sharpe": worst_record.sharpe_ratio,
            "new_prompt_version": len(self._prompt_versions.get(worst_record.agent_name, [])),
        }

    async def evaluate_rewrite_outcomes(self) -> dict[str, Any]:
        """
        Called 1 week after a prompt rewrite.
        Compares the new prompt's Sharpe to the old one.
        Reverts if performance regressed.
        """
        results = {}
        for agent_name, versions in self._prompt_versions.items():
            if len(versions) < 2:
                continue
            latest = versions[-1]
            previous = versions[-2]

            # New Sharpe for the agent after the rewrite
            record = self._performance.get(agent_name)
            if record is None:
                continue

            new_sharpe = record.sharpe_ratio
            latest.performance_after = new_sharpe

            if new_sharpe >= previous.sharpe_at_creation:
                # Rewrite improved performance — keep it
                results[agent_name] = {
                    "action": "kept",
                    "old_sharpe": previous.sharpe_at_creation,
                    "new_sharpe": new_sharpe,
                }
                logger.info(
                    "%s: Prompt rewrite for %s KEPT (%.2f → %.2f Sharpe)",
                    self.name, agent_name, previous.sharpe_at_creation, new_sharpe,
                )
            else:
                # Rewrite regressed — revert to previous version
                latest.active = False
                previous.active = True
                results[agent_name] = {
                    "action": "reverted",
                    "old_sharpe": previous.sharpe_at_creation,
                    "new_sharpe": new_sharpe,
                }
                logger.info(
                    "%s: Prompt rewrite for %s REVERTED (%.2f → %.2f Sharpe)",
                    self.name, agent_name, previous.sharpe_at_creation, new_sharpe,
                )

        return results

    # ------------------------------------------------------------------
    # Prompt rewriting via Claude
    # ------------------------------------------------------------------

    async def _rewrite_prompt(
        self,
        agent: BaseAnalystAgent,
        record: AgentPerformanceRecord,
        current_prompt: str | None,
    ) -> str | None:
        """
        Ask Claude to rewrite the underperforming agent's system prompt.
        Returns the new prompt text or None on failure.
        """
        system_prompt = (
            "You are a world-class prompt engineer specialising in financial AI agents. "
            "Your task is to improve a trading agent's system prompt to make its "
            "analysis more accurate and profitable. "
            "Focus on making the agent more: precise, contrarian-aware, and calibrated. "
            "Return ONLY the new system prompt text — no explanations, no JSON, just the prompt."
        )

        # Gather recent prediction errors for diagnosis
        recent = agent.get_recent_predictions(10)
        error_examples = [
            f"  Trade on {p['symbol']}: predicted {p['direction']}, "
            f"P&L={p.get('pnl_pct', 0):+.2f}%"
            for p in recent
            if p.get("resolved") and p.get("pnl_pct") is not None
        ]

        user_message = f"""Improve the following trading agent's system prompt.

Agent: {agent.name}
Current performance:
  Win rate: {record.win_rate:.1%}
  Sharpe ratio: {record.sharpe_ratio:.2f}
  Trade count: {record.trade_count}
  Avg P&L per attributed trade: {record.avg_pnl_pct:+.2f}%

Recent prediction examples:
{chr(10).join(error_examples) if error_examples else "  No resolved predictions yet."}

Current system prompt:
---
{current_prompt or f"You are {agent.name}. Analyse market data and produce trading signals."}
---

Write an improved system prompt that addresses the agent's weaknesses.
Focus on what is causing incorrect predictions and how to fix it.
The new prompt should be concise (under 300 words) and directly actionable."""

        try:
            new_prompt = await self.call_claude(system_prompt, user_message, max_tokens=600)
            # Strip any accidental JSON wrapping
            new_prompt = new_prompt.strip().strip("```").strip()
            return new_prompt
        except Exception as exc:
            logger.warning("%s: Prompt rewrite failed: %s", self.name, exc)
            return None

    # ------------------------------------------------------------------
    # Prompt version management
    # ------------------------------------------------------------------

    def _get_current_prompt_version(self, agent_name: str) -> str | None:
        """Return the text of the currently active prompt for an agent."""
        versions = self._prompt_versions.get(agent_name, [])
        active = [v for v in versions if v.active]
        if active:
            return active[-1].prompt_text
        return None

    def _store_prompt_version(
        self,
        agent_name: str,
        prompt_text: str,
        sharpe_at_creation: float,
    ) -> PromptVersion:
        """Store a new prompt version and deactivate the previous one."""
        if agent_name not in self._prompt_versions:
            self._prompt_versions[agent_name] = []

        # Deactivate all previous versions
        for v in self._prompt_versions[agent_name]:
            v.active = False

        version = PromptVersion(
            version=len(self._prompt_versions[agent_name]) + 1,
            prompt_text=prompt_text,
            sharpe_at_creation=sharpe_at_creation,
            created_at=datetime.now(UTC),
            active=True,
        )
        self._prompt_versions[agent_name].append(version)
        return version

    # ------------------------------------------------------------------
    # Performance reporting
    # ------------------------------------------------------------------

    def get_leaderboard(self) -> list[dict[str, Any]]:
        """Return agents sorted by Sharpe ratio descending."""
        return sorted(
            [
                {
                    "agent_name": r.agent_name,
                    "weight": r.current_weight,
                    "win_rate": r.win_rate,
                    "sharpe_ratio": r.sharpe_ratio,
                    "trade_count": r.trade_count,
                    "avg_pnl_pct": r.avg_pnl_pct,
                }
                for r in self._performance.values()
            ],
            key=lambda x: x["sharpe_ratio"],
            reverse=True,
        )

    def should_run_weekly_review(self) -> bool:
        """Return True if 7 days have passed since the last review."""
        if self._last_weekly_review is None:
            return True
        return datetime.now(UTC) - self._last_weekly_review >= timedelta(days=7)

    # ------------------------------------------------------------------
    # Required by ABC
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        """Not used — DarwinianEvolutionEngine is not an analyst."""
        leaderboard = self.get_leaderboard()
        top = leaderboard[0]["agent_name"] if leaderboard else "none"
        return AgentSignal.neutral(
            self.name,
            reason=f"Evolution engine. Top agent: {top}. Registered: {len(self.agents)}.",
        )
