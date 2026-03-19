# ATLAS Execution Protocol v1.0

> The definitive step-by-step decision framework for every trade ATLAS executes.
> This protocol is NON-NEGOTIABLE. Every step must pass before capital is risked.

---

## Pre-Session Checklist (Run Once Per Session Start)

### 1. System Health Check

- Verify exchange API connectivity (CCXT ping — reject if latency > 2000ms)
- Confirm database is accessible and writeable (test INSERT + ROLLBACK)
- Check available capital balance (log starting equity for daily P&L tracking)
- Verify all kill switches are ACTIVE in `core/risk_manager.py`:
  - Max drawdown gate: **15%**
  - Daily loss gate: **5%**
  - Per-trade risk ceiling: **1.5%**
- Confirm `paper_trade` mode matches intent — DOUBLE CHECK before any live session
- Load strategy health states from database (`StrategyHealthMonitor` — Darwinian monitor)
- If ANY health check fails → ABORT session, alert via Telegram, do NOT proceed

### 2. Market Context Assessment

- Run `RegimeDetector` → classify market as one of:
  - `BULL_TREND` — sustained higher highs, price above 200 EMA
  - `BEAR_TREND` — sustained lower lows, price below 200 EMA
  - `CHOPPY` — range-bound, no directional structure
  - `HIGH_VOL` — ATR spike > 2 standard deviations above 30-day average
- Run `MomentumClassifier` → identify cycle phase:
  - `ACCUMULATION` — smart money loading, low volatility base
  - `MARKUP` — trend emergence, increasing volume
  - `DISTRIBUTION` — institutions selling into retail strength
  - `MARKDOWN` — active downtrend
  - `REVERSAL` — inflection point, high uncertainty
  - `RANGE_BOUND` — mean reversion conditions
- Run `CorrelationTracker` → refresh 30-day rolling correlation matrix across all watched symbols
- Note current UTC hour → apply session filter (London: 07:00–16:00 UTC, NY: 13:00–22:00 UTC, Asia: 00:00–09:00 UTC)
- Log regime + phase + session to database as session context record

---

## Per-Tick Decision Loop (Every Candle Close)

Execute the following 10 steps in strict order. Any REJECT or SKIP terminates the loop for that signal. Move to the next strategy.

---

### Step 1: Regime Gate

**Purpose:** Prevent running trend strategies in choppy markets, or mean-reversion strategies in strong trends.

- Fetch latest regime classification from `RegimeDetector`
- If `HIGH_VOL` AND current drawdown > 5% → **SKIP ALL TRADES** (capital preservation mode — log reason)
- Look up this strategy's regime weight from the Strategy-Regime Matrix (see below)
- If weight = 0 (❌ Skip) → **SKIP** — do not proceed to Step 2
- Store regime weight multiplier for use in Steps 5 and 7

**Gate passes if:** Strategy is cleared to run in the current regime.

---

### Step 2: Playbook Gate (8-Rule Matrix)

**Purpose:** Filter out structurally poor trade conditions before any signal analysis.

Evaluate all 8 rules. If `should_trade = false` on any rule → **SKIP**.

| Rule | Check | Fail Condition |
|------|-------|----------------|
| 1. Regime Alignment | Is this strategy designed for this regime? | Weight = 0 in matrix |
| 2. Volatility Filter | Is ATR within strategy's operating range? | ATR outside min/max thresholds |
| 3. Session Filter | Is this the right session for this strategy? | Wrong UTC hour range |
| 4. Streak Protection | Recent consecutive losses? | 3+ losses → 50% size; 5+ → pause |
| 5. Sentiment Check | Extreme fear/greed index reading? | Score < 15 or > 85 → contrarian filter |
| 6. Macro Awareness | Major news event within 4 hours? | FOMC / CPI / NFP → reduce exposure 50% |
| 7. Correlation Limit | Correlated positions already open? | > 3 positions with r > 0.7 |
| 8. Drawdown Scaling | How close to daily/max drawdown limit? | Linear size reduction as limit approaches |

Log which rules triggered and why. The playbook gate is the highest-volume filter — most skips happen here.

