---
tags: [canon, finance, tax, investing, frameworks, knowledge-base, reference, cfo-canonical]
---

# CFO CANON — The Frameworks Atlas Grounds Every Decision In

> Every Atlas recommendation, allocation, tax move, spend approval, and stock pick should trace to at least one of these canonical frameworks. If a decision can't be defended with one of these, it's probably a vibe, not finance.
>
> This is the CFO equivalent of Maven's `MARKETING_CANON.md`. Skills reference it by pointer (`see [[CFO_CANON]] § Buffett`).
>
> Neighbors: [[SOUL]] · [[STATE]] · [[skills/unit-economics-validation/SKILL|unit-economics-validation]] · [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] · [[INDEX]].

---

## The 10 Pillars (memorize)

### 1. **Warren Buffett & Charlie Munger — Compounders + Margin of Safety in practice**
- Source: *Berkshire Hathaway letters* (1965–present), *Poor Charlie's Almanack*, *The Essays of Warren Buffett* (Cunningham ed.)
- **Core idea**: buy wonderful businesses at fair prices. The compounding machine is a business with durable economics, honest management, and reinvestment runway. Price is what you pay; value is what you get.
- **Owner-earnings**: GAAP earnings lie. Owner-earnings = net income + D&A – maintenance capex – working-capital changes. This is the cash a business actually throws off.
- **Moat categories** (Munger): switching costs, network effects, cost advantages, intangibles (brand/patents/licenses), efficient scale.
- **Reinvestment ROIC**: a compounder only compounds if it can redeploy earnings at high incremental returns. If it can't, cash should return to owner.
- **Apply**: every stock pick Atlas makes for the operator answers: (a) does this business have a moat? (b) does management allocate capital well? (c) is the price below owner-earnings-based fair value with margin of safety? If no to any, reject.
- **Anti-pattern**: paying up for growth without moat. Revenue growth without ROIC is capital incineration.

### 2. **Benjamin Graham — The Intelligent Investor**
- Book: *The Intelligent Investor* (1949; Zweig rev. 2003), *Security Analysis* (1934, with Dodd)
- **Mr. Market metaphor**: the market is a manic-depressive business partner. You don't need his opinion on the value of your holdings every day. Use his mood to your advantage; don't let it set your behavior.
- **Margin of safety**: never buy at intrinsic value. Demand a discount — ideally 30%+ — to protect against analytical error and bad luck. The margin IS the risk management.
- **Defensive vs enterprising investor**: most operators are defensive. Index the core, concentrate the edge, don't confuse effort for return.
- **Apply**: Atlas rejects any pick priced at or above computed fair value. Every buy has an explicit discount-to-IV number. Cash is a position — holding cash waiting for a Mr. Market tantrum is a valid strategy.
- **Anti-pattern**: "the market is efficient, buying at fair value is fine." It isn't. Over a 20-year hold, entry price matters a lot more than newsletter intuition suggests.

### 3. **Nassim Nicholas Taleb — Antifragility, tail risk, convexity**
- Books: *Fooled by Randomness* (2001), *The Black Swan* (2007), *Antifragile* (2012), *Skin in the Game* (2018)
- **Barbell strategy**: 85-90% in extremely safe assets (cash equivalents, short T-bills), 10-15% in asymmetric bets (positive convexity). Zero in the middle — the "medium-risk" zone is the blind spot where ruin hides.
- **Via negativa**: most improvement comes from REMOVING fragilities, not adding sophistication. Cancel the bad subscriptions before optimizing the good ones.
- **Skin in the game**: if the advisor can't lose from bad advice, discount the advice. Management with meaningful ownership > management with options grants.
- **Lindy Effect**: the longer an idea has survived, the longer it likely will. Applies to tax strategies (RRSP/TFSA have survived decades; some new loophole might not).
- **Apply**: Atlas never puts the operator in positions with unbounded downside for bounded upside. Barbell the portfolio. Every tax strategy passes a "what's the worst CRA interpretation?" test. Every pick passes a "what kills this?" bear case.
- **Anti-pattern**: selling volatility for small premiums. One tail event ends the game; the pennies-in-front-of-steamroller trade is always worse than it looks ex ante.

