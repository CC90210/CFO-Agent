"""
run_forex_gold_test.py
----------------------
Real-data backtest of ATLAS forex and gold strategies using live OANDA data.

Data source  : OANDA v20 REST API (direct requests — bypasses OANDAAdapter
               async complexity to keep this script synchronous and readable)
Strategies   : london_breakout, forex_carry_momentum,
               gold_trend_follower, forex_session_momentum
Param sets   : conservative (defaults), aggressive, daredevil
Engine       : BacktestEngine(initial_capital=10_000, commission_pct=0.0005)
"""

from __future__ import annotations

import sys
import time
from typing import Any

# Windows-safe UTF-8 output
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Atlas imports
# ---------------------------------------------------------------------------
from backtesting.engine import BacktestEngine, BacktestResult
from config.settings import settings

# Import all strategy modules so subclasses are registered
import strategies.technical  # noqa: F401 — side-effect import

from strategies.technical.london_breakout import LondonBreakoutStrategy
from strategies.technical.forex_carry_momentum import ForexCarryMomentumStrategy
from strategies.technical.gold_trend_follower import GoldTrendFollowerStrategy
from strategies.technical.forex_session_momentum import ForexSessionMomentumStrategy

# ---------------------------------------------------------------------------
# OANDA direct REST fetcher
# ---------------------------------------------------------------------------

_OANDA_BASE = "https://api-fxtrade.oanda.com/v3"
_TIMEFRAME_MAP: dict[str, str] = {
    "5m": "M5",
    "15m": "M15",
    "1h": "H1",
    "4h": "H4",
    "1d": "D",
}


def _fetch_oanda_ohlcv(
    symbol: str,
    timeframe: str,
    count: int = 600,
) -> pd.DataFrame:
    """
    Fetch OHLCV candles from OANDA v20 REST API directly.

    Parameters
    ----------
    symbol    : OANDA instrument format, e.g. "EUR_USD", "XAU_USD"
    timeframe : CCXT-style timeframe, e.g. "4h", "1h", "5m"
    count     : number of completed candles to fetch (max 5000 per OANDA docs)

    Returns
    -------
    pd.DataFrame with DatetimeIndex (UTC) and columns open/high/low/close/volume.
    df.attrs["symbol"] is set to the OANDA instrument name.
    """
    granularity = _TIMEFRAME_MAP.get(timeframe)
    if granularity is None:
        raise ValueError(f"Unsupported timeframe '{timeframe}'. Valid: {list(_TIMEFRAME_MAP)}")

    token = settings.oanda.oanda_token
    url = f"{_OANDA_BASE}/instruments/{symbol}/candles"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    # OANDA max per request: 5000 candles.
    # For large counts we page — but 600 is well within limits.
    params: dict[str, str] = {
        "count": str(min(count, 5000)),
        "granularity": granularity,
        "price": "M",  # midpoint prices
    }

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    candles = data.get("candles", [])
    rows: list[dict[str, Any]] = []
    for c in candles:
        if not c.get("complete", True):
            continue  # skip incomplete (live) candle
        mid = c.get("mid", {})
        ts = pd.Timestamp(c["time"]).tz_convert("UTC")
        rows.append(
            {
                "timestamp": ts,
                "open": float(mid.get("o", 0.0)),
                "high": float(mid.get("h", 0.0)),
                "low": float(mid.get("l", 0.0)),
                "close": float(mid.get("c", 0.0)),
                "volume": float(c.get("volume", 1.0)),  # OANDA tick-volume proxy
            }
        )

    df = pd.DataFrame(rows).set_index("timestamp")
    df.index = pd.DatetimeIndex(df.index, tz="UTC")
    df.attrs["symbol"] = symbol
    return df


# ---------------------------------------------------------------------------
# Parameter sets
# ---------------------------------------------------------------------------

def _make_strategies(
    name: str,
    atr_stop_mult: float,
    rr_ratio: float,
) -> dict[str, Any]:
    """Return a dict of strategy_key → strategy_instance for one param set."""
    return {
        "london_breakout": LondonBreakoutStrategy(
            breakout_vol_mult=0.8,  # relaxed volume gate (OANDA tick volume ≠ real volume)
            tp_range_mult=rr_ratio,
        ),
        "forex_carry_momentum": ForexCarryMomentumStrategy(
            atr_stop_mult=atr_stop_mult,
            rr_ratio=rr_ratio,
        ),
        "gold_trend_follower": GoldTrendFollowerStrategy(
            atr_stop_mult=atr_stop_mult,
            atr_tp_mult=atr_stop_mult * rr_ratio,
        ),
        "forex_session_momentum": ForexSessionMomentumStrategy(
            sl_range_mult=atr_stop_mult / 2.5,  # normalise relative to conservative=1.0
            tp_range_mult=rr_ratio / 1.5,       # normalise relative to conservative=1.0
        ),
    }


