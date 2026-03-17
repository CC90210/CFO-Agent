# ATLAS LONG-TERM MEMORY — High-Confidence Persistent Facts

> Only facts with confidence >= 0.8 belong here. Reviewed monthly.

## Architecture Facts

| Fact | Confidence | Source | Last Verified |
|------|-----------|--------|---------------|
| 12 strategies registered: RSI, EMA, Bollinger, VWAP, multi-TF, London, opening range, smart money, Ichimoku, order flow, z-score, volume profile | 0.95 | Code + tests | 2026-03-17 |
| Regime detector classifies BULL_TREND, BEAR_TREND, CHOPPY, HIGH_VOL using Sharpe, ADX, volatility ratio | 0.95 | Implemented + backtested | 2026-03-17 |
| Regime filter improves backtest returns across all strategies | 0.90 | A/B backtest comparison | 2026-03-17 |
| Trailing stops disabled by default — too aggressive for trend-followers at 3x ATR | 0.95 | Backtest evidence | 2026-03-17 |
| Trade protocol (10-step) exists but NOT wired into engine | 0.95 | Code review | 2026-03-17 |
| Correlation tracker exists but NOT wired into risk manager | 0.95 | Code review | 2026-03-17 |
| 140 tests passing (all strategies + risk manager + position sizer) | 0.95 | pytest output | 2026-03-17 |
| Backtest engine has regime_filter=True, trailing_stops=False by default | 0.95 | Code | 2026-03-17 |

## Trading Safety Facts (NON-NEGOTIABLE)

| Fact | Confidence | Source | Last Verified |
|------|-----------|--------|---------------|
| Max drawdown: 15% — all trading halts | 1.00 | Hardcoded in risk_manager.py | 2026-03-16 |
| Daily loss limit: 5% — stop for the day | 1.00 | Hardcoded in risk_manager.py | 2026-03-16 |
| Per-trade risk: 1.5% max | 1.00 | Hardcoded in risk_manager.py | 2026-03-16 |
| Min conviction: 0.3 (30%) | 1.00 | Hardcoded in backtest + engine | 2026-03-16 |
| Risk score veto threshold: > 7 | 1.00 | agents/risk_agent.py | 2026-03-16 |
| Kill switches in core/risk_manager.py are UNTOUCHABLE | 1.00 | CLAUDE.md | 2026-03-16 |

## Strategy-Specific Facts

| Fact | Confidence | Source | Last Verified |
|------|-----------|--------|---------------|
| Ichimoku MUST use strict 5/5 conditions — 4/5 caused -91% | 1.00 | Backtest disaster | 2026-03-17 |
| RSI oversold=25, overbought=75, ATR stop=2.5x gives best results | 0.85 | Backtest +3.28% | 2026-03-17 |
| EMA crossover confirmation bar delay reduces fakeouts | 0.80 | Backtest observation | 2026-03-17 |
| Short positions get 15% size reduction (higher tail risk) | 0.85 | Portfolio manager config | 2026-03-17 |
| Adaptive R:R: <40% WR → 3.5:1, <50% → 3:1, <60% → 2:1, 60%+ → 1.5:1 | 0.85 | Portfolio manager config | 2026-03-17 |

## Backtest Results (BTC/USDT 4H, WITH regime filter)

| Strategy | Return | Win Rate | Trades | Regime Impact |
|----------|--------|----------|--------|---------------|
| Volume Profile | +4.95% | 40% | 15 | +4.95% vs +6.43% raw |
| Multi-Timeframe | +4.66% | ~28% | 7 | +4.66% vs +7.81% raw |
| RSI Mean Reversion | +2.71% | 33% | 3 | Improved from +1.75% raw |
| Ichimoku Trend | +0.38% | 31% | 13 | Slight reduction |
| EMA Crossover | -0.70% | ~17% | 12 | Improved from -1.52% raw |
| Smart Money | -2.87% | — | 2 | Improved from -3.37% raw |

## Confidence Decay Rules

- Facts not re-verified in 30 days: confidence -= 0.1
- Facts contradicted by new evidence: immediately flag and update
- Facts confirmed by new evidence: confidence += 0.05 (cap at 1.0)
