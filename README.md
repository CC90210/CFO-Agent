# Atlas Trading Agent

Autonomous multi-agent trading system with Darwinian self-improvement, institutional-grade risk management, and 9 proven trading strategies.

## Architecture

```
Market Data (CCXT) --> 4 Analyst Agents (parallel) --> Bull/Bear Debate --> Risk Manager (veto) --> Portfolio Manager --> Order Execution
                           |                              |                      |
                    Technical Analyst              3-round debate          Hardcoded kill switches
                    Sentiment Analyst              Claude-moderated        15% max drawdown
                    Fundamentals Analyst           Weighted consensus      5% daily loss limit
                    News Analyst                                           1.5% per-trade risk
                           |
                    Darwinian Evolution (weekly)
                    - Weight agents by accuracy
                    - Rewrite worst performer's prompt
                    - Git-revert if no improvement
```

## Strategies

| Strategy | Type | Best Market | Timeframe |
|----------|------|-------------|-----------|
| EMA Crossover | Momentum | Trending | 1H-4H |
| RSI Mean Reversion | Mean Reversion | Range-bound | 15m-1H |
| Bollinger Squeeze | Breakout | Low volatility | 1H-4H |
| VWAP Bounce | Intraday | High volume | 5m-15m |
| Multi-Timeframe | Confluence | Any | 15m+4H+1D |
| London Breakout | Session | GBP/USD, EUR/USD, XAU | 15m |
| Opening Range | Session | SPY, QQQ | 5m |
| Ichimoku Trend | Trend Following | Strong trends | 4H-1D |
| Smart Money Concepts | Order Flow | Any | 15m-1H |

## Quick Start

```bash
# 1. Clone and install
cd C:\Users\User\APPS\trading-agent
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Backtest a strategy
python main.py backtest --strategy ema_crossover --symbol BTC/USDT --start 2024-01-01

# 4. Paper trade (no real money)
python main.py paper-trade --strategy all --exchange binance

# 5. Multi-agent analysis
python main.py analyze --symbol BTC/USDT

# 6. Live trading (requires explicit confirmation)
python main.py live --strategy momentum --exchange binance --confirm-live
```

## Safety Rails (Non-Negotiable)

These limits are **hardcoded at module level** and cannot be overridden by config or agents:

| Rule | Default | Description |
|------|---------|-------------|
| Max Drawdown | 15% | Portfolio drops 15% from peak = ALL trading halted |
| Daily Loss Limit | 5% | Day's P&L drops 5% = stop for the day |
| Per-Trade Risk | 1.5% | Maximum risk on any single trade |
| Max Open Positions | 5 | No more than 5 concurrent positions |
| Max Single Asset | 20% | No more than 20% of portfolio in one asset |
| Min Conviction | 0.3 | Agents must be 30%+ confident to trade |
| Volatility Halving | 2x ATR | High-vol regimes = position sizes halved |

## Multi-Agent Intelligence

The system runs 4 specialist agents in parallel via Claude API:

1. **Technical Analyst** - Computes 13 indicators, scores confluence, has pure quant fallback
2. **Sentiment Analyst** - CryptoPanic, NewsAPI, Fear & Greed Index, recency-weighted
3. **Fundamentals Analyst** - CoinGecko (crypto) or Yahoo Finance (stocks), value scoring
4. **News Analyst** - Real-time monitoring, impact classification (HIGH/MEDIUM/LOW)

**Decision Pipeline:**
- If all agents agree (>0.75 conviction) -> execute immediately
- If agents disagree -> 3-round Bull/Bear debate moderated by Claude
- Risk Agent has absolute veto power (fires before Claude)
- Portfolio Manager sizes position with Half-Kelly + conviction scaling

**Darwinian Evolution (weekly):**
- Accurate agents: weight * 1.05 (max 2.5)
- Inaccurate agents: weight * 0.95 (min 0.3)
- Worst performer: prompt rewritten by Claude
- If rewrite doesn't improve Sharpe -> revert to old prompt

## Backtesting

