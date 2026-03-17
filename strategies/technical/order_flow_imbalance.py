"""
strategies/technical/order_flow_imbalance.py — Order Flow Imbalance Strategy

Logic
-----
Detects institutional accumulation / distribution using volume delta analysis as a
proxy for true Level 2 order flow.  Since exchange-level bid/ask data is unavailable,
buying and selling pressure are inferred from candle structure and volume.

Core concepts
~~~~~~~~~~~~~
Volume Delta Proxy
    Bullish candle (close > open): entire bar volume classified as buying pressure.
    Bearish candle (close <= open): entire bar volume classified as selling pressure.
    Delta = buying_volume - selling_volume per bar.

Cumulative Volume Delta (CVD)
    Rolling sum of per-bar delta over the lookback window.  Rising CVD = buyers in
    control; falling CVD = sellers in control.

CVD Divergence
    Bullish divergence: price makes an equal or lower low while CVD makes a higher
    low over the same window — smart money accumulating into the weakness.
    Bearish divergence: price makes an equal or higher high while CVD makes a lower
    high — institutions distributing into strength.

Absorption
    High-volume candle with a small body relative to its total range.  Signals that
    one side is absorbing the opposing flow — the price barely moves despite large
    participation, indicating institutional supply/demand being worked.

Exhaustion Volume
    Volume spike > 3x the rolling average accompanied by a candle that closes
    against the spike direction (reversal wick) — signals the move is running out
    of fresh participants.

LONG signal conditions (all required):
    - CVD bullish divergence detected over the lookback window
    - Absorption candle present (high volume, small body, close >= open)
    - Volume >= 1.5x 20-bar rolling average
    - ADX < 30 (catching reversals in non-runaway trends)

SHORT signal conditions (mirror):
    - CVD bearish divergence detected
    - Absorption candle present (high volume, close < open)
    - Volume >= 1.5x average
    - ADX < 30

Exit triggers:
    - CVD crosses back through zero (pressure fully reversed)
    - OR price crosses the 20-bar SMA (structural mean)

Stop loss:  2.0x ATR(14) beyond entry candle extreme.
Take profit: 3:1 reward-to-risk ratio from entry.

Conviction scoring
------------------
    +0.35  CVD divergence strength — normalised by the number of bars diverging
           (longer divergence = higher conviction)
    +0.35  Absorption quality — (1 - body_ratio), where body_ratio = body / range.
           A doji on huge volume scores maximum here.
    +0.30  Volume spike magnitude relative to the 1.5x threshold

Best markets   : Crypto (BTC/USDT, ETH/USDT), high-volume liquid equities
Best timeframes: 15m, 1H, 4H
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, adx, sma


# ---------------------------------------------------------------------------
# Internal helpers — not part of the public indicator library
# ---------------------------------------------------------------------------


def _volume_delta(df: pd.DataFrame) -> pd.Series:
    """
    Classify each bar's volume as net buying or selling pressure.

    Bullish candle (close > open)  → positive delta (buying pressure).
    Bearish candle (close <= open) → negative delta (selling pressure).

    Returns a pd.Series aligned to df.index.
    """
    direction = np.where(df["close"] > df["open"], 1.0, -1.0)
    return pd.Series(direction * df["volume"].values, index=df.index, name="vol_delta")


def _cvd(delta: pd.Series, window: int) -> pd.Series:
    """Rolling Cumulative Volume Delta over `window` bars."""
    return delta.rolling(window).sum().rename("cvd")


def _detect_divergence(
    price: pd.Series,
    cvd: pd.Series,
    window: int,
    direction: Direction,
) -> tuple[bool, float]:
    """
    Scan the last `window` bars for a CVD divergence against price.

    Returns
    -------
    (detected: bool, strength: float in [0, 1])
        strength is the fraction of the window over which divergence held,
        used to weight conviction.
    """
    if len(price) < window or len(cvd) < window:
        return False, 0.0

    price_window = price.iloc[-window:]
    cvd_window = cvd.iloc[-window:]

    if direction == Direction.LONG:
        # Bullish divergence: price at / below its window low, CVD above its window low
        price_min_idx = price_window.idxmin()
        cvd_at_price_min = cvd_window.loc[price_min_idx]
        cvd_window_min = cvd_window.min()

        if price_window.iloc[-1] <= price_window.iloc[0]:
            # Price is equal or lower at end vs start — check CVD is higher at end
            if cvd_window.iloc[-1] > cvd_at_price_min:
                # Count how many bars CVD was above its own window low while price was
                # at or below its starting level — measures how long accumulation ran
                price_below = price_window <= price_window.iloc[0]
                cvd_above_min = cvd_window > cvd_window_min
                diverging_bars = int((price_below & cvd_above_min).sum())
                strength = min(diverging_bars / window, 1.0)
                return True, strength

    else:  # SHORT
        # Bearish divergence: price at / above its window high, CVD below its window high
        price_max_idx = price_window.idxmax()
        cvd_at_price_max = cvd_window.loc[price_max_idx]
        cvd_window_max = cvd_window.max()

        if price_window.iloc[-1] >= price_window.iloc[0]:
            if cvd_window.iloc[-1] < cvd_at_price_max:
                price_above = price_window >= price_window.iloc[0]
                cvd_below_max = cvd_window < cvd_window_max
                diverging_bars = int((price_above & cvd_below_max).sum())
                strength = min(diverging_bars / window, 1.0)
                return True, strength

    return False, 0.0


def _absorption_quality(df: pd.DataFrame, vol_avg: pd.Series, idx: int = -1) -> tuple[bool, float]:
    """
    Evaluate the most recent bar for institutional absorption characteristics.

    Absorption = high volume + small body relative to total range.

    Returns
    -------
    (is_absorption: bool, quality: float in [0, 1])
        quality = 1 - body_ratio (closer to 0 body = higher quality)
    """
    bar = df.iloc[idx]
    avg = vol_avg.iloc[idx]

    if avg <= 0:
        return False, 0.0

    total_range = bar["high"] - bar["low"]
    if total_range <= 0:
        return False, 0.0

    body = abs(bar["close"] - bar["open"])
    body_ratio = body / total_range  # 0 = doji (perfect absorption), 1 = marubozu

    vol_ratio = bar["volume"] / avg
    is_high_vol = vol_ratio >= 1.5
    is_small_body = body_ratio <= 0.4  # body <= 40% of range

    is_absorption = is_high_vol and is_small_body
    quality = max(0.0, 1.0 - body_ratio) if is_absorption else 0.0

    return is_absorption, quality


# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class OrderFlowImbalanceStrategy(BaseStrategy):
    """
    Order flow imbalance reversal — detects institutional accumulation / distribution
    via CVD divergence and volume absorption, then fades the move.
    """

    name = "order_flow_imbalance"
    description = (
        "Infers institutional order flow from volume delta and CVD divergence. "
        "Enters on absorption candles where CVD contradicts price structure, "
        "filtered to non-trending regimes (ADX < 30). Target: 3:1 R:R."
    )
    timeframes = ["15m", "1h", "4h"]
    markets = ["crypto", "equities"]

    def __init__(
        self,
        cvd_window: int = 20,
        adx_period: int = 14,
        adx_max: float = 30.0,
        atr_period: int = 14,
        atr_stop_mult: float = 2.0,
        rr_ratio: float = 3.0,
        volume_period: int = 20,
        volume_mult: float = 1.5,
        exhaustion_mult: float = 3.0,
        sma_period: int = 20,
    ) -> None:
        self.cvd_window = cvd_window
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.exhaustion_mult = exhaustion_mult
        self.sma_period = sma_period
        self._min_bars = max(cvd_window, adx_period * 2, atr_period, sma_period) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # Compute indicators
        delta = _volume_delta(df)
        cvd_series = _cvd(delta, self.cvd_window)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()
        sma_series = sma(close, self.sma_period)

        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        close_now = close.iloc[-1]
        sma_now = sma_series.iloc[-1]

        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # Guard: ADX filter — only operate in ranging / transitioning markets
        if adx_now >= self.adx_max:
            return None

        # Guard: volume confirmation required before any analysis
        if vol_ratio < self.volume_mult:
            return None

        # Check both long and short divergence
        long_div, long_div_strength = _detect_divergence(
            close, cvd_series, self.cvd_window, Direction.LONG
        )
        short_div, short_div_strength = _detect_divergence(
            close, cvd_series, self.cvd_window, Direction.SHORT
        )

        # Absorption check (direction-aware)
        bar = df.iloc[-1]
        is_bullish_bar = bar["close"] >= bar["open"]
        absorption_detected, absorption_quality = _absorption_quality(df, avg_vol)

        direction: Direction | None = None
        div_strength: float = 0.0

        if long_div and absorption_detected and is_bullish_bar:
            direction = Direction.LONG
            div_strength = long_div_strength
        elif short_div and absorption_detected and not is_bullish_bar:
            direction = Direction.SHORT
            div_strength = short_div_strength

        if direction is None:
            return None

        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            # Stop below the bar's low, buffered by ATR
            stop_loss = bar["low"] - stop_dist
            take_profit = entry_price + (entry_price - stop_loss) * self.rr_ratio
        else:
            # Stop above the bar's high, buffered by ATR
            stop_loss = bar["high"] + stop_dist
            take_profit = entry_price - (stop_loss - entry_price) * self.rr_ratio

        # Sanity: ensure prices are positive and directionally sound
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        conviction = self._score_conviction(div_strength, absorption_quality, vol_ratio, direction)

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "cvd_now": round(float(cvd_series.iloc[-1]), 4),
                "cvd_divergence_strength": round(div_strength, 4),
                "absorption_quality": round(absorption_quality, 4),
                "volume_ratio": round(vol_ratio, 2),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 8),
                "sma_20": round(sma_now, 8),
                "bar_body_ratio": round(
                    abs(bar["close"] - bar["open"]) / max(bar["high"] - bar["low"], 1e-12), 4
                ),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when:
          - CVD crosses back through zero (buying/selling pressure exhausted), OR
          - Price crosses the 20-bar SMA (structural mean reclaimed / broken).
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        delta = _volume_delta(df)
        cvd_series = _cvd(delta, self.cvd_window)
        sma_series = sma(close, self.sma_period)

        cvd_now = cvd_series.iloc[-1]
        cvd_prev = cvd_series.iloc[-2]
        close_now = close.iloc[-1]
        sma_now = sma_series.iloc[-1]

        if position.side == Direction.LONG:
            # CVD rolled back to zero or negative — buyers gave up
            cvd_reversal = cvd_prev > 0 and cvd_now <= 0
            # Price reclaimed or crossed below the structural mean
            price_exit = close_now <= sma_now
            return cvd_reversal or price_exit
        else:
            # CVD rolled back to zero or positive — sellers gave up
            cvd_reversal = cvd_prev < 0 and cvd_now >= 0
            price_exit = close_now >= sma_now
            return cvd_reversal or price_exit

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        div_strength: float,
        absorption_quality: float,
        vol_ratio: float,
        direction: Direction,
    ) -> float:
        """
        Three-component conviction score:

        0.35 — CVD divergence duration (fraction of window bars that diverged)
        0.35 — Absorption quality (1 - body_ratio; doji on huge vol = max score)
        0.30 — Volume spike above the volume_mult threshold
        """
        score = 0.0

        # Component 1: divergence duration (already normalised to [0, 1])
        score += 0.35 * self._clamp(div_strength, 0.0, 1.0)

        # Component 2: absorption quality (already normalised to [0, 1])
        score += 0.35 * self._clamp(absorption_quality, 0.0, 1.0)

        # Component 3: volume magnitude above the minimum threshold
        # vol_ratio == volume_mult → 0 score; vol_ratio == 2x threshold → max score
        vol_excess = (vol_ratio - self.volume_mult) / self.volume_mult
        vol_score = min(max(vol_excess, 0.0), 1.0)
        score += 0.30 * vol_score

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
