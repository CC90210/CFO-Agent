"""
cfo/cashflow.py — Montreal Move Runway Model for CC (Conaugh McKenna)

Atlas CFO module. No external dependencies. Pure math.
Run: python -m cfo.cashflow

ASSUMPTIONS (edit the constants block below — all marked with # <EDITABLE>):
- USD/CAD rate: 1.37 (Bank of Canada mid-rate, April 2026 approximate)
- Montreal move date: 2026-07-01 (CC moving summer 2026)
- Pre-move burn is minimal (living at parents' in Collingwood — near-zero housing cost)
- Post-move base rent: $750 CAD (splitting with a friend per USER.md — "~$750 CC's share")
- Worst-case rent: $1,500 CAD (CC's stated ceiling if solo or split falls through)
- Tax reserve: 25% of gross self-employment income set aside each month (CPP + federal + ON)
  Rationale: At $35K-$50K CAD net income, effective rate ~22-28%. 25% is conservative buffer.
  CPP self-employment: 11.9% on net earnings up to $68,500 (2026 limit, both sides)
- GST/HST: 5% federal + QC 9.975% = 14.975% QC sales tax (TPS/TVQ)
  CC charges HST/QST to clients; it is a pass-through (not income), but modelled as quarterly
  cash outflow. Collected monthly, remitted quarterly. Watch $30K TTM threshold for mandatory
  registration (already crossed at current MRR).
- QST registration required in Quebec as soon as CC establishes a Montreal presence.
  Budget ~$200 one-time for QST registration (modelled as move-month expense).
- CCPC incorporation trigger: $80K CAD TTM revenue (modelled as milestone marker only,
  no cash impact in this model — budget $2K-$5K separately for legal setup).
- Projection horizon: 24 months from 2026-05-01 (first full month of model)
"""

from __future__ import annotations

import io
import sys

# Force UTF-8 output on Windows (cp1252 console cannot encode em-dashes or box-drawing chars).
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

# ─────────────────────────────────────────────
# EDITABLE CONSTANTS — change these freely
# ─────────────────────────────────────────────

# FX: USD → CAD conversion rate
USD_TO_CAD: float = 1.37  # Bank of Canada mid-rate, April 2026 approximate

# Current liquid position — loaded live from data/manual_balances.json
# Falls back to sensible defaults if the file is missing or malformed.
def _load_cash_position() -> tuple[float, float]:
    """Return (cad_cash, usd_cash) from data/manual_balances.json.

    Sums all balances in category == "cash" by currency. Any non-CAD/USD
    currency is ignored here (add new currencies if they become meaningful).
    """
    import json
    from pathlib import Path

    default_cad, default_usd = 6_419.00, 0.00
    path = Path(__file__).resolve().parent.parent / "data" / "manual_balances.json"
    if not path.exists():
        return default_cad, default_usd
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cad = sum(b["amount"] for b in data.get("balances", [])
                  if b.get("category") == "cash" and b.get("currency") == "CAD")
        usd = sum(b["amount"] for b in data.get("balances", [])
                  if b.get("category") == "cash" and b.get("currency") == "USD")
        return cad or default_cad, usd
    except Exception:
        return default_cad, default_usd


CURRENT_CAD, CURRENT_USD = _load_cash_position()

# Montreal move date — expenses shift at this point
MONTREAL_MOVE_DATE: date = date(2026, 7, 1)

# Model start date
MODEL_START: date = date(2026, 5, 1)

# Projection horizon in months
HORIZON_MONTHS: int = 24

# Self-employment tax reserve rate (federal + ON marginal + CPP both sides)
# At ~$40K net income: ~12% fed + ~9.15% ON + 11.9% CPP = ~33%. We use 25% as a floor
# because deductions (home office, equipment, subscriptions) reduce taxable income materially.
TAX_RESERVE_RATE: float = 0.25

