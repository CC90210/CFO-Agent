"""Test RSI-MR parameter variations."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import ccxt
import pandas as pd
import numpy as np

k = ccxt.kraken()

def backtest_rsi_mr(symbol, rsi_os=35, rsi_ob=65, rsi_period=10, bars=500, tf='4h'):
    ohlcv = k.fetch_ohlcv(symbol, tf, limit=bars)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(rsi_period).mean()
    loss = (-delta.clip(upper=0)).rolling(rsi_period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    tr = np.maximum(df['high'] - df['low'],
                    np.maximum(abs(df['high'] - df['close'].shift(1)),
                              abs(df['low'] - df['close'].shift(1))))
    df['atr'] = tr.rolling(14).mean()

    trades = []
    in_trade = False

    for i in range(30, len(df)):
        row = df.iloc[i]
        if pd.isna(row['rsi']) or pd.isna(row['atr']) or row['atr'] <= 0:
            continue

        if not in_trade:
            if row['rsi'] < rsi_os:
                in_trade = True
                entry_price = row['close']
                entry_bar = i
                stop_loss = entry_price - 1.0 * row['atr']
                take_profit = entry_price + 2.0 * row['atr']
        else:
            if row['low'] <= stop_loss:
                pnl = (stop_loss - entry_price) / entry_price * 100
                trades.append({'pnl': pnl, 'reason': 'SL'})
                in_trade = False
            elif row['high'] >= take_profit:
                pnl = (take_profit - entry_price) / entry_price * 100
                trades.append({'pnl': pnl, 'reason': 'TP'})
                in_trade = False
            elif row['rsi'] >= 50:  # RSI exit
                pnl = (row['close'] - entry_price) / entry_price * 100
                trades.append({'pnl': pnl, 'reason': 'RSI_EXIT'})
                in_trade = False

    wins = [t for t in trades if t['pnl'] > 0]
    total = sum(t['pnl'] for t in trades)
    wr = len(wins) / len(trades) * 100 if trades else 0
    return {'trades': len(trades), 'wr': wr, 'total': total}


symbols = ['BTC/USD', 'AVAX/USD', 'LINK/USD', 'ETH/USD', 'DOGE/USD', 'ADA/USD', 'LTC/USD']
params = [
    (30, 70, "30/70 (strict)"),
    (35, 65, "35/65 (current)"),
    (38, 62, "38/62 (agent rec)"),
]

for rsi_os, rsi_ob, label in params:
    print(f"\n=== RSI {label} ===")
    print(f"{'Symbol':12s} {'Trades':>6s} {'WR%':>6s} {'Return%':>8s}")
    print("-" * 38)
    grand = 0
    grand_t = 0
    for sym in symbols:
        try:
            r = backtest_rsi_mr(sym, rsi_os=rsi_os, rsi_ob=rsi_ob)
            print(f"{sym:12s} {r['trades']:6d} {r['wr']:5.0f}% {r['total']:+7.2f}%")
            grand += r['total']
            grand_t += r['trades']
        except Exception as e:
            print(f"{sym:12s} ERROR: {e}")
    print(f"{'TOTAL':12s} {grand_t:6d}        {grand:+7.2f}%")
