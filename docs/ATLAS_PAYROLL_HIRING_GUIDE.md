# ATLAS Canadian Payroll, Hiring & Contractor Management Guide

> **For:** Conaugh McKenna (CC), OASIS AI Solutions, Collingwood Ontario
> **Jurisdiction:** Canada (Ontario primary) | **Tax year:** 2025-2026 (planning)
> **Last Updated:** 2026-03-27
> **Purpose:** Definitive guide for hiring employees, engaging contractors, payroll compliance,
> equity compensation, termination obligations, and international hiring. Covers everything a
> Canadian business owner needs from first contractor to scaled team.
> All ITA references are to the *Income Tax Act (Canada)*, R.S.C. 1985, c.1 (5th Supp.).
> All ESA references are to the *Employment Standards Act, 2000*, S.O. 2000, c.41 (Ontario).
> All CPP references are to the *Canada Pension Plan*, R.S.C. 1985, c.C-8.
> All EI references are to the *Employment Insurance Act*, S.C. 1996, c.23.

**Tags used throughout:**
- `[NOW]` -- Actionable today as a sole proprietor at OASIS's current revenue
- `[FUTURE]` -- Relevant upon incorporation or significant revenue growth
- `[OASIS]` -- Specific to OASIS AI Solutions
- `[CRITICAL]` -- Compliance failure here triggers penalties, audits, or litigation
- `[SAVINGS]` -- Direct dollar impact or cost reduction opportunity

---

## Table of Contents

