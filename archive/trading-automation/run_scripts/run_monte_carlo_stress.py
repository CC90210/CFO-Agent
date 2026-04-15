"""
run_monte_carlo_stress.py — Monte Carlo Stress Testing for Atlas Winning Strategies

Tests tail risk and worst-case scenarios for the 3 winning strategies:
  1. donchian_breakout
  2. rsi_mean_reversion
  3. smart_money

Process:
  - Runs backtests on configured symbols (BTC/USD, ETH/USD, SOL/USD crypto)
  - Collects all trade PnL results
  - Runs 1000 Monte Carlo simulations per strategy (resample with replacement)
  - Reports worst-case drawdowns, probability of ruin, Sharpe distributions

Starting capital: $140 (CC's real account)
Risk per trade: 1% ($1.40)

Usage:
    python run_monte_carlo_stress.py
"""

import asyncio
import logging
import math
import sys

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from backtesting.engine import BacktestEngine
from data.fetcher import MarketDataFetcher
from strategies.base import StrategyRegistry

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas.monte_carlo")
logger.setLevel(logging.INFO)

# ── Configuration ──
STARTING_CAPITAL = 140.0       # CC's real account
RISK_PER_TRADE = 0.01          # 1% per trade ($1.40)
NUM_SIMULATIONS = 1000
TIMEFRAME = "4h"
CANDLE_LIMIT = 500             # minimum 500 candles per symbol
RUIN_THRESHOLD = 0.50          # losing >50% = ruin

# ── Strategies and their crypto symbols (USD pairs — Ontario restriction) ──
STRATEGY_CONFIGS = {
    "donchian_breakout": {
        "symbols": ["BTC/USD", "ETH/USD", "SOL/USD", "ADA/USD", "XRP/USD", "DOGE/USD", "AVAX/USD", "ATOM/USD", "DOT/USD"],
    },
    "rsi_mean_reversion": {
        "symbols": ["ATOM/USD", "SOL/USD", "BTC/USD", "ETH/USD"],
    },
    "smart_money": {
        "symbols": ["ETH/USD", "XRP/USD", "SOL/USD", "DOGE/USD", "AVAX/USD", "BTC/USD"],
    },
}


