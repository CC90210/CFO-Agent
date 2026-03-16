"""
agents/sentiment_analyst.py
----------------------------
Sentiment Analysis Agent — aggregates news headlines, social signals, and
the crypto Fear & Greed Index to produce a market-sentiment conviction score.

Data sources (all free):
  - NewsAPI       : https://newsapi.org/v2/everything
  - CryptoPanic   : https://cryptopanic.com/api/v1/posts/
  - Fear & Greed  : https://api.alternative.me/fng/

Recency weighting:
  Headlines from the last hour  → weight 1.0
  Headlines from the last day   → weight 0.5
  Headlines older than a day    → weight 0.2
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction

logger = logging.getLogger(__name__)

# Free API endpoints (no auth required for basic usage)
_CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"
_FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"
_NEWSAPI_URL = "https://newsapi.org/v2/everything"

# Default request timeout (seconds)
_HTTP_TIMEOUT = 10


class SentimentAnalyst(BaseAnalystAgent):
    """
    Specialist in market sentiment derived from news and social data.

    Expected market_data shape:
        {
            "asset_class": "crypto" | "stock",   # optional, default "crypto"
            "extra_headlines": [                  # optional caller-supplied headlines
                {"title": "...", "published_at": "ISO8601", "source": "..."},
            ]
        }

    Environment variables (optional — agents degrade gracefully if absent):
        NEWS_API_KEY      : NewsAPI key for stock/general news
        CRYPTOPANIC_KEY   : CryptoPanic API auth token
    """

    @property
    def name(self) -> str:
        return "SentimentAnalyst"

    # ------------------------------------------------------------------
    # Main implementation
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        asset_class = market_data.get("asset_class", "crypto").lower()
        extra_headlines = market_data.get("extra_headlines", [])

        headlines: list[dict[str, Any]] = list(extra_headlines)
        fear_greed_score: float | None = None

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_HTTP_TIMEOUT)
        ) as session:
            # Fetch from available sources concurrently
            import asyncio
            results = await asyncio.gather(
                self._fetch_cryptopanic(session, symbol),
                self._fetch_newsapi(session, symbol),
                self._fetch_fear_greed(session) if asset_class == "crypto" else self._noop(),
                return_exceptions=True,
            )

        cp_headlines, newsapi_headlines, fg_result = results

        if isinstance(cp_headlines, list):
            headlines.extend(cp_headlines)
        if isinstance(newsapi_headlines, list):
            headlines.extend(newsapi_headlines)
        if isinstance(fg_result, dict):
            fear_greed_score = fg_result.get("score")

        if not headlines and fear_greed_score is None:
            return AgentSignal.neutral(
                self.name,
                reason="No sentiment data available for this symbol",
            )

        # Score headlines by recency-weighted sentiment (simple heuristic)
        quant_sentiment = self._quant_sentiment_score(headlines)

        # Incorporate Fear & Greed Index for crypto
        if fear_greed_score is not None:
            # Fear & Greed: 0 = extreme fear (bearish), 100 = extreme greed (bullish)
            fg_conviction = (fear_greed_score - 50) / 50.0   # maps to [-1, 1]
            # Blend: 60% headline sentiment, 40% F&G
            quant_sentiment = 0.6 * quant_sentiment + 0.4 * fg_conviction

        # Build a compact news brief for Claude
        headline_text = self._format_headlines_for_claude(headlines[:15])

        try:
            signal = await self._claude_analysis(
                symbol, headline_text, quant_sentiment, fear_greed_score
            )
        except Exception as exc:
            logger.warning(
                "%s: Claude unavailable (%s), using quant sentiment", self.name, exc
            )
            signal = self._quant_signal(quant_sentiment, fear_greed_score)

        return signal

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    async def _fetch_cryptopanic(
        self, session: aiohttp.ClientSession, symbol: str
    ) -> list[dict[str, Any]]:
        """Fetch posts from CryptoPanic. Works without auth for public posts."""
        # Strip market suffix if present (e.g. "BTC/USDT" → "BTC")
        clean_symbol = symbol.split("/")[0].split("-")[0].upper()
        params: dict[str, str] = {
            "currencies": clean_symbol,
            "public": "true",
            "kind": "news",
        }
        cp_key = os.environ.get("CRYPTOPANIC_KEY", "")
        if cp_key:
            params["auth_token"] = cp_key

        try:
            async with session.get(_CRYPTOPANIC_URL, params=params) as resp:
                if resp.status != 200:
                    logger.debug("CryptoPanic returned %d", resp.status)
                    return []
                data = await resp.json()
                results = data.get("results", [])
                headlines = []
                for item in results:
                    headlines.append(
                        {
                            "title": item.get("title", ""),
                            "published_at": item.get("published_at", ""),
                            "source": item.get("source", {}).get("title", "CryptoPanic"),
                            "votes": item.get("votes", {}),
                        }
                    )
                return headlines
        except Exception as exc:
            logger.debug("CryptoPanic fetch failed: %s", exc)
            return []

    async def _fetch_newsapi(
        self, session: aiohttp.ClientSession, symbol: str
    ) -> list[dict[str, Any]]:
        """Fetch general news from NewsAPI (requires NEWS_API_KEY env var)."""
        api_key = os.environ.get("NEWS_API_KEY", "")
        if not api_key:
            return []

        clean_symbol = symbol.split("/")[0]
        params = {
            "q": clean_symbol,
            "sortBy": "publishedAt",
            "pageSize": "20",
            "apiKey": api_key,
            "language": "en",
        }

        try:
            async with session.get(_NEWSAPI_URL, params=params) as resp:
                if resp.status != 200:
                    logger.debug("NewsAPI returned %d", resp.status)
                    return []
                data = await resp.json()
                articles = data.get("articles", [])
                headlines = []
                for art in articles:
                    headlines.append(
                        {
                            "title": art.get("title", ""),
                            "published_at": art.get("publishedAt", ""),
                            "source": art.get("source", {}).get("name", "NewsAPI"),
                        }
                    )
                return headlines
        except Exception as exc:
            logger.debug("NewsAPI fetch failed: %s", exc)
            return []

    async def _fetch_fear_greed(
        self, session: aiohttp.ClientSession
    ) -> dict[str, float]:
        """Fetch the current Crypto Fear & Greed Index (0–100)."""
        try:
            async with session.get(_FEAR_GREED_URL) as resp:
                if resp.status != 200:
                    return {}
                data = await resp.json()
                value_str = data.get("data", [{}])[0].get("value", "50")
                return {"score": float(value_str)}
        except Exception as exc:
            logger.debug("Fear & Greed fetch failed: %s", exc)
            return {}

    async def _noop(self) -> dict[str, Any]:
        """Placeholder coroutine for non-crypto assets."""
        return {}

    # ------------------------------------------------------------------
    # Quant sentiment scoring
    # ------------------------------------------------------------------

    _BULLISH_WORDS = frozenset(
        [
            "surge", "rally", "breakout", "bullish", "soar", "jump", "gain",
            "high", "record", "adoption", "approve", "buy", "accumulate",
            "upgrade", "positive", "growth", "launch", "partnership",
        ]
    )
    _BEARISH_WORDS = frozenset(
        [
            "crash", "dump", "bearish", "plunge", "drop", "fall", "low",
            "hack", "ban", "regulate", "sell", "liquidat", "concern",
            "negative", "loss", "decline", "fraud", "scam", "lawsuit",
        ]
    )

    def _score_headline(self, title: str) -> float:
        """Simple lexical sentiment score: -1 to +1."""
        words = title.lower().split()
        score = 0
        for word in words:
            if any(bw in word for bw in self._BULLISH_WORDS):
                score += 1
            if any(bw in word for bw in self._BEARISH_WORDS):
                score -= 1
        return max(-1.0, min(1.0, score * 0.25))

    def _recency_weight(self, published_at: str) -> float:
        """Return a weight based on how recent the headline is."""
        if not published_at:
            return 0.2
        try:
            pub = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            now = datetime.now(tz=timezone.utc)
            age = now - pub
            if age < timedelta(hours=1):
                return 1.0
            if age < timedelta(days=1):
                return 0.5
            return 0.2
        except Exception:
            return 0.2

    def _quant_sentiment_score(self, headlines: list[dict[str, Any]]) -> float:
        """Recency-weighted average headline sentiment."""
        total_weight = 0.0
        weighted_sum = 0.0
        for h in headlines:
            title = h.get("title", "")
            published_at = h.get("published_at", "")
            score = self._score_headline(title)
            weight = self._recency_weight(published_at)
            weighted_sum += score * weight
            total_weight += weight
        if total_weight == 0:
            return 0.0
        return max(-1.0, min(1.0, weighted_sum / total_weight))

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    def _format_headlines_for_claude(self, headlines: list[dict[str, Any]]) -> str:
        lines = []
        for i, h in enumerate(headlines, 1):
            ts = h.get("published_at", "unknown time")
            source = h.get("source", "unknown")
            title = h.get("title", "")
            lines.append(f"{i}. [{source} | {ts}] {title}")
        return "\n".join(lines) if lines else "No headlines available."

    # ------------------------------------------------------------------
    # Claude analysis
    # ------------------------------------------------------------------

    async def _claude_analysis(
        self,
        symbol: str,
        headline_text: str,
        quant_sentiment: float,
        fear_greed: float | None,
    ) -> AgentSignal:
        system_prompt = (
            "You are an elite market sentiment analyst. "
            "Your job is to assess the market sentiment for a specific asset "
            "based on recent news headlines. Be precise and contrarian-aware. "
            "Respond ONLY with valid JSON."
        )

        fg_section = ""
        if fear_greed is not None:
            fg_label = (
                "Extreme Fear" if fear_greed < 25
                else "Fear" if fear_greed < 45
                else "Neutral" if fear_greed < 55
                else "Greed" if fear_greed < 75
                else "Extreme Greed"
            )
            fg_section = f"\nCrypto Fear & Greed Index: {fear_greed:.0f}/100 ({fg_label})"

        user_message = f"""Analyse market sentiment for {symbol} from these recent headlines.{fg_section}

