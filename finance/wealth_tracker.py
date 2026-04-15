"""
finance/wealth_tracker.py
--------------------------
Net Worth & Wealth Tracking for Atlas.

Tracks CC's complete financial picture: trading portfolio, business income,
bank accounts, registered accounts (TFSA/RRSP/FHSA), and liabilities.

Includes:
- Point-in-time net worth snapshots with breakdown
- Compound-growth wealth projection (year-by-year)
- FIRE (Financial Independence, Retire Early) calculator using the 4% rule
- Savings rate calculation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any

try:
    from db.models import NetWorthSnapshot as NetWorthSnapshotModel
except ImportError:
    NetWorthSnapshotModel = None  # db/ archived in CFO pivot; ORM methods now no-op

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class NetWorthSnapshot:
    """
    Point-in-time net worth record.

    date            : Snapshot date
    total_assets    : Sum of all assets in CAD
    total_liabilities: Sum of all liabilities in CAD
    net_worth       : total_assets - total_liabilities
    breakdown       : Category → value dict (e.g. {"TFSA": 5000, "Crypto": 8000})
    """

    date: date
    total_assets: float
    total_liabilities: float
    net_worth: float
    breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.net_worth = round(self.total_assets - self.total_liabilities, 2)
        self.total_assets = round(self.total_assets, 2)
        self.total_liabilities = round(self.total_liabilities, 2)


@dataclass
class YearlyProjection:
    """A single year in a wealth projection."""

    year: int
    balance: float
    contributions_to_date: float
    growth_to_date: float


@dataclass
class WealthProjection:
    """
    Output of ``WealthTracker.project_wealth``.

    yearly_values         : Year-by-year balance
    final_balance         : Balance at the end of the projection
    total_contributions   : Total capital contributed over the period
    total_growth          : Total investment growth (interest/gains)
    double_by_year        : Calendar year when initial balance doubles (or None)
    """

    yearly_values: list[YearlyProjection]
    final_balance: float
    total_contributions: float
    total_growth: float
    double_by_year: int | None


@dataclass
class FIREProjection:
    """
    Output of ``WealthTracker.fire_calculator``.

    fire_number         : Portfolio size needed for FIRE (annual_expenses / withdrawal_rate)
    years_to_fire       : Estimated years to reach FIRE number
    fire_date           : Estimated calendar date
    current_gap         : How far away from FIRE number today
    monthly_savings_needed: Monthly saving required to hit FIRE on schedule
    withdrawal_rate     : Safe withdrawal rate used (default 4%)
    annual_expenses     : Annual expenses used in calculation
    confidence          : 0.0–1.0 confidence in the projection
    notes               : List of planning notes
    """

    fire_number: float
    years_to_fire: int
    fire_date: date
    current_gap: float
    monthly_savings_needed: float
    withdrawal_rate: float
    annual_expenses: float
    confidence: float
    notes: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
#  Wealth Tracker
# ─────────────────────────────────────────────────────────────────────────────


class WealthTracker:
    """
    Tracks CC's complete financial picture over time.

    All values are in CAD. Snapshots are stored in-memory AND can be
    persisted to the database when a session is passed in.
    """

    def __init__(self) -> None:
        self._snapshots: list[NetWorthSnapshot] = []

    # ------------------------------------------------------------------
    # Net worth tracking
    # ------------------------------------------------------------------

    def update_net_worth(
        self,
        assets: dict[str, float],
        liabilities: dict[str, float],
    ) -> NetWorthSnapshot:
        """
        Record a new net worth snapshot.

        Parameters
        ----------
        assets      : Category → CAD value dict.
                      e.g. {"Trading Portfolio": 8500, "TFSA": 14000,
                             "RRSP": 0, "Chequing": 3200, "FHSA": 8000}
        liabilities : Category → CAD value dict.
                      e.g. {"Credit Card": 1200, "Student Loan": 0}

        Returns
        -------
        NetWorthSnapshot stored in memory and returned to caller.
        """
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())

        breakdown: dict[str, float] = {}
        for category, value in assets.items():
            breakdown[f"Asset: {category}"] = value
        for category, value in liabilities.items():
            breakdown[f"Liability: {category}"] = value

        snapshot = NetWorthSnapshot(
            date=date.today(),
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=total_assets - total_liabilities,
            breakdown=breakdown,
        )

        self._snapshots.append(snapshot)
        logger.info(
            "WealthTracker: net worth snapshot recorded — $%,.0f CAD", snapshot.net_worth
        )
        return snapshot

    def get_net_worth_history(self) -> list[NetWorthSnapshot]:
        """
        Return all recorded net worth snapshots in chronological order.

        In-memory only. For persistent history, load from the database using
        ``load_from_db``.
        """
        return sorted(self._snapshots, key=lambda s: s.date)

    def load_from_db(self, db_rows: list[Any]) -> None:
        """
        Populate in-memory history from database rows (NetWorthSnapshotModel).

        Parameters
        ----------
        db_rows : List of NetWorthSnapshotModel ORM objects fetched from the db.
        """
        self._snapshots.clear()
        for row in db_rows:
            breakdown = row.breakdown_json or {}
            snapshot = NetWorthSnapshot(
                date=row.date,
                total_assets=row.total_assets,
                total_liabilities=row.total_liabilities,
                net_worth=row.net_worth,
                breakdown=breakdown,
            )
            self._snapshots.append(snapshot)

    def to_db_model(self, snapshot: NetWorthSnapshot):
        """Convert a NetWorthSnapshot dataclass to the ORM model for saving.

        Requires db/ module (archived in CFO pivot). Returns None if unavailable.
        """
        if NetWorthSnapshotModel is None:
            logger.warning("db.models.NetWorthSnapshot unavailable; db persistence disabled.")
            return None
        return NetWorthSnapshotModel(
            date=snapshot.date,
            total_assets=snapshot.total_assets,
            total_liabilities=snapshot.total_liabilities,
            net_worth=snapshot.net_worth,
            breakdown_json=snapshot.breakdown,
        )

    # ------------------------------------------------------------------
    # Savings rate
    # ------------------------------------------------------------------

    def calculate_savings_rate(self, income: float, expenses: float) -> float:
        """
        Calculate the savings rate as a fraction.

        Parameters
        ----------
        income   : Total take-home income for the period (CAD).
        expenses : Total expenses for the period (CAD).

        Returns
        -------
        Savings rate between 0.0 and 1.0. Returns 0.0 if income is zero.
        """
        if income <= 0:
            return 0.0
        savings = income - expenses
        return round(max(0.0, min(1.0, savings / income)), 4)

    # ------------------------------------------------------------------
    # Wealth projection
    # ------------------------------------------------------------------

    def project_wealth(
        self,
        years: int,
        monthly_savings: float,
        avg_return: float,
        starting_balance: float | None = None,
    ) -> WealthProjection:
        """
        Project wealth growth year-by-year using compound interest.

        Parameters
        ----------
        years            : Number of years to project.
        monthly_savings  : Monthly contribution to portfolio (CAD).
        avg_return       : Expected annual return as fraction (e.g. 0.08).
        starting_balance : Starting balance. If None, uses latest net worth snapshot.

        Returns
        -------
        WealthProjection with yearly values.
        """
        if starting_balance is None:
            history = self.get_net_worth_history()
            starting_balance = history[-1].net_worth if history else 0.0

        monthly_rate = avg_return / 12
        balance = starting_balance
        initial_balance = starting_balance
        total_contributions = 0.0
        yearly_values: list[YearlyProjection] = []
        current_year = date.today().year
        double_by_year: int | None = None

        for year_num in range(1, years + 1):
            for _ in range(12):
                balance = balance * (1 + monthly_rate) + monthly_savings
                total_contributions += monthly_savings

            total_growth = balance - initial_balance - total_contributions
            yearly_values.append(
                YearlyProjection(
                    year=current_year + year_num,
                    balance=round(balance, 2),
                    contributions_to_date=round(total_contributions, 2),
                    growth_to_date=round(total_growth, 2),
                )
            )

            if double_by_year is None and balance >= initial_balance * 2 and initial_balance > 0:
                double_by_year = current_year + year_num

        return WealthProjection(
            yearly_values=yearly_values,
            final_balance=round(balance, 2),
            total_contributions=round(total_contributions, 2),
            total_growth=round(balance - initial_balance - total_contributions, 2),
            double_by_year=double_by_year,
        )

    # ------------------------------------------------------------------
    # FIRE calculator
    # ------------------------------------------------------------------

    def fire_calculator(
        self,
        annual_expenses: float,
        withdrawal_rate: float = 0.04,
        monthly_savings: float | None = None,
        avg_return: float = 0.08,
        starting_balance: float | None = None,
    ) -> FIREProjection:
        """
        Calculate when CC reaches Financial Independence using the 4% rule.

        The "FIRE number" is: annual_expenses / withdrawal_rate
        With 4% withdrawal rate, you need 25× annual expenses invested.

        Parameters
        ----------
        annual_expenses  : CC's expected annual expenses at retirement (CAD).
        withdrawal_rate  : Safe withdrawal rate (default 4% — Trinity Study).
        monthly_savings  : Monthly contribution. Falls back to settings default if None.
        avg_return       : Expected annual portfolio return (fraction).
        starting_balance : Current investable portfolio. Falls back to latest snapshot.

        Returns
        -------
        FIREProjection with FIRE number, years/date to FIRE, and monthly target.
        """
        from config.settings import settings as app_settings

        if monthly_savings is None:
            monthly_savings = app_settings.finance.monthly_savings_target

        if starting_balance is None:
            history = self.get_net_worth_history()
            starting_balance = history[-1].net_worth if history else 0.0

        fire_number = annual_expenses / withdrawal_rate
        current_gap = max(0.0, fire_number - starting_balance)

        if starting_balance >= fire_number:
            return FIREProjection(
                fire_number=round(fire_number, 2),
                years_to_fire=0,
                fire_date=date.today(),
                current_gap=0.0,
                monthly_savings_needed=0.0,
                withdrawal_rate=withdrawal_rate,
                annual_expenses=annual_expenses,
                confidence=0.95,
                notes=["Congratulations — you have reached your FIRE number!"],
            )

        # Simulate month-by-month to FIRE
        monthly_rate = avg_return / 12
        balance = starting_balance
        months = 0
        for _ in range(600):  # cap at 50 years
            balance = balance * (1 + monthly_rate) + monthly_savings
            months += 1
            if balance >= fire_number:
                break

        years_to_fire = months // 12
        fire_date = date(date.today().year + years_to_fire, date.today().month, 1)

        # Calculate monthly savings needed to hit FIRE in 20 years (typical target)
        target_months = 240
        needed_monthly = self._solve_monthly_savings(
            starting_balance, fire_number, avg_return / 12, target_months
        )

        # Confidence degrades past 15 years
        confidence = round(max(0.1, 1.0 - years_to_fire / 50), 3)

        notes = [
            f"FIRE number: ${fire_number:,.0f} CAD ({annual_expenses:,.0f} ÷ {withdrawal_rate*100:.0f}% = 25× expenses)",
            f"Current portfolio gap: ${current_gap:,.0f} CAD",
            f"At ${monthly_savings:,.0f}/month savings and {avg_return*100:.0f}% annual return, "
            f"projected FIRE in {years_to_fire} years.",
            "At 22, even modest savings in a TFSA (tax-free compounding) dramatically accelerate this timeline.",
        ]
        if years_to_fire > 20:
            notes.append(
                f"To hit FIRE in 20 years, you'd need to save ${needed_monthly:,.0f}/month."
            )

        return FIREProjection(
            fire_number=round(fire_number, 2),
            years_to_fire=years_to_fire,
            fire_date=fire_date,
            current_gap=round(current_gap, 2),
            monthly_savings_needed=round(needed_monthly, 2),
            withdrawal_rate=withdrawal_rate,
            annual_expenses=annual_expenses,
            confidence=confidence,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _solve_monthly_savings(
        current_balance: float,
        target_balance: float,
        monthly_rate: float,
        months: int,
    ) -> float:
        """
        Solve for the monthly contribution needed to reach target in N months.

        Uses the future value of an annuity formula:
            FV = PV*(1+r)^n + PMT * [((1+r)^n - 1) / r]
        Solving for PMT:
            PMT = (FV - PV*(1+r)^n) / [((1+r)^n - 1) / r]
        """
        if monthly_rate <= 0:
            return max(0.0, (target_balance - current_balance) / months)

        growth_factor = (1 + monthly_rate) ** months
        annuity_factor = (growth_factor - 1) / monthly_rate

        required = (target_balance - current_balance * growth_factor) / annuity_factor
        return max(0.0, required)
