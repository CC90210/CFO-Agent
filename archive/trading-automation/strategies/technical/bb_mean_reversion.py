"""
strategies/technical/bb_mean_reversion.py — Bollinger Band Mean Reversion (Range Trader)

Logic
-----
This strategy is designed specifically for RANGE-BOUND / CHOPPY markets where
trending strategies go silent. It profits from mean reversion within Bollinger Bands
when the market lacks directional trend.

Entry conditions (ALL must be true):
    1. ADX < 25 — confirms no trend (range-bound market)
    2. Price near band edge:
       - LONG:  percent_b < 0.15 (price at or below lower band)
       - SHORT: percent_b > 0.85 (price at or above upper band)
    3. StochRSI confirmation (catches momentum shifts even when RSI is mid-range):
       - LONG:  StochRSI K < 20 (oversold micro-momentum)
       - SHORT: StochRSI K > 80 (overbought micro-momentum)
    4. BB width is NOT in extreme squeeze (bottom 5th percentile) — squeeze
       breakouts are handled by bollinger_squeeze strategy, not this one

Stops — ATR-based (tight for mean reversion):
    - LONG stop:  entry - 1.5× ATR
    - SHORT stop: entry + 1.5× ATR

Take profit — middle band (SMA20) is the mean reversion target:
    - LONG:  BB middle band (conservative) or upper band (aggressive)
    - SHORT: BB middle band (conservative) or lower band (aggressive)

Exit logic:
    - Price reaches opposite band (full mean reversion complete)
    - StochRSI crosses into opposite extreme (momentum exhausted)
    - Trailing stop hit
    - ADX rises above 30 (trend emerging — exit range trade)

Conviction scoring:
    +0.30  Band proximity (how close to the band edge)
    +0.25  StochRSI extremity (deeper = higher conviction)
    +0.20  Volume confirmation (above-average volume at band = institutional interest)
    +0.15  RSI divergence (price at band but RSI not at extreme = potential reversal)
    +0.10  BB width (wider bands = more profit potential per trade)

Best markets  : All crypto, commodities — anything that oscillates
Best timeframes: 1H, 4H — range-bound conditions resolve within hours to days
"""

from __future__ import annotations

import logging

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import (
    adx,
    atr,
    bollinger_bands,
    rsi,
    stochastic_rsi,
)

logger = logging.getLogger(__name__)