### 4. **CRA tax guides — the source of truth**
- Sources: T4002 (Self-employed business income), T2125 line definitions, T2 Corporation guide, CCPC small-business deduction (s.125), GAAR (s.245), s.128.1 (departure tax), FHSA guide (RC727), TFSA limits, T1135 (foreign property > $100K), CARF (Crypto-Asset Reporting Framework), s.7(1.1) stock option rules for CCPCs.
- **Core idea**: the rules are written down. Every Atlas tax recommendation has a statute, folio, or technical interpretation behind it. No invented strategies, no "my cousin's accountant said." Substance over form — GAAR-safe structures only.
- **Apply**: before any tax recommendation is surfaced to the operator, Atlas names the specific section or folio. Example: "Advertising deducts on T2125 line 8521 — CRA Guide T4002, ch. 3." If the section can't be named, the recommendation is paused pending research.
- **Anti-pattern**: "crypto is untaxed if you don't convert to fiat." False. Disposition includes crypto-to-crypto trades (CRA technical interpretation 2014-0561081E5). Atlas flags this every time.

### 5. **CPA Canada — audit-defensible bookkeeping**
- Sources: *CPA Canada Handbook*, CRA audit protocols, IFRS for small business, ASPE (Accounting Standards for Private Enterprises).
- **Core idea**: bookkeeping is a defense system. Every deduction must survive an audit 7 years later, when the context is forgotten and only the paper trail remains.
- **The receipts rule**: no receipt → no deduction. Period. Digital copies are fine; receipts must show vendor, date, amount, GST/HST, and business purpose.
- **Segregate personal from business**: commingling = audit risk. Even as a sole prop, run a separate bank account and card for business.
- **Apply**: Atlas's `gmail_receipts.py` pipeline feeds the audit trail. Every ambiguous charge is flagged, not silently allocated. CSV export for T2125 is the source of truth; Atlas does not estimate.
- **Anti-pattern**: "I'll reconstruct it from memory." Never survives audit. Book now, claim later.

### 6. **Philip Fisher — 15 Points for growth stocks**
- Book: *Common Stocks and Uncommon Profits* (1958)
- **The 15 Points** (abbreviated): (1) sufficient market? (2) management commitment to growing through R&D/sales effort when current products mature? (3) R&D effectiveness vs spend? (4) above-average sales organization? (5) worthwhile profit margin? (6) what's the company doing to maintain or improve margin? (7) outstanding labor and personnel relations? (8) outstanding executive relations? (9) management depth? (10) cost analysis and accounting controls? (11) industry-specific clues? (12) short-range vs long-range profit outlook? (13) equity financing avoided to dilute shareholders? (14) management candor with shareholders (especially in trouble)? (15) management unquestionable integrity?
- **Scuttlebutt method**: talk to customers, suppliers, ex-employees. Public filings are the 20%; scuttlebutt is the 80%.
- **Apply**: Atlas's research pipeline includes qualitative signals — glassdoor trends, ex-employee LinkedIn notes, customer-forum sentiment — alongside fundamentals. A stock that passes the 15 Points earns a higher conviction floor.
- **Anti-pattern**: filter-only quant screens. Fisher's insight is that the unmeasurable (management candor, R&D culture) often dominates the measurable.

### 7. **Howard Marks — Memos (cycles + second-level thinking)**
- Source: *The Most Important Thing* (2011), Oaktree memos (2001–present).
- **Second-level thinking**: first-level says "company is good, buy." Second-level asks "is the market's consensus on this business already in the price?" Every pick is a contest against expectations, not a contest on merit alone.
- **Pendulum of investor psychology**: greed↔fear. Cycles are inevitable; timing exact peaks/troughs is not. Lean against the crowd when extremes appear.
- **Risk = permanent loss of capital, not volatility**. Volatility is the vehicle; permanent impairment is the destination to avoid.
- **Apply**: every pick answers "what's in the price?" If the story is consensus, conviction floor rises. Atlas flags sentiment extremes from `research/macro_watch.py` + news sentiment as inputs.
- **Anti-pattern**: "the chart looks strong, trend is your friend." First-level. Trends reverse when expectations meet reality.

