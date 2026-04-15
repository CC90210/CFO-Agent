"""
agents/news_analyst.py
-----------------------
Breaking News Agent — classifies real-time news events by impact level and
urgency. Designed for rapid signal generation when market-moving events occur
before they are fully priced in.

Impact classification:
  HIGH   : regulation, exchange hacks, Fed decisions, major partnership
  MEDIUM : protocol upgrades, product launches, secondary partnerships
  LOW    : opinion pieces, price predictions, minor updates

HIGH-impact news triggers an immediate risk review signal with elevated
conviction. MEDIUM and LOW are weighted proportionally.

In live mode, this agent can be polled every 60 seconds by the orchestrator.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction

logger = logging.getLogger(__name__)

_CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"
_HTTP_TIMEOUT = 10

# Impact weights for conviction scaling
_IMPACT_WEIGHT = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 0.15}

# Seconds to cache news results before re-fetching
_NEWS_CACHE_TTL = 60  # 1 minute


class NewsAnalyst(BaseAnalystAgent):
    """
    Specialist in breaking news impact analysis.

    Expected market_data shape:
        {
            "asset_class": "crypto" | "stock",
            "injected_news": [          # optional: pre-fetched headlines
                {
                    "title": str,
                    "url": str,
                    "published_at": ISO8601,
                    "source": str,
                }
            ]
        }

    The agent also maintains an internal news cache so repeated calls within
    _NEWS_CACHE_TTL seconds do not hit external APIs.
    """

    def __init__(self) -> None:
        super().__init__()
        self._news_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}

    @property
    def name(self) -> str:
        return "NewsAnalyst"

    # Override the base cache TTL for news (shorter = fresher)
    _CACHE_TTL: int = _NEWS_CACHE_TTL

    # ------------------------------------------------------------------
    # Main implementation
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        injected = market_data.get("injected_news", [])
        articles = list(injected)

        if not articles:
            articles = await self._fetch_news(symbol)

        if not articles:
            return AgentSignal.neutral(
                self.name,
                reason="No recent news articles found",
            )

        # Classify articles without Claude first (deterministic fast path)
        classified = [self._classify_article(a) for a in articles]

        # Find the highest-impact articles
        high_impact = [c for c in classified if c["impact"] == "HIGH"]
        medium_impact = [c for c in classified if c["impact"] == "MEDIUM"]

        # If HIGH impact news exists, escalate immediately
        if high_impact:
            most_urgent = high_impact[0]
            try:
                signal = await self._claude_classify(symbol, most_urgent, classified[:10])
            except Exception as exc:
                logger.warning("%s: Claude unavailable (%s)", self.name, exc)
                signal = self._heuristic_signal(symbol, classified)
            return signal

        # No HIGH impact — run a broader sentiment pass through Claude
        try:
            signal = await self._claude_classify(symbol, None, classified[:10])
        except Exception as exc:
            logger.warning("%s: Claude unavailable (%s)", self.name, exc)
            signal = self._heuristic_signal(symbol, classified)

        return signal

    # ------------------------------------------------------------------
    # News fetching
    # ------------------------------------------------------------------

    async def _fetch_news(self, symbol: str) -> list[dict[str, Any]]:
        """Fetch from CryptoPanic (and potentially other sources)."""
        cache_key = symbol.upper()
        cached = self._news_cache.get(cache_key)
        if cached is not None:
            stored_at, articles = cached
            if time.monotonic() - stored_at < _NEWS_CACHE_TTL:
                return articles

        clean_symbol = symbol.split("/")[0].split("-")[0].upper()
        params: dict[str, str] = {
            "currencies": clean_symbol,
            "public": "true",
        }
        cp_key = os.environ.get("CRYPTOPANIC_KEY", "")
        if cp_key:
            params["auth_token"] = cp_key

        articles: list[dict[str, Any]] = []
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=_HTTP_TIMEOUT)
            ) as session:
                async with session.get(_CRYPTOPANIC_URL, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("results", []):
                            articles.append(
                                {
                                    "title": item.get("title", ""),
                                    "url": item.get("url", ""),
                                    "published_at": item.get("published_at", ""),
                                    "source": item.get("source", {}).get("title", ""),
                                    "votes": item.get("votes", {}),
                                }
                            )
        except Exception as exc:
            logger.debug("News fetch failed: %s", exc)

        self._news_cache[cache_key] = (time.monotonic(), articles)
        return articles

    # ------------------------------------------------------------------
    # Article classification (heuristic)
    # ------------------------------------------------------------------

    _HIGH_IMPACT_KEYWORDS = frozenset(
        [
            "hack", "exploit", "breach", "stolen", "sec", "regulation",
            "ban", "federal reserve", "fed rate", "etf approved", "etf rejected",
            "bankruptcy", "insolvency", "emergency", "ceo resign",
            "exchange down", "halted", "critical vulnerability",
        ]
    )
    _MEDIUM_IMPACT_KEYWORDS = frozenset(
        [
            "partnership", "launch", "upgrade", "integration", "listed",
            "acquisition", "raise", "funding", "mainnet", "major update",
            "etf filing", "institutional", "whale", "accumulate",
        ]
    )
    _BULLISH_KEYWORDS = frozenset(
        ["approved", "partnership", "launch", "upgrade", "institutional",
         "accumulate", "bullish", "rally", "surge", "adoption"]
    )
    _BEARISH_KEYWORDS = frozenset(
        ["hack", "ban", "rejected", "bankruptcy", "crash", "bearish",
         "exploit", "stolen", "insolvency", "emergency"]
    )

    def _classify_article(self, article: dict[str, Any]) -> dict[str, Any]:
        """Classify an article by impact level and preliminary direction."""
        title_lower = (article.get("title") or "").lower()
        url_lower = (article.get("url") or "").lower()
        text = f"{title_lower} {url_lower}"

        # Impact level
        if any(k in text for k in self._HIGH_IMPACT_KEYWORDS):
            impact = "HIGH"
        elif any(k in text for k in self._MEDIUM_IMPACT_KEYWORDS):
            impact = "MEDIUM"
        else:
            impact = "LOW"

        # Preliminary direction
        bullish_score = sum(1 for k in self._BULLISH_KEYWORDS if k in text)
        bearish_score = sum(1 for k in self._BEARISH_KEYWORDS if k in text)

        if bearish_score > bullish_score:
            preliminary_direction = "BEARISH"
        elif bullish_score > bearish_score:
            preliminary_direction = "BULLISH"
        else:
            preliminary_direction = "NEUTRAL"

        return {
            **article,
            "impact": impact,
            "preliminary_direction": preliminary_direction,
        }

    def _age_hours(self, published_at: str) -> float:
        """Return article age in hours (0 = just published)."""
        if not published_at:
            return 24.0
        try:
            pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            now = datetime.now(tz=timezone.utc)
            return (now - pub).total_seconds() / 3600
        except Exception:
            return 24.0

    # ------------------------------------------------------------------
    # Heuristic signal (no Claude)
    # ------------------------------------------------------------------

    def _heuristic_signal(
        self,
        symbol: str,
        classified: list[dict[str, Any]],
    ) -> AgentSignal:
        """
        Aggregate classified articles into a conviction score without Claude.
        More recent + higher impact articles carry more weight.
        """
        total_weight = 0.0
        weighted_sum = 0.0

        for c in classified:
            impact_w = _IMPACT_WEIGHT.get(c["impact"], 0.1)
            age_h = self._age_hours(c.get("published_at", ""))
            # Recency decay: fresh news has full weight, 24h-old has ~10%
            recency_w = max(0.05, 1.0 - age_h / 25.0)
            weight = impact_w * recency_w

            dirn = c.get("preliminary_direction", "NEUTRAL")
            if dirn == "BULLISH":
                score = 1.0
            elif dirn == "BEARISH":
                score = -1.0
            else:
                score = 0.0

            weighted_sum += score * weight
            total_weight += weight

        conviction = max(-1.0, min(1.0, weighted_sum / total_weight)) if total_weight else 0.0
        direction = self._direction_from_conviction(conviction)

        high_count = sum(1 for c in classified if c["impact"] == "HIGH")
        reasoning = (
            f"News heuristic score: {conviction:+.2f}. "
            f"{high_count} high-impact article(s) detected. "
            "Claude unavailable — using keyword classification."
        )

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=reasoning,
            confidence=min(0.65, abs(conviction)),
            metadata={
                "mode": "heuristic",
                "high_impact_count": high_count,
                "article_count": len(classified),
            },
        )

    # ------------------------------------------------------------------
    # Claude classification
    # ------------------------------------------------------------------

    async def _claude_classify(
        self,
        symbol: str,
        urgent_article: dict[str, Any] | None,
        all_classified: list[dict[str, Any]],
    ) -> AgentSignal:
        system_prompt = (
            "You are an expert in breaking news impact on financial markets. "
            "Your task is to classify news articles and determine their effect "
            "on the specified asset's short-term price. "
            "Be decisive. Respond ONLY with valid JSON."
        )

        urgent_section = ""
        if urgent_article:
            urgent_section = (
                f"\nURGENT HIGH-IMPACT ARTICLE:\n"
                f"  Title: {urgent_article.get('title', '')}\n"
                f"  Published: {urgent_article.get('published_at', '')}\n"
            )

        articles_text = "\n".join(
            f"[{c.get('impact', 'LOW')}] {c.get('title', '')} "
            f"({c.get('preliminary_direction', 'NEUTRAL')})"
            for c in all_classified[:10]
        )

        user_message = f"""Classify recent news for {symbol}.{urgent_section}

