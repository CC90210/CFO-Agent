---
name: ATLAS Agent Registry (CFO era)
description: Subagent definitions and task routing for the Atlas CFO + Research Analyst runtime
tags: [agents, orchestration, routing, subagents, identity]
version: V2.1
last_updated: 2026-04-25 (Data Integrity rule added after EDGAR 503 incident)
---

# ATLAS — Agent Registry & Task Routing (CFO era)

> Identity + routing map for the Atlas runtime. This file applies to ANY AI
> runtime invoking Atlas's modules (Claude Code, OpenAI Codex, Antigravity,
> Gemini). Read alongside [[CLAUDE]], [[GEMINI]], [[SOUL]], [[USER]],
> [[STATE]], [[CFO_CANON]], [[AGENT_ORCHESTRATION]].

## Identity (mirror of CLAUDE.md)

- **Name:** ATLAS — CFO + Research Analyst.
- **Not:** trading bot, auto-trader, signal cron. The 2026-04-14 pivot moved
  all algorithmic trading into `archive/trading-automation/`. Anything in
  this file referring to "trading agents" describes the archive only.
- **Open every reply with:** `Atlas online.`

## Data Integrity (NON-NEGOTIABLE — same wording across all runtime files)

> Codified after the 2026-04-25 EDGAR 503 incident.

When a live data feed (yfinance, SEC EDGAR, ccxt, Finnhub, FMP, Alpha Vantage,
Wise, Stripe, Kraken, OANDA) is unavailable, NO runtime — Claude, Codex,
Antigravity, Gemini — may substitute training-memory data, recall prior
conversation numbers, or guess.

**Required behavior:**
1. Fail loudly with the canonical banner: `API DOWN - CANNOT GENERATE PICK. Please fix the data feed.`
2. Surface the failed source, ticker (if applicable), and detail.
3. Do NOT proceed with a degraded analysis that looks complete.

**Enforced in code by:**
- `research/_data_integrity.py` — `DataFeedError`, `require_live_price_data`, `require_live_fundamentals`, `require_live_quote`
- `research/_sec_client.py` — single allowed path to SEC endpoints (real User-Agent, 9 req/s ceiling, exponential-jittered retry)

A new SEC HTTP call that bypasses `_sec_client` is a defect.

## Active Modules (post-pivot)

### CFO toolkit — `cfo/`

| Module | Role | File | Domain |
|--------|------|------|--------|
| Cashflow | Montreal runway, burn, break-even | `cfo/cashflow.py` | Liquidity planning |
| Dashboard | Net-worth aggregation across platforms | `cfo/dashboard.py` | Net worth |
| Accounts | Wise / Stripe / Kraken / OANDA / manual readers | `cfo/accounts.py` | Balance fetch |
| Gmail Receipts | IMAP receipt puller → CSV for T2125 | `cfo/gmail_receipts.py` | Bookkeeping |
| Crypto ACB | Weighted-average ACB for CRA T5008 | `cfo/crypto_acb.py` | Crypto tax |
| Pulse | Writes `data/pulse/cfo_pulse.json` for cross-agent contract | `cfo/pulse.py` | C-suite IPC |
| Setup Wizard | Onboarding wizard | `cfo/setup_wizard.py` | First run |

### Research — `research/`

| Module | Role | File | Notes |
|--------|------|------|-------|
| **SEC HTTP client** | Centralized EDGAR access (real UA, retry, rate limit) | `research/_sec_client.py` | **Required for any SEC call** |
| **Data Integrity guard** | `DataFeedError` + live-feed validators | `research/_data_integrity.py` | **Required at every research entry point** |
| News ingest | RSS + Google + NewsAPI + Finnhub + FMP + EDGAR filings | `research/news_ingest.py` | 7 source redundancy |
| Macro watch | Geopolitical flashpoints + sector rotation | `research/macro_watch.py` | |
| Fundamentals | yfinance → FMP → Alpha Vantage → Finnhub waterfall | `research/fundamentals.py` | |
| Finnhub client | Quote / profile / company news / basic financials | `research/finnhub_client.py` | 60 req/min free |
| Insider tracking | Form 4 insider-buy/sell scoring | `research/insider_tracking.py` | |
| Institutional tracking | 13F smart-money consensus + who_owns | `research/institutional_tracking.py` | Uses `_sec_client` |
| Earnings calendar | Days-to-earnings + surprise score | `research/earnings_calendar.py` | |
| Options flow | P/C ratio, IV rank, squeeze score | `research/options_flow.py` | |
| Psychology | AAII / NAAIM / fear-greed sentiment | `research/psychology.py` | |
| Historical patterns | Cycle context for the lead ticker | `research/historical_patterns.py` | |
| Stock Picker Agent | Claude Opus 4.7 synthesis → execution-ready Pick | `research/stock_picker.py` | Catches `DataFeedError` |