PARAM_SETS: dict[str, dict[str, float]] = {
    "conservative": {"atr_stop_mult": 2.5, "rr_ratio": 2.0},
    "aggressive":   {"atr_stop_mult": 1.5, "rr_ratio": 4.0},
    "daredevil":    {"atr_stop_mult": 1.0, "rr_ratio": 6.0},
}

# ---------------------------------------------------------------------------
# Instrument configuration
# ---------------------------------------------------------------------------

# (symbol, timeframe, strategy_names_that_apply)
INSTRUMENTS: list[tuple[str, str, list[str]]] = [
    # London breakout: 15m is ideal but 600-bar requirement means we need a
    # long window. Use 1h as compromise (still session-level resolution).
    ("EUR_USD", "1h",  ["london_breakout", "forex_session_momentum"]),
    ("GBP_USD", "1h",  ["london_breakout", "forex_session_momentum"]),
    ("USD_JPY", "1h",  ["london_breakout", "forex_session_momentum"]),
    ("AUD_USD", "1h",  ["forex_session_momentum"]),
    ("USD_CAD", "1h",  ["forex_session_momentum"]),
    # Carry + momentum runs on 4h
    ("EUR_USD", "4h",  ["forex_carry_momentum"]),
    ("GBP_USD", "4h",  ["forex_carry_momentum"]),
    ("USD_JPY", "4h",  ["forex_carry_momentum"]),
    ("AUD_USD", "4h",  ["forex_carry_momentum"]),
    ("USD_CAD", "4h",  ["forex_carry_momentum"]),
    # Gold and silver — trend follower on 4h, session momentum on 1h
    ("XAU_USD", "4h",  ["gold_trend_follower"]),
    ("XAG_USD", "4h",  ["gold_trend_follower"]),
    ("XAU_USD", "1h",  ["forex_session_momentum"]),
]

# ---------------------------------------------------------------------------
# Result table helpers
# ---------------------------------------------------------------------------

def _emoji_pnl(total_return_pct: float) -> str:
    """Simple text indicator — no emojis per coding rules."""
    if total_return_pct >= 5.0:
        return "STRONG+"
    if total_return_pct >= 1.0:
        return "PROFIT "
    if total_return_pct >= 0.0:
        return "FLAT   "
    return "LOSS   "


def _print_header() -> None:
    print()
    print("=" * 110)
    print("  ATLAS — Forex & Gold Strategy Backtest on REAL OANDA Data")
    print(f"  Data source  : OANDA v20 REST API (live account)")
    print(f"  Capital      : $10,000 | Commission: 0.05% per side (5 bps)")
    print(f"  Regime filter: ON | Scale-out: OFF")
    print("=" * 110)
    hdr = (
        f"  {'Symbol':<10} {'TF':<4} {'Strategy':<25} {'Params':<14}"
        f" {'Return':>8} {'Trades':>6} {'WinRate':>8} {'MaxDD':>8} {'Sharpe':>7} {'Status':<10}"
    )
    print(hdr)
    print("  " + "-" * 107)


def _print_row(
    symbol: str,
    tf: str,
    strategy_name: str,
    param_label: str,
    result: BacktestResult,
) -> None:
    ret_pct = result.total_return * 100
    wr_pct = result.win_rate * 100
    mdd_pct = result.max_drawdown * 100
    status = _emoji_pnl(ret_pct)

    print(
        f"  {symbol:<10} {tf:<4} {strategy_name:<25} {param_label:<14}"
        f" {ret_pct:>+7.2f}% {result.total_trades:>6}"
        f" {wr_pct:>7.1f}% {mdd_pct:>+7.2f}% {result.sharpe_ratio:>7.3f}"
        f"  {status}"
    )