class BBMeanReversionStrategy(BaseStrategy):
    """
    Bollinger Band Mean Reversion — buys lower band, sells upper band in
    range-bound markets. Designed to generate signals when trending strategies
    are silent (ADX < 25, RSI 30-70).
    """

    name = "bb_mean_reversion"
    description = (
        "Range-bound mean reversion: buys at lower BB + oversold StochRSI, "
        "sells at upper BB + overbought StochRSI. Only active when ADX < 25 "
        "(no trend). Targets the middle band for quick, high-probability trades."
    )
    timeframes = ["1h", "4h"]
    markets = ["crypto", "commodities", "equities"]

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        adx_period: int = 14,
        adx_max: float = 25.0,
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,
        pctb_long_threshold: float = 0.15,
        pctb_short_threshold: float = 0.85,
        stoch_rsi_period: int = 14,
        stoch_k_smooth: int = 3,
        stoch_d_smooth: int = 3,
        stoch_oversold: float = 20.0,
        stoch_overbought: float = 80.0,
        rsi_period: int = 14,
        volume_period: int = 20,
        squeeze_guard_percentile: float = 5.0,
        squeeze_lookback: int = 60,
        tp_target: str = "middle",  # "middle" or "opposite"
    ) -> None:
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.pctb_long_threshold = pctb_long_threshold
        self.pctb_short_threshold = pctb_short_threshold
        self.stoch_rsi_period = stoch_rsi_period
        self.stoch_k_smooth = stoch_k_smooth
        self.stoch_d_smooth = stoch_d_smooth
        self.stoch_oversold = stoch_oversold
        self.stoch_overbought = stoch_overbought
        self.rsi_period = rsi_period
        self.volume_period = volume_period
        self.squeeze_guard_percentile = squeeze_guard_percentile
        self.squeeze_lookback = squeeze_lookback
        self.tp_target = tp_target
        self._min_bars = max(bb_period, squeeze_lookback, 2 * adx_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # Indicators
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        rsi_series = rsi(close, self.rsi_period)
        stoch = stochastic_rsi(
            close, self.stoch_rsi_period, self.stoch_rsi_period,
            self.stoch_k_smooth, self.stoch_d_smooth,
        )
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # Current values
        close_now = close.iloc[-1]
        pctb_now = bb.percent_b.iloc[-1]
        bb_upper = bb.upper.iloc[-1]
        bb_middle = bb.middle.iloc[-1]
        bb_lower = bb.lower.iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        rsi_now = rsi_series.iloc[-1]
        stoch_k = stoch["stoch_rsi_k"].iloc[-1] * 100  # Convert 0-1 to 0-100
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]

        # Guard: NaN check
        if any(pd.isna(v) for v in [pctb_now, adx_now, atr_now, rsi_now, stoch_k]):
            return None

        # ------------------------------------------------------------------
        # Gate 1: Must be range-bound (ADX < threshold)
        # ------------------------------------------------------------------
        if adx_now > self.adx_max:
            logger.debug(
                "BB-MR [%s]: ADX %.1f > %.1f — trending, skip",
                symbol, adx_now, self.adx_max,
            )
            return None

        # ------------------------------------------------------------------
        # Gate 2: Squeeze guard — only active if squeeze_guard_percentile > 0
        # NOTE: Disabled when bollinger_squeeze strategy is off (set percentile=0
        # in YAML). When active, prevents competing with squeeze breakout strategy.
        # ------------------------------------------------------------------
        bb_width = bb.width
        if self.squeeze_guard_percentile > 0:
            squeeze_window = bb_width.iloc[-self.squeeze_lookback:]
            if len(squeeze_window.dropna()) >= 10:
                pct_threshold = squeeze_window.quantile(
                    self.squeeze_guard_percentile / 100.0
                )
                if bb_width.iloc[-1] <= pct_threshold:
                    logger.debug(
                        "BB-MR [%s]: squeeze guard triggered (width=%.6f <= %.6f)",
                        symbol, bb_width.iloc[-1], pct_threshold,
                    )
                    return None  # Extreme squeeze — let bollinger_squeeze handle it

        # ------------------------------------------------------------------
        # Gate 3: Price near band edge + StochRSI confirmation
        # Cross-compensation: if one indicator is extremely strong, relax
        # the other by up to 50%.  This catches trades where e.g. StochRSI
        # is deeply oversold (K=10) but pctB is 0.31 instead of < 0.25.
        # ------------------------------------------------------------------
        direction = None

        # Dynamic threshold relaxation based on cross-indicator strength
        pctb_long_eff = self.pctb_long_threshold
        pctb_short_eff = self.pctb_short_threshold
        stoch_os_eff = self.stoch_oversold
        stoch_ob_eff = self.stoch_overbought

        # If StochK is deeply oversold (<75% of threshold), widen pctB by up to 80%
        if stoch_k < self.stoch_oversold * 0.75:
            depth = 1.0 - stoch_k / (self.stoch_oversold * 0.75)
            pctb_long_eff *= (1.0 + 0.8 * depth)  # e.g. 0.25 -> up to 0.45
        # If pctB is deeply below threshold (<60% of it), widen StochK by up to 60%
        if pctb_now < self.pctb_long_threshold * 0.6:
            depth = 1.0 - pctb_now / (self.pctb_long_threshold * 0.6)
            stoch_os_eff *= (1.0 + 0.6 * depth)  # e.g. 25 -> up to 40

        # Same for SHORT side
        if stoch_k > self.stoch_overbought + (100 - self.stoch_overbought) * 0.25:
            excess = (stoch_k - self.stoch_overbought) / (100 - self.stoch_overbought)
            pctb_short_eff -= (1.0 - self.pctb_short_threshold) * 0.8 * min(excess, 1.0)
        if pctb_now > self.pctb_short_threshold + (1.0 - self.pctb_short_threshold) * 0.4:
            excess = (pctb_now - self.pctb_short_threshold) / (1.0 - self.pctb_short_threshold)
            stoch_ob_eff -= (100 - self.stoch_overbought) * 0.6 * min(excess, 1.0)

        if pctb_now < pctb_long_eff and stoch_k < stoch_os_eff:
            direction = Direction.LONG
        elif pctb_now > pctb_short_eff and stoch_k > stoch_ob_eff:
            direction = Direction.SHORT

        if direction is None:
            # Near-miss logging — show how close we are to a signal
            long_pctb_gap = pctb_now - self.pctb_long_threshold
            short_pctb_gap = self.pctb_short_threshold - pctb_now
            nearest = "LONG" if long_pctb_gap < short_pctb_gap else "SHORT"
            gap = min(long_pctb_gap, short_pctb_gap)
            if gap < 0.15:  # Only log when somewhat close
                logger.info(
                    "BB-MR near-miss [%s]: pctB=%.3f StochK=%.1f ADX=%.1f RSI=%.1f "
                    "| nearest=%s gap=%.3f",
                    symbol, pctb_now, stoch_k, adx_now, rsi_now, nearest, gap,
                )
            return None

        # ------------------------------------------------------------------
        # Stops and targets
        # ------------------------------------------------------------------
        entry_price = close_now

        if direction == Direction.LONG:
            stop_loss = entry_price - (atr_now * self.atr_stop_mult)
            if self.tp_target == "opposite":
                take_profit = bb_upper
            else:
                take_profit = bb_middle
        else:
            stop_loss = entry_price + (atr_now * self.atr_stop_mult)
            if self.tp_target == "opposite":
                take_profit = bb_lower
            else:
                take_profit = bb_middle

        if stop_loss <= 0 or take_profit <= 0:
            return None

        # Ensure TP is in the right direction
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        # ------------------------------------------------------------------
        # Conviction scoring
        # ------------------------------------------------------------------
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 0.0
        conviction = self._score_conviction(
            pctb_now, stoch_k, rsi_now, vol_ratio,
            float(bb_width.iloc[-1]), direction,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "bb_upper": round(bb_upper, 8),
                "bb_middle": round(bb_middle, 8),
                "bb_lower": round(bb_lower, 8),
                "percent_b": round(pctb_now, 4),
                "adx": round(adx_now, 2),
                "rsi": round(rsi_now, 2),
                "stoch_rsi_k": round(stoch_k, 2),
                "volume_ratio": round(vol_ratio, 2),
                "bb_width": round(float(bb_width.iloc[-1]), 6),
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit conditions:
          - Price reaches opposite band (full mean reversion)
          - StochRSI crosses into opposite extreme (momentum exhausted)
          - ADX rises above 30 (trend emerging — exit range trade)
          - Trailing stop hit
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        adx_df = adx(df, self.adx_period)
        stoch = stochastic_rsi(
            close, self.stoch_rsi_period, self.stoch_rsi_period,
            self.stoch_k_smooth, self.stoch_d_smooth,
        )

        close_now = close.iloc[-1]
        pctb_now = bb.percent_b.iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        stoch_k = stoch["stoch_rsi_k"].iloc[-1] * 100

        # Exit if trend emerges (ADX breakout)
        if not pd.isna(adx_now) and adx_now > 30:
            return True

        if position.side == Direction.LONG:
            # Full mean reversion: price reached upper band
            if not pd.isna(pctb_now) and pctb_now > 0.90:
                return True
            # Momentum exhausted: StochRSI overbought
            if not pd.isna(stoch_k) and stoch_k > 85:
                return True
            # Trailing stop
            if position.trailing_stop is not None and close_now <= position.trailing_stop:
                return True
        else:
            # Full mean reversion: price reached lower band
            if not pd.isna(pctb_now) and pctb_now < 0.10:
                return True
            # Momentum exhausted: StochRSI oversold
            if not pd.isna(stoch_k) and stoch_k < 15:
                return True
            # Trailing stop
            if position.trailing_stop is not None and close_now >= position.trailing_stop:
                return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        pctb: float,
        stoch_k: float,
        rsi_val: float,
        vol_ratio: float,
        bb_width: float,
        direction: Direction,
    ) -> float:
        score = 0.0

        # 30%: Band proximity — deeper into the band = higher conviction
        if direction == Direction.LONG:
            band_score = max(0, (self.pctb_long_threshold - pctb) / self.pctb_long_threshold)
        else:
            band_score = max(0, (pctb - self.pctb_short_threshold) / (1.0 - self.pctb_short_threshold))
        score += 0.30 * min(band_score, 1.0)

        # 25%: StochRSI extremity — deeper oversold/overbought = higher conviction
        if direction == Direction.LONG:
            stoch_score = max(0, (self.stoch_oversold - stoch_k) / self.stoch_oversold)
        else:
            stoch_score = max(0, (stoch_k - self.stoch_overbought) / (100 - self.stoch_overbought))
        score += 0.25 * min(stoch_score, 1.0)

        # 20%: Volume confirmation — above-average volume at band edge
        if vol_ratio >= 1.0:
            vol_score = min((vol_ratio - 1.0) / 1.0, 1.0)  # 2x avg = max score
            score += 0.20 * vol_score
        else:
            score += 0.05  # Baseline even without volume spike

        # 15%: RSI alignment — RSI confirming direction boosts conviction
        if direction == Direction.LONG and rsi_val < 45:
            rsi_score = (45 - rsi_val) / 15  # RSI 30 = max score
            score += 0.15 * min(rsi_score, 1.0)
        elif direction == Direction.SHORT and rsi_val > 55:
            rsi_score = (rsi_val - 55) / 15  # RSI 70 = max score
            score += 0.15 * min(rsi_score, 1.0)

        # 10%: BB width — wider bands = more profit room
        width_score = min(bb_width / 0.06, 1.0)  # 6% width = max
        score += 0.10 * width_score

        # Ensure minimum conviction of 0.20 when all gates passed
        score = max(score, 0.20)

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
