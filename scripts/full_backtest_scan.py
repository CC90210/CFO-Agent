"""
full_backtest_scan.py — Comprehensive backtest of ALL strategies on fresh market data.

Fetches live OHLCV from Kraken (crypto) and OANDA (gold/forex), runs each
strategy-symbol pair through the backtest engine, and ranks by Sharpe ratio.

Usage:
    python scripts/full_backtest_scan.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
import traceback
from datetime import datetime, timezone

import ccxt.async_support as ccxt
import pandas as pd
import yaml

from backtesting.engine import BacktestEngine
from strategies import StrategyRegistry

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("backtest_scan")

# ── Config ────────────────────────────────────────────────────────────────────
INITIAL_CAPITAL = 136.0  # Current Kraken balance
COMMISSION = 0.001       # 0.1% per side
BARS = 500               # Number of candles to fetch

# Map strategy names → timeframes for data fetching
TIMEFRAME_MAP = {
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "15m": "15m",
    "5m": "5m",
}


async def fetch_kraken_data(symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
    """Fetch OHLCV data from Kraken."""
    exchange = ccxt.kraken({"enableRateLimit": True})
    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        return df
    finally:
        await exchange.close()


def load_strategies_config():
    """Load strategies.yaml and return enabled + interesting disabled strategies."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "config", "strategies.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config.get("strategies", {})


async def run_backtest_pair(strategy_name: str, symbol: str, timeframe: str,
                            params: dict) -> dict | None:
    """Run a single strategy-symbol backtest and return results dict."""
    try:
        # Build strategy with params
        strategy = StrategyRegistry.build(strategy_name, **params)

        # Fetch data
        df = await fetch_kraken_data(symbol, timeframe, BARS)
        if df is None or len(df) < 100:
            return None

        # Run backtest
        engine = BacktestEngine(
            initial_capital=INITIAL_CAPITAL,
            commission_pct=COMMISSION,
            risk_per_trade_pct=0.08,  # Micro account: 8% risk as decimal fraction
        )
        result = engine.run(df, strategy)

        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "return_pct": result.total_return * 100,
            "sharpe": result.sharpe_ratio,
            "win_rate": result.win_rate * 100,
            "trades": result.total_trades,
            "profit_factor": result.profit_factor,
            "max_dd_pct": result.max_drawdown * 100,
            "expectancy": result.expectancy,
            "final_equity": result.final_equity,
        }
    except Exception as e:
        logger.warning("FAIL %s/%s: %s", strategy_name, symbol, e)
        traceback.print_exc()
        return None


