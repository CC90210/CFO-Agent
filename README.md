# ATLAS — Autonomous CFO, Trading & Tax Intelligence System

> **ATLAS** (Autonomous Trading & Leverage Acquisition System) is an AI-powered CFO agent that combines autonomous trading, tax strategy, accounting, wealth management, and financial literacy into a single system. Built by [OASIS AI Solutions](https://github.com/OasisAIolutions).

**This is not a chatbot.** ATLAS is backed by 80,000+ lines of pre-researched, ITA-section-referenced, case-law-cited financial intelligence across 59 documents — the equivalent of a senior accountant, portfolio manager, and wealth advisor working together 24/7.

---

## What ATLAS Does

### CFO & Accounting (59 docs, 80,738 lines)
- **Tax Preparation** — Prepares T1, T2125 (self-employment), Schedule 3 (capital gains), HST returns with 200+ ITA sections referenced
- **25 Tax Strategies** — From basic deductions to CPA-grade elite strategies (SR&ED 43%, estate freeze, LCGE multiplication, OpCo/HoldCo)
- **Crypto Tax** — ACB tracking, staking/LP/yield farming, CRA enforcement intelligence, CARF 2026 compliance
- **International Tax** — 94+ treaty network, Crown Dependencies (0% CGT), transfer pricing (OECD methods), BEPS Pillar Two
- **Business Valuation & M&A** — DCF, comps, s.85/86/87/88 rollovers, butterfly transactions, pipeline planning
- **Forensic Accounting** — Beneish M-Score, Benford's Law, Altman Z-Score, GAAR case law, fraud detection
- **Trust Taxation** — 10 trust types, 21-year rule, prescribed rate loans, Henson trusts, LCGE multiplication
- **Every CCA Class (1-56)** — Immediate expensing, AII, vehicle CCA, rental restrictions
- **Platform Economy** — Tax rules for Uber, Airbnb, DoorDash, Etsy, YouTube, Twitch, OnlyFans, Upwork
- **Charitable Giving** — Securities donation (zero capital gains), DAFs, private foundations, billionaire strategies
- **Departure Tax** — Complete Canada exit playbook, tie-severing checklist, IoM/Guernsey/Ireland comparison
- **Professional Corporations** — Doctor/lawyer/CPA corps, IPP, RCA, GP/LP/LLP/JV partnerships
- **Financial Literacy** — 115 wealth principles from 50+ books (Buffett, Dalio, Taleb, Housel, Graham, Munger)

### Autonomous Trading (12 strategies, 10 AI agents)
- **12 Regime-Aware Strategies** — RSI mean reversion, EMA crossover, Bollinger squeeze, VWAP bounce, multi-timeframe momentum, London breakout, opening range, Ichimoku trend, smart money concepts, order flow imbalance, Z-score mean reversion, volume profile
- **Multi-Agent Intelligence** — 4 analyst agents (technical, sentiment, fundamentals, news) + bull/bear debate + risk veto + portfolio management + Darwinian self-improvement
- **Risk Management** — Hardcoded kill switches (15% max drawdown, 5% daily loss, 1.5% per-trade), regime detection (BULL/BEAR/CHOPPY/HIGH_VOL), correlation tracking
- **Connected Brokers** — Kraken (crypto), OANDA (gold/forex), Alpaca (US equities)
- **Backtesting** — Walk-forward validation, Monte Carlo simulation, regime-aware filtering

### Wealth Management
- **Hedge Fund Strategies** — 17 strategies documented (L/S equity, global macro, stat arb, trend following, volatility trading, distressed debt, multi-strategy pod model)
- **13 Legendary Investors** — Replicable frameworks from Buffett, Soros, Dalio, Simons, Marks, Lynch, Druckenmiller, Klarman, Burry
- **Portfolio Construction** — MPT, Black-Litterman, risk parity, core-satellite, barbell strategy
- **Canadian Optimization** — TFSA/RRSP/FHSA maximization, Smith Manoeuvre, CPP/OAS/GIS planning, FIRE

### 16 Executable Skills
Automated routines that monitor thresholds and take action:

| Skill | What It Does |
|-------|-------------|
| `accounting-advisor` | CRA filing prep, T2125, Schedule 3, deductions |
| `tax-optimization` | 25-strategy optimizer with dollar impact |
| `financial-planning` | FIRE calculations, net worth projections |
| `quarterly-tax-review` | Q1-Q4 income tracking, installment planning |
| `tax-loss-harvesting` | Unrealized loss flagging, superficial loss detection |
| `departure-tax-planning` | Canada exit strategy, s.128.1 calculations |
| `compliance-monitor` | Deadline tracking, red flag alerts |
| `incorporation-readiness` | $80K trigger analysis, cost-benefit |
| `cross-border-compliance` | W-8BEN, T1135, multi-currency |
| `crypto-acb-tracking` | Weighted-average ACB, Schedule 3 prep |
| `income-tier-monitoring` | Strategy shifts at income thresholds |
| `cash-flow-invoicing` | AR tracking, cash flow forecasting |
| `financial-health-check` | Health score (0-100), benchmarks |
| `portfolio-rebalancing` | Tax-aware rebalancing |
| `position-sizing` | Kelly criterion, risk-budget sizing |
| `trade-protocol` | 10-step trade decision framework |

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/OasisAIolutions/trading-agent.git
cd trading-agent
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys (Anthropic, exchange, Telegram)

# Backtest a strategy
python main.py backtest --strategy ema_crossover --symbol BTC/USDT --start 2024-01-01

# Paper trade (simulated — no real money)
python main.py paper-trade --strategy all --exchange binance

# Multi-agent analysis
python main.py analyze --symbol BTC/USDT

# Standalone paper trading dashboard
python paper_trade.py

# Live trading (DANGEROUS — requires explicit flags)
python main.py live --strategy momentum --exchange binance --confirm-live
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ATLAS BRAIN                               │
│  brain/SOUL.md → brain/USER.md → brain/STATE.md                 │
│  12 brain files | 16 skills | 59 docs (80,738 lines)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   TRADING     │  │   FINANCE    │  │   TAX & ACCOUNTING    │  │
│  │              │  │              │  │                       │  │
│  │ 12 Strategies │  │ Tax Calc     │  │ 59 Reference Docs     │  │
│  │ 10 AI Agents  │  │ Advisor      │  │ 16 Executable Skills  │  │
│  │ Risk Manager  │  │ Wealth Track │  │ 125+ Quick Lookups    │  │
│  │ Regime Detect │  │ Budget       │  │ 200+ ITA Sections     │  │
│  │ Trailing Stop │  │              │  │ 19+ Jurisdictions     │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────┘  │
│         │                 │                       │              │
│  ┌──────┴─────────────────┴───────────────────────┴──────────┐  │
│  │                    CONNECTED SERVICES                      │  │
│  │  Kraken (crypto) | OANDA (gold/forex) | Alpaca (equities) │  │
│  │  Telegram Bot (12 commands) | Claude API (agents)          │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Document Library (59 docs, 80,738 lines)

The full index is in [`brain/TAX_PLAYBOOK_INDEX.md`](brain/TAX_PLAYBOOK_INDEX.md) with 125+ quick-lookup entries.

### By Category

| Category | Docs | Lines | Coverage |
|----------|------|-------|----------|
| Core Tax Strategy | 3 | 4,100+ | 25-strategy playbook, income scaling, deductions |
| Crypto & DeFi | 4 | 3,400+ | ACB, staking, LP, NFTs, CARF, CRA enforcement |
| International Tax | 7 | 9,700+ | Treaties, Crown Dependencies, transfer pricing, BEPS |
| Incorporation & Corporate | 3 | 3,100+ | CCPC, RDTOH, TOSI, estate freeze |
| Compliance & Audit | 5 | 4,700+ | CRA risk scoring, VDP, installments, HST |
| Business Valuation & M&A | 1 | 2,629 | DCF, comps, s.85/86/87/88, butterfly |
| Forensic Accounting | 1 | 2,520 | Beneish, Benford, Altman, GAAR, fraud cases |
| Trust & Family Planning | 1 | 2,224 | 10 trust types, 21-year rule, RESP/RDSP |
| CCA & Depreciation | 1 | 1,835 | Every CCA class (1-56), AII, immediate expensing |
| Platform Economy | 1 | 1,653 | Uber, Airbnb, YouTube, DoorDash, Etsy, OnlyFans |
| Hedge Funds & Wealth Mgmt | 1 | 2,055 | 17 strategies, 13 legendary investors |
| Financial Literacy | 1 | 2,714 | 115 principles from 50+ books |
| Professional Corps & Partnerships | 1 | 2,201 | Doctor/lawyer corps, GP/LP/LLP/JV |
| Automobile Expenses | 1 | 1,969 | Vehicle CCA, logbook, EV strategy |
| Charitable Giving | 1 | 983 | Securities donation, DAFs, foundations |
| Digital Nomad & Departure | 1 | 1,849 | Canada exit playbook, IoM/Guernsey/Ireland |
| Real Estate | 2 | 1,800+ | PRE, rental CCA, FHSA+HBP, house hacking |
| Retirement & Pension | 2 | 1,900+ | CPP/OAS/GIS, RRSP meltdown, estate protection |
| Estate & Succession | 1 | 1,503 | Wills, probate, LCGE, digital assets |
| SaaS/AI Business | 3 | 4,500+ | SR&ED, SaaS metrics, AI regulation |
| And 15+ more... | | | Debt, insurance, payroll, negotiation, grants, etc. |

### Referenced Sources
- **75+ Books** — Graham, Buffett, Dalio, Soros, Taleb, Housel, Klarman, Lynch, Marks, Munger, and more
- **200+ ITA Sections** — Every relevant section of Canada's Income Tax Act
- **Case Law** — Canada Trustco, Copthorne, Alta Energy, Singleton, Neuman, Stewart, Henderson Estate
- **CRA Guidance** — Interpretation Bulletins, Information Circulars, CRA guides
- **OECD** — Transfer pricing guidelines, BEPS actions, Pillar One/Two

---

## Trading Strategies (12)

| Strategy | Type | Best Regime | Timeframe |
|----------|------|-------------|-----------|
| EMA Crossover | Momentum | Trending | 1H-4H |
| RSI Mean Reversion | Mean Reversion | Range-bound | 15m-1H |
| Bollinger Squeeze | Breakout | Low volatility | 1H-4H |
| VWAP Bounce | Intraday | High volume | 5m-15m |
| Multi-Timeframe | Confluence | Any | 15m+4H+1D |
| London Breakout | Session | London open | 15m |
| Opening Range | Session | US open | 5m |
| Ichimoku Trend | Trend Following | Strong trends | 4H-1D |
| Smart Money Concepts | Order Flow | Any | 15m-1H |
| Order Flow Imbalance | CVD Divergence | High volume | 5m-1H |
| Z-Score Mean Reversion | Statistical | Mean-reverting | 1H-4H |
| Volume Profile | Institutional | Any | 1H-4H |

All strategies are regime-aware — the regime detector classifies markets as BULL/BEAR/CHOPPY/HIGH_VOL and adjusts strategy weights accordingly.

---

## Safety Rails (Non-Negotiable)

Hardcoded at module level — cannot be overridden by config or agents:

| Rule | Limit | Effect |
|------|-------|--------|
| Max Drawdown | 15% | ALL trading halted |
| Daily Loss | 5% | Stop for the day |
| Per-Trade Risk | 1.5% | Maximum risk per position |
| Max Open Positions | 5 | Concentration limit |
| Max Single Asset | 20% | Diversification floor |
| Min Conviction | 0.3 | 30%+ confidence required |
| Volatility Halving | 2x ATR | Position sizes halved in high-vol |

---

## Project Structure

```
trading-agent/
├── main.py                     # CLI entry point
├── paper_trade.py              # Standalone paper trading dashboard
├── analyze.py                  # Standalone analysis tool
│
├── brain/                      # Intelligence layer (12 files)
│   ├── SOUL.md                 # Immutable identity and values
│   ├── USER.md                 # User financial profile
│   ├── STATE.md                # Operational state snapshot
│   ├── CAPABILITIES.md         # Master tool/strategy registry
│   ├── DASHBOARD.md            # Navigation hub
│   ├── TAX_PLAYBOOK_INDEX.md   # 59-doc index with 125+ lookups
│   ├── GROWTH.md               # Evolution timeline
│   ├── RISKS.md                # Kill switches and risk controls
│   ├── BRAIN_LOOP.md           # 10-step reasoning protocol
│   ├── INTERACTION_PROTOCOL.md # State sync and governance
│   ├── HEARTBEAT.md            # Proactive monitoring
│   └── AGENTS.md               # Task routing
│
├── docs/                       # 59 reference documents (80,738 lines)
│   ├── ATLAS_TAX_STRATEGY.md              # Core 25-strategy playbook
│   ├── ATLAS_BUSINESS_VALUATION_MA.md     # DCF, M&A, s.85/86/87/88
│   ├── ATLAS_FORENSIC_ACCOUNTING_FRAUD.md # Beneish, Benford, GAAR
│   ├── ATLAS_FINANCIAL_LITERACY_MASTERCLASS.md  # 115 principles, 50+ books
│   ├── ATLAS_HEDGE_FUND_WEALTH_MANAGEMENT.md    # 17 strategies, 13 investors
│   └── ... (54 more — see brain/TAX_PLAYBOOK_INDEX.md)
│
├── skills/                     # 16 executable CFO skills
│   ├── accounting-advisor/     # CRA filing prep
│   ├── tax-optimization/       # 25-strategy optimizer
│   ├── compliance-monitor/     # Deadline and threshold alerts
│   └── ... (13 more)
│
├── strategies/                 # 12 trading strategies
│   ├── base.py                 # BaseStrategy ABC + registry
│   └── technical/              # All strategy implementations
│
├── agents/                     # 10 AI agents
│   ├── orchestrator.py         # Parallel agent coordination
│   ├── darwinian.py            # Self-improving evolution
│   └── ...                     # Analysts, debate, risk, portfolio
│
├── core/                       # Trading engine
│   ├── engine.py               # Main trading loop
│   ├── risk_manager.py         # Kill switches (hardcoded)
│   ├── regime_detector.py      # BULL/BEAR/CHOPPY/HIGH_VOL
│   ├── correlation_tracker.py  # Rolling correlation matrix
│   ├── trade_protocol.py       # 10-step decision framework
│   ├── trailing_stop.py        # Chandelier, SAR, ATR-trail
│   └── order_executor.py       # Live + paper execution
│
├── finance/                    # Financial modules
│   ├── tax.py                  # CRA-accurate tax calculator
│   ├── advisor.py              # Claude-powered financial advisor
│   ├── wealth_tracker.py       # Net worth + FIRE calculator
│   └── budget.py               # Expense tracking
│
├── backtesting/                # Backtest engine
│   ├── engine.py               # Bar-by-bar simulation
│   ├── walk_forward.py         # Overfitting prevention
│   └── monte_carlo.py          # Probability of ruin
│
├── config/                     # Configuration
│   ├── settings.py             # Pydantic-validated settings
│   └── strategies.yaml         # Strategy parameters
│
├── data/                       # Market data
├── db/                         # SQLAlchemy models
├── utils/                      # Logging, Telegram, market hours
├── memory/                     # Operational memory
└── tests/                      # 140+ tests
```

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=       # Claude API for agent intelligence
EXCHANGE_API_KEY=        # Kraken API key
EXCHANGE_SECRET=         # Kraken API secret
OANDA_ACCOUNT_ID=        # OANDA trading account
OANDA_API_KEY=           # OANDA API token
TELEGRAM_BOT_TOKEN=      # Telegram bot for alerts
TELEGRAM_CHAT_ID=        # Telegram chat ID
PAPER_TRADE=true         # Must be false + CONFIRM_LIVE=true for live
```

---

## Who Built This

**ATLAS** is built and maintained by **Conaugh McKenna** at **OASIS AI Solutions** (Collingwood, Ontario, Canada).

ATLAS operates as CC's autonomous CFO — trading, tax optimization, accounting, wealth management, and financial strategy. It is one half of a two-agent system:
- **ATLAS** (this repo) — CFO: finance, trading, tax, accounting
- **Bravo** (separate repo) — CEO: business operations, client acquisition, content

---

## License

Private - Conaugh McKenna / OASIS AI Solutions
