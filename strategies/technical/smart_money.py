"""
strategies/technical/smart_money.py — Smart Money Concepts (SMC) / Order Flow Strategy

Logic
-----
Smart Money Concepts is the dominant retail-facing framework used by prop firm traders
in 2024-2026.  It models institutional footprints in price data.

Core concepts implemented:

Order Blocks (OB):
    A bearish OB is the last bullish candle before a significant bearish displacement
    (a "down move" that creates a Break of Structure).  Price often returns to this
    zone to fill institutional sell orders.
    A bullish OB is the last bearish candle before a bullish displacement.

    Displacement requirement: 2 consecutive opposing candles (relaxed from 3) whose
    combined range covers at least 1.5× ATR, AND average volume of those candles
    must exceed 1.2× the 20-period average volume.  This catches real institutional
    moves while filtering low-conviction noise.

Fair Value Gaps (FVG):
    A 3-candle pattern where candle 1's high is lower than candle 3's low (bullish FVG)
    or candle 1's low is higher than candle 3's high (bearish FVG).  The "gap" in the
    middle candle represents institutional imbalance — price tends to return to fill it.

Break of Structure (BOS):
    A higher high (bullish BOS) or lower low (bearish BOS) that confirms trend continuation.

Change of Character (CHoCH):
    A BOS in the *opposite* direction to the prior trend — the first sign of reversal.
    A CHoCH is the most powerful signal: it means smart money has flipped.

Strategy flow:
    1. Detect the most recent BOS or CHoCH to determine bias (LONG or SHORT).
    2. Find the most recent unmitigated Order Block in the direction of bias.
    3. Find any Fair Value Gap inside or near the OB.
    4. LONG: Wait for price to return to the bullish OB / FVG zone, then enter.
    5. SHORT: Wait for price to return to the bearish OB / FVG zone.

Stop loss: Below the OB's low (LONG) or above OB's high (SHORT).
Take profit: Primary = R:R ratio (default 3:1). Swing point used only when it
             exists above entry (LONG) / below entry (SHORT) AND delivers at
             least 2:1 R:R — ensures every trade has a reachable target.

Exit triggers (any one fires):
    1. CHoCH against position direction (structural flip = thesis dead).
    2. OB mitigation — price closes through OB zone (zone fails = thesis dead).
    3. Time-based stop — 50 bars without TP hit (opportunity cost exit).

Conviction scoring
------------------
    +0.35  OB strength (volume on OB formation bar, relative to average)
    +0.35  FVG size (larger gap = more institutional imbalance = stronger magnet)
    +0.30  BOS vs CHoCH quality (CHoCH = higher conviction, recent = higher weight)

Best markets  : BTC/USDT, ETH/USDT, NQ (Nasdaq futures), GBP/USD, Gold
Best timeframes: 15m entry, 1H structure, 4H bias
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr


@dataclass
class OrderBlock:
    index: pd.Timestamp
    high: float
    low: float
    direction: Direction  # LONG = bullish OB, SHORT = bearish OB
    volume: float
    mitigated: bool = False


@dataclass
class FairValueGap:
    index: pd.Timestamp
    top: float
    bottom: float
    direction: Direction  # LONG = bullish FVG, SHORT = bearish FVG
    size: float


@dataclass
class StructureEvent:
    index: pd.Timestamp
    kind: str  # "BOS_bullish", "BOS_bearish", "CHoCH_bullish", "CHoCH_bearish"
    level: float  # the structure level that was broken


class SmartMoneyStrategy(BaseStrategy):
    """
    Smart Money Concepts — Order Blocks, Fair Value Gaps, Break of Structure,
    and Change of Character for institutional-grade entries.
    """

    name = "smart_money"
    description = (
        "Detects Order Blocks (last candle before displacement), Fair Value Gaps "
        "(3-candle imbalance), Break of Structure, and Change of Character. "
        "Enters when price returns to unmitigated OB/FVG after confirming BOS/CHoCH."
    )
    timeframes = ["15m", "1h", "4h"]
    markets = ["crypto", "forex", "indices", "futures"]

    def __init__(
        self,
        swing_lookback: int = 5,         # bars each side — reduced from 10 (4h: 10=40h too long, 5=20h)
        ob_lookback: int = 50,           # bars to search for order blocks
        fvg_min_size_atr_ratio: float = 0.15,  # reduced from 0.3 — small FVGs inside OBs are valid
        bos_lookback: int = 100,         # bars to look back for structure events
        ob_entry_tolerance: float = 0.015,    # widened from 0.8% to 1.5% — institutional zones are wide
        atr_period: int = 14,
        atr_stop_mult: float = 2.0,      # stop beyond OB (2x ATR buffer for breathing room)
        rr_ratio: float = 3.0,
        volume_period: int = 20,
        min_rr_for_swing_tp: float = 2.0,  # swing TP only used if it delivers at least this R:R
        displacement_atr_mult: float = 1.5,  # OB displacement must cover this × ATR total range
        displacement_vol_mult: float = 1.2,  # displacement candles avg vol > this × rolling avg vol
        time_stop_bars: int = 50,        # exit if TP not reached within this many bars
    ) -> None:
        self.swing_lookback = swing_lookback
        self.ob_lookback = ob_lookback
        self.fvg_min_size_atr_ratio = fvg_min_size_atr_ratio
        self.bos_lookback = bos_lookback
        self.ob_entry_tolerance = ob_entry_tolerance
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self.min_rr_for_swing_tp = min_rr_for_swing_tp
        self.displacement_atr_mult = displacement_atr_mult
        self.displacement_vol_mult = displacement_vol_mult
        self.time_stop_bars = time_stop_bars
        self._min_bars = max(ob_lookback, bos_lookback, swing_lookback * 2, atr_period) + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        atr_series = atr(df, self.atr_period)
        atr_now = atr_series.iloc[-1]
        close_now = df["close"].iloc[-1]

        avg_vol = df["volume"].rolling(self.volume_period).mean()
        avg_vol_now = avg_vol.iloc[-1]

        # Step 1: Determine structural bias from recent BOS/CHoCH
        structure_events = self._detect_structure(df)
        if not structure_events:
            return None

        most_recent = structure_events[-1]
        if "bullish" in most_recent.kind:
            bias = Direction.LONG
        elif "bearish" in most_recent.kind:
            bias = Direction.SHORT
        else:
            return None

        # Step 2: Find the most recent unmitigated Order Block aligned with bias
        order_blocks = self._detect_order_blocks(df, atr_series, avg_vol)
        relevant_obs = [
            ob for ob in order_blocks
            if ob.direction == bias and not ob.mitigated
        ]

        if not relevant_obs:
            return None

        # Use the most recent unmitigated OB
        target_ob = relevant_obs[-1]

        # Step 3: Check if price is currently inside or touching the OB zone
        if bias == Direction.LONG:
            ob_zone_top = target_ob.high
            ob_zone_bottom = target_ob.low
            in_ob = ob_zone_bottom * (1 - self.ob_entry_tolerance) <= close_now <= ob_zone_top
        else:
            ob_zone_top = target_ob.high
            ob_zone_bottom = target_ob.low
            in_ob = ob_zone_bottom <= close_now <= ob_zone_top * (1 + self.ob_entry_tolerance)

        if not in_ob:
            return None  # Price hasn't returned to OB yet

        # Step 4: Find nearby FVG for additional confluence
        fvgs = self._detect_fvgs(df, atr_now)
        aligned_fvgs = [
            f for f in fvgs
            if f.direction == bias
            and ob_zone_bottom <= (f.top + f.bottom) / 2 <= ob_zone_top
        ]
        best_fvg: Optional[FairValueGap] = aligned_fvgs[-1] if aligned_fvgs else None

        # Step 5: Entry price and levels
        entry_price = close_now
        buffer = atr_now * self.atr_stop_mult

        if bias == Direction.LONG:
            stop_loss = target_ob.low - buffer
            risk = entry_price - stop_loss

            # Primary TP: always guarantee a reachable R:R target
            take_profit = entry_price + risk * self.rr_ratio

            # Bonus: use swing high only if it provides at least min_rr_for_swing_tp
            swing_highs = self._swing_highs(df)
            candidates = [sh for sh in swing_highs if sh > entry_price]
            if candidates:
                tp_swing = min(candidates)  # nearest swing high above entry
                swing_rr = (tp_swing - entry_price) / risk if risk > 0 else 0.0
                if swing_rr >= self.min_rr_for_swing_tp:
                    take_profit = tp_swing
        else:
            stop_loss = target_ob.high + buffer
            risk = stop_loss - entry_price

            # Primary TP: always guarantee a reachable R:R target
            take_profit = entry_price - risk * self.rr_ratio

            # Bonus: use swing low only if it provides at least min_rr_for_swing_tp
            swing_lows = self._swing_lows(df)
            candidates = [sl for sl in swing_lows if sl < entry_price]
            if candidates:
                tp_swing = max(candidates)  # nearest swing low below entry
                swing_rr = (entry_price - tp_swing) / risk if risk > 0 else 0.0
                if swing_rr >= self.min_rr_for_swing_tp:
                    take_profit = tp_swing

        # Conviction
        ob_vol_ratio = target_ob.volume / avg_vol_now if avg_vol_now > 0 else 1.0
        fvg_size = best_fvg.size if best_fvg else 0.0
        is_choch = "CHoCH" in most_recent.kind

        conviction = self._score_conviction(
            ob_vol_ratio, fvg_size, atr_now, is_choch, bias
        )

        return Signal(
            symbol=symbol,
            direction=bias,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "ob_high": round(target_ob.high, 8),
                "ob_low": round(target_ob.low, 8),
                "ob_volume_ratio": round(ob_vol_ratio, 2),
                "fvg_size": round(fvg_size, 8) if fvg_size else None,
                "structure_event": most_recent.kind,
                "structure_level": round(most_recent.level, 8),
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when ANY of the following triggers fires:
          1. CHoCH forms against position direction (structural flip — thesis dead).
          2. OB mitigation — price closes through the OB zone (zone fails).
          3. Time-based stop — position open more than time_stop_bars bars.
        """
        if not self._min_rows(df, self.bos_lookback + 5):
            return False

        close_now = df["close"].iloc[-1]

        # Trigger 1: CHoCH against position
        structure_events = self._detect_structure(df)
        if structure_events:
            last_event = structure_events[-1]
            if position.side == Direction.LONG and "CHoCH_bearish" in last_event.kind:
                return True
            if position.side == Direction.SHORT and "CHoCH_bullish" in last_event.kind:
                return True

        # Trigger 2: OB mitigation — price closed through the zone (OB invalidated)
        ob_high = position.metadata.get("ob_high")
        ob_low = position.metadata.get("ob_low")
        if ob_high is not None and ob_low is not None:
            if position.side == Direction.LONG and close_now < ob_low:
                return True
            if position.side == Direction.SHORT and close_now > ob_high:
                return True

        # Trigger 3: Time-based stop — find how many bars since entry
        if df.index[-1] > position.entry_time:
            bars_since_entry = (df.index >= position.entry_time).sum()
            if bars_since_entry > self.time_stop_bars:
                return True

        return False

    # ------------------------------------------------------------------
    # Structure detection
    # ------------------------------------------------------------------

    def _detect_structure(self, df: pd.DataFrame) -> list[StructureEvent]:
        """Detect Break of Structure (BOS) and Change of Character (CHoCH) events."""
        events: list[StructureEvent] = []
        lookback = min(self.bos_lookback, len(df) - self.swing_lookback * 2)
        if lookback < 10:
            return events

        working_df = df.iloc[-lookback:]
        highs = working_df["high"].values
        lows = working_df["low"].values
        n = len(working_df)
        sw = self.swing_lookback

        last_swing_high: float | None = None
        last_swing_low: float | None = None
        trend = "neutral"  # "up" or "down"

        for i in range(sw, n - sw):
            ts = working_df.index[i]
            # Swing high: highest in window
            if highs[i] == max(highs[max(0, i - sw) : i + sw + 1]):
                sh = highs[i]
                if last_swing_high is not None:
                    if sh > last_swing_high:
                        kind = "BOS_bullish" if trend == "up" else "CHoCH_bullish"
                        events.append(StructureEvent(ts, kind, last_swing_high))
                        trend = "up"
                last_swing_high = sh

            # Swing low: lowest in window
            if lows[i] == min(lows[max(0, i - sw) : i + sw + 1]):
                sl = lows[i]
                if last_swing_low is not None:
                    if sl < last_swing_low:
                        kind = "BOS_bearish" if trend == "down" else "CHoCH_bearish"
                        events.append(StructureEvent(ts, kind, last_swing_low))
                        trend = "down"
                last_swing_low = sl

        return events

    # ------------------------------------------------------------------
    # Order Block detection
    # ------------------------------------------------------------------

    def _detect_order_blocks(
        self,
        df: pd.DataFrame,
        atr_series: pd.Series,
        avg_vol_series: pd.Series,
    ) -> list[OrderBlock]:
        """
        Detect Order Blocks: the last opposing candle before a displacement move.

        Bearish OB: last bullish candle before 2+ consecutive bearish candles
                    whose combined range >= displacement_atr_mult × ATR AND whose
                    average volume >= displacement_vol_mult × rolling avg volume.
        Bullish OB: last bearish candle before 2+ consecutive bullish candles
                    with the same size/volume requirements.

        Using 2 candles (relaxed from 3) with mandatory ATR + volume filters
        catches real institutional displacement while rejecting random noise.
        """
        blocks: list[OrderBlock] = []
        working = df.iloc[-self.ob_lookback :]
        opens = working["open"].values
        closes = working["close"].values
        highs = working["high"].values
        lows = working["low"].values
        volumes = working["volume"].values

        # Align ATR and avg_vol to the working slice
        atr_vals = atr_series.reindex(working.index).values
        avg_vol_vals = avg_vol_series.reindex(working.index).values

        n = len(working)

        for i in range(1, n - 2):
            ts = working.index[i]
            atr_val = atr_vals[i]
            avg_vol = avg_vol_vals[i]

            # Need valid indicator values
            if atr_val != atr_val or avg_vol != avg_vol:  # NaN guard
                continue

            # Bullish displacement: 2 consecutive bullish candles after a bearish candle
            if closes[i] < opens[i]:  # bearish candle — potential bullish OB
                if i + 2 < n and all(closes[i + k] > opens[i + k] for k in range(1, 3)):
                    # Size filter: combined range of displacement candles >= 1.5× ATR
                    disp_range = (
                        max(highs[i + 1], highs[i + 2]) - min(lows[i + 1], lows[i + 2])
                    )
                    if disp_range < self.displacement_atr_mult * atr_val:
                        continue

                    # Volume filter: avg volume of displacement candles > 1.2× rolling avg
                    disp_avg_vol = (volumes[i + 1] + volumes[i + 2]) / 2.0
                    if avg_vol > 0 and disp_avg_vol < self.displacement_vol_mult * avg_vol:
                        continue

                    zone_high = highs[i]
                    zone_low = lows[i]
                    prices_after = closes[i + 2 :]
                    mitigated = any(zone_low <= p <= zone_high for p in prices_after)
                    blocks.append(
                        OrderBlock(
                            index=ts,
                            high=zone_high,
                            low=zone_low,
                            direction=Direction.LONG,
                            volume=volumes[i],
                            mitigated=mitigated,
                        )
                    )

            # Bearish displacement: 2 consecutive bearish candles after a bullish candle
            elif closes[i] > opens[i]:  # bullish candle — potential bearish OB
                if i + 2 < n and all(closes[i + k] < opens[i + k] for k in range(1, 3)):
                    # Size filter: combined range of displacement candles >= 1.5× ATR
                    disp_range = (
                        max(highs[i + 1], highs[i + 2]) - min(lows[i + 1], lows[i + 2])
                    )
                    if disp_range < self.displacement_atr_mult * atr_val:
                        continue

                    # Volume filter: avg volume of displacement candles > 1.2× rolling avg
                    disp_avg_vol = (volumes[i + 1] + volumes[i + 2]) / 2.0
                    if avg_vol > 0 and disp_avg_vol < self.displacement_vol_mult * avg_vol:
                        continue

                    zone_high = highs[i]
                    zone_low = lows[i]
                    prices_after = closes[i + 2 :]
                    mitigated = any(zone_low <= p <= zone_high for p in prices_after)
                    blocks.append(
                        OrderBlock(
                            index=ts,
                            high=zone_high,
                            low=zone_low,
                            direction=Direction.SHORT,
                            volume=volumes[i],
                            mitigated=mitigated,
                        )
                    )

        return blocks

    # ------------------------------------------------------------------
    # Fair Value Gap detection
    # ------------------------------------------------------------------

    def _detect_fvgs(self, df: pd.DataFrame, atr_val: float) -> list[FairValueGap]:
        """
        Detect Fair Value Gaps — 3-candle imbalance pattern.

        Bullish FVG: candle[0].high < candle[2].low (gap in the middle candle's range)
        Bearish FVG: candle[0].low > candle[2].high
        """
        fvgs: list[FairValueGap] = []
        working = df.iloc[-self.ob_lookback :]
        highs = working["high"].values
        lows = working["low"].values
        min_size = atr_val * self.fvg_min_size_atr_ratio

        for i in range(len(working) - 2):
            ts = working.index[i + 1]  # middle candle is the FVG candle
            # Bullish FVG
            gap = lows[i + 2] - highs[i]
            if gap > min_size:
                fvgs.append(
                    FairValueGap(
                        index=ts,
                        top=lows[i + 2],
                        bottom=highs[i],
                        direction=Direction.LONG,
                        size=gap,
                    )
                )
            # Bearish FVG
            gap = lows[i] - highs[i + 2]
            if gap > min_size:
                fvgs.append(
                    FairValueGap(
                        index=ts,
                        top=lows[i],
                        bottom=highs[i + 2],
                        direction=Direction.SHORT,
                        size=gap,
                    )
                )

        return fvgs

    # ------------------------------------------------------------------
    # Swing point detection helpers
    # ------------------------------------------------------------------

    def _swing_highs(self, df: pd.DataFrame) -> list[float]:
        sw = self.swing_lookback
        highs = df["high"].values
        n = len(highs)
        result = []
        for i in range(sw, n - sw):
            if highs[i] == max(highs[max(0, i - sw) : i + sw + 1]):
                result.append(float(highs[i]))
        return result

    def _swing_lows(self, df: pd.DataFrame) -> list[float]:
        sw = self.swing_lookback
        lows = df["low"].values
        n = len(lows)
        result = []
        for i in range(sw, n - sw):
            if lows[i] == min(lows[max(0, i - sw) : i + sw + 1]):
                result.append(float(lows[i]))
        return result

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        ob_vol_ratio: float,
        fvg_size: float,
        atr_val: float,
        is_choch: bool,
        direction: Direction,
    ) -> float:
        score = 0.0

        # OB volume strength
        vol_score = min((ob_vol_ratio - 1.0) / 3.0, 1.0)
        score += 0.35 * max(0.0, vol_score)

        # FVG size
        if atr_val > 0 and fvg_size > 0:
            fvg_norm = min(fvg_size / (atr_val * 2), 1.0)
            score += 0.35 * fvg_norm

        # CHoCH is a stronger signal than BOS
        if is_choch:
            score += 0.30
        else:
            score += 0.15  # BOS = partial credit

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
