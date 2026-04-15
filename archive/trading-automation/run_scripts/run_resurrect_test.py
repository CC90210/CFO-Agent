"""
run_resurrect_test.py — Parameter Resurrection Test for momentum_exhaustion & multi_timeframe
==============================================================================================
Tests whether disabled strategies can become profitable under aggressive parameter variants.
Fetches live Kraken 1h data (2000 bars) for 7 crypto symbols and runs 4 parameter sets
for momentum_exhaustion plus 2 sets for multi_timeframe (4h, 1000 bars).

Outputs a comparison table: return%, WR%, trades, Sharpe per param-set per symbol.

Usage:
    python run_resurrect_test.py
"""

from __future__ import annotations

import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

# Force UTF-8 on Windows before any other output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

# Ensure project root on path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backtesting.engine import BacktestEngine, BacktestResult
from strategies.base import BaseStrategy

# Import all strategies to trigger registration
from strategies.technical import *  # noqa: F401,F403

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

INITIAL_CAPITAL = 10_000.0
COMMISSION_PCT = 0.001

CRYPTO_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "ADA/USDT",
    "DOT/USDT",
]

# ─────────────────────────────────────────────────────────────────────────────
#  Parameter sets under test
# ─────────────────────────────────────────────────────────────────────────────

EXHAUSTION_PARAM_SETS: list[tuple[str, dict]] = [
    (
        "Baseline",
        dict(
            atr_stop_mult=1.5,
            rr_ratio=2.0,
            reversal_body_pct=0.30,
            volume_mult=1.5,
            move_atr_mult=2.0,
        ),
    ),
    (
        "Aggressive-A",
        dict(
            atr_stop_mult=1.0,
            rr_ratio=3.0,
            reversal_body_pct=0.15,
            volume_mult=1.2,
            move_atr_mult=2.0,
        ),
    ),
    (
        "Aggressive-B",
        dict(
            atr_stop_mult=2.0,
            rr_ratio=3.5,
            reversal_body_pct=0.20,
            volume_mult=1.0,
            move_atr_mult=2.0,
        ),
    ),
    (
        "Daredevil",
        dict(
            atr_stop_mult=0.8,
            rr_ratio=4.0,
            reversal_body_pct=0.15,
            volume_mult=1.0,
            move_atr_mult=1.5,
        ),
    ),
]

