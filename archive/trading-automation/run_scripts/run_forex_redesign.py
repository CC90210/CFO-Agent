"""
run_forex_redesign.py -- Atlas Forex Strategy Redesign
=====================================================
Fetches real OANDA data for major forex pairs, tests ALL crypto/universal
strategies on forex data with multiple parameter profiles, and identifies
any profitable setups.

Hypothesis: market-structure-agnostic strategies (Donchian, Smart Money,
Z-score, Bollinger, etc.) that work on crypto might work on forex if
properly parameterized with tighter stops and lower commission.
"""

import os
import sys
import warnings
import traceback
from datetime import timedelta

import requests
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# -- OANDA data fetcher --------------------------------------------------

def get_oanda_token():
    token = os.getenv("OANDA_TOKEN")
    if token:
        return token
    try:
        with open(".env") as f:
            for line in f:
                if "OANDA_TOKEN=" in line:
                    return line.split("OANDA_TOKEN=")[1].split("\n")[0].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    raise RuntimeError("OANDA_TOKEN not found in env or .env file")

TOKEN = get_oanda_token()
BASE = "https://api-fxtrade.oanda.com/v3"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]
TIMEFRAMES = ["H1", "H4"]
BARS = 600

def fetch_oanda(instrument, granularity="H4", count=600):
    """Fetch OANDA candles and return OHLCV DataFrame."""
    url = f"{BASE}/instruments/{instrument}/candles"
    params = {"granularity": granularity, "count": count, "price": "M"}
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code != 200:
        print(f"  ERROR fetching {instrument} {granularity}: {r.status_code} {r.text[:200]}")
        return None
    data = r.json().get("candles", [])
    if not data:
        print(f"  WARNING: No candles for {instrument} {granularity}")
        return None
    rows = []
    for c in data:
        if not c.get("complete", True):
            continue
        mid = c["mid"]
        rows.append({
            "timestamp": pd.Timestamp(c["time"]),
            "open": float(mid["o"]),
            "high": float(mid["h"]),
            "low": float(mid["l"]),
            "close": float(mid["c"]),
            "volume": float(c.get("volume", 0))
        })
    df = pd.DataFrame(rows)
    df.set_index("timestamp", inplace=True)
    df.index = df.index.tz_localize(None)  # Remove tz for backtest engine compatibility
    return df


# -- Strategy profiles --------------------------------------------------─

# Each profile overrides atr_stop_mult and rr_ratio to test different
# risk/reward configurations on forex's tighter ranges.

PROFILES = {
    "conservative": {"atr_stop_mult": 2.5, "rr_ratio": 3.0},
    "aggressive":   {"atr_stop_mult": 1.5, "rr_ratio": 2.0},
    "daredevil":    {"atr_stop_mult": 1.0, "rr_ratio": 1.5},
}

# Strategies to test -- skip forex-specific ones (confirmed dead) and stock-specific
STRATEGIES_TO_TEST = [
    "donchian_breakout",
    "smart_money",
    "multi_timeframe",
    "volume_profile",
    "ema_crossover",
    "bollinger_squeeze",
    "ichimoku_trend",
    "zscore_mean_reversion",
    "momentum_exhaustion",
    "rsi_mean_reversion",
    "gold_trend_follower",
]


def build_strategy(name, profile_params):
    """Build a strategy instance, injecting profile params where the constructor accepts them."""
    from strategies.base import StrategyRegistry
    import inspect

    cls = StrategyRegistry.get(name)
    sig = inspect.signature(cls.__init__)
    kwargs = {}
    for param_name, value in profile_params.items():
        if param_name in sig.parameters:
            kwargs[param_name] = value
    # Special overrides for specific strategies on forex
    if name == "ichimoku_trend" and "atr_stop_mult" not in sig.parameters:
        # ichimoku uses rr_ratio only
        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    if name == "bollinger_squeeze":
        # bollinger uses atr_tp_mult instead of rr_ratio
        if "atr_tp_mult" in sig.parameters and "rr_ratio" in profile_params:
            kwargs["atr_tp_mult"] = profile_params["rr_ratio"] * 1.5
            kwargs.pop("rr_ratio", None)
    if name == "gold_trend_follower":
        # gold uses atr_tp_mult instead of rr_ratio
        if "atr_tp_mult" in sig.parameters and "rr_ratio" in profile_params:
            kwargs["atr_tp_mult"] = profile_params["rr_ratio"] * 1.5
            kwargs.pop("rr_ratio", None)

    return cls(**kwargs)


