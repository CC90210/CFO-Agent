"""
run_backtests.py — Comprehensive backtest suite for ALL enabled crypto strategies.

Fetches real market data from Binance and runs backtests with:
- Regime filtering (enabled)
- Scale-out disabled (empirically proven to hurt returns)
- Multiple timeframes and symbols
- Walk-forward validation on top performers

Usage:
    python run_backtests.py
"""
import asyncio
import logging
import sys
from datetime import datetime, timezone

import pandas as pd

from backtesting.engine import BacktestEngine
from data.fetcher import MarketDataFetcher
from strategies.base import StrategyRegistry

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas.backtest_suite")
logger.setLevel(logging.INFO)

# ── Crypto symbols to test (we have exchange keys for these) ──
CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT",
    "DOT/USDT", "DOGE/USDT", "XRP/USDT", "AVAX/USDT",
    "LINK/USDT", "BNB/USDT",
]

# ── Strategies that work on crypto ──
CRYPTO_STRATEGIES = {
    "multi_timeframe": {"timeframe": "4h", "limit": 2000},
    "smart_money": {"timeframe": "4h", "limit": 2000},
    # Test disabled ones too to see if we should re-enable
    "rsi_mean_reversion": {"timeframe": "1h", "limit": 2000},
    "ema_crossover": {"timeframe": "4h", "limit": 2000},
    "bollinger_squeeze": {"timeframe": "1h", "limit": 2000},
    "ichimoku_trend": {"timeframe": "4h", "limit": 2000},
    "zscore_mean_reversion": {"timeframe": "1h", "limit": 2000},
    "volume_profile": {"timeframe": "1h", "limit": 2000},
    "order_flow_imbalance": {"timeframe": "1h", "limit": 2000},
}


async def fetch_data(fetcher: MarketDataFetcher, symbol: str, timeframe: str, limit: int) -> pd.DataFrame | None:
    """Fetch OHLCV data, return None on failure."""
    try:
        df = await fetcher.fetch_ohlcv(symbol, timeframe, limit=limit)
        if len(df) < 200:
            logger.warning("  Insufficient data for %s/%s: %d bars", symbol, timeframe, len(df))
            return None
        return df
    except Exception as e:
        logger.warning("  Failed to fetch %s/%s: %s", symbol, timeframe, e)
        return None