async def main():
    config = load_strategies_config()

    # Strategies to test — ALL enabled + promising disabled ones
    test_pairs = []

    # Crypto symbols available on Kraken
    KRAKEN_SYMBOLS = [
        "BTC/USD", "ETH/USD", "SOL/USD", "LTC/USD", "ADA/USD",
        "DOGE/USD", "XRP/USD", "ATOM/USD", "DOT/USD", "LINK/USD",
        "AVAX/USD", "NEAR/USD",
    ]

    # Currently ENABLED strategies — test their configured symbols
    enabled_crypto = {
        "rsi_mean_reversion": {"tf": "4h"},
        "bollinger_squeeze": {"tf": "1h"},
        "multi_timeframe": {"tf": "4h"},
        "donchian_breakout": {"tf": "4h"},
    }

    for strat_name, meta in enabled_crypto.items():
        strat_config = config.get(strat_name, {})
        params = strat_config.get("parameters", {})
        symbols = strat_config.get("symbols", [])
        # Only test Kraken-available crypto symbols
        for sym in symbols:
            if sym in KRAKEN_SYMBOLS:
                test_pairs.append((strat_name, sym, meta["tf"], params))

    # Also test DISABLED strategies that showed promise — broad scan for alpha
    disabled_to_test = {
        "tsmom": {"tf": "1d", "symbols": ["BTC/USD", "ETH/USD", "SOL/USD", "DOGE/USD"]},
        "volume_profile": {"tf": "4h", "symbols": ["BTC/USD", "ETH/USD", "AVAX/USD", "XRP/USD"]},
        "ema_crossover": {"tf": "4h", "symbols": ["BTC/USD", "ETH/USD"]},
        "ichimoku_trend": {"tf": "4h", "symbols": ["BTC/USD", "ETH/USD"]},
        "zscore_mean_reversion": {"tf": "1h", "symbols": ["ETH/USD", "BTC/USD"]},
        "bb_mean_reversion": {"tf": "1h", "symbols": ["BTC/USD", "DOGE/USD", "ADA/USD"]},
        "smart_money": {"tf": "4h", "symbols": ["XRP/USD", "ETH/USD"]},
        "momentum_exhaustion": {"tf": "1h", "symbols": ["BTC/USD", "ETH/USD", "DOGE/USD"]},
    }

    for strat_name, meta in disabled_to_test.items():
        strat_config = config.get(strat_name, {})
        params = strat_config.get("parameters", {})
        for sym in meta["symbols"]:
            test_pairs.append((strat_name, sym, meta["tf"], params))

    # Also do EXPANDED symbol scan on top enabled strategies
    # Test RSI and Donchian on ALL Kraken symbols to find new alpha
    for strat_name in ["rsi_mean_reversion", "donchian_breakout"]:
        strat_config = config.get(strat_name, {})
        params = strat_config.get("parameters", {})
        tf = "4h"
        configured = set(strat_config.get("symbols", []))
        for sym in KRAKEN_SYMBOLS:
            if sym not in configured:
                test_pairs.append((strat_name, sym, tf, params))

    print(f"\n{'='*80}")
    print(f"  ATLAS COMPREHENSIVE BACKTEST SCAN")
    print(f"  Capital: ${INITIAL_CAPITAL:.2f} | Bars: {BARS} | Commission: {COMMISSION*100:.1f}%")
    print(f"  Total pairs to test: {len(test_pairs)}")
    print(f"{'='*80}\n")

    # Run all backtests — batch to avoid rate limits
    results = []
    batch_size = 3
    for i in range(0, len(test_pairs), batch_size):
        batch = test_pairs[i:i+batch_size]
        tasks = [run_backtest_pair(s, sym, tf, p) for s, sym, tf, p in batch]
        batch_results = await asyncio.gather(*tasks)
        for r in batch_results:
            if r is not None:
                results.append(r)
        done = min(i + batch_size, len(test_pairs))
        print(f"  Progress: {done}/{len(test_pairs)} pairs tested...")

    # Sort by Sharpe ratio
    results.sort(key=lambda x: x["sharpe"], reverse=True)

    # Print results table
    print(f"\n{'='*110}")
    print(f"  RESULTS — Ranked by Sharpe Ratio")
    print(f"{'='*110}")
    print(f"{'Strategy':<25} {'Symbol':<12} {'Return%':>8} {'Sharpe':>7} {'WR%':>6} {'Trades':>7} {'PF':>6} {'MaxDD%':>8} {'Expect$':>8}")
    print(f"{'-'*110}")

    profitable = 0
    for r in results:
        flag = "***" if r["sharpe"] > 1.0 else "  *" if r["sharpe"] > 0.5 else "   "
        if r["return_pct"] > 0:
            profitable += 1
        print(f"{flag} {r['strategy']:<22} {r['symbol']:<12} {r['return_pct']:>+7.2f}% "
              f"{r['sharpe']:>7.2f} {r['win_rate']:>5.1f}% {r['trades']:>6} "
              f"{r['profit_factor']:>6.2f} {r['max_dd_pct']:>+7.2f}% ${r['expectancy']:>7.2f}")

    print(f"\n{'='*110}")
    print(f"  SUMMARY: {profitable}/{len(results)} pairs profitable | "
          f"Top Sharpe: {results[0]['sharpe']:.2f} ({results[0]['strategy']}/{results[0]['symbol']})" if results else "No results")

    # Print TOP 10 recommendations
    top = [r for r in results if r["sharpe"] > 0.3 and r["trades"] >= 3]
    if top:
        print(f"\n  TOP RECOMMENDATIONS (Sharpe > 0.3, trades >= 3):")
        for i, r in enumerate(top[:15], 1):
            print(f"    {i}. {r['strategy']}/{r['symbol']} — "
                  f"Return: {r['return_pct']:+.2f}%, Sharpe: {r['sharpe']:.2f}, "
                  f"WR: {r['win_rate']:.0f}%, PF: {r['profit_factor']:.2f}")

    # Print WORST — what to disable
    worst = [r for r in results if r["return_pct"] < -3.0]
    if worst:
        print(f"\n  DISABLE THESE (Return < -3%):")
        for r in sorted(worst, key=lambda x: x["return_pct"]):
            print(f"    X {r['strategy']}/{r['symbol']} — "
                  f"Return: {r['return_pct']:+.2f}%, Sharpe: {r['sharpe']:.2f}")

    print(f"\n{'='*110}")


if __name__ == "__main__":
    asyncio.run(main())
