---
name: ATLAS Mistakes Log
description: Root cause analysis of every significant error — trading-era, CFO-era, tax, system — with prevention strategies
tags: [mistakes, errors, prevention, learning]
---

# ATLAS Mistakes Log

> Every mistake gets: what happened, root cause, prevention strategy.
> Read this BEFORE repeating a task type. Learn once, not twice.
>
> Neighbors: [[PATTERNS]] · [[CAPABILITY_GAPS]] · [[SOUL]] · [[CFO_CANON]] · [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] · [[INDEX]].

---

## CFO-Era Mistakes (added 2026-04-19 via self-improvement cycle 1)

Five mistakes from the trading-era (and early CFO-era) root-caused with the CFO-era prevention rule for each. Meta-pattern: trading-era Atlas optimized for execution velocity; CFO-era Atlas optimizes for diagnostic rigor. [[CFO_CANON]] is the structural fix.

### 2026-04-19 (backlog) — Autonomous trading daemon as "product"
**What happened**: Atlas v1 (2026-03-16) launched a 24/7 trading daemon on cron against live Kraken and OANDA. The architecture assumed algorithmic edge would be discovered post-launch. CC pivoted 2026-04-14 — 29 days later.
**Root cause (5 Whys)**: (1) brief was "build a trading agent"; (2) CC believed algo-trading was the fastest compounding path; (3) pattern-matched from finance YouTube, not from his own edge; (4) Atlas optimized for execution over diagnosis; (5) no canonical framework to challenge the brief.
**Prevention rule (CFO-era)**: Before any major build, Atlas runs the diagnostic checklist from [[CFO_CANON]] § Graham + Marks — (1) what's the edge? (2) is it durable? (3) probability-weighted return vs alternative allocation? (4) what kills this? If any answer is "we'll figure it out post-launch," ship research not system.
**Pattern**: `execution-before-diagnosis` → see [[PATTERNS]] § canon-backed decisions.

### 2026-04-19 (backlog) — Live execution on zero-backtest strategies
**What happened**: Several strategies (gold trend, London breakout, gold pullback) wired to OANDA live with no walk-forward validation and no Monte Carlo. Paper-trading was referenced in architecture but not enforced as a gate.
**Root cause (5 Whys)**: (1) config cut for speed; (2) "ship it and iterate" software mindset; (3) finance wasn't distinguished from software; (4) no CFO canon, no Taleb presence, no "ruin is irreversible" frame; (5) Atlas was still "trading agent," not "CFO." Identity drove doctrine.
**Prevention rule (CFO-era)**: No capital deployment without a documented thesis that passes [[CFO_CANON]] § Buffett (moat/edge), § Graham (margin of safety), § Taleb (tail risk survival); explicit kill-conditions written before entry; position size per [[skills/position-sizing/SKILL|position-sizing]]. Atlas advises — operator clicks — but REFUSES to advise a position that fails these three gates.
**Pattern**: `no-thesis-no-trade`.

### 2026-04-19 (backlog) — Over-concentration tolerated
**What happened**: CC's MRR is 94% from a single client (Bennett). Atlas only surfaced it reactively (via pulse protocol once Bravo was installed, 2026-04-18). The risk existed for months with informal awareness only.
**Root cause (5 Whys)**: (1) no concentration metric in cfo_pulse until Bravo handshake; (2) CFO skills focused on tax, not revenue-book risk; (3) CC's immediate pain was 2025 filing; concentration was slower-moving; (4) heartbeat cadence was event-driven not scheduled; (5) no weekly CFO review cron.
**Prevention rule (CFO-era)**: `cfo_pulse.json` always exposes concentration metrics (single-client %, HHI index). Atlas surfaces any concentration > 70% on every session-start brief until the operator acknowledges it. Added `brand_economics.portfolio_summary.hhi_concentration_index` on 2026-04-19.
**Pattern**: `quantify-the-slow-risks`.

### 2026-04-19 (backlog) — Receipt parser declared "done" at 5/10 emails
**What happened** (Session 100, 2026-04-18): Gmail receipt parser processed 5 of 10 emails and reported success. Real cause: no PDF extraction for Anthropic receipts, no email-body fallback for Apple receipts. Caught only because CC asked "why only 5?"
**Root cause (5 Whys)**: (1) aggregate count "5/10" looked like partial success; (2) success threshold never defined pre-run; (3) no completeness contract for data parsers; (4) parsers treated as best-effort utilities; (5) bookkeeping was downstream of trading in v1.
**Prevention rule (CFO-era)**: Per `feedback_parser_completeness.md` — every parser run reports total input count, parsed count, unparsed count with reason per item, and confirms every input channel (HTML, plaintext, PDF attachment, email body) was attempted. No success report until every channel tried.
**Pattern**: `exhaustive-channels-before-success`.

### 2026-04-19 (backlog) — Suggesting already-done actions
**What happened** (recurring sessions 22-26): Atlas suggested opening the FHSA, filing 2025 taxes, retrying CRA My Account — all already done. Each re-suggestion cost trust.
**Root cause (5 Whys)**: (1) Atlas skipped memory files before responding; (2) under time pressure, brain-file reads were deprioritized; (3) no hard gate enforced; (4) CLAUDE.md rule lived as prose, not a checkpoint; (5) agent design treated instructions as soft norms.
**Prevention rule (CFO-era)**: Per `feedback_no_redundant_questions.md` + CLAUDE.md MANDATORY section. Before answering ANY question, Atlas reads [[CAPABILITIES]], [[USER]], [[STATE]], and `memory/MEMORY.md` (auto-memory index). The "Things CC has already done" list in CLAUDE.md is checked against every suggestion before surfacing. Treated as a gate, not a guideline.
**Pattern**: `pre-response-reads`.

