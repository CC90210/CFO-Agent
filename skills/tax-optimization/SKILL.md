---
name: tax-optimization
description: >
  25-strategy Canadian tax optimization: registered accounts (TFSA, RRSP, FHSA),
  tax-loss harvesting, incorporation planning, OpCo/HoldCo, SR&ED credits,
  offshore/LLC analysis, CPA-grade elite strategies, FIRE planning.
triggers: [TFSA, RRSP, FHSA, tax-loss, harvest, incorporate, incorporation, registered account, contribution room, HBP, LCGE, OpCo, HoldCo, SR&ED, SRED, IPP, RCA, CDA, COLI, family trust, Smith Manoeuvre, PSB, loss carryback, GAAR, FAPI, offshore, LLC, tonnage tax, shipping tax, flow-through, estate freeze, departure tax, FIRE]
tier: core
dependencies: [accounting-advisor]
---

# Tax Optimization — 25-Strategy Canadian Playbook

> The full tax optimization arsenal. Covers every strategy from basic registered accounts
> to CPA-grade elite structures. All strategies reference `docs/ATLAS_TAX_STRATEGY.md` (1,663 lines).

## Strategy Index by Section

### Sections 1-12: Core Domestic Strategies
| # | Strategy | ITA Ref | NOW/FUTURE | Est. Savings |
|---|----------|---------|-----------|-------------|
| 1 | GST/HST Voluntary Registration (ITC Recovery) | Excise Tax Act | NOW | $400-800/yr |
| 2 | FHSA Contribution Deduction Timing | s.146.6 | NOW | $768 one-time |
| 3 | Medical Expense 12-Month Timing | s.118.2 | NOW | $200-500/yr |
| 4 | Capital Gains Reserve (5-year spread) | s.40(1)(a)(iii) | FUTURE | Variable |
| 5 | LCGE ($1.25M tax-free) | s.110.6 | FUTURE | Up to $334,375 |
| 6 | Canadian Entrepreneurs' Incentive | Budget 2024 | FUTURE | Up to $2M at 33% |
| 7 | Prescribed Rate Loan (income splitting) | s.74.5(2) | FUTURE | Variable |
| 8 | CPP Self-Employed Optimization | CPP Act s.10 | NOW | $541/yr |
| 9 | CCA Immediate Expensing | Reg.1104(3.2) | NOW | $200-1,000/yr |
| 10 | Convention Expense Deduction | s.20(10) | NOW | $200-500/yr |
| 11 | CRA Voluntary Disclosure | N/A | Safety net | Penalty avoidance |
| 12 | Audit-Proofing | N/A | NOW | Risk reduction |

### Section 13: Shipping & Tonnage Tax
| # | Strategy | NOW/FUTURE | Notes |
|---|----------|-----------|-------|
| 13 | Shipping/Tonnage Tax Structures | FUTURE ($1M+) | Canada has NO tonnage tax. ETFs only for sector exposure. |

### Section 14: LLC, Trust & Tax Haven Structures
| # | Strategy | NOW/FUTURE | Key Rule |
|---|----------|-----------|---------|
| 14 | Wyoming/Delaware/NM LLC | Operational only | CRA treats as foreign corp — FAPI applies |
| 14 | Nevis LLC / Cook Islands Trust | FUTURE ($500K+) | Asset protection, not tax savings |
| 14 | Cayman/BVI/Singapore/Dubai | FUTURE ($1M+) | Most are BS for Canadian residents |
| 14 | GAAR (s.245) | ALWAYS | Nuclear anti-avoidance — kills paper structures |

### Section 15: Elite CPA-Grade Domestic Strategies
| # | Strategy | ITA Ref | NOW/FUTURE | Est. Savings |
|---|----------|---------|-----------|-------------|
| 13 | Individual Pension Plan (IPP) | Reg.8503-8516 | FUTURE (age 40+) | $1K-5K/yr |
| 14 | Retirement Compensation (RCA) | s.248(1) | FUTURE ($200K+) | Variable |
| 15 | OpCo/HoldCo Structure | s.186, s.55, s.112 | FUTURE ($150K+) | $5K-20K/yr |
| 16 | Capital Dividend Account (CDA) | s.89(1), s.83(2) | FUTURE (inc.) | Tax-free extraction |
| 17 | Corporate Life Insurance (COLI) | s.148 | FUTURE (inc.) | $100K-500K lifetime |
| 18 | Family Trust (Inter Vivos) | s.104, s.74.1-74.5 | FUTURE (family) | $10K-50K/yr |
| 19 | SR&ED Tax Credits | s.37, s.127(5) | **NOW (partial)** | $3K-25K/yr |
| 20 | Flow-Through Mining Shares | s.66.1, s.66.2 | NOW (marginal) | 25-30% of invested |
| 21 | Salary vs Dividend Optimization | s.82, s.121 | FUTURE (inc.) | $2K-8K/yr |
| 22 | Smith Manoeuvre | s.20(1)(c) | FUTURE (homeowner) | $45K-60K/25yr |
| 23 | PSB Trap Avoidance | s.125(7) | **NOW** | Avoids $5K-20K penalty |
| 24 | Loss Carryback/Forward | s.111(1) | **NOW** | Depends on losses |
| 25 | TFSA Aggressive Strategies | s.146.2, s.207.01 | **NOW (conservative)** | Tax-free growth |

