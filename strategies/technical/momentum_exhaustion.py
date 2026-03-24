"""
strategies/technical/momentum_exhaustion.py — Momentum Exhaustion / Reversal Strategy

Logic
-----
Catches "exhaustion moves" — when price has moved too far too fast and is primed to snap
back toward the mean.  Designed specifically for choppy/ranging crypto markets where trends
exhaust quickly and mean-reversion dominates.

LONG signal conditions (all four required):
    1. Price has dropped > move_atr_mult × ATR(14) in the last lookback_bars bars
       (panic selling / exhaustion to the downside)
    2. RSI(14) < rsi_oversold (momentum confirms oversold)
    3. Current bar close is ABOVE its low by ≥ reversal_body_pct of bar range
       (hammer / bullish reversal candle)
    4. Volume ≥ volume_mult × 20-bar average (capitulation spike)

SHORT signal conditions (mirror):
    1. Price has risen > move_atr_mult × ATR(14) in the last lookback_bars bars
    2. RSI(14) > rsi_overbought
    3. Current bar close is BELOW its high by ≥ reversal_body_pct of bar range
       (shooting star / bearish reversal candle)
    4. Volume ≥ volume_mult × 20-bar average

Exit: RSI crosses back through rsi_exit (50) OR price crosses the 20-SMA (mean reversion
      complete).

Stop loss:  atr_stop_mult × ATR from entry (tight — mean-reversion plays need discipline).
Take profit: Entry + risk × rr_ratio (2:1 default — quick target, protect the R).

Conviction scoring
------------------
    0.40  base score when all four conditions are met
    +0.15 RSI is extremely oversold/overbought (< rsi_extreme_low or > rsi_extreme_high)
    +0.15 volume is > 2.0× average (strong capitulation)
    +0.15 bar reversal body > 50% of range (strong reversal candle)
    +0.15 ADX < adx_max (ranging market — exhaustion reversals work best in chop)

Best markets  : Choppy/ranging crypto
Best timeframes: 1h, 4h
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, adx, rsi, sma


class MomentumExhaustionStrategy(BaseStrategy):
    """
    Fades exhaustion moves — buys panic dips, sells panic rips.
    Works best in choppy/ranging crypto markets where trends exhaust quickly.
    """

    name = "momentum_exhaustion"
    description = (
        "Fades exhaustion moves — buys panic dips, sells panic rips. "
        "Works best in choppy/ranging crypto."
    )
    timeframes = ["1h", "4h"]
    markets = ["crypto"]

    def __init__(
        self,
        lookback_bars: int = 3,
        move_atr_mult: float = 2.0,
        rsi_period: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        rsi_extreme_low: float = 20.0,
        rsi_extreme_high: float = 80.0,
        rsi_exit: float = 50.0,
        reversal_body_pct: float = 0.30,
        sma_period: int = 20,
        adx_period: int = 14,
        adx_max: float = 25.0,
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,
        rr_ratio: float = 2.0,
        volume_period: int = 20,
        volume_mult: float = 1.5,
    ) -> None:
        self.lookback_bars = lookback_bars
        self.move_atr_mult = move_atr_mult
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi_extreme_low = rsi_extreme_low
        self.rsi_extreme_high = rsi_extreme_high
        self.rsi_exit = rsi_exit
        self.reversal_body_pct = reversal_body_pct
        self.sma_period = sma_period
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self.volume_mult = volume_mult

        # Minimum bars needed before any indicator is reliable.
        # adx() internally requires 2 * adx_period; add lookback_bars on top.
        self._min_bars = (
            max(rsi_period, sma_period, atr_period, 2 * adx_period, volume_period)
            + lookback_bars
            + 5
        )

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # ── Compute indicators ──────────────────────────────────────────
        rsi_series = rsi(close, self.rsi_period)
        atr_series = atr(df, self.atr_period)
        sma_series = sma(close, self.sma_period)
        adx_df = adx(df, self.adx_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # Current-bar scalars
        rsi_now = rsi_series.iloc[-1]
        atr_now = atr_series.iloc[-1]
        sma_now = sma_series.iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        close_now = close.iloc[-1]
        high_now = df["high"].iloc[-1]
        low_now = df["low"].iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]

        # Guard: any NaN in required values means indicators haven't warmed up
        if any(
            v != v  # NaN check without importing math
            for v in (rsi_now, atr_now, sma_now, adx_now, avg_vol_now)
        ):
            return None

        # Guard: zero ATR or zero average volume would cause division errors
        if atr_now <= 0 or avg_vol_now <= 0:
            return None

        vol_ratio = vol_now / avg_vol_now

        # ── Condition 4: volume spike (shared gate) ─────────────────────
        if vol_ratio < self.volume_mult:
            return None

        # ── Condition 1: price move > move_atr_mult × ATR over lookback ─
        # For LONG: price has dropped sharply (panic selling)
        # For SHORT: price has risen sharply (panic buying)
        lookback_close = close.iloc[-self.lookback_bars - 1]  # bar N bars ago
        price_move = close_now - lookback_close  # negative = drop, positive = rise
        move_threshold = self.move_atr_mult * atr_now

        # ── Condition 3: reversal candle body check ─────────────────────
        bar_range = high_now - low_now

        direction: Direction | None = None

        if price_move < -move_threshold:
            # Price dropped hard — look for LONG exhaustion reversal

            # Condition 2: RSI oversold
            if rsi_now >= self.rsi_oversold:
                return None

            # Condition 3: close is above low by ≥ reversal_body_pct of range (hammer)
            if bar_range > 0 and (close_now - low_now) / bar_range < self.reversal_body_pct:
                return None

            direction = Direction.LONG

        elif price_move > move_threshold:
            # Price rose hard — look for SHORT exhaustion reversal

            # Condition 2: RSI overbought
            if rsi_now <= self.rsi_overbought:
                return None

            # Condition 3: close is below high by ≥ reversal_body_pct of range (shooting star)
            if bar_range > 0 and (high_now - close_now) / bar_range < self.reversal_body_pct:
                return None

            direction = Direction.SHORT

        else:
            # Move was not large enough — no exhaustion signal
            return None

        # ── Build signal levels ─────────────────────────────────────────
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now
        tp_dist = stop_dist * self.rr_ratio

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + tp_dist
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - tp_dist

        # Hard safety: prices must be positive and directionally valid
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        # ── Conviction scoring ──────────────────────────────────────────
        conviction = self._score_conviction(
            rsi_val=rsi_now,
            vol_ratio=vol_ratio,
            bar_range=bar_range,
            close_now=close_now,
            high_now=high_now,
            low_now=low_now,
            adx_now=adx_now,
            direction=direction,
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
                "rsi": round(rsi_now, 2),
                "atr": round(atr_now, 8),
                "sma": round(sma_now, 8),
                "adx": round(adx_now, 2),
                "volume_ratio": round(vol_ratio, 2),
                "price_move": round(price_move, 8),
                "move_threshold": round(move_threshold, 8),
                "bar_range": round(bar_range, 8),
                "stop_dist": round(stop_dist, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when RSI crosses back through rsi_exit (50) — mean reversion complete.
        OR when price crosses the 20-SMA — price has returned to the mean.
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        rsi_series = rsi(close, self.rsi_period)
        sma_series = sma(close, self.sma_period)

        rsi_now = rsi_series.iloc[-1]
        close_now = close.iloc[-1]
        sma_now = sma_series.iloc[-1]

        if rsi_now != rsi_now or sma_now != sma_now:
            return False

        if position.side == Direction.LONG:
            rsi_exit = rsi_now >= self.rsi_exit
            price_exit = close_now >= sma_now
            return rsi_exit or price_exit
        else:
            rsi_exit = rsi_now <= self.rsi_exit
            price_exit = close_now <= sma_now
            return rsi_exit or price_exit

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        rsi_val: float,
        vol_ratio: float,
        bar_range: float,
        close_now: float,
        high_now: float,
        low_now: float,
        adx_now: float,
        direction: Direction,
    ) -> float:
        score = 0.40  # Base: all four required conditions are satisfied

        # +0.15 if RSI is extremely oversold/overbought
        if direction == Direction.LONG and rsi_val < self.rsi_extreme_low:
            score += 0.15
        elif direction == Direction.SHORT and rsi_val > self.rsi_extreme_high:
            score += 0.15

        # +0.15 if volume is > 2.0× average (strong capitulation)
        if vol_ratio > 2.0:
            score += 0.15

        # +0.15 if reversal body > 50% of bar range (strong reversal candle)
        if bar_range > 0:
            if direction == Direction.LONG:
                body_pct = (close_now - low_now) / bar_range
            else:
                body_pct = (high_now - close_now) / bar_range
            if body_pct > 0.50:
                score += 0.15

        # +0.15 if ADX < adx_max (ranging market — exhaustion reversals work best in chop)
        if adx_now < self.adx_max:
            score += 0.15

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