def run_monte_carlo(trade_pnls: list[float], n_sims: int, starting_capital: float) -> dict:
    """
    Run Monte Carlo simulation on a pool of trade PnL values.

    For each simulation:
      - Resample len(trade_pnls) trades with replacement
      - Build equity curve starting from starting_capital
      - Track max drawdown, final equity, worst losing streak, daily-equivalent Sharpe

    Returns dict with all aggregate statistics.
    """
    if not trade_pnls:
        return {
            "n_trades": 0,
            "n_sims": 0,
            "error": "No trades to simulate",
        }

    pnls = np.array(trade_pnls, dtype=np.float64)
    n_trades = len(pnls)

    # Pre-allocate result arrays
    final_equities = np.zeros(n_sims)
    max_drawdowns = np.zeros(n_sims)
    worst_streaks = np.zeros(n_sims, dtype=int)
    sharpe_ratios = np.zeros(n_sims)

    rng = np.random.default_rng(seed=42)

    for sim in range(n_sims):
        # Resample trades with replacement
        sampled_indices = rng.integers(0, n_trades, size=n_trades)
        sampled_pnls = pnls[sampled_indices]

        # Build equity curve
        equity_curve = np.empty(n_trades + 1)
        equity_curve[0] = starting_capital
        for i, pnl in enumerate(sampled_pnls):
            equity_curve[i + 1] = equity_curve[i] + pnl

        final_equities[sim] = equity_curve[-1]

        # Max drawdown (peak-to-trough)
        running_max = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - running_max) / running_max
        max_drawdowns[sim] = np.min(drawdowns)  # most negative

        # Worst consecutive losing streak
        streak = 0
        max_streak = 0
        for pnl in sampled_pnls:
            if pnl < 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        worst_streaks[sim] = max_streak

        # Sharpe ratio (trade-level, annualized assuming ~6 trades/day on 4h bars)
        # More conservative: use trade-level returns as % of equity
        trade_returns = sampled_pnls / starting_capital  # simple approximation
        if len(trade_returns) > 1 and np.std(trade_returns, ddof=1) > 0:
            # Annualize: assume ~2 trades per week on 4h, ~104 trades/year
            trades_per_year = max(n_trades, 52)  # at least 52 for annualization
            sharpe_ratios[sim] = (np.mean(trade_returns) / np.std(trade_returns, ddof=1)) * math.sqrt(trades_per_year)
        else:
            sharpe_ratios[sim] = 0.0

    # Probability of ruin (losing >50% of starting capital)
    ruin_count = np.sum(final_equities < starting_capital * (1 - RUIN_THRESHOLD))
    prob_ruin = ruin_count / n_sims

    # Also compute probability that equity ever dips below ruin threshold (not just final)
    # This is captured by max_drawdown > RUIN_THRESHOLD
    prob_ruin_intrapath = np.sum(max_drawdowns < -RUIN_THRESHOLD) / n_sims

    return {
        "n_trades": n_trades,
        "n_sims": n_sims,
        "starting_capital": starting_capital,
        # Final equity distribution
        "final_equity_5th": float(np.percentile(final_equities, 5)),
        "final_equity_25th": float(np.percentile(final_equities, 25)),
        "final_equity_median": float(np.percentile(final_equities, 50)),
        "final_equity_75th": float(np.percentile(final_equities, 75)),
        "final_equity_95th": float(np.percentile(final_equities, 95)),
        "final_equity_mean": float(np.mean(final_equities)),
        "final_equity_min": float(np.min(final_equities)),
        "final_equity_max": float(np.max(final_equities)),
        # Max drawdown distribution
        "max_dd_5th": float(np.percentile(max_drawdowns, 5)),       # worst-case DD
        "max_dd_25th": float(np.percentile(max_drawdowns, 25)),
        "max_dd_median": float(np.percentile(max_drawdowns, 50)),
        "max_dd_75th": float(np.percentile(max_drawdowns, 75)),
        "max_dd_95th": float(np.percentile(max_drawdowns, 95)),     # best-case DD
        # Sharpe distribution
        "sharpe_5th": float(np.percentile(sharpe_ratios, 5)),
        "sharpe_median": float(np.percentile(sharpe_ratios, 50)),
        "sharpe_95th": float(np.percentile(sharpe_ratios, 95)),
        "sharpe_mean": float(np.mean(sharpe_ratios)),
        # Worst streaks
        "worst_streak_max": int(np.max(worst_streaks)),
        "worst_streak_95th": int(np.percentile(worst_streaks, 95)),
        "worst_streak_median": int(np.percentile(worst_streaks, 50)),
        # Ruin probability
        "prob_ruin_final": float(prob_ruin),
        "prob_ruin_intrapath": float(prob_ruin_intrapath),
        # Raw trade stats
        "avg_trade_pnl": float(np.mean(pnls)),
        "median_trade_pnl": float(np.median(pnls)),
        "best_trade": float(np.max(pnls)),
        "worst_trade": float(np.min(pnls)),
        "win_rate": float(np.sum(pnls > 0) / len(pnls)),
        "profit_factor": float(np.sum(pnls[pnls > 0]) / abs(np.sum(pnls[pnls < 0]))) if np.sum(pnls[pnls < 0]) != 0 else float("inf"),
    }


