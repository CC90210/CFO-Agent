"""Donchian Breakout parameter sensitivity analysis."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
import ccxt, pandas as pd, numpy as np
from itertools import product

exchange = ccxt.kraken({'enableRateLimit': True})

# Fetch data once for top performers
data = {}
for sym in ['ATOM/USDT', 'SHIB/USDT', 'DOT/USDT', 'ETH/USDT', 'AVAX/USDT', 'BTC/USDT']:
    ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=1500)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    data[sym] = df
    print(f'Loaded {sym}: {len(df)} candles')

print()
print('=' * 90)
print('  DONCHIAN PARAMETER SENSITIVITY ANALYSIS')
print('  Testing: entry_period x atr_stop_mult x rr_ratio')
print('=' * 90)

# Parameter grid
entry_periods = [15, 20, 25, 30]
atr_mults = [1.5, 2.0, 2.5, 3.0]
rr_ratios = [2.0, 3.0, 4.0, 5.0]

results = []
total_combos = len(entry_periods) * len(atr_mults) * len(rr_ratios)
combo_num = 0

for ep, am, rr in product(entry_periods, atr_mults, rr_ratios):
    combo_num += 1
    if combo_num % 16 == 0:
        print(f'  Progress: {combo_num}/{total_combos} combinations tested...')

    portfolio_pnl = 0
    portfolio_trades = 0
    portfolio_wins = 0
    sharpes = []

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            strat = DonchianBreakoutStrategy(
                entry_period=ep,
                exit_period=max(10, ep // 2),
                atr_stop_mult=am,
                rr_ratio=rr,
            )
            result = engine.run(df, strat)
            trades = result.trades

            if trades:
                net = sum(t.net_pnl for t in trades)
                wins = sum(1 for t in trades if t.net_pnl > 0)
                pnls = [t.pnl_pct for t in trades]
                sharpe = np.mean(pnls) / np.std(pnls) * np.sqrt(len(trades)) if np.std(pnls) > 0 else 0

                portfolio_pnl += net
                portfolio_trades += len(trades)
                portfolio_wins += wins
                sharpes.append(sharpe)
        except Exception:
            pass

    wr = portfolio_wins / portfolio_trades * 100 if portfolio_trades else 0
    avg_sharpe = np.mean(sharpes) if sharpes else 0

    results.append({
        'entry': ep, 'atr': am, 'rr': rr,
        'pnl': portfolio_pnl, 'trades': portfolio_trades,
        'wr': wr, 'sharpe': avg_sharpe,
    })

# Sort by P&L
results.sort(key=lambda x: -x['pnl'])

print()
header = f"{'Rank':>4s} {'Entry':>5s} {'ATR':>5s} {'RR':>5s} {'Trades':>6s} {'Net PnL':>10s} {'WR':>6s} {'Sharpe':>7s}"
print(header)
print('-' * len(header))

for i, r in enumerate(results[:20]):
    sign = '+' if r['pnl'] >= 0 else ''
    tag = ' <-- CURRENT' if r['entry'] == 20 and r['atr'] == 2.0 and r['rr'] == 3.0 else ''
    print(f"{i+1:>4d} {r['entry']:>5d} {r['atr']:>5.1f} {r['rr']:>5.1f} {r['trades']:>6d} {sign}${r['pnl']:>8.0f} {r['wr']:>5.1f}% {r['sharpe']:>6.2f}{tag}")

print()

# Show worst 5
print('WORST 5 COMBINATIONS:')
for r in results[-5:]:
    sign = '+' if r['pnl'] >= 0 else ''
    print(f"  entry={r['entry']} atr={r['atr']} rr={r['rr']} -> {sign}${r['pnl']:.0f} ({r['trades']} trades, WR={r['wr']:.0f}%)")

# Find optimal and compare to current
best = results[0]
current = [r for r in results if r['entry'] == 20 and r['atr'] == 2.0 and r['rr'] == 3.0]
current = current[0] if current else results[0]
current_rank = results.index(current) + 1

print()
print(f"OPTIMAL: entry={best['entry']}, ATR_stop={best['atr']}, RR={best['rr']}")
print(f"  Net P&L: +${best['pnl']:.0f} | {best['trades']} trades | WR: {best['wr']:.1f}% | Sharpe: {best['sharpe']:.2f}")
print(f"CURRENT (rank #{current_rank}): entry=20, ATR=2.0, RR=3.0")
print(f"  Net P&L: +${current['pnl']:.0f} | {current['trades']} trades | WR: {current['wr']:.1f}% | Sharpe: {current['sharpe']:.2f}")
improvement = best['pnl'] - current['pnl']
pct_improvement = (best['pnl'] / current['pnl'] - 1) * 100 if current['pnl'] > 0 else 0
print(f"  IMPROVEMENT AVAILABLE: +${improvement:.0f} ({pct_improvement:.1f}% better)")

# Robustness check: are the top params clustered or scattered?
print()
print('ROBUSTNESS CHECK — top 5 parameter sets:')
for r in results[:5]:
    print(f"  entry={r['entry']} atr={r['atr']} rr={r['rr']} -> +${r['pnl']:.0f}")
top_entries = [r['entry'] for r in results[:5]]
top_atrs = [r['atr'] for r in results[:5]]
top_rrs = [r['rr'] for r in results[:5]]
print(f"  Entry range: {min(top_entries)}-{max(top_entries)} | ATR range: {min(top_atrs)}-{max(top_atrs)} | RR range: {min(top_rrs)}-{max(top_rrs)}")
if max(top_entries) - min(top_entries) <= 10:
    print("  -> Entry period STABLE (narrow cluster = robust)")
else:
    print("  -> Entry period UNSTABLE (wide range = fragile)")
