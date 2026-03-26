"""Validate BB-MR with actual strategy parameters matching live config.
Uses cross-compensation logic like the real strategy."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

import ccxt
import pandas as pd
import numpy as np

k = ccxt.kraken()

def backtest_bbmr_full(symbol, bars=500, tf='1h'):
    """Full BB-MR backtest matching live strategy parameters."""
    ohlcv = k.fetch_ohlcv(symbol, tf, limit=bars)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    # BB (period=20, std=2.0)
    df['sma'] = df['close'].rolling(20).mean()
    df['bb_std'] = df['close'].rolling(20).std()
    df['bb_upper'] = df['sma'] + 2.0 * df['bb_std']
    df['bb_lower'] = df['sma'] - 2.0 * df['bb_std']
    df['pctb'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

    # RSI (14)
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # StochRSI -> StochK (14 period, 3 smooth)
    rsi_min = df['rsi'].rolling(14).min()
    rsi_max = df['rsi'].rolling(14).max()
    df['stoch_k'] = ((df['rsi'] - rsi_min) / (rsi_max - rsi_min) * 100).rolling(3).mean()

    # ADX (simplified)
    tr = np.maximum(df['high'] - df['low'],
                    np.maximum(abs(df['high'] - df['close'].shift(1)),
                              abs(df['low'] - df['close'].shift(1))))
    df['atr'] = tr.rolling(14).mean()
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

    # Live params
    pctb_long = 0.25
    pctb_short = 0.75
    stoch_oversold = 25.0
    stoch_overbought = 75.0
    adx_max = 30.0
    atr_stop_mult = 1.5

    trades = []
    in_trade = False
    direction = None
    entry_price = entry_bar = stop_loss = take_profit = 0

    for i in range(50, len(df)):
        row = df.iloc[i]
        if pd.isna(row['adx']) or pd.isna(row['atr']) or pd.isna(row['stoch_k']):
            continue

        if not in_trade:
            # Cross-compensation (matching live strategy)
            pctb_eff = pctb_long
            stoch_os_eff = stoch_oversold
            if row['stoch_k'] < stoch_oversold * 0.75:
                depth = 1.0 - row['stoch_k'] / (stoch_oversold * 0.75)
                pctb_eff *= (1.0 + 0.8 * depth)
            if row['pctb'] < pctb_long * 0.6:
                depth = 1.0 - row['pctb'] / (pctb_long * 0.6)
                stoch_os_eff *= (1.0 + 0.6 * depth)

            # LONG entry
            if (row['pctb'] < pctb_eff and row['stoch_k'] < stoch_os_eff
                and row['adx'] < adx_max and row['atr'] > 0):
                in_trade = True
                direction = 'LONG'
                entry_price = row['close']
                entry_bar = i
                stop_loss = entry_price - atr_stop_mult * row['atr']
                take_profit = row['bb_upper']  # opposite band TP
        else:
            if direction == 'LONG':
                if row['low'] <= stop_loss:
                    pnl = (stop_loss - entry_price) / entry_price * 100
                    trades.append({'pnl': pnl, 'reason': 'SL', 'bars': i - entry_bar})
                    in_trade = False
                elif row['high'] >= take_profit or row['pctb'] >= 0.75:
                    exit_p = min(row['close'], take_profit) if row['close'] > entry_price else row['close']
                    pnl = (exit_p - entry_price) / entry_price * 100
                    trades.append({'pnl': pnl, 'reason': 'TP', 'bars': i - entry_bar})
                    in_trade = False

    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    total = sum(t['pnl'] for t in trades)
    wr = len(wins) / len(trades) * 100 if trades else 0
    loss_sum = abs(sum(t['pnl'] for t in losses)) if losses else 0.001
    pf = sum(t['pnl'] for t in wins) / loss_sum if wins else 0

    return {
        'symbol': symbol, 'trades': len(trades), 'wr': wr,
        'total': total, 'pf': pf,
        'avg_win': np.mean([t['pnl'] for t in wins]) if wins else 0,
        'avg_loss': np.mean([t['pnl'] for t in losses]) if losses else 0,
    }


print("=== BB-MR Full Validation (500 bars 1h, cross-comp + opposite TP) ===")
print(f"{'Symbol':12s} {'Trades':>6s} {'WR%':>6s} {'Return%':>8s} {'PF':>6s} {'AvgWin':>8s} {'AvgLoss':>8s}")
print("-" * 65)

symbols = ['DOGE/USD', 'BTC/USD', 'ADA/USD', 'LTC/USD', 'ATOM/USD', 'LINK/USD', 'XRP/USD']
grand_total = 0
grand_trades = 0
for sym in symbols:
    try:
        r = backtest_bbmr_full(sym)
        marker = " ***" if r['total'] > 2.0 else " ++" if r['total'] > 0 else " --"
        print(f"{r['symbol']:12s} {r['trades']:6d} {r['wr']:5.0f}% {r['total']:+7.2f}% {r['pf']:5.1f}x {r['avg_win']:+7.2f}% {r['avg_loss']:+7.2f}%{marker}")
        grand_total += r['total']
        grand_trades += r['trades']
    except Exception as e:
        print(f"{sym:12s} ERROR: {e}")

print("-" * 65)
print(f"{'TOTAL':12s} {grand_trades:6d}        {grand_total:+7.2f}%")
print(f"\nPortfolio return (equal weight): {grand_total / len(symbols):+.2f}%")
