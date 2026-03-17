"""
agents/base_agent.py
--------------------
Abstract base class for all analyst agents in the Atlas trading framework.

Responsibilities:
- AgentSignal dataclass (the standard output contract for every agent)
- BaseAnalystAgent ABC with Claude API retry logic, caching, and
  performance tracking
- Non-fatal Claude failure: agents fall back to NEUTRAL / 0.0 conviction
  rather than propagating exceptions to the orchestrator
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import anthropic

from config.settings import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & data structures
# ---------------------------------------------------------------------------


class Direction(str, Enum):
    """Trading signal direction."""

    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


@dataclass
class AgentSignal:
    """
    Standardised output from any analyst agent.

    conviction:  -1.0 (max bearish) → 0.0 (neutral) → +1.0 (max bullish)
    confidence:   0.0 (no confidence in the signal) → 1.0 (maximum confidence)
    """

    agent_name: str
    direction: Direction
    conviction: float          # [-1.0, 1.0]
    reasoning: str
    confidence: float          # [0.0, 1.0]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.conviction = max(-1.0, min(1.0, self.conviction))
        self.confidence = max(0.0, min(1.0, self.confidence))

    @classmethod
    def neutral(cls, agent_name: str, reason: str = "No signal") -> "AgentSignal":
        """Convenience constructor for a neutral / fallback signal."""
        return cls(
            agent_name=agent_name,
            direction=Direction.NEUTRAL,
            conviction=0.0,
            reasoning=reason,
            confidence=0.0,
        )

    @property
    def weighted_conviction(self) -> float:
        """Conviction scaled by confidence — used for consensus weighting."""
        return self.conviction * self.confidence


# ---------------------------------------------------------------------------
# Base analyst
# ---------------------------------------------------------------------------


class BaseAnalystAgent(ABC):
    """
    Abstract base for all Atlas analyst agents.

    Sub-classes must implement ``_analyze_impl`` which receives pre-validated
    inputs and returns a raw ``AgentSignal``. This base class wraps that call
    with:
    - An in-memory 5-minute result cache keyed on symbol + data hash
    - Claude API call helper with 3 retries and exponential back-off
    - Darwinian performance tracking (win_rate, sharpe_ratio, weight)
    - Non-fatal error handling: any unhandled exception returns NEUTRAL
    """

    # How long (seconds) a cached result is considered fresh
    _CACHE_TTL: int = 300  # 5 minutes

    # Retry configuration for Claude API calls
    _MAX_RETRIES: int = 3
    _BACKOFF_BASE: float = 1.5  # seconds — multiplied exponentially

    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, AgentSignal]] = {}
        self._client: anthropic.AsyncAnthropic | None = None

        # Darwinian tracking — updated by DarwinianEvolutionEngine
        self.weight: float = 1.0       # [0.3, 2.5]
        self.win_rate: float = 0.5
        self.sharpe_ratio: float = 0.0
        self._prediction_history: list[dict[str, Any]] = []

        logger.debug("Initialised agent: %s", self.name)

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent identifier."""

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def analyze(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> AgentSignal:
        """
        Analyse ``symbol`` using ``market_data`` and optional extra ``context``.

        Returns a cached signal if the same data was analysed within the last
        5 minutes.  Falls back to a NEUTRAL signal on any unhandled error so
        that a single agent failure never crashes the orchestrator.
        """
        cache_key = self._make_cache_key(symbol, market_data)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            logger.debug("%s: cache hit for %s", self.name, symbol)
            return cached

        try:
            signal = await self._analyze_impl(symbol, market_data, context or {})
        except Exception as exc:
            logger.warning(
                "%s: analysis failed for %s — returning NEUTRAL. Error: %s",
                self.name,
                symbol,
                exc,
                exc_info=True,
            )
            signal = AgentSignal.neutral(self.name, reason=f"Agent error: {exc}")

        self._store_in_cache(cache_key, signal)
        return signal

    # ------------------------------------------------------------------
    # Abstract implementation hook
    # ------------------------------------------------------------------

    @abstractmethod
    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        """Subclasses implement analysis logic here."""

    # ------------------------------------------------------------------
    # Claude API helper
    # ------------------------------------------------------------------

    def _get_client(self) -> anthropic.AsyncAnthropic:
        """Lazy-initialise the Anthropic async client."""
        if self._client is None:
            api_key = settings.ai.anthropic_api_key
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set. "
                    "Add it to your .env file to enable Claude-powered analysis."
                )
            self._client = anthropic.AsyncAnthropic(api_key=api_key)
        return self._client

    async def call_claude(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int | None = None,
    ) -> str:
        """
        Call Claude with retry logic (3 attempts, exponential back-off).

        Raises the final exception if all retries are exhausted — callers
        should catch and return a neutral fallback.
        """
        if max_tokens is None:
            max_tokens = settings.ai.max_tokens

        last_exc: Exception | None = None

        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                client = self._get_client()
                response = await client.messages.create(
                    model=settings.ai.claude_model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                # Extract text from the first content block
                content = response.content[0]
                if hasattr(content, "text"):
                    return content.text
                return str(content)

            except anthropic.RateLimitError as exc:
                last_exc = exc
                wait = self._BACKOFF_BASE ** attempt
                logger.warning(
                    "%s: Claude rate-limited (attempt %d/%d). Waiting %.1fs.",
                    self.name,
                    attempt,
                    self._MAX_RETRIES,
                    wait,
                )
                await asyncio.sleep(wait)

            except anthropic.APIStatusError as exc:
                last_exc = exc
                wait = self._BACKOFF_BASE ** attempt
                logger.warning(
                    "%s: Claude API error %d (attempt %d/%d). Waiting %.1fs.",
                    self.name,
                    exc.status_code,
                    attempt,
                    self._MAX_RETRIES,
                    wait,
                )
                if exc.status_code < 500:
                    # Client-side error — no point retrying
                    raise
                await asyncio.sleep(wait)

            except Exception as exc:
                last_exc = exc
                logger.error("%s: Unexpected Claude error: %s", self.name, exc)
                raise

        raise RuntimeError(
            f"{self.name}: Claude API unavailable after {self._MAX_RETRIES} retries"
        ) from last_exc

    def _parse_json_response(self, raw: str) -> dict[str, Any]:
        """
        Best-effort JSON extraction from a Claude response.

        Claude often wraps JSON in markdown fences — this strips those before
        parsing.
        """
        # Strip markdown code fences if present
        text = raw.strip()
        for fence in ("```json", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
                break
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            # Return the raw text under a dedicated key so callers can still
            # extract a direction from natural-language output if needed.
            return {"raw": raw}

    # ------------------------------------------------------------------
    # Caching
    # ------------------------------------------------------------------

    def _make_cache_key(self, symbol: str, market_data: dict[str, Any]) -> str:
        """Deterministic cache key: agent name + symbol + data fingerprint."""
        payload = json.dumps(market_data, sort_keys=True, default=str)
        digest = hashlib.md5(payload.encode()).hexdigest()[:12]
        return f"{self.name}:{symbol}:{digest}"

    def _get_from_cache(self, key: str) -> AgentSignal | None:
        if key not in self._cache:
            return None
        stored_at, signal = self._cache[key]
        if time.monotonic() - stored_at > self._CACHE_TTL:
            del self._cache[key]
            return None
        return signal

    def _store_in_cache(self, key: str, signal: AgentSignal) -> None:
        self._cache[key] = (time.monotonic(), signal)

    def invalidate_cache(self) -> None:
        """Flush the entire cache for this agent (e.g. after Darwinian rewrite)."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Darwinian performance tracking
    # ------------------------------------------------------------------

    def record_prediction(
        self,
        symbol: str,
        signal: AgentSignal,
        entry_price: float,
    ) -> None:
        """
        Called by DarwinianEvolutionEngine when a trade is opened.
        Stores the prediction for later evaluation.
        """
        self._prediction_history.append(
            {
                "symbol": symbol,
                "direction": signal.direction,
                "conviction": signal.conviction,
                "entry_price": entry_price,
                "timestamp": signal.timestamp.isoformat(),
                "resolved": False,
                "pnl_pct": None,
            }
        )

    def resolve_prediction(self, symbol: str, exit_price: float, entry_price: float) -> None:
        """
        Called by DarwinianEvolutionEngine when a trade closes.
        Marks the prediction as resolved with the realised P&L.
        """
        pnl_pct = (exit_price - entry_price) / entry_price * 100.0
        for pred in reversed(self._prediction_history):
            if pred["symbol"] == symbol and not pred["resolved"]:
                pred["resolved"] = True
                pred["pnl_pct"] = pnl_pct
                break

    def get_recent_predictions(self, n: int = 20) -> list[dict[str, Any]]:
        """Return the most recent n resolved predictions."""
        resolved = [p for p in self._prediction_history if p["resolved"]]
        return resolved[-n:]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _direction_from_conviction(self, conviction: float) -> Direction:
        """Map a conviction float to a Direction enum."""
        if conviction > 0.05:
            return Direction.LONG
        if conviction < -0.05:
            return Direction.SHORT
        return Direction.NEUTRAL

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"weight={self.weight:.2f} win_rate={self.win_rate:.2f}>"
        )
