# ATLAS — Estate Planning, Succession & Wealth Transfer for Canadian Business Owners

> **Audience:** CC (primary) + any Canadian entrepreneur building a CCPC
> **Jurisdiction:** Ontario, Canada. Federal (ITA) + provincial rules. Cross-border notes for UK/Ireland/US.
> **Last updated:** 2026-03-27 | **Author:** ATLAS (CFO Agent)
> **Status:** Reference document. CC reviews with licensed estate lawyer and tax advisor before acting.
> **Companion docs:** `ATLAS_INSURANCE_ESTATE_PROTECTION.md` (COLI mechanics, insurance types), `ATLAS_INCORPORATION_TAX_STRATEGIES.md` (estate freeze s.86/s.85, QSBC purification), `ATLAS_TOSI_DEFENSE.md` (income splitting restrictions), `ATLAS_WEALTH_PLAYBOOK.md` (wealth transfer book strategies)

---

## Table of Contents

1. [Deemed Disposition at Death — s.70(5) ITA](#1-deemed-disposition-at-death--s705-ita)
2. [Probate and How to Avoid It](#2-probate-and-how-to-avoid-it)
3. [Estate Freeze — Deep Dive](#3-estate-freeze--deep-dive)
4. [Family Trusts](#4-family-trusts)
5. [Succession Planning for Business Owners](#5-succession-planning-for-business-owners)
6. [Life Insurance as Estate Planning Tool](#6-life-insurance-as-estate-planning-tool)
7. [Power of Attorney and Incapacity Planning](#7-power-of-attorney-and-incapacity-planning)
8. [Digital Asset Estate Planning](#8-digital-asset-estate-planning)
9. [Charitable Giving Strategies](#9-charitable-giving-strategies)
10. [Cross-Border Estate Issues](#10-cross-border-estate-issues)
11. [Tax-Efficient Wealth Transfer Strategies](#11-tax-efficient-wealth-transfer-strategies)
12. [CC's Estate Planning Action Items](#12-ccs-estate-planning-action-items)

---

## 1. Deemed Disposition at Death — s.70(5) ITA

### The Core Rule: You Die, CRA Gets Paid

When a Canadian resident dies, the Income Tax Act treats every capital property they own as having been sold at fair market value (FMV) immediately before death. This is not optional. There is no Canadian estate tax — instead, Canada uses this deemed disposition mechanism to collect tax on accrued gains.

**ITA s.70(5)(a):** The taxpayer is deemed to have disposed of each capital property immediately before death for proceeds equal to FMV.

The practical effect: every unrealized gain that accumulated during the taxpayer's lifetime becomes taxable on their final tax return. The estate (or the estate's executor/liquidator) must file a final T1 return covering January 1 to the date of death, reporting all deemed dispositions.

```
Example — CC dies owning the following (hypothetical future state):

  OASIS Corp shares:    ACB = $100        FMV = $2,000,000
  TFSA:                 ACB = $50,000     FMV = $180,000
  Crypto (personal):    ACB = $15,000     FMV = $95,000
  Principal residence:  ACB = $400,000    FMV = $750,000
  RRSP:                 Balance = $300,000

Deemed disposition triggers:
  OASIS shares:     Capital gain = $1,999,900  →  Taxable (50%) = $999,950
  Crypto:           Capital gain = $80,000     →  Taxable (50%) = $40,000
  RRSP:             Full balance = income      →  $300,000
  TFSA:             No tax (see below)
  Principal res:    PRE eliminates gain (see below)

  Total income on final return: ~$1,339,950
  Federal + Ontario tax at top rates: ~$700,000+
```

That is the problem estate planning solves. Without planning, CRA takes roughly 35-53% of every unrealized gain at death.

### 1.1 Spousal Rollover — s.70(6)

The most important deferral at death. If capital property passes to a surviving spouse or common-law partner (or to a spousal trust), the deemed disposition is deferred — the property transfers at the deceased's ACB, not FMV.

**ITA s.70(6):** Property that vests indefeasibly in the spouse within 36 months of death (or longer if the court allows) rolls over at ACB. No tax on the first death.

**Requirements:**
- Property must vest indefeasibly in the spouse (they must become the absolute owner, not a conditional beneficiary)
- The spouse must be a Canadian resident at the time of death
- The executor can elect OUT of the rollover (s.70(6.2)) — useful if the deceased has unused LCGE or losses

**What qualifies:**
- All capital property: real estate, shares, bonds, partnership interests, crypto
- RRSP/RRIF: rolls to spouse's RRSP/RRIF tax-free (see below)
- TFSA: successor holder designation (see below)

**What does NOT qualify:**
- Property left to children, siblings, parents, or anyone other than a spouse
- Property left to a non-resident spouse (fails the Canadian residency test)

**Planning implication for CC (currently unmarried):** This rollover is not available. Every capital property CC owns will face full deemed disposition at death. This makes other planning tools (estate freeze, life insurance, LCGE crystallization) even more critical.

```
Spousal rollover example:

  CC dies. Spouse inherits OASIS Corp shares (ACB $100, FMV $2M).
  s.70(6) rollover: Spouse takes shares at ACB = $100. No tax on CC's death.
  When spouse eventually disposes (sale or their own death):
    Capital gain = FMV at spouse's disposition − $100

  Tax deferred, not eliminated. The gain crystallizes on the second death.
```

### 1.2 Graduated Rate Estate (GRE) — 36-Month Window

A Graduated Rate Estate is a testamentary trust that forms on death and qualifies for graduated personal tax rates (instead of the flat top rate that applies to most trusts). It is the ONLY type of trust that gets graduated rates.

**ITA s.248(1) "graduated rate estate":** An estate that arises on death, is designated in the estate's first T3 return, and meets the following conditions for up to 36 months after death:
- It is a testamentary trust (created by will or on intestacy)
- No more than 36 months have passed since the individual's death
- The estate designates itself as a GRE in its first T3 filing
- Only one estate per individual can be a GRE
- The estate's SIN must be reported

**Why it matters:** Normal trusts pay the top marginal rate on all income (53.53% in Ontario). A GRE pays graduated rates — the same brackets as an individual. On the final return + GRE, the estate effectively gets two sets of graduated brackets.

**GRE benefits:**
- Graduated tax rates for up to 36 months
- Can carry back losses to the deceased's final return (s.164(6))
- Can claim donation credits on the deceased's final return or the estate's returns
- Can designate a principal residence (one of the few trusts that can)
- Can use an off-calendar fiscal year-end (tax deferral opportunity)

```
GRE graduated rate benefit:

  Estate earns $200,000 in Year 1:

  WITHOUT GRE (regular trust):
    All $200,000 taxed at 53.53% = $107,060

  WITH GRE (graduated rates, Ontario 2026):
    First $55,867:  ~20% combined = $11,173
    $55,867-$111,733: ~30% combined = $16,760
    $111,733-$154,906: ~37% combined = $15,974
    $154,906-$200,000: ~46% combined = $20,743
    Total tax: ~$64,650

  GRE saves: ~$42,410 on $200K of estate income
```

**36-month deadline:** After 36 months, the GRE becomes an ordinary trust taxed at the top rate. The executor should wind up the estate within 36 months if possible. Any property remaining in the estate after 36 months loses the GRE advantage.

### 1.3 Principal Residence Exemption at Death

The principal residence exemption (PRE) under s.40(2)(b) can be claimed on the final return to eliminate the capital gain on a home.

**Rules at death:**
- The deemed disposition at FMV triggers a gain on the home
- The executor claims the PRE on the final return using Form T2091
- PRE formula: Gain x (1 + years designated) / years owned
- If the home was the taxpayer's principal residence for every year owned: full exemption, zero tax
- Only ONE principal residence per family unit per year (spouse + minor children)

**CC relevance:** CC does not currently own real estate. If CC purchases a home (potentially using the FHSA), the PRE protects it at death.

### 1.4 RRSP/RRIF Collapse at Death

RRSPs and RRIFs receive harsh treatment at death. The entire balance is included in the deceased's income on the final return.

**ITA s.146(8.8):** The RRSP is deemed to pay the full FMV of all property held in the plan to the annuitant (deceased) immediately before death.

```
RRSP at death:

  RRSP balance: $300,000
  Deemed income on final return: $300,000
  Tax at top Ontario rate (53.53%): $160,590
  Amount received by beneficiaries: $139,410

  The RRSP effectively loses 54% of its value to tax at death.
```

**Exceptions — Tax-Free Rollovers:**

| Beneficiary | ITA Section | Treatment |
|-------------|-------------|-----------|
| Spouse / common-law partner | s.146(8.1) | Rolls to spouse's RRSP/RRIF tax-free |
| Financially dependent child/grandchild (under 18) | s.146(8.1) | Can purchase term annuity to age 18 |
| Financially dependent child/grandchild (any age, if infirm) | s.146(8.1) | Rolls to RDSP or RRSP |
| Anyone else | No rollover | Full balance = income on final return |

**Designation vs. will:** Name the spouse as RRSP beneficiary directly with the financial institution. This bypasses the estate (and probate) entirely. If the RRSP has no beneficiary designation, it falls into the estate — subject to probate fees AND possible delays.

**CC now:** No RRSP balance. But once CC starts contributing, beneficiary designation is critical.

### 1.5 TFSA at Death — Successor Holder vs. Beneficiary

TFSA treatment at death depends entirely on whether the surviving person is named as a **successor holder** or a **beneficiary**. These are NOT the same.

| Designation | Who Can Be Named | What Happens | Tax Treatment |
|-------------|-----------------|--------------|---------------|
| **Successor holder** | Spouse/common-law partner ONLY | TFSA continues under spouse's name — seamless transition | No tax. Growth continues tax-free. Does not affect spouse's own TFSA room. |
| **Beneficiary** | Anyone (spouse, child, charity, etc.) | TFSA assets distributed to beneficiary. TFSA ceases to exist. | Value at date of death = tax-free. Growth BETWEEN death and distribution = TAXABLE to beneficiary. |
| **No designation** | N/A — falls into estate | Assets go through will/probate | Same as beneficiary: value at death tax-free, subsequent growth taxable. Plus probate fees apply. |

**The successor holder advantage is enormous.** The TFSA simply continues — no tax, no probate, no interruption. Always designate a spouse as successor holder (not beneficiary) if possible.

**CC now:** TFSA at Wealthsimple ($155). No spouse currently. Designate a beneficiary (parent or sibling) so the TFSA does not fall into the estate.

### 1.6 FHSA at Death

The First Home Savings Account has specific death rules:

| Situation | Treatment |
|-----------|-----------|
| Spouse/common-law partner designated as successor holder | FHSA continues under spouse's name (they must be eligible FHSA holder or transfer to RRSP within 1 year) |
| Spouse who is NOT an eligible FHSA holder | Must transfer to RRSP (no RRSP room required) or withdraw (taxable) within 1 year |
| Non-spouse beneficiary | Full FMV = taxable income on deceased's final return |
| No designation | Falls into estate, full FMV = taxable income |

**CC now:** FHSA opened 2026-03-27 at Wealthsimple, $0 balance. Once funded, designate a beneficiary.

---

## 2. Probate and How to Avoid It

### What Probate Is

Probate is the court process that validates a will and grants the executor legal authority to administer the estate. In Ontario, probate is formally called "Certificate of Appointment of Estate Trustee."

The problem is not the process — it is the tax.

### 2.1 Ontario Probate Fees (Estate Administration Tax)

Ontario charges the highest probate fees in Canada:

| Estate Value | Rate |
|-------------|------|
| First $50,000 | 0.5% ($250 max) |
| Over $50,000 | 1.5% |

**ITA:** Ontario Estate Administration Tax Act, 1998. Not technically income tax — it is a provincial levy on the value of assets that pass through the will.

```
Example — Estate valued at $2,000,000:

  First $50,000:     $50,000 × 0.5% = $250
  Remaining:         $1,950,000 × 1.5% = $29,250
  Total probate fee: $29,500

  On a $5M estate: $74,750
  On a $10M estate: $149,750
```

These fees are calculated on the GROSS value of the estate — not net of debts. A property worth $1M with a $900K mortgage pays probate on the full $1M.

**What goes through probate:**
- Assets held in the deceased's name alone
- Assets passing under the will
- Real property held solely by the deceased
- Bank accounts with no joint holder or beneficiary

**What does NOT go through probate:**
- Assets with designated beneficiaries (RRSP, TFSA, FHSA, life insurance)
- Jointly held property with right of survivorship
- Assets held in trusts
- Private company shares addressed by a secondary will (see below)
- Property transferred during lifetime (inter vivos gifts)

### 2.2 Multiple Wills Strategy

The most common probate avoidance tool for business owners in Ontario. The concept was validated in *Granovsky Estate v. Ontario* (1998) — the Ontario court confirmed that a secondary will dealing only with private company shares does not need to be probated.

**How it works:**

| Will | Covers | Probated? |
|------|--------|-----------|
| **Primary will** | Assets that REQUIRE probate: real estate, bank accounts, publicly traded securities, personal property | YES — submitted to court for Certificate of Appointment |
| **Secondary will** | Private company shares (CCPC shares), personal loans receivable, jewelry, art, other assets where no third party requires a probated will | NO — executor acts under the secondary will without court involvement |

**Why private company shares don't need probate:** The corporation's directors/officers recognize the secondary will directly. No bank, land registry, or transfer agent needs a court certificate. The company's minute book is updated, and new share certificates are issued.

```
Example — CC's future estate with dual wills:

  Total estate value: $3,000,000
    OASIS Corp shares:    $2,000,000 (secondary will)
    Real estate:          $750,000 (primary will)
    Bank accounts:        $150,000 (primary will)
    Personal property:    $100,000 (primary will)

  WITHOUT dual wills:
    Probate on $3,000,000: $44,500

  WITH dual wills:
    Primary will: $1,000,000 → probate = $14,500
    Secondary will: $2,000,000 → probate = $0

    Savings: $30,000
```

**Requirements:**
- Both wills must be drafted by the SAME lawyer at the SAME time
- Both wills must cross-reference each other
- The primary will must not revoke the secondary will (carefully worded revocation clauses)
- Cost: $2,000-$5,000 for dual will preparation (Ontario estate lawyer)

**CRA audit risk:** NONE. This is standard Ontario estate practice endorsed by the courts.

### 2.3 Joint Ownership with Right of Survivorship

When property is held jointly with right of survivorship (JTWROS), the surviving joint owner automatically becomes the sole owner at death — no probate required.

**Common uses:**
- Joint bank accounts (parent + child)
- Joint real estate ownership (spousal)
- Joint investment accounts

**Tax traps:**

| Issue | Explanation |
|-------|-------------|
| Attribution rules | If CC adds a parent as joint owner of an investment account, income may be attributed back to CC (s.74.1) |
| Deemed disposition on adding joint owner | Adding a joint owner IS a disposition of 50% of the property — capital gain triggered (ITA s.69(1)) unless an exemption applies |
| Creditor risk | Joint owner's creditors can access the jointly held property |
| Loss of control | Joint owner can withdraw funds, refuse to sell, or create complications |
| Perot v. Perot problem | On the joint owner's death FIRST, their 50% goes to THEIR estate, not back to the original owner |

**Best practice:** Use joint ownership only for bank accounts with a spouse (for convenience) and real estate with a spouse. Do NOT use for investment accounts or business assets — too many tax traps.

### 2.4 Beneficiary Designations

The simplest probate avoidance tool. Name a beneficiary directly on:

| Account | Designation Type | Bypasses Probate? |
|---------|-----------------|-------------------|
| RRSP/RRIF | Beneficiary or successor annuitant (spouse) | YES |
| TFSA | Successor holder (spouse) or beneficiary | YES |
| FHSA | Successor holder (spouse) or beneficiary | YES |
| Life insurance | Named beneficiary | YES (if not "estate") |
| Segregated funds | Named beneficiary | YES |
| Group RRSP/pension | Named beneficiary | YES |

**Critical mistake:** Naming the "estate" as beneficiary on a life insurance policy. This pulls the insurance proceeds INTO the estate — subject to probate fees and creditor claims. Always name a specific person or trust as beneficiary.

### 2.5 Inter Vivos (Living) Trusts

An inter vivos trust is created during the settlor's lifetime. Assets transferred to the trust are no longer in the settlor's estate — they bypass probate entirely.

**Types relevant to estate planning:**

| Trust Type | Age Requirement | Tax Treatment | Probate Bypass? |
|------------|----------------|---------------|-----------------|
| **Alter ego trust** | 65+ | Deemed disposition deferred to death of settlor | YES |
| **Joint partner trust** | 65+ (either partner) | Deferred to death of surviving partner | YES |
| **Family trust** | None | Top marginal rate on undistributed income; 21-year rule | YES |
| **Bare trust** | None | Transparent — income taxed to beneficiary | YES (if properly structured) |

**Alter ego and joint partner trusts (s.73(1), s.73(1.01)):**
- Available at age 65+ only
- Transfer property to the trust at ACB (no tax on transfer)
- Deemed disposition occurs at the settlor's death (alter ego) or last surviving partner's death (joint partner)
- Avoids probate entirely
- Avoids publicity (probated wills are public documents)

**For CC at age 22:** Alter ego/joint partner trusts are not available for 43 years. The relevant tools now are beneficiary designations, dual wills at incorporation, and family trusts at the appropriate income level.

### 2.6 Cost-Benefit Analysis of Probate Avoidance

| Strategy | Setup Cost | Annual Cost | Probate Savings (on $2M estate) | Break-Even |
|----------|-----------|-------------|--------------------------------|------------|
| Beneficiary designations | $0 | $0 | Variable (depends on assets) | Immediate |
| Dual wills | $2,000-$5,000 | $0 (update every 5 years ~$1K) | $15,000-$30,000 | Immediate at incorporation |
| Joint ownership | $0-$500 | $0 | Up to $29,500 | Immediate, but tax traps |
| Inter vivos trust | $3,000-$10,000 | $1,500-$3,000 (T3 filing) | Up to $29,500 | 2-5 years depending on estate |
| Alter ego trust | $5,000-$15,000 | $1,500-$3,000 (T3 filing) | Up to $29,500 | 3-7 years |

---

## 3. Estate Freeze — Deep Dive

> Cross-reference: `ATLAS_INCORPORATION_TAX_STRATEGIES.md` Section 6 covers the basic mechanics of s.86 and s.85 freezes. This section goes deeper into planning, timing, LCGE multiplication, and the refreeze strategy.

### 3.1 What an Estate Freeze Actually Does

An estate freeze is a corporate reorganization that converts the current owner's equity into fixed-value shares and issues new growth shares to the next generation (directly or through a trust). The effect:

```
Before freeze:
  CC owns 100% of OASIS Corp
  Current FMV: $1,000,000
  CC's deemed disposition at death: $999,900 gain (ACB $100)
  Tax at death: ~$266,000 (at 2026 capital gains rates)

After freeze:
  CC holds: preferred shares frozen at $1,000,000
  Family trust holds: new common shares (current value: $0)

  5 years later, OASIS Corp is worth $3,000,000:
    CC's deemed disposition at death: still $999,900 (frozen value)
    Tax at death: still ~$266,000
    $2,000,000 of growth belongs to trust beneficiaries — NOT taxed on CC's death

  Without freeze:
    CC's deemed disposition: $2,999,900
    Tax at death: ~$800,000+
```

The freeze saved $534,000 in tax on $2M of post-freeze growth.

### 3.2 Section 86 — Share Exchange (The Standard Freeze)

**ITA s.86(1):** When a shareholder exchanges ALL shares of a particular class for shares of a new class as part of a reorganization of capital, the exchange is tax-deferred if:
- No boot (non-share consideration) is received, or
- Boot does not exceed the ACB of the old shares

**Step-by-step mechanics:**

1. **Amend corporate articles** — Create a new class of preferred shares (Class A Preferred) with these attributes:
   - Fixed redemption value equal to current FMV of the company
   - Retractable (holder can force the company to redeem)
   - Non-participating (no share of future growth beyond redemption value)
   - Voting (CC retains control)
   - Cumulative dividend right (optional — ensures CC can still extract income)

2. **Exchange old common shares for new preferred shares** — CC surrenders all common shares and receives preferred shares with redemption value = current FMV.

3. **Issue new common shares** — New common shares (nominal value, $1 each) issued to:
   - A family trust (most common — see Section 4)
   - CC's children directly (simpler but less flexible)
   - A new holding company

4. **File corporate minute book** — Directors' resolution, shareholders' resolution, amended articles, new share certificates. All documented in the corporate minute book.

**Tax consequences:**
- CC's ACB in new preferred = ACB of old common shares ($100 if incorporated at nominal cost)
- PUC of new preferred = PUC of old common
- No capital gain triggered (deferred to redemption, sale, or death)
- FMV of preferred = FMV of old common (the "frozen" amount)

### 3.3 Section 85 — The Flexible Freeze with LCGE Crystallization

**When to use s.85 instead of s.86:**
- You want to crystallize the LCGE (claim the $1.25M capital gains exemption NOW)
- You want to transfer specific assets, not all shares of a class
- You want to elect a specific agreed amount

**ITA s.85(1):** Transfer of eligible property to a taxable Canadian corporation. The transferor and the corporation jointly elect an agreed amount between the ACB floor and FMV ceiling.

**LCGE crystallization through s.85:**

```
CC's OASIS Corp qualifies as QSBC (90%+ active business assets).
LCGE for QSBC shares (2025+): $1,250,000

Step 1: CC creates Holdco
Step 2: CC transfers OASIS shares to Holdco via s.85 election
Step 3: Elect agreed amount = ACB + LCGE available

  ACB of OASIS shares: $100
  FMV of OASIS shares: $1,500,000
  Elected amount: $1,250,100 (ACB + $1.25M LCGE)
  Capital gain: $1,250,000
  Taxable capital gain (50%): $625,000
  LCGE deduction (s.110.6(2.1)): ($625,000)
  NET TAX = $0

Step 4: CC receives Holdco preferred shares with ACB = $1,250,100
         (stepped up from $100 — enormous improvement)
Step 5: New Holdco common shares issued to family trust
Step 6: All growth above $1,250,100 accrues to trust

Result: $1.25M of gain crystallized tax-free
        CC's new ACB = $1,250,100 (was $100)
        Deemed disposition at CC's death: FMV − $1,250,100 (not FMV − $100)
```

### 3.4 LCGE Multiplication — The Family Trust Advantage

The Lifetime Capital Gains Exemption is available to EACH individual. By involving family members through a trust, multiple LCGEs can shelter the same company's value.

**CC's family:**
- CC: $1.25M LCGE
- Mom: $1.25M LCGE
- Dad: $1.25M LCGE
- Sister 1: $1.25M LCGE
- Sister 2: $1.25M LCGE

**Total family LCGE: $6.25M**

**How to access multiple LCGEs:**

1. Estate freeze: CC freezes at current value, new common shares to family trust
2. Trust beneficiaries: CC, mom, dad, sister 1, sister 2
3. When OASIS is eventually sold (or shares redeemed), the trust allocates capital gains to each beneficiary
4. Each beneficiary claims their own LCGE against their share of the gain

```
OASIS Corp sold for $5,000,000:

  CC's frozen preferred shares: $1,250,100 (ACB after crystallization)
  Remaining $3,749,900 of growth held by trust common shares

  Trust allocates $3,749,900 gain across 4 beneficiaries (mom, dad, 2 sisters):
    Each receives ~$937,475 capital gain
    Each claims LCGE: up to $1.25M available
    Each pays: $0 tax (gain within their LCGE)

  CC's preferred shares redeemed:
    Gain = $0 (already crystallized via s.85)

  TOTAL TAX ON $5M SALE: $0

  Without planning:
    CC pays tax on $4,999,900 gain
    Taxable capital gain: $2,499,950
    Tax: ~$1,300,000

  Estate freeze + LCGE multiplication saved: ~$1,300,000
```

**TOSI warning:** Allocating gains to family members through a trust triggers TOSI analysis (s.120.4). The capital gain on sale of QSBC shares is generally exempt from TOSI if the shares qualify as "excluded shares" — the trust held them for 24+ months and the company is not a professional corporation. See `ATLAS_TOSI_DEFENSE.md` for the full analysis.

### 3.5 Refreezing — When the Company Value Drops

If OASIS Corp's value decreases after the freeze, CC is frozen at a value higher than the current FMV. This means CC would be paying tax on a gain that no longer exists.

**The refreeze:**

1. Exchange CC's preferred shares (frozen at $1M) for new preferred shares (frozen at current FMV, say $600K)
2. The trust's common shares are also exchanged for new common shares
3. The entire capital structure is reset at the lower value

**Tax implication:** The refreeze itself should be tax-neutral if structured as another s.86 exchange. Professional advice is essential — CRA scrutinizes refreezes for abusive transactions.

**When to refreeze:**
- Material decline in business value (>20%)
- Market downturn affecting private company valuations
- Before a planned exit (ensures frozen value matches actual proceeds)

### 3.6 Professional Cost and Timing

| Component | Cost Range | Provider |
|-----------|-----------|----------|
| Legal (articles, share exchange, minute book) | $5,000-$12,000 | Corporate/tax lawyer |
| Accounting (valuation, tax elections, T2057) | $3,000-$8,000 | Tax accountant/CPA |
| Business valuation (formal, for CRA defense) | $5,000-$25,000 | CBV (Chartered Business Valuator) |
| Total simple freeze (s.86) | $8,000-$20,000 | |
| Total complex freeze (s.85 + LCGE) | $15,000-$35,000 | |

**When to freeze — timing principles:**
- BEFORE significant value appreciation (freeze locks current value — future growth is the goal)
- AFTER incorporation but before the next growth phase
- When company value is defensibly low (easier to justify a low frozen value)
- NOT during active negotiations for a sale (CRA may challenge the timing as abusive)

**CC timing:** The freeze should happen shortly after OASIS incorporates (at the $80K trigger), when the company value is still modest ($50K-$200K range). Freezing at $100K instead of $2M saves $500K+ in future tax.

---

## 4. Family Trusts

### 4.1 Types of Trusts

| Type | Created | Tax Rate | Key Feature |
|------|---------|----------|-------------|
| **Inter vivos (living) trust** | During lifetime | Top marginal (53.53% Ontario) on undistributed income | Flexible — can sprinkle income to beneficiaries |
| **Testamentary trust** | At death (in will) | Top marginal rate (except GRE for 36 months) | Created by will, activated at death |
| **Alter ego trust** | During lifetime, age 65+ | Top marginal on undistributed income; deferred until settlor's death | No deemed disposition on transfer |
| **Spousal trust** | During lifetime or at death | Top marginal; deferred until spouse's death | Income payable to spouse during lifetime |
| **Bare trust** | During lifetime | Transparent — taxed to beneficiary directly | Simplest structure; no T3 required in some cases |

### 4.2 The 21-Year Deemed Disposition Rule

**ITA s.104(4):** Every 21 years, a trust is deemed to have disposed of all its capital property at FMV. This is the government's mechanism to prevent property from being locked in trusts indefinitely, avoiding deemed disposition at death.

**Why 21 years:** It roughly corresponds to a generation. Without this rule, a family could keep property in trust forever, deferring capital gains indefinitely.

```
Example:

  Family trust holds OASIS Corp common shares:
    Year 0 (trust creation): ACB = $100, FMV = $100
    Year 21: FMV = $5,000,000
    Deemed disposition at Year 21:
      Capital gain: $4,999,900
      Taxable (50%): $2,499,950
      Tax at trust top rate (53.53%): $1,338,023
```

**Strategies to manage the 21-year rule:**

1. **Distribute shares to beneficiaries before Year 21** — Rollover at ACB (s.107(2)). No tax on rollout, but the beneficiaries now hold the shares personally and will face their own deemed disposition at death.

2. **Distribute shares and refreeze** — Roll shares out to beneficiaries, then do a new estate freeze into a new trust. Resets the 21-year clock.

3. **Trigger gain strategically** — If the gain is within the beneficiaries' LCGE room, distribute and have each beneficiary crystallize the exemption.

4. **Wind up the trust** — Distribute all assets to beneficiaries and terminate the trust.

**CC planning:** If CC creates a family trust at age 25 (upon incorporation), the 21-year deemed disposition hits at age 46 — still in CC's prime earning years. Plan the exit strategy well before Year 21.

### 4.3 Income Splitting Through Trusts — TOSI Restrictions

Before 2018, family trusts were the ultimate income-splitting tool. The trust would receive dividends from the family corporation and distribute them to lower-income family members.

Post-2018, TOSI (s.120.4) imposes the top marginal rate on split income unless an exclusion applies. The key exclusions:

| Beneficiary | Age | Exclusion Available? | Condition |
|-------------|-----|---------------------|-----------|
| Spouse | Any | Excluded business income | Spouse is 25+, actively and regularly works in the business for 20+ hours/week |
| Adult child | 25+ | Excluded shares | Owns 10%+ of votes and value; corporation earns <90% of income from services; not a professional corp |
| Adult child | 18-24 | Excluded business income only | Must work 20+ hours/week, or own excluded shares (harder to meet) |
| Parent | Any | Excluded business income | Same tests as spouse |
| Minor child | Under 18 | Almost never | TOSI applies to virtually all income |

**Practical impact for CC:**
- Mom (works in family restaurant, not OASIS): TOSI likely applies to dividends from OASIS trust unless she works 20+ hours/week for OASIS
- Dad (lives in Ireland): Foreign resident — TOSI does not apply to non-resident individuals (s.120.4(1) "specified individual" must be Canadian resident), BUT non-resident withholding tax (Part XIII, 25% or treaty rate) applies instead
- Sisters (age 25+, presumably): Could qualify for excluded shares exclusion if they hold 10%+ of the trust's allocated shares through an excluded business

**Bottom line:** TOSI makes trust-based income splitting harder but not impossible. The estate freeze + trust structure still works for capital gains (LCGE multiplication) and for distributions to family members who meet the excluded business income or excluded shares tests. See `ATLAS_TOSI_DEFENSE.md` for detailed strategies.

### 4.4 Trust Taxation

| Income Type | If Distributed to Beneficiary | If Retained in Trust |
|-------------|------------------------------|---------------------|
| Business income | Taxed at beneficiary's marginal rate | 53.53% (Ontario top rate) |
| Capital gains | 50% inclusion, beneficiary's rate | 50% inclusion, 53.53% |
| Eligible dividends | Grossed up, beneficiary's rate + DTC | Grossed up, 39.34% effective |
| Non-eligible dividends | Grossed up, beneficiary's rate + DTC | Grossed up, 47.74% effective |
| Interest/rental | Beneficiary's marginal rate | 53.53% |

**Rule of thumb:** NEVER retain income in a trust. Always distribute to beneficiaries (or make the income "payable" to them by the trust's fiscal year-end) to avoid the punitive flat top rate.

### 4.5 Trust Reporting Requirements

Since 2023, ALL trusts (including bare trusts, with limited exceptions) must file a T3 return and report:
- All trustees, beneficiaries, and settlors
- Beneficial ownership information (UBO)
- Full financial reporting

**Penalties for non-filing:** $25/day, minimum $100, maximum $2,500 (standard late-filing). Gross negligence: 5% of trust assets.

**Annual filing cost:** $1,500-$3,000 (accountant-prepared T3 return for a family trust).

---

## 5. Succession Planning for Business Owners

### 5.1 Internal Succession — Key Employee Buyout

The simplest succession: a trusted employee or group of employees purchases the business.

**Structure options:**
- **Share purchase:** Employee buys CC's shares. CC gets capital gains treatment (50% inclusion). Employee's cost = purchase price (their new ACB).
- **Asset purchase:** The corporation sells its assets to a new entity owned by the employee. More complex, but allows the buyer to claim CCA on the purchased assets (fresh cost base).

**Financing:** Key employees rarely have the capital. Common solutions:
- Vendor take-back mortgage (CC finances the purchase over 5-10 years)
- Capital gains reserve (s.40(1)(a)(iii)): CC can spread the gain over up to 5 years if purchase price is not all received in the year of sale
- Bank financing (employee borrows, CC guarantees initially)

### 5.2 External Sale — Strategic Buyer or PE Firm

**Types of buyers:**

| Buyer Type | Typical Multiple | CC's Control Post-Sale | Speed |
|-----------|-----------------|----------------------|-------|
| Strategic buyer (competitor, larger company) | 4-8x EBITDA | None — clean exit | 6-12 months |
| Private equity | 5-10x EBITDA | Partial — PE wants CC to stay 2-3 years | 6-18 months |
| Individual buyer (entrepreneur) | 2-5x EBITDA | None — clean exit | 3-12 months |

**AI/SaaS multiples (2025-2026 market):**
- SaaS with >$1M ARR: 5-12x ARR (depending on growth rate, churn, NRR)
- AI services/consulting: 1-3x revenue (lower than pure SaaS)
- OASIS (hybrid AI consulting + SaaS): likely 2-5x revenue at current scale

**Tax optimization on sale:**
- LCGE: up to $1.25M tax-free on QSBC share sale
- LCGE multiplication through family trust (see Section 3.4)
- Capital gains reserve to spread gain over 5 years
- Share sale vs asset sale: CC should almost always sell SHARES (capital gains) rather than have the corp sell assets (corporate tax + personal tax on extraction)

### 5.3 Management Buyout (MBO)

A management team purchases the company from the owner, typically with significant leverage.

**Structure:**
1. Management team forms Newco (acquisition vehicle)
2. Newco borrows from bank/mezzanine lender
3. Newco acquires CC's shares (or the company's assets)
4. Debt is repaid from the company's future cash flows

**CC relevance:** If OASIS grows to a team of 5-10, the senior employees may want to buy CC out. MBO allows this without finding an external buyer.

### 5.4 Employee Ownership Trust (EOT) — Budget 2024 Changes

The 2024 federal budget introduced a powerful new tool: the Employee Ownership Trust.

**Key features:**
- On sale of a qualifying business to an EOT: **up to $10 million in capital gains exempt from tax**
- The EOT must be a Canadian-resident trust
- The business must be a CCPC
- The trust must be for the benefit of the employees
- The 10-year capital gains exemption applies to the first $10M of gains (in addition to the LCGE)

**Combined exemption:**
```
CC sells OASIS to an EOT:

  Sale price: $12,000,000
  ACB: $100
  Capital gain: $11,999,900

  LCGE: $1,250,000 exempt
  EOT exemption: $10,000,000 exempt
  Remaining taxable gain: $749,900
  Taxable capital gain (50%): $374,950
  Tax (~48%): $179,976

  Effective tax rate on $12M sale: 1.5%

  Without EOT or LCGE:
  Taxable capital gain: $5,999,950
  Tax: ~$2,880,000

  Savings: ~$2,700,000
```

**Conditions:**
- Must be a genuine employee ownership transition (not a sham)
- CC cannot retain control or be a beneficiary of the EOT
- Employees must have genuine economic interest
- The business must continue to operate

### 5.5 Intergenerational Business Transfer — Bill C-208

Before 2021, selling shares to a child's corporation was treated as a dividend (not a capital gain) under s.84.1. Bill C-208 (effective June 29, 2021, refined in 2024) changed this:

**Old rule:** Parent sells CCPC shares to child's holding company. CRA treats excess over PUC as a dividend (no LCGE, no capital gains treatment). Effective tax rate: up to 47.74% (non-eligible dividend rate in Ontario).

**New rule:** If specific conditions are met, the sale is treated as a capital gain — eligible for LCGE treatment.

**Conditions (2024 rules):**
- The purchaser corporation must be controlled by one or more children/grandchildren (age 18+)
- The business must be transferred within 36 months (immediate transfer) or 5-10 years (gradual transfer)
- Parent must transfer legal AND factual control
- Parent cannot continue to control the business indirectly
- An independent assessment of FMV is recommended (not mandatory but CRA expects it)
- Parent must file an election and specific forms

**CC relevance:** If CC has children in the future and wants to transfer OASIS to them, Bill C-208 ensures the transfer gets capital gains treatment (and LCGE eligibility) instead of punitive dividend treatment.

### 5.6 Valuation Methods for Private Businesses

Any succession event requires a defensible business valuation. CRA will challenge valuations that appear artificially low.

| Method | How It Works | Best For | OASIS Relevance |
|--------|-------------|----------|-----------------|
| **DCF (Discounted Cash Flow)** | Project future cash flows, discount to present value at WACC | High-growth companies, SaaS/recurring revenue | HIGH — captures OASIS's growth trajectory |
| **Comparable multiples** | Apply revenue or EBITDA multiples from similar transactions | Companies with public comparables | MEDIUM — AI/SaaS comparables exist |
| **Asset-based** | Net asset value (assets minus liabilities) | Asset-heavy businesses, holding companies | LOW — OASIS is IP/service-based |
| **Capitalized earnings** | Normalize earnings, apply capitalization rate | Stable, mature businesses | LOW — OASIS is early-stage, growing |
| **Rules of thumb** | Industry-specific multiples (e.g., 1x revenue for service business) | Quick estimates, small businesses | MEDIUM — useful for planning, not for CRA |

**Cost of formal valuation:**
- Informal estimate (CPA): $2,000-$5,000
- Formal valuation report (CBV): $5,000-$25,000
- Litigation-quality valuation: $25,000-$75,000+

### 5.7 Non-Compete and Transition Planning

Any succession involves transition risk. Structures to manage it:

- **Non-compete agreement:** CC agrees not to compete for 2-5 years. Payments for non-compete are taxable as ordinary income (not capital gains). Structure as part of the share purchase price instead.
- **Consulting/transition agreement:** CC provides 6-24 months of consulting. Income is employment or self-employment income. Keep this separate from the share sale.
- **Earn-out:** Portion of purchase price contingent on future performance. Tax treatment: capital gains reserve (s.40(1)(a)(iii)), spread over up to 5 years. Risk: CC may not receive the full earn-out if targets are missed.
- **IP assignment:** Ensure all code, trade secrets, customer relationships are formally assigned. See `ATLAS_AI_SAAS_TAX_GUIDE.md` for IP transfer tax issues.

---

## 6. Life Insurance as Estate Planning Tool

> Cross-reference: `ATLAS_INSURANCE_ESTATE_PROTECTION.md` Section 1 covers term vs. whole vs. UL comparison, COLI mechanics, and the insured retirement strategy in detail. This section focuses on estate-specific applications.

### 6.1 Corporate-Owned Life Insurance (COLI) — Estate Tax Solution

**The core problem:** When CC dies owning CCPC shares, the deemed disposition creates a large tax bill. The estate needs cash to pay it — but the company's value is illiquid (it is in the business, not in a bank account).

**COLI solves this:**

1. Corporation buys a permanent life insurance policy on CC's life
2. Premiums are NOT deductible — paid with after-tax corporate dollars (~12.2% SBD rate)
3. On CC's death, the corporation receives the death benefit TAX-FREE (s.148(1))
4. Death benefit (less policy ACB) is credited to the Capital Dividend Account (s.89(1))
5. Corporation pays a capital dividend to the estate from the CDA — TAX-FREE (s.83(2))
6. Estate uses the tax-free cash to pay the tax bill from the deemed disposition

```
Example — COLI to fund estate tax:

  CC dies. OASIS Corp shares FMV = $3,000,000. ACB = $100.
  Deemed disposition: $2,999,900 capital gain
  Tax on final return: ~$800,000

  COLI policy on CC's life:
    Death benefit: $1,000,000
    Policy ACB: $200,000
    CDA credit: $800,000
    Capital dividend to estate: $800,000 (TAX-FREE)

  Estate uses the $800K to pay the $800K tax bill.
  Beneficiaries receive the OASIS shares intact — no forced sale.

  Without COLI:
    Estate must sell OASIS shares (or assets) to raise $800K
    Forced sale under time pressure = discount price
    Business may be destroyed by the liquidation
```

### 6.2 Insurance to Equalize Among Heirs

When one child inherits the business and others do not, life insurance can equalize the estate.

```
CC has 3 children (hypothetical future):
  Child A: Takes over OASIS Corp (value $3M)
  Child B: Gets life insurance proceeds ($1M)
  Child C: Gets life insurance proceeds ($1M)
  Remaining estate: split equally

  Without insurance:
    Child A gets $3M business, others get whatever is left
    Creates resentment, potential estate litigation
```

### 6.3 Universal Life (UL) vs. Whole Life vs. Term

| Feature | Term | Whole Life | Universal Life |
|---------|------|-----------|----------------|
| **Estate planning role** | Fund tax liability (cheapest per dollar of coverage) | Guaranteed estate value, forced savings | Maximum tax-sheltered investment + estate funding |
| **When to use** | Young, low income, need maximum coverage per dollar | Conservative, want guarantees, participating dividends | Sophisticated, want investment control, max tax shelter |
| **Corporate use** | Key person insurance, temporary needs | COLI — insured retirement strategy, CDA funding | COLI — aggressive tax-sheltered accumulation |
| **CC now** | YES — $500K term 20 at ~$25/month | Not yet — too expensive at current income | Not yet — requires incorporation + stable cash flow |

### 6.4 Key Person Insurance

If CC is the sole operator of OASIS and dies or becomes disabled, the business dies with CC. Key person insurance provides the corporation with cash to:
- Hire a replacement
- Cover lost revenue during transition
- Pay off business debts
- Fund a buyout of CC's shares by remaining stakeholders

**Tax treatment:** Premiums paid by the corporation are NOT deductible (unless the policy is assigned as collateral for a business loan, in which case a portion may be deductible under s.20(1)(e.2)). Death benefit is received tax-free by the corporation.

**CC action item:** At incorporation, purchase $500K-$1M of corporate-owned term insurance on CC's life. Cost: ~$30-$50/month at age 25.

---

## 7. Power of Attorney and Incapacity Planning

### 7.1 Why This Matters at Age 22

Most 22-year-olds do not have a will or power of attorney. But CC is not most 22-year-olds:
- CC runs a business generating revenue
- CC holds crypto assets that cannot be accessed without private keys
- CC trades on multiple exchanges with 2FA enabled
- CC is building a SaaS business with client relationships

If CC is in an accident and cannot communicate for 6 months, who manages the business? Who pays the bills? Who accesses the trading accounts? Without POA documents, the answer is: nobody, until a court appoints someone (which takes months and costs thousands).

### 7.2 POA for Property

**Ontario Substitute Decisions Act, 1992:** A Power of Attorney for Property authorizes a named person (the "attorney") to manage CC's financial affairs if CC becomes mentally incapable.

**Two types:**
- **Continuing POA for property:** Remains effective even if CC becomes mentally incapable. THIS is the one CC needs.
- **General POA for property:** Revoked automatically if CC becomes incapable. Useless for incapacity planning.

**What the attorney can do:**
- Access bank accounts, pay bills, manage investments
- File tax returns, deal with CRA
- Manage the business (within the scope granted)
- Sell assets if necessary to fund CC's care

**Who to appoint:** Someone CC trusts absolutely with money. Options:
- Mom (most common for a 22-year-old)
- A trusted friend with financial literacy
- A professional (lawyer, accountant) — expensive but objective
- Name an alternate in case the primary is unavailable

**Cost:** $200-$500 at a lawyer (often bundled with will).

### 7.3 POA for Personal Care

Authorizes a named person to make medical and personal care decisions if CC cannot.

**Decisions covered:**
- Medical treatment consent
- Residence decisions (where CC lives during recovery)
- Nutrition, hygiene, safety decisions
- End-of-life care (if CC includes specific instructions)

**Who to appoint:** Someone who understands CC's values and medical preferences. Often a different person than the property attorney (financial skill vs. personal knowledge).

### 7.4 Corporate Incapacity Planning

A sole proprietorship dies with the proprietor's incapacity. A corporation continues — but someone must have authority to act.

**At incorporation, CC should establish:**
- **Corporate resolution:** Authorize a named person (mom, lawyer, or trusted advisor) to act as emergency director if CC is incapacitated for more than 30 days
- **Banking resolutions:** Add a secondary authorized signer on corporate bank accounts
- **Signing authority documentation:** Ensure someone besides CC can sign contracts, accept payments, and manage client relationships
- **Emergency operations manual:** Documented procedures for:
  - How to log into corporate bank account
  - How to access Stripe/payment processors
  - How to communicate with active clients
  - How to pause automated trading systems
  - How to access cloud infrastructure (AWS, Vercel, etc.)

### 7.5 Digital Estate — Crypto and Technology Access

This is the most commonly overlooked area. If CC is incapacitated or dies, crypto and digital assets are PERMANENTLY LOST unless someone has access credentials.

**Critical items to document and store securely:**

| Asset | Access Information Needed | Storage Method |
|-------|--------------------------|----------------|
| Kraken exchange | Email, password, 2FA backup codes | Sealed envelope with lawyer |
| Wealthsimple | Email, password, 2FA backup codes | Sealed envelope with lawyer |
| OANDA | Account ID, password, 2FA | Sealed envelope with lawyer |
| Hardware wallet (future) | Seed phrase (12 or 24 words) | Metal backup plate in safety deposit box |
| Software wallet (MetaMask etc.) | Seed phrase, password | Separate sealed envelope |
| Password manager | Master password | Sealed envelope with lawyer + trusted person |
| GitHub repositories | SSH keys, account credentials | Documented in password manager |
| Domain names (registrar) | Account credentials | Documented in password manager |
| Email accounts | Recovery codes | Documented in password manager |
| SaaS clients (Stripe, hosting) | Admin credentials | Documented operations manual |

**Storage hierarchy:**
1. Password manager contains everything (1Password, Bitwarden)
2. Master password to password manager in a sealed envelope with estate lawyer
3. Crypto seed phrases in a SEPARATE location (safety deposit box with metal plate backup)
4. Trusted person (mom, sister) knows the lawyer's name and that envelopes exist
5. Will specifically references the digital asset plan

**NEVER store seed phrases digitally** (not in email, not in cloud storage, not in a text file). Physical-only for seed phrases.

---

## 8. Digital Asset Estate Planning

### 8.1 Crypto Succession — The Unique Challenge

Traditional assets (bank accounts, real estate, stocks) have institutional custodians who can transfer ownership through legal processes. Crypto held in self-custody has no such mechanism. If the private keys are lost, the crypto is lost. Forever.

**The estate planning problem:**
- Executor presents a death certificate to a bank: bank transfers the account. Done.
- Executor presents a death certificate to a blockchain: nothing happens. The blockchain does not recognize death certificates, court orders, or probate certificates.

### 8.2 Exchange-Held Crypto

Crypto held on centralized exchanges (Kraken, Coinbase, Wealthsimple Crypto) is simpler:

| Exchange | Death/Incapacity Process | Beneficiary Designation? |
|----------|------------------------|------------------------|
| Kraken | Submit death certificate + proof of executorship to support | No direct beneficiary designation |
| Wealthsimple | Contact support with death certificate + estate trustee certificate | No — but TFSA can have beneficiary |
| Coinbase | Probate/estate process through support | No |
| Binance | Varies by jurisdiction — support request | No |

**Planning:** Ensure the executor knows which exchanges CC uses, can access the registered email, and has the account information. Exchange-held crypto goes through the standard estate process (probate if in the estate, or trust if held in trust).

### 8.3 Self-Custody Crypto

For hardware wallets (Ledger, Trezor) or software wallets (MetaMask):

**Seed phrase is everything.** The 12 or 24-word recovery phrase can regenerate the entire wallet on any compatible device. Anyone with the seed phrase controls the crypto.

**Multi-layer protection:**

```
Layer 1: Hardware wallet (Ledger/Trezor) — CC's daily access device
Layer 2: Seed phrase backup — stamped on metal plate (fireproof, waterproof)
Layer 3: Metal plate stored in bank safety deposit box (not at home)
Layer 4: Instructions in sealed envelope at lawyer's office:
          "Safety deposit box at [bank], box #[number], contains
           crypto recovery phrase. Recover to [specific wallet].
           Current approximate value: $[amount].
           Access code for box: [code]."
Layer 5: Trusted person (not the same as the lawyer) knows the
         lawyer has the envelope and the safety deposit box exists
```

**Why split the information:** No single person has enough information to steal the crypto. The lawyer knows instructions exist but not the seed phrase. The trusted person knows the lawyer but not the details. The seed phrase is in a physical vault.

### 8.4 Multi-Signature Wallets for Business Crypto

If OASIS holds significant crypto as a corporate asset, a multi-signature wallet adds security:

- **2-of-3 multisig:** Requires 2 of 3 private keys to authorize a transaction
- **Key holders:** CC (key 1), trusted advisor (key 2), lawyer in sealed envelope (key 3)
- **Benefit:** No single point of failure. If CC dies, keys 2 and 3 can move the funds.
- **Cost:** Free (built into most blockchain protocols). Setup complexity is moderate.

### 8.5 Smart Contract Implications

DeFi positions (staking, liquidity pools, lending protocols) create unique estate challenges:

- **Staking:** Staked tokens may have unbonding periods (7-28 days). The executor needs to initiate unstaking and wait.
- **Liquidity pools:** LP tokens must be redeemed from the protocol. Impermanent loss may have occurred.
- **Lending:** Collateralized loans must be repaid or the collateral will be liquidated. If crypto prices move against the position, the estate loses value.
- **Governance tokens / DAOs:** Voting rights may be locked. vesting schedules may continue.
- **NFTs:** Transferable with the wallet's private key. Value is speculative and may need to be appraised for the estate.

**CC action:** Maintain a current inventory of all DeFi positions, including protocol names, chain, token addresses, and approximate values. Update monthly. Store with the digital estate documents.

### 8.6 SaaS Business Digital Assets

OASIS is a digital business. Its value is in code, data, and relationships — not physical assets.

| Asset | How to Transfer | Planning Required |
|-------|----------------|-------------------|
| Source code (GitHub) | Add co-owner or organization account | NOW — set up GitHub organization |
| Domain names | Registrar account access (Namecheap, Cloudflare) | Document in password manager |
| Cloud hosting (Vercel, AWS) | Account credentials + billing | Document; add backup admin |
| Stripe account | Cannot easily transfer — may need new account | Document; ensure backup admin |
| Customer database | Export from CRM/database | Document export procedure |
| API keys (Claude, etc.) | Regenerable with account access | Document account credentials |
| Client contracts | Stored in accessible location | Digital + physical copies |
| Intellectual property | Assignment in corporate articles | At incorporation |

---

## 9. Charitable Giving Strategies

### 9.1 Donation Tax Credit Mechanics

Canada does not give a tax deduction for donations — it gives a tax credit (directly reduces tax payable).

**Federal donation tax credit (s.118.1):**
- First $200 of donations: 15% credit
- Amounts over $200: 29% credit (or 33% if income exceeds $235,675 — the top bracket)

**Ontario donation tax credit:**
- First $200: 5.05%
- Over $200: 11.16%

**Combined credit rate (Ontario):**
- First $200: 20.05%
- Over $200: 40.16% (or 44.16% at top income)

```
CC donates $10,000 to charity:

  Credit on first $200: $200 × 20.05% = $40
  Credit on remaining $9,800: $9,800 × 40.16% = $3,936
  Total tax reduction: $3,976

  Effective cost of $10,000 donation: $6,024
  The government funded ~40% of the donation.
```

**Annual limit:** Donations cannot exceed 75% of net income in any year (s.118.1(1)). Unused credits carry forward 5 years.

### 9.2 Donate Publicly Traded Securities — Zero Capital Gains

**ITA s.38(a.1):** When publicly traded securities are donated directly to a registered charity (or through a donor-advised fund), the capital gains inclusion rate is ZERO.

This is one of the most powerful tax provisions in the ITA:

```
CC holds shares: ACB = $5,000, FMV = $25,000, capital gain = $20,000

Option A: Sell shares, donate cash:
  Capital gain: $20,000
  Taxable (50%): $10,000
  Tax on gain (~40%): $4,000
  Donate $25,000 cash: tax credit = ~$10,000
  Net tax reduction: $10,000 - $4,000 = $6,000

Option B: Donate shares directly:
  Capital gain: $20,000
  Taxable (0% inclusion): $0
  Tax on gain: $0
  Donation receipt: $25,000 FMV
  Tax credit: ~$10,000
  Net tax reduction: $10,000

  Option B saves $4,000 more than Option A on the same donation.
```

**Eligible securities:** Shares, bonds, units of mutual funds, ETFs listed on a designated stock exchange (TSX, NYSE, NASDAQ, etc.). NOT eligible: private company shares (use the CCPC strategy below), crypto (not publicly traded — CRA does not recognize crypto as publicly listed securities).

### 9.3 Donate Through a CCPC — CDA Strategy

Private company shares cannot be donated for the zero-inclusion capital gains treatment. But the corporate structure offers a different path:

```
Strategy: Donate through CDA

Step 1: OASIS Corp sells publicly traded securities with large gains
Step 2: 50% of the capital gain is added to the CDA
Step 3: Corporation donates the securities directly to charity
        (gets the zero-inclusion treatment at the corporate level)
Step 4: Corporation receives donation receipt
Step 5: Donation tax credit reduces corporate tax

OR:

Step 1: Corporation realizes capital gains (50% non-taxable portion → CDA)
Step 2: Corporation pays capital dividend from CDA to CC (tax-free, s.83(2))
Step 3: CC donates the cash personally
Step 4: CC claims the personal donation tax credit (higher rates than corporate)
```

**Which is better (personal vs. corporate donation)?** Personal donation usually yields a higher combined benefit because the personal tax credit rates (40-44%) exceed the corporate tax rate reduction. But the CDA extraction step must be planned carefully.

### 9.4 Gifts in Will — GRE Charitable Donations

Donations made by will (bequests to charities) can be claimed on the deceased's final return OR on the GRE's returns for up to 5 years. This flexibility (introduced in 2016) allows the executor to optimize which year claims the credit.

**s.118.1(5.1):** Gifts made by the GRE can be allocated to the GRE's return OR the deceased's final return for the year of death or the preceding year.

**Strategy:** If the final return has high income (from deemed dispositions), claim the donation credit on the final return to offset the tax. If the final return income is low, carry the credit to the GRE's return where it may be more valuable.

### 9.5 Private Foundation vs. Donor-Advised Fund (DAF)

| Feature | Private Foundation | Donor-Advised Fund |
|---------|-------------------|-------------------|
| Setup cost | $5,000-$25,000 (legal, CRA registration) | $0-$5,000 (open account with existing DAF) |
| Annual cost | $5,000-$20,000 (audit, filing, admin) | 0.6-1.0% of assets (management fee) |
| Control | Full — CC appoints the board | Advisory — CC recommends grants, DAF administrator approves |
| Minimum size | $500K+ to justify costs | $5,000-$25,000 minimum (varies by provider) |
| Disbursement quota | Must grant 3.5% of assets annually to qualified donees | DAF administrator handles compliance |
| Tax receipt | On donation to foundation | On donation to DAF |
| Public disclosure | Annual T3010 filing (public) | Private — donations not publicly disclosed |
| CC relevance | FUTURE — when net worth > $2M | FUTURE — when charitable giving > $10K/year |

**Canadian DAF providers:** Community foundations (e.g., Toronto Foundation, Ontario Trillium Foundation), Charitable Impact (Chimp), CanadaHelps, National Bank Philanthropic Fund.

### 9.6 Cultural Property Donation

Donations of certified cultural property (art, manuscripts, archival material) to designated institutions have a **0% capital gains inclusion rate** AND the 75% income limit does not apply — the donation can offset up to 100% of income.

CC relevance: LOW now. But if CC acquires significant art or digital collectibles that qualify as cultural property, this is the most tax-efficient donation possible.

---

## 10. Cross-Border Estate Issues

> Cross-reference: `ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md` for CC's multi-jurisdiction planning, `ATLAS_FOREIGN_REPORTING.md` for T1135/T1134 reporting, `ATLAS_TREATY_FIRE_STRATEGY.md` for treaty exploitation and departure tax.

### 10.1 US Estate Tax

The United States imposes an estate tax on worldwide assets of US citizens/residents AND on US-situs assets of non-residents.

**CC is a Canadian resident, non-US citizen. US estate tax applies to CC's US-situs assets:**

| US-Situs Asset | Example | Taxable? |
|----------------|---------|----------|
| US real estate | Rental property, vacation home | YES |
| US corporate shares | Apple, Google, Microsoft, US ETFs | YES |
| US partnership interests | LP units in US PE fund | YES |
| US bank deposits | Wise USD account (if US branch) | Generally NO (bank deposit exemption) |
| US government bonds | Treasury bills, notes | NO (s.2105(b) IRC) |
| Crypto on US exchange | Kraken (US entity) | UNCLEAR — situs of crypto is debated |

**US estate tax rates:** 18-40% (graduated), with exemptions.

**Non-resident exemption:** Only $60,000 USD (compared to $13.61M for US citizens in 2024). This means a non-resident with $100,000 in US stocks could face US estate tax.

**Canada-US Tax Treaty (Article XXIX-B):**
- Provides a pro-rated unified credit to Canadian residents
- Effective exemption: ~$13.61M × (US-situs assets / worldwide assets)
- If CC's worldwide estate is $2M and US-situs assets are $500K (25%), the effective exemption is ~$3.4M — well above $500K, so no US estate tax

**Planning for CC:**
- Monitor total US-situs asset exposure
- If US investments are significant, consider holding them through a Canadian corporation (corporate shares are Canadian-situs, not US-situs — but watch for PFIC issues)
- The Wise USD account is generally exempt under the bank deposit exception if held at a US-regulated bank branch
- Keep Kraken holdings modest until crypto situs rules are clarified

### 10.2 UK Inheritance Tax (IHT)

CC holds a British passport. UK IHT rules are complex:

**UK domicile vs. residence:**
- IHT is based on DOMICILE, not citizenship or residence
- CC was born in Canada, raised in Canada — CC's domicile of origin is Canada
- CC is NOT UK-domiciled unless CC moves to the UK and establishes domicile of choice (approximately 15 of 20 years resident)
- Crown Dependencies (IOM, Guernsey, Jersey) are NOT part of the UK for IHT purposes

**IHT for non-UK domiciliaries:**
| Asset | Subject to IHT? |
|-------|-----------------|
| UK real estate | YES — 40% above nil-rate band (£325,000) |
| UK bank accounts | YES |
| UK shares | YES |
| Non-UK assets | NO — only UK-situs assets are taxable |

**Planning for CC:**
- CC is NOT UK-domiciled — only UK-situs assets are exposed
- Avoid holding UK real estate personally if possible (use a non-UK structure)
- Crown Dependencies do not have inheritance tax (IOM: 0%, Guernsey: 0%, Jersey: 0%)
- If CC eventually moves to IOM/Guernsey, there is NO local inheritance tax
- If CC later establishes UK domicile (living in England/Scotland for 15+ years), worldwide assets become subject to IHT

### 10.3 Ireland — Capital Acquisitions Tax (CAT)

If CC obtains Irish citizenship and holds Irish assets, or if CC's father (Irish resident) leaves CC an inheritance:

**Irish CAT:**
- Rate: **33%** on gifts/inheritances above the threshold
- Group A threshold (parent to child): **EUR 335,000** (2024)
- Group B threshold (sibling, grandparent): **EUR 32,500**
- Group C threshold (anyone else): **EUR 16,250**

**Double taxation relief:** Canada-Ireland tax treaty does not specifically cover inheritance/gift tax. However, Ireland provides unilateral credit for foreign tax paid on the same assets.

```
Example: CC's father (Irish resident) dies, leaves CC EUR 500,000

  Group A threshold: EUR 335,000
  Taxable: EUR 165,000
  CAT at 33%: EUR 54,450

  Canada: No estate tax (CC receives the inheritance tax-free in Canada)
  But: Irish CAT must be paid before assets are released

  Planning: Father should use his EUR 335,000 threshold efficiently
            Consider lifetime gifts (EUR 3,000/year small gift exemption per person)
```

### 10.4 Situs Rules — Where Is the Property Located?

| Asset Type | Situs (Location for Estate Tax) |
|-----------|-------------------------------|
| Real estate | Where the property is physically located |
| Shares in a corporation | Where the corporation is incorporated (not traded) |
| Bank accounts | Where the branch holding the deposit is located |
| Bonds/debt | Where the issuer is resident |
| Tangible personal property | Where it is physically located |
| Intangible personal property | Generally where the owner is domiciled |
| Crypto | UNCLEAR — some argue situs of the exchange, others argue situs of the owner |
| Partnership interests | Generally where the partnership carries on business |

**Planning principle:** Hold foreign-situs assets through Canadian corporations where possible. The Canadian corporation's shares are Canadian-situs — the foreign assets inside the corporation are "hidden" from foreign estate taxes. But this creates complexity (PFIC in the US, CFC rules, FAPI) and must be analyzed carefully.

---

## 11. Tax-Efficient Wealth Transfer Strategies

### 11.1 Prescribed Rate Loans — s.74.5(2)

The most underutilized income-splitting tool in the ITA. It works even with TOSI because it is a genuine loan, not a gift.

**How it works:**
1. CC lends money to a spouse (or family trust) at the CRA prescribed rate
2. The borrower invests the funds
3. Investment returns above the prescribed rate belong to the borrower — taxed at their rate
4. The prescribed interest must actually be paid by January 30 of the following year
5. Attribution rules (s.74.1) do NOT apply as long as the prescribed rate is charged

**Current prescribed rate (2026):** 5% (historically has been as low as 1%)

```
CC lends $200,000 to spousal trust at 5% prescribed rate:

  Trust invests in diversified portfolio earning 10% annually
  Investment return: $20,000
  Prescribed interest paid to CC: $10,000 (taxed to CC)
  Net return retained by trust: $10,000 (taxed to trust beneficiaries)

  If trust distributes to spouse in 20% bracket:
    Tax on $10,000: $2,000

  If CC had earned the $10,000 directly (53.53% bracket):
    Tax: $5,353

  Annual savings: $3,353
  Over 20 years (compounding): $100,000+
```

**The rate lock advantage:** The prescribed rate is set at the time the loan is made and remains fixed for the life of the loan. If CC establishes a prescribed rate loan when the rate is 1-2% (as it was in 2020-2021), the spread is enormous. At 5%, the strategy still works but the spread is tighter — wait for a low-rate environment if possible.

**Requirements:**
- Formal loan agreement (written, signed, witnessed)
- Interest actually paid by January 30 of each following year
- If interest is missed even ONCE, the attribution rules apply retroactively to ALL years
- The loan must bear interest at least equal to the prescribed rate in effect at the time the loan was made

### 11.2 Salary to Family Members

Paying salary to family members is the simplest form of income splitting — and it works even under TOSI (salary is excluded from the TOSI regime).

**Requirements (s.67):**
- The family member must ACTUALLY work for the business
- The salary must be REASONABLE for the work performed
- Hours and duties must be documented
- T4 slip issued and payroll deductions remitted

```
CC pays mom $30,000/year to do bookkeeping and admin for OASIS:

  Mom's tax on $30,000 (Ontario, basic personal amount ~$11,865):
    Taxable: $18,135
    Tax: ~$3,264

  If CC earned the same $30,000 at 43% marginal:
    Tax: ~$12,900

  Savings: ~$9,636/year

  BUT: Mom must actually do the work. CRA audits this aggressively.
  Documented hours, specific duties, comparable salary research required.
```

### 11.3 Dividend Sprinkling — Post-TOSI Strategies

Paying dividends to family members through a CCPC is restricted by TOSI but not impossible:

**Strategies that still work:**
1. **Excluded business income:** Family members who work 20+ hours/week in the business can receive dividends free of TOSI
2. **Excluded shares (age 25+):** Family members who own 10%+ of the voting shares can receive dividends if the corporation is not a services business and the shares are not derived from a related business
3. **Arm's length capital:** Family members who contributed their own capital (not received from CC) can earn returns on that capital TOSI-free
4. **Non-resident family members:** TOSI does not apply to non-residents (but Part XIII withholding at 25% or treaty rate applies) — CC's dad in Ireland may receive dividends subject to 15% withholding (Canada-Ireland treaty) rather than 53.53% TOSI

### 11.4 LCGE Crystallization — Trigger Gain Now

Even without an estate freeze, CC can crystallize the LCGE by triggering a capital gain on QSBC shares while the exemption is available.

**Why crystallize early:**
- LCGE may be reduced or eliminated in future budgets (it has been expanded recently but could be clawed back)
- Stepping up the ACB now reduces future deemed disposition at death
- If the shares qualify as QSBC today but may not in the future (e.g., passive investment buildup), crystallize while eligibility exists

**How to crystallize (s.85 election):**
- Transfer OASIS shares to Holdco
- Elect agreed amount = ACB + LCGE
- Capital gain triggered, offset by LCGE = $0 tax
- New ACB = elected amount (stepped up)

**Cost:** $5,000-$10,000 (legal + accounting for the s.85 election and T2057 filing).

### 11.5 Family Trust with Corporate Beneficiary

The most sophisticated structure: OpCo distributes to HoldCo, HoldCo distributes to a family trust, and the trust sprinkles to individual beneficiaries.

```
Structure:
  OASIS OpCo
      ↓ (intercorporate dividends, s.112 — tax-free)
  HoldCo (owned by family trust)
      ↓ (dividends from HoldCo)
  Family Trust
      ↓ (distributions to beneficiaries)
  CC | Mom | Sister 1 | Sister 2

Benefits:
  - Intercorporate dividends are tax-free (s.112 deduction)
  - Trust can sprinkle income to the lowest-taxed beneficiary
  - Each beneficiary has their own LCGE on sale of QSBC shares
  - HoldCo protects OpCo's assets from operational risk
  - AAII in HoldCo does not grind OpCo's SBD

Costs:
  - Setup: $15,000-$30,000 (legal + accounting)
  - Annual maintenance: $5,000-$10,000 (2 corporate returns + T3)
  - TOSI compliance documentation: ongoing
```

**When to implement:** When OASIS generates $200K+ in annual revenue and CC has family members who can legitimately participate in the business structure.

### 11.6 Capital Gains Reserve — Spreading the Tax

On any sale where the full proceeds are not received in the year of sale, CC can claim a capital gains reserve (s.40(1)(a)(iii)):

- Spread the capital gain over up to **5 years** (minimum 20% recognized per year)
- For qualifying farm property or fishing property or transfer to a child: up to **10 years**
- The reserve is mandatory for the amount not yet received — but the 5-year limit ensures the gain is eventually recognized

```
CC sells OASIS for $5,000,000, receives $1,000,000 per year for 5 years:

  Capital gain: $4,999,900
  Year 1: recognize $999,980 (20%)
  Year 2: recognize $999,980
  Year 3: recognize $999,980
  Year 4: recognize $999,980
  Year 5: recognize $999,980

  This spreads the tax impact, potentially keeping CC in lower brackets
  (especially if CC has minimal other income in later years).
```

---

## 12. CC's Estate Planning Action Items

### [NOW] — Age 22, Sole Proprietor, ~$49K Income

| Priority | Action | Cost | Impact |
|----------|--------|------|--------|
| 1 | **Basic will** — even a simple one. Appoints executor, distributes assets, references digital estate plan. | $500-$1,500 | Avoids intestacy (Ontario Succession Law Reform Act defaults — assets split by formula, not CC's wishes) |
| 2 | **Continuing POA for Property** — appoint mom (or trusted person) to manage finances if incapacitated | $200-$500 (bundle with will) | Prevents months of court process to appoint a guardian |
| 3 | **POA for Personal Care** — appoint someone for medical decisions | $200-$500 (bundle with will) | Ensures CC's medical wishes are followed |
| 4 | **Document crypto access** — seed phrases on metal plate in secure location, exchange credentials in sealed envelope with lawyer, instructions letter | $50-$200 (metal plate + safety deposit box) | Prevents permanent loss of crypto assets |
| 5 | **Beneficiary designations** — name beneficiaries on TFSA, FHSA, and any future RRSP at Wealthsimple | $0 | Bypasses probate, ensures tax-efficient transfer |
| 6 | **Life insurance quote** — term 20, $500K, healthy 22-year-old male | ~$25-$30/month | Locks in insurability while healthy; covers business debts and family protection |
| 7 | **Digital estate inventory** — maintain a current list of all accounts, exchanges, wallets, DeFi positions, SaaS credentials | $0 (just time) | Executor can actually find and access CC's assets |
| 8 | **GitHub organization** — move OASIS code to a GitHub org with a secondary admin | $0 | Prevents code loss if CC's personal account is inaccessible |

**Estimated total cost for [NOW] items: $1,000-$2,500 one-time + ~$30/month insurance**

### [INCORPORATION] — Revenue > $80K, CCPC Established

| Priority | Action | Cost | Impact |
|----------|--------|------|--------|
| 1 | **Dual wills (primary + secondary)** — secondary will covers OASIS Corp shares, avoids probate on the most valuable asset | $2,000-$5,000 | Saves 1.5% probate on corporate share value ($15K-$30K+ on a $1M-$2M company) |
| 2 | **Corporate resolution for incapacity** — who acts as emergency director if CC cannot | $500-$1,000 | Business continuity; prevents operational paralysis |
| 3 | **Key person insurance** — corporate-owned term policy on CC's life | ~$30-$50/month | Corporation has cash to survive if CC dies |
| 4 | **Estate freeze planning** — engage tax lawyer for s.86 freeze at low corporate valuation | $8,000-$20,000 | Locks current value, shifts all future growth to trust/beneficiaries. Do this EARLY when company value is low. |
| 5 | **LCGE crystallization** — s.85 election to step up ACB using $1.25M exemption | $5,000-$10,000 | $1.25M of gain becomes tax-free; reduces future death tax by ~$330,000 |
| 6 | **Corporate articles — share provisions** — ensure articles address what happens to shares on death, voting control, redemption rights | Included in freeze cost | Legal clarity prevents disputes |

### [REVENUE $200K+] — Growth Phase

| Priority | Action | Cost | Impact |
|----------|--------|------|--------|
| 1 | **Family trust establishment** — discretionary trust with CC, mom, dad, sisters as beneficiaries | $5,000-$15,000 | LCGE multiplication ($6.25M combined with 5 family members) |
| 2 | **OpCo/HoldCo structure** — separate operating and holding companies | $3,000-$8,000 additional | Asset protection, AAII management, estate flexibility |
| 3 | **COLI evaluation** — corporate-owned permanent insurance for insured retirement strategy | $500-$2,000/month corporate premium | Tax-free wealth accumulation, CDA funding, estate equalization |
| 4 | **Formal business valuation** — CBV-prepared report for CRA defense of freeze values | $5,000-$15,000 | Defensible valuation protects freeze from CRA challenge |

### [FUTURE] — High Net Worth, Family, Exit Planning

| Priority | Action | Cost | Impact |
|----------|--------|------|--------|
| 1 | **Comprehensive estate plan review** — update all documents every 3-5 years or after major life events (marriage, children, move, sale of business) | $2,000-$5,000 per review | Keeps plan current; new life events create new tax exposures |
| 2 | **EOT evaluation** — if selling OASIS to employees, structure as Employee Ownership Trust for $10M capital gains exemption | Professional fees for structuring | Combined with LCGE: up to $11.25M tax-free on sale |
| 3 | **Charitable giving strategy** — donor-advised fund or foundation at $2M+ net worth | $0-$25,000 setup | 40%+ tax credit on donations; donate securities for 0% capital gains |
| 4 | **Cross-border estate tax audit** — if CC holds significant US, UK, or Irish assets, engage cross-border tax specialist | $3,000-$10,000 | Prevents unexpected foreign estate tax exposure |
| 5 | **Trust 21-year planning** — if family trust is established at age 25, the 21-year deemed disposition occurs at age 46. Plan the exit 5 years in advance (age 41). | Part of ongoing planning | Avoids surprise tax bill at Year 21 |
| 6 | **Alter ego trust** — at age 65+, transfer remaining assets to alter ego trust for probate avoidance | $5,000-$15,000 | Complete probate bypass for all assets |
| 7 | **Intergenerational transfer (Bill C-208)** — if CC has children who will take over the business | Professional fees | LCGE treatment on parent-to-child sale instead of dividend treatment |

---

## Appendix A: Key ITA References

| Section | Topic |
|---------|-------|
| s.70(5) | Deemed disposition at death (capital property at FMV) |
| s.70(5.1) | Deemed proceeds of NISA Fund No. 2 at death |
| s.70(6) | Spousal rollover at death (transfer at ACB) |
| s.70(6.2) | Election to opt out of spousal rollover |
| s.73(1) | Alter ego trust rollover |
| s.73(1.01) | Joint partner trust rollover |
| s.74.1 | Attribution rules (transfers to spouse) |
| s.74.5(2) | Prescribed rate loan exception to attribution |
| s.83(2) | Capital dividend election (tax-free extraction from CDA) |
| s.84.1 | Surplus stripping on non-arm's length share sale |
| s.85(1) | Rollover on transfer to corporation (elected amount) |
| s.86(1) | Share exchange on reorganization of capital (estate freeze) |
| s.89(1) | CDA — Capital Dividend Account definition |
| s.104(4) | 21-year deemed disposition rule for trusts |
| s.107(2) | Tax-free rollout of trust property to beneficiaries |
| s.110.6(2.1) | Lifetime Capital Gains Exemption (QSBC shares) |
| s.118.1 | Donation tax credit |
| s.120.4 | Tax on Split Income (TOSI) |
| s.128.1 | Departure tax (deemed disposition on emigration) |
| s.146(8.8) | RRSP deemed receipt at death |
| s.148(1) | Life insurance — proceeds not taxable |
| s.164(6) | GRE loss carry-back to final return |
| s.248(1) | Graduated Rate Estate definition |

## Appendix B: Cross-Reference Map

| Topic | Primary Document | Section |
|-------|-----------------|---------|
| COLI mechanics, insured retirement strategy | `ATLAS_INSURANCE_ESTATE_PROTECTION.md` | Section 1.2 |
| Estate freeze s.86/s.85 basics | `ATLAS_INCORPORATION_TAX_STRATEGIES.md` | Section 6 |
| QSBC purification for LCGE | `ATLAS_INCORPORATION_TAX_STRATEGIES.md` | Section 7 |
| TOSI rules and exclusions | `ATLAS_TOSI_DEFENSE.md` | Full document |
| Billionaire wealth transfer tactics | `ATLAS_WEALTH_PLAYBOOK.md` | Section 11 |
| Crown Dependencies (0% CGT, 0% IHT) | `ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md` | Full document |
| Departure tax on emigration | `ATLAS_TREATY_FIRE_STRATEGY.md` | Departure tax section |
| T1135 foreign property reporting | `ATLAS_FOREIGN_REPORTING.md` | Section 1 |
| SR&ED credits (IP in trust structure) | `ATLAS_AI_SAAS_TAX_GUIDE.md` | SR&ED section |
| Income splitting strategies | `ATLAS_TOSI_DEFENSE.md` | Section 4 |
| Prescribed rate loan details | `ATLAS_TOSI_DEFENSE.md` | Section 4 |
| CRA audit defense for estate structures | `ATLAS_CRA_AUDIT_DEFENSE.md` | Full document |
| Bookkeeping for estate-related transactions | `ATLAS_BOOKKEEPING_SYSTEMS.md` | Chart of accounts |

## Appendix C: Estate Planning Checklist — Annual Review

Use this checklist annually (or after any major life event: marriage, child, business sale, relocation):

```
[ ] Will is current and reflects wishes
[ ] POA for Property is current (attorney is still appropriate)
[ ] POA for Personal Care is current
[ ] Beneficiary designations reviewed (RRSP, TFSA, FHSA, insurance)
[ ] Digital estate inventory updated (new accounts, wallets, positions)
[ ] Crypto access documentation current (seed phrases, exchange credentials)
[ ] Life insurance coverage adequate for current estate tax exposure
[ ] Corporate minute book current (share register, director resolutions)
[ ] Trust T3 filed (if applicable)
[ ] 21-year rule countdown tracked (if applicable)
[ ] Cross-border asset exposure reviewed
[ ] Estate freeze value still appropriate (refreeze needed?)
[ ] Family members' LCGE status confirmed
[ ] Business valuation estimate updated
[ ] Executor/trustee still willing and capable
```

---

*This document is for educational and planning purposes. CC must engage a licensed Ontario estate lawyer, tax accountant (CPA), and Chartered Business Valuator (CBV) before implementing any estate freeze, trust, or succession plan. ATLAS researches, calculates, and prepares — CC reviews and executes with professional advisors.*

*Last updated: 2026-03-27 | Next review: 2026-06-27 (quarterly) or after any major life event*
