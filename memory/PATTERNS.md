---
name: ATLAS Patterns
description: Validated and probationary approaches — proven methods and emerging best practices
tags: [patterns, validated, probationary, best-practices]
---

# ATLAS Patterns

> [VALIDATED] = proven in 3+ sessions. Trust these.
> [PROBATIONARY] = 1-2 observations. Promising but needs more evidence.
> [UNDER_REVIEW] = caused issues. Investigate before using again.

---

## Trading Patterns

### [VALIDATED] Regime-Aware Strategy Filtering
Regime detector classifies market as BULL/BEAR/CHOPPY/HIGH_VOL. Each strategy has per-regime weight multipliers. Backtests WITH regime filtering consistently outperform backtests without.
**Evidence:** Sessions 8, 10, 12, 15 — every strategy improved with regime awareness.

### [VALIDATED] Regime Hysteresis (min_hold_bars=6)
Don't flip regime classification on every bar. Use minimum 6-bar hold period. Reduces false regime transitions by 51%.
**Evidence:** Sessions 14, 16, 18.

### [VALIDATED] Volume as Conviction Modifier, Not Hard Gate
Volume filters should modify conviction scores, not block trades entirely. Hard volume gates killed too many valid signals.
**Evidence:** Sessions 12, 14, 17.

### [VALIDATED] Per-Strategy Trailing Stop Tuning
Trend-followers need wide stops (3x+ ATR). Mean reversion needs tight stops (1.5-2x ATR). One-size-fits-all kills either trend or reversion returns.
**Evidence:** Sessions 10, 12, 15, 18.

### [VALIDATED] /USD Suffix for Ontario Crypto
USDT restricted in Ontario. All Kraken pairs must use /USD suffix.
**Evidence:** Sessions 6, 8, 11.

### [VALIDATED] Single Daemon Instance
Only one trading daemon at a time. PID file check on startup. Multiple daemons create duplicate orders.
**Evidence:** Sessions 18, 19.

### [VALIDATED] Async CCXT — Always Await
CCXT async methods must use `await`, never `asyncio.to_thread()`. Multiple bugs traced to this.
**Evidence:** Sessions 17, 18.

### [VALIDATED] OANDA Semaphore(2)
Max 2 concurrent OANDA API calls. oandapyV20 requests.Session is not thread-safe.
**Evidence:** Sessions 18, 19.

### [VALIDATED] Portfolio Tightening > Portfolio Expansion
Removing losing strategies/pairs (+110% improvement) is more valuable than adding new ones.
**Evidence:** Sessions 15, 17.

### [PROBATIONARY] Gold Outperforms Forex
OANDA gold (XAU_USD) validates across multiple strategies. Forex majors all negative.
**Evidence:** Sessions 17, 18. Needs more data.

### [PROBATIONARY] Donchian on Gold — Best Performer
Donchian trend-following on XAU_USD: +10.93% backtest, Monte Carlo 0% ruin probability.
**Evidence:** Session 17. Single backtest — needs live validation.

### [PROBATIONARY] London Breakout on GBP_USD — 67% Win Rate
London session breakout strategy on GBP_USD shows 67% win rate in backtest.
**Evidence:** Session 18. Single backtest.

## Tax Patterns

### [VALIDATED] FHSA > TFSA > RRSP Priority Order
For CC at current income: FHSA first (deduction + tax-free growth + tax-free withdrawal), TFSA second (tax-free growth), RRSP third (only when marginal rate >= 29.65%).
**Evidence:** Sessions 20, 21, 22. Consistent across all analysis.

### [VALIDATED] Deduct NOW, Not Later
Business deductions are worth more NOW (save tax + invest the savings) even if marginal rate is lower. Time value of the tax savings outweighs waiting for a higher bracket.
**Evidence:** Sessions 21, 22.

### [VALIDATED] Crypto ACB — Weighted Average Only
CRA requires weighted-average method for crypto ACB. Not FIFO, not LIFO, not specific identification (despite some tools offering these). Weighted average across ALL wallets and exchanges.
**Evidence:** Sessions 13, 20, 22.

### [PROBATIONARY] Start SR&ED Tracking Before Incorporation
T661 claims are based on when R&D occurred, not when entity existed. Track R&D hours and activities NOW for potential retroactive claim post-incorporation.
**Evidence:** Session 23 (income scaling playbook analysis).

### [PROBATIONARY] Irish Passport as Free Option
Apply for Irish citizenship via Foreign Births Registry (€278, 6-12 months). Zero downside, unlocks EU + 6.25% KDB rate if ever needed.
**Evidence:** Session 23 (Crown Dependencies analysis).

### [PROBATIONARY] Departure Tax Window — Act While Assets Are Small
Departure tax (s.128.1) is based on FMV at time of departure. CC's current asset base is minimal (~$0 departure tax). Window closes as OASIS and crypto appreciate.
**Evidence:** Session 23 (single analysis).

## System Patterns

### [VALIDATED] Windows Daemon Launch
Use subprocess.Popen with DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP flags. nohup/disown doesn't work on Windows.
**Evidence:** Sessions 18, 19.

### [VALIDATED] Read Before Edit
Always read files before editing. Never guess at method signatures, class structures, or file contents.
**Evidence:** Multiple sessions — core development principle.

### [VALIDATED] Backtest -> Paper Trade -> Live
Never skip the pipeline. Strategies must prove themselves at each stage before promotion.
**Evidence:** Core principle, validated across all strategy deployments.
