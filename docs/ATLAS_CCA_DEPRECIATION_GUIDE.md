# ATLAS — Capital Cost Allowance (CCA) & Depreciation Guide
## Complete Canadian Tax Depreciation Reference for CC's CFO Engine

> **Atlas Role:** This document is the authoritative CCA reference for ATLAS operations. Use it to
> maximize deductions on all business assets, plan acquisitions for maximum tax efficiency, and
> defend every position taken on T2125, T776, and T2 returns.
>
> **ITA Authority:** s.20(1)(a), Regulations Part XI (s.1100–1107), Schedule II of the Regulations
> **CRA References:** IT-79R3, IT-195R4, IT-285R2, IT-464R, IT-478R2, IT-514, IT-522R

---

## TABLE OF CONTENTS

1. [CCA Fundamentals](#1-cca-fundamentals)
2. [The Half-Year Rule and Its Replacements](#2-the-half-year-rule-and-its-replacements)
3. [Accelerated Investment Incentive (AII)](#3-accelerated-investment-incentive-aii)
4. [Immediate Expensing — $1.5M CCPC Deduction](#4-immediate-expensing--15m-ccpc-deduction)
5. [Available for Use Rules](#5-available-for-use-rules)
6. [Recapture — When CCA Gets Clawed Back](#6-recapture--when-cca-gets-clawed-back)
7. [Terminal Loss — When You Over-Depreciated](#7-terminal-loss--when-you-over-depreciated)
8. [Change of Use Rules](#8-change-of-use-rules)
9. [Complete CCA Class Reference Table](#9-complete-cca-class-reference-table)
10. [Class-by-Class Deep Dive](#10-class-by-class-deep-dive)
11. [CCA Calculation Worksheets](#11-cca-calculation-worksheets)
12. [Advanced CCA Strategies](#12-advanced-cca-strategies)
13. [Automobile CCA Optimization](#13-automobile-cca-optimization)
14. [Rental Property CCA — The Restriction Nobody Knows](#14-rental-property-cca--the-restriction-nobody-knows)
15. [Home Office CCA — The PRE Trap](#15-home-office-cca--the-pre-trap)
16. [Software, Hardware, and AI Tools](#16-software-hardware-and-ai-tools)
17. [Class 14.1 — Goodwill and Intangibles](#17-class-141--goodwill-and-intangibles)
18. [Lease vs Buy — Tax Comparison](#18-lease-vs-buy--tax-comparison)
19. [CCA on T2125, T776, and T2](#19-cca-on-t2125-t776-and-t2)
20. [CRA Audit Triggers for CCA](#20-cra-audit-triggers-for-cca)
21. [CC-Specific CCA Planning](#21-cc-specific-cca-planning)
22. [Quick Reference Cheat Sheet](#22-quick-reference-cheat-sheet)

---

## 1. CCA FUNDAMENTALS

### What is Capital Cost Allowance?

Capital Cost Allowance (CCA) is Canada's tax depreciation system. It is **not** the same as accounting
depreciation (which follows GAAP/IFRS). CCA is a **statutory deduction** under ITA s.20(1)(a) that
allows taxpayers to deduct a portion of the cost of depreciable property used to earn income.

**Key principle:** CCA reduces taxable income dollar-for-dollar. On a marginal rate of 46.16% (Ontario
2024, $100K+ income), every $1,000 of CCA claimed saves $461.60 in tax.

### ITA Authority

| Section | What It Does |
|---------|-------------|
| **s.20(1)(a)** | Authorizes the CCA deduction against income |
| **s.13(1)** | Recapture — excess CCA forced back into income |
| **s.20(16)** | Terminal loss deduction on class extinction |
| **s.13(7)** | Change of use rules — deemed disposition at FMV |
| **s.13(21)** | Definitions: UCC, capital cost, proceeds of disposition |
| **s.13(26)-(28)** | Available for use rules |
| **Reg. 1100** | CCA rates for each class |
| **Reg. 1101** | Separate class elections |
| **Reg. 1102** | Property excluded from CCA classes |
| **Schedule II** | Prescribed classes of depreciable property |

### The Undepreciated Capital Cost (UCC) Concept

Every CCA class has a running balance called the **Undepreciated Capital Cost (UCC)**. This is the
tax book value — not FMV, not accounting book value.

```
Opening UCC
+ Additions (cost of new property added to the class)
- Dispositions (lesser of: proceeds of disposition OR original cost of disposed asset)
- Government assistance received (grants, rebates, ITCs reduce capital cost)
= Net UCC before CCA
- CCA claimed (any amount from $0 to the maximum)
= Closing UCC (becomes next year's Opening UCC)
```

**Critical rule:** CCA is **optional**. You can claim any amount from $0 to the maximum. This is the
single most powerful planning tool — defer or accelerate based on your income needs.

### Declining Balance vs Straight-Line

**Declining Balance (most classes):**
- Rate applied to UCC (not original cost) each year
- Balance never fully depreciates to zero (asymptotic)
- Higher deduction in early years, lower in later years
- Classes 1, 8, 10, 10.1, 14.1, 50, etc.

**Straight-Line (specific classes):**
- Fixed amount each year based on original cost or useful life
- Class 13 (leasehold improvements): over lease term
- Class 14 (limited-life intangibles): over legal life
- Class 29 (historical M&P equipment): 25%/50%/25% schedule

### Separate vs Pooled Classes

**Pooled class:** Multiple assets in one UCC pool. Most classes are pooled.
- Risk: if you sell one asset for more than UCC, recapture triggers for the whole class
- Benefit: individual asset dispositions don't automatically cause recapture

**Separate class (per asset):** Some rules or elections require one UCC pool per asset.
- Class 10.1: each passenger vehicle > limit gets its own class
- Class 1: election available for rental buildings > $50K (s.1101(1ac))
- Benefit of separate class: terminal loss available on individual assets

---

## 2. THE HALF-YEAR RULE AND ITS REPLACEMENTS

### Original Half-Year Rule — s.1100(2) (Still Applies in Some Cases)

For property **not** eligible for AII (acquired before Nov 21, 2018, or phaseout period):

**Rule:** In the year of acquisition, only **50% of the normal CCA** can be claimed.

This prevents taxpayers from buying an asset on December 31 and claiming a full year of CCA.

**Example:** Class 8 (20%), $10,000 purchase
- Without half-year rule: $10,000 × 20% = $2,000
- With half-year rule: $10,000 × 20% × 50% = $1,000

### Half-Year Rule Phaseout Under AII

For **eligible property acquired after November 20, 2018**, the half-year rule is replaced by the
Accelerated Investment Incentive (AII). See Section 3 below.

### When the Half-Year Rule Still Applies

| Situation | Half-Year Rule Applies? |
|-----------|------------------------|
| Property acquired before Nov 21, 2018 | Yes |
| Property excluded from AII (listed personal property, etc.) | Yes |
| AII phaseout period (2024–2027) — partial AII | Depends on AII factor |
| Class 12, 14 (100% or straight-line) | Irrelevant (100% claimed anyway) |

---

## 3. ACCELERATED INVESTMENT INCENTIVE (AII)

### What AII Does

The AII, introduced in the 2018 Fall Economic Statement, allows businesses to write off **three times**
the normal first-year CCA for eligible property acquired after November 20, 2018. It was designed to
counter US tax reform and encourage Canadian business investment.

**Authority:** Reg. 1100(2)(a)(ii) and related provisions; Finance Canada Technical Notes Nov 2018

### AII Mechanics

**Normal first-year (with half-year rule):** UCC × rate × 50%
**AII first-year:** UCC × rate × **1.5**

The "1.5" factor means: instead of 50% of normal, you get 150% of normal — three times the
half-year amount.

**Effective first-year rates with AII:**

| Class | Normal Rate | Half-Year Amount | AII First Year |
|-------|-------------|-----------------|----------------|
| Class 1 (buildings) | 4% | 2% | 6% |
| Class 6 | 10% | 5% | 15% |
| Class 8 (misc.) | 20% | 10% | 30% |
| Class 10 (vehicles) | 30% | 15% | 45% |
| Class 10.1 | 30% | 15% | 45% |
| Class 43 (M&P) | 30% | 15% | 45% |
| Class 43.2 (clean energy) | 50% | 25% | 75% |
| Class 50 (computers) | 55% | 27.5% | 82.5% |
| Class 14.1 (goodwill) | 5% | 2.5% | 7.5% |

### AII — Zero-Emission Vehicles (Full First-Year)

For Class 54 (ZEV passenger) and Class 55 (ZEV commercial) acquired after March 18, 2019 and before
2024:
- **100% write-off in year 1** (not subject to half-year rule or AII factor)
- This is better than AII — effectively immediate expensing for ZEVs

### AII Phaseout Schedule

The AII is being wound down as the economy normalized post-COVID. The transition affects property that
becomes available for use after the following dates:

| Period | AII Factor |
|--------|-----------|
| After Nov 20, 2018 – before 2024 | 1.5× (full AII) |
| 2024 – 2025 | 1.0× (i.e., 100% of normal half-year — no enhancement) |
| 2026 – 2027 | 0.75× |
| 2028 and later | Half-year rule applies (0.5× = back to normal) |

**Planning implication for CC (2026):** The AII has phased to 0.75× for property available for use in
2026. The old half-year rule effectively returns in 2028. Accelerate major acquisitions before 2028
if possible.

### AII — Immediate Expensing Interaction

For CCPCs, **immediate expensing trumps AII** on eligible property up to $1.5M. Use immediate
expensing first (100%), then AII for amounts above $1.5M or ineligible property.

---

## 4. IMMEDIATE EXPENSING — $1.5M CCPC DEDUCTION

### Overview

Budget 2021 introduced a temporary (later extended) rule allowing **Canadian-Controlled Private
Corporations (CCPCs)** to immediately expense up to **$1.5 million** of eligible depreciable property
acquired after April 18, 2021 and available for use before January 1, 2024. Budget 2023 extended
this for individuals and partnerships.

**Authority:** ITA s.13(1.1), (1.2); Reg. 1100(0.1)–(0.2)

### Who Qualifies

| Taxpayer Type | Eligible? | Limit | Period |
|---------------|-----------|-------|--------|
| CCPC | Yes | $1,500,000 | After Apr 18, 2021 |
| Canadian individual (sole proprietor) | Yes | $1,500,000 | After Dec 31, 2021 |
| Partnership with CCPC/individual members | Yes | $1,500,000 shared | Same |
| Non-CCPC corporations | No | N/A | N/A |
| Trusts | No | N/A | N/A |

**CC's status:** As a sole proprietor operating OASIS AI Solutions, CC qualifies for the individual
immediate expensing limit of $1,500,000.

### Eligible Property (EPOP — Eligible Property of an Eligible Person)

Immediate expensing applies to **all CCA classes except:**
- Class 1 to 6, 14, 14.1, 17, 47, 49, and 51
- Essentially: buildings, most structures, limited-life intangibles, and pipeline/transmission property
- **All equipment classes (8, 10, 10.1, 12, 43, 50, 53, 54, 55, 56) are eligible**

### How Immediate Expensing Works

1. Identify eligible property acquired and available for use in the year
2. Apply immediate expensing to bring UCC to zero (100% deduction) up to $1.5M limit
3. Any remaining cost beyond $1.5M uses AII/normal CCA rules
4. The $1.5M limit is per year, not per class

**Example — CC buys $80,000 of computer equipment (Class 50) in 2024:**
- Immediate expensing: claim 100% = $80,000 deduction in year 1
- Tax saving at 46.16% marginal: $36,928
- vs. normal Class 50 (55%): $44,000 first year → $20,312 tax saving
- **Immediate expensing saves $16,616 more in year 1**

### $1.5M Limit Allocation Strategy

When multiple asset types are acquired, prioritize immediate expensing on **lower-rate classes first**:

| Priority | Class | Why |
|----------|-------|-----|
| 1st | Class 1 (4% buildings) | NOT eligible for immediate expensing — use AII |
| 2nd | Class 14.1 (5% goodwill) | NOT eligible — use AII |
| 3rd | Class 8 (20%) | Eligible — immediate expensing massively improves write-off vs 30% AII |
| 4th | Class 50 (55%) | Eligible — but AII already gives 82.5% first year, lower incremental benefit |
| 5th | Class 12 (100%) | Already 100% without immediate expensing — no benefit |

**Counter-intuitive truth:** Immediate expensing adds the most value on **slow-depreciating classes**
because normal CCA leaves them on the books for decades. A 4% building takes 17+ years to reach 50%
depreciated; immediate expensing collapses that to year 1.

---

## 5. AVAILABLE FOR USE RULES

### The Problem These Rules Solve

CRA won't let you claim CCA on property you've paid for but haven't started using. Without this rule,
taxpayers could buy equipment in December, claim CCA, and not actually use it until next year.

**Authority:** ITA s.13(26), (27), (28)

### General Rule — s.13(26)

Property is **available for use** on the **earlier of:**
1. The time the taxpayer first uses the property for the purpose of earning income
2. The time the property is delivered (or construction completed if self-constructed) and reasonably
   expected to be used for income-earning purposes

### Special Rules

**Buildings under construction — s.13(27):**
- Building acquired to be used for rental or business: available for use when construction is complete
  AND the property can be used for its intended purpose
- If construction is on taxpayer's land: when building is completed AND tenant/use is in place
- Special 2-year rule: property available for use no later than **2 years after year of acquisition**,
  even if not yet in use

**Exception — s.13(28) (the 2-year deemed rule):**
- If property is not available for use by the end of the **second calendar year** after the year of
  acquisition, it is **deemed available for use** at the start of the third year
- This prevents indefinite deferral of CCA claims

### Planning Implication

If buying equipment late in the year for use next year:
- Confirm "delivery + reasonable expectation of income use" is met before year-end
- Keep documentation: delivery receipts, purchase orders, first use records
- For buildings: construction completion certificate, first lease commencement date

---

## 6. RECAPTURE — WHEN CCA GETS CLAWED BACK

### What Triggers Recapture

Recapture occurs when the **UCC of a class drops below zero** — meaning you received more proceeds
(or deemed proceeds) than the remaining tax book value of assets in that class.

**Authority:** ITA s.13(1)

**Recapture = fully taxable income (not capital gain)**

This is the most important distinction: recapture is taxed at your **full marginal rate**, while
capital gains are taxed at 50% inclusion. On a $100,000 recapture at 46.16% marginal = $46,160 tax.

### When It Happens

```
Example: Class 8 (20% declining balance)
Opening UCC: $5,000 (all that's left in the class)
Sell all assets for proceeds of: $12,000
Deemed proceeds capped at original cost: $10,000

UCC calculation:
$5,000 - $10,000 (lesser of proceeds $12,000 or cost $10,000) = -$5,000

Negative UCC = $5,000 RECAPTURE → included in income as s.13(1) income
Remaining $2,000 ($12,000 - $10,000) = capital gain (taxable at 50% inclusion)
```

### Recapture vs Capital Gain Split

When proceeds exceed original cost:
- **Proceeds up to original cost:** triggers recapture (if UCC was lower)
- **Proceeds above original cost:** capital gain (taxable at 50% inclusion rate)

### Recapture Planning Strategies

**Strategy 1 — Keep the class open:**
Buy a cheap replacement asset before year-end to keep UCC positive. If you sell your $5,000 UCC
asset for $12,000, buy a $100 asset in the same class. This keeps the class open and prevents
forced recapture until you're ready to trigger it in a low-income year.

**Strategy 2 — Time the disposition:**
Trigger recapture in years with large deductions (RRSP room, business losses, other CCA) to offset.

**Strategy 3 — Reserve low-income year:**
If retirement or sabbatical is planned, time major asset disposals to that year. Recapture at 20%
effective rate is far better than 46% during peak earning years.

**Strategy 4 — Incorporate before selling:**
Transfer business assets to CCPC at ACB (using s.85 rollover). The corporation holds the assets;
no recapture until corporation sells. Small business deduction brings corporate rate to 12.2%
(Ontario) on first $500K active income, which can include recapture if it's incidental to M&P.

---

## 7. TERMINAL LOSS — WHEN YOU OVER-DEPRECIATED

### What is Terminal Loss

The opposite of recapture. When all assets in a class are **disposed of** and the **UCC is still
positive**, the remaining balance is a **terminal loss** — fully deductible against income.

**Authority:** ITA s.20(16)

```
Example: Class 8
Opening UCC: $8,000
Sell last asset in class for: $3,000

UCC = $8,000 - $3,000 = $5,000 remaining UCC
All assets disposed — no property left in class

Terminal loss = $5,000 → deductible against any income
```

### Terminal Loss NOT Available: Class 10.1

For Class 10.1 (passenger vehicles over the $37K limit), **no terminal loss is allowed** on
disposition — s.13(2). You simply close the class and lose the remaining UCC. This is the price
of the separate-class treatment.

**CCA is also restricted in the year of disposal:** only half-year CCA (or zero, depending on
disposition timing) is allowed in the year you dispose of a Class 10.1 vehicle.

### Terminal Loss on Rental Buildings

If you make the separate-class election for rental buildings (s.1101(1ac)), each building gets
its own UCC pool. You can therefore trigger a terminal loss on one building without affecting others.

This is enormously valuable: if rental property has dropped in value (vacancy, damage, market
decline), selling it can generate a terminal loss that offsets other income — on top of any capital
loss on the land portion.

### Creating Terminal Loss

**Related-party transfers:** You can transfer assets to a non-arm's-length party at FMV to trigger
terminal loss on the class. However:
- s.13(21.2): stop-loss rules apply to affiliated persons (spouse, corporation you control)
- The loss may be denied and added to the transferee's UCC
- Works cleanly with unrelated arm's-length buyers

**Best clean trigger:** Sell assets on the open market (arm's length) and wind down the class.

---

## 8. CHANGE OF USE RULES

### Personal to Business Conversion

When property changes from **personal use to business use**, there is a **deemed acquisition at FMV**
on the date of change.

**Authority:** ITA s.13(7)(b)

**Example:** CC uses personal laptop for business starting 2024:
- FMV at conversion date = $800
- This $800 becomes the **capital cost** for CCA purposes (Class 50, 55%)
- CCA claimed on $800, not original purchase price

**Critical:** The deemed acquisition at FMV cannot exceed the **original cost**. If the asset
has declined in value, the capital cost for CCA is the lower FMV.

### Business to Personal Conversion

When property moves from **business to personal use**, there is a **deemed disposition at FMV**.

**Authority:** ITA s.13(7)(a)

This triggers:
1. A reduction in UCC by the lower of FMV or original cost
2. Potential recapture if UCC goes negative
3. Potential capital gain if FMV exceeds original cost
4. Potential capital loss (only 50% deductible) if FMV < original cost

**Warning for home offices:** If you claim CCA on the home and later convert fully back to personal
use, this triggers a deemed disposition at FMV on the business portion — and eliminates the PRE for
that portion for all years CCA was claimed.

### Partial Change of Use

When an asset moves from 100% business to, say, 70% business:
- Proportional deemed disposition for the 30% that moved to personal use
- UCC adjusted accordingly
- Most common with automobiles and home offices

### IT-Bulletin Reference

**IT-285R2 — Capital Cost Allowance — General Comments**
- Paragraph 8: change of use rules summary
- Paragraph 14: partial changes of use

---

## 9. COMPLETE CCA CLASS REFERENCE TABLE

| Class | Rate | Method | Key Assets | AII Eligible | Immediate Exp. |
|-------|------|--------|-----------|-------------|----------------|
| 1 | 4% | DB | Buildings (post-1987) | Yes | No |
| 1(q) | 6% | DB | Non-residential buildings (90%+ non-res) | Yes | No |
| 1(k) | 10% | DB | M&P buildings | Yes | No |
| 3 | 5% | DB | Buildings (pre-1988) | No | No |
| 6 | 10% | DB | Frame/log buildings, fences, greenhouses | Yes | No |
| 7 | 15% | DB | Canoes, boats, vessels | Yes | No |
| 8 | 20% | DB | Office furniture, tools >$500, appliances | Yes | Yes |
| 10 | 30% | DB | Vehicles (under limit), old computers | Yes | Yes |
| 10.1 | 30% | DB | Passenger vehicles (over $37K limit) | Yes | Yes |
| 12 | 100% | DB | Small tools <$500, software, cutlery | Yes | Yes |
| 13 | SL | SL | Leasehold improvements | No | No |
| 14 | SL | SL | Limited-life patents/franchises/licences | No | No |
| 14.1 | 5% | DB | Goodwill, trademarks, unlimited intangibles | Yes | No |
| 16 | 40% | DB | Taxis, coin-operated games, rental autos | Yes | Yes |
| 17 | 8% | DB | Roads, parking lots, runways | Yes | No |
| 29 | 50% SL | SL | Historical M&P equipment (2007–2015) | No | No |
| 43 | 30% | DB | M&P equipment (post-2015) | Yes | Yes |
| 43.1 | 30% | DB | Clean energy generation equipment | Yes | Yes |
| 43.2 | 50% | DB | Enhanced clean energy equipment | Yes | Yes |
| 44 | 25% | DB | Patents (post April 26, 1993) | Yes | Yes |
| 45 | 45% | DB | Computers (Mar 2004 – Dec 2004) | No | No |
| 46 | 30% | DB | Data network infrastructure | Yes | Yes |
| 50 | 55% | DB | Computers and systems software (post-2009) | Yes | Yes |
| 52 | 100% | DB | Computers (Jan 2009 – Feb 2011) CCPC only | No | No |
| 53 | 50% | DB | M&P equipment (2016–2025) | Yes | Yes |
| 54 | 30% | DB | Zero-emission passenger vehicles ($61K limit) | Full write-off | Yes |
| 55 | 40% | DB | Zero-emission commercial vehicles | Full write-off | Yes |
| 56 | 30% | DB | Zero-emission automotive equipment (post Mar 2020) | Full write-off | Yes |

**DB = Declining Balance | SL = Straight-Line**

---

## 10. CLASS-BY-CLASS DEEP DIVE

### Class 1 — Buildings (4%)

**Authority:** Schedule II, Class 1; Reg. 1100(1)(a)(i); IT-79R3

**Assets included:**
- Buildings or other structures acquired after 1987 (frame, brick, concrete, steel)
- Components permanently attached: wiring, plumbing, HVAC (unless separate class applies)
- Parking areas paved as part of the building property

**Subclasses:**
| Subclass | Rate | Condition |
|----------|------|-----------|
| 1(q) | 6% | Non-residential building where 90%+ of floor space is non-residential use, acquired after March 18, 2007 |
| 1(k) | 10% | Buildings acquired after March 18, 2007 used 90%+ for M&P in Canada |

**Separate class election — s.1101(1ac):**
- Available for each **rental** building that costs **$50,000 or more**
- Strongly recommended: allows terminal loss on each building individually
- Without this election: all buildings pool together, terminal loss on one is offset by gains on others

**Strategies:**
1. Always make the separate class election for rental buildings
2. Use Class 1 for the shell; elect separate classes for capital improvements if eligible
3. For non-residential income property: Class 1(q) at 6% vs Class 1 at 4% — significant over time
4. Building improvements after original construction: usually Class 3 or Class 1 depending on date

**IT-79R3 Reference:** Archived but foundational — defines what constitutes a "building" for CCA purposes. Distinction between building components (Class 1) and separate equipment components (Class 8, Class 43).

---

### Class 3 — Pre-1988 Buildings (5%)

Buildings or other structures acquired **before 1988**. Grandfathered at 5% declining balance.
New acquisitions in 2024+ cannot enter Class 3. Relevant only for inherited/purchased older properties
where the original owner acquired before 1988 and the cost base transfers.

---

### Class 6 — Frame Buildings and Fences (10%)

**Assets:**
- Buildings or structures of **frame, log, stucco on frame, galvanized iron, or corrugated metal** construction
- Must have **no footings or other base below ground level** (or in permafrost)
- Fences, greenhouses, wooden wharves/docks
- Tents and awnings

**When it matters:** Farm structures, garage buildings, storage sheds on commercial property.
Frame construction storage building for a tech company would be Class 6 (10%), not Class 1 (4%).
Saves meaningful tax on commercial storage/workshop buildings.

---

### Class 7 — Vessels (15%)

**Assets:** Canoes, boats, vessels, motor vessels. Also includes furniture and fittings built into vessels.
Relevant for fishing businesses, marine transport, tourism operators.

---

### Class 8 — Miscellaneous Tangible Property (20%)

**Authority:** IT-285R2 — "catch-all" class

**Assets (anything not specifically listed elsewhere):**
- Office furniture (desks, chairs, filing cabinets, bookshelves)
- Office equipment (except computers): photocopiers, fax machines, shredders
- Tools and implements costing **over $500**
- Outdoor advertising signs and displays
- Refrigerators, freezers, dishwashers (business use)
- Machinery and equipment not in Classes 43, 43.1, 43.2, 53
- Medical and dental equipment
- Portable storage containers
- Theatrical costumes, props
- Lamps, shades, blinds — if not attached to building

**Class 8 is the default:** If an asset doesn't fit a more specific class, it goes in Class 8.

**AII + Immediate Expensing:** Both fully available. With immediate expensing, 100% write-off in
year 1 vs 30% (AII first year) or 20% (normal declining balance).

---

### Class 10 — Motor Vehicles (30%)

**Assets:**
- **All motor vehicles** not described elsewhere (trucks, vans, SUVs, motorcycles)
- Passenger vehicles **at or below** the prescribed cost limit ($37,000 for 2024 before tax)
- **General-purpose electronic data processing equipment** acquired before January 1, 2009
- Trailers, semi-trailers

**Key distinction from Class 10.1:**
- Class 10: no per-vehicle limit on cost base
- Class 10.1: mandatory for passenger vehicles exceeding $37,000 (2024 limit)

**Terminal loss available** (unlike Class 10.1)

---

### Class 10.1 — Luxury Passenger Vehicles (30%)

**Authority:** ITA s.13(2); Reg. 7307(1); IT-521R (Motor Vehicle Expenses)

**Mandatory classification:** When a passenger vehicle's cost exceeds the prescribed limit, it **must**
go in Class 10.1. This is not optional.

**2024 prescribed limit:** $37,000 (before HST/PST) = $41,810 including Ontario HST

**Rules unique to Class 10.1:**
1. **Separate class per vehicle** — each vehicle has its own UCC pool (no pooling)
2. **CCA base capped at $37,000** (not your actual purchase price)
3. **Terminal loss NOT allowed** on disposition — s.13(2)
4. **Recapture NOT required** on disposition — s.13(2)
5. **50% CCA allowed in year of acquisition AND year of disposition** — not zero in year of disposal
6. **Interest deduction capped** at $10/day ($300/month) — s.67.2

**Why "no terminal loss" is a trap:**
You buy a $55,000 vehicle. CCA base: $37,000. After 5 years, UCC = ~$11,000. You sell for $8,000.
Normally: terminal loss = $11,000 - $8,000 = $3,000 deduction. Under Class 10.1: **zero**. The
$3,000 UCC just disappears. You get no deduction for it.

**Planning implication:** For vehicles over the limit, consider leasing — full lease payment is
deductible (subject to s.67.3 limit of $950/month for 2024), avoiding the Class 10.1 trap.

---

### Class 12 — 100% Write-Off Assets

**Authority:** Schedule II, Class 12; IT-285R2 paragraphs 9-11

**Assets (100% CCA, subject to half-year rule for pre-AII property):**
- **Small tools and instruments:** Cost less than $500 per item
  - Hammers, screwdrivers, wrenches, power tools (if < $500)
- **Medical and dental instruments:** Cost less than $500
- **Kitchen utensils and cutlery:** Restaurants, hotels
- **Uniforms and costumes:** Used in business, not for warmth
- **Linen:** Bed sheets, tablecloths, towels (hospitality)
- **Videotapes and videocassettes:** (archaic but still in the class)
- **Computer application software:** Word processing, accounting software, Adobe, etc.
- **Chinaware and glassware:** Restaurants

**AII applies:** With AII in place, 100% × 1.5 = still 100% (can't exceed 100%). So Class 12
assets are always 100% in year 1, AII or not.

**Critical distinction — Software:**
| Type | Class | Rate |
|------|-------|------|
| Application software (Word, Excel, QuickBooks, Adobe) | 12 | 100% |
| Systems software (Windows OS, macOS, Linux, iOS) | 50 | 55% |
| SaaS subscription (Notion, Slack, Xero) | N/A — operating expense | 100% deductible |
| Custom software developed for business | 12 (if < $500) or 14.1 or 50 | Depends |

**For CC:** All software tools (Claude API, coding tools, accounting software) should be analyzed:
- SaaS subscriptions = operating expense (fully deductible in year incurred)
- Perpetual software licenses = Class 12 (100%)
- Hardware (MacBook, servers) = Class 50 (55%) or immediate expensing

---

### Class 13 — Leasehold Improvements (Straight-Line)

**Authority:** Schedule II, Class 13; IT-464R

**Assets:** Improvements made by a **lessee** (tenant) to leased property. The lessee does not own
the building but has made improvements that revert to the landlord.

**Examples:** Office renovations, custom partitions, built-in shelving, flooring upgrades,
specialized electrical wiring, tenant fit-out costs.

**CCA Rate Formula (Straight-Line):**
```
Annual CCA = Capital cost ÷ Amortization period

Amortization period = Lease term remaining + first renewal option period
Subject to:
  - Minimum: 5 years
  - Maximum: 40 years
```

**Example:**
- Office lease remaining: 3 years, with one 2-year renewal option
- Amortization period: 3 + 2 = 5 years (at minimum)
- Improvement cost: $30,000
- Annual CCA: $30,000 ÷ 5 = $6,000/year

**Multiple improvements in same class:** Each improvement calculates its own amortization period,
then the pool is managed accordingly. In practice, use Schedule for Class 13 to track each
improvement separately.

**IT-464R Reference:** Capital Cost Allowance — Leasehold Interests — covers sublease payments,
assignment of leases, early termination consequences.

---

### Class 14 — Limited-Life Intangibles (Straight-Line)

**Assets:** Patents, franchises, licences, or limited-life rights with a **fixed term** — known
end date at time of acquisition.

**Rate:** 100% ÷ legal life in years (straight-line over the life)

**Examples:**
| Asset | Life | Annual CCA |
|-------|------|-----------|
| 20-year patent | 20 years | 5%/year |
| 10-year franchise | 10 years | 10%/year |
| 5-year software licence | 5 years | 20%/year |
| 15-year government licence | 15 years | 6.67%/year |

**Distinction from Class 14.1:** If the intangible has **unlimited or indefinite** life → Class 14.1 (5%)
If the intangible has a **fixed, known term** → Class 14 (straight-line over that term)

**Disposition:** On sale, recapture or terminal loss applies based on remaining UCC vs proceeds.

---

### Class 14.1 — Goodwill and Unlimited-Life Intangibles (5%)

**Authority:** ITA s.13(34)–(42); transitional rules from 2017 budget; CPA Canada guidance

**Assets:**
- **Goodwill** (business reputation, going-concern value)
- **Trademarks** (unlimited registration periods)
- **Customer lists and relationships**
- **Non-compete agreements** with no fixed end date
- **Government licences** with unlimited or indefinitely renewable terms
- **Franchise rights** with renewable/perpetual terms

**Background — ECP system replaced in 2017:**
Before 2017, these were "eligible capital property" (ECP) with a three-quarters inclusion rule.
Budget 2016 abolished ECP effective January 1, 2017, replacing it with Class 14.1.

**Key rules:**
1. **5% declining balance** — very slow write-off
2. **No half-year rule originally**, but AII applies with 1.5× factor for qualifying acquisitions
3. **On disposition:** If proceeds exceed cost → s.14 capital gain rules (75% included — see below)
4. **Transitional balance:** Pre-2017 ECP converted to Class 14.1 at 4/3 of CECB (Cumulative
   Eligible Capital Balance) — grandfathered separately

**Disposition rules — the 75% trap:**
When you sell a Class 14.1 asset (or a business with goodwill):
- **Proceeds up to cost:** reduces UCC, potential recapture
- **Proceeds above cost:** 75% is included in income (as s.14(1) income), not capital gain
- This is more onerous than regular capital gains (50% inclusion) — plan accordingly

**Planning for business sale:**
- Try to allocate more purchase price to depreciable equipment (Class 8, 50) and less to goodwill
- Equipment: recapture (100%) + capital gain (50%) depending on FMV vs cost
- Goodwill: 75% inclusion on amounts above original cost
- Sometimes goodwill allocation is unavoidable when buying an ongoing business

---

### Class 16 — Taxis and Coin-Operated Games (40%)

**Assets:**
- Taxis licensed to carry passengers for hire
- Coin-operated video games or games equipment
- Rental automobiles (used in the business of renting automobiles)

**40% declining balance** — faster write-off than Class 10/10.1 for qualifying vehicles.

---

### Class 17 — Roads and Parking Lots (8%)

**Assets:**
- Roads, streets, sidewalks, airplane runways
- Parking areas, storage areas (surface)
- Similar paved or graded surfaces

**Does NOT include:** Buildings on paved lots (those are Class 1).
**Does NOT include:** Underground parking structures (those are Class 1 — building).

---

### Class 43 — Manufacturing and Processing Equipment (30%)

**Authority:** Regulation 1104(9); IT-285R2

**Assets (acquired after 2015):** Machinery and equipment used primarily for manufacturing or
processing in Canada. Replaces Class 29 (50% straight-line) for post-2015 acquisitions.

**30% declining balance** with full AII available.

**What counts as M&P:** CRA defines manufacturing as the mechanical transformation of materials
into finished products. Processing includes procedures applied to raw materials to change their
form or character. For an AI/SaaS company: server hardware used in ML training would not qualify
for Class 43 (not M&P). Server farms for a product company: potentially Class 50 or 46.

---

### Class 43.1 and 43.2 — Clean Energy Equipment

**Class 43.1 (30%):** Clean energy generation equipment acquired on or after February 22, 2005
- Solar panels, wind turbines, small hydroelectric equipment
- Ground source heat pumps (geothermal)
- Biomass-fueled equipment
- Cogeneration systems

**Class 43.2 (50%):** Enhanced version of 43.1 — same equipment at higher rate

**Authority:** Regulation 1104(17) defines eligible clean energy property in exhaustive detail

**Investment Tax Credit (ITC) stacking:** Some Class 43.1/43.2 equipment also qualifies for
the Clean Technology ITC (30% refundable for CCPCs under Budget 2023). CCA + ITC = extremely
attractive. The ITC reduces capital cost by the amount received, reducing future CCA base.

---

### Class 44 — Patents (25%)

**Assets:** Patents acquired after April 26, 1993.

**Note vs Class 14:** Class 44 gives 25% declining balance. Class 14 gives straight-line over
the patent's remaining life. Choose the class that gives better deductions:
- Short-remaining-life patents (e.g., 5 years left): Class 14 (20%/year) beats Class 44 (25% DB)
  in total deductions and timing
- Long-remaining-life patents (e.g., 15+ years): Class 44 (25% DB) may give larger early deductions

**Election available:** Taxpayer can elect under Reg. 1103(2h) to include a patent in Class 14
instead of Class 44 on a per-patent basis.

---

### Class 46 — Data Network Infrastructure (30%)

**Assets:** Equipment that is used primarily for the purpose of gaining or producing income from
a **network data communication** service — routers, switches, hubs, modems, network access points,
fiber optic cables used in data infrastructure.

**For CC's context:** Data center networking equipment, server interconnects, networking equipment
for OASIS AI Solutions would fall here. **Not** personal computers (those are Class 50).

---

### Class 50 — Computers and Systems Software (55%)

**Authority:** Schedule II, Class 50; supersedes Class 45

**Assets (acquired after January 27, 2009):**
- General-purpose electronic data processing equipment (computers, servers, tablets)
- Systems software (operating systems, firmware)
- Peripheral computer equipment (monitors, keyboards, mice, printers connected to computers)
- Network servers

**55% declining balance — the highest rate for any computer equipment class.**

**AII first-year:** 55% × 1.5 = 82.5% in year 1 (before AII phaseout)
**With immediate expensing:** 100% in year 1 (for CCPCs and individuals up to $1.5M)

**For CC (as OASIS AI Solutions):** All computer hardware, MacBook, development servers, external
drives, monitors — Class 50. With immediate expensing, every dollar of computer equipment is
deductible in full in the year of purchase.

---

### Class 52 — CCPC Computers 2009–2011 (100%)

**Historical class** — 100% CCA for computers acquired by CCPCs between January 28, 2009 and
February 1, 2011. Stimulus measure during 2008-09 recession. No new acquisitions qualify.
Only relevant if a business still has assets from that era on the books.

---

### Class 53 — Manufacturing/Processing Equipment 2016–2025 (50%)

**Assets:** M&P equipment acquired after 2015 and before 2026. Transitional class between Class 29
(50% straight-line) and Class 43 (30% declining balance).

**50% declining balance** — faster write-off than Class 43. With AII, first-year = 75%.

---

### Class 54 — Zero-Emission Passenger Vehicles (30%)

**Authority:** ITA s.13(2.1); Budget 2019

**Assets:** Zero-emission passenger vehicles (electric, fuel cell, plug-in hybrid with 7+ kWh battery)
acquired after March 18, 2019.

**2024 cost limit:** $61,000 (before HST) — separate limit from Class 10.1's $37,000

**Special first-year write-off:**
- No half-year rule: full CCA in year of acquisition
- For CCPCs with immediate expensing: 100% of $61,000 cap in year 1
- Without immediate expensing: 30% DB with no AII half-year rule restriction (effectively 30% on cost)

**Terminal loss:** Unlike Class 10.1, Class 54 **DOES allow terminal loss** on disposition

**Example (2024, CC buys Tesla Model 3 for $58,000):**
- Eligible cost: $58,000 (under $61,000 limit)
- Business use: 80%
- Immediate expensing: $58,000 × 100% = $58,000 deduction
- Business portion: $46,400
- Tax saving at 46.16%: $21,419 in year 1

---

### Class 55 — Zero-Emission Commercial Vehicles (40%)

**Assets:** Zero-emission vehicles acquired after March 18, 2019 that are used to transport
goods or people for hire (commercial use) and are **not** passenger vehicles under Class 54.

**No cost limit** (unlike Class 54's $61,000 cap). Full first-year write-off available.

---

### Class 56 — Zero-Emission Automotive Equipment (30%)

**Assets:** Zero-emission automotive equipment acquired after March 1, 2020 that is not a
motor vehicle — electric forklifts, electric industrial equipment, electric ground support equipment.

---

## 11. CCA CALCULATION WORKSHEETS

### Worksheet 1: Standard UCC Schedule

```
YEAR: ______ | CLASS: ______ | RATE: ______%

Line 1:  Opening UCC (prior year closing UCC)           $__________
Line 2:  Capital cost of NEW acquisitions               $__________
Line 3:  Subtotal (Line 1 + Line 2)                     $__________
Line 4:  Proceeds of disposition (LESSER of:
           actual proceeds OR original cost)             $__________
Line 5:  Net UCC before CCA (Line 3 - Line 4)           $__________
Line 6:  AII/Immediate expensing adjustment (if any)    $__________
Line 7:  Maximum CCA (Line 5 × rate %)                  $__________
Line 8:  CCA CLAIMED (your choice: $0 to Line 7)        $__________
Line 9:  Closing UCC (Line 5 - Line 8)                  $__________

RECAPTURE: If Line 5 is NEGATIVE → $(Line 5) included in income
TERMINAL LOSS: If Line 5 is POSITIVE and NO PROPERTY in class → Line 5 deductible
```

### Worksheet 2: AII First-Year Calculation

```
For property acquired after Nov 20, 2018 (pre-phaseout):

Step 1: Capital cost of new property:                   $__________
Step 2: Half-year amount (× 50%):                       $__________
Step 3: AII first-year amount (Step 2 × 3):             $__________
        = Step 1 × rate × 1.5

Example: $50,000 Class 8 equipment
  Half-year normal: $50,000 × 20% × 0.5 = $5,000
  AII first year:   $50,000 × 20% × 1.5 = $15,000
  Improvement:      $10,000 more in year 1
```

### Worksheet 3: Immediate Expensing (CCPC/Individual to $1.5M)

```
Step 1:  Total eligible property acquired              $__________
Step 2:  Limit: $1,500,000
Step 3:  Immediate expensing claimed (min of 1, 2):    $__________
Step 4:  Remaining cost above $1.5M limit              $__________
Step 5:  AII applies to Step 4 amount (if any)

Priority of allocation:
  Lowest-rate classes first (maximizes incremental benefit)
  Class 1 (4%) → INELIGIBLE, use AII
  Class 8 (20%) → ELIGIBLE, allocate here
  Class 50 (55%) → ELIGIBLE, but AII already = 82.5%, lower incremental
  Class 12 (100%) → ELIGIBLE but already 100% — no benefit
```

### Worksheet 4: Vehicle CCA (Full Example)

**Scenario:** 2024, CC purchases vehicle for $45,000 + HST ($5,085) = $50,850 total
Business use: 70%

**Step 1: Classify the vehicle**
- Is it a passenger vehicle? Yes
- Does the cost ($45,000) exceed the 2024 limit ($37,000)? Yes
- → **Class 10.1 is mandatory**

**Step 2: Determine CCA base (capped at $37,000)**
```
Prescribed limit (2024):           $37,000
HST on $37,000 (13%):              + $4,810
CCA base (capital cost):           $41,810
```

**Step 3: First-year CCA (AII 2024 — 0.75× factor)**
```
AII factor for 2024-2025: 0.75×
Normal half-year: $41,810 × 30% × 0.5 = $6,272
AII-enhanced:     $41,810 × 30% × (0.5 + 0.5 × 0.75)
                = $41,810 × 30% × 0.875 = $10,973
```
Wait — let me clarify: under the phaseout, the AII enhancement factor is being reduced.
For 2024-2025, the enhancement (above the 0.5 half-year base) is reduced by 25%.
In practice, CRA's calculation uses:

```
Full AII (pre-2024): 1.5× → $41,810 × 30% × 1.5 = $18,815
2024-2025 rate:      1.0× → $41,810 × 30% × 1.0 = $12,543
(half-year base 0.5, no enhancement in 2024-2025)

Business portion: $12,543 × 70% = $8,780
```

**Step 4: Year 2 CCA**
```
Opening UCC Year 2: $41,810 - $12,543 = $29,267
CCA Year 2: $29,267 × 30% = $8,780
Business portion: $8,780 × 70% = $6,146
```

**Step 5: Cumulative write-off schedule (business portion)**
| Year | CCA Claimed | Business Deduction | Running UCC |
|------|------------|-------------------|-------------|
| 1 | $12,543 | $8,780 | $29,267 |
| 2 | $8,780 | $6,146 | $20,487 |
| 3 | $6,146 | $4,302 | $14,341 |
| 4 | $4,302 | $3,011 | $10,038 |
| 5 | $3,011 | $2,108 | $7,027 |
| 6 | $2,108 | $1,476 | $4,919 |

**Step 6: Disposition (sell for $12,000 at Year 6)**
- UCC: $4,919
- Proceeds: $12,000, capped at original cost $41,810 → use $12,000
- UCC after disposition: $4,919 - $12,000 = -$7,081
- But Class 10.1 rules: **no recapture, no terminal loss**
- The negative UCC simply disappears. No tax consequence on disposition.

### Worksheet 5: Leasehold Improvement (Class 13)

```
Scenario: Tenant builds $25,000 renovation
Lease terms: 2 years remaining, one 2-year renewal option, one 1-year renewal option

Step 1: Amortization period
  Remaining term:            2 years
  First renewal option:     + 2 years
  Total:                     4 years
  Subject to minimum of 5 years → use 5 years

Step 2: Annual CCA = $25,000 ÷ 5 = $5,000/year

Note: In year of acquisition, HALF the annual amount applies
  Year 1: $5,000 × 50% = $2,500 (half-year rule applies to Class 13)
  Year 2 through 5: $5,000/year
  Year 6: remaining $2,500

Step 3: If lease terminates early at Year 3 (after claiming $12,500)
  UCC = $25,000 - $12,500 = $12,500
  All assets in class disposed
  Terminal loss = $12,500 (deductible against income)
```

---

## 12. ADVANCED CCA STRATEGIES

### Strategy 1 — CCA Income Smoothing

**The principle:** CCA is optional. Claim more in high-income years, less in low-income years.

**Why it matters:**
- Ontario top marginal rate: 46.16% (above $220,000)
- Ontario basic rate: 20.05% (below $51,446)
- Value of $1,000 CCA at top rate: $461.60 saved
- Value of $1,000 CCA at basic rate: $200.50 saved
- **Difference: $261.10 per $1,000 of CCA timing**

**Implementation:**
1. Track UCC pools annually
2. In years with high income (above $100K): claim maximum CCA
3. In years with low income (RRSP deduction year, business losses, parental leave): reduce CCA claim
4. Use the UCC pool as a "tax timing reserve" — deploy when marginal rate is highest

**Interaction with installments:** Claiming more CCA reduces net income, which affects the
prior-year method installment base. Plan CCA claims in conjunction with installment strategy
(see ATLAS_INSTALLMENT_PAYMENTS.md).

### Strategy 2 — Separate Class Election to Create Terminal Loss

**The problem:** You have a Class 8 pool with multiple assets. One asset (worth $1,000) has been
fully depreciated on your books but is physically worthless. You want to write it off but can't
easily separate it from the pool.

**The solution:** For rental buildings specifically, use the separate class election under
s.1101(1ac). For other assets, the strategy works at the point of full disposition.

**Step-by-step:**
1. Identify assets in a class where individual items are nearly worthless
2. Dispose of them (even at $1) to arm's-length party
3. If this clears **all** assets from the class and UCC > $0 → terminal loss
4. If class still has assets: no terminal loss yet, but the disposed asset's proceeds
   ($1) reduce UCC marginally

**The affiliate stop-loss warning:** s.13(21.2) — if you transfer depreciable property to an
affiliated person (spouse, controlled corporation), the terminal loss may be denied and added
to the transferee's UCC. Only works cleanly with arm's-length dispositions.

### Strategy 3 — Purchase Timing for Maximum First-Year Deduction

**Rule:** CCA only applies to property **available for use** in the taxation year.

**Strategy:** Buy and deploy business assets **before** your fiscal year-end to claim first-year
CCA (even just AII/half-year, which is still 15–82.5% depending on class).

**For CC (December 31 personal tax year):**
- Buy computer equipment (Class 50) on December 15 → claim 82.5% (AII pre-2024) or 100%
  (immediate expensing) in that tax year
- Buy office furniture (Class 8) on December 20 → claim 30% (AII) or 100% (immediate expensing)
- **Do not buy on January 2** — you lose an entire year of CCA

**Year-end acquisition checklist:**
- [ ] Is the asset available for use before December 31?
- [ ] Do you have delivery confirmation/receipt?
- [ ] Is the business purpose documented?
- [ ] Does the acquisition fit within the $1.5M immediate expensing limit?

### Strategy 4 — CCA and RRSP Coordination

**The problem:** RRSP contributions reduce taxable income. But so does CCA. Stack both in the
same year and you may push yourself into a much lower bracket — wasting the RRSP deduction.

**Solution:** Sequence carefully.
1. Estimate income before CCA and RRSP
2. Determine optimal bracket (e.g., keep income at $100,000 for Ontario — stays in combined 43.41%)
3. Claim RRSP first (hard deadline — 60 days after year-end)
4. Then determine how much CCA to claim to bring income to the optimal level
5. Never claim CCA that pushes you below the bracket where RRSP deductions would also be wasted

### Strategy 5 — SR&ED and CCA Interaction

**The problem:** When you claim SR&ED tax credits (ITCs), the ITC reduces the capital cost of
the qualifying property. This reduces your CCA base.

**Authority:** ITA s.127(11.1), (12)

**Example:**
- CC buys $100,000 of SR&ED equipment (Class 50)
- SR&ED ITC at 35% (CCPC rate): $35,000 refundable credit
- Reduced capital cost for CCA: $100,000 - $35,000 = $65,000
- CCA (55% Class 50) applied to $65,000, not $100,000

**Net result:** You get $35,000 cash back AND CCA on the remaining $65,000.
This is still better than just CCA on $100,000 without SR&ED.

**Important:** The ITC reduction happens in the year following the ITC claim (or year it's received).
So year-1 CCA may be on full $100,000; year-2 UCC is reduced by $35,000.

### Strategy 6 — Class 14.1 Sale vs Asset Sale Planning

**When selling OASIS AI Solutions (or any business):**

**Option A — Sell shares:** No CCA recapture, no terminal loss. Capital gains at 50% inclusion.
LCGE potentially available ($1.25M lifetime capital gains exemption if CCPC qualifies as QSBC).

**Option B — Sell assets:** Each asset class triggers recapture/terminal loss/capital gain:
- Computers (Class 50): likely full recapture if selling for more than UCC
- Goodwill (Class 14.1): 75% income inclusion on gains above cost
- Equipment (Class 8): recapture (100%) + capital gain (50%) split

**General rule:** Asset sales favor the buyer (step up in cost base, fresh CCA).
Share sales favor the seller (capital gains treatment, LCGE eligibility).

**Purchase price allocation strategy:**
If forced into asset sale, allocate to:
1. Assets with terminal loss (get deductions)
2. Capital property with capital gain (50% inclusion)
3. Goodwill/14.1 last (75% inclusion = most expensive)

---

## 13. AUTOMOBILE CCA OPTIMIZATION

### The $37,000 Decision Tree

```
Is it a passenger vehicle?
├── NO → Class 10 (30%), no limit, no restrictions
└── YES
    ├── Cost ≤ $37,000 (before tax)?
    │   └── Class 10 (30%), no per-vehicle limit
    └── Cost > $37,000 (before tax)?
        └── Class 10.1 (30%), mandatory
            ├── CCA base capped at $37,000 + tax
            ├── No terminal loss on disposal
            ├── No recapture on disposal
            └── Separate class per vehicle
```

**"Passenger vehicle" definition (ITA s.248(1)):**
A motor vehicle designed or adapted primarily to carry individuals on highways and streets,
with seating capacity for not more than the driver + 8 passengers. **Excludes:**
- Ambulances
- Clearly marked emergency response vehicles
- Vehicles used primarily to transport goods (pickup trucks used 90%+ for goods)
- Taxis, hearses

**Key escape from Class 10.1 — the pickup truck rule:**
A pickup truck used **more than 50% of the time for transporting goods, equipment, or passengers
in the course of earning income** and not designed primarily as a passenger vehicle → Class 10
(no cost limit).

### Interest Deduction Cap — s.67.2

For Class 10.1 (and any vehicle subject to the prescribed limit):
- Maximum interest deduction: **$10/day** ($300/month, ~$3,600/year)
- Interest paid above this level: not deductible
- This applies regardless of the actual loan rate

**Example:** $55,000 vehicle, $45,000 loan at 6% = $2,700/year interest
- Deduction allowed: $3,600/year
- So full interest is deductible in this case (loan is small enough)

For a $75,000 vehicle loan at 6% = $4,500/year interest:
- Deduction allowed: $3,600/year
- $900/year is non-deductible

### Lease vs Buy for Expensive Vehicles — s.67.3

**Lease payment deduction cap:**
- Monthly limit: **$950/month** (2024) × business-use%
- Annual limit: ~$11,400

**Example:** $55,000 vehicle, lease at $1,100/month, 70% business use
- Monthly lease: $1,100
- Monthly cap: $950
- Business portion of cap: $950 × 70% = $665/month deductible
- Vs Class 10.1 CCA: complex — but generally leasing gives more flexibility

**Lease vs Buy quick comparison:**

| Factor | Lease | Buy (Class 10.1) |
|--------|-------|-----------------|
| Monthly deduction | Up to $950 × biz% | CCA on $41,810 × biz% |
| Year 1 deduction | Full payment × biz% | AII: $41,810 × 30% × 1.0 × biz% = $12,543 × biz% |
| Terminal value | Walk away | Recapture risk or UCC disappears |
| Flexibility | Swap every 3-5yr | Own it |
| CRA risk | Must be true lease | Must track business use |

### Business Use Percentage Documentation

**CRA requirement (IT-521R — Motor Vehicle Expenses):**
- Maintain a **mileage log** (paper or app)
- Record: date, starting/ending odometer, destination, business purpose
- Calculate: business km ÷ total km = business use %
- Log must cover the **full tax year** (or full representative period with CRA approval)

**CRA audit trigger:** Vehicle expense claims without mileage log are easily denied.
Apps: MileIQ, Driversnote, TripLog — all CRA-acceptable. Auto-tracking enabled on phone.

**If you forget to track:** Reconstruct from calendar, email records, client invoices.
Not perfect but defensible if documented.

### Zero-Emission Vehicle Strategy (Class 54)

For CC, if planning a vehicle acquisition:
- **EV under $61,000:** Class 54, 100% immediate expensing (individual + CCPC)
- **vs gas vehicle over $37,000:** Class 10.1, $41,810 cap, no terminal loss

**Financial comparison (80% business use):**
| Vehicle | Cost | Class | Year 1 Deduction | Tax Saving (46.16%) |
|---------|------|-------|-----------------|---------------------|
| Gas SUV $50,000 | $41,810 cap | 10.1 | $12,543 | $5,790 |
| Tesla Model 3 $55,000 | $55,000 | 54 | $55,000 | $25,388 |
| **Difference** | | | $42,457 more | **$19,598 more** |

The EV saves nearly $20,000 more in taxes in year 1 — before government EV rebates.

---

## 14. RENTAL PROPERTY CCA — THE RESTRICTION NOBODY KNOWS

### The s.1100(11) Restriction

**The rule:** CCA on rental property **cannot be used to create or increase a net rental loss**.
CCA can only reduce rental income to zero — you cannot use it to generate a loss that offsets
other income (employment, business, interest).

**Authority:** Reg. 1100(11)

**Example:**
```
Rental income:           $18,000
Rental expenses
  (mortgage interest,
   property tax, repairs):  -$15,000
Net rental income before CCA: $3,000

CCA on rental building
(Class 1, 4%, $300,000 cost):   Maximum $12,000

CCA you can CLAIM:        MAX $3,000 (can only reduce to zero, not below)
CCA you CANNOT CLAIM:    $9,000 (restricted — cannot create rental loss)
```

**The restricted $9,000** doesn't disappear — it's not claimed now but the UCC pool carries
forward. You claim it in future years when rental income is higher.

### Exception — Principally Rental Corporations

**s.1100(12) exception:** The restriction does NOT apply to:
- **Corporations** whose **principal business** is renting or leasing real property
- REITs and real estate holding companies

**Planning implication:** A sole proprietor with a rental property is restricted.
If CC incorporates a HoldCo that solely holds rental properties and earns rental income as its
principal business, the restriction doesn't apply and CCA can create rental losses.

This is a significant reason to incorporate rental holdings separately from the operating company
(OASIS).

### Separate Class Election — s.1101(1ac)

**Strongly recommended for every rental building costing $50,000 or more.**

**Without separate class election:**
All rental buildings pool in one Class 1 UCC account. When one building is sold:
- All proceeds reduce the single UCC pool
- If the pool goes negative → recapture on all buildings
- Terminal loss on one building offsets gains on another

**With separate class election:**
Each building has its own UCC account. On disposal:
- That building's UCC stands alone
- Terminal loss on one building is fully deductible
- Other buildings unaffected

**Election process:** File with T776 rental income return for the year the building is acquired.
File CRA Form T2091/T1255 is not for this — the election is simply made on the return by
placing the building in its own CCA schedule with the notation "s.1101(1ac) election."

---

## 15. HOME OFFICE CCA — THE PRE TRAP

### The Principal Residence Exemption (PRE) Problem

**Critical warning — read this before claiming CCA on your home.**

The Principal Residence Exemption (PRE) under ITA s.40(2)(b) allows you to eliminate capital gains
on your home when you sell. This is worth **tens of thousands to hundreds of thousands of dollars**
tax-free on a typical Canadian home sale.

**The trap:** If you claim CCA on the **home itself** (as a business asset) for your home office,
CRA treats the home office portion as having changed use from personal to business:
- The home office portion is no longer "ordinarily inhabited" as principal residence
- The PRE cannot apply to that portion for the years CCA was claimed
- On sale: a proportional capital gain becomes taxable

**Example:**
- CC owns home worth $600,000 (purchased at $350,000) — potential gain = $250,000
- Home office = 15% of home
- If CCA claimed for 5 years: 15% × $250,000 × 50% inclusion = $18,750 taxable gain
- Tax at 46.16%: **$8,655 in tax** — plus recapture on any CCA claimed

**The smarter approach:** Claim operating expenses for the home office but **never claim CCA**.

### What You CAN Claim (Without PRE Risk)

**Allowable home office operating expenses (T2125 Part 7):**

| Expense | Deductible? |
|---------|------------|
| Heat, hydro, water | Yes — proportionate to office |
| Internet | Yes — business portion |
| Rent (if renting) | Yes — proportionate |
| Mortgage interest | NOT directly — but "rent equivalent" available |
| Property taxes | Yes — proportionate |
| Home insurance | Yes — proportionate |
| Maintenance and repairs | Yes — proportionate to workspace |
| **CCA on home** | **NO — destroys PRE** |

**CRA form:** T2125 Part 7, or T2200/T777 for employees.
**IT-514 reference:** Home Office Expenses (archived but principles unchanged).

**Work-space-in-home proportion:** Calculate as workspace square footage ÷ total home area.

### The Renter's Exception

If CC is **renting** (not owning) the home:
- No PRE concern (renter doesn't have capital gains on the property)
- CCA doesn't apply to leased property anyway
- Claim rent proportionate to workspace as expense
- No downside here — full deduction available

---

## 16. SOFTWARE, HARDWARE, AND AI TOOLS

### Complete Classification for OASIS AI Solutions

| Asset Type | CCA Class | Rate | Notes |
|-----------|-----------|------|-------|
| MacBook, iMac, PC | 50 | 55% (or 100% IE) | General purpose computer |
| iPad, Surface tablet | 50 | 55% (or 100% IE) | If used for business |
| iPhone (business) | 50 | 55% (or 100% IE) | Smartphone = computer |
| External drives, NAS | 50 | 55% (or 100% IE) | Computer peripherals |
| Monitors, keyboard, mouse | 50 | 55% (or 100% IE) | Part of computer system |
| Network switches, routers | 46 | 30% (or 100% IE) | Data network infrastructure |
| Printers | 8 | 20% (or 100% IE) | Office equipment |
| Webcam, microphone | 8 | 20% (or 100% IE) | If separate from computer |
| Microsoft Office (perpetual) | 12 | 100% | Application software |
| Adobe Creative Cloud (annual) | N/A — operating | 100% immediate | SaaS subscription = expense |
| Claude API credits | N/A — operating | 100% immediate | Cloud service = expense |
| GitHub Copilot sub | N/A — operating | 100% immediate | SaaS = expense |
| QuickBooks Online | N/A — operating | 100% immediate | SaaS = expense |
| Windows/macOS licence | 50 | 55% | Systems software |
| Custom AI model (owned IP) | 14.1 or 12 | 5% or 100% | Depends on nature/cost |
| Domain name (perpetual) | 14.1 | 5% | Unlimited-life intangible |
| Domain name (annual renewal) | N/A — operating | 100% immediate | Recurring fee = expense |

### Cloud Services — Operating Expense (Not CCA)

This is a critical distinction. **SaaS = expense, not depreciable property.**

You cannot claim CCA on:
- Monthly subscriptions (Notion, Slack, AWS, GCP, Azure monthly billing)
- API usage fees (OpenAI, Anthropic Claude API)
- Software-as-a-service (anything you access over the internet without a perpetual licence)

You claim these as **operating expenses** on T2125 Line 8760 (computer costs) or 8810 (office).
The full amount is deductible in the year paid.

**This is actually better than CCA:** SaaS fees are 100% deductible immediately with no UCC
tracking required. No recapture risk. Simpler bookkeeping.

### AI Tool Classification Decision Tree

```
Did you pay a one-time fee for a perpetual licence?
├── YES
│   ├── Is it application software?      → Class 12 (100%)
│   ├── Is it systems software?           → Class 50 (55%)
│   └── Is it custom IP you developed?    → Class 14.1 (5%) or Class 12 (<$500)
└── NO (monthly/annual subscription)
    └── Operating expense (100% deductible) — not CCA
```

---

## 17. CLASS 14.1 — GOODWILL AND INTANGIBLES

### The 2017 ECP Transition

Before January 1, 2017: "Eligible Capital Property" (ECP) rules under ITA s.14 (old).
After January 1, 2017: Class 14.1 (5% declining balance) under ITA s.13.

**Transitional conversion:**
- Pre-2017 Cumulative Eligible Capital (CEC) balance × 4/3 = opening Class 14.1 UCC
- Reason: ECP included 75% of cost (¾ rule); Class 14.1 includes 100% — must gross up

### What Goes Into Class 14.1

**Inclusions:**
- Goodwill on business acquisition (excess of price over FMV of identifiable assets)
- Trademarks, trade names (with indefinite registration)
- Customer lists, client relationships
- Non-compete agreements (indefinite)
- Franchise rights (perpetual or indefinitely renewable)
- Government licences and permits (unlimited duration)
- Milk quotas, supply management quotas (agriculture)
- Taxi licences (unlimited)

**Exclusions (do NOT go in Class 14.1):**
- Patents, trademarks, licences with fixed terms → Class 14 (straight-line)
- Tangible property (equipment, buildings) → appropriate tangible class
- Land (not depreciable at all)

### Class 14.1 Disposition — The 75% Rule

**When selling goodwill or Class 14.1 property:**

```
Proceeds of disposition
-  Capital cost (what you paid for it)
=  Gain

If gain > 0:
  Portion up to original cost reduces UCC (potential recapture = 100% income)
  Portion above original cost → s.14(1) gain → 75% included in income
  (this 75% is more expensive than regular capital gains at 50%)
```

**Why this matters for OASIS sale:**
If CC sells OASIS for $500,000, with identifiable assets worth $100,000 and goodwill therefore
$400,000 (assuming no prior CCA on goodwill = original cost $0):
- $400,000 gain on goodwill × 75% = $300,000 included in income
- Tax at 26.5% corporate (if incorporated) = $79,500
- Vs if shares sold: LCGE exempts first $1.25M of capital gains — $0 tax

**This is the #1 reason to structure OASIS as a CCPC for a future sale.**

---

## 18. LEASE VS BUY — TAX COMPARISON

### General Principle

**Buying (CCA):** Deduct the asset over its class life (potentially accelerated with AII/IE).
Risk of recapture on disposal. Terminal loss possible.

**Leasing (operating expense):** Deduct lease/rental payments in full (subject to vehicle caps)
in the year paid. No recapture. No terminal loss. Off-balance sheet for small businesses.

### When Leasing Wins

1. **Short-term use:** You only need the asset for 2-3 years. CCA write-off is too slow.
2. **Rapidly obsoleting technology:** Computers, servers — you want to upgrade often.
3. **Luxury vehicles over $37,000:** Avoid Class 10.1 CCA cap and terminal loss trap.
4. **Cash flow:** Lease payments spread the cost; buying requires upfront capital.
5. **True tax lease (CRA accepts):** Full payment deductible; no CCA complexity.

### When Buying Wins

1. **Long-term use:** You'll keep the asset for 10+ years; total deductions are the same.
2. **High-rate classes (Class 12, 50):** Immediate write-off of 100% or 82.5% year 1.
3. **CCPC with immediate expensing:** 100% write-off in year 1, no long-term commitment.
4. **Appreciating assets:** Buy; lease payments for appreciating assets are economically wasteful.
5. **SR&ED eligible:** Owned equipment qualifies for SR&ED ITC; leased equipment generally doesn't.

### Operating Lease vs Financing Lease

**Operating lease (true lease):**
- Lessee uses the asset, does not own it
- Full lease payment = deductible operating expense
- CRA tests: is the lessor bearing the risks/rewards of ownership?

**Financing lease (capital lease / conditional sale):**
- Economically a purchase financed by the lessor
- CRA may reclassify: lessee must capitalize the asset and claim CCA
- Lessor cannot also claim CCA — only one party claims
- Test: Does the lease transfer substantially all risks and rewards to lessee?

**CRA position (IT-233R — archived):** CRA uses substance over form. A "lease" that contains
an option to buy at a nominal price, or where the present value of lease payments equals substantially
all of the fair market value of the asset, will be treated as a conditional sale.

---

## 19. CCA ON T2125, T776, AND T2

### T2125 — Business and Professional Income (Sole Proprietors)

**Where CCA appears:** T2125 Part 10 (CCA section), Area A through Area H

**Area A:** CCA Calculation — main schedule
- Column 1: Class number
- Column 2: Undepreciated capital cost at start of year
- Column 3: Cost of acquisitions during the year
- Column 4: Proceeds of dispositions
- Column 5: UCC after adjustments
- Column 6: CCA rate
- Column 7: CCA for the year

**Area B–H:** Specific schedules for:
- B: Automotive and Class 10.1 (separate schedule per vehicle)
- C: Rental property (if mixed use)
- D: Leasehold improvements (Class 13)
- E: Class 14 (straight-line intangibles)
- F: Class 14.1 (goodwill additions/dispositions)
- G: Equipment additions and dispositions

**Key line:** Net income (loss) on T2125 flows to T1 Schedule 1, Line 13500 (net business income).
CCA reduces this amount.

### T776 — Rental Income

**Where CCA appears:** T776 Part 4 (CCA for Rental)

Important: s.1100(11) restriction must be applied here. Cannot create a rental loss using CCA.
CRA's T776 calculates the restriction automatically if you enter income and expenses correctly.

**Separate class election notation:** Add a note to the T776 identifying each building by address
with its own UCC pool (invoking s.1101(1ac)).

### T2 — Corporate Income Tax Return

**Where CCA appears:** Schedule 8 (T2 Schedule 8 — Capital Cost Allowance)

Schedule 8 requires:
- Class-by-class UCC breakdown
- Acquisitions and dispositions by class
- CCA claimed and CCA available
- Recapture and terminal loss calculations

Schedule 8 flows to T2 line 403 (CCA deduction).

**T2 additional form:** For immediate expensing under the CCPC rules, use CRA's updated
Schedule 8 which includes the immediate expensing limit tracking.

---

## 20. CRA AUDIT TRIGGERS FOR CCA

### Top CCA Audit Flags

| Flag | Risk Level | Mitigation |
|------|-----------|-----------|
| Large vehicle deduction without mileage log | High | Use MileIQ app daily |
| CCA on home + PRE claim on same property | Very High | Never claim CCA on owned home |
| 100% business use of a vehicle | High | Maintain contemporaneous log |
| Computer purchased near year-end (large deduction) | Medium | Keep receipt + usage documentation |
| Leasehold improvements on expired lease | High | Update UCC schedule, claim terminal loss |
| Class 14.1 goodwill purchased from related party | High | FMV documentation required |
| Large M&P equipment in non-manufacturing business | Medium | Document nexus to income |
| Rental CCA creating a loss | High | Apply s.1100(11) correctly on T776 |

### Documentation Standards

**For any CCA claim, keep:**
1. Original purchase receipt (date, amount, HST/PST, vendor)
2. Description of the asset and its business purpose
3. First date placed in use for income-earning purposes
4. For vehicles: complete mileage log for the year
5. For home office: floorplan or measurement documentation
6. For leasehold improvements: lease agreement showing term and renewal options
7. For Class 14.1: purchase agreement showing goodwill allocation

**Retention period:** ITA s.230 — books and records must be retained for **6 years** after the
taxation year to which they relate. For depreciable property: retain until 6 years after the
class is extinct.

### IT Bulletins (Reference Archive)

These are archived but remain authoritative on CCA interpretation:

| Bulletin | Topic |
|---------|-------|
| **IT-79R3** | Capital Cost Allowance — Meaning of Depreciable Property |
| **IT-195R4** | Rental Property — Capital Cost Allowance Restrictions |
| **IT-285R2** | Capital Cost Allowance — General Comments |
| **IT-464R** | Capital Cost Allowance — Leasehold Interests |
| **IT-478R2** | Capital Cost Allowance — Class 14.1 transitional and intangibles |
| **IT-514** | Work-Space-in-Home Expenses |
| **IT-521R** | Motor Vehicle Expenses Claimed by Self-Employed Individuals |
| **IT-522R** | Vehicle, Travel and Sales Expenses of Employees |

**Note:** CRA archived these ITs but their interpretive content is still cited in Tax Court cases
and CRA technical interpretations. They are valid CCA guidance even though marked archived.

---

## 21. CC-SPECIFIC CCA PLANNING

### Current Status Assessment (2026-03-28)

**CC's profile:**
- 22-year-old, Ontario sole proprietor
- OASIS AI Solutions (AI/SaaS business)
- PropFlow (product business)
- December 31 fiscal year-end
- No CCPC yet (incorporation trigger: $80K+ revenue)

### Priority CCA Actions for CC

**1. Computer and Equipment (Class 50 — 100% with Immediate Expensing)**

As a sole proprietor, CC qualifies for immediate expensing up to $1.5M.
Every dollar of computer equipment is a 100% deduction in year of purchase.

Checklist:
- [ ] MacBook: Class 50, 100% if purchased in 2024/2025+
- [ ] External drives: Class 50
- [ ] Monitors: Class 50
- [ ] iPad/tablet: Class 50
- [ ] Phone (business use portion): Class 50
- [ ] Network equipment: Class 46 (30%) or Class 50

**2. Software (Class 12 — 100%)**
- [ ] Any perpetual software licences: Class 12, 100% in year of purchase
- [ ] All SaaS subscriptions: operating expense, 100% immediate — no UCC tracking needed

**3. Office Furniture (Class 8 — 20%, or 100% with Immediate Expensing)**
- Desk, chair, shelving: Class 8
- With immediate expensing: 100% in year of purchase

**4. Vehicle (if applicable)**
- Gas vehicle > $37K: Class 10.1, cap at $37K, no terminal loss
- EV ≤ $61K: Class 54, 100% immediate expensing — dramatically better
- Maintain mileage log from Day 1

**5. Home Office — DO NOT claim CCA**
- CC almost certainly plans to own property and use PRE eventually
- Claim operating expenses only (internet, hydro, heat, property tax — proportionate)
- Document workspace as % of total home area

### OASIS Incorporation Trigger — CCA Implications

When OASIS crosses $80K+ revenue and CC incorporates:

**CCA advantages of incorporation:**
1. **s.85 rollover:** Transfer existing assets (computer, equipment) to CCPC at ACB → no recapture
2. **CCPC immediate expensing:** $1.5M limit available again (fresh limit for the corporation)
3. **SR&ED + CCA stacking:** CCPC SR&ED ITC is 35% refundable; reduces CCA base but gives cash
4. **Rental property CCA:** If CC holds rental property in CCPC with rental as principal business,
   s.1100(11) restriction doesn't apply → CCA can create rental losses to offset other income
5. **Goodwill planning:** On incorporation, no goodwill transfer needed initially (CCPC hasn't
   bought goodwill) — goodwill builds in the CCPC for future LCGE planning

**Warning on s.85 rollover — CCA interaction:**
When transferring assets via s.85(1), the elected amount must be between:
- **Minimum:** Greater of FMV of boot received OR tax cost (adjusted cost base)
- **Maximum:** FMV of assets

If elected amount = UCC of transferred assets → no immediate CCA recapture.
Corporation takes over the UCC and continues claiming CCA at the same rates.
Document each asset class separately in the s.85 election agreement.

### Annual CCA Optimization Checklist for CC

**September/October (pre-year-end planning):**
- [ ] Project year-end net income before CCA
- [ ] Determine target taxable income bracket
- [ ] Calculate optimal CCA to claim in each class
- [ ] Identify any assets to acquire before December 31 (immediate expensing/AII)
- [ ] Review mileage log — is it complete for the year?
- [ ] Confirm available for use status on any late-year acquisitions

**December 31:**
- [ ] Finalize equipment purchases (receipt dated 2024/2025 — available for use)
- [ ] Document business purpose of all assets acquired

**January–February (T1 preparation):**
- [ ] Update UCC schedule for each class
- [ ] Apply recapture/terminal loss calculations
- [ ] Claim optimal CCA (0 to maximum — not automatic)
- [ ] Enter on T2125 Part 10 Schedule A (Areas A–H)
- [ ] Verify rental property CCA doesn't violate s.1100(11)

---

## 22. QUICK REFERENCE CHEAT SHEET

### Top 10 CCA Rules Everyone Forgets

| # | Rule | Why It Matters |
|---|------|---------------|
| 1 | CCA is **optional** — claim $0 to max | Smooth income, maximize rate benefit |
| 2 | Half-year rule → AII → Immediate expensing | Know which regime applies to your acquisition year |
| 3 | Class 10.1: **no terminal loss** on disposal | Choose EV (Class 54) for luxury vehicles instead |
| 4 | Rental CCA **cannot create a loss** (s.1100(11)) | Restrict CCA to rental income available |
| 5 | CCA on home **destroys PRE** proportionately | Claim operating expenses, never building CCA |
| 6 | SaaS = **operating expense**, not CCA | 100% deductible immediately, no UCC tracking |
| 7 | Class 14.1 gains: **75% included** (not 50%) | Sell shares, not goodwill, for best tax |
| 8 | SR&ED ITC **reduces capital cost** for CCA | Plan CCA base after SR&ED credit received |
| 9 | Separate class election for **rental buildings** | Get terminal loss on individual buildings |
| 10 | Recapture is **100% income** (not 50% cap gain) | Time disposals in low-income years |

### Maximum First-Year CCA Rates (2024, After AII Phaseout)

| Class | Normal Half-Year | 2024-2025 AII | Immediate Expensing |
|-------|-----------------|---------------|---------------------|
| 1 Buildings | 2% | 4% (1.0×) | Not eligible |
| 8 Misc | 10% | 20% (1.0×) | 100% |
| 10 Vehicles | 15% | 30% (1.0×) | 100% |
| 10.1 Luxury veh. | 15% | 30% (1.0×) | 100% |
| 12 Small tools | 100% | 100% | 100% |
| 14.1 Goodwill | 2.5% | 5% (1.0×) | Not eligible |
| 43 M&P | 15% | 30% (1.0×) | 100% |
| 50 Computers | 27.5% | 55% (1.0×) | 100% |
| 53 M&P 2016+ | 25% | 50% (1.0×) | 100% |
| 54 ZEV passenger | Full rate | 100% | 100% |

*2024-2025: AII enhancement = 1.0× (back to normal half-year; no additional enhancement vs pre-2024)*
*2026-2027: 0.75× enhancement over base half-year rate*
*2028+: Return to straight half-year rule (0.5×)*

### Dollar-Value Decision Table

| Annual Income | Marginal Rate | Value of $10,000 CCA |
|--------------|--------------|---------------------|
| $0 – $51,446 | 20.05% | $2,005 |
| $51,447 – $57,375 | 24.15% | $2,415 |
| $57,376 – $102,894 | 29.65% | $2,965 |
| $102,895 – $111,733 | 31.48% | $3,148 |
| $111,734 – $150,000 | 33.89% | $3,389 |
| $150,001 – $165,430 | 37.91% | $3,791 |
| $165,431 – $220,000 | 43.41% | $4,341 |
| $220,001 – $246,752 | 46.16% | **$4,616** |
| $246,753+ | 53.53% | **$5,353** |

*Ontario 2024 combined federal + provincial rates*

**Takeaway:** The same $10,000 of CCA claimed is worth $5,353 at the top rate vs $2,005 at the
bottom. **CCA timing optimization is a 2.67× multiplier on value.**

### Key ITA Sections — Reference Card

```
CCA deduction:        s.20(1)(a)
CCA definitions:      s.13(21)
Available for use:    s.13(26)-(28)
Recapture:            s.13(1)
Terminal loss:        s.20(16)
Change of use:        s.13(7)
Class 10.1 special:   s.13(2), (2.1)
Rental restriction:   Reg. 1100(11), (12)
Half-year rule:       Reg. 1100(2)
AII:                  Reg. 1100(2)(a)(ii)
Immediate expensing:  s.13(1.1), (1.2); Reg. 1100(0.1)
SR&ED ITC reduction:  s.127(11.1)
Vehicle limits:       s.67.2 (interest), s.67.3 (lease), Reg. 7307
Class 14.1 gain:      s.14(1) (post-2016 reference rules)
s.85 rollover:        s.85(1)
Affiliated stop-loss: s.13(21.2)
ECP transition:       s.13(37)-(42), Reg. 1100(1)(a)(xiv.1)
```

---

## APPENDIX — PHASE-OUT SCHEDULE REFERENCE

### AII Phaseout by Property Category

**Category A — General (most classes):**
| Period | AII Multiplier | Effective First-Year = Rate × |
|--------|---------------|-------------------------------|
| After Nov 20, 2018 – Dec 31, 2023 | 1.5× | 1.5 |
| Jan 1, 2024 – Dec 31, 2025 | 1.0× | 1.0 |
| Jan 1, 2026 – Dec 31, 2027 | 0.75× | 0.75 |
| Jan 1, 2028 + | 0.5× (half-year rule returns) | 0.5 |

**Category B — Zero-emission vehicles (Classes 54, 55, 56):**
- No half-year rule from the start; maintained full first-year rates longer
- Phase-in and phase-out follows Budget 2019 schedules
- After 2027: subject to AII on remaining amounts

**Category C — Immediate expensing (CCPCs and individuals):**
- 100% on eligible property, $1.5M limit
- Originally for property available for use before 2024, but extended
- Individuals: extended to 2024 and beyond in Budget 2022/2023 — confirm current status

---

*Document created: 2026-03-28*
*Atlas version: Wave 5*
*Authority: ITA, Regulations (SOR/85-696), CRA Interpretation Bulletins*
*Next review: Year-end 2026 — update for Budget 2026 changes (AII phaseout confirmation)*
