"""
Comprehensive Portfolio Validation — All Strategies x All Symbols
================================================================
Runs the FULL portfolio backtest as the paper trader would see it,
then computes aggregate stats, strategy-level breakdown, and risk metrics.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy
from strategies.technical.multi_timeframe import MultiTimeframeStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
INITIAL_CAPITAL = 10000

# Full portfolio as configured in strategies.yaml
PORTFOLIO = {
    'donchian_breakout': {
        'class': DonchianBreakoutStrategy,
        'symbols': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT',
                     'XRP/USDT', 'AVAX/USDT', 'ATOM/USDT', 'DOGE/USDT', 'SHIB/USDT', 'MANA/USDT'],
    },
    'smart_money': {
        'class': SmartMoneyStrategy,
        'symbols': ['ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'AVAX/USDT'],
    },
    'rsi_mean_reversion': {
        'class': RSIMeanReversionStrategy,
        'symbols': ['BTC/USDT', 'ATOM/USDT', 'SOL/USDT'],
    },
    'bollinger_squeeze': {
        'class': BollingerSqueezeStrategy,
        'symbols': ['ATOM/USDT', 'BTC/USDT', 'ETH/USDT', 'DOGE/USDT'],
    },
    'multi_timeframe': {
        'class': MultiTimeframeStrategy,
        'symbols': ['DOGE/USDT', 'XRP/USDT'],
    },
}

print('=' * 90)
print('  ATLAS COMPREHENSIVE PORTFOLIO VALIDATION')
print(f'  {sum(len(v["symbols"]) for v in PORTFOLIO.values())} strategy-symbol pairs | 1500 candles (4h) | ${INITIAL_CAPITAL:,} per pair')
print('=' * 90)

# Fetch all unique symbols
all_symbols = set()
for cfg in PORTFOLIO.values():
    all_symbols.update(cfg['symbols'])

data_cache = {}
for sym in sorted(all_symbols):
    try:
        ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=1500)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        data_cache[sym] = df
        date_range = f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}"
        print(f'  Loaded {sym}: {len(df)} candles ({date_range})')
    except Exception as e:
        print(f'  FAILED {sym}: {e}')

print()

# Run all backtests
all_results = []
strategy_summaries = {}

for strat_name, cfg in PORTFOLIO.items():
    StratClass = cfg['class']
    strat_trades = []
    strat_pnl = 0
    strat_wins = 0
    strat_pairs_tested = 0

    for sym in cfg['symbols']:
        if sym not in data_cache:
            continue
        df = data_cache[sym]
        try:
            engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, regime_filter=True)
            result = engine.run(df, StratClass())
            trades = result.trades

            net = sum(t.net_pnl for t in trades)
            wins = sum(1 for t in trades if t.net_pnl > 0)
            wr = wins / len(trades) * 100 if trades else 0
            pnls = [t.pnl_pct for t in trades]
            sharpe = np.mean(pnls) / np.std(pnls) * np.sqrt(len(trades)) if pnls and np.std(pnls) > 0 else 0

            tag = 'OK' if net > 0 else 'LOSS'
            print(f'  {strat_name:25s} | {sym:12s} | {len(trades):3d} trades | '
                  f'{net:>+8.0f} | WR {wr:4.0f}% | Sharpe {sharpe:5.2f} | {tag}')

            for t in trades:
                strat_trades.append(t)
                all_results.append({
                    'strategy': strat_name,
                    'symbol': sym,
                    'pnl': t.net_pnl,
                    'pnl_pct': t.pnl_pct,
                    'direction': t.side.value if hasattr(t.side, 'value') else str(t.side),
                })

            strat_pnl += net
            strat_wins += wins
            strat_pairs_tested += 1
        except Exception as e:
            print(f'  {strat_name:25s} | {sym:12s} | ERROR: {e}')

    total_trades = len(strat_trades)
    wr = strat_wins / total_trades * 100 if total_trades else 0
    strategy_summaries[strat_name] = {
        'trades': total_trades,
        'pnl': strat_pnl,
        'wins': strat_wins,
        'wr': wr,
        'pairs': strat_pairs_tested,
    }

print()
print('=' * 90)
print('  STRATEGY-LEVEL SUMMARY')
print('=' * 90)
print(f"  {'Strategy':25s} {'Pairs':>5s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s}")
print('-' * 60)

total_portfolio_pnl = 0
total_portfolio_trades = 0
total_portfolio_wins = 0

for name, s in sorted(strategy_summaries.items(), key=lambda x: -x[1]['pnl']):
    sign = '+' if s['pnl'] >= 0 else ''
    print(f"  {name:25s} {s['pairs']:>5d} {s['trades']:>7d} {sign}${s['pnl']:>8.0f} {s['wr']:>5.1f}%")
    total_portfolio_pnl += s['pnl']
    total_portfolio_trades += s['trades']
    total_portfolio_wins += s['wins']

total_wr = total_portfolio_wins / total_portfolio_trades * 100 if total_portfolio_trades else 0

print('-' * 60)
print(f"  {'PORTFOLIO TOTAL':25s} {'':>5s} {total_portfolio_trades:>7d} "
      f"{'+'if total_portfolio_pnl>=0 else ''}${total_portfolio_pnl:>8.0f} {total_wr:>5.1f}%")

# Direction breakdown
if all_results:
    df_results = pd.DataFrame(all_results)
    longs = df_results[df_results['direction'] == 'LONG']
    shorts = df_results[df_results['direction'] == 'SHORT']

    print()
    print('  DIRECTION BREAKDOWN:')
    if len(longs):
        long_pnl = longs['pnl'].sum()
        print(f"    LONG:  {len(longs)} trades, {'+'if long_pnl>=0 else ''}${long_pnl:.0f}")
    if len(shorts):
        short_pnl = shorts['pnl'].sum()
        print(f"    SHORT: {len(shorts)} trades, {'+'if short_pnl>=0 else ''}${short_pnl:.0f}")

    # Risk metrics
    pnl_pcts = [r['pnl_pct'] for r in all_results]
    print()
    print('  RISK METRICS:')
    print(f"    Total trades: {len(pnl_pcts)}")
    print(f"    Avg trade P&L: {np.mean(pnl_pcts):+.2f}%")
    print(f"    Median trade P&L: {np.median(pnl_pcts):+.2f}%")
    print(f"    Std dev: {np.std(pnl_pcts):.2f}%")
    print(f"    Best trade: {max(pnl_pcts):+.2f}%")
    print(f"    Worst trade: {min(pnl_pcts):+.2f}%")

    # Simulate aggregate equity curve
    equity = INITIAL_CAPITAL
    peak = equity
    max_dd = 0
    equity_curve = [equity]
    for pnl_pct in pnl_pcts:
        equity *= (1 + pnl_pct / 100)
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd:
            max_dd = dd
        equity_curve.append(equity)

    total_return = (equity - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    print(f"    Max drawdown: {max_dd:.1f}%")
    print(f"    Total return: {total_return:+.1f}%")
    print(f"    Final equity: ${equity:,.0f}")

    # Kelly criterion
    win_pcts = [p for p in pnl_pcts if p > 0]
    loss_pcts = [abs(p) for p in pnl_pcts if p < 0]
    if win_pcts and loss_pcts:
        avg_win = np.mean(win_pcts)
        avg_loss = np.mean(loss_pcts)
        wr_decimal = len(win_pcts) / len(pnl_pcts)
        kelly = wr_decimal - (1 - wr_decimal) / (avg_win / avg_loss)
        print(f"    Kelly fraction: {kelly*100:.1f}% (half-Kelly: {kelly*50:.1f}%)")

    # Consecutive losses
    streak = 0
    max_streak = 0
    for p in pnl_pcts:
        if p < 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    print(f"    Max consecutive losses: {max_streak}")

print()
print('=' * 90)
print('  VALIDATION COMPLETE')
print('=' * 90)
