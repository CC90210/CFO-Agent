# ATLAS Voluntary Disclosure Program (VDP) Guide

> **Compiled by:** ATLAS (CC's CFO Agent)
> **Date:** 2026-03-27
> **Scope:** Complete VDP playbook — eligibility, both tracks, application mechanics, crypto-specific considerations, cost-benefit analysis, and strategic timing
> **Jurisdiction:** Canada (Ontario) | **Taxpayer profile:** Self-employed sole proprietor, 22, active crypto trader (Kraken), OASIS AI Solutions
> **Authority level:** IC00-1R6 (Information Circular), Income Tax Act (ITA), Federal Court jurisprudence, CRA administrative policy
> **Supplements:** `CRA_CRYPTO_ENFORCEMENT_INTEL.md` (enforcement intel), `ATLAS_TAX_STRATEGY.md` (main playbook), `ATLAS_CRA_AUDIT_DEFENSE.md` (post-audit defense)

---

## Why This Document Exists

The CRA's crypto enforcement window is closing. CRA obtained Kraken user data via IRS court order (2023) plus Canada-U.S. Tax Convention Article XXVII data sharing. CARF (Crypto-Asset Reporting Framework) starts reporting in 2026 — after which every exchange will automatically transmit Canadian user data to CRA annually.

**The VDP window for crypto is effectively 2026 — and narrowing.**

CC trades crypto on Kraken. CC is a sole proprietor with multiple income streams. If any crypto income went unreported in 2021-2024, the VDP is the single most cost-effective remedy available under Canadian law. This document is the complete operational playbook.

---

## Table of Contents

1. [What is the VDP?](#1-what-is-the-vdp)
2. [The Five Eligibility Conditions (IC00-1R6)](#2-the-five-eligibility-conditions-ic00-1r6)
3. [General Program vs Limited Program](#3-general-program-vs-limited-program)
4. [The Application Process (Step by Step)](#4-the-application-process-step-by-step)
5. [Crypto-Specific VDP Considerations](#5-crypto-specific-vdp-considerations)
6. [Calculating Your Crypto VDP Amounts](#6-calculating-your-crypto-vdp-amounts)
7. [Penalty and Interest Framework](#7-penalty-and-interest-framework)
8. [Cost-Benefit Analysis — CC-Specific Scenarios](#8-cost-benefit-analysis--cc-specific-scenarios)
9. [When NOT to Use the VDP](#9-when-not-to-use-the-vdp)
10. [Strategic Timing](#10-strategic-timing)
11. [Professional Help — Tax Lawyer vs Accountant](#11-professional-help--tax-lawyer-vs-accountant)
12. [Key Statutory References](#12-key-statutory-references)
13. [Action Items for CC](#13-action-items-for-cc)

---

## 1. What is the VDP?

The **Voluntary Disclosure Program (VDP)** is a CRA administrative program under which taxpayers who come forward to correct past non-compliance before the CRA initiates contact can receive relief from penalties and partial relief from interest. The program is governed by **Information Circular IC00-1R6** ("Voluntary Disclosures Program"), which replaced IC00-1R5 effective March 1, 2018, following significant reforms.

### Core Principle

> You correct past errors on your own terms. In exchange, CRA waives or reduces penalties and limits interest charges. Criminal prosecution is taken off the table.

The VDP is entirely distinct from:
- **T1-ADJ (T1 Adjustment Request)** — for simple corrections where no penalty would apply
- **Objections (ITA s.165)** — for disputing an existing assessment
- **Taxpayer Relief (ITA s.220(3.1))** — for waiving interest/penalties after the fact, with a lower success rate

**The VDP is the proactive, penalty-eliminating path. Taxpayer Relief is the reactive, uncertain fallback.**

### Legislative Basis

The VDP has no explicit legislative basis — it is an exercise of the Minister's discretionary authority under **ITA s.220(3.1)** to waive or cancel penalties and interest. The program is entirely administrative, governed by IC00-1R6 and its predecessor circulars. This means:

- CRA retains discretion to deny a VDP application (rare, but possible in egregious cases)
- The Federal Court can review CRA's exercise of discretion if it is unreasonable (*Lanno v. Canada* [2005] FCA 153)
- The program survives government changes because it is built into CRA's operational framework, not statute

---

## 2. The Five Eligibility Conditions (IC00-1R6)

All five conditions under IC00-1R6, paragraph 27, must be satisfied. Failure on any one disqualifies the application.

### Condition 1 — Voluntary

**The disclosure must be made before CRA enforcement action begins.**

IC00-1R6, paragraph 28:

> A disclosure is voluntary if it is initiated before the taxpayer is aware of any CRA enforcement action being taken against them for the matter disclosed.

**What disqualifies:**
| Disqualifying Event | Notes |
|--------------------|-------|
| CRA audit notice issued for the relevant tax years | An audit of Year X disqualifies VDP for Year X. If you are under audit for 2022 and 2023, you can still VDP 2021 and prior years — but CRA may roll the audit into those years. |
| CRA letter requesting information about the specific issue | A general compliance letter is NOT automatically disqualifying — a targeted inquiry about unreported crypto IS. |
| CRA has contacted CC about crypto specifically | Check if any CRA correspondence references crypto, Kraken, or trading activity. |
| Enforcement action commenced (search warrant, requirement to produce) | Automatic disqualification. |
| CC knows CRA is about to contact her (credible information) | Disqualifying under IC00-1R6 if she delays specifically because she knows CRA is coming. |

**The CRA exchange data question:** CRA having obtained bulk Kraken data through the IRS court order does NOT automatically disqualify CC. The disqualifier is CRA specifically identifying CC and initiating enforcement against her file. Bulk data possession ≠ enforcement action. However, the risk that CC's file has already been flagged increases materially with each passing quarter. See Section 10 (Strategic Timing).

**Practical test:** Has CC received any CRA letter, notice, or phone call referencing her crypto trading, Kraken account, or capital gains from digital assets? If no — the voluntary condition is likely satisfied.

### Condition 2 — Complete

**The disclosure must be complete. Partial disclosures are rejected or result in loss of relief.**

IC00-1R6, paragraph 32:

> A disclosure must be complete. This means the taxpayer must provide full and accurate facts relating to all inaccuracies or omissions for all tax years that are part of the disclosure.

**What this requires for crypto:**
- ALL unreported crypto activity across ALL years, not just selected transactions
- ALL exchanges (Kraken, Coinbase, DEX activity, any other platform)
- ALL crypto-related income types: spot gains, futures gains, staking rewards, airdrops, DeFi income
- If CC traded on multiple platforms, every platform must be disclosed
- If staking rewards were received on-chain, those are includable even if never cashed to fiat

**Practical implication:** Do not attempt to disclose Kraken 2023 gains while leaving out Coinbase 2022 activity. CRA VDP officers are experienced and will look for consistency. Incomplete disclosures can be revoked, resulting in full penalty exposure with no benefit.

### Condition 3 — Involves a Penalty

**The information must be subject to a penalty under the ITA.**

This condition is almost always satisfied for unreported income. Key penalties for unreported crypto:

| Penalty | ITA Section | Applies When |
|---------|------------|--------------|
| Late-filing penalty | s.162(1) | Return filed after due date |
| Repeated failure to report income | s.163(1) | Same income type unreported twice in 4 years |
| Gross negligence penalty | s.163(2) | Knowingly or under gross negligence failed to report |
| False statements penalty | s.163(2) | Intentional misstatement |

If no penalty applies (e.g., a simple math error with no omission), CC should file a T1-ADJ instead — no VDP needed, no VDP benefit available.

### Condition 4 — Information is at Least 1 Year Overdue

**The disclosure must relate to a tax year or period that ended at least one year before the date of the VDP application.**

IC00-1R6, paragraph 30: The information at issue must have been **required to be provided** at least **one year prior** to the application date.

**For CC in 2026:**
- 2024 tax return (due April 30, 2025) — eligible if applying after April 30, 2026. For a March 2026 VDP application, 2024 is borderline — the 2024 return was due April 30, 2025, which is less than one year before March 2026. **Safest approach: include 2024 anyway with clear explanation.** CRA has administrative discretion to accept recent years.
- 2023 and prior — clearly eligible. 2023 return was due April 30, 2024 — more than one year before any 2026 application.
- 2022, 2021, 2020 — fully eligible.

**Normal reassessment period (ITA s.152(3.1)):** CRA generally has **3 years** from the date of the original assessment to reassess a return. **Exception:** For misrepresentation attributable to neglect, carelessness, or wilful default, CRA can go back **indefinitely** under **ITA s.152(4)(a)(i)**. For most crypto non-reporters, this exception applies — meaning CRA is not statute-barred. The VDP eliminates penalty risk regardless of how far back it goes.

### Condition 5 — Payment Included

**The estimated tax owing must accompany the VDP application or a payment arrangement must be proposed.**

IC00-1R6, paragraph 34:

> As a condition of accepting a disclosure, the taxpayer must include payment of the estimated taxes owing, or make a request for a payment arrangement at the time of filing.

**What this means practically:**
- Full payment with the application = fastest processing, best optics
- Payment arrangement = accepted if CC genuinely cannot pay in full. CRA VDP officers are instructed to accept reasonable installment proposals.
- Not making payment AND not proposing an arrangement = application may be rejected

**Interest continues to accrue on unpaid balances** even after VDP acceptance — full payment at time of filing minimizes total interest cost.

---

## 3. General Program vs Limited Program

Since March 1, 2018 (IC00-1R6), the VDP has two tracks. CRA assigns the track — but the taxpayer's disclosure narrative influences which track applies.

### Comparison Table

| Feature | General Program | Limited Program |
|---------|----------------|-----------------|
| **Penalties** | 100% waived | Not waived (assessed at normal rates) |
| **Gross negligence penalty (s.163(2))** | Waived | Not waived — but CRA agrees not to assess a HIGHER penalty beyond normal late-filing |
| **Interest relief** | Yes — 50% reduction, most recent 3 years only (see below) | No interest relief |
| **Criminal prosecution** | No | No |
| **Named publicly** | No | Possible in cases of significant public interest |
| **Audit risk post-VDP** | Lower (resolved) | Remains higher (CRA scrutinizes going forward) |

### Interest Relief — General Program Detail

Under the General Program, CRA provides partial interest relief:

- **50% reduction** on arrears interest charged under **ITA s.161(1)**
- Relief applies only to the **3 most recent tax years** included in the disclosure
- Interest on years beyond 3 years back is charged at the full prescribed rate + 4%
- The prescribed interest rate is set quarterly; as of Q1 2026 it is elevated (track CRA website for current rate)

**Example:** CC files a VDP in March 2026 covering 2021-2024. Interest relief applies to 2022, 2023, and 2024 (3 most recent). Interest on 2021 is charged at full rate.

### Which Track Applies to CC?

**General Program indicators (more favorable):**
- First-time non-compliance
- Unreported amounts due to confusion about crypto tax rules (legitimate — CRA guidance was sparse pre-2020)
- Amounts under $25,000-$50,000 total
- No evidence of deliberate evasion scheme
- No offshore structures used to conceal assets
- Prompt action once aware of the obligation

**Limited Program indicators (less favorable):**
- Intentional tax avoidance or planning to evade
- Use of nominees, trusts, or offshore accounts to hide assets
- Repeated prior non-compliance
- Amounts exceeding $250,000
- Professional advice obtained that warned of the obligation (and was ignored)
- Sophisticated taxpayer who clearly knew the rules

**For CC:** Given CC's age (22), the genuine complexity of crypto tax rules, and typical trading volumes, the General Program is the likely track. The narrative on Form RC199 should:
1. Describe the genuine confusion about how crypto trading is taxed in Canada
2. Reference the lack of clear CRA guidance prior to 2021
3. Note that upon learning of the obligation, CC came forward proactively
4. Avoid language suggesting deliberate concealment

**Do not say:** "I didn't report it because I thought I could get away with it."
**Do say:** "I was unaware that cryptocurrency dispositions constituted taxable events under Canadian tax law and did not report the transactions. Upon becoming aware of the obligation, I initiated this disclosure."

---

## 4. The Application Process (Step by Step)

### Step 1 — Pre-Disclosure Discussion (Optional but Strongly Recommended)

Before filing Form RC199, conduct an **anonymous pre-disclosure discussion** with the CRA VDP unit.

**Contact:** CRA VDP unit — 1-800-267-3311, or your local Tax Services Office
**Anonymous:** Yes — CRA will not ask for your name or SIN during a pre-disclosure call
**Purpose:**
- Confirm CRA has not already initiated enforcement action against your file
- Get CRA's preliminary view on which track your situation falls under
- Understand what documentation they will require
- Confirm the application will be accepted in principle before you disclose

**If engaging a tax lawyer:** The lawyer makes the pre-disclosure call on your behalf, protected by solicitor-client privilege. This is the preferred approach for amounts exceeding $10,000 (see Section 11).

**What to ask on the pre-disclosure call:**
1. "Has any enforcement action been initiated for [general description of issue — e.g., unreported investment income for the years 2021-2024]?"
2. "Would this situation qualify for the General Program or Limited Program?"
3. "What documentation will be required with the application?"
4. "Is there currently any compliance project or sector-specific audit initiative that would affect this application?"

Document the call: date, time, CRA officer's name/ID number, and the responses. This is evidence of good faith.

### Step 2 — Gather and Organize All Documentation

Crypto VDP documentation requirements are extensive. Do not file until this package is complete — incomplete applications are rejected or trigger requests that delay processing by months.

**Exchange Records**

| Document | Source | Notes |
|----------|--------|-------|
| Complete transaction history — all years | Kraken account portal (CSV export) | Include every trade, deposit, withdrawal |
| Staking reward history | Kraken Earn section | Each reward receipt = income event |
| Fiat on/off-ramp records | Bank statements (RBC/Wise) | Corroborates transaction dates and values |
| Any other exchange histories | Coinbase, DEX exports | Must be complete across all platforms |

**ACB Calculation Workbook**

Canada uses the **weighted-average Adjusted Cost Base (ACB)** method for crypto — not FIFO, not specific identification. The ACB calculation must be:
- Prepared on a per-asset basis (BTC pool, ETH pool, SOL pool, etc.)
- Updated after every acquisition and disposition
- Compliant with the **superficial loss rule** (ITA s.54 "superficial loss", ITA s.53(1)(f)) — losses are denied if the same crypto is repurchased within 30 days before or after the sale

Recommended tools: **Koinly** (connects to Kraken API, generates CRA-compliant reports), **CoinTracker**, or manual Excel workbook. Koinly generates a Schedule 3 equivalent report that maps directly onto the T1 return.

**Amended T1 Returns**

For each year covered by the VDP, prepare a complete amended T1 return showing:
- Original reported amounts
- Additions from the VDP (unreported crypto income or gains)
- Recalculated tax owing
- Net additional tax due

**Schedule 3 Amendments (Capital Gains)**

If the crypto is treated as capital property (investment position vs active trading):
- List each disposition on Schedule 3 (Capital Gains and Losses)
- Show proceeds, ACB, expenses (exchange fees), and net gain/loss
- Aggregate into the annual capital gains inclusion

**T2125 Amendments (Business Income)**

If CC's trading activity is determined to be **business income** (see Section 5 for the classification discussion):
- Report net trading profit on T2125 (Statement of Business or Professional Activities)
- Deduct allowable expenses (exchange fees, software subscriptions, hardware portion, internet, home office portion)
- 100% of net profit is taxable (vs 50% inclusion rate for capital gains)

**Payment or Payment Proposal**

Calculate total tax owing for all years. Prepare either:
- A cheque or bank transfer for the full amount (attach to RC199), OR
- A written installment proposal specifying amounts and dates

### Step 3 — Complete and File Form RC199

**Form RC199** — "Voluntary Disclosures Program (VDP) Application" — is the formal application document. Available at canada.ca/voluntary-disclosures-program.

**RC199 requires:**
- Full legal name, SIN, address
- Tax years involved (list each year separately)
- Type of information being disclosed (income? capital gains? information return?)
- Amount of unreported income or gain per year
- Explanation of circumstances — narrative explaining why the information was not reported
- Declaration that the disclosure is complete
- Signature

**Narrative section is critical.** This is where the General vs Limited determination is often made. Key elements to include:
1. How and when CC became aware of the tax obligation
2. Why it was not reported initially (confusion, lack of guidance, age/inexperience)
3. Steps taken to come into compliance (obtained proper calculation tools, engaged professional, etc.)
4. Commitment to full future compliance

File by **mail** to the applicable Tax Services Office (TSO) for CC's region (Southern Ontario TSO, or the TSO indicated on the RC199 instructions). Do not file online — the VDP application requires original signature and physical documentation.

**Include with RC199:**
- [ ] Amended T1 returns for each year
- [ ] Schedule 3 amendments (capital gains) and/or T2125 amendments (business income)
- [ ] ACB calculation workbook (complete, year-by-year)
- [ ] Exchange transaction history exports (all platforms, all years)
- [ ] Payment or written installment proposal
- [ ] Narrative explanation letter
- [ ] Copy of any pre-disclosure call documentation

**Send by registered mail** (Canada Post Xpresspost with tracking) and retain the delivery confirmation. This establishes the filing date, which is legally significant if CRA initiates contact after you mail but before they receive it.

### Step 4 — CRA Review (60-180 Days Typical)

After receipt, CRA assigns a **VDP officer** (different from an auditor — VDP officers are trained in program administration, not enforcement).

**What happens during review:**
1. VDP officer confirms all five eligibility conditions are met
2. Officer reviews documentation for completeness
3. Officer determines General vs Limited track
4. Officer may issue a **Request for Additional Information** (common — provide promptly)
5. Officer may contact CC's representative (or CC directly if no representative) with questions
6. Officer prepares a **VDP acceptance letter** (or rejection letter) and proposed reassessments

**Common reasons for delay:**
- Incomplete documentation (ACB workbooks missing years or assets)
- Missing exchange data for some platforms
- Payment not included or installment proposal not accepted
- Questions about business income vs capital gains characterization

**During review:** Do NOT contact the VDP unit repeatedly asking for status. Allow 60 days before a follow-up inquiry. Excessive contact can create friction.

### Step 5 — Resolution

Upon acceptance, CRA issues:

1. **Acceptance letter** confirming VDP terms (General or Limited, years covered)
2. **Notices of Reassessment** for each year — showing:
   - Additional tax assessed
   - Penalties assessed (General: $0 penalties; Limited: reduced penalties)
   - Interest charged (General: 50% reduction on most recent 3 years; full rate on older years)
   - Net amount owing after any payment already submitted
3. **Payment instructions** if balance remains after initial payment

**After receiving reassessments:** Pay any remaining balance promptly. Late payment of VDP-assessed amounts accrues interest at the prescribed rate and can technically revoke the VDP if CRA considers it non-compliance with the payment condition.

**Going forward:** All future returns must correctly report all crypto activity. A second VDP for the same type of income is possible but CRA will be skeptical. Repeated non-compliance post-VDP risks the Limited Program for any future disclosure.

---

## 5. Crypto-Specific VDP Considerations

### Business Income vs Capital Gains — The Most Important Classification Decision

The VDP application must characterize the unreported crypto as either **business income** (100% taxable, T2125) or **capital gains** (50% inclusion rate, Schedule 3). This characterization has massive financial consequences.

**Business income treatment (less favorable):**
- 100% of net profit taxable
- Superficial loss rule technically does not apply (losses fully deductible, but gains fully taxable)
- ITA s.9 — profit from an adventure in the nature of trade

**Capital gains treatment (more favorable):**
- 50% inclusion rate (ITA s.38(a)) — only half the gain is taxable
- Superficial loss rule (ITA s.54) applies to deny losses if repurchased within 30 days
- ITA s.39 — capital gain on disposition of capital property

**CRA's characterization factors** (from CRA Guide "Information for crypto-asset users and tax professionals," canada.ca; CRA IT-479R "Transactions in securities"):

| Factor | Suggests Business Income | Suggests Capital Gains |
|--------|-------------------------|----------------------|
| Frequency of trading | Daily/multiple times daily | Occasional, long-term holds |
| Holding period | Short-term (days/weeks) | Long-term (months/years) |
| Primary purpose | Profit from price movements (speculation) | Investment / store of value |
| Use of leverage | Yes (futures, margin) | No |
| Expertise applied | Technical analysis, automated strategies | Passive buy-and-hold |
| Resources devoted | Significant time, tools, software | Minimal |
| Volume relative to income | Large relative to other income | Small |

**For CC specifically:** CC runs ATLAS — an automated trading system using RSI mean reversion, EMA crossover, momentum, and other algorithmic strategies. CC trades daily on Kraken. This profile is strongly suggestive of **business income** treatment. CRA may independently characterize it as such. The VDP application should either:
1. **Accept business income treatment** — higher tax but lower audit risk, can deduct trading expenses
2. **Argue capital gains** — lower tax but higher risk CRA reassesses to business income post-VDP (which would void the penalty relief)

**Atlas recommendation:** Disclose as **business income** on T2125. The trading activity profile is too algorithmic and active to credibly sustain capital gains treatment under CRA scrutiny. Accept the higher rate in exchange for clean resolution. Deduct all allowable expenses (see below) to reduce the net.

**Deductible trading expenses (T2125):**
- Exchange fees and trading commissions (directly deductible)
- Subscription fees for data services, analysis tools (e.g., TradingView)
- Software and API access costs
- Home office deduction (proportional)
- Internet and phone (business use portion)
- Professional development (courses, books on trading)
- Hardware depreciation (CCA — computer used for trading)
- Bank fees on trading accounts

### Common Crypto VDP Scenarios Relevant to CC

**Scenario 1: Unreported Kraken spot trading gains**
Most common scenario. Every crypto-to-crypto swap AND crypto-to-fiat sale is a taxable disposition. Even swapping BTC/USDT on Kraken is a disposition of BTC at fair market value.

**Scenario 2: Unreported staking income (SOL, ETH, ATOM)**
ATLAS trades SOL and ATOM — both have staking mechanisms on Kraken Earn. Staking rewards received = income at FMV at time of receipt (CRA crypto guide, 2023; CRA Interpretation 2024-1031821I7, January 2025). If CC staked any assets on Kraken and received rewards, those were reportable as income.

**Scenario 3: Wrong cost basis method**
If CC or a prior accountant used FIFO instead of weighted-average ACB, the gains may be miscalculated. The VDP corrects this, potentially resulting in LOWER tax if the recalculation is favorable.

**Scenario 4: DeFi activity not reported**
Any Uniswap, Aave, Compound, or similar protocol use outside Kraken generates taxable events. See `ATLAS_DEFI_TAX_GUIDE.md` for detailed treatment.

**Scenario 5: Never filed a T1 at all for years with crypto gains**
If CC did not file a T1 return for any year between 2020-2023, the VDP covers the unfiled return. File late returns as part of the VDP package.

### CRA's Crypto Intelligence Infrastructure

Understand what CRA likely already knows when you file. This is not to discourage VDP — it is to illustrate why waiting is irrational.

| Intelligence Source | What CRA Knows | Timeline |
|--------------------|---------------|----------|
| IRS court order (Kraken, 2023) + Canada-U.S. Tax Convention Art. XXVII | CC's Kraken account profile, transaction history, cumulative volume | Data likely received by CRA in 2023-2024 |
| Coinsquare Federal Court order (2021) | Any Coinsquare activity by CC | Data transferred 2021 |
| Dapper Labs Federal Court order (2025) | Any NBA Top Shot / Flow blockchain NFT activity | Data transferred 2025 |
| CARF — Crypto-Asset Reporting Framework | ALL exchange activity globally, automated annual reporting | Starts 2026 filing year |
| Bank transaction monitoring (RBC/Wise) | Large fiat deposits not matching reported income | Ongoing |
| CRA blockchain analytics (Chainalysis contract) | On-chain transactions linked to KYC'd exchange accounts | Ongoing |

**The CARF deadline is existential for the VDP option:** Once CARF data flows (first reports covering 2026 activity, received by CRA in 2027), CRA will have a complete automated picture of every Canadian's crypto activity. At that point, crypto VDPs become reactive rather than proactive — and the voluntary condition becomes very difficult to satisfy.

---

## 6. Calculating Your Crypto VDP Amounts

### Step-by-Step ACB Calculation (Weighted-Average Method)

Canada requires the **weighted-average ACB** method. Every asset (BTC, ETH, SOL, etc.) is tracked in its own pool.

**Formula:**
```
ACB per unit = (Total cost of all acquisitions to date) / (Total units held)
Gain/Loss on disposition = (Proceeds) - (ACB per unit × units disposed) - (Transaction fees)
```

**Example — BTC Pool:**

| Date | Event | Units | Price (CAD) | Total Cost (CAD) | Running ACB/unit |
|------|-------|-------|-------------|-----------------|-----------------|
| 2022-03-01 | Buy | +1.00 BTC | $65,000 | $65,000 | $65,000 |
| 2022-09-15 | Buy | +0.50 BTC | $27,000 | $13,500 | $52,333 |
| 2023-01-10 | Sell | -0.75 BTC | $40,000 | — | — |

**2023-01-10 gain calculation:**
- Proceeds: 0.75 × $40,000 = $30,000
- ACB: 0.75 × $52,333 = $39,250
- **Capital loss: $30,000 - $39,250 = ($9,250)**

**Example — SOL Pool (with staking rewards):**

Each staking reward receipt creates:
1. Business income event at FMV at time of receipt (T2125 income)
2. New acquisition at that FMV (adds to ACB pool at cost = FMV at receipt)

This means staking rewards are taxed twice in a sense: once as income when received, once as capital gain/loss when ultimately sold. The ACB base from the income inclusion prevents double-taxation on the same gain.

### Tools for CC

| Tool | Cost | CRA Compatibility | Notes |
|------|------|------------------|-------|
| **Koinly** | ~$100-$200 CAD/year | Generates Schedule 3-equivalent, T2125 support | Connects to Kraken API, handles ACB automatically |
| **CoinTracker** | ~$100-$300 CAD/year | High | Similar to Koinly |
| **Crypto Tax Calculator** | ~$100-$200 CAD/year | High | Australian-origin, strong Canada support |
| **Manual Excel workbook** | Free | Exact | Most transparent for VDP — auditor can follow every calculation |

**Atlas recommendation:** Use **Koinly** to generate the initial calculation (import all Kraken API history), then verify the output against a manual spot-check of 10 large transactions. Submit both the Koinly report and the manual verification workbook with the VDP application. This demonstrates good faith and methodological rigor.

### Years to Include

If CC traded crypto from 2020 onward, include ALL years back to first transaction:

| Year | T1 Due Date | VDP Eligible | Notes |
|------|------------|--------------|-------|
| 2020 | April 30, 2021 | Yes | More than 1 year before 2026 application |
| 2021 | April 30, 2022 | Yes | Fully eligible |
| 2022 | April 30, 2023 | Yes | Fully eligible |
| 2023 | April 30, 2024 | Yes | Fully eligible |
| 2024 | April 30, 2025 | Borderline | Less than 1 year old — include anyway, note in narrative |

**Do not stop at 2021 because "it was too long ago."** CRA has unlimited reassessment authority for misrepresentation (ITA s.152(4)(a)(i)). Including 2020 in the VDP actually provides MORE protection — it locks in the VDP's penalty waiver for that year rather than leaving it open to CRA reassessment with full penalties.

---

## 7. Penalty and Interest Framework

Understanding exactly what the VDP eliminates is critical for cost-benefit analysis.

### Penalties the VDP Eliminates (General Program)

**ITA s.162(1) — Late-Filing Penalty:**
> 5% of unpaid tax at the filing deadline, plus 1% per complete month late, up to 12 months maximum
> Maximum total: 17% of unpaid tax

**ITA s.162(2) — Repeated Failure to File:**
> 10% of unpaid tax (first repeat) up to 50% (multiple repeats)
> Applies if CRA has previously demanded a return under s.150(2) and it was not filed

**ITA s.163(1) — Repeated Failure to Report Income:**
> 10% of the unreported amount (federal) + provincial equivalent
> Applies if the same type of income was unreported in both the current year AND any prior year within a 4-year window

**ITA s.163(2) — Gross Negligence Penalty:**
> 50% of the tax attributable to the unreported amount (federal only)
> The most severe civil penalty in the ITA — applies where the taxpayer "knowingly, or under circumstances amounting to gross negligence" failed to report
> For crypto non-reporters who are aware of the obligation: high risk of this penalty being applied

**ITA s.238 — Failure to File (Criminal):**
> Fine of $1,000-$25,000 and/or imprisonment up to 12 months
> VDP explicitly provides protection from criminal prosecution

### Interest the VDP Reduces (General Program)

**ITA s.161(1) — Arrears Interest:**
- Prescribed rate + 4% (currently elevated — check CRA quarterly rates)
- Compounds daily
- Runs from original due date (April 30 of the following year) to payment date
- VDP General Program: 50% reduction on the most recent 3 years only
- Interest on years beyond 3 most recent: charged at full rate

**Provincial interest:** Ontario also assesses interest on provincial tax owing. The VDP covers federal tax. Provincial relief follows automatically as the provinces generally accept federal VDP determinations.

---

## 8. Cost-Benefit Analysis — CC-Specific Scenarios

### Assumptions

- Ontario marginal rate used: ~43.4% combined federal + Ontario for income in the $49,020-$98,040 bracket (2024)
- Capital gains inclusion rate: 50% (for capital property treatment)
- Business income rate: full marginal rate
- Interest rate used: prescribed rate + 4% = approximately 7% annually (2024-2025)
- All scenarios assume General Program (penalties 100% waived)

### Scenario A — $5,000 Net Unreported Crypto Gains (2023-2024)

*Assumption: treated as business income at 43.4% marginal rate*

| Cost Component | Without VDP | With VDP (General) | Savings |
|---------------|-------------|-------------------|---------|
| Tax owing | $2,170 | $2,170 | $0 |
| s.162(1) late-filing penalty (17% max) | $369 | $0 | $369 |
| s.163(2) gross negligence penalty (50% of tax) | $1,085 | $0 | $1,085 |
| Arrears interest (7%, ~1.5 years avg) | $228 | $114 (50% relief) | $114 |
| **Total** | **$3,852** | **$2,284** | **$1,568 (41%)** |

### Scenario B — $15,000 Net Unreported Crypto Gains (2021-2024)

| Cost Component | Without VDP | With VDP (General) | Savings |
|---------------|-------------|-------------------|---------|
| Tax owing | $6,510 | $6,510 | $0 |
| s.162(1) late-filing penalty | $1,107 | $0 | $1,107 |
| s.163(1) repeated failure (if applicable) | $1,500 | $0 | $1,500 |
| s.163(2) gross negligence penalty | $3,255 | $0 | $3,255 |
| Arrears interest (full rate on 2021-2022, 50% relief on 2022-2024) | $1,200 | $700 | $500 |
| **Total** | **$13,572** | **$7,210** | **$6,362 (47%)** |

### Scenario C — $40,000 Net Unreported Crypto Gains (2020-2024, business income)

| Cost Component | Without VDP | With VDP (General) | Savings |
|---------------|-------------|-------------------|---------|
| Tax owing | $17,360 | $17,360 | $0 |
| s.162(1) late-filing penalties | $2,951 | $0 | $2,951 |
| s.163(1) repeated failure | $4,000 | $0 | $4,000 |
| s.163(2) gross negligence penalty | $8,680 | $0 | $8,680 |
| Arrears interest (blended — full on 2020-2021, 50% relief on 2022-2024) | $4,200 | $2,400 | $1,800 |
| **Total** | **$37,191** | **$19,760** | **$17,431 (47%)** |

### Scenario D — $40,000 But Under Audit (VDP Not Available)

If CC is already under audit and the VDP is not available, CRA will assess:
- Full tax ($17,360)
- Full gross negligence penalty ($8,680)
- Full late-filing penalties ($2,951)
- Full interest ($4,200)
- Total: $33,191

**And potentially:** Criminal prosecution referral (rare, but possible for large amounts with clear evasion intent). This scenario illustrates the value of acting before CRA makes contact.

### Professional Fees vs VDP Benefit

| Scenario | VDP Savings | Tax Lawyer Cost | Net Benefit |
|----------|------------|-----------------|-------------|
| Scenario A ($5K gains) | $1,568 | $2,000-$3,000 | Break-even or slight loss — consider DIY or accountant |
| Scenario B ($15K gains) | $6,362 | $3,000-$5,000 | $1,362-$3,362 net benefit |
| Scenario C ($40K gains) | $17,431 | $5,000-$10,000 | $7,431-$12,431 net benefit |

**Rule of thumb:** Engage a tax lawyer if:
- Total unreported gains exceed $15,000 (lawyer fees justified by savings)
- Any possibility of the Limited Program (lawyer's narrative framing helps argue for General)
- CRA has made ANY contact about crypto (lawyer needed immediately)
- Offshore accounts or non-disclosure of foreign assets involved

---

## 9. When NOT to Use the VDP

### Use a T1-ADJ Instead (Simple Corrections)

If the error is **not a deliberate omission but a calculation mistake**, file a **T1 Adjustment Request (T1-ADJ)** instead. No VDP is needed. Examples:
- Miscalculated ACB due to FIFO vs weighted-average confusion (no penalties apply — reasonable error)
- Missed a single deduction on T2125
- Forgot to include a T4A slip you only recently received

The T1-ADJ corrects the return. CRA may assess interest on the resulting balance but generally does not apply penalties for corrections that do not involve income omissions.

**Critical distinction:** If you omitted income entirely (didn't report crypto gains at all), that's a VDP situation. If you reported crypto gains but got the number wrong due to a methodology error, that may be a T1-ADJ situation.

### VDP is NOT Available If:

1. **CRA has already contacted you** about the specific issue — the voluntary condition fails
2. **You are currently under audit** for the relevant years — VDP cannot be used to resolve an ongoing audit
3. **The statute of limitations has passed AND CRA cannot reassess** — rare for fraud/misrepresentation, but if CRA is genuinely statute-barred (3-year normal period, no misrepresentation), you may not need to do anything. Consult a tax lawyer before concluding this.
4. **The information relates to a transaction CRA has already publicly identified** as abusive (listed transactions under ITA s.237.4) — Limited Program applies by default, no General Program available

### The "Just Pay and File" Option

For very small amounts (under $2,000 in unreported gains), particularly for recent years, it may be more practical to simply:
1. File an amended T1 with the corrected income
2. Pay the resulting tax
3. Hope CRA either doesn't notice or applies minimal penalties

CRA's administrative tolerance for small, isolated corrections is real — they are resource-constrained and generally do not aggressively pursue penalties on small first-time corrections. However, this approach:
- Provides no formal protection
- Leaves penalty exposure open
- Does not generate a VDP acceptance letter (which is protective documentation)
- Is not recommended for amounts above $3,000-$5,000 or for multi-year non-compliance

**Atlas position:** For any multi-year crypto non-compliance or any amount above $5,000, use the VDP. The formal penalty waiver is worth the administrative cost.

---

## 10. Strategic Timing

### The CARF Cliff

The single most important timing factor is **CARF implementation** (Crypto-Asset Reporting Framework — OECD standard, adopted by Canada). CARF requires crypto exchanges to automatically report every Canadian user's crypto activity to the CRA annually.

**CARF timeline:**
- Canada has committed to CARF implementation effective for the **2026 tax year**
- First CARF reports (for 2026 activity) will be transmitted to CRA in **early 2027**
- Once CRA has automated 2026 crypto data, a VDP covering 2026 becomes impossible (CRA will already have the data)
- **More critically:** The existence of CARF data for 2026 means CRA can cross-reference against 2021-2025 data (which it already has from the Kraken IRS order) and identify discrepancies

**The practical conclusion:** File the VDP **before the end of 2026**, and ideally in Q1 2026 (January-March), while CARF has not yet been activated and while the VDP unit is less busy.

### The Kraken Data Exposure Window

The IRS court order compelling Kraken to provide user data was executed in **November 2023**. The IRS shared relevant Canadian-resident data with the CRA under the Canada-U.S. Tax Convention. CRA's crypto audit team had time in 2024-2025 to process this data and identify files for review.

**What this means for timing:**
- If CRA had CC's file on its radar and initiated action, a VDP filed in early 2026 may still satisfy the voluntary condition — CRA's possession of raw data is not the same as initiating enforcement action against CC specifically
- However, the longer the delay, the higher the risk that CC's file gets flagged from the Kraken data
- **Every month of delay increases the probability of disqualification**

### Q1 Processing Advantage

CRA VDP unit processing volumes follow tax season patterns:
- **January to March:** Low volume — fastest processing (60-90 days)
- **April to June:** Very high volume (tax season + filing deadlines) — slowest processing (120-180 days)
- **July to September:** Moderate volume — 90-120 day processing
- **October to December:** Moderate volume — 90-120 day processing

Filing in **January or February** gets faster assignment, faster resolution, and faster peace of mind.

### Summary: Optimal VDP Filing Window

```
OPTIMAL:     January - March 2026     (fast processing, pre-CARF, pre-audit-season)
ACCEPTABLE:  April - September 2026   (CARF not yet active, but higher risk)
RISKY:       Q4 2026                  (CARF imminent, processing slow)
DANGER ZONE: 2027+                    (CARF active, CRA has automated data)
```

---

## 11. Professional Help — Tax Lawyer vs Accountant

### Why a Tax Lawyer, Not an Accountant

For VDP applications above $10,000, engage a **tax lawyer**, not an accountant. The distinction is critical:

| Professional | Privilege | VDP Role |
|-------------|-----------|---------|
| **Tax lawyer** | Full solicitor-client privilege — communications protected, CRA cannot compel disclosure | Makes anonymous pre-disclosure inquiry. Prepares narrative. Files application. Negotiates track. Protects CC from self-incrimination during the process. |
| **Accountant / CPA** | **No privilege** — CRA can compel an accountant to produce all communications with a client | Prepares the ACB calculations, amended T1 returns, and financial workbooks. Does NOT make strategy calls or communicate with CRA. |

**Practically:** The lawyer handles all CRA communication and strategy. The accountant (or Koinly) handles the number-crunching. This division of labor protects CC.

**Finding a tax lawyer:**
- Search: "voluntary disclosure program tax lawyer Ontario"
- Organizations: Canadian Tax Foundation (CTF) referral list, Ontario Bar Association Tax Law section
- Firms with dedicated VDP practices: Rotfleisch & Samulovitch PC (Toronto), Taxpage.com, Garber Tax Law

### Cost Estimates

| Complexity | Professional | Estimated Cost |
|-----------|-------------|----------------|
| Simple VDP (1-2 years, single exchange, < $10K tax) | Tax accountant | $1,500-$3,000 |
| Moderate VDP (2-4 years, multiple platforms, $10K-$30K tax) | Tax lawyer | $3,000-$7,000 |
| Complex VDP (5+ years, DeFi/staking/multiple assets, $30K+ tax) | Tax lawyer | $7,000-$15,000 |
| DIY (single year, simple spot trading, < $5K tax) | Self-prepared | $200-$500 (Koinly + filing costs) |

**VDP is still financially positive** at all complexity levels when the penalty savings exceed professional fees (see Section 8 analysis).

### DIY Viability

If unreported gains are under $5,000 and confined to a single year of simple spot trading on one exchange:
1. Export Kraken CSV
2. Run through Koinly to calculate weighted-average ACB gains
3. Prepare amended T1 with corrected Schedule 3 (or T2125)
4. Complete RC199 with clear narrative
5. Send by registered mail with payment

The CRA's RC199 guide is well-written and the application is straightforward for simple situations. The risk of DIY errors increases with transaction volume, DeFi activity, or multi-year complexity.

---

## 12. Key Statutory References

| Reference | Title | Relevance |
|-----------|-------|-----------|
| **IC00-1R6** | Voluntary Disclosures Program | Governing information circular for the VDP — all eligibility conditions, two tracks, application process |
| **ITA s.220(3.1)** | Waiver of penalties and interest | Statutory authority for Minister to grant VDP relief |
| **ITA s.150(1)** | Filing requirements | Obligation to file T1 annual return |
| **ITA s.152(3.1)** | Normal reassessment period (3 years) | Standard limitation period for CRA reassessment |
| **ITA s.152(4)(a)(i)** | Extended reassessment period | Unlimited reassessment for misrepresentation — applies to intentional non-reporting |
| **ITA s.161(1)** | Arrears interest | Interest on unpaid tax from original due date |
| **ITA s.162(1)** | Late-filing penalty | 5% + 1%/month to 17% max |
| **ITA s.162(2)** | Repeated failure to file | 10%-50% for repeat offenders |
| **ITA s.163(1)** | Repeated failure to report income | 10% federal penalty, second offence within 4 years |
| **ITA s.163(2)** | Gross negligence penalty | 50% of tax on unreported amount — most severe civil penalty |
| **ITA s.238** | Failure to file — criminal | Fine and/or imprisonment; VDP provides immunity |
| **ITA s.231.2(2)** | Unnamed persons requirements | Authority for CRA exchange data orders (Coinsquare, Dapper Labs orders) |
| **ITA s.38(a)** | Capital gains inclusion | 50% inclusion rate for capital property dispositions |
| **ITA s.39** | Definition of capital gain/loss | Capital gain = proceeds - ACB - expenses |
| **ITA s.9** | Business income | Adventure or concern in the nature of trade = business income |
| **ITA s.54** | Superficial loss | 30-day repurchase rule denying capital losses |
| **ITA s.53(1)(f)** | ACB adjustment for superficial loss | Adds denied superficial loss to ACB of repurchased property |
| **ITA s.248(1)** | Definition of "disposition" | Broad — includes crypto-to-crypto swaps |
| **Canada-U.S. Tax Convention, Art. XXVII** | Exchange of information | Basis for IRS-CRA Kraken data sharing |
| *Lanno v. Canada* [2005] FCA 153 | Federal Court review of VDP | CRA discretion subject to judicial review if unreasonable |
| *Amicarelli v. The King* 2025 TCC 185 | First Bitcoin TCC ruling | Bitcoin gains = capital property; loss claims analyzed |
| *MNR v. Coinsquare Ltd.* FC 2021 | Exchange data court order | UPR mechanism, confirms CRA can obtain bulk exchange data |

---

## 13. Action Items for CC

### Immediate (This Week)

- [ ] **Check CRA My Account** — Review correspondence inbox for any letters mentioning crypto, Kraken, digital assets, or capital gains discrepancies. If any such letter exists, call a tax lawyer immediately before taking any other action.
- [ ] **Export all Kraken transaction history** — Download complete CSV for 2020-2025. Keep a local backup. This is step one regardless of whether the VDP proceeds.
- [ ] **List all platforms ever used** — Write down every crypto exchange, wallet, and DeFi protocol CC has used since first crypto transaction. This determines the scope of the VDP.

### Short-Term (Next 2-4 Weeks)

- [ ] **Run Koinly ACB calculation** — Import Kraken API key into Koinly (read-only permissions). Generate the tax report for all years. Review the net gain/loss numbers.
- [ ] **Assess total unreported amounts** — Cross-reference Koinly output against what was reported on T1 returns for 2020-2024. Calculate the gap.
- [ ] **Decide: DIY or professional** — If total unreported gains exceed $10,000 or involve multi-year DeFi activity, engage a tax lawyer. Budget $3,000-$7,000 for professional fees (a deductible business expense in the year paid).
- [ ] **Make pre-disclosure inquiry** (lawyer or directly) — Call CRA VDP unit anonymously to confirm no enforcement action is pending.

### VDP Filing (Q1 2026 — Optimal Window)

- [ ] Complete ACB workbooks for all years
- [ ] Prepare amended T1 returns (with corrected Schedule 3 or T2125)
- [ ] Draft RC199 narrative — clear, non-incriminating explanation
- [ ] Calculate tax owing + interest estimate (use CRA prescribed rate calculator)
- [ ] Prepare payment or installment proposal
- [ ] File by registered mail with tracking — retain proof of filing date

### Post-VDP

- [ ] Implement proper crypto bookkeeping going forward — Koinly auto-sync to Kraken, monthly reconciliation
- [ ] Record staking rewards on receipt (FMV at time of receipt = income)
- [ ] Report all crypto activity on every T1 going forward
- [ ] Add crypto tax line items to Atlas's budget tracker

---

## Risk Summary

| Risk Factor | Current Risk Level | Risk With VDP Filed |
|------------|-------------------|-------------------|
| CRA penalty assessment for unreported crypto | HIGH | ELIMINATED |
| Gross negligence penalty (50% of tax) | HIGH | ELIMINATED |
| Criminal prosecution referral | LOW-MEDIUM | ELIMINATED |
| CRA audit post-2026 CARF data | VERY HIGH | MANAGED (VDP on file) |
| Public naming by CRA | LOW | ELIMINATED |
| Interest on unpaid tax | HIGH | REDUCED (50% on recent 3 years) |

**Bottom line:** The VDP is the single highest-return risk management action available to a Canadian crypto trader with unreported gains. The penalty elimination alone can represent 40-50% cost reduction on total liability. The CARF deadline makes 2026 the last practical window for most crypto traders. File early in the year, file completely, and include payment.

---

*Document compiled by ATLAS — CC's CFO Agent | March 2026*
*Supplements: `CRA_CRYPTO_ENFORCEMENT_INTEL.md` | `ATLAS_TAX_STRATEGY.md` | `ATLAS_CRA_AUDIT_DEFENSE.md` | `ATLAS_DEFI_TAX_GUIDE.md`*
*Review annually: IC00-1R6 is subject to CRA administrative updates. Verify current program terms at canada.ca/voluntary-disclosures-program before filing.*
