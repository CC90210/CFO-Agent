# ATLAS Personalization Interview

**For initial setup and ongoing updates.** Atlas uses your answers to populate `brain/USER.md`, which it reads before every interaction. Your answers ensure Atlas gives personalized guidance, not generic advice.

**Time:** 10–15 minutes  
**Output:** Updated `brain/USER.md` with your complete financial profile  
**Frequency:** Initial setup + annual review (or after major life changes)

---

## A. Identity & Citizenship

*These questions determine your tax jurisdiction and international structuring options.*

### A1. Personal Information

**Question:** What is your legal name (as it appears on your ID)?  
**Field in USER.md:** `name`  
**Example:** Conaugh McKenna

---

**Question:** What is your date of birth?  
**Field in USER.md:** `age`, `dob`  
**Example:** 2003-06-15 (age will auto-calculate)

---

**Question:** What is your current city and province/state?  
**Field in USER.md:** `location`, `province`  
**Example:** Collingwood, Ontario, Canada

---

**Question:** Are you planning to relocate in the next 12 months?  
**Field in USER.md:** `relocation_planned`, `relocation_target`  
**Example:** Yes, Montreal summer 2026

---

### A2. Citizenship

**Question:** What country/countries are you a citizen of?  
**Field in USER.md:** `citizenship`  
**Example:** Canadian + British (dual passport holder)

---

**Question:** What other countries are you *eligible* for citizenship in? (E.g., through parents, grandparents, spouse.)  
**Field in USER.md:** `eligible_citizenship`  
**Example:** Irish (through father)

---

**Question:** If you hold a British passport, are you interested in Crown Dependencies (Isle of Man, Guernsey, Jersey) tax planning?  
**Field in USER.md:** `crown_dependencies_interest`  
**Example:** Yes, at $120K+ revenue

---

### A3. Family & Dependents

**Question:** Are you married, in a common-law relationship, or single?  
**Field in USER.md:** `marital_status`  
**Example:** Single

---

**Question:** Do you have any children or dependents?  
**Field in USER.md:** `dependents`  
**Example:** None

---

**Question:** Do any family members have significant income that might affect family trust structures or income splitting?  
**Field in USER.md:** `family_income_context`  
**Example:** Mother ~$80K, Dad ~$60K EUR (in Ireland)

---

## B. Income & Business

*These questions determine tax bracket, installment requirements, and incorporation ROI.*

### B1. Employment Type

**Question:** How do you currently earn income? (Select all that apply)  
- [ ] Employed full-time (T4 employee)
- [ ] Employed part-time (T4 employee)
- [ ] Self-employed / sole proprietor (T2125)
- [ ] Incorporated business (T2 / T5 dividends)
- [ ] Passive income (T5, interest, dividends, rental)
- [ ] Freelance / contract work (no long-term client)

**Field in USER.md:** `employment_type`  
**Example:** Sole proprietor (T2125)

---

**Question:** What is your legal business structure?  
- [ ] Sole proprietor (no incorporation)
- [ ] CCPC (Canadian-controlled private corporation)
- [ ] Partnership / LLP
- [ ] Single-member LLC (if US)
- [ ] Other: ___

**Field in USER.md:** `business_structure`, `incorporation_status`  
**Example:** Sole proprietor; planning CCPC incorporation at $80K+ revenue

---

### B2. Revenue Streams

**Question:** List all your income sources. For each, estimate:  
1. **Name of source** (e.g., "Bennett Skool partnership")
2. **Type** (SaaS subscription, consulting, employee salary, freelance, course, affiliate, trading, rental)
3. **Currency** (CAD, USD, EUR, crypto)
4. **Monthly amount** (current month or average)
5. **Customer concentration** (% from largest customer)
6. **Growth trajectory** (stable, growing, declining)

**Field in USER.md:** `income_sources` (array)

**Example 1:**
```
Name: Bennett Skool Partnership
Type: SaaS Revenue Share + Flat Fee
Currency: USD
Monthly: $2,500 flat + 15% of Skool revenue
Customer Concentration: 100% (single-client risk)
Status: Primary relationship, month-to-month
Growth: Growing 10-15%/month (Skool growth)
```

**Example 2:**
```
Name: Stripe (OASIS + Nostalgic brands)
Type: SaaS Subscription
Currency: USD
Monthly: $180-200 MRR
Customer Concentration: 5+ small clients, 50%+ from 2 clients
Status: Active, scaling
Growth: 65% MRR growth rate (last quarter)
```

