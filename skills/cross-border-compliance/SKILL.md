---
name: cross-border-compliance
description: >
  US/international payment compliance for Canadian sole proprietors and corporations.
  W-8BEN management (individual + entity), withholding tax recovery, 1099 interception,
  FX accounting (BoC noon rate), T1135 monitoring, Reg 105 contractor rules,
  multi-currency reconciliation. Prevents 30% backup withholding and $25/day T1135
  penalties. CC-specific: Wise USD, Stripe, Bennett (US client), Kraken.
triggers: [W-8BEN, withholding, 1099, cross-border, US tax, foreign tax, FX, exchange rate, T1135, international payment, Stripe, Wise, Bennett, USD income, foreign client, 1042-S, FATCA, treaty claim, backup withholding, FX gain, currency, Regulation 105, T4A-NR]
tier: core
dependencies: [accounting-advisor]
---

# Cross-Border Compliance — W-8BEN, Withholding Tax & International Payments

> Used when CC earns from US clients, holds USD, uses Stripe/Wise, or receives
> foreign payments. Prevents 30% withholding, T1135 penalties, and IRS letters.
> Covers sole proprietor now and corporation (W-8BEN-E) post-incorporation.

## Why This Matters for CC Right Now

Bennett (US client) paying OASIS for AI services. Without a valid W-8BEN on file,
Bennett is legally required to withhold 30% of every payment and remit it to the IRS.
That is CC's money, held by the US government, recoverable only by filing a US non-
resident return. The fix: one form, submitted once, renewed every 3 years.

---

## 1. W-8BEN Management

### When to Submit

Submit a W-8BEN to **any US person or entity paying you**, including:
- US clients (Bennett, any future US OASIS contracts)
- Stripe (if account holds USD or receives US payments)
- US freelance platforms (Upwork, Fiverr — US-based)
- US brokerages (if CC ever holds US securities outside RRSP/TFSA)
- Any US platform that asks for tax documentation

**Rule of thumb:** If a US entity sends you money and asks for tax forms, they need a W-8BEN.

### W-8BEN (Individual) vs W-8BEN-E (Entity)

| Form | Use When | CC's Status |
|------|----------|-------------|
| W-8BEN | You are a sole proprietor or individual | **Current — use this now** |
| W-8BEN-E | You are incorporated (OASIS Inc.) | Switch on incorporation |

When OASIS incorporates, file W-8BEN-E as the entity. Until then, W-8BEN as individual.

### Field-by-Field Guide for CC

```
Part I — Identification of Beneficial Owner

Line 1 — Name: Conaugh McKenna
Line 2 — Country of citizenship: Canada
Line 3 — Permanent residence address: [CC's current Collingwood ON address]
          City/State: Collingwood, Ontario
          Country: Canada
Line 4 — Mailing address: [same, unless different]
Line 5 — US TIN: Leave blank (Canadians do not need a US SSN/EIN)
Line 6a — Foreign TIN: [CC's Canadian SIN — 9-digit number]
Line 6b — FTIN not legally required: Leave unchecked (SIN is the FTIN)
Line 7 — Reference number: Leave blank
Line 8 — Date of birth: [CC's DOB in MM-DD-YYYY format]

Part II — Claim of Tax Treaty Benefits

Line 9 — Residence: Canada
Line 10 — Treaty claim (CRITICAL — this gets the 0% rate):
  "The beneficial owner is claiming the provisions of Article VII
   (Business Profits) of the Canada-US Tax Convention.
   The rate of withholding specified in the article is 0%."
  Type of income: Business profits / services income
  Article: VII
  Rate: 0%

Part III — Certification
  Sign and date. By signing, you certify you are the beneficial owner,
  not a US person, and the information is accurate.
```

### Why Article VII Gets 0%

Under the Canada-US Tax Convention, business profits earned by a Canadian resident
are only taxable in Canada — not the US — unless the business has a permanent
establishment (PE) in the US. CC has no US office, employees, or fixed place of
business, so the US has zero taxing rights. Result: 0% US withholding.

