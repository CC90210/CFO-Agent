---
tags: [account, wise, business, usd, multi-currency, api-backed]
type: business_multi_currency
currency: USD
api_backed: true
---

# Wise Business USD

> CC's primary USD holding account — the largest single balance. API-read live every `python scripts/refresh.py` run.
>
> Neighbors: [[README|accounts/]] · [[STATE]] · [[BRANDS]] · [[ENV_STRUCTURE]] · [[stripe]].

## Purpose

CC stores USD revenue here. Bennett pays via Wise payment link directly into this account. Stripe payouts also land here. CAD conversion happens only when CC needs CAD for living expenses — reduces FX-spread bleed.

## Access

- **API:** Wise API token (`WISE_API_TOKEN`) + profile ID (`WISE_PROFILE_ID`) — see [[ENV_STRUCTURE]]
- **Read path:** `cfo/accounts.py::WiseReader` → pulse refresh
- **Scope:** read-only. No outgoing-transfer permission on Atlas's token.

## Current state (2026-04-17 live read)

- USD balance: $4,543
- CAD-equivalent @ 1.37 FX: $6,224
- Share of total liquid: 88.6%

## Tax treatment

- **Reporting jurisdiction:** Ontario (CC's current tax residency)
- **CRA view:** USD income converts to CAD at spot rate on receipt date — CRA s.261(2) (functional-currency election not applicable to sole-prop individuals)
- **T1135 threshold:** foreign-property cost base > $100K CAD triggers T1135 foreign-property reporting. Current cost base well below. Monitor quarterly.
- **GAAR risk:** none — genuine business transactions through a commercial multi-currency provider.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Currency (USD-denominated income in CAD tax jurisdiction) | MEDIUM | Natural hedge: USD revenues, USD expenses (API fees, Stripe fees). Net exposure modest. |
| Custody (Wise holding CC's funds) | LOW | Wise is FCA-regulated in UK, licensed as MSB in Canada. Funds segregated in partner banks. Still not CDIC-insured like a bank deposit — treat as fintech risk. |
| Counterparty (Wise solvency) | LOW | Public company (NYSE: WISE), profitable, scale. Monitor quarterly earnings if exposure grows. |
| Concentration (89% of liquid in one fintech) | HIGH | At current scale OK — cost of spreading across multiple providers > benefit. Reassess at $50K+ liquid. |

## Maintenance cadence

- **Daily:** API read via pulse refresh — automatic
- **Quarterly:** manual reconciliation with Wise statements — catches any drift
- **Annual:** T1135 trigger check; FX-rate documentation for T2125

## Relevant skills

- [[skills/financial-health-check/SKILL|financial-health-check]] — pulls this balance into runway calc
- [[skills/cross-border-compliance/SKILL|cross-border-compliance]] — T1135 and CRS reporting
- [[skills/cash-flow-invoicing/SKILL|cash-flow-invoicing]] — Wise payment links for invoicing

## Notes

- Bennett pays USD here via Wise link; Atlas treats Bennett revenue as USD-denominated until withdrawal
- OASIS Stripe payouts route here (USD payout setting)
- When CC incorporates (CCPC trigger at $80K+), a new Wise Business account should be opened in the corp's name; this personal business account stays for sole-prop tail income