## Registered Account Priority

```
FHSA (#1) → TFSA (#2) → RRSP (#3)

Why this order:
- FHSA: Tax deduction NOW + tax-free growth + tax-free withdrawal for home = triple benefit
- TFSA: Tax-free growth forever, no deduction but most flexible
- RRSP: Tax deduction now, taxed on withdrawal — save room for higher-income years
```

## CC's Priority Roadmap (Age 22, ~$49K)

**NOW:** Strategies 1-12 + SR&ED documentation + PSB avoidance + loss carryback
**$80K+:** Incorporate → 12.2% corp rate, SR&ED 35% refundable, salary/dividend mix
**$150K+:** OpCo/HoldCo, COLI, flow-through shares
**$200K+:** RCA, full salary/dividend optimization
**$500K+:** Revisit offshore (only with real substance)

## Decision Trees

### Incorporation Trigger
```
IF oasis_annual_revenue_cad > 80,000
   AND revenue_consistent_for_3_months:
   → INCORPORATE as CCPC
   → SBD rate: ~12.2% on first $500K
   → Unlock: SR&ED 35%, CDA, COLI, salary/dividend optimization
```

### Offshore Structure Decision
```
IF income < $500K AND no foreign operations:
   → NO offshore structures (compliance cost exceeds benefit)
   → US LLC ONLY for operational necessity (US clients, payment processing)

IF income >= $500K AND genuine foreign business:
   → Consider Singapore/Dubai with REAL substance (office, employees)
   → Engage international tax counsel ($10K+/year)
```

## Complete Document Library (18 docs)

| Doc | Triggers | Location |
|-----|----------|----------|
| **Core Playbook** | Any tax question | `docs/ATLAS_TAX_STRATEGY.md` |
| **CRA Crypto Intel** | CRA, audit, crypto tax, CARF | `docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md` |
| **DeFi Tax Guide** | Staking, LP, yield farming, NFT, bridge, wrapping, DAO, airdrop | `docs/ATLAS_DEFI_TAX_GUIDE.md` |
| **Incorporation** | RDTOH, GRIP, shareholder loan, estate freeze, purification | `docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md` |
| **Real Estate** | PRE, rental, flipping, REIT, LTT, HST, Smith Manoeuvre | `docs/ATLAS_REAL_ESTATE_TAX_STRATEGY.md` |
| **Treaties & FIRE** | Treaty, departure tax, FIRE, OAS, GIS, dividend arbitrage | `docs/ATLAS_TREATY_FIRE_STRATEGY.md` |
| **Wealth Playbook** | Books, Buy/Borrow/Die, Thiel, Buffett, wealth building | `docs/ATLAS_WEALTH_PLAYBOOK.md` |
| **Business Structures** | Entity, LLC, incorporation process, banking, international | `docs/ATLAS_BUSINESS_STRUCTURES.md` |
| **Deductions Masterlist** | Obscure deductions, OIDMTC, credits, tax calendar | `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` |
| **CRA Audit Defense** | Audit, objection, Tax Court, collections, rights | `docs/ATLAS_CRA_AUDIT_DEFENSE.md` |
| **Insurance & Estate** | Life insurance, COLI, estate, probate, asset protection | `docs/ATLAS_INSURANCE_ESTATE_PROTECTION.md` |
| **Government Grants** | Grant, Futurpreneur, IRAP, OIDMTC, funding, subsidy | `docs/ATLAS_GOVERNMENT_GRANTS.md` |
| **Pension & Retirement** | CPP, OAS, GIS, RRIF, pension splitting, meltdown, income layering | `docs/ATLAS_PENSION_RETIREMENT_GUIDE.md` |
| **AI/SaaS Tax** | SaaS revenue, SR&ED AI, DST, IP, cloud credits, contractor | `docs/ATLAS_AI_SAAS_TAX_GUIDE.md` |
| **Alternative Investments** | Accredited investor, VC, angel, MIC, flow-through, LSVCC, farmland | `docs/ATLAS_ALTERNATIVE_INVESTMENTS.md` |
| **Debt & Leverage** | OSAP, Smith Manoeuvre, interest deductibility, margin, CSBFP, credit | `docs/ATLAS_DEBT_LEVERAGE_STRATEGY.md` |
| **Bookkeeping Systems** | Chart of accounts, T2125, Wave, QBO, receipts, monthly close | `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` |
| **Wealth Psychology** | Cognitive bias, decision framework, behavioral finance, compounding | `docs/ATLAS_WEALTH_PSYCHOLOGY.md` |

## Code Integration
- **Tax calculator:** `finance/tax.py`
- **Accounting skill:** `skills/accounting-advisor/SKILL.md`
