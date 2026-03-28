# ATLAS — SaaS Financial Metrics, Revenue Optimization & CFO Playbook

> **For:** Conaugh McKenna (CC), OASIS AI Solutions, Collingwood Ontario
> **Entity:** Sole Proprietor (Ontario) — CCPC incorporation planned at $80K+ sustained revenue
> **Current MRR:** ~$2,982 USD (~$4,100 CAD) | **ARR:** ~$35,784 USD (~$49,200 CAD)
> **Revenue Split:** Bennett $2,500 + 15% rev share (~94%), Stripe $100 (~6%)
> **Target:** $15K-$20K USD MRR by December 2026
> **Last Updated:** 2026-03-27
> **Companion Docs:** ATLAS_AI_SAAS_TAX_GUIDE.md (tax treatment), ATLAS_BOOKKEEPING_SYSTEMS.md (accounting ops),
> ATLAS_INCORPORATION_TAX_STRATEGIES.md (CCPC planning)

**This document is NOT about tax treatment of SaaS revenue.** It is about the financial operations, metrics,
pricing, cash flow management, and strategic decisions that a SaaS CFO needs to master. Tax-specific content
lives in ATLAS_AI_SAAS_TAX_GUIDE.md.

**Tags used throughout:**
- `[NOW]` — Actionable today at CC's current revenue and entity structure
- `[FUTURE]` — Relevant at $80K+ revenue, post-incorporation, or with a team
- `[OASIS]` — Specific to CC's actual business situation

---

## Table of Contents

