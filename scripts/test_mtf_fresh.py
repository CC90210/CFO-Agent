"""
scripts/test_mtf_fresh.py — Fresh backtest of MultiTimeframeStrategy on Kraken 4H data.

Symbols  : DOGE/USD, XRP/USD, LINK/USD
Bars     : 500 x 4H candles
Exchange : Kraken (public API — no keys required)

LIMITATION: The backtesting engine supports only a single primary timeframe.
The MultiTimeframeStrategy performs internal resampling from the supplied DataFrame.
When the primary timeframe is already 4H:
  - HTF resample ("4h") from 4H data → produces the same candles (no-op resample).
  - MTF resample ("1h") from 4H data → Pandas resample with forward-filled timestamps,
    but since 4H bars already span > 1H, the resulting 1H frame has the same bars
    with a 1H-aligned index. The strategy reads EMA slopes, which still hold signal.
  - LTF is the raw 4H data used for MACD/RSI entry triggers.

This matches how test_bsq.py operates: single-TF self-contained loop.
The multi-TF confluence score will be lower than with true multi-TF feeds,
which means trade counts will be conservative (fewer false signals).

Parameters from config/strategies.yaml:
  htf_fast_ema=30, htf_slow_ema=100, mtf_ema=10
  ltf_macd_fast=12, ltf_macd_slow=26, ltf_macd_signal=9
  atr_period=14, atr_stop_mult=2.5, atr_tp_mult(rr_ratio)=5.0
  rsi_period=14 (mapped to ltf_rsi_period), rsi_oversold=35 (ltf_rsi_entry_long),
  rsi_overbought=65 (ltf_rsi_entry_short)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import ccxt
import pandas as pd
import numpy as np

from strategies.technical.multi_timeframe import MultiTimeframeStrategy
from strategies.base import Direction

# ---------------------------------------------------------------------------
# Strategy instance — parameters from config/strategies.yaml
# ---------------------------------------------------------------------------
STRATEGY = MultiTimeframeStrategy(
    htf_fast_ema=30,
    htf_slow_ema=100,
    mtf_ema=10,
    ltf_macd_fast=12,
    ltf_macd_slow=26,
    ltf_macd_signal=9,
    ltf_rsi_period=14,
    ltf_rsi_entry_long=35.0,    # rsi_oversold from config
    ltf_rsi_entry_short=65.0,   # rsi_overbought from config
    atr_period=14,
    atr_stop_mult=2.5,
    rr_ratio=5.0,               # atr_tp_mult from config
    min_confluence=2,
    htf_resample_rule="4h",
    mtf_resample_rule="1h",
)

SYMBOLS = ["DOGE/USD", "XRP/USD", "LINK/USD"]
TF = "4h"
BARS = 500
TIMEOUT_BARS = 72   # 12 days on 4H — same timeout ratio as test_bsq.py's 48 on 1H

kraken = ccxt.kraken()


def fetch_df(symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    """Fetch OHLCV from Kraken and return a properly indexed DataFrame."""
    ohlcv = kraken.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp")
    df.attrs["symbol"] = symbol
    return df


def backtest_symbol(symbol: str) -> dict:
    """Walk-forward bar-by-bar backtest using MultiTimeframeStrategy.analyze()."""
    df_full = fetch_df(symbol, TF, BARS)

    # Need enough warm-up bars for the slowest indicator (htf_slow_ema=100 + buffer)
    warmup = STRATEGY._min_bars_ltf  # already computed in __init__

    trades = []
    in_trade = False
    direction = None
    entry = 0.0
    sl = 0.0
    tp = 0.0
    entry_bar = 0

    for i in range(warmup, len(df_full)):
        # Feed strategy a growing window up to bar i (inclusive)
        window = df_full.iloc[: i + 1].copy()
        window.attrs["symbol"] = symbol

        row = df_full.iloc[i]

        if not in_trade:
            signal = STRATEGY.analyze(window)

            if signal is not None:
                if signal.direction == Direction.LONG:
                    in_trade = True
                    direction = "LONG"
                    entry = signal.metadata["entry_price"]
                    sl = signal.stop_loss
                    tp = signal.take_profit
                    entry_bar = i
                elif signal.direction == Direction.SHORT:
                    in_trade = True
                    direction = "SHORT"
                    entry = signal.metadata["entry_price"]
                    sl = signal.stop_loss
                    tp = signal.take_profit
                    entry_bar = i
        else:
            bars_held = i - entry_bar

            if direction == "LONG":
                if row["low"] <= sl:
                    pnl_pct = (sl - entry) / entry * 100
                    trades.append({"pnl": pnl_pct, "bars": bars_held, "reason": "SL"})
                    in_trade = False
                elif row["high"] >= tp:
                    pnl_pct = (tp - entry) / entry * 100
                    trades.append({"pnl": pnl_pct, "bars": bars_held, "reason": "TP"})
                    in_trade = False
                elif bars_held >= TIMEOUT_BARS:
                    pnl_pct = (row["close"] - entry) / entry * 100
                    trades.append({"pnl": pnl_pct, "bars": bars_held, "reason": "TIMEOUT"})
                    in_trade = False
            else:  # SHORT
                if row["high"] >= sl:
                    pnl_pct = (entry - sl) / entry * 100
                    trades.append({"pnl": pnl_pct, "bars": bars_held, "reason": "SL"})
                    in_trade = False
                elif row["low"] <= tp:
                    pnl_pct = (entry - tp) / entry * 100
                    trades.append({"pnl": pnl_pct, "bars": bars_held, "reason": "TP"})
                    in_trade = False
                elif bars_held >= TIMEOUT_BARS:
                    pnl_pct = (entry - row["close"]) / entry * 100
                    trades.append({"pnl": pnl_pct, "bars": bars_held, "reason": "TIMEOUT"})
                    in_trade = False

    # --- Metrics ---
    if not trades:
        return {
            "symbol": symbol,
            "trades": 0,
            "win_rate": 0.0,
            "total_return": 0.0,
            "profit_factor": 0.0,
            "sharpe": 0.0,
        }

    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]

    total_return = sum(pnls)
    win_rate = len(wins) / len(trades) * 100
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses)) or 1e-9
    profit_factor = gross_profit / gross_loss if wins else 0.0

    # Sharpe: annualised on per-trade PnL series (4H bars → ~1460 bars/year)
    # Approximate trades-per-year for annualisation
    arr = np.array(pnls)
    if arr.std() > 0 and len(arr) > 1:
        bars_per_year = 1460  # 365 days * 4 bars/day on 4H
        trades_per_year = len(trades) / (BARS / bars_per_year)
        sharpe = (arr.mean() / arr.std()) * np.sqrt(trades_per_year)
    else:
        sharpe = 0.0

    return {
        "symbol": symbol,
        "trades": len(trades),
        "win_rate": win_rate,
        "total_return": total_return,
        "profit_factor": profit_factor,
        "sharpe": sharpe,
        "breakdown": {
            "sl_hits": sum(1 for t in trades if t["reason"] == "SL"),
            "tp_hits": sum(1 for t in trades if t["reason"] == "TP"),
            "timeouts": sum(1 for t in trades if t["reason"] == "TIMEOUT"),
        },
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
print()
print("=== MultiTimeframe Strategy — Fresh Backtest ===")
print(f"Bars: {BARS} x {TF} | Exchange: Kraken | Symbols: {', '.join(SYMBOLS)}")
print()
print("LIMITATION: Single primary timeframe (4H). MTF resamples from 4H data.")
print("  HTF ('4h' resample of 4H) = same candles — trend filter is valid.")
print("  MTF ('1h' resample of 4H) = same bars, 1H-aligned index — EMA slope valid.")
print("  Confluence count will be conservative vs. true multi-TF feeds.")
print()
print(f"{'Symbol':12s} {'Trades':>7s} {'WinRate':>8s} {'Return%':>9s} {'ProfFact':>9s} {'Sharpe':>7s}")
print("-" * 58)

grand_return = 0.0
grand_trades = 0

for sym in SYMBOLS:
    try:
        r = backtest_symbol(sym)
        marker = " ***" if r["total_return"] > 5 else " ++" if r["total_return"] > 0 else " --"
        print(
            f"{r['symbol']:12s}"
            f" {r['trades']:7d}"
            f" {r['win_rate']:7.1f}%"
            f" {r['total_return']:+8.2f}%"
            f" {r['profit_factor']:8.2f}x"
            f" {r['sharpe']:+6.2f}"
            f"{marker}"
        )
        if r["trades"] > 0:
            bd = r["breakdown"]
            print(
                f"{'':12s}  SL:{bd['sl_hits']} TP:{bd['tp_hits']} TIMEOUT:{bd['timeouts']}"
            )
        grand_return += r["total_return"]
        grand_trades += r["trades"]
    except Exception as exc:
        print(f"{sym:12s} ERROR: {exc}")

print("-" * 58)
print(f"{'TOTAL':12s} {grand_trades:7d}          {grand_return:+8.2f}%")
print()
print("Params: htf_fast=30 htf_slow=100 mtf=10 | atr_stop=2.5x atr_tp=5.0x")
print("        macd(12,26,9) | rsi_period=14 oversold=35 overbought=65")
