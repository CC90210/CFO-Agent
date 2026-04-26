---
tags: [account, rbc, checking, banking, manual, cad]
type: bank_checking
currency: CAD
api_backed: false
---

# RBC Checking

> CC's day-to-day Canadian banking. Minimal balance by design. Manual entry.
>
> Neighbors: [[README|accounts/]] · [[STATE]] · [[USER]] · [[MISTAKES]].

## Purpose

Day-to-day Canadian spending: e-transfers, debit card, rent (when applicable), groceries, convenience-store/gym spend. Real money parked elsewhere ([[wise_business|Wise USD]] primarily).

## Access

- **API:** RBC has no free public API for personal checking
- **Balance entry:** manual via CC updating `data/manual_balances.json` or ad-hoc via Atlas CLI

## Current state

- Balance as of 2026-04-18: $164 CAD (down from $700 after gym + convenience store leak — flagged as a spending pattern to watch)
- Weekly budget cap: $165 CAD (set 2026-04-18 by CC)

## Tax treatment

- **Interest income:** T5 slip if > $50 CAD/year in interest. Current balance generates < $5/yr — non-material. Line 12100 when filed.
- **No T1135 implication:** domestic account.
- **Sole-prop bookkeeping:** CC ideally runs a SEPARATE RBC business checking for OASIS transactions to avoid commingling. Current state = commingled — a [[CFO_CANON]] § CPA Canada anti-pattern. See [[OKRs]] Objective 2 for resolution.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Lifestyle drift (convenience-store / gym overspend) | MEDIUM | Weekly $165 cap enforced via CC self-awareness; Atlas surfaces weekly burn during session briefs |
| Commingling personal + business expenses | MEDIUM | Open separate RBC Business Checking — on Q2 2026 to-do list |
| Overdraft | LOW (at $164) | N/A at current balance |
| Zero-interest idle capital | LOW | Balance too small to worry about; structural issue at > $1K idle (then move to Wise or GIC) |

## Maintenance cadence

- **Weekly:** CC sanity-checks balance; Atlas asks during session
- **Monthly:** reconcile against `data/receipts_cache.json` + Wise inflows to catch mis-categorized transactions
- **Trigger:** if balance trends upward past $1K, move surplus to Wise (idle-cash rule)

## Relevant skills

- [[skills/cash-flow-invoicing/SKILL|cash-flow-invoicing]]
- [[skills/accounting-advisor/SKILL|accounting-advisor]] — separation of business/personal
- [[skills/financial-health-check/SKILL|financial-health-check]] — burn-rate monitoring

## Notes

- The 2026-04-18 RBC drop ($700 → $164) is noted in [[STATE]] Known Blockers as a LOW-severity but watchable lifestyle pattern.
- Spending categories to watch from receipts: convenience store (non-essential), gym (essential — keep), groceries (essential).
- Montreal move planning: RBC checking is fine to keep through the move; only change if CC needs Quebec-based branch access.
