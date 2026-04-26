---
name: unit-economics-validation
version: 0.1.0
status: PROBATIONARY
description: "CFO-side gate for CMO ad-spend requests. Validates a proposed campaign on CAC, LTV, contribution margin, payback period, and target close rate BEFORE Atlas approves any portion of the cap. Approves, partial-approves, or rejects with a one-paragraph rationale."
metadata:
  category: spend-governance
  owner: atlas
  consumers: [maven-spend-requests, bravo-runway-decisions]
  tier: full
triggers: [validate-unit-economics, check-ltv-cac, ad-spend-gate, spend-approval, maven-request, review-campaign-math]
sources:
  - "Benjamin Graham — margin of safety (unit economics must clear with buffer, not at parity)"
  - "Warren Buffett / Berkshire letters — owner earnings, durable advantage, reinvestment ROI"
  - "David Skok / For Entrepreneurs — SaaS LTV:CAC > 3, CAC payback < 12 months"
  - "Alex Hormozi — Value Equation, CFO-side pairs with Maven's offer-side"
  - "Philip Fisher — 15 points (retention, operator skill, real growth vs vanity)"
  - "CPA Canada — audit-defensible cost classification (T2125 line 8521)"
---

# unit-economics-validation — CFO Spend Gate

> Maven draws up the campaign. Atlas checks the math. No ad dollar leaves until the unit economics clear.

## When to invoke

**Automatic** whenever:
1. `data/pulse/cmo_pulse.json.current_spend_request_cad > 0`
2. A new brand or channel is proposed
3. CAC or close rate moves ±20% from the last approved baseline
4. Spend request > 25% of current `approved_ad_spend_monthly_cap_cad`

**Manual**: any time the operator or Bravo asks "should we greenlight this spend?"

## Required inputs (Maven must provide; Atlas rejects if missing)

| Field | Definition | Source of truth |
|-------|------------|-----------------|
| `channel` | Meta, Google, TikTok, cold email, organic | Maven campaign brief |
| `brand` | OASIS / Bennett-shared / SunBiz / PropFlow / Nostalgic | Maven pulse |
| `proposed_monthly_spend_cad` | Total budget before buffer | Maven request |
| `target_cpl_cad` | Cost per lead, forecasted | Maven forecast / historical |
| `target_close_rate_pct` | Lead → paying customer conversion | Bravo CRM / historical |
| `avg_deal_size_cad` | First-touch revenue | Stripe / invoice history |
| `gross_margin_pct` | After cost of delivery (excl. ad spend) | CFO books / brand_economics in cfo_pulse |
| `expected_retention_months` | Median customer lifetime | Cohort data if available, else sector benchmark |
| `time_to_payback_months` | Months until cumulative GM >= CAC | Derived |

If any field is forecast-only (no historical evidence), flag it `SPECULATIVE` and demote the approval to experimentation-only.

## The 5 Checks

### Check 1 — LTV:CAC ratio (Skok's 3:1 rule)
```
CAC            = proposed_monthly_spend_cad / (leads × close_rate)
LTV            = avg_deal_size_cad × gross_margin_pct × expected_retention_months
                 (for subscription products: use MRR × gross_margin × avg_lifetime_months)
LTV:CAC ratio  = LTV / CAC

PASS if ratio >= 3.0
WATCH if 2.0 <= ratio < 3.0  (allow only if at least one lever has headroom)
FAIL if ratio < 2.0
```
Rationale: Skok's canonical benchmark. Below 3:1 the business can grow but generates no surplus to compound. Below 2:1 growth actively destroys capital.

### Check 2 — CAC payback period (the cashflow check)
```
monthly_gross_margin_per_customer = avg_deal_size_cad × gross_margin_pct
                                    / expected_retention_months
payback_months                    = CAC / monthly_gross_margin_per_customer

PASS if payback_months <= 12  (SaaS default)
PASS if payback_months <= 6   (services / one-time revenue)
WATCH if 12 < payback_months <= 18
FAIL if payback_months > 18
```
Rationale: Atlas guards the capital floor. Long payback periods compound into runway problems if retention misses. Canadian sole-prop tax treatment amplifies the hit (spend is deductible but cash is cash).

### Check 3 — Positive contribution margin at target close rate
```
contribution_per_customer = (avg_deal_size_cad × gross_margin_pct) - CAC

PASS if contribution_per_customer > 0 AND close_rate IS historical (not forecast)
WATCH if contribution_per_customer > 0 but close_rate IS a forecast (allow 25% of cap)
FAIL if contribution_per_customer <= 0
```
Rationale: Graham's margin of safety. Positive contribution with forecast close rate = theoretical; with historical close rate = validated.

