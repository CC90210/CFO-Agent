# CRA Audit Triggers, Red Flags, and Bulletproof Compliance

> **Compiled by:** ATLAS (CC's CFO Agent)
> **Date:** 2026-03-27
> **Scope:** Proactive audit prevention, CRA risk-scoring systems, red flag identification, documentation systems, and compliance calendar
> **Jurisdiction:** Canada (Ontario) | **Taxpayer profile:** 22-year-old sole proprietor (OASIS AI Solutions), crypto trader (Kraken), forex/metals (OANDA), DJ income, dual Canadian-British citizenship, projected $280K-$480K+ CAD in 2026
> **Purpose:** Prevent audits before they happen. Be bulletproof if one does. This is the PROACTIVE document. See `ATLAS_CRA_AUDIT_DEFENSE.md` for reactive defense and `ATLAS_VDP_GUIDE.md` for voluntary disclosure.
> **Philosophy:** The cheapest audit is the one that never happens. The second-cheapest is the one where CRA finds nothing.

---

## Table of Contents

1. [CRA's Matching and Risk-Assessment Systems (2025-2026)](#1-cras-matching-and-risk-assessment-systems-2025-2026)
2. [The 25 Biggest CRA Red Flags (Ranked by Audit Probability)](#2-the-25-biggest-cra-red-flags-ranked-by-audit-probability)
3. [CC-Specific Risk Assessment](#3-cc-specific-risk-assessment)
4. [The Bulletproof Documentation System](#4-the-bulletproof-documentation-system)
5. [The 6-Year Rule and Document Retention](#5-the-6-year-rule-and-document-retention)
6. [CRA Installment Payment Strategy](#6-cra-installment-payment-strategy)
7. [HST Compliance for SaaS](#7-hst-compliance-for-saas)
8. [Transfer Pricing for Solo Founders](#8-transfer-pricing-for-solo-founders)
9. [CRA Voluntary Compliance Programs](#9-cra-voluntary-compliance-programs)
10. [Digital Nomad / Cross-Border Compliance](#10-digital-nomad--cross-border-compliance)
11. [CRA Penalties and Interest Reference](#11-cra-penalties-and-interest-reference)
12. [The Annual Compliance Calendar for CC](#12-the-annual-compliance-calendar-for-cc)
13. [Master Compliance Checklist](#13-master-compliance-checklist)

---

## 1. CRA's Matching and Risk-Assessment Systems (2025-2026)

CRA does not audit randomly. Approximately 75% of audits are triggered by automated systems that score, match, and flag returns before any human touches them. Understanding these systems is step one in never triggering them.

### 1.1 T1 Auto-Assessment (Slip Matching)

CRA receives **every information slip** filed by third parties before your return arrives:

| Slip | Who Files It | What CRA Knows |
|------|-------------|----------------|
| **T4** | Employers (Nicky's) | CC's employment income, CPP/EI deductions, tax withheld |
| **T4A** | Contract payers | Any single payment > $500 for services |
| **T5** | Banks/brokers (Wealthsimple, RBC) | Interest income, dividends, capital gains distributions |
| **T5008** | Investment dealers | Securities transactions — proceeds of disposition (not ACB) |
| **T3** | Trusts/mutual funds | Trust income allocations |
| **T2202** | Educational institutions | Tuition amounts |
| **RC62** | CRA itself | UCCB, Canada Worker Benefit, GST/HST credit |
| **NR4** | Non-resident payers | Foreign-source income with Canadian withholding |

**How matching works:** CRA's Automated Compliance Technology (ACT) system compares every slip amount against the corresponding line on your T1. If you reported $5,046.73 from Nicky's but the T4 says $5,246.73, the system flags the discrepancy automatically. No human judgment required.

**CC risk:** Moderate. Nicky's T4 is straightforward. The risk is on the self-employment side (OASIS, DJ) where no third-party slips exist — CRA relies on cross-referencing bank deposits and payment processor data instead.

**Critical rule:** NEVER omit a T-slip. CRA already has it. Omitting a T4 or T5 is the single easiest way to trigger automated review. If you don't have a slip by late February, call the issuer or check My Account.

### 1.2 CORTAX Risk-Scoring System

CORTAX is CRA's core assessment and case management system. Within CORTAX, the **Risk Assessment and Workload System (RAWS)** assigns a numerical risk score to every return filed. This score determines whether your return sails through processing or gets flagged for human review.

**How RAWS scores your return:**

1. **Statistical deviation analysis** — Your claimed deductions, income ratios, and expense-to-revenue percentages are compared against statistical norms for your industry (NAICS code), income bracket, age group, and geographic region. If your home office deduction is 3 standard deviations above the mean for "Computer systems design" (NAICS 5415) in Ontario for a sole proprietor earning $200K-$500K, it triggers a flag.

2. **Year-over-year delta analysis** — CRA compares your current return to your prior-year return. Major swings trigger flags:
   - Income increase > 25-50% without corresponding changes in deductions
   - Income decrease > 50% (CRA suspects income splitting or diversion)
   - New line items that never appeared before (e.g., suddenly claiming business losses)
   - Disappearance of previously reported income sources

3. **Cross-return matching** — Your T1 is cross-referenced with:
   - Your spouse's return (income splitting detection)
   - Your corporation's T2 (shareholder benefit, management fees)
   - Your HST return (revenue consistency check)
   - Third-party returns that reference you (partnerships, trusts)

4. **Profile-based risk factors** — Certain taxpayer profiles carry inherent higher risk scores:
   - Self-employed (2-5x the audit rate of T4 employees)
   - First-time filers with business income
   - Young taxpayers with high income (statistical anomaly for age group)
   - Taxpayers in cash-intensive industries (DJ income qualifies)
   - Taxpayers with foreign accounts or dual citizenship

5. **Compliance history** — Prior audit adjustments, late filings, missed installments, and penalty history increase your baseline risk score permanently. A clean compliance history reduces it.

**CC's CORTAX profile (estimated risk):**
- Self-employed: +HIGH
- First significant filing year: +HIGH (no track record = higher scrutiny)
- Age 22 with $280K+ income: +HIGH (statistical outlier for age cohort)
- Cash-based DJ income: +MEDIUM
- Crypto trading: +HIGH (CRA compliance project target)
- Dual citizenship: +MEDIUM (international compliance flag)
- No prior audit adjustments: -MODERATE (clean history helps)
- **Estimated aggregate risk score: ELEVATED** — CC's return will receive above-average scrutiny in 2026

### 1.3 AI and Machine Learning in CRA Audit Selection

CRA confirmed in its 2024-25 Departmental Plan that it is deploying **advanced data analytics and machine learning** to improve audit selection. This is not hypothetical — it is operational.

**What CRA's ML systems do:**

1. **Anomaly detection** — Neural networks trained on millions of returns identify statistical outliers that traditional rule-based systems miss. For example, a sole proprietor in Collingwood claiming 35% of revenue as "professional development" when the regional average is 3%.

2. **Pattern recognition across multiple years** — ML models identify multi-year patterns like gradually increasing deductions, income smoothing, or cyclical non-reporting that suggest systematic non-compliance rather than honest mistakes.

3. **Network analysis** — CRA maps relationships between taxpayers, businesses, advisors, and accounts. If your accountant's other clients have a high reassessment rate, your risk score increases.

4. **Predictive scoring** — ML models predict the probability that auditing a specific return will yield a reassessment. CRA allocates audit resources to maximize revenue recovery per auditor-hour.

5. **Natural language processing** — CRA's systems analyze text in objection letters, VDP applications, and correspondence to identify patterns associated with non-compliance.

**What this means for CC:** Traditional "stay below the radar" advice is becoming obsolete. CRA's systems identify complex patterns that simple rule-following does not address. The only reliable defense is legitimate compliance backed by documentation.

### 1.4 Crypto-Specific Intelligence Gathering

CRA has the most aggressive crypto enforcement program in the G7 outside of the United States.

**Exchange data orders (as of 2026):**

| Exchange | Order Date | Court | Data Obtained | CC Impact |
|----------|-----------|-------|---------------|-----------|
| **Coinsquare** | March 2021 | Federal Court | All users with accounts > $20K (2014-2020): names, addresses, DOB, transaction history | None (CC not on Coinsquare) |
| **Kraken** | 2022 | Via IRS (FATCA/Treaty Art. XXVII) | All Canadian-linked users: identity, trades, deposits/withdrawals | **DIRECT** — CRA has or can obtain CC's Kraken data |
| **Coinbase** | Filed 2024 | Federal Court | Pending — expected to cover all Canadian users 2018-2024 | None (CC not on Coinbase) |
| **Dapper Labs** | 2023 | Federal Court | NFT users (NBA Top Shot, Flow blockchain) | None |

**IRS data sharing:** Under Canada-U.S. Tax Convention Article XXVII and FATCA IGA, the IRS shares financial account data with CRA automatically. Kraken, as a U.S.-based exchange, reports to the IRS, which shares with CRA. This is NOT a one-time data request — it is ongoing, automatic, and annual.

**CARF (Crypto-Asset Reporting Framework) — 2026:**

The OECD's CARF was adopted by Canada in the 2024 federal budget and takes effect for reporting periods starting **January 1, 2026**. Under CARF:

1. Every Canadian crypto exchange and intermediary must report to CRA annually
2. Data reported: user identity, aggregate transaction values, number of transactions, types of crypto-assets
3. Foreign exchanges with Canadian users must also report under CARF's international exchange provisions
4. CRA will receive data from **100+ countries** that have adopted CARF
5. The data is granular — not just "has an account" but "traded $X across Y transactions"

**Impact for CC:** After 2026, there is essentially zero chance of unreported crypto activity going undetected. Every trade on Kraken will be automatically reported to CRA. Compliance is the only option.

### 1.5 International: CRS/AEOI Automatic Exchange

The Common Reporting Standard (CRS) has been active since 2018. Under CRS, financial institutions in 100+ countries automatically report account balances and income for non-resident account holders to the account holder's home country's tax authority.

**What CRA receives via CRS:**

| Data Category | Detail |
|--------------|--------|
| Account holder identity | Name, address, TIN (SIN for Canada), date of birth |
| Account balance | Year-end balance in the account currency |
| Income | Interest, dividends, gross proceeds from sales, other income |
| Account type | Deposit, custodial, equity, debt |

**CC-specific CRS risk:**
- **Wise USD account (~$1,900 USD)** — Wise is an e-money institution, not a traditional bank, but most jurisdictions include e-money institutions under CRS. If Wise reports CC's USD account to CRA, CRA will cross-reference it with any reported foreign income.
- **Kraken (US-based)** — Already covered under FATCA IGA; also potentially captured by CARF from 2026.
- **Any future accounts in UK, Ireland, Crown Dependencies** — Will be reported to CRA under CRS for as long as CC remains a Canadian tax resident.

**Key point:** Dual citizenship does not help here. CRS reports based on tax residency, not citizenship. As long as CC is a Canadian tax resident, all foreign accounts are reported to CRA.

### 1.6 Digital Platform Reporting (Coming 2026-2027)

Canada is implementing OECD Model Rules for Platform Reporting (DPI — Digital Platform Information). This requires digital platforms to report seller/earner income to CRA:

**Platforms affected:**
- **Stripe** — Must report merchant income to CRA. CC's Stripe revenue will be visible.
- **PayPal** — Must report business account transactions above thresholds.
- **Wise** — May be captured as a "relevant financial intermediary."
- **Airbnb, Uber, Fiverr, Upwork** — All captured under platform reporting.
- **Skool** — Unclear but possible under "digital intermediary" definitions if revenue flows through the platform.

**What this means:** CRA will have independent verification of CC's OASIS revenue through Stripe's reports. If CC reports $200K in business income but Stripe shows $250K in merchant transactions, automatic flag.

**CC action:** Ensure T2125 business income matches Stripe + Wise + direct payment records exactly. Reconcile monthly.

### 1.7 Social Media Monitoring

CRA has confirmed it monitors social media as part of lifestyle audits. This is not speculation — it has been disclosed in Federal Court proceedings and confirmed by the CRA Commissioner's office.

**What CRA looks for:**
- Visible wealth inconsistent with reported income (luxury cars, travel, jewelry)
- Business activity not reflected on tax returns (advertising services but reporting no business income)
- Claims contradicted by social media (claiming full-time business use of a vehicle while posting vacation photos of the same car)
- Cash-intensive businesses promoted on social media with no matching revenue reported

**CC-specific risk:** LOW currently. CC's lifestyle is modest relative to projected income. However, as income grows to $280K-$480K+, social media posts should be consistent with someone earning that level — not vastly above or below it.

**Practical rule:** Never post about income, revenue, or wealth on social media. Let CRA find out from your return, not Instagram.

---

## 2. The 25 Biggest CRA Red Flags (Ranked by Audit Probability)

These are ranked by the combination of (a) how likely each flag is to trigger audit selection, and (b) how likely a reassessment follows. Based on CRA published audit priorities, Federal Court decisions, and audit statistics.

### Tier 1 — Near-Certain Audit Triggers (50%+ probability in any given year)

**1. Unreported crypto income when CRA has exchange data**
- CRA has Kraken data. If your return shows zero crypto income but Kraken shows $50K+ in transactions, expect a letter within 12 months of assessment.
- Penalty: s.163(1) — 10% of omitted amount on second offence; s.163(2) gross negligence — 50% of tax understated.
- CC relevance: HIGH. Kraken trades must be reported accurately.

**2. Missing T-slips (T4, T5, T5008) — CRA already has them**
- CRA's matching system catches 100% of missing slips. This is not a judgment call — it is automated.
- Result: Automatic reassessment, no human review needed. Interest from original due date.
- CC relevance: MEDIUM. Nicky's T4 ($5,046.73) and any Wealthsimple T5/T5008 must be reported.

**3. HST collected but not remitted**
- CRA treats unremitted HST as trust fraud. This is one of the few areas where criminal prosecution occurs.
- If you charge HST to clients but don't file HST returns or remit, CRA treats it as holding government money in trust.
- Penalty: s.280 ETA — 6% interest + penalties; potential criminal prosecution under s.327 ETA.
- CC relevance: CRITICAL once registered for HST. If OASIS passes $30K in revenue (already there), registration is mandatory.

**4. T1135 not filed when required ($100K+ foreign property)**
- Penalty: $25/day late (max $2,500); gross negligence = $12,000/year per unfiled T1135.
- CRA has CRS data showing foreign accounts — they know if you have $100K+ abroad.
- CC relevance: LOW now (well below threshold). MONITOR as Wise USD balance grows and crypto values fluctuate.

### Tier 2 — High Audit Probability (25-50%)

**5. Repeated business losses (hobby loss rule)**
- CRA tests "reasonable expectation of profit" (REOP). Three or more consecutive years of losses on T2125 triggers automatic review.
- Key case: *Stewart v. Canada* (2002 SCC 46) — REOP not a standalone test, but CRA still uses it as a screening criterion.
- CC relevance: LOW. OASIS is profitable. But if CC starts a new venture that generates losses, be cautious about claiming them against OASIS income.

**6. Large deductions relative to revenue (expense-to-income ratio)**
- CRA compares your expense ratios to your NAICS code averages. If "Computer systems design" (NAICS 5415) sole proprietors in Ontario average 15% expenses-to-revenue and CC claims 45%, flag.
- Industry averages CRA uses: total expenses as % of gross revenue, by NAICS code, by province, by income bracket.
- CC relevance: MEDIUM. Keep OASIS deductions reasonable relative to revenue. At $280K+ revenue, $30K-$50K in legitimate deductions is defensible. $150K would trigger review.

**7. Self-employment income with no installments paid**
- CRA cross-references T2125 filers against installment payment records. If you owe > $3,000 at filing and paid zero installments, it signals either ignorance or intentional non-compliance.
- Result: Installment interest charges (prescribed rate, currently ~7-8% annualized) + potential flag for broader review.
- CC relevance: HIGH for 2026. With projected income, CC will owe $60K-$120K+ in tax. Zero installments = guaranteed flag.

**8. Claiming home office > 50% of home**
- CRA's administrative position: home office claims > 50% of square footage are presumptively unreasonable for a residence. The more space you claim, the more documentation you need.
- Must be "principally" (> 50% of time) used for business, OR used exclusively for business and for meeting clients.
- CC relevance: MEDIUM. CC works from home. Measure the office space carefully. A 150 sq ft room in a 1,200 sq ft apartment = 12.5% — perfectly defensible. Claiming 60% of a home = audit bait.

**9. Year-over-year income spikes or drops > 50%**
- CRA's delta analysis flags large year-over-year changes. Going from $6K in 2025 to $300K+ in 2026 is a massive spike.
- This alone does not trigger an audit, but it places the return in a higher-scrutiny queue.
- CC relevance: HIGH. The 2025-to-2026 income jump is dramatic. CRA will notice. Mitigation: ensure every dollar of 2026 income has a paper trail.

**10. Cash-intensive businesses with no clear paper trail**
- DJ income is cash-based. CRA has dedicated audit programs for cash businesses.
- CRA uses deposit analysis: total bank deposits minus explained sources = suspected unreported income.
- CC relevance: MEDIUM for DJ income. Every DJ gig payment should be invoiced and deposited, even cash payments. No cash under the mattress.

### Tier 3 — Moderate Audit Probability (10-25%)

**11. Inconsistent lifestyle vs reported income**
- CRA's net worth assessment (s.152(7)) compares your known spending to reported income. If you report $50K but buy a $60K vehicle, CRA notices.
- CC relevance: LOW currently. CC's lifestyle is modest. Will increase as income grows — do not make visible large purchases in years with low reported income.

**12. Vehicle expenses claimed at 100% business use**
- CRA almost never accepts 100% business use for a personal vehicle. Even 90% is aggressive.
- Requires a logbook showing every trip, distance, business purpose for at least one full year.
- CC relevance: LOW if CC doesn't claim vehicle expenses. If claiming, keep a 12-month logbook.

**13. Large charitable donations relative to income**
- Donations > 30-40% of net income are flagged. "Donation tax shelter" schemes are a CRA enforcement priority.
- CC relevance: LOW. CC is not making large charitable donations.

**14. SR&ED claims (20-30% audit rate)**
- SR&ED has one of the highest audit rates of any tax credit. At 43% refundable (Ontario), the incentive for abuse is high.
- CRA audits ~20-30% of SR&ED claims. First-time claimants have an even higher audit rate (~40%).
- CC relevance: FUTURE. When OASIS claims SR&ED, expect CRA review. Need detailed technical documentation of experimental development, technological uncertainty, and systematic investigation.

**15. Foreign income not reported**
- CRA receives CRS data from 100+ countries. Unreported foreign income is automatically detectable.
- CC relevance: MEDIUM. Wise USD income from Bennett (US client) must be reported. All Stripe revenue regardless of currency.

**16. Related-party transactions (TOSI territory)**
- Payments to family members, income splitting through corporations, management fees between related entities.
- CC relevance: LOW now. FUTURE if CC incorporates and pays dividends to family members (TOSI rules, s.120.4).

**17. Moving expenses claimed (s.62)**
- CRA heavily audits moving expense claims. Must move 40+ km closer to new work/business location.
- CC relevance: POTENTIAL for Montreal move (summer 2026). Collingwood to Montreal = ~560 km. The move qualifies if CC's business is in Montreal. Keep every receipt.

### Tier 4 — Lower but Real Audit Probability (5-10%)

**18. Late filing (s.162 penalties + extra scrutiny)**
- Late filers are automatically flagged for compliance review. Late filing is correlated with non-compliance — CRA knows this.
- Penalty: 5% of balance owing + 1%/month (max 12 months). Doubles for repeat offenders.
- CC relevance: MEDIUM. Self-employed deadline is June 15, but payment is due April 30. File on time every year.

**19. Meals and entertainment > industry norms**
- CRA only allows 50% of M&E. Claims significantly above industry norms trigger review.
- CC relevance: LOW. Minimal M&E expenses expected for a SaaS business.

**20. Rental losses every year**
- Persistent rental losses suggest personal use disguised as investment property.
- CC relevance: NONE currently. FUTURE if CC buys rental property.

**21. Home Buyers' Plan not repaid**
- HBP withdrawals require annual RRSP repayments over 15 years. Missing payments = added to income.
- CC relevance: NONE. CC has not withdrawn under HBP. FHSA is a better vehicle.

**22. Employment expenses claimed without T2200**
- Employees claiming work-from-home expenses need employer-signed T2200.
- CC relevance: LOW. CC is self-employed (T2125, not T2200). Only relevant for Nicky's if claiming employment expenses, which is unlikely.

**23. Business use of personal vehicle without logbook**
- Without a logbook, CRA can deny the entire vehicle deduction. Not just reduce it — deny it entirely.
- CC relevance: LOW unless claiming vehicle expenses. If claiming, a 12-month continuous logbook is mandatory.

**24. Capital gains not reported (CRA has T5008)**
- Investment dealers file T5008 showing proceeds. CRA matches against Schedule 3. If you sold securities and didn't report, automatic flag.
- CC relevance: MEDIUM for Wealthsimple (though CC has zero dispositions there currently). Kraken crypto dispositions must be on Schedule 3 or T2125.

**25. Investment carrying charges without corresponding income**
- Claiming interest on money borrowed to invest, but reporting no investment income. CRA infers the investments are not income-producing.
- CC relevance: LOW. Not currently borrowing to invest. FUTURE for Smith Manoeuvre or leveraged strategies.

---

## 3. CC-Specific Risk Assessment

### 3.1 CC's Risk Profile Summary

| Risk Factor | Severity | Mitigation Priority |
|-------------|----------|-------------------|
| Self-employed sole proprietor (T2125) | HIGH | Cannot change — accept higher baseline risk |
| First significant filing year (2025) | HIGH | File early, file accurately, over-document |
| Age 22 with $280K-$480K+ income | HIGH | Statistical outlier — CRA will look twice |
| 2025→2026 income spike ($6K → $300K+) | HIGH | Paper trail for every dollar |
| Crypto trader (Kraken) | HIGH | Full ACB tracking, report every disposition |
| No installment history | HIGH | Start installments immediately for 2026 |
| HST non-registration (above threshold) | CRITICAL | Register NOW if OASIS revenue > $30K |
| DJ income (cash-based) | MEDIUM | Invoice every gig, deposit all cash |
| Dual citizenship (UK) | MEDIUM | CRA cross-references with HMRC via CRS |
| International payments (Wise, Stripe) | MEDIUM | Reconcile platform records with T2125 |
| Home office deduction | MEDIUM | Measure, photograph, calculate precisely |
| No prior returns beyond 2024 | MEDIUM | File 2025 return promptly and accurately |
| Future SR&ED claims | FUTURE HIGH | Document technical uncertainty contemporaneously |
| Future incorporation | FUTURE HIGH | Transfer pricing, TOSI, management fees |

### 3.2 CC's Estimated Audit Probability (2026 Tax Year)

Based on the combination of risk factors above, CC's estimated audit probability for the 2026 tax year is **15-25%** — approximately 3-5x the average Canadian audit rate of ~5%.

**Primary drivers:**
1. Dramatic income spike (2025 → 2026) combined with first-time significant filing
2. Self-employment status (T2125 filers are audited at 2-5x the rate of employees)
3. Crypto trading on a platform where CRA has data
4. Age-income anomaly (22-year-old earning $300K+ in Ontario)

**How to reduce this to 5-10%:**
1. File early (don't wait until June 15 — file by April 30)
2. Pay installments on time (demonstrates compliance intent)
3. Register for HST and file on time
4. Report every income source with supporting documentation
5. Keep deductions reasonable relative to NAICS averages
6. Maintain a multi-year clean compliance record

### 3.3 Dollar Impact of Non-Compliance

If CRA audits and finds unreported income of $50,000:

| Component | Amount |
|-----------|--------|
| Federal tax on $50K (at ~33% marginal) | $16,500 |
| Ontario tax on $50K (at ~20.53% marginal) | $10,265 |
| CPP contributions on $50K | ~$3,500 |
| s.163(1) penalty (10% repeat offence) | $2,627-$5,000 |
| s.163(2) gross negligence (50% of tax) | $13,382 |
| Interest (3 years at ~8%) | $6,424 |
| **Total exposure (worst case)** | **$52,698** |

That is over 100% of the unreported amount. Non-compliance is mathematically irrational.

---

## 4. The Bulletproof Documentation System

### 4.1 Receipt Organization

**The system that works (30 minutes/month):**

1. **Digital capture:** Use a dedicated app (Dext, HubDoc, or even Google Drive) to photograph every receipt the day you get it. Paper receipts fade — thermal paper becomes blank within 1-2 years. CRA accepts digital copies since 2010 (IC05-1R1).

2. **Folder structure:**
   ```
   2026-Taxes/
   ├── Income/
   │   ├── OASIS-Invoices/
   │   ├── DJ-Invoices/
   │   ├── Nickys-T4/
   │   ├── Stripe-Statements/
   │   └── Wise-Statements/
   ├── Expenses/
   │   ├── Software-Subscriptions/
   │   ├── Home-Office/
   │   ├── Equipment/
   │   ├── Professional-Development/
   │   ├── Meals-Entertainment/
   │   ├── Vehicle/ (if claiming)
   │   └── Other-Business/
   ├── Crypto/
   │   ├── Kraken-Trade-History/
   │   ├── OANDA-Trade-History/
   │   ├── Wealthsimple-Statements/
   │   └── ACB-Calculations/
   ├── HST/
   │   ├── HST-Collected/
   │   └── ITC-Receipts/
   └── Banking/
       ├── RBC-Statements/
       └── Wise-Statements/
   ```

3. **Naming convention:** `YYYY-MM-DD_vendor_amount_category.pdf` (e.g., `2026-03-15_anthropic_20usd_software.pdf`)

4. **Monthly reconciliation:** Last Sunday of each month, reconcile bank/credit card statements against receipts. Flag any missing receipts and obtain duplicates immediately. This 30-minute monthly habit saves $5,000-$15,000+ in audit costs.

### 4.2 Mileage Logbook (CRA-Compliant)

If CC claims any vehicle expenses (business use of personal car):

**CRA's requirement:** A logbook recording every business trip with:
- Date
- Destination
- Purpose (client meeting, equipment purchase, DJ gig venue)
- Kilometres driven (odometer reading at start and end)

**Duration:** One full 12-month base year, then a 3-month sample year every subsequent year (if usage pattern is consistent within 10%).

**Template:**

| Date | Start KM | End KM | KM Driven | Destination | Business Purpose |
|------|----------|--------|-----------|-------------|-----------------|
| 2026-01-15 | 45,230 | 45,278 | 48 | Barrie | Client meeting - Bennett |
| 2026-01-17 | 45,278 | 45,310 | 32 | Collingwood Club | DJ gig - private event |

**Critical:** Start the logbook on January 1. CRA does not accept retroactive logbooks created during an audit. The logbook must be contemporaneous.

**CC recommendation:** If vehicle expenses are minimal, skip the claim entirely. The documentation burden is not worth a $500 deduction. Focus on home office and software, which are easier to defend.

### 4.3 Home Office Documentation

CRA allows home office deductions under two conditions (ITA s.18(12)):
1. The workspace is your **principal place of business** (> 50% of work time), OR
2. It is used **exclusively** for business AND for meeting clients regularly

**CC's position:** CC works from home full-time for OASIS. The home office is CC's principal place of business. This qualifies under condition 1.

**Required documentation:**

1. **Floor plan or sketch** — Draw or photograph the office space with measurements. A simple hand-drawn floor plan with dimensions is sufficient.

2. **Square footage calculation:**
   - Measure office room: length x width = office sq ft
   - Total home sq ft (from lease, listing, or measurement)
   - Business use % = office sq ft / total sq ft
   - Example: 150 sq ft office / 1,200 sq ft home = 12.5%

3. **Expenses to prorate:**
   - Rent (or mortgage interest + property tax if owned)
   - Utilities (heat, electricity, water)
   - Internet (100% if dedicated business line; otherwise prorate)
   - Home insurance
   - Maintenance and repairs (common areas only)

4. **Photograph the space** — Date-stamped photos of the office showing it is set up for business use. If CRA does a field audit, they will inspect the office. The photos should match reality.

5. **Form T2125, Part 5** — "Business use of home" section must be completed accurately.

**CC's estimated home office deduction:**
- Assume $1,200/month rent equivalent (or $0 if rent-free from parents — see below)
- If CC pays no rent: CC can only claim the proportionate share of expenses CC actually pays (utilities, internet). Cannot claim rent CC doesn't pay.
- If CC pays rent to parents: Must be at fair market value to be deductible. A sweetheart deal is fine, but if CRA asks for a lease, have one.
- Internet ($80/month x 12.5% = $120/year) + utilities (proportionate share)

**Warning:** If CC lives rent-free with parents, the home office deduction will be small (just proportionate utilities and internet). Do not inflate this.

### 4.4 Bank Account Separation

**Non-negotiable rule:** Separate business and personal banking.

CRA does not legally require separate accounts for sole proprietors, but in practice:
- Commingled accounts make it nearly impossible to prove business vs. personal expenses in an audit
- CRA will request 12 months of bank statements. If business and personal are mixed, they see everything — including personal spending that may not match reported income
- A separate business account creates a clean audit trail

**CC's action plan:**
1. **RBC business chequing** — All OASIS income deposits, all business expenses
2. **Wise business account** — USD income from Bennett/Stripe, USD business expenses
3. **Personal accounts** — Owner draws (transfers from business to personal)
4. **Never** pay personal expenses from business accounts or vice versa
5. **Monthly reconciliation** — All business account transactions categorized

### 4.5 Invoice Templates (CRA Requirements)

CRA requires invoices for all business income to substantiate T2125 revenue. Invoices must include:

1. Seller's legal name and business address
2. Buyer's name and address
3. Invoice number (sequential)
4. Date of invoice
5. Description of goods/services provided
6. Amount before tax
7. HST/GST charged (if registered) with registration number
8. Total amount
9. Payment terms

**Template for CC:**
```
OASIS AI Solutions
[CC's Address], Collingwood, ON, Canada
HST# [when registered]

INVOICE #2026-001
Date: March 27, 2026

Bill To:
Bennett [Last Name]
[Address]

Services: AI SaaS development and consulting — March 2026
Amount: $2,500.00 USD

HST (13%): $0.00 (zero-rated export — client outside Canada, ETA s.7/Sch. VI, Part V)

Total: $2,500.00 USD

Payment: Due upon receipt via Wise
```

### 4.6 Contractor vs Employee Documentation (Wiebe Door Test)

If CC hires subcontractors for OASIS, CRA may challenge whether they are employees (requiring source deductions) or independent contractors.

**Wiebe Door test (from *Wiebe Door Services v MNR* [1986] 3 FC 553):**

| Factor | Employee | Contractor |
|--------|----------|------------|
| Control | Employer controls how/when/where work is done | Worker controls own methods and schedule |
| Ownership of tools | Employer provides tools/equipment | Worker uses own tools |
| Chance of profit/risk of loss | No financial risk to worker | Worker bears financial risk |
| Integration | Worker is integral to employer's business | Worker operates own independent business |
| Intent | Parties intended employment relationship | Parties intended contractor relationship |

**CC's protection:** For any subcontractor, have a written Independent Contractor Agreement that specifies:
- Contractor controls their own schedule and methods
- Contractor uses their own equipment
- Contractor invoices for work (not paid on payroll)
- Contractor can work for other clients
- Relationship is not exclusive

Keep a copy of each contractor's invoice. If CRA reclassifies a contractor as employee, CC becomes liable for unremitted CPP, EI, and income tax source deductions — plus penalties.

### 4.7 T2125 Working Papers

The T2125 (Statement of Business or Professional Activities) is CRA's primary document for auditing self-employment income. Prepare working papers that tie every T2125 line to source documents:

**Revenue:**
- Line 8000 (Business income): Total of all invoices issued, reconciled against Stripe + Wise + direct payments
- Keep a revenue summary spreadsheet: date, client, invoice #, amount (CAD equivalent), payment method, FX rate used

**Expenses (sample lines):**
- Line 8521 (Advertising): Google Ads, Facebook Ads — receipts for each
- Line 8590 (Office expenses): Software subscriptions — Anthropic API, hosting, Serato, SoundCloud
- Line 8710 (Travel): Only if applicable — flights, hotels for client meetings
- Line 8811 (Telephone/internet): Business portion of phone and internet bills
- Line 9270 (Other expenses): Must have supporting detail for every dollar

**Working paper format:** A spreadsheet with columns: Date | Vendor | Description | Amount (foreign) | FX Rate | Amount (CAD) | T2125 Line | Receipt Location

### 4.8 Monthly Bookkeeping Routine (30 Minutes/Month)

| Task | Time | Frequency |
|------|------|-----------|
| Download bank/credit card statements | 5 min | Monthly |
| Categorize transactions | 10 min | Monthly |
| Photograph/file new receipts | 5 min | Monthly |
| Reconcile revenue (invoices vs. deposits) | 5 min | Monthly |
| Flag missing receipts, obtain duplicates | 5 min | Monthly |
| **Total** | **30 min** | **Monthly** |

This 30-minute routine produces audit-ready books at year-end. Skipping it means 10-20 hours of panic in April and gaps that CRA exploits.

---

## 5. The 6-Year Rule and Document Retention

### 5.1 General Rule: 6 Years from Notice of Assessment

ITA s.230(4) requires every person carrying on business to keep records and books of account for **6 years from the end of the last taxation year to which they relate**.

In practice, the clock starts from the date CRA issues the **Notice of Assessment (NOA)** for that tax year. If CC files the 2026 return in April 2027 and receives the NOA in June 2027, records must be kept until June 2033.

### 5.2 Category-Specific Retention Periods

| Record Type | Retention Period | Why |
|-------------|-----------------|-----|
| **T2125 business records** | 6 years from NOA | Standard ITA s.230(4) |
| **Employment records (T4)** | 6 years from NOA | Same |
| **Capital property (stocks, crypto, real estate)** | 6 years from the year of DISPOSAL | NOT from purchase. If you buy BTC in 2024 and sell in 2032, keep records until 2038. |
| **Crypto transaction history** | FOREVER | ACB calculation requires complete purchase history from first acquisition. Missing early transactions make accurate ACB impossible. |
| **CCA (depreciation) records** | 6 years from the year you claim the LAST deduction | UCC carries forward until fully depreciated or disposed |
| **Real estate purchase records** | 6 years from year of sale | Keep purchase docs forever until you sell |
| **RRSP/TFSA/FHSA contribution records** | 6 years from year of withdrawal/closure | Contribution room is cumulative |
| **HST/GST records** | 6 years from end of reporting period | ETA s.286(3) |
| **Moving expense records** | 6 years from NOA of the year claimed | s.62 claims are heavily audited |
| **Donation receipts** | 6 years from NOA | Required for DTC claims |
| **Corporate records (future)** | 6 years from dissolution or last T2 filing | Plus 2 years as a buffer |

### 5.3 Crypto: Why "Forever" Means Forever

Canada uses the **weighted-average ACB method** for crypto. This means every single purchase affects the ACB of every subsequent disposition. Example:

- 2021: Buy 0.5 BTC at $40,000 CAD. ACB = $20,000. Per-unit ACB = $40,000.
- 2022: Buy 0.3 BTC at $25,000 CAD. ACB = $27,500. Per-unit ACB = $34,375.
- 2026: Sell 0.2 BTC at $120,000 CAD. Proceeds = $24,000. ACB of 0.2 BTC = $6,875. Capital gain = $17,125.

If you delete the 2021 purchase record, you cannot calculate the correct ACB for the 2026 sale. CRA will deem ACB = $0 if you cannot prove it, resulting in the entire proceeds being taxable.

**CC action:** Export Kraken, Wealthsimple, and all wallet transaction histories NOW. Save them in multiple locations (cloud + local). Never delete historical crypto data.

### 5.4 What Happens If You Don't Have Records

If CRA requests records and you cannot produce them:

1. **CRA estimates income** — They use bank deposit analysis, third-party data (T-slips, exchange data), and statistical models. CRA's estimates are always higher than reality because they err on the side of the government.

2. **Burden of proof shifts to you** — Under *Hickman Motors v Canada* (1997 SCC), the initial onus is on the taxpayer to demolish the Minister's assumptions. Without records, you cannot.

3. **Gross negligence penalties apply** — s.163(2) penalties (50% of tax understated) are much easier for CRA to sustain when the taxpayer cannot produce records. The Federal Court has held that failure to keep adequate records can itself constitute gross negligence (*Venne v Canada* [1984] FC).

4. **No ITC claims** — Without receipts meeting ETA s.169 requirements, ITC claims are denied entirely.

**Dollar impact:** On $100K of estimated unreported income, CRA denial of records could cost $50K+ in tax, penalties, and interest.

### 5.5 Digital Record Requirements

CRA Information Circular IC05-1R1 confirms that electronic records are acceptable provided:

1. Records are maintained in an accessible, readable format
2. Records can be produced on request (paper printout or electronic file)
3. The taxpayer can demonstrate the integrity of the electronic records (no tampering)
4. Records are stored in Canada (or accessible from Canada — cloud storage is fine)

**Acceptable formats:** PDF, spreadsheet (Excel, Google Sheets), accounting software exports, bank statement downloads, screenshot images of receipts.

**Unacceptable:** Verbal records, memory, reconstructed records created after the fact (CRA can detect backdating through metadata).

---

## 6. CRA Installment Payment Strategy

### 6.1 When Installments Are Required

Under ITA s.156(1), you must pay quarterly installments if your **net tax owing** (after credits and withholdings) exceeds **$3,000** in:
- The current tax year, OR
- Either of the two preceding tax years

For Ontario residents, the Ontario threshold is also $3,000 in provincial tax. In practice, if your combined federal + Ontario tax owing exceeds $3,000, you need installments.

**CC's situation:** With projected 2026 income of $280K-$480K+ and minimal tax withheld at source (only Nicky's T4), CC will owe well over $3,000. Installments are mandatory starting March 15, 2026.

### 6.2 The Three Safe-Harbor Methods

CRA allows three methods for calculating installment amounts. If you pay at least the amount calculated under any one method, you avoid installment interest and penalties:

**Method 1: Prior-Year Method**
- Each quarterly installment = 1/4 of prior year's total tax owing
- CC's 2025 tax will be minimal (income ~$6K). So 2026 installments based on 2025 could be very small.
- Advantage: Smallest payments in a rapidly growing income year
- Risk: Large balance owing on April 30, 2027

**Method 2: Second-Prior-Year + Prior-Year (CRA's Default)**
- March 15 and June 15: each = 1/4 of tax from two years ago (2024)
- September 15 and December 15: each = (prior year tax - amount from first two installments) / 2
- CC's 2024 tax was nil or minimal. First two installments could be ~$0.
- This is what CRA calculates on your installment reminder.

**Method 3: Current-Year Method**
- Each quarterly installment = 1/4 of estimated current-year tax
- Requires accurate income projection
- Most accurate but most work

**CC's optimal strategy for 2026:**
- Use **Method 2** (CRA default). Since 2024 and 2025 taxes are minimal, the first two installments (March 15, June 15) will be very small or zero.
- This is perfectly legal — CRA's own safe-harbor rules allow it.
- The trade-off: a large balance owing by April 30, 2027. Plan for this — set aside 30-35% of all income received into a separate tax savings account.
- **CRITICAL:** Do not spend the tax money. CC will owe $60K-$120K+ by April 2027. That money must be segregated.

### 6.3 Avoiding Installment Interest

Installment interest is charged at the prescribed rate (currently ~7-8% annualized) on the shortfall between what you paid and what you should have paid, calculated quarterly.

**Key rules:**
1. If you use any of the three safe-harbor methods, NO installment interest applies — even if you owe a large balance at year-end.
2. CRA calculates installment interest for each quarter independently. Overpaying in Q1 offsets underpayment in Q2 (netting within the year).
3. Installment interest is NOT deductible.

**CC's action:** Calculate the safe-harbor amount for each quarter and pay exactly that. Do not overpay (you earn no interest on overpayments). Do not underpay (CRA charges ~8% interest on the shortfall).

### 6.4 Payment Methods

| Method | Processing Time | Notes |
|--------|----------------|-------|
| CRA My Account (online banking) | 1-3 business days | Preferred — instant confirmation |
| Interac Debit via My Account | Immediate | $25,000 daily limit at most banks |
| Pre-authorized debit | Scheduled | Set and forget — reduces missed payments |
| Cheque mailed to Sudbury tax centre | 5-10 business days | Not recommended — slow, no confirmation |
| Third-party payment service | Varies | Some charge credit card fees |

**CC recommendation:** Set up pre-authorized debit through CRA My Account. Automate the quarterly payments to avoid missed deadlines.

---

## 7. HST Compliance for SaaS

### 7.1 The $30,000 Threshold — CC Has Passed It

Under ETA s.148(1), registration is mandatory once taxable supplies exceed $30,000 in any four consecutive calendar quarters or in a single quarter.

**CC's OASIS revenue:** $2,982 USD/month = ~$4,100 CAD/month = ~$49,200 CAD/year. CC has exceeded $30K. Registration is mandatory.

**When to register:** Within 29 days of exceeding the threshold. If CC has already passed $30K in revenue, the registration deadline has likely already passed. Register immediately.

**Penalty for late registration:** CRA can assess HST on all taxable supplies made after the threshold was exceeded, plus interest and penalties. On $50K of unregistered revenue, the HST exposure is $6,500 (13% HST) plus penalties.

### 7.2 Place of Supply — Why Most of CC's Revenue Is Zero-Rated

This is the good news. Under ETA Schedule VI, Part V (exports), services supplied to non-resident customers who are not registered for HST/GST in Canada are **zero-rated** — meaning HST rate = 0%.

**CC's revenue breakdown:**
- **Bennett (US client):** Zero-rated. No HST charged. Bennett is a non-resident, not HST-registered.
- **Other US/international clients via Stripe:** Zero-rated. Same logic.
- **Canadian clients via Stripe:** HST applies. Must charge 13% (Ontario) on the invoice.
- **DJ gigs in Ontario:** HST applies (13%) on domestic services.

**Practical impact:** If 80%+ of CC's revenue is from US/international clients, CC will collect very little HST but can still claim ITCs on all Canadian business purchases. This means HST filing likely results in a **refund** (ITCs exceed HST collected).

### 7.3 Input Tax Credits (ITCs) — Getting 13% Back

Once HST-registered, CC can claim ITCs on the 13% HST paid on business purchases:

| Expense | HST Paid | ITC Claimable |
|---------|----------|---------------|
| Internet ($80/mo x 12.5% business) | $15.60/year | $15.60 |
| Software subscriptions ($200/mo) | $312/year | $312 |
| Computer equipment ($1,500) | $195 | $195 (one-time) |
| Phone ($100/mo x 80% business) | $124.80/year | $124.80 |
| Office supplies | Variable | Full HST on business portion |
| Professional services (accountant, lawyer) | Variable | Full HST |

**ITC documentation requirements (ETA s.169(4)):**
- Purchases < $100: vendor name, date, total amount (HST can be included)
- Purchases $100-$500: above plus HST amount or rate, vendor HST number
- Purchases > $500: above plus buyer's name and payment terms

### 7.4 Quick Method vs Regular Method

**Regular method:** Collect HST on taxable supplies, subtract ITCs, remit the difference.

**Quick method (ETA s.227):** Remit a flat percentage of revenue (8.8% for service businesses in Ontario), keep the difference. No ITCs claimed (except on capital purchases > $30K).

**Which saves CC more?**

With mostly zero-rated exports:
- **Regular method:** Collect ~$0 HST (exports), claim ~$1,000+ in ITCs = **net refund of ~$1,000+**
- **Quick method:** Remit 8.8% of domestic revenue only = smaller refund or small payment

**Verdict:** Regular method wins for CC because export-heavy revenue means low HST collected but full ITC recovery. Do NOT elect the Quick Method.

### 7.5 Filing Frequency

| Annual Revenue | Filing Frequency | Notes |
|----------------|-----------------|-------|
| < $1.5M | Annual (default) | File by June 15 if sole proprietor |
| $1.5M - $6M | Quarterly | Mandatory |
| > $6M | Monthly | Mandatory |
| Persistent refund position | Can request monthly | Get money back faster |

**CC recommendation:** Start with annual filing. If CC is consistently in a refund position (export-heavy), request monthly filing to get refunds 12x/year instead of 1x/year.

### 7.6 Crypto and HST

Financial instruments (including cryptocurrency) are **exempt financial services** under ETA s.123(1). No HST is charged on crypto purchases or sales. Crypto trading does not count toward the $30K threshold and does not require HST collection.

However, if CC provides crypto-related consulting services (e.g., advising clients on crypto), the consulting fee is a taxable supply subject to HST (unless the client is a non-resident).

---

## 8. Transfer Pricing for Solo Founders

### 8.1 When s.247 Applies

Transfer pricing rules under ITA s.247 apply to transactions between:
- A Canadian taxpayer and a non-arm's length non-resident, OR
- A Canadian corporation and its related entities (domestic or foreign)

**CC's current situation (sole proprietor):** s.247 generally does NOT apply to CC right now. CC is a sole proprietor transacting with arm's length clients (Bennett, Stripe customers). There is no related-party cross-border transaction.

**When s.247 will apply (post-incorporation):**
- If CC incorporates OASIS as a CCPC and creates a HoldCo
- If CC sets up an Irish IP company (Knowledge Development Box structure)
- If CC pays management fees between OpCo and HoldCo
- If CC licenses IP from an offshore entity

### 8.2 Related-Party Transactions (Post-Incorporation)

When CC incorporates, the following transactions require arm's length pricing:

**Management fees (OpCo → HoldCo):**
- Must reflect the fair market value of services actually provided
- HoldCo must actually provide services (strategic direction, administration, financial oversight)
- Document: written management services agreement, time records, market rate benchmarking
- CRA audit rate for management fee claims: ~15-20% for CCPCs

**Shareholder salary/dividends (CCPC → CC):**
- Salary must be reasonable for the work performed
- CRA tests: Would you pay an arm's length person this amount for this work?
- At $300K+ revenue, a $150K salary to the sole shareholder-employee is defensible. $300K might be questioned if the business has no other employees.

**Intercompany loans:**
- Loans from HoldCo to CC must bear interest at the CRA prescribed rate (currently ~5%)
- Interest-free loans trigger s.15(2) shareholder benefit — entire loan amount added to income
- Loan must have bona fide repayment terms and actually be repaid

### 8.3 Simplified Transfer Pricing for SMEs

CRA's Transfer Pricing Memorandum TPM-09 provides simplified compliance for small and medium enterprises:

- Businesses with < $1M in related-party cross-border transactions are subject to simplified documentation requirements
- No formal transfer pricing study required (but must still have reasonable pricing)
- CRA may request a functional analysis and comparables — keep basic records of how prices were set

**CC's action (future):** When incorporating, have the lawyer draft intercompany agreements at market rates. Keep a one-page memo documenting the arm's length rationale for each related-party transaction.

---

## 9. CRA Voluntary Compliance Programs

### 9.1 Voluntary Disclosure Program (VDP)

**Full details in `ATLAS_VDP_GUIDE.md`.** Summary:

- For unreported income, unfiled returns, or incorrect claims from prior years
- Must be voluntary (before CRA contacts you about the issue)
- Must be complete (disclose everything, not just part)
- General Program: Full penalty relief, partial interest relief (last 3 years only)
- Limited Program: Only gross negligence/criminal penalties waived, full interest charged
- **CC timing:** File VDP before CARF reporting starts (2026) if any crypto income was unreported in 2021-2024

### 9.2 Taxpayer Relief Provisions (s.220(3.1))

CRA can waive or cancel penalties and interest in cases of:
1. **Extraordinary circumstances** — Natural disaster, serious illness, death in family
2. **CRA actions** — CRA processing delays, incorrect information from CRA
3. **Financial hardship** — Inability to pay would cause undue hardship

**10-year limitation:** Relief is available for the 10 calendar years preceding the request.

**CC relevance:** If CC files late or misses installments due to legitimate circumstances (e.g., CRA My Account login issues preventing payment), file a Taxpayer Relief request to waive penalties and interest.

### 9.3 Advance Income Tax Ruling

For complex structures (incorporation, IP licensing, Crown Dependencies migration):

- CRA provides a binding ruling on the tax consequences of a proposed transaction
- Fee: $10,000-$30,000+ depending on complexity
- Timeline: 6-12 months
- **When to use:** Before implementing a Crown Dependencies structure or Irish IP company. The ruling provides certainty that CRA will not challenge the structure later.
- **CC timing:** Not needed now. Consider when income exceeds $300K+ and multi-jurisdiction structures are implemented.

### 9.4 Pre-Ruling Consultation (Free)

Before paying for a formal ruling:
- Call CRA's Business Enquiries line (1-800-959-5525) for informal guidance
- File a written technical interpretation request (free, but non-binding)
- CRA publishes these as "Technical Interpretations" — search CRA's website for relevant precedents
- Timeline: 3-6 months for a written interpretation

### 9.5 CPA Liaison Officer Program (Free)

CRA provides free liaison officers to help small businesses understand their tax obligations:

- Available to new businesses (< 3 years old) with revenue < $1M
- Officer visits your business (or calls) to review your record-keeping
- NOT an audit — no penalties or reassessments result from the visit
- Identifies compliance issues before they become audit problems
- **CC eligibility:** Yes. OASIS is < 3 years old with revenue < $1M.
- **CC recommendation:** Request a liaison officer visit in late 2026 after the first full year of operations. It is free insurance against compliance gaps.

### 9.6 What to Disclose Voluntarily vs. Stay Quiet About

| Situation | Action | Reasoning |
|-----------|--------|-----------|
| Unreported crypto income from prior years | VDP immediately | CRA will find it via exchange data — better to disclose first |
| Missed T1135 filing | VDP if T1135 was required | $25/day penalty is automatic; VDP eliminates it |
| Minor calculation errors on a filed return | T1-ADJ request | Not significant enough for VDP; simple correction |
| Aggressive but defensible tax positions | Stay quiet | If you have a reasonable basis, CRA must prove you wrong |
| Undocumented home office claim | Fix going forward, don't amend | Amending to reduce draws CRA attention; just document properly next year |
| HST not registered when required | Register now, file voluntarily | Late registration with voluntary filing demonstrates good faith |
| Cash DJ income not reported | VDP if material (> $1K) | CRA cash-business audit programs are active |

**General principle:** Disclose when CRA will inevitably find out (exchange data, CRS, platform reporting). Stay quiet when the position is defensible and CRA has no independent data source.

---

## 10. Digital Nomad / Cross-Border Compliance

### 10.1 CRA Residency Determination

CRA determines tax residency based on the **totality of facts**, not a single test. The two forms CRA uses:

- **NR73** — Determination of Residency (Leaving Canada): Filed when emigrating
- **NR74** — Determination of Residency (Entering Canada): Filed when immigrating

These are optional but provide certainty. CRA's ruling is binding (unless facts change).

### 10.2 Factual vs Deemed vs Non-Resident

| Status | How Determined | Tax Obligation |
|--------|---------------|----------------|
| **Factual resident** | Residential ties to Canada (home, spouse, dependants) | Taxed on worldwide income |
| **Deemed resident** | Present in Canada 183+ days in a year with no factual ties | Taxed on worldwide income |
| **Factual non-resident** | Severed all significant residential ties | Taxed only on Canadian-source income |
| **Deemed non-resident** | Treaty tie-breaker rules override factual residency | Taxed per treaty provisions |

### 10.3 Residential Ties — What CRA Weighs

**Primary residential ties (most important):**
1. **Dwelling place in Canada** — Owned or rented home available for your use
2. **Spouse or common-law partner in Canada**
3. **Dependants in Canada** — Children, elderly parents you support

**Secondary residential ties:**
1. Personal property in Canada (furniture, car, clothing)
2. Social ties (club memberships, religious organizations)
3. Economic ties (Canadian bank accounts, credit cards, investments)
4. Government ties (provincial health insurance, driver's license)
5. Mailing address, PO box, or safety deposit box in Canada
6. Canadian passport (not determinative but noted)

**CRA's weighting:** Primary ties are dispositive. If you maintain a dwelling in Canada available for your use, CRA will almost certainly consider you a factual resident — even if you spend 300 days abroad.

### 10.4 The 183-Day Rule Myth

**The 183-day rule does NOT mean what most people think.**

- Spending fewer than 183 days in Canada does NOT automatically make you a non-resident
- Spending more than 183 days does NOT automatically make you a resident
- The 183-day rule only applies to **deemed residency** under ITA s.250(1)(a) — it catches people who are not factual residents but spend too much time in Canada
- A person with a home, spouse, and bank accounts in Canada is a factual resident even if they spend 364 days abroad

**CC's situation:** As long as CC has a dwelling available in Canada (living with parents), a Canadian bank account, provincial health insurance, and a driver's license, CC is a factual Canadian resident regardless of days spent abroad.

### 10.5 Treaty Tie-Breaker Rules

When two countries both claim you as a tax resident, the applicable tax treaty determines which country has primary taxing rights:

**Canada-UK Treaty (Article 4(2)) — Tie-Breaker Order:**
1. **Permanent home** — Where do you maintain a permanent home? If in both countries, proceed to:
2. **Centre of vital interests** — Where are your personal and economic relations closer? (family, social, occupational, political, cultural). If inconclusive:
3. **Habitual abode** — Where do you spend more time? If inconclusive:
4. **Nationality** — Which country's citizen are you? (Both = inconclusive, proceed to:)
5. **Mutual agreement** — The two countries' tax authorities negotiate

**CC's path (Collingwood → IoM/UK):**
- To be treated as non-resident of Canada under the treaty, CC must:
  1. Establish a permanent home in IoM/UK
  2. Sever or weaken the Canadian permanent home (not just travel — actually give up the dwelling)
  3. Move centre of vital interests (clients, social life, business operations) to IoM/UK
  4. Spend more time in IoM/UK than Canada

### 10.6 Non-Resident Withholding Tax (Part XIII)

Once CC becomes a non-resident, any Canadian-source income is subject to **Part XIII withholding tax** at 25% (default rate), reduced by treaty:

| Income Type | Default Rate | Canada-UK Treaty Rate |
|-------------|-------------|----------------------|
| Dividends (from Canadian corp) | 25% | 15% (5% if > 10% ownership) |
| Interest | 25% | 0% (most types) |
| Royalties | 25% | 0-10% |
| Pension/annuity | 25% | 0-15% |
| Capital gains on Canadian property | Taxable at regular rates | Generally exempt (except real property) |

### 10.7 Departure Return (s.128.1) — Deemed Disposition

When CC ceases to be a Canadian tax resident, ITA s.128.1 triggers a **deemed disposition** of most property at fair market value. This means:

**What is deemed disposed:**
- All securities (stocks, ETFs, mutual funds)
- Cryptocurrency (all BTC, SOL, LTC, ATOM — deemed sold at FMV on departure date)
- Business goodwill (value of OASIS client relationships, recurring revenue)
- Options, interests in trusts, other property

**What is exempt:**
- Canadian real property (taxed when actually sold)
- RRSP/TFSA/FHSA (remain tax-sheltered)
- Canadian business property used in a Canadian business

**Tax on departure:**
If CC has $500K in crypto gains and $200K in OASIS goodwill at departure:
- Capital gains: $700K x 50% inclusion = $350K taxable
- Tax (at ~50% marginal): ~$175,000

**Deferral option:** ITA s.220(4.5) allows posting security (letter of credit or acceptable guarantee) to defer payment until the property is actually sold. This is critical for unrealized crypto gains — CC should not have to sell BTC to pay departure tax on paper gains.

### 10.8 CC's Montreal to UK/IoM Path — Compliance Steps

**Phase 1: Montreal Move (Summer 2026)**
1. Update address with CRA, banks, and provincial agencies
2. Obtain Quebec health insurance (RAMQ) — lose OHIP within 3 months
3. File 2026 return with Ontario residency for part of year, Quebec for remainder
4. Provincial tax optimization: if moving mid-year, income is allocated by days of residency in each province

**Phase 2: Pre-Departure Preparation (When Income > $150K)**
1. Calculate departure tax exposure (deemed disposition of all property)
2. Maximize TFSA/FHSA/RRSP contributions before departure (these survive departure)
3. Consider crystallizing capital losses before departure to offset departure gains
4. Review all contracts for Canadian-source income that will be subject to Part XIII withholding
5. File NR73 with CRA to get a residency determination

**Phase 3: Departure**
1. File departure return (s.128.1 deemed disposition)
2. Sever all primary residential ties (give up dwelling, cancel provincial health insurance)
3. Close or convert Canadian bank accounts to non-resident status
4. Establish permanent home in IoM/UK
5. Notify CRA of new address and non-resident status
6. Post security under s.220(4.5) to defer departure tax if applicable
7. Register for IoM/UK tax as applicable

---

## 11. CRA Penalties and Interest Reference

### 11.1 Late Filing Penalties

| Situation | Penalty | ITA Section |
|-----------|---------|-------------|
| **Late T1 filing (first offence)** | 5% of balance owing + 1%/month (max 12 months) = max 17% | s.162(1) |
| **Late T1 filing (repeat offender)** | 10% of balance owing + 2%/month (max 20 months) = max 50% | s.162(2) |
| **Late T2 (corporate) filing** | Same structure as T1 | s.162(1) |
| **Late HST/GST filing** | 1% of balance + 0.25%/month (max 12 months) | ETA s.280.1 |
| **Late T1135** | $25/day (max $2,500) per T1135 | s.162(7) |
| **Late T1135 (gross negligence)** | $500/month (max $12,000/year) per T1135 | s.162(10) |
| **Failure to file T1135 (knowingly)** | $1,000/month (max $24,000) | s.162(10.1) |

**CC's exposure if 2026 return filed late:**
- Projected tax owing: $80K-$150K (at $280K-$480K income)
- Late by 1 month: $80K x 6% = $4,800 (first offence)
- Late by 6 months: $80K x 11% = $8,800
- Late by 12 months: $80K x 17% = $13,600

**The math is clear: never file late.** Even if you cannot pay, file on time. The filing penalty is on the balance owing — if you file on time, the penalty is $0 regardless of whether you've paid.

### 11.2 Gross Negligence Penalty

**s.163(2):** 50% of the tax attributable to the false statement or omission, PLUS 50% of the excess credits claimed.

**What constitutes gross negligence:**
- *Venne v Canada* (1984 FC): "A high degree of negligence tantamount to intentional acting, an indifference as to whether the law is complied with or not"
- Failing to keep records when you know you should
- Not reporting income from an exchange that sent you a T-slip
- Claiming personal expenses as business expenses when the distinction is obvious
- Consistent pattern of underreporting over multiple years

**What does NOT constitute gross negligence:**
- Honest mathematical errors
- Misunderstanding a complex tax provision (if you took reasonable steps to comply)
- Relying on professional advice that turned out to be wrong (if the advisor was qualified and you disclosed all facts)

**CC's protection against s.163(2):**
1. Hire a qualified CPA for tax preparation (creates "due diligence" defense)
2. Keep complete records (impossible to claim gross negligence when records are meticulous)
3. Report all income, even if you're not sure of the exact amount (report high if uncertain)
4. Document any uncertain tax positions and the reasoning behind them

### 11.3 False Statement Penalty (Third-Party)

**s.163.2:** Applies to anyone who makes, participates in, or counsels a false statement on a return. Penalty: $100,000 or 50% of tax sought to be avoided, whichever is greater.

This targets tax preparers, advisors, and promoters of aggressive schemes. CC's risk here is minimal as a taxpayer, but it means CC should be cautious about which tax advisors to use — an advisor who promotes "too good to be true" schemes may be the one who gets penalized, and the underlying position may be reassessed.

### 11.4 Installment Interest

| Situation | Rate | Compounding |
|-----------|------|-------------|
| Underpaid installments | Prescribed rate + 4% (currently ~7-8%) | Compounded daily |
| Overpaid installments | Prescribed rate only (~3-4%) | Applied as offset only |
| Balance owing after filing | Prescribed rate + 4% | Compounded daily from April 30 |

**Key asymmetry:** CRA charges ~8% on underpayments but credits only ~3-4% on overpayments. Underpaying is more expensive than overpaying, but overpaying ties up cash.

**CC's optimal strategy:** Pay the minimum safe-harbor amount for each installment. Set aside the remainder in a high-interest savings account (currently ~4-5% at EQ Bank or similar) to earn interest until April 30 filing.

### 11.5 Director Liability (s.227.1) — Post-Incorporation

Once CC incorporates, CC becomes personally liable as a director for:
- Unremitted source deductions (CPP, EI, income tax withheld from employees)
- Unremitted HST/GST
- Trust fund amounts

**Due diligence defense (s.227.1(3)):** A director is not liable if they "exercised the degree of care, diligence and skill to prevent the failure that a reasonably prudent person would have exercised in comparable circumstances."

**CC's protection:** Once incorporated, ensure payroll and HST remittances are handled by a payroll service or automated accounting system. Set up pre-authorized debits for all remittances.

### 11.6 Criminal Penalties (ITA s.238-239)

| Offence | Penalty | Prison |
|---------|---------|--------|
| Tax evasion (s.239(1)) | 50-200% of tax evaded | Up to 5 years |
| Making false statements (s.239(1)(a)) | $1,000-$25,000 fine | Up to 2 years |
| Willful failure to file (s.238(1)) | $1,000-$25,000 fine | Up to 12 months |
| Destroying records (s.238(2)) | $1,000-$25,000 fine | Up to 12 months |

**CRA's criminal prosecution bar is high.** CRA has filed zero criminal charges for crypto tax evasion to date. Criminal prosecution requires intent (mens rea), which is harder to prove than negligence. However, the bar drops when taxpayers actively conceal income, use nominee accounts, or destroy records.

**CC's criminal risk:** Essentially zero, as long as CC files returns and reports income. Aggressive optimization is not evasion. Failing to report income when CRA has exchange data could escalate to gross negligence but would only reach criminal territory with active concealment.

---

## 12. The Annual Compliance Calendar for CC

### January
- [ ] Download all T4s from CRA My Account (or request from employers by Jan 31)
- [ ] Download Kraken annual trade history CSV (all transactions for prior year)
- [ ] Download OANDA annual trade history
- [ ] Download Wealthsimple tax documents (T5, T5008 if applicable)
- [ ] Export Stripe annual revenue report
- [ ] Export Wise annual transaction report
- [ ] Compile DJ income records (all invoices/receipts for prior year)
- [ ] Start ACB calculation for crypto dispositions
- [ ] Begin organizing receipts (if not done monthly throughout the year)

### February
- [ ] Gather all T-slips (wait until Feb 28 — issuers must file by this date)
- [ ] Cross-check T-slips against CRA My Account (My Account shows all slips CRA has received)
- [ ] Calculate home office deduction (sq ft measurement + expense proration)
- [ ] Calculate CCA (depreciation) for equipment
- [ ] Compile all software subscription receipts
- [ ] **RRSP contribution deadline: March 1** — make contribution before cutoff if using RRSP strategy
- [ ] FHSA contribution: can contribute any time before Dec 31, but earlier = more tax-free growth
- [ ] Begin tax return preparation (T1, T2125, Schedule 3)

### March
- [ ] **March 1: RRSP contribution deadline for prior tax year deduction**
- [ ] **March 15: First quarterly installment due (if required)**
- [ ] File T1 return (no need to wait until June 15 — filing early triggers earlier NOA and benefit payments)
- [ ] Review prior year's Notice of Assessment when received — check for errors

### April
- [ ] **April 30: Tax PAYMENT deadline** (even though filing deadline is June 15 for self-employed)
- [ ] If return not yet filed, ensure payment is made by April 30 to avoid interest on balance owing
- [ ] Review and reconcile Q1 income against projections
- [ ] Update installment calculations if income is significantly higher or lower than projected

### May
- [ ] Review CRA Notice of Assessment (typically received 2-4 weeks after filing)
- [ ] Verify TFSA/RRSP/FHSA contribution room on My Account
- [ ] If any discrepancies on NOA, file T1-ADJ or notice of objection within 90 days

### June
- [ ] **June 15: Self-employed filing deadline** (if not filed in March/April — but ALWAYS aim to file by April 30)
- [ ] **June 15: Second quarterly installment due**
- [ ] HST annual return due (if annual filer) — June 15 for sole proprietors
- [ ] Mid-year tax planning review: are projected installments sufficient?

### July-August
- [ ] Mid-year financial review: income vs projections, expense tracking current?
- [ ] If income is significantly above projection, increase September installment
- [ ] Review any pending CRA correspondence

### September
- [ ] **September 15: Third quarterly installment due**
- [ ] Q3 income reconciliation
- [ ] Start thinking about year-end tax planning:
  - Can you accelerate deductions into the current year?
  - Can you defer income to the next year (if lower marginal rate expected)?
  - Are there unrealized capital losses to harvest?

### October
- [ ] **Start tax-loss harvesting analysis** — review all investment positions for unrealized losses
- [ ] Superficial loss rule: must wait 30 days before repurchasing same or identical property
- [ ] If harvesting, execute sales by late November to clear the 30-day window before Dec 31
- [ ] Review TFSA/FHSA room — plan contributions before year-end

### November
- [ ] Execute any planned tax-loss harvesting trades (before Nov 30 for 30-day clearance)
- [ ] Finalize year-end expense purchases (equipment, software annual subscriptions)
- [ ] Verify all installment payments have been made

### December
- [ ] **December 15: Fourth quarterly installment due**
- [ ] **December 31 deadlines:**
  - Last day for TFSA contributions (current year room)
  - Last day for FHSA contributions
  - Last day for charitable donations (current year receipt)
  - Last day to accelerate business expenses into current year
  - Last day for tax-loss harvesting (trades must settle by Dec 31 — execute by Dec 27-28 for T+2 settlement)
- [ ] End-of-year bookkeeping close: reconcile all accounts, categorize all transactions
- [ ] Export year-end crypto portfolio balances (for ACB tracking)
- [ ] Back up all financial records to cloud and local storage

---

## 13. Master Compliance Checklist

### Filing Compliance
- [ ] T1 return filed on time (by June 15 for self-employed, ideally by April 30)
- [ ] T2125 completed with accurate business income and expenses
- [ ] Schedule 3 completed for all capital gains/losses (crypto, securities)
- [ ] All T-slips reported (cross-check CRA My Account)
- [ ] HST return filed (if registered)
- [ ] T1135 filed (if foreign property cost > $100K CAD)
- [ ] Installment payments made on time (March 15, June 15, September 15, December 15)

### Income Reporting
- [ ] All OASIS revenue reported (Stripe + Wise + direct payments)
- [ ] All DJ income reported (including cash payments)
- [ ] All Nicky's employment income reported (T4)
- [ ] All crypto dispositions reported (Kraken, Wealthsimple, any wallet-to-wallet if taxable event)
- [ ] All OANDA trading gains/losses reported
- [ ] Foreign exchange gains/losses calculated on USD income
- [ ] Interest income reported (bank accounts, Wise)

### Deduction Documentation
- [ ] Home office: floor plan, measurements, expense calculation on file
- [ ] Software subscriptions: receipts for each service
- [ ] Equipment (CCA): purchase receipts, CCA schedule maintained
- [ ] Professional development: receipts and proof of business relevance
- [ ] Vehicle (if claiming): 12-month logbook, gas receipts, insurance, maintenance receipts
- [ ] Phone/internet: business use percentage documented
- [ ] OSAP interest: annual interest statement from NSLSC

### Record Retention
- [ ] All records stored digitally in organized folder structure
- [ ] Crypto transaction history exported and backed up (all-time, not just current year)
- [ ] Bank statements downloaded and saved (6+ years)
- [ ] Receipts photographed/scanned (no reliance on thermal paper originals)
- [ ] T2125 working papers linking each line to source documents

### Account Compliance
- [ ] Business and personal bank accounts separated
- [ ] HST registration in place (if revenue > $30K)
- [ ] CRA My Account set up and functioning
- [ ] CRA installment reminders reviewed against safe-harbor calculations
- [ ] TFSA/FHSA contributions within annual room limits

### Cross-Border Compliance
- [ ] All USD income converted to CAD at Bank of Canada rate on date received (or annual average)
- [ ] Wise USD account monitored against T1135 threshold ($100K CAD cost)
- [ ] No unreported foreign accounts or income
- [ ] CRS/AEOI implications considered for any new foreign accounts

### Ongoing Monitoring
- [ ] Monthly bookkeeping completed (30 minutes/month)
- [ ] Quarterly installment review (amounts still appropriate?)
- [ ] HST collected on Canadian-sourced services
- [ ] Revenue reconciliation: invoices issued vs. payments received vs. bank deposits
- [ ] Year-over-year expense ratios within industry norms (flag if > 2x prior year)

---

## Key Takeaways

1. **CRA knows more than you think.** Between slip matching, exchange data orders, CRS, CARF, and platform reporting, CRA has independent verification of almost every income stream. The era of underreporting is over.

2. **File early, file accurately, file completely.** The single most effective audit-prevention strategy is a clean, well-documented return filed before the deadline.

3. **The documentation is the defense.** In an audit, the taxpayer with receipts wins. The taxpayer without receipts loses. It is that simple.

4. **Installments signal compliance intent.** CRA treats taxpayers who pay installments on time as lower risk. The installment interest charges are small compared to the audit-prevention benefit.

5. **Separate your money.** Business account for business. Personal account for personal. Commingled accounts are audit accelerants.

6. **CC's biggest risks in 2026:** HST non-registration (register NOW), zero installment history (start Q1), and the dramatic income spike from 2025 to 2026 (document every dollar).

7. **Aggressive optimization is legal. Non-compliance is not.** CC can use every legal strategy in the tax code to minimize taxes. But every dollar of income must be reported, every deduction must be documented, and every filing must be on time.

---

> **Document statistics:** ~1,250 lines | **Cross-references:** `ATLAS_CRA_AUDIT_DEFENSE.md` (reactive defense), `ATLAS_VDP_GUIDE.md` (voluntary disclosure), `ATLAS_TAX_STRATEGY.md` (25-strategy playbook), `CRA_CRYPTO_ENFORCEMENT_INTEL.md` (crypto enforcement), `ATLAS_HST_REGISTRATION_GUIDE.md` (HST details), `ATLAS_INSTALLMENT_PAYMENTS.md` (installment calculation details)
> **Last updated:** 2026-03-27 | **Next review:** After 2026 federal budget (expected April 2026)
