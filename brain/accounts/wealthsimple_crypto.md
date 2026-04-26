---
tags: [account, wealthsimple, crypto, non-registered, manual]
type: crypto_holding
currency: CAD
api_backed: false
---

# Wealthsimple Crypto

> CC's buy-and-hold crypto account. Non-registered, distinct from [[kraken|Kraken]] (active trading). Manual balance entry.
>
> Neighbors: [[README|accounts/]] · [[kraken]] · [[STATE]] · [[skills/crypto-acb-tracking/SKILL|crypto-acb-tracking]].

## Purpose

Long-term crypto holding. BTC primarily. ZERO DISPOSITIONS — only buys and transfers. The account is by design tax-event-free (per [[USER]] CRITICAL note).

## Access

- **API:** Wealthsimple Crypto has no public API for self-directed users
- **Balance entry:** manual
- **Balance as of 2026-04-15:** $206.41 CAD
- **Holdings:** BTC
- **ACB:** $356.39 (CC is currently UNDER water; unrealized loss)

## Tax treatment

- **Buys:** non-event. ACB accumulates per weighted-average method.
- **Transfers (wallet-to-wallet, same beneficial owner):** non-event for CRA (Folio S3-F4-C1 treats internal transfers as non-dispositions).
- **Sales (disposition):** would trigger capital gain/loss at disposition price minus ACB.
- **Swap to another crypto:** would trigger disposition (CRA technical interpretation 2014-0561081E5).
- **Current status:** ZERO sales, zero swaps → zero tax events. Clean.

## Why ZERO DISPOSITIONS is the strategic choice

CC's current marginal rate is low. A realized loss now = small tax shield. A realized gain now = tax paid at low rate but then no compounding runway. For BTC specifically:
- **Long-term thesis:** digital-gold narrative + fiat debasement tailwind. CC holds long.
- **Tax deferral:** holding defers any gain into a jurisdiction decision. At UK tax residency (FIG regime 2028-2031), first 4 years = 0% on foreign gains → disposition during FIG window could be tax-free if structured correctly.
- **Rule:** Atlas flags ANY Wealthsimple crypto disposition request as a HIGH-IMPACT decision requiring explicit CC confirmation + tax-event modeling.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Accidental disposition | LOW (manual-only account) | Atlas's ZERO DISPOSITION rule surfaces on every interaction |
| ACB drift | LOW | Zero dispositions = ACB reconciliation is trivial |
| Custody (Wealthsimple Crypto) | MEDIUM | Held via third-party custodian (Gemini → now ZeroHash). Known custody-chain caveats apply. Insurance coverage ≠ CDIC. |
| Price volatility | HIGH | Inherent; position size small (~3% of liquid) |
| Regulatory change | MEDIUM | Wealthsimple Crypto operates under OSC; pairs may shrink |

## Maintenance cadence

- **Quarterly:** balance update + verify zero activity
- **Annual:** ACB snapshot for record (no tax filing needed — no disposition)
- **Pre-departure (ages 25-28):** full disposition-timing strategy session; [[skills/departure-tax-planning/SKILL|departure-tax-planning]] runs the numbers

## Relevant skills

- [[skills/crypto-acb-tracking/SKILL|crypto-acb-tracking]] — primary
- [[skills/departure-tax-planning/SKILL|departure-tax-planning]] — FIG-window disposition strategy
- [[skills/tax-optimization/SKILL|tax-optimization]] — comparative: TFSA vs non-registered crypto long-hold

## Notes

- NOT a trading account — different role from [[kraken|Kraken]]. Kraken = active trading, ACB tracked per-trade; Wealthsimple Crypto = zero-activity long-hold.
- BTC ACB $356.39 vs market $206.41 = unrealized loss ~$150. Harvesting would be available but: (a) CC has no gains to offset, (b) superficial-loss rule (30-day) would apply if re-buying, (c) the narrative hold is multi-year.