**Gate passes if:** All 8 rules return `should_trade = true` (or a size reduction, not a full skip).

---

### Step 3: Strategy Health Gate (Darwinian)

**Purpose:** The Darwinian agent evolves strategy weights over time based on live performance. Respect its verdicts.

- Call `StrategyHealthMonitor.should_trade(strategy_name)` → returns `(should_trade: bool, size_multiplier: float, reason: str)`

| Health State | Action | Size Multiplier |
|-------------|--------|----------------|
| `ACTIVE` | Proceed | 1.0x |
| `WARNING` | Proceed with caution | Per monitor (typically 0.7x) |
| `PROBATION` | Proceed, reduced size | 0.5x |
| `COOLDOWN` | **SKIP entirely** | 0.0x |
| `DISABLED` | **SKIP entirely** | 0.0x |

- Store `size_multiplier` for use in Step 7
- Log reason for any gate action to database
- Do NOT override a `COOLDOWN` or `DISABLED` verdict — the Darwinian agent earned these conclusions through observed losses

**Gate passes if:** Health state is `ACTIVE`, `WARNING`, or `PROBATION`.

---

### Step 4: Signal Generation

**Purpose:** Ask the strategy if there is actually a trade setup in the current data.

- Call `strategy.analyze(df)` → returns `Signal` object or `None`
- If `None` → no setup detected, **SKIP** (this is normal — most candles produce no signal)
- A valid `Signal` must contain all of the following fields:

```
Signal:
  direction:    LONG | SHORT
  conviction:   float  (-1.0 to 1.0)
  entry_price:  float
  stop_loss:    float
  take_profit:  float
  metadata:     dict   (strategy-specific context)
```

- If any required field is missing or malformed → **REJECT** signal, log malformed signal error

**Gate passes if:** Strategy returns a well-formed Signal object.

---

### Step 5: Conviction Filter

**Purpose:** Ensure the combined signal strength — adjusted for current conditions — clears the minimum threshold.

- Start with raw conviction from Step 4
- Apply regime multiplier (from Step 1): `conviction × regime_weight`
- Apply sentiment risk modifier from `SentimentAnalyzer` (e.g., 0.8x in extreme conditions)
- Apply playbook size multiplier from Step 2 streak/macro rules
- Final conviction = `raw_conviction × regime_weight × sentiment_modifier × playbook_multiplier`
- If final conviction < **0.3** → **REJECT** signal

Minimum conviction of 0.3 is a hard floor. A signal that clears 0.30001 after adjustments is valid. A signal at 0.299 is rejected. No exceptions.

**Gate passes if:** Final adjusted conviction ≥ 0.3.

---

### Step 6: Risk Assessment

**Purpose:** Verify the trade structure meets all risk requirements before sizing.

Perform each check in order. Any single failure → **REJECT**.

1. **Per-trade risk check:** `(entry_price - stop_loss) / entry_price ≤ 0.015` (1.5% max)
2. **R:R ratio check:** `(take_profit - entry_price) / (entry_price - stop_loss) ≥ 2.0` — prefer 3.0+
3. **Daily loss budget:** `today's realized losses < 5% of starting equity`
4. **Open positions limit:** `current open positions < 5`
5. **Correlation check:** Query `CorrelationTracker` — reject if adding this position would exceed 3 correlated positions at r > 0.7
6. **Kill switch status:** Confirm `risk_manager.can_trade()` returns `True`

Log which check failed and the values that triggered the rejection.

**Gate passes if:** All 6 checks pass.

---

### Step 7: Position Sizing (Half-Kelly)

**Purpose:** Size the position mathematically to maximize long-run growth without risking ruin.

Calculate in this order:

```
1. Kelly fraction:
   K = (win_rate × avg_win_R - loss_rate × avg_loss_R) / avg_win_R

2. Half-Kelly (safety margin):
   base_fraction = 0.5 × K

3. Apply regime multiplier (Step 1):
   fraction = base_fraction × regime_weight
   (reduce to 0.5x in CHOPPY or HIGH_VOL)

4. Apply sentiment multiplier:
   fraction = fraction × sentiment_modifier

5. Apply streak discount (Step 2, Rule 4):
   fraction = fraction × streak_discount

6. Apply Darwinian size multiplier (Step 3):
   fraction = fraction × darwinian_size_multiplier

7. Enforce floor:
   fraction = max(fraction, exchange_minimum_position)

8. Enforce ceiling — per-trade risk cap:
   max_position = (portfolio_value × 0.015) / stop_distance
   final_size = min(fraction × portfolio_value / entry_price, max_position)
```

