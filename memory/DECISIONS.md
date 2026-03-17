# ATLAS Decision Log

## 2026-03-17 — Regime Detection as Core Architecture

**Context:** All strategies were losing money in backtests. Mean-reversion strategies performed terribly in trending markets, trend-followers failed in choppy markets.

**Options:**
1. Tune each strategy individually to handle all regimes
2. Add a regime detector that adjusts strategy weights dynamically
3. Run all strategies and let the portfolio manager sort it out

**Decision:** Option 2 — Regime detector classifies market as BULL_TREND/BEAR_TREND/CHOPPY/HIGH_VOL and assigns per-strategy weight multipliers. Strategies with weight <= 0.5 are suppressed entirely.

**Consequences:**
- RSI Mean Reversion improved from -3.79% to +2.71%
- EMA Crossover improved from -1.52% to -0.70%
- All strategies benefit from not trading in hostile regimes
- Regime detector is wired into both the live engine and backtest engine

---

## 2026-03-17 — Trailing Stops Disabled by Default

**Context:** Built a comprehensive trailing stop system (Chandelier, Parabolic SAR, ATR-trail) and wired it into the backtest engine.

**Options:**
1. Enable for all strategies with uniform 3x ATR
2. Enable per-strategy with different multipliers
3. Disable by default until properly tuned

**Decision:** Option 3 — Disabled by default. Backtest showed trailing stops HURT trend-following strategies (multi_timeframe: +7.81% → -1.29%) while helping mean-reversion (smart_money: -3.37% → +1.69%).

**Consequences:**
- `trailing_stops=False` is the default in BacktestEngine
- Must be tuned per-strategy type before enabling
- Trend-followers need 4-5x ATR; mean-reversion needs 1.5-2x ATR

---

## 2026-03-17 — Ichimoku Strict 5/5 Conditions

**Context:** Attempted to relax Ichimoku from 5/5 to 4/5 entry conditions to generate more trades.

**Options:**
1. Allow 4/5 conditions for more trade frequency
2. Keep strict 5/5 conditions

**Decision:** Option 2 — REVERTED immediately. 4/5 conditions caused 501 trades and -91% return. Ichimoku is a complete system; partial signals are noise.

**Consequences:** Ichimoku will always require ALL 5 conditions. Trade frequency is low (~13-22 trades per 1000 bars) but that's correct for a daily-designed system on 4H charts.
