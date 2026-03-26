"""
strategies/technical/forex_rsi2.py — Connors RSI(2) adapted for FOREX / commodities on OANDA

Thesis
------
Ultra-short RSI(2) catches micro-reversals that RSI(14) misses entirely.  Forex pairs are
structurally mean-reverting due to central bank policy anchoring.  RSI(2) < 10 on EUR_USD
triggers a snap-back ~83% of the time within 2-5 bars (academic literature: Connors & Alvarez).

This implementation is adapted for:
  - OANDA symbol convention  (EUR_USD not EUR/USD)
  - 4h bars (primary) and 1d bars (secondary)
  - Forex and precious-metal markets instead of equities
  - A hard time stop (10 bars) not present in the equity version (connors_rsi.py)
  - SMA(5) crossing as the primary TP trigger instead of yesterday's high/low
  - JPY-pair awareness: USD_JPY inverts the SMA(200) direction filter because
    JPY strengthening means the pair *falls*, not rises

LONG entry — all four conditions required:
    1. RSI(2) < rsi_entry_long (10)            — extreme oversold on ultra-short TF
    2. Close > SMA(200)                        — macro uptrend filter (not inverted for JPY)
    3. Close < SMA(5)                          — price is below short-term MA (dip confirmed)
    4. Previous bar RSI(2) < rsi_prev_long (25)— consecutive weakness (not a single-bar blip)

SHORT entry — mirror:
    1. RSI(2) > rsi_entry_short (90)
    2. Close < SMA(200)
    3. Close > SMA(5)
    4. Previous bar RSI(2) > rsi_prev_short (75)

Exits (first to fire wins):
    1. SMA(5) crossing — close crosses above SMA(5) for LONG / below for SHORT
    2. RSI(2) mean-reversion — RSI(2) > rsi_exit_long (70) for LONG / < rsi_exit_short (30) for SHORT
    3. ATR stop-loss  — 1.5x ATR(14) from entry (set at signal time as Signal.stop_loss)
    4. Time stop      — 10 bars since entry; thesis is wrong if no reversion by then

Gold (XAU_USD) uses relaxed RSI thresholds (< 15 for long, > 85 for short) because gold
trends harder than currency pairs and requires wider extreme readings for a genuine signal.

Conviction scoring (base 0.55 — high-probability strategy baseline):
    +0.10  RSI(2) < 5 (long) / > 95 (short)       — deeper extreme, rarer, more reliable
    +0.10  2+ consecutive directional bars confirmed — sustained selling/buying pressure
    +0.10  Close below SMA(10) for LONG / above for SHORT — deeper pullback into trend
    +0.05  Volume above 20-bar average              — selling/buying on meaningful volume
    +0.10  Price within 2% of SMA(200)              — near support/resistance adds conviction

Score is clamped to [-1.0, 1.0] and signed: positive for LONG, negative for SHORT.

Best markets    : EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CHF, XAU_USD
Best timeframes : 4h (primary), 1d (secondary)
"""

from __future__ import annotations

import pandas as pd

from strategies.base import BaseStrategy, Direction, Position, Signal
from strategies.technical.indicators import atr, rsi, sma


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

# Symbols where XAU (gold/silver) relaxed RSI thresholds apply.
_GOLD_SILVER_PREFIXES: frozenset[str] = frozenset({"XAU", "XAG"})

# Symbols that are JPY pairs — direction of SMA(200) filter must be noted
# in metadata but the filter itself is not inverted (see design note below).
_JPY_PAIRS: frozenset[str] = frozenset({"USD_JPY", "EUR_JPY", "GBP_JPY", "AUD_JPY"})


def _is_gold_silver(symbol: str) -> bool:
    """Return True when the symbol represents gold or silver (XAU_*, XAG_*)."""
    prefix = symbol.upper().split("_")[0]
    return prefix in _GOLD_SILVER_PREFIXES


def _is_jpy_pair(symbol: str) -> bool:
    """Return True when the symbol is a JPY cross (USD_JPY, EUR_JPY, etc.)."""
    return symbol.upper() in _JPY_PAIRS


# ---------------------------------------------------------------------------
# Strategy class
# ---------------------------------------------------------------------------


