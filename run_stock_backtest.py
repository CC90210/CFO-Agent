"""
run_stock_backtest.py — Atlas stock strategy backtest on real yfinance data.

Fetches ~5 years of daily OHLCV data for US equity and sector ETF symbols,
then runs four stock-specific strategies under three risk profiles:
  - conservative  (yaml defaults)
  - aggressive    (atr_stop_mult=1.0, rr_ratio=4.0)
  - daredevil     (atr_stop_mult=0.75, rr_ratio=5.0)

Strategies tested
-----------------
  connors_rsi          — RSI(2) mean reversion, daily bars
  ibs_mean_reversion   — Internal Bar Strength snap-back, daily bars
  sector_rotation      — Composite 1/3/6-month momentum ranking, daily bars
  equity_mean_reversion — RSI + Bollinger Bands within trend, daily bars

Usage
-----
    python run_stock_backtest.py
"""

from __future__ import annotations

import sys
import logging
from dataclasses import dataclass
from typing import Any

# ── Windows UTF-8 safety ────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Silence noisy third-party loggers ───────────────────────────────────────
logging.basicConfig(level=logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.ERROR)
logging.getLogger("peewee").setLevel(logging.ERROR)

import pandas as pd
import yfinance as yf  # type: ignore[import]

# ── Atlas imports ────────────────────────────────────────────────────────────
from backtesting.engine import BacktestEngine, BacktestResult
from strategies.technical.connors_rsi import ConnorsRSIStrategy
from strategies.technical.ibs_mean_reversion import IBSMeanReversionStrategy
from strategies.technical.sector_rotation import SectorRotationStrategy
from strategies.technical.equity_mean_reversion import EquityMeanReversionStrategy

# ── Universe ─────────────────────────────────────────────────────────────────
EQUITY_SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "GOOG", "AMD"]
SECTOR_SYMBOLS = ["XLC", "XLY", "XLU", "XLB", "XLK", "XLF", "XLE"]

# ── Risk profiles ─────────────────────────────────────────────────────────────
# Each profile is a dict of kwargs to overlay on top of the strategy constructor.
# Keys that do not exist in a specific strategy's __init__ are ignored safely via
# the per-strategy factory functions below.
RISK_PROFILES: dict[str, dict[str, Any]] = {
    "conservative": {},
    "aggressive":   {"atr_stop_mult": 1.0,  "rr_ratio": 4.0},
    "daredevil":    {"atr_stop_mult": 0.75, "rr_ratio": 5.0},
}


# ---------------------------------------------------------------------------
# Strategy factories — one per strategy, accepts only valid kwargs
# ---------------------------------------------------------------------------

def make_connors_rsi(profile: dict[str, Any]) -> ConnorsRSIStrategy:
    return ConnorsRSIStrategy(
        rsi_period=2,
        rsi_entry_long=10.0,
        rsi_entry_short=90.0,
        sma_trend_period=200,
        sma_mid_period=50,
        cumulative_bars=2,
        cumulative_threshold=35.0,
        bb_period=20,
        bb_std=2.0,
        volume_period=20,
        volume_mult=1.2,
        atr_period=14,
        atr_stop_mult=profile.get("atr_stop_mult", 1.5),
        rr_ratio=profile.get("rr_ratio", 2.0),
    )


def make_ibs_mean_reversion(profile: dict[str, Any]) -> IBSMeanReversionStrategy:
    return IBSMeanReversionStrategy(
        ibs_entry_long=0.2,
        ibs_entry_short=0.8,
        ibs_extreme=0.1,
        rsi_period=21,
        rsi_entry_long=40.0,
        rsi_entry_short=60.0,
        rsi_deep_oversold=30.0,
        rsi_deep_overbought=70.0,
        sma_trend_period=200,
        sma_mid_period=50,
        consecutive_down_days=3,
        volume_period=20,
        volume_mult=1.3,
        atr_period=14,
        atr_stop_mult=profile.get("atr_stop_mult", 1.5),
        rr_ratio=profile.get("rr_ratio", 2.0),
    )


