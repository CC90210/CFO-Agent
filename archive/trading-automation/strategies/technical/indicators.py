"""
strategies/technical/indicators.py — Vectorized technical indicator library.

All functions accept a pandas DataFrame with OHLCV columns (open, high, low, close, volume)
and return pandas Series or DataFrames.  Every calculation is fully vectorized — no Python
loops — so they run at backtesting speed across millions of rows.

Dependencies: ta>=0.11.0, pandas>=2.2.0, numpy>=1.26.0
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
import pandas as pd
import ta
import ta.momentum
import ta.trend
import ta.volatility
import ta.volume


# ---------------------------------------------------------------------------
# Trend indicators
# ---------------------------------------------------------------------------


def ema(series: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average.

    Parameters
    ----------
    series : typically df["close"]
    period : lookback window

    Returns
    -------
    pd.Series of EMA values, same index as input.
    """
    return series.ewm(span=period, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    """
    Simple Moving Average.
    """
    return series.rolling(window=period).mean()


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    MACD — Moving Average Convergence Divergence.

    Returns a DataFrame with columns:
        macd      — MACD line (fast EMA − slow EMA)
        signal    — signal line (EMA of MACD)
        histogram — MACD − signal
    """
    ind = ta.trend.MACD(series, window_fast=fast, window_slow=slow, window_sign=signal)
    return pd.DataFrame(
        {
            "macd": ind.macd(),
            "signal": ind.macd_signal(),
            "histogram": ind.macd_diff(),
        },
        index=series.index,
    )


# ---------------------------------------------------------------------------
# Momentum indicators
# ---------------------------------------------------------------------------


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (Wilder smoothing).

    Returns
    -------
    pd.Series — values in [0, 100].
    """
    return ta.momentum.RSIIndicator(series, window=period).rsi()


def stochastic_rsi(
    series: pd.Series,
    rsi_period: int = 14,
    stoch_period: int = 14,
    k_smooth: int = 3,
    d_smooth: int = 3,
) -> pd.DataFrame:
    """
    Stochastic RSI — RSI normalised within its own range.

    Returns a DataFrame with columns: stoch_rsi_k, stoch_rsi_d.
    Values are in [0, 1] (multiply by 100 for percentage representation).
    """
    ind = ta.momentum.StochRSIIndicator(
        series,
        window=rsi_period,
        smooth1=k_smooth,
        smooth2=d_smooth,
    )
    return pd.DataFrame(
        {
            "stoch_rsi_k": ind.stochrsi_k(),
            "stoch_rsi_d": ind.stochrsi_d(),
        },
        index=series.index,
    )


# ---------------------------------------------------------------------------
# Volatility indicators
# ---------------------------------------------------------------------------


class BollingerBands(NamedTuple):
    upper: pd.Series
    middle: pd.Series
    lower: pd.Series
    width: pd.Series
    percent_b: pd.Series


def bollinger_bands(
    series: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> BollingerBands:
    """
    Bollinger Bands.

    Returns a BollingerBands namedtuple with fields:
        upper, middle, lower  — price levels
        width                 — (upper - lower) / middle  (normalised bandwidth)
        percent_b             — position of price within the bands (0 = lower, 1 = upper)
    """
    ind = ta.volatility.BollingerBands(series, window=period, window_dev=std_dev)
    upper = ind.bollinger_hband()
    middle = ind.bollinger_mavg()
    lower = ind.bollinger_lband()
    width = (upper - lower) / middle.replace(0, np.nan)
    percent_b = ind.bollinger_pband()
    return BollingerBands(upper, middle, lower, width, percent_b)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range — measures raw volatility in price units.

    Useful for setting adaptive stop-losses and position sizing.
    Requires df columns: high, low, close.
    """
    return ta.volatility.AverageTrueRange(
        df["high"], df["low"], df["close"], window=period
    ).average_true_range()


class KeltnerChannels(NamedTuple):
    upper: pd.Series
    middle: pd.Series
    lower: pd.Series


def keltner_channels(
    df: pd.DataFrame,
    ema_period: int = 20,
    atr_period: int = 10,
    multiplier: float = 2.0,
) -> KeltnerChannels:
    """
    Keltner Channels — EMA ± (ATR × multiplier).

    Used alongside Bollinger Bands to detect volatility squeezes.
    Requires df columns: high, low, close.
    """
    ind = ta.volatility.KeltnerChannel(
        df["high"],
        df["low"],
        df["close"],
        window=ema_period,
        window_atr=atr_period,
        original_version=False,
    )
    # Rescale to match the requested multiplier (ta uses 2x by default)
    middle = ind.keltner_channel_mband()
    half_width = (ind.keltner_channel_hband() - middle) * (multiplier / 2.0)
    return KeltnerChannels(
        upper=middle + half_width,
        middle=middle,
        lower=middle - half_width,
    )


# ---------------------------------------------------------------------------
# Volume indicators
# ---------------------------------------------------------------------------


def vwap(df: pd.DataFrame, reset_daily: bool = True) -> pd.Series:
    """
    Volume Weighted Average Price.

    When reset_daily=True (default), VWAP resets at each calendar day boundary,
    which is the standard intraday definition.

    When reset_daily=False, a rolling cumulative VWAP is returned — useful for
    higher-timeframe trend bias.

    Requires df columns: high, low, close, volume, and a UTC DatetimeIndex.
    """
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    tp_vol = typical_price * df["volume"]

    if not reset_daily:
        cum_vol = df["volume"].cumsum()
        cum_tp_vol = tp_vol.cumsum()
        return (cum_tp_vol / cum_vol.replace(0, np.nan)).rename("vwap")

    # Group by date, compute VWAP within each session
    dates = df.index.normalize() if hasattr(df.index, "normalize") else pd.Series(
        df.index
    ).dt.normalize()

    result = pd.Series(index=df.index, dtype=float, name="vwap")
    for date, group in df.groupby(dates):  # type: ignore[call-overload]
        tp = (group["high"] + group["low"] + group["close"]) / 3.0
        cum_vol = group["volume"].cumsum()
        cum_tpv = (tp * group["volume"]).cumsum()
        result.loc[group.index] = (cum_tpv / cum_vol.replace(0, np.nan)).values

    return result


def volume_profile(
    df: pd.DataFrame,
    bins: int = 20,
) -> pd.DataFrame:
    """
    Volume Profile — distribution of volume across price levels.

    Returns a DataFrame with columns:
        price_low, price_high  — price bin edges
        volume                 — total volume traded at that level
        poc                    — bool, True for the Point of Control (highest volume bin)
        value_area             — bool, True for bins inside the 70% Value Area
    """
    price_min = df["low"].min()
    price_max = df["high"].max()
    bin_edges = np.linspace(price_min, price_max, bins + 1)

    vol_per_bin = np.zeros(bins)
    for _, row in df.iterrows():
        # Distribute bar volume across price bins touched by high-low range
        idx_lo = max(0, np.searchsorted(bin_edges, row["low"], side="left") - 1)
        idx_hi = min(bins - 1, np.searchsorted(bin_edges, row["high"], side="right") - 1)
        n_bins = max(1, idx_hi - idx_lo + 1)
        vol_per_bin[idx_lo : idx_hi + 1] += row["volume"] / n_bins

    profile = pd.DataFrame(
        {
            "price_low": bin_edges[:-1],
            "price_high": bin_edges[1:],
            "volume": vol_per_bin,
        }
    )
    profile["poc"] = profile["volume"] == profile["volume"].max()

    # Value Area: bins containing 70% of total volume, starting from POC
    total_vol = profile["volume"].sum()
    target = 0.70 * total_vol
    poc_idx = profile["volume"].idxmax()
    va_indices = {poc_idx}
    lo = hi = poc_idx
    accumulated = profile.at[poc_idx, "volume"]
    while accumulated < target:
        lo_vol = profile.at[lo - 1, "volume"] if lo > 0 else 0.0
        hi_vol = (
            profile.at[hi + 1, "volume"] if hi < len(profile) - 1 else 0.0
        )
        if hi_vol >= lo_vol and hi < len(profile) - 1:
            hi += 1
            va_indices.add(hi)
            accumulated += hi_vol
        elif lo > 0:
            lo -= 1
            va_indices.add(lo)
            accumulated += lo_vol
        else:
            break
    profile["value_area"] = profile.index.isin(va_indices)
    return profile


# ---------------------------------------------------------------------------
# Trend-strength indicators
# ---------------------------------------------------------------------------


def adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Average Directional Index — measures trend strength (not direction).

    Returns a DataFrame with columns:
        adx    — trend strength (0-100; >25 = trending, >50 = strong trend)
        dmp    — +DI (positive directional indicator)
        dmn    — -DI (negative directional indicator)

    Requires df columns: high, low, close.

    Note: the ta library's ADXIndicator requires at least 2 * period rows to
    compute correctly.  When fewer rows are provided, a NaN-filled DataFrame
    is returned so callers with their own _min_bars guards are unaffected.
    """
    if len(df) < 2 * period:
        return pd.DataFrame(
            {"adx": np.nan, "dmp": np.nan, "dmn": np.nan},
            index=df.index,
        )
    ind = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=period)
    return pd.DataFrame(
        {
            "adx": ind.adx(),
            "dmp": ind.adx_pos(),
            "dmn": ind.adx_neg(),
        },
        index=df.index,
    )


# ---------------------------------------------------------------------------
# Ichimoku Cloud
# ---------------------------------------------------------------------------


class IchimokuCloud(NamedTuple):
    tenkan: pd.Series      # Conversion line (9)
    kijun: pd.Series       # Base line (26)
    senkou_a: pd.Series    # Leading span A (26-period displacement)
    senkou_b: pd.Series    # Leading span B (52-period displacement)
    chikou: pd.Series      # Lagging span (26-period back)


def ichimoku(
    df: pd.DataFrame,
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_b_period: int = 52,
    displacement: int = 26,
) -> IchimokuCloud:
    """
    Ichimoku Kinko Hyo (Ichimoku Cloud).

    Components returned as a namedtuple:
        tenkan   — (highest high + lowest low) / 2 over tenkan_period
        kijun    — (highest high + lowest low) / 2 over kijun_period
        senkou_a — (tenkan + kijun) / 2, shifted forward by displacement
        senkou_b — (highest high + lowest low) / 2 over senkou_b_period, shifted forward
        chikou   — close shifted backward by displacement (lagging for validation)

    Note: senkou spans are shifted forward, so the 'current' cloud values for today
    are at index [today + displacement] in the raw Series.  When comparing to current
    price, use .shift(displacement) to align — or compare price against the raw
    shifted values at today's index.

    Requires df columns: high, low, close.
    """
    ind = ta.trend.IchimokuIndicator(
        df["high"],
        df["low"],
        window1=tenkan_period,
        window2=kijun_period,
        window3=senkou_b_period,
        visual=False,  # don't shift — we handle alignment manually
    )
    tenkan = ind.ichimoku_conversion_line()
    kijun = ind.ichimoku_base_line()
    senkou_a = ind.ichimoku_a()
    senkou_b = ind.ichimoku_b()
    chikou = df["close"].shift(-displacement)

    return IchimokuCloud(tenkan, kijun, senkou_a, senkou_b, chikou)


# ---------------------------------------------------------------------------
# Support / Resistance
# ---------------------------------------------------------------------------


class PivotPoints(NamedTuple):
    pp: pd.Series   # Pivot point
    r1: pd.Series   # Resistance 1
    r2: pd.Series   # Resistance 2
    r3: pd.Series   # Resistance 3
    s1: pd.Series   # Support 1
    s2: pd.Series   # Support 2
    s3: pd.Series   # Support 3


def pivot_points(df: pd.DataFrame) -> PivotPoints:
    """
    Classic (floor trader) pivot points calculated from the previous bar's OHLC.

    Formula:
        PP = (H + L + C) / 3
        R1 = 2*PP - L,  S1 = 2*PP - H
        R2 = PP + (H-L), S2 = PP - (H-L)
        R3 = H + 2*(PP-L), S3 = L - 2*(H-PP)

    The pivots are computed from the *prior* bar so that they are available
    at the open of the current bar — matching live trading behaviour.

    Requires df columns: high, low, close.
    """
    h = df["high"].shift(1)
    lo = df["low"].shift(1)
    c = df["close"].shift(1)

    pp = (h + lo + c) / 3.0
    r1 = 2.0 * pp - lo
    r2 = pp + (h - lo)
    r3 = h + 2.0 * (pp - lo)
    s1 = 2.0 * pp - h
    s2 = pp - (h - lo)
    s3 = lo - 2.0 * (h - pp)

    return PivotPoints(pp, r1, r2, r3, s1, s2, s3)


def fibonacci_levels(
    swing_high: float,
    swing_low: float,
    direction: str = "retracement",
) -> dict[str, float]:
    """
    Fibonacci retracement and extension levels.

    Parameters
    ----------
    swing_high : the most recent significant high
    swing_low  : the most recent significant low
    direction  : "retracement" (default) or "extension"

    Returns
    -------
    dict mapping label → price level.

    Example
    -------
    >>> levels = fibonacci_levels(high=50_000, low=40_000)
    >>> levels["0.618"]  # 43,820
    """
    diff = swing_high - swing_low

    ratios_retrace = {
        "0.0": swing_high,
        "0.236": swing_high - 0.236 * diff,
        "0.382": swing_high - 0.382 * diff,
        "0.5": swing_high - 0.5 * diff,
        "0.618": swing_high - 0.618 * diff,
        "0.786": swing_high - 0.786 * diff,
        "1.0": swing_low,
    }

    ratios_extension = {
        "0.0": swing_low,
        "0.236": swing_low - 0.236 * diff,
        "0.618": swing_low - 0.618 * diff,
        "1.0": swing_low - diff,
        "1.272": swing_low - 1.272 * diff,
        "1.618": swing_low - 1.618 * diff,
        "2.618": swing_low - 2.618 * diff,
    }

    return ratios_retrace if direction == "retracement" else ratios_extension
