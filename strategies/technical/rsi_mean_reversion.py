"""
strategies/technical/rsi_mean_reversion.py — RSI Mean Reversion Strategy

Logic
-----
Profit from price mean-reverting after short-term exhaustion moves.

LONG signal conditions (all required):
    - RSI(14) < 25 (deeply oversold — tighter threshold reduces false signals)
    - Close <= Bollinger Band lower (price at statistical extreme)
    - Volume >= 1.5x 20-period average (capitulation spike confirms reversal)
    - ADX < 25 (market is range-bound — mean reversion works, trend-following fails)
    - Price >= 200 EMA (trend filter — only fade dips in a macro uptrend; requires 210+ bars)

SHORT signal conditions (mirror):
    - RSI(14) > 75 (deeply overbought)
    - Close >= Bollinger Band upper
    - Volume >= 1.5x average
    - ADX < 25
    - Price <= 200 EMA (trend filter — only fade rallies in a macro downtrend; requires 210+ bars)

Exit trigger: RSI returns to 50 (mean), OR price crosses the Bollinger midline.

Stop loss:  1.0x ATR(14) beyond entry — tighter stop improves R:R.
Take profit: Bollinger midline OR 2x stop distance (whichever is greater) — enforces 2:1 R:R floor.

Conviction scoring
------------------
    +0.35  RSI distance from extreme (deeper = more conviction)
    +0.35  Bollinger %B position (0 = at lower band, negative = below → more extreme)
    +0.30  Volume spike magnitude (>2x average = max score)

Best markets  : Range-bound assets, BTC/USDT on sideways weeks, SPY inside trading ranges
Best timeframes: 15m, 1H
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import rsi, bollinger_bands, atr, adx, ema


class RSIMeanReversionStrategy(BaseStrategy):
    """RSI + Bollinger Band mean-reversion — fades exhaustion moves in ranging markets."""

    name = "rsi_mean_reversion"
    description = (
        "RSI < 30 / > 70 combined with price at Bollinger extremes and volume spike, "
        "filtered to range-bound regimes via ADX < 25. Target: reversion to BB midline."
    )
    timeframes = ["15m", "1h"]
    markets = ["crypto", "equities", "forex"]

    def __init__(
        self,
        rsi_period: int = 14,
        rsi_oversold: float = 28.0,
        rsi_overbought: float = 72.0,
        rsi_exit: float = 50.0,
        bb_period: int = 20,
        bb_std: float = 2.0,
        adx_period: int = 14,
        adx_max: float = 25.0,
        atr_period: int = 14,
        atr_stop_mult: float = 1.0,
        volume_period: int = 20,
        volume_mult: float = 1.2,
        ema_trend_period: int = 200,
        rr_min: float = 2.0,
    ) -> None:
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi_exit = rsi_exit
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        # 200 EMA trend filter — only applied when sufficient history is available.
        # Requiring ema_trend_period + 10 bars prevents distorted EMA readings on
        # cold-start data where the exponential smoothing hasn't converged yet.
        self.ema_trend_period = ema_trend_period
        self._ema_min_bars = ema_trend_period + 10
        # Minimum risk:reward ratio enforced on every signal.
        self.rr_min = rr_min
        self._min_bars = max(rsi_period, bb_period, adx_period, atr_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        rsi_series = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        rsi_now = rsi_series.iloc[-1]
        close_now = close.iloc[-1]
        bb_upper = bb.upper.iloc[-1]
        bb_lower = bb.lower.iloc[-1]
        bb_mid = bb.middle.iloc[-1]
        bb_pct = bb.percent_b.iloc[-1]  # 0 = at lower band, 1 = at upper band
        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # ADX filter — only operate in ranging markets
        if adx_now >= self.adx_max:
            return None

        # Volume confirmation required — above-average volume on the signal bar
        if vol_ratio < self.volume_mult:
            return None

        # 200 EMA trend filter — only active when enough bars exist for a reliable read.
        # Avoids fading dips in a macro downtrend (LONG) or rallies in an uptrend (SHORT).
        ema_trend: float | None = None
        if len(df) >= self._ema_min_bars:
            ema_series = ema(close, self.ema_trend_period)
            ema_trend = ema_series.iloc[-1]

        direction: Direction | None = None

        if rsi_now < self.rsi_oversold and close_now <= bb_lower:
            # Trend filter: skip LONG if price is in a macro downtrend
            if ema_trend is not None and close_now < ema_trend:
                return None
            direction = Direction.LONG
        elif rsi_now > self.rsi_overbought and close_now >= bb_upper:
            # Trend filter: skip SHORT if price is in a macro uptrend
            if ema_trend is not None and close_now > ema_trend:
                return None
            direction = Direction.SHORT

        if direction is None:
            return None

        entry_price = close_now
        # Stop loss: 1.0x ATR — tighter stop to improve R:R
        stop_dist = self.atr_stop_mult * atr_now
        # Take profit: BB midline OR rr_min * stop_dist, whichever gives a larger move.
        # This enforces a minimum 2:1 R:R on every trade.
        min_tp_dist = self.rr_min * stop_dist

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            bb_mid_dist = bb_mid - entry_price
            take_profit = entry_price + max(bb_mid_dist, min_tp_dist)
        else:
            stop_loss = entry_price + stop_dist
            bb_mid_dist = entry_price - bb_mid
            take_profit = entry_price - max(bb_mid_dist, min_tp_dist)

        # Hard safety: ensure take_profit is directionally valid and positive
        if direction == Direction.LONG and take_profit <= entry_price:
            take_profit = entry_price + min_tp_dist
        if direction == Direction.SHORT and take_profit >= entry_price:
            take_profit = entry_price - min_tp_dist
        if take_profit <= 0:
            return None

        conviction = self._score_conviction(rsi_now, bb_pct, vol_ratio, direction)

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
                "bb_upper": round(bb_upper, 8),
                "bb_lower": round(bb_lower, 8),
                "bb_mid": round(bb_mid, 8),
                "bb_pct_b": round(bb_pct, 4),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 8),
                "volume_ratio": round(vol_ratio, 2),
                "ema_trend": round(ema_trend, 8) if ema_trend is not None else None,
                "stop_dist": round(stop_dist, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit when RSI returns to 50 OR price crosses the Bollinger midline."""
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        rsi_series = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)

        rsi_now = rsi_series.iloc[-1]
        close_now = close.iloc[-1]
        bb_mid = bb.middle.iloc[-1]

        if position.side == Direction.LONG:
            # RSI mean-reversion complete, or price has crossed above midline
            rsi_exit = rsi_now >= self.rsi_exit
            price_exit = close_now >= bb_mid
            return rsi_exit or price_exit
        else:
            rsi_exit = rsi_now <= self.rsi_exit
            price_exit = close_now <= bb_mid
            return rsi_exit or price_exit

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        rsi_val: float,
        pct_b: float,
        vol_ratio: float,
        direction: Direction,
    ) -> float:
        score = 0.0

        # RSI distance from extreme (deeper = more conviction)
        if direction == Direction.LONG:
            rsi_extreme = self.rsi_oversold - rsi_val  # positive when below oversold
            rsi_norm = min(rsi_extreme / self.rsi_oversold, 1.0)
        else:
            rsi_extreme = rsi_val - self.rsi_overbought
            rsi_norm = min(rsi_extreme / (100.0 - self.rsi_overbought), 1.0)
        score += 0.35 * max(0.0, rsi_norm)

        # Bollinger %B position (0 = at lower band, -∞ = below)
        if direction == Direction.LONG:
            bb_extreme = -pct_b  # negative pct_b = price below lower band
            bb_norm = min(max(bb_extreme, 0.0), 1.0)
        else:
            bb_extreme = pct_b - 1.0  # pct_b > 1.0 = price above upper band
            bb_norm = min(max(bb_extreme, 0.0), 1.0)
        score += 0.35 * bb_norm

        # Volume spike
        vol_score = min((vol_ratio - self.volume_mult) / self.volume_mult + 1.0, 1.0)
        score += 0.30 * max(0.0, vol_score)

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
