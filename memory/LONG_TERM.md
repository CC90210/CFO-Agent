---
name: ATLAS Long-Term Facts
description: High-confidence persistent facts about CC, markets, and the system — with confidence scores and verification dates
tags: [facts, persistent, long-term, confidence]
---

# ATLAS Long-Term Facts

> Each fact carries a confidence score (0.0–1.0) and last verification date.
> Facts not verified in 90+ days get flagged for review.
> Confidence decays: Business facts λ=0.02, Technical λ=0.015, Architecture λ=0.005, Identity λ=0

---

## CC Identity & Profile (λ=0, no decay)

| Fact | Confidence | Last Verified |
|------|-----------|---------------|
| CC is Conaugh McKenna, age 22, Collingwood ON | 1.0 | 2026-03-27 |
| CC holds Canadian + British dual citizenship | 1.0 | 2026-03-27 |
| CC is eligible for Irish citizenship (ancestry) | 0.95 | 2026-03-27 |
| CC runs OASIS AI Solutions (sole proprietor) | 1.0 | 2026-03-27 |
| CC is self-employed (T2125 filer) | 1.0 | 2026-03-27 |
| CC works part-time at Nicky's (family restaurant) | 0.95 | 2026-03-27 |
| CC DJs seasonally (~13 gigs/year × $100) | 0.9 | 2026-03-27 |
| CC has OSAP debt (~$9K) | 0.9 | 2026-03-26 |
| CC banks with RBC (primary) and Wise (multi-currency) | 0.95 | 2026-03-26 |
| CC has NOT opened FHSA yet | 0.95 | 2026-03-27 |
| CC filed 2025 taxes (SIN 567 502 901) | 1.0 | 2026-03-27 |

## Financial Facts (λ=0.02, verify quarterly)

| Fact | Confidence | Last Verified |
|------|-----------|---------------|
| Kraken equity: ~$136 USD | 0.85 | 2026-03-27 |
| OASIS MRR target: $5K USD by May 15, 2026 | 0.9 | 2026-03-27 |
| Current MRR: ~$2,982 USD (94% from Bennett) | 0.85 | 2026-03-27 |
| Wise USD balance: well below $100K T1135 threshold | 0.9 | 2026-03-26 |
| TFSA cumulative room: ~$46K (if unused) | 0.8 | 2026-03-26 |
| Ontario USDT restriction: must use /USD pairs | 1.0 | 2026-03-27 |
| Departure tax today: ~$0 (minimal asset base) | 0.9 | 2026-03-27 |

## Tax Law Facts (λ=0.015, verify semi-annually)

| Fact | Confidence | Last Verified |
|------|-----------|---------------|
| CCPC SBD rate (Ontario): 12.2% | 0.95 | 2026-03-27 |
| Ontario top marginal rate: 53.53% (>$220K) | 0.95 | 2026-03-27 |
| Capital gains inclusion: 50% (first $250K), 66.67% (above) | 0.95 | 2026-03-27 |
| FHSA: $8K/year, $40K lifetime, deduction + tax-free growth + tax-free withdrawal | 0.95 | 2026-03-27 |
| SR&ED credit: 35% federal + 8% Ontario = 43% refundable (CCPC <$500K) | 0.95 | 2026-03-27 |
| CRA installment threshold: >$3K tax owing in current AND prior year | 0.95 | 2026-03-27 |
| Self-employed filing deadline: June 15 (payment April 30) | 1.0 | 2026-03-27 |
| HST small supplier threshold: $30K (not $40K) | 0.95 | 2026-03-27 |
| Crypto ACB method: weighted average (CRA mandatory) | 1.0 | 2026-03-27 |
| Superficial loss rule: 30-day window | 1.0 | 2026-03-27 |
| CARF starts: 2026 (crypto exchanges auto-report to CRA) | 0.9 | 2026-03-27 |

## International Tax Facts (λ=0.015)

| Fact | Confidence | Last Verified |
|------|-----------|---------------|
| Guernsey corporate rate: 0% (most companies) | 0.95 | 2026-03-27 |
| Isle of Man corporate rate: 0% (standard) | 0.95 | 2026-03-27 |
| Jersey corporate rate: 0% (standard) | 0.95 | 2026-03-27 |
| Ireland corporate rate: 12.5% (trading income) | 0.95 | 2026-03-27 |
| Ireland KDB rate: 6.25% (qualifying IP income) | 0.9 | 2026-03-27 |
| Crown Dependencies: 0% capital gains tax | 0.95 | 2026-03-27 |
| Canada-UK treaty: capital gains taxed only in state of residence (Art XIII) | 0.9 | 2026-03-27 |
| Irish passport via Foreign Births Registry: €278, 6-12 months | 0.85 | 2026-03-27 |

## System Architecture Facts (λ=0.005, slow decay)

| Fact | Confidence | Last Verified |
|------|-----------|---------------|
| Trading strategies: 12+ active (regime-aware) | 0.95 | 2026-03-27 |
| Kill switches: 15% DD, 5% daily, 1.5% per-trade | 1.0 | 2026-03-27 |
| Regime detector uses min_hold_bars=6 hysteresis | 0.95 | 2026-03-26 |
| OANDA requires Semaphore(2) — max 2 concurrent calls | 1.0 | 2026-03-26 |
| Windows daemon: subprocess.Popen with DETACHED_PROCESS | 1.0 | 2026-03-26 |
| Async CCXT: must use await, NOT asyncio.to_thread() | 1.0 | 2026-03-26 |
| Brain files: 12 (Session 23 expansion) | 1.0 | 2026-03-27 |
| Tax documents: 25 (~24,300 lines) | 1.0 | 2026-03-27 |
| Bravo (CEO) at Business-Empire-Agent: READ ONLY | 1.0 | 2026-03-27 |
