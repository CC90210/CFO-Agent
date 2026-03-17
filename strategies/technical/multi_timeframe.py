"""
strategies/technical/multi_timeframe.py — Multi-Timeframe Momentum Strategy

Logic
-----
The highest-conviction strategies align across multiple timeframes.  This is the
approach used by institutional prop traders who build "conviction stacks":

  Higher TF (4H / Daily)  — Determine macro trend direction via EMA 50/200 position.
  Medium TF  (1H)         — Find pullbacks to key EMA levels (21 EMA) within the trend.
  Lower TF   (15m)        — Precise entry timing via MACD crossover or RSI trigger.

Entry rules (LONG example):
    1. HTF: Close > EMA(50) AND EMA(50) > EMA(200) (uptrend confirmed)
    2. MTF: Price has pulled back to or below MTF EMA(21) but EMA(21) is rising
    3. LTF: MACD histogram crossed positive OR RSI crossed back above 40
    All three must be true — confluence_score >= 2/3 (minimum 2 timeframes aligned).

The caller must supply resampled DataFrames for each timeframe.  When only one
DataFrame is provided, the strategy degrades to single-timeframe mode using
internal resampling.

Conviction scoring
------------------
    +0.40  All three TFs aligned (score: 0 = 1/3, 0.40 = 2/3, 1.0 = 3/3)
    +0.30  HTF EMA separation (50/200 distance normalised to ATR)
    +0.30  LTF MACD histogram strength

Best markets  : BTC/USDT, ETH/USDT, SPY/QQQ, major FX pairs (EUR/USD, GBP/USD)
Best timeframes: 15m entry, 1H medium, 4H/Daily trend — provide all three DataFrames
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import ema, macd, rsi, atr, adx


class MultiTimeframeStrategy(BaseStrategy):
    """
    Multi-Timeframe Momentum — enters only when higher, medium, and lower
    timeframes align in the same direction.
    """

    name = "multi_timeframe"
    description = (
        "Three-timeframe confluence strategy: HTF trend direction (EMA 50/200), "
        "MTF pullback detection (EMA 21), LTF entry trigger (MACD/RSI). "
        "Minimum 2/3 TFs must agree."
    )
    timeframes = ["15m", "1h", "4h", "1d"]
    markets = ["crypto", "equities", "forex"]

    def __init__(
        self,
        htf_fast_ema: int = 50,
        htf_slow_ema: int = 200,
        mtf_ema: int = 21,
        ltf_macd_fast: int = 12,
        ltf_macd_slow: int = 26,
        ltf_macd_signal: int = 9,
        ltf_rsi_period: int = 14,
        ltf_rsi_entry_long: float = 40.0,
        ltf_rsi_entry_short: float = 60.0,
        atr_period: int = 14,
        atr_stop_mult: float = 2.5,
        rr_ratio: float = 3.0,
        min_confluence: int = 2,
        htf_resample_rule: str = "4h",
        mtf_resample_rule: str = "1h",
    ) -> None:
        self.htf_fast_ema = htf_fast_ema
        self.htf_slow_ema = htf_slow_ema
        self.mtf_ema = mtf_ema
        self.ltf_macd_fast = ltf_macd_fast
        self.ltf_macd_slow = ltf_macd_slow
        self.ltf_macd_signal = ltf_macd_signal
        self.ltf_rsi_period = ltf_rsi_period
        self.ltf_rsi_entry_long = ltf_rsi_entry_long
        self.ltf_rsi_entry_short = ltf_rsi_entry_short
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.min_confluence = min_confluence
        self.htf_resample_rule = htf_resample_rule
        self.mtf_resample_rule = mtf_resample_rule
        self._min_bars_ltf = max(htf_slow_ema, mtf_ema, ltf_macd_slow, atr_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(
        self,
        df: pd.DataFrame,
        df_mtf: pd.DataFrame | None = None,
        df_htf: pd.DataFrame | None = None,
    ) -> Signal | None:
        """
        Parameters
        ----------
        df     : LTF (lowest timeframe) OHLCV DataFrame — used for entry timing.
        df_mtf : Medium TF DataFrame (optional — resampled from df if not provided).
        df_htf : High TF DataFrame (optional — resampled from df if not provided).
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars_ltf):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")

        # Build HTF and MTF from LTF via resampling if not supplied
        df_htf = df_htf if df_htf is not None else self._resample(df, self.htf_resample_rule)
        df_mtf = df_mtf if df_mtf is not None else self._resample(df, self.mtf_resample_rule)

        # Score each timeframe
        htf_score = self._score_htf(df_htf)   # +1 LONG, -1 SHORT, 0 neutral
        mtf_score = self._score_mtf(df_mtf)
        ltf_score = self._score_ltf(df)

        confluence_long = sum(s > 0 for s in [htf_score, mtf_score, ltf_score])
        confluence_short = sum(s < 0 for s in [htf_score, mtf_score, ltf_score])

        if confluence_long >= self.min_confluence:
            direction = Direction.LONG
        elif confluence_short >= self.min_confluence:
            direction = Direction.SHORT
        else:
            return None  # Not enough confluence

        # LTF entry trigger must agree (it's the precision entry)
        if direction == Direction.LONG and ltf_score <= 0:
            return None
        if direction == Direction.SHORT and ltf_score >= 0:
            return None

        close = df["close"]
        atr_series = atr(df, self.atr_period)
        entry_price = close.iloc[-1]
        atr_now = atr_series.iloc[-1]
        stop_dist = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + stop_dist * self.rr_ratio
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - stop_dist * self.rr_ratio

        total_confluence = confluence_long if direction == Direction.LONG else confluence_short
        conviction = self._score_conviction(
            total_confluence, htf_score, ltf_score, df_htf, atr_now, direction
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
                "htf_score": htf_score,
                "mtf_score": mtf_score,
                "ltf_score": ltf_score,
                "confluence": total_confluence,
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit when HTF trend reverses against the position."""
        if not self._min_rows(df, self.htf_slow_ema + 5):
            return False

        df_htf = self._resample(df, self.htf_resample_rule)
        htf_score = self._score_htf(df_htf)

        if position.side == Direction.LONG and htf_score < 0:
            return True
        if position.side == Direction.SHORT and htf_score > 0:
            return True
        return False

    # ------------------------------------------------------------------
    # Timeframe-specific scoring helpers
    # ------------------------------------------------------------------

    def _score_htf(self, df_htf: pd.DataFrame) -> int:
        """
        +1 = uptrend (fast EMA > slow EMA)
        -1 = downtrend
         0 = neutral / insufficient data
        """
        if len(df_htf) < self.htf_slow_ema + 2:
            return 0
        close = df_htf["close"]
        fast = ema(close, self.htf_fast_ema).iloc[-1]
        slow = ema(close, self.htf_slow_ema).iloc[-1]
        if pd.isna(fast) or pd.isna(slow):
            return 0
        return 1 if fast > slow else -1

    def _score_mtf(self, df_mtf: pd.DataFrame) -> int:
        """
        +1 = price pulled back to rising MTF EMA (bullish continuation setup)
        -1 = price pulled back to falling MTF EMA (bearish)
         0 = neutral
        """
        if len(df_mtf) < self.mtf_ema + 3:
            return 0
        close = df_mtf["close"]
        mtf_ema_series = ema(close, self.mtf_ema)
        ema_now = mtf_ema_series.iloc[-1]
        ema_prev = mtf_ema_series.iloc[-3]  # 3-bar slope
        close_now = close.iloc[-1]
        if pd.isna(ema_now) or pd.isna(ema_prev):
            return 0
        ema_rising = ema_now > ema_prev
        ema_falling = ema_now < ema_prev
        near_ema = abs(close_now - ema_now) / ema_now <= 0.005  # within 0.5%
        if ema_rising and (close_now <= ema_now * 1.01):
            return 1  # price testing rising EMA from above = bullish pullback
        if ema_falling and (close_now >= ema_now * 0.99):
            return -1  # price testing falling EMA from below = bearish pullback
        return 0

    def _score_ltf(self, df_ltf: pd.DataFrame) -> int:
        """
        +1 = MACD histogram crossed positive OR RSI crossed above ltf_rsi_entry_long
        -1 = MACD histogram crossed negative OR RSI crossed below ltf_rsi_entry_short
         0 = no trigger
        """
        if len(df_ltf) < self.ltf_macd_slow + self.ltf_macd_signal + 3:
            return 0
        close = df_ltf["close"]
        macd_df = macd(close, self.ltf_macd_fast, self.ltf_macd_slow, self.ltf_macd_signal)
        rsi_series = rsi(close, self.ltf_rsi_period)

        hist_now = macd_df["histogram"].iloc[-1]
        hist_prev = macd_df["histogram"].iloc[-2]
        rsi_now = rsi_series.iloc[-1]
        rsi_prev = rsi_series.iloc[-2]

        macd_bullish = (hist_prev <= 0) and (hist_now > 0)
        macd_bearish = (hist_prev >= 0) and (hist_now < 0)
        rsi_bullish = (rsi_prev < self.ltf_rsi_entry_long) and (
            rsi_now >= self.ltf_rsi_entry_long
        )
        rsi_bearish = (rsi_prev > self.ltf_rsi_entry_short) and (
            rsi_now <= self.ltf_rsi_entry_short
        )

        if macd_bullish or rsi_bullish:
            return 1
        if macd_bearish or rsi_bearish:
            return -1
        return 0

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        confluence: int,
        htf_score: int,
        ltf_score: int,
        df_htf: pd.DataFrame,
        atr_val: float,
        direction: Direction,
    ) -> float:
        score = 0.0

        # Confluence weight
        confluence_norm = (confluence - 1) / (3 - 1)  # 1→0, 2→0.5, 3→1.0
        score += 0.40 * confluence_norm

        # HTF EMA separation
        if len(df_htf) >= self.htf_slow_ema + 2 and atr_val > 0:
            close_htf = df_htf["close"]
            fast_val = ema(close_htf, self.htf_fast_ema).iloc[-1]
            slow_val = ema(close_htf, self.htf_slow_ema).iloc[-1]
            if not (pd.isna(fast_val) or pd.isna(slow_val)):
                sep = abs(fast_val - slow_val) / (atr_val * 5)
                score += 0.30 * min(sep, 1.0)

        # LTF MACD histogram strength
        if len(df_htf) >= self.ltf_macd_slow + 5 and atr_val > 0:
            ltf_macd = macd(
                df_htf["close"], self.ltf_macd_fast,
                self.ltf_macd_slow, self.ltf_macd_signal,
            )
            hist_strength = min(abs(ltf_macd["histogram"].iloc[-1]) / atr_val, 1.0)
            score += 0.30 * hist_strength

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    # ------------------------------------------------------------------
    # Resampling helper
    # ------------------------------------------------------------------

    @staticmethod
    def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
        """Resample OHLCV DataFrame to a higher timeframe."""
        resampled = df.resample(rule).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        ).dropna()
        resampled.attrs = df.attrs
        return resampled
