---
tags: [capabilities, tools]
---

# ATLAS — Capability Registry

> Master index of everything Atlas can do. Updated when new modules ship.

## Capability Counts (2026-03-26)

- **Trading Strategies:** 12+ (RSI MR, Donchian, EMA crossover, Bollinger squeeze, VWAP, multi-TF momentum, London breakout, opening range, smart money, Ichimoku, order flow, Z-score, volume profile, RSI divergence, TSMOM, gold pullback)
- **AI Agents:** 10 (4 analysts + debate + risk + portfolio + Darwinian evolution + financial advisor + budget)
- **Finance Modules:** 4 (tax calculator, financial advisor, wealth tracker, budget)
- **Brokers:** 3 (Kraken/CCXT, OANDA, Alpaca — not configured)
- **Skills:** 3 (accounting-advisor, tax-optimization, financial-planning)

## Trading Engine

| Module | Location | Purpose |
|--------|----------|---------|
| **Engine** | `core/engine.py` | Main trading loop — 60s ticks, regime-aware |
| **Risk Manager** | `core/risk_manager.py` | Kill switches — 15% DD, 5% daily, 1.5% per-trade |
| **Regime Detector** | `core/regime_detector.py` | BULL/BEAR/CHOPPY/HIGH_VOL classification |
| **Trailing Stops** | `core/trailing_stop.py` | Chandelier, SAR, ATR-trail, composite |
| **Order Executor** | `core/order_executor.py` | Limit orders, 30s timeout |
| **Broker Registry** | `core/broker_registry.py` | Multi-broker routing (Kraken, OANDA, Alpaca) |
| **Correlation Tracker** | `core/correlation_tracker.py` | Rolling 30-day correlation matrix |

## Finance & Accounting

| Module | Location | Purpose |
|--------|----------|---------|
| **CryptoTaxCalculator** | `finance/tax.py` | CRA-accurate capital gains, ACB tracking, T5008/Schedule 3 |
| **FinancialAdvisor** | `finance/advisor.py` | Portfolio analysis, allocation, monthly reviews, emergency plans |
| **WealthTracker** | `finance/wealth_tracker.py` | Net worth snapshots, FIRE calculator, projections |
| **Budget** | `finance/budget.py` | Expense tracking, category breakdown, savings analysis |

## Strategy Documents

| Document | Location | Purpose |
|----------|----------|---------|
| **Trading Algorithm** | `docs/ATLAS_ALGORITHM.md` | THE trading algorithm — every parameter validated |
| **Tax Strategy** | `docs/ATLAS_TAX_STRATEGY.md` | Canadian tax optimization playbook (Ontario) |
| **Strategy Research** | `docs/STRATEGY_RESEARCH.md` | Deep research — top repos, ML, profitable strategies |
| **IBKR Research** | `docs/IBKR_STRATEGY_RESEARCH.md` | Options, bonds, futures strategies |
| **Commodity/Forex Research** | `docs/COMMODITY_FOREX_STRATEGY_RESEARCH.md` | Top 10 commodity/forex by Sharpe |

## Broker Connections

| Broker | Module | Markets | Status |
|--------|--------|---------|--------|
| **Kraken** | CCXT (async) | Crypto (BTC, ETH, SOL, XRP, etc.) | LIVE |
| **OANDA** | oandapyV20 + BrokerAdapter | Forex, Gold, Silver | LIVE |
| **Alpaca** | alpaca-py | US Equities | NOT CONFIGURED |

## Integrations

| Integration | Purpose | Status |
|-------------|---------|--------|
| **Telegram Bot** | 12 commands — balance, positions, alerts | OPERATIONAL |
| **CRA Tax Engine** | Capital gains, ACB, quarterly estimates, deductions | CODE COMPLETE |
| **Anthropic Claude** | AI agents, financial advisor, budget analysis | ACTIVE |

## Skills (Domain Knowledge)

| Skill | Location | Triggers |
|-------|----------|----------|
| **Accounting Advisor** | `skills/accounting-advisor/SKILL.md` | tax, accounting, CRA, T2125, deduction |
| **Tax Optimization** | `skills/tax-optimization/SKILL.md` | TFSA, RRSP, FHSA, tax-loss harvest, crypto tax |
| **Financial Planning** | `skills/financial-planning/SKILL.md` | budget, FIRE, net worth, savings, allocation |
