"""
Walk-Forward V2 — Rolling out-of-sample validation for donchian_breakout.
Tests the core strategy that generates 92% of our trades.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})

TRAIN_SIZE = 500
TEST_SIZE = 200
STEP_SIZE = 150

print('=' * 80)
print('  WALK-FORWARD V2 — DONCHIAN BREAKOUT OUT-OF-SAMPLE VALIDATION')
print(f'  Train: {TRAIN_SIZE} bars | Test: {TEST_SIZE} bars | Step: {STEP_SIZE} bars')
print('=' * 80)

symbols = ['ATOM/USDT', 'SHIB/USDT', 'ETH/USDT', 'DOT/USDT', 'AVAX/USDT', 'ADA/USDT', 'BTC/USDT', 'DOGE/USDT']
all_results = []

for sym in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=1500)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        print(f'\n  {sym} ({len(df)} candles)')

        windows = []
        start = 0
        while start + TRAIN_SIZE + TEST_SIZE <= len(df):
            test_df = df.iloc[start:start + TRAIN_SIZE + TEST_SIZE].copy()
            test_start_time = df.index[start + TRAIN_SIZE]

            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(test_df, DonchianBreakoutStrategy())

            # Only count trades entering in the test window
            test_trades = [t for t in result.trades if pd.Timestamp(t.entry_time) >= test_start_time]

            if test_trades:
                net = sum(t.net_pnl for t in test_trades)
                wins = sum(1 for t in test_trades if t.net_pnl > 0)
                wr = wins / len(test_trades) * 100
            else:
                net, wr = 0, 0

            sign = '+' if net >= 0 else ''
            print(f"    W{len(windows)+1}: {test_start_time.strftime('%Y-%m-%d')} | "
                  f"{len(test_trades)} trades | {sign}${net:.0f} | WR: {wr:.0f}%")

            windows.append({'trades': len(test_trades), 'net': net, 'wr': wr})
            start += STEP_SIZE

        if windows:
            total_pnl = sum(w['net'] for w in windows)
            total_trades = sum(w['trades'] for w in windows)
            profitable = sum(1 for w in windows if w['net'] > 0)
            consistency = profitable / len(windows) * 100

            verdict = 'ROBUST' if consistency >= 60 and total_pnl > 0 else 'MARGINAL' if total_pnl > 0 else 'WEAK'
            sign = '+' if total_pnl >= 0 else ''
            print(f"    => {sign}${total_pnl:.0f} | {total_trades} trades | "
                  f"{profitable}/{len(windows)} profitable windows ({consistency:.0f}%) | {verdict}")

            all_results.append({
                'symbol': sym, 'trades': total_trades, 'pnl': total_pnl,
                'consistency': consistency, 'verdict': verdict, 'windows': len(windows),
            })
    except Exception as e:
        print(f"  {sym}: ERROR - {e}")

print('\n' + '=' * 80)
print('  WALK-FORWARD SUMMARY')
print('=' * 80)

print(f"\n  {'Symbol':12s} {'Windows':>7s} {'OOS Trades':>10s} {'OOS P&L':>10s} {'Consistency':>12s} {'Verdict':>8s}")
print('  ' + '-' * 62)

for r in sorted(all_results, key=lambda x: -x['pnl']):
    sign = '+' if r['pnl'] >= 0 else ''
    print(f"  {r['symbol']:12s} {r['windows']:>7d} {r['trades']:>10d} {sign}${r['pnl']:>8.0f} {r['consistency']:>10.0f}% {r['verdict']:>8s}")

robust = sum(1 for r in all_results if r['verdict'] == 'ROBUST')
marginal = sum(1 for r in all_results if r['verdict'] == 'MARGINAL')
weak = sum(1 for r in all_results if r['verdict'] == 'WEAK')
total_oos = sum(r['pnl'] for r in all_results)

print(f"\n  ROBUST: {robust} | MARGINAL: {marginal} | WEAK: {weak}")
print(f"  Total OOS P&L: +${total_oos:.0f}")
print(f"\n  {'EDGE CONFIRMED' if robust >= len(all_results) * 0.6 else 'NEEDS MORE VALIDATION'}")
