---
name: income-tier-monitoring
description: Dynamic income tier tracking — monitors CC's income across all sources and flags strategy changes at tier boundaries
triggers: [income tier, income level, tax bracket, how much do I make, income tracking, tier change, bracket change]
tier: core
dependencies: [quarterly-tax-review, tax-optimization]
---

# Income Tier Monitoring

## Overview
CC's income determines which tax strategies are available and optimal. This skill tracks income across all sources and alerts when tier boundaries are crossed, unlocking new strategies.

## When to Use
- Quarterly tax review (scheduled)
- When CC reports new income (client contract, gig, windfall)
- When asking "what strategies are available at my income?"
- When income changes significantly (new client, lost client, crypto windfall)

## Income Tiers (from ATLAS_INCOME_SCALING_PLAYBOOK.md)

| Tier | Income Range | Key Strategies Unlocked | Ontario Marginal Rate |
|------|-------------|------------------------|----------------------|
| 0 | $0 - $30K | Basic deductions, CWB, TFSA, FHSA | 20.05% |
| 1 | $30K - $55K | HST decision, crypto optimization | 20.05-29.65% |
| 2 | $55K - $100K | RRSP valuable, incorporation decision ($80K), installments | 29.65-33.89% |
| 3 | $100K - $200K | Corporate structure, SR&ED, CDA, Crown Dependencies eval | 33.89-46.41% |
| 4 | $200K - $500K | OpCo/HoldCo, family trust, COLI, LCGE planning, prescribed rate loan | 46.41-53.53% |
| 5 | $500K - $2M | Multi-entity architecture, IPP, RCA, flow-through | 53.53% |
| 6 | $2M+ | APA, private foundation, dynasty planning | 53.53% |

## Tier Change Alerts

When income crosses a boundary:
1. Identify OLD tier and NEW tier
2. List strategies that are NOW available
3. List strategies that may no longer be optimal
4. Calculate dollar impact of new strategies
5. Report to CC with specific recommendations

**Example alert:**
```
TIER CHANGE: Tier 1 -> Tier 2 ($55K+ income)

NEW strategies unlocked:
- RRSP contributions now save 29.65% per dollar (was 20.05% — not worth it before)
- Installment payments may be required (check: >$3K tax owing?)
- Incorporation analysis recommended (approaching $80K trigger)

Dollar impact:
- RRSP $10K contribution: saves $2,965 (was $2,005 at Tier 1)
- Incorporation at $80K: saves ~$5K-$8K/year in tax deferral

Recommended actions:
1. Start contributing to RRSP (up to bringing taxable income to $55,867)
2. Track OASIS revenue monthly — incorporation trigger at $80K sustained
3. Review installment payment obligations
```

## Monitoring Cadence
- **Quarterly:** Full income assessment (SOP-004)
- **Monthly:** Quick estimate from Stripe/Wise/paychecks
- **On event:** New client contract, major crypto gain, job change

## Income Source Tracking

| Source | How to Track | Frequency |
|--------|-------------|-----------|
| OASIS AI Solutions | Stripe dashboard / Wise transfers | Monthly |
| Nicky's | T4 / paycheck stubs | Bi-weekly |
| DJ Income | Gig count × rate | Per gig |
| Crypto Trading | Kraken realized P&L | Weekly |
| OANDA Trading | OANDA account summary | Weekly |

## Document References
- ATLAS_INCOME_SCALING_PLAYBOOK.md — Full tier breakdown
- ATLAS_TAX_STRATEGY.md — Strategy details
- ATLAS_INSTALLMENT_PAYMENTS.md — When installments kick in
- ATLAS_INCORPORATION_TAX_STRATEGIES.md — $80K trigger analysis
