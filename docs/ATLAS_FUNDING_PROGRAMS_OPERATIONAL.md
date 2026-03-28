# ATLAS — Funding Programs Operational Guide

> **For:** Conaugh McKenna (CC), 22, OASIS AI Solutions (AI SaaS)
> **Entity:** Sole proprietor (Ontario) — CCPC incorporation planned 2026
> **Location:** Collingwood, Ontario (Montreal move summer 2026)
> **Projected 2026 Revenue:** $280K-$480K+ CAD
> **Last Updated:** 2026-03-27
> **Document Type:** OPERATIONAL — application-ready checklists, timelines, dollar amounts
> **Companion Document:** `ATLAS_GOVERNMENT_GRANTS.md` (high-level overview, 809 lines)
> **Estimated Total Accessible Funding:** $600K-$1.2M+ (grants + credits + subsidized loans + cloud credits)

---

## Table of Contents

1. [SR&ED — Scientific Research & Experimental Development](#1-sred--scientific-research--experimental-development)
2. [IRAP — Industrial Research Assistance Program](#2-irap--industrial-research--assistance-program)
3. [CSBFP — Canada Small Business Financing Program](#3-csbfp--canada-small-business-financing-program)
4. [Futurpreneur Canada](#4-futurpreneur-canada)
5. [BDC — Business Development Bank of Canada](#5-bdc--business-development-bank-of-canada)
6. [CanExport — International Market Development](#6-canexport--international-market-development)
7. [CDAP — Canada Digital Adoption Program](#7-cdap--canada-digital-adoption-program)
8. [Strategic Innovation Fund (SIF)](#8-strategic-innovation-fund-sif)
9. [Mitacs — Research Internship Programs](#9-mitacs--research-internship-programs)
10. [OIDMTC — Ontario Interactive Digital Media Tax Credit](#10-oidmtc--ontario-interactive-digital-media-tax-credit)
11. [OITC — Ontario Innovation Tax Credit](#11-oitc--ontario-innovation-tax-credit)
12. [Starter Company Plus (Ontario)](#12-starter-company-plus-ontario)
13. [Ontario Centres of Excellence (OCE) / Ontario Vehicle Innovation Network](#13-ontario-centres-of-excellence--ontario-vehicle-innovation-network)
14. [Ontario Together Fund and Provincial Innovation Programs](#14-ontario-together-fund-and-provincial-innovation-programs)
15. [Quebec — CDAE (e-Business Tax Credit)](#15-quebec--cdae-e-business-tax-credit)
16. [Quebec — Investissement Quebec](#16-quebec--investissement-quebec)
17. [Quebec — SR&ED Provincial Credit](#17-quebec--sred-provincial-credit)
18. [Quebec — NovaScience and FRQNT](#18-quebec--novascience-and-frqnt)
19. [Quebec — AI Ecosystem (MILA, IVADO, Scale AI)](#19-quebec--ai-ecosystem-mila-ivado-scale-ai)
20. [Cloud Credits and Platform Programs](#20-cloud-credits-and-platform-programs)
21. [Accelerators and Incubators](#21-accelerators-and-incubators)
22. [Stacking Strategy — Maximum Total Funding](#22-stacking-strategy--maximum-total-funding)
23. [Master Application Timeline](#23-master-application-timeline)
24. [Application Best Practices](#24-application-best-practices)
25. [Stacking Calculator — CC's 2026-2027 Scenario](#25-stacking-calculator--ccs-2026-2027-scenario)

---

## 1. SR&ED — Scientific Research & Experimental Development

**Program Type:** Refundable tax credit (federal)
**Administering Body:** CRA (Canada Revenue Agency)
**Website:** canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program.html

### What It Is

The single most valuable program for AI/ML companies in Canada. The government refunds a percentage of qualifying R&D expenditures. Not a grant you apply for separately — claimed on your tax return.

### ITC Rates

| Entity Type | Federal Rate | Refundable? | Expenditure Cap | Max Annual ITC |
|-------------|-------------|-------------|-----------------|----------------|
| Sole Proprietor | 15% | Yes (refundable up to $928K qualified expenditures) | $928K | $139,200 |
| CCPC (< $500K taxable income) | 35% | Fully refundable up to $3M expenditure pool | $3M | $1,050,000 |
| CCPC (above threshold) | 15% | 40% refundable | No cap | Unlimited (but 40% refund) |

**Ontario provincial add-on (OITC):** 8% refundable on qualifying Ontario SR&ED expenditures.
**Combined CCPC rate:** 35% federal + 8% Ontario = **43% refundable.**

### Eligibility Criteria for AI/ML Work

CRA uses three criteria. ALL three must be met:

**1. Technological Uncertainty**
- [ ] The outcome could not be determined in advance using standard practice
- [ ] Existing AI/ML techniques were insufficient or their applicability was unknown
- [ ] You did not know if a particular approach would work before trying it
- [ ] Examples for OASIS: "We did not know if fine-tuning an LLM on domain-specific data would achieve acceptable accuracy for automated client onboarding" or "Standard retrieval-augmented generation produced hallucinations above acceptable thresholds for our use case"

**2. Systematic Investigation**
- [ ] You followed a structured process (hypothesis, test, measure, iterate)
- [ ] You documented your approach, experiments, and results
- [ ] Git commits serve as evidence of iterative development
- [ ] You can describe what you tried, what failed, and why you changed approach

**3. Technological Advancement**
- [ ] You created new knowledge or techniques in the field
- [ ] You solved a technological problem that had no known solution
- [ ] The advancement goes beyond standard application of existing tools
- [ ] Example: "Developed a novel prompt-chaining architecture that reduced hallucination rates by 40% compared to baseline RAG implementations"

### What DOES NOT Qualify

- Routine software development (CRUD apps, standard web dev)
- Market research, style changes, quality control testing
- Social science or humanities research
- Data collection for business purposes (not technological)
- Work done after the technological uncertainty was resolved
- Simply using existing AI APIs without modification or novel application

### Qualifying Expenditures

| Category | What Counts | Calculation |
|----------|-------------|-------------|
| **Salary (including CC's own)** | Time spent on qualifying R&D work | Hourly rate x R&D hours. CC as sole prop: reasonable salary equivalent based on comparable market rate. As CCPC: actual T4 salary paid. |
| **Materials consumed** | Cloud computing costs used in R&D (training runs, GPU hours), test data | Actual cost. Must be consumed or transformed — not end-product. |
| **Overhead (proxy method)** | Rent, utilities, office supplies attributable to R&D | 55% of qualifying salary expenditures (use proxy method — simpler, recommended) |
| **Subcontractors (arm's length)** | Contractors doing R&D work for you | 80% of invoiced amount (only 80% eligible) |
| **Subcontractors (non-arm's length)** | Related parties doing R&D | Actual salary cost of the subcontractor's employees |
| **Third-party payments** | Payments to universities, research institutes | 100% of amount paid |

### CC's Estimated SR&ED Claim (2026)

**Assumptions:**
- CC spends 50% of working time on qualifying R&D (novel AI architecture, model fine-tuning, automation pipelines with technological uncertainty)
- ~2,000 working hours/year x 50% = 1,000 R&D hours
- Reasonable salary equivalent: $75/hour (market rate for AI/ML developer)
- Cloud computing for R&D: $5K/year (training runs, API calls during experimentation)

| Expenditure | Amount |
|-------------|--------|
| Salary (CC, 1,000 hrs x $75) | $75,000 |
| Overhead proxy (55% of salary) | $41,250 |
| Materials (cloud, APIs) | $5,000 |
| Subcontractors (80% of any) | $0 (currently) |
| **Total Qualifying Expenditure** | **$121,250** |

| Entity | Rate | ITC (Federal) | OITC (8%) | Total Refund |
|--------|------|---------------|-----------|-------------|
| Sole Proprietor | 15% | $18,187 | N/A (provincial for corps) | **$18,187** |
| CCPC | 35% | $42,437 | $9,700 | **$52,137** |

**This is why incorporation matters.** CCPC gets $52K back vs. $18K as sole prop. The $34K difference alone pays for incorporation costs 10x over.

### Application Process — Step by Step

**Form:** T661 (Claim for Scientific Research and Experimental Development)

**Step 1 — Track R&D Hours NOW (Start Immediately)**
- [ ] Create a weekly time log: date, hours, project, description of work
- [ ] Separate R&D time from routine operational time
- [ ] Use git commits as corroborating evidence (timestamps, commit messages describing experimental work)
- [ ] Save screenshots of failed experiments, error logs, benchmark results

**Step 2 — Document Technological Uncertainties BEFORE Solving Them**
- [ ] Before starting a new R&D task, write 2-3 sentences describing: What you do not know. Why existing methods are insufficient. What you plan to try.
- [ ] This is the single most important thing for a successful claim
- [ ] Keep a running "R&D journal" — even a simple text file with dated entries

**Step 3 — Write the Technical Narrative (80% of Success)**

The T661 requires a project description answering three questions:
1. What technological uncertainties did you face?
2. What systematic investigation did you undertake?
3. What technological advancements did you achieve?

Template for each project:
```
PROJECT: [Name]
PERIOD: [Start date] to [End date]

UNCERTAINTY: We did not know whether [specific technical challenge] could be
solved using [available methods/tools]. Standard approaches [describe what
exists] were insufficient because [specific limitation].

INVESTIGATION: We hypothesized that [approach]. We tested this by [method].
Results showed [outcome]. We then modified our approach to [next iteration].
After [N] iterations, we [achieved/did not achieve] the desired outcome.

ADVANCEMENT: We developed [specific technique/architecture/method] that
[measurable improvement]. This advancement goes beyond standard practice
because [why it is novel].
```

**Step 4 — Calculate Financial Summary**
- [ ] Tally all qualifying expenditures by category
- [ ] Apply proxy method (55%) for overhead
- [ ] Apply 80% rule for arm's-length subcontractors
- [ ] Complete Form T661 Part 2 (financial)

**Step 5 — File with Tax Return**
- [ ] T661 must be filed with your T1 (sole prop) or T2 (CCPC) return
- [ ] Deadline: **18 months after the end of the fiscal year** in which expenditures were incurred
- [ ] For sole prop with Dec 31 year-end: file by June 30 of the year after next
- [ ] For CCPC: 18 months after corporate fiscal year-end

**Step 6 — CRA Review (If Selected)**
- [ ] ~20% of first-time claims are reviewed
- [ ] CRA sends a Research and Technology Advisor (RTA) to interview you
- [ ] Have your time logs, git history, technical documentation ready
- [ ] Be prepared to explain uncertainties and your systematic approach
- [ ] Do NOT overstate claims — CRA will reduce the entire claim if they find exaggeration

### Common Rejection Reasons

| Reason | How to Avoid |
|--------|-------------|
| "Work is routine software development" | Emphasize what you did NOT know, not what you built |
| "No technological uncertainty documented" | Write uncertainties BEFORE starting work |
| "Insufficient records" | Keep weekly time logs + git commit evidence |
| "Advancement is business innovation, not technological" | Focus on HOW you solved it, not WHAT it does for customers |
| "Work was done by subcontractors without oversight" | Maintain technical direction and documentation |
| "Proxy method improperly applied" | Only apply 55% to salary of employees doing SR&ED work |

### Professional Help

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| SR&ED consultant (contingency) | 25-30% of refund | Zero upfront cost, they are motivated to maximize | Expensive on large claims |
| SR&ED consultant (flat fee) | $5K-$15K | Predictable cost, you keep full refund | Must pay regardless of outcome |
| Accountant with SR&ED experience | $3K-$8K | Lower cost, integrated with tax filing | May not write strong technical narratives |
| DIY | $0 | Keep everything | High rejection risk on first claim |

**Atlas recommendation for CC:** Use a contingency-fee SR&ED consultant for the first claim. Yes, you lose 25-30% of the refund, but they know exactly what CRA wants and will maximize the claim. Switch to flat fee once you understand the process (year 2+).

---

## 2. IRAP — Industrial Research Assistance Program

**Program Type:** Non-repayable contribution (grant)
**Administering Body:** NRC (National Research Council)
**Website:** nrc.canada.ca/en/support-technology-innovation/about-nrc-industrial-research-assistance-program
**Amount:** Up to **$500K** per project (typical first project: $50K-$150K)

### What It Is

The most generous pure grant program for Canadian tech SMEs. NRC gives you money (not a loan) to cover salary costs for R&D staff. You get assigned a dedicated Industrial Technology Advisor (ITA) who acts as a free business consultant.

### Eligibility Checklist

- [ ] Canadian incorporated company (CCPC incorporation required — sole props do not qualify)
- [ ] Fewer than 500 employees
- [ ] For-profit entity
- [ ] Conducting R&D or technology-driven innovation in Canada
- [ ] Project has commercial potential
- [ ] Company can demonstrate financial capacity to complete the project

**CC BLOCKER:** IRAP requires incorporation. This is another reason to incorporate ASAP.

### What IRAP Covers

| Covered | Not Covered |
|---------|------------|
| Salary for R&D staff (including CC if on payroll) | Equipment purchases |
| Salary for technical contractors (with approval) | Marketing and sales costs |
| Up to 80% of eligible salary costs | Travel (usually) |
| | Overhead (no proxy like SR&ED) |

### Typical IRAP Project for OASIS

**Project:** Develop AI-powered automation platform with novel natural language processing capabilities for business workflow optimization.

**Eligible Costs:**
- CC's salary (as CCPC employee): $80K-$120K x 80% = $64K-$96K contribution
- Additional developer hire: $70K x 80% = $56K contribution
- Total potential IRAP funding: $120K-$152K for a 12-month project

### Application Process

**Step 1 — Contact Your Local ITA (Do This First)**
- [ ] Go to nrc.canada.ca and find the "Contact an ITA" page
- [ ] Or call NRC directly: 1-877-994-4727
- [ ] Your ITA will be assigned based on location (Ontario, then Quebec after move)
- [ ] The ITA meeting is informal — describe your business and R&D plans
- [ ] Build a relationship before asking for money. ITAs are advisors first, gatekeepers second.

**Step 2 — ITA Assessment**
- [ ] ITA visits (or calls) to assess your company
- [ ] They evaluate: innovation potential, management capability, market opportunity, financial health
- [ ] This is not an exam — it is a conversation. Be genuine about challenges.
- [ ] ITA may suggest adjustments to your project scope before formal application

**Step 3 — Project Proposal**
- [ ] ITA helps you develop the proposal (free assistance)
- [ ] Proposal includes: project objectives, technical approach, milestones, budget, expected outcomes
- [ ] Budget must show co-funding (you pay 20%+ of salary costs yourself)
- [ ] Timeline: typically 6-18 month projects

**Step 4 — Approval and Contribution Agreement**
- [ ] NRC reviews and approves (2-4 months typical)
- [ ] You sign a Contribution Agreement with specific milestones
- [ ] Funding is disbursed as you hit milestones and submit claims
- [ ] You must NOT start the project before the Contribution Agreement is signed

**Step 5 — Execution and Reporting**
- [ ] Submit quarterly progress reports to your ITA
- [ ] Submit financial claims with payroll records as evidence
- [ ] ITA may visit periodically to check progress
- [ ] Final report at project completion

### Timeline

| Phase | Duration |
|-------|----------|
| Initial ITA contact to first meeting | 1-3 weeks |
| Assessment and proposal development | 4-8 weeks |
| NRC internal review and approval | 6-12 weeks |
| Contribution Agreement signing | 2-4 weeks |
| **Total: contact to first dollar** | **3-6 months** |

### IRAP + SR&ED Stacking Rules

You CAN claim both, but:
- IRAP-funded salary portions must be **reduced** from your SR&ED qualifying expenditures
- Example: CC earns $100K salary. IRAP covers $80K. Only $20K of CC's salary counts for SR&ED.
- The overhead proxy (55%) also reduces because it is based on qualifying salary
- Net effect: you still come out ahead, but the SR&ED refund is smaller

### CC Fit Assessment: STRONG

IRAP is ideal for OASIS. AI/ML work is exactly what NRC wants to fund. CC's age and ambition are positives (NRC likes supporting high-growth potential companies). The only blocker is incorporation.

---

## 3. CSBFP — Canada Small Business Financing Program

**Program Type:** Government-guaranteed loan
**Administering Body:** Innovation, Science and Economic Development Canada (ISED)
**Website:** ic.gc.ca/eic/site/csbfp-pfpec.nsf/eng/home

### Loan Limits

| Category | Maximum |
|----------|---------|
| Equipment and leasehold improvements | $500,000 |
| Real property | $500,000 |
| Intangible assets and working capital | $150,000 |
| **Total maximum** | **$1,000,000** |

### Terms

| Term | Detail |
|------|--------|
| Interest rate (variable) | Prime + 3% |
| Interest rate (fixed) | Lender's residential mortgage rate + 3% |
| Registration fee | 2% of loan amount (financed into loan) |
| Term — equipment | Up to 10 years |
| Term — leasehold | Up to 10 years (or lease term) |
| Term — real property | Up to 15 years |
| Term — intangible/working capital | Up to 5 years |
| Personal guarantee | Maximum 10% of original loan amount |

### Eligibility Checklist

- [ ] Canadian business (sole prop or corporation)
- [ ] Gross annual revenue under $10M
- [ ] Operating or about to operate in Canada
- [ ] Not a farming enterprise
- [ ] Loan purpose fits eligible categories

### What It Covers vs. Does Not Cover

**Covers:**
- Computers, servers, GPUs, monitors, networking equipment
- Office furniture and fixtures
- Leasehold improvements (if CC rents office space in Montreal)
- Software licenses (if capitalized as an asset)
- Working capital (up to $150K — new as of 2022)
- Real property purchase

**Does NOT Cover:**
- Inventory, franchise fees, goodwill
- R&D costs (use SR&ED for that)
- Working capital above $150K

### Application Process

**Step 1 — Choose a Lender**
- [ ] Any chartered bank, credit union, or caisse populaire
- [ ] CC has RBC relationship — start there
- [ ] In Montreal: Desjardins is a strong option (caisse populaire, government-friendly)
- [ ] Shop around — lenders can add their own requirements on top of CSBFP minimums

**Step 2 — Prepare Documentation**
- [ ] Business plan (OASIS overview, revenue projections, market opportunity)
- [ ] Financial statements (2025 T2125 or corporate financials)
- [ ] Personal financial statement (assets and liabilities)
- [ ] Quote/invoice for intended purchase (equipment, leasehold)
- [ ] Proof of business registration

**Step 3 — Apply Explicitly for CSBFP**
- [ ] Ask specifically for a "Canada Small Business Financing Program loan"
- [ ] Loan officers may push commercial products instead (higher margins for the bank)
- [ ] Insist on CSBFP — the government guarantee makes approval easier
- [ ] The bank submits the registration to ISED

**Step 4 — Approval and Funding**
- [ ] Typical approval: 2-6 weeks
- [ ] Funds disbursed directly to vendor (for equipment) or to business account (working capital)
- [ ] Registration fee (2%) added to loan balance

### CC's Play

**Montreal Move Equipment Package: $50K-$75K**
- Workstation with GPU: $5K-$10K
- Multiple monitors, peripherals: $3K-$5K
- Office setup (desk, chair, lighting, sound): $3K-$5K
- Server/cloud infrastructure deposit: $5K-$10K
- Working capital reserve: $25K-$40K

Personal guarantee maxes at $5K-$7.5K (10% of loan). This is one of the lowest-risk loans available.

---

## 4. Futurpreneur Canada

**Program Type:** Startup loan + mentorship
**Website:** futurpreneur.ca
**Amount:** Up to **$60,000** ($20K Futurpreneur + $40K BDC co-lending)

### Eligibility Checklist

- [ ] Canadian citizen or permanent resident
- [ ] Age 18-39 (CC: 22 — qualifies for 17 more years)
- [ ] Business operating for less than 12 months OR in pre-launch
- [ ] Not a franchise
- [ ] Willing to complete business plan
- [ ] Willing to accept 2-year mentorship

### CC Fit Assessment: UNCERTAIN

**Potential Issue:** If OASIS has been operating since January 2025 (over 12 months by now), CC may not qualify under the startup definition. However:
- Futurpreneur sometimes accepts "pivots" as new ventures
- If CC incorporates as a CCPC, the corporation is a new entity
- Contact Futurpreneur directly to clarify — they are flexible

### Application Process

**Step 1 — Online Application**
- [ ] Go to futurpreneur.ca/en/get-started
- [ ] Complete initial eligibility questionnaire
- [ ] If eligible, you will be assigned a Futurpreneur advisor

**Step 2 — Business Plan Development**
- [ ] Futurpreneur provides free templates and advisor support
- [ ] Business plan must include: executive summary, market analysis, operations plan, 2-year cash flow projections
- [ ] Cash flow projections are the most scrutinized part — be realistic but ambitious
- [ ] Atlas can prepare these projections for CC

**Step 3 — Review and Approval**
- [ ] Futurpreneur reviews business plan (4-8 weeks)
- [ ] If approved for $20K+, BDC co-lending review (additional 2-4 weeks)
- [ ] Total timeline: 6-12 weeks from application to funding

**Step 4 — Mentorship Matching**
- [ ] Matched with experienced entrepreneur for 2 years
- [ ] Monthly meetings (minimum)
- [ ] Genuinely valuable — treat it as free consulting worth $10K+/year

### Loan Terms

| Term | Detail |
|------|--------|
| Amount | $20K (Futurpreneur) + $40K (BDC) = $60K |
| Interest | Variable, typically prime + 2-3% |
| Repayment | Up to 5 years |
| Grace period | Up to 12 months (interest only) |
| Collateral | None required |
| Personal guarantee | Limited |

---

## 5. BDC — Business Development Bank of Canada

**Program Type:** Various loans, advisory, venture capital
**Website:** bdc.ca
**Key Advantage:** BDC exists to serve entrepreneurs that commercial banks underserve

### Loan Products Relevant to CC

**BDC Small Business Loan**
- Amount: $10K-$100K
- Unsecured (no collateral required)
- Online application, fast approval (days, not weeks)
- Higher interest rate than CSBFP but simpler process
- Use for: working capital, small equipment purchases

**BDC Technology Loan**
- Amount: up to $5M
- For technology companies investing in growth
- Covers: hiring, IP development, market expansion, infrastructure
- More flexible repayment terms than banks
- Requires business plan and financial projections

**BDC Advisory Services**
- Free or subsidized consulting
- Strategic planning, digital strategy, operational efficiency
- Can pair with loan application

**BDC Venture Capital**
- For high-growth tech companies
- Typically Series A and later ($1M+)
- Not relevant for CC currently but good to know for $1M+ ARR stage

### Application Process (Small Business Loan)

- [ ] Apply online at bdc.ca
- [ ] Provide: business registration, financial statements, personal ID
- [ ] BDC reviews (typically 5-10 business days)
- [ ] If approved, funds deposited to business bank account
- [ ] No branches required — fully digital

### CC Fit Assessment: GOOD

BDC Small Business Loan is a strong option for $50K-$100K working capital. Higher cost than CSBFP but faster and simpler. Consider as backup if CSBFP takes too long.

---

## 6. CanExport — International Market Development

**Program Type:** Non-repayable grant
**Administering Body:** Trade Commissioner Service (Global Affairs Canada)
**Website:** tradecommissioner.gc.ca/funding
**Amount:** Up to **$50,000** per project (matching contribution — you fund 50%, they fund 50%)

### Eligibility Checklist

- [ ] Canadian business (incorporated or sole proprietorship)
- [ ] Annual revenue between $100K-$100M CAD
- [ ] Fewer than 500 employees
- [ ] Seeking to develop NEW international markets
- [ ] Must not already be active in the target market

### What It Covers

- International travel for market development
- Trade show attendance and booth costs
- Legal fees for international contracts
- Marketing and promotional materials for foreign markets
- Market research for international expansion
- Translation and localization costs

### CC Fit Assessment: RELEVANT (When Ready)

If OASIS starts selling to US or UK clients (likely given CC's British passport and English-language SaaS), CanExport can fund the expansion costs. Not immediate priority, but important once revenue diversifies beyond Canada.

### Application Process

- [ ] Apply online through the Trade Commissioner Service portal
- [ ] Submit: project description, budget, target market analysis
- [ ] Approval: 6-8 weeks
- [ ] Claim expenses as incurred (submit receipts quarterly)
- [ ] Project must be completed within 12-24 months

---

## 7. CDAP — Canada Digital Adoption Program

**Program Type:** Grant + interest-free loan
**Amount:** Up to **$15,000** grant + **$100,000** at 0% interest from BDC

### Current Status (2026)

CDAP was launched 2022 with finite funding. Check ised-isde.canada.ca for current availability. Program may be renewed, modified, or closed.

### Eligibility Checklist (Original Program)

- [ ] Canadian-owned SME
- [ ] At least 1 employee (non-owner)
- [ ] Annual revenue $500K-$100M
- [ ] Must adopt new digital technologies (not create them)

### CC Fit Assessment: WEAK (As Recipient)

CC is a technology CREATOR, not adopter. The $500K revenue minimum and employee requirement are additional barriers. However:
- If program is renewed with lower thresholds, reassess
- If CC hires one employee, partially qualifies
- CC could be a CDAP-approved digital advisor (earn revenue by helping other businesses adopt digital tools — separate opportunity)

---

## 8. Strategic Innovation Fund (SIF)

**Program Type:** Repayable/non-repayable contributions
**Administering Body:** ISED
**Amount:** $10M+ (for large-scale innovation projects)
**Website:** ic.gc.ca/eic/site/125.nsf/eng/home

### CC Fit Assessment: NOT YET

SIF targets large-scale projects ($10M+ investment). Not relevant until OASIS is significantly larger. Noted here for completeness — revisit at $5M+ ARR.

---

## 9. Mitacs — Research Internship Programs

**Program Type:** Subsidized research internships
**Website:** mitacs.ca

### Programs

**Mitacs Accelerate**
- Fund research interns at 50% cost ($15K per 4-month unit — Mitacs pays $7.5K)
- Intern must be a graduate student at a Canadian university
- Multiple units stackable (up to 2 years)
- CC could hire a masters/PhD student in ML/AI at half cost

**Mitacs Business Strategy Internship (BSI)**
- Fund MBA/business students for strategic projects
- Similar 50% cost share
- Useful for market research, business development

### CC Fit Assessment: GOOD (Post-Montreal Move)

Montreal has the highest concentration of AI/ML graduate students in Canada (MILA, Universite de Montreal, McGill, Polytechnique, Concordia). CC could hire a subsidized ML intern for $7.5K/4 months to work on OASIS AI capabilities.

### Application Process

- [ ] Partner with a Canadian university (the intern's institution)
- [ ] Professor must be involved as academic supervisor
- [ ] Submit joint application through Mitacs portal
- [ ] Approval: 6-8 weeks
- [ ] Intern works on-site or remotely on defined project

---

## 10. OIDMTC — Ontario Interactive Digital Media Tax Credit

**Program Type:** Refundable tax credit (Ontario)
**Rate:** **40%** of qualifying Ontario labour expenditures and marketing/distribution expenses
**Administering Body:** Ontario Creates (certification) + CRA (claim)
**Website:** ontariocreates.ca/tax-incentives/oidmtc

### What It Is

A 40% refundable tax credit on eligible expenditures for interactive digital media products developed in Ontario. This is one of the most generous provincial tech credits in Canada.

### Eligibility Criteria

The product must be:
- [ ] Interactive digital media (user interaction required — not passive content)
- [ ] Developed in Ontario by an Ontario corporation
- [ ] Not primarily a search engine, portal, or internet service
- [ ] Not primarily for internal business use
- [ ] Not online gambling

### Qualifying Expenditures

| Category | Details |
|----------|---------|
| Ontario labour | Salary of employees working on the product in Ontario |
| Marketing and distribution | Costs directly related to marketing the product |
| Maximum | No annual cap on expenditures |

### CC Fit Assessment: STRONG (If Eligible)

OASIS AI platform could qualify as interactive digital media if it meets the interactivity requirement. SaaS platforms with user-facing AI interaction are a strong fit.

**Key question:** Does OASIS qualify as "interactive digital media" under Ontario Creates' definition? The product must be primarily for entertainment, education, or information and involve user interaction.

**Action item:** Apply for a certificate of eligibility from Ontario Creates BEFORE claiming. This is a two-stage process:
1. Ontario Creates certifies the product
2. CRA processes the tax credit claim

### Application Process

**Step 1 — Pre-Application Review**
- [ ] Review Ontario Creates guidelines for eligible products
- [ ] Determine if OASIS product meets interactivity definition
- [ ] Consider applying for a pre-certification ruling (informal inquiry to Ontario Creates)

**Step 2 — Certificate of Eligibility Application**
- [ ] Apply to Ontario Creates with: product description, demo/prototype, business plan, expenditure summary
- [ ] Ontario Creates reviews and certifies (8-16 weeks)
- [ ] Certification is required before CRA claim

**Step 3 — Claim on Corporate Tax Return**
- [ ] File with T2 corporate return (CCPC required)
- [ ] Include Ontario Creates certificate number
- [ ] Credit is 40% of qualifying expenditures

### OIDMTC vs. OITC vs. SR&ED: Stacking Rules

- OIDMTC and SR&ED **cannot be claimed on the same expenditures**
- If work qualifies for both, choose the higher value:
  - SR&ED (federal 35% + OITC 8% = 43%) vs. OIDMTC (40%)
  - SR&ED generally wins for pure R&D work
  - OIDMTC wins for product development work that is NOT R&D (design, UI/UX, marketing)
- Strategy: claim SR&ED on research work, OIDMTC on non-R&D product development

**Estimated value for CC:**
- $50K non-R&D product development labour x 40% = $20,000 credit

---

## 11. OITC — Ontario Innovation Tax Credit

**Program Type:** Refundable tax credit (Ontario)
**Rate:** **8%** of qualifying SR&ED expenditures incurred in Ontario
**Claimed on:** T2 corporate return (automatic with SR&ED claim)

### How It Works

When you file a federal SR&ED claim, Ontario automatically calculates the OITC based on the Ontario portion of your expenditures. No separate application required.

### Eligibility

- [ ] Canadian-controlled private corporation (CCPC)
- [ ] Incurred SR&ED expenditures in Ontario
- [ ] Filed federal SR&ED claim (T661)

### Calculation for CC

Using the SR&ED numbers from Section 1:
- Total qualifying SR&ED expenditure in Ontario: $121,250
- OITC: $121,250 x 8% = **$9,700**
- This is ON TOP of the federal 35% SR&ED credit

### CC Fit Assessment: AUTOMATIC

Once CC incorporates and claims SR&ED, OITC is free money. No extra paperwork. Just ensure SR&ED expenditures are incurred in Ontario (or Quebec equivalent after move).

**Important:** After moving to Montreal, Ontario OITC no longer applies. Quebec has its own provincial SR&ED credit (Section 17 below).

---

## 12. Starter Company Plus (Ontario)

**Program Type:** Non-repayable grant
**Amount:** Up to **$5,000**
**Administering Body:** Small Business Enterprise Centres (local municipalities)
**Website:** ontario.ca/page/start-business

### Eligibility Checklist

- [ ] Ontario resident, 18 years or older
- [ ] Starting a new business OR expanding an existing business (< 5 years old)
- [ ] Not a franchise
- [ ] Willing to complete training program (typically 3-5 days)
- [ ] Create a business plan as part of the program

### Application Process

- [ ] Contact local Small Business Enterprise Centre (Simcoe County for Collingwood)
- [ ] Complete application and eligibility screening
- [ ] Attend mandatory business training workshop
- [ ] Develop business plan with mentor support
- [ ] Present business plan to review committee
- [ ] If approved, receive up to $5K grant (no repayment)

### CC Fit Assessment: EASY WIN

$5K free money for completing a training program. Low effort, moderate reward. Apply before Montreal move while still Ontario resident.

**Timing:** Do this immediately. Program availability varies by region and funding cycles.

---

## 13. Ontario Centres of Excellence / Ontario Vehicle Innovation Network

**Program Type:** Various innovation funding
**Note:** Ontario Centres of Excellence (OCE) merged into Ontario Vehicle Innovation Network (OVIN) and other programs. AI/software companies may have limited access to current programs, which tend to focus on automotive and advanced manufacturing.

### CC Fit Assessment: LOW (Currently)

Check ontarioinnovates.ca for current AI-eligible programs. Most OCE successor programs are sector-specific. Revisit if Ontario launches new AI-specific funding.

---

## 14. Ontario Together Fund and Provincial Innovation Programs

**Program Type:** Various grants and investments
**Note:** Ontario provincial programs change frequently with government priorities.

### Current Opportunities to Monitor

| Program | Type | CC Relevance |
|---------|------|-------------|
| Ontario Together Fund | Varies | Monitor for AI/tech streams |
| Ontario Trillium Foundation | Grants for social impact | Low (for-profit limitation) |
| Ontario Capital Growth Corporation | Venture capital | For larger raises |
| Ontario Scale-Up Voucher | Subsidized consulting | Good for growth strategy |

### Action Item

- [ ] Set Google Alert for "Ontario AI funding" and "Ontario tech grants"
- [ ] Check ontario.ca/page/available-funding-opportunities monthly
- [ ] Register with Ontario Business Registry for program notifications

---

## 15. Quebec — CDAE (e-Business Tax Credit)

**Program Type:** Refundable tax credit (Quebec)
**Rate:** **24%** of qualifying salaries for e-business activities
**Administering Body:** Investissement Quebec (certification) + Revenu Quebec (claim)
**Full Name:** Credit d'impot pour le developpement des affaires electroniques

### What It Is

Quebec's signature tech incentive. A 24% refundable credit on salaries paid to employees performing qualifying e-business activities. This is why Montreal is a tech hub.

### Qualifying Activities

- [ ] Design and development of information systems
- [ ] E-business solutions development
- [ ] IT infrastructure design and integration
- [ ] AI/ML development (explicitly included)
- [ ] SaaS product development and maintenance
- [ ] Data analytics and business intelligence

### Eligibility Requirements

- [ ] Corporation with establishment in Quebec
- [ ] Minimum 6 eligible full-time employees throughout the year (OR qualifying startup exemption)
- [ ] At least 75% of activities must be in the e-business sector
- [ ] Employees must work in Quebec

### Salary Cap

- Per-employee salary cap: approximately $83,333/year for credit calculation
- Maximum credit per employee: $83,333 x 24% = approximately **$20,000/year**

### CC Fit Assessment: STRONG (Post-Move, Post-Hire)

The 6-employee minimum is a barrier initially. However:
- Quebec periodically offers startup exemptions or phased-in requirements
- As OASIS grows and hires, this becomes a major incentive
- At 6 employees x $20K/each = $120K annual refundable credit

**This is the single biggest reason to locate tech operations in Quebec rather than Ontario.**

### Application Process

**Step 1 — Obtain Certification from Investissement Quebec**
- [ ] Apply for "Attestation d'admissibilite" (eligibility certificate)
- [ ] Submit: company description, employee list, activity breakdown
- [ ] Investissement Quebec reviews (4-8 weeks)
- [ ] Must be renewed annually

**Step 2 — Claim on Quebec Corporate Return**
- [ ] File with CO-17 (Quebec corporate tax return)
- [ ] Include Investissement Quebec certificate
- [ ] Credit is refundable — paid out even if no tax owing

---

## 16. Quebec — Investissement Quebec

**Program Type:** Various loans, loan guarantees, equity investments, tax credits
**Website:** investquebec.com

### Programs Relevant to CC

**ESSOR Program**
- Loans and loan guarantees for investment projects
- Amount: $50K-$500K+
- For: equipment, leasehold improvements, working capital
- Competitive interest rates (often below commercial)

**PME en action**
- Financing for SME growth projects
- Flexible terms, patient capital
- Especially favorable for tech companies

**Start-Up Quebec**
- Financing for new businesses in Quebec
- CC would qualify after establishing Quebec operations

**Immigrant Entrepreneur Program**
- Not applicable to CC (Canadian citizen), but relevant if CC hires internationally

### Application Process

- [ ] Contact Investissement Quebec regional office (Montreal)
- [ ] Meet with advisor to discuss funding needs
- [ ] Submit project proposal and financial projections
- [ ] Review and approval: 4-12 weeks depending on program
- [ ] Multiple programs can be combined

### CC Fit Assessment: STRONG (Post-Move)

Investissement Quebec is aggressive about attracting tech companies to the province. CC's AI SaaS company is exactly what they want. Contact them within first month of Montreal residency.

---

## 17. Quebec — SR&ED Provincial Credit

**Program Type:** Refundable tax credit (Quebec)
**Rate:** **14%** of qualifying SR&ED expenditures in Quebec (for CCPCs)
**Note:** This REPLACES the Ontario OITC (8%) after CC moves to Quebec

### Combined Rate in Quebec

| Level | Rate |
|-------|------|
| Federal SR&ED (CCPC) | 35% |
| Quebec provincial SR&ED | 14% |
| **Combined** | **49%** |

**Quebec beats Ontario for SR&ED.** Ontario gives 43% combined (35% + 8%). Quebec gives **49%** combined (35% + 14%). This is another financial argument for the Montreal move.

### Eligibility

- Same qualifying criteria as federal SR&ED
- Must have establishment in Quebec
- Expenditures must be incurred in Quebec
- Claimed on Quebec corporate return (CO-17)

### Additional Quebec R&D Incentives

**Superdeduction for R&D (Quebec Budget 2024+)**
- Check current Revenu Quebec for additional R&D deductions
- Quebec frequently introduces bonus incentives for AI/tech R&D
- These stack with federal SR&ED

---

## 18. Quebec — NovaScience and FRQNT

**Program Type:** Research collaboration funding
**Administering Body:** Fonds de recherche du Quebec (FRQ)

### NovaScience

- Supports collaborative R&D between companies and Quebec research institutions
- Covers: salary of research staff, equipment, travel
- Typical amount: $50K-$200K per project
- Requires academic partner (university professor as co-PI)

### FRQNT (Fonds de recherche du Quebec — Nature et technologies)

- Funds applied research in technology
- Industry partnership programs available
- CC could partner with a MILA researcher for subsidized AI research

### CC Fit Assessment: MODERATE (Requires Academic Partner)

After moving to Montreal, CC could partner with MILA, McGill, or UdeM researchers. The funding covers research costs, and the academic partner provides world-class AI expertise.

---

## 19. Quebec — AI Ecosystem (MILA, IVADO, Scale AI)

### MILA (Montreal Institute for Learning Algorithms)

- World-leading AI research institute (Yoshua Bengio)
- Not a funding program but a **partnership ecosystem**
- MILA startup program: office space, mentorship, access to researchers
- CC should attend MILA events and explore startup partnership after Montreal move

### IVADO (Institute for Data Valorization)

- Collaboration between MILA, HEC Montreal, Polytechnique, UdeM
- Offers: funded internships, collaborative research projects, training
- CC could access AI talent through IVADO partnership

### Scale AI (Canada's AI Supercluster)

- **Type:** Non-repayable contribution
- **Amount:** Up to $1M+ for AI adoption/development projects
- **Focus:** AI supply chain solutions (broader than it sounds)
- **Requires:** Industry-academic collaboration
- **CC Fit:** Moderate — depends on project alignment with Scale AI priorities

### NextAI (Next Canada)

- AI-focused accelerator program
- Based in Toronto but national scope
- No equity taken (rare for accelerators)
- Provides: mentorship, workspace, $20K-$50K in support services
- CC Fit: STRONG — AI SaaS company is core focus

---

## 20. Cloud Credits and Platform Programs

### Tier 1 — Cloud Infrastructure (Apply Immediately)

| Program | Credits | Duration | Eligibility | Application |
|---------|---------|----------|-------------|-------------|
| **AWS Activate** | $10K-$100K | 1-2 years | Startup, < $10M funding | Through affiliated accelerator or direct application at aws.amazon.com/activate |
| **Google Cloud for Startups** | Up to **$200K** | 2 years | Startup, funded or accepted to partner program | cloud.google.com/startup |
| **Microsoft for Startups (Founders Hub)** | Up to **$150K** Azure | 2 years | Any stage startup | startups.microsoft.com |
| **Oracle for Startups** | Up to $100K Oracle Cloud | 1 year | Tech startup | oracle.com/startup |
| **IBM Cloud** | Up to $120K credits | 1 year | Startup | ibm.com/partnerplus/isv |

**Total cloud credits accessible:** $580K-$670K

### Tier 2 — AI/ML Specific

| Program | Credits | Details |
|---------|---------|---------|
| **OpenAI Startup Program** | API credits (variable) | For startups building on GPT |
| **Anthropic Partnerships** | Variable | Enterprise partnerships for high-volume |
| **Cohere for AI** | Free tier + startup credits | NLP-focused |
| **Hugging Face** | Free tier, compute credits | Open-source ML |
| **Weights & Biases** | Free for academics/startups | ML experiment tracking |

### Tier 3 — SaaS and Development Tools

| Program | Benefit | Details |
|---------|---------|---------|
| **Stripe Atlas** | Free incorporation + payments | stripe.com/atlas |
| **HubSpot for Startups** | 90% off Year 1 (worth $5K+) | Through affiliated accelerator/VC |
| **Notion for Startups** | Free Plus plan (6 months) | Through startup program |
| **Figma for Startups** | Free Organization plan (2 years) | figma.com/startups |
| **MongoDB Atlas** | Free tier + $500-$5K credits | MongoDB startup program |
| **Vercel** | Free Pro plan (1 year) | vercel.com/startups |
| **GitHub** | Free Team plan | github.com/startups |
| **1Password** | Free Teams plan (1 year) | 1password.com/startups |
| **Brex** | $150K in partner credits bundle | brex.com/startups |

### Application Strategy

**Step 1 (This Week):** Apply for Microsoft Founders Hub (easiest, no requirements) and AWS Activate (direct track).

**Step 2 (This Month):** Apply for Google Cloud for Startups through a partner program (CDL, Centech, or similar accelerator affiliation increases approval rate).

**Step 3 (Ongoing):** As CC joins an accelerator (Section 21), most of these become available through the accelerator's partner perks package.

---

## 21. Accelerators and Incubators

### Tier 1 — Highest Value for CC

**CDL (Creative Destruction Lab)**
- Location: Toronto (Rotman), Montreal, and other sites
- Focus: AI, ML, science-based ventures
- Format: 9-month program, objective-based milestones
- Equity: **None taken** (CDL does not take equity)
- Value: Mentorship from experienced tech entrepreneurs and investors, demo day exposure
- CC Fit: **STRONGEST FIT.** AI SaaS company, growing revenue, no equity cost.
- Apply: cdl.ca (annual cohort, typically starts September)
- Deadline: Usually April-June for fall cohort

**Centech (Montreal)**
- Affiliated with ETS (Ecole de technologie superieure)
- Focus: Deep tech, AI, hardware
- Equity: None (some programs may differ)
- Provides: office space, mentorship, access to ETS labs, $15K-$50K in support
- CC Fit: **STRONG.** Located in Montreal, AI-focused, no equity.
- Apply: centech.co (rolling admissions)

**Next AI (Next Canada)**
- Focus: AI-specific accelerator
- Equity: None
- Provides: mentorship, workspace, peer network, $20K-$50K in services
- CC Fit: **STRONG.** Pure AI focus.
- Apply: nextcanada.com (annual cohort)

### Tier 2 — Strong Options

**DMZ (Toronto Metropolitan University)**
- Top university incubator in Canada
- No equity taken
- Provides: workspace, mentorship, investor access
- Focus: tech startups broadly
- CC Fit: Good (broad tech, not AI-specific)

**Communitech (Kitchener-Waterloo)**
- Hub for Canadian tech companies
- Various programs (Rev, Bold, etc.)
- Provides: workspace, events, peer community
- CC Fit: Moderate (geographic mismatch with Montreal move)

**District 3 (Concordia University, Montreal)**
- Innovation center and startup incubator
- No equity
- Good for early-stage tech companies
- CC Fit: Good (Montreal-based, accessible post-move)

**Notman House (Montreal)**
- Tech startup community hub
- Workspace, events, networking
- CC Fit: Good (Montreal-based)

### Tier 3 — High Value but Equity Cost

**Y Combinator**
- Amount: $500K ($125K for 7% equity + $375K uncapped SAFE)
- Location: San Francisco (remote participation possible)
- Prestige: Highest in the world
- CC Fit: Strong business, but 7% equity is expensive
- Apply: ycombinator.com (biannual batches)

**Techstars**
- Amount: $120K for 6% equity
- Various programs worldwide (including Toronto)
- Strong mentor network
- CC Fit: Good, but 6% is steep for current stage

### Application Priority for CC

1. **CDL Toronto or Montreal** — Apply NOW for fall 2026 cohort (no equity, AI-focused)
2. **Centech** — Apply after Montreal move (rolling admissions, AI-focused, local)
3. **Microsoft Founders Hub** — Apply immediately (cloud credits, no application friction)
4. **Next AI** — Apply for next cohort (AI-specific, no equity)
5. **Y Combinator** — Consider when ARR exceeds $500K+ (equity cost justified at scale)

---

## 22. Stacking Strategy — Maximum Total Funding

### The Rules of Stacking

| Rule | Detail |
|------|--------|
| SR&ED + IRAP | Allowed, but IRAP-funded salaries reduce SR&ED qualifying expenditures |
| SR&ED + OIDMTC | Cannot claim on same expenditures — split by activity type |
| SR&ED + CDAE (Quebec) | Different programs (federal vs. provincial), generally stackable on different expenditure pools |
| IRAP + any loan program | Allowed — IRAP is a grant, loans are debt |
| Cloud credits + everything | Cloud credits are private programs, no government conflict |
| Multiple provincial credits | Can only claim in the province where work is performed |
| Grants as taxable income | Most grants and credits reduce deductible expenses or are included in income — net positive but plan for tax impact |

### Stacking Anti-Patterns (What NOT To Do)

- Do NOT claim SR&ED and OIDMTC on the same salary dollars
- Do NOT count IRAP-funded salary in your SR&ED qualifying expenditure calculation
- Do NOT claim work done in Ontario for Quebec credits (or vice versa)
- Do NOT start an IRAP project before the Contribution Agreement is signed
- Do NOT overstate R&D percentage of your time — CRA will audit the entire claim

### CC's Optimal Stack (Year 1 — 2026/2027, as CCPC)

**Scenario: OASIS incorporated as CCPC, 1-2 employees, operating in Ontario then Quebec**

| Program | Type | Estimated Value | Status |
|---------|------|-----------------|--------|
| SR&ED (federal, 35%) | Tax credit | $42,437 | Apply with first corporate return |
| OITC/Quebec provincial SR&ED | Tax credit | $9,700-$16,975 | Automatic with SR&ED |
| IRAP | Grant | $64,000-$96,000 | Apply after incorporation |
| CSBFP loan | Subsidized loan | $50,000-$75,000 | Apply through RBC |
| Cloud credits (all platforms) | Credits | $300,000-$500,000 | Apply immediately |
| Starter Company Plus | Grant | $5,000 | Apply before Montreal move |
| CDL accelerator | Services | $50,000+ (in-kind) | Apply for fall 2026 |
| **Total (Year 1)** | | **$521K-$740K+** | |

### CC's Optimal Stack (Year 2 — 2027/2028, Quebec-based, growing team)

| Program | Type | Estimated Value | Status |
|---------|------|-----------------|--------|
| SR&ED (federal, 35%) | Tax credit | $60,000+ | Larger team, more R&D |
| Quebec SR&ED (14%) | Tax credit | $24,000+ | Higher provincial rate |
| CDAE (Quebec, 24%) | Tax credit | $40,000-$120,000 | 2-6 employees in e-business |
| IRAP (continued or new project) | Grant | $100,000+ | Expanded scope |
| Mitacs intern | Subsidized hire | $15,000-$30,000 | Partner with Montreal university |
| CanExport | Grant | $25,000-$50,000 | International market expansion |
| Investissement Quebec | Subsidized loan | $50,000-$200,000 | Growth financing |
| **Total (Year 2)** | | **$314K-$580K+** | |

---

## 23. Master Application Timeline

### IMMEDIATE (Now — April 2026)

| Action | Program | Priority | Time Required |
|--------|---------|----------|---------------|
| Start R&D time tracking | SR&ED preparation | CRITICAL | 15 min/week ongoing |
| Apply for Microsoft Founders Hub | Cloud credits ($150K) | HIGH | 1 hour |
| Apply for AWS Activate | Cloud credits ($10K-$100K) | HIGH | 1 hour |
| Apply for Google Cloud for Startups | Cloud credits ($200K) | HIGH | 2 hours |
| Contact Starter Company Plus (Simcoe County) | $5K grant | MEDIUM | 1 hour initial |
| Begin incorporation planning | Enables IRAP, OIDMTC, OITC, CDAE | CRITICAL | Ongoing with lawyer |

### Q2 2026 (April-June)

| Action | Program | Priority | Time Required |
|--------|---------|----------|---------------|
| Incorporate as CCPC | All corporate programs | CRITICAL | 2-4 weeks with lawyer |
| Contact NRC for IRAP ITA meeting | IRAP ($100K+) | HIGH | 1 hour + follow-up meetings |
| Apply for CDL fall cohort | Accelerator (no equity) | HIGH | 10-20 hours for application |
| Apply for Next AI | Accelerator (no equity) | MEDIUM | 10-15 hours |
| Complete Starter Company Plus training | $5K grant | MEDIUM | 3-5 days |
| Contact Futurpreneur | $60K loan + mentorship | MEDIUM | 2-3 hours initial |
| File 2025 T1 with business deductions | Tax filing | CRITICAL | Deadline June 15 |

### Q3 2026 (July-September — Montreal Move)

| Action | Program | Priority | Time Required |
|--------|---------|----------|---------------|
| Establish Quebec operations | Enables Quebec credits | HIGH | Part of move logistics |
| Contact Investissement Quebec | Loans + support | HIGH | Half-day meeting |
| Apply for CSBFP through RBC or Desjardins | $50K-$75K equipment/WC | MEDIUM | 5-10 hours |
| Begin IRAP project (if approved) | Execute funded R&D | HIGH | Ongoing |
| Explore Centech application | Montreal AI incubator | MEDIUM | 5-10 hours |
| Connect with MILA startup community | Ecosystem access | LOW | Attend events |

### Q4 2026 (October-December)

| Action | Program | Priority | Time Required |
|--------|---------|----------|---------------|
| Prepare first SR&ED claim | $42K-$52K tax credit | HIGH | 20-40 hours (or hire consultant) |
| Prepare OIDMTC application (Ontario Creates) | $20K credit (on Ontario work) | MEDIUM | 10-20 hours |
| Apply for Mitacs intern | Subsidized AI hire | MEDIUM | 5-10 hours |
| Assess CDAE eligibility (if 6+ employees) | $120K annual credit | MEDIUM | 5 hours assessment |
| Apply for CanExport (if international sales) | $25K-$50K grant | LOW | 10 hours |

### 2027 and Beyond

| Action | Program | Priority |
|--------|---------|----------|
| File SR&ED with corporate T2 return | Annual (within 18 months of year-end) |
| Renew CDAE certification annually | Annual |
| Apply for Scale AI project funding | When project scope warrants ($250K+) |
| Explore BDC venture capital | When ARR exceeds $1M+ |
| Consider SIF | When project exceeds $10M investment |
| Y Combinator application | When ARR exceeds $500K+ (equity justified) |

---

## 24. Application Best Practices

### Documentation Protocol (Start TODAY)

**SR&ED Evidence Chain:**
1. **Weekly time log:** Date, hours, project name, brief description of R&D work done
2. **Uncertainty journal:** Before starting new R&D task, write 2-3 sentences: what you don't know, why existing approaches fail, what you'll try
3. **Git commits as evidence:** Use descriptive commit messages that reference experimental work ("test hypothesis: RAG with semantic chunking vs. fixed-size chunking for accuracy improvement")
4. **Save failures:** Screenshots, error logs, benchmark results from failed approaches are MORE valuable than successes for SR&ED
5. **Iteration records:** Document each approach tried and why you moved to the next one
6. **Separate R&D from operations:** Track time in distinct categories — never blur the line between maintaining existing product and genuine R&D

**Template for Weekly R&D Log:**
```
WEEK OF: [Date]
TOTAL R&D HOURS: [X]

PROJECT: [Name]
HOURS: [X]
UNCERTAINTY: [What we didn't know]
WORK DONE: [What we tried]
OUTCOME: [Result — success, failure, partial, pivoted]
NEXT STEPS: [What we'll try next based on results]

[Repeat for each project]
```

### Grant Application Writing Tips

1. **Lead with the problem, not the technology.** Reviewers want to know what pain you're solving before how you solve it.

2. **Quantify everything.** "Improve efficiency" is weak. "Reduce processing time from 4 hours to 12 minutes (95% reduction)" is strong.

3. **Show traction.** Revenue, users, growth rate. Programs fund momentum, not ideas.

4. **Be specific about use of funds.** "Hire 2 ML engineers at $85K each + $20K cloud computing for model training" beats "general R&D expenses."

5. **Address risk.** Acknowledge technical risks and explain mitigation strategies. This shows maturity.

6. **Know the reviewer.** IRAP reviewers are technical. Futurpreneur reviewers are business-focused. SR&ED reviewers want uncertainty documentation. Tailor your language.

7. **Follow the rubric.** Every program publishes evaluation criteria. Answer each criterion explicitly. Do not assume they will infer.

### Relationship Management

| Contact | When | How |
|---------|------|-----|
| NRC ITA (IRAP) | Before formal application | Request introductory meeting, build rapport, ask for advice |
| Ontario Creates (OIDMTC) | Before claiming | Request pre-certification guidance |
| Investissement Quebec | Month 1 in Montreal | In-person meeting at regional office |
| SR&ED consultant | After incorporation | Interview 2-3, check references, negotiate contingency rate |
| BDC advisor | Alongside loan application | Free advisory — use it |

### Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---------|-------------|-----------|
| Starting IRAP project before agreement signed | All expenditures before agreement are ineligible | Wait for signed Contribution Agreement |
| Claiming routine development as SR&ED | CRA rejects or claws back entire claim | Document genuine technological uncertainty |
| Not incorporating before applying | Locked out of IRAP, OIDMTC, OITC, CDAE | Incorporate ASAP |
| Applying for the wrong CSBFP category | Loan denied or reduced | Clarify eligible categories with lender first |
| Mixing personal and business expenses | Audit risk, disqualification from programs | Separate bank accounts from day one |
| Over-committing to accelerator equity deals | Dilution regret at scale | Prioritize no-equity programs (CDL, Centech, Next AI) first |
| Not tracking R&D time contemporaneously | Reconstructed logs rejected by CRA | Start weekly time tracking immediately |
| Claiming same expenditure for SR&ED and OIDMTC | One claim will be denied | Allocate each dollar to one program only |

---

## 25. Stacking Calculator — CC's 2026-2027 Scenario

### Assumptions

| Parameter | Value |
|-----------|-------|
| Entity | CCPC (incorporated mid-2026) |
| CC's salary | $100,000 |
| R&D time percentage | 50% |
| Additional hires (by end 2026) | 1 developer ($80K) |
| Cloud/API spend | $15,000 |
| Equipment purchases | $25,000 |
| Location | Ontario (H1 2026), Quebec (H2 2026 onward) |

### Year 1 Funding Stack (2026-2027)

**Tax Credits (Refundable Cash Back):**

| Credit | Calculation | Amount |
|--------|-------------|--------|
| SR&ED federal (35%) | ($50K CC R&D salary + $40K dev R&D salary + $49.5K overhead proxy + $10K cloud R&D) x 35% | **$52,325** |
| Provincial SR&ED (8% ON or 14% QC, blended) | $149.5K x 11% (blended rate, split year) | **$16,445** |
| OIDMTC (40%, on non-R&D product dev in Ontario) | $30K eligible labour x 40% | **$12,000** |
| **Subtotal Tax Credits** | | **$80,770** |

**Grants (Non-Repayable):**

| Grant | Amount |
|-------|--------|
| IRAP (NRC) | $72,000 (80% of $90K eligible salary) |
| Starter Company Plus | $5,000 |
| **Subtotal Grants** | **$77,000** |

**Cloud Credits:**

| Platform | Credits |
|----------|---------|
| Microsoft Founders Hub | $150,000 |
| Google Cloud for Startups | $200,000 |
| AWS Activate | $25,000 |
| Other (MongoDB, Vercel, etc.) | $10,000 |
| **Subtotal Cloud Credits** | **$385,000** |

**Subsidized Loans:**

| Loan | Amount | Terms |
|------|--------|-------|
| CSBFP | $50,000 | Prime + 3%, 85% guaranteed |
| BDC Small Business | $50,000 | Competitive rate, unsecured |
| **Subtotal Loans** | **$100,000** |

**Accelerator Value (In-Kind):**

| Program | Estimated Value |
|---------|----------------|
| CDL (if accepted) | $50,000+ (mentorship, network) |
| Centech (if accepted) | $25,000+ (space, mentorship) |
| **Subtotal In-Kind** | **$50,000-$75,000** |

### Year 1 Total

| Category | Amount |
|----------|--------|
| Tax credits (cash refund) | $80,770 |
| Grants (free money) | $77,000 |
| Cloud credits (infrastructure) | $385,000 |
| Subsidized loans (cheap debt) | $100,000 |
| Accelerator in-kind | $50,000-$75,000 |
| **TOTAL YEAR 1 VALUE** | **$692,770 - $717,770** |

### Year 2 Projection (2027-2028, Full Quebec, 4-6 Employees)

| Category | Amount |
|----------|--------|
| SR&ED federal (35%) + Quebec (14%) | $120,000+ |
| CDAE (24% on Quebec salaries, 6 employees) | $100,000+ |
| IRAP (continued) | $100,000+ |
| CanExport | $25,000-$50,000 |
| Mitacs intern | $15,000 |
| Cloud credits (carry-over) | $200,000+ |
| **TOTAL YEAR 2 VALUE** | **$560,000+** |

### Two-Year Combined Funding Potential: $1.25M-$1.5M+

---

## Appendix A: Key Contacts and Links

| Resource | Contact/URL |
|----------|-------------|
| NRC IRAP | 1-877-994-4727, nrc.canada.ca/en/support-technology-innovation |
| CRA SR&ED | canada.ca/en/revenue-agency/services/scientific-research-experimental-development-tax-incentive-program |
| Ontario Creates (OIDMTC) | ontariocreates.ca/tax-incentives/oidmtc |
| Investissement Quebec | investquebec.com, 1-866-870-0437 |
| BDC | bdc.ca, 1-877-232-2269 |
| Futurpreneur | futurpreneur.ca, 1-866-646-8853 |
| CDL | cdl.ca |
| Centech | centech.co |
| Scale AI | scaleai.ca |
| MILA | mila.quebec |
| AWS Activate | aws.amazon.com/activate |
| Google Cloud for Startups | cloud.google.com/startup |
| Microsoft Founders Hub | startups.microsoft.com |
| Mitacs | mitacs.ca |
| CanExport | tradecommissioner.gc.ca/funding |
| Starter Company Plus | ontario.ca/page/start-business |

## Appendix B: SR&ED Technical Narrative Examples for AI/ML

### Example 1: Novel Prompt Engineering Architecture

```
PROJECT: Adaptive Multi-Agent Prompt Architecture for Business Automation
PERIOD: March 2026 — August 2026

UNCERTAINTY: It was not known whether a multi-agent LLM architecture could
reliably coordinate complex multi-step business workflows without
hallucination or task drift. Existing single-prompt approaches produced
error rates above 15% on multi-step tasks, which was unacceptable for
production deployment. No published research demonstrated reliable
multi-agent coordination for our specific use case (SaaS client onboarding
with variable data schemas).

INVESTIGATION: We designed a systematic series of experiments testing
5 architectural approaches:
1. Sequential chain-of-thought (baseline): 18% error rate
2. Parallel agents with majority voting: 12% error rate
3. Hierarchical agent with verification loop: 8% error rate
4. Debate-style multi-agent with arbitrator: 6% error rate
5. Hybrid hierarchical-debate with domain-specific grounding: 2.3% error rate

Each architecture was tested against a standardized test suite of 200
business workflow scenarios with known correct outputs. We measured:
accuracy, latency, cost, and failure modes.

ADVANCEMENT: We developed a hybrid hierarchical-debate architecture (approach 5)
that achieved a 2.3% error rate, an 87% reduction from baseline. The key
innovation was a domain-specific grounding layer that constrained agent
outputs to validated schema patterns, preventing hallucination without
sacrificing flexibility. This approach was not described in existing
literature and represents a genuine advancement in multi-agent LLM
coordination for structured business tasks.
```

### Example 2: Fine-Tuning for Domain-Specific Accuracy

```
PROJECT: Domain-Adapted Language Model for Vertical SaaS Application
PERIOD: June 2026 — October 2026

UNCERTAINTY: It was unknown whether fine-tuning a general-purpose LLM on
domain-specific data (< 10,000 examples) could achieve specialist-level
accuracy for [specific vertical] without catastrophic forgetting of general
capabilities. Published benchmarks showed mixed results for small-dataset
fine-tuning, and no prior work addressed our specific domain vocabulary
and task requirements.

INVESTIGATION: We conducted a systematic investigation involving:
1. Baseline evaluation of 3 foundation models on domain-specific test suite
2. Data augmentation techniques to expand training set (synthetic examples)
3. Parameter-efficient fine-tuning (LoRA, prefix tuning, adapter layers)
4. Evaluation of catastrophic forgetting using general capability benchmarks
5. Iterative hyperparameter optimization across 47 training runs

ADVANCEMENT: We identified that [specific technique] combined with
[specific approach] achieved 94% domain accuracy while retaining 98% of
general capabilities, compared to 71% domain accuracy for the base model.
We documented the minimum viable training set size (4,200 examples with
augmentation) and optimal hyperparameter ranges for our model class.
```

## Appendix C: IRAP Project Proposal Template

```
1. COMPANY OVERVIEW
   - Legal name, incorporation date, location
   - Number of employees, revenue (last 2 years)
   - Core technology and products
   - Market and competitive landscape

2. PROJECT DESCRIPTION
   - Project title and duration (6-18 months)
   - Technical objectives (specific, measurable)
   - Innovation: what is new about this approach
   - Technical challenges and risks
   - Methodology and work plan
   - Expected outcomes and deliverables

3. MARKET OPPORTUNITY
   - Target market size (TAM, SAM, SOM)
   - Customer validation (existing revenue, letters of intent, pilot customers)
   - Competitive advantage
   - Revenue model and pricing

4. PROJECT TEAM
   - Key personnel (name, role, qualifications)
   - Time commitment to project (% FTE)
   - Subcontractors (if any)

5. BUDGET
   - Salary costs by person (monthly, with R&D %)
   - Contractor costs
   - Total eligible costs
   - IRAP contribution requested (up to 80% of eligible costs)
   - Company co-funding commitment (minimum 20%)

6. MILESTONES
   - 3-5 project milestones with deliverables and dates
   - Go/no-go decision points
   - Metrics for success at each milestone

7. COMMERCIALIZATION PLAN
   - How project results will be brought to market
   - Sales and marketing strategy
   - Revenue projections (3-year)
   - IP strategy (patents, trade secrets, copyright)
```

## Appendix D: Incorporation Checklist (Prerequisite for Most Programs)

Incorporation as a CCPC is the single highest-leverage action CC can take to access funding. Many programs (IRAP, OIDMTC, OITC, CDAE, enhanced SR&ED) require corporate status.

**Steps:**

- [ ] Choose a lawyer or use online service ($1,500-$5,000)
- [ ] Federal incorporation (Corporations Canada) vs. Ontario/Quebec provincial
- [ ] Recommendation: Federal incorporation (valid in all provinces)
- [ ] Choose fiscal year-end (consider tax planning — December 31 is standard but not required)
- [ ] Issue shares (Class A common for CC, consider Class B preference for future flexibility)
- [ ] Register for: GST/HST number, payroll account, corporate income tax account
- [ ] Open corporate bank account (separate from personal)
- [ ] Set up payroll (CC must be on payroll for IRAP and optimal SR&ED claiming)
- [ ] Transfer business assets to corporation (s.85 rollover — tax-deferred)
- [ ] Update Stripe, Wise, and all payment processors to corporate entity
- [ ] Update contracts with Bennett and other clients

**Cost:** $1,500-$5,000 (lawyer) + $200 (federal incorporation fee) + $500-$1,000 (accounting setup)

**ROI:** Incorporation cost is recovered in the FIRST SR&ED claim alone ($52K CCPC vs. $18K sole prop = $34K difference). Plus access to IRAP ($72K+), OIDMTC ($12K+), CDAE (eventually $120K+/year).

**Atlas recommendation:** Incorporate by June 2026 at the latest. Every month of delay is lost funding.

---

## Appendix E: Grant Accounting Treatment

Understanding how grants and credits affect your books:

| Program | Tax Treatment | Effect on Deductions |
|---------|--------------|---------------------|
| SR&ED ITC | Reduces the cost base of related expenses | Claimed R&D expenses reduced by ITC amount in following year |
| IRAP contribution | Included in income (but offsets expenses) | Net neutral — income offsets salary expense deduction |
| OIDMTC | Reduces qualifying expenditures | Similar to SR&ED — credit reduces deductible costs |
| CDAE | Refundable credit, reduces salary deduction | Claimed credit reduces deductible salary in following year |
| CSBFP loan | Not income (it's debt) | Interest is deductible as business expense |
| Cloud credits | Not income (private benefit) | Cannot deduct expenses covered by credits |
| Starter Company Plus | Taxable income (government grant) | Include in business income |
| CanExport | Reduces deductible expenses | Claimed expenses reduced by grant amount |

**Key principle:** Most government assistance reduces either your deductible expenses or must be included in income. You still come out ahead (you receive more than the tax cost), but budget for the tax impact. A $50K grant at a 25% tax rate costs $12.5K in tax — you net $37.5K.

---

*Document prepared by ATLAS — CC's CFO Agent*
*Total programs covered: 25+ federal, provincial, private, and institutional*
*Estimated 2-year accessible funding: $1.25M-$1.5M+*
*Critical prerequisite: CCPC incorporation (target: June 2026)*
*Next review: After incorporation and Montreal move*
