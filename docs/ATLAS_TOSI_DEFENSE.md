# ATLAS TOSI Defense & Income Splitting Guide v1.0

> Navigating s.120.4 ITA — the tax on split income rules that block (and permit) income splitting.
> Prepared by ATLAS (CFO) for CC | Jurisdiction: Ontario, Canada | Tax Year: 2026
> All ITA references are to the Income Tax Act (Canada), R.S.C. 1985, c.1 (5th Supp.).
> Ontario rates per Ontario Taxation Act, 2007. CRA administrative positions per Income Tax Folios and IT Bulletins.

**Status:** Future planning document — CC is currently a sole proprietor. TOSI is a corporate/trust issue. This guide prepares CC for the moment OASIS incorporates and income splitting becomes available.

---

## Table of Contents

1. [What is TOSI?](#1-what-is-tosi)
2. [The TOSI Framework — Post-2018](#2-the-tosi-framework--post-2018)
3. [The Exclusion Tests — How to Beat TOSI](#3-the-exclusion-tests--how-to-beat-tosi)
4. [Strategies That Work — TOSI-Proof Income Splitting](#4-strategies-that-work--tosi-proof-income-splitting)
5. [Strategies That Don't Work — CRA Will Catch](#5-strategies-that-dont-work--cra-will-catch)
6. [Documentation Requirements — TOSI Defense File](#6-documentation-requirements--tosi-defense-file)
7. [CC-Specific Planning Roadmap](#7-cc-specific-planning-roadmap)
8. [Decision Trees](#8-decision-trees)
9. [Dollar-Amount Examples](#9-dollar-amount-examples)
10. [Key ITA References](#10-key-ita-references)

---

## 1. What is TOSI?

### The Core Problem

Income splitting — paying dividends from a private corporation to lower-income family members — is the most powerful tax reduction tool available to Canadian business owners. A family of four with $200K in corporate profit can potentially pay $40K-60K less tax per year by splitting income across four personal returns instead of concentrating it on one.

The government noticed. TOSI is the legislative response.

**Tax on Split Income (s.120.4 ITA)** imposes the **top marginal rate** on "split income" received by a "specified individual" from a "related business." In Ontario (2026), that rate is **53.53%**.

The consequence is punishing:

```
Business owner receives $100K dividend:
  Ontario combined marginal rate (top bracket):    53.53%
  Tax paid:                                        $53,530
  After-tax income:                                $46,470

Family member receives same $100K dividend (TOSI applies):
  TOSI rate:                                       53.53%
  Tax paid:                                        $53,530
  After-tax income:                                $46,470
```

TOSI eliminates ALL benefit of income splitting when it applies. The family member pays exactly what the business owner would have paid — at top rates — regardless of their actual income. If the family member is a student earning $15K/year, TOSI still hammers them at 53.53%.

TOSI is intentionally brutal to discourage the strategy entirely.

### History

| Period | Scope | Nickname |
|--------|-------|----------|
| 2000–2017 | Applied only to minors (under 18) receiving dividends from family-owned corporations | "Kiddie Tax" |
| January 1, 2018 | Massively expanded to all adults — spouses, children of any age, parents, siblings | "2018 TOSI Expansion" |

The 2018 expansion was the most significant Canadian personal tax change in decades. It fundamentally altered the calculus of incorporation and income splitting.

### The Attribution Rules (Related but Separate)

TOSI is distinct from the attribution rules (s.74.1–74.5). Both can apply simultaneously:

| Rule | ITA Section | Targets | Effect |
|------|-------------|---------|--------|
| **Attribution** | s.74.1 | Transfers/loans of property to spouse or minor child | Income attributed BACK to the transferor |
| **TOSI** | s.120.4 | Split income received by specified individuals | Top marginal rate on the recipient |

When you lend money to a spouse without charging the prescribed rate, attribution rules pull the income back to you (s.74.1). TOSI then potentially applies to dividends from private corporations regardless of attribution. The two rules operate independently — you can trigger both simultaneously if a transaction is structured carelessly.

---

## 2. The TOSI Framework — Post-2018

### 2.1 Who is a "Specified Individual"?

Per s.120.4(1), a **specified individual** means a Canadian resident who either:

1. Is related to a person who is resident in Canada and carries on a business at any time in the year, OR
2. Is related to a person who holds an interest in a partnership or trust that carries on a business

**Related persons include (ITA s.251):**
- Spouse or common-law partner
- Children (any age — this is new post-2018)
- Parents
- Siblings
- Nieces and nephews
- Corporations controlled by a related person

**NOT a specified individual:**
- The business owner themselves
- Arm's length parties (unrelated employees, investors, consultants)
- Persons connected only by marriage to a non-controlling family member (in some structures)

> **CC Note:** This is future planning. CC is currently single with no dependents. The "specified individual" pool is empty today. When CC has a spouse or children, TOSI immediately becomes the dominant issue in any dividend payment decision.

---

### 2.2 What is "Split Income"?

Split income is defined in s.120.4(1). It captures five categories:

#### Category A — Dividends from Private Corporations

The primary target. Any dividend (declared or deemed) received from a private corporation where:
- A person related to the recipient is a shareholder, director, officer, or employee of the corporation, OR
- A person related to the recipient carries on a business through a partnership or trust that holds shares

**Example:** OASIS Corp pays a dividend to CC's spouse. CC is the shareholder and operator. This is split income unless an exclusion applies.

#### Category B — Income from a Partnership or Trust

Income allocated from a partnership or trust to a specified individual where a related person carries on business through that partnership or trust.

**Example:** OASIS LP (if structured as a partnership) allocates income to CC's parent. Split income unless excluded.

#### Category C — Capital Gains on Private Corporation Shares (s.120.4(4))

The 2018 expansion added a deemed dividend rule: when a specified individual disposes of private corporation shares (or an interest in a partnership/trust) and the gain is essentially a dividend in economic substance, TOSI may apply.

This does NOT mean all capital gains on private company shares are TOSI. It means gains that are structured as disguised dividends (e.g., a share redemption that economically mirrors a dividend) can be recharacterized.

Legitimate arm's length sales — including sales qualifying for the LCGE — are excluded (see s.120.4(1)(e)).

#### Category D — Interest on Loans to Private Corporations

Interest income received from a private corporation by a specified individual where the interest rate is non-commercial. This captures situations where family members lend money to the corporation at inflated rates.

#### Category E — Rent from Property (Related Source)

Rent received from a person related to the recipient where the property is used in a related business.

---

### 2.3 What is NOT Split Income (Statutory Exclusions)?

S.120.4(1) contains explicit exclusions. If an exclusion applies, TOSI is off the table entirely.

| Exclusion | ITA Reference | Condition |
|-----------|---------------|-----------|
| Salary/wages | s.120.4(1) definition, para (a) | Reasonable salary paid to family member for actual work performed — NEVER TOSI |
| Excluded business income | s.120.4(1) "excluded amount" (a) | Individual meets active engagement test (see Section 3) |
| Excluded shares income | s.120.4(1) "excluded amount" (b) | Individual meets share ownership + arm's length income test (see Section 3) |
| Capital gains on QSBC (arm's length) | s.120.4(1.1) | Shares sold to arm's length buyer; individual has contributed to the business |
| Inherited property income | s.120.4(1) para (e) | Income from property inherited directly from a deceased person |
| Pension income splitting | s.120.4(1) para (f) | Age 65+, eligible pension income under s.60.03 |
| Public company dividends | definition of "split income" | Only private corporation dividends are caught |
| Arm's length employee income | definition of "specified individual" | Unrelated employees are never specified individuals |

---

### 2.4 The Tax Consequence When TOSI Applies

When TOSI applies to split income:

1. The split income is included in the specified individual's income (normal inclusion)
2. A **special TOSI tax** under Part I (s.120.4(2)) is added equal to the excess of the top federal rate over the individual's applicable rate
3. A **provincial TOSI tax** is imposed equivalent to the provincial top rate
4. The **dividend tax credit** is **denied** on split income dividends
5. The **basic personal amount** cannot offset TOSI tax
6. Net result: the individual pays **53.53% Ontario combined** regardless of their income level

```
Result when TOSI applies to a $50,000 dividend paid to CC's future spouse (student earning $20K):

  Without TOSI (if spouse had $20K other income):
    Combined marginal rate on dividend:   ~29.52% (Ontario non-eligible)
    Tax on $50,000 dividend:              $14,760
    After-tax:                            $35,240

  With TOSI:
    TOSI rate:                            53.53%
    Tax on $50,000 dividend:              $26,765
    After-tax:                            $23,235

  TOSI penalty on this single dividend:  $12,005
```

The dividend tax credit is also denied — this is a double punishment. The tax credit normally offsets the corporate pre-payment, but TOSI recipients cannot access it, creating economic double taxation.

---

## 3. The Exclusion Tests — How to Beat TOSI

### 3.1 Ages Under 18 — No Escape

For individuals under 18, the original "kiddie tax" applies in full. No exclusions exist beyond literal exceptions (inheritance, arm's length dispositions). Income from private corporations flowing to minor children through dividends will be taxed at 53.53%. Full stop.

**CC Planning:** Do not structure corporate share ownership for minor children. RESP is the correct vehicle for children's financial planning. See Section 7.

---

### 3.2 Ages 18–24 — Two Narrow Paths

#### Path A: Excluded Business (s.120.4(1) "excluded business")

TOSI does not apply to income from an **excluded business**, defined as a business in which the individual is **actively engaged on a regular, continuous, and substantial basis** during the year OR during any 5 prior years.

**The ≥20 hour/week threshold:**

CRA's administrative position (confirmed in 2017 Technical Notes) is that "regular, continuous, and substantial" means at least **20 hours per week** during the period the business operates. This is not in the statute directly but is CRA's established benchmark.

Key points on the 20-hour test:
- Seasonal businesses: 20 hours/week during the operating season, not year-round
- The 5 prior years provision means an individual who worked 20+ hours/week for 5 previous years qualifies even if they've stepped back
- Part-time students who work summers may qualify on a seasonal basis
- **Documentation is everything** — time logs, task descriptions, correspondence showing active involvement

**What qualifies as "active engagement":**
- Administrative work (bookkeeping, invoicing, client management)
- Operational work (delivering service, managing projects)
- Sales and business development
- IT / technical work on business systems

**What does NOT qualify:**
- Attending board meetings only
- Being listed on documents without working
- Occasional advice or consultation
- Passive oversight of investments

**Example for CC:**

```
CC's future sibling (age 20) works at OASIS Corp doing client onboarding:
  Hours/week during operating season:   22 hours (documented)
  Duration:                             Full year

  Result: Excluded business — dividends paid to sibling are NOT TOSI.
  Dividend to sibling:                  $30,000
  Sibling's marginal rate (income = $30K total):   ~32.02%
  Tax on dividend:                      ~$9,606

  Without excluded business exclusion (TOSI):      $16,059
  Savings:                              $6,453/year
```

#### Path B: Excluded Shares (s.120.4(1) "excluded shares")

The excluded shares definition has four conditions that ALL must be met:

1. The shares are NOT shares of a professional corporation (no law firms, medical clinics, etc.)
2. The specified individual owns shares representing **at least 10% of votes AND 10% of FMV** of all issued shares
3. The corporation earns less than **90% of its income from the provision of services** (manufacturing, product sales, real estate pass through the test — most service businesses fail this)
4. The corporation does NOT earn more than 90% of its income from **another related business**

**The 10% FMV test is a trap:**

This must be REAL economic ownership. If CC holds 90 shares and gives a family member 10 shares but the shares are different classes with different economic rights, CRA will look through the structure. The 10% must reflect genuine 10% economic entitlement.

**The 90% services income test is a killer for tech/AI:**

OASIS AI Solutions earns nearly 100% from service contracts. This means the excluded shares test is almost certainly **not available** to OASIS shareholders.

```
OASIS Corp income breakdown (illustrative):
  Client service contracts (AI automation):    95% of revenue
  90% services threshold:                      FAIL

  Excluded shares: NOT AVAILABLE for OASIS family members
```

This is the most important planning constraint for CC. The excluded shares path is closed for OASIS-type service businesses. The excluded business path (active engagement) is the only viable route for 18–24 year-old family members.

---

### 3.3 Ages 25+ — The Reasonable Return Test

For individuals aged 25 or older, TOSI applies only to the extent the amount received **exceeds a "reasonable return"** in respect of the contributions made by the individual to the business.

**s.120.4(1) "reasonable return" — five factors:**

1. **Work performed** — What labour did this person contribute to the business? At what market rate would this work be compensated?
2. **Property contributed** — What capital, equipment, IP, or other property did this person bring to the business?
3. **Risk assumed** — Did this person personally guarantee debt? Put capital at risk? Have legal exposure?
4. **Amounts previously paid** — What has the individual already received? Is the total compensation proportionate to their contribution?
5. **Other relevant factors** — Education, expertise, connections that benefit the business

**The reasonable return test is a balancing analysis, not a formula.** CRA assesses facts and circumstances. A spouse who introduced $100K of startup capital and five major clients has contributed more than one who did nothing. The standard is economic substance.

**Practical guidance:**

| Contribution Type | Reasonable Return Implication |
|-------------------|-------------------------------|
| $50K cash invested at incorporation | Reasonable return on invested capital (e.g., 5-10% annual return = $2,500-5,000/year) |
| 15 hrs/week bookkeeping | Market rate: $30-50/hr → $23,400-39,000/year |
| Personal guarantee on $200K bank loan | Risk premium: $5,000-15,000/year is defensible |
| Introducing 3 enterprise clients worth $120K ARR | Finders fee/contribution: potentially significant |
| Spouse listed on shares, no involvement | Reasonable return: $0 |

**The spouse scenario for CC at age 25+:**

```
CC's future spouse (age 27) contributes to OASIS Corp:
  - Works 10 hrs/week on social media and content (market rate: $35/hr)
  - Contributed $20,000 seed capital at incorporation
  - Has network that generated 2 clients worth $40K/year

  Reasonable return calculation:
    Labour: 10 hrs × $35 × 52 weeks =          $18,200/year
    Return on $20K capital (6%):                $1,200/year
    Client introduction (one-time or ongoing):  $4,000-8,000/year
    Total reasonable return:                    ~$23,400-27,400/year

  Dividends up to ~$25,000/year to spouse: NOT TOSI (reasonable return)
  Dividends above ~$25,000/year to spouse: TOSI applies on the excess
```

**Documentation is the entire game at 25+.** The "reasonable return" determination is CRA's subjective assessment of your contribution evidence. Build the file contemporaneously — not after you receive a reassessment notice.

---

### 3.4 Age 65+ — Pension Income Exception

For individuals aged 65 or older, TOSI does not apply to split income from **excluded shares** that would otherwise qualify as eligible pension income under s.60.03 (pension income splitting). This is the retirement planning pathway.

**Practical use:** CC's parents at age 65+ may receive dividend income from OASIS Corp without TOSI if:
- The parents hold excluded shares (10%+ ownership, non-service business — same tests as above, OR)
- The amount would qualify as eligible pension income

This is planning for decades away. Document it here for completeness.

---

## 4. Strategies That Work — TOSI-Proof Income Splitting

### Strategy 1: Reasonable Salary (The Safest, Always Works)

**ITA reference:** s.120.4(1) definition of "split income" — salary is explicitly excluded.

**How it works:** Pay family members a market-rate salary for work they actually perform in the business. Salary is NEVER split income. Full stop. No tests, no thresholds, no age restrictions.

**Requirements for CRA to accept:**
1. Written employment contract (signed before work starts)
2. Work is real and documented (time sheets, deliverables, communications)
3. Salary is commensurate with what you would pay an arm's length employee for the same work
4. T4 issued, source deductions remitted (CPP, income tax, EI if applicable)
5. Salary is "reasonable" under s.67 (the general reasonableness test for deductions)

**Double benefit:** Salary paid to family members is:
- Deductible to the corporation (reduces corporate taxable income at 12.2% SBD rate)
- Creates RRSP contribution room for the family member
- Taxed at the family member's actual marginal rate (not TOSI rate)

**Market rate benchmarks for common OASIS roles (2026 Ontario):**

| Role | Hours/Week | Market Rate | Annual Salary Range |
|------|-----------|-------------|---------------------|
| Administrative assistant | 15 hrs | $20-28/hr | $15,600-21,840 |
| Bookkeeper | 10 hrs | $30-45/hr | $15,600-23,400 |
| Social media manager | 10 hrs | $25-40/hr | $13,000-20,800 |
| Content writer | 8 hrs | $35-55/hr | $14,560-22,880 |
| Sales coordinator | 15 hrs | $22-35/hr | $17,160-27,300 |
| QA / testing | 10 hrs | $25-40/hr | $13,000-20,800 |

**CRA audit trigger:** Salary exceeding market rate. If CC pays a spouse $80K/year for 5 hours/week of administrative work, CRA will reassess to $15-25K and add penalties. Never inflate.

```
Tax example — Reasonable salary strategy:

  OASIS Corp profit before family salary:     $120,000
  Spouse salary (social media, 10 hrs/week):  $18,000
  OASIS Corp taxable income after salary:     $102,000

  Corp tax saved on deduction (12.2% SBD):   $18,000 × 12.2% = $2,196

  Spouse's tax on $18,000 salary:
    Basic personal amount credit:             $15,705 (2026, federal+Ontario combined)
    Taxable income above BPA:                 $2,295
    Tax:                                      $2,295 × ~20.05% = ~$460
    CPP premiums (employee):                  ~$850
    Total cost to spouse:                     ~$1,310

  Net family tax saving vs. CC keeping all income at top rate:
    If CC had kept $18K at 53.53%:            $9,635
    Spouse pays $1,310 in taxes:              $1,310
    Corp saves $2,196 in corporate tax:       $2,196
    Family net saving:                        $9,635 - $1,310 + $2,196 = ~$10,521/year
```

**Risk level:** Very low. This is the intended mechanism. Document thoroughly.

---

### Strategy 2: Prescribed Rate Loan (s.74.5(2) — Attribution Override)

**ITA references:** s.74.1 (attribution rules), s.74.5(2) (prescribed rate loan exception), Reg. 4301(c)

**How it works:** Lend money to your spouse (or a family trust for the spouse's benefit) at the CRA prescribed interest rate. The spouse invests the loan proceeds. Investment returns are taxed in the spouse's hands at their lower rate, not attributed back to you under s.74.1.

**TOSI interaction:** The prescribed rate loan strategy neutralizes the attribution rules. TOSI applies to dividends from private corporations — if the spouse invests the loan proceeds in public securities, mutual funds, or ETFs, the returns are NOT split income (TOSI only hits private company dividends and related business income). This strategy is primarily an attribution-bypass tool, not a TOSI bypass.

**Requirements — all four must be met, forever:**

1. **Prescribed rate:** The loan must charge at least the CRA prescribed rate at the time the loan is made. The rate is locked in at inception.
2. **January 30 interest deadline:** The borrower must actually PAY the interest (not just accrue it) by January 30 of the following calendar year. Miss this deadline even once, and the exception is permanently gone for that loan.
3. **Bona fide loan:** The loan must be a genuine, documented debt with terms (promissory note, repayment schedule, security if applicable).
4. **Not a sham:** The investment must be real. If the spouse immediately gifts the money back to you, CRA will ignore the structure.

**Prescribed rate history and strategy:**

| Quarter | Prescribed Rate | Optimal to Set Up? |
|---------|-----------------|-------------------|
| Q1-Q2 2020 | 1% | BEST OPPORTUNITY IN HISTORY — rate locked at 1% forever |
| 2022-2023 | 5-6% | Poor — too expensive to borrow |
| 2024-2025 | 3-4% | Acceptable if rates drop further |
| Watch for: | Rate drops | Lock in when rates fall to 1-2% |

**The 1% prescribed rate loans from 2020 are still active and earning their owners millions in tax savings.** Miss a future low-rate quarter and you lose the opportunity for that quarter's setup.

**Dollar-amount example:**

```
CC sets up $200,000 prescribed rate loan to spouse at 2% (hypothetical future low rate):

  Annual interest payable by spouse to CC:        $200,000 × 2% = $4,000
  CC reports $4,000 interest income (their rate):
    At 53.53% top rate:                           $2,141 tax

  Spouse invests $200,000 in Canadian dividend ETF (5% yield):
    Dividend income:                              $10,000/year
    Minus interest paid on loan:                  ($4,000)
    Net income to spouse:                         $6,000
    Spouse's marginal rate (low income):          ~20.05%
    Tax:                                          ~$1,203

  Without the loan (CC receives all investment income):
    $10,000 at 53.53%:                            $5,353 tax

  Annual tax saving:
    Old tax:                                      $5,353
    New tax (CC interest + spouse investment):    $2,141 + $1,203 = $3,344
    Annual saving:                                $2,009/year
    Over 20 years (compounded):                   $40,000+ in tax savings
```

**Critical warning:** The January 30 interest payment is a hard deadline. Calendar it every year. One missed payment destroys the exception permanently. Set up automatic bank transfers.

**Risk level:** Low when documented properly and interest paid on time. Medium if setup is sloppy.

---

### Strategy 3: Spousal RRSP

**ITA references:** s.146(1) "spousal RRSP", s.146(8.3) (3-year attribution rule)

**How it works:** CC contributes to a spousal RRSP using CC's own contribution room. The spouse is the annuitant (owner). At retirement, withdrawals are taxed in the spouse's hands at their lower rate.

**TOSI: not applicable.** Spousal RRSP is a registered plan. TOSI does not apply to registered account distributions. This is the cleanest income splitting tool for retirement.

**The 3-year attribution rule (s.146(8.3)):** If the spouse withdraws from the spousal RRSP within the same calendar year OR the two preceding calendar years in which CC made a contribution, the withdrawal is attributed back to CC. Plan a 3-year cooling-off period.

**Annual mechanics:**

1. CC contributes to spousal RRSP (reduces CC's taxable income — deduction at CC's top rate, ~53.53%)
2. Contribution room used is CC's (not the spouse's)
3. Wait 3 calendar years before any withdrawal
4. Spouse withdraws at their marginal rate in retirement (potentially 20-30% vs. CC's 53.53%)

```
Tax arbitrage on spousal RRSP contribution:

  CC contributes $10,000/year to spousal RRSP:
    CC's deduction at 53.53%:                    $5,353 tax saved now

  Spouse withdraws $10,000 at retirement (low income):
    Spouse's marginal rate (assuming $40K income): ~29.65%
    Tax on withdrawal:                            $2,965

  Per $10,000 contributed:
    Tax saved now:                               $5,353
    Tax paid at withdrawal:                      $2,965
    Net lifetime saving:                         $2,388 per $10K contributed
    Plus: decades of tax-free compounding inside the RRSP
```

**Contribution limit:** CC's annual RRSP room (18% of prior-year earned income, max $32,490 in 2026). The contribution CAN go entirely to a spousal RRSP — there is no split requirement.

**Risk level:** Zero. This is explicitly permitted by the ITA. Zero documentation requirements beyond normal RRSP records.

---

### Strategy 4: Family Trust with Active Beneficiaries

**ITA references:** s.104 (trusts), s.120.4(1) "specified individual", s.75(2) (reversionary trust rules), s.107(2) (capital distribution)

**How it works:** Establish a discretionary family trust during incorporation. The trust holds shares of OASIS Corp. ATLAS Corp pays dividends to the trust. The trustee (CC or a corporate trustee) allocates income to beneficiaries who meet the TOSI exclusion tests.

**Structure:**

```
CC (trustee + settlor contribution from arm's length party)
        |
    Family Trust
        |
   Holds: shares of OASIS Corp (via estate freeze or subscription)
        |
   Beneficiaries:
     - CC (business owner — not a specified individual, TOSI never applies to CC)
     - CC's spouse (age 25+ — reasonable return test applies)
     - CC's future children (at 25+ — reasonable return test applies)
     - CC's parents (reasonable return test or 65+ pension exception)
```

**TOSI still applies inside the trust.** The trust does not eliminate TOSI — it provides flexibility to allocate income to beneficiaries who qualify under one of the exclusion tests. Allocating to minor children is still TOSI. Allocating to a spouse who does no work is still TOSI (on the excess above reasonable return).

**The trust advantage is flexibility and capital gains multiplication:**

1. Trustees can choose each year HOW to allocate — if the spouse earns a reasonable return this year, allocate dividends to them. If not, allocate to CC.
2. Each family member holds a beneficial interest in OASIS shares — each gets their own $1.25M LCGE on a future business sale.

**Family of four on a $2M OASIS Corp sale:**

```
Sale price of OASIS Corp:                       $2,000,000
Cost base (nominal at incorporation):           $4

With family trust (4 beneficiaries):
  Each member's capital gain:                   $500,000
  Each member's LCGE:                           $1,250,000 (2026)
  LCGE available per member:                    exceeds gain — ALL TAX FREE
  Total capital gains tax:                      $0

Without family trust (CC holds all shares):
  CC's capital gain:                            $2,000,000 - $4 = $1,999,996
  CC's LCGE (one person):                       ($1,250,000)
  Remaining taxable gain:                       $749,996
  Inclusion rate (2/3 post-June 2024):          $499,997
  Tax at 53.53%:                                $267,618

  Tax saved via family trust:                   $267,618
```

**Setup requirements:**
- Independent settlor (not CC) makes a nominal contribution ($100 is standard) — prevents reversionary trust rules under s.75(2)
- Trust deed drafted by a tax lawyer (not a DIY template) — $3,000-8,000
- Annual T3 trust return filed
- 21-year deemed disposition rule — plan capital distribution or wind-up before year 21

**Risk level:** Medium. Well-established structure but requires professional setup and ongoing administration. CRA scrutinizes family trusts heavily — substance must match form.

---

### Strategy 5: Capital Gains Multiplication via LCGE

**ITA references:** s.110.6 (lifetime capital gains exemption), s.110.6(1) "qualified small business corporation shares", s.110.6(14) (purification)

**How it works:** Structure OASIS Corp so that each family member holds qualifying shares. On a future sale of OASIS, each member claims their own LCGE ($1.25M in 2026, indexed to inflation).

**QSBC share qualification requirements (all must be met at time of sale):**
1. Shares of a **Canadian-Controlled Private Corporation** (CCPC)
2. **Substantially all** (90%+) of the corporation's assets are used in an **active business** carried on primarily in Canada
3. The shares have been owned by the individual (or a related person) for at least **24 months** continuously
4. During the 24-month holding period, more than **50% of FMV** of assets were used in active business

**The purification problem:**

As OASIS accumulates retained earnings and invests them (in brokerage accounts, GICs, or real estate), those passive assets can disqualify the shares from QSBC status. Purification means removing those passive assets before a sale.

**Purification strategies:**
- Pay dividends before the sale (distributes retained earnings, removes passive assets)
- Wind down passive investments into the business
- Establish a holding company (HoldCo) to hold passive assets — OpCo remains pure

**TOSI on capital gains (s.120.4(1.1)):**

Capital gains on QSBC shares are excluded from TOSI IF the individual contributed to the business. The exclusion for 18–24 year-olds requires the "excluded business" test to be met. For 25+ year-olds, the "reasonable return" contribution test applies. For arm's length dispositions, TOSI does not apply at all.

**The family trust connection:**

Family trust beneficiaries each get a separate LCGE claim. This is why setting up the trust at incorporation (before value accrues) is so important — the trust can hold shares on behalf of all beneficiaries from day one, and each beneficiary's share of the gain is separately eligible for LCGE.

**Risk level:** Low to medium. LCGE is a statutory entitlement. The risk is in qualification — ensuring QSBC status at time of sale requires advance planning and may require professional share restructuring.

---

### Strategy 6: Second-Generation Income (The Clean Cascade)

**ITA references:** No specific provision — this is structural planning using existing rules.

**How it works:** Pay a reasonable salary to a family member (TOSI-proof). The family member uses their after-tax salary to invest in arm's length publicly traded securities. The returns on those investments are entirely their own income — no connection to the related business, no TOSI.

```
OASIS Corp pays spouse $25,000 salary (reasonable, documented):
  Spouse nets after tax:                   ~$21,500

  Spouse invests $21,500 in diversified ETF portfolio:
    Annual return (6%):                    $1,290/year
    Interest/dividends from public companies: taxed at spouse's rate (~29%)
    Capital gains on public stocks:        50% inclusion, taxed at ~15%

  None of this investment income is TOSI — it came from arm's length investments,
  not from the related business. CRA cannot reach it.
```

This strategy is slow but clean. Over a decade, the spouse can build a meaningful investment portfolio from salary income with no TOSI exposure.

---

### Strategy 7: Pension Income Splitting (Future — Age 65+)

**ITA references:** s.60.03 (pension income splitting election), s.118(3) (pension income amount)

**How it works:** At age 65+, CC and spouse can jointly elect to allocate up to 50% of "eligible pension income" to the lower-income spouse. This reduces combined household tax.

**Eligible pension income includes:**
- Registered Pension Plan (RPP) payments
- RRIF withdrawals (mandatory at 72, or voluntary after 65)
- Annuity payments from RRSP/DPSP

**NOT eligible (before age 65):**
- CPP/OAS
- RRSP withdrawals (age 65+ only for RRIF)

**Example (far future planning):**

```
CC (age 70):
  RRIF income:                              $60,000
  CPP:                                      $18,000
  Other income:                             $25,000
  Total:                                    $103,000
  Marginal rate:                            ~46%

  Pension split — allocate $30,000 RRIF to spouse:
  CC's income after split:                  $73,000 (marginal rate drops to ~33%)
  Spouse's additional income:               $30,000 (marginal rate ~23%)

  Annual tax saving on $30,000 split:
    CC saves (46% - 33%) on $30K:           $3,900
    Spouse pays 23% on $30K:                $6,900 (would have paid 0% on first $30K)
    Net if spouse has zero other income:    $3,900 saved
    If spouse has other income, both rates compress. Real saving varies.
```

**TOSI: not applicable.** Pension income splitting is a statutory election under s.60.03, explicitly excluded from TOSI rules.

---

## 5. Strategies That Don't Work — CRA Will Catch

### 5.1 Dividend Sprinkling to Non-Contributing Family Members

**The original TOSI target.** The 2018 reforms were specifically aimed at this: paying dividends to a spouse or adult child who has no real connection to the business.

**How it was done (pre-2018):**
- CC incorporates OASIS
- Gives spouse 50 shares of a "Family" share class
- Pays spouse $40K in dividends — spouse pays ~$8K tax (low rate)
- vs. CC paying $40K dividend — CC pays ~$21K (top rate)
- Tax savings: $13K/year from a spouse who does nothing

**Why it fails post-2018:**
- Spouse is a "specified individual" — s.120.4 applies
- Spouse does no work → no "excluded business" qualification
- Spouse has no capital contribution → "reasonable return" is $0
- Result: TOSI at 53.53% — spouse pays $21,400 tax on $40K dividend, same as CC

**The attempt to disguise it:**

Some advisors suggested giving the spouse a nominal "consulting role" with a token monthly meeting. CRA and the courts see through this. The test is substantive engagement, not nominal role creation. Sham involvement creates audit risk and penalties, not tax savings.

---

### 5.2 Nominal Share Ownership

Transferring shares to a family member without real economic contribution:
- Gifting shares to a spouse without charging FMV (triggers s.74.1 attribution AND TOSI on dividends)
- Selling shares at below FMV to a spouse (CRA deems proceeds at FMV under s.69, plus TOSI)

**The correct approach:** If the family trust structure is used, the trust holds the shares. Family members are beneficiaries, not direct shareholders (avoiding nominal ownership concerns).

---

### 5.3 Distributions to Minor Children

TOSI applies at full rates to dividends flowing to anyone under 18 from a private corporation. The original "kiddie tax" from 2000 applies. There is no exclusion for minor children receiving corporate dividends.

**The correct vehicle for children's financial planning is the RESP**, not corporate dividends.

```
RESP vs. Corporate dividend to minor child:

  RESP:
    Contribution:                           $2,500/year
    CESG (20% government match):            $500/year
    Annual benefit:                         $500 in free government money
    Growth:                                 Tax-free inside RESP
    Withdrawal by child:                    Taxed at child's rate (usually 0%)

  Corporate dividend to minor:
    TOSI rate:                              53.53%
    Tax on $2,500 dividend:                 $1,338
    After-tax to child:                     $1,162

  RESP wins by an enormous margin.
```

---

### 5.4 Inflated Salary to Family Members

Paying a family member $80K/year for 5 hours/week of administrative work will:
1. Fail the reasonableness test under s.67 (CRA will reassess to market rate)
2. Result in a reassessment of the excess as a deemed dividend — and then TOSI applies to that deemed dividend
3. Add gross negligence penalties if CRA determines the inflation was deliberate (25% penalty on the disallowed amount)

**The line:** Pay exactly what you would pay an arm's length hire. Use Glassdoor, Indeed, and industry salary surveys to document the market rate. Attach this to the employment contract.

---

### 5.5 Circular Arrangements

Corporation pays salary to family member → family member loans money back to corporation at a nominal rate → corporation pays the family member "interest" → CRA treats the interest as a disguised dividend.

Section 56(4.1) catches back-to-back arrangements where the substance of the transaction is to convert dividends into interest. The interest income can be recharacterized as split income.

**Also:** If a spouse receives salary and then transfers it to CC or the corporation, CRA may treat the transfer as evidence the salary was not for real work.

---

### 5.6 Retroactive Documentation

Building a paper trail after a CRA audit notice is a serious mistake. Time logs, employment contracts, and meeting minutes must be created at the time the activity occurs. Backdated documents are evidence of fraud, not a defense against TOSI.

**Atlas Rule:** TOSI documentation must be created contemporaneously and filed in a dedicated binder. After every year-end, confirm the file is complete before filing T1s or T2s.

---

## 6. Documentation Requirements — TOSI Defense File

The TOSI defense lives or dies on documentation. When CRA audits an income-splitting arrangement (and they will, given the 2018 reforms), the documentation file is the entire defense.

### 6.1 For Each Family Member Receiving Business Income

Maintain a dedicated folder (physical or digital, securely backed up) for each family member. The folder must contain:

**Employment/Contract Documentation:**
- [ ] Signed employment contract or consulting agreement (signed BEFORE work begins)
- [ ] Clear description of duties and responsibilities
- [ ] Compensation amount and payment schedule
- [ ] Arm's length comparable salary evidence (job postings, salary surveys, recruiter quotes)
- [ ] T4 copies and payroll records (if employee) or T4A (if contractor)
- [ ] Source deduction remittance records (PD7A forms)

**Time and Activity Tracking:**
- [ ] Weekly time logs (date, hours, task description)
- [ ] Email and communication records showing active involvement
- [ ] Project deliverables (completed tasks, outputs produced)
- [ ] Meeting attendance records

**Capital and Risk Contribution:**
- [ ] Shareholder agreement documenting any capital contribution
- [ ] Bank records showing any loans or investments made to the business
- [ ] Personal guarantee documentation (if applicable)
- [ ] Risk assessment narrative: what financial risk does this person face if the business fails?

**Professional Qualifications:**
- [ ] Resume or CV showing relevant skills
- [ ] Certifications, degrees, or training relevant to their role
- [ ] LinkedIn profile or similar (saves contemporaneously)
- [ ] Prior relevant work experience

**Board and Corporate Records:**
- [ ] Board resolutions authorizing salary or dividends
- [ ] Shareholder meeting minutes
- [ ] Dividend declarations (formal documentation, not just a bank transfer)
- [ ] Annual corporate resolution confirming ongoing compensation terms

**Reasonable Return Analysis (25+ year-olds):**
- [ ] Annual written analysis of the five s.120.4(1) factors for each family member
- [ ] Valuation of capital contributed (at current fair market value)
- [ ] Risk assessment for the year (did they personally guarantee anything? Bear any losses?)
- [ ] "Reasonable return cap" calculation (the maximum dividend payable without TOSI)

---

### 6.2 Annual TOSI Review Checklist (for Atlas to run at year-end)

```
□ List all family members who received any income from OASIS Corp this year
□ For each: confirm their age on Dec 31 of the tax year
□ For each: apply the correct age-based test (under 18 / 18-24 / 25+)
□ For each 18-24 year old: confirm hours/week worked, check ≥20 hr threshold
□ For each 25+ year old: calculate reasonable return cap
  □ Labour: hours × market rate
  □ Capital: contributed amount × reasonable rate of return
  □ Risk: any personal guarantees or capital at risk this year?
□ Compare dividends paid against reasonable return cap
□ Any excess above cap: flag as potential TOSI — consult CPA before filing
□ Confirm all employment contracts are current and signed
□ Confirm time logs are complete and filed
□ Confirm corporate resolutions for all salary and dividend payments are signed
□ Confirm T4s issued and payroll remittances filed (PD7A)
```

---

## 7. CC-Specific Planning Roadmap

### 7.1 Current State (2026 — Sole Proprietor, Single)

TOSI is irrelevant today. CC is the only income recipient. Nothing to split, no one to split with.

**Priority actions now (building the foundation):**
1. Maximize TFSA contributions — investment income inside TFSA is forever exempt from TOSI and everything else
2. Open FHSA immediately — $8,000/year deduction, tax-free growth, TOSI-free
3. Document CC's foundational contributions to OASIS in writing today:
   - IP created (algorithms, prompts, systems)
   - Sweat equity (hours, market rate valuation)
   - Capital contributed (initial investment)
   - Revenue generated (client contracts, ARR)
   - This documentation proves CC's "reasonable return" basis if CC ever contributes to a family trust

---

### 7.2 Incorporation Trigger (Revenue > $80K CAD)

When OASIS crosses $80K revenue, incorporate. TOSI becomes relevant immediately because corporate shareholders can receive dividends.

**Incorporation structure to enable future income splitting:**

```
Recommended share structure at incorporation:
  Class A Common:   CC holds all shares (voting + full economic rights)
  Class B Preferred: Family trust can subscribe later (no voting, participating in dividends and capital)
  Class C Preferred: Future spouse can subscribe later
  Class D Common:   Future key employees (options or direct)

This multi-class structure (s.51 and s.86 reorg-proof) allows:
  - Future estate freeze (exchange Class A commons for new preferred, issue new commons to family trust)
  - Dividend sprinkling to Class B/C holders who meet TOSI tests
  - LCGE multiplication across multiple individuals
```

**Setup cost:** $3,000-8,000 for incorporation with proper share structure. DIY incorporation ($200 online) does not include the multi-class share structure needed for income splitting. Pay the lawyer once, avoid tax complexity forever.

---

### 7.3 When CC Has a Partner/Spouse

**Immediate steps on marriage or common-law at 12 months:**

1. **Prescribed rate loan — lock in immediately.** Watch the quarterly rate announcement. If rates are at 2% or below, establish a loan on the first day of the quarter. A $100K+ loan at 1-2% locked in forever is worth $5,000-15,000+/year in lifetime tax savings. Set up automatic interest payments by January 15 each year.

2. **Spousal RRSP — begin contributions.** Use CC's RRSP room to contribute to the spousal RRSP. Every $1 contributed at CC's marginal rate (50%+) and withdrawn at the spouse's rate (20-30%) saves $0.20-0.30 in tax. Over 40 years, this compounds enormously.

3. **Employ the spouse if they contribute real work.** If the spouse is involved in OASIS (marketing, admin, bookkeeping, client relations), create an employment contract immediately. Document from day one. The spouse's reasonable salary is TOSI-proof, deductible to the corporation, and creates RRSP room for them.

4. **Family trust — consider establishing at this point.** Once there is a spouse (and potentially children in future), a family trust can be the central vehicle for LCGE multiplication and long-term income splitting. Cost: $3,000-8,000 for setup plus annual T3 filing ($500-1,500/year).

5. **Update corporate share structure to add Class B/C shares.** The spouse can subscribe for new shares at nominal value (if the trust is involved, the trust holds them). This begins the beneficiary structure.

---

### 7.4 When CC Has Children

**RESP — first priority, always:**

```
RESP contributions (per child):
  Annual contribution:                    $2,500
  CESG (20% match, max $500/year):        $500 government grant
  Lifetime CESG:                          $7,200 per child
  Annual family income > $49,020:         No additional ACESG
  Annual family income < $49,020:         Additional 10-20% CESG ($100-200/year extra)

  Child at 18 with $2,500/year + CESG + 6% growth:
    Total:                                ~$97,000
    Taxed at child's rate on withdrawal (usually 0-15%):
    Vs. no RESP (same money invested personally):
    Tax on growth at 40%+ rate:           saves $15,000-25,000
```

**Child employment (age 14+, genuine work):**

CRA permits deduction of wages paid to family members as young as 14 provided the work is real, documented, and compensated at market rates. Teenagers can provide legitimate services:
- Social media management
- Content creation
- Data entry and administrative tasks
- Testing and QA
- Research assistance

**At age 18+:** Employment continues as before. If the child works 20+ hours/week in the business continuously, they qualify for the "excluded business" test and dividends can be paid to them without TOSI even during ages 18-24.

**Family trust beneficiary:** Include children as beneficiaries from birth. They do not receive income until they qualify under TOSI tests, but they hold beneficial interests that can grow in value and qualify for LCGE on a future sale.

---

### 7.5 TOSI Planning Summary Timeline

```
Age 22 (Now):
  → No TOSI concerns. Build the foundation.
  → Maximize TFSA + FHSA.
  → Document CC's OASIS contributions in writing.

At Incorporation (~$80K revenue):
  → Set up multi-class share structure.
  → Document CC's foundational contribution to the corporation.
  → No income splitting possible yet — CC is the only shareholder.

When CC Has a Partner:
  → Prescribed rate loan immediately (watch for low rate quarters).
  → Spousal RRSP contributions begin.
  → Employment if spouse works in the business (document from day 1).
  → Consider family trust if planning children.

When CC Has Children:
  → RESP immediately (CESG = free money).
  → Employment from age 14+ (real work only).
  → Family trust if not already established (adds children as beneficiaries).

At Age 65+ (Retirement):
  → RRIF/RPP pension splitting.
  → RRSP meltdown strategy (see ATLAS_PENSION_RETIREMENT_GUIDE.md).
  → Capital gains harvesting to use remaining LCGE.

On Business Sale:
  → Purify OASIS Corp 2+ years in advance.
  → Confirm QSBC status.
  → Each family trust beneficiary claims LCGE on their share of proceeds.
  → Target: $0 capital gains tax up to $5M on a family of four.
```

---

## 8. Decision Trees

### 8.1 Does TOSI Apply to This Payment?

```
Is the payment SALARY or WAGES to a family member?
  YES → TOSI DOES NOT APPLY. Stop here. Document employment.
  NO → Continue.

Is the payment a DIVIDEND from OASIS Corp (or similar private corp)?
  YES → Continue.
  NO (e.g., interest on arm's length loan) → Lower risk, likely not TOSI. Review with CPA.

Is the recipient a "specified individual" (spouse, child, parent, sibling, niece/nephew)?
  NO (arm's length, unrelated) → TOSI DOES NOT APPLY. Stop here.
  YES → Continue.

How old is the recipient on December 31 of the tax year?
  Under 18 → TOSI APPLIES. No exclusions. Consider RESP instead.
  Ages 18-24 → Go to the 18-24 test (below).
  Ages 25+ → Go to the 25+ test (below).
  Ages 65+ → Go to the 65+ test (below).

--- 18-24 TEST ---
Does the individual actively work in the business ≥20 hours/week?
  YES → Excluded business applies → TOSI DOES NOT APPLY on this income.
  NO → Did they work ≥20 hrs/week in any 5 prior years?
    YES → Excluded business applies → TOSI DOES NOT APPLY.
    NO → Does the individual own 10%+ of shares AND the corp earns <90% from services?
      YES → Excluded shares may apply → verify all four conditions → potentially TOSI-free.
      NO → TOSI APPLIES at 53.53%.

--- 25+ TEST ---
Calculate the "reasonable return" cap:
  Step 1: Market rate × hours worked per year = labour contribution
  Step 2: Capital contributed × reasonable rate = capital return
  Step 3: Risk premium for personal guarantees or capital at risk
  Step 4: Sum = reasonable return cap

  Is the dividend ≤ reasonable return cap?
    YES → TOSI DOES NOT APPLY on this amount.
    NO → TOSI APPLIES on the EXCESS above the reasonable return cap.

--- 65+ TEST ---
Are the shares "excluded shares" AND does the amount qualify as pension income?
  YES → TOSI DOES NOT APPLY.
  NO → Fall back to 25+ reasonable return test.
```

---

### 8.2 Which Income Splitting Strategy Should I Use?

```
Do I have a family member who actually WORKS in the business?
  YES → Pay reasonable salary. Document everything. TOSI-proof. Also consider dividend
        component up to reasonable return (25+) or excluded business (18-24).
  NO → Continue.

Do I have a spouse with low income?
  YES → Is the prescribed rate currently low (≤2%)?
          YES → Establish prescribed rate loan immediately. Lock in rate.
          NO → Wait for a lower rate quarter. Meanwhile, maximize spousal RRSP.
        Regardless: Contribute to spousal RRSP using CC's room.
  NO → Continue.

Do I have children?
  YES → Open RESP. Contribute $2,500/year minimum (maximize CESG).
        At 14+: Consider part-time employment in business.
        At 18+: Consider "excluded business" qualification if they work 20+ hrs/week.
  NO → Continue.

Am I planning a future business sale?
  YES → Establish family trust NOW (before value accrues).
        Issue shares to trust beneficiaries.
        Each beneficiary gets their own $1.25M LCGE.
        Plan on a $0 tax exit up to $5M (family of 4).
  NO → Maintain current structure.

Is incorporation imminent?
  YES → Design multi-class share structure at incorporation.
        Get tax lawyer, not DIY online filing.
  NO → Document CC's sole proprietor contributions now for future incorporation.
```

---

## 9. Dollar-Amount Examples

### Example A — The TOSI Tax Cost (Baseline Horror Story)

**Situation:** CC incorporates OASIS at $120K revenue. CC and spouse are 50/50 shareholders. Spouse does nothing in the business. OASIS Corp pays $50K in dividends to each of CC and spouse.

**CC's dividend — no TOSI:**
```
CC receives $50,000 non-eligible dividend:
  Gross-up (15%):                          $57,500
  Combined marginal rate (~40% bracket):   ~40.13%
  Gross-up-adjusted tax:                   ~$23,075
  Federal dividend tax credit (9.0301%):   ($4,515)
  Ontario DTC (2.9863%):                   ($1,493)
  Net tax on $50,000 dividend:             ~$17,067 (34.1% effective)
```

**Spouse's dividend — TOSI applies:**
```
Spouse receives $50,000 non-eligible dividend:
  TOSI rate (Ontario top marginal):        53.53%
  TOSI tax:                                $26,765
  Dividend tax credit:                     DENIED under TOSI
  Effective rate:                          53.53%

  Without TOSI, if spouse earned $50K total income:
    Tax would be:                          ~$17,067
  TOSI penalty:                            $26,765 - $17,067 = $9,698 excess tax

  vs. CC keeping both dividends (CC pays CC's rate on $100K):
    CC's tax on $100K dividend:            ~$45,000
  After TOSI, family total:                $17,067 + $26,765 = $43,832

  Conclusion: TOSI nearly eliminated the splitting benefit AND was worse than
  CC keeping all $100K in some scenarios. No meaningful tax saving, high compliance
  cost, CRA audit risk. This is exactly what TOSI was designed to achieve.
```

---

### Example B — TOSI Defeated via Reasonable Salary

**Situation:** Same as above, but spouse works 15 hrs/week on OASIS client management and marketing (market rate $30/hr).

```
Reasonable salary calculation:
  15 hrs/week × $30/hr × 52 weeks:        $23,400

OASIS Corp pays spouse:
  Salary:                                 $23,400 (TOSI-proof, deductible to corp)
  Dividend (reasonable return — capital):  $0 (no capital contributed)
  Total to spouse:                        $23,400

  Corp deduction saves tax at 12.2%:      $23,400 × 12.2% = $2,855
  Spouse's tax on $23,400 salary:
    Federal BPA coverage:                 ($15,705)
    Ontario BPA coverage:                 ($11,865)
    Approximate net tax:                  ~$3,200
    CPP contributions:                    ~$1,150
    Total cost:                           ~$4,350

CC keeps remaining $96,600 in corporation.

  Family annual tax saving (salary strategy vs. no splitting):
    Without splitting: CC pays 53.53% on additional $23,400 = $12,526
    With splitting: spouse pays $4,350, corp saves $2,855 = net $1,495
    Annual saving:                        $12,526 - $1,495 = $11,031
```

---

### Example C — Prescribed Rate Loan Over 20 Years

**Situation:** CC earns $200K/year from OASIS. Future spouse has no other income. Prescribed rate is 2%. CC lends spouse $150,000 at 2%.

```
Year 1 setup:
  Loan amount:                            $150,000
  Rate locked at inception:               2% (permanent)
  Annual interest payable by spouse:      $3,000
  CC reports $3,000 interest income:
    At ~53.53%:                           $1,606 tax on interest

  Spouse invests $150,000 in balanced ETF portfolio (5% annual return):
    Annual return:                        $7,500
    Less interest paid to CC:             ($3,000)
    Net investment income to spouse:      $4,500
    Spouse's marginal rate:               ~20.05% (low income earner)
    Tax:                                  ~$902

  Vs. CC investing the $150,000 themselves:
    $7,500 return at CC's 53.53%:         $4,015 tax

  Annual tax saving Year 1:              $4,015 - ($1,606 + $902) = $1,507

  Over 20 years (portfolio grows, rates stay locked at 2%):
  Year 10 portfolio value (6% compound):  $268,611
  Year 10 annual return:                  $16,117
  Year 10 tax saving (approximately):     ~$4,500-6,000/year
  Total 20-year tax savings:             Conservatively $50,000-80,000+

  IMPORTANT: If CC missed the interest payment ONE YEAR (say year 7),
  the entire structure collapses permanently. Spouse must attribute
  all future income back to CC. The $50,000+ in savings over remaining
  13 years is gone. Set up automatic bank transfers.
```

---

### Example D — Family Trust on Business Sale

**Situation:** CC incorporates at 25, establishes family trust with spouse and 2 future children as beneficiaries. CC sells OASIS at age 40 for $3,000,000.

```
Without family trust:
  CC's capital gain:                      $3,000,000 - cost base
  CC's LCGE (2040, inflation-indexed ~$1.8M):  ($1,800,000)
  Remaining gain:                         $1,200,000
  Inclusion rate (2/3):                   $800,000
  Tax at ~50%:                            $400,000

With family trust (CC + spouse + 2 children = 4 beneficiaries):
  Each beneficiary's share of gain:       $750,000
  Each beneficiary's LCGE (2040):         $1,800,000 (indexed)
  LCGE covers full gain per person:       YES — all $750,000 per person
  Total capital gains tax:                $0

  Tax savings on the sale:                $400,000
  Trust setup and 15 years maintenance:  ~$30,000-50,000
  Net benefit:                           $350,000-370,000 after trust costs

This is the single most powerful tax strategy available to CC.
```

---

## 10. Key ITA References

| Section | Title | Relevance |
|---------|-------|-----------|
| **s.120.4** | Tax on split income | The main TOSI provision — the entire framework |
| **s.120.4(1)** | Definitions | "specified individual", "split income", "excluded business", "excluded shares", "excluded amount", "reasonable return" |
| **s.120.4(1.1)** | Capital gains exclusion | QSBC capital gains excluded from TOSI if individual contributed to business |
| **s.120.4(2)** | TOSI tax imposition | The actual tax calculation — top rate applied to split income |
| **s.120.4(4)** | Deemed dividend on capital gains | Certain private corp capital gains recharacterized as split income |
| **s.74.1** | Attribution — spouse and minors | Income on property transferred to spouse attributed back |
| **s.74.5** | Attribution exceptions | When attribution rules do NOT apply |
| **s.74.5(2)** | Prescribed rate loan exception | Attribution overridden when loan meets prescribed rate conditions |
| **s.56(4.1)** | Income splitting anti-avoidance | Catches circular arrangements where income is diverted back |
| **s.67** | Reasonableness of expenses | Salaries to family members must be "reasonable" |
| **s.110.6** | Lifetime capital gains exemption | $1.25M LCGE on QSBC shares (2026, indexed) |
| **s.110.6(1)** | QSBC share definition | Qualifying conditions for LCGE eligibility |
| **s.110.6(14)** | Purification rules | Active business asset test for QSBC qualification |
| **s.104** | Trusts | Trust taxation rules, income allocation, 21-year rule |
| **s.75(2)** | Reversionary trust rule | Attribution where property can revert to contributor |
| **s.107(2)** | Capital distribution from trust | Tax-free rollout to beneficiaries |
| **s.146(1)** | Spousal RRSP definition | Annuitant vs. contributor rules |
| **s.146(8.3)** | 3-year attribution rule | Spousal RRSP withdrawals attributed if contribution made in same/prior 2 years |
| **s.60.03** | Pension income splitting | Eligible pension income allocation to spouse |
| **Reg. 4301(c)** | Prescribed interest rate | CRA quarterly rate for prescribed rate loans |
| **s.251** | Related persons | Definition of "related" for attribution and TOSI |
| **s.251.1** | Affiliated persons | Broader affiliation rules for certain provisions |
| **s.86** | Share exchange | Tax-free exchange of shares on reorganization (useful for estate freeze) |
| **s.51** | Convertible property | Share-for-share exchange provisions |

---

## Appendix: TOSI Quick Reference Card

**Print this. Keep it with every year-end review.**

```
QUESTION: Does TOSI apply to this payment to a family member?

Step 1: Is it salary?             YES → Not TOSI. Done.
Step 2: Is it a dividend?         NO  → Review with CPA.
Step 3: Is recipient related?     NO  → Not TOSI. Done.
Step 4: Age?
  Under 18?                       → TOSI. Full stop. Use RESP.
  18-24?                          → Works ≥20 hrs/week? YES → Excluded business, not TOSI.
                                    Owns ≥10% of non-service corp? YES → Excluded shares, not TOSI.
                                    Neither? → TOSI. 53.53%.
  25+?                            → Calculate reasonable return.
                                    Dividend ≤ reasonable return? → Not TOSI.
                                    Dividend > reasonable return? → TOSI on excess.
  65+?                            → Pension income splitting available. → Not TOSI.

REASONABLE RETURN CAP (25+):
  Labour × market rate + Capital × return rate + Risk premium = cap
  Document annually. Keep in TOSI Defense Binder.

INCOME SPLITTING TOOLS (TOSI-SAFE, RANKED BY SIMPLICITY):
  1. Reasonable salary (simplest, always works)
  2. Spousal RRSP (retirement splitting, zero risk)
  3. Prescribed rate loan (watch for low rate quarters, lock in forever)
  4. Family trust (most powerful, requires lawyer)
  5. LCGE multiplication (best return on exit, requires advance planning)
```

---

*Document prepared by ATLAS CFO | CC's financial intelligence layer*
*Jurisdiction: Ontario, Canada | Updated: 2026-03-27*
*Companion documents: ATLAS_INCORPORATION_TAX_STRATEGIES.md, ATLAS_TAX_STRATEGY.md, ATLAS_WEALTH_PLAYBOOK.md*
*ITA references verified against R.S.C. 1985, c.1 (5th Supp.) as amended through 2024*
*This document does not constitute legal advice. CC reviews and makes all decisions. Atlas prepares, CC executes.*
