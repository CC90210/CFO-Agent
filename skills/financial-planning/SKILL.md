---
name: financial-planning
description: >
  Budgeting, net worth tracking, FIRE calculations, wealth projections,
  and portfolio allocation for CC's complete financial picture.
triggers: [budget, FIRE, net worth, savings, allocation, projection, wealth, portfolio, rebalance, emergency fund]
tier: core
dependencies: []
---

# Financial Planning — Budget, Wealth & FIRE

> Atlas's financial planning engine. Tracks CC's complete financial picture:
> income, expenses, net worth, savings rate, and path to financial independence.

## Overview

Four planning domains:
1. **Budgeting** — Income/expense tracking, category analysis, savings opportunities
2. **Net Worth** — Point-in-time snapshots, asset/liability breakdown
3. **Wealth Projection** — Compound growth modeling, year-by-year projections
4. **FIRE Calculator** — Financial independence timeline using 4% rule

## Tool Routing

| Operation | Module | Method |
|-----------|--------|--------|
| Add expense | `finance/budget.py` | `Budget.add_expense()` |
| Monthly summary | `finance/budget.py` | `Budget.monthly_summary()` |
| Find savings | `finance/budget.py` | `Budget.find_savings_opportunities()` |
| Net worth snapshot | `finance/wealth_tracker.py` | `WealthTracker.update_net_worth()` |
| Wealth projection | `finance/wealth_tracker.py` | `WealthTracker.project_wealth()` |
| FIRE calculator | `finance/wealth_tracker.py` | `WealthTracker.fire_calculator()` |
| Portfolio analysis | `finance/advisor.py` | `FinancialAdvisor.analyze_portfolio()` |
| Asset allocation | `finance/advisor.py` | `FinancialAdvisor.suggest_allocation()` |
| Monthly review | `finance/advisor.py` | `FinancialAdvisor.monthly_review()` |
| Emergency plan | `finance/advisor.py` | `FinancialAdvisor.emergency_assessment()` |
| Goal tracking | `finance/advisor.py` | `FinancialAdvisor.goal_tracker()` |
| Rebalancing | `finance/advisor.py` | `FinancialAdvisor.compute_rebalancing_actions()` |

## Budget Quick Start

```python
from finance.budget import Budget, ExpenseCategory

budget = Budget(monthly_income=4000)  # CAD
budget.add_expense(1200, ExpenseCategory.HOUSING, "Rent")
budget.add_expense(400, ExpenseCategory.FOOD, "Groceries")
budget.add_expense(50, ExpenseCategory.SUBSCRIPTIONS, "Claude API")
summary = budget.monthly_summary(month=3, year=2026)
# summary.savings_rate → 0.5875 (58.75%)
```

## Net Worth Tracking

```python
from finance.wealth_tracker import WealthTracker

tracker = WealthTracker()
snapshot = tracker.update_net_worth(
    assets={"Trading Portfolio": 136, "TFSA": 0, "Chequing": 2000, "FHSA": 0},
    liabilities={"Credit Card": 500},
)
# snapshot.net_worth → $1,636 CAD
```

## FIRE Calculator

```python
projection = tracker.fire_calculator(
    annual_expenses=36000,    # $3K/month
    withdrawal_rate=0.04,     # 4% rule
    monthly_savings=1500,     # target savings
    avg_return=0.08,          # 8% annual return
    starting_balance=2000,
)
# projection.fire_number → $900,000
# projection.years_to_fire → ~22 years
# projection.monthly_savings_needed → for 20-year target
```

## CC's Financial Targets

| Target | Amount | Timeline |
|--------|--------|----------|
| Emergency fund (3 months) | $9,000 CAD | Priority 1 |
| FHSA maxed | $8,000/year | Annual |
| TFSA maxed | $7,000/year | Annual |
| FIRE number (4% rule) | ~$900,000 | 20-year horizon |
| OASIS MRR | $5,000 USD | By May 15, 2026 |
