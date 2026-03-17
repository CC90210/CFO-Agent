"""
strategies/technical/volume_profile.py — Volume Profile / Value Area Strategy

Institutional-grade strategy that exploits the fact that markets spend most of their
time near "fair value" (the Value Area) and revert when price becomes "unfair" (outside
the VA).  High-Volume Nodes act as strong S/R; Low-Volume Nodes are thin air that price
rips through.

Key concepts
------------
POC  (Point of Control)  — The price bin with the highest volume.  Acts as a magnet.
VA   (Value Area)        — The band of bins containing 70% of total volume.
VAH  (Value Area High)   — Upper boundary of the VA.  Strong resistance inside VA.
VAL  (Value Area Low)    — Lower boundary of the VA.  Strong support inside VA.
HVN  (High Volume Node)  — Bin with volume significantly above the per-bin average.
LVN  (Low Volume Node)   — Bin with volume significantly below the per-bin average;
                           price accelerates through LVNs.

Entry logic
-----------
MEAN REVERSION — LONG:
    - Price closes below VAL (price is "cheap" / unfair)
    - Volume on the drop is >= volume_mult × average (institutional absorption)
    - RSI < rsi_oversold (35 by default)
    - Current bar is bullish (close > open) — rejection candle at VAL

MEAN REVERSION — SHORT:
    - Price closes above VAH (price is "expensive" / unfair)
    - Volume >= volume_mult × average
    - RSI > rsi_overbought (65 by default)
    - Current bar is bearish (close < open)

BREAKOUT — LONG:
    - Price closes above VAH with volume >= breakout_vol_mult × average
    - POC has been rising over the last poc_trend_bars bars (value migrating up)

BREAKOUT — SHORT:
    - Price closes below VAL with volume >= breakout_vol_mult × average
    - POC has been falling over the last poc_trend_bars bars

Exits
-----
Mean reversion trades: exit when price reaches POC or crosses the midpoint of the VA.
Breakout trades: exit at target = VAH + 1.5 × VA_width (long) or VAL - 1.5 × VA_width.

Stop loss
---------
Wider of: low of the setup bar (long) / high of the setup bar (short), or 1.5 × ATR.

Conviction scoring
------------------
+0.35  Distance from POC (further → more extreme → higher conviction)
+0.30  Volume confirmation strength
+0.20  RSI extremity (how far past the threshold)
+0.15  Number of previous bounces at VAH/VAL level in the profile window

Best timeframes: 15m, 1h, 4h
Best markets   : crypto, equities, futures
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, rsi, volume_profile


# ---------------------------------------------------------------------------
# Internal result container for computed profile levels
# ---------------------------------------------------------------------------


class _ProfileLevels:
    """Holds the derived scalar levels from one volume profile computation."""

    __slots__ = (
        "poc",
        "vah",
        "val",
        "va_width",
        "hvn_levels",
        "lvn_levels",
    )

    def __init__(
        self,
        poc: float,
        vah: float,
        val: float,
        va_width: float,
        hvn_levels: list[float],
        lvn_levels: list[float],
    ) -> None:
        self.poc = poc
        self.vah = vah
        self.val = val
        self.va_width = va_width
        self.hvn_levels = hvn_levels
        self.lvn_levels = lvn_levels


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


class VolumeProfileStrategy(BaseStrategy):
    """
    Volume Profile / Value Area mean-reversion and breakout strategy.

    Uses a rolling window of OHLCV bars to build a live volume profile, then
    trades price dislocations from the Value Area with volume confirmation.
    """

    name = "volume_profile"
    description = (
        "Institutional volume-profile strategy: fades moves outside the 70% Value Area "
        "(mean reversion to POC) and plays breakouts confirmed by 2× volume with a "
        "rising/falling POC trend.  Stop = wider of setup-bar extreme or 1.5× ATR."
    )
    timeframes = ["15m", "1h", "4h"]
    markets = ["crypto", "equities", "futures"]

    def __init__(
        self,
        profile_window: int = 100,
        profile_bins: int = 50,
        rsi_period: int = 14,
        rsi_oversold: float = 35.0,
        rsi_overbought: float = 65.0,
        rsi_exit: float = 50.0,
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,
        volume_period: int = 20,
        volume_mult: float = 1.5,
        breakout_vol_mult: float = 2.0,
        hvn_threshold: float = 1.5,   # bins with volume > hvn_threshold × mean are HVNs
        lvn_threshold: float = 0.5,   # bins with volume < lvn_threshold × mean are LVNs
        poc_trend_bars: int = 10,
        bounce_lookback: int = 30,
        bounce_tolerance: float = 0.003,  # 0.3 % of price counts as "touching" a level
    ) -> None:
        self.profile_window = profile_window
        self.profile_bins = profile_bins
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi_exit = rsi_exit
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.breakout_vol_mult = breakout_vol_mult
        self.hvn_threshold = hvn_threshold
        self.lvn_threshold = lvn_threshold
        self.poc_trend_bars = poc_trend_bars
        self.bounce_lookback = bounce_lookback
        self.bounce_tolerance = bounce_tolerance

        self._min_bars = max(
            profile_window,
            rsi_period + 5,
            atr_period + 5,
            volume_period + 5,
        )

        # Rolling cache: keyed by last bar timestamp to avoid recomputing on
        # every should_enter / should_exit call within the same bar.
        self._cache_key: object = None
        self._cache_levels: _ProfileLevels | None = None

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        close = df["close"]

        # --- Indicators ---
        rsi_series = rsi(close, self.rsi_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        rsi_now = rsi_series.iloc[-1]
        atr_now = atr_series.iloc[-1]
        close_now = close.iloc[-1]
        open_now = df["open"].iloc[-1]
        low_now = df["low"].iloc[-1]
        high_now = df["high"].iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # --- Volume Profile for the rolling window ---
        levels = self._compute_levels(df)
        if levels is None:
            return None

        poc = levels.poc
        vah = levels.vah
        val = levels.val
        va_width = levels.va_width

        # --- POC trend (rising / falling) over poc_trend_bars ---
        poc_rising, poc_falling = self._poc_trend(df)

        # --- Bounce count at VAH/VAL ---
        bounces = self._count_bounces(df, levels)

        # ---------------------------------------------------------------
        # Determine setup mode and direction
        # ---------------------------------------------------------------
        direction: Direction | None = None
        is_breakout = False

        is_bullish_candle = close_now > open_now
        is_bearish_candle = close_now < open_now

        # Mean reversion — LONG: price has dropped below VAL
        if (
            close_now < val
            and vol_ratio >= self.volume_mult
            and rsi_now < self.rsi_oversold
            and is_bullish_candle
        ):
            direction = Direction.LONG
            is_breakout = False

        # Mean reversion — SHORT: price has risen above VAH
        elif (
            close_now > vah
            and vol_ratio >= self.volume_mult
            and rsi_now > self.rsi_overbought
            and is_bearish_candle
        ):
            direction = Direction.SHORT
            is_breakout = False

        # Breakout — LONG: close above VAH with heavy volume + rising POC
        elif (
            close_now > vah
            and vol_ratio >= self.breakout_vol_mult
            and poc_rising
        ):
            direction = Direction.LONG
            is_breakout = True

        # Breakout — SHORT: close below VAL with heavy volume + falling POC
        elif (
            close_now < val
            and vol_ratio >= self.breakout_vol_mult
            and poc_falling
        ):
            direction = Direction.SHORT
            is_breakout = True

        if direction is None:
            return None

        # ---------------------------------------------------------------
        # Stop loss and take profit
        # ---------------------------------------------------------------
        atr_stop = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            bar_stop = low_now - atr_now * 0.1   # fractionally below bar low
            stop_loss = min(close_now - atr_stop, bar_stop)
            stop_loss = max(stop_loss, 1e-8)  # never zero or negative

            if is_breakout:
                take_profit = vah + 1.5 * va_width
            else:
                # Mean reversion: target POC
                take_profit = poc
                if take_profit <= close_now:
                    # Degenerate edge: POC already below entry (shouldn't normally happen)
                    take_profit = close_now + (close_now - stop_loss)

        else:  # SHORT
            bar_stop = high_now + atr_now * 0.1
            stop_loss = max(close_now + atr_stop, bar_stop)

            if is_breakout:
                take_profit = val - 1.5 * va_width
                take_profit = max(take_profit, 1e-8)
            else:
                take_profit = poc
                if take_profit >= close_now:
                    take_profit = close_now - (stop_loss - close_now)
                    take_profit = max(take_profit, 1e-8)

        # Final sanity guard: ensure TP is on the correct side of entry
        if direction == Direction.LONG and take_profit <= close_now:
            take_profit = close_now + abs(close_now - stop_loss)
        if direction == Direction.SHORT and take_profit >= close_now:
            take_profit = close_now - abs(stop_loss - close_now)
            take_profit = max(take_profit, 1e-8)

        # ---------------------------------------------------------------
        # Conviction scoring
        # ---------------------------------------------------------------
        conviction = self._score_conviction(
            direction=direction,
            close_now=close_now,
            poc=poc,
            vah=vah,
            val=val,
            va_width=va_width,
            vol_ratio=vol_ratio,
            rsi_now=rsi_now,
            bounces=bounces,
            is_breakout=is_breakout,
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
                "poc": round(poc, 8),
                "vah": round(vah, 8),
                "val": round(val, 8),
                "va_width": round(va_width, 8),
                "rsi": round(rsi_now, 2),
                "atr": round(atr_now, 8),
                "volume_ratio": round(vol_ratio, 2),
                "bounces": bounces,
                "is_breakout": is_breakout,
                "poc_rising": poc_rising,
                "poc_falling": poc_falling,
                "hvn_levels": [round(p, 8) for p in levels.hvn_levels],
                "lvn_levels": [round(p, 8) for p in levels.lvn_levels],
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit conditions:
          Mean reversion: price reaches POC, or RSI crosses back to 50.
          Breakout: RSI reaches overbought/oversold, or price stalls at opposite VA boundary.
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        rsi_series = rsi(close, self.rsi_period)
        rsi_now = rsi_series.iloc[-1]
        close_now = close.iloc[-1]

        levels = self._compute_levels(df)
        if levels is None:
            return False

        poc = levels.poc
        is_breakout = position.metadata.get("is_breakout", False)

        if position.side == Direction.LONG:
            if is_breakout:
                # Exit if RSI becomes extremely overbought or price pulls back below VAH
                return rsi_now > 80.0 or close_now < levels.vah
            else:
                # Mean reversion: exit when price reaches POC or RSI recovers to mid
                return close_now >= poc or rsi_now >= self.rsi_exit

        else:  # SHORT
            if is_breakout:
                return rsi_now < 20.0 or close_now > levels.val
            else:
                return close_now <= poc or rsi_now <= self.rsi_exit

    # ------------------------------------------------------------------
    # Volume profile computation
    # ------------------------------------------------------------------

    def _compute_levels(self, df: pd.DataFrame) -> _ProfileLevels | None:
        """
        Build the volume profile over the last profile_window bars and derive
        POC, VAH, VAL, HVN list, and LVN list.

        Results are cached by the last bar's index label so the profile is not
        recomputed multiple times within the same bar.
        """
        last_key = df.index[-1]
        if last_key == self._cache_key and self._cache_levels is not None:
            return self._cache_levels

        window_df = df.iloc[-self.profile_window :]
        if len(window_df) < 2:
            return None

        profile = volume_profile(window_df, bins=self.profile_bins)

        # POC: midpoint of the highest-volume bin
        poc_row = profile.loc[profile["poc"]]
        if poc_row.empty:
            return None
        poc_price = float(
            (poc_row["price_low"].iloc[0] + poc_row["price_high"].iloc[0]) / 2.0
        )

        # VAH / VAL from value_area bins
        va_bins = profile.loc[profile["value_area"]]
        if va_bins.empty:
            return None
        vah = float(va_bins["price_high"].max())
        val = float(va_bins["price_low"].min())
        va_width = vah - val
        if va_width <= 0:
            return None

        # HVN / LVN classification
        mean_bin_vol = float(profile["volume"].mean())
        hvn_levels: list[float] = []
        lvn_levels: list[float] = []
        for _, row in profile.iterrows():
            mid = (row["price_low"] + row["price_high"]) / 2.0
            if mean_bin_vol > 0:
                ratio = row["volume"] / mean_bin_vol
                if ratio >= self.hvn_threshold:
                    hvn_levels.append(float(mid))
                elif ratio <= self.lvn_threshold:
                    lvn_levels.append(float(mid))

        levels = _ProfileLevels(
            poc=poc_price,
            vah=vah,
            val=val,
            va_width=va_width,
            hvn_levels=hvn_levels,
            lvn_levels=lvn_levels,
        )
        self._cache_key = last_key
        self._cache_levels = levels
        return levels

    # ------------------------------------------------------------------
    # POC trend detection
    # ------------------------------------------------------------------

    def _poc_trend(self, df: pd.DataFrame) -> tuple[bool, bool]:
        """
        Compare the POC of the most recent profile_window bars against the POC
        computed poc_trend_bars periods earlier.  Returns (rising, falling).
        """
        lookback = self.profile_window + self.poc_trend_bars
        if len(df) < lookback:
            return False, False

        # Current POC
        current_levels = self._compute_levels(df)
        if current_levels is None:
            return False, False

        # Earlier POC — build a temporary profile on the earlier window slice
        older_df = df.iloc[-(lookback) : -(self.poc_trend_bars)]
        if len(older_df) < 2:
            return False, False

        older_profile = volume_profile(older_df, bins=self.profile_bins)
        older_poc_row = older_profile.loc[older_profile["poc"]]
        if older_poc_row.empty:
            return False, False

        older_poc = float(
            (older_poc_row["price_low"].iloc[0] + older_poc_row["price_high"].iloc[0]) / 2.0
        )

        current_poc = current_levels.poc
        rising = current_poc > older_poc * 1.001   # >0.1% move to avoid noise
        falling = current_poc < older_poc * 0.999
        return rising, falling

    # ------------------------------------------------------------------
    # Bounce counting
    # ------------------------------------------------------------------

    def _count_bounces(self, df: pd.DataFrame, levels: _ProfileLevels) -> int:
        """
        Count the number of times price has touched VAH or VAL and reversed
        within the bounce_lookback bars preceding the current bar.

        A "touch" is defined as: the bar's low (for VAL touches) or high
        (for VAH touches) came within bounce_tolerance × price of the level,
        and the close reversed away from it (close > val for VAL touches,
        close < vah for VAH touches).
        """
        window = df.iloc[-(self.bounce_lookback + 1) : -1]
        if window.empty:
            return 0

        vah = levels.vah
        val = levels.val
        bounces = 0

        for _, row in window.iterrows():
            tol_val = val * self.bounce_tolerance
            tol_vah = vah * self.bounce_tolerance
            # VAL bounce: low near VAL and close above VAL
            if abs(row["low"] - val) <= tol_val and row["close"] > val:
                bounces += 1
            # VAH bounce: high near VAH and close below VAH
            if abs(row["high"] - vah) <= tol_vah and row["close"] < vah:
                bounces += 1

        return bounces

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        close_now: float,
        poc: float,
        vah: float,
        val: float,
        va_width: float,
        vol_ratio: float,
        rsi_now: float,
        bounces: int,
        is_breakout: bool,
    ) -> float:
        score = 0.0

        # --- Component 1 (weight 0.35): Distance from POC ---
        # Further from POC = more extreme dislocation = higher conviction.
        # Normalize against VA width so the score is asset-agnostic.
        if va_width > 0:
            poc_distance = abs(close_now - poc) / va_width
            # Cap at 2× VA widths (very extreme moves)
            poc_norm = min(poc_distance / 2.0, 1.0)
        else:
            poc_norm = 0.0
        score += 0.35 * poc_norm

        # --- Component 2 (weight 0.30): Volume confirmation strength ---
        if is_breakout:
            ref_mult = self.breakout_vol_mult
        else:
            ref_mult = self.volume_mult
        # Excess above the required threshold, capped at 2× the threshold
        vol_excess = (vol_ratio - ref_mult) / ref_mult
        vol_norm = min(max(vol_excess, 0.0), 1.0)
        score += 0.30 * vol_norm

        # --- Component 3 (weight 0.20): RSI extremity ---
        if direction == Direction.LONG:
            rsi_excess = self.rsi_oversold - rsi_now
            rsi_norm = min(max(rsi_excess / self.rsi_oversold, 0.0), 1.0)
        else:
            rsi_excess = rsi_now - self.rsi_overbought
            rsi_norm = min(max(rsi_excess / (100.0 - self.rsi_overbought), 0.0), 1.0)
        score += 0.20 * rsi_norm

        # --- Component 4 (weight 0.15): Historical bounces at the level ---
        # Normalize: 3+ bounces = max score (levels are well-tested S/R).
        bounce_norm = min(bounces / 3.0, 1.0)
        score += 0.15 * bounce_norm

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
