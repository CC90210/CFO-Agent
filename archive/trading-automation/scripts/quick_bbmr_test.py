"""Quick BB-MR backtest for new symbols."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import ccxt
import pandas as pd
import numpy as np

k = ccxt.kraken()

def backtest_bbmr(symbol, bars=500, tf='1h'):
    ohlcv = k.fetch_ohlcv(symbol, tf, limit=bars)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # BB
    df['sma'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['sma'] + 2.0 * df['bb_std']
    df['bb_lower'] = df['sma'] - 2.0 * df['bb_std']
    df['pctb'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # RSI
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # StochRSI -> StochK
    rsi_min = df['rsi'].rolling(14).min()
    rsi_max = df['rsi'].rolling(14).max()
    df['stoch_k'] = ((df['rsi'] - rsi_min) / (rsi_max - rsi_min) * 100).rolling(3).mean()

    # ADX (simplified)
    tr = np.maximum(df['high'] - df['low'],
                    np.maximum(abs(df['high'] - df['close'].shift(1)),
                              abs(df['low'] - df['close'].shift(1))))
    df['atr'] = tr.rolling(14).mean()

    # Simple ADX proxy using directional movement
    up = df['high'].diff()
    down = -df['low'].diff()
    pdm = np.where((up > down) & (up > 0), up, 0)
    ndm = np.where((down > up) & (down > 0), down, 0)
    pdm_smooth = pd.Series(pdm).rolling(14).mean()
    ndm_smooth = pd.Series(ndm).rolling(14).mean()
    pdi = 100 * pdm_smooth / df['atr']
    ndi = 100 * ndm_smooth / df['atr']
    dx = 100 * abs(pdi - ndi) / (pdi + ndi)
    df['adx'] = dx.rolling(14).mean()

    trades = []
    in_trade = False
    entry_price = entry_bar = stop_loss = 0

    for i in range(50, len(df)):
        row = df.iloc[i]
        if pd.isna(row['adx']) or pd.isna(row['atr']) or pd.isna(row['stoch_k']):
            continue

        if not in_trade:
            if (row['pctb'] < 0.25 and row['stoch_k'] < 25 and row['adx'] < 30
                and row['atr'] > 0):
                in_trade = True
                entry_price = row['close']
                entry_bar = i
                stop_loss = entry_price - 1.5 * row['atr']
        else:
            if row['low'] <= stop_loss:
                pnl = (stop_loss - entry_price) / entry_price * 100
                trades.append({'pnl': pnl, 'reason': 'SL', 'bars': i - entry_bar})
                in_trade = False
            elif row['pctb'] >= 0.75 or row['close'] >= row['bb_upper']:
                pnl = (row['close'] - entry_price) / entry_price * 100
                trades.append({'pnl': pnl, 'reason': 'TP', 'bars': i - entry_bar})
                in_trade = False

    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    total = sum(t['pnl'] for t in trades)
    wr = len(wins) / len(trades) * 100 if trades else 0
    pf = sum(t['pnl'] for t in wins) / abs(sum(t['pnl'] for t in losses)) if losses and sum(t['pnl'] for t in losses) != 0 else float('inf')

    return {
        'symbol': symbol,
        'trades': len(trades),
        'wr': wr,
        'total': total,
        'pf': pf,
        'avg_bars': np.mean([t['bars'] for t in trades]) if trades else 0,
    }

# Test new symbols for BB-MR
symbols = ['ATOM/USD', 'DOT/USD', 'LINK/USD', 'SOL/USD', 'AVAX/USD', 'ETH/USD',
           'DOGE/USD', 'BTC/USD', 'ADA/USD', 'LTC/USD', 'XRP/USD']

print(f"{'Symbol':12s} {'Trades':>6s} {'WR%':>6s} {'Return%':>8s} {'PF':>6s} {'AvgBars':>7s}")
print("-" * 55)
for sym in symbols:
    try:
        r = backtest_bbmr(sym)
        marker = " ***" if r['total'] > 1.0 else " ++" if r['total'] > 0 else ""
        print(f"{r['symbol']:12s} {r['trades']:6d} {r['wr']:5.0f}% {r['total']:+7.2f}% {r['pf']:5.1f}x {r['avg_bars']:6.0f}{marker}")
    except Exception as e:
        print(f"{sym:12s} ERROR: {e}")
