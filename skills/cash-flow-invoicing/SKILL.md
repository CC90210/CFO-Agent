---
name: cash-flow-invoicing
description: >
  Invoice tracking, accounts receivable, cash flow forecasting, and payment
  optimization for CC's multi-income structure. Manages what's owed, what's
  coming in, and projects cash position 13 weeks forward. Covers OASIS consulting
  invoices, Stripe MRR, DJ gig payments, and FX conversion (USD/CAD).
triggers: [invoice, cash flow, accounts receivable, payment, billing, forecast, runway, when will I get paid, money coming in, overdue, outstanding, AR, DSO, burn rate, reserve, HST collected, Wise payment, Bennett, Stripe payout]
tier: core
dependencies: [accounting-advisor, financial-planning]
---

# Cash Flow & Invoicing — Invoice Tracking and Cash Forecasting

> Atlas's cash management brain. Used when CC needs to track outstanding invoices,
> follow up on payments, forecast cash position, or calculate runway. Covers all
> income sources: OASIS (Wise), Stripe (PropFlow), DJ gigs (e-transfer/cash),
> and Nicky's (T4 paycheck).

## Overview

Atlas manages CC's cash flow by:
1. Tracking every invoice from creation through payment (outstanding, overdue, paid)
2. Maintaining a 13-week rolling cash forecast across all income channels
3. Triggering follow-up cadence automatically on overdue invoices
4. Calculating runway and firing action alerts when reserves fall below thresholds
5. Segregating HST collected and tax provisions so CC never spends money that belongs to CRA

---

## Section 1 — Invoice Management

### Invoice Creation Checklist

Every OASIS invoice must include all of the following before sending:

| Field | Requirement |
|-------|-------------|
| Invoice number | Sequential (OASIS-2026-001, OASIS-2026-002, etc.) |
| Issue date | Date sent |
| Due date | Issue date + payment terms (default net-30) |
| CC legal name | Conaugh McKenna (sole proprietor until incorporated) |
| CC address | Current Collingwood ON address |
| Client name + address | Full legal entity name |
| Services rendered | Itemized description with dates of work |
| Currency | Explicit — CAD or USD |
| Amount before HST | Subtotal |
| HST line | 13% HST if client is Canadian and CC is HST-registered |
| HST number | Only include once CC crosses $30K and registers |
| Total due | Subtotal + HST |
| Bank details | Wise account (USD invoices) or RBC (CAD invoices) |
| Payment terms | "Net-30. Late payments accrue interest at 2% per month." |

**Currency rule:** Bennett pays in USD via Wise — invoice in USD. Local CAD clients invoice in CAD. Never mix currencies on a single invoice.

**FX conversion for CRA:** Use the Bank of Canada noon rate on the date of payment. Atlas pulls this from `https://www.bankofcanada.ca/rates/exchange/daily-exchange-rates/` when calculating CAD income for T2125.

### Invoice Status Tracking

| Status | Definition |
|--------|------------|
| Draft | Created, not yet sent |
| Sent | Delivered to client, clock starts |
| Outstanding | Within payment terms, not yet paid |
| Overdue | Past due date, follow-up triggered |
| Paid | Payment received and confirmed |
| Bad Debt | Written off after 90+ days, no collection expected |

### Follow-Up Cadence

Atlas triggers follow-ups on the schedule below. Tone escalates progressively.

| Day | Trigger | Action | Tone |
|-----|---------|--------|------|
| Due date - 7 | 7 days before due | Friendly reminder with invoice attached | Warm |
| Due date | Day of | Confirm payment is being processed | Neutral |
| Due date + 3 | 3 days overdue | Polite follow-up, re-attach invoice | Firm |
| Due date + 7 | 7 days overdue | Formal notice, mention late interest | Formal |
| Due date + 14 | 14 days overdue | Escalation — flag for relationship review, consider pausing work | Escalation |
| Due date + 30 | 30 days overdue | Final notice before collections consideration | Legal |

**Late interest calculation:** 2% per month (24% annualized) or as stated in the contract. Applied to the outstanding principal from due date forward.

Example: $2,500 invoice overdue by 14 days = $2,500 x 2% x (14/30) = $23.33 accrued interest.

Atlas does not charge interest automatically — it calculates the amount and drafts the notice for CC to review.

---

## Section 2 — Accounts Receivable Dashboard