# GST/HST collected on Canadian client revenue (QC: TPS/TVQ = 14.975%)
# Pass-through — CC collects it from clients, remits quarterly. Modelled as a liability that
# builds monthly and is paid out Q end. If majority clients are US (Bennett), HST does NOT apply
# to exports. Applied only to the "CAD client" revenue slice.
QC_SALES_TAX_RATE: float = 0.14975   # TPS 5% + TVQ 9.975%
SALES_TAX_PASS_THROUGH: bool = True   # True = HST/QST is collected from clients, not absorbed

# Quarterly GST/HST remittance months (Jan=1, Apr=4, Jul=7, Oct=10 for calendar-year filers)
GST_REMITTANCE_MONTHS: tuple[int, ...] = (1, 4, 7, 10)

# One-time QST setup cost when moving to Montreal
QST_SETUP_COST_CAD: float = 200.00

# CCPC incorporation threshold (annual revenue CAD TTM — milestone marker only)
CCPC_TRIGGER_CAD: float = 80_000.00

# GST/HST mandatory registration threshold
GST_REGISTRATION_THRESHOLD: float = 30_000.00  # Already crossed — CC should already be registered


# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class MonthlyBurn:
    """
    Monthly living expenses in CAD.
    Pre-move: living at parents' in Collingwood, near-zero housing.
    Post-move: Montreal rent + full cost of living.
    All values are POST-MOVE defaults unless noted.
    """
    # Housing
    rent: float = 750.00           # <EDITABLE> $750 = CC's share (split w/ friend). $1,500 if solo.
    # Food & groceries — Montreal is affordable vs Toronto. $500 is reasonable for a 22yo.
    food: float = 500.00           # <EDITABLE>
    # Software & streaming subscriptions:
    # Serato $21 USD (~$29 CAD) + SoundCloud $9.99 USD (~$14 CAD) + Claude/ChatGPT/Hostinger ~$60 CAD
    # Total software: ~$103 CAD. Round up to $120 for rounding + occasional one-offs.
    subs: float = 120.00           # <EDITABLE>
    # Transit: Montreal STM monthly pass $97.50 (2026 estimate). No car = no insurance/gas.
    transit: float = 100.00        # <EDITABLE>
    # Phone: mid-tier plan ~$55-65/mo
    phone: float = 60.00           # <EDITABLE>
    # Miscellaneous: toiletries, clothes, entertainment, haircuts, dining out, etc.
    misc: float = 150.00           # <EDITABLE>

    # Pre-move override: living at parents' = no rent, reduced food/transit
    # Applied automatically for months before MONTREAL_MOVE_DATE
    pre_move_rent: float = 0.00
    pre_move_food: float = 200.00   # Parents cover most food
    pre_move_transit: float = 50.00  # Collingwood — minimal transit
    pre_move_misc: float = 100.00

    def total(self, post_move: bool = True) -> float:
        """Return total monthly burn in CAD."""
        if post_move:
            return self.rent + self.food + self.subs + self.transit + self.phone + self.misc
        else:
            # Pre-move: no rent, reduced food/transit/misc, same subs/phone
            return (self.pre_move_rent + self.pre_move_food + self.subs
                    + self.pre_move_transit + self.phone + self.pre_move_misc)

    def breakdown(self, post_move: bool = True) -> dict[str, float]:
        """Return itemised burn as dict."""
        if post_move:
            return {
                "rent": self.rent,
                "food": self.food,
                "subs": self.subs,
                "transit": self.transit,
                "phone": self.phone,
                "misc": self.misc,
            }
        return {
            "rent": self.pre_move_rent,
            "food": self.pre_move_food,
            "subs": self.subs,
            "transit": self.pre_move_transit,
            "phone": self.phone,
            "misc": self.pre_move_misc,
        }