Use the strategy's historical win rate and R values from the backtesting database. If fewer than 20 trades exist for this strategy, use conservative defaults: `win_rate = 0.4`, `avg_win_R = 2.0`, `avg_loss_R = 1.0`.

**Output:** `final_size` in base asset units, ready for order placement.

---

### Step 8: Entry Execution

**Purpose:** Enter the position cleanly, without chasing price.

- Verify entry price has not moved more than 0.5 ATR from the signal's `entry_price` since signal generation. If it has → **SKIP** (do not chase)
- Place a **limit order** at `signal.entry_price` — never use market orders (slippage control)
- Set a **30-second fill timeout**
- If order not filled within 30 seconds → cancel order, **SKIP** — do not adjust price to chase
- On fill confirmation, log:

```
entry_log:
  symbol, strategy, direction, size, entry_price,
  stop_loss, take_profit, conviction (adjusted),
  regime, session, timestamp, order_id
```

**Execution passes if:** Limit order fills within 30 seconds at or better than signal price.

---

### Step 9: Position Management (Post-Entry)

**Purpose:** Protect capital immediately, then let the trade develop according to its plan.

**Immediately after fill:**

1. Place stop-loss order on exchange (do NOT rely on software-side stops alone)
2. Activate trailing stop — select method based on strategy type:

| Strategy Type | Trailing Method | Multiplier | Rationale |
|--------------|----------------|------------|-----------|
| Trend Following (EMA Crossover, Multi-TF, Ichimoku) | Chandelier Exit | 3.0x ATR | Wide — trends need room to breathe |
| Mean Reversion (RSI, Z-Score, VWAP Bounce) | ATR Trail | 1.5x ATR | Tight — lock in reversion profits quickly |
| Breakout (Bollinger Squeeze, London Breakout, Opening Range) | Parabolic SAR | Default | Accelerates naturally as move extends |
| Structure (Smart Money, Order Flow, Volume Profile) | Composite | Blend | Votes across all methods for best level |

**Scale-out plan (execute at each tier):**

| Tier | Trigger | Action |
|------|---------|--------|
| 1 | +1R profit | Close 30% of position — lock in first gains |
| 2 | +2R profit | Close 30% of position — confirm momentum |
| 3 | Trailing stop | Trail remaining 40% — let winners run |

**Break-even promotion:** Move stop to entry price (zero-loss) immediately after Tier 1 is hit. From this point, the worst outcome is breakeven on the remaining position.

**Monitoring on each subsequent candle:**
- Check trailing stop level — update exchange stop order if level has moved in favor
- Check if daily/max drawdown limits were hit by this or other positions
- Check for opposing signal from strategy (early exit consideration)

---

### Step 10: Exit and Post-Mortem

**Purpose:** Close the loop — record results and feed the learning system.

**On position close (any reason):**

1. Record exit to database:
   ```
   exit_log:
     exit_price, realized_pnl, pnl_pct, duration_hours,
     exit_reason (TP_TIER1 | TP_TIER2 | TRAILING_STOP | STOP_LOSS | TIME_STOP | MANUAL),
     r_multiple_achieved
   ```

2. Update `StrategyHealthMonitor`:
   - Call `monitor.refresh(strategy_name, trade_result)`
   - Win: multiply Darwinian weight by **1.08x**
   - Loss: multiply Darwinian weight by **0.90x**
   - Consecutive losses tracked for streak protection (Rule 4)

3. Update walk-forward validation dataset (append trade to rolling window)

4. Check session-level kill conditions:
   - If `today's total losses ≥ 5% of starting equity` → **HALT all trading for the day**, send Telegram alert
   - If `portfolio drawdown ≥ 15%` → **HALT all trading**, send Telegram alert, flag for manual review — do NOT auto-resume

