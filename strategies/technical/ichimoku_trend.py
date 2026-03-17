"""
strategies/technical/ichimoku_trend.py — Ichimoku Cloud Trend Following Strategy

Logic
-----
The Ichimoku Kinko Hyo system is a complete trading system — it provides trend
direction, momentum, support/resistance, and signal confirmation all in one view.

LONG entry — ALL conditions required:
    1. Price above the cloud (above both Senkou A and B)
    2. Tenkan-sen (conversion line) > Kijun-sen (base line)
    3. Tenkan-sen crosses above Kijun-sen (TK cross) — the primary entry signal
    4. Chikou Span (lagging span) is above the cloud 26 bars ago (future confirmation)
    5. The cloud ahead is bullish (Senkou A > Senkou B)

SHORT entry (mirror):
    1. Price below cloud
    2. Tenkan-sen < Kijun-sen
    3. Bearish TK cross (Tenkan crosses below Kijun)
    4. Chikou below past cloud
    5. Cloud ahead is bearish (Senkou A < Senkou B)

Entry timing: enter on the bar after the TK cross is confirmed.

Stop loss:  Enter at Kijun-sen level (acts as dynamic support/resistance).
Take profit: Opposite side of the cloud (cloud is both support and target zone).

Cloud thickness = trend strength → used to scale conviction.

Exit: Price enters the cloud (loses cloud support/resistance).

Conviction scoring
------------------
    +0.30  Cloud thickness (normalised to ATR)
    +0.30  Chikou confirmation strength
    +0.20  TK cross distance from cloud (crossing far above cloud = strong)
    +0.20  Cloud bullish/bearish agreement with direction

Best markets  : BTC/USDT, ETH/USDT, USD/JPY (Ichimoku's native market), gold, SPY
Best timeframes: 4H, Daily — Ichimoku was designed for Daily charts
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import ichimoku, atr


class IchimokuTrendStrategy(BaseStrategy):
    """Ichimoku Cloud Trend Following — full 5-condition entry checklist."""

    name = "ichimoku_trend"
    description = (
        "Full Ichimoku entry: price above/below cloud, bullish/bearish TK cross, "
        "Chikou confirmation, future cloud direction. Stop at Kijun-sen. "
        "Exit when price enters cloud."
    )
    timeframes = ["4h", "1d"]
    markets = ["crypto", "forex", "equities", "commodities"]

    def __init__(
        self,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_b_period: int = 52,
        displacement: int = 26,
        atr_period: int = 14,
        rr_ratio: float = 2.0,
    ) -> None:
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_b_period = senkou_b_period
        self.displacement = displacement
        self.atr_period = atr_period
        self.rr_ratio = rr_ratio
        self._min_bars = max(senkou_b_period, kijun_period, displacement, atr_period) * 2 + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        close = df["close"]

        cloud = ichimoku(
            df,
            self.tenkan_period,
            self.kijun_period,
            self.senkou_b_period,
            self.displacement,
        )
        atr_series = atr(df, self.atr_period)

        # Current bar values
        tenkan_now = cloud.tenkan.iloc[-1]
        tenkan_prev = cloud.tenkan.iloc[-2]
        kijun_now = cloud.kijun.iloc[-1]
        kijun_prev = cloud.kijun.iloc[-2]
        senkou_a_now = cloud.senkou_a.iloc[-1]
        senkou_b_now = cloud.senkou_b.iloc[-1]
        close_now = close.iloc[-1]
        atr_now = atr_series.iloc[-1]

        # Chikou: check 26 bars back in time
        # Chikou is the close plotted displacement bars in the past
        # For current bar: chikou represents today's close plotted 26 bars ago.
        # To check if chikou is above/below the cloud at THAT point, we look at
        # senkou_a and senkou_b at position [-1 - displacement].
        chikou_check_idx = -(self.displacement + 1)
        if abs(chikou_check_idx) >= len(df):
            return None

        chikou_close = close.iloc[-1]  # current close is the chikou value 26 bars ago
        chikou_ref_senkou_a = cloud.senkou_a.iloc[chikou_check_idx]
        chikou_ref_senkou_b = cloud.senkou_b.iloc[chikou_check_idx]
        chikou_above_cloud = chikou_close > max(chikou_ref_senkou_a, chikou_ref_senkou_b)
        chikou_below_cloud = chikou_close < min(chikou_ref_senkou_a, chikou_ref_senkou_b)

        # Future cloud direction (cloud 26 bars ahead — compare senkou A vs B now)
        # In the ta library implementation, senkou_a/b are already displaced forward.
        # We check the CURRENT senkou values which represent the "future" cloud.
        cloud_bullish = senkou_a_now > senkou_b_now
        cloud_bearish = senkou_a_now < senkou_b_now

        # Cloud boundaries for current bar
        cloud_top = max(senkou_a_now, senkou_b_now)
        cloud_bottom = min(senkou_a_now, senkou_b_now)
        cloud_thickness = cloud_top - cloud_bottom

        # Check if any value is NaN
        if any(
            pd.isna(v) for v in [
                tenkan_now, tenkan_prev, kijun_now, kijun_prev,
                senkou_a_now, senkou_b_now, chikou_ref_senkou_a, chikou_ref_senkou_b,
            ]
        ):
            return None

        # TK cross detection
        tk_cross_up = (tenkan_prev <= kijun_prev) and (tenkan_now > kijun_now)
        tk_cross_down = (tenkan_prev >= kijun_prev) and (tenkan_now < kijun_now)

        # Evaluate LONG conditions
        long_conditions = [
            close_now > cloud_top,            # 1. Price above cloud
            tenkan_now > kijun_now,           # 2. Tenkan > Kijun
            tk_cross_up,                       # 3. TK cross up
            chikou_above_cloud,                # 4. Chikou above cloud
            cloud_bullish,                     # 5. Future cloud bullish
        ]

        # Evaluate SHORT conditions
        short_conditions = [
            close_now < cloud_bottom,          # 1. Price below cloud
            tenkan_now < kijun_now,           # 2. Tenkan < Kijun
            tk_cross_down,                     # 3. TK cross down
            chikou_below_cloud,                # 4. Chikou below cloud
            cloud_bearish,                     # 5. Future cloud bearish
        ]

        long_met = sum(long_conditions)
        short_met = sum(short_conditions)

        # Allow 4/5 conditions (Chikou confirmation can lag)
        if long_met >= 4:
            direction = Direction.LONG
        elif short_met >= 4:
            direction = Direction.SHORT
        else:
            return None  # Not enough conditions met — no signal

        entry_price = close_now
        stop_loss = kijun_now  # Kijun acts as dynamic S/R

        if direction == Direction.LONG:
            risk = entry_price - stop_loss
            take_profit = cloud_top + cloud_thickness  # beyond the cloud
            if risk <= 0:
                take_profit = entry_price + atr_now * self.rr_ratio
                stop_loss = entry_price - atr_now
        else:
            risk = stop_loss - entry_price
            take_profit = cloud_bottom - cloud_thickness
            if risk <= 0:
                take_profit = entry_price - atr_now * self.rr_ratio
                stop_loss = entry_price + atr_now

        conviction = self._score_conviction(
            cloud_thickness, atr_now, chikou_close,
            chikou_ref_senkou_a, chikou_ref_senkou_b,
            close_now, cloud_top, cloud_bottom,
            cloud_bullish, cloud_bearish, direction,
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
                "tenkan": round(tenkan_now, 8),
                "kijun": round(kijun_now, 8),
                "senkou_a": round(senkou_a_now, 8),
                "senkou_b": round(senkou_b_now, 8),
                "cloud_thickness": round(cloud_thickness, 8),
                "cloud_top": round(cloud_top, 8),
                "cloud_bottom": round(cloud_bottom, 8),
                "chikou_above": chikou_above_cloud,
                "cloud_bullish": cloud_bullish,
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """Exit when price enters the Ichimoku Cloud."""
        if not self._min_rows(df, self._min_bars):
            return False

        cloud = ichimoku(
            df,
            self.tenkan_period,
            self.kijun_period,
            self.senkou_b_period,
            self.displacement,
        )

        close_now = df["close"].iloc[-1]
        senkou_a = cloud.senkou_a.iloc[-1]
        senkou_b = cloud.senkou_b.iloc[-1]

        if pd.isna(senkou_a) or pd.isna(senkou_b):
            return False

        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)

        # Require price to penetrate 50% into the cloud, not just touch the edge
        cloud_mid = (cloud_top + cloud_bottom) / 2.0
        if position.side == Direction.LONG:
            return close_now <= cloud_mid  # Price has penetrated deep into cloud
        else:
            return close_now >= cloud_mid  # Price has penetrated deep into cloud

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        cloud_thickness: float,
        atr_val: float,
        chikou: float,
        ref_a: float,
        ref_b: float,
        close: float,
        cloud_top: float,
        cloud_bottom: float,
        cloud_bullish: bool,
        cloud_bearish: bool,
        direction: Direction,
    ) -> float:
        score = 0.0

        # Cloud thickness as trend strength proxy
        if atr_val > 0:
            thickness_norm = min(cloud_thickness / (atr_val * 3), 1.0)
            score += 0.30 * thickness_norm

        # Chikou confirmation: how far is chikou from the cloud edge?
        cloud_edge = min(ref_a, ref_b) if direction == Direction.LONG else max(ref_a, ref_b)
        if atr_val > 0 and not pd.isna(cloud_edge):
            chikou_dist = abs(chikou - cloud_edge) / atr_val
            score += 0.30 * min(chikou_dist / 3.0, 1.0)

        # Price distance above/below cloud
        if atr_val > 0:
            if direction == Direction.LONG:
                price_dist = (close - cloud_top) / atr_val
            else:
                price_dist = (cloud_bottom - close) / atr_val
            score += 0.20 * min(max(price_dist, 0.0), 1.0)

        # Cloud colour alignment
        if (direction == Direction.LONG and cloud_bullish) or (
            direction == Direction.SHORT and cloud_bearish
        ):
            score += 0.20

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
