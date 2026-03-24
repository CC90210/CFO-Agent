"""
run_gold_silver_backtest.py — ATLAS Gold/Silver Comprehensive Backtest

Fetches live XAU_USD and XAG_USD candles from OANDA REST API (live endpoint),
then backtests all relevant strategies with regime filtering ON and scale-out OFF.

Strategies tested:
  - donchian_breakout (enabled, gold+silver in config)
  - multi_timeframe (enabled, gold+silver in config)
  - rsi_mean_reversion (bear market winner — test on gold)
  - smart_money (bear market winner — test on gold)
  - gold_trend_follower (profitable on real OANDA data)

Reports: total PnL, trade count, win rate, max drawdown, Sharpe ratio, profit factor.

Usage:
    python run_gold_silver_backtest.py
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import requests
import pandas as pd

# ---------------------------------------------------------------------------
# OANDA API setup — direct REST to live endpoint
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
        print(f"  ERROR fetching {instrument} {granularity}: {r.status_code} -- {r.text[:200]}")
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

# Strategies to test on gold and silver
GOLD_STRATEGIES = [
    "donchian_breakout",
    "multi_timeframe",
    "rsi_mean_reversion",
    "smart_money",
    "gold_trend_follower",
]

SILVER_STRATEGIES = [
    "donchian_breakout",
    "multi_timeframe",
]


def run_backtest(strategy, df, label, commission=0.0005):
    """Run a single backtest and return a results dict."""
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=commission,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # scale-out disabled per MEMORY feedback
    )
    try:
        result = engine.run(df, strategy)
        return {
            "label": label,
            "strategy": strategy.name,
            "return_pct": round(result.total_return * 100, 2),
            "return_dollar": round(result.final_equity - result.initial_capital, 2),
            "win_rate": round(result.win_rate * 100, 1),
            "sharpe": round(result.sharpe_ratio, 3),
            "sortino": round(result.sortino_ratio, 3),
            "max_dd_pct": round(result.max_drawdown * 100, 2),
            "profit_factor": round(result.profit_factor, 3),
            "trades": result.total_trades,
            "winning": result.winning_trades,
            "losing": result.losing_trades,
            "final_equity": round(result.final_equity, 2),
            "expectancy": round(result.expectancy, 2),
        }
    except Exception as e:
        return {
            "label": label,
            "strategy": strategy.name,
            "return_pct": "ERROR",
            "return_dollar": "-",
            "win_rate": "-",
            "sharpe": "-",
            "sortino": "-",
            "max_dd_pct": "-",
            "profit_factor": "-",
            "trades": 0,
            "winning": "-",
            "losing": "-",
            "final_equity": "-",
            "expectancy": "-",
            "error": str(e)[:120],
        }


def print_table(results):
    """Print a formatted results table."""
    if not results:
        print("  No results to display.\n")
        return

    header = f"{'Instrument':<14} {'Strategy':<24} {'Return%':>9} {'PnL$':>9} {'WR':>7} {'Sharpe':>8} {'Sortino':>8} {'MaxDD%':>8} {'PF':>7} {'W/L':>7} {'Exp$':>8}"
    print(header)
    print("-" * len(header))
    for r in results:
        ret = r['return_pct'] if isinstance(r['return_pct'], str) else f"{r['return_pct']:+.2f}%"
        pnl = r['return_dollar'] if isinstance(r['return_dollar'], str) else f"${r['return_dollar']:+.0f}"
        wr = r['win_rate'] if isinstance(r['win_rate'], str) else f"{r['win_rate']:.1f}%"
        sh = r['sharpe'] if isinstance(r['sharpe'], str) else f"{r['sharpe']:.2f}"
        so = r['sortino'] if isinstance(r['sortino'], str) else f"{r['sortino']:.2f}"
        dd = r['max_dd_pct'] if isinstance(r['max_dd_pct'], str) else f"{r['max_dd_pct']:.2f}%"
        pf = r['profit_factor'] if isinstance(r['profit_factor'], str) else f"{r['profit_factor']:.2f}"
        wl = f"{r['winning']}/{r['losing']}" if isinstance(r.get('winning'), int) else "-"
        exp = r['expectancy'] if isinstance(r['expectancy'], str) else f"${r['expectancy']:.0f}"
        print(f"{r['label']:<14} {r['strategy']:<24} {ret:>9} {pnl:>9} {wr:>7} {sh:>8} {so:>8} {dd:>8} {pf:>7} {wl:>7} {exp:>8}")
        if 'error' in r:
            print(f"  ^^ ERROR: {r['error']}")
    print()


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main():
    print("=" * 90)
    print("  ATLAS -- Gold & Silver Comprehensive Backtest (LIVE OANDA DATA)")
    print("  Regime filtering: ON | Scale-out: OFF | Commission: 0.05%")
    print("=" * 90)
    print()

    # ── Step 1: Fetch data ──
    print("[1] FETCHING LIVE OANDA DATA")
    print("-" * 50)

    instruments = [
        ("XAU_USD", "H4", 600, "Gold 4H"),
        ("XAG_USD", "H4", 600, "Silver 4H"),
    ]

    data_cache = {}
    for instrument, granularity, count, label in instruments:
        print(f"  Fetching {instrument} {granularity} ({count} bars)...")
        df = fetch_oanda(instrument, granularity, count)
        if df is not None:
            print(f"    {len(df)} bars: {df.index[0]} -> {df.index[-1]}")
            print(f"    Price: {df['close'].min():.2f} - {df['close'].max():.2f} (latest: {df['close'].iloc[-1]:.2f})")
            print(f"    Avg volume: {df['volume'].mean():.0f}")
            data_cache[(instrument, granularity)] = df
        else:
            print(f"    FAILED -- skipping {label}")

    if not data_cache:
        print("\nFATAL: No data fetched. Check OANDA credentials.")
        sys.exit(1)
    print()

    all_results = []

    # ── Step 2: Gold (XAU_USD) backtests ──
    print("=" * 90)
    print("[2] GOLD (XAU_USD) -- ALL STRATEGIES")
    print("=" * 90)

    gold_4h = data_cache.get(("XAU_USD", "H4"))
    gold_results = []

    if gold_4h is not None:
        for strat_name in GOLD_STRATEGIES:
            try:
                strat = StrategyRegistry.build(strat_name)
                r = run_backtest(strat, gold_4h, "XAU_USD")
                gold_results.append(r)
            except Exception as e:
                gold_results.append({
                    "label": "XAU_USD",
                    "strategy": strat_name,
                    "return_pct": "SKIP",
                    "return_dollar": "-",
                    "win_rate": "-",
                    "sharpe": "-",
                    "sortino": "-",
                    "max_dd_pct": "-",
                    "profit_factor": "-",
                    "trades": 0,
                    "winning": "-",
                    "losing": "-",
                    "final_equity": "-",
                    "expectancy": "-",
                    "error": str(e)[:120],
                })
        print_table(gold_results)
        all_results.extend(gold_results)
    else:
        print("  Skipped -- no Gold 4H data.\n")

    # ── Step 3: Silver (XAG_USD) backtests ──
    print("=" * 90)
    print("[3] SILVER (XAG_USD) -- DONCHIAN + MULTI_TIMEFRAME")
    print("=" * 90)

    silver_4h = data_cache.get(("XAG_USD", "H4"))
    silver_results = []

    if silver_4h is not None:
        for strat_name in SILVER_STRATEGIES:
            try:
                strat = StrategyRegistry.build(strat_name)
                r = run_backtest(strat, silver_4h, "XAG_USD")
                silver_results.append(r)
            except Exception as e:
                silver_results.append({
                    "label": "XAG_USD",
                    "strategy": strat_name,
                    "return_pct": "SKIP",
                    "return_dollar": "-",
                    "win_rate": "-",
                    "sharpe": "-",
                    "sortino": "-",
                    "max_dd_pct": "-",
                    "profit_factor": "-",
                    "trades": 0,
                    "winning": "-",
                    "losing": "-",
                    "final_equity": "-",
                    "expectancy": "-",
                    "error": str(e)[:120],
                })
        print_table(silver_results)
        all_results.extend(silver_results)
    else:
        print("  Skipped -- no Silver 4H data.\n")

    # ── Step 4: Summary ──
    print("=" * 90)
    print("[4] COMBINED RESULTS -- SORTED BY RETURN")
    print("=" * 90)

    # Separate valid results from errors
    valid = [r for r in all_results if isinstance(r.get('return_pct'), (int, float))]
    errors = [r for r in all_results if not isinstance(r.get('return_pct'), (int, float))]

    # Sort by return
    valid.sort(key=lambda x: x['return_pct'], reverse=True)
    print_table(valid)

    if errors:
        print("ERRORS/SKIPPED:")
        for e in errors:
            print(f"  {e['label']} / {e['strategy']}: {e.get('error', 'unknown')}")
        print()

    # ── Step 5: Verdict ──
    profitable = [r for r in valid if r['return_pct'] > 0]
    unprofitable = [r for r in valid if r['return_pct'] <= 0]

    print("=" * 90)
    print("[5] VERDICT")
    print("=" * 90)
    print(f"  Total tests:    {len(valid)}")
    print(f"  Profitable:     {len(profitable)}")
    print(f"  Unprofitable:   {len(unprofitable)}")
    if valid:
        avg_ret = sum(r['return_pct'] for r in valid) / len(valid)
        total_pnl = sum(r['return_dollar'] for r in valid if isinstance(r['return_dollar'], (int, float)))
        best = max(valid, key=lambda x: x['return_pct'])
        worst = min(valid, key=lambda x: x['return_pct'])
        print(f"  Avg return:     {avg_ret:+.2f}%")
        print(f"  Total PnL:      ${total_pnl:+,.0f} (across all tests)")
        print(f"  Best:           {best['strategy']} on {best['label']} ({best['return_pct']:+.2f}%, Sharpe {best['sharpe']})")
        print(f"  Worst:          {worst['strategy']} on {worst['label']} ({worst['return_pct']:+.2f}%, Sharpe {worst['sharpe']})")
    print()

    # ── GO/NO-GO per strategy-symbol pair ──
    print("  GO/NO-GO:")
    for r in valid:
        is_go = r['return_pct'] > 0 and r['trades'] >= 3
        sharpe_ok = isinstance(r['sharpe'], (int, float)) and r['sharpe'] > 0.5
        verdict = "GO" if is_go else "NO-GO"
        confidence = "HIGH" if (is_go and sharpe_ok) else ("MEDIUM" if is_go else "LOW")
        print(f"    {r['label']:<14} {r['strategy']:<24} -> {verdict} (confidence: {confidence})")

    print()
    print("=" * 90)
    print("  ATLAS Gold/Silver Backtest Complete.")
    print("=" * 90)


if __name__ == "__main__":
    main()