def print_strategy_report(strategy_name: str, mc_results: dict, trade_details: list[dict]) -> None:
    """Print formatted Monte Carlo report for a single strategy."""
    print()
    print("=" * 70)
    print(f"  MONTE CARLO STRESS TEST — {strategy_name.upper()}")
    print("=" * 70)

    if "error" in mc_results:
        print(f"  ERROR: {mc_results['error']}")
        return

    r = mc_results
    cap = r["starting_capital"]

    print(f"  Starting Capital: ${cap:.2f}")
    print(f"  Trades Collected: {r['n_trades']}")
    print(f"  Simulations:      {r['n_sims']}")
    print()

    # Trade pool stats
    print("  -- TRADE POOL STATISTICS --")
    print(f"    Win Rate:          {r['win_rate'] * 100:.1f}%")
    print(f"    Avg Trade PnL:     ${r['avg_trade_pnl']:.4f}")
    print(f"    Median Trade PnL:  ${r['median_trade_pnl']:.4f}")
    print(f"    Best Trade:        ${r['best_trade']:.4f}")
    print(f"    Worst Trade:       ${r['worst_trade']:.4f}")
    print(f"    Profit Factor:     {r['profit_factor']:.3f}")
    print()

    # Final equity distribution
    print("  -- FINAL EQUITY DISTRIBUTION --")
    print(f"    Worst case (min):  ${r['final_equity_min']:.2f}  ({(r['final_equity_min'] / cap - 1) * 100:+.1f}%)")
    print(f"    5th percentile:    ${r['final_equity_5th']:.2f}  ({(r['final_equity_5th'] / cap - 1) * 100:+.1f}%)")
    print(f"    25th percentile:   ${r['final_equity_25th']:.2f}  ({(r['final_equity_25th'] / cap - 1) * 100:+.1f}%)")
    print(f"    MEDIAN:            ${r['final_equity_median']:.2f}  ({(r['final_equity_median'] / cap - 1) * 100:+.1f}%)")
    print(f"    75th percentile:   ${r['final_equity_75th']:.2f}  ({(r['final_equity_75th'] / cap - 1) * 100:+.1f}%)")
    print(f"    95th percentile:   ${r['final_equity_95th']:.2f}  ({(r['final_equity_95th'] / cap - 1) * 100:+.1f}%)")
    print(f"    Best case (max):   ${r['final_equity_max']:.2f}  ({(r['final_equity_max'] / cap - 1) * 100:+.1f}%)")
    print()

    # Drawdown distribution
    print("  -- MAX DRAWDOWN DISTRIBUTION --")
    print(f"    5th pctile (WORST): {r['max_dd_5th'] * 100:.2f}%")
    print(f"    25th percentile:    {r['max_dd_25th'] * 100:.2f}%")
    print(f"    MEDIAN:             {r['max_dd_median'] * 100:.2f}%")
    print(f"    75th percentile:    {r['max_dd_75th'] * 100:.2f}%")
    print(f"    95th pctile (BEST): {r['max_dd_95th'] * 100:.2f}%")
    print()

    # Sharpe ratio distribution
    print("  -- SHARPE RATIO DISTRIBUTION --")
    print(f"    5th percentile:     {r['sharpe_5th']:.3f}")
    print(f"    MEDIAN:             {r['sharpe_median']:.3f}")
    print(f"    95th percentile:    {r['sharpe_95th']:.3f}")
    print(f"    Mean:               {r['sharpe_mean']:.3f}")
    print()

    # Losing streaks
    print("  -- WORST LOSING STREAKS --")
    print(f"    Median worst streak:  {r['worst_streak_median']} consecutive losses")
    print(f"    95th pctile streak:   {r['worst_streak_95th']} consecutive losses")
    print(f"    Absolute worst:       {r['worst_streak_max']} consecutive losses")
    print()

    # Ruin probability
    print("  -- PROBABILITY OF RUIN (losing >50% of capital) --")
    print(f"    By final equity:    {r['prob_ruin_final'] * 100:.2f}%")
    print(f"    Intra-path (ever):  {r['prob_ruin_intrapath'] * 100:.2f}%")
    print()

    # Risk assessment
    print("  -- RISK ASSESSMENT --")
    if r['prob_ruin_intrapath'] < 0.01:
        print("    RUIN RISK:    VERY LOW (<1%) — Capital preservation strong")
    elif r['prob_ruin_intrapath'] < 0.05:
        print("    RUIN RISK:    LOW (1-5%) — Acceptable for live trading")
    elif r['prob_ruin_intrapath'] < 0.15:
        print("    RUIN RISK:    MODERATE (5-15%) — Consider reducing position size")
    else:
        print(f"    RUIN RISK:    HIGH ({r['prob_ruin_intrapath'] * 100:.1f}%) — DO NOT TRADE LIVE")

    if r['max_dd_5th'] < -0.30:
        print(f"    TAIL DD RISK: SEVERE (5th pctile DD = {r['max_dd_5th'] * 100:.1f}%) — Exceeds 15% kill switch")
    elif r['max_dd_5th'] < -0.15:
        print(f"    TAIL DD RISK: WARNING (5th pctile DD = {r['max_dd_5th'] * 100:.1f}%) — Approaches 15% kill switch")
    else:
        print(f"    TAIL DD RISK: SAFE (5th pctile DD = {r['max_dd_5th'] * 100:.1f}%) — Within risk limits")

    if r['sharpe_5th'] > 0.5:
        print(f"    SHARPE FLOOR: GOOD (5th pctile = {r['sharpe_5th']:.2f}) — Positive even in bad scenarios")
    elif r['sharpe_5th'] > 0:
        print(f"    SHARPE FLOOR: OK (5th pctile = {r['sharpe_5th']:.2f}) — Marginally positive")
    else:
        print(f"    SHARPE FLOOR: WEAK (5th pctile = {r['sharpe_5th']:.2f}) — Negative in worst scenarios")

    print("=" * 70)

    # Print per-symbol trade breakdown
    if trade_details:
        print()
        print(f"  Per-symbol trade breakdown for {strategy_name}:")
        print(f"    {'Symbol':<12} {'Trades':>7} {'Win%':>6} {'Avg PnL':>10} {'Total PnL':>10}")
        print(f"    {'-'*47}")
        symbol_groups: dict[str, list[float]] = {}
        for td in trade_details:
            symbol_groups.setdefault(td["symbol"], []).append(td["pnl"])
        for sym, pnls_list in sorted(symbol_groups.items()):
            n = len(pnls_list)
            wins = sum(1 for p in pnls_list if p > 0)
            wr = wins / n * 100 if n > 0 else 0
            avg = sum(pnls_list) / n
            total = sum(pnls_list)
            print(f"    {sym:<12} {n:>7} {wr:>5.1f}% ${avg:>9.4f} ${total:>9.4f}")


