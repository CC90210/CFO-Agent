"""
strategies/technical/ema_crossover.py — EMA Crossover Momentum Strategy

Logic
-----
Fast EMA (12) crossing above Slow EMA (26) generates a LONG signal.
Fast EMA crossing below Slow EMA generates a SHORT signal.

Confirmation filters (all three must align):
    1. MACD histogram polarity matches direction (positive = bullish, negative = bearish).
    2. ADX > 25 — only trade in trending markets, avoid whipsaws in ranging conditions.
    3. Volume on signal bar >= 1x 20-bar average volume (optional but scored).

Stop loss: 2x ATR(14) below entry for LONG, above entry for SHORT.
Take profit: 3:1 risk-reward ratio (6x ATR distance).

Conviction scoring
------------------
    +0.30  ADX strength normalised to [0, 0.30] (ADX 25 → 0, ADX 50+ → 0.30)
    +0.30  MACD histogram momentum normalised to [0, 0.30]
    +0.20  Volume confirmation (>1.5x average → full 0.20, else scaled)
    +0.20  EMA separation (fast–slow gap normalised to recent ATR)
    Total possible: 1.0 per direction

Best markets  : BTC/USDT, ETH/USDT, SPY, QQQ, liquid FX pairs
Best timeframes: 1H, 4H, Daily
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import ema, macd, atr, adx


class EMACrossoverStrategy(BaseStrategy):
    """EMA Crossover Momentum — trend-following via dual-EMA crossover system."""

    name = "ema_crossover"
    description = (
        "Dual EMA crossover (12/26) confirmed by MACD polarity, ADX trend filter, "
        "and volume. ATR-based stops with 3:1 R:R."
    )
    timeframes = ["1h", "4h", "1d"]
    markets = ["crypto", "equities", "forex"]

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        adx_period: int = 14,
        adx_threshold: float = 20.0,
        atr_period: int = 14,
        atr_stop_mult: float = 3.0,
        rr_ratio: float = 3.0,
        volume_period: int = 20,
    ) -> None:
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self._min_bars = max(slow_period, adx_period, atr_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        fast_ema = ema(close, self.fast_period)
        slow_ema = ema(close, self.slow_period)
        macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # Current, previous, and 2-bars-ago values for confirmation
        f_now, f_prev, f_prev2 = fast_ema.iloc[-1], fast_ema.iloc[-2], fast_ema.iloc[-3]
        s_now, s_prev, s_prev2 = slow_ema.iloc[-1], slow_ema.iloc[-2], slow_ema.iloc[-3]
        hist_now = macd_df["histogram"].iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        entry_price = close.iloc[-1]

        # Confirmation bar: crossover happened on PREVIOUS bar, current bar confirms
        crossed_up = (f_prev2 <= s_prev2) and (f_prev > s_prev) and (f_now > s_now)
        crossed_down = (f_prev2 >= s_prev2) and (f_prev < s_prev) and (f_now < s_now)

        # ADX filter — reject signals in ranging markets
        trending = adx_now >= self.adx_threshold

        if not trending:
            return None
        if not (crossed_up or crossed_down):
            return None

        # MACD histogram polarity confirmation
        if crossed_up and hist_now <= 0:
            return None
        if crossed_down and hist_now >= 0:
            return None

        direction = Direction.LONG if crossed_up else Direction.SHORT
        conviction = self._score_conviction(
            adx_now, hist_now, vol_now, avg_vol_now,
            f_now, s_now, atr_now, direction,
        )

        # Stop loss and take profit
        stop_dist = self.atr_stop_mult * atr_now
        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + stop_dist * self.rr_ratio
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - stop_dist * self.rr_ratio

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "fast_ema": round(f_now, 8),
                "slow_ema": round(s_now, 8),
                "macd_histogram": round(hist_now, 8),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 8),
                "volume_ratio": round(vol_now / avg_vol_now, 2) if avg_vol_now else None,
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit on EMA crossover in the opposite direction."""
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        fast_ema = ema(close, self.fast_period)
        slow_ema = ema(close, self.slow_period)

        f_now, f_prev = fast_ema.iloc[-1], fast_ema.iloc[-2]
        s_now, s_prev = slow_ema.iloc[-1], slow_ema.iloc[-2]

        if position.side == Direction.LONG:
            # Exit on bearish crossover
            return (f_prev >= s_prev) and (f_now < s_now)
        else:
            # Exit on bullish crossover
            return (f_prev <= s_prev) and (f_now > s_now)

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        adx_val: float,
        hist: float,
        vol: float,
        avg_vol: float,
        fast: float,
        slow: float,
        atr_val: float,
        direction: Direction,
    ) -> float:
        score = 0.0

        # ADX component: 0 at threshold, max 0.30 at ADX 50+
        adx_norm = min((adx_val - self.adx_threshold) / (50.0 - self.adx_threshold), 1.0)
        score += 0.30 * max(0.0, adx_norm)

        # MACD histogram momentum: normalise over recent ATR
        if atr_val > 0:
            hist_norm = min(abs(hist) / atr_val, 1.0)
            score += 0.30 * hist_norm

        # Volume confirmation
        if avg_vol > 0:
            vol_ratio = vol / avg_vol
            vol_score = min(vol_ratio / 1.5, 1.0)  # full score at 1.5x average
            score += 0.20 * vol_score

        # EMA separation
        if atr_val > 0:
            sep = abs(fast - slow) / atr_val
            sep_norm = min(sep / 2.0, 1.0)  # full score at 2x ATR separation
            score += 0.20 * sep_norm

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
