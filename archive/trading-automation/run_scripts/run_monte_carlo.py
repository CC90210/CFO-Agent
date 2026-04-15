"""
Monte Carlo Simulation — estimate expected returns and confidence intervals.
Randomly resamples trade P&L to simulate 1000 possible equity paths.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
import ccxt, pandas as pd, numpy as np

np.random.seed(42)

exchange = ccxt.kraken({'enableRateLimit': True})
SIMULATIONS = 1000
INITIAL_CAPITAL = 10000

print('=' * 80)
print('  MONTE CARLO SIMULATION — PORTFOLIO CONFIDENCE INTERVALS')
print(f'  {SIMULATIONS} simulations | ${INITIAL_CAPITAL:,} initial capital')
print('=' * 80)

# Collect all trades from the portfolio
all_pnl_pcts = []

configs = [
    ('donchian_breakout', DonchianBreakoutStrategy,
     ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'XRP/USDT',
      'AVAX/USDT', 'ATOM/USDT', 'DOGE/USDT', 'SHIB/USDT', 'MANA/USDT']),
    ('smart_money', SmartMoneyStrategy,
     ['ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'AVAX/USDT']),
]

for strat_name, StratClass, symbols in configs:
    for sym in symbols:
        try:
            ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=1500)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, regime_filter=True)
            result = engine.run(df, StratClass())

            for t in result.trades:
                all_pnl_pcts.append(t.pnl_pct)
        except:
            pass

print(f'\n  Collected {len(all_pnl_pcts)} historical trades for resampling')
print(f'  Avg trade P&L: {np.mean(all_pnl_pcts):+.2f}%')
print(f'  Median trade P&L: {np.median(all_pnl_pcts):+.2f}%')
print(f'  Std dev: {np.std(all_pnl_pcts):.2f}%')
print(f'  Win rate: {sum(1 for p in all_pnl_pcts if p > 0) / len(all_pnl_pcts) * 100:.1f}%')

# Simulate N equity paths, each with the same number of trades as historical
n_trades = len(all_pnl_pcts)
final_equities = []
max_drawdowns = []

for sim in range(SIMULATIONS):
    # Resample with replacement
    resampled = np.random.choice(all_pnl_pcts, size=n_trades, replace=True)

    # Build equity curve
    equity = INITIAL_CAPITAL
    peak = equity
    max_dd = 0

    for pnl_pct in resampled:
        equity *= (1 + pnl_pct / 100)
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak * 100
        if dd > max_dd:
            max_dd = dd

    final_equities.append(equity)
    max_drawdowns.append(max_dd)

final_equities = np.array(final_equities)
max_drawdowns = np.array(max_drawdowns)
returns = (final_equities - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

print(f'\n  --- MONTE CARLO RESULTS ({SIMULATIONS} simulations, {n_trades} trades each) ---')
print()

# Return distribution
percentiles = [5, 10, 25, 50, 75, 90, 95]
print(f'  RETURN DISTRIBUTION:')
for p in percentiles:
    val = np.percentile(returns, p)
    equity = INITIAL_CAPITAL * (1 + val / 100)
    print(f'    {p:>3d}th percentile: {val:>+7.1f}% (${equity:>10,.0f})')

print(f'\n    Mean return: {np.mean(returns):>+7.1f}%')
print(f'    Probability of profit: {(returns > 0).sum() / SIMULATIONS * 100:.1f}%')
print(f'    Probability of >50% return: {(returns > 50).sum() / SIMULATIONS * 100:.1f}%')
print(f'    Probability of >100% return: {(returns > 100).sum() / SIMULATIONS * 100:.1f}%')
print(f'    Probability of loss: {(returns < 0).sum() / SIMULATIONS * 100:.1f}%')

# Drawdown distribution
print(f'\n  MAX DRAWDOWN DISTRIBUTION:')
for p in [50, 75, 90, 95]:
    val = np.percentile(max_drawdowns, p)
    print(f'    {p:>3d}th percentile: {val:>5.1f}%')

print(f'\n    Median max drawdown: {np.median(max_drawdowns):.1f}%')
print(f'    Probability DD > 10%: {(max_drawdowns > 10).sum() / SIMULATIONS * 100:.1f}%')
print(f'    Probability DD > 15% (kill switch): {(max_drawdowns > 15).sum() / SIMULATIONS * 100:.1f}%')
print(f'    Probability DD > 20%: {(max_drawdowns > 20).sum() / SIMULATIONS * 100:.1f}%')

# Risk-adjusted metrics
sharpe_sims = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
print(f'\n  RISK-ADJUSTED METRICS:')
print(f'    Portfolio Sharpe (from MC): {sharpe_sims:.2f}')
print(f'    Expected return / Expected DD: {np.mean(returns) / np.median(max_drawdowns):.2f}')
print(f'    Kelly fraction estimate: {np.mean(all_pnl_pcts) / np.var(all_pnl_pcts) * 100:.1f}% of portfolio')

print('\n' + '=' * 80)
