---
name: financial-health-check
description: >
  Comprehensive financial health assessment — 8-dimension scoring (0-100),
  Canadian benchmark comparison, red/yellow/green status flags, prioritized
  action plan ranked by dollar impact, and quarterly trend tracking.
  Run at onboarding and at the start of each quarter.
triggers: [health check, financial checkup, how am I doing, financial score, benchmark, assessment, onboarding, score my finances, quarterly review, financial grade]
tier: core
dependencies: [accounting-advisor, financial-planning, income-tier-monitoring]
---

# Financial Health Check

> A doctor's full-body checkup — for money. Produces a composite score across 8
> financial dimensions, compares against Canadian benchmarks, flags urgent issues,
> and delivers a prioritized action plan with dollar-value estimates.
> Run at onboarding for new users. Run at the start of Q1/Q2/Q3/Q4 for CC.

---

## When to Run

| Trigger | Cadence |
|---------|---------|
| New user onboarding | Once (first session) |
| Quarterly CFO review | Q1 (Jan), Q2 (Apr), Q3 (Jul), Q4 (Oct) |
| Major life event | Income jump, new debt, job change, relocation |
| CC asks "how am I doing" | Immediately |

---

## Step 1 — Data Collection Protocol

Before scoring, collect or retrieve the following. Check `brain/USER.md` first — never ask
CC for information that is already documented.

### Pull from brain/USER.md (no questions needed)
- Age, province, citizenship
- All income sources and current MRR
- Asset balances (TFSA, RRSP, FHSA, Kraken, Wise, Wealthsimple)
- Liabilities (OSAP balance, credit card debt)
- Tax filing status and compliance notes
- Business structure (sole prop vs incorporated)
- Equipment and deductible assets

### Ask CC only if not documented
| Data Point | Why Needed | Estimate if Unknown |
|------------|-----------|---------------------|
| Monthly take-home after tax | Savings rate calc | Use gross income - 20% tax |
| Monthly expenses (total) | Emergency fund coverage | Use $2,500/mo CAD default |
| Insurance policies held | Insurance dimension | Assume none if not mentioned |
| Outstanding debt balances and rates | Debt health dimension | Use OSAP balance from USER.md |
| Investment account growth YTD | Net worth trajectory | Use current balances |

### Calculate from available data
- Total net worth = sum of all assets - all liabilities
- Monthly savings = monthly income - monthly expenses
- Savings rate = monthly savings / monthly gross income
- Emergency fund ratio = liquid savings / monthly expenses
- Debt-to-income = total debt / annual gross income

---

## Step 2 — Financial Health Score (0-100)

Score 8 dimensions. Sum equals the composite Health Score.

### Dimension 1 — Emergency Fund Coverage (0-15 pts)

**What it measures:** Months of expenses covered by liquid, non-investment savings.

| Coverage | Points | Status |
|----------|--------|--------|
| 0 months | 0 | RED |
| < 1 month | 3 | RED |
| 1-2 months | 6 | YELLOW |
| 3 months | 10 | YELLOW |
| 4-5 months | 12 | GREEN |
| 6+ months | 15 | GREEN |

**Formula:** `liquid_savings / monthly_expenses` = months covered
**Liquid savings** = chequing + savings + Wise (exclude crypto, trading accounts, RRSP)

---

### Dimension 2 — Debt Health (0-15 pts)

**What it measures:** Debt-to-income ratio, interest rate burden, good vs bad debt mix.

| D/I Ratio | Base Points | Notes |
|-----------|-------------|-------|
| 0% (no debt) | 15 | GREEN |
| 1-15% | 12 | GREEN |
| 16-30% | 9 | YELLOW |
| 31-50% | 5 | YELLOW |
| > 50% | 2 | RED |

**Adjustments:**
- All debt is student loans (0% interest via RAP): +2 pts (low-rate, income-protected)
- Any high-interest debt (credit card > 15%): -3 pts per account
- All debt is tax-deductible (Smith Manoeuvre, business loans): +2 pts

**Formula:** `total_debt / annual_gross_income`

---

### Dimension 3 — Savings Rate (0-15 pts)

