"""
finance/budget.py
-----------------
Budget & Expense Tracking for Atlas.

Simple, lightweight expense categorisation and monthly summarisation.
Claude is used for finding savings opportunities — everything else is
pure Python arithmetic for auditability.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any

import anthropic

from config.settings import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Enumerations
# ─────────────────────────────────────────────────────────────────────────────


class ExpenseCategory(str, Enum):
    """Expense categories for CC's budget."""

    HOUSING = "Housing"
    FOOD = "Food"
    TRANSPORT = "Transport"
    BUSINESS = "Business"
    ENTERTAINMENT = "Entertainment"
    SUBSCRIPTIONS = "Subscriptions"
    SAVINGS = "Savings"
    INVESTING = "Investing"
    OTHER = "Other"


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Expense:
    """A single expense record."""

    amount: float
    category: ExpenseCategory
    description: str
    date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Expense amount cannot be negative: {self.amount}")


@dataclass
class BudgetSummary:
    """
    Monthly budget summary.

    total_income    : Total income received in the month (CAD)
    total_expenses  : Total expenses paid in the month (CAD)
    net_savings     : total_income - total_expenses
    savings_rate    : net_savings / total_income (0.0–1.0)
    by_category     : ExpenseCategory label → total spent
    """

    total_income: float
    total_expenses: float
    net_savings: float
    savings_rate: float
    by_category: dict[str, float]
    month: int
    year: int


@dataclass
class Suggestion:
    """A Claude-generated savings suggestion."""

    category: str
    description: str
    estimated_monthly_saving: float
    priority: str   # "HIGH" | "MEDIUM" | "LOW"
    action: str


# ─────────────────────────────────────────────────────────────────────────────
#  Budget tracker
# ─────────────────────────────────────────────────────────────────────────────