### 8. **Ray Dalio — All-Weather + Principles**
- Books: *Principles: Life and Work* (2017), *Principles for Dealing with the Changing World Order* (2021), *A Template for Understanding Big Debt Crises* (2018).
- **All-Weather portfolio**: four economic regimes (growth up/down, inflation up/down). Construct a portfolio that has a productive asset for each quadrant, weighted by risk-parity not dollar-parity.
- **Economic machine** video: productivity + short-term credit cycle + long-term debt cycle = the waves. Understand which wave you're surfing.
- **Radical transparency / principles-based decision-making**: decisions are algorithms. Write them down, iterate on them, reuse them.
- **Apply**: Atlas constructs a regime-aware allocation even at small balances. Real return protection (inflation hedges) gets at least a nominal sleeve even at $10K liquid. Atlas's skills are written as principles (CFO_CANON + SKILL.md pattern) for the same reason Dalio wrote Principles down.
- **Anti-pattern**: 60/40 as default without regime awareness. 60/40 lost 18% in real terms in 2022 because both sleeves were short-duration fragility in a rising-rate regime.

### 9. **Peter Bernstein — Against the Gods (risk as a concept)**
- Book: *Against the Gods: The Remarkable Story of Risk* (1996).
- **Core idea**: risk is the thing we don't yet know how to price. Probability and statistics are tools to bring some of the unknown into the known. The rest stays unknown — that is the permanent residual.
- **Historical lesson**: every era thought it had risk figured out, right until it didn't (Long-Term Capital, 2008, 2020). Humility is a core competency of the CFO.
- **Insurance thinking**: separate insurable risks (frequency-based) from uninsurable ones (tail events). Different instruments address each.
- **Apply**: Atlas builds scenarios, not point estimates. Every projection is a range with stated confidence. Atlas never says "this will return X%" — it says "base case X, bear Y, bull Z, assumptions stated."
- **Anti-pattern**: Monte Carlo with Gaussian assumptions. Bernstein + Taleb both warn: the tails are fatter than the models.

### 10. **Nassim Taleb (again) — Skin in the Game + ethics of financial advice**
- Book: *Skin in the Game* (2018).
- **Core idea**: never trust an advisor who doesn't bear the consequences of their advice. Agency problems destroy value. The best financial advice comes from people who have made AND lost real money — not credentialed commentators.
- **Asymmetric information ethics**: don't recommend what you wouldn't own yourself in the same situation.
- **Apply**: Atlas's recommendations to the operator are recommendations Atlas would make to itself. If a pick fails the "would I put my own capital into this at this size?" test, Atlas downgrades it.
- **Anti-pattern**: "this is risky for you but low-risk for us" (most brokers). Aligned incentives > clever incentives.

---

## The Next Tier (working knowledge — reference on demand)

- **Burton Malkiel** — *A Random Walk Down Wall Street*. Indexing as the default, active as the exception. Humility counterbalance to conviction-based picking.
- **John Bogle** — *The Little Book of Common Sense Investing*. Cost minimization as the dominant predictable edge.
- **Joel Greenblatt** — *The Little Book That Beats the Market*. Magic Formula (ROIC + earnings yield). Decent screen, not a complete thesis.
- **Charlie Munger (direct)** — *Psychology of Human Misjudgment*. 25 biases every operator must know before allocating.
- **Daniel Kahneman** — *Thinking, Fast and Slow*. System 1 / System 2, loss aversion, anchoring. The operator's own brain is often the biggest risk.
- **Mary Buffett & David Clark** — *Buffettology*. Readable translation of Buffett's methodology for operators learning the framework.
- **Preston Pysh / The Investor's Podcast** — Buffett-Munger applied interviews; useful scuttlebutt for names on the research shortlist.
- **Morgan Housel** — *The Psychology of Money*. Behavior > strategy. The operator who never blows up wins.
- **Aswath Damodaran** — *Investment Valuation* + NYU lectures. The canonical DCF + valuation source. Slow but rigorous.
- **Michael Mauboussin** — *The Success Equation*, *Expectations Investing*. Skill vs luck in investing. Probability thinking.
- **Jim Collins** (of *Good to Great*) — also *Stockpicking with Jim Collins* frameworks on flywheel economics. The operator's business side of CFO work.
- **Robert Shiller** — *Irrational Exuberance*. CAPE ratio and long-run valuation anchors.
- **David Swensen** — *Pioneering Portfolio Management*. Endowment model for portfolios with real long-term horizon.

