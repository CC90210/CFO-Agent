---
name: crypto-acb-tracking
description: CRA-compliant weighted-average ACB tracking for crypto — multi-exchange, superficial loss detection, Schedule 3 preparation
triggers: [ACB, adjusted cost base, cost basis, crypto tax, capital gain, capital loss, Schedule 3, T5008, weighted average, crypto accounting]
tier: core
dependencies: [accounting-advisor]
---

# Crypto ACB Tracking

## Overview
CRA requires weighted-average ACB method for cryptocurrency. This skill manages ACB calculations across all exchanges and wallets, detects superficial losses, and prepares Schedule 3 data.

## When to Use
- Tax filing season (Schedule 3 preparation)
- After significant crypto trading activity
- When CC asks "what's my cost basis?"
- When evaluating tax-loss harvesting candidates
- When checking if a trade would trigger superficial loss

## CRA Rules (Non-Negotiable)

### Weighted-Average ACB
- ACB is calculated as a WEIGHTED AVERAGE across ALL holdings of the same asset
- ALL exchanges and wallets are pooled (Kraken + Wealthsimple + personal wallets = one pool per asset)
- NOT FIFO, NOT LIFO, NOT specific identification
- Formula: ACB per unit = Total ACB of all units / Total units held

### What is a Disposition?
A disposition triggers a gain/loss calculation:
- Yes: Selling crypto for fiat (CAD, USD)
- Yes: Trading crypto for crypto (BTC -> ETH = sell BTC + buy ETH)
- Yes: Using crypto to buy goods/services
- Yes: Gifting crypto (deemed disposition at FMV)
- No: Transferring between own wallets (NOT a disposition)
- No: Buying crypto with fiat (NOT a disposition — it's an acquisition)

### Capital Gain/Loss Calculation
```
Proceeds = amount received (in CAD at date of transaction)
ACB = weighted average cost basis × units sold
Capital Gain/Loss = Proceeds - ACB - Transaction Fees
Taxable Capital Gain = Capital Gain × 50% (or 66.67% above $250K cumulative)
```

## The Process

### Phase 1: Data Collection
1. Export trade history from ALL exchanges:
   - Kraken: Reports -> Export -> Trades (CSV)
   - Wealthsimple: Tax Documents -> Crypto Activity
   - Any DEX activity: manual transaction log
   - Any P2P trades: manual log
2. Export wallet transfers (to verify wallet-to-wallet vs dispositions)

### Phase 2: Data Normalization
1. Convert all amounts to CAD using Bank of Canada daily exchange rate
2. Standardize timestamps (UTC -> EST for CRA)
3. Identify transaction types: buy, sell, swap, transfer, airdrop, staking reward
4. Match wallet transfers (same asset, similar amount, close timestamps = transfer, not trade)

### Phase 3: ACB Calculation (Per Asset)
For each crypto asset:
1. Start with ACB = 0, units = 0
2. For each ACQUISITION (buy, swap-in, airdrop, staking reward):
   - New ACB = (old ACB + cost of acquisition including fees)
   - New units = old units + acquired units
   - ACB per unit = New ACB / New units
3. For each DISPOSITION (sell, swap-out, payment):
   - Capital gain/loss = proceeds - (ACB per unit × units disposed) - fees
   - Remaining ACB = old ACB - (ACB per unit × units disposed)
   - Remaining units = old units - units disposed
4. Record every step (CRA may audit the full calculation)

### Phase 4: Superficial Loss Detection
For each realized LOSS:
1. Check: did CC (or spouse, or controlled corporation) buy the SAME asset within 30 days BEFORE or AFTER the sale?
2. If YES:
   - Loss is DENIED
   - Denied loss is added to ACB of repurchased units
   - Mark in records as "superficial loss — denied, added to ACB"
3. If NO: loss is valid, include on Schedule 3

### Phase 5: Schedule 3 Preparation
1. List all dispositions for the tax year
2. For each: date, description, proceeds, ACB, gain/loss
3. Separate: capital gains vs capital losses
4. Calculate net capital gain/loss
5. Apply 50% inclusion rate (or 66.67% above $250K cumulative)
6. Carry forward any net capital losses (indefinite carryforward)

### Phase 6: Verification
1. Cross-check: ending units per asset match exchange balances
2. Cross-check: total ACB is positive (negative ACB = error)
3. Cross-check: no duplicate transactions (common with CSV exports)
4. Cross-check: all CAD conversions use correct daily rate

## Tools
- finance/tax.py — CryptoTaxCalculator class
  - calculate_capital_gains_tax(): full ACB calculation
  - generate_tax_report(): Schedule 3 + T5008 output
  - suggest_tax_loss_harvesting(): unrealized loss scanner
- Koinly / CoinTracker: third-party verification (cross-check Atlas calculations)

## Common Mistakes
1. Using FIFO instead of weighted average (CRA won't accept)
2. Forgetting crypto-to-crypto swaps are dispositions
3. Not converting to CAD at date of transaction
4. Counting wallet transfers as dispositions (inflates gains)
5. Missing airdrops/staking rewards (income on receipt at FMV)
6. Not tracking across ALL exchanges (ACB must be pooled)

## Document References
- ATLAS_TAX_STRATEGY.md — Crypto tax treatment
- ATLAS_DEFI_TAX_GUIDE.md — DeFi-specific dispositions
- CRA_CRYPTO_ENFORCEMENT_INTEL.md — Audit program, CARF
- finance/tax.py — CryptoTaxCalculator
