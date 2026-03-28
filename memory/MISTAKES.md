---
name: ATLAS Mistakes Log
description: Root cause analysis of every significant error — trading, tax, system — with prevention strategies
tags: [mistakes, errors, prevention, learning]
---

# ATLAS Mistakes Log

> Every mistake gets: what happened, root cause, prevention strategy.
> Read this BEFORE repeating a task type. Learn once, not twice.

---

## Trading Mistakes

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
