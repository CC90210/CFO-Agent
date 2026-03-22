#!/usr/bin/env python3
"""
ATLAS — Donchian Breakout Expansion Backtest (2026-03-21)
=========================================================
Tests donchian_breakout on 12 candidate symbols NOT yet in the config.
Also tests smart_money on 3 high-liquidity alts: LINK, LTC, BCH.

Admission criteria (all three must pass):
  return > +1.0%  AND  Sharpe > 0.5  AND  trades >= 5

Profitable symbols are auto-added to:
  1. config/strategies.yaml  (donchian_breakout symbols)
  2. core/risk_profiles.py   (OPTIMAL_PROFILES dict)

Data: 721 bars × 4h from Kraken (approx 120 days of coverage)
Engine: BacktestEngine(regime_filter=True, scale_out_tiers=[], trailing_stops=False)
"""

from __future__ import annotations

import re
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
BARS = 721
INITIAL_CAPITAL = 10_000
COMMISSION_PCT = 0.001
FETCH_DELAY_SEC = 1.2

# Symbols to probe for donchian_breakout
DONCHIAN_CANDIDATES = [
    "LINK/USDT",
    "MATIC/USDT",
    "UNI/USDT",
    "FIL/USDT",
    "NEAR/USDT",
    "ALGO/USDT",
    "ICP/USDT",
    "SAND/USDT",
    "MANA/USDT",
    "LTC/USDT",
    "BCH/USDT",
    "SHIB/USDT",
]

# Additional smart_money candidates (high-liquidity alts with potential SMC edge)
SMART_MONEY_CANDIDATES = [
    "LINK/USDT",
    "LTC/USDT",
    "BCH/USDT",
]

# Risk profiles tested per symbol
RISK_PROFILES: dict[str, dict[str, float]] = {
    "conservative": {"atr_stop_mult": 2.0, "rr_ratio": 3.0},
    "aggressive":   {"atr_stop_mult": 1.5, "rr_ratio": 4.0},
    "daredevil":    {"atr_stop_mult": 1.0, "rr_ratio": 5.0},
}

# Admission thresholds
MIN_RETURN_PCT = 1.0
MIN_SHARPE = 0.5
MIN_TRADES = 5

# Base constructor params (from strategies.yaml, unchanged)
DONCHIAN_PARAMS = dict(
    entry_period=20, exit_period=10, atr_period=14,
    atr_stop_mult=2.0, rr_ratio=3.0, adx_period=14, adx_min=20.0,
    rsi_period=14, rsi_max_long=75.0, rsi_min_short=25.0,
    volume_period=20, volume_mult=1.2, sma_trend_period=200,
)

SMART_MONEY_PARAMS = dict(
    swing_lookback=5, ob_lookback=50, fvg_min_size_atr_ratio=0.15,
    bos_lookback=100, ob_entry_tolerance=0.015, atr_period=14,
    atr_stop_mult=2.0, rr_ratio=3.0, volume_period=20,
    min_rr_for_swing_tp=2.0, displacement_atr_mult=1.5,
    displacement_vol_mult=1.2, time_stop_bars=50,
)


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

_exchange = ccxt.kraken({"enableRateLimit": True})
_data_cache: dict[str, pd.DataFrame] = {}


def fetch_ohlcv(symbol: str) -> pd.DataFrame | None:
    """Fetch BARS bars of 4h data from Kraken. Cached per symbol."""
    if symbol in _data_cache:
        return _data_cache[symbol]

    time.sleep(FETCH_DELAY_SEC)
    try:
        raw = _exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=BARS)
    except ccxt.BadSymbol:
        print(f"  [SKIP] {symbol} -- not listed on Kraken")
        _data_cache[symbol] = None  # type: ignore[assignment]
        return None
    except Exception as exc:
        print(f"  [ERROR] {symbol} -- fetch failed: {exc}")
        return None

    if not raw or len(raw) < 200:
        print(f"  [SKIP] {symbol} -- insufficient bars ({len(raw) if raw else 0})")
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

    @property
    def passes_threshold(self) -> bool:
        return (
            self.return_pct > MIN_RETURN_PCT
            and self.sharpe > MIN_SHARPE
            and self.trades >= MIN_TRADES
        )


# ---------------------------------------------------------------------------
# Core backtest runner
# ---------------------------------------------------------------------------

