"""
run_param_optimization.py — Parameter Grid Search for Winning Strategies

Tests parameter variations for:
  1. Donchian Breakout (entry_period, volume_mult, atr_stop_mult)
  2. RSI Mean Reversion (rsi_period, rsi_oversold, rsi_overbought)
  3. Smart Money (swing_lookback, ob_entry_tolerance, displacement_atr_mult, rr_ratio)

For each combo: runs backtest on BTC/USD + ETH/USD (4h, 500+ candles).
Tracks: net PnL, Sharpe ratio, max drawdown, win rate, trade count.
Optimizes for Sharpe ratio.

Usage:
    python run_param_optimization.py
"""
import asyncio
import itertools
import logging
import sys
import time

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from dataclasses import dataclass

import pandas as pd

from backtesting.engine import BacktestEngine
from data.fetcher import MarketDataFetcher
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
from strategies.technical.smart_money import SmartMoneyStrategy

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas.param_opt")
logger.setLevel(logging.INFO)

# ── Test symbols (Ontario-compliant /USD pairs) ──
SYMBOLS = ["BTC/USD", "ETH/USD"]
TIMEFRAME = "4h"
CANDLE_LIMIT = 600  # fetch 600 to ensure 500+ usable after warmup


@dataclass
class OptResult:
    strategy: str
    params: dict
    symbol: str
    sharpe: float
    total_return: float
    max_drawdown: float
    win_rate: float
    trades: int
    pnl: float
    profit_factor: float


# ── Parameter grids ──

DONCHIAN_GRID = {
    "entry_period": [15, 20, 25, 30, 35],
    "volume_mult": [1.0, 1.2, 1.5],
    "atr_stop_mult": [1.5, 2.0, 2.5, 3.0],
}

RSI_GRID = {
    "rsi_period": [10, 14, 18, 21],
    "rsi_oversold": [25, 28, 30, 33],
    "rsi_overbought": [67, 70, 72, 75],
}

SMART_MONEY_GRID = {
    "swing_lookback": [3, 5, 7, 10],
    "ob_entry_tolerance": [0.010, 0.015, 0.020, 0.025],
    "rr_ratio": [2.0, 3.0, 4.0],
    "displacement_atr_mult": [1.0, 1.5, 2.0],
}


def generate_combos(grid: dict) -> list[dict]:
    """Generate all parameter combinations from a grid dict."""
    keys = list(grid.keys())
    values = list(grid.values())
    combos = []
    for combo in itertools.product(*values):
        combos.append(dict(zip(keys, combo)))
    return combos


def run_single_backtest(engine: BacktestEngine, df: pd.DataFrame, strategy) -> OptResult | None:
    """Run a single backtest and return structured results."""
    try:
        result = engine.run(df, strategy)
        return OptResult(
            strategy=strategy.name,
            params={},  # filled by caller
            symbol=df.attrs.get("symbol", "UNKNOWN"),
            sharpe=result.sharpe_ratio,
            total_return=result.total_return,
            max_drawdown=result.max_drawdown,
            win_rate=result.win_rate,
            trades=result.total_trades,
            pnl=result.final_equity - result.initial_capital,
            profit_factor=result.profit_factor,
        )
    except Exception as e:
        logger.warning("    Backtest error: %s", e)
        return None


def optimize_donchian(engine: BacktestEngine, data: dict[str, pd.DataFrame]) -> list[OptResult]:
    """Grid search over donchian_breakout parameters."""
    combos = generate_combos(DONCHIAN_GRID)
    total = len(combos) * len(data)
    logger.info("=" * 70)
    logger.info("DONCHIAN BREAKOUT: %d combos x %d symbols = %d backtests", len(combos), len(data), total)
    logger.info("=" * 70)

    results = []
    done = 0
    for combo in combos:
        strategy = DonchianBreakoutStrategy(
            entry_period=combo["entry_period"],
            volume_mult=combo["volume_mult"],
            atr_stop_mult=combo["atr_stop_mult"],
            # Keep other params at current production defaults
            exit_period=10,
            atr_period=14,
            rr_ratio=3.0,
            adx_period=14,
            adx_min=20.0,
            rsi_period=14,
            rsi_max_long=75.0,
            rsi_min_short=25.0,
            volume_period=20,
            sma_trend_period=200,
        )
        for sym, df in data.items():
            r = run_single_backtest(engine, df, strategy)
            done += 1
            if r:
                r.params = combo
                r.symbol = sym
                results.append(r)
                if done % 20 == 0 or done == total:
                    logger.info("  [%d/%d] %s | %s | Sharpe=%.3f Return=%.2f%% Trades=%d",
                                done, total, sym,
                                " ".join(f"{k}={v}" for k, v in combo.items()),
                                r.sharpe, r.total_return * 100, r.trades)
    return results


