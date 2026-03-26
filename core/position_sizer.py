"""
core/position_sizer.py
-----------------------
Position Sizing Engine for Atlas Trading Agent.

Implements Half-Kelly Criterion with conviction scaling, ATR-based stop loss
calculation, and fee-aware size adjustment.

Half-Kelly formula
------------------
    kelly_fraction   = (win_rate * rr - (1 - win_rate)) / rr
    position_pct     = kelly_fraction * 0.5          # half-Kelly
    conviction_size  = position_pct * |conviction|   # conviction scaling

Where:
    rr       = avg_win / avg_loss ratio
    win_rate = fraction of historical trades that were winners

Minimum conviction threshold: 0.3 — any signal below this is flat-out rejected
regardless of Kelly output.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("atlas.sizer")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_MIN_CONVICTION: float = 0.15  # Lowered from 0.3 — micro-account needs more trade opportunities
_ATR_SL_MULTIPLIER_LONG: float = 1.5   # entry - 1.5 × ATR for LONG stop
_ATR_SL_MULTIPLIER_SHORT: float = 1.5  # entry + 1.5 × ATR for SHORT stop
_DEFAULT_RR_RATIO: float = 3.0          # risk-reward ratio used for TP calculation
_MAKER_FEE_PCT: float = 0.001           # 0.10 %
_TAKER_FEE_PCT: float = 0.001           # 0.10 %
_MAX_KELLY_FRACTION: float = 0.25       # cap full Kelly at 25% before halving
_SHORT_DIRECTION_DISCOUNT: float = 0.85  # 15% size reduction for shorts (higher tail risk)
_REGIME_SIZE_FLOOR: float = 0.3          # minimum regime multiplier


# ---------------------------------------------------------------------------
# PositionSizer
# ---------------------------------------------------------------------------


class PositionSizer:
    """
    Calculates risk-adjusted position sizes for every trade.

    Usage
    -----
    sizer = PositionSizer(maker_fee_pct=0.001, taker_fee_pct=0.001)
    size  = sizer.calculate_position_size(
        portfolio_value = 10_000,
        direction       = "LONG",
        entry_price     = 64_000,
        stop_loss       = 62_500,
        conviction      = 0.75,
        avg_win_rate    = 0.55,
        avg_rr          = 2.0,
    )

    Parameters
    ----------
    maker_fee_pct : maker fee expressed as a decimal (default 0.001 = 0.1 %)
    taker_fee_pct : taker fee expressed as a decimal (default 0.001 = 0.1 %)
    """

    def __init__(
        self,
        maker_fee_pct: float = _MAKER_FEE_PCT,
        taker_fee_pct: float = _TAKER_FEE_PCT,
    ) -> None:
        self.maker_fee_pct = maker_fee_pct
        self.taker_fee_pct = taker_fee_pct

    # ------------------------------------------------------------------
    # Primary public methods
    # ------------------------------------------------------------------

    def calculate_position_size(
        self,
        portfolio_value: float,
        direction: str,
        entry_price: float,
        stop_loss: float,
        conviction: float,
        avg_win_rate: float,
        avg_rr: float,
        use_market_order: bool = True,
        regime_multiplier: float = 1.0,
        sentiment_multiplier: float = 1.0,
    ) -> float:
        """
        Return the recommended position size in base-asset units.

        The calculation pipeline:
        1. Reject if |conviction| < MIN_CONVICTION.
        2. Compute the half-Kelly fraction from win_rate and avg_rr.
        3. Scale by |conviction|.
        4. Apply direction discount (shorts get 15% reduction for tail risk).
        5. Apply regime and sentiment multipliers.
        6. Compute the max units given the portfolio allocation.
        7. Cap by the risk-based size (stop-loss distance × portfolio risk budget).
        8. Subtract estimated entry + exit fees so the true risk stays within budget.

        Parameters
        ----------
        portfolio_value      : total equity in quote currency
        direction            : "LONG" or "SHORT"
        entry_price          : expected fill price in quote currency
        stop_loss            : stop-loss price in quote currency
        conviction           : signal conviction in [-1.0, 1.0]; sign encodes direction
        avg_win_rate         : fraction of historical trades that were winners [0, 1]
        avg_rr               : average win/loss ratio of historical trades (e.g. 2.0)
        use_market_order     : True ⇒ taker fee; False ⇒ maker fee
        regime_multiplier    : 0.0–1.0 from RegimeDetector.size_multiplier()
        sentiment_multiplier : 0.0–1.0 from SentimentEngine.risk_modifier

        Returns
        -------
        float — recommended size in base units (0.0 if trade should be skipped)
        """
        if portfolio_value <= 0:
            logger.warning("portfolio_value must be positive, got %.2f", portfolio_value)
            return 0.0

        if entry_price <= 0 or stop_loss <= 0:
            logger.warning("entry_price and stop_loss must be positive")
            return 0.0

        if abs(conviction) < _MIN_CONVICTION:
            logger.debug(
                "Conviction %.3f below minimum threshold %.3f — size=0",
                conviction,
                _MIN_CONVICTION,
            )
            return 0.0

        # ── Half-Kelly fraction ────────────────────────────────────────────────
        kelly = self._half_kelly(avg_win_rate, avg_rr)
        if kelly <= 0:
            logger.debug("Half-Kelly fraction ≤ 0 (%.4f) — negative expected value — size=0", kelly)
            return 0.0

        # ── Conviction scaling ─────────────────────────────────────────────────
        allocation_pct = kelly * abs(conviction)

        # ── Direction discount — shorts carry higher tail risk ─────────────────
        dir_upper = direction.upper() if isinstance(direction, str) else "LONG"
        direction_scalar = _SHORT_DIRECTION_DISCOUNT if dir_upper == "SHORT" else 1.0
        allocation_pct *= direction_scalar

        # ── Regime and sentiment scaling ───────────────────────────────────────
        regime_mult = max(_REGIME_SIZE_FLOOR, min(1.0, regime_multiplier))
        sentiment_mult = max(0.1, min(1.0, sentiment_multiplier))
        allocation_pct *= regime_mult * sentiment_mult

        allocation_value = portfolio_value * allocation_pct

        # ── Units from allocation ──────────────────────────────────────────────
        units_from_allocation = allocation_value / entry_price

        # ── Units from risk budget (stop-distance sizing) ──────────────────────
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance == 0:
            logger.warning("entry_price == stop_loss, cannot size position")
            return 0.0

        # Per-trade risk budget: scale with account size.
        # Micro accounts (< $500) need 2.5% risk to meet exchange minimums.
        # Standard accounts use 1% (conservative).
        if portfolio_value < 500:
            risk_pct = 0.025  # micro account — need larger % to clear exchange minimums
        elif portfolio_value < 2000:
            risk_pct = 0.015  # small account
        else:
            risk_pct = 0.01   # standard
        risk_budget = portfolio_value * risk_pct
        units_from_risk = risk_budget / stop_distance

        # Take the smaller of the two sizing methods for extra conservatism.
        raw_size = min(units_from_allocation, units_from_risk)

        # ── Fee adjustment ─────────────────────────────────────────────────────
        fee_pct = self.taker_fee_pct if use_market_order else self.maker_fee_pct
        # We pay fees on entry AND exit; subtract the total fee impact from size.
        fee_factor = 1.0 - (2.0 * fee_pct)
        adjusted_size = raw_size * fee_factor

        if adjusted_size <= 0:
            return 0.0

        logger.debug(
            "PositionSizer: kelly=%.4f conviction=%.3f dir=%s "
            "regime=%.2f sentiment=%.2f raw=%.6f fee_adj=%.6f",
            kelly,
            conviction,
            dir_upper,
            regime_mult,
            sentiment_mult,
            raw_size,
            adjusted_size,
        )
        return adjusted_size

    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        direction: str,
        atr_multiplier: float = _ATR_SL_MULTIPLIER_LONG,
    ) -> float:
        """
        Return an ATR-based stop-loss price.

        Parameters
        ----------
        entry_price    : expected fill price
        atr            : current ATR value (same units as entry_price)
        direction      : "LONG" or "SHORT"
        atr_multiplier : number of ATR widths for the stop distance (default 1.5)

        Returns
        -------
        float — stop-loss price
        """
        if entry_price <= 0 or atr < 0:
            raise ValueError("entry_price must be positive and atr must be non-negative")

        if direction.upper() == "LONG":
            stop = entry_price - atr_multiplier * atr
            return max(stop, 1e-8)  # guard against zero/negative prices
        elif direction.upper() == "SHORT":
            return entry_price + atr_multiplier * atr
        else:
            raise ValueError(f"direction must be 'LONG' or 'SHORT', got '{direction}'")

    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        rr_ratio: float = _DEFAULT_RR_RATIO,
    ) -> float:
        """
        Return a take-profit price that satisfies the given risk-reward ratio.

        Parameters
        ----------
        entry_price : expected fill price
        stop_loss   : stop-loss price (used to measure risk distance)
        rr_ratio    : reward-to-risk ratio (default 3.0 ⇒ TP is 3× the risk away)

        Returns
        -------
        float — take-profit price
        """
        if rr_ratio <= 0:
            raise ValueError("rr_ratio must be positive")

        risk_distance = abs(entry_price - stop_loss)
        reward_distance = risk_distance * rr_ratio

        if entry_price > stop_loss:
            # LONG
            return entry_price + reward_distance
        else:
            # SHORT
            return entry_price - reward_distance

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _half_kelly(win_rate: float, rr: float) -> float:
        """
        Compute the half-Kelly position fraction.

        Full Kelly: k = (p * rr - q) / rr  where q = 1 - p
        Half Kelly:  k / 2

        The output is capped at _MAX_KELLY_FRACTION / 2 to prevent
        runaway allocation even with unrealistically good statistics.

        Parameters
        ----------
        win_rate : probability of a winning trade [0, 1]
        rr       : average win / average loss ratio

        Returns
        -------
        float — half-Kelly fraction in [0, _MAX_KELLY_FRACTION / 2]
                Returns 0 if Kelly is negative (negative expected value).
        """
        if not (0 < win_rate < 1):
            logger.debug("Invalid win_rate %.4f — must be in (0, 1)", win_rate)
            return 0.0
        if rr <= 0:
            logger.debug("Invalid rr %.4f — must be positive", rr)
            return 0.0

        loss_rate = 1.0 - win_rate
        full_kelly = (win_rate * rr - loss_rate) / rr

        if full_kelly <= 0:
            return 0.0

        capped_kelly = min(full_kelly, _MAX_KELLY_FRACTION)
        return capped_kelly * 0.5
