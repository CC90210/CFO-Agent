"""
Live Market Scanner — Check how close each pair is to generating a signal.
Shows regime, Donchian channel distance, RSI, ADX, volume ratio for all pairs.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy
from core.regime_detector import RegimeDetector
import ccxt, pandas as pd, numpy as np

exchange = ccxt.kraken({'enableRateLimit': True})
regime_detector = RegimeDetector()

SYMBOLS = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'ADA/USD', 'DOT/USD',
           'XRP/USD', 'AVAX/USD', 'ATOM/USD', 'DOGE/USD', 'SHIB/USD', 'MANA/USD']

print('=' * 100)
print('  ATLAS LIVE MARKET SCANNER — How close are we to signals?')
print('=' * 100)
print()

for sym in SYMBOLS:
    try:
        ohlcv = exchange.fetch_ohlcv(sym, '4h', limit=300)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        close = df['close']
        high = df['high']
        low = df['low']
        close_now = close.iloc[-1]

        # Regime
        regime_result = regime_detector.detect(df)
        regime = regime_result.regime.value

        # Donchian channels (20-period)
        entry_high = high.shift(1).rolling(20).max().iloc[-1]
        entry_low = low.shift(1).rolling(20).min().iloc[-1]
        dist_to_long = ((entry_high - close_now) / close_now * 100) if entry_high > close_now else 0
        dist_to_short = ((close_now - entry_low) / close_now * 100) if close_now > entry_low else 0
        long_breakout = close_now > entry_high
        short_breakout = close_now < entry_low

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi_now = float((100 - 100 / (1 + rs)).iloc[-1])

        # ADX (simplified)
        from strategies.technical.indicators import adx
        adx_df = adx(df, 14)
        adx_now = float(adx_df['adx'].iloc[-1])

        # Volume ratio
        vol_avg = df['volume'].rolling(20).mean().iloc[-1]
        vol_now = df['volume'].iloc[-1]
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 0

        # Strategy signals
        donchian = DonchianBreakoutStrategy()
        donchian_signal = donchian.analyze(df)
        donchian_dir = donchian_signal.direction.value if donchian_signal else 'FLAT'

        sm = SmartMoneyStrategy()
        sm_signal = sm.analyze(df)
        sm_dir = sm_signal.direction.value if sm_signal else 'FLAT'

        # Status
        if long_breakout:
            channel_status = 'LONG BREAKOUT!'
        elif short_breakout:
            channel_status = 'SHORT BREAKOUT!'
        elif dist_to_long < 2.0:
            channel_status = f'NEAR LONG ({dist_to_long:.1f}% away)'
        elif dist_to_short < 2.0:
            channel_status = f'NEAR SHORT ({dist_to_short:.1f}% away)'
        else:
            channel_status = f'mid-range (L:{dist_to_long:.1f}% S:{dist_to_short:.1f}%)'

        # Volume gate
        vol_status = 'OK' if vol_ratio >= 1.2 else f'LOW ({vol_ratio:.2f}x)'

        # RSI status
        if rsi_now < 28:
            rsi_status = f'OVERSOLD ({rsi_now:.0f})'
        elif rsi_now > 72:
            rsi_status = f'OVERBOUGHT ({rsi_now:.0f})'
        else:
            rsi_status = f'{rsi_now:.0f}'

        print(f'  {sym:12s} | {regime:12s} | Donchian: {channel_status:30s} | '
              f'RSI: {rsi_status:15s} | ADX: {adx_now:4.0f} | Vol: {vol_status:12s} | '
              f'Signal: {donchian_dir:5s} / SM:{sm_dir:5s}')

    except Exception as e:
        print(f'  {sym:12s} | ERROR: {e}')

print()
print('  LEGEND:')
print('    Donchian: distance to 20-bar high (long breakout) or low (short breakout)')
print('    Volume: need 1.2x avg for signal confirmation (OK = meets threshold)')
print('    ADX: need >= 20 for trend confirmation')
print('    Signal: actual strategy output (LONG/SHORT/FLAT)')
print()

# Check Kraken account balance
try:
    # This would need API keys to work
    print('  NOTE: To check Kraken balance, use the Kraken web interface.')
    print('  Paper trading daemon is running — it will execute when signals appear.')
except:
    pass

print('=' * 100)
