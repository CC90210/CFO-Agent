"""
strategies/technical/pairs_mean_reversion.py — Pairs / Statistical Arbitrage Strategy

Logic
-----
A market-neutral mean reversion strategy that fades statistically extreme deviations of
price from its rolling mean.  The concept borrows from classical pairs trading: when the
spread (here: price relative to its own rolling distribution) is stretched beyond ±2
standard deviations, the probability of reversion is high enough to justify a trade.

The strategy is market-neutral by design — it performs in BULL, BEAR, and CHOPPY regimes
because it bets purely on the *statistical* return to the mean, not on directional bias.
ADX < 30 gate further ensures we only trade when the market is ranging, not trending away.

LONG signal conditions (all required):
    - Z-score(50) < -2.0        (price is 2+ std devs below rolling mean)
    - RSI(14) < 35              (oversold momentum confirmation)
    - ADX(14) < 30              (ranging/mean-reverting environment)
    - Price within 5% of Bollinger lower band (at statistical support)

SHORT signal conditions (mirror):
    - Z-score(50) > +2.0
    - RSI(14) > 65
    - ADX(14) < 30
    - Price within 5% of Bollinger upper band

Exit triggers (first to fire wins):
    - Z-score crosses back through 0 (reversion complete — primary target)
    - RSI crosses back through 50 (momentum normalised)
    - Price crosses back through the SMA (the rolling mean itself)

Stop loss  : 1.5x ATR(14) — tight: mean reversion is wrong fast or not at all
Take profit: 2.0x risk distance (2R target for efficient capital use)

Conviction scoring
------------------
    Base:   0.40  — baseline for passing all four entry gates
    +0.15   Z-score extreme (|z| > 2.5 — higher probability of sharp reversion)
    +0.15   RSI extreme (< 25 long / > 75 short — capitulation/euphoria)
    +0.15   ADX < 20 (deeply ranging — strongest environment for mean reversion)
    +0.15   Volume elevated (capitulation spike or euphoria buying/selling)

Best markets  : Crypto (24/7, frequent chop phases)
Best timeframes: 1h, 4h
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, adx, bollinger_bands, rsi, sma


# ---------------------------------------------------------------------------
# Module-private helpers
# ---------------------------------------------------------------------------


def _rolling_zscore(series: pd.Series, period: int) -> pd.Series:
    """
    Rolling Z-score: (price - rolling_mean) / rolling_std.

    NaN for the first period - 1 rows.  Zero-std windows return 0.0 to avoid
    division-by-zero (flat price series have no edge — correctly scored neutral).
    """
    rolling_mean = series.rolling(window=period).mean()
    rolling_std = series.rolling(window=period).std(ddof=0)
    safe_std = rolling_std.replace(0.0, np.nan)
    return ((series - rolling_mean) / safe_std).fillna(0.0)


# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class PairsMeanReversionStrategy(BaseStrategy):
    """
    Pairs / Statistical Arbitrage mean reversion strategy.

    Fades price deviations beyond ±2 standard deviations from the rolling mean,
    using RSI, ADX, and Bollinger Band proximity as confirming filters.
    Market-neutral: no directional bias required — works in any regime.
    """

    name = "pairs_mean_reversion"
    description = (
        "Statistical arbitrage — fades z-score extremes with BB/RSI confirmation. "
        "Market-neutral in chop. Tight 1.5x ATR stop, 2R take profit."
    )
    timeframes = ["1h", "4h"]
    markets = ["crypto"]

    def __init__(
        self,
        zscore_period: int = 50,
        zscore_entry: float = 2.0,
        zscore_extreme: float = 2.5,
        zscore_exit: float = 0.0,
        rsi_period: int = 14,
        rsi_oversold: float = 35.0,
        rsi_overbought: float = 65.0,
        rsi_extreme_low: float = 25.0,
        rsi_extreme_high: float = 75.0,
        rsi_exit: float = 50.0,
        bb_period: int = 20,
        bb_std: float = 2.0,
        bb_touch_pct: float = 0.05,
        sma_period: int = 50,
        adx_period: int = 14,
        adx_max: float = 30.0,
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,
        rr_ratio: float = 2.0,
        volume_period: int = 20,
        volume_mult: float = 1.2,
    ) -> None:
        self.zscore_period = zscore_period
        self.zscore_entry = zscore_entry
        self.zscore_extreme = zscore_extreme
        self.zscore_exit = zscore_exit
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi_extreme_low = rsi_extreme_low
        self.rsi_extreme_high = rsi_extreme_high
        self.rsi_exit = rsi_exit
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.bb_touch_pct = bb_touch_pct
        self.sma_period = sma_period
        self.adx_period = adx_period
        self.adx_max = adx_max
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.volume_period = volume_period
        self.volume_mult = volume_mult

        # Minimum bars before any indicator is reliable.
        # adx() internally requires 2 * period; we honour that.
        self._min_bars = (
            max(zscore_period, adx_period * 2, rsi_period, atr_period, bb_period) + 5
        )

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full pairs mean reversion analysis and return a Signal or None.

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
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        sma_series = sma(close, self.sma_period)

        zscore_now = float(zscore_series.iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])
        adx_now = float(adx_df["adx"].iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        close_now = float(close.iloc[-1])
        sma_now = float(sma_series.iloc[-1])
        bb_upper_now = float(bb.upper.iloc[-1])
        bb_lower_now = float(bb.lower.iloc[-1])

        vol_now = float(df["volume"].iloc[-1])
        avg_vol = float(df["volume"].rolling(self.volume_period).mean().iloc[-1])
        vol_ratio = vol_now / avg_vol if avg_vol > 0 else 1.0

        # Gate: ADX must indicate a ranging (non-trending) market
        if pd.isna(adx_now) or adx_now >= self.adx_max:
            return None

        # Gate: Z-score must breach the entry threshold
        if abs(zscore_now) < self.zscore_entry:
            return None

        # Gate: NaN guards on critical indicators
        if pd.isna(rsi_now) or pd.isna(atr_now) or atr_now <= 0:
            return None
        if pd.isna(sma_now) or pd.isna(bb_upper_now) or pd.isna(bb_lower_now):
            return None

        # --- Determine direction ---
        direction: Direction | None = None

        if zscore_now < -self.zscore_entry and rsi_now < self.rsi_oversold:
            # Price stretched below mean AND oversold — check BB proximity
            bb_touch_threshold = bb_lower_now * (1.0 + self.bb_touch_pct)
            if close_now <= bb_touch_threshold:
                direction = Direction.LONG

        elif zscore_now > self.zscore_entry and rsi_now > self.rsi_overbought:
            # Price stretched above mean AND overbought — check BB proximity
            bb_touch_threshold = bb_upper_now * (1.0 - self.bb_touch_pct)
            if close_now >= bb_touch_threshold:
                direction = Direction.SHORT

        if direction is None:
            return None

        # --- Price levels ---
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now
        take_dist = stop_dist * self.rr_ratio

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + take_dist
            # Primary target is mean reversion to SMA; use whichever comes first
            # but ensure TP is above entry (use max to stay conservative)
            if sma_now > entry_price:
                # SMA is above — reversion target is valid; cap at 2R if SMA is very far
                take_profit = min(sma_now, take_profit)
                # If SMA is closer than 2R, still enforce minimum 2R
                take_profit = max(take_profit, entry_price + take_dist)
        else:  # SHORT
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - take_dist
            # SMA below entry is the reversion target
            if sma_now < entry_price:
                take_profit = max(sma_now, take_profit)
                take_profit = min(take_profit, entry_price - take_dist)

        # Final sanity checks — SL and TP must be on the correct side of entry
        if direction == Direction.LONG and (stop_loss >= entry_price or take_profit <= entry_price):
            return None
        if direction == Direction.SHORT and (stop_loss <= entry_price or take_profit >= entry_price):
            return None

        conviction = self._score_conviction(
            zscore_now=zscore_now,
            rsi_now=rsi_now,
            adx_now=adx_now,
            vol_ratio=vol_ratio,
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
                "rolling_mean": round(sma_now, 8),
                "rsi": round(rsi_now, 2),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 8),
                "bb_upper": round(bb_upper_now, 8),
                "bb_lower": round(bb_lower_now, 8),
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
          1. Z-score crosses back through zero (mean reversion complete).
          2. RSI crosses back through 50 (momentum normalised).
          3. Price crosses back through the SMA (rolling mean).
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        zscore_series = _rolling_zscore(close, self.zscore_period)
        rsi_series = rsi(close, self.rsi_period)
        sma_series = sma(close, self.sma_period)

        zscore_now = float(zscore_series.iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])
        close_now = float(close.iloc[-1])
        sma_now = float(sma_series.iloc[-1])

        if pd.isna(zscore_now) or pd.isna(rsi_now) or pd.isna(sma_now):
            return False

        if position.side == Direction.LONG:
            # Condition 1: Z-score returned to zero or above
            zscore_exit = zscore_now >= self.zscore_exit
            # Condition 2: RSI mean-reversion complete
            rsi_exit = rsi_now >= self.rsi_exit
            # Condition 3: Price crossed back above the SMA
            sma_exit = close_now >= sma_now
            return zscore_exit or rsi_exit or sma_exit

        else:  # SHORT
            # Condition 1: Z-score returned to zero or below
            zscore_exit = zscore_now <= self.zscore_exit
            # Condition 2: RSI mean-reversion complete
            rsi_exit = rsi_now <= self.rsi_exit
            # Condition 3: Price crossed back below the SMA
            sma_exit = close_now <= sma_now
            return zscore_exit or rsi_exit or sma_exit

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        zscore_now: float,
        rsi_now: float,
        adx_now: float,
        vol_ratio: float,
        direction: Direction,
    ) -> float:
        """
        Additive conviction score in [0, 1], then signed to [-1, 1].

        Component weights:
            0.40  Base — reward for passing all four entry gates
            0.15  Z-score extreme (|z| > zscore_extreme — sharp reversion expected)
            0.15  RSI extreme (< rsi_extreme_low or > rsi_extreme_high)
            0.15  ADX deeply ranging (< 20 — strongest mean-reversion environment)
            0.15  Volume elevated above average (capitulation or euphoria spike)
        """
        score = 0.40  # base conviction for clearing all gates

        # --- Z-score extremity bonus ---
        if abs(zscore_now) >= self.zscore_extreme:
            score += 0.15

        # --- RSI extremity bonus ---
        if direction == Direction.LONG and rsi_now < self.rsi_extreme_low:
            score += 0.15
        elif direction == Direction.SHORT and rsi_now > self.rsi_extreme_high:
            score += 0.15

        # --- ADX deeply ranging bonus ---
        if adx_now < 20.0:
            score += 0.15

        # --- Volume elevation bonus ---
        if vol_ratio >= self.volume_mult:
            score += 0.15

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
