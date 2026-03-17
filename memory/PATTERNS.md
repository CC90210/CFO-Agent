# ATLAS LEARNED PATTERNS
> What works, what doesn't in trading strategy development and system tuning.
> Check this BEFORE making changes to strategies or the engine.
> `[VALIDATED]` = proven across backtests + live. `[PROBATIONARY]` = promising but needs more evidence.

## Strategy Development Patterns

### Regime-Aware Strategy Selection `[VALIDATED]`
**Context:** Running multiple strategies simultaneously
**Pattern:** 1) Classify market regime (BULL/BEAR/CHOPPY/HIGH_VOL) → 2) Assign weight multiplier per strategy → 3) Suppress strategies with weight <= 0.5 → 4) Scale conviction and position size by regime weight
**Why it works:** Mean-reversion strategies lose badly in trends, trend-followers whipsaw in ranges. Regime filter prevents the #1 source of losses.
**Evidence:** RSI Mean Reversion improved -3.79% → +2.71%. EMA Crossover improved -1.52% → -0.70%.
**Sessions validated:** 1 | **Last used:** 2026-03-17

### Wider Stop Losses Improve Win Rate `[VALIDATED]`
**Context:** Tuning any strategy's stop-loss distance
**Pattern:** Use 2.0-3.0x ATR stops instead of 1.0-1.5x. Accept lower R:R in exchange for fewer stop-outs from noise.
**Why it works:** Crypto and 4H timeframes have high intrabar noise. Tight stops get triggered by wicks that don't represent actual reversals.
**Evidence:** RSI stop mult 1.5→2.5 improved returns. EMA stop mult 2.0→3.0 reduced false stop-outs.
**Sessions validated:** 1 | **Last used:** 2026-03-17

### Confirmation Bar Delay `[PROBATIONARY]`
**Context:** Entry timing for crossover-based strategies
**Pattern:** Enter on the bar AFTER the crossover, not on the crossover bar itself. Check that the signal persists for 2 consecutive bars.
**Why it works:** Many crossovers reverse within 1 bar (fakeouts). Waiting 1 bar filters ~30% of false signals.
**Evidence:** Added to EMA crossover. Reduced false entries but total impact mixed in backtest.
**Sessions validated:** 1 | **Last used:** 2026-03-17

### Conviction × Confidence Sizing `[VALIDATED]`
**Context:** Position sizing from multi-agent consensus
**Pattern:** Size = Half-Kelly × |conviction| × max(confidence, 0.1) × risk_multiplier × direction_scalar
**Why it works:** High conviction with low confidence (disagreeing agents) should produce smaller sizes. Pure conviction ignores whether agents agree.
**Sessions validated:** 1 | **Last used:** 2026-03-17

### Neutral Signal Suppression `[VALIDATED]`
**Context:** Computing consensus from multiple analyst agents
**Pattern:** Exclude NEUTRAL signals from the consensus calculation entirely. Only directional signals contribute.
**Why it works:** NEUTRAL signals from cautious agents were diluting strong directional consensus, causing the system to pass on valid trades.
**Sessions validated:** 1 | **Last used:** 2026-03-17

## Anti-Patterns (NEVER DO THIS)

### Relaxing Ichimoku Conditions `[VALIDATED — DO NOT DO]`
**Context:** Ichimoku strategy generates few trades
**Anti-pattern:** Relaxing from 5/5 to 4/5 conditions
**Result:** 501 trades, -91% return. CATASTROPHIC.
**Why it fails:** Ichimoku is a complete system. Each condition filters different noise. Partial signals are pure noise.

### Uniform Trailing Stops `[VALIDATED — DO NOT DO]`
**Context:** Applying trailing stops to all strategies
**Anti-pattern:** Same Chandelier exit (3x ATR) for all strategy types
**Result:** Trend-followers went from +7.81% to -1.29%. Mean-reversion improved.
**Why it fails:** Trend-followers need to ride winners through pullbacks. Tight trailing stops create whipsaw.

### Mean Reversion in Bear Trends `[VALIDATED — DO NOT DO]`
**Context:** Running RSI/z-score mean reversion during downtrends
**Anti-pattern:** Buying oversold dips in a bear market
**Result:** Catching falling knives. "Oversold" keeps getting more oversold.
**Why it fails:** In bear trends, mean reversion = value trap. The regime detector prevents this.