Headlines:
{headline_text}

Quant lexical sentiment score: {quant_sentiment:+.3f} (range: -1.0 to +1.0)

Consider: fear/greed dynamics, institutional flow mentions, regulatory news,
macro events, and whether sentiment is already priced in (contrarian signal).

Respond with this exact JSON:
{{
  "direction": "LONG" | "SHORT" | "NEUTRAL",
  "conviction": <float -1.0 to 1.0>,
  "confidence": <float 0.0 to 1.0>,
  "sentiment_label": "extreme_fear" | "fear" | "neutral" | "greed" | "extreme_greed",
  "key_themes": ["<theme1>", "<theme2>"],
  "reasoning": "<2-3 sentence explanation>"
}}"""

        raw = await self.call_claude(system_prompt, user_message, max_tokens=512)
        parsed = self._parse_json_response(raw)

        if "raw" in parsed:
            return self._quant_signal(quant_sentiment, fear_greed)

        direction_str = str(parsed.get("direction", "NEUTRAL")).upper()
        try:
            direction = Direction(direction_str)
        except ValueError:
            direction = Direction.NEUTRAL

        conviction = float(parsed.get("conviction", quant_sentiment))
        confidence = float(parsed.get("confidence", 0.5))
        reasoning = str(parsed.get("reasoning", "No reasoning provided"))

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=reasoning,
            confidence=confidence,
            metadata={
                "mode": "claude",
                "sentiment_label": parsed.get("sentiment_label", "neutral"),
                "key_themes": parsed.get("key_themes", []),
                "fear_greed_score": fear_greed,
                "quant_sentiment": quant_sentiment,
            },
        )

    def _quant_signal(
        self, quant_sentiment: float, fear_greed: float | None
    ) -> AgentSignal:
        direction = self._direction_from_conviction(quant_sentiment)
        fg_note = f" Fear&Greed index: {fear_greed:.0f}." if fear_greed is not None else ""
        reasoning = (
            f"Quant sentiment score: {quant_sentiment:+.2f}.{fg_note} "
            "Claude analysis unavailable — using lexical headline scoring."
        )
        confidence = min(0.6, abs(quant_sentiment))
        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=quant_sentiment,
            reasoning=reasoning,
            confidence=confidence,
            metadata={"mode": "quant_fallback", "fear_greed_score": fear_greed},
        )
