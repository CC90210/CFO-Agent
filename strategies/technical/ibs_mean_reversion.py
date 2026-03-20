"""
strategies/technical/ibs_mean_reversion.py — IBS + RSI Mean Reversion Strategy

Designed for liquid US equities and ETFs (SPY, QQQ, AAPL, MSFT, etc.) via Alpaca.

Strategy overview
-----------------
Internal Bar Strength (IBS) measures where price closed within its daily range:

    IBS = (close - low) / (high - low)

IBS near 0  → closed near the day's low  → short-term oversold exhaustion
IBS near 1  → closed near the day's high → short-term overbought exhaustion

Historical research (Cesar Alvarez, Connors) shows IBS < 0.2 combined with
RSI(21) < 40 has a ~78% win rate on SPY on daily bars.  The short holding
period (1–3 days) keeps exposure low and captures the snap-back.

LONG signal — all conditions required:
    1. IBS < 0.2          — closed near the low (intraday exhaustion)
    2. RSI(21) < 40       — intermediate momentum oversold (21-period is smoother than 14)
    3. Close > SMA(200)   — macro uptrend filter; only fade dips in bull regimes

SHORT signal — mirror image:
    1. IBS > 0.8          — closed near the high (intraday exhaustion to the upside)
    2. RSI(21) > 60       — intermediate momentum overbought
    3. Close < SMA(200)   — macro downtrend filter

Exit rules:
    - Primary: close > yesterday's close (for longs) or close < yesterday's close (for shorts)
      This captures the snap-back on the very next bar — keeping holding periods tight.
    - Stop loss:   1.5x ATR(14) below entry
    - Take profit: 2.0x stop distance (2:1 R:R floor)

Conviction scoring (additive, base 0.45, max ±1.0):
    Base:   0.45  — minimum when all three conditions are met
    +0.15   IBS < 0.1 (extreme — closed right at the session low, maximum intraday exhaustion)
    +0.15   RSI(21) < 30 (deeply oversold — well past the entry threshold)
    +0.10   Volume > 1.3x 20-bar average (capitulation volume confirms the exhaustion)
    +0.10   Close > SMA(50) (intermediate uptrend intact — higher-probability mean reversion)
    +0.05   Three or more consecutive down days (multi-day selloff amplifies snap-back edge)

Best markets    : SPY, QQQ, large-cap liquid US equities
Best timeframes : 1d (strategy designed for daily bars)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import rsi, sma, atr


class IBSMeanReversionStrategy(BaseStrategy):
    """
    IBS + RSI mean reversion for liquid US equities and ETFs.

    Buys intraday exhaustion dips (IBS < 0.2, RSI < 40) above the 200 SMA,
    and shorts intraday exhaustion rallies (IBS > 0.8, RSI > 60) below the
    200 SMA.  Exit rule is price-action based: close above yesterday's close
    for longs (snap-back confirmed), close below yesterday's close for shorts.
    """

    name = "ibs_mean_reversion"
    description = (
        "IBS < 0.2 / > 0.8 combined with RSI(21) extremes and 200 SMA trend filter. "
        "Exit when price snaps back past yesterday's close. "
        "Designed for liquid US equities and ETFs on daily bars via Alpaca."
    )
    timeframes = ["1d"]
    markets = ["equities"]

    def __init__(
        self,
        ibs_entry_long: float = 0.2,       # IBS must be below this for a long signal
        ibs_entry_short: float = 0.8,      # IBS must be above this for a short signal
        ibs_extreme: float = 0.1,          # extreme IBS threshold for +0.15 conviction bonus
        rsi_period: int = 21,              # longer period than typical — smoother signal
        rsi_entry_long: float = 40.0,      # RSI must be below this for a long
        rsi_entry_short: float = 60.0,     # RSI must be above this for a short
        rsi_deep_oversold: float = 30.0,   # threshold for +0.15 deep-oversold conviction bonus
        rsi_deep_overbought: float = 70.0, # threshold for +0.15 deep-overbought conviction bonus
        sma_trend_period: int = 200,       # 200 SMA macro trend filter
        sma_mid_period: int = 50,          # 50 SMA intermediate trend filter (conviction bonus)
        consecutive_down_days: int = 3,    # min streak of declining closes for +0.05 bonus
        volume_period: int = 20,           # lookback for average volume calculation
        volume_mult: float = 1.3,          # volume must exceed this multiple for +0.10 bonus
        atr_period: int = 14,              # ATR lookback for stop/TP sizing
        atr_stop_mult: float = 1.5,        # stop loss = entry ± atr_stop_mult * ATR
        rr_ratio: float = 2.0,             # take profit = entry ± rr_ratio * stop_dist
    ) -> None:
        self.ibs_entry_long = ibs_entry_long
        self.ibs_entry_short = ibs_entry_short
        self.ibs_extreme = ibs_extreme
        self.rsi_period = rsi_period
        self.rsi_entry_long = rsi_entry_long
        self.rsi_entry_short = rsi_entry_short
        self.rsi_deep_oversold = rsi_deep_oversold
        self.rsi_deep_overbought = rsi_deep_overbought
        self.sma_trend_period = sma_trend_period
        self.sma_mid_period = sma_mid_period
        self.consecutive_down_days = consecutive_down_days
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio

        # 200 SMA is the binding constraint — add a 10-bar buffer for convergence.
        self._min_bars = sma_trend_period + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full IBS + RSI analysis on OHLCV data and return a Signal, or
        None when entry conditions are not met.

        Requires at minimum sma_trend_period + 10 rows (210 by default).
        Returns None — never raises — when data is insufficient or any
        indicator returns NaN.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        high = df["high"]
        low = df["low"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # --- Compute indicators ---
        rsi_series = rsi(close, self.rsi_period)
        sma_200 = sma(close, self.sma_trend_period)
        sma_50 = sma(close, self.sma_mid_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # --- Current-bar scalars ---
        close_now = float(close.iloc[-1])
        high_now = float(high.iloc[-1])
        low_now = float(low.iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])
        sma_200_now = float(sma_200.iloc[-1])
        sma_50_now = float(sma_50.iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        vol_now = float(df["volume"].iloc[-1])
        avg_vol_now = float(avg_vol.iloc[-1])

        # --- Guard against NaN / degenerate data ---
        if any(
            pd.isna(v)
            for v in (rsi_now, sma_200_now, sma_50_now, atr_now, avg_vol_now)
        ):
            return None

        if atr_now <= 0 or avg_vol_now <= 0:
            return None

        # --- IBS: (close - low) / (high - low) ---
        # IBS is undefined when high == low (doji / no range) — skip the bar.
        bar_range = high_now - low_now
        if bar_range <= 0:
            return None
        ibs_now = (close_now - low_now) / bar_range

        vol_ratio = vol_now / avg_vol_now

        # --- Determine direction ---
        direction: Direction | None = None

        if ibs_now < self.ibs_entry_long and rsi_now < self.rsi_entry_long:
            # LONG: only fade dips while price is above the 200 SMA (bull regime)
            if close_now <= sma_200_now:
                return None
            direction = Direction.LONG

        elif ibs_now > self.ibs_entry_short and rsi_now > self.rsi_entry_short:
            # SHORT: only fade rallies while price is below the 200 SMA (bear regime)
            if close_now >= sma_200_now:
                return None
            direction = Direction.SHORT

        if direction is None:
            return None

        # --- Stop loss and take profit (absolute price levels) ---
        stop_dist = self.atr_stop_mult * atr_now
        tp_dist = self.rr_ratio * stop_dist  # enforces rr_ratio:1 R:R

        entry_price = close_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + tp_dist
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - tp_dist

        # Hard safety: all price levels must be positive and directionally valid
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        # --- Consecutive down days (for conviction bonus) ---
        # Count how many bars ending on close[-2] were consecutively lower closes.
        # Using [-2] because the signal bar itself ([-1]) is already an "oversold" bar.
        down_streak = self._count_down_streak(close)

        # --- Conviction scoring ---
        conviction = self._score_conviction(
            ibs_now=ibs_now,
            rsi_now=rsi_now,
            vol_ratio=vol_ratio,
            close_now=close_now,
            sma_50_now=sma_50_now,
            down_streak=down_streak,
            direction=direction,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 4),
            take_profit=round(take_profit, 4),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "ibs": round(ibs_now, 4),
                "rsi": round(rsi_now, 2),
                "sma_200": round(sma_200_now, 4),
                "sma_50": round(sma_50_now, 4),
                "atr": round(atr_now, 4),
                "volume_ratio": round(vol_ratio, 2),
                "down_streak": down_streak,
                "stop_dist": round(stop_dist, 4),
                "tp_dist": round(tp_dist, 4),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — delegates to analyze()."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when the snap-back is confirmed:
          - LONG : today's close > yesterday's close (price recovered)
          - SHORT: today's close < yesterday's close (price rolled over)

        This keeps the average holding period to 1–3 days, which is the
        primary edge of the IBS strategy.
        """
        # Need at least 2 bars to compare today vs. yesterday
        if not self._min_rows(df, 2):
            return False

        close_now = float(df["close"].iloc[-1])
        close_prev = float(df["close"].iloc[-2])

        if pd.isna(close_now) or pd.isna(close_prev):
            return False

        if position.side == Direction.LONG:
            # Snap-back confirmed: today's close is above yesterday's close
            return close_now > close_prev
        else:
            # Short snap-back confirmed: today's close is below yesterday's close
            return close_now < close_prev

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _count_down_streak(self, close: pd.Series) -> int:
        """
        Count the number of consecutive bars (ending before the signal bar)
        on which close was lower than the prior close.

        Uses close.iloc[-2] as the most recent reference point — the signal
        bar (iloc[-1]) is the oversold bar itself, not counted in the streak.

        Returns 0 when there are fewer than 2 prior bars to compare.
        """
        if len(close) < 3:
            return 0

        streak = 0
        # Walk backwards from iloc[-2] (one bar before the signal bar)
        for i in range(len(close) - 2, 0, -1):
            if close.iloc[i] < close.iloc[i - 1]:
                streak += 1
            else:
                break
        return streak

    def _score_conviction(
        self,
        ibs_now: float,
        rsi_now: float,
        vol_ratio: float,
        close_now: float,
        sma_50_now: float,
        down_streak: int,
        direction: Direction,
    ) -> float:
        """
        Build conviction score starting from a base of 0.45.

        Bonuses (additive, each independent):
            +0.15  IBS < ibs_extreme (extreme — closed at/near session low or high)
            +0.15  RSI < rsi_deep_oversold (deeply oversold, well past the entry threshold)
            +0.10  Volume > volume_mult * average (capitulation volume)
            +0.10  Intermediate trend intact (price > SMA(50) for longs, < SMA(50) for shorts)
            +0.05  Consecutive down days >= consecutive_down_days threshold

        Score is clamped to [-1.0, 1.0] and signed: positive for LONG, negative for SHORT.
        """
        score = 0.45  # base conviction for a clean IBS + RSI + SMA200 signal

        # Bonus 1: Extreme IBS reading (closed right at the session extreme)
        if direction == Direction.LONG and ibs_now < self.ibs_extreme:
            score += 0.15
        elif direction == Direction.SHORT and ibs_now > (1.0 - self.ibs_extreme):
            score += 0.15

        # Bonus 2: Deep RSI extreme (well below/above the entry threshold)
        if direction == Direction.LONG and rsi_now < self.rsi_deep_oversold:
            score += 0.15
        elif direction == Direction.SHORT and rsi_now > self.rsi_deep_overbought:
            score += 0.15

        # Bonus 3: Capitulation / exhaustion volume
        if vol_ratio >= self.volume_mult:
            score += 0.10

        # Bonus 4: Intermediate trend alignment (SMA 50)
        if direction == Direction.LONG and close_now > sma_50_now:
            score += 0.10
        elif direction == Direction.SHORT and close_now < sma_50_now:
            score += 0.10

        # Bonus 5: Multi-day selloff (amplifies mean-reversion edge)
        if down_streak >= self.consecutive_down_days:
            score += 0.05

        # Sign: positive for LONG, negative for SHORT; clamp to [-1.0, 1.0]
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