class Budget:
    """
    Monthly budget and expense tracker for CC.

    Expenses are stored in memory. For persistence, convert to the Expense
    ORM model and save via SQLAlchemy (the model is defined in db/models.py).

    Usage
    -----
    budget = Budget()
    budget.add_expense(45.00, ExpenseCategory.FOOD, "Groceries")
    summary = budget.monthly_summary(month=3, year=2026)
    suggestions = await budget.find_savings_opportunities(summary)
    """

    _MAX_RETRIES: int = 3
    _BACKOFF_BASE: float = 1.5

    _SYSTEM_PROMPT = (
        "You are Atlas, a financial advisor for CC, a 22-year-old entrepreneur "
        "in Collingwood, Ontario. He earns ~$2,982/month MRR from OASIS AI Solutions. "
        "Analyse his spending and provide specific, actionable savings recommendations. "
        "Be direct and practical — no generic advice."
    )

    def __init__(self, monthly_income: float = 2982.0) -> None:
        """
        Parameters
        ----------
        monthly_income : CC's current MRR / regular monthly income (CAD).
                         Used as the default income figure in monthly_summary
                         when no explicit income is passed.
        """
        self.monthly_income = monthly_income
        self._expenses: list[Expense] = []
        self._client: anthropic.AsyncAnthropic | None = None

    # ------------------------------------------------------------------
    # Expense management
    # ------------------------------------------------------------------

    def add_expense(
        self,
        amount: float,
        category: ExpenseCategory,
        description: str,
        expense_date: date | None = None,
    ) -> Expense:
        """
        Record a new expense.

        Parameters
        ----------
        amount      : Amount in CAD (must be positive).
        category    : ExpenseCategory enum value.
        description : Human-readable description.
        expense_date: Date of expense. Defaults to today.
        """
        if amount <= 0:
            raise ValueError(f"Expense amount must be positive, got {amount}")

        expense = Expense(
            amount=round(amount, 2),
            category=category,
            description=description,
            date=expense_date or date.today(),
        )
        self._expenses.append(expense)
        logger.debug("Budget: expense added — %s $%.2f", category.value, amount)
        return expense

    def remove_expense(self, index: int) -> None:
        """Remove an expense by its list index."""
        if 0 <= index < len(self._expenses):
            removed = self._expenses.pop(index)
            logger.debug("Budget: expense removed — %s $%.2f", removed.category.value, removed.amount)

    def get_expenses(
        self,
        month: int | None = None,
        year: int | None = None,
        category: ExpenseCategory | None = None,
    ) -> list[Expense]:
        """
        Return expenses filtered by month, year, and/or category.

        All filters are optional — omitting them returns all expenses.
        """
        expenses = self._expenses
        if month is not None:
            expenses = [e for e in expenses if e.date.month == month]
        if year is not None:
            expenses = [e for e in expenses if e.date.year == year]
        if category is not None:
            expenses = [e for e in expenses if e.category == category]
        return expenses

    # ------------------------------------------------------------------
    # Monthly summary
    # ------------------------------------------------------------------

    def monthly_summary(
        self,
        month: int,
        year: int,
        income_override: float | None = None,
    ) -> BudgetSummary:
        """
        Summarise income, expenses, and savings for a given month.

        Parameters
        ----------
        month           : Month number (1–12).
        year            : Calendar year.
        income_override : Override the default monthly income for this calculation.
        """
        monthly_expenses = self.get_expenses(month=month, year=year)
        by_category = self.category_breakdown(month=month, year=year)

        total_expenses = sum(e.amount for e in monthly_expenses)
        income = income_override if income_override is not None else self.monthly_income
        net_savings = income - total_expenses
        savings_rate = round(net_savings / income, 4) if income > 0 else 0.0

        return BudgetSummary(
            total_income=round(income, 2),
            total_expenses=round(total_expenses, 2),
            net_savings=round(net_savings, 2),
            savings_rate=savings_rate,
            by_category=by_category,
            month=month,
            year=year,
        )

    def category_breakdown(
        self,
        month: int | None = None,
        year: int | None = None,
    ) -> dict[str, float]:
        """
        Return total spending per category for the given period.

        Parameters
        ----------
        month : Month filter (optional).
        year  : Year filter (optional).
        """
        expenses = self.get_expenses(month=month, year=year)
        totals: dict[str, float] = {cat.value: 0.0 for cat in ExpenseCategory}
        for expense in expenses:
            totals[expense.category.value] = round(
                totals[expense.category.value] + expense.amount, 2
            )
        # Remove zero categories for cleaner output
        return {cat: total for cat, total in totals.items() if total > 0}

    # ------------------------------------------------------------------
    # Claude-powered savings analysis
    # ------------------------------------------------------------------

    async def find_savings_opportunities(
        self,
        summary: BudgetSummary,
    ) -> list[Suggestion]:
        """
        Use Claude to identify savings opportunities from a month's spending.

        Parameters
        ----------
        summary : BudgetSummary from ``monthly_summary``.

        Returns
        -------
        List of Suggestion sorted by estimated savings (highest first).
        Falls back to rule-based suggestions if Claude is unavailable.
        """
        prompt = (
            f"CC's budget for {summary.month}/{summary.year}:\n"
            f"- Monthly income: ${summary.total_income:,.2f} CAD\n"
            f"- Total expenses: ${summary.total_expenses:,.2f} CAD\n"
            f"- Net savings: ${summary.net_savings:+,.2f} CAD\n"
            f"- Savings rate: {summary.savings_rate*100:.1f}%\n\n"
            f"Spending by category:\n"
            f"{json.dumps(summary.by_category, indent=2)}\n\n"
            "Identify 3–5 specific savings opportunities. For each, provide:\n"
            "- category: spending category\n"
            "- description: what the overspend is\n"
            "- estimated_monthly_saving: dollar amount saved per month\n"
            "- priority: HIGH | MEDIUM | LOW\n"
            "- action: the exact concrete step CC should take\n\n"
            "Respond in JSON: {\"suggestions\": [{...}, ...]}"
        )

        try:
            raw = await self._call_claude(prompt)
            parsed = self._parse_json(raw)
            raw_suggestions = parsed.get("suggestions", [])
            suggestions = [
                Suggestion(
                    category=s.get("category", ""),
                    description=s.get("description", ""),
                    estimated_monthly_saving=float(s.get("estimated_monthly_saving") or 0),
                    priority=s.get("priority", "MEDIUM"),
                    action=s.get("action", ""),
                )
                for s in raw_suggestions
                if isinstance(s, dict)
            ]
            return sorted(suggestions, key=lambda s: s.estimated_monthly_saving, reverse=True)

        except Exception as exc:
            logger.warning("Budget.find_savings_opportunities: Claude failed — %s", exc)
            return self._rule_based_suggestions(summary)

    # ------------------------------------------------------------------
    # Fallback rule-based suggestions
    # ------------------------------------------------------------------

    def _rule_based_suggestions(self, summary: BudgetSummary) -> list[Suggestion]:
        """Generate basic suggestions without Claude, based on category thresholds."""
        suggestions: list[Suggestion] = []

        thresholds = {
            ExpenseCategory.FOOD.value: (400.0, "Consider meal prepping to reduce food costs."),
            ExpenseCategory.ENTERTAINMENT.value: (200.0, "Review entertainment spend — cut one subscription or outing."),
            ExpenseCategory.SUBSCRIPTIONS.value: (100.0, "Audit subscriptions — cancel any unused services."),
            ExpenseCategory.TRANSPORT.value: (300.0, "Reduce transport costs — consider carpooling or combining trips."),
        }

        for category, (threshold, action) in thresholds.items():
            spent = summary.by_category.get(category, 0.0)
            if spent > threshold:
                saving = spent - threshold
                suggestions.append(
                    Suggestion(
                        category=category,
                        description=f"${spent:,.0f} spent on {category} exceeds ${threshold:,.0f} target.",
                        estimated_monthly_saving=round(saving, 2),
                        priority="HIGH" if saving > 100 else "MEDIUM",
                        action=action,
                    )
                )

        if summary.savings_rate < 0.20:
            suggestions.append(
                Suggestion(
                    category="Savings",
                    description=f"Savings rate is {summary.savings_rate*100:.1f}% — below 20% target.",
                    estimated_monthly_saving=round(summary.total_income * 0.20 - summary.net_savings, 2),
                    priority="HIGH",
                    action="Automate a transfer of 20% of income to savings on payday.",
                )
            )

        return sorted(suggestions, key=lambda s: s.estimated_monthly_saving, reverse=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> anthropic.AsyncAnthropic:
        """Lazy-initialise the Anthropic async client."""
        if self._client is None:
            api_key = settings.ai.anthropic_api_key
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY is not set. Add it to your .env file."
                )
            self._client = anthropic.AsyncAnthropic(api_key=api_key)
        return self._client

    async def _call_claude(self, prompt: str, max_tokens: int = 1024) -> str:
        """Call Claude with retry on rate limits."""
        import asyncio

        last_exc: Exception | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                client = self._get_client()
                response = await client.messages.create(
                    model=settings.ai.claude_model,
                    max_tokens=max_tokens,
                    system=self._SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0]
                return content.text if hasattr(content, "text") else str(content)

            except anthropic.RateLimitError as exc:
                last_exc = exc
                wait = self._BACKOFF_BASE ** attempt
                await asyncio.sleep(wait)

            except anthropic.APIStatusError as exc:
                last_exc = exc
                if exc.status_code < 500:
                    raise
                wait = self._BACKOFF_BASE ** attempt
                await asyncio.sleep(wait)

            except Exception as exc:
                raise exc

        raise RuntimeError(
            f"Budget: Claude unavailable after {self._MAX_RETRIES} retries"
        ) from last_exc

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        """Strip markdown fences and parse JSON from a Claude response."""
        text = raw.strip()
        for fence in ("```json", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
                break
        if text.endswith("```"):
            text = text[:-3]
        try:
            return json.loads(text.strip())  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return {"raw": raw}