# -- Main test loop ------------------------------------------------------

def run_backtest(df, strategy, commission=0.0005):
    """Run a single backtest, return result or None on failure."""
    from backtesting.engine import BacktestEngine
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=commission,
        risk_per_trade_pct=0.015,
        slippage_enabled=True,
        regime_filter=False,  # No regime filter -- let strategies speak for themselves
        trailing_stops=False,
        scale_out_tiers=[],  # No scale-out -- per CLAUDE.md feedback
    )
    try:
        result = engine.run(df, strategy)
        return result
    except Exception as e:
        return None


def main():
    print("=" * 80)
    print("  ATLAS FOREX STRATEGY REDESIGN -- COMPREHENSIVE SCAN")
    print("  Testing ALL universal strategies on real OANDA forex data")
    print("=" * 80)
    print()

    # -- Phase 1: Fetch data ------------------------------------------
    print("[PHASE 1] Fetching OANDA data...")
    data_cache = {}
    for pair in PAIRS:
        for tf in TIMEFRAMES:
            key = f"{pair}_{tf}"
            print(f"  Fetching {pair} {tf} ({BARS} bars)...", end=" ")
            df = fetch_oanda(pair, tf, BARS)
            if df is not None:
                data_cache[key] = df
                span = (df.index[-1] - df.index[0]).days
                print(f"OK -- {len(df)} bars, {span} days, {df.index[0].date()} to {df.index[-1].date()}")
            else:
                print("FAILED")
    print()

    if not data_cache:
        print("FATAL: No data fetched. Check OANDA_TOKEN.")
        sys.exit(1)

    # -- Phase 2: Register strategies --------------------------------─
    print("[PHASE 2] Loading strategies...")
    from strategies.base import StrategyRegistry
    StrategyRegistry.discover()
    available = StrategyRegistry.list()
    test_strategies = [s for s in STRATEGIES_TO_TEST if s in available]
    print(f"  Available: {len(available)} total, testing {len(test_strategies)}")
    print(f"  Strategies: {', '.join(test_strategies)}")
    print()

    # -- Phase 3: Sweep all combinations ------------------------------
    print("[PHASE 3] Running backtests -- all strategies x all profiles x all pairs x all TFs")
    print("-" * 80)

    results = []  # List of dicts for final analysis
    total_tests = len(test_strategies) * len(PROFILES) * len(data_cache)
    completed = 0

    for strat_name in test_strategies:
        for profile_name, profile_params in PROFILES.items():
            for data_key, df in data_cache.items():
                completed += 1
                pair = data_key.rsplit("_", 1)[0]  # EUR_USD from EUR_USD_H4
                tf = data_key.split("_")[-1]

                try:
                    strategy = build_strategy(strat_name, profile_params)
                except Exception as e:
                    continue

                result = run_backtest(df, strategy)
                if result is None:
                    continue

                ret = result.total_return * 100
                trades = result.total_trades
                wr = result.win_rate * 100
                sharpe = result.sharpe_ratio
                pf = result.profit_factor
                mdd = result.max_drawdown * 100

                record = {
                    "strategy": strat_name,
                    "profile": profile_name,
                    "pair": pair.replace("_", "/"),
                    "timeframe": tf,
                    "return_pct": ret,
                    "trades": trades,
                    "win_rate": wr,
                    "sharpe": sharpe,
                    "profit_factor": pf,
                    "max_dd_pct": mdd,
                    "expectancy": result.expectancy,
                }
                results.append(record)

                # Only print noteworthy results (positive return or many trades)
                marker = ""
                if ret > 0 and trades >= 3:
                    marker = " *** PROFITABLE ***"
                elif ret > 0:
                    marker = " (positive but few trades)"

                if ret > 0 or trades >= 5:
                    print(f"  [{completed}/{total_tests}] {strat_name:25s} | {profile_name:12s} | "
                          f"{pair.replace('_','/'):<8s} {tf} | "
                          f"Return: {ret:+7.2f}% | Trades: {trades:3d} | "
                          f"WR: {wr:5.1f}% | Sharpe: {sharpe:6.2f} | "
                          f"PF: {pf:5.2f} | MDD: {mdd:+6.2f}%{marker}")

    print("-" * 80)
    print(f"  Completed {completed} backtests total")
    print()

    if not results:
        print("NO RESULTS -- all backtests failed or produced no trades.")
        return

    # -- Phase 4: Analysis --------------------------------------------
    df_results = pd.DataFrame(results)

    print("=" * 80)
    print("  PHASE 4: RESULTS ANALYSIS")
    print("=" * 80)
    print()

    # 4a. Best results by return
    print("-- TOP 20 RESULTS BY RETURN (min 3 trades) --")
    filtered = df_results[df_results["trades"] >= 3].sort_values("return_pct", ascending=False)
    if len(filtered) > 0:
        top20 = filtered.head(20)
        for _, row in top20.iterrows():
            print(f"  {row['strategy']:25s} | {row['profile']:12s} | "
                  f"{row['pair']:<8s} {row['timeframe']} | "
                  f"Return: {row['return_pct']:+7.2f}% | Trades: {row['trades']:3.0f} | "
                  f"WR: {row['win_rate']:5.1f}% | Sharpe: {row['sharpe']:6.2f} | "
                  f"PF: {row['profit_factor']:5.2f}")
    else:
        print("  NO results with 3+ trades found!")
    print()

    # 4b. Profitable strategies summary
    print("-- PROFITABLE STRATEGIES (Return > 0, >= 3 trades) --")
    profitable = df_results[(df_results["return_pct"] > 0) & (df_results["trades"] >= 3)]
    if len(profitable) > 0:
        by_strat = profitable.groupby("strategy").agg({
            "return_pct": ["mean", "count", "max"],
            "trades": "mean",
            "win_rate": "mean",
            "sharpe": "mean",
            "profit_factor": "mean",
        }).round(2)
        print(by_strat.to_string())
        print()

        # 4c. Best strategy + pair combos
        print("-- BEST STRATEGY-PAIR COMBOS (avg return > 0, >= 2 profitable runs) --")
        combo = profitable.groupby(["strategy", "pair"]).agg({
            "return_pct": ["mean", "count", "std"],
            "trades": "mean",
            "win_rate": "mean",
            "sharpe": "mean",
        }).round(2)
        combo.columns = ["avg_return", "profitable_runs", "return_std", "avg_trades", "avg_wr", "avg_sharpe"]
        combo = combo[combo["profitable_runs"] >= 2].sort_values("avg_return", ascending=False)
        if len(combo) > 0:
            print(combo.to_string())
        else:
            print("  No combos with 2+ profitable runs")
        print()
    else:
        print("  ZERO profitable setups found across all strategies.")
        print()

    # 4d. Strategy-level summary (all results)
    print("-- STRATEGY SUMMARY (ALL RESULTS, includes losing) --")
    summary = df_results.groupby("strategy").agg({
        "return_pct": ["mean", "median", "std", "min", "max", "count"],
        "trades": ["mean", "sum"],
        "win_rate": "mean",
        "sharpe": "mean",
    }).round(2)
    summary.columns = [
        "avg_ret", "med_ret", "std_ret", "min_ret", "max_ret", "n_tests",
        "avg_trades", "total_trades", "avg_wr", "avg_sharpe"
    ]
    summary = summary.sort_values("avg_ret", ascending=False)
    print(summary.to_string())
    print()

    # 4e. Timeframe analysis
    print("-- TIMEFRAME COMPARISON (avg return by TF) --")
    tf_summary = df_results.groupby("timeframe").agg({
        "return_pct": ["mean", "median"],
        "trades": "mean",
        "win_rate": "mean",
    }).round(2)
    print(tf_summary.to_string())
    print()

    # 4f. Pair analysis
    print("-- PAIR COMPARISON (avg return by pair) --")
    pair_summary = df_results.groupby("pair").agg({
        "return_pct": ["mean", "median"],
        "trades": "mean",
        "win_rate": "mean",
    }).round(2)
    print(pair_summary.to_string())
    print()

    # 4g. Profile analysis
    print("-- PROFILE COMPARISON (avg return by risk profile) --")
    profile_summary = df_results.groupby("profile").agg({
        "return_pct": ["mean", "median"],
        "trades": "mean",
        "win_rate": "mean",
    }).round(2)
    print(profile_summary.to_string())
    print()

    # -- Phase 5: Deep-dive on profitable setups ----------------------
    if len(profitable) > 0:
        print("=" * 80)
        print("  PHASE 5: DEEP DIVE ON PROFITABLE SETUPS")
        print("=" * 80)
        print()

        # Statistical significance test
        # For each profitable strategy, check if returns are significantly > 0
        from scipy import stats

        print("-- STATISTICAL SIGNIFICANCE (t-test: H0 = returns <= 0) --")
        for strat_name in profitable["strategy"].unique():
            strat_data = df_results[df_results["strategy"] == strat_name]
            returns = strat_data["return_pct"].values
            if len(returns) >= 3:
                t_stat, p_value = stats.ttest_1samp(returns, 0)
                # One-sided: we want returns > 0
                p_one_sided = p_value / 2 if t_stat > 0 else 1 - p_value / 2
                sig = "***" if p_one_sided < 0.01 else "**" if p_one_sided < 0.05 else "*" if p_one_sided < 0.10 else ""
                print(f"  {strat_name:25s} | mean: {returns.mean():+6.2f}% | "
                      f"t={t_stat:+5.2f} | p(one-sided)={p_one_sided:.4f} {sig}")
        print()

        # Best single setup details
        best = profitable.sort_values("return_pct", ascending=False).iloc[0]
        print(f"-- BEST SINGLE SETUP --")
        print(f"  Strategy:  {best['strategy']}")
        print(f"  Profile:   {best['profile']}")
        print(f"  Pair:      {best['pair']}")
        print(f"  Timeframe: {best['timeframe']}")
        print(f"  Return:    {best['return_pct']:+.2f}%")
        print(f"  Trades:    {best['trades']:.0f}")
        print(f"  Win Rate:  {best['win_rate']:.1f}%")
        print(f"  Sharpe:    {best['sharpe']:.2f}")
        print(f"  PF:        {best['profit_factor']:.2f}")
        print(f"  Max DD:    {best['max_dd_pct']:.2f}%")
        print()

    # -- Phase 6: Verdict --------------------------------------------─
    print("=" * 80)
    print("  PHASE 6: VERDICT")
    print("=" * 80)
    print()

    n_profitable = len(profitable) if len(df_results) > 0 else 0
    n_total = len(df_results)
    pct_profitable = (n_profitable / n_total * 100) if n_total > 0 else 0

    print(f"  Total backtests:     {n_total}")
    print(f"  Profitable (>=3 tr): {n_profitable} ({pct_profitable:.1f}%)")
    print()

    if n_profitable == 0:
        print("  VERDICT: FOREX IS DEAD FOR ALL STRATEGIES.")
        print("  None of the 11 universal strategies produce positive returns")
        print("  on any of the 4 major pairs at any risk profile.")
        print("  Recommendation: Do NOT allocate capital to forex.")
    elif pct_profitable < 15:
        print("  VERDICT: FOREX IS MARGINAL.")
        print(f"  Only {pct_profitable:.0f}% of configs are profitable -- likely noise.")
        print("  Any 'profitable' result needs walk-forward validation before trust.")
    else:
        print("  VERDICT: SOME FOREX EDGE EXISTS.")
        print(f"  {pct_profitable:.0f}% of configs are profitable -- worth investigating further.")
        print("  Next step: Walk-forward validate the top performers.")

    print()
    print("=" * 80)
    print("  SCAN COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
