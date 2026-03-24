"""
run_timeframe_test.py — Test different timeframes for donchian_breakout and smart_money strategies.

Fetches 1500 candles per timeframe from Kraken via ccxt, runs backtests, and prints
a comparison table showing optimal timeframe per strategy per symbol.
"""

import sys
import io
import time
import math
import warnings

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")

import ccxt
import pandas as pd
import numpy as np

from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.smart_money import SmartMoneyStrategy


def fetch_ohlcv(exchange, symbol: str, timeframe: str, limit: int = 1500) -> pd.DataFrame:
    """Fetch OHLCV data from Kraken and return a DataFrame with DatetimeIndex."""
    all_candles = []
    since = None
    batch = min(limit, 720)  # Kraken max per request

    while len(all_candles) < limit:
        remaining = limit - len(all_candles)
        fetch_count = min(batch, remaining)
        try:
            candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=fetch_count)
        except Exception as e:
            print(f"  [WARN] Fetch error for {symbol} {timeframe}: {e}")
            break

        if not candles:
            break

        all_candles.extend(candles)
        since = candles[-1][0] + 1  # next ms after last candle
        time.sleep(exchange.rateLimit / 1000 + 0.1)

        # Deduplicate by timestamp
        seen = set()
        unique = []
        for c in all_candles:
            if c[0] not in seen:
                seen.add(c[0])
                unique.append(c)
        all_candles = unique

        if len(candles) < fetch_count:
            break  # No more data available

    df = pd.DataFrame(all_candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    df.attrs["symbol"] = symbol
    return df


def compute_metrics(result):
    """Extract key metrics from a BacktestResult."""
    trades = result.trades
    total = len(trades)
    if total == 0:
        return {
            "trades": 0,
            "net_pnl": 0.0,
            "win_rate": 0.0,
            "sharpe": 0.0,
            "profit_factor": 0.0,
        }

    net_pnl = sum(t.net_pnl for t in trades)
    winners = [t for t in trades if t.net_pnl > 0]
    losers = [t for t in trades if t.net_pnl <= 0]
    win_rate = len(winners) / total * 100.0

    gross_profit = sum(t.net_pnl for t in winners)
    gross_loss = abs(sum(t.net_pnl for t in losers))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0.0)

    return {
        "trades": total,
        "net_pnl": net_pnl,
        "win_rate": win_rate,
        "sharpe": result.sharpe_ratio,
        "profit_factor": profit_factor,
    }


