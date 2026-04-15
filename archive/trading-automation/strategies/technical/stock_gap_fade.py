"""
strategies/technical/stock_gap_fade.py — Stock Gap Fade Strategy

Logic
-----
When a US equity gaps up or down at the open (opens significantly different from
the prior close), there is a statistically proven tendency for the gap to "fill"
— price reverts back toward the prior close — within the first 1-2 hours of the
session.  This strategy fades those gaps.

Gap detection
    A gap is defined as: |today_open - prior_close| / prior_close > min_gap_pct
    Only small-to-medium gaps are faded:
        min_gap_pct = 0.5%  — below this, no meaningful edge
        max_gap_pct = 3.0%  — above this, gap is likely news-driven; do not fade

Entry (SHORT — fading a gap up):
    1. Today's open is > min_gap_pct above prior close (gap up)
    2. Gap size < max_gap_pct
    3. RSI(14) > rsi_overbought on the first bar after the gap
    4. Volume on the gap bar > vol_mult × rolling average
    5. Close is at or above the upper Bollinger Band threshold (percent_b >= bb_zone_pct)

Entry (LONG — fading a gap down):
    1. Today's open is > min_gap_pct below prior close (gap down)
    2. Gap size < max_gap_pct
    3. RSI(14) < rsi_oversold on the first bar after the gap
    4. Volume on the gap bar > vol_mult × rolling average
    5. Close is at or below the lower Bollinger Band threshold (percent_b <= 1 - bb_zone_pct)

Exit levels (set at signal time):
    Take profit : prior_close (the gap fill target)
    Stop loss   : open ± (gap_size × stop_mult)  — beyond the open in the gap direction
    Time stop   : if position is still open after time_stop_bars bars, close it

Conviction scoring:
    Base:   0.50
    +0.15   gap size in sweet spot (sweet_gap_lo – sweet_gap_hi)
    +0.15   RSI extreme (< rsi_extreme_low or > rsi_extreme_high)
    +0.10   prior day was a trend day (ADX > adx_trend_threshold)
    +0.10   volume ratio > vol_extreme_mult

Best markets  : US equities (SPY, QQQ, large-cap single stocks)
Best timeframes: 5m, 15m
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, bollinger_bands, rsi


class StockGapFadeStrategy(BaseStrategy):
    """Fades small-to-medium US equity gaps at the open targeting a full gap fill."""

    name = "stock_gap_fade"
    description = (
        "Detects opening gaps in US equities and fades them with RSI + Bollinger Band "
        "confirmation, targeting the prior close as the gap-fill take-profit level. "
        "A time stop closes any unfilled position after a configurable number of bars."
    )
    timeframes = ["5m", "15m"]
    markets = ["equities"]

    # Market open window in UTC — 09:30 ET = 13:30 UTC
    _MARKET_OPEN_HOUR_UTC: int = 13
    _MARKET_OPEN_MINUTE_UTC: int = 30

    def __init__(
        self,
        # Gap thresholds
        min_gap_pct: float = 0.005,       # 0.5% minimum gap to trade
        max_gap_pct: float = 0.030,       # 3.0% maximum; above = news-driven, skip
        sweet_gap_lo: float = 0.008,      # sweet-spot lower bound (conviction bonus)
        sweet_gap_hi: float = 0.020,      # sweet-spot upper bound (conviction bonus)
        # RSI parameters
        rsi_period: int = 14,
        rsi_overbought: float = 65.0,     # threshold for gap-up fade (SHORT)
        rsi_oversold: float = 35.0,       # threshold for gap-down fade (LONG)
        rsi_extreme_high: float = 75.0,   # extreme level adds conviction
        rsi_extreme_low: float = 25.0,
        # Volume parameters
        volume_period: int = 20,
        vol_mult: float = 1.5,            # minimum volume ratio to qualify
        vol_extreme_mult: float = 2.0,    # extreme volume adds conviction
        # Bollinger Band parameters
        bb_period: int = 20,
        bb_std: float = 2.0,
        bb_zone_pct: float = 0.8,         # percent_b >= 0.8 for gap-up, <= 0.2 for gap-down
        # Exit parameters
        stop_mult: float = 1.5,           # stop = open ± (gap_size × stop_mult)
        time_stop_bars: int = 8,          # close if gap unfilled after N bars
        # ADX parameters
        adx_period: int = 14,
        adx_trend_threshold: float = 25.0,
        # ATR (for _min_bars calculation)
        atr_period: int = 14,
    ) -> None:
        self.min_gap_pct = min_gap_pct
        self.max_gap_pct = max_gap_pct
        self.sweet_gap_lo = sweet_gap_lo
        self.sweet_gap_hi = sweet_gap_hi
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.rsi_extreme_high = rsi_extreme_high
        self.rsi_extreme_low = rsi_extreme_low
        self.volume_period = volume_period
        self.vol_mult = vol_mult
        self.vol_extreme_mult = vol_extreme_mult
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.bb_zone_pct = bb_zone_pct
        self.stop_mult = stop_mult
        self.time_stop_bars = time_stop_bars
        self.adx_period = adx_period
        self.adx_trend_threshold = adx_trend_threshold
        self.atr_period = atr_period

        # Need enough bars to warm up every indicator
        self._min_bars = max(rsi_period, bb_period, volume_period, adx_period * 2) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:  # noqa: C901 — complexity justified
        """
        Run full gap-fade analysis on OHLCV data.

        The current bar (df.iloc[-1]) is expected to be the first bar of the new
        trading day, or shortly after the open.  Gap detection compares df.iloc[-1]
        open to df.iloc[-2] close, so at minimum two bars are needed beyond the
        indicator warm-up period.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol: str = df.attrs.get("symbol", "UNKNOWN")
        current_ts: pd.Timestamp = df.index[-1]

        # Only trade on weekdays
        if current_ts.dayofweek >= 5:
            return None

        # Only enter in the opening window — within the first 90 minutes of US market open
        # so we don't fade gaps that have already had time to resolve or extend
        market_open = current_ts.normalize() + pd.Timedelta(
            hours=self._MARKET_OPEN_HOUR_UTC,
            minutes=self._MARKET_OPEN_MINUTE_UTC,
        )
        # Allow signals from the first bar at open through 90 minutes later
        entry_cutoff = market_open + pd.Timedelta(minutes=90)
        if current_ts < market_open or current_ts > entry_cutoff:
            return None

        # --- Gap detection ---------------------------------------------------
        # Use today's open vs the last close of the prior session.
        # We find the last bar whose timestamp is before today's market open.
        prior_session_bars = df.loc[df.index < market_open]
        if len(prior_session_bars) < 1:
            return None

        prior_close: float = prior_session_bars["close"].iloc[-1]
        today_open: float = df.loc[df.index >= market_open, "open"].iloc[0]

        if prior_close <= 0:
            return None

        raw_gap = today_open - prior_close
        gap_pct = raw_gap / prior_close  # positive = gap up, negative = gap down
        abs_gap_pct = abs(gap_pct)

        if abs_gap_pct < self.min_gap_pct or abs_gap_pct > self.max_gap_pct:
            return None

        # --- Indicator calculations ------------------------------------------
        rsi_series = rsi(df["close"], self.rsi_period)
        rsi_now: float = rsi_series.iloc[-1]
        if pd.isna(rsi_now):
            return None

        bb = bollinger_bands(df["close"], self.bb_period, self.bb_std)
        pct_b: float = bb.percent_b.iloc[-1]
        if pd.isna(pct_b):
            return None

        avg_vol = df["volume"].rolling(self.volume_period).mean()
        avg_vol_now: float = avg_vol.iloc[-1]
        vol_now: float = df["volume"].iloc[-1]
        if avg_vol_now <= 0:
            return None
        vol_ratio: float = vol_now / avg_vol_now

        adx_df = adx(df, self.adx_period)
        adx_now: float = adx_df["adx"].iloc[-1]
        # adx may be NaN if insufficient rows (handled in conviction scorer)

        close_now: float = df["close"].iloc[-1]

        # --- Direction and filter application --------------------------------
        if gap_pct > 0:
            # Gap up — fade SHORT
            if rsi_now <= self.rsi_overbought:
                return None
            if pct_b < self.bb_zone_pct:
                return None
            if vol_ratio < self.vol_mult:
                return None

            direction = Direction.SHORT
            # Stop: gap_size × stop_mult above the open (gap gets worse)
            stop_loss = today_open + abs(raw_gap) * self.stop_mult
            # Take profit: prior close is the gap fill target
            take_profit = prior_close

            # Guard: take_profit must be below current price for a SHORT
            if take_profit >= close_now:
                return None
            if stop_loss <= close_now:
                return None

        elif gap_pct < 0:
            # Gap down — fade LONG
            if rsi_now >= self.rsi_oversold:
                return None
            if pct_b > (1.0 - self.bb_zone_pct):
                return None
            if vol_ratio < self.vol_mult:
                return None

            direction = Direction.LONG
            # Stop: gap_size × stop_mult below the open (gap gets worse)
            stop_loss = today_open - abs(raw_gap) * self.stop_mult
            # Take profit: prior close is the gap fill target
            take_profit = prior_close

            # Guard: take_profit must be above current price for a LONG
            if take_profit <= close_now:
                return None
            if stop_loss >= close_now:
                return None

        else:
            return None  # No gap

        # Ensure stop_loss and take_profit are strictly positive (Signal validation)
        if stop_loss <= 0 or take_profit <= 0:
            return None

        conviction = self._score_conviction(
            abs_gap_pct=abs_gap_pct,
            rsi_value=rsi_now,
            adx_value=adx_now,
            vol_ratio=vol_ratio,
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
                "entry_price": round(close_now, 8),
                "prior_close": round(prior_close, 8),
                "today_open": round(today_open, 8),
                "gap_pct": round(gap_pct * 100, 4),   # expressed as % for readability
                "abs_gap_pct": round(abs_gap_pct * 100, 4),
                "rsi": round(rsi_now, 2),
                "pct_b": round(pct_b, 4),
                "volume_ratio": round(vol_ratio, 2),
                "adx": round(adx_now, 2) if not pd.isna(adx_now) else None,
                "time_stop_bars": self.time_stop_bars,
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit conditions (beyond stop/TP which the engine handles separately):

        1. Time stop — position has been open for >= time_stop_bars bars.
           If the gap hasn't filled in time, momentum has shifted and we close.

        2. Gap has filled — current price has crossed the prior-close level stored
           in the position metadata.  This is a belt-and-suspenders check in case
           the engine's take_profit logic lags by one bar.
        """
        if not self._min_rows(df, 2):
            return False

        # --- Time stop -------------------------------------------------------
        entry_time = position.entry_time
        bars_since_entry = (df.index >= entry_time).sum()
        if bars_since_entry >= self.time_stop_bars:
            return True

        # --- Gap fill check --------------------------------------------------
        prior_close: float | None = position.metadata.get("prior_close")
        if prior_close is not None:
            close_now: float = df["close"].iloc[-1]
            if position.side == Direction.SHORT and close_now <= prior_close:
                return True
            if position.side == Direction.LONG and close_now >= prior_close:
                return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        abs_gap_pct: float,
        rsi_value: float,
        adx_value: float,
        vol_ratio: float,
        direction: Direction,
    ) -> float:
        """
        Build a conviction score from 0.50 base with four additive bonuses.

        Component breakdown:
            0.50  base score — pattern alone has positive expectancy
            0.15  gap in sweet spot (avoids tiny or news-driven gaps)
            0.15  RSI at extreme (stronger mean-reversion signal)
            0.10  prior day was trending (ADX > threshold; gaps after trend days fill more)
            0.10  volume ratio > vol_extreme_mult (institutional participation)
        """
        score: float = 0.50

        # Gap sweet-spot bonus
        if self.sweet_gap_lo <= abs_gap_pct <= self.sweet_gap_hi:
            score += 0.15

        # RSI extreme bonus
        if direction == Direction.SHORT and rsi_value > self.rsi_extreme_high:
            score += 0.15
        elif direction == Direction.LONG and rsi_value < self.rsi_extreme_low:
            score += 0.15

        # ADX trend-day bonus
        if not pd.isna(adx_value) and adx_value > self.adx_trend_threshold:
            score += 0.10

        # Volume extreme bonus
        if vol_ratio >= self.vol_extreme_mult:
            score += 0.10

        # Sign and clamp: SHORT = negative conviction, LONG = positive
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
