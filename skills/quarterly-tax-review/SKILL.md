---
name: quarterly-tax-review
description: Proactive quarterly tax optimization — income tracking, deduction timing, registered account management, installment planning
triggers: [quarterly, tax review, Q1, Q2, Q3, Q4, quarter end, year end, tax planning, installment]
tier: core
dependencies: [accounting-advisor, tax-optimization, financial-planning]
---

# Quarterly Tax Review

## Overview
Every quarter, Atlas proactively reviews CC's tax position and identifies optimization opportunities. This skill prevents year-end scrambles and catches opportunities that have deadlines.

## When to Use
- End of each calendar quarter (March, June, September, December)
- When CC's income changes significantly
- When major purchases or investments are planned
- When CC asks "how are we doing on taxes?"

## The Process

### Phase 1: Income Assessment (10 min)
1. Estimate YTD income from ALL sources:
   - OASIS: Check Stripe/Wise for revenue
   - Nicky's: T4 data or paycheck estimate
   - DJ: Count gigs × rate
   - Crypto: Realized gains/losses on Kraken
   - OANDA: Realized gains/losses
2. Annualize: (YTD income ÷ months elapsed) × 12
3. Determine income tier from ATLAS_INCOME_SCALING_PLAYBOOK.md
4. Compare to last quarter — tier change?

### Phase 2: Deduction Review (10 min)
1. Review business expenses since last quarter
2. Any major purchases planned? Accelerate before quarter-end?
3. Home office deduction: has anything changed? (moved, renovated)
4. Vehicle log up to date?
5. Software subscriptions — all tracked?
6. Professional development — any courses or conferences?

### Phase 3: Registered Accounts (5 min)
1. FHSA: contributed? Room remaining? ($8K/year)
2. TFSA: contributed? Room remaining? ($7K/year, ~$46K cumulative)
3. RRSP: contribution decision (only if marginal rate ≥ 29.65%)
4. Deadline awareness: RRSP contribution deadline is March 1

### Phase 4: Tax-Loss Harvesting (10 min, especially Q4)
1. Review unrealized losses in crypto portfolio
2. Identify candidates for harvesting (sell at loss, realize deduction)
3. CHECK: superficial loss rule — cannot repurchase within 30 days
4. Calculate tax savings: loss × marginal rate
5. Decision: harvest now or hold? (consider future potential)

### Phase 5: Installment Check (5 min)
1. Estimate total tax owing for the year
2. Will it exceed $3,000? (remember: CPP counts toward this)
3. If installments needed: which method is optimal?
   - Rising income → prior-year method (lower payments)
   - Falling income → current-year method (avoid overpayment)
4. Next payment date?

### Phase 6: Forward Planning (10 min)
1. Incorporation trigger: is revenue approaching $80K sustained?
2. International planning: is income approaching $120K+ (Crown Dependencies)?
3. Departure tax snapshot: what would it cost to leave today?
4. Any upcoming deadlines? (filing, payments, elections)

### Phase 7: Report
Generate quarterly brief for CC:
```
Q[X] 2026 Tax Review

Income: $[YTD] / $[annualized estimate]
Tier: [X] ($[range])
Tier change: [Yes/No — if yes, new strategies unlocked]

Registered Accounts:
- FHSA: $[contributed] / $8,000
- TFSA: $[contributed] / $7,000
- RRSP: [decision]

Tax-Loss Harvesting: [opportunities or "none identified"]
Installments: [required? amount? next due date?]
Deductions: [anything to accelerate?]

Key Actions:
1. [most important item]
2. [second item]
3. [third item]
```

## Quarter-Specific Focus

| Quarter | Special Focus |
|---------|--------------|
| Q1 (Jan-Mar) | RRSP deadline (March 1), tax filing prep, gather documents |
| Q2 (Apr-Jun) | April 30 payment due, June 15 filing deadline, mid-year income check |
| Q3 (Jul-Sep) | Mid-year review, incorporation trigger check, plan Q4 harvesting |
| Q4 (Oct-Dec) | TAX-LOSS HARVESTING, max registered accounts, accelerate deductions, year-end planning |

## Document References
- ATLAS_INCOME_SCALING_PLAYBOOK.md — Income tier strategies
- ATLAS_INSTALLMENT_PAYMENTS.md — Installment calculations
- ATLAS_DEDUCTIONS_MASTERLIST.md — Deduction checklist
- ATLAS_TAX_STRATEGY.md — Core 25-strategy playbook
