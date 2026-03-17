"""
core/regime_detector.py
-----------------------
Market Regime Detector for Atlas Trading Agent.

Classifies the current market environment into one of four regimes:
  BULL_TREND  — Sustained uptrend, momentum strategies favoured
  BEAR_TREND  — Sustained downtrend, mean-reversion is dangerous
  CHOPPY      — Low-trend, range-bound, mean-reversion and breakout favoured
  HIGH_VOL    — Extreme volatility, reduce all position sizes

The regime influences:
  - Which strategies get higher weight
  - How aggressive the position sizing should be
  - Whether mean-reversion or trend-following signals are trusted

Detection uses:
  - Rolling Sharpe ratio (20-bar)
  - ADX (trend strength)
  - Volatility relative to its rolling average
  - Consecutive win/loss streaks
"""

from __future__ import annotations

import logging
from enum import Enum

import numpy as np
import pandas as pd

logger = logging.getLogger("atlas.regime")


class MarketRegime(str, Enum):
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    CHOPPY = "CHOPPY"
    HIGH_VOL = "HIGH_VOL"


class RegimeDetector:
    """
    Stateless regime classifier — call detect() with recent OHLCV data.

    Usage
    -----
    detector = RegimeDetector()
    regime = detector.detect(df_ohlcv)
    # regime.regime -> MarketRegime
    # regime.confidence -> 0.0 to 1.0
    # regime.volatility_ratio -> current vol / avg vol
    """

    def __init__(
        self,
        sharpe_window: int = 20,
        adx_window: int = 14,
        vol_window: int = 20,
        vol_spike_threshold: float = 1.8,
        trend_adx_threshold: float = 25.0,
        bull_sharpe_threshold: float = 0.3,
        bear_sharpe_threshold: float = -0.3,
    ) -> None:
        self.sharpe_window = sharpe_window
        self.adx_window = adx_window
        self.vol_window = vol_window
        self.vol_spike_threshold = vol_spike_threshold
        self.trend_adx_threshold = trend_adx_threshold
        self.bull_sharpe_threshold = bull_sharpe_threshold
        self.bear_sharpe_threshold = bear_sharpe_threshold

    def detect(self, df: pd.DataFrame) -> RegimeResult:
        """
        Classify the market regime from recent OHLCV data.

        Parameters
        ----------
        df : DataFrame with columns: open, high, low, close, volume
             At least 50 rows recommended.

        Returns
        -------
        RegimeResult with regime, confidence, and diagnostic metrics.
        """
        min_bars = max(self.sharpe_window, self.adx_window, self.vol_window) + 5
        if len(df) < min_bars:
            return RegimeResult(
                regime=MarketRegime.CHOPPY,
                confidence=0.0,
                rolling_sharpe=0.0,
                adx=0.0,
                volatility_ratio=1.0,
                mean_return=0.0,
            )

        close = df["close"].values
        high = df["high"].values
        low = df["low"].values

        # Rolling returns
        returns = np.diff(close) / close[:-1]
        recent_returns = returns[-self.sharpe_window:]
        mean_ret = float(np.mean(recent_returns))
        std_ret = float(np.std(recent_returns, ddof=1)) if len(recent_returns) > 1 else 1e-8

        # Rolling Sharpe (annualised approximation)
        rolling_sharpe = (mean_ret / max(std_ret, 1e-8)) * np.sqrt(252)

        # ADX approximation (simplified — uses true range)
        tr = np.maximum(
            high[1:] - low[1:],
            np.maximum(
                np.abs(high[1:] - close[:-1]),
                np.abs(low[1:] - close[:-1]),
            ),
        )
        atr = float(np.mean(tr[-self.adx_window:]))

        # Directional movement
        plus_dm = np.where(
            (high[1:] - high[:-1]) > (low[:-1] - low[1:]),
            np.maximum(high[1:] - high[:-1], 0),
            0,
        )
        minus_dm = np.where(
            (low[:-1] - low[1:]) > (high[1:] - high[:-1]),
            np.maximum(low[:-1] - low[1:], 0),
            0,
        )

        avg_plus_dm = float(np.mean(plus_dm[-self.adx_window:]))
        avg_minus_dm = float(np.mean(minus_dm[-self.adx_window:]))

        plus_di = (avg_plus_dm / max(atr, 1e-8)) * 100
        minus_di = (avg_minus_dm / max(atr, 1e-8)) * 100
        dx = abs(plus_di - minus_di) / max(plus_di + minus_di, 1e-8) * 100
        adx_value = dx  # Simplified single-period ADX

        # Volatility ratio
        recent_vol = float(np.std(returns[-self.vol_window:], ddof=1))
        lookback_vol = float(np.std(returns[-self.vol_window * 3:], ddof=1)) if len(returns) >= self.vol_window * 3 else recent_vol
        vol_ratio = recent_vol / max(lookback_vol, 1e-8)

        # Classification
        regime, confidence = self._classify(
            rolling_sharpe, adx_value, vol_ratio, mean_ret
        )

        logger.debug(
            "Regime: %s (conf=%.2f) Sharpe=%.2f ADX=%.1f VolRatio=%.2f",
            regime.value, confidence, rolling_sharpe, adx_value, vol_ratio,
        )

        return RegimeResult(
            regime=regime,
            confidence=confidence,
            rolling_sharpe=float(rolling_sharpe),
            adx=adx_value,
            volatility_ratio=vol_ratio,
            mean_return=mean_ret,
        )

    def _classify(
        self,
        sharpe: float,
        adx: float,
        vol_ratio: float,
        mean_ret: float,
    ) -> tuple[MarketRegime, float]:
        """Return (regime, confidence) based on metrics."""
        # High volatility overrides everything
        if vol_ratio >= self.vol_spike_threshold:
            confidence = min((vol_ratio - self.vol_spike_threshold) / 1.0 + 0.6, 1.0)
            return MarketRegime.HIGH_VOL, confidence

        # Strong trend detected
        if adx >= self.trend_adx_threshold:
            if sharpe >= self.bull_sharpe_threshold and mean_ret > 0:
                confidence = min(0.5 + (sharpe - self.bull_sharpe_threshold) / 2.0, 1.0)
                return MarketRegime.BULL_TREND, confidence
            elif sharpe <= self.bear_sharpe_threshold and mean_ret < 0:
                confidence = min(0.5 + abs(sharpe - self.bear_sharpe_threshold) / 2.0, 1.0)
                return MarketRegime.BEAR_TREND, confidence

        # Weak trend or ranging
        return MarketRegime.CHOPPY, 0.5 + min(abs(adx - self.trend_adx_threshold) / 50.0, 0.3)


