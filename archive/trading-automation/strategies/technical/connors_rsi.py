"""
strategies/technical/connors_rsi.py — Connors RSI-2 Cumulative Mean Reversion

The most backtested mean reversion system in existence.  Developed by Larry Connors
and Cesar Alvarez.  Historically delivers ~83% win rate and ~26% CAGR on SPY (daily bars).
Trades short, sharp reversions: buy extreme oversold dips in bull regimes; sell extreme
overbought rallies in bear regimes.  The edge is the 2-period RSI, which becomes so
sensitive that single-digit readings are genuinely rare and reliably snap back.

Strategy logic
--------------
LONG entry — all required:
    1. Close > SMA(200)                   — macro uptrend filter (never buy in bear market)
    2. RSI(2) < rsi_entry_long (10)       — extreme short-term oversold
       OR cumulative RSI(2) over last
       cumulative_bars < cumulative_threshold (35) — more trades via cumulation
    3. Conviction bonuses applied         — see _score_conviction()

SHORT entry — mirror:
    1. Close < SMA(200)                   — macro downtrend
    2. RSI(2) > rsi_entry_short (90)      — extreme short-term overbought
       OR cumulative RSI(2) over last 2 bars > (200 - cumulative_threshold)

Exit rules (Connors canonical):
    LONG  → Close > yesterday's High     (profit target hit — exit into strength)
    SHORT → Close < yesterday's Low      (profit target hit — exit into weakness)
    Fallback stop: 1.5x ATR(14) below/above entry (capital preservation gate)

Conviction scoring (base 0.50, max ±1.0):
    +0.15  RSI(2) < 5 / > 95              — extreme reading (very rare, very reliable)
    +0.10  Price near lower/upper BB(20)  — Bollinger confirmation
    +0.10  Cumulative RSI < 20 / > 180    — multi-bar exhaustion
    +0.10  Volume > 1.2x average          — institutional participation
    +0.05  Close > SMA(50) for longs /
           Close < SMA(50) for shorts    — intermediate trend alignment

Best markets    : SPY, QQQ, AAPL, MSFT, NVDA, AMZN, META, GOOG — liquid large-caps
Best timeframes : 1d (daily bars — this is a daily swing strategy by design)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import (
    rsi,
    sma,
    bollinger_bands,
    atr,
)


class ConnorsRSIStrategy(BaseStrategy):
    """
    Connors RSI-2 Cumulative Mean Reversion for US equities.

    Entry on extreme short-term RSI readings (RSI(2) < 10 or > 90) filtered by
    the 200 SMA macro trend.  Exits when price closes above yesterday's high
    (longs) or below yesterday's low (shorts).  Tight ATR stop as a backstop.
    """

    name = "connors_rsi"
    description = (
        "Connors RSI-2 mean reversion: RSI(2) < 10 above SMA(200) for longs, "
        "RSI(2) > 90 below SMA(200) for shorts.  Exit when close exceeds "
        "yesterday's high/low (Connors canonical exit).  Cumulative RSI variant "
        "included for higher trade frequency."
    )
    timeframes = ["1d"]
    markets = ["equities"]

    def __init__(
        self,
        rsi_period: int = 2,                   # the key — very short period RSI
        rsi_entry_long: float = 10.0,          # RSI(2) below this = extreme oversold
        rsi_entry_short: float = 90.0,         # RSI(2) above this = extreme overbought
        sma_trend_period: int = 200,           # macro trend filter
        sma_mid_period: int = 50,              # intermediate trend (conviction bonus)
        cumulative_bars: int = 2,              # number of bars to sum RSI for cumulation
        cumulative_threshold: float = 35.0,   # sum of last N RSI(2) values < this → long
        bb_period: int = 20,
        bb_std: float = 2.0,
        volume_period: int = 20,
        volume_mult: float = 1.2,
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,           # tight — mean reversion snaps back fast
        rr_ratio: float = 2.0,                # used only when ATR fallback TP is needed
    ) -> None:
        self.rsi_period = rsi_period
        self.rsi_entry_long = rsi_entry_long
        self.rsi_entry_short = rsi_entry_short
        self.sma_trend_period = sma_trend_period
        self.sma_mid_period = sma_mid_period
        self.cumulative_bars = cumulative_bars
        self.cumulative_threshold = cumulative_threshold
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio

        # 200 SMA is the binding constraint; add a small buffer for convergence.
        self._min_bars = sma_trend_period + cumulative_bars + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run Connors RSI-2 analysis and return a Signal, or None when no edge.

        Requires at least sma_trend_period + cumulative_bars + 5 rows.
        Returns None — never raises — when data is insufficient or no signal fires.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        high = df["high"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # --- Indicators ---
        rsi_series = rsi(close, self.rsi_period)
        sma_200 = sma(close, self.sma_trend_period)
        sma_50 = sma(close, self.sma_mid_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # --- Current-bar scalars ---
        rsi_now = float(rsi_series.iloc[-1])
        close_now = float(close.iloc[-1])
        sma_200_now = float(sma_200.iloc[-1])
        sma_50_now = float(sma_50.iloc[-1])
        bb_lower = float(bb.lower.iloc[-1])
        bb_upper = float(bb.upper.iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        vol_now = float(df["volume"].iloc[-1])
        avg_vol_now = float(avg_vol.iloc[-1])

        # Yesterday's high is used for the Connors exit target (metadata only here;
        # the actual exit check lives in should_exit).
        prev_high = float(high.iloc[-2]) if len(high) >= 2 else close_now

        # Guard NaN — indicators return NaN for early bars even past _min_bars.
        if any(
            pd.isna(v)
            for v in (rsi_now, sma_200_now, sma_50_now, bb_lower, bb_upper, atr_now, avg_vol_now)
        ):
            return None

        if atr_now <= 0 or avg_vol_now <= 0:
            return None

        vol_ratio = vol_now / avg_vol_now

        # --- Cumulative RSI: sum of the last cumulative_bars RSI(2) values ---
        # This is the Connors "cumulative" variant that generates more trades.
        rsi_window = rsi_series.iloc[-self.cumulative_bars :]
        if len(rsi_window) < self.cumulative_bars or rsi_window.isna().any():
            cum_rsi = rsi_now  # fallback: treat single bar as the sum
        else:
            cum_rsi = float(rsi_window.sum())

        # --- Gate 1: 200 SMA macro filter ---
        # LONG only above 200 SMA; SHORT only below.  Non-negotiable — this is the
        # single most important filter in the Connors system.
        above_200 = close_now > sma_200_now
        below_200 = close_now < sma_200_now

        # --- Gate 2: RSI(2) or cumulative RSI trigger ---
        # Either the raw RSI(2) or the cumulative sum must breach the threshold.
        cum_short_threshold = 200.0 - self.cumulative_threshold  # mirror for shorts

        rsi_long_trigger = rsi_now < self.rsi_entry_long
        rsi_short_trigger = rsi_now > self.rsi_entry_short
        cum_long_trigger = cum_rsi < self.cumulative_threshold
        cum_short_trigger = cum_rsi > cum_short_threshold

        # --- Direction determination ---
        direction: Direction | None = None

        if above_200 and (rsi_long_trigger or cum_long_trigger):
            direction = Direction.LONG
        elif below_200 and (rsi_short_trigger or cum_short_trigger):
            direction = Direction.SHORT

        if direction is None:
            return None

        # --- Price levels ---
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            # Primary target: yesterday's high (Connors canonical).
            # When that is not above entry (e.g. gap-down day), fall back to ATR-based TP.
            take_profit = max(prev_high, entry_price + stop_dist * self.rr_ratio)
        else:
            stop_loss = entry_price + stop_dist
            prev_low = float(df["low"].iloc[-2]) if len(df) >= 2 else close_now
            take_profit = min(prev_low, entry_price - stop_dist * self.rr_ratio)

        # Hard safety checks
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        conviction = self._score_conviction(
            rsi_now=rsi_now,
            cum_rsi=cum_rsi,
            close_now=close_now,
            sma_50_now=sma_50_now,
            bb_lower=bb_lower,
            bb_upper=bb_upper,
            vol_ratio=vol_ratio,
            direction=direction,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 4),
            take_profit=round(take_profit, 4),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "rsi_2": round(rsi_now, 2),
                "cum_rsi": round(cum_rsi, 2),
                "sma_200": round(sma_200_now, 4),
                "sma_50": round(sma_50_now, 4),
                "bb_lower": round(bb_lower, 4),
                "bb_upper": round(bb_upper, 4),
                "atr": round(atr_now, 4),
                "volume_ratio": round(vol_ratio, 2),
                "prev_high": round(prev_high, 4),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — delegates to analyze()."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Connors canonical exit rules:
            LONG  → current close > yesterday's high
            SHORT → current close < yesterday's low

        A fallback ATR trailing stop triggers if the primary exit has not fired
        after multiple bars, preventing a winning trade from becoming a full loser.
        """
        if not self._min_rows(df, self.atr_period + 2):
            return False

        close = df["close"]
        high = df["high"]
        low = df["low"]

        if len(df) < 2:
            return False

        close_now = float(close.iloc[-1])
        prev_high = float(high.iloc[-2])
        prev_low = float(low.iloc[-2])

        if position.side == Direction.LONG:
            # Primary Connors exit: close above yesterday's high
            if close_now > prev_high:
                return True
            # Fallback: ATR trailing stop — tracks highest close since entry
            atr_series = atr(df, self.atr_period)
            atr_now = float(atr_series.iloc[-1])
            if pd.isna(atr_now) or atr_now <= 0:
                return False
            trail_high = position.metadata.get("trail_high", position.entry_price)
            trail_high = max(trail_high, close_now)
            position.metadata["trail_high"] = trail_high
            trail_stop = trail_high - self.atr_stop_mult * atr_now
            return close_now <= trail_stop

        else:  # SHORT
            # Primary Connors exit: close below yesterday's low
            if close_now < prev_low:
                return True
            # Fallback: ATR trailing stop — tracks lowest close since entry
            atr_series = atr(df, self.atr_period)
            atr_now = float(atr_series.iloc[-1])
            if pd.isna(atr_now) or atr_now <= 0:
                return False
            trail_low = position.metadata.get("trail_low", position.entry_price)
            trail_low = min(trail_low, close_now)
            position.metadata["trail_low"] = trail_low
            trail_stop = trail_low + self.atr_stop_mult * atr_now
            return close_now >= trail_stop

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        rsi_now: float,
        cum_rsi: float,
        close_now: float,
        sma_50_now: float,
        bb_lower: float,
        bb_upper: float,
        vol_ratio: float,
        direction: Direction,
    ) -> float:
        """
        Build conviction score from base 0.50 with additive bonuses.

        Bonuses:
            +0.15  RSI(2) < 5 (long) or > 95 (short)    — extreme reading
            +0.10  Price near Bollinger Band extreme      — volatility confirmation
            +0.10  Cumulative RSI < 20 or > 180           — multi-bar exhaustion
            +0.10  Volume > 1.2x average                  — institutional participation
            +0.05  Close > SMA(50) for longs /
                   Close < SMA(50) for shorts            — intermediate trend aligned

        Score is clamped to [-1.0, 1.0] and signed: positive for LONG, negative for SHORT.
        """
        score = 0.50

        # Bonus 1: extreme RSI(2) reading
        if direction == Direction.LONG and rsi_now < 5.0:
            score += 0.15
        elif direction == Direction.SHORT and rsi_now > 95.0:
            score += 0.15

        # Bonus 2: price near Bollinger Band
        # For longs: close at or below the lower band.
        # For shorts: close at or above the upper band.
        if direction == Direction.LONG and close_now <= bb_lower:
            score += 0.10
        elif direction == Direction.SHORT and close_now >= bb_upper:
            score += 0.10

        # Bonus 3: multi-bar cumulative RSI exhaustion
        # Long: sum of 2 RSI(2) values < 20 (each bar averaging < 10).
        # Short: mirror — sum > 180 (each bar averaging > 90).
        cum_long_extreme = self.cumulative_threshold * (20.0 / 35.0)   # ~20
        cum_short_extreme = 200.0 - cum_long_extreme                    # ~180
        if direction == Direction.LONG and cum_rsi < cum_long_extreme:
            score += 0.10
        elif direction == Direction.SHORT and cum_rsi > cum_short_extreme:
            score += 0.10

        # Bonus 4: volume spike — confirms institutional participation
        if vol_ratio >= self.volume_mult:
            score += 0.10

        # Bonus 5: intermediate trend alignment via SMA(50)
        if direction == Direction.LONG and close_now > sma_50_now:
            score += 0.05
        elif direction == Direction.SHORT and close_now < sma_50_now:
            score += 0.05

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