### Check 4 — Concentration and runway drag
```
Read cfo_pulse.json.liquid_cad and montreal_floor_target_cad.
Read ceo_pulse concentration_risk_single_client_pct.

IF liquid_cad < montreal_floor_target_cad:
    cap_multiplier = 0.5
IF concentration_risk_single_client_pct >= 70:
    cap_multiplier *= 0.5
IF concentration_risk_single_client_pct >= 80:
    spend_veto = True

approved_cap_cad = approved_ad_spend_monthly_cap_cad × cap_multiplier
```
Rationale: Capital preservation beats growth. No campaign is worth taking the operator below the relocation floor. No campaign is worth doubling down on a concentrated revenue book.

### Check 5 — T2125 deductibility
Spend on line 8521 (advertising) is a dollar-for-dollar deduction against self-employment income. Post-CCPC it deducts at the CCPC bracket (~12.2% in Ontario on first $500K). Atlas logs the expected tax offset so the after-tax spend number is honest.
```
after_tax_spend = proposed_monthly_spend_cad × (1 - marginal_rate)
Note: marginal_rate is a savings, NOT a justification. A deductible bad spend is still a bad spend.
```

## Decision matrix

| Check 1 | Check 2 | Check 3 | Check 4 | Decision |
|---------|---------|---------|---------|----------|
| PASS    | PASS    | PASS    | OK      | **APPROVE** up to cap |
| PASS    | PASS    | WATCH   | OK      | **PARTIAL** at 50% of cap, require 14-day CAC feedback |
| PASS    | WATCH   | PASS    | OK      | **PARTIAL** at 50% of cap, require payback re-proof by day 30 |
| FAIL anywhere | —   | —       | —       | **REJECT** with specific failing metric + what would unblock |
| any     | any     | any     | veto    | **REJECT** regardless — concentration/floor breach |

## Output format Atlas writes into `cfo_pulse.json`

```json
"maven_spend_decision": {
  "request_id": "<uuid or timestamp>",
  "campaign": "pulse-lead-gen",
  "brand": "OASIS",
  "requested_cad": 1200,
  "approved_cad": 100,
  "decision": "PARTIAL",
  "checks": {
    "ltv_cac": { "value": 4.2, "verdict": "PASS" },
    "payback_months": { "value": 9.1, "verdict": "PASS" },
    "contribution_margin": { "value": 180, "verdict": "WATCH", "reason": "close_rate is forecast" },
    "concentration": { "value": 94, "verdict": "VETO_ACTIVE", "cap_multiplier": 0.25 },
    "deductibility": { "line": "T2125 8521", "marginal_rate": 0.2565 }
  },
  "rationale": "LTV:CAC healthy, payback inside 12 months. Close rate is a forecast not historical, so downgraded to experimentation only. Bennett concentration at 94% caps total monthly spend at $100 CAD until diversification below 70%.",
  "unblock_at": ["Bennett concentration < 70%", "14-day historical close rate ≥ forecast", "liquid_cad ≥ $10K floor"]
}
```

## Anti-patterns Atlas actively rejects

1. **"Trust the creative"** — creative variance is real but can't rescue broken unit economics. Reject.
2. **"Scale reveals retention"** — retention gets WORSE at scale (light buyers have lower loyalty per Sharp). Don't budget based on early-cohort retention.
3. **"We'll make it back on upsell"** — model upsell separately with its own LTV. Primary purchase must stand on its own.
4. **"Competitors spend more so we should"** — competitor spend is not a signal of their unit economics. They may be burning capital too.
5. **"Lifetime value is theoretical anyway"** — no: without LTV, every campaign is a gamble. Require historical cohort data or use conservative sector median.

## When to probationary-promote → VALIDATED

After 3 successful decisions where:
- The approval rationale held (6-month post-approval review)
- Maven hit CAC within ±15% of target
- No capital-floor breach occurred

Log review outcomes in `memory/PATTERNS.md` as they happen.

## Cross-references

- [[CFO_CANON]] — the investors/frameworks this skill derives from (pillars 1–5 especially)
- [[AGENT_ORCHESTRATION]] — pulse protocol, spend handshake sequence
- [[skills/financial-health-check/SKILL|financial-health-check]] — concentration and runway inputs
- [[skills/position-sizing/SKILL|position-sizing]] — parallel sizing logic for equity positions
- [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] — the loop that promoted this skill from gap to build
- [[STATE]] — live `liquid_cad` + `approved_ad_spend_monthly_cap_cad`
- `cfo_pulse.json.brand_economics` — per-brand gross margin inputs to Check 1
- [[INDEX]] — graph hub

## Success metrics for this skill itself

| Metric | Target | Review cadence |
|--------|--------|----------------|
| Approval accuracy | ≥ 80% of approvals hit target CAC within ±15% | Monthly |
| Rejection accuracy | ≥ 80% of rejections would have burned capital if approved | Quarterly (retrospective on rejected campaigns) |
| Time-to-decision | < 10 minutes from Maven request → pulse write | Per-request |
| CC override rate | < 10% of decisions overridden by operator | Monthly |

If any metric trips below target for two consecutive reviews, trigger self-improvement Protocol 4 Reflexion on this skill.