### Renewal

- W-8BEN expires after **3 calendar years** from the year it is signed
- Example: signed March 2026 — expires December 31, 2028
- The paying entity (Bennett, Stripe) should remind you, but do not rely on this
- Set a calendar reminder for January 2029 to resubmit
- If any information changes (address, entity type, incorporation), resubmit immediately

### What Happens Without It

Without a current W-8BEN on file, the payer **must** withhold 30% of gross payment
and remit to IRS. Recovery requires filing Form 1040-NR (US non-resident return) —
time-consuming, requires a US ITIN, and delays money by months or years.

### Record Keeping

- Keep a signed copy of every W-8BEN submitted
- Log: date submitted, submitted to whom, expiry date
- Store in `docs/compliance/` or equivalent folder
- Pair with confirmation email from payer that it was received and accepted

---

## 2. 1099 Management

### What Is a 1099

A 1099 is a US information return. 1099-NEC reports non-employee compensation
(services). 1099-K reports payment platform transactions. Neither should be issued
to a non-US person with a valid W-8BEN on file — but errors happen.

### 1099-NEC — Should Not Reach CC

With a valid W-8BEN, US clients should issue Form 1042-S instead of a 1099-NEC.
1042-S reports payments to foreign persons. If a client issues a 1099-NEC to CC
by mistake, it is their administrative error, not CC's tax liability.

### 1099-K — Stripe / PayPal Risk

Stripe may generate a 1099-K if:
- The Stripe account is configured as a US entity or US person
- Threshold exceeded: $5,000 USD (US 2024 threshold, state thresholds vary)

**Prevention:** Ensure Stripe account lists CC's Canadian address, Canadian business
information, and has W-8BEN on file via Stripe's tax settings dashboard.

### If CC Receives a 1099

1. Do not panic. It is not a tax bill.
2. Do not file a US tax return based on a 1099 alone.
3. Check: does CC have a valid W-8BEN on file with the issuer?
4. If yes: contact the issuer, request a corrected 1042-S in place of 1099.
5. If the IRS sends a CP2000 letter (underreporter inquiry): respond in writing,
   attach W-8BEN copy, state treaty exemption under Article VII.
6. CC does not have a PE in the US, so US taxing rights do not apply.

### Does CC Need to File a US Return

No, unless CC:
- Has a US permanent establishment (office, employees in the US)
- Has US-source income not covered by treaty (eg. US rental property, US employment)
- Elects to file for a refund of improperly withheld amounts

Business profit from services performed in Canada for US clients = Canadian-sourced
income. The Canada-US treaty assigns taxing rights to Canada only.

---

## 3. FX Accounting

### The Rule: Bank of Canada Noon Rate

CRA requires all foreign amounts on a T1/T2125 to be converted to CAD using the
**Bank of Canada nominal noon rate** for the transaction date.

- Source: bankofcanada.ca/rates/exchange/daily-exchange-rates/
- Download the annual average rate file for year-end reconciliation
- For individual transactions: use the rate on the date funds were received

### When to Use Which Rate

| Situation | Rate to Use |
|-----------|-------------|
| Single USD invoice paid on specific date | BoC noon rate on that date |
| Multiple small transactions in same month | BoC monthly average (acceptable for CRA) |
| Year-end foreign account balance (T1135) | BoC December 31 noon rate |
| Estimating quarterly income for installments | BoC rate on date of estimate |

### FX Gains and Losses on USD Accounts (s.39(2))

Holding USD cash in a Wise or RBC USD account creates FX exposure. When USD is
converted to CAD (or used to pay CAD-denominated expenses), a gain or loss arises.

- The gain or loss = (CAD value at disposition) minus (CAD value at acquisition)
- **$200 exemption:** First $200 of net annual FX gains is exempt (personal-use rule)
- Above $200: 50% capital gain inclusion applies (same as any capital gain)
- This applies to **cash currency**, not business receivables (those are business income)