def _print_section(title: str) -> None:
    print()
    print(f"  >>> {title}")
    print("  " + "-" * 107)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:  # noqa: C901
    _print_header()

    engine = BacktestEngine(
        initial_capital=10_000.0,
        commission_pct=0.0005,   # 0.05% = 5 bps — realistic for forex
        regime_filter=True,
        trailing_stops=False,    # disabled per feedback_trailing_stops.md
        scale_out_tiers=[],      # disabled per feedback_scaleout_harmful.md
    )

    # Cache fetched DataFrames to avoid re-fetching the same symbol+timeframe
    data_cache: dict[tuple[str, str], pd.DataFrame | None] = {}

    # Accumulate all results for the summary table
    all_results: list[tuple[str, str, str, str, BacktestResult]] = []

    for symbol, tf, strategy_names in INSTRUMENTS:
        cache_key = (symbol, tf)
        if cache_key not in data_cache:
            print(f"\n  Fetching {symbol} / {tf} from OANDA...", end=" ", flush=True)
            try:
                # Fetch enough bars:
                # - gold_trend_follower needs 210+ bars (EMA200)
                # - forex_carry_momentum needs 210+ bars (SMA200)
                # - london_breakout / forex_session_momentum need ~100+ bars
                # Ask for 600 to give every strategy a full warmup window.
                df = _fetch_oanda_ohlcv(symbol, tf, count=600)
                print(f"OK ({len(df)} bars, {df.index[0].date()} to {df.index[-1].date()})")
                data_cache[cache_key] = df
            except Exception as exc:
                print(f"FAILED: {exc}")
                data_cache[cache_key] = None
            # Small sleep to be polite to the API
            time.sleep(0.3)

        df = data_cache[cache_key]
        if df is None:
            continue

        for param_label, param_kwargs in PARAM_SETS.items():
            strategies_for_run = _make_strategies("", **param_kwargs)

            for strat_name in strategy_names:
                strategy = strategies_for_run[strat_name]
                try:
                    result = engine.run(df, strategy)
                    _print_row(symbol, tf, strat_name, param_label, result)
                    all_results.append((symbol, tf, strat_name, param_label, result))
                except Exception as exc:
                    print(
                        f"  {symbol:<10} {tf:<4} {strat_name:<25} {param_label:<14}"
                        f"  ERROR: {exc}"
                    )

    # ---------------------------------------------------------------------------
    # Summary: best-performing strategy+param per symbol
    # ---------------------------------------------------------------------------
    print()
    print("=" * 110)
    print("  SUMMARY — Best Param Set per Symbol/Strategy (by Total Return)")
    print("=" * 110)
    hdr = (
        f"  {'Symbol':<10} {'TF':<4} {'Strategy':<25} {'Best Params':<14}"
        f" {'Return':>8} {'WinRate':>8} {'MaxDD':>8} {'Sharpe':>7}"
    )
    print(hdr)
    print("  " + "-" * 90)

    # Group by (symbol, tf, strategy_name) — pick best return
    grouped: dict[tuple[str, str, str], tuple[str, BacktestResult]] = {}
    for symbol, tf, strat_name, param_label, result in all_results:
        key = (symbol, tf, strat_name)
        existing = grouped.get(key)
        if existing is None or result.total_return > existing[1].total_return:
            grouped[key] = (param_label, result)

    # Sort descending by return
    sorted_results = sorted(
        grouped.items(),
        key=lambda kv: kv[1][1].total_return,
        reverse=True,
    )

    profitable_count = 0
    for (symbol, tf, strat_name), (best_param, result) in sorted_results:
        ret_pct = result.total_return * 100
        wr_pct = result.win_rate * 100
        mdd_pct = result.max_drawdown * 100
        if ret_pct > 0:
            profitable_count += 1
        print(
            f"  {symbol:<10} {tf:<4} {strat_name:<25} {best_param:<14}"
            f" {ret_pct:>+7.2f}% {wr_pct:>7.1f}% {mdd_pct:>+7.2f}% {result.sharpe_ratio:>7.3f}"
        )

    total_unique = len(sorted_results)
    print()
    print(f"  Profitable strategy/symbol combos: {profitable_count} / {total_unique}")
    print(f"  (Regime filter active — some combos may have 0 trades if regime not aligned)")
    print("=" * 110)

    # ---------------------------------------------------------------------------
    # Verdict: which strategies have a genuine OANDA edge
    # ---------------------------------------------------------------------------
    print()
    print("  VERDICT — Strategy-level edge on real OANDA data:")
    print()

    strat_summary: dict[str, list[float]] = {}
    for (symbol, tf, strat_name), (_, result) in sorted_results:
        strat_summary.setdefault(strat_name, []).append(result.total_return * 100)

    for strat_name, returns in sorted(strat_summary.items(), key=lambda kv: -sum(kv[1]) / max(len(kv[1]), 1)):
        avg_ret = sum(returns) / len(returns)
        best_ret = max(returns)
        worst_ret = min(returns)
        profitable_pct = 100 * sum(1 for r in returns if r > 0) / len(returns)
        verdict = "EDGE CONFIRMED" if avg_ret > 0 and profitable_pct >= 50 else "NEEDS TUNING"
        print(
            f"    {strat_name:<30}  avg={avg_ret:>+6.2f}%  "
            f"best={best_ret:>+6.2f}%  worst={worst_ret:>+6.2f}%  "
            f"profitable={profitable_pct:.0f}%  -> {verdict}"
        )

    print()
    print("  Atlas forex/gold backtest complete.")
    print()


if __name__ == "__main__":
    main()
