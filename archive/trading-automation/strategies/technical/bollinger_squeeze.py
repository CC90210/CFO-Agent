"""
strategies/technical/bollinger_squeeze.py — Bollinger Band Squeeze Breakout Strategy (v2)

Logic
-----
Volatility contracts into an extreme squeeze, then expands — this strategy profits from
catching the breakout EARLY, before the crowd piles in.

Squeeze detection (early entry, not late):
    - BB width is in the bottom 10th percentile of the lookback period (extremely compressed)
    - Keltner Channel squeeze adds minor confirmation weight (not a hard gate)

2-bar breakout filter (eliminates false breakouts):
    - Bar N-1 AND Bar N must BOTH close outside the same BB band
    - First close outside the band is ignored — require consecutive confirmation

Volume logic (FLIPPED from v1):
    - Enter when volume is NORMAL or BELOW average (accumulation phase, not exhaustion)
    - Skip if breakout bar volume > 2x average (retail exhaustion / distribution)
    - High volume ON the breakout bar is a warning sign, not confirmation

Stops — ATR-based (not band-based which is too wide after squeeze release):
    - LONG stop:  entry - 1.5× ATR
    - SHORT stop: entry + 1.5× ATR

Take profit — volatility expansion target:
    - LONG:  entry + 2.5× ATR
    - SHORT: entry - 2.5× ATR

Exit logic (no premature BB re-entry exits):
    - Exit when: trailing stop hit OR price closes inside the OPPOSITE band (reversal)
    - The old "2 closes inside same band" exit is removed — caused constant false exits

Conviction scoring (v2):
    +0.40  BB width compression ratio (how extreme was the squeeze)
    +0.30  Momentum on breakout bars (Rate of Change across the 2-bar confirmation window)
    +0.30  Keltner squeeze confirmation (minor weight — correlation guard, not primary gate)

Best markets  : BTC/USDT, ETH/USDT, Gold (XAU/USD), high-beta stocks
Best timeframes: 4H, Daily — squeezes take days to weeks to resolve
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import bollinger_bands, atr, keltner_channels


class BollingerSqueezeStrategy(BaseStrategy):
    """
    Bollinger Band Squeeze Breakout v2 — enters early on 2-bar confirmed breakout
    from an extreme compression, with volume-exhaustion filter and ATR-based risk.
    """

    name = "bollinger_squeeze"
    description = (
        "Detects extreme volatility squeezes (BB width bottom 10th percentile) and enters "
        "on 2 consecutive closes outside the BB band — only when volume is NOT exhausted. "
        "ATR-based stops and exits only on confirmed reversal, not band re-entry."
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
        squeeze_lookback: int = 60,
        squeeze_percentile: float = 10.0,
        exhaustion_vol_mult: float = 2.0,
        atr_period: int = 14,
        atr_stop_mult: float = 2.0,
        atr_tp_mult: float = 5.0,
        volume_period: int = 20,
    ) -> None:
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.kc_ema_period = kc_ema_period
        self.kc_atr_period = kc_atr_period
        self.kc_mult = kc_mult
        self.squeeze_lookback = squeeze_lookback
        # Bottom N-th percentile of BB width that defines "extreme squeeze"
        self.squeeze_percentile = squeeze_percentile
        # Volume above this multiple = exhaustion, skip entry
        self.exhaustion_vol_mult = exhaustion_vol_mult
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
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

        # Current and previous bar values
        bb_upper_now = bb.upper.iloc[-1]
        bb_lower_now = bb.lower.iloc[-1]
        bb_upper_prev = bb.upper.iloc[-2]
        bb_lower_prev = bb.lower.iloc[-2]
        kc_upper_now = kc.upper.iloc[-1]
        kc_lower_now = kc.lower.iloc[-1]
        close_now = close.iloc[-1]
        close_prev = close.iloc[-2]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]

        if avg_vol_now <= 0 or pd.isna(avg_vol_now):
            return None

        vol_ratio = vol_now / avg_vol_now

        # ------------------------------------------------------------------
        # Step 1: Squeeze must be EXTREME — BB width in bottom N-th percentile
        # ------------------------------------------------------------------
        bb_width = bb.width
        squeeze_window = bb_width.iloc[-self.squeeze_lookback:]

        if squeeze_window.isna().all() or len(squeeze_window.dropna()) < 10:
            return None

        percentile_threshold = squeeze_window.quantile(self.squeeze_percentile / 100.0)
        current_width = bb_width.iloc[-1]

        # Width on the PREVIOUS bar (when squeeze was active) must have been
        # in the bottom percentile — we detect squeeze while still in it,
        # not after it has already expanded several bars.
        prev_width = bb_width.iloc[-2]
        squeeze_was_extreme = (
            prev_width <= percentile_threshold or current_width <= percentile_threshold
        )

        if not squeeze_was_extreme:
            return None

        # ------------------------------------------------------------------
        # Step 2: 2-bar breakout confirmation — BOTH bars must close outside
        # the SAME band. Filters the majority of false breakouts.
        # ------------------------------------------------------------------
        long_breakout = (close_now > bb_upper_now) and (close_prev > bb_upper_prev)
        short_breakout = (close_now < bb_lower_now) and (close_prev < bb_lower_prev)

        if long_breakout:
            direction = Direction.LONG
        elif short_breakout:
            direction = Direction.SHORT
        else:
            return None

        # ------------------------------------------------------------------
        # Step 3: Volume exhaustion filter (FLIPPED from v1)
        # High volume on breakout = retail chasing = exhaustion → SKIP
        # Low/normal volume = accumulation/institutional → ENTER
        # ------------------------------------------------------------------
        if vol_ratio > self.exhaustion_vol_mult:
            return None

        # ------------------------------------------------------------------
        # Step 4: Keltner Channel squeeze confirmation (minor weight only)
        # ------------------------------------------------------------------
        kc_squeeze = (bb_upper_now <= kc_upper_now) and (bb_lower_now >= kc_lower_now)

        # ------------------------------------------------------------------
        # Step 5: ATR-based stops and targets
        # ------------------------------------------------------------------
        entry_price = close_now

        if direction == Direction.LONG:
            stop_loss = entry_price - (atr_now * self.atr_stop_mult)
            take_profit = entry_price + (atr_now * self.atr_tp_mult)
        else:
            stop_loss = entry_price + (atr_now * self.atr_stop_mult)
            take_profit = entry_price - (atr_now * self.atr_tp_mult)

        # Guard: stop and take_profit must be valid positive prices
        if stop_loss <= 0 or take_profit <= 0:
            return None

        # ------------------------------------------------------------------
        # Step 6: Conviction scoring
        # ------------------------------------------------------------------
        max_width = squeeze_window.max()
        compression_ratio = (
            1.0 - (float(prev_width) / float(max_width))
            if max_width > 0
            else 0.0
        )

        # Rate of change across the 2-bar breakout window as momentum signal
        close_2_bars_ago = close.iloc[-3] if len(close) >= 3 else close.iloc[-2]
        roc = abs(close_now - close_2_bars_ago) / close_2_bars_ago if close_2_bars_ago > 0 else 0.0
        # Normalise ROC: 1% move = ~0.5 score, 2%+ = max score
        roc_score = min(roc / 0.02, 1.0)

        conviction = self._score_conviction(
            compression_ratio, roc_score, kc_squeeze, direction
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
                "bb_width_current": round(float(current_width), 6),
                "bb_width_prev": round(float(prev_width), 6),
                "squeeze_percentile_threshold": round(float(percentile_threshold), 6),
                "kc_squeeze_confirmed": kc_squeeze,
                "volume_ratio": round(vol_ratio, 2),
                "compression_ratio": round(float(compression_ratio), 4),
                "roc_2bar": round(roc, 6),
                "atr": round(atr_now, 8),
                "stop_distance_atr": self.atr_stop_mult,
                "tp_distance_atr": self.atr_tp_mult,
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit conditions (no premature band re-entry exits):
          - Trailing stop hit, OR
          - Price closes inside the OPPOSITE band (confirmed reversal, not just retracement).
            LONG: close below BB lower band = reversal confirmed.
            SHORT: close above BB upper band = reversal confirmed.
        """
        if not self._min_rows(df, self.bb_period + 2):
            return False

        close = df["close"]
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        close_now = close.iloc[-1]
        bb_upper_now = bb.upper.iloc[-1]
        bb_lower_now = bb.lower.iloc[-1]

        if position.side == Direction.LONG:
            # Reversal: price crossed through and closed below the LOWER band
            if close_now < bb_lower_now:
                return True
            if position.trailing_stop is not None and close_now <= position.trailing_stop:
                return True
        else:
            # Reversal: price crossed through and closed above the UPPER band
            if close_now > bb_upper_now:
                return True
            if position.trailing_stop is not None and close_now >= position.trailing_stop:
                return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        compression_ratio: float,
        roc_score: float,
        kc_confirmed: bool,
        direction: Direction,
    ) -> float:
        score = 0.0

        # 40%: how extreme was the squeeze compression
        score += 0.40 * min(float(compression_ratio), 1.0)

        # 30%: momentum on the 2-bar breakout (rate of change)
        score += 0.30 * min(float(roc_score), 1.0)

        # 30%: Keltner Channel squeeze confirmation
        if kc_confirmed:
            score += 0.30

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
