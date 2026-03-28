# ATLAS — Financial Statements, Accounting Fundamentals & CFO-Level Financial Analysis

> The language of money. Every business decision reduces to numbers on one of three statements.
> If you cannot read financial statements, you are flying blind.
> This document is the definitive reference for understanding, generating, and analyzing
> the financial reporting that drives every business from solo freelancer to public company.
> Atlas is CC's CFO. This is the operating manual for financial literacy.

**Applicability:** Universal (any business owner, any jurisdiction) | **Canadian-specific:** Flagged with `[CAN]` | **SaaS-specific:** Flagged with `[SAAS]`
**Last Updated:** 2026-03-27

**Tags used throughout:**
- `[NOW]` -- Actionable today for a sole proprietor or small business
- `[FUTURE]` -- Relevant at scale, incorporation, or institutional fundraising
- `[CAN]` -- Canada-specific (CRA, ITA, ASPE, IFRS as adopted in Canada)
- `[SAAS]` -- SaaS/subscription business specific
- `[TEMPLATE]` -- Reusable template or checklist

---

## Table of Contents

1. [The Three Financial Statements](#1-the-three-financial-statements)
2. [Income Statement Deep Dive](#2-income-statement-deep-dive)
3. [Balance Sheet Deep Dive](#3-balance-sheet-deep-dive)
4. [Cash Flow Statement Deep Dive](#4-cash-flow-statement-deep-dive)
5. [Key Financial Ratios -- The CFO's Toolkit](#5-key-financial-ratios--the-cfos-toolkit)
6. [Accrual vs Cash Accounting](#6-accrual-vs-cash-accounting)
7. [Chart of Accounts for Business Owners](#7-chart-of-accounts-for-business-owners)
8. [Bookkeeping Systems and Automation](#8-bookkeeping-systems-and-automation)
9. [Tax Accounting vs Financial Accounting](#9-tax-accounting-vs-financial-accounting)
10. [Management Accounting -- Internal Decision-Making](#10-management-accounting--internal-decision-making)
11. [Audit, Compliance, and Financial Controls](#11-audit-compliance-and-financial-controls)
12. [Financial Reporting for Stakeholders](#12-financial-reporting-for-stakeholders)
13. [Appendix A -- Templates and Checklists](#appendix-a--templates-and-checklists)
14. [Appendix B -- Glossary of Financial Terms](#appendix-b--glossary-of-financial-terms)

---

## 1. The Three Financial Statements

Every business in the world -- from a hot dog cart to Apple -- communicates its financial reality through three documents. They are the income statement, the balance sheet, and the cash flow statement. Together, they tell the complete story: how much you earned, what you own and owe, and where the cash actually went.

### 1.1 The Income Statement (Profit & Loss / P&L)

**Question it answers:** "Did we make money over this period?"

The income statement measures performance over a period of time (month, quarter, year). It is a movie, not a photograph.

```
  Revenue (Sales)
- Cost of Goods Sold (COGS)
= GROSS PROFIT
- Operating Expenses (Opex)
= EBITDA (Earnings Before Interest, Taxes, Depreciation & Amortization)
- Depreciation & Amortization (D&A)
= EBIT (Earnings Before Interest & Taxes) / Operating Income
- Interest Expense
= EBT (Earnings Before Tax)
- Income Tax
= NET INCOME (Bottom Line)
```

**Example:**

```
OASIS AI Solutions — Income Statement (Year Ended Dec 31, 2026)
---------------------------------------------------------------
Revenue                                         $120,000
  SaaS subscriptions            $72,000
  Consulting/dev services       $48,000
Cost of Goods Sold                               ($18,000)
  Cloud hosting (AWS/Vercel)    ($9,600)
  API costs (Anthropic/OpenAI)  ($6,000)
  Subcontractor costs           ($2,400)
                                                ---------
GROSS PROFIT                                    $102,000     (85% margin)
Operating Expenses                               ($34,200)
  Marketing & advertising       ($6,000)
  Software subscriptions        ($4,800)
  Home office                   ($3,600)
  Professional fees (CPA/legal) ($3,000)
  Equipment depreciation (CCA)  ($5,400)
  Insurance                     ($1,800)
  Travel & conferences          ($2,400)
  Meals & entertainment (50%)   ($1,200)
  Telecom/internet              ($2,400)
  Bank/payment processing fees  ($1,800)
  Miscellaneous                 ($1,800)
                                                ---------
EBITDA                                           $67,800
Depreciation & Amortization                      ($5,400)
                                                ---------
EBIT (Operating Income)                          $62,400
Interest Expense (OSAP interest)                 ($1,200)
                                                ---------
EBT (Earnings Before Tax)                        $61,200
Income Tax (estimated)                           ($11,300)
                                                ---------
NET INCOME                                       $49,900
```

### 1.2 The Balance Sheet (Statement of Financial Position)

**Question it answers:** "What do we own, what do we owe, and what is left over -- right now?"

The balance sheet is a snapshot at a single point in time. It is a photograph.

```
ASSETS = LIABILITIES + EQUITY
```

This is the fundamental accounting equation. It always balances. Always. If it does not balance, something is wrong. Every transaction in the history of accounting maintains this equation.

**Example:**

```
OASIS AI Solutions — Balance Sheet (As at Dec 31, 2026)
-------------------------------------------------------
ASSETS
  Current Assets
    Cash (RBC + Wise)                   $38,000
    Accounts Receivable                  $8,500
    Prepaid Expenses                     $2,400
    HST Input Tax Credits Receivable     $1,200
  Total Current Assets                              $50,100

  Non-Current Assets
    Computer Equipment                  $12,000
    Less: Accumulated Depreciation      ($5,400)
    DJ Equipment                         $4,000
    Less: Accumulated Depreciation      ($1,600)
  Total Non-Current Assets                           $9,000
                                                   -------
TOTAL ASSETS                                       $59,100

LIABILITIES
  Current Liabilities
    Accounts Payable                     $2,200
    HST Collected (owing to CRA)         $3,800
    Income Tax Payable                   $4,500
    Credit Card Balance                  $1,100
  Total Current Liabilities                        $11,600

  Non-Current Liabilities
    OSAP Student Loan                   $18,000
  Total Non-Current Liabilities                    $18,000
                                                   -------
TOTAL LIABILITIES                                  $29,600

EQUITY
  Owner's Capital                        $5,000
  Retained Earnings (prior years)       ($25,400)
  Current Year Net Income                $49,900
TOTAL EQUITY                                       $29,500
                                                   -------
TOTAL LIABILITIES + EQUITY                         $59,100  <-- balances
```

### 1.3 The Cash Flow Statement

**Question it answers:** "Where did the cash come from, and where did it go?"

The cash flow statement reconciles what the income statement says you earned with what actually happened to your bank account.

```
  Operating Cash Flow    (cash from running the business)
+ Investing Cash Flow    (cash from buying/selling assets)
+ Financing Cash Flow    (cash from debt and equity)
= NET CHANGE IN CASH
```

**Example:**

```
OASIS AI Solutions — Cash Flow Statement (Year Ended Dec 31, 2026)
------------------------------------------------------------------
OPERATING ACTIVITIES
  Net Income                                        $49,900
  Adjustments for non-cash items:
    Depreciation & Amortization                      $5,400
  Changes in working capital:
    Increase in Accounts Receivable                 ($3,500)
    Increase in Prepaid Expenses                      ($800)
    Increase in Accounts Payable                     $1,200
    Increase in HST Payable                          $1,400
    Increase in Income Tax Payable                   $2,100
  Net Cash from Operating Activities                $55,700

INVESTING ACTIVITIES
  Purchase of Computer Equipment                    ($4,800)
  Purchase of DJ Equipment                          ($1,200)
  Net Cash used in Investing Activities             ($6,000)

FINANCING ACTIVITIES
  OSAP Loan Repayment                              ($3,600)
  Owner Draws                                      ($24,000)
  Net Cash used in Financing Activities            ($27,600)

NET CHANGE IN CASH                                  $22,100
Cash, Beginning of Year                             $15,900
Cash, End of Year                                   $38,000
```

### 1.4 How the Three Statements Connect

This is the single most important concept in financial literacy. The three statements are not independent documents -- they are an interconnected system.

```
                    INCOME STATEMENT                BALANCE SHEET
                    ================                ==============

                    Revenue         $120,000         ASSETS
                  - COGS            ($18,000)          Cash --------+
                  - Opex            ($34,200)          AR           |
                  - D&A              ($5,400)          Equipment    |
                  - Interest         ($1,200)                       |
                  - Tax             ($11,300)        LIABILITIES    |
                    --------                           AP           |
                    Net Income ---->  $49,900           Debt        |
                         |                                          |
                         |                           EQUITY         |
                         +---> Flows to ----------> Retained       |
                                                    Earnings       |
                                                                    |
                    CASH FLOW STATEMENT                             |
                    ====================                            |
                                                                    |
                    Net Income        $49,900                       |
                  + D&A (add back)     $5,400   (non-cash charge    |
                                                 reduces income     |
                                                 but no cash left)  |
                  +/- Working Capital                               |
                    changes            $400                         |
                  - Capex             ($6,000)  (also hits Balance  |
                                                 Sheet as asset)    |
                  - Loan Repayment   ($3,600)                      |
                  - Owner Draws     ($24,000)                      |
                    --------                                        |
                    Net Change -----> $22,100 ----> Reconciles to --+
                                                    Cash on Balance
                                                    Sheet
```

**The key connections:**

1. **Net Income** from the Income Statement flows into **Retained Earnings** on the Balance Sheet
2. **Depreciation** reduces Net Income (Income Statement) but gets added back on the Cash Flow Statement because no cash left the building
3. **Capital expenditures** (buying equipment) appear on the Balance Sheet as an asset and on the Cash Flow Statement as an investing outflow -- but NOT on the Income Statement (only the depreciation portion hits P&L each year)
4. **Cash** on the Balance Sheet equals the ending balance on the Cash Flow Statement
5. **Accounts Receivable** increases on the Balance Sheet mean revenue was recognized (Income Statement) but cash was not collected (Cash Flow Statement shows a reduction)

### 1.5 Why a Profitable Company Can Go Bankrupt

This question separates people who understand accounting from people who do not.

**Profit does not equal cash.** A company can show $1M in net income and have zero dollars in the bank. How?

- **Scenario 1: Collecting too slowly.** You invoiced $500K in December. Income statement says $500K revenue. Balance sheet shows $500K in AR. Cash collected: $0. You cannot pay rent with accounts receivable.

- **Scenario 2: Inventory buildup.** Manufacturer buys $2M in raw materials (cash out). Converts to finished goods. Sells $1M worth. Income statement shows $1M COGS against the $1M sold. But $1M in inventory sits on the balance sheet. Cash spent: $2M. Cash received: maybe $800K (some customers have not paid yet).

- **Scenario 3: Debt repayment.** You owe $500K in loan principal due this month. Loan repayment is NOT an expense (it does not appear on the income statement). It is a financing cash outflow. If you do not have $500K in cash, you are in default -- regardless of profitability.

- **Scenario 4: Growth kills cash.** SaaS company growing 200% per year. Spending $3 on sales and marketing to acquire each $1 of monthly revenue. Income statement might eventually show profit from existing customers, but the cash burn to acquire new ones drains the bank. This is why fast-growing startups raise capital -- growth consumes cash.

**The rule:** Cash is oxygen. Profit is a scorecard. You can survive a bad scorecard with oxygen. You cannot survive without oxygen, regardless of the scorecard.

---

## 2. Income Statement Deep Dive

### 2.1 Revenue Recognition

Revenue recognition is the most manipulated line on the income statement. The core question: **when** do you count the money?

**The principle (universal):** Revenue is recognized when the **performance obligation** is satisfied -- meaning you have delivered the goods or rendered the service. NOT when you send the invoice. NOT when you receive payment.

**Examples:**

| Event | Revenue Recognized? | Why |
|-------|-------------------|-----|
| Client signs $24K annual contract, pays upfront | No (not yet) | Service not yet delivered |
| First month of service delivered | Yes -- $2,000 | 1/12 of annual contract earned |
| You send an invoice for completed project | Yes | Work is done, obligation satisfied |
| Client pays invoice 45 days later | No additional revenue | Already recognized on delivery |
| Client pays $5K deposit for future work | No | Deposit is deferred revenue (liability) |

`[SAAS]` **SaaS revenue recognition specifics:**
- Monthly subscriptions: recognize in the month of service
- Annual prepayments: recognize 1/12 per month; the remaining 11/12 sits as **deferred revenue** (a liability on the balance sheet)
- Setup fees: if the setup has standalone value, recognize on completion; if not, spread over the contract term
- Professional services (custom development): recognize on delivery or by percentage-of-completion for long projects
- Usage-based pricing (API calls, seats): recognize as usage occurs

`[CAN]` **Canadian rules:**
- **ASPE 3400** (private companies): Revenue recognized when risks and rewards transferred, measurable, collectible
- **IFRS 15** (public companies, optional for private): Five-step model -- identify contract, identify performance obligations, determine price, allocate price, recognize when satisfied
- **Sole proprietors:** CRA follows accrual principles per s.9(1) ITA. You must include amounts receivable, not just cash received. However, the s.20(1)(m) reserve allows deferral of amounts for services to be rendered after year-end.

### 2.2 COGS vs Operating Expenses

This distinction determines your **gross margin**, which is the most important profitability metric for product businesses.

**Cost of Goods Sold (COGS):** Costs directly attributable to producing the product or delivering the service. These costs scale with revenue -- if you sell nothing, COGS is zero.

| Business Type | COGS Examples |
|--------------|---------------|
| SaaS | Cloud hosting, API costs, payment processing fees, CDN, customer support directly on product |
| Consulting | Subcontractor costs, project-specific tools/licenses |
| E-commerce | Product cost, shipping, packaging, marketplace fees |
| Manufacturing | Raw materials, factory labor, factory overhead |

**Operating Expenses (Opex):** Costs of running the business regardless of sales volume. You pay these even if revenue is zero.

| Category | Examples |
|----------|----------|
| Sales & Marketing | Ads, content creation, trade shows, sales team salaries |
| General & Administrative | Rent, insurance, legal, accounting, office supplies, software |
| Research & Development | Developer salaries (not capitalized), prototyping, testing |

**The dividing line:** If the cost exists because you served a customer, it is COGS. If the cost exists because you operate a business, it is Opex. Grey areas abound. Be consistent.

### 2.3 Margins -- What Each Reveals

```
                Revenue                     $120,000    (100%)
                - COGS                      ($18,000)
                                            --------
GROSS MARGIN =  Gross Profit / Revenue  =   $102,000    (85%)

                - Opex                      ($34,200)
                                            --------
OPERATING       EBIT / Revenue          =    $67,800    (56.5%)
MARGIN
                - Interest, Tax             ($12,500)
                                            --------
NET MARGIN  =   Net Income / Revenue    =    $49,900    (41.6%)
```

| Metric | What It Reveals | Benchmark |
|--------|----------------|-----------|
| **Gross Margin** | Efficiency of your core product/service delivery. How much of each dollar of revenue is left after direct costs. | SaaS: 70-85%. Consulting: 50-70%. E-commerce: 30-50%. Manufacturing: 25-40%. |
| **Operating Margin** | Efficiency of the whole business operation. Can you run the business profitably? | SaaS (mature): 20-30%. Consulting: 15-25%. S&P 500 median: ~15%. |
| **Net Margin** | What the owner/shareholders actually keep after everything. | Varies wildly. 10-20% is healthy for most SMBs. Tech can be 25%+. |
| **EBITDA Margin** | Cash-like operating profitability before capital structure and tax effects. | SaaS: 25-40%. Consulting: 20-30%. Used for valuation and debt covenants. |

### 2.4 EBITDA -- The Most Loved and Most Abused Metric

EBITDA = Earnings Before Interest, Taxes, Depreciation, and Amortization.

**Why investors love it:**
- Strips out capital structure (interest) -- so you can compare a debt-free company with a leveraged one
- Strips out tax jurisdiction -- so you can compare a Canadian company with an Irish one
- Strips out non-cash accounting charges (D&A) -- focuses on operating cash generation
- Proxy for operating cash flow (imperfect but fast)
- Standard basis for valuation multiples (EV/EBITDA)

**Why it can be misleading:**
- Ignores capex entirely. A factory that spends $50M/year on equipment maintenance shows the same EBITDA as a software company that spends $0. But the factory must keep spending or it dies.
- Ignores working capital needs. A company with $10M in uncollected receivables shows great EBITDA but may have a cash crisis.
- Ignores stock-based compensation. Tech companies pay employees in stock, which is a real cost but excluded from "adjusted EBITDA."
- Can be "adjusted" into fantasy. Companies add back restructuring charges, litigation, one-time costs (that happen every year), until the number is meaningless.

**Charlie Munger's verdict:** "Every time you see EBITDA, replace it with 'bullshit earnings.'"

**The fix:** Always look at EBITDA together with Free Cash Flow and capex. If EBITDA is $10M but FCF is $2M, the $8M gap is real spending the company must do to stay alive.

### 2.5 T2125 as an Income Statement

`[CAN]` For Canadian sole proprietors, the T2125 (Statement of Business or Professional Activities) IS your income statement for tax purposes. It maps directly:

| T2125 Line | Income Statement Equivalent |
|------------|----------------------------|
| Line 8000-8230 (Part 3) | Revenue by type |
| Line 8518-8521 | Cost of Goods Sold |
| Line 8521 result | Gross Profit |
| Lines 8590-8760 (Part 4) | Operating Expenses |
| Line 9369 | Net Income (before adjustments) |
| Part 6: CCA | Depreciation (different calculation) |
| Part 7: Home Office | Additional deduction |
| Line 9946 | Net Business Income (flows to T1 Line 13500) |

### 2.6 Multi-Entity: Consolidated vs Standalone

`[FUTURE]` When you have multiple entities (e.g., OpCo + HoldCo, or a Canadian parent with a US subsidiary):

- **Standalone P&L:** Each entity's own income statement. Required for each entity's tax filing.
- **Consolidated P&L:** Combines all entities as if they were one. Eliminates inter-company transactions (if OpCo pays HoldCo $50K in management fees, that revenue and expense cancel out on consolidation).
- **Elimination entries:** The key difference. Revenue between related entities gets eliminated. Only revenue from external third parties survives consolidation.

---

## 3. Balance Sheet Deep Dive

### 3.1 Current Assets (Convert to Cash Within 12 Months)

| Account | Description | Key Considerations |
|---------|-------------|-------------------|
| **Cash & Equivalents** | Bank balances, money market, GICs < 90 days | The most liquid asset. Your survival metric. |
| **Accounts Receivable (AR)** | Money clients owe you for delivered work | Not all AR is collectible. Allowance for doubtful accounts reduces AR on the balance sheet. DSO (Days Sales Outstanding) measures how fast you collect. |
| **Inventory** | Goods held for sale (physical products) | Not applicable to pure SaaS/consulting. Valued at lower of cost or net realizable value. |
| **Prepaid Expenses** | Payments for future services (annual software, insurance) | Cash is gone, but you have not consumed the service yet. Expense is recognized over the service period. |
| **Short-term Investments** | T-bills, GICs, marketable securities | Liquid reserves beyond operating cash. |

`[SAAS]` **SaaS current assets are simple:** mostly cash + AR. No inventory, minimal prepaid. This is one reason SaaS businesses are valued highly -- asset-light model.

### 3.2 Non-Current Assets (Long-Lived, > 12 Months)

| Account | Description | Key Considerations |
|---------|-------------|-------------------|
| **Property, Plant & Equipment (PP&E)** | Land, buildings, computers, furniture, vehicles | Recorded at cost. Depreciated over useful life (straight-line, declining balance, etc.). On the balance sheet at cost minus accumulated depreciation (net book value). |
| **Intangible Assets** | Patents, trademarks, software, customer lists | If purchased: recorded at cost, amortized. If internally developed: usually expensed (ASPE) or capitalized under IAS 38 (IFRS) if criteria are met. |
| **Goodwill** | Premium paid in an acquisition above fair value of net assets | Only arises from acquisitions. Tested for impairment annually (not amortized under IFRS; amortized under ASPE over max 40 years). |
| **Right-of-Use Assets** | Leased assets under IFRS 16 / ASC 842 | Operating leases now appear on the balance sheet. A corresponding lease liability is recorded. |
| **Investments** | Equity in subsidiaries, associate companies, long-term holdings | Recorded at cost, equity method, or fair value depending on level of ownership and accounting standard. |

`[CAN]` **Capital Cost Allowance (CCA)** is the tax version of depreciation. CCA classes and rates are prescribed by regulation (Class 50 for computers at 55%, Class 8 for furniture at 20%, etc.). CCA is claimed on the tax return, not necessarily in the financial statements.

### 3.3 Current Liabilities (Due Within 12 Months)

| Account | Description | Key Considerations |
|---------|-------------|-------------------|
| **Accounts Payable (AP)** | Bills you owe to suppliers | Pay on time or lose vendor relationships and credit terms. DPO (Days Payable Outstanding) measures how long you take to pay. |
| **Deferred Revenue** (current portion) | Cash received for services not yet delivered | This is the most counterintuitive concept for beginners: receiving cash creates a LIABILITY. You owe the customer service. As you deliver, the liability converts to revenue. |
| **Accrued Expenses** | Expenses incurred but not yet billed/paid (salaries, utilities, interest) | The matching principle: expense recognized when incurred, not when paid. |
| **Current Portion of Long-Term Debt** | Principal payments on loans due within 12 months | Reclassified from long-term to current as payments come due. |
| **HST/GST Payable** | Sales tax collected, owed to CRA | `[CAN]` This is NOT your money. It is a trust obligation. Segregate it. |
| **Income Tax Payable** | Estimated tax owed for the current year | `[CAN]` Quarterly installments reduce this. Remainder due April 30 (individuals) or 2-3 months after fiscal year-end (corporations). |

`[SAAS]` **Deferred revenue is the signature SaaS liability.** A SaaS company billing annually will have large deferred revenue. This is actually a sign of strength -- customers have prepaid. As long as the company delivers the service, this liability converts to revenue month by month.

### 3.4 Non-Current Liabilities (Due After 12 Months)

| Account | Description |
|---------|-------------|
| **Long-Term Debt** | Bank loans, term loans, bonds (portion due after 12 months) |
| **Lease Obligations** | Long-term portion of lease liabilities (IFRS 16 / ASC 842) |
| **Deferred Tax Liabilities** | Tax owed in the future due to timing differences between accounting and tax |
| **Shareholder Loans** | `[CAN]` Loans from owner to the corporation -- treated as a liability of the corp |

### 3.5 Equity (What the Owners Own After All Debts Are Paid)

| Account | Description |
|---------|-------------|
| **Common Shares / Share Capital** | Amount invested by shareholders in exchange for ownership |
| **Retained Earnings** | Cumulative net income minus cumulative dividends since the company began. This is where net income accumulates over time. |
| **Owner's Capital / Draws** | `[CAN]` For sole proprietors: equity = capital contributed + cumulative earnings - cumulative draws. No shares exist. |
| **Accumulated Other Comprehensive Income (AOCI)** | Unrealized gains/losses on certain financial instruments, FX translation adjustments, pension adjustments. Bypasses the income statement. |
| **Treasury Stock** | Shares repurchased by the company. Reduces equity (contra-equity account). |

### 3.6 Working Capital -- The Lifeline

```
WORKING CAPITAL = Current Assets - Current Liabilities
```

**Example:** $50,100 - $11,600 = **$38,500** (healthy)

Working capital measures your ability to meet short-term obligations. If this number is negative, you cannot pay your bills with your current assets -- you need to borrow, sell long-term assets, or raise equity.

**Working capital cycle:**
```
Cash ---> Buy inventory/supplies ---> Deliver service/product ---> Invoice client
  ^                                                                      |
  |                                                                      v
  +----------------------- Client pays (AR collected) <-----------+
```

The faster this cycle turns, the less working capital you need. SaaS with annual prepayment has a *negative* working capital cycle (customers pay before you deliver) -- this is extremely valuable.

### 3.7 Book Value vs Market Value

**Book value** = Total Assets - Total Liabilities (= Total Equity on the balance sheet)

**Market value** = What someone would pay to buy the whole business (for public companies: share price x shares outstanding = market cap)

They are almost never equal. Why:

1. **Intangible assets not on the balance sheet.** Brand, reputation, customer relationships, talented employees, proprietary technology -- these are worth enormous amounts but largely do not appear on the balance sheet.
2. **Historical cost basis.** Assets are recorded at what you paid, not what they are worth today. A building bought for $1M in 1990 might be worth $15M today but sits on the balance sheet at $1M minus depreciation.
3. **Future earnings.** Market value reflects expected future cash flows. Book value reflects the past. A high-growth SaaS company might have $5M in book value but a $100M market value because investors expect massive future cash flows.

**Rule of thumb:**
- Book value > market value: the market thinks the company is destroying value (or assets are overstated)
- Market value >> book value: the market sees significant intangible value or growth (typical for tech/SaaS)
- Price-to-Book ratio: market value / book value. S&P 500 average is ~4x. Tech companies can be 10-50x.

---

## 4. Cash Flow Statement Deep Dive

### 4.1 Operating Cash Flow (CFO -- Cash Flow from Operations)

**Starting point:** Net income from the income statement.

**Then adjust for:**

1. **Non-cash charges (add back):**
   - Depreciation & amortization (expense that did not use cash)
   - Stock-based compensation (expense recorded but no cash paid)
   - Deferred tax expense (tax recognized but not yet paid)
   - Amortization of debt issuance costs
   - Impairment charges

2. **Working capital changes:**
   - AR increases = cash NOT collected (subtract)
   - AR decreases = cash collected from past sales (add)
   - Inventory increases = cash spent on unsold goods (subtract)
   - AP increases = bills not yet paid (add -- cash retained)
   - AP decreases = paid old bills (subtract)
   - Deferred revenue increases = cash received for future service (add)
   - Prepaid expense increases = cash paid for future benefit (subtract)

```
Operating Cash Flow Reconciliation:

  Net Income                                  $49,900
  + Depreciation & Amortization                $5,400
  - Increase in Accounts Receivable           ($3,500)   <-- earned but not collected
  - Increase in Prepaid Expenses                ($800)   <-- paid ahead
  + Increase in Accounts Payable               $1,200    <-- delayed paying suppliers
  + Increase in Tax/HST Payable                $3,500    <-- tax accrued, not yet remitted
                                              -------
  Operating Cash Flow                         $55,700
```

### 4.2 Investing Cash Flow (CFI)

Cash spent on or received from long-term assets.

**Outflows (negative):**
- Purchase of PP&E (capex)
- Purchase of intangible assets
- Acquisitions of other businesses
- Purchase of investments

**Inflows (positive):**
- Sale of PP&E
- Sale of investments
- Proceeds from business dispositions

For most small businesses, investing cash flow = capex (buying equipment, computers, etc.).

### 4.3 Financing Cash Flow (CFF)

Cash from/to capital providers (lenders and owners).

**Inflows (positive):**
- Proceeds from bank loans / lines of credit
- Proceeds from issuing equity (selling shares)
- Capital contributions from owner

**Outflows (negative):**
- Loan principal repayments (NOT interest -- interest is operating)
- Dividends paid to shareholders
- Share buybacks
- Owner draws (sole proprietor taking money out)

### 4.4 Free Cash Flow -- The Real Money

```
FREE CASH FLOW (FCF) = Operating Cash Flow - Capital Expenditures
```

**Example:** $55,700 - $6,000 = **$49,700**

FCF is the cash available to the business after maintaining and investing in its asset base. It is the cash that can be used to:
- Pay dividends
- Repay debt
- Make acquisitions
- Build cash reserves
- Return capital to owners

**Why FCF matters more than net income for valuation:**

Net income includes non-cash items (depreciation, stock comp, deferred tax) and excludes real cash outlays (capex, working capital needs). FCF measures what you can actually take out of the business.

A business is fundamentally worth the present value of all its future free cash flows. This is the basis of discounted cash flow (DCF) valuation, which is how sophisticated investors value companies.

### 4.5 SaaS Cash Flow Dynamics

`[SAAS]` SaaS companies with annual billing have a structural cash flow advantage:

1. Customer pays $12,000 upfront for an annual subscription
2. Income statement recognizes $1,000/month (deferred revenue converts to revenue)
3. Cash flow statement shows $12,000 inflow in month 1, then nothing for 11 months
4. The company has use of that $12,000 from day one

This creates **positive working capital** -- the business collects cash before recognizing revenue. High-growth SaaS companies can fund growth partially from customer prepayments.

**Billings** (a non-GAAP metric) = Revenue + Change in Deferred Revenue. This captures total cash committed by customers, regardless of recognition timing. Billings growth > revenue growth = accelerating business.

### 4.6 Cash Conversion Cycle (CCC)

```
CCC = DSO + DIO - DPO
```

| Metric | Formula | Meaning |
|--------|---------|---------|
| **DSO** (Days Sales Outstanding) | (AR / Revenue) x 365 | How fast you collect from customers |
| **DIO** (Days Inventory Outstanding) | (Inventory / COGS) x 365 | How fast you sell inventory |
| **DPO** (Days Payable Outstanding) | (AP / COGS) x 365 | How long you take to pay suppliers |

**Lower CCC = better.** Negative CCC = you collect cash before you have to pay suppliers (Amazon, Dell -- they are funded by their suppliers).

**Example for OASIS (service business, no inventory):**
- DSO = ($8,500 / $120,000) x 365 = 26 days
- DIO = 0 (no inventory)
- DPO = ($2,200 / $18,000) x 365 = 45 days
- **CCC = 26 + 0 - 45 = -19 days** (excellent -- collecting before paying)

---

## 5. Key Financial Ratios -- The CFO's Toolkit

Ratios transform raw numbers into comparable, actionable intelligence. A single number means nothing. A ratio compared to last year, last quarter, and your industry -- that is insight.

### 5.1 Profitability Ratios

| Ratio | Formula | What It Reveals | Benchmark |
|-------|---------|----------------|-----------|
| **Gross Margin** | Gross Profit / Revenue | Pricing power and production efficiency | SaaS: 70-85%. Services: 50-70%. |
| **Operating Margin** | EBIT / Revenue | Operational efficiency including overhead | SaaS mature: 20-30%. SMB: 10-20%. |
| **Net Margin** | Net Income / Revenue | Bottom-line profitability after everything | 10-20% healthy. Tech: 20-35%. |
| **EBITDA Margin** | EBITDA / Revenue | Cash-like operating profitability | SaaS: 25-40%. |
| **ROE** (Return on Equity) | Net Income / Avg Equity | Return generated on owners' investment | 15-25% excellent. >25% exceptional. |
| **ROA** (Return on Assets) | Net Income / Avg Total Assets | How efficiently assets generate profit | 5-10% good. Asset-light businesses higher. |
| **ROIC** (Return on Invested Capital) | NOPAT / Invested Capital | Return on ALL capital (debt + equity) | >15% excellent. Compare to WACC. |

**ROIC explained:** NOPAT = EBIT x (1 - tax rate). Invested Capital = Equity + Net Debt. ROIC above your cost of capital (WACC) means you are creating value. Below WACC = destroying value.

### 5.2 Liquidity Ratios

| Ratio | Formula | What It Reveals | Benchmark |
|-------|---------|----------------|-----------|
| **Current Ratio** | Current Assets / Current Liabilities | Can you pay bills due within 12 months? | 1.5-3.0 healthy. <1.0 = danger. |
| **Quick Ratio** | (Cash + AR) / Current Liabilities | Same, but excludes inventory (tighter test) | >1.0 comfortable. |
| **Cash Ratio** | Cash / Current Liabilities | Strictest test -- cash only | >0.5 conservative. |

**Warning signs:**
- Current ratio declining quarter over quarter = cash being consumed
- Quick ratio < 1.0 = cannot cover short-term obligations without selling inventory
- Cash ratio < 0.2 = one bad month could trigger a crisis

### 5.3 Efficiency Ratios

| Ratio | Formula | What It Reveals | Benchmark |
|-------|---------|----------------|-----------|
| **Asset Turnover** | Revenue / Avg Total Assets | Revenue generated per dollar of assets | Higher = more efficient. SaaS: 0.5-1.5x. |
| **Inventory Turnover** | COGS / Avg Inventory | How many times inventory is sold/replaced per year | Retail: 8-12x. Manufacturing: 4-8x. |
| **AR Turnover** | Revenue / Avg AR | How many times AR is collected per year | 10-12x typical (30-36 day collection). |
| **DSO** | 365 / AR Turnover | Average days to collect payment | <30 excellent. 30-45 normal. >60 problem. |

### 5.4 Leverage Ratios

| Ratio | Formula | What It Reveals | Benchmark |
|-------|---------|----------------|-----------|
| **Debt-to-Equity** | Total Debt / Total Equity | How much debt vs owner's money funds the business | <1.0 conservative. 1-2 moderate. >3 aggressive. |
| **Interest Coverage** | EBIT / Interest Expense | Can you afford your debt payments? | >3x comfortable. <1.5x danger. <1.0x = default risk. |
| **Debt-to-EBITDA** | Total Debt / EBITDA | Years of earnings needed to pay off all debt | <2x conservative. 3-4x moderate. >5x highly leveraged. |
| **Net Debt / EBITDA** | (Debt - Cash) / EBITDA | Adjusted for cash on hand | More accurate than gross debt ratio. |

### 5.5 Valuation Ratios

| Ratio | Formula | What It Reveals | Benchmark |
|-------|---------|----------------|-----------|
| **P/E** (Price/Earnings) | Share Price / EPS | How much investors pay per dollar of earnings | S&P 500: ~20x. Growth tech: 30-60x. |
| **P/S** (Price/Sales) | Market Cap / Revenue | Valuation relative to revenue (used for unprofitable companies) | SaaS: 5-15x. Mature: 1-3x. |
| **EV/EBITDA** | Enterprise Value / EBITDA | Most common acquisition multiple | SaaS: 15-25x. SMB: 4-8x. |
| **EV/Revenue** | Enterprise Value / Revenue | Revenue multiple for high-growth companies | SaaS growth: 10-20x. Mature: 1-4x. |
| **PEG** | P/E / Earnings Growth Rate | P/E adjusted for growth | <1.0 undervalued. 1.0 fair. >2.0 expensive. |

**Enterprise Value (EV)** = Market Cap + Total Debt - Cash. This is the total cost to acquire the business (you buy the equity AND take on the debt, but get the cash).

### 5.6 SaaS-Specific Metrics

`[SAAS]` These are the metrics that SaaS investors actually care about:

| Metric | Formula | What It Reveals | Benchmark |
|--------|---------|----------------|-----------|
| **MRR** | Monthly Recurring Revenue | Predictable revenue base | Growth rate matters more than absolute |
| **ARR** | MRR x 12 | Annualized recurring revenue | Standard SaaS top-line metric |
| **NDR** (Net Dollar Retention) | (Starting MRR + Expansion - Contraction - Churn) / Starting MRR | Do existing customers spend more or less over time? | >120% elite. >100% good. <100% leaky bucket. |
| **Gross Churn** | Lost MRR / Starting MRR (monthly) | Rate of customer revenue loss | <2% monthly good. <1% excellent. |
| **LTV** (Lifetime Value) | ARPU x Gross Margin / Monthly Churn Rate | Total profit from one customer over their lifetime | Minimum 3x CAC. |
| **CAC** (Customer Acquisition Cost) | Total S&M Spend / New Customers Acquired | Cost to acquire one customer | Payback < 18 months. |
| **LTV/CAC** | LTV / CAC | Unit economics -- is each customer profitable? | >3x good. >5x great. <1x = burning money. |
| **Magic Number** | Net New ARR / Prior Quarter S&M Spend | Efficiency of sales and marketing spend | >1.0 = invest more. 0.5-1.0 = efficient. <0.5 = fix unit economics. |
| **Burn Multiple** | Net Burn / Net New ARR | Cash burned per dollar of new ARR | <1x elite. 1-2x good. >3x = inefficient growth. |
| **Rule of 40** | Revenue Growth Rate + EBITDA Margin | Balances growth vs profitability | >40% = healthy SaaS. Best-in-class: >60%. |

**Example -- Rule of 40:**
- Company A: 50% growth, -15% EBITDA margin = 35% (below 40, needs to improve efficiency)
- Company B: 20% growth, 25% EBITDA margin = 45% (above 40, well-balanced)
- Company C: 100% growth, -70% EBITDA margin = 30% (hypergrowth but burning too fast)

---

## 6. Accrual vs Cash Accounting

### 6.1 Cash Basis Accounting

**Recognize revenue when cash arrives. Recognize expenses when cash leaves.**

```
March 15: Complete $10,000 project for client
March 31: Revenue recognized = $0 (no cash received)
April 10: Client pays $10,000
April 30: Revenue recognized = $10,000 (cash received)
```

**Advantages:**
- Simple. Match your books to your bank statements.
- Easy to understand -- what you see in the bank is what you have.
- No need to track accruals, deferred revenue, or receivables.

**Disadvantages:**
- Misleading -- a month with no collections looks like no revenue, even if you delivered $50K in services.
- Can be manipulated by timing payments around year-end.
- Does not match expenses to the revenue they generate (violates matching principle).
- Not accepted for larger businesses or corporations.

**Best for:** Solo freelancers, very small service businesses, early-stage sole proprietors.

### 6.2 Accrual Basis Accounting

**Recognize revenue when earned. Recognize expenses when incurred. Regardless of cash movement.**

```
March 15: Complete $10,000 project for client
March 31: Revenue recognized = $10,000 (earned on delivery)
           Accounts Receivable = $10,000 (balance sheet)
April 10: Client pays $10,000
           Cash up $10,000, AR down $10,000 (no P&L impact)
```

**Advantages:**
- Accurate picture of economic reality.
- Matches revenue with the expenses that generated it.
- Required for any serious financial analysis, investor reporting, or lending.
- Shows the true earning power of the business regardless of collection timing.

**Disadvantages:**
- More complex bookkeeping.
- "Profit" may exist without corresponding cash (profitable but broke problem from Section 1.5).
- Requires tracking receivables, payables, deferrals, accruals.

**Best for:** Any business beyond the smallest sole proprietorship. All corporations. Any business seeking investment, loans, or serious growth.

### 6.3 CRA Rules on Accounting Method

`[CAN]`

| Entity Type | Cash Allowed? | Accrual Required? |
|-------------|--------------|-------------------|
| Sole proprietor (revenue < $2M) | Yes | No |
| Sole proprietor (revenue > $2M) | No | Yes |
| Partnership | Depends on partners' choices | If any partner is a corporation |
| Corporation (any size) | No | Yes |
| Professional (doctor, lawyer, etc.) | Yes (special election) | Default is accrual but WIP election available |

**Transition trigger:** When you incorporate, you MUST switch to accrual. Plan for this -- it can create a one-time income spike as you recognize AR that was previously deferred under cash basis.

### 6.4 Accounting Standards -- A Map

| Standard | Who Uses It | Key Feature |
|----------|------------|-------------|
| **IFRS** (International Financial Reporting Standards) | Public companies in 140+ countries including Canada. All Canadian publicly accountable enterprises. | Principles-based. Fair value emphasis. IFRS 15 (revenue), IFRS 16 (leases). |
| **US GAAP** | US public and many private companies. | Rules-based. More prescriptive. ASC 606 (revenue), ASC 842 (leases). |
| **ASPE** (Accounting Standards for Private Enterprises) | `[CAN]` Canadian private companies (choice between ASPE and IFRS). | Simplified IFRS. Less disclosure. Goodwill amortized (not impairment-only). Popular with SMBs. |
| **Cash basis / modified cash** | Small sole proprietors, freelancers. | Not a formal standard. Acceptable for tax reporting under certain conditions. |

### 6.5 Revenue Recognition Under IFRS 15 / ASC 606

`[FUTURE]` The five-step model (same under both IFRS 15 and ASC 606):

1. **Identify the contract** -- Agreement with commercial substance, rights and obligations identifiable, payment terms, approved.
2. **Identify performance obligations** -- Distinct goods/services promised. A SaaS subscription + implementation + training = potentially three separate obligations.
3. **Determine the transaction price** -- Total consideration, adjusted for variable consideration (discounts, bonuses, penalties), significant financing components, non-cash consideration.
4. **Allocate the transaction price** -- Allocate to each performance obligation based on standalone selling price. If SaaS is $100/mo standalone and implementation is $5,000 standalone, a bundled $15,000 annual deal allocates proportionally.
5. **Recognize revenue** -- When each performance obligation is satisfied. Point in time (implementation complete) or over time (SaaS subscription delivered monthly).

### 6.6 The Matching Principle

Expenses should be recognized in the same period as the revenue they helped generate.

**Examples:**
- Sales commission on a $50K deal closed in March: expense in March (even if commission is paid in April)
- Insurance premium paid in January for the full year: expense $1/12 per month, not $12K in January
- Laptop purchased for $2,400: not a $2,400 expense today. Capitalize as an asset, depreciate over 3-5 years ($40-67/month)
- Advertising spend in Q1 that generates Q2 revenue: expense in Q1 (you cannot reliably attribute the future revenue)

---

## 7. Chart of Accounts for Business Owners

### 7.1 What It Is and Why It Matters

A chart of accounts (CoA) is the complete list of every account used to record financial transactions. It is the taxonomy of your financial data. Every transaction is classified into one of these accounts.

**Why it matters:**
- Determines the granularity of your financial reporting
- Enables accurate tax filing (accounts map to tax form lines)
- Allows meaningful comparison period over period
- Once set up properly, categorization is semi-automatic

**Numbering convention (universal standard):**

| Range | Category | Balance Sheet / P&L |
|-------|----------|-------------------|
| 1000-1999 | Assets | Balance Sheet |
| 2000-2999 | Liabilities | Balance Sheet |
| 3000-3999 | Equity | Balance Sheet |
| 4000-4999 | Revenue | Income Statement |
| 5000-5999 | Cost of Goods Sold | Income Statement |
| 6000-6999 | Operating Expenses | Income Statement |
| 7000-7999 | Other Income/Expense | Income Statement |

### 7.2 T2125-Aligned Chart of Accounts

`[CAN]` `[NOW]` This chart of accounts maps directly to CRA T2125 lines, making tax filing straightforward. See `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` for the complete OASIS-specific chart.

**Revenue (4000s):**

| Account | Name | T2125 Line |
|---------|------|-----------|
| 4000 | SaaS Subscription Revenue | 8000 |
| 4010 | Consulting / Development Revenue | 8000 |
| 4020 | DJ Performance Revenue | 8000 |
| 4030 | Subcontract Revenue | 8000 |
| 4100 | Returns & Refunds (contra) | 8000 (net) |

**COGS (5000s):**

| Account | Name | T2125 Line |
|---------|------|-----------|
| 5000 | Cloud Hosting (AWS/Vercel) | 8518-8521 |
| 5010 | API Costs (Anthropic/OpenAI) | 8518-8521 |
| 5020 | Subcontractor Costs | 8518-8521 |
| 5030 | Payment Processing Fees | 8518-8521 |

**Operating Expenses (6000s):**

| Account | Name | T2125 Line | Notes |
|---------|------|-----------|-------|
| 6000 | Advertising & Marketing | 8520 | Google Ads, social media ads |
| 6050 | Meals & Entertainment | 8523 | 50% deductible per s.67.1 |
| 6100 | Insurance | 8690 | Professional liability, E&O |
| 6150 | Professional Fees | 8860 | CPA, legal, bookkeeper |
| 6200 | Office Supplies | 8810 | Stationery, small items |
| 6250 | Software Subscriptions | 8760 | GitHub, Figma, Notion, etc. |
| 6300 | Telephone / Internet | 8220 | Business % of home plan |
| 6350 | Travel | 8520 | Client visits, conferences |
| 6400 | Vehicle (business %) | 9281 | Per-km rate or actual costs |
| 6450 | Bank Charges | 8710 | Monthly fees, wire charges |
| 6500 | Home Office Expenses | Part 7 | Rent/mortgage interest, utilities, insurance -- prorated |
| 6600 | Training / Education | 8523 | Courses, certifications |
| 6700 | CCA (Depreciation) | Part 6 | Tax depreciation on assets |

### 7.3 SaaS/Consulting Hybrid Accounts

`[SAAS]` Additional accounts for a SaaS + consulting business:

| Account | Name | Notes |
|---------|------|-------|
| 2150 | Deferred Revenue -- Short Term | Annual subscriptions, unearned portion |
| 2160 | Deferred Revenue -- Long Term | Multi-year contracts (>12 month portion) |
| 4040 | Professional Services Revenue | Implementation, custom dev (distinct from subscription) |
| 4050 | Training Revenue | Onboarding, workshops |
| 5040 | Capitalized Development Costs | Internally developed software (if capitalizing under IFRS/ASPE) |
| 1600 | Capitalized Software Development | Asset account for capitalized dev costs |
| 1610 | Accumulated Amortization -- Software | Amortize over useful life (3-5 years typical) |

### 7.4 Multi-Currency Accounts

For businesses with USD revenue (like OASIS billing US clients):

| Account | Name | Notes |
|---------|------|-------|
| 1025 | Wise Business -- USD | USD balance held |
| 4200 | Revenue -- USD (converted to CAD) | Record at spot rate on transaction date |
| 7100 | FX Gain (Realized) | Gain when USD converted to CAD at better rate than recorded |
| 7110 | FX Loss (Realized) | Loss when USD converted at worse rate |
| 7120 | FX Gain/Loss (Unrealized) | Year-end revaluation of USD balances at Dec 31 rate |

`[CAN]` CRA requires all amounts in Canadian dollars. Convert each transaction at the Bank of Canada daily rate on the transaction date. For year-end balances, use the Dec 31 rate and recognize unrealized FX gains/losses.

---

## 8. Bookkeeping Systems and Automation

### 8.1 Software Comparison for Canadian Business Owners

| Feature | Wave | QuickBooks Online | FreshBooks | Xero |
|---------|------|------------------|-----------|------|
| **Price (CAD/mo)** | Free | $20-50 | $22-55 | $20-48 |
| **Best For** | Freelancers, micro | SMBs, growing | Service businesses | Tech-savvy, multi-currency |
| **Bank Feeds** | Yes (Canadian banks) | Yes (excellent) | Yes | Yes |
| **Multi-Currency** | Limited | Good | Basic | Excellent |
| **Invoicing** | Good | Excellent | Best-in-class | Good |
| **T2125 Mapping** | Decent | Good | Basic | Manual |
| **HST Filing** | Manual | Built-in | Basic | Good |
| **Payroll** | Wave Payroll (free basic) | QuickBooks Payroll ($) | No | No (integrate) |
| **Receipt Scanning** | No | Yes (mobile) | Yes | Yes (Hubdoc) |
| **API / Integrations** | Limited | Extensive | Moderate | Extensive |
| **Stripe Integration** | No | Yes | Yes | Yes |
| **Wise Integration** | No | Yes | No | Yes |
| **Scalability** | Low | High | Medium | High |

**Recommendation by stage:**
- **$0-30K revenue, sole proprietor:** Wave (free, Canadian, gets the job done)
- **$30K-150K, growing:** QuickBooks Online or Xero (bank feeds, integrations, HST)
- **$150K+, multi-currency, scaling:** Xero (best multi-currency) or QBO (best ecosystem)
- **Post-incorporation:** QBO or Xero (accountant access, payroll, proper reporting)

### 8.2 Bank Feed Setup

Bank feeds automatically import transactions from your bank and credit card into your accounting software. This is the single highest-ROI automation.

**Setup steps:**
1. Connect all business bank accounts (checking, savings, credit card)
2. Connect payment processors (Stripe, PayPal, Wise)
3. Set up matching rules: "Anthropic API" always categorizes to 5010 (API Costs)
4. Review and approve daily (2-3 minutes) or weekly (15 minutes)
5. Target: 80% of transactions auto-categorized, 20% need manual review

**Rules to create on day one:**
- Cloud hosting charges -> 5000 (COGS - Hosting)
- Software subscriptions (name each one) -> 6250 (Software)
- Stripe deposits -> 4000/4010 (Revenue by type)
- CRA payments -> 2400/2410 (Tax/CPP Payable)

### 8.3 Receipt Management

CRA requires receipts for all business expenses. No receipt = no deduction in an audit.

**Options:**
- **Dext (formerly Receipt Bank):** $24/mo. Photograph receipt, auto-extracts vendor/amount/date/tax, pushes to QBO/Xero. Best-in-class.
- **Hubdoc (included with Xero):** Free with Xero. Similar to Dext. Also fetches recurring bills automatically.
- **QBO Mobile:** Built-in receipt capture. Attach to transactions. Free with QBO.
- **Phone camera + Google Drive:** Free. Photograph receipts, organize by month. Manual but works.

**The rule:** Photograph every receipt the moment you get it. Paper fades, gets lost, goes through the wash. Digital is forever.

`[CAN]` CRA accepts electronic copies of receipts. You do not need to keep paper originals if you have clear digital copies with date, vendor, amount, and tax. Retain for 6 years from the end of the tax year.

### 8.4 Month-End Close Process

`[TEMPLATE]` **5 steps, target 90 minutes:**

```
MONTH-END CLOSE CHECKLIST
=========================

Step 1: RECONCILE (30 min)
[ ] Bank reconciliation -- all accounts match statements
[ ] Credit card reconciliation
[ ] Stripe/payment processor reconciliation
[ ] Wise balance reconciliation (check FX rate)

Step 2: CATEGORIZE (20 min)
[ ] Review and approve all bank feed transactions
[ ] Categorize any uncategorized items
[ ] Code all receipts in Dext/Hubdoc to correct accounts

Step 3: ACCRUE (15 min)
[ ] Record any revenue earned but not yet invoiced
[ ] Record any expenses incurred but not yet billed
[ ] Adjust prepaid expenses (reduce by 1/12 if annual)
[ ] Adjust deferred revenue (recognize earned portion)

Step 4: REVIEW (15 min)
[ ] Run P&L -- does it make sense vs last month?
[ ] Run Balance Sheet -- does it balance?
[ ] Check AR aging -- who owes you money? Follow up.
[ ] Check AP aging -- what bills are due?

Step 5: REPORT (10 min)
[ ] Export P&L and Balance Sheet to PDF
[ ] Note any unusual items or one-time events
[ ] Update cash flow forecast for next 3 months
[ ] File in monthly archive (YYYY-MM format)
```

### 8.5 Year-End Close Process for CPA Handoff

`[CAN]` `[TEMPLATE]`

```
YEAR-END CLOSE CHECKLIST (for CPA)
===================================

BEFORE DEC 31:
[ ] Complete all 12 month-end closes
[ ] Review CCA schedule -- confirm asset additions and dispositions
[ ] Trigger any tax-loss harvesting (sell losers before Dec 31)
[ ] Confirm all invoices issued for work completed in the year
[ ] Pre-pay January expenses if cash basis and want the deduction now

JANUARY-FEBRUARY:
[ ] Final bank reconciliation for Dec 31
[ ] Record all December accruals
[ ] Reconcile HST collected vs HST paid -- confirm net payable
[ ] Compile T-slips received (T4, T5, T3, T4A, etc.)
[ ] Compile crypto transaction report (all trades, staking, dispositions)
[ ] Confirm FX rates for all USD balances as at Dec 31
[ ] Prepare CCA schedule (asset cost, class, rate, prior UCC, additions, dispositions)

PACKAGE FOR CPA:
[ ] Full year P&L (January 1 - December 31)
[ ] Balance Sheet as at December 31
[ ] General Ledger trial balance
[ ] Bank statements (all accounts, all 12 months)
[ ] AR aging report as at Dec 31
[ ] AP listing as at Dec 31
[ ] CCA schedule
[ ] Home office calculation (square footage, total costs)
[ ] Vehicle log (if claiming vehicle expenses)
[ ] Crypto transaction summary
[ ] Any unusual items or questions
[ ] Prior year Notice of Assessment from CRA
```

---

## 9. Tax Accounting vs Financial Accounting

### 9.1 They Are NOT the Same

Financial accounting (what your P&L and balance sheet show) and tax accounting (what you report to CRA) start from the same transactions but diverge significantly. The result: your taxable income is different from your accounting income.

**Why they diverge:**

| Item | Financial Accounting | Tax Accounting |
|------|---------------------|---------------|
| **Depreciation** | Straight-line over useful life (e.g., 3 years) | CCA at prescribed rates (e.g., Class 50 at 55% declining balance) |
| **Meals** | 100% expense | `[CAN]` 50% deductible (s.67.1 ITA) |
| **Entertainment** | 100% expense | `[CAN]` 50% deductible (s.67.1 ITA) |
| **Reserves** | Per accounting standards (IFRS/ASPE) | Per ITA s.20(1)(m) -- different formula |
| **Stock-based comp** | Fair value expense | `[CAN]` Deductible when exercised, not when granted |
| **Capital gains** | Included in income at 100% | `[CAN]` 50% inclusion rate (first $250K), 66.7% thereafter (2024+ rules) |
| **Fines & penalties** | Expense (reduces income) | `[CAN]` NOT deductible (s.67.6 ITA) |
| **Life insurance premiums** | Expense | `[CAN]` NOT deductible (unless collateral for loan) |
| **Club dues** | Expense | `[CAN]` NOT deductible (s.18(1)(l) ITA) |

### 9.2 CCA vs Depreciation

`[CAN]` This is the most common book-tax difference.

**Financial accounting depreciation:** You choose a method (straight-line is most common) and a useful life.
- Example: $3,000 laptop, 3-year useful life, straight-line = $1,000/year expense

**Tax depreciation (CCA):** CRA prescribes the class and rate. You have no choice on rate (but you choose how much to claim up to the maximum).
- Example: $3,000 laptop, Class 50, 55% declining balance
  - Year 1: $3,000 x 55% x 50% (half-year rule) = $825 (or up to $3,000 with immediate expensing for CCPCs)
  - Year 2: ($3,000 - $825) x 55% = $1,196
  - Year 3: ($2,175 - $1,196) x 55% = $539

**Immediate expensing** `[CAN]`: Eligible businesses (CCPCs and unincorporated businesses) can claim 100% CCA in the first year on up to $1.5M of eligible property. This eliminates the timing difference for many assets.

### 9.3 Deferred Tax

When financial accounting recognizes an expense before tax accounting does (or vice versa), a **deferred tax** balance is created.

**Example (simplified):**
- Financial statements depreciation: $1,000/year for 3 years
- CCA claimed: $1,650 in year 1, $743 in year 2, $409 in year 3

Year 1: CCA ($1,650) > book depreciation ($1,000) by $650. You paid less tax now than your books suggest. This creates a **deferred tax liability** of $650 x tax rate -- you will pay this tax in the future when CCA runs out but book depreciation continues.

For a sole proprietor, deferred tax is not formally tracked (CRA only sees the tax return). But for corporations reporting under ASPE or IFRS, deferred tax assets and liabilities appear on the balance sheet.

### 9.4 Common Book-Tax Differences (Canada)

| Item | Book Treatment | Tax Treatment | Effect |
|------|---------------|--------------|--------|
| Depreciation vs CCA | Straight-line | Declining balance at CRA rates | Timing difference |
| Meals & entertainment | 100% expense | 50% deductible | Permanent difference |
| Capital gains | 100% in income | 50% inclusion (first $250K) | Permanent difference |
| Warranty provisions | Accrued when probable | Deductible when paid | Timing difference |
| Bad debt expense | Accrued when doubtful | Deductible when written off | Timing difference |
| Accounting reserves | Per GAAP/IFRS | Only specific reserves per ITA | Permanent or timing |
| Stock option expense | Fair value at grant | Deductible at exercise | Timing difference |
| R&D costs | Expensed or capitalized (IAS 38) | SR&ED: 100% deductible + 35% ITC | Permanent difference (benefit) |

### 9.5 The Reconciliation

Your CPA performs a tax-to-book reconciliation as part of preparing your tax return:

```
Accounting Net Income (per financial statements)      $49,900
ADD BACK (non-deductible or timing):
  + Meals & entertainment (50% non-deductible)         $1,200
  + Accounting depreciation (replaced by CCA)          $5,400
  + Fines and penalties                                    $0
  + Club dues                                              $0
DEDUCT (tax-only deductions):
  - CCA claimed                                       ($8,200)
  - Home office (if different from book)                   $0
                                                      -------
Taxable Income (for CRA)                              $48,300
```

---

## 10. Management Accounting -- Internal Decision-Making

Financial accounting tells the outside world how you did. Management accounting tells YOU what to do next. No rules, no standards, no auditors -- just useful information for decisions.

### 10.1 Budgeting

**Zero-Based Budgeting (ZBB):** Start from zero every period. Every expense must be justified from scratch. No "we spent $X last year so we will spend $X this year."

- **Advantage:** Eliminates waste, forces scrutiny of every dollar
- **Disadvantage:** Time-consuming, can be demoralizing ("justify your existence every quarter")
- **Best for:** Cost-cutting periods, new businesses, annual strategic planning

**Incremental Budgeting:** Start from last year's actual, adjust up or down.

- **Advantage:** Fast, easy, based on reality
- **Disadvantage:** Perpetuates inefficiencies ("we always spent $10K on X")
- **Best for:** Stable businesses with predictable costs

**Rolling Forecast:** Always maintain a 12-month forward view. Each month, drop the completed month and add a new month at the end.

- **Advantage:** Always forward-looking, adapts to reality, never "stale"
- **Disadvantage:** Requires monthly updates, more work
- **Best for:** SaaS businesses, high-growth companies, volatile environments

**Recommendation for SMBs:** Annual budget (incremental) + quarterly rolling forecast. Review budget vs actual monthly.

### 10.2 Variance Analysis

Every month, compare budget to actual. The three questions:

1. **What happened?** Revenue was $8K vs $12K budget. A $4K negative variance.
2. **Why?** Two major clients delayed projects by 6 weeks.
3. **What do we do?** Pipeline still strong. Adjust Q2 forecast upward. No cost cuts needed.

**Variance types:**
- **Favorable:** Revenue higher than budgeted, or expenses lower than budgeted
- **Unfavorable:** Revenue lower than budgeted, or expenses higher than budgeted
- **Volume variance:** Sold more or fewer units than planned
- **Price variance:** Sold at a higher or lower price than planned
- **Mix variance:** Sold a different product mix than planned (more consulting, less SaaS)

**Template:**

```
MONTHLY VARIANCE REPORT — March 2026
=====================================

                     Budget    Actual    Variance    %       Note
Revenue              $12,000   $8,000    ($4,000)   -33%    2 projects delayed
COGS                 ($1,800)  ($1,200)   $600      +33%    Lower volume
Gross Profit         $10,200   $6,800    ($3,400)   -33%
Opex                 ($3,200)  ($2,900)   $300      +9%     Under on marketing
Net Income            $7,000   $3,900    ($3,100)   -44%

Action: Pipeline solid. Revenue expected to catch up in April-May.
        No cost reductions required. Continue marketing spend.
```

### 10.3 Cost Accounting: Fixed vs Variable

| Cost Type | Definition | Examples | Behavior |
|-----------|-----------|----------|----------|
| **Fixed** | Does not change with volume | Rent, insurance, salaries, software subscriptions | Same at 0 clients or 100 clients |
| **Variable** | Changes proportionally with volume | COGS, commissions, payment processing fees, API costs | Doubles if volume doubles |
| **Semi-variable** | Fixed base + variable component | Phone (fixed plan + overages), utilities, cloud (reserved + on-demand) | Step-function or mixed |

**Why it matters:** Fixed costs create **operating leverage**. A SaaS business with 85% gross margin and mostly fixed opex gets dramatically more profitable as revenue grows -- each new dollar of revenue drops almost entirely to the bottom line.

### 10.4 Break-Even Analysis

```
BREAK-EVEN POINT = Fixed Costs / Contribution Margin per Unit
```

**Contribution Margin** = Revenue per Unit - Variable Cost per Unit

**Example:**
- SaaS subscription: $200/month per customer
- Variable cost per customer: $30/month (hosting, API, support)
- Contribution margin: $170/month per customer
- Fixed monthly costs: $8,500 (software, home office, insurance, etc.)
- Break-even: $8,500 / $170 = **50 customers**

Below 50 customers, you lose money. Above 50, every new customer contributes $170/month to profit.

**In dollars:**
- Break-even revenue = Fixed Costs / Contribution Margin Ratio
- Contribution margin ratio = $170 / $200 = 85%
- Break-even revenue = $8,500 / 0.85 = **$10,000/month**

### 10.5 Contribution Margin by Client/Product

Not all revenue is equal. Which clients and products contribute the most?

```
CLIENT CONTRIBUTION ANALYSIS — Q1 2026
=======================================

Client          Revenue    Direct Costs   Contribution   Margin    Verdict
Enterprise A    $15,000    $2,000         $13,000        87%       Star
Startup B        $4,500    $3,200          $1,300        29%       Drain
Agency C         $8,000    $1,500          $6,500        81%       Solid
Startup D        $2,000      $400          $1,600        80%       Small but efficient
                -------    ------         -------
Total           $29,500    $7,100         $22,400        76%

INSIGHT: Startup B consumes 45% of direct costs for 15% of revenue.
ACTION: Raise price, reduce scope, or replace with a better-fit client.
```

### 10.6 Pricing Using Cost-Volume-Profit (CVP)

**Cost-plus pricing:** Calculate total cost per unit, add desired margin.
- Total cost per customer/month: $30 variable + ($8,500 / 50 customers) = $200
- Desired margin: 50%
- Price: $200 / (1 - 0.50) = $400/month

**Value-based pricing:** Price based on value delivered, not cost.
- Your SaaS saves a client 20 hours/month of manual work at $50/hour = $1,000/month value
- Price at 20-30% of value = $200-300/month
- Your cost is irrelevant to the pricing decision (but must be covered)

**Competitor-based pricing:** Price relative to alternatives.
- Competitors charge $150-350/month
- Position at $249 for mid-market with superior features

**The CFO perspective:** Use all three inputs. Cost-plus sets the floor (never go below). Value-based sets the ceiling. Competitor-based sets the market range. Optimize within.

### 10.7 Make vs Buy (In-House vs Outsource)

**Framework:**

| Factor | In-House | Outsource |
|--------|---------|-----------|
| **Cost** | Fixed (salary, benefits, equipment) | Variable (pay per project/hour) |
| **Quality control** | High (direct supervision) | Variable (depends on vendor) |
| **Scalability** | Limited by headcount | Scales up/down quickly |
| **IP protection** | Retained internally | Risk of leakage |
| **Opportunity cost** | Time spent managing | Time spent vendor managing |

**Decision rule:** Outsource if the activity is not a core competency AND the outsource cost is less than 70% of in-house fully-loaded cost AND quality is acceptable.

### 10.8 Capital Budgeting: NPV, IRR, Payback

For investment decisions (should I buy this equipment? hire this person? build this product?):

**Net Present Value (NPV):**
```
NPV = Sum of [Cash Flow_t / (1 + r)^t] for all periods t, minus initial investment
```

If NPV > 0, the investment creates value. Accept it.

**Example:** Invest $10,000 in a new server. Expected to generate $4,000/year in savings for 4 years. Discount rate: 10%.

```
Year 0: -$10,000
Year 1: $4,000 / 1.10 = $3,636
Year 2: $4,000 / 1.21 = $3,306
Year 3: $4,000 / 1.33 = $3,005
Year 4: $4,000 / 1.46 = $2,740
NPV = -$10,000 + $3,636 + $3,306 + $3,005 + $2,740 = +$2,687

NPV is positive. Accept the investment.
```

**Internal Rate of Return (IRR):** The discount rate at which NPV = 0. If IRR > your cost of capital, accept.

In the example above, IRR = ~22%. If your cost of capital is 10%, the investment clears the hurdle.

**Payback Period:** How long until you recover the initial investment.
- $10,000 / $4,000 per year = **2.5 years**

Simple but ignores time value of money and cash flows after payback. Use as a sanity check alongside NPV.

---

## 11. Audit, Compliance, and Financial Controls

### 11.1 Internal Controls

Internal controls are processes that ensure financial data is accurate, assets are protected, and fraud is prevented. The three pillars:

1. **Segregation of duties:** The person who approves a purchase should not be the person who writes the check. The person who receives inventory should not be the person who records it.
2. **Authorization limits:** Purchases over $X require a second approval. Wire transfers require dual authorization.
3. **Reconciliation:** Bank reconciliation, AR reconciliation, inventory counts -- verify that records match reality.

### 11.2 Controls for Solo Founders

When you ARE the only person, segregation of duties is impossible. Compensating controls:

| Risk | Compensating Control |
|------|---------------------|
| No one reviews your expenses | Set a monthly budget. Flag anything over $500 for deliberate review. Have your CPA review quarterly. |
| No one reconciles your bank | Automated bank feeds + monthly reconciliation (you do it, but the automation catches errors). |
| No one approves payments | Separate business and personal accounts. Never pay personal expenses from business account. |
| Fraud by employees (future) | Background checks, fidelity bond, regular financial review, surprise audits. |
| Data loss | Cloud accounting software (auto-backup), receipt scanning (off-device copies), encrypted offsite backup of financial records. |

**The minimum viable control set for a solo founder:**
1. Monthly bank reconciliation (non-negotiable)
2. Separate business bank account (non-negotiable)
3. Receipt capture for every expense (non-negotiable)
4. Quarterly CPA review of books (highly recommended)
5. Annual financial statement preparation (required for tax)

### 11.3 Bank Reconciliation

**What:** Compare your accounting records to the bank statement line by line. Every transaction in the bank must be in your books. Every transaction in your books must be in the bank. Any differences must be explained.

**Common reconciling items:**
- Outstanding checks (you recorded it, bank has not cleared it yet)
- Deposits in transit (you recorded it, bank has not credited it yet)
- Bank charges (bank charged you, you have not recorded it yet)
- Interest earned (bank credited you, you have not recorded it yet)
- Errors (yours or the bank's)

**Frequency:** Monthly, within 5 business days of receiving the statement. With bank feeds, this is largely automated -- but you must still review.

### 11.4 Review, Audit, and Compilation (Canada)

`[CAN]` Three levels of assurance for financial statements:

| Level | What It Is | Who Needs It | Cost (estimate) |
|-------|-----------|-------------|----------------|
| **Compilation (Notice to Reader)** | CPA compiles statements from your data. No verification. "I compiled these from management's numbers." | Most small businesses, sole proprietors, basic tax filing | $500-2,000 |
| **Review Engagement** | CPA performs analytical procedures and inquiries. "Nothing came to my attention suggesting these are wrong." Limited assurance. | Some lenders, franchise agreements, larger businesses | $3,000-8,000 |
| **Audit** | CPA performs extensive testing -- confirms bank balances, sends letters to customers, counts inventory, tests transactions. "These statements are fairly presented." Highest assurance. | Public companies (mandatory), some private companies, investor requirements, bank covenants | $10,000-50,000+ |

**When you need an audit:**
- Public companies: always required
- Private companies: if required by corporate statute (e.g., shareholders holding 10%+ can demand one)
- Investor term sheets: often require annual audited financials
- Bank loans: lenders may require audited or reviewed financials for loans above a threshold

### 11.5 SOC 2 Compliance

`[SAAS]` `[FUTURE]` If selling to enterprise clients, SOC 2 is increasingly expected.

**SOC 2 Type I:** Point-in-time assessment of security controls. "As of date X, these controls exist."
**SOC 2 Type II:** Assessment over a period (usually 6-12 months). "Over this period, these controls operated effectively."

**Trust Service Criteria:**
- Security (required)
- Availability (common for SaaS)
- Processing Integrity
- Confidentiality
- Privacy

**Cost:** $20K-80K for the audit, plus internal preparation costs. For small SaaS companies, alternatives like SOC 2 compliance platforms (Vanta, Drata, Secureframe) can reduce effort and cost.

### 11.6 Record Retention Requirements

| Jurisdiction | Retention Period | What to Keep |
|-------------|-----------------|-------------|
| `[CAN]` CRA | **6 years** from end of tax year | All books, records, source documents, invoices, receipts, bank statements, contracts |
| US (IRS) | **7 years** from filing date (or 6 from payment of tax) | Same as above for US-source income |
| CRA (fraud) | **Indefinite** | If CRA suspects fraud, no time limit on reassessment or record requests |
| Corporate records | **Permanent** | Articles of incorporation, bylaws, shareholder agreements, minutes |
| Employee records | **7 years** after termination | T4s, payroll records, ROEs, employment contracts |

**Practical rule:** Keep everything for 7 years. Digital storage is cheap. Getting audited without records is expensive.

---

## 12. Financial Reporting for Stakeholders

Different audiences need different reports. The CFO's job is to translate the same financial reality into the format each stakeholder needs.

### 12.1 Reporting to Yourself (Monthly Management Report)

`[TEMPLATE]` **The Monthly CFO Dashboard:**

```
MONTHLY CFO REPORT — [Month Year]
==================================

1. HEADLINES
   Revenue:           $XX,XXX  (vs $XX,XXX budget, +/-X%)
   Net Income:        $XX,XXX  (vs $XX,XXX budget, +/-X%)
   Cash Balance:      $XX,XXX  (vs $XX,XXX last month)
   AR Outstanding:    $XX,XXX  (XX days DSO)
   Runway:            XX months at current burn

2. P&L SUMMARY
   Revenue by type:
     SaaS:            $XX,XXX  (X% of total)
     Consulting:      $XX,XXX  (X% of total)
     Other:           $XX,XXX  (X% of total)
   Gross Margin:      XX%  (target: XX%)
   Operating Margin:  XX%  (target: XX%)

3. CASH FLOW
   Operating CF:      $XX,XXX
   Investing CF:      ($X,XXX)
   Financing CF:      ($X,XXX)
   Free Cash Flow:    $XX,XXX

4. KEY METRICS
   MRR:               $XX,XXX  (vs $XX,XXX last month, +X%)
   Active Clients:    XX  (vs XX last month)
   LTV/CAC:           X.Xx
   Rule of 40:        XX%

5. AR AGING
   Current (0-30):    $XX,XXX
   31-60 days:        $XX,XXX
   61-90 days:        $XX,XXX  <-- FOLLOW UP
   90+ days:          $XX,XXX  <-- ESCALATE

6. TAX POSITION
   Estimated tax owing YTD:     $XX,XXX
   Installments paid YTD:       $XX,XXX
   HST owing (net):             $XX,XXX
   Next installment due:        [date]

7. ACTIONS
   [ ] Follow up on 60+ day AR
   [ ] Review [specific expense] that was over budget
   [ ] Forecast updated for Q2
```

### 12.2 Reporting to Partners/Co-Founders (Quarterly Board Deck)

`[TEMPLATE]` `[FUTURE]` **10-slide quarterly business review:**

```
Slide 1: Executive Summary (3 bullet points: good, bad, what's next)
Slide 2: KPI Dashboard (MRR, growth rate, churn, NRR, runway)
Slide 3: Financial Summary (P&L, key line items, budget vs actual)
Slide 4: Revenue Breakdown (by product, by segment, by geography)
Slide 5: Cash Position (cash balance, runway, burn rate trend)
Slide 6: Customer Metrics (new, churned, expansion, NDR, pipeline)
Slide 7: Product Update (shipped, planned, roadmap priorities)
Slide 8: Team Update (headcount, key hires, org changes)
Slide 9: Risks & Opportunities (top 3 each, with mitigation/capture plans)
Slide 10: Asks / Decisions Needed (specific requests from the board)
```

### 12.3 Reporting to Investors (Annual)

`[FUTURE]` Investors expect:
- **Audited or reviewed financial statements** (P&L, Balance Sheet, Cash Flow, Notes)
- **Management Discussion & Analysis (MD&A):** Narrative explanation of financial results
- **Key metrics dashboard:** Revenue growth, NDR, LTV/CAC, burn multiple, Rule of 40
- **Cap table update:** Ownership percentages, outstanding options, dilution
- **Use of funds:** How investment capital was deployed vs plan
- **Forward guidance:** Revenue projections for next 12 months with assumptions

### 12.4 Reporting to Banks/Lenders

Lenders care about one thing: can you repay the loan? Reports focus on:

- **Debt service coverage ratio (DSCR):** EBITDA / (Interest + Principal payments). Must be > 1.2x typically.
- **Covenant compliance:** Whatever ratios the loan agreement specifies (current ratio, debt-to-equity, minimum cash balance).
- **Aged AR report:** Lenders want to see collectible receivables.
- **Cash flow projections:** Next 12 months, showing ability to meet all debt obligations.

### 12.5 Reporting to CRA

`[CAN]`

| Filing | Due Date | What It Contains |
|--------|---------|-----------------|
| **T1 (with T2125)** | June 15 (self-employed), payment due April 30 | Personal return with business income statement |
| **T2 (Corporate)** | 6 months after fiscal year-end | Corporate tax return |
| **HST Return** | Varies (monthly, quarterly, or annual based on revenue) | HST collected minus ITCs = net remittance |
| **T4 Summary** | Feb 28 | Employee compensation reporting |
| **T5 Summary** | Feb 28 | Dividends paid reporting |
| **T1135** | With T1/T2 | Foreign property > $100K CAD |

### 12.6 Reporting for US Clients

If you have US-based clients and revenue:

- **W-8BEN** (individuals) or **W-8BEN-E** (entities): Provide to US clients so they do not withhold 30% US tax on payments to you. Claims treaty rate (typically 0% for business profits under Canada-US treaty).
- **Invoices:** Issue in USD, with your business name, address, and (optionally) Canadian HST number. US clients do not pay HST.
- **1099 avoidance:** With a valid W-8BEN on file, US clients should NOT issue you a 1099. If they do, it does not create a US tax obligation -- but keep records showing you properly filed the W-8BEN.

---

## Appendix A -- Templates and Checklists

### A.1 Startup Financial Statements Template (Year 1)

```
[COMPANY NAME] — Income Statement
For the Period [Start Date] to [End Date]
==========================================

REVENUE
  Product/Service Revenue A                 $________
  Product/Service Revenue B                 $________
  Other Revenue                             $________
TOTAL REVENUE                                           $________

COST OF GOODS SOLD
  Direct Cost 1                             $________
  Direct Cost 2                             $________
  Direct Cost 3                             $________
TOTAL COGS                                              ($________)

GROSS PROFIT                                            $________
  Gross Margin:                                          ________%

OPERATING EXPENSES
  Salaries & Wages                          $________
  Rent / Home Office                        $________
  Software & Subscriptions                  $________
  Marketing & Advertising                   $________
  Professional Fees (CPA/Legal)             $________
  Insurance                                 $________
  Telecom / Internet                        $________
  Travel & Meals                            $________
  Office Supplies                           $________
  Bank & Processing Fees                    $________
  Depreciation & Amortization               $________
  Other Expenses                            $________
TOTAL OPERATING EXPENSES                                ($________)

OPERATING INCOME (EBIT)                                 $________
  Operating Margin:                                      ________%

  Interest Expense                          ($________)
  Other Non-Operating Items                 $________

INCOME BEFORE TAX                                       $________
  Income Tax Provision                      ($________)

NET INCOME                                              $________
  Net Margin:                                            ________%
```

### A.2 Monthly Financial Health Checklist

```
MONTHLY FINANCIAL HEALTH CHECK
===============================

CASH & LIQUIDITY
[ ] Cash balance is sufficient for 3+ months of expenses
[ ] No unexpected large outflows upcoming
[ ] Working capital ratio > 1.5x

REVENUE & GROWTH
[ ] Revenue is on track vs budget (+/- 10%)
[ ] No customer concentration risk (no client > 30% of revenue)
[ ] Pipeline covers next quarter's target

PROFITABILITY
[ ] Gross margin is within 5% of target
[ ] Operating expenses are within budget
[ ] No line items with >20% unfavorable variance unexplained

COLLECTIONS & PAYABLES
[ ] AR aging: nothing over 60 days without follow-up
[ ] AP: all vendors paid within terms
[ ] HST collected is segregated (not spent)

COMPLIANCE
[ ] Bank reconciliation complete
[ ] All receipts captured and categorized
[ ] Tax installments paid on time
[ ] HST filed on time

FORWARD LOOK
[ ] 3-month cash flow forecast updated
[ ] Known large expenses identified and planned for
[ ] Tax position estimated (no April surprise)
```

### A.3 Financial Statement Analysis Checklist

```
HOW TO READ ANYONE'S FINANCIAL STATEMENTS (5-Minute Assessment)
================================================================

INCOME STATEMENT (2 min)
[ ] Revenue trend: growing, flat, or declining? (3 years minimum)
[ ] Gross margin: is it stable, expanding, or compressing?
[ ] Operating margin: is the company operationally profitable?
[ ] Net income: positive? If not, how far from breakeven?
[ ] Any one-time items distorting the picture?

BALANCE SHEET (2 min)
[ ] Cash: how many months of operating expenses?
[ ] Current ratio: > 1.5x? (can pay short-term obligations)
[ ] Debt-to-equity: < 2x? (not over-leveraged)
[ ] Goodwill: is it a large % of total assets? (acquisition risk)
[ ] Working capital: positive or negative? Trend?

CASH FLOW (1 min)
[ ] Operating cash flow: positive? (the business generates cash)
[ ] Free cash flow: positive? (cash after maintaining the business)
[ ] Is the company funding operations from financing? (unsustainable)
[ ] Capex: is it growing faster than revenue? (investment or waste?)
[ ] Cash balance change: increasing or decreasing over 3 years?

RED FLAGS:
- Revenue growing but cash flow declining = collection problems or aggressive recognition
- Inventory growing faster than revenue = demand problem
- AR growing faster than revenue = collection problem
- Debt growing while cash declines = borrowing to survive
- Consistent "one-time" charges = they are not one-time
- Operating CF negative but net income positive = accrual manipulation
```

### A.4 Chart of Accounts Setup Checklist

```
CHART OF ACCOUNTS SETUP (New Business)
=======================================

BEFORE YOU START:
[ ] Determine your business type (service, product, SaaS, hybrid)
[ ] Determine your accounting method (cash or accrual)
[ ] Determine your tax jurisdiction and filing requirements
[ ] Review the tax form you'll file (T2125, T2, Schedule C) -- accounts should map to form lines

MINIMUM ACCOUNTS NEEDED:
[ ] 1000: Operating Bank Account (checking)
[ ] 1010: Savings Account (HST/tax reserve)
[ ] 1100: Accounts Receivable
[ ] 1500: Equipment / Fixed Assets
[ ] 1550: Accumulated Depreciation
[ ] 2000: Accounts Payable
[ ] 2100: Sales Tax Payable (HST/GST)
[ ] 2200: Credit Card
[ ] 2400: Income Tax Payable
[ ] 3000: Owner's Equity / Capital
[ ] 3100: Owner's Draws / Distributions
[ ] 3200: Retained Earnings
[ ] 4000: Revenue (by type -- at least 2-3 accounts)
[ ] 5000: Cost of Goods Sold (by type)
[ ] 6000-6999: Operating Expenses (15-25 accounts covering all expense categories)
[ ] 7000: Other Income (interest, FX gains)
[ ] 7100: Other Expense (FX losses, non-operating)

RULES:
- Start simple. You can always add accounts later. You cannot easily merge accounts.
- Every account needs a clear, unambiguous name
- Use consistent numbering gaps (10s or 100s) to allow for future additions
- Map each expense account to the corresponding tax form line
- Expense accounts should be specific enough for tax reporting but general enough to avoid clutter
```

---

## Appendix B -- Glossary of Financial Terms

| Term | Definition |
|------|-----------|
| **Accounts Payable (AP)** | Money you owe to suppliers for goods/services received but not yet paid for |
| **Accounts Receivable (AR)** | Money customers owe you for goods/services delivered but not yet paid for |
| **Accrual** | Recording revenue when earned and expenses when incurred, regardless of cash flow |
| **Amortization** | Spreading the cost of an intangible asset over its useful life (or of a loan over its term) |
| **ASPE** | Accounting Standards for Private Enterprises -- Canadian GAAP for private companies |
| **Book Value** | Total assets minus total liabilities per the balance sheet |
| **Burn Rate** | Monthly cash consumption (how fast you are spending your cash reserves) |
| **CAC** | Customer Acquisition Cost -- total sales and marketing spend divided by new customers acquired |
| **Capex** | Capital Expenditure -- spending on long-lived assets (equipment, buildings, software development) |
| **CCA** | Capital Cost Allowance -- Canadian tax depreciation system with prescribed rates by asset class |
| **COGS** | Cost of Goods Sold -- direct costs to produce/deliver your product or service |
| **Contribution Margin** | Revenue minus variable costs. The amount each unit sale contributes to covering fixed costs |
| **Current Assets** | Assets expected to be converted to cash within 12 months |
| **Current Liabilities** | Obligations due within 12 months |
| **DCF** | Discounted Cash Flow -- valuation method based on present value of projected future cash flows |
| **Deferred Revenue** | Cash received for services not yet delivered. A liability until the service is performed |
| **Depreciation** | Spreading the cost of a tangible asset over its useful life |
| **DSO** | Days Sales Outstanding -- average number of days to collect payment from customers |
| **EBIT** | Earnings Before Interest and Taxes -- operating profit |
| **EBITDA** | Earnings Before Interest, Taxes, Depreciation, and Amortization -- proxy for operating cash flow |
| **Enterprise Value (EV)** | Market capitalization plus total debt minus cash. The total acquisition cost of a business |
| **Equity** | The owners' residual interest in the business after all liabilities are paid |
| **FCF** | Free Cash Flow -- operating cash flow minus capital expenditures. The cash truly available |
| **GAAP** | Generally Accepted Accounting Principles -- the standard rules for financial reporting |
| **Goodwill** | The premium paid in an acquisition above the fair value of identifiable net assets |
| **Gross Margin** | (Revenue - COGS) / Revenue. Measures production/delivery efficiency |
| **IFRS** | International Financial Reporting Standards -- used by public companies in 140+ countries |
| **IRR** | Internal Rate of Return -- the discount rate that makes NPV equal zero |
| **LTV** | Lifetime Value -- total profit expected from a customer over their entire relationship |
| **MRR** | Monthly Recurring Revenue -- predictable subscription revenue per month |
| **NDR** | Net Dollar Retention -- measures whether existing customers spend more or less over time |
| **Net Income** | The bottom line. Revenue minus all expenses, interest, and taxes |
| **NOPAT** | Net Operating Profit After Tax -- EBIT x (1 - tax rate). Used for ROIC calculation |
| **NPV** | Net Present Value -- sum of discounted future cash flows minus initial investment |
| **Opex** | Operating Expenditure -- ongoing costs of running the business (not capitalized) |
| **P&L** | Profit and Loss statement. Synonym for Income Statement |
| **PP&E** | Property, Plant, and Equipment -- tangible long-lived assets |
| **Retained Earnings** | Cumulative net income minus cumulative dividends since the company began |
| **Revenue Recognition** | The principle governing when revenue is recorded in the financial statements |
| **ROA** | Return on Assets -- net income divided by average total assets |
| **ROE** | Return on Equity -- net income divided by average shareholders' equity |
| **ROIC** | Return on Invested Capital -- NOPAT divided by invested capital (equity + net debt) |
| **Runway** | Months of operation remaining at current cash burn rate |
| **WACC** | Weighted Average Cost of Capital -- blended cost of debt and equity financing |
| **Working Capital** | Current assets minus current liabilities. Measures short-term financial health |

---

## Quick Reference: The Three Statements at a Glance

```
+-------------------+     +-------------------+     +-------------------+
|  INCOME STATEMENT |     |   BALANCE SHEET    |     | CASH FLOW STMT   |
|  (Period: movie)  |     |  (Point: snapshot) |     |  (Period: movie)  |
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
| Revenue           |     | ASSETS            |     | Operating CF      |
| - COGS            |     |   Cash --------+  |     |   Net Income      |
| = Gross Profit    |     |   AR            |  |     |   + D&A           |
| - Opex            |     |   Inventory     |  |     |   +/- Working Cap |
| = EBITDA          |     |   PP&E          |  |     |                   |
| - D&A  --------+  |     |   Intangibles   |  |     | Investing CF      |
| = EBIT         |  |     |                 |  |     |   - Capex         |
| - Interest     |  |     | LIABILITIES     |  |     |   - Acquisitions  |
| = EBT          |  |     |   AP            |  |     |                   |
| - Tax          |  |     |   Deferred Rev  |  |     | Financing CF      |
| = Net Income --+--+---> |   Debt          |  |     |   + Debt raised   |
|                |  |     |                 |  |     |   - Debt repaid   |
|    Retained ---+  |     | EQUITY          |  |     |   - Dividends     |
|    Earnings    |  |     |   Share Capital  |  |     |                   |
|                |  +---> |   Retained Earn |  |     | = Net Cash Change |
|                |        |                 |  |     |        |          |
| D&A adds back  +------> |                 |  +-----+--------+          |
| to cash flow   |        |   Cash balance <+--+     Reconciles to      |
+-------------------+     +-------------------+     | ending cash       |
                                                    +-------------------+
```

---

*This document is part of the ATLAS CFO knowledge base. For tax-specific guidance, see `docs/ATLAS_TAX_STRATEGY.md`. For bookkeeping procedures, see `docs/ATLAS_BOOKKEEPING_SYSTEMS.md`. For SaaS tax treatment, see `docs/ATLAS_AI_SAAS_TAX_GUIDE.md`.*