### Tax-specific next-tier
- **Jamie Golombek** (CIBC) — most readable Canadian personal-tax commentary. RRSP/TFSA/FHSA reader-level analyses.
- **Tim Cestnick** — *Winning the Tax Game*. Practical Canadian tax optimization, annual edition.
- **KPMG Canadian Tax Facts** — authoritative tax table reference, updated annually.
- **The Accountant Beside You** series — small-business bookkeeping operational.

---

## Knowledge Frontier (added 2026-04-19, self-improvement cycle 2)

Theories and frameworks being integrated as Atlas's advisory scope widens. Each entry names the canonical source and the practical decision it unlocks. Promoted to full pillar if applied 3+ times with validated outcomes; see [[PATTERNS]] for the promotion ledger.

### Capital structure — the trade-off the CFO owns

- **Modigliani-Miller (1958, 1963)** — the original "capital structure is irrelevant in a frictionless world" proof, corrected for tax shields. Unlocks: the real-world decision of how much debt a CCPC should carry once it exists, given Canadian interest-deductibility under s.20(1)(c) and the tax shield from leverage.
- **Pecking Order Theory (Myers-Majluf, 1984)** — under asymmetric information, firms prefer internal funds → debt → equity in that order. Unlocks: for OASIS, retained earnings before any external financing; if external, prefer debt before diluting CC's ownership.
- **Trade-off Theory (Kraus-Litzenberger, 1973)** — optimal leverage balances tax-shield benefit against bankruptcy-cost risk. Unlocks: target debt/EBITDA ratio once OASIS has stable cashflow. For services businesses: low target (< 2x). For cash-cow SaaS with contracted MRR: moderate (2-3x).

### Portfolio theory — and the cases it breaks

- **Harry Markowitz — Modern Portfolio Theory (1952)** — mean-variance optimization, efficient frontier, the case for diversification. Unlocks: the portfolio-construction baseline. Caveats: assumes normally distributed returns; crypto and tails break this (see [[CFO_CANON]] § Taleb).
- **William Sharpe — CAPM (1964)** — expected return = rf + β × (Rm - rf). Unlocks: a first-pass discount rate for DCFs and a sanity check on whether a pick compensates for its systematic risk.
- **Fama-French 3-Factor (1993) + 5-Factor (2015)** — size, value, profitability, investment quality added to market beta. Unlocks: factor-based screening beyond raw ratios. Caveats: factor returns are cyclical and sometimes decade-long negative (value from 2010-2020).

### Behavioral finance — formally

- **Daniel Kahneman & Amos Tversky — Prospect Theory (1979)** — losses feel ~2× as bad as equivalent gains feel good. Reference-dependence, loss aversion, probability weighting. Unlocks: a formal lens for every CC decision — "are we anchored to the wrong reference point?" and "are we overweighting a 2% tail?" Directly wired into [[skills/behavioral-finance-guard/SKILL|behavioral-finance-guard]].
- **Richard Thaler — Mental Accounting (1985) + Nudge (2008)** — people treat money differently by "mental bucket" (bonus money vs salary, tax refund vs earned). Unlocks: calling out when CC is treating a windfall like "play money." Structural nudges (auto-save, default TFSA contribution cadence) beat willpower.

### Working capital + cashflow

- **Cash Conversion Cycle (DSO + DIO - DPO)** — days sales outstanding + days inventory outstanding − days payable outstanding. Unlocks: for OASIS, DIO is ~0 (no inventory). DSO matters most — Wise-paid clients = 0-3 DSO, Stripe = 0 DSO, Bennett Wise link = ~instant. Keep DSO < 30 always; factor if it drifts higher.
- **Greg Crabtree — *Simple Numbers, Straight Talk, Big Profits* (2011)** — for service businesses: salary cap rule (owner pay ≤ 33% of gross profit until business is debt-free), labor efficiency ratio (gross margin / total labor). Unlocks: when CC starts paying himself formally (post-CCPC), the ratio that keeps the business healthy.
- **Mike Michalowicz — *Profit First* (2017)** — pay yourself first via structural % allocation across 5 accounts (Income, Profit, Owner Comp, Tax, OpEx). Unlocks: when CC's revenue stabilizes, this is the envelope system to impose Parkinson's-Law discipline on spend.

### Growth investing methodologies

