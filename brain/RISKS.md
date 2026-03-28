---
name: ATLAS Risk Controls
description: Kill switches, position limits, drawdown rules — NON-NEGOTIABLE safety layer
tags: [risk, safety, kill-switches, limits]
---

# ATLAS Risk Controls

> These limits are HARDCODED. They cannot be overridden by any signal, strategy, or agent.
> Changing these requires CC's explicit authorization AND code changes in core/risk_manager.py.

## Trading Kill Switches

| Control | Limit | Action | ITA Reference |
|---------|-------|--------|---------------|
| Max Drawdown | 15% | ALL trading halts | — |
| Daily Loss Limit | 5% | Stop trading for the day | — |
| Per-Trade Risk | 1.5% max | Position sizing cap | — |
| Min Conviction | 0.3 (30%) | No trade below threshold | — |
| Correlation Limit | Max 3 correlated positions | Block new correlated entries | — |

## Position Sizing Rules

### Standard Account (>$1,000)
- Risk per trade: 1.5% of equity
- Max positions: 6 concurrent
- Max single-asset exposure: 25% of equity

### Micro Account (<$500, current situation)
- Risk per trade: 8% of equity (adjusted for viability)
- Risk-budget sizing model
- Protocol caps are advisory (not hard blocks)
- Rationale: 1.5% of $136 = $2 trades = useless

## Strategy-Specific Controls

| Strategy Type | Trailing Stop | Regime Filter | Notes |
|--------------|--------------|---------------|-------|
| Trend Following (EMA, Ichimoku, TSMOM) | Wide (3x+ ATR) | BULL_TREND only | Chandelier at 3x ATR kills trend-followers |
| Mean Reversion (RSI, Z-score) | Tight (1.5-2x ATR) | CHOPPY preferred | Quick exits on reversion failure |
| Breakout (London, Opening Range) | Medium (2x ATR) | Any non-HIGH_VOL | Volatility expansion expected |
| Volume-Based (VWAP, Volume Profile) | Medium (2x ATR) | Any | Institutional flow confirmation |

## Disabled Strategies

| Strategy | Reason | Session Disabled |
|----------|--------|-----------------|
| BB Mean Reversion | ALL symbols -20% to -27% | Session 15 |
| Scale-Out Tiers | -5% to -20% drag on crypto returns | Session 12 |
| Forex Majors (except GBP_USD London) | ALL negative across every strategy | Session 17 |

## Tax Risk Controls

| Risk | Mitigation | Priority |
|------|-----------|----------|
| Unreported crypto income | VDP before CARF 2026 | HIGH |
| T1135 threshold breach | Monitor foreign property cost basis quarterly | MEDIUM |
| Superficial loss rule violation | 31-day tracking on all crypto sells | HIGH |
| GAAR on international structures | Genuine substance required, not paper entities | MEDIUM |
| CRA audit | Documentation-first approach, 6-year retention | ONGOING |
| Departure tax miscalculation | Snapshot unrealized gains quarterly | LOW (future) |

## Emergency Procedures

### Market Crash (>10% single-day drop)
1. All trailing stops activate automatically
2. No new positions for 24 hours
3. Review correlation exposure
4. Atlas alerts CC via Telegram

### CRA Audit Notice
1. Do NOT respond to CRA without reviewing
2. Engage tax lawyer (solicitor-client privilege)
3. Gather all documentation per ATLAS_CRA_AUDIT_DEFENSE.md
4. Consider VDP if unreported items exist (before audit scope widens)

### Broker API Failure
1. OANDA: Semaphore(2) prevents thread-safety crashes
2. Kraken: Async CCXT with proper await (not asyncio.to_thread)
3. All orders have timeout protection
4. Telegram alert on connection failure