### AR Aging Buckets

| Bucket | Days Outstanding | Action |
|--------|-----------------|--------|
| Current | 0–30 days | Monitor |
| Aging | 31–60 days | First follow-up sent |
| At Risk | 61–90 days | Escalation follow-up, consider pausing delivery |
| Critical | 90+ days | Collections decision required |

### Days Sales Outstanding (DSO)

```
DSO = (Total AR Outstanding / Total Revenue in Period) x Days in Period
```

**CC's target DSO:** 30 days or less (matches net-30 terms)
**Warning threshold:** DSO > 45 days — collection process is breaking down
**Critical threshold:** DSO > 60 days — revenue is real but cash is not arriving

Track monthly. A rising DSO on stable revenue means clients are paying slower — address before it compounds.

### Bad Debt Risk Assessment

| Risk Level | Signal | Action |
|------------|--------|--------|
| Low | Paid on time previously, established client | Standard follow-up |
| Medium | First invoice, new client, slow payer history | Require partial upfront (50%) |
| High | Dispute raised, unresponsive, invoice 60+ days | Pause work, escalate |
| Write-off | 90+ days, no response, amount under $500 | Write off, claim business expense on T2125 |

**Bad debt deduction:** Written-off invoices for income already reported are deductible on T2125 Line 8590 (Bad Debts). Atlas tracks this for tax filing.

### Collection Escalation Process

1. Exhaust all follow-up cadence steps above
2. Send formal demand letter (Atlas drafts on request)
3. Small Claims Court (Ontario): amounts up to $35,000 — filing fee ~$102
4. Collection agency: typically 25-40% of recovered amount as fee
5. Write off as bad debt and claim deduction — often more economical below $1,000

---

## Section 3 — Cash Flow Forecasting

### 13-Week Rolling Cash Flow Forecast

The forecast rolls every Monday. Atlas updates it when CC provides new invoice status, expense confirmations, or payment receipts.

```
Week N Cash Position = Week (N-1) Cash + Expected Inflows - Expected Outflows
```

**Forecast template structure:**

| Week | Opening Balance | Inflows | Outflows | Closing Balance | Notes |
|------|----------------|---------|----------|-----------------|-------|
| W1 | $X | $Y | $Z | $X+Y-Z | |
| W2 | Prior closing | ... | ... | ... | |
| ... | | | | | |
| W13 | | | | | |

### Income Sources and Settlement Times

| Source | Amount | Frequency | Settlement Lag | Account |
|--------|--------|-----------|---------------|---------|
| Bennett (OASIS) | $2,500 + 15% rev share | Monthly | 1–3 days (Wise) | Wise USD |
| PropFlow (Stripe MRR) | ~$180 | Monthly | 2 business days | Stripe → Wise/RBC |
| DJ gigs | Variable ($200–$800) | Irregular, summer-heavy | Immediate (cash/e-transfer) | RBC |
| Nicky's Donuts | ~$400–$600 bi-weekly | Bi-weekly | Payday (T4 employment) | RBC |
| Trading (Kraken/OANDA) | Variable | Irregular | 2–5 days (exchange withdrawal) | RBC |

**Forecasting rule:** Only include confirmed income in weeks 1-4. Use probability-weighted estimates for weeks 5-13.

### Expense Categories

**Fixed (predictable, include every week):**
- Rent (monthly — prorate weekly)
- Phone plan
- Software subscriptions (Anthropic API, hosting, tools)
- Minimum debt payments (OSAP if applicable)

**Variable (estimate from trailing 4-week average):**
- API usage costs (scales with PropFlow/OASIS activity)
- Contractor payments
- Food and personal spending
- Transportation

**One-time (include in specific weeks when known):**
- Equipment purchases
- Legal/accounting fees
- Tax installment payments (March 15, June 15, Sept 15, Dec 15)
- HST remittance (quarterly if registered)

### Tax Provisions (Set Aside, Do Not Spend)

These are not expenses — they are liabilities. Atlas tracks them separately.

| Provision | Rate | Basis | Notes |
|-----------|------|-------|-------|
| Federal + Ontario income tax | 25–30% of net self-employment income | All OASIS + DJ revenue minus expenses | Lower end at current income, rises with scale |
| CPP self-employment | 11.9% of net income ($3,500–$68,500 range) | Net business income | Both employee and employer portions |
| HST collected | 100% of HST billed | Only applies once registered | Not income — remit quarterly to CRA |