def optimize_rsi(engine: BacktestEngine, data: dict[str, pd.DataFrame]) -> list[OptResult]:
    """Grid search over rsi_mean_reversion parameters."""
    combos = generate_combos(RSI_GRID)
    total = len(combos) * len(data)
    logger.info("=" * 70)
    logger.info("RSI MEAN REVERSION: %d combos x %d symbols = %d backtests", len(combos), len(data), total)
    logger.info("=" * 70)

    results = []
    done = 0
    for combo in combos:
        strategy = RSIMeanReversionStrategy(
            rsi_period=combo["rsi_period"],
            rsi_oversold=float(combo["rsi_oversold"]),
            rsi_overbought=float(combo["rsi_overbought"]),
            # Keep other params at current production defaults
            rsi_exit=50.0,
            bb_period=20,
            bb_std=2.0,
            adx_period=14,
            adx_max=25.0,
            atr_period=14,
            atr_stop_mult=1.0,
            volume_period=20,
            volume_mult=1.2,
            ema_trend_period=200,
            rr_min=2.0,
        )
        for sym, df in data.items():
            r = run_single_backtest(engine, df, strategy)
            done += 1
            if r:
                r.params = combo
                r.symbol = sym
                results.append(r)
                if done % 20 == 0 or done == total:
                    logger.info("  [%d/%d] %s | %s | Sharpe=%.3f Return=%.2f%% Trades=%d",
                                done, total, sym,
                                " ".join(f"{k}={v}" for k, v in combo.items()),
                                r.sharpe, r.total_return * 100, r.trades)
    return results


def optimize_smart_money(engine: BacktestEngine, data: dict[str, pd.DataFrame]) -> list[OptResult]:
    """Grid search over smart_money parameters."""
    combos = generate_combos(SMART_MONEY_GRID)
    total = len(combos) * len(data)
    logger.info("=" * 70)
    logger.info("SMART MONEY: %d combos x %d symbols = %d backtests", len(combos), len(data), total)
    logger.info("=" * 70)

    results = []
    done = 0
    for combo in combos:
        strategy = SmartMoneyStrategy(
            swing_lookback=combo["swing_lookback"],
            ob_entry_tolerance=combo["ob_entry_tolerance"],
            rr_ratio=combo["rr_ratio"],
            displacement_atr_mult=combo["displacement_atr_mult"],
            # Keep other params at current production defaults
            ob_lookback=50,
            fvg_min_size_atr_ratio=0.15,
            bos_lookback=100,
            atr_period=14,
            atr_stop_mult=2.0,
            volume_period=20,
            min_rr_for_swing_tp=2.0,
            displacement_vol_mult=1.2,
            time_stop_bars=50,
        )
        for sym, df in data.items():
            r = run_single_backtest(engine, df, strategy)
            done += 1
            if r:
                r.params = combo
                r.symbol = sym
                results.append(r)
                if done % 20 == 0 or done == total:
                    logger.info("  [%d/%d] %s | %s | Sharpe=%.3f Return=%.2f%% Trades=%d",
                                done, total, sym,
                                " ".join(f"{k}={v}" for k, v in combo.items()),
                                r.sharpe, r.total_return * 100, r.trades)
    return results


