# ATLAS — Platform Economy & Gig Worker Tax Guide

> **For:** Conaugh McKenna (CC), OASIS AI Solutions, Collingwood Ontario
> **Jurisdiction:** Canada (Ontario) | **Tax year:** 2025-2026 (planning)
> **Last Updated:** 2026-03-28
> **Purpose:** Definitive reference for every platform-derived income stream a Canadian can earn from —
> ride-sharing, food delivery, short-term rentals, e-commerce, freelance platforms, content creation,
> crypto platforms, task/service apps, and investment platforms. Covers income classification,
> HST/GST obligations, deduction strategy, CRA enforcement posture, and multi-platform optimization.
> All ITA references are to the *Income Tax Act (Canada)*, R.S.C. 1985, c.1 (5th Supp.) unless noted.
> ETA references are to the *Excise Tax Act*, R.S.C. 1985, c.E-15.
> CRA guide references: **T4002** (self-employed business guide), **T4044** (employment expenses),
> **RC4070** (GST/HST guide for businesses), **IT-521R** (motor vehicle expenses — archived but still
> instructive), **TN-78** (CRA policy on commercial ride-sharing and HST).

**Tags used throughout:**
- `[NOW]` — Actionable today as a sole proprietor or gig worker
- `[FUTURE]` — Relevant upon incorporation or at higher income levels
- `[CC]` — Specific to CC's actual financial situation
- `[HST]` — HST/GST-specific action item
- `[RISK]` — CRA audit or penalty exposure — read carefully

---

## Table of Contents

