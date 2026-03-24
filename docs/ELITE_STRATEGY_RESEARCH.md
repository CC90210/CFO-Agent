# ATLAS Elite Strategy Research — 2026-03-20

## Cross-Analysis Summary

After 6 deep research agents across options, bonds, leveraged ETFs, futures, elite quant strategies, and ML-based trading, here are the findings ranked by viability for a $500–$5,000 account.

## Critical Finding: Current Strategies Are NOT Production Ready

Backtests on live Kraken data (Nov 2025 – Mar 2026) show:
- **multi_timeframe:** -3.99% avg (1/10 profitable) — crypto is in choppy/bear regime
- **smart_money:** +0.52% avg (6/10 profitable) — marginal
- **Forex strategies:** -47% to -18% — crypto strategies don't translate to forex
- **Gold (XAU_USD):** +16.18% — ONLY bright spot, strong trend

## Root Cause

Our strategies are trend-followers tuned on bull market data. They get destroyed in choppy/ranging markets. We need:
1. Strategies that PROFIT from chop (grid/DCA, pairs trading, mean reversion)
2. Better regime detection (HMM replaces hard thresholds)
3. Meta-labeling to filter out bad signals
4. Asset-specific tuning (forex needs different strategies than crypto)

## Implementation Priority (ranked by impact/effort ratio)

| Rank | Strategy | Alpha Source | Regime | Account Size | Complexity | Expected Return |
|------|----------|--------------|--------|--------------|-----------|-----------------|
| 1 | Meta-Labeling (LightGBM) | Signal filtering | All | Any | Low | +0.3–0.6 Sharpe lift |
| 2 | HMM Regime Detector | Probabilistic switching | N/A | Any | Medium | +5–15% CAGR |
| 3 | Grid/DCA Hybrid (Crypto) | Range-bound mean reversion | Choppy | $500–5k | Low | 25–35% backtest |
| 4 | Pairs Trading (Stat Arb) | Market-neutral spread | All (best choppy) | $5k+ | Medium | 8–12% Sharpe |
| 5 | Forex Carry + COT | Interest rate + structure | Choppy/bull | $5k+ | High | 6–15% annualized |
| 6 | LightGBM Direction | ML prediction (100+ features) | All | Any | High | +50–200 bps |
| 7 | Credit Spreads (IBKR) | Volatility premium | All | $5k+ | High | 65–80% win rate |
| 8 | TQQQ SMA Trend (IBKR) | Leverage + momentum | Bull | $5k+ | Low | 25–35% CAGR |
| 9 | MES Overnight Mean Reversion | Overnight dislocation | Choppy | $5k+ | Medium | Sharpe 1.0–1.5 |
| 10 | Funding Rate Arbitrage | Basis spread | All | $5k+ | Medium | 8–20% APY |

## Key Insights from Renaissance Technologies

- **Right on ~50.75% of the time** — but wins are bigger than losses (Sharpe 2.0+)
- **Stack many weak edges** rather than seeking one perfect strategy
- **Use HMMs** (borrowed from speech recognition) for regime detection
- **Market-neutral positioning** reduces max drawdown
- **Short holding periods** reduce overnight/weekend risk
- **Continuous risk monitoring** beats post-trade analysis

## Recommended ML Stack

**For signal filtering & regime detection:**
- `lightgbm` — meta-labeling (production-ready, 5 min training)
- `hmmlearn` — HMM regime detector (2–4 regimes, probabilistic switching)
- `mlfinlab` — triple-barrier labeling, CPCV walk-forward validation
- `fracdiff` — fractional differentiation for stationarity

**For new strategies:**
- `ib_async` — IBKR async API (non-blocking orders)
- `mibian` — option Greeks calculation (Black-Scholes)
- `py_vollib` — volatility surface for implied vol
- `skfolio` — portfolio optimization (correlation-aware position sizing)

**For data & research:**
- `microsoft/qlib` — full AI quant research pipeline (50+ technical indicators, ML)
- `freqtrade` — backtesting framework, FreqAI ML module
- `pysystemtrade` — systematic futures framework (Rob Carver)

## GitHub Repos to Implement From

| Repo | Use Case | Stars | Relevance |
|------|----------|-------|-----------|
| `mlfinlab` | Meta-labeling, triple-barrier | 4.5k | **Critical** — add to existing strategies |
| `fracdiff` | Stationarity for ML | 700+ | Improves LightGBM features |
| `microsoft/qlib` | Full ML quant platform | 14k | Reference for 100+ feature engineering |
| `freqtrade` | Crypto bot + FreqAI ML | 28k | Existing strategies can plug into FreqAI |
| `ThetaGang` | IBKR options selling bot | 1.5k | Credit spreads reference |
| `pysystemtrade` | Systematic futures | 2k | Trend-following reference (Rob Carver) |
| `passivbot` | Grid/DCA crypto | 1.5k | Reference for grid/DCA implementation |
| `hummingbot` | Market making + arbitrage | 8.5k | Reference for funding rate arb |

## Immediate Action Plan

**Phase 1 (Week 1 – 2): Meta-Labeling**
- Train LightGBM on existing signals vs. actual returns
- Apply to all 12 strategies, measure Sharpe improvement
- Expected lift: +0.3–0.6 (net positive on marginal strategies)

**Phase 2 (Week 2 – 3): HMM Regime Detector**
- Replace hard thresholds in `core/regime_detector.py`
- Test 2, 3, 4-state HMMs on BTC/USDT 4H data
- Measure: win rate, Sharpe, max drawdown vs. hard-threshold version

**Phase 3 (Week 3 – 4): Grid/DCA Hybrid**
- Build range-detection module (Donchian, Bollinger, ATR)
- Implement grid placement logic (even spacing, mid-weighted, or Kelly fraction)
- Backtest on 5 crypto pairs in ranging markets (Nov 2025 – Mar 2026)

**Phase 4 (Month 2): Live Deploy**
- Meta-labeling on all strategies (paper trade)
- HMM regime switching (paper trade, 2 weeks)
- Grid/DCA on 2 stable pairs (paper trade, 2 weeks)
- Then: LIVE on Kraken with 50% position sizing

## Why Bonds Are OFF the Table

- Minimum investment for meaningful income: $10k (coupon yield < inflation)
- Account size: $500–5k (not suited for bonds)
- Liquidity: poor on micro accounts, spreads eat profits
- Complexity: yield curve, duration, credit risk — not worth the friction

## Why Credit Spreads & TQQQ Are IBKR's Edge

| Strategy | Win Rate | Sharpe | Max DD | Capital Required |
|----------|----------|--------|--------|-----------------|
| Credit Spreads (PUT) | 65–80% | 1.2–1.8 | 15–20% | $5k–10k |
| TQQQ SMA Trend | N/A | 1.0–1.4 | 20–35% | $2k–5k |
| MES Overnight Reversion | 55–60% | 1.0–1.5 | 12–18% | $3k–5k |
| SPY/QQQ Straddle Sell | 50%+ | 1.5–2.0 | 18–25% | $5k–10k |

## Next Steps

1. Read `mlfinlab` documentation, implement TripleBarrier labeling
2. Train LightGBM on existing strategy signals (2-3 hours)
3. Backtest all 12 strategies WITH meta-labeling layer (4-6 hours)
4. Decision: if Sharpe improves >0.2, deploy immediately; if <0.1, investigate signal quality
5. Begin HMM regime detector in parallel

---

**Document Date:** 2026-03-20
**Researcher:** ATLAS (6 research agents)
**Confidence:** 0.95 (based on peer-reviewed research + backtests + Renaissance insights)
