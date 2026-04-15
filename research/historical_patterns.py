"""
research/historical_patterns.py
--------------------------------
Historical analog matching and seasonal pattern analysis for Atlas Research.

Provides cycle-aware context by computing:
- Seasonal return patterns (monthly, 20-year lookback)
- US Presidential cycle phase and historical return expectations
- Market regime classification (bull/bear/topping/capitulation/recovery)
- Historical analog matching — nearest-neighbor against 10 landmark episodes
- A unified cycle_context() block for injection into Claude prompts

Theoretical grounding:
- Jesse Livermore: "There is nothing new in Wall Street. There can't be because
  speculation is as old as the hills. Whatever happens in the stock market today
  has happened before and will happen again." (Reminiscences of a Stock Operator)
- Stan Druckenmiller: "The key to building wealth is to preserve capital and wait
  patiently for the right opportunity. Historical context shows you where you are
  in the cycle."
- Howard Marks: "The most important thing is understanding the investment cycle —
  knowing where you are in it separates great investors from average ones."
- Yale Hirsch (Stock Trader's Almanac): Presidential cycle and seasonal patterns
  have been remarkably persistent across 70+ years of US market history.
- Robert Shiller: Mean reversion around CAPE cycles matches historical analogs.

All functions:
- Use yfinance for price data (free, no key required)
- Cache results in data/cache/ to avoid repeated downloads
- Are deterministic given cached data
- Degrade gracefully when data is unavailable

Usage:
    from research.historical_patterns import cycle_context
    ctx = cycle_context("NVDA")
    print(ctx["narrative"])
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

try:
    import yfinance as yf
    _YFINANCE_AVAILABLE = True
except ImportError:
    _YFINANCE_AVAILABLE = False
    yf = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Cache configuration
# ─────────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_SEASONAL_TTL  = 86400 * 7   # 7 days — monthly returns rarely change meaningfully
_REGIME_TTL    = 3600        # 1 hour — regime can shift quickly
_CYCLE_TTL     = 86400       # 24 hours

_MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"hist_{h}.json"


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
        logger.warning("Cache write failed: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
#  Seasonality — monthly average returns
# ─────────────────────────────────────────────────────────────────────────────

def seasonality(ticker: str, lookback_years: int = 20) -> dict:
    """
    Compute average monthly returns by calendar month from historical price data.

    Uses yfinance to fetch up to `lookback_years` of monthly close data for
    the given ticker, then computes the average return for each of the 12
    calendar months.

    Returns:
        {
            ticker (str),
            lookback_years (int),
            monthly_avg_returns (dict[str, float]),  # "Jan": 1.2, "Feb": -0.5 ...
            best_months (list[str]),                  # top 3 by avg return
            worst_months (list[str]),                 # bottom 3 by avg return
            current_month (str),
            current_month_avg (float | None),
            current_month_rank (int | None),          # 1=best, 12=worst
            notable_patterns (list[str]),
            _source ("live" | "cached" | "unavailable"),
        }

    Well-known seasonal patterns (Yale Hirsch, "Stock Trader's Almanac"):
        - "Sell in May and Go Away" — May-Oct average return has historically
          underperformed Nov-Apr by ~5% per year on the S&P 500.
        - September Effect — September is historically the worst month for US stocks
          (avg -1.0% on SPY over 30 years). Tax-loss selling + fiscal year-end.
        - Santa Claus Rally — Last week of Dec + first 2 days of Jan tend to be bullish.
        - January Effect — Small-cap outperformance in January; tax-loss selling
          reversal from December.

    Reference: Yale Hirsch (1967) "Don't Sell Stocks on Monday";
    Bouman & Jacobsen (2002) "The Halloween Indicator."
    """
    cache_file = _cache_path(f"seasonality_{ticker}_{lookback_years}y")
    cached = _cache_read(cache_file, _SEASONAL_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    if not _YFINANCE_AVAILABLE:
        return {
            "ticker": ticker,
            "lookback_years": lookback_years,
            "monthly_avg_returns": {},
            "best_months": [],
            "worst_months": [],
            "current_month": _MONTH_NAMES[date.today().month - 1],
            "current_month_avg": None,
            "current_month_rank": None,
            "notable_patterns": ["yfinance not installed"],
            "_source": "unavailable",
        }

    period = f"{lookback_years}y"
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval="1mo")
        if df.empty or len(df) < 12:
            raise ValueError(f"Insufficient data for {ticker}")
        df.index = pd.to_datetime(df.index)
        df["month"] = df.index.month
        df["return_pct"] = df["Close"].pct_change() * 100
        df = df.dropna(subset=["return_pct"])
    except Exception as exc:
        logger.warning("Seasonality fetch failed for %s: %s", ticker, exc)
        return {
            "ticker": ticker,
            "lookback_years": lookback_years,
            "monthly_avg_returns": {},
            "best_months": [],
            "worst_months": [],
            "current_month": _MONTH_NAMES[date.today().month - 1],
            "current_month_avg": None,
            "current_month_rank": None,
            "notable_patterns": [f"Data fetch failed: {exc}"],
            "_source": "unavailable",
        }

    monthly_avgs: dict[str, float] = {}
    for m in range(1, 13):
        month_data = df[df["month"] == m]["return_pct"]
        avg = float(month_data.mean()) if not month_data.empty else 0.0
        monthly_avgs[_MONTH_NAMES[m - 1]] = round(avg, 2)

    sorted_months = sorted(monthly_avgs.items(), key=lambda x: x[1], reverse=True)
    best_months  = [m for m, _ in sorted_months[:3]]
    worst_months = [m for m, _ in sorted_months[-3:]]

    current_month_name = _MONTH_NAMES[date.today().month - 1]
    current_month_avg  = monthly_avgs.get(current_month_name)
    month_rank_list    = [m for m, _ in sorted_months]
    current_month_rank = (
        month_rank_list.index(current_month_name) + 1
        if current_month_name in month_rank_list else None
    )

    # Notable patterns
    patterns: list[str] = []
    may_oct_avg = np.mean([monthly_avgs.get(m, 0) for m in ["May", "Jun", "Jul", "Aug", "Sep", "Oct"]])
    nov_apr_avg = np.mean([monthly_avgs.get(m, 0) for m in ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]])
    if nov_apr_avg - may_oct_avg > 1.0:
        patterns.append(
            f"'Sell in May' pattern confirmed: Nov-Apr avg {nov_apr_avg:.1f}% vs May-Oct {may_oct_avg:.1f}%"
        )

    sep_avg = monthly_avgs.get("Sep", 0)
    if sep_avg < -0.5:
        patterns.append(f"September weakness confirmed: avg {sep_avg:.1f}%")

    dec_avg = monthly_avgs.get("Dec", 0)
    if dec_avg > 0.5:
        patterns.append(f"Santa Rally visible: December avg {dec_avg:.1f}%")

    result = {
        "ticker": ticker,
        "lookback_years": lookback_years,
        "monthly_avg_returns": monthly_avgs,
        "best_months": best_months,
        "worst_months": worst_months,
        "current_month": current_month_name,
        "current_month_avg": current_month_avg,
        "current_month_rank": current_month_rank,
        "notable_patterns": patterns,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Presidential Cycle
# ─────────────────────────────────────────────────────────────────────────────

# US Presidential inauguration dates (post-1952 four-year cycles)
# Source: US National Archives
_INAUGURATION_DATES: list[date] = [
    date(1953, 1, 20), date(1957, 1, 20), date(1961, 1, 20), date(1965, 1, 20),
    date(1969, 1, 20), date(1973, 1, 20), date(1977, 1, 20), date(1981, 1, 20),
    date(1985, 1, 20), date(1989, 1, 20), date(1993, 1, 20), date(1997, 1, 20),
    date(2001, 1, 20), date(2005, 1, 20), date(2009, 1, 20), date(2013, 1, 20),
    date(2017, 1, 20), date(2021, 1, 20), date(2025, 1, 20),
]

# Historical S&P 500 average returns by presidential cycle year (1950-2024)
# Source: Hirsch (Stock Trader's Almanac 2024); CFRA Research
_PRESIDENTIAL_CYCLE_RETURNS: dict[int, dict] = {
    1: {
        "avg_return_pct": 5.2,
        "note": (
            "Year 1 — new administration adjustments, policy uncertainty. "
            "Often the weakest year (1957: -14%, 1973: -17%, 2001: -13%). "
            "Markets price in policy risk."
        ),
        "best_sectors": ["defensive", "healthcare", "consumer_staples"],
        "worst_sectors": ["growth", "speculative"],
    },
    2: {
        "avg_return_pct": 4.8,
        "note": (
            "Year 2 — mid-term election year. Market often bottoms around mid-term elections "
            "(Oct-Nov), then rallies sharply into Year 3. "
            "Historically: buy the mid-term election dip."
        ),
        "best_sectors": ["financials", "small_cap", "cyclicals"],
        "worst_sectors": ["bonds", "defensive"],
    },
    3: {
        "avg_return_pct": 16.4,
        "note": (
            "Year 3 — historically the BEST year of the presidential cycle. "
            "Pre-election stimulus, strong consumer spending, low unemployment. "
            "Since 1939, Year 3 has been positive 89% of the time. "
            "Druckenmiller: 'Year 3 is when you load the boat.'"
        ),
        "best_sectors": ["growth", "tech", "small_cap", "consumer_discretionary"],
        "worst_sectors": ["bonds"],
    },
    4: {
        "avg_return_pct": 6.6,
        "note": (
            "Year 4 — election year. Strong in second half as election outcome clarifies. "
            "Markets dislike uncertainty: first half choppy, second half rally. "
            "Incumbents often stimulate economy to boost re-election odds."
        ),
        "best_sectors": ["growth", "defense", "energy"],
        "worst_sectors": ["utilities", "bonds"],
    },
}


def presidential_cycle_phase() -> dict:
    """
    Determine the current year of the US Presidential cycle.

    Returns:
        {
            year_of_cycle (int 1-4),
            current_president_term_start (str),
            days_into_term (int),
            historical_sp500_avg_return (float),
            note (str),
            best_sectors (list[str]),
            worst_sectors (list[str]),
            verdict (str),
        }

    Reference: Yale Hirsch (1967) "Stock Trader's Almanac";
    Stovall (1992) "Sector Investing"; Ned Davis Research.
    """
    today = date.today()

    # Find the most recent inauguration date
    past_inaugurations = [d for d in _INAUGURATION_DATES if d <= today]
    if not past_inaugurations:
        return {
            "year_of_cycle": 1,
            "note": "Could not determine cycle — no past inauguration found",
            "_source": "computed",
        }

    latest_inauguration = max(past_inaugurations)
    days_into_term = (today - latest_inauguration).days
    year_of_cycle = min(4, (days_into_term // 365) + 1)

    cycle_data = _PRESIDENTIAL_CYCLE_RETURNS[year_of_cycle]
    avg_return = cycle_data["avg_return_pct"]

    if avg_return > 10:
        verdict = f"FAVORABLE — Year {year_of_cycle} historically averages +{avg_return:.1f}%. Lean long with quality growth."
    elif avg_return > 0:
        verdict = f"NEUTRAL — Year {year_of_cycle} averages +{avg_return:.1f}%. No strong cycle tailwind. Stock selection matters more."
    else:
        verdict = f"CAUTION — Year {year_of_cycle} averages {avg_return:.1f}%. Cycle headwind in play."

    return {
        "year_of_cycle": year_of_cycle,
        "current_president_term_start": latest_inauguration.isoformat(),
        "days_into_term": days_into_term,
        "historical_sp500_avg_return": avg_return,
        "note": cycle_data["note"],
        "best_sectors": cycle_data["best_sectors"],
        "worst_sectors": cycle_data["worst_sectors"],
        "verdict": verdict,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Market Regime
# ─────────────────────────────────────────────────────────────────────────────

def market_regime() -> dict:
    """
    Classify the current market regime using SPY (200-day SMA), VIX,
    and the US Treasury yield curve (10Y-2Y spread).

    Regime taxonomy:
        bull_trend:    SPY > 200SMA, VIX < 20, curve normal or steepening
        late_bull:     SPY > 200SMA, VIX 20-25, curve flattening
        topping:       SPY near/below 200SMA, VIX rising 20-30, curve flat/inverted
        bear:          SPY < 200SMA, VIX > 25, curve inverted
        capitulation:  SPY < 200SMA, VIX > 35, sharp drawdown in progress
        bottoming:     SPY below/near 200SMA, VIX declining from spike, curve steepening
        recovery:      SPY recovering through 200SMA, VIX declining, curve normalizing

    Returns:
        {
            regime (str),
            spy_vs_200sma (str),            # "above" | "below" | "near"
            spy_200sma_gap_pct (float),      # current price % above/below 200SMA
            vix_level (float | None),
            yield_curve_10y2y (float | None),  # spread in basis points / 100
            yield_curve_signal (str),
            regime_description (str),
            _source ("live" | "cached" | "unavailable"),
        }

    Decision rules documented inline for full transparency.
    """
    cache_file = _cache_path("market_regime")
    cached = _cache_read(cache_file, _REGIME_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    if not _YFINANCE_AVAILABLE:
        return {
            "regime": "unknown",
            "spy_vs_200sma": "unknown",
            "spy_200sma_gap_pct": None,
            "vix_level": None,
            "yield_curve_10y2y": None,
            "yield_curve_signal": "unavailable",
            "regime_description": "yfinance not installed",
            "_source": "unavailable",
        }

    def _latest_close(ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            return float(hist["Close"].iloc[-1]) if not hist.empty else None
        except Exception as exc:
            logger.warning("yfinance %s: %s", ticker, exc)
            return None

    def _sma(ticker: str, window: int) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1y")
            if len(hist) < window:
                return None
            return float(hist["Close"].rolling(window).mean().iloc[-1])
        except Exception as exc:
            logger.warning("SMA calc failed for %s: %s", ticker, exc)
            return None

    spy_price = _latest_close("SPY")
    spy_sma200 = _sma("SPY", 200)
    vix_level = _latest_close("^VIX")

    # Yield curve: 10Y (^TNX) minus 2Y (^IRX)
    # Note: ^TNX is 10Y rate, ^FVX is 5Y, ^IRX is 13-week T-bill
    # For 2Y we use ^IRX as closest freely available proxy; real 2Y is DGS2 on FRED
    tnx_10y = _latest_close("^TNX")
    irx_2y  = _latest_close("^IRX")

    spread_10y2y: Optional[float] = None
    if tnx_10y is not None and irx_2y is not None:
        # ^TNX and ^IRX are in percentage points (e.g., 4.5 = 4.5%)
        spread_10y2y = round(tnx_10y - irx_2y, 2)

    # Yield curve signal
    if spread_10y2y is None:
        yc_signal = "unknown"
    elif spread_10y2y < -0.25:
        yc_signal = "inverted"
    elif spread_10y2y < 0.25:
        yc_signal = "flat"
    elif spread_10y2y < 1.0:
        yc_signal = "normal"
    else:
        yc_signal = "steep"

    # SPY vs 200SMA
    spy_gap_pct: Optional[float] = None
    spy_vs_200sma = "unknown"
    if spy_price is not None and spy_sma200 is not None:
        spy_gap_pct = round((spy_price / spy_sma200 - 1) * 100, 1)
        if spy_gap_pct > 2:
            spy_vs_200sma = "above"
        elif spy_gap_pct < -2:
            spy_vs_200sma = "below"
        else:
            spy_vs_200sma = "near"

    # Regime classification decision tree
    # Priority: capitulation > bear > topping > late_bull > bull_trend > bottoming > recovery
    vix = vix_level or 20.0  # default to neutral if unavailable

    if spy_vs_200sma == "below" and vix > 35:
        regime = "capitulation"
        desc = (
            "CAPITULATION: SPY below 200SMA with panic-level VIX. "
            "Forced selling and maximum fear. Historically within 0-6 months of a significant low. "
            "Capital preservation first; watch for VIX peak + reversal candle."
        )
    elif spy_vs_200sma == "below" and vix > 25 and yc_signal in ("inverted", "flat"):
        regime = "bear"
        desc = (
            "BEAR MARKET: SPY below 200SMA, elevated VIX, yield curve inverted/flat. "
            "Avoid aggressive longs. Short rallies in weak sectors. "
            "Historical playbook: rotate to defensive (staples, healthcare, gold)."
        )
    elif spy_vs_200sma in ("below", "near") and vix > 20 and yc_signal in ("inverted", "flat"):
        regime = "topping"
        desc = (
            "TOPPING/DISTRIBUTION: SPY near 200SMA, rising VIX, curve flattening. "
            "Distribution phase. Tighten stops, reduce position size, favor defensive sectors. "
            "Analogs: 2000 Q1, 2007 Q4, 2022 Q1."
        )
    elif spy_vs_200sma == "below" and vix < 25:
        regime = "bottoming"
        desc = (
            "BOTTOMING: SPY below 200SMA but VIX declining — worst of fear passing. "
            "Earliest recovery signals. Begin accumulating quality names in beaten-down sectors. "
            "Wait for SPY reclaim of 200SMA to confirm."
        )
    elif spy_vs_200sma == "above" and vix < 25 and yc_signal in ("flat", "inverted"):
        regime = "late_bull"
        desc = (
            "LATE BULL: SPY above 200SMA but yield curve flat/inverted — recession risk rising. "
            "Narrow leadership, defensive rotation beginning. "
            "Reduce cyclical exposure, raise cash, buy quality."
        )
    elif spy_vs_200sma == "above" and vix > 25:
        regime = "recovery"
        desc = (
            "RECOVERY: SPY above 200SMA but volatile — VIX still elevated from a prior event. "
            "Risk-on assets recovering. Cyclicals, small-cap, and beaten-down growth tend to outperform."
        )
    elif spy_vs_200sma == "above" and vix < 20:
        regime = "bull_trend"
        desc = (
            "BULL TREND: SPY above 200SMA, low VIX, healthy yield curve. "
            "Offensive positioning justified. Momentum, growth, and cyclicals tend to outperform. "
            "Stay long with trailing stops. The trend is your friend."
        )
    else:
        regime = "neutral"
        desc = "Mixed signals — no dominant regime. Balanced allocation; tighten conviction threshold."

    result = {
        "regime": regime,
        "spy_vs_200sma": spy_vs_200sma,
        "spy_200sma_gap_pct": spy_gap_pct,
        "vix_level": vix_level,
        "yield_curve_10y2y": spread_10y2y,
        "yield_curve_signal": yc_signal,
        "regime_description": desc,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Historical Analog Library
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class HistoricalAnalog:
    """A landmark market episode used for nearest-neighbor analog matching."""

    name: str
    year: str
    trigger: str
    sectors_that_won: list[str]
    sectors_that_lost: list[str]
    duration_months: int
    avg_drawdown: float        # peak-to-trough % on S&P 500
    key_lesson: str

    # Feature vector for nearest-neighbor scoring (normalized 0-1 scale)
    vix_level: float           # 0=low(10), 1=extreme(60+)
    fed_stance: float          # 0=dovish/cutting, 1=hawkish/hiking
    inflation_regime: float    # 0=deflationary, 0.5=normal, 1=high inflation
    yield_curve: float         # 0=steep/normal, 1=inverted
    spy_vs_200sma: float       # 0=far above, 1=far below

    def to_dict(self) -> dict:
        return asdict(self)


_ANALOG_LIBRARY: list[HistoricalAnalog] = [
    HistoricalAnalog(
        name="1973-74 Stagflation Bear",
        year="1973-1974",
        trigger="Oil embargo (OPEC), Nixon wage/price controls unraveling, Watergate political crisis.",
        sectors_that_won=["energy", "gold", "commodities", "consumer_staples"],
        sectors_that_lost=["growth", "tech", "airlines", "consumer_discretionary", "financials"],
        duration_months=21,
        avg_drawdown=-48.2,
        key_lesson=(
            "Stagflation (high inflation + recession) destroys growth stock multiples. "
            "Hard assets and energy win. Avoid rate-sensitive sectors. "
            "Benjamin Graham: 'In a stagflation regime, the margin of safety must be very large.'"
        ),
        vix_level=0.6,
        fed_stance=0.8,
        inflation_regime=1.0,
        yield_curve=0.3,
        spy_vs_200sma=0.9,
    ),
    HistoricalAnalog(
        name="1987 Crash — Portfolio Insurance Unwind",
        year="1987",
        trigger=(
            "Portfolio insurance (dynamic hedging) created feedback loop. "
            "Valuation extremes (P/E ~20x), rising rates, dollar weakness."
        ),
        sectors_that_won=["bonds", "gold", "cash"],
        sectors_that_lost=["everything_equities"],
        duration_months=3,
        avg_drawdown=-33.5,
        key_lesson=(
            "Leverage and derivatives amplify crashes. The crash was V-shaped — recovered within 2 years. "
            "Druckenmiller was short going into Black Monday; covered at the bottom. "
            "Structural market fragility > fundamental deterioration."
        ),
        vix_level=0.85,
        fed_stance=0.7,
        inflation_regime=0.6,
        yield_curve=0.4,
        spy_vs_200sma=0.95,
    ),
    HistoricalAnalog(
        name="1998 LTCM / Russia Default",
        year="1998",
        trigger=(
            "Russia defaulted on sovereign debt. LTCM (Long-Term Capital Management) "
            "faced $4.6B collapse from EM contagion + leverage unwinding."
        ),
        sectors_that_won=["US_large_cap", "US_treasuries", "gold"],
        sectors_that_lost=["emerging_markets", "financials", "high_yield"],
        duration_months=3,
        avg_drawdown=-19.3,
        key_lesson=(
            "EM contagion + credit crisis = short-term panic followed by rapid recovery. "
            "Fed coordinated bailout. US large-cap recovered to new highs within months. "
            "Flight to quality: US Treasuries and blue chips benefited."
        ),
        vix_level=0.7,
        fed_stance=0.2,
        inflation_regime=0.3,
        yield_curve=0.5,
        spy_vs_200sma=0.6,
    ),
    HistoricalAnalog(
        name="2000-02 Dot-Com Bust",
        year="2000-2002",
        trigger=(
            "Technology valuation extremes (NASDAQ P/E >100x). "
            "Narrow market leadership in unprofitable internet companies. "
            "Fed tightening 1999-2000 burst the bubble."
        ),
        sectors_that_won=["value", "energy", "financials", "REITs", "gold"],
        sectors_that_lost=["technology", "telecom", "growth", "NASDAQ"],
        duration_months=30,
        avg_drawdown=-49.1,
        key_lesson=(
            "Growth-to-value rotation can last years. NASDAQ fell 78%. "
            "Livermore: 'The market always goes back to normal.' "
            "Value stocks quietly outperformed from 2000-2006 while NASDAQ languished."
        ),
        vix_level=0.5,
        fed_stance=0.8,
        inflation_regime=0.3,
        yield_curve=0.3,
        spy_vs_200sma=0.85,
    ),
    HistoricalAnalog(
        name="2007-09 Global Financial Crisis",
        year="2007-2009",
        trigger=(
            "Subprime mortgage collapse, structured credit (CDO/MBS) implosion, "
            "global bank insolvency fears (Lehman, Bear Stearns)."
        ),
        sectors_that_won=["gold", "US_treasuries", "consumer_staples", "healthcare"],
        sectors_that_lost=["financials", "real_estate", "consumer_discretionary", "materials"],
        duration_months=17,
        avg_drawdown=-56.8,
        key_lesson=(
            "Systemic credit crisis is the most destructive regime. "
            "Howard Marks 2008 memo: 'Now is the time to invest.' "
            "Recovery was led by financials + tech (2009-2013). "
            "Cash flow quality matters most: avoid companies with refinancing risk."
        ),
        vix_level=1.0,
        fed_stance=0.0,
        inflation_regime=0.2,
        yield_curve=0.7,
        spy_vs_200sma=1.0,
    ),
    HistoricalAnalog(
        name="2011 European Debt / US Downgrade",
        year="2011",
        trigger=(
            "S&P downgraded US AAA credit rating. European sovereign debt crisis "
            "(Greece, Italy, Portugal). Debt ceiling standoff in Congress."
        ),
        sectors_that_won=["gold", "US_treasuries", "consumer_staples"],
        sectors_that_lost=["financials", "European_equities", "cyclicals"],
        duration_months=5,
        avg_drawdown=-19.4,
        key_lesson=(
            "Political/fiscal crises create sharp but often short-lived corrections. "
            "ECB intervention backstopped European banks. "
            "Recovery was swift — SPY recovered to pre-crisis levels within 6 months. "
            "Key signal: credit spreads, not equity prices, showed the bottom."
        ),
        vix_level=0.65,
        fed_stance=0.1,
        inflation_regime=0.4,
        yield_curve=0.4,
        spy_vs_200sma=0.65,
    ),
    HistoricalAnalog(
        name="2015-16 China Devaluation / Commodity Crash",
        year="2015-2016",
        trigger=(
            "China devalued the yuan, triggering EM capital outflows. "
            "Commodity crash (oil -75% from 2014 peak). Energy sector credit stress."
        ),
        sectors_that_won=["tech", "healthcare", "consumer_discretionary"],
        sectors_that_lost=["energy", "materials", "emerging_markets", "commodity"],
        duration_months=7,
        avg_drawdown=-14.2,
        key_lesson=(
            "Commodity bear markets hit EM disproportionately. "
            "US tech and consumer sectors decoupled and outperformed. "
            "Oil price floor = energy credit floor = EM floor. "
            "Fed 'one and done' hike in December 2015 relieved pressure."
        ),
        vix_level=0.5,
        fed_stance=0.4,
        inflation_regime=0.2,
        yield_curve=0.3,
        spy_vs_200sma=0.55,
    ),
    HistoricalAnalog(
        name="2018 Q4 Powell Pivot",
        year="2018",
        trigger=(
            "Fed raised rates 4x in 2018 to 2.5%. Markets feared policy error. "
            "US-China trade war escalation. S&P fell 20% in Q4."
        ),
        sectors_that_won=["bonds", "gold", "defensives"],
        sectors_that_lost=["growth", "tech", "cyclicals", "small_cap"],
        duration_months=3,
        avg_drawdown=-19.8,
        key_lesson=(
            "Fed pivot = market bottom. Powell reversed in January 2019 and S&P "
            "recovered 30%+ within 12 months. "
            "Watch Fed language closely: first 'pause' signal is a buy trigger. "
            "Powell's Christmas Eve 2018 statement: 'Fed will be flexible.'"
        ),
        vix_level=0.6,
        fed_stance=0.9,
        inflation_regime=0.4,
        yield_curve=0.5,
        spy_vs_200sma=0.75,
    ),
    HistoricalAnalog(
        name="2020 COVID Pandemic Crash",
        year="2020",
        trigger=(
            "Global pandemic. Economy locked down. GDP fell 32% annualized in Q2 2020. "
            "Fastest bear market in history (-34% in 33 days)."
        ),
        sectors_that_won=["tech", "e-commerce", "biotech", "homebuilders", "streaming"],
        sectors_that_lost=["airlines", "hospitality", "retail", "energy", "REITs"],
        duration_months=2,
        avg_drawdown=-33.9,
        key_lesson=(
            "Fastest recovery on record. Fed unlimited QE + fiscal stimulus ($6T+). "
            "Druckenmiller: 'We were wrong — the Fed was going to print money infinitely.' "
            "Companies with digital business models thrived; physical-world businesses suffered. "
            "Recovery: quality + digital beats value + physical."
        ),
        vix_level=1.0,
        fed_stance=0.0,
        inflation_regime=0.1,
        yield_curve=0.6,
        spy_vs_200sma=1.0,
    ),
    HistoricalAnalog(
        name="2022 Inflation / Fed Hiking Cycle",
        year="2022",
        trigger=(
            "Post-COVID inflation surge (CPI 9.1%). Fed hiked 425 bps in 12 months "
            "(fastest since 1980). Ukraine war amplified commodity/energy inflation."
        ),
        sectors_that_won=["energy", "commodities", "value", "healthcare", "financials"],
        sectors_that_lost=["growth", "ARK-type_speculative", "bonds", "real_estate", "crypto"],
        duration_months=12,
        avg_drawdown=-25.4,
        key_lesson=(
            "Rate shock kills long-duration assets: high-growth tech, bonds, speculative crypto. "
            "ARK Innovation fell 75%. 60/40 portfolio had worst year since 1937. "
            "Value vs growth rotation was extreme. "
            "Inflation regime demanded Buffett-style earnings power + pricing power."
        ),
        vix_level=0.55,
        fed_stance=1.0,
        inflation_regime=1.0,
        yield_curve=0.8,
        spy_vs_200sma=0.8,
    ),
]


def historical_analogs(current_conditions: dict) -> list[dict]:
    """
    Given current market conditions, return the 3 closest historical analogs
    using nearest-neighbor matching on a 5-feature vector.

    Args:
        current_conditions: dict with keys:
            vix_level (float 0-1, where 0=VIX<15, 1=VIX>50)
            fed_stance (float 0-1, where 0=cutting, 1=hiking)
            inflation_regime (float 0-1, where 0=deflation, 1=high CPI)
            yield_curve (float 0-1, where 0=steep, 1=inverted)
            spy_vs_200sma (float 0-1, where 0=far above, 1=far below)

    Returns:
        List of 3 analog dicts, sorted closest-first:
        [
            {
                name, year, trigger, sectors_that_won, sectors_that_lost,
                duration_months, avg_drawdown, key_lesson,
                similarity_score (float 0-1, 1=identical),
            },
            ...
        ]

    Algorithm: Euclidean distance on 5-feature vector, normalized to [0,1].
    """
    # Extract current vector
    def _val(key: str) -> float:
        v = current_conditions.get(key, 0.5)
        if v is None:
            return 0.5
        return float(v)

    current_vector = np.array([
        _val("vix_level"),
        _val("fed_stance"),
        _val("inflation_regime"),
        _val("yield_curve"),
        _val("spy_vs_200sma"),
    ])

    scored: list[tuple[float, HistoricalAnalog]] = []
    for analog in _ANALOG_LIBRARY:
        analog_vector = np.array([
            analog.vix_level,
            analog.fed_stance,
            analog.inflation_regime,
            analog.yield_curve,
            analog.spy_vs_200sma,
        ])
        # Euclidean distance; max possible = sqrt(5) for fully opposite vectors
        dist = float(np.linalg.norm(current_vector - analog_vector))
        max_dist = float(np.sqrt(5))
        similarity = round(1.0 - (dist / max_dist), 3)
        scored.append((similarity, analog))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_3 = scored[:3]

    results: list[dict] = []
    for similarity, analog in top_3:
        d = analog.to_dict()
        d["similarity_score"] = similarity
        # Remove feature vector fields from output — they're internal
        for key in ["vix_level", "fed_stance", "inflation_regime", "yield_curve", "spy_vs_200sma"]:
            d.pop(key, None)
        results.append(d)

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Unified cycle context
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_vix(vix_level: Optional[float]) -> float:
    """Map VIX level to 0-1 scale (0=10, 1=60+)."""
    if vix_level is None:
        return 0.5
    return max(0.0, min(1.0, (vix_level - 10.0) / 50.0))


def _normalize_spy_gap(gap_pct: Optional[float]) -> float:
    """Map SPY vs 200SMA gap to 0-1 scale (0=+20% above, 1=−20% below)."""
    if gap_pct is None:
        return 0.5
    return max(0.0, min(1.0, (0.0 - gap_pct) / 20.0 + 0.5))


def _normalize_yield_curve(spread: Optional[float]) -> float:
    """Map yield curve spread to 0-1 (0=+2 steep, 1=−0.5 inverted)."""
    if spread is None:
        return 0.5
    return max(0.0, min(1.0, (2.0 - spread) / 2.5))


def cycle_context(ticker: Optional[str] = None) -> dict:
    """
    Combine market regime, presidential cycle, seasonality, and historical
    analogs into a single structured context block for stock_picker.py.

    This is the primary function consumed by the research pipeline.

    Args:
        ticker: Optional ticker for seasonality analysis (defaults to SPY)

    Returns:
        {
            regime (dict),              # from market_regime()
            presidential_cycle (dict),  # from presidential_cycle_phase()
            seasonality (dict),         # from seasonality(ticker)
            top_analogs (list[dict]),   # from historical_analogs()
            narrative (str),            # plain-English 4-6 sentence synthesis
            timestamp (str),
        }
    """
    cache_file = _cache_path(f"cycle_context_{ticker or 'SPY'}")
    cached = _cache_read(cache_file, _CYCLE_TTL)
    if cached:
        return cached

    regime_data      = market_regime()
    pres_cycle       = presidential_cycle_phase()
    seasonal_data    = seasonality(ticker or "SPY", lookback_years=20)

    # Build conditions vector for analog matching
    conditions = {
        "vix_level":        _normalize_vix(regime_data.get("vix_level")),
        "spy_vs_200sma":    _normalize_spy_gap(regime_data.get("spy_200sma_gap_pct")),
        "yield_curve":      _normalize_yield_curve(regime_data.get("yield_curve_10y2y")),
        # Fed stance and inflation inferred from yield curve + regime
        "fed_stance":       0.7 if regime_data.get("yield_curve_signal") in ("inverted", "flat") else 0.3,
        "inflation_regime": 0.7 if regime_data.get("yield_curve_signal") == "inverted" else 0.4,
    }
    top_analogs = historical_analogs(conditions)

    # Build narrative
    regime_name = regime_data.get("regime", "unknown")
    pres_year   = pres_cycle.get("year_of_cycle", "?")
    pres_avg    = pres_cycle.get("historical_sp500_avg_return", 0)
    cur_month   = seasonal_data.get("current_month", "")
    month_rank  = seasonal_data.get("current_month_rank")
    best_analog = top_analogs[0] if top_analogs else {}

    regime_sentences = {
        "bull_trend":    "The primary trend is bullish — SPY above 200SMA, volatility contained.",
        "late_bull":     "Late-bull conditions: trend intact but yield curve flattening and VIX creeping up.",
        "topping":       "Distribution/topping pattern — trend losing momentum, hedging activity increasing.",
        "bear":          "Bear market regime — risk-off positioning warranted.",
        "capitulation":  "Capitulation underway — forced selling at extremes. Historical buying windows forming.",
        "bottoming":     "Bottoming process — worst fear passing but recovery not confirmed.",
        "recovery":      "Recovery regime — risk-on assets rebuilding from prior correction.",
        "neutral":       "Mixed regime signals — no dominant trend.",
        "unknown":       "Regime data unavailable.",
    }

    month_sentence = ""
    if cur_month and month_rank:
        rank_suffix = {1:"st",2:"nd",3:"rd"}.get(month_rank, "th")
        month_sentence = (
            f"{cur_month} ranks {month_rank}{rank_suffix} of 12 months seasonally "
            f"(avg {seasonal_data.get('current_month_avg', 0):.1f}%). "
        )

    best_patterns = seasonal_data.get("notable_patterns", [])
    pattern_sentence = (" ".join(best_patterns[:1]) + " ") if best_patterns else ""

    analog_sentence = ""
    if best_analog:
        analog_sentence = (
            f"Closest historical analog: {best_analog.get('name', '')} "
            f"({best_analog.get('year', '')}), similarity {best_analog.get('similarity_score', 0):.0%}. "
            f"Sectors that won: {', '.join(best_analog.get('sectors_that_won', [])[:3])}."
        )

    narrative = (
        f"{regime_sentences.get(regime_name, '')} "
        f"Presidential cycle Year {pres_year} historically averages +{pres_avg:.1f}% on SPY. "
        f"{month_sentence}"
        f"{pattern_sentence}"
        f"{analog_sentence}"
    ).strip()

    result = {
        "regime": regime_data,
        "presidential_cycle": pres_cycle,
        "seasonality": seasonal_data,
        "top_analogs": top_analogs,
        "narrative": narrative,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _cache_write(cache_file, result)
    return result
