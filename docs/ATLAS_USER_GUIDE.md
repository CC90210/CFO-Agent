# ATLAS — Personal CFO Agent User Guide

**Version:** 2.0  
**Last Updated:** 2026-04-14  
**Target Audience:** Self-employed founders, solopreneurs, and early-stage entrepreneurs

---

## What Atlas Is

Think of Atlas as a senior portfolio manager, tax strategist, and accountant rolled into one — except it fits in your repository and costs nothing after initial setup. Atlas is not a trading robot. It does not execute trades automatically. It is an advisor that synthesizes financial data, research, and tax law into plain-English guidance so you can make faster, better money decisions.

Atlas handles four categories of work: personal accounting (net worth, cashflow, receipts), tax strategy (filings, deductions, international structuring), research (stock picks with entry/exit, macro analysis), and financial literacy (wealth principles, FIRE planning). It integrates with your bank APIs, brokerage APIs, Gmail, and Claude AI to produce personalized reports without sending your data to anyone.

---

## The Operator's Shed — Your Toolkit

Imagine Atlas as an operator who works in a shed full of specialized tools. Each tool serves a different purpose, but when properly synchronized, they build something remarkable.

### Money Tools (CFO Module)

These tools handle the numbers that matter: your cash, investments, and runway.

- **Runway Modeler** — How long can you operate in Montreal on current cash? Models 3 scenarios (best/base/worst), tells you breakeven point, projects cash runway
- **Net Worth Dashboard** — Snapshot across all accounts (Kraken, OANDA, Wise, Stripe, banks, registered accounts). Single command shows your total wealth by asset class
- **Receipt Puller** — Scans your Gmail inbox for receipts, categorizes them (meals, software, equipment, travel), exports CSV ready for tax filing. Uses IMAP + OCR heuristics
- **Tax Reserve Calculator** — Based on year-to-date income, estimates quarterly tax you should set aside. Prevents surprises at filing time
- **Budget Tracker** — Monthly expense categorization (rent, food, software, entertainment), spending analysis, savings rate calculation

### Research Tools (Analyst Module)

These tools find investment ideas and track what's moving markets.

- **Stock Picker** — On-demand equity research. You give a theme ("AI infrastructure plays for 6 months"), Atlas synthesizes news + fundamentals + technicals, returns 3-5 picks with conviction scores, entry/exit prices, and specific catalysts
- **News Ingest** — Monitors 15+ finance RSS feeds + Google News + SEC EDGAR. Identifies trends, sector rotations, geopolitical flashpoints that move markets
- **Fundamentals Engine** — Pulls P/E, earnings, revenue growth, margins, insider trades, short interest. Ranks companies by valuation, growth, quality
- **Technicals Analyzer** — 50/200-day moving averages, RSI, MACD, Bollinger bands, volume analysis. Identifies support/resistance levels
- **Macro Watch** — Tracks geopolitical hot spots (Middle East, Ukraine, Taiwan, Fed policy). Tells you which sectors benefit/suffer if situation escalates

### Knowledge Tools (Brain Module)

These are the reference documents and decision frameworks that power everything else.

- **59-Doc Tax Library** — ~80,000 lines covering 25 tax strategies, crypto ACB, Crown Dependencies migration, CCPC incorporation, SR&ED credits, FHSA/TFSA/RRSP mechanics, departure tax, estate freeze, international treaties. Every strategy includes ITA sections, examples, and gotchas
- **16 CFO Skills** — Structured decision frameworks for accounting, tax optimization, financial planning, tax-loss harvesting, departure tax planning, portfolio rebalancing, position sizing, quarterly reviews, compliance monitoring, cash flow forecasting, cross-border tax, and incorporation readiness
- **Financial Literacy Engine** — 115 wealth principles extracted from 50+ books (Wheelwright, Buffett, Kiyosaki, Stanley, etc.). FIRE frameworks. Compounding math for your age and goals
- **Identity & State Files** — Your complete financial profile (accounts, citizenship, income, debt, goals) stays in files that Atlas reads before every interaction. No hallucinations, no asking you questions you already answered

### Interface Tools

These are the entry points: how you talk to Atlas.

- **CLI** — `python main.py runway`, `python main.py networth`, `python main.py picks "AI plays"`. Fast, scriptable, works offline
- **Telegram Bot** — Natural language commands in Telegram. `what's my net worth?` → instant dashboard. `give me NVDA picks` → research runs. 16 commands built in
- **File-Based Prompts** — Drop a markdown file with your question in `prompts/` folder, Atlas reads it and generates a response. Good for complex multi-part questions

