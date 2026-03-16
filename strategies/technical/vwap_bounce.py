"""
strategies/technical/vwap_bounce.py — VWAP Intraday Bounce Strategy

Logic
-----
VWAP acts as a dynamic mean for intraday price action.  Institutional order flow
gravitates around it — buying dips to VWAP and selling rallies to VWAP.

LONG signal (all required):
    - Price is above VWAP at session start (higher-timeframe bias is bullish)
    - Price pulls back and touches / slightly penetrates VWAP
    - On the touch bar, a bullish candle forms (close > open)
    - Volume on the touch bar >= 1.2x the session's own average volume so far
    - RSI(14) shows positive divergence: RSI higher than at previous VWAP touch
    - Time filter: trade only in the first 2 hours (09:30-11:30 ET) or last hour
      (15:00-16:00 ET) of the US equity session.  For crypto, use UTC 08:00-10:00
      and 13:00-15:00.

SHORT signal (mirror):
    - Price below VWAP, rallies back to it, bearish rejection candle, volume spike.

Stop loss: 0.5x ATR(14) above/below the VWAP touch.
Take profit: Previous session high/low OR 1.5x ATR from entry.

Conviction scoring
------------------
    +0.40  How cleanly price bounced from VWAP (close distance from VWAP / ATR)
    +0.30  Volume spike relative to session average
    +0.30  RSI divergence strength

Best markets  : SPY, QQQ, large-cap stocks, BTC/USDT 1H during active hours
Best timeframes: 5m, 15m (intraday)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import vwap, rsi, atr


class VWAPBounceStrategy(BaseStrategy):
    """VWAP Intraday Bounce — fades intraday pullbacks to the VWAP anchor."""

    name = "vwap_bounce"
    description = (
        "Intraday mean-reversion bounce off VWAP, confirmed by volume and RSI divergence. "
        "Time-filtered to high-activity windows. Tight ATR-based stops."
    )
    timeframes = ["5m", "15m"]
    markets = ["equities", "crypto", "indices"]

    def __init__(
        self,
        rsi_period: int = 14,
        atr_period: int = 14,
        atr_stop_mult: float = 0.5,
        atr_tp_mult: float = 1.5,
        volume_period: int = 20,
        volume_mult: float = 1.2,
        vwap_touch_pct: float = 0.001,  # 0.1% — how close price must get to VWAP
        active_hours_utc: list[tuple[int, int]] | None = None,
    ) -> None:
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.atr_tp_mult = atr_tp_mult
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.vwap_touch_pct = vwap_touch_pct
        # UTC hour ranges considered "active" — (start_hour, end_hour) inclusive
        self.active_hours_utc: list[tuple[int, int]] = active_hours_utc or [
            (13, 15),  # US market open (09:30-11:30 ET ≈ 13:30-15:30 UTC)
            (20, 21),  # US afternoon push (15:00-16:00 ET ≈ 20:00-21:00 UTC)
        ]
        self._min_bars = max(rsi_period, atr_period, volume_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        vwap_series = vwap(df, reset_daily=True)
        rsi_series = rsi(close, self.rsi_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # Current bar values
        close_now = close.iloc[-1]
        open_now = df["open"].iloc[-1]
        vwap_now = vwap_series.iloc[-1]
        rsi_now = rsi_series.iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # Time filter
        if not self._in_active_hours(df.index[-1]):
            return None

        # Volume filter
        if vol_ratio < self.volume_mult:
            return None

        # VWAP touch detection: is the current bar within touch_pct of VWAP?
        if vwap_now <= 0:
            return None
        price_to_vwap_pct = abs(close_now - vwap_now) / vwap_now
        touching_vwap = price_to_vwap_pct <= self.vwap_touch_pct

        if not touching_vwap:
            return None

        # Determine directional bias from price position relative to VWAP
        # Look at the average of the last 5 bars to gauge trend into the touch
        avg_close_5 = close.iloc[-6:-1].mean()
        bias_long = avg_close_5 > vwap_now
        bias_short = avg_close_5 < vwap_now

        # Candle direction confirmation
        bullish_candle = close_now > open_now
        bearish_candle = close_now < open_now

        # RSI divergence vs previous VWAP touch
        rsi_divergence = self._check_rsi_divergence(close, vwap_series, rsi_series)

        if bias_long and bullish_candle:
            direction = Direction.LONG
        elif bias_short and bearish_candle:
            direction = Direction.SHORT
        else:
            return None

        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now
        tp_dist = self.atr_tp_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = vwap_now - stop_dist
            take_profit = entry_price + tp_dist
        else:
            stop_loss = vwap_now + stop_dist
            take_profit = entry_price - tp_dist

        conviction = self._score_conviction(
            price_to_vwap_pct, vwap_now, atr_now, vol_ratio, rsi_divergence, direction
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
                "vwap": round(vwap_now, 8),
                "rsi": round(rsi_now, 2),
                "atr": round(atr_now, 8),
                "volume_ratio": round(vol_ratio, 2),
                "price_to_vwap_pct": round(price_to_vwap_pct * 100, 4),
                "rsi_divergence": rsi_divergence,
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit when price crosses back through VWAP in the opposite direction."""
        if not self._min_rows(df, self.atr_period + 2):
            return False

        close = df["close"]
        vwap_series = vwap(df, reset_daily=True)
        close_now = close.iloc[-1]
        vwap_now = vwap_series.iloc[-1]

        # End-of-day time stop: exit last bar of active hours
        if self._is_session_end(df.index[-1]):
            return True

        if position.side == Direction.LONG:
            return close_now < vwap_now
        else:
            return close_now > vwap_now

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _in_active_hours(self, ts: pd.Timestamp) -> bool:
        try:
            hour = ts.hour
        except AttributeError:
            return True  # If timestamp has no hour, don't filter
        return any(start <= hour <= end for start, end in self.active_hours_utc)

    def _is_session_end(self, ts: pd.Timestamp) -> bool:
        """Return True if we're in the last 15 minutes of the last active window."""
        try:
            hour = ts.hour
            minute = ts.minute
        except AttributeError:
            return False
        if not self.active_hours_utc:
            return False
        last_end = max(end for _, end in self.active_hours_utc)
        return hour == last_end and minute >= 45

    def _check_rsi_divergence(
        self,
        close: pd.Series,
        vwap_series: pd.Series,
        rsi_series: pd.Series,
    ) -> float:
        """
        Compare RSI at current VWAP touch vs prior VWAP touch.
        Returns positive value for bullish divergence, negative for bearish.
        Range: [-1.0, 1.0]
        """
        # Find the most recent prior bar where price also touched VWAP
        touch_mask = (
            (close - vwap_series).abs() / vwap_series.replace(0, float("nan"))
            <= self.vwap_touch_pct
        )
        prior_touches = touch_mask.iloc[:-1]
        if not prior_touches.any():
            return 0.0

        last_touch_idx = prior_touches[::-1].idxmax()
        rsi_at_prior = rsi_series.loc[last_touch_idx]
        rsi_now = rsi_series.iloc[-1]
        price_at_prior = close.loc[last_touch_idx]
        price_now = close.iloc[-1]

        if price_now > price_at_prior and rsi_now > rsi_at_prior:
            return min((rsi_now - rsi_at_prior) / 30.0, 1.0)  # bullish
        if price_now < price_at_prior and rsi_now < rsi_at_prior:
            return max((rsi_now - rsi_at_prior) / 30.0, -1.0)  # bearish
        return 0.0

    def _score_conviction(
        self,
        touch_pct: float,
        vwap_val: float,
        atr_val: float,
        vol_ratio: float,
        rsi_div: float,
        direction: Direction,
    ) -> float:
        score = 0.0

        # Bounce quality: cleaner touches (very low touch_pct) score higher
        bounce_score = max(0.0, 1.0 - touch_pct / self.vwap_touch_pct)
        score += 0.40 * bounce_score

        # Volume spike
        vol_score = min((vol_ratio - 1.0) / 1.5, 1.0)
        score += 0.30 * max(0.0, vol_score)

        # RSI divergence
        if (direction == Direction.LONG and rsi_div > 0) or (
            direction == Direction.SHORT and rsi_div < 0
        ):
            score += 0.30 * abs(rsi_div)

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
