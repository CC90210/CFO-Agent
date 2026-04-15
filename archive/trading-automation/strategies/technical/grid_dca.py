"""
strategies/technical/grid_dca.py — Grid/DCA Hybrid Mean Reversion Strategy

Logic
-----
Traditional grid bots place fixed buy/sell orders at equal price intervals.  This
strategy ports that concept into Atlas's signal framework: instead of managing live
orders, it generates a Signal whenever price has drifted far enough from a central
anchor (the 50-period SMA) to represent a statistically meaningful mean-reversion
opportunity.

The grid spacing is ATR-adaptive: wider in volatile markets, tighter in calm ones,
so each level always represents a consistent risk-normalised deviation rather than
a fixed dollar distance.

Design principle
----------------
Every other Atlas strategy is a trend-follower that bleeds in CHOPPY / RANGING
conditions.  This strategy is the deliberate complement: it ONLY trades when ADX
confirms the market is NOT trending (ADX < 25).  In trending regimes the strategy
returns None and steps aside — the regime-aware engine weights it down further.

Grid levels
-----------
The center is the 50-SMA.  Grid spacing = ATR × grid_atr_mult.  With grid_levels=3
there are 3 buy zones below center and 3 sell zones above:

    Sell zone 3:  SMA + 3 × spacing
    Sell zone 2:  SMA + 2 × spacing
    Sell zone 1:  SMA + 1 × spacing
    ────────── SMA (center) ──────────
    Buy  zone 1:  SMA - 1 × spacing
    Buy  zone 2:  SMA - 2 × spacing
    Buy  zone 3:  SMA - 3 × spacing

Signal is generated for the deepest active level: if price is below buy zone 3,
that's the signal level used (deepest discount = highest conviction).

Entry filters
-------------
  • ADX < adx_max        — market must be non-trending (core filter)
  • RSI < 40 for LONG / RSI > 60 for SHORT — momentum confirms mean-reversion pull
  • Volume > 0.8 × avg   — relaxed vs other strategies; frequent trades desired

Stop / target
-------------
  • Stop: entry − (atr_stop_mult × ATR) for LONG; entry + atr_stop_mult × ATR for SHORT
  • TP:   entry + (risk × rr_ratio) — tight RR (1.5) since we expect frequent small wins

Conviction
----------
Deepest level hit = highest conviction.  Conviction scales linearly from 0.3 (level 1)
to max_conviction (level N).  RSI extremity and ADX reading add small bonuses.

Best markets  : BTC/USDT, ETH/USDT, and altcoins in sideways accumulation
Best timeframes: 1h, 4h (daily bars too slow for grid capture)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, rsi, sma, adx


class GridDCAStrategy(BaseStrategy):
    """
    Grid/DCA Hybrid — profits from sideways price oscillation in choppy crypto
    markets by generating mean-reversion signals at ATR-scaled grid levels around
    a moving-average anchor.  Fully disabled in trending markets (ADX >= adx_max).
    """

    name = "grid_dca"
    description = (
        "ATR-adaptive grid mean reversion anchored to 50-SMA. "
        "Buys deep below SMA, sells deep above SMA. "
        "ADX < 25 filter ensures trades only happen in choppy/ranging markets."
    )
    timeframes = ["1h", "4h"]
    markets = ["crypto"]

    def __init__(
        self,
        grid_atr_mult: float = 1.0,       # grid spacing as multiple of ATR
        grid_levels: int = 3,              # number of grid levels above/below SMA
        sma_period: int = 50,              # center anchor period
        rsi_period: int = 14,
        adx_period: int = 14,
        adx_max: float = 25.0,            # only trade when market is non-trending
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,       # stop distance as multiple of ATR
        rr_ratio: float = 1.5,            # tight RR for frequent small wins
        volume_period: int = 20,
        volume_mult: float = 0.8,         # relaxed: want frequent trades in chop
    ) -> None:
        self.grid_atr_mult = grid_atr_mult
        self.grid_levels = grid_levels
        self.sma_period = sma_period
        self.rsi_period = rsi_period
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        # Need enough bars for all indicators; 60 is a hard floor per spec
        self._min_bars = max(
            sma_period + 10,
            adx_period * 2 + 5,   # adx() requires 2× period
            atr_period + 5,
            rsi_period + 5,
            volume_period + 5,
            60,
        )

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")
        close = df["close"]
        close_now = close.iloc[-1]

        # ── Indicators ──────────────────────────────────────────────────
        sma_series = sma(close, self.sma_period)
        sma_now = sma_series.iloc[-1]
        if pd.isna(sma_now):
            return None

        atr_series = atr(df, self.atr_period)
        atr_now = atr_series.iloc[-1]
        if pd.isna(atr_now) or atr_now <= 0:
            return None

        rsi_series = rsi(close, self.rsi_period)
        rsi_now = rsi_series.iloc[-1]
        if pd.isna(rsi_now):
            return None

        adx_df = adx(df, self.adx_period)
        adx_now = adx_df["adx"].iloc[-1]
        if pd.isna(adx_now):
            return None

        avg_vol = df["volume"].rolling(self.volume_period).mean().iloc[-1]
        vol_now = df["volume"].iloc[-1]
        if pd.isna(avg_vol) or avg_vol <= 0:
            return None

        # ── Gate 1: ADX must confirm a non-trending / choppy market ────
        if adx_now >= self.adx_max:
            return None

        # ── Gate 2: Volume confirmation (relaxed) ──────────────────────
        if vol_now < self.volume_mult * avg_vol:
            return None

        # ── Grid level detection ────────────────────────────────────────
        grid_spacing = atr_now * self.grid_atr_mult

        # Find the deepest active LONG grid level price has reached
        active_long_level = 0
        for lvl in range(1, self.grid_levels + 1):
            threshold = sma_now - lvl * grid_spacing
            if close_now <= threshold:
                active_long_level = lvl

        # Find the deepest active SHORT grid level price has reached
        active_short_level = 0
        for lvl in range(1, self.grid_levels + 1):
            threshold = sma_now + lvl * grid_spacing
            if close_now >= threshold:
                active_short_level = lvl

        # ── Signal selection ───────────────────────────────────────────
        direction: Direction | None = None
        grid_level_hit: int = 0

        if active_long_level > 0 and rsi_now < 40.0:
            direction = Direction.LONG
            grid_level_hit = active_long_level
        elif active_short_level > 0 and rsi_now > 60.0:
            direction = Direction.SHORT
            grid_level_hit = active_short_level

        if direction is None:
            return None

        # ── Risk levels ────────────────────────────────────────────────
        entry_price = close_now
        atr_stop = atr_now * self.atr_stop_mult

        if direction == Direction.LONG:
            stop_loss = entry_price - atr_stop
            risk = entry_price - stop_loss
            take_profit = entry_price + risk * self.rr_ratio
        else:
            stop_loss = entry_price + atr_stop
            risk = stop_loss - entry_price
            take_profit = entry_price - risk * self.rr_ratio

        # Sanity: stop and TP must be positive and on the right side
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and (stop_loss >= entry_price or take_profit <= entry_price):
            return None
        if direction == Direction.SHORT and (stop_loss <= entry_price or take_profit >= entry_price):
            return None

        # ── Conviction scoring ─────────────────────────────────────────
        conviction = self._score_conviction(
            direction=direction,
            grid_level_hit=grid_level_hit,
            rsi_now=rsi_now,
            adx_now=adx_now,
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
                "sma": round(sma_now, 8),
                "atr": round(atr_now, 8),
                "grid_spacing": round(grid_spacing, 8),
                "grid_level_hit": grid_level_hit,
                "grid_levels": self.grid_levels,
                "rsi": round(rsi_now, 2),
                "adx": round(adx_now, 2),
                "volume_ratio": round(vol_now / avg_vol, 2),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when ANY of:
          1. Price crosses back through the SMA (mean-reversion target reached).
          2. ADX spikes above adx_max — market has started trending (thesis dead).
          3. RSI crosses neutral (50) in the direction of the trade (momentum exhausted).
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close_now = df["close"].iloc[-1]

        # Trigger 1: price returned to / through SMA
        sma_series = sma(df["close"], self.sma_period)
        sma_now = sma_series.iloc[-1]
        if not pd.isna(sma_now):
            if position.side == Direction.LONG and close_now >= sma_now:
                return True
            if position.side == Direction.SHORT and close_now <= sma_now:
                return True

        # Trigger 2: ADX spike — market started trending against choppy thesis
        adx_df = adx(df, self.adx_period)
        adx_now = adx_df["adx"].iloc[-1]
        if not pd.isna(adx_now) and adx_now >= self.adx_max * 1.2:
            return True

        # Trigger 3: RSI neutral cross — momentum used up
        rsi_series = rsi(df["close"], self.rsi_period)
        rsi_now = rsi_series.iloc[-1]
        if not pd.isna(rsi_now):
            if position.side == Direction.LONG and rsi_now >= 55.0:
                return True
            if position.side == Direction.SHORT and rsi_now <= 45.0:
                return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        grid_level_hit: int,
        rsi_now: float,
        adx_now: float,
    ) -> float:
        """
        Conviction scales with:
          - Grid level depth: deeper = higher conviction (0.30 per level, max 0.60)
          - RSI extremity: further from 50 = stronger mean-reversion pull (+0.20 max)
          - ADX quietness: lower ADX = choppier = better grid environment (+0.20 max)
        """
        # Grid depth contribution: level 1 = 0.30, level 2 = 0.45, level 3 = 0.60
        level_fraction = grid_level_hit / self.grid_levels  # 0.33 → 0.67 → 1.0
        grid_score = 0.30 + (level_fraction * 0.30)  # [0.30, 0.60]

        # RSI extremity: how far from 50 (neutral) — normalised to [0, 0.20]
        rsi_distance = abs(rsi_now - 50.0)  # 0–50 range
        rsi_score = min(rsi_distance / 50.0, 1.0) * 0.20

        # ADX quietness: lower ADX = more range-bound = better for this strategy
        # adx_now is already < adx_max (25) at this point
        adx_score = max(0.0, 1.0 - (adx_now / self.adx_max)) * 0.20

        raw = grid_score + rsi_score + adx_score  # [0.30, 1.0]
        signed = raw if direction == Direction.LONG else -raw
        return self._clamp(signed)
