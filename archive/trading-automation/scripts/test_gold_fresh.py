"""
scripts/test_gold_fresh.py — Fresh backtest: gold_trend_follower vs donchian_breakout on XAU_USD

Fetches 500 bars of 4H XAU_USD data directly from the OANDA REST API (live account,
read-only candlestick endpoint — no trades placed). Runs two strategies through the
BacktestEngine and reports a side-by-side comparison.

Strategies tested
-----------------
  gold_trend_follower  — Keltner Channel + triple EMA + ADX + MACD (tuned for gold)
  donchian_breakout    — 20-bar channel breakout with ADX + volume filters

Parameters
----------
  gold_trend_follower (from config/strategies.yaml):
    keltner_ema_period=20, keltner_atr_period=14, keltner_multiplier=2.0
    ema_fast=20, ema_mid=50, ema_slow=200
    adx_period=14, adx_threshold=25.0
    macd_fast=12, macd_slow=26, macd_signal=9
    atr_period=14, atr_stop_mult=2.5, atr_tp_mult=5.0

  donchian_breakout (defaults — same as crypto validation):
    entry_period=20, exit_period=10, atr_stop_mult=2.0, rr_ratio=3.0

Data source
-----------
  OANDA v20 REST API  (live endpoint — practice=True uses the same URL)
  Instrument : XAU_USD (gold vs USD)
  Granularity: H4 (4-hour bars)
  Count      : 500 complete bars
  Credentials: OANDA_TOKEN and OANDA_ACCOUNT_ID from .env
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Path bootstrap — run from any working directory
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO_ROOT)
os.chdir(_REPO_ROOT)

from dotenv import load_dotenv

load_dotenv()

import requests
import pandas as pd

# ---------------------------------------------------------------------------
# OANDA credentials — always from environment, never hardcoded
# ---------------------------------------------------------------------------
OANDA_TOKEN = os.getenv("OANDA_TOKEN", "")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID", "")
OANDA_BASE_URL = "https://api-fxtrade.oanda.com/v3"

if not OANDA_TOKEN or not OANDA_ACCOUNT_ID:
    print("ERROR: OANDA_TOKEN or OANDA_ACCOUNT_ID not set.")
    print("  Set both in your .env file and retry.")
    sys.exit(1)

_HEADERS = {"Authorization": f"Bearer {OANDA_TOKEN}"}

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
INSTRUMENT = "XAU_USD"
GRANULARITY = "H4"
BARS = 500

# ---------------------------------------------------------------------------
# Strategy imports and instances
# ---------------------------------------------------------------------------
from strategies.base import StrategyRegistry

StrategyRegistry.discover()

from backtesting.engine import BacktestEngine

GOLD_TREND_FOLLOWER = StrategyRegistry.build(
    "gold_trend_follower",
    # Keltner Channel
    keltner_ema_period=20,
    keltner_atr_period=14,
    keltner_multiplier=2.0,
    # Triple EMA stack
    ema_fast=20,
    ema_mid=50,
    ema_slow=200,
    # ADX
    adx_period=14,
    adx_threshold=25.0,
    # MACD
    macd_fast=12,
    macd_slow=26,
    macd_signal=9,
    # ATR-based risk
    atr_period=14,
    atr_stop_mult=2.5,
    atr_tp_mult=5.0,
)

DONCHIAN = StrategyRegistry.build(
    "donchian_breakout",
    # Defaults — same as used in crypto validation runs
    entry_period=20,
    exit_period=10,
    atr_stop_mult=2.0,
    rr_ratio=3.0,
    adx_min=20.0,
)

STRATEGIES = [GOLD_TREND_FOLLOWER, DONCHIAN]


# ---------------------------------------------------------------------------
# Data fetching — direct OANDA REST, no async needed
# ---------------------------------------------------------------------------

def fetch_oanda_ohlcv(instrument: str, granularity: str, count: int) -> pd.DataFrame:
    """
    Fetch OHLCV candles from the OANDA v20 REST API.

    Returns a DataFrame indexed by UTC timestamp with columns:
        open, high, low, close, volume

    Only complete (closed) candles are included. The live/incomplete bar
    is skipped to avoid look-ahead bias in backtesting.

    Raises RuntimeError if the API returns a non-200 status.
    """
    url = f"{OANDA_BASE_URL}/instruments/{instrument}/candles"
    params = {
        "granularity": granularity,
        "count": str(count),
        "price": "M",  # mid prices (bid/ask midpoint)
    }
    response = requests.get(url, headers=_HEADERS, params=params, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"OANDA API error {response.status_code} for {instrument}/{granularity}: "
            f"{response.text[:300]}"
        )

    candles = response.json().get("candles", [])
    if not candles:
        raise RuntimeError(f"No candles returned for {instrument}/{granularity}")

    rows = []
    for candle in candles:
        if not candle.get("complete", True):
            continue  # skip live/incomplete bar — avoids look-ahead bias
        mid = candle["mid"]
        rows.append(
            {
                "timestamp": pd.Timestamp(candle["time"]),
                "open": float(mid["o"]),
                "high": float(mid["h"]),
                "low": float(mid["l"]),
                "close": float(mid["c"]),
                "volume": float(candle.get("volume", 0.0)),
            }
        )

    if not rows:
        raise RuntimeError(
            f"All candles were incomplete for {instrument}/{granularity} — "
            "market may be closed."
        )

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp")
    # Strip tz — BacktestEngine expects tz-naive index (matches existing test scripts)
    df.index = df.index.tz_localize(None)
    df.attrs["symbol"] = instrument
    return df


# ---------------------------------------------------------------------------
# Backtest runner — delegates to BacktestEngine (same as run_fresh_gold_validation.py)
# ---------------------------------------------------------------------------

def run_backtest(strategy, df: pd.DataFrame) -> dict:
    """
    Run a single strategy through the BacktestEngine and return a results dict.

    Commission of 0.05% per side (~$5 per $10K notional) approximates OANDA's
    typical spread on gold. Scale-out tiers are disabled per MEMORY feedback_scaleout_harmful.
    """
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.0005,
        regime_filter=True,
        scale_out_tiers=[],  # disabled per MEMORY — destroys returns
    )
    try:
        result = engine.run(df, strategy)
        return {
            "strategy": strategy.name,
            "return_pct": round(result.total_return * 100, 2),
            "trades": result.total_trades,
            "win_rate": round(result.win_rate * 100, 1),
            "profit_factor": round(result.profit_factor, 3),
            "max_drawdown_pct": round(result.max_drawdown * 100, 2),
            "sharpe": round(result.sharpe_ratio, 3),
            "final_equity": round(result.final_equity, 2),
            "error": None,
        }
    except Exception as exc:
        return {
            "strategy": strategy.name,
            "return_pct": None,
            "trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe": 0.0,
            "final_equity": 10_000.0,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_header() -> None:
    print()
    print("=" * 72)
    print("  ATLAS — Gold Backtest: gold_trend_follower vs donchian_breakout")
    print(f"  Instrument : {INSTRUMENT}  |  Timeframe : {GRANULARITY}  |  Bars : {BARS}")
    print(f"  Data source: OANDA v20 REST API (live, read-only)")
    print(f"  Capital    : $10,000  |  Commission : 0.05%/side  |  Regime filter: ON")
    print("=" * 72)
    print()


def print_results(results: list[dict]) -> None:
    col_w = {
        "strategy": 24,
        "return": 10,
        "trades": 7,
        "win_rate": 9,
        "pf": 9,
        "max_dd": 9,
        "sharpe": 8,
        "equity": 12,
    }

    header = (
        f"{'Strategy':<{col_w['strategy']}} "
        f"{'Return%':>{col_w['return']}} "
        f"{'Trades':>{col_w['trades']}} "
        f"{'WinRate':>{col_w['win_rate']}} "
        f"{'ProfFact':>{col_w['pf']}} "
        f"{'MaxDD%':>{col_w['max_dd']}} "
        f"{'Sharpe':>{col_w['sharpe']}} "
        f"{'Equity':>{col_w['equity']}}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        if r["error"]:
            print(f"{r['strategy']:<{col_w['strategy']}}  ERROR: {r['error'][:60]}")
            continue

        ret_str = f"{r['return_pct']:+.2f}%" if r["return_pct"] is not None else "N/A"
        marker = (
            " ***" if (r["return_pct"] or 0) > 10
            else " ++" if (r["return_pct"] or 0) > 0
            else " --"
        )

        print(
            f"{r['strategy']:<{col_w['strategy']}} "
            f"{ret_str:>{col_w['return']}} "
            f"{r['trades']:>{col_w['trades']}} "
            f"{r['win_rate']:>{col_w['win_rate'] - 1}.1f}% "
            f"{r['profit_factor']:>{col_w['pf']}.3f} "
            f"{r['max_drawdown_pct']:>{col_w['max_dd']}.2f}% "
            f"{r['sharpe']:>{col_w['sharpe']}.3f} "
            f"${r['final_equity']:>{col_w['equity'] - 1},.2f}"
            f"{marker}"
        )
    print()


def print_params_summary() -> None:
    print("Parameters used:")
    print("  gold_trend_follower:")
    print("    keltner_ema=20  keltner_atr=14  keltner_mult=2.0")
    print("    ema_fast=20  ema_mid=50  ema_slow=200")
    print("    adx_period=14  adx_threshold=25.0")
    print("    macd(12,26,9)  atr_stop=2.5x  atr_tp=5.0x")
    print()
    print("  donchian_breakout:")
    print("    entry_period=20  exit_period=10  adx_min=20.0")
    print("    atr_stop=2.0x  rr_ratio=3.0")
    print()


def print_verdict(results: list[dict]) -> None:
    valid = [r for r in results if r["error"] is None and r["trades"] > 0]
    if not valid:
        print("Verdict: No tradeable signals generated. Increase bars or relax filters.")
        return

    best = max(valid, key=lambda r: r["return_pct"])
    print("Verdict:")
    print(f"  Best performer : {best['strategy']}")
    print(f"  Return         : {best['return_pct']:+.2f}%")
    print(f"  Win rate       : {best['win_rate']:.1f}%")
    print(f"  Profit factor  : {best['profit_factor']:.3f}")
    print(f"  Max drawdown   : {best['max_drawdown_pct']:.2f}%")

    profitable = [r for r in valid if r["return_pct"] > 0]
    if profitable:
        print(f"  Profitable strategies: {', '.join(r['strategy'] for r in profitable)}")
    else:
        print("  No profitable strategies found in this window.")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print_header()

    # --- Fetch data ---
    print(f"[1] Fetching {BARS} bars of {INSTRUMENT} {GRANULARITY} from OANDA...")
    try:
        df = fetch_oanda_ohlcv(INSTRUMENT, GRANULARITY, BARS)
    except RuntimeError as exc:
        print(f"  FATAL: {exc}")
        sys.exit(1)

    n_bars = len(df)
    date_from = df.index[0].strftime("%Y-%m-%d %H:%M")
    date_to = df.index[-1].strftime("%Y-%m-%d %H:%M")
    price_lo = df["close"].min()
    price_hi = df["close"].max()

    print(f"  Received : {n_bars} complete bars")
    print(f"  Range    : {date_from}  ->  {date_to}")
    print(f"  Close    : ${price_lo:,.2f}  —  ${price_hi:,.2f}")
    print()

    # --- Run backtests ---
    print("[2] Running bar-by-bar backtests (BacktestEngine, regime_filter=True)...")
    results = []
    for strategy in STRATEGIES:
        print(f"  Running {strategy.name}...", end=" ", flush=True)
        r = run_backtest(strategy, df)
        results.append(r)
        if r["error"]:
            print(f"ERROR — {r['error'][:60]}")
        else:
            print(f"done ({r['trades']} trades, {r['return_pct']:+.2f}%)")

    print()

    # --- Report ---
    print("[3] Results — XAU_USD 4H  ({} bars)\n".format(n_bars))
    print_results(results)
    print_params_summary()
    print_verdict(results)

    print("=" * 72)
    print("  ATLAS gold backtest complete.")
    print("=" * 72)
    print()


if __name__ == "__main__":
    main()