def analyze_results(strategy_name: str, results: list[OptResult], current_params: dict):
    """Analyze optimization results and print findings."""
    if not results:
        print(f"\n{'=' * 70}")
        print(f"  {strategy_name}: NO RESULTS (0 backtests completed)")
        print(f"{'=' * 70}")
        return

    print(f"\n{'=' * 70}")
    print(f"  {strategy_name.upper()} — PARAMETER OPTIMIZATION RESULTS")
    print(f"{'=' * 70}")

    # Aggregate across symbols: average Sharpe per param combo
    from collections import defaultdict
    combo_stats = defaultdict(lambda: {"sharpes": [], "returns": [], "trades": [], "win_rates": [],
                                        "drawdowns": [], "pnls": [], "pfs": []})

    for r in results:
        key = tuple(sorted(r.params.items()))
        combo_stats[key]["sharpes"].append(r.sharpe)
        combo_stats[key]["returns"].append(r.total_return)
        combo_stats[key]["trades"].append(r.trades)
        combo_stats[key]["win_rates"].append(r.win_rate)
        combo_stats[key]["drawdowns"].append(r.max_drawdown)
        combo_stats[key]["pnls"].append(r.pnl)
        combo_stats[key]["pfs"].append(r.profit_factor)

    # Rank by average Sharpe (only combos with trades on both symbols)
    ranked = []
    for key, stats in combo_stats.items():
        avg_sharpe = sum(stats["sharpes"]) / len(stats["sharpes"])
        avg_return = sum(stats["returns"]) / len(stats["returns"])
        total_trades = sum(stats["trades"])
        avg_wr = sum(stats["win_rates"]) / len(stats["win_rates"])
        avg_dd = sum(stats["drawdowns"]) / len(stats["drawdowns"])
        avg_pnl = sum(stats["pnls"]) / len(stats["pnls"])
        avg_pf = sum(stats["pfs"]) / len(stats["pfs"])
        ranked.append({
            "params": dict(key),
            "avg_sharpe": avg_sharpe,
            "avg_return": avg_return,
            "total_trades": total_trades,
            "avg_win_rate": avg_wr,
            "avg_drawdown": avg_dd,
            "avg_pnl": avg_pnl,
            "avg_pf": avg_pf,
        })

    ranked.sort(key=lambda x: x["avg_sharpe"], reverse=True)

    # Show current params results
    current_key = tuple(sorted(current_params.items()))
    current_entry = combo_stats.get(current_key)
    if current_entry:
        current_sharpe = sum(current_entry["sharpes"]) / len(current_entry["sharpes"])
        current_return = sum(current_entry["returns"]) / len(current_entry["returns"])
        print(f"\n  CURRENT PARAMS: {current_params}")
        print(f"    Avg Sharpe: {current_sharpe:.3f}  |  Avg Return: {current_return * 100:.2f}%  |  Trades: {sum(current_entry['trades'])}")
    else:
        current_sharpe = 0.0
        print(f"\n  CURRENT PARAMS: {current_params}")
        print(f"    (Current combo not in grid — using baseline Sharpe = 0)")

    # Top 10
    print(f"\n  TOP 10 PARAMETER COMBOS (ranked by avg Sharpe across BTC/USD + ETH/USD):")
    print(f"  {'Rank':<5} {'Avg Sharpe':>10} {'Avg Ret%':>9} {'Trades':>7} {'WR%':>6} {'MaxDD%':>8} {'AvgPnL':>9} {'PF':>6}  Params")
    print(f"  {'-' * 100}")
    for i, entry in enumerate(ranked[:10]):
        params_str = " ".join(f"{k}={v}" for k, v in entry["params"].items())
        marker = " <-- CURRENT" if entry["params"] == current_params else ""
        print(f"  {i+1:<5} {entry['avg_sharpe']:>10.3f} {entry['avg_return']*100:>+8.2f}% {entry['total_trades']:>7} "
              f"{entry['avg_win_rate']*100:>5.1f}% {entry['avg_drawdown']*100:>+7.2f}% "
              f"${entry['avg_pnl']:>8.2f} {entry['avg_pf']:>5.2f}  {params_str}{marker}")

    # Bottom 5 (worst)
    if len(ranked) > 10:
        print(f"\n  BOTTOM 5 (avoid these):")
        for entry in ranked[-5:]:
            params_str = " ".join(f"{k}={v}" for k, v in entry["params"].items())
            print(f"         {entry['avg_sharpe']:>10.3f} {entry['avg_return']*100:>+8.2f}% {entry['total_trades']:>7}  {params_str}")

    # Best vs current improvement
    if ranked:
        best = ranked[0]
        improvement = best["avg_sharpe"] - current_sharpe
        print(f"\n  OPTIMAL PARAMS: {best['params']}")
        print(f"    Avg Sharpe: {best['avg_sharpe']:.3f}  |  Avg Return: {best['avg_return'] * 100:+.2f}%  |  Trades: {best['total_trades']}")
        print(f"    Sharpe improvement vs current: {improvement:+.3f}")
        if improvement > 0.1:
            print(f"    ** SIGNIFICANT IMPROVEMENT — recommend updating config **")
        elif improvement > 0:
            print(f"    Marginal improvement — validate on more symbols before switching.")
        else:
            print(f"    Current params are already near-optimal.")

    # Per-symbol breakdown for best combo
    if ranked:
        best_params = ranked[0]["params"]
        print(f"\n  Per-symbol breakdown for best combo:")
        for r in results:
            if r.params == best_params:
                print(f"    {r.symbol:<10} Sharpe={r.sharpe:>7.3f}  Return={r.total_return*100:>+7.2f}%  "
                      f"WR={r.win_rate*100:>5.1f}%  Trades={r.trades:>3}  DD={r.max_drawdown*100:>+6.2f}%  PnL=${r.pnl:>8.2f}")


