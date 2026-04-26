---
tags: [accounts, registry, cfo, brain-subdir]
---

# accounts/ — Per-Account Briefs

> Every financial account CC operates gets a brief here. Atlas reads these to answer account-specific questions without guessing. Mirrors Bravo's `brain/clients/` subdirectory pattern, scoped for CFO concerns.
>
> Companion to [[BRANDS]] (per-brand economics) — brands produce revenue; accounts store/move it.
>
> Neighbors: [[INDEX]] · [[STATE]] · [[USER]] · [[ENV_STRUCTURE]] · [[DASHBOARD]].

## Account registry (2026-04-19)

| Account | Type | Currency | API-backed? | Balance (CAD) | Brief |
|---------|------|----------|:-:|--------------:|-------|
| Wise Business USD | Business multi-currency | USD | YES | $6,224 | [[wise_business]] |
| Stripe | Payment processor | USD → Wise payouts | YES | varies | [[stripe]] |
| Kraken | Crypto exchange | USD | YES | $183 | [[kraken]] |
| OANDA | Forex/metals broker | CAD base | YES | varies | [[oanda]] |
| Wealthsimple TFSA | Registered investment | CAD | MANUAL | $155 | [[wealthsimple_tfsa]] |
| Wealthsimple FHSA | Registered investment | CAD | MANUAL | $0 | [[wealthsimple_fhsa]] |
| Wealthsimple RRSP | Registered investment | CAD | MANUAL | $0 | [[wealthsimple_rrsp]] |
| Wealthsimple Crypto | Crypto holding | CAD | MANUAL | $206 | [[wealthsimple_crypto]] |
| RBC Checking | Day-to-day banking | CAD | MANUAL | $164 | [[rbc_checking]] |

**Total liquid (last reconciled 2026-04-18):** $7,023 CAD.

## Account-file conventions

Every account brief contains:
1. **Frontmatter** with tags, type, currency, API-backed flag
2. **Purpose** — what role this account plays in CC's overall structure
3. **Access** — how Atlas reads it (API key? manual entry? external tool?)
4. **Tax treatment** — registered vs non-registered; foreign-property reporting; deemed disposition rules if any
5. **Risk flags** — currency, custody, counterparty, concentration
6. **Maintenance cadence** — how often to reconcile
7. **Wikilinks** to [[STATE]], [[ENV_STRUCTURE]], relevant skills

## Maintenance rules

1. **One file per account.** No shared files. When an account closes, move its brief to `accounts/_archived/` (to be created on first archive), don't delete.
2. **Never write credentials here.** Documented in [[ENV_STRUCTURE]]; this folder is committed.
3. **Balance numbers are indicative only.** Pulse file (`data/pulse/cfo_pulse.json`) is the authoritative current balance; these briefs hold context that doesn't move balance-by-balance.
4. **Tax treatment must cite the CRA section/folio.** If the answer is "I'd have to look it up," look it up first.