**Practical example:**
- Receive USD $5,000 on Jan 15 when rate = 1.35 → ACB = CAD $6,750
- Convert to CAD on Mar 10 when rate = 1.40 → proceeds = CAD $7,000
- FX gain = $250 → minus $200 exemption = $50 taxable → $25 capital gain included

**Record keeping:** Log USD received (date, amount, BoC rate), USD spent (date, amount,
BoC rate). Net the gain/loss annually.

### Multi-Currency Reconciliation

Revenue earned in USD must be reported in CAD on T2125. Process:

1. Export all USD transactions from Wise (CSV)
2. Match each transaction to BoC noon rate on payment date
3. Record CAD equivalent as business revenue
4. CAD expenses paid from USD account: convert at rate on date of payment
5. Year-end USD balance: record at Dec 31 rate for T1135 assessment

### Accounting Software Setup

- **Wave (free):** Set base currency to CAD, enable multi-currency, enter USD
  transactions at BoC rate manually or via bank feed
- **QuickBooks Online:** Multi-currency plan required; set auto-rate to BoC feed
- **Manual:** Spreadsheet with columns: Date, USD Amount, BoC Rate, CAD Equivalent,
  Category, Client

---

## 4. T1135 Monitoring

### The Threshold

T1135 (Foreign Income Verification) is required if the **total cost** of CC's
specified foreign property exceeded **$100,000 CAD at any point during the year**.
Not the year-end balance — any single day during the year.

### What Counts as Specified Foreign Property

| Counts | Does Not Count |
|--------|----------------|
| Foreign bank accounts (Wise USD balance) | RRSP/TFSA holdings (even if holding US stocks) |
| Foreign stocks held directly (not in registered account) | Canadian-listed ETFs holding foreign stocks (eg. XAW.TO) |
| Foreign rental property | Personal-use property abroad |
| Shares of foreign private corporations | |
| Crypto on foreign exchanges (Kraken) | Crypto on Canadian exchanges |
| Foreign bonds, notes | |

### CC's Current T1135 Exposure

| Asset | Approximate Cost Basis | T1135 Status |
|-------|------------------------|--------------|
| Wise USD account | Track USD received → converted to CAD at acquisition rate | Monitor |
| Kraken (crypto) | Total cost basis of all crypto positions | Monitor |
| Foreign stocks | None currently | N/A |

**Action:** Atlas tracks total T1135-eligible cost basis quarterly. Alert CC when
aggregate approaches $80,000 CAD (20% buffer before the $100K threshold).

### Filing Requirement

- File T1135 with annual T1 return (by June 15 for self-employed)
- Two reporting tiers:
  - **Simplified (< $250K):** Report each property type with aggregate cost, max gain, year-end balance, income
  - **Detailed (>= $250K):** Property-by-property itemized disclosure

### Penalties

| Violation | Penalty |
|-----------|---------|
| Late filing | $25/day (min $100, max $2,500) |
| Gross negligence | Greater of $12,000 or 5% of max cost |
| False statement | Greater of $24,000 or 5% of max cost |
| Criminal (willful) | Up to $500,000 + 2 years imprisonment |

VDP (Voluntary Disclosure) is available if T1135 was not filed in prior years.
See `docs/ATLAS_VDP_GUIDE.md` for the process.

---

## 5. Withholding Tax Recovery (Foreign Tax Credits)

### The Mechanism — s.126 ITA

If foreign tax is withheld on income that is also taxable in Canada, CC can claim
a Foreign Tax Credit (FTC) on the Canadian return to avoid double taxation.

Form: T2209 (Federal FTC), ON-T2036 (Ontario FTC)

### US Withholding Scenarios