### Memory Tools

These track what Atlas has done and learned.

- **Session Log** — Every interaction timestamped (YYYY-MM-DD). Tracks what you asked, what Atlas did, decisions made
- **Mistakes Log** — When something goes wrong, Atlas logs it (root cause + prevention). Prevents the same error twice
- **Patterns Log** — After 3 successful uses of an approach, promoted to a "pattern." Your approved playbook grows over time
- **Decisions Log** — Major choices (incorporation decision, international structure) are logged with context, options considered, why you chose path A over B
- **Long-term Memory** — Quarterly reflections, yearly retrospectives, strategic milestones

---

## End-to-End Workflow

Here's how a natural-language request becomes a decision:

```
You (Telegram)
    ↓
"Am I going to make it in Montreal?"
    ↓
Telegram Bridge (detects intent: cashflow question)
    ↓
Intent Router (routes to CFO module)
    ↓
Cashflow Analyzer
    ├─ reads USER.md (current income, expenses)
    ├─ reads account balances (Wise, RBC, Kraken)
    ├─ reads rent scenarios (solo vs split)
    ├─ models 3 scenarios (best/base/worst case)
    └─ calculates runway in months
    ↓
Claude Synthesis (plain English)
    ├─ "You have $12.8K liquid, $3K MRR, worst-case 4 months."
    ├─ "Best case (new client on Bennett): 7+ months."
    ├─ "Verdict: You're fine. Diversify within 3 months to reduce risk."
    ↓
Telegram Response (instant)
    ↓
Memory Update (session logged)
```

When you ask for stock picks:

```
You (CLI)
    ↓
"python main.py picks 'AI infrastructure 6-12 months'"
    ↓
Stock Picker Agent
    ├─ fetches last 7 days news (Google News, RSS, SEC EDGAR)
    ├─ analyzes macro context (Fed policy, chip cycles, Taiwan risk)
    ├─ screens fundamentals (growth, margins, insider buys)
    ├─ analyzes technicals (50/200 SMA, RSI, volume)
    ├─ Claude synthesizes: 3-5 picks with
    │   ├─ ticker, company name, thesis
    │   ├─ catalysts (earnings, product launch, partnerships)
    │   ├─ conviction (0-10 scale)
    │   ├─ entry price + window (e.g., "NVDA $85-90 within 2 weeks")
    │   ├─ exit target + window (e.g., "$110+ within 6 months")
    │   ├─ stop loss (downside protection)
    │   └─ risks (what could go wrong)
    ├─ picks saved to data/picks/ for tracking
    ↓
CLI Output (clean JSON or markdown)
    ↓
Tax Account Assignment
    ├─ Growth → TFSA (tax-free forever)
    ├─ Dividend/qualified → RRSP (treaty withholding exemption)
    ├─ Short-term spec → non-registered (losses offset gains)
    ↓
You Review & Decide
    └─ You execute trades on your broker. Atlas never touches it.
```

---

## Natural Language Examples

This is what Atlas can do when you just ask.

