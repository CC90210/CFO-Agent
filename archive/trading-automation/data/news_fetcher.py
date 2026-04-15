"""
data/news_fetcher.py
--------------------
News & Sentiment Data Fetcher for Atlas Trading Agent.

Free data sources used:
  CryptoPanic  — crypto news aggregator (free tier, 5 req/min)
  NewsAPI.org  — general financial news (free tier, 100 req/day)
  Reddit API   — r/cryptocurrency and r/wallstreetbets sentiment
  Fear & Greed — alternative.me index (no auth required)
  Yahoo Finance — per-symbol news via yfinance library
  CoinGecko    — trending coins + market data (no key needed)
  FMP          — earnings calendar, SEC filings (free tier, 250 calls/day)
  FRED         — macro economic indicators (Fed rates, CPI, unemployment)

All methods are async, all results are cached to avoid hammering rate limits.

Cache TTLs:
  News items         — 5 minutes
  Sentiment          — 1 hour
  Macro / calendar   — 6 hours
  CoinGecko market   — 10 minutes

Required environment variables (in .env):
  CRYPTOPANIC_API_KEY  — optional but raises free tier limit
  NEWSAPI_KEY          — required for NewsAPI
  REDDIT_CLIENT_ID     — for Reddit OAuth2
  REDDIT_CLIENT_SECRET — for Reddit OAuth2
  FMP_API_KEY          — for Financial Modeling Prep (free tier)
  FRED_API_KEY         — for FRED macro data (free at fred.stlouisfed.org)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
_COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_FMP_BASE = "https://financialmodelingprep.com/api/v3"
_FRED_BASE = "https://api.stlouisfed.org/fred"
_REDDIT_USER_AGENT = "Atlas-Trading-Agent/1.0"

_NEWS_CACHE_TTL = 300.0        # 5 minutes
_SENTIMENT_CACHE_TTL = 3600.0  # 1 hour
_COINGECKO_CACHE_TTL = 600.0   # 10 minutes
_MACRO_CACHE_TTL = 21600.0     # 6 hours


# ---------------------------------------------------------------------------
# Dataclasses
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


@dataclass
class MacroEvent:
    """A scheduled macro-economic event that can move markets."""

    name: str
    date: str                # ISO 8601 date string, e.g. "2026-03-19"
    expected_impact: str     # "HIGH" | "MEDIUM" | "LOW"
    previous_value: str = ""
    forecast_value: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "date": self.date,
            "expected_impact": self.expected_impact,
            "previous_value": self.previous_value,
            "forecast_value": self.forecast_value,
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
    fmp_api_key          : Financial Modeling Prep API key (free tier)
    fred_api_key         : FRED API key (free at fred.stlouisfed.org)

    All keys default to empty string — the corresponding methods will
    gracefully return empty results if the key is not configured rather
    than raising exceptions.

    Usage
    -----
    async with NewsFetcher(cryptopanic_api_key="abc") as nf:
        news        = await nf.fetch_crypto_news("BTC")
        yf_news     = await nf.fetch_yahoo_finance_news("AAPL")
        cg_data     = await nf.fetch_coingecko_market_data("bitcoin")
        macro       = await nf.fetch_macro_calendar()
        earnings    = await nf.fetch_earnings_calendar("NVDA")
        fg          = await nf.fetch_fear_greed_index()
        reddit      = await nf.fetch_reddit_sentiment("cryptocurrency", "bitcoin")
    """

    def __init__(
        self,
        cryptopanic_api_key: str = "",
        newsapi_key: str = "",
        reddit_client_id: str = "",
        reddit_client_secret: str = "",
        fmp_api_key: str = "",
        fred_api_key: str = "",
    ) -> None:
        self._cp_key = cryptopanic_api_key
        self._na_key = newsapi_key
        self._reddit_id = reddit_client_id
        self._reddit_secret = reddit_client_secret
        self._fmp_key = fmp_api_key
        self._fred_key = fred_api_key

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
    # Original public methods (unchanged)
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
            return cached  # type: ignore[return-value]

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
            return cached  # type: ignore[return-value]

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
          +1 for titles containing bullish keywords
          -1 for titles containing bearish keywords
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
        logger.debug(
            "Reddit sentiment for '%s' in r/%s: %.3f (%d posts)",
            keyword, subreddit, sentiment, len(scores),
        )
        return sentiment

    # ------------------------------------------------------------------
    # NEW: Yahoo Finance news (via yfinance)
    # ------------------------------------------------------------------

    async def fetch_yahoo_finance_news(
        self,
        symbol: str,
        limit: int = 20,
    ) -> list[NewsItem]:
        """
        Fetch recent news for a symbol from Yahoo Finance using the yfinance
        library. Runs the blocking yfinance call in a thread executor to keep
        the event loop free.

        yfinance is free and requires no API key.

        Parameters
        ----------
        symbol : ticker or crypto symbol, e.g. "AAPL", "BTC-USD"
        limit  : max number of articles to return

        Returns
        -------
        list of NewsItem, sorted newest-first; empty list on failure
        """
        cache_key = f"yf_news:{symbol.upper()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug("Yahoo Finance news cache hit: %s", symbol)
            return cached  # type: ignore[return-value]

        try:
            import yfinance as yf  # imported lazily — not required at module level
        except ImportError:
            logger.warning("yfinance not installed — run: pip install yfinance")
            return []

        def _blocking_fetch() -> list[dict[str, Any]]:
            ticker = yf.Ticker(symbol)
            return ticker.news or []  # type: ignore[return-value]

        try:
            raw_news: list[dict[str, Any]] = await asyncio.get_event_loop().run_in_executor(
                None, _blocking_fetch
            )
        except Exception as exc:
            logger.error("Yahoo Finance news fetch failed for %s: %s", symbol, exc)
            return []

        items: list[NewsItem] = []
        for article in raw_news[:limit]:
            # yfinance returns providerPublishTime as a UNIX timestamp
            ts = float(article.get("providerPublishTime", 0))
            items.append(
                NewsItem(
                    title=article.get("title", ""),
                    source=article.get("publisher", "Yahoo Finance"),
                    timestamp=ts,
                    url=article.get("link", ""),
                    impact_estimate=0.0,
                    symbols=[symbol.upper()],
                    body=article.get("summary", ""),
                )
            )

        # Sort newest-first
        items.sort(key=lambda x: x.timestamp, reverse=True)
        self._cache.set(cache_key, items, _NEWS_CACHE_TTL)
        logger.debug("Fetched %d Yahoo Finance news items for %s", len(items), symbol)
        return items

    # ------------------------------------------------------------------
    # NEW: CoinGecko market data
    # ------------------------------------------------------------------

    async def fetch_coingecko_market_data(self, coin_id: str) -> dict[str, Any]:
        """
        Fetch comprehensive market data for a coin from CoinGecko's free API.
        No API key required.

        Parameters
        ----------
        coin_id : CoinGecko coin identifier, e.g. "bitcoin", "ethereum", "solana"

        Returns
        -------
        dict with keys:
            price_usd         : float
            market_cap_usd    : float
            volume_24h_usd    : float
            price_change_24h  : float  (percentage)
            price_change_7d   : float  (percentage)
            price_change_30d  : float  (percentage)
            ath_usd           : float
            ath_change_pct    : float  (percentage below ATH, negative)
            atl_usd           : float
            atl_change_pct    : float  (percentage above ATL, positive)
            circulating_supply: float
            total_supply      : float | None
            market_cap_rank   : int
            trending_score    : float  (0.0 if not in trending list)
        Returns empty dict on failure.
        """
        cache_key = f"cg_market:{coin_id.lower()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug("CoinGecko cache hit: %s", coin_id)
            return cached  # type: ignore[return-value]

        url = f"{_COINGECKO_BASE}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false",
        }

        try:
            data = await self._get_json(url, params=params)
        except Exception as exc:
            logger.error("CoinGecko market data fetch failed for %s: %s", coin_id, exc)
            return {}

        md = data.get("market_data", {})

        def _usd(field: str) -> float | None:
            val = md.get(field, {})
            if isinstance(val, dict):
                return val.get("usd")
            return None

        result: dict[str, Any] = {
            "price_usd": _usd("current_price"),
            "market_cap_usd": _usd("market_cap"),
            "volume_24h_usd": _usd("total_volume"),
            "price_change_24h": md.get("price_change_percentage_24h"),
            "price_change_7d": md.get("price_change_percentage_7d"),
            "price_change_30d": md.get("price_change_percentage_30d"),
            "ath_usd": _usd("ath"),
            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd"),
            "atl_usd": _usd("atl"),
            "atl_change_pct": md.get("atl_change_percentage", {}).get("usd"),
            "circulating_supply": md.get("circulating_supply"),
            "total_supply": md.get("total_supply"),
            "market_cap_rank": data.get("market_cap_rank"),
            "trending_score": 0.0,  # populated below if in trending list
        }

        # Check if coin is currently trending
        try:
            trending_data = await self._get_json(f"{_COINGECKO_BASE}/search/trending")
            trending_coins = trending_data.get("coins", [])
            for entry in trending_coins:
                item = entry.get("item", {})
                if item.get("id", "").lower() == coin_id.lower():
                    # Score based on rank (1st = 1.0, 7th = ~0.14)
                    rank = item.get("score", 6)
                    result["trending_score"] = round(1.0 / (rank + 1), 3)
                    break
        except Exception:
            pass  # trending check is best-effort

        self._cache.set(cache_key, result, _COINGECKO_CACHE_TTL)
        logger.debug("CoinGecko market data fetched for %s", coin_id)
        return result

    # ------------------------------------------------------------------
    # NEW: Macro economic calendar (FRED)
    # ------------------------------------------------------------------

    async def fetch_macro_calendar(self) -> list[MacroEvent]:
        """
        Fetch upcoming macro-economic events using the FRED API.

        Pulls key series release dates for:
          - Federal Funds Rate (DFF)
          - CPI (CPIAUCSL)
          - Unemployment Rate (UNRATE)
          - Non-Farm Payrolls (PAYEMS)
          - GDP (GDP)

        Requires FRED_API_KEY environment variable (free at fred.stlouisfed.org).

        Returns
        -------
        list of MacroEvent sorted by date ascending; empty list on failure
        """
        cache_key = "macro_calendar"
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug("Macro calendar cache hit")
            return cached  # type: ignore[return-value]

        if not self._fred_key:
            logger.warning("FRED_API_KEY not configured — macro calendar unavailable")
            return []

        # FRED series IDs and their market impact
        series_config = [
            ("FEDFUNDS", "Fed Funds Rate", "HIGH"),
            ("CPIAUCSL", "CPI (Inflation)", "HIGH"),
            ("UNRATE", "Unemployment Rate", "HIGH"),
            ("PAYEMS", "Non-Farm Payrolls", "HIGH"),
            ("GDP", "GDP Growth", "MEDIUM"),
            ("T10Y2Y", "10Y-2Y Yield Spread", "MEDIUM"),
        ]

        events: list[MacroEvent] = []
        now_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

        for series_id, name, impact in series_config:
            url = f"{_FRED_BASE}/series/release/dates"
            params = {
                "series_id": series_id,
                "api_key": self._fred_key,
                "file_type": "json",
                "realtime_start": now_str,
                "limit": "3",
                "sort_order": "asc",
            }
            try:
                data = await self._get_json(url, params=params)
                release_dates = data.get("release_dates", [])
                for entry in release_dates:
                    release_date = entry.get("date", "")
                    if release_date and release_date >= now_str:
                        events.append(
                            MacroEvent(
                                name=name,
                                date=release_date,
                                expected_impact=impact,
                                previous_value="",
                                forecast_value="",
                            )
                        )
            except Exception as exc:
                logger.debug("FRED fetch failed for %s: %s", series_id, exc)
                continue

        # Sort by date
        events.sort(key=lambda e: e.date)
        self._cache.set(cache_key, events, _MACRO_CACHE_TTL)
        logger.debug("Fetched %d macro events from FRED", len(events))
        return events

    # ------------------------------------------------------------------
    # NEW: Earnings calendar (FMP)
    # ------------------------------------------------------------------

    async def fetch_earnings_calendar(self, symbol: str) -> dict[str, Any]:
        """
        Fetch the next earnings date and EPS estimates for a stock symbol
        using the Financial Modeling Prep API (free tier: 250 calls/day).

        Requires FMP_API_KEY environment variable.

        Parameters
        ----------
        symbol : stock ticker, e.g. "AAPL", "NVDA"

        Returns
        -------
        dict with keys:
            symbol          : str
            next_earnings_date : str (ISO date or "")
            eps_estimate    : float | None
            eps_actual      : float | None  (None if not yet reported)
            revenue_estimate: float | None
        Returns empty dict on failure or missing key.
        """
        cache_key = f"earnings:{symbol.upper()}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        if not self._fmp_key:
            logger.warning("FMP_API_KEY not configured — earnings calendar unavailable")
            return {}

        url = f"{_FMP_BASE}/earnings-surprises/{symbol.upper()}"
        params = {"apikey": self._fmp_key}

        # Also fetch upcoming earnings date from the calendar endpoint
        calendar_url = f"{_FMP_BASE}/earnings-calendar"
        now = datetime.now(tz=timezone.utc)
        calendar_params = {
            "apikey": self._fmp_key,
            "from": now.strftime("%Y-%m-%d"),
            "to": (now.replace(month=min(now.month + 3, 12))).strftime("%Y-%m-%d"),
        }

        result: dict[str, Any] = {
            "symbol": symbol.upper(),
            "next_earnings_date": "",
            "eps_estimate": None,
            "eps_actual": None,
            "revenue_estimate": None,
        }

        try:
            cal_data = await self._get_json(calendar_url, params=calendar_params)
            if isinstance(cal_data, list):
                for entry in cal_data:
                    if entry.get("symbol", "").upper() == symbol.upper():
                        result["next_earnings_date"] = entry.get("date", "")
                        result["eps_estimate"] = entry.get("epsEstimated")
                        result["revenue_estimate"] = entry.get("revenueEstimated")
                        break
        except Exception as exc:
            logger.debug("FMP earnings calendar fetch failed for %s: %s", symbol, exc)

        try:
            surprise_data = await self._get_json(url, params=params)
            if isinstance(surprise_data, list) and surprise_data:
                latest = surprise_data[0]
                result["eps_actual"] = latest.get("actualEarningResult")
                if not result["eps_estimate"]:
                    result["eps_estimate"] = latest.get("estimatedEarning")
        except Exception as exc:
            logger.debug("FMP earnings surprise fetch failed for %s: %s", symbol, exc)

        self._cache.set(cache_key, result, _MACRO_CACHE_TTL)
        logger.debug("Earnings calendar fetched for %s: next=%s", symbol, result["next_earnings_date"])
        return result

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
            async with self._session.post(
                _REDDIT_AUTH_URL, data=data, auth=auth, headers=headers
            ) as resp:
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
        bullish_words = {
            "moon", "buy", "long", "bullish", "pump", "rocket",
            "breakout", "surge", "rally",
        }
        bearish_words = {
            "crash", "dump", "sell", "short", "bearish", "dead",
            "collapse", "tank", "plunge",
        }
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
    if not iso_str:
        return 0.0
    # Handle both "2024-01-01T12:00:00Z" and "2024-01-01T12:00:00+00:00"
    iso_str = iso_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.timestamp()
    except ValueError:
        return 0.0
