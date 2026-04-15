"""
run_optimized_backtest.py — Per-Symbol Risk Profile Validation
===============================================================
Backtests using the empirically optimal risk profile for each strategy-symbol
pair, comparing results against the conservative baseline.

Usage:
    python run_optimized_backtest.py
"""

from __future__ import annotations

import sys
import time
from copy import deepcopy
from pathlib import Path

import numpy as np
import yaml

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backtesting.engine import BacktestEngine, BacktestResult
from core.risk_profiles import (
    OPTIMAL_PROFILES,
    RiskProfile,
    get_risk_profile,
    _PROFILE_BY_NAME,
    CONSERVATIVE,
)
from strategies.base import BaseStrategy
from strategies.technical import *  # noqa: F401,F403

INITIAL_CAPITAL = 10_000.0
COMMISSION_PCT = 0.001


def fetch_kraken_ohlcv(symbol, timeframe, limit):
    import ccxt
    exchange = ccxt.kraken({"enableRateLimit": True})
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    if not ohlcv or len(ohlcv) < 50:
        return None
    import pandas as pd
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df.attrs["symbol"] = symbol
    return df


def get_strategy_class(name):
    for cls in BaseStrategy.__subclasses__():
        if cls.name == name:
            return cls
    return None


def run():
    with open(_ROOT / "config" / "strategies.yaml") as f:
        cfg = yaml.safe_load(f)

    enabled = {
        name: scfg for name, scfg in cfg["strategies"].items()
        if scfg.get("enabled", False)
    }

    data_cache = {}
    results_conservative = []
    results_optimized = []

    print("=" * 100)
    print("  ATLAS — PER-SYMBOL RISK PROFILE VALIDATION")
    print("  Comparing conservative baseline vs empirically optimal profiles")
    print("=" * 100)

    for strat_name, strat_cfg in enabled.items():
        cls = get_strategy_class(strat_name)
        if not cls:
            continue

        timeframe = strat_cfg.get("timeframe", "4h")
        symbols = strat_cfg.get("symbols", [])
        base_params = strat_cfg.get("parameters", {})
        n_bars = 1000

        print(f"\n{'─' * 100}")
        print(f"  STRATEGY: {strat_name}")
        print(f"{'─' * 100}")
        print(f"  {'Symbol':<14s} {'Profile':<15s} {'Return':>8s} {'WR':>6s} {'Trades':>7s} "
              f"{'Sharpe':>8s} {'MaxDD':>7s} {'PF':>6s}  {'vs Conservative':>15s}")
        print(f"  {'-' * 90}")

        for symbol in symbols:
            if "/" not in symbol or "USDT" not in symbol:
                continue  # skip non-crypto (no live data)

            # Fetch data once
            cache_key = (symbol, timeframe)
            if cache_key not in data_cache:
                df = fetch_kraken_ohlcv(symbol, timeframe, n_bars)
                if df is None:
                    print(f"  {symbol:<14s} [SKIP] No data")
                    continue
                data_cache[cache_key] = df
            df = data_cache[cache_key]
            df.attrs["symbol"] = symbol

            # Get optimal profile for this pair
            profile = get_risk_profile(strat_name, symbol, conviction=0.7)

            # Run conservative baseline
            cons_params = deepcopy(base_params)
            cons_params["atr_stop_mult"] = CONSERVATIVE.atr_stop_mult
            cons_params["rr_ratio"] = CONSERVATIVE.rr_ratio
            try:
                cons_strategy = cls(**cons_params)
                engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, commission_pct=COMMISSION_PCT, regime_filter=True)
                cons_result = engine.run(df, cons_strategy)
                cons_ret = cons_result.total_return * 100
            except Exception as e:
                print(f"  {symbol:<14s} [ERROR] Conservative: {e}")
                continue

            # Run optimized profile
            opt_params = deepcopy(base_params)
            opt_params["atr_stop_mult"] = profile.atr_stop_mult
            opt_params["rr_ratio"] = profile.rr_ratio
            try:
                opt_strategy = cls(**opt_params)
                engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, commission_pct=COMMISSION_PCT, regime_filter=True)
                opt_result = engine.run(df, opt_strategy)
            except Exception as e:
                print(f"  {symbol:<14s} [ERROR] Optimized: {e}")
                continue

            opt_ret = opt_result.total_return * 100
            opt_wr = opt_result.win_rate * 100
            opt_trades = opt_result.total_trades
            opt_sharpe = opt_result.sharpe_ratio
            opt_dd = opt_result.max_drawdown * 100
            opt_pf = opt_result.profit_factor

            delta = opt_ret - cons_ret
            delta_str = f"{delta:+.2f}%" if profile.name != "conservative" else "baseline"

            results_conservative.append(cons_ret)
            results_optimized.append(opt_ret)

            icon = "+" if opt_ret > 0 else "X"
            print(
                f"  [{icon}] {symbol:<12s} {profile.name:<15s} {opt_ret:+7.2f}% {opt_wr:5.1f}% "
                f"{opt_trades:6d}  {opt_sharpe:+7.2f} {opt_dd:+6.1f}% {opt_pf:5.2f}  {delta_str:>15s}"
            )

    # Summary
    if results_conservative and results_optimized:
        cons_avg = np.mean(results_conservative)
        opt_avg = np.mean(results_optimized)
        improvement = opt_avg - cons_avg

        print(f"\n{'=' * 100}")
        print(f"  SUMMARY")
        print(f"{'=' * 100}")
        print(f"  Conservative baseline avg:  {cons_avg:+.2f}%")
        print(f"  Optimized profiles avg:     {opt_avg:+.2f}%")
        print(f"  Improvement:                {improvement:+.2f}%")
        print(f"  Pairs tested:               {len(results_optimized)}")

        go_cons = sum(1 for r in results_conservative if r > 0)
        go_opt = sum(1 for r in results_optimized if r > 0)
        print(f"  GO pairs (conservative):    {go_cons}/{len(results_conservative)}")
        print(f"  GO pairs (optimized):       {go_opt}/{len(results_optimized)}")
        print(f"\n{'=' * 100}")


if __name__ == "__main__":
    start = time.time()
    run()
    print(f"\n  [Validation took {time.time() - start:.1f}s]")
