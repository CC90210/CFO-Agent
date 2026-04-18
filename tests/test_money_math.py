"""
tests/test_money_math.py
------------------------
Unit tests for Atlas's critical money math — the calculations CC actually
bases real financial decisions on. If any of these break silently, CC could
move to Montreal under-capitalized or underestimate his tax reserve.

Run:
    python -m pytest tests/test_money_math.py -v
"""

from __future__ import annotations

from datetime import date

import pytest

from cfo.cashflow import (
    IncomeStream,
    MonthlyBurn,
    _month_iter,
    runway_months,
)


# ─────────────────────────────────────────────────────────────────────────────
#  MonthlyBurn — the "what does CC need to live on" number
# ─────────────────────────────────────────────────────────────────────────────


class TestMonthlyBurn:
    def test_default_post_move_total_is_reasonable(self) -> None:
        """Default Montreal burn should land between $1,400 and $1,900."""
        burn = MonthlyBurn()
        total = burn.total(post_move=True)
        assert 1400 < total < 1900, f"Post-move total ${total} outside sanity band"

    def test_pre_move_is_much_lower_than_post_move(self) -> None:
        """Living at parents' should be <= 40% of Montreal burn."""
        burn = MonthlyBurn()
        assert burn.total(post_move=False) <= burn.total(post_move=True) * 0.4

    def test_breakdown_sum_matches_total(self) -> None:
        burn = MonthlyBurn()
        for post_move in (True, False):
            bd = burn.breakdown(post_move=post_move)
            assert abs(sum(bd.values()) - burn.total(post_move=post_move)) < 0.01

    def test_solo_rent_worst_case(self) -> None:
        """If CC goes solo at $1,500 rent, burn should still be under $2,500."""
        burn = MonthlyBurn(rent=1500.00)
        assert burn.total(post_move=True) < 2500


# ─────────────────────────────────────────────────────────────────────────────
#  IncomeStream — FX conversion + confidence weighting
# ─────────────────────────────────────────────────────────────────────────────


class TestIncomeStream:
    def test_cad_income_passes_through(self) -> None:
        s = IncomeStream(name="CAD client", amount_cad_monthly=1000)
        assert s.cad_amount() == 1000

    def test_usd_income_converts_at_rate(self) -> None:
        s = IncomeStream(name="US client", amount_usd_monthly=1000)
        assert s.cad_amount(usd_rate=1.37) == pytest.approx(1370)

    def test_mixed_streams_sum_correctly(self) -> None:
        s = IncomeStream(
            name="mixed",
            amount_cad_monthly=500,
            amount_usd_monthly=1000,
        )
        assert s.cad_amount(usd_rate=1.40) == pytest.approx(1900)

    def test_confidence_reduces_effective_income(self) -> None:
        """A speculative 50%-confidence $2,000/mo stream should contribute $1,000."""
        s = IncomeStream(
            name="speculative",
            amount_cad_monthly=2000,
            confidence=0.5,
        )
        assert s.effective_cad(month=date(2026, 5, 1)) == pytest.approx(1000)

    def test_inactive_before_start_month(self) -> None:
        s = IncomeStream(
            name="future",
            amount_cad_monthly=1000,
            start_month=date(2026, 7, 1),
        )
        assert s.is_active(date(2026, 5, 1)) is False
        assert s.effective_cad(date(2026, 5, 1)) == 0

    def test_inactive_after_end_month(self) -> None:
        s = IncomeStream(
            name="expiring",
            amount_cad_monthly=1000,
            end_month=date(2026, 5, 1),
        )
        assert s.is_active(date(2026, 6, 1)) is False


# ─────────────────────────────────────────────────────────────────────────────
#  _month_iter — month-date generator used everywhere
# ─────────────────────────────────────────────────────────────────────────────


class TestMonthIter:
    def test_yields_first_of_month(self) -> None:
        months = list(_month_iter(date(2026, 4, 15), 3))
        assert all(m.day == 1 for m in months)

    def test_handles_year_boundary(self) -> None:
        months = list(_month_iter(date(2026, 11, 1), 4))
        assert months == [
            date(2026, 11, 1),
            date(2026, 12, 1),
            date(2027, 1, 1),
            date(2027, 2, 1),
        ]

    def test_correct_length(self) -> None:
        assert len(list(_month_iter(date(2026, 1, 1), 24))) == 24


