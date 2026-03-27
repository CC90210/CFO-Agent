# CRA Cryptocurrency Enforcement & Tax Intelligence Brief

> **Compiled by:** ATLAS (CC's CFO Agent)
> **Date:** 2026-03-27
> **Scope:** CRA crypto audit program, data-sharing orders, Tax Court case law, DeFi tax treatment, CARF implementation, penalty framework
> **Jurisdiction:** Canada (Ontario) | **Taxpayer profile:** Self-employed sole proprietor, active crypto trader (Kraken), automated trading system
> **Purpose:** Master reference document for crypto tax compliance. Supplements `ATLAS_TAX_STRATEGY.md`.

---

## Table of Contents

1. [CRA Cryptocurrency Audit Program (2024-2026)](#1-cra-cryptocurrency-audit-program-2024-2026)
2. [Data-Sharing Agreements & Court Orders](#2-data-sharing-agreements--court-orders)
3. [Tax Court of Canada Case Law (2023-2025)](#3-tax-court-of-canada-case-law-2023-2025)
4. [CRA Position on DeFi Activities](#4-cra-position-on-defi-activities)
5. [CARF — Crypto-Asset Reporting Framework](#5-carf--crypto-asset-reporting-framework)
6. [Penalty Framework for Unreported Crypto](#6-penalty-framework-for-unreported-crypto)
7. [CC-Specific Risk Assessment & Action Items](#7-cc-specific-risk-assessment--action-items)

---

## 1. CRA Cryptocurrency Audit Program (2024-2026)

### Program Scale

The CRA has a dedicated **cryptoasset audit team** with **35 auditors** working on **230+ active files**. Over the past three years (2023-2025), this team has recovered **$100 million+** in assessed taxes from crypto-related audits. Despite this, as of late 2025 the CRA has filed **zero criminal charges** for crypto tax evasion — enforcement has been entirely civil (reassessments, penalties, interest).

The CRA's 2025-26 Departmental Plan explicitly identifies crypto-assets as an **"emerging high-risk area"** for compliance enforcement.

### CRA Tracking Methods

The CRA uses a multi-layered approach to identify unreported crypto income:

| Method | How It Works | Risk to CC |
|--------|-------------|------------|
| **Exchange data orders** | Federal Court unnamed persons requirements (UPRs) compel exchanges to hand over customer data (see Section 2) | **HIGH** — Kraken is a known target |
| **Blockchain analytics** | CRA contracts with firms like Chainalysis to trace on-chain transactions back to real identities | **MEDIUM** — on-chain activity linkable to KYC'd exchange deposits/withdrawals |
| **Financial institution monitoring** | Banks and payment processors report suspicious large deposits; CRA cross-references with tax filings | **MEDIUM** — fiat on/off-ramps via Wise/RBC are visible |
| **International data exchange** | CRS (Common Reporting Standard) and soon CARF provide automated cross-border data sharing | **HIGH** — Kraken is US-based; IRS-CRA data sharing via FATCA/CRS |
| **Lifestyle audits** | CRA compares reported income to spending patterns, asset acquisitions, social media | **LOW** — CC's trading is small-scale |
| **Informant tips** | CRA pays informants for information leading to tax recovery (Offshore Tax Informant Program) | **LOW** |

### What Triggers a Crypto Audit

Based on CRA enforcement patterns and published audit criteria:

1. **Unreported exchange activity** — CRA receives exchange data showing $50K+ in transactions; taxpayer reported zero capital gains or crypto income
2. **Large fiat deposits without matching income** — Bank deposits that don't correlate with T4/T2125 reported income
3. **T1135 non-filing** — Foreign crypto holdings exceeding $100,000 CAD cost base without T1135 filed
4. **Inconsistent reporting** — Reporting capital gains one year, nothing the next, despite continued exchange activity
5. **High-volume trading without business income treatment** — Hundreds of trades reported as capital gains instead of business income
6. **DeFi/NFT activity** — CRA is specifically targeting NFT platforms (see Dapper Labs below)
7. **Repeated failure to report income** — ITA s.163(1) triggers automatic 10% penalty on second offence within 4 years

### Non-Compliance Rate

CRA internal analysis (disclosed December 2025) found that **40% of Canadian crypto platform users** are either evading taxes or at high risk of non-compliance. This statistic is driving increased audit resources and legislative action.

---

## 2. Data-Sharing Agreements & Court Orders

### Unnamed Persons Requirements (UPRs) — ITA s.231.2

The CRA's primary weapon for obtaining exchange data is the **unnamed persons requirement** under subsection 231.2(2) of the Income Tax Act. This allows CRA to apply to Federal Court for an order compelling any person (including exchanges) to provide information about unnamed taxpayers, provided:

- The group is **ascertainable** (e.g., "all users with accounts over $20K")
- The requirement is to **verify compliance** with the ITA
- A **judge is satisfied** there are reasonable grounds

### Coinsquare — Federal Court Order (March 19, 2021)

**Case:** *MNR v. Coinsquare Ltd.* (Federal Court, 2021)

The CRA obtained a Federal Court order compelling **Coinsquare Ltd.** to disclose:

| Data Category | Scope |
|---------------|-------|
| User identity | Names, addresses, dates of birth, KYC documentation |
| Account values | Users with accounts >= **$20,000** on Dec 31 of any year (2014-2020) |
| Cumulative deposits | Users who deposited a cumulative **$20,000+** |
| Top traders | **16,500 largest accounts** by trading volume (CAD) AND 16,500 largest by number of trades (2014-2020) |
| Transaction records | All crypto and fiat deposits/withdrawals with source/destination |
| Trading activity | All trading pairs, buy/sell orders, dates, times, amounts, prices |

**Impact:** This was the CRA's **first** crypto-specific UPR. It established the legal precedent that Canadian courts will authorize bulk exchange data transfers to CRA.

### Dapper Labs — Federal Court Order (2025)

**Case:** *MNR v. Dapper Labs Inc.* (Federal Court, 2025)

The CRA's **second** crypto UPR targeted **Dapper Labs Inc.**, a Canadian company behind NBA Top Shot and the Flow blockchain (NFT marketplace).

- CRA initially sought data on **18,000 users**
- Negotiated down to **2,500 users** (the highest-value/most active accounts)
- Targets NFT traders specifically — signaling CRA is expanding beyond traditional crypto to digital collectibles

**Significance:** Confirms CRA is actively pursuing NFT platforms, not just crypto exchanges. Any Canadian using NFT marketplaces built on Canadian platforms is exposed.

### International Exchange Data (Kraken, Coinbase — U.S. Parallel)

While the Coinsquare and Dapper Labs orders are Canadian Federal Court actions, the CRA also receives data through **international tax treaties**:

**Kraken (U.S.):**
- In 2023, a U.S. court ordered Kraken to provide the IRS with profile and transaction data for users who exceeded **$20,000 in transactions** in any single year (2016-2020)
- Kraken complied in November 2023, sharing data on **42,000 users**
- Under the **Canada-U.S. Tax Convention** (Article XXVII) and **FATCA IGA**, the IRS shares relevant data on Canadian-resident Kraken users with the CRA
- **CC's Kraken account is almost certainly known to CRA** through this channel

**Coinbase (U.S.):**
- In 2018, Coinbase informed **13,000 users** it would provide the IRS with taxpayer IDs, names, birth dates, addresses, and transaction records (2013-2015)
- Same Canada-U.S. treaty data-sharing applies

### Summary: CC's Exchange Exposure

| Exchange | CRA Has Data? | Mechanism |
|----------|--------------|-----------|
| **Kraken** | **YES — near certain** | IRS court order (2023) + Canada-U.S. tax treaty data sharing |
| **Coinsquare** | Yes (if CC used it) | Federal Court UPR (2021) |
| **Coinbase** | Yes (if CC used it) | IRS John Doe summons (2018) + treaty sharing |
| **OANDA** | Regulated broker — reports to CRA directly | Standard broker reporting (T5/T5008) |
| **Any Canadian exchange** | Likely | CRA has signaled more UPRs are coming |

---

## 3. Tax Court of Canada Case Law (2023-2025)

### Amicarelli v. The King (2025 TCC 185) — LANDMARK

**Date:** December 9, 2025
**Judge:** Justice Sorensen
**Significance:** **First Tax Court of Canada ruling directly addressing Bitcoin taxation**

**Facts:**
- The taxpayer, an Air Canada employee, purchased **100+ Bitcoin in 2017** through QuadrigaCX
- She used RRSP savings, a second mortgage, and credit card cash advances to fund purchases
- In late December 2017, her QuadrigaCX account was **emptied without consent** (QuadrigaCX CEO was later found to be a fraudster who misused client assets)
- She claimed the loss as a **non-capital loss** (business loss, fully deductible)
- CRA argued it should be a **capital loss** (only 50% deductible, and only against capital gains)

**Court's Analysis — Business Income vs. Capital Gains:**

Justice Sorensen applied the traditional badges of trade and found:

| Factor | Finding |
|--------|---------|
| Intention | Purchased Bitcoin **with a view to profit** |
| Activity level | Regular purchases, routine monitoring of account and market — **"more than dabbling"** |
| Trading pattern | Activities **"more akin to activities of a trader or dealer"** |
| Personal use | **No personal use or benefit** from the Bitcoin |
| Financing | Leveraged purchases (mortgage, credit cards) suggest commercial intent |

**Ruling:** The Bitcoin was held on **income account** (business income/loss), NOT capital account. The loss was a deductible **non-capital loss**.

**Key Takeaways for CC:**

1. **Running ATLAS with 12 automated strategies, backtesting infrastructure, and risk management = textbook "trader or dealer" activity.** CRA would almost certainly classify CC's Kraken trading as business income, consistent with what ATLAS_TAX_STRATEGY.md already recommends.
2. **Exchange losses from fraud may be deductible** as business losses if trading activity qualifies as business income.
3. **The court looked at the totality of circumstances** — frequency, infrastructure, intent, financing, and personal use.
4. **This case provides the judicial precedent** CRA will cite when assessing active crypto traders as business income earners.

### Capital Gains Inclusion Rate — Status Update (March 2025)

**Timeline of the 66.67% saga:**

| Date | Event |
|------|-------|
| April 2024 | Federal Budget proposes increasing capital gains inclusion rate from 50% to 66.67% for corporations/trusts (all gains) and individuals (gains above $250,000), effective June 25, 2024 |
| June 25, 2024 | Proposed effective date passes; legislation **never enacted** (Parliament prorogued) |
| January 31, 2025 | Government defers proposed effective date to January 1, 2026 |
| March 21, 2025 | **PM Mark Carney's government formally cancels the increase** |

**Current law (as of March 2026):** Capital gains inclusion rate remains at **50%** for all taxpayers. The lifetime capital gains exemption was increased to **$1,250,000** (from $1M) — this change survived the cancellation.

**Impact on CC:** If any of CC's crypto is on capital account (long-term holdings in cold storage), only 50% of gains are taxable. The planned increase to 66.67% is dead.

---

## 4. CRA Position on DeFi Activities

### Official CRA Guidance

The CRA has published guidance on **mining and staking** (canada.ca crypto guide) but has issued **no formal guidance on DeFi** (yield farming, liquidity pools, lending protocols, wrapped tokens, bridges, governance tokens). Taxpayers must apply general ITA principles.

### Staking Rewards

**CRA's published position (canada.ca):**

- Staking rewards are **taxable when received** at fair market value in CAD
- Classification depends on activity level:
  - **Business income** if operating commercially (running validator nodes, staking as primary activity)
  - **Property income** if passive (delegating to a validator, exchange-based staking)
- Both are **100% taxable** (no 50% inclusion rate — that's only for capital gains)
- A **second taxable event** occurs when staking rewards are later sold (capital gain/loss on the difference between FMV at receipt and sale price)

**ITA Reference:** Staking income reported under **s.9** (business income) or **s.12(1)(c)** (property income), depending on classification.

### Yield Farming / Liquidity Pools

**No formal CRA guidance.** Conservative treatment:

| Event | Tax Treatment |
|-------|--------------|
| Depositing tokens into a liquidity pool | **Likely a disposition** — you exchange Token A for LP tokens. Report capital gain/loss at FMV. |
| Receiving yield/rewards | **Income at FMV when received** (business or property income) |
| Impermanent loss | **Not deductible until crystallized** — only realized when you withdraw from the pool |
| Withdrawing from pool | **Disposition of LP tokens** — report capital gain/loss |

### Airdrops

**CRA's general position:**

| Airdrop Type | Tax Treatment |
|-------------|--------------|
| Promotional airdrop (no action required) | **Income at FMV when received** — reported as business or property income |
| Airdrop tied to holding (e.g., Uniswap UNI drop) | **Income at FMV when tokens become available** |
| Hard fork (e.g., BCH from BTC fork) | **Income at FMV when made available** to the taxpayer |
| Bounty/task airdrop (e.g., testnet participation) | **Business income** — compensation for services rendered |

**Cost base of airdropped tokens = FMV at time of receipt.** Subsequent sale triggers a separate capital gain/loss event.

### NFTs

| Event | Tax Treatment |
|-------|--------------|
| **Purchasing an NFT with crypto** | Disposition of the crypto used — capital gain/loss on the crypto |
| **Selling an NFT you bought** | Capital gain/loss (if investment) or business income (if frequent trader/flipper) |
| **Selling an NFT you created** | **Business income** — proceeds from sale of inventory/services |
| **NFT royalties** | Business or property income, depending on activity level |

**Dapper Labs UPR confirms CRA is actively pursuing NFT traders** — this is not theoretical.

### Wrapped Tokens (WETH, WBTC, etc.)

**No explicit CRA guidance.** Two schools of thought:

1. **Conservative (CRA likely position):** Wrapping a token = **disposition** (crypto-to-crypto swap). You exchange BTC for WBTC — technically different assets. Report at FMV. In practice, gain/loss is usually near-zero since values are pegged.

2. **Aggressive (taxpayer argument):** Wrapping is a **change in form, not substance** — economically equivalent, no real gain or loss. Analogous to exchanging a $20 bill for four $5 bills.

**Recommended approach for CC:** Treat wrapping as a disposition with near-zero gain/loss. Document the transaction. Don't take the risk of CRA arguing it's unreported.

### Cross-Chain Bridges

Same treatment as wrapped tokens — a **bridge transaction is a crypto-to-crypto swap** and constitutes a taxable disposition. The bridged token on the destination chain has a cost base equal to FMV at the time of bridging.

### Key DeFi Principle

**Every token swap, wrap, bridge, deposit, or withdrawal involving a change in the underlying token is a taxable disposition under CRA's "property" framework.** The only non-taxable events are:

- Transferring the same token between your own wallets (no change in beneficial ownership)
- Transferring crypto to/from your own exchange account

---

## 5. CARF — Crypto-Asset Reporting Framework

### What Is CARF?

The **Crypto-Asset Reporting Framework (CARF)** is an OECD-developed international standard that requires crypto-asset service providers (CASPs) to collect customer information and report it to tax authorities, who then automatically exchange that data across borders. Think of it as **CRS (Common Reporting Standard) but for crypto**.

### Canada's Implementation Timeline

| Date | Milestone |
|------|-----------|
| **2023** | OECD finalizes CARF standard |
| **April 2024** | Canada's Federal Budget 2024 announces commitment to implement CARF |
| **August 15, 2025** | Draft legislative amendments to the Income Tax Act released |
| **September 12, 2025** | Public consultation period closes |
| **January 1, 2026** | **CARF takes effect** — due diligence and data collection obligations begin |
| **2027** | **First annual XML submissions** — CASPs file reports for 2026 transactions; first automatic international exchanges occur |

### Who Must Report (Reporting Crypto-Asset Service Providers — RCASPs)

Any entity that, as a business, provides services to exchange crypto-assets (or facilitate such exchanges) for or on behalf of customers, including:

- Centralized exchanges (Kraken, Coinbase, Coinsquare, Bitbuy, etc.)
- Crypto ATM operators
- Crypto brokers and dealers
- Payment processors accepting crypto
- Potentially: DeFi front-ends with KYC (emerging area)

### What Gets Reported

| Data Element | Details |
|-------------|---------|
| **Customer identity** | Name, address, date of birth, TIN (SIN for Canadians), jurisdiction of residence |
| **Transaction data** | Aggregate gross proceeds from crypto-to-fiat, crypto-to-crypto trades, and crypto transfers |
| **Account balances** | Year-end crypto holdings |
| **Transfer data** | Transfers exceeding $50,000 USD equivalent to non-RCASP wallets |

### International Scope

- **52 jurisdictions** committed to first CARF exchanges by 2027 (including Canada, U.S., UK, EU, Australia, Japan, South Korea, Singapore)
- Canada will receive crypto transaction data from **every participating jurisdiction** and share Canadian user data reciprocally
- This means **any exchange anywhere in the world** that has KYC on CC will eventually report to CRA

### Impact on CC

**CARF makes crypto tax evasion functionally impossible starting 2027.** Even if CC used a foreign exchange without a direct CRA court order, that exchange's home country will send the data to CRA through CARF automatic exchange.

**CC's Kraken data will flow through two channels:**
1. IRS court order data shared via Canada-U.S. tax treaty (already happening)
2. CARF automatic exchange starting 2027 (formalized, ongoing)

---

## 6. Penalty Framework for Unreported Crypto

### Penalty Escalation Ladder

| Violation | ITA Section | Penalty | Notes |
|-----------|-------------|---------|-------|
| **Late filing** | s.162(1) | 5% of unpaid tax + 1% per month (max 12 months) = **max 17%** of balance owing | Automatic — no intent required |
| **Repeat late filing** (within 3 years) | s.162(2) | 10% of unpaid tax + 2% per month (max 20 months) = **max 50%** of balance owing | Automatic on second offence |
| **Failure to report income** | s.163(1) | **10% of unreported amount** (federal) + provincial equivalent | Triggered on second instance within 4 taxation years |
| **Gross negligence** | s.163(2) | **50% of understated tax** (or $100, whichever is greater) | Requires CRA to prove knowledge or wilful blindness |
| **T1135 late filing** (foreign property > $100K) | s.162(7) | **$25/day**, min $100, max **$2,500** | Per year of non-filing |
| **T1135 gross negligence** | s.163(2.4) | **$500/month**, max **$12,000** + standard gross negligence penalty | For knowingly failing to file |
| **Criminal tax evasion** | s.239 | Fine of 50%-200% of evaded tax **+ up to 5 years imprisonment** | Requires criminal prosecution (CRA has not used this for crypto yet) |

### Compound Example: What $50K Unreported Crypto Income Costs

Assume CC has $50,000 in unreported crypto business income at a ~30% marginal rate ($15,000 tax owing):

| Scenario | Tax | Penalties | Interest (5% compound) | Total |
|----------|-----|-----------|----------------------|-------|
| **Filed 1 year late, no penalty** | $15,000 | $2,550 (17%) | ~$750 | **$18,300** |
| **Repeat late filer** | $15,000 | $7,500 (50%) | ~$750 | **$23,250** |
| **Failure to report (2nd time in 4 yrs)** | $15,000 | $5,000 (10% of unreported) | ~$750 | **$20,750** |
| **Gross negligence** | $15,000 | $7,500 (50% of tax) | ~$750 | **$23,250** |
| **Criminal evasion** | $15,000 | $15,000-$30,000 (100-200%) | ~$750 | **$30,750-$45,750 + prison** |

### Interest Compounds

CRA charges **prescribed interest** on all unpaid amounts, compounding daily. The current prescribed rate is approximately **5%** (adjusts quarterly). Interest runs from the original filing deadline, not from when CRA catches you.

### Statute of Limitations

| Scenario | Reassessment Window |
|----------|-------------------|
| Normal reassessment | **3 years** from date of original notice of assessment |
| Carelessness, neglect, or wilful default | **6 years** (s.152(4)(a)(i)) |
| Fraud / misrepresentation | **No limit** — CRA can reassess at any time (s.152(4)(a)(i)) |
| T1135 non-filing | **No limit** — clock doesn't start until a proper return is filed |

**For crypto:** If CRA can argue misrepresentation (e.g., you knew about crypto income and didn't report it), there is **no statute of limitations**. They can reassess back to 2014 or earlier.

### Voluntary Disclosure Program (VDP) — Updated October 1, 2025

The CRA's VDP was significantly updated effective October 1, 2025 (IC00-1R7). This is the escape hatch for taxpayers who want to come clean:

| Application Type | Interest Relief | Penalty Relief | Criminal Prosecution |
|-----------------|----------------|---------------|---------------------|
| **Unprompted** (CRA hasn't contacted you) | **75% waived** | **100% waived** | **No referral** |
| **Prompted** (CRA already contacted you about related issue) | **25% waived** | **Up to 100% waived** | **No referral** |
| **After audit/investigation** | **Not eligible** | **Not eligible** | **Not eligible** |

**VDP Requirements:**
- Must cover the most recent **6 taxation years** (domestic income) or **10 years** (foreign income/offshore assets)
- Must be **complete** — partial disclosures are rejected
- Must include **payment or payment arrangement** for all taxes owing
- Gross negligence penalties are **waived** for eligible VDP applications
- No criminal prosecution referral for any VDP-accepted disclosure

**Critical for CC:** The VDP is the best option if there are any past years with unreported crypto. But eligibility **evaporates** the moment CRA initiates contact about crypto. With CARF starting January 2026, the window for unprompted VDP applications is narrowing rapidly.

---

## 7. CC-Specific Risk Assessment & Action Items

### Current Risk Profile

| Risk Factor | Status | Severity |
|-------------|--------|----------|
| Kraken account data known to CRA | **Near certain** (via IRS 2023 court order + treaty) | HIGH |
| OANDA reporting | **Automatic** (regulated broker, T5008 issued) | MANAGED |
| Active trading classification | **Business income** (12 automated strategies, ATLAS infrastructure) | MANAGED (already treating as business income per ATLAS_TAX_STRATEGY.md) |
| T1135 exposure | **LOW** (crypto holdings under $100K CAD cost base) | LOW |
| DeFi/NFT exposure | **Minimal** (CC primarily trades on centralized exchanges) | LOW |
| CARF exposure starting 2027 | **Universal** (all exchange data will flow to CRA automatically) | HIGH (long-term) |
| Past-year compliance | **Verify** — ensure all Kraken activity from 2024 is reported on 2024 T1 | CRITICAL |

### Action Items (Priority Order)

1. **Verify 2024 tax return completeness** — Ensure all Kraken trades for 2024 are reported on T2125 (business income) or Schedule 3 (capital gains for long-term holdings). The 2024 return is due June 15, 2026 (self-employed) with payment due April 30, 2026.

2. **Maintain ACB records** — Weighted average cost method is mandatory in Canada (NOT FIFO, NOT LIFO). Every crypto-to-crypto swap is a disposition. Tools: Koinly, CoinTracker, or manual spreadsheet reconciled to Kraken export.

3. **Separate active trading from investment holdings** — Document in writing (investment policy statement) that cold storage BTC/ETH are held for long-term appreciation (capital gains treatment) while Kraken/ATLAS trading is business income.

4. **T1135 monitoring** — If total cost of foreign-held crypto (Kraken is US-based) exceeds $100,000 CAD at any point during the year, T1135 must be filed. Currently below threshold but monitor as portfolio grows.

5. **VDP assessment** — If any prior years (2021-2023) have unreported crypto activity, file a VDP application **immediately** while it can still be unprompted. The window closes the moment CRA sends a letter.

6. **CARF preparation** — Starting January 1, 2026, Kraken is collecting enhanced data for CARF reporting. Ensure TIN (SIN) is accurate on all exchange accounts. Discrepancies between exchange-reported data and tax returns will trigger automatic flags.

7. **Staking rewards documentation** — If CC earns any staking rewards on Kraken, document FMV in CAD at time of receipt. This is income when received, not when sold.

---

## Appendix: Key Legislative References

| Reference | Description |
|-----------|-------------|
| ITA s.9 | Business income — net profit from business |
| ITA s.12(1)(c) | Property income — interest, dividends, rents, royalties |
| ITA s.38 | Capital gains inclusion rate (currently 50%) |
| ITA s.39 | Definition of capital gain/loss |
| ITA s.47 | Identical properties — weighted average cost (ACB method) |
| ITA s.54 | Definition of "disposition" (includes crypto-to-crypto swaps) |
| ITA s.152(4) | Extended reassessment periods (6 years for neglect, unlimited for fraud) |
| ITA s.162(1)-(2) | Late filing penalties |
| ITA s.162(7) | T1135 late filing penalty ($25/day) |
| ITA s.163(1) | Repeated failure to report income (10% penalty) |
| ITA s.163(2) | Gross negligence penalty (50% of understated tax) |
| ITA s.163(2.4) | T1135 gross negligence ($500/month, max $12,000) |
| ITA s.231.2(2) | Unnamed persons requirements (UPRs) — exchange data orders |
| ITA s.239 | Criminal tax evasion (50-200% fine + imprisonment) |
| IT-479R | Transactions in securities (badges of trade for business vs. capital) |
| IC00-1R7 | Voluntary Disclosures Program (updated October 1, 2025) |

---

## Sources

- [Canada Struggles to Track Crypto Taxes as $100M Recovered in Audits — CoinDesk (Dec 2025)](https://www.coindesk.com/policy/2025/12/08/40-of-canadian-crypto-users-flagged-for-tax-evasion-risk-canadian-tax-authority-reveals)
- [CRA Cryptocurrency Audits: How the CRA Tracks Crypto — Taxpayer.law](https://taxpayer.law/cra-cryptocurrency-audits/)
- [CRA Audit Changes 2025-2026 — JWCGA](https://jwcga.ca/canada-revenue-agency/cra-audit-changes-2025-2026/)
- [How the CRA Tracks Cryptocurrency — Tax Partners](https://www.taxpartners.ca/how-the-canada-revenue-agency-tracks-crypto-transactions)
- [CRA Turns Its Focus to Cryptocurrency Transactions — DWPV (UPR analysis)](https://dwpv.com/en/Insights/Publications/2021/CRA-Turns-Focus-Cryptocurrency-Transactions)
- [Canada Targets Dapper Labs Users in Second-Ever Crypto Tax Probe — The Block (2025)](https://www.theblock.co/post/381627/canada-targets-dapper-labs-users-in-second-ever-crypto-tax-probe-as-enforcement-gap-widens-report)
- [Amicarelli v The King — Tax Interpretations](https://taxinterpretations.com/content/1085949)
- [Amicarelli v The King — Aird & Berlis Analysis](https://www.airdberlis.com/who-we-are/representative-matters/work/tax-court-delivers-first-judicial-guidance-on-treatment-of-losses-incurred-in-bitcoin-theft-fraud)
- [Amicarelli v The King — Mondaq Analysis](https://www.mondaq.com/canada/tax-authorities/1732940/amicarelli-v-the-king-how-cryptocurrency-exchange-losses-are-treated-for-tax-purposes-under-canadian-cryptocurrency-tax-laws)
- [Taxing Unrealized Crypto Gains: TCC Guidance — Lexology](https://www.lexology.com/library/detail.aspx?g=94a096a8-4dc1-4266-9a79-2824c96b895c)
- [CRA Reporting Income from Crypto Mining and Staking — Canada.ca](https://www.canada.ca/en/revenue-agency/programs/about-canada-revenue-agency-cra/compliance/cryptocurrency-guide/income-crypto-mining-staking-activities.html)
- [CRA Reporting Income from Crypto Transactions — Canada.ca](https://www.canada.ca/en/revenue-agency/programs/about-canada-revenue-agency-cra/compliance/cryptocurrency-guide/income-crypto-transactions.html)
- [Canada DeFi Taxes — Koinly Expert Guide](https://koinly.io/blog/canada-defi-tax/)
- [Crypto Mining and Staking in Canada: CRA Tax Treatment — Mackisen CPA](https://mackisen.com/blog/crypto-mining-and-staking-rewards-in-canada-how-cra-taxes-mining-validators-defi-yield-and-on-chain-rewards)
- [CARF in Canada: Preparing for Crypto-Asset Reporting 2026 — TaxDo](https://taxdo.com/resources/blog/post/carf-canada-crypto-asset-reporting-2026)
- [Proposed Crypto-Asset Reporting for Canadian Digital Finance — RSM Canada](https://rsmcanada.com/insights/tax-alerts/2025/proposed-crypto-asset-reporting-pivotal-for-canadian-digital-finance-regulation.html)
- [OECD CARF Monitoring and Implementation Update 2025 (PDF)](https://www.oecd.org/content/dam/oecd/en/networks/global-forum-tax-transparency/crypto-asset-reporting-framework-monitoring-implementation-update-2025.pdf)
- [Global Crypto Tax Reporting Takes Effect: CARF Goes Live — Crowdfund Insider (Jan 2026)](https://www.crowdfundinsider.com/2026/01/257069-global-crypto-tax-reporting-takes-effect-oecds-carf-framework-goes-live-in-48-nations/)
- [CRA Penalties: False Reporting or Repeated Failure — Canada.ca](https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/interest-penalties/false-reporting.html)
- [ITA Section 162 — Justice Canada](https://laws-lois.justice.gc.ca/eng/acts/I-3.3/section-162.html)
- [ITA Section 163 — Justice Canada](https://laws-lois.justice.gc.ca/eng/acts/I-3.3/section-163.html)
- [CRA VDP Updates October 2025 — Dentons](https://www.dentons.com/en/insights/alerts/2025/november/26/cra-updates-voluntary-disclosures-program)
- [CRA VDP: Canadian Tax Lawyer's Guide — TaxPage](https://taxpage.com/articles-and-tips/cra-voluntary-disclosure-program-vdp-a-canadian-tax-lawyers-guide-to-the-new-rules-effective-october-1-2025/)
- [CRA VDP Streamlined Program — EY Tax Alert 2025 No. 46](https://www.ey.com/en_ca/technical/tax/tax-alerts/2025/tax-alert-2025-no-46)
- [Cancellation of Capital Gains Inclusion Rate Increase — Scotia Wealth](https://enrichedthinking.scotiawealthmanagement.com/2025/04/07/cancellation-of-the-proposed-capital-gains-inclusion-rate-increase/)
- [Government of Canada: Deferral of Capital Gains Change — Canada.ca](https://www.canada.ca/en/department-finance/news/2025/01/government-of-canada-announces-deferral-in-implementation-of-change-to-capital-gains-inclusion-rate.html)
- [Cancellation of Canadian Capital Gains Inclusion Rate Increase — Lexology](https://www.lexology.com/library/detail.aspx?g=46c1a57f-a1e5-4f35-98a8-c1afec1a77df)
- [Crypto Tax Planning & Voluntary Disclosure — Tax Partners](https://www.taxpartners.ca/canadian-cryptocurrency-tax-planning-income-tax-voluntary-disclosure-relief-explained)
- [Kraken Compliance with IRS Court Order — The Block](https://www.theblock.co/post/259757/kraken-irs-user-data-order)

---

*This document is for informational and compliance planning purposes. It does not constitute legal or tax advice. CC should consult a qualified Canadian tax professional before making filing decisions. ATLAS researches, calculates, and prepares — CC reviews and submits.*
