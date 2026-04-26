---
name: ATLAS Session Log
description: Append-only narrative log of every session — trading actions, tax events, financial decisions
tags: [log, sessions, activity, narrative]
---

# ATLAS Session Log

> Append-only. New entries at the top. Compress entries >14 days old to ARCHIVES/.
> Every session adds a brief summary of what happened.

---

### Session 33 — 2026-04-25 evening (Claude Code runtime) — Deep system audit & hardening
- CC requested full deep-audit. Inventoried 35 Python modules across cfo/, research/, finance/, utils/, scripts/. Every module compiles + imports clean.
- **Bug fixes (5 real defects found and fixed):**
  - `OptionsSnapshot` attribute mismatch in `research/stock_picker._fetch_options_signals` — was reading `put_call_oi_ratio` / `atm_iv_pct` / `days_to_cover` (don't exist); real fields are `put_call_ratio` / `implied_volatility_30d` / `short_interest_ratio_days_to_cover`. Caused `AttributeError` per ticker on every picks run.
  - `_infer_tickers` regex extracted account acronyms (TFSA / RRSP / FHSA / USD / CAD / RBC / CCPC / ETF / PE / Q1 etc.) as candidate tickers, tripping the integrity guard. Fixed with explicit `_TICKER_BLOCKLIST` + SEC company_tickers manifest membership check via new `_filter_real_tickers` helper. Tested across 5 cases.
  - SEC 13F `/Archives/edgar/data/.../index.htm` 503-loop in `_fetch_13f_document` retried up to 12× per fund × 12 tracked funds × every ticker, burning minutes. Added 15-min negative cache so a single broken accession is recorded once and skipped instead of re-attempted.
  - `Pick.sources_used` was hallucinated by Claude (cited SEC 13F as source even when 13F retries had exhausted). Now computed deterministically in `pick()` from actual contributing modules and written over Claude's value after parsing.
  - `research/insider_tracking.py` had its OWN local SEC HTTP helper with the bad generic User-Agent and no retry — same pre-fix pattern. Refactored to delegate to `research/_sec_client.get` like `institutional_tracking` and `news_ingest`.
- **New tooling:**
  - `scripts/audit_imports.py` — imports every project module, reports failures with traceback. Repo-root sys.path setup so it works from any cwd.
  - `scripts/self_test.py` + `python main.py self-test [categories...]` — CI-style end-to-end smoke test: imports / cli / modules_dry / provider_health / graph / memory. Each category runs independently and reports per-test pass/fail.
  - `/health` Telegram command + `_run_provider_health` executor in `telegram_bridge.py` — CC can now check provider status from his phone without going to the CLI.
- **Hygiene:**
  - Fixed 17 broken wikilinks in `brain/AGENTS.md` and `memory/CLAUDE_TASK_FIX_EDGAR.md` — relative-path links into `.py` source files that the validator (correctly) couldn't resolve as vault notes. Replaced with plain backtick code refs.
  - Final graph state: **0 orphans, 0 broken wikilinks, 422 total wikilinks**.
- **CAPABILITIES.md regenerated**: 19 skills, 13 Telegram commands (was 12), 11 CLI commands (was 9), 8 Claude tools, 8 CFO modules, 14 research modules.

### Session 32 — 2026-04-25 (Claude Code runtime)
- **EDGAR 503 fix + anti-hallucination guard + new providers** — completed CC's three-task brief in [[CLAUDE_TASK_FIX_EDGAR]].
- Built `research/_sec_client.py` (real SEC User-Agent `Atlas CFO Agent (Conaugh McKenna) conaugh@oasisai.work`, 9 req/s ceiling, tenacity retry on 429/503).
- Built `research/_data_integrity.py` (`DataFeedError` + `require_live_*` validators) — every research entry point now refuses to generate a pick if live feeds are down. Canonical banner: `API DOWN - CANNOT GENERATE PICK. Please fix the data feed.`
- Built `research/finnhub_client.py` (quote / profile / company_news / basic_financials).
- Extended `research/fundamentals.py` waterfall: yfinance → FMP → Alpha Vantage → Finnhub.
- Extended `research/news_ingest.py` with `fetch_finnhub_news`, `fetch_fmp_news`, unified `fetch_ticker_news` aggregator.
- Refactored `research/institutional_tracking.py` and the SEC paths in `news_ingest.py` to delegate every SEC HTTP call through `_sec_client`.
- Added Data Integrity section to project-root `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` (the actual files runtimes read).
- Rewrote `brain/AGENTS.md` — removed pre-pivot trading agents (`technical_analyst`, `risk_analyst`, `debate_agent`, `orchestrator`, `darwinian` etc., all archived) and added CFO-era routing matrix with Data Integrity rule.
- Patched Windows charmap encoding bug in `scripts/validate_memory.py` (`→` → `->`) and added skip list for self-improvement-protocol artifacts (MISTAKES, PATTERNS, CAPABILITY_GAPS).
- Smoke tests: SEC company_tickers manifest 200 OK (10,341 entries); NVDA 8-K filings 10/10; Berkshire 13F 110/110 holdings; NVDA Finnhub quote $208.29; NVDA news aggregator 341 articles (Finnhub 249 + Google 92).

---

### Session 31 — 2026-04-18 (Antigravity runtime)
- **File structure audit & optimization** — CC requested full audit after noticing `.claude/skills/` only had 2 files
- **Critical fixes applied (4):**
  - `telegram_bridge.py:345` — tax status "BEING PREPARED" → "FILED (Session 24)"
  - `finance/advisor.py:257` — stale MRR $2,191 → $2,982 in Claude system prompt
  - `finance/budget.py:122,127` — stale MRR $2,191 → $2,982 in prompt + default constructor
  - `cfo/accounts.py` — added `get_fx_rates()` for live FX via exchangerate.host (15-min cache, fallback to defaults)
- **`.claude/skills/` restructured (2 → 7 files):**
  - Rewrote `tax-strategy.md` — maps to all 7 tax skill playbooks + docs
  - Rewrote `trading.md` — replaced pre-pivot algo trading refs with current 10-layer research pipeline
  - NEW: `cfo-operations.md` — net worth, runway, cashflow, accounts
  - NEW: `compliance-crossborder.md` — CRA deadlines, HST, W-8BEN, foreign reporting
  - NEW: `accounting-receipts.md` — Gmail receipts, T2125, crypto ACB
  - NEW: `international-strategy.md` — departure tax, Crown Dependencies, exit ladder
  - NEW: `financial-planning.md` — budget, FIRE, wealth, incorporation readiness
  - NEW: `system-multiagent.md` — architecture, pulse protocol, 4-runtime coordination
- **`.claude/settings.local.json` fixed** — memory path pointed to old `trading-agent` project name
- **NEW: `brain/STRUCTURE.md`** — file ownership map + multi-agent conventions
  - Defines SSOT (Single Source of Truth) rules
  - "Update in-place, don't spawn" convention per CC's directive
  - Session tracking requirements for all runtimes
  - Pulse-before-close protocol
- **CC directive captured:** "Don't make a new file each time you change something — update existing files"

- **Bravo delegation prompt created** — full C-suite architecture handoff (CFO+CEO+CMO)
  - Inventoried CC's 5 marketing repos: Marketing-Agent, shopify-ad-engine, ig-setter-pro, cc-funnel, Bravo content-studio
  - Designed 3-way pulse protocol (cmo_pulse.json schema)
  - Mapped 11 Bravo skills for CMO extraction
  - Flagged stale Atlas reference in Bravo's brain/AGENTS.md (still says "trading-agent")
- **Claude Code Maven Handoff Prompt created** — generated specialized artifact for Claude Code to execute the CMO buildout and orchestrate marketing repos.
- **Updated Atlas orchestrator** to integrate Maven into the 3-agent C-suite structure (`brain/AGENT_ORCHESTRATION.md` and `brain/STRUCTURE.md`).
- **CC switching to Bravo/Maven runtime** for CMO agent buildout

**Runtime:** Antigravity (via AGENTS.md)
**Files changed:** 15 (6 edited, 9 created)

---

### Session 30 — 2026-03-29
- **Comprehensive system audit** — 5 parallel agents audited engine, finance, brain, tests, infrastructure
- **4 CRITICAL engine fixes:**
  - Wired RiskManager into engine.py (kill switches were INERT — validate_trade() now gates every trade)
  - Correlation tracker now feeds RiskManager via update_correlations() every 10 ticks (threshold 0.70, was hardcoded 0.80)
  - Per-strategy trailing stops: trend-followers get 4-5x ATR (atr method), mean-reversion gets 1.5-2x (chandelier). Configured in strategies.yaml.
  - Position sizing hierarchy clarified: PositionSizer primary, Protocol advisory, RiskManager validation gate
- **MAJOR fix:** Regime detection cached per (symbol, timestamp) — prevents 10x redundant calls
- **Documentation fixes:** 7 orphaned docs indexed in TAX_PLAYBOOK_INDEX, doc counts updated (66 docs, ~82,900+ lines)
- **Infrastructure fixes:** db/__init__.py exports all 10 models, Telegram bridge string formatting bug fixed
- **MEMORY.md trimmed** from 220 lines to ~75 (under 200-line limit)
- **Tests:** 200/200 passing, all imports verified
- **.env security:** Clean — never committed to git history
- **7 core memory files confirmed present:** SESSION_LOG, MISTAKES, PATTERNS, DECISIONS, LONG_TERM, SOP_LIBRARY, ACTIVE_TASKS

---

### 2026-03-28 — Session 25: Largest Build Ever — 17 Docs, 5 Skills, Product Vision

**Duration:** Extended session (multi-wave, 11 parallel agents)
**Category:** Knowledge Base Expansion + Product Foundation + Skills Build

**What happened:**
- SIN scrubbed from 5 tracked files, added tax_filing_2025.md to .gitignore
- Full tax knowledge audit — plain-English rundown of 25-strategy playbook for CC
- GitHub competitive analysis: ATLAS confirmed first-of-kind (no comparable project exists)
- Full query routing diagnostic: 5-layer routing verified (brain→reasoning→skills→docs→code)
- **Wave 1 (5 docs, 7,867 lines):** Options/derivatives tax, CRA bulletproof compliance, wealth building mastery, advanced investment strategies, SaaS CFO playbook
- **Wave 2 (5 docs, 8,747 lines):** Global financial system, US tax for Canadians, financial statements guide, business insurance & liability, payroll & hiring guide
- **Wave 3 (7 docs + 5 skills, 12,697 lines):** Estate & succession planning, tax calendar & automation, AI regulation & compliance, real estate investing, negotiation & deal strategy, funding programs operational, crypto DeFi strategies + compliance-monitor, financial-health-check, cash-flow-invoicing, cross-border-compliance, incorporation-readiness skills
- Product vision crystallized: ATLAS = sellable CFO-in-a-box. docs/ + skills/ = sellable core
- W-8BEN action item surfaced for CC (submit to Bennett immediately)

**Final counts:** 53 docs (~57,787 lines), 16 skills, 76 quick-lookup routing entries
**Commits:** 3 pushed (SIN scrub + Wave 1 + Wave 2) + Wave 3 pending

---

### 2026-03-27 — Session 24: FHSA Opened, CRA Blocked, International Tax Masterplan

**Duration:** Extended session
**Category:** Financial Action + Knowledge Base + Citizenship Path

**What happened:**
- CC opened FHSA at Wealthsimple (self-directed investing, 2026-03-27 ✅). Understands mechanics: room accumulates $8K/year, tax deduction on contributions, tax-free growth, for first home purchase.
- CC attempted CRA My Account setup via RBC Partner Sign-In but blocked at identity verification (Line 15000 required, no prior returns assessed). Will retry in 1-2 weeks after 2025 return is assessed. Has 5 attempts remaining.
- CC confirmed Irish passport eligibility through father's Irish residency. Will contact father about grandfather's birth certificate for expedited citizenship claim (6-12 month timeline).
- CC confirmed: zero crypto sales ever on Wealthsimple (only buys and transfers to Kraken). No tax events on $206.41 CAD holdings.
- CC provided education details: Bishop's University 3 years, tuition ~$2K-$2.5K/year. Potential $4.5K-$7.5K tuition carryforward (will verify on CRA My Account).
- Deep research compiled: 4 new docs (4,207 lines):
  - ATLAS_INTERNATIONAL_TAX_MASTERPLAN.md — 19-jurisdiction comparison, UK FIG regime (4yr 0% foreign income), IoM vs Guernsey vs Jersey, Ireland KDB, cost-benefit analysis by income level
  - ATLAS_CRYPTO_TAX_ADVANCED.md — Margin trading, derivatives, DeFi risk, CARF compliance 2026, CRA audit triggers, international reporting
  - ATLAS_CANADIAN_TAX_LOOPHOLES.md — Obscure deductions, entity structures, prescribed rate arbitrage, prescribed debt planning
  - ATLAS_ASSET_PROTECTION_MASTERPLAN.md — Corporate structures, liability shields, insurance strategies, US residency trust, foreign trusts
- Updated income projection to $280K-$480K+ CAD (from $240K-$400K). MRR currently $2,982 USD/mo with 64.99% growth rate on Stripe.
- Family structure documented: mom in Canada ($80K-$90K/year), dad in Ireland ($60K-$70K/year, EUR likely), 2 sisters (LCGE potential). Dad strategic asset for Irish citizenship path.
- CC feedback captured: "Stop asking redundant questions, speak plain English, act as real CFO."
- Committed and pushed 39 files to GitHub.

**Key discoveries:**
- UK FIG regime: 4 years 0% tax on foreign income if UK-resident. Valuable bridge before Isle of Man.
- Isle of Man implementation cost: ~£400-500/month all-in (residential + company setup). Breaks even at ~$120K revenue vs Canadian tax.
- SR&ED for AI: 43% refundable CCPC (35% federal + 8% Ontario). At $280K revenue = $16K-$24K annual credits once incorporated.
- Shipping tonnage tax (Strategy 13 in core playbook): Debunked. Not applicable to CC's business type.
- Father's documentation can accelerate Irish passport by 3-6 months vs standard Foreign Birth Registry timeline.

**Metrics:**
- Docs: 25 → 29 (4 new, 4,207 lines)
- Total lines: ~24,300 → ~28,500
- Brain files: 12 (unchanged)
- Memory entries: user_citizenship, user_financial_profile, ACTIVE_TASKS updated

**CC's explicit directives:**
- "I shouldn't limit my loopholes to one place. I'm a dual citizen."
- "You don't work for governments. Save me money through any means necessary, ethically and abiding by the laws."
- "Operate like I'm a billion-dollar company."
- No more political caution — be aggressive on tax optimization within legal bounds.

---

### 2026-03-27 — Session 23: CFO Intelligence Expansion

**Duration:** Extended session
**Category:** Knowledge Base + Architecture

**What happened:**
- CC filed 2025 taxes successfully (SIN on file)
- CC mandated aggressive tax optimization — "operate like a billion-dollar company"
- CC revealed dual citizenship: Canadian + British passport, Irish eligible
- Built 7 new tax documents (7,772 lines):
  - ATLAS_INSTALLMENT_PAYMENTS.md (1,014 lines) — CRA quarterly installments
  - ATLAS_HST_REGISTRATION_GUIDE.md (1,057 lines) — HST registration, ITCs
  - ATLAS_VDP_GUIDE.md (802 lines) — Voluntary Disclosure Program
  - ATLAS_TOSI_DEFENSE.md (1,223 lines) — Income splitting defense
  - ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md (1,217 lines) — British passport strategy
  - ATLAS_FOREIGN_REPORTING.md (1,143 lines) — T1135, T1134, transfer pricing
  - ATLAS_INCOME_SCALING_PLAYBOOK.md (1,316 lines) — $0 to $10M+ tiers
- Expanded brain/ from 2 → 12 files (Bravo pattern adoption):
  - SOUL.md, USER.md, DASHBOARD.md, GROWTH.md, RISKS.md, TAX_PLAYBOOK_INDEX.md
  - BRAIN_LOOP.md, INTERACTION_PROTOCOL.md, HEARTBEAT.md, AGENTS.md
- Deep dive into Business-Empire-Agent architecture (163 skills, 15 agents, 10-step brain loop)
- Saved dual citizenship + tax aggression mandate to memory
- Updated CLAUDE.md, CAPABILITIES.md, STATE.md

**Key decisions:**
- Atlas recommendation: Isle of Man at $120K+ revenue, Irish IP company at $300K+
- Start Irish passport application NOW (€278, 6-12 months)
- Departure tax today is ~$0 — window closes as assets appreciate
- RRSP contributions wrong below $55K marginal rate
- SR&ED tracking should start NOW, before incorporation

**Metrics:**
- Total docs: 18 → 25 (~24,300 lines)
- Brain files: 2 → 12
- Memory entries: +2 (citizenship, tax mandate)

---

### Prior Sessions (1-22) — Summary

**Sessions 1-5 (V1.0):** Foundation — basic strategies, CCXT/Kraken, backtest engine, risk manager, 10 AI agents, Telegram bot.

**Sessions 6-12 (V1.5):** Strategy expansion — 12 strategies, OANDA, trailing stops, trade protocol, correlation tracker, live exit loop fix.

**Sessions 13-17:** Finance modules (tax.py, advisor.py, wealth_tracker.py, budget.py). Tax strategy playbook. Regime hysteresis. Portfolio tightening.

**Session 18:** Async CCXT bug fixes. OANDA thread safety (Semaphore(2)). Windows daemon launch (subprocess.Popen). Commodity/forex research. TSMOM strategy.

**Session 19:** Daemon freeze fix (OANDA semaphore). Single-instance enforcement. 10 strategies active.

**Session 20:** CC's financial profile documented. US bank accounts (Wise). T1135 assessment.

**Session 21:** Wave 1-2 tax docs (10 docs, 7,929 lines). CRA crypto intel, incorporation, real estate, treaties, wealth playbook, business structures, deductions, audit defense, insurance, grants.

**Session 22:** Wave 3 tax docs (7 docs, 5,939 lines). DeFi tax, pension, alternative investments, debt, AI/SaaS, bookkeeping, wealth psychology. Brain/ directory created. Skills created.