@dataclass
class IncomeStream:
    """
    A single income source contributing to CC's cash position.

    amount_usd_monthly: if income is in USD, set this and leave amount_cad_monthly=0.
    amount_cad_monthly: if income is in CAD, set this and leave amount_usd_monthly=0.
    confidence: 0.0 = speculative / 1.0 = locked contract.
    start_month: date of first payment month (first day of month).
    end_month: last payment month, or None if ongoing indefinitely.
    is_canadian_client: if True, QST/HST collected on top (pass-through, but affects cash timing).
    """
    name: str
    amount_usd_monthly: float = 0.0
    amount_cad_monthly: float = 0.0
    confidence: float = 1.0
    start_month: date = field(default_factory=lambda: MODEL_START)
    end_month: Optional[date] = None
    is_canadian_client: bool = False

    def cad_amount(self, usd_rate: float = USD_TO_CAD) -> float:
        """Returns gross CAD income before tax reserve deduction."""
        return self.amount_cad_monthly + (self.amount_usd_monthly * usd_rate)

    def is_active(self, month: date) -> bool:
        """True if this stream is paying in the given month (first day of month)."""
        if month < self.start_month:
            return False
        if self.end_month is not None and month > self.end_month:
            return False
        return True

    def effective_cad(self, month: date, usd_rate: float = USD_TO_CAD) -> float:
        """Returns confidence-weighted CAD income for a given month."""
        if not self.is_active(month):
            return 0.0
        return self.cad_amount(usd_rate) * self.confidence


# ─────────────────────────────────────────────
# RUNWAY CALCULATION
# ─────────────────────────────────────────────

def _month_iter(start: date, n: int):
    """Yield n consecutive month-start dates beginning at start."""
    current = start.replace(day=1)
    for _ in range(n):
        yield current
        # Advance to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