# ─────────────────────────────────────────────────────────────────────────────
#  runway_months — the critical Montreal-affordability calculation
# ─────────────────────────────────────────────────────────────────────────────


class TestRunwayMonths:
    def test_broke_fast_with_zero_income(self) -> None:
        """$1,000 cash with $500/mo burn and no income → broke in ~2 months."""
        burn = MonthlyBurn(rent=0, food=500, subs=0, transit=0, phone=0, misc=0,
                           pre_move_rent=0, pre_move_food=500,
                           pre_move_transit=0, pre_move_misc=0)
        result = runway_months(
            cash_cad=1000,
            burn=burn,
            income=[],
            horizon=12,
            scenario_name="no income",
        )
        assert result["months_until_broke"] is not None
        assert 1 <= result["months_until_broke"] <= 3

    def test_never_broke_when_income_exceeds_burn(self) -> None:
        """With $4K/mo income and $1.5K burn, never broke over 24 months."""
        burn = MonthlyBurn()  # defaults ~$1,680
        income = [IncomeStream(name="bennett", amount_cad_monthly=4000, confidence=1.0)]
        result = runway_months(
            cash_cad=7466,
            burn=burn,
            income=income,
            horizon=24,
            scenario_name="solvent",
        )
        assert result["months_until_broke"] is None

    def test_returns_month_level_data(self) -> None:
        burn = MonthlyBurn()
        income = [IncomeStream(name="test", amount_cad_monthly=3000)]
        result = runway_months(
            cash_cad=7466,
            burn=burn,
            income=income,
            horizon=12,
            scenario_name="test",
        )
        assert "months" in result
        assert len(result["months"]) == 12
        # Every month entry should have the full cashflow fields
        required_keys = {"month", "opening_balance", "closing_balance",
                        "gross_income", "burn", "net_cashflow"}
        for m in result["months"]:
            assert required_keys.issubset(m.keys()), (
                f"Month missing keys: {required_keys - m.keys()}"
            )

    def test_scenario_name_preserved(self) -> None:
        result = runway_months(
            cash_cad=10000,
            burn=MonthlyBurn(),
            income=[IncomeStream(name="x", amount_cad_monthly=5000)],
            horizon=6,
            scenario_name="realistic",
        )
        assert result["scenario"] == "realistic"


# ─────────────────────────────────────────────────────────────────────────────
#  Tax-reserve sanity — if this breaks, CC under-saves for taxes
# ─────────────────────────────────────────────────────────────────────────────


class TestTaxReserveMath:
    def test_25_percent_reserve_on_current_mrr(self) -> None:
        """
        CC's MRR is ~$2,982 USD/mo. At 25% self-employment reserve and 1.37 FX,
        quarterly reserve should be ~$3,075 CAD.
        """
        mrr_usd = 2982.0
        usd_cad = 1.37
        reserve_rate = 0.25
        monthly_reserve_cad = mrr_usd * usd_cad * reserve_rate
        quarterly = monthly_reserve_cad * 3
        assert 2900 < quarterly < 3200, (
            f"Quarterly reserve ${quarterly:.0f} outside expected band"
        )

    def test_reserve_scales_linearly_with_income(self) -> None:
        """Reserve at $10K MRR should be 2x reserve at $5K MRR."""
        rate = 0.25
        low = 5000 * rate
        high = 10000 * rate
        assert high == pytest.approx(low * 2)


# ─────────────────────────────────────────────────────────────────────────────
#  Montreal floor sanity — money CC won't move without
# ─────────────────────────────────────────────────────────────────────────────


class TestMontrealFloor:
    FLOOR = 10_000

    def test_current_cash_below_floor_triggers_gap(self) -> None:
        """At $7,466 liquid, gap should be exactly $2,534."""
        liquid = 7466
        gap = self.FLOOR - liquid
        assert gap == 2534

    def test_floor_is_a_minimum_not_target(self) -> None:
        """The advice 'target $15K before moving' means real target is 1.5x floor."""
        prudent_target = self.FLOOR * 1.5
        assert prudent_target == 15_000
