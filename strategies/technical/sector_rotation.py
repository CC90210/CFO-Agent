"""
strategies/technical/sector_rotation.py — Sector Momentum Rotation

Background
----------
Ranks the 11 S&P 500 sector ETFs by momentum and holds the top performers.
Academic literature (Meb Faber, Gary Antonacci) consistently shows that a
simple cross-sectional momentum filter applied to sector ETFs outperforms
SPY by ~3-4% annually while reducing maximum drawdown.

This strategy evaluates each sector ETF independently.  It does not require
awareness of the other sectors — the conviction score naturally encodes
relative momentum strength, so the portfolio manager can rank open signals
and allocate to the top scorers.

Universe
--------
The 11 SPDR Select Sector ETFs covering the full S&P 500:
    XLK  — Technology
    XLF  — Financials
    XLE  — Energy
    XLV  — Health Care
    XLI  — Industrials
    XLC  — Communication Services
    XLY  — Consumer Discretionary
    XLP  — Consumer Staples
    XLU  — Utilities
    XLRE — Real Estate
    XLB  — Materials

Entry logic (LONG ONLY — sector rotation goes to cash, not short)
-----------------------------------------------------------------
All three gates must be satisfied:
    1. Momentum score > 0   — absolute momentum filter (Antonacci dual momentum).
       Momentum = average of 1-month, 3-month, and 6-month returns.
       Being positive on all three ensures the sector is in a genuine
       up-cycle, not just recovering from a deeper hole.
    2. Close > SMA(200)     — macro uptrend filter. A sector below its
       200-day MA is in a structural downtrend; we do not fight that.
    3. RSI(14) < 70         — avoids chasing overbought entries.  This
       is a timing filter, not a reversal filter; 70 is the ceiling,
       not a target.

Exit logic
----------
    - Momentum score turns negative  — the sector has lost its relative edge.
    - Price drops below SMA(200)     — structural downtrend confirmed.
    Both conditions are checked on every daily bar, giving prompt exits even
    though rebalancing typically occurs monthly in a live implementation.

Conviction scoring (base 0.40, max 1.0 — LONG signals only)
------------------------------------------------------------
    base:    +0.40
    +0.10  short-term momentum positive  (1-month return > 0)
    +0.10  medium-term momentum positive (3-month return > 0)
    +0.10  long-term momentum positive   (6-month return > 0)
    +0.10  all three timeframes positive (full alignment bonus)
    +0.10  price > SMA(50)              (intermediate trend confirming macro trend)
    +0.05  ADX(14) > 25                 (strong, clean trend — not choppy rotation)
    +0.05  volume > 1.2x 20-bar average (institutional accumulation present)

Stop / take-profit
------------------
    Stop loss  : entry − (atr_stop_mult × ATR)  — default 2.0x ATR.
                 Wider than crypto strategies because sector ETFs have
                 lower volatility and longer hold periods (days to weeks).
    Take profit: entry + (rr_ratio × atr_stop_mult × ATR) — default 2.5 R:R.

Best timeframe : 1d (daily bars; rebalance monthly in practice)
Best markets   : XLK, XLF, XLE, XLV, XLI, XLC, XLY, XLP, XLU, XLRE, XLB
"""

from __future__ import annotations

import math

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, rsi, sma


