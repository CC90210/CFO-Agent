"""
strategies/technical/zscore_mean_reversion.py — Z-Score Mean Reversion Strategy

Logic
-----
A quantitative, hedge-fund-style approach that trades the statistical reversion of price
back toward its rolling mean.  The core signal is the Z-score: the number of standard
deviations price is away from its rolling mean.  When that distance exceeds ±2 standard
deviations and multiple confirming filters agree, the edge is to fade the move.

LONG signal conditions (all required):
    - Z-score(50) < -2.0  (price 2+ std devs below rolling mean)
    - RSI(14) < 30        (momentum confirms exhaustion)
    - Volume >= 1.5x 20-bar average (capitulation spike)
    - ADX < 25            (ranging market — mean reversion has edge)
    - Higher-TF Z-score (4x resampled) < -1.5 (multi-timeframe alignment)

SHORT signal conditions (mirror):
    - Z-score(50) > +2.0
    - RSI(14) > 70
    - Volume >= 1.5x average
    - ADX < 25
    - Higher-TF Z-score > +1.5

Exit triggers (first to fire wins):
    - Z-score crosses back through 0 (mean reversion complete — primary target)
    - RSI returns to 50 (momentum normalised)
    - Trailing stop: 1.5x ATR(14) beyond the highest/lowest close seen since entry

Stop loss  : 2.5x ATR(14) — wide enough to survive noise around the extreme
Take profit: Rolling mean (Z-score = 0) — the statistical mean we are reverting to

Conviction scoring
------------------
    +0.35  Z-score extremity  — how far beyond ±2 the current reading is
    +0.30  RSI extremity      — depth below 30 (long) or above 70 (short)
    +0.20  Volume spike       — magnitude of volume versus average
    +0.15  Higher-TF Z-score  — alignment on the 4x resampled timeframe

Best markets  : Crypto and equities during accumulation/distribution phases
Best timeframes: 15m, 1h
"""

from __future__ import annotations

import pandas as pd
import numpy as np

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import rsi, atr, adx


# ---------------------------------------------------------------------------
# Internal helpers (module-private)
# ---------------------------------------------------------------------------


def _rolling_zscore(series: pd.Series, period: int) -> pd.Series:
    """
    Compute rolling Z-score: (price - rolling_mean) / rolling_std.

    NaN is returned for the first `period - 1` rows where the window is
    not yet full.  A zero standard deviation window returns 0.0 to avoid
    division-by-zero.
    """
    rolling_mean = series.rolling(window=period).mean()
    rolling_std = series.rolling(window=period).std(ddof=0)
    # Replace zero std with NaN, then fill resulting NaN with 0.0
    safe_std = rolling_std.replace(0.0, np.nan)
    return ((series - rolling_mean) / safe_std).fillna(0.0)


def _higher_tf_zscore(close: pd.Series, primary_period: int, resample_factor: int) -> float:
    """
    Resample close to a coarser timeframe (last of every `resample_factor` bars)
    and return the most recent Z-score on that higher timeframe.

    Returns 0.0 when there is insufficient data to compute the Z-score.
    """
    # Take every Nth bar — equivalent to viewing the chart on a higher timeframe
    htf_close = close.iloc[::resample_factor]
    if len(htf_close) < primary_period:
        return 0.0
    htf_zscore = _rolling_zscore(htf_close, primary_period)
    last = htf_zscore.iloc[-1]
    return float(last) if pd.notna(last) else 0.0


# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class ZScoreMeanReversionStrategy(BaseStrategy):
    """
    Statistical Z-score mean reversion with multi-timeframe confirmation.

    Fades extreme deviations from the rolling mean when the market is
    ranging, momentum is exhausted, and volume confirms the move.
    """

    name = "zscore_mean_reversion"
    description = (
        "Z-score(50) beyond ±2 std devs combined with RSI extremes, volume spike, "
        "ADX < 25 regime filter, and higher-TF Z-score alignment. "
        "Target: full reversion to the rolling mean (Z-score = 0)."
    )
    timeframes = ["15m", "1h"]
    markets = ["crypto", "equities", "forex"]

    def __init__(
        self,
        zscore_period: int = 50,
        zscore_entry: float = 2.0,      # |z| must exceed this to qualify
        zscore_htf_entry: float = 1.5,  # |z| on higher TF must exceed this
        htf_resample_factor: int = 4,   # 4x bars → ~4h on 1h chart
        rsi_period: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        rsi_exit: float = 50.0,
        adx_period: int = 14,
        adx_max: float = 25.0,
        atr_period: int = 14,
        atr_stop_mult: float = 2.5,     # wide stop — survives noise at extremes
        atr_trail_mult: float = 1.5,    # tighter trailing stop once in profit
        volume_period: int = 20,
        volume_mult: float = 1.5,
    ) -> None:
        self.zscore_period = zscore_period
        self.zscore_entry = zscore_entry
        self.zscore_htf_entry = zscore_htf_entry
        self.htf_resample_factor = htf_resample_factor
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi_exit = rsi_exit
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.atr_trail_mult = atr_trail_mult
        self.volume_period = volume_period
        self.volume_mult = volume_mult

        # Minimum bars needed before any indicator is reliable
        self._min_bars = max(zscore_period, adx_period * 2, rsi_period, atr_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full Z-score mean reversion analysis and return a Signal or None.

        Parameters
        ----------
        df : OHLCV DataFrame, UTC-indexed, lowercase column names.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # --- Compute indicators ---
        zscore_series = _rolling_zscore(close, self.zscore_period)
        rsi_series = rsi(close, self.rsi_period)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)

        zscore_now = float(zscore_series.iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])
        adx_now = float(adx_df["adx"].iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        close_now = float(close.iloc[-1])
        rolling_mean = float(close.rolling(self.zscore_period).mean().iloc[-1])

        vol_now = float(df["volume"].iloc[-1])
        avg_vol = float(df["volume"].rolling(self.volume_period).mean().iloc[-1])
        vol_ratio = vol_now / avg_vol if avg_vol > 0 else 1.0

        # --- Gate 1: ADX regime filter — only trade ranging markets ---
        if pd.isna(adx_now) or adx_now >= self.adx_max:
            return None

        # --- Gate 2: Volume confirmation — require exhaustion spike ---
        if vol_ratio < self.volume_mult:
            return None

        # --- Gate 3: Z-score must breach the entry threshold ---
        if abs(zscore_now) < self.zscore_entry:
            return None

        # --- Gate 4: Determine direction from Z-score and RSI together ---
        direction: Direction | None = None

        if zscore_now < -self.zscore_entry and rsi_now < self.rsi_oversold:
            direction = Direction.LONG
        elif zscore_now > self.zscore_entry and rsi_now > self.rsi_overbought:
            direction = Direction.SHORT

        if direction is None:
            return None

        # --- Gate 5: Multi-timeframe Z-score confirmation ---
        htf_z = _higher_tf_zscore(close, self.zscore_period, self.htf_resample_factor)
        if direction == Direction.LONG and htf_z >= -self.zscore_htf_entry:
            return None
        if direction == Direction.SHORT and htf_z <= self.zscore_htf_entry:
            return None

        # --- Price levels ---
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = rolling_mean  # Z-score = 0 target
            # Sanity check: take profit must be above entry
            if take_profit <= entry_price:
                take_profit = entry_price + stop_dist  # fallback 1:1 R:R
        else:
            stop_loss = entry_price + stop_dist
            take_profit = rolling_mean
            # Sanity check: take profit must be below entry
            if take_profit >= entry_price:
                take_profit = entry_price - stop_dist

        conviction = self._score_conviction(
            zscore_now=zscore_now,
            rsi_now=rsi_now,
            vol_ratio=vol_ratio,
            htf_z=htf_z,
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
                "entry_price": entry_price,
                "zscore": round(zscore_now, 4),
                "zscore_htf": round(htf_z, 4),
                "rolling_mean": round(rolling_mean, 8),
                "rsi": round(rsi_now, 2),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 8),
                "volume_ratio": round(vol_ratio, 2),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — delegates to analyze()."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when any of three conditions are met:
          1. Z-score has crossed back through zero (reversion complete).
          2. RSI has returned to 50 (momentum normalised).
          3. Trailing stop at 1.5x ATR from the most favourable close.
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        zscore_series = _rolling_zscore(close, self.zscore_period)
        rsi_series = rsi(close, self.rsi_period)
        atr_series = atr(df, self.atr_period)

        zscore_now = float(zscore_series.iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])
        close_now = float(close.iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        trail_dist = self.atr_trail_mult * atr_now

        if position.side == Direction.LONG:
            # Condition 1: Z-score crossed zero (or above) — mean reversion complete
            zscore_exit = zscore_now >= 0.0
            # Condition 2: RSI mean-reversion complete
            rsi_exit = rsi_now >= self.rsi_exit
            # Condition 3: Trailing stop — track best close since entry
            best_close = position.metadata.get("trail_high", position.entry_price)
            best_close = max(best_close, close_now)
            # Write back the updated trail high so each bar advances it
            position.metadata["trail_high"] = best_close
            trail_stop = best_close - trail_dist
            trailing_exit = close_now <= trail_stop

            return zscore_exit or rsi_exit or trailing_exit

        else:  # SHORT
            zscore_exit = zscore_now <= 0.0
            rsi_exit = rsi_now <= self.rsi_exit
            # Trailing stop — track best (lowest) close since entry
            best_close = position.metadata.get("trail_low", position.entry_price)
            best_close = min(best_close, close_now)
            position.metadata["trail_low"] = best_close
            trail_stop = best_close + trail_dist
            trailing_exit = close_now >= trail_stop

            return zscore_exit or rsi_exit or trailing_exit

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        zscore_now: float,
        rsi_now: float,
        vol_ratio: float,
        htf_z: float,
        direction: Direction,
    ) -> float:
        """
        Weighted conviction score in [0, 1] (then signed and clamped to [-1, 1]).

        Component weights:
            0.35 — Z-score extremity
            0.30 — RSI extremity
            0.20 — Volume spike
            0.15 — Higher-TF Z-score alignment
        """
        score = 0.0

        # --- Z-score extremity (0.35 weight) ---
        # Normalise the excess beyond the entry threshold.
        # e.g. z = -3.0, entry = 2.0 → excess = 1.0, norm = 1.0 / 2.0 = 0.5
        z_excess = abs(zscore_now) - self.zscore_entry
        z_norm = min(z_excess / self.zscore_entry, 1.0)
        score += 0.35 * max(0.0, z_norm)

        # --- RSI extremity (0.30 weight) ---
        if direction == Direction.LONG:
            rsi_excess = self.rsi_oversold - rsi_now  # positive when below oversold
            rsi_norm = min(rsi_excess / self.rsi_oversold, 1.0)
        else:
            rsi_excess = rsi_now - self.rsi_overbought
            rsi_norm = min(rsi_excess / (100.0 - self.rsi_overbought), 1.0)
        score += 0.30 * max(0.0, rsi_norm)

        # --- Volume spike (0.20 weight) ---
        # vol_ratio = 1.5 → score = 0.0 (just at threshold)
        # vol_ratio = 3.0 → score = 1.0 (double threshold = max)
        vol_score = min((vol_ratio - self.volume_mult) / self.volume_mult, 1.0)
        score += 0.20 * max(0.0, vol_score)

        # --- Higher-TF Z-score alignment (0.15 weight) ---
        # How far beyond the htf threshold the higher-TF Z-score is
        htf_excess = abs(htf_z) - self.zscore_htf_entry
        htf_norm = min(htf_excess / self.zscore_htf_entry, 1.0)
        score += 0.15 * max(0.0, htf_norm)

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