**What it measures:** Percentage of gross income saved or invested each month.

| Savings Rate | Points | Status |
|-------------|--------|--------|
| < 5% | 2 | RED |
| 5-10% | 5 | RED |
| 11-20% | 8 | YELLOW |
| 21-30% | 11 | YELLOW |
| 31-50% | 13 | GREEN |
| > 50% | 15 | GREEN |

**Note:** For early-stage entrepreneurs with variable income, use a 3-month rolling average.
**Canadian median savings rate:** ~5-8%. High earner target: 20-30%. FIRE target: 40-60%.

---

### Dimension 4 — Tax Efficiency (0-15 pts)

**What it measures:** How much of available tax optimization is being captured.

| Sub-Factor | Max Points | Criteria |
|------------|-----------|---------|
| Registered account utilization | 5 | TFSA + FHSA open and contributing |
| Deduction capture rate | 4 | Business expenses, CCA, home office claimed |
| Income structure optimization | 3 | Optimal split, incorporation at trigger |
| Proactive planning | 3 | Installments current, no penalties |

**Score guide:**
- 13-15 pts (GREEN): All accounts open, deductions maximized, proactive quarterly planning
- 9-12 pts (YELLOW): Some accounts unused, deductions partially captured
- 0-8 pts (RED): TFSA/FHSA unused, filing late, missing major deductions, penalties

---

### Dimension 5 — Insurance Coverage (0-10 pts)

**What it measures:** Appropriate coverage relative to risk profile and income level.

| Coverage Type | Points | Notes |
|--------------|--------|-------|
| Provincial health (OHIP) | 2 | Assumed for all Ontario residents |
| Tenant/renter's insurance | 2 | Required if renting; covers equipment |
| Business liability (E&O) | 3 | Critical for consultants/SaaS providers |
| Disability / income protection | 3 | Protects primary income source |

**Score guide:**
- 9-10 pts (GREEN): All relevant coverage in place
- 5-8 pts (YELLOW): Basic coverage, missing one key policy
- 0-4 pts (RED): Major gaps; one event could erase wealth

---

### Dimension 6 — Income Diversification (0-10 pts)

**What it measures:** Number of income streams and concentration risk.

| # of Active Streams | Base Points | Notes |
|--------------------|-------------|-------|
| 1 (single source) | 2 | RED |
| 2 | 4 | YELLOW |
| 3 | 7 | YELLOW |
| 4+ | 9 | GREEN |

**Adjustments:**
- Single client > 80% of revenue: -3 pts (concentration risk)
- Single client 50-80%: -1 pt
- Passive income stream present (dividends, rental, royalties): +1 pt (max 10)
- No concentration risk (no single source > 40%): +1 pt

---

### Dimension 7 — Net Worth Trajectory (0-10 pts)

**What it measures:** Net worth growth rate vs age benchmarks and personal targets.

**Canadian net worth benchmarks by age:**

| Age | Median | Top 25% | Top 10% |
|-----|--------|---------|---------|
| 20-24 | $5K-$15K | $30K-$60K | $80K+ |
| 25-29 | $20K-$50K | $75K-$150K | $200K+ |
| 30-34 | $60K-$100K | $200K-$350K | $500K+ |

**Scoring:**
- Above top 10% for age bracket: 10 pts (GREEN)
- Top 25-10% for age bracket: 8 pts (GREEN)
- Median to top 25%: 6 pts (YELLOW)
- Below median but positive and growing: 4 pts (YELLOW)
- Negative net worth (liabilities > assets): 2 pts (RED)
- Net worth shrinking quarter-over-quarter: 0 pts (RED)

**For new users with no prior snapshot:** Score based on current position vs benchmark only.

---

### Dimension 8 — Business Health (0-10 pts)

**What it measures:** Gross margin, cash runway, revenue growth, concentration.
Skip or score 5/10 if user has no business income.

| Sub-Factor | Max Points | Criteria |
|------------|-----------|---------|
| Revenue growth rate | 3 | > 20%/mo = 3, > 10%/mo = 2, growing = 1 |
| Gross margin | 3 | > 70% = 3, > 50% = 2, > 30% = 1 |
| Cash runway | 2 | 3+ months expenses covered by business account |
| Client concentration | 2 | No single client > 50% = 2, > 50% = 1, > 80% = 0 |

