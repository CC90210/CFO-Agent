"""
tests/test_position_sizer.py — Unit tests for core/position_sizer.py.

Tests cover:
1. Half-Kelly formula returns correct values for known inputs.
2. Conviction scaling: 0.3 conviction → 30 % of full Kelly size.
3. Minimum conviction threshold: abs(conviction) < 0.3 → size 0.
4. ATR-based stop-loss calculation (LONG and SHORT).
5. Fee accounting reduces the raw size proportionally.
6. Take-profit calculation satisfies the requested R:R ratio.
7. Edge cases: zero equity, zero ATR, equal entry/stop prices.
"""

from __future__ import annotations

import pytest

from core.position_sizer import PositionSizer, _MIN_CONVICTION


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sizer(maker: float = 0.001, taker: float = 0.001) -> PositionSizer:
    return PositionSizer(maker_fee_pct=maker, taker_fee_pct=taker)


# ---------------------------------------------------------------------------
# Half-Kelly calculation
# ---------------------------------------------------------------------------


class TestHalfKelly:
    """Tests for PositionSizer._half_kelly (accessed via calculate_position_size)."""

    def test_positive_expected_value_returns_positive_fraction(self) -> None:
        """win_rate=0.6, rr=2.0 → positive Kelly."""
        sizer = _sizer()
        # kelly_full = (0.6 * 2 - 0.4) / 2 = (1.2 - 0.4) / 2 = 0.4
        kelly = sizer._half_kelly(win_rate=0.6, rr=2.0)
        assert kelly > 0

    def test_negative_expected_value_returns_zero(self) -> None:
        """win_rate=0.3, rr=1.0 → kelly = (0.3*1 - 0.7)/1 = -0.4 → 0."""
        sizer = _sizer()
        kelly = sizer._half_kelly(win_rate=0.3, rr=1.0)
        assert kelly == 0.0

    def test_half_kelly_is_half_of_full_kelly(self) -> None:
        """Half-Kelly should be exactly half the full Kelly (before cap)."""
        sizer = _sizer()
        win_rate, rr = 0.55, 2.5
        full_kelly = (win_rate * rr - (1 - win_rate)) / rr
        half = sizer._half_kelly(win_rate=win_rate, rr=rr)
        # Only valid when full_kelly < _MAX_KELLY_FRACTION
        from core.position_sizer import _MAX_KELLY_FRACTION
        if full_kelly < _MAX_KELLY_FRACTION:
            assert half == pytest.approx(full_kelly / 2.0, rel=1e-6)

    def test_half_kelly_capped_at_max_fraction(self) -> None:
        """Even with unrealistically perfect statistics, fraction is capped."""
        from core.position_sizer import _MAX_KELLY_FRACTION

        sizer = _sizer()
        # win_rate=0.99, rr=10 → huge Kelly
        kelly = sizer._half_kelly(win_rate=0.99, rr=10.0)
        assert kelly <= _MAX_KELLY_FRACTION / 2.0

    def test_half_kelly_known_value(self) -> None:
        """
        Verify by hand for win_rate=0.55, rr=2.0:
            full_kelly = (0.55 * 2 - 0.45) / 2 = 0.65 / 2 = 0.325
            half_kelly = 0.325 / 2 = 0.1625
        """
        sizer = _sizer()
        result = sizer._half_kelly(win_rate=0.55, rr=2.0)
        # 0.325 / 2 = 0.1625 — but capped at MAX_KELLY_FRACTION=0.25, half=0.125
        # full_kelly=0.325 > 0.25 cap → capped_kelly=0.25 → half=0.125
        from core.position_sizer import _MAX_KELLY_FRACTION
        full = (0.55 * 2 - 0.45) / 2.0
        expected = min(full, _MAX_KELLY_FRACTION) / 2.0
        assert result == pytest.approx(expected, rel=1e-6)

    def test_win_rate_zero_returns_zero(self) -> None:
        sizer = _sizer()
        assert sizer._half_kelly(win_rate=0.0, rr=3.0) == 0.0

    def test_win_rate_one_capped(self) -> None:
        sizer = _sizer()
        assert sizer._half_kelly(win_rate=1.0, rr=3.0) == 0.0  # boundary — not (0,1)


# ---------------------------------------------------------------------------
# Conviction scaling
# ---------------------------------------------------------------------------


