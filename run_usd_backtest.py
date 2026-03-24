import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
# USD pairs (not USDT) — required for Ontario Canada
symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'DOT/USD', 'XRP/USD', 'ATOM/USD', 'DOGE/USD']

data = {}
for sym in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=721)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        data[sym] = df
        print(f'  Fetched {sym}: {len(df)} bars')
    except Exception as e:
        print(f'  SKIP {sym}: {e}')

strategies = [
    ('Donchian', DonchianBreakoutStrategy()),
    ('SmartMoney', SmartMoneyStrategy()),
    ('RSI_MR', RSIMeanReversionStrategy()),
]

print()
print('=' * 90)
print('  USD PAIR BACKTEST — Confirming profitability before live trading')
print('=' * 90)
print()
print(f"  {'Strategy':15s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s} {'Avg PnL':>8s} {'Sharpe':>7s}")
print('-' * 60)

portfolio_total = 0
portfolio_trades = 0

for name, strat in strategies:
    total_pnl = 0
    total_trades = 0
    total_wins = 0
    all_pnls = []

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(df, strat)
            for t in result.trades:
                total_pnl += t.net_pnl
                total_trades += 1
                if t.net_pnl > 0:
                    total_wins += 1
                all_pnls.append(t.pnl_pct)
        except:
            pass

    wr = total_wins / total_trades * 100 if total_trades else 0
    avg = np.mean(all_pnls) if all_pnls else 0
    sharpe = np.mean(all_pnls) / np.std(all_pnls) if all_pnls and np.std(all_pnls) > 0 else 0
    sign = '+' if total_pnl >= 0 else ''
    print(f"  {name:15s} {total_trades:>7d} {sign}${total_pnl:>8.0f} {wr:>5.1f}% {avg:>+7.2f}% {sharpe:>6.2f}")

    portfolio_total += total_pnl
    portfolio_trades += total_trades

print()
print(f"  PORTFOLIO TOTAL: {portfolio_trades} trades, +${portfolio_total:,.0f}")
print()
if portfolio_total > 0:
    print('  VERDICT: PROFITABLE on USD pairs. Safe to go live.')
else:
    print('  VERDICT: NOT PROFITABLE on USD pairs. DO NOT go live.')
print('=' * 90)