| You say | Atlas does | Output |
|---------|-----------|--------|
| "am I going to make it in Montreal?" | Runs cashflow analysis, reads runway scenarios, current MRR vs rent | "You have 4-7 months depending on revenue. Breakeven at $2,500/mo. Diversify within 3 months to reduce risk." |
| "what's my net worth?" | Aggregates all accounts (Kraken, OANDA, Wise, RBC, TFSA, RRSP, FHSA) | Single table showing assets by account, liabilities, net worth, change vs last month |
| "give me 3 AI plays for the next 6 months" | News scan → macro analysis → fundamentals screen → technicals → Claude synthesis | 3 tickers with conviction, entry/exit, thesis, catalysts, risk assessment |
| "pull my receipts from January" | IMAP scans Gmail (conaugh@oasisai.work), OCRs, categorizes | CSV file ready to paste into T2125: meals ($342), software ($89), equipment ($0) |
| "what's the Fed doing this week?" | News ingest + macro watch | Plain-English summary of Fed announcements, impact on different asset classes |
| "should I sell my DOGE?" | Reads your Kraken position, cost basis (ACB), current price, tax impact | "Selling now = $X unrealized gain. Hold until next year for tax loss harvesting. Risk: adoption risk remains. Conviction: low (3/10)." |
| "how much tax should I set aside?" | Reads YTD income from all sources, applies Canadian rates (53.53% max Ontario) | "$X should be reserved quarterly. Next payment due [date]. Current reserve: $Y." |
| "deep dive on NVDA" | Analyzes fundamentals (valuation, growth, margins), news (chip cycles, Taiwan, competition), technicals | Bull case ($110+), bear case ($60), base case, catalysts, 18-month outlook, risks |
| "rebalance my portfolio" | Reads all holdings, calculates target allocation, recommends account placement | "Move $X from non-reg to TFSA (tax savings: $Y). Move $Z from RRSP to FHSA (next year's room)." |
| "am I ready to incorporate?" | Reads revenue, checks $80K threshold, models CCPC vs sole prop tax | "Revenue: $Y. At this level, CCPC saves $X/year. Incorporation cost: $2-5K legal. ROI: 2.4 months." |
| "what's my tax bill for 2025?" | Aggregates income (Stripe, Bennett, DJ, Nicky's, crypto trades), applies deductions (home office, equipment, software), calculates liability | "2025 income: $X. Deductions: $Y. Taxable: $Z. Estimated tax: $Amount (rate: 23.4%). File by June 15, 2026." |
| "set up FHSA strategy" | Calculates combined FHSA + RRSP HBP withdrawal | "Contribute $8K/year to FHSA. After 4 years: $32K grows tax-free. HBP: withdraw $35K from RRSP. Total down payment fund: $67K (10-year timeline)." |
| "track my crypto ACB" | Reads all Kraken trades, calculates weighted-average cost basis per coin | "BTC: $X ACB, current: $Y, unrealized: $Z. If you sell, $W tax owing (superficial loss triggered on 3 coins)." |
| "what revenue do I need for Isle of Man?" | Reads UK passport (eligible), models tax at different income levels | "At $120K CAD, Isle of Man saves $18K/year vs Ontario. Requires UK residency. Timeline: 12 months. Departure tax: ~$5K." |

---

## Commands Reference

### CLI Commands

Run these from terminal: `python main.py [command] [options]`

#### Cashflow & Runway

```bash
python main.py runway
```
- **What it does:** Models 3 scenarios (best/base/worst) for Montreal runway
- **Output:** Table showing months until cash runs out, breakeven income, recommended diversification timeline
- **Use case:** Before a big decision (moving, hiring, new software) — verify runway holds
- **Speed:** <2 seconds

```bash
python main.py runway --scenario worst
```
- Detailed worst-case breakdown

---

#### Net Worth

```bash
python main.py networth
```
- **What it does:** Snapshots all account balances in one view
- **Output:** Table by account (Kraken, OANDA, Wise, RBC, Wealthsimple), by asset class (crypto, forex, fiat, equities), subtotals and net worth
- **Use case:** Monthly review, before financial decisions, tracking progress
- **Speed:** <5 seconds (parallel API calls to all brokers)

```bash
python main.py networth --by-account
```
- Breakdown by individual account

```bash
python main.py networth --vs-last-month
```
- Shows change vs previous snapshot

---

#### Receipts & Accounting

```bash
python main.py receipts --since 2026-01-01
```
- **What it does:** Scans Gmail (conaugh@oasisai.work) for receipts since date, OCRs, categorizes
- **Output:** CSV file (receipts.csv) ready for T2125 / bookkeeping entry
- **Categories:** Software, Equipment, Meals, Travel, Office, Subscriptions, Other
- **Use case:** Weekly during month, monthly aggregation before tax prep
- **Speed:** ~10 seconds

```bash
python main.py receipts --category meals
```
- Filter to specific category

```bash
python main.py receipts --since 2026-01-01 --export xlsx
```
- Export to Excel instead of CSV

---

#### Stock Picks & Research

```bash
python main.py picks "AI infrastructure plays for 6-12 months"
```
- **What it does:** Generates 3 stock picks on demand based on your theme
- **Output:** Markdown with ticker, thesis, entry/exit, conviction, catalysts, risks
- **Use case:** When you want new research ideas or second opinion on a sector
- **Speed:** ~15 seconds (news fetching is cached)

```bash
python main.py picks "biotech GLP-1 plays" -n 5
```
- Get 5 picks instead of 3

```bash
python main.py picks "uranium energy plays" --save
```
- Automatically save picks to data/picks/ for tracking vs outcomes

```bash
python main.py picks "defense stocks" --json
```
- Get JSON output instead of markdown (for piping to other tools)

---

#### Deep Dive

```bash
python main.py deepdive NVDA
```
- **What it does:** Multi-layer analysis on one ticker
- **Output:** Fundamentals (P/E, growth, margins), news (last 14 days), technicals (50/200 SMA, RSI, volume), bull case, bear case, base case
- **Use case:** Before entering a position you're unsure about, or quarterly review of holdings
- **Speed:** ~20 seconds

```bash
python main.py deepdive NVDA --save
```
- Save full analysis to data/picks/ for later reference

---

#### Tax & Quarterly Review

```bash
python main.py taxes
```
- **What it does:** Calculates year-to-date tax liability, estimates quarterly payment, suggests deductions you might be missing
- **Output:** Summary of income, deductions, taxable income, estimated tax owing, payment schedule
- **Use case:** Run quarterly (end of Q1, Q2, Q3, Q4) to stay ahead of surprises
- **Speed:** <5 seconds

```bash
python main.py taxes --detailed
```
- Full T2125 preview with line-item breakdown

---

#### Crypto Tax

```bash
python main.py crypto-acb
```
- **What it does:** Calculates ACB (average cost basis) across all Kraken positions, tracks superficial losses (30-day rule), estimates tax on dispositions
- **Output:** Table showing cost basis, current value, unrealized gain/loss per coin, tax impact of selling
- **Use case:** Q4 tax-loss harvesting, before selling a position, quarterly reconciliation
- **Speed:** <5 seconds

---

### Telegram Commands

Message your bot (token in `.env`). All commands start with `/`.

| Command | What it does | Example | Output |
|---------|------------|---------|--------|
| `/networth` | Instant net worth snapshot | `/networth` | "$42,350 total. Kraken: $X. Wise: $Y. RBC: $Z." |
| `/runway` | Quick runway estimate | `/runway` | "4-7 months at current spend. Diversify within 90 days." |
| `/balance [account]` | Single account balance | `/balance kraken` | "Kraken: $133 USD (4 positions: BTC, SOL, LTC, ATOM)" |
| `/positions` | List all open positions | `/positions` | Ticker, entry price, current price, unrealized P&L |
| `/price [ticker]` | Real-time stock/crypto price | `/price NVDA` | "NVDA: $98.50 (↑2.1% today, 52w: $75–$140)" |
| `/news [ticker]` | Last 3 news items | `/news NVDA` | Bulleted summary of recent news |
| `/tax` | Quarterly tax estimate | `/tax` | "YTD income: $X. Reserve: $Y. Next payment: [date]" |
| `/pick [theme]` | Quick pick (1 stock) | `/pick "AI plays"` | "NVDA: 7/10 conviction, entry $90-95, target $110+" |
| `/deepdive [ticker]` | Compact deep dive | `/deepdive NVDA` | 1-page analysis with bull/bear/base cases |
| `/portfolio` | Full holdings view | `/portfolio` | Table of all positions with allocation % |
| `/calendar` | Upcoming events | `/calendar` | Earnings dates, Fed meetings, economic reports (next 2 weeks) |
| `/alert [condition]` | Set price/threshold alert | `/alert NVDA > 100` | "Alert set. I'll notify you when NVDA hits $100+." |
| `/help` | Command list | `/help` | Full list of commands |
| `/status` | System health check | `/status` | API keys working? Data freshness? Next scheduled task? |
| `/log` | Recent activity | `/log` | Last 5 commands run, timestamps |
| `/feedback` | Improvements | `/feedback improve deep_dive` | "Logged. Will be reviewed next session." |

---

## The Personalization Questionnaire

When you first set up Atlas, it needs to know you. This questionnaire auto-populates `brain/USER.md`, which Atlas reads before every interaction.

See `PERSONALIZATION_INTERVIEW.md` for the full interactive version. Here's the summary:

### A. Identity & Citizenship (for tax jurisdiction)

- Legal name, age, current location
- Citizenship(s) held, eligible for (triggers international tax planning)
- Dependents, marital status, province of residence

**Why it matters:** Your province sets your tax rate (from 29.65% to 53.53% when combined with federal). Dual citizenship opens Crown Dependencies (0% corporate, 0% CGT). Irish eligibility (via father) adds 12.5% corporate, 6.25% knowledge box. This is foundational.

### B. Income & Business

- Employment type (employee / sole prop / incorporated / mixed)
- Revenue streams (name, type, monthly estimate, currency, customer concentration)
- Payment processors (Stripe, Wise, PayPal, direct deposit, crypto)
- Incorporation status and timeline plans

**Why it matters:** Income determines tax bracket, installment requirements (at $3K+), HST obligation ($30K+), and incorporation ROI threshold ($80K+). Revenue stream concentration drives diversification priority.

### C. Accounts & Platforms

- Banks (primary + secondary)
- Brokers (stocks, crypto, forex)
- Registered accounts (TFSA, RRSP, FHSA, RESP equivalents)
- Foreign accounts (triggers T1135 or IRS FBAR reporting at $100K+)

**Why it matters:** Atlas reads balances from each account to calculate net worth, runway, and rebalancing recommendations. International accounts trigger tax filing requirements.

### D. Assets & Liabilities

- Cash (by currency and account)
- Investments (by platform)
- Real estate (owned / rented / equity)
- Debts (student loans, credit cards, mortgage)
- Equipment (CCA-eligible: computers, vehicles, cameras)

**Why it matters:** Net worth calculation, tax deductions (CCA, interest), FIRE timeline, and asset protection strategy all depend on knowing what you own and owe.

### E. Tax Situation

- Last return filed (year, method, outcome)
- Current year estimated income
- Expected deduction categories (home office, software, equipment, meals, travel)
- Prior losses / credits carried forward

**Why it matters:** Avoids double-counting deductions, prevents overlapping filings, optimizes credits carryforward, prevents CRA audit triggers.

### F. Risk & Goals

- Risk tolerance (conservative / moderate / aggressive)
- Time horizon (short-term trade / 5-year / 20-year FIRE / retirement)
- Primary goal (wealth building / tax optimization / first home / exit / sell business)
- Near-term concerns (runway, diversification, incorporation, relocation)

**Why it matters:** Determines whether picks are suggested (aggressive growth, small-cap) vs avoided (high-vol crypto). Affects account placement (TFSA for long-term, non-reg for tax losses). Shapes tax strategy (incorporation vs deferral, Crown Dependencies timeline).

### G. Data Access (Optional Automations)

- Gmail app password (for receipt scanning)
- Stripe API key (read-only, for invoice/revenue tracking)
- Wise API key (for cash monitoring)
- Exchange APIs (read-only balance reads)

**Why it matters:** Enables automated receipt ingestion, real-time net worth, and cashflow forecasting. All read-only; Atlas never executes trades or transfers.

### H. Communication Preferences

- Telegram? SMS? Email? Slack?
- Check-in cadence (daily, weekly, monthly, on-request)
- Alert thresholds (e.g., "tell me if runway drops below 3 months")

**Why it matters:** Determines how Atlas proactively surfaces risks and opportunities. Daily check-ins suit traders; monthly suit buy-and-holders.

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- Git
- ~2GB disk space
- API keys for: Anthropic Claude (required), Gmail (optional), Stripe/Wise (optional), exchange APIs (optional)

### Step 1: Clone the Repository

```bash
git clone https://github.com/oasisai/atlas.git
cd atlas
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: Anthropic SDK, CCXT (exchange integration), oandapyV20 (forex), yfinance, Alpha Vantage, FMP, Finnhub, NewsAPI, Telegram, SQLAlchemy, Pydantic, and utilities.

### Step 3: Create `.env` Configuration

```bash
cp .env.example .env
```

Open `.env` and fill in:

**Required:**
```
ANTHROPIC_API_KEY=sk-...          # Claude API key from console.anthropic.com
```

**Optional (enable by filling):**
```
# Gmail receipts
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx     # NOT your normal password

# Brokerage APIs
EXCHANGE_API_KEY=...              # Kraken API public key
EXCHANGE_SECRET=...               # Kraken API secret

OANDA_TOKEN=...                   # OANDA API token
OANDA_ACCOUNT_ID=...              # OANDA account ID

# Research APIs (free tiers)
ALPHA_VANTAGE_KEY=...             # alphavantage.co (25 req/day free)
FINNHUB_KEY=...                   # finnhub.io (60 req/min free)
NEWSAPI_KEY=...                   # newsapi.org (100 req/day free)
FMP_KEY=...                       # financialmodelingprep.com (250 req/day free)

# Telegram bot (optional)
TELEGRAM_BOT_TOKEN=...            # From BotFather on Telegram
TELEGRAM_CHAT_ID=...              # Your Telegram user ID

# Payment processors
STRIPE_API_KEY=...                # Stripe read-only key
WISE_API_TOKEN=...                # Wise API token
```

No `.env` file is committed to the repo — it's in `.gitignore` for security.

### Step 4: Personalization Interview (TODO — CC builds)

Eventually, this command will walk you through the questionnaire and auto-populate `brain/USER.md`:

```bash
python main.py setup
```

For now, manually edit `brain/USER.md` with your details. Template provided.

### Step 5: Verify Installation

```bash
python -c "import cfo.dashboard, research.stock_picker; print('✓ Atlas ready')"
```

### Step 6: First Run — Net Worth

```bash
python main.py networth
```

You should see a table with your account balances. If an API key is missing, it will skip that account gracefully.

### Step 7: Optional — Set Up Telegram Bot

1. Message `@BotFather` on Telegram, create a bot, save token to `.env`
2. Send `/start` to your bot
3. Run: `python telegram_bridge.py` (in separate terminal or as daemon)
4. Try: `/networth` in Telegram

---

## Architecture Overview

### High-Level Module Map

```
atlas/
├── cfo/                          # Financial data aggregation
│   ├── dashboard.py              # Net worth snapshots
│   ├── cashflow.py               # Runway modeling
│   ├── accounts.py               # Balance readers (Kraken, OANDA, Wise, etc.)
│   └── gmail_receipts.py         # IMAP receipt scanner + OCR
│
├── research/                     # Stock picking & analysis
│   ├── stock_picker.py           # Main agent (Claude-powered)
│   ├── news_ingest.py            # RSS + Google News + SEC EDGAR
│   ├── macro_watch.py            # Geopolitical impact analysis
│   ├── fundamentals.py           # Valuation + growth metrics
│   └── prompts/stock_pick.md     # Claude prompt (edit to tune)
│
├── finance/                      # Tax, wealth, budget
│   ├── tax.py                    # CRA-accurate capital gains, ACB
│   ├── advisor.py                # Portfolio analysis & rebalancing
│   ├── wealth_tracker.py         # Net worth tracking, FIRE calc
│   └── budget.py                 # Expense tracking
│
├── brain/                        # Identity & reference
│   ├── USER.md                   # Your complete financial profile
│   ├── SOUL.md                   # Atlas's immutable identity
│   ├── STATE.md                  # Current operational state
│   ├── CAPABILITIES.md           # This tool registry
│   ├── TAX_PLAYBOOK_INDEX.md    # Master index of tax docs
│   └── ... 7 more brain files
│
├── skills/                       # Domain expertise modules
│   ├── accounting-advisor/
│   ├── tax-optimization/
│   ├── financial-planning/
│   ├── quarterly-tax-review/
│   ├── tax-loss-harvesting/
│   ├── ... 11 more skills
│
├── memory/                       # Session logs & learning
│   ├── SESSION_LOG.md            # What Atlas did (timestamped)
│   ├── MISTAKES.md               # Errors & prevention
│   ├── PATTERNS.md               # Approved playbooks
│   ├── DECISIONS.md              # Major choices documented
│   └── ... 3 more memory files
│
├── docs/                         # 59 tax/finance documents
│   ├── ATLAS_TAX_STRATEGY.md
│   ├── ATLAS_ALGORITHM.md
│   ├── ATLAS_INCORPORATION_TAX_STRATEGIES.md
│   ├── ATLAS_CRYPTO_DEFI_TAX_GUIDE.md
│   └── ... 55 more
│
├── config/                       # Settings & strategy params
│   └── settings.py
│
├── utils/                        # Logging, Telegram, market hours
│   ├── telegram.py
│   ├── logger.py
│   └── market_hours.py
│
├── main.py                       # CLI entry point
├── telegram_bridge.py            # Telegram bot dispatcher
├── requirements.txt              # Dependencies
├── .env.example                  # Configuration template
└── .gitignore                    # (includes .env, secrets, cache)
```

### Data Flow

```
USER INPUT (CLI / Telegram / File)
    ↓
INTENT ROUTER
    ├─ "networth" → CFO Dashboard
    ├─ "picks AI plays" → Research StockPicker
    ├─ "tax estimate" → Finance TaxCalculator
    ├─ "rebalance" → Finance Advisor
    ├─ "receipt scan" → CFO GmailReceipts
    └─ "deep dive NVDA" → Research StockPicker
    ↓
MODULE EXECUTION
    ├─ Reads brain/USER.md (context)
    ├─ Reads brain/STATE.md (current state)
    ├─ Fetches data (APIs, cache, files)
    ├─ Applies logic (tax code, valuation models, technicals)
    ├─ Calls Claude for synthesis (complex reasoning)
    ↓
OUTPUT FORMATTING
    ├─ CLI: Plain text / table / JSON
    ├─ Telegram: Concise, bullet-list format
    ├─ File: Markdown / CSV / Excel
    ↓
STATE MANAGEMENT
    ├─ Update brain/STATE.md (last run, next check-in)
    ├─ Append memory/SESSION_LOG.md
    ├─ If error → memory/MISTAKES.md
    ↓
USER SEES RESULT
```

### Synchronization Protocol

**The core rule:** Before every interaction, Atlas reads `brain/USER.md` and `brain/STATE.md`. This prevents drift and hallucinations.

- **brain/USER.md** — Your financial identity (accounts, citizenship, income, debt, goals). Slow-changing. Updated after major life events (relocation, new job, incorporation).
- **brain/STATE.md** — Operational snapshot (last net worth, last tax calc, current runway, upcoming milestones). Updated every session.
- **memory/SESSION_LOG.md** — Every command you run, timestamped, with outcome.
- **memory/MISTAKES.md** — Errors with root causes and prevention tactics.

This architecture prevents:
- Asking you the same question twice
- Recommending actions you've already completed
- Losing context across sessions
- Hallucinating account balances

---

## Product Roadmap

### ✅ Built (v2.0)

- CFO toolkit: net worth, cashflow, runway modeling
- Gmail receipt ingestion → CSV export
- Tax calculator (capital gains, ACB, quarterly estimates)
- 59-doc tax library (~80K lines)
- 16 CFO skills (accounting, tax optimization, financial planning, etc.)
- Research module: stock picker, news ingest, macro watch, fundamentals
- CLI (`main.py`) with 15+ commands
- Telegram bot with 16 natural-language commands
- Brain architecture (USER, SOUL, STATE, CAPABILITIES, etc.)
- Memory system (session logs, mistakes, patterns, decisions)

### 🚧 Beta (in progress)

- Stripe API integration (revenue dashboard)
- Wise API integration (multi-currency cash monitoring)
- Interactive setup wizard (`python main.py setup`) to populate USER.md
- Insider trade tracking (who's buying/selling inside big tech)
- Options flow analysis (institutional positioning)

### 📋 Planned (next quarter)

- **Automated quarterly check-ins** — Atlas proactively alerts you on: runway dropping below 3 months, income tier crossing (CCPC trigger at $80K, HST at $30K), upcoming tax payments, unrealized losses > 5% of portfolio
- **CPA handoff docs** — One-click NETFILE-ready T2125 with all deductions pre-calculated and categorized
- **Portfolio rebalancer** — Auto-suggest rebalancing based on target allocation, new contributions, and tax-loss harvesting opportunities
- **Multi-user mode** — Support multiple family members (spouse, business partners) with role-based access
- **Mobile app** — Lightweight React Native app for net worth / runway / alerts on the go
- **Crypto wallet scanner** — Auto-detect cold wallets (MetaMask, Ledger exports) and add to ACB calculations

---

## Why Buy Atlas?

### The Case

- **80,000+ lines of tax/finance documentation** — Equivalent to hiring a senior CPA part-time ($150/hour × 500+ hours = $75,000 of captured knowledge)
- **16 specialized skills** — Accounting, tax optimization, financial planning, quarterly reviews, rebalancing, position sizing, compliance monitoring, cross-border tax, incorporation readiness, and more
- **Claude-powered research** — Stock picks generated by a senior portfolio manager mindset (conviction scoring, bull/bear/base cases, anti-bullshit filters for meme stocks)
- **Self-hosted** — Your data never leaves your machine. No SaaS subscription fees. No privacy concerns. No vendor lock-in
- **Extensible** — Add your own brokers, APIs, skills, and tax strategies without waiting for vendor updates
- **Transferable** — Own the code. Run it locally, in a container, on a VPS. Version control all updates
- **Compounding** — Every decision Atlas logs becomes a pattern. Every mistake gets prevented next time. The system improves over time
- **Multi-jurisdiction** — Built for Canadian tax law but structured to handle US, UK, Irish, and Crown Dependencies jurisdictions. Global tax treaties included

### The Numbers (CC's Case Study)

- **Tax savings (2026):** $12-18K via CCPC structure + RRSP HBP + FHSA strategy (vs filing without Atlas)
- **Incorporation ROI:** $2K legal cost, saves $18K/year starting year 2 = 11% ROI, breaks even in 1.3 months
- **Crown Dependencies migration:** At $150K+ revenue, moving to Isle of Man (0% corporate, 0% CGT) saves $25-40K/year
- **Time saved:** 20 hours/year on tax prep, 10 hours/year on bookkeeping, 5 hours/month on research = ~100 hours/year = $6K in reclaimed time (at $60/hr)

---

## Licensing & Disclaimers

### License

This repository is provided as-is for educational and personal use. You have the right to use, modify, and extend it for your own financial management.

### Not Financial/Tax/Legal Advice

Atlas synthesizes research and applies tax logic, but:
- Atlas is not a lawyer. Corporate structuring advice should be reviewed by a lawyer.
- Atlas is not a CPA. Tax advice should be reviewed by a CPA before filing.
- Atlas is not a broker. Investment recommendations are educational; you decide whether to trade.
- All picks carry risk of loss. Past performance does not guarantee future results.

### Your Responsibility

- Keep `.env` secrets private. Never commit to version control.
- Verify all numbers before filing or making large financial decisions.
- Use kill switches (drawdown limits, daily loss limits) before any live trading.
- Ensure you have proper business insurance before operating a business.

### Data & Privacy

All data processed by Atlas stays on your machine or your chosen cloud provider (if self-hosting remotely). Atlas does not send your financial data to any third party except:
- Anthropic Claude API (for reasoning, configurable if you swap to another LLM)
- Your chosen brokers' APIs (for balance reads, read-only)
- Your chosen email provider (Gmail IMAP, for receipt scanning)

You control all of these integrations via `.env`.

---

## Support & Community

- **Issues:** File bugs and feature requests on GitHub
- **Discussions:** Community forum for tax/investing questions (monitored by maintainer)
- **Contributing:** Pull requests welcome. Guidelines: read files before editing, test before committing, use `atlas: type — description` commit format

---

## Changelog

### v2.0 (2026-04-14)

- Pivot from algorithmic trading to CFO + research agent
- Added stock picker, news ingest, macro watch
- Added 59-doc tax library (~80K lines)
- Telegram bot with 16 commands
- Brain architecture (USER, SOUL, STATE, CAPABILITIES, etc.)
- 16 CFO skills, fully documented

### v1.0 (2025-Q4)

- Algorithmic trading engine (12 strategies, backtesting, paper/live)
- Initial tax calculations
- Kraken + OANDA integration
- Archived — recoverable via branch `refactor/cfo-pivot`

---

## Frequently Asked Questions

**Q: Do I need to pay for APIs?**  
A: No. All APIs used are free-tier or included with your broker. Optional paid upgrades (Financial Modeling Prep, Polygon, Benzinga) are ~$43/mo if you want deeper research — but not required.

**Q: How often should I run commands?**  
A: Run `runway` and `networth` monthly. Run `taxes` quarterly (or after large income events). Run `picks` when you want new research ideas. No subscription or mandatory cadence.

**Q: Can Atlas execute trades?**  
A: No. Atlas only reads balances and generates recommendations. You execute trades yourself on your broker. This is intentional — full control stays with you.

**Q: What if I move to another country?**  
A: Update `brain/USER.md` with new tax residency. Atlas has 25+ tax strategies for different jurisdictions (US, UK, Ireland, Crown Dependencies, etc.) — it will recalculate everything.

**Q: Can I use this for a business partner?**  
A: Yes, but multi-user mode is planned for Q2 2026. Until then, you can run separate instances with different `.env` configs.

**Q: What if I find a bug?**  
A: File an issue on GitHub with: command run, expected output, actual output, error message. Include your Python version and OS.

**Q: Can I sell picks Atlas generates?**  
A: Atlas is educational. If you package picks for sale to clients, you're liable for those recommendations. Read the disclaimers above.

---

**Last Updated:** 2026-04-14  
**Maintainer:** CC McKenna, OASIS AI Solutions  
**Status:** Production-ready CFO agent. Commercial license available for resale.
