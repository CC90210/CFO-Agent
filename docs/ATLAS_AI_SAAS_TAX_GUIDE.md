# ATLAS — AI/SaaS Business Tax Guide

> **For:** Conaugh McKenna (CC), OASIS AI Solutions, Collingwood Ontario
> **Jurisdiction:** Canada (Ontario) | **Tax year:** 2025-2026 (planning)
> **Last Updated:** 2026-03-27
> **Purpose:** Definitive tax reference for CC's AI/SaaS revenue streams — SR&ED claims, OIDMTC analysis,
> DST thresholds, IP structures, international revenue, open source monetization, and compute cost deductibility.
> All ITA references are to the *Income Tax Act (Canada)*, R.S.C. 1985, c.1 (5th Supp.) unless noted.
> ETA references are to the *Excise Tax Act*, R.S.C. 1985, c.E-15.

**Tags used throughout:**
- `[NOW]` — Actionable today as a sole proprietor at OASIS's current revenue
- `[FUTURE]` — Relevant upon incorporation or significant revenue growth
- `[OASIS]` — Specific to CC's actual business situation, named and applied directly

---

## Table of Contents

1. [SaaS Revenue Recognition](#1-saas-revenue-recognition)
2. [Digital Services Tax (DST)](#2-digital-services-tax-dst)
3. [SR&ED for AI/ML Development](#3-sred-for-aiml-development)
4. [OIDMTC — Ontario Interactive Digital Media Tax Credit](#4-oidmtc)
5. [IP Tax Treatment and CCA](#5-ip-tax-treatment-and-cca)
6. [AI Training and Compute Costs](#6-ai-training-and-compute-costs)
7. [International SaaS Revenue and GST/HST](#7-international-saas-revenue-and-gsthst)
8. [Open Source Monetization](#8-open-source-monetization)
9. [SaaS Metrics and Tax Planning](#9-saas-metrics-and-tax-planning)
10. [Contractor vs Employee Classification](#10-contractor-vs-employee-classification)
11. [Cloud Credits and Government Grant Tax Treatment](#11-cloud-credits-and-government-grant-tax-treatment)
12. [Key ITA/ETA Reference Index](#12-key-itaeta-reference-index)
13. [OASIS Action Matrix](#13-oasis-action-matrix)

---

## 1. SaaS Revenue Recognition

### 1.1 The Core Rule: Earned vs Received

Under CRA's matching principle (consistent with ASPE 3400 and IFRS 15), income is recognized when
**earned**, not when cash is received. For SaaS, subscription revenue is recognized as services are
delivered across the subscription period — not on the date of payment.

**ITA authority:** s.9(1) — business income is the profit therefrom, calculated on accrual principles.
s.12(1)(a) — amounts received for services not yet rendered must be included in income when received.

The problem this creates: a client pays $12,000 in November for a 12-month OASIS contract. Under s.12(1)(a),
the full $12,000 is taxable in November's tax year, even though 11 months of service will be delivered
in the following year.

### 1.2 The s.20(1)(m) Reserve — The Deferral Tool

ITA s.20(1)(m) allows a deduction for a "reasonable reserve" for services to be rendered after year-end.
The reserve reverses the s.12(1)(a) inclusion on a pro-rated basis.

**Mechanics:**
1. Include full payment in income under s.12(1)(a)
2. Deduct a reserve under s.20(1)(m) for the unearned portion
3. The prior year's reserve is added back under s.12(1)(e) in the next year
4. A new reserve is claimed for that year's unearned balance
5. Net effect: a rolling one-year deferral, not permanent elimination

**Calculation example:**

| Item | Amount |
|------|--------|
| Annual OASIS contract sold November 1, 2026 | $12,000 |
| Service delivered in 2026 (Nov + Dec = 2 months) | $2,000 |
| s.20(1)(m) reserve claimable | $10,000 |
| Taxable in 2026 | $2,000 |
| Added back to 2027 income (s.12(1)(e)) | $10,000 |
| Fresh 2027 reserve (if same contract continues) | Pro-rated to remaining undelivered months |

**Reserve constraints:**
- Must be "reasonable" — CRA reads this as proportional to undelivered service
- Cannot exceed the amount included in income
- Applies to services not yet delivered, NOT goods already delivered
- Must be documented with contract start dates and service delivery records

### 1.3 Monthly vs Annual Plans — Tax Comparison

| Plan Type | Tax Treatment | Best For |
|-----------|---------------|----------|
| Monthly billing | Revenue equals cash received each month. No reserve. Clean. | Simplicity, early stage |
| Annual (prepaid) | Full amount included via s.12(1)(a). Claim s.20(1)(m) reserve for unearned months. | Cash flow — one-year tax deferral |
| Quarterly | Same as annual, smaller reserve amounts | Middle ground |
| Usage-based (API calls) | Recognized as consumed. No reserve needed. | Variable-output AI products |
| Non-refundable setup fee | Recognized over expected customer lifetime per ASPE 3400, not immediately. | Multi-phase engagements |

`[OASIS]` **Strategic timing:** If CC sells annual OASIS contracts, close them in January — most
of the 12-month period falls in the same tax year, minimizing the reserve calculation and simplifying
accounting. A November sale creates a large reserve and administrative tracking burden.

### 1.4 ASPE 3400 vs IFRS 15

| Standard | Applies To | Key Principle |
|----------|-----------|---------------|
| **ASPE 3400** | Private Canadian companies (OASIS post-incorporation) | Revenue recognized when risks/rewards transferred, amount determinable, collectibility probable |
| **IFRS 15** | Public companies or those choosing IFRS | 5-step model: contract → performance obligations → transaction price → allocate → recognize |

`[FUTURE]` OASIS follows **ASPE 3400** post-incorporation. For CRA purposes, both standards
converge on the same earned-revenue principle. ASPE is the correct and simpler standard for a private CCPC.

### 1.5 Deferred Revenue on the Balance Sheet

`[FUTURE]` Post-incorporation, deferred revenue appears as a **liability**. It reduces current-year
taxable income and defers tax — an interest-free loan from CRA. At $100K+ ARR, strategic annual plan
timing can shift $20K-$40K of taxable income into the following year.

### 1.6 Documentation Requirements

Keep all of the following for 6 years (CRA reassessment window is normally 3 years; 6 years for
cases involving negligence or fraud):
- Contract dates (start, end, renewal) for every subscription
- Monthly service delivery records or usage logs
- Reserve calculation working papers
- Invoice dates vs payment dates
- Refund records and policies

---

## 2. Digital Services Tax (DST)

### 2.1 What It Is

Canada's **Digital Services Tax Act** (DSTA), effective January 1, 2024, imposes a **3% levy** on
in-scope Canadian digital services revenue.

`[NOW]` **CC does not currently meet DST thresholds.** This section documents the thresholds for
growth-trajectory tracking.

### 2.2 DST Thresholds — BOTH Must Be Met

| Threshold | Amount | Notes |
|-----------|--------|-------|
| Global consolidated revenue (all sources, all entities) | **≥ EUR 750M (~CAD $1.1B)** | The multinational test — designed to target global tech platforms |
| Canadian in-scope digital services revenue | **≥ CAD $20M** | Revenue attributable to Canadian users specifically |

**Conclusion:** DST targets Amazon, Google, Meta, Netflix. At OASIS's current scale, even $500K ARR
is 2.5% of the Canadian threshold. No exposure.

### 2.3 In-Scope Revenue Categories

When relevant in future, DST applies to:
- Online marketplace services (platform transaction fees)
- Online advertising services (ad revenue)
- Social media platform services (user-generated content monetization)
- User data sales or data licensing

**Out of scope for OASIS:** Direct SaaS subscriptions where CC delivers a software service to a paying
client. A client paying $1,000/month for OASIS AI automation is a direct B2B service contract — not
an online marketplace, not advertising, not a data sale. OASIS's core revenue model is structurally
outside the DST even as it scales.

### 2.4 DST Indirect Effects — Cost Pass-Through

Even if OASIS never pays DST, major platforms have passed their DST costs to advertisers:

- **Google Ads / Meta Ads:** Pricing in Canada absorbs ~3% DST cost passthrough. Factor into CAC.
- **App stores (Apple/Google):** Commission structures may shift to embed DST costs. Monitor if OASIS
  ever distributes via app stores.
- **AWS/GCP/Azure:** Cloud providers have not publicly announced DST pass-through to Canadian customers
  as of 2026. Watch pricing changes in the cloud billing dashboard.

### 2.5 OECD Pillar One — The Global Context

The OECD Pillar One (Amount A) framework is designed to replace unilateral DSTs with a multilateral
profit-allocation system. Canada committed to withdraw the DST once Pillar One is ratified. As of 2026,
ratification remains stalled. The DST stays in effect. Irrelevant to OASIS operationally but worth
monitoring as it signals the direction of global digital taxation.

---

## 3. SR&ED for AI/ML Development

### 3.1 Overview — The Most Valuable Credit in Canadian Tech

SR&ED (Scientific Research and Experimental Development) is Canada's primary R&D tax incentive,
delivering up to **35% refundable** cash-back on eligible R&D expenditures for CCPCs.

**ITA authority:** s.37 (SR&ED expenditure deduction), s.127(5) and s.127(9) (investment tax credit),
Regulation 2900 (prescribed proxy amount), IT-151R5 (software SR&ED guidance).

| Entity Type | SR&ED ITC Rate | Refundable? | Notes |
|-------------|---------------|-------------|-------|
| Sole proprietor (CC now) | **20%** | Non-refundable | Reduces federal tax owing |
| CCPC (OASIS incorporated) | **35%** | Refundable up to expenditure limit | Cash paid by CRA even if no tax owing |
| CCPC — Ontario OITC | **+8%** | Refundable | Additional provincial credit |
| CCPC combined (ON) | **~43%** | Refundable | On first $3M of qualified expenditure |

`[FUTURE]` Post-incorporation: SR&ED becomes a cash-generation engine, not just a tax reducer.

### 3.2 The Three-Part Eligibility Test

CRA requires **all three** to be satisfied (Reg. 2900(1)):

| Condition | What It Means in Practice |
|-----------|--------------------------|
| **1. Scientific or technological advancement** | The work must attempt to advance knowledge or achieve a capability not previously known. The question "can this be done at all?" must genuinely exist. |
| **2. Scientific or technological uncertainty** | The outcome cannot be known in advance by a competent professional. Genuine technical risk must be present — not commercial risk or business uncertainty. |
| **3. Systematic investigation** | Hypothesis → experiment → analysis → conclusion. Scientific method must be documented in real time. Retroactive documentation is a red flag. |

**The threshold question CRA asks:** Would a competent professional in the field know the answer to the
technical problem without performing the experimental work? If yes — not SR&ED. If no — potentially SR&ED.

### 3.3 OASIS Activity Eligibility Analysis

`[OASIS]` CC's specific work and its SR&ED eligibility:

| Activity | Eligible? | Rationale |
|----------|-----------|-----------|
| ATLAS novel regime detection algorithm (ML classification) | **YES** | Genuine technological uncertainty in optimal architecture for financial time-series regime classification |
| Custom market microstructure analysis (order flow, CVD divergence) | **YES** | Non-standard application requiring systematic investigation |
| Walk-forward validation methodology for non-stationary financial data | **LIKELY YES** | Advancement in validation methodology beyond industry-standard backtesting |
| Monte Carlo risk modeling with custom distribution assumptions | **LIKELY YES** | Custom statistical advancement if non-standard models are tested |
| Standard CCXT API integration | **NO** | Routine professional practice. Known outcome. |
| UI dashboard / frontend development | **NO** | Routine software development. No technical uncertainty. |
| Bug fixes and maintenance | **NO** | Routine. |
| Calling Anthropic/OpenAI API with standard prompts | **NO** | Known outcome. API integration is not SR&ED. |
| Fine-tuning or training custom models on proprietary financial data | **YES** | Genuine uncertainty in training outcomes and model behavior |
| Novel prompt engineering with systematic A/B testing | **GREY AREA** | Requires evidence of systematic experimental methodology and genuine uncertainty |
| Custom AI pipeline for OASIS clients (novel architecture) | **CASE BY CASE** | Novel architectures under uncertainty qualify; gluing known APIs does not |
| AI automation workflows (n8n + existing APIs) | **NO** | Assembling existing tools. Competent professional knows the outcome. |

### 3.4 Eligible Expenditures — What Can Be Claimed

| Cost Category | Eligible % | Notes |
|---------------|-----------|-------|
| Salary/wages (own salary from OASIS Corp) | 100% | Must document time by project |
| Contractor fees (arms-length, Canadian) | 80% | Must be for SR&ED work |
| Materials **consumed** in SR&ED | 100% | Destroyed or transformed. Cloud compute consumed during training qualifies. |
| Overhead — Prescribed Proxy Amount (PPA) | 55% of eligible labour | Simpler than tracking actual overhead. Avoids overhead disputes with CRA. |
| Equipment used exclusively for SR&ED | 100% (Class 10 CCA or immediate expensing) | Pro-rated if dual use |
| Leased space for SR&ED | Pro-rated | Must document SR&ED use vs commercial use |

**What CANNOT be claimed:**
- Capital expenditures (claim CCA separately)
- Selling, marketing, administration costs
- Quality control testing
- Social sciences research
- Data collection or market research

### 3.5 SR&ED Claim Walkthrough — OASIS Dollar Estimates

`[OASIS]` Three scenarios illustrating real-world SR&ED numbers:

---

**Scenario A — Sole Proprietor (NOW)**

```
CC earns $45,000 net from OASIS in 2026.
SR&ED time: 35% of CC's working hours on qualifying algorithm development.

[Note: Sole proprietors CANNOT deduct their own labour as SR&ED expenditure —
only out-of-pocket costs count. This is a critical distinction.]

Qualifying expenses (third-party only):
  Cloud GPU compute during model development (documented): $2,800
  External ML contractor (arms-length, SR&ED work):         $8,000
  Materials consumed in experiments:                          $400
  Total eligible expenditure:                              $11,200

Federal ITC at 20% (non-refundable):   $2,240
Applied against CC's federal tax owing: up to $2,240 tax reduction

Estimated annual benefit as sole proprietor: $1,500 – $3,000/year
(Depends on actual tax owing — non-refundable means benefit capped at tax bill)
```

---

**Scenario B — CCPC, Conservative (FUTURE: Post-Incorporation, Year 1)**

```
OASIS Corp pays CC a salary of $55,000.
SR&ED-qualifying time: 40% of CC's billable hours.

Eligible labour:                   $55,000 × 40%  = $22,000
Overhead (PPA, 55% of labour):     $22,000 × 55%  = $12,100
Cloud compute consumed in training:                  $3,200
External SR&ED contractor:                           $6,000
Total eligible SR&ED pool:                          $43,300

Federal ITC at 35% (refundable):   $43,300 × 35% = $15,155
Ontario OITC at 8% (refundable):   $43,300 × 8%  =  $3,464
Total cash refund from CRA:                        $18,619/year
```

---

**Scenario C — CCPC, Growth Stage (FUTURE: $150K ARR, hires one developer)**

```
OASIS Corp employs CC ($65,000 salary) + 1 developer ($70,000 salary).
SR&ED time: CC 50%, developer 80%.

CC eligible labour:           $65,000 × 50% = $32,500
Developer eligible labour:    $70,000 × 80% = $56,000
Total eligible labour:                        $88,500
Overhead PPA (55%):           $88,500 × 55% = $48,675
Cloud compute (training):                      $8,400
Third-party data licensing:                    $4,200
Total eligible SR&ED pool:                   $149,775

Federal ITC at 35%:           $149,775 × 35% = $52,421
Ontario OITC at 8%:           $149,775 × 8%  = $11,982
Total cash refund:                             $64,403/year
```

This is the compounding effect of SR&ED at scale: OASIS essentially gets 43% of its R&D labor costs
back in cash. The developer's full salary net effective cost drops from $70,000 to ~$40,000.

### 3.6 Documentation — The Difference Between Approval and Denial

SR&ED claims are reviewed by CRA at roughly 20% of filed claims. Software SR&ED is scrutinized at
higher rates due to historic abuse. Documentation is the only defense.

**Required contemporaneous records:**
- Project technical descriptions explaining the specific technological uncertainty
- Hypothesis and experimental design per project (written before work begins)
- Git commit logs with descriptive messages (CRA accepts as lab notebook equivalent)
- Time logs per project, per week, per employee (approximate is acceptable; complete absence is not)
- Cloud billing statements filterable by project/tag
- Results documentation — negative results prove systematic investigation as clearly as positive ones

`[OASIS]` **Immediate action:** Create a `sred/` directory in the ATLAS repository. For every novel
algorithm development session, commit a short entry: what technical uncertainty existed, what hypothesis
was tested, what experiment was run, what was learned. Two paragraphs per session, committed with the
code change. This costs 5 minutes per session and builds a multi-year audit-ready record.

**CRA audit risk for SR&ED:** HIGH (routine program-level review, not a personal flag). Use an SR&ED
consultant for the first CCPC claim — they work on contingency (typically 10-15% of the refund) and
understand CRA's technical review process. The consultant fee is itself a deductible business expense.

### 3.7 Filing Mechanics

- File **Form T661** (SR&ED Expenditures Claim) with the T1 (sole proprietor) or T2 (corporation)
- **Deadline for SR&ED:** 18 months after the end of the tax year (extended beyond the normal T1/T2 deadline)
- CRA may issue a Form T1240 (Ruling Request) for pre-approval on specific project eligibility
- CCPC expenditure limit phase-out: the $3M expenditure limit begins reducing when prior-year taxable
  capital exceeds $10M. Not applicable to OASIS for the foreseeable future.

---

## 4. OIDMTC

### 4.1 What It Is

The **Ontario Interactive Digital Media Tax Credit** (OIDMTC) is a **40% refundable** provincial tax
credit on eligible Ontario labour and marketing/distribution expenditures for qualifying interactive
digital media products.

**Authority:** Ontario Taxation Act, 2007, s.91-108. Administered by **Ontario Creates** (OMDC).
Requires a CCPC with a permanent establishment in Ontario.

`[FUTURE]` Applicable only post-incorporation.

### 4.2 Qualifying Product Test

A product qualifies if it is primarily designed to **entertain, educate, or inform** a user AND requires
**user interaction** to navigate its content. The product must also incorporate at least **two of:**

1. Text
2. Sound
3. Images (static)
4. Moving images

**Critical requirement:** The product must be a standalone product sold or licensed to the public —
not solely an internal business tool or a client-services deliverable.

### 4.3 OASIS Products — Eligibility Analysis

`[OASIS]` Can any OASIS product qualify?

**ATLAS Trading Platform (internal use only):**
Not eligible. ATLAS is an internal tool used to manage CC's own trading. It is not a product sold
to the public. The OIDMTC requires a product distributed externally.

**Hypothetical "ATLAS Analytics" SaaS product (market regime analysis, financial education, signal reports):**

| Criterion | Assessment |
|-----------|-----------|
| Primarily educational/informational? | Yes — market analysis, regime intelligence, financial literacy content | PASSES |
| Requires user interaction to navigate? | Yes — dashboard navigation, report drilling, command-driven queries | PASSES |
| 2+ of text/sound/images/moving images? | Text (analysis reports) + charts/images (regime visualizations) | PASSES |
| Sold to the public as a product? | If sold externally as a SaaS subscription — YES | PASSES IF STRUCTURED AS PRODUCT |
| Not primarily transactional? | A pure trade-execution product FAILS. An analytics/education product PASSES. | KEY DESIGN DECISION |

**OIDMTC verdict:** If CC builds a version of ATLAS or OASIS analytical tools as an externally-sold
SaaS product — a **financial analytics and AI education platform** — it has a credible path to OIDMTC
eligibility. The product must be designed and marketed as educational/informational, not as a trading
execution tool.

**Estimated credit if a qualifying OASIS product is built:**

```
Ontario eligible labour on qualifying product: $35,000/year
OIDMTC at 40%: $14,000 refundable cash (Ontario only)
Combined with SR&ED (if qualifying R&D work overlaps): additive
```

**NOTE:** SR&ED and OIDMTC can stack on DIFFERENT labour costs. They cannot apply to the same dollar
of expenditure. Keep separate timesheets: OIDMTC tracks product-building labour; SR&ED tracks
experimental/R&D labour.

### 4.4 OMDC Pre-Certification

Ontario Creates offers **pre-certification** before the credit is claimed. This is strongly recommended:
- Confirms product eligibility before spending resources
- Reduces audit risk (CRA cannot disallow a credit that OMDC has pre-certified)
- Must be applied for at the **product design stage**, not after development is complete

`[OASIS]` If CC plans to productize any OASIS analytics capability for external clients, apply for
OMDC pre-certification during the design phase. The application requires a product description,
business plan, and budget. Processing takes 4-8 weeks.

**CRA audit risk for OIDMTC:** MEDIUM. OMDC pre-certification reduces risk substantially. The main
risk is characterization — CRA may challenge whether the product is "interactive digital media" vs a
transactional financial service. The design and marketing of the product (educational/informational
framing) is the primary defense.

---

## 5. IP Tax Treatment and CCA

### 5.1 Internally Developed Software

OASIS's codebase — ATLAS, client automation tools, AI pipelines — is internally developed software.
The default tax treatment for development costs is **current expense** deductibility, not capitalization.

CRA position (confirmed via IT-283R2 and subsequent technical interpretations):
- Contractor fees for development: current expense, deductible in year incurred
- Cloud compute used during development: current expense
- Third-party API costs during development: current expense
- CC's own time (sole proprietor): NOT deductible — sole proprietor labour is not a business expense

This is one of the most favorable treatments available. OASIS can deduct its entire development cost
base in the year incurred, creating immediate tax reduction rather than multi-year amortization.

### 5.2 CCA Classes for Software and IP

When OASIS **purchases** software or IP (rather than developing it):

| Asset Type | CCA Class | Rate | Notes |
|------------|-----------|------|-------|
| Application software (licenses, COTS tools) | **Class 12** | 100% | Half-year rule: 50% in Year 1. Immediate expensing available for CCPCs. |
| Systems software (OS, databases) | **Class 12** | 100% | Same treatment |
| Custom software purchased from a third party | **Class 12** | 100% | Full cost, including implementation |
| Patents | **Class 44** | 25% (declining balance) | For acquired patents |
| Trademarks, goodwill, indefinite-life IP | **Class 14.1** | 5% (declining balance) | Replaced eligible capital property system post-2017 |
| Computer hardware (workstations, servers) | **Class 50** | 55% (declining balance) or immediate expensing | Eligible for full immediate expensing as CCPC |

### 5.3 Immediate Expensing — 2021 Budget Rule

`[NOW]` Sole proprietors and `[FUTURE]` CCPCs can claim **100% CCA in the year of purchase** on
eligible depreciable property, up to **$1.5M per year**. Eligible classes include Class 12 (software),
Class 10 (most equipment), Class 50 (computer hardware).

`[OASIS]` GPU workstation, development laptops, monitors, external storage: 100% expensed in Year 1.
Do not spread across 3-5 years. The half-year rule is overridden by the immediate expensing election.

Immediate expensing does NOT apply to: Class 1 (buildings), Class 14.1 (indefinite-life IP), rental
properties, or property acquired from a non-arm's-length party.

### 5.4 IP Holding Company Structure

`[FUTURE]` Advanced IP planning for OASIS at $200K+ ARR:

```
CC (Individual)
  └── HoldCo (IP ownership, passive investment income)
        └── OASIS OpCo (active business operations, client revenue)
              - OpCo licenses IP from HoldCo at arms-length FMV
              - Licensing fees are deductible to OpCo (reduces active business income)
              - Royalty income flows to HoldCo (taxed at passive rate, retained for investment)
              - HoldCo shares may qualify for LCGE on sale if structured as QSBC
```

**Benefits:**
- Asset protection: IP is shielded if OpCo faces litigation
- Income splitting potential (if a family trust holds HoldCo shares)
- LCGE preservation: HoldCo shares can qualify for the $1,016,602 (2024, indexed) exemption
- Sale flexibility: sell OpCo without transferring IP, or license IP to acquirer

**Transfer pricing requirements (ITA s.247):**
- Licensing royalty must be at arm's-length fair market value
- CRA scrutinizes related-party IP licensing aggressively
- Get a transfer pricing study from a specialist before implementing
- GAAR (s.245) risk if the structure lacks business substance beyond tax minimization

**When to implement:** Not at OASIS's current scale. Trigger: incorporation complete, meaningful IP
with determinable value ($50K+ in development costs), revenue exceeding $150K, and a CPA/tax lawyer
structuring it properly.

---

## 6. AI Training and Compute Costs

### 6.1 Expense vs Capital — The Framework

Deductibility of AI development costs turns on whether the spend is **consumed** (current expense) or
creates an **enduring asset** (capital/CCA).

| Cost Type | Treatment | Rationale |
|-----------|-----------|-----------|
| Cloud compute for model training (AWS/GCP/Azure GPU hours) | **Current expense** | Consumed in the period. No enduring physical asset. Analogous to SaaS subscription. |
| Cloud compute for production inference | **Current expense** | Ongoing cost of delivering the service. Cost of goods sold. |
| On-premise GPU workstation purchase | **Class 50 CCA (55%)** or immediate expensing | Physical equipment. Depreciable property. |
| API subscription costs (Anthropic, OpenAI, Cohere) | **Current expense** | Recurring service fee, not an asset purchase. |
| Pre-trained model license (perpetual) | **Class 12 (100%)** | Software license. One-time purchase with enduring value. |
| Pre-trained model license (annual subscription) | **Current expense** | Recurring subscription. Not a capital acquisition. |
| Training dataset purchase (perpetual, unique) | **Class 14.1 (5%)** or current expense | If dataset has enduring commercial value, it is a capital intangible. If consumed/refreshed annually, it is current. |
| Training dataset subscription (annual refresh) | **Current expense** | Recurring data fee. |
| Data labeling/annotation services | **Current expense** | Contractor services for data preparation. |
| Model fine-tuning costs (third-party GPU rental) | **Current expense** | Analogous to software customization — not a capital acquisition. |
| Model hosting (Replicate, Modal, RunPod) | **Current expense** | Cost of delivering the service. |

### 6.2 Anthropic Claude API — OASIS Business Expense

`[NOW]` `[OASIS]` Claude API costs are **100% deductible** as business expenses under s.18(1)(a)
(expenses incurred to earn income from a business). This is unambiguous.

**Keep:** Monthly invoices from console.anthropic.com billing. Download and store as PDFs organized
by month. Categorize as "computer and internet expenses" or "AI/ML API costs" on T2125.

**If CC uses Claude personally AND for business:** Prorate. Estimate the business percentage and
document the methodology. A 70/30 business/personal split is defensible if OASIS generates material
income from Claude usage. A 100% business deduction requires that personal use is truly negligible.

**CRA audit risk:** NEGLIGIBLE. API subscriptions are unambiguous business expenses for an AI company.
The risk is forgetting to claim them, not claiming them wrongly.

### 6.3 Full OASIS Compute Cost Deduction List

`[NOW]` Every line item CC should be tracking and deducting on T2125:

| Expense | Deductible? | T2125 Line |
|---------|-------------|-----------|
| Anthropic Claude API | YES — 100% | Computer/internet expenses |
| OpenAI API | YES — 100% | Computer/internet expenses |
| GitHub Copilot / GitHub Pro | YES — 100% | Software subscriptions |
| AWS / GCP / Azure monthly compute | YES — 100% | Computer/internet expenses |
| GPU rental (RunPod, Lambda Labs, Vast.ai) | YES — 100% | Computer/internet expenses |
| Weights & Biases / MLflow cloud | YES — 100% | Software subscriptions |
| Cloud notebooks (Google Colab Pro, etc.) | YES — 100% | Computer/internet expenses |
| Domain registration | YES — 100% | Advertising/computer expenses |
| Web hosting / CDN (Cloudflare, Vercel) | YES — 100% | Computer/internet expenses |
| SSL certificates | YES — 100% | Computer/internet expenses |
| Development laptop / MacBook | YES — 100% (immediate expensing) | CCA — Class 50 or 10 |
| External monitors, keyboard, peripherals | YES — office % | Home office or CCA |
| Internet connection (business portion) | YES — business % | Office expenses |
| Supabase / Postgres cloud hosting | YES — 100% | Computer/internet expenses |
| Figma / design tools | YES — 100% | Software subscriptions |
| Training dataset subscriptions | YES — 100% | Computer/internet or data costs |

### 6.4 Home Office Deduction for AI Development

`[NOW]` CC develops OASIS from home. ITA s.18(12) permits a home office deduction.

**Method A — Simplified flat rate:** $2/day for each day worked at home. Maximum $500/year. No receipts.
Easiest but worst outcome.

**Method B — Detailed calculation (recommended for CC):**
1. Measure total home square footage
2. Measure dedicated workspace square footage
3. Calculate percentage: workspace sq ft ÷ total sq ft
4. Apply percentage to: rent, utilities, internet, home insurance, maintenance/repairs

Example: 600 sq ft apartment, 60 sq ft workspace = **10%**
```
Annual rent:      $16,800 × 10% = $1,680
Utilities:         $1,440 × 10% =   $144
Internet:          $1,080 × 10% =   $108 (can also deduct full business-use internet separately)
Home insurance:      $900 × 10% =    $90
Home office deduction:              $2,022/year
```

**Requirement:** The workspace must be the principal place of business OR used exclusively and regularly
to meet clients (s.18(12)(a)). For a home-based sole proprietor, the first condition is easily met.

---

## 7. International SaaS Revenue and GST/HST

### 7.1 GST/HST Registration Obligation

`[NOW]` CC must register for GST/HST when OASIS taxable revenues exceed **$30,000 in any four
consecutive calendar quarters** (ETA s.240). This is a mandatory legal obligation — not optional.

**Voluntary early registration:** Permitted and advisable. Once registered, CC can claim **Input Tax
Credits (ITCs)** on all business purchases — recovering HST paid on computer equipment, software,
cloud services from Canadian vendors. At OASIS's current expense level, this is $500-$2,000/year
in recoverable HST.

### 7.2 Zero-Rated Exports — The International SaaS Advantage

Services supplied to **non-residents for use outside Canada** are zero-rated (0% GST/HST) under
ETA Schedule VI, Part V. This is one of the most strategically important provisions for a SaaS business
targeting international clients.

| Customer Location | GST/HST Rate | Evidence Required |
|------------------|-------------|------------------|
| Ontario client | 13% HST | No evidence needed — default rate |
| Quebec client | 14.975% (GST + QST) | GST collected; QST separate registration if over QST threshold |
| BC client | 12% (GST + PST) | GST collected only; BC PST separate system |
| US client | **0% (zero-rated export)** | Client billing address + contract showing foreign residency |
| EU client | **0% (zero-rated export)** | Client billing address + contract |
| Any non-resident | **0% (zero-rated export)** | Proof of non-residency must be maintained |

**Zero-rating is not automatic.** CC must maintain documented evidence of customer non-residency.
If CRA audits and evidence is insufficient, a zero-rated sale can be reassessed at 13% — meaning CC
absorbs the HST that wasn't collected.

**Invoice language for international sales:**
> "Zero-rated supply of services to non-resident — Excise Tax Act, Schedule VI, Part V"

**ITC claim on zero-rated revenue:** CC can still claim ITCs on expenses related to zero-rated supplies.
Zero-rated is not exempt — it is taxable at 0%. The ITC recovery remains fully available. This is the
export advantage: no output tax on international sales, full recovery of input tax on costs.

### 7.3 Input Tax Credits — Cash Recovery Mechanics

Once GST/HST registered, CC claims ITCs on the HST portion of all business purchases. This is a
quarterly or annual cash recovery from CRA.

Example ITC recovery for OASIS (annual):
```
Laptop purchase ($2,500 + 13% = $325 HST paid)      ITC: $325
Software subscriptions from Canadian vendors ($800 × 13% = $104 HST)  ITC: $104
Office supplies, equipment                            ITC: ~$50
Annual ITC recovery:                                  ~$479
```

File HST returns quarterly (recommended for growing businesses — more frequent cash recovery from ITCs).

### 7.4 Canada-US Tax Treaty — Revenue Classification

`[OASIS]` OASIS selling to US clients faces zero withholding — but the SaaS vs royalty distinction matters:

| Revenue Type | Treaty Article | Withholding (US side) |
|--------------|---------------|----------------------|
| SaaS subscription (hosted service, no software download) | Article VII (Business Profits) | 0% — no US withholding, no US PE |
| Software royalty (client downloads and installs the software) | Article XII | 0% — copyright royalty withholding is 0% under Canada-US treaty |
| Technical consulting services (CC performs work in Canada) | Article VII | 0% — no US PE |

**Result:** Whether OASIS charges for SaaS access or software licensing, US clients pay CC the full
amount with no US withholding. CC reports income in Canada and pays Canadian tax.

### 7.5 Permanent Establishment (PE) Risk

A PE in the US would expose OASIS to US federal and state corporate tax. Current OASIS operations
carry **LOW PE risk:**

Does NOT create PE:
- AWS/GCP servers in US data centers (generally — server alone is not a PE under OECD commentary)
- US customers accessing a Canadian-hosted SaaS
- CC travelling occasionally to the US for sales meetings
- US-based independent contractors with no authority to bind OASIS

Would create PE risk:
- Hiring a US-based employee with authority to conclude contracts
- Opening a US office
- Maintaining a US warehouse (not applicable to SaaS)

### 7.6 EU VAT — One-Stop Shop (OSS)

`[FUTURE]` If OASIS sells to EU consumers (B2C, not B2B):

- EU VAT registration required once EU sales exceed **€10,000/year** (low threshold)
- The **EU OSS (One-Stop Shop)** system: register in one EU member state, remit VAT for all 27
  countries through a single return
- B2B EU sales: reverse charge mechanism applies — the EU business customer accounts for VAT on
  their own return. No OASIS obligation.
- VAT rates by country: 15%-27%. Ireland (23%), Germany (19%), France (20%) are the common ones.

**Practical guidance:** If OASIS goes self-serve with a checkout page accessible to EU consumers,
use **Paddle or LemonSqueezy** as Merchant of Record — they handle EU VAT automatically for a ~5% fee.
This eliminates the need for EU OSS registration, VAT tracking, and compliance filings.

### 7.7 Payment Processor Comparison

| Processor | Fee | Handles Tax? | Merchant of Record? | Best For |
|-----------|-----|-------------|---------------------|----------|
| **Stripe** | 2.9% + $0.30 | No — CC handles all GST/HST/VAT | No | B2B OASIS clients (they handle own tax) |
| **Paddle** | ~5% all-in | Yes — handles GST/HST, VAT, US state tax globally | Yes | Self-serve SaaS with international consumers |
| **LemonSqueezy** | 5% + $0.50 | Yes | Yes | Digital products, simple setup |
| **Gumroad** | 10% | Yes | Yes | Expensive. Use only for one-off digital product launches. |

`[OASIS]` **Recommendation:** Use Stripe for B2B OASIS automation clients (corporate clients handle
their own tax compliance). If CC ever builds a self-serve SaaS product with consumer checkout, switch
that product to Paddle. The 5% MoR fee costs less than the accounting overhead of multi-jurisdiction
tax compliance at meaningful revenue.

---

## 8. Open Source Monetization

### 8.1 Revenue Types and Tax Treatment

| Revenue Stream | Tax Treatment | Notes |
|----------------|---------------|-------|
| Commercial software license fees (dual licensing) | Business income — T2125 / corporate T2 | Standard business income in year received |
| Support and maintenance contracts | Business income — recognized as delivered | Apply s.20(1)(m) reserve for prepaid support |
| Hosted/SaaS version of open source tool | Business income — apply all SaaS rules (Section 1) | Subscription timing, reserve rules apply |
| One-time license sales | Business income in year of sale | No deferral unless future obligations exist |
| GitHub Sponsors / OpenCollective donations | **Business income** | NOT charitable. Received in commercial context. Include in revenue. |
| Consulting/implementation fees (open source expertise) | Business income | Service fee, recognized when delivered |

**Key point on donations/sponsorships:** GitHub Sponsors revenue paid to CC for OASIS-related projects
is taxable business income under s.9(1). It is not a gift (s.248(1) gift requires donative intent with
no expectation of benefit — commercial sponsorship does not qualify). It is not a charitable receipt
(CC is not a registered charity).

### 8.2 Open Source Contributions as Business Deduction

Developer time contributed to open source projects is deductible **only if** the connection to
income-earning is clear and documentable (s.18(1)(a) — expense incurred to earn income from business).

**Strong deductible case:**
- Contributing to CCXT (the crypto library ATLAS depends on directly) — OASIS directly uses CCXT
  in production. A bug fix or feature enhancement reduces CC's development time on dependent code.
  Document as "technical infrastructure maintenance for trading system."
- Contributing to a library that OASIS clients use, where contribution maintains the OASIS relationship
  or prevents client-billable support hours.

**Weak case, likely not deductible:**
- General open source goodwill contributions with no direct connection to any OASIS product or client
- Contributions to projects CC personally believes in but which have no commercial connection to OASIS

`[OASIS]` Rule of thumb: If CC can draw a straight line from the open source work to revenue protection
or generation, deduct it. If the connection requires an indirect multi-step argument, don't claim it.

### 8.3 Open Source is NOT a Charitable Donation

Common misconception among developers: open source project sponsorships or contributions do not
generate charitable tax receipts.

- A **qualified donee** under ITA s.149.1 must be a CRA-registered charity or other eligible entity
- The Linux Foundation, Apache Foundation, Python Software Foundation, and similar entities are US 501(c)(3)
  organizations, NOT CRA-registered charities
- Donations to US nonprofits through the Canada-US Tax Treaty Article XXI are only deductible up to
  75% of US-source income — not available for CC unless CC has US employment or business income
- **Practical result:** If CC sponsors an open source foundation, it is a business expense at best
  (deductible if connection to income is clear) or a non-deductible personal expense

### 8.4 Dual Licensing — OASIS Application

If CC develops a proprietary AI tool for OASIS and releases an open-core version under a GPL license
with a paid commercial tier:

```
Revenue from commercial licenses:        Business income (T2125 or T2)
Revenue from hosted SaaS:                Business income (SaaS rules — Section 1)
Development cost (OASIS internal):       Current expense — deductible immediately
Marketing cost:                           Current expense
SR&ED on underlying algorithm (if novel): Qualifies for ITC (Section 3)
```

Dual licensing creates no special tax category. It is standard business income with standard
deductible development costs and standard SR&ED eligibility for novel technical work.

---

## 9. SaaS Metrics and Tax Planning

### 9.1 MRR/ARR — Installment Trigger Tracking

CRA requires **quarterly installment payments** once CC's net federal tax owing exceeds **$3,000 in
the current year** AND exceeded $3,000 in one of the two preceding years (ITA s.156).

| MRR Range | ARR | Tax Status | Action |
|-----------|-----|-----------|--------|
| $0 – $500/mo | <$6K | Below installment threshold | Standard T1 filing |
| $500 – $2,500/mo | $6K-$30K | Likely below threshold | Monitor. Begin setting aside 25% of net income. |
| $2,500 – $4,000/mo | $30K-$48K | **Installment trigger zone** | Begin quarterly installments proactively. |
| $4,000+/mo | $48K+ | Installments required | Quarterly payments March/June/Sep/Dec. |

**Installment interest (ITA s.163.1):** Underpaid installments accrue interest at the CRA prescribed
rate + 2% (currently ~7-8% annualized). Installment interest is **not deductible** (ITA s.18(1)(t)).
Pay installments accurately.

**Installment calculation methods (choose lowest):**
1. Prior year method: pay last year's tax liability in four equal installments
2. Second prior year + prior year method: first two installments based on Year -2; last two based on Year -1
3. Current year estimate: if income is lower this year, pay what you actually owe

For a growing SaaS: prior year method creates underpayment. Current year estimate is best but requires
accurate quarterly revenue forecasting.

### 9.2 Customer Acquisition Cost (CAC) — Full Deductibility

CAC is **fully deductible** in the year incurred as advertising and marketing expense (ITA s.18(1)(a)).
No amortization required, even if customers are retained for multiple years.

Deductible CAC components:
- Digital ad spend (Google Ads, LinkedIn Ads, Twitter/X)
- Sales automation tools (Apollo.io, Lemlist, HubSpot)
- CRM subscriptions (deductible regardless of multi-year customer value)
- Referral fees and commissions to arms-length introducers
- Content marketing production (writers, designers, video production)
- Free trial/freemium hosting costs (OASIS demos and trial accounts)
- Conference attendance for sales prospecting (travel + 50% of meals)

**Exception — capitalize only if:** A customer list is purchased outright with a determinable value
and no ongoing obligation. This is a capital acquisition (Class 14.1, 5% CCA). Organic CAC is always
expensed currently.

`[OASIS]` Track CAC by channel in Stripe or your CRM. This creates both a marketing analytics
dataset and a tax audit trail showing what was spent and why.

### 9.3 Deferred Revenue as Tax Planning Tool

`[FUTURE]` At meaningful ARR, annual subscription timing is a deliberate tax-deferral mechanism.

**Strategy — December vs January promotion:**
- December annual subscription drive: large deferred revenue reserve, lower Q4 taxable income
- January annual subscription drive: revenue earned in same year, higher taxable income

**Numeric example:**
```
OASIS launches an annual plan promotion in December 2027.
30 new clients × $2,400/year = $72,000 in December 2027 cash receipts
Service delivered in December: 1/12 × $72,000 = $6,000 earned
s.20(1)(m) reserve: 11/12 × $72,000 = $66,000 deferred to 2028

Tax impact (CCPC at 12.2% SBD rate):
  December promotion: 2027 taxable income increases by $6,000 (not $72,000)
  January promotion: 2028 taxable income increases by full $72,000

Tax deferral: ~$8,052 of corporate tax deferred one year (12.2% × $66,000)
```

The reserve reverses in 2028 — this is a one-year deferral, not permanent elimination. But at
growing ARR, each year's new reserves offset the prior year's reversals, creating a permanent pool
of deferred taxable income. Maintain consistency year over year — CRA requires the same reserve
methodology to be applied consistently.

### 9.4 Churn and Revenue Reversal

Customer refunds reduce taxable revenue in the year issued. If a client cancels and receives a refund
for prepaid months, the refund reduces the prior s.12(1)(a) inclusion.

For non-refundable contracts: the full prepaid amount was properly included in income. No revenue
reversal on cancellation.

Document refund policies consistently — CRA requires the same treatment year over year.

---

## 10. Contractor vs Employee Classification

### 10.1 The Wiebe Door Test

CRA uses the four-factor **Wiebe Door test** (confirmed in *671122 Ontario Ltd v MNR* [1987]) to
classify workers:

| Factor | Employee | Independent Contractor |
|--------|----------|----------------------|
| **Control** | CC dictates when, where, and how work is done | Worker controls their methods and schedule |
| **Tools** | CC provides equipment, accounts, and software | Worker uses their own tools |
| **Chance of profit / risk of loss** | Fixed salary, no financial risk | Can profit more by working efficiently; bears risk of loss |
| **Integration** | Work is integral to CC's business | Worker operates their own independent business |

CRA Guide RC4110 provides detailed guidance. Courts look at the **totality of the relationship**, not
a mechanical point-score.

### 10.2 Personal Services Business Risk (PSB) — Post-Incorporation

`[FUTURE]` **This is a critical incorporation trap.** If CRA determines OASIS Corp is a Personal
Services Business (ITA s.125(7)):

- Small Business Deduction (SBD) is **denied** → effective tax rate jumps from ~12.2% to ~44.5%
  (Ontario combined general rate)
- Most expense deductions are **denied** (only salary to the incorporated employee is deductible)
- All incorporation tax benefits are eliminated

**PSB test:** Would CC have been considered an employee of the client if there were no corporation?
Factors: client controls how work is done, CC works exclusively for one client, CC uses client's
infrastructure.

**PSB protection for OASIS:**
- Maintain multiple clients (no single client >80% of OASIS revenue)
- Document that CC controls how OASIS work is performed
- Use CC's own equipment and software (not client-provided)
- OASIS has the ability to hire substitute workers to complete projects

`[OASIS]` **Rule:** Never let one client constitute more than 75% of OASIS revenue. Diversification
is both a business and a tax imperative once incorporated.

### 10.3 T4A Obligations for Canadian Contractors

`[NOW]` When CC pays Canadian contractors (sole proprietors) more than **$500 for services in a
calendar year**, a T4A slip must be issued by **February 28** (Box 48 — fees for services).

CRA matches T4A-reported payments against individual T1 returns. Missing T4As create audit risk for both
the contractor (unreported income) and the payer (OASIS — for issuing penalties). Penalty: $100/slip
per day of delay, maximum $7,500.

This applies to any freelancer, developer, designer, or consultant CC pays for OASIS work.

### 10.4 International Contractors

| Scenario | Withholding | Reporting |
|----------|-------------|-----------|
| US contractor, work performed in the US | 0% (Canada-US Treaty, Article VII) | Obtain W-8BEN. No T4A-NR required. |
| US contractor, work performed IN Canada | Potential Reg. 105 issue — get a waiver | Consult CPA |
| Non-treaty-country contractor, work in Canada | 15% Regulation 105 withholding | Remit to CRA. Contractor can file NR4 refund claim. |
| Non-treaty-country contractor, work outside Canada | 0% — services not rendered in Canada | Maintain written confirmation of work location |

**Regulation 105 (Reg. 105 ITA):** Requires 15% withholding on fees paid to non-residents for
services **rendered in Canada**. Remote work from another country generally falls outside Reg. 105.
Maintain records showing where work was physically performed.

**Safe practice for all international contractors:** Obtain a written declaration confirming tax
residency, no Canadian PE, and work location before first payment.

---

## 11. Cloud Credits and Government Grant Tax Treatment

### 11.1 Cloud Provider Startup Credits — Income Inclusion Analysis

AWS Activate, GCP for Startups, Azure Startup, and similar programs provide credits against cloud
usage. The tax treatment depends on how the credit is structured.

| Credit Type | Tax Treatment |
|-------------|---------------|
| Credits automatically applied against invoices (no cash disbursed) | Reduces deductible expense. No separate income inclusion. Net expense = what CC actually pays. |
| Cash deposited to account (redeemable credits that function like prepaid balance) | Taxable income under s.12(1)(x) (government assistance received) in year received. |
| Conditional credits (must be spent on qualifying services within a time limit) | Recognized as income as credits are consumed against charges. |

**CRA IT-273R2 (Government Assistance):** Any amount received from a government, governmental agency,
or similar body as assistance is included in income under s.12(1)(x) — unless it reduces the cost of
depreciable property (in which case it reduces the CCA base under s.13(7.1) rather than being included
in income).

**Practical treatment for AWS/GCP/Azure credits at OASIS scale:**
- Credits reduce CC's actual cloud bill. Deduct the **net amount paid** (after credits). No separate
  income inclusion required — the credit offsets the expense, reducing the deduction rather than
  creating separate income.
- Example: $500 AWS Activate credit reduces a $500 AWS bill to $0. CC deducts $0 in cloud expenses
  for that month (the credit offsets the expense). No income inclusion, no deduction — washes out.

### 11.2 IRAP Grants — Income Inclusion and SR&ED Interaction

NRC IRAP (Industrial Research Assistance Program) grants are **taxable income** under s.12(1)(x).
Include in business income in the year received.

**Critical SR&ED interaction — ITA s.127(18):**
When government assistance (including IRAP) funds the same expenditures as an SR&ED ITC claim, the
**SR&ED pool is reduced** by the amount of assistance. You cannot claim the same dollar twice.

```
Example:
  IRAP grant received: $50,000 (for ATLAS algorithm development)
  Include $50,000 in income under s.12(1)(x): adds to taxable income

  SR&ED expenditure pool (without IRAP): $120,000
  Reduction under s.127(18):              -$50,000
  Adjusted SR&ED pool:                    $70,000
  SR&ED ITC at 35%:                       $24,500

  Net benefit:
    IRAP grant after tax (at 12.2% CCPC rate): $50,000 × (1 - 0.122) = $43,900
    SR&ED ITC on remaining pool:               $24,500
    Total:                                     $68,400

  Without IRAP (SR&ED only on full $120,000):  $42,000
  Net advantage of IRAP even with SR&ED reduction: +$26,400
```

**Conclusion:** IRAP is still strongly net-positive even after the SR&ED pool reduction. Always apply.

### 11.3 FedDev Ontario and Other Provincial Grants

Same treatment as IRAP: taxable income under s.12(1)(x), SR&ED pool reduction under s.127(18) if
the grant funds SR&ED expenditures.

**Optimization strategy:** Structure grant applications to fund **commercialization, hiring, and
marketing costs** — activities that are NOT SR&ED expenditures. This preserves the full SR&ED pool
for ITC claims, maximizing total government benefit.

```
IRAP / FedDev funds:        hiring costs, business development, market entry → no SR&ED overlap
SR&ED ITC claims:           R&D labour, experimental compute costs → full pool intact
OIDMTC claims:              product-building labour → separate from SR&ED labour

Result: Triple-stack without overlap — the three funding sources claim different expenditures.
```

### 11.4 Futurpreneur and BDC Loans — NOT Income

Business development loans (Futurpreneur, BDC, CSBFP) are **liabilities, not income**. No income
inclusion on receipt. Principal repayment is not deductible. Interest on the loan IS deductible under
s.20(1)(c) (interest on money borrowed to earn business income).

### 11.5 The Full Government Benefit Stack — Post-Incorporation

`[FUTURE]` The optimal combined annual government benefit for an incorporated OASIS executing on
AI development:

```
Funding Source              Annual Cash Benefit     Notes
IRAP grant                  $25,000 – $100,000      Non-dilutive. Apply through NRC IRAP advisor.
SR&ED ITC (35% refundable)  $15,000 – $65,000       On R&D labour not covered by IRAP
OIDMTC (40% refundable)     $8,000 – $20,000        On product-building labour (separate from SR&ED)
Ontario OITC (8%)           $3,500 – $12,000        Additional Ontario SR&ED layer
AWS/GCP startup credits     $5,000 – $100,000       Reduces compute costs (non-cash benefit)
                            ─────────────────────
Estimated total annual:     $55,000 – $300,000+     Scenario-dependent
```

No single expenditure can appear in more than one claim. Keep separate cost centers and maintain
clear documentation showing which spending is attributed to which program.

**CRA audit risk for stacking:** MEDIUM-HIGH. CRA specifically examines SR&ED claims for double-dipping
with government assistance. Keep auditable separation between expense categories. The documentation
burden is substantial — budget for a dedicated SR&ED consultant and part-time CFO/bookkeeper to
maintain proper records.

---

## 12. Key ITA/ETA Reference Index

| Section | Statute | Topic |
|---------|---------|-------|
| **s.9(1)** | ITA | Business income = profit, calculated on accrual basis |
| **s.12(1)(a)** | ITA | Include advance receipts for unrendered services |
| **s.12(1)(e)** | ITA | Add back prior year's reserve |
| **s.12(1)(x)** | ITA | Include government assistance in income |
| **s.13(7.1)** | ITA | Government assistance reduces CCA base instead of income inclusion |
| **s.18(1)(a)** | ITA | Deductibility — expense incurred to earn income |
| **s.18(1)(t)** | ITA | Installment interest is NOT deductible |
| **s.18(12)** | ITA | Home office deduction rules |
| **s.20(1)(c)** | ITA | Deduct interest on borrowed money used to earn income |
| **s.20(1)(m)** | ITA | Reserve for goods/services to be delivered after year-end |
| **s.37** | ITA | SR&ED expenditure deduction |
| **s.69** | ITA | Non-arm's-length transactions deemed at FMV |
| **s.125(7)** | ITA | Personal Services Business definition |
| **s.127(5), (9)** | ITA | Investment Tax Credit (SR&ED ITC) |
| **s.127(18)** | ITA | Government assistance reduces SR&ED pool |
| **s.156** | ITA | Quarterly installment requirement |
| **s.163.1** | ITA | Installment interest |
| **s.245** | ITA | General Anti-Avoidance Rule (GAAR) |
| **s.247** | ITA | Transfer pricing penalties |
| **Reg. 105** | ITA | 15% withholding on non-resident service fees |
| **Reg. 2900** | ITA | SR&ED — prescribed proxy amount and systematic investigation |
| **CCA Class 12** | ITA Reg. 1100 | Software — 100% rate |
| **CCA Class 14.1** | ITA Reg. 1100 | Indefinite-life IP, goodwill — 5% |
| **CCA Class 44** | ITA Reg. 1100 | Patents — 25% |
| **CCA Class 50** | ITA Reg. 1100 | Computer equipment — 55% |
| **s.240 ETA** | ETA | GST/HST registration threshold ($30K) |
| **Sch. VI, Pt. V ETA** | ETA | Zero-rated exports of services to non-residents |

---

## 13. OASIS Action Matrix

### NOW — Sole Proprietor Actions

| Priority | Action | Annual Benefit | Complexity |
|----------|--------|---------------|-----------|
| 1 | Track ALL compute/API costs monthly (Claude, OpenAI, AWS, GitHub Copilot) | $1,000-$4,000 deduction | LOW — download invoices monthly |
| 2 | Home office detailed calculation (square footage method) | $1,500-$3,000 deduction | LOW — one-time measurement |
| 3 | Issue T4As to contractors paid >$500 | Legal compliance, $100/slip penalty avoided | LOW — 15 min/contractor in February |
| 4 | Start SR&ED documentation in `sred/` directory | Positions $2,000-$5,000 non-refundable ITC | MEDIUM — 5 min per dev session |
| 5 | Register for GST/HST voluntarily (before $30K if expenses are high) | ITC recovery + legal compliance | MEDIUM — CRA online form |
| 6 | Time annual plan closings to January (not November/December) | Reduces reserve complexity | LOW — sales process adjustment |
| 7 | Begin quarterly tax installments when OASIS hits $2,500/mo MRR | Avoids 7-8% installment interest | MEDIUM — calendar reminders + savings habit |

### FUTURE — Post-Incorporation Actions

| Priority | Action | Annual Benefit | Complexity |
|----------|--------|---------------|-----------|
| 1 | File SR&ED claim via T661 (use a consultant for first claim) | $15,000-$65,000 refundable cash | HIGH — engage SR&ED specialist |
| 2 | Apply for IRAP funding for ATLAS/OASIS R&D | $25,000-$100,000 non-dilutive grant | HIGH — NRC IRAP advisor contact + application |
| 3 | Apply for OIDMTC pre-certification if building external analytics product | $8,000-$20,000 refundable cash | HIGH — OMDC application, design-stage timing |
| 4 | Optimize salary vs dividend mix annually with CPA | $3,000-$15,000/year in combined tax | MEDIUM — annual calculation |
| 5 | PSB protection — diversify clients, document control of work | Preserves SBD (saves ~32% corporate rate) | LOW — commercial practice |
| 6 | IP HoldCo structure if OASIS IP has $50K+ value | LCGE preservation, royalty income split | HIGH — requires tax lawyer |
| 7 | Switch consumer SaaS checkout to Paddle (if B2C product launched) | Eliminates VAT compliance overhead | LOW — payment processor switch |

---

> **Prepared by ATLAS | CFO, OASIS AI Solutions**
> *ATLAS researches, calculates, and prepares. CC reviews and submits. ATLAS does not have CRA login access.*
> *Companion documents: ATLAS_TAX_STRATEGY.md | ATLAS_DEDUCTIONS_MASTERLIST.md |*
> *ATLAS_GOVERNMENT_GRANTS.md | ATLAS_INCORPORATION_TAX_STRATEGIES.md | ATLAS_CRA_AUDIT_DEFENSE.md*