class SectorRotationStrategy(BaseStrategy):
    """
    Sector Momentum Rotation for the 11 SPDR S&P 500 sector ETFs.

    Long-only strategy.  Ranks sector ETFs by their composite momentum score
    (average of 1-month, 3-month, and 6-month returns) and enters when:
        - Composite momentum > 0 (absolute momentum filter)
        - Price > SMA(200)       (macro trend filter)
        - RSI(14) < 70           (not overbought)

    Exits when momentum turns negative or price falls below SMA(200).
    """

    name = "sector_rotation"
    description = (
        "Ranks the 11 SPDR sector ETFs by 1/3/6-month composite momentum. "
        "Goes long when momentum is positive, price > SMA(200), and RSI < 70. "
        "Exits on negative momentum or price below SMA(200). Long-only. "
        "Designed for daily bars; rebalances monthly in practice."
    )
    timeframes = ["1d"]
    markets = ["equities", "etf"]

    # Class-level constant for documentation; actual minimum enforced via self._min_bars.
    _SECTOR_UNIVERSE: list[str] = [
        "XLK", "XLF", "XLE", "XLV", "XLI",
        "XLC", "XLY", "XLP", "XLU", "XLRE", "XLB",
    ]

    def __init__(
        self,
        short_momentum_bars: int = 21,    # ~1 month of daily bars
        mid_momentum_bars: int = 63,      # ~3 months
        long_momentum_bars: int = 126,    # ~6 months
        sma_trend_period: int = 200,      # 200-day SMA macro filter
        sma_mid_period: int = 50,         # 50-day SMA intermediate trend
        rsi_period: int = 14,
        rsi_overbought: float = 70.0,
        adx_period: int = 14,
        adx_min: float = 25.0,            # trend-strength confirmation bonus threshold
        volume_period: int = 20,
        volume_mult: float = 1.2,         # volume confirmation threshold for bonus
        atr_period: int = 14,
        atr_stop_mult: float = 2.0,       # wider stop — longer-hold equity positions
        rr_ratio: float = 2.5,            # R:R ratio; TP = rr_ratio × stop_distance
    ) -> None:
        self.params: dict[str, int | float] = {
            "short_momentum_bars": short_momentum_bars,
            "mid_momentum_bars": mid_momentum_bars,
            "long_momentum_bars": long_momentum_bars,
            "sma_trend_period": sma_trend_period,
            "sma_mid_period": sma_mid_period,
            "rsi_period": rsi_period,
            "rsi_overbought": rsi_overbought,
            "adx_period": adx_period,
            "adx_min": adx_min,
            "volume_period": volume_period,
            "volume_mult": volume_mult,
            "atr_period": atr_period,
            "atr_stop_mult": atr_stop_mult,
            "rr_ratio": rr_ratio,
        }

        # SMA(200) is the binding constraint; add a 10-bar buffer for convergence.
        self._min_bars: int = sma_trend_period + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full analysis on OHLCV data and return a Signal, or None when
        conditions are not met.

        Requires sma_trend_period + 10 rows (210 by default with default params).
        Returns None — never raises — when data is insufficient or conditions fail.

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV DataFrame, UTC-indexed. Must have columns:
            open, high, low, close, volume.
            df.attrs["symbol"] should be set to the ticker (e.g., "XLK").
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol = df.attrs.get("symbol", "UNKNOWN")

        short_bars = int(self.params["short_momentum_bars"])
        mid_bars = int(self.params["mid_momentum_bars"])
        long_bars = int(self.params["long_momentum_bars"])
        sma_trend_period = int(self.params["sma_trend_period"])
        sma_mid_period = int(self.params["sma_mid_period"])
        rsi_period = int(self.params["rsi_period"])
        adx_period = int(self.params["adx_period"])
        volume_period = int(self.params["volume_period"])
        atr_period = int(self.params["atr_period"])

        # Guard: need enough bars for the longest momentum window too.
        if len(df) < long_bars + 1:
            return None

        # --- Compute indicators ---
        rsi_series = rsi(close, rsi_period)
        sma_200 = sma(close, sma_trend_period)
        sma_50 = sma(close, sma_mid_period)
        adx_df = adx(df, adx_period)
        atr_series = atr(df, atr_period)
        avg_vol = df["volume"].rolling(volume_period).mean()

        # Momentum: simple return over N bars
        # return = (close_now / close_N_bars_ago) - 1
        ret_short = (close / close.shift(short_bars)) - 1.0
        ret_mid = (close / close.shift(mid_bars)) - 1.0
        ret_long = (close / close.shift(long_bars)) - 1.0

        # --- Extract current-bar values ---
        close_now = close.iloc[-1]
        rsi_now = rsi_series.iloc[-1]
        sma_200_now = sma_200.iloc[-1]
        sma_50_now = sma_50.iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        atr_now = atr_series.iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]
        ret_short_now = ret_short.iloc[-1]
        ret_mid_now = ret_mid.iloc[-1]
        ret_long_now = ret_long.iloc[-1]

        # Guard against NaN values from cold-start windows
        if any(
            pd.isna(v)
            for v in (
                rsi_now, sma_200_now, sma_50_now, adx_now,
                atr_now, avg_vol_now,
                ret_short_now, ret_mid_now, ret_long_now,
            )
        ):
            return None

        if atr_now <= 0 or avg_vol_now <= 0:
            return None

        # Composite momentum: equal-weight average of three lookback windows
        momentum_score = (ret_short_now + ret_mid_now + ret_long_now) / 3.0

        # --- Gate 1: Absolute momentum — composite score must be positive ---
        # A negative score means the sector has declined on average; we wait
        # for it to establish positive momentum before entering.
        if momentum_score <= 0:
            return None

        # --- Gate 2: Macro trend filter — price must be above SMA(200) ---
        if close_now <= sma_200_now:
            return None

        # --- Gate 3: Not overbought — RSI < 70 ---
        # Avoids chasing entries at the top of a parabolic move.
        if rsi_now >= float(self.params["rsi_overbought"]):
            return None

        # --- Build stop loss and take profit ---
        stop_dist = float(self.params["atr_stop_mult"]) * atr_now
        tp_dist = float(self.params["rr_ratio"]) * stop_dist

        entry_price = close_now
        stop_loss = entry_price - stop_dist
        take_profit = entry_price + tp_dist

        # Hard safety checks
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if take_profit <= entry_price:
            return None

        # --- Conviction scoring ---
        conviction = self._score_conviction(
            ret_short=ret_short_now,
            ret_mid=ret_mid_now,
            ret_long=ret_long_now,
            close_now=close_now,
            sma_50_now=sma_50_now,
            adx_now=adx_now,
            vol_now=vol_now,
            avg_vol_now=avg_vol_now,
        )

        return Signal(
            symbol=symbol,
            direction=Direction.LONG,
            conviction=conviction,
            stop_loss=round(stop_loss, 4),
            take_profit=round(take_profit, 4),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "momentum_score": round(momentum_score, 4),
                "ret_1m": round(ret_short_now, 4),
                "ret_3m": round(ret_mid_now, 4),
                "ret_6m": round(ret_long_now, 4),
                "rsi": round(rsi_now, 2),
                "sma_200": round(sma_200_now, 4),
                "sma_50": round(sma_50_now, 4),
                "adx": round(adx_now, 2),
                "atr": round(atr_now, 4),
                "volume_ratio": round(vol_now / avg_vol_now, 2),
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
        Exit when sector momentum turns negative OR price drops below SMA(200).

        Momentum is the composite average of 1/3/6-month returns. Either
        condition alone is sufficient to trigger an exit — we do not require
        both, since either represents a meaningful deterioration of the thesis.

        Returns False (stay in trade) when there is insufficient data to
        compute the required indicators rather than forcing a premature exit.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")

        long_bars = int(self.params["long_momentum_bars"])
        sma_trend_period = int(self.params["sma_trend_period"])

        # Need enough rows for the 6-month momentum window and SMA(200).
        min_exit_bars = max(long_bars + 1, sma_trend_period + 1)
        if not self._min_rows(df, min_exit_bars):
            return False

        close = df["close"]
        short_bars = int(self.params["short_momentum_bars"])
        mid_bars = int(self.params["mid_momentum_bars"])

        ret_short = (close.iloc[-1] / close.iloc[-(short_bars + 1)]) - 1.0
        ret_mid = (close.iloc[-1] / close.iloc[-(mid_bars + 1)]) - 1.0
        ret_long = (close.iloc[-1] / close.iloc[-(long_bars + 1)]) - 1.0

        # Guard against division errors producing NaN/Inf
        if any(pd.isna(v) or not math.isfinite(v) for v in (ret_short, ret_mid, ret_long)):
            return False

        momentum_score = (ret_short + ret_mid + ret_long) / 3.0

        sma_200 = sma(close, sma_trend_period)
        sma_200_now = sma_200.iloc[-1]

        if pd.isna(sma_200_now):
            return False

        close_now = close.iloc[-1]

        # Exit condition 1: Momentum has turned negative
        if momentum_score <= 0:
            return True

        # Exit condition 2: Price has broken below the 200-day SMA
        if close_now < sma_200_now:
            return True

        return False

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        ret_short: float,
        ret_mid: float,
        ret_long: float,
        close_now: float,
        sma_50_now: float,
        adx_now: float,
        vol_now: float,
        avg_vol_now: float,
    ) -> float:
        """
        Build conviction score starting from a base of 0.40.

        The conviction score represents both signal quality and relative
        momentum strength — a sector with all three timeframes positive and
        clean trend structure will score near 1.0, giving the portfolio
        manager a natural ranking signal.

        Bonuses (each independent):
            +0.10  1-month return positive   (short-term momentum present)
            +0.10  3-month return positive   (medium-term momentum present)
            +0.10  6-month return positive   (long-term momentum present)
            +0.10  all three positive        (full multi-timeframe alignment)
            +0.10  price > SMA(50)           (intermediate trend confirming macro)
            +0.05  ADX > adx_min             (strong, clean trend)
            +0.05  volume > volume_mult x avg (institutional participation)

        Maximum possible: 0.40 + 0.10 + 0.10 + 0.10 + 0.10 + 0.10 + 0.05 + 0.05 = 1.00
        Score is clamped to [0.0, 1.0] before return.
        All sector rotation signals are LONG; negative conviction is never used.
        """
        score = 0.40

        # Bonus: individual timeframe momentum
        if ret_short > 0:
            score += 0.10
        if ret_mid > 0:
            score += 0.10
        if ret_long > 0:
            score += 0.10

        # Bonus: all three aligned — full multi-timeframe momentum
        if ret_short > 0 and ret_mid > 0 and ret_long > 0:
            score += 0.10

        # Bonus: intermediate trend confirmation
        if close_now > sma_50_now:
            score += 0.10

        # Bonus: strong trend structure (not whipsaw rotation)
        if adx_now > float(self.params["adx_min"]):
            score += 0.05

        # Bonus: volume — institutional money entering the sector
        if avg_vol_now > 0 and (vol_now / avg_vol_now) >= float(self.params["volume_mult"]):
            score += 0.05

        # Sector rotation is long-only; return positive conviction only.
        return self._clamp(score, lo=0.0, hi=1.0)