**Practical rule:** Every dollar of OASIS invoice revenue — move 30% to a dedicated tax reserve account immediately upon receipt. HST billed goes entirely into a separate holding account.

---

## Section 4 — Payment Optimization

### Billing Timing

- Invoice on the 1st of each month for recurring work
- Net-15 terms for clients with strong payment history (accelerates collection vs net-30)
- Net-30 default for new clients
- Require 50% upfront deposit for project work over $1,000 — non-negotiable

### Annual Billing Discount

Offer consulting clients annual prepay at a 2-month discount (10 months billed, 12 months service):

```
Annual price = Monthly rate x 10
Monthly price = Monthly rate x 12
Savings to client = 2 months of billing
Benefit to CC = 12 months of cash upfront, zero collection risk
```

For Bennett at $2,500/month: annual option = $25,000 upfront vs $30,000 over 12 months. Offer if relationship is strong — dramatically improves cash position and eliminates DSO risk on that contract.

### Stripe vs Wise Fee Comparison

| Payment Method | Fee | Best For |
|---------------|-----|----------|
| Stripe (card) | 2.9% + $0.30 CAD | Small recurring payments, PropFlow subscribers |
| Stripe (bank debit) | 0.8%, capped $5 CAD | Larger amounts from Canadian clients |
| Wise (bank transfer) | 0.4–1.2% FX + fixed fee | USD payments from Bennett, international clients |
| E-transfer (RBC) | Free (included in plan) | Canadian clients, DJ gigs, any CAD payment |
| Cash | Free | DJ gigs only — log immediately, declare as income |

**Rule:** E-transfer for CAD. Wise for USD. Stripe only when client requires card. Never accept cheque — 5-7 day clearing delays cash flow unnecessarily.

### Multi-Currency: When to Convert USD to CAD

| Situation | Action |
|-----------|--------|
| CAD bills coming due immediately | Convert at current rate, use Bank of Canada noon rate for records |
| USD stronger than usual (USD/CAD > 1.40) | Convert and capture the FX gain |
| Accumulating USD for US expenses | Hold in Wise USD account |
| Tax filing time | Convert all USD income at BoC noon rate for T2125 reporting |

**FX record-keeping:** Log every USD-to-CAD conversion with date, USD amount, CAD amount, and rate used. Required for CRA if questioned.

---

## Section 5 — Cash Reserve Targets

### Allocation Waterfall

When cash arrives, allocate in this order before treating the remainder as spendable:

```
Gross Revenue Received
  └─ HST collected → HST Reserve Account (100%, remit quarterly)
  └─ Tax provision → Tax Reserve (30% of net revenue)
  └─ Business operating reserve → top up to 2-month target
  └─ Personal emergency fund → top up to 3-month target
  └─ Remaining → available for spending, investing, TFSA contribution
```

### Reserve Targets (CC's Current Profile)

| Reserve | Target Amount | Current Status | Notes |
|---------|--------------|----------------|-------|
| Personal emergency fund | ~$9,000 (3 months expenses at ~$3,000/month) | Track in RBC | Liquid, HISA or TFSA |
| Business operating reserve | ~$6,000 (2 months OASIS operating costs) | Track in RBC | Covers tools, API, contractor costs |
| Tax reserve | 30% of all OASIS + DJ income | Separate account | Federal/provincial income tax + CPP |
| HST reserve | 100% of HST billed | Separate account | Belongs to CRA — do not touch |

**Total reserve target before TFSA investing:** ~$15,000 + outstanding tax provision.

---

## Section 6 — Runway Calculation

### Formula

```
Monthly Burn Rate = Average monthly fixed + variable expenses (exclude tax provisions and savings)
Runway (months) = Total liquid cash / Monthly Burn Rate
```

**Exclude from burn rate:** Tax reserve, HST reserve, RRSP/TFSA contributions (these are assets, not expenses).

**Include in burn rate:** Rent, food, transport, phone, subscriptions, API costs, loan payments.

### Action Thresholds

| Runway | Status | Action Required |
|--------|--------|-----------------|
| 6+ months | Healthy | Normal operations. Review quarterly. |
| 3–6 months | Caution | No new discretionary expenses. Accelerate invoicing. |
| Under 3 months | Warning | Cut all non-essential expenses immediately. Chase all outstanding invoices. Explore bridge options. |
| Under 1 month | Emergency | Stop all non-essential spending. Contact all clients to accelerate payment. Consider credit line. |

