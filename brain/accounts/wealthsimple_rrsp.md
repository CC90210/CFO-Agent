---
tags: [account, wealthsimple, rrsp, registered, manual, deferred]
type: registered_investment
currency: CAD
api_backed: false
---

# Wealthsimple RRSP

> Registered Retirement Savings Plan. Active but intentionally un-used at current income level.
>
> Neighbors: [[README|accounts/]] · [[wealthsimple_fhsa]] · [[wealthsimple_tfsa]] · [[USER]] · [[MISTAKES]].

## Purpose

Tax-deferred retirement savings. For CC at current income (< $55,867 → < 29.65% marginal rate), RRSP is SUBOPTIMAL — FHSA and TFSA beat it. Slow-deploy by design.

## Access

- **API:** Wealthsimple no public API
- **Balance entry:** manual
- **Balance as of 2026-04-19:** $0 CAD

## Tax treatment

- **Deduction:** contributions deduct at current marginal rate
- **Withdrawal:** fully taxable at then-marginal rate (+ withholding at source)
- **Growth:** tax-deferred (not tax-free)
- **Non-resident withdrawal:** 25% non-resident withholding (reducible to 15% under some treaties — UK yes, Isle of Man no, Ireland yes)
- **Contribution room:** 18% of previous-year earned income, capped annually ($31,560 for 2025). CC's prior year earned income was ~$6,347 → room ~$1,142 for 2026.

## Why CC's RRSP is intentionally minimal

The asymmetric-tax mistake: contributing at 25.55% marginal (below $55K income) and withdrawing at 29.65%+ marginal (retirement income or mid-career income) = net loss. See [[MISTAKES]] § RRSP Contribution Below $55K.

**Rule (per [[PATTERNS]] FHSA > TFSA > RRSP priority):** Contribute to RRSP only when marginal rate ≥ 29.65% ($55,867+ income).

## Strategic use (future)

When CC crosses $55K+ income:
1. Evaluate RRSP vs corp retention (post-CCPC). Corp retention often wins for reinvestable income.
2. RRSP best for US dividends via treaty-relieved withholding (0% US withholding on RRSP dividends vs 15% in TFSA).
3. Home Buyer's Plan (HBP) — borrow up to $60K from RRSP for first home, repay over 15 years.

## Exit-ladder interaction (important)

Per CC's exit ladder (2028-2031 Canadian tax residency exit):
- At departure, RRSP continues to be tax-deferred (no deemed disposition under s.128.1(4) exception for RRSPs)
- Withdrawals post-emigration: 25% non-resident withholding (UK: reducible to 15% via treaty; Isle of Man: no treaty, 25% applies)
- Treaty planning: UK withholding is the best treaty; RRSP withdrawals timed during UK tax years could be optimal
- Alternative: lump-sum wind-down pre-emigration at Canadian marginal rate (may be higher than 15% treaty rate → worse)

**Implication:** keep RRSP small until the exit ladder is executed, then evaluate wind-down vs slow-withdrawal.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Over-contribution | LOW (room is tiny) | Atlas tracks |
| Wrong-time contribution (low marginal rate) | MEDIUM | Atlas rejects any contribution suggestion below $55K income |
| Non-resident withholding surprise at exit | MEDIUM | [[skills/departure-tax-planning/SKILL\|departure-tax-planning]] models this before departure |

## Maintenance cadence

- **Annual:** room reconciliation (NOA line)
- **Trigger events:** income crosses $55K or $80K — re-evaluate contribution strategy

## Relevant skills

- [[skills/tax-optimization/SKILL|tax-optimization]]
- [[skills/departure-tax-planning/SKILL|departure-tax-planning]]
- [[skills/financial-planning/SKILL|financial-planning]]
