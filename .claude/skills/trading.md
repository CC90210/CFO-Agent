---
description: "Execute or monitor trading operations — paper trade, live trade, backtest strategies, check portfolio status."
---
# Atlas Trading Operations

## Paper Trading (safe)
```bash
python paper_trade.py --strategy ema_crossover --pair BTC/USDT --exchange kraken
```

## Live Trading (requires confirmation)
```bash
python live_trade.py --strategy <name> --pair <pair> --exchange <exchange>
```
**ALWAYS confirm with CC before live trading.**

## Backtest
```bash
python -m backtesting.run --strategy <name> --start 2025-01-01 --end 2026-01-01
```

## Portfolio Status
```bash
python dashboard.py status
```

## 12 Strategies Available
RSI mean reversion, EMA crossover, Bollinger squeeze, VWAP bounce, multi-timeframe momentum, London breakout, opening range, Ichimoku trend, smart money concepts, order flow imbalance, Z-score mean reversion, volume profile.

## Risk Limits (Hardcoded — never override)
- Max drawdown: 15%
- Max position: 5% of portfolio
- Max daily loss: 3%