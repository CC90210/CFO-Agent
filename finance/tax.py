"""
finance/tax.py
--------------
Canadian Tax Calculator & Strategist for Atlas.

CRA Rules Implemented
---------------------
1. Capital gains inclusion rate:
   - 50% for net gains up to $250,000/year (pre-June 25, 2024 and continuing for
     individuals below the threshold)
   - 66.67% (2/3) for gains ABOVE $250,000/year (effective June 25, 2024)
2. Crypto as property — every trade is a taxable disposition; ACB (Adjusted Cost
   Base) method is used for cost tracking.
3. Business income vs capital gains — frequent trading activity may be classified
   as business income by CRA (100% inclusion). Warning is raised when trade
   frequency suggests business income treatment is possible.
4. TFSA: gains are completely TAX FREE. Contribution room: $7,000/year (2024+).
5. RRSP: contributions are tax-deductible, withdrawals taxed as income.
6. FHSA: $8,000/year, deductible, tax-free for first home purchase.

Tax Brackets (2024 — updated annually by CRA):
Federal and Ontario provincial brackets included.

DISCLAIMER: This module provides estimates for planning purposes only.
CC should consult a CPA for final filing. Numbers are accurate as of 2024.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  2024 Federal Tax Brackets (income after personal exemption adjustments)
# ─────────────────────────────────────────────────────────────────────────────

# Format: (upper_limit, rate)  — last entry has no upper limit
_FEDERAL_BRACKETS: list[tuple[float, float]] = [
    (55_867.0, 0.15),
    (111_733.0, 0.205),
    (154_906.0, 0.26),
    (220_000.0, 0.29),
    (float("inf"), 0.33),
]

# Basic personal amount 2024 (federal)
_FEDERAL_BASIC_PERSONAL = 15_705.0

# ─────────────────────────────────────────────────────────────────────────────
#  2024 Ontario Provincial Tax Brackets
# ─────────────────────────────────────────────────────────────────────────────

_ONTARIO_BRACKETS: list[tuple[float, float]] = [
    (51_446.0, 0.0505),
    (102_894.0, 0.0915),
    (150_000.0, 0.1116),
    (220_000.0, 0.1216),
    (float("inf"), 0.1316),
]

# Ontario basic personal amount 2024
_ONTARIO_BASIC_PERSONAL = 11_865.0

# ─────────────────────────────────────────────────────────────────────────────
#  Capital Gains Inclusion Rates
# ─────────────────────────────────────────────────────────────────────────────

# Below this threshold: 50% inclusion rate
_CAPITAL_GAINS_LOWER_THRESHOLD = 250_000.0
_INCLUSION_RATE_LOWER = 0.50   # 50%
_INCLUSION_RATE_UPPER = 2 / 3  # ~66.67% — effective June 25, 2024

# Business income warning: > 30 round-trip trades in a year is a signal
_BUSINESS_INCOME_TRADE_THRESHOLD = 30

# Quarterly instalment due dates (CRA)
_QUARTERLY_DUE_DATES: dict[int, str] = {
    1: "March 15",
    2: "June 15",
    3: "September 15",
    4: "December 15",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class TaxSummary:
    """
    Full capital gains tax summary for a given year.

    total_proceeds      : Sum of all sale proceeds (CAD)
    total_cost_basis    : Sum of ACB for all disposed assets (CAD)
    capital_gains       : Gross capital gains (proceeds - cost_basis, positive only)
    capital_losses      : Gross capital losses (absolute value, positive)
    net_gain            : capital_gains - capital_losses (can be negative)
    taxable_amount      : Amount actually included in income (after inclusion rate)
    tax_owing_estimate  : Estimated combined federal + Ontario tax on taxable_amount
    inclusion_rate      : Effective inclusion rate applied (0.50 or 0.667)
    is_business_income  : True when CRA may reclassify gains as business income
    business_income_warning: Explanation if is_business_income is True
    trade_count         : Number of dispositions in the tax year
    """

    total_proceeds: float
    total_cost_basis: float
    capital_gains: float
    capital_losses: float
    net_gain: float
    taxable_amount: float
    tax_owing_estimate: float
    inclusion_rate: float
    is_business_income: bool
    business_income_warning: str
    trade_count: int


@dataclass
class HarvestOpportunity:
    """
    A tax-loss harvesting candidate.

    symbol               : Asset symbol
    unrealized_loss      : Negative dollar amount (CAD)
    tax_benefit_estimate : Estimated tax saved by realising the loss (CAD)
    wash_sale_warning    : Canada does not have a formal wash-sale rule, but
                           CRA can use GAAR (General Anti-Avoidance Rule) if the
                           sale is deemed to lack economic substance.
    acb                  : Adjusted Cost Base per unit (CAD)
    current_price        : Current market price per unit (CAD)
    quantity             : Number of units held
    """

    symbol: str
    unrealized_loss: float
    tax_benefit_estimate: float
    wash_sale_warning: str
    acb: float
    current_price: float
    quantity: float


@dataclass
class QuarterlyEstimate:
    """
    Quarterly tax instalment estimate.

    federal_tax          : Federal portion owing
    provincial_tax       : Ontario provincial portion owing
    total_estimated      : Combined estimate
    due_date             : CRA quarterly due date string
    quarter              : 1–4
    ytd_income           : Year-to-date business/employment income used for estimate
    ytd_capital_gains    : Year-to-date net taxable capital gains
    """

    federal_tax: float
    provincial_tax: float
    total_estimated: float
    due_date: str
    quarter: int
    ytd_income: float
    ytd_capital_gains: float


@dataclass
class AccountStrategy:
    """
    Account placement strategy (what to hold where).

    tfsa_holdings    : List of assets suited to TFSA (tax-free growth)
    rrsp_holdings    : List of assets suited to RRSP (tax-deferred)
    fhsa_holdings    : List of assets suited to FHSA (first home savings)
    taxable_holdings : List of assets to hold in non-registered accounts
    reasoning        : Explanation of placement decisions
    estimated_annual_savings: Estimated annual tax savings from optimal placement (CAD)
    """

    tfsa_holdings: list[str]
    rrsp_holdings: list[str]
    fhsa_holdings: list[str]
    taxable_holdings: list[str]
    reasoning: str
    estimated_annual_savings: float


@dataclass
class TaxReport:
    """
    Full exportable tax report for CRA filing preparation.

    tax_year         : Calendar year
    summary          : TaxSummary
    trade_log        : List of dicts — each disposition with proceeds, acb, gain/loss
    t5008_rows       : T5008 (securities transactions) data rows
    schedule3_lines  : Schedule 3 (capital gains) summary lines
    notes            : List of important notes/warnings for the filer
    generated_at     : Timestamp of report generation
    """

    tax_year: int
    summary: TaxSummary
    trade_log: list[dict[str, Any]]
    t5008_rows: list[dict[str, Any]]
    schedule3_lines: list[dict[str, Any]]
    notes: list[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Deduction:
    """A potential business expense deduction."""

    description: str
    amount: float
    cra_reference: str   # e.g. "ITA s. 18(1)(a)"
    confidence: str      # "HIGH" | "MEDIUM" | "LOW"
    notes: str


# ─────────────────────────────────────────────────────────────────────────────
#  CRA Tax Calculator
# ─────────────────────────────────────────────────────────────────────────────


class CryptoTaxCalculator:
    """
    Canadian tax calculator for crypto and general capital gains.

    Uses the Adjusted Cost Base (ACB) method as required by CRA.
    ACB is tracked per symbol across all tax years for accurate
    cross-year carry-forward calculations.

    Usage
    -----
    calculator = CryptoTaxCalculator()
    summary = calculator.calculate_capital_gains_tax(trades, 2025)
    report = calculator.generate_tax_report(trades, 2025)
    """

    def __init__(self) -> None:
        # ACB tracking: symbol → {"total_units": float, "total_cost": float}
        self._acb_ledger: dict[str, dict[str, float]] = {}

    # ------------------------------------------------------------------
    # Core tax calculation
    # ------------------------------------------------------------------

    def calculate_capital_gains_tax(
        self,
        trades: list[dict[str, Any]],
        tax_year: int,
    ) -> TaxSummary:
        """
        Compute capital gains / losses from a list of trade dicts for a tax year.

        Each trade dict must have:
        - symbol         : str  (e.g. "BTC", "ETH", "AAPL")
        - side           : str  "buy" | "sell"
        - size           : float  (units)
        - entry_price    : float  (CAD per unit, used for buys)
        - exit_price     : float | None  (CAD per unit, used for sells)
        - fees           : float  (CAD — added to cost for buys, subtracted from proceeds for sells)
        - opened_at      : datetime or ISO string
        - closed_at      : datetime or ISO string | None

        BUY trades: update ACB ledger.
        SELL trades: compute gain/loss using ACB.
        """
        self._acb_ledger.clear()  # Start fresh for this calculation

        year_trades = [
            t for t in trades
            if self._trade_year(t) == tax_year
        ]

        # Process ALL trades in chronological order so ACB is correct
        all_sorted = sorted(trades, key=lambda t: self._trade_date(t))

        total_proceeds = 0.0
        total_cost_basis = 0.0
        capital_gains = 0.0
        capital_losses = 0.0

        sell_count = 0

        for trade in all_sorted:
            symbol = trade.get("symbol", "UNKNOWN").split("/")[0]  # "BTC/USDT" → "BTC"
            side = (trade.get("side") or "").lower()
            size = float(trade.get("size") or 0)
            fees = float(trade.get("fees") or 0)

            if side == "buy":
                price = float(trade.get("entry_price") or 0)
                cost = size * price + fees  # Fees increase ACB
                self._update_acb(symbol, size, cost)

            elif side == "sell" and self._trade_year(trade) == tax_year:
                price = float(trade.get("exit_price") or 0)
                if price <= 0:
                    continue
                proceeds = size * price - fees  # Fees reduce proceeds
                acb_per_unit = self._get_acb_per_unit(symbol)
                cost_basis = size * acb_per_unit

                gain = proceeds - cost_basis

                total_proceeds += proceeds
                total_cost_basis += cost_basis
                sell_count += 1

                if gain > 0:
                    capital_gains += gain
                else:
                    capital_losses += abs(gain)

                # Reduce ACB ledger for disposed units
                self._reduce_acb(symbol, size)

        net_gain = capital_gains - capital_losses

        # Apply inclusion rates
        taxable_amount, inclusion_rate = self._apply_inclusion_rate(net_gain)
        tax_owing = self._estimate_tax(taxable_amount)

        # Business income check
        is_business = sell_count >= _BUSINESS_INCOME_TRADE_THRESHOLD
        warning = ""
        if is_business:
            warning = (
                f"You made {sell_count} dispositions in {tax_year}. "
                "CRA may treat frequent crypto trading as business income, "
                "which is 100% taxable (not 50%/66.67%). "
                "Consult a CPA to assess your situation."
            )

        return TaxSummary(
            total_proceeds=round(total_proceeds, 2),
            total_cost_basis=round(total_cost_basis, 2),
            capital_gains=round(capital_gains, 2),
            capital_losses=round(capital_losses, 2),
            net_gain=round(net_gain, 2),
            taxable_amount=round(taxable_amount, 2),
            tax_owing_estimate=round(tax_owing, 2),
            inclusion_rate=inclusion_rate,
            is_business_income=is_business,
            business_income_warning=warning,
            trade_count=len(year_trades),
        )

    # ------------------------------------------------------------------
    # Tax-loss harvesting
    # ------------------------------------------------------------------

    def suggest_tax_loss_harvesting(
        self,
        positions: list[dict[str, Any]],
        marginal_rate: float = 0.40,
    ) -> list[HarvestOpportunity]:
        """
        Find unrealised losses that could be realised to offset capital gains.

        Parameters
        ----------
        positions     : List of dicts with keys: symbol, quantity, current_price,
                        average_cost (CAD per unit)
        marginal_rate : Approximate combined marginal tax rate for benefit estimate.
                        Defaults to 40% (reasonable for ~$100K income in Ontario).

        Returns
        -------
        List of HarvestOpportunity sorted by largest benefit first.
        Note: Canada has no wash-sale rule, but CRA GAAR may apply if the
        trade lacks genuine commercial purpose.
        """
        opportunities: list[HarvestOpportunity] = []

        for pos in positions:
            symbol = pos.get("symbol", "")
            quantity = float(pos.get("quantity") or 0)
            current_price = float(pos.get("current_price") or 0)
            avg_cost = float(pos.get("average_cost") or pos.get("acb") or 0)

            if quantity <= 0 or current_price <= 0:
                continue

            unrealised_pnl = (current_price - avg_cost) * quantity
            if unrealised_pnl >= 0:
                continue  # Only interested in losses

            # Tax benefit = loss × inclusion_rate × marginal_rate
            # Using 50% inclusion as conservative estimate
            tax_benefit = abs(unrealised_pnl) * _INCLUSION_RATE_LOWER * marginal_rate

            opportunities.append(
                HarvestOpportunity(
                    symbol=symbol,
                    unrealized_loss=round(unrealised_pnl, 2),
                    tax_benefit_estimate=round(tax_benefit, 2),
                    wash_sale_warning=(
                        "Canada has no formal wash-sale rule, but CRA GAAR "
                        "may disallow the loss if you immediately repurchase "
                        "the same asset without genuine commercial purpose."
                    ),
                    acb=round(avg_cost, 4),
                    current_price=round(current_price, 4),
                    quantity=quantity,
                )
            )

        return sorted(opportunities, key=lambda o: o.tax_benefit_estimate, reverse=True)

    # ------------------------------------------------------------------
    # Quarterly tax instalments
    # ------------------------------------------------------------------

    def estimate_quarterly_taxes(
        self,
        ytd_income: float,
        ytd_capital_gains: float,
    ) -> QuarterlyEstimate:
        """
        Estimate how much to set aside for the current CRA quarterly instalment.

        CRA requires quarterly instalments when your net tax owing exceeds
        $3,000 in the current OR either of the two previous years.

        Parameters
        ----------
        ytd_income        : Year-to-date employment / business income (CAD).
        ytd_capital_gains : Year-to-date net realised capital gains (CAD).
        """
        today = date.today()
        quarter = (today.month - 1) // 3 + 1

        # Annualise YTD figures
        months_elapsed = today.month
        annualisation_factor = 12.0 / months_elapsed

        projected_income = ytd_income * annualisation_factor
        projected_gains = ytd_capital_gains * annualisation_factor

        # Taxable capital gains (50% inclusion for sub-$250K)
        taxable_gains, _ = self._apply_inclusion_rate(projected_gains)
        total_taxable_income = projected_income + taxable_gains

        federal_annual = self._calculate_bracket_tax(
            total_taxable_income - _FEDERAL_BASIC_PERSONAL,
            _FEDERAL_BRACKETS,
        )
        ontario_annual = self._calculate_bracket_tax(
            total_taxable_income - _ONTARIO_BASIC_PERSONAL,
            _ONTARIO_BRACKETS,
        )

        # Quarterly portion
        quarterly_federal = max(0.0, federal_annual / 4)
        quarterly_ontario = max(0.0, ontario_annual / 4)
        total = quarterly_federal + quarterly_ontario

        return QuarterlyEstimate(
            federal_tax=round(quarterly_federal, 2),
            provincial_tax=round(quarterly_ontario, 2),
            total_estimated=round(total, 2),
            due_date=_QUARTERLY_DUE_DATES.get(quarter, "December 15"),
            quarter=quarter,
            ytd_income=ytd_income,
            ytd_capital_gains=ytd_capital_gains,
        )

    # ------------------------------------------------------------------
    # Account placement optimisation
    # ------------------------------------------------------------------

    def optimize_account_placement(
        self,
        holdings: list[dict[str, Any]],
        tfsa_room_available: float = 7000.0,
        has_fhsa: bool = True,
    ) -> AccountStrategy:
        """
        Recommend what to hold in TFSA, RRSP, FHSA, and taxable accounts.

        Parameters
        ----------
        holdings          : List of dicts: {"symbol": str, "asset_class": str,
                            "value_cad": float, "expected_return": float (annual)}
        tfsa_room_available: Available TFSA contribution room in CAD.
        has_fhsa          : Whether CC has an FHSA open.
        """
        # Sort by expected return — highest return assets benefit most from TFSA
        sorted_holdings = sorted(
            holdings,
            key=lambda h: float(h.get("expected_return") or 0),
            reverse=True,
        )

        tfsa_holdings: list[str] = []
        rrsp_holdings: list[str] = []
        fhsa_holdings: list[str] = []
        taxable_holdings: list[str] = []

        tfsa_filled = 0.0
        fhsa_room = 8000.0 if has_fhsa else 0.0
        fhsa_filled = 0.0

        for holding in sorted_holdings:
            symbol = holding.get("symbol", "")
            value = float(holding.get("value_cad") or 0)
            asset_class = holding.get("asset_class", "")

            # High-growth assets → TFSA first (tax-free compounding)
            if tfsa_filled + value <= tfsa_room_available:
                tfsa_holdings.append(symbol)
                tfsa_filled += value

            # Cash or stable assets → FHSA (if CC plans to buy a home)
            elif asset_class in ("Cash", "Bonds") and fhsa_filled + value <= fhsa_room and has_fhsa:
                fhsa_holdings.append(symbol)
                fhsa_filled += value

            # Canadian dividend stocks → RRSP (US withholding tax exemption)
            elif asset_class == "Canadian Stocks":
                rrsp_holdings.append(symbol)

            else:
                taxable_holdings.append(symbol)

        # Estimate tax savings from TFSA usage (rough: avg 8% return × tfsa_filled × marginal rate)
        estimated_savings = tfsa_filled * 0.08 * 0.40

        reasoning = (
            f"Highest-return assets ({', '.join(tfsa_holdings[:3]) or 'none'}) placed in TFSA "
            f"for tax-free compounding. "
            f"FHSA used for stable assets if CC is saving for a first home. "
            f"Canadian dividend stocks in RRSP benefit from the dividend tax credit in non-registered, "
            f"but RRSP provides tax deferral on interest-bearing assets. "
            f"Estimated annual tax saving from TFSA optimisation: ${estimated_savings:,.0f} CAD."
        )

        return AccountStrategy(
            tfsa_holdings=tfsa_holdings,
            rrsp_holdings=rrsp_holdings,
            fhsa_holdings=fhsa_holdings,
            taxable_holdings=taxable_holdings,
            reasoning=reasoning,
            estimated_annual_savings=round(estimated_savings, 2),
        )

    # ------------------------------------------------------------------
    # Full tax report generation
    # ------------------------------------------------------------------

    def generate_tax_report(
        self,
        trades: list[dict[str, Any]],
        year: int,
    ) -> TaxReport:
        """
        Generate a complete CRA-ready tax report for the given year.

        Includes:
        - TaxSummary (Schedule 3 inputs)
        - Itemised trade log with ACB and gain/loss per disposition
        - T5008 rows (securities transactions)
        - Schedule 3 summary lines
        - Filing notes and warnings
        """
        summary = self.calculate_capital_gains_tax(trades, year)

        year_trades = sorted(
            [t for t in trades if self._trade_year(t) == year and
             (t.get("side") or "").lower() == "sell"],
            key=lambda t: self._trade_date(t),
        )

        # Rebuild ACB pass for the trade log (need a fresh run to get per-trade ACB)
        acb_tracker: dict[str, dict[str, float]] = {}
        all_sorted = sorted(trades, key=lambda t: self._trade_date(t))
        trade_log: list[dict[str, Any]] = []
        t5008_rows: list[dict[str, Any]] = []

        for trade in all_sorted:
            symbol = trade.get("symbol", "UNKNOWN").split("/")[0]
            side = (trade.get("side") or "").lower()
            size = float(trade.get("size") or 0)
            fees = float(trade.get("fees") or 0)
            trade_date = self._trade_date(trade)

            if symbol not in acb_tracker:
                acb_tracker[symbol] = {"total_units": 0.0, "total_cost": 0.0}

            if side == "buy":
                price = float(trade.get("entry_price") or 0)
                cost = size * price + fees
                acb_tracker[symbol]["total_units"] += size
                acb_tracker[symbol]["total_cost"] += cost

            elif side == "sell" and trade_date.year == year:
                price = float(trade.get("exit_price") or 0)
                if price <= 0:
                    continue
                proceeds = size * price - fees
                units = acb_tracker[symbol]["total_units"]
                total_cost = acb_tracker[symbol]["total_cost"]
                acb_per_unit = (total_cost / units) if units > 0 else 0.0
                cost_basis = size * acb_per_unit
                gain_loss = proceeds - cost_basis

                entry = {
                    "date": trade_date.isoformat(),
                    "symbol": symbol,
                    "quantity": size,
                    "proceeds_cad": round(proceeds, 2),
                    "acb_per_unit": round(acb_per_unit, 4),
                    "cost_basis_cad": round(cost_basis, 2),
                    "gain_loss_cad": round(gain_loss, 2),
                    "type": "CAPITAL GAIN" if gain_loss >= 0 else "CAPITAL LOSS",
                }
                trade_log.append(entry)

                t5008_rows.append({
                    "box_131_proceeds": round(proceeds, 2),
                    "box_132_acb": round(cost_basis, 2),
                    "box_135_gain_loss": round(gain_loss, 2),
                    "description": f"{symbol} — {size} units",
                    "year": year,
                })

                # Reduce ACB
                acb_tracker[symbol]["total_cost"] -= cost_basis
                acb_tracker[symbol]["total_units"] = max(0.0, units - size)

        schedule3_lines = [
            {"line": "197", "label": "Proceeds of disposition", "amount": round(summary.total_proceeds, 2)},
            {"line": "198", "label": "Adjusted cost base", "amount": round(summary.total_cost_basis, 2)},
            {"line": "199", "label": "Outlays and expenses (fees)", "amount": 0.0},
            {"line": "200", "label": "Gain (or loss)", "amount": round(summary.net_gain, 2)},
            {"line": "230", "label": f"Taxable capital gains ({summary.inclusion_rate*100:.0f}% inclusion)",
             "amount": round(summary.taxable_amount, 2)},
        ]

        notes: list[str] = [
            f"Tax year: {year}",
            f"Total dispositions: {summary.trade_count}",
            f"Inclusion rate applied: {summary.inclusion_rate*100:.1f}%",
            "Crypto is treated as property under CRA IT-479R. Every trade is a disposition.",
            "ACB must be tracked across ALL purchases, including crypto-to-crypto swaps.",
            "Capital losses can be applied against capital gains in the same year.",
            "Unused capital losses may be carried back 3 years or forward indefinitely.",
        ]
        if summary.is_business_income:
            notes.append(f"WARNING: {summary.business_income_warning}")
        if summary.net_gain > _CAPITAL_GAINS_LOWER_THRESHOLD:
            notes.append(
                f"Gains exceed $250,000 — the 66.67% inclusion rate applies to the "
                f"${summary.net_gain - _CAPITAL_GAINS_LOWER_THRESHOLD:,.0f} above the threshold."
            )

        return TaxReport(
            tax_year=year,
            summary=summary,
            trade_log=trade_log,
            t5008_rows=t5008_rows,
            schedule3_lines=schedule3_lines,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # Business deduction finder
    # ------------------------------------------------------------------

    def deduction_finder(
        self,
        business_expenses: list[dict[str, Any]],
    ) -> list[Deduction]:
        """
        Identify eligible CRA business deductions for OASIS AI Solutions.

        Parameters
        ----------
        business_expenses : List of dicts: {"description": str, "amount": float,
                            "category": str}

        Returns
        -------
        List of Deduction with CRA reference and confidence level.
        """
        deductions: list[Deduction] = []

        eligible_keywords = {
            "software": ("Software subscription", "ITA s. 20(1)(a)", "HIGH"),
            "subscription": ("Software/service subscription", "ITA s. 20(1)(a)", "HIGH"),
            "hosting": ("Website/server hosting", "ITA s. 18(1)(a)", "HIGH"),
            "domain": ("Domain name registration", "ITA s. 18(1)(a)", "HIGH"),
            "advertising": ("Advertising and promotion", "ITA s. 19.1", "HIGH"),
            "marketing": ("Marketing and promotion", "ITA s. 19.1", "HIGH"),
            "office": ("Office supplies", "ITA s. 18(1)(a)", "HIGH"),
            "phone": ("Cell phone (business portion)", "ITA s. 18(1)(a)", "MEDIUM"),
            "internet": ("Internet (business portion)", "ITA s. 18(1)(a)", "MEDIUM"),
            "travel": ("Business travel", "ITA s. 20(1)(a)", "MEDIUM"),
            "education": ("Professional development", "ITA s. 18(1)(a)", "MEDIUM"),
            "course": ("Professional development course", "ITA s. 18(1)(a)", "MEDIUM"),
            "equipment": ("Business equipment/hardware", "ITA s. 20(1)(a) CCA", "HIGH"),
            "computer": ("Computer equipment (CCA Class 10)", "ITA s. 20(1)(a) CCA", "HIGH"),
            "accounting": ("Accounting/bookkeeping fees", "ITA s. 18(1)(a)", "HIGH"),
            "legal": ("Legal fees", "ITA s. 18(1)(a)", "HIGH"),
            "contractor": ("Subcontractor/freelancer payments", "ITA s. 18(1)(a)", "HIGH"),
            "api": ("API / developer tools", "ITA s. 18(1)(a)", "HIGH"),
            "openai": ("AI API costs (business use)", "ITA s. 18(1)(a)", "HIGH"),
            "anthropic": ("AI API costs (business use)", "ITA s. 18(1)(a)", "HIGH"),
        }

        for expense in business_expenses:
            description = (expense.get("description") or "").lower()
            amount = float(expense.get("amount") or 0)
            if amount <= 0:
                continue

            for keyword, (label, cra_ref, confidence) in eligible_keywords.items():
                if keyword in description:
                    deductions.append(
                        Deduction(
                            description=label,
                            amount=amount,
                            cra_reference=cra_ref,
                            confidence=confidence,
                            notes=f"Original expense: {expense.get('description', '')}",
                        )
                    )
                    break  # One deduction per expense

        return sorted(deductions, key=lambda d: d.amount, reverse=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_acb(self, symbol: str, units: float, cost: float) -> None:
        """Add a purchase to the ACB ledger."""
        if symbol not in self._acb_ledger:
            self._acb_ledger[symbol] = {"total_units": 0.0, "total_cost": 0.0}
        self._acb_ledger[symbol]["total_units"] += units
        self._acb_ledger[symbol]["total_cost"] += cost

    def _get_acb_per_unit(self, symbol: str) -> float:
        """Return the current ACB per unit for a symbol."""
        if symbol not in self._acb_ledger:
            return 0.0
        entry = self._acb_ledger[symbol]
        if entry["total_units"] <= 0:
            return 0.0
        return entry["total_cost"] / entry["total_units"]

    def _reduce_acb(self, symbol: str, units_sold: float) -> None:
        """Remove disposed units from the ACB ledger."""
        if symbol not in self._acb_ledger:
            return
        entry = self._acb_ledger[symbol]
        acb_per_unit = self._get_acb_per_unit(symbol)
        cost_removed = units_sold * acb_per_unit
        entry["total_units"] = max(0.0, entry["total_units"] - units_sold)
        entry["total_cost"] = max(0.0, entry["total_cost"] - cost_removed)

    @staticmethod
    def _apply_inclusion_rate(net_gain: float) -> tuple[float, float]:
        """
        Apply the correct CRA capital gains inclusion rate.

        Returns (taxable_amount, inclusion_rate_used).
        Losses (negative net_gain) → (0.0, 0.5) — losses are not included in income
        but can be carried forward/back.
        """
        if net_gain <= 0:
            return 0.0, _INCLUSION_RATE_LOWER

        if net_gain <= _CAPITAL_GAINS_LOWER_THRESHOLD:
            return net_gain * _INCLUSION_RATE_LOWER, _INCLUSION_RATE_LOWER

        # Below threshold at 50%, above at 66.67%
        lower_portion = _CAPITAL_GAINS_LOWER_THRESHOLD * _INCLUSION_RATE_LOWER
        upper_portion = (net_gain - _CAPITAL_GAINS_LOWER_THRESHOLD) * _INCLUSION_RATE_UPPER
        taxable = lower_portion + upper_portion

        # Effective inclusion rate
        effective_rate = taxable / net_gain
        return taxable, round(effective_rate, 4)

    @staticmethod
    def _estimate_tax(taxable_amount: float, other_income: float = 0.0) -> float:
        """
        Estimate combined federal + Ontario tax on a taxable capital gains amount.

        ``other_income`` can be used to stack the gains on top of employment/
        business income to use the correct marginal bracket.
        """
        total_income = taxable_amount + other_income
        federal = CryptoTaxCalculator._calculate_bracket_tax(
            total_income - _FEDERAL_BASIC_PERSONAL, _FEDERAL_BRACKETS
        )
        ontario = CryptoTaxCalculator._calculate_bracket_tax(
            total_income - _ONTARIO_BASIC_PERSONAL, _ONTARIO_BRACKETS
        )
        # Subtract tax on other_income alone to isolate the capital gains portion
        if other_income > 0:
            federal_base = CryptoTaxCalculator._calculate_bracket_tax(
                other_income - _FEDERAL_BASIC_PERSONAL, _FEDERAL_BRACKETS
            )
            ontario_base = CryptoTaxCalculator._calculate_bracket_tax(
                other_income - _ONTARIO_BASIC_PERSONAL, _ONTARIO_BRACKETS
            )
            return max(0.0, (federal - federal_base) + (ontario - ontario_base))

        return max(0.0, federal + ontario)

    @staticmethod
    def _calculate_bracket_tax(
        taxable_income: float,
        brackets: list[tuple[float, float]],
    ) -> float:
        """
        Compute progressive bracket tax for a given income level.

        Parameters
        ----------
        taxable_income : Income after personal exemptions.
        brackets       : List of (upper_limit, rate) tuples (last has inf limit).
        """
        if taxable_income <= 0:
            return 0.0

        tax = 0.0
        previous_limit = 0.0

        for upper_limit, rate in brackets:
            if taxable_income <= previous_limit:
                break
            taxable_in_bracket = min(taxable_income, upper_limit) - previous_limit
            tax += taxable_in_bracket * rate
            previous_limit = upper_limit

        return tax

    @staticmethod
    def _trade_date(trade: dict[str, Any]) -> datetime:
        """Extract a datetime from a trade dict, handling strings and datetime objects."""
        for key in ("closed_at", "opened_at"):
            val = trade.get(key)
            if val is None:
                continue
            if isinstance(val, datetime):
                return val
            if isinstance(val, str):
                try:
                    return datetime.fromisoformat(val.replace("Z", "+00:00"))
                except ValueError:
                    pass
        return datetime(1970, 1, 1)

    @staticmethod
    def _trade_year(trade: dict[str, Any]) -> int:
        """Return the tax year for a trade (uses closed_at for sells, opened_at for buys)."""
        return CryptoTaxCalculator._trade_date(trade).year