def run_strategy(
    engine: BacktestEngine,
    strategy_name: str,
    base_params: dict,
    symbol: str,
    df: pd.DataFrame,
) -> list[RunResult]:
    """Run all three risk profiles for one strategy-symbol pair."""
    results: list[RunResult] = []

    for profile_name, overrides in RISK_PROFILES.items():
        params = base_params.copy()
        params.update(overrides)

        try:
            strategy = StrategyRegistry.build(strategy_name, **params)
            result = engine.run(df, strategy)

            ret = result.total_return * 100
            wr = result.win_rate * 100
            sharpe = result.sharpe_ratio
            mdd = result.max_drawdown * 100
            pf = result.profit_factor
            trades = result.total_trades

            r = RunResult(
                strategy=strategy_name,
                symbol=symbol,
                profile=profile_name,
                return_pct=ret,
                win_rate=wr,
                sharpe=sharpe,
                max_dd=mdd,
                profit_factor=pf,
                trades=trades,
            )
            results.append(r)

            tag = " PASS" if r.passes_threshold else ""
            print(
                f"    {profile_name:<14s} | {ret:+7.2f}% | WR:{wr:5.1f}% "
                f"| Sharpe:{sharpe:5.2f} | DD:{mdd:5.2f}% | PF:{pf:5.2f} "
                f"| Trades:{trades:3d}{tag}"
            )

        except Exception as exc:
            print(f"    {profile_name:<14s} | ERROR: {exc}")
            results.append(RunResult(
                strategy=strategy_name, symbol=symbol, profile=profile_name,
                return_pct=0.0, win_rate=0.0, sharpe=0.0, max_dd=0.0,
                profit_factor=0.0, trades=0,
            ))

    return results


# ---------------------------------------------------------------------------
# Config file updaters
# ---------------------------------------------------------------------------

def best_passing_result(results: list[RunResult]) -> RunResult | None:
    """Return the best (highest return) result that passes admission thresholds."""
    passing = [r for r in results if r.passes_threshold]
    if not passing:
        return None
    return max(passing, key=lambda r: r.return_pct)


