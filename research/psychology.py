"""
research/psychology.py
----------------------
Behavioral finance indicators for Atlas Research.

Provides sentiment and psychology signals derived from publicly available free
sources. These are the same macro-sentiment inputs that legendary traders and
investors (Druckenmiller, Howard Marks, Paul Tudor Jones) use to understand
whether markets are acting on fear or greed — and position accordingly.

Theoretical grounding:
- Daniel Kahneman & Amos Tversky (1979): Prospect Theory — investors feel losses
  ~2x more intensely than equivalent gains. Extreme fear signals often mark
  turning points because the marginal seller is exhausted.
- Robert Shiller (2000): Irrational Exuberance — investor sentiment drives
  multi-year valuation cycles independent of fundamentals.
- Hersh Shefrin (2000): Beyond Greed and Fear — systematic behavioral biases
  (overconfidence, disposition effect, representativeness) create exploitable
  mispricings.
- John Templeton: "Bull markets are born on pessimism, grow on skepticism,
  mature on optimism and die on euphoria."

All functions:
- Have a 10-second network timeout
- Fall back to cached data in data/cache/ if the network call fails
- Return dictionaries with a `_source` key indicating live vs. cached
- Are idempotent given the same cached data

Usage:
    from research.psychology import behavioral_snapshot, fear_greed_index, vix_signal
    snap = behavioral_snapshot()
    print(snap["narrative"])
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import requests

try:
    import yfinance as yf
    _YFINANCE_AVAILABLE = True
except ImportError:
    _YFINANCE_AVAILABLE = False
    yf = None  # type: ignore[assignment]

try:
    from bs4 import BeautifulSoup  # type: ignore[import-untyped]
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Cache configuration
# ─────────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_SENTIMENT_TTL = 3600        # 1 hour — sentiment is intraday relevant
_VIX_TTL = 1800              # 30 min — VIX moves fast during sessions
_WEEKLY_TTL = 86400 * 3      # 3 days — AAII/NAAIM publish weekly

_REQUEST_TIMEOUT = 10


def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"psych_{h}.json"


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
#  Fear & Greed Index — CNN
# ─────────────────────────────────────────────────────────────────────────────

_CNN_FNG_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"

_FNG_CLASSIFICATIONS: list[tuple[int, int, str]] = [
    (0,   24,  "Extreme Fear"),
    (25,  44,  "Fear"),
    (45,  55,  "Neutral"),
    (56,  74,  "Greed"),
    (75,  100, "Extreme Greed"),
]


def _classify_fng(value: float) -> str:
    for lo, hi, label in _FNG_CLASSIFICATIONS:
        if lo <= value <= hi:
            return label
    return "Unknown"


def fear_greed_index() -> dict:
    """
    Fetch the CNN Fear & Greed Index and its seven sub-components.

    Source: https://production.dataviz.cnn.io/index/fearandgreed/graphdata
    Free, no authentication required.

    Returns:
        {
            value (float 0-100),
            classification (str),
            timestamp (ISO 8601),
            components: {
                momentum (str label + score),
                put_call_ratio (str label + score),
                junk_bond_demand (str label + score),
                market_volatility (str label + score),
                safe_haven_demand (str label + score),
                stock_price_strength (str label + score),
                stock_price_breadth (str label + score),
            },
            _source ("live" | "cached" | "unavailable"),
        }

    Contrarian reading (Shiller 2000):
        - Value < 25: Extreme Fear → historically a buying window
        - Value > 75: Extreme Greed → elevated risk of correction
    """
    cache_file = _cache_path("fear_greed_index")
    cached = _cache_read(cache_file, _SENTIMENT_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    try:
        resp = requests.get(
            _CNN_FNG_URL,
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 AtlasResearch/1.0"},
        )
        resp.raise_for_status()
        raw = resp.json()
    except Exception as exc:
        logger.warning("Fear & Greed fetch failed: %s", exc)
        return {
            "value": None,
            "classification": "unavailable",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "_source": "unavailable",
        }

    # The CNN endpoint returns a nested structure; drill to fear_and_greed
    fng_data = raw.get("fear_and_greed", {})
    value = float(fng_data.get("score", 50))
    timestamp = fng_data.get("timestamp", datetime.now(timezone.utc).isoformat())

    # Extract component scores — CNN wraps them under fear_and_greed_historical
    # and under per-indicator keys at the top level
    component_map = {
        "momentum":            raw.get("market_momentum_sp500", {}),
        "put_call_ratio":      raw.get("put_and_call_options", {}),
        "junk_bond_demand":    raw.get("junk_bond_demand", {}),
        "market_volatility":   raw.get("market_volatility_vix", {}),
        "safe_haven_demand":   raw.get("safe_haven_demand", {}),
        "stock_price_strength": raw.get("stock_price_strength", {}),
        "stock_price_breadth": raw.get("stock_price_breadth", {}),
    }

    components: dict[str, dict] = {}
    for name, comp in component_map.items():
        if isinstance(comp, dict) and "score" in comp:
            components[name] = {
                "score": round(float(comp["score"]), 1),
                "rating": comp.get("rating", _classify_fng(float(comp["score"]))),
            }
        else:
            components[name] = {"score": None, "rating": "unavailable"}

    result = {
        "value": round(value, 1),
        "classification": _classify_fng(value),
        "timestamp": timestamp,
        "components": components,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  VIX Signal — CBOE Volatility Index via yfinance
# ─────────────────────────────────────────────────────────────────────────────

_VIX_BANDS: list[tuple[float, float, str, str]] = [
    (0.0,  12.0,  "Complacency",       "Danger zone — euphoria often precedes sharp reversals"),
    (12.0, 20.0,  "Normal",            "Healthy volatility regime — no edge from VIX alone"),
    (20.0, 30.0,  "Elevated Concern",  "Risk-off building — position sizing prudence warranted"),
    (30.0, 40.0,  "Fear",              "Historically a buying zone. 2011, 2018, 2020 pre-recovery"),
    (40.0, 999.0, "Panic",             "Historically best long-term entry. 2008 GFC, 2020 COVID"),
]


def _classify_vix(vix: float) -> tuple[str, str]:
    for lo, hi, label, note in _VIX_BANDS:
        if lo <= vix < hi:
            return label, note
    return "Unknown", ""


def vix_signal() -> dict:
    """
    Fetch the current VIX level plus term structure (VIX3M, VIX6M).

    Data source: yfinance — ^VIX, ^VIX3M, ^VIX6M (all free).

    Returns:
        {
            vix_spot (float),
            vix_3m (float | None),
            vix_6m (float | None),
            classification (str),
            note (str),
            term_structure ("contango" | "backwardation" | "flat" | "unknown"),
            term_structure_note (str),
            _source ("live" | "cached" | "unavailable"),
        }

    Interpretation:
        - Contango (VIX < VIX3M < VIX6M): Normal — market calm, fear priced
          into the future but not here yet.
        - Backwardation (VIX > VIX3M > VIX6M): Elevated present stress — often
          coincides with crisis peaks (2008, 2020). Historically a buy signal.

    Reference: CBOE Volatility Index white paper (2009); Whaley (2009)
    "Understanding the VIX."
    """
    cache_file = _cache_path("vix_signal")
    cached = _cache_read(cache_file, _VIX_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    if not _YFINANCE_AVAILABLE:
        return {
            "vix_spot": None,
            "vix_3m": None,
            "vix_6m": None,
            "classification": "unavailable",
            "note": "yfinance not installed",
            "term_structure": "unknown",
            "term_structure_note": "",
            "_source": "unavailable",
        }

    def _latest_close(ticker: str) -> Optional[float]:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if hist.empty:
                return None
            return float(hist["Close"].iloc[-1])
        except Exception as exc:
            logger.warning("yfinance fetch failed for %s: %s", ticker, exc)
            return None

    vix_spot = _latest_close("^VIX")
    vix_3m   = _latest_close("^VIX3M")
    vix_6m   = _latest_close("^VIX6M")

    if vix_spot is None:
        return {
            "vix_spot": None,
            "vix_3m": None,
            "vix_6m": None,
            "classification": "unavailable",
            "note": "VIX data unavailable",
            "term_structure": "unknown",
            "term_structure_note": "",
            "_source": "unavailable",
        }

    classification, note = _classify_vix(vix_spot)

    # Term structure
    term_structure = "unknown"
    term_note = ""
    if vix_3m is not None:
        if vix_spot < vix_3m:
            term_structure = "contango"
            term_note = "Market calm — future risk priced higher. Normal regime."
        elif vix_spot > vix_3m:
            term_structure = "backwardation"
            term_note = (
                "Spot stress exceeds forward pricing — present panic. "
                "Historically coincides with crisis peaks and subsequent recoveries."
            )
        else:
            term_structure = "flat"
            term_note = "VIX term structure flat — no strong signal."

    result = {
        "vix_spot": round(vix_spot, 2),
        "vix_3m": round(vix_3m, 2) if vix_3m else None,
        "vix_6m": round(vix_6m, 2) if vix_6m else None,
        "classification": classification,
        "note": note,
        "term_structure": term_structure,
        "term_structure_note": term_note,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  AAII Sentiment Survey (weekly)
# ─────────────────────────────────────────────────────────────────────────────

_AAII_URL = "https://www.aaii.com/sentimentsurvey/sent_results"

# Historical averages (AAII publishes these as long-run means)
_AAII_BULL_MEAN  = 37.5
_AAII_BEAR_MEAN  = 31.0
_AAII_NEUTRAL_MEAN = 31.5


def aaii_sentiment() -> dict:
    """
    Fetch AAII weekly bull/bear/neutral sentiment survey results.

    Source: https://www.aaii.com/sentimentsurvey (public, no auth required)
    Publishes every Thursday.

    Returns:
        {
            bullish_pct (float),
            neutral_pct (float),
            bearish_pct (float),
            bull_bear_spread (float),
            bull_deviation_from_mean (float),   # bullish - 37.5 long-run avg
            bear_deviation_from_mean (float),
            signal (str),                        # "contrarian_buy" | "contrarian_sell" | "neutral"
            note (str),
            survey_date (str),
            _source ("live" | "cached" | "unavailable"),
        }

    Contrarian interpretation (Shefrin 2000; Clarke & Statman 1998):
        - Bearish% > 55%: Historically a bullish contrarian signal. Most retail
          sellers are exhausted; professional buyers step in.
        - Bullish% > 55%: Historically a cautionary signal. Euphoria near peaks.

    Reference: AAII Sentiment Survey Methodology (1987–present); Zweig (1986)
    "Martin Zweig's Winning on Wall Street."
    """
    cache_file = _cache_path("aaii_sentiment")
    cached = _cache_read(cache_file, _WEEKLY_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    fallback = {
        "bullish_pct": None,
        "neutral_pct": None,
        "bearish_pct": None,
        "bull_bear_spread": None,
        "bull_deviation_from_mean": None,
        "bear_deviation_from_mean": None,
        "signal": "unavailable",
        "note": "",
        "survey_date": None,
        "_source": "unavailable",
    }

    if not _BS4_AVAILABLE:
        fallback["note"] = "beautifulsoup4 not installed — pip install beautifulsoup4"
        return fallback

    try:
        resp = requests.get(
            _AAII_URL,
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 AtlasResearch/1.0"},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # AAII publishes the latest percentages in a table
        # Parse the first data row (most recent week)
        rows = soup.select("table tr")
        bullish_pct = neutral_pct = bearish_pct = None
        survey_date = None

        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if not cells:
                continue
            # Look for a row that has percentage values
            pct_cells = [c for c in cells if c.endswith("%")]
            if len(pct_cells) >= 3:
                try:
                    bullish_pct = float(pct_cells[0].strip("%"))
                    neutral_pct = float(pct_cells[1].strip("%"))
                    bearish_pct = float(pct_cells[2].strip("%"))
                    # Date is usually first cell
                    date_candidate = cells[0]
                    if "/" in date_candidate or "-" in date_candidate:
                        survey_date = date_candidate
                    break
                except (ValueError, IndexError):
                    continue

    except Exception as exc:
        logger.warning("AAII sentiment fetch failed: %s", exc)
        return fallback

    if bullish_pct is None:
        fallback["note"] = "Could not parse AAII table structure — site may have changed"
        return fallback

    bull_bear_spread = round(bullish_pct - bearish_pct, 1)
    bull_dev = round(bullish_pct - _AAII_BULL_MEAN, 1)
    bear_dev = round(bearish_pct - _AAII_BEAR_MEAN, 1)

    # Contrarian signal logic
    if bearish_pct > 55 or (bull_bear_spread < -20):
        signal = "contrarian_buy"
        note = (
            f"Extreme bearishness ({bearish_pct:.1f}% bears, {bull_bear_spread:+.1f} spread). "
            "Historically a bullish contrarian entry — retail capitulation often precedes rallies."
        )
    elif bullish_pct > 55 or (bull_bear_spread > 25):
        signal = "contrarian_sell"
        note = (
            f"Extreme bullishness ({bullish_pct:.1f}% bulls, {bull_bear_spread:+.1f} spread). "
            "Historically a cautionary signal — sentiment peaks often precede corrections."
        )
    else:
        signal = "neutral"
        note = "Sentiment within historical norms — no strong contrarian signal."

    result = {
        "bullish_pct": bullish_pct,
        "neutral_pct": neutral_pct,
        "bearish_pct": bearish_pct,
        "bull_bear_spread": bull_bear_spread,
        "bull_deviation_from_mean": bull_dev,
        "bear_deviation_from_mean": bear_dev,
        "signal": signal,
        "note": note,
        "survey_date": survey_date,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  NAAIM Exposure Index (weekly)
# ─────────────────────────────────────────────────────────────────────────────

_NAAIM_URL = "https://www.naaim.org/programs/naaim-exposure-index/"

# NAAIM historical mean exposure ~70%
_NAAIM_MEAN = 70.0


def naaim_exposure() -> dict:
    """
    Fetch the NAAIM Exposure Index — active equity manager positioning.

    Source: https://www.naaim.org/programs/naaim-exposure-index/
    NAAIM members report their equity exposure weekly. The aggregate number
    shows how much professional active managers are invested in equities.

    Returns:
        {
            exposure (float 0-200, where 200 = 2x levered long),
            deviation_from_mean (float),
            signal (str),
            note (str),
            week_ending (str | None),
            _source ("live" | "cached" | "unavailable"),
        }

    Interpretation:
        - High exposure (>90): Managers all-in. Limited buying power remaining.
          Often a warning signal (no more buyers to push market higher).
        - Low exposure (<30): Managers de-risked. Substantial dry powder on the
          sidelines that can fuel a recovery.

    Reference: NAAIM (National Association of Active Investment Managers)
    published survey 2006–present.
    """
    cache_file = _cache_path("naaim_exposure")
    cached = _cache_read(cache_file, _WEEKLY_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    fallback = {
        "exposure": None,
        "deviation_from_mean": None,
        "signal": "unavailable",
        "note": "",
        "week_ending": None,
        "_source": "unavailable",
    }

    if not _BS4_AVAILABLE:
        fallback["note"] = "beautifulsoup4 not installed"
        return fallback

    try:
        resp = requests.get(
            _NAAIM_URL,
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 AtlasResearch/1.0"},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        exposure = None
        week_ending = None

        # NAAIM posts current exposure prominently on page
        # Look for a number that looks like an exposure reading (0-200)
        for tag in soup.find_all(["p", "td", "strong", "span", "h3", "h4"]):
            text = tag.get_text(strip=True)
            # Try to find something like "Current Exposure: 72.35" or just a float
            import re
            match = re.search(r'\b(\d{1,3}\.\d{1,2})\b', text)
            if match:
                val = float(match.group(1))
                # Exposure is 0-200; typical range is 10-150
                if 0 <= val <= 200:
                    exposure = val
                    # Look for a nearby date
                    date_match = re.search(
                        r'\b(\d{1,2}/\d{1,2}/\d{2,4}|\w+ \d{1,2},?\s*\d{4})\b', text
                    )
                    if date_match:
                        week_ending = date_match.group(1)
                    break

    except Exception as exc:
        logger.warning("NAAIM fetch failed: %s", exc)
        return fallback

    if exposure is None:
        fallback["note"] = "Could not parse NAAIM exposure value from page"
        return fallback

    dev = round(exposure - _NAAIM_MEAN, 1)

    if exposure < 30:
        signal = "contrarian_buy"
        note = (
            f"NAAIM exposure {exposure:.1f}% — managers heavily de-risked. "
            "Substantial institutional dry powder available to fuel recovery."
        )
    elif exposure > 95:
        signal = "caution"
        note = (
            f"NAAIM exposure {exposure:.1f}% — managers near fully invested. "
            "Limited marginal buyers. Elevated risk of mean reversion on bad news."
        )
    else:
        signal = "neutral"
        note = f"NAAIM exposure {exposure:.1f}% — within normal range ({_NAAIM_MEAN:.0f}% historical mean)."

    result = {
        "exposure": round(exposure, 1),
        "deviation_from_mean": dev,
        "signal": signal,
        "note": note,
        "week_ending": week_ending,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  CBOE Put/Call Ratio
# ─────────────────────────────────────────────────────────────────────────────

_CBOE_PC_URL = "https://www.cboe.com/us/options/market_statistics/daily/"


def put_call_ratio_cboe() -> dict:
    """
    Fetch the CBOE total put/call ratio from CBOE market statistics.

    Source: https://www.cboe.com/us/options/market_statistics/daily/
    No API key required.

    Returns:
        {
            total_ratio (float),
            equity_ratio (float | None),
            index_ratio (float | None),
            signal (str),
            note (str),
            date (str | None),
            _source ("live" | "cached" | "unavailable"),
        }

    Contrarian interpretation:
        - Ratio > 1.2: Elevated put buying. Market is overly hedged / bearish.
          Historically bullish for stocks (too many people already short).
        - Ratio < 0.7: Elevated call buying. Complacency / greed extreme.
          Historically bearish for stocks (too many one-way longs).
        - "Normal" range 0.8–1.0 for total ratio.

    Reference: McMillan (2002) "Options as a Strategic Investment."
    Zweig (1970s) put/call ratio as contrarian indicator.
    """
    cache_file = _cache_path("put_call_ratio")
    cached = _cache_read(cache_file, _SENTIMENT_TTL)
    if cached:
        cached["_source"] = "cached"
        return cached

    fallback = {
        "total_ratio": None,
        "equity_ratio": None,
        "index_ratio": None,
        "signal": "unavailable",
        "note": "",
        "date": None,
        "_source": "unavailable",
    }

    if not _BS4_AVAILABLE:
        fallback["note"] = "beautifulsoup4 not installed"
        return fallback

    try:
        resp = requests.get(
            _CBOE_PC_URL,
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 AtlasResearch/1.0"},
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        total_ratio = equity_ratio = index_ratio = None
        date_str = None

        import re
        # CBOE page has a table with columns like "TOTAL", "INDEX", "EQUITY"
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 3:
                    continue
                # Look for the put/call rows
                joined = " ".join(cells).lower()
                if "put/call" in joined or "total" in joined:
                    for cell in cells:
                        m = re.search(r'\b(\d\.\d{2})\b', cell)
                        if m:
                            val = float(m.group(1))
                            if total_ratio is None:
                                total_ratio = val
                            elif equity_ratio is None:
                                equity_ratio = val
                            elif index_ratio is None:
                                index_ratio = val
                # Grab date from page title or header
                for cell in cells:
                    dm = re.search(r'\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})\b', cell)
                    if dm and not date_str:
                        date_str = dm.group(1)

    except Exception as exc:
        logger.warning("CBOE put/call fetch failed: %s", exc)
        return fallback

    if total_ratio is None:
        fallback["note"] = "Could not parse CBOE put/call ratio from page"
        return fallback

    if total_ratio > 1.2:
        signal = "contrarian_buy"
        note = (
            f"Put/call {total_ratio:.2f} — extreme put buying. Options market overly hedged. "
            "Historically a bullish contrarian signal."
        )
    elif total_ratio < 0.7:
        signal = "contrarian_sell"
        note = (
            f"Put/call {total_ratio:.2f} — complacency in options market. "
            "Too many calls relative to puts — historically a caution flag."
        )
    else:
        signal = "neutral"
        note = f"Put/call {total_ratio:.2f} — within normal range (0.7–1.2)."

    result = {
        "total_ratio": round(total_ratio, 3),
        "equity_ratio": round(equity_ratio, 3) if equity_ratio else None,
        "index_ratio": round(index_ratio, 3) if index_ratio else None,
        "signal": signal,
        "note": note,
        "date": date_str,
        "_source": "live",
    }
    _cache_write(cache_file, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  FINRA Margin Debt
# ─────────────────────────────────────────────────────────────────────────────

_FINRA_MARGIN_URL = "https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics"

# Hardcoded recent margin debt peaks for context (FINRA updates monthly, ~45-day lag)
# Source: FINRA Margin Statistics published reports
_MARGIN_DEBT_PEAKS = {
    "2000_dot_com":   {"month": "March 2000",    "value_bn": 278.5},
    "2007_pre_gfc":   {"month": "July 2007",     "value_bn": 381.4},
    "2018_q4_crash":  {"month": "May 2018",      "value_bn": 668.9},
    "2021_peak":      {"month": "October 2021",  "value_bn": 935.9},
    "2022_low":       {"month": "December 2022", "value_bn": 588.0},
}


def margin_debt_signal() -> dict:
    """
    Return context on FINRA margin debt as a systemic leverage indicator.

    FINRA publishes margin statistics monthly with a ~45-day lag. Rather than
    scraping (the page is JS-heavy), this function returns the hardcoded
    historical context plus instructions on how to interpret the data.

    Returns:
        {
            note (str),
            historical_peaks (dict),
            interpretation (str),
            action_threshold (str),
            _source ("hardcoded"),
        }

    Key insight (Soros 2003, "The Alchemy of Finance"):
        Margin debt expansion is reflexive — rising markets encourage more
        borrowing which buys more stocks. The reversal is vicious: forced
        liquidations accelerate drawdowns. Rapid % increases in margin debt
        (>30% YoY) have preceded every major market top since 2000.

    For live margin debt: https://www.finra.org/investors/learn-to-invest/advanced-investing/margin-statistics
    """
    return {
        "note": (
            "FINRA margin debt is published monthly with ~45-day lag. "
            "Scraping is not practical (JS-rendered). Use the historical context below."
        ),
        "historical_peaks": _MARGIN_DEBT_PEAKS,
        "interpretation": (
            "Rapid YoY margin debt growth (>30%) has preceded every major market top since 2000. "
            "2021 peak of $936B coincided with meme stock mania. "
            "2022 deleveraging drove -25% S&P correction. "
            "Current context: if margin debt is expanding aggressively, treat as a late-cycle warning."
        ),
        "action_threshold": (
            "When margin debt YoY growth > 30%: reduce leveraged positions, hedge. "
            "When margin debt YoY decline > 20%: prior forced selling may be exhausted — "
            "consider it a structural support for a recovery."
        ),
        "_source": "hardcoded",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Behavioral Snapshot — aggregate all signals
# ─────────────────────────────────────────────────────────────────────────────

def _greed_score_from_signals(fng: dict, vix: dict, aaii: dict, pc: dict) -> float:
    """
    Compute a 0-100 composite greed score from available signals.

    0  = Extreme Fear
    50 = Neutral
    100 = Extreme Greed

    Weighting:
    - Fear & Greed Index: 40% (broadest composite)
    - VIX classification: 30%
    - AAII bull/bear spread: 20%
    - Put/call ratio: 10%
    """
    score = 50.0  # start neutral
    weight_used = 0.0

    # CNN Fear & Greed (40%)
    fng_val = fng.get("value")
    if fng_val is not None:
        score = score * weight_used + fng_val * 0.40
        weight_used += 0.40
        if weight_used > 0.40:
            score = score / weight_used

    # VIX (30%) — invert: low VIX = high greed
    vix_spot = vix.get("vix_spot")
    if vix_spot is not None:
        # Map VIX to 0-100 greed: VIX 10 = 90 greed, VIX 40 = 10 greed
        vix_greed = max(0.0, min(100.0, 100.0 - (vix_spot - 10.0) * 3.0))
        if weight_used == 0:
            score = vix_greed
        else:
            score = (score * weight_used + vix_greed * 0.30) / (weight_used + 0.30)
        weight_used += 0.30

    # AAII bull/bear spread (20%) — map spread [-50, +50] to [0, 100]
    spread = aaii.get("bull_bear_spread")
    if spread is not None:
        aaii_greed = max(0.0, min(100.0, (spread + 50.0)))
        if weight_used == 0:
            score = aaii_greed
        else:
            score = (score * weight_used + aaii_greed * 0.20) / (weight_used + 0.20)
        weight_used += 0.20

    # Put/Call (10%) — invert: high p/c = fear = low greed
    pc_ratio = pc.get("total_ratio")
    if pc_ratio is not None:
        # Map 0.5-1.5 put/call to 100-0 greed
        pc_greed = max(0.0, min(100.0, 100.0 - (pc_ratio - 0.5) * 100.0))
        if weight_used == 0:
            score = pc_greed
        else:
            score = (score * weight_used + pc_greed * 0.10) / (weight_used + 0.10)
        weight_used += 0.10

    return round(score, 1)


def _regime_from_score(greed_score: float) -> str:
    if greed_score < 20:
        return "extreme_fear"
    elif greed_score < 40:
        return "fear"
    elif greed_score < 60:
        return "neutral"
    elif greed_score < 80:
        return "greed"
    else:
        return "extreme_greed"


def _build_narrative(regime: str, greed_score: float, fng: dict, vix: dict, aaii: dict) -> str:
    """
    Build a deterministic 2-3 sentence plain-English behavioral read.
    Output is fully determined by the input values — no randomness.
    """
    regime_sentences: dict[str, str] = {
        "extreme_fear": (
            f"Market psychology is in Extreme Fear (composite greed score {greed_score}/100). "
            "Retail investors are capitulating, options markets are heavily hedged, and volatility "
            "is elevated — conditions historically associated with major bottoming processes "
            "(cf. Kahneman & Tversky: loss aversion drives overshoots below fair value)."
        ),
        "fear": (
            f"Market psychology is in Fear territory (composite score {greed_score}/100). "
            "Sentiment is below historical averages across multiple indicators, suggesting "
            "risk-averse positioning that often resolves in a contrarian opportunity "
            "as seller exhaustion sets in."
        ),
        "neutral": (
            f"Market psychology is broadly Neutral (composite score {greed_score}/100). "
            "Fear and greed indicators are within historical norms. "
            "No strong behavioral edge — this environment demands fundamentals and catalyst discipline."
        ),
        "greed": (
            f"Market psychology is in Greed territory (composite score {greed_score}/100). "
            "Bullish sentiment and low hedging suggest positioning is extended. "
            "Howard Marks: 'The less prudence others exercise, the more prudence you should exercise.' "
            "Raise conviction bar and tighten stops."
        ),
        "extreme_greed": (
            f"Market psychology is at Extreme Greed (composite score {greed_score}/100). "
            "Euphoria indicators are elevated — consistent with late-cycle conditions seen before "
            "2000, 2007, and 2021 peaks. Shiller CAPE and margin debt context should be cross-checked. "
            "Reduce position sizing, avoid chasing momentum entries."
        ),
    }

    vix_addendum = ""
    vix_spot = vix.get("vix_spot")
    if vix_spot and vix_spot > 30:
        vix_addendum = (
            f" VIX at {vix_spot:.1f} signals acute fear — "
            "historically a buying window within 6-12 months (2008, 2020 precedent)."
        )
    elif vix_spot and vix_spot < 12:
        vix_addendum = (
            f" VIX at {vix_spot:.1f} — complacency extreme. "
            "Low VIX regimes have preceded rapid volatility spikes."
        )

    return regime_sentences.get(regime, f"Composite greed score: {greed_score}/100.") + vix_addendum


def behavioral_snapshot() -> dict:
    """
    Aggregate all behavioral finance indicators into a single market psychology read.

    Calls: fear_greed_index(), vix_signal(), aaii_sentiment(), put_call_ratio_cboe()
    Combines them into a composite greed score (0-100) and regime classification.

    Returns:
        {
            regime ("extreme_fear" | "fear" | "neutral" | "greed" | "extreme_greed"),
            greed_score (float 0-100),
            flags (list[str]),          # notable signals to highlight in prompts
            narrative (str),            # 2-3 sentence plain-English read
            components: {
                fear_greed_index (dict),
                vix (dict),
                aaii (dict),
                put_call_ratio (dict),
                margin_debt (dict),
            },
            timestamp (str),
        }

    This is the primary function consumed by stock_picker.py.
    """
    fng   = fear_greed_index()
    vix   = vix_signal()
    aaii  = aaii_sentiment()
    pc    = put_call_ratio_cboe()
    margin = margin_debt_signal()

    greed_score = _greed_score_from_signals(fng, vix, aaii, pc)
    regime = _regime_from_score(greed_score)

    flags: list[str] = []

    # VIX flags
    vix_spot = vix.get("vix_spot")
    if vix_spot:
        if vix_spot > 40:
            flags.append(f"VIX PANIC ({vix_spot:.1f}) — historically strongest buy zone")
        elif vix_spot > 30:
            flags.append(f"VIX FEAR ({vix_spot:.1f}) — elevated; historical buying window")
        elif vix_spot < 12:
            flags.append(f"VIX COMPLACENCY ({vix_spot:.1f}) — reversal risk elevated")
        if vix.get("term_structure") == "backwardation":
            flags.append("VIX BACKWARDATION — present stress > future; crisis signal")

    # FNG flags
    fng_val = fng.get("value")
    if fng_val is not None:
        if fng_val < 20:
            flags.append(f"CNN EXTREME FEAR ({fng_val}) — contrarian opportunity zone")
        elif fng_val > 80:
            flags.append(f"CNN EXTREME GREED ({fng_val}) — euphoria warning")

    # AAII flags
    aaii_signal = aaii.get("signal", "")
    if aaii_signal == "contrarian_buy":
        flags.append(f"AAII EXTREME BEARISHNESS — retail capitulation (contrarian buy)")
    elif aaii_signal == "contrarian_sell":
        flags.append(f"AAII EXTREME BULLISHNESS — contrarian caution signal")

    # Put/call flags
    pc_signal = pc.get("signal", "")
    if pc_signal == "contrarian_buy":
        flags.append(f"PUT/CALL RATIO HIGH ({pc.get('total_ratio')}) — options hedging extreme")
    elif pc_signal == "contrarian_sell":
        flags.append(f"PUT/CALL RATIO LOW ({pc.get('total_ratio')}) — complacency in options")

    narrative = _build_narrative(regime, greed_score, fng, vix, aaii)

    return {
        "regime": regime,
        "greed_score": greed_score,
        "flags": flags,
        "narrative": narrative,
        "components": {
            "fear_greed_index": fng,
            "vix": vix,
            "aaii": aaii,
            "put_call_ratio": pc,
            "margin_debt": margin,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