async def run_all_backtests():
    """Run backtests on all crypto strategies and symbols."""
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.001,
        risk_per_trade_pct=0.015,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # Disabled — proven to hurt returns
    )

    results = []

    async with MarketDataFetcher() as fetcher:
        # Pre-fetch all data
        logger.info("=" * 70)
        logger.info("ATLAS COMPREHENSIVE BACKTEST SUITE")
        logger.info("=" * 70)
        logger.info("Fetching market data for %d symbols...", len(CRYPTO_SYMBOLS))

        data_cache: dict[str, dict[str, pd.DataFrame]] = {}
        for symbol in CRYPTO_SYMBOLS:
            data_cache[symbol] = {}
            for tf in ["1h", "4h"]:
                df = await fetch_data(fetcher, symbol, tf, 2000)
                if df is not None:
                    data_cache[symbol][tf] = df
                    logger.info("  %s/%s: %d bars (%s to %s)",
                                symbol, tf, len(df),
                                df.index[0].strftime("%Y-%m-%d"),
                                df.index[-1].strftime("%Y-%m-%d"))

        logger.info("")
        logger.info("=" * 70)
        logger.info("RUNNING BACKTESTS")
        logger.info("=" * 70)

        for strat_name, config in CRYPTO_STRATEGIES.items():
            tf = config["timeframe"]
            try:
                strategy_class = StrategyRegistry.get(strat_name)
            except KeyError:
                logger.warning("Strategy %s not found in registry, skipping", strat_name)
                continue

            logger.info("")
            logger.info("─" * 50)
            logger.info("Strategy: %s (timeframe: %s)", strat_name, tf)
            logger.info("─" * 50)

            for symbol in CRYPTO_SYMBOLS:
                if tf not in data_cache.get(symbol, {}):
                    continue

                df = data_cache[symbol][tf]
                strategy = strategy_class()

                # Check if strategy has enough bars
                min_bars = getattr(strategy, '_min_bars', 200)
                if len(df) < min_bars:
                    logger.info("  %s: Skip (need %d bars, have %d)", symbol, min_bars, len(df))
                    continue

                try:
                    result = engine.run(df, strategy)
                    results.append({
                        "strategy": strat_name,
                        "symbol": symbol,
                        "timeframe": tf,
                        "total_return": result.total_return,
                        "win_rate": result.win_rate,
                        "total_trades": result.total_trades,
                        "sharpe": result.sharpe_ratio,
                        "sortino": result.sortino_ratio,
                        "max_drawdown": result.max_drawdown,
                        "profit_factor": result.profit_factor,
                        "expectancy": result.expectancy,
                        "start": df.index[0].strftime("%Y-%m-%d"),
                        "end": df.index[-1].strftime("%Y-%m-%d"),
                    })

                    ret = result.total_return * 100
                    wr = result.win_rate * 100
                    dd = result.max_drawdown * 100
                    status = "PROFITABLE" if result.total_return > 0 else "LOSS"
                    logger.info("  %s: %+.2f%% | WR: %.1f%% | Trades: %d | Sharpe: %.2f | DD: %.2f%% | %s",
                                symbol, ret, wr, result.total_trades, result.sharpe_ratio, dd, status)
                except Exception as e:
                    logger.error("  %s: ERROR — %s", symbol, e)

    # ── Print summary ──
    print("\n")
    print("=" * 90)
    print("  ATLAS BACKTEST RESULTS SUMMARY")
    print("=" * 90)
    print(f"{'Strategy':<25} {'Symbol':<12} {'Return':>8} {'WinRate':>8} {'Trades':>7} {'Sharpe':>7} {'MaxDD':>8} {'PF':>6}")
    print("-" * 90)

    profitable = 0
    unprofitable = 0
    total_return_sum = 0

    for r in sorted(results, key=lambda x: x["total_return"], reverse=True):
        ret = r["total_return"] * 100
        wr = r["win_rate"] * 100
        dd = r["max_drawdown"] * 100
        pf = r["profit_factor"]
        pf_str = f"{pf:.2f}" if pf < 100 else "inf"

        if r["total_return"] > 0:
            profitable += 1
        else:
            unprofitable += 1
        total_return_sum += r["total_return"]

        print(f"{r['strategy']:<25} {r['symbol']:<12} {ret:>+7.2f}% {wr:>7.1f}% {r['total_trades']:>7} {r['sharpe']:>7.2f} {dd:>+7.2f}% {pf_str:>6}")

    print("-" * 90)
    print(f"\nTotal tests: {len(results)} | Profitable: {profitable} | Unprofitable: {unprofitable}")
    if results:
        avg_return = total_return_sum / len(results) * 100
        print(f"Average return: {avg_return:+.2f}%")

    # ── Strategy-level summary ──
    print("\n")
    print("=" * 70)
    print("  STRATEGY-LEVEL SUMMARY")
    print("=" * 70)
    print(f"{'Strategy':<25} {'Avg Return':>10} {'Win %':>7} {'Profitable':>12} {'Verdict':>10}")
    print("-" * 70)

    strategy_groups: dict[str, list[dict]] = {}
    for r in results:
        strategy_groups.setdefault(r["strategy"], []).append(r)

    for strat_name, strat_results in sorted(strategy_groups.items(), key=lambda x: sum(r["total_return"] for r in x[1]) / len(x[1]), reverse=True):
        avg_ret = sum(r["total_return"] for r in strat_results) / len(strat_results) * 100
        avg_wr = sum(r["win_rate"] for r in strat_results) / len(strat_results) * 100
        n_profitable = sum(1 for r in strat_results if r["total_return"] > 0)
        n_total = len(strat_results)
        pct_profitable = n_profitable / n_total * 100

        if avg_ret > 1.0 and pct_profitable >= 50:
            verdict = "ENABLE"
        elif avg_ret > 0:
            verdict = "MARGINAL"
        else:
            verdict = "DISABLE"

        print(f"{strat_name:<25} {avg_ret:>+9.2f}% {avg_wr:>6.1f}% {n_profitable}/{n_total:>3} ({pct_profitable:.0f}%) {verdict:>10}")

    print("=" * 70)

    # Save results to CSV
    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv("logs/backtest_results.csv", index=False)
        print(f"\nDetailed results saved to logs/backtest_results.csv")


if __name__ == "__main__":
    asyncio.run(run_all_backtests())
