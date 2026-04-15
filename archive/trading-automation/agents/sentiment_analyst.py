"""
agents/sentiment_analyst.py
----------------------------
Sentiment Analysis Agent — aggregates news headlines, social signals, and
the crypto Fear & Greed Index to produce a market-sentiment conviction score.

Data sources (all free):
  - NewsAPI       : https://newsapi.org/v2/everything
  - CryptoPanic   : https://cryptopanic.com/api/v1/posts/
  - Fear & Greed  : https://api.alternative.me/fng/
  - Yahoo Finance : per-symbol news via yfinance library
  - CoinGecko     : trending coins list (no key required)
  - EconomicCalendar: high-impact event detection (local)

Recency weighting:
  Headlines from the last hour  → weight 1.0
  Headlines from the last day   → weight 0.5
  Headlines older than a day    → weight 0.2

Economic calendar integration:
  If a HIGH-impact event is within 24 hours, caution_multiplier is applied
  to dampen conviction (the agent becomes more conservative).
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
from data.economic_calendar import EconomicCalendar

logger = logging.getLogger(__name__)

# Free API endpoints (no auth required for basic usage)
_CRYPTOPANIC_URL = "https://cryptopanic.com/api/v1/posts/"
_FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=1"
_NEWSAPI_URL = "https://newsapi.org/v2/everything"
_COINGECKO_TRENDING_URL = "https://api.coingecko.com/api/v3/search/trending"

# Default request timeout (seconds)
_HTTP_TIMEOUT = 10

# When a HIGH-impact event is within 24h, reduce conviction by this factor
_CAUTION_MULTIPLIER = 0.5

# Cache TTL for trending list (10 minutes)
_TRENDING_CACHE_TTL = 600.0


class SentimentAnalyst(BaseAnalystAgent):
    """
    Specialist in market sentiment derived from news and social data.

    Expected market_data shape:
        {
            "asset_class": "crypto" | "stock",   # optional, default "crypto"
            "coingecko_id": "bitcoin",            # optional, for trending check
            "extra_headlines": [                  # optional caller-supplied headlines
                {"title": "...", "published_at": "ISO8601", "source": "..."},
            ]
        }

    Environment variables (optional — agents degrade gracefully if absent):
        NEWS_API_KEY      : NewsAPI key for stock/general news
        CRYPTOPANIC_KEY   : CryptoPanic API auth token
    """

    def __init__(self) -> None:
        super().__init__()
        self._economic_calendar = EconomicCalendar()
        # Simple module-level cache for trending data
        self._trending_cache: tuple[float, list[str]] | None = None

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
        _context: dict[str, Any],
    ) -> AgentSignal:
        asset_class = market_data.get("asset_class", "crypto").lower()
        extra_headlines = market_data.get("extra_headlines", [])
        coingecko_id = market_data.get("coingecko_id", "")

        headlines: list[dict[str, Any]] = list(extra_headlines)
        fear_greed_score: float | None = None

        # Check economic calendar — are we near a HIGH-impact event?
        high_impact_soon = self._economic_calendar.is_high_impact_event_within_hours(hours=24)
        if high_impact_soon:
            logger.warning(
                "%s: HIGH-impact macro event within 24h — applying caution multiplier to %s",
                self.name, symbol,
            )

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_HTTP_TIMEOUT)
        ) as session:
            # Fetch from all available sources concurrently
            results = await asyncio.gather(
                self._fetch_cryptopanic(session, symbol),
                self._fetch_newsapi(session, symbol),
                self._fetch_fear_greed(session) if asset_class == "crypto" else self._noop(),
                self._fetch_yahoo_finance_news(symbol),
                self._fetch_coingecko_trending(session, coingecko_id) if asset_class == "crypto" else self._noop(),
                return_exceptions=True,
            )

        cp_headlines, newsapi_headlines, fg_result, yf_headlines, trending_result = results

        if isinstance(cp_headlines, list):
            headlines.extend(cp_headlines)
        if isinstance(newsapi_headlines, list):
            headlines.extend(newsapi_headlines)
        if isinstance(yf_headlines, list):
            headlines.extend(yf_headlines)

        if isinstance(fg_result, dict):
            fear_greed_score = fg_result.get("score")

        # CoinGecko trending boost
        is_trending = False
        if isinstance(trending_result, dict):
            is_trending = bool(trending_result.get("is_trending", False))
            if is_trending:
                logger.debug("%s is currently trending on CoinGecko", symbol)

        if not headlines and fear_greed_score is None:
            return AgentSignal.neutral(
                self.name,
                reason="No sentiment data available for this symbol",
            )

        # Score headlines by recency-weighted sentiment (simple heuristic)
        quant_sentiment = self._quant_sentiment_score(headlines)

        # Apply CoinGecko trending boost (trending assets tend to see momentum)
        if is_trending:
            quant_sentiment = min(1.0, quant_sentiment + 0.1)

        # Incorporate Fear & Greed Index for crypto
        if fear_greed_score is not None:
            # Fear & Greed: 0 = extreme fear (bearish), 100 = extreme greed (bullish)
            fg_conviction = (fear_greed_score - 50) / 50.0   # maps to [-1, 1]
            # Blend: 60% headline sentiment, 40% F&G
            quant_sentiment = 0.6 * quant_sentiment + 0.4 * fg_conviction

        # Dampen conviction when a high-impact event is imminent
        if high_impact_soon:
            quant_sentiment *= _CAUTION_MULTIPLIER

        # Build a compact news brief for Claude
        headline_text = self._format_headlines_for_claude(headlines[:15])

        try:
            signal = await self._claude_analysis(
                symbol, headline_text, quant_sentiment, fear_greed_score,
                high_impact_soon=high_impact_soon,
                is_trending=is_trending,
            )
        except Exception as exc:
            logger.warning(
                "%s: Claude unavailable (%s), using quant sentiment", self.name, exc
            )
            signal = self._quant_signal(quant_sentiment, fear_greed_score, high_impact_soon)

        return signal

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    async def _fetch_cryptopanic(
        self, session: aiohttp.ClientSession, symbol: str
    ) -> list[dict[str, Any]]:
        """Fetch posts from CryptoPanic. Works without auth for public posts."""
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

    async def _fetch_yahoo_finance_news(self, symbol: str) -> list[dict[str, Any]]:
        """
        Fetch recent news from Yahoo Finance using the yfinance library.
        Runs in an executor to avoid blocking the event loop.

        Normalises output to the same headline dict shape used by other fetchers.
        """
        try:
            import yfinance as yf  # lazy import — optional dependency
        except ImportError:
            logger.debug("yfinance not installed — Yahoo Finance news unavailable")
            return []

        # Map crypto symbols to Yahoo Finance format (e.g. BTC/USDT → BTC-USD)
        clean = symbol.split("/")[0].split("-")[0].upper()
        yf_symbol = f"{clean}-USD" if "USDT" in symbol or "USD" in symbol else clean

        def _blocking_fetch() -> list[dict[str, Any]]:
            ticker = yf.Ticker(yf_symbol)
            return ticker.news or []  # type: ignore[return-value]

        try:
            raw: list[dict[str, Any]] = await asyncio.get_event_loop().run_in_executor(
                None, _blocking_fetch
            )
        except Exception as exc:
            logger.debug("Yahoo Finance news fetch failed for %s: %s", yf_symbol, exc)
            return []

        headlines = []
        for article in raw[:20]:
            # Convert UNIX timestamp to ISO 8601 for consistent processing
            ts = article.get("providerPublishTime", 0)
            if ts:
                published_at = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            else:
                published_at = ""
            headlines.append(
                {
                    "title": article.get("title", ""),
                    "published_at": published_at,
                    "source": article.get("publisher", "Yahoo Finance"),
                }
            )
        return headlines

    async def _fetch_coingecko_trending(
        self,
        session: aiohttp.ClientSession,
        coingecko_id: str,
    ) -> dict[str, Any]:
        """
        Check if a coin is currently in CoinGecko's trending list.
        Returns {"is_trending": bool, "rank": int | None}.
        """
        if not coingecko_id:
            return {"is_trending": False}

        # Check module-level cache to avoid repeated API calls
        now = time.monotonic()
        if self._trending_cache is not None:
            cached_at, trending_ids = self._trending_cache
            if now - cached_at < _TRENDING_CACHE_TTL:
                is_trending = coingecko_id.lower() in trending_ids
                return {"is_trending": is_trending}

        try:
            async with session.get(_COINGECKO_TRENDING_URL) as resp:
                if resp.status != 200:
                    return {"is_trending": False}
                data = await resp.json()
                coins = data.get("coins", [])
                trending_ids = [
                    entry.get("item", {}).get("id", "").lower()
                    for entry in coins
                ]
                self._trending_cache = (now, trending_ids)
                is_trending = coingecko_id.lower() in trending_ids
                return {"is_trending": is_trending}
        except Exception as exc:
            logger.debug("CoinGecko trending fetch failed: %s", exc)
            return {"is_trending": False}

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
        high_impact_soon: bool = False,
        is_trending: bool = False,
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

        trending_note = "\nNOTE: This asset is currently trending on CoinGecko." if is_trending else ""
        caution_note = (
            "\nWARNING: A HIGH-impact macro event is scheduled within 24 hours. "
            "Reduce conviction accordingly."
        ) if high_impact_soon else ""

        user_message = f"""Analyse market sentiment for {symbol} from these recent headlines.{fg_section}{trending_note}{caution_note}

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
            return self._quant_signal(quant_sentiment, fear_greed, high_impact_soon)

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
                "is_trending": is_trending,
                "high_impact_event_soon": high_impact_soon,
            },
        )

    def _quant_signal(
        self,
        quant_sentiment: float,
        fear_greed: float | None,
        high_impact_soon: bool = False,
    ) -> AgentSignal:
        direction = self._direction_from_conviction(quant_sentiment)
        fg_note = f" Fear&Greed index: {fear_greed:.0f}." if fear_greed is not None else ""
        caution_note = " HIGH-impact macro event within 24h — caution applied." if high_impact_soon else ""
        reasoning = (
            f"Quant sentiment score: {quant_sentiment:+.2f}.{fg_note}{caution_note} "
            "Claude analysis unavailable — using lexical headline scoring."
        )
        confidence = min(0.6, abs(quant_sentiment))
        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=quant_sentiment,
            reasoning=reasoning,
            confidence=confidence,
            metadata={
                "mode": "quant_fallback",
                "fear_greed_score": fear_greed,
                "high_impact_event_soon": high_impact_soon,
            },
        )
