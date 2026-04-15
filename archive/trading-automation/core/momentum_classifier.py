"""
core/momentum_classifier.py
----------------------------
Multi-Factor Momentum Classifier for Atlas Trading Agent.

Goes beyond simple regime detection to classify the QUALITY and PHASE
of the current trend/momentum, giving strategies granular context about
whether to be aggressive, patient, or defensive.

Phases detected:
  ACCUMULATION  — Smart money buying, price flat, volume building
  MARKUP        — Early trend, EMA alignment forming, breakout beginning
  DISTRIBUTION  — Price at highs, volume declining, divergences forming
  MARKDOWN      — Active selling, price breaking structure, momentum negative
  REVERSAL      — Counter-trend move detected, CHoCH signals present
  RANGE_BOUND   — No clear trend, oscillating between S/R levels

Each phase comes with recommended:
  - Strategy type (trend/mean-reversion/breakout)
  - Position sizing bias (aggressive/normal/defensive)
  - Preferred timeframe
  - Expected holding period

Usage
-----
    classifier = MomentumClassifier()
    phase = classifier.classify(df)
    print(phase.phase)           # "MARKUP"
    print(phase.recommended)     # "trend-following, aggressive"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from strategies.technical.indicators import ema, atr, adx, rsi

logger = logging.getLogger("atlas.momentum")


# ---------------------------------------------------------------------------
# Phase classification
# ---------------------------------------------------------------------------


@dataclass
class MomentumPhase:
    """Classification of the current market momentum phase."""

    phase: str               # ACCUMULATION, MARKUP, DISTRIBUTION, MARKDOWN, REVERSAL, RANGE_BOUND
    confidence: float        # 0.0 to 1.0
    trend_strength: float    # -1.0 (strong down) to 1.0 (strong up)

    # Recommendations
    strategy_type: str       # "trend", "mean_reversion", "breakout", "defensive"
    sizing_bias: str         # "aggressive", "normal", "defensive"
    preferred_timeframe: str # "15m", "1h", "4h"
    expected_hold_bars: int  # how many bars the current phase typically lasts

    # Supporting evidence
    ema_alignment: str       # "BULLISH", "BEARISH", "MIXED"
    volume_trend: str        # "RISING", "FALLING", "FLAT"
    momentum_divergence: bool  # True if price/momentum disagree
    adx_value: float
    rsi_value: float

    # Raw factors used in classification
    factors: dict[str, float] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"{self.phase} (conf={self.confidence:.2f}) | "
            f"trend={self.trend_strength:+.2f} ADX={self.adx_value:.1f} "
            f"RSI={self.rsi_value:.1f} | "
            f"rec={self.strategy_type}/{self.sizing_bias}"
        )


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class MomentumClassifier:
    """
    Classifies the current momentum phase from OHLCV data.

    Parameters
    ----------
    fast_ema    : Fast EMA period (default 20)
    slow_ema    : Slow EMA period (default 50)
    trend_ema   : Trend EMA period (default 200)
    atr_period  : ATR period (default 14)
    adx_period  : ADX period (default 14)
    rsi_period  : RSI period (default 14)
    vol_period  : Volume moving average period (default 20)
    """

    def __init__(
        self,
        fast_ema: int = 20,
        slow_ema: int = 50,
        trend_ema: int = 200,
        atr_period: int = 14,
        adx_period: int = 14,
        rsi_period: int = 14,
        vol_period: int = 20,
    ) -> None:
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.trend_ema = trend_ema
        self.atr_period = atr_period
        self.adx_period = adx_period
        self.rsi_period = rsi_period
        self.vol_period = vol_period
        self._min_bars = trend_ema + 10

    def classify(self, df: pd.DataFrame) -> MomentumPhase:
        """
        Classify the current momentum phase from OHLCV data.

        Parameters
        ----------
        df : OHLCV DataFrame with columns open, high, low, close, volume

        Returns
        -------
        MomentumPhase with classification and recommendations
        """
        if len(df) < self._min_bars:
            return self._default_phase()

        close = df["close"]
        volume = df["volume"]

        # Compute indicators
        ema_fast = ema(close, self.fast_ema)
        ema_slow = ema(close, self.slow_ema)
        ema_trend = ema(close, self.trend_ema)
        atr_val = float(atr(df, self.atr_period).iloc[-1])
        adx_val = float(adx(df, self.adx_period)["adx"].iloc[-1])
        rsi_val = float(rsi(close, self.rsi_period).iloc[-1])
        # Guard against NaN from insufficient data
        if np.isnan(atr_val):
            atr_val = 0.0
        if np.isnan(adx_val):
            adx_val = 0.0
        if np.isnan(rsi_val):
            rsi_val = 50.0

        # Current values
        price = float(close.iloc[-1])
        fast_now = float(ema_fast.iloc[-1])
        slow_now = float(ema_slow.iloc[-1])
        trend_now = float(ema_trend.iloc[-1])

        # Volume analysis
        vol_ma = volume.rolling(self.vol_period).mean()
        vol_ratio = float(volume.iloc[-1] / vol_ma.iloc[-1]) if float(vol_ma.iloc[-1]) > 0 else 1.0
        vol_trend = self._volume_trend(volume, self.vol_period)

        # EMA alignment
        ema_align = self._ema_alignment(price, fast_now, slow_now, trend_now)

        # Momentum divergence detection
        momentum_div = self._detect_divergence(close, rsi_val)

        # Trend strength: -1 to 1 based on EMA positioning and slope
        trend_strength = self._compute_trend_strength(
            price, fast_now, slow_now, trend_now, adx_val
        )

        # Compute phase factors
        factors = {
            "ema_alignment_score": 1.0 if ema_align == "BULLISH" else (-1.0 if ema_align == "BEARISH" else 0.0),
            "adx": adx_val,
            "rsi": rsi_val,
            "volume_ratio": vol_ratio,
            "trend_strength": trend_strength,
            "momentum_divergence": 1.0 if momentum_div else 0.0,
        }

        # Classify phase
        phase, confidence = self._determine_phase(
            ema_align, adx_val, rsi_val, vol_trend, vol_ratio,
            trend_strength, momentum_div, price, fast_now, slow_now, trend_now,
        )

        # Generate recommendations
        strategy_type, sizing_bias, pref_tf, hold_bars = self._recommend(phase, adx_val)

        result = MomentumPhase(
            phase=phase,
            confidence=confidence,
            trend_strength=trend_strength,
            strategy_type=strategy_type,
            sizing_bias=sizing_bias,
            preferred_timeframe=pref_tf,
            expected_hold_bars=hold_bars,
            ema_alignment=ema_align,
            volume_trend=vol_trend,
            momentum_divergence=momentum_div,
            adx_value=adx_val,
            rsi_value=rsi_val,
            factors=factors,
        )

        logger.info("Momentum: %s", result.summary())
        return result

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _ema_alignment(
        self, price: float, fast: float, slow: float, trend: float
    ) -> str:
        """Determine EMA stack alignment."""
        if price > fast > slow > trend:
            return "BULLISH"
        if price < fast < slow < trend:
            return "BEARISH"
        return "MIXED"

    def _volume_trend(self, volume: pd.Series, period: int) -> str:
        """Determine if volume is trending up, down, or flat."""
        if len(volume) < period * 2:
            return "FLAT"
        recent_avg = float(volume.iloc[-period:].mean())
        older_avg = float(volume.iloc[-period * 2:-period].mean())
        if older_avg == 0:
            return "FLAT"
        ratio = recent_avg / older_avg
        if ratio > 1.2:
            return "RISING"
        if ratio < 0.8:
            return "FALLING"
        return "FLAT"

    def _detect_divergence(self, close: pd.Series, current_rsi: float) -> bool:
        """Simple divergence: price making new highs but RSI isn't (or vice versa)."""
        if len(close) < 20:
            return False
        # Check if price is near 20-bar high but RSI is below 60
        recent_high = float(close.iloc[-20:].max())
        price_near_high = float(close.iloc[-1]) > recent_high * 0.98
        rsi_weak = current_rsi < 60
        if price_near_high and rsi_weak:
            return True
        # Check if price is near 20-bar low but RSI is above 40
        recent_low = float(close.iloc[-20:].min())
        price_near_low = float(close.iloc[-1]) < recent_low * 1.02
        rsi_strong = current_rsi > 40
        if price_near_low and rsi_strong:
            return True
        return False

    def _compute_trend_strength(
        self, price: float, fast: float, slow: float, trend: float, adx_val: float,
    ) -> float:
        """Compute trend strength from -1 (strong bear) to 1 (strong bull)."""
        score = 0.0

        # EMA positioning (each ±0.2)
        if price > fast:
            score += 0.2
        else:
            score -= 0.2
        if fast > slow:
            score += 0.2
        else:
            score -= 0.2
        if slow > trend:
            score += 0.2
        else:
            score -= 0.2

        # ADX amplifier: strong ADX amplifies the directional signal
        adx_factor = min(adx_val / 50.0, 1.0)  # 0-1 based on ADX
        score *= (0.5 + 0.5 * adx_factor)  # 50%-100% of the directional score

        # Price distance from 200 EMA (±0.2)
        if trend > 0:
            dist_pct = (price - trend) / trend
            score += max(-0.2, min(0.2, dist_pct * 5))

        return max(-1.0, min(1.0, score))

    def _determine_phase(
        self,
        ema_align: str,
        adx_val: float,
        rsi_val: float,
        vol_trend: str,
        vol_ratio: float,
        trend_strength: float,
        momentum_div: bool,
        price: float,
        fast: float,
        slow: float,
        trend: float,
    ) -> tuple[str, float]:
        """Determine the market phase and confidence level."""

        # ACCUMULATION: price flat near support, volume building, EMAs converging
        if abs(trend_strength) < 0.3 and vol_trend == "RISING" and adx_val < 25:
            return "ACCUMULATION", 0.6 + min(vol_ratio / 5, 0.3)

        # MARKUP: bullish EMA alignment forming, ADX rising, momentum positive
        if ema_align == "BULLISH" and adx_val > 20 and rsi_val > 50:
            if momentum_div:
                # Potential distribution (price up, momentum weakening)
                return "DISTRIBUTION", 0.7
            conf = 0.5 + (adx_val - 20) / 60  # higher ADX = more confident
            return "MARKUP", min(conf, 0.95)

        # DISTRIBUTION: price at highs, volume declining, divergences
        if trend_strength > 0.3 and (vol_trend == "FALLING" or momentum_div):
            if rsi_val > 65:
                return "DISTRIBUTION", 0.7
            return "DISTRIBUTION", 0.5

        # MARKDOWN: bearish alignment, ADX rising, momentum negative
        if ema_align == "BEARISH" and adx_val > 20 and rsi_val < 50:
            if momentum_div:
                # Potential reversal (price down, momentum strengthening)
                return "REVERSAL", 0.6
            conf = 0.5 + (adx_val - 20) / 60
            return "MARKDOWN", min(conf, 0.95)

        # REVERSAL: counter-trend signals present
        if momentum_div and adx_val < 30:
            return "REVERSAL", 0.5

        # RANGE_BOUND: default when nothing else fits
        return "RANGE_BOUND", 0.4 + (0.3 if adx_val < 20 else 0.0)

    def _recommend(
        self, phase: str, adx_val: float,
    ) -> tuple[str, str, str, int]:
        """
        Return (strategy_type, sizing_bias, preferred_timeframe, expected_hold_bars).
        """
        recommendations = {
            "ACCUMULATION": ("breakout", "defensive", "4h", 30),
            "MARKUP":       ("trend", "aggressive", "4h", 50),
            "DISTRIBUTION": ("mean_reversion", "defensive", "1h", 20),
            "MARKDOWN":     ("trend", "normal", "4h", 40),
            "REVERSAL":     ("mean_reversion", "defensive", "1h", 15),
            "RANGE_BOUND":  ("mean_reversion", "normal", "1h", 10),
        }
        return recommendations.get(phase, ("defensive", "defensive", "1h", 10))

    def _default_phase(self) -> MomentumPhase:
        """Return a neutral phase when data is insufficient."""
        return MomentumPhase(
            phase="RANGE_BOUND",
            confidence=0.0,
            trend_strength=0.0,
            strategy_type="defensive",
            sizing_bias="defensive",
            preferred_timeframe="1h",
            expected_hold_bars=10,
            ema_alignment="MIXED",
            volume_trend="FLAT",
            momentum_divergence=False,
            adx_value=0.0,
            rsi_value=50.0,
        )