def runway_months(
    cash_cad: float,
    burn: MonthlyBurn,
    income: list[IncomeStream],
    usd_rate: float = USD_TO_CAD,
    horizon: int = HORIZON_MONTHS,
    scenario_name: str = "Unnamed",
) -> dict:
    """
    Month-by-month cash flow projection.

    Returns a dict with:
      - scenario: str
      - months: list of monthly snapshots
      - months_until_broke: int | None
      - broke_date: str | None
      - ttm_revenue_at_month: dict[month_str -> float]  (for CCPC trigger detection)
      - gst_warning_month: str | None
      - ccpc_trigger_month: str | None
      - summary: plain-English summary
    """
    months_data: list[dict] = []
    balance: float = cash_cad
    months_until_broke: Optional[int] = None
    broke_date: Optional[str] = None

    # Accumulate GST/HST liability (collected from Canadian clients, paid quarterly)
    gst_liability: float = 0.0

    # Rolling 12-month revenue accumulator for CCPC/GST thresholds
    monthly_revenue_log: list[float] = []
    gst_warning_month: Optional[str] = None
    ccpc_trigger_month: Optional[str] = None
    gst_already_warned: bool = False
    ccpc_already_triggered: bool = False

    # One-time QST setup cost (July 2026 move month)
    qst_setup_paid: bool = False

    for i, month in enumerate(_month_iter(MODEL_START, horizon)):
        post_move: bool = month >= MONTREAL_MOVE_DATE
        month_str = month.strftime("%Y-%m")

        # ── Income ──────────────────────────────────────────
        gross_income_cad: float = 0.0
        gst_collected_this_month: float = 0.0

        for stream in income:
            eff = stream.effective_cad(month, usd_rate)
            gross_income_cad += eff
            # Collect QST/HST on Canadian-client revenue (pass-through liability)
            if stream.is_canadian_client and eff > 0 and SALES_TAX_PASS_THROUGH:
                gst_collected_this_month += eff * QC_SALES_TAX_RATE

        # GST collected enters balance (CC collects it from clients), then paid out quarterly
        balance += gross_income_cad + gst_collected_this_month
        gst_liability += gst_collected_this_month

        # ── Tax Reserve ─────────────────────────────────────
        # Set aside 25% of gross self-employment income monthly.
        # This leaves the balance but is earmarked — we track it separately as a memo.
        # In this model we DO reduce spendable balance by the reserve (conservative).
        tax_reserve: float = gross_income_cad * TAX_RESERVE_RATE

        # ── Burn ────────────────────────────────────────────
        burn_total: float = burn.total(post_move)

        # One-time: QST setup cost in move month
        one_off: float = 0.0
        if post_move and not qst_setup_paid:
            one_off += QST_SETUP_COST_CAD
            qst_setup_paid = True

        # ── GST Quarterly Remittance ─────────────────────────
        gst_remittance: float = 0.0
        if month.month in GST_REMITTANCE_MONTHS and gst_liability > 0:
            gst_remittance = gst_liability
            gst_liability = 0.0

        # ── Net Cash Movement ────────────────────────────────
        total_outflow = burn_total + tax_reserve + one_off + gst_remittance
        balance -= total_outflow
        net_cashflow = gross_income_cad - total_outflow

        # ── Rolling TTM Revenue ──────────────────────────────
        monthly_revenue_log.append(gross_income_cad)
        if len(monthly_revenue_log) > 12:
            monthly_revenue_log.pop(0)
        ttm_revenue = sum(monthly_revenue_log)

        # ── Milestone Checks ─────────────────────────────────
        if not gst_already_warned and ttm_revenue >= GST_REGISTRATION_THRESHOLD:
            gst_warning_month = month_str
            gst_already_warned = True

        if not ccpc_already_triggered and ttm_revenue >= CCPC_TRIGGER_CAD:
            ccpc_trigger_month = month_str
            ccpc_already_triggered = True

        # ── Broke Check ──────────────────────────────────────
        if balance <= 0 and months_until_broke is None:
            months_until_broke = i + 1
            broke_date = month_str

        months_data.append({
            "month": month_str,
            "post_move": post_move,
            "opening_balance": round(balance + total_outflow - gross_income_cad - gst_collected_this_month, 2),
            "gross_income": round(gross_income_cad, 2),
            "gst_collected": round(gst_collected_this_month, 2),
            "burn": round(burn_total, 2),
            "tax_reserve": round(tax_reserve, 2),
            "gst_remittance": round(gst_remittance, 2),
            "one_off": round(one_off, 2),
            "net_cashflow": round(net_cashflow, 2),
            "closing_balance": round(balance, 2),
            "ttm_revenue": round(ttm_revenue, 2),
        })

    # ── Plain-English Summary ────────────────────────────────
    final_balance = months_data[-1]["closing_balance"]
    move_month_data = next((m for m in months_data if m["month"] == MONTREAL_MOVE_DATE.strftime("%Y-%m")), None)
    balance_at_move = move_month_data["opening_balance"] if move_month_data else cash_cad

    if months_until_broke is None:
        survival_msg = (
            f"You do NOT go broke in this scenario over 24 months. "
            f"Final balance at month 24: ${final_balance:,.0f} CAD."
        )
    else:
        survival_msg = (
            f"WARNING: Balance hits $0 at month {months_until_broke} ({broke_date}). "
            f"You have {months_until_broke - 1} months of runway."
        )

    move_msg = (
        f"Estimated balance when you land in Montreal ({MONTREAL_MOVE_DATE.strftime('%Y-%m')}): "
        f"${balance_at_move:,.0f} CAD."
    )

    ccpc_msg = (
        f"CCPC incorporation trigger (${CCPC_TRIGGER_CAD:,.0f} TTM): "
        + (f"reached {ccpc_trigger_month}." if ccpc_trigger_month else "not reached in 24 months.")
    )

    gst_msg = (
        "GST/HST already mandatory (TTM > $30K) — ensure registered before first Montreal invoice."
        if gst_already_warned else
        "GST/HST $30K threshold not crossed in this scenario."
    )

    summary = f"{survival_msg} {move_msg} {ccpc_msg} {gst_msg}"

    return {
        "scenario": scenario_name,
        "months": months_data,
        "months_until_broke": months_until_broke,
        "broke_date": broke_date,
        "ccpc_trigger_month": ccpc_trigger_month,
        "gst_warning_month": gst_warning_month,
        "summary": summary,
    }


# ─────────────────────────────────────────────
# THREE SCENARIOS
# ─────────────────────────────────────────────