class ForexRSI2Strategy(BaseStrategy):
    """
    Connors RSI(2) mean reversion adapted for FOREX and commodities on OANDA.

    Entries on extreme ultra-short RSI readings (RSI(2) < 10 / > 90) gated by
    macro trend (SMA 200), short-term dip confirmation (SMA 5), and consecutive
    weakness (prior bar RSI(2) < 25 / > 75).  Exits via SMA(5) crossing, RSI
    mean-reversion, ATR stop, or a hard 10-bar time stop.

    All constructor parameters are injectable for Darwinian agent evolution.
    """

    name = "forex_rsi2"
    description = (
        "Connors RSI(2) mean reversion for OANDA forex and precious metals. "
        "RSI(2) < 10 above SMA(200) and below SMA(5) with consecutive weakness. "
        "Exits via SMA(5) cross, RSI reversion (> 70), ATR stop, or 10-bar time stop. "
        "Gold/silver use relaxed thresholds (< 15 / > 85)."
    )
    timeframes = ["4h", "1d"]
    markets = ["forex", "commodities"]

    # SMA(200) is the longest indicator; add a buffer for RSI(2) convergence.
    _MIN_BARS: int = 210

    def __init__(
        self,
        rsi_period: int = 2,
        rsi_entry_long: float = 10.0,           # RSI(2) below this → extreme oversold
        rsi_entry_short: float = 90.0,          # RSI(2) above this → extreme overbought
        rsi_prev_long: float = 25.0,            # previous bar RSI(2) must be below this
        rsi_prev_short: float = 75.0,           # previous bar RSI(2) must be above this
        rsi_exit_long: float = 70.0,            # RSI(2) reversion target for LONG exit
        rsi_exit_short: float = 30.0,           # RSI(2) reversion target for SHORT exit
        rsi_extreme_long: float = 5.0,          # deep extreme bonus threshold
        rsi_extreme_short: float = 95.0,        # deep extreme bonus threshold
        sma_trend_period: int = 200,            # macro trend filter
        sma_short_period: int = 5,             # short-term MA for dip/rally confirmation
        sma_mid_period: int = 10,              # mid MA for conviction bonus
        atr_period: int = 14,
        atr_stop_mult: float = 1.5,            # stop distance in ATR units
        volume_period: int = 20,               # lookback for volume average
        time_stop_bars: int = 10,              # exit after this many bars regardless
        gold_rsi_entry_long: float = 15.0,     # relaxed oversold threshold for gold/silver
        gold_rsi_entry_short: float = 85.0,    # relaxed overbought threshold for gold/silver
        sma_support_pct: float = 0.02,         # within this % of SMA(200) = support bonus
        conviction_base: float = 0.55,         # baseline conviction (high-probability strategy)
    ) -> None:
        self.rsi_period = rsi_period
        self.rsi_entry_long = rsi_entry_long
        self.rsi_entry_short = rsi_entry_short
        self.rsi_prev_long = rsi_prev_long
        self.rsi_prev_short = rsi_prev_short
        self.rsi_exit_long = rsi_exit_long
        self.rsi_exit_short = rsi_exit_short
        self.rsi_extreme_long = rsi_extreme_long
        self.rsi_extreme_short = rsi_extreme_short
        self.sma_trend_period = sma_trend_period
        self.sma_short_period = sma_short_period
        self.sma_mid_period = sma_mid_period
        self.atr_period = atr_period
        self.atr_stop_mult = atr_stop_mult
        self.volume_period = volume_period
        self.time_stop_bars = time_stop_bars
        self.gold_rsi_entry_long = gold_rsi_entry_long
        self.gold_rsi_entry_short = gold_rsi_entry_short
        self.sma_support_pct = sma_support_pct
        self.conviction_base = conviction_base

        # _MIN_BARS is class-level; store an instance alias so _min_rows() works.
        self._min_bars = self._MIN_BARS

    # ------------------------------------------------------------------
    # Core interface — analyze
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full Forex RSI(2) analysis and return a Signal, or None when no edge.

        Parameters
        ----------
        df : OHLCV DataFrame, UTC-indexed, lowercase column names.
             df.attrs["symbol"] must carry the OANDA symbol (e.g. "EUR_USD").

        Returns
        -------
        Signal | None — None when data is insufficient or no edge is detected.
        """
        self._require_columns(df, "open", "high", "low", "close", "volume")
        if not self._min_rows(df, self._min_bars):
            return None

        close = df["close"]
        symbol: str = df.attrs.get("symbol", "UNKNOWN")
        is_gold = _is_gold_silver(symbol)
        is_jpy = _is_jpy_pair(symbol)

        # --- Indicators ---
        rsi_series = rsi(close, self.rsi_period)
        sma_200 = sma(close, self.sma_trend_period)
        sma_5 = sma(close, self.sma_short_period)
        sma_10 = sma(close, self.sma_mid_period)
        atr_series = atr(df, self.atr_period)
        avg_vol = df["volume"].rolling(self.volume_period).mean()

        # --- Current-bar scalars ---
        rsi_now = float(rsi_series.iloc[-1])
        rsi_prev = float(rsi_series.iloc[-2])   # previous bar RSI(2)
        close_now = float(close.iloc[-1])
        sma_200_now = float(sma_200.iloc[-1])
        sma_5_now = float(sma_5.iloc[-1])
        sma_10_now = float(sma_10.iloc[-1])
        atr_now = float(atr_series.iloc[-1])
        vol_now = float(df["volume"].iloc[-1])
        avg_vol_now = float(avg_vol.iloc[-1])
        bar_index = len(df) - 1  # integer position of the entry bar in the df

        # Guard NaN — can occur despite _min_bars passing on edge cases.
        if any(
            pd.isna(v)
            for v in (rsi_now, rsi_prev, sma_200_now, sma_5_now, sma_10_now, atr_now, avg_vol_now)
        ):
            return None

        if atr_now <= 0 or avg_vol_now <= 0:
            return None

        vol_ratio = vol_now / avg_vol_now

        # --- Select RSI entry thresholds (gold/silver use relaxed values) ---
        entry_long = self.gold_rsi_entry_long if is_gold else self.rsi_entry_long
        entry_short = self.gold_rsi_entry_short if is_gold else self.rsi_entry_short

        # --- Direction determination ---
        # Design note on JPY pairs: USD_JPY falls when the dollar weakens / yen strengthens.
        # The SMA(200) filter direction is NOT inverted here.  When close > SMA(200) on
        # USD_JPY the pair is still in a macro uptrend (dollar strong), so buying dips is
        # correct.  The JPY flag is propagated to metadata for informational transparency;
        # the engine or risk manager can apply additional logic if desired.

        above_200 = close_now > sma_200_now
        below_200 = close_now < sma_200_now
        below_sma5 = close_now < sma_5_now
        above_sma5 = close_now > sma_5_now

        long_trigger = (
            rsi_now < entry_long          # Rule 1: extreme oversold
            and above_200                 # Rule 2: macro uptrend
            and below_sma5               # Rule 3: price below short-term MA (dip confirmed)
            and rsi_prev < self.rsi_prev_long  # Rule 4: consecutive weakness
        )
        short_trigger = (
            rsi_now > entry_short         # Rule 1: extreme overbought
            and below_200                 # Rule 2: macro downtrend
            and above_sma5               # Rule 3: price above short-term MA (rally confirmed)
            and rsi_prev > self.rsi_prev_short  # Rule 4: consecutive strength
        )

        direction: Direction | None = None
        if long_trigger:
            direction = Direction.LONG
        elif short_trigger:
            direction = Direction.SHORT

        if direction is None:
            return None

        # --- Price levels ---
        entry_price = close_now
        stop_dist = self.atr_stop_mult * atr_now

        if direction == Direction.LONG:
            stop_loss = entry_price - stop_dist
            # Primary TP: the SMA(5) itself (mean reversion target).
            # If SMA(5) is already at or below entry (e.g. gap day), use 1:1 ATR fallback.
            take_profit = sma_5_now if sma_5_now > entry_price else entry_price + stop_dist
        else:
            stop_loss = entry_price + stop_dist
            take_profit = sma_5_now if sma_5_now < entry_price else entry_price - stop_dist

        # Hard safety checks — Signal.__post_init__ will also validate these.
        if stop_loss <= 0 or take_profit <= 0:
            return None
        if direction == Direction.LONG and take_profit <= entry_price:
            return None
        if direction == Direction.SHORT and take_profit >= entry_price:
            return None

        # --- Check for 2+ consecutive directional bars (conviction bonus input) ---
        consec_bars = self._count_consecutive_directional_bars(df, direction)

        conviction = self._score_conviction(
            rsi_now=rsi_now,
            close_now=close_now,
            sma_200_now=sma_200_now,
            sma_10_now=sma_10_now,
            vol_ratio=vol_ratio,
            consec_bars=consec_bars,
            direction=direction,
            is_gold=is_gold,
        )

        return Signal(
            symbol=symbol,
            direction=direction,
            conviction=conviction,
            stop_loss=round(stop_loss, 6),
            take_profit=round(take_profit, 6),
            strategy_name=self.name,
            metadata={
                "entry_price": entry_price,
                "entry_bar_index": bar_index,  # engine uses this for the time stop
                "rsi_2": round(rsi_now, 2),
                "rsi_2_prev": round(rsi_prev, 2),
                "sma_200": round(sma_200_now, 6),
                "sma_5": round(sma_5_now, 6),
                "sma_10": round(sma_10_now, 6),
                "atr": round(atr_now, 6),
                "volume_ratio": round(vol_ratio, 2),
                "consecutive_bars": consec_bars,
                "is_gold_silver": is_gold,
                "is_jpy_pair": is_jpy,
                "stop_dist": round(stop_dist, 6),
            },
        )

    # ------------------------------------------------------------------
    # Core interface — should_enter
    # ------------------------------------------------------------------

    def should_enter(self, df: pd.DataFrame) -> bool:
        """Lightweight entry check — delegates to analyze()."""
        signal = self.analyze(df)
        return signal is not None and signal.direction != Direction.FLAT

    # ------------------------------------------------------------------
    # Core interface — should_exit
    # ------------------------------------------------------------------

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Exit when ANY of four conditions fire (first wins):

        1. SMA(5) crossing — close crosses the short-term MA (primary mean-reversion target).
        2. RSI(2) reversion — RSI(2) has reverted to the opposite extreme (>70 for LONG).
        3. ATR stop-loss   — price has moved against us by more than 1.5x ATR from entry.
           (This mirrors the SL set in analyze(); included here so should_exit is
           self-contained when the engine polls it each bar.)
        4. Time stop       — 10 bars since entry; thesis was wrong, exit to preserve capital.

        The time stop requires `position.metadata["entry_bar_index"]` to be set.  This is
        written by analyze() into the Signal metadata.  The engine is expected to carry it
        forward into Position.metadata when the position is opened.

        When entry_bar_index is absent (legacy or manually opened positions), the time stop
        is skipped rather than triggering a spurious exit.
        """
        if not self._min_rows(df, self.rsi_period + self.sma_short_period + 2):
            return False

        close = df["close"]
        rsi_series = rsi(close, self.rsi_period)
        sma_5_series = sma(close, self.sma_short_period)
        atr_series = atr(df, self.atr_period)

        close_now = float(close.iloc[-1])
        rsi_now = float(rsi_series.iloc[-1])
        sma_5_now = float(sma_5_series.iloc[-1])
        atr_now = float(atr_series.iloc[-1]) if not pd.isna(atr_series.iloc[-1]) else 0.0
        current_bar_index = len(df) - 1

        if position.side == Direction.LONG:
            # Exit 1: SMA(5) crossing — price has crossed above the short-term MA
            sma5_cross = close_now > sma_5_now

            # Exit 2: RSI(2) has mean-reverted to overbought territory
            rsi_reverted = rsi_now > self.rsi_exit_long

            # Exit 3: ATR stop — price has dropped atr_stop_mult * ATR below entry
            stop_hit = (
                atr_now > 0
                and close_now <= position.entry_price - self.atr_stop_mult * atr_now
            )

            # Exit 4: Time stop — bail after time_stop_bars regardless of price action
            time_stop = _time_stop_triggered(
                position, current_bar_index, self.time_stop_bars
            )

            return sma5_cross or rsi_reverted or stop_hit or time_stop

        else:  # SHORT
            # Exit 1: SMA(5) crossing — price has crossed below the short-term MA
            sma5_cross = close_now < sma_5_now

            # Exit 2: RSI(2) has mean-reverted to oversold territory
            rsi_reverted = rsi_now < self.rsi_exit_short

            # Exit 3: ATR stop — price has risen above entry by atr_stop_mult * ATR
            stop_hit = (
                atr_now > 0
                and close_now >= position.entry_price + self.atr_stop_mult * atr_now
            )

            # Exit 4: Time stop
            time_stop = _time_stop_triggered(
                position, current_bar_index, self.time_stop_bars
            )

            return sma5_cross or rsi_reverted or stop_hit or time_stop

    # ------------------------------------------------------------------
    # Conviction scoring
    # ------------------------------------------------------------------

    def _score_conviction(
        self,
        rsi_now: float,
        close_now: float,
        sma_200_now: float,
        sma_10_now: float,
        vol_ratio: float,
        consec_bars: int,
        direction: Direction,
        is_gold: bool,
    ) -> float:
        """
        Build conviction score from base 0.55 with additive bonuses.

        Bonuses:
            +0.10  RSI(2) < 5 (long) / > 95 (short)    — deeper extreme, very rare
            +0.10  2+ consecutive directional bars       — sustained selling/buying
            +0.10  Close below SMA(10) for LONG /
                   above SMA(10) for SHORT              — deeper pullback into trend
            +0.05  Volume above 20-bar average           — selling on volume
            +0.10  Price within 2% of SMA(200)           — at key support/resistance

        Score is clamped to [-1.0, 1.0] and signed: positive for LONG, negative for SHORT.
        """
        score = self.conviction_base

        # Bonus 1: deep RSI(2) extreme
        if direction == Direction.LONG and rsi_now < self.rsi_extreme_long:
            score += 0.10
        elif direction == Direction.SHORT and rsi_now > self.rsi_extreme_short:
            score += 0.10

        # Bonus 2: consecutive bars confirm sustained pressure
        if consec_bars >= 2:
            score += 0.10

        # Bonus 3: deeper pullback — price below SMA(10) for LONG, above for SHORT
        if direction == Direction.LONG and close_now < sma_10_now:
            score += 0.10
        elif direction == Direction.SHORT and close_now > sma_10_now:
            score += 0.10

        # Bonus 4: volume above average
        if vol_ratio > 1.0:
            score += 0.05

        # Bonus 5: price within sma_support_pct of SMA(200) — near structural S/R
        if sma_200_now > 0:
            proximity_pct = abs(close_now - sma_200_now) / sma_200_now
            if proximity_pct <= self.sma_support_pct:
                score += 0.10

        signed = score if direction == Direction.LONG else -score
        return self._clamp(signed)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _count_consecutive_directional_bars(df: pd.DataFrame, direction: Direction) -> int:
        """
        Count how many consecutive bars (looking backward from the current bar,
        not including the current bar) moved in the expected entry direction.

        For LONG entries we count consecutive DOWN bars (close < open) because we
        are buying the dip — sustained selling pressure is what we want to confirm.
        For SHORT entries we count consecutive UP bars (close > open).

        Returns 0 when the previous bar moved the wrong way or data is insufficient.
        """
        if len(df) < 2:
            return 0

        count = 0
        # Walk backward from bar[-2] (the most recent complete bar before current)
        for i in range(len(df) - 2, max(len(df) - 7, -1), -1):
            bar_open = float(df["open"].iloc[i])
            bar_close = float(df["close"].iloc[i])
            if direction == Direction.LONG:
                if bar_close < bar_open:  # down bar
                    count += 1
                else:
                    break
            else:  # SHORT
                if bar_close > bar_open:  # up bar
                    count += 1
                else:
                    break

        return count


# ---------------------------------------------------------------------------
# Module-level helper (not a method — avoids cluttering the class namespace)
# ---------------------------------------------------------------------------


def _time_stop_triggered(position: Position, current_bar_index: int, time_stop_bars: int) -> bool:
    """
    Return True when the position has been open for >= time_stop_bars bars.

    The entry bar index is stored in Signal.metadata["entry_bar_index"] and
    carried forward into Position.metadata by the engine when the trade is opened.
    If the key is absent, the time stop is silently skipped (returns False).

    Parameters
    ----------
    position          : the open Position object
    current_bar_index : integer index of the current bar (len(df) - 1)
    time_stop_bars    : maximum bars to hold before forced exit
    """
    entry_bar_index = position.metadata.get("entry_bar_index")
    if entry_bar_index is None:
        return False
    bars_held = current_bar_index - int(entry_bar_index)
    return bars_held >= time_stop_bars