5. Log post-mortem summary to `SESSION_LOG.md` at session end (see Memory System conventions)

---

## Risk Management Non-Negotiables

These rules CANNOT be overridden by any signal, strategy, agent, or instruction.

| Rule | Limit | Action When Breached |
|------|-------|---------------------|
| Max Drawdown | 15% | ALL trading halts immediately — manual review required to resume |
| Daily Loss | 5% | Stop trading for the remainder of the calendar day |
| Per-Trade Risk | 1.5% | Reject any trade that would risk more than this |
| Min Conviction | 0.3 | Reject any signal below this after all adjustments |
| Min R:R Ratio | 2.0 | Reject any setup with reward less than 2x the risk |
| Max Open Positions | 5 | Queue signals — do not open a 6th position |
| Max Correlated Positions | 3 at r > 0.7 | Reject correlated entries beyond this limit |
| Consecutive Loss Pause | 5 losses | Pause strategy, enter COOLDOWN state |
| Kill Switch — Manual | Telegram /stop | Immediately halts all trading activity |

These limits live in `core/risk_manager.py`. Do NOT modify these values without explicit instruction from CC. Do NOT route around them with try/except blocks or conditional logic.

---

## Strategy-Regime Matrix

Defines which strategies are active in each market regime and at what position size.

| Strategy | BULL_TREND | BEAR_TREND | CHOPPY | HIGH_VOL |
|----------|-----------|-----------|---------|----------|
| EMA Crossover | Full | Full | Skip | Half |
| RSI Mean Reversion | Half | Half | Full | Skip |
| Bollinger Squeeze | Half | Half | Full | Full |
| Multi-Timeframe | Full | Full | Skip | Half |
| Ichimoku Trend | Full | Full | Skip | Skip |
| VWAP Bounce | Half | Half | Full | Skip |
| London Breakout | Full | Full | Half | Full |
| Opening Range | Full | Full | Half | Full |
| Smart Money | Full | Full | Skip | Half |
| Order Flow Imbalance | Half | Half | Full | Full |
| Z-Score Reversion | Half | Half | Full | Skip |
| Volume Profile | Half | Half | Full | Skip |

**Legend:** Full = 1.0x position size | Half = 0.5x position size | Skip = do not trade

---

## Trailing Stop Configuration Per Strategy

| Strategy | Type | Method | Multiplier | Notes |
|----------|------|--------|------------|-------|
| EMA Crossover | Trend Following | Chandelier Exit | 3.0x ATR | Trends need room — 3x prevents premature exits |
| Multi-Timeframe | Trend Following | Chandelier Exit | 3.0x ATR | Same rationale — multi-TF trends are persistent |
| Ichimoku Trend | Trend Following | Chandelier Exit | 3.0x ATR | Ichimoku signals are slow-burn; never tighten |
| RSI Mean Reversion | Mean Reversion | ATR Trail | 1.5x ATR | Reversion plays are short-duration — take profits |
| Z-Score Reversion | Mean Reversion | ATR Trail | 1.5x ATR | Statistical reversion — exit before mean re-breaks |
| VWAP Bounce | Mean Reversion | ATR Trail | 1.5x ATR | VWAP bounces resolve quickly; tight trail is correct |
| Bollinger Squeeze | Breakout | Parabolic SAR | Default | SAR accelerates naturally with momentum |
| London Breakout | Breakout | Parabolic SAR | Default | Session breakouts trend hard — SAR keeps pace |
| Opening Range | Breakout | Parabolic SAR | Default | Same as London — impulse moves need SAR |
| Smart Money | Structure | Composite | Blend | Structure levels are complex — composite wins |
| Order Flow Imbalance | Structure | Composite | Blend | CVD signals have mixed duration — composite best |
| Volume Profile | Structure | Composite | Blend | VAH/VAL/POC setups vary widely — composite adapts |

**CRITICAL NOTE:** Do NOT change Chandelier multipliers below 3.0x for trend-following strategies. Historical testing showed that 2.5x or lower kills winning trades prematurely and degrades returns significantly. This is documented in `memory/feedback_trailing_stops.md`.

