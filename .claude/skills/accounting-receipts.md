---
description: "Receipt ingestion, T2125 expense categorization, crypto ACB tracking, bookkeeping. Use for any accounting, receipt, or expense question."
---
# Atlas Accounting & Receipts Skill

## When to activate
Any question about: receipts, expenses, categorize, deduction, T2125, bookkeeping, invoice, cost, write-off, business expense, home office, automobile, CCA, depreciation.

## Quick Commands
```bash
python main.py receipts --since 2026-01-01  # Pull Gmail receipts → categorized CSV
python main.py crypto-acb                    # CRA-compliant weighted-average ACB report
```

## Telegram Commands
- `/receipts` — sync Gmail receipts from `conaugh@oasisai.work`

## Python Engines
- `cfo/gmail_receipts.py` — IMAP receipt puller, Gmail label auto-discovery, amount parsing, category extraction, CSV export
- `cfo/crypto_acb.py` — weighted-average ACB, superficial loss detection, T5008 export

## Skill Playbooks
- `skills/accounting-advisor/SKILL.md` — T2125, T4, Schedule 3, deduction finder
- `skills/cash-flow-invoicing/SKILL.md` — invoice tracking, AR, cash flow forecasting
- `skills/crypto-acb-tracking/SKILL.md` — CRA ACB rules, exchange imports

## Knowledge Base
- `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` — 30+ deductions with ITA references
- `docs/ATLAS_AUTOMOBILE_EXPENSE_GUIDE.md` — vehicle deductions, logbook rules
- `docs/ATLAS_CCA_DEPRECIATION_GUIDE.md` — Capital Cost Allowance classes
- `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` — recordkeeping best practices
- `docs/ATLAS_AI_SAAS_TAX_GUIDE.md` — SaaS-specific deductions
- `docs/ATLAS_FINANCIAL_STATEMENTS_GUIDE.md` — financial statement preparation

## Data Files
- `data/receipts_cache.json` — cached Gmail receipt data
- `data/crypto_trades.csv` — historical crypto trades for ACB

## Gmail Setup
- Email: `conaugh@oasisai.work` (Google Workspace, app password in `.env`)
- Labels: `Receipts/<year>/<category>` — auto-discovered

## Rules
- Receipts must be categorized per CRA-accepted T2125 expense categories
- Keep original receipt data — never discard raw amounts
- Crypto ACB must use weighted-average method (CRA requirement for non-professional traders)
- All CSV exports must be audit-ready — CRA expects 6-year retention