| Scenario | Withholding Rate | With Treaty Claim | Recovery Method |
|----------|-----------------|-------------------|-----------------|
| Business income (W-8BEN, Article VII) | 30% → **0%** | 0% — prevention is recovery | N/A |
| US dividends (registered account) | 15% → 15% (no treaty relief for TFSA) | 15% in RRSP, 0% on T2209 | RRSP: claim FTC on T2209 |
| US dividends (TFSA) | 15% | **No FTC available — permanently lost** | Hold US dividend stocks in RRSP, not TFSA |
| US dividends (non-registered) | 15% | Claim FTC on T2209 | FTC offsets Canadian tax |

### TFSA Warning

This is a structural trap. US dividends paid to a TFSA are subject to 15% IRS
withholding, and because TFSA income is not reported on the Canadian return,
there is no Canadian tax to credit against. The 15% is simply lost.

**Fix:** Hold US dividend-paying stocks (VTI, SCHD, etc.) in RRSP, not TFSA.
Hold Canadian or international stocks in TFSA.

### Claiming the FTC

1. Identify total foreign tax withheld (shown on broker statement, 1042-S, or T3/T5)
2. Calculate Canadian tax owing on that same income
3. FTC = lesser of: (a) foreign tax paid, or (b) average Canadian rate x foreign income
4. Enter on T2209 (line 40500 of T1)
5. Ontario FTC claimed separately on ON-T2036 (provincial allocation)

---

## 6. International Contractor Payments

### CC Paying US Contractors (Future — When OASIS Scales)

When OASIS hires US-based contractors for services performed outside Canada:
- No Canadian withholding required
- No T4A required (T4A is only for Canadian payees)
- Contractor handles their own US tax obligations
- OASIS can deduct the expense on T2125 (sole prop) or T2 (corporate)
- Get a completed W-9 (US person) from the contractor for records

### Regulation 105 — Non-Residents Providing Services in Canada

If CC hires a non-Canadian contractor who **physically performs work in Canada**
(eg. a US consultant who comes to Collingwood for a project):
- Payer must withhold **15%** of gross payment and remit to CRA (Form PD27 / T4A-NR)
- Contractor can apply for a Regulation 105 waiver from CRA in advance
- Failure to withhold: OASIS is jointly and severally liable for the contractor's
  Canadian tax

**Trigger point:** Services performed remotely from outside Canada = no Reg 105.
Services performed while physically present in Canada = Reg 105 applies.

### T4A for Canadian Contractors

Issue a T4A slip (Box 048 — fees for services) to any Canadian contractor paid
more than $500 in the calendar year. Due February 28 of the following year.

### HST on International Services

- Services exported to non-Canadian clients (Bennett, US customers): **zero-rated**
  (0% HST charged, but ITCs still claimable on inputs)
- Services imported from foreign contractors: **reverse-charge** — if CC is HST
  registered, may need to self-assess HST on imported services
- See `docs/ATLAS_HST_REGISTRATION_GUIDE.md` for full place-of-supply rules

---

## 7. Compliance Calendar

| Deadline | Action | Responsible |
|----------|--------|-------------|
| Immediately | Submit W-8BEN to Bennett | CC — do this now |
| Immediately | Verify Stripe tax settings (Canadian entity, W-8BEN uploaded) | CC |
| Ongoing | Log USD receipt: date, amount, BoC rate | Atlas / CC bookkeeping |
| Quarterly | Review Wise USD balance + Kraken cost basis vs $100K T1135 threshold | Atlas |
| Quarterly | Calculate FX gains/losses on USD holdings | Atlas |
| Dec 31 | Record year-end foreign account balances at BoC Dec 31 noon rate | Atlas |
| Feb 28 | Issue T4A slips to Canadian contractors (if any) | CC |
| Apr 30 | Pay any balance on T1 (including FX gains, FTC reconciliation) | CC |
| June 15 | File T1 with T1135 (if threshold exceeded), T2209 FTC claim | CC via NETFILE |
| W-8BEN expiry | Resubmit before expiry (3-year cycle) | Calendar reminder set |

---

## 8. CC-Specific Checklist

### Urgent (Do Now)

