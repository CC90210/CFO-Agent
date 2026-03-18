"""
core/market_structure.py
------------------------
Market Structure Analysis Module for Atlas Trading Agent.

Provides a unified view of where price stands relative to key structure levels,
how strong the prevailing trend is, and what the volatility environment looks like.
Any strategy or the engine can call this once per bar and consume the result.

Key outputs
-----------
- Support and resistance levels derived from swing pivots (clustered into zones)
- Trend strength score: -1.0 (strong bear) to +1.0 (strong bull)
- Volatility regime: LOW / NORMAL / HIGH / EXTREME
- Higher-highs / higher-lows / lower-highs / lower-lows flags
- Bullish and bearish confluence counts for quick signal filtering

Usage
-----
    ms = MarketStructure()
    analysis = ms.analyze(df)          # df is a standard OHLCV DataFrame
    print(analysis.trend_strength)     # e.g. 0.72
    print(analysis.nearest_support)    # e.g. 64_200.0
    print(analysis.nearest_resistance) # e.g. 67_850.0
    print(analysis.volatility_regime)  # e.g. "NORMAL"
    print(analysis.bullish_confluence) # e.g. 4
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from strategies.technical.indicators import adx, atr, ema

logger = logging.getLogger("atlas.market_structure")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TREND_STRENGTH_CLAMP = 1.0

# EMA component weights (must sum to ≤ 1.0 in absolute terms per direction)
_EMA_ALIGNMENT_WEIGHT = 0.3   # per EMA cross: 20>50, 50>200, 20>200 → max ±0.9 → capped
_PRICE_EMA_WEIGHT = 0.1       # per EMA level: price > EMA20/50/200
_ADX_MAX_WEIGHT = 0.2
_SWING_STRUCTURE_WEIGHT = 0.2 # higher-highs + higher-lows together

# Pivot clustering threshold: levels within this % are merged
_CLUSTER_THRESHOLD_PCT = 0.005  # 0.5%

# Volatility regime thresholds (multiples of 50-bar ATR-pct mean)
_VOL_LOW_THRESHOLD = 0.5
_VOL_HIGH_THRESHOLD = 1.5
_VOL_EXTREME_THRESHOLD = 2.5

# Minimum bars required for a full analysis
_MIN_BARS_FULL = 60


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class MarketStructureAnalysis:
    """
    Full market structure snapshot for a single bar.

    All price fields are in the same units as the input DataFrame's close column.
    """

    # --- Trend ---
    trend_direction: str   # "BULLISH", "BEARISH", "NEUTRAL"
    trend_strength: float  # -1.0 (strong bear) to +1.0 (strong bull)

    # --- Key levels ---
    nearest_support: float
    nearest_resistance: float
    support_levels: list[float]     # sorted ascending
    resistance_levels: list[float]  # sorted ascending

    # --- Market position ---
    distance_to_support_pct: float      # % gap between price and nearest support
    distance_to_resistance_pct: float   # % gap between price and nearest resistance

    # --- Volatility context ---
    atr_pct: float          # ATR(14) expressed as % of current price
    volatility_regime: str  # "LOW", "NORMAL", "HIGH", "EXTREME"

    # --- Structure flags ---
    higher_highs: bool
    higher_lows: bool
    lower_highs: bool
    lower_lows: bool

    # --- Confluence ---
    bullish_confluence: int  # count of bullish structure signals (0-7)
    bearish_confluence: int  # count of bearish structure signals (0-7)

    # --- Diagnostic fields (not part of public contract, but useful for debugging) ---
    ema20: float = field(repr=False, default=float("nan"))
    ema50: float = field(repr=False, default=float("nan"))
    ema200: float = field(repr=False, default=float("nan"))
    adx_value: float = field(repr=False, default=float("nan"))
    current_price: float = field(repr=False, default=float("nan"))


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class MarketStructure:
    """
    Stateless market structure analyser — call analyze() with any OHLCV DataFrame.

    Parameters
    ----------
    swing_lookback : int
        Number of bars on each side of a candle that must be lower/higher for it
        to qualify as a swing high/low (pivot point).  Default 5.
    atr_period : int
        ATR period used for volatility calculations.  Default 14.
    vol_avg_period : int
        Rolling period for computing the baseline ATR-pct average that the
        current ATR-pct is compared against to classify volatility regime.
        Default 50.
    swing_history : int
        How many bars of history to scan when detecting swing pivots.
        Default 200 (roughly 200 candles back).
    """

    def __init__(
        self,
        swing_lookback: int = 5,
        atr_period: int = 14,
        vol_avg_period: int = 50,
        swing_history: int = 200,
    ) -> None:
        self.swing_lookback = swing_lookback
        self.atr_period = atr_period
        self.vol_avg_period = vol_avg_period
        self.swing_history = swing_history

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> MarketStructureAnalysis:
        """
        Run a full market structure analysis on the supplied OHLCV DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Must contain columns: open, high, low, close, volume.
            The last row is treated as the current bar.
            Minimum 20 rows required; 60+ recommended for full signal fidelity.

        Returns
        -------
        MarketStructureAnalysis
            Complete snapshot.  When insufficient data is available, sensible
            safe defaults are returned (NEUTRAL trend, NaN-free floats).
        """
        if df is None or len(df) < max(self.atr_period + 1, self.swing_lookback * 2 + 1):
            logger.warning("market_structure.analyze: insufficient data (%d rows)", len(df) if df is not None else 0)
            return self._safe_defaults(df)

        # Work on a clean copy — never mutate the caller's frame
        df = df.copy()
        for col in ("open", "high", "low", "close", "volume"):
            if col not in df.columns:
                logger.warning("market_structure.analyze: missing column '%s'", col)
                return self._safe_defaults(df)

        current_price = float(df["close"].iloc[-1])
        if not np.isfinite(current_price) or current_price <= 0:
            return self._safe_defaults(df)

        # ---- ATR & volatility ----
        atr_series = atr(df, period=self.atr_period)
        current_atr = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
        if not np.isfinite(current_atr):
            current_atr = 0.0
        atr_pct = (current_atr / current_price) * 100.0 if current_price > 0 else 0.0
        volatility_regime = self._classify_volatility(atr_series, current_price)

        # ---- EMAs ----
        close = df["close"]
        ema20_series  = ema(close, 20)
        ema50_series  = ema(close, 50)
        ema200_series = ema(close, 200)

        ema20  = float(ema20_series.iloc[-1])
        ema50  = float(ema50_series.iloc[-1])
        ema200 = float(ema200_series.iloc[-1])

        # Guard against NaN EMAs (too-short series)
        ema20  = ema20  if np.isfinite(ema20)  else current_price
        ema50  = ema50  if np.isfinite(ema50)  else current_price
        ema200 = ema200 if np.isfinite(ema200) else current_price

        # ---- ADX ----
        adx_df = adx(df, period=14)
        adx_row = adx_df.iloc[-1]
        adx_value = float(adx_row["adx"]) if np.isfinite(adx_row["adx"]) else 0.0
        dmp = float(adx_row["dmp"]) if np.isfinite(adx_row["dmp"]) else 0.0
        dmn = float(adx_row["dmn"]) if np.isfinite(adx_row["dmn"]) else 0.0

        # ---- Swing structure ----
        swing_highs, swing_lows = self._detect_swings(df)
        higher_highs, higher_lows, lower_highs, lower_lows = self._classify_swing_structure(
            swing_highs, swing_lows
        )

        # ---- Trend strength ----
        trend_strength = self._compute_trend_strength(
            current_price, ema20, ema50, ema200,
            adx_value, dmp, dmn,
            higher_highs, higher_lows, lower_highs, lower_lows,
        )
        trend_direction = self._trend_direction_label(trend_strength)

        # ---- Support / resistance levels ----
        support_levels, resistance_levels = self._build_levels(
            df, swing_highs, swing_lows, current_price
        )

        nearest_support = self._nearest_below(support_levels, current_price)
        nearest_resistance = self._nearest_above(resistance_levels, current_price)

        distance_to_support_pct = (
            ((current_price - nearest_support) / current_price) * 100.0
            if nearest_support > 0 else float("nan")
        )
        distance_to_resistance_pct = (
            ((nearest_resistance - current_price) / current_price) * 100.0
            if np.isfinite(nearest_resistance) else float("nan")
        )

        # ---- Confluence ----
        bullish_confluence, bearish_confluence = self._count_confluence(
            current_price, ema20, ema50, ema200,
            adx_value, dmp, dmn,
            higher_highs, higher_lows, lower_highs, lower_lows,
        )

        logger.debug(
            "MarketStructure: price=%.4f trend=%.2f (%s) support=%.4f resistance=%.4f "
            "vol=%s bull_conf=%d bear_conf=%d",
            current_price, trend_strength, trend_direction,
            nearest_support, nearest_resistance,
            volatility_regime, bullish_confluence, bearish_confluence,
        )

        return MarketStructureAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            distance_to_support_pct=distance_to_support_pct,
            distance_to_resistance_pct=distance_to_resistance_pct,
            atr_pct=atr_pct,
            volatility_regime=volatility_regime,
            higher_highs=higher_highs,
            higher_lows=higher_lows,
            lower_highs=lower_highs,
            lower_lows=lower_lows,
            bullish_confluence=bullish_confluence,
            bearish_confluence=bearish_confluence,
            ema20=ema20,
            ema50=ema50,
            ema200=ema200,
            adx_value=adx_value,
            current_price=current_price,
        )

    # ------------------------------------------------------------------
    # Swing detection
    # ------------------------------------------------------------------

    def _detect_swings(
        self, df: pd.DataFrame
    ) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
        """
        Identify swing highs and lows using a pivot-point approach.

        A bar at index i is a swing high if its high is strictly greater than
        the `swing_lookback` bars on each side.  Likewise for swing lows.

        Returns
        -------
        swing_highs : list of (bar_index, price) sorted by bar_index ascending
        swing_lows  : list of (bar_index, price) sorted by bar_index ascending
        """
        lb = self.swing_lookback
        # Only examine the most recent `swing_history` bars for performance
        start_idx = max(0, len(df) - self.swing_history)
        sub = df.iloc[start_idx:]

        highs = sub["high"].values
        lows = sub["low"].values
        n = len(sub)
        bar_indices = sub.index

        swing_highs: list[tuple[int, float]] = []
        swing_lows: list[tuple[int, float]] = []

        for i in range(lb, n - lb):
            h = highs[i]
            if np.isnan(h):
                continue
            window_h = highs[i - lb: i]
            window_h_right = highs[i + 1: i + lb + 1]
            if h > np.nanmax(window_h) and h > np.nanmax(window_h_right):
                swing_highs.append((bar_indices[i], float(h)))

            lo = lows[i]
            if np.isnan(lo):
                continue
            window_l = lows[i - lb: i]
            window_l_right = lows[i + 1: i + lb + 1]
            if lo < np.nanmin(window_l) and lo < np.nanmin(window_l_right):
                swing_lows.append((bar_indices[i], float(lo)))

        return swing_highs, swing_lows

    # ------------------------------------------------------------------
    # Support / resistance level building
    # ------------------------------------------------------------------

    def _build_levels(
        self,
        df: pd.DataFrame,
        swing_highs: list[tuple[int, float]],
        swing_lows: list[tuple[int, float]],
        current_price: float,
    ) -> tuple[list[float], list[float]]:
        """
        Cluster raw swing prices into support and resistance zones, then sort.

        Nearby prices (within _CLUSTER_THRESHOLD_PCT of each other) are merged
        by taking their mean.  This prevents a single congestion area from
        generating five distinct but nearly identical levels.

        Returns
        -------
        (support_levels, resistance_levels) — both sorted ascending
        """
        raw_resistance = [price for _, price in swing_highs]
        raw_support = [price for _, price in swing_lows]

        resistance_levels = self._cluster_levels(raw_resistance)
        support_levels = self._cluster_levels(raw_support)

        # Filter: supports should be below current price, resistances above.
        # Keep a small band (0.5× ATR-pct) around current price to catch
        # levels that are essentially at current price — these are still valid.
        margin = current_price * _CLUSTER_THRESHOLD_PCT * 2
        support_levels = sorted(
            [lvl for lvl in support_levels if lvl <= current_price + margin]
        )
        resistance_levels = sorted(
            [lvl for lvl in resistance_levels if lvl >= current_price - margin]
        )

        return support_levels, resistance_levels

    def _cluster_levels(self, prices: list[float]) -> list[float]:
        """
        Merge prices within _CLUSTER_THRESHOLD_PCT of each other into a single
        representative level (their mean).
        """
        if not prices:
            return []

        sorted_prices = sorted(prices)
        clusters: list[list[float]] = []
        current_cluster: list[float] = [sorted_prices[0]]

        for price in sorted_prices[1:]:
            anchor = current_cluster[0]
            if anchor > 0 and abs(price - anchor) / anchor <= _CLUSTER_THRESHOLD_PCT:
                current_cluster.append(price)
            else:
                clusters.append(current_cluster)
                current_cluster = [price]
        clusters.append(current_cluster)

        return [float(np.mean(c)) for c in clusters]

    # ------------------------------------------------------------------
    # Swing structure classification
    # ------------------------------------------------------------------

    def _classify_swing_structure(
        self,
        swing_highs: list[tuple[int, float]],
        swing_lows: list[tuple[int, float]],
    ) -> tuple[bool, bool, bool, bool]:
        """
        Determine whether the last 3 swing highs and lows are ascending or descending.

        Returns (higher_highs, higher_lows, lower_highs, lower_lows).
        """
        higher_highs = False
        lower_highs = False
        higher_lows = False
        lower_lows = False

        if len(swing_highs) >= 3:
            last_highs = [p for _, p in swing_highs[-3:]]
            higher_highs = last_highs[0] < last_highs[1] < last_highs[2]
            lower_highs  = last_highs[0] > last_highs[1] > last_highs[2]

        if len(swing_lows) >= 3:
            last_lows = [p for _, p in swing_lows[-3:]]
            higher_lows = last_lows[0] < last_lows[1] < last_lows[2]
            lower_lows  = last_lows[0] > last_lows[1] > last_lows[2]

        return higher_highs, higher_lows, lower_highs, lower_lows

    # ------------------------------------------------------------------
    # Trend strength
    # ------------------------------------------------------------------

    def _compute_trend_strength(
        self,
        price: float,
        ema20: float,
        ema50: float,
        ema200: float,
        adx_value: float,
        dmp: float,
        dmn: float,
        higher_highs: bool,
        higher_lows: bool,
        lower_highs: bool,
        lower_lows: bool,
    ) -> float:
        """
        Composite trend strength score in [-1.0, 1.0].

        Components
        ----------
        EMA alignment (±0.3 each, 3 crosses):
            20 > 50  → +0.3   |  20 < 50  → -0.3
            50 > 200 → +0.3   |  50 < 200 → -0.3
            20 > 200 → +0.3   |  20 < 200 → -0.3

        Price vs EMAs (±0.1 each, 3 levels):
            price > EMA20  → +0.1  etc.

        ADX contribution (±0.2 max):
            adx > 25 and dmp > dmn → +0.2 (scaled by adx/100)
            adx > 25 and dmn > dmp → -0.2 (scaled by adx/100)

        Swing structure (±0.2):
            higher_highs AND higher_lows → +0.2
            lower_highs  AND lower_lows  → -0.2
            partial match                → ±0.1

        Raw sum is clamped to [-1.0, 1.0].
        """
        score = 0.0

        # EMA alignment
        score += _EMA_ALIGNMENT_WEIGHT  if ema20  > ema50  else -_EMA_ALIGNMENT_WEIGHT
        score += _EMA_ALIGNMENT_WEIGHT  if ema50  > ema200 else -_EMA_ALIGNMENT_WEIGHT
        score += _EMA_ALIGNMENT_WEIGHT  if ema20  > ema200 else -_EMA_ALIGNMENT_WEIGHT

        # Price vs EMAs
        score += _PRICE_EMA_WEIGHT if price > ema20  else -_PRICE_EMA_WEIGHT
        score += _PRICE_EMA_WEIGHT if price > ema50  else -_PRICE_EMA_WEIGHT
        score += _PRICE_EMA_WEIGHT if price > ema200 else -_PRICE_EMA_WEIGHT

        # ADX directional contribution
        if adx_value >= 25.0:
            adx_scale = min(adx_value / 100.0, 1.0)  # normalise 25-100 → 0.25-1.0
            if dmp > dmn:
                score += _ADX_MAX_WEIGHT * adx_scale
            elif dmn > dmp:
                score -= _ADX_MAX_WEIGHT * adx_scale

        # Swing structure
        if higher_highs and higher_lows:
            score += _SWING_STRUCTURE_WEIGHT
        elif higher_highs or higher_lows:
            score += _SWING_STRUCTURE_WEIGHT * 0.5

        if lower_highs and lower_lows:
            score -= _SWING_STRUCTURE_WEIGHT
        elif lower_highs or lower_lows:
            score -= _SWING_STRUCTURE_WEIGHT * 0.5

        return float(np.clip(score, -_TREND_STRENGTH_CLAMP, _TREND_STRENGTH_CLAMP))

    @staticmethod
    def _trend_direction_label(strength: float) -> str:
        """Convert a numeric trend strength into a human-readable label."""
        if strength > 0.1:
            return "BULLISH"
        if strength < -0.1:
            return "BEARISH"
        return "NEUTRAL"

    # ------------------------------------------------------------------
    # Volatility regime
    # ------------------------------------------------------------------

    def _classify_volatility(
        self, atr_series: pd.Series, current_price: float
    ) -> str:
        """
        Classify current volatility as LOW / NORMAL / HIGH / EXTREME by comparing
        the current ATR-pct to its rolling `vol_avg_period`-bar mean.

        Falls back to NORMAL when there is insufficient history.
        """
        if atr_series is None or len(atr_series) < self.vol_avg_period + 1:
            return "NORMAL"

        # ATR as % of closing price (requires aligned close series)
        # atr_series is already a raw price-unit series; we normalise by current_price
        # as a proxy (close is not passed here but the last ATR reflects recent prices).
        atr_pct_series = atr_series / current_price * 100.0
        atr_pct_series = atr_pct_series.replace([np.inf, -np.inf], np.nan).dropna()

        if len(atr_pct_series) < self.vol_avg_period:
            return "NORMAL"

        current_atr_pct = float(atr_pct_series.iloc[-1])
        avg_atr_pct = float(atr_pct_series.iloc[-self.vol_avg_period:].mean())

        if avg_atr_pct <= 0:
            return "NORMAL"

        ratio = current_atr_pct / avg_atr_pct

        if ratio < _VOL_LOW_THRESHOLD:
            return "LOW"
        if ratio < _VOL_HIGH_THRESHOLD:
            return "NORMAL"
        if ratio < _VOL_EXTREME_THRESHOLD:
            return "HIGH"
        return "EXTREME"

    # ------------------------------------------------------------------
    # Level helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _nearest_below(levels: list[float], price: float) -> float:
        """Return the highest level that is at or below price.  Returns 0.0 if none."""
        below = [lvl for lvl in levels if lvl <= price]
        return max(below) if below else 0.0

    @staticmethod
    def _nearest_above(levels: list[float], price: float) -> float:
        """Return the lowest level that is at or above price.  Returns inf if none."""
        above = [lvl for lvl in levels if lvl >= price]
        return min(above) if above else float("inf")

    # ------------------------------------------------------------------
    # Confluence
    # ------------------------------------------------------------------

    def _count_confluence(
        self,
        price: float,
        ema20: float,
        ema50: float,
        ema200: float,
        adx_value: float,
        dmp: float,
        dmn: float,
        higher_highs: bool,
        higher_lows: bool,
        lower_highs: bool,
        lower_lows: bool,
    ) -> tuple[int, int]:
        """
        Count distinct structure signals that are bullish or bearish.

        Signals checked (7 total per direction):
          1. EMA20 > EMA50 (bullish alignment)
          2. EMA50 > EMA200 (macro alignment)
          3. Price > EMA200 (above macro baseline)
          4. Price > EMA20  (short-term momentum)
          5. Higher highs
          6. Higher lows
          7. ADX trending and dmp > dmn (bullish momentum)

        Returns (bullish_count, bearish_count).
        """
        bullish = 0
        bearish = 0

        # 1. Short EMA vs medium EMA
        if ema20 > ema50:
            bullish += 1
        else:
            bearish += 1

        # 2. Medium EMA vs long EMA
        if ema50 > ema200:
            bullish += 1
        else:
            bearish += 1

        # 3. Price above/below EMA200
        if price > ema200:
            bullish += 1
        else:
            bearish += 1

        # 4. Price above/below EMA20
        if price > ema20:
            bullish += 1
        else:
            bearish += 1

        # 5. Higher highs
        if higher_highs:
            bullish += 1
        elif lower_highs:
            bearish += 1

        # 6. Higher lows
        if higher_lows:
            bullish += 1
        elif lower_lows:
            bearish += 1

        # 7. ADX directional bias
        if adx_value >= 25.0:
            if dmp > dmn:
                bullish += 1
            elif dmn > dmp:
                bearish += 1

        return bullish, bearish

    # ------------------------------------------------------------------
    # Safe defaults
    # ------------------------------------------------------------------

    def _safe_defaults(self, df: pd.DataFrame | None) -> MarketStructureAnalysis:
        """Return a safe, neutral analysis when data is insufficient."""
        price = 0.0
        if df is not None and len(df) > 0 and "close" in df.columns:
            last = df["close"].iloc[-1]
            price = float(last) if np.isfinite(last) else 0.0

        return MarketStructureAnalysis(
            trend_direction="NEUTRAL",
            trend_strength=0.0,
            nearest_support=0.0,
            nearest_resistance=float("inf"),
            support_levels=[],
            resistance_levels=[],
            distance_to_support_pct=float("nan"),
            distance_to_resistance_pct=float("nan"),
            atr_pct=0.0,
            volatility_regime="NORMAL",
            higher_highs=False,
            higher_lows=False,
            lower_highs=False,
            lower_lows=False,
            bullish_confluence=0,
            bearish_confluence=0,
            current_price=price,
        )