def montreal_scenarios(
    starting_cash_cad: float = CURRENT_CAD + (CURRENT_USD * USD_TO_CAD),
    usd_rate: float = USD_TO_CAD,
) -> list[dict]:
    """
    Returns three scenario projections:

    PESSIMISTIC — Only Bennett ($2,500 USD/mo flat). Rev-share ignored (uncertain).
      Burn: worst-case rent ($1,500 CAD), standard everything else.
      This is the "what if everything stays flat and I go solo on rent" scenario.

    REALISTIC — Bennett flat + $500 CAD avg other clients.
      Rent: $750 CAD (splitting with friend as planned).
      Income grows modestly. No hockey-stick assumed.

    OPTIMISTIC — Bennett + ramp to $8K USD MRR by month 6 (per CC's projection trajectory).
      64.99% MRR growth rate on Stripe is real data. Modelled as linear ramp from
      $3K USD → $8K USD over 6 months, then held flat (conservative vs CC's $15-20K target).
      Rent: $750 CAD.
    """
    burn_default = MonthlyBurn()
    burn_worst_rent = MonthlyBurn(rent=1_500.00)  # Solo apartment, no split

    # ── PESSIMISTIC ──────────────────────────────────────────
    pessimistic_income = [
        IncomeStream(
            name="Bennett (flat only)",
            amount_usd_monthly=2_500.00,
            confidence=0.90,  # Sticky relationship but month-to-month contract
            start_month=MODEL_START,
            end_month=None,
            is_canadian_client=False,  # US client — no HST on exports
        ),
    ]

    # ── REALISTIC ────────────────────────────────────────────
    # Bennett flat + modest client diversification ($500 CAD avg/mo from other clients)
    # Some Canadian clients — QST/HST applies to CAD slice
    realistic_income = [
        IncomeStream(
            name="Bennett (flat only)",
            amount_usd_monthly=2_500.00,
            confidence=0.90,
            start_month=MODEL_START,
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="Other clients (CAD avg)",
            amount_cad_monthly=500.00,
            confidence=0.70,  # Not guaranteed — average estimate
            start_month=MODEL_START,
            end_month=None,
            is_canadian_client=True,  # Mix of Canadian clients
        ),
        IncomeStream(
            name="Bennett rev-share (15% Skool)",
            # Conservative: $200 USD/mo average rev-share. Skool community could be much more.
            amount_usd_monthly=200.00,
            confidence=0.60,
            start_month=MODEL_START,
            end_month=None,
            is_canadian_client=False,
        ),
    ]

    # ── OPTIMISTIC — ramp to $8K USD MRR by month 6 ─────────
    # Model as individual streams that activate at different months.
    # Starting base: ~$3K USD (Bennett $2.5K + $500 Stripe). Ramp adds ~$833/mo in new USD MRR.
    # By month 6 (Oct 2026), total USD income = ~$8K/mo.
    # Held flat after that (conservative — CC targets $15-20K but we don't model hockey stick).
    def _ramp_start(month_offset: int) -> date:
        """Return the date that is month_offset months after MODEL_START."""
        d = MODEL_START
        for _ in range(month_offset):
            if d.month == 12:
                d = d.replace(year=d.year + 1, month=1)
            else:
                d = d.replace(month=d.month + 1)
        return d

    optimistic_income = [
        IncomeStream(
            name="Bennett (flat)",
            amount_usd_monthly=2_500.00,
            confidence=0.90,
            start_month=MODEL_START,
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="Bennett rev-share",
            amount_usd_monthly=300.00,
            confidence=0.70,
            start_month=MODEL_START,
            end_month=None,
            is_canadian_client=False,
        ),
        # New MRR added each month from month 1 through month 6 (+~$833 USD each step)
        IncomeStream(
            name="New MRR tranche 1 (starts May)",
            amount_usd_monthly=833.00,
            confidence=0.75,
            start_month=_ramp_start(0),
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="New MRR tranche 2 (starts Jun)",
            amount_usd_monthly=833.00,
            confidence=0.70,
            start_month=_ramp_start(1),
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="New MRR tranche 3 (starts Jul)",
            amount_usd_monthly=833.00,
            confidence=0.65,
            start_month=_ramp_start(2),
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="New MRR tranche 4 (starts Aug)",
            amount_usd_monthly=833.00,
            confidence=0.60,
            start_month=_ramp_start(3),
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="New MRR tranche 5 (starts Sep)",
            amount_usd_monthly=833.00,
            confidence=0.55,
            start_month=_ramp_start(4),
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="New MRR tranche 6 (starts Oct)",
            amount_usd_monthly=833.00,
            confidence=0.50,
            start_month=_ramp_start(5),
            end_month=None,
            is_canadian_client=False,
        ),
        IncomeStream(
            name="Canadian clients (CAD)",
            amount_cad_monthly=800.00,
            confidence=0.65,
            start_month=_ramp_start(2),  # picks up after move
            end_month=None,
            is_canadian_client=True,
        ),
    ]

    results = []

    results.append(runway_months(
        cash_cad=starting_cash_cad,
        burn=burn_worst_rent,
        income=pessimistic_income,
        usd_rate=usd_rate,
        scenario_name="PESSIMISTIC (Bennett only, solo rent $1,500)",
    ))

    results.append(runway_months(
        cash_cad=starting_cash_cad,
        burn=burn_default,
        income=realistic_income,
        usd_rate=usd_rate,
        scenario_name="REALISTIC (Bennett + $500 CAD avg other, split rent $750)",
    ))

    results.append(runway_months(
        cash_cad=starting_cash_cad,
        burn=burn_default,
        income=optimistic_income,
        usd_rate=usd_rate,
        scenario_name="OPTIMISTIC (ramp to ~$8K USD MRR by Oct, split rent $750)",
    ))

    return results