async def main():
    start = time.time()

    print("=" * 70)
    print("  ATLAS PARAMETER OPTIMIZATION ENGINE")
    print("  Strategies: donchian_breakout, rsi_mean_reversion, smart_money")
    print(f"  Symbols: {', '.join(SYMBOLS)}")
    print(f"  Timeframe: {TIMEFRAME}, Candles: {CANDLE_LIMIT}")
    print("=" * 70)

    # ── Fetch data ──
    print("\nFetching market data from Kraken...")
    data: dict[str, pd.DataFrame] = {}

    async with MarketDataFetcher() as fetcher:
        for sym in SYMBOLS:
            try:
                df = await fetcher.fetch_ohlcv(sym, TIMEFRAME, limit=CANDLE_LIMIT)
                if df is not None and len(df) >= 300:
                    df.attrs["symbol"] = sym
                    data[sym] = df
                    print(f"  {sym}: {len(df)} bars fetched ({df.index[0].date()} to {df.index[-1].date()})")
                else:
                    print(f"  {sym}: INSUFFICIENT DATA ({len(df) if df is not None else 0} bars)")
            except Exception as e:
                print(f"  {sym}: FETCH ERROR — {e}")

    if not data:
        print("\nFATAL: No data fetched. Check API keys and network.")
        sys.exit(1)

    # ── Backtest engine ──
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.001,
        risk_per_trade_pct=0.010,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],
    )

    # ── Current production parameters (from strategies.yaml) ──
    current_donchian = {"entry_period": 20, "volume_mult": 1.2, "atr_stop_mult": 2.0}
    current_rsi = {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70}
    current_smart_money = {"swing_lookback": 5, "ob_entry_tolerance": 0.015,
                           "rr_ratio": 3.0, "displacement_atr_mult": 1.5}

    # ── Run optimizations ──
    donchian_results = optimize_donchian(engine, data)
    rsi_results = optimize_rsi(engine, data)
    smart_money_results = optimize_smart_money(engine, data)

    # ── Analyze and report ──
    analyze_results("donchian_breakout", donchian_results, current_donchian)
    analyze_results("rsi_mean_reversion", rsi_results, current_rsi)
    analyze_results("smart_money", smart_money_results, current_smart_money)

    elapsed = time.time() - start
    total_backtests = len(donchian_results) + len(rsi_results) + len(smart_money_results)

    print(f"\n{'=' * 70}")
    print(f"  OPTIMIZATION COMPLETE")
    print(f"  Total backtests: {total_backtests}")
    print(f"  Runtime: {elapsed:.1f}s ({elapsed/60:.1f}min)")
    print(f"  Avg per backtest: {elapsed/max(total_backtests,1):.2f}s")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    asyncio.run(main())
