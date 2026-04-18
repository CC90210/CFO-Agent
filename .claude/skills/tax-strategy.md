---
description: "CRA tax optimization, quarterly review, ACB tracking, tax-loss harvesting, RRSP/TFSA/FHSA strategy, departure tax, Crown Dependencies, CCPC incorporation triggers. Use for any tax or accounting question."
---
# Atlas Tax & Accounting Skill

## When to activate
Any question about: taxes, CRA, deductions, T2125, T4, Schedule 3, capital gains, ACB, crypto tax, incorporation, CCPC, departure tax, TFSA, RRSP, FHSA, HST/GST, installments, tax-loss harvesting, SR&ED, TOSI, estate freeze, trust taxation.

## Quick Commands
```bash
python main.py taxes              # Quarterly tax reserve check
python main.py crypto-acb         # CRA-compliant weighted-average ACB report
```

## Skill Playbooks (read these for deep answers)
- `skills/tax-optimization/SKILL.md` — 25-strategy playbook
- `skills/quarterly-tax-review/SKILL.md` — quarterly income/deduction timing
- `skills/tax-loss-harvesting/SKILL.md` — systematic loss harvesting + superficial loss detection
- `skills/crypto-acb-tracking/SKILL.md` — CRA-compliant ACB, T5008 prep
- `skills/departure-tax-planning/SKILL.md` — s.128.1, Crown Dependencies, tie severing
- `skills/incorporation-readiness/SKILL.md` — $80K CCPC trigger, cost-benefit
- `skills/accounting-advisor/SKILL.md` — T2125, T4, deduction finder

## Knowledge Base (80,000+ lines in docs/)
- `docs/ATLAS_TAX_STRATEGY.md` — Master 25-strategy playbook
- `docs/ATLAS_CANADIAN_TAX_LOOPHOLES.md` — Obscure deductions, entity structures
- `docs/ATLAS_CRYPTO_TAX_ADVANCED.md` — Crypto ACB, DeFi, CARF 2026
- `docs/ATLAS_INTERNATIONAL_TAX_MASTERPLAN.md` — 19-jurisdiction comparison
- `docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md` — IoM/Jersey/Guernsey
- `docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md` — CCPC, SBC, integration
- `docs/ATLAS_TRUST_TAXATION_PLANNING.md` — Trust structures, 21-year rule
- `docs/ATLAS_TOSI_DEFENSE.md` — Income splitting rules
- `docs/ATLAS_INSTALLMENT_PAYMENTS.md` — CRA quarterly installments
- `docs/ATLAS_HST_REGISTRATION_GUIDE.md` — GST/HST registration, ITCs
- `brain/TAX_PLAYBOOK_INDEX.md` — Quick reference index for all 59+ docs

## Python Engines
- `finance/tax.py` — CRA-compliant tax calculator, federal + Ontario brackets, capital gains inclusion rate
- `cfo/crypto_acb.py` — Weighted-average ACB engine, superficial loss detection

## Rules
- All calculations: CRA-accurate (ITA section references required)
- Never round tax numbers — exact cents matter
- Always cite the relevant ITA section for tax advice
- CC is in Ontario — provincial rates apply (Quebec rates needed post-Montreal move)
- CC's 2025 return is FILED — do not suggest filing it
- CC's FHSA is OPENED — do not suggest opening it