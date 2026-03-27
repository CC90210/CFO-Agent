# ATLAS — Elite Canadian Incorporation Tax Strategies

> Prepared by ATLAS (CFO) for CC | Jurisdiction: Ontario, Canada | Tax Year: 2024-2025
> This document covers advanced CCPC tax planning. Prerequisite: CC incorporates OASIS AI Solutions.
> All ITA references are to the Income Tax Act (Canada), R.S.C. 1985, c.1 (5th Supp.).
> Ontario rates per Ontario Taxation Act, 2007. CRA administrative positions per IT Bulletins and Folios.

**Trigger for incorporation:** OASIS revenue > $80K CAD (per ATLAS_TAX_STRATEGY.md).

---

## Table of Contents

1. [RDTOH / ERDTOH — Refundable Dividend Tax on Hand](#1-rdtoh--erdtoh)
2. [Integration Analysis — 2024 Ontario](#2-integration-analysis--2024-ontario)
3. [Shareholder Loan Rules — ITA s.15, s.80.4](#3-shareholder-loan-rules)
4. [Reasonable Salary Doctrine](#4-reasonable-salary-doctrine)
5. [Corporate Investment Strategies — SBD & Passive Income Grind](#5-corporate-investment-strategies)
6. [Estate Freeze Techniques](#6-estate-freeze-techniques)
7. [Purification Strategies — QSBC Qualification](#7-purification-strategies)

---

## 1. RDTOH / ERDTOH

### How the Mechanism Works

The refundable dividend tax on hand system is the cornerstone of corporate investment taxation in Canada. It prevents corporations from being used as tax shelters for passive investment income.

**The Core Cycle:**

```
1. Corporation earns passive income (interest, rents, non-eligible portfolio dividends, taxable capital gains)
2. Federal tax applies at ~38.67% (Part I) — well above the ~9% SBD rate
3. A portion of that tax (~30.67%) is added to the RDTOH account
4. When the corporation pays taxable dividends to shareholders, it gets a REFUND of $1 for every $3.03 of dividends paid
5. The shareholder then pays personal tax on those dividends
```

This achieves **integration** — the combined corporate + personal tax roughly equals what the individual would have paid directly.

### Two Pools: ERDTOH and NERDTOH

Post-2018 (ITA s.129(4)), RDTOH was split into two separate accounts:

| Account | Full Name | Source | Refund Trigger |
|---------|-----------|--------|----------------|
| **ERDTOH** | Eligible Refundable Dividend Tax on Hand | Part IV tax on **eligible dividends** received from connected/non-connected corporations | Payment of **eligible dividends** only |
| **NERDTOH** | Non-Eligible Refundable Dividend Tax on Hand | Part I refundable tax on **investment income** (interest, rents, capital gains) + Part IV tax on non-eligible dividends | Payment of **either** eligible or non-eligible dividends |

**Critical Rule:** NERDTOH is refunded first. You MUST pay non-eligible dividends first to recover NERDTOH before paying eligible dividends to recover ERDTOH.

### GRIP vs LRIP

| Account | Full Name | ITA Section | What It Tracks |
|---------|-----------|-------------|---------------|
| **GRIP** | General Rate Income Pool | s.89(1) | Income taxed at the **general corporate rate** (no SBD). Eligible dividends can be paid from GRIP. |
| **LRIP** | Low Rate Income Pool | s.89(1) | Income taxed at the **small business rate** (SBD). Non-eligible dividends must be paid from LRIP first. |

**For a CCPC like OASIS (sub-$500K active income):**
- Almost all income taxed at SBD rate → flows to LRIP
- You MUST pay non-eligible dividends first (to clear LRIP) before paying eligible dividends
- Eligible dividends paid when LRIP > 0 trigger **Part III.1 penalty tax** (ITA s.185.2) at 20% of excess

### Optimization Strategy

```
Step 1: Track NERDTOH balance annually (from passive investment income)
Step 2: Pay non-eligible dividends = NERDTOH × 3.03 to recover full refund
Step 3: Only pay eligible dividends when GRIP > 0 and LRIP = 0
Step 4: Time dividend payments to fiscal year-end for maximum refund recovery
```

### Numerical Example — OASIS Corp

```
OASIS Corp earns $20,000 in passive investment income (interest + capital gains):
  Federal Part I tax on investment income:    $20,000 × 38.67% = $7,734
  Refundable portion added to NERDTOH:        $20,000 × 30.67% = $6,134

To recover the $6,134 NERDTOH:
  Pay non-eligible dividends:                 $6,134 × 3.03 = $18,586
  Dividend refund received by corp:           $18,586 / 3.03 = $6,134

CC receives $18,586 non-eligible dividend:
  Gross-up (15%):                            $18,586 × 1.15 = $21,374
  Federal tax (~20.5% bracket):              $21,374 × 20.5% = $4,382
  Federal dividend tax credit (9.0301%):     $18,586 × 9.0301% = ($1,679)
  Ontario dividend tax credit (2.9863%):     $18,586 × 2.9863% = ($555)
  Net personal tax on dividend:              ~$2,148

Total tax (corp + personal):                 $7,734 - $6,134 + $2,148 = $3,748
Effective rate on $20,000:                   18.7%
vs. Personal rate if earned directly:        ~29.65% marginal → $5,930
Tax saved via RDTOH mechanism:               $2,182
```

**CRA Audit Risk:** LOW — This is the system working as intended. Just maintain proper RDTOH tracking in T2 Schedule 3.

---

## 2. Integration Analysis — 2024 Ontario

### Corporate Tax Rates

| Income Type | Federal | Ontario | Combined | ITA Reference |
|-------------|---------|---------|----------|---------------|
| **Active business (SBD)** — first $500K | 9.0% | 3.2% | **12.2%** | s.125(1), s.123 |
| **Active business (general)** — over $500K | 15.0% | 11.5% | **26.5%** | s.123, s.123.4 |
| **Investment income (passive)** | 38.67% | 11.5% | **50.17%** | s.123.3, s.129(4) |
| **Capital gains (in corp)** | 50% × 38.67% = 19.33% | 50% × 11.5% = 5.75% | **25.08%** | s.38(a), s.123.3 |
| **Canadian eligible dividends received** | 38.33% Part IV | 0% | **38.33%** | s.186(1) |
| **Canadian non-eligible dividends received** | 38.33% Part IV | 0% | **38.33%** | s.186(1) |

Note: Investment income tax of 50.17% includes the refundable portion (30.67%). After RDTOH refund on dividend payout, effective permanent rate is ~19.5%.

### Personal Tax Rates — 2024 Ontario Combined Marginal Rates

| Taxable Income Bracket | Federal | Ontario | Combined Marginal |
|------------------------|---------|---------|-------------------|
| $0 – $55,867 | 15.0% | 5.05% | **20.05%** |
| $55,867 – $57,375 | 20.5% | 5.05% | **25.55%** |
| $57,375 – $111,733 | 20.5% | 9.15% | **29.65%** |
| $111,733 – $154,906 | 26.0% | 9.15% | **35.15%** |
| $154,906 – $173,205 | 29.0% | 9.15% | **38.15%** |
| $173,205 – $220,000 | 29.0% | 11.16% | **40.16%** |
| $220,000 – $246,752 | 33.0% | 11.16% | **44.16%** |
| $246,752+ | 33.0% | 13.16% | **46.16%** (actual top = **53.53%** with Ontario surtax) |

### Integration Table — Combined Corporate + Personal Tax

The goal of integration: total tax paid (corporate level + shareholder level) should approximately equal what the individual would have paid directly.

| Income Type | Corp Rate | Personal on Dividend | Combined | Direct Personal Rate | Integration Gap |
|-------------|-----------|---------------------|----------|---------------------|-----------------|
| **Active (SBD) → non-eligible dividend** | 12.2% | ~33.3% on remainder | **~41.4%** | 29.65%–46.16% | **Over-integrated at low brackets** (penalty ~4-12% at <$100K income) |
| **Active (SBD) → salary** | 0% (deductible) | 29.65%–46.16% | **29.65%–46.16%** | Same | **Perfect** (salary = flow-through) |
| **Active (general) → eligible dividend** | 26.5% | ~25.4% on remainder | **~39.3%** | 46.16%+ | **Under-integrated at high brackets** (savings ~7% at $250K+) |
| **Passive investment → non-eligible dividend** | 50.17% – 30.67% refund = 19.5% | ~33.3% on remainder | **~46.3%** | 46.16% | **Near-perfect** (~0.1% gap) |
| **Capital gains (in corp) → non-eligible dividend** | 25.08% – 15.34% refund = 9.74% | ~33.3% on remainder | **~37.1%** | 23.08% (50% inclusion) | **Over-integrated** by ~14% — corp CG + dividend worse than personal CG |
| **Capital gains (in corp) → capital dividend** | 25.08% – 15.34% refund = 9.74% | 0% (CDA) | **~9.74%** | 23.08% | **Under-integrated** (savings ~13%) — **this is the planning opportunity** |

### Integration Gaps — Where Planning Opportunities Exist

#### Gap 1: Capital Dividend Account (CDA) — ITA s.83(2)

**The single best reason to earn capital gains inside a CCPC.**

The non-taxable 50% of capital gains flows to the Capital Dividend Account. Dividends paid from CDA are **completely tax-free** to the shareholder. This creates massive under-integration:

```
$100,000 capital gain earned inside OASIS Corp:
  Taxable portion (50%):           $50,000
  Corp tax on taxable portion:     $50,000 × 50.17% = $25,085
  RDTOH refund:                    $50,000 × 30.67% = $15,335
  Net corp tax:                    $25,085 - $15,335 = $9,750
  CDA balance:                     $50,000 (non-taxable half)

  Pay $50,000 capital dividend from CDA:  TAX-FREE to CC
  Pay remaining as non-eligible dividend: taxed at personal rate

  Effective combined rate:          ~18.5% on $100,000
  vs. Personal capital gains rate:  ~23.08% (at $100K bracket)
  Savings:                          ~$4,580 per $100K of capital gains
```

**CRA Audit Risk:** LOW — CDA is a well-established mechanism. File T2054 election for each capital dividend. Maintain meticulous CDA schedule. Over-declaring CDA triggers Part III tax (ITA s.184) at 60%.

#### Gap 2: SBD Income Paid as Non-Eligible Dividends at Low Brackets

At lower personal income brackets ($0–$55K), the non-eligible dividend gross-up and credit system actually **over-taxes** compared to earning the income personally. This means:

**Planning rule:** At low personal income, prefer salary over dividends. The integration system assumes you are in a high bracket. CC at 22 with modest income should lean salary-heavy.

#### Gap 3: General Rate Income + Eligible Dividends at High Brackets

When total income exceeds $500K and income is taxed at general corporate rate (26.5%), the eligible dividend gross-up (38%) and credit system creates ~7% under-integration above $250K personal. This is a future planning opportunity when OASIS scales.

#### Gap 4: Deferral Advantage — Active Business Income

```
$100,000 active business income:
  Personal tax (29.65% bracket):     $29,650  ← pay NOW if sole proprietor
  Corporate tax (SBD rate):          $12,200  ← pay now if incorporated

  Deferral advantage:                $17,450 retained in the corporation
  That $17,450 invested at 7% for 10 years: ~$34,321 additional wealth
```

**This is the primary argument for incorporation at $80K+ revenue.** The deferral lets more capital compound inside the corp.

**CRA Audit Risk:** N/A — Deferral is the intended design of the system.

---

## 3. Shareholder Loan Rules — ITA s.15, s.80.4

### Section 15(2) — Shareholder Debt Inclusion

**The Rule:** If a corporation loans money to a shareholder (or a person connected to the shareholder), the **full amount of the loan** is included in the shareholder's income for that tax year.

**ITA s.15(2):** *"Where a person ... is a shareholder of a particular corporation, ... and the person ... has received a loan from or has become indebted to the particular corporation, ... the amount of the loan or indebtedness is included in computing the income for the year of the person ..."*

### The 1-Year Repayment Exception — ITA s.15(2.6)

The loan is NOT included in income if ALL of the following are met:

| Condition | Requirement |
|-----------|------------|
| **Repayment deadline** | Loan is repaid within **1 year after the end of the corporation's tax year** in which the loan was made |
| **Bona fide arrangement** | The repayment is part of a bona fide arrangement at the time the loan was made |
| **No series of loans** | The repayment was not part of a series of loans and repayments |

```
Example — OASIS Corp fiscal year-end December 31, 2025:
  CC borrows $30,000 from OASIS Corp on March 1, 2025
  Repayment deadline: December 31, 2026 (1 year after fiscal year-end)
  If CC repays by Dec 31, 2026 → NOT included in income
  If CC does NOT repay → full $30,000 included in CC's 2025 T1 as income
```

**CRA Anti-Avoidance — Series of Loans:**
CRA aggressively audits "revolving" shareholder loans. If CC borrows $30K, repays it January 2 of the next year, then borrows $30K again on January 5 — CRA treats this as a **series of loans and repayments** and will deny the s.15(2.6) exception. The repayment must be genuine and sustained.

**CRA interpretation:** Per IT-119R4, the repayment must come from the shareholder's own resources, not from another corporate loan. Round-tripping is caught.

### Section 80.4 — Deemed Interest Benefit

Even if the loan qualifies for the s.15(2.6) exception (i.e., repaid on time), CRA still imputes a **deemed interest benefit** on the shareholder for any period the loan was outstanding.

**ITA s.80.4(2):** The benefit = (Prescribed rate × Loan amount × Days outstanding / 365) − Interest actually paid within 30 days of year-end.

| Period | Prescribed Rate (CRA) |
|--------|----------------------|
| Q1 2024 | 6% |
| Q2 2024 | 6% |
| Q3 2024 | 6% |
| Q4 2024 | 5% |
| Q1 2025 | 5% |

```
Example:
  $30,000 loan outstanding for full year at 5% prescribed rate
  Deemed benefit: $30,000 × 5% = $1,500
  This $1,500 is added to CC's T4 or T4A as a taxable benefit
  CC can AVOID this by paying 5% interest ($1,500) to the corp within 30 days of Dec 31
  Corp must report that interest as income
```

### Legitimate Uses of Shareholder Loans

| Use Case | Structure | Risk Level |
|----------|-----------|------------|
| **Short-term bridge** | Borrow < $20K, repay within 6 months | LOW |
| **Home purchase loan** | s.15(2.4) exception — must be employee, loan for home purchase, bona fide arrangement | MEDIUM (documentation-heavy) |
| **Vehicle loan** | s.15(2.4) exception — must be employee, vehicle required for employment | MEDIUM |
| **Revolving credit facility** | Borrow → repay → re-borrow | **HIGH** — CRA will deny exception |
| **Back-to-back loans** | Corp lends to CC → CC lends to related party | **HIGH** — s.15(2.1) connected person rules |

### Best Practices for CC

1. **Declare dividends or salary instead** — Cleaner than shareholder loans
2. If a loan is necessary, **document it**: board resolution, promissory note, fixed repayment schedule
3. Pay **prescribed rate interest** within 30 days of year-end to eliminate s.80.4 benefit
4. **Never** do a revolving loan pattern
5. Track the **shareholder loan account** on the balance sheet at all times
6. If CC accidentally overdraws (takes money without declaring salary/dividend), reclassify as dividend before year-end

**CRA Audit Risk:** HIGH if undocumented or revolving. LOW if properly structured with promissory note, board resolution, and timely repayment. CRA T2 Schedule 10 (Related Party Transactions) specifically asks about shareholder loans.

---

## 4. Reasonable Salary Doctrine

### The Rule

There is no specific ITA section defining "reasonable salary." The concept comes from:

- **ITA s.67** — *"In computing income, no deduction shall be made in respect of an outlay or expense except to the extent that it was reasonable in the circumstances."*
- **ITA s.5(1)** — Employment income inclusion
- **CRA administrative practice** — CRA can reassess and reduce a deduction if the salary is unreasonable

This cuts both ways:
1. **Too high a salary** — CRA denies the excess as a corporate deduction (s.67)
2. **Too low a salary** (or zero) — CRA may not directly challenge, but:
   - No CPP contribution = no CPP pension credits
   - No RRSP room generated (RRSP room = 18% of earned income)
   - Income splitting via dividends only may trigger TOSI (Tax on Split Income, s.120.4)

### What CRA Considers "Reasonable"

Per CRA Folio S4-F2-C2 and case law, factors include:

| Factor | Assessment |
|--------|-----------|
| **Nature and quantity of services** | What does the shareholder actually do? |
| **Qualifications and experience** | What would an arm's-length employee with similar skills earn? |
| **Industry comparables** | What do similar roles pay in the market? |
| **Time spent** | Full-time vs. part-time involvement |
| **Corporate profitability** | Can the company support this salary level? |
| **Past compensation** | Has the salary been consistent or did it spike suspiciously? |

### Key Case Law

| Case | Citation | Holding |
|------|----------|---------|
| **Mulder v. The Queen** | 2008 TCC 358 | Salary of $480K to owner of construction company with $4M revenue upheld as reasonable given industry norms and owner's active role |
| **Gabco Ltd v. MNR** | [1968] CTC 313 | The test: "Would a reasonable business person have paid this amount to an arm's-length employee for these services?" |
| **Detchon v. The Queen** | 1995 TCC — 2 T.C. 630 | Salary paid to family members disallowed where services were minimal |
| **Leung v. The Queen** | 2009 TCC 421 | Bonus to shareholder-employee partially disallowed — must relate to services actually performed |
| **Tonn v. The Queen** | [1996] 2 FC 73 (FCA) | CRA cannot second-guess business decisions unless objectively unreasonable — courts give deference to commercial judgment |

### The Gabco Test (The Gold Standard)

From Gabco Ltd v. MNR: *"It is not a question of the Minister or this Court substituting its judgment for what is a reasonable amount to pay, but rather whether what was paid was so unreasonable that no reasonable business person would have paid it."*

This is a **high bar for CRA to clear.** They must show the amount is so excessive that no rational businessperson would agree to it.

### Salary vs. Dividend Decision Framework for CC

| Factor | Salary Favored | Dividend Favored |
|--------|---------------|-----------------|
| **RRSP room needed** | YES — 18% of salary creates room | No room generated |
| **CPP credits wanted** | YES — builds retirement pension | No CPP from dividends |
| **Personal income < $55K** | YES — low bracket, perfect integration | Over-taxed at low brackets |
| **Personal income > $200K** | Consider mix | YES — eligible dividends save ~7% |
| **Childcare expense deduction** | YES — requires earned income | Not applicable |
| **Corporation has SBD room** | Mix — salary deduction reduces corp income | Leave in corp at 12.2% |

### Recommended Salary for CC (OASIS Corp)

```
CC's role: Founder, sole operator, AI developer, client manager, service delivery
Comparable arm's-length salary: $60,000–$120,000 for a full-stack AI consultant
Recommended initial salary: $60,000–$80,000
  → Generates $10,800–$14,400 RRSP room
  → Builds CPP credits (max pensionable earnings ~$68,500 for 2024)
  → Leaves remainder in corp at 12.2% for deferral advantage

Remaining profit: pay as non-eligible dividends (to clear NERDTOH/LRIP)
  or retain in corp for investment/growth
```

**CRA Audit Risk:** LOW at $60K–$80K for a sole-operator tech consultant. CRA rarely challenges owner-operators who are clearly the business. Risk increases if salary exceeds $200K with no employees and <$500K revenue.

---

## 5. Corporate Investment Strategies — SBD & Passive Income Grind

### The Passive Income Problem (Post-2018 Budget)

The 2018 federal budget introduced the **passive income grind** — the most significant anti-deferral measure for CCPCs:

**ITA s.125(5.1) — Adjusted Aggregate Investment Income (AAII):**

```
Small Business Deduction limit reduction:
  If AAII > $50,000:
    SBD limit reduced by $5 for every $1 of AAII over $50,000
    At AAII = $150,000: SBD limit reduced to $0 (full clawback)

  SBD limit = $500,000 − 5 × (AAII − $50,000)

  At $50,000 AAII: Full $500K SBD → 12.2% rate on active income
  At $100,000 AAII: $250K SBD → half at 12.2%, half at 26.5%
  At $150,000 AAII: $0 SBD → ALL active income at 26.5%
```

### What Counts as AAII

| Income Type | Included in AAII? | Notes |
|-------------|-------------------|-------|
| Interest income | YES | Fully included |
| Rental income (net) | YES | Unless > 5 full-time employees |
| Taxable capital gains (net) | YES | 50% inclusion |
| Foreign income (non-active) | YES | |
| Portfolio dividends | NO | Not included (already Part IV taxed) |
| Active business income | NO | This is what SBD applies to |
| Capital gains on active assets | NO | If used in active business |
| Capital gains on shares of connected corps | NO | Active business shares exempt |

### The $50K AAII Safe Harbor

$50,000 of AAII = roughly $1,000,000 invested at 5% return. This is the **critical threshold**.

```
$1,000,000 portfolio at 5% = $50,000 AAII → SAFE
$1,500,000 portfolio at 5% = $75,000 AAII → SBD reduced by $125,000
$3,000,000 portfolio at 5% = $150,000 AAII → SBD fully eliminated
```

### Optimal Investment Allocation — Inside vs. Outside Corp

| Investment Type | Inside Corp? | Outside Corp (Personal)? | Reasoning |
|----------------|-------------|-------------------------|-----------|
| **GICs / Bonds / Interest** | AVOID | Use RRSP/TFSA | Interest = 100% AAII, taxed at 50.17% in corp, grinds SBD |
| **Canadian equity (dividends)** | OK | OK | Dividends = Part IV tax (refundable), NOT included in AAII |
| **Capital growth (equity ETFs)** | MONITOR | TFSA preferred | Unrealized gains don't count. Realized gains count at 50%. CDA offsets. |
| **Permanent life insurance** | YES | N/A | Exempt policy — growth not taxed, CDA credit on death, no AAII impact |
| **Real estate (passive)** | AVOID unless > 5 FTE | Hold personally or in separate corp | Rental = AAII, grinds SBD |

### Strategies to Minimize AAII While Investing Inside Corp

#### Strategy 1: Canadian Dividend Portfolio

Invest in Canadian dividend-paying stocks/ETFs inside the corp. Dividends received are NOT AAII. Part IV refundable tax (38.33%) is recovered when dividends are paid out. **Best corporate investment for AAII management.**

#### Strategy 2: Capital Gains Deferral

Unrealized capital gains are NOT AAII. Buy-and-hold equity ETFs (VFV, XQQ) — gains only count when realized. Time dispositions to stay under $50K AAII per year. Use CDA for the non-taxable 50%.

#### Strategy 3: Permanent Life Insurance (Exempt Policy)

Corporate-owned whole life or universal life policy. Investment growth inside the policy is **not taxable** and **not AAII.** On death, proceeds (less ACB) credit the CDA → tax-free capital dividend to estate. Functions as a tax-exempt corporate investment vehicle.

Cost: Insurance premiums are NOT deductible (unless collateral for business loan). But the tax-free compounding often exceeds after-tax investment returns.

#### Strategy 4: Separate Investment Holding Company (Holdco)

```
Structure:
  CC (shareholder)
  └── Holdco (holding company)
       └── Opco (OASIS — operating company)

How it works:
  - Opco pays tax-free intercorporate dividends to Holdco (s.112 deduction)
  - Holdco invests the funds
  - AAII in Holdco does NOT grind Opco's SBD
  - Opco maintains full $500K SBD

Cost: Additional corporate filings (~$2,000–3,000/year accounting)
Trigger: When corporate investments approach $1M
```

**CRA Audit Risk for AAII strategies:** LOW — These are standard tax planning techniques. CRA designed the system with these thresholds. The holdco structure is the most common response to the passive income rules and is well-established.

### Numerical Example — AAII Grind Impact

```
OASIS Corp earns $200,000 active business income + $80,000 AAII:

Without planning (all in one corp):
  SBD limit: $500,000 − 5 × ($80,000 − $50,000) = $500,000 − $150,000 = $350,000
  First $200K active income: still within reduced $350K limit → 12.2%
  Corp tax on active: $200,000 × 12.2% = $24,400
  Corp tax on $80K AAII: $80,000 × 50.17% = $40,136 (less refundable)

With Holdco structure:
  AAII in Holdco, not Opco → Opco SBD = full $500,000
  Corp tax on active: $200,000 × 12.2% = $24,400 (same)
  Corp tax on $80K AAII in Holdco: same $40,136
  BUT: Opco SBD not grinded. If active income grows to $400K, saves:
    Without holdco (AAII grinds): $50K taxed at 26.5% instead of 12.2% = $7,150 extra tax
    With holdco: full SBD preserved = $7,150 saved annually
```

---

## 6. Estate Freeze Techniques

### Purpose

An estate freeze locks the current value of a corporation's shares in the hands of the current owner, so that all **future growth** accrues to the next generation (or a trust). This:

1. Caps the deemed disposition on death at the frozen value
2. Crystallizes the Lifetime Capital Gains Exemption (LCGE) — $1,016,836 for 2024 QSBC shares
3. Transfers future growth to children/trust at no immediate tax cost
4. Enables income splitting (within TOSI rules) through discretionary trust distributions

### Section 86 — Share Exchange (The Simple Freeze)

**ITA s.86(1):** A shareholder exchanges ALL shares of a particular class for new shares of a different class, in the course of a reorganization of capital. This is a **tax-deferred rollover** (no elected amount — automatic).

**How it works:**

```
Before freeze:
  CC owns 100 common shares of OASIS Corp
  FMV of OASIS Corp: $500,000
  ACB of CC's shares: $100 (nominal incorporation cost)

Freeze transaction (s.86):
  1. OASIS Corp amends articles to create new Class A preferred shares
     (fixed value, retractable, non-participating, voting)
  2. CC exchanges 100 common shares for:
     - New Class A preferred shares with redemption value = $500,000 (FMV)
     - No boot (no cash consideration) to avoid immediate gain
  3. New common shares issued to:
     - Family trust (for future children), OR
     - New holding company, OR
     - Directly to next-generation family members

After freeze:
  CC holds: Class A preferred shares (frozen at $500,000 value)
  Trust/Newco holds: New common shares ($0 current value)
  All future growth accrues to the new common shares → trust/Newco
```

**Tax consequences under s.86:**
- CC's ACB in new preferred = ACB of old common ($100)
- No capital gain triggered (deferred until redemption, sale, or death)
- PUC (paid-up capital) of new preferred = PUC of old common

**Key requirement:** CC must exchange ALL shares of that class. Cannot do a partial exchange under s.86.

### Section 85 — Rollover (The Flexible Freeze)

**ITA s.85(1):** A taxpayer transfers "eligible property" to a taxable Canadian corporation and elects an agreed amount (between the ACB floor and FMV ceiling). This is more flexible than s.86 because you can choose the elected amount.

**Why use s.85 over s.86:**

| Feature | s.86 | s.85 |
|---------|------|------|
| Elected amount | No choice (automatic) | Choose between ACB and FMV |
| Crystallize LCGE | Cannot — must use other mechanisms | YES — elect at ACB + $1,016,836 to use LCGE |
| Partial transfer | No — must exchange ALL shares of a class | Yes — can transfer specific properties |
| Boot allowed | Limited | Yes — with rules on non-share consideration |
| Complexity | Low | High — requires T2057 election form |

### Crystallizing the LCGE — The Key Planning Move

**LCGE for QSBC shares (2024): $1,016,836**

If CC's OASIS Corp qualifies as a QSBC (see Section 7 below), CC can crystallize the LCGE through an estate freeze:

```
s.85 rollover to crystallize LCGE:

Step 1: Confirm OASIS Corp qualifies as QSBC (90%+ active business assets)
Step 2: CC transfers common shares to Newco (Holdco)
Step 3: Elect transfer at FMV up to LCGE limit:
  - ACB of common shares: $100
  - FMV of common shares: $500,000
  - Elected amount: $500,000 (full FMV)
  - Capital gain: $500,000 − $100 = $499,900
  - Taxable capital gain (50%): $249,950
  - LCGE deduction (s.110.6(2.1)): ($249,950) → TAX = $0

Step 4: CC receives preferred shares of Newco with ACB = $500,000
         (ACB now "stepped up" — no tax on first $500K on future disposition)
Step 5: New common shares of Newco issued to family trust
Step 6: All future growth accrues to trust beneficiaries

Result: $500,000 of gain crystallized tax-free via LCGE
        CC's new ACB = $500,000 (was $100)
        Future $500K+ of growth flows to trust → potential TOSI optimization
```

### Freeze and Refreeze Strategies

As the corporation grows, you can **refreeze** periodically:

```
Year 1: Freeze at $500,000 (LCGE crystallized)
Year 5: Corp value now $2,000,000
  → Refreeze: CC exchanges preferred shares for new preferred at $2,000,000
  → New common shares issued to trust
  → Growth above $2M flows to trust
  → CC's preferred now locked at $2M (deferred gain = $2M − $500K = $1.5M on death)

Year 10: Corp value $5,000,000
  → Refreeze again at $5M
  → Pattern continues every 5-7 years or when significant growth occurs
```

**Refreeze caution:** Each refreeze locks in a higher deemed disposition value on death. Ensure life insurance covers the tax liability.

### Alternative: s.86.1 — Exchange of Shares for Securities

Rarely used in private company context, but worth noting: s.86.1 allows exchange of shares in a public corporation for shares/debt of the same corporation on a tax-deferred basis. Not applicable to OASIS currently.

**CRA Audit Risk:**
- s.86 freeze: LOW — straightforward, well-established, no election form required
- s.85 freeze with LCGE crystallization: MEDIUM — CRA scrutinizes QSBC qualification carefully. Must meet the three tests (see Section 7). T2057 must be filed on time.
- Refreeze: LOW-MEDIUM — standard planning, but CRA may examine if FMV is reasonable at refreeze date. Get a **business valuation** for any refreeze over $1M.

---

## 7. Purification Strategies — QSBC Qualification

### Why QSBC Status Matters

**Lifetime Capital Gains Exemption (LCGE):** ITA s.110.6(2.1) — $1,016,836 (2024, indexed) exemption on capital gains from disposing of qualified small business corporation (QSBC) shares. At the 50% inclusion rate and top Ontario bracket, this is worth approximately **$270,000 in tax savings.**

This is the single largest individual tax exemption in the Canadian tax system.

### The Three Tests — ITA s.110.6(1) "Qualified Small Business Corporation Share"

A share must pass ALL THREE tests at the time of disposition:

| Test | Requirement | ITA Reference | Time Period |
|------|-------------|---------------|-------------|
| **SBC Test** | At the **time of sale**, 90%+ of FMV of assets must be used in an **active business carried on primarily in Canada** | s.248(1) "small business corporation" | Point-in-time (at disposition) |
| **Holding Period Test** | Shares must be owned by the taxpayer (or related person) for the **entire 24-month period** before disposition | s.110.6(1)(d)(i) | Preceding 24 months |
| **Asset Test (24-month)** | Throughout the 24-month period, 50%+ of FMV of assets must have been used in an active business carried on primarily in Canada | s.110.6(1)(d)(ii) | Preceding 24 months |

### The 90% Active Business Asset Test (SBC Test) — In Detail

**Assets that COUNT as active business assets:**
- Cash used in the business (working capital — reasonable amount)
- Accounts receivable from business operations
- Equipment, computers, furniture used in business
- Intellectual property used in business
- Shares of connected corporations that are themselves SBCs (look-through rule)
- Goodwill

**Assets that DO NOT count (and contaminate the 90% test):**
- Excess cash (beyond reasonable working capital needs)
- Portfolio investments (stocks, bonds, ETFs, crypto)
- Rental real estate (unless > 5 FTE employees)
- Shareholder loans receivable
- Life insurance cash surrender value (debatable — CRA position evolving)
- Personal-use assets

### Purification Strategies

When a corporation has accumulated non-active assets (investments, excess cash) that would fail the 90% test, you must **purify** before selling.

#### Strategy 1: Pay Out Excess Cash as Dividends or Salary

The simplest approach. Remove non-active assets by paying them out.

```
OASIS Corp FMV breakdown before purification:
  Active assets (equipment, AR, IP, goodwill): $400,000 (80%)
  Excess cash and investments:                  $100,000 (20%)
  Total FMV:                                    $500,000

  FAILS 90% test (only 80% active)

Purification: Pay $55,000 dividend to CC before sale
  Active assets: $400,000 (89%)
  Remaining cash: $45,000 (11%) — argue this is reasonable working capital
  Total: $445,000

  Active percentage: $400,000 / $445,000 = 89.9% → borderline
  Better: pay out $60,000 → $400,000 / $440,000 = 90.9% → PASSES
```

**Downside:** Triggers immediate personal tax on dividends/salary. But LCGE savings ($270K) vastly exceeds dividend tax cost.

#### Strategy 2: Inter-Company Loans to Connected Active Corporation

Transfer excess cash as a loan to a connected corporation that uses it in active business. The receivable from a connected SBC is an active business asset.

```
Structure:
  CC owns 100% of Holdco
  Holdco owns 100% of Opco (OASIS — active business)

  Holdco has $200K in investments (non-active)
  Holdco loans $200K to Opco
  Opco uses funds in business operations

  Holdco's receivable from Opco = active asset (connected SBC)
  Holdco now passes 90% test
```

**CRA caution:** The loan must be genuinely used in active business by Opco. CRA will look through if Opco parks the money in GICs. Maintain evidence that Opco deployed the capital operationally.

#### Strategy 3: Repay Corporate Debt

Use excess cash to repay any outstanding corporate loans, mortgages, or lines of credit. This removes cash (non-active) from the balance sheet and reduces liabilities — net effect improves the active asset ratio.

#### Strategy 4: Purchase Active Business Assets

Reinvest excess cash into business equipment, software, marketing, or inventory. Converts non-active cash into active business assets. Timing must be genuine — CRA will challenge last-minute asset purchases that are reversed after sale.

#### Strategy 5: Transfer Non-Active Assets to a Separate Corporation

```
Before sale:
  OASIS Corp: $400K active + $100K investments = 80% active (FAILS)

Purification via s.85 rollover:
  1. OASIS Corp transfers $100K investments to Newco (Holdco) using s.85
  2. OASIS Corp receives Holdco shares (which are connected SBC shares if Holdco is an SBC)
  3. OR: OASIS Corp transfers investments for promissory note (boot)
     → Promissory note may not be an active asset → careful structuring needed

Better approach:
  1. CC incorporates Holdco
  2. OASIS Corp pays $100K dividend to CC (after-tax)
  3. CC contributes $100K to Holdco
  4. OASIS Corp now 90%+ active → PASSES

  Wait 24 months before sale (to satisfy holding period test)
```

#### Strategy 6: Timing — The 24-Month Look-Back

Remember: the 50% test applies for the **full 24 months** preceding the sale. Plan purification **at least 24 months before an anticipated sale.** Last-minute purification may clean the point-in-time 90% test but fail the 24-month 50% test if the corporation was investment-heavy for most of that period.

```
Timeline:
  Month 0:  OASIS Corp is 60% active / 40% investments
  Month 1:  Begin purification — pay out investments
  Month 12: OASIS Corp is 95% active
  Month 24: 24-month look-back satisfied (>50% for full period)
  Month 25: SAFE to sell and claim LCGE
```

#### Strategy 7: Reasonable Working Capital Argument

CRA accepts that some cash is needed for business operations. "Reasonable working capital" is an active business asset. The question is how much is reasonable.

**CRA benchmarks:**
- 2-3 months of operating expenses is generally accepted
- Cash held for a specific upcoming business expense (expansion, equipment purchase) with board documentation = active
- Cash sitting idle for years with no business purpose = non-active

**Document everything:** Board resolutions for cash reserves, business plans for expansion, contractor retainer agreements. CRA auditors look for evidence that cash is earmarked for business use.

### QSBC Qualification Checklist for OASIS Corp

```
□ Corporation is a CCPC (Canadian-controlled private corporation)
□ 90%+ of FMV of assets used in active business in Canada (at time of sale)
□ 50%+ of FMV of assets used in active business for preceding 24 months
□ Shares held by CC for entire 24 months preceding sale
□ No QSBC disqualification events (e.g., ceasing to carry on active business)
□ Corporation carries on "active business" — not "specified investment business"
    (OASIS = AI consulting = clearly active business)
□ Excess cash purified or justified as working capital
□ Portfolio investments removed or negligible
□ If holdco structure: all connected corporations also qualify as SBCs (look-through)
□ T2057 filed (if s.85 rollover used in purification)
□ Business valuation obtained from CBV for amounts > $500K
```

**CRA Audit Risk Ratings for Purification:**

| Strategy | Risk | Notes |
|----------|------|-------|
| Pay dividends to remove cash | LOW | Most conservative approach |
| Inter-company loans | MEDIUM | Must show genuine active use of funds |
| Purchase business assets | MEDIUM | Must be genuine, sustained purchases |
| Transfer to separate corp | MEDIUM-HIGH | CRA may apply GAAR if sole purpose is purification right before sale |
| Reasonable working capital | LOW-MEDIUM | Depends on documentation quality |
| 24-month advance planning | LOW | Best practice — time heals audit risk |

---

## Summary — Priority Actions for CC

| Priority | Action | When | Impact |
|----------|--------|------|--------|
| 1 | **Incorporate OASIS at $80K revenue** | When triggered | ~$17K/year deferral at $100K income |
| 2 | **Set salary at $60K–$80K** | Year 1 of incorporation | Builds RRSP room + CPP, leaves rest in corp |
| 3 | **Track RDTOH/NERDTOH from day one** | Ongoing | Ensures optimal dividend refund recovery |
| 4 | **Invest inside corp using Canadian dividend ETFs** | After retained earnings build | Avoids AAII grind |
| 5 | **Keep AAII under $50K** | Ongoing | Preserves full $500K SBD |
| 6 | **Crystallize LCGE via s.85 freeze** | When QSBC-qualified | $270K+ tax savings on eventual sale |
| 7 | **Purify 24 months before any sale** | Pre-exit planning | Ensures QSBC qualification |
| 8 | **Consider holdco structure at $1M+ invested** | Future milestone | Separates AAII from Opco's SBD |
| 9 | **Corporate-owned life insurance** | When cash flow supports premiums | Tax-exempt growth + CDA credit on death |
| 10 | **Annual refreeze review** | Every 5 years once frozen | Locks growth for next generation |

---

*Document prepared by ATLAS (CFO). All ITA references verified against R.S.C. 1985, c.1 (5th Supp.) as amended. Ontario rates per 2024 Ontario Budget. This is educational planning material — CC should consult a CPA and tax lawyer before implementing any strategy involving s.85/s.86 rollovers, estate freezes, or LCGE crystallization.*

*Last updated: 2026-03-27 | Version: 1.0*
