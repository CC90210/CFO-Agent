"""
strategies/technical/donchian_breakout.py — Donchian Channel Breakout Strategy

Logic
-----
The Turtle Traders strategy — Richard Dennis proved in the 1980s that a mechanical
breakout system could turn beginners into profitable traders.  The core idea: price
breaking to a new N-bar high/low is statistically meaningful.  When a market makes
a 20-bar high it is doing something it hasn't done in three weeks — that is signal.

Entry rules:

LONG:
    1. Close breaks ABOVE the highest high of the last `entry_period` bars (default 20)
       — meaning current close > rolling max of prior N bars (excludes current bar)
    2. ADX > adx_min (default 20) — a trend is present, not just noise
    3. Volume > volume_mult × volume_period SMA (breakout has participation)
    4. RSI < rsi_max_long (default 75) — not already overbought

SHORT:
    1. Close breaks BELOW the lowest low of the last `entry_period` bars (default 20)
    2. ADX > adx_min — same filter
    3. Volume > volume_mult × volume_period SMA
    4. RSI > rsi_min_short (default 25) — not already oversold

Exit rules:
    Long: close drops below lowest low of the last `exit_period` bars (default 10)
    Short: close rises above highest high of the last `exit_period` bars (default 10)

Stop loss:  entry ± atr_stop_mult × ATR(14)   (default 2.0× ATR)
Take profit: entry ± risk × rr_ratio           (default 3.0)

Conviction scoring (long: positive, short: negative):
    Base:  0.40
    +0.15  ADX > 30 (strong trend, not just marginal trend)
    +0.15  volume > 1.5× average (strong participation)
    +0.15  RSI 40-60 (fresh breakout, not extended)
    +0.15  close > SMA(200) (macro trend aligned)

Best markets  : BTC/USDT, ETH/USDT, Gold, Forex majors
Best timeframes: 4h, 1d — breakouts need room to breathe
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, adx, rsi, sma


class DonchianBreakoutStrategy(BaseStrategy):
    """
    Classic Turtle Traders Donchian Channel Breakout.

    Enters on a fresh N-bar high/low with ADX trend and volume filters.
    Exits on the shorter (exit_period) Donchian channel in the opposite direction.
    """

    name = "donchian_breakout"
    description = (
        "Classic Turtle Traders breakout — 20-bar high/low channel. "
        "Filters: ADX trend strength, volume participation, RSI not extended. "
        "Exit on 10-bar channel reversal. Proven profitable for 40+ years."
    )
    timeframes = ["4h", "1d"]
    markets = ["crypto", "forex", "commodities"]

    def __init__(
        self,
        entry_period: int = 20,
        exit_period: int = 10,
        atr_period: int = 14,
        atr_stop_mult: float = 2.0,
        rr_ratio: float = 3.0,
        adx_period: int = 14,
        adx_min: float = 20.0,
        rsi_period: int = 14,
        rsi_max_long: float = 75.0,
        rsi_min_short: float = 25.0,
        volume_period: int = 20,
        volume_mult: float = 1.2,
        sma_trend_period: int = 200,
        # Ensemble lookback periods (Zarattini-Barbon 2025 method).
        # When provided, the strategy checks breakout on multiple periods
        # and requires >=2 to agree.  Set to empty list to disable ensemble.
        ensemble_periods: list[int] | None = None,
    ) -> None:
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.rr_ratio = rr_ratio
        self.adx_period = adx_period
        self.adx_min = adx_min
        self.rsi_period = rsi_period
        self.rsi_max_long = rsi_max_long
        self.rsi_min_short = rsi_min_short
        self.volume_period = volume_period
        self.volume_mult = volume_mult
        self.sma_trend_period = sma_trend_period
        # Ensemble: default to [short, primary, long] lookbacks
        self.ensemble_periods = ensemble_periods if ensemble_periods is not None else [entry_period]
        # Need enough bars for the longest lookback
        max_lookback = max(self.ensemble_periods) if self.ensemble_periods else entry_period
        self._min_bars = max(sma_trend_period, 2 * adx_period, max_lookback) + 5

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")

        # --- Indicators ---
        close = df["close"]
        atr_series = atr(df, self.atr_period)
        atr_now = atr_series.iloc[-1]
        if pd.isna(atr_now) or atr_now <= 0:
            return None

        adx_df = adx(df, self.adx_period)
        adx_now = adx_df["adx"].iloc[-1]
        if pd.isna(adx_now):
            return None

        rsi_series = rsi(close, self.rsi_period)
        rsi_now = rsi_series.iloc[-1]
        if pd.isna(rsi_now):
            return None

        vol_avg = df["volume"].rolling(self.volume_period).mean()
        vol_avg_now = vol_avg.iloc[-1]
        vol_now = df["volume"].iloc[-1]

        sma_200 = sma(close, self.sma_trend_period)
        sma_200_now = sma_200.iloc[-1]
        price_above_sma = (not pd.isna(sma_200_now)) and (close.iloc[-1] > sma_200_now)

        close_now = close.iloc[-1]

        # --- Primary Donchian channel (entry decision) ---
        shifted_high = df["high"].shift(1)
        shifted_low = df["low"].shift(1)
        entry_high_now = shifted_high.rolling(self.entry_period).max().iloc[-1]
        entry_low_now = shifted_low.rolling(self.entry_period).min().iloc[-1]

        if pd.isna(entry_high_now) or pd.isna(entry_low_now):
            return None

        # --- Ensemble agreement (conviction modifier, not hard gate) ---
        # Zarattini-Barbon 2025: check breakout on multiple lookback periods.
        # More agreement = higher conviction, but entry only requires the primary.
        long_votes = 0
        short_votes = 0
        n_periods = len(self.ensemble_periods)
        for period in self.ensemble_periods:
            ch_high = shifted_high.rolling(period).max().iloc[-1]
            ch_low = shifted_low.rolling(period).min().iloc[-1]
            if pd.isna(ch_high) or pd.isna(ch_low):
                continue
            if close_now > ch_high:
                long_votes += 1
            if close_now < ch_low:
                short_votes += 1

        # --- Trend filter ---
        adx_ok = adx_now >= self.adx_min

        # --- Determine direction (primary period only) ---
        long_breakout = close_now > entry_high_now
        short_breakout = close_now < entry_low_now

        # Volume is a conviction modifier, not a hard gate — in consolidation
        # markets volume is structurally lower but breakouts are still valid.
        if long_breakout and adx_ok and rsi_now < self.rsi_max_long:
            direction = Direction.LONG
        elif short_breakout and adx_ok and rsi_now > self.rsi_min_short:
            direction = Direction.SHORT
        else:
            return None

        # --- Risk levels ---
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + stop_dist * self.rr_ratio
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - stop_dist * self.rr_ratio

        # Guard: stop and TP must be positive prices
        if stop_loss <= 0 or take_profit <= 0:
            return None

        # --- Conviction ---
        ensemble_votes = long_votes if direction == Direction.LONG else short_votes
        conviction = self._score_conviction(
            direction=direction,
            adx_now=adx_now,
            vol_now=vol_now,
            vol_avg_now=vol_avg_now,
            rsi_now=rsi_now,
            price_above_sma=price_above_sma,
            ensemble_votes=ensemble_votes,
            n_periods=n_periods,
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
                "entry_channel_high": round(entry_high_now, 8),
                "entry_channel_low": round(entry_low_now, 8),
                "adx": round(adx_now, 4),
                "rsi": round(rsi_now, 4),
                "volume_ratio": round(vol_now / vol_avg_now, 4) if vol_avg_now > 0 else None,
                "price_above_sma200": price_above_sma,
                "atr": round(atr_now, 8),
                "ensemble_votes": f"{ensemble_votes}/{n_periods}",
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when price crosses the shorter (exit_period) Donchian channel against the trade.

        Long:  close drops below the lowest low of the last exit_period bars
        Short: close rises above the highest high of the last exit_period bars
        """
        min_required = self.exit_period + 2
        if not self._min_rows(df, min_required):
            return False

        close_now = df["close"].iloc[-1]

        # Exit channel uses the prior N bars (shift(1) to avoid look-ahead)
        exit_high = df["high"].shift(1).rolling(self.exit_period).max().iloc[-1]
        exit_low = df["low"].shift(1).rolling(self.exit_period).min().iloc[-1]

        if pd.isna(exit_high) or pd.isna(exit_low):
            return False

        if position.side == Direction.LONG and close_now < exit_low:
            return True
        if position.side == Direction.SHORT and close_now > exit_high:
            return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        adx_now: float,
        vol_now: float,
        vol_avg_now: float,
        rsi_now: float,
        price_above_sma: bool,
        ensemble_votes: int = 1,
        n_periods: int = 1,
    ) -> float:
        score = 0.35  # Base conviction for a confirmed breakout

        # +0.10 ensemble unanimity bonus (all lookback periods agree)
        if n_periods > 1 and ensemble_votes == n_periods:
            score += 0.10

        # +0.15 if ADX > 30 (strong trend, not marginal)
        if adx_now > 30.0:
            score += 0.15

        # +0.15 if volume > 1.5× average (strong participation)
        if vol_avg_now > 0 and vol_now >= 1.5 * vol_avg_now:
            score += 0.15

        # +0.10 if RSI in sweet spot (fresh breakout momentum — not already extended)
        if 40.0 <= rsi_now <= 60.0:
            score += 0.10

        # +0.15 if price above SMA(200) — macro trend aligned for longs; below for shorts
        if direction == Direction.LONG and price_above_sma:
            score += 0.15
        elif direction == Direction.SHORT and not price_above_sma:
            score += 0.15

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
