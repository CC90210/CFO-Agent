"""
strategies/technical/london_breakout.py — London Session Breakout Strategy

Logic
-----
The London open (07:00 UTC) is the highest-liquidity event in FX markets.
Price often breaks aggressively out of the quiet Asian session range.

Asian session range:
    - Window: 00:00 – 07:00 UTC
    - Mark the highest high and lowest low within this window.
    - Range must be at least 0.3x ATR to avoid flat/thin sessions.

Breakout detection (07:00 – 09:00 UTC):
    - LONG:  Close breaks above Asian high with volume surge (>1.5x hour average).
    - SHORT: Close breaks below Asian low with volume surge.

Stop loss:  Opposite end of the Asian range.
Take profit: 1.5x the Asian range size beyond breakout point.
    (e.g., Asian range = 50 pips → TP = 75 pips from breakout level)

Filters:
    - Only valid Monday–Friday (no Sunday opens or holiday sessions).
    - Skip if NFP Friday (first Friday of each month) — too volatile.
    - Skip if Asian range > 2x ATR (unusual overnight volatility — stale range).

Conviction scoring
------------------
    +0.35  Asian range size relative to ATR (tight range → explosive breakout)
    +0.35  Volume on breakout bar
    +0.30  Hour of breakout (07:00-07:30 = highest conviction; 08:00-09:00 = lower)

Best markets  : GBP/USD, EUR/USD, XAU/USD (Gold), USD/JPY
Best timeframes: 15m, 1H (signal generated on 15m bars during the window)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr


class LondonBreakoutStrategy(BaseStrategy):
    """London Session Breakout — trades the directional expansion at the London open."""

    name = "london_breakout"
    description = (
        "Marks the Asian session (00:00-07:00 UTC) high/low, then enters on breakout "
        "at the London open (07:00-09:00 UTC) with volume confirmation. "
        "Stop = opposite end of Asian range. TP = 1.5x range."
    )
    timeframes = ["15m", "1h"]
    markets = ["forex", "commodities"]

    def __init__(
        self,
        asian_start_hour: int = 0,
        asian_end_hour: int = 7,
        breakout_start_hour: int = 7,
        breakout_end_hour: int = 9,
        breakout_vol_mult: float = 1.2,
        min_range_atr_ratio: float = 0.3,
        max_range_atr_ratio: float = 2.0,
        tp_range_mult: float = 1.5,
        atr_period: int = 14,
        volume_period: int = 20,
        avoid_nfp: bool = True,
    ) -> None:
        self.asian_start_hour = asian_start_hour
        self.asian_end_hour = asian_end_hour
        self.breakout_start_hour = breakout_start_hour
        self.breakout_end_hour = breakout_end_hour
        self.breakout_vol_mult = breakout_vol_mult
        self.min_range_atr_ratio = min_range_atr_ratio
        self.max_range_atr_ratio = max_range_atr_ratio
        self.tp_range_mult = tp_range_mult
        self.atr_period = atr_period
        self.volume_period = volume_period
        self.avoid_nfp = avoid_nfp
        self._min_bars = max(atr_period, volume_period, 96) + 5  # 96 bars = 1 day on 15m

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        current_ts: pd.Timestamp = df.index[-1]

        # Day-of-week filter
        if not self._is_valid_trading_day(current_ts):
            return None

        # Time filter: must be in London breakout window
        if not (self.breakout_start_hour <= current_ts.hour < self.breakout_end_hour):
            return None

        # Build today's Asian session range
        today_date = current_ts.normalize()
        asian_start = today_date + pd.Timedelta(hours=self.asian_start_hour)
        asian_end = today_date + pd.Timedelta(hours=self.asian_end_hour)
        asian_bars = df.loc[(df.index >= asian_start) & (df.index < asian_end)]

        if len(asian_bars) < 3:
            return None  # Not enough Asian session data

        asian_high = asian_bars["high"].max()
        asian_low = asian_bars["low"].min()
        asian_range = asian_high - asian_low

        atr_series = atr(df, self.atr_period)
        atr_now = atr_series.iloc[-1]

        if atr_now <= 0:
            return None

        # Range validity checks
        range_ratio = asian_range / atr_now
        if range_ratio < self.min_range_atr_ratio:
            return None  # Too thin — no breakout setup
        if range_ratio > self.max_range_atr_ratio:
            return None  # Too wide — unusual overnight session, skip

        avg_vol = df["volume"].rolling(self.volume_period).mean()
        close_now = df["close"].iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # Volume filter
        if vol_ratio < self.breakout_vol_mult:
            return None

        # Breakout direction
        if close_now > asian_high:
            direction = Direction.LONG
            stop_loss = asian_low
            take_profit = asian_high + asian_range * self.tp_range_mult
        elif close_now < asian_low:
            direction = Direction.SHORT
            stop_loss = asian_high
            take_profit = asian_low - asian_range * self.tp_range_mult
        else:
            return None  # No breakout yet

        conviction = self._score_conviction(
            range_ratio, vol_ratio, current_ts.hour, direction
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
                "asian_high": round(asian_high, 8),
                "asian_low": round(asian_low, 8),
                "asian_range": round(asian_range, 8),
                "range_atr_ratio": round(range_ratio, 4),
                "volume_ratio": round(vol_ratio, 2),
                "breakout_hour": current_ts.hour,
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit at end of London session (14:00 UTC) if still open."""
        if not self._min_rows(df, 2):
            return False
        current_ts: pd.Timestamp = df.index[-1]
        # London session extends to US equity open — time stop at 16:00 UTC
        return current_ts.hour >= 16

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_valid_trading_day(self, ts: pd.Timestamp) -> bool:
        """Return False on weekends and NFP Fridays."""
        # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
        if ts.dayofweek >= 5:
            return False
        if self.avoid_nfp and ts.dayofweek == 4:
            # First Friday of the month = NFP
            if ts.day <= 7:
                return False
        return True

    def _score_conviction(
        self,
        range_ratio: float,
        vol_ratio: float,
        breakout_hour: int,
        direction: Direction,
    ) -> float:
        score = 0.0

        # Tight range → more explosive breakout expected
        # range_ratio close to min_range = tightest (highest conviction)
        # cap at max_range
        tightness = max(0.0, 1.0 - (range_ratio - self.min_range_atr_ratio) / (
            self.max_range_atr_ratio - self.min_range_atr_ratio
        ))
        score += 0.35 * tightness

        # Volume surge
        vol_score = min((vol_ratio - 1.0) / 2.0, 1.0)
        score += 0.35 * max(0.0, vol_score)

        # Timing: first 30 minutes of London open is highest conviction
        if breakout_hour == self.breakout_start_hour:
            score += 0.30
        elif breakout_hour == self.breakout_start_hour + 1:
            score += 0.15

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
