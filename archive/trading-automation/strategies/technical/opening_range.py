"""
strategies/technical/opening_range.py — Opening Range Breakout (ORB) Strategy

Logic
-----
The first 15 minutes of US equity trading (09:30–09:45 ET / 13:30–13:45 UTC)
establish the Opening Range.  Price tends to trend in the direction of the
first break out of this range for the rest of the morning session.

Opening Range:
    - Window: 09:30 – 09:45 ET (13:30 – 13:45 UTC)
    - Mark the high and low of all bars within this window.
    - Range must be > 0.5x ATR (active open) and < 2x ATR (not gap-driven chaos).

Breakout signal (after 09:45 ET / 13:45 UTC):
    - LONG:  Close above OR high with volume > 1.5x the day's average so far.
    - SHORT: Close below OR low with volume > 1.5x the day's average so far.

Gap filter:
    - If the prior day's close vs today's open gap is > 2%, skip the session.
      Gaps cause fake breakouts as price fills back.

Stop loss:  Opposite end of the Opening Range.
Take profit: 1.5x the Opening Range size beyond breakout level, OR 3:1 R:R (whichever
             is farther from entry — most favourable).

Time stop:  Close all positions by 15:30 ET (20:30 UTC) regardless of P&L.

Conviction scoring
------------------
    +0.35  Volume surge on breakout bar
    +0.35  OR size relative to ATR (moderate range = most reliable)
    +0.30  How far the breakout closed beyond the OR level (momentum)

Best markets  : SPY, QQQ, AAPL, NVDA, high-beta large-caps, ES futures
Best timeframes: 5m (build OR from 5m bars)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr


class OpeningRangeStrategy(BaseStrategy):
    """Opening Range Breakout — intraday trend-following from the first 15-min range."""

    name = "opening_range"
    description = (
        "Marks the US equity Opening Range (first 15 minutes of trading), then enters "
        "on the first breakout with volume confirmation. Gap filter prevents trading "
        "volatile gap opens. Time stop at 15:30 ET."
    )
    timeframes = ["5m"]
    markets = ["equities", "indices", "futures"]

    def __init__(
        self,
        or_start_hour_utc: int = 13,
        or_start_minute_utc: int = 30,
        or_end_hour_utc: int = 13,
        or_end_minute_utc: int = 45,
        time_stop_hour_utc: int = 20,
        time_stop_minute_utc: int = 30,
        breakout_vol_mult: float = 1.5,
        gap_filter_pct: float = 0.015,
        min_range_atr_ratio: float = 0.75,
        max_range_atr_ratio: float = 1.5,
        tp_range_mult: float = 1.5,
        rr_ratio: float = 3.0,
        atr_period: int = 14,
        volume_period: int = 20,
    ) -> None:
        self.or_start_hour_utc = or_start_hour_utc
        self.or_start_minute_utc = or_start_minute_utc
        self.or_end_hour_utc = or_end_hour_utc
        self.or_end_minute_utc = or_end_minute_utc
        self.time_stop_hour_utc = time_stop_hour_utc
        self.time_stop_minute_utc = time_stop_minute_utc
        self.breakout_vol_mult = breakout_vol_mult
        self.gap_filter_pct = gap_filter_pct
        self.min_range_atr_ratio = min_range_atr_ratio
        self.max_range_atr_ratio = max_range_atr_ratio
        self.tp_range_mult = tp_range_mult
        self.rr_ratio = rr_ratio
        self.atr_period = atr_period
        self.volume_period = volume_period
        self._min_bars = max(atr_period, volume_period, 20) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        current_ts: pd.Timestamp = df.index[-1]

        # Must be after OR is established
        or_end = current_ts.normalize() + pd.Timedelta(
            hours=self.or_end_hour_utc, minutes=self.or_end_minute_utc
        )
        if current_ts <= or_end:
            return None

        # Time stop: don't enter new trades after session cutoff
        time_stop = current_ts.normalize() + pd.Timedelta(
            hours=self.time_stop_hour_utc, minutes=self.time_stop_minute_utc
        )
        if current_ts >= time_stop:
            return None

        # Weekday filter
        if current_ts.dayofweek >= 5:
            return None

        # Build Opening Range for today
        or_start = current_ts.normalize() + pd.Timedelta(
            hours=self.or_start_hour_utc, minutes=self.or_start_minute_utc
        )
        or_bars = df.loc[(df.index >= or_start) & (df.index < or_end)]

        if len(or_bars) < 1:
            return None

        or_high = or_bars["high"].max()
        or_low = or_bars["low"].min()
        or_range = or_high - or_low

        atr_series = atr(df, self.atr_period)
        atr_now = atr_series.iloc[-1]

        if atr_now <= 0:
            return None

        range_ratio = or_range / atr_now

        # Range validity
        if range_ratio < self.min_range_atr_ratio or range_ratio > self.max_range_atr_ratio:
            return None

        # Gap filter: compare prior close to today's open
        today_open = df.loc[df.index >= or_start, "open"].iloc[0] if len(
            df.loc[df.index >= or_start]
        ) > 0 else None
        prior_close_bars = df.loc[df.index < or_start]
        if today_open is not None and len(prior_close_bars) > 0:
            prior_close = prior_close_bars["close"].iloc[-1]
            if prior_close > 0:
                gap_pct = abs(today_open - prior_close) / prior_close
                if gap_pct > self.gap_filter_pct:
                    return None

        avg_vol = df["volume"].rolling(self.volume_period).mean()
        close_now = df["close"].iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # Volume filter
        if vol_ratio < self.breakout_vol_mult:
            return None

        # Breakout direction
        if close_now > or_high:
            direction = Direction.LONG
            breakout_distance = close_now - or_high
            stop_loss = or_low
            tp_range = or_high + or_range * self.tp_range_mult
            tp_rr = close_now + (close_now - or_low) * (self.rr_ratio - 1.0)
            take_profit = max(tp_range, tp_rr)
        elif close_now < or_low:
            direction = Direction.SHORT
            breakout_distance = or_low - close_now
            stop_loss = or_high
            tp_range = or_low - or_range * self.tp_range_mult
            tp_rr = close_now - (or_high - close_now) * (self.rr_ratio - 1.0)
            take_profit = min(tp_range, tp_rr)
        else:
            return None  # No breakout yet

        conviction = self._score_conviction(
            vol_ratio, range_ratio, breakout_distance, or_range, direction
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": close_now,
                "or_high": round(or_high, 8),
                "or_low": round(or_low, 8),
                "or_range": round(or_range, 8),
                "range_atr_ratio": round(range_ratio, 4),
                "volume_ratio": round(vol_ratio, 2),
                "breakout_distance": round(breakout_distance, 8),
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit at time stop regardless of P&L."""
        if not self._min_rows(df, 2):
            return False
        current_ts: pd.Timestamp = df.index[-1]
        time_stop = current_ts.normalize() + pd.Timedelta(
            hours=self.time_stop_hour_utc, minutes=self.time_stop_minute_utc
        )
        return current_ts >= time_stop

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        vol_ratio: float,
        range_ratio: float,
        breakout_distance: float,
        or_range: float,
        direction: Direction,
    ) -> float:
        score = 0.0

        # Volume surge
        vol_score = min((vol_ratio - 1.0) / 2.0, 1.0)
        score += 0.35 * max(0.0, vol_score)

        # Range quality: moderate range is most reliable
        # Score peaks around 1.0x ATR, drops off for very tight or very wide ranges
        ideal_ratio = (self.min_range_atr_ratio + self.max_range_atr_ratio) / 2.0
        range_score = 1.0 - abs(range_ratio - ideal_ratio) / ideal_ratio
        score += 0.35 * max(0.0, range_score)

        # Breakout momentum: how far did the close go beyond the OR level
        if or_range > 0:
            momentum = min(breakout_distance / or_range, 1.0)
            score += 0.30 * momentum

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