MTF_PARAM_SETS: list[tuple[str, dict]] = [
    (
        "Baseline",
        dict(
            htf_fast_ema=50,
            htf_slow_ema=200,
            mtf_ema=21,
            atr_stop_mult=3.0,
            rr_ratio=4.0,
        ),
    ),
    (
        "Aggressive",
        dict(
            htf_fast_ema=30,
            htf_slow_ema=100,
            mtf_ema=10,
            atr_stop_mult=2.0,
            rr_ratio=2.5,
        ),
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
#  Data fetching
# ─────────────────────────────────────────────────────────────────────────────


def fetch_kraken_ohlcv(symbol: str, timeframe: str, limit: int) -> pd.DataFrame | None:
    """Fetch OHLCV from Kraken via ccxt (free, no API key required)."""
    try:
        import ccxt

        exchange = ccxt.kraken({"enableRateLimit": True})
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not ohlcv or len(ohlcv) < 50:
            return None
        df = pd.DataFrame(
            ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df.attrs["symbol"] = symbol
        return df
    except Exception as exc:
        print(f"    [WARN] Failed to fetch {symbol} {timeframe}: {exc}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Strategy helpers
# ─────────────────────────────────────────────────────────────────────────────


def get_strategy_class(name: str) -> type[BaseStrategy] | None:
    """Find a registered strategy class by its `name` attribute."""
    for cls in BaseStrategy.__subclasses__():
        if cls.name == name:
            return cls
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Result container
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ResurrectResult:
    strategy: str
    param_label: str
    symbol: str
    return_pct: float
    win_rate: float
    total_trades: int
    sharpe: float
    max_dd_pct: float
    profit_factor: float
    status: str  # "GO" or "NO-GO"


# ─────────────────────────────────────────────────────────────────────────────
#  Core run function
# ─────────────────────────────────────────────────────────────────────────────


def run_param_set(
    strategy_name: str,
    param_label: str,
    override_params: dict,
    df: pd.DataFrame,
    engine: BacktestEngine,
) -> ResurrectResult | None:
    """
    Build a strategy instance with default constructor params overridden by
    override_params, run the backtest, and return a ResurrectResult.
    Returns None on construction or runtime failure.
    """
    cls = get_strategy_class(strategy_name)
    if cls is None:
        print(f"      [ERROR] Strategy class '{strategy_name}' not found in registry.")
        return None

    try:
        strategy = cls(**override_params)
    except Exception as exc:
        print(f"      [ERROR] Constructor failed for {param_label}: {exc}")
        return None

    symbol = df.attrs.get("symbol", "UNKNOWN")
    try:
        result: BacktestResult = engine.run(df, strategy)
    except Exception as exc:
        print(f"      [ERROR] Backtest crashed ({param_label}): {exc}")
        traceback.print_exc()
        return None

    ret_pct = result.total_return * 100
    win_rate = result.win_rate * 100
    trades = result.total_trades
    sharpe = result.sharpe_ratio
    max_dd = result.max_drawdown * 100
    pf = result.profit_factor
    status = "GO" if (ret_pct > 0 and trades >= 2 and win_rate >= 15) else "NO-GO"

    return ResurrectResult(
        strategy=strategy_name,
        param_label=param_label,
        symbol=symbol,
        return_pct=ret_pct,
        win_rate=win_rate,
        total_trades=trades,
        sharpe=sharpe,
        max_dd_pct=max_dd,
        profit_factor=pf,
        status=status,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Printing helpers
# ─────────────────────────────────────────────────────────────────────────────

_COL_W = 14  # column width for param-set columns


def _header_row(param_labels: list[str]) -> str:
    left = f"  {'Symbol':<12s}"
    cols = "".join(f"  {lbl:>{_COL_W}s}" for lbl in param_labels)
    return left + cols


def _metric_row(
    metric: str,
    symbol: str,
    results_by_label: dict[str, ResurrectResult | None],
    fmt: str,
) -> str:
    """Build a single metric row for one symbol across all param-set columns."""
    left = f"  {symbol:<12s}"
    cols_parts = []
    for lbl, res in results_by_label.items():
        if res is None:
            cols_parts.append(f"  {'N/A':>{_COL_W}s}")
        else:
            val = getattr(res, metric)
            formatted = format(val, fmt)
            cols_parts.append(f"  {formatted:>{_COL_W}s}")
    return left + "".join(cols_parts)


def print_strategy_table(
    strategy_name: str,
    param_labels: list[str],
    all_results: dict[str, dict[str, ResurrectResult | None]],
) -> None:
    """
    Print a comparison table for one strategy.

    all_results layout: all_results[symbol][param_label] = ResurrectResult | None
    """
    width = 14 + len(param_labels) * (_COL_W + 2) + 2
    sep = "  " + "-" * (width - 2)

    metrics: list[tuple[str, str, str]] = [
        ("Return %", "return_pct", "+.2f"),
        ("Win Rate %", "win_rate", ".1f"),
        ("Trades", "total_trades", "d"),
        ("Sharpe", "sharpe", "+.2f"),
        ("MaxDD %", "max_dd_pct", "+.2f"),
        ("Prof Factor", "profit_factor", ".2f"),
        ("Status", "status", "s"),
    ]

    print()
    print(f"  {'=' * (width - 2)}")
    print(f"  STRATEGY: {strategy_name.upper()}")
    print(f"  {'=' * (width - 2)}")

    for metric_label, metric_attr, fmt in metrics:
        print()
        print(f"  [{metric_label}]")
        print(_header_row(param_labels))
        print(sep)
        for symbol in sorted(all_results.keys()):
            row_data = all_results[symbol]
            print(_metric_row(metric_attr, symbol, row_data, fmt))

    # Per-param summary (avg return and GO count)
    print()
    print(f"  [PARAM-SET SUMMARY]")
    print(_header_row(param_labels))
    print(sep)
    for metric_label, metric_attr, fmt in [
        ("Avg Return %", "return_pct", "+.2f"),
        ("GO count", "status", ""),
    ]:
        left = f"  {metric_label:<12s}"
        cols_parts = []
        for lbl in param_labels:
            valid = [
                all_results[sym][lbl]
                for sym in all_results
                if all_results[sym][lbl] is not None
            ]
            if metric_attr == "status":
                go_n = sum(1 for r in valid if r.status == "GO")  # type: ignore[union-attr]
                cols_parts.append(f"  {f'{go_n}/{len(valid)}':>{_COL_W}s}")
            else:
                vals = [getattr(r, metric_attr) for r in valid]
                avg = np.mean(vals) if vals else float("nan")
                cols_parts.append(f"  {format(avg, '+.2f'):>{_COL_W}s}")
        print(left + "".join(cols_parts))

    print(f"  {'=' * (width - 2)}")


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    engine = BacktestEngine(
        initial_capital=INITIAL_CAPITAL,
        commission_pct=COMMISSION_PCT,
        regime_filter=True,
    )

    # ── Fetch data (cached per symbol+timeframe) ──────────────────────────
    print("=" * 70)
    print("  ATLAS RESURRECTION TEST — momentum_exhaustion & multi_timeframe")
    print("=" * 70)
    print(f"  Capital: ${INITIAL_CAPITAL:,.0f} | Commission: {COMMISSION_PCT * 100:.1f}%")
    print(f"  Symbols: {', '.join(CRYPTO_SYMBOLS)}")
    print()

    data_1h: dict[str, pd.DataFrame] = {}
    data_4h: dict[str, pd.DataFrame] = {}

    print("  Fetching live Kraken data...")
    for symbol in CRYPTO_SYMBOLS:
        print(f"    {symbol} 1h (2000 bars)...", end=" ", flush=True)
        df1 = fetch_kraken_ohlcv(symbol, "1h", 2000)
        if df1 is not None:
            data_1h[symbol] = df1
            print(f"OK ({len(df1)} bars)")
        else:
            print("FAILED — symbol skipped")

        print(f"    {symbol} 4h (1000 bars)...", end=" ", flush=True)
        df4 = fetch_kraken_ohlcv(symbol, "4h", 1000)
        if df4 is not None:
            data_4h[symbol] = df4
            print(f"OK ({len(df4)} bars)")
        else:
            print("FAILED — symbol skipped")

        time.sleep(0.3)  # Rate-limit courtesy pause

    # ── momentum_exhaustion ───────────────────────────────────────────────
    exh_param_labels = [label for label, _ in EXHAUSTION_PARAM_SETS]
    # all_results[symbol][param_label] = ResurrectResult | None
    exh_results: dict[str, dict[str, ResurrectResult | None]] = {}

    print()
    print("  Running momentum_exhaustion backtests...")

    for symbol, df in data_1h.items():
        exh_results[symbol] = {}
        for label, override_params in EXHAUSTION_PARAM_SETS:
            print(f"    {symbol} [{label}]...", end=" ", flush=True)
            res = run_param_set(
                "momentum_exhaustion", label, override_params, df, engine
            )
            exh_results[symbol][label] = res
            if res is not None:
                status_tag = "GO" if res.status == "GO" else "NO-GO"
                print(
                    f"{status_tag}  Ret:{res.return_pct:+.2f}%  "
                    f"WR:{res.win_rate:.1f}%  T:{res.total_trades}  "
                    f"Sharpe:{res.sharpe:+.2f}"
                )
            else:
                print("FAILED")

    print_strategy_table("momentum_exhaustion", exh_param_labels, exh_results)

    # ── multi_timeframe ───────────────────────────────────────────────────
    mtf_param_labels = [label for label, _ in MTF_PARAM_SETS]
    mtf_results: dict[str, dict[str, ResurrectResult | None]] = {}

    print()
    print("  Running multi_timeframe backtests...")

    for symbol, df in data_4h.items():
        mtf_results[symbol] = {}
        for label, override_params in MTF_PARAM_SETS:
            print(f"    {symbol} [{label}]...", end=" ", flush=True)
            res = run_param_set(
                "multi_timeframe", label, override_params, df, engine
            )
            mtf_results[symbol][label] = res
            if res is not None:
                status_tag = "GO" if res.status == "GO" else "NO-GO"
                print(
                    f"{status_tag}  Ret:{res.return_pct:+.2f}%  "
                    f"WR:{res.win_rate:.1f}%  T:{res.total_trades}  "
                    f"Sharpe:{res.sharpe:+.2f}"
                )
            else:
                print("FAILED")

    print_strategy_table("multi_timeframe", mtf_param_labels, mtf_results)

    # ── Final verdict ─────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  RESURRECTION VERDICT")
    print("=" * 70)

    def best_variant(
        all_res: dict[str, dict[str, ResurrectResult | None]],
        labels: list[str],
    ) -> tuple[str, float, int]:
        """Return (best_label, avg_return, go_count) across all symbols."""
        best_lbl = ""
        best_avg = float("-inf")
        best_go = 0
        for lbl in labels:
            valid = [
                all_res[sym][lbl]
                for sym in all_res
                if all_res[sym].get(lbl) is not None
            ]
            if not valid:
                continue
            avg_ret = float(np.mean([r.return_pct for r in valid]))  # type: ignore[union-attr]
            go_n = sum(1 for r in valid if r.status == "GO")  # type: ignore[union-attr]
            if avg_ret > best_avg:
                best_avg = avg_ret
                best_lbl = lbl
                best_go = go_n
        return best_lbl, best_avg, best_go

    exh_best_lbl, exh_best_avg, exh_best_go = best_variant(
        exh_results, exh_param_labels
    )
    mtf_best_lbl, mtf_best_avg, mtf_best_go = best_variant(
        mtf_results, mtf_param_labels
    )
    n_syms = len(CRYPTO_SYMBOLS)

    print()
    print(f"  momentum_exhaustion — best variant: [{exh_best_lbl}]")
    print(f"    Avg return: {exh_best_avg:+.2f}%  |  GO: {exh_best_go}/{n_syms}")
    if exh_best_avg > 0 and exh_best_go >= 4:
        print("    VERDICT: RESURRECT — update strategies.yaml with these params")
    elif exh_best_avg > 0 and exh_best_go >= 2:
        print("    VERDICT: PARTIAL — profitable but not across enough symbols")
    else:
        print("    VERDICT: STILL DEAD — signal logic needs fundamental rework")

    print()
    print(f"  multi_timeframe — best variant: [{mtf_best_lbl}]")
    print(f"    Avg return: {mtf_best_avg:+.2f}%  |  GO: {mtf_best_go}/{n_syms}")
    if mtf_best_avg > 0 and mtf_best_go >= 4:
        print("    VERDICT: RESURRECT — update strategies.yaml with these params")
    elif mtf_best_avg > 0 and mtf_best_go >= 2:
        print("    VERDICT: PARTIAL — profitable but not across enough symbols")
    else:
        print("    VERDICT: STILL DEAD — trend-follower may need regime-gating only")

    print()
    print("=" * 70)
    print("  Resurrection test complete.")
    print("=" * 70)


if __name__ == "__main__":
    start = time.time()
    main()
    elapsed = time.time() - start
    print(f"\n  [Test took {elapsed:.1f}s]")
