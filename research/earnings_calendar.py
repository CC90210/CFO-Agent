"""
research/earnings_calendar.py
------------------------------
Earnings dates, EPS/revenue surprise history, and post-earnings drift signals.

Data sources (in priority order):
1. yfinance — free, no key required. Provides .calendar (upcoming dates),
   .earnings_dates (historical with EPS estimate/actual), and .quarterly_earnings.
2. Finnhub free tier — 60 req/min, requires FINNHUB_KEY in .env. Provides a
   structured /calendar/earnings endpoint with richer metadata. Degrades
   gracefully if key is absent or quota is exceeded.

Academic backing:
  Post-Earnings Announcement Drift (PEAD): Ball & Brown (1968), Foster et al.
  (1984), Bernard & Thomas (1989). Stocks that beat estimates continue drifting
  upward for 60+ days; those that miss continue drifting down. The anomaly
  persists because most investors anchor on prior-quarter results and are slow
  to fully revise expectations. Tracking who beats consistently — and by how
  much — provides a systematic edge.

Caching:
  - Upcoming / live data: 15-minute TTL (options IV can reprice fast around
    earnings, so staleness matters here)
  - Historical surprise data: 24-hour TTL (stable, rarely changes)

Usage:
    from research.earnings_calendar import upcoming_earnings, surprise_score

CLI:
    python -m research.earnings_calendar NVDA
    python -m research.earnings_calendar AAPL --quarters 12
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests

try:
    import yfinance as yf
    _YFINANCE_AVAILABLE = True
except ImportError:
    _YFINANCE_AVAILABLE = False
    yf = None  # type: ignore[assignment]

try:
    import pandas as pd
    _PANDAS_AVAILABLE = True
except ImportError:
    _PANDAS_AVAILABLE = False
    pd = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Cache configuration
# ─────────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_LIVE_TTL = 900        # 15 minutes — for upcoming/live queries
_HISTORY_TTL = 86400   # 24 hours  — for historical surprise data

_FINNHUB_BASE = "https://finnhub.io/api/v1"


# ─────────────────────────────────────────────────────────────────────────────
#  Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class TickerNotFound(Exception):
    """Raised when yfinance returns no data for a given ticker symbol."""


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EarningsEvent:
    """
    A single earnings report — either upcoming (actual = None) or historical.

    Fields:
        ticker:             Stock symbol, e.g. "NVDA"
        company:            Full company name, e.g. "NVIDIA Corporation"
        report_date:        The date earnings were/will be reported (YYYY-MM-DD)
        when:               Timing relative to market session:
                              "before_open" — pre-market release
                              "after_close" — after-hours release
                              "unknown"     — timing not available
        period:             Fiscal period, e.g. "Q4 2025" or "2025-01-26"
        eps_estimate:       Analyst consensus EPS estimate at time of report (None if unavailable)
        eps_actual:         Reported EPS (None for upcoming events)
        revenue_estimate:   Analyst consensus revenue estimate in USD (None if unavailable)
        revenue_actual:     Reported revenue in USD (None for upcoming events)
        surprise_pct:       EPS surprise as a percentage:
                              (actual - estimate) / |estimate| * 100
                              None if actual or estimate is missing
    """
    ticker: str
    company: str
    report_date: str           # ISO date string "YYYY-MM-DD"
    when: str                  # "before_open" | "after_close" | "unknown"
    period: str
    eps_estimate: Optional[float] = None
    eps_actual: Optional[float] = None
    revenue_estimate: Optional[float] = None
    revenue_actual: Optional[float] = None
    surprise_pct: Optional[float] = None

    def is_upcoming(self) -> bool:
        """True when the event has not yet occurred (no actual EPS reported)."""
        return self.eps_actual is None

    def beat(self) -> Optional[bool]:
        """
        True = beat (positive surprise), False = miss, None = no data.
        A meet (0% surprise) is classified as False (no edge signal).
        """
        if self.surprise_pct is None:
            return None
        return self.surprise_pct > 0


# ─────────────────────────────────────────────────────────────────────────────
#  Internal cache helpers (mirror fundamentals.py pattern)
# ─────────────────────────────────────────────────────────────────────────────

def _cache_key(identifier: str) -> Path:
    h = hashlib.md5(identifier.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"earn_{h}.json"


def _cache_read(path: Path, ttl: int) -> Optional[dict]:
    if not path.exists():
        return None
    if time.time() - path.stat().st_mtime > ttl:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _cache_write(path: Path, data: dict) -> None:
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.warning("Cache write failed for %s: %s", path, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  yfinance helpers
# ─────────────────────────────────────────────────────────────────────────────

def _require_yfinance() -> None:
    if not _YFINANCE_AVAILABLE:
        raise ImportError("yfinance is not installed. Run: pip install yfinance")


def _yf_ticker(ticker: str) -> "yf.Ticker":  # type: ignore[name-defined]
    """Return a yfinance Ticker, raising TickerNotFound for unknown symbols."""
    _require_yfinance()
    t = yf.Ticker(ticker.upper())
    info = t.info
    # yfinance returns a minimal dict (sometimes just {"trailingPegRatio": None})
    # for unknown tickers. A real ticker always has quoteType or shortName.
    if not info or (info.get("quoteType") is None and info.get("shortName") is None):
        raise TickerNotFound(
            f"No data found for ticker '{ticker}'. "
            "Check the symbol and ensure it is listed on a US exchange."
        )
    return t


def _company_name(ticker: str) -> str:
    """Best-effort company name lookup; falls back to the ticker string."""
    try:
        info = yf.Ticker(ticker.upper()).info  # type: ignore[union-attr]
        return info.get("longName") or info.get("shortName") or ticker.upper()
    except Exception:
        return ticker.upper()


def _safe_float(value: object) -> Optional[float]:
    """Convert a value to float, returning None on failure or NaN."""
    if value is None:
        return None
    try:
        f = float(value)  # type: ignore[arg-type]
        return None if (f != f) else f  # NaN check
    except (TypeError, ValueError):
        return None


def _surprise_pct(actual: Optional[float], estimate: Optional[float]) -> Optional[float]:
    """
    EPS surprise as a percentage of the absolute estimate.

    Signed: positive = beat, negative = miss.
    Returns None when either value is unavailable.
    """
    if actual is None or estimate is None:
        return None
    if estimate == 0:
        return None
    return round((actual - estimate) / abs(estimate) * 100, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  Finnhub helpers
# ─────────────────────────────────────────────────────────────────────────────

def _finnhub_key() -> str:
    return os.environ.get("FINNHUB_KEY", "")


def _finnhub_get(endpoint: str, params: dict) -> Optional[dict]:
    """
    Make a Finnhub API call. Returns None (instead of raising) when:
      - FINNHUB_KEY is not set
      - Rate limit or HTTP error
      - JSON decode failure
    """
    key = _finnhub_key()
    if not key:
        return None

    params = {**params, "token": key}
    try:
        resp = requests.get(
            f"{_FINNHUB_BASE}{endpoint}",
            params=params,
            timeout=10,
        )
        if resp.status_code == 429:
            logger.warning("Finnhub rate limit hit — degrading to yfinance only")
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        logger.warning("Finnhub request failed (%s %s): %s", endpoint, params, exc)
        return None


def _finnhub_when(call_code: Optional[str]) -> str:
    """
    Map Finnhub's earningsCallCode values to our canonical 'when' strings.

    Finnhub uses: "bmo" (before market open), "amc" (after market close),
    "dmh" (during market hours), and sometimes empty string.
    """
    mapping = {
        "bmo": "before_open",
        "amc": "after_close",
        "dmh": "unknown",
    }
    return mapping.get((call_code or "").lower(), "unknown")


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def upcoming_earnings(
    tickers: Optional[list[str]] = None,
    days_ahead: int = 30,
) -> list[EarningsEvent]:
    """
    Return upcoming earnings events for the given tickers (or a curated
    watchlist if none are specified) within the next `days_ahead` days.

    Data pipeline:
    1. yfinance `.calendar` property — returns a small dict with
       "Earnings Date" as the most reliable field.
    2. Finnhub `/calendar/earnings` — enriches with timing (bmo/amc) and
       revenue estimates when FINNHUB_KEY is present.

    If `tickers` is None, a curated 30-ticker watchlist is used rather than
    attempting the full S&P 500 (which would exhaust rate limits). Pass an
    explicit list to control scope.

    Args:
        tickers:    List of ticker symbols. Defaults to a curated 30-stock list.
        days_ahead: How many calendar days forward to search.

    Returns:
        List of EarningsEvent, sorted ascending by report_date.

    Raises:
        TickerNotFound: When a specific ticker resolves to nothing in yfinance.
    """
    _require_yfinance()

    if tickers is None:
        # Curated 30-ticker watchlist representative of major cap/sector themes.
        # Intentionally capped to stay well within free-tier rate limits.
        tickers = [
            "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD",
            "AVGO", "NFLX", "CRM", "ORCL", "ADBE", "QCOM", "INTC",
            "JPM", "BAC", "GS", "V", "MA",
            "XOM", "CVX", "LMT", "RTX",
            "CRWD", "PANW", "ZS",
            "UNH", "JNJ", "LLY",
        ]

    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    # Build Finnhub calendar snapshot for the whole date range in one call
    # (more efficient than per-ticker lookups)
    finnhub_map: dict[str, dict] = {}
    fh_data = _finnhub_get(
        "/calendar/earnings",
        {
            "from": today.isoformat(),
            "to": cutoff.isoformat(),
        },
    )
    if fh_data and isinstance(fh_data.get("earningsCalendar"), list):
        for item in fh_data["earningsCalendar"]:
            sym = (item.get("symbol") or "").upper()
            if sym:
                finnhub_map[sym] = item

    events: list[EarningsEvent] = []

    for raw_ticker in tickers:
        ticker = raw_ticker.upper().strip()
        cache_path = _cache_key(f"upcoming:{ticker}")
        cached = _cache_read(cache_path, _LIVE_TTL)

        if cached and isinstance(cached.get("report_date"), str):
            # Validate cached date is still within window before using it
            try:
                rd = date.fromisoformat(cached["report_date"])
                if today <= rd <= cutoff:
                    events.append(EarningsEvent(**cached))
                    continue
                elif rd < today:
                    # Stale — fall through to re-fetch
                    pass
                else:
                    # Beyond window — skip (still cache for later queries)
                    continue
            except (ValueError, TypeError):
                pass

        try:
            t = yf.Ticker(ticker)  # type: ignore[union-attr]
            cal = t.calendar
        except Exception as exc:
            logger.debug("yfinance calendar failed for %s: %s", ticker, exc)
            continue

        if cal is None:
            continue

        # yfinance returns calendar as a dict or DataFrame depending on version.
        report_date_raw: Optional[str] = None

        if _PANDAS_AVAILABLE and hasattr(cal, "columns"):
            # DataFrame shape — transpose to dict
            try:
                cal_dict = cal.iloc[:, 0].to_dict() if not cal.empty else {}
                earn_dates = cal_dict.get("Earnings Date")
                if earn_dates is not None:
                    if hasattr(earn_dates, "date"):
                        report_date_raw = earn_dates.date().isoformat()
                    else:
                        report_date_raw = str(earn_dates)[:10]
            except Exception:
                pass
        elif isinstance(cal, dict):
            earn_val = cal.get("Earnings Date")
            if earn_val is not None:
                if isinstance(earn_val, list) and earn_val:
                    earn_val = earn_val[0]
                if hasattr(earn_val, "date"):
                    report_date_raw = earn_val.date().isoformat()
                else:
                    report_date_raw = str(earn_val)[:10]

        if report_date_raw is None:
            continue

        try:
            rd = date.fromisoformat(report_date_raw)
        except ValueError:
            continue

        if not (today <= rd <= cutoff):
            continue

        # Resolve timing and estimates — prefer Finnhub when available
        fh = finnhub_map.get(ticker, {})
        when = _finnhub_when(fh.get("hour"))

        eps_est: Optional[float] = None
        rev_est: Optional[float] = None
        if fh:
            eps_est = _safe_float(fh.get("epsEstimate"))
            rev_est = _safe_float(fh.get("revenueEstimate"))
        else:
            # Fall back to yfinance calendar estimates
            if isinstance(cal, dict):
                eps_est = _safe_float(cal.get("EPS Estimate"))
                rev_est = _safe_float(cal.get("Revenue Estimate"))

        company = fh.get("name") or _company_name(ticker)

        ev = EarningsEvent(
            ticker=ticker,
            company=company,
            report_date=report_date_raw,
            when=when,
            period=fh.get("period") or f"Q{(rd.month - 1) // 3 + 1} {rd.year}",
            eps_estimate=eps_est,
            revenue_estimate=rev_est,
        )

        _cache_write(cache_path, ev.__dict__)
        events.append(ev)

    events.sort(key=lambda e: e.report_date)
    return events


def earnings_history(ticker: str, quarters: int = 8) -> list[EarningsEvent]:
    """
    Return historical earnings reports with EPS estimates, actuals, and
    calculated surprise percentages.

    Data pipeline:
    1. yfinance `.earnings_dates` — returns a DataFrame indexed by date with
       columns "EPS Estimate", "Reported EPS", "Surprise(%)" going back ~4 years.
    2. Finnhub `/stock/earnings` — fallback/enrichment with revenue figures
       when FINNHUB_KEY is present.

    The PEAD literature (Bernard & Thomas, 1989) shows that 8–12 quarters of
    history gives a reliable read on whether a company is a consistent beater
    vs. a miss machine. 8 quarters is the default.

    Args:
        ticker:   Stock symbol.
        quarters: Number of historical quarters to return (most recent first).

    Returns:
        List of EarningsEvent, sorted descending (most recent first).

    Raises:
        TickerNotFound: When ticker resolves to nothing in yfinance.
    """
    ticker = ticker.upper().strip()

    cache_path = _cache_key(f"history:{ticker}:{quarters}")
    cached = _cache_read(cache_path, _HISTORY_TTL)
    if cached and isinstance(cached.get("events"), list):
        try:
            return [EarningsEvent(**e) for e in cached["events"]]
        except Exception:
            pass

    t = _yf_ticker(ticker)
    company = _company_name(ticker)

    events: list[EarningsEvent] = []

    # Primary: yfinance earnings_dates DataFrame
    if _PANDAS_AVAILABLE:
        try:
            earn_df = t.earnings_dates
            if earn_df is not None and not earn_df.empty:
                # Limit to requested quarters. The DF is sorted most-recent first.
                # Only include rows where Reported EPS is available (historical).
                historical = earn_df[earn_df["Reported EPS"].notna()].head(quarters)

                for idx, row in historical.iterrows():
                    # idx is a Timestamp
                    try:
                        rd = idx.date() if hasattr(idx, "date") else date.fromisoformat(str(idx)[:10])
                    except Exception:
                        continue

                    eps_est = _safe_float(row.get("EPS Estimate"))
                    eps_act = _safe_float(row.get("Reported EPS"))
                    spct: Optional[float] = None

                    # yfinance provides "Surprise(%)" directly but it can be NaN.
                    raw_spct = row.get("Surprise(%)")
                    if raw_spct is not None:
                        spct = _safe_float(raw_spct)
                    if spct is None:
                        spct = _surprise_pct(eps_act, eps_est)

                    events.append(EarningsEvent(
                        ticker=ticker,
                        company=company,
                        report_date=rd.isoformat(),
                        when="unknown",   # yfinance doesn't provide this in earnings_dates
                        period=f"Q{(rd.month - 1) // 3 + 1} {rd.year}",
                        eps_estimate=eps_est,
                        eps_actual=eps_act,
                        surprise_pct=spct,
                    ))
        except Exception as exc:
            logger.warning("yfinance earnings_dates failed for %s: %s", ticker, exc)

    # Finnhub enrichment / fallback: adds revenue figures and better period labels
    fh_data = _finnhub_get("/stock/earnings", {"symbol": ticker, "limit": quarters})
    if fh_data and isinstance(fh_data, list):
        # Build a map by date so we can enrich existing events
        fh_by_date: dict[str, dict] = {}
        for item in fh_data:
            period_str = item.get("period") or ""
            fh_by_date[period_str[:10]] = item  # YYYY-MM-DD key

        if not events:
            # Full fallback to Finnhub
            for item in fh_data[:quarters]:
                period_str = (item.get("period") or "")[:10]
                try:
                    rd = date.fromisoformat(period_str)
                except ValueError:
                    continue

                eps_est = _safe_float(item.get("estimate"))
                eps_act = _safe_float(item.get("actual"))
                events.append(EarningsEvent(
                    ticker=ticker,
                    company=company,
                    report_date=period_str,
                    when="unknown",
                    period=item.get("period") or period_str,
                    eps_estimate=eps_est,
                    eps_actual=eps_act,
                    surprise_pct=_surprise_pct(eps_act, eps_est),
                    revenue_estimate=_safe_float(item.get("revenueEstimate")),
                    revenue_actual=_safe_float(item.get("revenueActual")),
                ))
        else:
            # Enrich yfinance events with revenue from Finnhub
            for ev in events:
                fh = fh_by_date.get(ev.report_date, {})
                if fh:
                    if ev.revenue_estimate is None:
                        ev.revenue_estimate = _safe_float(fh.get("revenueEstimate"))
                    if ev.revenue_actual is None:
                        ev.revenue_actual = _safe_float(fh.get("revenueActual"))
                    if ev.period == f"Q{(date.fromisoformat(ev.report_date).month - 1) // 3 + 1} {date.fromisoformat(ev.report_date).year}":
                        fh_period = fh.get("period")
                        if fh_period:
                            ev.period = fh_period

    events.sort(key=lambda e: e.report_date, reverse=True)

    _cache_write(cache_path, {"events": [e.__dict__ for e in events]})
    return events


def surprise_score(ticker: str) -> dict:
    """
    Summarize a ticker's earnings surprise track record over 8 quarters.

    Returns a dict:
        beats:           Number of quarters with positive EPS surprise
        misses:          Number of quarters with negative EPS surprise
        meets:           Number of quarters with zero surprise
        avg_surprise_pct: Mean EPS surprise percentage (signed)
        consistency:     beats / total reported (beat rate as a fraction)
        signal:          One of:
                           "high_quality"  — consistent beater: consistency >= 0.75
                                            AND avg_surprise > 3%
                           "unreliable"    — consistency < 0.40 (coin-flip or worse)
                           "neutral"       — neither strong nor weak
        data_available:  How many quarters had both estimate and actual (denominator)

    Academic basis:
        PEAD (Post-Earnings Announcement Drift): Stocks that beat estimates
        by > 3% on average, and do so consistently (75%+ of the time), tend
        to exhibit continued positive drift for 30–90 days post-announcement.
        The reverse is true for consistent missers. (Bernard & Thomas, 1989;
        Livnat & Mendenhall, 2006.)

    Args:
        ticker: Stock symbol.

    Returns:
        Dict as described above.
    """
    history = earnings_history(ticker, quarters=8)

    beats = 0
    misses = 0
    meets = 0
    surprise_values: list[float] = []

    for ev in history:
        if ev.surprise_pct is None:
            continue
        surprise_values.append(ev.surprise_pct)
        if ev.surprise_pct > 0.5:       # > 0.5% = beat (avoids floating-point noise)
            beats += 1
        elif ev.surprise_pct < -0.5:    # < -0.5% = miss
            misses += 1
        else:
            meets += 1

    total = beats + misses + meets
    avg_surprise = round(sum(surprise_values) / len(surprise_values), 2) if surprise_values else 0.0
    consistency = round(beats / total, 3) if total > 0 else 0.0

    if consistency >= 0.75 and avg_surprise > 3.0:
        signal = "high_quality"
    elif consistency < 0.40 and total >= 4:
        signal = "unreliable"
    else:
        signal = "neutral"

    return {
        "ticker": ticker.upper(),
        "beats": beats,
        "misses": misses,
        "meets": meets,
        "avg_surprise_pct": avg_surprise,
        "consistency": consistency,
        "signal": signal,
        "data_available": total,
    }


def days_to_next_earnings(ticker: str) -> Optional[int]:
    """
    Return the number of calendar days until the next earnings report.

    Practical use: Exit open positions or hedge before earnings when IV
    expansion is expected. A rule of thumb — options implied volatility
    (IV) typically spikes 3–10 days before earnings and collapses immediately
    after (IV crush). Positions should be managed before entering the
    high-IV window.

    Returns:
        Number of calendar days (0 = today, negative = already past).
        None if no upcoming earnings date is found.

    Args:
        ticker: Stock symbol.
    """
    ticker = ticker.upper().strip()

    try:
        t = _yf_ticker(ticker)
        cal = t.calendar
    except TickerNotFound:
        raise
    except Exception as exc:
        logger.warning("days_to_next_earnings: yfinance calendar failed for %s: %s", ticker, exc)
        return None

    if cal is None:
        return None

    report_date_raw: Optional[str] = None

    if _PANDAS_AVAILABLE and hasattr(cal, "columns"):
        try:
            cal_dict = cal.iloc[:, 0].to_dict() if not cal.empty else {}
            earn_dates = cal_dict.get("Earnings Date")
            if earn_dates is not None:
                if hasattr(earn_dates, "date"):
                    report_date_raw = earn_dates.date().isoformat()
                else:
                    report_date_raw = str(earn_dates)[:10]
        except Exception:
            pass
    elif isinstance(cal, dict):
        earn_val = cal.get("Earnings Date")
        if earn_val is not None:
            if isinstance(earn_val, list) and earn_val:
                earn_val = earn_val[0]
            if hasattr(earn_val, "date"):
                report_date_raw = earn_val.date().isoformat()
            else:
                report_date_raw = str(earn_val)[:10]

    if report_date_raw is None:
        return None

    try:
        rd = date.fromisoformat(report_date_raw)
    except ValueError:
        return None

    return (rd - date.today()).days


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def _cli() -> None:
    """
    CLI usage:
        python -m research.earnings_calendar NVDA
        python -m research.earnings_calendar AAPL --quarters 12
        python -m research.earnings_calendar --upcoming --days 14
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Atlas Earnings Calendar — surprise history + upcoming dates",
    )
    parser.add_argument(
        "ticker",
        nargs="?",
        default=None,
        help="Ticker symbol (e.g. NVDA). Omit to show upcoming earnings for watchlist.",
    )
    parser.add_argument(
        "--quarters",
        type=int,
        default=8,
        help="Number of historical quarters to display (default: 8).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Days ahead to scan for upcoming earnings (default: 30).",
    )
    args = parser.parse_args()

    # Configure basic logging for CLI output
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    if args.ticker:
        ticker = args.ticker.upper()
        print(f"\n{'='*60}")
        print(f"  EARNINGS CALENDAR — {ticker}")
        print(f"{'='*60}\n")

        # Upcoming
        dtne = days_to_next_earnings(ticker)
        if dtne is not None:
            if dtne < 0:
                print(f"Next earnings: {abs(dtne)} days ago (already reported)")
            elif dtne == 0:
                print("Next earnings: TODAY")
            else:
                next_date = (date.today() + timedelta(days=dtne)).isoformat()
                print(f"Next earnings: {next_date} ({dtne} days)")
        else:
            print("Next earnings: date not available")

        # Surprise score
        print()
        sc = surprise_score(ticker)
        print(f"Surprise track record ({sc['data_available']} quarters with data):")
        print(f"  Beats:           {sc['beats']}")
        print(f"  Misses:          {sc['misses']}")
        print(f"  Meets:           {sc['meets']}")
        print(f"  Avg surprise:    {sc['avg_surprise_pct']:+.2f}%")
        print(f"  Beat rate:       {sc['consistency']*100:.1f}%")
        print(f"  Signal:          {sc['signal'].upper()}")

        # History
        print(f"\nLast {args.quarters} quarters:\n")
        history = earnings_history(ticker, quarters=args.quarters)
        if not history:
            print("  No historical earnings data available.")
        else:
            header = f"  {'Date':<12} {'Period':<12} {'EPS Est':>9} {'EPS Act':>9} {'Surprise':>10} {'Rev Est (B)':>12} {'Rev Act (B)':>12}"
            print(header)
            print("  " + "-" * (len(header) - 2))
            for ev in history:
                eps_est_str = f"{ev.eps_estimate:>9.3f}" if ev.eps_estimate is not None else f"{'n/a':>9}"
                eps_act_str = f"{ev.eps_actual:>9.3f}" if ev.eps_actual is not None else f"{'n/a':>9}"
                surp_str = f"{ev.surprise_pct:>+9.2f}%" if ev.surprise_pct is not None else f"{'n/a':>10}"
                rev_est_str = f"{ev.revenue_estimate/1e9:>12.2f}" if ev.revenue_estimate else f"{'n/a':>12}"
                rev_act_str = f"{ev.revenue_actual/1e9:>12.2f}" if ev.revenue_actual else f"{'n/a':>12}"
                print(f"  {ev.report_date:<12} {ev.period:<12} {eps_est_str} {eps_act_str} {surp_str} {rev_est_str} {rev_act_str}")

    else:
        # Upcoming watchlist
        print(f"\n{'='*60}")
        print(f"  UPCOMING EARNINGS — next {args.days} days")
        print(f"{'='*60}\n")

        upcoming = upcoming_earnings(days_ahead=args.days)
        if not upcoming:
            print("  No upcoming earnings found in the watchlist for this window.")
        else:
            print(f"  {'Ticker':<8} {'Date':<12} {'When':<14} {'Company':<35} {'EPS Est':>9}")
            print("  " + "-" * 85)
            for ev in upcoming:
                eps_str = f"{ev.eps_estimate:>9.3f}" if ev.eps_estimate is not None else f"{'n/a':>9}"
                print(f"  {ev.ticker:<8} {ev.report_date:<12} {ev.when:<14} {ev.company[:35]:<35} {eps_str}")


if __name__ == "__main__":
    _cli()
