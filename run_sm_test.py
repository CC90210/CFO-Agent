import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.smart_money import SmartMoneyStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOT/USDT', 'XRP/USDT', 'ATOM/USDT', 'DOGE/USDT']

print('=' * 80)
print('  SMART MONEY STRATEGY — Fresh Backtest (4H, 721 bars)')
print('=' * 80)
print()

total_pnl = 0
total_trades = 0
total_wins = 0

for sym in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=721)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        engine = BacktestEngine(initial_capital=10000, regime_filter=True)
        strat = SmartMoneyStrategy()
        result = engine.run(df, strat)

        sym_pnl = sum(t.net_pnl for t in result.trades)
        sym_trades = len(result.trades)
        sym_wins = sum(1 for t in result.trades if t.net_pnl > 0)
        wr = sym_wins / sym_trades * 100 if sym_trades else 0

        total_pnl += sym_pnl
        total_trades += sym_trades
        total_wins += sym_wins

        sign = '+' if sym_pnl >= 0 else ''
        print(f"  {sym:12s}: {sym_trades:3d} trades, {sign}${sym_pnl:>8.2f}, WR {wr:>5.1f}%")
    except Exception as e:
        print(f"  {sym:12s}: ERROR — {e}")

print()
wr = total_wins / total_trades * 100 if total_trades else 0
sign = '+' if total_pnl >= 0 else ''
print(f"  TOTAL: {total_trades} trades, {sign}${total_pnl:.2f}, WR {wr:.1f}%")
print('=' * 80)
