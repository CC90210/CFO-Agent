"""
strategies/technical/london_session_breakout.py — Enhanced London Session Breakout

Thesis
------
The London open (08:00–11:00 UTC) is the highest-liquidity window in global markets.
Institutional flow consistently drives breakouts from the prior Asian session range
(00:00–08:00 UTC), which acts as a coiled spring.  When the range is neither too
narrow (false-breakout risk) nor already expanded (exhausted move), a decisive push
through the Asian high or low with volume confirmation offers a clean, time-bounded
edge with natural stop placement (opposite side of the range).

Gold (XAU_USD) benefits from wider exits because it exhibits larger average true range
and follow-through momentum.  Forex majors (EUR_USD, GBP_USD) use standard exits.

Entry rules (LONG):
    1. Current bar is within 08:00–11:00 UTC entry window.
    2. Close breaks above Asian session high (00:00–08:00 UTC).
    3. Confirmation candle: close > open (bullish bar body).
    4. Asian range >= 0.3 × ATR(14) — range is wide enough to trade.
    5. Asian range <= 2.0 × ATR(14) — range has not already expanded.
    6. ATR(14) > SMA(ATR, 5) — volatility is expanding, not contracting.
    7. RSI(14) between 40 and 70 — not already overbought.

Entry rules (SHORT): mirror image of the above (RSI 30–60).

Exit:
    - Stop loss  : Asian range opposite side, min 1.0 × range width below/above entry.
    - Take profit: 1.5 × range width from breakout level.
    - Gold override (symbol contains "XAU"): SL 1.5 × range, TP 2.5 × range.
    - Time stop  : Close at 16:00 UTC if neither SL nor TP hit (no overnight holds).
    - Structural : Price returns inside Asian range — breakout failed.

Conviction scoring (base 0.50):
    +0.10  Volume > 1.3 × SMA(volume, 20) on breakout bar.
    +0.10  ADX(14) > 25 — trending market, not just noise.
    +0.10  Breakout distance > 0.3 × ATR beyond the level — decisive, not a tick.
    +0.10  Previous day's close in same direction as breakout — trend continuation.
    +0.10  Asian range between 0.5–1.0 × ATR — goldilocks zone, cleanest setups.

Best markets    : XAU_USD (gold), EUR_USD, GBP_USD via OANDA.
Best timeframes : 1h (optimal), 4h (reduced resolution but still functional).

Notes on 4h timeframe
---------------------
On 1h bars the Asian session (00:00–08:00 UTC) produces 8 bars.
On 4h bars it produces only 2 bars (00:00 and 04:00 UTC).  The range is still
calculated correctly; the primary degradation is reduced session resolution.
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, rsi, sma


class LondonSessionBreakoutStrategy(BaseStrategy):
    """
    London open breakout from the Asian session range.

    All threshold parameters are injectable via __init__ so the Darwinian agent
    can evolve them without touching strategy logic.
    """

    name = "london_session_breakout"
    description = (
        "Trades breakouts from the Asian session (00:00–08:00 UTC) range during the "
        "London open (08:00–11:00 UTC).  Optimised for XAU_USD (gold) and forex majors "
        "(EUR_USD, GBP_USD) via OANDA.  Hard time stop closes all positions by 16:00 UTC. "
        "Gold uses wider ATR-based exits (1.5× SL, 2.5× TP) to account for higher volatility."
    )
    timeframes = ["1h", "4h"]
    markets = ["commodities", "forex"]

    # Minimum bars to compute RSI(14), ATR(14), ADX(14), SMA(20) — ADX needs 2×period
    _MIN_BARS: int = 50

    def __init__(
        self,
        # Session hour boundaries (UTC, inclusive/exclusive as noted)
        asian_session_start_hour: int = 0,
        asian_session_end_hour: int = 8,       # bars with hour < 8 are Asian session
        entry_window_start_hour: int = 8,       # entry allowed from 08:00 UTC
        entry_window_end_hour: int = 11,        # no new entries at 11:00 UTC or later
        time_stop_hour: int = 16,               # force-close all positions at 16:00 UTC
        # Range validity filters (multiples of ATR)
        range_min_atr_ratio: float = 0.3,       # range < 0.3×ATR → skip (too narrow)
        range_max_atr_ratio: float = 2.0,       # range > 2.0×ATR → skip (already expanded)
        range_goldilocks_lo: float = 0.5,       # conviction bonus lower bound
        range_goldilocks_hi: float = 1.0,       # conviction bonus upper bound
        # Volatility expansion filter
        atr_period: int = 14,
        atr_sma_period: int = 5,               # ATR must be > SMA(ATR, 5)
        # RSI filter
        rsi_period: int = 14,
        rsi_long_lo: float = 40.0,
        rsi_long_hi: float = 70.0,
        rsi_short_lo: float = 30.0,
        rsi_short_hi: float = 60.0,
        # Standard exit multipliers (non-gold)
        sl_range_mult: float = 1.0,
        tp_range_mult: float = 1.5,
        # Gold-specific exit multipliers
        gold_sl_range_mult: float = 1.5,
        gold_tp_range_mult: float = 2.5,
        # Conviction scoring thresholds
        volume_sma_period: int = 20,
        volume_expansion_factor: float = 1.3,
        adx_period: int = 14,
        adx_trending_threshold: float = 25.0,
        breakout_decisive_atr_ratio: float = 0.3,  # decisive if > 0.3×ATR beyond level
    ) -> None:
        self.asian_session_start_hour = asian_session_start_hour
        self.asian_session_end_hour = asian_session_end_hour
        self.entry_window_start_hour = entry_window_start_hour
        self.entry_window_end_hour = entry_window_end_hour
        self.time_stop_hour = time_stop_hour
        self.range_min_atr_ratio = range_min_atr_ratio
        self.range_max_atr_ratio = range_max_atr_ratio
        self.range_goldilocks_lo = range_goldilocks_lo
        self.range_goldilocks_hi = range_goldilocks_hi
        self.atr_period = atr_period
        self.atr_sma_period = atr_sma_period
        self.rsi_period = rsi_period
        self.rsi_long_lo = rsi_long_lo
        self.rsi_long_hi = rsi_long_hi
        self.rsi_short_lo = rsi_short_lo
        self.rsi_short_hi = rsi_short_hi
        self.sl_range_mult = sl_range_mult
        self.tp_range_mult = tp_range_mult
        self.gold_sl_range_mult = gold_sl_range_mult
        self.gold_tp_range_mult = gold_tp_range_mult
        self.volume_sma_period = volume_sma_period
        self.volume_expansion_factor = volume_expansion_factor
        self.adx_period = adx_period
        self.adx_trending_threshold = adx_trending_threshold
        self.breakout_decisive_atr_ratio = breakout_decisive_atr_ratio

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full London session breakout analysis on the OHLCV DataFrame.

        Returns a Signal when all entry conditions are met, None otherwise.

        Parameters
        ----------
        df : OHLCV DataFrame, UTC DatetimeIndex.
             Required columns: open, high, low, close, volume.
             Minimum length: 50 bars.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._MIN_BARS):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        is_gold = "XAU" in symbol.upper()

        # ---- Time-window gate: only generate signals during entry window -----
        current_bar = df.index[-1]
        current_hour = current_bar.hour

        if not (self.entry_window_start_hour <= current_hour < self.entry_window_end_hour):
            return None

        # ---- Compute indicators ----------------------------------------------
        indicators = self._compute_indicators(df)
        if indicators is None:
            return None

        atr_now, atr_sma_now, rsi_now, adx_now, vol_now, vol_sma_now = indicators

        if any(pd.isna(v) for v in [atr_now, atr_sma_now, rsi_now, adx_now]):
            return None

        # ---- Extract Asian session range for the current trading day ---------
        asian_range = self._get_asian_range(df)
        if asian_range is None:
            return None

        asian_high, asian_low = asian_range
        range_width = asian_high - asian_low

        if range_width <= 0:
            return None

        # ---- Range validity filters ------------------------------------------
        # Too narrow: false breakout risk
        if range_width < self.range_min_atr_ratio * atr_now:
            return None

        # Already expanded: move may be exhausted
        if range_width > self.range_max_atr_ratio * atr_now:
            return None

        # Volatility expansion: ATR must be expanding vs its own short-term SMA
        if atr_now <= atr_sma_now:
            return None

        close_now = df["close"].iloc[-1]
        open_now = df["open"].iloc[-1]

        # ---- Evaluate LONG conditions ----------------------------------------
        long_breakout = close_now > asian_high
        long_confirmation = close_now > open_now  # bullish bar body
        long_rsi_ok = self.rsi_long_lo <= rsi_now <= self.rsi_long_hi

        # ---- Evaluate SHORT conditions ---------------------------------------
        short_breakout = close_now < asian_low
        short_confirmation = close_now < open_now  # bearish bar body
        short_rsi_ok = self.rsi_short_lo <= rsi_now <= self.rsi_short_hi

        if long_breakout and long_confirmation and long_rsi_ok:
            direction = Direction.LONG
        elif short_breakout and short_confirmation and short_rsi_ok:
            direction = Direction.SHORT
        else:
            return None

        # ---- Risk levels (absolute prices) -----------------------------------
        if is_gold:
            sl_mult = self.gold_sl_range_mult
            tp_mult = self.gold_tp_range_mult
        else:
            sl_mult = self.sl_range_mult
            tp_mult = self.tp_range_mult

        if direction == Direction.LONG:
            # SL: Asian low, or entry minus (sl_mult × range), whichever is lower
            sl_from_range_opposite = asian_low
            sl_from_entry = close_now - sl_mult * range_width
            stop_loss = min(sl_from_range_opposite, sl_from_entry)
            take_profit = asian_high + tp_mult * range_width
        else:
            # SL: Asian high, or entry plus (sl_mult × range), whichever is higher
            sl_from_range_opposite = asian_high
            sl_from_entry = close_now + sl_mult * range_width
            stop_loss = max(sl_from_range_opposite, sl_from_entry)
            take_profit = asian_low - tp_mult * range_width

        if stop_loss <= 0 or take_profit <= 0:
            return None

        # ---- Conviction scoring ---------------------------------------------
        conviction = self._score_conviction(
            direction=direction,
            df=df,
            close_now=close_now,
            atr_now=atr_now,
            asian_high=asian_high,
            asian_low=asian_low,
            range_width=range_width,
            adx_now=adx_now,
            vol_now=vol_now,
            vol_sma_now=vol_sma_now,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            strategy_name=self.name,
            metadata={
                "entry_price": close_now,
                "asian_high": round(asian_high, 5),
                "asian_low": round(asian_low, 5),
                "range_width": round(range_width, 5),
                "atr": round(atr_now, 5),
                "rsi": round(rsi_now, 2),
                "adx": round(adx_now, 2),
                "is_gold": is_gold,
                "entry_window_utc": f"{self.entry_window_start_hour:02d}:00–{self.entry_window_end_hour:02d}:00",
                "time_stop_utc": f"{self.time_stop_hour:02d}:00",
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """
        Lightweight entry check called by the high-frequency scanner.
        Returns True when analyze() would produce a non-FLAT signal.
        """
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Structural and time-based exit logic for an open London breakout position.

        The engine handles ATR stop-loss and take-profit levels as hard exits.
        This method handles two additional exit conditions:

        1. Time stop: force-close at 16:00 UTC (no overnight holds).
        2. Structural failure: price returns inside the Asian session range —
           the breakout has failed and the trade thesis is invalidated.

        Parameters
        ----------
        df       : current OHLCV DataFrame (same format as analyze)
        position : the currently open position for this symbol
        """
        if not self._min_rows(df, self._MIN_BARS):
            return False

        current_bar = df.index[-1]
        current_hour = current_bar.hour
        close_now = df["close"].iloc[-1]

        # ---- Time stop: no overnight holds ----------------------------------
        if current_hour >= self.time_stop_hour:
            return True

        # ---- Structural exit: price returned inside Asian range -------------
        asian_range = self._get_asian_range(df)
        if asian_range is not None:
            asian_high, asian_low = asian_range
            if position.side == Direction.LONG and close_now < asian_high:
                # Price has retreated back below breakout level — thesis failed
                return True
            if position.side == Direction.SHORT and close_now > asian_low:
                # Price has reclaimed breakout level — thesis failed
                return True

        return False

    # ------------------------------------------------------------------
    # Indicator computation
    # ------------------------------------------------------------------

    def _compute_indicators(
        self, df: pd.DataFrame
    ) -> tuple[float, float, float, float, float, float] | None:
        """
        Compute all indicators in one place, return latest scalar values.

        Returns
        -------
        Tuple of (atr_now, atr_sma_now, rsi_now, adx_now, vol_now, vol_sma_now)
        or None if computation fails.
        """
        try:
            atr_series = atr(df, self.atr_period)
            atr_now = atr_series.iloc[-1]

            # SMA of ATR over the last atr_sma_period bars — used for expansion filter
            atr_sma_now = sma(atr_series, self.atr_sma_period).iloc[-1]

            rsi_series = rsi(df["close"], self.rsi_period)
            rsi_now = rsi_series.iloc[-1]

            adx_df = adx(df, self.adx_period)
            adx_now = adx_df["adx"].iloc[-1]

            vol_now = df["volume"].iloc[-1]
            vol_sma_now = sma(df["volume"], self.volume_sma_period).iloc[-1]

        except (IndexError, KeyError):
            return None

        return atr_now, atr_sma_now, rsi_now, adx_now, vol_now, vol_sma_now

    # ------------------------------------------------------------------
    # Asian session range extraction
    # ------------------------------------------------------------------

    def _get_asian_range(
        self, df: pd.DataFrame
    ) -> tuple[float, float] | None:
        """
        Extract the high and low of bars belonging to the Asian session
        (hour >= asian_session_start_hour and hour < asian_session_end_hour)
        on the same calendar date as the current (last) bar.

        On 4h timeframes this may return only 2 bars; the range is still valid.

        Returns
        -------
        (asian_high, asian_low) or None if no Asian bars found.
        """
        current_date = df.index[-1].date()

        # Filter to bars on today's date within the Asian session hours
        asian_mask = (
            (df.index.date == current_date)
            & (df.index.hour >= self.asian_session_start_hour)
            & (df.index.hour < self.asian_session_end_hour)
        )
        asian_bars = df[asian_mask]

        if asian_bars.empty:
            return None

        asian_high = float(asian_bars["high"].max())
        asian_low = float(asian_bars["low"].min())

        return asian_high, asian_low

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        df: pd.DataFrame,
        close_now: float,
        atr_now: float,
        asian_high: float,
        asian_low: float,
        range_width: float,
        adx_now: float,
        vol_now: float,
        vol_sma_now: float,
    ) -> float:
        """
        Build conviction from base score plus five optional bonuses.

        Base: 0.50
        +0.10  Volume > volume_expansion_factor × SMA(volume, 20).
        +0.10  ADX(14) > adx_trending_threshold — market is trending.
        +0.10  Breakout distance > breakout_decisive_atr_ratio × ATR beyond level.
        +0.10  Previous day's close supports breakout direction.
        +0.10  Asian range in goldilocks zone (range_goldilocks_lo–range_goldilocks_hi × ATR).

        Result is signed (+ve for LONG, -ve for SHORT) and clamped to [-1, 1].
        """
        score = 0.50

        # Bonus 1: Volume expansion on breakout bar
        if not pd.isna(vol_sma_now) and vol_sma_now > 0:
            if vol_now > self.volume_expansion_factor * vol_sma_now:
                score += 0.10

        # Bonus 2: ADX trending — not just range noise
        if not pd.isna(adx_now) and adx_now > self.adx_trending_threshold:
            score += 0.10

        # Bonus 3: Decisive breakout — not just a single-tick poke through the level
        if atr_now > 0:
            decisive_threshold = self.breakout_decisive_atr_ratio * atr_now
            if direction == Direction.LONG:
                breakout_distance = close_now - asian_high
            else:
                breakout_distance = asian_low - close_now
            if breakout_distance > decisive_threshold:
                score += 0.10

        # Bonus 4: Previous day's close in the same direction as the breakout
        prev_day_close = self._get_previous_day_close(df)
        if prev_day_close is not None:
            current_date = df.index[-1].date()
            # Approximate "today's open" as the first bar's open on today's date
            today_bars = df[df.index.date == current_date]
            if not today_bars.empty:
                today_open = float(today_bars["open"].iloc[0])
                prev_close_bullish = prev_day_close > today_open
                prev_close_bearish = prev_day_close < today_open
                if direction == Direction.LONG and prev_close_bullish:
                    score += 0.10
                elif direction == Direction.SHORT and prev_close_bearish:
                    score += 0.10

        # Bonus 5: Goldilocks zone — range is cleanly sized for this market's volatility
        if atr_now > 0:
            range_atr_ratio = range_width / atr_now
            if self.range_goldilocks_lo <= range_atr_ratio <= self.range_goldilocks_hi:
                score += 0.10

        score = min(score, 1.0)
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    def _get_previous_day_close(self, df: pd.DataFrame) -> float | None:
        """
        Return the closing price of the last bar from the previous calendar day.

        Used by the conviction scorer to determine trend continuation direction.
        Returns None if there is no prior-day data in the DataFrame.
        """
        current_date = df.index[-1].date()
        prior_day_bars = df[df.index.date < current_date]

        if prior_day_bars.empty:
            return None

        return float(prior_day_bars["close"].iloc[-1])
