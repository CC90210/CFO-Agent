# ATLAS — US Tax Obligations for Canadian Business Owners

> **For:** Conaugh McKenna (CC), OASIS AI Solutions, Collingwood Ontario
> **Jurisdiction:** Canada (Ontario) resident earning USD from US clients
> **Last Updated:** 2026-03-27
> **Purpose:** Comprehensive guide for Canadian residents and businesses earning US-source income,
> receiving payments through US platforms (Stripe, Wise, PayPal), and navigating the Canada-US
> tax treaty. Universally applicable to any Canadian business owner with US revenue streams.
> All ITA references are to the *Income Tax Act (Canada)*, R.S.C. 1985, c.1 (5th Supp.) unless noted.
> All IRC references are to the *Internal Revenue Code (United States)* unless noted.

**Tags used throughout:**
- `[NOW]` — Actionable today for a Canadian sole proprietor earning USD
- `[FUTURE]` — Relevant upon incorporation, scaling, or structural changes
- `[OASIS]` — Specific to CC's actual situation
- `[WARNING]` — High-penalty or high-cost risk area
- `[COMMON MISTAKE]` — Errors Atlas sees repeatedly among Canadian freelancers/SaaS founders

---

## Table of Contents

1. [When Cross-Border Tax Issues Arise](#1-when-cross-border-tax-issues-arise)
2. [Canada-US Tax Treaty Deep Dive](#2-canada-us-tax-treaty-deep-dive)
3. [US Withholding Tax on Payments to Canadians](#3-us-withholding-tax-on-payments-to-canadians)
4. [1099 Reporting Issues](#4-1099-reporting-issues)
5. [US Investment Tax for Canadian Residents](#5-us-investment-tax-for-canadian-residents)
6. [Foreign Tax Credit Mechanism](#6-foreign-tax-credit-mechanism)
7. [US Sales Tax and State Tax Nexus](#7-us-sales-tax-and-state-tax-nexus)
8. [Canadian Corporations with US Clients](#8-canadian-corporations-with-us-clients)
9. [Stripe, Wise, and US Payment Platform Compliance](#9-stripe-wise-and-us-payment-platform-compliance)
10. [Snowbird Rules and Physical Presence](#10-snowbird-rules-and-physical-presence)
11. [Common Mistakes and How to Avoid Them](#11-common-mistakes-and-how-to-avoid-them)
12. [CC-Specific US Tax Checklist](#12-cc-specific-us-tax-checklist)

---

## 1. When Cross-Border Tax Issues Arise

### 1.1 The Core Principle

Canada taxes its **residents** on **worldwide income**. The US taxes based on **source of income**
and **citizenship**. When a Canadian earns income from a US source, both countries can potentially
claim the right to tax it. The Canada-US Tax Treaty (1980, as amended) exists to prevent double
taxation and allocate taxing rights.

**The question is never "do I owe Canadian tax?" (yes, always — you are a Canadian resident).**
**The question is "do I ALSO owe US tax?"**

For most Canadian freelancers, consultants, and SaaS companies selling to US clients: **No, you
do not owe US tax.** But there are forms to file, withholding to manage, and traps to avoid.

---

### 1.2 Scenario Matrix — When Issues Arise

| Scenario | US Tax Filing? | US Withholding Risk? | Canadian Reporting | CC Match? |
|----------|---------------|---------------------|-------------------|-----------|
| Canadian selling services to US clients remotely | No (treaty protection) | Low (if W-8BEN filed) | Report all income on T2125 | YES |
| Canadian with US payment processor (Stripe) | No | 1099-K possible | Report all revenue normally | YES |
| Canadian with US bank account (Wise USD) | No | None | T1135 if cost > $100K CAD | YES |
| Canadian receiving 1099-NEC from US client | Usually no | Possible IRS matching issue | Report income in Canada | POSSIBLE |
| Canadian with US stock investments | No (but withholding on dividends) | 15% on dividends (treaty) | Report dividends + claim FTC | FUTURE |
| Snowbird spending months in US | Maybe (Substantial Presence Test) | If treaty tie-breaker fails | Maintain Canadian residency docs | NO |
| Canadian digital nomad working from US | Possibly — depends on duration | If physically present in US while earning | Complex — get advice | NO |
| US citizen living in Canada | YES — always (worldwide taxation) | Already in US system | File both US and Canadian returns | NO |
| Canadian with US LLC | YES — FAPI disaster for Canadians | Complex | T1134 + FAPI accrual in Canada | NO |

---

### 1.3 CC's Specific Situation

CC earns USD from Bennett (US-based client) via Wise payment link. Stripe processes additional
client payments (US company). CC has no US office, no US employees, no physical presence in the
US, and performs all work from Canada.

**Bottom line for CC:** No US tax obligation. No US return required. But there are compliance
steps to take (W-8BEN, Stripe configuration, FX conversion) that prevent future headaches.

---

### 1.4 Canadian Selling Services to US Clients

This is the most common scenario and the one that applies to CC and the vast majority of
Canadian freelancers, consultants, and SaaS companies.

**The rule:** If you are a Canadian tax resident, performing services from Canada, selling to
US clients, you are taxed ONLY in Canada. The Canada-US Treaty (Article VII — Business Profits)
protects you. The US has no right to tax your income unless you have a "Permanent Establishment"
in the US.

**What you must do:**
- Report ALL USD income on your Canadian tax return (T2125 for sole proprietors)
- Convert USD to CAD using Bank of Canada exchange rate on date of receipt (or annual average)
- File W-8BEN with any US client who asks (or proactively, to prevent withholding)
- Confirm your Stripe account is registered as a Canadian business

**What you do NOT need to do:**
- File a US tax return (Form 1040-NR)
- Get a US Social Security Number
- Get an ITIN (unless you need to claim a refund of incorrectly withheld tax)
- Pay US federal or state income tax
- Collect US sales tax (unless you have economic nexus — see Section 7)

---

### 1.5 Canadian with US Payment Processors

Stripe, PayPal, and Square are US companies. Using them does NOT create a US tax obligation.
A payment processor is a conduit, not a business presence.

`[WARNING]` However, Stripe may issue Form 1099-K if your account is configured as a US account
(US address, US bank account for settlement). This creates an IRS matching problem even though
you owe no US tax. **Always set up Stripe as a Canadian business.** See Section 9.

---

### 1.6 Canadian with US Bank Accounts

Having a US-dollar bank account (e.g., Wise USD account) does NOT create a US tax obligation.
A bank account is not a Permanent Establishment. It is not "carrying on business" in the US.

**Canadian reporting obligation:** If the total cost of ALL your foreign property (bank accounts,
crypto on foreign exchanges, US stocks in non-registered accounts, etc.) exceeds $100,000 CAD
at any point during the year, you must file T1135. See `docs/ATLAS_FOREIGN_REPORTING.md` for
the complete T1135 guide.

`[OASIS]` CC's Wise USD balance (~$1,900 USD) is well below the $100K threshold. Monitor as
revenue scales — at $2,500 USD/mo from Bennett alone, the account could accumulate quickly if
not regularly converted to CAD or invested.

---

### 1.7 Canadian with US Investments

US stocks, ETFs, and real estate owned by Canadian residents carry specific withholding and
reporting obligations. Covered in detail in Section 5.

---

### 1.8 US Citizens Living in Canada

The US is one of only two countries (the other is Eritrea) that taxes based on **citizenship**,
not just residency. A US citizen living in Canada must file US tax returns (Form 1040) every year
regardless of where they live or earn income.

This does NOT apply to CC (Canadian and British citizen, NOT a US citizen). But if any future
Atlas/CFO agent client is a US citizen residing in Canada, they face:
- Annual US filing (Form 1040 + FBAR for foreign accounts > $10K USD)
- FATCA reporting (Form 8938) for foreign financial assets > $200K USD (for expats)
- Foreign Earned Income Exclusion (up to ~$126,500 USD for 2025) OR Foreign Tax Credit
- Potential double taxation on Canadian-source income if US rate exceeds Canadian rate (rare)
- Renunciation process costs $2,350 USD and triggers exit tax

---

## 2. Canada-US Tax Treaty Deep Dive

### 2.1 Overview

The Canada-United States Tax Convention (1980), as amended by five protocols (most recently 2007),
governs the allocation of taxing rights between the two countries. It is implemented in Canadian
law under the *Canada-United States Tax Convention Act, 1984* and in US law under the treaty's
self-executing provisions.

**Key principle:** The treaty REDUCES taxation — it never creates a tax obligation that would
not otherwise exist under domestic law. If domestic law does not tax something, the treaty
is irrelevant for that item.

---

### 2.2 Article VII — Business Profits (THE Key Article for CC)

> "The business profits of a resident of a Contracting State shall be taxable only in that
> State unless the enterprise carries on business in the other Contracting State through a
> permanent establishment situated therein."

**Translation:** CC's OASIS business profits are taxable ONLY in Canada, unless OASIS has a
Permanent Establishment in the US. No PE = no US tax on business profits. Period.

**What constitutes a Permanent Establishment (Article V):**

| Creates PE | Does NOT Create PE |
|-----------|-------------------|
| Fixed place of business in US (office, branch) | Occasional business trips to US |
| Employees regularly working in US | Using US payment processor (Stripe) |
| Dependent agent habitually concluding contracts in US | Having a US bank account (Wise) |
| Construction site > 12 months | Attending US conferences |
| Server you own/lease in US (debatable, but CRA/IRS position is yes) | Using US cloud hosting (AWS, Azure) |
| Warehouse with inventory in US | Storing data on US servers you don't own |

`[OASIS]` CC has NONE of the PE indicators. All work performed from Canada. No US office, no
US employees, no dependent agent. Treaty Article VII fully protects CC's business profits from
US taxation.

**Does visiting US clients create PE?**

Possibly, if the visits are **regular and sustained** and you are **concluding contracts** during
visits. Occasional business trips — even quarterly — do NOT create PE. The test looks at whether
the activity in the US is the core profit-generating activity vs. ancillary.

`[WARNING]` If you work from a US co-working space for several months, rent an office, or have
a US address on your business cards, you are creating PE indicators. Avoid this.

**Does a US Stripe account create PE?** No. Stripe is a third-party payment processor. Using
Stripe does not give you a "fixed place of business" in the US. CRA and IRS agree on this.

**Does a US bank account create PE?** No. A bank account is a passive financial arrangement,
not a place of business. Confirmed by both treaty interpretation and CRA guidance.

---

### 2.3 Article XIV — Independent Personal Services (Repealed, but context matters)

Article XIV was deleted by the Fifth Protocol (2007). Independent personal services income is
now covered under Article VII (Business Profits). The effect is the same: no PE = no US tax.

Older references may cite Article XIV. For services performed after 2008, Article VII controls.

---

### 2.4 Article XV — Employment Income (Dependent Personal Services)

> "Salaries, wages, and other similar remuneration derived by a resident of a Contracting State
> in respect of an employment shall be taxable only in that State unless the employment is
> exercised in the other Contracting State."

**Translation:** If a Canadian is employed (W-2 relationship) by a US company and physically
works in the US, the US can tax that employment income. If the Canadian works from Canada
(remote), Canada taxes it.

**Exception (Article XV(2)):** Even if the employment is exercised in the US, the US cannot tax
it if ALL three conditions are met:
1. The employee is present in the US for less than 183 days in any 12-month period
2. The remuneration is paid by an employer who is NOT a US resident
3. The remuneration is not borne by a PE the employer has in the US

`[OASIS]` CC is NOT an employee — CC is a self-employed business owner. Article XV does not
apply. But if CC ever takes a W-2 position with a US company while residing in Canada and
working remotely from Canada, the income is taxable ONLY in Canada.

---

### 2.5 Article X — Dividends

| Recipient | Treaty Withholding Rate | Notes |
|-----------|------------------------|-------|
| Individual (portfolio) | 15% | Standard rate on US stock dividends |
| Company owning 10%+ of voting stock | 5% | Reduced rate for substantial holdings |
| RRSP/RRIF | 0% | Special treaty provision — unique to Canada-US treaty |
| TFSA | 15% | US does not recognize TFSA as a pension — NO exemption |
| FHSA | 15% | Same as TFSA — not recognized as pension by US |
| Pension fund | 0% | Applies to registered pension plans |

`[NOW]` If CC holds US stocks, hold them in RRSP (0% withholding) rather than TFSA (15% withholding
that cannot be recovered). This is one of the most important investment allocation decisions for
Canadians holding US equities.

---

### 2.6 Article XI — Interest

**Treaty rate: 0% withholding** on most interest payments between Canada and US.

This means US bonds, GICs at US banks, and interest from US sources are paid to Canadian
residents without withholding. The income is still taxable in Canada at your marginal rate.

**Exception:** Certain contingent interest (interest linked to receipts, sales, income, or cash
flow) may be subject to withholding. Straightforward bank/bond interest is 0%.

---

### 2.7 Article XII — Royalties

**Treaty rate: 0% withholding** on royalties between Canada and US.

If CC licenses software (SaaS) to US clients, the payments are either:
- **Business profits** (Article VII) — if the software is a service (SaaS model). Most common.
- **Royalties** (Article XII) — if the payment is for the right to use intellectual property.

Either way: 0% US withholding for a Canadian resident without US PE.

`[OASIS]` CC's SaaS/consulting revenue from Bennett is business profits under Article VII,
not royalties. Even if characterized as royalties, the treaty rate is 0%.

---

### 2.8 Article XIII — Capital Gains

**General rule:** Capital gains from the disposition of property are taxable ONLY in the
country of residence.

**Exceptions:**
- **Real property:** Gains on US real estate are taxable in the US (FIRPTA — see Section 5.6)
- **Business property of a PE:** If the gain is from property forming part of a US PE
- **Shares deriving value from real property:** If >50% of share value comes from US real property
- **Stock options:** Generally taxed where services were performed

`[OASIS]` CC's crypto and stock gains are taxable ONLY in Canada. If CC ever buys US real
estate, the US can tax the gain on sale (FIRPTA withholding of 15% at closing, then
reconciled on US tax return — refund possible if actual gain is less).

---

### 2.9 Treaty Override and Domestic Law

**In Canada:** The treaty overrides the ITA to the extent of any inconsistency, because the
*Canada-United States Tax Convention Act, 1984* gives it force of law.

**In the US:** Under the "later-in-time" rule, if Congress passes a law after the treaty that
contradicts it, the later law prevails. In practice, the Canada-US treaty is well-respected and
overrides have been rare.

**Savings clause (Article XXIX(2)):** The US reserves the right to tax its own citizens and
residents as if the treaty did not exist (with specific exceptions). This is why US citizens
living in Canada cannot use the treaty to avoid US filing obligations.

---

### 2.10 Mutual Agreement Procedure (MAP) — Article XXVI

If Canada and the US both claim the right to tax the same income, you can invoke MAP. The
Competent Authorities of both countries (CRA Commissioner and IRS Commissioner) will negotiate.

**When to use MAP:**
- Double taxation not resolved by treaty provisions
- Tax assessed contrary to treaty provisions
- Transfer pricing disputes between related Canadian and US entities

**Practical reality:** MAP is slow (2-4 years), bureaucratic, and used mainly by large
corporations. For individual freelancers, the treaty provisions and FTC mechanism almost always
prevent double taxation without needing MAP.

---

## 3. US Withholding Tax on Payments to Canadians

### 3.1 The Default: 30% Withholding

Under IRC s.1441, any US person (individual or corporation) making a payment of "fixed or
determinable annual or periodical" (FDAP) income to a non-resident alien must withhold **30%**
and remit it to the IRS.

FDAP income includes: dividends, interest, rents, royalties, compensation for services
performed IN the US, and other fixed/determinable income.

`[WARNING]` The 30% rate is the DEFAULT. It applies when the US payer does not know whether a
treaty reduction is available. Filing a W-8BEN reduces this to the treaty rate (often 0%).

---

### 3.2 Treaty Reductions

| Income Type | Default (No W-8BEN) | Treaty Rate (With W-8BEN) | CC Relevant? |
|-------------|---------------------|--------------------------|--------------|
| Business profits (no PE) | 30% if mischaracterized | 0% | YES |
| Services performed in Canada | 30% if payer withholds | 0% | YES |
| Dividends (portfolio) | 30% | 15% | FUTURE |
| Interest | 30% | 0% | FUTURE |
| Royalties | 30% | 0% | POSSIBLE |
| Rent on US real property | 30% (on gross) | 30% (but can elect net basis) | FUTURE |

---

### 3.3 W-8BEN (Individuals) and W-8BEN-E (Entities)

**Form W-8BEN** (Certificate of Foreign Status of Beneficial Owner for United States Tax
Withholding and Reporting — Individuals):
- Filed by non-US individuals with US payers
- Claims treaty benefits to reduce or eliminate US withholding
- Valid for 3 calendar years from signing (year signed + 2 full years)
- Requires: name, country of citizenship, foreign TIN (SIN for Canadians), treaty article

**Form W-8BEN-E** (same, but for entities):
- Filed by non-US corporations, partnerships, trusts with US payers
- More complex — requires entity classification, beneficial owner information
- Used after CC incorporates OASIS as a CCPC

**How to fill out W-8BEN for CC's situation:**
- Part I, Line 1: Conaugh McKenna
- Part I, Line 2: Canada
- Part I, Line 3: Permanent residence address (Collingwood, ON)
- Part I, Line 5: Not needed unless CC has an ITIN
- Part I, Line 6a: SIN (Canadian equivalent of TIN)
- Part II, Line 9a: Canada
- Part II, Line 9b: Article VII (business profits)
- Part II, Line 9c: 0%
- Part II, Line 9d: Exempt from withholding under Article VII — services performed outside
  the US by a Canadian resident with no US permanent establishment
- Part III: Sign and date

`[NOW]` CC should prepare a W-8BEN and have it ready for Bennett or any US client who requests
one. Even if Bennett has not asked, submitting one proactively prevents future withholding
problems.

---

### 3.4 When US Clients SHOULD Withhold vs. When They DON'T Need To

**US clients SHOULD withhold (30% or treaty rate) when:**
- Paying for services performed IN the United States
- Paying dividends, interest, royalties, or rents to a non-resident
- No W-8BEN on file and income is FDAP

**US clients do NOT need to withhold when:**
- Paying for services performed OUTSIDE the United States by a non-resident
- A valid W-8BEN is on file claiming treaty exemption
- The income is business profits of a non-resident with no US PE

`[OASIS]` Bennett pays CC for services performed entirely in Canada. Even without a W-8BEN,
Bennett technically has no withholding obligation because the services are not performed in the
US and are not FDAP income. But having a W-8BEN on file is best practice — it protects both
parties and creates documentation.

`[COMMON MISTAKE]` Many US clients (especially small businesses without accountants) either:
(a) withhold 30% unnecessarily because they think they must, or
(b) issue a 1099-NEC to the Canadian thinking they are a US contractor.
Both are wrong. A W-8BEN prevents both problems.

---

### 3.5 Getting a Refund of Incorrectly Withheld Tax

If a US payer withholds tax on payments that should have been exempt under the treaty:

**Step 1:** Ask the payer to correct it. They can file an amended Form 1042-S and request a
refund from the IRS on your behalf. This is the fastest resolution.

**Step 2:** If the payer refuses or cannot correct, file **Form 1040-NR** (US Nonresident Alien
Income Tax Return) to claim a refund.
- You will need an ITIN (Form W-7) if you do not already have one
- Attach Form 1042-S showing the withholding
- Claim the treaty benefit on the 1040-NR
- The IRS will process the refund (typically 6-12 months)
- You can claim a foreign tax credit in Canada for any US tax that is NOT refunded

`[WARNING]` Filing a US tax return when not required creates a US filing obligation going
forward. The IRS may expect future returns. Only file 1040-NR if you actually need to recover
withheld funds AND the amount justifies the hassle.

---

### 3.6 ITIN — Individual Taxpayer Identification Number

**What:** A US tax processing number for individuals who are not eligible for a US Social
Security Number but need to interact with the IRS.

**When needed:**
- Filing Form 1040-NR to claim a refund
- Required by a US financial institution for account opening
- Required by a US payer as a condition of reduced withholding

**When NOT needed:**
- You have a W-8BEN on file with treaty benefits (W-8BEN uses your foreign TIN / Canadian SIN)
- You have no US filing obligation
- You do not have US-source income subject to withholding

**How to get one:** File Form W-7 with the IRS, either by mail or through an IRS-authorized
Certified Acceptance Agent (CAA). Processing takes 7-11 weeks.

`[OASIS]` CC does NOT need an ITIN unless incorrect withholding occurs that requires a
1040-NR filing.

---

### 3.7 EIN — Employer Identification Number

**What:** A US tax identification number for businesses (similar to a Canadian BN).

**When needed:**
- You have US employees
- You operate a US entity (LLC, Inc.)
- Some US platforms require one for account setup (usually can be avoided)

**When NOT needed:**
- You are a Canadian business selling to US clients remotely
- You are a Canadian sole proprietor with no US entity

`[OASIS]` CC does NOT need an EIN. Do not apply for one unless creating a US entity.

**Getting an EIN if needed:** File Form SS-4 with the IRS. Non-US applicants cannot use the
online application — must file by fax (3-4 weeks) or call IRS at 267-941-1099 (immediate,
during business hours).

---

### 3.8 CC's Situation: Bennett Pays via Wise — Is This an Issue?

No. Here is why:

1. **Bennett pays for services performed in Canada** — no US-source income
2. **Wise is a transfer mechanism**, not a tax-relevant entity in this context
3. **No W-8BEN is currently on file** — this is not a problem YET because:
   - Bennett is not withholding anything (correct behavior)
   - Bennett may not be issuing any US tax forms (correct if CC gave foreign address)
4. **But CC should submit a W-8BEN proactively** because:
   - It documents that CC is a foreign person (no 1099 required)
   - If Bennett hires an accountant, the accountant may ask for W-8BEN or start withholding
   - It takes 5 minutes and prevents months of headache later

---

## 4. 1099 Reporting Issues

### 4.1 When US Clients Issue 1099-NEC to Canadians

**They should NOT.** Form 1099-NEC (Nonemployee Compensation) is for payments to US persons.
Payments to non-US persons are reported on Form 1042-S (Foreign Person's US Source Income
Subject to Withholding), and ONLY if there was US-source income and withholding.

However, many US small business owners and even some accountants do not understand this
distinction. Common mistakes:

- Client collects CC's information on a W-9 (US form) instead of W-8BEN (foreign form)
- Client treats CC as a US contractor because payment is in USD
- Client's accounting software auto-generates 1099 for all vendors paid > $600

**The result:** A 1099-NEC is filed with the IRS showing income paid to CC, but CC has no
US tax return. The IRS computer sees an information return with no matching tax return and
may eventually send a notice.

---

### 4.2 1099-K from Stripe/PayPal

**Current US thresholds (2025-2026):**
- Form 1099-K is issued for US persons receiving > $600 in gross payments through payment
  card transactions or third-party network transactions
- Prior to 2023: threshold was $20,000 AND 200+ transactions

**For Canadians:** If your Stripe or PayPal account is set up as a **Canadian** account with a
**Canadian** address, you should NOT receive a 1099-K. These forms are for US persons.

`[WARNING]` If you set up Stripe with a US address or US bank account as your primary settlement
account, Stripe may treat you as a US person and issue a 1099-K. This creates an IRS matching
problem.

`[OASIS]` CC must verify that Stripe is configured with:
- Canadian business address (Collingwood, ON)
- Canadian business entity (OASIS AI Solutions, sole proprietor)
- Even if payouts go to Wise USD, the account profile should be Canadian

---

### 4.3 What to Do When You Receive a 1099

**Scenario:** CC receives a 1099-NEC or 1099-K from a US source.

**Do NOT panic. Do NOT file a US tax return just because you received a 1099.**

**Step-by-step:**

1. **Contact the issuer** and explain you are a non-US person. Provide your W-8BEN. Ask them to
   correct the filing by submitting a corrected 1099 (zeroed out) to the IRS.

2. **If the issuer corrects it:** Problem solved. Keep records of the correction.

3. **If the issuer refuses or cannot correct:**
   - You have no US tax filing obligation (assuming no PE and treaty protection applies)
   - The IRS may send a CP2000 notice (proposed assessment) matching the 1099 to your name
   - If you receive a CP2000, respond with a letter explaining you are a non-resident alien,
     attach your W-8BEN, and cite Article VII of the Canada-US Tax Treaty
   - If the amount is significant (>$10,000), consider having a US tax professional respond

4. **Report the income in Canada regardless.** The 1099 does not change your Canadian obligation.
   You owe Canadian tax on the income whether or not a 1099 was issued.

---

### 4.4 W-8BEN Blocks 1099 Issuance

When a US payer has a valid W-8BEN on file for a payee, they know the payee is a non-US person.
This means:
- **No 1099-NEC should be issued** (1099-NEC is for US persons)
- **No backup withholding** (28% backup withholding applies to US persons who fail to provide TIN)
- If withholding IS required (e.g., FDAP income), the payer reports on Form 1042-S instead

**This is the single most important reason to file W-8BEN with every US client.** It prevents
the entire cascade of 1099 problems, IRS matching issues, and potential notices.

---

### 4.5 IRS Matching — What Happens If 1099 Filed But No US Return Exists

The IRS Automated Underreporter (AUR) system compares information returns (1099s, W-2s) against
filed tax returns. If a 1099-NEC shows $30,000 paid to "Conaugh McKenna" but there is no US
return filed under that name/TIN, the system may:

1. **Do nothing** — if CC has no US TIN (no SSN, no ITIN), the AUR system may not be able to
   match the 1099 to anyone. This is common and often the end of it.

2. **Send a notice** — if there IS a TIN on the 1099 (e.g., the US client guessed or used a
   wrong number), the IRS may send a notice to the address on the 1099.

3. **Assess tax** — in rare cases, the IRS may assess a deficiency based on unreported income.
   This is correctable by responding with treaty documentation.

**Practical risk level for CC:** Low, assuming no US TIN is on file. But the W-8BEN eliminates
even this low risk entirely.

---

### 4.6 Practical Steps to Handle Incorrect 1099s

| Action | When | How |
|--------|------|-----|
| Provide W-8BEN to all US clients | NOW — before year-end | Download W-8BEN from IRS.gov, complete, email to client |
| Check Stripe account setup | NOW | Stripe Dashboard > Settings > ensure Canadian profile |
| Receive 1099? Contact issuer immediately | Within 30 days of receipt | Request corrected 1099 (zero amount) |
| Receive IRS notice? Respond with treaty claim | Within 60 days of notice | Letter + W-8BEN + Article VII citation |
| Keep records of all cross-border payments | Ongoing | Invoice copies, Wise transfer confirmations, W-8BEN copies |

---

## 5. US Investment Tax for Canadian Residents

### 5.1 US Stocks in Non-Registered Accounts

When a Canadian resident holds US stocks in a non-registered (taxable) brokerage account:

- **Dividends:** 15% US withholding tax (treaty rate). The Canadian broker handles this
  automatically if your account profile shows Canadian residency.
- **Capital gains:** 0% US tax. Gains are taxable ONLY in Canada.
- **Interest:** 0% US withholding (treaty rate).

The 15% US withholding on dividends is creditable against your Canadian tax via the Foreign Tax
Credit (Form T2209). See Section 6.

---

### 5.2 US Stocks in RRSP — The 0% Withholding Advantage

**This is the most valuable provision for Canadian investors in the Canada-US treaty.**

Under Article XXI(2) of the treaty, income earned in a "retirement arrangement" recognized by
both countries is exempt from US withholding. The IRS recognizes the RRSP (and RRIF) as a
qualifying retirement arrangement.

**Result:** 0% US withholding on dividends paid to stocks held in an RRSP.

**Practical implication:** US dividend-paying stocks (and US-listed ETFs holding dividend stocks)
should be held in your RRSP to maximize returns. The 15% withholding in a TFSA or non-registered
account is a permanent drag — in an RRSP, it is fully eliminated.

**Example:**
- $10,000 in US dividend ETF (2.5% yield) = $250/year in dividends
- In TFSA: $37.50/year lost to US withholding (15% of $250) — unrecoverable
- In RRSP: $0 lost — full $250 received
- Over 30 years at 7% growth: ~$3,400 difference on a $10,000 position

---

### 5.3 US Stocks in TFSA — The 15% Withholding Trap

`[WARNING]` The TFSA is NOT recognized by the US as a pension or retirement arrangement under
the treaty. US dividends paid to TFSA-held stocks are subject to the full 15% treaty rate
withholding, and this withholding is UNRECOVERABLE.

Why unrecoverable? Because the TFSA is tax-free in Canada — you do not report TFSA income on
your Canadian return. Since there is no Canadian tax on the income, there is no tax to apply the
Foreign Tax Credit against. The 15% is a permanent loss.

**Same applies to FHSA.** The US does not recognize the FHSA. 15% withholding, unrecoverable.

**Optimization rule:** Hold Canadian stocks (and international stocks via Canadian-domiciled ETFs)
in your TFSA. Hold US dividend-paying stocks in your RRSP.

---

### 5.4 US ETFs and PFIC Rules

**PFIC (Passive Foreign Investment Company)** rules are an IRS anti-deferral regime targeting US
persons who invest in foreign mutual funds and ETFs. PFICs are subject to punitive US taxation.

**Canadian residents do NOT need to worry about PFIC rules.** PFIC is a US tax concept that
applies to US taxpayers. Canadians buying US-listed ETFs (e.g., VTI, SPY, QQQ) on US exchanges
are not subject to PFIC rules.

`[WARNING]` The reverse IS a problem: US citizens living in Canada who buy Canadian-listed ETFs
(e.g., VEQT, XEQT) may trigger PFIC rules on those Canadian funds. This is a disaster for
US-Canadian dual citizens.

---

### 5.5 Canadian-Listed ETFs Holding US Stocks

When you buy a Canadian-listed ETF (e.g., XUU, VFV) that holds US stocks:

- **Layer 1:** The ETF itself suffers 15% US withholding on dividends received from US companies
- **Layer 2:** The ETF distributes the net amount to you — the withholding is embedded in the
  lower return, not shown explicitly on your tax slip
- **You cannot claim FTC** for the embedded withholding in a non-registered account because it
  is not shown on your T3/T5 slip as foreign tax paid

**Solution:** For large US equity positions in non-registered accounts, consider holding
US-listed ETFs directly (e.g., VTI instead of VFV). You pay the 15% withholding directly, it
appears on your tax slip, and you claim FTC. Net result: same or better than the embedded
withholding in a Canadian wrapper.

**In RRSP:** Holding US-listed ETFs directly eliminates the withholding entirely (0% treaty rate).
Holding Canadian-listed ETFs that hold US stocks still suffers the embedded 15%. The RRSP
exemption only applies to the direct holding, not the look-through.

---

### 5.6 US Real Estate — FIRPTA

**FIRPTA (Foreign Investment in Real Property Tax Act)** requires that when a non-US person sells
US real property, the buyer withhold **15% of the gross sale price** and remit it to the IRS.

**Key points:**
- This is a WITHHOLDING, not the final tax. The actual tax on the gain may be more or less.
- The seller files Form 1040-NR to report the actual gain and get a refund of excess withholding.
- Withholding can be reduced to 10% if the sale price is under $1,000,000 and the buyer intends
  to use as a residence.
- Canadian owners can also apply for a withholding certificate (Form 8288-B) BEFORE closing to
  reduce withholding to the expected tax on the actual gain.

**Canada's treatment:** The gain on US real estate is also taxable in Canada (worldwide income).
Canada gives a Foreign Tax Credit for the US tax paid under s.126 ITA, preventing double taxation.

---

### 5.7 US Estate Tax Exposure

`[WARNING]` US estate tax applies to non-resident aliens who own US-situs property at death.

**US-situs property includes:**
- US real estate
- US stocks (including in Canadian brokerage accounts — the stock is US-situs)
- Tangible personal property located in the US

**Exemption:**
- US citizens/residents: ~$13.61 million (2024, indexed) — effectively no estate tax for most
- Non-residents: **$60,000** only — this is shockingly low

**Treaty benefit (Article XXIX-B):** Canadian residents get a unified credit pro-rated based on
the ratio of US-situs assets to worldwide assets. Effectively, if your worldwide estate is under
~$13.61 million AND you are a Canadian resident, the treaty eliminates US estate tax in most
cases.

**Example:** CC has $500K in US stocks and $1.5M total worldwide estate.
- Without treaty: $500K - $60K exemption = $440K taxable at up to 40% = $176K estate tax
- With treaty: $500K/$1.5M = 33% of worldwide estate. Pro-rated credit covers it. Estate tax: $0.

`[NOW]` CC has negligible US assets. But as wealth grows, ensure the executor is aware of the
treaty benefit and files Form 706-NA if US-situs assets exceed $60,000 at death.

---

### 5.8 Qualified vs. Ordinary Dividends — Irrelevant for Canadians

US tax law distinguishes between "qualified dividends" (taxed at preferential capital gains rates)
and "ordinary dividends" (taxed at full ordinary rates). This distinction matters for US
taxpayers.

**For Canadian residents: this distinction is irrelevant.** All US dividends are reported on your
Canadian return as foreign income. Canada does not distinguish between qualified and ordinary US
dividends — they are all taxed as income (though eligible Canadian dividends receive a gross-up
and tax credit, US dividends do not).

---

## 6. Foreign Tax Credit Mechanism

### 6.1 The Concept

The Foreign Tax Credit (FTC) prevents double taxation. If you pay tax to a foreign country on
income that Canada also taxes, you can credit the foreign tax against your Canadian tax owing.

**Canadian authority:** ITA s.126

**Federal form:** T2209 — Federal Foreign Tax Credits
**Provincial form:** T2036 — Provincial or Territorial Foreign Tax Credit (varies by province)

---

### 6.2 FTC Calculation

The federal FTC for "non-business income" (e.g., dividends, interest) is the LESSER of:

**(a) Foreign tax paid** on that income

**(b) Canadian tax otherwise payable** on that income, calculated as:

```
(Foreign non-business income / Total income) x Basic federal tax
```

**Example for CC (future scenario):**
- Total income: $100,000 CAD
- US dividend income: $5,000 CAD (from US stocks in non-registered account)
- US withholding paid: $750 CAD (15% of $5,000)
- Basic federal tax: $15,000
- FTC limit: ($5,000 / $100,000) x $15,000 = $750
- FTC claimed: $750 (lesser of $750 paid and $750 limit)
- Result: full credit, no double taxation

---

### 6.3 When FTC Does Not Fully Offset

The FTC can be limited when:

1. **Foreign tax rate exceeds Canadian rate on that income.** If you pay 25% foreign tax but
   Canada only taxes that income at 20%, you can only credit 20%. The 5% excess becomes a cost.

2. **Low total income relative to foreign income.** The formula limits FTC to the proportion of
   Canadian tax attributable to foreign income.

3. **Multiple foreign sources.** FTC is calculated separately for each country (separate basket
   for each country) and for business vs. non-business income.

**Carryover rules:**
- Excess non-business FTC: carry back 3 years or forward 10 years
- Excess business FTC: carry back 3 years or forward 10 years
- The carryover is to years where the basket has room

---

### 6.4 Provincial FTC

Ontario provides its own FTC on Form ON428. The calculation is similar but uses Ontario tax
payable instead of federal tax. Provincial FTC is often smaller because provincial rates are
lower, which means provincial tax on foreign income may not be fully offset.

`[OASIS]` CC claims both federal (T2209) and provincial (ON428) FTCs on any US tax withheld.

---

### 6.5 FTC vs. Deduction

You can choose to take a **deduction** for foreign taxes paid instead of a credit (s.20(11) ITA
for non-business income, s.20(12) for business income). A deduction reduces taxable income
rather than reducing tax payable.

**Almost always, the CREDIT is better than the deduction.** A $750 credit reduces tax by $750. A
$750 deduction at 30% marginal rate reduces tax by only $225.

**Exception:** If you have no Canadian tax payable (e.g., your income is below the basic personal
amount), a deduction may be preferable because a credit against zero tax is worthless, but a
deduction creates or increases a loss that can be carried forward.

---

### 6.6 Ordering Rules

When preparing your Canadian return with foreign income:

1. **Convert foreign income to CAD** using the Bank of Canada exchange rate (noon rate on date
   of receipt, or annual average rate — either is acceptable, but be consistent)
2. **Report gross foreign income** on the appropriate schedule (T2125 for business, Schedule 4
   for investments, etc.)
3. **Claim eligible deductions** against the income
4. **Calculate tax payable**
5. **Apply FTC** (T2209 for federal, T2036 / provincial form for provincial)
6. **FTC reduces tax owing** — any excess is carried back/forward

---

### 6.7 T2209 — Federal Foreign Tax Credit Form

**Who files:** Any Canadian resident who paid foreign income tax and wants to claim a credit.

**Key fields:**
- Country of foreign tax
- Foreign non-business income (in CAD)
- Foreign tax paid on non-business income (in CAD)
- Foreign business income (in CAD)
- Foreign tax paid on business income (in CAD)
- Basic federal tax (from T1 return)

`[OASIS]` Currently, CC has no US tax withheld (Bennett does not withhold). If CC begins
investing in US stocks and suffers withholding on dividends, T2209 becomes relevant.

---

## 7. US Sales Tax and State Tax Nexus

### 7.1 The Post-Wayfair Landscape

In 2018, the US Supreme Court ruled in *South Dakota v. Wayfair* that states can require
out-of-state sellers to collect sales tax if they meet certain economic thresholds, even without
physical presence. This created "economic nexus."

**Common state thresholds:**
- $100,000 in sales into the state, OR
- 200 or more separate transactions into the state

This applies to GOODS and certain SERVICES. The applicability to SaaS and digital services
varies by state.

---

### 7.2 Does This Apply to Canadian Companies?

**Generally: No, with caveats.**

Most state economic nexus laws target sellers of tangible goods or taxable services delivered
into the state. The enforcement mechanism (requiring collection and remittance) assumes the
seller has some connection to the US tax system.

**For a Canadian SaaS company selling B2B to US clients:**
- Most states do not tax B2B SaaS (it varies — Texas does, California does not)
- Even states that tax SaaS typically only enforce against sellers with US nexus
- A Canadian company with no US presence, no US employees, and no US entity has no practical
  mechanism for US states to enforce collection

`[WARNING]` This does NOT mean you are legally exempt. Some states (particularly Texas, New York,
and Washington) are aggressive about requiring foreign sellers to register and collect. The
practical enforcement risk for a Canadian sole proprietor selling B2B is near zero, but it
increases with revenue scale and US physical presence.

---

### 7.3 State-by-State SaaS Taxability

| State | SaaS Taxable? | B2B Exempt? | Notes |
|-------|--------------|-------------|-------|
| California | No | N/A | SaaS is not tangible personal property |
| Texas | Yes | No | SaaS is taxable "data processing service" |
| New York | Yes | No | SaaS is tangible personal property equivalent |
| Florida | No (until 7/2024, Yes after) | Some exemptions | Changed in 2024 |
| Washington | Yes (B&O tax, not sales tax) | No | Unique B&O tax system |
| Illinois | No (unless delivered with tangible media) | N/A | |
| Pennsylvania | Yes | No | "Canned" SaaS is taxable |
| Massachusetts | Yes | No | SaaS explicitly taxable since 2019 |
| Tennessee | No | N/A | SaaS not taxable |
| Georgia | No | N/A | |
| States with NO income tax | TX, FL, WA, WY, NV, SD, TN, NH, AK | | May still have sales tax |

---

### 7.4 Does CC Have Nexus?

**Assessment:**
- Physical presence in US: NO
- US employees: NO
- US office or facility: NO
- US inventory: NO (SaaS, no physical goods)
- Affiliate relationships in US: NO
- Economic nexus: UNLIKELY (would need $100K+ in sales to a SINGLE state)
- Revenue from US: ~$30,000 USD/year from Bennett (one state)

**Conclusion:** CC does NOT currently have economic nexus in any US state. As revenue scales,
monitor total sales per state. If CC exceeds $100K in sales to clients in a single state that
taxes SaaS, registration may be required.

`[FUTURE]` If OASIS scales to dozens of US clients across multiple states, consider using an
automated sales tax platform (TaxJar, Avalara) to manage nexus obligations. But this is a
$100K+ revenue-per-state problem, not a current concern.

---

### 7.5 State Income Tax on Foreign Sellers

Most states follow the federal rule: no PE = no state income tax. But some states (California
is notorious) assert that doing business in the state, even without physical presence, can
create a state income tax filing obligation.

**Practical risk for CC:** Near zero. California's FTB (Franchise Tax Board) is aggressive, but
it targets companies with significant California presence (employees, customers, property). A
Canadian sole proprietor selling SaaS to a client in another state is not on their radar.

---

### 7.6 Marketplace Facilitator Rules

If CC sells through a US marketplace (e.g., Shopify App Store, AWS Marketplace, Salesforce
AppExchange), the MARKETPLACE is responsible for collecting and remitting sales tax — not CC.
This is called the "marketplace facilitator" rule and has been adopted by most US states.

**Result:** Selling through US marketplaces simplifies tax compliance because the platform
handles it.

---

## 8. Canadian Corporations with US Clients

### 8.1 Post-Incorporation: Same Treaty Protections

When CC incorporates OASIS as a CCPC (Canadian-Controlled Private Corporation), the treaty
protections remain the same. Article VII applies to enterprises (corporations included). No US
PE = no US tax on business profits.

**Key difference:** Instead of W-8BEN (individuals), the CCPC files **W-8BEN-E** with US clients.

---

### 8.2 W-8BEN-E for Corporations

Form W-8BEN-E is more complex than W-8BEN. Key sections:

- **Part I:** Entity identification (corporation name, country of incorporation, address)
- **Part I, Line 4:** Chapter 3 status — "Corporation" for a CCPC
- **Part I, Line 5:** Chapter 4 (FATCA) status — likely "Active NFFE" (Non-Financial Foreign
  Entity) for a SaaS company. This means OASIS is not a financial institution and has
  substantial active business income (not passive investment income).
- **Part II:** Disregarded entity or branch (usually N/A for a simple CCPC)
- **Part III:** Claim of tax treaty benefits — Article VII, 0% rate on business profits
- **Part XXX (or relevant):** FATCA certification

`[FUTURE]` When CC incorporates, Atlas will prepare the W-8BEN-E with exact field-by-field
guidance.

---

### 8.3 Transfer Pricing (Multi-Entity Structures)

If OASIS eventually has both a Canadian entity (parent) and a US entity (subsidiary), transactions
between them must be at arm's length prices. Otherwise, the IRS (s.482 IRC) and CRA (s.247 ITA)
can adjust the prices and assess additional tax.

**Common transfer pricing scenarios:**
- US subsidiary pays Canadian parent for software license (royalty)
- Canadian parent charges US subsidiary for management services
- US subsidiary handles US sales and retains a markup

**Documentation requirements:** Both Canada and the US require contemporaneous documentation
of transfer pricing methodology. Penalties for non-compliance: 10% of the adjustment (ITA s.247)
and up to 40% in the US (IRC s.6662(e)).

`[FUTURE]` Transfer pricing becomes relevant only if CC creates a US entity. Current structure
(Canadian sole prop selling directly to US clients) has no transfer pricing issues.

---

### 8.4 US Branch vs. US Subsidiary

| Factor | US Branch | US Subsidiary (Inc.) |
|--------|----------|---------------------|
| Legal structure | Extension of Canadian corp | Separate US entity |
| US filing | Form 1120-F (foreign corp) | Form 1120 (US corp) |
| Treaty benefit | Branch profits tax exemption (usually) | Dividends taxed at treaty rate |
| Liability | Canadian parent fully liable | Limited liability (separate entity) |
| State registration | Required in state of operation | Required in state of incorporation |
| Transfer pricing | Between head office and branch (simpler) | Between parent and sub (complex) |
| Repatriation | No withholding (branch profits tax exempted by treaty) | 5% or 15% withholding on dividends |
| When to use | Temporary US operations, testing the market | Permanent US presence, US employees, US clients wanting US entity |

**Atlas recommendation for CC:** Neither, for now. Current structure (Canadian sole prop / future
CCPC selling directly to US clients) is optimal. A US entity only makes sense when CC has US
employees, significant US-based operations, or US clients who contractually require a US entity.

---

### 8.5 State Income Tax on Foreign Corporations

Some US states tax foreign (non-US) corporations that do business in the state. The definition
of "doing business" varies by state.

**High-risk states for foreign corporations:**
- **California:** Apportions worldwide income based on US sales factor. $800/year minimum tax.
- **New York:** Similar apportionment. Filing required if "doing business" in NY.
- **Texas:** Franchise tax (margin tax) applies to entities doing business in TX.

`[FUTURE]` Only relevant if CC creates a US entity or establishes significant nexus in a state.

---

### 8.6 Effectively Connected Income (ECI)

Under US tax law, a foreign person is taxed on income "effectively connected" with a US trade
or business. If a Canadian company has ECI, it must file Form 1120-F and pay US corporate tax
on the ECI.

**What creates ECI:** Having a US office, US employees conducting core business activities, or
a "fixed base" in the US (mirrors the PE concept).

**Treaty interaction:** Even if the IRS argues ECI exists, the treaty Article VII overrides —
no tax unless there is a PE. The treaty definition of PE is stricter than the domestic law
definition of ECI, so the treaty is more protective.

---

### 8.7 Branch Profits Tax

The US imposes a 30% "branch profits tax" on the after-tax earnings of a US branch of a foreign
corporation (IRC s.884). This is the US equivalent of dividend withholding — the idea is that
branch profits are equivalent to dividends that would be paid if the branch were a subsidiary.

**Treaty exemption:** Article X(6) of the Canada-US treaty reduces the branch profits tax to
**5%** for Canadian corporations. Furthermore, the first $500,000 of cumulative branch profits
is exempt.

`[FUTURE]` Only relevant if CC opens a US branch of the Canadian corporation.

---

## 9. Stripe, Wise, and US Payment Platform Compliance

### 9.1 Stripe — A US Company

Stripe, Inc. is a US corporation. When you create a Stripe account, Stripe needs to determine
whether you are a US person (subject to 1099 reporting) or a non-US person (subject to 1042-S
reporting, if applicable).

**Critical setup decisions:**
- **Country of account:** Set this to CANADA. This tells Stripe you are a non-US entity.
- **Business address:** Canadian address. Do NOT use a US address.
- **Bank account for settlement:** Canadian bank or Wise (either works). Using a US-based Wise
  USD account does not change your tax status, but keeping settlement in CAD simplifies
  accounting.

**If set up correctly as Canadian:**
- Stripe does NOT issue 1099-K (that is for US persons only)
- Stripe may share data with CRA under CRS (Common Reporting Standard) or FATCA if applicable
- All revenue is reported on your Canadian T2125 as self-employment income

`[OASIS]` CC has two Stripe brands (OASIS AI Solutions + Nostalgic DJ). Both should be verified
as Canadian entities in Stripe settings.

---

### 9.2 1099-K Threshold and Canadian Accounts

**For US-configured Stripe accounts:** Stripe issues 1099-K when gross payments exceed $600/year.
**For Canadian-configured accounts:** Stripe does NOT issue 1099-K.

The key is the account's country configuration, not where the money ends up.

`[WARNING]` If CC created the Stripe account with a US address or US business entity during
initial setup (perhaps for faster approval or access), Stripe treats it as a US account. Change
this immediately if so — contact Stripe support to update the country and entity type.

---

### 9.3 Wise — International Platform

Wise (formerly TransferWise) is headquartered in London with a US subsidiary (Wise US Inc.).
Wise provides multi-currency accounts including USD accounts with US routing numbers.

**Tax reporting by Wise:**
- **US tax forms:** Wise issues 1099-INT for US-based accounts earning interest above $10. If
  CC's Wise USD account earns interest, Wise may issue a 1099-INT.
- **CRS reporting:** Wise reports account information to tax authorities under the Common
  Reporting Standard. As a Canadian resident, CC's Wise account information is shared with CRA.
- **FATCA:** If CC has a US-based Wise account, FATCA reporting applies. Wise reports to IRS.

**CC's Wise setup:**
- Wise Business Account: active (CAD + USD)
- USD account: used for Bennett payments and Stripe payouts
- Currency conversion: manually converted CAD<->USD as needed

**Best practice:**
- Keep Wise account registered under Canadian address
- Convert USD to CAD regularly to simplify bookkeeping (fewer FX calculations at year-end)
- Track FX gains/losses on conversion (technically taxable in Canada but de minimis for operating
  conversions)
- Monitor total foreign property cost for T1135 threshold ($100K CAD)

---

### 9.4 PayPal and Payoneer

**PayPal:**
- US company, issues 1099-K to US account holders above $600 threshold
- Canadian PayPal accounts should not receive 1099-K
- If you do receive one, same process as Section 4 — provide W-8BEN, request correction

**Payoneer:**
- Israeli company with US operations
- Issues 1099-K for US-classified accounts
- Canadian accounts should be set up with Canadian address and entity

---

### 9.5 Multi-Currency Accounting — Exchange Rate Rules

**CRA requirement:** All amounts on your Canadian tax return must be in Canadian dollars.

**Acceptable exchange rates:**
1. **Bank of Canada noon rate on the date of the transaction** — most accurate, required for
   large/infrequent transactions
2. **Bank of Canada annual average rate** — acceptable for regular recurring amounts (e.g.,
   monthly invoices). The 2025 annual average USD/CAD rate will be published by CRA.

**Consistency rule:** Pick one method and use it consistently throughout the tax year. You can
use different methods for different types of income (e.g., daily rate for individual invoices,
annual average for portfolio dividends), but be consistent within each type.

**FX gains and losses:**
- When you convert USD to CAD, the difference between the exchange rate when you received the
  USD and the rate when you converted is a foreign exchange gain or loss
- Under s.39(2) ITA, the first $200 of net FX gains in a year is exempt (personal exemption)
- Above $200, FX gains are capital gains (50% inclusion) or fully deductible if business-related
- For operational conversions (converting client payments to pay Canadian expenses), the gain/loss
  is part of business income, not a capital transaction

`[OASIS]` CC receives USD from Bennett and converts to CAD via Wise. The FX gain/loss on each
conversion is technically taxable but likely de minimis. Track it anyway — at scale it adds up.

**Practical approach for CC:**
1. Record the CAD equivalent of each USD payment received (using BoC rate on date received)
2. Report this CAD amount as business revenue on T2125
3. If you hold USD for extended periods and convert later, track the FX gain/loss separately
4. Use the BoC rate lookup tool: `bankofcanada.ca/rates/exchange/daily-exchange-rates/`

---

### 9.6 Practical Stripe/Wise Setup Guide for Canadian Business Owners

**Stripe setup checklist:**
- [ ] Country: Canada
- [ ] Business type: Sole proprietor (or CCPC after incorporation)
- [ ] Business name: OASIS AI Solutions (or your Canadian business name)
- [ ] Address: Canadian business address
- [ ] Tax ID: Canadian BN (Business Number) if registered, or SIN for sole props
- [ ] Bank account for payouts: Canadian bank account or Wise (CAD recommended)
- [ ] Currency: Default to CAD (Stripe converts automatically) or USD if you prefer

**Wise setup checklist:**
- [ ] Account type: Business (not personal — for business income)
- [ ] Country of registration: Canada
- [ ] Business address: Canadian address
- [ ] USD account: Active (for receiving US client payments)
- [ ] CAD account: Active (for paying Canadian expenses)
- [ ] Regular conversion schedule: Convert USD to CAD monthly (simplifies accounting)

---

## 10. Snowbird Rules and Physical Presence

### 10.1 US Substantial Presence Test

The US determines tax residency for non-citizens using the **Substantial Presence Test** (IRC
s.7701(b)). You are a US resident for tax purposes if:

**You were physically present in the US for at least 31 days during the current year, AND**

**The sum of the following exceeds 183 days:**
- All days present in the current year, PLUS
- 1/3 of the days present in the prior year, PLUS
- 1/6 of the days present in the year before that

**Example:**
- 2024: 120 days in US = 120
- 2023: 120 days in US = 40 (120 x 1/3)
- 2022: 120 days in US = 20 (120 x 1/6)
- Total: 180 — does NOT meet test (under 183)

- 2024: 130 days in US = 130
- 2023: 130 days in US = 43 (130 x 1/3)
- 2022: 130 days in US = 22 (130 x 1/6)
- Total: 195 — MEETS test. You are a US resident alien for tax purposes.

---

### 10.2 The 183-Day Misconception

`[COMMON MISTAKE]` Many Canadians believe "I can spend up to 183 days in the US without tax
consequences." This is WRONG for two reasons:

1. **The Substantial Presence Test uses a weighted formula** over three years, not just the
   current year. You can trigger the test with as few as 121 days per year over three years.

2. **Even under 183 days, you may still be taxed** on US-source income earned while physically
   present (e.g., consulting work done from a US location).

---

### 10.3 Closer Connection Exception (Form 8840)

If you meet the Substantial Presence Test but can demonstrate a "closer connection" to Canada
(or another foreign country) than to the US, you can avoid US tax residency by filing **Form
8840** (Closer Connection Exception Statement for Aliens).

**Closer connection factors:**
- Location of permanent home
- Location of family
- Location of personal belongings
- Location of social, political, cultural, religious organizations
- Location of business activities
- Location of driver's license
- Location where you vote
- Country of residence stated on forms (W-8BEN, etc.)
- Where you bank
- Location of investments

**Filing deadline:** June 15 of the following year (same as Canadian self-employed deadline).

`[WARNING]` If you fail to file Form 8840 when required, the IRS may determine you are a US
resident alien and assess tax on your worldwide income.

---

### 10.4 Treaty Tie-Breaker (Article IV)

If both Canada and the US consider you a tax resident (e.g., you meet the Substantial Presence
Test AND are a Canadian resident), the treaty tie-breaker rules determine which country gets
to tax you as a resident.

**Tie-breaker order:**
1. **Permanent home** — where is your permanent home? If in only one country, that country wins.
2. **Centre of vital interests** — where are your personal and economic relations closer?
3. **Habitual abode** — where do you spend more time?
4. **Citizenship** — if all else fails, the country of citizenship wins.

**For CC:** Permanent home in Canada, centre of vital interests in Canada, habitual abode in
Canada, Canadian citizen. CC is unambiguously Canadian for treaty purposes, even if he ever
triggers the Substantial Presence Test.

---

### 10.5 Canadian Residency for Tax Purposes

Canada determines tax residency based on **facts and circumstances**, not a simple day count.

**Key factors (CRA IT-221R3):**
- Dwelling place (owned or rented) in Canada
- Spouse/common-law partner in Canada
- Dependants in Canada
- Personal property in Canada (furniture, car, etc.)
- Social ties (memberships, bank accounts)
- Economic ties (employment, business)
- Provincial health insurance coverage
- Driver's license
- Passport

**A Canadian remains a tax resident unless they sever these ties AND establish residency
elsewhere.** Simply spending time outside Canada does not end Canadian residency.

---

### 10.6 Travel Documentation Requirements

If you spend significant time in the US:

- **Keep a travel log** (dates of entry/exit, purpose of visit)
- **Retain boarding passes, hotel receipts, passport stamps** (US/Canada border is often unstamped,
  so electronic records matter)
- **The IRS can access US CBP entry/exit records** — do not lie about days present
- **The CRA can request travel records** during an audit to verify residency claims

---

### 10.7 Health Insurance Implications (OHIP)

Ontario's OHIP (Ontario Health Insurance Plan) requires you to be **physically present in Ontario
for at least 153 days in any 12-month period** (the "212-day rule" — you can be absent up to
212 days but must be present at least 153 days).

If you are absent from Ontario for more than 212 days in a 12-month period, you may lose OHIP
coverage. This is independent of your tax residency status.

`[OASIS]` CC lives in Collingwood, ON, and is not currently at risk. But if CC becomes a digital
nomad or spends extended time in the US or abroad, OHIP coverage should be monitored.

---

## 11. Common Mistakes and How to Avoid Them

### 11.1 Not Filing W-8BEN with US Clients

**The mistake:** Canadian freelancer starts working with US client, never submits W-8BEN.
US client's accountant sees foreign payments without documentation and either:
(a) withholds 30% "just to be safe," OR
(b) issues 1099-NEC, creating IRS matching problems.

**The fix:** Submit W-8BEN to EVERY US client within the first 30 days of the relationship.
It takes 5 minutes to fill out and lasts 3 years. Renew before expiry.

**Cost of not doing this:** Potentially 30% of your income withheld, requiring an ITIN
application and 1040-NR filing (months of work) to recover.

---

### 11.2 Thinking Stripe USD = US Tax Obligation

**The mistake:** "I receive payments in USD through Stripe (a US company), so I must have
US tax obligations."

**The truth:** The currency of payment and the nationality of the payment processor are
irrelevant to tax obligations. What matters is:
- Where YOU are a tax resident (Canada)
- Where the SERVICES are performed (Canada)
- Whether you have a US PE (no)

A Canadian receiving EUR through a German payment processor does not owe German tax. Same logic.

---

### 11.3 Not Reporting US-Source Income in Canada

**The mistake:** "I already received USD, that was taxed in the US (or I think it was), so I
do not need to report it in Canada."

**The truth:** Canada taxes residents on WORLDWIDE income. Every dollar earned, regardless of
source country or currency, must be reported on your Canadian return. Convert to CAD and
include on T2125 (business income) or the appropriate schedule.

`[WARNING]` CRA receives information about your foreign income through:
- CRS (Common Reporting Standard) — 100+ countries sharing financial data
- FATCA (Foreign Account Tax Compliance Act) — US reports to Canada
- Exchange of information under the Canada-US Tax Treaty
- Stripe/Wise/PayPal data sharing

CRA WILL know about your US income. Report it proactively.

---

### 11.4 Opening a US LLC as a Canadian

**The mistake:** "I will set up a US LLC for my US clients. It is simpler and they prefer it."

**The disaster:** A US LLC owned by a Canadian resident is a "controlled foreign affiliate"
under Canadian tax law. Income earned by the LLC is subject to FAPI (Foreign Accrual Property
Income) rules under ITA s.91. This means:

- The LLC's income is **attributed to you personally** in the year it is earned
- You pay **full Canadian tax** on the income (as if you earned it directly)
- The LLC provides **zero tax deferral** (unlike a CCPC, which defers personal tax until dividends)
- You must file **T1134** (foreign affiliate reporting) annually
- US LLC may also require a US tax return (Form 1065 or 1120, depending on classification)
- You may end up filing in BOTH countries with no tax benefit

**The fix:** If you need a corporate entity, incorporate a Canadian corporation (CCPC). It
provides treaty protection, small business deduction, and tax deferral. There is almost never
a reason for a Canadian resident to create a US LLC.

**Only exception:** If you have a genuine US business with US employees, US clients who
contractually require a US entity, and you plan to use the US entity as an operating subsidiary
of a Canadian parent. Even then, get cross-border tax advice first.

---

### 11.5 Not Claiming FTC for Withholding Suffered

**The mistake:** US stocks in a non-registered account have 15% withheld on dividends. Canadian
taxpayer reports the dividend income but forgets to claim the Foreign Tax Credit.

**The cost:** Double taxation. You pay 15% to the US AND your full Canadian marginal rate on
the same income. The FTC would have eliminated the double taxation.

**The fix:** File T2209 (federal) and your provincial FTC form (ON428 for Ontario) every year
you have foreign tax withheld. Your T3/T5 slip from your broker will show the foreign tax paid.

---

### 11.6 Assuming TFSA Is Tax-Free for US Dividends

**The mistake:** "My TFSA is tax-free, so dividends from US stocks in my TFSA are tax-free."

**The truth:** The TFSA is tax-free for CANADIAN tax purposes. The US does not recognize the
TFSA as a tax-exempt account. US dividends paid to TFSA holdings are subject to 15% withholding,
and this withholding is UNRECOVERABLE because:
- You cannot claim FTC (no Canadian tax on TFSA income to credit against)
- You cannot file a US return to recover it (you are not a US taxpayer)
- The withholding is a permanent cost

**The fix:** Hold US dividend-paying stocks in your RRSP (0% withholding, treaty exemption).
Hold Canadian stocks and non-US stocks in your TFSA.

---

### 11.7 Not Reporting US Bank Accounts on T1135

**The mistake:** "My Wise USD account is just for receiving client payments. It is not an
investment, so I do not need to report it."

**The truth:** If the total cost of ALL your specified foreign property (bank accounts, crypto
on foreign exchanges, US stocks, etc.) exceeds $100,000 CAD at any point during the year, you
must file T1135. A Wise USD account IS specified foreign property.

**Penalty for non-filing:** $25/day, up to $2,500 per year. Plus, if non-filing is deliberate,
the normal reassessment period extends to 3 years from filing (or indefinitely if form is
never filed).

`[OASIS]` CC's foreign property is currently well below $100K. Monitor as revenue scales.

---

### 11.8 Filing a US Tax Return When Not Required

**The mistake:** Canadian receives a 1099, panics, and files Form 1040-NR "just to be safe."

**The problem:** Filing a US tax return when not required can:
- Create a US filing obligation going forward (IRS expects returns from filers)
- Open you up to IRS audit for past years
- Require future FBAR/FATCA compliance if IRS considers you a person with filing obligation
- Cost $500-2,000 in US tax preparation fees per year, indefinitely

**The fix:** Do NOT file a US return unless you actually owe US tax or need to recover
incorrectly withheld funds. If you receive a 1099, follow the steps in Section 4.3.

---

## 12. CC-Specific US Tax Checklist

### 12.1 Immediate Actions [NOW]

| Priority | Action | Why | How | Time |
|----------|--------|-----|-----|------|
| 1 | **Submit W-8BEN to Bennett** | Prevents potential 30% withholding, blocks 1099 issuance, documents foreign status | Download W-8BEN from IRS.gov, complete per Section 3.3, email to Bennett | 15 min |
| 2 | **Verify Stripe is Canadian** | Prevents 1099-K issuance, ensures correct tax reporting | Stripe Dashboard > Settings > Business > verify country = Canada | 5 min |
| 3 | **Verify Wise account country** | Ensures correct CRS reporting, clean records | Wise Settings > verify business address = Canada | 5 min |
| 4 | **Set up FX tracking** | CRA requires CAD conversion of all USD income | Spreadsheet: date received, USD amount, BoC rate, CAD equivalent | 30 min |
| 5 | **Confirm T1135 not required** | Wise USD + Kraken cost basis under $100K | Total foreign property cost < $100K CAD = no T1135 | 5 min |
| 6 | **Use Bank of Canada rate for conversions** | CRA-accepted rate, consistent methodology | bankofcanada.ca/rates/exchange/daily-exchange-rates/ | Ongoing |

---

### 12.2 Future Actions [FUTURE]

| Trigger | Action | Details |
|---------|--------|---------|
| Incorporation of OASIS | File W-8BEN-E for CCPC | Replace personal W-8BEN with entity form. Claim Article VII. |
| US stock investments | Hold in RRSP (not TFSA) | 0% withholding in RRSP vs. 15% permanent loss in TFSA |
| US stock dividends received | File T2209 for FTC | Claim credit for 15% US withholding against Canadian tax |
| Foreign property cost > $100K CAD | File T1135 | Annual filing with Canadian return. See ATLAS_FOREIGN_REPORTING.md |
| Hiring US contractors | Understand 1099 obligations | If OASIS hires US persons, may need to issue 1099-NEC |
| US real estate purchase | Plan for FIRPTA + estate tax | 15% withholding on sale, treaty estate tax protection |
| Revenue > $100K/state in SaaS-taxable state | Sales tax registration | Unlikely near-term, but monitor with TaxJar/Avalara |
| Creating US entity | Get cross-border tax advice | Do NOT create US LLC without professional guidance (FAPI risk) |
| W-8BEN renewal (every 3 years) | Re-submit to all US clients | Set calendar reminder for expiry date |

---

### 12.3 Annual Checklist for Canadian Business Owners with US Revenue

**January (Tax year preparation):**
- [ ] Confirm all W-8BENs on file with US clients are still valid (3-year expiry)
- [ ] Review Stripe and Wise account settings — verify Canadian configuration
- [ ] Calculate total foreign property cost — determine T1135 obligation

**March-April (Tax filing):**
- [ ] Convert all USD income to CAD using BoC rates
- [ ] Report all US-source business income on T2125
- [ ] File T2209 if any US tax was withheld (dividends, incorrectly withheld payments)
- [ ] File T1135 if foreign property cost exceeded $100K at any point
- [ ] Pay any tax owing by April 30 (even though filing deadline is June 15 for self-employed)

**June (Filing deadline):**
- [ ] File T1 return by June 15 (self-employed deadline)
- [ ] File Form 8840 with IRS if you spent significant time in US (by June 15)

**September (Quarterly planning):**
- [ ] Review US revenue per state — any approaching nexus thresholds?
- [ ] Consider tax-loss harvesting on US investments (if applicable)

**December (Year-end):**
- [ ] Confirm all US client payments received and recorded in CAD
- [ ] Review registered account allocation (US stocks in RRSP, not TFSA)
- [ ] Renew any expiring W-8BENs before year-end

---

### 12.4 Key Forms Reference

| Form | Filed With | Who Files | When | Purpose |
|------|-----------|-----------|------|---------|
| **W-8BEN** | US client (not IRS directly) | Canadian individual | Before first payment | Claim treaty benefits, prevent withholding |
| **W-8BEN-E** | US client | Canadian corporation | Before first payment | Same, for entities |
| **W-9** | US client | US persons ONLY | Do NOT file this if Canadian | Request for US Taxpayer ID — Canadians use W-8BEN instead |
| **1099-NEC** | IRS (by US payer) | US payer | Jan 31 | Reports payments to US contractors — should NOT be issued for Canadians |
| **1099-K** | IRS (by payment processor) | Stripe/PayPal | Jan 31 | Reports payment processing — should NOT be issued for Canadian accounts |
| **1042-S** | IRS (by US payer) | US payer | Mar 15 | Reports US-source income paid to foreign persons with withholding |
| **1040-NR** | IRS | Non-resident alien | Apr 15 (or June 15 if no wages) | US nonresident income tax return — only if you owe US tax or need refund |
| **Form 8840** | IRS | Non-resident meeting SPT | June 15 | Closer Connection Exception — avoids US residency determination |
| **T2209** | CRA | Canadian taxpayer | With T1 return | Federal Foreign Tax Credit claim |
| **T1135** | CRA | Canadian resident | With T1 return | Foreign property > $100K CAD reporting |
| **W-7** | IRS | Applicant | With 1040-NR or standalone | ITIN application |
| **SS-4** | IRS | Business applicant | Anytime | EIN application |
| **Form 706-NA** | IRS | Executor | 9 months after death | US estate tax return for non-resident aliens |

---

### 12.5 Quick Decision Trees

**Do I need to file a US tax return?**
```
Are you a US citizen or green card holder?
  YES → File 1040 every year, regardless of where you live
  NO → Continue

Do you have a Permanent Establishment in the US?
  YES → File 1120-F (corporation) or 1040-NR (individual) for PE income
  NO → Continue

Was US tax withheld on your income?
  YES → Do you want to claim a refund?
    YES → File 1040-NR (but read Section 3.5 first — this creates filing obligation)
    NO → Claim FTC in Canada instead (if possible). Do not file US return.
  NO → Continue

Do you have US-source FDAP income (rents, royalties, dividends)?
  YES → Was withholding handled correctly per treaty?
    YES → No US return needed. Report income in Canada and claim FTC.
    NO → File 1040-NR or request payer correction.
  NO → No US return needed. Report all income in Canada.
```

**Should I set up a US entity?**
```
Do you have US employees or need to hire in the US?
  YES → Consider US subsidiary of Canadian parent. Get professional advice.
  NO → Continue

Do US clients contractually require a US entity?
  YES → Consider US subsidiary. But first, try W-8BEN-E — most clients accept Canadian corp.
  NO → Continue

Do you want tax deferral or reduced rates in the US?
  As a Canadian, a US entity provides ZERO tax benefit (FAPI rules).
  → Do NOT create a US LLC. Incorporate in Canada (CCPC) instead.
```

**Where should I hold US stocks?**
```
RRSP → 0% US withholding (treaty exemption). BEST for US dividend stocks.
Non-registered → 15% US withholding, recoverable via FTC. SECOND BEST.
TFSA/FHSA/RESP → 15% US withholding, UNRECOVERABLE. WORST for US dividend stocks.
```

---

### 12.6 Cost of Getting This Wrong vs. Right

| Scenario | Cost of Getting It Wrong | Cost of Getting It Right |
|----------|------------------------|------------------------|
| No W-8BEN, client withholds 30% | 30% of income trapped in IRS for 6-12 months. ITIN application + 1040-NR filing ($1,000+ in fees). | 15 minutes to fill out W-8BEN. Zero withholding. |
| 1099 issued incorrectly | IRS matching notice. Response letter. Possible need to file 1040-NR. Ongoing anxiety. | W-8BEN blocks 1099. Zero IRS interaction. |
| US stocks in TFSA | 15% permanent annual drag on all dividends. On $100K portfolio: ~$375/year lost forever. | Hold in RRSP instead. $0 lost. |
| Created US LLC | FAPI accrual, dual filing (US + Canada), T1134 reporting, zero tax benefit, $2,000-5,000/year in compliance costs. | Canadian CCPC: single jurisdiction, SBD, tax deferral, $500-1,000/year in compliance. |
| US income unreported in Canada | CRA reassessment, penalties (5% + 1%/month late), interest, potential gross negligence penalty (50% of tax owing). | Report on T2125, pay tax. No penalties. |
| T1135 not filed when required | $25/day penalty (up to $2,500/year), extended reassessment period, possible gross negligence penalty. | File with return. Zero penalty. |

---

## Appendix A: Key Treaty Articles Summary

| Article | Subject | Canadian Resident Impact |
|---------|---------|------------------------|
| IV | Residence | Tie-breaker rules for dual residents |
| V | Permanent Establishment | Defines PE — key to business profits taxation |
| VII | Business Profits | Only taxable in residence country unless PE exists |
| X | Dividends | 15% withholding (5% for 10%+ corporate owners) |
| XI | Interest | 0% withholding |
| XII | Royalties | 0% withholding |
| XIII | Capital Gains | Taxable in residence country (exceptions for real property) |
| XIV | Independent Services | Deleted by 5th Protocol — now under Article VII |
| XV | Employment Income | Taxable where work is performed (exceptions for short-term) |
| XXI | Other Income | Covers items not specifically addressed |
| XXIV | Elimination of Double Taxation | FTC mechanism codified in treaty |
| XXV | Non-Discrimination | Prevents discriminatory taxation |
| XXVI | Mutual Agreement Procedure | Dispute resolution between CRA and IRS |
| XXIX | Miscellaneous | Savings clause (US can tax its citizens regardless) |
| XXIX-B | Taxes on Estates/Gifts | Pro-rated US estate tax exemption for Canadians |

---

## Appendix B: US-Source Income Classification for Canadians

| Income Type | US Source? | Treaty Article | US Withholding (with W-8BEN) | Canadian Treatment |
|-------------|----------|---------------|-----------------------------|--------------------|
| Services performed in Canada for US client | No (Canadian source) | VII | 0% | T2125 business income |
| SaaS sold to US customers | No (Canadian source) | VII | 0% | T2125 business income |
| US stock dividends | Yes | X | 15% (0% in RRSP) | Foreign income + FTC |
| US bond interest | Yes | XI | 0% | Foreign income |
| US real estate rent | Yes | VI | 30% gross (or net election) | Foreign income + FTC |
| US real estate sale gain | Yes | XIII | FIRPTA 15% | Capital gain + FTC |
| US employment (performed in US) | Yes | XV | Standard US withholding | Foreign income + FTC |
| US employment (performed in Canada) | No | XV | 0% | Employment income |
| Royalties from US | Yes | XII | 0% | Foreign income |

---

## Appendix C: Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| W-8BEN form | irs.gov/forms-pubs/about-form-w-8-ben | Download blank W-8BEN |
| W-8BEN-E form | irs.gov/forms-pubs/about-form-w-8-ben-e | Download blank W-8BEN-E |
| Bank of Canada exchange rates | bankofcanada.ca/rates/exchange/daily-exchange-rates/ | Official FX rates for CRA |
| Canada-US Tax Treaty (full text) | fin.gc.ca/treaties-conventions/usa_-eng.asp | Complete treaty text |
| CRA Foreign Tax Credit guide | canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-40500-federal-foreign-tax-credit.html | T2209 instructions |
| IRS Publication 519 | irs.gov/publications/p519 | US Tax Guide for Aliens |
| IRS Publication 901 | irs.gov/publications/p901 | US Tax Treaties |
| T1135 guide | canada.ca/en/revenue-agency/services/tax/international-non-residents/information-been-moved/foreign-reporting/questions-answers-about-form-t1135.html | Foreign property reporting |
| Substantial Presence Test calculator | irs.gov/individuals/international-taxpayers/substantial-presence-test | Check if SPT met |

---

**Document version:** 1.0
**Author:** ATLAS — CC's CFO Agent
**Lines:** ~1,300
**Covers:** 12 major sections + 3 appendices
**Applicability:** Any Canadian resident earning USD from US clients, with specific guidance for CC/OASIS

> "The best tax strategy is knowing which country gets to tax you — and making sure only one does."
> — ATLAS