- **William O'Neil — CAN SLIM (1984, 2009)** — Current earnings, Annual earnings, New product/management, Supply-demand, Leader-laggard, Institutional sponsorship, Market direction. Unlocks: a complementary screen to Buffett — catches growth leaders Buffett would skip on P/E.
- **Mary Buffett & David Clark — Interpretive Buffettology** — practitioner's translation of Warren's letters into repeatable screens. Unlocks: readable teaching material for CC while learning.
- **Peter Lynch — *One Up on Wall Street* (1989)** — six-category stock taxonomy (slow growers, stalwarts, fast growers, cyclicals, turnarounds, asset plays). Each category demands a different valuation lens. Unlocks: avoiding the category error of valuing a fast grower like a stalwart (or vice versa).

### International tax frontier

- **OECD BEPS 2.0 — Pillar 1 + Pillar 2 (2021-2024)** — 15% global minimum corporate rate for MNCs > €750M revenue. Unlocks: a ceiling on how much Crown Dependencies optimization matters at scale. CC's ladder targets < €750M revenue so Pillar 2 doesn't bite — but should be monitored as thresholds tend downward over time.
- **CRS (Common Reporting Standard, 2014)** — automatic exchange of financial account info across 120+ jurisdictions. Unlocks: a reminder that "offshore" is not "hidden." Every structure must be openly reportable and substance-backed.
- **FATCA (2010)** — US-tax-person reporting. Unlocks: mostly not CC-applicable (he is not a US person), but matters if he ever marries/greencards into the US system.
- **Henley & Partners Passport Index + Residence-by-Investment reports** — quarterly updates on passport-strength rankings + legal RBI programs. Unlocks: data-driven prioritization of the Irish-passport push vs alternatives.

### Operational finance discipline

- **Luca Pacioli — *Summa de Arithmetica* (1494)** — the invention of double-entry bookkeeping. Every transaction affects two accounts. Unlocks: the epistemic foundation — if the books don't balance, something is wrong before you argue about strategy. See [[CFO_CANON]] § CPA Canada for the modern practice.
- **Michael Porter — *Competitive Strategy* (1980) + *Competitive Advantage* (1985)** — Five Forces, generic strategies (cost leadership, differentiation, focus), value chain. Unlocks: the frame Buffett's "moat" actually derives from. When analyzing a stock, a Porter 5-Forces decomposition grounds the moat narrative in structural economics.
- **Warren Bennis / Jim Collins — *Good to Great* (2001)** — Level 5 leadership, hedgehog concept, flywheel, doom loop. Unlocks: the qualitative screen on management quality Buffett and Fisher both use but rarely formalize.

### Research-frontier watchlist (not-yet-integrated)

These are on Atlas's reading list. Integration pending practical application opportunity. Logged in [[RESEARCH_FRONTIER]].
- **Hyman Minsky — *Stabilizing an Unstable Economy* (1986)** — financial instability hypothesis. Hedge → speculative → Ponzi finance. Relevant when cycle-timing real-estate or macro calls.
- **Andrew Lo — *Adaptive Markets* (2017)** — behavioral-evolutionary synthesis of market behavior. Relevant when rethinking "efficient markets vs Buffett" tension.
- **Perry Mehrling — *The New Lombard Street* (2011)** — the "money view" of finance — dealers, payments, balance-sheet plumbing. Relevant when crypto/stablecoin regulation shifts.
- **Reinhart-Rogoff — *This Time Is Different* (2009)** — eight centuries of financial crises. Relevant for sovereign-risk context when assessing international structures.
- **William N. Goetzmann — *Money Changes Everything* (2016)** — financial history as civilization infrastructure. Foundational reading; not decision-urgent.

---

## Anti-Canon (the bad financial takes to actively reject)

### "Timing the market is impossible — just buy and hold forever"
Partially true (timing precise peaks is hard) but weaponized into "never consider price." Entry price matters. Starting yield matters. Atlas applies Graham's margin-of-safety check before any buy. Not day-trading; just not buying at obvious bubbles.

### "Cash is trash"
Dalio said this once in a specific regime and it became gospel. Cash is optionality. In a rising-rate / inflating environment, cash loses to inflation; in a correcting market, cash buys the dip at 40% off. Atlas holds cash as a position, sized to the opportunity set.

