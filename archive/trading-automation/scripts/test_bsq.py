"""Test Bollinger Squeeze strategy potential."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import ccxt
import pandas as pd
import numpy as np

k = ccxt.kraken()

def test_squeeze(symbol, tf='1h', bars=500):
    """Simple BB squeeze backtest."""
    ohlcv = k.fetch_ohlcv(symbol, tf, limit=bars)
    df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])

    # Bollinger Bands
    df['sma20'] = df['c'].rolling(20).mean()
    df['bb_std'] = df['c'].rolling(20).std()
    df['bb_upper'] = df['sma20'] + 2.0 * df['bb_std']
    df['bb_lower'] = df['sma20'] - 2.0 * df['bb_std']
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['sma20']

    # Keltner Channels
    tr = np.maximum(df['h'] - df['l'], np.maximum(abs(df['h'] - df['c'].shift(1)), abs(df['l'] - df['c'].shift(1))))
    df['atr'] = tr.rolling(20).mean()
    df['kc_upper'] = df['sma20'] + 1.5 * df['atr']
    df['kc_lower'] = df['sma20'] - 1.5 * df['atr']

    # Squeeze = BB inside KC
    df['squeeze'] = (df['bb_lower'] > df['kc_lower']) & (df['bb_upper'] < df['kc_upper'])

    # Momentum (close - midline of KC/BB)
    df['momentum'] = df['c'] - df['sma20']
    df['mom_accel'] = df['momentum'].diff()

    trades = []
    in_trade = False

    for i in range(30, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i-1]

        if pd.isna(row['atr']) or row['atr'] <= 0:
            continue

        if not in_trade:
            # Squeeze fires: was in squeeze, now released
            if not row['squeeze'] and prev['squeeze']:
                # Direction from momentum
                if row['momentum'] > 0 and row['mom_accel'] > 0:
                    in_trade = True
                    direction = 'LONG'
                    entry = row['c']
                    sl = entry - 1.5 * row['atr']
                    tp = entry + 3.0 * row['atr']
                    entry_bar = i
                elif row['momentum'] < 0 and row['mom_accel'] < 0:
                    in_trade = True
                    direction = 'SHORT'
                    entry = row['c']
                    sl = entry + 1.5 * row['atr']
                    tp = entry - 3.0 * row['atr']
                    entry_bar = i
        else:
            if direction == 'LONG':
                if row['l'] <= sl:
                    pnl = (sl - entry) / entry * 100
                    trades.append({'pnl': pnl, 'bars': i - entry_bar, 'reason': 'SL'})
                    in_trade = False
                elif row['h'] >= tp:
                    pnl = (tp - entry) / entry * 100
                    trades.append({'pnl': pnl, 'bars': i - entry_bar, 'reason': 'TP'})
                    in_trade = False
                elif i - entry_bar > 48:  # 48 bar timeout
                    pnl = (row['c'] - entry) / entry * 100
                    trades.append({'pnl': pnl, 'bars': i - entry_bar, 'reason': 'TIMEOUT'})
                    in_trade = False
            else:  # SHORT
                if row['h'] >= sl:
                    pnl = (entry - sl) / entry * 100
                    trades.append({'pnl': pnl, 'bars': i - entry_bar, 'reason': 'SL'})
                    in_trade = False
                elif row['l'] <= tp:
                    pnl = (entry - tp) / entry * 100
                    trades.append({'pnl': pnl, 'bars': i - entry_bar, 'reason': 'TP'})
                    in_trade = False
                elif i - entry_bar > 48:
                    pnl = (entry - row['c']) / entry * 100
                    trades.append({'pnl': pnl, 'bars': i - entry_bar, 'reason': 'TIMEOUT'})
                    in_trade = False

    wins = [t for t in trades if t['pnl'] > 0]
    total = sum(t['pnl'] for t in trades)
    wr = len(wins) / len(trades) * 100 if trades else 0
    loss_sum = abs(sum(t['pnl'] for t in trades if t['pnl'] <= 0)) or 0.001
    pf = sum(t['pnl'] for t in wins) / loss_sum if wins else 0

    return {'symbol': symbol, 'trades': len(trades), 'wr': wr, 'total': total, 'pf': pf}


symbols = ['BTC/USD', 'ETH/USD', 'DOGE/USD', 'ADA/USD', 'LTC/USD', 'ATOM/USD', 'LINK/USD', 'AVAX/USD', 'XRP/USD']
print("=== Bollinger Squeeze Backtest (500 bars 1h, R:R 1:2) ===")
print(f"{'Symbol':12s} {'Trades':>6s} {'WR%':>6s} {'Return%':>8s} {'PF':>6s}")
print("-" * 42)

grand = 0
grand_t = 0
for sym in symbols:
    try:
        r = test_squeeze(sym)
        marker = " ***" if r['total'] > 2 else " ++" if r['total'] > 0 else " --"
        print(f"{r['symbol']:12s} {r['trades']:6d} {r['wr']:5.0f}% {r['total']:+7.2f}% {r['pf']:5.1f}x{marker}")
        grand += r['total']
        grand_t += r['trades']
    except Exception as e:
        print(f"{sym:12s} ERROR: {e}")

print("-" * 42)
print(f"{'TOTAL':12s} {grand_t:6d}        {grand:+7.2f}%")