async def main():
    """Run Monte Carlo stress test on 3 winning strategies."""
    # Force-discover all strategies
    StrategyRegistry.discover()
    logger.info("Registered strategies: %s", StrategyRegistry.list())

    engine = BacktestEngine(
        initial_capital=STARTING_CAPITAL,
        commission_pct=0.001,
        risk_per_trade_pct=RISK_PER_TRADE,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],
    )

    all_mc_results: dict[str, dict] = {}
    all_trade_details: dict[str, list[dict]] = {}

    print()
    print("=" * 70)
    print("  ATLAS MONTE CARLO STRESS TEST")
    print(f"  Starting Capital: ${STARTING_CAPITAL:.2f}")
    print(f"  Risk Per Trade: {RISK_PER_TRADE * 100:.1f}%")
    print(f"  Simulations: {NUM_SIMULATIONS}")
    print(f"  Timeframe: {TIMEFRAME}")
    print(f"  Candles: {CANDLE_LIMIT}")
    print("=" * 70)

    async with MarketDataFetcher() as fetcher:
        for strat_name, config in STRATEGY_CONFIGS.items():
            symbols = config["symbols"]

            logger.info("")
            logger.info("=" * 50)
            logger.info("Backtesting: %s", strat_name)
            logger.info("=" * 50)

            try:
                strategy_class = StrategyRegistry.get(strat_name)
            except KeyError as e:
                logger.error("Strategy %s not found: %s", strat_name, e)
                continue

            all_trades_pnl: list[float] = []
            trade_details: list[dict] = []

            for symbol in symbols:
                logger.info("  Fetching %s %s %d candles...", symbol, TIMEFRAME, CANDLE_LIMIT)
                try:
                    df = await fetcher.fetch_ohlcv(symbol, TIMEFRAME, limit=CANDLE_LIMIT)
                    if df is None or len(df) < 200:
                        logger.warning("  %s: insufficient data (%d bars), skipping",
                                       symbol, len(df) if df is not None else 0)
                        continue
                    logger.info("  %s: %d bars (%s to %s)",
                                symbol, len(df),
                                df.index[0].strftime("%Y-%m-%d"),
                                df.index[-1].strftime("%Y-%m-%d"))
                except Exception as e:
                    logger.warning("  %s: fetch failed — %s", symbol, e)
                    continue

                try:
                    strategy = strategy_class()
                    result = engine.run(df, strategy)

                    for trade in result.trades:
                        all_trades_pnl.append(trade.net_pnl)
                        trade_details.append({
                            "symbol": symbol,
                            "pnl": trade.net_pnl,
                            "pnl_pct": trade.pnl_pct,
                            "exit_reason": trade.exit_reason,
                        })

                    logger.info("  %s: %d trades, return: %+.2f%%, WR: %.1f%%",
                                symbol, result.total_trades,
                                result.total_return * 100,
                                result.win_rate * 100)
                except Exception as e:
                    logger.error("  %s: backtest error — %s", symbol, e)

            logger.info("  Total trades collected for %s: %d", strat_name, len(all_trades_pnl))

            # Run Monte Carlo
            if all_trades_pnl:
                logger.info("  Running %d Monte Carlo simulations...", NUM_SIMULATIONS)
                mc_results = run_monte_carlo(all_trades_pnl, NUM_SIMULATIONS, STARTING_CAPITAL)
            else:
                mc_results = {"n_trades": 0, "n_sims": 0, "error": "No trades generated"}

            all_mc_results[strat_name] = mc_results
            all_trade_details[strat_name] = trade_details

    # Print all reports
    for strat_name in STRATEGY_CONFIGS:
        print_strategy_report(strat_name, all_mc_results[strat_name], all_trade_details.get(strat_name, []))

    # ── Combined portfolio Monte Carlo ──
    print()
    print("=" * 70)
    print("  COMBINED PORTFOLIO MONTE CARLO (ALL 3 STRATEGIES POOLED)")
    print("=" * 70)

    all_combined_pnls: list[float] = []
    all_combined_details: list[dict] = []
    for strat_name in STRATEGY_CONFIGS:
        details = all_trade_details.get(strat_name, [])
        for d in details:
            all_combined_pnls.append(d["pnl"])
            all_combined_details.append(d)

    if all_combined_pnls:
        combined_mc = run_monte_carlo(all_combined_pnls, NUM_SIMULATIONS, STARTING_CAPITAL)
        print_strategy_report("COMBINED PORTFOLIO", combined_mc, all_combined_details)
    else:
        print("  No trades from any strategy — cannot run combined simulation.")

    # ── Final verdict ──
    print()
    print("=" * 70)
    print("  ATLAS FINAL VERDICT")
    print("=" * 70)
    for strat_name, mc in all_mc_results.items():
        if "error" in mc:
            verdict = "NO DATA"
        elif mc["prob_ruin_intrapath"] > 0.10:
            verdict = "DO NOT TRADE"
        elif mc["max_dd_5th"] < -0.15:
            verdict = "REDUCE SIZE"
        elif mc["prob_ruin_intrapath"] < 0.02 and mc["sharpe_5th"] > 0:
            verdict = "CLEARED FOR LIVE"
        else:
            verdict = "PROCEED WITH CAUTION"
        n = mc.get("n_trades", 0)
        med_eq = mc.get("final_equity_median", 0)
        dd5 = mc.get("max_dd_5th", 0)
        ruin = mc.get("prob_ruin_intrapath", 0)
        print(f"  {strat_name:<25} | Trades: {n:>3} | Med Equity: ${med_eq:>7.2f} | DD-5th: {dd5 * 100:>+6.2f}% | Ruin: {ruin * 100:>5.2f}% | {verdict}")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