1. [Employee vs Contractor -- The Most Expensive Decision](#1-employee-vs-contractor--the-most-expensive-decision)
2. [Personal Services Business (PSB) -- The Nuclear Penalty](#2-personal-services-business-psb--the-nuclear-penalty)
3. [Canadian Payroll Obligations -- Complete Guide](#3-canadian-payroll-obligations--complete-guide)
4. [Payroll Processing Mechanics](#4-payroll-processing-mechanics)
5. [Hiring Process -- Legal Compliance](#5-hiring-process--legal-compliance)
6. [Employment Agreements -- What to Include](#6-employment-agreements--what-to-include)
7. [Contractor Management](#7-contractor-management)
8. [International Contractors and Foreign Hiring](#8-international-contractors-and-foreign-hiring)
9. [Benefits and Compensation Design](#9-benefits-and-compensation-design)
10. [Equity Compensation for Startups](#10-equity-compensation-for-startups)
11. [Termination and Severance](#11-termination-and-severance)
12. [Payroll Software Comparison](#12-payroll-software-comparison)
13. [International Hiring -- Full Employees Abroad](#13-international-hiring--full-employees-abroad)
14. [Compliance Calendar for Employers](#14-compliance-calendar-for-employers)
15. [CC-Specific Hiring Action Plan](#15-cc-specific-hiring-action-plan)
16. [Quick Reference Tables](#16-quick-reference-tables)
17. [Key Legislation Reference Index](#17-key-legislation-reference-index)

---

## 1. Employee vs Contractor -- The Most Expensive Decision

### Why This Matters

Getting worker classification wrong is the single most expensive compliance mistake a Canadian business owner can make. CRA can reassess **years** of payroll, making you liable for employer AND employee portions of CPP and EI -- retroactively, with interest and penalties. A single misclassified worker earning $70,000/year can trigger a $15,000-$25,000 reassessment.

### The CRA Four-Factor Test

CRA uses a framework derived from two landmark cases: **Wiebe Door Services Ltd. v. MNR (1986)** and **671122 Ontario Ltd. v. Sagaz Industries Canada Inc. (2001 SCC)**. No single factor is determinative -- CRA weighs the totality of the relationship.

#### Factor 1: Control

The most important factor. Asks: who decides **how**, **when**, and **where** the work is done?

| Indicator | Employee | Contractor |
|-----------|----------|------------|
| Work schedule | Payer sets hours | Worker sets own hours |
| Work location | Payer's office/site | Worker chooses |
| Method of work | Payer dictates process | Worker decides how to achieve result |
| Supervision | Direct oversight | Minimal -- deliverable-based |
| Exclusivity | Works only for payer | Multiple clients |
| Training | Payer provides training | Worker already skilled |
| Sequence of tasks | Payer dictates order | Worker decides |
| Right to subcontract | Worker cannot delegate | Worker can hire helpers |

**Key nuance:** It is the **right** to control that matters, not whether control is actually exercised. If you *could* dictate hours and methods, even if you don't, that points to employment.

**CC example:** If you hire a developer for OASIS and say "work on this feature, deliver by Friday, I don't care when or how you build it," that points to contractor. If you say "be online 9-5, attend our standups, use our branching strategy," that points to employee.

#### Factor 2: Ownership of Tools

Who provides the equipment, software licenses, office space, and infrastructure needed to do the work?

| Indicator | Employee | Contractor |
|-----------|----------|------------|
| Computer/hardware | Payer provides | Worker owns |
| Software licenses | Payer's accounts | Worker's accounts |
| Office space | Payer's office | Worker's home/office |
| Specialized equipment | Payer provides | Worker provides |
| Vehicle | Company vehicle | Own vehicle |
| Supplies/materials | Payer purchases | Worker purchases |

**For tech companies:** This factor has weakened somewhat because modern knowledge workers often own laptops and software subscriptions regardless. But if you provide GitHub seats, Figma licenses, Slack workspace, cloud infrastructure access -- that still leans employee.

**CC example:** OASIS contractor should use their own laptop, their own IDE licenses, their own internet. You provide access to the project repo and deployment credentials only.

#### Factor 3: Chance of Profit / Risk of Loss

Does the worker have a genuine financial stake in the outcome? Can they profit from efficiency or lose money on the engagement?

| Indicator | Employee | Contractor |
|-----------|----------|------------|
| Payment structure | Hourly/salary (time-based) | Fixed fee, project-based, milestones |
| Expenses | Payer reimburses | Worker absorbs |
| Financial risk | None -- gets paid regardless | Can lose money on a project |
| Ability to profit | Fixed compensation | Efficiency = more profit |
| Bad debts | N/A | Worker bears non-payment risk |
| Investment at risk | None | Equipment, training, marketing |
| Warranty/rework | Payer covers | Worker covers at own cost |

**The test:** If the worker is paid $50/hour regardless of output quality or project success, they have no risk of loss. If the worker quotes $5,000 for a project and it takes twice as long as estimated, they absorb the loss -- that is genuine financial risk.

**CC example:** Pay OASIS contractors per project or per milestone, not hourly. A fixed-fee contract for "build the authentication module, $3,000, delivered by March 30" is far stronger than "$75/hour, ~40 hours estimated."

#### Factor 4: Integration

Is the worker integral to the business, or are they providing an independent service that the business consumes?

| Indicator | Employee | Contractor |
|-----------|----------|------------|
| Business cards | Has company cards | Uses own branding |
| Email address | company@domain.com | worker@ownbusiness.com |
| Client-facing | Represents the company | Represents themselves |
| Continuity | Ongoing, indefinite | Project-based, defined end |
| Dependency | Business depends on them | Business contracts them as needed |
| Branding | Wears company brand | Own brand identity |

**Modern reality:** For SaaS companies, even contractors often need access to internal tools and repos. Integration analysis now focuses more on whether the worker is economically dependent on your business (one client = employee-like) or genuinely independent (multiple clients, own brand, own marketing).

### The Overall Test: Whose Business Is It?

The Supreme Court in *Sagaz* boiled it down to one question: **"Whose business is it?"**

- Is the worker performing services **as a person in business on their own account**?
- Or is the worker performing services **as an employee of the payer's business**?

If the worker has their own business name, their own website, their own clients, their own insurance, invoices you with HST, and could replace themselves with a subcontractor -- they are in business for themselves. That is a contractor.

If the worker shows up, does what you say, uses your stuff, gets paid by the hour, and has no other clients -- they are your employee regardless of what the contract says.

### `[CRITICAL]` The Contract Does Not Override Reality

A written contract labeling someone as an "independent contractor" is **necessary but not sufficient**. CRA and the courts look at the **actual working relationship**, not the contractual label. If the reality looks like employment, a contractor agreement will not save you.

The contract matters as evidence of **mutual intent**, but intent is only one factor weighed against the operational reality.

### Requesting a CRA Ruling: Form RC4110

If you are uncertain about a worker's status:

1. Either the payer or the worker can request a ruling
2. File **CPT1** (Request for a Ruling as to the Status of a Worker under CPP/EI)
3. CRA will investigate and issue a binding ruling
4. Appeal: within 90 days to the Tax Court of Canada
5. **Do this BEFORE engaging the worker if possible** -- retroactive rulings are painful

**When to request a ruling:**
- Long-term engagement (6+ months) with a single worker
- Worker has no other clients
- You are providing significant tools/equipment
- Payment is hourly rather than project-based
- Any of the four factors are borderline

### `[CRITICAL]` Consequences of Misclassification

If CRA determines your "contractor" is actually an employee:

| Consequence | Impact |
|-------------|--------|
| CPP -- employer portion | Retroactive: 5.95% on all pensionable earnings, all years |
| CPP -- employee portion | You owe this too if you didn't withhold (s.21(1) CPP Act) |
| CPP2 -- both portions | Additional contributions on earnings between YMPE and YAMPE |
| EI -- employer portion | Retroactive: 2.212% (1.4x employee rate) on all insurable earnings |
| EI -- employee portion | You owe this if you didn't withhold |
| Income tax | No retroactive liability (worker filed their own taxes), but T4 amendment required |
| Penalty | 10% of amounts that should have been withheld but were not (s.227(8) ITA) |
| Interest | Prescribed rate compounded daily from the date amounts were due |
| WSIB | Retroactive premiums + potential penalties for non-registration |
| Worker claims EI | Worker may now be eligible for Employment Insurance benefits |
| Repeated failure | 20% penalty (s.227(9) ITA) for second or subsequent failures |

**Dollar example:** Contractor paid $80,000/year for 3 years. Misclassified.
- CPP employer: ~$4,100/year x 3 = $12,300
- CPP employee (you owe): ~$4,100/year x 3 = $12,300
- EI employer: ~$1,450/year x 3 = $4,350
- EI employee (you owe): ~$1,035/year x 3 = $3,105
- 10% penalty: ~$3,200
- Interest: ~$2,000-$4,000
- **Total exposure: $37,000-$39,000** -- on a single worker

### Safe Harbor Practices Checklist

To protect a contractor classification, ensure ALL of the following:

- [ ] Written independent contractor agreement (not employment agreement)
- [ ] Worker has **multiple clients** (ideally 3+, documented)
- [ ] Worker provides **own tools** (laptop, software, office)
- [ ] Worker sets **own schedule** (no set hours, no attendance requirements)
- [ ] Payment is **project-based or milestone-based** (not hourly or salaried)
- [ ] Worker has a **registered business** (sole prop or corporation)
- [ ] Worker **invoices** with HST/GST (if registered)
- [ ] Worker can **subcontract** or delegate the work
- [ ] Worker has **own business insurance** (errors & omissions)
- [ ] Worker is **not integrated** into your org chart (no company email, no team meetings requirement)
- [ ] Engagement has a **defined scope and end date** (not indefinite)
- [ ] Worker bears **financial risk** (rework at own cost, fixed-fee overruns)

**Minimum for reasonable safety:** At least 8 of 12 should be clearly satisfied.

---

## 2. Personal Services Business (PSB) -- The Nuclear Penalty

### What Is a PSB?

A Personal Services Business (s.125(7)(d) ITA) exists when:

1. A corporation provides services to another entity (the "payer")
2. The person performing the services (the "incorporated employee") would reasonably be considered an **employee** of the payer if not for the existence of the corporation
3. The incorporated employee does not employ more than 5 full-time employees throughout the year
4. The services are not provided to an **associated corporation**

In plain English: you incorporated yourself to look like a contractor, but the actual working relationship is employment. CRA looks through the corporate veil.

### PSB Tax Consequences -- Devastating

| Item | Regular CCPC | PSB Corporation |
|------|-------------|-----------------|
| Small Business Deduction | Yes (12.2% federal on first $500K) | **NO** |
| General Rate Reduction | Yes (13% federal reduction) | **NO** |
| Effective federal rate | ~9% (SBD) or ~15% (general) | **~33%** (full Part I rate) |
| Combined federal + Ontario | ~12.2% (SBD) or ~26.5% (general) | **~44.5%** |
| Deductions allowed | All reasonable business expenses | **ONLY:** salary/wages to incorporated employee, benefits, and amounts the incorporated employee would have been able to deduct under s.8 ITA |
| Home office deduction | Yes | **NO** |
| Equipment/CCA deduction | Yes | **NO** (unless it would be deductible as employee expense) |
| Advertising, marketing | Yes | **NO** |
| Subcontractor costs | Yes | **NO** |
| Professional development | Yes | **NO** |

**The devastation:** Not only is the tax rate nearly 4x higher than the SBD rate, but you lose almost every deduction that makes incorporation attractive. You can only deduct salary paid to the incorporated employee and their benefits. Everything else is non-deductible.

### How to Avoid PSB Classification

The five-employee exception is one path, but impractical for most small businesses. The real defense is ensuring the relationship genuinely is **not** employment:

1. **Multiple clients:** The incorporated worker provides services to several unrelated entities (strongest single factor)
2. **Own tools:** The corporation provides its own equipment, software, and workspace
3. **Control:** The corporation controls how, when, and where the work is done
4. **Financial risk:** The corporation bears risk of loss on projects (fixed-fee contracts)
5. **Ability to subcontract:** The corporation can (and ideally does) hire others to help deliver

**The gold standard:** If your corporation has 3+ unrelated clients, uses its own tools, bills project-based, and has the right to subcontract -- PSB risk is very low.

### `[OASIS]` CC's PSB Risk Assessment

When CC incorporates OASIS and takes on client projects:
- If OASIS has only ONE client and CC works full-time for them using their tools = **HIGH PSB RISK**
- If OASIS has 3+ clients, CC uses own equipment, bills per project = **LOW PSB RISK**
- Action: Always maintain at least 2-3 active client relationships after incorporation

---

## 3. Canadian Payroll Obligations -- Complete Guide

### Employer Registration with CRA

Before paying your first employee, you must register for a payroll account:

1. **Business Number (BN):** If you already have one (from HST or income tax), you add a payroll program account (RP extension)
2. **New BN:** Register via CRA My Business Account, by phone (1-800-959-5525), or Form RC1
3. **Program account:** Your payroll account number format is `123456789 RP 0001`
4. **Timeline:** Register before the first pay date -- CRA needs time to set up your account
5. **Multiple payroll accounts:** You may need separate RP accounts for different worker groups (rare for small businesses)

### `[CRITICAL]` CPP Contributions (2026 Rates)

The Canada Pension Plan has two tiers since 2024:

**CPP1 (Base):**
| Item | 2026 Amount |
|------|-------------|
| Basic exemption | $3,500 |
| Year's Maximum Pensionable Earnings (YMPE) | ~$73,200 |
| Pensionable earnings range | $3,500 to ~$73,200 |
| Employee contribution rate | 5.95% |
| Employer contribution rate | 5.95% (matches employee) |
| Maximum employee contribution | ~$4,148 |
| Maximum employer contribution | ~$4,148 |
| Self-employed rate | 11.90% (both portions) |
| Maximum self-employed contribution | ~$8,296 |

**CPP2 (Enhanced -- Second Ceiling):**
| Item | 2026 Amount |
|------|-------------|
| Year's Additional Maximum Pensionable Earnings (YAMPE) | ~$81,300 |
| Earnings range for CPP2 | ~$73,200 to ~$81,300 |
| Employee contribution rate | 4.00% |
| Employer contribution rate | 4.00% (matches employee) |
| Maximum employee CPP2 contribution | ~$324 |
| Maximum employer CPP2 contribution | ~$324 |
| Self-employed CPP2 rate | 8.00% (both portions) |
| Maximum self-employed CPP2 contribution | ~$648 |

**Who is exempt from CPP:**
- Workers under 18
- Workers 65-70 who elect out (Form CPT30)
- Workers 70+ (mandatory exemption)
- Casual employment not in the course of the payer's business
- Certain Indigenous employment on reserves (specific conditions)

**Employer obligation:** Calculate, withhold employee portion from each pay, match it with employer portion, remit both to CRA.

### `[CRITICAL]` Employment Insurance (EI) Premiums (2026 Rates)

| Item | 2026 Amount |
|------|-------------|
| Maximum insurable earnings | ~$65,700 |
| Employee premium rate | 1.58% |
| Maximum employee premium | ~$1,038 |
| Employer premium rate | 1.4x employee rate = 2.212% |
| Maximum employer premium | ~$1,453 |
| Employer cost per employee | 40% more than employee pays |

**EI premium reduction:** Employers who provide a short-term disability plan that meets EI standards can apply for a premium reduction (typically 5/12 of 5% = ~$25-$50/employee/year savings). Not worth the paperwork for most small businesses.

**Self-employed EI:** Sole proprietors can opt into EI for **special benefits only** (maternity, parental, sickness, compassionate care, family caregiver). You do NOT get regular EI (job loss) benefits. Opt in via My Business Account. Once opted in, you cannot opt out until you have not been self-employed for 12+ months.

### Income Tax Withholding

Every pay period, you must withhold federal and Ontario provincial income tax:

1. **TD1 Form:** Each employee completes federal TD1 and Ontario TD1ON upon hire
   - Claims personal tax credits (basic personal amount, spouse, dependants, disability, tuition)
   - Determines which withholding rate to apply
   - Employee must file new TD1 if circumstances change (marriage, new child, etc.)
   - If no TD1 filed, withhold as if basic personal amount only

2. **How to calculate withholding:**
   - **CRA Payroll Deductions Online Calculator (PDOC):** Free, accurate, updated annually -- use this
   - **CRA Payroll Deductions Tables (T4032):** Published annually by province
   - **Formula method:** CRA publishes T4127 (Payroll Deductions Formulas) for software developers
   - **Payroll software:** Automates all of this (strongly recommended)

3. **Combined marginal rates (Ontario 2026):**

   | Taxable Income | Federal Rate | Ontario Rate | Combined |
   |----------------|-------------|-------------|----------|
   | $0 - $57,375 | 15% | 5.05% | 20.05% |
   | $57,375 - $59,906 | 20.5% | 5.05% | 25.55% |
   | $59,906 - $79,880 | 20.5% | 9.15% | 29.65% |
   | $79,880 - $95,259 | 20.5% | 11.16% | 31.66% |
   | $95,259 - $114,750 | 26% | 11.16% | 37.16% |
   | $114,750 - $150,000 | 26% | 12.16% | 38.16% |
   | $150,000 - $173,205 | 29% | 12.16% | 41.16% |
   | $173,205 - $220,000 | 29% | 13.16% | 42.16% |
   | $220,000 - $246,752 | 33% | 13.16% | 46.16% |
   | $246,752+ | 33% | 13.16% | 46.16% |

   *Note: Ontario surtax applies at higher incomes, effectively increasing provincial rates. These are approximate combined rates for withholding guidance.*

### WSIB (Workplace Safety and Insurance Board -- Ontario)

| Item | Details |
|------|---------|
| Mandatory? | Yes for most industries (Schedule 1 and Schedule 2 employers) |
| Tech/SaaS companies | Generally mandatory, classified under "Computer Systems Design" (NAICS 5415) |
| Premium rate | Varies by industry: tech ~$0.24-$0.36 per $100 of insurable earnings |
| Annual cost example | $70K salary x 0.30% = ~$210/year per tech employee |
| Executive directors | Mandatory coverage if they perform work for the business |
| Sole proprietor (no employees) | Optional -- can purchase Voluntary Personal Coverage |
| Registration | Register within 10 days of hiring first employee |
| Reporting | Annual reconciliation (Form 7) due March 31 |
| Penalties | Failure to register: premiums back-assessed + 100% surcharge |

**When to register:** Before the first employee's first day. You can register online at wsib.ca.

**Independent operators (IT):** If you hire contractors who are true independent operators, they are not covered by your WSIB policy. However, if CRA or WSIB reclassifies them as employees, you owe retroactive premiums.

### EHT (Employer Health Tax -- Ontario)

| Item | Details |
|------|---------|
| What it is | Ontario payroll tax to fund provincial health care |
| Small business exemption | First $1,000,000 of payroll is exempt (if total payroll < $5M) |
| Rate | 1.95% on payroll exceeding the exemption |
| CC relevance | **None until payroll exceeds $1M** -- irrelevant for early-stage OASIS |
| Associated employer rules | Connected corporations share the $1M exemption |
| Filing | Annual return, monthly instalments if >$600K payroll |

**Bottom line:** Not relevant until OASIS has 10-15+ employees. Ignore until then.

---

## 4. Payroll Processing Mechanics

### Pay Period Options

| Pay Period | Frequency | Common For | Notes |
|------------|-----------|------------|-------|
| Weekly | 52/year | Hourly workers, construction | Higher admin cost |
| Bi-weekly | 26/year | Most common in Canada | Every 2 weeks (not twice a month) |
| Semi-monthly | 24/year | Salaried employees | 1st and 15th of each month |
| Monthly | 12/year | Senior executives | Lowest admin cost, employees may not like waiting |

**Ontario ESA requirement:** Wages must be paid on a regular pay day, at least monthly. Most businesses choose bi-weekly or semi-monthly.

**Recommendation for OASIS:** Semi-monthly (1st and 15th). Clean, predictable, easy to align with accounting periods.

### Pay Stub Requirements (Ontario)

Every pay period, you must provide a **written statement** (physical or electronic) showing:

- [ ] Pay period start and end dates
- [ ] Gross earnings (regular + overtime + any other)
- [ ] Each deduction itemized with description and amount:
  - Federal income tax
  - Provincial income tax
  - CPP (employee portion)
  - CPP2 (employee portion, if applicable)
  - EI (employee portion)
  - Any voluntary deductions (benefits, RRSP, union dues)
- [ ] Net pay (amount deposited)
- [ ] Year-to-date totals for all of the above
- [ ] Vacation pay accrued (if tracked separately)

### Statutory Holiday Pay (Ontario)

Ontario's 9 public holidays:
1. New Year's Day
2. Family Day (3rd Monday in February)
3. Good Friday
4. Victoria Day
5. Canada Day
6. Labour Day
7. Thanksgiving Day
8. Christmas Day
9. Boxing Day

**Calculation for holiday pay:**
- Regular wages earned in the 4 work weeks before the holiday, divided by 20
- If employee works on the holiday: premium pay (1.5x for hours worked) + substitute day off, OR regular pay + premium pay for hours worked (employee choice not required -- employer determines which applies per policy)

### Vacation Pay and Entitlement (Ontario)

| Service Length | Vacation Time | Vacation Pay |
|---------------|---------------|-------------|
| < 5 years | 2 weeks minimum | 4% of gross wages |
| 5+ years | 3 weeks minimum | 6% of gross wages |

**Key rules:**
- Vacation pay accrues on ALL compensation (salary, commissions, bonuses)
- Must be paid before vacation begins, or on regular pay dates (if agreed)
- Cannot include vacation pay in regular pay rate without clear, written agreement
- Unused vacation pay must be paid out on termination
- Vacation time must be taken in complete weeks (unless employee agrees otherwise)
- Employer schedules vacation (with reasonable notice) -- employee does not have unilateral right to choose

### Overtime (Ontario)

| Item | Rule |
|------|------|
| Overtime threshold | 44 hours/week |
| Overtime rate | 1.5x regular rate |
| Averaging agreements | Allowed -- average over 2+ weeks (written agreement required) |
| Exempt employees | Managers/supervisors (ESA s.174, O.Reg. 285/01), IT professionals are NOT exempt in Ontario |
| Comp time | Allowed at 1.5 hours per OT hour, written agreement, taken within 3 months (or 12 months if agreed) |

**Critical note for tech companies:** Unlike in the US, there is NO "white-collar" overtime exemption for IT professionals in Ontario. Your developers earn overtime after 44 hours/week unless they are genuine managers/supervisors who do not perform non-managerial work.

### `[CRITICAL]` Payroll Remittance to CRA

You must remit withheld taxes, CPP, and EI to CRA on a schedule based on your average monthly withholding amount (AMWA):

| Remitter Type | AMWA | Due Date | Penalty if Late |
|---------------|------|----------|-----------------|
| Regular (new employer default) | < $25,000 | 15th of following month | 3% (1-3 days), 5% (4-5 days), 7% (6-7 days), 10% (7+ days) |
| Accelerated -- Threshold 1 | $25,000 - $99,999.99 | 25th for pay in first 15 days; 10th of following month for pay in last 15 days | Same penalty scale |
| Accelerated -- Threshold 2 | $100,000+ | Within 3 business days of pay date | Same penalty scale |

**New employer rule:** All new payroll accounts start as monthly remitters. CRA will reclassify you after reviewing your AMWA.

**Penalties stack:** If you fail to remit for multiple periods, penalties apply to each period separately. Interest compounds daily at the CRA prescribed rate.

**When to remit:** You can remit online via CRA My Business Account, through your bank (using your payroll account number), or via payroll software that auto-remits.

**`[SAVINGS]` Pro tip:** Remit on time, every time. A single late remittance triggers a penalty that likely exceeds the cost of payroll software for an entire year.

### Year-End Filing

| Filing | Deadline | What |
|--------|----------|------|
| T4 Summary + T4 slips | February 28 | All employees -- wages, deductions, benefits |
| T4A Summary + T4A slips | February 28 | All contractors paid > $500 |
| RL-1 (Quebec only) | February 28 | Quebec employees only |
| WSIB Form 7 | March 31 | Annual reconciliation of insurable earnings |

**T4 slip contents:**
- Box 14: Employment income
- Box 16: Employee CPP contributions
- Box 17: Employee CPP2 contributions
- Box 18: Employee EI premiums
- Box 22: Income tax deducted
- Box 24: EI insurable earnings
- Box 26: CPP pensionable earnings
- Box 40: Taxable benefits (if any)
- Box 44: Union dues
- Box 46: Charitable donations (if payroll deducted)
- Various other boxes for specific situations

**Electronic filing:** Mandatory if filing 6+ T4 slips. Use CRA Internet File Transfer (XML) or payroll software.

### Record of Employment (ROE)

| Item | Rule |
|------|------|
| When to file | Within 5 calendar days of an interruption of earnings |
| How to file | Electronically via ROE Web (mandatory for most employers) |
| Interruption of earnings | Termination, layoff, leave (maternity, parental, sick), reduced hours below 60% |
| Block 15A | Total insurable hours |
| Block 15B | Total insurable earnings |
| Reason code | Most common: K (other), M (dismissal), E (quit), N (leave), A (shortage of work) |
| Penalty for late/incorrect | Up to $2,000 per offence + employee may experience EI benefit delays |

**Why it matters:** The ROE determines your former employee's EI eligibility and benefit amount. Filing late or with incorrect information delays their benefits and exposes you to penalties.

---

## 5. Hiring Process -- Legal Compliance

### Job Posting Compliance

**Ontario Human Rights Code (OHRC)** prohibits discrimination in hiring on these grounds:
- Race, colour, ethnic origin, ancestry, place of origin, citizenship
- Creed (religion)
- Sex, sexual orientation, gender identity, gender expression
- Age (18-65 for employment)
- Marital/family status
- Disability (physical or mental)
- Record of offences (provincial -- pardoned offences only)

**What this means for job postings:**
- No "must be under 35" or "energetic young professional" (age discrimination)
- No "must have Canadian experience" (ancestry/place of origin discrimination -- OHRT case law)
- No "must be available Sundays" unless bona fide occupational requirement (creed discrimination)
- "Must be legally entitled to work in Canada" is permitted
- Language requirements must be justified by job duties

**Pay transparency (Ontario):** As of 2026, Ontario requires posting expected salary ranges for publicly advertised positions. Include a range (e.g., "$70,000 - $85,000") in your postings.

### Interview Compliance

**Prohibited questions** (you cannot ask, directly or indirectly):

| Topic | Cannot Ask | Can Ask |
|-------|-----------|---------|
| Age | "How old are you?" / "When did you graduate?" | "Are you legally entitled to work in Canada?" |
| Family | "Do you have children?" / "Are you planning to get pregnant?" | Nothing -- not relevant to ability to do the job |
| Religion | "What church do you attend?" / "Can you work Saturdays?" | "This role requires Saturday availability -- can you meet that requirement?" (bona fide) |
| Disability | "Do you have any disabilities?" / "How many sick days did you take?" | "Can you perform the essential duties of this position?" / "Do you require accommodation?" |
| Criminal record | "Have you ever been arrested?" | "Have you been convicted of a criminal offence for which a pardon has not been granted?" (and only if relevant to the job) |
| National origin | "Where are you from?" / "What is your first language?" | "Are you legally authorized to work in Canada?" |
| Marital status | "Are you married?" / "What does your spouse do?" | Nothing -- irrelevant |

**Background checks:**
- Written consent required before conducting any check
- Criminal record checks: permitted when relevant to the position (e.g., working with vulnerable persons, handling money)
- Credit checks: only when directly relevant to the role (financial positions)
- Reference checks: standard practice, get consent
- Social media screening: legal grey area -- do it before knowing protected characteristics, document the process

### Offer Letter vs Employment Contract

| Document | Purpose | Binding? |
|----------|---------|----------|
| Offer letter | Initial conditional offer with key terms | Yes, once accepted (forms the initial contract) |
| Employment contract | Comprehensive legal agreement | Yes, and supersedes offer letter |

**Best practice:** Send offer letter first (conditional on references/background check), then have the full employment agreement signed **before the first day of work**. If signed after work begins, it may lack fresh consideration and be unenforceable for restrictive terms.

### Probationary Period

| Item | Rule |
|------|------|
| ESA minimum notice | No notice or severance required for first 3 months of employment |
| After 3 months | 1 week notice minimum (ESA) |
| Common law | Probationary clauses are enforceable if clear and signed before start |
| Typical length | 3-6 months |
| Best practice | 3 months (aligns with ESA) -- extend to 6 months for complex roles |
| Termination during probation | Must still not be discriminatory or in bad faith |

---

## 6. Employment Agreements -- What to Include

### Essential Clauses

Every employment agreement for OASIS (or any Canadian tech company) should include:

#### 1. Parties and Start Date
- Full legal name of employer (corporation) and employee
- Start date
- Reporting relationship

#### 2. Position and Duties
- Job title and description of core responsibilities
- "Such other duties as may be reasonably assigned" (flexibility clause)
- Full-time vs part-time, hours per week
- Remote/hybrid/in-office expectations

#### 3. Compensation
- Base salary (annual amount, pay frequency)
- Bonus (if any): formula or discretionary, timing, pro-ration rules
- Equity (if any): reference to separate stock option agreement
- Commission (if any): detailed commission plan as schedule
- Salary review: annual review (not guarantee of increase)
- Expense reimbursement policy

#### 4. Benefits
- Reference to group benefits plan (details in separate plan document)
- Health Spending Account (HSA) allocation
- RRSP matching (if any)
- Paid time off beyond statutory minimums

#### 5. `[CRITICAL]` Termination Provisions
- **Must meet or exceed ESA minimums** -- any clause providing less is void
- Specify: "The Company may terminate employment without cause by providing X weeks notice or pay in lieu, per the following schedule..."
- Common approach: mirror ESA minimums in the contract to **limit** common law reasonable notice
- Without a termination clause, courts award common law notice: roughly **1 month per year of service** (can be 18-26 months for senior/long-service employees)
- **Waksdale v. Swegon (2020 ONCA):** If ANY part of the termination clause is unenforceable (e.g., the just cause section violates ESA), the ENTIRE termination clause is void -- employee gets common law notice
- **Best practice:** Have an employment lawyer draft/review your termination clause. This is the most litigated clause in Canadian employment law.

#### 6. `[CRITICAL]` Intellectual Property Assignment
- "All work product, inventions, code, designs, and intellectual property created by the Employee in the course of employment or using Company resources shall be the sole and exclusive property of the Company"
- Include: pre-existing IP carve-out (employee lists their existing IP that is excluded)
- Include: moral rights waiver (Copyright Act, s.14.1)
- **For tech companies, this clause is non-negotiable.** Without it, the employee may have a claim to code they wrote.

#### 7. Confidentiality
- Definition of confidential information (broad)
- Obligation survives termination (indefinitely for trade secrets)
- Return of materials upon termination
- No social media posting of confidential information

#### 8. Restrictive Covenants

| Covenant | Enforceable in Ontario? | Notes |
|----------|------------------------|-------|
| Non-compete | **NO** (banned by Working for Workers Act, 2021, effective Oct 25, 2021) | Exception: C-suite executives (CEO, CFO, COO, etc.) and sale of business |
| Non-solicitation (clients) | Maybe -- must be reasonable in scope, geography, and duration | 12 months, specific client list = more enforceable |
| Non-solicitation (employees) | Maybe -- courts are more lenient here | 12-18 months is typical |
| Non-disparagement | Generally enforceable | Mutual is best practice |
| Garden leave | Enforceable if structured as notice period | Employee is paid, remains employed, but stays home |

**Ontario non-compete ban:** Since October 2021, non-competition agreements are **void** for most employees. Only enforceable for:
- C-suite executives
- Sale of a business (vendor non-compete)

**What to use instead:** Well-drafted non-solicitation (clients + employees) + confidentiality + IP assignment. Together these protect most of what a non-compete would.

#### 9. Other Standard Clauses
- Governing law (Ontario)
- Entire agreement (supersedes prior discussions)
- Severability (if one clause is void, others survive)
- Amendment (in writing only)
- Notice provisions
- Statutory compliance language ("any provision that violates ESA minimums is deemed amended to meet ESA")
- Independent legal advice acknowledgment

### Remote Worker Considerations

**Which province's ESA applies?**

The general rule: the employment standards legislation of the **province where the employee ordinarily performs work** applies, regardless of where the employer is located.

| Employee Location | Applicable ESA | Implication |
|-------------------|---------------|-------------|
| Ontario | Ontario ESA | Standard |
| British Columbia | BC ESA | Different OT rules (8 hrs/day), different notice periods |
| Alberta | Alberta ESA | Different OT (8 hrs/day, 44/week), different holiday pay |
| Quebec | Quebec Labour Standards Act + Civil Code | Entirely different regime -- psychological harassment, language requirements, distinctive notice/severance |
| Outside Canada | Complex -- may not apply | Employment standards of the worker's country may apply |

**OASIS recommendation:** If possible, limit initial hires to Ontario residents to avoid multi-provincial compliance complexity. If hiring across provinces, get province-specific legal advice.

---

## 7. Contractor Management

### Written Contractor Agreement -- Essential Clauses

Every contractor engagement for OASIS should have a signed agreement containing:

#### 1. Relationship Definition
- "The Contractor is an independent contractor and not an employee, agent, or partner of the Company"
- "Nothing in this agreement creates an employment relationship"
- "The Contractor is responsible for their own taxes, CPP, and EI"

#### 2. Scope of Work
- Detailed description of deliverables (as a schedule/SOW)
- Acceptance criteria for each deliverable
- Change order process for scope changes
- Timeline and milestones

#### 3. Compensation
- Fixed fee per project/milestone, OR hourly/daily rate with cap
- Payment terms: Net-15 or Net-30 from invoice date
- Invoice requirements: date, description, hours (if hourly), HST/GST (if registered), payment instructions
- No expense reimbursement (unless explicitly agreed -- strengthens contractor status)
- Currency (CAD unless specified)

#### 4. `[CRITICAL]` Intellectual Property
- "All work product created under this agreement is a 'work made for hire' and is the exclusive property of the Company"
- Canadian copyright note: "work made for hire" is not a statutory concept in Canada like it is in the US. Use: "The Contractor hereby assigns all right, title, and interest in and to any work product..."
- Moral rights waiver (Copyright Act s.14.1)
- Pre-existing IP license: contractor grants license to use any pre-existing components incorporated into deliverables

#### 5. Confidentiality
- Same as employment agreement: broad definition, survives termination, return of materials
- Particularly important for contractors who may work with competitors

#### 6. Non-Solicitation
- Contractor will not solicit Company's clients or employees for 12 months after engagement ends
- More enforceable for contractors than employees (commercial agreement, not employment)

#### 7. Termination
- Either party can terminate with X days notice (30 days is standard)
- Payment for work completed to date
- Return of materials and access revocation upon termination
- Survival clauses: IP, confidentiality, non-solicitation survive termination

#### 8. Indemnification and Liability
- Contractor indemnifies Company against third-party claims arising from contractor's work
- Limitation of liability: typically capped at fees paid under the agreement
- Contractor carries own insurance (errors & omissions, general liability)

#### 9. Contractor Status Maintenance
- "Contractor will maintain multiple clients throughout the engagement" (yes, you can contractually require this)
- "Contractor will provide own tools and workspace"
- "Contractor determines their own work schedule and methods"
- These clauses reinforce the contractor relationship if CRA ever questions it

### T4A Reporting

| Item | Rule |
|------|------|
| When required | If you pay a contractor > $500 in a calendar year for services |
| What to report | Fees for services (Box 048) |
| Filing deadline | February 28 of the following year |
| Provide to contractor | By last day of February |
| HST included? | No -- report the pre-tax amount (fees only, not HST) |
| Penalty for late filing | $100-$7,500 depending on number of slips and how late |

**Important:** You do NOT need the contractor's SIN to pay them. But you need it for T4A reporting. Get it at the start of the engagement. If the contractor refuses to provide their SIN, you can still file the T4A -- CRA will match it later.

### Contractor Payment Best Practices

1. **Never pay cash** -- always bank transfer, e-transfer, or cheque (paper trail)
2. **Keep all invoices** -- required for your expense deduction
3. **Track HST/GST separately** -- claim ITCs if you are HST-registered
4. **No withholding** -- contractor handles their own income tax, CPP, and EI
5. **1099 vs T4A:** If paying a US contractor for work performed outside Canada, you do NOT issue a T4A. No Canadian reporting required. (The US contractor reports it on their US taxes.)
6. **Written contract before work begins** -- never start without a signed agreement

---

## 8. International Contractors and Foreign Hiring

### Regulation 105 Withholding (Services Rendered in Canada)

When a non-resident performs services **in Canada**, the payer must withhold **15%** of the gross payment and remit to CRA.

| Scenario | Withholding Required? |
|----------|----------------------|
| US contractor works remotely from New York | **No** -- services performed outside Canada |
| US contractor flies to Toronto for 2-week project | **Yes** -- 15% on the portion for services in Canada |
| UK contractor works remotely from London | **No** -- services performed outside Canada |
| Contractor from any country, works in Canada | **Yes** -- 15% |

**Waiver:** The non-resident can apply for a Reg 105 waiver (Form R105) if they will have no Canadian tax liability (e.g., treaty protection). CRA typically takes 30-60 days to process.

**Treaty override:** Canada has tax treaties with 90+ countries. Many treaties exempt short-term service income if the non-resident has no Permanent Establishment in Canada and is present for fewer than 183 days. But the **payer's obligation to withhold still applies** unless a waiver is obtained -- the treaty protects the non-resident, not you.

### Paying US Contractors

| Situation | Action |
|-----------|--------|
| US person, works from US, no Canadian presence | Pay gross, no withholding, no T4A |
| US corporation, services performed in US | Pay gross, no withholding, no T4A |
| US person, travels to Canada to perform some work | 15% withholding on Canada-sourced portion (Reg 105) |
| US person, no work in Canada, but you want CRA documentation | Issue T4A-NR (optional but recommended for large amounts) |

**Currency:** Pay in USD or CAD as negotiated. Track exchange rates for your expense deduction.

**W-8BEN:** You may request a US contractor complete IRS Form W-8BEN to certify their non-resident status. This protects you if CRA questions whether you should have withheld.

### Paying EU/International Contractors

Same principles as US contractors:
- Services performed entirely outside Canada = no Canadian withholding
- Services performed in Canada = 15% Reg 105 withholding
- Always check if a tax treaty applies (reduced withholding or exemption)

**Platforms for international contractor payments:**
| Platform | Cost | Best For |
|----------|------|----------|
| Wise (TransferWise) | 0.4-1.5% FX fee | Direct bank transfers, best rates |
| Payoneer | 1-2% FX fee | Popular with international freelancers |
| Deel | $49/contractor/month | Compliance, contracts, payments bundled |
| Remote | $29/contractor/month | Similar to Deel, slightly cheaper |
| Oyster | $29/contractor/month | Good for contractor-to-employee conversion |
| PayPal | 2.5-4% fees | Easy but expensive, no compliance features |

**OASIS recommendation:** Wise for simple international payments. Deel if you want compliance documentation and localized contracts.

### Permanent Establishment (PE) Risk

If your contractor (or employee) in a foreign country constitutes a "Permanent Establishment" for tax purposes, your Canadian corporation may have a tax filing obligation in that country.

**PE risk factors:**
- Worker has authority to conclude contracts on your behalf
- Worker has a fixed office that is at your disposal
- Long-term presence (usually 6+ months)

**How to avoid PE:**
- Contractor acts independently (not as your agent)
- Contractor has no authority to bind your company
- Keep engagements under 6 months where possible
- Use "services PE" thresholds in tax treaties (often 183 days in any 12-month period)

---

## 9. Benefits and Compensation Design

### Hierarchy of Benefits (Build Up as You Scale)

#### Stage 1: Sole Proprietor / First Contractor `[NOW]`
- No benefits obligations to contractors
- CC: use personal HSA through incorporated business (after incorporation)

#### Stage 2: First Employee `[FUTURE -- 1-3 employees]`
- Statutory minimums: CPP, EI, vacation pay, statutory holidays
- Optional: Health Spending Account ($1,000-$3,000/year per employee)
- Optional: Home office / equipment allowance
- Cost: $500-$3,000/year above statutory minimums per employee

#### Stage 3: Small Team `[FUTURE -- 3-10 employees]`
- Group health/dental insurance: $100-$200/employee/month for basic
- Health Spending Account (HSA): $1,500-$5,000/year
- Group RRSP with employer matching (3-5% of salary)
- Extended paramedical (massage, physio, chiro)
- Cost: $3,000-$8,000/year per employee above salary

#### Stage 4: Scaling `[FUTURE -- 10+ employees]`
- Comprehensive group benefits: $200-$400/employee/month
- HSA: $3,000-$10,000/year
- Group RRSP: 5% match
- Life insurance and AD&D: 1-2x salary
- Short-term disability: 66% of salary for 15-17 weeks
- Long-term disability: 60-66% of salary
- Employee Assistance Program (EAP)
- Equity compensation (stock options)
- Cost: $8,000-$20,000/year per employee above salary

### Health Spending Account (HSA)

| Item | Details |
|------|---------|
| What it is | Employer-funded account for medical expenses not covered by provincial health or group benefits |
| Tax treatment -- employer | 100% tax-deductible business expense |
| Tax treatment -- employee | Not a taxable benefit (tax-free) |
| Annual limit | No statutory limit, but CRA expects "reasonable" -- $500 to $10,000 typical |
| Eligible expenses | Same as medical expense tax credit (ITA s.118.2): dental, vision, prescriptions, paramedical, orthotics, etc. |
| Unused balance | Typically use-it-or-lose-it annually (can allow 1-year carryforward) |
| Can owners use it? | Yes -- shareholders/owner-employees can participate (must offer to all employees in the class) |

**`[SAVINGS]` Why HSAs are powerful:** $5,000 through a salary bonus costs the employee ~$2,300 in tax (at 46%). $5,000 through an HSA costs $0 in tax. The employer deducts it either way. Net savings to the employee: $2,300.

**Providers:** Blendable, Benecaid, Olympia Benefits, League (now Telus Health)

### Group RRSP

| Item | Details |
|------|---------|
| Employer matching | Typically 3-5% of salary (100% match up to the cap) |
| Vesting | Immediate or 1-2 year cliff (forfeiture if they leave before vesting) |
| Tax treatment -- employer | 100% deductible when contributed |
| Tax treatment -- employee | Employer match is NOT taxable employment income (unlike bonus) |
| Payroll integration | Employee contributions via payroll deduction (reduces withholding at source) |
| Annual limit | Employee + employer cannot exceed RRSP contribution room |
| Administration | Group plan provider (Manulife, Sun Life, Canada Life, Wealthsimple Work) |
| Cost | Provider fees: 0.5-1.5% MER on plan assets + ~$500-$1,500/year admin |

**`[SAVINGS]` RRSP matching is the most tax-efficient compensation increase.** A 5% match on a $70K salary = $3,500/year. Employee pays no tax on the match (deferred until withdrawal). Employer deducts it. Compare to a $3,500 bonus: employee nets ~$1,900 after tax.

### Group TFSA

| Item | Details |
|------|---------|
| Employer matching | Less common but emerging (1-3% of salary) |
| Tax treatment -- employer | Deductible as compensation expense |
| Tax treatment -- employee | Employer contributions ARE taxable employment income |
| Advantage | Growth is tax-free; better than RRSP for lower-income employees |
| Providers | Same as Group RRSP providers |

### Taxable Benefits -- What Triggers a T4 Inclusion?

| Benefit | Taxable? | Box on T4 |
|---------|----------|-----------|
| Group health/dental premiums (employer-paid) | **No** (Ontario) -- not taxable in most provinces | N/A |
| HSA claims | **No** | N/A |
| Life insurance premiums (employer-paid) | **Yes** -- Group Term Life is taxable | Box 40 |
| Parking (employer-paid) | **Yes** -- if regular, reasonable value | Box 40 |
| Company car / car allowance | **Yes** -- standby charge + operating cost | Box 34 |
| Cell phone / internet (employer-paid plan) | **Yes** -- unless primarily for business | Box 40 |
| Cell phone / internet reimbursement (receipts) | **No** -- if reasonable, receipted, primarily business | N/A |
| Education / training | **No** -- if primarily benefits the employer | N/A |
| Gifts / awards | **No** -- up to $500/year (non-cash), + $500 for long-service (5+ year intervals) | Box 40 if over |
| Meals / entertainment | Generally **no** if occasional; **yes** if regular/daily | Depends |
| Home office equipment (lump sum) | **Yes** -- unless returned upon termination | Box 40 |
| Home office equipment (reimbursement with receipts) | **No** -- if reasonable and required for job | N/A |
| Fitness / wellness (employer-paid membership) | **Yes** | Box 40 |
| Transit pass | **No** (federal tax credit available to employee) | N/A |

**Key rule:** Reimbursement of receipted business expenses = not taxable. Flat allowances without accountability = taxable.

---

## 10. Equity Compensation for Startups

### Stock Options in a CCPC (s.7 ITA) -- The Canadian Advantage

Canada offers a **unique tax advantage** for stock options in Canadian-Controlled Private Corporations (CCPCs):

| Feature | CCPC (Canada) | US Company (409A) |
|---------|--------------|-------------------|
| Tax event | **Disposition** (sale of shares) | Exercise |
| Deferral | Unlimited until you sell | None (taxed at exercise) |
| 50% deduction (s.110(1)(d)) | Yes, if exercise price >= FMV at grant | N/A (US has different rules) |
| Effective tax rate on gain | ~24% (half the marginal rate) | Depends on holding period |
| $200K annual vesting limit | **CCPCs are exempt** | N/A |
| Cash-flow friendly | Very -- no tax until you sell for cash | Terrible -- tax at exercise with no cash |

**How CCPC stock options work:**
1. **Grant:** Company grants employee option to buy X shares at $Y (exercise price = FMV at grant)
2. **Vest:** Options vest over time (typically 4 years, 1-year cliff)
3. **Exercise:** Employee pays exercise price, receives shares -- **NO tax event** (CCPC only)
4. **Disposition:** Employee sells shares -- employment benefit taxed at this point
5. **Benefit calculation:** FMV at exercise - exercise price = employment benefit
6. **50% deduction:** If exercise price >= FMV at grant date, half the benefit is deducted (s.110(1)(d))
7. **Capital gain:** FMV at disposition - FMV at exercise = capital gain (50% inclusion)

**Dollar example:**
- Grant: 10,000 options at $1.00 (FMV at grant = $1.00)
- Exercise: shares now worth $5.00 each -- exercise all for $10,000
- Employment benefit: ($5.00 - $1.00) x 10,000 = $40,000
- 50% deduction: $20,000 deducted from income
- Taxable employment benefit: $20,000
- Tax at 30% marginal rate: $6,000
- Later sell at $10.00/share: capital gain = ($10.00 - $5.00) x 10,000 = $50,000
- Taxable capital gain (50% inclusion): $25,000
- Tax on gain: $7,500
- **Total tax on $90,000 of economic gain: $13,500 (15% effective rate)**

### The $200K Annual Vesting Limit

Budget 2024 introduced a $200,000 annual vesting limit for the 50% stock option deduction -- but **CCPCs are exempt**. This limit only applies to publicly traded companies and non-CCPCs.

**What this means for OASIS:** When CC incorporates, OASIS stock options will qualify for the full CCPC advantage regardless of how much vests in a year.

### Valuation for CCPC Stock Options

Unlike publicly traded companies, CCPCs need a formal valuation to establish FMV at grant date:

| Method | Cost | When to Use |
|--------|------|-------------|
| 409A-style independent valuation | $3,000-$10,000 | Gold standard, defendable with CRA |
| Board resolution with internal valuation | $0 (internal) | Acceptable for early-stage if methodology is reasonable |
| Recent financing round price | $0 | Strongest evidence if recent arms-length transaction |
| Discounted cash flow (DCF) | $0-$5,000 | Standard methodology, document assumptions |
| Book value | $0 | Weakest -- only for very early stage with minimal assets |

**Best practice:** Get a formal valuation before issuing options. CRA can challenge the FMV retroactively, which would change the tax treatment for ALL option holders.

### Other Equity Compensation Types

| Type | How It Works | Tax Treatment | Best For |
|------|-------------|---------------|----------|
| Common share grant | Employee receives shares outright | Employment income at FMV on grant date | Founders, very early stage |
| Restricted Stock Units (RSUs) | Promise to deliver shares at vesting | Employment income at FMV on vesting date | Larger companies, retention |
| Phantom Stock / SARs | Cash payment tied to share value appreciation | Employment income when paid | Cash-strapped company, no dilution |
| ESPP (Employee Stock Purchase Plan) | Employee buys shares at discount | Discount up to 15% may not be taxable benefit (prescribed plan) | Public companies |
| Profit Sharing | Cash distribution from profits | Employment income when paid | All stages, simple to administer |
| Deferred Profit Sharing Plan (DPSP) | Employer-only contributions, vests over time | Taxed on withdrawal, like RRSP | Medium+ companies, RRSP alternative |

**OASIS recommendation:** Start with stock options (CCPC advantage). Consider phantom stock / SARs for early contractors you want to incentivize without dilution.

### Vesting Schedules

| Schedule | Description | Typical Use |
|----------|-------------|-------------|
| 4-year, 1-year cliff | 25% vests after year 1, then monthly/quarterly | Industry standard for startups |
| 3-year, 1-year cliff | 33% after year 1, then monthly | More aggressive, used for senior hires |
| Immediate vesting | All shares vest at grant | Founders only |
| Performance-based | Vests upon achievement of milestones | Revenue targets, product launches |
| Reverse vesting | Shares granted immediately but subject to buyback if you leave | Co-founders |

### Cap Table Management

| Tool | Cost | Best For |
|------|------|----------|
| Spreadsheet | Free | Very early stage (<5 shareholders) |
| Carta | $3,000+/year | Funded startups, option pool management |
| Shareworks (Morgan Stanley) | Enterprise pricing | Larger companies |
| Pulley | $50/month+ | Modern alternative to Carta |
| Capbase | Free tier available | Early-stage startups |

---

## 11. Termination and Severance

### `[CRITICAL]` ESA Minimum Notice (Ontario)

The Employment Standards Act sets the **floor** -- you cannot provide less than this:

| Length of Employment | Minimum Notice (or Pay in Lieu) |
|---------------------|-------------------------------|
| Less than 3 months | None |
| 3 months to 1 year | 1 week |
| 1 year to 3 years | 2 weeks |
| 3 years to 4 years | 3 weeks |
| 4 years to 5 years | 4 weeks |
| 5 years to 6 years | 5 weeks |
| 6 years to 7 years | 6 weeks |
| 7 years to 8 years | 7 weeks |
| 8 years or more | 8 weeks |

### ESA Severance Pay (Separate from Notice)

Severance pay under the ESA is **in addition to** notice and only applies when:
1. The employee has 5+ years of service, **AND**
2. The employer has a payroll of $2.5 million or more, **OR** 50+ employees are being terminated within a 6-month period

| Severance Amount | Calculation |
|-----------------|-------------|
| Rate | 1 week of regular wages per year of service |
| Maximum | 26 weeks |
| Example | 10 years of service = 10 weeks severance (+ 8 weeks notice = 18 weeks total) |

**CC relevance:** The $2.5M payroll threshold means severance pay is unlikely to apply until OASIS is significantly larger. But notice obligations apply from the first employee.

### Common Law Reasonable Notice -- The Real Exposure

If your employment agreement does NOT contain an enforceable termination clause, courts award "reasonable notice" based on the **Bardal factors**:

| Factor | Effect |
|--------|--------|
| Length of service | Longer service = more notice |
| Age of employee | Older = more notice (harder to find new work) |
| Character of employment | Senior/specialized = more notice |
| Availability of comparable employment | Scarce market = more notice |

**Rule of thumb:** ~1 month per year of service, subject to a rough ceiling of 24-26 months.

**Dollar examples of common law exposure:**

| Employee | Service | Age | Salary | Likely Common Law Notice | Cost |
|----------|---------|-----|--------|-------------------------|------|
| Junior dev | 2 years | 25 | $70K | 2-4 months | $12K-$23K |
| Senior dev | 5 years | 35 | $120K | 5-8 months | $50K-$80K |
| VP Engineering | 10 years | 50 | $180K | 12-18 months | $180K-$270K |
| C-suite | 15 years | 55 | $250K | 18-24 months | $375K-$500K |

**`[SAVINGS]` This is why termination clauses matter.** A proper termination clause limiting notice to ESA minimums would cap the VP Engineering example at 8 weeks (~$28K) instead of potentially $270K.

### `[CRITICAL]` Waksdale v. Swegon (2020 ONCA) -- The Termination Clause Killer

This Ontario Court of Appeal decision changed the landscape:

**Rule:** If ANY part of a termination clause is unenforceable (violates ESA), the **ENTIRE** termination clause is void -- even parts that were otherwise fine.

**Common trap:** The "for cause" section says "the employer may terminate for cause without notice or severance." But the ESA requires notice/severance even for some misconduct (only "wilful misconduct, disobedience, or wilful neglect of duty" qualifies for zero ESA entitlement). If your for-cause clause is broader than the ESA exception, the whole clause fails.

**Protection:** Have an employment lawyer draft your termination clause using ESA-mirroring language. Do not use templates from the internet.

### Just Cause Termination

| Factor | Details |
|--------|---------|
| Legal standard | **Very high bar** -- equivalent to the "capital punishment" of employment law |
| What qualifies | Theft, fraud, violence, serious insubordination, persistent absenteeism (after warnings), fundamental breach of trust |
| What usually doesn't qualify | Poor performance (absent warnings + PIP), one-time misconduct, personality conflicts, economic reasons |
| Progressive discipline | Required for most conduct issues: verbal warning, written warning, final warning, termination |
| Documentation | **Everything in writing.** Verbal warnings documented by email. PIPs with measurable goals and timelines. |
| Even with cause | File ROE immediately, pay outstanding wages/vacation pay, may still owe ESA minimums depending on the specific misconduct |

**Practical advice:** Assume you do not have just cause. Budget for notice/severance. If you think you have cause, get legal advice before terminating -- the cost of a wrongful dismissal suit far exceeds the cost of a severance package.

### Constructive Dismissal

If you unilaterally change a **material term** of employment, the employee may treat this as constructive dismissal (employer terminated the relationship):

**Changes that trigger constructive dismissal:**
- Significant salary reduction (>10-15%)
- Demotion (title, reporting, responsibility)
- Geographic relocation (without contractual mobility clause)
- Fundamental change in job duties
- Toxic work environment (harassment, bullying) that employer fails to address
- Layoff/temporary layoff exceeding ESA limits (35 weeks in 52-week period)

**The employee must:** Treat the change as termination immediately. If they continue working under the new terms, they may be deemed to have accepted them.

### Termination Process Checklist

On the termination date:

- [ ] Have the conversation in private, ideally with a witness
- [ ] Provide termination letter (reason, effective date, severance offer, release terms)
- [ ] Explain what you are offering (notice, severance, benefit continuation)
- [ ] Provide release/settlement agreement -- give employee time to review with a lawyer (minimum 1-2 weeks)
- [ ] Revoke system access (email, Slack, GitHub, cloud platforms) -- coordinate with IT
- [ ] Collect company property (laptop, keys, badge, credit card)
- [ ] Calculate final pay: outstanding wages + accrued vacation pay + any earned but unpaid bonus
- [ ] Pay final amount within **7 days** (Ontario) or by the next regular pay date (whichever is sooner)
- [ ] File ROE within **5 calendar days** with correct reason code
- [ ] Continue benefits through the notice period (working notice or pay in lieu)
- [ ] Provide T4 at year-end reflecting total compensation including severance
- [ ] Update payroll records and headcount

### Severance Tax Treatment

| Component | Tax Treatment |
|-----------|--------------|
| Salary continuance (working notice) | Regular employment income -- normal deductions |
| Lump-sum severance (pay in lieu) | Employment income -- can be transferred to RRSP (if room) to defer tax |
| Retiring allowance | Pre-1996 service: $2,000/year eligible for RRSP rollover; post-1995 service: employment income |
| Damages (human rights, wrongful dismissal) | General damages: not taxable; specific damages for lost wages: taxable |
| Legal fees | Employee can deduct legal fees paid to collect/establish severance (ITA s.60(o.1)) |

**`[SAVINGS]` RRSP rollover strategy:** If paying a significant lump-sum severance, advise the employee (and structure the payment) to allow RRSP transfer. This reduces their immediate tax hit and can save you money on the gross-up if you are negotiating a net number.

---

## 12. Payroll Software Comparison

### Detailed Comparison

| Software | Base Cost | Per Employee | Best For | CRA Integration | Strengths | Weaknesses |
|----------|-----------|-------------|----------|-----------------|-----------|------------|
| **Wagepoint** | $20/month | $4/employee | 1-50 employees | Yes -- direct T4/ROE/remittance | Canadian-built, simple, great support | Limited HR features |
| **Knit** | $0 base | $6/employee | 1-50 employees | Yes -- auto-remit | Modern UI, Canadian-focused, affordable | Newer, less market share |
| **Humi** | ~$5/employee (HR+payroll) | Included | 5-200 employees | Yes | Full HR suite + payroll | More expensive for payroll-only |
| **Rise People** | Free (benefits-supported) | $0 (payroll) | 10-500 employees | Yes | Free payroll if you buy benefits through them | Must use their benefits platform |
| **QuickBooks Payroll** | $25/month | $6/employee | QBO users | Yes | Integrates with QBO accounting | Less flexible than standalone |
| **ADP** | Custom pricing | $20-$40/employee | 50+ employees | Yes | Enterprise-grade, scalable | Expensive, contracts, complex |
| **Ceridian Dayforce** | Custom pricing | $15-$30/employee | 100+ employees | Yes | Best-in-class workforce management | Overkill for small businesses |
| **Wave Payroll** | $20/month (ON/AB/BC) | $6/employee | Freelancers, micro-businesses | Yes | Free accounting software integration | Limited provinces, basic features |

### OASIS Recommendation by Stage

| Stage | Recommended | Monthly Cost (est.) | Why |
|-------|------------|--------------------|----|
| 1-3 employees | Wagepoint or Knit | $26-$38/month | Simple, cheap, Canadian, CRA-integrated |
| 3-10 employees | Wagepoint or Humi | $36-$75/month | Wagepoint for payroll-only; Humi if you want HR features |
| 10-50 employees | Humi or Rise | $50-$250/month | Need HR features, onboarding, PTO tracking |
| 50+ employees | ADP or Ceridian | $1,000+/month | Enterprise compliance, multi-province, reporting |

### Integration Architecture

```
Payroll Software (Wagepoint/Knit)
  |
  |-- > CRA: T4/T4A filing, payroll remittances, ROE
  |-- > Accounting (QBO/Xero): journal entries, payroll expenses
  |-- > Bank: direct deposit processing
  |-- > Benefits provider: enrollment, premium deductions
  |-- > Time tracking (Clockify/Toggl): hours import (if hourly employees)
```

### DIY Payroll (Not Recommended Past 3 Employees)

If you insist on manual payroll:

1. **CRA PDOC (Payroll Deductions Online Calculator):** Calculate CPP, EI, and income tax for each employee
2. **Excel/Google Sheets:** Track earnings, deductions, net pay, YTD
3. **Manual remittance:** Log into CRA My Business Account and remit monthly
4. **Manual T4/ROE:** Use CRA's online tools to file year-end
5. **Manual pay stubs:** Generate using a template

**Cost:** $0 in software. Likely 4-8 hours/month of your time (or bookkeeper's time). Error-prone. One late remittance penalty will exceed the annual cost of Wagepoint.

---

## 13. International Hiring -- Full Employees Abroad

### Options for Hiring Full Employees Outside Canada

| Option | Setup Cost | Ongoing Cost | Complexity | Best For |
|--------|-----------|-------------|------------|----------|
| **Independent contractor** | $0 | Contractor rate only | Low | Short-term, project-based work |
| **Employer of Record (EOR)** | $0 | $299-$599/employee/month | Low | 1-10 employees in a country |
| **Professional Employer Organization (PEO)** | $0-$5K | $200-$500/employee/month | Medium | US employees specifically |
| **Foreign subsidiary** | $5K-$15K setup | $5K-$20K/year compliance | High | 10+ employees in a country, long-term commitment |
| **Branch office** | $2K-$10K setup | $3K-$10K/year compliance | High | Operations in the country |

### Employer of Record (EOR) -- The Modern Default

An EOR is a third-party company that legally employs workers on your behalf in foreign countries. They handle:
- Local employment contracts
- Payroll and tax withholding
- Benefits administration
- Statutory compliance (notice periods, severance, leave entitlements)
- Work permits and immigration (in some cases)

**Top EOR providers:**

| Provider | Price | Countries | Strengths |
|----------|-------|-----------|-----------|
| Deel | $599/employee/month | 150+ | Largest, best contractor conversion, crypto payroll |
| Remote | $299-$599/employee/month | 75+ | Own entities (not sub-contracting), competitive pricing |
| Oyster | $399-$599/employee/month | 130+ | Good contractor-to-employee conversion |
| Papaya Global | $650+/employee/month | 160+ | Enterprise-grade analytics |
| Multiplier | $300-$400/employee/month | 150+ | Competitive pricing, growing quickly |
| Velocity Global | Custom | 185+ | Most countries covered |

**When EOR makes sense:**
- 1-10 employees in a given country
- You don't want to incorporate there
- You need employees (not contractors) for compliance reasons
- You want to test a market before committing to a subsidiary

**When EOR doesn't make sense:**
- 10+ employees in one country (subsidiary becomes cheaper)
- You need specific local entity benefits (grants, R&D credits)
- You want full control over the employment relationship

### Permanent Establishment Risk from Foreign Employees

Hiring an employee in a foreign country can create a Permanent Establishment (PE), which means:
- Your Canadian company may have a corporate tax filing obligation in that country
- Profits attributable to the PE are taxable there
- Transfer pricing documentation required for intercompany transactions

**PE triggers by country (common treaty positions):**

| Country | PE Threshold | Key Risk |
|---------|-------------|----------|
| US | Fixed place of business OR dependent agent | Employee with contracting authority in the US |
| UK | Fixed place of business, agent, 12-month project | Even a home office can be PE if "at the disposal of" the employer |
| EU (varies) | Generally similar to UK | Each country has different interpretation |
| Australia | 183+ days of services in 12 months | Services PE threshold |

**Mitigation via EOR:** Using an EOR typically avoids PE because the worker is legally employed by the EOR entity, not your Canadian company. This is a primary reason to use an EOR.

### Social Security Totalization Agreements

Canada has social security agreements with 60+ countries to prevent double CPP/social security contributions:

**Key agreements:**
- US: only pay into one system based on where work is performed (Certificate of Coverage)
- UK: similar totalization, generally pay into country of residence
- EU countries: generally, pay into country where work is performed
- Australia, Japan, South Korea: bilateral agreements

**Why this matters:** Without an agreement, a Canadian company with a US employee might owe both CPP (Canada) and Social Security (US) on the same wages. The totalization agreement prevents this.

### Currency and Payment Considerations

| Approach | Pros | Cons |
|----------|------|------|
| Pay in local currency | Employee receives stable amount, no FX risk for them | FX risk for employer, need multi-currency accounting |
| Pay in CAD | Simple for employer accounting | Employee bears FX risk, may be less attractive |
| Pay in USD | Common middle ground for tech companies | FX risk for both parties, but USD is widely accepted |

**Best practice for small companies:** Pay in the employee's local currency. Use Wise Business for transfers (best FX rates). If using an EOR, they handle currency conversion.

---

## 14. Compliance Calendar for Employers

### Monthly

| Date | Task |
|------|------|
| 15th | Payroll remittance to CRA (regular remitter) |
| 25th | Payroll remittance for first 15 days' pay (accelerated Threshold 1) |
| 10th | Payroll remittance for previous month's last 15 days' pay (accelerated Threshold 1) |
| Ongoing | Process payroll per pay schedule |
| Ongoing | Track hours for overtime calculation |
| Ongoing | Maintain employee files (TD1 changes, address changes, etc.) |

### Quarterly

| Quarter | Tasks |
|---------|-------|
| Q1 (Jan-Mar) | Review compensation vs budget; process any salary increases; update TD1 forms |
| Q2 (Apr-Jun) | Review headcount forecast; update hiring plan; benefits renewal review |
| Q3 (Jul-Sep) | Mid-year compensation review; performance check-ins; update succession plans |
| Q4 (Oct-Dec) | Budget for next year's hiring; process year-end bonuses; vacation accrual reconciliation |

### Annual

| Date | Filing / Task |
|------|---------------|
| **January** | Review employment agreements for salary increases; distribute updated TD1 forms |
| **February 28** | **T4 Summary + individual T4 slips** (employees) |
| **February 28** | **T4A Summary + individual T4A slips** (contractors > $500) |
| **March 31** | **WSIB Form 7** (annual reconciliation of insurable earnings) |
| **April** | Benefits plan renewal review; negotiate rates with insurer |
| **June** | Review EHT exemption status (if approaching $1M payroll) |
| **July** | Mid-year payroll audit: verify CPP/EI maximums being tracked correctly |
| **October** | Prepare next-year hiring budget; forecast payroll costs |
| **November** | Open enrollment for benefits (if applicable) |
| **December** | Process final payroll; calculate vacation accruals; year-end reconciliation |
| **December 31** | Ensure all contractor invoices received for T4A reporting |

### On-Event

| Event | Action | Deadline |
|-------|--------|----------|
| New hire | Collect TD1, SIN, banking info; register with payroll software; WSIB | Before first pay |
| Termination | File ROE; final pay; revoke access | ROE within 5 days; final pay within 7 days |
| Leave of absence | File ROE; determine benefit continuation; plan workload coverage | ROE within 5 days of interruption |
| Employee moves provinces | Update provincial tax tables; review ESA applicability | Immediately |
| Raise/promotion | Update payroll; confirm RRSP matching adjustment; update personnel file | Effective date of change |
| New contractor | Signed agreement; collect SIN for T4A; set up payment method | Before work begins |

---

## 15. CC-Specific Hiring Action Plan

### `[NOW]` -- Sole Proprietor Stage

| Action | Priority | Details |
|--------|----------|---------|
| Contractor agreements | **IMMEDIATE** | Any OASIS subcontractors need signed independent contractor agreements |
| T4A tracking | **IMMEDIATE** | Track all contractor payments > $500 for year-end T4A filing |
| Contractor classification audit | **IMMEDIATE** | Review each OASIS contractor against the four-factor test |
| IP assignment | **IMMEDIATE** | Ensure every contractor agreement has IP assignment + moral rights waiver |
| Safe harbor checklist | **IMMEDIATE** | Verify each contractor passes 8/12 items on the safe harbor checklist |

### `[INCORPORATION]` -- When OASIS Incorporates

| Action | Priority | Details |
|--------|----------|---------|
| Register payroll account | Day 1 | Add RP extension to corporation BN (for paying yourself salary) |
| Set up payroll software | Day 1 | Wagepoint or Knit -- $26-$38/month for one employee (you) |
| Determine salary vs dividends | Day 1 | See ATLAS_INCORPORATION_TAX_STRATEGIES.md for optimal split |
| WSIB registration | Week 1 | Register even if just paying yourself -- may be mandatory |
| Process first payroll | Month 1 | Pay yourself salary, withhold CPP/EI/tax, remit to CRA |
| T4 yourself | February 28 | File T4 for salary paid to yourself |

### `[FIRST HIRE]` -- First Employee (Not CC)

| Action | Priority | Details |
|--------|----------|---------|
| Decision: employee vs contractor | **FIRST** | Use the four-factor test. If ongoing, integrated, supervised = employee |
| Decision: remote vs local | **FIRST** | Local (Ontario) simplifies ESA compliance initially |
| Decision: full-time vs part-time | **FIRST** | Part-time = same compliance, less cost, more flexibility |
| Employment agreement | Before start | Lawyer-drafted, including termination clause, IP assignment |
| Collect documents | Before start | TD1 federal + TD1ON, SIN, banking info, signed contract |
| WSIB confirmation | Before start | Verify registration is current, correct industry code |
| Payroll setup | Before start | Add employee to Wagepoint/Knit, set up pay schedule |
| ESA poster | Day 1 | Post Ontario ESA poster in workplace (or provide digital copy for remote) |
| Health & safety | Day 1 | Basic workplace health & safety policy (even for remote/tech) |
| Probation | First 3 months | Clear goals, regular check-ins, written feedback |
| Benefits review | Month 3 | Evaluate: HSA ($1,000-$3,000/year) is cheapest meaningful benefit |
| Budget impact | Ongoing | Employee costs ~1.15-1.35x their salary (CPP + EI + WSIB + benefits + admin) |

### `[3-5 EMPLOYEES]` -- Small Team

| Action | Priority | Details |
|--------|----------|---------|
| Group benefits | HIGH | Health/dental plan: ~$150/employee/month; HSA: $2,000-$5,000/year |
| Group RRSP matching | MEDIUM | 3-5% match -- strongest retention/recruitment tool for the cost |
| Formal offer letters | HIGH | Standardize hiring process with template contracts |
| Employee handbook | MEDIUM | Policies: PTO, remote work, expense reimbursement, code of conduct |
| Performance reviews | MEDIUM | Semi-annual or annual, documented |
| Payroll review | LOW | Confirm still on correct CRA remittance schedule |
| Budget forecast | ONGOING | Payroll typically 60-80% of total expenses for SaaS companies |

### `[SCALING]` -- 10+ Employees

| Action | Priority | Details |
|--------|----------|---------|
| Equity compensation | HIGH | Stock option plan (CCPC advantage), vesting schedules, cap table |
| Formal job levels | HIGH | Junior/Intermediate/Senior/Lead/Principal + compensation bands |
| Compensation bands | HIGH | Market-rate research, internal equity, total comp framework |
| HR software | HIGH | Upgrade from Wagepoint to Humi or similar with HR features |
| Multi-province compliance | MEDIUM | If hiring outside Ontario, need province-specific contracts |
| Dedicated HR | MEDIUM | Either fractional HR consultant or first full-time HR hire |
| EHT review | LOW | Check if approaching $1M payroll threshold |
| Benefits upgrade | MEDIUM | Comprehensive package: health/dental/life/disability/EAP |

### Decision Tree: Employee vs Contractor vs EOR

```
Is the worker in Canada?
|
+-- YES --> Is the work ongoing (6+ months)?
|           |
|           +-- YES --> Will you control how/when/where?
|           |           |
|           |           +-- YES --> EMPLOYEE (hire properly)
|           |           +-- NO  --> Does the worker have other clients?
|           |                       |
|           |                       +-- YES --> CONTRACTOR (with proper agreement)
|           |                       +-- NO  --> HIGH RISK -- consider making them an employee
|           |
|           +-- NO  --> Is it a defined project with deliverables?
|                       |
|                       +-- YES --> CONTRACTOR
|                       +-- NO  --> SHORT-TERM EMPLOYEE (or temp agency)
|
+-- NO  --> Is the work ongoing (6+ months)?
            |
            +-- YES --> Do you need full employment compliance?
            |           |
            |           +-- YES --> EMPLOYER OF RECORD (Deel/Remote)
            |           +-- NO  --> INTERNATIONAL CONTRACTOR (check Reg 105)
            |
            +-- NO  --> INTERNATIONAL CONTRACTOR (project-based)
```

---

## 16. Quick Reference Tables

### Total Cost of an Employee (Ontario, 2026 Estimates)

| Salary | CPP (employer) | CPP2 (employer) | EI (employer) | WSIB (~0.3%) | Vacation (4%) | Benefits (basic) | **Total Cost** | **Multiplier** |
|--------|---------------|-----------------|---------------|-------------|--------------|-----------------|---------------|---------------|
| $40,000 | $2,172 | $0 | $885 | $120 | $1,600 | $2,400 | **$47,177** | **1.18x** |
| $60,000 | $3,362 | $0 | $1,327 | $180 | $2,400 | $2,400 | **$69,669** | **1.16x** |
| $70,000 | $3,957 | $0 | $1,453 | $210 | $2,800 | $2,400 | **$80,820** | **1.15x** |
| $80,000 | $4,148 | $244 | $1,453 | $240 | $3,200 | $2,400 | **$91,685** | **1.15x** |
| $100,000 | $4,148 | $324 | $1,453 | $300 | $4,000 | $2,400 | **$112,625** | **1.13x** |
| $120,000 | $4,148 | $324 | $1,453 | $360 | $4,800 | $2,400 | **$133,485** | **1.11x** |
| $150,000 | $4,148 | $324 | $1,453 | $450 | $6,000 | $2,400 | **$164,775** | **1.10x** |

*Note: CPP/EI employer costs are capped at maximum pensionable/insurable earnings. Higher salaries have lower percentage overhead. Benefits estimate assumes basic health/dental at ~$200/month.*

### Contractor vs Employee Cost Comparison

| Scenario | Annual Cost (Employee) | Annual Cost (Contractor) | Savings | Risk |
|----------|----------------------|-------------------------|---------|------|
| Junior dev, $70K salary | $80,820 (1.15x) | $70,000 (invoiced) | $10,820 | Misclassification |
| Senior dev, $120K salary | $133,485 (1.11x) | $120,000 (invoiced) | $13,485 | Misclassification |
| Contractor with higher rate (market) | $80,820 (employee) | $91,000 ($130/hr x 700hrs) | -$10,180 | Low (genuine contractor) |

**Reality check:** True independent contractors often charge **higher** hourly rates than equivalent employee salaries because they cover their own CPP, EI, benefits, equipment, office, insurance, vacation, and administration. If someone is willing to "contractor" at the same salary rate, that is a red flag for misclassification.

### Key Compliance Deadlines at a Glance

| Deadline | What | Penalty for Failure |
|----------|------|---------------------|
| Before first pay | Register payroll account (RP) with CRA | Cannot legally pay employees |
| Before first day | WSIB registration | Retroactive premiums + 100% surcharge |
| Each pay period | Calculate and withhold CPP/EI/tax | 10% penalty + interest |
| 15th of following month | Remit payroll deductions to CRA (regular) | 3-10% penalty + interest |
| 5 calendar days after interruption | File ROE | $2,000 penalty, employee EI delays |
| February 28 | File T4s and T4As | $100-$7,500 penalties |
| March 31 | WSIB annual reconciliation (Form 7) | Estimated premiums applied |

---

## 17. Key Legislation Reference Index

### Federal Legislation

| Statute | Relevance |
|---------|-----------|
| **Income Tax Act (ITA)** R.S.C. 1985, c.1 (5th Supp.) | Income tax withholding, stock options (s.7), PSB (s.125(7)(d)), taxable benefits, deductions |
| **Canada Pension Plan (CPP)** R.S.C. 1985, c.C-8 | CPP contributions, employer obligations, self-employed contributions |
| **Employment Insurance Act (EI)** S.C. 1996, c.23 | EI premiums, insurable employment, ROE filing, special benefits |
| **Canada Labour Code (CLC)** R.S.C. 1985, c.L-2 | Federal employees only (banks, telecoms, transportation, federal government) |
| **Excise Tax Act (ETA)** R.S.C. 1985, c.E-15 | HST on contractor invoices, ITCs |
| **Income Tax Regulations (ITR)** C.R.C., c.945 | Regulation 105 (non-resident withholding), payroll calculation formulas |

### Provincial Legislation (Ontario)

| Statute | Relevance |
|---------|-----------|
| **Employment Standards Act, 2000 (ESA)** S.O. 2000, c.41 | Minimum wage, overtime, vacation, termination notice, severance, statutory holidays |
| **Ontario Human Rights Code (OHRC)** R.S.O. 1990, c.H.19 | Anti-discrimination in hiring, accommodation, prohibited grounds |
| **Workplace Safety and Insurance Act, 1997 (WSIA)** S.O. 1997, c.16, Sch. A | WSIB premiums, workplace injury coverage, employer obligations |
| **Employer Health Tax Act (EHTA)** R.S.O. 1990, c.E.11 | EHT premiums, small business exemption |
| **Occupational Health and Safety Act (OHSA)** R.S.O. 1990, c.O.1 | Workplace safety obligations, even for remote workers |
| **Working for Workers Act, 2021-2024** | Non-compete ban, disconnection policy, electronic monitoring disclosure |
| **Pay Transparency Act, 2018** S.O. 2018, c.5 | Salary range disclosure in job postings |

### Key CRA Forms

| Form | Purpose |
|------|---------|
| RC1 | Business Number registration |
| TD1 / TD1ON | Personal tax credit claim (federal + Ontario) |
| CPT1 | Request for worker status ruling (employee vs contractor) |
| CPT30 | Election to stop CPP contributions (65-70) |
| T4 / T4 Summary | Employee wage and deduction reporting |
| T4A / T4A Summary | Contractor payment reporting (> $500) |
| ROE (Record of Employment) | Filed electronically via ROE Web upon interruption of earnings |
| PD7A | Statement of account for current source deductions (remittance voucher) |
| RC4110 | Employee or Self-Employed? (guide for determining status) |
| T2200 | Declaration of Conditions of Employment (home office expenses) |
| R105 | Non-resident waiver application (services in Canada) |

### Key Case Law

| Case | Year | Significance |
|------|------|-------------|
| **Wiebe Door Services Ltd. v. MNR** | 1986 FCA | Established the four-factor test for employee vs contractor |
| **671122 Ontario Ltd. v. Sagaz Industries** | 2001 SCC | Confirmed four-factor test; added "whose business is it?" central question |
| **Waksdale v. Swegon** | 2020 ONCA | If any part of termination clause violates ESA, entire clause is void |
| **Bardal v. Globe & Mail Ltd.** | 1960 ONHC | Established factors for reasonable notice (length of service, age, character of employment, availability of similar employment) |
| **Machtinger v. HOJ Industries** | 1992 SCC | Termination provisions that violate ESA minimums are void |
| **Matthews v. Ocean Nutrition Canada** | 2020 SCC | Employees are entitled to bonus/compensation they would have earned during reasonable notice period unless clearly excluded |
| **Potter v. New Brunswick Legal Aid** | 2015 SCC | Constructive dismissal framework -- employer bears burden of proving no breach |

---

## Appendix A: Employment Agreement Template Outline

This is a structural outline only. Have an employment lawyer customize for OASIS.

```
EMPLOYMENT AGREEMENT

1. PARTIES
   - Corporation name, address
   - Employee name, address

2. POSITION AND DUTIES
   - Title, reporting to, primary responsibilities
   - "Other duties as reasonably assigned"
   - Full-time, 40 hours/week (or part-time)
   - Remote/hybrid/in-office

3. TERM AND PROBATION
   - Indefinite term
   - 3-month probationary period (ESA-compliant language)

4. COMPENSATION
   - Annual salary: $[AMOUNT], paid semi-monthly
   - Annual review (not guarantee)
   - Bonus: [discretionary/formula], timing, pro-ration
   - Equity: reference to stock option agreement (if applicable)
   - Expense reimbursement per Company policy

5. BENEFITS
   - Enrollment in group benefits plan (after probation or 3 months)
   - HSA allocation: $[AMOUNT]/year
   - Group RRSP matching: [X]% (if applicable)
   - Vacation: [X] weeks (minimum ESA)

6. TERMINATION BY COMPANY WITHOUT CAUSE
   - [LAWYER-DRAFTED CLAUSE mirroring ESA minimums]
   - "The notice and/or severance provided under this section
     shall constitute the Employee's full and final entitlement
     upon termination, subject to the minimums required by the
     Employment Standards Act, 2000, as amended."

7. TERMINATION BY COMPANY FOR CAUSE
   - [LAWYER-DRAFTED CLAUSE using ESA language]
   - "Wilful misconduct, disobedience, or wilful neglect of duty
     that is not trivial and has not been condoned by the Company"

8. RESIGNATION
   - Employee provides 2 weeks written notice (or more for senior roles)

9. INTELLECTUAL PROPERTY
   - All work product is Company property
   - Assignment of all rights, title, and interest
   - Moral rights waiver
   - Pre-existing IP schedule (employee lists exclusions)

10. CONFIDENTIALITY
    - Broad definition of Confidential Information
    - Obligation survives termination
    - Return of materials

11. NON-SOLICITATION (NO NON-COMPETE in Ontario)
    - 12 months: clients
    - 12 months: employees
    - Reasonable scope and geography

12. GENERAL
    - Governing law: Ontario
    - Entire agreement
    - Severability
    - Independent legal advice acknowledgment
    - Amendment in writing only

SIGNATURES
- Employee
- Company (authorized signatory)
- Date
- Witness (recommended)
```

---

## Appendix B: Independent Contractor Agreement Template Outline

```
INDEPENDENT CONTRACTOR AGREEMENT

1. PARTIES
   - Company name
   - Contractor name (individual or corporation)

2. SERVICES
   - Scope of work (reference SOW as Schedule A)
   - Deliverables and acceptance criteria
   - Change order process

3. TERM
   - Start date, end date (or project completion)
   - Renewal terms (if any)

4. COMPENSATION
   - Fixed fee / milestone payments / hourly rate with cap
   - Payment terms: Net-30 from invoice date
   - Invoice requirements
   - No expense reimbursement unless pre-approved in writing
   - HST/GST: Contractor to include if registered

5. RELATIONSHIP
   - Independent contractor, not employee
   - Contractor responsible for own taxes, CPP, EI
   - Contractor maintains other clients
   - Contractor provides own tools and workspace
   - Contractor determines own schedule and methods
   - Contractor may subcontract with Company's consent

6. INTELLECTUAL PROPERTY
   - Assignment of all work product
   - Moral rights waiver
   - Pre-existing IP license
   - Survival clause

7. CONFIDENTIALITY
   - Same structure as employment agreement

8. NON-SOLICITATION
   - 12 months: clients and employees

9. INDEMNIFICATION
   - Mutual indemnification
   - Limitation of liability: capped at fees paid

10. INSURANCE
    - Contractor maintains professional liability / E&O insurance
    - Minimum coverage: $1,000,000 (or appropriate for scope)

11. TERMINATION
    - Either party: 30 days written notice
    - Payment for work completed to date
    - Return of materials and access

12. GENERAL
    - Governing law: Ontario
    - Entire agreement
    - Severability
    - Independent legal advice

SIGNATURES
- Company
- Contractor
- Date

SCHEDULE A: STATEMENT OF WORK
- Detailed deliverables, timelines, milestones, acceptance criteria
```

---

## Appendix C: Hiring Cost Calculator

Quick formula to budget the true cost of hiring:

```
TRUE ANNUAL COST OF AN EMPLOYEE

Base Salary:                         $________
+ CPP employer (5.95% to YMPE):      $________
+ CPP2 employer (4% YMPE to YAMPE):  $________
+ EI employer (2.212% to max):        $________
+ WSIB (~0.3% for tech):             $________
+ Vacation pay (4-6%):               $________
+ Statutory holiday pay (~3.5%):      $________
+ Benefits (health/dental/HSA):       $________
+ Group RRSP match (3-5%):           $________
+ Payroll software (~$50/year):       $________
+ Recruitment cost (if any):          $________
                                     ---------
= TOTAL ANNUAL COST:                 $________
= MULTIPLIER (Total / Salary):       ___x

TYPICAL MULTIPLIERS:
  No benefits:                        1.12-1.15x
  Basic benefits (HSA only):          1.15-1.20x
  Standard benefits (health + RRSP):  1.20-1.30x
  Comprehensive (full package):       1.25-1.40x
```

---

*This document is maintained by ATLAS as part of CC's CFO intelligence library. All rates, thresholds, and legislation references are current as of 2026-03-27. Rates are updated annually by CRA (CPP/EI) and WSIB. Consult an employment lawyer for contract drafting and a CPA for payroll setup.*

*Related ATLAS documents:*
- `docs/ATLAS_TAX_STRATEGY.md` -- Core tax playbook
- `docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md` -- When and how to incorporate
- `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` -- Chart of accounts including payroll expense categories
- `docs/ATLAS_HST_REGISTRATION_GUIDE.md` -- HST on contractor invoices and ITCs
- `docs/ATLAS_AI_SAAS_TAX_GUIDE.md` -- SR&ED credits, contractor vs employee for R&D
- `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` -- All deductible business expenses including payroll-related
- `docs/ATLAS_TOSI_DEFENSE.md` -- Income splitting strategies when paying family members
