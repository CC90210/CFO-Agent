---
name: tax-loss-harvesting
description: Systematic identification and execution of tax-loss harvesting opportunities — superficial loss detection, Q4 automation, portfolio impact analysis
triggers: [tax-loss, harvest, unrealized loss, superficial, capital loss, loss selling, Q4 tax, year-end tax]
tier: core
dependencies: [accounting-advisor]
---

# Tax-Loss Harvesting

## Overview
Sell investments at a loss to realize a capital loss deduction, reducing tax on other gains. Critical in Q4 for year-end optimization. Must navigate the superficial loss rule.

## When to Use
- Q4 (October-December) — primary harvesting season
- When significant unrealized losses exist in portfolio
- When realized gains need offsetting
- When CC asks about reducing capital gains tax

## The Process

### Phase 1: Portfolio Scan
1. Pull current positions from Kraken (via CCXT API)
2. Pull current positions from OANDA
3. For each position, calculate:
   - Current FMV (market price × quantity)
   - ACB (weighted-average cost basis)
   - Unrealized gain/loss (FMV - ACB)
   - Holding period (days since acquisition)

### Phase 2: Candidate Identification
1. Filter for positions with unrealized LOSSES
2. Rank by absolute loss amount (biggest loss = biggest deduction)
3. Calculate tax savings per candidate: |loss| × 50% inclusion × marginal rate
4. Flag positions you still want exposure to (will need substitute)

### Phase 3: Superficial Loss Check (CRITICAL)
**The Rule (s.40(2)(g) + s.54):**
- If you sell at a loss AND repurchase the SAME property within 30 calendar days (before OR after the sale), the loss is DENIED
- The denied loss is added to the ACB of the repurchased property
- This applies to: you, your spouse, a corporation you control, a trust you're affiliated with
- "Same property" for crypto: same token (BTC is BTC regardless of exchange or wallet)

**Superficial Loss Prevention:**
1. Wait 31 days before repurchasing the same asset
2. OR replace with a correlated but different asset (e.g., sell BTC, buy ETH)
3. OR use the loss denial to your advantage: sell, let 31 days pass, repurchase (if you still want the asset)
4. Track the 30-day window in a spreadsheet or calendar

### Phase 4: Execution Decision
For each candidate:
1. **Sell and don't repurchase:** Best if you've lost conviction in the asset
2. **Sell and substitute:** Sell BTC at loss, buy BTC ETF (different property) — maintains exposure without superficial loss
3. **Sell and wait 31 days:** Best if you want the same asset back — market risk during 31-day gap
4. **Don't harvest:** If the loss is small (<$500) or you expect recovery before year-end

### Phase 5: Impact Analysis
1. Total harvestable losses: $[sum]
2. Total tax savings: $[sum × 50% × marginal rate]
3. Capital loss carryforward: unused losses carry forward indefinitely
4. Capital loss carryback: can apply to 3 prior years (amend prior returns)
5. Net capital losses can ONLY offset capital gains (not business income)

### Phase 6: Execute Trades
1. Place sell orders for approved candidates
2. Record: date, price, quantity, ACB, realized loss
3. Start 31-day superficial loss timer for each sale
4. Set calendar reminder: earliest repurchase date
5. Update ACB records

### Phase 7: Documentation
1. Update crypto ACB tracking spreadsheet
2. Record all dispositions for Schedule 3
3. Note any substitute assets purchased
4. File trade confirmations (6-year retention per s.230)

## Key Rules
- Net capital losses can only offset capital gains, NOT business income
- Unused capital losses carry forward INDEFINITELY
- Capital losses can be carried back 3 years (file T1A)
- Superficial loss: 30 calendar days before AND after sale (61-day window total)
- ACB must be recalculated after every disposition (weighted average)
- Crypto-to-crypto trades ARE dispositions (trigger gains/losses)

## Common Mistakes
1. Repurchasing within 30 days (superficial loss — loss denied)
2. Forgetting spouse's trades count for superficial loss rule
3. Not tracking ACB after harvest (inflated future gains)
4. Harvesting losses on assets you should hold long-term (selling winners to save pennies)
5. Ignoring transaction costs (if loss is small, costs may exceed tax savings)

## Document References
- ATLAS_TAX_STRATEGY.md — Capital gains strategies
- ATLAS_DEFI_TAX_GUIDE.md — DeFi disposition rules
- CRA_CRYPTO_ENFORCEMENT_INTEL.md — Audit triggers
- finance/tax.py — CryptoTaxCalculator.suggest_tax_loss_harvesting()
