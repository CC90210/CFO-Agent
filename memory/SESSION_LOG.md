# ATLAS Session Log

## 2026-03-17 — Major Strategy Expansion + Regime Detection

**Goal:** Transform ATLAS into a profitable, elite trading system with cutting-edge strategies.

**Done:**
- Tuned 8 existing strategy parameters (RSI, EMA, Bollinger, VWAP, multi-TF, smart money, Ichimoku, London breakout, opening range)
- Built regime detector (BULL_TREND, BEAR_TREND, CHOPPY, HIGH_VOL) with per-strategy weight multipliers
- Fixed 12 systemic weaknesses in multi-agent consensus system (top 4 fixed)
- Built 3 new strategies: order flow imbalance, z-score mean reversion, volume profile
- Built trade protocol (10-step decision framework) — not yet wired into engine
- Built correlation tracker (rolling 30-day matrix) — not yet wired into risk manager
- Built adaptive trailing stop system (Chandelier, Parabolic SAR, ATR-trail, composite) — disabled by default
- Wired regime detector into backtest engine — improves returns across the board
- All 12 strategies registered in __init__.py, strategies.yaml, and regime detector weights
- 140 tests passing
- Updated CLAUDE.md, GEMINI.md, ANTIGRAVITY.md with current architecture

**Key Findings:**
- RSI Mean Reversion: -3.79% → +2.71% (with regime filter)
- EMA Crossover: -1.52% → -0.70% (with regime filter)
- Regime filter helps mean-reversion strategies most (suppresses them in bear trends)
- Trailing stops at 3x ATR are TOO AGGRESSIVE for trend-followers (multi-TF went +7.81% → -1.29%)
- Ichimoku at 4/5 conditions = CATASTROPHIC (-91%, 501 trades). Must stay strict 5/5.

**Issues:**
- Trailing stops need per-strategy tuning before enabling
- Trade protocol not wired into main engine loop
- Correlation tracker not wired into risk manager
- Smart money strategy has 0% win rate (low trade count, needs more data)

**Next:**
1. Tune trailing stops per strategy type (wide for trend, tight for MR)
2. Wire trade_protocol.py into core/engine.py
3. Wire correlation_tracker.py into risk_manager.py
4. Run multi-day paper trading with all 12 strategies
5. Backtest new strategies on multiple symbols/timeframes
6. Add more trading symbols

**Files Changed:**
- `strategies/technical/rsi_mean_reversion.py` — deeper thresholds, wider stops
- `strategies/technical/ema_crossover.py` — confirmation bar delay, lower ADX
- `strategies/technical/bollinger_squeeze.py` — 2-bar exit confirmation
- `strategies/technical/vwap_bounce.py` — wider ATR stop
- `strategies/technical/multi_timeframe.py` — wider stops
- `strategies/technical/smart_money.py` — wider OB tolerance, wider stops
- `strategies/technical/ichimoku_trend.py` — deeper cloud exit (50% penetration)
- `strategies/technical/london_breakout.py` — extended time window
- `strategies/technical/opening_range.py` — tighter gap filter
- `strategies/technical/order_flow_imbalance.py` — NEW
- `strategies/technical/zscore_mean_reversion.py` — NEW
- `strategies/technical/volume_profile.py` — NEW
- `strategies/technical/__init__.py` — registered 3 new strategies
- `core/regime_detector.py` — NEW: market regime classification
- `core/trade_protocol.py` — NEW: 10-step decision framework
- `core/correlation_tracker.py` — NEW: rolling correlation matrix
- `core/trailing_stop.py` — NEW: adaptive trailing stop system
- `backtesting/engine.py` — regime filter + trailing stop integration
- `agents/orchestrator.py` — neutral suppression, debate threshold, conviction×confidence
- `agents/portfolio_manager.py` — adaptive R:R, short bias, conviction×confidence sizing
- `agents/darwinian.py` — faster evolution weights
- `config/strategies.yaml` — all 12 strategies configured
- `CLAUDE.md` / `GEMINI.md` / `ANTIGRAVITY.md` — updated architecture + status

## 2026-03-16 — Initial Setup + Paper Trading Ready

**Goal:** First IDE session — verify project readiness, review architecture.
**Done:** Validated 140 tests passing, reviewed all components, confirmed paper trading ready.
**Issues:** 49 datetime.utcnow() deprecation warnings (non-critical)
**Next:** Start paper trading, tune strategies, add new strategies.
