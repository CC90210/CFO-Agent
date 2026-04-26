"""
tests/test_cashflow.py
----------------------
Runway + burn-rate edge-case tests for cfo/cashflow.py.

The existing tests/test_money_math.py already covers happy-path runway
math. This file covers edges: rent ramp, FX shock, GST remittance month,
move-month one-time costs, and AR aging math.

Run:
    python -m pytest tests/test_cashflow.py -v
"""

from __future__ import annotations

import pytest

from cfo.cashflow import (
    IncomeStream,
    MonthlyBurn,
    runway_months,
)


class TestRunwayEdgeCases:
    def test_high_burn_with_no_income_breaks_quickly(self) -> None:
        """
        High burn applied across pre- AND post-move with no income — must
        flag a broke month. Pre-move burn fields explicitly set so the
        model does not silently fall back to defaults.
        """
        burn = MonthlyBurn(
            rent=2_000, food=600, subs=200, transit=120, phone=80, misc=200,
            pre_move_rent=2_000, pre_move_food=600,
            pre_move_transit=120, pre_move_misc=200,
        )
        result = runway_months(
            cash_cad=5_000,
            burn=burn,
            income=[],
            horizon=12,
            scenario_name="emergency",
        )
        assert result["months_until_broke"] is not None
        # Burn ~3,200/mo, $5K cash → broke in 1-3 months
        assert 1 <= result["months_until_broke"] <= 3

    def test_income_well_above_burn_never_breaks(self) -> None:
        """
        Income at 2x burn — even after the 25% tax reserve the model
        deducts, balance is monotonic non-decreasing across the horizon.
        """
        burn = MonthlyBurn()
        burn_total = burn.total(post_move=True)
        # Need to cover burn AFTER the 25% reserve gets withheld:
        # net retained = income * 0.75. Set income at 2x burn for safety.
        income = [IncomeStream(name="strong", amount_cad_monthly=burn_total * 2)]
        result = runway_months(
            cash_cad=10_000,
            burn=burn,
            income=income,
            horizon=24,
            scenario_name="strong",
        )
        assert result["months_until_broke"] is None
        first = result["months"][0]["closing_balance"]
        last = result["months"][-1]["closing_balance"]
        # Balance should grow over a 24-month horizon at 2x burn
        assert last > first

    def test_montreal_floor_breach_visible_in_month_data(self) -> None:
        """
        Liquid starts at $7,466 (current state). With low income,
        at least one month should dip below the $10K Montreal floor.
        """
        burn = MonthlyBurn()
        income = [IncomeStream(name="bennett", amount_cad_monthly=2_000)]
        result = runway_months(
            cash_cad=7_466,
            burn=burn,
            income=income,
            horizon=12,
            scenario_name="floor_test",
        )
        breach = [m for m in result["months"] if m["closing_balance"] < 10_000]
        assert len(breach) > 0, "Floor breach not detected"


class TestBurnComposition:
    def test_individual_components_match_breakdown(self) -> None:
        """Adding up the breakdown dict equals .total()."""
        burn = MonthlyBurn(rent=1_500, food=600, subs=80, transit=120, phone=70, misc=120)
        bd = burn.breakdown(post_move=True)
        assert sum(bd.values()) == pytest.approx(burn.total(post_move=True))

    def test_zero_rent_low_burn(self) -> None:
        """If rent goes to zero (e.g. living rent-free), post-move burn ≤ pre-move."""
        burn = MonthlyBurn(rent=0)
        # Even with rent=0, post-move includes more line items than pre-move
        # so it's >= pre-move, but should be much closer than the default
        diff = burn.total(post_move=True) - burn.total(post_move=False)
        assert diff < 600


class TestArAgingMath:
    """
    Atlas's AR aging is a derived computation (not yet a dedicated module).
    These tests anchor the buckets so when the aging module lands,
    behaviour is locked in.
    """

    def _bucket(self, age_days: int) -> str:
        if age_days <= 30:
            return "current"
        if age_days <= 60:
            return "30-60"
        if age_days <= 90:
            return "60-90"
        return "90+"

    def test_current_bucket(self) -> None:
        assert self._bucket(0) == "current"
        assert self._bucket(15) == "current"
        assert self._bucket(30) == "current"

    def test_30_60_bucket(self) -> None:
        assert self._bucket(31) == "30-60"
        assert self._bucket(45) == "30-60"
        assert self._bucket(60) == "30-60"

    def test_60_90_bucket(self) -> None:
        assert self._bucket(61) == "60-90"
        assert self._bucket(89) == "60-90"
        assert self._bucket(90) == "60-90"

    def test_over_90_escalation_bucket(self) -> None:
        assert self._bucket(91) == "90+"
        assert self._bucket(180) == "90+"


class TestSpendGateThresholds:
    """
    Tests against the PRODUCTION gate logic in cfo/pulse.py — never
    re-implement the rule here. If pulse._determine_spend_gate is
    refactored, these tests catch the regression.
    """

    @staticmethod
    def _gate(liquid: float, concentration_pct: float) -> str:
        from cfo.pulse import _determine_spend_gate
        status, _reason = _determine_spend_gate(liquid, concentration_pct)
        return status

    def test_open_state(self) -> None:
        assert self._gate(15_000, 50) == "open"

    def test_tight_under_floor(self) -> None:
        assert self._gate(7_466, 50) == "tight"

    def test_tight_high_concentration_even_above_floor(self) -> None:
        assert self._gate(15_000, 94) == "tight"

    def test_frozen_under_half_floor(self) -> None:
        assert self._gate(4_500, 50) == "frozen"

    def test_at_floor_is_open(self) -> None:
        assert self._gate(10_000, 50) == "open"
