"""
strategies/technical/gold_trend_follower.py — Gold Keltner Channel Trend Follower

Thesis
------
Gold (XAU/USD) and silver (XAG/USD) are among the most reliable trending instruments
in the world.  Unlike equities, they do not revert to earnings — they trend on
macro regime shifts (real-rate changes, USD cycles, geopolitical stress) that can
persist for months.  This strategy exploits that by requiring a full structural
alignment before entering: triple EMA stack, ADX trend-strength filter, MACD
momentum confirmation, and a Keltner Channel breakout that signals volatility
expansion beyond the "noise band".

Entry rules (LONG):
    1. Close > upper Keltner Channel  (EMA(20) + multiplier × ATR(14)) — breakout
    2. EMA(20) > EMA(50) > EMA(200)   — triple EMA stack confirms macro uptrend
    3. ADX(14) > adx_threshold        — trend is strong (default 25)
    4. MACD histogram > 0             — short-term momentum confirms direction
    5. close[-1] > close[-4]          — price higher than 3 bars ago (recent thrust)

Entry rules (SHORT): mirror image of the above.

Exit:
    - Stop loss  : 2.5 × ATR below/above entry  (gold whipsaws tight stops)
    - Take profit: 5.0 × ATR (2:1 R:R baseline; gold trends far when it moves)
    - Trailing   : after 1.5 × ATR profit, trail at 2.0 × ATR from the best price

Conviction scoring (base 0.50):
    +0.15  Triple EMA stack clean — no crossovers in the last 10 bars
    +0.15  ADX > adx_strong_threshold (default 35) — very strong trend
    +0.10  Decisive breakout — close > upper band + 0.5 × ATR (for LONG)
    +0.10  Volume expanding — volume > vol_expansion_factor × SMA(20) of volume

Best markets    : XAU/USD (gold), XAG/USD (silver) via OANDA
Best timeframes : 1h (intraday swing), 4h (positional), 1d (macro)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import (
    adx,
    atr,
    ema,
    keltner_channels,
    macd,
    sma,
)


class GoldTrendFollowerStrategy(BaseStrategy):
    """
    Keltner Channel trend-following strategy tuned for gold and silver.

    All parameters are configurable through __init__ kwargs so the Darwinian
    agent can evolve them without touching strategy logic.
    """

    name = "gold_trend_follower"
    description = (
        "Keltner Channel breakout combined with triple EMA stack, ADX trend-strength, "
        "and MACD momentum confirmation.  Designed for XAU/USD and XAG/USD via OANDA. "
        "Wide ATR-based stops account for gold's inherent volatility."
    )
    timeframes = ["1h", "4h", "1d"]
    markets = ["commodities"]

    # Minimum bars needed to compute all indicators (EMA 200 is the longest)
    _MIN_BARS: int = 210

    def __init__(
        self,
        # Keltner Channel parameters
        keltner_ema_period: int = 20,
        keltner_atr_period: int = 14,
        keltner_multiplier: float = 2.0,
        # Triple EMA stack periods
        ema_fast: int = 20,
        ema_mid: int = 50,
        ema_slow: int = 200,
        # ADX parameters
        adx_period: int = 14,
        adx_threshold: float = 25.0,
        adx_strong_threshold: float = 35.0,
        # MACD parameters
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        # Momentum lookback (bars)
        momentum_lookback: int = 3,
        # ATR-based risk parameters
        atr_period: int = 14,
        atr_stop_mult: float = 2.5,
        atr_tp_mult: float = 5.0,
        atr_trail_trigger_mult: float = 1.5,
        atr_trail_dist_mult: float = 2.0,
        # Conviction bonuses
        ema_clean_lookback: int = 10,
        decisive_breakout_extra_atr: float = 0.5,
        vol_expansion_factor: float = 1.3,
        vol_sma_period: int = 20,
    ) -> None:
        self.keltner_ema_period = keltner_ema_period
        self.keltner_atr_period = keltner_atr_period
        self.keltner_multiplier = keltner_multiplier
        self.ema_fast = ema_fast
        self.ema_mid = ema_mid
        self.ema_slow = ema_slow
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.adx_strong_threshold = adx_strong_threshold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.momentum_lookback = momentum_lookback
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.atr_tp_mult = atr_tp_mult
        self.atr_trail_trigger_mult = atr_trail_trigger_mult
        self.atr_trail_dist_mult = atr_trail_dist_mult
        self.ema_clean_lookback = ema_clean_lookback
        self.decisive_breakout_extra_atr = decisive_breakout_extra_atr
        self.vol_expansion_factor = vol_expansion_factor
        self.vol_sma_period = vol_sma_period

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run all five entry filters and return a Signal when all conditions are met,
        or None when there is no tradeable edge.

        Parameters
        ----------
        df : OHLCV DataFrame, UTC-indexed.  Must contain: open, high, low, close, volume.
             Minimum length: 210 bars (driven by EMA 200 lookback).
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._MIN_BARS):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")

        indicators = self._compute_indicators(df)
        if indicators is None:
            return None

        (
            close_now,
            atr_now,
            kc_upper,
            kc_lower,
            ema20_now,
            ema50_now,
            ema200_now,
            adx_now,
            hist_now,
            vol_now,
            vol_sma_now,
        ) = indicators

        # Guard: any NaN in the critical values means indicators haven't warmed up
        critical = [
            close_now, atr_now, kc_upper, kc_lower,
            ema20_now, ema50_now, ema200_now, adx_now, hist_now,
        ]
        if any(pd.isna(v) for v in critical):
            return None

        # ---- Momentum filter: recent price thrust ----------------------------
        if len(df) < self.momentum_lookback + 2:
            return None
        close_n_bars_ago = df["close"].iloc[-(self.momentum_lookback + 1)]
        price_rising = close_now > close_n_bars_ago
        price_falling = close_now < close_n_bars_ago

        # ---- Evaluate LONG conditions ----------------------------------------
        long_conditions = (
            close_now > kc_upper                       # (1) Keltner breakout
            and ema20_now > ema50_now > ema200_now     # (2) Triple EMA stack
            and adx_now > self.adx_threshold           # (3) Trending market
            and hist_now > 0                           # (4) MACD histogram positive
            and price_rising                           # (5) Recent thrust upward
        )

        # ---- Evaluate SHORT conditions ---------------------------------------
        short_conditions = (
            close_now < kc_lower                       # (1) Keltner breakdown
            and ema20_now < ema50_now < ema200_now     # (2) Triple EMA stack (inverted)
            and adx_now > self.adx_threshold           # (3) Trending market
            and hist_now < 0                           # (4) MACD histogram negative
            and price_falling                          # (5) Recent thrust downward
        )

        if long_conditions:
            direction = Direction.LONG
        elif short_conditions:
            direction = Direction.SHORT
        else:
            return None

        # ---- Risk levels (absolute prices) -----------------------------------
        stop_dist = self.atr_stop_mult * atr_now
        tp_dist = self.atr_tp_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = close_now - stop_dist
            take_profit = close_now + tp_dist
        else:
            stop_loss = close_now + stop_dist
            take_profit = close_now - tp_dist

        # Prices must remain positive (prevents negative gold price nonsense)
        if stop_loss <= 0 or take_profit <= 0:
            return None

        # ---- Conviction score ------------------------------------------------
        conviction = self._score_conviction(
            direction=direction,
            df=df,
            close_now=close_now,
            atr_now=atr_now,
            kc_upper=kc_upper,
            kc_lower=kc_lower,
            adx_now=adx_now,
            vol_now=vol_now,
            vol_sma_now=vol_sma_now,
        )

        # Trailing stop metadata for the engine / trade protocol
        trail_trigger = self.atr_trail_trigger_mult * atr_now
        trail_distance = self.atr_trail_dist_mult * atr_now

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            strategy_name=self.name,
            metadata={
                "entry_price": close_now,
                "atr": round(atr_now, 5),
                "adx": round(adx_now, 2),
                "macd_histogram": round(hist_now, 5),
                "ema_20": round(ema20_now, 5),
                "ema_50": round(ema50_now, 5),
                "ema_200": round(ema200_now, 5),
                "kc_upper": round(kc_upper, 5),
                "kc_lower": round(kc_lower, 5),
                "trail_trigger_dist": round(trail_trigger, 5),
                "trail_distance": round(trail_distance, 5),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """
        Lightweight entry check called by the scanner loop.
        Returns True when analyze() would produce a non-FLAT signal.
        """
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Signal-based exit: close the position when the structural trend has reversed.

        The engine handles ATR stop-loss and take-profit levels; this method handles
        signal reversal — specifically when the triple EMA stack flips against us or
        the Keltner Channel closes back inside (failed breakout).

        Parameters
        ----------
        df       : current OHLCV DataFrame
        position : the currently open position
        """
        if not self._min_rows(df, self._MIN_BARS):
            return False

        indicators = self._compute_indicators(df)
        if indicators is None:
            return False

        (
            close_now,
            _atr_now,
            kc_upper,
            kc_lower,
            ema20_now,
            ema50_now,
            ema200_now,
            _adx_now,
            hist_now,
            _vol_now,
            _vol_sma_now,
        ) = indicators

        if any(
            pd.isna(v)
            for v in [close_now, kc_upper, kc_lower, ema20_now, ema50_now, ema200_now]
        ):
            return False

        if position.side == Direction.LONG:
            # Exit long when ANY of:
            #   (a) price retreats back inside the Keltner Channel (breakout failed)
            #   (b) EMA stack has broken down (20 crosses below 50)
            #   (c) MACD histogram flips bearish
            breakout_failed = close_now < kc_upper
            ema_stack_broken = ema20_now < ema50_now
            macd_flipped_bearish = hist_now < 0
            return breakout_failed or ema_stack_broken or macd_flipped_bearish

        if position.side == Direction.SHORT:
            # Exit short when ANY of:
            #   (a) price reclaims back inside the Keltner Channel
            #   (b) EMA stack has recovered (20 crosses above 50)
            #   (c) MACD histogram flips bullish
            breakout_failed = close_now > kc_lower
            ema_stack_broken = ema20_now > ema50_now
            macd_flipped_bullish = hist_now > 0
            return breakout_failed or ema_stack_broken or macd_flipped_bullish

        return False

    # ------------------------------------------------------------------
    # Indicator computation
    # ------------------------------------------------------------------

    def _compute_indicators(
        self, df: pd.DataFrame
    ) -> tuple[
        float, float, float, float,
        float, float, float,
        float, float, float, float,
    ] | None:
        """
        Compute all indicators in one place and return the latest scalar values.

        Returns None if any computation fails (e.g., insufficient warmup).
        The returned tuple is:
            close_now, atr_now, kc_upper, kc_lower,
            ema20_now, ema50_now, ema200_now,
            adx_now, macd_hist_now,
            vol_now, vol_sma_now
        """
        try:
            close = df["close"]

            # ATR (for stop sizing)
            atr_series = atr(df, self.atr_period)
            atr_now = atr_series.iloc[-1]

            # Keltner Channels
            kc = keltner_channels(
                df,
                ema_period=self.keltner_ema_period,
                atr_period=self.keltner_atr_period,
                multiplier=self.keltner_multiplier,
            )
            kc_upper = kc.upper.iloc[-1]
            kc_lower = kc.lower.iloc[-1]

            # Triple EMA stack
            ema20_series = ema(close, self.ema_fast)
            ema50_series = ema(close, self.ema_mid)
            ema200_series = ema(close, self.ema_slow)
            ema20_now = ema20_series.iloc[-1]
            ema50_now = ema50_series.iloc[-1]
            ema200_now = ema200_series.iloc[-1]

            # ADX trend strength
            adx_df = adx(df, self.adx_period)
            adx_now = adx_df["adx"].iloc[-1]

            # MACD histogram
            macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)
            hist_now = macd_df["histogram"].iloc[-1]

            # Volume vs its own SMA (for conviction bonus)
            vol_now = df["volume"].iloc[-1]
            vol_sma_now = sma(df["volume"], self.vol_sma_period).iloc[-1]

            close_now = close.iloc[-1]

        except (IndexError, KeyError):
            return None

        return (
            close_now, atr_now, kc_upper, kc_lower,
            ema20_now, ema50_now, ema200_now,
            adx_now, hist_now,
            vol_now, vol_sma_now,
        )

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        df: pd.DataFrame,
        close_now: float,
        atr_now: float,
        kc_upper: float,
        kc_lower: float,
        adx_now: float,
        vol_now: float,
        vol_sma_now: float,
    ) -> float:
        """
        Build conviction from the base score plus four optional bonuses.

        Base: 0.50
        +0.15  Triple EMA stack is clean (no crossovers in last ema_clean_lookback bars)
        +0.15  ADX > adx_strong_threshold (very strong trend)
        +0.10  Decisive breakout: close > upper KC + 0.5 × ATR (LONG) or mirror (SHORT)
        +0.10  Volume expanding: volume > vol_expansion_factor × vol SMA(20)

        Result is signed (+ve for LONG, -ve for SHORT) and clamped to [-1, 1].
        """
        score = 0.50

        # Bonus 1: Clean EMA stack (no crossovers in last N bars)
        score += self._bonus_clean_ema_stack(df, direction)

        # Bonus 2: Very strong trend (ADX > strong threshold)
        if adx_now > self.adx_strong_threshold:
            score += 0.15

        # Bonus 3: Decisive Keltner breakout
        if atr_now > 0:
            if direction == Direction.LONG:
                decisive_level = kc_upper + self.decisive_breakout_extra_atr * atr_now
                if close_now > decisive_level:
                    score += 0.10
            else:
                decisive_level = kc_lower - self.decisive_breakout_extra_atr * atr_now
                if close_now < decisive_level:
                    score += 0.10

        # Bonus 4: Volume expansion
        if not pd.isna(vol_sma_now) and vol_sma_now > 0:
            if vol_now > self.vol_expansion_factor * vol_sma_now:
                score += 0.10

        # Cap at 1.0 before signing
        score = min(score, 1.0)

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    def _bonus_clean_ema_stack(
        self, df: pd.DataFrame, direction: Direction
    ) -> float:
        """
        Return +0.15 when the triple EMA stack shows no crossovers in the last
        ema_clean_lookback bars (stack has been consistently aligned).

        A crossover is detected by checking whether the ordering of EMA(20),
        EMA(50) flipped sign over the lookback window.
        """
        lookback = self.ema_clean_lookback + 1  # +1 to compare previous bar
        if len(df) < self.ema_slow + lookback:
            return 0.0

        close = df["close"]
        ema20 = ema(close, self.ema_fast).iloc[-lookback:]
        ema50 = ema(close, self.ema_mid).iloc[-lookback:]

        if ema20.isna().any() or ema50.isna().any():
            return 0.0

        diff = ema20 - ema50  # positive = 20 above 50

        if direction == Direction.LONG:
            # All values must be positive — 20 consistently above 50
            consistently_aligned = (diff > 0).all()
        else:
            # All values must be negative — 20 consistently below 50
            consistently_aligned = (diff < 0).all()

        return 0.15 if consistently_aligned else 0.0
