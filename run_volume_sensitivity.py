"""
Volume Gate Sensitivity Analysis
================================
Tests what happens if we LOWER the volume requirement.
Current: 1.2x average volume required
Testing: 0.5x, 0.8x, 1.0x, 1.2x (current), 1.5x

Question: Can we safely trade with less volume confirmation?
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})

# Top 6 performers
symbols = ['ATOM/USDT', 'SHIB/USDT', 'DOT/USDT', 'BTC/USDT', 'ETH/USDT', 'DOGE/USDT']
volume_thresholds = [0.0, 0.5, 0.8, 1.0, 1.2, 1.5]

# Fetch data
data = {}
for sym in symbols:
    ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=721)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    data[sym] = df

print('=' * 90)
print('  VOLUME GATE SENSITIVITY — Should we lower the volume requirement?')
print('=' * 90)
print()
print(f"  {'Vol Mult':>8s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s} {'Avg PnL':>8s} {'Sharpe':>7s} {'Worst':>8s} {'Verdict':>12s}")
print('-' * 75)

for vm in volume_thresholds:
    total_pnl = 0
    total_trades = 0
    total_wins = 0
    all_pnls = []

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            strat = DonchianBreakoutStrategy(volume_mult=vm)
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
    avg_pnl = np.mean(all_pnls) if all_pnls else 0
    worst = min(all_pnls) if all_pnls else 0
    sharpe = np.mean(all_pnls) / np.std(all_pnls) if all_pnls and np.std(all_pnls) > 0 else 0

    current = ' <-- CURRENT' if vm == 1.2 else ''
    if total_pnl > 0 and wr > 40:
        verdict = 'PROFITABLE'
    elif total_pnl > 0:
        verdict = 'MARGINAL'
    else:
        verdict = 'UNPROFITABLE'

    sign = '+' if total_pnl >= 0 else ''
    print(f"  {vm:>8.1f} {total_trades:>7d} {sign}${total_pnl:>8.0f} {wr:>5.1f}% {avg_pnl:>+7.2f}% {sharpe:>6.2f} {worst:>+7.2f}% {verdict:>12s}{current}")

print()
print('  INTERPRETATION:')
print('    If lowering volume mult keeps profitability → safe to lower (more trades in bear markets)')
print('    If profitability drops sharply → volume gate is protecting us from bad trades')
print()
print('=' * 90)
