"""
run_fresh_gold_validation.py — ATLAS Gold/Silver Strategy Validation with REAL OANDA Data

Fetches live XAU_USD and XAG_USD candles directly from OANDA REST API (bypassing
the adapter's practice=True bug), then backtests every viable strategy across
multiple instruments, timeframes, and risk profiles.
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import requests
import pandas as pd

# ---------------------------------------------------------------------------
# OANDA API setup — direct REST, bypassing the buggy adapter
# ---------------------------------------------------------------------------

def _read_env_var(key):
    """Read from env or .env file."""
    val = os.getenv(key)
    if val:
        return val
    try:
        with open(".env", "r") as f:
            content = f.read()
        val = content.split(f"{key}=")[1].split("\n")[0].strip().strip('"').strip("'")
        return val
    except Exception:
        return None

TOKEN = _read_env_var("OANDA_TOKEN")
ACCOUNT = _read_env_var("OANDA_ACCOUNT_ID")
BASE = "https://api-fxtrade.oanda.com/v3"
headers = {"Authorization": f"Bearer {TOKEN}"}

if not TOKEN or not ACCOUNT:
    print("ERROR: OANDA_TOKEN or OANDA_ACCOUNT_ID not found in env or .env")
    sys.exit(1)


def fetch_oanda(instrument, granularity="H4", count=600):
    """Fetch OHLCV candles from OANDA live API."""
    url = f"{BASE}/instruments/{instrument}/candles"
    params = {"granularity": granularity, "count": count, "price": "M"}
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print(f"  ERROR fetching {instrument} {granularity}: {r.status_code} — {r.text[:200]}")
        return None
    data = r.json().get("candles", [])
    if not data:
        print(f"  ERROR: No candles returned for {instrument} {granularity}")
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
    df.index = df.index.tz_localize(None)  # strip tz for backtest engine compatibility
    return df


# ---------------------------------------------------------------------------
# Backtest setup
# ---------------------------------------------------------------------------

from backtesting.engine import BacktestEngine
from strategies.base import StrategyRegistry

# Auto-discover all strategies
StrategyRegistry.discover()

# Gold-applicable strategies to test
STRATEGIES_TO_TEST = [
    "gold_trend_follower",
    "donchian_breakout",
    "smart_money",
    "ema_crossover",
    "rsi_mean_reversion",
    "bollinger_squeeze",
    "multi_timeframe",
    "ichimoku_trend",
    "zscore_mean_reversion",
    "momentum_exhaustion",
]

# Gold trend follower risk profiles
GOLD_PROFILES = {
    "conservative": dict(
        keltner_multiplier=2.5,
        adx_threshold=30.0,
        atr_stop_mult=3.0,
        atr_tp_mult=6.0,
    ),
    "aggressive": dict(
        keltner_multiplier=1.5,
        adx_threshold=20.0,
        atr_stop_mult=2.0,
        atr_tp_mult=4.0,
    ),
    "daredevil": dict(
        keltner_multiplier=1.0,
        adx_threshold=15.0,
        atr_stop_mult=1.5,
        atr_tp_mult=3.0,
    ),
}

# Test matrix: (instrument, granularity, label)
TEST_MATRIX = [
    ("XAU_USD", "H4", "Gold 4H"),
    ("XAU_USD", "H1", "Gold 1H"),
    ("XAG_USD", "H4", "Silver 4H"),
]


def run_backtest(strategy, df, label, commission=0.0005):
    """Run a single backtest and return a results dict."""
    engine = BacktestEngine(
        initial_capital=10000,
        commission_pct=commission,
        regime_filter=True,
        scale_out_tiers=[],  # scale-out disabled per MEMORY feedback
    )
    try:
        result = engine.run(df, strategy)
        return {
            "label": label,
            "strategy": strategy.name,
            "return_pct": round(result.total_return * 100, 2),
            "win_rate": round(result.win_rate * 100, 1),
            "sharpe": round(result.sharpe_ratio, 3),
            "max_dd_pct": round(result.max_drawdown * 100, 2),
            "profit_factor": round(result.profit_factor, 3),
            "trades": result.total_trades,
            "final_equity": round(result.final_equity, 2),
        }
    except Exception as e:
        return {
            "label": label,
            "strategy": strategy.name,
            "return_pct": "ERROR",
            "win_rate": "-",
            "sharpe": "-",
            "max_dd_pct": "-",
            "profit_factor": "-",
            "trades": 0,
            "final_equity": "-",
            "error": str(e)[:80],
        }


def print_table(results):
    """Print a formatted results table."""
    if not results:
        print("  No results to display.\n")
        return

    header = f"{'Label':<16} {'Strategy':<24} {'Return%':>9} {'WinRate':>8} {'Sharpe':>8} {'MaxDD%':>8} {'PF':>8} {'Trades':>7} {'Equity':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        ret = r['return_pct'] if isinstance(r['return_pct'], str) else f"{r['return_pct']:+.2f}%"
        wr = r['win_rate'] if isinstance(r['win_rate'], str) else f"{r['win_rate']:.1f}%"
        sh = r['sharpe'] if isinstance(r['sharpe'], str) else f"{r['sharpe']:.3f}"
        dd = r['max_dd_pct'] if isinstance(r['max_dd_pct'], str) else f"{r['max_dd_pct']:.2f}%"
        pf = r['profit_factor'] if isinstance(r['profit_factor'], str) else f"{r['profit_factor']:.3f}"
        eq = r['final_equity'] if isinstance(r['final_equity'], str) else f"${r['final_equity']:,.2f}"
        print(f"{r['label']:<16} {r['strategy']:<24} {ret:>9} {wr:>8} {sh:>8} {dd:>8} {pf:>8} {r['trades']:>7} {eq:>10}")
        if 'error' in r:
            print(f"  ^^ ERROR: {r['error']}")
    print()


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main():
    print("=" * 80)
    print("  ATLAS — Gold/Silver Strategy Validation (LIVE OANDA DATA)")
    print("=" * 80)
    print()

    # Step 1: Fetch all data
    print("[1] Fetching live OANDA data...")
    data_cache = {}
    for instrument, granularity, label in TEST_MATRIX:
        print(f"  Fetching {instrument} {granularity} (600 bars)...")
        df = fetch_oanda(instrument, granularity, count=600)
        if df is not None:
            print(f"    Got {len(df)} bars: {df.index[0]} -> {df.index[-1]}")
            print(f"    Price range: {df['close'].min():.2f} — {df['close'].max():.2f}")
            data_cache[(instrument, granularity)] = df
        else:
            print(f"    FAILED — skipping {label}")
    print()

    if not data_cache:
        print("FATAL: No data fetched. Check OANDA credentials.")
        sys.exit(1)

    # Step 2: Gold Trend Follower — 3 risk profiles across all instruments/timeframes
    print("=" * 80)
    print("[2] GOLD TREND FOLLOWER — Risk Profile Comparison")
    print("=" * 80)
    profile_results = []

    for (instrument, granularity), df in data_cache.items():
        label_base = f"{instrument.replace('_','/')}-{granularity}"
        # Default profile first
        strat = StrategyRegistry.build("gold_trend_follower")
        r = run_backtest(strat, df, f"{label_base}/default")
        profile_results.append(r)

        # Named profiles
        for profile_name, params in GOLD_PROFILES.items():
            strat = StrategyRegistry.build("gold_trend_follower", **params)
            r = run_backtest(strat, df, f"{label_base}/{profile_name[:5]}")
            profile_results.append(r)

    print_table(profile_results)

    # Step 3: All strategies on Gold 4H
    print("=" * 80)
    print("[3] ALL STRATEGIES ON GOLD 4H (XAU_USD)")
    print("=" * 80)
    gold_4h = data_cache.get(("XAU_USD", "H4"))
    strat_results = []

    if gold_4h is not None:
        for strat_name in STRATEGIES_TO_TEST:
            try:
                strat = StrategyRegistry.build(strat_name)
                r = run_backtest(strat, gold_4h, "XAU/USD-H4")
                strat_results.append(r)
            except Exception as e:
                strat_results.append({
                    "label": "XAU/USD-H4",
                    "strategy": strat_name,
                    "return_pct": "SKIP",
                    "win_rate": "-",
                    "sharpe": "-",
                    "max_dd_pct": "-",
                    "profit_factor": "-",
                    "trades": 0,
                    "final_equity": "-",
                    "error": str(e)[:80],
                })
        print_table(strat_results)
    else:
        print("  Skipped — no Gold 4H data.\n")

    # Step 4: All strategies on Gold 1H
    print("=" * 80)
    print("[4] ALL STRATEGIES ON GOLD 1H (XAU_USD)")
    print("=" * 80)
    gold_1h = data_cache.get(("XAU_USD", "H1"))
    strat_results_1h = []

    if gold_1h is not None:
        for strat_name in STRATEGIES_TO_TEST:
            try:
                strat = StrategyRegistry.build(strat_name)
                r = run_backtest(strat, gold_1h, "XAU/USD-H1")
                strat_results_1h.append(r)
            except Exception as e:
                strat_results_1h.append({
                    "label": "XAU/USD-H1",
                    "strategy": strat_name,
                    "return_pct": "SKIP",
                    "win_rate": "-",
                    "sharpe": "-",
                    "max_dd_pct": "-",
                    "profit_factor": "-",
                    "trades": 0,
                    "final_equity": "-",
                    "error": str(e)[:80],
                })
        print_table(strat_results_1h)
    else:
        print("  Skipped — no Gold 1H data.\n")

    # Step 5: All strategies on Silver 4H
    print("=" * 80)
    print("[5] ALL STRATEGIES ON SILVER 4H (XAG_USD)")
    print("=" * 80)
    silver_4h = data_cache.get(("XAG_USD", "H4"))
    strat_results_silver = []

    if silver_4h is not None:
        for strat_name in STRATEGIES_TO_TEST:
            try:
                strat = StrategyRegistry.build(strat_name)
                r = run_backtest(strat, silver_4h, "XAG/USD-H4")
                strat_results_silver.append(r)
            except Exception as e:
                strat_results_silver.append({
                    "label": "XAG/USD-H4",
                    "strategy": strat_name,
                    "return_pct": "SKIP",
                    "win_rate": "-",
                    "sharpe": "-",
                    "max_dd_pct": "-",
                    "profit_factor": "-",
                    "trades": 0,
                    "final_equity": "-",
                    "error": str(e)[:80],
                })
        print_table(strat_results_silver)
    else:
        print("  Skipped — no Silver 4H data.\n")

    # Step 6: Summary — profitable setups only
    print("=" * 80)
    print("[6] PROFITABLE SETUPS SUMMARY (Return > 0%)")
    print("=" * 80)
    all_results = profile_results + strat_results + strat_results_1h + strat_results_silver
    profitable = [r for r in all_results if isinstance(r.get('return_pct'), (int, float)) and r['return_pct'] > 0]
    profitable.sort(key=lambda x: x['return_pct'], reverse=True)

    if profitable:
        print_table(profitable)
    else:
        print("  No profitable setups found.\n")

    # Losers
    print("=" * 80)
    print("[7] UNPROFITABLE SETUPS (Return <= 0%)")
    print("=" * 80)
    unprofitable = [r for r in all_results if isinstance(r.get('return_pct'), (int, float)) and r['return_pct'] <= 0]
    unprofitable.sort(key=lambda x: x['return_pct'])
    if unprofitable:
        print_table(unprofitable)
    else:
        print("  All setups were profitable.\n")

    print("=" * 80)
    print("  ATLAS Gold/Silver Validation Complete.")
    print(f"  Total tests: {len(all_results)} | Profitable: {len(profitable)} | Unprofitable: {len(unprofitable)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
