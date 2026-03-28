---
tags: [capabilities, tools]
---

# ATLAS — Capability Registry

> Master index of everything Atlas can do. Updated when new modules ship.

## Capability Counts (2026-03-27, Session 23)

- **Trading Strategies:** 12+ (RSI MR, Donchian, EMA crossover, Bollinger squeeze, VWAP, multi-TF momentum, London breakout, opening range, smart money, Ichimoku, order flow, Z-score, volume profile, RSI divergence, TSMOM, gold pullback)
- **AI Agents:** 10 (4 analysts + debate + risk + portfolio + Darwinian evolution + financial advisor + budget)
- **Finance Modules:** 4 (tax calculator, financial advisor, wealth tracker, budget)
- **Tax/Accounting Documents:** 29 (25 prior + 4 new Session 24: international tax masterplan, crypto tax advanced, Canadian tax loopholes, asset protection masterplan)
- **Brain Files:** 12 (SOUL, USER, STATE, CAPABILITIES, DASHBOARD, GROWTH, RISKS, TAX_PLAYBOOK_INDEX, BRAIN_LOOP, INTERACTION_PROTOCOL, HEARTBEAT, AGENTS)
- **Brokers:** 3 (Kraken/CCXT, OANDA, Alpaca — not configured)
- **Skills:** 11 (accounting-advisor, tax-optimization, financial-planning, quarterly-tax-review, tax-loss-harvesting, departure-tax-planning, portfolio-rebalancing, position-sizing, trade-protocol, income-tier-monitoring, crypto-acb-tracking)
- **Memory Files:** 7 (SESSION_LOG, MISTAKES, PATTERNS, DECISIONS, LONG_TERM, SOP_LIBRARY, ACTIVE_TASKS)

## Brain Architecture (Session 23 — Bravo Pattern Adoption)

| File | Purpose | Mutability |
|------|---------|-----------|
| `brain/SOUL.md` | Immutable identity, values, prime directive | CC ONLY |
| `brain/USER.md` | CC's financial profile, citizenship, accounts | Major changes only |
| `brain/STATE.md` | Live operational snapshot | Every session |
| `brain/CAPABILITIES.md` | This file — tool/strategy/doc registry | When tools change |
| `brain/DASHBOARD.md` | Navigation hub | When structure changes |
| `brain/GROWTH.md` | Capability evolution timeline | On milestones |
| `brain/RISKS.md` | Kill switches, position limits, tax risk controls | CC approval |
| `brain/TAX_PLAYBOOK_INDEX.md` | Master index of 25+ tax documents | When docs added |
| `brain/BRAIN_LOOP.md` | 10-step structured reasoning protocol | Semi-mutable |
| `brain/INTERACTION_PROTOCOL.md` | State sync, logging, governance | Semi-mutable |
| `brain/HEARTBEAT.md` | Session-start proactive monitoring | Semi-mutable |
| `brain/AGENTS.md` | Subagent registry and task routing | When agents change |

## Trading Engine

| Module | Location | Purpose |
|--------|----------|---------|
| **Engine** | `core/engine.py` | Main trading loop — 60s ticks, regime-aware |
| **Risk Manager** | `core/risk_manager.py` | Kill switches — 15% DD, 5% daily, 1.5% per-trade |
| **Regime Detector** | `core/regime_detector.py` | BULL/BEAR/CHOPPY/HIGH_VOL classification |
| **Trailing Stops** | `core/trailing_stop.py` | Chandelier, SAR, ATR-trail, composite |
| **Order Executor** | `core/order_executor.py` | Limit orders, 30s timeout |
| **Broker Registry** | `core/broker_registry.py` | Multi-broker routing (Kraken, OANDA, Alpaca) |
| **Correlation Tracker** | `core/correlation_tracker.py` | Rolling 30-day correlation matrix |

## Finance & Accounting

| Module | Location | Purpose |
|--------|----------|---------|
| **CryptoTaxCalculator** | `finance/tax.py` | CRA-accurate capital gains, ACB tracking, T5008/Schedule 3 |
| **FinancialAdvisor** | `finance/advisor.py` | Portfolio analysis, allocation, monthly reviews, emergency plans |
| **WealthTracker** | `finance/wealth_tracker.py` | Net worth snapshots, FIRE calculator, projections |
| **Budget** | `finance/budget.py` | Expense tracking, category breakdown, savings analysis |