# ─────────────────────────────────────────────
# FORMATTING & CLI OUTPUT
# ─────────────────────────────────────────────

_COL_W = 12  # Column width for ASCII table


def _fmt(val: float, prefix: str = "$") -> str:
    """Format a dollar amount for table display."""
    if val < 0:
        return f"-{prefix}{abs(val):>8,.0f}"
    return f" {prefix}{val:>8,.0f}"


def _print_table(result: dict) -> None:
    """Print a scenario as a formatted ASCII table."""
    months = result["months"]
    name = result["scenario"]
    broke = result["broke_date"]
    ccpc = result["ccpc_trigger_month"]

    # Header
    border = "=" * 110
    thin = "-" * 110
    print(f"\n{border}")
    print(f"  SCENARIO: {name}")
    print(border)

    col_hdr = (
        f"  {'Month':<8} {'PostMove':>8} {'OpenBal':>12} {'Income':>12} "
        f"{'Burn':>10} {'TaxRes':>10} {'GSTRem':>10} {'NetFlow':>10} {'CloseBal':>12}"
    )
    print(col_hdr)
    print(thin)

    for m in months:
        flag = ""
        if broke and m["month"] == broke:
            flag = " *** BROKE ***"
        if ccpc and m["month"] == ccpc:
            flag = " *** CCPC TRIGGER ***"
        if m["month"] == MONTREAL_MOVE_DATE.strftime("%Y-%m"):
            flag = " <<< MONTREAL MOVE"

        post_move_str = "YES" if m["post_move"] else "no"
        one_off_note = f" +${m['one_off']:.0f} setup" if m["one_off"] > 0 else ""

        print(
            f"  {m['month']:<8} {post_move_str:>8} "
            f"{_fmt(m['opening_balance']):>12} "
            f"{_fmt(m['gross_income']):>12} "
            f"{_fmt(m['burn']):>10} "
            f"{_fmt(m['tax_reserve']):>10} "
            f"{_fmt(m['gst_remittance']):>10} "
            f"{_fmt(m['net_cashflow']):>10} "
            f"{_fmt(m['closing_balance']):>12}"
            f"{one_off_note}{flag}"
        )

    print(thin)
    print(f"\n  SUMMARY: {result['summary']}")
    if ccpc:
        print(f"  CCPC trigger at {ccpc} — budget $2K-$5K for incorporation setup NOW.")
    print()


