import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
import ccxt, pandas as pd, numpy as np
from collections import defaultdict

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
        print(f'  OK {sym}: {len(df)} candles')
    except Exception as e:
        print(f'  SKIP {sym}: {e}')

strategies = [
    ('Donchian', DonchianBreakoutStrategy()),
    ('RSI_MR', RSIMeanReversionStrategy()),
    ('SmartMoney', SmartMoneyStrategy()),
]

print('=' * 100)
print('  ATLAS WINNER PORTFOLIO — Top 3 strategies x 9 pairs (4H, ~120 days)')
print('=' * 100)
print()

all_trades = []
strategy_stats = {}

for name, strat in strategies:
    strat_pnl = 0
    strat_trades = 0
    strat_wins = 0
    strat_long_pnl = 0
    strat_short_pnl = 0

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(df, strat)

            for t in result.trades:
                strat_pnl += t.net_pnl
                strat_trades += 1
                if t.net_pnl > 0:
                    strat_wins += 1

                side = t.side.value if hasattr(t.side, 'value') else str(t.side)
                if side.upper() in ['LONG', 'BUY']:
                    strat_long_pnl += t.net_pnl
                else:
                    strat_short_pnl += t.net_pnl

                # Collect for portfolio analysis
                all_trades.append({
                    'strategy': name,
                    'symbol': sym,
                    'entry_time': t.entry_time if hasattr(t, 'entry_time') else None,
                    'exit_time': t.exit_time if hasattr(t, 'exit_time') else None,
                    'pnl': t.net_pnl,
                    'pnl_pct': t.pnl_pct,
                    'side': side,
                })
        except Exception as e:
            pass

    wr = strat_wins / strat_trades * 100 if strat_trades else 0
    strategy_stats[name] = {
        'trades': strat_trades, 'pnl': strat_pnl, 'wr': wr,
        'long_pnl': strat_long_pnl, 'short_pnl': strat_short_pnl, 'wins': strat_wins
    }

# Print per-strategy results
print(f"  {'Strategy':15s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s} {'Long $':>10s} {'Short $':>10s}")
print('-' * 65)
for name, s in strategy_stats.items():
    sign = '+' if s['pnl'] >= 0 else ''
    lsign = '+' if s['long_pnl'] >= 0 else ''
    ssign = '+' if s['short_pnl'] >= 0 else ''
    print(f"  {name:15s} {s['trades']:>7d} {sign}${s['pnl']:>8.0f} {s['wr']:>5.1f}% {lsign}${s['long_pnl']:>8.0f} {ssign}${s['short_pnl']:>8.0f}")

print()

# Portfolio totals
total_trades = sum(s['trades'] for s in strategy_stats.values())
total_pnl = sum(s['pnl'] for s in strategy_stats.values())
total_wins = sum(s['wins'] for s in strategy_stats.values())
total_wr = total_wins / total_trades * 100 if total_trades else 0
total_long = sum(s['long_pnl'] for s in strategy_stats.values())
total_short = sum(s['short_pnl'] for s in strategy_stats.values())

print(f"  {'PORTFOLIO':15s} {total_trades:>7d} +${total_pnl:>8.0f} {total_wr:>5.1f}% +${total_long:>8.0f} +${total_short:>8.0f}")
print()

# Portfolio metrics
all_pnl_pcts = [t['pnl_pct'] for t in all_trades]
if all_pnl_pcts:
    sharpe = np.mean(all_pnl_pcts) / np.std(all_pnl_pcts) if np.std(all_pnl_pcts) > 0 else 0

    # Simulate equity curve (starting with $10,000 per strategy = $30,000 total)
    initial = 30000
    equity = initial
    peak = initial
    max_dd = 0
    equity_curve = [initial]

    # Sort trades by exit time
    sorted_trades = sorted([t for t in all_trades if t['exit_time'] is not None],
                          key=lambda x: x['exit_time'])

    for t in sorted_trades:
        equity += t['pnl']
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd:
            max_dd = dd
        equity_curve.append(equity)

    total_return = (equity - initial) / initial * 100

    print('  PORTFOLIO METRICS:')
    print(f'    Starting Capital:  ${initial:,.0f} ($10K per strategy)')
    print(f'    Final Equity:      ${equity:,.0f}')
    print(f'    Total Return:      +{total_return:.1f}%')
    print(f'    Total Trades:      {total_trades}')
    print(f'    Win Rate:          {total_wr:.1f}%')
    print(f'    Sharpe Ratio:      {sharpe:.2f}')
    print(f'    Max Drawdown:      {max_dd:.1f}%')
    print(f'    Avg PnL/Trade:     {np.mean(all_pnl_pcts):+.2f}%')
    print(f'    Best Trade:        {max(all_pnl_pcts):+.2f}%')
    print(f'    Worst Trade:       {min(all_pnl_pcts):+.2f}%')
    print()

    # Strategy overlap analysis
    print('  STRATEGY OVERLAP:')
    for name in strategy_stats:
        strat_trades = [t for t in all_trades if t['strategy'] == name]
        months = set()
        for t in strat_trades:
            if t['exit_time'] is not None:
                if hasattr(t['exit_time'], 'strftime'):
                    months.add(t['exit_time'].strftime('%Y-%m'))
                else:
                    months.add(str(t['exit_time'])[:7])
        print(f'    {name:15s}: active in {len(months)} months, {len(strat_trades)} trades')

print()
print('=' * 100)
