# ATLAS DeFi Tax Guide v2.0 — Canadian Decentralized Finance

> **Compiled by:** ATLAS (CC's CFO Agent)
> **Date:** 2026-03-27
> **Scope:** Canadian tax treatment of every major DeFi activity — staking, liquidity pools, yield farming, NFTs, bridges, DAOs, airdrops, DeFi lending, DEX trading, and enforcement
> **Jurisdiction:** Canada (Ontario) | **Taxpayer profile:** Self-employed sole proprietor, 22, active crypto trader
> **Authority level:** CRA published guidance, Income Tax Act (ITA), CRA interpretation bulletins and folios, Tax Court of Canada decisions
> **Supplements:** `CRA_CRYPTO_ENFORCEMENT_INTEL.md` (enforcement), `ATLAS_TAX_STRATEGY.md` (main playbook), `ATLAS_DEDUCTIONS_MASTERLIST.md` (deductions)

---

## Critical Framing: No DeFi-Specific CRA Legislation Exists

The CRA has published guidance on **mining and staking** (canada.ca crypto guide, updated 2023; CRA Interpretation 2024-1031821I7, January 2025) but has issued **no formal guidance, interpretation bulletin, or information circular** specifically addressing DeFi protocols, liquidity pools, yield farming, cross-chain bridges, DAOs, or governance tokens.

**What this means in practice:**
- All DeFi tax treatment is derived by applying general ITA principles to novel technology
- The CRA treats crypto-assets as **"property"** under the ITA (not currency), established in the Department of Finance technical interpretation (2013) and confirmed in CRA Guide "Information for crypto-asset users and tax professionals" (canada.ca)
- Every acquisition, disposition, or receipt of property has potential tax consequences
- **The taxpayer bears the burden of characterization** — document your position and apply it consistently year to year

**The fundamental principle underlying all DeFi tax:**
> Any time you give up one crypto-asset and receive a different one, you have **disposed of property** under ITA s.248(1). The only exception is transferring identical assets between your own wallets with no change in beneficial ownership.

---

## Table of Contents

1. [Staking](#1-staking)
2. [Liquidity Pools (LPs)](#2-liquidity-pools-lps)
3. [Yield Farming](#3-yield-farming)
4. [NFTs](#4-nfts)
5. [Bridges and Wrapping](#5-bridges-and-wrapping)
6. [DAOs](#6-daos)
7. [Airdrops and Hard Forks](#7-airdrops-and-hard-forks)
8. [DeFi Lending and Borrowing](#8-defi-lending-and-borrowing)
9. [DEX Trading](#9-dex-trading)
10. [Record-Keeping Requirements](#10-record-keeping-requirements)
11. [CRA Enforcement — DeFi Specifically](#11-cra-enforcement--defi-specifically)
12. [Key Case Law](#12-key-case-law)
13. [Summary Risk Table](#13-summary-risk-table)
14. [Action Items for CC](#14-action-items-for-cc)

---

## 1. Staking

### Audit Risk: MEDIUM | Timing: NOW

### What Is Staking

Staking is the process of locking crypto-assets in a proof-of-stake network to validate transactions and earn rewards. Two operationally distinct categories exist with different tax treatment:

| Category | Description | Examples |
|----------|-------------|---------|
| **Validator staking** | Operating your own node, committing hardware, minimum stake thresholds, technical responsibility | ETH solo validator (32 ETH minimum), SOL validator |
| **Delegator staking** | Delegating tokens to a third-party validator or exchange staking service | Kraken Earn, Coinbase staking |
| **Liquid staking** | Receiving a liquid receipt token representing your staked position | Lido (stETH), Rocket Pool (rETH) |

### CRA's Published Position

**Source:** CRA Guide "Reporting income from crypto-asset mining and staking activities" (canada.ca) and CRA Interpretation 2024-1031821I7 (January 17, 2025 — specific to CSA-compliant custodial staking platforms).

The CRA states: *"If you are staking cryptocurrency and receive rewards, the rewards are taxable when you receive them."*

**ITA Reference:**
- **Business income:** ITA s.9(1) — profit from a business. Applies if operating a validator node commercially, staking as a primary revenue activity, or managing multiple validators with significant infrastructure.
- **Property income:** ITA s.12(1)(c) by analogy and s.9(1) applied to passive property returns. Applies if delegating passively — receiving rewards without active participation.
- Both classifications result in **100% inclusion** in income (no capital gains 50% inclusion rate — that applies only to capital gains under ITA s.38).

### Income Inclusion: When Is the Tax Event?

**Receipt date is the trigger.** The CRA's position on crypto rewards (mining analogy from IT-490 interpretation) holds that income is recognized **when the taxpayer has dominion and control** over the asset — meaning when rewards are credited to your wallet or exchange account.

| Staking Type | Income Trigger | FMV to Use |
|-------------|---------------|------------|
| On-chain validator rewards | Block timestamp when rewards credited | Spot price in CAD at that block time |
| Exchange staking (Kraken Earn) | Date credited to account as shown on exchange statement | Exchange spot price at credit time (use UTC end-of-day if intraday unavailable) |
| Liquid staking (stETH rebasing) | Each daily rebase that increases stETH balance | Spot price at each rebase date |

**Practical problem for daily rebasing tokens (stETH):** Lido's stETH rebases daily — that is 365 separate taxable income events per year per staked ETH. Each rebase amount must be converted to CAD and reported. Koinly and CoinTracker handle stETH rebase events automatically when you connect your wallet. Do not attempt to calculate 365 daily events manually.

### ACB of Staking Rewards

Each batch of staking rewards received creates a **new lot** in your adjusted cost base pool at the FMV on the day of receipt.

**Example:**
- January 15: Receive 0.05 ETH staking reward when ETH = $4,000 CAD
  - Income recognized: 0.05 x $4,000 = **$200 CAD** (property income — T1 Line 12100 or T2125)
  - ACB of that 0.05 ETH lot: **$200 CAD**
- March 20: Sell that 0.05 ETH when ETH = $6,000 CAD
  - Proceeds: 0.05 x $6,000 = $300 CAD
  - ACB: $200 CAD
  - Capital gain: **$100 CAD** (50% inclusion if investor; 100% if business trader)

**You pay tax twice on staking rewards:** once when received (income), and again when sold (capital gain or business income on the appreciation). This is the correct treatment under the ITA, not double-counting — these are two separate economic events.

### ETH 2.0 / Beacon Chain Staking Specifics

Early ETH 2.0 staking (before the Shanghai withdrawal upgrade, April 2023) locked ETH and did not allow reward withdrawals. Rewards accrued on the Beacon Chain but were inaccessible.

**CRA's likely position (no formal guidance issued):**
- **Conservative approach (recommended):** Rewards are taxable when credited to the Beacon Chain balance, even if illiquid, because the taxpayer has constructive receipt — the right to the income has vested.
- **Aggressive approach (taxpayer argument):** No tax until Shanghai enabled actual access (April 2023), because prior to that there was no dominion and control.

For CC's current staking activity (post-Shanghai, all rewards freely withdrawable), there is no ambiguity — income on receipt date.

### Validator vs Delegator — Tax Classification Test

| Factor | Points to Business Income | Points to Property Income |
|--------|--------------------------|---------------------------|
| Operating your own validator node | YES | — |
| Hardware/infrastructure investment | YES | — |
| Delegating to a third-party validator | — | YES |
| Exchange-based staking (1-click) | — | YES |
| Staking is your primary income source | YES | — |
| Staking is incidental to other activities | — | YES |
| Active management of validator configuration | YES | — |

**CC's situation:** Kraken Earn or liquid staking protocols = **property income**, not business income. Report on **T1 Line 12100 (Interest and other investment income)** or within T2125 if treating all crypto activity as a single trading business. Either is defensible — pick one and be consistent across all years.

### Estimated Tax Impact (CC Profile, ~30% marginal rate)

| Annual Staking Rewards in CAD | Tax Owing (Income on Receipt) | Additional Tax if Rewards Appreciate 50% Before Sale |
|------------------------------|------------------------------|------------------------------------------------------|
| $500 | ~$150 | ~$75 capital gains tax |
| $2,000 | ~$600 | ~$300 capital gains tax |
| $10,000 | ~$3,000 | ~$1,500 capital gains tax |

---

## 2. Liquidity Pools (LPs)

### Audit Risk: MEDIUM-HIGH | Timing: NOW

### What Is a Liquidity Pool

A liquidity pool (LP) involves depositing two tokens (e.g., ETH + USDC) into a smart contract at a defined ratio, receiving LP tokens representing your pro-rata share of the pool. Fees generated by traders are distributed to LP token holders proportionally.

### The Three Taxable Event Types in an LP Position

**Event Type 1: Depositing into the pool**

The CRA treats the token-to-LP-token exchange as a **taxable disposition** because you surrender two distinct assets (ETH and USDC) and receive a new, different asset (the LP token).

- **Disposition of Token A (ETH):** Proceeds = FMV of ETH deposited in CAD. Capital gain/loss = proceeds minus ACB of that ETH.
- **Disposition of Token B (USDC):** If USDC = $1 CAD, gain is typically nil. Any peg deviation must be computed.
- **ACB of LP tokens received:** Combined FMV of both tokens deposited at the time of deposit.

**ITA Reference:** ITA s.248(1) — definition of disposition. ITA s.40(1) — gain or loss computation.

**Example:**
- Deposit 1 ETH ($4,000 CAD) + 4,000 USDC ($4,000 CAD) into Uniswap V3 pool
- Your ACB on that 1 ETH was $2,500 CAD
- Disposition of ETH: $4,000 proceeds - $2,500 ACB = **$1,500 capital gain** (or business income)
- Disposition of USDC: $4,000 - $4,000 = **$0 gain**
- ACB of LP tokens received: **$8,000 CAD**

**Event Type 2: Fee income while in the pool**

Trading fees accumulate in the LP position and are **income when received or accrued** — business or property income depending on the activity level of the LP participant. On Uniswap V3, fees must be manually claimed as a separate on-chain transaction, making each claim a distinct income event.

- Each fee collection is a taxable income event at FMV in CAD on the date of collection
- ACB of fee tokens received = FMV at time of receipt (same mechanics as staking rewards)
- **ITA Reference:** s.9(1) — profit from a business (or property income by analogy)

**Event Type 3: Withdrawing from the pool**

Withdrawing LP tokens in exchange for the underlying tokens is a **disposition of LP tokens** and an acquisition of the returned tokens.

- Proceeds of LP token disposition = FMV of underlying tokens received on withdrawal in CAD
- ACB of LP tokens = as established on deposit
- New ACB of tokens received = their FMV at withdrawal date (they are a fresh acquisition)

### Impermanent Loss — NOT a Separately Deductible Loss

**This is the most widely misunderstood aspect of LP taxation in Canada.**

Impermanent loss (IL) is the economic shortfall incurred when pool asset prices diverge from the deposit ratio, causing LP holders to receive a different quantity of tokens than deposited. However:

- IL is an economic concept, not a recognized tax concept under the ITA
- CRA computes proceeds as the **actual FMV of tokens received on withdrawal**, not the hypothetical value you would have had if you held the tokens directly
- There is no ITA provision permitting a deduction for "what you could have earned if you had done something else"
- The economic impact of IL is only **captured in the capital loss calculation** when withdrawal proceeds are lower than the LP token ACB

**Example where IL is reflected in the capital loss:**
- Deposit: 1 ETH ($4,000) + 4,000 USDC ($4,000) = LP ACB $8,000 CAD
- ETH drops significantly; withdraw and receive: 0.8 ETH ($2,400 at $3,000/ETH) + 5,200 USDC ($5,200)
- Withdrawal FMV: $2,400 + $5,200 = **$7,600**
- Capital loss on LP tokens: $7,600 - $8,000 = **-$400** (deductible at 50% inclusion = -$200 net capital loss)

The $400 loss embeds the effect of impermanent loss — it is deductible because it is reflected in actual proceeds, not because "IL" is a recognized deduction category.

### LP Tax Complexity Score: HIGH

LP positions generate multiple interacting taxable events. Uniswap V3 concentrated liquidity positions are especially complex — changing the price range triggers additional dispositions of LP tokens and re-acquisitions at the new range's parameters.

---

## 3. Yield Farming

### Audit Risk: HIGH | Timing: NOW

### What Is Yield Farming

Yield farming deploys capital into one or more DeFi protocols to maximize return through accumulated governance tokens, protocol incentives, and fee income. Complex strategies involve chained protocols — for example: deposit into Aave, use aToken as collateral in Curve, stake Curve LP tokens in Convex to earn CVX and CRV simultaneously.

### Governance Token Rewards — Income on Receipt

CRA analogy: Governance token rewards are analogous to mining rewards and promotional airdrops — received as compensation for providing liquidity or services to a protocol.

**Tax treatment:**
- **Income at FMV in CAD on the date received** — ITA s.9(1) for active farmers, property income under s.9(1) for passive
- ACB of governance tokens received = FMV at time of receipt
- Subsequent sale triggers a separate capital gain/loss event on the appreciation or depreciation after receipt

**ITA Reference:** CRA Cryptocurrency Guide (December 2023) states rewards from providing services or liquidity to a protocol are taxable as income on receipt. IT-334R2 (Miscellaneous Receipts) provides the analogy for unexpected or promotional property receipts.

### Multi-Protocol Farming Chains — The ACB Nightmare

A single yield farming strategy can generate the following chain of taxable events:

```
Step 1: Deposit ETH into Aave             → Receive aETH
         Disposition of ETH + acquisition of aETH at FMV

Step 2: Deposit aETH into Curve           → Receive Curve LP tokens
         Disposition of aETH + acquisition of Curve LP tokens at FMV

Step 3: Stake Curve LP into Convex        → Receive cvxLP tokens
         Disposition of Curve LP tokens + acquisition of cvxLP tokens at FMV

Step 4: CRV rewards claimed daily         → Income: FMV of CRV at claim date (365 events/year)

Step 5: CVX rewards claimed daily         → Income: FMV of CVX at claim date (365 events/year)

Step 6: Auto-compound: reinvest CRV       → Disposition of CRV (gain/loss) + new LP acquisition

Step 7: Unwind in reverse                 → 3-4 additional disposition events
```

**Estimated annual taxable events in one farming position:** 5 dispositions on entry, 730 income events (daily CRV + CVX), potentially 730 auto-compound dispositions, 4 dispositions on exit. **Total: 1,400-1,500+ taxable events per year per farming position.**

### Auto-Compounders (Yearn Finance, Beefy Finance)

Auto-compounding vaults reinvest earned rewards automatically, sometimes multiple times per day:

- Each harvest of a reward token = income at FMV in CAD
- Each reinvestment of that token into LP = disposition of reward token + acquisition of LP token
- A daily compounder creates 365 income events AND 365 disposition events per year per vault

**Tax software note:** Koinly and CryptoTaxCalculator categorize Yearn/Beefy vault interactions as aggregate positions rather than individual compound events in some configurations. CRA has not issued guidance approving this aggregation — the individual-event approach is more conservative and defensible under audit.

### Asymmetric Tax Risk in Yield Farming

This is the most dangerous tax exposure in DeFi:

1. You receive 1,000 governance tokens when FMV = $10 each = **$10,000 income, $3,000 tax owing at 30%**
2. Token crashes 90% before you sell
3. You sell 1,000 tokens at $1 each = $1,000 proceeds vs $10,000 ACB = **-$9,000 capital loss**
4. Capital loss offsets capital gains only (not income) — deductible at 50% inclusion = **-$4,500 net capital loss**
5. Net position: paid $3,000 income tax; recovered at most $4,500 × 30% = $1,350 if you have offsetting capital gains
6. **Net tax damage if no offsetting capital gains: $3,000 income tax paid, $9,000 real economic loss, $1,350 future recovery**

**Mitigation:** Sell governance tokens promptly upon receipt to crystallize capital gains/losses close to the income event FMV, and avoid the asymmetric income-tax-on-receipt / capital-loss-on-sale mismatch.

### Estimated Tax Impact — Yield Farming

| Annual Governance Token Income (FMV at Receipt) | Tax at ~30% Marginal Rate | Risk if Token Falls 80% |
|-------------------------------------------------|--------------------------|-------------------------|
| $1,000 | ~$300 | Pay $300, lose $800 real value, recover ~$120 |
| $5,000 | ~$1,500 | Pay $1,500, lose $4,000 real value, recover ~$600 |
| $20,000 | ~$6,000 | Pay $6,000, lose $16,000 real value, recover ~$2,400 |

---

## 4. NFTs

### Audit Risk: HIGH | Timing: NOW

### CRA Enforcement Context

The Dapper Labs Unnamed Persons Requirement (UPR, Federal Court, September 2025) compelled Dapper Labs to disclose all Canadian users on the NBA Top Shot and Flow blockchain platforms. This confirmed that CRA is **actively pursuing NFT traders specifically** — this is not a theoretical future risk.

**ITA Reference for UPR authority:** ITA s.231.2(2) — unnamed persons requirement.

### Business Income vs Capital Gains Test for NFTs

| Indicator | Points to Business Income | Points to Capital Gains |
|-----------|--------------------------|------------------------|
| Frequency of NFT purchases/sales | High volume | Occasional |
| Holding period | Days/weeks (flipping) | Months/years |
| Intent at purchase | Resale profit | Collection or long-term appreciation |
| Knowledge and expertise | Deep market expertise | Casual collector |
| Time spent on NFT activities | Significant | Minimal |
| Use of infrastructure (bots, analytics) | YES | NO |

### Minting an NFT (Purchasing with Crypto)

When you spend ETH or another crypto to mint or purchase an NFT, **two separate taxable events occur simultaneously:**

1. **Disposition of the crypto used** — capital gain/loss on the crypto spent
   - Proceeds = FMV of NFT received in CAD (which equals FMV of crypto spent at transaction time)
   - Gain/loss = proceeds minus ACB of that crypto
2. **Acquisition of the NFT** — establishes your ACB in the NFT
   - ACB of NFT = FMV of crypto spent in CAD + gas fees paid in CAD (ITA s.54 ACB definition includes incidental acquisition costs)

**Example:**
- Mint NFT using 0.5 ETH + 0.02 ETH gas when ETH = $4,000 CAD
- Total ETH disposed: 0.52 ETH × $4,000 = $2,080 CAD proceeds
- ACB of that 0.52 ETH: $1,200 CAD
- **Capital gain on ETH disposition: $2,080 - $1,200 = $880 CAD**
- **ACB of the NFT: $2,080 CAD**

### Selling an NFT

Sale proceeds minus ACB = capital gain (investor) or business income (active flipper).

If sold for crypto, proceeds = FMV of crypto received in CAD at transaction date. Selling an NFT also creates a **new acquisition of the crypto received** at that FMV.

**Example (continuing from mint above):**
- Sell NFT 6 months later for 1.2 ETH when ETH = $5,000 CAD
- Proceeds: 1.2 × $5,000 = **$6,000 CAD**
- ACB: **$2,080 CAD**
- Gain: $6,000 - $2,080 = **$3,920 CAD**
- Capital gains tax (investor, 50% inclusion, 30% rate): $3,920 × 50% × 30% = **$588**
- Business income tax (flipper, 100% inclusion, 30% rate): $3,920 × 30% = **$1,176**

### Creator NFT Sales — Always Business Income

When you **create** an NFT and sell it:
- Proceeds from the sale = **business income** — you are selling inventory or the product of your creative services
- Report on **T2125** under the relevant industry code
- Deductible: platform fees (OpenSea/Blur listing fees), gas fees for minting and listing, equipment CCA, software costs
- **ITA Reference:** ITA s.9(1) — profit from a business. IT-218R (Profits, capital gains, and losses from property sales) provides the creator vs investor distinction.

### NFT Royalties

Creator royalties (e.g., 5-10% of secondary sales automatically sent to creator wallet via smart contract):
- **Business or property income on receipt** — FMV in CAD at the time each royalty payment arrives
- If operating an NFT creative business = business income on T2125
- **ITA Reference:** IT-465R (Royalties) — royalty income is included in income when receivable; analogy applies to on-chain royalty payments.

### NFT-to-NFT Swaps — Barter Transaction

Swapping one NFT for another without cash changing hands is a **barter transaction** under Canadian tax law:

- **Proceeds of disposition = FMV of the NFT received** — ITA s.69 (non-arm's-length and barter pricing rules); CRA Interpretation Bulletin IT-490 (Barter Transactions)
- Capital gain = FMV of NFT received minus ACB of NFT given up
- ACB of new NFT = FMV at time of swap

**Example:**
- Swap NFT A (ACB $3,000 CAD) for NFT B (FMV $5,000 CAD)
- Proceeds on NFT A: $5,000 CAD
- Capital gain: $5,000 - $3,000 = **$2,000 CAD**
- ACB of NFT B: **$5,000 CAD**

### Gaming NFTs and Play-to-Earn

No CRA guidance exists. Conservative treatment by applying general principles:
- In-game item sales generating real crypto income = taxable business or property income
- Play-to-earn model rewards = income on receipt at FMV (same as governance token rewards)
- Breeding, crafting, or manufacturing in-game NFTs for sale = business income if done at scale

---

## 5. Bridges and Wrapping

### Audit Risk: LOW-MEDIUM for the transactions themselves; HIGH for non-compliance | Timing: NOW

### The CRA's Property Framework Applied to Bridges

**No formal CRA guidance on bridges or wrapping exists.** The CRA's property-based framework leads to the following conclusion:

> **Any exchange of one crypto-asset token for a different crypto-asset token is a taxable disposition, regardless of whether the economic value is equivalent.**

This applies to WBTC/WETH wrapping, cross-chain bridging, and liquid staking receipt tokens (ETH to stETH).

**ITA Reference:** ITA s.248(1) — "disposition" of property means any transaction or event entitling a taxpayer to proceeds of disposition of the property, including the exchange of one property for another. ITA s.54 — "proceeds of disposition" means the sale price or the value of other consideration received.

### Wrapping (ETH to WETH, BTC to WBTC)

**Conservative position (CRA likely):**
- Wrapping ETH for WETH is a **disposition of ETH** and acquisition of WETH
- Proceeds = FMV of WETH received (which equals FMV of ETH wrapped, since both trade at 1:1)
- In practice: gain/loss is near-zero because values are pegged
- The transaction is technically taxable but the tax owing is negligible
- Still must be **reported** if the ACB of the ETH differed from its FMV (which it usually does for appreciated holdings)

**Taxpayer (aggressive) position:**
- Wrapping is a change in form, not substance — economic substance is identical at all times
- No beneficial ownership has been transferred; you hold the same economic interest
- Analogous to exchanging a $20 bill for four $5 bills — no taxable disposition has occurred
- ITA s.248(1) "disposition" requires an alienation of a beneficial interest in property, not merely a change in technical form

**Atlas recommendation:** Report wrapping as a disposition with near-zero gain/loss. The conservative position costs essentially no incremental tax (the gain is near-zero since values are pegged) and eliminates audit risk entirely. Do not litigate the aggressive position for a transaction that generates essentially no benefit — the legal fees would vastly exceed any tax saving.

### Cross-Chain Bridges

Same treatment as wrapping. When you bridge ETH from Ethereum mainnet to Arbitrum:
- You surrender ETH on Ethereum
- You receive bridged ETH on Arbitrum (technically a different asset at the smart contract level)
- CRA's likely position: disposition of ETH at current FMV; acquisition of bridged ETH at same FMV

**Additional complexity with multi-hop bridges:** Some bridges use intermediate wrapped or canonical tokens. A bridge from Ethereum to Solana may involve: ETH → WETH → wrapped ETH on Wormhole (each step a potential disposition).

**Practical problem with appreciated ETH:** If you hold 1 ETH with ACB of $2,000 CAD and bridge when ETH = $5,000 CAD, you have a $3,000 capital gain on a bridge transaction where you received no cash and have no funds to pay the tax. This is the correct application of the law — plan bridges accordingly.

**Tax mechanics:**
1. Disposition of ETH: proceeds = FMV at bridge initiation in CAD
2. Capital gain = proceeds minus ACB of ETH
3. Gas fees paid in ETH = separate disposition of that ETH (near-zero ACB computation) + add to ACB of bridged asset received
4. Bridged ETH ACB = FMV at time of bridging

---

## 6. DAOs

### Audit Risk: MEDIUM | Timing: NOW (payments received) / FUTURE (governance distributions at scale)

### Holding DAO Governance Tokens — No Tax Event

Simply holding DAO governance tokens (UNI, COMP, MKR, AAVE) is not a taxable event. You hold property. Tax arises only on:
- Receipt of governance tokens (if airdropped or earned = income at FMV; see Section 7)
- Voting rewards (if any compensation is attached to voting = income at FMV)
- Sale or disposal = capital gain/loss or business income on disposition

**ITA Reference:** Property held without a disposition event does not create income — ITA s.248(1) definition of disposition applies.

### DAO Treasury Distributions to Token Holders

When a DAO votes to distribute treasury assets proportionally to token holders (analogous to a dividend but with no issuing corporation):

- **Income at FMV in CAD on date of receipt**
- Character depends on your relationship to the DAO: passive holder = property income; active contributor = business income
- Report: T2125 (business income) or T1 Line 12100 (investment income)
- ACB of tokens received = FMV at distribution date
- **ITA Reference:** DAO distributions are not eligible for the dividend tax credit (that applies only to dividends from taxable Canadian corporations — ITA s.82). Treated as property income under s.9(1).

### DAO Contributor Payments

If a DAO pays you in crypto for work performed (development, community management, design, legal, governance coordination):

- **Business income at FMV in CAD on the date received** — ITA s.9(1)
- Report on **T2125** under appropriate industry code
- CPP self-employment contribution obligation applies (both employee + employer portions = ~11.9%)
- ACB of crypto received as payment = FMV at date of receipt
- Deductible expenses against this income: same rules as any self-employment income (home office, equipment, professional development)

**Example:**
- DAO pays you 1,000 USDC ($1,000 CAD) for a smart contract audit
- Business income: $1,000 CAD on T2125
- CPP owing on this amount: ~$119 (combined employee/employer)
- If USDC is later held and converts to ETH via a swap: that is a separate disposition

### Governance Voting — Tax-Neutral

Submitting a governance vote is not a taxable event. No consideration is exchanged. The gas fee paid to submit the vote is a disposition of that gas-token ETH (near-zero or small capital gain/loss).

---

## 7. Airdrops and Hard Forks

### Audit Risk: HIGH | Timing: NOW

### CRA's Published Position on Airdrops

**CRA Cryptocurrency Guide (2023):** *"If you receive cryptocurrency from an airdrop following a hard fork, your income is the value of the cryptocurrency at the time you receive it."*

The CRA applies **IT-334R2 (Miscellaneous Receipts)** by analogy: if you receive property of value without paying for it, that value is income under ITA s.9(1) or s.12(1). This principle has been consistently applied across all CRA technical interpretations touching on crypto receipts.

### Classification by Airdrop Type

| Airdrop Type | CRA Treatment | ITA Reference | ACB of Tokens Received |
|-------------|--------------|---------------|------------------------|
| **Promotional** (random token drop, no action required) | Income at FMV when received | s.9(1) or s.12(1), IT-334R2 analogy | FMV at receipt date |
| **Holding-based** (e.g., Uniswap UNI — held v1, received governance token) | Income at FMV when tokens become claimable | s.9(1) or s.12(1) | FMV at claimable date |
| **Activity-based / retroactive** (used protocol, received retroactive drop) | Income at FMV when claimable | s.9(1) or s.12(1) | FMV at claimable date |
| **Bounty / testnet participation** (tested protocol, received compensation) | **Business income** — compensation for services | s.9(1) | FMV at receipt |
| **Spam / dust airdrop** (unsolicited scam tokens with nil FMV) | No income if FMV is demonstrably nil; document | IT-334R2 nil value exception | $0 ACB |

### The "Claimable vs Actually Claimed" Timing Risk

Many airdrops require an on-chain claim transaction. The CRA's likely position (applying constructive receipt doctrine, analogous to CRA's position on accrued but uncollected business income):

- Income arises when tokens **become claimable**, not when you execute the claim transaction
- Rationale: once claimable, you have the right to the income and can exercise it at any time

**Practical implication:** If tokens become claimable when price = $50 and you wait 8 months to claim when price = $5:
- Income recognized: $50 × number of tokens (when claimable)
- Tax owing: on the higher $50 FMV
- ACB of tokens: $50/token
- When sold at $5: $45/token capital loss (which offsets capital gains at 50% inclusion only)

**Risk mitigation:** Claim airdrops promptly so the "claimable date FMV" and "actual receipt FMV" are as close as possible.

### Hard Forks

**CRA's position (2023 Crypto Guide):**

When a blockchain hard fork distributes new tokens to existing holders (BCH from BTC in 2017, ETC from ETH in 2016):
- New fork tokens are **income at FMV when made available** to the taxpayer
- ACB of fork tokens = FMV at the time they became available
- Original token ACB is **not reduced** by the fork
- If the new fork tokens have $0 FMV at creation (obscure or illiquid fork with no trading market), income = $0, ACB = $0

**Example — Bitcoin Cash fork:**
- You held 1 BTC when BCH forked in 2017. BCH first traded at $400 CAD when available on your exchange.
- BCH income: **$400 CAD** (reported as property income in that tax year)
- ACB of BCH: **$400 CAD**
- BTC ACB: **unchanged**
- Sell BCH for $150 CAD later: $150 proceeds - $400 ACB = **-$250 capital loss**

### Estimated Tax Impact — Airdrops

| Scenario | Airdrop FMV at Claimable Date | Tax at 30% Marginal | Token Value When Sold | Net Tax Position |
|----------|------------------------------|--------------------|-----------------------|-----------------|
| UNI retroactive (400 UNI at $30 = $12,000) | $12,000 | **$3,600 income tax** | Sell at $10,000 | -$2,000 cap loss = ~$300 recovery; net tax cost: $3,300 |
| Small protocol drop ($200 CAD) | $200 | $60 | Token rugs ($0) | -$200 cap loss (~$30 recovery); net: $30 loss |
| Testnet bounty ($500) | $500 | $150 (business income) | N/A | $150 |
| Hard fork with nil FMV | $0 | $0 | Later trades for $2,000 | $2,000 capital gain when sold ($300 tax at 50% inclusion) |

---

## 8. DeFi Lending and Borrowing

### Audit Risk: MEDIUM | Timing: NOW

### Interest Income from Lending (Aave, Compound, etc.)

When you deposit crypto into a lending protocol and earn interest, the interest is **taxable income** regardless of whether it is paid in the deposited token or a protocol-specific token.

**For aToken-based protocols (Aave):** aTokens rebase daily — your balance increases each day. Each day's increase = taxable interest income at that day's spot price in CAD.

**For cToken-based protocols (Compound):** cTokens appreciate in value (exchange rate increases). Income is recognized as the cToken appreciates. Under ITA s.12(3), interest on debt obligations outstanding for more than 12 months must be reported on an **accrual basis annually** even if not received in cash.

**ITA Reference:** ITA s.12(1)(c) — any amount received or receivable as interest on money lent. ITA s.12(3) — annual accrual rule for interest-bearing obligations outstanding more than 12 months.

**Example:**
- Deposit $10,000 USDC into Aave at 5% APY
- Annual interest earned: $500 USDC
- CAD income (assuming $1 USDC peg): **$500 CAD**
- Report: T1 Line 12100 or T2125 if lending is part of the trading business
- ACB of interest received: $500 CAD (new lot at FMV on receipt)

### Collateral Deposits — NOT a Disposition (Usually)

Depositing crypto as collateral in a lending protocol to borrow against it:
- **Not a disposition** provided you retain beneficial ownership of the collateral and the protocol holds it purely as security
- Analogy: pledging a stock portfolio as brokerage margin collateral — no disposition until assets are actually sold
- **However:** If the protocol issues an **interest-bearing receipt token** (e.g., aETH on Aave in exchange for ETH collateral), that receipt token may constitute a different asset — triggering the same analysis as LP token deposits (conservative view = disposition)

### Borrowing Against Collateral — NOT Taxable Income

Taking a loan (USDC, DAI, or any asset) against your collateral is **not taxable income.** A loan creates a liability that must be repaid — it does not enrich the taxpayer on a net basis.

**Strategic implication (Buy, Borrow, Die strategy):** Instead of selling appreciated crypto and triggering capital gains, borrow against it and spend the loan proceeds. No tax event on borrowing. See `ATLAS_WEALTH_PLAYBOOK.md` for the full Buy/Borrow/Die strategy analysis.

**ITA Reference:** Loan proceeds are not income under any provision of the ITA — the loan creates a corresponding liability. General tax principles (not a specific provision) establish this.

### Liquidation Events — Taxable Disposition

If your collateral ratio falls below the liquidation threshold and the protocol automatically liquidates your collateral:
- **Taxable disposition of the collateral at the actual liquidation price in CAD**
- Capital gain = liquidation proceeds minus ACB of collateral
- The fact that you did not choose to sell is irrelevant — the ITA includes involuntary dispositions
- **ITA Reference:** ITA s.248(1) "disposition" explicitly encompasses events that entitle a person to proceeds of disposition, whether voluntary or involuntary. ITA s.44 and s.13(21.2) provide specific involuntary disposition rules for certain capital property — apply by analogy.

**Example:**
- Deposited 1 BTC (ACB: $30,000 CAD) as collateral; borrowed 20,000 USDC
- BTC falls; protocol liquidates 0.75 BTC at $38,000 CAD/BTC to cover the loan
- Liquidation proceeds: 0.75 × $38,000 = **$28,500 CAD**
- ACB of 0.75 BTC: 0.75 × $30,000 = **$22,500 CAD**
- **Capital gain on liquidation: $6,000 CAD** (or business income if crypto trading is your business)
- This gain must be reported even though you received no cash — the proceeds were applied to repay your debt

**Audit risk note:** Liquidation events are permanently on-chain. If there were gains at liquidation and they were not reported, this discrepancy will be apparent when CARF data and blockchain analytics reach CRA.

### Flash Loans

Flash loans (uncollateralized, must be repaid within the same Ethereum transaction) are an arbitrage tool. Tax treatment:
- The loan itself is not income (same principle as any loan)
- Any arbitrage profit captured in the same transaction = **business income** (arbitrage is always active trading, not passive)
- Gas fees paid = deductible business expense on T2125
- Net profit reported on T2125

---

## 9. DEX Trading

### Audit Risk: MEDIUM-HIGH | Timing: NOW

### Every Swap Is a Disposition — Non-Negotiable

Each token swap on a DEX (Uniswap, Curve, PancakeSwap, dYdX, Raydium, etc.) constitutes:
1. A **disposition of Token A** at FMV in CAD — capital gain/loss or business income
2. An **acquisition of Token B** at FMV in CAD (equals proceeds of Token A disposition) — establishes new ACB

**ITA Reference:** ITA s.39(1) and s.40(1) — capital gains on property dispositions. ITA s.9(1) — business income where trading is the taxpayer's course of conduct. CRA Technical Interpretation 2020-0850961I7 (confirmed crypto-to-crypto swaps are dispositions).

**Example:**
- Swap 2,000 USDC for 0.4 ETH when ETH = $5,000 CAD
- Disposition of 2,000 USDC: proceeds = $2,000 CAD; ACB = $2,000 CAD; gain = $0
- Acquisition of 0.4 ETH: ACB = $2,000 CAD
- Three weeks later: swap 0.4 ETH for 2,400 USDC when ETH = $6,000 CAD
  - Disposition of 0.4 ETH: proceeds = $2,400 CAD
  - ACB: $2,000 CAD
  - **Capital gain: $400 CAD** (50% inclusion if investor = $200 taxable; 100% if business trader)

### Gas Fees — Two Tax Consequences

Gas fees paid in ETH (or native chain token) have two simultaneous tax consequences:

1. **Disposition of the ETH used for gas** — a separate capital gain/loss event (usually small)
2. **Addition to the ACB** of the asset acquired in that transaction — ITA s.54 definition of ACB includes costs of acquisition including transaction costs

**ITA Reference:** ITA s.54 — ACB of property includes the cost plus all costs incurred to acquire the property (commissions, fees, expenses).

**Example with gas:**
- Swap costs 0.003 ETH in gas; ETH = $5,000 CAD; ACB of that 0.003 ETH = $8 CAD
- Gas in CAD: 0.003 × $5,000 = $15 CAD
- Disposition gain on gas ETH: $15 proceeds - $8 ACB = $7 capital gain (small but reportable)
- Gas cost ($15) added to ACB of the token you acquired in this swap

**Volume problem:** An active DEX trader executing 10 swaps per day generates 10 gas dispositions per day = 3,650 additional micro-taxable events per year. Each requires its own ACB calculation. Crypto tax software is not optional at this scale — manual calculation is not feasible and CRA would not accept estimates.

### Stablecoin-to-Stablecoin Swaps

Swapping USDC for USDT (or any stable-to-stable exchange) is still a taxable disposition under ITA principles. In practice, gain/loss is near-zero (both track $1 CAD) but must be recorded. Each stablecoin must have its ACB tracked separately.

### MEV and Sandwich Attacks

Maximal Extractable Value (MEV) sandwich attacks cause the victim trader to receive fewer tokens than the quoted swap rate. Tax treatment:
- You received the **actual tokens delivered to your wallet** — those are your proceeds of disposition of Token A
- No additional deduction for "expected tokens you did not receive"
- The MEV extraction is an economic loss but there is no ITA mechanism to deduct it as a separate line item
- **Exception — protocol exploit theft:** If a DeFi protocol exploit caused actual crypto to be stolen from your wallet (not merely a worse trade price), ITA s.39(1)(c) may allow a capital loss from theft for assets held as capital property. Document the exploit with the transaction hash, protocol announcement, and on-chain proof of the theft.

### DEX Volume and Business Income Classification

High-frequency DEX trading follows the same characterization test as centralized exchange trading (see `ATLAS_TAX_STRATEGY.md` Section 4 for the full Charania/Stewart analysis). CC's use of automated DEX strategies via ATLAS almost certainly satisfies the **Stewart commercial nature test** — business income classification, meaning:

- 100% inclusion in income (no 50% capital gains treatment)
- Full deductibility of gas fees, RPC provider fees, hardware, software, home office on T2125

---

## 10. Record-Keeping Requirements

### Timing: NOW — ITA Obligations Are Immediate and Retroactive

### CRA's Record-Keeping Obligation

**ITA s.230(1):** Every person carrying on a business or required to pay tax must keep records and books of account at their place of business or residence in Canada to allow CRA to determine their tax liability.

**CRA Guide RC4409 (Keeping Records):** Records must be retained for **6 years** from the end of the last tax year to which they relate. 2025 tax year records must be kept until at least 2031. Historical DeFi records (if you participated in 2021-2023 DeFi activity) must still be preserved.

**The critical challenge:** Blockchain transactions are permanent and publicly visible — but the **CAD FMV at each historical transaction time** is NOT permanently and easily accessible unless you preserved it contemporaneously. CoinGecko and CoinMarketCap historical data only goes back a limited time for many smaller tokens.

### Required Documentation Per Transaction

| Data Point | Why Required | How to Capture |
|-----------|--------------|----------------|
| Transaction date and time (UTC) | Determines tax year + ACB timing | Block explorer timestamp |
| Transaction hash | Audit proof — verifiable on-chain | Block explorer |
| Transaction type | Characterize the tax event (disposition, income, etc.) | Tax software categorization + manual review |
| Token quantities (in and out) | Compute gain/loss and income amounts | Exchange export + on-chain data |
| CAD FMV at transaction time | Convert all amounts to Canadian dollars | Koinly, CoinGecko historical API, CoinMarketCap |
| ACB of asset disposed | Calculate gain/loss | Cumulative ACB ledger maintained by tax software |
| Gas fees paid | Compute gas disposition gain/loss + add to acquired asset ACB | Block explorer fee data |
| Protocol or counterparty | Context for characterization under audit | Self-documented or tax software tagging |

### Blockchain Explorers by Network

| Network | Explorer | DeFi Coverage |
|---------|---------|---------------|
| Ethereum | etherscan.io | All ERC-20, Uniswap, Aave, Compound, Curve, Lido |
| Solana | solscan.io, explorer.solana.com | SOL, SPL tokens, Raydium, Orca, Marinade |
| BNB Chain | bscscan.com | BEP-20, PancakeSwap |
| Arbitrum | arbiscan.io | Arbitrum DeFi (Uniswap V3, GMX, Radiant) |
| Polygon | polygonscan.com | Polygon DeFi (QuickSwap, Aave Polygon) |
| Avalanche | snowtrace.io | AVAX, Trader Joe, Benqi |
| Bitcoin | mempool.space, blockchain.com | BTC only |

**Export method:** Most explorers allow CSV export of full transaction history by wallet address. Export at year-end (December 31) every year and archive the file.

### Recommended Tax Software (Canadian Workflow)

| Software | DeFi Support | Wealthsimple Tax Integration | Approx. Annual Cost (CAD) |
|---------|-------------|------------------------------|---------------------------|
| **Koinly** | Excellent — 350+ integrations, handles LP/staking/farming/bridges | YES — direct import | ~$200-400 |
| **CryptoTaxCalculator** | Very good — strong DEX and DeFi coverage | YES | ~$150-300 |
| **CoinTracker** | Good — major protocols | Partial | ~$150-600 |
| **TokenTax** | Good — US-focused, Canadian use is supported | Limited | ~$200-800 |

**Atlas recommended workflow for CC:**
1. Connect all wallets and exchange accounts to **Koinly**
2. Review and correct any mis-categorized DeFi transactions (Koinly flags unknowns)
3. Export the **CRA-format capital gains report** and **income report** from Koinly
4. Import into **Wealthsimple Tax** (formerly SimpleTax) for T1 filing
5. Cross-reference T2125 totals against Koinly's business income summary

### CRA's Position on Blockchain Records

CRA has confirmed in technical interpretations (accessible via ATI requests) that blockchain transaction records are acceptable as contemporaneous business records under ITA s.230. However, CRA auditors request them accompanied by:
1. CAD FMV documentation for each transaction
2. Running ACB ledger (weighted average cost method per CRA's mandatory method)
3. Summary reconciliation tying on-chain totals to T1/T2125 reported amounts

**Weighted average cost method:** Canada requires ACB calculations using the **weighted average cost** method — NOT FIFO, LIFO, or specific identification. This is confirmed in CRA Technical Interpretation 2020-0850961I7. Koinly defaults to weighted average for Canadian users.

### Wallet Segregation for Clean Record-Keeping

Segregating wallets by income character simplifies characterization arguments and audit defense:

| Wallet Purpose | Income Character | Tax Form |
|---------------|-----------------|----------|
| Cold storage (long-term BTC/ETH hold) | Capital gains | Schedule 3 |
| Active trading (ATLAS/DEX bot wallet) | Business income | T2125 |
| DeFi wallet (LP, yield farming) | Property or business income | T1 Line 12100 or T2125 |
| NFT wallet | Capital gains (collector) or business (flipper) | Schedule 3 or T2125 |

---

## 11. CRA Enforcement — DeFi Specifically

### Overall DeFi Enforcement Trajectory: ACCELERATING

This section supplements `CRA_CRYPTO_ENFORCEMENT_INTEL.md`. Cross-reference that document for the full enforcement framework (audit triggers, UPR mechanics, CARF implementation timeline, penalty calculations).

### Dapper Labs UPR — NFT Precedent (September 2025)

Federal Court order compelling Dapper Labs to disclose all Canadian users on NBA Top Shot and the Flow blockchain. Key significance:
1. CRA has the legal infrastructure and willingness to pursue DeFi and NFT platforms specifically
2. The UPR tool (ITA s.231.2) applies to any platform with Canadian users, even if the platform is foreign
3. NFT trading is an **active, funded audit priority** — not a theoretical future risk
4. CRA identified NFT traders as a distinct category of non-compliant taxpayers with high-volume unreported income

### CARF 2026 — Impact on DeFi Traceability

**CARF effective January 1, 2026; first reporting cycle 2027** (see `CRA_CRYPTO_ENFORCEMENT_INTEL.md` Section 5 for full CARF analysis).

**DeFi-specific CARF gaps:**
- Purely on-chain DeFi protocols without KYC (Uniswap direct, Aave direct protocol) are not CARF reporting entities in the current framework
- However: **on-ramps and off-ramps ARE captured** — Kraken reports CC's fiat deposits and withdrawals, and CRA knows all wallet addresses associated with CC's Kraken account
- Blockchain analytics (Chainalysis, TRM Labs — CRA has active contracts) then trace those known wallets through all on-chain DeFi interactions
- The practical effect: **all DeFi activity connected to a KYC'd exchange account is traceable**

### Blockchain Analytics Capabilities (CRA Vendor Contracts)

CRA's contracted analytics firms can:
- **Cluster wallets** belonging to the same beneficial owner based on transaction graph patterns (shared inputs, change address patterns, etc.)
- **Map all interactions** with named DeFi protocols — Uniswap, Aave, Compound, Curve, Lido, and all major protocols are fully decoded by Chainalysis
- **Estimate holdings and gains** by reconstructing token flows and applying historical price data
- **Bridge on-chain identity to real-world identity** by tracing from KYC'd exchange withdrawal addresses through DeFi protocol interactions

**Practical implication for CC:** If CC has ever withdrawn funds from Kraken to a wallet and used that wallet on any DeFi protocol, CRA has the technical capability to reconstruct all of those DeFi activities when they audit the Kraken account data.

### Privacy Coins and Mixers — Critical Risks

| Activity | CRA Risk Level | Notes |
|----------|---------------|-------|
| Tornado Cash usage | **CRITICAL** | OFAC-sanctioned since August 2022. CRA and FINTRAC both view mixer usage as a strong money laundering indicator. Automatic escalation. |
| Monero (XMR) | **HIGH** | On-chain untraceable, but CRA knows you bought via exchange. Unexplained disappearance of funds triggers audit. KYC'd exchanges that hold XMR are CARF-reportable. |
| Zcash (ZEC) shielded transactions | **HIGH** | Similar to Monero — exchange side is visible, on-chain shielded side is not. The gap is suspicious. |
| CoinJoin (Bitcoin mixer) | **HIGH** | Not OFAC-sanctioned but viewed as deliberate obfuscation. CRA treats it as a red flag for concealment. |

**Atlas position: Do not use mixers, privacy coins, or obfuscation tools for any assets that connect to the Canadian financial system. The legal and audit risk is catastrophically disproportionate to any benefit.**

### Voluntary Disclosure for Unreported DeFi Income

If CC has unreported DeFi income from prior tax years, the **Voluntary Disclosure Program (VDP)** (IC00-1R7, updated October 1, 2025) provides:

| Application Type | Interest Relief | Penalty Relief | Criminal Referral |
|-----------------|----------------|---------------|-------------------|
| **Unprompted** (before CRA contacts you on the issue) | **75% waived** | **100% waived** | **None** |
| **Prompted** (CRA already contacted you on a related matter) | **25% waived** | Up to 100% waived | None |
| **Post-audit / post-investigation** | Not eligible | Not eligible | Not eligible |

**Process for DeFi-specific VDP:**
1. Reconstruct complete transaction history using block explorers + Koinly for all open years
2. Calculate CAD FMV at each transaction date using Koinly historical price data
3. Compute income and capital gains per year
4. Engage a CPA with crypto expertise to prepare amended T1s or a formal VDP application
5. Submit with estimated tax payment to maximize relief
6. **Act before CARF data exchanges begin in 2027** — after that, disclosure is no longer truly "unprompted"

---

## 12. Key Case Law

### Amicarelli v. The Queen — 2025 TCC 185 (STAKING)

**Facts:** Taxpayer received staking rewards from Ethereum validator node operation. CRA assessed the rewards as business income at FMV on receipt. Taxpayer argued rewards should be treated as a capital receipt with nil or deferred inclusion until sold.

**Decision:** Tax Court of Canada held in favour of CRA. Staking rewards constitute income at FMV when received, not capital. The court applied two principles:

1. **Surrogatum principle:** A receipt that substitutes for income takes the character of income (established in *Schwartz v. Canada*, SCC 1996)
2. **Accretion concept:** Staking rewards represent an increase in the taxpayer's net wealth at the moment of receipt; this enrichment is income in the period it arises

**Significance for CC:**
- Definitively confirms: staking rewards = income on receipt, not on sale
- Eliminates the "zero-cost-basis + defer all tax to eventual sale" argument
- FMV-at-receipt approach is the correct and confirmed Canadian approach

### Charania v. The Queen — 2023 TCC 22 (ACTIVE CRYPTO TRADING)

**Facts:** Taxpayer purchased and sold Bitcoin and Ethereum over multiple years, treating all gains as capital gains (50% inclusion). CRA reassessed the gains as business income (100% inclusion).

**Decision:** Tax Court upheld CRA's reassessment. The frequency, volume, and systematic nature of the crypto trading constituted a business. Key factors the court weighed:
- Use of a dedicated trading platform
- Application of technical analysis
- Active position management
- Profit motive on short-term price movements (not long-term investment appreciation)

**Significance for CC:** ATLAS = dedicated trading platform + technical analysis (12 strategies) + active management + automated execution. The Charania fact pattern maps directly onto CC's situation. **Business income treatment is almost certain for ATLAS-executed trades.**

### Stewart v. Canada — 2002 SCC 46 (PROFIT MOTIVE TEST)

**Facts:** Property rental business with years of losses. CRA challenged whether a "source of income" existed under ITA s.3.

**Decision:** Supreme Court of Canada established the two-stage profit motive test:
1. Is the activity commercial in nature (pursued in a business-like manner with profit motive)?
2. If yes, it is a "source of income" — deductible expenses and taxable income both apply

**Application to DeFi:** Automated yield farming, systematic DEX trading, and structured LP management all satisfy Stewart's commercial nature test. CRA auditors apply Stewart to determine whether DeFi activity constitutes a taxable income source. For CC, ATLAS's systematic, infrastructure-backed approach almost certainly satisfies the commercial nature standard.

### CRA Technical Interpretation 2020-0850961I7 (ACB AND CRYPTO SWAPS)

Not a court case, but a formal CRA technical interpretation that carries the weight of CRA policy:

**Key confirmations:**
1. Crypto-to-crypto swaps constitute dispositions of property — every swap is taxable
2. ACB must be calculated using the **weighted average cost method** — not FIFO, not specific identification
3. Transaction fees (gas) are added to the ACB of the asset acquired and constitute a separate disposition of the fee-token paid

**Significance:** This interpretation is what CRA auditors cite when reassessing taxpayers who did not report crypto-to-crypto swaps. It has been applied consistently in every subsequent CRA enforcement action.

### Re Dapper Labs UPR — Federal Court (September 2025) (NFT ENFORCEMENT)

**Facts:** CRA applied to Federal Court under ITA s.231.2(2) for an Unnamed Persons Requirement compelling Dapper Labs to disclose all Canadian users on the NBA Top Shot and Flow blockchain platforms.

**Decision:** Federal Court granted the UPR. CRA obtained full user data including names, addresses, transaction histories, and wallet identifiers for all Canadian Dapper Labs users.

**Significance:** CRA is actively pursuing NFT platform data. The UPR mechanism works against any platform with Canadian users, regardless of where the platform is incorporated. NFT trading is a funded enforcement priority.

---

## 13. Summary Risk Table

| DeFi Activity | Tax Event Generated | CRA Income Classification | Audit Risk | ITA Reference | NOW or FUTURE |
|--------------|--------------------|-----------------------------|------------|---------------|---------------|
| Staking rewards received | Income at FMV on receipt | Property income (delegator) / Business income (validator) | MEDIUM | s.9(1), s.12(1)(c) | NOW |
| Staking reward sale/swap | Capital gain or business income | Capital (investor) / Business (trader) | LOW | s.39(1), s.40(1) | NOW |
| LP deposit (2 tokens → LP token) | Disposition of both tokens | Capital or business | MEDIUM | s.248(1), s.40(1) | NOW |
| LP fee collection | Income at FMV on receipt | Property or business income | MEDIUM-HIGH | s.9(1) | NOW |
| LP withdrawal (LP token → 2 tokens) | Disposition of LP tokens | Capital or business | MEDIUM | s.39(1) | NOW |
| Impermanent loss (unrealized, still in pool) | NOT a deductible event | N/A | N/A | No ITA mechanism | N/A |
| Yield farming governance token rewards | Income at FMV on receipt | Business income (usually) | HIGH | s.9(1), IT-334R2 | NOW |
| Auto-compound (auto-reinvest rewards) | Income + disposition per cycle | Business income | HIGH | s.9(1), s.40(1) | NOW |
| NFT purchase with crypto | Disposition of crypto used | Capital or business | HIGH | s.248(1), s.40(1) | NOW |
| NFT sale (investor/collector) | Capital gain/loss | Capital gain (Schedule 3) | HIGH | s.39(1) | NOW |
| NFT sale (active flipper) | Business income | Business income (T2125) | HIGH | s.9(1) | NOW |
| Creator NFT sale | Business income | Business income (T2125) | HIGH | s.9(1) | NOW |
| NFT royalty received | Income at FMV on receipt | Business or property income | MEDIUM | s.9(1), IT-465R | NOW |
| NFT-to-NFT swap | Disposition at FMV received | Capital or business | MEDIUM | s.69, IT-490 | NOW |
| Wrapping (ETH → WETH, BTC → WBTC) | Disposition (near-zero gain usually) | Capital | LOW-MEDIUM | s.248(1) | NOW |
| Cross-chain bridge | Disposition at FMV on bridging | Capital or business | MEDIUM | s.248(1) | NOW |
| DAO governance token receipt (airdrop) | Income at FMV when claimable | Property or business income | HIGH | s.9(1), IT-334R2 | NOW |
| DAO contributor payment (crypto) | Business income at FMV | Business income (T2125) | MEDIUM | s.9(1) | NOW |
| DAO treasury distribution | Income at FMV on receipt | Property income | MEDIUM | s.9(1) | NOW |
| Airdrop (promotional / retroactive) | Income at FMV when claimable | Business or property income | HIGH | s.9(1), IT-334R2 | NOW |
| Hard fork (new token receipt) | Income at FMV when available | Property income | MEDIUM | CRA Crypto Guide 2023 | NOW |
| DeFi lending interest (Aave/Compound) | Income when accrued | Property income (s.12(3) accrual) | MEDIUM | s.12(1)(c), s.12(3) | NOW |
| Crypto collateral deposit (no receipt token) | NOT a disposition | N/A | LOW | s.248(1) negative | NOW |
| Borrowing against crypto collateral | NOT taxable income | Loan liability | LOW | ITA general loan principles | NOW |
| Liquidation of collateral by protocol | Disposition at liquidation FMV | Capital or business | MEDIUM-HIGH | s.248(1), s.40(1) | NOW |
| Flash loan arbitrage profit | Business income | Business income (T2125) | MEDIUM | s.9(1) | NOW |
| DEX token swap | Disposition + acquisition | Capital or business (per characterization) | MEDIUM-HIGH | s.39(1), s.40(1), 2020-0850961I7 | NOW |
| Gas fee paid (as part of swap/TX) | Disposition of gas token | Capital or business | LOW | s.248(1), s.54 | NOW |
| MEV sandwich attack (worse trade price) | Proceeds = actual received; no additional loss | N/A | LOW | General ITA principles | N/A |
| Protocol exploit / theft capital loss | Capital loss if held as capital property | Capital loss (Schedule 3) | MEDIUM | s.39(1)(c) | NOW |
| Mixer / Tornado Cash usage | Disposition + FINTRAC violation | Audit trigger and possible s.239 exposure | CRITICAL | ITA s.239, PCMLTFA | NEVER |

---

## 14. Action Items for CC

| Priority | Action | Deadline |
|---------|--------|----------|
| **P1** | Connect all DeFi wallets to Koinly — cover Ethereum, Solana, and any other chains used | Before June 15, 2026 (T1 filing deadline) |
| **P1** | Run Koinly transaction review — manually correct any mis-categorized DeFi transactions (swaps tagged as transfers, LP deposits not recognized, etc.) | Before filing |
| **P1** | Export Koinly CRA capital gains report and income report; reconcile against T2125 and Schedule 3 totals | Before filing |
| **P2** | Review 2023 and 2024 returns for any unreported staking, LP fee, yield farming, or airdrop income | Before June 15, 2026 |
| **P2** | Segregate wallets going forward — separate wallets for long-term holding, ATLAS trading, DeFi/LP activity, and NFTs | Immediately |
| **P2** | Document intent for each wallet (brief written policy statement: "This wallet holds long-term investment ETH acquired for appreciation, not short-term trading") | Now |
| **P3** | Evaluate whether any prior years require VDP amendment — unprompted VDP available until CRA contacts you | Before CARF data exchanges begin in 2027 |
| **P3** | Archive annual CSV exports from all block explorers for all wallets every December 31 | Ongoing |

---

*Document prepared by ATLAS — CC's CFO Agent. This document is a reference for planning and tax preparation. For positions with material tax consequences, engage a CPA with Canadian crypto tax expertise before filing. ATLAS prepares, calculates, and advises — CC reviews, confirms, and files via NETFILE. CC is responsible for the accuracy of the T1 return.*

*ITA = Income Tax Act (Canada), R.S.C. 1985, c. 1 (5th Supp.) | Last reviewed: 2026-03-27*
