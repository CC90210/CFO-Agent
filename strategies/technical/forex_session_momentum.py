"""
strategies/technical/forex_session_momentum.py — Forex Session Momentum Strategy

Background
----------
Forex markets cycle through three distinct trading sessions, each with its own
liquidity profile and volatility character:

    Asian session  : 00:00 – 08:00 UTC  (Tokyo / Sydney)
    London session : 08:00 – 16:00 UTC  (highest FX liquidity globally)
    New York session: 13:00 – 21:00 UTC (USD pairs most active)
    London–NY overlap: 13:00 – 16:00 UTC (highest combined liquidity)

Each session tends to break out of — or reverse — the range established by the
preceding session.  This strategy identifies that prior-session range and enters
on a momentum-confirmed breakout at the start of the next session.

Entry logic (LONG)
------------------
1. Price closes above the previous session's high.
2. EMA(8) > EMA(21)          — short-term momentum is bullish.
3. MACD histogram is positive AND the most recent bar's histogram > the prior
   bar's histogram (momentum building, not fading).
4. ATR(14) is expanding vs its own 5-bar SMA (breakout is real, not a drift).
5. RSI(14) between 40 and 70  — confirmed strength but not overbought.

Entry logic (SHORT)
-------------------
Mirror of the above: break below previous session's low, EMA(8) < EMA(21),
histogram negative and decreasing, ATR expanding, RSI 30–60.

Exits
-----
- Stop loss  : 1.0x previous session range from entry price.
- Take profit: 1.5x previous session range from entry price.
- Gold (XAU/USD): SL = 1.5x range, TP = 2.0x range (gold trends harder).
- Time stop  : If position is still open at the END of the current session,
               close it.  Session-end hours: Asian 08:00, London 16:00, NY 21:00.

Conviction scoring
------------------
    +0.45  base score
    +0.15  all three momentum indicators aligned (EMA + MACD + RSI zone)
    +0.15  volume > 1.5x rolling average (institutional flow)
    +0.15  ADX(14) > 25 (confirmed trending market)
    +0.10  London–NY overlap window (13:00–16:00 UTC — highest liquidity)

Best markets    : EUR/USD, GBP/USD, USD/JPY, XAU/USD, XAG/USD (via OANDA)
Best timeframes : 15m, 1h, 4h
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import adx, atr, ema, macd, rsi, sma


# ---------------------------------------------------------------------------
# Session definitions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Session:
    name: str
    start_hour: int   # UTC, inclusive
    end_hour: int     # UTC, exclusive


_SESSIONS: Final[list[_Session]] = [
    _Session("asian",   start_hour=0,  end_hour=8),
    _Session("london",  start_hour=8,  end_hour=16),
    _Session("new_york", start_hour=13, end_hour=21),
]

# London–NY overlap: 13:00–16:00 UTC
_OVERLAP_START: Final[int] = 13
_OVERLAP_END: Final[int] = 16

# Symbols that receive the gold treatment (wider stops/targets)
_GOLD_SYMBOLS: Final[frozenset[str]] = frozenset({"XAU/USD", "XAUUSD"})


def _current_session(hour: int) -> _Session | None:
    """Return the session active at the given UTC hour, or None if between sessions."""
    # Preference order: NY overlaps London 13-16, but we classify as NY once it opens.
    # Iterate in reverse priority so NY wins during the overlap for session-end timing.
    for session in reversed(_SESSIONS):
        if session.start_hour <= hour < session.end_hour:
            return session
    return None


def _previous_session(current: _Session) -> _Session:
    """Return the session that immediately preceded the current one (wraps midnight)."""
    idx = _SESSIONS.index(current)
    return _SESSIONS[(idx - 1) % len(_SESSIONS)]


class ForexSessionMomentumStrategy(BaseStrategy):
    """
    Forex Session Momentum — enters on momentum-confirmed breakouts of the
    previous session's range at the open of a new session.

    Designed for OANDA forex pairs and commodities (XAU/USD, XAG/USD).
    """

    name = "forex_session_momentum"
    description = (
        "Breaks the previous session's high/low with EMA, MACD, ATR expansion, "
        "and RSI confirmation.  Gold uses wider SL/TP multiples.  Time stop at "
        "session close."
    )
    timeframes = ["15m", "1h", "4h"]
    markets = ["forex", "commodities"]

    def __init__(
        self,
        # EMA periods for momentum filter
        ema_fast: int = 8,
        ema_slow: int = 21,
        # MACD parameters
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        # RSI parameters
        rsi_period: int = 14,
        rsi_long_lo: float = 40.0,   # RSI lower bound for long entries
        rsi_long_hi: float = 70.0,   # RSI upper bound for long entries
        rsi_short_lo: float = 30.0,  # RSI lower bound for short entries
        rsi_short_hi: float = 60.0,  # RSI upper bound for short entries
        # ATR parameters
        atr_period: int = 14,
        atr_expansion_lookback: int = 5,   # bars used for ATR expansion check
        # Volume parameters
        volume_period: int = 20,
        volume_surge_mult: float = 1.5,    # threshold for "institutional flow" bonus
        # ADX parameters
        adx_period: int = 14,
        adx_trend_threshold: float = 25.0,
        # Standard SL/TP multiples (forex)
        sl_range_mult: float = 1.0,
        tp_range_mult: float = 1.5,
        # Gold-specific SL/TP multiples (XAU/USD trends harder)
        gold_sl_range_mult: float = 1.5,
        gold_tp_range_mult: float = 2.0,
        # Minimum session range as a fraction of ATR (filters flat sessions)
        min_range_atr_ratio: float = 0.2,
        # NFP avoidance
        avoid_nfp: bool = True,
    ) -> None:
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal_period = macd_signal
        self.rsi_period = rsi_period
        self.rsi_long_lo = rsi_long_lo
        self.rsi_long_hi = rsi_long_hi
        self.rsi_short_lo = rsi_short_lo
        self.rsi_short_hi = rsi_short_hi
        self.atr_period = atr_period
        self.atr_expansion_lookback = atr_expansion_lookback
        self.volume_period = volume_period
        self.volume_surge_mult = volume_surge_mult
        self.adx_period = adx_period
        self.adx_trend_threshold = adx_trend_threshold
        self.sl_range_mult = sl_range_mult
        self.tp_range_mult = tp_range_mult
        self.gold_sl_range_mult = gold_sl_range_mult
        self.gold_tp_range_mult = gold_tp_range_mult
        self.min_range_atr_ratio = min_range_atr_ratio
        self.avoid_nfp = avoid_nfp

        # Minimum bars needed before any indicator is valid.
        # macd_slow + macd_signal covers MACD warmup; 2*adx_period covers ADX.
        # 96 bars = one full day of 15m data, needed to reconstruct the prior session.
        self._min_bars = max(
            macd_slow + macd_signal,
            2 * adx_period,
            volume_period,
            96,
        ) + 10

    # ------------------------------------------------------------------
    # Core interface
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        symbol: str = df.attrs.get("symbol", "UNKNOWN")
        current_ts: pd.Timestamp = df.index[-1]

        if not self._is_valid_trading_day(current_ts):
            return None

        session = _current_session(current_ts.hour)
        if session is None:
            return None  # Between sessions — no trade

        prev_session = _previous_session(session)

        # Build the previous session's range from recent bars in df.
        prev_range_result = self._build_session_range(df, current_ts, prev_session)
        if prev_range_result is None:
            return None
        prev_high, prev_low, prev_range = prev_range_result

        # ATR filter: skip if previous session range is too thin (flat/holiday)
        atr_series = atr(df, self.atr_period)
        atr_now = atr_series.iloc[-1]
        if atr_now <= 0 or pd.isna(atr_now):
            return None
        if (prev_range / atr_now) < self.min_range_atr_ratio:
            return None  # Range too thin to produce a meaningful breakout

        close_now = df["close"].iloc[-1]

        # Direction: has price broken out of the previous session's range?
        if close_now > prev_high:
            direction = Direction.LONG
        elif close_now < prev_low:
            direction = Direction.SHORT
        else:
            return None  # No breakout yet

        # Compute all indicators
        ema_fast_series = ema(df["close"], self.ema_fast)
        ema_slow_series = ema(df["close"], self.ema_slow)
        macd_df = macd(
            df["close"],
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal_period,
        )
        rsi_series = rsi(df["close"], self.rsi_period)
        atr_sma = sma(atr_series, self.atr_expansion_lookback)
        adx_df = adx(df, self.adx_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        ema_fast_now = ema_fast_series.iloc[-1]
        ema_slow_now = ema_slow_series.iloc[-1]
        hist_now = macd_df["histogram"].iloc[-1]
        hist_prev = macd_df["histogram"].iloc[-2]
        rsi_now = rsi_series.iloc[-1]
        atr_sma_now = atr_sma.iloc[-1]
        adx_now = adx_df["adx"].iloc[-1]
        vol_now = df["volume"].iloc[-1]
        avg_vol_now = avg_vol.iloc[-1]

        # Guard against NaN from insufficient data for any indicator
        for val in (ema_fast_now, ema_slow_now, hist_now, hist_prev, rsi_now,
                    atr_sma_now):
            if pd.isna(val):
                return None

        vol_ratio = (vol_now / avg_vol_now) if avg_vol_now > 0 else 1.0

        # Apply directional filters
        momentum_aligned = self._check_momentum(
            direction, ema_fast_now, ema_slow_now,
            hist_now, hist_prev, rsi_now,
        )
        if not momentum_aligned:
            return None

        # ATR expansion check — used as conviction bonus, not a hard gate.
        # Hard-gating on ATR expansion rejects clean early breakouts and only
        # accepts late, already-exhausted moves.
        atr_expanding = atr_now > atr_sma_now

        # Build SL/TP levels
        is_gold = symbol in _GOLD_SYMBOLS
        sl_mult = self.gold_sl_range_mult if is_gold else self.sl_range_mult
        tp_mult = self.gold_tp_range_mult if is_gold else self.tp_range_mult

        if direction == Direction.LONG:
            stop_loss = close_now - prev_range * sl_mult
            take_profit = close_now + prev_range * tp_mult
        else:
            stop_loss = close_now + prev_range * sl_mult
            take_profit = close_now - prev_range * tp_mult

        # Safety: SL and TP must be positive prices
        if stop_loss <= 0 or take_profit <= 0:
            return None

        # Conviction scoring
        adx_value = adx_now if not pd.isna(adx_now) else 0.0
        is_overlap = _OVERLAP_START <= current_ts.hour < _OVERLAP_END
        conviction = self._score_conviction(
            direction=direction,
            momentum_aligned=momentum_aligned,
            vol_ratio=vol_ratio,
            adx_value=adx_value,
            is_overlap=is_overlap,
            atr_expanding=atr_expanding,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 8),
            take_profit=round(take_profit, 8),
            strategy_name=self.name,
            metadata={
                "entry_price": close_now,
                "prev_session": prev_session.name,
                "current_session": session.name,
                "prev_session_high": round(prev_high, 8),
                "prev_session_low": round(prev_low, 8),
                "prev_session_range": round(prev_range, 8),
                "ema_fast": round(ema_fast_now, 8),
                "ema_slow": round(ema_slow_now, 8),
                "macd_histogram": round(hist_now, 8),
                "rsi": round(rsi_now, 4),
                "atr": round(atr_now, 8),
                "atr_expanding": atr_expanding,
                "adx": round(adx_value, 4),
                "volume_ratio": round(vol_ratio, 4),
                "is_gold": is_gold,
                "is_overlap": is_overlap,
                "sl_mult": sl_mult,
                "tp_mult": tp_mult,
            },
        )

    def should_enter(self, df: pd.DataFrame) -> bool:
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Close position at the end of whichever session was active at entry.
        Session-end hours (UTC): Asian 08:00, London 16:00, NY 21:00.

        Derives the entry session from position.entry_time (not metadata) so that
        this works correctly in the backtest engine, which does not forward signal
        metadata to the Position object.
        """
        if not self._min_rows(df, 2):
            return False

        current_ts: pd.Timestamp = df.index[-1]

        # Determine which session the trade was entered in from the entry timestamp
        entry_hour = position.entry_time.hour if position.entry_time else 0
        entry_session = _current_session(entry_hour)

        if entry_session is None:
            return True  # Entered between sessions — shouldn't happen, exit immediately

        end_hour = entry_session.end_hour

        # For sessions that span past midnight this would need adjustment,
        # but all three sessions end before 24:00 UTC so a simple hour
        # comparison works.  We also need to handle the day boundary: only
        # exit if we are on the same day or later AND past the end hour.
        entry_date = position.entry_time.date() if position.entry_time else current_ts.date()
        current_date = current_ts.date()

        if current_date > entry_date:
            # Next day — session has definitely ended
            return True
        # Same day: exit once the session's end hour is reached
        return current_ts.hour >= end_hour

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_session_range(
        self,
        df: pd.DataFrame,
        current_ts: pd.Timestamp,
        prev_session: _Session,
    ) -> tuple[float, float, float] | None:
        """
        Return (high, low, range) for the previous session.

        The previous session may span two calendar days if it crosses midnight
        (e.g. current session = Asian 00:00, previous session = NY 13-21 UTC on
        the prior day).  We search up to 2 calendar days back to accommodate this.

        Returns None if fewer than 3 bars are found for that session window.
        """
        today = current_ts.normalize()

        for day_offset in (0, 1):
            candidate_date = today - pd.Timedelta(days=day_offset)
            window_start = candidate_date + pd.Timedelta(hours=prev_session.start_hour)
            window_end = candidate_date + pd.Timedelta(hours=prev_session.end_hour)

            # For sessions that end the next calendar day we don't need to worry
            # here — all defined sessions end before midnight UTC.
            session_bars = df.loc[
                (df.index >= window_start) & (df.index < window_end)
            ]

            if len(session_bars) >= 3:
                high = session_bars["high"].max()
                low = session_bars["low"].min()
                return high, low, high - low

        return None  # Could not reconstruct prior session range

    def _check_momentum(
        self,
        direction: Direction,
        ema_fast: float,
        ema_slow: float,
        hist_now: float,
        hist_prev: float,
        rsi_now: float,
    ) -> bool:
        """
        Return True when all three momentum conditions are satisfied for the
        given direction.  All three must pass — no partial credit here.

        LONG:
            EMA(8) > EMA(21)
            MACD histogram > 0 AND increasing
            RSI between rsi_long_lo and rsi_long_hi

        SHORT:
            EMA(8) < EMA(21)
            MACD histogram < 0 AND decreasing (more negative)
            RSI between rsi_short_lo and rsi_short_hi
        """
        if direction == Direction.LONG:
            ema_ok = ema_fast > ema_slow
            macd_ok = hist_now > 0 and hist_now > hist_prev
            rsi_ok = self.rsi_long_lo <= rsi_now <= self.rsi_long_hi
        else:
            ema_ok = ema_fast < ema_slow
            macd_ok = hist_now < 0 and hist_now < hist_prev
            rsi_ok = self.rsi_short_lo <= rsi_now <= self.rsi_short_hi

        return ema_ok and macd_ok and rsi_ok

    def _score_conviction(
        self,
        direction: Direction,
        momentum_aligned: bool,
        vol_ratio: float,
        adx_value: float,
        is_overlap: bool,
        atr_expanding: bool = False,
    ) -> float:
        """
        Conviction is signed: positive = bullish, negative = bearish.

        Score breakdown:
            0.40  base (strategy has edge at session open breakouts)
            0.15  all three momentum indicators aligned
            0.15  volume surge > volume_surge_mult  (institutional flow)
            0.10  ADX > adx_trend_threshold          (confirmed trend)
            0.10  ATR expanding (breakout confirmed by volatility expansion)
            0.10  London–NY overlap window            (highest liquidity)
        """
        score = 0.40

        if momentum_aligned:
            score += 0.15

        if vol_ratio >= self.volume_surge_mult:
            vol_bonus = min((vol_ratio - 1.0) / 2.0, 1.0) * 0.15
            score += vol_bonus

        if adx_value >= self.adx_trend_threshold:
            score += 0.10

        if atr_expanding:
            score += 0.10

        if is_overlap:
            score += 0.10

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    def _is_valid_trading_day(self, ts: pd.Timestamp) -> bool:
        """Return False on weekends and NFP Fridays."""
        # 5 = Saturday, 6 = Sunday
        if ts.dayofweek >= 5:
            return False
        if self.avoid_nfp and ts.dayofweek == 4 and ts.day <= 7:
            # First Friday of the month is NFP — skip to avoid whipsaw
            return False
        return True
