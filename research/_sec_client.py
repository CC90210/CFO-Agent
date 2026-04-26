"""
research/_sec_client.py
-----------------------
Centralized HTTP client for the SEC EDGAR family of APIs (data.sec.gov,
www.sec.gov, efts.sec.gov).

Why this module exists:
- SEC enforces a strict identification policy. The User-Agent header MUST
  identify a real party with a real, monitored email. Generic strings
  (`python-requests`, `Atlas/1.0`) get auto-blocked with HTTP 403/503 from
  CloudFront. SEC public guidance:
  https://www.sec.gov/os/accessing-edgar-data
- SEC enforces 10 requests/second. Bursting beyond that returns 429.
- Transient 503 from CloudFront is common during high-load windows; retries
  with exponential backoff resolve almost all of them.

This module:
- Holds the canonical User-Agent string with CC's real contact.
- Enforces a 10 req/s ceiling via a process-wide token bucket.
- Wraps every call in a tenacity retry loop (3 attempts, exponential backoff,
  jittered) for 429/503/connection errors.
- Returns None on hard failure so callers can degrade gracefully without
  crashing the research pipeline.

Used by:
- research/institutional_tracking.py (13F filings)
- research/news_ingest.py (8-K, 10-K, 10-Q, ticker→CIK lookup)
- any future module that needs SEC data
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Identification — SEC requires a real, monitored email here.
#  CC's real Google Workspace inbox is conaugh@oasisai.work.
# ─────────────────────────────────────────────────────────────────────────────

USER_AGENT = "Atlas CFO Agent (Conaugh McKenna) conaugh@oasisai.work"

_DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}

# data.sec.gov requires the Host header to match exactly.
_DATA_HEADERS = {**_DEFAULT_HEADERS, "Host": "data.sec.gov"}


# ─────────────────────────────────────────────────────────────────────────────
#  Token-bucket rate limiter (process-wide). Caps at 10 req/s.
# ─────────────────────────────────────────────────────────────────────────────

class _RateLimiter:
    """Simple sliding-window limiter shared across threads."""

    def __init__(self, max_per_second: int = 9):
        # Use 9, not 10, to leave a safety margin for clock drift / SEC's own
        # counter granularity. SEC has historically blocked bursts at 11+/sec.
        self._min_interval = 1.0 / max_per_second
        self._lock = threading.Lock()
        self._last_call: float = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_call = time.monotonic()


_LIMITER = _RateLimiter(max_per_second=9)


# ─────────────────────────────────────────────────────────────────────────────
#  Custom exceptions
# ─────────────────────────────────────────────────────────────────────────────

class SecRetryableError(requests.RequestException):
    """Marker for errors we want tenacity to retry on (429, 503, connection)."""


def _classify(resp: requests.Response) -> Optional[Exception]:
    """Return a retry-eligible exception if status warrants retry, else None."""
    if resp.status_code in (429, 502, 503, 504):
        return SecRetryableError(
            f"SEC returned {resp.status_code} for {resp.url}", response=resp
        )
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  The retry-wrapped GET
# ─────────────────────────────────────────────────────────────────────────────

@retry(
    retry=retry_if_exception_type((SecRetryableError, requests.ConnectionError, requests.Timeout)),
    stop=stop_after_attempt(4),
    wait=wait_exponential_jitter(initial=1.0, max=15.0, jitter=2.0),
    reraise=False,
)
def _get_with_retry(url: str, headers: dict, timeout: int) -> requests.Response:
    _LIMITER.wait()
    resp = requests.get(url, headers=headers, timeout=timeout)
    err = _classify(resp)
    if err is not None:
        logger.warning(
            "SEC %d on %s — retrying with backoff", resp.status_code, url
        )
        raise err
    resp.raise_for_status()
    return resp


def get(
    url: str,
    *,
    headers: Optional[dict] = None,
    timeout: int = 20,
    use_data_host: bool = False,
) -> Optional[requests.Response]:
    """
    Rate-limited, retry-wrapped GET against an SEC endpoint.

    Args:
        url: Full SEC URL.
        headers: Optional override headers. Falls back to defaults that include
            the SEC-required User-Agent.
        timeout: Per-request timeout in seconds.
        use_data_host: If True, sets `Host: data.sec.gov` for data.sec.gov calls.

    Returns:
        Response on success, None if all retries are exhausted or the response
        is a non-retryable HTTP error.
    """
    if headers is None:
        headers = _DATA_HEADERS if use_data_host else _DEFAULT_HEADERS

    try:
        return _get_with_retry(url, headers=headers, timeout=timeout)
    except (SecRetryableError, requests.ConnectionError, requests.Timeout) as exc:
        logger.warning("SEC GET exhausted retries for %s: %s", url, exc)
        return None
    except requests.HTTPError as exc:
        # 4xx other than 429 — auth, 404, etc. Not retried.
        logger.warning("SEC GET hard-failed for %s: %s", url, exc)
        return None
    except requests.RequestException as exc:
        logger.warning("SEC GET request error for %s: %s", url, exc)
        return None
