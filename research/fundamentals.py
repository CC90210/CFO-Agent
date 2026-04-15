"""
research/fundamentals.py
------------------------
Company fundamentals, price history, and technical indicators for Atlas Research.

Data sources (in priority order):
1. yfinance (Yahoo Finance) — free, no key required, ~2000 req/day before throttling
2. Alpha Vantage — 25 req/day free (ALPHA_VANTAGE_KEY in .env)
3. Financial Modeling Prep — 250 req/day free (FMP_KEY in .env)

Caching:
- Fundamentals: 24 hours (data is slow-moving)
- Price history: 1 hour (used for technicals)

Technicals are computed directly from price DataFrames using pandas/numpy —
no external TA library required (though pandas_ta is used if available for
more accurate indicator implementations).
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

import numpy as np
import pandas as pd
import requests

try:
    import yfinance as yf
    _YFINANCE_AVAILABLE = True
except ImportError:
    _YFINANCE_AVAILABLE = False
    yf = None  # type: ignore[assignment]

try:
    import pandas_ta as ta  # type: ignore[import-untyped]
    _PANDAS_TA_AVAILABLE = True
except ImportError:
    _PANDAS_TA_AVAILABLE = False

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Cache configuration
# ─────────────────────────────────────────────────────────────────────────────

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_FUNDAMENTALS_TTL = 86400   # 24 hours
_PRICE_TTL = 3600           # 1 hour


def _cache_key(identifier: str) -> Path:
    h = hashlib.md5(identifier.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"fund_{h}.json"


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
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    except OSError as exc:
        logger.warning("Cache write failed for %s: %s", path, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Fundamentals:
    """Key fundamental metrics for a single equity."""

    ticker: str
    name: str
    sector: str
    industry: str
    market_cap: Optional[float] = None          # USD
    pe_ratio: Optional[float] = None            # trailing P/E
    forward_pe: Optional[float] = None
    ps_ratio: Optional[float] = None            # price/sales
    peg_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None            # price/book
    ev_ebitda: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None      # annual FCF in USD
    fcf_yield: Optional[float] = None           # FCF / market cap (%)
    revenue_growth_yoy: Optional[float] = None  # % YoY
    earnings_growth_yoy: Optional[float] = None
    operating_margin: Optional[float] = None    # %
    net_margin: Optional[float] = None
    roe: Optional[float] = None                 # return on equity %
    short_interest_pct: Optional[float] = None  # % of float
    insider_buy_sell_ratio_90d: Optional[float] = None  # >1 bullish
    institutional_ownership_pct: Optional[float] = None
    analyst_rating: Optional[str] = None        # "Buy" | "Hold" | "Sell"
    analyst_target_price: Optional[float] = None
    currency: str = "USD"
    data_source: str = "yfinance"
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, d: dict) -> "Fundamentals":
        # Remove keys not in the dataclass to be forward-compatible
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)

    def valuation_summary(self) -> str:
        """Return a human-readable one-liner valuation summary."""
        parts = []
        if self.pe_ratio:
            parts.append(f"P/E: {self.pe_ratio:.1f}x")
        if self.forward_pe:
            parts.append(f"FWD P/E: {self.forward_pe:.1f}x")
        if self.ps_ratio:
            parts.append(f"P/S: {self.ps_ratio:.1f}x")
        if self.peg_ratio:
            parts.append(f"PEG: {self.peg_ratio:.2f}")
        if self.fcf_yield:
            parts.append(f"FCF yield: {self.fcf_yield:.1f}%")
        if self.revenue_growth_yoy:
            parts.append(f"Rev growth: {self.revenue_growth_yoy:.1f}%")
        return " | ".join(parts) if parts else "Limited data available"


# ─────────────────────────────────────────────────────────────────────────────
#  Fundamentals fetcher
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_yfinance(ticker: str) -> Optional[Fundamentals]:
    """Pull fundamentals from yfinance (Yahoo Finance)."""
    if not _YFINANCE_AVAILABLE:
        logger.warning("yfinance not installed — run: pip install yfinance")
        return None

    try:
        t = yf.Ticker(ticker)
        info = t.info
    except Exception as exc:
        logger.warning("yfinance fundamentals failed for %s: %s", ticker, exc)
        return None

    if not info or info.get("quoteType") is None:
        return None

    market_cap = info.get("marketCap")
    fcf = info.get("freeCashflow")
    fcf_yield = None
    if fcf and market_cap and market_cap > 0:
        fcf_yield = round((fcf / market_cap) * 100, 2)

    # Insider buy/sell ratio (90d) — yfinance provides 6-month insider data
    insider_ratio: Optional[float] = None
    try:
        insider = t.insider_purchases
        if insider is not None and not insider.empty:
            buys = insider[insider.get("Transaction", "").str.contains("Buy", na=False)]
            sells = insider[insider.get("Transaction", "").str.contains("Sell", na=False)]
            buy_shares = buys["Shares"].sum() if "Shares" in buys.columns else 0
            sell_shares = sells["Shares"].sum() if "Shares" in sells.columns else 0
            if sell_shares > 0:
                insider_ratio = round(buy_shares / sell_shares, 2)
            elif buy_shares > 0:
                insider_ratio = 999.0  # All buys, no sells
    except Exception:
        pass

    return Fundamentals(
        ticker=ticker.upper(),
        name=info.get("longName", ticker),
        sector=info.get("sector", "Unknown"),
        industry=info.get("industry", "Unknown"),
        market_cap=market_cap,
        pe_ratio=info.get("trailingPE"),
        forward_pe=info.get("forwardPE"),
        ps_ratio=info.get("priceToSalesTrailing12Months"),
        peg_ratio=info.get("pegRatio"),
        pb_ratio=info.get("priceToBook"),
        ev_ebitda=info.get("enterpriseToEbitda"),
        debt_to_equity=info.get("debtToEquity"),
        current_ratio=info.get("currentRatio"),
        free_cash_flow=fcf,
        fcf_yield=fcf_yield,
        revenue_growth_yoy=round(info.get("revenueGrowth", 0) * 100, 2) if info.get("revenueGrowth") else None,
        earnings_growth_yoy=round(info.get("earningsGrowth", 0) * 100, 2) if info.get("earningsGrowth") else None,
        operating_margin=round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else None,
        net_margin=round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else None,
        roe=round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else None,
        short_interest_pct=round(info.get("shortPercentOfFloat", 0) * 100, 2) if info.get("shortPercentOfFloat") else None,
        insider_buy_sell_ratio_90d=insider_ratio,
        institutional_ownership_pct=round(info.get("heldPercentInstitutions", 0) * 100, 2) if info.get("heldPercentInstitutions") else None,
        analyst_rating=info.get("recommendationKey", "").replace("_", " ").title() or None,
        analyst_target_price=info.get("targetMeanPrice"),
        currency=info.get("currency", "USD"),
        data_source="yfinance",
    )


def _fetch_alpha_vantage_overview(ticker: str) -> Optional[dict]:
    """Pull company overview from Alpha Vantage (25 req/day free)."""
    api_key = os.environ.get("ALPHA_VANTAGE_KEY", "")
    if not api_key:
        return None

    cache_path = _cache_key(f"av_overview:{ticker.upper()}")
    cached = _cache_read(cache_path, _FUNDAMENTALS_TTL)
    if cached:
        return cached

    try:
        resp = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "OVERVIEW", "symbol": ticker.upper(), "apikey": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Alpha Vantage overview failed for %s: %s", ticker, exc)
        return None

    if "Symbol" not in data:
        return None

    _cache_write(cache_path, data)
    return data


def _fetch_fmp_profile(ticker: str) -> Optional[dict]:
    """Pull company profile from Financial Modeling Prep (250 req/day free)."""
    api_key = os.environ.get("FMP_KEY", "")
    if not api_key:
        return None

    cache_path = _cache_key(f"fmp_profile:{ticker.upper()}")
    cached = _cache_read(cache_path, _FUNDAMENTALS_TTL)
    if cached:
        return cached

    try:
        resp = requests.get(
            f"https://financialmodelingprep.com/api/v3/profile/{ticker.upper()}",
            params={"apikey": api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("FMP profile failed for %s: %s", ticker, exc)
        return None

    if not data or not isinstance(data, list):
        return None

    _cache_write(cache_path, data[0])
    return data[0]


def get_fundamentals(ticker: str) -> Fundamentals:
    """
    Fetch fundamental metrics for a ticker.

    Waterfall:
    1. yfinance (always tried first — no quota)
    2. Alpha Vantage enrichment if ALPHA_VANTAGE_KEY is set
    3. FMP enrichment if FMP_KEY is set

    Results cached 24 hours.
    """
    cache_path = _cache_key(f"fundamentals:{ticker.upper()}")
    cached = _cache_read(cache_path, _FUNDAMENTALS_TTL)
    if cached:
        try:
            return Fundamentals.from_dict(cached)
        except Exception:
            pass

    fund = _fetch_yfinance(ticker)
    if fund is None:
        # Return a stub rather than crashing the pipeline
        logger.warning("All fundamentals sources failed for %s — returning stub", ticker)
        fund = Fundamentals(
            ticker=ticker.upper(),
            name=ticker.upper(),
            sector="Unknown",
            industry="Unknown",
            data_source="stub",
        )

    # Enrich with Alpha Vantage if available and yfinance had gaps
    av_data = _fetch_alpha_vantage_overview(ticker)
    if av_data:
        if fund.pe_ratio is None and av_data.get("PERatio") not in (None, "None", "-"):
            try:
                fund.pe_ratio = float(av_data["PERatio"])
            except (ValueError, TypeError):
                pass
        if fund.analyst_target_price is None and av_data.get("AnalystTargetPrice") not in (None, "None", "-"):
            try:
                fund.analyst_target_price = float(av_data["AnalystTargetPrice"])
            except (ValueError, TypeError):
                pass

    _cache_write(cache_path, fund.to_dict())
    return fund


# ─────────────────────────────────────────────────────────────────────────────
#  Price history
# ─────────────────────────────────────────────────────────────────────────────

def get_price_history(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch OHLCV price history from yfinance.

    Args:
        ticker: Stock ticker symbol.
        period: yfinance period string ("1y", "2y", "5y", "max", etc.)

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume, Adj Close.
        Empty DataFrame if fetching fails.
    """
    if not _YFINANCE_AVAILABLE:
        logger.warning("yfinance not installed — cannot fetch price history")
        return pd.DataFrame()

    cache_path = _cache_key(f"prices:{ticker.upper()}:{period}")
    # Cache as CSV inside the JSON cache (store as dict with "csv" key)
    cached = _cache_read(cache_path, _PRICE_TTL)
    if cached and "csv" in cached:
        try:
            import io
            return pd.read_csv(io.StringIO(cached["csv"]), index_col=0, parse_dates=True)
        except Exception:
            pass

    try:
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    except Exception as exc:
        logger.warning("yfinance price history failed for %s: %s", ticker, exc)
        return pd.DataFrame()

    if df.empty:
        return df

    # Flatten MultiIndex columns if present (yfinance sometimes returns MultiIndex)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    _cache_write(cache_path, {"csv": df.to_csv()})
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  Technical indicators
# ─────────────────────────────────────────────────────────────────────────────

