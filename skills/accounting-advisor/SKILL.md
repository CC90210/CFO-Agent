---
name: accounting-advisor
description: >
  Full-service Canadian accounting and tax advisory. CRA filing preparation,
  T2125 self-employment, Schedule 3 capital gains, business deductions,
  home office calculations, crypto ACB tracking, corporate structuring (OpCo/HoldCo),
  SR&ED claims, estate planning. 25-strategy playbook. Replaces a human accountant.
triggers: [tax, accounting, CRA, T2125, T4, deduction, filing, accountant, T1, Schedule 3, NETFILE, ACB, capital gains, crypto tax, HST, ITC, dividend, salary, corporate, T1134, T1135, FAPI, transfer pricing]
tier: core
dependencies: []
---

# Accounting Advisor — CRA Tax Filing & Business Deductions

> Atlas's accounting brain. Used when CC needs tax calculations, filing guidance,
> deduction identification, or CRA compliance checks. References docs/ATLAS_TAX_STRATEGY.md
> (1,663 lines, 25 strategies) for the full playbook.

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

## Advanced Capabilities (Sections 13-15 of Tax Strategy)

| Capability | Triggers | Reference |
|-----------|----------|-----------|
| **Shipping/Tonnage Tax** | shipping, tonnage, maritime, flag of convenience | Section 13 |
| **LLC/Offshore Analysis** | LLC, Wyoming, Delaware, Nevis, FAPI, GAAR, offshore, tax haven | Section 14 |
| **IPP/RCA** | pension plan, retirement compensation, IPP, RCA | Strategy 13-14 |
| **OpCo/HoldCo** | holding company, operating company, dividend pipeline | Strategy 15 |
| **CDA** | capital dividend account, tax-free extraction | Strategy 16 |
| **COLI** | corporate life insurance, insured retirement | Strategy 17 |
| **Family Trust** | trust, income splitting, TOSI, estate freeze, 21-year rule | Strategy 18 |
| **SR&ED** | research credits, SR&ED, SRED, R&D, scientific research | Strategy 19 |
| **Flow-Through Shares** | mining shares, flow-through, exploration expense | Strategy 20 |
| **Salary/Dividend Mix** | salary vs dividend, integration, RDTOH, GRIP | Strategy 21 |
| **Smith Manoeuvre** | mortgage deductible, readvanceable, Smith | Strategy 22 |
| **PSB Trap** | personal services business, single client | Strategy 23 |
| **Loss Carry** | carryback, carryforward, ABIL, net capital loss | Strategy 24 |
| **TFSA Aggressive** | TFSA trading, private shares, CRA audit TFSA | Strategy 25 |

## Document Library (18 docs — route queries to the right doc)

| Document | Location | When to Use |
|----------|----------|-------------|
| **Core Tax Playbook** | `docs/ATLAS_TAX_STRATEGY.md` | 25 strategies, CC's profile, registered accounts, crypto, offshore, CPA-grade |
| **CRA Crypto Intel** | `docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md` | CRA audit triggers, exchange data orders, Tax Court cases, DeFi, CARF, penalties |
| **DeFi Tax Guide** | `docs/ATLAS_DEFI_TAX_GUIDE.md` | Staking, LP, yield farming, NFT, bridge, wrapping, DAO, airdrop, CARF, DeFi record-keeping |
| **Incorporation Strategies** | `docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md` | RDTOH, GRIP/LRIP, shareholder loans, salary doctrine, SBD grind, estate freeze, purification |
| **Real Estate Tax** | `docs/ATLAS_REAL_ESTATE_TAX_STRATEGY.md` | PRE, rental CCA, flipping rules, REITs, Smith Manoeuvre, LTT, HST, corporate RE |
| **Treaty & FIRE** | `docs/ATLAS_TREATY_FIRE_STRATEGY.md` | Treaty exploitation, departure tax, FIRE drawdown, OAS/GIS, dividend arbitrage |
| **Wealth Playbook** | `docs/ATLAS_WEALTH_PLAYBOOK.md` | Book strategies, Buy/Borrow/Die, Thiel TFSA play, Buffett structure |
| **Business Structures** | `docs/ATLAS_BUSINESS_STRUCTURES.md` | Entity types (CA/US/UK/SG/Dubai/Estonia), multi-entity architectures, banking |
| **Deductions Masterlist** | `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` | Every obscure deduction + Ontario credits + tax calendar |
| **CRA Audit Defense** | `docs/ATLAS_CRA_AUDIT_DEFENSE.md` | Audit process, rights, objections, Tax Court, collections, audit-proofing |
| **Insurance & Estate** | `docs/ATLAS_INSURANCE_ESTATE_PROTECTION.md` | COLI, disability, estate planning, probate avoidance, asset protection, crypto custody |
| **Government Grants** | `docs/ATLAS_GOVERNMENT_GRANTS.md` | Federal/Ontario grants, Futurpreneur, IRAP, OIDMTC, SR&ED filing, AI credits |
| **Pension & Retirement** | `docs/ATLAS_PENSION_RETIREMENT_GUIDE.md` | CPP timing, OAS clawback avoidance, GIS hidden wealth, RRSP meltdown, RRIF, pension splitting, income layering |
| **AI/SaaS Tax** | `docs/ATLAS_AI_SAAS_TAX_GUIDE.md` | SaaS revenue recognition, SR&ED for AI, DST, IP tax, cloud credits, contractor vs employee |
| **Alternative Investments** | `docs/ATLAS_ALTERNATIVE_INVESTMENTS.md` | Accredited investor, VC/angel, MIC, flow-through shares, LSVCC, farmland, crypto ETFs |
| **Debt & Leverage** | `docs/ATLAS_DEBT_LEVERAGE_STRATEGY.md` | OSAP RAP, interest deductibility s.20(1)(c), Smith Manoeuvre, margin, CSBFP, credit score |
| **Bookkeeping Systems** | `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` | Chart of accounts, T2125 mapping, software comparison, automation, monthly close, KPIs |
| **Wealth Psychology** | `docs/ATLAS_WEALTH_PSYCHOLOGY.md` | Cognitive biases, decision frameworks, behavioral finance, compounding advantage at 22 |

## Code Integration

- **Tax Calculator:** `finance/tax.py`
- **Trade Database:** `trading_agent.db` (SQLAlchemy — all trades logged)
- **Kraken API:** Export via CCXT or Kraken CSV download
- **Tax Optimization Skill:** `skills/tax-optimization/SKILL.md`
- **Financial Planning Skill:** `skills/financial-planning/SKILL.md`