Recent articles (pre-classified by keyword):
{articles_text}

For each HIGH-impact article, determine:
- Expected price direction (LONG/SHORT)
- Duration of impact (hours to days)
- Whether this is already priced in

Respond with this exact JSON:
{{
  "direction": "LONG" | "SHORT" | "NEUTRAL",
  "conviction": <float -1.0 to 1.0>,
  "confidence": <float 0.0 to 1.0>,
  "impact_level": "HIGH" | "MEDIUM" | "LOW",
  "duration_hours": <integer 1-168>,
  "is_priced_in": <bool>,
  "urgency": "IMMEDIATE" | "WATCH" | "MONITOR",
  "reasoning": "<2-3 sentence explanation>"
}}"""

        raw = await self.call_claude(system_prompt, user_message, max_tokens=512)
        parsed = self._parse_json_response(raw)

        if "raw" in parsed:
            return self._heuristic_signal(symbol, all_classified)

        direction_str = str(parsed.get("direction", "NEUTRAL")).upper()
        try:
            direction = Direction(direction_str)
        except ValueError:
            direction = Direction.NEUTRAL

        conviction = float(parsed.get("conviction", 0.0))
        is_priced_in = bool(parsed.get("is_priced_in", False))
        if is_priced_in:
            # Dampen conviction if news is already priced in
            conviction *= 0.3

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=str(parsed.get("reasoning", "")),
            confidence=float(parsed.get("confidence", 0.6)),
            metadata={
                "mode": "claude",
                "impact_level": parsed.get("impact_level", "LOW"),
                "duration_hours": parsed.get("duration_hours", 24),
                "is_priced_in": is_priced_in,
                "urgency": parsed.get("urgency", "MONITOR"),
            },
        )