def _sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window).mean()


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


def _macd(series: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns (macd_line, signal_line, histogram)."""
    ema12 = _ema(series, 12)
    ema26 = _ema(series, 26)
    macd_line = ema12 - ema26
    signal = _ema(macd_line, 9)
    histogram = macd_line - signal
    return macd_line, signal, histogram


def technicals(df: pd.DataFrame) -> dict:
    """
    Compute key technical indicators from an OHLCV DataFrame.

    Returns a dict with:
    - sma_50, sma_200: latest values
    - price_vs_sma50_pct, price_vs_sma200_pct: how far price is from each SMA
    - rsi_14: current RSI
    - macd, macd_signal, macd_histogram: current MACD values
    - week_52_high, week_52_low: range boundaries
    - price_vs_52wk_high_pct: % below 52-week high (buying opportunity metric)
    - volume_trend: "increasing" | "decreasing" | "flat" (vs 20-day average)
    - golden_cross: True if 50 SMA > 200 SMA (bullish long-term)
    - death_cross: True if 50 SMA < 200 SMA
    - trend: "uptrend" | "downtrend" | "sideways"
    """
    if df.empty or "Close" not in df.columns:
        return {}

    close = df["Close"].dropna()
    volume = df["Volume"].dropna() if "Volume" in df.columns else pd.Series(dtype=float)

    if len(close) < 20:
        return {}

    latest_price = float(close.iloc[-1])

    sma50 = _sma(close, 50)
    sma200 = _sma(close, 200)
    latest_sma50 = float(sma50.iloc[-1]) if not sma50.empty and not pd.isna(sma50.iloc[-1]) else None
    latest_sma200 = float(sma200.iloc[-1]) if not sma200.empty and not pd.isna(sma200.iloc[-1]) else None

    rsi = _rsi(close)
    latest_rsi = float(rsi.iloc[-1]) if not rsi.empty and not pd.isna(rsi.iloc[-1]) else None

    macd_line, signal_line, histogram = _macd(close)
    latest_macd = float(macd_line.iloc[-1]) if not macd_line.empty and not pd.isna(macd_line.iloc[-1]) else None
    latest_signal = float(signal_line.iloc[-1]) if not signal_line.empty and not pd.isna(signal_line.iloc[-1]) else None
    latest_hist = float(histogram.iloc[-1]) if not histogram.empty and not pd.isna(histogram.iloc[-1]) else None

    # 52-week high/low using last 252 trading days
    lookback = min(252, len(close))
    week_52_high = float(close.iloc[-lookback:].max())
    week_52_low = float(close.iloc[-lookback:].min())

    price_vs_52wk_high_pct = round((latest_price - week_52_high) / week_52_high * 100, 2) if week_52_high > 0 else None
    price_vs_sma50_pct = round((latest_price - latest_sma50) / latest_sma50 * 100, 2) if latest_sma50 else None
    price_vs_sma200_pct = round((latest_price - latest_sma200) / latest_sma200 * 100, 2) if latest_sma200 else None

    # Volume trend: compare last 5 days avg vs 20-day avg
    volume_trend = "unknown"
    if len(volume) >= 20:
        avg_5 = float(volume.iloc[-5:].mean())
        avg_20 = float(volume.iloc[-20:].mean())
        ratio = avg_5 / avg_20 if avg_20 > 0 else 1.0
        if ratio > 1.15:
            volume_trend = "increasing"
        elif ratio < 0.85:
            volume_trend = "decreasing"
        else:
            volume_trend = "flat"

    golden_cross = (latest_sma50 is not None and latest_sma200 is not None and latest_sma50 > latest_sma200)
    death_cross = (latest_sma50 is not None and latest_sma200 is not None and latest_sma50 < latest_sma200)

    # Trend classification
    if latest_sma50 and latest_sma200:
        if latest_price > latest_sma50 > latest_sma200:
            trend = "uptrend"
        elif latest_price < latest_sma50 < latest_sma200:
            trend = "downtrend"
        else:
            trend = "sideways"
    else:
        trend = "unknown"

    return {
        "latest_price": round(latest_price, 2),
        "sma_50": round(latest_sma50, 2) if latest_sma50 else None,
        "sma_200": round(latest_sma200, 2) if latest_sma200 else None,
        "price_vs_sma50_pct": price_vs_sma50_pct,
        "price_vs_sma200_pct": price_vs_sma200_pct,
        "rsi_14": round(latest_rsi, 1) if latest_rsi else None,
        "macd": round(latest_macd, 4) if latest_macd else None,
        "macd_signal": round(latest_signal, 4) if latest_signal else None,
        "macd_histogram": round(latest_hist, 4) if latest_hist else None,
        "week_52_high": round(week_52_high, 2),
        "week_52_low": round(week_52_low, 2),
        "price_vs_52wk_high_pct": price_vs_52wk_high_pct,
        "volume_trend": volume_trend,
        "golden_cross": golden_cross,
        "death_cross": death_cross,
        "trend": trend,
    }
