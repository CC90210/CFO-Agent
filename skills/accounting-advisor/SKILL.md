---
name: accounting-advisor
description: >
  Full-service Canadian accounting and tax advisory. CRA filing preparation,
  T2125 self-employment, Schedule 3 capital gains, business deductions,
  home office calculations. Replaces a human accountant for CC's tax filing.
triggers: [tax, accounting, CRA, T2125, T4, deduction, filing, accountant, T1, Schedule 3, NETFILE]
tier: core
dependencies: []
---

# Accounting Advisor — CRA Tax Filing & Business Deductions

> Atlas's accounting brain. Used when CC needs tax calculations, filing guidance,
> deduction identification, or CRA compliance checks. References docs/ATLAS_TAX_STRATEGY.md
> for the full playbook.

## Overview

Atlas replaces a human accountant for CC's tax filing by:
1. Calculating capital gains/losses from Kraken trade history (ACB method)
2. Identifying all eligible business deductions (OASIS + DJ income)
3. Preparing T2125, Schedule 3, and ON-BEN data
4. Optimizing registered account contributions (FHSA > RRSP > TFSA)
5. Flagging tax-loss harvesting opportunities before year-end

## Tool Routing

| Operation | Module | Method |
|-----------|--------|--------|
| Capital gains calculation | `finance/tax.py` | `CryptoTaxCalculator.calculate_capital_gains_tax()` |
| Tax report generation | `finance/tax.py` | `CryptoTaxCalculator.generate_tax_report()` |
| Tax-loss harvesting | `finance/tax.py` | `CryptoTaxCalculator.suggest_tax_loss_harvesting()` |
| Quarterly estimates | `finance/tax.py` | `CryptoTaxCalculator.estimate_quarterly_taxes()` |
| Account placement | `finance/tax.py` | `CryptoTaxCalculator.optimize_account_placement()` |
| Deduction finder | `finance/tax.py` | `CryptoTaxCalculator.deduction_finder()` |

## Process — Filing CC's Taxes

### Step 1: Gather Documents
- T4 from Nicky's Donuts (employer provides by Feb 28)
- Kraken transaction history CSV (full 2024)
- OASIS invoices and payment records
- DJ gig payment records
- Rent receipts (12 months — needed for Ontario credits)
- Utility bills, internet bills, phone bills
- Home office measurements (workspace sq ft / total sq ft)
- FHSA/RRSP contribution receipts
- Equipment purchase receipts

### Step 2: Calculate Crypto Tax
```python
from finance.tax import CryptoTaxCalculator
calc = CryptoTaxCalculator()
report = calc.generate_tax_report(trades, 2024)
# report.summary → TaxSummary (proceeds, ACB, gains, losses, tax owing)
# report.trade_log → itemized dispositions
# report.schedule3_lines → Schedule 3 data
# report.t5008_rows → T5008 securities transaction rows
```

### Step 3: Identify Deductions
```python
deductions = calc.deduction_finder(business_expenses)
# Returns: list of Deduction(description, amount, cra_reference, confidence)
```

### Step 4: Prepare T2125 (Business Income)
- Revenue: OASIS invoices + DJ gig payments
- Expenses: software, hosting, internet, phone, home office, equipment
- Net business income = Revenue - Expenses
- CPP self-employment = 11.9% of net income ($3,500-$68,500)

### Step 5: File via NETFILE
- Use Wealthsimple Tax (free, handles T2125 + Schedule 3)
- Enter T4, T2125, Schedule 3, ON-BEN
- Review and submit electronically
- Pay any balance by April 30

## Key Tax Rules (Quick Reference)

| Rule | Details |
|------|---------|
| Capital gains inclusion | 50% (2024 — 66.67% over $250K deferred) |
| Self-employed CPP | 11.9% both portions ($3,500-$68,500) |
| Home office | Detailed method: workspace% x eligible expenses |
| Crypto ACB | Weighted average method (NOT FIFO) |
| Superficial loss | 30 days before/after — same asset repurchase denied |
| Filing deadline (self-employed) | June 15 |
| Payment deadline | April 30 |
| FHSA annual limit | $8,000 ($16,000 with carryforward) |
| TFSA 2024 limit | $7,000 |
| CCA immediate expensing | Up to $1.5M for sole proprietors |

## Integration

- **Tax Strategy Document:** `docs/ATLAS_TAX_STRATEGY.md`
- **Tax Calculator Code:** `finance/tax.py`
- **Trade Database:** `trading_agent.db` (SQLAlchemy — all trades logged)
- **Kraken API:** Export via CCXT or Kraken CSV download
