"""
strategies/technical/tsmom.py — Time Series Momentum (TSMOM) Strategy

Based on Moskowitz, Ooi, Pedersen (2012) "Time Series Momentum".
Sharpe ratio 1.0–1.5 documented across all asset classes.

Logic
-----
An asset that has gone up over the past 1–12 months tends to continue going up.
Unlike cross-sectional momentum (ranking assets against each other), TSMOM uses only
the asset's own price history.  The key innovation is blending three lookback windows
(1-month, 3-month, 12-month) for robustness — no single window is relied upon.

Signal construction
~~~~~~~~~~~~~~~~~~~
1. Compute log-returns over three windows: short (1mo), mid (3mo), long (12mo).
2. Sign each return: +1 if positive, -1 if negative.
3. Blend: average the three signed returns.
   - Blended average > 0 → potential LONG
   - Blended average < 0 → potential SHORT
   - Mixed (some windows disagree) → reduced conviction, may still trade
4. Magnitude: |average return| across the three windows gives raw conviction.
5. Volatility scaling: realized volatility (ATR/close) modulates position size via
   the conviction score — higher volatility reduces conviction.

LONG entry conditions (all required):
    - Blended signal > 0 (at least 2 of 3 windows positive)
    - Close > EMA(50) — structural trend confirmation
    - ADX(14) > 15    — minimum directional trend strength (TSMOM needs trends)
    - ATR/close is NOT in the top 10th percentile of its own 50-bar distribution

SHORT entry conditions (mirror of above):
    - Blended signal < 0
    - Close < EMA(50)
    - ADX(14) > 15
    - Volatility not in top 10th percentile

Exit triggers (first to fire):
    - Stop loss: 2.5 × ATR(14) from entry
    - Take profit: 5.0 × ATR(14) from entry (2:1 minimum R:R enforced)
    - Signal reversal: blended signal flips to the opposing direction
    - Volatility spike: current ATR > 3× its 50-bar SMA → emergency exit

Conviction scoring (additive bonuses on top of base):
    Base: |average of 3 signed returns| normalised by realised volatility (capped at 0.5)
    +0.15  All 3 windows agree (unanimous signal — strongest quality filter)
    +0.10  ADX > 25 (confirmed strong trend)
    +0.10  Close > EMA(200) for LONG / close < EMA(200) for SHORT (macro trend aligned)
    +0.10  ATR/close below its 50-bar median (calmer markets trend more cleanly)
    Maximum raw score before clamping: 0.5 + 0.45 = 0.95

Lookback calibration per timeframe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Daily  bars: short=21,   mid=63,   long=252
    4h     bars: short=126,  mid=378,  long=756  (default — cap at 756 for data availability)
    1h     bars: short=504,  mid=1512, long=6048

Make these configurable via short_lookback / mid_lookback / long_lookback so the
Darwinian agent can optimise them.

Best markets    : crypto, commodities, equities, forex
Best timeframes : 4h, 1d
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, ema, sma


# ---------------------------------------------------------------------------
# Module-private helpers
# ---------------------------------------------------------------------------


def _log_return(close: pd.Series, lookback: int) -> float:
    """
    Compute the log-return over `lookback` bars ending at the most recent row.

    Returns 0.0 when there is insufficient data.
    """
    if len(close) < lookback + 1:
        return 0.0
    current = float(close.iloc[-1])
    past = float(close.iloc[-1 - lookback])
    if past <= 0 or current <= 0:
        return 0.0
    return float(np.log(current / past))


def _realised_vol(close: pd.Series, period: int = 20) -> float:
    """
    Annualised realised volatility from daily log-returns over `period` bars.

    Returns a small positive floor (0.01) to avoid division-by-zero.
    """
    if len(close) < period + 1:
        return 0.01
    log_rets = np.log(close.iloc[-period:] / close.iloc[-period:].shift(1)).dropna()
    if len(log_rets) < 2:
        return 0.01
    return max(float(log_rets.std(ddof=1)) * np.sqrt(period), 0.01)


# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class TSMOMStrategy(BaseStrategy):
    """
    Time Series Momentum — blends 1-month, 3-month, and 12-month own-series
    momentum signals with volatility scaling and trend-strength filters.

    Reference: Moskowitz, Ooi, Pedersen (2012).  Documented Sharpe 1.0–1.5
    across equities, fixed income, commodities, and FX.
    """

    name = "tsmom"
    description = (
        "Time series momentum (Moskowitz 2012): blends 3 lookback windows "
        "(1mo/3mo/12mo) into a single signal, filtered by EMA(50) trend, "
        "ADX > 15 trend strength, and volatility regime. "
        "Wide stops (2.5× ATR) and 2:1 R:R minimum for trend-following."
    )
    timeframes = ["4h", "1d"]
    markets = ["crypto", "commodities", "forex", "equities"]

    def __init__(
        self,
        # Lookback windows — default calibrated for 4h bars
        short_lookback: int = 126,   # ~1 month on 4h (6 bars/day × 21 days)
        mid_lookback: int = 378,     # ~3 months on 4h (6 bars/day × 63 days)
        long_lookback: int = 756,    # ~12 months capped at 756 for data availability
        # Trend filters
        ema_fast_period: int = 50,
        ema_slow_period: int = 200,
        adx_period: int = 14,
        adx_min: float = 15.0,        # minimum trend strength to enter
        adx_strong: float = 25.0,     # threshold for "strong trend" conviction bonus
        # Volatility gates
        atr_period: int = 14,
        atr_stop_mult: float = 2.5,   # wider stop — let trends breathe
        atr_tp_mult: float = 5.0,     # high R:R for trend following
        atr_spike_mult: float = 3.0,  # emergency exit if ATR > mult × its own SMA
        atr_sma_period: int = 50,     # SMA of ATR for spike / percentile check
        vol_pct_cap: float = 90.0,    # refuse entry if vol in top N-th percentile
        # Realised vol for conviction base
        realised_vol_period: int = 20,
    ) -> None:
        self.short_lookback = short_lookback
        self.mid_lookback = mid_lookback
        self.long_lookback = long_lookback
        self.ema_fast_period = ema_fast_period
        self.ema_slow_period = ema_slow_period
        self.adx_period = adx_period
        self.adx_min = adx_min
        self.adx_strong = adx_strong
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.atr_tp_mult = atr_tp_mult
        self.atr_spike_mult = atr_spike_mult
        self.atr_sma_period = atr_sma_period
        self.vol_pct_cap = vol_pct_cap
        self.realised_vol_period = realised_vol_period

        # Minimum rows: need EMA(200) AND the longest lookback window both to be valid
        self._min_bars: int = max(long_lookback, ema_slow_period) + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full TSMOM analysis on OHLCV data and return a Signal or None.

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
        ema50_series = ema(close, self.ema_fast_period)
        ema200_series = ema(close, self.ema_slow_period)
        adx_df = adx(df, self.adx_period)
        atr_series = atr(df, self.atr_period)
        atr_sma_series = sma(atr_series, self.atr_sma_period)

        close_now = float(close.iloc[-1])
        ema50_now = float(ema50_series.iloc[-1])
        ema200_now = float(ema200_series.iloc[-1])
        adx_now = float(adx_df["adx"].iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        atr_sma_now = float(atr_sma_series.iloc[-1])

        # --- Volatility regime gate ---
        # Compute ATR/close as a normalised volatility measure (percentage ATR)
        pct_atr_series = atr_series / close.replace(0.0, np.nan)
        pct_atr_now = float(pct_atr_series.iloc[-1])

        # Use available history to compute percentile; fall back to last atr_sma_period bars
        pct_atr_history = pct_atr_series.dropna()
        if len(pct_atr_history) >= self.atr_sma_period:
            vol_pct_threshold = float(
                np.percentile(pct_atr_history.values, self.vol_pct_cap)
            )
            vol_in_top_pct = pct_atr_now >= vol_pct_threshold
        else:
            vol_in_top_pct = False

        # --- Gate 1: Volatility must NOT be in the top percentile ---
        if vol_in_top_pct:
            return None

        # --- Gate 2: ADX must show minimum trend strength ---
        if pd.isna(adx_now) or adx_now < self.adx_min:
            return None

        # --- Blended signal computation ---
        blended_avg, agreement_count, individual_returns = self._compute_blended_signal(close)

        # Need at least 2 of 3 windows to agree on direction
        if agreement_count < 2:
            return None

        # --- Gate 3: Structural trend alignment (EMA 50) ---
        if blended_avg > 0 and close_now <= ema50_now:
            return None
        if blended_avg < 0 and close_now >= ema50_now:
            return None

        # Determine direction
        direction = Direction.LONG if blended_avg > 0 else Direction.SHORT

        # --- Price levels ---
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now
        tp_dist = self.atr_tp_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            take_profit = entry_price + tp_dist
        else:
            stop_loss = entry_price + stop_dist
            take_profit = entry_price - tp_dist

        # Sanity checks: prices must be positive and directionally sound
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        # --- Conviction scoring ---
        realised_vol = _realised_vol(close, self.realised_vol_period)

        conviction = self._score_conviction(
            blended_avg=blended_avg,
            agreement_count=agreement_count,
            individual_returns=individual_returns,
            realised_vol=realised_vol,
            adx_now=adx_now,
            close_now=close_now,
            ema200_now=ema200_now,
            pct_atr_now=pct_atr_now,
            pct_atr_history=pct_atr_history,
            direction=direction,
        )

        # Enforce minimum conviction threshold (mirrors system-wide 0.3 floor)
        if abs(conviction) < 0.30:
            return None

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "blended_signal": round(blended_avg, 6),
                "agreement_count": agreement_count,
                "return_short": round(individual_returns[0], 6),
                "return_mid": round(individual_returns[1], 6),
                "return_long": round(individual_returns[2], 6),
                "realised_vol": round(realised_vol, 6),
                "pct_atr": round(pct_atr_now, 6),
                "adx": round(adx_now, 2),
                "ema50": round(ema50_now, 8),
                "ema200": round(ema200_now, 8),
                "atr": round(atr_now, 8),
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — delegates to analyze()."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when any of the following fires:
          1. Blended signal has reversed to the opposing direction.
          2. ATR spike: current ATR > atr_spike_mult × ATR's own 50-bar SMA.
        """
        if not self._min_rows(df, self._min_bars):
            return False

        close = df["close"]
        atr_series = atr(df, self.atr_period)
        atr_sma_series = sma(atr_series, self.atr_sma_period)

        atr_now = float(atr_series.iloc[-1])
        atr_sma_now = float(atr_sma_series.iloc[-1])

        # --- Exit 1: Volatility spike — emergency exit ---
        if pd.notna(atr_sma_now) and atr_sma_now > 0:
            if atr_now > self.atr_spike_mult * atr_sma_now:
                return True

        # --- Exit 2: Signal reversal ---
        blended_avg, agreement_count, _ = self._compute_blended_signal(close)

        # Only act on reversal if the opposing signal also has at least 2/3 agreement
        if position.side == Direction.LONG:
            if blended_avg < 0 and agreement_count >= 2:
                return True
        else:
            if blended_avg > 0 and agreement_count >= 2:
                return True

        return False

    # ------------------------------------------------------------------
    # TSMOM-specific computation
    # ------------------------------------------------------------------

    def _compute_blended_signal(
        self,
        close: pd.Series,
    ) -> tuple[float, int, list[float]]:
        """
        Compute the blended TSMOM signal from three lookback windows.

        Returns
        -------
        blended_avg : float
            Average of the three signed (+1/-1) returns, scaled by return magnitude.
            Range: approximately (-1, +1) but not hard-bounded before clamping.
            Positive → long bias, negative → short bias.
        agreement_count : int
            Number of windows (0-3) that agree on the majority direction.
            2 or 3 = tradeable signal.
        individual_returns : list[float]
            Raw log-returns for [short_lookback, mid_lookback, long_lookback] windows.
        """
        r_short = _log_return(close, self.short_lookback)
        r_mid = _log_return(close, self.mid_lookback)
        r_long = _log_return(close, self.long_lookback)

        individual_returns = [r_short, r_mid, r_long]

        # Sign each return (+1 or -1)
        signs = [
            1.0 if r > 0 else -1.0
            for r in individual_returns
        ]

        # Blended average: mean of signed returns, weighted by their magnitude
        # This preserves direction information while letting strong moves vote harder
        signed_returns = [s * abs(r) for s, r in zip(signs, individual_returns)]
        blended_avg = float(np.mean(signed_returns))

        # Count how many windows agree with the blended direction
        majority_sign = 1.0 if blended_avg >= 0 else -1.0
        agreement_count = sum(1 for s in signs if s == majority_sign)

        return blended_avg, agreement_count, individual_returns

    def _score_conviction(
        self,
        blended_avg: float,
        agreement_count: int,
        individual_returns: list[float],
        realised_vol: float,
        adx_now: float,
        close_now: float,
        ema200_now: float,
        pct_atr_now: float,
        pct_atr_history: pd.Series,
        direction: Direction,
    ) -> float:
        """
        Build a signed conviction score in [-1.0, 1.0].

        Component weights
        -----------------
        Base (up to 0.50): |blended_avg| / realised_vol, normalised and capped.
        +0.15  All 3 lookback windows agree (unanimous signal)
        +0.10  ADX > adx_strong (strong confirmed trend)
        +0.10  Price aligned with EMA(200) macro trend
        +0.10  ATR/close below its 50-bar median (calmer vol = cleaner trends)
        """
        score = 0.0

        # --- Base: signal strength relative to realised volatility ---
        # |blended_avg| is the average log-return magnitude across windows.
        # Dividing by realised_vol makes it volatility-adjusted (Sharpe-like).
        # Cap normalised value at 1.0 and scale to 0.50 weight.
        vol_adj_strength = abs(blended_avg) / realised_vol
        base = min(vol_adj_strength / 2.0, 1.0) * 0.50
        score += base

        # --- Bonus 1: All 3 windows agree (+0.15) ---
        if agreement_count == 3:
            score += 0.15

        # --- Bonus 2: Strong trend (ADX > adx_strong) (+0.10) ---
        if adx_now >= self.adx_strong:
            score += 0.10

        # --- Bonus 3: Macro trend alignment with EMA(200) (+0.10) ---
        if direction == Direction.LONG and close_now > ema200_now:
            score += 0.10
        elif direction == Direction.SHORT and close_now < ema200_now:
            score += 0.10

        # --- Bonus 4: Volatility below 50-bar median (+0.10) ---
        if len(pct_atr_history) >= self.atr_sma_period:
            median_vol = float(np.percentile(pct_atr_history.values, 50.0))
            if pct_atr_now < median_vol:
                score += 0.10

        # Sign and clamp
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)