def main():
    print("=" * 80)
    print("  ATLAS Timeframe Optimization Test")
    print("  donchian_breakout + smart_money | 1h, 4h, 1d | Kraken data")
    print("=" * 80)
    print()

    exchange = ccxt.kraken({"enableRateLimit": True})
    exchange.load_markets()

    timeframes = ["1h", "4h", "1d"]

    strategies_config = {
        "donchian_breakout": {
            "strategy": DonchianBreakoutStrategy(),
            "symbols": ["ATOM/USDT", "ETH/USDT", "AVAX/USDT"],
        },
        "smart_money": {
            "strategy": SmartMoneyStrategy(),
            "symbols": ["ETH/USDT", "DOGE/USDT", "AVAX/USDT"],
        },
    }

    engine = BacktestEngine(initial_capital=10000, regime_filter=True)

    # Store all results: {(strategy_name, symbol, timeframe): metrics_dict}
    all_results = {}

    for strat_name, config in strategies_config.items():
        strategy = config["strategy"]
        symbols = config["symbols"]

        print(f"\n{'='*70}")
        print(f"  Strategy: {strat_name.upper()}")
        print(f"{'='*70}")

        for symbol in symbols:
            print(f"\n  --- {symbol} ---")
            for tf in timeframes:
                print(f"    Fetching {symbol} {tf} (1500 candles)...", end=" ", flush=True)
                try:
                    df = fetch_ohlcv(exchange, symbol, tf, limit=1500)
                except Exception as e:
                    print(f"FAILED: {e}")
                    all_results[(strat_name, symbol, tf)] = {
                        "trades": 0, "net_pnl": 0.0, "win_rate": 0.0,
                        "sharpe": 0.0, "profit_factor": 0.0, "error": str(e),
                    }
                    continue

                print(f"got {len(df)} bars.", end=" ", flush=True)

                if len(df) < 250:
                    print("SKIP (too few bars)")
                    all_results[(strat_name, symbol, tf)] = {
                        "trades": 0, "net_pnl": 0.0, "win_rate": 0.0,
                        "sharpe": 0.0, "profit_factor": 0.0, "error": "too few bars",
                    }
                    continue

                # Re-instantiate strategy to reset any state
                if strat_name == "donchian_breakout":
                    strat_instance = DonchianBreakoutStrategy()
                else:
                    strat_instance = SmartMoneyStrategy()

                try:
                    result = engine.run(df, strat_instance)
                    metrics = compute_metrics(result)
                    all_results[(strat_name, symbol, tf)] = metrics
                    pf_str = f"{metrics['profit_factor']:.2f}" if not math.isinf(metrics['profit_factor']) else "inf"
                    print(
                        f"Trades: {metrics['trades']:>3} | "
                        f"P&L: ${metrics['net_pnl']:>+10.2f} | "
                        f"WR: {metrics['win_rate']:>5.1f}% | "
                        f"Sharpe: {metrics['sharpe']:>+6.3f} | "
                        f"PF: {pf_str}"
                    )
                except Exception as e:
                    print(f"BACKTEST FAILED: {e}")
                    all_results[(strat_name, symbol, tf)] = {
                        "trades": 0, "net_pnl": 0.0, "win_rate": 0.0,
                        "sharpe": 0.0, "profit_factor": 0.0, "error": str(e),
                    }

    # =========================================================================
    # Print comparison tables
    # =========================================================================
    print("\n\n")
    print("=" * 90)
    print("  COMPARISON TABLE — All Results")
    print("=" * 90)

    header = f"{'Strategy':<20} {'Symbol':<12} {'TF':<5} {'Trades':>7} {'Net P&L':>12} {'WR%':>7} {'Sharpe':>8} {'PF':>8}"
    print(header)
    print("-" * 90)

    for strat_name, config in strategies_config.items():
        for symbol in config["symbols"]:
            for tf in timeframes:
                key = (strat_name, symbol, tf)
                m = all_results.get(key, {})
                if "error" in m:
                    print(f"{strat_name:<20} {symbol:<12} {tf:<5} {'ERROR':>7}   {m.get('error','')}")
                    continue
                pf_str = f"{m['profit_factor']:.2f}" if not math.isinf(m.get('profit_factor', 0)) else "inf"
                print(
                    f"{strat_name:<20} {symbol:<12} {tf:<5} "
                    f"{m['trades']:>7} "
                    f"${m['net_pnl']:>+11.2f} "
                    f"{m['win_rate']:>6.1f}% "
                    f"{m['sharpe']:>+8.3f} "
                    f"{pf_str:>8}"
                )
        print()

    # =========================================================================
    # Optimal timeframe per strategy-symbol
    # =========================================================================
    print("\n")
    print("=" * 70)
    print("  OPTIMAL TIMEFRAME PER STRATEGY-SYMBOL (by Net P&L)")
    print("=" * 70)
    print(f"{'Strategy':<20} {'Symbol':<12} {'Best TF':<8} {'Net P&L':>12} {'Sharpe':>8} {'Trades':>7}")
    print("-" * 70)

    for strat_name, config in strategies_config.items():
        for symbol in config["symbols"]:
            best_tf = None
            best_pnl = -float("inf")
            best_m = None
            for tf in timeframes:
                key = (strat_name, symbol, tf)
                m = all_results.get(key, {})
                if "error" in m:
                    continue
                if m.get("net_pnl", -float("inf")) > best_pnl:
                    best_pnl = m["net_pnl"]
                    best_tf = tf
                    best_m = m
            if best_m and best_tf:
                print(
                    f"{strat_name:<20} {symbol:<12} {best_tf:<8} "
                    f"${best_m['net_pnl']:>+11.2f} "
                    f"{best_m['sharpe']:>+8.3f} "
                    f"{best_m['trades']:>7}"
                )
            else:
                print(f"{strat_name:<20} {symbol:<12} {'N/A':<8} {'No valid results'}")

    # =========================================================================
    # Optimal timeframe by Sharpe
    # =========================================================================
    print("\n")
    print("=" * 70)
    print("  OPTIMAL TIMEFRAME PER STRATEGY-SYMBOL (by Sharpe Ratio)")
    print("=" * 70)
    print(f"{'Strategy':<20} {'Symbol':<12} {'Best TF':<8} {'Sharpe':>8} {'Net P&L':>12} {'Trades':>7}")
    print("-" * 70)

    for strat_name, config in strategies_config.items():
        for symbol in config["symbols"]:
            best_tf = None
            best_sharpe = -float("inf")
            best_m = None
            for tf in timeframes:
                key = (strat_name, symbol, tf)
                m = all_results.get(key, {})
                if "error" in m:
                    continue
                if m.get("trades", 0) == 0:
                    continue
                if m.get("sharpe", -float("inf")) > best_sharpe:
                    best_sharpe = m["sharpe"]
                    best_tf = tf
                    best_m = m
            if best_m and best_tf:
                print(
                    f"{strat_name:<20} {symbol:<12} {best_tf:<8} "
                    f"{best_m['sharpe']:>+8.3f} "
                    f"${best_m['net_pnl']:>+11.2f} "
                    f"{best_m['trades']:>7}"
                )
            else:
                print(f"{strat_name:<20} {symbol:<12} {'N/A':<8} {'No trades generated'}")

    print("\n" + "=" * 70)
    print("  Test complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
