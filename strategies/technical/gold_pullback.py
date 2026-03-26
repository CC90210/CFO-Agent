"""
strategies/technical/gold_pullback.py — Gold Keltner Channel Pullback Strategy

Thesis
------
Breakout entries on gold and silver carry the highest risk of being whipsawed —
price breaks the channel, retail chases, institutions fade the move, and the
breakout reverses before completing.  A better entry is the PULLBACK: wait for the
institutional breakout to confirm the new trend, then buy the retracement at a
structurally superior price with tighter risk.

This strategy implements a 4-phase state machine per symbol:

  SCANNING        → Wait for a clean KC breakout with ADX trend confirmation.
  PULLBACK_WAIT   → After breakout, wait for price to retrace into EMA(20) ± 0.5×ATR.
                    Timeout after 10 bars. Abort if price falls below EMA(50).
  ENTRY           → On the first bullish candle above EMA(20) with positive MACD
                    histogram and RSI not overbought (< 75), generate a Signal.
  MANAGING        → Handled by the engine (SL/TP/trailing). Strategy resets to SCANNING.

Entry rules (LONG):
    Phase 1 — Breakout:  close > upper KC  AND  ADX > 20
    Phase 2 — Pullback:  price enters EMA(20) ± 0.5×ATR zone  (within 10 bars)
    Phase 3 — Entry:     bullish candle (close > open)  AND  close > EMA(20)
                         AND  MACD histogram > 0  AND  RSI < 75

Entry rules (SHORT): mirror image.

Exit signals (engine handles SL/TP; strategy adds structural exits):
    - EMA(20) crosses below EMA(50)   — trend structure broken
    - Price drops below lower KC       — trend failed
    - MACD histogram negative 3 consecutive bars — momentum died

Conviction scoring (base 0.55):
    +0.10  ADX > 30 (strong trend at entry time)
    +0.10  Pullback touched but did not break below EMA(20) (clean retracement)
    +0.10  Pullback volume < breakout volume (healthy, low-volume retrace)
    +0.10  Close > EMA(200) (macro trend aligned)
    +0.05  Seasonal bonus — Aug–Feb (gold seasonally strong months)
    Cap at 1.0; signed per direction.

Best markets    : XAU_USD (gold), XAG_USD (silver) via OANDA
Best timeframes : 1h, 4h, 1d
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum, auto
from typing import NamedTuple

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import (
    adx,
    atr,
    ema,
    keltner_channels,
    macd,
    rsi,
    sma,
)


# ---------------------------------------------------------------------------
# State machine definitions
# ---------------------------------------------------------------------------


class _Phase(Enum):
    SCANNING = auto()
    PULLBACK_WAIT = auto()
    ENTRY = auto()


class _SymbolState(NamedTuple):
    """Immutable snapshot of per-symbol state machine data."""

    phase: _Phase
    breakout_price: float
    breakout_atr: float
    breakout_volume: float
    bars_waiting: int        # bars elapsed since breakout (PULLBACK_WAIT counter)
    direction: Direction     # direction of the detected breakout


_GOLD_STRONG_MONTHS = frozenset([8, 9, 10, 11, 12, 1, 2])
_PULLBACK_TIMEOUT_BARS = 10


# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class GoldPullbackStrategy(BaseStrategy):
    """
    4-phase state-machine pullback strategy for gold and silver.

    The _state dict is keyed by symbol string and holds a _SymbolState
    describing which phase the instrument is currently in.  Each call to
    analyze() advances or resets the state for that symbol.
    """

    name = "gold_pullback"
    description = (
        "Keltner Channel breakout detection followed by pullback entry for superior "
        "risk:reward.  Tracks per-symbol state across bars (SCANNING → PULLBACK_WAIT "
        "→ ENTRY → MANAGING).  Designed for XAU_USD and XAG_USD via OANDA."
    )
    timeframes = ["1h", "4h", "1d"]
    markets = ["commodities"]

    # Minimum bars to compute EMA(200)
    _MIN_BARS: int = 210

    # Shared state across all instances, keyed by symbol
    _state: dict[str, _SymbolState] = {}

    def __init__(
        self,
        # Keltner Channel parameters
        keltner_ema_period: int = 20,
        keltner_atr_period: int = 14,
        keltner_multiplier: float = 2.0,
        # Pullback zone half-width (ATR multiples around EMA 20)
        pullback_zone_atr_mult: float = 0.5,
        # EMA periods
        ema_fast: int = 20,
        ema_mid: int = 50,
        ema_slow: int = 200,
        # ADX parameters
        adx_period: int = 14,
        adx_breakout_threshold: float = 20.0,
        adx_strong_threshold: float = 30.0,
        # MACD parameters
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        # RSI parameters
        rsi_period: int = 14,
        rsi_overbought: float = 75.0,
        rsi_oversold: float = 25.0,
        # ATR risk parameters
        atr_period: int = 14,
        atr_stop_mult: float = 2.0,
        atr_tp_mult: float = 4.0,
        # Pullback timeout (bars)
        pullback_timeout_bars: int = _PULLBACK_TIMEOUT_BARS,
        # Volume SMA period for breakout volume reference
        vol_sma_period: int = 20,
        # Consecutive negative MACD bars before exit
        macd_exit_consecutive_bars: int = 3,
    ) -> None:
        self.keltner_ema_period = keltner_ema_period
        self.keltner_atr_period = keltner_atr_period
        self.keltner_multiplier = keltner_multiplier
        self.pullback_zone_atr_mult = pullback_zone_atr_mult
        self.ema_fast = ema_fast
        self.ema_mid = ema_mid
        self.ema_slow = ema_slow
        self.adx_period = adx_period
        self.adx_breakout_threshold = adx_breakout_threshold
        self.adx_strong_threshold = adx_strong_threshold
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.atr_tp_mult = atr_tp_mult
        self.pullback_timeout_bars = pullback_timeout_bars
        self.vol_sma_period = vol_sma_period
        self.macd_exit_consecutive_bars = macd_exit_consecutive_bars

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Advance the per-symbol state machine by one bar and return a Signal
        when the ENTRY phase conditions are all satisfied, or None otherwise.

        Parameters
        ----------
        df : OHLCV DataFrame, UTC-indexed.
             Must contain: open, high, low, close, volume.
             Minimum length: 210 bars (EMA 200 warmup).
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._MIN_BARS):
            return None

        symbol = df.attrs.get("symbol", "UNKNOWN")

        indicators = self._compute_indicators(df)
        if indicators is None:
            return None

        (
            close_now,
            open_now,
            atr_now,
            kc_upper,
            kc_lower,
            ema20_now,
            ema50_now,
            ema200_now,
            adx_now,
            hist_now,
            rsi_now,
            vol_now,
        ) = indicators

        critical = [
            close_now, atr_now, kc_upper, kc_lower,
            ema20_now, ema50_now, ema200_now, adx_now, hist_now, rsi_now,
        ]
        if any(pd.isna(v) for v in critical):
            return None

        # Retrieve (or initialise) the state for this symbol
        state = GoldPullbackStrategy._state.get(
            symbol,
            _SymbolState(
                phase=_Phase.SCANNING,
                breakout_price=0.0,
                breakout_atr=0.0,
                breakout_volume=0.0,
                bars_waiting=0,
                direction=Direction.FLAT,
            ),
        )

        # ----------------------------------------------------------------
        # Phase 1: SCANNING
        # ----------------------------------------------------------------
        if state.phase == _Phase.SCANNING:
            long_breakout = (
                close_now > kc_upper
                and adx_now > self.adx_breakout_threshold
            )
            short_breakout = (
                close_now < kc_lower
                and adx_now > self.adx_breakout_threshold
            )

            if long_breakout or short_breakout:
                direction = Direction.LONG if long_breakout else Direction.SHORT
                GoldPullbackStrategy._state[symbol] = _SymbolState(
                    phase=_Phase.PULLBACK_WAIT,
                    breakout_price=close_now,
                    breakout_atr=atr_now,
                    breakout_volume=vol_now,
                    bars_waiting=0,
                    direction=direction,
                )
            # No signal during SCANNING
            return None

        # ----------------------------------------------------------------
        # Phase 2: PULLBACK_WAIT
        # ----------------------------------------------------------------
        if state.phase == _Phase.PULLBACK_WAIT:
            bars_waiting = state.bars_waiting + 1

            # Abort conditions
            timeout = bars_waiting >= self.pullback_timeout_bars
            trend_failed_long = (
                state.direction == Direction.LONG and close_now < ema50_now
            )
            trend_failed_short = (
                state.direction == Direction.SHORT and close_now > ema50_now
            )

            if timeout or trend_failed_long or trend_failed_short:
                GoldPullbackStrategy._state[symbol] = _SymbolState(
                    phase=_Phase.SCANNING,
                    breakout_price=0.0,
                    breakout_atr=0.0,
                    breakout_volume=0.0,
                    bars_waiting=0,
                    direction=Direction.FLAT,
                )
                return None

            # Pullback zone: EMA(20) ± pullback_zone_atr_mult × ATR
            zone_half = self.pullback_zone_atr_mult * atr_now
            in_pullback_zone_long = (
                state.direction == Direction.LONG
                and (ema20_now - zone_half) <= close_now <= (ema20_now + zone_half)
            )
            in_pullback_zone_short = (
                state.direction == Direction.SHORT
                and (ema20_now - zone_half) <= close_now <= (ema20_now + zone_half)
            )

            if in_pullback_zone_long or in_pullback_zone_short:
                GoldPullbackStrategy._state[symbol] = _SymbolState(
                    phase=_Phase.ENTRY,
                    breakout_price=state.breakout_price,
                    breakout_atr=state.breakout_atr,
                    breakout_volume=state.breakout_volume,
                    bars_waiting=bars_waiting,
                    direction=state.direction,
                )
            else:
                # Still waiting — update bar counter only
                GoldPullbackStrategy._state[symbol] = _SymbolState(
                    phase=_Phase.PULLBACK_WAIT,
                    breakout_price=state.breakout_price,
                    breakout_atr=state.breakout_atr,
                    breakout_volume=state.breakout_volume,
                    bars_waiting=bars_waiting,
                    direction=state.direction,
                )
            return None

        # ----------------------------------------------------------------
        # Phase 3: ENTRY
        # ----------------------------------------------------------------
        if state.phase == _Phase.ENTRY:
            direction = state.direction

            # Bullish candle confirmation for LONG
            bullish_candle = close_now > open_now and close_now > ema20_now
            # Bearish candle confirmation for SHORT
            bearish_candle = close_now < open_now and close_now < ema20_now

            macd_positive = hist_now > 0
            macd_negative = hist_now < 0
            rsi_not_overbought = rsi_now < self.rsi_overbought
            rsi_not_oversold = rsi_now > self.rsi_oversold

            long_entry = (
                direction == Direction.LONG
                and bullish_candle
                and macd_positive
                and rsi_not_overbought
            )
            short_entry = (
                direction == Direction.SHORT
                and bearish_candle
                and macd_negative
                and rsi_not_oversold
            )

            if not (long_entry or short_entry):
                # Entry conditions not yet met — check if we should abort:
                # Price moved back through EMA(50) means trend failed
                trend_failed_long = (
                    direction == Direction.LONG and close_now < ema50_now
                )
                trend_failed_short = (
                    direction == Direction.SHORT and close_now > ema50_now
                )
                if trend_failed_long or trend_failed_short:
                    GoldPullbackStrategy._state[symbol] = _SymbolState(
                        phase=_Phase.SCANNING,
                        breakout_price=0.0,
                        breakout_atr=0.0,
                        breakout_volume=0.0,
                        bars_waiting=0,
                        direction=Direction.FLAT,
                    )
                return None

            # ---- Risk levels (absolute prices) ---------------------------
            stop_dist = self.atr_stop_mult * atr_now
            tp_dist = self.atr_tp_mult * atr_now

            if direction == Direction.LONG:
                # Stop below EMA(20) by 2×ATR
                stop_loss = ema20_now - stop_dist
                take_profit = close_now + tp_dist
            else:
                stop_loss = ema20_now + stop_dist
                take_profit = close_now - tp_dist

            if stop_loss <= 0 or take_profit <= 0:
                return None

            # ---- Conviction score ----------------------------------------
            conviction = self._score_conviction(
                direction=direction,
                df=df,
                close_now=close_now,
                atr_now=atr_now,
                ema20_now=ema20_now,
                ema200_now=ema200_now,
                adx_now=adx_now,
                breakout_volume=state.breakout_volume,
                vol_now=vol_now,
            )

            # Reset state machine — engine takes over position management
            GoldPullbackStrategy._state[symbol] = _SymbolState(
                phase=_Phase.SCANNING,
                breakout_price=0.0,
                breakout_atr=0.0,
                breakout_volume=0.0,
                bars_waiting=0,
                direction=Direction.FLAT,
            )

            return Signal(
                symbol=symbol,
                direction=direction,
                conviction=conviction,
                stop_loss=round(stop_loss, 5),
                take_profit=round(take_profit, 5),
                strategy_name=self.name,
                metadata={
                    "entry_price": close_now,
                    "atr": round(atr_now, 5),
                    "adx": round(adx_now, 2),
                    "rsi": round(rsi_now, 2),
                    "macd_histogram": round(hist_now, 5),
                    "ema_20": round(ema20_now, 5),
                    "ema_50": round(ema50_now, 5),
                    "ema_200": round(ema200_now, 5),
                    "kc_upper": round(kc_upper, 5),
                    "kc_lower": round(kc_lower, 5),
                    "phase_transition": "ENTRY_TRIGGERED",
                },
            )

        # Unreachable — defensive return
        return None

    def should_enter(self, df: pd.DataFrame) -> bool:
        """
        Lightweight entry check called by the scanner loop.
        Returns True when analyze() produces a non-FLAT signal.
        """
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Structural exit signals — called each bar while a position is open.

        The engine handles SL/TP exits.  This method handles three additional
        structural failure conditions:
          (a) EMA(20) crosses below EMA(50) — trend structure broken
          (b) Price drops below lower KC     — trend reversal / failed breakout
          (c) MACD histogram negative for N consecutive bars — momentum dead

        Parameters
        ----------
        df       : current OHLCV DataFrame
        position : the currently open position
        """
        if not self._min_rows(df, self._MIN_BARS):
            return False

        indicators = self._compute_indicators(df)
        if indicators is None:
            return False

        (
            close_now,
            _open_now,
            _atr_now,
            kc_upper,
            kc_lower,
            ema20_now,
            ema50_now,
            _ema200_now,
            _adx_now,
            _hist_now,
            _rsi_now,
            _vol_now,
        ) = indicators

        if any(
            pd.isna(v)
            for v in [close_now, kc_upper, kc_lower, ema20_now, ema50_now]
        ):
            return False

        if position.side == Direction.LONG:
            ema_stack_broken = ema20_now < ema50_now
            trend_failed = close_now < kc_lower
            momentum_dead = self._macd_negative_consecutive(df)
            return ema_stack_broken or trend_failed or momentum_dead

        if position.side == Direction.SHORT:
            ema_stack_broken = ema20_now > ema50_now
            trend_failed = close_now > kc_upper
            momentum_dead = self._macd_positive_consecutive(df)
            return ema_stack_broken or trend_failed or momentum_dead

        return False

    # ------------------------------------------------------------------
    # Indicator computation
    # ------------------------------------------------------------------

    def _compute_indicators(
        self,
        df: pd.DataFrame,
    ) -> (
        tuple[
            float, float, float, float, float,
            float, float, float, float, float, float, float,
        ]
        | None
    ):
        """
        Compute all indicators in one place and return the latest scalar values.

        Returns None if any computation fails (e.g., insufficient warmup rows).
        Returned tuple:
            close_now, open_now, atr_now,
            kc_upper, kc_lower,
            ema20_now, ema50_now, ema200_now,
            adx_now, macd_hist_now, rsi_now, vol_now
        """
        try:
            close = df["close"]

            atr_series = atr(df, self.atr_period)
            atr_now = atr_series.iloc[-1]

            kc = keltner_channels(
                df,
                ema_period=self.keltner_ema_period,
                atr_period=self.keltner_atr_period,
                multiplier=self.keltner_multiplier,
            )
            kc_upper = kc.upper.iloc[-1]
            kc_lower = kc.lower.iloc[-1]

            ema20_series = ema(close, self.ema_fast)
            ema50_series = ema(close, self.ema_mid)
            ema200_series = ema(close, self.ema_slow)
            ema20_now = ema20_series.iloc[-1]
            ema50_now = ema50_series.iloc[-1]
            ema200_now = ema200_series.iloc[-1]

            adx_df = adx(df, self.adx_period)
            adx_now = adx_df["adx"].iloc[-1]

            macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)
            hist_now = macd_df["histogram"].iloc[-1]

            rsi_series = rsi(close, self.rsi_period)
            rsi_now = rsi_series.iloc[-1]

            close_now = close.iloc[-1]
            open_now = df["open"].iloc[-1]
            vol_now = df["volume"].iloc[-1]

        except (IndexError, KeyError):
            return None

        return (
            close_now,
            open_now,
            atr_now,
            kc_upper,
            kc_lower,
            ema20_now,
            ema50_now,
            ema200_now,
            adx_now,
            hist_now,
            rsi_now,
            vol_now,
        )

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        direction: Direction,
        df: pd.DataFrame,
        close_now: float,
        atr_now: float,
        ema20_now: float,
        ema200_now: float,
        adx_now: float,
        breakout_volume: float,
        vol_now: float,
    ) -> float:
        """
        Build conviction from the base score plus up to five optional bonuses.

        Base: 0.55
        +0.10  ADX > adx_strong_threshold (strong trend at entry)
        +0.10  Pullback touched but did not break below EMA(20) (clean retracement)
        +0.10  Pullback volume < breakout volume (healthy low-volume retrace)
        +0.10  Close > EMA(200) for LONG / Close < EMA(200) for SHORT (macro aligned)
        +0.05  Seasonal bonus: current month in Aug-Feb (gold strong season)
        Cap at 1.0 before signing.  Signed negative for SHORT.
        """
        score = 0.55

        # Bonus 1: Strong trend at entry
        if adx_now > self.adx_strong_threshold:
            score += 0.10

        # Bonus 2: Clean pullback — price touched but did not violate EMA(20)
        # Approximated by checking that the candle low (for LONG) is >= EMA(20) - ATR*0.1
        # (tight tolerance to confirm price bounced off, not through the EMA)
        tolerance = 0.1 * atr_now
        if not pd.isna(atr_now) and atr_now > 0:
            low_now = df["low"].iloc[-1]
            high_now = df["high"].iloc[-1]
            if direction == Direction.LONG:
                clean_pullback = low_now >= (ema20_now - tolerance)
            else:
                clean_pullback = high_now <= (ema20_now + tolerance)
            if clean_pullback:
                score += 0.10

        # Bonus 3: Pullback volume < breakout volume
        if breakout_volume > 0 and not pd.isna(vol_now):
            if vol_now < breakout_volume:
                score += 0.10

        # Bonus 4: Macro trend alignment via EMA(200)
        if not pd.isna(ema200_now):
            if direction == Direction.LONG and close_now > ema200_now:
                score += 0.10
            elif direction == Direction.SHORT and close_now < ema200_now:
                score += 0.10

        # Bonus 5: Seasonal factor — gold seasonally strong Aug–Feb
        current_month = datetime.now(UTC).month
        if current_month in _GOLD_STRONG_MONTHS:
            score += 0.05

        score = min(score, 1.0)
        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    # ------------------------------------------------------------------
    # Exit helpers
    # ------------------------------------------------------------------

    def _macd_negative_consecutive(self, df: pd.DataFrame) -> bool:
        """
        Return True when the MACD histogram has been negative for
        macd_exit_consecutive_bars consecutive bars (momentum confirmed dead
        for a LONG position).
        """
        n = self.macd_exit_consecutive_bars
        if len(df) < n:
            return False
        close = df["close"]
        macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)
        recent_hist = macd_df["histogram"].iloc[-n:]
        if recent_hist.isna().any():
            return False
        return bool((recent_hist < 0).all())

    def _macd_positive_consecutive(self, df: pd.DataFrame) -> bool:
        """
        Return True when the MACD histogram has been positive for
        macd_exit_consecutive_bars consecutive bars (momentum reversed
        for a SHORT position).
        """
        n = self.macd_exit_consecutive_bars
        if len(df) < n:
            return False
        close = df["close"]
        macd_df = macd(close, self.macd_fast, self.macd_slow, self.macd_signal)
        recent_hist = macd_df["histogram"].iloc[-n:]
        if recent_hist.isna().any():
            return False
        return bool((recent_hist > 0).all())
