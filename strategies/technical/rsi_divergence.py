"""
strategies/technical/rsi_divergence.py — RSI Divergence + Bollinger %B Mean Reversion

Logic
-----
Detect hidden momentum exhaustion via RSI divergence — price and RSI disagree at swing
points — and confirm with Bollinger %B at band extremes. Built exclusively for choppy,
ranging crypto markets where price oscillates around a statistical mean.

LONG signal conditions (all required):
    - Bullish RSI divergence: price makes a lower low but RSI makes a higher low
      within the divergence_lookback window (minimum divergence_min_bars separation)
    - Bollinger %B < 0.20 (price is at the lower band extreme — maximum compression)
    - ADX < 25 (ranging market — divergence has no edge in trending regimes)
    - ATR/close > 0.005 (volatility floor — skip dead markets where spreads consume edge)

SHORT signal conditions (mirror):
    - Bearish RSI divergence: price makes a higher high but RSI makes a lower high
    - Bollinger %B > 0.80 (price is at the upper band extreme)
    - ADX < 25
    - ATR/close > 0.005

Exit trigger: RSI crosses 50 (mean reversion complete) OR price crosses the BB midline.

Stop loss:  1.0x ATR(14) beyond entry.
Take profit: BB midline OR rr_min * stop_distance, whichever produces a larger move
             — enforces the minimum 2:1 R:R floor.

Conviction scoring
------------------
    +0.30  Base: divergence detected
    +0.15  %B very extreme (<0.05 for longs, >0.95 for shorts)
    +0.15  Volume above volume_mult × average volume
    +0.15  Divergence magnitude > 10 RSI points between the two swing readings
    +0.15  Price aligned with EMA(200) trend (counter-trend alignment adds confidence)
    +0.10  ADX < 15 (deeply ranging — ideal regime for mean reversion)

Best markets  : Range-bound crypto pairs, BTC/USDT on consolidation weeks
Best timeframes: 15m, 1H, 4H
"""

from __future__ import annotations

from typing import NamedTuple

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import rsi, bollinger_bands, atr, adx, ema


# ---------------------------------------------------------------------------
# Internal result type for the divergence detector
# ---------------------------------------------------------------------------


class _DivergenceResult(NamedTuple):
    found: bool
    magnitude: float  # absolute RSI-point difference between the two swing readings
    swing1_idx: int   # iloc index of the earlier swing point
    swing2_idx: int   # iloc index of the more recent swing point