**CRITICAL NOTE:** Do NOT relax Ichimoku entry conditions from 5/5 to 4/5. This caused a -91% backtest result when previously attempted. This is documented in `memory/feedback_ichimoku_strict.md`.

---

## Edge Preservation Rules

These rules protect the statistical edge that makes this system profitable over time. Violating them converts a positive-expectancy system into a gambling operation.

1. **Never chase** — If entry price has moved more than 0.5 ATR from the signal price, the setup is gone. Skip it. The next one will come.

2. **Never average down** — Adding to a losing position is not a strategy. It is hope. The stop-loss is the exit plan. Use it.

3. **Never remove a stop-loss** — A stop-loss exists precisely for the moment you want to remove it. Under no circumstances is a live stop-loss removed.

4. **Never exceed position limits** — Five concurrent positions is the maximum regardless of signal quality. Capital concentration is tail-risk.

5. **Never trade during exchange maintenance** — Check exchange status API at session start. Partial fills and phantom orders during maintenance are unrecoverable.

6. **Never override the Darwinian agent** — When a strategy is in COOLDOWN or DISABLED, it earned that verdict through actual losses. Overriding it defeats the purpose of the self-improvement system.

7. **Always log everything** — Every decision, every skip, every gate pass, every trade, every exit reason. The log is the post-mortem feedstock. Unlogged decisions cannot be learned from.

8. **Review walk-forward results weekly** — Check Darwinian weights, review the bottom 3 performing strategies, validate that regime filter is improving results. Tune parameters only after backtesting the change first.

---

## Paper Trading Graduation Criteria

Before transitioning from paper trading to live capital, ALL of the following criteria must be met. No single criterion can be waived.

- [ ] 30+ consecutive calendar days of paper trading completed
- [ ] Total P&L is positive over the 30-day period (not just the last week)
- [ ] Maximum drawdown stayed below **10%** during the 30 days (stricter than the 15% live kill switch)
- [ ] Win rate is **≥ 35%** measured across all strategies combined
- [ ] Profit factor is **≥ 1.3** across all strategies combined (gross profit / gross loss)
- [ ] At least **50 closed trades** in the dataset (minimum for statistical significance)
- [ ] Walk-forward validation shows no overfitting: out-of-sample score **< 0.3**
- [ ] Every active strategy has been running for at least **14 days** (Darwinian evolution needs time)
- [ ] Darwinian system has completed at least **3 full evolution cycles**
- [ ] CC has manually reviewed the top 10 winning trades and top 10 losing trades
- [ ] All Telegram alerts are confirmed working (critical for live monitoring)
- [ ] A written review of system behavior, anomalies, and parameter adjustments has been completed

When all boxes are checked, transition to live with a **reduced initial capital allocation** — not full portfolio. Scale capital in as confidence is validated by live results.

---

## Quick Reference: Decision Flow

```
CANDLE CLOSE
     │
     ▼
[Step 1] Regime Gate ──────────────────────────► SKIP (wrong regime)
     │ PASS
     ▼
[Step 2] Playbook Gate (8 rules) ──────────────► SKIP (conditions wrong)
     │ PASS
     ▼
[Step 3] Darwinian Health Gate ─────────────────► SKIP (COOLDOWN/DISABLED)
     │ PASS (ACTIVE / WARNING / PROBATION)
     ▼
[Step 4] Signal Generation ─────────────────────► SKIP (no setup)
     │ Signal returned
     ▼
[Step 5] Conviction Filter (≥ 0.3) ────────────► REJECT (too weak)
     │ PASS
     ▼
[Step 6] Risk Assessment (6 checks) ────────────► REJECT (risk violation)
     │ PASS
     ▼
[Step 7] Position Sizing (Half-Kelly) ──────────► Calculate final_size
     │
     ▼
[Step 8] Entry Execution (limit, 30s timeout) ──► SKIP (not filled / chasing)
     │ FILLED
     ▼
[Step 9] Position Management (stops + scale-out)
     │
     ▼
[Step 10] Exit + Post-Mortem (log + Darwinian update)
```

---

*ATLAS Execution Protocol v1.0 — March 2026*
*"Protect capital first. Compound gains second. Never gamble."*