- [ ] **Submit W-8BEN to Bennett** — prevents 30% withholding on all OASIS payments.
      Use the field guide in Section 1. Email a signed PDF to Bennett's accounts payable.
      Request written confirmation that it is on file.

- [ ] **Verify Stripe account settings** — log into Stripe Dashboard → Settings →
      Tax information. Confirm country is Canada, address is Collingwood ON, and
      a W-8BEN is uploaded. If Stripe shows a US address, correct it immediately.

### Now (This Month)

- [ ] **Start T1135 tracking spreadsheet** — columns: Asset, Date Acquired, USD Cost,
      BoC Rate, CAD Cost Basis, Date Disposed (if applicable). Seed with Wise USD
      balance and Kraken positions.

- [ ] **Export Kraken cost basis** — total CAD cost of all open crypto positions
      (BTC, ETH, SOL, etc.). Add to T1135 tracker. Alert if approaching $80K CAD.

- [ ] **Set up FX log in bookkeeping software** — every USD payment from Bennett
      gets logged with BoC rate on receipt date.

### Quarterly

- [ ] Review T1135 tracker — has aggregate foreign property cost exceeded $80K CAD?
- [ ] Calculate FX gains/losses on USD cash positions
- [ ] Confirm all US platforms still have current W-8BEN on file

### Annual

- [ ] Assess T1135 requirement — file if threshold was exceeded at any point in year
- [ ] Claim FTC on T2209 for any foreign tax withheld
- [ ] Check W-8BEN expiry date — renew if within 90 days of expiry
- [ ] Reconcile all USD revenue to CAD at BoC transaction-date rates

### Post-Incorporation

- [ ] Replace W-8BEN (individual) with W-8BEN-E (entity) for all US payers
- [ ] Update Stripe to OASIS Inc. as the account entity
- [ ] Review Regulation 105 obligations if hiring non-resident contractors in Canada
- [ ] Re-assess T1135 — corporation files separately; sole prop T1135 closes out

---

## Document Library

| Document | Location | When to Use |
|----------|----------|-------------|
| **Foreign Reporting** | `docs/ATLAS_FOREIGN_REPORTING.md` | T1135/T1134 deep dive, transfer pricing, FAPI, FTC calculation, withholding tax credits |
| **HST Registration** | `docs/ATLAS_HST_REGISTRATION_GUIDE.md` | Zero-rated exports, place-of-supply rules, ITCs on business expenses, reverse-charge |
| **VDP Guide** | `docs/ATLAS_VDP_GUIDE.md` | Prior-year T1135 non-compliance, unreported foreign income, penalty elimination |
| **Income Scaling Playbook** | `docs/ATLAS_INCOME_SCALING_PLAYBOOK.md` | Crown Dependencies exit ramp when foreign income scales (IE: Isle of Man at $120K+) |
| **Treaty & FIRE** | `docs/ATLAS_TREATY_FIRE_STRATEGY.md` | Full Canada-US treaty text, departure tax, non-resident planning |
| **Accounting Advisor** | `skills/accounting-advisor/SKILL.md` | T2125 filing, FX gains on Schedule 3, FTC on T2209 |

---

## Quick Reference

| Question | Answer |
|----------|--------|
| What form prevents US withholding? | W-8BEN (individual) or W-8BEN-E (corporation) |
| Which treaty article covers CC's OASIS income? | Article VII — Business Profits, 0% rate |
| What rate applies without W-8BEN? | 30% backup withholding on gross payment |
| When does T1135 kick in? | $100,000 CAD cost of foreign property at any point in year |
| What rate converts USD to CAD for CRA? | Bank of Canada nominal noon rate on transaction date |
| Is TFSA withholding recoverable? | No — hold US dividend stocks in RRSP instead |
| Does CC need to file a US return? | No, unless permanent establishment in US |
| How often does W-8BEN expire? | Every 3 calendar years from year of signing |
| T1135 late-filing penalty? | $25/day, max $2,500 |