class RegimeResult:
    """Result of regime detection with diagnostic metrics."""

    __slots__ = ("regime", "confidence", "rolling_sharpe", "adx", "volatility_ratio", "mean_return")

    def __init__(
        self,
        regime: MarketRegime,
        confidence: float,
        rolling_sharpe: float,
        adx: float,
        volatility_ratio: float,
        mean_return: float,
    ) -> None:
        self.regime = regime
        self.confidence = confidence
        self.rolling_sharpe = rolling_sharpe
        self.adx = adx
        self.volatility_ratio = volatility_ratio
        self.mean_return = mean_return

    def __repr__(self) -> str:
        return (
            f"RegimeResult(regime={self.regime.value}, confidence={self.confidence:.2f}, "
            f"sharpe={self.rolling_sharpe:.2f}, adx={self.adx:.1f}, "
            f"vol_ratio={self.volatility_ratio:.2f})"
        )

    def size_multiplier(self) -> float:
        """
        Position size multiplier based on regime.
        BULL_TREND: full size (1.0)
        BEAR_TREND: reduced (0.7) — higher tail risk
        CHOPPY:     reduced (0.8) — whipsaw risk
        HIGH_VOL:   minimal (0.5) — capital preservation
        """
        multipliers = {
            MarketRegime.BULL_TREND: 1.0,
            MarketRegime.BEAR_TREND: 0.7,
            MarketRegime.CHOPPY: 0.8,
            MarketRegime.HIGH_VOL: 0.5,
        }
        return multipliers.get(self.regime, 0.8)

    def strategy_weights(self) -> dict[str, float]:
        """
        Strategy preference multipliers by regime.
        Values > 1.0 = favour, < 1.0 = penalise.
        """
        if self.regime == MarketRegime.BULL_TREND:
            return {
                "ema_crossover": 1.3,
                "multi_timeframe": 1.3,
                "ichimoku_trend": 1.2,
                "rsi_mean_reversion": 0.7,  # Mean reversion risky in trends
                "bollinger_squeeze": 1.1,
                "vwap_bounce": 0.8,
                "london_breakout": 1.1,
                "opening_range": 1.0,
                "smart_money": 1.1,
                "order_flow_imbalance": 0.7,  # Reversal strategy — penalised in trends
                "zscore_mean_reversion": 0.6,  # Mean reversion dangerous in trends
                "volume_profile": 1.1,  # Breakout mode works in trends
            }
        elif self.regime == MarketRegime.BEAR_TREND:
            return {
                "ema_crossover": 1.2,   # Shorts work in bear trends
                "multi_timeframe": 1.2,
                "ichimoku_trend": 1.1,
                "rsi_mean_reversion": 0.5,  # Mean reversion is a trap
                "bollinger_squeeze": 0.8,
                "vwap_bounce": 0.6,
                "london_breakout": 0.9,
                "opening_range": 0.8,
                "smart_money": 1.0,
                "order_flow_imbalance": 0.6,  # Catching knives is dangerous
                "zscore_mean_reversion": 0.5,  # Mean reversion trap in bear trends
                "volume_profile": 1.0,  # Neutral — breakout shorts can work
            }
        elif self.regime == MarketRegime.HIGH_VOL:
            return {
                "ema_crossover": 0.6,
                "multi_timeframe": 0.7,
                "ichimoku_trend": 0.7,
                "rsi_mean_reversion": 0.5,
                "bollinger_squeeze": 0.5,
                "vwap_bounce": 0.5,
                "london_breakout": 0.6,
                "opening_range": 0.5,
                "smart_money": 0.6,
                "order_flow_imbalance": 0.5,  # Too noisy for flow analysis
                "zscore_mean_reversion": 0.4,  # Extreme vol invalidates z-score
                "volume_profile": 0.6,  # Profiles less reliable in chaos
            }
        else:  # CHOPPY
            return {
                "ema_crossover": 0.8,
                "multi_timeframe": 0.9,
                "ichimoku_trend": 0.8,
                "rsi_mean_reversion": 1.3,  # Mean reversion thrives in ranges
                "bollinger_squeeze": 1.2,
                "vwap_bounce": 1.3,
                "london_breakout": 1.1,
                "opening_range": 1.1,
                "smart_money": 1.0,
                "order_flow_imbalance": 1.3,  # Flow analysis excels in ranges
                "zscore_mean_reversion": 1.3,  # Statistical reversion thrives
                "volume_profile": 1.2,  # VA mean reversion is ideal in ranges
            }
