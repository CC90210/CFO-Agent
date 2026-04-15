import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'XRP/USDT', 'ATOM/USDT', 'DOGE/USDT', 'SHIB/USDT']

# Fetch data
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

print()
print('=' * 95)
print('  VOLUME GATE COMPARISON: 1.2x (old) vs 0.8x (new) vs 0.5x (aggressive)')
print('=' * 95)
print()
print(f"  {'Symbol':12s} {'VM':>4s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s} {'Avg PnL':>8s} {'Sharpe':>7s}")
print('-' * 65)

for vm_label, vm in [('1.2x', 1.2), ('0.8x', 0.8), ('0.5x', 0.5)]:
    total_pnl = 0
    total_trades = 0
    total_wins = 0
    all_pnls = []

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            strat = DonchianBreakoutStrategy(volume_mult=vm)
            result = engine.run(df, strat)

            sym_pnl = 0
            sym_trades = 0
            sym_wins = 0

            for t in result.trades:
                sym_pnl += t.net_pnl
                sym_trades += 1
                if t.net_pnl > 0:
                    sym_wins += 1
                all_pnls.append(t.pnl_pct)

            total_pnl += sym_pnl
            total_trades += sym_trades
            total_wins += sym_wins

            if sym_trades > 0:
                wr = sym_wins / sym_trades * 100
                sign = '+' if sym_pnl >= 0 else ''
                print(f"  {sym:12s} {vm_label:>4s} {sym_trades:>7d} {sign}${sym_pnl:>8.0f} {wr:>5.1f}%")
        except Exception as e:
            pass

    wr = total_wins / total_trades * 100 if total_trades else 0
    avg = np.mean(all_pnls) if all_pnls else 0
    sharpe = np.mean(all_pnls) / np.std(all_pnls) if all_pnls and np.std(all_pnls) > 0 else 0
    sign = '+' if total_pnl >= 0 else ''
    print(f"  {'TOTAL':12s} {vm_label:>4s} {total_trades:>7d} {sign}${total_pnl:>8.0f} {wr:>5.1f}% {avg:>+7.2f}% {sharpe:>6.2f}")
    print()
