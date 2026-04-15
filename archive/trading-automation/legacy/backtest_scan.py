import asyncio
import sys
sys.path.insert(0, '.')

from backtesting.engine import BacktestEngine
from strategies.registry import get_all_strategies
import yaml
import ccxt

# Load strategy config
with open('config/strategies.yaml') as f:
    config = yaml.safe_load(f)

strategies_config = config.get('strategies', {})

# Get all strategy classes
all_strats = get_all_strategies()

exchange = ccxt.kraken()

results = []

for strat_name, strat_cfg in strategies_config.items():
    if not strat_cfg.get('enabled', False):
        continue

    symbols = strat_cfg.get('symbols', [])
    timeframe = strat_cfg.get('timeframe', '1h')
    strat_class = all_strats.get(strat_name)

    if not strat_class:
        continue

    for symbol in symbols:
        # Skip OANDA symbols for now (underscore format)
        if '_' in symbol:
            continue

        try:
            # Fetch 500 bars
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)
            if len(ohlcv) < 100:
                continue

            import pandas as pd
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df.attrs['symbol'] = symbol

            # Backtest
            params = strat_cfg.get('parameters', {})
            strat_instance = strat_class(**{k: v for k, v in params.items() if k in strat_class.__init__.__code__.co_varnames})

            engine = BacktestEngine(
                strategy=strat_instance,
                initial_capital=100,
                commission_pct=0.0026,
                risk_per_trade_pct=0.08,
            )
            result = engine.run(df)

            results.append({
                'strategy': strat_name,
                'symbol': symbol,
                'timeframe': timeframe,
                'return_pct': result.total_return,
                'sharpe': getattr(result, 'sharpe_ratio', 0),
                'trades': result.total_trades,
                'win_rate': result.win_rate * 100 if result.win_rate else 0,
                'max_dd': getattr(result, 'max_drawdown_pct', 0),
                'profit_factor': getattr(result, 'profit_factor', 0),
            })
            print(f'{strat_name:25s} {symbol:12s} {timeframe:4s} ret={result.total_return:+6.2f}% trades={result.total_trades:3d} WR={result.win_rate*100 if result.win_rate else 0:5.1f}% sharpe={getattr(result, "sharpe_ratio", 0):5.2f}')
        except Exception as e:
            print(f'{strat_name:25s} {symbol:12s} ERROR: {str(e)[:80]}')

print('\n=== TOP PERFORMERS (by return) ===')
results.sort(key=lambda x: x['return_pct'], reverse=True)
for r in results[:10]:
    print(f"{r['strategy']:25s} {r['symbol']:12s} ret={r['return_pct']:+6.2f}% sharpe={r['sharpe']:5.2f} trades={r['trades']:3d} WR={r['win_rate']:5.1f}%")

print('\n=== WORST PERFORMERS ===')
for r in results[-5:]:
    print(f"{r['strategy']:25s} {r['symbol']:12s} ret={r['return_pct']:+6.2f}% sharpe={r['sharpe']:5.2f} trades={r['trades']:3d}")

print('\n=== BY STRATEGY (avg return) ===')
from collections import defaultdict
strat_returns = defaultdict(list)
for r in results:
    strat_returns[r['strategy']].append(r['return_pct'])
for strat, rets in sorted(strat_returns.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
    avg = sum(rets)/len(rets)
    print(f'{strat:25s} avg={avg:+6.2f}% across {len(rets)} pairs')