### Finance — `finance/`

| Module | Role | File | Domain |
|--------|------|------|--------|
| Tax Calculator | CRA-accurate capital gains, ACB, deductions | `finance/tax.py` | Tax filing |
| Financial Advisor | Portfolio analysis, allocation, reviews | `finance/advisor.py` | Wealth management |
| Wealth Tracker | Net-worth, FIRE projections | `finance/wealth_tracker.py` | FIRE planning |
| Budget Tracker | Expense tracking, savings opportunities | `finance/budget.py` | Budgeting |

### Skills — `skills/`

19 CFO skills under `skills/`. Examples: `tax-optimization`, `crypto-acb-tracking`,
`departure-tax-planning`, `behavioral-finance-guard`, `unit-economics-validation`,
`self-improvement-protocol`. Each skill has its own `SKILL.md`. Discover via
[[CAPABILITIES]] (auto-generated by `scripts/build_capabilities.py`).

## Cross-Agent Contracts

3-way C-suite. All data flows via `data/pulse/*.json` — one-way writes, no
shared mutable state. See [[AGENT_ORCHESTRATION]].

| Agent | Role | Project | Pulse |
|-------|------|---------|-------|
| **ATLAS** (this) | CFO + Analyst | `CFO-Agent/` | `data/pulse/cfo_pulse.json` (writes) |
| **Bravo** | CEO | `Business-Empire-Agent/` | `data/pulse/ceo_pulse.json` (Atlas reads) |
| **Maven** | CMO | `CMO-Agent/` | `data/pulse/cmo_pulse.json` (Atlas reads) |

Atlas vetoes ad spend via `approved_ad_spend_monthly_cap_cad`. Maven must
honor it.

## Task Routing Matrix (CFO era)

| Task | Route To | Complexity |
|------|----------|------------|
| Stock pick request | `research/stock_picker.py::pick` | COMPLEX (live feeds required) |
| Deep dive on ticker | `research/stock_picker.py::deep_dive` | COMPLEX |
| Net worth snapshot | `cfo/dashboard.py` (`python main.py networth`) | SIMPLE |
| Montreal runway | `cfo/cashflow.py` (`python main.py runway`) | SIMPLE |
| Receipt pull | `cfo/gmail_receipts.py` (`python main.py receipts`) | MODERATE |
| Crypto ACB report | `cfo/crypto_acb.py` (`python main.py crypto-acb`) | MODERATE |
| Tax-quarter check | `finance/tax.py` + `python main.py taxes` | SIMPLE |
| Tax strategy question | `brain/TAX_PLAYBOOK_INDEX.md` → relevant doc | SIMPLE-COMPLEX |
| Tax filing prep | `skills/accounting-advisor` | COMPLEX |
| FIRE calculation | `finance/wealth_tracker.py` | SIMPLE |
| Portfolio rebalance | `cfo/rebalance.py` (`python main.py rebalance`) | MODERATE |
| Ad-spend approval | `skills/unit-economics-validation` + cfo_pulse | MODERATE |
| Behavioral check (CC frustrated / impulsive) | `skills/behavioral-finance-guard` | SIMPLE |
| Self-improvement cycle | `skills/self-improvement-protocol` | MODERATE |

## Complexity Classification

| Level | Files Touched | Steps | CC Involvement |
|-------|--------------|-------|----------------|
| TRIVIAL | 1 | 1-2 | None |
| SIMPLE | 1-2 | 3-5 | Inform after completion |
| MODERATE | 3-5 | 5-15 | Show reasoning + result |
| COMPLEX | 5+ | 15+ | Plan → CC approves → execute |
| CRITICAL | Any | Any | Money/compliance at stake → CC approves first |

## Coordination Rules

1. **Live data is mandatory for picks.** If `DataFeedError` raises, surface it
   verbatim. No fabricated numbers. Ever.
2. **Risk vetoes are final.** A safety rule violation in CLAUDE.md aborts
   any plan, regardless of CC's pressure to ship.
3. **Tax calculations always cite the ITA section** and show dollar impact.
4. **Cross-domain decisions** (e.g. tax-loss harvest tied to a pick) go
   through both `research/stock_picker.py` AND `finance/tax.py` — never one
   in isolation.
5. **Pulse is the only cross-agent channel.** Reading Bravo / Maven state
   means reading their pulse, not their internal files.

## Archived (do not invoke)

Pre-pivot trading agents at `archive/trading-automation/agents/`:
`technical_analyst.py`, `fundamental_analyst.py`, `sentiment_analyst.py`,
`risk_analyst.py`, `debate_agent.py`, `portfolio_agent.py`, `orchestrator.py`,
`darwinian.py`. None of these run. None of them are imported. If a routing
suggestion mentions any of them, that suggestion is wrong — flag it.