1. [SaaS Metrics That Matter (The CFO Dashboard)](#1-saas-metrics-that-matter-the-cfo-dashboard)
2. [Revenue Recognition for SaaS (Accounting Rules)](#2-revenue-recognition-for-saas-accounting-rules)
3. [Pricing Strategy for AI SaaS](#3-pricing-strategy-for-ai-saas)
4. [Cash Flow Management for SaaS](#4-cash-flow-management-for-saas)
5. [Unit Economics Deep Dive](#5-unit-economics-deep-dive)
6. [Client Concentration Risk](#6-client-concentration-risk)
7. [Financial Projections and Modeling](#7-financial-projections-and-modeling)
8. [SaaS Valuation (What is OASIS Worth?)](#8-saas-valuation-what-is-oasis-worth)
9. [CFO Operations for Solo Founder](#9-cfo-operations-for-solo-founder)
10. [Scaling from Solo to Team](#10-scaling-from-solo-to-team)
11. [Fundraising vs Bootstrapping](#11-fundraising-vs-bootstrapping)
12. [CC-Specific SaaS CFO Action Plan](#12-cc-specific-saas-cfo-action-plan)

---

## 1. SaaS Metrics That Matter (The CFO Dashboard)

Every SaaS CFO manages the business through a small set of metrics that tell the full story of growth,
retention, efficiency, and health. If you only look at bank balance, you are flying blind. These are the
instruments on the cockpit dashboard.

### 1.1 MRR — Monthly Recurring Revenue (The North Star)

MRR is the single most important number in a SaaS business. It is the total predictable revenue you
collect every month from active subscriptions, normalized to a monthly figure.

**Formula:**
```
MRR = Sum of all active monthly subscription amounts
```

If a customer pays $12,000/year, their MRR contribution is $1,000/month — not $12,000 in the month
they paid.

**MRR Components (the five buckets):**
| Component | Definition | CC Example |
|-----------|-----------|------------|
| New MRR | Revenue from brand-new customers this month | A new Stripe subscriber at $50/mo |
| Expansion MRR | Revenue increase from existing customers (upsell, upgrade) | Bennett's rev share increases as Skool grows |
| Contraction MRR | Revenue decrease from existing customers (downgrade) | Bennett drops from $2,500 to $2,000 |
| Churned MRR | Revenue lost from customers who cancelled | A Stripe subscriber cancels |
| Reactivation MRR | Revenue from previously churned customers returning | A past client re-subscribes |

**Net New MRR = New + Expansion + Reactivation - Contraction - Churned**

`[OASIS]` CC's current MRR breakdown:
- Bennett: ~$2,882 USD ($2,500 flat + estimated $382 in 15% rev share)
- Stripe: ~$100 USD (2 subscribers)
- **Total MRR: ~$2,982 USD (~$4,100 CAD)**

**What good looks like:**
| Stage | MRR Range | What it signals |
|-------|-----------|----------------|
| Pre-Product/Market Fit | $0-$5K | Still validating. CC is here. |
| Early Traction | $5K-$25K | Product works, need to scale acquisition |
| Growth | $25K-$100K | Hire, systematize, potentially raise capital |
| Scale | $100K-$1M | Real company, institutional-grade operations |

### 1.2 ARR — Annual Recurring Revenue

ARR is simply MRR multiplied by 12. It is the standard metric used for SaaS valuation, benchmarking,
and board reporting.

```
ARR = MRR x 12
```

`[OASIS]` CC's current ARR: $2,982 x 12 = **$35,784 USD (~$49,200 CAD)**

ARR is the number investors, acquirers, and benchmarking platforms use. When someone asks "how big is
your SaaS," the answer is ARR.

**Caution:** Only count truly recurring revenue. One-time setup fees, consulting projects, or custom
builds are NOT ARR. Bennett's $2,500 flat is recurring (if contracted monthly). The 15% rev share is
variable and some analysts would exclude it from ARR or apply a discount. Conservative approach: count
the $2,500 flat as ARR, treat the rev share as variable revenue reported separately.

### 1.3 Net Revenue Retention (NRR) — The Most Important Growth Metric

NRR measures how much revenue you keep and grow from your existing customer base, excluding new
customers entirely. It answers: "If I stopped acquiring customers today, would my revenue grow or shrink?"

**Formula:**
```
NRR = (Starting MRR + Expansion - Contraction - Churned) / Starting MRR x 100%
```

**Benchmarks:**
| NRR | What it means |
|-----|---------------|
| < 80% | Leaky bucket. Customers are leaving faster than remaining ones grow. |
| 80-100% | Stable but not expanding. Revenue from existing customers is flat or declining. |
| 100-120% | Healthy. Existing customers are spending more over time. |
| 120%+ | Elite. Expansion revenue exceeds all losses. Twilio, Snowflake, Datadog territory. |

**Why NRR is king:** A SaaS business with 130% NRR doubles its revenue from existing customers every
~2.5 years, even if it never acquires a single new customer. This is the compounding engine of SaaS.

`[OASIS]` CC cannot meaningfully calculate NRR yet with only 3 customers. But the structure is right:
Bennett's rev share component means expansion is built into the contract (as Skool grows, CC earns more).
This is a natural NRR booster. Once CC has 10+ customers, NRR becomes the metric to obsess over.

### 1.4 Gross Revenue Retention (GRR) — The Floor

GRR strips out expansion revenue. It only measures how much existing revenue you keep, not how much
you grow it. It is always <= 100%.

```
GRR = (Starting MRR - Contraction - Churned) / Starting MRR x 100%
```

**Benchmarks:**
| GRR | What it means |
|-----|---------------|
| < 80% | Serious retention problem. Product or market fit issue. |
| 80-90% | Average for SMB SaaS. Acceptable but needs improvement. |
| 90-95% | Good. Strong product-market fit. |
| 95%+ | Excellent. Enterprise-grade retention. |

GRR is the floor of your business. If GRR is 70%, you lose 30% of revenue every year just from existing
customers — you need massive new acquisition just to stay flat.

### 1.5 Churn Rate: Customer Churn vs Revenue Churn

These are different metrics and you must track both.

**Customer churn (logo churn):**
```
Customer Churn Rate = Customers lost this month / Customers at start of month x 100%
```

**Revenue churn (MRR churn):**
```
Gross MRR Churn Rate = (Contraction MRR + Churned MRR) / Starting MRR x 100%
Net MRR Churn Rate = (Contraction + Churned - Expansion) / Starting MRR x 100%
```

**Why they differ:** If you lose 5 small customers ($50/mo each = $250 total) but your one enterprise
customer expands by $500/mo, your customer churn is terrible but your net revenue churn is negative
(which is good — you grew).

**Benchmarks:**
| Metric | Good | Great | Elite |
|--------|------|-------|-------|
| Monthly customer churn | < 5% | < 3% | < 1% |
| Monthly gross MRR churn | < 3% | < 1.5% | < 0.5% |
| Annual gross MRR churn | < 30% | < 15% | < 5% |
| Net revenue churn | Negative | Negative | Very negative |

Negative net revenue churn means expansion exceeds losses. This is the goal.

`[OASIS]` With 3 customers, losing Bennett = 94% churn. This is not a churn rate problem — it is a
concentration risk problem (covered in Section 6).

### 1.6 ARPU — Average Revenue Per User

```
ARPU = MRR / Total active customers
```

`[OASIS]` CC's ARPU: $2,982 / 3 = **$994/customer/month** (or $1,441 if counting Bennett as $2,882).

This is extremely high ARPU for a micro-SaaS. The Stripe-only customers at $50/mo drag it down, but
Bennett at $2,882/mo pulls it way up. High ARPU is not inherently bad — enterprise SaaS companies
(Salesforce, Snowflake) have $100K+ ARPU. The problem is when high ARPU comes from concentration
in one customer.

**ARPU tells you your market positioning:**
| ARPU Range | Market Segment | Sales Motion |
|-----------|---------------|-------------|
| $10-$50/mo | Consumer / prosumer | Self-serve, freemium, PLG |
| $50-$500/mo | SMB | Low-touch sales, content marketing |
| $500-$5,000/mo | Mid-market | Inside sales, demos |
| $5,000+/mo | Enterprise | Field sales, custom deals, long cycles |

CC's Stripe customers ($50/mo) are SMB. Bennett ($2,882/mo) is mid-market. The question is: does CC
want more Bennetts or more $50/mo self-serve customers? The answer shapes the entire go-to-market
strategy. (More on this in Section 3.)

### 1.7 LTV — Lifetime Value

LTV estimates the total revenue a customer will generate over their entire relationship with you.

**Simple formula:**
```
LTV = ARPU x Average Customer Lifespan (months)
```

**Margin-adjusted formula (more accurate):**
```
LTV = ARPU x Gross Margin % / Monthly Churn Rate
```

Example with CC's numbers (assuming 5% monthly churn for SMB segment):
```
LTV (Stripe customer) = $50 x 80% / 0.05 = $800
LTV (Bennett-type client) = $2,882 x 85% / 0.02 = $122,485
```

The margin-adjusted formula shows why enterprise clients are so valuable: they churn less (2% vs 5%)
and pay more. One Bennett is worth 153 Stripe subscribers in LTV terms.

### 1.8 CAC — Customer Acquisition Cost

CAC is the total cost to acquire one new paying customer.

```
CAC = Total Sales & Marketing Spend / New Customers Acquired
```

Include: ads, content creation costs, sales salaries, tools (CRM, email), conference tickets, free trials
that cost you money (API costs during trial), and CC's own time valued at a reasonable hourly rate.

`[OASIS]` CC's current CAC is effectively $0 in hard costs — Bennett came through a personal relationship,
Stripe subscribers likely through word-of-mouth. But CC's time is not free. If CC spent 20 hours on
sales activities at $100/hr imputed cost, that is $2,000 in CAC spread across customers acquired.

**Why CAC matters:** If it costs $5,000 to acquire a customer who generates $800 in LTV, the business
loses money on every sale. You must know CAC to know if your growth is profitable.

### 1.9 LTV:CAC Ratio — The Efficiency Test

```
LTV:CAC Ratio = Customer LTV / CAC
```

**Benchmarks:**
| Ratio | Interpretation | Action |
|-------|---------------|--------|
| < 1:1 | Losing money on every customer | Stop. Fix product or pricing. |
| 1:1 - 3:1 | Marginal. Barely breaking even on acquisition. | Optimize funnel and pricing. |
| 3:1 | Healthy. Industry standard target. | Maintain and scale. |
| 5:1+ | Either very efficient or under-investing in growth | Spend more on acquisition. |
| 10:1+ | Massively under-investing in growth | Aggressively scale marketing spend. |

`[OASIS]` CC is likely at 10:1+ because CAC is near-zero. This means CC should be spending more on
customer acquisition — the economics support it.

### 1.10 CAC Payback Period

How many months until a customer's gross profit covers the cost of acquiring them.

```
CAC Payback = CAC / (ARPU x Gross Margin %)
```

**Benchmarks:**
| Payback | Assessment |
|---------|-----------|
| < 6 months | Excellent. Fast capital recovery. |
| 6-12 months | Good. Standard for SMB SaaS. |
| 12-18 months | Acceptable for mid-market. |
| 18-24 months | Enterprise only. Requires strong retention. |
| 24+ months | Dangerous unless NRR is very high. |

Short payback = more cash to reinvest in growth. Long payback = you need outside capital to fund growth
because you are laying out cash years before you recover it.

### 1.11 Rule of 40

The Rule of 40 is the standard benchmark for balancing growth and profitability in SaaS.

```
Rule of 40 Score = Revenue Growth Rate (%) + Profit Margin (%)
```

If your revenue is growing 50% YoY and your profit margin is -10%, your score is 40. The Rule of 40
says this combination is healthy — you are burning cash to grow fast.

If revenue grows 10% and profit margin is 20%, your score is 30. You are profitable but not growing.
Below 40 total means you are neither growing fast enough nor profitable enough.

**For CC at this stage:** Growth rate matters far more than margin. A solo founder with ~90% margins
and any reasonable growth rate will crush the Rule of 40. CC's focus should be 100% on growth rate —
profitability is already built into the model because there are almost no costs.

### 1.12 Burn Multiple

```
Burn Multiple = Net Cash Burn / Net New ARR
```

Burn multiple measures how efficiently you convert cash into new revenue. Lower is better.

| Burn Multiple | Interpretation |
|--------------|---------------|
| < 1x | Amazing. You are adding more ARR than you are burning. |
| 1-1.5x | Great. Very capital efficient. |
| 1.5-2x | Good. Normal for growth-stage. |
| 2-3x | Mediocre. Need to improve efficiency. |
| 3x+ | Burning cash inefficiently. Fix sales or reduce spend. |

`[OASIS]` CC is not burning cash (sole proprietor, minimal expenses), so burn multiple is near 0.
This is the advantage of bootstrapping — every dollar of new revenue is essentially free.

### 1.13 SaaS Quick Ratio

```
SaaS Quick Ratio = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)
```

This measures how healthy your growth is. Are you filling a leaky bucket or building on a solid base?

| Quick Ratio | Interpretation |
|------------|---------------|
| < 1 | Shrinking. Losses exceed gains. |
| 1-2 | Struggling. Growing but fragile. |
| 2-4 | Healthy. Good balance of growth and retention. |
| 4+ | Excellent. Strong growth with minimal losses. |

`[OASIS]` CC's quick ratio is infinite right now (no churn, only new/expansion). That will change as
the customer base grows. Track this monthly once you have 10+ customers.

### 1.14 The CFO Dashboard — What to Track Weekly

`[NOW]` Set up a simple spreadsheet (or Stripe dashboard) tracking:

| Metric | Frequency | CC's Current Value |
|--------|-----------|-------------------|
| MRR | Weekly | $2,982 USD |
| ARR | Monthly | $35,784 USD |
| Net New MRR | Monthly | Track starting now |
| Customer Count | Weekly | 3 |
| ARPU | Monthly | $994/customer |
| Churned MRR | Monthly | $0 (so far) |
| Revenue by Customer | Monthly | Bennett 94%, Stripe 6% |
| Cash Balance | Weekly | ~$1,900 USD |
| Runway | Monthly | Infinite (no burn) |

---

## 2. Revenue Recognition for SaaS (Accounting Rules)

Revenue recognition determines when revenue shows up on your income statement. For SaaS, this is more
nuanced than "money hits the bank."

### 2.1 ASPE vs IFRS for Canadian Private Companies

Canadian private companies have a choice:

| Framework | Who Uses It | Complexity | CC's Choice |
|-----------|------------|-----------|-------------|
| **ASPE** (Accounting Standards for Private Enterprises) | Most Canadian small/mid private companies | Moderate | This one. |
| **IFRS** (International Financial Reporting Standards) | Public companies, some private by choice | High | Only if pursuing institutional funding or acquisition by a public company. |

**ASPE Section 3400 (Revenue):** Revenue is recognized when:
1. Performance is achieved (service delivered)
2. Measurable (you know the dollar amount)
3. Collectibility is reasonably assured (customer will actually pay)
4. Risks and rewards have transferred

For a SaaS subscription, performance is achieved ratably over the subscription period — not at the
moment of billing.

`[FUTURE]` If CC incorporates as a CCPC and uses an accountant, ASPE is standard. Only switch to
IFRS if (a) pursuing VC funding from international investors who want IFRS, or (b) planning an IPO
or acquisition by a public company.

### 2.2 When to Recognize SaaS Subscription Revenue

**Monthly billing:** Simple. Bill $100 on March 1, recognize $100 of revenue in March.

**Annual billing:** More complex. Bill $1,200 on January 1 for a 12-month subscription.
- January cash in: $1,200
- January revenue recognized: $100
- January deferred revenue (liability): $1,100
- Each subsequent month: recognize $100, reduce deferred revenue by $100
- December 31: $0 deferred revenue remaining

**Why this matters for tax:** Under ASPE/CRA rules, if you receive annual payments, you cannot just
claim all $1,200 as revenue on day one (well, under s.12(1)(a) you technically must include it, but
s.20(1)(m) allows a reserve — see ATLAS_AI_SAAS_TAX_GUIDE.md Section 1 for the detailed mechanics).

### 2.3 Deferred Revenue (The Liability on Your Balance Sheet)

Deferred revenue is money you have received but have not yet earned. It is a **liability**, not revenue.

When a customer pays $12,000 upfront for a year:
```
Day 1:  Cash +$12,000  |  Deferred Revenue (liability) +$12,000
Month 1: Deferred Revenue -$1,000  |  Revenue +$1,000
Month 2: Deferred Revenue -$1,000  |  Revenue +$1,000
...
Month 12: Deferred Revenue -$1,000  |  Revenue +$1,000  |  Deferred Revenue = $0
```

**Why deferred revenue is actually good:** A large deferred revenue balance means customers have
pre-committed. It is future revenue that is already paid for. High-growth SaaS companies often have
millions in deferred revenue — it is a sign of strength, not debt.

`[OASIS]` CC's current billing is monthly, so deferred revenue is minimal. If CC moves to annual
billing (recommended — see Section 4), deferred revenue will grow and needs proper tracking.

### 2.4 Annual vs Monthly Billing — Cash Flow vs Revenue Timing

| Billing Type | Cash Flow Impact | Revenue Impact | Discount Offered |
|-------------|-----------------|---------------|-----------------|
| Monthly | Steady but slow | Recognized monthly | None |
| Quarterly | Lumpy, 3 months ahead | Recognized over 3 months | 5-10% |
| Annual | Big upfront, 12 months ahead | Recognized over 12 months | 15-20% (2 months free) |

**The annual billing advantage:**
- You collect 12 months of cash on day one
- Customer is locked in (lower churn — switching cost is psychological)
- You can invest that cash while delivering the service over time
- Reduces payment failure risk (credit card expiry, payment disputes)

**The trade-off:** You give a discount (typically 2 months free = 16.7% off) in exchange for cash
certainty. For a company like OASIS with near-zero marginal cost, this is almost always worth it.

`[OASIS]` CC should offer annual billing at a 15-17% discount as soon as MRR stabilizes. A $2,500/mo
client paying annually at 17% discount = $24,900 upfront instead of $30,000 over 12 months. CC gets
$24,900 in cash today. The $5,100 "discount" is the cost of cash certainty and reduced churn.

### 2.5 Implementation/Setup Fees

If CC charges a one-time setup or onboarding fee (common for AI SaaS), the accounting treatment depends
on whether the setup has standalone value.

**If setup has standalone value** (customer could use it without subscribing): recognize immediately.

**If setup only has value with the subscription** (it is just onboarding): amortize over the expected
customer lifespan or the initial contract period.

`[OASIS]` If CC charges $5,000 to build a custom AI automation and $500/mo for ongoing SaaS access,
the $5,000 is likely a separate deliverable (standalone value) and recognized at completion. If the
$5,000 is just "getting set up on the platform," amortize it.

### 2.6 Revenue Share Accounting (Bennett's 15% Rev Share)

Bennett's deal: $2,500 flat + 15% revenue share of the Skool community.

**How to account for this:**
- The $2,500 flat is straightforward subscription revenue
- The 15% rev share is variable consideration — recognized when the amount is determinable (when
  Skool revenue for the period is known)
- CC should receive a statement from Bennett (or access Skool analytics) showing total community
  revenue, then apply 15% to determine the rev share amount
- The rev share is recognized in the period it relates to, not when cash is received

**Journal entry (monthly):**
```
Debit: Accounts Receivable - Bennett     $2,882
  Credit: SaaS Subscription Revenue        $2,500
  Credit: Revenue Share Revenue              $382  (15% of estimated Skool revenue)
```

`[NOW]` CC should ensure the rev share is documented in a written agreement specifying:
- How Skool revenue is calculated (gross vs net)
- When the rev share is reported (monthly, quarterly)
- Payment terms (net-15, net-30)
- Audit rights (can CC verify the Skool revenue numbers?)

### 2.7 Multi-Element Arrangements

If CC sells a package that includes SaaS + consulting + custom development + support, each element
should be separated and recognized according to its own rules.

| Element | Recognition | Typical Approach |
|---------|------------|-----------------|
| SaaS subscription | Ratably over subscription period | Monthly as service delivered |
| Custom development | On delivery/milestones | Percentage of completion or completed contract |
| Consulting hours | As hours delivered | Time and materials |
| Support (included in SaaS) | Ratably with SaaS | Part of subscription price |
| Training (one-time) | On delivery | When training is completed |

`[OASIS]` CC should separate invoices or at minimum line-item the components. This matters for:
1. Accurate MRR tracking (only the subscription portion is MRR)
2. Tax treatment (different recognition rules)
3. Valuation (acquirers value recurring revenue much higher than services)

### 2.8 ITA Revenue Rules (Summary — Detail in ATLAS_AI_SAAS_TAX_GUIDE.md)

| ITA Section | Rule | SaaS Impact |
|------------|------|-------------|
| s.9(1) | Business income = profit therefrom | Accrual basis, not cash basis |
| s.12(1)(a) | Include amounts receivable for services | Must include even if not yet earned |
| s.20(1)(m) | Reserve for unearned revenue | Deduct the unearned portion (key deferral) |
| s.12(1)(e) | Prior year reserves added back | Last year's reserve reversed, new one claimed |

Full mechanics of s.20(1)(m) reserve in `ATLAS_AI_SAAS_TAX_GUIDE.md`, Section 1.

---

## 3. Pricing Strategy for AI SaaS

Pricing is the single highest-leverage decision in a SaaS business. A 10% price increase flows
directly to the bottom line with zero additional cost. Most founders underprice by 30-50%.

### 3.1 Value-Based Pricing (Not Cost-Plus, Not Competitor-Based)

**Cost-plus pricing** (your costs + margin) makes no sense for SaaS. The marginal cost of serving one
more customer is near $0, so cost-plus would price the product at almost nothing.

**Competitor-based pricing** (match what others charge) ignores your unique value proposition. If CC's
AI automation saves a client $50,000/year, pricing it at $500/mo because a competitor charges that
is leaving massive money on the table.

**Value-based pricing** (price based on the value you create for the customer) is the correct approach:

```
Maximum price = Customer's value received
Minimum price = Your cost to deliver
Optimal price = 10-25% of the value created for the customer
```

If CC's AI automation saves Bennett 20 hours/week and Bennett values his time at $100/hr:
```
Annual value to Bennett: 20 hrs x $100 x 52 weeks = $104,000
10% of value = $10,400/year = $867/month
25% of value = $26,000/year = $2,167/month
```

Bennett is paying $2,500/mo flat, which is about 29% of this estimated value. That is at the high
end but acceptable if the value is real and measurable. The 15% rev share adds more, which could push
total compensation to 35-40% of value — this is fine for a high-touch, critical service.

### 3.2 Pricing Models for AI SaaS

| Model | How It Works | Best For | Risk |
|-------|-------------|----------|------|
| **Flat rate** | $X/month, same for everyone | Simple products, early stage | Underprices big customers, overprices small ones |
| **Per-seat** | $X/user/month | Collaboration tools, team products | Revenue scales with customer's team size |
| **Usage-based** | Pay per API call, per generation, per action | AI/ML products, infrastructure | Revenue volatile, hard to predict MRR |
| **Tiered** | Good/Better/Best packages | Most SaaS | Price anchoring works, clear upsell path |
| **Hybrid** | Base subscription + usage overage | AI SaaS (best model) | Complexity in billing |

**Recommendation for OASIS:** Hybrid model — a base subscription (predictable MRR) with usage-based
overage for heavy use (captures value from power users).

Example OASIS pricing structure:
```
Starter:    $497/mo  — 1,000 AI automations/mo, email support, 1 user
Growth:     $997/mo  — 5,000 AI automations/mo, priority support, 5 users
Enterprise: $2,497/mo — Unlimited, dedicated support, custom integrations, SLA
Custom:     $5,000+/mo — White-glove, custom AI development, account manager
```

### 3.3 Price Anchoring with 3-Tier Pricing

The psychology: people avoid the cheapest option (feels inadequate) and the most expensive (feels risky).
They gravitate to the middle. This is why 3-tier pricing works:

```
Tier 1 (Starter):    $497/mo  — The "decoy" that makes middle look good
Tier 2 (Growth):     $997/mo  — The "target" — this is what you want people to buy
Tier 3 (Enterprise): $2,497/mo — The "anchor" — makes the middle feel like a deal
```

**Design the middle tier to be the obvious choice.** Give it 80% of the enterprise features at 40%
of the price. The enterprise tier should include high-touch elements (dedicated support, SLA, custom
work) that justify the premium.

### 3.4 Annual Discount Strategy

Industry standard: offer 2 months free for annual commitment = 16.7% discount.

```
Monthly: $997/mo x 12 = $11,964/year
Annual:  $997/mo x 10 = $9,970/year (save $1,994 = 16.7% off)
```

**Why this works for CC:**
- Cash upfront (12 months of cash on day 1)
- Lower churn (annual customers churn at ~5-10%/year vs 3-7%/month for monthly)
- Better forecasting (locked in for 12 months)
- The "discount" costs CC almost nothing because marginal cost is ~$0

`[NOW]` Offer annual pricing on the Stripe subscription page. Display both options with the savings
highlighted.

### 3.5 Enterprise Pricing

Once CC targets clients at $5,000+/mo:
- Custom quotes (never publish enterprise pricing on the website)
- Minimum 12-month contract with annual prepayment
- SOWs (Statements of Work) for custom development
- Net-30 invoicing (enterprises pay slow — budget for this)
- Multi-year discounts for 2-3 year commitments

Enterprise sales have longer cycles (3-6 months) but dramatically higher LTV. One enterprise client
at $10,000/mo = 200 self-serve clients at $50/mo. But enterprise requires a real sales process —
demos, proposals, procurement, legal review, security questionnaires.

### 3.6 Usage-Based Pricing for AI

AI SaaS has a unique cost structure: API calls to LLMs (Anthropic Claude, OpenAI) cost real money
per request. Unlike traditional SaaS where marginal cost is near-zero, AI SaaS has meaningful COGS.

**Strategies to handle AI costs:**
1. **Include a usage cap in each tier** (1,000 / 5,000 / unlimited automations)
2. **Charge overage** ($0.05 per automation beyond the cap)
3. **Charge per seat + usage** ($200/user/mo + $0.03/API call)
4. **Set a cost ceiling** (if API costs exceed X% of revenue per customer, throttle or upsell)

`[OASIS]` CC should track Anthropic API costs per customer per month. If any customer's API cost
exceeds 20% of their subscription, that customer is underpriced and needs to be upsold or moved to
a higher tier.

### 3.7 Free Tier / Freemium — When It Makes Sense

| Approach | When It Works | When It Fails |
|----------|-------------|--------------|
| **No free tier** | High ARPU, enterprise focus, complex product | Loses viral growth potential |
| **Free trial (14 days)** | Product shows value quickly, easy onboarding | Trial too short = low conversion |
| **Freemium (free forever, limited)** | Large TAM, self-serve, viral potential | Small TAM, high COGS |

`[OASIS]` At CC's stage (3 customers, high-touch sales), a free trial makes more sense than freemium.
Offer a 14-day free trial with full features, then convert to paid. Freemium makes sense later when
CC has a self-serve product and wants volume.

### 3.8 Price Increase Cadence

SaaS companies should raise prices annually. Most founders are terrified to do this. Data shows:
- Price increases of 5-10% annually have < 1% incremental churn
- Most customers do not notice or care
- New customers get the new price automatically; existing customers get a 30-60 day notice

**Best practices:**
- Give 60 days notice via email ("Starting [date], your plan will increase to $X/mo")
- Explain what is new ("We have added X, Y, Z features since you joined")
- Grandfather loyal customers for 1 year if needed (optional goodwill gesture)
- Never apologize for price increases. It signals the product is growing in value.

### 3.9 CC's Current Pricing Analysis

`[OASIS]` Bennett pays $2,500/mo + 15% rev share. Analysis:

**Pros of this structure:**
- $2,500 flat provides predictable base revenue
- 15% rev share aligns incentives (CC earns more when Bennett earns more)
- High ARPU relative to effort if the product is automated

**Cons:**
- The rev share makes total compensation unpredictable
- If Skool community revenue spikes, the 15% could become very large — does Bennett cap it?
- If Skool community revenue drops, CC's income drops with it
- 94% concentration in one client means any pricing renegotiation is existential

**Recommendation:** Keep Bennett's deal as-is (do not rock the boat). But for new clients, use a
clean subscription model without rev share. Rev share creates complexity, unpredictability, and
accounting headaches. A flat $2,500-$5,000/mo subscription is simpler and more scalable.

---

## 4. Cash Flow Management for SaaS

Cash is oxygen. Revenue is not cash. You can be profitable on paper and still run out of cash. SaaS
businesses have a unique cash flow dynamic: if you grow fast with monthly billing, you spend money to
acquire customers months before they pay back the CAC. Annual billing solves this.

### 4.1 Monthly Cash Flow Projection Template

`[NOW]` CC should build a simple monthly cash flow projection:

```
MONTHLY CASH FLOW PROJECTION — OASIS AI Solutions

CASH IN:
  Bennett flat                          $2,500
  Bennett rev share (estimated)           $382
  Stripe subscription revenue             $100
  Other income (consulting, one-time)       $0
  ──────────────────────────────────────────────
  Total Cash In                         $2,982

CASH OUT:
  Anthropic API (Claude)                  $50   (estimate — track actual)
  Hosting (Vercel/AWS/etc)                $20
  Stripe fees (2.9% + $0.30 per txn)     $90   (on $2,982)
  Wise fees (FX conversion)              $30
  Software subscriptions                  $50   (tools, domains, etc.)
  Marketing/ads                           $0
  Contractor payments                     $0
  Personal draws (CC's living expenses)  TBD
  Tax provision (25% of net income)     $680   (set aside, do not spend)
  ──────────────────────────────────────────────
  Total Cash Out                         $920 + personal draws + tax provision

NET CASH FLOW = Cash In - Cash Out
```

### 4.2 Billing Timing

| Billing Approach | Cash Flow Impact | Risk |
|-----------------|-----------------|------|
| Prepaid annual | Best. 12 months of cash upfront. | Customer wants a refund? |
| 1st of month | Clean, predictable. Industry standard. | Payment failures early in month. |
| Net-15 | Good for enterprise. 15 days to pay. | Minor delay. |
| Net-30 | Enterprise standard. 30 days to pay. | Significant cash delay. Requires AR tracking. |
| Net-60 | Large enterprise. 60 days to pay. | Do not do this unless the contract is huge. |

`[OASIS]` CC should bill on the 1st of every month for Stripe subscriptions. For Bennett (Wise),
establish a consistent billing date. Late payments should trigger automated reminders at Day 3,
Day 7, and Day 14.

### 4.3 Payment Processing Costs

| Processor | Fee | CC's Monthly Cost |
|-----------|-----|-------------------|
| Stripe | 2.9% + $0.30 per transaction | ~$90 on $2,982 (3 transactions) |
| Wise | 0.41-1.5% FX + $0-$3 per transfer | ~$30 on Bennett transfers |
| Total payment processing | ~3-4% of revenue | ~$120/month |

**Stripe optimization tips:**
- Stripe invoicing (0.4% on top of standard fees) — avoid if possible, use subscriptions directly
- Annual billing reduces per-transaction costs (one $12,000 charge vs twelve $1,000 charges)
- Stripe volume discounts kick in at ~$80K/month processing — negotiate custom rates at that point

**Wise optimization:**
- Have Bennett pay in USD to CC's Wise USD account (avoid FX conversion)
- Only convert to CAD when CC needs CAD for expenses (batch conversions, pick good rates)
- Wise business account has lower fees than personal

### 4.4 Cash Conversion Score

```
Cash Conversion Score = Operating Cash Flow / EBITDA
```

A score of 1.0 means every dollar of EBITDA turns into cash. SaaS companies with annual prepayment
can have scores > 1.0 (they collect cash before earning the revenue).

`[OASIS]` CC's cash conversion is currently ~1.0 (monthly billing, minimal deferred revenue). Moving
to annual billing would push this above 1.0.

### 4.5 Runway Calculation

```
Runway (months) = Total Cash / Monthly Net Burn Rate
```

If monthly burn is $0 (CC has no employees, minimal costs, lives with parents), runway is infinite.
This is a massive advantage. Most SaaS founders are burning $10K-$50K/month on salaries and rent.
CC burns almost nothing.

`[OASIS]` CC's runway: infinite (no meaningful burn). This means CC can be patient with growth, take
risks on product development, and never make desperate decisions for cash. Protect this advantage.

However, CC should still maintain an emergency cash reserve of 3 months of personal expenses.
If CC spends ~$1,500/month on living, that is $4,500 in a savings account that is never touched.

### 4.6 Cash Float Strategy

If CC moves to annual billing and collects, say, $50,000 in annual prepayments, that cash sits in the
bank while CC delivers the service over 12 months. In the meantime, that cash can be invested short-term.

**Safe options for deferred revenue float:**
- High-interest savings account (Wealthsimple Cash 4%, EQ Bank 4%)
- GICs (1-12 month terms matching revenue recognition schedule)
- **Never** put deferred revenue in risky investments — this is money you owe to customers in the
  form of future service delivery

At $50,000 in deferred revenue earning 4%: **$2,000/year in free money.** At $200,000: **$8,000/year.**

### 4.7 FX Impact (CC's USD Income, CAD Expenses)

`[OASIS]` CC earns in USD and spends in CAD. This creates FX exposure.

**Current dynamic:** USD/CAD has ranged from 1.33-1.39 in 2025-2026. At $2,982 USD/month:
- At 1.33 CAD/USD: $3,966 CAD
- At 1.39 CAD/USD: $4,145 CAD
- Difference: **$179 CAD/month or $2,148/year** just from FX fluctuation

**FX management strategy:**
1. Keep USD revenue in Wise USD account as long as possible
2. Convert to CAD in batches when the rate is favorable (not every transaction)
3. Set rate alerts on Wise (notify when USD/CAD > 1.38)
4. For tax purposes, use Bank of Canada daily rate on the date of each transaction (CRA requirement)
5. Report FX gains/losses on Schedule 3 or as part of business income

---

## 5. Unit Economics Deep Dive

Unit economics answer: "Do we make money on each customer?" If the answer is no, growth just accelerates
losses.

### 5.1 Gross Margin for SaaS

```
Gross Margin = (Revenue - Cost of Revenue) / Revenue x 100%
```

**SaaS gross margin benchmarks:**
| Margin | Assessment |
|--------|-----------|
| < 60% | Not really SaaS. More like a services company. |
| 60-70% | Acceptable for AI/ML companies with high compute costs. |
| 70-80% | Good. Standard for most SaaS. |
| 80-90% | Great. Low compute costs, automated delivery. |
| 90%+ | Elite. Minimal infrastructure costs. |

AI SaaS companies typically have lower gross margins (60-75%) than traditional SaaS (80-90%) because
of LLM API costs. This is a known investor concern. CC should monitor and optimize this.

### 5.2 Cost of Revenue (COGS) for AI SaaS

Cost of revenue includes everything directly tied to delivering the service:

| Cost Category | CC's Estimated Monthly Cost | Notes |
|--------------|---------------------------|-------|
| Anthropic Claude API | $30-$100 | Depends on usage volume |
| Hosting (Vercel/AWS/Railway) | $0-$50 | Free tier covers early stage |
| Third-party APIs | $0-$30 | Any other APIs CC uses |
| Customer support time | $0 | CC does this himself (but imputed cost is real) |
| **Total COGS** | **$30-$180** | |

`[OASIS]` CC's estimated gross margin:
```
Revenue:     $2,982/month
COGS:        ~$100/month (estimate)
Gross Profit: $2,882/month
Gross Margin: 96.6%
```

This is exceptional. Even if API costs scale to $500/month at $15K MRR, gross margin would be 96.7%.
AI SaaS gross margins can stay high if the AI does the work instead of humans.

**Caution:** If CC ever hires customer success or support staff, their salary is COGS and gross margin
drops significantly. A $50K/year support person on $180K ARR = 28% of revenue in COGS alone.

### 5.3 CC's Specific COGS Breakdown

`[NOW]` CC should track these monthly:

| Item | Monthly Cost | Annual Cost | % of Revenue |
|------|-------------|-------------|-------------|
| Anthropic API | $50-100 | $600-$1,200 | 1.7-3.4% |
| Hosting | $0-50 | $0-$600 | 0-1.7% |
| Domain/DNS | $2-5 | $24-$60 | <0.2% |
| Stripe fees | ~$90 | ~$1,080 | 3.0% |
| Wise fees | ~$30 | ~$360 | 1.0% |
| Software tools | $20-50 | $240-$600 | 0.7-1.7% |
| **Total** | **$192-$325** | **$2,304-$3,900** | **6.4-10.9%** |

**Gross margin after all direct costs: ~89-94%.** This is world-class.

### 5.4 Contribution Margin by Customer Segment

| Customer | Monthly Revenue | COGS (est.) | Contribution Margin | Margin % |
|----------|---------------|-------------|-------------------|----------|
| Bennett | $2,882 | $80 (API + Wise fees) | $2,802 | 97.2% |
| Stripe Client A | $50 | $5 (API + Stripe fees) | $45 | 90.0% |
| Stripe Client B | $50 | $5 (API + Stripe fees) | $45 | 90.0% |

Every customer is massively profitable. The Stripe clients have slightly lower margins because
Stripe's minimum per-transaction fee ($0.30) is a larger percentage of small transactions.

### 5.5 Marginal Cost of One Additional Customer

This is why SaaS businesses are so valuable:

```
Marginal cost of customer #4:
  Anthropic API usage increase:  ~$20/month
  Stripe per-transaction:        $0.30/transaction
  Wise per-transfer:             $0 (only if they pay via Stripe)
  Hosting increase:              ~$0 (capacity not exceeded)
  CC's time (onboarding):        ~5 hours one-time = $500 imputed
  ────────────────────────────────────
  Total marginal cost:           ~$20/month ongoing + $500 one-time
```

If customer #4 pays $500/month, the marginal profit is $480/month. Payback on the $500 onboarding
cost: ~1 month. This is the magic of SaaS — nearly all incremental revenue drops to the bottom line.

### 5.6 Why SaaS Businesses are Worth 5-15x Revenue

Traditional businesses trade at 1-3x revenue. SaaS trades at 5-15x. Why?

1. **Recurring revenue** — predictable cash flows that compound
2. **High gross margins** — 70-90%+ vs 20-50% for traditional businesses
3. **Low marginal cost** — serving one more customer costs almost nothing
4. **Network effects** — some SaaS products become more valuable with more users
5. **Switching costs** — once integrated, customers rarely switch (sticky)
6. **Scalability** — revenue grows exponentially while costs grow linearly

A SaaS business at $500K ARR with 85% gross margins, < 5% monthly churn, and 120% NRR might trade
at 10x ARR = **$5 million.** The same $500K in a consulting business trades at 1-2x = $500K-$1M.

This is why CC should categorize revenue as "SaaS" (recurring subscription) vs "services" (consulting,
custom development). The SaaS portion is worth 5-10x more per dollar than the services portion.

---

## 6. Client Concentration Risk (CC's #1 Financial Risk)

This is the most urgent section of this document. Client concentration is CC's single largest
financial risk — larger than market risk, tax risk, or operational risk.

### 6.1 The Problem: 94% from One Client

```
Bennett:     $2,882/mo = 94% of revenue
Stripe:        $100/mo =  6% of revenue
```

If Bennett leaves, CC's MRR drops from $2,982 to $100. That is a 97% revenue loss overnight.

This is not theoretical. Common reasons clients leave:
- Business closes or pivots
- Hires in-house developer to replace CC's automation
- Budget cuts
- Relationship deterioration
- Competitor offers a cheaper solution
- Key contact at Bennett's company leaves (if it is not Bennett himself)
- Bennett simply decides the Skool community is not worth continuing

**None of these require CC to do anything wrong.**

### 6.2 Industry Standards for Revenue Concentration

| Concentration Level | Assessment | Investor View |
|--------------------|-----------|--------------|
| No client > 10% | Excellent. Diversified. | Investable. |
| No client > 20% | Acceptable. | Fundable with conditions. |
| One client 20-50% | Concerning. | Requires concentration discount on valuation. |
| One client > 50% | High risk. | Most investors walk away. |
| One client > 80% | Critical risk. | Effectively a single contract, not a business. |
| **One client > 90%** | **Existential risk. CC is here.** | **Unfundable, unacquirable, uninsurable.** |

### 6.3 Herfindahl-Hirschman Index (HHI)

HHI is the standard measure of concentration used in antitrust and portfolio analysis. It is the sum
of squared market shares.

```
HHI = Sum of (each customer's revenue share)^2
```

**CC's HHI:**
```
HHI = (0.94)^2 + (0.03)^2 + (0.03)^2 = 0.8836 + 0.0009 + 0.0009 = 0.8854
```

HHI of 0.8854 (or 8,854 on the 10,000 scale) is extremely concentrated.

| HHI (10,000 scale) | Concentration Level |
|--------------------|-------------------|
| < 1,500 | Unconcentrated (healthy) |
| 1,500 - 2,500 | Moderately concentrated |
| > 2,500 | Highly concentrated |
| **8,854** | **CC — near-monopolistic concentration** |

**Target:** Get HHI below 2,500. This requires getting Bennett below 50% of revenue and having at
least 5-10 customers.

### 6.4 Mitigation Strategies

#### Strategy 1: Product-Led Growth (PLG)
Build a version of OASIS that customers can sign up for, use, and pay for without talking to CC.
Self-serve onboarding, credit card billing, no demos required.

- **Timeline:** 3-6 months to build
- **Impact:** Adds dozens of small customers ($50-$500/mo), diversifies revenue base
- **Risk:** Requires product development time that could go to client work

#### Strategy 2: Inbound Marketing Funnel
```
Content (blog, YouTube, LinkedIn) → Lead Magnet → Email Nurture → Demo → Close
```
Create content showing AI automation results. Capture emails. Nurture with case studies. Book demos.
Close deals. This is Bravo's domain (CEO agent), but Atlas tracks the financial impact.

- **Timeline:** 1-3 months for pipeline, 3-6 months for revenue impact
- **Impact:** 3-5 new clients at $500-$2,500/mo within 6 months
- **Cost:** CC's time + potentially $500-$1,000/mo in ads

#### Strategy 3: Strategic Partnerships and Referral Programs
Partner with agencies, consultants, or SaaS platforms that serve CC's target market. Offer 10-20%
referral commission on the first year of revenue.

- **Timeline:** 1-2 months to set up
- **Impact:** 1-3 new clients per quarter
- **Cost:** 10-20% of first-year revenue per referred client

#### Strategy 4: Vertical SaaS
Instead of being a general "AI automation" company, specialize in one industry (real estate, legal,
healthcare, e-commerce). Vertical SaaS companies have:
- Higher retention (industry-specific features are sticky)
- Higher ARPU (industry expertise commands premium pricing)
- Clearer marketing (speak the customer's language)

#### Strategy 5: White-Label / Reseller Model
Let other agencies resell OASIS under their own brand. CC provides the technology; partners provide
the client relationships. CC gets 60-70% of revenue, partner gets 30-40%.

- **Timeline:** 2-4 months to build reseller infrastructure
- **Impact:** Rapid client acquisition without CC doing direct sales
- **Risk:** Less control over customer experience and relationship

### 6.5 Revenue Diversification Timeline for CC

| Month | Bennett % | Target | How |
|-------|-----------|--------|-----|
| Now (Mar 2026) | 94% | Acknowledge the risk | Document and plan |
| May 2026 | 70-80% | Add 2-3 clients at $500-$1,000/mo | Outbound + referral |
| Aug 2026 | 50-60% | Add 3-5 more clients | Inbound funnel producing leads |
| Nov 2026 | 30-40% | 10+ clients, self-serve pipeline working | PLG + inbound + partnerships |
| Mar 2027 | < 20% | Healthy diversification | No client > 20% |

### 6.6 Scenario Planning: What If Bennett Leaves?

**Scenario: Bennett cancels with 30 days notice.**

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| MRR | $2,982 | $100 | -97% |
| ARR | $35,784 | $1,200 | -97% |
| Monthly cash in | $2,982 | $100 | Cannot cover expenses |
| Months to replace | N/A | 6-12 months | Estimated at current pipeline |

**Emergency plan if Bennett leaves:**
1. Immediately activate outbound sales (reach out to 50 potential clients in week 1)
2. Offer first 3 months at 50% discount to accelerate acquisition
3. Launch on Product Hunt / Indie Hackers / relevant communities
4. Consider taking contract/freelance work to bridge the gap
5. Apply for CSBFP working capital loan ($150K available) if cash runs out

`[NOW]` **Do not wait for this to happen.** Start diversifying now. The best time to find new clients
is when you do not desperately need them.

---

## 7. Financial Projections and Modeling

### 7.1 Bottom-Up Revenue Forecast

The bottom-up forecast starts with concrete inputs you can measure and control:

```
Monthly New Customers = Leads x Conversion Rate

Revenue Growth = (New Customers x ARPU) + Expansion MRR - Churned MRR
```

**CC's model inputs (estimate for planning):**

| Input | Conservative | Base Case | Optimistic |
|-------|-------------|-----------|-----------|
| Monthly leads (demos booked) | 5 | 10 | 20 |
| Demo-to-close rate | 15% | 25% | 35% |
| New customers/month | 0.75 | 2.5 | 7 |
| Average new customer ARPU | $500 | $1,000 | $2,000 |
| Monthly gross churn | 5% | 3% | 1% |

**12-month MRR projection from April 2026:**

| Month | Conservative | Base Case | Optimistic |
|-------|-------------|-----------|-----------|
| Apr 2026 | $3,357 | $5,482 | $11,982 |
| May 2026 | $3,564 | $7,567 | $20,244 |
| Jun 2026 | $3,761 | $9,490 | $28,022 |
| Jul 2026 | $3,948 | $11,185 | $35,541 |
| Aug 2026 | $4,126 | $12,849 | $42,683 |
| Sep 2026 | $4,295 | $14,363 | $49,604 |
| Oct 2026 | $4,455 | $15,802 | $56,277 |
| Nov 2026 | $4,607 | $17,128 | $62,722 |
| Dec 2026 | $4,752 | $18,364 | $68,954 |

The base case reaches CC's $15K-$20K MRR target by October-November 2026. This requires ~2.5 new
customers per month at $1,000 ARPU with 3% monthly churn. That is 10 demos/month closing 25%.

### 7.2 Top-Down TAM/SAM/SOM

| Market | Definition | Estimate for AI Automation SaaS |
|--------|-----------|-------------------------------|
| TAM (Total Addressable Market) | All businesses that could use AI automation | $50B+ globally |
| SAM (Serviceable Addressable Market) | SMBs in North America wanting AI automation | $5B |
| SOM (Serviceable Obtainable Market) | CC's realistic reach in 12-24 months | $2-5M |

TAM is useful for investor decks. SOM is useful for financial planning. CC should focus on SOM:
"How much of this market can I realistically capture with my current resources?"

If CC's SOM is $5M and OASIS captures 1%: $50K ARR. Captures 5%: $250K ARR. 10%: $500K ARR.

### 7.3 Cohort Analysis

Track how customer cohorts behave over time. A "cohort" is all customers who signed up in the same
month.

```
Example Cohort Table (% of original MRR retained):

         Month 0   Month 3   Month 6   Month 9   Month 12
Jan 26:   100%      90%       82%       76%       71%
Feb 26:   100%      88%       79%       —         —
Mar 26:   100%      92%       —         —         —
```

**What to look for:**
- Are newer cohorts retaining better? (Product improving)
- Are newer cohorts retaining worse? (Quality of customers declining, or product fit weakening)
- Where does the retention curve flatten? (The "natural retention floor")

`[FUTURE]` Start cohort tracking once CC has 3+ months of multi-customer data.

### 7.4 Scenario Modeling: Base, Bull, Bear

| Scenario | Assumptions | Dec 2026 MRR | Dec 2026 ARR |
|----------|-----------|-------------|-------------|
| **Bear** | Bennett leaves Q3, slow acquisition (1 new/mo at $500) | $3,000-$5,000 | $36K-$60K |
| **Base** | Bennett stays, 2-3 new clients/mo at $1,000 | $15,000-$18,000 | $180K-$216K |
| **Bull** | Bennett stays, 5+ new clients/mo at $1,500, enterprise deal | $25,000-$40,000 | $300K-$480K |

**CC's stated target of $15K-$20K MRR by December 2026 is the base case.** It requires consistent
sales effort (10+ demos/month) and product that sells. The bull case requires a sales hire or
partnership channel.

### 7.5 Key Assumptions to Validate Monthly

`[NOW]` Review these assumptions on the first of every month:

1. Is Bennett's contract still active? (Y/N — existential check)
2. How many leads came in this month? (Pipeline health)
3. What was the demo-to-close conversion rate? (Sales efficiency)
4. Did any existing customer churn or downgrade? (Retention health)
5. What is the average new customer ARPU? (Pricing power)
6. Are API costs growing faster than revenue? (Margin check)

If any assumption breaks, revise the financial model immediately.

### 7.6 Break-Even Analysis

```
Break-Even MRR = Total Monthly Fixed Costs / Gross Margin %
```

`[OASIS]` CC's fixed costs:
| Cost | Monthly |
|------|---------|
| Software subscriptions | $50 |
| Hosting | $20 |
| Phone/internet (business portion) | $30 |
| Personal expenses (rent, food, etc.) | $1,500 |
| Tax provision (estimated) | Variable |
| **Total fixed (personal + business)** | **~$1,600** |

Break-even MRR = $1,600 / 0.90 (90% gross margin) = **$1,778/month**

CC is already above break-even. OASIS is profitable. Every dollar above $1,778/month is profit.

---

## 8. SaaS Valuation (What is OASIS Worth?)

### 8.1 Revenue Multiples for Private SaaS

Private SaaS companies are typically valued as a multiple of ARR:

| ARR Range | Typical Multiple | What Drives It |
|-----------|-----------------|---------------|
| $0-$100K | 2-4x | Early stage, high risk |
| $100K-$500K | 3-6x | Product-market fit proven |
| $500K-$2M | 5-8x | Scaling, proven retention |
| $2M-$10M | 7-12x | Growth + retention + team |
| $10M+ | 10-20x | Enterprise-grade, IPO potential |

### 8.2 Factors That Increase Multiple

| Factor | Impact on Multiple | CC's Status |
|--------|-------------------|-------------|
| Revenue growth > 50% YoY | +2-3x | Strong (early stage growth) |
| NRR > 120% | +2-3x | Unknown (too few customers) |
| Monthly churn < 2% | +1-2x | 0% (but only 3 customers) |
| Gross margin > 80% | +1x | Yes (~90%+) |
| Annual contracts | +1x | No (monthly billing) |
| No client > 20% | +1-2x | **NO — 94% from one client** |
| Founder not required for delivery | +2-3x | Partially (AI does the work) |
| Growing market (AI) | +1-2x | Yes |

### 8.3 Factors That Decrease Multiple

| Factor | Impact on Multiple | CC's Status |
|--------|-------------------|-------------|
| Client concentration > 50% | -2-4x | **YES — critical** |
| Founder dependency | -1-3x | **YES — CC is the product** |
| Monthly billing only | -0.5-1x | Yes |
| No team | -1x | Yes |
| Services revenue mixed in | -1-2x | Partially (consulting mixed with SaaS) |
| Small ARR (< $100K) | -1-2x | Yes |

### 8.4 CC's Current Valuation Estimate

```
Current ARR: $35,784 USD
Base multiple for micro-SaaS: 3-4x
Concentration discount: -1.5x (94% one client)
Founder dependency discount: -0.5x
Applied multiple: 1-2x

Estimated value: $35,784 x 1.5 = ~$54,000 USD
```

Honestly, OASIS is not currently "valuable" as a sellable asset because of the Bennett concentration.
An acquirer would see a single contract, not a SaaS business. The 15% rev share further complicates
things (is that transferable?).

**However, the potential value is enormous.** If CC gets to:
```
$200K ARR, < 20% concentration, 90% margins, 120% NRR:
$200K x 6-8x = $1.2M - $1.6M valuation
```

### 8.5 Path to Meaningful Valuation

| Milestone | ARR | Multiple | Valuation |
|-----------|-----|----------|-----------|
| Today | $36K | 1.5x | $54K |
| After diversification (Bennett < 30%) | $60K | 3-4x | $180K-$240K |
| $100K ARR with 10+ customers | $100K | 4-5x | $400K-$500K |
| $250K ARR, NRR > 110%, low churn | $250K | 6-8x | $1.5M-$2M |
| $500K ARR, team of 3-5, enterprise clients | $500K | 8-10x | $4M-$5M |
| $1M ARR, strong metrics across the board | $1M | 10-12x | $10M-$12M |

### 8.6 SDE for MicroSaaS Valuation

SDE (Seller's Discretionary Earnings) is used for small businesses where the owner is the primary
operator. It adds back the owner's salary and discretionary expenses to the business profit.

```
SDE = Net Profit + Owner's Salary + Owner's Benefits + One-time Expenses + Discretionary Expenses
```

MicroSaaS acquisitions (marketplaces like Acquire.com, MicroAcquire) typically value at 3-5x SDE
or 3-6x annual profit.

`[OASIS]` CC's SDE (annualized):
```
Revenue:               $35,784
- COGS:                -$2,400
- Business expenses:   -$1,200
= Net Profit:          $32,184
+ Owner's salary addback: $0 (CC takes all profit)
= SDE:                 $32,184
Valuation at 3-4x SDE: $96K-$129K
```

### 8.7 Sell vs Hold Forever

**Sell when:**
- CC wants to start something new and needs capital
- The market for AI SaaS is peaking (sell into hype)
- An acquirer offers 10x+ and CC believes growth is slowing
- CC is burned out and wants to move on

**Hold when:**
- Revenue is compounding (NRR > 100%, growing customer base)
- Cash flow funds CC's lifestyle comfortably
- CC enjoys the work
- The CCPC structure provides tax advantages on retained earnings
- Building toward something bigger (platform, ecosystem)

**Atlas recommendation:** Hold. OASIS is early stage with massive growth potential. Selling now
captures $50K-$100K. Holding for 2-3 years could yield $1M-$5M+ in value, plus ongoing cash flow
plus CCPC tax advantages. Do not sell a compounding asset.

---

## 9. CFO Operations for Solo Founder

### 9.1 Monthly Close Process (5 Steps, 2 Hours)

`[NOW]` Perform this on the 1st-3rd of every month:

**Step 1: Reconcile Revenue (30 min)**
- Export Stripe revenue report (MRR, new, churned, expanded)
- Record Bennett payment from Wise
- Compare actual revenue to forecast — explain any variance

**Step 2: Reconcile Expenses (20 min)**
- Categorize all business expenses from the past month
- Match receipts to transactions (Dext/Hubdoc auto-capture if set up)
- Flag any uncategorized or unusual expenses

**Step 3: Update Cash Position (10 min)**
- Record balances: Wise USD, Wise CAD, RBC, Stripe pending payouts
- Calculate total available cash
- Update runway calculation (even if infinite — it is the habit)

**Step 4: Update KPI Dashboard (15 min)**
- MRR (total and by customer)
- Customer count
- ARPU
- Revenue concentration (Bennett %)
- Gross margin
- Cash balance

**Step 5: Forecast Update (15 min)**
- Is the financial model still on track?
- Any new assumptions to incorporate?
- What does next month look like?
- Any upcoming large expenses?

**Total: ~90 minutes.** Do this religiously. The discipline of a monthly close transforms a freelancer
into a business.

### 9.2 Quarterly Business Review (QBR)

`[NOW]` Every 3 months (March, June, September, December):

| Review Area | Questions to Answer |
|------------|-------------------|
| Revenue | Growth rate? Concentration improving? New customer traction? |
| Margins | Gross margin trending up or down? API costs growing faster than revenue? |
| Cash | Runway still healthy? Emergency reserve funded? Tax provision set aside? |
| Customers | NRR trend? Churn pattern? Expansion opportunities? |
| Pricing | Any customers underpriced? Time for a price increase? |
| Product | What features drive retention? What causes churn? |
| Growth | Is the acquisition funnel working? Where to invest next? |
| Risk | Client concentration? Single points of failure? Regulatory changes? |
| Tax | Quarterly installment due? HST filing due? Any tax-loss harvesting opportunity? |

### 9.3 KPI Dashboard — What to Track

| Metric | Frequency | Tool |
|--------|-----------|------|
| MRR | Weekly | Stripe dashboard or Baremetrics |
| ARR | Monthly | Calculated from MRR |
| Customer count | Weekly | Stripe |
| Revenue by customer | Monthly | Spreadsheet |
| ARPU | Monthly | Calculated |
| Gross margin | Monthly | Bookkeeping software |
| Churn (customer + revenue) | Monthly | Stripe or manual |
| NRR | Quarterly | Calculated |
| Cash balance | Weekly | Wise + RBC |
| Tax provision balance | Monthly | Separate savings account |
| Bennett concentration % | Weekly | Calculated |
| Pipeline (leads, demos) | Weekly | CRM or spreadsheet |

### 9.4 Bookkeeping Workflow

See `ATLAS_BOOKKEEPING_SYSTEMS.md` for the full T2125-aligned chart of accounts. Key workflow:

1. **Stripe** auto-deposits to **Wise USD** account
2. **Bennett** pays via Wise payment link to **Wise USD** account
3. CC converts USD to CAD via Wise when needed (batch, not per-transaction)
4. CC categorizes transactions weekly (15 min/week) in Wave or QBO
5. Receipts captured via phone (Dext app or email forwarding)
6. Monthly close reconciles everything (Step 1-5 above)

`[NOW]` If CC is not on Wave or QBO yet, set up Wave (free) today. Connect Stripe. Start categorizing.

### 9.5 Invoicing Best Practices

| Practice | Why |
|----------|-----|
| Use Stripe Billing for subscriptions | Automated, card on file, reduces late payments |
| Net-15 for enterprise invoices | Faster than net-30, still professional |
| Late payment terms in contract | "1.5% per month on overdue balances" — rarely enforced but motivates payment |
| Auto-reminders at Day 3, 7, 14 | Stripe handles this automatically for subscriptions |
| Annual prepayment discount | 15-17% off for paying 12 months upfront |

### 9.6 Tax Provision — The "Do Not Touch" Account

`[NOW]` CC should set aside **25-30% of net revenue** into a separate savings account labeled
"TAX — DO NOT TOUCH."

```
Monthly net revenue: $2,982
Tax provision (25%): $745.50/month → separate account

After 12 months: ~$8,946 set aside for tax
```

This ensures CC is never surprised by a tax bill. The actual tax rate may be lower (deductions,
credits), in which case the surplus becomes profit. But it is always better to over-provision than
to owe CRA with no cash to pay.

See `ATLAS_INSTALLMENT_PAYMENTS.md` for quarterly installment requirements once income exceeds
the s.156 threshold (~$3,000 net tax owing in current or either of two prior years).

### 9.7 Emergency Cash Reserve

`[NOW]` Build a reserve of 3 months of personal + business expenses:

```
Monthly personal expenses: ~$1,500
Monthly business expenses:   ~$300
Total monthly:              $1,800
3-month reserve:            $5,400
```

This is separate from the tax provision. It is CC's safety net if revenue drops suddenly (Bennett
scenario). Park it in a high-interest savings account (Wealthsimple Cash 4%, EQ Bank 4%).

Current status: CC has ~$1,900 USD in Wise. This is about 1 month of expenses. **Need to build
this to $5,400+ as soon as cash flow allows.**

---

## 10. Scaling from Solo to Team (Financial Considerations)

### 10.1 When to Hire: Employee vs Contractor

| Hire Type | When | Cost to CC | Obligations |
|-----------|------|-----------|-------------|
| **Contractor** | Project-based work, specialized skills, testing demand | Invoice amount only | T4A if > $500/year, no source deductions |
| **Employee** | Ongoing role, you control how/when/where they work | Salary + 15-20% overhead | CPP, EI, WSIB, income tax withholding, vacation pay, T4 |

**CRA employee vs contractor test** (from `ATLAS_AI_SAAS_TAX_GUIDE.md`):
- Control: Do you control how, when, where they work? → Employee
- Tools: Do you provide the tools? → Employee
- Financial risk: Do they bear financial risk? → Contractor
- Integration: Are they integrated into your business? → Employee
- Exclusivity: Do they only work for you? → Leans employee

**PSB (Personal Services Business) risk:** If CC hires a "contractor" who is really an employee,
CRA can reclassify them. The contractor loses all deductions and pays the highest tax rate. CC could
face penalties for not withholding. Be careful.

`[OASIS]` CC's first hire should probably be a **contractor** for specific tasks (UI design, content
creation, sales outreach). Only convert to employee when the role is ongoing (20+ hrs/week) and you
need control over how the work is done.

### 10.2 Payroll Obligations in Canada

`[FUTURE]` When CC hires an employee (likely post-incorporation):

| Obligation | Rate (2026 est.) | Employer Cost on $50K Salary |
|-----------|------------------|------------------------------|
| CPP (employer share) | 5.95% on $63,100 pensionable earnings | ~$2,975 |
| CPP2 (second ceiling) | 4% on next ~$5,000 | ~$200 |
| EI (employer share) | 1.4x employee rate = ~2.21% on $65,700 insurable | ~$1,105 |
| WSIB (Ontario) | 0.5-3%+ depending on industry classification | ~$500-$1,500 |
| Vacation pay | 4% minimum (Ontario ESA) | $2,000 |
| **Total employer overhead** | **~13-18% on top of salary** | **$6,780-$7,780** |

A $50,000 salary actually costs CC **$56,780-$57,780.** Budget 15-20% on top of every salary.

### 10.3 Contractor Payments

- **T4A filing:** Required if you pay a contractor $500+ in a calendar year
- **No source deductions:** Contractors handle their own CPP, EI, and income tax
- **HST:** If the contractor is registered for HST, they charge 13% on their invoices.
  CC can claim this as an ITC if OASIS is also HST-registered.
- **Written contract:** Always. Specify scope, deliverables, timeline, payment terms, IP ownership.

### 10.4 Remote Worker in Different Province

If CC hires an employee in, say, Alberta:
- **Payroll tax:** Withhold based on the employee's province of residence
- **WSIB/WCB:** Register in the employee's province (Alberta WCB, not Ontario WSIB)
- **ESA:** Follow the employment standards of the employee's province
- **CRA:** Employer account remains in Ontario, but withholding rates differ by province

This adds complexity. It is one reason to use contractors or a PEO (Professional Employer Organization)
like Remote.com or Deel for out-of-province or international hires.

### 10.5 Remote Worker in Different Country

| Issue | Risk | Mitigation |
|-------|------|-----------|
| Permanent Establishment (PE) | If worker performs core business functions in another country, CC may create a taxable PE there | Use contractors, not employees. Limit scope. |
| Withholding tax | Some countries require withholding on payments to foreign contractors | Check treaty network. Canada has 90+ tax treaties. |
| Employment law | Some countries deem contractors as employees regardless of contract | Use a PEO (Deel, Remote.com) to handle compliance. |
| Transfer pricing | If paying a related entity (e.g., CC's own Irish company), must be at arm's length rates | Document pricing methodology. See ATLAS_FOREIGN_REPORTING.md. |

`[OASIS]` CC should avoid hiring employees in other countries directly. Use contractor agreements
or a PEO. The compliance burden of international employment is enormous for a solo founder.

### 10.6 Co-Founder Equity Split

If CC takes a co-founder:
- 50/50 is standard for equal co-founders joining at the same time
- CC built OASIS alone, so any new co-founder should get less (20-35% with 4-year vesting)
- **Always vest.** 4-year vesting with 1-year cliff. If the co-founder leaves after 6 months, they
  get nothing. This protects CC.
- Use a shareholders' agreement drafted by a lawyer ($2,000-$5,000 well spent)
- Consider: does CC even need a co-founder? For AI SaaS, a solo founder with contractors may be
  more capital-efficient.

### 10.7 ESOP / Stock Options in CCPC

`[FUTURE]` Once incorporated as CCPC:

ITA s.7 provides a significant advantage for stock options in CCPCs:
- Employee exercises option → no immediate tax (deferred until shares sold)
- When shares sold → 50% inclusion rate (capital gains treatment) if certain conditions met
- **Combined effect:** employee pays ~25% effective tax on stock option gains instead of ~50%

This makes CCPC stock options extremely attractive for recruiting. It is one of the best talent
retention tools available to Canadian startups.

**Conditions for s.7 deferral:**
- Must be a CCPC at time of grant
- Shares must be prescribed shares (common shares qualify)
- Employee must deal at arm's length with the company
- Employee must not own > 10% of any class of shares

---

## 11. Fundraising vs Bootstrapping (CC's Decision)

### 11.1 Bootstrapping: Keep Everything

| Advantage | Detail |
|-----------|--------|
| 100% ownership | CC keeps all equity. No dilution. |
| No investor pressure | No board meetings, no growth targets imposed by others. |
| Full control | CC decides everything — pricing, product, hiring, direction. |
| Profitable from day one | No "grow at all costs" pressure. Sustainable. |
| No fundraising time sink | Raising money takes 3-6 months of full-time effort. |

| Disadvantage | Detail |
|-------------|--------|
| Slower growth | Limited by cash flow. Cannot hire 5 people tomorrow. |
| No network | Investors bring introductions, advisors, credibility. |
| All risk on CC | If it fails, CC absorbs 100% of the loss. |

### 11.2 Fundraising: Trade Equity for Speed

| Advantage | Detail |
|-----------|--------|
| Capital to hire and scale | Fund 12-18 months of burn to grow faster. |
| Investor network | Intros to customers, hires, partners. |
| Validation signal | "We raised $X" is social proof. |
| Shared risk | Investors bear some downside. |

| Disadvantage | Detail |
|-------------|--------|
| Dilution | A $500K seed round at $2M valuation = 25% gone. |
| Loss of control | Investors may have board seats, veto rights, preferences. |
| Growth pressure | Must hit milestones or risk down round / bridge. |
| Time cost | 3-6 months to fundraise = 3-6 months not building product. |

### 11.3 Revenue-Based Financing (No Dilution)

Companies like Clearco (formerly Clearbanc) and Lighter Capital offer financing based on revenue:

| Feature | Detail |
|---------|--------|
| How it works | Lend $X, repay as a % of monthly revenue until X + fee is repaid |
| Typical terms | 6-12% flat fee, repay 5-15% of monthly revenue |
| Amount | 3-6x monthly revenue ($9K-$18K for CC today) |
| Dilution | Zero |
| Speed | 1-2 weeks to fund |

**Good for:** Funding a specific growth initiative (ads, hire) with predictable ROI.
**Bad for:** Speculative investments or when revenue is volatile.

`[OASIS]` At CC's current MRR, the loan amount would be small ($9K-$18K). Wait until MRR is $10K+
to make this worthwhile. Use for a specific purpose: "I will spend $15K on ads that should generate
$5K/mo in new MRR."

### 11.4 Government Grants (Free Money)

See `ATLAS_GOVERNMENT_GRANTS.md` for the full playbook. Highlights for CC:

| Program | Amount | Type | CC Eligible? |
|---------|--------|------|-------------|
| **IRAP** (NRC Industrial Research Assistance) | Up to $500K | Grant (non-repayable) | Yes — AI/ML R&D |
| **Futurpreneur** | $20K grant + $40K BDC loan | Grant + Loan | Yes — under 39, new business |
| **Starter Company Plus** (Ontario) | $5,000 | Grant | Likely yes |
| **CSBFP** | Up to $1M | Government-backed loan | Yes |
| **Digital Main Street** | $2,500 | Grant | Check eligibility |
| **SR&ED** | 35% federal + 8% Ontario = 43% | Tax credit (refundable for CCPCs) | Yes, post-incorporation |

**Total accessible:** $200K-$500K+ in grants and subsidized financing.

`[NOW]` Apply for Futurpreneur and Starter Company Plus. These are the fastest to access and require
the least documentation. IRAP requires a more formal application but is the biggest prize.

### 11.5 CSBFP Business Loans

The Canada Small Business Financing Program is the single best loan program available:
- Up to **$1,000,000** total
- Government guarantees 85% (banks love this)
- 10% personal guarantee (not 100% like a normal business loan)
- Use for equipment, working capital, leasehold improvements

`[FUTURE]` Apply when CC needs capital for a specific purpose (office, equipment, working capital
for hiring). Do not borrow just because you can.

### 11.6 Angel Investors and SAFE Notes

If CC decides to raise:
- **SAFE (Simple Agreement for Future Equity):** Not a loan, not equity. It converts to equity at
  the next priced round. Standard in early-stage startup fundraising. YCombinator invented it.
- **Typical angel round:** $50K-$250K on a SAFE with $2M-$5M valuation cap
- **Where to find angels:** AngelList, local angel groups (Golden Horseshoe, York Angel Investors,
  MaRS), tech meetups, LinkedIn

**Key terms to understand:**
| Term | What It Means | CC's Interest |
|------|-------------|--------------|
| Valuation cap | Maximum valuation at which the SAFE converts | Higher = less dilution for CC |
| Discount | % discount on the next round's price | 15-25% typical |
| Pro-rata rights | Investor can maintain % ownership in future rounds | Standard |
| MFN (Most Favored Nation) | If CC gives a better deal later, early investor gets it too | Fair |

### 11.7 Atlas Recommendation: Bootstrap + Grants

**For CC specifically:**

1. **Bootstrap** — CC has infinite runway (low costs, lives with parents). Do not give up equity.
2. **Apply for grants** — Futurpreneur ($20K), Starter Company Plus ($5K), IRAP ($500K). Free money.
3. **Revenue-based financing** — Consider at $10K+ MRR if there is a specific growth investment.
4. **Angel investors** — Only if CC wants to grow aggressively AND needs specific expertise/network
   that the investor brings. Do not raise just for cash.

At 22 with a profitable SaaS, CC is in an enviable position. Most founders would kill for $3K MRR
with 90%+ margins and no burn. The worst thing CC could do is give away 25% of the company for
$250K that is not needed. Keep the equity. Grow with revenue.

---

## 12. CC-Specific SaaS CFO Action Plan

### Immediate Actions [NOW]

| # | Action | Time | Impact |
|---|--------|------|--------|
| 1 | Set up Wave or QBO, connect Stripe | 2 hours | Foundation of all financial tracking |
| 2 | Create MRR tracking spreadsheet (Section 1.14) | 1 hour | Know your north star metric |
| 3 | Open "TAX PROVISION" savings account, start depositing 25% of net income | 30 min | Never surprised by CRA |
| 4 | Document Bennett agreement in writing (scope, rev share terms, payment terms, notice period) | 2 hours | Legal protection + accounting clarity |
| 5 | Build pipeline: reach out to 10 potential clients this week | 3 hours | Start reducing Bennett concentration |
| 6 | Track Anthropic API costs per customer per month | 1 hour setup | Understand true COGS and margins |
| 7 | Set up annual billing option on Stripe (17% discount for prepaid) | 30 min | Better cash flow, lower churn |
| 8 | Build emergency cash reserve to $5,400 | Ongoing | Financial safety net |

### Q2 2026 Actions [NEXT 90 DAYS]

| # | Action | Target |
|---|--------|--------|
| 1 | Get Bennett below 70% of revenue | Add 2-3 clients at $500-$1,000/mo |
| 2 | Implement 3-tier pricing on website | Starter / Growth / Enterprise |
| 3 | Start monthly close process (Section 9.1) | 2 hours, 1st of every month |
| 4 | Apply for Futurpreneur + Starter Company Plus | $25K in grants |
| 5 | Prepare financial model for incorporation decision | Spreadsheet with scenarios |
| 6 | Start tracking all SaaS metrics (Section 1) | Build CFO dashboard |
| 7 | Set up CRM for pipeline tracking (HubSpot free or Pipedrive) | Track leads, demos, close rate |

### Q3 2026 Actions [FUTURE]

| # | Action | Trigger |
|---|--------|---------|
| 1 | If $80K+ annualized revenue: incorporate as CCPC | Revenue sustained 3+ months |
| 2 | Set up payroll system (if hiring employee) | Full-time role needed |
| 3 | Apply for IRAP ($500K grant for AI R&D) | Post-incorporation preferred |
| 4 | Get Bennett below 50% of revenue | 5+ clients active |
| 5 | Implement annual billing for all new clients | Standard offering |
| 6 | Consider revenue-based financing for specific growth investment | If ROI is clear |

### Q4 2026 Actions [FUTURE]

| # | Action | Target |
|---|--------|--------|
| 1 | Year-end financial review + valuation estimate | Know what OASIS is worth |
| 2 | 2027 budget and financial model | Plan the next year |
| 3 | Quarterly installment payment review | See ATLAS_INSTALLMENT_PAYMENTS.md |
| 4 | Tax optimization review with accountant | Maximize deductions before Dec 31 |
| 5 | Bennett below 30% of revenue | 10+ clients, diversified base |

### Monthly CFO Routine (2 Hours Total)

```
ATLAS MONTHLY CFO ROUTINE — OASIS AI Solutions
Perform on 1st-3rd of every month. Non-negotiable.

[ ] STEP 1: Revenue Reconciliation (30 min)
    [ ] Export Stripe MRR report
    [ ] Record Bennett payment from Wise
    [ ] Calculate total MRR, compare to forecast
    [ ] Calculate Bennett concentration %

[ ] STEP 2: Expense Reconciliation (20 min)
    [ ] Categorize all business transactions
    [ ] Match receipts
    [ ] Calculate gross margin

[ ] STEP 3: Cash Position Update (10 min)
    [ ] Record all account balances (Wise USD, Wise CAD, RBC, Stripe)
    [ ] Update runway calculation
    [ ] Verify tax provision account balance

[ ] STEP 4: KPI Dashboard Update (15 min)
    [ ] MRR (total and by customer)
    [ ] Customer count and ARPU
    [ ] Gross margin
    [ ] Pipeline status (leads, demos, proposals)
    [ ] Revenue concentration (HHI or Bennett %)

[ ] STEP 5: Forecast and Planning (15 min)
    [ ] Compare actuals to forecast — explain variances
    [ ] Update 3-month rolling forecast
    [ ] Identify any upcoming large expenses
    [ ] Flag any risks or opportunities for Atlas

Total time: ~90 minutes
```

### Quarterly CFO Routine (Additional 2 Hours)

```
Perform in addition to monthly routine — March, June, September, December.

[ ] QUARTERLY REVIEW (60 min)
    [ ] Full QBR (Section 9.2 template)
    [ ] NRR calculation
    [ ] Cohort analysis (when applicable)
    [ ] Pricing review — any customers underpriced?
    [ ] Product-market fit check — what is driving retention/churn?

[ ] TAX AND COMPLIANCE (30 min)
    [ ] Quarterly installment due? (See ATLAS_INSTALLMENT_PAYMENTS.md)
    [ ] HST filing due? (See ATLAS_HST_REGISTRATION_GUIDE.md)
    [ ] Any tax-loss harvesting opportunities? (See skills/tax-loss-harvesting/)
    [ ] T1135 threshold check — foreign property > $100K CAD?

[ ] STRATEGY (30 min)
    [ ] Is the growth plan working? Adjust if not.
    [ ] Any new revenue opportunities?
    [ ] Incorporation trigger check ($80K+ sustained revenue?)
    [ ] Competitive landscape — any threats?
```

---

## Appendix A: Key Formulas Reference

```
MRR = Sum of all active monthly subscription amounts
ARR = MRR x 12
NRR = (Starting MRR + Expansion - Contraction - Churned) / Starting MRR x 100%
GRR = (Starting MRR - Contraction - Churned) / Starting MRR x 100%
Customer Churn Rate = Customers lost / Starting customers x 100%
Revenue Churn Rate = (Contraction + Churned MRR) / Starting MRR x 100%
ARPU = MRR / Active customers
LTV = ARPU x Gross Margin % / Monthly Churn Rate
CAC = Sales & Marketing Spend / New Customers Acquired
LTV:CAC = LTV / CAC  (target: > 3:1)
CAC Payback = CAC / (ARPU x Gross Margin %)
Rule of 40 = Revenue Growth Rate % + Profit Margin %  (target: >= 40)
Burn Multiple = Net Cash Burn / Net New ARR  (target: < 2x)
SaaS Quick Ratio = (New MRR + Expansion MRR) / (Churned MRR + Contraction MRR)  (target: > 4)
Gross Margin = (Revenue - COGS) / Revenue x 100%
Cash Conversion = Operating Cash Flow / EBITDA
Runway = Cash / Monthly Net Burn
Break-Even MRR = Fixed Costs / Gross Margin %
HHI = Sum of (customer revenue share)^2  (target: < 0.15)
SDE = Net Profit + Owner Salary + Discretionary Expenses
Valuation = ARR x Multiple  (multiple depends on growth, retention, concentration)
```

## Appendix B: SaaS Benchmarks by Stage

| Metric | Pre-PMF ($0-$10K MRR) | Growth ($10K-$100K MRR) | Scale ($100K+ MRR) |
|--------|----------------------|------------------------|-------------------|
| Monthly customer churn | < 8% | < 5% | < 2% |
| Monthly revenue churn | < 5% | < 3% | < 1% |
| NRR | > 90% | > 100% | > 120% |
| GRR | > 80% | > 85% | > 90% |
| Gross margin | > 70% | > 75% | > 80% |
| LTV:CAC | > 2:1 | > 3:1 | > 4:1 |
| CAC payback | < 12 mo | < 12 mo | < 18 mo |
| Rule of 40 | Growth focused | > 30 | > 40 |
| Burn multiple | < 3x | < 2x | < 1.5x |
| Quick ratio | > 2 | > 3 | > 4 |
| Revenue concentration (max single client) | < 50% | < 25% | < 10% |

## Appendix C: Recommended Tools

| Function | Tool | Cost | Notes |
|----------|------|------|-------|
| Bookkeeping | Wave (free) or QBO ($25/mo) | $0-$25/mo | See ATLAS_BOOKKEEPING_SYSTEMS.md |
| SaaS metrics | Stripe Dashboard (free) or Baremetrics ($50/mo) | $0-$50/mo | Stripe built-in is fine until $50K MRR |
| CRM | HubSpot Free or Pipedrive ($15/mo) | $0-$15/mo | Track pipeline and close rates |
| Invoicing | Stripe Billing (built-in) | Included in Stripe fees | Auto-invoice + auto-retry |
| Receipt capture | Dext ($20/mo) or Wave receipt scanning (free) | $0-$20/mo | Take photo, auto-categorize |
| Financial model | Google Sheets (free) | $0 | Build the model in Section 7 |
| Cash management | Wise Business (free) + RBC | $0 | Multi-currency, low FX fees |
| Tax provision | Wealthsimple Cash or EQ Bank | $0 | 4% interest on tax reserves |

---

> **Atlas note:** This document covers the financial operations and strategy that make a SaaS business
> run well. For tax treatment of SaaS revenue, see `ATLAS_AI_SAAS_TAX_GUIDE.md`. For bookkeeping
> mechanics, see `ATLAS_BOOKKEEPING_SYSTEMS.md`. For incorporation planning, see
> `ATLAS_INCORPORATION_TAX_STRATEGIES.md`. For government grants, see `ATLAS_GOVERNMENT_GRANTS.md`.
>
> CC: Read this document once. Internalize the metrics. Then execute the action plan in Section 12.
> The monthly routine takes 2 hours. The quarterly routine adds 2 more. 4 hours per month to run
> OASIS like a real company. Do it.

---

*Prepared by ATLAS (CFO) | OASIS AI Solutions | 2026-03-27*
