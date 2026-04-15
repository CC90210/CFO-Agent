import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'XRP/USDT', 'ATOM/USDT', 'DOGE/USDT', 'SHIB/USDT']

# Import all strategies
strategies = []
try:
    from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
    strategies.append(('Donchian', DonchianBreakoutStrategy()))
except: pass
try:
    from strategies.technical.smart_money import SmartMoneyStrategy
    strategies.append(('SmartMoney', SmartMoneyStrategy()))
except: pass
try:
    from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
    strategies.append(('RSI_MR', RSIMeanReversionStrategy()))
except: pass
try:
    from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy
    strategies.append(('Bollinger', BollingerSqueezeStrategy()))
except: pass
try:
    from strategies.technical.multi_timeframe_momentum import MultiTimeframeStrategy
    strategies.append(('MultiTF', MultiTimeframeStrategy()))
except: pass
try:
    from strategies.technical.ema_crossover import EMACrossoverStrategy
    strategies.append(('EMA', EMACrossoverStrategy()))
except: pass
try:
    from strategies.technical.ichimoku_trend import IchimokuTrendStrategy
    strategies.append(('Ichimoku', IchimokuTrendStrategy()))
except: pass

# Fetch data
data = {}
for sym in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=721)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        data[sym] = df
    except Exception as e:
        print(f'  SKIP {sym}: {e}')

print('=' * 95)
print('  FULL PORTFOLIO WITH UPDATED REGIME WEIGHTS (regime_filter=True)')
print('=' * 95)
print()

# Run WITH regime filter (new weights)
print('  WITH updated regime filter:')
print(f"  {'Strategy':15s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s}")
print('-' * 45)

portfolio_pnl_filtered = 0
portfolio_trades_filtered = 0
portfolio_wins_filtered = 0

for name, strat in strategies:
    strat_pnl = 0
    strat_trades = 0
    strat_wins = 0

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(df, strat)
            for t in result.trades:
                strat_pnl += t.net_pnl
                strat_trades += 1
                if t.net_pnl > 0:
                    strat_wins += 1
        except: pass

    portfolio_pnl_filtered += strat_pnl
    portfolio_trades_filtered += strat_trades
    portfolio_wins_filtered += strat_wins

    wr = strat_wins / strat_trades * 100 if strat_trades else 0
    sign = '+' if strat_pnl >= 0 else ''
    print(f"  {name:15s} {strat_trades:>7d} {sign}${strat_pnl:>8.0f} {wr:>5.1f}%")

wr_f = portfolio_wins_filtered / portfolio_trades_filtered * 100 if portfolio_trades_filtered else 0
print(f"  {'TOTAL':15s} {portfolio_trades_filtered:>7d} +${portfolio_pnl_filtered:>8.0f} {wr_f:>5.1f}%")

print()

# Run WITHOUT regime filter
print('  WITHOUT regime filter (raw):')
print(f"  {'Strategy':15s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s}")
print('-' * 45)

portfolio_pnl_raw = 0
portfolio_trades_raw = 0
portfolio_wins_raw = 0

for name, strat in strategies:
    strat_pnl = 0
    strat_trades = 0
    strat_wins = 0

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=False)
            result = engine.run(df, strat)
            for t in result.trades:
                strat_pnl += t.net_pnl
                strat_trades += 1
                if t.net_pnl > 0:
                    strat_wins += 1
        except: pass

    portfolio_pnl_raw += strat_pnl
    portfolio_trades_raw += strat_trades
    portfolio_wins_raw += strat_wins

    wr = strat_wins / strat_trades * 100 if strat_trades else 0
    sign = '+' if strat_pnl >= 0 else ''
    print(f"  {name:15s} {strat_trades:>7d} {sign}${strat_pnl:>8.0f} {wr:>5.1f}%")

wr_r = portfolio_wins_raw / portfolio_trades_raw * 100 if portfolio_trades_raw else 0
print(f"  {'TOTAL':15s} {portfolio_trades_raw:>7d} +${portfolio_pnl_raw:>8.0f} {wr_r:>5.1f}%")

print()
print('  COMPARISON:')
improvement = portfolio_pnl_filtered - portfolio_pnl_raw
print(f'    Regime filter ON:  +${portfolio_pnl_filtered:,.0f} ({portfolio_trades_filtered} trades, {wr_f:.1f}% WR)')
print(f'    Regime filter OFF: +${portfolio_pnl_raw:,.0f} ({portfolio_trades_raw} trades, {wr_r:.1f}% WR)')
print(f'    Improvement:       ${improvement:+,.0f} from regime gating')
print()
print('=' * 95)
