"""
strategies/technical/forex_carry_momentum.py — Forex Carry + Momentum Hybrid Strategy

Background
----------
The carry trade is one of the oldest and most consistently profitable edges in foreign
exchange.  The idea is simple: borrow in a low-yielding currency (JPY, CHF) and invest
in a high-yielding one (AUD, NZD, CAD).  The net swap income compounds over time.

The classic weakness of pure carry is that it unwinds violently in risk-off episodes —
the "carry crash."  This strategy defends against that by adding a trend filter: we only
hold carry positions when the underlying price trend confirms the carry direction.  A
carry trade that is ALSO trending in our favour has two tailwinds simultaneously.

Why existing forex strategies fail on EUR/USD (-47%)
----------------------------------------------------
The forex strategies in this codebase are fundamentally crypto strategies applied to
forex pairs.  They rely on volume surges, session breakouts, and SMC concepts designed
for 24-hour crypto markets.  EUR/USD has:

  1. Much lower volatility (daily range 0.3-0.8% vs BTC's 2-5%)
  2. Persistent, multi-week trends driven by interest rate differentials
  3. Reliable session patterns but no meaningful "volume" data on retail feeds
  4. Carry as a structural return source (absent in crypto)

This strategy is built from the ground up for forex characteristics.

Strategy logic
--------------
Two edges stacked:
  1. CARRY DIRECTION — defined per-symbol based on typical interest rate hierarchy:
       - AUD_USD, NZD_USD: high-yield base currency → carry = LONG
       - USD_JPY, USD_CHF: low-yield quote currency → carry = LONG (USD higher than JPY/CHF)
       - EUR_USD, GBP_USD: differential varies; treated symmetrically (trend decides)
       - USD_CAD: symmetric; trend decides
       - EUR_GBP: symmetric; trend decides

  2. TREND FILTER (must align with carry direction or override it):
       - 200 SMA: macro trend
       - 50 SMA: medium-term trend confirmation
       - MACD histogram: momentum
       - RSI(14): entry timing (not overbought on longs, not oversold on shorts)
       - ADX(14): trend strength gate — avoids choppy, rangey periods that cause whipsaw

BUY signal (long high-yield pair):
    Price > SMA(200)  — macro uptrend
    Price > SMA(50)   — medium-term confirmation
    RSI > 40 and < 70 — confirmed strength, not overbought
    ADX > 20          — trending market, not chop
    MACD histogram > 0 — positive momentum

SELL signal:
    Mirror image of the above (all conditions reversed)

Stop loss  : 2.5x ATR(14) — wider than crypto strategies, forex mean-reverts less aggressively
Take profit: entry + risk * rr_ratio  (default 2.0:1)

Conviction scoring
------------------
    Base score:  0.40
    +0.15   Both SMA200 and SMA50 confirm (trend fully aligned across timeframes)
    +0.15   Price distance above/below SMA200 > 0.5% (sustained, not marginal, breakout)
    +0.15   ADX > 25 (strong trend, not just threshold pass)
    +0.15   MACD and RSI both confirm strongly (RSI > 50 for long, < 50 for short)

Best markets     : AUD_USD, NZD_USD, USD_JPY, USD_CAD — pairs with structural carry differentials
Best timeframes  : 4h (captures multi-day trends without microstructure noise)
"""

from __future__ import annotations

from typing import Final

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, macd, rsi, sma


# ---------------------------------------------------------------------------
# Carry direction hints — based on typical G10 rate hierarchy
# These are soft biases that are CONFIRMED by the trend filter before entry.
# Neutral pairs let the trend decide without a carry tilt.
# ---------------------------------------------------------------------------

# Maps OANDA-format symbol to preferred carry direction:
#   Direction.LONG  — structural carry favours owning the base currency
#   Direction.SHORT — structural carry favours selling the base currency
#   Direction.FLAT  — carry is symmetric; trend decides
_CARRY_BIAS: Final[dict[str, Direction]] = {
    # AUD and NZD are high-yield vs USD (historically)
    "AUD_USD": Direction.LONG,
    "NZD_USD": Direction.LONG,
    # USD yields more than JPY and CHF — long USD = earning carry
    "USD_JPY": Direction.LONG,
    "USD_CHF": Direction.LONG,
    # EUR/GBP/CAD differential varies — treat symmetrically
    "EUR_USD": Direction.FLAT,
    "GBP_USD": Direction.FLAT,
    "USD_CAD": Direction.FLAT,
    "EUR_GBP": Direction.FLAT,
    "EUR_JPY": Direction.LONG,   # EUR yields more than JPY
    "GBP_JPY": Direction.LONG,   # GBP yields more than JPY
}