---

## Archive — Trading-Era Mistakes

> Kept for pattern recognition. The trading stack was archived 2026-04-14 at `archive/trading-automation/`. These remain load-bearing lessons for any future strategy execution (stock-pick sizing, crypto ACB handling) even though the daemon is retired.

### [2026-03-26] Ichimoku Relaxation — Catastrophic Loss
**What happened:** Changed Ichimoku from 5/5 conditions to 4/5. Result: -91% drawdown.
**Root cause:** Removing even one confirmation condition eliminated the strategy's edge entirely.
**Prevention:** NEVER relax Ichimoku below 5/5. Add to RISKS.md as hard rule.

### [2026-03-25] Scale-Out Tiers — Systematic Drag
**What happened:** Enabled scale-out tiers (partial position exits at profit targets). Result: -5% to -20% drag on every crypto strategy.
**Root cause:** Crypto trends are volatile — scaling out locks in small gains and misses the big moves that make the strategy profitable.
**Prevention:** Scale-out is DISABLED. Never re-enable for crypto. May work for equities (untested).

### [2026-03-24] BB Mean Reversion — Total Failure
**What happened:** Bollinger Band mean reversion strategy tested across all symbols. ALL returned -20% to -27%.
**Root cause:** Crypto doesn't mean-revert cleanly at BB bands — trends dominate. Strategy assumes normal distribution; crypto is fat-tailed.
**Prevention:** BB Mean Reversion DISABLED permanently. Document in RISKS.md disabled strategies table.

### [2026-03-23] Forex Expansion — All Negative
**What happened:** Expanded to forex majors (EUR/USD, USD/JPY, AUD/USD, etc.). Every strategy produced negative returns.
**Root cause:** Forex majors have extremely tight ranges and high institutional competition. Our strategies need volatility to profit.
**Prevention:** Only gold works on OANDA. Don't expand forex beyond GBP_USD London breakout.

### [2026-03-22] Chandelier Trailing Stop — Killed Trend Followers
**What happened:** Applied chandelier exit at 3x ATR to all strategies. Trend-following strategies (EMA, Ichimoku, TSMOM) had winners cut short.
**Root cause:** 3x ATR is too tight for trend-followers in crypto. Normal volatility triggers the stop before the trend completes.
**Prevention:** Tune trailing stops PER STRATEGY TYPE: wide (3x+ ATR) for trend-followers, tight (1.5-2x) for mean reversion.

### [2026-03-20] EMA 200 Trend Filter on Mean Reversion
**What happened:** Added EMA 200 as hard filter on RSI mean reversion. Killed most signals.
**Root cause:** Mean reversion explicitly trades AGAINST the trend. Requiring trend alignment defeats the purpose.
**Prevention:** EMA 200 as conviction MODIFIER only, never hard gate. Volume filters same rule.

## System Mistakes

### [2026-03-26] Async CCXT — to_thread() Bug
**What happened:** engine.py called CCXT exchange methods via asyncio.to_thread() instead of await. Caused silent failures on fetch_balance, cancel_order, fetch_open_orders.
**Root cause:** CCXT async methods return coroutines. to_thread() wraps sync functions. Mixing them = coroutine never awaited.
**Prevention:** ALL async CCXT calls MUST use `await exchange.method()`. NEVER use `asyncio.to_thread()` for CCXT.

### [2026-03-26] OANDA Thread Safety — Daemon Freeze
**What happened:** Trading daemon froze completely. No logs, no errors, just hung.
**Root cause:** oandapyV20 uses requests.Session which is NOT thread-safe. Multiple concurrent OANDA API calls caused deadlock.
**Prevention:** Use `asyncio.Semaphore(2)` on OANDAAdapter._execute_request. Max 2 concurrent OANDA calls. Implemented in start_daemon.py.

### [2026-03-26] Windows Daemon — Process Died After Terminal Close
**What happened:** Started daemon with nohup/disown. Process died when terminal closed.
**Root cause:** Windows doesn't support nohup/disown for background processes.
**Prevention:** Use `subprocess.Popen` with `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` flags. Implemented in start_daemon.py.

### [2026-03-25] Multi-Daemon Bug — Duplicate Instances
**What happened:** Multiple daemon instances running simultaneously, creating duplicate orders.
**Root cause:** No single-instance enforcement. Each terminal launch created a new daemon.
**Prevention:** PID file check on startup. Kill existing daemon before starting new one.

### [2026-03-20] Micro Account Position Sizing — $2 Trades
**What happened:** Risk-per-trade at 1.5% on $136 account = $2 positions. Useless.
**Root cause:** Standard position sizing assumes reasonable account size. Micro accounts need different rules.
**Prevention:** Micro accounts (<$500): 8% risk, risk-budget sizing, protocol caps advisory-only.

## Tax Mistakes

### [2026-03-27] RRSP Contribution Below $55K — Net Loss
**What happened:** (Prevented, not made) Analysis showed contributing to RRSP at 25.55% marginal rate and withdrawing at 29.65%+ = net loss.
**Root cause:** RRSP deduction is worth the marginal rate at contribution. If future withdrawal rate is higher, you lose.
**Prevention:** Only contribute to RRSP when marginal rate >= 29.65% ($55,867+ income). Below that, TFSA and FHSA are superior.

### [2026-03-27] USDT Pairs — Ontario Restriction
**What happened:** Attempted to trade USDT pairs on Kraken. Not available in Ontario.
**Root cause:** Ontario Securities Commission restricts USDT. Must use /USD suffix for all pairs.
**Prevention:** ALL Kraken pairs must use /USD suffix. Hardcoded in config.
