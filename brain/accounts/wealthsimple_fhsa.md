---
tags: [account, wealthsimple, fhsa, registered, manual, first-home]
type: registered_investment
currency: CAD
api_backed: false
opened: 2026-03-27
---

# Wealthsimple FHSA

> First Home Savings Account. OPENED 2026-03-27. Self-directed investing. Best-in-class registered vehicle for CC right now.
>
> Neighbors: [[README|accounts/]] · [[wealthsimple_tfsa]] · [[wealthsimple_rrsp]] · [[STATE]] · [[USER]].

## Purpose

First-home savings with TRIPLE tax benefit: deductible contributions (like RRSP) + tax-free growth (like TFSA) + tax-free withdrawal for qualifying home purchase. Stack with HBP for ~$75K tax-advantaged home down-payment capacity over time.

## Access

- **API:** Wealthsimple no public API
- **Balance entry:** manual
- **Balance as of 2026-04-19:** $0 CAD (account opened, not yet funded)

## Tax treatment (CRA guide RC727)

- **Annual contribution limit:** $8,000 CAD
- **Lifetime limit:** $40,000 CAD
- **Unused room carries forward:** up to $8,000 (i.e., can contribute $16K in a year if last year was skipped, but never more than $8K of new room per year)
- **Deduction:** contributions deduct from taxable income in the year of contribution OR later (RRSP-like — bank the deduction for high-bracket years)
- **Growth:** tax-free
- **Withdrawal for qualifying home purchase:** tax-free
- **Withdrawal for non-qualifying use:** fully taxable + no room restored
- **Qualifying home:** CC's first home as principal residence. Must be a Canadian property, CC must not have owned a home in the past 4 years.
- **Close-out:** within 15 years of opening OR by age 71, whichever is earlier. Un-used balance transfers to RRSP tax-free at that point (so no lost room).

## CC's strategic use

- **Contribution sequence:** max $8K this year (2026). Stack with [[wealthsimple_tfsa|TFSA]] as liquid grows. FHSA first priority over TFSA because of the deduction.
- **Deduction timing:** DO NOT claim the deduction in a low-income year. Bank it. Claim when marginal rate is highest (CC is sub-30% rate currently — defer to post-$80K income year).
- **HBP combination:** FHSA + HBP + TFSA stack = $75K-$95K tax-advantaged home purchase.
- **Exit ladder interaction:** if CC emigrates before buying a home, FHSA transfers to RRSP tax-free. Still better than not opening.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Over-contribution | LOW | Atlas tracks cumulative; CRA My Account confirms room once unblocked |
| Non-qualifying withdrawal (expensive) | MEDIUM | Atlas flags ANY withdrawal request before execution; checks qualifying-home status |
| Missed deduction timing | MEDIUM | Atlas defers the deduction claim annually until CC's marginal rate optimizes |
| Custody (Wealthsimple) | LOW | CIPF-insured |

## Maintenance cadence

- **Monthly:** contribution decisions evaluated against cashflow + liquid floor
- **Annual (Feb):** deduction-timing evaluation against T1 projected income
- **Annual:** contribution-room tracker update

## Relevant skills

- [[skills/tax-optimization/SKILL|tax-optimization]] — deduction-timing strategy
- [[skills/financial-planning/SKILL|financial-planning]] — home-purchase timeline integration
- [[skills/departure-tax-planning/SKILL|departure-tax-planning]] — FHSA behavior on non-residency

## Notes

- Opened 2026-03-27 — recorded as a DO NOT RE-SUGGEST item in [[MISTAKES]] prevention rules.
- CC understands mechanics per [[USER]] financial literacy note.
- No current contributions. Funding will be a real KR for Q2 or Q3 OKRs.