## Strategy Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **Trading Algorithm** | `docs/ATLAS_ALGORITHM.md` | THE trading algorithm — every parameter validated |
| **Tax Strategy** | `docs/ATLAS_TAX_STRATEGY.md` | 25-strategy tax playbook — domestic, offshore, shipping, CPA-grade elite (1,663 lines) |
| **Strategy Research** | `docs/STRATEGY_RESEARCH.md` | Deep research — top repos, ML, profitable strategies |
| **IBKR Research** | `docs/IBKR_STRATEGY_RESEARCH.md` | Options, bonds, futures strategies |
| **Commodity/Forex Research** | `docs/COMMODITY_FOREX_STRATEGY_RESEARCH.md` | Top 10 commodity/forex by Sharpe |
| **CRA Crypto Enforcement Intel** | `docs/CRA_CRYPTO_ENFORCEMENT_INTEL.md` | CRA audit program, exchange data orders, TCC case law, DeFi tax, CARF, penalties |
| **DeFi Tax Guide** | `docs/ATLAS_DEFI_TAX_GUIDE.md` | Definitive Canadian DeFi tax treatment — staking (solo/delegated/liquid/re-staking), LP/yield farming, lending/borrowing, NFTs, bridges/wrapping/L2, DAOs/airdrops/forks, CARF, tax planning, CRA enforcement |
| **Incorporation Tax Strategies** | `docs/ATLAS_INCORPORATION_TAX_STRATEGIES.md` | Elite CCPC playbook — RDTOH/ERDTOH, integration analysis, shareholder loans, reasonable salary, AAII/SBD grind, estate freeze (s.85/s.86), QSBC purification |
| **Real Estate Tax Strategy** | `docs/ATLAS_REAL_ESTATE_TAX_STRATEGY.md` | PRE, rental CCA, flipping rules (s.12(12)), REITs, Smith Manoeuvre, LTT, HST, corporate RE, JV vs partnership |
| **Treaty Network & FIRE Strategy** | `docs/ATLAS_TREATY_FIRE_STRATEGY.md` | Canada-US/Barbados/Ireland/UAE treaties, departure tax (s.128.1), FIRE drawdown, OAS/GIS optimization, dividend tax credit arbitrage |
| **Wealth Playbook** | `docs/ATLAS_WEALTH_PLAYBOOK.md` | 10-book strategy extraction (Wheelwright, Chilton, Kiyosaki, KPMG, Stanley, Brown, Clason, Piper, Nolo) + billionaire tactics (Buy/Borrow/Die, Thiel TFSA, Walton estate freeze, Buffett unrealized gains). 50+ actionable strategies with NOW/FUTURE tags, ITA refs, dollar impacts. |
| **Business Structures** | `docs/ATLAS_BUSINESS_STRUCTURES.md` | Entity types (CA/US/UK/SG/Dubai/Estonia/Georgia/Labuan), incorporation process, multi-entity architectures, banking |
| **Deductions Masterlist** | `docs/ATLAS_DEDUCTIONS_MASTERLIST.md` | 30-item checklist: obscure federal deductions (s.62 moving, DTC mental health, s.20(1)(c) interest, stock options), Ontario credits (OIDMTC 40%, SR&ED+OITC 43%, co-op), creative strategies (family salaries, bad debts, prepaid timing), month-by-month tax calendar, CRA audit risk factors |
| **Insurance, Estate & Asset Protection** | `docs/ATLAS_INSURANCE_ESTATE_PROTECTION.md` | COLI/insured retirement, disability/CI insurance, HSA, wills/POA, probate avoidance (multiple wills), OpCo/HoldCo, crypto estate planning, creditor protection |
| **CRA Audit Defense** | `docs/ATLAS_CRA_AUDIT_DEFENSE.md` | Complete "when CRA comes knocking" playbook — audit selection/types, s.231 powers, Taxpayer Bill of Rights, VDP, Notice of Objection (s.165), Tax Court (informal/general), collections/garnishment, audit-proofing, crypto characterization, key case law (Stewart, Venne, Friedberg) |
| **Government Grants Playbook** | `docs/ATLAS_GOVERNMENT_GRANTS.md` | 30+ federal/provincial/municipal/AI programs — CSBFP $1M, Futurpreneur $60K, IRAP $500K, OIDMTC 35%, SR&ED 43%, Starter Company $5K, cloud credits $450K, accelerators (CDL, YC, Techstars). Stacking strategy: $425K-$700K accessible Year 1. Step-by-step for top 5 programs. |
| **AI/SaaS Tax Guide** | `docs/ATLAS_AI_SAAS_TAX_GUIDE.md` | SaaS revenue recognition (s.12(1)(a), s.20(1)(m) reserves), IP tax treatment (CCA classes, SR&ED 43%), DST, AI training cost deductions, international SaaS (treaty, PE, MoR), contractor vs employee (Wiebe Door), SaaS metrics driving tax planning (PSB risk, incorporation triggers, installments) |
| **Pension & Retirement Optimization** | `docs/ATLAS_PENSION_RETIREMENT_GUIDE.md` | CPP deep optimization (timing/sharing/PRB/CRDO/disability), OAS mastery (clawback avoidance, deferral), GIS hidden wealth strategy (deplete RRSP before 65), RRSP/RRIF meltdown, pension splitting (s.60.03), 6-layer retirement income stack, CC-specific 20-year FIRE timeline |
| **Alternative Investments & Exempt Market** | `docs/ATLAS_ALTERNATIVE_INVESTMENTS.md` | Accredited investor (NI 45-106), angel/VC (ABIL/LCGE/s.44.1), flow-through shares, MICs (s.130.1), private credit, farmland, gold, art (LPP), cultural property donation, LSVCCs, crypto ETFs in TFSA, SR&ED partnerships, CC's deployment roadmap |
| **Debt Optimization & Leverage Strategy** | `docs/ATLAS_DEBT_LEVERAGE_STRATEGY.md` | OSAP/RAP optimization, s.20(1)(c) interest deductibility, Smith Manoeuvre, Singleton Shuffle, CSBFP/BDC business loans, margin tax treatment, mortgage optimization (fixed/variable/CMHC/prepayment), credit score building, FHSA+HBP $100K home strategy, debt payoff methods, s.80 forgiven debt, director liability s.227.1 |
| **Bookkeeping & Financial Systems** | `docs/ATLAS_BOOKKEEPING_SYSTEMS.md` | T2125-aligned chart of accounts, software comparison (Wave/QBO/FreshBooks/Xero/Sage), automation stack (bank feeds, receipts, invoicing, crypto tracking, HST filing, payroll), bank account structure, monthly/quarterly routines, CRA document retention (6-year rules), KPIs and CFO report template |
| **Wealth Psychology** | `docs/ATLAS_WEALTH_PSYCHOLOGY.md` | Behavioral finance operating system — 8 cognitive biases mapped to ATLAS mitigations, wealth psychology frameworks (Housel, Clear, Stoic, hedonic adaptation), 7 decision frameworks (EV thinking, inversion, regret minimization, optionality, margin of safety), 22-year-old compounding math, wealth protection (lifestyle inflation, insurance, fraud, relationships), ATLAS as behavioral guardrail |