---

## Step 3 — Composite Score and Grade

```
Health Score = sum of all 8 dimensions (max 100)
```

| Score | Grade | Assessment |
|-------|-------|------------|
| 85-100 | A | Financially excellent — optimize and compound |
| 70-84 | B | Strong foundation — address yellow flags |
| 55-69 | C | Functional but gaps present — immediate action needed |
| 40-54 | D | Significant vulnerabilities — prioritize red flags now |
| 0-39 | F | Financial emergency — multiple urgent issues |

---

## Step 4 — Red / Yellow / Green Status Flags

After scoring, produce a status table showing each dimension's flag and a one-line finding.

```
DIMENSION           | SCORE | STATUS  | FINDING
Emergency Fund      | 0/15  | RED     | $0 liquid savings — one event away from crisis
Debt Health         | 11/15 | YELLOW  | OSAP $9K at 0% effective via RAP — low risk but present
Savings Rate        | 5/15  | RED     | Variable income, no consistent savings habit yet
Tax Efficiency      | 11/15 | YELLOW  | FHSA opened, TFSA underused, deductions partially captured
Insurance           | 2/10  | RED     | Only OHIP — no tenant's, no E&O, no disability
Income Diversity    | 4/10  | RED     | 4 streams but 94% Bennett concentration
Net Worth           | 5/10  | YELLOW  | Below age median but young + high-trajectory business
Business Health     | 8/10  | GREEN   | 64.99% MRR growth, high margin SaaS — strong signal
```

---

## Step 5 — Benchmark Comparison

Compare the composite score and each dimension against three benchmarks.

| Benchmark | Source | Composite Target |
|-----------|--------|-----------------|
| Canadian average (age 22) | StatsCan + CRA data | ~35-45 |
| High-income earner (age 22, $50K+) | Financial planning industry | ~55-65 |
| Entrepreneur benchmark (early-stage) | Startup financial health norms | ~50-60 |

Present as:

```
Your Score: XX/100 (Grade: X)

vs Canadian average (age 22):   +/- XX points  [ABOVE / BELOW / AT]
vs High-income earner benchmark: +/- XX points  [ABOVE / BELOW / AT]
vs Entrepreneur benchmark:       +/- XX points  [ABOVE / BELOW / AT]

Strongest dimension: [name] — [score/max]
Weakest dimension:   [name] — [score/max]
```

---

## Step 6 — Prioritized Action Plan

Rank the top 5 actions by estimated dollar impact (saved, earned, or protected).
Format each action identically.

```
ACTION #1 — [Title]
What:       [One sentence — exactly what to do]
Why:        [One sentence — why this is the highest priority]
Impact:     [Dollar estimate — saved per year, protected, or gained]
Effort:     [Low / Medium / High] | Time: [e.g., "30 minutes", "1 week"]
Status:     [RED flag address / YELLOW optimization / GREEN maintain]
Reference:  [docs/ATLAS_DOCUMENT.md — section name]
```

**Impact estimation rules:**
- Always estimate in CAD
- Emergency fund: impact = income protection value (3 months income)
- Insurance gap: impact = risk exposure (e.g., equipment value, annual revenue)
- Tax deduction missed: impact = deduction amount × marginal tax rate
- Registered account unused: impact = annual contribution limit × marginal rate + tax-free growth
- Concentration risk: impact = revenue at risk if largest client churns

---

## Step 7 — Quarterly Trend Tracking

On Q2/Q3/Q4 runs (when a prior score exists), produce a trend table.

```
DIMENSION           | Q1 2026 | Q2 2026 | CHANGE | TREND
Emergency Fund      | 0/15    | 3/15    | +3     | IMPROVING
Savings Rate        | 5/15    | 8/15    | +3     | IMPROVING
Tax Efficiency      | 11/15   | 13/15   | +2     | IMPROVING
Insurance           | 2/10    | 2/10    | 0      | STALLED — action needed
Income Diversity    | 4/10    | 7/10    | +3     | IMPROVING — 3 new clients
Net Worth           | 5/10    | 6/10    | +1     | IMPROVING
Business Health     | 8/10    | 9/10    | +1     | IMPROVING
Overall             | 46/100  | 60/100  | +14    | SIGNIFICANT IMPROVEMENT
```

