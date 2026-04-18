# ATLAS — Your Personal CFO Agent

> **Tax strategist. Accountant. Research analyst. Stockbroker.**
> Not an auto-trader. Atlas advises — you decide.

[![version](https://img.shields.io/badge/version-1.0-blue)]()
[![python](https://img.shields.io/badge/python-3.12%2B-green)]()
[![license](https://img.shields.io/badge/license-personal_use-orange)]()

Atlas is a self-hosted personal CFO agent for Canadian solo-entrepreneurs, freelancers, and founders. It tracks your money, researches stocks, pulls receipts for tax prep, models cashflow, and talks to you naturally through Telegram — all from your own laptop, with your own API keys, nothing leaking to anyone.

---

## Part of a 3-Agent AI C-Suite

Atlas is the **CFO** of a three-agent executive team running an entire business. Each agent has its own repo, identity, and specialty — together they replicate what would normally take a $500K/yr executive team to handle.

| Agent | Role | What they handle | Repo |
|-------|------|------------------|------|
| 🏛️ **Bravo** | CEO | Strategy, clients, revenue, partnerships, decision-making | [`CC90210/CEO-Agent`](https://github.com/CC90210/CEO-Agent) |
| 💰 **Atlas** | CFO | Money, tax, wealth, research, compliance — **you're here** | [`CC90210/CFO-Agent`](https://github.com/CC90210/CFO-Agent) |
| 🎨 **Maven** | CMO | Brand, content, ads, funnels, growth | [`CC90210/CMO-Agent`](https://github.com/CC90210/CMO-Agent) |

They talk to each other through shared state files (called "pulses") and a shared Supabase database. Atlas reads the CEO's revenue targets to model runway; Maven reads Atlas's spend gate before launching paid ads; Bravo reads everything to decide the next play.

---

## For non-technical readers: what this actually is

**Think of it like this.** A growing business owner normally has to either (a) do everything themselves — finances, marketing, operations, strategy — or (b) hire three expensive executives. With three agents, you get the third option: a personal C-suite running on your laptop, making real decisions on real data, 24/7, for the cost of a few API calls per month.

- **Atlas** is the financial brain. It knows how much money you have, how much tax you owe, where your runway ends, and what to do about it. Ask it "can I afford to hire someone?" and it actually checks.
- **Bravo** is the strategic brain. It decides what to build, who to sell to, and when to pivot. It reads customer data, tracks deals, writes briefings.
- **Maven** is the creative brain. It produces ad copy, edits videos, launches campaigns, manages multi-brand marketing.

**They coordinate automatically.** When Maven wants to spend $500 on Facebook ads, it has to write a request that Atlas approves by checking runway first. No rogue spending. No memory gaps. Every decision is logged.

**They never lose track.** Every action is recorded in the shared database. If you haven't looked at the system for two weeks, you can query: "what happened in marketing while I was away?" and get a precise answer.

This is not ChatGPT. It's not a chatbot. It's three agents with their own skills, memories, and decision rights, running like a real company.

You don't need to understand Python to use it. You talk to it via Telegram ("/networth", "how much runway?"), and it responds in plain English with the answer.

---

## What Atlas does

**💰 CFO Toolkit** — Net-worth aggregation, Montreal runway modeling, Gmail receipt puller for T2125 tax prep, quarterly tax snapshots, portfolio rebalancing with exit-plan awareness.

**🔍 Research Analyst** — 10-layer stock picks powered by Claude Opus 4.6: fundamentals, technicals, macro flashpoints, news sentiment, market psychology (Fear/Greed, VIX, AAII), historical analogs, insider transactions (SEC Form 4), institutional holdings (13F from Buffett/Burry/Ackman/Druckenmiller/Tepper + 7 more), earnings surprise history, options flow + IV rank. Every pick comes with entry price, stop-loss, 3 profit targets, and click-by-click Wealthsimple execution steps.

**📚 Tax Library** — 59 curated documents, ~80,000 lines. Canadian tax code, crypto ACB tracking, Crown Dependencies migration (Isle of Man, Jersey, Guernsey), CCPC incorporation, SR&ED credits, departure tax (s.128.1), UK FIG regime, Irish Knowledge Development Box, estate freeze, RDTOH, every registered account strategy.

**📱 Telegram Bot** — 12 slash commands plus natural-language dispatch. "How much runway do I have?" "Give me 3 AI plays for 6 months." "Should I sell DOGE?" — Atlas routes the question, runs the pipeline, replies with execution-ready output.

**🧠 Brain Architecture** — `USER.md` is your identity. Atlas reads it before answering anything. No redundant questions. Personalization persists across sessions.

---

## 30-second quickstart

```bash
git clone https://github.com/CC90210/CFO-Agent.git atlas && cd atlas
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # fill in your API keys
python main.py setup                                 # interactive personalization
python main.py networth                              # first run — see your money
```

Full setup in **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)**.

---

## The CLI (9 commands)

```bash
python main.py setup                      # Interactive personalization wizard
python main.py networth                   # Live net-worth across all accounts
python main.py runway                     # Cashflow + runway scenarios
python main.py receipts --since 2026-01-01 # Gmail IMAP → T2125 CSV
python main.py taxes                      # Quarterly tax-reserve check
python main.py picks "AI plays 6 months"  # 10-layer stock picks, execution-ready
python main.py deepdive NVDA              # Bull/bear/base ticker analysis
python main.py crypto-acb                 # CRA T5008 weighted-avg ACB report
python main.py rebalance                  # Portfolio drift + recommendations
```

## The Telegram bot

```bash
python telegram_bridge.py                 # starts the bot
```

Then on your phone:

```
/networth            → live balances
/runway              → cashflow scenarios
/picks AI infra 6mo  → 3 execution-ready picks
/deepdive NVDA       → full analysis
/receipts 2026-01-01 → pull receipts

Or just TYPE:
  "am I going to make it in Montreal?"
  "give me 3 long-term plays"
  "what's the Fed doing this week?"
  "how much tax should I set aside?"
```

Full guide: **[docs/TELEGRAM_GUIDE.md](docs/TELEGRAM_GUIDE.md)**.

---

## Architecture

```
CFO-Agent/
├── cfo/               # CFO operations
│   ├── cashflow.py    # Runway modeling
│   ├── dashboard.py   # Net-worth aggregator
│   ├── accounts.py    # Kraken/OANDA/Wise/Stripe/manual readers
│   ├── gmail_receipts.py  # IMAP → T2125 CSV
│   ├── setup_wizard.py    # Personalization interview
│   ├── crypto_acb.py      # CRA T5008 ACB report
│   └── rebalance.py       # Drift + exit-plan-aware recs
│
├── research/          # Analyst brain (10 layers)
│   ├── news_ingest.py
│   ├── macro_watch.py         # Geopolitical flashpoints
│   ├── fundamentals.py        # P/E, growth, margins
│   ├── psychology.py          # F/G, VIX, AAII, NAAIM
│   ├── historical_patterns.py # Cycles, analogs, seasonality
│   ├── insider_tracking.py    # SEC Form 4
│   ├── institutional_tracking.py  # 13F (12 tracked legends)
│   ├── earnings_calendar.py   # Surprise history, PEAD
│   ├── options_flow.py        # IV, short interest, squeeze
│   └── stock_picker.py        # Claude Opus 4.6 synthesis
│
├── finance/           # Tax calc, advisor, budget, wealth tracker
├── brain/             # Identity + instructions (USER.md, SOUL.md, STATE.md, ...)
├── skills/            # 16 CFO playbooks
├── docs/              # 59 tax docs + 5 product guides
├── memory/            # Operational intelligence
├── data/              # manual_balances.json, picks, cache
├── utils/             # Logger, Telegram alerts
├── main.py            # CLI entry
├── telegram_bridge.py # Telegram bot (913 lines, NL dispatch)
└── archive/           # Archived algorithmic trading (recoverable)
```

---

## Who this is for

✅ **Self-employed founders** building SaaS, consulting, creator businesses
✅ **Canadian freelancers** filing T2125 who want tax + income tracking automated
✅ **Aggressive long-horizon investors** (3-18 month holds, not day-trading)
✅ **Dual-citizens** considering jurisdictional optimization (UK, Ireland, Crown Dependencies, EU)
✅ **Early high-earners** approaching $80K revenue who need CCPC incorporation guidance

❌ **Not for:** day-traders, retail scalpers, people wanting automated bot trading, users who want legal or registered financial advice (Atlas researches and advises — you still file your own taxes and make your own trades)

---

## Product guides

- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** — Full install + `.env` walkthrough (4,200 words, 702 lines)
- **[TELEGRAM_GUIDE.md](docs/TELEGRAM_GUIDE.md)** — Phone interface (3,800 words, 20+ NL examples)
- **[ATLAS_USER_GUIDE.md](docs/ATLAS_USER_GUIDE.md)** — Architecture + capabilities (3,847 words)
- **[QUICKSTART.md](docs/QUICKSTART.md)** — 15-minute onboarding
- **[PERSONALIZATION_INTERVIEW.md](docs/PERSONALIZATION_INTERVIEW.md)** — Every question the wizard asks

---

## Tax library (the moat)

59 documents, ~80,738 lines. Index at **[brain/TAX_PLAYBOOK_INDEX.md](brain/TAX_PLAYBOOK_INDEX.md)**. Topics:

Core Tax Strategy · Crypto & DeFi · International & Multi-Jurisdiction · CCPC & Corporate · Compliance & Audit Defense · Business Valuation & M&A · Forensic Accounting · Trust Taxation · CCA & Depreciation · Platform Economy · Professional Corps · Transfer Pricing · Financial Literacy · Real Estate · Wealth Building · Retirement · Estate & Succession · SaaS/AI Business · Options & Derivatives · Payroll & Hiring · Insurance · Funding & Grants · Global Financial System · Debt & Leverage · Tax Calendar · Negotiation

---

## Data sources

**Free tier out of the box:** yfinance (fundamentals + price history), SEC EDGAR (Form 4 + 13F filings), Google News RSS, Reuters / Bloomberg / WSJ / FT public RSS, CNN Fear/Greed, AAII, NAAIM, CBOE, FINRA public data.

**Optional free API upgrades:** Alpha Vantage (25 req/day), Finnhub (60 req/min), NewsAPI (100 req/day), FMP (250 req/day). Add keys to `.env` when you want them.

**Paid upgrade path (documented but not required):** FMP Premium $14/mo → Polygon Starter $29/mo → Benzinga Pro $27/mo. See [research/README.md](research/README.md).

---

## Safety rules (hardcoded)

- Atlas never executes trades. Period.
- Atlas never claims legal or tax advice — you file via NETFILE.
- Every stock pick has a conviction score, not a guarantee.
- Kill switches on every signal layer — graceful degradation if any API fails.
- `.env` is gitignored. Secrets never leave your machine.

---

## Versioning

- **v1.0** (2026-04-15) — CFO pivot from algorithmic trader. Production-ready.

Commit format: `atlas: type — description`

---

## License

Personal use. Commercial resale or redistribution requires written permission.

---

## Contact

Built by CC / OASIS AI Solutions — `conaugh@oasisai.work`
