import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from backtesting.engine import BacktestEngine
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'DOT/USDT', 'XRP/USDT', 'ATOM/USDT', 'DOGE/USDT']

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

# Try all available strategies
strategy_classes = []

try:
    from strategies.technical.multi_timeframe import MultiTimeframeStrategy
    strategy_classes.append(('MultiTF', MultiTimeframeStrategy()))
except Exception as e:
    print(f"MultiTF: {e}")

try:
    from strategies.technical.ichimoku_trend import IchimokuTrendStrategy
    strategy_classes.append(('Ichimoku', IchimokuTrendStrategy()))
except Exception as e:
    print(f"Ichimoku: {e}")

try:
    from strategies.technical.ema_crossover import EMACrossoverStrategy
    strategy_classes.append(('EMA_Cross', EMACrossoverStrategy()))
except Exception as e:
    print(f"EMA: {e}")

try:
    from strategies.technical.vwap_bounce import VWAPBounceStrategy
    strategy_classes.append(('VWAP', VWAPBounceStrategy()))
except Exception as e:
    print(f"VWAP: {e}")

try:
    from strategies.technical.order_flow_imbalance import OrderFlowImbalanceStrategy
    strategy_classes.append(('OrderFlow', OrderFlowImbalanceStrategy()))
except Exception as e:
    print(f"OrderFlow: {e}")

try:
    from strategies.technical.volume_profile import VolumeProfileStrategy
    strategy_classes.append(('VolProfile', VolumeProfileStrategy()))
except Exception as e:
    print(f"VolProfile: {e}")

try:
    from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy
    strategy_classes.append(('BollSqueeze', BollingerSqueezeStrategy()))
except Exception as e:
    print(f"BollSqueeze: {e}")

try:
    from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
    strategy_classes.append(('RSI_MR', RSIMeanReversionStrategy()))
except Exception as e:
    print(f"RSI_MR: {e}")

try:
    from strategies.technical.zscore_mean_reversion import ZScoreMeanReversionStrategy
    strategy_classes.append(('ZScore', ZScoreMeanReversionStrategy()))
except Exception as e:
    print(f"ZScore: {e}")

try:
    from strategies.technical.smart_money import SmartMoneyStrategy
    strategy_classes.append(('SmartMoney', SmartMoneyStrategy()))
except Exception as e:
    print(f"SmartMoney: {e}")

try:
    from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
    strategy_classes.append(('Donchian', DonchianBreakoutStrategy()))
except Exception as e:
    print(f"Donchian: {e}")

try:
    from strategies.technical.momentum_exhaustion import MomentumExhaustionStrategy
    strategy_classes.append(('MomExhaust', MomentumExhaustionStrategy()))
except Exception as e:
    print(f"MomExhaust: {e}")

print()
print('=' * 100)
print('  STRATEGY SHORT-SIDE PERFORMANCE — Can we profit from the bear?')
print('=' * 100)
print()
print(f"  {'Strategy':15s} {'Total':>7s} {'Longs':>7s} {'Shorts':>7s} {'Net PnL':>10s} {'Long $':>10s} {'Short $':>10s} {'WR':>6s}")
print('-' * 85)

for name, strat in strategy_classes:
    total_trades = 0
    long_trades = 0
    short_trades = 0
    total_pnl = 0
    long_pnl = 0
    short_pnl = 0
    total_wins = 0

    for sym, df in data.items():
        try:
            engine = BacktestEngine(initial_capital=10000, regime_filter=True)
            result = engine.run(df, strat)

            for t in result.trades:
                total_trades += 1
                total_pnl += t.net_pnl
                if t.net_pnl > 0:
                    total_wins += 1

                side = t.side.value if hasattr(t.side, 'value') else str(t.side)
                if side.upper() in ['LONG', 'BUY']:
                    long_trades += 1
                    long_pnl += t.net_pnl
                else:
                    short_trades += 1
                    short_pnl += t.net_pnl
        except Exception as e:
            pass

    wr = total_wins / total_trades * 100 if total_trades else 0
    sign = '+' if total_pnl >= 0 else ''
    lsign = '+' if long_pnl >= 0 else ''
    ssign = '+' if short_pnl >= 0 else ''
    print(f"  {name:15s} {total_trades:>7d} {long_trades:>7d} {short_trades:>7d} {sign}${total_pnl:>8.0f} {lsign}${long_pnl:>8.0f} {ssign}${short_pnl:>8.0f} {wr:>5.1f}%")

print()
print('=' * 100)
