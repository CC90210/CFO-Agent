import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'DOT/USDT', 'XRP/USDT', 'ATOM/USDT', 'DOGE/USDT', 'SHIB/USDT']

# Try importing other strategies
try:
    from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
    has_rsi = True
except Exception as e:
    print(f"RSI import error: {e}")
    has_rsi = False

try:
    from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy
    has_boll = True
except Exception as e:
    print(f"Bollinger import error: {e}")
    has_boll = False

try:
    from strategies.technical.equity_mean_reversion import EquityMeanReversionStrategy
    has_emr = True
except Exception as e:
    print(f"Equity MR import error: {e}")
    has_emr = False

try:
    from strategies.technical.zscore_mean_reversion import ZScoreMeanReversionStrategy
    has_zscore = True
except Exception as e:
    print(f"Z-Score import error: {e}")
    has_zscore = False

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

strategies = []
strategies.append(('Donchian', DonchianBreakoutStrategy()))
strategies.append(('SmartMoney', SmartMoneyStrategy()))
if has_rsi:
    strategies.append(('RSI_MeanRev', RSIMeanReversionStrategy()))
if has_boll:
    strategies.append(('Boll_Squeeze', BollingerSqueezeStrategy()))
if has_zscore:
    strategies.append(('ZScore_MR', ZScoreMeanReversionStrategy()))
if has_emr:
    strategies.append(('Equity_MR', EquityMeanReversionStrategy()))

print()
print('=' * 100)
print('  BEAR MARKET STRATEGY SHOWDOWN — Which strategies profit when crypto bleeds?')
print('=' * 100)
print()
print(f"  {'Strategy':15s} {'Trades':>7s} {'Net PnL':>10s} {'WR':>6s} {'Avg PnL':>8s} {'Sharpe':>7s} {'Longs $':>10s} {'Shorts $':>10s}")
print('-' * 85)

for name, strat in strategies:
    total_pnl = 0
    total_trades = 0
    total_wins = 0
    all_pnls = []
    long_pnl = 0
    short_pnl = 0

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(df, strat)

            for t in result.trades:
                total_pnl += t.net_pnl
                total_trades += 1
                if t.net_pnl > 0:
                    total_wins += 1
                all_pnls.append(t.pnl_pct)

                side = t.side.value if hasattr(t.side, 'value') else str(t.side)
                if side.upper() in ['LONG', 'BUY']:
                    long_pnl += t.net_pnl
                else:
                    short_pnl += t.net_pnl
        except Exception as e:
            pass

    wr = total_wins / total_trades * 100 if total_trades else 0
    avg = np.mean(all_pnls) if all_pnls else 0
    sharpe = np.mean(all_pnls) / np.std(all_pnls) if all_pnls and np.std(all_pnls) > 0 else 0
    sign = '+' if total_pnl >= 0 else ''
    lsign = '+' if long_pnl >= 0 else ''
    ssign = '+' if short_pnl >= 0 else ''

    print(f"  {name:15s} {total_trades:>7d} {sign}${total_pnl:>8.0f} {wr:>5.1f}% {avg:>+7.2f}% {sharpe:>6.2f} {lsign}${long_pnl:>8.0f} {ssign}${short_pnl:>8.0f}")

print()
print('  KEY: Positive Shorts $ = making money on downside. This is what we want in bear markets.')
print('  Sharpe > 0.3 = good risk-adjusted. WR > 40% = reliable.')
print('=' * 100)