**Trend interpretation:**
- +5 or more on a dimension in one quarter: flag as major win — explain why
- 0 change on a RED dimension: flag as stalled — escalate to action plan top slot
- Decline on any GREEN dimension: flag as regression — investigate root cause

**Where to store scores:** Append a dated entry to `memory/LONG_TERM.md` after each run.

---

## Step 8 — CC Current Assessment (Q1 2026 Baseline)

Running the full model against CC's actual numbers from `brain/USER.md` as of 2026-03-27.

### Input Data

| Data Point | Value | Source |
|------------|-------|--------|
| Age | 22 | USER.md |
| Monthly gross income (current) | ~$4,100 CAD ($2,982 USD MRR) | USER.md |
| Monthly expenses (estimated) | ~$1,500-$2,000 CAD | USER.md (lives rent-free) |
| Liquid savings | ~$3,300 CAD total | USER.md |
| OSAP debt | ~$9,000 CAD | USER.md |
| Credit card debt | Unknown (monitored) | Estimate: $500 CAD |
| TFSA balance | $155.16 CAD | USER.md |
| FHSA | $0 (just opened) | USER.md |
| RRSP | $0 | USER.md |
| Crypto (Wealthsimple) | $206.41 CAD | USER.md |
| Kraken | ~$183 CAD | USER.md |
| Income streams | 4 active (OASIS, Nicky's, DJ, Trading) | USER.md |
| Bennett concentration | ~94% of revenue | USER.md |
| Business growth rate | 64.99% MRR growth | USER.md |
| Insurance | OHIP only (assumed) | Not documented — assumed |

### Dimension Scores

**D1 — Emergency Fund: 0/15 (RED)**
- Liquid savings: ~$1,900 USD Wise + ~$155 TFSA + ~$500 RBC chequing (estimated) = ~$3,300 CAD
- Monthly expenses: ~$1,500 CAD (rent-free, frugal baseline)
- Coverage: ~2.2 months
- Score: 6/15 (1-2 months bracket)
- Finding: Thin cushion. One client churn (Bennett = 94% of revenue) = financial emergency within 60 days.

**D2 — Debt Health: 11/15 (YELLOW)**
- Total debt: ~$9,500 CAD (OSAP $9,000 + estimated $500 credit card)
- Annual gross income: ~$49,200 CAD ($4,100 x 12)
- D/I ratio: ~19%
- Base score: 9 (16-30% bracket)
- Adjustment: OSAP effectively 0% via RAP at current income = +2 pts
- Score: 11/15
- Finding: Manageable debt load. OSAP is low-risk. Watch credit card balance.

**D3 — Savings Rate: 5/15 (RED)**
- Monthly income: ~$4,100 CAD gross
- Monthly expenses: ~$1,500 CAD estimated
- Implied savings capacity: ~$2,600 CAD but no consistent savings habit documented
- Self-reported: "pretty broke," spending more than he should
- Score: 5/15 (using 5-10% estimate — income is there but savings not flowing to accounts)
- Finding: Income is strong for age 22 but money is not being captured. No automated saving in place.

**D4 — Tax Efficiency: 10/15 (YELLOW)**
- TFSA: open but $155 (room ~$46K unused) = partial (-1)
- FHSA: just opened March 27, 2026 — $8K room accumulating = +2 (proactive)
- RRSP: unused but low priority at current income level = neutral
- Deductions: CCA, home office, subscriptions — NOT YET CLAIMED for 2025 (unfiled)
- Installments: not yet required at current income
- Score: 10/15
- Finding: FHSA opened is a win. 2025 return unfiled with deductions on the table. TFSA contribution room sitting idle at 0% return.

**D5 — Insurance Coverage: 2/10 (RED)**
- OHIP (provincial health): 2 pts assumed
- Tenant's insurance: not documented — assumed none (lives with parents, so lower urgency)
- E&O / business liability: none documented — HIGH RISK for AI consultant
- Disability: none documented
- Score: 2/10
- Finding: Major gap. As an AI consultant with $50K+ revenue, a single client dispute or error could result in a lawsuit with zero coverage.

**D6 — Income Diversification: 4/10 (RED)**
- Active streams: OASIS AI (~94% Bennett), Nicky's part-time, DJ (seasonal), Trading (minimal)
- 4 streams present = base 9 pts
- Bennett > 80% concentration = -3 pts
- Score: 4/10 (was 9, heavily penalized by concentration)
- Finding: 4 streams on paper but effectively a single-client business. Bennett churning = $2,500 USD/mo gone overnight. Diversification is the single biggest financial risk.

**D7 — Net Worth Trajectory: 4/10 (YELLOW)**
- Current net worth: ~$3,300 CAD assets - ~$9,500 liabilities = approximately -$6,200 CAD
- Age 22 Canadian median: $5K-$15K positive
- Currently below median (negative net worth)
- However: trajectory is sharply positive — income scaling from $0 to ~$50K in 12 months
- Score: 4/10 (below median, but positive growth trajectory earns partial credit)
- Finding: Technically negative net worth but entirely attributable to OSAP. Business trajectory puts CC in top 10% for age 22 within 12-18 months if income holds.

**D8 — Business Health: 8/10 (GREEN)**
- Revenue growth: 64.99% MRR growth = 3/3
- Gross margin: SaaS/consulting margins typically 70-85% = 3/3
- Cash runway: ~2 months Wise balance = 1/2 (thin but not critical)
- Client concentration: Bennett > 80% = 0/2
- Score: 7/10 (capped by concentration)
- Finding: Exceptional growth rate for a 22-year-old solo founder. Margin profile is strong. Concentration is the only real business health concern.

### Composite Score

```
D1 Emergency Fund:    6/15
D2 Debt Health:      11/15
D3 Savings Rate:      5/15
D4 Tax Efficiency:   10/15
D5 Insurance:         2/10
D6 Income Diversity:  4/10
D7 Net Worth:         4/10
D8 Business Health:   7/10
----------------------------
TOTAL:               49/100   Grade: D
```

### Benchmark Comparison

```
CC's Score: 49/100 (Grade: D)

vs Canadian average (age 22):    ~35-45  — ABOVE average  (+4 to +14 pts)
vs High-income earner benchmark: ~55-65  — BELOW target   (-6 to -16 pts)
vs Entrepreneur benchmark:       ~50-60  — AT/BELOW range (-1 to -11 pts)

Strongest dimension: Debt Health (11/15) — OSAP is structured and low-risk
Weakest dimension:   Insurance (2/10)    — Largest absolute gap from ideal
Biggest opportunity: Emergency Fund + Savings Rate — both fixable with income that already exists
```

### CC's Prioritized Action Plan (Q1 2026)

```
ACTION #1 — Get E&O/Professional Liability Insurance
What:    Purchase a professional liability (Errors & Omissions) policy for OASIS AI Solutions.
Why:     One client lawsuit with zero coverage could wipe out all assets plus future earnings.
         At $50K+ AI consulting revenue, this is non-negotiable.
Impact:  Protects ~$50K-$200K in annual revenue; eliminates existential financial risk.
Effort:  Low | Time: 1-2 hours online (BFL Canada, Hiscox, or broker quote)
Status:  RED — immediate action required
Reference: docs/ATLAS_INSURANCE_ESTATE_PROTECTION.md — Professional Liability section

ACTION #2 — Build a $4,500 Emergency Fund (3 months)
What:    Automate $500/month from Wise USD transfers → RBC TFSA until $4,500 CAD reached.
Why:     Bennett represents 94% of revenue. One conversation could end $2,500 USD/mo overnight.
         Currently 2.2 months coverage — needs to reach 3 months minimum.
Impact:  Protects ~3 months of expenses ($4,500); prevents debt spiral on client loss.
Effort:  Low | Time: 15 minutes to set up auto-transfer
Status:  RED — structural vulnerability
Reference: skills/financial-planning/SKILL.md — Emergency Fund targets

ACTION #3 — File 2025 Tax Return with All Deductions (Before June 15, 2026)
What:    File T1 + T2125 with CCA (computer $989.25, Class 50), home office, all subscriptions,
         OSAP interest (Line 31900), and DJ expenses. Use Wealthsimple Tax → NETFILE.
Why:     Every month of delay costs refund dollars and keeps deductions unclaimed.
         Estimated $800-$1,500 CAD in deductions + $541 CPP self-employed credit.
Impact:  $800-$1,500 CAD refund/savings; cleans CRA record before installments become required.
Effort:  Medium | Time: 2-4 hours with Atlas guiding each line
Status:  YELLOW — deadline June 15, payment due April 30
Reference: docs/ATLAS_DEDUCTIONS_MASTERLIST.md — T2125 checklist

ACTION #4 — Start Putting Money Into TFSA (Target $500/month)
What:    Open automatic monthly contribution from RBC to Wealthsimple TFSA.
         Buy XEQT (all-equity ETF) — one holding, no decisions needed.
Why:     $46K of TFSA room is sitting at 0%. Every dollar in there compounds tax-free forever.
         At 22, this is the single highest long-term wealth building action available.
Impact:  $500/month compounding at 8% for 40 years = ~$1.6M tax-free at age 62.
         More immediately: $6,000/year growing tax-free vs taxable account saves ~$200-$300/yr in tax now.
Effort:  Low | Time: 20 minutes to set up
Status:  YELLOW — optimization opportunity
Reference: docs/ATLAS_TAX_STRATEGY.md — Strategy 1 (TFSA maximization)

ACTION #5 — Diversify Revenue Away from Bennett (1 new client target by June 2026)
What:    Land 1 new paying client (minimum $500 USD/mo) through Bravo's pipeline by June 2026.
         This moves Bennett from 94% concentration to ~83% — not perfect but trending right.
Why:     Concentration risk is the single largest threat to CC's financial plan. Every dollar of
         diversification reduces dependency and makes the business financeable/sellable later.
Impact:  $6,000+ USD/year in new revenue; reduces single-client failure risk by ~15%.
Effort:  High | Time: Ongoing — delegate strategy to Bravo (CEO agent)
Status:  RED — systemic business risk
Reference: docs/ATLAS_BUSINESS_STRUCTURES.md — client concentration risk section
```

---

## Output Format

Always end a health check with this summary block:

```
ATLAS FINANCIAL HEALTH CHECK — [Date] — [Quarter]
Score: XX/100 — Grade: [A/B/C/D/F]
Strongest: [dimension] ([score/max])
Weakest:   [dimension] ([score/max])
REDs:      [count] — [dimension names]
YELLOWs:   [count] — [dimension names]
GREENs:    [count] — [dimension names]
Top action: [Action #1 title] — est. $[impact] impact
Next check: [Date of next quarterly run]
```

---

## Document References

| Doc | Relevant Dimensions |
|-----|-------------------|
| `docs/ATLAS_TAX_STRATEGY.md` | Tax Efficiency (D4) |
| `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` | Tax Efficiency (D4) — filing |
| `docs/ATLAS_INSURANCE_ESTATE_PROTECTION.md` | Insurance (D5) |
| `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` | Business Health (D8), Savings Rate (D3) |
| `docs/ATLAS_DEBT_LEVERAGE_STRATEGY.md` | Debt Health (D2) |
| `docs/ATLAS_INCOME_SCALING_PLAYBOOK.md` | Income Diversification (D6) |
| `docs/ATLAS_WEALTH_PLAYBOOK.md` | Net Worth Trajectory (D7) |
| `docs/ATLAS_TREATY_FIRE_STRATEGY.md` | Net Worth Trajectory (D7) — FIRE endgame |
| `skills/financial-planning/SKILL.md` | Emergency Fund (D1), FIRE targets |
| `skills/income-tier-monitoring/SKILL.md` | Tax Efficiency (D4), tier thresholds |
| `skills/accounting-advisor/SKILL.md` | Business Health (D8), deduction capture |
