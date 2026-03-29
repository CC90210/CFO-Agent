# ATLAS — Business Valuation & M&A Tax Guide
## The Definitive Canadian Reference for Business Valuation, M&A Structuring, and Tax-Optimized Exits

**Maintained by:** ATLAS (Autonomous Trading & Leverage Acquisition System) — CC's CFO
**Jurisdiction:** Canada (Federal + Ontario), with cross-border coverage
**Last Updated:** 2026-03-28
**References:** ITA (Income Tax Act), CRA IT Bulletins, IC Circulars, McKinsey Valuation (7th ed), Damodaran Investment Valuation (3rd ed), Rosenbaum & Pearl Investment Banking (3rd ed), Pratt & Niculita Valuing a Business (6th ed), Shannon Pratt Business Valuation Discounts and Premiums (2nd ed), CCH Canadian Tax Reporter, Wolters Kluwer Tax Planning Guide

---

## TABLE OF CONTENTS

### Part I: Business Valuation Methodologies
1. [Discounted Cash Flow (DCF)](#1-discounted-cash-flow-dcf)
2. [Comparable Company Analysis (Trading Comps)](#2-comparable-company-analysis-trading-comps)
3. [Precedent Transaction Analysis](#3-precedent-transaction-analysis)
4. [Asset-Based Valuation](#4-asset-based-valuation)
5. [Capitalized Earnings (Income Approach)](#5-capitalized-earnings-income-approach)
6. [SaaS-Specific Valuation](#6-saas-specific-valuation)
7. [Valuation Discounts and Premiums](#7-valuation-discounts-and-premiums)
8. [CRA Valuation Rules](#8-cra-valuation-rules)

### Part II: M&A Tax Mechanics
9. [Section 85 Rollover](#9-section-85-rollover)
10. [Section 86 Share Exchange (Estate Freeze)](#10-section-86-share-exchange-estate-freeze)
11. [Section 87 Amalgamation](#11-section-87-amalgamation)
12. [Section 88 Wind-Up](#12-section-88-wind-up)
13. [Asset Purchase vs Share Purchase](#13-asset-purchase-vs-share-purchase)
14. [Earn-Outs and Contingent Consideration](#14-earn-outs-and-contingent-consideration)
15. [Tax Due Diligence](#15-tax-due-diligence)
16. [Lifetime Capital Gains Exemption (LCGE) on QSBC Shares](#16-lifetime-capital-gains-exemption-lcge-on-qsbc-shares)
17. [Cross-Border M&A](#17-cross-border-ma)
18. [Post-Acquisition Integration](#18-post-acquisition-integration)

### Part III: Corporate Restructuring
19. [Corporate Reorganizations](#19-corporate-reorganizations)
20. [Distressed Situations](#20-distressed-situations)

### Appendices
- [A: Valuation Quick Reference Tables](#appendix-a-valuation-quick-reference-tables)
- [B: M&A Checklist (Seller's Perspective)](#appendix-b-ma-checklist-sellers-perspective)
- [C: ATLAS Decision Framework — Which Structure to Use](#appendix-c-atlas-decision-framework)
- [D: Key ITA Sections Reference Map](#appendix-d-key-ita-sections-reference-map)

---

## PART I: BUSINESS VALUATION METHODOLOGIES

---

## 1. Discounted Cash Flow (DCF)

### What It Is

DCF is the gold-standard valuation methodology for businesses with predictable cash flows. It answers the question: what is the present value of all future cash flows the business will generate? Every dollar earned in the future is worth less today — the discount rate captures that time value and risk premium.

DCF is the methodology CRA appraisers default to for disputes, and what every investment banker uses to anchor valuation negotiations. Know this methodology cold.

**Primary References:**
- McKinsey & Company, *Valuation: Measuring and Managing the Value of Companies* (7th ed., 2020) — the practitioner bible
- Aswath Damodaran, *Investment Valuation* (3rd ed., 2012) — the academic counterpart
- Damodaran's website (pages.stern.nyu.edu/~adamodar/) — free industry data updated annually

---

### 1.1 FCFF vs FCFE — Which to Use and When

The most critical decision in DCF: which cash flow measure to discount.

#### Free Cash Flow to Firm (FCFF)
The cash flow available to ALL capital providers (equity holders AND debt holders) before debt service.

```
FCFF = EBIT × (1 - Tax Rate)
     + Depreciation & Amortization
     - Capital Expenditures
     - Change in Net Working Capital

Alternatively:
FCFF = Net Income
     + Depreciation & Amortization
     + Interest Expense × (1 - Tax Rate)
     - Capital Expenditures
     - Change in Net Working Capital
```

**Discount rate for FCFF:** WACC (Weighted Average Cost of Capital)
**Output:** Enterprise Value (EV) — value to all providers of capital

**When to use FCFF:**
- Company has significant debt
- Capital structure is expected to change
- Comparing companies with different leverage ratios
- Standard for LBO analysis and strategic M&A

#### Free Cash Flow to Equity (FCFE)
The cash flow available ONLY to equity holders after debt obligations are satisfied.

```
FCFE = Net Income
     + Depreciation & Amortization
     - Capital Expenditures
     - Change in Net Working Capital
     - Principal Repayments
     + New Debt Issued
```

**Discount rate for FCFE:** Cost of Equity (Ke)
**Output:** Equity Value directly

**When to use FCFE:**
- Stable, predictable capital structure
- Financial institutions (banks, insurance) where debt is part of operations
- Minority stake valuations

#### Bridge: EV to Equity Value
```
Enterprise Value (EV)
- Total Debt (including finance leases)
- Minority Interest
- Preferred Shares
+ Cash and Cash Equivalents
+ Investments in Associates
= Equity Value

Per Share = Equity Value ÷ Fully Diluted Shares Outstanding
```

**Canadian tax note:** When calculating FCFF from EBIT, use the combined federal + provincial marginal tax rate for the corporation. For an Ontario CCPC earning ≤ $500K active business income: 12.2% (federal 9% + Ontario 3.2%). Above $500K or after losing SBD: 26.5%.

---

### 1.2 WACC Calculation — Step by Step

WACC is the blended cost of all capital, weighted by each source's proportion in the capital structure.

```
WACC = (E/V) × Ke + (D/V) × Kd × (1 - T)

Where:
E = Market value of equity
D = Market value of debt
V = E + D (total capital)
Ke = Cost of equity
Kd = Cost of debt (pre-tax)
T = Marginal corporate tax rate
```

#### Step 1: Cost of Equity via CAPM

```
Ke = Rf + β × (Rm - Rf) + Size Premium + Company-Specific Risk

Where:
Rf = Risk-free rate (Government of Canada 10-year bond yield)
β = Beta (systematic risk relative to market)
Rm - Rf = Equity Risk Premium (ERP)
```

**Risk-Free Rate (Rf):**
- Use Government of Canada 10-year benchmark bond yield
- As of 2025-2026: approximately 3.2% - 3.8% (check Bank of Canada daily)
- For long-horizon projections, use normalized long-term rate (3.5% is commonly applied)
- Do NOT use 91-day T-bill — too short-term for business valuation

**Equity Risk Premium (ERP):**
- Canada ERP: 4.5% - 5.5% (Damodaran 2025 estimate: 4.6% for Canada)
- US ERP tends to be slightly lower (4.0% - 4.5%) due to deeper markets
- Source: Damodaran's annual ERP country-by-country table (January update each year)
- For private company valuations in Canada, use 5.0% - 5.5% to reflect less liquid market

**Beta:**
- Public companies: use 2-year weekly regression vs TSX Composite or TSX 60
- Private companies: use industry beta from public comparables, then relevered

Unlevering/Relevering Beta (Hamada Equation):
```
βU (Unlevered) = βL ÷ [1 + (1 - T) × (D/E)]
βL (Relevered) = βU × [1 + (1 - T) × (D/E)]
```

| Industry (Canada) | Typical Unlevered Beta |
|---|---|
| Technology / SaaS | 1.0 - 1.4 |
| Professional Services | 0.7 - 1.0 |
| Healthcare | 0.6 - 0.9 |
| Real Estate | 0.5 - 0.8 |
| Financial Services | 0.3 - 0.7 |
| Resource / Mining | 1.0 - 1.6 |
| Consumer / Retail | 0.6 - 1.0 |

Source: Damodaran Industry Betas (Canada-specific data via country adjustment)

**Size Premium:**
- Ibbotson (Morningstar) CRSP Decile data: size premiums by market cap decile
- For micro-cap / small private company: add 3% - 6% above CAPM
- Duff & Phelps (Kroll) Size Study provides Canadian-equivalent data
- Practical application: companies <$10M revenue should add minimum 4% size premium

**Company-Specific Risk Premium (CSRP):**
- Qualitative adjustment: 0% to 5%+ depending on business-specific factors
- Factors increasing CSRP:
  - Single customer concentration (>20% revenue from one client: +1% - 3%)
  - Key person dependence (founder-led, no management depth: +1% - 3%)
  - Regulatory risk
  - Limited operating history (<3 years: +2% - 4%)
  - Lack of audited financial statements
  - Highly competitive / undifferentiated market
- Factors decreasing CSRP:
  - Long-term contracts / recurring revenue
  - Strong management team depth
  - Defensible competitive moat
  - Diversified customer base

**Example WACC Calculation (OASIS AI Solutions):**
```
Rf = 3.5% (GoC 10-year)
ERP = 5.0%
β (relevered) = 1.3 (SaaS / professional services blend)
Size Premium = 5.0% (micro-cap, <$500K revenue)
CSRP = 2.0% (key person risk: founder-led)

Ke = 3.5% + 1.3 × 5.0% + 5.0% + 2.0%
   = 3.5% + 6.5% + 5.0% + 2.0%
   = 17.0%

Kd = 6.5% (prime + 2%, typical small business loan)
T = 12.2% (Ontario CCPC, SBD rate)
D/V = 0% (no debt currently)

WACC = 100% × 17.0% + 0% × 6.5% × (1 - 12.2%)
     = 17.0%
```

For OASIS at current stage: 17% - 22% WACC is appropriate. Do not use a lower rate — the business is early-stage with key person risk.

#### Step 2: Cost of Debt

```
Kd (after-tax) = Interest Rate × (1 - Marginal Tax Rate)

Example:
Bank loan at 7.5% → after-tax cost = 7.5% × (1 - 26.5%) = 5.51%
```

For private company debt cost: use actual interest rate on existing debt, or prime + 2-4% depending on creditworthiness.

---

### 1.3 Terminal Value — Gordon Growth vs Exit Multiple

Terminal value typically represents 60% - 80% of total DCF value for stable businesses. Getting this right is critical.

#### Method 1: Gordon Growth Model (Perpetuity Growth)
```
TV = FCF_n × (1 + g) ÷ (WACC - g)

Where:
FCF_n = Free cash flow in final projection year
g = Perpetual growth rate
WACC = Discount rate

Critical rule: g MUST be ≤ long-term nominal GDP growth rate
Canadian nominal GDP growth: ~3.5% - 4.5% historically
Practical cap: g ≤ 3.0% for conservative; 4.0% for aggressive
```

**Sensitivity to growth rate assumption:**

| Perpetual Growth Rate | TV (FCF_n = $1M, WACC = 17%) |
|---|---|
| 1.0% | $6.25M |
| 2.0% | $6.67M |
| 3.0% | $7.14M |
| 4.0% | $7.69M |
| 5.0% | $8.33M |

Small changes in g create large swings in value. Always disclose the assumed growth rate prominently.

#### Method 2: Exit Multiple
```
TV = EBITDA_n × Exit Multiple

OR

TV = Revenue_n × Exit Multiple (for SaaS / high-growth companies)

Where:
EBITDA_n or Revenue_n = metric in final projection year
Exit Multiple = selected from trading comps or precedent transactions
```

**Why both methods matter:**
- Gordon Growth anchors to fundamental cash flow economics
- Exit Multiple anchors to market-based pricing
- The two methods should converge within ±15%. If they diverge widely, re-examine assumptions.
- Always present BOTH and triangulate

---

### 1.4 Discount Rate Selection for Private Companies

Private company DCF requires significant judgment over public company models. The three adjustments:

**A. Size Premium (Kroll/Ibbotson Data)**

| Company Size by Market Cap | Added Premium |
|---|---|
| > $2B (mid-cap) | 0.5% - 1.5% |
| $500M - $2B (small-cap) | 1.5% - 2.5% |
| $50M - $500M (micro-cap) | 3.0% - 5.0% |
| <$50M (nano-cap / private) | 5.0% - 8.0% |

**B. Illiquidity Discount on Discount Rate**
- Public company shares can be sold in seconds; private company ownership cannot
- Add 1% - 3% to discount rate for illiquidity of underlying business
- Alternatively, apply DLOM (Discount for Lack of Marketability) to equity value output (see Section 7)
- Do not double-count: use one or the other, not both

**C. Company-Specific Risk (covered above)**

**Practical private company WACC ranges by stage:**

| Stage | Revenue | Typical WACC |
|---|---|---|
| Pre-revenue / seed | $0 | 35% - 60%+ (VC discount rates) |
| Early-stage | <$500K | 25% - 40% |
| Growth stage | $500K - $5M | 18% - 28% |
| Established SMB | $5M - $25M | 14% - 20% |
| Mature business | >$25M | 10% - 15% |

---

### 1.5 Sensitivity Analysis

No DCF is credible without sensitivity analysis. The output is a range of values, not a point estimate.

**Tornado Chart — Key Variables by Impact:**
Build a tornado chart showing which input assumptions drive the most value variance:

1. Terminal growth rate (biggest impact)
2. WACC / discount rate (second biggest)
3. Revenue growth rate in years 3-5
4. EBITDA margin improvement assumptions
5. Capital expenditure intensity
6. Working capital assumptions
7. Tax rate

**Two-Way Sensitivity Table:**
Always present WACC vs Terminal Growth Rate table:

```
Example: OASIS FCF at $200K in Year 5, projecting exit

                    Terminal Growth Rate
              1.0%    2.0%    3.0%    4.0%    5.0%
WACC 15%    $1.25M  $1.33M  $1.43M  $1.54M  $1.67M
WACC 17%    $1.07M  $1.14M  $1.22M  $1.30M  $1.39M
WACC 19%    $0.93M  $0.98M  $1.04M  $1.11M  $1.19M
WACC 21%    $0.81M  $0.86M  $0.91M  $0.97M  $1.03M
WACC 23%    $0.71M  $0.75M  $0.79M  $0.83M  $0.88M
```

**Monte Carlo Simulation:**
For sophisticated buyers / CRA disputes, run 10,000 simulations varying all input assumptions simultaneously. Tools: Crystal Ball (Excel add-in), @Risk, or custom Python with `numpy.random`.

Output: probability distribution of enterprise values with 10th / 50th / 90th percentiles. This is defensible in Tax Court.

---

## 2. Comparable Company Analysis (Trading Comps)

### What It Is

Trading comps value a business by referencing how similar public companies trade in the market. The logic: if Company A (public, comparable) trades at 10x EBITDA, Company B (private, similar) should be worth approximately 10x EBITDA — adjusted for size, liquidity, and growth differences.

**Critical limitation:** Public company multiples include a liquidity premium not available to private companies. Always apply a DLOM (15% - 35%) to bridge public-to-private.

---

### 2.1 Key Multiples — Definitions and Application

#### Enterprise Value Multiples (Capital Structure Neutral)

```
EV = Market Cap + Total Debt + Minority Interest + Preferred Equity - Cash
```

| Multiple | Formula | Used For |
|---|---|---|
| EV/Revenue | EV ÷ Annual Revenue | High-growth, low-margin businesses |
| EV/Gross Profit | EV ÷ Gross Profit | Comparing businesses with different COGS structures |
| EV/EBITDA | EV ÷ EBITDA | The most common; eliminates D&A and capital structure |
| EV/EBIT | EV ÷ EBIT | Businesses with significant D&A differences |
| EV/NOPAT | EV ÷ Net Operating Profit After Tax | Academic precision |

#### Equity Value Multiples (Capital Structure Specific)

| Multiple | Formula | Used For |
|---|---|---|
| P/E | Share Price ÷ EPS | Mature, profitable public companies |
| P/Book | Share Price ÷ Book Value per Share | Financial institutions |
| P/Sales | Share Price ÷ Revenue per Share | Retail, consumer |

#### SaaS / Technology Multiples
| Multiple | Formula | Used For |
|---|---|---|
| EV/ARR | EV ÷ Annual Recurring Revenue | SaaS; most used by VCs and strategic buyers |
| EV/NTM Revenue | EV ÷ Next Twelve Months Revenue | Forward-looking for fast growers |
| Price/NTM ARR | Same as above, equity basis | Early-stage SaaS |

---

### 2.2 Building the Comp Universe — Selection Criteria

The quality of the comp set determines the quality of the valuation. Bad comps = bad numbers.

**Step 1: Define the business accurately**
- Primary revenue model (services vs product vs SaaS vs transaction-based)
- Customer segment (enterprise vs SMB vs consumer)
- Geography (Canadian, North American, global)
- Growth stage (hypergrowth vs growth vs mature vs declining)

**Step 2: Screen for comparables**
Sources for Canadian / North American comps:
- Capital IQ (S&P Global) — premium, industry standard
- PitchBook — private deal comps, VC/PE context
- Bloomberg Terminal — real-time financials
- TSX + TSXV listed companies (SEDAR filings for financial data)
- SEC EDGAR + EDGAR Online (for US comparables)
- Damodaran's free datasets (aggregated by industry)

**Screening criteria:**

| Criterion | Guidance |
|---|---|
| Business model | Same revenue type (recurring vs transactional) |
| Industry/sector | Same NAICS or GICS code, but use judgment |
| Size | ±3x revenue band is acceptable (with adjustment) |
| Geography | Same market exposure where possible |
| Growth profile | Similar growth stage (±15% growth rate differential ideal) |
| Profitability | Similar margin profile OR adjust |
| Fiscal year | Use LTM (Last Twelve Months) to normalize |

**Minimum comp set:** 5 - 8 companies. Fewer raises questions. More than 15 dilutes the analysis.

---

### 2.3 Normalization Adjustments

Raw public company financials require adjustment before applying to private company. The process:

**Revenue normalization:**
- Exclude one-time, non-recurring revenue items
- Annualize partial-year revenue for recent acquisitions
- Adjust for revenue recognition policy differences (IFRS 15 vs ASPE)
- For Canadian comps: confirm IFRS vs ASPE treatment

**EBITDA normalization:**
- Add back: non-recurring expenses (restructuring, litigation settlements, executive departures)
- Add back: owner compensation in excess of market rate (common for owner-operated businesses)
- Add back: related party transactions at non-arm's length pricing
- Add back: personal expenses run through the business (car, travel, club memberships)
- Subtract: synergies claimed by acquirer (not inherent to business)
- Adjust for: stock-based compensation (cash or non-cash — disclosed separately)

**Example — OASIS Normalization:**
```
Reported EBITDA: $50,000
Add: Owner salary above market ($120K reported, $60K market rate): +$60,000
Add: Personal vehicle expenses: +$8,000
Add: Home office allocated costs (over-allocated): +$5,000
Add: One-time legal expense (contract dispute): +$12,000
Subtract: Below-market rent (related party): -$18,000

Normalized EBITDA: $117,000
```

This adjustment more than doubles apparent profitability — critical for both valuation and tax planning.

---

### 2.4 SaaS-Specific Multiple — Rule of 40

The Rule of 40 is the primary SaaS health metric that drives multiple selection:

```
Rule of 40 Score = ARR Growth Rate (%) + EBITDA Margin (%)

Example:
ARR Growth: 80% YoY
EBITDA Margin: -20% (investing aggressively)
Rule of 40 Score: 80 + (-20) = 60 → Excellent → Premium multiple

Another example:
ARR Growth: 15%
EBITDA Margin: 25%
Rule of 40 Score: 15 + 25 = 40 → Meets threshold → Market multiple
```

**EV/NTM Revenue multiples by Rule of 40 score (2024-2025 market):**

| Rule of 40 Score | EV/NTM Revenue Multiple |
|---|---|
| > 60 | 8x - 20x+ |
| 40 - 60 | 4x - 10x |
| 20 - 40 | 2x - 5x |
| < 20 | 1x - 3x |

Source: BVP Nasdaq Emerging Cloud Index, SaaS Capital Index (quarterly updates)

**Important 2022-2024 context:** SaaS multiples compressed dramatically from 2021 peaks (some at 40x+ NTM revenue) to 2023-2024 lows (4x - 8x). As of 2025-2026, multiples have partially recovered but remain below 2021 peaks. Always use current market data.

---

## 3. Precedent Transaction Analysis

### What It Is

Precedent transactions value a business based on prices actually paid in completed M&A deals for similar companies. Unlike trading comps (minority stake, liquid), transactions capture control premiums and reflect the price a motivated buyer paid to acquire full control.

**Key difference from trading comps:** Precedent transactions typically reflect a 20% - 40% premium over trading comps due to:
1. Control premium (ability to direct the business)
2. Synergy expectations (strategic buyer value)
3. Competitive bidding dynamics

---

### 3.1 Control Premiums

**Definition:** The premium paid by an acquirer above the standalone trading value of a target company to acquire a controlling interest.

```
Control Premium = (Acquisition Price per Share - Pre-Announcement Trading Price) ÷ Pre-Announcement Trading Price × 100%
```

**Historical Canadian M&A control premiums:**

| Sector | Typical Control Premium Range |
|---|---|
| Technology / SaaS | 25% - 55% |
| Professional Services | 20% - 40% |
| Healthcare | 30% - 50% |
| Financial Services | 20% - 35% |
| Consumer / Retail | 25% - 45% |
| Industrial / Manufacturing | 20% - 40% |
| Resource / Energy | 15% - 35% |

Source: Mergerstat Review, Bloomberg M&A database, Capital IQ precedent transactions

**Important:** Control premiums vary significantly based on:
- Competitive auction process (increases premium)
- Single bidder negotiation (decreases premium)
- Strategic vs. financial buyer (strategic pays more for synergies)
- Market conditions (bull vs. bear M&A market)
- Target's standalone performance (distressed targets get lower premiums)

---

### 3.2 Synergy Adjustments

Synergies represent value created by combining two businesses that neither could create independently.

**Revenue synergies:**
- Cross-selling (buyer's customers to target's products)
- Geographic expansion (target enters new markets via buyer's distribution)
- New product development acceleration
- Reduced customer acquisition costs (shared brand)

**Cost synergies:**
- Elimination of duplicate corporate overhead (G&A)
- Procurement leverage (volume discounts)
- Technology platform consolidation
- Workforce rationalization (overlap in back-office functions)
- Facility consolidation

**Synergy valuation rule of thumb:**
- Cost synergies: 70% - 90% realization probability; value on 3-5 year horizon discounted back
- Revenue synergies: 30% - 50% realization probability; heavily discounted (harder to achieve)

**Canadian accounting treatment (ASPE 1582 / IFRS 3):**
- Synergies are included in goodwill on acquisition
- Goodwill = Purchase Price - Fair Value of Net Identifiable Assets
- Canada: Goodwill → Class 14.1 (CCA eligible at 5% declining balance)

---

### 3.3 Deal Structure Impact on Valuation

**All-cash deal:** Buyer assumes all risk. Seller gets certainty. Typically commands 5% - 10% lower headline price vs. share-for-share due to tax efficiency for seller (capital gains tax triggered).

**Share-for-share deal:** Tax-deferred under ITA s.85.1. Seller takes buyer's shares as consideration. Deferred CGT = higher headline price tolerance. Risk: seller exposed to buyer's post-deal performance.

**Earn-out structure:** Part of purchase price contingent on future performance. Reduces buyer risk. Seller can receive higher total price IF performance targets are met. CRA treatment: complex (covered in Section 14).

**Asset deal vs. share deal tax dynamics:**

| Deal Type | Buyer Prefers | Seller Prefers |
|---|---|---|
| Asset deal | Yes (resets CCA, avoids liability inheritance) | No (income/recapture exposure) |
| Share deal | No (inherits historical tax cost base) | Yes (capital gains, LCGE potential) |

The tension between buyer/seller preference on deal structure is one of the most common negotiation points in Canadian M&A. Hybrid structures resolve this via tax indemnities and purchase price adjustments.

---

### 3.4 Canadian M&A Databases and Data Sources

**Premium sources (required for professional work):**
- **Capital IQ (S&P Global):** Best for Canadian and North American precedent transactions. Filter by deal date, industry, size, geography. Cost: ~$30K-$60K/year (institutional). University access often available.
- **PitchBook:** Best for VC/PE transactions, growth-stage private deals. Superior to Capital IQ for early-stage data.
- **MergerMarket:** Proprietary M&A intelligence, deal rumours, completed transactions in Europe/Canada.
- **Bloomberg M&A:** Real-time deal tracking, premium pricing.

**Free/accessible sources:**
- **SEDAR+** (Canadian securities filings): Management Information Circulars for public company M&A must disclose valuation opinions (fairness opinions)
- **Competition Bureau Canada:** Merger notifications for deals >$400M threshold
- **Business Development Bank of Canada (BDC):** Valuation research for Canadian SMBs
- **Damodaran's Acquisition Premiums dataset:** Free annual update (stern.nyu.edu)

---

## 4. Asset-Based Valuation

### What It Is

Asset-based valuation determines business worth by reference to the net value of the underlying assets, either as a going concern or on liquidation. This methodology is appropriate for:
- Holding companies (HoldCos with investment portfolios)
- Asset-intensive businesses (real estate, equipment dealers)
- Distressed businesses (liquidation value)
- Early-stage businesses with no earnings history
- CRA disputes where "fair market value" of specific assets is in question

**ITA Reference:** IT-416R3 (Valuation of Shares of a Corporation Receiving Passive Income) — CRA's guidance on asset-based valuation for passive holding corporations.

---

### 4.1 Net Asset Value (NAV) Methodology

```
NAV = Fair Market Value of All Assets
    - Fair Market Value of All Liabilities
    = Net Asset Value (= Equity Value)

Adjustments to Book Value:
+ Unrealized appreciation on capital assets (land, building, equipment)
+ Unrealized appreciation on investments (securities, real estate)
+ Fair value of intangibles not on balance sheet (goodwill, customer lists, IP)
- Contingent liabilities (tax exposures, litigation, guarantees)
- Deferred tax liability on unrealized gains (if assets sold on exit)
```

**Key distinction:** Book NAV (balance sheet) vs. Economic NAV (fair market value of each asset).

**Example — HoldCo NAV:**
```
Assets (Book Value → FMV Adjustment → FMV):
  Cash: $200,000 → $0 → $200,000
  GIC / short-term bonds: $500,000 → $0 → $500,000
  Publicly traded equities: $750,000 → +$200,000 → $950,000
  Rental property (cost): $1,200,000 → +$300,000 → $1,500,000
  OpCo shares (at cost): $100,000 → +$900,000 → $1,000,000
Total Assets FMV: $4,150,000

Liabilities:
  Mortgage on rental property: ($600,000)
  Deferred tax on unrealized gains ($200K + $300K + $900K = $1.4M gains × 26.5% corp rate): ($371,000)
Total Liabilities: ($971,000)

NAV (Equity Value): $3,179,000
```

The deferred tax haircut is critical — a sophisticated buyer will discount for the tax cost of liquidating the portfolio.

---

### 4.2 Intangible Asset Valuation

Intangibles often represent the majority of value in a modern business. Three recognized methods:

**Relief from Royalty Method (most common for IP / brands):**
```
Value of IP = Σ (Revenue × Royalty Rate × (1-T)) ÷ (1+r)^t + Terminal Value

Where:
Revenue = Projected revenue attributable to the IP
Royalty Rate = Market rate at which the IP would be licensed (derived from comparables)
T = Tax rate
r = Risk-adjusted discount rate
t = Year number
```

Royalty rate benchmarks (arm's length, CRA-defensible):
- Software / technology IP: 3% - 10% of revenue
- Pharmaceutical / biotech: 10% - 25% of revenue
- Brand / trademark: 0.5% - 5% of revenue
- Customer lists / relationships: 1% - 5% of revenue

**Excess Earnings Method (for customer relationships / goodwill):**
```
Intangible Value = Excess Earnings ÷ Capitalization Rate

Excess Earnings = Normalized Earnings - Required Return on Tangible Assets
Required Return on Tangible = Fair Value of Net Tangible Assets × Required Rate of Return
```

**Replacement Cost Method:**
For internally developed software, databases, proprietary processes:
```
Value = Cost to recreate × (1 - Functional Obsolescence %) × (1 - Economic Obsolescence %)
```

**CRA Transfer Pricing Alignment:** If IP is being transferred between related parties (e.g., Canadian OpCo to offshore structure), the valuation MUST be arm's length per ITA s.247. Use the Relief from Royalty method and document thoroughly. See `docs/ATLAS_FOREIGN_REPORTING.md` for transfer pricing rules.

---

### 4.3 CRA FMV Definition — Henderson Estate v. MNR

The foundational Canadian case defining Fair Market Value for tax purposes:

**Henderson Estate and Bank of New York v. MNR, 73 DTC 5471 (FCTD)**

Key holding: FMV is "the highest price available in an open and unrestricted market between informed and prudent parties acting at arm's length and under no compulsion to transact."

**The five elements of FMV:**
1. **Highest price** — not average, not most likely; the maximum achievable
2. **Open and unrestricted market** — no artificial constraints
3. **Informed parties** — both buyer and seller have full information
4. **Prudent parties** — acting in their economic self-interest
5. **Arm's length** — no special relationship affecting the price

**Why this matters for Canadian tax filings:**
- All property transferred between non-arm's length parties (s.69): must use FMV
- Death (deemed disposition at death per s.70(5)): FMV at date of death
- Gift (s.69(1)(b)): proceeds deemed to be FMV
- Shareholder benefits (s.15(1)): FMV determines benefit amount
- Estate freezes, rollovers, corporate reorganizations: all anchored to FMV

**Penalties for misvaluation:**
- s.163(2): Gross negligence penalty = greater of $100 or 50% of understated tax
- s.247(3): Transfer pricing penalty (up to 10% of quantum of transfer)
- Tax Court findings of misvaluation can lead to reassessments going back 7+ years (vs. normal 3-year window) where misrepresentation is found

---

## 5. Capitalized Earnings (Income Approach)

### What It Is

The capitalized earnings method values a business by dividing normalized earnings by a capitalization rate. It is a simplified DCF appropriate for stable, mature businesses with predictable earnings and no high-growth period.

```
Value = Normalized Earnings ÷ Capitalization Rate

Capitalization Rate = Discount Rate (WACC) - Long-Term Growth Rate

Value = Normalized Earnings ÷ (WACC - g)
```

This is mathematically equivalent to a single-stage DCF where growth is constant in perpetuity — the Gordon Growth Model applied to earnings.

---

### 5.1 Calculating Normalized Earnings

Normalization is the most important step. The goal: represent sustainable, recurring earnings that a new owner of the business would expect to receive.

**Standard add-backs (increase earnings):**
```
Reported Net Income (or EBITDA): $XXX
+ Owner salary above arm's length market rate
+ Non-recurring expenses (one-time items)
+ Personal expenses charged to business
+ Excessive rent to related party (above market)
+ One-time professional fees (legal disputes)
+ Discretionary travel and entertainment above reasonable level
+ Depreciation on personal-use assets
+ Amortization of goodwill (if non-cash, non-economic)
= Normalized Earnings Pre-Tax

× (1 - Tax Rate)
= Normalized After-Tax Earnings
```

**Standard deductions (decrease earnings):**
```
- Market-rate replacement salary for owner's working role
- Normalized maintenance capex required to sustain earnings
- Contingent liabilities likely to crystallize
- Below-market rent that will normalize post-sale
```

**Weighting historical years:**
Not all years are equally representative. Common approaches:

| Method | When to Use |
|---|---|
| Simple 3-year average | Stable, mature business |
| Weighted 3-year (3:2:1 — most recent weighted highest) | Growing business |
| Single most recent year | High-growth, recent inflection point |
| Expert judgment blend | Turnaround, restructuring, or market disruption period |

---

### 5.2 Selecting the Capitalization Rate

```
Cap Rate = Risk-Free Rate + Equity Risk Premium + Size Premium + CSRP - Long-Term Growth Rate

Practically:
Cap Rate = WACC - g
```

**Capitalization Rate Ranges by Business Type (Canada, 2025-2026):**

| Business Type | Cap Rate Range | Implied Multiple |
|---|---|---|
| Large established business ($25M+ revenue) | 8% - 12% | 8x - 12.5x |
| Mid-size business ($5M - $25M revenue) | 12% - 18% | 5.5x - 8x |
| Small established business ($1M - $5M revenue) | 18% - 25% | 4x - 5.5x |
| Small owner-operated (<$1M revenue) | 25% - 40% | 2.5x - 4x |
| Early-stage / pre-profit | 35% - 60%+ | 1.7x - 2.9x |

**Example Calculation:**
```
OASIS Normalized After-Tax Earnings: $117,000 (from normalized EBITDA above, adj. for tax)
Cap Rate: 30% (early-stage SaaS, key person risk, small size)

Value = $117,000 ÷ 30% = $390,000

Cross-check with earnings multiple: $117K × 3.3x = $390K ✓ (consistent)

Sensitivity:
Cap Rate 25%: $468,000
Cap Rate 30%: $390,000
Cap Rate 35%: $334,000
```

---

## 6. SaaS-Specific Valuation

### Why SaaS Is Different

SaaS businesses are valued differently from traditional businesses for several structural reasons:
1. **Recurring, predictable revenue** (ARR vs transactional) → higher multiple
2. **Negative cash flow early, massive cash flow later** → DCF underestimates value unless growth period is long
3. **Revenue recognition under IFRS 15** — performance obligations over time, not at point of sale
4. **Key metrics (NRR, CAC, LTV) reveal unit economics** that EBITDA alone cannot

---

### 6.1 Key SaaS Metrics That Drive Valuation

**Annual Recurring Revenue (ARR):**
```
ARR = MRR × 12
MRR = Sum of all active monthly subscription revenue
     (NOT one-time fees, NOT professional services)

ARR Movement:
New ARR: Revenue from new customers
Expansion ARR: Revenue from upsells/cross-sells to existing customers
Churned ARR: Revenue lost from cancelled customers
Contracted ARR: Revenue lost from downgrades
Net New ARR = New + Expansion - Churned - Contracted
```

**Net Revenue Retention (NRR) / Net Dollar Retention (NDR):**
```
NRR = (Starting ARR + Expansion - Contraction - Churn) ÷ Starting ARR × 100%

Interpretation:
NRR > 120%: Elite (Snowflake-tier, Datadog-tier)
NRR 110-120%: Excellent (enterprise SaaS benchmark)
NRR 100-110%: Good (healthy growth)
NRR 90-100%: Adequate (replacement growth)
NRR < 90%: Concerning (shrinking customer base in value)
```

NRR is the single most powerful driver of SaaS valuation multiples. A company with 120% NRR grows revenue from existing customers alone — new customer acquisition is purely additive.

**Customer Acquisition Cost (CAC) and LTV:**
```
CAC = Total Sales & Marketing Spend ÷ New Customers Acquired (same period)

LTV = ARPA × Gross Margin % ÷ Churn Rate
     (where ARPA = Average Revenue Per Account)

LTV/CAC ratio:
> 3x = Healthy (benchmark for SaaS)
> 5x = Excellent
< 2x = Concerning (unprofitable unit economics)

CAC Payback Period = CAC ÷ (ARPA × Gross Margin %)
< 12 months = Excellent
12-18 months = Good
18-24 months = Acceptable
> 24 months = Concern
```

**Gross Revenue Churn:**
```
Gross Revenue Churn = Churned ARR ÷ Beginning ARR × 100%

Annual benchmarks:
< 5% annual = Elite
5-10% = Good
10-20% = Manageable
> 20% = Value destructive
```

---

### 6.2 SaaS Valuation Multiples Framework

**EV/ARR multiple selection matrix:**

| ARR Growth | NRR | Gross Margin | Rule of 40 | EV/ARR Multiple (2025) |
|---|---|---|---|---|
| > 100% | > 120% | > 75% | > 80 | 15x - 25x+ |
| 60-100% | 110-120% | > 70% | 60-80 | 8x - 15x |
| 40-60% | 100-110% | > 65% | 40-60 | 4x - 8x |
| 20-40% | 90-100% | > 60% | 20-40 | 2x - 4x |
| < 20% | < 90% | < 60% | < 20 | 1x - 2x |

Sources: Bessemer Venture Partners State of the Cloud Report (annual), SaaS Capital Index, Battery Ventures State of Public Market SaaS

**EV/NTM Revenue vs. NTM Growth Rate regression:**
A rough rule of thumb for 2024-2025 market:
```
EV/NTM Revenue ≈ 0.5 × (NTM Revenue Growth %)

Example:
Company growing at 80% YoY → ~40x NTM revenue might be a VC expectation in prior years
2024 market: apply a compression factor of 0.3-0.5x from peak multiples
→ 80% growth → 24-40x NTM revenue (high end; for elite metrics only)
→ 40% growth → 12-20x NTM revenue
→ 20% growth → 6-10x NTM revenue
```

---

### 6.3 Cohort Analysis for Churn-Adjusted Valuation

Traditional valuation ignores cohort-level revenue decay from churn. Sophisticated buyers always request cohort data.

**How to build a cohort model:**
```
For each acquisition cohort (quarterly or annual):
  Month 0: $ARR at acquisition
  Month 12: $ARR × (1 - annual churn)
  Month 24: $ARR × (1 - annual churn)^2
  Month 36: $ARR × (1 - annual churn)^3
  etc.

Sum all cohort revenue trajectories to get total revenue projection
Add new cohort acquisitions each period
Result: revenue projection that accounts for inherent decay from existing base
```

This methodology reveals that a company with 20% annual churn will lose 65% of a cohort's revenue over 5 years — making the customer asset worth far less than a simple ARR multiple implies.

---

### 6.4 Canadian SaaS M&A Market Context

**Relevant Canadian SaaS exits (public record, 2019-2024):**

| Company | Acquirer | ARR at Exit | Multiple |
|---|---|---|---|
| Tulip Retail | Acquisition | ~$50M ARR | ~6-8x |
| Hootsuite | Meridian Partners | ~$300M ARR | ~3-4x (distressed) |
| Shopify | Public (TSX/NYSE) | $6B+ ARR | 20x+ NTM |
| Lightspeed | Public (TSX/NYSE) | ~$800M ARR | 8-12x NTM |

For sub-$5M ARR companies in Canada, buyer universe is primarily:
1. Strategic acquirers (large SaaS companies expanding features)
2. Private equity (searching for platform companies to build on)
3. Search funds (individual operators acquiring single businesses)
4. Management buyouts (existing team buying out founder)

**Canadian government as M&A catalyst:**
SR&ED tax credits (43% effective for CCPCs) increase the after-tax value of acquired technology assets. A strategic acquirer who can claim SR&ED on acquired IP pays effectively 43% less for that IP. This increases buyer willingness to pay — and is a negotiation point rarely used by Canadian SaaS sellers.

---

## 7. Valuation Discounts and Premiums

### 7.1 Discount for Lack of Control (Minority Discount)

When valuing a non-controlling interest in a private company, apply a minority discount to reflect the inability to direct operations, set compensation, declare dividends, or force a liquidity event.

```
Minority Discount = 1 - (1 ÷ (1 + Control Premium))

Example:
Control Premium = 30%
Minority Discount = 1 - (1 ÷ 1.30) = 23.1%

Value of 40% minority interest:
Control Value of Business: $2,000,000
Pro-rata 40%: $800,000
Less Minority Discount (23.1%): ($184,800)
Minority Interest Value: $615,200
```

**Range:** 15% - 35% depending on governance rights, shareholder agreement protections, voting class structure.

**CRA consideration:** In related-party transactions, CRA may challenge minority discounts claimed to reduce gift/benefit amounts. Document the discount rigorously with reference to shareholder agreement, lack of drag-along/tag-along rights, lack of board seat.

---

### 7.2 Discount for Lack of Marketability (DLOM)

Reflects the lack of a ready market to sell a private company interest. Even a controlling interest in a private company takes 6-18 months to sell vs. seconds for public shares.

**Empirical DLOM studies:**

| Study | Average DLOM Found |
|---|---|
| Restricted stock studies (pre-IPO) | 25% - 45% |
| Pre-IPO studies | 40% - 60% |
| Mandelbaum factors (Tax Court methodology) | 15% - 40% |
| Protective Put model (Longstaff) | 25% - 45% |

**Mandelbaum v. Commissioner, T.C. Memo 1995-255:**
The foundational US Tax Court case establishing a 9-factor framework for DLOM. Adopted widely in Canadian practice:
1. Financial statement analysis and distributions
2. Business nature and history
3. Economic outlook
4. Book value vs. enterprise value
5. Dividend-paying capacity
6. Goodwill and intangibles
7. Sale of interest restrictions (shareholder agreement)
8. Market for shares (trading history)
9. Comparable transaction data

**Practical DLOM by holding period:**

| Expected Holding Period to Exit | DLOM |
|---|---|
| < 1 year (imminent exit) | 5% - 15% |
| 1-3 years | 15% - 25% |
| 3-5 years | 25% - 35% |
| 5+ years (indefinite hold) | 30% - 40% |

**Combined discount example:**
```
Business 100% Control Value: $5,000,000
Minority interest (40%):
  Pro-rata value: $2,000,000
  Minority discount (20%): ($400,000)
  After minority discount: $1,600,000
  DLOM (25%): ($400,000)
  Final minority interest FMV: $1,200,000

Effective combined discount: 40% from pro-rata value
```

---

### 7.3 Key Person Discount

When the business's value is substantially dependent on one individual (typically the founder), a key person discount reflects the risk that loss of that person would damage the business.

**Quantification approach:**
- Estimate revenue/earnings that would be at risk if key person departed suddenly
- Discount for probability × impact
- Typically 5% - 20% of total business value
- Reduce via: employment contract, non-compete, strong management team, documented processes, key person insurance

**Tax planning note:** If key person life insurance is owned by the corporation, the death benefit flows through the Capital Dividend Account (CDA), allowing tax-free payment to shareholders. This is a direct mitigation strategy for key person risk — and a valuation uplift.

---

### 7.4 Control Premium

When a buyer acquires a controlling interest (>50%, or effective operational control), they pay a premium above the minority/public market value.

```
Control Premium = (FMV of Controlling Interest - FMV of Minority Interest) ÷ FMV of Minority Interest × 100%
```

**Drivers of higher control premiums:**
- Competitive auction with multiple strategic bidders
- Significant operational synergies available
- Strategic scarcity (target has defensible competitive position)
- Technology assets with network effects
- Long-term contracts / captive customer base

**Drivers of lower control premiums:**
- Single buyer negotiation (no competition)
- Seller under time pressure / distress
- Financial buyer (PE firm) — limited synergies; values cash flows only
- Fragmented, easy-to-replicate business

---

## 8. CRA Valuation Rules

### 8.1 FMV Definition Recap (ITA Application)

All provisions below require FMV determination based on Henderson Estate standard:

| ITA Section | Triggering Event | FMV Consequence |
|---|---|---|
| s.69(1) | Non-arm's length transfer | Proceeds deemed to be FMV |
| s.70(5) | Death (deemed disposition) | FMV at date of death |
| s.15(1) | Shareholder benefit | Benefit = FMV - Amount Paid |
| s.84(1) | Deemed dividend on share issuance | FMV of consideration received |
| s.85 | Rollover elected amount | Floor = ACB, Ceiling = FMV |
| s.110.6 | LCGE (QSBC shares) | FMV at date of sale |
| s.247 | Transfer pricing | Arm's length = FMV pricing |

---

### 8.2 CRA Valuation Process — What Happens in an Audit

**CRA Business Equity Valuation (BEV) Program:**
CRA has specialized valuators in their Business Equity Valuation group who review transactions involving private company shares.

**Triggers for CRA valuation review:**
1. Estate filing with private company shares (FMV reported on T1 terminal return)
2. Section 85 rollover where CRA questions elected amount
3. Estate freeze (s.86) where new share values are questioned
4. Large capital gains exemption claims (>$500K LCGE)
5. Related party transactions at non-arm's length prices
6. Shareholder benefit assessments

**CRA's methodology preferences (IC 89-3):**
- CRA prefers income-based approaches (DCF or capitalized earnings) for operating businesses
- Asset-based for holding companies and passive investment corporations
- Market approaches as corroborating methods
- CRA is skeptical of high DLOM and minority discounts — will challenge aggressively

**Defending a valuation at CRA:**
1. Retain a Chartered Business Valuator (CBV) — the professional designation in Canada (CICBV — Canadian Institute of Chartered Business Valuators)
2. Obtain a full CBV opinion report (not just a calculation engagement) — higher standard of evidence
3. Document all assumptions explicitly with reference to market data
4. Cross-check with at least two methodologies
5. File the CBV opinion with the T1 or T2 return when a large amount is at stake

**IT-416R3 — Valuation of Shares:**
CRA's interpretation bulletin for valuing shares of a corporation. Key points:
- Look-through to underlying assets for holding corporations
- Going concern vs. liquidation: depends on whether business would continue under new owner
- Minority interest in private company: DLOM is recognized but limited
- Goodwill: recognized but must be supported by earnings evidence

---

### 8.3 Penalties for Misvaluation

**Civil penalties:**

| Provision | Description | Penalty |
|---|---|---|
| s.163(2) | Gross negligence | Greater of $100 or 50% of understated tax |
| s.163.2(4) | Third-party civil penalty (advisor who prepared misvalued document) | Greater of $1,000 or 50% of advisor benefit |
| s.247(3) | Transfer pricing — inadequate documentation | 10% of quantum of transfer (even if arm's length price found) |

**Criminal penalties (rare but possible for egregious cases):**
- s.238: Failure to file — fine up to $25,000 + up to 12 months imprisonment
- s.239: Tax evasion — up to $200,000 + 200% of tax evaded + 5 years imprisonment

**Limitation periods:**
- Normal reassessment period: 3 years from notice of assessment
- Extended to 6 years: if misrepresentation due to carelessness, neglect, or wilful default
- No limitation: if fraud involved

---

## PART II: M&A TAX MECHANICS

---

## 9. Section 85 Rollover

### Overview

The Section 85 rollover is the most important tax provision in Canadian corporate law for entrepreneurs. It allows the tax-deferred transfer of eligible property to a corporation (or between corporations) in exchange for shares plus other consideration. Without it, every business incorporation would trigger immediate capital gains tax.

**Legislative authority:** ITA s.85(1) (individual to corporation), s.85(2) (partnership to corporation)

---

### 9.1 Eligible Property

Not all property qualifies. The list under s.85(1):

**Eligible:**
- Capital property (real property, equipment, vehicles, investments)
- Eligible depreciable property (Class 10 vehicles, Class 8 equipment, etc.)
- Real property inventory (developer's land)
- Eligible capital property → now Class 14.1 (goodwill, customer lists, trademarks, non-competes)
- Canadian resource property
- Foreign resource property
- Inventory of a business (goods for sale) — with conditions
- Accounts receivable — with special s.22 election

**NOT Eligible:**
- Cash (but: can transfer cash as part of transaction, with boot adjustment)
- Services / labour (future services cannot be rolled over)
- Personal use property below threshold
- Debt instruments (promissory notes) held by the transferor

---

### 9.2 The Elected Amount — Floor and Ceiling Rules

The elected amount determines the proceeds of disposition for the transferor AND the cost base to the corporation receiving the property. The flexibility of the election is what makes s.85 powerful.

```
Floor (minimum elected amount):
= MAX (ACB of property, UCC of property if depreciable, $1 if eligible capital property)

Ceiling (maximum elected amount):
= FMV of the property at time of transfer

You elect any amount between floor and ceiling.
```

**Strategic goal:** Elect at the lowest possible amount to maximize tax deferral.

**Depreciable property rules:**
- If elected amount < UCC → no recapture, no CG triggered
- If elected amount > UCC but < Original Cost → recapture triggered (income)
- If elected amount > Original Cost → both recapture AND capital gain triggered

**Example — OASIS Software Platform Transfer:**
```
Property: Internally developed software platform (Class 12)
ACB / UCC: $0 (immediately expensed under capital cost allowance rules)
FMV: $500,000

Floor: $1 (elected minimum for s.85)
Ceiling: $500,000

Optimal election: $1

Result:
- Transferor (CC personally) realizes $1 as proceeds → no capital gain
- Corporation receives asset at cost of $1
- The $499,999 of unrealized appreciation is deferred inside the corporation
- Accrued gain of $499,999 will be realized when corporation sells the asset
```

**Consideration received must equal FMV of property transferred:**
Total consideration (shares + non-share "boot") must = FMV of transferred property. If not, CRA may assert a shareholder benefit (s.15) or a gift.

---

### 9.3 Boot Consideration

"Boot" = any non-share consideration received in the exchange (cash, debt, notes payable by the corporation).

**Boot rules:**
- Boot is allocated first to the elected amount
- Boot cannot exceed the elected amount (otherwise immediate income tax triggered)
- Common boot uses:
  - Receive a promissory note = extract tax-paid capital from the business
  - Receive assumption of existing debt on transferred property

```
Example — Boot for Working Capital Access:
Transfer property with ACB = $200,000, FMV = $800,000
Want to access $200,000 cash without immediate tax

Election structure:
Elected Amount: $200,000 (= ACB = floor)
Boot (promissory note): $200,000
Share consideration (preferred shares): $600,000

Result:
- No capital gain triggered (elected at ACB)
- CC receives $200K note (tax-free return of capital)
- $600K preferred shares = deferred gain position
```

---

### 9.4 Paid-Up Capital (PUC) Considerations

After a s.85 rollover, the PUC of issued shares must be carefully tracked. PUC grinding is an anti-avoidance rule designed to prevent extraction of PUC in excess of the elected amount.

**PUC Grind (s.85(2.1)):**
```
PUC of New Shares = MIN (Legal Capital of New Shares, Elected Amount - Boot)

If this results in a PUC reduction, the grind equals:
Grind = Legal Capital - Elected Amount + Boot

PUC after grind = Legal Capital - Grind
```

**Why PUC matters:**
- PUC can be returned to shareholders tax-free (capital returns)
- Excess over PUC is a deemed dividend (s.84)
- PUC tracking errors compound over multiple transactions — can result in double-taxation

---

### 9.5 Joint Election Filing (T2057)

**Form T2057** — Election on Disposition of Property by a Taxpayer to a Taxable Canadian Corporation

**Filing requirements:**
- Filed by BOTH transferor AND corporation
- Due date: Earlier of: (a) 3 years after transferor's tax filing deadline, (b) 1 year after corporation's tax filing deadline
- Late filing allowed: with CRA discretion fee ($100/month, max $8,000)
- Must include: description of property, ACB, UCC, FMV, elected amount, consideration received

**Common traps:**
1. **Inadequate consideration:** Total consideration ≠ FMV → s.15 shareholder benefit
2. **Shareholder benefit:** If corporation assumes personal liabilities exceeding elected amount
3. **PUC grinding failure:** Creating phantom PUC that will be taxed as dividend on return
4. **Post-rollover disposition:** If corporatized property is sold within 90 days, CRA may challenge that FMV was different at time of rollover (temporal issue)
5. **Related party transfer:** Must be to a corporation controlled by (or related to) the transferor

---

### 9.6 The Incorporation Rollover — OASIS Application

When CC incorporates OASIS AI Solutions, the s.85 rollover is the mechanism to transfer business assets to the corporation tax-free.

**Assets typically transferred:**
| Asset | ACB | FMV | Optimal Elected Amount |
|---|---|---|---|
| Client contracts / relationships | $0 | TBD | $1 |
| Software / IP | $0 | TBD | $1 |
| Equipment (MacBook, etc.) | UCC (after CCA) | FMV | UCC |
| Accounts receivable | Face value | Face value | Face value (+ s.22) |
| Business name / brand | $0 | TBD | $1 |

**Section 22 Election (Accounts Receivable):**
When AR is transferred alongside a business, s.22 allows the buyer (corporation) to deduct bad debts that become uncollectible — even on AR transferred at face value. File T2022 jointly.

**Result of OASIS incorporation rollover:**
- All accrued business value transfers to corporation with zero immediate tax
- Future income taxed at corporate rate (12.2% vs. personal marginal rate)
- LCGE planning begins immediately (24-month holding period clock starts)
- Freeze preferred shares created for estate planning / multiplication

---

## 10. Section 86 Share Exchange (Estate Freeze)

### Overview

Section 86 allows shareholders to exchange ALL shares of a class for a mix of different shares (and potentially other consideration) on a tax-deferred basis. This is the primary mechanism for an estate freeze — locking in the current value of a business for the founder while allowing future growth to accrue to the next generation.

**Legislative authority:** ITA s.86

---

### 10.1 Conditions for Section 86 to Apply

1. The taxpayer must dispose of ALL shares of a particular class
2. As part of the reorganization of the corporation's capital structure
3. Receiving new shares of the SAME corporation in exchange
4. The exchange must be part of a reorganization of capital

**Key difference from s.85:** Section 86 applies to reorganizations of capital structure involving shares-for-shares exchange (plus possible boot). Section 85 is about transferring property TO a corporation.

---

### 10.2 The Estate Freeze — Structure and Mechanics

**Purpose:** Freeze the current business value in the founder's hands (via preferred shares with fixed redemption value), while allowing future appreciation to flow to children/family trust (via new common shares).

**Step-by-step estate freeze via s.86:**

```
Before Freeze:
CC holds 100 common shares of OASIS Corp
Current value: $1,000,000
Future value potential: $5,000,000+

Step 1: CC exchanges all 100 common shares for:
  - 1,000,000 freeze preferred shares (redeemable at $1/share = $1,000,000 total)
  - Nominal common shares (1,000 new common shares at $0.001 = $1 nominal)

Step 2: Family trust subscribes for 9,000,000 new common shares at nominal cost
  (or children personally subscribe for new common shares)

Step 3: Future business value growth accrues to common shares held by trust/children

Result:
  CC's estate: $1,000,000 (frozen — preferred share redemption value)
  Family trust: Holds all future appreciation above $1M
  Total business value at exit $5M: CC's estate $1M, trust holds $4M

  Capital gains tax on death: Only on $1M preferred shares (if not redeemed)
  vs. Without freeze: Estate tax on full $5M

  Tax saved (estimated at 27% capital gains inclusion, 53% top marginal):
  Tax on $5M (no freeze): ~$714,000
  Tax on $1M (with freeze): ~$143,000
  Savings: ~$571,000 — all future appreciation flows to trust essentially tax-free
```

---

### 10.3 Gift/Benefit Anti-Avoidance

The critical valuation risk in a freeze: if preferred shares are valued too low (making the common shares worth more than nominal at the time of freeze), CRA may assert:
- **s.86(2) benefit:** If FMV of shares received < FMV of shares surrendered + benefit to non-arm's length person
- The benefit = gift to family trust/children → shareholder benefit or deemed dividend

**Best practice:** Obtain an independent CBV valuation at the time of freeze. Document that:
- Preferred share FMV = Total Business FMV at time of freeze
- Common shares issued for nominal consideration reflect ZERO current value
- Common share value is entirely prospective (future growth only)

---

### 10.4 Section 85 vs Section 86 — When to Use Each

| Scenario | Use s.85 | Use s.86 |
|---|---|---|
| Incorporating a sole proprietorship | Yes | No |
| Transferring property to an existing corporation | Yes | No |
| Reorganizing share capital to implement an estate freeze | No | Yes |
| Creating two classes of shares from one class | No | Yes |
| Separating voting from economic rights | No | Yes |
| Splitting a business line into a new company | Use s.85 for assets | N/A |

Often, a complete freeze transaction uses BOTH:
1. s.85 rollover to transfer business assets to the corporation (at incorporation)
2. s.86 exchange to freeze the shares issued in step 1 (subsequent year)

---

## 11. Section 87 Amalgamation

### Overview

Section 87 governs the tax treatment of an amalgamation — the legal merger of two or more Canadian corporations into a single new corporation. An amalgamation can be horizontal (two sibling companies merging) or vertical (parent absorbing a wholly-owned subsidiary).

**Legislative authority:** ITA s.87; CBCA (Canada Business Corporations Act) s.181-185 for corporate law requirements

---

### 11.1 Tax Consequences of Amalgamation

**For the predecessor corporations:**
- Deemed to have disposed of all assets immediately before amalgamation
- Subject to s.87(2): NO income, gain, or loss recognized — the attributes carry forward

**For the new amalgamated corporation:**
```
Tax attributes that carry forward (s.87(2)):
- Non-capital loss carryforwards (s.87(2.1))
- Net capital loss carryforwards
- UCC (Undepreciated Capital Cost) of all CCA pools
- RDTOH (Refundable Dividend Tax on Hand)
- ERDTOH (Enhanced Refundable Dividend Tax on Hand)
- CDA (Capital Dividend Account)
- Eligible capital property (now Class 14.1)
- SREP (Scientific Research and Experimental Development) expenditure pools
- FMV of assets = cost to predecessor corporation (no step-up)
```

---

### 11.2 The Bump Rules — Section 87(11)

The bump rules allow a parent corporation, upon vertical amalgamation with a subsidiary, to step up (increase) the cost base of certain non-depreciable capital property to its FMV at the time of acquisition.

**When the bump applies:**
- Parent owned ≥ 90% of subsidiary
- Assets are "non-depreciable capital property" (land, shares of other companies, bonds)
- NOT eligible: depreciable property, eligible capital property, Canadian resource property

**Bump calculation:**
```
Bump Amount = ACB of Subsidiary Shares in Parent's Hands
            - Net Tax Cost of Subsidiary's Assets at Acquisition
            (i.e., the difference between what parent paid for subsidiary
            and what the subsidiary's assets cost)

This bump is allocated among non-depreciable capital property
to step up their cost bases to FMV.
```

**Why the bump matters:**
Without the bump, a parent that acquires a subsidiary for $5M, when the sub's assets have a $2M tax cost, has a permanent gap. On future sale of those assets, $3M of gain is taxed twice (once in the acquisition price, once on the asset sale). The bump eliminates this double taxation.

---

### 11.3 Loss Restriction Events

A "loss restriction event" (LRE) under s.251.2 occurs when a person acquires control of a corporation. After an LRE:
- Non-capital loss carryforwards are restricted (s.111(5))
- Net capital losses are eliminated (s.111(4))
- Capital property is deemed disposed at FMV (potential gain triggers)
- Unused SRED expenditures are restricted

**Implications for M&A:**
- Buyers pay less for companies with large loss carryforwards if a change of control triggers LRE
- Structure acquisitions carefully around change of control timing
- Consider whether target has had a prior LRE that already limited its losses

---

### 11.4 Amalgamation vs. Wind-Up — Strategic Comparison

| Factor | Amalgamation (s.87) | Wind-Up (s.88) |
|---|---|---|
| Result | New continuing corporation | Parent absorbs subsidiary |
| Tax attributes | Both predecessors carry forward | Sub's attributes move to parent |
| Bump available | Yes (s.87(11)) | Yes (s.88(1)(d)) |
| Corporate law | Requires CBCA amalgamation process | Simpler dissolution |
| Shareholder approval | Required (often 2/3 vote) | If 90%+ owned: straightforward |
| Continuity of contracts | Automatic (new corp assumes all) | Requires assignment |
| Best for | Equal merger of two independent companies | Parent cleaning up subsidiary |

---

## 12. Section 88 Wind-Up

### Overview

Section 88 governs the winding up (dissolution) of a Canadian corporation. The key provision for tax planning is s.88(1): the wind-up of a subsidiary into a parent corporation where the parent owns ≥ 90% of subsidiary shares.

**Legislative authority:** ITA s.88(1) — subsidiary wind-up; s.88(2) — general corporate dissolution

---

### 12.1 Section 88(1) — Subsidiary Wind-Up

When a parent corporation owns ≥ 90% of a subsidiary and winds it up:

**Tax treatment:**
- Subsidiary is deemed to have disposed of all assets at their ACB / UCC (no gain/loss — same as s.87)
- Parent is deemed to have received all assets at same cost (continuity)
- Net tax attributes of subsidiary (losses, RDTOH, CDA, CCA pools) flow to parent
- **Critical: Bump rules apply (s.88(1)(d))** — same as amalgamation, parent can step up cost of non-depreciable capital property

**The s.88(1)(d) bump — detailed rules:**

```
Maximum bump on any particular property:
= MIN of:
  (a) FMV of that property at acquisition time
  (b) ACB of subsidiary shares (in parent's hands)
      MINUS net tax cost of ALL subsidiary's property at acquisition

Total bump cannot exceed:
  ACB of subsidiary shares - Net fair market value of subsidiary's assets at time of acquisition
```

**Loss streaming on wind-up:**
After a wind-up, the parent can access the subsidiary's loss carryforwards, but subject to the change of control restrictions from when the parent first acquired control. The losses can offset income from the same type of business that generated the losses.

---

### 12.2 Section 88(2) — General Dissolution

For a corporation that isn't being wound up into a parent (i.e., standalone dissolution):
- Corporation is deemed to have disposed of all assets at FMV immediately before dissolution
- Capital gains / recapture triggered on any appreciated assets
- Remaining funds distributed to shareholders — treated as deemed dividend (s.84(2)) to the extent of PUC surplus

**Planning opportunity: Use CDA before dissolution**
Before dissolving a corporation, extract the Capital Dividend Account (CDA) balance tax-free via capital dividend election (s.83(2)). This is cash that accumulated from:
- The non-taxable portion of capital gains
- Life insurance proceeds
- Capital dividends received from other corporations

Any CDA balance NOT extracted before dissolution is permanently lost.

---

## 13. Asset Purchase vs Share Purchase

### The Fundamental Tension

This is the most common negotiation point in Canadian M&A. The buyer wants assets; the seller wants shares. Understanding exactly why allows you to quantify the gap and structure creative solutions.

---

### 13.1 Asset Purchase — Tax Analysis

**For the BUYER:**

Advantages:
- **CCA reset:** Buy assets at FMV, which becomes new UCC. Restart depreciation from a higher base.
- **No legacy liabilities:** Tax debts, contingent liabilities, CRA disputes all stay with vendor
- **SRED base:** Fresh expenditure base for future SRED claims
- **Goodwill:** Class 14.1, 5% CCA on the declining balance; eligible capital property rules
- **Immediate expensing:** Eligible depreciable property can be 100% immediately expensed in first year (s.1100(2) — check current CCPC eligibility)

Disadvantages:
- Requires assignment of all contracts (customers, leases, suppliers)
- May trigger change of control clauses in key contracts
- Higher legal costs (each asset transferred separately)
- HST/GST on asset transfer (mitigated by s.167 election — going concern transfer)

**HST note on asset deals:**
Under ETA s.167, if transferring a business as a "going concern" (buyer will continue the business), the parties can jointly elect to exclude the transfer from HST. File jointly within 90 days of transfer. This avoids $100K+ HST liability on a $1M+ asset deal.

**For the SELLER:**

Disadvantages:
- Asset sale proceeds are taxed as a MIX of income and capital gains at the corporate level:
  - Recapture on depreciable assets: 100% income (fully taxable at 26.5%)
  - Gain on non-depreciable capital property: 50% taxable (capital gains)
  - Goodwill / Class 14.1: half-rate inclusion (25% included) on first $100K, 50% inclusion above
  - Inventory: 100% income
  - AR: 100% income
- Double taxation risk: corporate tax on sale, then personal tax when distributing to shareholder
- LCGE NOT available on asset sales (only on QSBC shares)

---

### 13.2 Share Purchase — Tax Analysis

**For the SELLER:**

Advantages:
- **Capital gains treatment:** All proceeds on share sale receive capital gains treatment (50% inclusion)
- **LCGE eligibility:** $1.25M LCGE if QSBC conditions met → potentially $0 tax on first $1.25M of gain (see Section 16)
- **Clean exit:** No retained liabilities once shares transferred
- **Simpler closing:** One transaction (transfer shares), vs. dozens of asset transfers

**For the BUYER:**

Disadvantages:
- **No CCA reset:** Assets inside corporation carry historical UCC, not FMV
- **Inherits ALL liabilities:** Tax debts, CRA disputes, contingent liabilities, employee claims, customer claims
- **Tax indemnity required:** Buyers negotiate for tax indemnities (usually 3-7 years) covering pre-closing tax exposures

---

### 13.3 Purchase Price Allocation (PPA) in Asset Deals

In an asset deal, the total purchase price must be allocated among the individual assets. This allocation has massive tax implications for both parties.

**ASPE 1582 / IFRS 3 require:**
The acquirer must allocate consideration to identifiable assets (at FMV) and recognize remaining amount as goodwill.

**For TAX purposes (not identical to accounting):**
CRA requires arm's length allocation. If buyer and seller disagree on allocation, CRA may reallocate to reflect FMV.

**Seller's preferred allocation:**
Maximum to capital gains property (50% inclusion) and minimum to inventory/receivables (100% income).

**Buyer's preferred allocation:**
Maximum to assets with short CCA lives (Class 8 equipment at 20%, Class 10 vehicles at 30%) and minimum to goodwill (Class 14.1 at 5%) — faster depreciation deductions.

**Example PPA dispute:**
```
Total purchase price: $3,000,000

Buyer's preferred allocation:
  Equipment (Class 8, 20% CCA): $1,500,000
  Customer lists (Class 14.1, 5% CCA): $500,000
  Goodwill (Class 14.1, 5% CCA): $1,000,000

Seller's preferred allocation:
  Equipment (same): $800,000 (lower = less recapture)
  Customer lists: $200,000 (capital gain, 50% inclusion)
  Goodwill: $2,000,000 (half-rate inclusion, lower tax)

Tax impact difference:
  Seller: paying 26.5% vs 13.25% on ~$500K swing = ~$66K more tax under buyer's allocation
  Buyer: accelerating $500K of deductions from Class 14.1 to Class 8 = NPV benefit of ~$50K
```

The buyer and seller negotiate PPA as part of the purchase agreement. The allocation is binding on both for CRA purposes if documented in the contract.

---

### 13.4 Hybrid Structures — Bridging the Gap

Hybrid deal structures capture the best of both worlds.

**Common hybrid approaches:**

**1. Cash out cash, roll the rest:**
- Seller extracts non-business cash from corporation before sale (dividend, return of PUC, capital dividend)
- Remaining "clean" operating business sold via share deal
- Result: LCGE available on shares; no inefficiency from passive assets

**2. Asset deal at OpCo, HoldCo retains IP:**
- Seller's HoldCo retains IP (software platform, brand)
- OpCo (operating business assets) sold in asset deal
- IP licensed to buyer post-sale (recurring income for HoldCo)
- Result: Buyer gets CCA step-up on operating assets; seller retains IP value on capital account

**3. s.85 rollover for seller, asset deal for buyer:**
- Buyer acquires assets
- Seller's corporation first does an internal s.85 rollover of appreciated assets to a new corporation
- Sell the new corporation (shares) → clean LCGE-eligible company
- Remaining original company contains pre-rollover assets (seller's retained portfolio)

**4. Earnout bridging valuation gap:**
- Pay $2M upfront (buyer's floor value)
- Earn up to $3M additional over 3 years based on revenue/EBITDA milestones
- Bridges buyer/seller gap on future performance expectations

---

## 14. Earn-Outs and Contingent Consideration

### Overview

An earn-out is a contractual provision where part of the purchase price is contingent on the post-closing performance of the acquired business. Earn-outs are common when:
- Buyer and seller disagree on forward-looking value
- Seller's growth projections are aggressive
- Key person (founder) staying on post-close
- Business is early-stage with limited operating history

---

### 14.1 CRA Tax Treatment of Earn-Outs

CRA's treatment depends on the nature of the earnout.

**Section 12(1)(g) — Contingent consideration:**
Where the purchase price is contingent on the use of or production from property:
- Amounts are included in income as RECEIVED (cash basis)
- NOT as capital — treated as ordinary income
- Can be problematic for sellers expecting capital gains treatment

**Section 40 Reserve — Capital Gains:**
For earn-outs that ARE treated as capital gains proceeds:
- Seller can claim a reserve for amounts not yet received
- Reserve = (Unrealized Proceeds ÷ Total Proceeds) × Capital Gain
- Reserve is added back to income in the LATER of:
  - Year following original sale year, OR
  - When proceeds become receivable
- Maximum reserve period: 5 years (s.40(1)(a)(iii))

**Example — Earn-Out Tax Treatment:**
```
Share sale at $2M upfront + $1M earn-out payable if ARR exceeds $500K in Year 2

ACB of shares: $50,000
Total agreed consideration: $3,000,000

Year 1 (sale year):
Capital gain on $2M received: $2,000,000 - $50,000 = $1,950,000
Less: Reserve on unearned $1M: ($650,000) (1M/3M × $1.95M gain)
Taxable capital gain (Year 1): $1,300,000 × 50% = $650,000

Year 2 (earn-out received):
Reverse reserve: +$650,000 income inclusion
Net: $325,000 of capital gains income (after 50% inclusion)

Total capital gains over 2 years: $975,000 — efficiently spread
```

**Structuring earn-outs for capital treatment:**
- Ensure earn-out is based on overall business performance (revenue, EBITDA), not on production from specific property
- Avoid s.12(1)(g) characterization by linking earn-out to profit-based metrics, not output of a particular asset
- Consider a note or deferred payment structure (creates s.40 reserve automatically) vs. contingent earn-out
- Get a tax ruling for large earn-outs if characterization is uncertain

---

### 14.2 Structuring Best Practices

**Earn-out metrics to use (capital-friendly):**
- Total revenue for the acquired business
- Gross profit or EBITDA of the business unit
- Cumulative free cash flow
- Number of customers at end of earn-out period

**Earn-out metrics to avoid (risk of income characterization):**
- Production volume of specific machinery or equipment
- Revenue from specific customer contracts
- Units produced from a particular facility

**Escrow arrangements:**
- Part of upfront payment held in escrow to secure seller's indemnification obligations
- Escrow release triggers must be clearly defined
- Tax treatment: proceeds received when released from escrow (or when claim limitations expire)

**Representation and warranty insurance:**
- Available in Canada for deals >$10M enterprise value
- Insures buyer against undisclosed pre-closing liabilities
- Reduces need for large escrow holdbacks
- Premiums: 2.5% - 4.5% of insured limit
- Increasingly common; allows clean exit for seller

---

## 15. Tax Due Diligence

### Overview

Tax due diligence (TDD) is a systematic review of a target company's tax compliance and potential tax exposures performed by a buyer prior to closing. Every Canadian M&A deal above $1M should include TDD. Failure to identify tax exposure prior to closing means the buyer inherits it in a share deal.

---

### 15.1 Tax Due Diligence Scope

**1. Tax Filing Compliance:**
- Confirm all T2 corporate returns filed (going back statute of limitations: 7 years for flagged items)
- Review notice of assessments for outstanding assessments, objections, appeals
- Confirm T4 employer returns filed, all payroll remittances current
- HST/GST returns filed; confirm HST number and registration status
- Confirm all withholding tax remitted (s.215 for payments to non-residents)

**2. Loss Carryforward Validity:**
- Non-capital losses: 20-year carryforward — confirm they remain valid (no LRE that restricted them)
- Net capital losses: Indefinite carryforward — review trigger events
- ABIL (Allowable Business Investment Loss) — special category, complex rules
- Confirm prior-year loss carryforward schedules in T2 returns match CRA records

**3. RDTOH / ERDTOH / CDA Balances:**
- These balances are valuable tax attributes in a share deal
- Confirm RDTOH balance: $38.33 refundable per $100 of eligible dividends paid
- ERDTOH: $30.67 refundable per $100 of non-eligible dividends
- CDA balance: Can be distributed as tax-free capital dividend post-closing

**4. Transfer Pricing:**
- Any related party transactions? (intercompany services, IP licensing, loans)
- If transactions with non-residents: contemporaneous documentation required under s.247
- Penalty risk: 10% of the quantum of transfer even if arm's length price found

**5. SR&ED Claims:**
- Prior SR&ED claims: Have they been audited/confirmed by CRA?
- Pending claims: Disclosed in T2 but not yet assessed
- Risk: CRA audits 30-35% of SR&ED claims; disallowed claims create reassessment risk
- Buyer should model scenario where prior claims are partially disallowed

**6. HST/GST Compliance:**
- Annual or quarterly HST returns filed on time?
- Input tax credit (ITC) claims appropriate?
- Has company charged HST on ALL taxable supplies?
- Cross-border supplies: zero-rated treatment claimed correctly?

**7. Payroll Compliance (CPP/EI):**
- CPP/EI arrears are priority claims — rank above secured creditors on insolvency
- Review T4 summary for each year; confirm employer remittances on time
- Workers classified as independent contractors: CRA may reassess as employees → arrears liability
- Director liability: Directors personally liable for unremitted CPP/EI under s.227.1

**8. CRA Audit History:**
- Has company been audited? Results?
- Any outstanding queries, requests for information, net worth assessments?
- Has company filed objections or appeals? Status?

---

### 15.2 Tax Due Diligence — OASIS/Early-Stage Company Specific

For a company at OASIS's stage, the key TDD items for a future acquirer:

| Item | Risk Level | Action |
|---|---|---|
| SR&ED claims sustainability | High if claimed | Obtain CRA pre-approval letters |
| Related party transactions (CC's personal use) | Medium | Document arm's length equivalents |
| HST registration + filing | Medium | Ensure filings current; ITC schedule maintained |
| Worker classification (contractors) | Medium | Ensure valid contractor agreements; no employee-like work |
| IP ownership in corporation | High | Ensure formal IP assignment agreements in place |
| ACB of shares | High | Maintain clean T2057 rollover records |

---

## 16. Lifetime Capital Gains Exemption (LCGE) on QSBC Shares

### Overview

The LCGE is Canada's most powerful wealth-building tax provision for entrepreneurs. It allows a Canadian individual to shelter up to $1,250,000 (indexed to inflation; 2025 amount — confirm annually in the federal budget) of capital gains on the sale of qualified small business corporation (QSBC) shares from ALL income tax.

Combined federal + Ontario tax savings: approximately $330,000 - $356,000 per eligible individual at 2025 rates.

**Legislative authority:** ITA s.110.6

---

### 16.1 QSBC Share Conditions — All Three Must Be Met

**Condition 1: Share of a Small Business Corporation (SBC) at time of sale**

The corporation must be a "small business corporation" at the time of sale:
- Canadian-Controlled Private Corporation (CCPC)
- All or substantially all (≥ 90%) of the FMV of its assets are used in an active business carried on primarily in Canada

**"Active business" definition:** Business activities that are not:
- Investment income (dividends, interest, rent — unless incidental)
- Specified investment business (main purpose is earning property income)
- Personal services business

**90% test at sale date:**
```
Total Assets FMV = $1,000,000

Active business assets: $920,000 (clients, IP, equipment, receivables from business operations)
Passive assets: $80,000 (idle cash, GICs, marketable securities)
Active % = $920,000 / $1,000,000 = 92% ✓ PASSES
```

**Condition 2: 24-Month Holding Period (look-back test)**

Throughout the 24 months immediately before the sale, shares must have been:
- Owned by the individual OR a related person (directly or via SHY / partnership)
- AND during that period, more than 50% of FMV of assets used in active business

**50% test during the 24-month period:**
This is a LOWER bar than the 90% test at sale — more than 50% active business assets throughout the holding period.

```
Strategy: Before selling, ensure at every point in the 24 months:
  Active assets > 50% of total assets

If passive assets accumulate (e.g., retained earnings sitting in cash):
  → Strip passive assets to HoldCo via s.84.1-safe dividend or s.85 rollover
  → This "purification" makes the operating company QSBC-clean again
```

**Condition 3: CCPC Status**

The corporation must have been a CCPC throughout the 24-month period. If the company:
- Was ever controlled by a non-Canadian → fails
- Had a public company shareholder → fails
- Was publicly listed → fails (must re-qualify after going private)

---

### 16.2 LCGE Calculation — Worked Example

```
Facts:
CC sells 100% of OASIS Inc. shares
Proceeds: $2,500,000
ACB of shares: $50,000 (post-rollover cost)
Capital gain: $2,450,000

LCGE available to CC: $1,250,000 (assuming zero prior LCGE usage)
Capital gain eligible for LCGE: $1,250,000
Remaining taxable capital gain: $1,200,000

Tax on LCGE portion: $0 (fully sheltered)

Tax on remaining $1,200,000 gain:
  Taxable capital gain (50% inclusion): $600,000
  Ontario + Federal tax at ~53% top marginal rate: $318,000

Total tax on $2.5M share sale: $318,000
Effective tax rate on sale proceeds: 12.7%

Without LCGE:
  Taxable capital gain (50%): $1,225,000
  Tax at 53%: $649,250
  Effective rate: 26.0%

LCGE Saves: ~$331,250
```

---

### 16.3 LCGE Multiplication via Family Trust

The most powerful LCGE planning strategy: use a family trust to multiply the $1.25M exemption across multiple beneficiaries.

**Structure:**
```
CC (founder) → Incorporates OpCo via s.85 rollover
             → Implements estate freeze (s.86): CC holds preferred shares
             → Family trust holds common shares
             → Trust beneficiaries: CC, spouse, children (even if minors)

On sale of OpCo:
  Common shares (held by trust) represent future growth above freeze value
  Trust allocates capital gain to each beneficiary
  Each beneficiary claims their own $1.25M LCGE

Example:
  Total gain on common shares: $5,000,000
  Trust beneficiaries: CC + spouse + 2 children = 4 persons
  Each claims $1.25M LCGE = $5,000,000 total shelter

  Tax on $5M gain WITHOUT trust multiplication: ~$1.3M
  Tax on $5M gain WITH trust multiplication: $0

  Savings: ~$1.3M in lifetime tax
```

**TOSI (Tax on Split Income) Interaction — Critical Trap:**
Since 2018, income allocated by a trust to a beneficiary under age 25 who is not actively engaged in the business is subject to TOSI at the top marginal rate — including capital gains on QSBC shares allocated by the trust.

**TOSI exceptions for capital gains (s.120.4(1) "split income" definition):**
- The beneficiary must meet certain "reasonable return" or "excluded shares" conditions to avoid TOSI on capital gains
- Children under 18: TOSI applies to capital gains from trust allocations
- Children 18-24: TOSI applies unless they meet "excluded business" (20+ hours/week test)
- Spouse: TOSI generally does not apply to capital gains from trust if QSBC conditions met

**Solution to TOSI on children's capital gains from trust:**
- Spouse can claim LCGE without TOSI issue
- Grandchildren may qualify under different conditions
- Tax counsel must review on current TOSI rules before implementation

---

### 16.4 Purification Strategies

If the operating company has accumulated passive assets (excess retained earnings sitting in cash/investments), purification strips these out before the sale to ensure the 90% active asset test is met.

**Method 1: Dividend to HoldCo**
```
OpCo declares a dividend of passive cash → HoldCo receives inter-company dividend tax-free
Result: OpCo's balance sheet cleaned of passive assets
HoldCo holds passive assets (still within corporate structure, low tax)
```

**Method 2: Section 85 Rollover of Passive Assets**
Transfer passive investments from OpCo to HoldCo via s.85 at ACB → no gain triggered, passive assets removed from OpCo.

**Method 3: Redemption of Shares / Return of Capital**
If no HoldCo exists: consider using excess cash to:
- Repurchase shares from other shareholders (reduces passive assets)
- Expand active business operations (convert passive to active)

**Timing of purification:**
Purification must be completed before the 24-month look-back window closes. If selling in June 2027, the active asset test is applied to every day back to June 2025. Start purification early.

---

### 16.5 Anti-Avoidance: Section 55(2)

s.55(2) prevents a corporation from converting a capital gain into a tax-free inter-corporate dividend. When purifying OpCo via dividends to HoldCo, the "safe income" exception must be available.

**Safe income:** The after-tax retained earnings of the paying corporation that are reasonably attributable to the income earned after 1971 and before the dividend.

```
Safe Income Example:
OpCo accumulated safe income: $800,000
OpCo wants to pay $1,000,000 dividend to HoldCo for purification

Safe income covers: $800,000 → no s.55(2) issue
Excess over safe income: $200,000 → triggers s.55(2), reclassified as capital gain

Strategy: Only pay dividends UP TO safe income balance to avoid s.55(2)
Or: Use alternative methods (s.85 rollover, loan repayment) for amounts above safe income
```

**s.110.6(7) Anti-Avoidance:**
The LCGE is denied if it is reasonable to consider that one of the purposes of a transaction was to increase the amount eligible for LCGE. This is a general anti-avoidance rule specific to LCGE planning. Ensure all LCGE planning has legitimate business rationale beyond tax savings alone.

---

## 17. Cross-Border M&A

### 17.1 Non-Resident Acquiring Canadian Company — Section 116

When a non-resident acquires taxable Canadian property (TCP) from a Canadian resident, the buyer has a WITHHOLDING obligation.

**Taxable Canadian Property includes:**
- Shares of a private Canadian corporation (if ≥ 25% interest at any time in prior 60 months + >50% value derived from Canadian real property or resource property)
- Real property in Canada
- Business property of a permanent establishment in Canada

**Section 116 Clearance Certificate process:**
```
Step 1: Canadian seller notifies CRA of pending sale (Form T2062 or T2062A)
        Filed within 10 days of sale agreement

Step 2: CRA issues a "clearance certificate" once satisfied that tax has been/will be paid

Step 3: If no clearance certificate obtained:
  Buyer must withhold 25% of GROSS purchase price and remit to CRA
  Seller must file Canadian tax return to recover excess (or pay shortfall)

Step 4: If clearance not received and buyer doesn't withhold:
  Buyer personally liable to CRA for 25% of price
  (This creates massive liability for foreign buyers — always request clearance)
```

**Treaty exemptions:**
- Canada-US Tax Treaty, Article XIII: Capital gains on sale of shares NOT derived from real property are generally exempt from Canadian tax for US residents (unless the corporation qualifies as a Canadian-resident real property holding corporation)
- Always consult treaty before assuming s.116 applies

---

### 17.2 Canadian Acquiring Foreign Target

When a Canadian corporation acquires a non-resident corporation, the key considerations:

**FAPI (Foreign Accrual Property Income) — ITA s.91:**
If the acquired foreign company earns "passive income" (dividends, interest, rents, royalties), that income is taxed in Canada CURRENTLY (not deferred) at the controlling CCPC's full corporate rate.

```
FAPI Inclusion:
Canadian corp owns 100% of offshore sub (CFA - Controlled Foreign Affiliate)
CFA earns €200,000 interest income (passive)
Canadian corp includes €200,000 in income immediately (whether or not distributed)
Converted at spot exchange rate
FTC (Foreign Tax Credit) for foreign taxes paid by CFA
```

**Exempt Surplus vs. Taxable Surplus:**
Active business income earned by a foreign affiliate in a treaty country or listed country accumulates as "exempt surplus" — can be repatriated as a dividend to the Canadian parent with NO Canadian tax. This is the basis for offshore structuring.

```
Active business income in Ireland (treaty country):
€1,000,000 active business profit → accumulated as exempt surplus
Dividend to Canadian parent: €1,000,000 × exchange rate = CAD $1,450,000
Canadian tax: $0 (exempt surplus dividend exemption — ITA s.113(1)(a))
Irish corporate tax paid: €120,000 (12.5% rate)
```

---

### 17.3 Canada-US M&A — Treaty and FIRPTA Equivalent

**Canada-US Tax Treaty (1980, as amended) — Article XIII:**
Key provisions for business sales:

- **Shares of private company:** Capital gains taxed only in country of residence (generally)
- **Real property:** Capital gains taxed where property located (US has right to tax)
- **Business property:** Taxed where permanent establishment located
- **Principal purpose test (PPT):** Anti-treaty shopping provision added in 2022 MLI amendment — benefits denied if one principal purpose of the structure is to obtain treaty benefits

**FIRPTA Equivalent (Canada):**
Canada's s.116 clearance certificate is the functional equivalent of FIRPTA (Foreign Investment in Real Property Tax Act) — both require withholding on sale of real property interests by non-residents. Unlike FIRPTA, s.116 applies to private company shares in some circumstances (not just real property).

**US-Side Considerations:**
- IRC §897 (FIRPTA): US taxes gain on "United States real property interests" regardless of non-resident status
- IRC §1445: 15% withholding on gross price for USRPI sold by foreign person
- Limitation: Treaty may reduce or eliminate withholding — need Form 8833 to claim

---

## 18. Post-Acquisition Integration

### 18.1 Loss Utilization Planning — Section 111 Restrictions

Following a change of control (s.249(4) — deemed year end on acquisition), loss carryforwards are restricted:

**Non-capital losses (s.111(5)):**
- Can only be applied against income from the SAME BUSINESS or a similar business
- Must operate the same or similar business continuously
- "Same business" test: based on products/services, customers, technology, employees

**Net capital losses (s.111(4)):**
- Eliminated on change of control
- No carryforward available to the acquiring entity
- Strategy: TRIGGER capital gains just before change of control to absorb net capital losses

**Strategy — Crystalizing gains before change of control:**
```
Target company has:
  Net capital losses: $500,000 (will be eliminated on acquisition)
  Unrealized capital gains in portfolio: $600,000

Action before closing:
  Sell the appreciated portfolio assets → crystallize $600,000 gain
  Apply $500,000 NCL → net gain = $100,000
  Tax on $100,000 gain: ~$26,500 (corporate rate)

  Without this strategy:
  NCL eliminated, gain crystallized later = $159,000 tax on $600,000 gain

  Savings: $132,500
```

---

### 18.2 RDTOH Integration

After acquiring a target corporation, the acquirer inherits RDTOH balances:
- Eligible RDTOH (ERDTOH): refundable at $30.67 per $100 of non-eligible dividends paid
- Non-eligible RDTOH: refundable at $38.33 per $100 of eligible dividends paid

**Integration strategy:**
The acquiring group should coordinate dividend declarations across all entities to maximize RDTOH refunds. This requires tracking which entity holds ERDTOH vs. RDTOH and which dividends are eligible vs. non-eligible.

**Connection amounts:** When a corporation receives a dividend from a "connected corporation," certain RDTOH transfers between them. Understand the connected corporation rules (s.186) to manage RDTOH across a corporate group.

---

### 18.3 SR&ED Eligibility Post-Acquisition

Acquiring a company with active SRED programs brings risks and opportunities:

**Risk — Prior claim sustainability:**
CRA has 3 years to audit SR&ED claims (longer if misrepresentation). Due diligence must confirm prior claims are defensible.

**Opportunity — New research after acquisition:**
The acquiring entity can continue SR&ED if:
- Experimental development / basic research continues
- Claim is for work performed AFTER closing date
- The acquirer pays for the research (not predecessor)

**SR&ED continuity on wind-up / amalgamation:**
If subsidiary is amalgamated into parent, SR&ED expenditure pools carry forward (s.87). If wound up, SRED pools also carry to parent (s.88). Continuing SR&ED activities must be documented carefully to maintain claim eligibility.

---

## PART III: CORPORATE RESTRUCTURING

---

## 19. Corporate Reorganizations

### 19.1 Butterfly Transactions — Tax-Free Corporate Division

A butterfly is a corporate reorganization that splits one corporation into two tax-free. It is the opposite of an amalgamation — dividing one company into separate entities for business or estate planning purposes.

**Legislative authority:** ITA s.55(3)(b) — the "butterfly" exception to the s.55(2) anti-avoidance rule.

**Why a butterfly:**
- Two shareholders want to go their separate ways
- Business lines with different risk profiles need separation
- Pre-sale cleanup: separate active business from passive assets before sale
- Estate planning: split assets among siblings

**The butterfly — four components:**
```
Step 1: Pro-rata distribution
  Target Corp pays a special dividend to each shareholder proportional to their interest
  Shares must be "distribution shares" — special class created for the butterfly

Step 2: Capital reorganization
  Shareholders exchange distribution shares for shares of new Transferee Corps

Step 3: Asset transfer
  Target Corp transfers assets proportionally to Transferee Corps
  via s.85 rollover (or at FMV — paid for with shares of Transferee Corp)

Step 4: Redemption
  Target Corp redeems the distribution shares held by Transferee Corps
  using the transferred assets
```

**CRITICAL conditions for butterfly to work (s.55(3)(b)):**
1. The distribution must be pro-rata (each shareholder receives assets proportional to their interest)
2. No undue concentration of business assets (cannot give all active business to one shareholder and all passive assets to another — this triggers s.55(2))
3. No acquisition of control of either resulting corporation within 3 years post-butterfly
4. No butterfly if one of the purposes is to avoid Part IV tax

**Butterfly example:**
```
Target Corp — 50/50 owned by CC and Partner
Assets:
  Active SaaS business: $2,000,000
  Investment portfolio: $1,000,000
  Total: $3,000,000

Butterfly creates:
  CC's Corp: $1,000,000 SaaS + $500,000 portfolio (50% of each)
  Partner's Corp: $1,000,000 SaaS + $500,000 portfolio (50% of each)

Note: CANNOT give all SaaS to CC and all investments to Partner — that would fail the pro-rata rule
Unless both shareholders agree the split itself is at arm's length
```

---

### 19.2 Surplus Stripping — Section 84.1

**The problem:** A shareholder wants to extract corporate surplus at capital gains rates (50% inclusion) rather than dividend rates (up to 47.74% effective rate in Ontario). The natural temptation: sell shares to a new corporation for cash — triggering a capital gain. CRA blocks this via s.84.1.

**Section 84.1 — Anti-Avoidance:**
When an individual (or a person not dealing at arm's length) disposes of shares of a Canadian corporation to another corporation that is not at arm's length, s.84.1 deems the amount received to be a dividend to the extent it exceeds:
- The paid-up capital (PUC) of the shares transferred, AND
- The adjusted cost base (ACB) of the shares (to the extent ACB > PUC)

**In plain language:** You cannot manufacture a capital gain by selling your corporation to a new company you control. The excess over PUC is recharacterized as a dividend.

**Safe harbour planning around s.84.1:**
- Legitimate business reasons must support the reorganization
- Pipeline planning (discussed below) provides legal tax deferral without surplus stripping
- LCGE claims reduce/eliminate tax on QSBC share sales (LCGE not affected by s.84.1 if QSBC conditions met independently)

---

### 19.3 Pipeline Planning Post-Death

Pipeline planning is a commonly used post-mortem strategy to avoid double taxation on death when a shareholder's estate holds shares of a private corporation.

**The double-tax problem:**
```
CC dies holding shares of OASIS Inc.
FMV of shares: $2,000,000
ACB: $50,000

Step 1 — Deemed disposition at death (s.70(5)):
Capital gain: $2,000,000 - $50,000 = $1,950,000
Taxable gain (50%): $975,000
Tax at ~53% top rate: ~$516,750 ← First tax

Step 2 — Distributing corporate assets to estate:
Distributing $2M cash from OASIS Inc. to CC's estate:
Deemed dividend (s.84(2)): $2,000,000 - PUC ($50,000) = $1,950,000
Tax on $1.95M dividend: ~$930,000 ← Second tax

Total double-tax without planning: ~$1,447,000 !!
```

**Pipeline solution:**
```
Step 1: Estate acquires new corporation (NewCo) via s.85 rollover
  Estate transfers OASIS shares to NewCo at ACB = FMV (triggered at death)
  ACB at death = $2,000,000 (step-up from deemed disposition)
  Election: $2,000,000 (at FMV)
  NewCo issues $2,000,000 of shares

Step 2: OASIS paid a promissory note of $2M to NewCo
  (intercompany reorganization; OASIS owes NewCo $2M)

Step 3: Over time (CRA requires 1-3 years), OASIS repays the note
  $2M flows from OASIS to NewCo as DEBT REPAYMENT — not a dividend

Step 4: NewCo distributes $2M to estate as return of capital
  No dividend; return of PUC = tax-free

Result:
  Total tax: ~$516,750 (only the deemed disposition at death)
  Savings vs. no planning: ~$930,000

  Note: CRA requires the pipeline to be bona fide and take real time.
  Too-quick repayment may be challenged under GAAR.
```

---

### 19.4 Capital Reorganizations — General

Beyond estate freezes and butterflies, other common capital reorganizations:

**Share reclassification:**
- Converting common shares to preferred shares (with shareholder approval)
- Must satisfy s.86 conditions for tax deferral
- Used for: income splitting, freeze, estate planning

**Paid-up capital reduction:**
- Return capital to shareholders without triggering a dividend
- Amount returned up to PUC of shares → tax-free (return of capital, s.84)
- Amount returned in excess of PUC → deemed dividend (s.84(3))

**Share consolidation / split:**
- No immediate tax consequence (ACB of each share adjusts proportionally)
- Used for: cleanup before public offering, share structure simplification

---

## 20. Distressed Situations

### 20.1 Debt Forgiveness Rules — Section 80

When a debtor is forgiven commercial debt, the forgiven amount is generally treated as income. The s.80 rules determine how forgiven debt reduces tax attributes (not directly taxed as income in most cases).

**Order of attribute reduction (s.80(3)-(12)):**
Forgiven debt reduces the debtor's tax attributes in this mandatory order:
1. Losses of the forgiveness year and prior years (applied on a $1-for-$1 basis for income losses; 50¢/$ for capital losses)
2. Non-capital losses (s.80(3)) — each $1 of forgiven debt reduces NCL by $1
3. Net capital losses (s.80(4))
4. UCC of depreciable property (s.80(5)) — each $1 reduces UCC
5. ACB of capital property (s.80(6))
6. Capital expenditures / resource pools
7. After all attributes exhausted: 50% of remaining forgiven amount is included in income (s.80(12))

**Example:**
```
Debtor has:
  Commercial debt forgiven: $1,000,000
  NCL carryforward: $400,000
  Net capital losses: $200,000
  Total attributes: $600,000

Application:
  Forgiven $1M reduces NCL: $400,000 → NCL reduced to $0
  Remaining $600,000 reduces NCL: wait, use in order:
  Reduce net capital losses: $200,000 → reduced to $0
  Remaining forgiveness: $400,000 (no more attributes)

  Income inclusion: 50% × $400,000 = $200,000 included in income
  Tax at 26.5%: $53,000
```

---

### 20.2 Debt Parking — Section 80.01

Debt parking occurs when a creditor transfers a commercial debt obligation to a person with whom the debtor does not deal at arm's length, at a price below the principal amount of the debt.

The effect: the debt is "parked" rather than forgiven, avoiding the s.80 income inclusion rules — but CRA's s.80.01 treats the debt as forgiven when it is parked below ACB.

**Practical implication:** In distressed M&A, if an acquirer buys the target's debt at a discount and plans to forgive or restructure it post-acquisition, s.80.01 may trigger s.80 consequences on the discount. Get tax advice before executing distressed debt acquisitions.

---

### 20.3 Director Liability — Section 227.1

Directors of a corporation are personally liable for UNREMITTED source deductions (payroll taxes, CPP, EI, HST) if the corporation fails to remit.

**Conditions for liability:**
- Corporation has failed to deduct/withhold/remit
- Director exercised the degree of care a "reasonably prudent person" would exercise (due diligence defence fails)
- CRA must: (a) obtain a judgment against corporation, (b) issue writ of execution returned unsatisfied, OR (c) corporation has begun insolvency proceedings

**Two-year limitation:** CRA has 2 years from the date a director ceases to be a director to assess personal liability.

**Due diligence defence (s.227.1(3)):**
A director is NOT liable if they exercised the degree of care, diligence, and skill that a reasonably prudent person would exercise in comparable circumstances. Courts have held this requires:
- Proactive steps to ensure remittances were made
- Challenging inappropriate decisions of management
- Resignation if unable to ensure compliance

**In M&A context:**
Before accepting directorship of an acquired company:
1. Conduct thorough TDD on payroll compliance (see Section 15)
2. Obtain representations and warranties about payroll compliance
3. Check WSIB/EHT compliance (Ontario workers' compensation and employer health tax)
4. Insist on indemnification from seller for pre-closing payroll arrears

---

### 20.4 CCAA and BIA — Tax Attribute Implications

**Companies' Creditors Arrangement Act (CCAA):**
Used for large corporate restructurings (>$5M debt). Key tax implications:
- CCAA protection does NOT prevent CRA from assessing outstanding tax
- Tax claims arising before the proceedings: subject to creditor priority rules
- Tax claims for post-filing periods: priority treatment (super-priority in some cases)
- Court may approve a "compromise" of tax debt — but CRA is typically last to agree

**Bankruptcy and Insolvency Act (BIA):**
CRA is an unsecured creditor for most tax claims under BIA. However:
- Source deductions (employee payroll deductions NOT remitted) are deemed trust property — super-priority over secured creditors
- HST collected but not remitted — same super-priority
- Pre-bankruptcy filing of tax returns is required (ss.100-107 BIA) with CRA receiving proof of claim

**Tax attribute survival after CCAA plan:**
- The plan of arrangement or compromise may reduce debt
- s.80 debt forgiveness rules apply to debt reduced/forgiven under CCAA plan
- Tax attributes (losses, CCA pools) survive the reorganization — this is a key asset in restructuring

---

## APPENDIX A: VALUATION QUICK REFERENCE TABLES

### Valuation Methodology Selection Guide

| Business Type | Primary Method | Secondary Method | Notes |
|---|---|---|---|
| SaaS / subscription | EV/ARR, DCF | Precedent transactions | Use Rule of 40 to select multiple |
| Professional services | Capitalized earnings | DCF | Heavy normalization required |
| Manufacturing / industrial | EV/EBITDA comps | Asset + goodwill | CCA step-up drives asset deal preference |
| Real estate holding co | NAV | Capitalized NOI | Look-through to underlying properties |
| Early-stage startup | DCF (long horizon) | VC method | Very high discount rates (35%+) |
| Distressed business | Liquidation value | Going concern DCF | Compare both; use higher |
| Financial institution | P/Book, P/E | Dividend discount | EBITDA irrelevant; use earnings-based |

### Discount Rate Quick Reference (Canada, 2025-2026)

| Stage | Revenue | WACC Range |
|---|---|---|
| Pre-revenue | $0 | 40% - 60%+ |
| Early stage | <$500K | 25% - 40% |
| Growth | $500K - $5M | 18% - 28% |
| Established SMB | $5M - $25M | 14% - 20% |
| Mid-market | $25M - $100M | 11% - 16% |
| Large private | >$100M | 9% - 13% |

### Key Valuation Discounts Reference

| Discount Type | Range | Basis |
|---|---|---|
| Minority discount | 15% - 35% | Derived from control premium |
| DLOM (1-3 year hold) | 15% - 25% | Restricted stock studies |
| DLOM (3-5 year hold) | 25% - 35% | Pre-IPO studies |
| Key person | 5% - 20% | Risk of dependency |
| Control premium | 20% - 45% | M&A database averages |

---

## APPENDIX B: M&A CHECKLIST (SELLER'S PERSPECTIVE)

### 24+ Months Before Desired Exit

- [ ] Assess QSBC eligibility — run 90% active asset test
- [ ] Begin 24-month clock (if not already running) — ensure shares have been held ≥ 24 months
- [ ] Purify any excess passive assets (dividends to HoldCo within safe income limits)
- [ ] Implement family trust if LCGE multiplication desired (NOTE: trust must be set up well before exit)
- [ ] Maximize SR&ED claims — increases earnings and creates acquirer tax asset
- [ ] Document all IP ownership formally (assignment agreements from all contributors)
- [ ] Begin maintaining audited or reviewed financial statements (buyers require 3 years)
- [ ] Clean up related party transactions — establish arm's length equivalents
- [ ] Review shareholder agreement — ensure no right of first refusal or drag-along issues
- [ ] Eliminate/resolve CRA disputes, objections, or open assessments

### 12 Months Before Exit

- [ ] Retain an independent CBV valuator for a formal valuation opinion
- [ ] Engage M&A advisor or investment banker (process management, buyer outreach)
- [ ] Build an electronic data room (financial, legal, IP, customer, employee files)
- [ ] Prepare a Confidential Information Memorandum (CIM)
- [ ] Model asset deal vs. share deal tax outcomes with current numbers
- [ ] Confirm LCGE availability with tax counsel — obtain written advice
- [ ] Assess whether earn-out structure would maximize total consideration

### During the Deal

- [ ] Request s.116 clearance certificate if non-resident buyer involved
- [ ] Negotiate PPA carefully in asset deal scenarios
- [ ] Ensure representation and warranty insurance is available
- [ ] Confirm CDA balance — plan capital dividend before closing if CDA is significant
- [ ] Extract any remaining RDTOH via appropriate dividends pre-closing
- [ ] File T2057 (s.85 joint election) for any rollover transactions
- [ ] Conduct anti-TOSI review on any trust distributions of capital gains

---

## APPENDIX C: ATLAS DECISION FRAMEWORK

### Which Tax Structure to Use — Decision Tree

```
TRANSACTION TYPE?
│
├─ Incorporating a sole proprietorship
│   → Section 85 rollover (T2057)
│   → Transfer all business assets at elected amount = ACB
│   → Receive: preferred shares + note = FMV of assets
│
├─ Freezing the value of shares I already hold
│   → Section 86 share exchange
│   → Exchange ALL common shares for freeze preferreds + nominal new common
│   → Issue new common to family trust for future growth
│
├─ Merging two corporations
│   → Amalgamation (s.87) if both entities equally owned
│   → Wind-up (s.88) if parent owns ≥ 90% of subsidiary
│   → Check: bump rules available? Tax attributes to preserve?
│
├─ Selling the business
│   → Share deal preferred (LCGE, capital gains treatment)
│   → Purify first (ensure QSBC-qualified)
│   → Negotiate: buyer wants asset deal → offer tax indemnity instead
│   → Consider hybrid: clean OpCo share deal, retain IP in HoldCo
│
├─ Splitting a corporation between partners
│   → Butterfly transaction (s.55(3)(b))
│   → MUST be pro-rata
│   → Obtain tax counsel — butterfly is one of the most complex transactions in the ITA
│
└─ Distressed / insolvent situation
    → Debt forgiveness: model s.80 attribute reduction order
    → Director liability: resign if cannot ensure compliance
    → Pipeline planning: available even post-death restructuring
```

---

## APPENDIX D: KEY ITA SECTIONS REFERENCE MAP

| ITA Section | Topic | Key Rule |
|---|---|---|
| s.69 | Non-arm's length transfers | Proceeds deemed at FMV |
| s.70(5) | Deemed disposition on death | FMV at date of death |
| s.80 | Debt forgiveness | Attribute reduction in mandatory order |
| s.80.01 | Debt parking | Parked debt treated as forgiven |
| s.84(2) | Deemed dividend on wind-up | Distributions in excess of PUC |
| s.84.1 | Anti-surplus stripping | Non-arm's length share sales to related corp |
| s.85(1) | Rollover to corporation | Elected amount between floor and ceiling |
| s.85(2) | Partnership rollover | Same as s.85(1) for partnership property |
| s.86 | Share exchange | All shares of a class exchanged |
| s.87 | Amalgamation | Tax attribute carryover; bump rules |
| s.88(1) | Subsidiary wind-up | Bump on non-depreciable capital property |
| s.88(2) | General dissolution | FMV deemed disposition; CDA must be extracted |
| s.91 | FAPI | Foreign passive income taxed currently in Canada |
| s.110.6 | LCGE | $1.25M exemption on QSBC shares |
| s.111 | Loss carryforwards | Change of control restrictions on NCL/NCapL |
| s.113(1) | Exempt surplus dividends | Tax-free repatriation from foreign affiliates |
| s.116 | Non-resident clearance | 25% withholding on TCP sold by non-resident |
| s.120.4 | TOSI | Split income — top rate on related party allocations |
| s.163(2) | Gross negligence penalty | 50% of understated tax |
| s.227.1 | Director liability | Personal liability for unremitted source deductions |
| s.247 | Transfer pricing | Arm's length standard; 10% documentation penalty |
| s.249(4) | Deemed year end | On acquisition of control |
| s.251.2 | Loss restriction event | Triggers on acquisition of control |

---

## KEY PROFESSIONAL REFERENCES

### Canadian Professional Standards

**Chartered Business Valuator (CBV):**
- Designation: CICBV (Canadian Institute of Chartered Business Valuators) — cicbv.ca
- Engagement types: (1) Calculation engagement, (2) Estimate engagement, (3) Comprehensive valuation report
- CBV report required for: CRA disputes, estate planning, shareholder disputes, significant M&A
- Always retain a CBV for any transaction where CRA scrutiny is possible

**Key CRA Documents:**
- IC 89-3: Policy Statement on Business Equity Valuations
- IT-416R3: Valuation of Shares of a Corporation Receiving Passive Income
- IC 76-19R3: Transfer of Property to a Corporation Under Section 85
- IT-474R2: Amalgamations of Canadian Corporations
- IT-149R4: Winding-Up Dividend
- Interpretation Bulletin IT-291R3: Transfer of Property to a Corporation Under Subsection 85(1)

### Academic and Practitioner References

1. **McKinsey & Company** — *Valuation: Measuring and Managing the Value of Companies* (7th ed., 2020, Koller/Goedhart/Wessels) — Wiley Finance
2. **Aswath Damodaran** — *Investment Valuation* (3rd ed., 2012) — Wiley; damodaran.com for current datasets
3. **Joshua Rosenbaum & Joshua Pearl** — *Investment Banking* (3rd ed., 2020) — Wiley Finance
4. **Shannon Pratt & Alina Niculita** — *Valuing a Business* (6th ed., 2008) — McGraw-Hill
5. **Shannon Pratt** — *Business Valuation Discounts and Premiums* (2nd ed., 2009) — Wiley
6. **Kroll (formerly Duff & Phelps)** — *Valuation Handbook: U.S. Guide to Cost of Capital* (annual) — size premium data
7. **CCH Canadian Tax Reporter** — Wolters Kluwer — comprehensive ITA annotation and case summaries
8. **Wolters Kluwer** — *Tax Planning Guide* (annual) — practical Canadian tax planning for professionals
9. **Blake, Cassels & Graydon** — *Canadian M&A Guide* — leading Canadian M&A firm publications
10. **Stikeman Elliott** — *Tax Aspects of Canadian Business Acquisitions* — Canadian M&A tax bible

### Case Law Reference

| Case | Citation | Principle |
|---|---|---|
| Henderson Estate v. MNR | 73 DTC 5471 | FMV definition — the definitive Canadian case |
| Mandelbaum v. Commissioner | T.C. Memo 1995-255 | 9-factor DLOM analysis |
| Interpretation of "active business" | Multiple TCC cases | What qualifies as active vs. passive |
| Antosko v. Canada | [1994] 2 SCR 312 | Tax provisions must be applied as written |
| Canada Trustco Mortgage v. Canada | 2005 SCC 54 | GAAR (s.245) — purpose and effect test |
| Copthorne Holdings v. Canada | 2011 SCC 63 | GAAR on PUC multiplication — leading case |

---

*ATLAS — CC's CFO | Document maintained in `docs/ATLAS_BUSINESS_VALUATION_MA.md`*
*For questions: consult Atlas directly. For implementation: retain a CBV and M&A tax counsel.*
*This document is for informational purposes. Tax rules change; verify current rates and thresholds annually.*
