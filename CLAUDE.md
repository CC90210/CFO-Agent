# ATLAS TRADING AGENT — Claude Code Instructions

> You are working on Atlas Trading Agent — an autonomous multi-agent trading system.
> Owner: CC (Conaugh McKenna), OASIS AI Solutions

## Project Overview
- **Purpose:** Autonomous trading with AI-powered multi-agent analysis and Darwinian self-improvement
- **Stack:** Python 3.11+, CCXT (109 exchanges), Claude API (Anthropic), SQLAlchemy/SQLite, pandas, ta
- **Mode:** Paper trading by default. Live trading requires PAPER_TRADE=false AND CONFIRM_LIVE=true

## Quick Commands
```bash
# Run all tests
python -m pytest tests/ -v

# Backtest a strategy
python main.py backtest --strategy ema_crossover --symbol BTC/USDT --start 2024-01-01

# Paper trade (simulated money)
python main.py paper-trade --strategy all --exchange binance

# Multi-agent analysis of a symbol
python main.py analyze --symbol BTC/USDT

# Standalone paper trading dashboard (easier entry point)
python paper_trade.py

# Standalone analysis tool
python analyze.py BTC/USDT

# Live trading (DANGEROUS — requires explicit flags)
python main.py live --strategy momentum --exchange binance --confirm-live
```

## Architecture
- `strategies/` — 9 proven trading strategies with technical indicators
- `agents/` — 10 AI agents (4 analysts + debate + risk + portfolio + Darwinian evolution)
- `core/` — Engine, risk management (hardcoded kill switches), position sizing, order execution
- `backtesting/` — Backtest engine, walk-forward validation, Monte Carlo, benchmarking
- `data/` — Market data (CCXT), news (CryptoPanic, Yahoo, NewsAPI), economic calendar, watchlists
- `db/` — SQLAlchemy models for trades, signals, agent performance
- `utils/` — Logging, Telegram alerts, market hours

## Safety Rules (NON-NEGOTIABLE)
- Max drawdown: 15% — ALL trading halts
- Daily loss limit: 5% — stop for the day
- Per-trade risk: 1.5% max
- Min conviction: 0.3 — agents must be 30%+ confident
- NEVER override kill switches in core/risk_manager.py
- NEVER commit .env or any file with API keys
- ALWAYS backtest before paper trading, paper trade before live

## Configuration
- `.env` — API keys (Anthropic, exchange, Telegram). Never commit.
- `config/settings.py` — Pydantic-validated settings
- `config/strategies.yaml` — Strategy parameters

## Key Files
- `main.py` — CLI entry point
- `paper_trade.py` — Standalone paper trading dashboard (60-second refresh)
- `analyze.py` — Standalone multi-agent analysis tool (no trades executed)
- `core/engine.py` — Main trading loop
- `core/risk_manager.py` — Kill switches (hardcoded floors)
- `agents/orchestrator.py` — Runs all agents in parallel
- `agents/darwinian.py` — Self-improvement engine
- `backtesting/engine.py` — Backtest runner

## Development Rules
- All strategies extend `strategies.base.BaseStrategy`
- All agents extend `agents.base_agent.BaseAnalystAgent`
- Conviction scores: -1.0 (max bearish) to 1.0 (max bullish)
- Risk scores: 0 (safe) to 10 (max risk). Veto if > 7.
- Always run tests after changes: `python -m pytest tests/ -v`
- Commit format: `atlas: type — description`