class ForexCarryMomentumStrategy(BaseStrategy):
    """
    Forex Carry + Momentum Hybrid — earns swap carry AND rides the trend.

    Combines the structural carry trade edge (long high-yield, short low-yield
    currencies) with a multi-indicator trend filter to avoid carry crashes.
    Entry is only taken when price trend confirms the carry direction.

    Designed exclusively for OANDA forex pairs (not crypto).
    """

    name = "forex_carry_momentum"
    description = (
        "Carry trade direction (rate differential) filtered by 200/50 SMA trend, "
        "ADX trend strength, RSI entry timing, and MACD momentum confirmation. "
        "Wider ATR stops (2.5x) match forex's lower volatility profile. "
        "Designed for OANDA G10 pairs on the 4h timeframe."
    )
    timeframes = ["4h", "1d"]
    markets = ["forex"]

    def __init__(
        self,
        # Trend filter
        sma_slow: int = 200,
        sma_fast: int = 50,
        # RSI
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
        # ADX
        adx_period: int = 14,
        adx_min: float = 20.0,
        adx_strong: float = 25.0,   # threshold for strong-trend conviction bonus
        # MACD
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        # ATR / risk
        atr_period: int = 14,
        atr_stop_mult: float = 2.5,   # wider than crypto — forex is less volatile
        rr_ratio: float = 2.0,
        # Volume (forex spot volume is proxy-only, so threshold is relaxed)
        volume_period: int = 20,
        volume_mult: float = 1.0,     # 1.0 = no volume gate by default
        # Minimum pip distance from SMA200 to score sustained-breakout conviction bonus
        # Expressed as a fraction of price (0.005 = 0.5%)
        sma_distance_pct: float = 0.005,
    ) -> None:
        self.sma_slow = sma_slow
        self.sma_fast = sma_fast
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.adx_period = adx_period
        self.adx_min = adx_min
        self.adx_strong = adx_strong
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.sma_distance_pct = sma_distance_pct

        # Minimum bars: SMA200 needs 200 bars + a buffer for all other indicators.
        # ADX requires 2 * adx_period rows internally.
        self._min_bars = max(sma_slow, 2 * adx_period, macd_slow + macd_signal) + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol: str = df.attrs.get("symbol", "UNKNOWN")

        # Compute indicators — all vectorized, no mutation of df
        sma_slow_series = sma(df["close"], self.sma_slow)
        sma_fast_series = sma(df["close"], self.sma_fast)
        rsi_series = rsi(df["close"], self.rsi_period)
        adx_df = adx(df, self.adx_period)
        macd_df = macd(
            df["close"],
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal,
        )
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # Current bar values
        close_now: float = df["close"].iloc[-1]
        sma_slow_now: float = sma_slow_series.iloc[-1]
        sma_fast_now: float = sma_fast_series.iloc[-1]
        rsi_now: float = rsi_series.iloc[-1]
        adx_now: float = adx_df["adx"].iloc[-1]
        hist_now: float = macd_df["histogram"].iloc[-1]
        atr_now: float = atr_series.iloc[-1]
        vol_now: float = df["volume"].iloc[-1]
        avg_vol_now: float = avg_vol.iloc[-1]

        # Guard: reject bars where any indicator has not yet warmed up
        for val in (sma_slow_now, sma_fast_now, rsi_now, hist_now, atr_now):
            if pd.isna(val):
                return None
        if atr_now <= 0:
            return None

        # Determine direction from trend signals
        direction = self._determine_direction(
            close_now, sma_slow_now, sma_fast_now,
            rsi_now, adx_now, hist_now, avg_vol_now, vol_now,
        )
        if direction == Direction.FLAT:
            return None

        # Apply carry bias overlay: if there is a hard carry bias for this symbol
        # and the trend contradicts it, skip the trade.  If carry and trend agree,
        # conviction is boosted in _score_conviction.
        carry_bias = _CARRY_BIAS.get(symbol, Direction.FLAT)
        if carry_bias != Direction.FLAT and carry_bias != direction:
            # Trend opposes carry — potential carry unwind scenario, skip.
            return None

        # Build entry levels
        entry_price = close_now
        risk = atr_now * self.atr_stop_mult

        if direction == Direction.LONG:
            stop_loss = entry_price - risk
            take_profit = entry_price + risk * self.rr_ratio
        else:
            stop_loss = entry_price + risk
            take_profit = entry_price - risk * self.rr_ratio

        # Safety: all levels must be positive prices (always true for forex, but guard anyway)
        if stop_loss <= 0 or take_profit <= 0:
            return None

        # Score conviction
        adx_val = adx_now if not pd.isna(adx_now) else 0.0
        carry_aligned = carry_bias == direction  # both carry and trend agree
        conviction = self._score_conviction(
            direction=direction,
            close_now=close_now,
            sma_slow_now=sma_slow_now,
            sma_fast_now=sma_fast_now,
            rsi_now=rsi_now,
            adx_val=adx_val,
            hist_now=hist_now,
            carry_aligned=carry_aligned,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 6),
            take_profit=round(take_profit, 6),
            strategy_name=self.name,
            metadata={
                "entry_price": round(entry_price, 6),
                "sma_200": round(sma_slow_now, 6),
                "sma_50": round(sma_fast_now, 6),
                "rsi": round(rsi_now, 4),
                "adx": round(adx_val, 4),
                "macd_histogram": round(hist_now, 8),
                "atr": round(atr_now, 6),
                "carry_bias": carry_bias.value,
                "carry_aligned": carry_aligned,
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when the trend reverses against the position.

        Triggers (any one fires):
          1. Price crosses below SMA50 for a LONG (medium-term trend failure).
          2. Price crosses above SMA50 for a SHORT.
          3. MACD histogram flips against position direction (momentum reversal).
          4. RSI reaches overbought on LONG (> 75) or oversold on SHORT (< 25)
             — carry unwind / exhaustion signal.
        """
        if not self._min_rows(df, self.sma_fast + 5):
            return False

        close_now: float = df["close"].iloc[-1]

        sma_fast_series = sma(df["close"], self.sma_fast)
        sma_fast_now: float = sma_fast_series.iloc[-1]

        macd_df = macd(
            df["close"],
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal,
        )
        hist_now: float = macd_df["histogram"].iloc[-1]
        rsi_series = rsi(df["close"], self.rsi_period)
        rsi_now: float = rsi_series.iloc[-1]

        if pd.isna(sma_fast_now) or pd.isna(hist_now) or pd.isna(rsi_now):
            return False

        if position.side == Direction.LONG:
            # SMA50 breach — trend is failing
            if close_now < sma_fast_now:
                return True
            # Momentum flipped negative
            if hist_now < 0:
                return True
            # RSI hit extreme overbought (>75) — exhaustion, take profit manually
            if rsi_now > 75:
                return True

        elif position.side == Direction.SHORT:
            # SMA50 breach upwards — trend is failing
            if close_now > sma_fast_now:
                return True
            # Momentum flipped positive
            if hist_now > 0:
                return True
            # RSI hit extreme oversold (<25) — exhaustion
            if rsi_now < 25:
                return True

        return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _determine_direction(
        self,
        close_now: float,
        sma_slow_now: float,
        sma_fast_now: float,
        rsi_now: float,
        adx_now: float,
        hist_now: float,
        avg_vol_now: float,
        vol_now: float,
    ) -> Direction:
        """
        Apply the five entry conditions and return LONG, SHORT, or FLAT.

        All five must pass for LONG or SHORT.  If no direction qualifies, FLAT.
        """
        # Gate 1: ADX must confirm a trend is present
        if pd.isna(adx_now) or adx_now < self.adx_min:
            return Direction.FLAT

        # Gate 2: Volume — if volume_mult > 1.0, enforce a volume threshold.
        # With the default of 1.0 this gate is always open, which is correct
        # for forex where retail feed volume is a noisy proxy.
        if self.volume_mult > 1.0 and avg_vol_now > 0:
            if vol_now < self.volume_mult * avg_vol_now:
                return Direction.FLAT

        # LONG conditions
        long_ok = (
            close_now > sma_slow_now                              # macro uptrend
            and close_now > sma_fast_now                          # medium uptrend
            and self.rsi_oversold < rsi_now < self.rsi_overbought # not at extremes
            and rsi_now > 40.0                                     # confirmed strength
            and hist_now > 0                                       # positive momentum
        )

        # SHORT conditions
        short_ok = (
            close_now < sma_slow_now                              # macro downtrend
            and close_now < sma_fast_now                          # medium downtrend
            and self.rsi_oversold < rsi_now < self.rsi_overbought # not at extremes
            and rsi_now < 60.0                                     # confirmed weakness
            and hist_now < 0                                       # negative momentum
        )

        if long_ok:
            return Direction.LONG
        if short_ok:
            return Direction.SHORT
        return Direction.FLAT

    def _score_conviction(
        self,
        direction: Direction,
        close_now: float,
        sma_slow_now: float,
        sma_fast_now: float,
        rsi_now: float,
        adx_val: float,
        hist_now: float,
        carry_aligned: bool,
    ) -> float:
        """
        Build a conviction score in [-1.0, 1.0].

        Scoring breakdown (all additive):
            0.40  base — strategy has structural edge when all 5 conditions align
            0.15  both SMAs confirm direction (200 and 50 agree — no conflicting signals)
            0.15  price is > sma_distance_pct away from SMA200 (sustained trend, not marginal)
            0.15  ADX > adx_strong (strong trend — reduces false starts)
            0.15  RSI confirms strongly (LONG: RSI > 50; SHORT: RSI < 50)
            ---- (note: carry alignment is already enforced as a gate — no extra bonus needed)
        """
        score = 0.40

        # Both SMAs aligned
        both_smas_aligned = (
            (direction == Direction.LONG and close_now > sma_slow_now and close_now > sma_fast_now)
            or (direction == Direction.SHORT and close_now < sma_slow_now and close_now < sma_fast_now)
        )
        if both_smas_aligned:
            score += 0.15

        # Sustained breakout above/below SMA200
        if sma_slow_now > 0:
            distance_pct = abs(close_now - sma_slow_now) / sma_slow_now
            if distance_pct >= self.sma_distance_pct:
                score += 0.15

        # Strong trend (ADX above strong threshold)
        if adx_val >= self.adx_strong:
            score += 0.15

        # RSI in the momentum sweet spot
        if direction == Direction.LONG and rsi_now > 50.0:
            score += 0.15
        elif direction == Direction.SHORT and rsi_now < 50.0:
            score += 0.15

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