def make_sector_rotation(profile: dict[str, Any]) -> SectorRotationStrategy:
    # sector_rotation does not accept atr_tp_mult; uses rr_ratio for TP sizing
    return SectorRotationStrategy(
        short_momentum_bars=21,
        mid_momentum_bars=63,
        long_momentum_bars=126,
        sma_trend_period=200,
        sma_mid_period=50,
        rsi_period=14,
        rsi_overbought=70.0,
        adx_period=14,
        adx_min=25.0,
        volume_period=20,
        volume_mult=1.2,
        atr_period=14,
        atr_stop_mult=profile.get("atr_stop_mult", 2.0),
        rr_ratio=profile.get("rr_ratio", 2.5),
    )


def make_equity_mean_reversion(profile: dict[str, Any]) -> EquityMeanReversionStrategy:
    # equity_mean_reversion uses atr_tp_mult (not rr_ratio) for TP sizing
    return EquityMeanReversionStrategy(
        rsi_period=14,
        rsi_oversold=30.0,
        rsi_overbought=70.0,
        rsi_exit=50.0,
        rsi_extreme_long=25.0,
        rsi_extreme_short=75.0,
        bb_period=20,
        bb_std=2.0,
        adx_period=14,
        adx_min=20.0,
        atr_period=14,
        atr_stop_mult=profile.get("atr_stop_mult", 1.5),
        atr_tp_mult=profile.get("rr_ratio", 3.0),  # rr_ratio maps to atr_tp_mult here
        volume_period=20,
        volume_mult=1.2,
        volume_high_mult=2.0,
        sma_trend_period=200,
    )


# ---------------------------------------------------------------------------
# Strategy matrix: (name, factory, symbols)
# ---------------------------------------------------------------------------