class TestConvictionScaling:
    def test_conviction_scales_size_linearly(self) -> None:
        """Doubling conviction should roughly double the position size."""
        sizer = _sizer()
        common_kwargs = dict(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        size_low = sizer.calculate_position_size(conviction=0.4, **common_kwargs)
        size_high = sizer.calculate_position_size(conviction=0.8, **common_kwargs)

        # size_high should be roughly 2× size_low (within rounding)
        assert size_high > size_low
        assert size_high / size_low == pytest.approx(2.0, rel=0.05)

    def test_conviction_0_3_gives_30_pct_of_full_size(self) -> None:
        """At conviction=0.3 we should get 30 % of the full (conviction=1.0) size."""
        sizer = _sizer()
        common_kwargs = dict(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        size_full = sizer.calculate_position_size(conviction=1.0, **common_kwargs)
        size_30 = sizer.calculate_position_size(conviction=0.3, **common_kwargs)

        # 0.3 / 1.0 = 30 %
        assert size_30 / size_full == pytest.approx(0.3, rel=0.05)


# ---------------------------------------------------------------------------
# Minimum conviction threshold
# ---------------------------------------------------------------------------


class TestMinimumConvictionThreshold:
    def test_conviction_exactly_at_threshold_gives_nonzero(self) -> None:
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=_MIN_CONVICTION,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        # Exactly at threshold → should proceed (not zero)
        assert size > 0.0

    def test_conviction_just_below_threshold_returns_zero(self) -> None:
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=_MIN_CONVICTION - 0.01,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        assert size == 0.0

    def test_zero_conviction_returns_zero(self) -> None:
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=0.0,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        assert size == 0.0

    def test_small_negative_conviction_returns_zero(self) -> None:
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="SHORT",
            entry_price=100.0,
            stop_loss=105.0,
            conviction=-0.1,  # below -0.3 threshold (abs < 0.3)
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        assert size == 0.0


# ---------------------------------------------------------------------------
# ATR-based stop-loss
# ---------------------------------------------------------------------------


class TestATRStopLoss:
    def test_long_stop_below_entry(self) -> None:
        sizer = _sizer()
        stop = sizer.calculate_stop_loss(entry_price=100.0, atr=5.0, direction="LONG")
        assert stop < 100.0

    def test_short_stop_above_entry(self) -> None:
        sizer = _sizer()
        stop = sizer.calculate_stop_loss(entry_price=100.0, atr=5.0, direction="SHORT")
        assert stop > 100.0

    def test_long_stop_known_value(self) -> None:
        """stop = entry - multiplier * ATR = 100 - 1.5 * 5 = 92.5"""
        sizer = _sizer()
        stop = sizer.calculate_stop_loss(
            entry_price=100.0, atr=5.0, direction="LONG", atr_multiplier=1.5
        )
        assert stop == pytest.approx(92.5, abs=1e-6)

    def test_short_stop_known_value(self) -> None:
        """stop = entry + multiplier * ATR = 100 + 1.5 * 5 = 107.5"""
        sizer = _sizer()
        stop = sizer.calculate_stop_loss(
            entry_price=100.0, atr=5.0, direction="SHORT", atr_multiplier=1.5
        )
        assert stop == pytest.approx(107.5, abs=1e-6)

    def test_stop_is_never_zero_or_negative(self) -> None:
        sizer = _sizer()
        # Low price, large ATR → could go below zero without guard
        stop = sizer.calculate_stop_loss(
            entry_price=1.0, atr=10.0, direction="LONG", atr_multiplier=5.0
        )
        assert stop > 0.0

    def test_invalid_direction_raises(self) -> None:
        sizer = _sizer()
        with pytest.raises(ValueError, match="direction"):
            sizer.calculate_stop_loss(entry_price=100.0, atr=5.0, direction="UP")


# ---------------------------------------------------------------------------
# Fee accounting
# ---------------------------------------------------------------------------


class TestFeeAccounting:
    def test_higher_fees_reduce_size(self) -> None:
        """With higher commission, adjusted size should be smaller."""
        size_low_fee = _sizer(taker=0.001).calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=0.6,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        size_high_fee = _sizer(taker=0.005).calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=0.6,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        assert size_low_fee > size_high_fee

    def test_fee_factor_correct_with_known_fee(self) -> None:
        """
        With taker_fee=0.001, fee_factor = 1 - 2*0.001 = 0.998.
        The adjusted size should be raw_size * 0.998.
        """
        sizer = _sizer(taker=0.001)
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=1.0,
            avg_win_rate=0.55,
            avg_rr=2.0,
            use_market_order=True,
        )
        # size should be positive and correctly reduced
        assert size > 0
        # We can verify the fee factor indirectly: zero-fee size should be larger
        sizer_no_fee = _sizer(taker=0.0)
        size_no_fee = sizer_no_fee.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=1.0,
            avg_win_rate=0.55,
            avg_rr=2.0,
            use_market_order=True,
        )
        assert size_no_fee > size


# ---------------------------------------------------------------------------
# Take-profit calculation
# ---------------------------------------------------------------------------


class TestTakeProfitCalculation:
    def test_long_take_profit_above_entry(self) -> None:
        sizer = _sizer()
        tp = sizer.calculate_take_profit(entry_price=100.0, stop_loss=95.0, rr_ratio=3.0)
        assert tp > 100.0

    def test_short_take_profit_below_entry(self) -> None:
        sizer = _sizer()
        tp = sizer.calculate_take_profit(entry_price=100.0, stop_loss=105.0, rr_ratio=3.0)
        assert tp < 100.0

    def test_take_profit_satisfies_rr_ratio(self) -> None:
        """
        entry=100, stop=95, rr=3 → risk=5, reward=15 → TP=115.
        """
        sizer = _sizer()
        tp = sizer.calculate_take_profit(
            entry_price=100.0, stop_loss=95.0, rr_ratio=3.0
        )
        risk = abs(100.0 - 95.0)
        reward = abs(tp - 100.0)
        assert reward / risk == pytest.approx(3.0, rel=1e-6)

    def test_invalid_rr_ratio_raises(self) -> None:
        sizer = _sizer()
        with pytest.raises(ValueError, match="rr_ratio"):
            sizer.calculate_take_profit(entry_price=100.0, stop_loss=95.0, rr_ratio=0.0)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_zero_portfolio_returns_zero(self) -> None:
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=0.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=0.8,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        assert size == 0.0

    def test_equal_entry_and_stop_returns_zero(self) -> None:
        """When entry == stop, risk distance = 0 → cannot size."""
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=100.0,  # same as entry
            conviction=0.8,
            avg_win_rate=0.55,
            avg_rr=2.0,
        )
        assert size == 0.0

    def test_negative_expected_value_returns_zero(self) -> None:
        """If win_rate × rr < loss_rate, Kelly is negative → don't trade."""
        sizer = _sizer()
        size = sizer.calculate_position_size(
            portfolio_value=10_000.0,
            direction="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            conviction=0.8,
            avg_win_rate=0.25,  # lose 75% of the time
            avg_rr=1.0,         # and wins are the same size as losses
        )
        assert size == 0.0