def _print_position_summary() -> None:
    """Print CC's current financial position."""
    cad_equiv = CURRENT_USD * USD_TO_CAD
    total_cad = CURRENT_CAD + cad_equiv

    border = "=" * 70
    print(f"\n{border}")
    print("  ATLAS — MONTREAL RUNWAY MODEL")
    print(f"  As of: {date.today().strftime('%Y-%m-%d')}  |  USD/CAD: {USD_TO_CAD}")
    print(border)
    print(f"\n  CURRENT POSITION:")
    print(f"    CAD liquid (RBC + Wealthsimple):  ${CURRENT_CAD:>10,.2f} CAD")
    print(f"    USD liquid (Wise):                ${CURRENT_USD:>10,.2f} USD")
    print(f"    USD->CAD (@ {USD_TO_CAD}):           ${cad_equiv:>10,.2f} CAD")
    print(f"    {'-' * 45}")
    print(f"    TOTAL CAD EQUIVALENT:             ${total_cad:>10,.2f} CAD")
    print(f"\n  KEY DATES:")
    print(f"    Model start:      {MODEL_START.strftime('%Y-%m-%d')}")
    print(f"    Montreal move:    {MONTREAL_MOVE_DATE.strftime('%Y-%m-%d')}")
    print(f"    Projection end:   {_projection_end_str()}")
    print(f"\n  BURN BREAKDOWN (post-move defaults):")
    b = MonthlyBurn()
    for k, v in b.breakdown(post_move=True).items():
        print(f"    {k:<20} ${v:>8,.2f} CAD/mo")
    print(f"    {'TOTAL':<20} ${b.total():>8,.2f} CAD/mo")
    print(f"\n  BURN BREAKDOWN (pre-move, living at parents'):")
    for k, v in b.breakdown(post_move=False).items():
        print(f"    {k:<20} ${v:>8,.2f} CAD/mo")
    print(f"    {'TOTAL':<20} ${b.total(post_move=False):>8,.2f} CAD/mo")
    print(f"\n  TAX RESERVE RATE: {TAX_RESERVE_RATE*100:.0f}% of gross monthly income set aside.")
    print(f"  GST/HST: Already mandatory (TTM > $30K). QST registration required in QC.")
    print(f"  $10K FLOOR: CC's stated minimum balance before Montreal move.")
    floor_gap = 10_000 - total_cad
    if floor_gap > 0:
        print(f"  STATUS: Currently ${floor_gap:,.0f} CAD SHORT of $10K floor. Need {_months_to_floor(total_cad):.1f} months at current burn.")
    else:
        print(f"  STATUS: ABOVE $10K floor by ${-floor_gap:,.0f} CAD. Move is feasible NOW if needed.")
    print()


def _projection_end_str() -> str:
    months = list(_month_iter(MODEL_START, HORIZON_MONTHS))
    return months[-1].strftime("%Y-%m")


def _months_to_floor(current_total: float) -> float:
    """Estimate months to reach $10K floor at current burn (rough calc)."""
    gap = 10_000 - current_total
    if gap <= 0:
        return 0.0
    # Pre-move net save ~= Bennett $2500 USD - pre-move burn $530 - tax 25%
    net_save = (2_500 * USD_TO_CAD * 0.75) - MonthlyBurn().total(post_move=False)
    if net_save <= 0:
        return float("inf")
    return gap / net_save


def _print_milestones(scenarios: list[dict]) -> None:
    """Cross-scenario milestone comparison table."""
    border = "=" * 70
    print(f"\n{border}")
    print("  MILESTONE COMPARISON — ALL SCENARIOS")
    print(border)
    print(f"  {'Milestone':<40} {'Pessimistic':>12} {'Realistic':>12} {'Optimistic':>12}")
    print("-" * 70)

    def _val(s: dict, key: str) -> str:
        v = s.get(key)
        return v if v else "Never"

    def _balance_at(s: dict, month_str: str) -> str:
        for m in s["months"]:
            if m["month"] == month_str:
                return f"${m['closing_balance']:,.0f}"
        return "N/A"

    move_month = MONTREAL_MOVE_DATE.strftime("%Y-%m")
    rows = [
        ("Balance at Montreal move", *[_balance_at(s, move_month) for s in scenarios]),
        ("CCPC $80K trigger", *[_val(s, "ccpc_trigger_month") for s in scenarios]),
        ("Went broke (if ever)", *[_val(s, "broke_date") for s in scenarios]),
        ("Balance at month 12", *[f"${s['months'][11]['closing_balance']:,.0f}" for s in scenarios]),
        ("Balance at month 24", *[f"${s['months'][23]['closing_balance']:,.0f}" for s in scenarios]),
    ]

    for label, pess, real, opt in rows:
        print(f"  {label:<40} {pess:>12} {real:>12} {opt:>12}")

    print()