Atlas fires a runway alert whenever the 13-week forecast projects closing balance below the 3-month threshold.

---

## Section 7 — Reporting Schedule

### Weekly (Monday — 5-minute update)

- Current cash position across all accounts (RBC + Wise USD + Wise CAD + Stripe balance)
- Outstanding invoices by aging bucket
- Any invoices that crossed a follow-up trigger since last week
- Updated 13-week forecast closing balance

### Monthly (1st of month — 15-minute review)

- Full cash flow report: actual vs forecast variance
- AR aging summary with DSO calculation
- Revenue by source vs prior month
- Tax provision balance vs projected annual tax bill
- HST collected vs HST remitted balance
- Any bad debt write-offs or escalations

### Quarterly (with quarterly-tax-review skill)

- AR aging trend (3-month view)
- DSO trend — is it improving or deteriorating?
- Bad debt review — any write-offs to claim on T2125?
- HST remittance due (if registered) — calculate net HST (collected minus ITCs)
- Tax installment payment due — calculate amount using prior-year method or current-year estimate
- Reserve adequacy review — are all four reserves funded?

---

## Section 8 — CC-Specific Income Profile

| Income Source | Type | Amount | Timing | Account | Currency | Predictability |
|--------------|------|--------|--------|---------|----------|----------------|
| Bennett (OASIS consulting) | Self-employment | $2,500 + 15% rev share | Monthly | Wise | USD | High |
| PropFlow (Stripe MRR) | Self-employment (SaaS) | ~$180/month | Monthly | Stripe → Wise/RBC | CAD/USD | High |
| DJ gigs | Self-employment | $200–$800/gig | Irregular (summer-heavy, Q2-Q3) | RBC (cash/e-transfer) | CAD | Seasonal |
| Nicky's Donuts | Employment (T4) | ~$400–$600 bi-weekly | Bi-weekly paydays | RBC | CAD | High |
| Kraken trading | Capital gains / business income | Variable | On withdrawal | RBC | CAD | Unpredictable |
| OANDA trading | Capital gains / business income | Variable | On withdrawal | RBC | CAD | Unpredictable |

**Forecasting rules by source:**
- Bennett + PropFlow: include at full value in weeks 1-8 (contracted/recurring)
- Nicky's: include every 2 weeks at average net-of-tax amount
- DJ: include only confirmed booked gigs. Apply 60% probability to unconfirmed summer inquiries.
- Trading: exclude from cash flow forecast entirely — treat as a windfall when it arrives

### Bennett Invoice Workflow

1. Send invoice on the 1st of each month (OASIS-2026-XXX)
2. USD amount — $2,500 base + any rev share calculation from prior month
3. Payment arrives via Wise within 1–3 days
4. Log USD received, convert to CAD at BoC noon rate for T2125
5. Move 30% of CAD equivalent to tax reserve immediately

### Stripe Payout Workflow

1. Stripe pays out every 2 business days automatically
2. Lands in Wise or RBC depending on payout destination configured
3. Log gross Stripe revenue (before Stripe fees) as income on T2125
4. Stripe fees (2.9% + $0.30) are deductible business expenses — log separately

---

## Integration Points

| Skill / Module | Purpose |
|----------------|---------|
| `skills/accounting-advisor/SKILL.md` | T2125 income reporting, bad debt deduction, FX income calculation |
| `skills/quarterly-tax-review/SKILL.md` | HST remittance, tax installment payments, quarterly reserve check |
| `skills/financial-planning/SKILL.md` | TFSA/RRSP contribution decisions after reserves are funded |
| `skills/tax-loss-harvesting/SKILL.md` | End-of-year cash planning around tax-loss trades |
| `finance/tax.py` | Tax provision calculations, quarterly installment estimates |
| `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` | Chart of accounts, monthly close routine, KPI tracking |
| `docs/ATLAS_HST_REGISTRATION_GUIDE.md` | HST registration threshold ($30K), ITC claims, quick method |
| `docs/ATLAS_INSTALLMENT_PAYMENTS.md` | CRA quarterly installment schedule, safe-harbor methods, penalty avoidance |