```bash
# Standard backtest
python main.py backtest --strategy rsi_mean_reversion --symbol ETH/USDT --start 2024-01-01

# Walk-forward validation (prevents overfitting)
# Built into the BacktestEngine with rolling train/test windows

# Monte Carlo simulation
# Run 1000 trade-order permutations to get probability of ruin
```

**Metrics:** Sharpe, Sortino, Calmar, max drawdown, win rate, profit factor, expectancy, alpha/beta vs benchmark.

## Project Structure

```
trading-agent/
├── main.py                          # CLI entry point
├── config/
│   ├── settings.py                  # Pydantic-validated settings
│   └── strategies.yaml              # Strategy parameters
├── core/
│   ├── engine.py                    # Main trading loop
│   ├── risk_manager.py              # Kill switches + risk validation
│   ├── position_sizer.py            # Half-Kelly sizing
│   └── order_executor.py            # Paper + live execution (CCXT)
├── strategies/
│   ├── base.py                      # BaseStrategy ABC + registry
│   └── technical/
│       ├── indicators.py            # 13 vectorized indicators
│       ├── ema_crossover.py         # Momentum
│       ├── rsi_mean_reversion.py    # Mean reversion
│       ├── bollinger_squeeze.py     # Breakout
│       ├── vwap_bounce.py           # Intraday
│       ├── multi_timeframe.py       # Confluence
│       ├── london_breakout.py       # Session (London)
│       ├── opening_range.py         # Session (US open)
│       ├── ichimoku_trend.py        # Trend following
│       └── smart_money.py           # Order flow / SMC
├── agents/
│   ├── base_agent.py                # Base with retry, caching, fallback
│   ├── technical_analyst.py         # Indicator-driven analysis
│   ├── sentiment_analyst.py         # News + social sentiment
│   ├── fundamentals_analyst.py      # Valuation analysis
│   ├── news_analyst.py              # Breaking news classification
│   ├── risk_agent.py                # Veto power + risk scoring
│   ├── debate.py                    # Bull/Bear 3-round debate
│   ├── portfolio_manager.py         # Position management
│   ├── darwinian.py                 # Self-improving evolution
│   └── orchestrator.py              # Parallel agent coordination
├── backtesting/
│   ├── engine.py                    # Bar-by-bar simulation
│   ├── walk_forward.py              # Overfitting prevention
│   ├── monte_carlo.py               # Probability of ruin
│   └── benchmark.py                 # Alpha/Beta vs buy-and-hold
├── data/
│   ├── fetcher.py                   # OHLCV via CCXT (109 exchanges)
│   └── news_fetcher.py              # CryptoPanic, NewsAPI, Reddit, F&G
├── db/
│   ├── models.py                    # Trade, Signal, AgentPerformance, etc.
│   └── database.py                  # SQLite + session management
├── utils/
│   ├── logger.py                    # Structured JSON logging
│   ├── alerts.py                    # Telegram notifications
│   └── market_hours.py              # Session awareness
└── tests/                           # 116 tests
    ├── conftest.py                  # Shared fixtures
    ├── test_indicators.py
    ├── test_risk_manager.py
    ├── test_position_sizer.py
    ├── test_backtest.py
    ├── test_strategies.py
    └── test_infrastructure.py
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
ANTHROPIC_API_KEY=       # Claude API for agent intelligence
EXCHANGE_API_KEY=        # Exchange API key (Binance, etc.)
EXCHANGE_SECRET=         # Exchange API secret
TELEGRAM_BOT_TOKEN=      # For trade alerts
TELEGRAM_CHAT_ID=        # Your Telegram chat ID
PAPER_TRADE=true         # MUST be false + CONFIRM_LIVE=true for live
```

## Roadmap

- [ ] Reinforcement learning integration (FinRL / PPO)
- [ ] On-chain DeFi strategies (Solana Agent Kit)
- [ ] Financial advisor mode (tax optimization, portfolio allocation)
- [ ] Web dashboard for monitoring
- [ ] Multi-exchange arbitrage
- [ ] Options strategies

## License

Private - Conaugh McKenna / OASIS AI Solutions
