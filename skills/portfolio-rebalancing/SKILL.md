---
name: portfolio-rebalancing
description: Tax-aware portfolio rebalancing — asset allocation, registered account placement, tax-efficient transitions
triggers: [rebalance, allocation, portfolio review, asset allocation, overweight, underweight, drift, diversification]
tier: core
dependencies: [tax-optimization, financial-planning]
---

# Portfolio Rebalancing

## Overview
Periodic portfolio review and rebalancing with full tax awareness. Every rebalance decision considers: which account holds the asset, what the tax cost of selling is, and whether the drift is large enough to justify the transaction.

## When to Use
- Quarterly portfolio review
- When a single position exceeds target allocation by >5%
- When CC asks about asset allocation
- After significant market moves
- When new capital is available to invest

## The Process

### Phase 1: Current State Assessment
1. Pull all holdings across accounts:
   - Kraken (crypto — non-registered)
   - OANDA (gold/forex — non-registered)
   - TFSA (if investments held)
   - RRSP (if investments held)
   - FHSA (if opened and invested)
2. Calculate total portfolio value
3. Calculate current allocation percentages
4. Compare to target allocation

### Phase 2: Tax-Efficient Account Placement
**Which assets belong in which accounts:**

| Asset Type | Best Account | Why |
|-----------|-------------|-----|
| High-growth crypto | TFSA | Tax-free gains on highest-growth assets |
| Crypto ETFs | TFSA | Tax-free, no ACB tracking needed |
| US dividend stocks | RRSP | 0% US withholding (Article XXI treaty) |
| Canadian dividend stocks | Non-registered | Enhanced dividend tax credit |
| Bonds / GICs | RRSP | Interest taxed at full rate — shelter it |
| REITs | TFSA or RRSP | Distributions are income, not eligible dividends |
| Gold ETFs | TFSA | Capital gains tax-free |
| High-growth equities | TFSA | Maximize tax-free room for highest appreciation |
| International stocks | Non-registered | Foreign tax credit available |

### Phase 3: Rebalance Decision
For each position that exceeds drift threshold:
1. **Sell in tax-free account (TFSA/FHSA)?** Do it — no tax consequences
2. **Sell in non-registered?** Calculate capital gain/loss
   - If gain: consider tax cost vs benefit of rebalancing
   - If loss: bonus — harvest the loss AND rebalance
3. **Redirect new contributions?** Often better than selling — no transaction costs or tax

### Phase 4: Execution
1. Prioritize rebalancing with new money (no tax impact)
2. If selling required: execute in tax-free accounts first
3. If selling in non-registered: check superficial loss rule
4. Record all transactions for tax tracking
5. Update ACB records

### Phase 5: Documentation
1. Record new allocation vs target
2. Note rationale for any deviations from target
3. Calculate tax cost of rebalancing (if any)
4. Set next review date

## CC's Target Allocation (Current Stage — Aggressive Growth)
This is a starting framework — adjust as income and risk tolerance evolve.

| Asset Class | Target | Account |
|------------|--------|---------|
| Crypto (BTC/ETH/SOL) | 30-40% | Kraken (non-reg) + TFSA (via ETFs) |
| Gold / Precious Metals | 10-15% | OANDA + TFSA (via ETFs) |
| Growth Equities | 20-30% | TFSA + RRSP |
| Cash / Emergency Fund | 10-15% | HISA (RBC/EQ Bank) |
| FHSA | Max ($8K/year) | Balanced growth fund |
| Alternative (future) | 0-10% | Various |

## Key Rules
- Rebalance with NEW MONEY first (zero tax cost)
- Never rebalance just to rebalance — drift must exceed 5% threshold
- Tax-loss harvesting during rebalance is a bonus, not a goal
- Keep TFSA for highest-growth assets (maximize tax-free compounding)
- Keep RRSP for US dividend stocks (treaty benefit) and bonds (shelter interest)
- Non-registered: Canadian dividends (DTC benefit) and international (FTC)

## Document References
- finance/advisor.py — FinancialAdvisor.suggest_allocation()
- ATLAS_TAX_STRATEGY.md — Account placement optimization
- ATLAS_INCOME_SCALING_PLAYBOOK.md — Allocation by income tier
- ATLAS_ALTERNATIVE_INVESTMENTS.md — Alternative asset options
