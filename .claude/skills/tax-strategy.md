---
description: "CRA tax optimization, quarterly review, ACB tracking, tax-loss harvesting, RRSP/TFSA/FHSA strategy. Use for any tax or accounting question."
---
# Atlas Tax & Accounting

## Quick Commands
```bash
# Quarterly tax review
python -c "from skills.quarterly_tax_review import run; run()"

# Tax optimization scan (25 strategies)
python -c "from skills.tax_optimization import run; run()"

# Crypto ACB tracking
python -c "from skills.crypto_acb_tracking import run; run()"

# Tax-loss harvesting scan
python -c "from skills.tax_loss_harvesting import run; run()"
```

## Knowledge Base (80,000+ lines)
- `docs/ATLAS_TAX_STRATEGY.md` — Master tax playbook
- `docs/ATLAS_CRYPTO_TAX.md` — Crypto-specific (ACB, staking, CARF 2026)
- `docs/ATLAS_INTERNATIONAL_TAX.md` — Cross-border (94+ treaty network)
- `docs/ATLAS_TRUST_TAXATION_PLANNING.md` — Trust structures
- `brain/TAX_PLAYBOOK_INDEX.md` — Quick reference index

## Rules
- All calculations: CRA-accurate (ITA section references included)
- Never round tax numbers — exact cents matter
- Always cite the relevant ITA section for tax advice
- CC is in Ontario — provincial rates apply