def _print_recommendation(scenarios: list[dict]) -> None:
    """Plain-English recommendation block."""
    pess, real, opt = scenarios
    total_cad = CURRENT_CAD + (CURRENT_USD * USD_TO_CAD)

    print("=" * 70)
    print("  ATLAS RECOMMENDATION")
    print("=" * 70)

    # Floor check
    floor_gap = 10_000 - total_cad
    if floor_gap > 0:
        print(f"\n  FLOOR ALERT: You're ${floor_gap:,.0f} CAD below your $10K move floor.")
        print(f"  At Bennett income alone, you'll cross $10K within ~1 month of clean saving.")
        print(f"  Do NOT move to Montreal until you hit $10K. Pre-move burn is low — use it.")
    else:
        print(f"\n  You're at ${total_cad:,.2f} CAD — above your $10K floor. Move is funded.")

    # Runway plain-english
    pess_broke = pess["broke_date"]
    print(f"\n  WORST CASE (solo rent, Bennett only, 90% confidence):")
    if pess_broke:
        print(f"    You run out of cash at {pess_broke}. Bennett must NOT churn before then.")
    else:
        print(f"    Even with solo $1,500/mo rent and only Bennett, you stay solvent 24 months.")
        pess_m12 = pess["months"][11]["closing_balance"]
        print(f"    Month-12 balance: ${pess_m12:,.0f} CAD. You are resilient but not growing.")

    real_ccpc = real["ccpc_trigger_month"]
    real_m12 = real["months"][11]["closing_balance"]
    print(f"\n  REALISTIC (split rent $750, Bennett + modest diversification):")
    print(f"    Month-12 balance: ${real_m12:,.0f} CAD.")
    if real_ccpc:
        print(f"    CCPC trigger at {real_ccpc}. Start talking to a lawyer NOW — $2K-$5K setup.")
    else:
        print(f"    CCPC trigger not reached — accelerate client diversification.")

    opt_ccpc = opt["ccpc_trigger_month"]
    opt_m12 = opt["months"][11]["closing_balance"]
    print(f"\n  OPTIMISTIC (ramp to ~$8K USD MRR by Oct 2026):")
    print(f"    Month-12 balance: ${opt_m12:,.0f} CAD.")
    if opt_ccpc:
        print(f"    CCPC trigger at {opt_ccpc}. Irish passport application should be in-flight by then.")

    print(f"\n  KEY RISKS:")
    print(f"    1. Bennett is 94% of income. If he churns, worst-case clock starts immediately.")
    print(f"    2. QST registration: Required in QC from first invoice to a Quebec client.")
    print(f"       Budget $200 for registration. File before your first Montreal CAD invoice.")
    print(f"    3. Tax reserve: {TAX_RESERVE_RATE*100:.0f}% held back monthly. DO NOT spend it.")
    print(f"       Quarterly installments kick in once 2025 taxes are assessed.")
    print(f"    4. $10K floor is not a cushion — it is a minimum. Target $15K before moving.")
    print(f"\n  WHAT TO DO NOW:")
    print(f"    - Stack cash aggressively in May-Jun (low burn, living at parents').")
    print(f"    - Sign at least one new non-Bennett client before July.")
    print(f"    - Confirm split-rent arrangement in writing. Don't go solo at $1,500.")
    print(f"    - If CCPC trigger hits before Oct: incorporate immediately (saves ~17% on income above $80K).")
    print()


# ─────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────

def main() -> None:
    starting_cash = CURRENT_CAD + (CURRENT_USD * USD_TO_CAD)
    _print_position_summary()
    scenarios = montreal_scenarios(starting_cash_cad=starting_cash)
    for s in scenarios:
        _print_table(s)
    _print_milestones(scenarios)
    _print_recommendation(scenarios)


if __name__ == "__main__":
    main()
