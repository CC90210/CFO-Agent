"""
strategies/technical/bollinger_squeeze.py — Bollinger Band Squeeze Breakout Strategy

Logic
-----
Volatility contracts (squeeze) and then expands violently — this strategy profits
from catching the expansion.

Squeeze detection:
    - BB width is at or near its lowest point in the past N bars (default 126 ~ 6 months)
    - Keltner Channels are *wider* than Bollinger Bands at the same moment
      (BB inside KC = classic John Carter squeeze confirmation)

Breakout signal:
    - Close breaks *outside* the Bollinger Bands after a confirmed squeeze
    - Volume on the breakout bar >= 2x the 20-period average
    - Direction: close > BB upper → LONG, close < BB lower → SHORT

Stop loss:
    - LONG: below the opposite (lower) Bollinger Band
    - SHORT: above the opposite (upper) Bollinger Band

Take profit:
    - Initially 2x the ATR from entry (can be upgraded to trailing stop once in profit)

Trailing stop:
    When unrealised PnL >= 1x ATR, activate a trailing stop at 1.5x ATR behind the
    highest close (LONG) or lowest close (SHORT).

Conviction scoring
------------------
    +0.35  BB width compression ratio (tighter squeeze → higher score)
    +0.35  Volume surge magnitude (capped at 3x average for max score)
    +0.30  Keltner Channel confirmation (are BB bands fully inside KC?)

Best markets  : BTC/USDT, ETH/USDT, Gold (XAU/USD), high-beta stocks
Best timeframes: 4H, Daily — the squeeze can take weeks to resolve
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import bollinger_bands, atr, keltner_channels


class BollingerSqueezeStrategy(BaseStrategy):
    """Bollinger Band Squeeze Breakout — trades the volatility expansion after compression."""

    name = "bollinger_squeeze"
    description = (
        "Detects volatility squeezes (BB inside Keltner Channels) and enters on the "
        "subsequent breakout outside the BB with a volume surge confirmation."
    )
    timeframes = ["4h", "1d"]
    markets = ["crypto", "equities", "commodities"]

    def __init__(
        self,
        bb_period: int = 20,
        bb_std: float = 2.0,
        kc_ema_period: int = 20,
        kc_atr_period: int = 10,
        kc_mult: float = 2.0,
        squeeze_lookback: int = 126,
        breakout_vol_mult: float = 2.0,
        atr_period: int = 14,
        atr_tp_mult: float = 2.0,
        volume_period: int = 20,
    ) -> None:
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.kc_ema_period = kc_ema_period
        self.kc_atr_period = kc_atr_period
        self.kc_mult = kc_mult
        self.squeeze_lookback = squeeze_lookback
        self.breakout_vol_mult = breakout_vol_mult
        self.atr_period = atr_period
        self.atr_tp_mult = atr_tp_mult
        self.volume_period = volume_period
        self._min_bars = max(bb_period, squeeze_lookback, atr_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        kc = keltner_channels(df, self.kc_ema_period, self.kc_atr_period, self.kc_mult)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        bb_width = bb.width
        bb_upper_now = bb.upper.iloc[-1]
        bb_lower_now = bb.lower.iloc[-1]
        kc_upper_now = kc.upper.iloc[-1]
        kc_lower_now = kc.lower.iloc[-1]
        close_now = close.iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # Step 1: Was there a squeeze recently?
        squeeze_window = bb_width.iloc[-self.squeeze_lookback :]
        if squeeze_window.isna().all():
            return None

        min_width = squeeze_window.min()
        current_width = bb_width.iloc[-1]

        # Squeeze is considered "just released" when bandwidth was at minimum within
        # the last 3 bars but has now widened (expansion has begun).
        recent_min = bb_width.iloc[-4:-1].min()  # previous 3 bars
        squeeze_was_active = recent_min <= min_width * 1.05  # was at historical min
        width_expanding = current_width > recent_min  # now widening

        if not (squeeze_was_active and width_expanding):
            return None

        # Step 2: Keltner Channel squeeze confirmation (BB inside KC)
        kc_squeeze = (bb_upper_now <= kc_upper_now) and (bb_lower_now >= kc_lower_now)

        # Step 3: Breakout direction
        if close_now > bb_upper_now:
            direction = Direction.LONG
        elif close_now < bb_lower_now:
            direction = Direction.SHORT
        else:
            return None  # Price still inside bands — no breakout yet

        # Step 4: Volume surge
        if vol_ratio < self.breakout_vol_mult:
            return None

        # Stop and take-profit
        entry_price = close_now
        stop_dist = atr_now * self.atr_tp_mult

        if direction == Direction.LONG:
            stop_loss = bb_lower_now  # below opposite band
            take_profit = entry_price + stop_dist * self.atr_tp_mult
        else:
            stop_loss = bb_upper_now
            take_profit = entry_price - stop_dist * self.atr_tp_mult

        # Compression ratio: how tight was the squeeze relative to historical width?
        compression_ratio = (
            1.0 - (min_width / bb_width.iloc[-self.squeeze_lookback :].max())
            if bb_width.iloc[-self.squeeze_lookback :].max() > 0
            else 0.0
        )

        conviction = self._score_conviction(
            compression_ratio, vol_ratio, kc_squeeze, direction
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
                "bb_upper": round(bb_upper_now, 8),
                "bb_lower": round(bb_lower_now, 8),
                "kc_upper": round(kc_upper_now, 8),
                "kc_lower": round(kc_lower_now, 8),
                "bb_width": round(current_width, 6),
                "bb_width_min_lookback": round(float(min_width), 6),
                "kc_squeeze_confirmed": kc_squeeze,
                "volume_ratio": round(vol_ratio, 2),
                "compression_ratio": round(float(compression_ratio), 4),
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit if:
          - Price re-enters the Bollinger Bands (breakout failure), OR
          - Trailing stop is set and price reverses past it.
        """
        if not self._min_rows(df, self.bb_period + 2):
            return False

        close = df["close"]
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        close_now = close.iloc[-1]
        bb_upper = bb.upper.iloc[-1]
        bb_lower = bb.lower.iloc[-1]

        if position.side == Direction.LONG:
            # Breakout failure: price drops back inside the bands
            if close_now < bb_upper:
                return True
            # Trailing stop
            if position.trailing_stop and close_now <= position.trailing_stop:
                return True
        else:
            if close_now > bb_lower:
                return True
            if position.trailing_stop and close_now >= position.trailing_stop:
                return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        compression_ratio: float,
        vol_ratio: float,
        kc_confirmed: bool,
        direction: Direction,
    ) -> float:
        score = 0.0

        # Compression depth
        score += 0.35 * min(float(compression_ratio), 1.0)

        # Volume surge (2x = base, 3x = max)
        vol_score = min((vol_ratio - self.breakout_vol_mult) / self.breakout_vol_mult, 1.0)
        score += 0.35 * max(0.0, vol_score)

        # Keltner confirmation
        if kc_confirmed:
            score += 0.30

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