def add_symbol_to_yaml(
    yaml_path: str,
    strategy_key: str,
    symbol: str,
    return_pct: float,
    profile: str,
    sharpe: float,
) -> None:
    """
    Append a symbol entry to the strategy's symbols list in strategies.yaml.
    Inserts after the last existing symbol entry in that strategy's block.
    Uses text manipulation to preserve all YAML comments and formatting.
    """
    with open(yaml_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Check it's not already present
    if f'- "{symbol}"' in content or f"- '{symbol}'" in content:
        print(f"    [YAML] {symbol} already present in {strategy_key} — skip")
        return

    # Find the strategy block, then locate the symbols list and insert at end
    # We look for the last '- "SOMETHING"' line within the strategy's symbols block.
    # Strategy blocks are separated by blank lines + '  # ──' headers.
    # Simple approach: find "strategy_key:" then scan forward for the last symbol entry
    # before the next top-level key at the same indentation.

    # Build the new line
    note = f"+{return_pct:.2f}% {profile}"
    if sharpe >= 1.0:
        note += f" Sharpe {sharpe:.2f}"
    new_line = f'      - "{symbol}"    # {note} (2026-03-21)\n'

    # Locate the strategy block start
    strategy_header = f"  {strategy_key}:"
    idx = content.find(strategy_header)
    if idx == -1:
        print(f"    [YAML] Could not locate strategy '{strategy_key}' — skip")
        return

    # Find the symbols: sub-key inside this block
    symbols_idx = content.find("    symbols:", idx)
    if symbols_idx == -1:
        print(f"    [YAML] Could not locate 'symbols:' under '{strategy_key}' — skip")
        return

    # Find the last symbol entry in this block by scanning forward line by line
    # Stop when we reach a line that is NOT indented with 6 spaces (i.e. not a symbol entry)
    # and NOT a comment at 6-space indent, AND is beyond the symbols section
    after_symbols = content[symbols_idx:]
    lines = after_symbols.split("\n")

    last_symbol_line_offset = None  # character offset in `after_symbols`
    char_pos = 0
    in_symbols_list = False

    for line in lines:
        if line.strip() == "symbols:":
            in_symbols_list = True
            char_pos += len(line) + 1
            continue

        if in_symbols_list:
            # A symbol entry line starts with exactly 6 spaces then "- "
            if re.match(r"^      - ", line):
                last_symbol_line_offset = char_pos
            elif line.strip() == "" or re.match(r"^      #", line):
                # blank line or comment within the list is fine, keep scanning
                pass
            else:
                # We've left the symbols list (hit a different key at same/outer indentation)
                break

        char_pos += len(line) + 1

    if last_symbol_line_offset is None:
        print(f"    [YAML] Could not find symbol entries in '{strategy_key}' — skip")
        return

    # Find the end of that last symbol line (the newline character)
    abs_last_line_start = symbols_idx + last_symbol_line_offset
    end_of_last_line = content.find("\n", abs_last_line_start)
    if end_of_last_line == -1:
        end_of_last_line = len(content) - 1

    # Insert our new line immediately after the last symbol line
    new_content = content[: end_of_last_line + 1] + new_line + content[end_of_last_line + 1:]

    with open(yaml_path, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    print(f"    [YAML] Added {symbol} to {strategy_key} ({note})")


def add_risk_profile_entry(
    py_path: str,
    strategy_key: str,
    symbol: str,
    profile: str,
    return_pct: float,
    sharpe: float,
    win_rate: float,
) -> None:
    """
    Append a new entry to OPTIMAL_PROFILES in core/risk_profiles.py.
    Inserts directly after the last existing entry for the given strategy_key.
    """
    with open(py_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Check not already present
    entry_key = f'("{strategy_key}", "{symbol}")'
    if entry_key in content:
        print(f"    [PY]   {symbol} already in OPTIMAL_PROFILES for {strategy_key} — skip")
        return

    # Build the new line
    comment = f"+{return_pct:.2f}%, Sharpe {sharpe:.2f}, WR {win_rate:.0f}%"
    new_line = (
        f'    ("{strategy_key}", "{symbol}"): "{profile}",   '
        f'# {comment} (2026-03-21)\n'
    )

    # Find the strategy comment anchor, e.g. "# ── donchian_breakout ──"
    anchor = f"# ── {strategy_key}"
    anchor_idx = content.find(anchor)
    if anchor_idx == -1:
        # Fallback: find the last existing entry for this strategy and append after it
        anchor_idx = content.rfind(f'("{strategy_key}",')
        if anchor_idx == -1:
            print(f"    [PY]   Could not find anchor for {strategy_key} — skip")
            return
        # Find end of that line
        end_line = content.find("\n", anchor_idx)
        insert_pos = end_line + 1
    else:
        # Find all lines for this strategy block and get the last one
        # Scan forward from anchor for all ("strategy_key", ...) lines
        last_entry_end = None

        for m in re.finditer(rf'\("{re.escape(strategy_key)}", "[^"]+"\):', content):
            last_entry_end = content.find("\n", m.start()) + 1

        if last_entry_end is None:
            # No entries yet for this strategy — insert after the anchor comment line
            end_of_anchor_line = content.find("\n", anchor_idx)
            insert_pos = end_of_anchor_line + 1
        else:
            insert_pos = last_entry_end

    new_content = content[:insert_pos] + new_line + content[insert_pos:]

    with open(py_path, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    print(f"    [PY]   Added {symbol} -> {profile} to OPTIMAL_PROFILES ({comment})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(base, "config", "strategies.yaml")
    py_path = os.path.join(base, "core", "risk_profiles.py")

    print("=" * 80)
    print("  ATLAS -- Donchian Breakout Expansion Backtest")
    print(f"  Date: 2026-03-21  |  Data: Kraken {TIMEFRAME} x {BARS} bars")
    print(f"  Admission threshold: return > {MIN_RETURN_PCT}%  AND  "
          f"Sharpe > {MIN_SHARPE}  AND  trades >= {MIN_TRADES}")
    print("=" * 80)

    engine = BacktestEngine(
        initial_capital=INITIAL_CAPITAL,
        commission_pct=COMMISSION_PCT,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],
    )

    # Collect all unique symbols to fetch
    all_symbols = sorted(set(DONCHIAN_CANDIDATES + SMART_MONEY_CANDIDATES))

    print(f"\n--- Fetching data for {len(all_symbols)} symbols ---")
    for sym in all_symbols:
        fetch_ohlcv(sym)

    # ── Donchian Breakout candidates ─────────────────────────────────────────

    print("\n")
    print("=" * 80)
    print("  DONCHIAN BREAKOUT — Expansion candidates")
    print("=" * 80)

    donchian_all_results: list[RunResult] = []

    for symbol in DONCHIAN_CANDIDATES:
        df = _data_cache.get(symbol)
        if df is None or not isinstance(df, pd.DataFrame):
            print(f"\n  {symbol}: [NO DATA — skipped]")
            continue

        print(f"\n  {symbol}:")
        results = run_strategy(engine, "donchian_breakout", DONCHIAN_PARAMS, symbol, df)
        donchian_all_results.extend(results)

    # ── Smart Money candidates ────────────────────────────────────────────────

    print("\n")
    print("=" * 80)
    print("  SMART MONEY CONCEPTS — High-liquidity alt candidates")
    print("=" * 80)

    smart_all_results: list[RunResult] = []

    for symbol in SMART_MONEY_CANDIDATES:
        df = _data_cache.get(symbol)
        if df is None or not isinstance(df, pd.DataFrame):
            print(f"\n  {symbol}: [NO DATA — skipped]")
            continue

        print(f"\n  {symbol}:")
        results = run_strategy(engine, "smart_money", SMART_MONEY_PARAMS, symbol, df)
        smart_all_results.extend(results)

    # ── Results summary ───────────────────────────────────────────────────────

    all_results = donchian_all_results + smart_all_results

    print("\n\n")
    print("=" * 100)
    print("  FULL RESULTS — All tests (sorted by return)")
    print("=" * 100)
    print(f"  {'Strategy':<22s} {'Symbol':<14s} {'Profile':<14s} "
          f"{'Return':>8s} {'WR':>7s} {'Sharpe':>8s} {'MaxDD':>8s} "
          f"{'PF':>7s} {'Trades':>7s} {'Admit':>8s}")
    print("-" * 100)

    for r in sorted(all_results, key=lambda r: r.return_pct, reverse=True):
        admit = "PASS" if r.passes_threshold else "fail"
        print(
            f"  {r.strategy:<22s} {r.symbol:<14s} {r.profile:<14s} "
            f"{r.return_pct:+7.2f}% {r.win_rate:6.1f}% {r.sharpe:8.2f} "
            f"{r.max_dd:7.2f}% {r.profit_factor:7.2f} {r.trades:7d} {admit:>8s}"
        )

    # ── Best profile per symbol ───────────────────────────────────────────────

    print("\n\n")
    print("=" * 100)
    print("  BEST PROFILE PER SYMBOL (admission filter applied)")
    print("=" * 100)

    # Group results by (strategy, symbol)
    from itertools import groupby
    keyfn = lambda r: (r.strategy, r.symbol)
    sorted_by_key = sorted(all_results, key=keyfn)

    admitted: list[RunResult] = []
    rejected: list[tuple[str, str]] = []

    for (strat, sym), group in groupby(sorted_by_key, key=keyfn):
        group_list = list(group)
        best = max(group_list, key=lambda r: r.return_pct)
        if best.passes_threshold:
            admitted.append(best)
        else:
            rejected.append((strat, sym))

    admitted.sort(key=lambda r: r.return_pct, reverse=True)

    if admitted:
        print(f"\n  ADMITTED ({len(admitted)} symbols pass threshold):")
        print(f"  {'Strategy':<22s} {'Symbol':<14s} {'Profile':<14s} "
              f"{'Return':>8s} {'Sharpe':>8s} {'Trades':>7s}")
        print("  " + "-" * 80)
        for r in admitted:
            print(
                f"  {r.strategy:<22s} {r.symbol:<14s} {r.profile:<14s} "
                f"{r.return_pct:+7.2f}% {r.sharpe:8.2f} {r.trades:7d}"
            )
    else:
        print("\n  No symbols passed the admission threshold.")

    if rejected:
        print(f"\n  REJECTED ({len(rejected)} symbols):")
        for strat, sym in rejected:
            print(f"    {strat:<22s} {sym}")

    # ── Auto-add to config files ──────────────────────────────────────────────

    if not admitted:
        print("\n  Nothing to add — config files unchanged.")
        return

    print("\n\n")
    print("=" * 80)
    print("  AUTO-UPDATING CONFIG FILES")
    print("=" * 80)

    for r in admitted:
        print(f"\n  Adding {r.strategy} / {r.symbol} ({r.profile}, "
              f"{r.return_pct:+.2f}%, Sharpe {r.sharpe:.2f}):")

        add_symbol_to_yaml(
            yaml_path=yaml_path,
            strategy_key=r.strategy,
            symbol=r.symbol,
            return_pct=r.return_pct,
            profile=r.profile,
            sharpe=r.sharpe,
        )

        add_risk_profile_entry(
            py_path=py_path,
            strategy_key=r.strategy,
            symbol=r.symbol,
            profile=r.profile,
            return_pct=r.return_pct,
            sharpe=r.sharpe,
            win_rate=r.win_rate,
        )

    print("\n  Config files updated. Run `python -m pytest tests/ -v` to verify.")
    print("\n  Atlas expansion complete.")


if __name__ == "__main__":
    main()
