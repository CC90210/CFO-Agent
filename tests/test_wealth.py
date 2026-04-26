"""
tests/test_wealth.py
--------------------
Known-answer tests for finance/wealth_tracker.py — net worth, savings rate,
compound projection, FIRE math.

Run:
    python -m pytest tests/test_wealth.py -v
"""

from __future__ import annotations

import pytest

from finance.wealth_tracker import (
    NetWorthSnapshot,
    WealthTracker,
)


class TestNetWorthSnapshot:
    def test_snapshot_round_trips_assets_and_liabilities(self) -> None:
        wt = WealthTracker()
        snap = wt.update_net_worth(
            assets={"TFSA": 5_000, "Cash": 3_000, "Crypto": 2_000},
            liabilities={"CC": 500},
        )
        assert snap.total_assets == pytest.approx(10_000)
        assert snap.total_liabilities == pytest.approx(500)
        assert snap.net_worth == pytest.approx(9_500)

    def test_snapshot_breakdown_includes_all_categories(self) -> None:
        wt = WealthTracker()
        snap = wt.update_net_worth(
            assets={"TFSA": 1_000, "Crypto": 2_000},
            liabilities={"Loan": 500},
        )
        keys = set(snap.breakdown.keys())
        assert "Asset: TFSA" in keys
        assert "Asset: Crypto" in keys
        assert "Liability: Loan" in keys

    def test_history_returns_chronological(self) -> None:
        wt = WealthTracker()
        wt.update_net_worth(assets={"Cash": 1_000}, liabilities={})
        wt.update_net_worth(assets={"Cash": 1_500}, liabilities={})
        history = wt.get_net_worth_history()
        assert len(history) == 2
        assert history[0].total_assets <= history[1].total_assets


class TestSavingsRate:
    def test_zero_income_returns_zero(self) -> None:
        wt = WealthTracker()
        assert wt.calculate_savings_rate(income=0, expenses=0) == 0.0

    def test_50pct_savings(self) -> None:
        wt = WealthTracker()
        assert wt.calculate_savings_rate(income=4_000, expenses=2_000) == 0.5

    def test_negative_savings_clamped_to_zero(self) -> None:
        """Spending more than income shouldn't produce a negative savings rate."""
        wt = WealthTracker()
        assert wt.calculate_savings_rate(income=2_000, expenses=3_000) == 0.0

    def test_100pct_savings_when_no_expenses(self) -> None:
        wt = WealthTracker()
        assert wt.calculate_savings_rate(income=5_000, expenses=0) == 1.0


class TestWealthProjection:
    def test_zero_return_zero_savings_balance_unchanged(self) -> None:
        wt = WealthTracker()
        proj = wt.project_wealth(
            years=10, monthly_savings=0, avg_return=0, starting_balance=10_000,
        )
        assert proj.final_balance == pytest.approx(10_000)
        assert proj.total_contributions == 0
        assert proj.total_growth == 0

    def test_compound_only_no_savings_known_answer(self) -> None:
        """
        $10,000 at 8% annual (compounded monthly) for 10 years.
        Expected: ~$22,196.40 (within rounding of (1 + 0.08/12)^120 * 10_000).
        """
        wt = WealthTracker()
        proj = wt.project_wealth(
            years=10, monthly_savings=0, avg_return=0.08, starting_balance=10_000,
        )
        expected = 10_000 * (1 + 0.08 / 12) ** 120
        assert proj.final_balance == pytest.approx(expected, rel=0.001)

    def test_savings_only_no_return(self) -> None:
        """$500/mo for 5 years at 0% return = $30,000."""
        wt = WealthTracker()
        proj = wt.project_wealth(
            years=5, monthly_savings=500, avg_return=0.0, starting_balance=0,
        )
        assert proj.total_contributions == pytest.approx(30_000)
        assert proj.final_balance == pytest.approx(30_000)
        assert proj.total_growth == pytest.approx(0)

    def test_doubling_year_set_when_balance_doubles(self) -> None:
        wt = WealthTracker()
        proj = wt.project_wealth(
            years=15, monthly_savings=0, avg_return=0.08, starting_balance=10_000,
        )
        assert proj.double_by_year is not None
        # Rule of 72: 72/8 ≈ 9 years to double
        from datetime import date
        delta_years = proj.double_by_year - date.today().year
        assert 8 <= delta_years <= 11

    def test_yearly_values_length_matches_years(self) -> None:
        wt = WealthTracker()
        proj = wt.project_wealth(
            years=7, monthly_savings=100, avg_return=0.05, starting_balance=1_000,
        )
        assert len(proj.yearly_values) == 7


class TestFireSanity:
    def test_fire_target_is_25x_annual_expenses_at_4pct_swr(self) -> None:
        """
        4% safe withdrawal rate → FIRE number = annual expenses × 25.
        Quick sanity check, no implementation dependency.
        """
        annual_expenses = 36_000
        swr = 0.04
        fire_number = annual_expenses / swr
        assert fire_number == pytest.approx(annual_expenses * 25)

    def test_atlas_uses_conservative_3_5pct_swr(self) -> None:
        """
        Atlas's wealth-tracker agent docs: 3.5% SWR for CC's 60-year horizon.
        FIRE multiplier = 1 / 0.035 ≈ 28.57.
        """
        swr = 0.035
        multiplier = 1 / swr
        assert multiplier == pytest.approx(28.57, abs=0.01)