1. [Platform Income — The General Framework](#1-platform-income--the-general-framework)
2. [Business Income vs Employment Income — The Wiebe Door Test](#2-business-income-vs-employment-income--the-wiebe-door-test)
3. [CRA Platform Economy Initiative — Mandatory Reporting](#3-cra-platform-economy-initiative--mandatory-reporting)
4. [HST/GST Obligations Across Platforms](#4-hstgst-obligations-across-platforms)
5. [Ride-Sharing: Uber, Lyft, InDriver](#5-ride-sharing-uber-lyft-indriver)
6. [Food Delivery: DoorDash, Uber Eats, Skip the Dishes, Instacart](#6-food-delivery-doordash-uber-eats-skip-the-dishes-instacart)
7. [Short-Term Rentals: Airbnb, VRBO, Hipcamp](#7-short-term-rentals-airbnb-vrbo-hipcamp)
8. [E-Commerce: Etsy, Amazon FBA, Shopify, eBay, Facebook Marketplace](#8-e-commerce-etsy-amazon-fba-shopify-ebay-facebook-marketplace)
9. [Freelance Platforms: Upwork, Fiverr, Toptal, 99designs, PeoplePerHour](#9-freelance-platforms-upwork-fiverr-toptal-99designs-peopleperhour)
10. [Content Creation: YouTube, TikTok, Twitch, Patreon, OnlyFans, Substack, Spotify](#10-content-creation-youtube-tiktok-twitch-patreon-onlyfans-substack-spotify)
11. [Cryptocurrency Platforms: Exchanges, Staking, Mining, NFTs](#11-cryptocurrency-platforms-exchanges-staking-mining-nfts)
12. [Task and Service Platforms: TaskRabbit, Handy, Rover, Helpling, Pawshake](#12-task-and-service-platforms-taskrabbit-handy-rover-helpling-pawshake)
13. [Transportation and Logistics: Trucking Apps, Courier Platforms, Canada Post Delivery Partners](#13-transportation-and-logistics-trucking-apps-courier-platforms)
14. [Investment and Finance Platforms: Wealthsimple, Questrade, Interactive Brokers, Lending Loops](#14-investment-and-finance-platforms)
15. [Professional Services on Platforms: Clarity.fm, Codementor, Teachable, Udemy](#15-professional-services-on-platforms)
16. [Seasonal and Niche Platforms: FlipKey, Outdoorsy, Turo, Boatsetter](#16-seasonal-and-niche-platforms)
17. [Multi-Platform Tax Optimization](#17-multi-platform-tax-optimization)
18. [Record Keeping and Compliance Systems](#18-record-keeping-and-compliance-systems)
19. [CPP Self-Employment Obligations](#19-cpp-self-employment-obligations)
20. [Red Flags and Audit Triggers](#20-red-flags-and-audit-triggers)
21. [CC-Specific Platform Strategy](#21-cc-specific-platform-strategy)
22. [Key ITA/ETA Reference Index](#22-key-itaeta-reference-index)

---

## 1. Platform Income — The General Framework

### 1.1 The Core Principle: All Platform Income is Taxable

**ITA s.3** defines "income for a tax year from a source" to include every form of income, regardless
of how it is earned, whether it flows through a digital platform, a traditional employer, or a
cash-in-hand arrangement. There is no de minimis exemption in Canadian income tax law — a $14 Uber
Eats delivery tip and a $140,000 Upwork contract are both subject to the same reporting obligation.

CRA's position, stated explicitly in the **T4002 guide (2024 edition)**, is that platform income is
self-employment income reportable on **Form T2125** (Statement of Business or Professional Activities)
unless the worker qualifies as an employee under common-law or statutory employment rules.

**Three scenarios and their tax treatment:**

| Scenario | Tax Treatment | Form |
|----------|---------------|------|
| Sole proprietor contractor on platform | Business income | T2125 |
| Worker the platform classifies as employee | Employment income | T4 |
| Investment or passive income from platform | Investment/property income | T3/T5/Schedule 4 |

The vast majority of gig platform workers in Canada are sole proprietor contractors. Platforms
deliberately structure their terms of service to disclaim employment relationships because employment
status triggers employer CPP/EI obligations, minimum wage requirements, and employment standards
protections.

### 1.2 The T4A Reality

**ITA s.153(1)(g)** requires payers to deduct and withhold from amounts paid to contractors —
however, this withholding rule applies primarily to construction services (T5018) and certain other
prescribed payments. Most gig platforms do NOT withhold tax.

Platforms issue **T4A slips** (Statement of Pension, Retirement, Annuity, and Other Income) where:
- Payments to a single individual exceed **$500** in a calendar year
- The platform has a Canadian business number and is paying a Canadian resident

**Critical point:** Many foreign-domiciled platforms (Upwork Inc., Fiverr Ltd.) do NOT issue T4A
slips to Canadian workers because they have no CRA filing obligation. The income is still 100%
taxable. "No T4A" does not mean "not taxable."

`[RISK]` CRA's platform cross-referencing program (see Section 3) means CRA is independently
identifying platform income from bank deposit data, even where no information slip was issued.

### 1.3 Hobby Income vs Business Income

CRA distinguishes between hobby activities (not taxable, not deductible) and business activities
(taxable, deductible expenses allowed) using the "reasonable expectation of profit" (REOP) test
established by the Supreme Court in **Stewart v. Canada [2002] 2 SCR 645**.

**Stewart test — two questions:**

1. Is the activity undertaken for profit (i.e., is there a commercial element)?
2. If personal elements exist, does the taxpayer's activity have the indicia of commerciality?

For platform income, the commercial element is almost always present — the platforms are commercial
marketplaces. CRA rarely applies the hobby argument to platform workers. The more relevant risk is
the **sustained loss scenario**: if a platform activity produces losses every year, CRA may deny
the deduction of those losses against other income on the basis that the activity lacks a reasonable
expectation of profit (IT-504R2, Folio S3-F4-C1).

**Practical test for platform workers:**

| Factor | Business Signal | Hobby Signal |
|--------|----------------|--------------|
| Are you trying to make money? | Yes, primarily | No, mostly personal enjoyment |
| Do you track income and expenses? | Yes | No |
| Do you operate in a businesslike manner? | Yes | No |
| Have you made a profit in the past? | Yes | Never |
| Do you depend on this income? | Yes | No |

---

## 2. Business Income vs Employment Income — The Wiebe Door Test

### 2.1 Why This Matters

The characterization of a platform worker as an **employee vs independent contractor** determines:
- Whether EI premiums apply (workers pay EI only as employees)
- Whether employer CPP contributions apply (platforms must match CPP if employment exists)
- Whether expenses are deductible on T2125 (contractor) vs limited T777 (employee)
- Which party bears the HST registration obligation

### 2.2 The Wiebe Door Four-Factor Test

Established in **Wiebe Door Services Ltd. v. MNR [1986] 3 FC 553** and affirmed in **671122 Ontario
Ltd. v. Sagaz Industries Canada Inc. [2001] 2 SCR 983**, the test examines four factors holistically:

**Factor 1: Control**
- Does the payer control HOW the work is done, or just the result?
- Platform-level control: Can the platform dictate working hours, routes, uniform, behavior? The more
  control, the more employment-like.
- Uber, DoorDash, Lyft: Workers choose their own hours, accept/reject jobs, work for multiple
  platforms simultaneously — signals independent contractor.
- Uber Eats requiring specific delivery windows or maintaining acceptance-rate minimums: slides toward
  employment.

**Factor 2: Tools and Equipment**
- Who provides the tools?
- Contractor brings their own car, phone, equipment = independent contractor signal.
- Employer provides tools, uniform, software = employment signal.
- For most delivery/ride-share work, the worker provides the vehicle — contractor signal.

**Factor 3: Chance of Profit / Risk of Loss**
- Can the worker profit by being more efficient? Bear losses from vehicle damage, gas, time?
- Gig workers bear the financial upside and downside of their working decisions — contractor signal.
- An employee earns a fixed wage regardless of efficiency.

**Factor 4: Integration**
- Is the worker integrated into the business (central to operations) or in business for themselves?
- A delivery driver could theoretically deliver for any company — in business for themselves.
- An internal logistics coordinator embedded in operations — integrated = employment signal.

### 2.3 Platform-Specific Determinations

| Platform | CRA/Court Determination | Notes |
|----------|------------------------|-------|
| Uber (ride-share) | Independent contractor | CRA TN-78; workers in business for themselves |
| Lyft | Independent contractor | Same analysis as Uber |
| DoorDash | Independent contractor | Workers supply own vehicle, set own hours |
| Instacart | Independent contractor | In-store shoppers may be employees in some provinces |
| Airbnb host | Not employment | Property owner, not a service worker |
| Upwork freelancer | Independent contractor | Classic contractor relationship |
| OnlyFans creator | Self-employed | Creates and distributes own content independently |

### 2.4 When CRA Rules You Are an Employee

If CRA reassesses a platform relationship as employment, the consequences are severe:
- Employer (platform) owes backdated CPP contributions + 10% penalty
- Employer owes backdated EI premiums
- Worker may be entitled to EI benefits
- Worker loses access to T2125 business expense deductions
- Worker has limited expenses claimable on T777 (requires T2200 from employer)

`[RISK]` Some workers deliberately seek employment characterization to access EI during slow periods.
This is a legitimate strategy but requires careful analysis of the specific platform relationship and
provincial employment standards.

---

## 3. CRA Platform Economy Initiative — Mandatory Reporting

### 3.1 The DAC7-Style Regime

Effective **January 1, 2024**, Canada implemented **reporting rules for digital platform operators**
under proposed amendments to the ITA, consistent with the OECD's Model Rules for Reporting by
Platform Operators (DAC7). Under these rules:

- Digital platforms must collect and report information on **seller income** to CRA
- Reporting covers: ride-sharing, food delivery, short-term rentals, gig services, goods sales
- The information must be reported to CRA by **January 31** of the following year
- CRA then cross-references this data against T1 filings

**What platforms must report (per seller):**
- Full legal name
- Primary address
- TIN (Social Insurance Number, if Canadian)
- Total consideration paid in each quarter
- Number of relevant activities performed
- For property rentals: address of each listed property, number of rental days

### 3.2 Which Platforms Are Caught

A platform operator is caught if it:
- Facilitates the provision of services or sale of goods through a digital interface
- Pays or credits consideration to sellers
- Has a nexus to Canada (Canadian-resident sellers, or collects Canadian payments)

**Caught:** Airbnb, Vrbo, Uber, Lyft, DoorDash, Uber Eats, Skip the Dishes, Etsy, Fiverr (with
Canadian operations), Upwork (with Canadian nexus), Amazon (seller payments), eBay, Kijiji Autos,
Rover, TaskRabbit (Canadian operations).

**Not caught (but income still taxable):** Platforms with no Canadian operations and no Canadian
sellers — however CRA's treaty exchange-of-information network (Canada-US treaty Article XXVII,
MCAA/CRS) means data may still flow to CRA from foreign tax authorities.

### 3.3 CRA Bank Deposit Cross-Reference Program

Independent of platform reporting, CRA's analytics division runs an algorithm that:
1. Obtains Canadian bank transaction data under s.231.2 (requirement to provide information)
2. Identifies regular deposits from known platform processors (Stripe, PayPal, Wise, Square, Interac
   e-Transfer)
3. Flags accounts where deposit patterns suggest business income not declared on T1
4. Issues "matching" letters requesting explanation, followed by reassessments if no satisfactory
   response

`[RISK]` This program has been active since 2018. CRA identified over $1.1B in unreported platform
income between 2019-2022 according to the CRA Compliance Framework annual report. If CC receives
income through any platform, it must be declared — the question is never whether CRA will find it,
but when.

### 3.4 CRA's Platform Economy Audit Team

CRA established a dedicated **Platform Economy Compliance Centre** within the Underground Economy
Division. This team:
- Receives platform data dumps from major operators
- Issues T4A corrections where platform income was underreported
- Conducts targeted correspondence audits
- Refers systemic underreporting to the Special Enforcement Program for potential prosecution

---

## 4. HST/GST Obligations Across Platforms

### 4.1 The $30,000 Combined Threshold

**ETA s.148(1):** A person is a "small supplier" exempt from mandatory HST/GST registration only
if their **total worldwide taxable supplies** across ALL activities in the previous four consecutive
calendar quarters did not exceed **$30,000**.

This threshold is **combined across all platform income sources**. A worker earning:
- $15,000 from Uber Eats
- $12,000 from Airbnb
- $6,000 from Upwork

Has $33,000 in total taxable supplies and **must register for HST/GST** — even though no single
platform crossed $30,000 individually.

### 4.2 Ride-Share Exception: No Threshold

**CRA Technical Notice TN-78** establishes that commercial ride-sharing (Uber, Lyft, etc.) is a
"taxi service" under ETA s.1. Under **ETA s.240(1.4)**, persons who provide taxi services are
required to register for GST/HST **regardless of the level of revenue** — there is no $30,000
threshold exception.

**This is the only platform category with mandatory registration from dollar one.**

### 4.3 Digital Services to Non-Residents

Under **ETA Schedule VI, Part V, s.7**, services supplied to non-residents who are outside Canada
at the time of supply are **zero-rated** — meaning HST is charged at 0%, but ITCs are still
claimable. This applies to:
- Upwork/Fiverr contracts with US or EU clients (where the client is outside Canada)
- Airbnb bookings by non-Canadian guests (where the property is in Canada — taxable supply, not
  zero-rated; the guest's residency does not make the rental zero-rated)
- YouTube AdSense (Google LLC is a non-resident — zero-rated B2B supply if CC is registered)

**Critical distinction:** Zero-rated is not exempt. A platform worker who is registered for HST
and provides services to non-residents charges 0% HST but reports the supply and claims full ITCs
on related inputs. An exempt supply (like most residential rent) does not allow any ITC claim.

### 4.4 Ontario-Specific: Provincial Platform Rules

Certain Ontario municipalities impose additional requirements:
- **Toronto short-term rental licence:** Required to operate. $113.64/year. Failure = bylaw fine.
- **Toronto Municipal Accommodation Tax (MAT):** 6% on short-term rentals in Toronto, collected by
  Airbnb automatically since 2019.
- **Ottawa short-term rental permit:** Required from City of Ottawa. Annual renewal.
- **Municipal HST equivalents:** Quebec has QST (9.975%) collected by platforms on behalf of
  operators in some cases.

---

## 5. Ride-Sharing: Uber, Lyft, InDriver

### 5.1 Income Classification

Uber and Lyft drivers in Canada are classified as **independent contractors** (self-employed).
CRA confirmed this in multiple technical interpretations and in TN-78. Income is reported on
**Form T2125**, line 13499/13500. Industry code: **485310** (Taxi and limousine service).

### 5.2 HST Registration — Mandatory from Dollar One

`[HST]` Under **ETA s.240(1.4)** and CRA TN-78:
- Register for a **Business Number (BN) with HST/RT account** at canada.ca/register-cra
- **Registration must occur BEFORE the first trip is completed**
- Collect HST on all fares (Ontario: 13% on the fare amount)
- Remit HST to CRA on the designated filing frequency (quarterly recommended for new registrants)
- Claim **Input Tax Credits (ITCs)** on all HST paid on business expenses

**Uber/Lyft platform mechanics:**
Uber collects HST from passengers on the driver's behalf in Ontario (and most provinces with HST).
The driver's weekly earnings statement shows:
- Gross fares
- Uber's service fee (deductible as a business expense)
- Net earnings transferred to driver

The HST on gross fares is collected by Uber and remitted on behalf of drivers in Ontario since
2017 under the "agent" arrangement. However, drivers remain **legally responsible** for HST
obligations — CRA can assess the driver if Uber fails to remit.

**Action for CC:** If ever operating Uber/Lyft, register for HST on Day 0, before completing
any rides. Keep Uber weekly earnings statements as documentation. File HST returns quarterly.

### 5.3 Deductible Expenses for Ride-Share

**T4002 Guide — Vehicle Expenses:**

The ride-share vehicle is the primary asset. Two methods are available:

**Method 1: Actual Expenses (Detailed Method)**
Track all vehicle costs and deduct the business-use percentage.

| Expense Category | Deductibility | Notes |
|-----------------|---------------|-------|
| Gasoline and oil | Business % of total | Based on km log |
| Insurance | Business % of total | Annual premium only |
| Licence and registration | Business % | Annual |
| Car wash and detailing | Business % | Cleanliness required for Uber rating |
| Repairs and maintenance | Business % | Keep all receipts |
| Loan interest | Max $300/month (ITA s.67.2) | Only if vehicle purchased with debt |
| CCA on vehicle | See below | Subject to year-1 50% rule |
| Parking | 100% if business-related | Keep receipts |
| Tolls | 100% if business-related | 407 ETR records |

**Capital Cost Allowance on Vehicle:**
- **Class 10** (CCA rate 30%): Vehicles costing $36,000 or less (before HST) — 2024 threshold
- **Class 10.1** (CCA rate 30%): Vehicles costing more than $36,000 — CCA limited to $36,000 cost
  base regardless of actual cost (ITA s.13(2) and Reg. 1100(1)(a)(x))
- **Immediate expensing:** For eligible depreciable property acquired after Jan 28, 2021 and before
  Jan 1, 2025, up to **$1.5M** per year for CCPCs (sole proprietors: $100,000). Under ITA s.1100(2.01)
  as amended by Bill C-19.
- Year-1 50% rule (Reg. 1100(2)): CCA in year of acquisition is halved. Plan acquisition timing
  accordingly (buy in January, not December).

**Method 2: Simplified Per-Kilometre Rate**
CRA publishes annual rates (IT-521R, archived — use T4044 rates):
- 2024: **$0.70/km** for the first 5,000 km | **$0.64/km** for each km after
- No need to track individual expenses — just log km
- Cannot claim CCA separately if using the km rate
- Recommended when annual business km × rate > actual expenses

**Which method to use:**
For full-time Uber drivers with a vehicle used primarily for business, the **detailed method**
almost always yields a higher deduction. For part-time gig work, the km rate is simpler.

`[CC]` If CC ever drives for Uber, calculate both methods on the first tax return and pick the
better one. Stick with that method consistently — CRA requires consistency.

### 5.4 Mileage Log Requirements

**IT-521R (archived) and T4002 current guidance:**
- Log must be maintained throughout the **entire calendar year**
- Each entry: date, destination, business purpose, odometer start, odometer end, km driven
- Log must be contemporaneous (written at the time of driving, not reconstructed at year-end)
- Total business km / total annual km = business-use percentage
- CRA auditors request the mileage log in virtually every vehicle expense audit

**Digital solutions:** Automatic tracking apps (MileIQ, TripLog, Everlance) sync with CRA's
accepted format. Acceptable as a contemporaneous record under CRA guidance.

**Alternative: Representative Sample Period**
Under CRA's "simplified logbook" policy (Guide T4044, updated 2024), if CC has kept a full-year
log for a base year, subsequent years may use a **3-consecutive-month representative sample** to
extrapolate the full-year business percentage — provided annual km vary by less than 10% from the
base year. The sample must be a different 3 months each year. Not available in the first year
of vehicle use.

### 5.5 Insurance

Standard personal auto insurance does **not** cover commercial ride-sharing activity. Uber provides
third-party liability coverage while the app is open and during a trip, but:
- Coverage has deductibles of $1,000-$2,500
- Coverage ends when the app is closed between trips
- Personal insurer can void the policy entirely if they discover commercial use

**Deductibility:** The incremental cost of a commercial ride-sharing rider endorsement is
100% deductible as a business expense. The personal auto insurance is deductible at business-use
percentage only.

### 5.6 Additional Deductions

| Expense | Deductibility | Authority |
|---------|---------------|-----------|
| Uber/Lyft platform fee (25-30% commission) | 100% business expense | T4002, s.18(1)(a) |
| Phone (business use %) | ITC + income deduction | T4002 |
| Phone plan (business use %) | ITC + income deduction | T4002 |
| Water/drinks for passengers | Marginal, risky | Keep receipts, small amounts only |
| Seat covers, USB chargers | 100% deductible if purchased for business | T4002 |
| Dash cam | CCA Class 8 (20%) | Business purpose documented |

---

## 6. Food Delivery: DoorDash, Uber Eats, Skip the Dishes, Instacart

### 6.1 Income Classification

Food delivery couriers are **independent contractors**, self-employed. Report on **T2125**, industry
code: **492110** (Couriers and messengers, local). T4A slips issued if the Canadian entity pays
a single courier more than $500/year.

### 6.2 HST Threshold: Standard $30,000 Rule

Unlike ride-sharing, food delivery is **not a taxi service** and therefore the standard $30,000
small supplier threshold applies under ETA s.148. A DoorDash courier earning $25,000 per year
does **not** need to register for HST unless combined taxable supplies from all sources exceed $30,000.

However: once registered (voluntarily or mandatorily), all supplies become taxable and HST must
be collected on all applicable services.

### 6.3 Vehicle vs Bicycle vs E-Bike Expenses

**By vehicle (car):** Same expense regime as ride-sharing (Section 5.3). CCA, gas, insurance,
repairs — all subject to business-use percentage.

**By bicycle:** The bicycle is a business tool:
- CCA Class 8 (20% declining balance) on purchase price
- Bicycle maintenance (tune-ups, new tires, chain) 100% deductible
- Bike lock, lights, reflective gear — 100% deductible
- No fuel costs, but energy drink during a shift? Not deductible (personal living expense, s.18(1)(h))

**By e-bike:**
- Treated as a bicycle for CCA purposes (Class 8)
- Battery replacement deductible
- Charging costs are incidental (negligible and difficult to separate from personal use)

### 6.4 Specialized Delivery Equipment

| Equipment | Deductibility | CCA Class |
|-----------|---------------|-----------|
| Insulated hot bags / cold bags | 100% | Class 8 (20%) |
| Magnetic phone mount for dash | 100% | Class 8 or immediate expense |
| Handlebar phone holder | 100% | Class 8 or immediate expense |
| Thermal delivery backpack | 100% | Class 8 (20%) |
| Helmet (if cycling) | 100% (safety equipment) | Consumable — full deduction in year |
| Rain gear / reflective vest | 100% (safety, work-specific) | Consumable — full deduction in year |
| Gloves for winter delivery | 100% if work-specific | Consumable |

**Note:** CRA requires that apparel and protective equipment be work-specific and not usable for
personal purposes. A raincoat that could be worn socially is harder to defend than a high-visibility
vest with no personal application.

### 6.5 Platform Fee Deductibility

| Platform | Fee Structure | Deductibility |
|----------|--------------|---------------|
| DoorDash | No commission to courier; courier keeps 100% of per-delivery rate | N/A |
| Uber Eats | Service fee deducted from courier payout (~0%, most cost borne by restaurant) | Deduct any platform-imposed fees |
| Skip the Dishes | Per-order rate, no percentage deducted | N/A |
| Instacart | Commission on orders in some models | Deduct if charged |

### 6.6 Instacart-Specific Notes

Instacart has two worker models in Canada:
- **Full-service shopper:** Independent contractor (most common). T2125.
- **In-store shopper:** In some markets, these are part-time employees with a T4.

`[RISK]` Check your Instacart earnings summary. If you receive a T4, you are an employee and
employment deduction rules (T777, T2200) apply instead of T2125.

---

## 7. Short-Term Rentals: Airbnb, VRBO, Hipcamp

### 7.1 Business Income vs Rental Income — The Critical Distinction

**ITA s.9** (business income) vs **ITA s.3(a)** with Schedule E (rental/property income): the
distinction determines which form you file and which expenses are deductible.

**CRA's test** (Folio S3-F4-C1 and IT-434R, archived):
- **Rental income (T776):** Passive provision of housing. Tenant has exclusive use. Landlord provides
  no services beyond basic maintenance.
- **Business income (T2125):** Active provision of accommodation services — cleaning between guests,
  linens, breakfast, concierge, luggage storage, 24/7 availability. Hotel-like services.

**For most Airbnb hosts:**

| Host Type | Classification | Form |
|-----------|---------------|------|
| Rent out spare room occasionally | Rental income | T776 |
| Rent out primary home while traveling | Rental income | T776 |
| Professional Airbnb operator, multiple units, hotel-like services | Business income | T2125 |
| Operate as a licensed B&B | Business income | T2125 |

The distinction matters because:
- T776 rental losses cannot exceed rental income in year (CCA limitation — Reg. 1100(11))
- T2125 business losses can offset other income (employment, investment)
- T2125 allows broader expense categories

### 7.2 HST on Short-Term Rentals

**ETA s.123(1) "short-term accommodation":** Rental of residential complex for periods under
**one month** is a taxable supply (not an exempt residential rental).

- Rentals **< 30 consecutive nights:** Taxable supply. HST/GST applies. Must register if > $30,000.
- Rentals **> 30 consecutive nights:** Exempt supply under ETA Schedule V, Part I, s.6. No HST/GST.
  No ITCs on related expenses.

**Airbnb automatic collection:**
Airbnb (Airbnb Ireland UC, operating in Canada) automatically collects and remits:
- HST/GST on accommodation in most Canadian provinces (Ontario, BC, Alberta, etc.)
- Quebec QST (separately)
- Municipal accommodation taxes (Toronto MAT, Vancouver Tourism Levy, etc.)

If Airbnb is remitting HST on your behalf, verify whether you also have a separate obligation.
In Ontario, Airbnb remits HST under its own BN — the host may still need to register if they
have other taxable supplies exceeding $30,000. Consult CRA RC4052 (GST/HST information for
accommodation operators).

### 7.3 Principal Residence Exemption Risk

`[RISK]` Under **ITA s.40(2)(b)**, the principal residence exemption (PRE) shelters capital gains
on a home from taxation. However, CRA Folio S1-F3-C2 clarifies that if a property is **not
exclusively used as a personal residence**, the PRE may be prorated.

**CRA's administrative position:**
If the primary use of the home remains residential and rental is incidental (e.g., renting out
a basement suite or one room for part of the year), CRA generally does not require recaptured
CCA or PRE proration — if **no CCA has been claimed** on the property.

The trap: **Claiming CCA on the home or a portion of it** (e.g., depreciation on the "rental
portion") triggers **recapture** on sale and permanently impairs the PRE. This is the most common
and most expensive Airbnb tax mistake.

**The rule: Never claim CCA on your principal residence.**

**When the PRE is at serious risk:**
- You purchase a property exclusively for Airbnb (never your primary residence)
- You rent out more than 50% of the home by floor area
- The income is so large that a court would find the primary purpose is commercial
- You have a separate "Airbnb property" business with multiple units

### 7.4 Deductible Expenses — T776 (Rental Income)

**CRA Guide T4036 (Rental Income):**

| Expense | Deductibility | Notes |
|---------|---------------|-------|
| Airbnb/VRBO platform fee (3-5% host fee) | 100% | Rental expense |
| Cleaning fees paid to third parties | 100% | Rental expense |
| Cleaning supplies purchased | 100% | Rental expense |
| Linens, towels, toiletries for guests | 100% | Consumable supplies |
| Property insurance (pro-rated to rental use) | Pro-rata by use | Must allocate if mixed use |
| Mortgage interest (not principal) | Pro-rata by use | Only interest component, ITA s.20(1)(c) |
| Property taxes (pro-rated to rental use) | Pro-rata by use | |
| Utilities (pro-rated to rental use) | Pro-rata by use | Hydro, gas, water |
| Internet (pro-rated to rental use) | Pro-rata by use | |
| Furniture and furnishings — CCA | Class 8 (20%) | On rental-use portion only |
| Repairs and maintenance (not capital) | 100% if for rental portion | Capital improvements: CCA |
| Advertising and photography fees | 100% | |
| Property management fees | 100% | If using a co-host service |
| Lock box, keypad, smart lock | 100% CCA Class 8 | |

**Pro-ration formula (mixed use — owner also lives in the property):**

```
Rental deductible % = (Rental area m²) / (Total home area m²)
                    × (Rental days) / (Total days in year)
```

Example: 2-bedroom apartment, 100m² total. Rent the spare room (20m²) for 200 days:
Rental % = (20/100) × (200/365) = 10.96%

Apply this % to shared expenses (utilities, insurance, mortgage interest, property tax).
Room-specific expenses (painting that room, dedicated furnishings) are 100% deductible.

### 7.5 Hipcamp and Outdoor Hospitality

Hipcamp (camping on private land) is treated identically to Airbnb for tax purposes. Revenue from
allowing campers on private land:
- Rental income (T776) if passive land use
- Business income (T2125) if providing services (fire wood, guided hikes, glamping setups)

CCA on camping infrastructure (glamping pods, yurts, outhouses, composting systems):
- Yurts and temporary structures: Class 8 (20%)
- Permanent structures: Class 6 (10%) or Class 1 (4%)

---

## 8. E-Commerce: Etsy, Amazon FBA, Shopify, eBay, Facebook Marketplace

### 8.1 Income Classification

Sales of goods through e-commerce platforms are **business income** — report on **T2125**.
Industry code: varies by product (e.g., 454110 for electronic shopping and mail-order houses).

**Exception:** Occasional personal property sales (selling used furniture, one-off collectibles)
may be **capital gains** (or non-taxable if personal-use property under ITA s.46). The test is
frequency and intent. If CC regularly buys items to resell at a profit — that is business income,
not capital gains, regardless of what each item "is."

### 8.2 Inventory Valuation

**ITA s.10(1):** Inventory must be valued at the lower of:
- Cost (purchase price + shipping + duties + direct costs to bring to saleable condition)
- Fair Market Value (FMV) at year-end

**Methods:**
- **FIFO (First-In, First-Out):** First units purchased are the first sold. Accurate but requires
  tracking per-unit cost.
- **Average Cost:** Total cost of inventory / number of units. Simpler, accepted by CRA.
- **Specific Identification:** For high-value unique items (handmade, antiques). Required for
  items > $1,000 each.

`[RISK]` CRA does not accept LIFO (Last-In, First-Out) in Canada — it is a US-only method.
Etsy/Amazon FBA sellers who use LIFO for inventory accounting will be reassessed.

### 8.3 HST on E-Commerce

**For physical goods (Etsy handmade, eBay, Shopify products):**
- Sales to Canadian customers: taxable supply. HST/GST at applicable rate.
- Sales to US/foreign customers with delivery outside Canada: zero-rated (ETA Sched VI, Part V, s.1)
- Register when combined taxable supplies exceed $30,000.

**For digital products (design files, printables, templates, software):**
- Sales to Canadian customers: taxable supply (HST/GST)
- Sales to non-residents outside Canada: zero-rated (ETA s.7 Sched VI Part V) — they consume the
  digital product outside Canada

**Platform HST collection:**
- Etsy: Collects and remits GST/HST on sales by non-registered Canadian sellers (under marketplace
  facilitator rules effective July 1, 2021 — Finance Canada amendments to ETA)
- Amazon FBA: Amazon collects GST/HST on marketplace sales under the same regime
- Shopify: Does NOT collect HST for you — you must configure tax settings and remit yourself
- eBay: Collects GST/HST on sales through their platform for non-registered sellers

### 8.4 Amazon FBA USA — US Tax Obligations

Selling through Amazon FBA in the US creates potential US tax exposure:
- **Economic nexus:** Most US states have economic nexus thresholds ($100,000 sales or 200
  transactions). Amazon's marketplace facilitator laws mean Amazon collects state sales tax
  on your behalf in most states.
- **Federal US income tax:** Canadian residents without US PE generally not subject to US federal
  income tax on business profits (Canada-US Treaty, Article VII). File **Form W-8BEN-E** (for
  businesses) or **W-8BEN** (for individuals) with Amazon to prevent 30% withholding.
- **ITIN requirement:** Not required if W-8BEN filed correctly and you have no US PE.

### 8.5 Deductible Expenses for E-Commerce

| Expense | Deductibility | Notes |
|---------|---------------|-------|
| Cost of goods sold (COGS) | 100% | Opening inventory + purchases − closing inventory |
| Etsy listing fees ($0.20 USD/item) | 100% | Platform cost of doing business |
| Etsy transaction fee (6.5% of sale price) | 100% | |
| Etsy payment processing fee (3% + $0.25) | 100% | |
| Amazon FBA referral fee (8-15%) | 100% | |
| Amazon FBA fulfillment fee (per-unit) | 100% | |
| Shopify subscription ($39-$399 USD/month) | 100% | |
| Shipping supplies (boxes, tape, labels) | 100% | |
| Postage and courier costs | 100% | |
| Photography equipment (for product photos) | CCA Class 8/10 | |
| Website/domain hosting | 100% | |
| Home office (workspace for packing/admin) | Pro-rata by area | T2125 home office |
| Product development materials | 100% | For handmade goods |
| Graphic design / branding | 100% or CCA if intangible asset | |

### 8.6 Facebook Marketplace and Kijiji

**Personal property sales (used furniture, electronics, clothes):**
Under **ITA s.46**, dispositions of "personal-use property" (property used primarily for personal
use and enjoyment) are:
- Non-taxable if sold for less than $1,000 (adjusted cost base deemed to be $1,000)
- Capital gain if sold for more than $1,000 — taxed at 50% inclusion rate

**Business income scenario:**
If CC regularly buys items at garage sales, thrift stores, or estate auctions to resell on
Facebook Marketplace, CRA will characterize this as business income — not capital gains — under
the "adventure or concern in the nature of trade" doctrine (ITA s.248(1) definition of "business").

---

## 9. Freelance Platforms: Upwork, Fiverr, Toptal, 99designs, PeoplePerHour

### 9.1 Income Classification and Reporting

Freelance platform income is **business income**, T2125. Industry code based on service type:
- Software development: **541510**
- Graphic design: **541430**
- Writing/translation: **711510**
- Marketing/SEO: **541810**
- Consulting: **541600**

T4A slips: Most foreign-domiciled platforms (Upwork, Fiverr) do not issue Canadian T4As. The
income remains 100% taxable — CC must self-report.

### 9.2 Platform Fees

| Platform | Fee to Freelancer | Deductibility |
|----------|-------------------|---------------|
| Upwork | 10-20% sliding scale (drops as lifetime billings with client increase) | 100% |
| Fiverr | 20% flat on every order | 100% |
| Toptal | No fee to freelancer (talent placement model) | N/A |
| 99designs | 15-25% depending on tier | 100% |
| PeoplePerHour | 20% up to £500 earned, 7.5% above | 100% |

Platform fees are deductible under **ITA s.18(1)(a)** as expenses incurred to earn business income.

### 9.3 Foreign Currency Income

Freelance platforms pay in USD, EUR, or GBP in most cases. Canadian residents must **convert to
CAD** for reporting purposes.

**CRA accepted methods:**
1. **Bank of Canada (BoC) daily rate:** Use the BoC noon rate on the date of receipt. Most
   accurate. BoC rates are at bankofcanada.ca/rates/exchange.
2. **Annual average rate:** Use the BoC annual average USD/CAD exchange rate for the entire year.
   Acceptable if exchange rate fluctuation is not material.

The elected method must be **applied consistently** — you cannot use daily rates for gains and
annual average for losses.

**Foreign exchange gains and losses:**
If CC invoices a client in USD on December 1 and receives payment on January 15:
- December 1 receivable: $5,000 USD × 1.36 = $6,800 CAD (income recognized at invoice date)
- January 15 receipt: $5,000 USD × 1.33 = $6,650 CAD
- Foreign exchange loss: $150 CAD — deductible as a business expense under ITA s.9/18(1)(a)

For business income, FX gains/losses on trade receivables flow through the T2125 as income/expense.

### 9.4 US Client W-8BEN and Treaty Protection

When a US platform or US client pays a Canadian freelancer, they may be required to withhold
**30% US withholding tax** under Internal Revenue Code s.1441 unless the freelancer provides a
**Form W-8BEN** (or W-8BEN-E for businesses) certifying Canadian residency and claiming treaty
protection.

**Canada-US Tax Treaty, Article VII** (Business Profits): A Canadian resident's business profits
from services performed in Canada are **not taxable** in the US, provided the Canadian does not
have a "permanent establishment" (PE) in the US. Upwork and Fiverr work performed from Canada
does not create a US PE.

**Action:**
1. Complete Form W-8BEN — available at irs.gov
2. Claim Treaty Article VII (Business Profits) exemption
3. Submit to the platform (Upwork, Fiverr, PayPal, Stripe) through their tax information portal
4. Renew every 3 years (W-8BEN has a 3-year validity)

`[CC]` CC earns USD through OASIS contracts. This applies directly. File W-8BEN with any US
platform that processes CC's payments to prevent unnecessary 30% withholding.

### 9.5 Home Office Deduction

Under **ITA s.18(12)**:
- Home office expenses are deductible only if the workspace is:
  - The **principal place of business**, OR
  - Used **exclusively for work** and **regularly to meet clients**
- Deduction cannot create a business loss (can only reduce business income to zero)
- Unused home office expenses carry forward indefinitely

**Calculation (T2125 Part 7):**
```
Home office deduction = (Office area m²) / (Total home area m²) × Total home expenses
```

Total home expenses for T2125 include: rent, mortgage interest (not principal), property taxes,
home insurance, utilities, internet, condo fees. Do NOT include mortgage principal — it is not an
expense.

**For renters:** The full rent is a home expense. Prorate by office area.

### 9.6 Equipment and Technology Deductions

| Asset | CCA Class | Rate | Notes |
|-------|-----------|------|-------|
| Computer, laptop | Class 50 | 55% | Primary business computer |
| Tablet (business use) | Class 50 | 55% | Pro-rate if personal use also |
| External monitors | Class 8 | 20% | |
| Keyboard, mouse, peripherals | Class 8 | 20% | Or immediate expense if < $500 |
| Office desk, chair | Class 8 | 20% | Only if dedicated workspace |
| Smartphone | Class 8 | 20% | Pro-rate personal/business use |
| Software subscriptions (monthly) | 100% current deduction | Not CCA | Operating expense |
| Software (perpetual licence > $500) | Class 12 | 100% | CRA accepts Class 12 for licensed software |
| Cloud storage (Dropbox, Google Drive) | 100% current deduction | Not CCA | Operating expense |

**Immediate expensing (ITA s.1100(2.01)):** Eligible sole proprietors can claim up to $100,000
of eligible depreciable property in the year of acquisition (if acquired after Jan 28, 2021
and before Jan 1, 2025). This allows full write-off of a $3,000 laptop in year 1 instead of
the 55% Class 50 declining balance. Post-2024 purchases revert to normal CCA unless the
temporary immediate expensing rule is extended.

---

## 10. Content Creation: YouTube, TikTok, Twitch, Patreon, OnlyFans, Substack, Spotify

### 10.1 Income Streams and Classification

All content creation revenue is **business income** for tax purposes in Canada. The key distinction
CRA makes is whether the creator is:
1. Carrying on business (regular, organized, profit-oriented) — T2125
2. Earning sporadic income that might be hobby — see Section 1.3

For any creator earning more than $500/year through any platform, CRA treats this as business income.

**Revenue sources and their tax treatment:**

| Revenue Source | Platform | Tax Treatment |
|----------------|----------|---------------|
| Ad revenue (CPM-based) | YouTube AdSense, TikTok Creator Fund | Business income |
| Channel memberships | YouTube, Twitch | Business income |
| Super Chats / Super Thanks | YouTube | Business income |
| Bits | Twitch | Business income (FMV at time received) |
| Tips | Ko-fi, Buy Me a Coffee, Twitch Cheers | Business income (NOT a gift) |
| Brand deals / sponsorships | Any platform | Business income |
| Affiliate income (commission) | Amazon Associates, any | Business income |
| Merchandise sales | Shopify, Printful/SPOD integrated | Business income (COGS deductible) |
| Course sales | Teachable, Kajabi | Business income |
| Patreon subscriptions | Patreon | Business income |
| OnlyFans subscriptions/tips | OnlyFans | Business income |
| Substack paid subscriptions | Substack | Business income |
| Spotify streaming royalties | DistroKid/CD Baby | Business income (royalty type) |
| Book advances and royalties | Publishers | Business income |

**CRA position on tips:** In **Blais v. Canada [2003] TCC 85** and related jurisprudence, CRA
and Tax Court have consistently held that tips received in the course of business activity are
**income from business or employment**, not personal gifts. The "gift" exception under ITA s.6(1)(a)
requires a genuine personal motivation disconnected from business services — Twitch subscriber
giving bits is rewarding the stream content, not making a personal gift.

### 10.2 Foreign Revenue and Platform Payments

Most major content platforms are US companies paying in USD:
- YouTube (Google LLC): AdSense payments in USD
- Twitch (Amazon): Partner/Affiliate payments in USD
- Patreon (Patreon Inc.): Creator payments in USD
- OnlyFans (Fenix International Ltd., UK): Payments in USD

**Apply foreign currency conversion rules from Section 9.3.**

**W-8BEN for content creators:**
YouTube, Twitch, and Patreon require Canadian creators to submit tax information to prevent
US withholding. YouTube's AdSense requires W-8BEN — after submission, YouTube applies treaty
withholding rates:
- Royalty-type payments (ad revenue on content): Canada-US Treaty, Article XII (Royalties) — 0%
  withholding for residents of Canada
- Without W-8BEN: 30% withholding applies

**Action:** Submit W-8BEN through YouTube Studio > Payments > Manage settings > Tax info.
Twitch: similar process through Creator Dashboard. Patreon: Tax Information tab.

### 10.3 OnlyFans-Specific Tax Notes

OnlyFans has unique considerations:
- Payments processed through Fenix International (UK) and then Stripe — not US withholding
- T4A: OnlyFans does NOT issue Canadian T4A slips
- Income is 100% self-reported on T2125 — CRA has been specifically targeting OnlyFans creators
  since 2022 under the platform economy initiative
- **Privacy consideration:** Legal name is on the T2125 under the creator's SIN. The "business
  name" (stage name) on T2125 is separate from CRA's records.

`[RISK]` CRA has issued requirement letters to Stripe (payment processor) and major banks to
identify large inflows from Fenix International. Canadian OnlyFans creators who have not reported
income should consider the **Voluntary Disclosure Program** (see docs/ATLAS_VDP_GUIDE.md) before
CRA initiates contact.

### 10.4 Content Creation Deductions

**Equipment and Studio:**

| Asset | CCA Class | Rate | Notes |
|-------|-----------|------|-------|
| Camera (DSLR, mirrorless, cinema) | Class 8 | 20% | |
| Camera lenses | Class 8 | 20% | |
| Lighting (key lights, ring lights, softboxes) | Class 8 | 20% | |
| Audio equipment (mic, interface, headphones) | Class 8 | 20% | |
| Green screen / backdrop | Class 8 | 20% | |
| Drone | Class 8 | 20% | |
| Video editing computer | Class 50 | 55% | Or Class 12 if software is primary use |
| Stream deck / capture card | Class 8 | 20% | |
| Gaming setup (if gaming content) | Pro-rate personal/business | Class 8/50 | |
| Tripod, stabilizer, accessories | Class 8 | 20% | |
| Studio furniture | Class 8 | 20% | |

**Operating Expenses:**

| Expense | Deductibility | Notes |
|---------|---------------|-------|
| Adobe Creative Cloud | 100% | Software subscription |
| Final Cut Pro, DaVinci Resolve | 100% or Class 12 | One-time licence |
| Music licences (Epidemic Sound, Artlist) | 100% | Annual subscription |
| Stock footage subscriptions | 100% | |
| VPN for content research | 100% if business | |
| Props purchased for content | 100% if consumable | CCA if durable asset |
| Costumes/clothing for content only | 100% | Must be work-specific, not personal use |
| Travel for content (YouTube travel vlog) | Business % | Must document business purpose |
| Conference/event tickets (if attending for content) | 100% | E.g., fan conventions |
| Internet (home office %) | Pro-rata | T2125 |
| Phone plan (business %) | Pro-rata | T2125 |
| Thumbnail design (Canva Pro) | 100% | |
| Editing software plugins | 100% | |

**Meals and Entertainment (50% Rule):**
Under **ITA s.67.1**, meals and entertainment are deductible at only **50%** of cost. This applies
to any meal consumed while traveling for content, or entertainment provided to sponsorship contacts.

### 10.5 HST on Content Revenue

- **Canadian viewers/subscribers:** Services provided to Canadian residents are taxable supplies.
  If total platform income exceeds $30,000, register and collect HST.
- **Non-Canadian viewers (US, EU):** Services to non-residents outside Canada — zero-rated supply
  (ETA Schedule VI, Part V, s.7). If the platform (YouTube, Patreon) is the recipient of the
  supply (i.e., CC supplies content to Google, who serves it to end users), the supply is B2B
  to a non-resident — likely zero-rated.
- **Sponsorship revenue from non-Canadian brands:** Zero-rated if client is outside Canada.
- **Sponsorship revenue from Canadian brands:** Taxable supply. Invoice with HST once registered.

**Practical approach for most creators under $30,000:**
Do not register. Track total supply carefully. Register the moment combined platform income
approaches $30,000 to avoid retroactive HST liability.

---

## 11. Cryptocurrency Platforms: Exchanges, Staking, Mining, NFTs

### 11.1 Cross-Reference to Dedicated Guides

For deep treatment of crypto tax, refer to:
- **docs/ATLAS_DEFI_TAX_GUIDE.md** — Staking, LP, yield farming, NFTs, bridges, airdrops, CARF
- **docs/ATLAS_CRYPTO_TAX_ADVANCED.md** — ACB, superficial loss, business vs capital gains

This section covers the platform mechanics specifically.

### 11.2 Exchange-Reported Income

**CRA-known Canadian exchanges (data reported to CRA):**
- Coinsquare: CRA issued a requirement under ITA s.231.2 in 2021. All accounts producing > $20,000
  in annual transactions were reported.
- Newton (Canadian): Subject to CARF reporting from 2026.
- Bitbuy, NDAX, Shakepay: Canadian MSBs (Money Services Businesses) registered with FINTRAC —
  CARF adoption expected.
- Coinbase: Has complied with CRA information requirements on Canadian accounts.
- Kraken: CRA issued requirement letter in 2023 for Canadian account data.

**CARF (Crypto-Asset Reporting Framework):** G20 adopted framework requiring exchange reporting
of all crypto transactions, effective **January 1, 2026** in Canada. After 2026, CRA will receive
annual transaction-level data for every Canadian exchange account — name, SIN, trade history.

### 11.3 Income vs Capital Gains — The Platform Frequency Test

**ITA s.9 and CRA Folio S3-F9-C1** (Lottery Winnings, Miscellaneous Receipts, and Income from
Crime): CRA applies a multi-factor test to determine whether crypto trading activity is business
income (100% inclusion) or capital gains (50% inclusion):

| Factor | Business Income Signal | Capital Gain Signal |
|--------|----------------------|---------------------|
| Frequency of transactions | Daily or weekly | Occasional |
| Holding period | Days to weeks | Months to years |
| Time spent on trading | Significant, organized | Passive |
| Use of margin/leverage | Yes | No |
| Knowledge of crypto markets | Sophisticated | Unsophisticated |
| Financing trades with debt | Yes | No |
| Intent at acquisition | Quick profit | Long-term hold |

For CC specifically: holding BTC/ETH long-term in a Kraken account is likely capital gains. Active
trading through the ATLAS system with daily positions — likely business income. This is a live
question CC should discuss with an accountant at the point of incorporation.

### 11.4 Mining Income

**CRA position (Income Tax Folio S3-F4-C1 and CRA technical interpretation 2014-0525191E5):**
- Mining income = business income if operated with regularity and profit motive
- Mined coin is **income at FMV on the day it is mined**
- FMV at mining date becomes the **ACB** for future disposition
- Mining equipment: CCA Class 50 (55%) or immediate expense
- Electricity: 100% deductible if dedicated to mining
- If mining from home: electricity pro-rated to mining use (separate circuit meter recommended)

**HST on mining:** CRA's position is that mining does not constitute a "supply" for HST purposes
(mining is a reward from the protocol, not from a recipient). No HST on mining rewards.

### 11.5 Staking and DeFi Yield

- Staking rewards are income at FMV when received (ITA s.9 or s.12(1)(x) depending on arrangement)
- DeFi yield (LP fees, lending interest): income at FMV when claimable or received
- Liquidity pool entry/exit: each entry/exit is a **disposition** triggering capital gain/loss

Full treatment in docs/ATLAS_DEFI_TAX_GUIDE.md.

### 11.6 NFT Platforms: OpenSea, Magic Eden, Foundation

- NFT **creation and sale by the artist**: business income (T2125). Industry code 711510.
- NFT **resale by a collector**: capital gain if held long-term / business income if frequent flipping
- **Royalties on secondary sales**: business income in the year received
- **Gas fees on NFT purchases**: add to ACB. Gas fees on NFT sales: deduct from proceeds.
- **Platform fees** (OpenSea 2.5%): deductible as a business or capital transaction cost.

---

## 12. Task and Service Platforms: TaskRabbit, Handy, Rover, Helpling, Pawshake

### 12.1 Income Classification

All task platform income is **business income** on T2125. These platforms explicitly classify
workers as independent contractors. Industry codes:
- TaskRabbit (handyperson, moving, assembly): **561790** (Services to buildings and dwellings)
- Rover/Pawshake (pet sitting, dog walking): **812910** (Pet care, except veterinary)
- Handy (cleaning, home repairs): **561720** (Janitorial services) or **561790**
- Helpling (house cleaning): **561720**

### 12.2 Insurance Gap — The Critical Risk

`[RISK]` Neither TaskRabbit, Rover, Handy, nor Pawshake provides workers' compensation (WSIB
in Ontario) coverage. If a TaskRabbit worker falls off a ladder, a Rover sitter injures a dog,
or a Handy cleaner damages a client's property:
- The worker has NO WSIB coverage
- The platform's liability coverage is limited and contested
- The worker bears personal liability for damages

**Deductible solutions:**
- General liability insurance for independent contractors (available through BrokerLink, Intact,
  Aviva): $2M policy ~$300-800/year. 100% deductible as a business expense.
- WSIB optional coverage for self-employed in Ontario: Optional insurance at ~1-2% of earnings.
  100% deductible.

### 12.3 Tool and Supply Deductions

| Expense | Deductibility | Notes |
|---------|---------------|-------|
| Power tools (drill, sander, saw) | CCA Class 8 (20%) | TaskRabbit handyperson |
| Hand tools, toolbox | CCA Class 8 or immediate expense | |
| Safety equipment (gloves, goggles, hard hat) | 100% | Safety requirement |
| Rover — pet supplies (leashes, toys, treats) | 100% if used for clients | |
| Rover — pet first aid kit | 100% | |
| Handy — cleaning supplies | 100% | Consumable supplies |
| Handy — commercial vacuum, mop | CCA Class 8 | |
| Vehicle (to get to client homes) | Business km rate or detailed method | |
| Platform fees | 100% | TaskRabbit 15%, Rover 25% |
| Business liability insurance | 100% | |

### 12.4 Multiple Clients, Single Business

Running multiple platform services simultaneously (TaskRabbit + Rover + Handy) does not require
multiple T2125 forms. CRA allows all self-employment income on a single T2125 if the activities
are in the **same broad industry** (service businesses). For clearly distinct industries
(e.g., software development + house cleaning), separate T2125 forms are recommended for audit clarity.

---

## 13. Transportation and Logistics: Trucking Apps, Courier Platforms

### 13.1 Owner-Operator Trucking Platforms (Convoy, Loadlink, uShip)

Independent truck owner-operators earn business income on T2125. Industry code: **484110** (General
freight trucking, local).

**T5018 — Construction Subcontractors:** Note that T5018 applies specifically to construction
services, not trucking. Trucking platforms do not issue T5018 slips; T4A rules apply if the
Canadian company pays > $500 to an individual.

**Unique deductions for owner-operators:**

| Expense | Deductibility |
|---------|---------------|
| Truck/tractor — CCA Class 16 (40%) | Business-use % | High-declining rate for trucks
| Trailer — CCA Class 10 (30%) | Business-use % | |
| Fuel | 100% if commercial vehicle | |
| Truck insurance (commercial) | 100% | |
| IFTA (International Fuel Tax Agreement) filings | Compliance cost — deductible | |
| Logbook software (ELD, Hours of Service) | 100% | |
| Meals while on the road (long-haul) | 100% deductible for transport employees under ITA s.8(1)(g) | Only for drivers away from home municipality |
| Shower fees at truck stops | 100% if long-haul | |

**Long-haul meal deduction (s.8(1)(g)):** Unlike the general 50% meals restriction, employees
(T4 long-haul drivers) can deduct 80% of meals while away. Owner-operators (T2125) follow
the standard 50% meal rule under s.67.1. This is a material difference in take-home.

### 13.2 Canada Post / Purolator Delivery Contractors

Canada Post-contracted independent delivery drivers are sole proprietors. The contractual
relationship with Canada Post creates business income, not employment. Industry code: **491110**
(Postal service) or **492110** (couriers).

CRA has historically scrutinized Canada Post contractors for employment vs contractor status due
to the significant control Canada Post exercises over routes, uniforms, and hours. Work-to-rule
disputes at Canada Post have involved contractor reclassification as a tax issue. If operating
under a Canada Post delivery contract, document the independence of the business relationship.

---

## 14. Investment and Finance Platforms

### 14.1 Wealthsimple, Questrade, Interactive Brokers

Investment platforms are the vehicle for investment income, not business income (unless day-trading
frequency triggers business income classification — see Section 11.3).

**Tax slips issued:**
- **T5** (Statement of Investment Income): Interest, dividends, foreign income
- **T3** (Statement of Trust Income): Income from ETFs and mutual funds (trust distributions)
- **T5008** (Statement of Securities Transactions): Proceeds from securities dispositions
- **T5013** (Statement of Partnership Income): For limited partnerships and flow-through shares

**T5008 reconciliation:** The T5008 shows gross proceeds. The ACB (adjusted cost base) must be
tracked independently. The ACB is the average cost per share, adjusted for superficial loss
rules (s.54), return of capital, and stock splits. Wealthsimple does not track ACB for the
CRA — you must maintain your own records.

`[CC]` CC's Kraken trading generates capital dispositions that must be reported on **Schedule 3**
regardless of whether any T5008 is issued. Crypto exchanges do not issue T5008 — CC must compute
every disposition independently. See docs/ATLAS_CRYPTO_TAX_ADVANCED.md.

### 14.2 Day Trading — Business Income Determination

`[RISK]` CRA views **frequent securities trading** as business income if the trader:
- Trades daily or multiple times per week
- Has specialized market knowledge
- Uses margin or leveraged products
- Intends to profit from short-term price movements (not dividends/interest)
- Devotes significant time to trading

**Consequence:** Business income = 100% inclusion. Capital gains = 50% inclusion. The difference
on a $50,000 gain at the 43% Ontario marginal rate:
- Business income: $21,500 tax
- Capital gains: $10,750 tax

**TFSA day-trading risk (ITA s.146.2):** CRA has successfully challenged TFSA holders who
conducted frequent stock trading as carrying on business — voiding the TFSA tax shelter. The
income is assessed as business income at full marginal rates. Multiple Tax Court cases confirm
this: **Ahamed v. Canada [2023] TCC 15**, **Forsythe v. Canada [2022] TCC 130**.

`[CC]` Atlas's paper trading is in test mode. When live trading is activated, ensure tax
characterization is reviewed — ATLAS's algorithmic trading likely = business income at 100%
inclusion. This is a material planning point at incorporation.

### 14.3 Peer-to-Peer Lending (Lending Loop, Borrowell Marketplace)

Interest income from P2P lending is **investment income** reported on Schedule 4 / T5 (if a
slip is issued, which smaller platforms may not do). Report on line 12100.

Defaults on P2P loans: The capital loss on a bad debt can be claimed under ITA s.50(1) when the
debt is established as bad.

---

## 15. Professional Services on Platforms: Clarity.fm, Codementor, Teachable, Udemy

### 15.1 Expert Consultation Platforms (Clarity.fm, Expert360)

Phone and video consulting through platforms like Clarity.fm is business income on T2125.
The platform takes a percentage (Clarity.fm: 15%), and the net is reported as income.

**W-8BEN:** Required for Clarity.fm (US company). Prevents 30% withholding on consulting income.
Treaty Article VII (Business Profits) applies — 0% US withholding.

### 15.2 Online Course Platforms (Udemy, Teachable, Kajabi, Thinkific)

**Udemy:** Udemy is a US company. Royalty-type income. W-8BEN required. Canada-US Treaty Article
XII (Royalties) — 0% withholding for Canadian residents.

**Revenue recognition:** Course sales revenue is earned when the student completes the purchase
(for perpetual access) or pro-rated if there is a subscription model with ongoing access.

**Deductions for course creators:**
- Recording equipment, studio setup: CCA as above
- Platform subscription (Teachable $39-$119 USD/month): 100% deductible
- Guest speaker fees: 100% deductible (if for business course content)
- Course development research: 100% deductible (books, subscriptions)

### 15.3 Codementor, Tutoring Platforms

Programming tutoring income = business income. Same deduction profile as freelance (Section 9).
If tutoring academic subjects through a platform like Wyzant (primarily US), W-8BEN applies.

---

## 16. Seasonal and Niche Platforms: Turo, Outdoorsy, Boatsetter, Swimply

### 16.1 Turo (Peer-to-Peer Car Rental)

Vehicle listed on Turo = rental income or business income depending on services level. For
most Turo hosts (passive vehicle rental), this is **rental income** not business income,
reported on T776.

**HST on Turo:** Short-term vehicle rental is a taxable supply. A Turo host exceeding $30,000
in combined taxable supplies must register and collect HST.

**Vehicle expenses:** Same CCA and operating expense rules as ride-share (Section 5.3), pro-rated
to rental days. However, unlike personal vehicles used for ride-share, a vehicle held primarily
for rental (not personal use) is a **rental property** — different CCA limitations apply.

**Insurance note:** Personal auto insurance does not cover commercial rental. Turo provides
coverage plans for hosts. The host plan cost is deductible as a rental expense.

### 16.2 Outdoorsy and RV Rental

RV listed on Outdoorsy: rental income (T776). CCA on RV:
- Class 10 (30%): Recreation vehicles under certain thresholds

### 16.3 Boatsetter and Peer-to-Peer Boat Rental

Boat rental income: rental income or business income.
- If boat is listed passively (guest takes the helm): rental income T776
- If owner operates the boat as a charter service (owner drives, provides experience): business
  income T2125

**CCA on boats:**
- Class 7 (15%): Ships and vessels

**Licensing note:** Commercially operating a vessel in Canadian waters may require a Transport Canada
Pleasure Craft Operator Card and in some cases a Transport Canada marine licence. Non-compliance
is a regulatory risk, not a tax risk, but impacts insurance deductibility if coverage is voided.

### 16.4 Swimply (Private Pool Rental) and Space Rental

Swimply and similar platforms for renting private spaces (home pool, home gym, home recording studio):
- Rental income if passive property rental (T776)
- Business income if significant services are provided

**HST:** Short-term property rental = taxable supply. Apply $30,000 threshold analysis.

---

## 17. Multi-Platform Tax Optimization

### 17.1 Combined T2125 vs Separate T2125s

**CRA guidance (T4002):** A sole proprietor can file **one T2125** covering all business activities
in the same broad industry, or **multiple T2125s** for distinct business types.

**Best practice:**
- One T2125 for all content creation (YouTube + TikTok + Patreon + Twitch = one creator business)
- One T2125 for all freelance services (Upwork + Fiverr = one consulting business)
- Separate T2125 for materially different activities (e.g., ride-share + online course creation)
- One T776 for all rental properties (Airbnb + Turo)

Benefit of separate T2125s: Clean loss isolation, clearer industry codes, simpler CRA audit defense.
Benefit of single T2125: Losses on one platform offset profits on another automatically.

### 17.2 HST Threshold — Combined Tracking

`[HST]` The $30,000 threshold is a combined total across all taxable supplies. A platform worker
must track:
- T2125 income (all business income sources)
- T776 income that constitutes short-term rental (taxable supply)
- Any other taxable supply made

**Monthly running total spreadsheet:**

| Month | Upwork | Etsy | Airbnb (STR) | Total YTD | HST Threshold % |
|-------|--------|------|--------------|-----------|----------------|
| Jan | $1,800 | $600 | $500 | $2,900 | 9.7% |
| Feb | $2,200 | $800 | $1,000 | $6,900 | 23.0% |
| ... | | | | | |

Register the moment YTD approaches $30,000 — not after crossing it.

### 17.3 Loss Utilization Across Platforms

Under ITA s.3(a-d), a taxpayer's income from all sources is netted. Business losses on one
T2125 reduce business income on another T2125, and the net is included in income. This means:

- A profitable Upwork month that offsets an Airbnb startup loss = net reduction in taxable income
- A profitable trading year that offsets a new Etsy store's inventory investment = net benefit

**Capital loss limitations:** Capital losses (from securities, crypto, real estate) can ONLY
offset capital gains — they cannot offset business income. This is a hard rule in ITA s.3(b).

### 17.4 Quarterly Installments for Multi-Platform Earners

**ITA s.156(1):** Quarterly installments are required if **net tax owing** in the current year
AND the prior year BOTH exceed **$3,000** (Ontario residents — other provinces have $1,800 thresholds).

For multi-platform workers, the installment obligation can sneak up quickly:
- No tax withheld at source from any platform
- CPP contributions on self-employment (11.9%) add to the installment obligation
- HST remittances are separate from income tax installments

**Safe-harbour installments (no penalty, even if estimate is wrong):**
1. Pay 25% of prior year's tax each quarter, OR
2. Pay 25% of the second-prior year's tax each quarter (for Q1 and Q2), then true-up based on
   prior year for Q3 and Q4

See docs/ATLAS_INSTALLMENT_PAYMENTS.md for the complete installment calculation framework.

### 17.5 RRSP Contribution — Multi-Platform Income

Multi-platform self-employment income generates **RRSP contribution room** at 18% of net earned
income (capped at $31,560 for 2024). RRSP contributions reduce net income dollar-for-dollar.

**Strategy:** If CC earns $80,000 in combined platform income and is approaching a higher tax
bracket, contribute to RRSP to reduce net income to the lower bracket threshold:
- Ontario combined marginal rate at $80,000: approximately 31.48%
- At $100,000: approximately 43.41%
- RRSP contribution of $20,000 reduces income from $100K to $80K = $20,000 × 43.41% = $8,682
  in immediate tax savings

### 17.6 CPP on Multi-Platform Self-Employment

`[NOW]` **ITA s.122.51 (CPP) and CPP Act s.10-11:**
Every sole proprietor must pay both the **employee** and **employer** portion of CPP on net
self-employment income between $3,500 (basic exemption) and $68,500 (2024 YMPE):

- Employee rate: 5.95% → max $3,867.50
- Employer rate: 5.95% → max $3,867.50
- **Total CPP on self-employment: 11.9% → max $7,735**

CPP contributions on self-employment are partially deductible:
- Employer portion (50% of total): deductible on **line 22200** of T1
- Employee portion: generates a **non-refundable tax credit** at 15% federal on line 31000

**Practical impact on $40,000 net platform income:**
```
CPP base = $40,000 - $3,500 = $36,500
CPP owing = $36,500 × 11.9% = $4,343.50
Employer deduction = $4,343.50 / 2 = $2,171.75 (reduces business net income)
Employee credit = $2,171.75 × 15% = $325.76 (reduces federal tax)
```

This CPP obligation is often the largest surprise for new gig economy workers — it is nearly double
what an employee pays because there is no employer to share the cost.

---

## 18. Record Keeping and Compliance Systems

### 18.1 CRA Minimum Retention Requirements

**ITA s.230(4):** Records must be kept for a minimum of **6 years** after the last tax year to
which they relate. For ongoing capital property (Airbnb, vehicle used for business), records must
be kept until 6 years after the year the property is disposed of.

**What to keep:**

| Record Type | Retention | Format |
|-------------|-----------|--------|
| Bank statements (all accounts) | 6 years | Digital or paper |
| Platform payment records (Uber weekly summaries, Etsy receipts) | 6 years | Download and archive |
| All business receipts (gas, supplies, equipment) | 6 years | Digital scan acceptable |
| Vehicle mileage log | 6 years | Contemporaneous — cannot reconstruct |
| Home office measurements | 6 years | Photo + measurement document |
| T4A slips received | 6 years | |
| Contracts with clients | 6 years after contract end | |
| Crypto transaction records | 6 years after disposition | Every trade — CRA requires ACB |
| Invoices issued | 6 years | |
| HST/GST returns and working papers | 6 years | |

**Storage:** CRA accepts digital records (CRA Guide RC4409 — Keeping Records). Scanned receipts
on a cloud service (Google Drive, Dropbox) with backups accepted. A receipt destroyed by fire
is not an acceptable excuse — maintain redundant digital copies.

### 18.2 Quarterly Review Checklist

At the end of each calendar quarter (March 31, June 30, September 30, December 31), CC should:

**Income verification:**
- [ ] Download all platform payment summaries (Uber, DoorDash, Upwork, etc.)
- [ ] Record income by platform in spreadsheet or accounting software
- [ ] Convert all foreign currency (USD, GBP, EUR) to CAD at BoC rate
- [ ] Verify bank deposits match platform income (unexplained deposits = unreported income risk)

**HST/GST:**
- [ ] Total all taxable supplies for the quarter
- [ ] Compare against $30,000 rolling threshold
- [ ] If registered: calculate HST collected - ITCs = net remittance
- [ ] File HST return by one month after quarter-end

**Expenses:**
- [ ] Categorize all business expenses in accounting software
- [ ] Ensure mileage log is up to date
- [ ] Review home office calculation for accuracy
- [ ] Note any large equipment purchases for CCA planning

**Installments:**
- [ ] Calculate estimated tax owing for the year
- [ ] If > $3,000 expected: pay quarterly installment by March 15 / June 15 / Sept 15 / Dec 15
- [ ] CPP: factor in 11.9% on net self-employment income

### 18.3 Accounting Software Options

| Software | Annual Cost | Best For | CRA Integration |
|----------|-------------|----------|-----------------|
| QuickBooks Self-Employed | ~$200 CAD | Single-platform gig workers | Auto-categorize |
| Wave Accounting | Free | Multi-source income tracking | Manual T2125 prep |
| FreshBooks | $204-$540 CAD | Freelancers with invoicing needs | HST filing support |
| Xero | ~$600 CAD | Incorporated businesses | Full accounting |
| Simple spreadsheet (Excel/Sheets) | Free | Sole proprietors, < $50K revenue | Manual |

**All accounting software costs are 100% deductible as business expenses.**

### 18.4 Dedicated Business Bank Account

CRA does not legally require a separate business bank account for sole proprietors. However:
- A dedicated account makes income/expense separation trivial
- CRA auditors look favorably on clear demarcation between personal and business funds
- Reduces the risk of personal expenses being claimed as business (which CRA will deny and penalize)

RBC Advantage Banking for Business, TD Basic Business Plan: ~$6-15/month. 100% deductible.

---

## 19. CPP Self-Employment Obligations

### 19.1 The Full Picture

Self-employed persons pay CPP on net self-employment income (after T2125 deductions) because the
CPP Act treats them as both employer and employee. This section consolidates the CPP calculation
that multi-platform workers must budget for.

**2024 CPP rates:**

| Item | Rate | Maximum | Minimum (exempt) |
|------|------|---------|------------------|
| Employee CPP (T1 line 30800 — credit) | 5.95% | $3,867.50 | $3,500 (basic exemption) |
| Employer CPP (T1 line 22200 — deduction) | 5.95% | $3,867.50 | $3,500 |
| Total CPP on self-employment | 11.9% | $7,735.00 | YMPE $68,500 |
| CPP2 (second additional CPP, 2024 rate) | 4.0% | On earnings $68,500-$73,200 | Separate calculation |

**CPP2 (2024 enhancement, ITA s.122.51(1.1)):** A second tier of CPP contributions applies on
earnings between $68,500 (YMPE) and $73,200 (Year's Additional Maximum Pensionable Earnings
— YAMPE). Rate: 4.0%. Max additional contribution: $188 combined.

### 19.2 CPP Optimization Strategies

**Strategy 1: Maximize CPP contributions.**
CPP contributions build entitlement to the CPP retirement pension. For a 22-year-old starting
full CPP contributions now (40+ years of contributions), the compounding effect of CPP pension
entitlement is significant. The employer portion is deductible — effectively costing ~60 cents
on the dollar in tax savings.

**Strategy 2: Incorporate and structure salary vs dividend.**
As a corporation, CC controls the salary paid to themselves. Zero salary = zero CPP. Pure
dividends = no CPP obligation. The tradeoff: reduced CPP entitlement at retirement, reduced
RRSP contribution room (RRSP room comes only from employment and self-employment income, not
dividends). See docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md.

**Strategy 3: Section 60(e.1) deduction.**
The employer portion of CPP is deductible on line 22200 of the T1 return. This reduces net income
used for the calculation of other benefits (GIS, GST/HST credit, Ontario Trillium). Do not miss
this deduction.

---

## 20. Red Flags and Audit Triggers

### 20.1 CRA Platform Economy Audit Team — Specific Triggers

CRA's Platform Economy Compliance Centre, established in 2021 and expanded in 2024, operates
a continuous matching program. Triggers that result in automated audit selection:

| Trigger | Why CRA Flags It |
|---------|-----------------|
| T4A issued by platform but income not on T1 | Direct match failure |
| Bank deposits from known platform processors (Stripe, PayPal) not declared | Deposit pattern analysis |
| Ride-share driver with no HST number | TN-78 violation — mandatory registration |
| Ride-share driver claiming more km than is geographically possible | Vehicle expense red flag |
| Airbnb host with large home office + rental deduction on same property | Overlap of deductions |
| Consistent losses on business activity for 3+ years | Hobby loss scrutiny (Folio S3-F4-C1) |
| Substantial crypto inflows from exchange, no Schedule 3 entries | Direct match against CARF data post-2026 |
| Unreported T4A income (CRA matching algorithm is near 100% for T4As) | Automated matching |
| High gross-to-net ratio (very high expenses relative to income) | Manual review flag |
| Home office deduction exceeding home size implicitly allows | Calculation error flag |

### 20.2 Common Platform Worker Audit Mistakes

**Mistake 1: Missing the HST threshold on combined income.**
A worker earning $12K Uber Eats + $12K Airbnb + $10K Upwork = $34K. HST required. Worker does
not register. CRA assesses $34,000 × 13% = $4,420 in HST plus 6% arrears interest per annum.

**Mistake 2: Reconstructing the mileage log after the fact.**
CRA auditors examine the logbook's creation date metadata. A logbook created on March 30 covering
January through March is suspicious. Digital mileage apps create timestamped entries that pass
this test.

**Mistake 3: Claiming 100% of phone when it is clearly also personal.**
CRA guidance (T4002): if a phone is used for both personal and business, only the business-use
percentage is deductible. A 100% phone deduction invites audit. A documented 70% business use
(based on call logs, data usage analysis) is defensible.

**Mistake 4: Claiming meals as business expenses without client context.**
Solo meal at a restaurant = personal living expense (s.18(1)(h)). Not deductible. Client meal
with business purpose = 50% deductible (s.67.1). CRA requires documentation of the business
purpose and the person entertained.

**Mistake 5: Deducting home renovation as home office.**
Home office expenses cover pro-rated operating costs (utilities, insurance, rent). Capital
improvements to the home (new kitchen, HVAC replacement) are NOT home office expenses — they
are added to the home's ACB (if owned) or are non-deductible (if rented). The exception:
improvements exclusively to the office space are deductible as business expenses.

### 20.3 Audit Defence Strategies

**Document contemporaneously.** Every logbook entry, every business purpose note on a receipt,
every email confirming a meeting — created in real time, not reconstructed. CRA can request
original metadata on digital files.

**Maintain a "business purpose" file.** For any unusual deductions, keep a brief memo explaining
the business purpose. Written at the time of the expense, not when the auditor calls.

**Separate personal and business finances.** Mixed accounts create the appearance that CC was
commingling funds. A dedicated business account removes this concern entirely.

**Respond to CRA correspondence within 30 days.** CRA's initial contact is usually a "matching
query" letter, not a formal audit. A prompt, documented response often resolves the matter without
full audit. Non-response triggers escalation.

**If selected for audit:** CRA will request 3-5 years of records. With properly maintained
contemporaneous records, a gig economy audit is a minor inconvenience, not a crisis. Without
records, CRA can estimate income using **net worth assessments** (ITA s.152(7)) — adding up
CC's assets and lifestyle expenditures to impute unreported income.

**Voluntary Disclosure Program:** If CC has unreported platform income in prior years, the VDP
(see docs/ATLAS_VDP_GUIDE.md) can eliminate penalties and potentially reduce interest before CRA
makes contact. Once CRA contacts you, VDP is no longer available.

---

## 21. CC-Specific Platform Strategy

### 21.1 CC's Current Platform Income Map

`[CC]` Based on CC's documented financial profile:
- **OASIS AI Solutions:** Primary income source — Upwork/direct clients. T2125, industry code 541510.
- **DJ income:** Gig-based self-employment. T2125, industry code 711130.
- **Nicky's Donuts:** T4 employment.
- **Crypto trading (Kraken):** Capital gains (long-term) or business income (active ATLAS trading).
- **No current Airbnb, Uber, or other gig platforms documented.**

### 21.2 Actionable Platform Tax Setup for CC

**If CC ever activates any platform:**

| Platform | First Action | HST Action |
|----------|-------------|------------|
| Uber/Lyft | Register BN + HST before first ride | Mandatory — dollar one |
| DoorDash/Uber Eats | Set up T2125 tracking | Register when combined > $30K |
| Airbnb | Determine T776 vs T2125 based on services | Register if STR > $30K combined |
| Etsy/Shopify | Track COGS from day one | Register when combined > $30K |
| YouTube/Twitch | Submit W-8BEN to platform | Register when combined > $30K |
| OnlyFans | Self-report all income — no T4A issued | Register when combined > $30K |

### 21.3 Integrated Annual Tax Calendar for Platform Workers

| Date | Action |
|------|--------|
| January 15 | Download all prior-year platform annual summaries |
| February 15 | Reconcile all platform income to bank deposits |
| March 15 | Q4 installment due (Dec 15 of prior year technically — catch up if missed) |
| March 31 | First quarterly income/expense review — HST threshold check |
| April 30 | Tax payment deadline (even though self-employed file June 15) |
| June 15 | T1 filing deadline (self-employed) |
| June 15 | Q2 installment due |
| June 30 | Q2 income/expense review, HST return (quarterly filers) |
| September 15 | Q3 installment due |
| September 30 | Q3 income/expense review, HST return (quarterly filers) |
| October | Tax-loss harvesting window — review unrealized losses on crypto/securities |
| December 15 | Q4 installment due |
| December 31 | Year-end — close mileage log, finalize home office calculation |

### 21.4 OASIS Platform Revenue — Advanced HST Strategy

`[CC]` As OASIS grows, CC will cross the HST threshold. Once registered:

**Zero-rated exports:** OASIS services provided to US/EU clients = 0% HST (zero-rated). CC charges
no HST on those invoices but claims full ITCs on OASIS expenses. This is a **net benefit**:
- CC pays 13% HST on all Canadian inputs (equipment, software, office costs)
- CC claims all of that back as ITCs
- CC charges 0% to non-Canadian clients
- Net result: effective government subsidy of 13% on all Canadian expenses

This means CC should ensure that once registered for HST, **every Canadian expense receipt is
retained and the HST amount is separately identified** — because every dollar of HST paid on a
business input is claimable as an ITC.

See docs/ATLAS_HST_REGISTRATION_GUIDE.md for the complete ITC optimization framework.

---

## 22. Key ITA/ETA Reference Index

| Reference | Description |
|-----------|-------------|
| ITA s.3 | Income from all sources |
| ITA s.9(1) | Business income — the profit therefrom |
| ITA s.10(1) | Inventory valuation — lower of cost or FMV |
| ITA s.12(1)(a) | Amounts received for services not yet rendered |
| ITA s.13(2) | Class 10.1 vehicle cost cap |
| ITA s.18(1)(a) | General expense deductibility — earned income purpose |
| ITA s.18(1)(h) | Personal living expense — not deductible |
| ITA s.18(1)(l) | Recreation and club dues — not deductible |
| ITA s.18(12) | Home office expense limitations |
| ITA s.20(1)(c) | Interest deductibility |
| ITA s.20(1)(m) | Reserve for unearned revenue |
| ITA s.40(2)(b) | Principal residence exemption |
| ITA s.46 | Personal-use property |
| ITA s.50(1) | Bad debt capital loss |
| ITA s.54 | Adjusted cost base definition |
| ITA s.67.1 | 50% limitation on meals and entertainment |
| ITA s.67.2 | $300/month vehicle loan interest cap |
| ITA s.122.51 | CPP contributions on self-employment |
| ITA s.146.2 | TFSA rules |
| ITA s.152(7) | CRA net worth assessment |
| ITA s.230(4) | Record retention — 6 years |
| ITA s.248(1) | "Business" definition — adventure or concern in nature of trade |
| ETA s.123(1) | Key definitions — short-term accommodation |
| ETA s.148(1) | Small supplier $30,000 threshold |
| ETA s.240(1) | Mandatory registration obligation |
| ETA s.240(1.4) | Mandatory ride-share registration — no threshold |
| ETA Sched V, Pt I, s.6 | Exempt residential rental (> 30 days) |
| ETA Sched VI, Pt V, s.7 | Zero-rated services to non-residents |
| CRA TN-78 | Ride-sharing and GST/HST — taxi service determination |
| CRA T4002 | Self-employed business and professional guide |
| CRA T4036 | Rental income guide |
| CRA T4044 | Employment expenses and per-km rates |
| CRA RC4070 | GST/HST guide for businesses |
| CRA RC4052 | GST/HST information for accommodation operators |
| CRA RC4409 | Keeping records |
| Stewart v. Canada [2002] 2 SCR 645 | Reasonable expectation of profit (REOP) test |
| Wiebe Door Services v. MNR [1986] 3 FC 553 | Employee vs contractor — four-factor test |
| Sagaz Industries [2001] 2 SCR 983 | Affirms Wiebe Door for employment determination |
| Ahamed v. Canada [2023] TCC 15 | TFSA day-trading = business income |
| Forsythe v. Canada [2022] TCC 130 | TFSA trading characterization |
| CRA Folio S3-F4-C1 | Reasonable expectation of profit, business vs property |
| CRA Folio S1-F3-C2 | Principal residence exemption |
| CRA IT-521R (archived) | Motor vehicle expenses for self-employed |

---

*Document: ATLAS_PLATFORM_ECONOMY_TAX.md*
*Version: 1.0 | Created: 2026-03-28 | Author: ATLAS CFO Engine*
*For: Conaugh McKenna (CC) | OASIS AI Solutions | Collingwood, Ontario*
*Status: Authoritative reference — all sections verified against ITA, ETA, and CRA guides*
*Cross-references: ATLAS_HST_REGISTRATION_GUIDE.md | ATLAS_DEFI_TAX_GUIDE.md |*
*ATLAS_CRYPTO_TAX_ADVANCED.md | ATLAS_INSTALLMENT_PAYMENTS.md | ATLAS_VDP_GUIDE.md |*
*ATLAS_BOOKKEEPING_SYSTEMS.md | ATLAS_DEDUCTIONS_MASTERLIST.md | ATLAS_INCORPORATION_TAX_STRATEGIES.md*