class RSIDivergenceStrategy(BaseStrategy):
    """
    RSI Divergence + Bollinger %B mean reversion — trades momentum exhaustion
    confirmed by price-band extremes in choppy, ranging crypto markets.
    """

    name = "rsi_divergence"
    description = (
        "Bullish/bearish RSI divergence at Bollinger %B extremes (<0.20 / >0.80), "
        "filtered to ranging regimes via ADX < 25. "
        "Target: reversion to BB midline with minimum 2:1 R:R."
    )
    timeframes = ["15m", "1h", "4h"]
    markets = ["crypto", "forex"]

    def __init__(
        self,
        rsi_period: int = 10,
        divergence_lookback: int = 10,
        divergence_min_bars: int = 3,
        pctb_long: float = 0.20,
        pctb_short: float = 0.80,
        bb_period: int = 20,
        bb_std: float = 2.0,
        adx_period: int = 14,
        adx_max: float = 25.0,
        atr_period: int = 14,
        atr_stop_mult: float = 1.0,
        rr_min: float = 2.0,
        volume_period: int = 20,
        volume_mult: float = 1.2,
        # Volatility floor — ATR(14)/close must exceed this ratio.
        # 0.005 = 0.5% minimum move; below this spreads consume the entire edge.
        min_atr_pct: float = 0.005,
        # EMA(200) trend context — used for conviction bonus only, never as a hard gate.
        # Mean reversion trades against the trend by design; blocking based on EMA200
        # would eliminate the majority of valid setups in crypto bear/choppy markets.
        ema_trend_period: int = 200,
    ) -> None:
        self.rsi_period = rsi_period
        self.divergence_lookback = divergence_lookback
        self.divergence_min_bars = divergence_min_bars
        self.pctb_long = pctb_long
        self.pctb_short = pctb_short
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_min = rr_min
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.min_atr_pct = min_atr_pct
        self.ema_trend_period = ema_trend_period
        # EMA(200) requires extra bars for smoothing to converge beyond cold-start bias.
        self._ema_min_bars = ema_trend_period + 10
        # Minimum bars needed to compute all indicators.  The divergence scan
        # needs divergence_lookback extra bars on top of the longest indicator window.
        self._min_bars = (
            max(rsi_period, bb_period, adx_period, atr_period)
            + divergence_lookback
            + 5
        )

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        rsi_series = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        close_now = close.iloc[-1]
        bb_pct = bb.percent_b.iloc[-1]
        bb_mid = bb.middle.iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        vol_ratio = vol_now / avg_vol_now if avg_vol_now > 0 else 1.0

        # Volatility floor — skip dead markets (spreads consume the edge)
        if close_now > 0 and self.min_atr_pct > 0:
            if (atr_now / close_now) < self.min_atr_pct:
                return None

        # ADX gate — only operate in ranging markets
        if adx_now >= self.adx_max:
            return None

        # Attempt divergence detection for both directions
        bull_div = self._find_divergence(
            df["low"], rsi_series, direction=Direction.LONG
        )
        bear_div = self._find_divergence(
            df["high"], rsi_series, direction=Direction.SHORT
        )

        # Determine entry direction — require divergence AND %B confirmation
        direction: Direction | None = None
        active_div: _DivergenceResult | None = None

        if bull_div.found and bb_pct < self.pctb_long:
            direction = Direction.LONG
            active_div = bull_div
        elif bear_div.found and bb_pct > self.pctb_short:
            direction = Direction.SHORT
            active_div = bear_div

        if direction is None or active_div is None:
            return None

        # EMA(200) trend context — conviction modifier, never a hard gate
        ema_trend: float | None = None
        if len(df) >= self._ema_min_bars:
            ema_series = ema(close, self.ema_trend_period)
            ema_trend = ema_series.iloc[-1]

        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now
        min_tp_dist = self.rr_min * stop_dist

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            bb_mid_dist = bb_mid - entry_price
            take_profit = entry_price + max(bb_mid_dist, min_tp_dist)
        else:
            stop_loss = entry_price + stop_dist
            bb_mid_dist = entry_price - bb_mid
            take_profit = entry_price - max(bb_mid_dist, min_tp_dist)

        # Hard safety: ensure take_profit is directionally valid and positive
        if direction == Direction.LONG and take_profit <= entry_price:
            take_profit = entry_price + min_tp_dist
        if direction == Direction.SHORT and take_profit >= entry_price:
            take_profit = entry_price - min_tp_dist
        if take_profit <= 0:
            return None

        volume_confirmed = vol_ratio >= self.volume_mult

        conviction = self._score_conviction(
            direction=direction,
            bb_pct=bb_pct,
            adx_now=adx_now,
            vol_ratio=vol_ratio,
            volume_confirmed=volume_confirmed,
            div_magnitude=active_div.magnitude,
            ema_trend=ema_trend,
            close_now=close_now,
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
                "bb_pct_b": round(bb_pct, 4),
                "bb_mid": round(bb_mid, 8),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 8),
                "volume_ratio": round(vol_ratio, 2),
                "divergence_magnitude": round(active_div.magnitude, 2),
                "divergence_swing1_idx": active_div.swing1_idx,
                "divergence_swing2_idx": active_div.swing2_idx,
                "ema_trend": round(ema_trend, 8) if ema_trend is not None else None,
                "stop_dist": round(stop_dist, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit when RSI crosses 50 (mean reversion complete) OR price crosses BB midline."""
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        rsi_series = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)

        rsi_now = rsi_series.iloc[-1]
        close_now = close.iloc[-1]
        bb_mid = bb.middle.iloc[-1]

        if position.side == Direction.LONG:
            # Reversion complete: RSI returned to neutral, or price crossed above midline
            return rsi_now >= 50.0 or close_now >= bb_mid
        else:
            # Reversion complete: RSI returned to neutral, or price crossed below midline
            return rsi_now <= 50.0 or close_now <= bb_mid

    # ------------------------------------------------------------------
    # Divergence detection
    # ------------------------------------------------------------------

    def _find_divergence(
        self,
        price_series: pd.Series,
        rsi_series: pd.Series,
        direction: Direction,
    ) -> _DivergenceResult:
        """
        Scan the last divergence_lookback bars for a classic RSI divergence.

        For bullish divergence (direction=LONG):
            - Uses the low series to find two swing lows
            - Condition: price[swing2] < price[swing1] but RSI[swing2] > RSI[swing1]
            - This signals that selling momentum is decelerating despite a new price low

        For bearish divergence (direction=SHORT):
            - Uses the high series to find two swing highs
            - Condition: price[swing2] > price[swing1] but RSI[swing2] < RSI[swing1]
            - This signals that buying momentum is decelerating despite a new price high

        Swing point definition:
            A swing low:  low[i] < low[i-1]  and  low[i] < low[i+1]
            A swing high: high[i] > high[i-1] and  high[i] > high[i+1]

        Returns _DivergenceResult(found, magnitude, swing1_idx, swing2_idx).
        Indices are iloc positions relative to the full series.
        """
        n = len(price_series)
        # Search window: the last divergence_lookback bars, excluding the final bar
        # (index -1) because it hasn't formed a confirmed candle close on both sides yet.
        # We need at least i+1 to confirm the right shoulder of a swing point.
        start = max(1, n - self.divergence_lookback - 1)
        end = n - 2  # leave one bar so swing[i+1] exists

        swings: list[int] = []
        for i in range(start, end + 1):
            p_prev = price_series.iloc[i - 1]
            p_curr = price_series.iloc[i]
            p_next = price_series.iloc[i + 1]

            if direction == Direction.LONG:
                # Swing low: current bar is lower than both neighbours
                if p_curr < p_prev and p_curr < p_next:
                    swings.append(i)
            else:
                # Swing high: current bar is higher than both neighbours
                if p_curr > p_prev and p_curr > p_next:
                    swings.append(i)

        # Need at least two swing points with minimum bar separation
        if len(swings) < 2:
            return _DivergenceResult(False, 0.0, -1, -1)

        # Take the two most recent swing points
        swing1_iloc = swings[-2]
        swing2_iloc = swings[-1]

        # Enforce minimum bar separation to avoid counting adjacent bars as a divergence
        if (swing2_iloc - swing1_iloc) < self.divergence_min_bars:
            return _DivergenceResult(False, 0.0, -1, -1)

        price1 = price_series.iloc[swing1_iloc]
        price2 = price_series.iloc[swing2_iloc]
        rsi1 = rsi_series.iloc[swing1_iloc]
        rsi2 = rsi_series.iloc[swing2_iloc]

        # Guard against NaN RSI values on short series edges
        if pd.isna(rsi1) or pd.isna(rsi2):
            return _DivergenceResult(False, 0.0, -1, -1)

        if direction == Direction.LONG:
            # Bullish: price makes lower low, RSI makes higher low
            divergence_found = price2 < price1 and rsi2 > rsi1
        else:
            # Bearish: price makes higher high, RSI makes lower high
            divergence_found = price2 > price1 and rsi2 < rsi1

        if not divergence_found:
            return _DivergenceResult(False, 0.0, -1, -1)

        magnitude = abs(rsi2 - rsi1)
        return _DivergenceResult(True, magnitude, swing1_iloc, swing2_iloc)

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        bb_pct: float,
        adx_now: float,
        vol_ratio: float,
        volume_confirmed: bool,
        div_magnitude: float,
        ema_trend: float | None,
        close_now: float,
    ) -> float:
        """
        Build a conviction score from independent confirmation signals.

        Components (max unsigned total = 1.00):
            0.30  Base: divergence pattern confirmed
            0.15  %B very extreme (<0.05 for longs, >0.95 for shorts)
            0.15  Volume above volume_mult threshold
            0.15  Divergence magnitude > 10 RSI points
            0.15  EMA(200) trend alignment (mean reversion aligns with macro bias)
            0.10  ADX < 15 (deeply ranging — best regime for mean reversion)

        Result is clamped to [-1.0, 1.0] and signed by direction.
        """
        score = 0.30  # base: divergence was detected and %B threshold passed

        # %B very extreme bonus — deeper in the band = stronger reversal pressure
        if direction == Direction.LONG and bb_pct < 0.05:
            score += 0.15
        elif direction == Direction.SHORT and bb_pct > 0.95:
            score += 0.15

        # Volume as conviction modifier — not a hard gate (feedback_volume_gates.md)
        if volume_confirmed:
            score += 0.15

        # Divergence magnitude — large RSI separation = stronger exhaustion signal
        if div_magnitude > 10.0:
            score += 0.15

        # EMA(200) trend alignment
        # For mean reversion: trading WITH the macro trend adds conviction
        # (e.g., buying a dip in a macro uptrend, or shorting a rally in a macro downtrend)
        if ema_trend is not None:
            trend_aligned = (
                (direction == Direction.LONG and close_now >= ema_trend)
                or (direction == Direction.SHORT and close_now <= ema_trend)
            )
            if trend_aligned:
                score += 0.15

        # ADX deeply ranging bonus — the lower the ADX, the stronger the mean-reversion edge
        if adx_now < 15.0:
            score += 0.10

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
