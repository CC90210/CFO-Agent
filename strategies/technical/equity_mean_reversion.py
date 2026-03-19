"""
strategies/technical/equity_mean_reversion.py — Equity RSI Mean Reversion with Bollinger Bands

Designed for liquid US equities (SPY, QQQ, AAPL, NVDA, etc.) via the Alpaca broker.

Strategy overview
-----------------
Buys oversold dips and shorts overbought rallies ONLY when the macro trend agrees.
The key insight vs. the crypto RSI strategy: US stocks trend more reliably, so we
require ADX > 20 (confirmed trend) rather than ADX < 25 (range-bound). We are fading
the PULLBACK within the prevailing trend, not fading a directionless chop.

LONG signal — all five conditions required:
    1. RSI(14) < 30             — oversold
    2. Close <= lower BB(20, 2) — price at or beyond statistical lower extreme
    3. ADX(14) > 20             — a genuine trend exists (we are buying a dip, not catching a knife)
    4. Volume >= 1.2x 20-bar avg — institutional participation on this bar
    5. Close > SMA(200)         — macro uptrend filter; only fade dips in bull regimes

SHORT signal — mirror image:
    1. RSI(14) > 70
    2. Close >= upper BB(20, 2)
    3. ADX(14) > 20
    4. Volume >= 1.2x average
    5. Close < SMA(200)         — macro downtrend filter

Exit rules:
    - Stop loss:   1.5x ATR(14) from entry
    - Take profit: 3.0x ATR(14) from entry — enforces 2:1 R:R
    - Also exit early when RSI crosses back through 50 (mean reversion complete)

Conviction scoring (base 0.50, max ±1.0):
    +0.15  RSI extreme depth (< 25 long / > 75 short)
    +0.15  Price closed beyond BB by > 0.5 ATR
    +0.10  Volume > 2x average
    +0.10  Stochastic RSI confirms (k < 0.20 for long, k > 0.80 for short)

Best markets    : SPY, QQQ, AAPL, NVDA — liquid large-caps with clean trends
Best timeframes : 1h, 4h, 1d
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import (
    rsi,
    sma,
    bollinger_bands,
    atr,
    adx,
    stochastic_rsi,
)


class EquityMeanReversionStrategy(BaseStrategy):
    """
    RSI + Bollinger Band mean reversion for US equities.

    Fades oversold dips (LONG) and overbought rallies (SHORT) within confirmed
    trends, gated by the 200 SMA macro filter. Sized by 1.5/3.0 ATR stop/TP.
    """

    name = "equity_mean_reversion"
    description = (
        "RSI < 30 / > 70 with price at Bollinger extremes, ADX > 20 trend confirmation, "
        "200 SMA macro filter, and volume spike. Targets mean reversion to RSI 50. "
        "Designed for liquid US equities via Alpaca."
    )
    timeframes = ["1h", "4h", "1d"]
    markets = ["equities"]

    def __init__(
        self,
        rsi_period: int = 14,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        rsi_exit: float = 50.0,
        rsi_extreme_long: float = 25.0,   # threshold for +0.15 extreme conviction bonus
        rsi_extreme_short: float = 75.0,  # threshold for +0.15 extreme conviction bonus
        bb_period: int = 20,
        bb_std: float = 2.0,
        adx_period: int = 14,
        adx_min: float = 20.0,            # trend must be present (opposite of crypto RSI)
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,
        atr_tp_mult: float = 3.0,         # 3x ATR TP gives 2:1 R:R vs 1.5x stop
        volume_period: int = 20,
        volume_mult: float = 1.2,         # minimum volume confirmation threshold
        volume_high_mult: float = 2.0,    # threshold for +0.10 high-volume conviction bonus
        sma_trend_period: int = 200,      # 200 SMA macro filter
        stoch_rsi_period: int = 14,
        stoch_rsi_oversold: float = 0.20,  # in [0,1]; 0.20 = 20%
        stoch_rsi_overbought: float = 0.80,
        bb_extreme_atr_mult: float = 0.5,  # price must be > this many ATR beyond BB for bonus
    ) -> None:
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.rsi_exit = rsi_exit
        self.rsi_extreme_long = rsi_extreme_long
        self.rsi_extreme_short = rsi_extreme_short
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.adx_period = adx_period
        self.adx_min = adx_min
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.atr_tp_mult = atr_tp_mult
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.volume_high_mult = volume_high_mult
        self.sma_trend_period = sma_trend_period
        self.stoch_rsi_period = stoch_rsi_period
        self.stoch_rsi_oversold = stoch_rsi_oversold
        self.stoch_rsi_overbought = stoch_rsi_overbought
        self.bb_extreme_atr_mult = bb_extreme_atr_mult

        # The 200 SMA is the binding constraint on minimum bars.
        # Adding a 10-bar buffer ensures the SMA has converged beyond the cold-start
        # period where it would reflect too few observations.
        self._min_bars = sma_trend_period + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full analysis on OHLCV data and return a Signal, or None when
        conditions are not met.

        Requires a minimum of sma_trend_period + 10 rows (210 by default).
        Returns None — never raises — when data is insufficient.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        # --- Compute all indicators ---
        rsi_series = rsi(close, self.rsi_period)
        bb = bollinger_bands(close, self.bb_period, self.bb_std)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        sma_trend = sma(close, self.sma_trend_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()
        stoch = stochastic_rsi(close, rsi_period=self.stoch_rsi_period)

        # --- Extract current-bar values ---
        rsi_now = rsi_series.iloc[-1]
        close_now = close.iloc[-1]
        bb_upper = bb.upper.iloc[-1]
        bb_lower = bb.lower.iloc[-1]
        bb_pct = bb.percent_b.iloc[-1]  # 0 = at lower band, 1 = at upper band
        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        sma_now = sma_trend.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        stoch_k = stoch["stoch_rsi_k"].iloc[-1]

        # Guard against NaN values that can appear at the start of indicator series
        if any(
            pd.isna(v)
            for v in (rsi_now, bb_upper, bb_lower, adx_now, atr_now, sma_now, avg_vol_now)
        ):
            return None

        if atr_now <= 0 or avg_vol_now <= 0:
            return None

        vol_ratio = vol_now / avg_vol_now

        # --- Gate 1: ADX — a real trend must exist ---
        # Equity mean reversion works best fading pullbacks WITHIN trends.
        # ADX < adx_min means the market is too choppy to trust a directional fade.
        if adx_now < self.adx_min:
            return None

        # --- Gate 2: Volume confirmation ---
        if vol_ratio < self.volume_mult:
            return None

        # --- Determine direction ---
        direction: Direction | None = None

        if rsi_now < self.rsi_oversold and close_now <= bb_lower:
            # LONG: only fade dips in macro uptrend (price above 200 SMA)
            if close_now < sma_now:
                return None
            direction = Direction.LONG

        elif rsi_now > self.rsi_overbought and close_now >= bb_upper:
            # SHORT: only fade rallies in macro downtrend (price below 200 SMA)
            if close_now > sma_now:
                return None
            direction = Direction.SHORT

        if direction is None:
            return None

        # --- Build stop loss and take profit (absolute price levels) ---
        stop_dist = self.atr_stop_mult * atr_now   # 1.5 ATR
        tp_dist = self.atr_tp_mult * atr_now       # 3.0 ATR → 2:1 R:R

        entry_price = close_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + tp_dist
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - tp_dist

        # Hard safety: prices must be positive and directionally valid
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        # --- Conviction scoring ---
        conviction = self._score_conviction(
            rsi_val=rsi_now,
            close_now=close_now,
            bb_lower=bb_lower,
            bb_upper=bb_upper,
            atr_now=atr_now,
            vol_ratio=vol_ratio,
            stoch_k=stoch_k,
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
                "rsi": round(rsi_now, 2),
                "bb_upper": round(bb_upper, 4),
                "bb_lower": round(bb_lower, 4),
                "bb_pct_b": round(bb_pct, 4),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 4),
                "volume_ratio": round(vol_ratio, 2),
                "sma_200": round(sma_now, 4),
                "stoch_rsi_k": round(stoch_k, 4) if not pd.isna(stoch_k) else None,
                "stop_dist": round(stop_dist, 4),
                "tp_dist": round(tp_dist, 4),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — delegates to analyze()."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when RSI crosses back through 50 (mean reversion complete).

        The ATR-based stop_loss and take_profit on the position are monitored
        by the engine's order execution layer; this method handles the
        RSI-based early exit only.
        """
        if not self._min_rows(df, self.rsi_period + 5):
            return False

        close = df["close"]
        rsi_series = rsi(close, self.rsi_period)
        rsi_now = rsi_series.iloc[-1]

        if pd.isna(rsi_now):
            return False

        if position.side == Direction.LONG:
            # Mean reversion complete — RSI has returned to neutral territory
            return rsi_now >= self.rsi_exit
        else:
            return rsi_now <= self.rsi_exit

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        rsi_val: float,
        close_now: float,
        bb_lower: float,
        bb_upper: float,
        atr_now: float,
        vol_ratio: float,
        stoch_k: float,
        direction: Direction,
    ) -> float:
        """
        Build conviction score starting from a base of 0.50.

        Bonuses (each independent):
            +0.15  RSI is in extreme zone (< rsi_extreme_long or > rsi_extreme_short)
            +0.15  Price has closed beyond the BB by more than bb_extreme_atr_mult * ATR
            +0.10  Volume exceeds volume_high_mult * average (institutional accumulation)
            +0.10  Stochastic RSI confirms the oversold/overbought reading

        Score is clamped to [-1.0, 1.0] and signed: positive for LONG, negative for SHORT.
        """
        score = 0.50

        # Bonus 1: RSI extreme depth
        if direction == Direction.LONG and rsi_val < self.rsi_extreme_long:
            score += 0.15
        elif direction == Direction.SHORT and rsi_val > self.rsi_extreme_short:
            score += 0.15

        # Bonus 2: Price closed beyond BB by more than bb_extreme_atr_mult * ATR
        if direction == Direction.LONG:
            bb_overshoot = bb_lower - close_now  # positive when price is below lower band
        else:
            bb_overshoot = close_now - bb_upper  # positive when price is above upper band

        if bb_overshoot > self.bb_extreme_atr_mult * atr_now:
            score += 0.15

        # Bonus 3: High volume — signals institutional participation rather than thin-air move
        if vol_ratio >= self.volume_high_mult:
            score += 0.10

        # Bonus 4: Stochastic RSI confirmation (NaN safe)
        if not pd.isna(stoch_k):
            if direction == Direction.LONG and stoch_k < self.stoch_rsi_oversold:
                score += 0.10
            elif direction == Direction.SHORT and stoch_k > self.stoch_rsi_overbought:
                score += 0.10

        # Sign and clamp: LONG → positive, SHORT → negative
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
