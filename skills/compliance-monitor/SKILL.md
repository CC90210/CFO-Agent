---
name: compliance-monitor
description: Proactive compliance monitoring — deadlines, thresholds, red flags, and regulatory changes
triggers: [compliance, deadline, filing, CRA, HST, installment, T1135, penalty, overdue, reminder, am I compliant, what's due, what do I owe, penalties, missing, late, upcoming]
tier: core
dependencies: [accounting-advisor, quarterly-tax-review, income-tier-monitoring]
---

# Compliance Monitor

## Overview

Atlas runs this skill automatically at every session start and whenever a compliance keyword is detected. It cross-checks CC's current date, income, accounts, and foreign assets against every CRA and provincial deadline. The output is a traffic-light compliance report with dollar-impact estimates for non-compliance.

**This skill does not wait to be asked.** If a deadline is within 30 days, Atlas flags it unprompted.

---

## Section 1 — Monthly Compliance Check (Every Session Start)

Run this check at the beginning of every session. Requires only the current date from system context.

### Step 1: Load Current State
1. Read `brain/USER.md` — income sources, accounts, crypto holdings, citizenship
2. Read `brain/STATE.md` — last known income estimate, last filings, open items
3. Note today's date from system context

### Step 2: Calendar Scan (Next 30 Days)
Cross-reference today's date against the Compliance Calendar in Section 5.
Flag any deadline falling within the next 30 days at P1 HIGH or above.

### Step 3: Threshold Checks

Run each check silently. Only surface a flag if a threshold is at risk or has been crossed.

| Check | Threshold | Action if Triggered |
|-------|-----------|---------------------|
| HST registration | $30,000 gross revenue (trailing 12 months) | Flag P1 — register within 29 days of crossing |
| Installment payments | $3,000 net tax owing (current or prior year) | Flag P1 — next quarterly date |
| T1135 foreign property | $100,000 CAD cost basis | Flag P1 — due with T1 (or June 15 for self-employed) |
| Incorporation trigger | $80,000 sustained OASIS revenue | Flag P2 — begin incorporation analysis |
| International planning | $120,000+ income | Flag P2 — Crown Dependencies eval, docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md |
| Revenue concentration | Single client > 50% of revenue | Flag P2 — business risk alert |
| Crypto ACB lag | Any disposition without ACB calc | Flag P2 — run crypto-acb-tracking skill |
| TFSA over-contribution | $7,000/year limit | Flag P0 CRITICAL — 1%/month penalty |
| FHSA contribution | $8,000/year room | Flag P3 — optimization reminder |
| RRSP deadline | March 1 each year | Flag P1 in January-February |
| Payroll remittances | Monthly (post-incorporation) | Flag P0 if overdue — 3-10% penalty |

### Step 4: Missing Documentation Flags

Check for known gaps. Flag if any of the following cannot be confirmed:
- Business receipts for the current quarter
- Vehicle log (if vehicle deduction claimed)
- Home office square footage on file
- Invoices issued matching Stripe/Wise deposits
- T4 from Nicky's (flag in January after year-end)
- Crypto transaction export (flag in January after year-end)

### Step 5: Output

If everything is clean, output one line:
`Compliance: GREEN — no deadlines within 30 days, all thresholds clear.`

If any flags exist, produce the Compliance Status Report (Section 7).

---

## Section 2 — Quarterly Deep Review

### Q1 — January through March

**Focus: RRSP deadline, prior-year reconciliation, filing prep**

1. **RRSP contribution deadline: March 1**
   - Calculate remaining room (prior-year NOA or estimate)
   - Only contribute if marginal rate is 29.65%+ (Tier 2+)
   - Model: contribution × marginal rate = immediate tax saving
   - Flag by January 15 if room exists and rate justifies it

2. **Prior-year T1 preparation**
   - Gather all T-slips: T4 (Nicky's), T5 (investment income), T3 (trust)
   - Confirm Stripe/Wise year-end totals for T2125
   - Reconcile crypto: ACB workbook complete?
   - OANDA: export realized gain/loss report
   - Home office: calculate deductible portion
   - Run accounting-advisor skill for T2125 draft

3. **Prior-year reconciliation**
   - Compare estimated tax to actual — were installments on track?
   - Identify deductions missed — VDP candidate?
   - Document lessons for current year

4. **Actions checklist**
   - [ ] RRSP decision made (contribute or defer)
   - [ ] All T-slips collected
   - [ ] T2125 draft complete
   - [ ] Crypto ACB reconciled
   - [ ] Prior-year installments compared to actual owing

---

### Q2 — April through June

**Focus: April 30 payment, June 15 filing, mid-year income projection**

1. **April 30 — Tax balance owing due** (even for self-employed)
   - Calculate balance: estimated total tax minus installments paid minus withholding
   - Wire transfer from Wise or RBC to CRA by April 30
   - Late payment: 5% immediately + 1%/month — flag P0 after April 15 if unpaid

2. **June 15 — T1 filing deadline for self-employed**
   - File via NETFILE (CC submits, Atlas prepares)
   - Reminder: balance was due April 30 even though filing is June 15
   - Flag P1 by May 15, P0 by June 8

3. **Mid-year income projection**
   - YTD income ÷ months elapsed × 12 = annualized estimate
   - Has income tier changed since year-start?
   - Are installments calibrated correctly for the current year?
   - Is HST threshold at risk? ($30K trailing 12 months)

4. **Actions checklist**
   - [ ] April 30 balance paid
   - [ ] T1 filed by June 15
   - [ ] Mid-year income projection run
   - [ ] Installments updated if income changed
   - [ ] HST threshold check

---

### Q3 — July through September

**Focus: Incorporation trigger, international planning, Q4 harvest prep**

1. **Incorporation trigger check**
   - Is OASIS revenue trending toward $80K annualized?
   - If yes: initiate incorporation-advisor skill, not reactive — lead time is 4-6 weeks
   - Model: incorporation savings vs. cost at current revenue

2. **International planning review**
   - Is income approaching $120K? Flag for Crown Dependencies evaluation
   - Reference: docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md
   - Is T1135 threshold approaching? ($100K foreign property at cost)

3. **Q4 tax-loss harvest preparation**
   - Identify unrealized losses in crypto and investment portfolios now
   - Build candidate list for December harvesting window
   - Note: superficial loss rule — no repurchase within 30 days before or after disposition
   - Calculate estimated savings at marginal rate

4. **September 15 — Q3 installment due**
   - Flag by August 25
   - Amount: based on whichever safe-harbor method was selected

5. **Actions checklist**
   - [ ] Incorporation trigger assessment complete
   - [ ] International planning review done
   - [ ] Q4 harvest candidate list built
   - [ ] September 15 installment paid

---

### Q4 — October through December

**Focus: Year-end tax minimization — highest leverage quarter**

1. **Tax-loss harvesting window (October–December 15)**
   - Execute from candidate list built in Q3
   - Deadline: December 15 for trades to settle by December 31 (T+2 settlement)
   - Flag P1 by November 1, P0 by December 10 if losses still unharvested

2. **TFSA and FHSA maximization**
   - TFSA: contribute up to annual limit ($7,000 in 2025, confirm 2026 limit)
   - FHSA: contribute up to $8,000 before December 31
   - Unused FHSA room carries forward (max $8K carryforward)

3. **Business expense acceleration**
   - Any planned equipment, software, or professional development — buy before December 31
   - Immediate expensing (100% CCA Year 1) for eligible property
   - Home office: confirm nothing has changed for the year

4. **December 15 — Q4 installment due**
   - Final quarterly installment of the year
   - Flag by December 1

5. **Year-end planning**
   - RRSP contribution decision for next year
   - Any income deferral opportunities (defer December invoices to January?)
   - Any income acceleration? (recognize gains this year if rate is lower)
   - OASIS year-end bookkeeping close: all expenses categorized

6. **Actions checklist**
   - [ ] Tax-loss harvesting executed (deadline December 15)
   - [ ] TFSA maxed
   - [ ] FHSA maxed
   - [ ] Expense acceleration complete
   - [ ] December 15 installment paid
   - [ ] Year-end bookkeeping close initiated

---

## Section 3 — Threshold Monitor (Continuous)

These thresholds are checked every session against CC's known financial state. A threshold is "approaching" when within 15% of the trigger point.

### Income Thresholds

| Threshold | Trigger Point | Action Required |
|-----------|--------------|-----------------|
| HST registration | $30,000 gross (trailing 12M) | Register within 29 days of crossing. Voluntary registration available before. Ref: docs/ATLAS_HST_REGISTRATION_GUIDE.md |
| RRSP contributions become high-value | $55,867 taxable income | Marginal rate hits 29.65% — RRSP contributions now save meaningfully |
| Incorporation trigger | $80,000 OASIS revenue (sustained) | Begin incorporation process. Ref: docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md |
| International structure trigger | $120,000+ income | Crown Dependencies evaluation. Ref: docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md |
| Multi-entity architecture | $200,000+ income | OpCo/HoldCo, family trust, RCA. Ref: docs/ATLAS_TAX_STRATEGY.md |

### Asset Thresholds

| Threshold | Trigger Point | Action Required |
|-----------|--------------|-----------------|
| T1135 foreign property | $100,000 CAD cost basis | File T1135 with T1. Late filing: $25/day, max $2,500. Ref: docs/ATLAS_FOREIGN_REPORTING.md |
| T1134 (foreign affiliate) | Any controlled foreign affiliate | File T1134. Complex — flag for specialist. |
| Accredited investor status | $1M financial assets or $200K income | Unlocks exempt market, MIC, flow-through. Ref: docs/ATLAS_ALTERNATIVE_INVESTMENTS.md |

### Tax-Owing Thresholds

| Threshold | Trigger Point | Action Required |
|-----------|--------------|-----------------|
| Installment payments | $3,000 net tax owing (2 consecutive years) | Quarterly installments required March 15, June 15, September 15, December 15. Ref: docs/ATLAS_INSTALLMENT_PAYMENTS.md |
| VDP candidate | Unreported income or gains in prior years | File voluntarily before CRA contacts. Eliminates penalties. Ref: docs/ATLAS_VDP_GUIDE.md |

### Business Thresholds

| Threshold | Trigger Point | Action Required |
|-----------|--------------|-----------------|
| Revenue concentration | Any single client > 50% of revenue | Business risk flag — not tax, but a CFO concern |
| HST remittance (post-registration) | Quarterly or annual threshold | Remit HST collected minus ITCs on schedule |
| Payroll remittances (post-incorporation) | Any payroll run | Due 15th of following month. Late: 3-10% penalty. |

### Crypto Thresholds

| Threshold | Trigger Point | Action Required |
|-----------|--------------|-----------------|
| ACB calculation lag | Any crypto disposition without ACB calc | Run crypto-acb-tracking skill immediately |
| Superficial loss risk | Repurchase within 30 days of crypto sale at loss | Flag — loss denied, adds to ACB of new position |
| CARF reporting (effective 2026) | Any crypto exchange with 10+ transactions or $10K+ | Canadian exchanges will report to CRA automatically |

---

## Section 4 — Regulatory Change Tracker

When regulatory changes are confirmed (CRA announcements, budget day, provincial budgets), update the following:

### Federal Changes to Monitor

| Item | Frequency | Source | Docs to Update |
|------|-----------|--------|----------------|
| TFSA annual limit | Announced in fall federal budget | CRA website | brain/USER.md, Section 3 thresholds |
| RRSP contribution limit (18% of prior income) | Annually on NOA | CRA | skills/quarterly-tax-review/SKILL.md |
| FHSA annual limit | Currently $8,000 — confirm each year | CRA | Section 3, quarterly-tax-review |
| CPP contribution rates | Announced in fall | CRA | docs/ATLAS_PENSION_RETIREMENT_GUIDE.md |
| EI premium rates | Announced in fall | CRA | docs/ATLAS_BOOKKEEPING_SYSTEMS.md |
| Federal corporate tax rate | Federal budget | Finance Canada | docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md |
| Capital gains inclusion rate | Federal budget (2024 changes pending) | Finance Canada | docs/ATLAS_TAX_STRATEGY.md |
| CARF implementation | 2026 effective date | CRA/OECD | docs/ATLAS_DEFI_TAX_GUIDE.md, docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md |
| CRA prescribed interest rate | Quarterly | CRA | docs/ATLAS_TOSI_DEFENSE.md |
| SR&ED rate changes | Federal budget | CRA | docs/ATLAS_AI_SAAS_TAX_GUIDE.md |

### Provincial Changes to Monitor (Ontario)

| Item | Frequency | Source |
|------|-----------|--------|
| Ontario surtax thresholds | Annual | Ontario budget |
| OIDMTC rate (10%) | Budget | Ontario MITE |
| Ontario ESA minimum wage | April 1 each year | Ontario MOL |
| Ontario corporate tax rate (11.5%) | Budget | Ontario budget |

### Treaty and International Changes

| Item | Watch For | Ref Doc |
|------|-----------|---------|
| Canada-UK treaty updates | Post-Brexit renegotiation | docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md |
| Crown Dependencies substance rules | OECD Pillar 2 | docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md |
| CRA exchange data orders | New exchange subpoenas | docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md |

---

## Section 5 — Compliance Calendar (Full Year)

### January
| Date | Deadline | Priority |
|------|----------|----------|
| Jan 1 | New TFSA contribution room opens | P3 |
| Jan 1 | New FHSA contribution room opens ($8,000) | P3 |
| Jan 15 | Begin RRSP contribution analysis (March 1 deadline approaching) | P2 |
| Jan 31 | T4s issued by employers (watch for Nicky's T4) | P2 |

### February
| Date | Deadline | Priority |
|------|----------|----------|
| Feb 15 | RRSP deadline approaching — P1 flag if room remains | P1 |
| Feb 28/29 | Confirm all T-slips received | P2 |

### March
| Date | Deadline | Priority |
|------|----------|----------|
| Mar 1 | **RRSP contribution deadline** (60 days after Dec 31) | P0/P1 |
| Mar 15 | **Q1 installment due** (if installments required) | P1 |
| Mar 31 | T3 slips due from trusts/ETFs | P2 |

### April
| Date | Deadline | Priority |
|------|----------|----------|
| Apr 15 | Flag balance owing if T1 not yet prepared | P1 |
| Apr 30 | **Tax balance owing due — self-employed** | P0 |
| Apr 30 | **T1 filing deadline — employees** | P0 |
| Apr 30 | FHSA — no deadline but confirm Q2 contribution on track | P3 |

### May
| Date | Deadline | Priority |
|------|----------|----------|
| May 15 | Flag June 15 T1 filing deadline — 30 days out | P1 |
| May 31 | HST annual filer deadline (if annual method elected) | P1 |

### June
| Date | Deadline | Priority |
|------|----------|----------|
| Jun 8 | Final flag: T1 filing in 7 days | P0 |
| Jun 15 | **T1 filing deadline — self-employed** | P0 |
| Jun 15 | **Q2 installment due** (if installments required) | P1 |
| Jun 30 | Mid-year income projection — run income-tier-monitoring skill | P2 |

### July
| Date | Deadline | Priority |
|------|----------|----------|
| Jul 15 | HST quarterly filer Q2 remittance due (one month after quarter-end) | P1 |
| Jul 31 | T1135 due if June 15 extension granted | P1 |

### August
| Date | Deadline | Priority |
|------|----------|----------|
| Aug 25 | Flag September 15 installment — 21 days out | P1 |

### September
| Date | Deadline | Priority |
|------|----------|----------|
| Sep 15 | **Q3 installment due** (if installments required) | P1 |
| Sep 30 | Q3 income review complete; Q4 harvest candidate list built | P2 |
| Sep 30 | Incorporation trigger decision point (Q3 revenue known) | P2 |

### October
| Date | Deadline | Priority |
|------|----------|----------|
| Oct 15 | HST quarterly filer Q3 remittance due | P1 |
| Oct 15 | Begin tax-loss harvest candidate list review | P2 |
| Oct 31 | T3 trust year-end (if applicable) | P2 |

### November
| Date | Deadline | Priority |
|------|----------|----------|
| Nov 1 | Tax-loss harvesting window open — P1 flag if candidates exist | P1 |
| Nov 15 | Federal budget typically announced — watch for rate changes | P2 |
| Nov 30 | TFSA/FHSA top-up check — room remaining? | P2 |

### December
| Date | Deadline | Priority |
|------|----------|----------|
| Dec 1 | Flag December 15 installment — 14 days out | P1 |
| Dec 10 | Final tax-loss harvest flag — 5 days until settlement cutoff | P0 |
| Dec 15 | **Tax-loss harvest deadline** (T+2 settlement for Dec 31) | P0 |
| Dec 15 | **Q4 installment due** (if installments required) | P1 |
| Dec 31 | **Year-end: TFSA maxed, FHSA maxed, expenses accelerated** | P1 |
| Dec 31 | Defer December invoices to January if income reduction beneficial | P2 |

---

## Section 6 — Alert Priority System

### Priority Definitions

| Level | Label | Criteria | Atlas Behavior |
|-------|-------|----------|----------------|
| P0 | CRITICAL | Deadline within 7 days OR active penalty risk OR over-contribution | Lead every session with this. Do not move on until CC acknowledges. |
| P1 | HIGH | Deadline within 30 days OR threshold crossed OR installment due | Flag at session start. Include dollar impact. |
| P2 | MEDIUM | Quarterly review due OR documentation gap OR threshold approaching (within 15%) | Include in session summary. Offer to run relevant skill. |
| P3 | LOW | Informational OR optimization opportunity OR future planning trigger | Mention once, do not repeat. |

### Penalty Impact Reference (for dollar-impact estimates)

| Violation | Penalty |
|-----------|---------|
| Late T1 filing (balance owing) | 5% of balance + 1%/month (max 12 months), doubled for repeat |
| Late tax payment | 5% immediately + 1%/month on balance |
| TFSA over-contribution | 1%/month on excess amount |
| Late T1135 | $25/day, minimum $100, maximum $2,500 |
| Late HST remittance | 3% (3 days late), 5% (6 days), 7% (7+ days), 10% (repeat) |
| Late payroll remittance | 3-10% depending on timing and repeat offence |
| Installment shortfall | Interest on shortfall at CRA prescribed rate (currently 8-9%) |
| Unreported income | 50% gross negligence penalty on unreported tax |
| Late T2 (corporate) | 5% + 1%/month |

---

## Section 7 — Compliance Status Report Format

Produce this report whenever P1 or higher alerts exist, or when CC asks about compliance.

```
ATLAS COMPLIANCE STATUS — [DATE]

Overall Status: [GREEN / YELLOW / RED]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P0 CRITICAL (action required immediately)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List P0 items, or "None"]
Each item: WHAT / DEADLINE / PENALTY IF MISSED / ACTION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P1 HIGH (action required within 30 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List P1 items, or "None"]
Each item: WHAT / DEADLINE / PENALTY IF MISSED / ACTION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P2 MEDIUM (this quarter)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List P2 items, or "None"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P3 LOW (informational)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[List P3 items, or "None"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THRESHOLD STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HST ($30K):         [GREEN: $X/$30K] / [YELLOW: $X/$30K — approaching] / [RED: TRIGGERED]
Installments ($3K): [GREEN: <$3K owing] / [RED: TRIGGERED — Q dates: Mar/Jun/Sep/Dec 15]
T1135 ($100K):      [GREEN: $X/$100K] / [YELLOW: approaching] / [RED: FILING REQUIRED]
Incorporation:      [GREEN: <$80K] / [YELLOW: $X — approaching] / [RED: TRIGGERED]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT DEADLINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Next upcoming deadline and days remaining]
```

---

## Section 8 — Cross-References

| Document | Relevance |
|----------|-----------|
| `docs/ATLAS_INSTALLMENT_PAYMENTS.md` | Quarterly payment rules, three safe-harbor methods, penalty calculation |
| `docs/ATLAS_HST_REGISTRATION_GUIDE.md` | $30K threshold, ITCs, quick method, voluntary registration |
| `docs/ATLAS_FOREIGN_REPORTING.md` | T1135 rules, T1134, transfer pricing, foreign tax credits |
| `docs/ATLAS_VDP_GUIDE.md` | Voluntary disclosure — penalty elimination for historic gaps |
| `docs/ATLAS_CRA_AUDIT_DEFENSE.md` | Red flags, documentation standards, audit-proofing |
| `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` | Deduction checklist, timing, documentation requirements |
| `docs/ATLAS_TAX_STRATEGY.md` | Core 25-strategy playbook |
| `docs/ATLAS_INCOME_SCALING_PLAYBOOK.md` | Tier-based strategy selection |
| `docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md` | $80K incorporation trigger, RDTOH, structure planning |
| `docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md` | $120K+ international structure trigger |
| `docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md` | CARF 2026, exchange data orders, audit risk |
| `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` | Monthly close routine, T2125 chart of accounts |
| `skills/accounting-advisor/` | T2125 preparation, expense categorization |
| `skills/quarterly-tax-review/` | Quarterly deep review process |
| `skills/income-tier-monitoring/` | Income tier tracking and threshold alerts |
| `skills/crypto-acb-tracking/` | ACB calculation for crypto dispositions |
| `skills/tax-loss-harvesting/` | Q4 harvest execution |
