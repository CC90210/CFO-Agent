"""
finance/advisor.py
------------------
Financial Advisor Agent for Atlas — CC's AI-powered financial guidance engine.

Responsibilities:
- Portfolio diversification analysis and risk assessment
- Asset allocation recommendations by risk profile
- Monthly financial reviews with actionable insights
- Emergency market-crash action plans
- Goal projection with bull/base/bear scenarios

Claude is used for all qualitative reasoning. Quantitative calculations (e.g.
rebalancing deltas, goal time-to-hit) are done deterministically in Python so
results are auditable and reproducible without a Claude call.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Any

import anthropic

from config.settings import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Enumerations
# ─────────────────────────────────────────────────────────────────────────────


class RiskTolerance(str, Enum):
    """Investor risk appetite levels."""

    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class AssetClass(str, Enum):
    """Broad asset class categories tracked by Atlas."""

    CRYPTO = "Crypto"
    US_STOCKS = "US Stocks"
    CANADIAN_STOCKS = "Canadian Stocks"
    BONDS = "Bonds"
    CASH = "Cash"
    REAL_ESTATE = "Real Estate"


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PortfolioAnalysis:
    """
    Output of ``FinancialAdvisor.analyze_portfolio``.

    diversification_score : 0–100, higher is more diversified
    risk_rating           : "LOW" | "MODERATE" | "HIGH" | "VERY HIGH"
    concentration_warnings: list of human-readable warning strings
    recommendations       : list of actionable suggestion strings
    asset_weights         : symbol → weight (fraction, sums to ~1.0)
    largest_position_pct  : % of portfolio in single biggest position
    """

    diversification_score: float
    risk_rating: str
    concentration_warnings: list[str]
    recommendations: list[str]
    asset_weights: dict[str, float]
    largest_position_pct: float
    raw_insight: str = ""


@dataclass
class AllocationPlan:
    """
    Output of ``FinancialAdvisor.suggest_allocation``.

    allocations     : AssetClass → target fraction (sums to 1.0)
    reasoning       : narrative from Claude
    expected_return : annualised expected return estimate (fraction, e.g. 0.08)
    expected_risk   : annualised volatility estimate (fraction)
    rebalance_actions: list of "BUY X in Y" / "SELL X from Y" strings
    """

    allocations: dict[str, float]
    reasoning: str
    expected_return: float
    expected_risk: float
    rebalance_actions: list[str] = field(default_factory=list)


@dataclass
class MonthlyReport:
    """
    Output of ``FinancialAdvisor.monthly_review``.

    total_pnl       : net realised P&L for the month (CAD)
    win_rate        : fraction of winning trades in the month
    best_trade      : description of the best performing trade
    worst_trade     : description of the worst performing trade
    insights        : list of key observations from Claude
    next_month_plan : forward-looking action plan from Claude
    trade_count     : total trades closed in the month
    """

    total_pnl: float
    win_rate: float
    best_trade: str
    worst_trade: str
    insights: list[str]
    next_month_plan: str
    trade_count: int
    raw_response: str = ""


@dataclass
class ActionPlan:
    """
    Output of ``FinancialAdvisor.emergency_assessment``.

    severity        : "LOW" | "MODERATE" | "HIGH" | "CRITICAL"
    immediate_steps : ordered list of actions to take right now
    hold_positions  : list of positions to keep
    exit_positions  : list of positions to exit
    opportunity     : any buying opportunity identified in the dislocation
    reasoning       : full Claude rationale
    """

    severity: str
    immediate_steps: list[str]
    hold_positions: list[str]
    exit_positions: list[str]
    opportunity: str
    reasoning: str


@dataclass
class ScenarioProjection:
    """A single bull/base/bear scenario for goal tracking."""

    label: str          # "Bull" | "Base" | "Bear"
    months: int
    projected_date: date
    final_amount: float
    monthly_return: float


@dataclass
class GoalProjection:
    """
    Output of ``FinancialAdvisor.goal_tracker``.

    months_to_goal   : estimated months to reach the goal (base case)
    projected_date   : estimated calendar date (base case)
    confidence_level : 0.0–1.0 confidence in the base projection
    scenarios        : list of ScenarioProjection (bull, base, bear)
    shortfall_risk   : fraction probability the goal is NOT met in time
    """

    months_to_goal: int
    projected_date: date
    confidence_level: float
    scenarios: list[ScenarioProjection]
    shortfall_risk: float


# ─────────────────────────────────────────────────────────────────────────────
#  Target allocation templates by risk profile
# ─────────────────────────────────────────────────────────────────────────────

_TARGET_ALLOCATIONS: dict[RiskTolerance, dict[str, float]] = {
    RiskTolerance.CONSERVATIVE: {
        AssetClass.CRYPTO.value: 0.05,
        AssetClass.US_STOCKS.value: 0.25,
        AssetClass.CANADIAN_STOCKS.value: 0.20,
        AssetClass.BONDS.value: 0.30,
        AssetClass.CASH.value: 0.15,
        AssetClass.REAL_ESTATE.value: 0.05,
    },
    RiskTolerance.MODERATE: {
        AssetClass.CRYPTO.value: 0.15,
        AssetClass.US_STOCKS.value: 0.35,
        AssetClass.CANADIAN_STOCKS.value: 0.20,
        AssetClass.BONDS.value: 0.15,
        AssetClass.CASH.value: 0.10,
        AssetClass.REAL_ESTATE.value: 0.05,
    },
    RiskTolerance.AGGRESSIVE: {
        AssetClass.CRYPTO.value: 0.35,
        AssetClass.US_STOCKS.value: 0.40,
        AssetClass.CANADIAN_STOCKS.value: 0.10,
        AssetClass.BONDS.value: 0.05,
        AssetClass.CASH.value: 0.05,
        AssetClass.REAL_ESTATE.value: 0.05,
    },
}

# Expected annual return and risk by asset class (conservative estimates)
_ASSET_EXPECTED_RETURNS: dict[str, float] = {
    AssetClass.CRYPTO.value: 0.40,
    AssetClass.US_STOCKS.value: 0.10,
    AssetClass.CANADIAN_STOCKS.value: 0.08,
    AssetClass.BONDS.value: 0.04,
    AssetClass.CASH.value: 0.04,
    AssetClass.REAL_ESTATE.value: 0.07,
}

_ASSET_EXPECTED_RISKS: dict[str, float] = {
    AssetClass.CRYPTO.value: 0.80,
    AssetClass.US_STOCKS.value: 0.18,
    AssetClass.CANADIAN_STOCKS.value: 0.16,
    AssetClass.BONDS.value: 0.05,
    AssetClass.CASH.value: 0.01,
    AssetClass.REAL_ESTATE.value: 0.12,
}

# Rebalancing fires when actual weight drifts more than this from target
_REBALANCE_DRIFT_THRESHOLD = 0.05


# ─────────────────────────────────────────────────────────────────────────────
#  Financial Advisor Agent
# ─────────────────────────────────────────────────────────────────────────────


class FinancialAdvisor:
    """
    AI-powered financial advisor for CC.

    All Claude calls use the same retry/parse pattern established in
    ``BaseAnalystAgent`` but without inheriting from it — this class is not
    a trading analyst, it is a standalone advisor.

    Parameters
    ----------
    risk_tolerance : Default risk profile used when none is passed to methods.
    """

    _MAX_RETRIES: int = 3
    _BACKOFF_BASE: float = 1.5

    _SYSTEM_PROMPT = (
        "You are Atlas, an elite financial advisor and wealth strategist for a "
        "22-year-old Canadian entrepreneur named CC (Conaugh McKenna) based in "
        "Collingwood, Ontario. He runs OASIS AI Solutions and earns ~$2,191/month "
        "MRR. Your advice must be specific, actionable, and grounded in Canadian "
        "tax and investment laws. Always consider TFSA, RRSP, and FHSA account "
        "optimization. Be direct, skip filler language."
    )

    def __init__(self, risk_tolerance: RiskTolerance = RiskTolerance.MODERATE) -> None:
        self.risk_tolerance = risk_tolerance
        self._client: anthropic.AsyncAnthropic | None = None

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    async def analyze_portfolio(
        self,
        holdings: dict[str, dict[str, float]],
    ) -> PortfolioAnalysis:
        """
        Assess diversification, risk exposure, and concentration of a portfolio.

        Parameters
        ----------
        holdings : dict mapping symbol → {"value_cad": float, "asset_class": str}
                   e.g. {"BTC": {"value_cad": 5000, "asset_class": "Crypto"}}

        Returns
        -------
        PortfolioAnalysis with deterministic metrics + Claude qualitative insight.
        """
        if not holdings:
            return PortfolioAnalysis(
                diversification_score=0.0,
                risk_rating="UNKNOWN",
                concentration_warnings=["Portfolio is empty."],
                recommendations=["Start building your portfolio."],
                asset_weights={},
                largest_position_pct=0.0,
            )

        total_value = sum(h["value_cad"] for h in holdings.values())
        if total_value <= 0:
            return PortfolioAnalysis(
                diversification_score=0.0,
                risk_rating="UNKNOWN",
                concentration_warnings=["Portfolio has zero value."],
                recommendations=["Deposit capital to begin investing."],
                asset_weights={},
                largest_position_pct=0.0,
            )

        # Build per-asset-class weights
        asset_class_values: dict[str, float] = {}
        for symbol, data in holdings.items():
            ac = data.get("asset_class", "Other")
            asset_class_values[ac] = asset_class_values.get(ac, 0.0) + data["value_cad"]

        asset_weights = {ac: v / total_value for ac, v in asset_class_values.items()}
        largest_position_pct = max(asset_weights.values()) * 100

        # Herfindahl-Hirschman Index → diversification score (0–100)
        hhi = sum(w**2 for w in asset_weights.values())
        diversification_score = round((1 - hhi) * 100, 1)

        # Risk rating based on crypto concentration
        crypto_pct = asset_weights.get(AssetClass.CRYPTO.value, 0.0)
        if crypto_pct >= 0.60:
            risk_rating = "VERY HIGH"
        elif crypto_pct >= 0.40:
            risk_rating = "HIGH"
        elif crypto_pct >= 0.20:
            risk_rating = "MODERATE"
        else:
            risk_rating = "LOW"

        # Concentration warnings
        warnings: list[str] = []
        for ac, weight in asset_weights.items():
            if weight > 0.50:
                warnings.append(
                    f"{ac} is {weight * 100:.1f}% of portfolio — dangerously concentrated."
                )
            elif weight > 0.35:
                warnings.append(
                    f"{ac} at {weight * 100:.1f}% — consider trimming to reduce single-asset risk."
                )

        # Claude qualitative insight
        prompt = (
            f"Portfolio breakdown (CAD values):\n"
            f"{json.dumps({k: v['value_cad'] for k, v in holdings.items()}, indent=2)}\n\n"
            f"Asset-class weights: {json.dumps({k: f'{v*100:.1f}%' for k, v in asset_weights.items()}, indent=2)}\n"
            f"Total value: ${total_value:,.0f} CAD\n"
            f"Diversification score: {diversification_score}/100\n"
            f"Risk profile: {self.risk_tolerance.value}\n\n"
            "Provide 3–5 specific, prioritised recommendations. "
            "Respond in JSON: {\"recommendations\": [\"...\", ...]}"
        )

        raw_insight = ""
        recommendations: list[str] = []
        try:
            raw_insight = await self._call_claude(prompt)
            parsed = self._parse_json(raw_insight)
            recommendations = parsed.get("recommendations", [])
        except Exception as exc:
            logger.warning("FinancialAdvisor.analyze_portfolio: Claude failed — %s", exc)
            recommendations = [
                "Diversify across asset classes to reduce single-asset risk.",
                "Ensure you hold 3–6 months of living expenses in cash.",
                "Max out TFSA annually for tax-free growth.",
            ]

        return PortfolioAnalysis(
            diversification_score=diversification_score,
            risk_rating=risk_rating,
            concentration_warnings=warnings,
            recommendations=recommendations,
            asset_weights=asset_weights,
            largest_position_pct=largest_position_pct,
            raw_insight=raw_insight,
        )

    async def suggest_allocation(
        self,
        risk_tolerance: RiskTolerance,
        capital: float,
        goals: list[str],
    ) -> AllocationPlan:
        """
        Recommend an asset allocation and rebalancing actions.

        Parameters
        ----------
        risk_tolerance : Investor risk profile.
        capital        : Total investable capital in CAD.
        goals          : List of financial goals, e.g. ["Buy house by 2028", "FIRE by 40"].

        Returns
        -------
        AllocationPlan with target weights, expected return/risk, and actions.
        """
        target = _TARGET_ALLOCATIONS[risk_tolerance]

        # Compute blended expected return and risk
        expected_return = sum(
            weight * _ASSET_EXPECTED_RETURNS.get(ac, 0.08)
            for ac, weight in target.items()
        )
        expected_risk = sum(
            weight * _ASSET_EXPECTED_RISKS.get(ac, 0.15)
            for ac, weight in target.items()
        )

        # Dollar amounts per asset class
        dollar_allocations = {ac: weight * capital for ac, weight in target.items()}

        prompt = (
            f"Risk profile: {risk_tolerance.value}\n"
            f"Investable capital: ${capital:,.0f} CAD\n"
            f"Financial goals: {goals}\n\n"
            f"Recommended target allocation:\n"
            f"{json.dumps({k: f'{v*100:.0f}% (${capital*v:,.0f})' for k, v in target.items()}, indent=2)}\n\n"
            f"Expected annual return: {expected_return*100:.1f}%\n"
            f"Expected annual volatility: {expected_risk*100:.1f}%\n\n"
            "Write a concise (150-word max) rationale for this allocation given the goals. "
            "Then list 3–5 specific rebalancing or investment actions CC should take this week. "
            "Respond in JSON: {\"reasoning\": \"...\", \"rebalance_actions\": [\"...\", ...]}"
        )

        reasoning = ""
        rebalance_actions: list[str] = []
        try:
            raw = await self._call_claude(prompt)
            parsed = self._parse_json(raw)
            reasoning = parsed.get("reasoning", "")
            rebalance_actions = parsed.get("rebalance_actions", [])
        except Exception as exc:
            logger.warning("FinancialAdvisor.suggest_allocation: Claude failed — %s", exc)
            reasoning = (
                f"A {risk_tolerance.value.lower()} allocation balances growth with downside protection. "
                f"With ${capital:,.0f} CAD, this split targets {expected_return*100:.1f}% annual return."
            )
            rebalance_actions = [
                f"Invest ${dollar_allocations.get(ac, 0):,.0f} in {ac}."
                for ac in target
            ]

        return AllocationPlan(
            allocations={ac: round(w, 4) for ac, w in target.items()},
            reasoning=reasoning,
            expected_return=round(expected_return, 4),
            expected_risk=round(expected_risk, 4),
            rebalance_actions=rebalance_actions,
        )

    async def monthly_review(
        self,
        trades: list[dict[str, Any]],
        pnl: float,
        portfolio: dict[str, Any],
    ) -> MonthlyReport:
        """
        Produce a comprehensive monthly financial review.

        Parameters
        ----------
        trades    : List of closed-trade dicts from db (must include pnl, symbol, strategy).
        pnl       : Total net realised P&L for the month in CAD.
        portfolio : Current portfolio state (from PortfolioManager.build_portfolio_state()).

        Returns
        -------
        MonthlyReport with stats and Claude-generated insights.
        """
        trade_count = len(trades)
        wins = [t for t in trades if (t.get("pnl") or 0) > 0]
        losses = [t for t in trades if (t.get("pnl") or 0) <= 0]
        win_rate = len(wins) / trade_count if trade_count > 0 else 0.0

        best_trade = "No trades this month."
        worst_trade = "No trades this month."
        if wins:
            best = max(wins, key=lambda t: t.get("pnl") or 0)
            best_trade = f"{best.get('symbol', 'N/A')} +${best.get('pnl', 0):.2f} ({best.get('strategy', '')})"
        if losses:
            worst = min(losses, key=lambda t: t.get("pnl") or 0)
            worst_trade = f"{worst.get('symbol', 'N/A')} ${worst.get('pnl', 0):.2f} ({worst.get('strategy', '')})"

        prompt = (
            f"Monthly trading summary:\n"
            f"- Net P&L: ${pnl:+,.2f} CAD\n"
            f"- Total trades: {trade_count}\n"
            f"- Win rate: {win_rate*100:.1f}%\n"
            f"- Best trade: {best_trade}\n"
            f"- Worst trade: {worst_trade}\n"
            f"- Portfolio state: {json.dumps(portfolio, default=str)}\n\n"
            "Provide: (1) 3–5 key insights from this month's performance, "
            "(2) a focused action plan for next month covering trading strategy, "
            "tax optimisation, and wealth building. "
            "Respond in JSON: {\"insights\": [\"...\", ...], \"next_month_plan\": \"...\"}"
        )

        insights: list[str] = []
        next_month_plan = ""
        raw_response = ""
        try:
            raw_response = await self._call_claude(prompt)
            parsed = self._parse_json(raw_response)
            insights = parsed.get("insights", [])
            next_month_plan = parsed.get("next_month_plan", "")
        except Exception as exc:
            logger.warning("FinancialAdvisor.monthly_review: Claude failed — %s", exc)
            insights = [
                f"Win rate: {win_rate*100:.1f}% — {'above' if win_rate > 0.5 else 'below'} 50% target.",
                f"Net P&L: ${pnl:+,.2f} CAD for the month.",
                "Review position sizing on losing trades.",
            ]
            next_month_plan = "Continue current strategy. Review stop-loss discipline."

        return MonthlyReport(
            total_pnl=pnl,
            win_rate=win_rate,
            best_trade=best_trade,
            worst_trade=worst_trade,
            insights=insights,
            next_month_plan=next_month_plan,
            trade_count=trade_count,
            raw_response=raw_response,
        )

    async def emergency_assessment(
        self,
        event: dict[str, Any],
    ) -> ActionPlan:
        """
        Produce an action plan during a market crash or black-swan event.

        Parameters
        ----------
        event : dict describing the event, e.g.:
                {"type": "market_crash", "btc_drawdown_pct": -30,
                 "portfolio_drawdown_pct": -25, "current_holdings": {...}}

        Returns
        -------
        ActionPlan with immediate steps, hold/exit lists, and opportunity notes.
        """
        prompt = (
            f"EMERGENCY MARKET EVENT:\n{json.dumps(event, indent=2, default=str)}\n\n"
            "As CC's financial advisor, assess the situation and provide:\n"
            "1. severity: LOW | MODERATE | HIGH | CRITICAL\n"
            "2. immediate_steps: ordered list of actions to take RIGHT NOW\n"
            "3. hold_positions: assets/positions to hold through the event\n"
            "4. exit_positions: assets/positions to exit or hedge immediately\n"
            "5. opportunity: any buying opportunities this dislocation creates\n"
            "6. reasoning: 100-word rationale\n\n"
            "Respond in JSON with those exact keys."
        )

        severity = "MODERATE"
        immediate_steps: list[str] = [
            "Do not panic sell into the dip.",
            "Check portfolio drawdown against your max-drawdown limit.",
            "Review stop-loss orders — ensure they are active.",
            "Preserve cash for potential re-entry at better prices.",
        ]
        hold_positions: list[str] = []
        exit_positions: list[str] = []
        opportunity = "Assess in 24–48 hours once volatility settles."
        reasoning = "Awaiting Claude assessment."

        try:
            raw = await self._call_claude(prompt, max_tokens=1024)
            parsed = self._parse_json(raw)
            severity = parsed.get("severity", severity)
            immediate_steps = parsed.get("immediate_steps", immediate_steps)
            hold_positions = parsed.get("hold_positions", hold_positions)
            exit_positions = parsed.get("exit_positions", exit_positions)
            opportunity = parsed.get("opportunity", opportunity)
            reasoning = parsed.get("reasoning", reasoning)
        except Exception as exc:
            logger.warning("FinancialAdvisor.emergency_assessment: Claude failed — %s", exc)

        return ActionPlan(
            severity=severity,
            immediate_steps=immediate_steps,
            hold_positions=hold_positions,
            exit_positions=exit_positions,
            opportunity=opportunity,
            reasoning=reasoning,
        )

    async def goal_tracker(
        self,
        goal_amount: float,
        current_amount: float,
        monthly_contribution: float,
        avg_return: float,
    ) -> GoalProjection:
        """
        Project when CC hits a financial goal under bull/base/bear scenarios.

        Parameters
        ----------
        goal_amount          : Target amount in CAD (e.g. 100_000.0).
        current_amount       : Current savings/investment balance in CAD.
        monthly_contribution : Amount added each month in CAD.
        avg_return           : Expected annual return as a fraction (e.g. 0.08 = 8%).

        Returns
        -------
        GoalProjection with months-to-goal and three scenarios.
        """
        if current_amount >= goal_amount:
            today = date.today()
            return GoalProjection(
                months_to_goal=0,
                projected_date=today,
                confidence_level=1.0,
                scenarios=[
                    ScenarioProjection("Base", 0, today, current_amount, avg_return / 12),
                ],
                shortfall_risk=0.0,
            )

        # Monthly return rates for each scenario
        scenario_returns = {
            "Bull": avg_return * 1.5 / 12,
            "Base": avg_return / 12,
            "Bear": avg_return * 0.4 / 12,
        }

        scenarios: list[ScenarioProjection] = []
        for label, monthly_rate in scenario_returns.items():
            months, final_amount = self._months_to_goal(
                current_amount, goal_amount, monthly_contribution, monthly_rate
            )
            projected_date = date.today() + timedelta(days=months * 30.44)
            scenarios.append(
                ScenarioProjection(
                    label=label,
                    months=months,
                    projected_date=projected_date,
                    final_amount=round(final_amount, 2),
                    monthly_return=monthly_rate,
                )
            )

        base = next(s for s in scenarios if s.label == "Base")
        bear = next(s for s in scenarios if s.label == "Bear")

        # Shortfall risk: crude estimate — if bear scenario takes >2x base, high risk
        shortfall_ratio = bear.months / base.months if base.months > 0 else 2.0
        shortfall_risk = round(min(1.0, (shortfall_ratio - 1.0) / 3.0), 3)

        # Confidence degrades with distance — beyond 10 years, <50% confidence
        confidence = max(0.1, 1.0 - base.months / 240.0)

        return GoalProjection(
            months_to_goal=base.months,
            projected_date=base.projected_date,
            confidence_level=round(confidence, 3),
            scenarios=scenarios,
            shortfall_risk=shortfall_risk,
        )

    # ------------------------------------------------------------------
    # Rebalancing helper
    # ------------------------------------------------------------------

    def compute_rebalancing_actions(
        self,
        current_weights: dict[str, float],
        risk_tolerance: RiskTolerance,
        total_portfolio_value: float,
    ) -> list[str]:
        """
        Return a list of rebalancing actions when any asset class has drifted
        more than ``_REBALANCE_DRIFT_THRESHOLD`` (default 5%) from its target.

        Returns an empty list when no rebalancing is required.
        """
        target = _TARGET_ALLOCATIONS[risk_tolerance]
        actions: list[str] = []

        for asset_class, target_weight in target.items():
            current = current_weights.get(asset_class, 0.0)
            drift = current - target_weight
            if abs(drift) > _REBALANCE_DRIFT_THRESHOLD:
                direction = "SELL" if drift > 0 else "BUY"
                dollar_delta = abs(drift) * total_portfolio_value
                actions.append(
                    f"{direction} ${dollar_delta:,.0f} of {asset_class} "
                    f"(currently {current*100:.1f}%, target {target_weight*100:.1f}%)"
                )

        return actions

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

    async def _call_claude(self, prompt: str, max_tokens: int = 2048) -> str:
        """Call Claude with the advisor system prompt and retry on rate limits."""
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
                logger.warning("FinancialAdvisor: rate-limited (attempt %d). Waiting %.1fs.", attempt, wait)
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
            f"FinancialAdvisor: Claude unavailable after {self._MAX_RETRIES} retries"
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

    @staticmethod
    def _months_to_goal(
        current: float,
        goal: float,
        monthly_contribution: float,
        monthly_rate: float,
    ) -> tuple[int, float]:
        """
        Iterate month-by-month to find when balance reaches the goal.

        Returns (months, final_balance). Capped at 600 months (50 years)
        to prevent infinite loops when the rate is very low.
        """
        balance = current
        for month in range(1, 601):
            balance = balance * (1 + monthly_rate) + monthly_contribution
            if balance >= goal:
                return month, balance
        return 600, balance
