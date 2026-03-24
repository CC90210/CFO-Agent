"""
run_full_portfolio_test.py — Comprehensive portfolio backtest on live Kraken data.

Tests:
  1. All 3 enabled strategies (smart_money, donchian_breakout, multi_timeframe)
     on their configured symbols with conservative AND optimal risk profiles.
  2. 10 additional crypto symbols (LINK, MATIC, ATOM, FIL, NEAR, APE, OP, ARB, INJ, SUI)
     tested against all 3 strategies with aggressive and daredevil params.

Data source : ccxt.kraken — free, no API key required.
Bars        : 1000 × 4h candles per symbol.
Engine      : BacktestEngine(initial_capital=10000, commission_pct=0.001, regime_filter=True)
              scale_out_tiers=[] (disabled — empirically shown to hurt returns)
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Any

# ── Windows encoding fix ─────────────────────────────────────────────────────
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Path bootstrap ────────────────────────────────────────────────────────────
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# ── Imports ───────────────────────────────────────────────────────────────────
import ccxt
import pandas as pd

from backtesting.engine import BacktestEngine, BacktestResult
from strategies.base import BaseStrategy
from strategies.technical.smart_money import SmartMoneyStrategy
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.technical.multi_timeframe import MultiTimeframeStrategy

# ── Trigger full strategy registration (required for BaseStrategy.__subclasses__) ──
import strategies.technical  # noqa: F401 — side-effect import

# =============================================================================
# Constants
# =============================================================================

BARS = 1000
TIMEFRAME = "4h"
INITIAL_CAPITAL = 10_000.0
COMMISSION = 0.001

# Fetch-rate limiting: Kraken rate-limits unauthenticated calls.
# A small sleep between fetches avoids 429 errors on bulk runs.
_FETCH_DELAY_SEC = 0.4


# =============================================================================
# Risk profiles
# =============================================================================

# Conservative — matches strategies.yaml defaults
_CONSERVATIVE = {
    "atr_stop_mult": 2.0,
    "rr_ratio": 3.0,
}

# Aggressive — empirically validated on live Kraken data (2026-03-20)
_AGGRESSIVE = {
    "atr_stop_mult": 1.5,
    "rr_ratio": 4.0,
}

# Daredevil — tightest stop, widest target
_DAREDEVIL = {
    "atr_stop_mult": 1.0,
    "rr_ratio": 5.0,
}


# =============================================================================
# Strategy factories
# =============================================================================

# Exact params from config/strategies.yaml
_SMART_MONEY_BASE: dict[str, Any] = {
    "swing_lookback": 5,
    "ob_lookback": 50,
    "fvg_min_size_atr_ratio": 0.15,
    "bos_lookback": 100,
    "ob_entry_tolerance": 0.015,
    "atr_period": 14,
    "atr_stop_mult": 2.0,
    "rr_ratio": 3.0,
    "volume_period": 20,
    "min_rr_for_swing_tp": 2.0,
    "displacement_atr_mult": 1.5,
    "displacement_vol_mult": 1.2,
    "time_stop_bars": 50,
}

_DONCHIAN_BASE: dict[str, Any] = {
    "entry_period": 20,
    "exit_period": 10,
    "atr_period": 14,
    "atr_stop_mult": 2.0,
    "rr_ratio": 3.0,
    "adx_period": 14,
    "adx_min": 20.0,
    "rsi_period": 14,
    "rsi_max_long": 75.0,
    "rsi_min_short": 25.0,
    "volume_period": 20,
    "volume_mult": 1.2,
    "sma_trend_period": 200,
}

_MULTI_TF_BASE: dict[str, Any] = {
    "htf_fast_ema": 30,
    "htf_slow_ema": 100,
    "mtf_ema": 10,
    "ltf_macd_fast": 12,
    "ltf_macd_slow": 26,
    "ltf_macd_signal": 9,
    "ltf_rsi_period": 14,
    "ltf_rsi_entry_long": 40.0,
    "ltf_rsi_entry_short": 60.0,
    "atr_period": 14,
    "atr_stop_mult": 2.0,
    "rr_ratio": 2.5,
    "min_confluence": 2,
    "htf_resample_rule": "4h",
    "mtf_resample_rule": "1h",
}


def _make_smart_money(profile: dict[str, Any]) -> SmartMoneyStrategy:
    params = {**_SMART_MONEY_BASE, **profile}
    return SmartMoneyStrategy(**params)


def _make_donchian(profile: dict[str, Any]) -> DonchianBreakoutStrategy:
    params = {**_DONCHIAN_BASE, **profile}
    return DonchianBreakoutStrategy(**params)


def _make_multi_tf(profile: dict[str, Any]) -> MultiTimeframeStrategy:
    params = {**_MULTI_TF_BASE, **profile}
    return MultiTimeframeStrategy(**params)


# =============================================================================
# Test plan
# =============================================================================

@dataclass
class TestCase:
    symbol: str
    strategy_name: str
    profile_name: str
    strategy: BaseStrategy


def build_configured_test_cases() -> list[TestCase]:
    """
    Part 1: Enabled strategies on their configured symbols.
    Tests conservative profile for all symbols, plus the empirically-validated
    optimal profile documented in strategies.yaml comments.
    """
    cases: list[TestCase] = []

    # ── smart_money ──────────────────────────────────────────────────────────
    sm_symbols = [
        ("ETH/USDT", "conservative"),
        ("XRP/USDT", "conservative"),
        ("SOL/USDT", "conservative"),
        ("DOGE/USDT", "aggressive"),   # optimal per yaml comment
        ("AVAX/USDT", "conservative"),
    ]
    for sym, optimal in sm_symbols:
        # Always test conservative
        cases.append(TestCase(sym, "smart_money", "conservative", _make_smart_money(_CONSERVATIVE)))
        # Also test the optimal profile if it differs
        if optimal != "conservative":
            profile = _AGGRESSIVE if optimal == "aggressive" else _DAREDEVIL
            cases.append(TestCase(sym, "smart_money", optimal, _make_smart_money(profile)))

    # ── donchian_breakout ────────────────────────────────────────────────────
    donchian_symbols = [
        ("ETH/USDT", "conservative"),
        ("SOL/USDT", "aggressive"),    # optimal per yaml comment
        ("ADA/USDT", "conservative"),
        ("DOT/USDT", "daredevil"),     # optimal per yaml comment
        ("XRP/USDT", "aggressive"),    # optimal per yaml comment
        ("AVAX/USDT", "conservative"),
    ]
    for sym, optimal in donchian_symbols:
        cases.append(TestCase(sym, "donchian_breakout", "conservative", _make_donchian(_CONSERVATIVE)))
        if optimal != "conservative":
            profile = _AGGRESSIVE if optimal == "aggressive" else _DAREDEVIL
            cases.append(TestCase(sym, "donchian_breakout", optimal, _make_donchian(profile)))

    # ── multi_timeframe ──────────────────────────────────────────────────────
    # All three profitable symbols from yaml; the yaml params ARE the aggressive
    # configuration (30/100 EMA). We test those as "optimal" and also a more
    # conservative stop variant.
    mtf_symbols = ["DOGE/USDT", "DOT/USDT", "XRP/USDT"]
    for sym in mtf_symbols:
        # The yaml params use atr_stop_mult=2.0, rr_ratio=2.5 (already aggressive EMAs)
        cases.append(TestCase(sym, "multi_timeframe", "conservative", _make_multi_tf(_CONSERVATIVE)))
        cases.append(TestCase(sym, "multi_timeframe", "aggressive",
                              _make_multi_tf({**_MULTI_TF_BASE, **_AGGRESSIVE})))

    return cases


def build_discovery_test_cases() -> list[TestCase]:
    """
    Part 2: 10 new symbols tested against all 3 strategies with aggressive
    and daredevil risk profiles to find breakout opportunities.
    """
    new_symbols = [
        "LINK/USDT",
        "MATIC/USDT",
        "ATOM/USDT",
        "FIL/USDT",
        "NEAR/USDT",
        "APE/USDT",
        "OP/USDT",
        "ARB/USDT",
        "INJ/USDT",
        "SUI/USDT",
    ]

    cases: list[TestCase] = []
    for sym in new_symbols:
        for profile_name, profile in [("aggressive", _AGGRESSIVE), ("daredevil", _DAREDEVIL)]:
            cases.append(TestCase(sym, "smart_money", profile_name, _make_smart_money(profile)))
            cases.append(TestCase(sym, "donchian_breakout", profile_name, _make_donchian(profile)))
            cases.append(TestCase(sym, "multi_timeframe", profile_name,
                                  _make_multi_tf({**_MULTI_TF_BASE, **profile})))
    return cases


# =============================================================================
# Data fetching
# =============================================================================

_exchange = ccxt.kraken({"enableRateLimit": True})
_data_cache: dict[str, pd.DataFrame] = {}


def fetch_ohlcv(symbol: str) -> pd.DataFrame | None:
    """Fetch 1000 bars of 4h data from Kraken. Results are cached per symbol."""
    if symbol in _data_cache:
        return _data_cache[symbol]

    time.sleep(_FETCH_DELAY_SEC)
    try:
        raw = _exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=BARS)
    except ccxt.BadSymbol:
        print(f"  [SKIP] {symbol} — not available on Kraken")
        return None
    except Exception as exc:  # noqa: BLE001 — broad catch for network errors
        print(f"  [ERROR] {symbol} — fetch failed: {exc}")
        return None

    if not raw or len(raw) < 50:
        print(f"  [SKIP] {symbol} — insufficient data ({len(raw) if raw else 0} bars)")
        return None

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df = df.set_index("timestamp").sort_index()
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
    df.attrs["symbol"] = symbol

    _data_cache[symbol] = df
    return df


# =============================================================================
# Result container
# =============================================================================

@dataclass
class RunResult:
    symbol: str
    strategy: str
    profile: str
    total_return_pct: float
    win_rate_pct: float
    total_trades: int
    sharpe: float
    max_drawdown_pct: float
    profit_factor: float
    verdict: str   # GO / MARGINAL / NO-GO / NO-DATA


_ENGINE = BacktestEngine(
    initial_capital=INITIAL_CAPITAL,
    commission_pct=COMMISSION,
    regime_filter=True,
    scale_out_tiers=[],   # Disabled — empirically shown to hurt returns (see strategies.yaml note)
)


def _verdict(ret: float, trades: int, win_rate: float) -> str:
    if trades == 0:
        return "NO-DATA"
    if ret >= 2.0 and win_rate >= 45.0:
        return "GO"
    if ret >= 0.0:
        return "MARGINAL"
    return "NO-GO"


def run_case(case: TestCase) -> RunResult | None:
    """Fetch data, attach symbol attr, run backtest, return RunResult."""
    df = fetch_ohlcv(case.symbol)
    if df is None:
        return RunResult(
            symbol=case.symbol,
            strategy=case.strategy_name,
            profile=case.profile_name,
            total_return_pct=0.0,
            win_rate_pct=0.0,
            total_trades=0,
            sharpe=0.0,
            max_drawdown_pct=0.0,
            profit_factor=0.0,
            verdict="NO-DATA",
        )

    # Ensure symbol attr is set (required by SmartMoneyStrategy)
    df.attrs["symbol"] = case.symbol

    try:
        result: BacktestResult = _ENGINE.run(df, case.strategy)
    except Exception as exc:  # noqa: BLE001 — surface strategy errors without aborting the whole run
        print(f"  [ERROR] {case.symbol} / {case.strategy_name} / {case.profile_name} — {exc}")
        return RunResult(
            symbol=case.symbol,
            strategy=case.strategy_name,
            profile=case.profile_name,
            total_return_pct=0.0,
            win_rate_pct=0.0,
            total_trades=0,
            sharpe=0.0,
            max_drawdown_pct=0.0,
            profit_factor=0.0,
            verdict="NO-DATA",
        )

    ret_pct = result.total_return * 100.0
    wr_pct = result.win_rate * 100.0

    return RunResult(
        symbol=case.symbol,
        strategy=case.strategy_name,
        profile=case.profile_name,
        total_return_pct=ret_pct,
        win_rate_pct=wr_pct,
        total_trades=result.total_trades,
        sharpe=result.sharpe_ratio,
        max_drawdown_pct=result.max_drawdown * 100.0,
        profit_factor=result.profit_factor,
        verdict=_verdict(ret_pct, result.total_trades, wr_pct),
    )


# =============================================================================
# Display helpers
# =============================================================================

_COL_W = {
    "symbol": 13,
    "strategy": 20,
    "profile": 13,
    "return": 9,
    "wr": 7,
    "trades": 7,
    "sharpe": 8,
    "mdd": 8,
    "pf": 6,
    "verdict": 9,
}


def _header() -> str:
    return (
        f"{'Symbol':<{_COL_W['symbol']}} "
        f"{'Strategy':<{_COL_W['strategy']}} "
        f"{'Profile':<{_COL_W['profile']}} "
        f"{'Return':>{_COL_W['return']}} "
        f"{'WR%':>{_COL_W['wr']}} "
        f"{'Trades':>{_COL_W['trades']}} "
        f"{'Sharpe':>{_COL_W['sharpe']}} "
        f"{'MaxDD%':>{_COL_W['mdd']}} "
        f"{'PF':>{_COL_W['pf']}} "
        f"{'Verdict':<{_COL_W['verdict']}}"
    )


def _row(r: RunResult) -> str:
    pf_str = f"{r.profit_factor:.2f}" if r.profit_factor != float("inf") else "  inf"
    return (
        f"{r.symbol:<{_COL_W['symbol']}} "
        f"{r.strategy:<{_COL_W['strategy']}} "
        f"{r.profile:<{_COL_W['profile']}} "
        f"{r.total_return_pct:>+{_COL_W['return']}.2f}% "
        f"{r.win_rate_pct:>{_COL_W['wr']}.1f}% "
        f"{r.total_trades:>{_COL_W['trades']}} "
        f"{r.sharpe:>{_COL_W['sharpe']}.2f} "
        f"{r.max_drawdown_pct:>+{_COL_W['mdd']}.2f}% "
        f"{pf_str:>{_COL_W['pf']}} "
        f"{r.verdict:<{_COL_W['verdict']}}"
    )


def _separator() -> str:
    total = sum(_COL_W.values()) + len(_COL_W) - 1
    return "-" * total


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    print()
    print("=" * 80)
    print("  ATLAS — Full Portfolio Backtest (Live Kraken Data, 4h, 1000 bars)")
    print("  Scale-out DISABLED | Regime filter ON | Commission 0.1%")
    print("=" * 80)

    # ── Part 1: Configured strategy / symbol pairs ────────────────────────────
    configured_cases = build_configured_test_cases()
    # ── Part 2: Discovery pass on new symbols ─────────────────────────────────
    discovery_cases = build_discovery_test_cases()

    all_cases = configured_cases + discovery_cases
    total = len(all_cases)

    print(f"\n  Total test cases: {total}")
    print(f"    Configured pairs : {len(configured_cases)}")
    print(f"    Discovery pairs  : {len(discovery_cases)}")
    print()

    configured_results: list[RunResult] = []
    discovery_results: list[RunResult] = []

    # ── Run configured cases ──────────────────────────────────────────────────
    print(">>> PART 1 — Configured strategies on known symbols")
    print()

    prev_symbol = ""
    for idx, case in enumerate(configured_cases, 1):
        if case.symbol != prev_symbol:
            print(f"  Fetching {case.symbol} from Kraken ...")
            prev_symbol = case.symbol
        print(f"  [{idx:>3}/{len(configured_cases)}] {case.symbol:<14} {case.strategy_name:<22} {case.profile_name}", end=" ... ", flush=True)
        r = run_case(case)
        if r:
            configured_results.append(r)
            print(f"{r.total_return_pct:>+.2f}%  {r.verdict}")
        else:
            print("SKIPPED")

    # ── Run discovery cases ───────────────────────────────────────────────────
    print()
    print(">>> PART 2 — Discovery pass on new symbols (all 3 strategies)")
    print()

    prev_symbol = ""
    for idx, case in enumerate(discovery_cases, 1):
        if case.symbol != prev_symbol:
            print(f"  Fetching {case.symbol} from Kraken ...")
            prev_symbol = case.symbol
        print(f"  [{idx:>3}/{len(discovery_cases)}] {case.symbol:<14} {case.strategy_name:<22} {case.profile_name}", end=" ... ", flush=True)
        r = run_case(case)
        if r:
            discovery_results.append(r)
            print(f"{r.total_return_pct:>+.2f}%  {r.verdict}")
        else:
            print("SKIPPED")

    all_results = configured_results + discovery_results

    # =========================================================================
    # Summary tables
    # =========================================================================

    _print_summary_table("PART 1 — Configured Strategies", configured_results)
    _print_summary_table("PART 2 — Discovery (New Symbols)", discovery_results)
    _print_go_signals(all_results)
    _print_aggregate_stats(all_results)


def _print_summary_table(title: str, results: list[RunResult]) -> None:
    if not results:
        return
    print()
    print("=" * 80)
    print(f"  {title}")
    print("=" * 80)
    print(_header())
    print(_separator())

    # Sort: GO first, then by return descending
    order = {"GO": 0, "MARGINAL": 1, "NO-GO": 2, "NO-DATA": 3}
    for r in sorted(results, key=lambda x: (order.get(x.verdict, 9), -x.total_return_pct)):
        print(_row(r))

    print(_separator())


def _print_go_signals(results: list[RunResult]) -> None:
    go_list = [r for r in results if r.verdict == "GO"]
    if not go_list:
        print("\n  No GO signals found in this run.")
        return

    print()
    print("=" * 80)
    print("  *** GO SIGNALS — Add to production config ***")
    print("=" * 80)
    print(_header())
    print(_separator())
    for r in sorted(go_list, key=lambda x: -x.total_return_pct):
        print(_row(r))
    print(_separator())
    print(f"\n  Total GO signals: {len(go_list)}")


def _print_aggregate_stats(results: list[RunResult]) -> None:
    tradeable = [r for r in results if r.total_trades > 0]
    if not tradeable:
        return

    go_count = sum(1 for r in results if r.verdict == "GO")
    marginal_count = sum(1 for r in results if r.verdict == "MARGINAL")
    nogo_count = sum(1 for r in results if r.verdict == "NO-GO")
    nodata_count = sum(1 for r in results if r.verdict == "NO-DATA")
    avg_ret = sum(r.total_return_pct for r in tradeable) / len(tradeable)
    avg_wr = sum(r.win_rate_pct for r in tradeable) / len(tradeable)
    best = max(tradeable, key=lambda x: x.total_return_pct)

    print()
    print("=" * 80)
    print("  AGGREGATE SUMMARY")
    print("=" * 80)
    print(f"  Total test cases run     : {len(results)}")
    print(f"  Cases with trades        : {len(tradeable)}")
    print(f"  GO signals               : {go_count}")
    print(f"  MARGINAL                 : {marginal_count}")
    print(f"  NO-GO                    : {nogo_count}")
    print(f"  NO-DATA (skip / 0 trades): {nodata_count}")
    print(f"  Avg return (tradeable)   : {avg_ret:>+.2f}%")
    print(f"  Avg win rate (tradeable) : {avg_wr:>.1f}%")
    print(f"  Best single result       : {best.symbol} / {best.strategy} / {best.profile} -> {best.total_return_pct:>+.2f}%")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
