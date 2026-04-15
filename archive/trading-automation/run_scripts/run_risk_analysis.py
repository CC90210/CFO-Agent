"""Risk & Drawdown Analysis — Darwinian health assessment."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})

print('=' * 100)
print('  RISK & DRAWDOWN ANALYSIS — DARWINIAN HEALTH CHECK')
print('=' * 100)

configs = [
    ('donchian_breakout', DonchianBreakoutStrategy,
     ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'XRP/USDT',
      'AVAX/USDT', 'ATOM/USDT', 'DOGE/USDT', 'SHIB/USDT', 'MANA/USDT']),
    ('smart_money', SmartMoneyStrategy,
     ['ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'AVAX/USDT']),
]

all_rows = []

for strat_name, StratClass, symbols in configs:
    for sym in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=1500)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(df, StratClass())
            trades = result.trades

            if not trades:
                continue

            # Equity curve
            equity = [10000]
            for t in trades:
                equity.append(equity[-1] + t.net_pnl)

            # Max drawdown
            peak = equity[0]
            max_dd = 0
            for e in equity:
                if e > peak:
                    peak = e
                dd = (peak - e) / peak * 100
                if dd > max_dd:
                    max_dd = dd

            # Consecutive losses
            max_consec = 0
            current = 0
            for t in trades:
                if t.net_pnl < 0:
                    current += 1
                    max_consec = max(max_consec, current)
                else:
                    current = 0

            # Trade stats
            worst_pct = min(t.pnl_pct for t in trades)
            best_pct = max(t.pnl_pct for t in trades)

            winners = [t.net_pnl for t in trades if t.net_pnl > 0]
            losers = [t.net_pnl for t in trades if t.net_pnl < 0]
            gross_wins = sum(winners)
            gross_losses = abs(sum(losers))
            pf = gross_wins / gross_losses if gross_losses > 0 else 999
            avg_win = np.mean(winners) if winners else 0
            avg_loss = np.mean(losers) if losers else 0

            net = sum(t.net_pnl for t in trades)
            wr = len(winners) / len(trades) * 100
            recovery = net / (max_dd * 100) if max_dd > 0 else 999

            # Avg trade duration
            durations = []
            for t in trades:
                try:
                    d = (pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time)).total_seconds() / 3600
                    durations.append(d)
                except:
                    pass
            avg_dur = np.mean(durations) if durations else 0

            all_rows.append({
                'strategy': strat_name, 'symbol': sym,
                'trades': len(trades), 'net': net, 'wr': wr,
                'max_dd': max_dd, 'max_consec': max_consec,
                'worst': worst_pct, 'best': best_pct,
                'pf': pf, 'avg_win': avg_win, 'avg_loss': avg_loss,
                'recovery': recovery, 'avg_dur_h': avg_dur,
            })
            print(f"  Processed {strat_name}/{sym}: {len(trades)} trades, +${net:.0f}")
        except Exception as e:
            print(f"  Error {strat_name}/{sym}: {e}")

print()
print(f"  {'Strategy':20s} {'Symbol':10s} {'#':>4s} {'Net':>9s} {'WR':>5s} {'MaxDD':>6s} {'Consec':>6s} {'Worst':>7s} {'Best':>7s} {'PF':>5s} {'Recov':>6s} {'AvgDur':>6s}")
print('  ' + '-' * 100)

for r in sorted(all_rows, key=lambda x: -x['net']):
    sign = '+' if r['net'] >= 0 else ''
    print(f"  {r['strategy']:20s} {r['symbol']:10s} {r['trades']:>4d} {sign}${r['net']:>7.0f} {r['wr']:>4.0f}% {r['max_dd']:>5.1f}% {r['max_consec']:>6d} {r['worst']:>+6.1f}% {r['best']:>+6.1f}% {r['pf']:>5.2f} {r['recovery']:>5.1f}x {r['avg_dur_h']:>5.0f}h")

# Risk flags
print()
print('RISK FLAGS:')
dangerous = [r for r in all_rows if r['max_dd'] > 15 or r['max_consec'] >= 6]
if dangerous:
    for r in dangerous:
        flags = []
        if r['max_dd'] > 15:
            flags.append(f"MaxDD {r['max_dd']:.1f}% > 15%")
        if r['max_consec'] >= 6:
            flags.append(f"{r['max_consec']} consecutive losses")
        print(f"  WARNING: {r['strategy']}/{r['symbol']} - {', '.join(flags)}")
else:
    print('  No pairs exceed risk thresholds.')

# Darwinian health simulation
print()
print('DARWINIAN HEALTH ASSESSMENT:')
print('  Auto-disable: 8 consec losses OR 10% DD OR <20% WR over 30 trades')
disabled_count = 0
for r in all_rows:
    issues = []
    if r['max_consec'] >= 8:
        issues.append(f"{r['max_consec']} consec losses")
    if r['max_dd'] >= 10:
        issues.append(f"DD {r['max_dd']:.1f}%")
    if r['trades'] >= 30 and r['wr'] < 20:
        issues.append(f"WR {r['wr']:.0f}%")
    if issues:
        disabled_count += 1
        print(f"  WOULD DISABLE: {r['strategy']}/{r['symbol']} - {'; '.join(issues)}")

healthy = len(all_rows) - disabled_count
print(f"\n  HEALTHY: {healthy}/{len(all_rows)} pairs pass all health checks")
print(f"  WOULD DISABLE: {disabled_count}/{len(all_rows)} pairs")

# Portfolio-level stats
total_net = sum(r['net'] for r in all_rows)
total_trades = sum(r['trades'] for r in all_rows)
worst_dd_pair = max(all_rows, key=lambda x: x['max_dd'])
worst_streak_pair = max(all_rows, key=lambda x: x['max_consec'])

print(f"\n  PORTFOLIO TOTALS:")
print(f"    Net P&L: +${total_net:.0f} on $10K ({total_net/100:.1f}%)")
print(f"    Total trades: {total_trades}")
print(f"    Worst drawdown: {worst_dd_pair['strategy']}/{worst_dd_pair['symbol']} at {worst_dd_pair['max_dd']:.1f}%")
print(f"    Worst losing streak: {worst_streak_pair['strategy']}/{worst_streak_pair['symbol']} at {worst_streak_pair['max_consec']} consecutive")
