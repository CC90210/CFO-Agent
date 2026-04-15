"""
research/options_flow.py
------------------------
Short interest, options chain analysis, unusual activity detection, squeeze
scoring, and IV rank for Atlas Research.

Data sources:
  yfinance — options chains (OI, volume, IV per strike), short interest
              via `Ticker.info` (shortPercentOfFloat, shortRatio).
  Free tier only. Unusual-options detection uses a naive volume-vs-OI
  heuristic that works well for large-cap daily sweeps.

Paid upgrades (documented but NOT implemented here):
  Unusual Whales ($48/mo)  — real-time institutional sweep detection with
                              sentiment scoring, dark pool prints, Congress
                              tracking. API available. Best-in-class for
                              retail-accessible unusual flow.
  CheddarFlow ($50/mo)     — live options flow with whale score, put/call
                              breakdown by expiry, heat maps.
  FlowAlgo ($199/mo)       — professional-grade dark pool + options alerts.
                              Used by prop desks. Overkill for retail.
  Market Chameleon (free)  — IV rank/percentile lookup for most US tickers,
                              no API but web-scrapeable.
  CBOE DataShop            — historical options data for backtesting.

Academic backing:
  Short squeeze mechanics: When short interest > 20% of float and days-to-cover
  > 3, a sustained price move up forces short sellers to buy-to-cover,
  accelerating the move. This is the mechanics behind GameStop (Jan 2021),
  Volkswagen squeeze (2008). Documented in: Asquith, Pathak & Ritter (2005),
  Boehmer, Jones & Zhang (2008).

  IV rank as a signal: IV rank (current IV percentile vs. 1-year range) above
  80 indicates options are expensive relative to history — favorable for
  premium sellers (covered calls, cash-secured puts). Below 20 is cheap —
  favorable for option buyers. (Natenberg, "Option Volatility & Pricing", 1994.)

  Put/call ratio as a contrarian indicator: Extreme put/call ratios (>1.5 or
  <0.5) signal crowded directional bets and often precede reversals. This is
  a sentiment indicator, not a momentum signal. (Pan & Poteshman, 2006.)

Caching:
  - Options chains (live): 15-minute TTL — options data is time-sensitive
  - Short interest / IV rank (history): 24-hour TTL

Usage:
    from research.options_flow import get_options_snapshot, squeeze_score

CLI:
    python -m research.options_flow NVDA
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

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

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    _NUMPY_AVAILABLE = False
    np = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Cache configuration
# ─────────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_LIVE_TTL = 900        # 15 minutes — options data
_HISTORY_TTL = 86400   # 24 hours   — IV rank history, short interest

# Minimum open interest / volume to avoid noise from illiquid strikes
_MIN_OI = 500
_MIN_VOLUME = 500


# ─────────────────────────────────────────────────────────────────────────────
#  Exceptions
# ─────────────────────────────────────────────────────────────────────────────

class TickerNotFound(Exception):
    """Raised when yfinance returns no meaningful data for a ticker."""


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class OptionsSnapshot:
    """
    Point-in-time options market summary for a single ticker.

    Fields:
        ticker:                     Stock symbol
        timestamp:                  ISO timestamp when data was fetched (UTC)
        spot_price:                 Current stock price in USD
        put_call_ratio:             Total put OI / total call OI.
                                    > 1.0 = more puts (bearish sentiment or hedging)
                                    < 0.5 = more calls (bullish positioning / complacency)
        total_call_oi:              Aggregate call open interest across all expiries
        total_put_oi:               Aggregate put open interest across all expiries
        implied_volatility_30d:     ATM 30-day implied volatility estimate (%).
                                    Computed as the average IV of near-ATM strikes
                                    in the nearest expiry >= 20 days out.
        iv_rank:                    Current IV as a percentile of its 1-year range (0–100).
                                    Computed from 1 year of historical close-to-close
                                    realised volatility as a proxy when options history
                                    is unavailable (yfinance doesn't provide IV history
                                    directly — see iv_rank() function for full method).
        short_interest_pct:         Short interest as % of float (from yfinance info)
        short_interest_ratio_days_to_cover: Days to cover at average daily volume
        borrow_rate:                Annualised borrow rate % (None — not available
                                    on free tier; requires Interactive Brokers or
                                    S3 Partners data subscription)
    """
    ticker: str
    timestamp: str
    spot_price: Optional[float]
    put_call_ratio: Optional[float]
    total_call_oi: int
    total_put_oi: int
    implied_volatility_30d: Optional[float]
    iv_rank: Optional[float]
    short_interest_pct: Optional[float]
    short_interest_ratio_days_to_cover: Optional[float]
    borrow_rate: Optional[float] = None   # Not available on free tier

    def to_dict(self) -> dict:
        return self.__dict__.copy()


# ─────────────────────────────────────────────────────────────────────────────
#  Internal cache helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cache_key(identifier: str) -> Path:
    h = hashlib.md5(identifier.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"opts_{h}.json"


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
#  Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _require_yfinance() -> None:
    if not _YFINANCE_AVAILABLE:
        raise ImportError("yfinance is not installed. Run: pip install yfinance")


def _safe_float(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        f = float(value)  # type: ignore[arg-type]
        return None if (f != f) else f  # NaN guard
    except (TypeError, ValueError):
        return None


def _yf_ticker(ticker: str) -> "yf.Ticker":  # type: ignore[name-defined]
    """Return a validated yfinance Ticker, raising TickerNotFound for unknown symbols."""
    _require_yfinance()
    t = yf.Ticker(ticker.upper())  # type: ignore[union-attr]
    info = t.info
    if not info or (info.get("quoteType") is None and info.get("shortName") is None):
        raise TickerNotFound(
            f"No data found for ticker '{ticker}'. "
            "Check the symbol and ensure it is listed on a US exchange."
        )
    return t


def _get_options_chain(t: "yf.Ticker", expiry: str) -> tuple["pd.DataFrame", "pd.DataFrame"]:  # type: ignore[name-defined]
    """
    Return (calls_df, puts_df) for a given expiry string.
    Both DataFrames have columns: strike, lastPrice, bid, ask, volume, openInterest, impliedVolatility.
    Empty DataFrames are returned on failure.
    """
    if not _PANDAS_AVAILABLE:
        return pd.DataFrame(), pd.DataFrame()  # type: ignore[union-attr]

    try:
        chain = t.option_chain(expiry)
        calls = chain.calls.copy() if chain.calls is not None else pd.DataFrame()  # type: ignore[union-attr]
        puts = chain.puts.copy() if chain.puts is not None else pd.DataFrame()    # type: ignore[union-attr]
        # Normalise column names (yfinance returns camelCase sometimes)
        return calls, puts
    except Exception as exc:
        logger.debug("option_chain fetch failed for expiry %s: %s", expiry, exc)
        return pd.DataFrame(), pd.DataFrame()  # type: ignore[union-attr]


def _atm_iv(calls: "pd.DataFrame", puts: "pd.DataFrame", spot: float) -> Optional[float]:
    """
    Estimate the at-the-money 30-day implied volatility.

    Method: average the impliedVolatility of the 3 call strikes closest to
    spot and the 3 put strikes closest to spot, then take the mean.
    This approximates the ATM vol without requiring a full options model.

    Returns IV as a percentage (e.g. 45.3 for 45.3% annualised vol).
    """
    if not _PANDAS_AVAILABLE or calls.empty or puts.empty:
        return None

    ivs: list[float] = []

    for df in (calls, puts):
        if "strike" not in df.columns or "impliedVolatility" not in df.columns:
            continue
        df_valid = df[df["impliedVolatility"].notna() & (df["impliedVolatility"] > 0)].copy()
        if df_valid.empty:
            continue
        df_valid = df_valid.copy()
        df_valid["dist"] = (df_valid["strike"] - spot).abs()
        nearest = df_valid.nsmallest(3, "dist")
        ivs.extend(nearest["impliedVolatility"].tolist())

    if not ivs:
        return None

    # yfinance returns IV as a decimal (0.453 = 45.3%); convert to percent
    avg_iv = sum(ivs) / len(ivs)
    return round(avg_iv * 100, 2)


def _aggregate_oi(
    all_calls: list["pd.DataFrame"],
    all_puts: list["pd.DataFrame"],
) -> tuple[int, int]:
    """Sum total open interest across all expiries for calls and puts."""
    if not _PANDAS_AVAILABLE:
        return 0, 0

    def _sum_oi(frames: list["pd.DataFrame"]) -> int:
        total = 0
        for df in frames:
            if df.empty or "openInterest" not in df.columns:
                continue
            total += int(df["openInterest"].fillna(0).sum())
        return total

    return _sum_oi(all_calls), _sum_oi(all_puts)


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def iv_rank(ticker: str, lookback_days: int = 365) -> Optional[float]:
    """
    Compute the current IV rank (IV percentile) vs. the past `lookback_days`.

    yfinance does not provide historical implied volatility directly. We use
    a proxy: 20-day realised (historical) volatility computed from close-to-
    close log returns, then track its percentile over the lookback period.

    This is NOT the same as true IV rank (which requires options chain history)
    but is a reasonable free-tier approximation. For true IV rank:
      - Market Chameleon (web): free, no API
      - Unusual Whales / CheddarFlow: paid, API available

    Args:
        ticker:        Stock symbol.
        lookback_days: Days of price history to compute rank against.

    Returns:
        IV rank as a float 0–100 (e.g. 72.4 = IV is at the 72nd percentile).
        None if insufficient data.

    Raises:
        TickerNotFound: If ticker is unknown.
    """
    ticker = ticker.upper().strip()
    cache_path = _cache_key(f"ivrank:{ticker}:{lookback_days}")
    cached = _cache_read(cache_path, _LIVE_TTL)
    if cached and "iv_rank" in cached:
        return cached["iv_rank"]

    _require_yfinance()
    t = _yf_ticker(ticker)

    # Download ~1.5 years of daily closes to get lookback_days of vol measurements
    fetch_days = lookback_days + 60
    period_years = max(2, (fetch_days // 365) + 1)

    try:
        df = yf.download(  # type: ignore[union-attr]
            ticker,
            period=f"{period_years}y",
            progress=False,
            auto_adjust=True,
        )
    except Exception as exc:
        logger.warning("iv_rank: price download failed for %s: %s", ticker, exc)
        return None

    if df.empty or len(df) < 30:
        return None

    if _PANDAS_AVAILABLE and isinstance(df.columns, pd.MultiIndex):  # type: ignore[union-attr]
        df.columns = df.columns.get_level_values(0)

    close = df["Close"].dropna()

    if len(close) < 30:
        return None

    # 20-day realised vol (annualised) as proxy for IV
    if _NUMPY_AVAILABLE and _PANDAS_AVAILABLE:
        log_ret = close.pct_change().apply(lambda x: float(np.log(1 + x)) if x is not None and x == x else float('nan'))  # type: ignore[union-attr]
        rolling_vol = log_ret.rolling(20).std() * float(np.sqrt(252)) * 100  # type: ignore[union-attr]
        rolling_vol = rolling_vol.dropna()
    else:
        # stdlib fallback: compute rolling std manually
        import math
        prices = list(close)
        log_rets = [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices)) if prices[i - 1] > 0]
        window = 20
        vols: list[float] = []
        for i in range(window, len(log_rets) + 1):
            w = log_rets[i - window:i]
            mean = sum(w) / len(w)
            variance = sum((x - mean) ** 2 for x in w) / (len(w) - 1)
            vols.append(math.sqrt(variance) * math.sqrt(252) * 100)
        rolling_vol = vols  # type: ignore[assignment]

    if _PANDAS_AVAILABLE and hasattr(rolling_vol, "__len__"):
        vol_series = list(rolling_vol)
    else:
        vol_series = rolling_vol  # type: ignore[assignment]

    if not vol_series or len(vol_series) < 2:
        return None

    # Limit to the requested lookback window
    vol_window = vol_series[-lookback_days:] if len(vol_series) > lookback_days else vol_series
    current_vol = vol_window[-1]

    vol_min = min(vol_window)
    vol_max = max(vol_window)

    if vol_max == vol_min:
        return 50.0  # Flat vol history — rank is indeterminate, return midpoint

    rank = round((current_vol - vol_min) / (vol_max - vol_min) * 100, 1)
    result = max(0.0, min(100.0, rank))

    _cache_write(cache_path, {"iv_rank": result, "current_vol_pct": round(current_vol, 2)})
    return result


def get_options_snapshot(ticker: str) -> OptionsSnapshot:
    """
    Pull current options chain from yfinance and compute a market-microstructure
    summary: put/call OI ratio, ATM IV, IV rank, and short interest.

    Process:
    1. Fetch all available option expiries via yfinance.
    2. For each expiry, download calls + puts DataFrames.
    3. Aggregate total call OI and total put OI for the put/call ratio.
    4. Find the nearest expiry >= 20 days out for ATM IV estimation.
    5. Pull short interest % and days-to-cover from yfinance info dict.
    6. Run iv_rank() for the IV percentile.

    Note on free-tier limitations:
      yfinance options chains refresh approximately every 15 minutes during
      market hours. OI figures are end-of-previous-day. Volume is intraday.

    Args:
        ticker: Stock symbol.

    Returns:
        OptionsSnapshot dataclass.

    Raises:
        TickerNotFound: If ticker is unknown.
    """
    ticker = ticker.upper().strip()

    cache_path = _cache_key(f"snapshot:{ticker}")
    cached = _cache_read(cache_path, _LIVE_TTL)
    if cached:
        try:
            return OptionsSnapshot(**cached)
        except Exception:
            pass

    t = _yf_ticker(ticker)

    # Spot price and short interest from info dict
    info = t.info
    spot = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    si_pct = _safe_float(info.get("shortPercentOfFloat"))
    if si_pct is not None:
        si_pct = round(si_pct * 100, 2)  # yfinance returns decimal (0.05 = 5%)
    dtc = _safe_float(info.get("shortRatio"))  # days-to-cover

    # Fetch all expiries
    try:
        expiries = t.options  # tuple of "YYYY-MM-DD" strings
    except Exception as exc:
        logger.warning("get_options_snapshot: could not fetch expiry list for %s: %s", ticker, exc)
        expiries = ()

    all_calls: list["pd.DataFrame"] = []  # type: ignore[name-defined]
    all_puts: list["pd.DataFrame"] = []   # type: ignore[name-defined]
    atm_iv_expiry_calls = None
    atm_iv_expiry_puts = None
    today = date.today()

    for expiry_str in expiries:
        try:
            expiry_date = date.fromisoformat(expiry_str)
        except ValueError:
            continue

        calls_df, puts_df = _get_options_chain(t, expiry_str)
        all_calls.append(calls_df)
        all_puts.append(puts_df)

        # Choose the first expiry that is >= 20 days out for ATM IV
        if atm_iv_expiry_calls is None and (expiry_date - today).days >= 20:
            atm_iv_expiry_calls = calls_df
            atm_iv_expiry_puts = puts_df

    total_call_oi, total_put_oi = _aggregate_oi(all_calls, all_puts)

    pc_ratio: Optional[float] = None
    if total_call_oi > 0:
        pc_ratio = round(total_put_oi / total_call_oi, 3)

    atm_iv: Optional[float] = None
    if spot and atm_iv_expiry_calls is not None and atm_iv_expiry_puts is not None:
        atm_iv = _atm_iv(atm_iv_expiry_calls, atm_iv_expiry_puts, spot)

    ivr = iv_rank(ticker)

    snapshot = OptionsSnapshot(
        ticker=ticker,
        timestamp=datetime.now(timezone.utc).isoformat(),
        spot_price=spot,
        put_call_ratio=pc_ratio,
        total_call_oi=total_call_oi,
        total_put_oi=total_put_oi,
        implied_volatility_30d=atm_iv,
        iv_rank=ivr,
        short_interest_pct=si_pct,
        short_interest_ratio_days_to_cover=dtc,
        borrow_rate=None,  # Not available on free tier
    )

    _cache_write(cache_path, snapshot.to_dict())
    return snapshot


def unusual_activity(
    ticker: str,
    threshold_multiplier: float = 3.0,
) -> list[dict]:
    """
    Detect unusual options activity using a naive volume-vs-OI heuristic.

    Definition of "unusual": a strike where today's volume is >= `threshold_multiplier`
    times the existing open interest AND both volume and OI exceed `_MIN_OI` (500).
    This filters for strikes where new positioning (volume) dramatically exceeds
    the existing outstanding contracts (OI) — a sign of large fresh bets.

    Limitation of free-tier detection:
      This approach catches end-of-day summary signals but CANNOT detect:
        - Real-time sweeps across multiple exchanges (requires Unusual Whales/CheddarFlow)
        - Dark pool prints (requires FlowAlgo or institutional data)
        - Block trades vs. retail order flow split
        - Whether the trade was a buy or sell to open (requires quote data)
      Upgrade path: Unusual Whales API ($48/mo) provides sweep detection,
      sentiment, and individual trade-level data.

    Args:
        ticker:               Stock symbol.
        threshold_multiplier: Volume / OI ratio to flag as unusual (default 3.0x).

    Returns:
        List of dicts, each containing:
          expiry, strike, option_type ("call" | "put"), volume, open_interest,
          volume_oi_ratio, implied_volatility (%), note.
        Sorted by volume_oi_ratio descending (most unusual first).

    Raises:
        TickerNotFound: If ticker is unknown.
    """
    ticker = ticker.upper().strip()

    if not _PANDAS_AVAILABLE:
        logger.warning("unusual_activity requires pandas. Run: pip install pandas")
        return []

    t = _yf_ticker(ticker)

    try:
        expiries = t.options
    except Exception:
        return []

    unusual: list[dict] = []
    today = date.today()

    for expiry_str in expiries[:8]:   # Limit scan to near-term expiries (reduces API calls)
        try:
            expiry_date = date.fromisoformat(expiry_str)
        except ValueError:
            continue

        # Skip expired options
        if expiry_date <= today:
            continue

        calls_df, puts_df = _get_options_chain(t, expiry_str)

        for opt_type, df in (("call", calls_df), ("put", puts_df)):
            if df.empty:
                continue
            if "volume" not in df.columns or "openInterest" not in df.columns:
                continue

            df_valid = df[
                df["volume"].notna() &
                df["openInterest"].notna() &
                (df["volume"] >= _MIN_VOLUME) &
                (df["openInterest"] >= _MIN_OI)
            ].copy()

            if df_valid.empty:
                continue

            df_valid["vol_oi_ratio"] = df_valid["volume"] / df_valid["openInterest"]
            flagged = df_valid[df_valid["vol_oi_ratio"] >= threshold_multiplier]

            for _, row in flagged.iterrows():
                iv_pct = None
                raw_iv = row.get("impliedVolatility")
                if raw_iv is not None:
                    iv_f = _safe_float(raw_iv)
                    if iv_f is not None:
                        iv_pct = round(iv_f * 100, 1)

                unusual.append({
                    "expiry": expiry_str,
                    "strike": float(row.get("strike", 0)),
                    "option_type": opt_type,
                    "volume": int(row.get("volume", 0)),
                    "open_interest": int(row.get("openInterest", 0)),
                    "volume_oi_ratio": round(float(row["vol_oi_ratio"]), 2),
                    "implied_volatility_pct": iv_pct,
                    "note": (
                        f"{opt_type.upper()} volume is {row['vol_oi_ratio']:.1f}x "
                        f"open interest at ${row['strike']:.2f} exp {expiry_str}"
                    ),
                })

    unusual.sort(key=lambda x: x["volume_oi_ratio"], reverse=True)
    return unusual


def squeeze_score(ticker: str) -> dict:
    """
    Compute a short squeeze setup score (0–10) using the classic mechanics.

    The short squeeze playbook (inverse of the short-seller's thesis):
      1. High short interest (> 20% of float) — enough fuel for a squeeze
      2. High days-to-cover (> 3 days) — shorts can't exit quickly; forced buying
         amplifies the move
      3. RSI trending upward from oversold — momentum is turning
      4. Stock near 52-week low reclaiming structure — short thesis failing

    Scoring (additive):
      Short interest > 10%:  +1  (notable positioning)
      Short interest > 20%:  +2  (high conviction shorts — more squeeze fuel)
      Days-to-cover  >  2:   +1
      Days-to-cover  >  3:   +2  (classic squeeze threshold)
      RSI(14)        < 35:   +1  (historically oversold — mean reversion candidate)
      RSI trending up 5d:    +1  (momentum turning)
      52-week low within 15%:+1  (short thesis worked — but reclaim = trap)
      Stock reclaiming SMA50:+1  (structural break forcing shorts to cover)

    Academic references:
      Asquith, Pathak & Ritter (2005): "Short Interest, Institutional Ownership,
        and Stock Returns" — high SI + low institutional coverage → extreme returns.
      Boehmer, Jones & Zhang (2008): "Which Shorts Are Informed?" — distinguishes
        informed vs. mechanical short covering.

    Carson Block / Chanos note: This score measures the INVERSE of their thesis.
    They look for SI rising + stock falling. We look for SI high + stock turning.

    Args:
        ticker: Stock symbol.

    Returns:
        Dict:
          short_interest_pct, days_to_cover, rsi, borrow_rate (None free tier),
          score (0–10), signal ("high_squeeze_potential" | "moderate" | "low"),
          notes: list of human-readable factors.

    Raises:
        TickerNotFound: If ticker is unknown.
    """
    ticker = ticker.upper().strip()

    cache_path = _cache_key(f"squeeze:{ticker}")
    cached = _cache_read(cache_path, _LIVE_TTL)
    if cached and "score" in cached:
        return cached

    t = _yf_ticker(ticker)
    info = t.info

    si_pct_raw = _safe_float(info.get("shortPercentOfFloat"))
    si_pct = round(si_pct_raw * 100, 2) if si_pct_raw is not None else None
    dtc = _safe_float(info.get("shortRatio"))

    # RSI and 52-week positioning from price history
    rsi_val: Optional[float] = None
    rsi_trending_up: bool = False
    near_52w_low: bool = False
    reclaiming_sma50: bool = False

    try:
        df = yf.download(  # type: ignore[union-attr]
            ticker, period="1y", progress=False, auto_adjust=True
        )
        if not df.empty:
            if _PANDAS_AVAILABLE and isinstance(df.columns, pd.MultiIndex):  # type: ignore[union-attr]
                df.columns = df.columns.get_level_values(0)

            close = df["Close"].dropna()

            if len(close) >= 14:
                # RSI(14) — manual implementation (mirrors fundamentals.py)
                delta = close.diff()
                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)
                avg_gain = gain.ewm(com=13, min_periods=14).mean()
                avg_loss = loss.ewm(com=13, min_periods=14).mean()
                avg_loss_safe = avg_loss.replace(0, float("nan"))
                rs = avg_gain / avg_loss_safe
                rsi_series = 100 - (100 / (1 + rs))
                rsi_val = round(float(rsi_series.iloc[-1]), 1)

                # Check if RSI is trending up over last 5 sessions
                if len(rsi_series) >= 5:
                    rsi_5d_ago = float(rsi_series.iloc[-5])
                    rsi_trending_up = bool(rsi_val > rsi_5d_ago)

            if len(close) >= 252:
                lookback = 252
            else:
                lookback = len(close)

            w52_low = float(close.iloc[-lookback:].min())
            spot = float(close.iloc[-1])
            near_52w_low = bool(spot <= w52_low * 1.15)  # within 15% of 52w low

            if len(close) >= 50:
                sma50 = float(close.rolling(50).mean().iloc[-1])
                reclaiming_sma50 = bool(spot >= sma50 * 0.98)  # at or above 98% of SMA50
    except Exception as exc:
        logger.warning("squeeze_score: price analysis failed for %s: %s", ticker, exc)

    # ── Score calculation ──────────────────────────────────────────────────
    score = 0
    notes: list[str] = []

    if si_pct is not None:
        if si_pct > 20:
            score += 2
            notes.append(f"High short interest: {si_pct:.1f}% of float (+2)")
        elif si_pct > 10:
            score += 1
            notes.append(f"Notable short interest: {si_pct:.1f}% of float (+1)")
        else:
            notes.append(f"Low short interest: {si_pct:.1f}% of float — squeeze unlikely")
    else:
        notes.append("Short interest data unavailable")

    if dtc is not None:
        if dtc > 3:
            score += 2
            notes.append(f"Days-to-cover {dtc:.1f} > 3 — shorts trapped (+2)")
        elif dtc > 2:
            score += 1
            notes.append(f"Days-to-cover {dtc:.1f} > 2 — notable coverage risk (+1)")
        else:
            notes.append(f"Days-to-cover {dtc:.1f} — shorts can exit quickly")
    else:
        notes.append("Days-to-cover data unavailable")

    if rsi_val is not None:
        if rsi_val < 35:
            score += 1
            notes.append(f"RSI {rsi_val:.0f} — historically oversold (+1)")
        if rsi_trending_up:
            score += 1
            notes.append("RSI trending up over last 5 sessions — momentum turning (+1)")

    if near_52w_low:
        score += 1
        notes.append("Price within 15% of 52-week low — short thesis worked, reversal risk (+1)")

    if reclaiming_sma50:
        score += 1
        notes.append("Price at/above 50-day SMA — structural breakout forcing short covering (+1)")

    score = min(10, score)

    if score >= 7:
        signal = "high_squeeze_potential"
    elif score >= 4:
        signal = "moderate"
    else:
        signal = "low"

    result = {
        "ticker": ticker,
        "short_interest_pct": si_pct,
        "days_to_cover": dtc,
        "rsi": rsi_val,
        "borrow_rate": None,   # Requires IBKR or S3 Partners subscription
        "score": score,
        "signal": signal,
        "notes": notes,
    }

    _cache_write(cache_path, result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def _cli() -> None:
    """
    CLI usage:
        python -m research.options_flow NVDA
        python -m research.options_flow AAPL --threshold 5.0
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Atlas Options Flow — snapshot, squeeze score, unusual activity",
    )
    parser.add_argument("ticker", help="Ticker symbol (e.g. NVDA)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        help="Unusual activity volume/OI multiplier threshold (default: 3.0)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    ticker = args.ticker.upper()

    print(f"\n{'='*60}")
    print(f"  OPTIONS FLOW ANALYSIS — {ticker}")
    print(f"{'='*60}\n")

    # Snapshot
    print("[ OPTIONS SNAPSHOT ]")
    try:
        snap = get_options_snapshot(ticker)
        spot_str = f"${snap.spot_price:.2f}" if snap.spot_price else "n/a"
        pc_str = f"{snap.put_call_ratio:.3f}" if snap.put_call_ratio is not None else "n/a"
        iv_str = f"{snap.implied_volatility_30d:.1f}%" if snap.implied_volatility_30d is not None else "n/a"
        ivr_str = f"{snap.iv_rank:.1f}" if snap.iv_rank is not None else "n/a"
        si_str = f"{snap.short_interest_pct:.1f}%" if snap.short_interest_pct is not None else "n/a"
        dtc_str = f"{snap.short_interest_ratio_days_to_cover:.1f}" if snap.short_interest_ratio_days_to_cover is not None else "n/a"

        print(f"  Spot price:          {spot_str}")
        print(f"  Put/Call OI ratio:   {pc_str}  (>1.0 = more puts)")
        print(f"  Total call OI:       {snap.total_call_oi:,}")
        print(f"  Total put OI:        {snap.total_put_oi:,}")
        print(f"  ATM IV (30d proxy):  {iv_str}")
        print(f"  IV rank (1-year):    {ivr_str} / 100  {'[expensive — sell premium]' if snap.iv_rank and snap.iv_rank > 80 else '[cheap — buy options]' if snap.iv_rank and snap.iv_rank < 20 else ''}")
        print(f"  Short interest:      {si_str}")
        print(f"  Days to cover:       {dtc_str}")
        print(f"  Borrow rate:         n/a (requires IBKR / S3 Partners subscription)")
        print(f"  Timestamp:           {snap.timestamp}")
    except TickerNotFound as exc:
        print(f"  ERROR: {exc}")
        return
    except Exception as exc:
        print(f"  ERROR fetching snapshot: {exc}")
        return

    # Squeeze score
    print(f"\n[ SQUEEZE SCORE ]")
    try:
        sq = squeeze_score(ticker)
        bar = "#" * sq["score"] + "-" * (10 - sq["score"])
        print(f"  Score:  {sq['score']}/10  [{bar}]  {sq['signal'].upper()}")
        print(f"\n  Factors:")
        for note in sq["notes"]:
            print(f"    - {note}")
    except Exception as exc:
        print(f"  ERROR: {exc}")

    # Unusual activity
    print(f"\n[ UNUSUAL OPTIONS ACTIVITY ]  (volume/{args.threshold:.1f}x OI, min OI/vol {_MIN_OI})")
    try:
        unusual = unusual_activity(ticker, threshold_multiplier=args.threshold)
        if not unusual:
            print(f"  No unusual activity detected at {args.threshold}x threshold.")
        else:
            print(f"  Found {len(unusual)} unusual strikes:\n")
            print(f"  {'Expiry':<12} {'Strike':>8} {'Type':<6} {'Volume':>8} {'OI':>8} {'Vol/OI':>7} {'IV':>8}")
            print("  " + "-" * 62)
            for item in unusual[:15]:   # Cap display at 15 rows
                iv_disp = f"{item['implied_volatility_pct']:.1f}%" if item["implied_volatility_pct"] else "n/a"
                print(
                    f"  {item['expiry']:<12} "
                    f"{item['strike']:>8.2f} "
                    f"{item['option_type']:<6} "
                    f"{item['volume']:>8,} "
                    f"{item['open_interest']:>8,} "
                    f"{item['volume_oi_ratio']:>6.1f}x "
                    f"{iv_disp:>8}"
                )
    except Exception as exc:
        print(f"  ERROR: {exc}")

    # Paid upgrade note
    print(f"""
[ PAID UPGRADE NOTE ]
  For institutional-grade unusual flow detection:
    - Unusual Whales ($48/mo)  — real-time sweeps, dark pool, Congress trades
    - CheddarFlow ($50/mo)     — live whale score, expiry heat maps
    - FlowAlgo ($199/mo)       — professional prop-desk level
    - Market Chameleon (free)  — manual IV rank lookup (no API)
  Current module uses end-of-day yfinance data only.
""")


if __name__ == "__main__":
    _cli()
