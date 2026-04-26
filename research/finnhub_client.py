"""
research/finnhub_client.py
--------------------------
Finnhub.io client for real-time quotes, company profile, news, and metrics.

Why Finnhub:
- Free tier: 60 req/min, no daily cap.
- Real-time US quotes (delayed for international).
- Company news endpoint complements NewsAPI / FMP / Google News for source
  redundancy after the EDGAR 503 incident (2026-04-25).
- Basic financials provide a sanity-check layer over yfinance/FMP.

All endpoints return None on failure so callers degrade gracefully — the
anti-hallucination guard in research/_data_integrity.py decides whether the
StockPickerAgent should refuse to generate a pick.

Cache: 1 hour for quotes/news, 24 hours for company profile/financials.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

# Load .env so callers that don't import config.settings still see provider keys.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)

_BASE = "https://finnhub.io/api/v1"
_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "finnhub"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_QUOTE_TTL = 3600        # 1h — for picks horizon, this is fine
_NEWS_TTL = 3600         # 1h
_PROFILE_TTL = 86400     # 24h — slow-moving metadata
_FINANCIALS_TTL = 86400  # 24h


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _api_key() -> Optional[str]:
    key = os.environ.get("FINNHUB_KEY", "").strip()
    return key or None


def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"finnhub_{h}.json"


def _cache_read(path: Path, ttl: int) -> Optional[dict | list]:
    if not path.exists():
        return None
    if time.time() - path.stat().st_mtime > ttl:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _cache_write(path: Path, data: dict | list) -> None:
    try:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.warning("Finnhub cache write failed for %s: %s", path, exc)


@retry(
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1.0, max=10.0, jitter=1.0),
    reraise=False,
)
def _get_with_retry(url: str, params: dict, timeout: int) -> requests.Response:
    resp = requests.get(url, params=params, timeout=timeout)
    if resp.status_code == 429:
        # Finnhub free tier — 60/min. Surface as retryable timeout so tenacity backs off.
        raise requests.Timeout(f"Finnhub 429 rate limit on {url}")
    resp.raise_for_status()
    return resp


def _request(endpoint: str, params: Optional[dict] = None, timeout: int = 10) -> Optional[dict | list]:
    key = _api_key()
    if not key:
        logger.debug("FINNHUB_KEY not set — Finnhub call skipped: %s", endpoint)
        return None
    p = dict(params or {})
    p["token"] = key
    try:
        resp = _get_with_retry(f"{_BASE}{endpoint}", params=p, timeout=timeout)
    except requests.RequestException as exc:
        logger.warning("Finnhub %s failed: %s", endpoint, exc)
        return None
    try:
        return resp.json()
    except ValueError as exc:
        logger.warning("Finnhub %s returned non-JSON: %s", endpoint, exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Quote:
    ticker: str
    price: float
    change: float
    change_pct: float
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: str
    source: str = "finnhub"


def quote(ticker: str) -> Optional[Quote]:
    """
    Real-time quote for a US-listed ticker.
    Returns None if the API key is missing or the call fails.
    """
    cache_path = _cache_path(f"quote:{ticker.upper()}")
    cached = _cache_read(cache_path, _QUOTE_TTL)
    if cached is None:
        data = _request("/quote", {"symbol": ticker.upper()})
        if not data or not isinstance(data, dict):
            return None
        # Finnhub quote shape: {c:current, d:change, dp:change_pct, h:high, l:low, o:open, pc:prev_close, t:unix_ts}
        if data.get("c") in (None, 0):
            return None
        _cache_write(cache_path, data)
        cached = data

    try:
        ts = datetime.fromtimestamp(int(cached.get("t", 0) or 0), tz=timezone.utc).isoformat()
    except (ValueError, OSError):
        ts = datetime.now(timezone.utc).isoformat()

    return Quote(
        ticker=ticker.upper(),
        price=float(cached.get("c") or 0),
        change=float(cached.get("d") or 0),
        change_pct=float(cached.get("dp") or 0),
        high=float(cached.get("h") or 0),
        low=float(cached.get("l") or 0),
        open=float(cached.get("o") or 0),
        previous_close=float(cached.get("pc") or 0),
        timestamp=ts,
    )


def company_profile(ticker: str) -> Optional[dict]:
    """Company profile2 endpoint — sector, industry, market cap, exchange, IPO date."""
    cache_path = _cache_path(f"profile:{ticker.upper()}")
    cached = _cache_read(cache_path, _PROFILE_TTL)
    if cached is not None and isinstance(cached, dict):
        return cached

    data = _request("/stock/profile2", {"symbol": ticker.upper()})
    if not data or not isinstance(data, dict) or not data.get("name"):
        return None
    _cache_write(cache_path, data)
    return data


def basic_financials(ticker: str) -> Optional[dict]:
    """
    Basic financials — P/E, P/B, ROE, margins, beta, etc.
    Used as a sanity-check overlay over yfinance.
    """
    cache_path = _cache_path(f"basicfin:{ticker.upper()}")
    cached = _cache_read(cache_path, _FINANCIALS_TTL)
    if cached is not None and isinstance(cached, dict):
        return cached

    data = _request("/stock/metric", {"symbol": ticker.upper(), "metric": "all"})
    if not data or not isinstance(data, dict) or not data.get("metric"):
        return None
    _cache_write(cache_path, data)
    return data


def company_news(ticker: str, days: int = 14) -> list[dict]:
    """
    Recent news articles for a ticker.

    Returns raw Finnhub article dicts (caller is expected to map to NewsItem
    via news_ingest._finnhub_to_newsitem).
    """
    cache_path = _cache_path(f"news:{ticker.upper()}:{days}")
    cached = _cache_read(cache_path, _NEWS_TTL)
    if cached is not None and isinstance(cached, list):
        return cached

    today = datetime.now(timezone.utc).date()
    start = (today - timedelta(days=days)).isoformat()
    data = _request("/company-news", {
        "symbol": ticker.upper(),
        "from": start,
        "to": today.isoformat(),
    })
    if not isinstance(data, list):
        return []
    _cache_write(cache_path, data)
    return data


def is_available() -> bool:
    """Cheap availability check — used by health probes."""
    return _api_key() is not None