## Broker Connections

| Broker | Module | Markets | Status |
|--------|--------|---------|--------|
| **Kraken** | CCXT (async) | Crypto (BTC, ETH, SOL, XRP, etc.) | LIVE |
| **OANDA** | oandapyV20 + BrokerAdapter | Forex, Gold, Silver | LIVE |
| **Alpaca** | alpaca-py | US Equities | NOT CONFIGURED |

## Integrations

| Integration | Purpose | Status |
|-------------|---------|--------|
| **Telegram Bot** | 12 commands — balance, positions, alerts | OPERATIONAL |
| **CRA Tax Engine** | Capital gains, ACB, quarterly estimates, deductions | CODE COMPLETE |
| **Anthropic Claude** | AI agents, financial advisor, budget analysis | ACTIVE |

## Skills (Domain Knowledge)

| Skill | Location | Triggers |
|-------|----------|----------|
| **Accounting Advisor** | `skills/accounting-advisor/SKILL.md` | tax, accounting, CRA, T2125, deduction |
| **Tax Optimization** | `skills/tax-optimization/SKILL.md` | TFSA, RRSP, FHSA, tax-loss harvest, crypto tax |
| **Financial Planning** | `skills/financial-planning/SKILL.md` | budget, FIRE, net worth, savings, allocation |
| **Quarterly Tax Review** | `skills/quarterly-tax-review/SKILL.md` | quarterly review, installments, Q1-Q4 cycle |
| **Tax-Loss Harvesting** | `skills/tax-loss-harvesting/SKILL.md` | unrealized losses, superficial loss, Q4 harvest |
| **Departure Tax Planning** | `skills/departure-tax-planning/SKILL.md` | s.128.1, Crown Dependencies, exit strategy |
| **Portfolio Rebalancing** | `skills/portfolio-rebalancing/SKILL.md` | rebalance, allocation, account placement |
| **Position Sizing** | `skills/position-sizing/SKILL.md` | position size, Kelly, risk budget, micro account |
| **Trade Protocol** | `skills/trade-protocol/SKILL.md` | trade decision, 10-step, regime, confluence |
| **Income Tier Monitoring** | `skills/income-tier-monitoring/SKILL.md` | income tier, threshold, CCPC trigger, HST |
| **Crypto ACB Tracking** | `skills/crypto-acb-tracking/SKILL.md` | ACB, cost basis, superficial loss, CRA crypto |

## Cross-Project Integration (Bravo — CEO)

| Resource | Path | Purpose |
|----------|------|---------|
| CC's Profile | `C:\Users\User\Business-Empire-Agent\brain\USER.md` | CC's identity, business portfolio, preferences |
| Business State | `C:\Users\User\Business-Empire-Agent\brain\STATE.md` | Current operational state, MRR tracking, infrastructure status |
| Active Tasks | `C:\Users\User\Business-Empire-Agent\memory\ACTIVE_TASKS.md` | What CC is working on across all brands |
| Session Log | `C:\Users\User\Business-Empire-Agent\memory\SESSION_LOG.md` | Recent work done by all agents |
| Patterns | `C:\Users\User\Business-Empire-Agent\memory\PATTERNS.md` | Proven approaches and lessons learned |
| Mistakes | `C:\Users\User\Business-Empire-Agent\memory\MISTAKES.md` | Known failure modes and prevention |
| Skills Library | `C:\Users\User\Business-Empire-Agent\skills/` | 50+ skills (debugging, TDD, browser automation, etc.) |

**Rule:** READ only. Never write to Business-Empire-Agent files from Atlas.
