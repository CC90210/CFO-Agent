"""
research/_data_integrity.py
---------------------------
Hard anti-hallucination guard for the research pipeline.

Why this exists (incident 2026-04-25):
    During a `python main.py picks` run, SEC EDGAR returned 503 and the
    fundamentals/price feeds dropped out. The active runtime filled the gap
    with hallucinated 2024 pricing from its training cutoff. CC caught it.
    A pick generated against fabricated prices is worse than no pick — it
    looks executable, so it gets executed.

Rule (matches CLAUDE.md / AGENTS.md / GEMINI.md "Data Integrity" section):
    No runtime — Claude, Gemini, Antigravity, Codex — may substitute training-
    memory data when a live feed fails. If the price/fundamentals feed for a
    ticker is unavailable, the script MUST raise DataFeedError and the agent
    MUST surface the failure verbatim, not improvise around it.

How callers use this:
    from research._data_integrity import (
        DataFeedError,
        require_live_price_data,
        require_live_fundamentals,
    )
    require_live_price_data(price_df, ticker)   # raises if empty/stale
    require_live_fundamentals(fund, ticker)     # raises if stub

The StockPickerAgent catches DataFeedError and aborts the pick run with the
canonical error string, so the same wording reaches CC across runtimes.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from research.fundamentals import Fundamentals

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Canonical error string — identical wording across runtimes per CC directive
# ─────────────────────────────────────────────────────────────────────────────

ERROR_BANNER = "API DOWN - CANNOT GENERATE PICK. Please fix the data feed."


class DataFeedError(RuntimeError):
    """
    Raised when a required live data feed is unavailable AND the runtime
    would otherwise be tempted to substitute training-memory data.

    Catch this at the top of any pick/research entry point. Do NOT catch
    it deep in the call stack and silently degrade — the whole point of
    raising is to refuse the pick rather than generate a fabricated one.
    """

    def __init__(self, ticker: str, source: str, detail: str = "") -> None:
        self.ticker = ticker.upper()
        self.source = source
        self.detail = detail
        msg = f"{ERROR_BANNER} [ticker={self.ticker}, source={source}]"
        if detail:
            msg += f" — {detail}"
        super().__init__(msg)


# ─────────────────────────────────────────────────────────────────────────────
#  Validators
# ─────────────────────────────────────────────────────────────────────────────

# Stale-data threshold: if the most recent close is older than this, assume
# the feed is broken (stocks should produce a close every trading day).
_PRICE_STALE_DAYS = 7


def require_live_price_data(df, ticker: str) -> None:
    """
    Raise DataFeedError if the OHLCV DataFrame is empty, missing Close,
    or the latest bar is older than _PRICE_STALE_DAYS.
    """
    if df is None or len(df) == 0 or "Close" not in df.columns:
        raise DataFeedError(
            ticker, "yfinance", "no price history returned (feed offline?)"
        )

    try:
        last_idx = df.index[-1]
        if hasattr(last_idx, "to_pydatetime"):
            last_ts = last_idx.to_pydatetime()
        else:
            last_ts = datetime.fromisoformat(str(last_idx))
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
    except Exception:
        # If we can't parse the timestamp at all, treat as broken.
        raise DataFeedError(
            ticker, "yfinance", "price-history index unparseable"
        )

    age = datetime.now(timezone.utc) - last_ts
    if age > timedelta(days=_PRICE_STALE_DAYS):
        raise DataFeedError(
            ticker,
            "yfinance",
            f"latest close is {age.days} days old (>{_PRICE_STALE_DAYS}d threshold)",
        )


def require_live_fundamentals(fund, ticker: str) -> None:
    """
    Raise DataFeedError if `fund` is None, a stub, or has no usable signal
    (no market_cap AND no pe_ratio AND no revenue_growth_yoy).
    """
    if fund is None:
        raise DataFeedError(ticker, "fundamentals", "all providers returned None")

    if getattr(fund, "data_source", "") == "stub":
        raise DataFeedError(
            ticker, "fundamentals", "all providers failed (yfinance/FMP/AV/Finnhub)"
        )

    has_signal = any([
        getattr(fund, "market_cap", None),
        getattr(fund, "pe_ratio", None),
        getattr(fund, "revenue_growth_yoy", None),
        getattr(fund, "ps_ratio", None),
    ])
    if not has_signal:
        raise DataFeedError(
            ticker,
            "fundamentals",
            "providers returned a record with zero usable metrics",
        )


def require_live_quote(quote, ticker: str) -> None:
    """Raise DataFeedError if a real-time quote is None or has zero price."""
    if quote is None or getattr(quote, "price", 0) <= 0:
        raise DataFeedError(ticker, "quote", "no live quote available")
