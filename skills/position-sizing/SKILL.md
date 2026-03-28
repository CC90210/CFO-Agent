---
name: position-sizing
description: Risk-budget position sizing — Kelly criterion adaptation, micro account rules, per-strategy calibration
triggers: [position size, lot size, how much, risk per trade, Kelly, sizing, allocation, trade size]
tier: core
dependencies: []
---

# Position Sizing

## Overview
Determines how much capital to allocate to each trade. The #1 factor in long-term trading survival — more important than entry signals.

## When to Use
- Every trade signal (automated via risk_manager.py)
- When account size changes significantly
- When adjusting risk parameters
- When CC asks "how much should I risk?"

## The Process

### Phase 1: Account Classification
| Account Size | Classification | Risk Per Trade | Model |
|-------------|---------------|----------------|-------|
| < $500 | Micro | 8% | Risk-budget, advisory caps |
| $500 - $5,000 | Small | 3-5% | Standard risk-budget |
| $5,000 - $50,000 | Medium | 1.5-2% | Full Kelly fraction |
| > $50,000 | Large | 1-1.5% | Half-Kelly conservative |

### Phase 2: Risk-Budget Sizing (Primary Method)
```
Position Size = (Account Equity × Risk%) / (Entry Price - Stop Loss Price)
```

**Example (Micro Account):**
- Equity: $136
- Risk: 8% = $10.88
- Entry: BTC at $65,000
- Stop: $63,000 (ATR-based, $2,000 below entry)
- Position size: $10.88 / ($65,000 - $63,000) × $65,000 = $353.60
- In BTC terms: 0.00544 BTC

### Phase 3: Kelly Criterion Adaptation
```
Kelly% = (Win Rate × Avg Win / Avg Loss) - (1 - Win Rate) / (Avg Win / Avg Loss)
Half-Kelly = Kelly% / 2  (recommended — full Kelly is too aggressive)
```

**Only use Kelly when you have:**
- Minimum 30 trades of history for the strategy
- Stable win rate (not trending down)
- Consistent average win/loss ratio

### Phase 4: Strategy-Specific Adjustments

| Strategy Type | Sizing Modifier | Reason |
|--------------|----------------|--------|
| Trend Following | 0.8x base | Wider stops = larger position notional at same risk |
| Mean Reversion | 1.2x base | Tighter stops = can afford larger position |
| Breakout | 0.7x base | Higher false breakout rate |
| Volume Profile | 1.0x base | Standard |
| Multi-TF Momentum | 0.9x base | Multiple timeframe alignment reduces but doesn't eliminate risk |

### Phase 5: Correlation Check
Before sizing, check via correlation_tracker.py:
1. How many correlated positions are already open?
2. If new trade is correlated (r > 0.7) with existing position:
   - Reduce size by 50% if 1 correlated position exists
   - Skip if 2+ correlated positions exist
3. Effective position count = actual positions × average correlation

### Phase 6: Final Validation
- [ ] Position size ≤ 25% of account equity (single-asset cap)
- [ ] Total risk across all positions ≤ 15% of equity (portfolio cap)
- [ ] Daily loss limit not already hit (5%)
- [ ] Kill switches not triggered

## Key Rules
- NEVER risk more than the per-trade limit, regardless of conviction
- Conviction score modifies WITHIN the risk budget, doesn't override it
- High conviction (0.8+): full position size. Medium (0.5-0.8): 70%. Low (0.3-0.5): 50%
- Position size is calculated BEFORE entry, not adjusted after
- If the minimum viable position size exceeds risk limits: DO NOT TRADE

## Code Reference
- core/risk_manager.py — RiskManager.calculate_position_size()
- core/engine.py — position sizing integration
- core/correlation_tracker.py — correlation-adjusted sizing