**Example 3:**
```
Name: DJ Income
Type: Freelance Events
Currency: CAD
Monthly: ~$150 (seasonal, 13 gigs in 2025)
Customer Concentration: Ad-hoc events
Status: Secondary, minimal focus
Growth: Declining (deprioritizing)
```

---

**Question:** What is your total monthly recurring revenue (MRR)?  
**Field in USER.md:** `mrr_total`, `mrr_target`  
**Example:** Current: $2,982 USD (~$4,100 CAD). Target by Dec 2026: $15K–$20K USD.

---

**Question:** What is your current annual revenue (YTD or estimated annual)?  
**Field in USER.md:** `revenue_annual`, `revenue_projection`  
**Example:** 2025: ~$6,347 CAD. 2026 projection: $280K–$480K CAD.

---

**Question:** What percentage of your revenue is concentrated in your largest client?  
**Field in USER.md:** `customer_concentration_pct`  
**Example:** 94% (Bennett)

---

**Question:** Do you have significant unrealized gains in any business (equity stake in a startup)?  
**Field in USER.md:** `unrealized_gains`  
**Example:** None currently

---

### B3. Payment Processors & Banking

**Question:** How do you receive payments? (Select all that apply)  
- [ ] Direct bank deposit
- [ ] Stripe
- [ ] Wise (formerly TransferWise)
- [ ] PayPal
- [ ] Cryptocurrency (Bitcoin, Ethereum, stablecoins)
- [ ] Cash
- [ ] Other: ___

**Field in USER.md:** `payment_processors`  
**Example:** Stripe → Wise USD account; Bennett sends via Wise payment link

---

