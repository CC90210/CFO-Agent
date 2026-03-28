# ATLAS — Foreign Property Reporting & Transfer Pricing Guide

> **For:** Conaugh McKenna (CC), OASIS AI Solutions, Collingwood Ontario
> **Jurisdiction:** Canada (Ontario) | **Tax year:** 2025-2026 (planning)
> **Last Updated:** 2026-03-27
> **Purpose:** Complete CRA foreign reporting obligations for a Canadian resident with a Wise USD account,
> crypto on foreign exchanges, and a roadmap for future foreign entities. T1135, T1134, T1141, T1142,
> transfer pricing under s.247, and foreign tax credits under s.126.
> All ITA references are to the *Income Tax Act (Canada)*, R.S.C. 1985, c.1 (5th Supp.) unless noted.
> All CRA form references are to their current versions as of 2026.

**Tags used throughout:**
- `[NOW]` — Actionable today as a Canadian-resident sole proprietor
- `[FUTURE]` — Relevant upon incorporation, foreign entity ownership, or departure
- `[OASIS]` — Specific to CC's actual situation, named and applied directly
- `[WARNING]` — High-penalty risk area. Do not skip or defer.

---

## Table of Contents

1. [T1135 — Foreign Income Verification Statement](#1-t1135--foreign-income-verification-statement)
2. [T1134 — Foreign Affiliates](#2-t1134--foreign-affiliates)
3. [T1141 — Contributions to Non-Resident Trusts](#3-t1141--contributions-to-non-resident-trusts)
4. [T1142 — Distributions from Non-Resident Trusts](#4-t1142--distributions-from-non-resident-trusts)
5. [Transfer Pricing — ITA s.247](#5-transfer-pricing--ita-s247)
6. [Foreign Tax Credits — ITA s.126](#6-foreign-tax-credits--ita-s126)
7. [Departure from Canada — Final Reporting](#7-departure-from-canada--final-reporting)
8. [Decision Trees](#8-decision-trees)
9. [CC-Specific Compliance Checklist](#9-cc-specific-compliance-checklist)
10. [Key ITA Reference Index](#10-key-ita-reference-index)

---

## 1. T1135 — Foreign Income Verification Statement

### 1.1 The Core Rule

**ITA s.233.3** requires every Canadian-resident individual, corporation, and trust that held
"specified foreign property" with a **total cost exceeding $100,000 CAD** at any point during the
tax year to file Form T1135.

`[WARNING]` The threshold is **cost basis**, not current fair market value. If you deposited
$110,000 CAD worth of crypto onto Kraken and the portfolio subsequently crashed to $40,000,
you still must file T1135 — because your **cost** exceeded $100,000 at the time of the deposits.

`[WARNING]` "At any point during the year" means the test is continuous, not just at year-end.
If you briefly crossed $100,000 in March and withdrew in April, T1135 was still triggered for
that tax year.

---

### 1.2 What Is "Specified Foreign Property"?

**ITA s.233.3(1) — Definition of "specified foreign property":**

#### INCLUDED — Must Count Toward $100K Threshold

| Property Type | ITA Authority | CC-Specific Notes |
|---------------|--------------|-------------------|
| Foreign bank accounts | s.233.3(1)(a) | Wise USD account — counts in CAD equivalent |
| Foreign brokerage accounts | s.233.3(1)(a) | Any USD securities account outside registered accounts |
| Shares of foreign corporations | s.233.3(1)(b) | US stocks, ETFs held at foreign brokers or direct |
| Debt owed by non-residents (receivables) | s.233.3(1)(c) | Outstanding invoices from foreign clients |
| Interests in foreign partnerships | s.233.3(1)(d) | LP interests, DAO token holdings (arguable) |
| Crypto on foreign exchanges | CRA guidance 2022 | Kraken, Coinbase, Binance — CRA position: counts |
| Foreign intellectual property | s.233.3(1)(e) | Domain names, patents held through foreign entities |
| Foreign rental/real property | s.233.3(1)(f) | Any non-personal-use foreign real estate |
| Property held by a non-resident trust for CC | s.233.3(1)(g) | Trust CC can benefit from |
| Loans to non-residents | s.233.3(1)(c) | Personal loans to foreign persons |

#### EXCLUDED — Does NOT Count Toward $100K Threshold

| Exclusion | ITA Authority | Notes |
|-----------|--------------|-------|
| RRSP / RRIF holdings | s.233.3(1) definition | Excluded explicitly — even US stocks inside RRSP |
| TFSA holdings | s.233.3(1) definition | Excluded — foreign investments inside TFSA are fine |
| FHSA, RESP, RDSP | s.233.3(1) definition | All registered plans excluded |
| Personal-use foreign property | s.233.3(1) definition | Vacation home used primarily personally (nuanced — see 1.3) |
| Active business inventory | s.233.3(1) definition | Goods held for sale in an active business |
| Shares of foreign affiliates | s.233.3(1) exception | Reported on T1134 instead (see Section 2) |
| Foreign government pensions | Administrative | CPP/OAS equivalents — not specified foreign property |

`[OASIS]` **Key implication for CC:** Foreign stocks held inside your TFSA or RRSP are completely
outside T1135. This is a major structural advantage — concentrate foreign holdings in registered
accounts where possible to stay below the $100K reporting threshold.

---

### 1.3 Personal-Use Property Exception — Nuanced

A foreign vacation property used **primarily for personal use** (i.e., not rented out) is excluded
from specified foreign property under s.233.3(1). However:

- "Primarily" = more than 50% of the year used personally
- If you rent it out for even a few weeks, the CRA may consider whether it shifted to investment property
- A foreign condo rented 8 months/year and used personally 4 months = **not** personal-use property → must include in T1135 threshold
- A foreign cottage you use all summer and never rent = personal-use → excluded

`[OASIS]` Not currently applicable for CC but relevant if a foreign property is acquired post-FIRE.

---

### 1.4 Crypto on Foreign Exchanges — CRA's Position

`[WARNING]` This is the area with the most ambiguity and highest current enforcement priority.

**CRA's published position (2022 CRA guidance on cryptocurrency):**

> Cryptocurrency held on a foreign exchange constitutes "funds or intangible property situated,
> deposited, or held outside Canada" — it is specified foreign property under s.233.3(1).

**The cost basis calculation for crypto T1135:**

CRA uses your **adjusted cost base (ACB)** — the total CAD-equivalent amount you paid to acquire
the crypto currently on the foreign exchange. Not current price.

```
Example — CC's Kraken account:

Purchase history:
  BTC: Bought at various times, total cost: $8,200 CAD
  SOL: Bought at various times, total cost: $3,100 CAD
  LTC: Bought at various times, total cost: $900 CAD
  ATOM: Bought at various times, total cost: $400 CAD
  Wise USD account: $3,000 CAD equivalent

  Total cost of specified foreign property: $15,600 CAD

  T1135 threshold: $100,000 CAD
  CC's current status: WELL BELOW threshold → No T1135 required at current scale

Threshold scenario — CC grows to:
  Kraken deposits (total cost): $85,000 CAD
  Wise USD account: $20,000 CAD
  Combined cost: $105,000 CAD → T1135 REQUIRED
```

`[OASIS]` At CC's current account size (~$136 equity on Kraken), T1135 is not required.
The threshold to monitor is: total deposits across ALL foreign accounts (cost basis, not value).
Track this annually. As OASIS revenue grows and trading capital increases, this threshold
could be crossed within 2-3 years.

---

### 1.5 The Two Reporting Methods

**Simplified Method** (total cost $100,000–$249,999):

- Do NOT need to list individual assets
- Report by category of property and country only
- Check the applicable boxes on T1135 Part A
- Report: maximum cost during year, cost at year-end, income earned, gain/loss on dispositions
- This is what CC would use initially if threshold is crossed

**Detailed Method** (total cost $250,000+):

- Must list each individual property
- For each item: description, country, maximum cost during year, year-end cost, income, gain/loss on disposition
- Much more administrative burden

```
Simplified Method reporting example (CC hypothetical at $140K cost):

Category: Funds held in foreign bank accounts
  Country: United States
  Maximum cost during year: $40,000 CAD (Wise USD)
  Cost at year-end: $22,000 CAD
  Income earned: $800 CAD (interest/FX gains)

Category: Funds or property held outside Canada
  Country: United States (Kraken exchange, domiciled in US)
  Maximum cost during year: $100,000 CAD
  Cost at year-end: $90,000 CAD (some dispositions during year)
  Income earned: $12,000 CAD (trading profit)
  Gain/loss on disposition: $8,000 CAD

Total → Simplified Method. No individual asset listing required.
```

---

### 1.6 Filing Deadline and Penalty Structure

**Due date:** Same as your T1 — April 30 (or June 15 for self-employed, but PAYMENT due April 30)

`[WARNING]` **Penalty schedule — one of CRA's most aggressive:**

| Scenario | Penalty | ITA Authority |
|----------|---------|--------------|
| Late filing (no demand from CRA) | $25/day, minimum $100, maximum $2,500 | s.162(7) |
| Late filing after CRA demand | $500/month, maximum $12,000 (24 months) | s.162(10) |
| Gross negligence or willful non-compliance | $1,000/month, maximum $24,000 (24 months) | s.163(2.4) |
| Knowingly failing to report (evasion) | Criminal prosecution + 200% of tax evaded | s.239 |
| Extended reassessment window | 6 years instead of 3 | s.152(4)(b.2) |

**The extended reassessment window is the hidden killer.** CRA normally has 3 years to reassess
your T1. If you failed to file T1135 for a year that contained unreported foreign income, the window
extends to **6 years** for that year's entire return — not just the T1135 issues. A missed T1135 in
2025 can expose every line of your 2025 T1 to reassessment until 2031.

---

### 1.7 T1135 Strategic Planning

`[NOW]` **Strategy 1: Track cost basis annually for all foreign accounts**

Maintain a running total: Wise balance (in CAD) + Kraken deposits (in CAD, all-time cost basis
of currently-held crypto, not total deposits net of withdrawals) + any other foreign property.
If this total at any point during the year approached $80,000, start monitoring monthly.

`[NOW]` **Strategy 2: Maximize holdings in registered accounts**

Foreign investments inside TFSA, RRSP, FHSA are fully excluded from T1135. If CC is holding
US ETFs or foreign-denominated assets, move them into registered accounts before they push
the foreign property cost above $100K.

```
Account placement optimization for T1135:

TFSA ($7,000/yr room):     → US ETFs (VFV, ZSP), foreign stocks → EXCLUDED from T1135
RRSP (18% of prior year income room): → US dividend stocks → EXCLUDED from T1135
                                         + Article XXI treaty benefit (0% US withholding)
Non-registered accounts:   → Canadian stocks, REITs → Not "specified foreign property"
Kraken (foreign):          → Minimize active capital → Count toward $100K threshold
Wise USD:                  → Keep for client invoicing, not investment storage
```

`[FUTURE]` **Strategy 3: CAD-denominated equivalent at a Canadian broker**

US stocks purchased through a Canadian brokerage (TD, RBC, Questrade) are still "specified
foreign property" technically — they are shares of foreign corporations. However, CRA's
administrative practice has been inconsistent on this point. Some tax practitioners argue
that property held through a Canadian regulated account has a "Canadian nexus" and should not
count. This has not been authoritatively decided. Do not rely on this ambiguity — include
them in the threshold calculation unless a CRA ruling or future guidance clarifies otherwise.

`[FUTURE]` **Strategy 4: If incorporating, hold crypto through the Canadian corporation**

A CCPC holding crypto does not eliminate T1135 (the corporation must also file T1135 if
it holds >$100K foreign property). However, it concentrates reporting into a single entity
with professional tax preparation, and separates business and personal reporting.

---

## 2. T1134 — Foreign Affiliates

### 2.1 Who Must File

**ITA s.233.4** requires every Canadian resident to file Form T1134 if they hold shares of a
"foreign affiliate" at any time during the year.

**"Foreign affiliate" (ITA s.95(1)):** A non-resident corporation where:
1. The Canadian taxpayer directly or indirectly owns **1% or more** of any class of shares, AND
2. The Canadian taxpayer together with related persons owns **10% or more** of any class of shares

**"Controlled foreign affiliate" (CFA):** A foreign affiliate where the Canadian taxpayer (plus
up to 4 related Canadians) controls more than **50%** of the votes or value. FAPI rules
apply to CFAs — see Section 2.4.

`[OASIS]` CC does not currently own shares of any foreign corporation. T1134 is not required now.
This section is the roadmap for when CC establishes a foreign entity (Irish company, Guernsey
company, US LLC with corporate treatment, etc.) while remaining a Canadian resident.

---

### 2.2 What T1134 Requires

**Form T1134 has two parts:**

**Part 1 — Summary (filed for every foreign affiliate):**
- Identity: name, country of incorporation, nature of business, fiscal year-end
- Share ownership: number and class held, FMV, percentage ownership
- Relationship: whether it is a "controlled foreign affiliate" (CFA) or non-controlled

**Part 2 — Supplement (filed separately for each foreign affiliate):**
- Detailed income breakdown: active business income, FAPI, taxable capital gains, dividends received
- Surplus account balances: exempt surplus, taxable surplus, pre-acquisition surplus
- FAPI calculation if applicable (see 2.4)
- Loans, dividends paid/payable to CC, disposition details

---

### 2.3 Filing Deadline

| Situation | Deadline | ITA Authority |
|-----------|---------|--------------|
| Individual taxpayer with foreign affiliate | 15 months after foreign affiliate's fiscal year-end | s.233.4(4) |
| Penalty — late filing | $25/day, min $100, max $2,500 | s.162(7) |
| Penalty — after CRA demand | $1,000/month, max $24,000 (24 months) | s.162(10.1) |

**Example:** If CC's Irish company has a December 31, 2027 fiscal year-end, T1134 is due
March 31, 2029 (15 months later) — giving substantial time to gather information after year-end.

---

### 2.4 FAPI — Foreign Accrual Property Income (ITA s.91)

**The most important tax rule for foreign corporate structures.**

FAPI is the mechanism by which CRA taxes Canadian residents on passive income earned inside
their CFAs — even if that income has not been distributed as a dividend.

**FAPI includes (ITA s.95(1)):**
- Interest income
- Dividends received from non-affiliated companies
- Rental income (passive)
- Royalties (if the CFA is not in the business of licensing IP)
- Taxable capital gains from non-active-business property

**FAPI does NOT include:**
- Active business income earned in a treaty country → "exempt surplus"
- Active business income in a TIEA country → "exempt surplus" (same treatment)
- Capital gains from the sale of shares of other foreign affiliates (generally)

**How FAPI is taxed:**

```
Year 1: CC's Irish CFA earns €10,000 FAPI (passive interest income)
  → CC includes €10,000 × CAD/EUR rate in income on CC's T1 (s.91(1))
  → Tax paid in Ireland on this amount (12.5%) → FTC available (s.91(4))
  → CC's deduction for Irish tax paid: included as a deduction (s.91(4)) or FTC
  → Net Canadian tax: (Canadian marginal rate - Irish rate) × FAPI

Year 2: Irish CFA pays the €10,000 as a dividend to CC
  → Dividend is NOT taxed again — already included in CC's income in Year 1
  → ITA s.113(1) dividend deduction eliminates double taxation
```

**The planning insight:** FAPI applies to PASSIVE income in a CFA. If the Irish company earns
**active business income** (SaaS subscriptions, service fees, consulting), it is NOT FAPI —
provided the company has genuine economic substance in Ireland.

---

### 2.5 Active Business Income Exemption — The Key Planning Tool

**ITA s.95(1) "exempt surplus" definition:**

Active business income earned by a CFA in a treaty country (or TIEA country) accumulates as
"exempt surplus." When the CFA pays a dividend to CC from exempt surplus, CC deducts it fully
under s.113(1)(a) — no Canadian tax ever payable on that income.

```
The Tax Math — Irish Active Business Income vs Passive Income:

Scenario A: Irish CFA earns €100,000 active SaaS revenue
  Irish corporate tax: 12.5% = €12,500
  Accumulated as exempt surplus
  Dividend to CC: €87,500
  Canadian tax on dividend: $0 (s.113(1)(a) exempt surplus deduction)
  Total tax cost: 12.5%
  Compare to: Canadian personal income tax at ~46% marginal rate = saving of 33.5%

Scenario B: Irish CFA earns €100,000 passive interest income (FAPI)
  Irish tax: 12.5% = €12,500
  FAPI inclusion in CC's T1 in the same year earned
  FTC for Irish tax: reduces Canadian tax by €12,500 equivalent
  Net Canadian tax: (46% - 12.5%) × €100,000 = 33.5% → €33,500
  Total tax: 12.5% + 33.5% = 46% (same as earning it directly in Canada)
  No deferral, no exemption — FAPI defeats the structure
```

`[OASIS]` The planning rule: any future Irish/Guernsey entity must earn **active business income**,
not passive income, to benefit from the exempt surplus exemption. This requires real employees,
real operations, and real economic substance in that jurisdiction.

---

### 2.6 Surplus Accounts — Tracking What Can Come Back Tax-Free

| Surplus Account | Source | Tax on Dividend to CC |
|-----------------|--------|----------------------|
| **Exempt surplus** | Active business income in treaty/TIEA country | $0 (s.113(1)(a)) |
| **Hybrid surplus** | Capital gains on active business property | 50% inclusion — half tax-free |
| **Taxable surplus** | FAPI, active business income in non-treaty country | Fully taxable, grossed up, FTC available |
| **Pre-acquisition surplus** | Accumulated before CC acquired the affiliate | Return of capital — reduces ACB |

**Strategic implication:** Build up exempt surplus first. Use it before touching taxable surplus.
Document each dividend with the surplus type it draws from — CRA requires this on T1134.

---

### 2.7 CC-Specific T1134 Scenarios

#### Scenario A: CC Incorporates an Irish Company (Remaining Canadian Resident)

- CC owns 100% → CFA (more than 50% controlled)
- T1134 must be filed annually
- Active SaaS revenue → exempt surplus → no FAPI
- Passive investment income (if any) → FAPI → taxed in CC's hands currently
- Transfer pricing applies (see Section 5)
- Recommendation: avoid holding passive investments in the Irish CFA while CC is Canadian-resident

#### Scenario B: CC Incorporates a Guernsey Company (Remaining Canadian Resident)

- Guernsey has a TIEA (Tax Information Exchange Agreement) with Canada, not a full treaty
- TIEA is sufficient to qualify income as exempt surplus under ITA s.95(1) "exempt surplus" definition
- 0% Guernsey corporate tax on most income
- Exempt surplus treatment applies → dividends to CC are tax-free in Canada
- T1134 required annually
- Real substance requirement is the key risk — must have genuine Guernsey operations

#### Scenario C: CC Departs Canada and Becomes Non-Resident

- No longer a Canadian resident → T1134 obligations cease immediately
- No FAPI inclusion (FAPI only applies to Canadian-resident shareholders)
- This is the cleanest scenario — see Section 7 for departure process

---

## 3. T1141 — Contributions to Non-Resident Trusts

### 3.1 Who Must File

**ITA s.233.2** requires every Canadian resident who "transfers or loans property to a
non-resident trust" (or to a trust that will become non-resident) to file Form T1141.

**"Non-resident trust":** A trust resident outside Canada (determined by where the trustee
exercises control and discretion over the trust property — generally the trustee's residence).

**Filing triggers:**
- Transferring any property (cash, crypto, real estate, shares) to a foreign trust
- Making a loan to a foreign trust at below-market rates
- Providing a guarantee for a foreign trust's obligations
- CC is deemed to have made a contribution if a closely related non-resident also contributes and CC benefits

---

### 3.2 Attribution Rules for Non-Resident Trusts (ITA s.94)

`[WARNING]` This is one of the most complex areas of Canadian tax law.

If CC contributes to a non-resident trust and the trust has **Canadian beneficiaries**, ITA s.94
may deem the trust to be **Canadian-resident** for tax purposes — meaning:

1. The trust must file Canadian T1 returns
2. CC as contributor may be jointly and severally liable for the trust's Canadian tax
3. The trust's worldwide income becomes taxable in Canada

**The planning trap:** Setting up a foreign trust (Jersey, Cayman) and naming CC as beneficiary
while CC is still a Canadian resident triggers s.94 attribution. The structure does not work
until CC is non-resident.

---

### 3.3 Filing Deadline and Penalties

| Item | Details | ITA Authority |
|------|---------|--------------|
| Due date | Same as T1 (April 30 / June 15 self-employed) | s.233.2(4) |
| Late filing penalty | $500/month, maximum $12,000 | s.162(7) |
| If demanded and not filed | Additional penalties; potential s.94 liability | s.162(10) |

---

### 3.4 CC-Specific T1141 Scenarios

`[OASIS]` T1141 is not currently applicable for CC. Future scenarios where it would apply:

1. **Jersey/Guernsey asset protection trust** — CC contributes assets to a Crown Dependencies
   trust while still Canadian-resident → T1141 required every year until departure
2. **Cayman islands investment trust** — same trigger
3. **Family trust structure** — if CC sets up a trust outside Canada for estate/wealth planning

**The practical rule:** Until CC departs Canada, contributing to a foreign trust where CC
remains a beneficiary is tax-neutral at best (s.94 attribution) and administratively burdensome.
The structures become powerful only after Canadian departure.

---

## 4. T1142 — Distributions from Non-Resident Trusts

### 4.1 Who Must File

**ITA s.233.5** requires any Canadian resident who receives a distribution from a non-resident
trust (or is beneficially interested in one) to file Form T1142.

This applies even if:
- The distribution is not taxable (return of capital)
- CC is only a contingent beneficiary (i.e., would inherit if something happened to the primary beneficiary)
- The amount is small

---

### 4.2 What Must Be Reported

For each non-resident trust:
- Name, country, trustee information
- CC's interest: income beneficiary, capital beneficiary, or both
- Distributions received during the year (type and amount)
- Whether the trust is subject to s.94 (deemed Canadian-resident)
- Whether CC has received or is entitled to receive income

---

### 4.3 Filing Deadline and Penalties

| Item | Details | ITA Authority |
|------|---------|--------------|
| Due date | Same as T1 (April 30 / June 15 self-employed) | s.233.5(2) |
| Late filing penalty | $500/month, maximum $12,000 | s.162(7) |

---

### 4.4 CC-Specific T1142 Scenarios

`[OASIS]` Not currently applicable. Would apply if:
- CC is named as beneficiary in a parent's or relative's foreign trust
- CC receives an inheritance through a foreign estate structured as a trust
- CC participates in a foreign employee benefit trust (future, if OASIS has foreign employees)

---

## 5. Transfer Pricing — ITA s.247

### 5.1 What Transfer Pricing Means for CC

Transfer pricing rules govern the prices charged between **related parties** in different
jurisdictions. The purpose is to prevent Canadian taxpayers from shifting profits to low-tax
foreign entities by setting artificial inter-company prices.

**ITA s.247(2):** CRA may adjust the terms of a transaction between CC (or a Canadian company
CC controls) and a related non-resident to arm's length terms. The adjustment is treated as
additional income for CC.

**"Related" for transfer pricing purposes (ITA s.247(1)):** Persons related under s.251
(connected by blood, marriage, adoption, or corporate control). If CC owns 100% of a foreign
company, CC and that company are related — all transactions between them are subject to s.247.

`[OASIS]` Transfer pricing does not apply today (no foreign entity). This section documents
the rules for when CC incorporates abroad while remaining Canadian-resident, or when OASIS
Canada transacts with a CC-owned foreign entity.

---

### 5.2 The Arm's Length Principle

**All related-party cross-border transactions must be priced as if they were between
unrelated parties dealing at arm's length under comparable circumstances.**

This is the OECD standard (OECD Transfer Pricing Guidelines 2022) adopted by CRA (Information
Circular IC87-2R).

---

### 5.3 The Five OECD Transfer Pricing Methods

CRA accepts all five OECD methods. Select the most appropriate based on the nature of the
transaction and available comparables.

#### Method 1: Comparable Uncontrolled Price (CUP)
- Compare the controlled transaction price directly to prices charged in identical or similar
  uncontrolled transactions
- Best method when direct comparables exist
- Example: CC's Irish company licenses SaaS IP to OASIS Canada for a royalty. CUP would compare
  this royalty rate to royalties charged between unrelated parties for similar software IP.
- ITA s.247(1) "arm's length price" — CUP is the most direct test

#### Method 2: Resale Price Method (RPM)
- Start with the resale price to an arm's length customer, subtract a normal gross margin,
  and work backward to the transfer price
- Best for distributors/resellers
- Example: OASIS Canada resells a foreign affiliate's software. If comparable resellers earn
  a 30% margin, the Irish company's price to OASIS Canada should leave OASIS with 30% margin.

#### Method 3: Cost Plus Method (CPM)
- Start with the cost of producing the goods or services, add a normal markup
- Best for manufacturers or service providers
- Example: CC's Guernsey company provides software development services to OASIS Canada.
  If comparable independent contractors charge cost + 15%, the Guernsey company should too.

#### Method 4: Transactional Net Margin Method (TNMM)
- Compare the **net profit margin** of the controlled entity to net margins of comparable
  independent companies performing similar functions
- Most widely used in practice — comparables are easier to find than for CUP
- Example: CC's Irish operating company has a net margin of 35%. If comparable Irish SaaS
  companies earn 25-40% net margins, TNMM analysis confirms the pricing is arm's length.

#### Method 5: Profit Split Method (PSM)
- Split the combined profit of both related entities as independent entities would negotiate
- Used when both parties contribute significant, unique, hard-to-value intangibles
- Most complex — requires detailed functional analysis of both entities
- Example: CC contributes OASIS brand/client relationships; Irish company contributes AI models.
  Split the combined profit based on each party's relative contribution.

---

### 5.4 Documentation Requirements — ITA s.247(4)

`[WARNING]` Documentation must be **contemporaneous** — prepared and finalized by the
T1 filing deadline of the year in which the transaction occurred. You cannot retroactively
document transfer prices after CRA starts asking questions.

**Required documentation elements (s.247(4)(a)):**

1. **Description of the property or services** involved in the transaction
2. **Terms and conditions** — pricing, payment terms, volume, exclusivity
3. **Functional analysis** — what functions does each entity perform? What assets does each use? What risks does each bear?
4. **Comparability analysis** — what comparable uncontrolled transactions or companies were considered?
5. **Transfer pricing method selected** and why it is most appropriate
6. **Application of the method** — the actual calculation showing the arm's length price
7. **Any assumptions or adjustments** made

**Penalty for no documentation (s.247(3)):**

```
Transfer pricing adjustment (CRA reassesses and adds income): $200,000 CAD
Penalty for lack of documentation: 10% of $200,000 = $20,000 CAD
  Note: This is ON TOP of the tax owing on the $200,000 reassessment
  At 46% marginal rate: $92,000 in additional tax
  + $20,000 documentation penalty
  + interest (currently ~8% on overdue amounts)
  Total exposure: ~$115,000+ on a $200,000 adjustment
```

---

### 5.5 Economic Substance — The Non-Negotiable Requirement

`[WARNING]` CRA (and foreign tax authorities) will attack foreign structures that lack
**genuine economic substance**. A shell company with no employees, no physical presence,
and no real operations will not be respected — regardless of legal formation documents.

**What "substance" means in practice:**

| Jurisdiction | Minimum Substance Expected |
|-------------|--------------------------|
| Ireland | Local directors, registered office, actual employees or contractors, company making real decisions locally, books kept locally |
| Guernsey | Adequate economic presence (Guernsey Economic Substance (Companies) Law 2018) — mandatory for certain activity types including finance, banking, IP holding |
| Cayman Islands | Less strict substance requirements, but OECD BEPS Action 5 pressures are increasing |
| US LLC (disregarded) | No corporate substance required at state level, but CC's Canadian residency means GAAR risk |

**Guernsey Substance Law specifics (Finance Law 2018, relevant if CC uses Guernsey):**

For "relevant activity" companies (which includes IP holding and finance), Guernsey requires:
- Core income-generating activities (CIGA) conducted in Guernsey
- Adequate employees, premises, and expenditure in Guernsey
- Directed and managed from Guernsey (board meetings held in Guernsey, majority local directors)
- Failure = automatic reporting to CRA by the Guernsey Revenue Service

---

### 5.6 CC-Specific Transfer Pricing Scenarios

#### Scenario A: IP Royalty (OASIS Canada → Irish IP Holdco)

```
Structure:
  Irish IP Holdco holds the OASIS AI software IP (algorithms, code, models)
  OASIS Canada licenses the IP from Irish company, pays a royalty
  Irish company taxed at 12.5%; Canada deducts the royalty payment

Arm's length royalty rate analysis:
  Industry benchmark: SaaS IP royalties typically 15%–30% of gross revenue
  Lower end (25%): Established brands with large client base
  Upper end (30%+): Novel, proprietary AI technology with no close substitutes
  OASIS (early-stage, growing): 20%–25% is defensible

Example at 20% royalty:
  OASIS Canada revenue: $200,000 CAD
  Royalty paid to Irish HoldCo: $40,000 CAD
  OASIS Canada deduction: $40,000 (reduces Canadian taxable income)
  Irish HoldCo receives: $40,000 CAD equivalent
  Irish tax: 12.5% × $40,000 = $5,000
  Net in Irish HoldCo: $35,000 → exempt surplus if distributed to CC

  Canadian tax saved on royalty deduction (at 46% marginal rate): $18,400
  Irish tax paid: $5,000
  Net benefit: $13,400 on $40,000 royalty

Documentation required:
  - IP assignment agreement (Irish company acquires/owns the IP)
  - License agreement (OASIS Canada pays royalty for use)
  - Royalty rate comparables analysis (software royalty databases)
  - Evidence Irish company has substance (employs developers, holds server IP, etc.)
```

`[WARNING]` For the IP structure to hold, the **IP must be genuinely owned and developed by
the Irish entity**, not just licensed from a pre-existing Canadian owner. CC cannot simply
"move" IP already developed at OASIS Canada to an Irish shell without triggering an ITA
s.56.4 transfer at FMV (which would itself be a taxable event). Ideal: set up the Irish
entity before OASIS develops new IP, and have the Irish entity own new development.

#### Scenario B: Service Fee (OASIS Canada → Guernsey Opco for Development Services)

```
Structure:
  Guernsey Opco employs developers who build features for OASIS
  OASIS Canada pays Guernsey a service fee for development work

Arm's length service fee:
  Method: Cost Plus — cost of Guernsey employees + 10-15% markup
  If Guernsey employs 2 developers at $80K each = $160K costs
  15% markup = $24K
  Arm's length service fee: $184,000 CAD equivalent

  OASIS Canada deduction: $184,000
  Guernsey income: $184,000 (0% Guernsey tax on most income)
  Accumulated as exempt surplus (Guernsey has TIEA with Canada)

Documentation required:
  - Intercompany services agreement (specific SOW, deliverables, timelines)
  - Developer contracts (Guernsey employment agreements)
  - Time records (hours billed to OASIS projects)
  - Comparable contractor rate analysis (what would arm's length developer cost?)
```

#### Scenario C: Post-Departure — Non-Resident CC Invoices Canadian Clients

```
CC is non-resident (departed Canada per Section 7)
CC personally invoices Canadian OASIS clients
No Canadian company involved — no transfer pricing issue

Key risk: Permanent Establishment (PE)
  If CC has an office in Canada, an employee in Canada, or habitually exercises
  a contract-making authority in Canada — CRA may assert a Canadian PE
  PE → Canadian-source business income → taxable in Canada

  Mitigation:
  - No Canadian office, no Canadian employees
  - Do not habitually conclude contracts from Canada
  - Use a non-Canadian email/phone as primary business contact
  - Provide services remotely from new country of residence
```

---

### 5.7 Transfer Pricing Red Flags CRA Monitors

| Red Flag | Why CRA Focuses On It |
|----------|-----------------------|
| Canadian entity consistently loses money while foreign affiliate is profitable | Classic profit-shifting pattern |
| Royalty rate above industry norms without IP substance documentation | IP box abuse |
| Management fees with no clear documentation of services | Disguised dividend |
| Related-party debt at below-market rates (s.17 loans) | Interest stripping |
| Sudden revenue shift to low-tax jurisdiction after restructuring | BEPS flag |
| Foreign affiliate in a tax haven (0% rate) | Automatic enhanced scrutiny |
| Lack of contemporaneous documentation | Penalty trigger + 6-year reassessment |

---

### 5.8 Advance Pricing Arrangement (APA) — ITA s.247(10)

An APA is an agreement between a taxpayer and CRA (sometimes also involving the foreign tax
authority) that pre-approves a specific transfer pricing methodology for a defined period
(typically 3–5 years).

**Benefits:**
- Eliminates transfer pricing audit risk for covered transactions
- Provides certainty for multi-year planning
- Bilateral APA also prevents double taxation by agreeing with the foreign jurisdiction

**Costs:**
- Application fee: $5,000 per application
- Professional costs to prepare: $50,000–$200,000+
- Processing time: 18–36 months

**When it makes sense:**
- Annual related-party transactions exceed $1,000,000 CAD
- Complex structures with unique intangibles
- Prior history of CRA scrutiny on pricing

`[OASIS]` Not warranted at current OASIS scale. Revisit when annual cross-border transactions
exceed $500,000 CAD.

---

## 6. Foreign Tax Credits — ITA s.126

### 6.1 The Core Mechanism

When CC earns income in a foreign country that is also taxable in Canada, Canada avoids double
taxation by granting a **credit** against Canadian tax for taxes paid abroad.

**ITA s.126(1) — Non-business income FTC:**
> Deduct from Canadian tax the lesser of: (a) the foreign tax paid on non-business income,
> or (b) the Canadian tax otherwise payable on that income.

**ITA s.126(2) — Business income FTC:**
> Same principle for business income. But business income FTC has carryforward/carryback rules.

---

### 6.2 Two Categories of Foreign Income

| Category | ITA Section | Carryover? | Notes |
|----------|------------|-----------|-------|
| **Non-business income** (dividends, interest, capital gains from foreign sources) | s.126(1) | None — use it or lose it in the year paid | Most common for passive investors |
| **Business income** (foreign business income, foreign employment income) | s.126(2) | Carry back 3 years, carry forward 10 years | Applies to CC's active business income from foreign clients |

---

### 6.3 The FTC Limitation — Preventing Windfall Credits

The FTC is capped. You cannot use foreign tax paid to reduce Canadian tax on Canadian-source
income — only on the foreign income itself.

**Limitation formula:**

```
FTC Limit = Canadian Tax Payable × (Net Foreign Income / Net Income for Tax Purposes)

Example:
  CC earns $150,000 Canadian income + $50,000 Irish income
  Total net income: $200,000
  Canadian tax on $200,000 at blended rates: $70,000
  Irish tax paid: $6,250 (12.5%)

  FTC Limit = $70,000 × ($50,000 / $200,000) = $17,500
  Actual Irish tax paid: $6,250
  FTC claimed: $6,250 (less than limit — use full amount)
  Net Canadian tax: $70,000 - $6,250 = $63,750

  Effective tax rate: ($6,250 + $63,750) / $200,000 = 35%
  Without FTC: ($6,250 + $70,000) / $200,000 = 38.1%
```

---

### 6.4 "Income or Profits Tax" Requirement

The FTC only applies to taxes that are "income or profits taxes" paid to a foreign government.

**Qualifying:**
- Irish corporate income tax (12.5%)
- US federal income tax
- UK corporation tax
- Guernsey income tax (20% personal rate on individuals resident there)
- Provincial/state income taxes in foreign countries
- Canadian-treaty-country withholding taxes on dividends, interest, royalties (see rates below)

**Not qualifying:**
- VAT / GST (consumption tax, not income tax)
- Social security/CPP equivalents (payroll taxes)
- Stamp duties / transfer taxes
- US state sales taxes

---

### 6.5 Withholding Tax Rates on Foreign Investment Income

`[NOW]` Key treaty withholding rates affecting CC's investment income:

| Country | Dividends (non-RRSP) | Interest | Royalties | ITA s.126(1) credit available? |
|---------|---------------------|----------|-----------|-------------------------------|
| **United States** | 15% (25% if < 10% ownership) | 0% (treaty) | 0% (treaty) | Yes — on dividends |
| **United Kingdom** | 15% | 0% (treaty) | 0% (treaty) | Yes — on dividends |
| **Ireland** | 15% | 0% (treaty) | 0% (treaty) | Yes — on dividends |
| **Germany** | 15% | 0% | 0% | Yes |
| **No treaty / no TIEA** | Up to 30% | Up to 30% | Up to 30% | Yes — but higher cost |

**RRSP exception (US dividends per Article XXI Canada-US Treaty):**
US dividends received inside an RRSP → 0% US withholding. No FTC needed because no foreign
tax is withheld. This is the most tax-efficient placement for US dividend stocks.

---

### 6.6 FTC Planning — Optimal Foreign Tax Rates

```
Canadian marginal rate (CC at ~$100K income, Ontario): ~43.41%

Optimal foreign tax rate for FTC efficiency:
  If foreign rate < Canadian rate:
    → FTC offsets the foreign tax fully
    → Residual difference is still taxed in Canada
    → Effective rate: Canadian marginal rate (no savings, just no double-tax)

  If foreign rate = Canadian rate:
    → FTC offsets entirely, effective rate = Canadian rate
    → No savings — you paid the tax somewhere, just not Canada

  If foreign rate > Canadian rate:
    → FTC capped at Canadian tax on that income
    → Excess foreign tax: non-business FTC → lost; business FTC → 10-year carryforward
    → No benefit from paying MORE tax than Canada would charge

  Strategic sweet spot: Low-tax jurisdiction (12.5% Ireland, 0% Guernsey) combined with
  active business income in exempt surplus treatment → eliminate Canadian layer entirely
  for offshore active income, rather than just crediting foreign tax against Canadian tax.
```

---

### 6.7 CC-Specific FTC Scenarios

`[OASIS]` **Current FTC situations:**

1. **US client payments with 30% withholding (no W-8BEN submitted):**
   If CC's US clients withhold 30% as a non-resident alien before paying CC, that 30% is
   a US income tax — creditable in Canada. BUT: if CC submits Form W-8BEN to US clients,
   the withholding drops to 0% (business income under the Canada-US treaty, Article VII —
   business profits taxable only in Canada unless US PE exists). Submit W-8BEN to avoid
   pre-paying US tax that must later be recovered via FTC.

2. **US dividend withholding in non-registered accounts:**
   Any US-listed ETF or stock held outside registered accounts will have 15% US withholding
   on dividends. Claim s.126(1) FTC on T1. Keep records of withholding: T3 or T5 slips
   from Canadian brokerages show this, or Form 1042-S from US payors.

3. **Kraken trading — US-sourced income:**
   Crypto trading income at Kraken: Kraken is US-incorporated but the trades are between CC
   and counterparties — no US withholding applies to trading gains. This is business income
   taxable only in Canada under Article VII of the Canada-US treaty (no US PE for CC).

---

## 7. Departure from Canada — Final Reporting

### 7.1 The Deemed Disposition — ITA s.128.1(4)

When CC ceases to be a Canadian resident, ITA s.128.1(4) deems CC to have **disposed of and
immediately reacquired** all property (at FMV) at the moment of departure.

**What gets caught in the departure tax net:**

| Property Type | Treatment on Departure |
|---------------|----------------------|
| Crypto (not on Canadian exchanges) | Deemed disposed at FMV — capital gain/loss triggered |
| Foreign stocks | Deemed disposed at FMV |
| Canadian private company shares (OASIS) | Deemed disposed — but elections available |
| Accounts receivable (OASIS) | Included in income if previously deducted |
| Registered accounts (RRSP, TFSA) | EXCLUDED — no deemed disposition |
| Canadian real property | EXCLUDED — taxed by Canada when actually sold (s.116) |
| Pensions (CPP, OAS) | EXCLUDED — remain Canadian-taxed per treaty |

---

### 7.2 The Departure Tax Election (ITA s.220(4.5))

For certain property (typically shares of private corporations), CC can **elect to defer** the
departure tax by posting security with CRA. This is critical for OASIS shares — the company
may be worth millions at departure but CC may not have liquid funds to pay tax on the deemed gain.

**Mechanics:**
- Post acceptable security (letter of credit, government bonds, mortgage on Canadian property)
- CRA allows deferral until the property is actually sold or CC returns to Canada
- Interest accrues on the deferred tax at prescribed rates

---

### 7.3 Forms Required on Departure

| Form | Purpose | ITA Authority |
|------|---------|--------------|
| **T1 (departure year)** | Final T1 for departure year — two periods (resident + non-resident) | s.128.1 |
| **T1161** | List of all property owned at departure (cost + FMV) | s.128.1(9) |
| **T1243** | Deemed disposal of taxable Canadian property on departure | s.128.1 |
| **T1244** | Election to defer payment of departure tax (s.220(4.5)) | s.220(4.5) |
| **Section 116 Certificate** | For future dispositions of taxable Canadian property while non-resident | s.116 |

---

### 7.4 Post-Departure Compliance — Non-Resident Obligations

After CC departs Canada and is confirmed non-resident:

**T1135, T1134, T1141, T1142 — ALL cease.** These forms only apply to Canadian residents.

**Remaining obligations:**

| Obligation | Trigger | Form |
|------------|---------|------|
| Non-resident withholding (Part XIII tax) | Any Canadian-source passive income (rent, interest, dividends from OASIS) | NR4 — payor withholds |
| Section 116 clearance certificate | Selling Canadian real property or OASIS shares while non-resident | T2062 |
| Non-resident rental filing | If CC rents Canadian real property | Section 216 election or NR6 |
| CPP/OAS pension (when age-eligible) | Pension income from Canada | Part XIII withholding (may elect s.217) |

---

## 8. Decision Trees

### 8.1 T1135 Decision Tree

```
START: Did CC hold any "specified foreign property" at any time this tax year?
│
├─ NO → No T1135 required. Stop.
│
└─ YES → Calculate total COST BASIS (not FMV) of all specified foreign property
          at any point during the year
          │
          ├─ Total cost < $100,000 CAD → No T1135 required. Document calculation.
          │
          └─ Total cost ≥ $100,000 CAD → T1135 REQUIRED
                    │
                    ├─ Maximum cost at any point < $250,000 → USE SIMPLIFIED METHOD
                    │    File T1135 Part A: categories, countries, max cost, year-end
                    │    cost, income earned, dispositions
                    │
                    └─ Maximum cost at any point ≥ $250,000 → USE DETAILED METHOD
                         File T1135 Part B: list every property individually
```

### 8.2 T1134 Decision Tree

```
START: Does CC own shares of any non-resident (foreign) corporation?
│
├─ NO → No T1134 required. Stop.
│
└─ YES → Does CC own ≥ 1% of any class of shares?
          AND together with related parties ≥ 10%?
          │
          ├─ NO → No T1134 required.
          │
          └─ YES → "Foreign affiliate" — T1134 REQUIRED
                    │
                    ├─ Does CC (+ up to 4 related Canadians) own > 50% → CFA
                    │    → FAPI rules apply to passive income (s.91)
                    │    → T1134 Part 1 + Part 2 Supplement required
                    │
                    └─ Ownership ≤ 50% → Non-controlled foreign affiliate
                         → No FAPI — only actual dividends taxed
                         → T1134 Part 1 required; Part 2 if applicable
```

### 8.3 Transfer Pricing Decision Tree

```
START: Did CC (or a CC-controlled Canadian entity) transact with a related
       non-resident entity this year?
│
├─ NO → No transfer pricing documentation required.
│
└─ YES → What type of transaction?
          │
          ├─ Sale/transfer of property (including IP) → Document FMV, method used
          │    Risk of s.56.4 if IP transferred below FMV
          │
          ├─ Service fees / management fees → Cost Plus preferred
          │    Document: actual services, comparable rates, time records
          │
          ├─ Royalties / licensing → CUP or TNMM preferred
          │    Document: IP description, royalty rate comparables, usage terms
          │
          └─ Loans / financial transactions → s.17 rules (non-arm's-length loans to
               non-residents) → must charge commercial interest rates or income inclusion
               │
               Does annual related-party transactions exceed $1M CAD?
               ├─ YES → Consider APA (s.247(10))
               └─ NO → Contemporaneous documentation still required; APA not yet warranted
```

---

## 9. CC-Specific Compliance Checklist

### Phase 1: Current (Canadian Resident, Sole Proprietor, No Foreign Entities)

- [ ] **Annually:** Calculate total cost basis of all specified foreign property
  - Wise USD account: convert balance to CAD at year-end exchange rate → record as cost
  - Kraken account: sum all CAD-equivalent deposits → this is cost basis (not current value)
  - Any other foreign accounts or property → include in total
- [ ] **If total cost < $100,000 CAD:** Document the calculation and file. No T1135 needed.
- [ ] **If total cost ≥ $100,000 CAD:** File T1135 by June 15 (self-employed deadline)
- [ ] Report all foreign income on T1 (worldwide income principle)
- [ ] Claim s.126 FTC for any foreign taxes withheld (check T3/T5 slips for withholding)
- [ ] Submit Form W-8BEN to all US clients to eliminate 30% US withholding at source
- [ ] Hold foreign investments in TFSA/RRSP where possible to stay below T1135 threshold

### Phase 2: Future (If CC Incorporates Foreign Entity While Still Canadian Resident)

- [ ] File T1134 annually (within 15 months of foreign entity fiscal year-end)
- [ ] Calculate FAPI quarterly — identify any passive income in CFA and include in T1
- [ ] Prepare transfer pricing documentation by T1 filing deadline (contemporaneous)
- [ ] Draft and execute intercompany agreements before transactions occur
  - IP license agreement (if royalty structure)
  - Intercompany services agreement (if service fee structure)
  - Intercompany loan agreement with arm's length interest rate (if loan)
- [ ] Ensure foreign entity has genuine economic substance (employees, premises, local directors)
- [ ] Monitor exempt surplus vs taxable surplus balances on T1134
- [ ] Confirm Guernsey Economic Substance Law compliance (if Guernsey entity)
- [ ] Do NOT hold passive investments inside the foreign CFA (FAPI trap — see 2.4)

### Phase 3: Departure from Canada (FIRE or Geographic Arbitrage)

- [ ] File final T1 covering both resident and non-resident periods
- [ ] File T1161 (list of all property at departure date with cost and FMV)
- [ ] File T1243 (deemed disposal of applicable property)
- [ ] Consider T1244 election to defer departure tax on OASIS shares (post security)
- [ ] File Section 116 certificate request for any taxable Canadian property to be sold post-departure
- [ ] Establish new tax residency in target country before filing departure return
- [ ] Close or transfer Canadian bank accounts as appropriate
- [ ] Notify OASIS clients, suppliers of new invoicing entity/jurisdiction
- [ ] After departure: T1135, T1134, T1141, T1142 obligations cease entirely
- [ ] Set up NR4 withholding arrangements if any Canadian passive income will continue

---

## 10. Key ITA Reference Index

| ITA Section | Topic |
|------------|-------|
| **s.9(1)** | Business income — profit principle |
| **s.91(1)** | FAPI inclusion — shareholder's income from CFA |
| **s.91(4)** | Foreign tax deduction for FAPI |
| **s.94** | Non-resident trusts — deemed Canadian residency |
| **s.95(1)** | Foreign affiliate definitions — exempt surplus, taxable surplus, FAPI |
| **s.95(2)** | Active business income definition for foreign affiliates |
| **s.113(1)** | Dividend deduction for dividends from foreign affiliates |
| **s.113(1)(a)** | Exempt surplus dividend — zero Canadian tax |
| **s.113(1)(b)** | Hybrid surplus dividend — 50% taxable |
| **s.113(1)(c)** | Taxable surplus dividend — fully taxable, FTC available |
| **s.126(1)** | Non-business income foreign tax credit |
| **s.126(2)** | Business income foreign tax credit — 3-year carryback, 10-year carryforward |
| **s.128.1(4)** | Deemed disposition on departure from Canada |
| **s.128.1(9)** | T1161 property reporting obligation on departure |
| **s.152(4)(b.2)** | Extended 6-year reassessment for unreported foreign income / unfiled T1135 |
| **s.162(7)** | Penalty for late information returns — $25/day, max $2,500 |
| **s.162(10)** | Penalty after CRA demand — $500/month, max $12,000 |
| **s.162(10.1)** | T1134 penalty after demand — $1,000/month, max $24,000 |
| **s.163(2.4)** | Gross negligence T1135 penalty — $1,000/month, max $24,000 |
| **s.220(4.5)** | Election to defer departure tax by posting security |
| **s.233.2** | T1141 filing obligation — contributions to non-resident trusts |
| **s.233.3** | T1135 filing obligation — foreign income verification |
| **s.233.3(1)** | Definition of "specified foreign property" |
| **s.233.4** | T1134 filing obligation — foreign affiliates |
| **s.233.5** | T1142 filing obligation — distributions from non-resident trusts |
| **s.247(1)** | Transfer pricing definitions |
| **s.247(2)** | CRA adjustment authority for non-arm's-length cross-border transactions |
| **s.247(3)** | 10% documentation penalty |
| **s.247(4)** | Contemporaneous documentation requirements |
| **s.247(10)** | Advance Pricing Arrangement |
| **s.251** | Definition of related persons |

**Other authorities referenced:**
- CRA Information Circular **IC87-2R** — Transfer pricing guidelines
- OECD **Transfer Pricing Guidelines 2022** — adopted by CRA for all five methods
- **Canada-Ireland Tax Treaty** (1967, as amended) — 15% dividend withholding, 0% interest/royalties
- **Guernsey-Canada TIEA** (2011) — qualifies Guernsey income for exempt surplus treatment
- **Canada-US Convention** (1980, as amended by 5 Protocols) — Article VII (business profits), XIII (capital gains), XXI (exempt organizations including RRSP)
- **Guernsey Economic Substance (Companies) Law 2018** — substance requirements for relevant activity companies
- **CRA T1135 Guide** (RC4139) — simplified vs detailed method threshold and instructions
- **CRA Folio S5-F2-C1** — Foreign tax credit

---

*Document prepared by ATLAS (CC's CFO Agent). Last updated: 2026-03-27.*
*CC reviews and files via NETFILE. ATLAS does not have CRA login access.*
*Cross-reference: ATLAS_TREATY_FIRE_STRATEGY.md (departure tax detail), ATLAS_INCORPORATION_TAX_STRATEGIES.md (CCPC structures), CRA_CRYPTO_ENFORCEMENT_INTEL.md (crypto reporting enforcement), ATLAS_AI_SAAS_TAX_GUIDE.md (SR&ED, IP structures), ATLAS_BUSINESS_STRUCTURES.md (Irish/Guernsey entity setup).*
