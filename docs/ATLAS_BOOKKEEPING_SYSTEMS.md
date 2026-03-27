# ATLAS Bookkeeping Systems & Financial Automation Guide

> The operational backbone that makes every Atlas tax strategy actually work.
> Without clean books, deductions get missed, HST filings are wrong, and CRA audits become nightmares.
> This document IS the bookkeeping system. Atlas follows this for all accounting operations.
> Atlas is CC's CFO. Bravo (Business-Empire-Agent) is the CEO. Different roles, complementary.

**Jurisdiction:** Canada (Ontario) | **Entity:** Sole Proprietor (OASIS AI Solutions) — transitioning to CCPC | **GST/HST:** Ontario (13% HST) | **Last updated:** 2026-03-27

**ITA References:** s.9 (business income), s.18 (limitations on deductions), s.20 (permitted deductions), s.67.1 (meals 50% rule), s.230 (record-keeping), Reg 1100-1107 (CCA classes and rates)

---

## Table of Contents

1. [Chart of Accounts (T2125-Aligned)](#section-1-chart-of-accounts-t2125-aligned)
2. [Accounting Software Comparison](#section-2-accounting-software-comparison)
3. [Bank Account Structure](#section-3-bank-account-structure)
4. [Receipt Management](#section-4-receipt-management)
5. [Automation Stack](#section-5-automation-stack)
6. [Monthly Close Routine](#section-6-monthly-close-routine)
7. [GST/HST Filing](#section-7-gsthst-filing)
8. [Payroll](#section-8-payroll)
9. [Year-End Procedures](#section-9-year-end-procedures)
10. [Financial Reporting](#section-10-financial-reporting)
11. [Crypto Bookkeeping](#section-11-crypto-bookkeeping)
12. [Appendix A — T2125 Line Map](#appendix-a-t2125-line-map)
13. [Appendix B — Key Deadlines](#appendix-b-key-deadlines)
14. [Appendix C — First-Week Setup Checklist](#appendix-c-first-week-setup-checklist)

---

## Section 1: Chart of Accounts (T2125-Aligned)

### 1.1 Account Numbering Convention

| Range | Category | Purpose |
|-------|----------|---------|
| 1000-1999 | Assets | What CC owns |
| 2000-2999 | Liabilities | What CC owes |
| 3000-3999 | Equity | Owner's stake |
| 4000-4999 | Revenue | Money in |
| 5000-5999 | Cost of Goods Sold | Direct costs |
| 6000-6999 | Operating Expenses | Maps to T2125 Part 4 |
| 7000-7999 | Other Income/Expense | FX gains, non-operating |

### 1.2 Asset Accounts

| Account | Name | Type | Notes |
|---------|------|------|-------|
| 1000 | RBC Personal Chequing | Current Asset | Personal — NEVER mix business transactions |
| 1010 | RBC Business Chequing | Current Asset | Primary CAD operating account |
| 1020 | Wise Business — CAD | Current Asset | CAD business balance |
| 1025 | Wise Business — USD | Current Asset | US client receipts |
| 1050 | Business Savings — HST Reserve | Current Asset | Segregated. This is NOT your money. |
| 1100 | Accounts Receivable | Current Asset | Outstanding client invoices |
| 1200 | Prepaid Expenses | Current Asset | Annual software paid in advance |
| 1300 | Crypto — BTC | Current Asset | FMV in CAD at reporting date |
| 1310 | Crypto — SOL | Current Asset | FMV in CAD at reporting date |
| 1320 | Crypto — ETH | Current Asset | FMV in CAD at reporting date |
| 1330 | Crypto — LTC | Current Asset | FMV in CAD at reporting date |
| 1340 | Crypto — ATOM | Current Asset | FMV in CAD at reporting date |
| 1390 | Crypto — Other | Current Asset | Any additional positions |
| 1500 | Computer Equipment | Fixed Asset | MacBook, monitors, peripherals — CCA Class 50 |
| 1510 | DJ Equipment | Fixed Asset | Controllers, speakers, lighting — CCA Class 8 |
| 1520 | Office Furniture | Fixed Asset | Desk, chair, monitor arms — CCA Class 8 |
| 1550 | Accumulated Depreciation — Equipment | Contra Asset | CCA claimed to date |

### 1.3 Liability Accounts

| Account | Name | Type | Notes |
|---------|------|------|-------|
| 2000 | Accounts Payable | Current Liability | Bills owed to vendors |
| 2100 | HST Collected | Current Liability | 13% Ontario HST on invoices. NOT your money. |
| 2110 | HST Paid on Purchases (ITC) | Current Asset | Input tax credits — offsets HST collected |
| 2120 | HST Payable (Net) | Current Liability | = 2100 minus 2110. Remit to CRA. |
| 2200 | Credit Card — Business | Current Liability | Business credit card balance |
| 2300 | OSAP Loan | Long-term Liability | Interest = non-refundable credit Line 31900 |
| 2400 | Income Tax Payable | Current Liability | Estimated income tax owing |
| 2410 | CPP Payable | Current Liability | Self-employed CPP both portions = 11.9% |

### 1.4 Equity Accounts

| Account | Name | Notes |
|---------|------|-------|
| 3000 | Owner's Equity | Opening balance |
| 3100 | Owner's Draws | Transfers to personal — NOT an expense |
| 3200 | Owner's Contributions | Capital injections — NOT revenue |
| 3300 | Retained Earnings | Accumulated profits — critical at incorporation |
| 3400 | Current Year Earnings | Revenue minus Expenses — auto-calculated |

Post-incorporation additions:

| Account | Name | Notes |
|---------|------|-------|
| 3500 | Common Shares | CCPC share capital |
| 3600 | Shareholder Loan — CC | Track every dollar. CRA scrutinizes s.15(2). Must repay within 1 year of corp fiscal year-end or it is income. |
| 2500 | Corporate Tax Payable | Federal 9% SBD + Ontario 3.2% = 12.2% on first $500K |
| 2510 | RDTOH Balance | Refundable dividend tax on hand |
| 2600 | Payroll Liabilities | CPP/EI/tax source deductions — remit by 15th |

### 1.5 Revenue Accounts (T2125 Part 3C — Line 8000)

| Account | Name | T2125 / CRA Reference | Notes |
|---------|------|----------------------|-------|
| 4100 | OASIS Consulting Revenue — CAD | Line 8000 | Primary AI automation services |
| 4110 | OASIS Consulting Revenue — USD | Line 8000 | US clients via Wise. Convert at BoC noon rate on invoice date. |
| 4200 | DJ Performance Income | Line 8000 (separate T2125) | Per-gig income. Industry code 711130. |
| 4300 | Crypto Trading Income — Business | Line 8000 | Only if deemed business income by CRA. 100% taxable. |
| 4310 | Crypto Trading Income — Capital | Schedule 3 | Capital gains — 50% inclusion. NOT on T2125. |
| 4400 | PropFlow Revenue | Line 8000 | When active |
| 4900 | Other Business Income | Line 8000 | Referral fees, affiliate commissions |

### 1.6 Cost of Goods Sold (Direct Costs — T2125 Part 3C)

| Account | Name | T2125 Reference | Notes |
|---------|------|-----------------|-------|
| 5010 | Subcontractor Costs | Line 8340 | Freelancers and contractors — issue T4A if >$500/year |
| 5020 | Direct Software/AI API — Client-billed | Line 8340 | OpenAI/Anthropic costs billed through to client |
| 5030 | Direct Cloud Hosting — Client Projects | Line 8340 | AWS, Vercel, Supabase on client infrastructure |

### 1.7 Operating Expense Accounts (T2125 Part 4)

Correct categorization here = direct deduction at tax time.

| Account | Name | T2125 Line | ITA Reference | Notes |
|---------|------|------------|---------------|-------|
| 6100 | Advertising & Promotion | **8521** | s.18(1)(a) | Google Ads, Meta Ads, website hosting, domain names, portfolio site, Canva |
| 6105 | Cloud & Hosting — Overhead | **8521** | s.18(1)(a) | AWS, Vercel, Supabase, n8n cloud not billed to client |
| 6110 | Meals & Entertainment | **8523** | s.67.1 ITA | **50% deductible only.** Client meals, networking. Keep receipt + attendees + business purpose. |
| 6120 | Bad Debts | **8590** | s.20(1)(p) | Uncollectable invoices. Must have been in revenue first. |
| 6130 | Insurance — Business | **8690** | s.18(1)(a) | E&O, liability, cyber insurance |
| 6140 | Interest & Bank Charges | **8710** | s.20(1)(c) | RBC fees, Wise fees, Stripe/PayPal processing fees, credit card interest on business purchases |
| 6150 | Office Expenses | **8810** | s.18(1)(a) | Printer ink, paper, small supplies under $500 |
| 6155 | Software Subscriptions | **8810** | s.18(1)(a) | Claude Pro, GitHub Copilot, Cursor, Notion, Figma — under $1,750/item |
| 6160 | Supplies | **8811** | s.18(1)(a) | USB drives, cables, items consumed in business |
| 6170 | Professional Fees — Legal | **8860** | s.18(1)(a) | Contract review, IP protection, incorporation |
| 6175 | Professional Fees — Accounting | **8860** | s.18(1)(a) | Tax prep, CPA consultation, bookkeeping software |
| 6180 | Management & Admin Fees | **8871** | s.18(1)(a) | Virtual assistant, admin subcontractors |
| 6185 | Subcontractor Payments | **8871** | s.18(1)(a) | Technical subs. Issue T4A if >$500/year per person. |
| 6190 | Rent — External | **8910** | s.18(1)(a) | Coworking space, studio rental |
| 6200 | Repairs & Maintenance | **8960** | s.18(1)(a) | Computer repairs, equipment maintenance |
| 6210 | Salaries & Wages | **8920** | s.18(1)(a) | Only when employees hired |
| 6220 | Travel — Transportation | **9200** | s.18(1)(h) | Flights, train, gas for business trips. NOT daily commute. |
| 6225 | Travel — Accommodation | **9200** | s.18(1)(h) | Hotels and accommodation for business trips |
| 6230 | Telephone — Business Portion | **9220** | s.18(1)(a) | Cell phone business-use % only |
| 6235 | Internet — Business Portion | **9220** | s.18(1)(a) | Internet business-use % only |
| 6240 | Utilities | **9224** | s.18(1)(a) | Heat, water, electricity — business-use % |
| 6250 | Motor Vehicle Expenses | **9281** | s.18(1)(h) | Gas, insurance, maintenance, parking — business km / total km |
| 6260 | CCA — Computer Equipment (Class 50, 55%) | **9936** | Reg 1100, Sch II | Laptops, desktops, servers |
| 6265 | CCA — DJ Equipment (Class 8, 20%) | **9936** | Reg 1100, Sch II | Speakers, controllers, lighting |
| 6270 | CCA — Furniture & Fixtures (Class 8, 20%) | **9936** | Reg 1100, Sch II | Desk, chair, monitor stand |
| 6280 | Home Office Expenses | **T2125 Part 7 → Line 9945** | s.18(12) | Calculated on T2125 Part 7. Cannot create a loss. |
| 6290 | Training & Education | **9270** | s.18(1)(a) | Courses, books, conferences directly tied to OASIS services |
| 6320 | Crypto Exchange & Trading Fees | **8710** | s.20(1)(c) | Kraken fees, OANDA spreads — deducted against gains |
| 6900 | Other Business Expenses | **9270** | s.18(1)(a) | Anything not listed above. Always add memo. |

### 1.8 Multi-Business Sub-Account Convention

OASIS and DJ are separate business activities. CRA requires a separate T2125 per distinct activity. Use a prefix in memo fields (or sub-accounts) to distinguish:

```
OASIS:   all 6xxx accounts tagged [OAS]
DJ/Music: all 6xxx accounts tagged [DJ]
```

This maps cleanly to two T2125 forms at filing time.

---

## Section 2: Accounting Software Comparison

### 2.1 Feature Matrix

| Feature | Wave (Free) | QuickBooks Online ($20-50/mo) | Xero ($17-54/mo) | FreshBooks ($19-60/mo) | Hurdlr ($10/mo) |
|---------|------------|-------------------------------|------------------|------------------------|-----------------|
| **Monthly cost (CAD)** | $0 | $20-50 | $17-54 | $19-60 | ~$13 |
| **HST/GST NETFILE to CRA** | No (manual) | Yes — built-in | No (manual) | No (manual) | No |
| **T2125 line mapping** | Manual | Built-in reports | Custom config | Manual | Manual |
| **Bank feeds — RBC** | Yes | Yes (Plaid) | Yes | Yes | Yes |
| **Bank feeds — Wise** | Inconsistent | Yes (native) | Yes (native) | Yes | Limited |
| **Multi-currency (USD/CAD)** | Basic | Good | Excellent | Good | No |
| **Receipt scanning** | Mobile app | HubDoc + app | Mobile + HubDoc | Mobile app | Core feature |
| **Payroll (Canadian)** | Add-on $20+ | Add-on $20+ | Wagepoint add-on | No | No |
| **T4A generation** | No | Yes | Yes | No | No |
| **Invoicing quality** | Good | Good | Good | Excellent | Basic |
| **Corp scalability** | Poor | Excellent | Good | Poor | No |
| **API / Zapier** | None | 750+ integrations | 1,000+ integrations | Limited | Limited |
| **CPA familiarity (Canada)** | Medium | Highest | Medium | Medium | Low |
| **Best for** | Sole prop <$30K | Growth + CCPC | Multi-currency | Invoicing-first | Mobile only |

### 2.2 Atlas Recommendation

**Phase 1 — Now (Sole Proprietor, <$50K revenue):**
Use **Wave** (free). Gets the basics right at zero cost. Self-serve. Canadian-native.

**Phase 2 — Growth ($30K-$80K):**
Migrate to **QuickBooks Online Simple Start** (~$20/mo CAD). HST NETFILE alone is worth it. T2125 reporting, CPA-ready files, HubDoc included for receipts.

**Phase 3 — Post-Incorporation ($80K+ CCPC):**
Stay on **QuickBooks Online Plus** (~$50/mo) + **Wagepoint** for payroll ($20/mo base). QBO scales cleanly — no migration needed. Add HoldCo as second company file when structure warrants it.

---

## Section 3: Bank Account Structure

### 3.1 Optimal Setup

```
CC's Business Banking Stack (Sole Proprietor)

PERSONAL
  RBC Personal Chequing [1000]
    - T4 employment income (Nicky's)
    - Owner's draws from business
    - Personal expenses

BUSINESS
  RBC Business Chequing [1010]  <-- Primary operating account
    - ALL OASIS and DJ revenue deposits
    - ALL business expense payments
    - HST collected (then transferred to reserve within 24 hours)

  Wise Business — CAD/USD [1020/1025]
    - US client invoice payments land here
    - USD held for USD-denominated expenses
    - Convert to CAD at Wise mid-market rate (~0.4% fee)

  EQ Bank Business Savings [1050]  <-- Tax reserve only
    - 13% of every invoice = HST reserve
    - 25-30% of net income = income tax reserve
    - This account ONLY pays CRA. Never spend on operations.

REGISTERED ACCOUNTS (Personal)
  FHSA  - Open immediately. $8,000/year. Deductible + tax-free.
  TFSA  - Maximize annually. Tax-free growth.
  RRSP  - Fund after FHSA. Deductible contributions build CPP room.
```

### 3.2 Separation Rules — CRA Audit Defense

Commingling personal and business funds is the single most common audit trigger for sole proprietors.

| Rule | Why It Matters |
|------|----------------|
| All business income deposits to business account only | Deposits to personal = assumed unreported income |
| All business expenses paid from business account or business card only | Mixed accounts make every expense a disputed deduction |
| Owner draws documented as separate transfers | Draws are not deductible — must be clearly distinguished |
| Capital injections logged as "Owner's Contribution" | Undocumented deposits look like income to CRA |
| No personal expenses ever paid from business account | Personal use = taxable benefit — must be reversed |

**Practical rule:** If CRA audits, they will review 12-24 months of bank statements. Every unexplained deposit into a mixed account is assumed to be taxable income until you prove otherwise. A dedicated business account eliminates this risk entirely.

### 3.3 HST Reserve Protocol

```
Client pays invoice → Deposit to RBC Business Chequing
Within 24 hours →
  Transfer (invoice amount × 13/113) to EQ Bank Savings [HST reserve]
  This is NOT your money. Do not spend it.

End of quarter →
  Net HST owing = HST Collected - ITCs
  Remit net amount to CRA
  Return excess to operating account (if ITCs > collected — rare)
```

### 3.4 Post-Incorporation Structure

```
PERSONAL (CC individual)
  Personal Chequing
    - Salary from OASIS Inc. (T4 slip)
    - Dividends from OASIS Inc. (T5 slip)
  TFSA, FHSA, RRSP

CORPORATE (OASIS AI Solutions Inc.)
  Corporate Chequing (new account — corporation is a separate legal entity)
    - All business revenue
    - All business expenses
    - Salary to CC
  Corporate Savings
    - HST reserve
    - Corporate tax reserve (12.2% of net profit)
    - 3-month operating emergency fund
  Corporate Investment (when retained earnings accumulate)
    - Passive investment of surplus retained earnings
    - Watch: passive income >$50K/year grinds down SBD limit (s.125(5.1) ITA)
```

**Shareholder loan rule (s.15(2) ITA):** Every dollar that moves between CC personally and OASIS Inc. must be tracked in Account 3600 (Shareholder Loan). Loans not repaid within one year of the corporation's fiscal year-end are deemed income. CRA audits this account aggressively.

---

## Section 4: Receipt Management

### 4.1 CRA Retention Requirement

**s.230(1) ITA:** Every person carrying on a business must keep records and books of account at their place of business or residence in Canada, in the prescribed form, for **6 years from the end of the tax year** to which they relate.

Practical example: A receipt dated March 15, 2026 relates to the 2026 tax year (ending December 31, 2026). Retain until at least January 1, 2033.

**Extended retention:**
- If CRA reassesses or you file a Notice of Objection: retain until resolution + 6 years (s.230(4))
- CCA (capital property) records: retain for 6 years after the year the asset is disposed of, not the year of acquisition
- Legal documents (contracts, incorporation): retain indefinitely or 6 years after the relationship ends

### 4.2 What Constitutes a Valid Receipt

CRA standards vary by transaction size:

| Transaction Value | Required Documentation |
|-------------------|----------------------|
| Under $30 | Receipt not required — bank statement is sufficient |
| $30 to $149.99 | Simplified receipt: vendor name, date, total, HST amount |
| $150 and over | Full receipt: vendor name, address, HST registration number, date, itemized description, subtotal, HST separately shown, total |
| Meals/entertainment | Any amount: add notation of attendees, their relationship to business, and specific business purpose discussed |
| Vehicle expenses | Contemporaneous mileage log required: date, destination, business purpose, km driven, odometer at year-start and year-end |

### 4.3 Digital Receipt Tools

CRA accepts digital copies of receipts (CRA IC05-1R1) provided they are legible, complete, and accessible for the full 6-year period. Original paper receipts can be destroyed once compliant digital copies exist.

| Tool | Cost | Key Feature | Integration |
|------|------|-------------|-------------|
| **Dext** (formerly Receipt Bank) | ~$24/mo CAD | Best OCR extraction — vendor, amount, date, HST auto-extracted | QBO, Xero, Wave |
| **HubDoc** | Free with QBO | Fetches bills from vendor portals automatically + receipt capture | QBO, Xero |
| **Wave Receipts** | Free (within Wave) | Mobile scan + auto-categorize | Wave |
| **FreshBooks mobile** | Included | Snap and attach to expense entry | FreshBooks |
| **Google Drive** | Free tier | Manual filing — no extraction | Manual export |

**Atlas recommendation:** HubDoc if using QuickBooks (zero additional cost). Dext if on Wave or Xero — the $24/mo pays for itself by catching one missed deduction.

### 4.4 File Naming Convention

```
/Receipts/[Year]/[Quarter]/[Category]/
  Naming format: YYYY-MM-DD_Vendor_Description_$Amount_CAD.pdf

Examples:
  2026-03-15_Google-Ads_March-campaign_$245.00_CAD.pdf
  2026-03-01_OpenAI-API_February-usage_$89.50_USD.pdf
  2026-03-20_Sweetwater_DJ-headphones_$312.00_CAD.pdf
```

### 4.5 Backup Strategy — 3-2-1 Rule

| Copy | Location | Sync Frequency |
|------|----------|----------------|
| Primary | Google Drive (cloud) | Real-time |
| Secondary | Local hard drive or NAS | Weekly automatic |
| Tertiary | External drive stored offsite | Monthly or quarterly |

---

## Section 5: Automation Stack

### 5.1 Bank Feed Categorization Rules

Set these rules in accounting software once — they apply automatically going forward.

| Payee Keyword | Category | Account | T2125 Line |
|---------------|----------|---------|------------|
| GOOGLE ADS | Advertising | 6100 | 8521 |
| META / FACEBOOK | Advertising | 6100 | 8521 |
| OPENAI | AI API — Overhead | 6900 | 9270 |
| ANTHROPIC | AI API — Overhead | 6900 | 9270 |
| GITHUB | Software Subscriptions | 6155 | 8810 |
| NOTION | Software Subscriptions | 6155 | 8810 |
| AWS / AMAZON WEB | Cloud & Hosting | 6105 | 8521 |
| VERCEL | Cloud & Hosting | 6105 | 8521 |
| STRIPE FEE | Bank / Merchant Charges | 6140 | 8710 |
| WISE FEE | Bank Charges | 6140 | 8710 |
| BELL / ROGERS / TELUS | Telephone | 6230 | 9220 |
| UBER | Review manually | Varies | 9200 or personal |
| AMAZON.CA | Review manually | Varies | Too varied to auto-categorize |

### 5.2 Invoice Automation (Recurring Retainers)

Every retainer client should have a recurring invoice configured:

```
Frequency: Monthly, 1st of month
Auto-send: Yes
Payment terms: Net 15

Required fields on every invoice:
  - OASIS AI Solutions + CC's name and Collingwood address
  - HST registration number (mandatory once registered)
  - Sequential invoice number: OASIS-2026-001
  - Issue date and due date
  - Service description (specific — not just "consulting")
  - Subtotal, HST (13%), Total
  - Payment methods: Wise transfer, Interac e-Transfer

Automated follow-up sequence:
  Day 1:  Invoice sent
  Day 7:  Friendly payment reminder
  Day 15: Payment due reminder
  Day 30: Overdue notice
  Day 45: Final notice — escalate to personal follow-up
```

### 5.3 Zapier / Make Automation Flows

**Flow 1: Invoice paid → Bookkeeping + reserve transfer**
```
Trigger: Stripe/Wise webhook — payment received
Action 1: Create income transaction in accounting software
Action 2: Calculate 13% HST portion → flag for transfer to reserve
Action 3: Send Telegram notification to CC (via Atlas Telegram bot)
```

**Flow 2: Receipt email → Digital filing**
```
Trigger: Gmail label "Receipts" applied to email
Action 1: Forward attachment to Dext/HubDoc email inbox
Action 2: Copy to Google Drive /Receipts/[current year]/[quarter]/
```

**Flow 3: Monthly HST summary alert**
```
Trigger: 1st of each month
Action 1: Pull HST Collected balance from accounting software
Action 2: Pull ITC balance
Action 3: Send net HST summary to CC via Telegram
```

### 5.4 Crypto Transaction Tracking

Connect Kraken API (read-only key only — never write access) to Koinly:

1. Koinly fetches all trades, transfers, fees automatically
2. Tag: trade / transfer / staking reward / airdrop / fee
3. Koinly calculates ACB using CRA weighted average method
4. Koinly detects superficial loss rule violations
5. Export CRA-ready Schedule 3 summary at tax time

**Koinly is the source of truth for crypto tax. Atlas `finance/tax.py` is the verification layer. They must agree before filing.**

---

## Section 6: Monthly Close Routine

### 6.1 Month-End Checklist

Complete by the 5th of the following month.

```
MONTH-END CLOSE CHECKLIST
Month: _____________ Year: _____________

STEP 1 — BANK RECONCILIATION
[ ] Download RBC Business Chequing statement (month-end)
[ ] Match every transaction to accounting software entry
[ ] Identify and resolve any unmatched transactions
[ ] Confirm closing balance matches accounting software to the dollar
[ ] Reconcile Wise Business (CAD) — match statement to software
[ ] Reconcile Wise Business (USD) — convert to CAD at month-end BoC rate
[ ] Reconcile business credit card statement
[ ] Confirm HST reserve account balance matches accumulated HST collected

STEP 2 — UNCATEGORIZED TRANSACTIONS
[ ] Open "Uncategorized" / "For Review" queue in accounting software
[ ] Categorize every transaction — zero uncategorized remaining
[ ] Flag any transactions over $500 — confirm correct account
[ ] Verify all meals have: attendees, relationship, business purpose (memo field)
[ ] Confirm all personal expenses are excluded or coded as Owner's Draw

STEP 3 — ACCOUNTS RECEIVABLE REVIEW
[ ] Run A/R aging report
[ ] Follow up on all invoices 15+ days overdue
[ ] Send final notice on invoices 45+ days overdue
[ ] Write off any invoices 90+ days overdue as bad debt (Account 6120, s.20(1)(p) ITA)
[ ] Confirm all payments received are matched to their invoices (no unapplied credits)

STEP 4 — HST RECONCILIATION
[ ] Total HST collected this month (Account 2100)
[ ] Total ITCs claimed this month (Account 2110)
[ ] Net HST owing = 2100 minus 2110
[ ] Update quarterly HST tracker → confirm reserve account balance adequate

STEP 5 — EXPENSE REVIEW
[ ] Home office: confirm proration percentage applied to all home-related expenses
[ ] Telephone/internet: confirm business-use percentage applied
[ ] Motor vehicle (if claimed): confirm km log updated for the month
[ ] Meals/entertainment: confirm 50% rule applied in all entries
[ ] Review software subscriptions — any unused tools to cancel?

STEP 6 — CRYPTO (if active trading month)
[ ] Record all trades at CAD FMV on trade date
[ ] Update ACB ledger in Koinly
[ ] Record all exchange fees paid
[ ] Reconcile Kraken balance to crypto asset accounts in bookkeeping software

STEP 7 — REPORTING
[ ] Generate monthly P&L — save as PDF
[ ] Compare to prior month (flag variances >20% for major expense lines)
[ ] Update KPI dashboard
[ ] Update 60-day cash flow projection
[ ] Transfer month's tax reserve to EQ Bank savings (income tax portion = ~28% of net income)

NOTES / ISSUES THIS MONTH:
_______________________________________________
```

### 6.2 Quarterly Additions

On top of the standard month-end close for Q1/Q2/Q3/Q4 closing months:

```
QUARTERLY ADDITIONS
[ ] Pull HST collected for full quarter (Account 2100 total)
[ ] Pull total ITCs for full quarter (Account 2110 total)
[ ] File HST return via CRA My Business Account (or QBO NETFILE if using QBO)
[ ] Remit net HST by due date (see Section 7 for deadlines)
[ ] Record HST remittance as payment in accounting software
[ ] Review year-to-date income — adjust income tax installments if needed
[ ] Review registered account contribution room — FHSA ($8K/year), TFSA, RRSP
```

---

## Section 7: GST/HST Filing

### 7.1 Registration Thresholds

| Revenue | Requirement |
|---------|-------------|
| $0 to $30,000 (rolling 4 quarters) | Voluntary registration only |
| Over $30,000 in any single quarter OR in 4 rolling consecutive quarters | **Mandatory registration within 29 days** |
| Once registered | Must collect and remit HST on all taxable supplies — no going back until deregistration |

**Atlas recommendation:** Register voluntarily immediately, even before $30K. OASIS serves B2B clients who can claim ITCs on the HST they pay you — HST does not hurt them. You benefit by claiming ITCs on all your business expenses (software, equipment, professional fees) from day one.

### 7.2 Filing Frequency

| Annual Revenue | Default Period | Election Option |
|----------------|---------------|-----------------|
| $0 to $1.5M | Annual | Elect quarterly for better cash flow |
| $1.5M to $6M | Quarterly | Elect monthly |
| Over $6M | Monthly | — |

**Atlas recommendation for OASIS:** File quarterly. Annual filing delays ITC refunds and builds up larger lump-sum remittances. Quarterly keeps HST reserves calibrated and avoids nasty surprises.

**Quarterly filing deadlines (calendar year-end):**

| Quarter | Period | Due Date |
|---------|--------|----------|
| Q1 | January to March | April 30 |
| Q2 | April to June | July 31 |
| Q3 | July to September | October 31 |
| Q4 | October to December | January 31 |

### 7.3 Quick Method vs. Regular Method

The Quick Method allows eligible businesses (under $400K in annual taxable supplies) to remit a flat percentage of gross revenue instead of tracking individual ITCs.

**Quick Method remittance rates (service businesses, Ontario):**

| Revenue Tranche | Rate |
|-----------------|------|
| First $30,000 of taxable supplies in the year | 8.8% |
| Amounts over $30,000 | 8.8% |
| Credit on first $30,000 | 1% (deduct from remittance) |

**Quick Method Example:**

```
Scenario: $80,000 annual revenue (HST-exclusive), modest expenses
HST Collected (13%):                   $10,400

Quick Method calculation:
  8.8% × $80,000 =                      $7,040
  Less 1% credit on first $30,000 =     ($300)
  Net Quick Method remittance =          $6,740
  HST retained by CC =                  $3,660

Regular Method calculation:
  HST Collected:                        $10,400
  ITCs on $15,000 expenses × 13% =     ($1,950)
  Net Regular Method remittance =        $8,450
  HST retained by CC =                  $1,950

Quick Method advantage in this scenario: $8,450 - $6,740 = $1,710 saved
```

**Decision rule:** Quick Method wins when your ITC-eligible expenses are less than approximately 18-20% of your gross revenue. Regular Method wins when your expenses are high (e.g., heavy subcontractor costs, large equipment purchases, or significant cloud infrastructure). Recalculate annually. Elect via CRA My Business Account.

### 7.4 Input Tax Credits — What Qualifies

ITCs reduce net HST remittable. Eligible when:
- The purchase is for commercial activity
- You are a registered HST participant
- You have a valid receipt with vendor HST number (for claims over $30)

| Expense | ITC Eligibility |
|---------|----------------|
| Software subscriptions (with HST) | 100% ITC |
| Computer equipment | 100% ITC |
| Professional fees (accountant, lawyer) | 100% ITC |
| Office supplies | 100% ITC |
| Advertising and marketing | 100% ITC |
| Cloud hosting | 100% ITC |
| Meals and entertainment | **50% ITC only** (s.236 ETA — mirrors income tax 50% rule) |
| Home office — rent portion | No ITC (residential rent is exempt supply) |
| Personal expenses | No ITC |

### 7.5 HST on Digital Services

If you sell digital services to non-registered Canadian consumers (individual end users):
- You must collect and remit HST on those sales (CRA digital economy measures, July 2021)
- If you sell exclusively to HST-registered businesses (B2B): the reverse-charge mechanism applies — the business client self-assesses
- Confirm your invoicing software (Stripe, etc.) is configured to apply 13% Ontario HST to Canadian customer billing addresses

---

## Section 8: Payroll

### 8.1 Sole Proprietor — No Payroll for Yourself

As a sole proprietor, you do not pay yourself a salary. You take **Owner's Draws** (Account 3100). Draws are not tax-deductible business expenses. You pay personal income tax on net business income, not draws.

CPP for sole proprietors: you pay **both** employee and employer portions = 11.9% of net self-employment income above the basic exemption (~$3,500). This is calculated on Schedule 8 of your T1 and is a mandatory payment — not optional.

### 8.2 When Payroll Applies

Payroll applies when you hire an arm's-length worker classified as an employee.

**Employee vs. Contractor — CRA Multi-Factor Test (Wiebe Door):**

| Factor | Employee Indicator | Contractor Indicator |
|--------|-------------------|---------------------|
| Control | You control how/when/where work is done | Worker controls their own methods |
| Ownership of tools | You provide the tools | Worker uses their own tools |
| Profit/risk | Worker earns fixed rate, no profit/loss exposure | Worker can profit more or lose by their own decisions |
| Integration | Worker is integral to your operation | Worker is in business for themselves |

**Practical rule:** If you pay the same person more than $2,500/year and they have no other clients, CRA may reclassify them as an employee. Use written contractor agreements. Ensure contractors invoice you with their own HST number.

### 8.3 Payroll Registration and Deductions

**Step 1:** Register for a CRA Payroll Account (RP number) before your first payroll run.

**Per paycheque deductions:**

| Deduction | 2025 Rate | Notes |
|-----------|-----------|-------|
| Employee CPP | 5.95% of insurable earnings | s.8(1) CPP Act |
| Employee EI | 1.66% of insurable earnings | s.68 EI Act |
| Income tax | Per CRA TD1 + withholding tables | Employee submits TD1 on hire |

**Employer costs (on top of salary):**

| Contribution | 2025 Rate | Notes |
|-------------|-----------|-------|
| Employer CPP | 5.95% (matches employee) | Employer matches dollar-for-dollar |
| Employer EI | 2.324% (= 1.4 × employee EI) | s.68(b) EI Act — employer pays more |
| Income tax | None — only deduct and remit | No employer income tax contribution |

**True cost of an employee earning $50,000 salary:**
```
Gross salary:          $50,000
Employer CPP:          $2,975
Employer EI:           $1,162
Total employer cost:  ~$54,137 (8.3% premium over salary)
```

### 8.4 Remittance Deadlines

| Employer Category | Annual Payroll | Remittance Deadline |
|-------------------|---------------|---------------------|
| Regular remitter | Under $1M | 15th of the following month |
| Quarterly remitter | New employer, prior year deductions <$3,000 | 15th after each quarter-end |
| Accelerated — Threshold 1 | Deductions $25,000-$99,999/year | Twice monthly (7th and 22nd) |
| Accelerated — Threshold 2 | Deductions $100,000+/year | Weekly |

**Late remittance penalties:** 3% if 1-3 days late, 5% if 4-5 days late, 7% if 6-7 days late, 10% if 8+ days late. A second late remittance in the same year doubles these rates (s.227.1 ITA). Do not be late.

### 8.5 Year-End Payroll Filings

| Filing | Deadline | Details |
|--------|----------|---------|
| T4 slips to employees | Last day of February | One per employee. Also file T4 Summary. |
| T4A slips to contractors | Last day of February | Required for any contractor paid >$500/year |
| Record of Employment (ROE) | 5 calendar days after last day of work | Required when employee stops working (layoff, quit, termination). File via Service Canada ROE Web. |

### 8.6 Payroll Software

**Atlas recommendation post-incorporation: Wagepoint** (~$20/mo base + $4/employee)
- Canadian-built, CRA-integrated
- Calculates CPP/EI/tax automatically
- Direct deposit to employee accounts
- Generates T4, T4A, ROE
- Remits source deductions to CRA automatically on your behalf
- Eliminates the risk of late remittance penalties

---

## Section 9: Year-End Procedures

### 9.1 Year-End Checklist

Complete Part A in December. Parts B through G by January 31.

```
YEAR-END CLOSE CHECKLIST
Tax Year: _____________

PART A — PRE-CLOSE (December)
[ ] Review all uncategorized transactions for the year — categorize everything
[ ] Reconcile all bank accounts through December 31
[ ] Confirm all client invoices for the year are issued and recorded
[ ] Make any final business purchases before Dec 31 to capture this year's deductions
[ ] Review A/R — write off bad debts (Account 6120, s.20(1)(p) ITA)
[ ] Make FHSA contribution by December 31 (FHSA deadline is Dec 31, not March 1)
[ ] Review tax-loss harvesting opportunities in crypto (sell by Dec 28 — T+2 settlement)
[ ] Watch superficial loss rule: no repurchase of same crypto within 30 days of harvested loss

PART B — ADJUSTING JOURNAL ENTRIES
[ ] Prepaid expenses: Identify expenses paid in 2026 covering 2027 period
    → Debit Prepaid Expenses (1200); remove 2027 portion from 2026 expenses
    → Example: Annual subscription paid Nov 2026 covering Nov 2026-Oct 2027
               → Only Nov/Dec 2026 portion = 2026 deduction (2/12 of annual cost)
[ ] Accrued expenses: Identify 2026 expenses not yet paid as of Dec 31
    → Debit expense account; Credit Accrued Liabilities (2000)
    → Example: December CPA invoice received Jan 5 — still a 2026 expense
[ ] Deferred revenue: Payments received in 2026 for work to be done in 2027
    → Debit Revenue; Credit Deferred Revenue
    → Note: CRA generally requires cash-basis reporting for most sole proprietors

PART C — CAPITAL ASSET VERIFICATION
[ ] List every capital asset purchased or disposed of in the year
[ ] Confirm CCA class for each asset (see quick reference below)
[ ] Apply half-year rule: only 50% of normal CCA rate in year of acquisition (Reg 1100(2))
[ ] Photograph all major business equipment (date-stamped — audit defense)
[ ] Confirm home office measurements have not changed; update if you moved

CCA Class Quick Reference:
  Class 8  (20%)    Furniture, equipment, machinery
  Class 10 (30%)    Vehicles (general)
  Class 10.1 (30%)  Vehicles >$37,000 (separate class per vehicle — s.13(7)(g))
  Class 12 (100%)   Software, tools under $1,750, small equipment
  Class 14.1 (5%)   Customer lists, goodwill, licences (eligible capital property)
  Class 50 (55%)    General-purpose computers and laptops
  Note: CCA is optional — you may claim less than the maximum. Useful if income
        is near a lower tax bracket (preserving CCA for a higher-income year).

PART D — HOME OFFICE CALCULATION (T2125 Part 7 → Line 9945)
[ ] Confirm square footage of dedicated work area (must be used exclusively OR principally for work)
[ ] Confirm total floor area of home
[ ] Business-use percentage = work area sq ft / total home sq ft
[ ] Eligible home expenses (apply the percentage to each):
    Rent (if renting), heat, electricity, water, home insurance (business portion),
    maintenance and repairs (proportional)
    NOT eligible: mortgage principal, property improvements
    Mortgage interest IS eligible (proportional %)
[ ] Home office deduction cannot create or increase a net business loss (s.18(12) ITA)
    Excess can be carried forward to future years

PART E — VEHICLE LOG SUMMARY (if motor vehicle claimed)
[ ] Total km driven in the year (odometer Dec 31 minus Jan 1)
[ ] Total business km driven (from contemporaneous mileage log)
[ ] Business-use percentage = business km / total km
[ ] Apply percentage to actual vehicle expenses for T2125 Line 9281

PART F — T2125 PREPARATION
[ ] Separate T2125 for OASIS and a separate T2125 for DJ (if both active)
[ ] Revenue per T2125 (Line 8000) — verify matches accounting software
[ ] Expenses per T2125 line — verify each category total
[ ] Meals/entertainment: enter 50% of actual amounts (gross amount × 50%)
[ ] Home office: enter calculated amount (from Part D above)
[ ] Motor vehicle: enter calculated amount (from Part E above)
[ ] CCA: complete CCA schedule (Area A) — half-year rule applied
[ ] Verify net business income flows correctly to T1 Line 13500

PART G — TAX SLIPS AND DOCUMENTS TO GATHER
[ ] T4 slip (Nicky's employment income)
[ ] T4 for any other employment
[ ] T5 slips (investment income, dividends)
[ ] T3 slips (trust income — mutual funds, ETFs)
[ ] T5008 slips (securities transactions — brokers)
[ ] RRSP contribution receipts (contributions made Jan 1 to March 1)
[ ] FHSA contribution receipt (year-end balance from institution)
[ ] T2202 (tuition carryforward — Bishop's University)
[ ] Charitable donation receipts
[ ] OSAP interest paid (Line 31900 non-refundable credit)
[ ] Prior year Notice of Assessment (for carryforward amounts)
[ ] Koinly Schedule 3 crypto report

PART H — PROFESSIONAL REVIEW
[ ] Provide T2125 draft + all documents to CPA/tax preparer (if using one)
[ ] Aim to file by March — do not wait until June 15 deadline
[ ] Tax owing is still due by April 30 even if you file on June 15
[ ] Early filing = faster NOA = faster access to benefit payments (CCB, GST/HST credit)

NOTES: _______________________________________________
```

---

## Section 10: Financial Reporting

### 10.1 Monthly P&L Statement

```
OASIS AI Solutions — Monthly Profit & Loss
Month: ________________  Year: ________________

REVENUE
  OASIS Consulting — CAD                        $____________
  OASIS Consulting — USD (converted)            $____________
  DJ / Event Income                             $____________
  Other Revenue                                 $____________
TOTAL REVENUE                                   $============

COST OF REVENUE (Direct Costs)
  Subcontractor Costs                           $____________
  Direct AI API / Software (client-billed)      $____________
  Direct Hosting (client projects)              $____________
GROSS PROFIT                                    $============
GROSS MARGIN                                    ____________%

OPERATING EXPENSES
  Advertising & Promotion (8521)                $____________
  Cloud & Hosting — Overhead (8521)             $____________
  Meals & Entertainment — 50% (8523)            $____________
  Bank & Merchant Charges (8710)                $____________
  Office Expenses & Software (8810)             $____________
  Professional Fees (8860)                      $____________
  Management / Admin (8871)                     $____________
  Telephone & Internet (9220)                   $____________
  Travel (9200)                                 $____________
  Home Office (9945)                            $____________
  Other Expenses (9270)                         $____________
  CCA (9936) — year-end only                   $____________
TOTAL OPERATING EXPENSES                        $============

NET INCOME (before tax)                         $============
NET MARGIN                                      ____________%

TAX RESERVE (28% of net income)                 $____________
OWNER'S DRAWS THIS MONTH                        $____________
```

### 10.2 Annual Balance Sheet (Sole Proprietor)

Not legally required, but critical for CCPC transition planning and understanding net worth trajectory.

```
As of December 31, ________

ASSETS                              LIABILITIES
Current Assets:                     Current Liabilities:
  Cash — Business Chequing  $____    HST Payable (Net)    $____
  Cash — Wise               $____    Income Tax Payable   $____
  Cash — HST Reserve        $____    Credit Card Payable  $____
  Accounts Receivable       $____    Accounts Payable     $____
  Prepaid Expenses          $____    Accrued Liabilities  $____
  Crypto (FMV, CAD)         $____  Total Current Liab.   $====

Fixed Assets:                       EQUITY
  Equipment (gross cost)    $____    Owner's Capital      $____
  Less: Accumulated CCA    ($____)   Owner's Draws       ($____)
  Equipment (net)           $____    Retained Earnings    $____
                                     Current Year Income  $____
TOTAL ASSETS                $====  TOTAL LIABILITIES + EQ $====
```

### 10.3 KPI Dashboard

Track these monthly. They are the vital signs of the business.

| KPI | Formula | Target |
|-----|---------|--------|
| Monthly Revenue | Sum of all invoiced revenue | Growing MoM |
| Gross Margin | (Revenue - COGS) / Revenue | >80% (service business) |
| Net Profit Margin | Net Income / Revenue | >50% (solo, low overhead) |
| Effective Tax Rate | Total tax paid / Gross income | Minimize vs marginal rate |
| Tax Reserve Balance | Running EQ Savings balance | Equal to 28% × YTD net income |
| A/R Days Outstanding | (A/R balance / Monthly revenue) × 30 | <30 days |
| Monthly Savings Rate | Saved amount / Net income after tax | >50% (aggressive FIRE path) |
| Cash Runway | Total cash / Average monthly expenses | >3 months minimum |
| HST Reserve Adequacy | Reserve balance / Next quarter's estimated HST | >100% |
| TFSA/FHSA Utilization | Contributions made / Available room | 100% annually |

### 10.4 Monthly CFO Report Template

```
==========================================================
    OASIS AI Solutions — Atlas CFO Report
    Period: [Month Year]  |  Prepared: [Date]
==========================================================

EXECUTIVE SUMMARY
  Revenue:     $XX,XXX    (MoM: +/- XX%)
  Net Income:  $XX,XXX    (Margin: XX%)
  Cash:        $XX,XXX    (Runway: X months)
  Net Worth:   $XX,XXX    (MoM: +/- XX%)

REVENUE
  OASIS Consulting:    $XX,XXX  (XX%)
  DJ Gigs:             $X,XXX   (XX%)
  Crypto (realized):   $X,XXX   (XX%)
  Total:               $XX,XXX

A/R STATUS
  Outstanding:         $X,XXX (X invoices)
  30+ days overdue:    $X,XXX  [ACTION if >$0]
  90+ days:            $XXX    [WRITE OFF]

TAX POSITION
  HST Collected YTD:   $X,XXX
  ITCs YTD:            $X,XXX
  Net HST Owing:       $X,XXX
  HST Reserve Bal:     $X,XXX  [OK / TOP UP NEEDED]
  Income Tax Reserve:  $X,XXX
  Next HST Due:        [Date]

REGISTERED ACCOUNTS
  FHSA:  $X,XXX contributed / $8,000 limit  [XX% utilized]
  TFSA:  $X,XXX contributed / $X,XXX room   [XX% utilized]
  RRSP:  $X,XXX contributed / $X,XXX room   [XX% utilized]

WEALTH
  Liquid Cash:     $XX,XXX
  TFSA:            $XX,XXX
  FHSA:            $X,XXX
  Crypto (FMV):    $X,XXX
  OSAP:           -$XX,XXX
  Net Worth:       $XX,XXX
  Savings Rate:    XX%

ALERTS AND ACTION ITEMS
  [ ] [Priority item 1]
  [ ] [Priority item 2]
  [ ] [Priority item 3]

==========================================================
Next report: [1st of next month]
==========================================================
```

---

## Section 11: Crypto Bookkeeping

### 11.1 CRA Tax Treatment Overview

CRA treats cryptocurrency as property, not currency. Every disposition is a taxable event (CRA interpretation bulletin 2014-0538691I7 and subsequent guidance):

| Event | Tax Treatment |
|-------|--------------|
| Sell crypto for CAD | Capital gain or loss (or business income if trading) |
| Trade crypto-to-crypto | Deemed disposition at FMV — capital gain or loss |
| Use crypto to purchase goods/services | Deemed disposition at FMV |
| Receive crypto as payment for services | Business income at FMV on receipt date |
| Receive staking rewards | Income at FMV on date received |
| Receive airdrops | Income at FMV on date received (CRA 2023 guidance) |
| DeFi lending interest received | Income at FMV on date received |
| Hard fork | Income at FMV on date the new coin is accessible |
| Crypto-to-fiat conversion | Capital gain or business income |
| Transfer between your own wallets | NOT a disposition — no tax event |

**Business income vs. capital gain — the critical distinction:**
- Business income: 100% taxable. Applicable if trading is frequent, systematic, profit-driven (day trader profile).
- Capital gain: 50% taxable (inclusion rate). Applicable if holding with investment intent.
- ATLAS trading daemon transactions on Kraken: likely **business income** given high frequency. Consult CPA to confirm characterization. Once characterized one way, maintain consistency.

### 11.2 Adjusted Cost Base (ACB) — Weighted Average Method

CRA requires the weighted average ACB method for identical properties (all BTC is fungible — tracked as a pool across all wallets/exchanges).

**Formula:**
```
ACB per coin = Total Cost of All Acquisitions to Date / Total Coins Held
```

**Example:**
```
Jan 15:  Buy  0.10 BTC @ $50,000 CAD = $5,000 cost. ACB = $50,000/BTC.
Mar 20:  Buy  0.05 BTC @ $60,000 CAD = $3,000 cost.
         Pool: 0.15 BTC, $8,000 total. ACB = $53,333/BTC.
Apr 1:   Sell 0.05 BTC @ $65,000 CAD = $3,250 proceeds (less $10 fee = $3,240 net)
         ACB of sold coins = 0.05 × $53,333 = $2,667
         Capital gain = $3,240 - $2,667 = $573
         Remaining pool: 0.10 BTC, $5,333 total. ACB stays $53,333/BTC.
```

**Exchange fees:** Add to ACB on purchase. Deduct from proceeds on sale.

### 11.3 Superficial Loss Rule (s.54 ITA)

If you sell crypto at a loss AND reacquire the **identical property** within the 30-day window before or after the sale, the loss is denied. The denied loss is added to the ACB of the reacquired property.

**The window:** 61 days total — 30 days before sale through 30 days after sale.

**CRA confirmed this applies to crypto.** Koinly detects superficial loss violations automatically. Critical for Q4 tax-loss harvesting: if you harvest a crypto loss, do not repurchase the same crypto for 31 days after the sale.

**Wash sale workaround (legal):** Sell BTC → buy ETH or SOL instead for 31 days → buy back BTC. Loss is preserved. You maintain crypto exposure through a different asset.

### 11.4 Crypto Ledger Template

Maintain per-coin ledger (or use Koinly). Each coin is a separate pool.

```
BTC Ledger — Weighted Average ACB Method
=========================================
Date     | Type  | Qty BTC | CAD Price | Total CAD | Fee CAD | Pool Qty | Pool Cost | ACB/BTC  | Gain/Loss
---------|-------|---------|-----------|-----------|---------|----------|-----------|----------|-----------
2026-01  | Buy   | 0.1000  | $50,000   | $5,000    | $15     | 0.1000   | $5,015    | $50,150  | —
2026-03  | Buy   | 0.0500  | $60,000   | $3,000    | $9      | 0.1500   | $8,024    | $53,493  | —
2026-04  | Sell  | 0.0500  | $65,000   | $3,250    | $10     | 0.1000   | $5,351    | $53,493  | +$890
2026-06  | Fee   | —       | —         | $25       | —       | 0.1000   | $5,376    | $53,760  | —
```

### 11.5 DeFi and Complex Transactions

| Activity | CRA Treatment | Record What |
|----------|--------------|-------------|
| Staking rewards | Income at FMV on receipt date | Date, quantity, CAD FMV, exchange rate source |
| DeFi lending interest | Income at FMV on receipt date | Same as above |
| Liquidity pool deposit | Disposition of deposited tokens at FMV | Treat as sell — calculate gain/loss |
| Liquidity pool withdrawal | Disposition of LP tokens at FMV | Treat as sell — calculate gain/loss on LP tokens |
| NFT creation (artist) | Income when sold | Proceeds = business income |
| NFT purchase/resale | Capital gain or business income (depends on frequency) | Full cost and disposition records |
| Crypto used to pay for services | Deemed disposition at FMV | Gain/loss based on ACB |

### 11.6 Crypto Tax Software Comparison

| Platform | Price | ACB/Weighted Avg | Superficial Loss | CRA Schedule 3 Export | Koinly Notes |
|----------|-------|-----------------|-----------------|----------------------|--------------|
| **Koinly** | Free (25 tx) / $49+ per tax year | Yes | Yes (auto-detect) | Yes — CRA-ready | Best Canadian support |
| **CoinTracker** | Free (25 tx) / $59+ per tax year | Yes | Partial | Yes | Weaker Canadian rules |
| **CryptoTaxCalculator** | $49+ per tax year | Yes | Yes | Yes | Good DeFi support |
| **adjustedcostbase.ca** | Free | Yes | Manual check | Manual | Canadian-made, good for verification |

**Atlas recommendation: Koinly.** Best Canadian tax support. Detects superficial loss rule violations. Kraken API integration. Generates CRA-ready Schedule 3 summary. Use `adjustedcostbase.ca` to verify ACB calculations for any disputed trades.

**Koinly setup:**
1. Connect Kraken read-only API (never give write access to any tax software)
2. Import historical transactions via CSV for pre-API history
3. Tag each transaction type: trade / transfer / staking reward / airdrop / fee
4. Review Koinly's income vs capital gain characterization — verify it matches your CPA's agreed position
5. Export Schedule 3 report at tax time
6. Cross-reference with Atlas `finance/tax.py` ACB calculations

### 11.7 T1135 Foreign Income Verification

**If the total cost of all foreign cryptocurrency accounts (Kraken, Binance, Coinbase, etc.) exceeded $100,000 CAD at any point during the year:** T1135 (Foreign Income Verification Statement) is required, filed with your T1 return.

**T1135 deadline:** Same as T1 filing deadline (June 15 for self-employed).

**Penalty for missing T1135:** $25/day up to $2,500, plus 5% of highest cost amount for repeat failures. CRA pursues this actively — see `docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md` for full enforcement context.

### 11.8 Year-End Crypto Snapshot Protocol

On December 31 each year:
1. Record FMV (CAD) of each coin position at closing price (Kraken closing price is acceptable)
2. Document source of FMV (e.g., "Kraken daily closing price, December 31, 2026")
3. Save snapshot as a signed, dated PDF — this is audit evidence
4. Update crypto asset accounts in bookkeeping software (1300-1390) to reflect FMV
5. Confirm FMV does not trigger T1135 obligation (see above)

---

## Appendix A: T2125 Line Map

| T2125 Line | Description | Chart of Account(s) |
|------------|-------------|---------------------|
| 8000 | Gross business income | 4100 + 4110 + 4200 + 4400 + 4900 |
| 8340 | Subcontracting costs | 5010 + 5020 + 5030 |
| 8521 | Advertising | 6100 + 6105 + 6155 (partial) |
| 8523 | Meals and entertainment (50%) | 6110 (enter 50% of gross) |
| 8590 | Bad debts | 6120 |
| 8690 | Insurance | 6130 |
| 8710 | Interest and bank charges | 6140 + 6320 |
| 8810 | Office expenses | 6150 + 6155 |
| 8811 | Supplies | 6160 |
| 8860 | Professional fees | 6170 + 6175 |
| 8871 | Management and admin fees | 6180 + 6185 |
| 8910 | Rent | 6190 |
| 8920 | Salaries, wages, benefits | 6210 |
| 8960 | Repairs and maintenance | 6200 |
| 9200 | Travel expenses | 6220 + 6225 |
| 9220 | Telephone and utilities | 6230 + 6235 |
| 9224 | Utilities | 6240 |
| 9270 | Other expenses | 6290 + 6900 |
| 9281 | Motor vehicle (from Part 7) | 6250 |
| 9936 | Capital cost allowance (from CCA Schedule) | 6260 + 6265 + 6270 |
| 9945 | Business-use-of-home (from Part 7) | 6280 |

---

## Appendix B: Key Deadlines

| Date | Obligation |
|------|------------|
| January 15 | Q4 HST remittance due |
| January 31 | Year-end bookkeeping close target |
| February 28 | T4 and T4A slips issued to employees and contractors |
| March 1 | RRSP contribution deadline (60 days after December 31) |
| March 31 | Annual HST return due (annual filers, calendar year-end) |
| April 30 | Q1 HST remittance due / T1 balance owing due (even if filing June 15) |
| June 15 | T1 filing deadline (self-employed) / T1135 if applicable |
| July 15 | Q2 HST remittance due |
| October 15 | Q3 HST remittance due |
| December 24 | Last day to sell securities/crypto and have T+2 settlement complete before year-end |
| December 31 | FHSA contribution deadline / TFSA contribution deadline |
| Ongoing | Receipt retention: 6 years from tax year-end (s.230 ITA) |
| Ongoing | CCA records: 6 years after asset disposal |

---

## Appendix C: First-Week Setup Checklist

**Day 1 — Bank Accounts**
- [ ] Open RBC Business Chequing (requires Master Business Licence — $60 at ServiceOntario)
- [ ] Open Wise Business account (CAD + USD)
- [ ] Open Business Savings account for HST/tax reserve (EQ Bank for 3%+ interest)
- [ ] Open FHSA if not already done (Wealthsimple or Questrade — no fees)

**Day 2 — Accounting Software**
- [ ] Sign up for Wave (free) or QuickBooks Online ($20/mo)
- [ ] Configure chart of accounts per Section 1
- [ ] Connect bank feeds (RBC Business + Wise)
- [ ] Set up invoice template with sequential numbering and HST registration number

**Day 3 — Automation**
- [ ] Install HubDoc (free with QBO) or Dext receipt capture
- [ ] Set up bank feed categorization rules for recurring transactions
- [ ] Connect Kraken read-only API to Koinly
- [ ] Create Google Drive folder structure per Section 4.4

**Day 4 — Routines**
- [ ] Set weekly calendar block: "Categorize transactions" (Sunday, 15 min)
- [ ] Set monthly calendar block: "Month-end close" (1st of month, 1 hour)
- [ ] Set quarterly calendar block: "HST filing + tax review" (quarterly, 2 hours)
- [ ] Create financial dashboard in Notion or spreadsheet per Section 10.3

**Day 5 — Catch-Up**
- [ ] Import or enter all YTD transactions from bank CSV
- [ ] Capture all outstanding receipts from the year to date
- [ ] Send any outstanding invoices
- [ ] Calculate HST collected YTD and transfer appropriate reserve to savings account

---

> This document is the operational backbone of Atlas's CFO function.
> The tax strategy (`docs/ATLAS_TAX_STRATEGY.md`) defines WHAT to optimize.
> The deductions masterlist (`docs/ATLAS_DEDUCTIONS_MASTERLIST.md`) defines EVERY available deduction.
> This document defines HOW to keep the books clean enough to actually execute those strategies.
> Without clean books, every strategy is theoretical. With clean books, Atlas runs the numbers automatically.
>
> ITA references: s.9, s.18, s.20, s.54, s.67.1, s.125(5.1), s.15(2), s.18(12), s.20(1)(c), s.20(1)(p), s.227.1, s.230, s.231.2
> Reg references: Reg 1100-1107 (CCA classes and rates), Sch II (CCA class listing)
> CRA guidance: IC05-1R1 (digital records), CRA 2014-0538691I7 (crypto as property)