**Question:** What currencies do you earn income in?  
**Field in USER.md:** `income_currencies`  
**Example:** USD (95% of SaaS), CAD (DJ + Nicky's)

---

**Question:** Do you have a multi-currency account (e.g., Wise with USD + CAD)?  
**Field in USER.md:** `multi_currency_accounts`  
**Example:** Yes, Wise USD + CAD

---

## C. Accounts & Platforms

*These questions allow Atlas to pull live balances and calculate accurate net worth.*

### C1. Banking

**Question:** What is your primary bank?  
**Field in USER.md:** `primary_bank`  
**Example:** RBC

---

**Question:** Do you have any secondary banks or accounts (international, business, savings)?  
**Field in USER.md:** `secondary_banks`  
**Example:** Wise (multi-currency), PayPal, Stripe

---

**Question:** If yes to secondary banks, do you want Atlas to track balances there?  
**Field in USER.md:** `track_secondary_accounts`  
**Example:** Yes (Wise for USD + EUR cash management)

---

### C2. Registered Accounts (Tax-Advantaged)

**Atlas is Canadian-first. Adjust for your country.**

**Question:** Do you have a TFSA (Tax-Free Savings Account)?  
- [ ] No
- [ ] Yes, with these institutions: (Wealthsimple, Interactive Brokers, other?)

**Field in USER.md:** `tfsa_status`, `tfsa_balance`, `tfsa_room`  
**Example:** Yes, Wealthsimple. Balance: $155.16. Estimated room: ~$46K.

---

**Question:** Do you have an RRSP (Registered Retirement Savings Plan)?  
- [ ] No
- [ ] Yes, with balance: ___

**Field in USER.md:** `rrsp_status`, `rrsp_balance`, `rrsp_room`  
**Example:** Yes, Wealthsimple. Balance: $0. Estimated room: ~$27K.

---

**Question:** Do you have an FHSA (First Home Savings Account)?  
- [ ] No
- [ ] Yes, with balance: ___

**Field in USER.md:** `fhsa_status`, `fhsa_balance`, `fhsa_opened_date`  
**Example:** Yes, Wealthsimple. Balance: $0 (just opened). Annual room: $8K.

---

**Question:** Do you have an RESP (Registered Education Savings Plan)?  
**Field in USER.md:** `resp_status`  
**Example:** No (no children)

---

**Question:** If you earn US income or have US assets, do you have a US 401(k), IRA, or brokerage?  
**Field in USER.md:** `us_accounts`  
**Example:** No

---

### C3. Brokerage & Trading Accounts

**Question:** Where do you trade stocks or ETFs?  
- [ ] Wealthsimple
- [ ] Interactive Brokers
- [ ] Questrade
- [ ] E-Trade / TD Direct Investing
- [ ] Fidelity
- [ ] Other: ___

**Field in USER.md:** `stock_brokers`  
**Example:** Wealthsimple (stocks in TFSA)

---

**Question:** Where do you trade crypto?  
- [ ] Kraken
- [ ] Coinbase
- [ ] Wealthsimple Crypto
- [ ] NDAX
- [ ] Self-custody (MetaMask, Ledger, hardware wallet)
- [ ] Other: ___

**Field in USER.md:** `crypto_platforms`, `crypto_holdings`  
**Example:** Kraken ($133 USD, 4 positions), Wealthsimple ($206 BTC)

---

**Question:** Where do you trade forex or metals?  
- [ ] OANDA
- [ ] IBKR
- [ ] Pepperstone
- [ ] Other: ___

**Field in USER.md:** `forex_platforms`  
**Example:** OANDA (gold/forex positions)

---

**Question:** Do you have any cold wallets (hardware wallets like Ledger)?  
**Field in USER.md:** `cold_wallets`  
**Example:** No (all on exchanges)

---

### C4. Foreign Accounts

**Question:** Do you have any bank accounts, investments, or property outside Canada?  
- [ ] No
- [ ] Yes, in: (list countries and account types)

**Field in USER.md:** `foreign_property`, `foreign_accounts`  
**Example:** Wise USD account (~$2K). Threshold for T1135 reporting: $100K CAD (not yet required).

---

**Question:** If yes, what is the *total cost basis* of all foreign assets?  
**Field in USER.md:** `foreign_property_cost`  
**Example:** $2,000 USD ≈ $2,800 CAD

---

## D. Assets & Liabilities

*These questions allow accurate net worth calculation and tax planning.*

### D1. Cash & Equivalents

**Question:** How much CAD cash do you have (across all accounts)?  
**Field in USER.md:** `cash_cad`  
**Example:** $6,419 (RBC) + $155 (TFSA) = $6,574

---

**Question:** How much USD cash (or other currency)?  
**Field in USER.md:** `cash_usd`, `cash_other_currencies`  
**Example:** $1,900 USD (Wise)

---

### D2. Investments

**Question:** List all your investment holdings (stocks, ETFs, crypto, bonds):

For each, provide:
- **Asset name and ticker**
- **Platform**
- **Quantity**
- **Current market value**
- **Cost basis** (if known)

**Field in USER.md:** `investments` (array)

**Example:**
```
Asset: Bitcoin
Ticker: BTC
Platforms: Kraken, Wealthsimple
Total Holdings: 0.005 BTC + small amount in Wealthsimple
Current Value: $350 USD
Cost Basis: $356 CAD (Wealthsimple)
Unrealized Gain/Loss: Small loss
```

---

### D3. Real Estate

**Question:** Do you own any real estate?  
- [ ] No
- [ ] Yes, primary residence (owner-occupied)
- [ ] Yes, rental property
- [ ] Yes, vacation property
- [ ] Yes, commercial property

**Field in USER.md:** `real_estate`  
**Example:** No (currently renting from parents)

---

**Question:** If renting, what is your monthly rent?  
**Field in USER.md:** `rent_monthly`  
**Example:** $0 (renting from parents); planning to relocate to Montreal at $750–$1,500/mo.

---

### D4. Equipment (CCA-Eligible)

**Question:** Do you have any equipment used for business (computer, camera, vehicle, etc.)?  
**Field in USER.md:** `equipment`  
**Example:**
```
- Computer: $989.25 (Nov 2023, Class 50 CCA)
- DJ equipment: hand-me-downs (no receipts)
- Monitor/speakers/microphones: hand-me-downs (no receipts)
```

---

### D5. Liabilities & Debt

**Question:** What debts do you have?  
- [ ] None
- [ ] Student loans (OSAP, NSLSC, private)
- [ ] Credit card debt
- [ ] Mortgage
- [ ] Car loan
- [ ] Other: ___

**Field in USER.md:** `liabilities`  
**Example:**
```
OSAP: ~$9,000 outstanding
Interest: Tax-deductible
Repayment Assistance Plan (RAP): Likely qualifies at current income level
```

---

**Question:** For student loans, are you in repayment or a hardship program (RAP, IBP)?  
**Field in USER.md:** `student_loan_status`  
**Example:** Not yet in repayment (income below threshold), but eligible for RAP if needed

---

## E. Tax Situation

*These questions prevent duplicate filings and optimize carryforwards.*

### E1. Recent Filing History

**Question:** What was the last tax year you filed?  
**Field in USER.md:** `last_return_filed`  
**Example:** 2024 (likely nil return)

---

**Question:** Did you file for 2025?  
- [ ] No, not yet
- [ ] Yes, and it was assessed
- [ ] Yes, currently under CRA review

**Field in USER.md:** `current_filing_status`  
**Example:** No, not yet (deadline June 15, 2026)

---

**Question:** What filing method do you use or plan to use?  
- [ ] Wealthsimple Tax (free)
- [ ] NETFILE directly
- [ ] CPA / accountant
- [ ] TurboTax
- [ ] StudioTax
- [ ] Other: ___

**Field in USER.md:** `filing_method`  
**Example:** Wealthsimple Tax → NETFILE

---

### E2. Expected Deductions

**Question:** Which of these deductions do you expect to claim in 2026?  
- [ ] Home office
- [ ] Vehicle expenses
- [ ] Software / subscriptions
- [ ] Equipment (CCA)
- [ ] Meals & entertainment (50% deductible)
- [ ] Travel
- [ ] Professional fees (accountant, lawyer)
- [ ] Business insurance
- [ ] Rent / workspace
- [ ] Education / courses
- [ ] Other: ___

**Field in USER.md:** `expected_deductions`  
**Example:** Home office, software, subscriptions, equipment, meals, travel

---

**Question:** Do you have a home office? If yes, what % of your home is dedicated to work?  
**Field in USER.md:** `home_office_sqft_pct`  
**Example:** ~15% (one room)

---

**Question:** Do you have a vehicle and use it for business? If yes, what % is business use?  
**Field in USER.md:** `vehicle_business_use_pct`  
**Example:** None (no vehicle)

---

### E3. Carryforwards & Credits

**Question:** Do you have any unused tax credits or loss carryforwards from prior years?  
**Field in USER.md:** `loss_carryforwards`, `unused_credits`  
**Example:** None known

---

**Question:** Are you eligible for any government R&D credits (SR&ED in Canada, R&D credit in US/UK)?  
**Field in USER.md:** `sr_ed_eligible`  
**Example:** Yes, if OASIS qualifies (AI/ML development). 43% refundable credit in Ontario.

---

## F. Risk & Goals

*These questions determine asset allocation, account placement, and strategic planning.*

### F1. Risk Tolerance

**Question:** How would you describe your risk tolerance?  
- [ ] Conservative (I want stable returns, minimal volatility)
- [ ] Moderate (I can tolerate 10–15% volatility)
- [ ] Aggressive (I can tolerate 30%+ volatility, long-term horizon)
- [ ] Speculative (I'm comfortable with 50%+ drawdowns in pursuit of high returns)

**Field in USER.md:** `risk_tolerance`  
**Example:** Aggressive growth (age 22, long time horizon), but disciplined (kill switches non-negotiable)

---

**Question:** What's the longest timeline you're comfortable holding an investment without reviewing it?  
**Field in USER.md:** `investment_horizon`  
**Example:** 3–18 months for picks; 20+ years for FIRE/index fund core holdings

---

### F2. Financial Goals

**Question:** What is your #1 financial goal?  
**Field in USER.md:** `primary_goal`  
**Example:** Wealth building + tax optimization

---

**Question:** Secondary goals (in priority order):  
**Field in USER.md:** `secondary_goals`  
**Example:**
1. Build to $15K–$20K MRR by Dec 2026
2. Incorporate at $80K+ revenue ($12K–$18K/year tax savings)
3. First home (FHSA + HBP strategy, 5–10 year horizon, $75K down payment target)
4. FIRE ($900K–$1.2M invested = $36K–$48K/year passive income)
5. International structuring (Isle of Man at $120K+, Irish IP company at $300K+)

---

### F3. Near-Term Concerns

**Question:** What's keeping you up at night financially? (Select all that apply)  
- [ ] Runway / cash flow (will I run out of money?)
- [ ] Income concentration (too dependent on one client)
- [ ] Tax liability (will I owe too much?)
- [ ] Market timing (should I sell / buy now?)
- [ ] Debt repayment (how fast should I pay down my loans?)
- [ ] Asset protection (do I need incorporation / insurance?)
- [ ] International structure (when should I move to lower-tax jurisdiction?)
- [ ] Diversification (should I expand to new revenue streams?)
- [ ] Other: ___

**Field in USER.md:** `concerns`  
**Example:** Runway, income concentration (94% from Bennett), incorporation timing, Montreal relocation cash impact

---

**Question:** What is your target income level (annual)?  
**Field in USER.md:** `income_target`, `income_target_timeline`  
**Example:** $200K–$500K CAD/year within 5 years

---

### F4. Time & Effort

**Question:** How much time per week are you willing to spend on financial management (tax planning, research, portfolio maintenance)?  
**Field in USER.md:** `time_budget_hours_per_week`  
**Example:** 2–3 hours/week (monthly planning + quarterly tax review)

---

## G. Data Access (Optional Automations)

*Only fill this section if you want Atlas to automatically pull data. Leave blank to do it manually.*

### G1. Gmail (Receipt Scanning)

**Question:** Do you want Atlas to scan your Gmail inbox for receipts?  
- [ ] No
- [ ] Yes

**Field in USER.md:** `gmail_enabled`  
**Example:** Yes

---

**Question:** What is your Gmail address?  
**Field in USER.md:** `gmail_user`  
**Example:** conaugh@oasisai.work

---

**Question:** Generate a Gmail app password (Settings > Security > App passwords), paste here:  
**Field in USER.md:** `gmail_app_password` (stored in `.env`, not USER.md)  
**Note:** Never paste the actual password in version control. Use `.env` only.

---

### G2. Stripe (Revenue Tracking)

**Question:** Do you want Atlas to pull revenue data from Stripe?  
- [ ] No
- [ ] Yes

**Field in USER.md:** `stripe_enabled`  
**Example:** Yes (TBD — API key placeholder in `.env`)

---

**Question:** Do you have a Stripe restricted API key (read-only)?  
**Field in USER.md:** Note in `.env`  
**Example:** Not yet configured

---

### G3. Wise (Cash Monitoring)

**Question:** Do you want Atlas to track your Wise balance?  
- [ ] No
- [ ] Yes

**Field in USER.md:** `wise_enabled`  
**Example:** Yes (TBD — API token placeholder)

---

### G4. Exchange APIs (Live Crypto Balance)

**Question:** Do you want Atlas to read live balances from Kraken, OANDA, or other brokers?  
- [ ] No
- [ ] Yes

**Field in USER.md:** `exchange_api_enabled`  
**Example:** Yes, Kraken + OANDA

---

**Question:** Do you have API keys for these platforms?  
**Field in USER.md:** Note which platforms in `.env`  
**Example:** Kraken API key + secret (read-only balance key, no trading perms)

---

### G5. News APIs (Research Acceleration)

**Question:** Do you want Atlas to use paid news/research APIs for deeper analysis?  
- [ ] No, free tier is enough
- [ ] Yes, I'm interested in upgrades

**Field in USER.md:** `research_api_tier`  
**Example:** Free tier for now; upgrade to FMP + Polygon when budget allows (~$43/mo)

---

## H. Communication Preferences

*This determines how Atlas proactively surfaces risks and opportunities.*

### H1. Communication Channel

**Question:** How do you prefer Atlas to communicate with you?  
- [ ] CLI only (I'll run commands as needed)
- [ ] Telegram (natural language, instant)
- [ ] Email (daily/weekly summaries)
- [ ] Slack (if you have workspace)
- [ ] Discord (if you're in a community server)
- [ ] Multiple: ___

**Field in USER.md:** `preferred_channels`  
**Example:** Telegram (primary), CLI (for deep dives)

---

**Question:** If Telegram, what's your Telegram user ID?  
**Field in USER.md:** (stored in `.env`, not USER.md)  
**Example:** Not yet configured

---

### H2. Check-In Cadence

**Question:** How often should Atlas proactively check in with you?  
- [ ] Daily
- [ ] 2–3x per week
- [ ] Weekly
- [ ] Monthly
- [ ] Quarterly
- [ ] On-demand only (never alert me unless something critical)

**Field in USER.md:** `check_in_cadence`  
**Example:** Monthly (net worth + runway), Quarterly (tax review)

---

### H3. Alert Thresholds

**Question:** Set thresholds for proactive alerts. When any of these hit, Atlas should notify you:

- Runway drops below ___ months
- Income concentration exceeds ___ %
- Unrealized losses exceed ___ % of portfolio
- Tax reserve falls below ___ CAD
- Major market event (Fed rate change, earnings, geopolitical)
- Tax deadline within ___ days

**Field in USER.md:** `alert_thresholds`  
**Example:**
```
- Runway drops below 3 months
- Income concentration > 85% (currently 94%)
- Unrealized losses > 5%
- Tax payment deadline within 30 days
- Major Fed announcements
```

---

## Finishing Up

**Save your answers:** Atlas will automatically update `brain/USER.md` with your responses.

**What comes next:**
1. Edit `.env` with API keys (if you want automations)
2. Run `python main.py networth` to verify Atlas can read your accounts
3. Run `python main.py runway` to see your cash position
4. Run `python main.py taxes` to see your tax estimate
5. On-demand: `python main.py picks "your theme"` for stock research

**Questions?** Read `ATLAS_USER_GUIDE.md` for deep dives on each module.

**Want to skip the interview?** Manually edit `brain/USER.md` with rough estimates. You can always refine later.

---

**Last Updated:** 2026-04-14  
**Version:** 2.0
