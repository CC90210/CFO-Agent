---
name: tax-optimization
description: >
  Registered account optimization (TFSA, RRSP, FHSA), tax-loss harvesting,
  incorporation planning, and year-end tax strategies for Canadian residents.
triggers: [TFSA, RRSP, FHSA, tax-loss, harvest, incorporate, incorporation, registered account, contribution room, HBP]
tier: core
dependencies: [accounting-advisor]
---

# Tax Optimization — Registered Accounts & Strategic Planning

> Maximizes CC's after-tax wealth through registered account optimization,
> tax-loss harvesting, and strategic income timing.

## Overview

Three pillars of tax optimization:
1. **Registered accounts** — FHSA, TFSA, RRSP placement for tax-free/deferred growth
2. **Tax-loss harvesting** — Crystallize losses to offset gains before year-end
3. **Incorporation timing** — Transition from sole proprietor to CCPC when revenue justifies it

## Registered Account Priority

```
FHSA (#1) → TFSA (#2) → RRSP (#3)

Why this order:
- FHSA: Tax deduction NOW + tax-free growth + tax-free withdrawal for home = triple benefit
- TFSA: Tax-free growth forever, no deduction but most flexible
- RRSP: Tax deduction now, taxed on withdrawal — save room for higher-income years
```

## FHSA Strategy (Priority 1)

| Parameter | Value |
|-----------|-------|
| Annual limit | $8,000 |
| Lifetime limit | $40,000 |
| Carryforward | Yes ($8K/year) |
| Tax benefit | Deduction + tax-free growth + tax-free withdrawal |
| Best investments | Broad market ETFs (XEQT, VEQT) or GICs |
| If no home purchase | Transfers to RRSP without using RRSP room |
| **Estimated 2024 savings** | **$1,600-2,400** |

## TFSA Strategy (Priority 2)

| Parameter | Value |
|-----------|-------|
| CC's estimated room | ~$31,500-38,500 (check CRA My Account) |
| 2024 annual limit | $7,000 |
| Qualified investments | Stocks, ETFs, bonds, GICs, crypto ETFs (BTCC, ETHH) |
| NOT qualified | Direct cryptocurrency |
| **WARNING** | CRA audits excessive TFSA trading — buy and hold only |
| Best use | Highest-return assets (crypto ETFs, growth stocks) |

## RRSP Strategy (Priority 3)

| Parameter | Value |
|-----------|-------|
| 2024 limit | 18% of 2023 earned income (max $31,560) |
| Strategy | Save room for higher-income years |
| HBP withdrawal | Up to $60,000 tax-free for first home |
| Best use at current income | Minimal — FHSA and TFSA first |

## Tax-Loss Harvesting (Q4 Automation)

```python
from finance.tax import CryptoTaxCalculator

calc = CryptoTaxCalculator()
opportunities = calc.suggest_tax_loss_harvesting(
    positions=[
        {"symbol": "BTC", "quantity": 0.01, "current_price": 50000, "average_cost": 55000},
        {"symbol": "ETH", "quantity": 0.5, "current_price": 2800, "average_cost": 3200},
    ],
    marginal_rate=0.2965,  # CC's estimated marginal rate
)
# Returns: list of HarvestOpportunity sorted by tax benefit
```

**Rules:**
- Sell losing positions before December 31
- Wait 31 days before rebuying same crypto (superficial loss rule)
- Can immediately buy DIFFERENT crypto (BTC→ETH swap is fine)
- Offset against capital gains or reduce business income

## Incorporation Decision Tree

```
IF oasis_annual_revenue_cad > 80,000
   AND revenue_consistent_for_3_months:

   → INCORPORATE as CCPC (Canadian-Controlled Private Corporation)
   → SBD rate: ~12.2% on first $500K (vs ~24% personal)
   → Tax deferral: retain earnings in corp at 12.2%
   → Lifetime Capital Gains Exemption: $1,250,000 on share sale (updated June 2024)
   → Cost: ~$1,500-2,000 incorporation + ~$2,500/year compliance

ELSE:
   → Stay sole proprietor (simpler, lower compliance cost)
   → Re-evaluate quarterly
```

## Account Placement Optimization

```python
from finance.tax import CryptoTaxCalculator

calc = CryptoTaxCalculator()
strategy = calc.optimize_account_placement(
    holdings=[
        {"symbol": "BTCC", "asset_class": "Crypto", "value_cad": 5000, "expected_return": 0.40},
        {"symbol": "XEQT", "asset_class": "US Stocks", "value_cad": 10000, "expected_return": 0.10},
    ],
    tfsa_room_available=31500,
    has_fhsa=True,
)
# Returns: AccountStrategy with optimal placement per account type
```
