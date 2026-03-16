"""
data/news_fetcher.py
--------------------
News & Sentiment Data Fetcher for Atlas Trading Agent.

Free data sources used:
  CryptoPanic  — crypto news aggregator (free tier, 5 req/min)
  NewsAPI.org  — general financial news (free tier, 100 req/day)
  Reddit API   — r/cryptocurrency and r/wallstreetbets sentiment
  Fear & Greed — alternative.me index (no auth required)

All methods are async, all results are cached to avoid hammering rate limits.

Cache TTLs:
  News items   — 5 minutes
  Sentiment    — 1 hour
  Fear & Greed — 1 hour

Required environment variables (in .env):
  CRYPTOPANIC_API_KEY  — optional but raises free tier limit
  NEWSAPI_KEY          — required for NewsAPI
  REDDIT_CLIENT_ID     — for Reddit OAuth2
  REDDIT_CLIENT_SECRET — for Reddit OAuth2
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import aiohttp

logger = logging.getLogger("atlas.news")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_CRYPTOPANIC_BASE = "https://cryptopanic.com/api/v1"
_NEWSAPI_BASE = "https://newsapi.org/v2"
_REDDIT_OAUTH_BASE = "https://oauth.reddit.com"
_REDDIT_AUTH_URL = "https://www.reddit.com/api/v1/access_token"
_FEAR_GREED_URL = "https://api.alternative.me/fng/"
_REDDIT_USER_AGENT = "Atlas-Trading-Agent/1.0"

_NEWS_CACHE_TTL = 300.0      # 5 minutes
_SENTIMENT_CACHE_TTL = 3600.0  # 1 hour
_MAX_MESSAGES_PER_MINUTE = 30


# ---------------------------------------------------------------------------
# NewsItem dataclass
# ---------------------------------------------------------------------------


@dataclass
class NewsItem:
    """A single news article or social mention."""

    title: str
    source: str
    timestamp: float  # UNIX epoch
    url: str
    impact_estimate: float = 0.0  # [-1.0, 1.0] — negative=bearish, positive=bullish
    symbols: list[str] = field(default_factory=list)
    body: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "source": self.source,
            "timestamp": self.timestamp,
            "url": self.url,
            "impact_estimate": self.impact_estimate,
            "symbols": self.symbols,
            "body": self.body,
        }


# ---------------------------------------------------------------------------
# Simple in-memory cache
# ---------------------------------------------------------------------------


class _Cache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        self._store[key] = (value, time.monotonic() + ttl)


# ---------------------------------------------------------------------------
# NewsFetcher
# ---------------------------------------------------------------------------


class NewsFetcher:
    """
    Aggregate news and sentiment from multiple free sources.

    Parameters
    ----------
    cryptopanic_api_key  : CryptoPanic API key (optional but recommended)
    newsapi_key          : NewsAPI.org API key
    reddit_client_id     : Reddit OAuth2 client ID
    reddit_client_secret : Reddit OAuth2 client secret

    All keys default to empty string — the corresponding methods will
    gracefully return empty results if the key is not configured rather
    than raising exceptions.

    Usage
    -----
    async with NewsFetcher(cryptopanic_api_key="abc") as nf:
        news   = await nf.fetch_crypto_news("BTC")
        fg     = await nf.fetch_fear_greed_index()
        reddit = await nf.fetch_reddit_sentiment("cryptocurrency", "bitcoin")
    """

    def __init__(
        self,
        cryptopanic_api_key: str = "",
        newsapi_key: str = "",
        reddit_client_id: str = "",
        reddit_client_secret: str = "",
    ) -> None:
        self._cp_key = cryptopanic_api_key
        self._na_key = newsapi_key
        self._reddit_id = reddit_client_id
        self._reddit_secret = reddit_client_secret

        self._session: aiohttp.ClientSession | None = None
        self._reddit_token: str = ""
        self._reddit_token_expires: float = 0.0
        self._cache: _Cache = _Cache()

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "NewsFetcher":
        self._session = aiohttp.ClientSession(
            headers={"User-Agent": _REDDIT_USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=15),
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._session is not None:
            await self._session.close()

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def fetch_crypto_news(
        self,
        symbol: str,
        limit: int = 20,
    ) -> list[NewsItem]:
        """
        Fetch recent crypto news for a symbol from CryptoPanic.

        Parameters
        ----------
        symbol : base currency symbol, e.g. "BTC", "ETH"
        limit  : max number of articles to return

        Returns
        -------
        list of NewsItem, sorted newest-first
        """
        base = symbol.split("/")[0].upper()
        cache_key = f"crypto_news:{base}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug("News cache hit: %s", cache_key)
            return cached

        if not self._cp_key:
            logger.warning("CryptoPanic API key not configured — returning empty news")
            return []

        url = f"{_CRYPTOPANIC_BASE}/posts/"
        params: dict[str, str] = {
            "auth_token": self._cp_key,
            "currencies": base,
            "public": "true",
            "kind": "news",
        }

        try:
            data = await self._get_json(url, params=params)
        except Exception as exc:
            logger.error("CryptoPanic fetch failed: %s", exc)
            return []

        items: list[NewsItem] = []
        for post in data.get("results", [])[:limit]:
            published = post.get("published_at", "")
            ts = _parse_iso_to_epoch(published)
            impact = self._estimate_impact_from_votes(post)
            items.append(
                NewsItem(
                    title=post.get("title", ""),
                    source=post.get("source", {}).get("title", "CryptoPanic"),
                    timestamp=ts,
                    url=post.get("url", ""),
                    impact_estimate=impact,
                    symbols=[base],
                    body="",
                )
            )

        self._cache.set(cache_key, items, _NEWS_CACHE_TTL)
        logger.debug("Fetched %d crypto news items for %s", len(items), base)
        return items

    async def fetch_stock_news(
        self,
        symbol: str,
        limit: int = 10,
    ) -> list[NewsItem]:
        """
        Fetch recent financial news for a stock symbol from NewsAPI.

        Parameters
        ----------
        symbol : ticker symbol, e.g. "AAPL", "TSLA"
        limit  : max number of articles (capped at 100 by free tier)

        Returns
        -------
        list of NewsItem, sorted newest-first
        """
        cache_key = f"stock_news:{symbol}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if not self._na_key:
            logger.warning("NewsAPI key not configured — returning empty news")
            return []

        url = f"{_NEWSAPI_BASE}/everything"
        params: dict[str, str] = {
            "q": symbol,
            "apiKey": self._na_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": str(min(limit, 100)),
        }

        try:
            data = await self._get_json(url, params=params)
        except Exception as exc:
            logger.error("NewsAPI fetch failed: %s", exc)
            return []

        items: list[NewsItem] = []
        for article in data.get("articles", [])[:limit]:
            ts = _parse_iso_to_epoch(article.get("publishedAt", ""))
            items.append(
                NewsItem(
                    title=article.get("title", ""),
                    source=article.get("source", {}).get("name", "NewsAPI"),
                    timestamp=ts,
                    url=article.get("url", ""),
                    impact_estimate=0.0,  # NewsAPI doesn't provide sentiment
                    symbols=[symbol],
                    body=article.get("description", ""),
                )
            )

        self._cache.set(cache_key, items, _NEWS_CACHE_TTL)
        return items

    async def fetch_fear_greed_index(self) -> int:
        """
        Return the current Crypto Fear & Greed Index (0–100).

        0   = Extreme Fear (historically good to buy)
        100 = Extreme Greed (historically good to sell)

        Source: alternative.me (no API key required)
        """
        cached = self._cache.get("fear_greed")
        if cached is not None:
            return int(cached)

        try:
            data = await self._get_json(_FEAR_GREED_URL, params={"limit": "1"})
        except Exception as exc:
            logger.error("Fear & Greed fetch failed: %s", exc)
            return 50  # neutral fallback

        value_str = data.get("data", [{}])[0].get("value", "50")
        value = int(value_str)
        self._cache.set("fear_greed", value, _SENTIMENT_CACHE_TTL)
        logger.debug("Fear & Greed Index: %d", value)
        return value

    async def fetch_reddit_sentiment(
        self,
        subreddit: str,
        keyword: str,
        post_limit: int = 50,
    ) -> float:
        """
        Return a sentiment score for a keyword across recent hot posts
        in a subreddit.

        The score is a simple keyword-heuristic approach:
          +1 for titles containing bullish keywords (moon, buy, long, bullish, pump)
          -1 for titles containing bearish keywords (crash, dump, sell, short, bearish, dead)
          0  for neutral
        Scores are averaged across matched posts.

        Parameters
        ----------
        subreddit  : e.g. "cryptocurrency" or "wallstreetbets"
        keyword    : search term to filter posts
        post_limit : number of hot posts to analyse

        Returns
        -------
        float in [-1.0, 1.0]; 0.0 on error or no matching posts
        """
        cache_key = f"reddit:{subreddit}:{keyword}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return float(cached)

        if not (self._reddit_id and self._reddit_secret):
            logger.warning("Reddit credentials not configured — returning neutral sentiment")
            return 0.0

        token = await self._get_reddit_token()
        if not token:
            return 0.0

        url = f"{_REDDIT_OAUTH_BASE}/r/{subreddit}/search"
        params: dict[str, str] = {
            "q": keyword,
            "sort": "hot",
            "restrict_sr": "1",
            "limit": str(min(post_limit, 100)),
            "t": "day",
        }
        headers = {"Authorization": f"bearer {token}"}

        try:
            data = await self._get_json(url, params=params, headers=headers)
        except Exception as exc:
            logger.error("Reddit fetch failed: %s", exc)
            return 0.0

        posts = data.get("data", {}).get("children", [])
        scores: list[float] = []
        for post in posts:
            title = post.get("data", {}).get("title", "").lower()
            score = self._score_reddit_title(title)
            if score != 0.0:
                scores.append(score)

        sentiment = sum(scores) / len(scores) if scores else 0.0
        self._cache.set(cache_key, sentiment, _SENTIMENT_CACHE_TTL)
        logger.debug("Reddit sentiment for '%s' in r/%s: %.3f (%d posts)", keyword, subreddit, sentiment, len(scores))
        return sentiment

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _get_json(
        self,
        url: str,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("NewsFetcher must be used as an async context manager")
        async with self._session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()
            return await resp.json()  # type: ignore[no-any-return]

    async def _get_reddit_token(self) -> str:
        """Obtain or refresh the Reddit OAuth2 bearer token."""
        if self._reddit_token and time.monotonic() < self._reddit_token_expires:
            return self._reddit_token

        if self._session is None:
            raise RuntimeError("NewsFetcher must be used as an async context manager")

        auth = aiohttp.BasicAuth(self._reddit_id, self._reddit_secret)
        data = {"grant_type": "client_credentials"}
        headers = {"User-Agent": _REDDIT_USER_AGENT}

        try:
            async with self._session.post(_REDDIT_AUTH_URL, data=data, auth=auth, headers=headers) as resp:
                resp.raise_for_status()
                token_data: dict[str, Any] = await resp.json()
        except Exception as exc:
            logger.error("Reddit OAuth2 token fetch failed: %s", exc)
            return ""

        self._reddit_token = token_data.get("access_token", "")
        expires_in = float(token_data.get("expires_in", 3600))
        self._reddit_token_expires = time.monotonic() + expires_in - 60  # 1 min buffer
        return self._reddit_token

    @staticmethod
    def _estimate_impact_from_votes(post: dict[str, Any]) -> float:
        """
        Derive a rough impact estimate from CryptoPanic vote data.
        Positive votes → bullish, negative votes → bearish.
        """
        votes = post.get("votes", {})
        positive = int(votes.get("positive", 0))
        negative = int(votes.get("negative", 0))
        total = positive + negative
        if total == 0:
            return 0.0
        return (positive - negative) / total

    @staticmethod
    def _score_reddit_title(title: str) -> float:
        """Simple keyword-based sentiment scoring for a Reddit post title."""
        bullish_words = {"moon", "buy", "long", "bullish", "pump", "rocket", "breakout", "surge", "rally"}
        bearish_words = {"crash", "dump", "sell", "short", "bearish", "dead", "collapse", "tank", "plunge"}
        words = set(title.lower().split())
        if words & bullish_words:
            return 1.0
        if words & bearish_words:
            return -1.0
        return 0.0


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def _parse_iso_to_epoch(iso_str: str) -> float:
    """Parse an ISO 8601 string to a UNIX epoch float; return 0.0 on failure."""
    import datetime

    if not iso_str:
        return 0.0
    # Handle both "2024-01-01T12:00:00Z" and "2024-01-01T12:00:00+00:00"
    iso_str = iso_str.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(iso_str)
        return dt.timestamp()
    except ValueError:
        return 0.0
