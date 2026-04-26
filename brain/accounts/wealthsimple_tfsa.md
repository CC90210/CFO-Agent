---
tags: [account, wealthsimple, tfsa, registered, manual]
type: registered_investment
currency: CAD
api_backed: false
---

# Wealthsimple TFSA

> CC's Tax-Free Savings Account. Self-directed investing. Manual balance entry.
>
> Neighbors: [[README|accounts/]] · [[wealthsimple_fhsa]] · [[wealthsimple_rrsp]] · [[STATE]].

## Purpose

Tax-free growth forever. Highest-priority registered account for CC's current income level (marginal rate < 29.65% → TFSA > RRSP per [[PATTERNS]] FHSA > TFSA > RRSP priority).

## Access

- **API:** Wealthsimple has no public API for self-directed accounts
- **Balance entry:** manual via `data/manual_balances.json` or `cfo/accounts.py manual` command
- **Balance as of 2026-04-15:** $155.16 CAD

## Tax treatment

- **Contribution room:** ~$46K CAD cumulative (if CC never contributed before turning 18 and hasn't since). CRA My Account (currently BLOCKED) will show exact room once unblocked.
- **Contribution tax:** NONE. After-tax dollars in.
- **Growth tax:** NONE. All returns tax-free forever.
- **Withdrawal tax:** NONE.
- **Re-contribution of withdrawals:** allowed in the following calendar year.
- **US dividends:** 15% US withholding tax applies in TFSA (no treaty relief). RRSP is better for US dividends. Growth/non-dividend US stocks are fine in TFSA.
- **Over-contribution penalty:** 1% per month of excess. Never over-contribute.

## CC's strategic allocation

Target profile for this account (per [[USER]] tax-aggressive + growth-horizon mindset):
- **Growth equities** — compounders Atlas researches (Buffett-style). Tax-free growth = best home for highest-return-expectation holdings.
- **Avoid in TFSA:** US dividend payers (15% withholding with no relief), GICs (wasted tax shelter), bonds (ordinary income shielding has lower value than capital-gain shielding).

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Over-contribution | LOW (at current balance) | Atlas tracks cumulative deposits; CRA room re-check when CRA My Account unblocks |
| Wrong-asset-placement | MEDIUM | Atlas enforces the asset-location rule: US dividends → RRSP, not TFSA |
| Custody (Wealthsimple) | LOW | CIPF-insured up to $1M for investment accounts; trust structure on the registered plan |

## Maintenance cadence

- **Monthly:** CC logs in, reads balance, updates manual entry
- **Annual:** contribution-room reconciliation (Jan of each year — new room allocation)
- **Per-trade:** log dispositions for ACB — though inside TFSA, ACB is irrelevant (no tax event)

## Relevant skills

- [[skills/tax-optimization/SKILL|tax-optimization]] — TFSA-vs-other-registered decisioning
- [[skills/portfolio-rebalancing/SKILL|portfolio-rebalancing]] — which assets belong where
- [[skills/financial-planning/SKILL|financial-planning]] — long-term compounding projections

## Notes

- Ticker ENB.TO (Enbridge) pick pending at limit $73, 2 shares (per [[USER]]). First real deployment of TFSA.
- When CC relocates (2028-2031 per exit ladder), TFSA disposition rules apply: ceases to be tax-free for non-residents; interest/dividend subject to non-resident withholding. Plan drawdown or hold-as-foreign-account before departure per [[skills/departure-tax-planning/SKILL|departure-tax-planning]].
