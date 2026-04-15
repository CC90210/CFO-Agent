"""Extended mean-reversion backtest: RSI Mean Reversion + Bollinger Squeeze across 9 symbols."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import ccxt
import pandas as pd
import numpy as np
import math
import traceback

from backtesting.engine import BacktestEngine
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy


SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "ATOM/USDT", "DOGE/USDT",
    "XRP/USDT", "ADA/USDT", "DOT/USDT", "AVAX/USDT",
]

TIMEFRAME = "4h"
CANDLE_LIMIT = 1500


def fetch_ohlcv(exchange, symbol: str) -> pd.DataFrame | None:
    """Fetch OHLCV from Kraken and return a DatetimeIndex DataFrame."""
    try:
        # Kraken uses different symbol format
        raw = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=CANDLE_LIMIT)
        if not raw or len(raw) < 100:
            print(f"  [SKIP] {symbol}: only {len(raw) if raw else 0} candles returned")
            return None
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        print(f"  [OK] {symbol}: {len(df)} candles fetched ({df.index[0].date()} to {df.index[-1].date()})")
        return df
    except Exception as e:
        print(f"  [ERROR] {symbol}: {e}")
        return None


def run_backtest(df: pd.DataFrame, strategy, symbol: str) -> dict | None:
    """Run a single backtest and return a summary dict."""
    try:
        engine = BacktestEngine(initial_capital=10000, regime_filter=True)
        result = engine.run(df, strategy)

        trades = result.trades
        total_trades = result.total_trades
        net_pnl = result.final_equity - result.initial_capital
        win_rate = result.win_rate
        sharpe = result.sharpe_ratio
        pf = result.profit_factor
        max_dd = result.max_drawdown

        candidate = total_trades > 3 and net_pnl > 0

        return {
            "symbol": symbol,
            "trades": total_trades,
            "net_pnl": net_pnl,
            "win_rate": win_rate,
            "sharpe": sharpe,
            "profit_factor": pf,
            "max_dd": max_dd,
            "candidate": candidate,
        }
    except Exception as e:
        print(f"    [BACKTEST ERROR] {symbol}: {e}")
        traceback.print_exc()
        return None


def print_table(strategy_name: str, results: list[dict]):
    """Print a formatted summary table."""
    print()
    print("=" * 100)
    print(f"  {strategy_name} — Extended Backtest Results ({TIMEFRAME}, {CANDLE_LIMIT} candles, Kraken)")
    print("=" * 100)
    header = f"{'Symbol':<14} {'Trades':>6} {'Net P&L':>12} {'Win Rate':>10} {'Sharpe':>8} {'PF':>8} {'Max DD':>10} {'Status'}"
    print(header)
    print("-" * 100)

    for r in results:
        if r is None:
            continue
        status = "** CANDIDATE **" if r["candidate"] else ""
        pnl_str = f"${r['net_pnl']:>+10.2f}"
        wr_str = f"{r['win_rate'] * 100:.1f}%"
        sharpe_str = f"{r['sharpe']:.3f}"
        pf_str = f"{r['profit_factor']:.3f}" if not math.isinf(r['profit_factor']) else "inf"
        dd_str = f"{r['max_dd'] * 100:.2f}%"
        print(f"{r['symbol']:<14} {r['trades']:>6} {pnl_str} {wr_str:>10} {sharpe_str:>8} {pf_str:>8} {dd_str:>10}   {status}")

    # Summary
    valid = [r for r in results if r is not None]
    candidates = [r for r in valid if r["candidate"]]
    total_pnl = sum(r["net_pnl"] for r in valid)
    print("-" * 100)
    print(f"  Total net P&L across all symbols: ${total_pnl:+.2f}")
    print(f"  Candidates for enabling: {len(candidates)}/{len(valid)}")
    if candidates:
        for c in candidates:
            print(f"    -> {c['symbol']}: ${c['net_pnl']:+.2f}, {c['trades']} trades, {c['win_rate']*100:.1f}% WR, Sharpe {c['sharpe']:.3f}")
    print("=" * 100)


def main():
    print("Atlas online. Running extended mean-reversion backtests.\n")

    # Initialize Kraken exchange
    print("Connecting to Kraken...")
    exchange = ccxt.kraken({"enableRateLimit": True})
    exchange.load_markets()
    print(f"Markets loaded: {len(exchange.markets)} pairs available.\n")

    # Fetch all data first
    print("--- Fetching OHLCV data ---")
    data = {}
    for sym in SYMBOLS:
        data[sym] = fetch_ohlcv(exchange, sym)

    # --- RSI Mean Reversion ---
    print("\n--- Running RSI Mean Reversion backtests ---")
    rsi_strategy = RSIMeanReversionStrategy()
    rsi_results = []
    for sym in SYMBOLS:
        df = data.get(sym)
        if df is None:
            rsi_results.append(None)
            continue
        print(f"  Backtesting {sym}...")
        r = run_backtest(df, rsi_strategy, sym)
        rsi_results.append(r)

    print_table("RSI Mean Reversion", rsi_results)

    # --- Bollinger Squeeze ---
    print("\n--- Running Bollinger Squeeze backtests ---")
    bb_strategy = BollingerSqueezeStrategy()
    bb_results = []
    for sym in SYMBOLS:
        df = data.get(sym)
        if df is None:
            bb_results.append(None)
            continue
        print(f"  Backtesting {sym}...")
        r = run_backtest(df, bb_strategy, sym)
        bb_results.append(r)

    print_table("Bollinger Squeeze", bb_results)

    print("\nDone.")


if __name__ == "__main__":
    main()