### "Leverage multiplies returns"
It multiplies outcomes, good and bad, and the geometric effect is asymmetric. A 50% drawdown on 2x leverage is ruin. Atlas recommends margin only with explicit modeled worst case and operator confirmation. SOUL Rule #1: never recommend margin debt without modeling ruin.

### "Just invest in what you know"
Peter Lynch's useful heuristic got corrupted into justification for concentration in employer stock or a narrow industry. "Know" must include financials, not just products. Atlas requires both product-level AND financial-level knowledge before concentration.

### "Crypto is the new gold / the future of money"
Maybe, maybe not, but size it like a venture bet, not a savings account. Atlas sizes crypto per Taleb's barbell: small percentage, prepared-to-lose. No leverage. No "all-in" narratives.

### "You should max your RRSP every year"
False for anyone whose marginal rate today is lower than expected retirement marginal rate (most 20-somethings). TFSA beats RRSP until the marginal rate crosses. FHSA beats both for first-home savings. The *right* sequencing depends on income trajectory. Atlas runs the math per operator, not the rule-of-thumb.

### "Don't pay capital gains tax, hold forever"
Partially true but ignores optimization. Tax-loss harvesting, superficial-loss rule navigation, ACB management, disposition timing before tax-rate changes — these are material. Holding forever is a default, not a ceiling.

---

## How Atlas Uses This Canon Operationally

1. **Every stock pick**: Buffett (moat) + Graham (margin of safety) + Marks (second-level thinking) + Fisher (qualitative scuttlebutt) + Taleb (barbell size) are mandatory inputs. The `stock_picker.py` prompt explicitly cites these frames. See also [[skills/position-sizing/SKILL|position-sizing]].
2. **Every tax recommendation**: names the CRA section or folio (canon #4) + passes GAAR (s.245) stress test + has audit paper trail (canon #5). See [[skills/tax-optimization/SKILL|tax-optimization]], [[skills/quarterly-tax-review/SKILL|quarterly-tax-review]], [[TAX_PLAYBOOK_INDEX]].
3. **Every allocation proposal**: Dalio regime awareness + Bernstein scenario ranges + Taleb barbell sizing. See [[skills/portfolio-rebalancing/SKILL|portfolio-rebalancing]].
4. **Every spend gate decision**: Graham margin of safety on LTV:CAC + Buffett durable advantage check + CPA Canada documentation rigor. Implemented by [[skills/unit-economics-validation/SKILL|unit-economics-validation]].
5. **Every behavioral nudge to the operator**: Munger's 25 biases + Kahneman System 1/2 + Housel's "never blow up" framing.

---

## How to Add To This Canon

New frameworks earn a pillar when they:
1. Have survived a full market cycle (not just one bull run)
2. Are cited by existing pillars (e.g., Buffett cites Graham, Munger cites Kahneman — that's the web)
3. Produce repeatable results when applied to Atlas's own decisions
4. Resist fashion — still cited decades after publication

Propose additions in `memory/PATTERNS.md` with evidence; promote after 3 successful applications where the framework produced a decision the operator later validated.

---

## Per-Vertical Canon Extensions

When Business in a Box ships vertical packs, each pack gets a CFO-side sources file:

- **Agency / Services CFO**: Blair Enns (pricing), Mike Michalowicz (*Profit First*), Verne Harnish (scaling up).
- **SaaS CFO**: David Skok (LTV/CAC), Patrick Campbell / ProfitWell (subscription economics), Ben Murray (The SaaS CFO).
- **E-commerce CFO**: Drew Sanocki (contribution margin), Nik Sharma (DTC P&L), Shopify financial model templates.
- **Coaching CFO**: Hormozi (pricing + offers), Dean Graziosi (deferred-revenue accounting).
- **Creator CFO**: Justin Welsh (income smoothing), Joe Pulizzi (content-asset capitalization).
- **Local Service CFO**: Mike Michalowicz (*Profit First* service edition), Joe Crisara (job-costing).

See `skills/verticals/<vertical>/cfo_sources.md` when the packs ship.

---

## The Meta-Rule

> If you can defend your recommendation with one of these frameworks, you're doing finance.
> If you can't, you're doing guessing — however sophisticated it sounds.

Atlas does finance. Never guessing.
