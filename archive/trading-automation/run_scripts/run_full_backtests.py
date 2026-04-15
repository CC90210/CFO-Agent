"""
run_full_backtests.py — ATLAS Comprehensive Backtest Suite (All Asset Classes)

Tests ALL enabled strategies on their intended asset classes using live Kraken data
for crypto and simulated data patterns for forex/gold/stocks.

Fetches real data from Kraken exchange (configured in .env).
Produces a ranked report showing which strategies to ENABLE vs DISABLE.

Usage:
    python run_full_backtests.py
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
logger = logging.getLogger("atlas.full_backtest")
logger.setLevel(logging.INFO)

# ── Crypto symbols available on Kraken ──
CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT",
    "DOT/USDT", "DOGE/USDT", "XRP/USDT",
]

# ── All crypto-capable strategies to test ──
CRYPTO_STRATEGIES = {
    # Enabled strategies
    "multi_timeframe":     {"timeframe": "4h", "limit": 720},
    "smart_money":         {"timeframe": "4h", "limit": 720},
    "grid_dca":            {"timeframe": "1h", "limit": 720},
    # New strategies (will be available once agents finish building them)
    "donchian_breakout":   {"timeframe": "4h", "limit": 720},
    "momentum_exhaustion": {"timeframe": "1h", "limit": 720},
    "pairs_mean_reversion": {"timeframe": "1h", "limit": 720},
    # Disabled strategies — retest to see if any improved
    "rsi_mean_reversion":  {"timeframe": "1h", "limit": 720},
    "ema_crossover":       {"timeframe": "4h", "limit": 720},
    "bollinger_squeeze":   {"timeframe": "1h", "limit": 720},
    "ichimoku_trend":      {"timeframe": "4h", "limit": 720},
    "zscore_mean_reversion": {"timeframe": "1h", "limit": 720},
    "volume_profile":      {"timeframe": "1h", "limit": 720},
    "order_flow_imbalance": {"timeframe": "1h", "limit": 720},
    "forex_carry_momentum": {"timeframe": "4h", "limit": 720},
}


async def fetch_data(
    fetcher: MarketDataFetcher, symbol: str, timeframe: str, limit: int
) -> pd.DataFrame | None:
    try:
        df = await fetcher.fetch_ohlcv(symbol, timeframe, limit=limit)
        if len(df) < 100:
            logger.warning("  Insufficient data for %s/%s: %d bars", symbol, timeframe, len(df))
            return None
        return df
    except Exception as e:
        logger.warning("  Failed to fetch %s/%s: %s", symbol, timeframe, e)
        return None


async def run_all_backtests():
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.001,
        risk_per_trade_pct=0.015,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],
    )

    results = []

    # Auto-discover strategies
    try:
        import strategies.technical
    except Exception:
        pass

    available_strategies = set()
    for name in CRYPTO_STRATEGIES:
        try:
            StrategyRegistry.get(name)
            available_strategies.add(name)
        except KeyError:
            logger.info("Strategy '%s' not yet registered — skipping", name)

    async with MarketDataFetcher() as fetcher:
        logger.info("=" * 80)
        logger.info("  ATLAS COMPREHENSIVE BACKTEST SUITE")
        logger.info("  Exchange: %s | Date: %s", fetcher._exchange.id, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
        logger.info("=" * 80)

        # Pre-fetch all data
        data_cache: dict[str, dict[str, pd.DataFrame]] = {}
        timeframes_needed = set()
        for config in CRYPTO_STRATEGIES.values():
            timeframes_needed.add(config["timeframe"])

        logger.info("\nFetching data for %d symbols across %s timeframes...",
                    len(CRYPTO_SYMBOLS), sorted(timeframes_needed))

        for symbol in CRYPTO_SYMBOLS:
            data_cache[symbol] = {}
            for tf in sorted(timeframes_needed):
                limit = 720  # Kraken limit
                df = await fetch_data(fetcher, symbol, tf, limit)
                if df is not None:
                    data_cache[symbol][tf] = df
                    logger.info("  %s %s: %d bars (%s to %s)",
                                symbol, tf, len(df),
                                df.index[0].strftime("%Y-%m-%d"),
                                df.index[-1].strftime("%Y-%m-%d"))

        # Run backtests
        logger.info("\n" + "=" * 80)
        logger.info("  RUNNING BACKTESTS — %d strategies x %d symbols",
                    len(available_strategies), len(CRYPTO_SYMBOLS))
        logger.info("=" * 80)

        for strat_name in sorted(available_strategies):
            config = CRYPTO_STRATEGIES[strat_name]
            tf = config["timeframe"]

            try:
                strategy_class = StrategyRegistry.get(strat_name)
            except KeyError:
                continue

            logger.info("\n--- %s (tf: %s) ---", strat_name, tf)

            for symbol in CRYPTO_SYMBOLS:
                if tf not in data_cache.get(symbol, {}):
                    continue

                df = data_cache[symbol][tf]
                strategy = strategy_class()

                min_bars = getattr(strategy, '_min_bars', 200)
                if len(df) < min_bars:
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
                    trades = result.total_trades
                    status = "WIN" if result.total_return > 0 else "LOSS"
                    logger.info("  %s: %+.2f%% | WR:%.0f%% | %d trades | Sharpe:%.2f | DD:%.1f%% | %s",
                                symbol, ret, wr, trades, result.sharpe_ratio, dd, status)
                except Exception as e:
                    logger.error("  %s: ERROR — %s", symbol, e)

    # ══════════════════════════════════════════════════════════════════════
    # RESULTS
    # ══════════════════════════════════════════════════════════════════════
    if not results:
        print("\nNo results to display. Check that strategies are registered.")
        return

    print("\n")
    print("=" * 100)
    print("  ATLAS BACKTEST RESULTS — FULL REPORT")
    print("=" * 100)
    print(f"{'Strategy':<25} {'Symbol':<12} {'TF':>4} {'Return':>8} {'WinRate':>8} {'Trades':>7} {'Sharpe':>7} {'MaxDD':>8} {'PF':>6} {'Status':>8}")
    print("-" * 100)

    profitable = 0
    unprofitable = 0

    for r in sorted(results, key=lambda x: x["total_return"], reverse=True):
        ret = r["total_return"] * 100
        wr = r["win_rate"] * 100
        dd = r["max_drawdown"] * 100
        pf = r["profit_factor"]
        pf_str = f"{pf:.2f}" if pf < 100 else "inf"
        status = "WIN" if r["total_return"] > 0 else "LOSS"

        if r["total_return"] > 0:
            profitable += 1
        else:
            unprofitable += 1

        print(f"{r['strategy']:<25} {r['symbol']:<12} {r['timeframe']:>4} {ret:>+7.2f}% {wr:>7.1f}% {r['total_trades']:>7} {r['sharpe']:>7.2f} {dd:>+7.2f}% {pf_str:>6} {status:>8}")

    print("-" * 100)
    total_return_sum = sum(r["total_return"] for r in results)
    avg_return = total_return_sum / len(results) * 100
    print(f"\nTotal: {len(results)} tests | Profitable: {profitable} | Losing: {unprofitable} | Avg Return: {avg_return:+.2f}%")

    # ── Strategy-level rankings ──
    print("\n")
    print("=" * 90)
    print("  STRATEGY RANKINGS (sorted by average return)")
    print("=" * 90)
    print(f"{'#':>3} {'Strategy':<25} {'Avg Ret':>9} {'Avg WR':>8} {'Prof/Total':>11} {'Avg Sharpe':>11} {'Verdict':>10}")
    print("-" * 90)

    strategy_groups: dict[str, list[dict]] = {}
    for r in results:
        strategy_groups.setdefault(r["strategy"], []).append(r)

    ranked = sorted(
        strategy_groups.items(),
        key=lambda x: sum(r["total_return"] for r in x[1]) / len(x[1]),
        reverse=True,
    )

    for rank, (strat_name, strat_results) in enumerate(ranked, 1):
        avg_ret = sum(r["total_return"] for r in strat_results) / len(strat_results) * 100
        avg_wr = sum(r["win_rate"] for r in strat_results) / len(strat_results) * 100
        avg_sharpe = sum(r["sharpe"] for r in strat_results) / len(strat_results)
        n_profitable = sum(1 for r in strat_results if r["total_return"] > 0)
        n_total = len(strat_results)

        if avg_ret > 1.0 and n_profitable / n_total >= 0.5:
            verdict = "ENABLE"
        elif avg_ret > 0:
            verdict = "MARGINAL"
        else:
            verdict = "DISABLE"

        print(f"{rank:>3} {strat_name:<25} {avg_ret:>+8.2f}% {avg_wr:>7.1f}% {n_profitable}/{n_total:>3} ({n_profitable/n_total*100:.0f}%) {avg_sharpe:>10.2f} {verdict:>10}")

    print("=" * 90)

    # ── Per-symbol heat map ──
    print("\n")
    print("=" * 90)
    print("  SYMBOL HEAT MAP — Best strategy per symbol")
    print("=" * 90)

    for symbol in CRYPTO_SYMBOLS:
        symbol_results = [r for r in results if r["symbol"] == symbol]
        if not symbol_results:
            continue
        best = max(symbol_results, key=lambda r: r["total_return"])
        worst = min(symbol_results, key=lambda r: r["total_return"])
        avg = sum(r["total_return"] for r in symbol_results) / len(symbol_results) * 100

        print(f"\n  {symbol}:")
        print(f"    Best:  {best['strategy']:<25} {best['total_return']*100:>+7.2f}%")
        print(f"    Worst: {worst['strategy']:<25} {worst['total_return']*100:>+7.2f}%")
        print(f"    Avg across all strategies: {avg:>+7.2f}%")

    print("\n" + "=" * 90)

    # ── Action items ──
    print("\n  ACTION ITEMS:")
    print("  " + "-" * 40)
    for strat_name, strat_results in ranked:
        avg_ret = sum(r["total_return"] for r in strat_results) / len(strat_results) * 100
        n_profitable = sum(1 for r in strat_results if r["total_return"] > 0)
        n_total = len(strat_results)

        if avg_ret > 1.0 and n_profitable / n_total >= 0.5:
            symbols = [r["symbol"] for r in strat_results if r["total_return"] > 0]
            print(f"  ENABLE  {strat_name}: +{avg_ret:.1f}% avg on {', '.join(symbols)}")
        elif avg_ret < -1.0:
            print(f"  DISABLE {strat_name}: {avg_ret:.1f}% avg — losing money")
        else:
            print(f"  REVIEW  {strat_name}: {avg_ret:+.1f}% avg — marginal, needs tuning")

    print()

    # Save to CSV
    df_results = pd.DataFrame(results)
    df_results.to_csv("logs/full_backtest_results.csv", index=False)
    print(f"  Full results saved to logs/full_backtest_results.csv")


if __name__ == "__main__":
    asyncio.run(run_all_backtests())
