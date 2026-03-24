#!/usr/bin/env python3
"""
ATLAS — Fresh Crypto Validation Run (2026-03-20)
=================================================
Due diligence validation of ALL 4 enabled crypto strategies on live Kraken data.

Strategies tested:
  - smart_money:       ETH/USDT, XRP/USDT, SOL/USDT, DOGE/USDT, AVAX/USDT
  - donchian_breakout: ETH/USDT, SOL/USDT, ADA/USDT, DOT/USDT, XRP/USDT, AVAX/USDT, ATOM/USDT
  - multi_timeframe:   DOGE/USDT, XRP/USDT
  - volume_profile:    AVAX/USDT, BTC/USDT, XRP/USDT, DOGE/USDT

Risk profiles per symbol: conservative, aggressive, daredevil
Data: 1000 bars × 4h from Kraken (free, no API key)
Engine: BacktestEngine(initial_capital=10000, commission_pct=0.001, regime_filter=True, scale_out_tiers=[])
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import ccxt
import pandas as pd

from backtesting.engine import BacktestEngine
from strategies import StrategyRegistry

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TIMEFRAME = "4h"
BARS = 1000
INITIAL_CAPITAL = 10_000
COMMISSION_PCT = 0.001
FETCH_DELAY_SEC = 1.2  # Rate-limit politeness for Kraken

# Strategy → symbols mapping (from strategies.yaml, enabled=true only)
STRATEGY_SYMBOLS: dict[str, list[str]] = {
    "smart_money": ["ETH/USDT", "XRP/USDT", "SOL/USDT", "DOGE/USDT", "AVAX/USDT"],
    "donchian_breakout": ["ETH/USDT", "SOL/USDT", "ADA/USDT", "DOT/USDT", "XRP/USDT", "AVAX/USDT", "ATOM/USDT"],
    "multi_timeframe": ["DOGE/USDT", "XRP/USDT"],
    "volume_profile": ["AVAX/USDT", "BTC/USDT", "XRP/USDT", "DOGE/USDT"],
}

# Risk profiles: override atr_stop_mult and rr_ratio
RISK_PROFILES: dict[str, dict[str, float]] = {
    "conservative": {"atr_stop_mult": 2.0, "rr_ratio": 3.0},
    "aggressive":   {"atr_stop_mult": 1.5, "rr_ratio": 4.0},
    "daredevil":    {"atr_stop_mult": 1.0, "rr_ratio": 5.0},
}

# Strategy-specific constructor kwargs from strategies.yaml
STRATEGY_PARAMS: dict[str, dict] = {
    "smart_money": dict(
        swing_lookback=5, ob_lookback=50, fvg_min_size_atr_ratio=0.15,
        bos_lookback=100, ob_entry_tolerance=0.015, atr_period=14,
        atr_stop_mult=2.0, rr_ratio=3.0, volume_period=20,
        min_rr_for_swing_tp=2.0, displacement_atr_mult=1.5,
        displacement_vol_mult=1.2, time_stop_bars=50,
    ),
    "donchian_breakout": dict(
        entry_period=20, exit_period=10, atr_period=14,
        atr_stop_mult=2.0, rr_ratio=3.0, adx_period=14, adx_min=20.0,
        rsi_period=14, rsi_max_long=75.0, rsi_min_short=25.0,
        volume_period=20, volume_mult=1.2, sma_trend_period=200,
    ),
    "multi_timeframe": dict(
        htf_fast_ema=30, htf_slow_ema=100, mtf_ema=10,
        ltf_macd_fast=12, ltf_macd_slow=26, ltf_macd_signal=9,
        ltf_rsi_period=14, ltf_rsi_entry_long=40.0, ltf_rsi_entry_short=60.0,
        atr_period=14, atr_stop_mult=2.0, rr_ratio=2.5, min_confluence=2,
        htf_resample_rule="4h", mtf_resample_rule="1h",
    ),
    "volume_profile": dict(
        profile_window=60, profile_bins=50, rsi_period=14,
        rsi_oversold=35.0, rsi_overbought=65.0, rsi_exit=50.0,
        atr_period=14, atr_stop_mult=1.0, volume_period=20,
        volume_mult=1.0, breakout_vol_mult=1.5, min_volume_mult=1.2,
        hvn_threshold=1.5, lvn_threshold=0.5, poc_trend_bars=10,
        bounce_lookback=30, bounce_tolerance=0.003, adx_period=14,
        adx_min_trend=10.0, min_distance_atr=0.3, min_rr=1.5,
    ),
}

# Previous results for regime-shift detection (from strategies.yaml comments)
PREVIOUS_RESULTS: dict[str, float] = {
    # smart_money
    "smart_money|ETH/USDT": +2.08,
    "smart_money|XRP/USDT": +2.16,
    "smart_money|SOL/USDT": +1.29,
    "smart_money|DOGE/USDT": +3.41,
    "smart_money|AVAX/USDT": +0.73,
    # donchian_breakout
    "donchian_breakout|ETH/USDT": +2.04,
    "donchian_breakout|SOL/USDT": +2.76,
    "donchian_breakout|ADA/USDT": +0.72,
    "donchian_breakout|DOT/USDT": +5.83,
    "donchian_breakout|XRP/USDT": +4.70,
    "donchian_breakout|AVAX/USDT": +0.10,  # marginal
    "donchian_breakout|ATOM/USDT": +14.56,
    # multi_timeframe
    "multi_timeframe|DOGE/USDT": +7.46,
    "multi_timeframe|XRP/USDT": +13.75,
    # volume_profile
    "volume_profile|AVAX/USDT": +4.37,
    "volume_profile|BTC/USDT": +2.14,
    "volume_profile|XRP/USDT": +2.43,
    "volume_profile|DOGE/USDT": +0.50,
}

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

_exchange = ccxt.kraken({"enableRateLimit": True})
_data_cache: dict[str, pd.DataFrame] = {}


def fetch_ohlcv(symbol: str) -> pd.DataFrame | None:
    """Fetch 1000 bars of 4h data from Kraken. Cached per symbol."""
    if symbol in _data_cache:
        return _data_cache[symbol]

    time.sleep(FETCH_DELAY_SEC)
    try:
        raw = _exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=BARS)
    except ccxt.BadSymbol:
        print(f"  [SKIP] {symbol} -- not available on Kraken")
        return None
    except Exception as exc:
        print(f"  [ERROR] {symbol} -- fetch failed: {exc}")
        return None

    if not raw or len(raw) < 50:
        print(f"  [SKIP] {symbol} -- insufficient data ({len(raw) if raw else 0} bars)")
        return None

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df = df.astype(float)

    _data_cache[symbol] = df
    print(f"  [OK] {symbol}: {len(df)} bars, {df.index[0].date()} -> {df.index[-1].date()}")
    return df


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    strategy: str
    symbol: str
    profile: str
    return_pct: float
    win_rate: float
    sharpe: float
    max_dd: float
    profit_factor: float
    trades: int
    prev_return: float | None
    regime_shift: bool  # True if was profitable, now losing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 80)
    print("  ATLAS -- Fresh Crypto Validation Run")
    print(f"  Date: 2026-03-20  |  Data: Kraken {TIMEFRAME} x {BARS} bars")
    print(f"  Capital: ${INITIAL_CAPITAL:,.0f}  |  Commission: {COMMISSION_PCT*100:.1f}%")
    print(f"  Scale-out: DISABLED  |  Regime filter: ON")
    print("=" * 80)

    # Collect all unique symbols needed
    all_symbols = sorted(set(
        sym for syms in STRATEGY_SYMBOLS.values() for sym in syms
    ))

    print(f"\n--- Fetching data for {len(all_symbols)} symbols ---")
    for sym in all_symbols:
        fetch_ohlcv(sym)

    # Run backtests
    engine = BacktestEngine(
        initial_capital=INITIAL_CAPITAL,
        commission_pct=COMMISSION_PCT,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # Disabled — empirically proven to hurt returns
    )

    results: list[RunResult] = []
    total_tests = sum(len(syms) for syms in STRATEGY_SYMBOLS.values()) * len(RISK_PROFILES)
    test_num = 0

    for strat_name, symbols in STRATEGY_SYMBOLS.items():
        print(f"\n{'='*60}")
        print(f"  Strategy: {strat_name}")
        print(f"{'='*60}")

        base_params = STRATEGY_PARAMS[strat_name].copy()

        for symbol in symbols:
            df = fetch_ohlcv(symbol)
            if df is None:
                for profile_name in RISK_PROFILES:
                    test_num += 1
                    results.append(RunResult(
                        strategy=strat_name, symbol=symbol, profile=profile_name,
                        return_pct=0.0, win_rate=0.0, sharpe=0.0, max_dd=0.0,
                        profit_factor=0.0, trades=0, prev_return=None, regime_shift=False,
                    ))
                continue

            for profile_name, profile_overrides in RISK_PROFILES.items():
                test_num += 1
                params = base_params.copy()
                params.update(profile_overrides)

                try:
                    # volume_profile uses min_rr instead of rr_ratio
                    if strat_name == "volume_profile" and "rr_ratio" in params:
                        params["min_rr"] = params.pop("rr_ratio")
                    strategy = StrategyRegistry.build(strat_name, **params)
                    result = engine.run(df, strategy)

                    ret = result.total_return * 100
                    wr = result.win_rate * 100
                    sharpe = result.sharpe_ratio
                    mdd = result.max_drawdown * 100
                    pf = result.profit_factor
                    trades = result.total_trades

                    # Check for regime shift
                    key = f"{strat_name}|{symbol}"
                    prev = PREVIOUS_RESULTS.get(key)
                    shift = prev is not None and prev > 0 and ret < 0

                    flag = " *** REGIME SHIFT ***" if shift else ""
                    status = "GO" if ret > 0 else "NO-GO"

                    print(f"  [{test_num:3d}/{total_tests}] {symbol:12s} {profile_name:14s} "
                          f"| {ret:+7.2f}% | WR:{wr:5.1f}% | Sharpe:{sharpe:6.2f} "
                          f"| DD:{mdd:6.2f}% | PF:{pf:5.2f} | Trades:{trades:3d} "
                          f"| {status}{flag}")

                    results.append(RunResult(
                        strategy=strat_name, symbol=symbol, profile=profile_name,
                        return_pct=ret, win_rate=wr, sharpe=sharpe, max_dd=mdd,
                        profit_factor=pf, trades=trades, prev_return=prev,
                        regime_shift=shift,
                    ))

                except Exception as exc:
                    print(f"  [{test_num:3d}/{total_tests}] {symbol:12s} {profile_name:14s} "
                          f"| ERROR: {exc}")
                    results.append(RunResult(
                        strategy=strat_name, symbol=symbol, profile=profile_name,
                        return_pct=0.0, win_rate=0.0, sharpe=0.0, max_dd=0.0,
                        profit_factor=0.0, trades=0, prev_return=None, regime_shift=False,
                    ))

    # ---------------------------------------------------------------------------
    # Summary tables
    # ---------------------------------------------------------------------------

    print("\n\n")
    print("=" * 120)
    print("  COMPREHENSIVE RESULTS — Sorted by Return (Descending)")
    print("=" * 120)
    print(f"  {'Strategy':<22s} {'Symbol':<12s} {'Profile':<14s} "
          f"{'Return':>8s} {'WinRate':>8s} {'Sharpe':>8s} {'MaxDD':>8s} "
          f"{'PF':>7s} {'Trades':>7s} {'Prev':>8s} {'Status':>8s} {'Shift':>12s}")
    print("-" * 120)

    sorted_results = sorted(results, key=lambda r: r.return_pct, reverse=True)

    for r in sorted_results:
        status = "GO" if r.return_pct > 0 and r.trades > 0 else "NO-GO"
        prev_str = f"{r.prev_return:+.2f}%" if r.prev_return is not None else "N/A"
        shift_str = "SHIFT!" if r.regime_shift else ""
        print(f"  {r.strategy:<22s} {r.symbol:<12s} {r.profile:<14s} "
              f"{r.return_pct:+7.2f}% {r.win_rate:7.1f}% {r.sharpe:8.2f} {r.max_dd:7.2f}% "
              f"{r.profit_factor:7.2f} {r.trades:7d} {prev_str:>8s} {status:>8s} {shift_str:>12s}")

    # ---------------------------------------------------------------------------
    # Best profile per strategy-symbol
    # ---------------------------------------------------------------------------

    print("\n\n")
    print("=" * 100)
    print("  BEST PROFILE PER STRATEGY-SYMBOL PAIR")
    print("=" * 100)
    print(f"  {'Strategy':<22s} {'Symbol':<12s} {'Best Profile':<14s} "
          f"{'Return':>8s} {'Sharpe':>8s} {'Trades':>7s} {'Prev':>8s} {'Shift':>12s}")
    print("-" * 100)

    # Group by strategy+symbol, pick best by return
    from itertools import groupby
    keyfn = lambda r: (r.strategy, r.symbol)
    sorted_by_key = sorted(results, key=keyfn)

    best_results: list[RunResult] = []
    for key, group in groupby(sorted_by_key, key=keyfn):
        group_list = list(group)
        best = max(group_list, key=lambda r: r.return_pct)
        best_results.append(best)

    best_results.sort(key=lambda r: r.return_pct, reverse=True)
    go_count = sum(1 for r in best_results if r.return_pct > 0 and r.trades > 0)
    shift_count = sum(1 for r in best_results if r.regime_shift)

    for r in best_results:
        status = "GO" if r.return_pct > 0 and r.trades > 0 else "NO-GO"
        prev_str = f"{r.prev_return:+.2f}%" if r.prev_return is not None else "N/A"
        shift_str = "SHIFT!" if r.regime_shift else ""
        print(f"  {r.strategy:<22s} {r.symbol:<12s} {r.profile:<14s} "
              f"{r.return_pct:+7.2f}% {r.sharpe:8.2f} {r.trades:7d} {prev_str:>8s} {shift_str:>12s}")

    print(f"\n  Total pairs: {len(best_results)}  |  GO: {go_count}  |  NO-GO: {len(best_results) - go_count}")
    print(f"  Regime shifts detected: {shift_count}")

    # ---------------------------------------------------------------------------
    # Strategy-level summary
    # ---------------------------------------------------------------------------

    print("\n\n")
    print("=" * 80)
    print("  STRATEGY-LEVEL SUMMARY (best profile per symbol, averaged)")
    print("=" * 80)

    for strat_name in STRATEGY_SYMBOLS:
        strat_bests = [r for r in best_results if r.strategy == strat_name]
        if not strat_bests:
            continue
        avg_ret = sum(r.return_pct for r in strat_bests) / len(strat_bests)
        avg_wr = sum(r.win_rate for r in strat_bests) / len(strat_bests)
        avg_sharpe = sum(r.sharpe for r in strat_bests) / len(strat_bests)
        go = sum(1 for r in strat_bests if r.return_pct > 0 and r.trades > 0)
        shifts = sum(1 for r in strat_bests if r.regime_shift)
        print(f"  {strat_name:<22s} | Avg Return: {avg_ret:+.2f}% | Avg WR: {avg_wr:.1f}% "
              f"| Avg Sharpe: {avg_sharpe:.2f} | GO: {go}/{len(strat_bests)} | Shifts: {shifts}")

    # ---------------------------------------------------------------------------
    # Regime shift alerts
    # ---------------------------------------------------------------------------

    shifts = [r for r in best_results if r.regime_shift]
    if shifts:
        print("\n\n")
        print("!" * 80)
        print("  REGIME SHIFT ALERTS — Previously profitable, now LOSING")
        print("!" * 80)
        for r in shifts:
            print(f"  {r.strategy:<22s} {r.symbol:<12s} | Was: {r.prev_return:+.2f}% -> Now: {r.return_pct:+.2f}% "
                  f"({r.profile})")
        print("!" * 80)
    else:
        print("\n  No regime shifts detected. All previously profitable pairs remain directionally consistent.")

    print("\n  Atlas validation complete.")


if __name__ == "__main__":
    main()
