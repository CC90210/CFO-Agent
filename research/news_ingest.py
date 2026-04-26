"""
research/news_ingest.py
-----------------------
Multi-source news aggregation for Atlas Research.

Sources:
- RSS feeds (Reuters, BBC, AP, Bloomberg, CNBC, FT, WSJ, MarketWatch,
  Seeking Alpha, Benzinga, Yahoo Finance, SEC Press Releases)
- Google News RSS (query-based, no key required)
- NewsAPI (100 req/day free — requires NEWSAPI_KEY in .env)
- SEC EDGAR JSON API (no key required)

Caching: news results cached 1 hour to data/cache/.
All I/O is synchronous; callers that need async should run in a thread pool.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv

try:
    import feedparser  # type: ignore[import-untyped]
    _FEEDPARSER_AVAILABLE = True
except ImportError:
    _FEEDPARSER_AVAILABLE = False

# Belt-and-suspenders: load .env at import time so NEWSAPI_KEY / FMP_KEY /
# ALPHA_VANTAGE_KEY / FINNHUB_KEY are visible even when callers bypass
# config.settings (smoke tests, ad-hoc scripts).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Cache configuration
# ─────────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_NEWS_TTL_SECONDS = 3600  # 1 hour


# ─────────────────────────────────────────────────────────────────────────────
#  Curated RSS feed dictionary
# ─────────────────────────────────────────────────────────────────────────────

CURATED_FEEDS: dict[str, str] = {
    "reuters_business": "https://feeds.reuters.com/reuters/businessNews",
    "bbc_business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "ap_business": "https://rsshub.app/ap/topics/business",
    "bloomberg_markets": "https://feeds.bloomberg.com/markets/news.rss",
    "bloomberg_technology": "https://feeds.bloomberg.com/technology/news.rss",
    "cnbc_top_news": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "cnbc_finance": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "ft_markets": "https://www.ft.com/markets?format=rss",
    "wsj_markets": "https://feeds.a.wsj.com/rss/RSSMarketsMain.xml",
    "marketwatch_top": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "marketwatch_marketpulse": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
    "seeking_alpha": "https://seekingalpha.com/market_currents.xml",
    "benzinga": "https://www.benzinga.com/feeds/news",
    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
    "sec_press_releases": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=&dateb=&owner=include&count=20&search_text=&output=atom",
    "investing_com": "https://www.investing.com/rss/news.rss",
    "zerohedge": "https://feeds.feedburner.com/zerohedge/feed",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class NewsItem:
    """A single news article from any source."""

    date: datetime
    source: str
    title: str
    url: str
    summary: str
    sentiment: Optional[float] = None  # -1.0 bearish → +1.0 bullish, None = not yet scored
    tickers_mentioned: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "tickers_mentioned": self.tickers_mentioned,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "NewsItem":
        return cls(
            date=datetime.fromisoformat(d["date"]),
            source=d["source"],
            title=d["title"],
            url=d["url"],
            summary=d.get("summary", ""),
            sentiment=d.get("sentiment"),
            tickers_mentioned=d.get("tickers_mentioned", []),
        )


@dataclass
class Filing:
    """An SEC EDGAR filing."""

    ticker: str
    form_type: str
    filed_date: datetime
    accession_number: str
    description: str
    filing_url: str

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "form_type": self.form_type,
            "filed_date": self.filed_date.isoformat(),
            "accession_number": self.accession_number,
            "description": self.description,
            "filing_url": self.filing_url,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  Cache helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cache_key(identifier: str) -> Path:
    """Return the cache file path for a given identifier string."""
    h = hashlib.md5(identifier.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"news_{h}.json"


def _cache_read(path: Path, ttl: int) -> Optional[list[dict]]:
    """Return cached data if it exists and is still fresh, else None."""
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _cache_write(path: Path, data: list[dict]) -> None:
    """Persist data to the cache file."""
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.warning("Cache write failed for %s: %s", path, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  RSS fetcher
# ─────────────────────────────────────────────────────────────────────────────

def fetch_rss(url: str, source_name: str = "") -> list[NewsItem]:
    """
    Parse an RSS/Atom feed and return a list of NewsItem objects.

    Gracefully returns an empty list if feedparser is unavailable or
    the feed is unreachable.
    """
    if not _FEEDPARSER_AVAILABLE:
        logger.warning("feedparser not installed — RSS ingestion disabled. Run: pip install feedparser")
        return []

    cache_path = _cache_key(f"rss:{url}")
    cached = _cache_read(cache_path, _NEWS_TTL_SECONDS)
    if cached is not None:
        return [NewsItem.from_dict(d) for d in cached]

    name = source_name or url.split("/")[2]
    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        logger.warning("RSS fetch failed for %s: %s", url, exc)
        return []

    items: list[NewsItem] = []
    for entry in feed.entries:
        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        if pub:
            dt = datetime(*pub[:6], tzinfo=timezone.utc)
        else:
            dt = datetime.now(timezone.utc)

        summary = entry.get("summary", "") or entry.get("description", "")
        # Strip any HTML tags naively
        import re
        summary = re.sub(r"<[^>]+>", "", summary).strip()

        items.append(NewsItem(
            date=dt,
            source=name,
            title=entry.get("title", "").strip(),
            url=entry.get("link", ""),
            summary=summary[:500],
        ))

    _cache_write(cache_path, [i.to_dict() for i in items])
    logger.info("Fetched %d items from %s", len(items), name)
    return items


def fetch_all_curated(max_per_feed: int = 10) -> list[NewsItem]:
    """Fetch all curated RSS feeds and return a merged, deduplicated list."""
    all_items: list[NewsItem] = []
    seen_urls: set[str] = set()

    for name, url in CURATED_FEEDS.items():
        try:
            items = fetch_rss(url, source_name=name)
            for item in items[:max_per_feed]:
                if item.url not in seen_urls:
                    all_items.append(item)
                    seen_urls.add(item.url)
        except Exception as exc:
            logger.debug("Skipping feed %s: %s", name, exc)

    all_items.sort(key=lambda x: x.date, reverse=True)
    return all_items


# ─────────────────────────────────────────────────────────────────────────────
#  Google News RSS (query-based, no key)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_google_news(query: str, days: int = 7) -> list[NewsItem]:
    """
    Search Google News RSS for a query string.

    Uses Google's public RSS endpoint — no API key required.
    Rate limit: Google may throttle heavy use. Results are cached 1 hour.
    """
    encoded = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en&when:{days}d"
    return fetch_rss(url, source_name=f"google_news:{query[:30]}")


# ─────────────────────────────────────────────────────────────────────────────
#  NewsAPI (100 req/day free)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_newsapi(query: str, days: int = 7) -> list[NewsItem]:
    """
    Fetch articles from NewsAPI (https://newsapi.org).

    Requires NEWSAPI_KEY in .env. Returns empty list if key is absent.
    Rate limit: 100 requests/day on the free tier — results cached 1 hour.
    """
    api_key = os.environ.get("NEWSAPI_KEY", "")
    if not api_key:
        logger.debug("NEWSAPI_KEY not set — skipping NewsAPI fetch")
        return []

    cache_path = _cache_key(f"newsapi:{query}:{days}")
    cached = _cache_read(cache_path, _NEWS_TTL_SECONDS)
    if cached is not None:
        return [NewsItem.from_dict(d) for d in cached]

    from datetime import timedelta, date as date_cls
    from_date = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()

    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 20,
        "apiKey": api_key,
    }

    try:
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("NewsAPI fetch failed: %s", exc)
        return []

    items: list[NewsItem] = []
    for article in data.get("articles", []):
        pub_str = article.get("publishedAt", "")
        try:
            dt = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
        except ValueError:
            dt = datetime.now(timezone.utc)

        items.append(NewsItem(
            date=dt,
            source=article.get("source", {}).get("name", "newsapi"),
            title=article.get("title", "").strip(),
            url=article.get("url", ""),
            summary=(article.get("description") or article.get("content") or "")[:500],
        ))

    _cache_write(cache_path, [i.to_dict() for i in items])
    logger.info("NewsAPI returned %d items for query '%s'", len(items), query)
    return items


# ─────────────────────────────────────────────────────────────────────────────
#  SEC EDGAR (no key required)
# ─────────────────────────────────────────────────────────────────────────────

def _get_cik(ticker: str) -> Optional[str]:
    """Resolve ticker to SEC CIK using the EDGAR company_tickers manifest."""
    from research._sec_client import get as sec_get

    cache_path = _cache_key(f"cik:{ticker.upper()}")
    cached = _cache_read(cache_path, ttl=86400)  # cache CIK mappings for 24h
    if cached:
        return cached[0].get("cik") if cached else None

    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    resp = sec_get(tickers_url, timeout=10)
    if resp is None:
        logger.warning("SEC CIK lookup failed for %s — feed unavailable", ticker)
        return None
    try:
        data = resp.json()
    except ValueError as exc:
        logger.warning("SEC CIK manifest unparseable for %s: %s", ticker, exc)
        return None

    ticker_upper = ticker.upper()
    for _, company in data.items():
        if company.get("ticker", "").upper() == ticker_upper:
            cik_str = str(company["cik_str"]).zfill(10)
            _cache_write(cache_path, [{"cik": cik_str}])
            return cik_str

    return None


def fetch_sec_filings(ticker: str, form: str = "8-K") -> list[Filing]:
    """
    Fetch recent SEC EDGAR filings for a ticker using the EDGAR REST API.

    No API key required. Returns up to 10 recent filings of the specified form type.
    Uses research._sec_client for proper User-Agent + retry/backoff.
    """
    from research._sec_client import get as sec_get

    cache_path = _cache_key(f"sec:{ticker.upper()}:{form}")
    cached = _cache_read(cache_path, ttl=_NEWS_TTL_SECONDS)
    if cached is not None:
        filings: list[Filing] = []
        for d in cached:
            try:
                filings.append(Filing(
                    ticker=d["ticker"],
                    form_type=d["form_type"],
                    filed_date=datetime.fromisoformat(d["filed_date"]),
                    accession_number=d["accession_number"],
                    description=d["description"],
                    filing_url=d["filing_url"],
                ))
            except (KeyError, ValueError):
                continue
        return filings

    cik = _get_cik(ticker)
    if not cik:
        logger.warning("Could not resolve CIK for ticker %s", ticker)
        return []

    submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    resp = sec_get(submissions_url, timeout=15, use_data_host=True)
    if resp is None:
        logger.warning("SEC filings fetch failed for %s (feed unavailable)", ticker)
        return []
    try:
        data = resp.json()
    except ValueError as exc:
        logger.warning("SEC submissions JSON unparseable for %s: %s", ticker, exc)
        return []

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    descriptions = recent.get("primaryDocument", [])

    results: list[Filing] = []
    for i, f in enumerate(forms):
        if f != form:
            continue
        try:
            filed_date = datetime.fromisoformat(dates[i])
        except (ValueError, IndexError):
            filed_date = datetime.now(timezone.utc)

        acc = accessions[i] if i < len(accessions) else ""
        acc_clean = acc.replace("-", "")
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_clean}/{descriptions[i] if i < len(descriptions) else ''}"

        results.append(Filing(
            ticker=ticker.upper(),
            form_type=f,
            filed_date=filed_date,
            accession_number=acc,
            description=descriptions[i] if i < len(descriptions) else "",
            filing_url=filing_url,
        ))

        if len(results) >= 10:
            break

    _cache_write(cache_path, [r.to_dict() for r in results])
    logger.info("SEC EDGAR returned %d %s filings for %s", len(results), form, ticker)
    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Finnhub company news (60 req/min free)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_finnhub_news(ticker: str, days: int = 14) -> list[NewsItem]:
    """
    Per-ticker news from Finnhub. Requires FINNHUB_KEY in .env.
    Adds source redundancy when EDGAR / Google News / NewsAPI degrade.
    """
    cache_path = _cache_key(f"finnhub_news:{ticker.upper()}:{days}")
    cached = _cache_read(cache_path, _NEWS_TTL_SECONDS)
    if cached is not None:
        return [NewsItem.from_dict(d) for d in cached]

    try:
        from research import finnhub_client
    except ImportError:
        return []

    raw = finnhub_client.company_news(ticker, days=days)
    items: list[NewsItem] = []
    for art in raw:
        ts = art.get("datetime", 0) or 0
        try:
            dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except (ValueError, OSError):
            dt = datetime.now(timezone.utc)
        title = (art.get("headline") or "").strip()
        if not title:
            continue
        items.append(NewsItem(
            date=dt,
            source=f"finnhub:{art.get('source', 'unknown')}",
            title=title,
            url=art.get("url", ""),
            summary=(art.get("summary") or "")[:500],
            tickers_mentioned=[ticker.upper()],
        ))

    _cache_write(cache_path, [i.to_dict() for i in items])
    logger.info("Finnhub returned %d news items for %s", len(items), ticker)
    return items


# ─────────────────────────────────────────────────────────────────────────────
#  FMP stock-news (250 req/day free)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_fmp_news(tickers: list[str], limit: int = 50) -> list[NewsItem]:
    """
    Stock news from Financial Modeling Prep stable API. Multi-ticker per request.
    Requires FMP_KEY in .env.

    Endpoint: /stable/news/stock?symbols=A,B,C (replaces legacy /api/v3/stock_news
    which now returns 403 "Legacy Endpoint" on free keys).

    /stable/news/stock returns articles with field names: symbol, publishedDate,
    publisher, title, url, text, image. Date format "YYYY-MM-DD HH:MM:SS".
    """
    api_key = os.environ.get("FMP_KEY", "")
    if not api_key or not tickers:
        return []

    tickers = [t.upper() for t in tickers]
    cache_path = _cache_key(f"fmp_news_stable:{','.join(sorted(tickers))}:{limit}")
    cached = _cache_read(cache_path, _NEWS_TTL_SECONDS)
    if cached is not None:
        return [NewsItem.from_dict(d) for d in cached]

    try:
        resp = requests.get(
            "https://financialmodelingprep.com/stable/news/stock",
            params={"symbols": ",".join(tickers), "limit": limit, "apikey": api_key},
            timeout=12,
        )
        resp.raise_for_status()
        articles = resp.json()
    except Exception as exc:
        logger.warning("FMP stable/news/stock fetch failed: %s", exc)
        return []

    if not isinstance(articles, list):
        return []

    items: list[NewsItem] = []
    for art in articles:
        pub = art.get("publishedDate", "") or ""
        # /stable/news returns "YYYY-MM-DD HH:MM:SS" — convert to ISO.
        try:
            iso = pub.replace(" ", "T") if "T" not in pub else pub
            dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            dt = datetime.now(timezone.utc)

        publisher = art.get("publisher") or art.get("site") or "unknown"
        items.append(NewsItem(
            date=dt,
            source=f"fmp:{publisher}",
            title=(art.get("title") or "").strip(),
            url=art.get("url", ""),
            summary=(art.get("text") or "")[:500],
            tickers_mentioned=[(art.get("symbol") or "").upper()] if art.get("symbol") else list(tickers),
        ))

    _cache_write(cache_path, [i.to_dict() for i in items])
    logger.info("FMP /stable/news/stock returned %d items for %s", len(items), tickers)
    return items


def fetch_alpha_vantage_news_sentiment(tickers: list[str], limit: int = 50) -> list[NewsItem]:
    """
    Alpha Vantage NEWS_SENTIMENT — free-tier endpoint that returns ticker-tagged
    articles with sentiment scores per ticker. Replaces the (now paid-only)
    OVERVIEW endpoint as Atlas's primary AV consumption.

    Each item carries a sentiment score in [-1, +1] derived from AV's
    `ticker_sentiment_score` for the matching ticker.
    """
    api_key = os.environ.get("ALPHA_VANTAGE_KEY", "")
    if not api_key or not tickers:
        return []

    tickers = [t.upper() for t in tickers]
    cache_path = _cache_key(f"av_news_sent:{','.join(sorted(tickers))}:{limit}")
    cached = _cache_read(cache_path, _NEWS_TTL_SECONDS)
    if cached is not None:
        return [NewsItem.from_dict(d) for d in cached]

    try:
        resp = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "NEWS_SENTIMENT",
                "tickers": ",".join(tickers),
                "limit": limit,
                "apikey": api_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Alpha Vantage NEWS_SENTIMENT failed: %s", exc)
        return []

    feed = data.get("feed") if isinstance(data, dict) else None
    if not isinstance(feed, list):
        # AV soft-rate-limit response: {"Information": "..."}
        return []

    items: list[NewsItem] = []
    for art in feed:
        # AV time format: "20260425T133045"
        ts = art.get("time_published", "")
        try:
            dt = datetime.strptime(ts, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            dt = datetime.now(timezone.utc)

        # Per-ticker sentiment: pick the score for the first matching ticker.
        sentiment: Optional[float] = None
        for ts_block in art.get("ticker_sentiment", []):
            if (ts_block.get("ticker") or "").upper() in tickers:
                try:
                    sentiment = float(ts_block.get("ticker_sentiment_score", 0))
                except (ValueError, TypeError):
                    sentiment = None
                break

        items.append(NewsItem(
            date=dt,
            source=f"alpha_vantage:{art.get('source', 'unknown')}",
            title=(art.get("title") or "").strip(),
            url=art.get("url", ""),
            summary=(art.get("summary") or "")[:500],
            sentiment=sentiment,
            tickers_mentioned=tickers,
        ))

    _cache_write(cache_path, [i.to_dict() for i in items])
    logger.info("AV NEWS_SENTIMENT returned %d items for %s", len(items), tickers)
    return items


# ─────────────────────────────────────────────────────────────────────────────
#  Unified ticker-news aggregator (used by stock_picker)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_ticker_news(ticker: str, days: int = 14) -> list[NewsItem]:
    """
    Aggregate news for a single ticker across every available provider.

    Order: Google News (always), NewsAPI (if key), Finnhub (if key), FMP (if key).
    Deduplicates by URL. Sorts by date desc.
    """
    seen: set[str] = set()
    out: list[NewsItem] = []

    def _add(items: list[NewsItem]) -> None:
        for it in items:
            key = it.url or f"{it.source}:{it.title}"
            if key in seen:
                continue
            seen.add(key)
            out.append(it)

    _add(fetch_google_news(ticker, days=days))
    _add(fetch_newsapi(ticker, days=days))
    _add(fetch_finnhub_news(ticker, days=days))
    _add(fetch_fmp_news([ticker], limit=30))
    _add(fetch_alpha_vantage_news_sentiment([ticker], limit=20))

    out.sort(key=lambda x: x.date, reverse=True)
    return out
