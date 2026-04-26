---
tags: [account, stripe, payment-processor, usd, api-backed]
type: payment_processor
currency: USD
api_backed: true
---

# Stripe

> CC's card-payment processor for OASIS (SaaS subscriptions) and Nostalgic (DJ side-income). Restricted read-only API key live.
>
> Neighbors: [[README|accounts/]] · [[STATE]] · [[BRANDS]] · [[ENV_STRUCTURE]] · [[wise_business]].

## Purpose

Accept credit card subscriptions and one-time payments. Pay out USD to [[wise_business|Wise USD]]. Two brands live here: OASIS AI Solutions + Nostalgic (DJ).

## Access

- **API:** restricted key (`STRIPE_API_KEY` = `rk_live_...`) — read-only scope
- **Read path:** `cfo/accounts.py::StripeReader` → pulse refresh
- **Scope:** balance, charges, invoices, customers, subscriptions. Cannot initiate charges, refunds, or payouts.

## Current state

- Active subscribers: 2 (OASIS beyond Bennett)
- MRR: $180.96 USD (Stripe dashboard)
- 4-week gross volume: $182.47
- MRR growth rate: 64.99% (very early stage — tiny base)
- Payout schedule: weekly → [[wise_business|Wise USD]]

## Tax treatment

- **Revenue recognition:** cash basis (sole-prop default) or accrual (elected). Stripe invoices = accrual-adjacent; document on receipt for cash-basis CC.
- **Stripe fees:** 2.9% + $0.30 per transaction = deductible T2125 line 8710 (other business expenses) OR line 8760 (bank charges). Track separately from revenue.
- **International buyers:** Stripe handles the transaction. CC reports the gross (in USD → CAD at spot); Stripe fees deduct separately. Don't net.
- **HST/GST:** at CC's sole-prop scale (< $30K TTM from CAD buyers), no GST/HST registration required yet. Monitor — the threshold triggers at $30K rolling 4-quarter.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Payout failure | LOW | Wise USD connection tested; backup ACH to RBC possible if Wise ever breaks |
| Chargeback | LOW | SaaS product = subscription-based; chargeback risk much lower than e-commerce |
| Restricted-key revocation | LOW | Atlas uses ONE restricted key; rotation needs manual swap in `.env` (per [[SOUL]] Rule #11 — no auto-rotate) |
| Account hold | MEDIUM | Stripe occasionally freezes accounts of small-MRR sellers with sudden spikes. Maintain usage pattern consistency. |

## Maintenance cadence

- **Daily:** pulse refresh pulls balance + recent charges
- **Monthly:** reconcile Stripe dashboard revenue ↔ Wise payouts ↔ CC's T2125 rolling tally
- **Quarterly:** fee audit — what % of revenue went to Stripe fees? If > 3.5%, investigate (international transactions, currency conversions)

## Relevant skills

- [[skills/cash-flow-invoicing/SKILL|cash-flow-invoicing]] — Stripe invoicing for non-subscription bookings
- [[skills/financial-health-check/SKILL|financial-health-check]] — MRR momentum input
- [[skills/accounting-advisor/SKILL|accounting-advisor]] — T2125 revenue/fee categorization

## Notes

- Two brands share one Stripe account today (OASIS + Nostalgic). When revenue scales, separate them into Stripe Connect sub-accounts or separate accounts entirely — this cleans up T2125 bookkeeping.
- Bravo (CEO) also has Stripe access for customer-facing ops (subscription management UI, refund authority). Atlas's access is read-only financial — no role overlap.