STRATEGY_CONFIGS = [
    ("connors_rsi",          make_connors_rsi,          EQUITY_SYMBOLS),
    ("ibs_mean_reversion",   make_ibs_mean_reversion,   EQUITY_SYMBOLS),
    ("sector_rotation",      make_sector_rotation,      SECTOR_SYMBOLS),
    ("equity_mean_reversion", make_equity_mean_reversion, EQUITY_SYMBOLS),
]


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_daily_ohlcv(symbol: str, period: str = "5y") -> pd.DataFrame | None:
    """
    Download daily OHLCV from yfinance, lowercase columns, tag attrs["symbol"].
    Returns None if yfinance returns an empty frame.
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval="1d", auto_adjust=True)

    if df is None or df.empty:
        return None

    # yfinance returns title-cased columns: Open, High, Low, Close, Volume
    df.columns = [c.lower() for c in df.columns]

    # Keep only the columns the engine expects
    required = {"open", "high", "low", "close", "volume"}
    available = set(df.columns)
    missing = required - available
    if missing:
        print(f"  [WARN] {symbol}: missing columns {missing} — skipping")
        return None

    df = df[list(required)].copy()

    # Ensure a UTC DatetimeIndex
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")

    df.attrs["symbol"] = symbol
    return df


# ---------------------------------------------------------------------------
# Result container for summary table
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    strategy: str
    profile: str
    symbol: str
    total_return_pct: float
    win_rate_pct: float
    sharpe: float
    max_drawdown_pct: float
    total_trades: int
    profit_factor: float


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n" + "=" * 72)
    print("  ATLAS — Stock Strategy Backtest on Real yfinance Data")
    print("  Date range: ~5 years daily bars  |  Capital: $10,000")
    print("=" * 72)

    # Pre-fetch all unique symbols so we download each once
    all_symbols: set[str] = set()
    for _, _, syms in STRATEGY_CONFIGS:
        all_symbols.update(syms)

    print(f"\n[1/3] Downloading {len(all_symbols)} symbols from yfinance ...")
    data: dict[str, pd.DataFrame] = {}
    for sym in sorted(all_symbols):
        df = fetch_daily_ohlcv(sym)
        if df is not None:
            data[sym] = df
            print(f"      {sym:8s}  {len(df):>4d} bars  "
                  f"{df.index[0].date()} -> {df.index[-1].date()}")
        else:
            print(f"      {sym:8s}  [NO DATA]")

    # Build backtest engine — scale_out disabled (empirically kills returns)
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.001,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # disable scale-out tiers
    )

    print("\n[2/3] Running backtests ...\n")
    all_results: list[RunResult] = []

    for strategy_name, factory, symbols in STRATEGY_CONFIGS:
        print(f"  Strategy: {strategy_name}")
        print(f"  {'Symbol':<8} {'Profile':<14} {'Return':>8} {'WR':>7} "
              f"{'Sharpe':>8} {'MaxDD':>8} {'Trades':>7} {'PF':>7}")
        print(f"  {'-'*8} {'-'*14} {'-'*8} {'-'*7} {'-'*8} {'-'*8} {'-'*7} {'-'*7}")

        for symbol in symbols:
            if symbol not in data:
                print(f"  {symbol:<8} [no data — skipped]")
                continue

            df = data[symbol]

            for profile_name, profile_kwargs in RISK_PROFILES.items():
                strategy = factory(profile_kwargs)

                try:
                    result: BacktestResult = engine.run(df, strategy)
                except Exception as exc:  # noqa: BLE001 — surface all errors cleanly
                    print(f"  {symbol:<8} {profile_name:<14} [ERROR: {exc}]")
                    continue

                rr = RunResult(
                    strategy=strategy_name,
                    profile=profile_name,
                    symbol=symbol,
                    total_return_pct=result.total_return * 100,
                    win_rate_pct=result.win_rate * 100,
                    sharpe=result.sharpe_ratio,
                    max_drawdown_pct=result.max_drawdown * 100,
                    total_trades=result.total_trades,
                    profit_factor=result.profit_factor,
                )
                all_results.append(rr)

                flag = "+" if result.total_return > 0 else " "
                print(
                    f"  {symbol:<8} {profile_name:<14} "
                    f"{flag}{result.total_return * 100:>6.2f}% "
                    f"{result.win_rate * 100:>6.1f}% "
                    f"{result.sharpe_ratio:>8.2f} "
                    f"{result.max_drawdown * 100:>7.2f}% "
                    f"{result.total_trades:>7d} "
                    f"{result.profit_factor:>7.2f}"
                )

        print()

    # ── Summary Table ─────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  [3/3] SUMMARY — Profitable runs (positive total return)")
    print("=" * 72)
    print(f"  {'Strategy':<24} {'Profile':<14} {'Symbol':<8} "
          f"{'Return':>8} {'WR':>7} {'Sharpe':>8} {'PF':>7}")
    print(f"  {'-'*24} {'-'*14} {'-'*8} {'-'*8} {'-'*7} {'-'*8} {'-'*7}")

    profitable = [r for r in all_results if r.total_return_pct > 0]
    profitable.sort(key=lambda r: r.total_return_pct, reverse=True)

    if profitable:
        for r in profitable:
            print(
                f"  {r.strategy:<24} {r.profile:<14} {r.symbol:<8} "
                f"+{r.total_return_pct:>6.2f}% "
                f"{r.win_rate_pct:>6.1f}% "
                f"{r.sharpe:>8.2f} "
                f"{r.profit_factor:>7.2f}"
            )
    else:
        print("  No profitable runs found.")

    print()
    print(f"  Total runs    : {len(all_results)}")
    print(f"  Profitable    : {len(profitable)} "
          f"({len(profitable)/max(1,len(all_results))*100:.1f}%)")

    # ── Strategy-level verdict ────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  VERDICT — Strategy enable recommendation")
    print("=" * 72)

    for strategy_name, _, _ in STRATEGY_CONFIGS:
        runs = [r for r in all_results if r.strategy == strategy_name]
        if not runs:
            print(f"  {strategy_name:<28} : NO DATA")
            continue

        profitable_runs = [r for r in runs if r.total_return_pct > 0]
        go_rate = len(profitable_runs) / len(runs) * 100
        best = max(runs, key=lambda r: r.total_return_pct)
        avg_return = sum(r.total_return_pct for r in runs) / len(runs)

        verdict = "ENABLE" if go_rate >= 50 and avg_return > 0 else "HOLD"
        if go_rate == 0:
            verdict = "DISABLE"

        print(
            f"  {strategy_name:<28} : {verdict}  "
            f"({len(profitable_runs)}/{len(runs)} GO, "
            f"avg {avg_return:+.2f}%, "
            f"best {best.total_return_pct:+.2f}% [{best.symbol}/{best.profile}])"
        )

    print("=" * 72)
    print()


if __name__ == "__main__":
    main()
