"""
strategies/technical/london_fade.py — London Breakout FADE (Contrarian) Strategy

Thesis
------
Research shows 60-70% of Asian range breakouts fail and reverse within the first 2-3 hours
of the London session.  Rather than trading WITH a breakout, this strategy waits for a
CONFIRMED false breakout — price pokes through the Asian range boundary, fails to attract
follow-through, then reclaims the boundary — and trades the reversal back toward the
opposite side of the range.

The setup is best in non-trending, choppy markets (ADX < 30) where mean reversion
dominates.  The Asian range acts as a magnetic attractor: once a failed breakout is
confirmed the range midpoint and far wall are the natural targets.

Asian session range (00:00–08:00 UTC):
    - Window:  00:00–08:00 UTC (same as london_session_breakout for consistency).
    - Mark the highest high (asian_high) and lowest low (asian_low) within that window.
    - Range must be >= 0.3 × ATR(14) — wide enough to be meaningful.
    - Range must be <= 1.5 × ATR(14) — if too wide the breakout may be genuine.

False-breakout detection (looks back 3 bars):
    - SHORT false breakout (LONG fade entry):
        * Any of the last 3 bars had a LOW below asian_low (the break happened).
        * Current close is ABOVE asian_low (price reclaimed the level).
        * Current bar is bullish: close > open.
        * RSI(14) reached <= 35 during the false-break window (oversold spike).
        * RSI(14) is now > 40 (momentum recovering).

    - LONG false breakout (SHORT fade entry): mirror of the above.
        * Any of the last 3 bars had a HIGH above asian_high.
        * Current close is BELOW asian_high.
        * Current bar is bearish: close < open.
        * RSI(14) reached >= 65 during the false-break window (overbought spike).
        * RSI(14) is now < 60.

Entry window:  08:00–12:00 UTC (wider than breakout strategies — fades develop later).

Exit:
    - Stop loss  : 1.0 × range_width beyond the false breakout extreme.
                   Gold (XAU): 1.5 × range_width (wider volatility).
    - Take profit: Opposite side of the Asian range (full range reversion target).
    - Time stop  : 14:00 UTC — no afternoon / overnight holds.
    - Structural : Price prints a new extreme beyond the false-breakout level — the
                   breakout was real after all, the thesis is invalidated.

Conviction scoring (base 0.50):
    +0.10  Volume declining on breakout bar vs prior bar (exhaustion — no follow-through).
    +0.10  Wick > 60 % of bar height on the false-breakout bar (sharp rejection).
    +0.10  Price has returned > 50 % of the way back into the Asian range (strong fade).
    +0.10  ADX(14) < 20 — strongly non-trending, ideal fading conditions.
    +0.10  Asian range in goldilocks zone: 0.5–1.0 × ATR.

Conviction is SIGNED: positive for LONG, negative for SHORT, clamped to [-1, 1].

Best markets    : XAU_USD (gold), EUR_USD, GBP_USD via OANDA.
Best timeframes : 1h.

Notes on gold
-------------
Gold exhibits larger intra-day swings.  The false-breakout bar's wick can be very large
even on a genuine reversal.  To compensate, the SL for gold is widened to 1.5 × range
(same multiplier applied in london_session_breakout).  The TP (opposite range wall)
remains unchanged — the fade target is structural, not volatility-adjusted.
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, rsi, sma


class LondonFadeStrategy(BaseStrategy):
    """
    London Breakout FADE — contrarian strategy that trades failed Asian range breakouts.

    All threshold parameters are injectable via __init__ so the Darwinian agent
    can evolve them without touching strategy logic.
    """

    name = "london_fade"
    description = (
        "Trades the REVERSAL of failed Asian session (00:00–08:00 UTC) range breakouts "
        "during the London morning (08:00–12:00 UTC).  Detects false breakouts (price "
        "pokes through the Asian range but closes back inside) then fades the move "
        "back toward the opposite range wall.  ADX < 30 filter ensures this only fires "
        "in non-trending, mean-reverting conditions.  Hard time stop at 14:00 UTC."
    )
    timeframes = ["1h"]
    markets = ["forex", "commodities"]

    # ADX needs 2 × period bars; 50 is well above max(14×2, 20) + safety margin.
    _MIN_BARS: int = 50

    def __init__(
        self,
        # Session boundaries (UTC)
        asian_session_start_hour: int = 0,
        asian_session_end_hour: int = 8,
        entry_window_start_hour: int = 8,
        entry_window_end_hour: int = 12,
        time_stop_hour: int = 14,
        # False-breakout lookback window (bars)
        false_breakout_lookback: int = 5,        # Widened from 3 — gives more bars to detect the false breakout
        # Range validity filters (multiples of ATR)
        range_min_atr_ratio: float = 0.2,        # Relaxed from 0.3 — allow narrower ranges
        range_max_atr_ratio: float = 2.0,         # Relaxed from 1.5 — allow wider ranges
        range_goldilocks_lo: float = 0.5,
        range_goldilocks_hi: float = 1.0,
        # ATR / RSI periods
        atr_period: int = 14,
        rsi_period: int = 14,
        # RSI thresholds — oversold on false SHORT breakout (triggers LONG fade)
        rsi_oversold_entry: float = 45.0,   # RSI must have reached this during breakdown (relaxed from 35)
        rsi_oversold_exit: float = 42.0,    # RSI must be above this now (recovering)
        # RSI thresholds — overbought on false LONG breakout (triggers SHORT fade)
        rsi_overbought_entry: float = 55.0,  # RSI must have reached this during spike (relaxed from 65)
        rsi_overbought_exit: float = 58.0,   # RSI must be below this now (fading)
        # ADX filter — fades only work in non-trending markets
        adx_period: int = 14,
        adx_max_trend: float = 30.0,         # Reject if ADX >= this (trending — don't fade)
        adx_ideal_max: float = 20.0,         # Conviction bonus if ADX < this (strongly choppy)
        # Standard exit multipliers (non-gold)
        sl_range_mult: float = 1.0,
        # Gold-specific exit multipliers
        gold_sl_range_mult: float = 1.5,
        # Conviction scoring thresholds
        volume_sma_period: int = 20,
        wick_rejection_threshold: float = 0.60,   # wick > 60% of bar height → rejection signal
        reentry_depth_threshold: float = 0.50,    # price > 50% back into range → strong fade
    ) -> None:
        self.asian_session_start_hour = asian_session_start_hour
        self.asian_session_end_hour = asian_session_end_hour
        self.entry_window_start_hour = entry_window_start_hour
        self.entry_window_end_hour = entry_window_end_hour
        self.time_stop_hour = time_stop_hour
        self.false_breakout_lookback = false_breakout_lookback
        self.range_min_atr_ratio = range_min_atr_ratio
        self.range_max_atr_ratio = range_max_atr_ratio
        self.range_goldilocks_lo = range_goldilocks_lo
        self.range_goldilocks_hi = range_goldilocks_hi
        self.atr_period = atr_period
        self.rsi_period = rsi_period
        self.rsi_oversold_entry = rsi_oversold_entry
        self.rsi_oversold_exit = rsi_oversold_exit
        self.rsi_overbought_entry = rsi_overbought_entry
        self.rsi_overbought_exit = rsi_overbought_exit
        self.adx_period = adx_period
        self.adx_max_trend = adx_max_trend
        self.adx_ideal_max = adx_ideal_max
        self.sl_range_mult = sl_range_mult
        self.gold_sl_range_mult = gold_sl_range_mult
        self.volume_sma_period = volume_sma_period
        self.wick_rejection_threshold = wick_rejection_threshold
        self.reentry_depth_threshold = reentry_depth_threshold

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full London Fade analysis on the OHLCV DataFrame.

        Returns a Signal when all false-breakout conditions are met, None otherwise.

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

        # ---- Time-window gate -----------------------------------------------
        current_bar = df.index[-1]
        current_hour = current_bar.hour

        if not (self.entry_window_start_hour <= current_hour < self.entry_window_end_hour):
            return None

        # ---- Day-of-week filter: no weekends --------------------------------
        if not self._is_valid_trading_day(current_bar):
            return None

        # ---- Compute indicators --------------------------------------------
        indicators = self._compute_indicators(df)
        if indicators is None:
            return None

        atr_now, rsi_series, adx_now, vol_sma_now = indicators

        if atr_now <= 0 or pd.isna(atr_now) or pd.isna(adx_now):
            return None

        # ---- ADX gate: only fade in non-trending markets -------------------
        if adx_now >= self.adx_max_trend:
            return None

        # ---- Asian session range -------------------------------------------
        asian_range = self._get_asian_range(df)
        if asian_range is None:
            return None

        asian_high, asian_low = asian_range
        range_width = asian_high - asian_low

        if range_width <= 0:
            return None

        # ---- Range validity filters ----------------------------------------
        if range_width < self.range_min_atr_ratio * atr_now:
            return None  # Too narrow — no meaningful range to fade back into
        if range_width > self.range_max_atr_ratio * atr_now:
            return None  # Too wide — the move may be a genuine institutional breakout

        # ---- Detect false breakout -----------------------------------------
        detection = self._detect_false_breakout(df, asian_high, asian_low, rsi_series)
        if detection is None:
            return None

        direction, breakout_meta = detection

        # ---- Build risk levels (absolute prices) ---------------------------
        close_now = df["close"].iloc[-1]
        sl_mult = self.gold_sl_range_mult if is_gold else self.sl_range_mult

        if direction == Direction.LONG:
            # Fading a false breakdown: entry is after price reclaims asian_low.
            # SL is below the false-break extreme (the lowest low during the breakdown).
            false_break_extreme = breakout_meta["false_break_extreme"]
            stop_loss = false_break_extreme - sl_mult * range_width
            take_profit = asian_high  # Full range reversion target
        else:
            # Fading a false breakout above: SL above the false-break extreme.
            false_break_extreme = breakout_meta["false_break_extreme"]
            stop_loss = false_break_extreme + sl_mult * range_width
            take_profit = asian_low  # Full range reversion target

        if stop_loss <= 0 or take_profit <= 0:
            return None

        # ---- Conviction scoring --------------------------------------------
        conviction = self._score_conviction(
            direction=direction,
            df=df,
            close_now=close_now,
            asian_high=asian_high,
            asian_low=asian_low,
            range_width=range_width,
            atr_now=atr_now,
            adx_now=adx_now,
            vol_sma_now=vol_sma_now,
            breakout_meta=breakout_meta,
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
                "adx": round(adx_now, 2),
                "is_gold": is_gold,
                "false_break_extreme": round(breakout_meta["false_break_extreme"], 5),
                "false_break_bar_idx": breakout_meta["false_break_bar_idx"],
                "rsi_at_extreme": round(breakout_meta["rsi_at_extreme"], 2),
                "rsi_now": round(rsi_series.iloc[-1], 2),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — returns True when analyze() would fire."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Structural and time-based exit logic for an open London Fade position.

        The engine handles hard SL/TP exits.  This method adds:
        1. Time stop: force-close at 14:00 UTC — no afternoon or overnight holds.
        2. Structural failure: price prints a new extreme beyond the false-breakout
           level, confirming the breakout was genuine — thesis is invalidated.

        Parameters
        ----------
        df       : current OHLCV DataFrame (same format as analyze).
        position : the currently open position for this symbol.
        """
        if not self._min_rows(df, self._MIN_BARS):
            return False

        current_hour = df.index[-1].hour
        close_now = df["close"].iloc[-1]

        # Time stop
        if current_hour >= self.time_stop_hour:
            return True

        # Structural exit — trade thesis failed: breakout was real
        asian_range = self._get_asian_range(df)
        if asian_range is not None:
            asian_high, asian_low = asian_range
            if position.side == Direction.LONG:
                # Entered fading a false breakdown; exit if price makes new low below asian_low
                new_extreme = df["low"].iloc[-1]
                original_extreme = position.metadata.get("false_break_extreme", asian_low)
                if new_extreme < original_extreme:
                    return True
            elif position.side == Direction.SHORT:
                # Entered fading a false breakout above; exit if price makes new high above asian_high
                new_extreme = df["high"].iloc[-1]
                original_extreme = position.metadata.get("false_break_extreme", asian_high)
                if new_extreme > original_extreme:
                    return True

        return False

    # ------------------------------------------------------------------
    # Indicator computation
    # ------------------------------------------------------------------

    def _compute_indicators(
        self,
        df: pd.DataFrame,
    ) -> tuple[float, pd.Series, float, float] | None:
        """
        Compute all needed indicators and return latest scalar values.

        Returns
        -------
        (atr_now, rsi_series, adx_now, vol_sma_now) or None on failure.

        Note: rsi_series is returned in full (not just the scalar) because
        _detect_false_breakout needs to inspect RSI values over the lookback window.
        """
        try:
            atr_now = float(atr(df, self.atr_period).iloc[-1])

            rsi_series = rsi(df["close"], self.rsi_period)

            adx_df = adx(df, self.adx_period)
            adx_now = float(adx_df["adx"].iloc[-1])

            vol_sma_now = float(sma(df["volume"], self.volume_sma_period).iloc[-1])

        except (IndexError, KeyError):
            return None

        return atr_now, rsi_series, adx_now, vol_sma_now

    # ------------------------------------------------------------------
    # Asian session range extraction
    # ------------------------------------------------------------------

    def _get_asian_range(
        self,
        df: pd.DataFrame,
    ) -> tuple[float, float] | None:
        """
        Extract the high and low of bars belonging to the Asian session
        (00:00–08:00 UTC by default) on the same calendar date as the current bar.

        Returns
        -------
        (asian_high, asian_low) or None if no Asian bars are found.
        """
        current_date = df.index[-1].date()

        asian_mask = (
            (df.index.date == current_date)
            & (df.index.hour >= self.asian_session_start_hour)
            & (df.index.hour < self.asian_session_end_hour)
        )
        asian_bars = df[asian_mask]

        if asian_bars.empty:
            return None

        return float(asian_bars["high"].max()), float(asian_bars["low"].min())

    # ------------------------------------------------------------------
    # False-breakout detection
    # ------------------------------------------------------------------

    def _detect_false_breakout(
        self,
        df: pd.DataFrame,
        asian_high: float,
        asian_low: float,
        rsi_series: pd.Series,
    ) -> tuple[Direction, dict] | None:
        """
        Scan the last `false_breakout_lookback` bars (plus current) for evidence of
        a failed breakout above asian_high or below asian_low.

        For a LONG fade signal (fading a false breakdown):
            - At least one of the lookback bars has low < asian_low.
            - Current close is back above asian_low (reclaimed).
            - Current bar is bullish (close > open).
            - RSI reached <= rsi_oversold_entry during the breakdown window.
            - RSI is now > rsi_oversold_exit (recovering momentum).

        For a SHORT fade signal (fading a false breakout):
            - At least one of the lookback bars has high > asian_high.
            - Current close is back below asian_high (reclaimed from above).
            - Current bar is bearish (close < open).
            - RSI reached >= rsi_overbought_entry during the breakout window.
            - RSI is now < rsi_overbought_exit (momentum fading).

        Parameters
        ----------
        df          : full OHLCV DataFrame.
        asian_high  : today's Asian session high.
        asian_low   : today's Asian session low.
        rsi_series  : full RSI series aligned to df.index.

        Returns
        -------
        (Direction, metadata_dict) or None if no false breakout detected.

        The metadata dict contains:
            false_break_extreme : the most extreme price reached during the false break
            false_break_bar_idx : the positional index (from end) of the bar that broke
            rsi_at_extreme      : RSI value on that bar
        """
        # Look back N bars (including current bar at index -1)
        lookback = self.false_breakout_lookback
        # Slice covering the lookback window: bars [-lookback-1 : ] gives us lookback+1
        # bars (the bars that could have made the false breakout) plus bar -1 (current).
        # We use at most `lookback` prior bars, so window is indices -(lookback+1) to -1.
        window_df = df.iloc[-(lookback + 1):]
        window_rsi = rsi_series.iloc[-(lookback + 1):]

        close_now = float(df["close"].iloc[-1])
        open_now = float(df["open"].iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])

        # ---- Check for false BREAKDOWN (triggers LONG fade) -----------------
        # Current bar must have reclaimed asian_low (close above it, bullish bar)
        if close_now > asian_low and close_now > open_now:
            # Search prior bars (exclude the current bar itself) for the breakdown
            prior_window = window_df.iloc[:-1]
            prior_rsi = window_rsi.iloc[:-1]

            breakdown_bars = prior_window[prior_window["low"] < asian_low]
            if not breakdown_bars.empty:
                # Find the bar with the most extreme (lowest) low — the deepest breakdown
                extreme_bar_pos = breakdown_bars["low"].idxmin()
                false_break_extreme = float(breakdown_bars["low"].min())

                # RSI on that bar — must have been oversold
                rsi_at_extreme = float(prior_rsi.loc[extreme_bar_pos]) if extreme_bar_pos in prior_rsi.index else float(prior_rsi.min())

                # RSI must have touched oversold AND now be recovering
                min_rsi_in_window = float(prior_rsi.min())
                if (
                    min_rsi_in_window <= self.rsi_oversold_entry
                    and rsi_now > self.rsi_oversold_exit
                ):
                    # Positional index from the end for metadata readability
                    try:
                        bar_pos_from_end = int(len(df) - 1 - df.index.get_loc(extreme_bar_pos))
                    except KeyError:
                        bar_pos_from_end = -1

                    return Direction.LONG, {
                        "false_break_extreme": false_break_extreme,
                        "false_break_bar_idx": bar_pos_from_end,
                        "rsi_at_extreme": rsi_at_extreme,
                    }

        # ---- Check for false BREAKOUT above (triggers SHORT fade) -----------
        # Current bar must have reclaimed below asian_high (close below it, bearish bar)
        if close_now < asian_high and close_now < open_now:
            prior_window = window_df.iloc[:-1]
            prior_rsi = window_rsi.iloc[:-1]

            breakout_bars = prior_window[prior_window["high"] > asian_high]
            if not breakout_bars.empty:
                # Find the bar with the most extreme (highest) high
                extreme_bar_pos = breakout_bars["high"].idxmax()
                false_break_extreme = float(breakout_bars["high"].max())

                rsi_at_extreme = float(prior_rsi.loc[extreme_bar_pos]) if extreme_bar_pos in prior_rsi.index else float(prior_rsi.max())

                max_rsi_in_window = float(prior_rsi.max())
                if (
                    max_rsi_in_window >= self.rsi_overbought_entry
                    and rsi_now < self.rsi_overbought_exit
                ):
                    try:
                        bar_pos_from_end = int(len(df) - 1 - df.index.get_loc(extreme_bar_pos))
                    except KeyError:
                        bar_pos_from_end = -1

                    return Direction.SHORT, {
                        "false_break_extreme": false_break_extreme,
                        "false_break_bar_idx": bar_pos_from_end,
                        "rsi_at_extreme": rsi_at_extreme,
                    }

        return None

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        df: pd.DataFrame,
        close_now: float,
        asian_high: float,
        asian_low: float,
        range_width: float,
        atr_now: float,
        adx_now: float,
        vol_sma_now: float,
        breakout_meta: dict,
    ) -> float:
        """
        Build conviction from a base score and five optional bonuses.

        Base:  0.50
        +0.10  Volume declining on the breakout bar vs the bar before it (exhaustion).
        +0.10  Wick > wick_rejection_threshold of the false-break bar's total height.
        +0.10  Price has returned > reentry_depth_threshold of the way back into range.
        +0.10  ADX < adx_ideal_max (strongly non-trending, best fading conditions).
        +0.10  Asian range in goldilocks zone (range_goldilocks_lo–range_goldilocks_hi × ATR).

        Result is SIGNED: positive for LONG, negative for SHORT.  Clamped to [-1, 1].
        """
        score = 0.50

        # Bonus 1: Volume declining on the false-break bar vs the bar prior to it.
        # A breakout on shrinking volume is an exhaustion signal — it lacks conviction.
        lookback = self.false_breakout_lookback
        window_df = df.iloc[-(lookback + 1):]
        prior_window = window_df.iloc[:-1]  # excludes current bar

        if len(prior_window) >= 2 and not pd.isna(vol_sma_now) and vol_sma_now > 0:
            # The false-break bar is the last bar in prior_window
            fb_vol = float(prior_window["volume"].iloc[-1])
            pre_fb_vol = float(prior_window["volume"].iloc[-2])
            if pre_fb_vol > 0 and fb_vol < pre_fb_vol:
                score += 0.10

        # Bonus 2: Wick > wick_rejection_threshold on the false-break bar.
        # A long wick on the bar that punched through the level signals strong rejection.
        if not prior_window.empty:
            fb_bar = prior_window.iloc[-1]
            bar_high = float(fb_bar["high"])
            bar_low = float(fb_bar["low"])
            bar_open = float(fb_bar["open"])
            bar_close_fb = float(fb_bar["close"])
            bar_height = bar_high - bar_low

            if bar_height > 0:
                if direction == Direction.LONG:
                    # Fading a false breakdown — we expect a long lower wick
                    lower_wick = min(bar_open, bar_close_fb) - bar_low
                    if lower_wick / bar_height > self.wick_rejection_threshold:
                        score += 0.10
                else:
                    # Fading a false breakout — we expect a long upper wick
                    upper_wick = bar_high - max(bar_open, bar_close_fb)
                    if upper_wick / bar_height > self.wick_rejection_threshold:
                        score += 0.10

        # Bonus 3: Price returned > reentry_depth_threshold into the Asian range.
        # A deep re-entry confirms that the false-break reversal has real momentum.
        if range_width > 0:
            if direction == Direction.LONG:
                # Price above asian_low; how far back toward asian_high has it come?
                reentry_depth = (close_now - asian_low) / range_width
            else:
                # Price below asian_high; how far back toward asian_low?
                reentry_depth = (asian_high - close_now) / range_width

            if reentry_depth > self.reentry_depth_threshold:
                score += 0.10

        # Bonus 4: ADX below ideal maximum — strongly non-trending, ideal for fading
        if not pd.isna(adx_now) and adx_now < self.adx_ideal_max:
            score += 0.10

        # Bonus 5: Range in the goldilocks zone (neither too tight nor already expanded)
        if atr_now > 0:
            range_atr_ratio = range_width / atr_now
            if self.range_goldilocks_lo <= range_atr_ratio <= self.range_goldilocks_hi:
                score += 0.10

        score = min(score, 1.0)
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_valid_trading_day(self, ts: pd.Timestamp) -> bool:
        """Return False on weekends (Saturday=5, Sunday=6)."""
        return ts.dayofweek < 5
