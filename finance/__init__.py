"""
finance/__init__.py
--------------------
Atlas Finance module — CC's complete financial brain.

Sub-modules
-----------
advisor       Financial Advisor Agent (portfolio analysis, allocation, monthly reviews)
tax           Canadian Tax Calculator & Strategist (CRA-accurate)
wealth_tracker Net Worth & Wealth Tracking (FIRE calculator, projections)
budget        Budget & Expense Tracking (categorisation, savings opportunities)
"""

from finance.advisor import (
    AllocationPlan,
    AssetClass,
    FinancialAdvisor,
    GoalProjection,
    MonthlyReport,
    PortfolioAnalysis,
    RiskTolerance,
)
from finance.budget import Budget, BudgetSummary, ExpenseCategory, Suggestion
from finance.tax import (
    AccountStrategy,
    CryptoTaxCalculator,
    Deduction,
    HarvestOpportunity,
    QuarterlyEstimate,
    TaxReport,
    TaxSummary,
)
from finance.wealth_tracker import (
    FIREProjection,
    NetWorthSnapshot,
    WealthProjection,
    WealthTracker,
)

__all__ = [
    # advisor
    "FinancialAdvisor",
    "RiskTolerance",
    "AssetClass",
    "PortfolioAnalysis",
    "AllocationPlan",
    "MonthlyReport",
    "GoalProjection",
    # tax
    "CryptoTaxCalculator",
    "TaxSummary",
    "HarvestOpportunity",
    "QuarterlyEstimate",
    "AccountStrategy",
    "TaxReport",
    "Deduction",
    # wealth_tracker
    "WealthTracker",
    "NetWorthSnapshot",
    "WealthProjection",
    "FIREProjection",
    # budget
    "Budget",
    "ExpenseCategory",
    "BudgetSummary",
    "Suggestion",
]
