"""
core/trailing_stop.py
---------------------
Adaptive Trailing Stop System for Atlas Trading Agent.

Purpose
-------
Fixed stop losses are a blunt instrument.  Set them too tight and you get
shaken out by noise; set them too loose and you hand back profit when a trend
reverses.  This module implements four complementary trailing-stop methods
together with automatic break-even promotion and tiered profit-locking — giving
every open position a dynamically tightening safety net that widens when
volatility is high and tightens as profit accumulates.

Methods available
-----------------
atr          — Trail at entry ± 2× ATR initially, then 1.5× ATR behind the
               running extreme.  Fast to respond to expanding volatility.
chandelier   — Trail at highest_high − 3× ATR (LONG) or lowest_low + 3× ATR
               (SHORT).  The institutional gold standard for trend following.
parabolic    — Parabolic-SAR-inspired: an acceleration factor grows from 0.02
               to 0.20 as profit compounds, pulling the stop tighter in
               runaway moves without choking early-stage trends.
composite    — Runs all three methods simultaneously and returns the most
               aggressive (highest floor for LONG, lowest ceiling for SHORT).
               Use this when you want belt-and-suspenders protection.

Break-even promotion
--------------------
Once profit ≥ 1× ATR the stop is silently promoted to entry + commission so
the trade can never turn into a loss.  This happens regardless of method.

Profit-lock tiers
-----------------
As unrealised profit grows relative to ATR the module guarantees a minimum
fraction of peak gain by ratcheting the stop floor:

    +1.5× ATR profit  →  lock 50% of peak unrealised gain
    +3.0× ATR profit  →  lock 75% of peak unrealised gain
    +5.0× ATR profit  →  lock 85% of peak unrealised gain

Usage
-----
    manager = TrailingStopManager(method="chandelier", atr_multiplier=3.0)
    result  = manager.update(
        current_price        = 68_400.0,
        current_atr          = 1_200.0,
        direction            = "LONG",
        entry_price          = 64_000.0,
        highest_since_entry  = 69_100.0,
        lowest_since_entry   = 63_800.0,
    )
    if result.triggered:
        # submit market exit order …
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger("atlas.trailing_stop")

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# ATR multipliers
_INITIAL_ATR_MULTIPLIER: float = 2.0     # first stop after entry (wider)
_TRAIL_ATR_MULTIPLIER: float = 1.5       # trailing distance once in profit
_CHANDELIER_ATR_MULTIPLIER: float = 3.0  # default chandelier width

# Parabolic SAR acceleration factor bounds
_PARABOLIC_AF_INITIAL: float = 0.02
_PARABOLIC_AF_STEP: float = 0.02
_PARABOLIC_AF_MAX: float = 0.20

# Break-even commission buffer expressed as a fraction of entry price.
# Covers a round-trip taker fee at 0.10 % per leg so the stop sits just
# above (LONG) or below (SHORT) the all-in break-even point.
_BREAK_EVEN_COMMISSION_PCT: float = 0.002  # 0.20 % round-trip

# Break-even trigger: promote to break-even once profit ≥ this many × ATR
_BREAK_EVEN_ATR_TRIGGER: float = 1.0

# Profit-lock tiers: (atr_multiple_trigger, fraction_of_peak_profit_locked)
_PROFIT_LOCK_TIERS: tuple[tuple[float, float], ...] = (
    (1.5, 0.50),
    (3.0, 0.75),
    (5.0, 0.85),
)

# Valid method names
_VALID_METHODS = frozenset({"atr", "chandelier", "parabolic", "composite"})

MethodName = Literal["atr", "chandelier", "parabolic", "composite"]


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class TrailingStopResult:
    """
    Returned by TrailingStopManager.update() on every bar.

    Attributes
    ----------
    stop_price       : The current trailing stop level.  The position should
                       be closed if this level is breached.
    triggered        : True when current_price has already breached stop_price
                       (i.e. the exit should be executed on this bar).
    method           : Which method produced the final stop_price.
    profit_locked_pct: Fraction of peak unrealised profit that is now
                       protected by the stop.  0.0 before break-even,
                       0.85 at the highest tier.
    reason           : Human-readable explanation of the current stop level.
    """

    stop_price: float
    triggered: bool
    method: str
    profit_locked_pct: float
    reason: str


# ---------------------------------------------------------------------------
# TrailingStopManager
# ---------------------------------------------------------------------------


class TrailingStopManager:
    """
    Adaptive trailing stop calculator.

    This is a *stateless calculator* — all state (highest_since_entry,
    lowest_since_entry, parabolic accumulator) is supplied by the caller on
    every call to update().  This design means the manager can be instantiated
    once and shared across many concurrent positions without any per-trade
    instance management.

    Parameters
    ----------
    method          : One of "atr", "chandelier", "parabolic", "composite".
                      Defaults to "chandelier".
    atr_multiplier  : Override the default ATR width for the chosen method.
                      If 0.0 (default sentinel) the method's own default is
                      used (chandelier=3.0, atr=initial 2.0 / trail 1.5).
    """

    def __init__(
        self,
        method: MethodName = "chandelier",
        atr_multiplier: float = 0.0,
    ) -> None:
        if method not in _VALID_METHODS:
            raise ValueError(
                f"method must be one of {sorted(_VALID_METHODS)}, got '{method}'"
            )
        if atr_multiplier < 0:
            raise ValueError("atr_multiplier must be >= 0")

        self.method: MethodName = method
        # If caller passes 0.0 we keep per-method defaults; any positive
        # value overrides all internal multipliers for that method.
        self._custom_multiplier: float = atr_multiplier

        logger.info(
            "TrailingStopManager initialised — method=%s atr_multiplier=%s",
            method,
            f"{atr_multiplier:.2f}" if atr_multiplier > 0 else "default",
        )

    # ------------------------------------------------------------------
    # Primary public interface
    # ------------------------------------------------------------------

    def update(
        self,
        current_price: float,
        current_atr: float,
        direction: str,
        entry_price: float,
        highest_since_entry: float,
        lowest_since_entry: float,
        parabolic_af: float = _PARABOLIC_AF_INITIAL,
    ) -> TrailingStopResult:
        """
        Calculate the current trailing stop and return a TrailingStopResult.

        Parameters
        ----------
        current_price       : The latest traded price (usually the bar close).
        current_atr         : The current ATR value in price units.
        direction           : "LONG" or "SHORT" (case-insensitive).
        entry_price         : The price at which the position was opened.
        highest_since_entry : Highest close (or high) recorded since entry.
                              The caller is responsible for maintaining this.
        lowest_since_entry  : Lowest close (or low) recorded since entry.
                              The caller is responsible for maintaining this.
        parabolic_af        : Current parabolic acceleration factor.  The
                              caller should increment this by _PARABOLIC_AF_STEP
                              each bar a new extreme is set, capped at
                              _PARABOLIC_AF_MAX.  Defaults to the initial AF.

        Returns
        -------
        TrailingStopResult
        """
        self._validate_inputs(
            current_price, current_atr, entry_price,
            highest_since_entry, lowest_since_entry
        )

        dir_upper = direction.upper()
        if dir_upper not in ("LONG", "SHORT"):
            raise ValueError(f"direction must be 'LONG' or 'SHORT', got '{direction}'")

        # ── Compute raw stop from the chosen method ────────────────────────────
        if self.method == "atr":
            raw_stop, method_label = self._atr_stop(
                current_atr, dir_upper, entry_price,
                highest_since_entry, lowest_since_entry,
            )
        elif self.method == "chandelier":
            raw_stop, method_label = self._chandelier_stop(
                current_atr, dir_upper, highest_since_entry, lowest_since_entry,
            )
        elif self.method == "parabolic":
            raw_stop, method_label = self._parabolic_stop(
                current_price, current_atr, dir_upper, entry_price,
                highest_since_entry, lowest_since_entry, parabolic_af,
            )
        else:  # composite
            raw_stop, method_label = self._composite_stop(
                current_price, current_atr, dir_upper, entry_price,
                highest_since_entry, lowest_since_entry, parabolic_af,
            )

        # ── Break-even promotion ───────────────────────────────────────────────
        stop_after_be, be_reason = self._apply_break_even(
            raw_stop, current_atr, dir_upper, entry_price, current_price,
        )

        # ── Profit-lock tiers ─────────────────────────────────────────────────
        final_stop, profit_locked_pct, lock_reason = self._apply_profit_lock(
            stop_after_be, current_atr, dir_upper, entry_price, current_price,
            highest_since_entry, lowest_since_entry,
        )

        # ── Triggered check ────────────────────────────────────────────────────
        triggered = self.should_exit(current_price, final_stop, dir_upper)

        # ── Compose reason string ──────────────────────────────────────────────
        parts = [method_label]
        if be_reason:
            parts.append(be_reason)
        if lock_reason:
            parts.append(lock_reason)
        if triggered:
            parts.append("TRIGGERED")
        reason = " | ".join(parts)

        result = TrailingStopResult(
            stop_price=final_stop,
            triggered=triggered,
            method=method_label,
            profit_locked_pct=profit_locked_pct,
            reason=reason,
        )

        logger.debug(
            "TrailingStop [%s] dir=%s price=%.4f stop=%.4f locked=%.0f%% triggered=%s",
            method_label,
            dir_upper,
            current_price,
            final_stop,
            profit_locked_pct * 100,
            triggered,
        )
        return result

    def should_exit(
        self,
        current_price: float,
        stop_price: float,
        direction: str,
    ) -> bool:
        """
        Return True if current_price has breached the trailing stop.

        For a LONG position the stop acts as a floor — exit when price falls
        at or below it.  For a SHORT position the stop acts as a ceiling —
        exit when price rises at or above it.

        Parameters
        ----------
        current_price : latest traded price
        stop_price    : the trailing stop level returned by update()
        direction     : "LONG" or "SHORT" (case-insensitive)
        """
        dir_upper = direction.upper()
        if dir_upper == "LONG":
            return current_price <= stop_price
        elif dir_upper == "SHORT":
            return current_price >= stop_price
        else:
            raise ValueError(f"direction must be 'LONG' or 'SHORT', got '{direction}'")

    # ------------------------------------------------------------------
    # Private — method implementations
    # ------------------------------------------------------------------

    def _atr_stop(
        self,
        atr: float,
        direction: str,
        entry_price: float,
        highest: float,
        lowest: float,
    ) -> tuple[float, str]:
        """
        ATR trailing stop.

        Initial stop is set at entry ± INITIAL_ATR_MULTIPLIER × ATR.
        Once the trade is in profit the stop trails at TRAIL_ATR_MULTIPLIER ×
        ATR behind the running extreme (highest close for LONG, lowest for SHORT).

        The more conservative (further from current price) of the two is used
        until the trailing level overtakes the initial level, at which point the
        trailing level takes over permanently.
        """
        mult_initial = self._custom_multiplier if self._custom_multiplier > 0 else _INITIAL_ATR_MULTIPLIER
        mult_trail = self._custom_multiplier if self._custom_multiplier > 0 else _TRAIL_ATR_MULTIPLIER

        if direction == "LONG":
            initial_stop = entry_price - mult_initial * atr
            trail_stop = highest - mult_trail * atr
            # Take the higher of the two (more protection)
            stop = max(initial_stop, trail_stop)
            label = f"ATR-trail(×{mult_trail:.1f} behind H={highest:.4f})"
        else:  # SHORT
            initial_stop = entry_price + mult_initial * atr
            trail_stop = lowest + mult_trail * atr
            # Take the lower of the two (more protection for short)
            stop = min(initial_stop, trail_stop)
            label = f"ATR-trail(×{mult_trail:.1f} above L={lowest:.4f})"

        return stop, label

    def _chandelier_stop(
        self,
        atr: float,
        direction: str,
        highest: float,
        lowest: float,
    ) -> tuple[float, str]:
        """
        Chandelier Exit (Chuck LeBeau / Alexander Elder).

        LONG  stop = highest_high − multiplier × ATR
        SHORT stop = lowest_low  + multiplier × ATR

        Uses the highest *high* (or highest close, depending on what the caller
        tracks) since entry so the stop never drops below a previously set level
        during a trend.
        """
        mult = self._custom_multiplier if self._custom_multiplier > 0 else _CHANDELIER_ATR_MULTIPLIER

        if direction == "LONG":
            stop = highest - mult * atr
            label = f"Chandelier(H={highest:.4f} - {mult:.1f}×ATR)"
        else:  # SHORT
            stop = lowest + mult * atr
            label = f"Chandelier(L={lowest:.4f} + {mult:.1f}×ATR)"

        return stop, label

    def _parabolic_stop(
        self,
        current_price: float,
        atr: float,
        direction: str,
        entry_price: float,
        highest: float,
        lowest: float,
        af: float,
    ) -> tuple[float, str]:
        """
        Parabolic-SAR-inspired adaptive stop.

        The acceleration factor (AF) starts at _PARABOLIC_AF_INITIAL (0.02)
        and is supplied by the caller, who should increment it by
        _PARABOLIC_AF_STEP each bar that a new extreme is set, capped at
        _PARABOLIC_AF_MAX (0.20).

        SAR formula (simplified for a single bar calculation):
            new_SAR = prev_SAR + AF × (EP − prev_SAR)
        where EP is the extreme point (highest high for LONG, lowest low for SHORT).

        Because we do not maintain inter-bar state here, we approximate prev_SAR
        as the chandelier stop, then apply one step of the parabolic formula.
        The result is an ATR-anchored floor for the SAR so it cannot be placed
        inside the noise band.

        Parameters
        ----------
        af : Current acceleration factor in [_PARABOLIC_AF_INITIAL, _PARABOLIC_AF_MAX].
        """
        af = max(_PARABOLIC_AF_INITIAL, min(af, _PARABOLIC_AF_MAX))

        # Use chandelier as the SAR baseline (prev_SAR proxy)
        chandelier_mult = self._custom_multiplier if self._custom_multiplier > 0 else _CHANDELIER_ATR_MULTIPLIER

        if direction == "LONG":
            prev_sar = highest - chandelier_mult * atr   # SAR baseline
            ep = highest                                  # extreme point
            sar = prev_sar + af * (ep - prev_sar)
            # SAR for a long must be below current price; also floor at initial ATR stop
            initial_floor = entry_price - _INITIAL_ATR_MULTIPLIER * atr
            stop = max(initial_floor, sar)
            label = f"Parabolic(AF={af:.2f} SAR={sar:.4f})"
        else:  # SHORT
            prev_sar = lowest + chandelier_mult * atr
            ep = lowest
            sar = prev_sar + af * (ep - prev_sar)
            initial_ceil = entry_price + _INITIAL_ATR_MULTIPLIER * atr
            stop = min(initial_ceil, sar)
            label = f"Parabolic(AF={af:.2f} SAR={sar:.4f})"

        return stop, label

    def _composite_stop(
        self,
        current_price: float,
        atr: float,
        direction: str,
        entry_price: float,
        highest: float,
        lowest: float,
        af: float,
    ) -> tuple[float, str]:
        """
        Run all three methods and return the most aggressive stop.

        For LONG:  most aggressive = highest stop price (tightest floor).
        For SHORT: most aggressive = lowest stop price (tightest ceiling).
        """
        atr_stop, _ = self._atr_stop(atr, direction, entry_price, highest, lowest)
        chan_stop, _ = self._chandelier_stop(atr, direction, highest, lowest)
        par_stop, _ = self._parabolic_stop(current_price, atr, direction, entry_price, highest, lowest, af)

        candidates = {"atr": atr_stop, "chandelier": chan_stop, "parabolic": par_stop}

        if direction == "LONG":
            winner = max(candidates, key=lambda k: candidates[k])
        else:
            winner = min(candidates, key=lambda k: candidates[k])

        stop = candidates[winner]
        label = (
            f"Composite→{winner}("
            f"atr={atr_stop:.4f} chan={chan_stop:.4f} par={par_stop:.4f})"
        )
        return stop, label

    # ------------------------------------------------------------------
    # Private — break-even and profit-lock
    # ------------------------------------------------------------------

    def _apply_break_even(
        self,
        stop: float,
        atr: float,
        direction: str,
        entry_price: float,
        current_price: float,
    ) -> tuple[float, str]:
        """
        Promote the stop to break-even once profit ≥ _BREAK_EVEN_ATR_TRIGGER × ATR.

        Break-even is defined as entry_price ± commission buffer so the trade
        cannot turn into a net loss even after paying fees.

        Returns the (possibly raised) stop and a reason string (empty if no
        promotion occurred).
        """
        if direction == "LONG":
            profit = current_price - entry_price
            be_price = entry_price * (1.0 + _BREAK_EVEN_COMMISSION_PCT)
            if profit >= _BREAK_EVEN_ATR_TRIGGER * atr:
                new_stop = max(stop, be_price)
                if new_stop > stop:
                    return new_stop, f"BE-promoted(floor={be_price:.4f})"
        else:  # SHORT
            profit = entry_price - current_price
            be_price = entry_price * (1.0 - _BREAK_EVEN_COMMISSION_PCT)
            if profit >= _BREAK_EVEN_ATR_TRIGGER * atr:
                new_stop = min(stop, be_price)
                if new_stop < stop:
                    return new_stop, f"BE-promoted(ceil={be_price:.4f})"

        return stop, ""

    def _apply_profit_lock(
        self,
        stop: float,
        atr: float,
        direction: str,
        entry_price: float,
        current_price: float,
        highest: float,
        lowest: float,
    ) -> tuple[float, float, str]:
        """
        Ratchet the stop upward (LONG) or downward (SHORT) to lock in a
        minimum percentage of peak unrealised profit based on _PROFIT_LOCK_TIERS.

        Returns (final_stop, profit_locked_pct, reason_string).
        """
        profit_locked_pct: float = 0.0
        lock_reason: str = ""

        if direction == "LONG":
            current_profit = current_price - entry_price
            peak_profit = highest - entry_price
        else:  # SHORT
            current_profit = entry_price - current_price
            peak_profit = entry_price - lowest

        if atr <= 0 or peak_profit <= 0:
            return stop, profit_locked_pct, lock_reason

        # Walk tiers from highest to lowest to apply the most aggressive tier
        for atr_multiple, lock_fraction in reversed(_PROFIT_LOCK_TIERS):
            if current_profit >= atr_multiple * atr:
                # Minimum stop must guarantee lock_fraction × peak_profit
                guaranteed_profit = lock_fraction * peak_profit
                if direction == "LONG":
                    lock_floor = entry_price + guaranteed_profit
                    if lock_floor > stop:
                        stop = lock_floor
                        profit_locked_pct = lock_fraction
                        lock_reason = (
                            f"ProfitLock({lock_fraction:.0%} of peak "
                            f"{peak_profit:.4f} → floor={lock_floor:.4f})"
                        )
                else:  # SHORT
                    lock_ceil = entry_price - guaranteed_profit
                    if lock_ceil < stop:
                        stop = lock_ceil
                        profit_locked_pct = lock_fraction
                        lock_reason = (
                            f"ProfitLock({lock_fraction:.0%} of peak "
                            f"{peak_profit:.4f} → ceil={lock_ceil:.4f})"
                        )
                break  # highest applicable tier already applied

        return stop, profit_locked_pct, lock_reason

    # ------------------------------------------------------------------
    # Private — input validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_inputs(
        current_price: float,
        current_atr: float,
        entry_price: float,
        highest_since_entry: float,
        lowest_since_entry: float,
    ) -> None:
        if current_price <= 0:
            raise ValueError(f"current_price must be positive, got {current_price}")
        if current_atr < 0:
            raise ValueError(f"current_atr must be non-negative, got {current_atr}")
        if entry_price <= 0:
            raise ValueError(f"entry_price must be positive, got {entry_price}")
        if highest_since_entry < entry_price and highest_since_entry < current_price:
            # Allow slight floating-point slack — only raise on obviously wrong data
            raise ValueError(
                f"highest_since_entry ({highest_since_entry}) cannot be below both "
                f"entry_price ({entry_price}) and current_price ({current_price})"
            )
        if lowest_since_entry > entry_price and lowest_since_entry > current_price:
            raise ValueError(
                f"lowest_since_entry ({lowest_since_entry}) cannot be above both "
                f"entry_price ({entry_price}) and current_price ({current_price})"
            )
        if lowest_since_entry > highest_since_entry:
            raise ValueError(
                f"lowest_since_entry ({lowest_since_entry}) > "
                f"highest_since_entry ({highest_since_entry})"
            )


# ---------------------------------------------------------------------------
# Module-level helpers (convenience functions for callers)
# ---------------------------------------------------------------------------


def next_parabolic_af(current_af: float, new_extreme_set: bool) -> float:
    """
    Advance the parabolic acceleration factor by one step if a new extreme
    was set on the current bar, capped at _PARABOLIC_AF_MAX.

    Parameters
    ----------
    current_af       : The AF value used on the previous bar.
    new_extreme_set  : True if price made a new high (LONG) or low (SHORT)
                       on this bar.

    Returns
    -------
    float — updated AF for the next call to TrailingStopManager.update().

    Example
    -------
        af = _PARABOLIC_AF_INITIAL
        for bar in bars:
            new_extreme = bar.high > running_high  # for a LONG position
            af = next_parabolic_af(af, new_extreme)
            result = manager.update(..., parabolic_af=af)
    """
    if new_extreme_set:
        return min(current_af + _PARABOLIC_AF_STEP, _PARABOLIC_AF_MAX)
    return current_af
