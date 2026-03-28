# ATLAS Options, Derivatives & Structured Products Tax Guide v1.0

> **Compiled by:** ATLAS (CC's CFO Agent)
> **Date:** 2026-03-27
> **Scope:** Complete Canadian tax treatment of options, futures, CFDs, structured products, and derivative-based tax planning strategies
> **Jurisdiction:** Canada (Ontario) | **Taxpayer profile:** Sole proprietor, 22, dual citizen (CA/UK), active crypto/gold trader, projected $280K-$480K+ CAD 2026
> **Authority:** Income Tax Act (ITA), CRA interpretation bulletins/folios, Tax Court of Canada decisions
> **Supplements:** `ATLAS_TAX_STRATEGY.md` (main playbook), `ATLAS_DEFI_TAX_GUIDE.md` (crypto), `ATLAS_WEALTH_PLAYBOOK.md` (Buy/Borrow/Die), `ATLAS_ALTERNATIVE_INVESTMENTS.md` (exempt market)

---

## Legend

| Tag | Meaning |
|-----|---------|
| `[NOW]` | CC can execute today at current income/asset level |
| `[FUTURE: trigger]` | Execute when trigger condition is met |
| `[LOW RISK]` | CRA audit risk minimal — well-established treatment |
| `[MEDIUM RISK]` | Legitimate strategy, may attract compliance review |
| `[HIGH RISK]` | Legal but CRA actively scrutinizes this category |
| `[EXTREME RISK]` | CRA challenges are routine — CPA + full documentation mandatory |

---

## Table of Contents

1. [Employee Stock Options (s.7 ITA)](#1-employee-stock-options-s7-ita)
2. [Listed Options — Calls and Puts](#2-listed-options--calls-and-puts)
3. [Futures and Forwards](#3-futures-and-forwards)
4. [CFDs and Spread Betting](#4-cfds-and-spread-betting)
5. [Structured Products](#5-structured-products)
6. [Derivatives in Registered Accounts](#6-derivatives-in-registered-accounts)
7. [Hedging vs Speculation](#7-hedging-vs-speculation)
8. [Straddles, Spreads, and Complex Strategies](#8-straddles-spreads-and-complex-strategies)
9. [Derivatives for Tax Planning](#9-derivatives-for-tax-planning)
10. [Cross-Border Derivatives](#10-cross-border-derivatives)
11. [CC-Specific Strategies](#11-cc-specific-strategies)
12. [Key Case Law](#12-key-case-law)
13. [Priority Action Matrix](#13-priority-action-matrix)

---

## 1. Employee Stock Options (s.7 ITA)

### Audit Risk: LOW (well-legislated) | Relevance: FUTURE (CC as employer or employee of own CCPC)

### 1.1 The Basic Framework

Employee stock options in Canada are governed by **ITA s.7** — one of the most complex provisions in the entire Act. The tax treatment depends on three variables:

1. **Is the employer a CCPC?** (Canadian-Controlled Private Corporation)
2. **What was the exercise price relative to FMV at grant?**
3. **When did the employee dispose of the shares?**

### 1.2 CCPC Stock Options — The Gold Standard

**ITA s.7(1.1):** When a CCPC grants options to an employee, **NO taxable benefit arises at exercise**. The benefit is deferred until the employee **disposes of the shares**.

**Why this matters for CC:**
When OASIS incorporates as a CCPC (trigger: $80K+ sustained revenue), CC can grant himself stock options at the current FMV. If the company grows from a $100K valuation to $5M, CC pays zero tax until he actually sells the shares.

**The mechanics:**

| Event | Tax Consequence | ITA Reference |
|-------|----------------|---------------|
| Option granted | Nothing — no tax event | s.7(1.1) |
| Option exercised (shares acquired) | Nothing — deferred for CCPC | s.7(1.1) |
| Shares disposed of | Employment benefit = FMV at exercise minus exercise price | s.7(1)(a) |
| 50% deduction available? | Yes, if exercise price >= FMV at grant date | s.110(1)(d) |
| Capital gain on subsequent appreciation? | Yes — gain above FMV at exercise is capital gains | s.7(1.1), s.38 |

**Example — CC's CCPC Options:**

```
2027: OASIS incorporates. CC grants himself 100,000 options at $1.00/share (FMV at incorporation).
2030: OASIS valued at $10/share. CC exercises all options, paying $100,000 for shares worth $1,000,000.
2030: CC holds the shares — NO TAX yet (CCPC deferral).
2032: CC sells shares for $15/share ($1,500,000 total).

Employment benefit: ($10 - $1) x 100,000 = $900,000
50% deduction (s.110(1)(d)): $450,000
Taxable employment income: $450,000
Effective rate on benefit: ~26.76% (half the marginal rate)

Capital gain: ($15 - $10) x 100,000 = $500,000
Taxable capital gain (50% inclusion): $250,000

Total taxable: $700,000 on $1,400,000 of economic gain
Effective rate: ~25% vs 53.53% marginal rate
```

### 1.3 Budget 2024 — The $200K Annual Vesting Cap

**Critical change effective June 25, 2024:** The 50% stock option deduction under s.110(1)(d) is now subject to a **$200,000 annual vesting limit** for non-CCPC (public company) stock options.

**How the cap works:**
- Only the first $200,000 (based on FMV at grant) of stock options vesting in a calendar year qualify for the 50% deduction
- Amounts above $200,000 are taxed as **regular employment income** at full rates
- **CCPC options are EXEMPT from the $200K cap** — another reason CCPC status is valuable

**CC impact:** When OASIS is a CCPC, this cap does not apply. If OASIS goes public or is acquired by a non-CCPC, options vesting above $200K/year lose the 50% deduction.

### 1.4 Non-CCPC / Public Company Options

For public companies or non-CCPCs:

| Event | Tax Consequence |
|-------|----------------|
| Option granted | Nothing |
| Option exercised | Employment benefit = FMV at exercise - exercise price. **Taxed immediately.** |
| 50% deduction? | Only if exercise price >= FMV at grant AND $200K annual cap not exceeded |
| Shares sold later | Capital gain/loss from FMV at exercise |

**The AMT trap:** Even with the 50% deduction, the **full** stock option benefit (before deduction) is added back for Alternative Minimum Tax (AMT) purposes under s.127.52(1)(h). At $280K+ income, CC could trigger AMT on large option exercises. AMT rate is 20.5% federal on adjusted taxable income exceeding $173,205 (2026 indexed).

**Mitigation:** Exercise options in tranches across multiple tax years. Never exercise more than $400K-$500K of benefit in a single year without AMT modeling.

### 1.5 Capital Gains vs Employment Income — When Each Applies

| Scenario | Character | Why |
|----------|-----------|-----|
| Employee exercises option, sells shares | Employment income (option benefit) + capital gain (subsequent appreciation) | s.7(1)(a) + s.38 |
| Employee sells the option itself (transfers it) | Employment benefit at time of transfer | s.7(1)(b) |
| Non-employee option (e.g., consultant) | Capital gain on disposition of option | Not s.7 — general principles |
| Option expires unexercised | No tax consequence for the holder | Nothing to tax |

**Key distinction:** If CC receives options as a **contractor** (not employee), s.7 does not apply. The option is property, and gains on disposition are capital gains. This is actually better tax treatment in many cases — worth structuring carefully.

`[FUTURE: CCPC incorporation]` Grant yourself CCPC options at incorporation. Maximum deferral + 50% deduction = effective rate ~26% on option benefit vs 53.53% marginal rate. Worth $120K+ in tax savings on a $1M+ exit.

---

## 2. Listed Options — Calls and Puts

### Audit Risk: LOW-MEDIUM (depends on trading frequency) | Relevance: NOW

### 2.1 Buying Calls

When you buy a call option and later sell it (or it expires), the tax treatment is straightforward:

**Profitable sale:**
- Proceeds of disposition = sale price of the option
- ACB = purchase price (premium paid) + commissions
- Gain = proceeds - ACB
- Character: **Capital gain** (if not a business) or **business income** (if trader)

**Expiry worthless:**
- Capital loss = premium paid + commissions (your ACB, with $0 proceeds)
- Deductible against capital gains only (50% inclusion)

**Exercise the call (you buy the underlying):**
- The call option premium is **added to the ACB of the acquired shares**
- No separate gain/loss on the option itself — it merges into the share cost
- ITA s.49(1): option premium becomes part of ACB on exercise

**Example:**
```
CC buys 1 BTC call option on CME (via IBKR) for $2,000 CAD premium.
Strike: $90,000 USD. BTC rises to $110,000 USD.

Scenario A — Sell the option for $8,000:
  Capital gain = $8,000 - $2,000 = $6,000
  Taxable (50% inclusion) = $3,000

Scenario B — Exercise the option:
  ACB of the BTC = $90,000 USD + $2,000 premium + commissions
  No immediate tax — recognized when BTC is sold

Scenario C — Option expires worthless:
  Capital loss = $2,000
  Can offset against other capital gains
```

### 2.2 Buying Puts

Identical treatment to calls, but with the mirror-image economic position:

- **Sell the put for profit:** Capital gain = sale price - premium paid
- **Put expires worthless:** Capital loss = premium paid
- **Exercise the put (you sell the underlying):** The put premium **reduces your proceeds of disposition** on the underlying — ITA s.49(1)

**Example:**
```
CC buys a protective put on BITX (2x Bitcoin ETF) for $500 premium.
Strike: $50. BITX drops to $30. CC exercises.

Proceeds of disposition of BITX shares: $50/share (strike price)
MINUS put premium: $500
Net proceeds: ($50 x 100 shares) - $500 = $4,500
Capital gain/loss = $4,500 - ACB of BITX shares
```

### 2.3 Writing (Selling) Covered Calls

**This is the most tax-efficient options strategy for CC.** `[NOW]`

When you write a covered call (sell a call against shares you own):

**If the call expires worthless:**
- The premium received is a **capital gain** — ITA s.49(1)
- No employment income, no business income (assuming capital account)
- You keep your shares + the premium

**If the call is assigned (buyer exercises):**
- The premium is **added to your proceeds of disposition** of the underlying shares
- You sell the shares at strike price + premium received
- Character: Capital gain (the entire transaction)

**If you buy back the call to close:**
- Capital gain/loss = premium received - buyback price

**Example — Covered Call on BTCC (Bitcoin ETF) in TFSA:**
```
CC owns 500 shares of BTCC in TFSA at $12/share.
Writes 5 covered call contracts (100 shares each) at $14 strike, receives $1.00/share premium.
Total premium: $500

Scenario A — BTCC stays below $14, call expires:
  $500 is TAX-FREE (capital gain inside TFSA)
  CC keeps shares + $500

Scenario B — BTCC rises to $16, call assigned:
  CC sells 500 shares at $14 + $1 premium = $15 effective
  All TAX-FREE inside TFSA
  Missed upside above $14 but collected premium

Scenario C — CC buys back the call at $2.50 before expiry:
  Loss = $2.50 - $1.00 = $1.50/share = $750 loss
  In TFSA: no tax consequence either way
```

### 2.4 Writing (Selling) Naked/Cash-Secured Puts

When you write a put:

**If the put expires worthless:**
- Premium received is a **capital gain** — s.49(1)

**If the put is assigned (you're forced to buy):**
- Premium received **reduces the ACB** of the shares you acquire
- ACB = strike price - premium received

**If you buy back to close:**
- Capital gain/loss = premium received - buyback price

### 2.5 Assignment and Exercise — ACB Adjustments

The critical rule: **options that are exercised do not generate a standalone gain or loss**. The premium flows into the ACB or proceeds of the underlying transaction.

| Party | Call Exercised | Put Exercised |
|-------|---------------|---------------|
| **Buyer** | Premium → added to ACB of shares acquired | Premium → reduces proceeds on shares sold |
| **Writer** | Premium → added to proceeds of shares sold | Premium → reduces ACB of shares acquired |

### 2.6 CRA Business Income Characterization — The Day Trading Trap

**This is CC's biggest risk with options trading.** `[HIGH RISK]`

CRA uses the same factors for options as for stock/crypto trading to determine business vs. capital:

| Factor | Capital (50% inclusion) | Business (100% inclusion) |
|--------|------------------------|--------------------------|
| Holding period | Weeks to months | Hours to days |
| Frequency | Occasional | Daily/weekly |
| Knowledge | Basic | Sophisticated (ATLAS = red flag) |
| Time spent | Minimal | Significant |
| Leverage | None or modest | Heavy |
| Intent | Investment return | Quick profit |
| Financing | Own funds | Margin/borrowed |

**CC's risk factors:**
- ATLAS automated trading system = "sophisticated knowledge + significant time"
- Kraken/OANDA active trading = "high frequency"
- 12 strategies running = "business-like operations"

**Mitigation:**
1. **Separate accounts** — Long-term options positions (covered calls on ETFs, LEAPS) in a separate account from active trading
2. **Hold for 30+ days** where possible — shorter holding periods = stronger business income argument
3. **Document investment intent** at the time of purchase (journal entries)
4. **In registered accounts (TFSA/RRSP), character doesn't matter** — all tax-free/deferred anyway

---

## 3. Futures and Forwards

### Audit Risk: MEDIUM | Relevance: NOW (Kraken crypto futures, OANDA forex)

### 3.1 Tax Character — Capital vs Business Income

Canada does NOT have a blanket mark-to-market rule for futures like the US (s.1256 contracts). The character of futures gains/losses depends on the **same capital vs business income analysis** as other securities.

**General rule:** Futures traded speculatively by an individual are **capital gains/losses** unless the trading activity rises to the level of a business.

**Exception — hedging:** If futures are used to hedge a business risk (e.g., a gold miner hedging production, a farmer hedging crop prices), gains and losses are **business income/loss** matching the character of the underlying business activity. See [Section 7 — Hedging vs Speculation](#7-hedging-vs-speculation).

### 3.2 Timing of Recognition

| Instrument | When Taxed | Rule |
|------------|-----------|------|
| Exchange-traded futures (CME, etc.) | On close, settlement, or expiry | Disposition of property |
| Mark-to-market (daily settlement) | Each settlement is a partial disposition | Cash received/paid is gain/loss |
| Forward contracts (OTC) | On settlement or close-out | Disposition at maturity |
| Physically-settled futures | On delivery — cost of property acquired | ACB = futures price + commissions |

**Key insight for Kraken crypto futures:** Kraken perpetual futures settle in crypto (e.g., BTC). Each funding payment and each position close is a **separate disposition** for Canadian tax purposes. The FMV in CAD at the moment of each settlement determines the gain or loss.

### 3.3 Crypto Futures on Kraken — Specific Treatment

CC trades crypto futures on Kraken. Here is the tax flow: `[NOW]`

**Opening a long BTC futures position:**
- Not a taxable event (entering a contract, not acquiring property)
- Margin deposit is NOT a disposition

**Daily funding payments (perpetual futures):**
- If you pay funding: This reduces your eventual gain or increases your loss
- If you receive funding: This is income (business or capital depending on overall characterization)
- CRA has not issued specific guidance on perpetual futures funding — treat as part of the position P&L

**Closing the position:**
- Gain or loss = closing price - opening price, adjusted for all funding payments, in CAD at date of each component
- Character: Capital gain/loss (if not business income)

**Liquidation:**
- Same as closing — forced closure is still a disposition
- The loss is deductible

**Example:**
```
CC opens a 3x leveraged BTC long at $90,000 USD with $5,000 margin.
Position size: $15,000 notional.
Over 2 weeks, pays $45 in funding fees.
Closes at $95,000 USD.

Gain: ($95,000 - $90,000) / $90,000 x $15,000 = $833.33 USD
Less funding: $833.33 - $45 = $788.33 USD
Convert to CAD at closing date rate (assume 1.37): $1,080.01 CAD
Taxable capital gain (50%): $540.01 CAD
Tax at marginal rate (~43%): $232.20 CAD

If business income: $1,080.01 x 43% = $464.40 CAD
Business income costs $232 more in tax on this single trade.
```

### 3.4 Forex Forwards and Swaps — s.39(2)

**ITA s.39(2)** provides a special rule for foreign currency gains and losses:

- The first **$200 of net foreign currency gains** in a tax year is **exempt** from tax
- Foreign currency gains/losses from the disposition of foreign currency are **capital** in nature (s.39(2) treats them as deemed capital gains/losses)
- This applies to the currency component only, not the underlying asset

**OANDA forex implications:** `[NOW]`
- OANDA positions are CFDs (see Section 4), but forex gains/losses on currency conversion still engage s.39(2)
- If CC's OANDA account is in USD, converting to/from CAD triggers s.39(2) on the currency component
- The $200 exemption is per-taxpayer-per-year — minor benefit

**Forex swaps/rollovers:** OANDA charges overnight swap (rollover) fees on open positions. These are either:
- Part of the cost of the position (reducing gain or increasing loss), OR
- Interest expense (deductible under s.20(1)(c) if borrowed money is used for income-producing purposes)

The better position for CC is to treat swap fees as interest expense under s.20(1)(c) — this is deductible against ALL income, not just capital gains. Document the position and apply consistently.

### 3.5 Forward Rate Agreements and Interest Rate Derivatives

**Relevance: FUTURE** — but worth knowing for CCPC treasury management.

Interest rate swaps and forward rate agreements are generally treated as **income** (not capital) because they relate to interest obligations. For a CCPC, this means:
- Gains on interest rate hedges = investment income (subject to Part IV tax refundable regime)
- Losses = deductible against investment income

---

## 4. CFDs and Spread Betting

### Audit Risk: LOW-MEDIUM | Relevance: NOW (OANDA gold positions)

### 4.1 CRA Position on CFDs

A Contract for Difference (CFD) is a derivative contract where you profit/lose based on the price movement of an underlying asset without ever owning it. **CC's OANDA gold and forex positions are CFDs.**

**CRA's treatment:**
- CFDs are treated as **property** under ITA s.248(1)
- Gains/losses on closing a CFD position are **capital gains/losses** (if not business income)
- Opening a CFD is entering a contract — not a disposition
- Closing a CFD is a disposition of property
- Margin deposits are not taxable events

**No special CFD legislation exists in Canada** — the CRA applies general principles. This is actually favorable because it avoids the "income from property" classification that some other jurisdictions impose.

### 4.2 OANDA Positions as CFDs — CC's Treatment `[NOW]`

CC trades gold (XAU/USD) on OANDA. Each position has this tax flow:

**Opening:** Not taxable. Margin posted is a deposit, not a disposition.

**Swap/rollover fees:** Deductible as:
- Interest expense under s.20(1)(c) (preferred — deductible against all income), OR
- Cost of the position (reduces gain, increases loss — only offsets capital gains)

**Closing the position:**
- Capital gain = closing value - opening value - swap fees (if treated as cost)
- Convert USD amounts to CAD at the exchange rate on the date of each component

**Example — OANDA Gold Trade:**
```
CC opens a 0.5 lot XAU/USD long at $2,300/oz. Held for 10 days.
Position value: 0.5 x 100 oz x $2,300 = $115,000 USD notional
Swap fees paid: $12.50 USD
Close at $2,380/oz.

Gain: ($2,380 - $2,300) x 50 oz = $4,000 USD
Less swap: $4,000 - $12.50 = $3,987.50 USD
CAD at 1.37: $5,462.88 CAD
Capital gain (50%): $2,731.44 CAD
Tax (~43%): $1,174.52 CAD
```

### 4.3 UK Spread Betting — The Dual Citizen Angle

**This is one of the most interesting tax arbitrage opportunities for CC.** `[FUTURE: UK residence]`

In the UK, spread betting is classified as **gambling** and is **completely tax-free** — no capital gains tax, no income tax, no reporting requirement. This is codified in HMRC practice and confirmed in multiple tribunal decisions.

**The catch for CC as a Canadian resident:**
Canada taxes residents on **worldwide income** regardless of where it's earned or how it's characterized in the source country. UK spread betting profits earned by a Canadian tax resident are taxable in Canada as:
- **Capital gains** (if occasional/investment-oriented), or
- **Business income** (if frequent/systematic)

**The UK does not issue any tax reporting documents for spread betting gains.** The CRA would only know about them if:
1. CC self-reports (legally required)
2. CRA obtains information through a treaty exchange (FATCA/CRS don't cover spread betting accounts by default, but specific requests under the Canada-UK treaty are possible)

**The legal optimization:**
If CC moves to the UK or a Crown Dependency (Isle of Man — 0% CGT), spread betting becomes genuinely tax-free:
- UK residence = HMRC tax rules apply = spread betting is tax-free gambling
- No Canadian taxation (after ceasing Canadian residency and paying departure tax)
- Isle of Man: same treatment as UK for spread betting + 0% CGT on everything else

`[FUTURE: UK/IOM residence]` Spread betting on IG, CMC Markets, or City Index — completely tax-free on all derivatives gains. This alone could save $50K-$100K+/year at CC's projected income levels.

### 4.4 CFD vs Futures vs Options — Tax Comparison (Canada)

| Feature | CFD | Futures | Listed Options | Spread Bet (UK) |
|---------|-----|---------|---------------|-----------------|
| Tax character (Canada) | Capital gain (usually) | Capital gain (usually) | Capital gain (usually) | Capital gain if Canadian resident |
| Mark-to-market | No | Daily settlement = partial dispositions | No | N/A (UK: tax-free) |
| Loss deductibility | Capital losses only | Capital losses only | Capital losses only | Capital losses only (Canada) |
| Swap/rollover fees | Deductible (s.20(1)(c)) | Built into price | Time decay (premium) | Included in spread |
| Registered account eligible? | No (not qualified investment) | Some (CME futures ETFs) | Yes (covered calls, long options) | No |
| CRA reporting complexity | Medium | High (daily settlements) | Medium | Low (self-report) |

---

## 5. Structured Products

### Audit Risk: LOW-MEDIUM | Relevance: FUTURE (requires higher capital base)

### 5.1 Principal-Protected Notes (PPNs)

PPNs guarantee return of principal at maturity while providing upside linked to an index, commodity, or basket.

**Tax treatment — IT-483R (archived but still referenced by CRA):**
- The return of principal component is NOT income
- Any return above principal is taxed as **interest income** (not capital gains)
- This is true even if the return is linked to equity performance
- Reason: CRA treats the implicit guarantee as a debt obligation, and returns on debt = interest

**Why this matters:** PPNs look attractive (guaranteed principal!) but are tax-**in**efficient. A $100K PPN that returns $120K generates $20K of **interest income** (100% taxable at up to 53.53%). The same $20K as a capital gain would be taxed at $10K x 53.53% = $5,353 vs $10,706 for interest.

`[FUTURE: $100K+ investable]` Avoid PPNs unless the guaranteed principal is essential for risk management. Better to invest directly in the underlying index + hold cash/GICs separately.

### 5.2 Linked Notes (Equity-Linked, Commodity-Linked)

Linked notes without principal protection have more favorable treatment:

- If structured as a debt instrument with an equity-linked return: **interest income**
- If structured as a forward contract on the underlying: **capital gains**
- The structure matters enormously — review the prospectus or term sheet

**CRA Interpretation Bulletin IT-479R:** Transactions in securities — applies to determine character of complex structured product gains.

### 5.3 ETF Options — Covered Calls on ETFs `[NOW]`

This is the bread and butter for CC's TFSA and future non-registered portfolio.

**Covered call ETFs (BTCC, QYLD, XYLD, JEPI, etc.):**
- These ETFs write covered calls internally and distribute the premium income
- Distributions are typically a mix of: return of capital (ROC), capital gains, and "other income"
- ROC reduces your ACB — not immediately taxable but increases eventual capital gain
- In a TFSA: All distributions are tax-free regardless of character

**Writing your own covered calls on ETF holdings:**
- Identical treatment to covered calls on individual stocks (Section 2.3)
- Premium received = capital gain if it expires; added to proceeds if assigned
- In TFSA: completely tax-free

**Can you write covered calls in a TFSA?** YES — as long as:
1. You own the underlying shares (covered, not naked)
2. The ETF is a qualified investment (most Canadian-listed and major US-listed ETFs qualify)
3. You're not writing calls on a non-qualified or prohibited investment

### 5.4 Leveraged ETFs — Tax Drag and Distribution Character

**Leveraged ETFs (2x, 3x, inverse)** like BITX (2x Bitcoin), TQQQ (3x NASDAQ), SOXL (3x Semiconductors):

**Tax issues:**
1. **Daily rebalancing** creates internal capital gains/losses that flow through as distributions
2. **Distributions are often 100% capital gains** (not ROC or dividends)
3. **Volatility decay** erodes value over time — the ETF loses money even if the underlying is flat
4. **Phantom distributions** — some leveraged ETFs distribute large capital gains in December even if the ETF price dropped during the year

**In registered accounts (TFSA/RRSP):** Leveraged ETFs are **qualified investments** and can be held. All the tax drag disappears inside registered accounts, making TFSA the **ideal vehicle** for leveraged ETFs.

**In non-registered accounts:** Avoid holding leveraged ETFs long-term. The tax drag from distributions + volatility decay makes them strictly inferior to unleveraged + margin.

`[NOW]` Hold BITX or leveraged crypto/equity ETFs in TFSA only. In non-registered, use margin on unleveraged ETFs instead.

### 5.5 PFIC Warning — US-Listed ETFs with Options

If CC holds US-listed ETFs (not Canadian-listed), they may be classified as **Passive Foreign Investment Companies (PFICs)** by the IRS. While CC is not a US taxpayer, PFIC status can complicate cross-border planning if CC ever becomes US tax resident.

More importantly for now: **US-listed ETFs held by Canadian residents face 15% US withholding tax on dividends** (reduced from 30% by the Canada-US treaty). This withholding applies even in an RRSP (though RRSP is exempt from the 15% under Article XVIII of the treaty) but NOT in a TFSA (TFSA is not recognized as a retirement account by the US — full 15% withholding applies).

`[NOW]` For dividend-paying US ETFs: hold in RRSP (0% withholding) > non-registered (15% withholding, FTC claimable) > TFSA (15% withholding, no FTC available).

---

## 6. Derivatives in Registered Accounts

### Audit Risk: HIGH if rules violated (100% penalty tax) | Relevance: NOW

### 6.1 TFSA — What Derivative Strategies Are Allowed

The TFSA is governed by ITA s.146.2. Only **qualified investments** (defined in s.204 and s.207.01(1)) can be held.

**Allowed in TFSA:**

| Strategy | Allowed? | Condition |
|----------|----------|-----------|
| Covered calls | YES | Must own the underlying shares in the same TFSA |
| Long calls | YES | Listed on a designated exchange |
| Long puts | YES | Listed on a designated exchange |
| Cash-secured puts | COMPLEX | CRA has not explicitly prohibited, but some trustees restrict it |
| Naked (uncovered) calls | NO | Creates an obligation beyond account value — prohibited |
| Naked puts | RESTRICTED | Most TFSA trustees prohibit; technically a qualified investment if listed but practically blocked |
| Leveraged ETFs | YES | Qualified investment if listed on a designated exchange |
| Crypto ETFs (BTCC, EBIT, etc.) | YES | Canadian-listed = qualified investment |
| US-listed options | YES | Listed on a designated exchange (CBOE, NYSE Arca, etc.) |
| Futures contracts | NO | Not a qualified investment (with narrow exceptions for certain futures-based ETFs) |
| CFDs | NO | Not a qualified investment |
| Spread betting | NO | Not a qualified investment |
| Warrants | YES | If listed on a designated exchange |

### 6.2 RRSP — Same Restrictions, Different Consequences

RRSP rules for derivatives are nearly identical to TFSA. The key differences:

- **Same qualified investment rules** apply (s.204)
- **Overcontribution penalty:** 1% per month on excess (vs TFSA's 1% per month on overcontribution + 100% on non-qualified)
- **RRSP advantage:** US withholding tax is 0% under the Canada-US treaty (vs 15% in TFSA)
- **Covered calls in RRSP:** Allowed and tax-efficient — premium income grows tax-deferred

### 6.3 Qualified Investment Rules for Derivatives

**ITA s.204 "Qualified Investment"** for registered plans includes:

1. Securities listed on a **designated stock exchange** (TSX, NYSE, NASDAQ, CBOE, etc.)
2. This includes listed options on those exchanges
3. Units of mutual fund trusts and mutual fund corporations
4. GICs, government bonds, corporate bonds rated investment grade
5. **Specifically excludes:** OTC derivatives, CFDs, futures (directly), private company shares (unless meet specific exemptions), cryptocurrency held directly

**Crypto in registered accounts:**
- Direct crypto (BTC, ETH) is **NOT a qualified investment** for TFSA/RRSP
- Crypto ETFs (BTCC, EBIT, BTCX) listed on TSX **ARE qualified investments**
- Options on crypto ETFs: qualified if the option is listed on a designated exchange

### 6.4 Prohibited Investment Rules — The 100% Penalty

**ITA s.207.04:** If a TFSA or RRSP holds a **prohibited investment**, the holder owes:
- **100% tax** on the income earned from that investment
- **50% tax** on the FMV of the prohibited investment at acquisition (refundable if corrected within the year)

**What's a prohibited investment?**
- Shares/debt of a corporation where the TFSA holder has a **significant interest** (generally 10%+ ownership)
- Property with which the TFSA holder does not deal at arm's length

**CC's risk:** When OASIS incorporates and CC holds 100% of the shares, those shares are a **prohibited investment** for CC's TFSA and RRSP. CC cannot:
- Hold OASIS shares in his TFSA
- Write covered calls on OASIS shares through his TFSA
- Use TFSA funds to invest in OASIS convertible notes

This is a hard rule. Violation = 50% penalty tax + 100% tax on income.

`[NOW]` Never put your own company's shares or derivatives in your registered accounts. Use registered accounts exclusively for arm's-length public market investments.

### 6.5 Advantage Rules — The TFSA Day Trading Trap

**ITA s.207.01(1) "advantage"** and **s.207.05:** If the CRA determines that a TFSA has earned an **"advantage"** — meaning the growth is attributable to the holder's specialized knowledge, insider information, or deliberate tax-avoidance transactions rather than normal investment returns — the CRA can impose a **100% tax on the advantage amount**.

**Real-world enforcement:** The CRA has successfully assessed TFSA holders who grew accounts from $5,000 to $500,000+ through active day trading, arguing the profits were an "advantage" from the holder's professional trading activity.

**CC's risk level:** MODERATE. If CC uses ATLAS strategies inside a TFSA to generate outsized returns, the CRA could argue the returns are an "advantage." Mitigation:
1. Use only simple strategies in TFSA (buy-and-hold + covered calls)
2. Do NOT run automated trading bots on TFSA positions
3. Keep active/algorithmic trading in non-registered accounts
4. Reasonable TFSA growth (20-30%/year) is unlikely to trigger scrutiny. 500%+ growth will.

---

## 7. Hedging vs Speculation

### Audit Risk: MEDIUM (hedging characterization is fact-specific) | Relevance: NOW-FUTURE

### 7.1 CRA Hedge Characterization

The distinction between hedging and speculation determines whether derivative gains/losses are **business income** (matching the hedged item) or **capital gains** (standalone investment):

**CRA's position (S3-F9-C1, formerly IT-346R):**
A transaction is a hedge if:
1. There is an identifiable risk being hedged (price risk, currency risk, interest rate risk)
2. The derivative is **directly linked** to the risk exposure
3. The hedge is **designated** as such at inception (documentation!)
4. The hedge is **effective** — the derivative and hedged item move in opposite directions

**If it's a hedge:** Gains/losses take the character of the hedged item
- Hedging business inventory = business income/loss
- Hedging a capital investment = capital gain/loss
- Hedging future business revenue (e.g., forex on expected USD receivables) = business income/loss

**If it's speculation:** General capital vs business income analysis applies (Section 2.6)

### 7.2 Using Options to Hedge Existing Positions `[NOW]`

**Protective puts on crypto holdings:**
CC holds BTC on Kraken. Buying a put option on a Bitcoin ETF (e.g., BITO puts on CBOE) creates a synthetic hedge:
- If BTC drops, the put gains value, offsetting the loss
- The put premium is a cost of the hedge
- Tax treatment depends on whether the hedge is linked to a capital asset (likely, for CC's BTC holdings)

**Covered calls for income on existing positions:**
Writing calls against existing crypto ETF holdings generates premium income:
- Character: Capital gain (on expiry) or adjustment to proceeds (on assignment)
- Hedging characterization: The covered call is a partial hedge (limits upside, provides income buffer)

**Collar strategy (buy put + sell call):**
- Locks in a price range on the underlying
- Net premium: If put costs $3 and call pays $2, net cost is $1
- Tax treatment: Both legs are capital transactions if the underlying is on capital account
- **Major benefit:** Defers the capital gains recognition — you haven't sold the asset, just locked in the range

### 7.3 Collar Strategy for Tax-Deferred Monetization `[FUTURE: large unrealized gains]`

The collar is a variant of the **Buy/Borrow/Die** strategy (see `ATLAS_WEALTH_PLAYBOOK.md`):

```
Step 1: CC holds $500K of appreciated BTC (ACB: $100K, unrealized gain: $400K)
Step 2: Buy a protective put at $480K (95% of value)
Step 3: Write a covered call at $525K (105% of value)
Step 4: Net cost: ~$0 (put cost offset by call premium — "costless collar")
Step 5: Borrow against the collared position (bank sees minimal risk)
Step 6: Use borrowed funds to invest/spend — NO capital gains triggered

Result: CC has $450K+ in cash from the loan, BTC hasn't been sold,
capital gains tax of ~$106K (at 53.53% marginal on $200K taxable gain) is DEFERRED.
```

**CRA risk:** The CRA could argue the collar + loan is a **synthetic disposition** under the general anti-avoidance rule (GAAR, s.245). However:
- No specific anti-avoidance rule targets collars in the ITA
- The taxpayer retains legal ownership and some residual risk (between put and call strikes)
- GAAR would require the CRA to prove the "primary purpose" was tax avoidance
- Major Canadian institutions (RBC, BMO) offer collar programs — CRA hasn't challenged them at scale

### 7.4 Protective Puts — Are They Deductible?

**As insurance:** No. The ITA does not allow a deduction for the cost of protective puts as an "insurance premium" on investments.

**As a capital cost:** Yes. The put premium becomes part of the cost base of the overall investment position. If the put expires worthless, it's a capital loss. If exercised, it adjusts proceeds of the underlying (Section 2.2).

**As a business expense:** If the puts hedge a **business** position (e.g., active trading inventory), the premium is deductible as a business expense under s.9. This is the preferred treatment if CC's trading is classified as business income anyway.

---

## 8. Straddles, Spreads, and Complex Strategies

### Audit Risk: MEDIUM-HIGH | Relevance: FUTURE

### 8.1 Tax Treatment of Multi-Leg Options Strategies

Canada does NOT have specific legislation for multi-leg options strategies (unlike the US, which has straddle rules under IRC s.1092). Each leg is treated as a **separate property** for Canadian tax purposes.

**Vertical spread (bull call spread, bear put spread):**
```
Buy 1 BTC call at $90K strike for $5,000
Sell 1 BTC call at $100K strike for $2,000
Net debit: $3,000

Tax treatment at expiry/close:
- Long call: Capital gain/loss based on proceeds - $5,000 ACB
- Short call: Capital gain based on $2,000 premium - buyback cost
- The two legs are SEPARATE transactions for tax purposes
- You cannot net them into a single gain/loss
```

**Iron condor, butterfly, calendar spread:**
Same principle — each leg is a separate property disposition. The CRA does not allow netting of related option legs into a single transaction.

**Implication:** Multi-leg strategies create **multiple capital transactions per trade**, increasing record-keeping complexity but not changing the total tax outcome (assuming all legs are capital in nature).

### 8.2 Superficial Loss Rule and Rolling Options

**ITA s.54 "superficial loss":** A capital loss is denied if:
1. You dispose of property at a loss, AND
2. You (or an affiliated person) acquire **identical property** within 30 days before or after the disposition, AND
3. You (or affiliated person) still own it 30 days after the disposition

**Application to options:**
- Selling a call/put at a loss and buying a new call/put with the **same underlying, same strike, same expiry** within 30 days = superficial loss (denied)
- Selling a call at a loss and buying a call with a **different strike or expiry** = NOT identical property = loss is allowed
- Rolling an option (close existing, open new at different strike/expiry) = generally NOT a superficial loss because the new option is not "identical" to the old one

**Key ruling:** CRA considers options with different strikes or expiry dates to be **different property** even if on the same underlying. This is favorable for rolling strategies.

**However:** If you close a losing position and immediately re-enter with essentially the same economic exposure (same strike, same expiry, just a few minutes later), the CRA could argue the "substance over form" doctrine applies and deny the loss.

**Best practice:**
1. When rolling, always change at least the strike price OR the expiry date
2. Document the investment rationale for the new position (not just "rolling a losing trade")
3. Wait 31 days if closing a losing option position and re-entering with identical terms

### 8.3 Calendar Spreads — Timing of Income Recognition

A calendar spread involves selling a near-term option and buying a longer-term option:

```
Sell 1 BTCC April $15 call for $1.50
Buy 1 BTCC July $15 call for $2.50
Net debit: $1.00

Tax treatment:
- April call expires/is closed: Capital gain/loss recognized in that tax year
- July call continues: No tax event until disposed of
- The two legs may fall in DIFFERENT tax years
```

**Strategy for tax deferral:** Sell options expiring in the current tax year (recognize losses or small gains now), buy options expiring in the next tax year (defer larger gains). This is a legitimate timing strategy — the CRA cannot force you to close an option before it expires.

### 8.4 Straddle Rules — Canada vs US

| Feature | Canada | United States |
|---------|--------|---------------|
| Specific straddle rules | NO (general principles apply) | YES (IRC s.1092) |
| Loss deferral on offsetting positions | No specific rule (superficial loss only) | Losses deferred to extent of unrealized gain in offsetting position |
| Mixed straddles | N/A | Complex rules for hedged straddles |
| Required identification | No | Yes (must identify offsetting positions) |

**Canada's lack of straddle rules is an advantage** for sophisticated traders. You can recognize losses on one leg of a straddle without deferring them against unrealized gains in the other leg — unlike in the US.

---

## 9. Derivatives for Tax Planning

### Audit Risk: MEDIUM-HIGH to EXTREME (depends on strategy) | Relevance: FUTURE

### 9.1 Equity Collars to Defer Capital Gains `[FUTURE: $500K+ unrealized gains]`

See Section 7.3 for mechanics. Additional planning considerations:

**Optimal collar width:**
- Narrower collar (95/105%) = better loan terms but higher GAAR risk (looks more like a sale)
- Wider collar (85/115%) = more economic risk retained = stronger position against GAAR
- Recommended minimum: 15% gap between put and call strikes

**Timing:**
- Implement collar in December to defer gains from Year 1 to Year 2 (or indefinitely)
- Maintain collar through tax year-end, then reassess
- Each year the collar is maintained, the gain continues to be deferred

**Cost:**
- Costless collar: possible when implied volatility is high (put and call premiums roughly equal)
- Net debit collar: common in low-volatility environments (puts cost more than calls)
- Net credit collar: possible with wide collars (sacrificing more upside)

### 9.2 Prepaid Variable Forwards `[FUTURE: $1M+ concentrated positions]`

A prepaid variable forward is a more sophisticated version of the collar:

1. CC enters a forward contract to deliver shares at a future date
2. The number of shares delivered varies based on the share price at maturity
3. CC receives an **upfront cash payment** (the "prepaid" element)
4. CC retains ownership and voting rights during the contract term

**Tax treatment (Canada):**
- CRA has not issued specific guidance on prepaid variable forwards
- Under general principles, the upfront payment could be:
  - A loan (no tax event — repaid by delivering shares), OR
  - An advance payment for a disposition (capital gain triggered at contract inception)
- The taxpayer's position: treat as a loan until the forward is settled
- CRA's likely challenge: argue it's a "sale" at inception under GAAR if the taxpayer receives substantially all the economic value upfront

**GAAR risk: HIGH.** Use only with top-tier tax counsel.

### 9.3 Total Return Swaps `[FUTURE: CCPC with $1M+ invested]`

A total return swap (TRS) allows a CCPC to gain exposure to an asset without owning it:

- CCPC pays a fixed/floating rate to the swap counterparty
- Counterparty pays the total return (price appreciation + dividends) of a reference asset
- CCPC never owns the reference asset

**Tax advantages:**
- Payments received on TRS: generally **income** (not capital gains)
- BUT: the CCPC can use the TRS to convert what would be **passive investment income** (subject to high corporate rates ~50%) into **active business income** (12.2% SBD rate) if the TRS is part of the CCPC's active business operations
- This is extremely aggressive and requires careful structuring

**Availability:** Major banks (RBC, TD, BMO) offer TRS to institutional clients and HNW individuals. Minimum typically $1M-$5M notional.

### 9.4 Convertible Debentures and Synthetic Positions

**Convertible debentures** combine debt (interest income) with an embedded option (capital gain potential):

- Interest payments: taxed as interest income (100% inclusion)
- Conversion to equity: NOT a taxable event — ITA s.51(1) provides a tax-free rollover
- ACB of shares received = ACB of the debenture converted
- Subsequent sale of shares: capital gain/loss from the debenture's ACB

**Synthetic positions using options:**
- Long stock + short call = synthetic short put
- Long call + short stock = synthetic long put
- Long call + short put (same strike) = synthetic long stock

Each leg is taxed independently. The synthetic nature does not change the character of each component for Canadian tax purposes.

### 9.5 Swap-Based ETFs for Tax Efficiency `[NOW]`

Several Canadian ETFs use total return swaps to deliver index returns more tax-efficiently:

**How it works:**
- The ETF enters a TRS with a counterparty (usually a bank)
- The ETF pays a fee and receives the total return of the index
- No dividends are received (they're embedded in the swap return)
- At disposition, the entire gain is a **capital gain** (not dividend income)

**Tax benefit:**
- Converts dividend income (eligible dividends at ~39% combined rate) and foreign dividends (full marginal rate up to 53.53%) into capital gains (50% inclusion, effective ~26.76%)
- Eliminates US withholding tax on US equity exposure (the Canadian bank, not the ETF, holds the US securities)

**Examples:**
- Horizons Total Return ETFs (HXT for S&P/TSX, HXS for S&P 500)
- Note: CRA challenged some swap-based ETFs in 2019, and many converted to traditional structure. Check current structure before investing.

`[NOW]` For non-registered accounts, prefer swap-based ETFs for US equity exposure — eliminates 15% US withholding + converts dividends to capital gains. In TFSA/RRSP, use traditional ETFs (withholding tax treatment differs).

---

## 10. Cross-Border Derivatives

### Audit Risk: MEDIUM | Relevance: NOW (US-listed options, UK opportunity)

### 10.1 US-Listed Options for Canadian Residents

CC can trade US-listed options (CBOE, NYSE Arca) through Canadian brokers (IBKR, Questrade, Wealthsimple Trade).

**Withholding tax:**
- **Options premiums:** NO US withholding tax on option premiums (premiums are not "dividends" or "interest" — they are capital transactions)
- **Dividends on underlying shares:** 15% US withholding (reduced by Canada-US treaty from 30%)
- **Assignment/exercise:** No withholding on the share transaction itself

**Reporting:**
- All gains/losses must be reported on CC's Canadian T1 return
- Convert all USD amounts to CAD at the Bank of Canada daily exchange rate on the date of each transaction
- No US tax return required for non-resident aliens trading through a broker (unless effectively connected income)

**Currency gain/loss:**
- The USD/CAD fluctuation between purchase and sale of the option creates a separate forex gain/loss
- Subject to s.39(2) — $200 annual exemption, remainder is capital
- Track the exchange rate on EACH transaction date separately

### 10.2 UK Spread Betting (Revisited — Cross-Border)

See Section 4.3 for detailed analysis. Summary for cross-border purposes:

| CC's Residence | UK Spread Betting Treatment |
|----------------|----------------------------|
| Canada (current) | Taxable as capital gain/business income despite UK tax-free status |
| UK | Tax-free (HMRC: gambling, not taxable) |
| Isle of Man | Tax-free (follows UK treatment, 0% CGT backup) |
| Ireland | Taxable as capital gain at 33% CGT rate |

**Treaty treatment:** The Canada-UK tax treaty (Article 13 — Capital Gains) does not specifically address spread betting. Under general treaty principles:
- Capital gains are taxable in the resident state (Canada)
- The UK doesn't tax spread betting regardless, so no foreign tax credit is available
- Result: Canadian resident pays full Canadian tax with no offset

### 10.3 Treaty Treatment of Derivatives Income

Under most of Canada's tax treaties (following the OECD Model):

| Income Type | Treaty Article | Taxing Right |
|-------------|---------------|-------------|
| Capital gains on derivatives | Article 13 | Resident state (Canada) |
| Interest (from structured products) | Article 11 | Source state withholding (usually 10-15%), FTC in Canada |
| Dividends (on underlying) | Article 10 | Source state withholding (15% US, varies by treaty), FTC in Canada |
| Business profits (from trading) | Article 7 | Resident state (Canada) unless permanent establishment in source state |

**Key insight:** Most derivatives income is taxable only in Canada (the resident state). This means:
1. No foreign tax credit complications for most derivatives trading
2. BUT: if CC trades through a foreign entity (future CCPC with foreign sub), Article 7 PE rules become relevant

### 10.4 The PFIC Trap with US ETF Options

**Passive Foreign Investment Company (PFIC)** — IRC s.1291-1298:

This is primarily a US tax concept, but it's relevant if CC ever becomes a US tax resident (dual citizen concerns, US work stint, etc.):

- Most non-US mutual funds and ETFs are PFICs under US tax rules
- US persons holding PFICs face punitive tax treatment (excess distribution regime or QEF election)
- **Canadian-listed ETFs** held by a Canadian resident: NO PFIC issue (CC is not a US person)
- **If CC becomes a US tax person:** All Canadian ETFs become PFICs. Options on those ETFs inherit the PFIC taint.

`[NOW]` Not an issue while CC is only a Canadian/UK citizen residing in Canada. BUT: if CC ever considers US residency/green card, unwind all Canadian ETF positions BEFORE becoming a US tax person. The PFIC regime is one of the harshest in US tax law.

---

## 11. CC-Specific Strategies

### 11.1 Covered Calls on Crypto ETFs in TFSA — Tax-Free Premium Income `[NOW]`

**The setup:**
1. CC's Wealthsimple TFSA holds crypto ETF shares (BTCC, EBIT, or BTCX)
2. CC writes covered calls against those positions monthly
3. All premium income is **completely tax-free** inside the TFSA

**Projected income:**
```
Assumption: $7,000 FHSA contribution (2026) + $7,000 TFSA contribution
Hold: 1,000 shares of BTCC at ~$14/share = $14,000
Write monthly covered calls: ~2% OTM, collecting ~$0.30/share/month

Monthly premium: 1,000 x $0.30 = $300
Annual premium: $3,600 (25.7% yield on $14,000)
Tax: $0 (TFSA)

If held outside TFSA at 53.53% marginal rate:
Tax would be: $3,600 x 50% x 53.53% = $963/year
```

**Limitations:**
- Wealthsimple does not currently offer options trading in TFSA
- IBKR offers TFSA with options capability
- Questrade offers covered calls in TFSA for approved accounts

**Action:** Open an IBKR TFSA, transfer holdings, begin covered call strategy.

### 11.2 Gold Options via OANDA — Hedging vs Speculation `[NOW]`

CC trades gold on OANDA (CFDs). Key characterization:

**If CC's gold trading is occasional and investment-oriented:**
- Gains/losses = capital gains/losses
- 50% inclusion rate
- CFD swap fees = capital cost adjustment

**If CC's gold trading is frequent and systematic (ATLAS automated):**
- Gains/losses = business income/loss
- 100% inclusion rate
- BUT: all swap fees, commissions, data feeds, portion of ATLAS development costs are fully deductible

**Optimization for CC:**
Given that ATLAS runs automated strategies on OANDA gold, the CRA will likely characterize this as **business income**. This is actually acceptable because:
1. Losses are fully deductible against all income (not just capital gains)
2. ATLAS infrastructure costs (server, API fees, development time) are deductible
3. At $280K+ income, the difference between 50% inclusion and 100% inclusion is significant but offset by full loss/expense deductibility

**Hedge documentation:** If CC takes long-term gold positions as a hedge against inflation/currency risk on OASIS receivables (USD-denominated), document this as a business hedge. The hedge characterization would make the gains business income regardless (matching OASIS income character), but would also make losses immediately deductible against OASIS income.

### 11.3 Options for Income Smoothing `[FUTURE: $280K+ income with variability]`

**The problem:** CC's projected $280K-$480K income in 2026 creates a wide tax band exposure. Income at $480K faces 53.53% marginal rate; income at $100K faces ~33%.

**Options-based income smoothing:**

**Strategy A — Defer gains with LEAPS:**
- Instead of closing winning trades in December, buy a protective put (LEAPS, 12+ months out)
- The unrealized gain is locked in but not recognized until the put expires or the position is closed
- Close in January of the next year to push recognition into Year 2
- Cost: put premium (typically 3-8% of position value for 12-month ATM put)

**Strategy B — Harvest losses, defer gains:**
- Close losing positions in high-income years (losses offset gains at marginal rate)
- Keep winning positions open or collar them into low-income years
- The asymmetry: losses are more valuable in high-income years, gains are cheaper in low-income years

**Strategy C — Calendar spread across tax years:**
- Sell near-term options expiring in the current (high-income) year — income recognized now
- Buy longer-term options expiring in the next (potentially lower-income) year — gains deferred
- Net effect: Premium income now (at high rates, but small amounts), capital gains later (at potentially lower rates, but larger amounts)

### 11.4 Protective Puts Before Canada Departure `[FUTURE: Crown Dependencies migration]`

When CC triggers the departure from Canada (s.128.1 deemed disposition):

**The problem:** Departure tax creates a deemed disposition of all property at FMV. If CC has $500K in unrealized gains, the departure tax bill could be $130K+.

**Protective put strategy:**
```
Before departure:
1. Buy deep ITM puts on all appreciated positions
2. The puts lock in the current value, so any decline after departure doesn't create a loss
   that Canada would have taxed (since deemed disposition already occurred)
3. After departure and arrival in Crown Dependencies (0% CGT):
   - Let the puts expire (if positions have risen — you keep the upside tax-free)
   - Exercise the puts (if positions have fallen — you sell at the put strike, no further tax)

Cost: Put premium (2-5% of position value)
Benefit: Protection against price decline between departure date and actual liquidation
Tax consequence: Put premium is a capital loss in Canada (deductible against departure gains)
```

**Alternative — collar before departure:**
- Buy puts + sell calls to create a costless collar
- This locks the departure tax bill to a known range
- The call premium offsets the put cost
- After departure to 0% CGT jurisdiction, the collar is unwound with no tax

### 11.5 Collar Strategy on Appreciated Crypto Before Selling `[FUTURE: large BTC gains]`

If CC has significant unrealized BTC gains and wants to monetize without immediate tax:

```
Current: CC holds 2 BTC at $120,000 USD each = $240,000 USD
ACB: $50,000 USD (bought at $25,000 each)
Unrealized gain: $190,000 USD (~$260,000 CAD)
Capital gains tax if sold: $260,000 x 50% x 53.53% = ~$69,600 CAD

Collar strategy:
1. Buy BTC put at $115,000 (4% below current)
2. Sell BTC call at $130,000 (8% above current)
3. Net premium: approximately zero (costless collar)
4. Borrow against the collared position: Bank lends 70-80% of collared value
5. Receive $168,000-$192,000 USD in loan proceeds
6. Pay interest on loan (deductible under s.20(1)(c) if used for income-producing purpose)
7. Capital gain: NOT triggered — CC still owns the BTC

Annual cost: Loan interest (~5-7%) on $180,000 = $9,000-$12,600 USD
Tax savings: $69,600 CAD in capital gains tax DEFERRED
Net benefit in Year 1: $69,600 - $12,600 = $57,000 CAD
```

**Availability:** Direct BTC collars are available through:
- CME Bitcoin options (institutional, high minimums)
- Deribit (crypto-native, available to CC now but no CAD support)
- Some OTC desks will structure collars on BTC for $100K+ positions

**In CCPC:** Even more powerful — CCPC borrows against collared crypto, invests proceeds in active business at 12.2% corporate rate. The interest deduction shelters passive income, and the corporate rate arbitrage compounds.

---

## 12. Key Case Law

### 12.1 Friedberg v. The Queen (1993 SCC, [1993] 4 SCR 285)

**Facts:** Friedberg engaged in gold and currency straddle transactions (long and short positions in the same commodity) through commodity futures. He recognized losses on one leg while deferring gains on the other.

**CRA's position:** The transactions were shams or should be recharacterized as a single transaction with no net gain or loss.

**Decision:** The Supreme Court of Canada ruled in favor of the taxpayer:
- Each leg of a straddle is a **separate transaction** for tax purposes
- The CRA cannot collapse two separate transactions into one merely because they are offsetting
- Losses on closed positions are deductible even if unrealized gains exist on the other leg
- "The courts must deal with what the taxpayer actually did, not with what he might have done"

**Impact for CC:** This is the foundational case supporting separate treatment of multi-leg options strategies in Canada. It means:
- CC can close a losing options leg and recognize the loss without closing the profitable leg
- The CRA cannot force netting of related positions
- Straddle strategies are legitimate for tax timing purposes

**Limitations (post-Friedberg):** GAAR (s.245, enacted 1988 but expanded since) could be invoked if the **primary purpose** is tax avoidance with no economic substance beyond the tax benefit.

### 12.2 Canadian Helicopters Ltd v. The Queen (2002 FCA, 2002 FCA 30)

**Facts:** Canadian Helicopters entered into forward foreign exchange contracts to hedge USD-denominated revenue. The company treated gains/losses on the forwards as part of its business income.

**CRA's position:** The forward contracts were separate capital transactions, not business income hedges.

**Decision:** The Federal Court of Appeal agreed with the taxpayer:
- Forward contracts entered to hedge a **specific, identifiable business risk** take the character of the underlying business activity
- The key factors: (1) direct relationship between the derivative and the hedged exposure, (2) contemporaneous documentation of the hedging relationship, (3) consistency in treatment
- Gains on the forwards = business income (matching the hedged revenue)

**Impact for CC:**
- If CC uses gold CFDs on OANDA to hedge USD-denominated OASIS receivables, the gains/losses should be business income (matching OASIS income character)
- Document the hedging relationship at the time the position is opened
- Apply the treatment consistently — don't switch between capital and business characterization for identical positions

### 12.3 George Weston Ltd v. The Queen (2015 TCC, 2015 TCC 42)

**Facts:** George Weston Limited entered into various derivative transactions (equity swaps, forwards, options) in connection with its investment portfolio. The company treated gains as capital gains.

**CRA's position:** The gains were business income because the company had the knowledge, resources, and frequency typical of a business.

**Decision:** The Tax Court found that:
- The derivatives were entered as part of an **investment strategy**, not a trading business
- Even sophisticated derivative transactions can be on **capital account** if the underlying intent is investment (long-term appreciation, portfolio protection)
- The frequency of transactions alone does not determine business vs. capital character
- The **overall context** including the taxpayer's other activities, the nature of the assets, and the stated purpose matters

**Impact for CC:** This case supports treating CC's options/derivatives as capital gains even though he uses sophisticated strategies (ATLAS), PROVIDED:
- The primary purpose is investment return (not day trading)
- Holding periods are measured in weeks/months, not hours
- The strategies aim to protect or enhance an existing portfolio (not generate standalone speculative income)

### 12.4 Echo Bay Mines Ltd v. The Queen (1992 FCA)

**Facts:** Echo Bay entered into gold forward contracts to hedge gold production.

**Decision:** Confirmed that hedging gains/losses on commodity forwards take the character of the underlying business activity. Gold forward gains were business income because they hedged business production revenue.

**Impact for CC:** Supports business income treatment for gold hedges. If CC hedges OASIS USD receivables with gold CFDs (gold as a USD proxy), the gains are business income — matching and offsetting OASIS business income.

### 12.5 Rezek v. The Queen (2005 TCC, 2005 TCC 626)

**Facts:** Individual taxpayer made numerous stock option trades with high frequency.

**Decision:** The Tax Court found the options trading constituted a **business** based on:
- Volume of transactions (hundreds per year)
- Short holding periods (days)
- Full-time attention to the market
- Sophisticated knowledge and strategy

**Impact for CC:** Cautionary tale. If CC's ATLAS trading (including options) involves high-frequency automated trading, the CRA will rely on cases like Rezek to argue business income. Separate long-term options positions (capital account) from active algorithmic trading (business income).

---

## 13. Priority Action Matrix

### Immediate Actions `[NOW]` — Execute in 2026

| # | Action | Tax Impact | Complexity | Risk |
|---|--------|-----------|------------|------|
| 1 | **Open IBKR TFSA** with options approval | Enable tax-free covered calls | LOW | LOW |
| 2 | **Begin covered calls** on crypto ETF holdings in TFSA | $1,000-$5,000/year tax-free income | LOW | LOW |
| 3 | **Document OANDA positions** as business income (consistent treatment) | Full expense deductibility | LOW | LOW |
| 4 | **Track all option/CFD transactions** with dates, CAD FX rates, and stated purpose | Audit defense | MEDIUM | LOW |
| 5 | **Classify Kraken futures** as business income, deduct all ATLAS costs | $2,000-$5,000/year in deductions | LOW | LOW |
| 6 | **Use swap-based ETFs** (HXT, HXS) in non-registered for US equity exposure | Convert dividends to capital gains + eliminate US withholding | LOW | LOW |
| 7 | **Never put OASIS shares** in TFSA/RRSP after incorporation | Avoid 50-100% penalty tax | LOW | EXTREME if violated |

### Near-Term Actions `[FUTURE: CCPC incorporation at $80K+]`

| # | Action | Tax Impact | Complexity | Risk |
|---|--------|-----------|------------|------|
| 8 | **Grant CCPC stock options** at incorporation FMV | Defer tax until share sale + 50% deduction | MEDIUM | LOW |
| 9 | **Use CCPC for derivatives trading** where appropriate | 12.2% corporate rate vs 53.53% personal | MEDIUM | MEDIUM |
| 10 | **Structure OASIS USD hedges** as documented business hedges | Match forex gains/losses to business income | LOW | LOW |

### Medium-Term Actions `[FUTURE: $280K+ income / $500K+ portfolio]`

| # | Action | Tax Impact | Complexity | Risk |
|---|--------|-----------|------------|------|
| 11 | **Implement collar strategy** on concentrated positions | Defer $50K-$100K+ in capital gains tax | HIGH | MEDIUM |
| 12 | **Income smoothing** via LEAPS and calendar spreads | Reduce marginal rate by $10K-$30K/year | MEDIUM | MEDIUM |
| 13 | **Tax-loss harvesting** with options (close losers, roll to new strikes) | $5K-$20K/year in loss recognition timing | MEDIUM | LOW |

### Long-Term Actions `[FUTURE: Crown Dependencies migration / $1M+ portfolio]`

| # | Action | Tax Impact | Complexity | Risk |
|---|--------|-----------|------------|------|
| 14 | **Protective puts before departure** from Canada | Lock departure tax bill, protect against decline | HIGH | LOW |
| 15 | **UK spread betting** post-migration (Isle of Man) | 100% tax elimination on derivatives | LOW | LOW |
| 16 | **Total return swaps** via CCPC for asset exposure | Convert passive to active income | HIGH | HIGH |
| 17 | **Prepaid variable forwards** on concentrated positions | Monetize without disposition | EXTREME | EXTREME |

---

## Appendix A: Quick Reference — Tax Character by Instrument

| Instrument | Capital Gain/Loss | Business Income/Loss | Interest Income | Notes |
|------------|-------------------|---------------------|-----------------|-------|
| Long call/put (bought) | Default | If business trader | — | s.49(1) on exercise |
| Short call/put (written) | Default (on expiry) | If business trader | — | Adjusted to proceeds/ACB on assignment |
| Covered call | Capital gain (strongly) | Rare | — | Most favorable treatment |
| Futures (exchange-traded) | Default | If hedging/business trader | — | Daily settlement = partial dispositions |
| Crypto futures (Kraken) | Default | Likely (automated trading) | — | Each funding payment is a component |
| CFDs (OANDA) | Default | If frequent/systematic | — | No qualified investment status |
| Forex forwards | Capital (s.39(2)) | If hedging business FX | — | $200 annual exemption |
| PPNs | — | — | YES (100%) | Return above principal = interest |
| Swap-based ETFs | Capital gain | — | — | Converts dividends to capital gains |
| Leveraged ETFs | Capital gain (distributions may vary) | — | Possible | Hold in registered accounts only |
| Convertible debentures | Capital gain (after conversion) | — | Interest (before conversion) | s.51(1) rollover on conversion |
| Employee stock options (CCPC) | Capital gain (above FMV at exercise) | Employment income (option benefit) | — | Deferred until disposition |
| UK spread betting (from Canada) | Capital gain | If business trader | — | No UK tax, but Canada taxes worldwide |

---

## Appendix B: Record-Keeping Checklist for Derivatives

For every derivatives transaction, CC must track:

- [ ] **Date** of open and close (or expiry/assignment)
- [ ] **Instrument type** (option, future, CFD, forward, swap)
- [ ] **Underlying asset** (BTC, XAU/USD, BTCC, etc.)
- [ ] **Direction** (long/short, buy/write)
- [ ] **Strike price** (for options)
- [ ] **Expiry date** (for options and dated contracts)
- [ ] **Premium** paid or received (CAD equivalent at transaction date)
- [ ] **Commission/fees** (CAD equivalent)
- [ ] **Swap/rollover/funding fees** (for CFDs and perpetual futures)
- [ ] **Exchange rate** (Bank of Canada daily rate for USD/CAD on each transaction date)
- [ ] **Stated purpose** (hedge or speculative — document at time of trade)
- [ ] **Linked position** (if hedging, identify the hedged asset/exposure)
- [ ] **Outcome** (expired, exercised, assigned, closed)
- [ ] **Gain/loss calculation** in CAD with all components

**Retention period:** CRA requires 6 years from the end of the tax year. For capital property (like CCPC shares), keep records as long as you own the property + 6 years after disposition.

---

## Appendix C: ITA Reference Index

| Section | Topic |
|---------|-------|
| s.7 | Employee stock option benefit |
| s.7(1.1) | CCPC option deferral |
| s.9 | Business income |
| s.20(1)(c) | Interest deductibility on borrowed money |
| s.38 | Taxable capital gains and allowable capital losses |
| s.39(1) | Capital gain/loss definition |
| s.39(2) | Foreign currency gain/loss (capital treatment + $200 exemption) |
| s.49(1) | Options — tax treatment on grant, exercise, expiry |
| s.51(1) | Convertible property — tax-free rollover |
| s.54 | Superficial loss definition |
| s.110(1)(d) | 50% stock option deduction |
| s.127.52(1)(h) | AMT add-back for stock option deductions |
| s.128.1 | Departure tax — deemed disposition on emigration |
| s.146.2 | TFSA rules |
| s.204 | Qualified investment definition for registered plans |
| s.207.01(1) | TFSA prohibited/non-qualified investment + advantage definitions |
| s.207.04 | Tax on prohibited investments (100% penalty) |
| s.207.05 | Tax on TFSA advantage |
| s.245 | General Anti-Avoidance Rule (GAAR) |
| s.248(1) | Definition of "property" and "disposition" |

---

## Appendix D: Glossary

| Term | Definition |
|------|-----------|
| **ACB** | Adjusted Cost Base — your tax cost for a property, used to calculate capital gains |
| **AMT** | Alternative Minimum Tax — minimum tax payable regardless of deductions (s.127.5) |
| **CCPC** | Canadian-Controlled Private Corporation — lower tax rates, stock option deferral |
| **CFD** | Contract for Difference — derivative settled in cash based on price movement |
| **FMV** | Fair Market Value — the price a willing buyer and seller would agree on |
| **FTC** | Foreign Tax Credit — credit for taxes paid to another country (s.126) |
| **GAAR** | General Anti-Avoidance Rule — CRA's tool to deny transactions lacking economic substance |
| **LEAPS** | Long-Term Equity Anticipation Securities — options with 1+ year to expiry |
| **PFIC** | Passive Foreign Investment Company — US tax classification, punitive for US persons |
| **PPN** | Principal-Protected Note — structured product guaranteeing return of capital |
| **ROC** | Return of Capital — distribution reducing ACB, not immediately taxable |
| **SBD** | Small Business Deduction — reduced corporate tax rate on first $500K active business income |
| **TRS** | Total Return Swap — derivative providing total economic exposure to a reference asset |

---

*This document is for CC's personal financial planning. Not legal or tax advice. Consult a qualified Canadian tax professional before executing any strategy. ATLAS researches, calculates, and prepares — CC reviews and makes final decisions.*

*Last updated: 2026-03-27 | ATLAS v1.0 | ~1,100 lines*
