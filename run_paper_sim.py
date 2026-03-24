"""
run_paper_sim.py — Accelerated Paper Trading Simulation
========================================================
Fetches live Kraken data for crypto, generates realistic synthetic data for
stocks/forex/gold, runs every enabled strategy through the backtest engine,
and produces a full profitability report with actionable improvement suggestions.

This simulates what paper trading would do over ~3-6 months of historical data,
compressed into a single run.

Usage:
    python run_paper_sim.py
"""

from __future__ import annotations

import math
import os
import sys
import time
import traceback

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Ensure project root on path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backtesting.engine import BacktestEngine, BacktestResult
from strategies.base import BaseStrategy

# Import all strategies to trigger registration
from strategies.technical import *  # noqa: F401,F403

# ─────────────────────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────────────────────

INITIAL_CAPITAL = 10_000.0
COMMISSION_PCT = 0.001  # 0.1% per trade

# How many candles to fetch/generate per timeframe
CANDLE_COUNTS = {
    "5m": 2000,   # ~7 days
    "15m": 2000,  # ~21 days
    "1h": 2000,   # ~83 days
    "4h": 1000,   # ~167 days
    "1d": 500,    # ~500 days
}

# Kraken crypto symbols (free, no API key)
CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT",
]

# Synthetic data profiles for non-crypto assets
STOCK_PROFILES = {
    "SPY":  {"annual_vol": 0.15, "annual_drift": 0.10, "base_price": 520.0},
    "QQQ":  {"annual_vol": 0.20, "annual_drift": 0.12, "base_price": 450.0},
    "AAPL": {"annual_vol": 0.25, "annual_drift": 0.08, "base_price": 190.0},
    "NVDA": {"annual_vol": 0.45, "annual_drift": 0.25, "base_price": 900.0},
    "MSFT": {"annual_vol": 0.22, "annual_drift": 0.10, "base_price": 420.0},
    "AMZN": {"annual_vol": 0.28, "annual_drift": 0.12, "base_price": 185.0},
    "TSLA": {"annual_vol": 0.55, "annual_drift": 0.05, "base_price": 175.0},
    "AMD":  {"annual_vol": 0.40, "annual_drift": 0.15, "base_price": 160.0},
    "META": {"annual_vol": 0.30, "annual_drift": 0.15, "base_price": 500.0},
    "GOOG": {"annual_vol": 0.25, "annual_drift": 0.10, "base_price": 155.0},
    # Sector ETFs
    "XLK":  {"annual_vol": 0.20, "annual_drift": 0.12, "base_price": 220.0},
    "XLF":  {"annual_vol": 0.18, "annual_drift": 0.08, "base_price": 42.0},
    "XLE":  {"annual_vol": 0.25, "annual_drift": 0.05, "base_price": 90.0},
    "XLV":  {"annual_vol": 0.15, "annual_drift": 0.07, "base_price": 145.0},
    "XLI":  {"annual_vol": 0.18, "annual_drift": 0.09, "base_price": 120.0},
    "XLC":  {"annual_vol": 0.22, "annual_drift": 0.10, "base_price": 85.0},
    "XLY":  {"annual_vol": 0.22, "annual_drift": 0.08, "base_price": 190.0},
    "XLP":  {"annual_vol": 0.12, "annual_drift": 0.06, "base_price": 80.0},
    "XLU":  {"annual_vol": 0.15, "annual_drift": 0.05, "base_price": 72.0},
    "XLRE": {"annual_vol": 0.18, "annual_drift": 0.04, "base_price": 40.0},
    "XLB":  {"annual_vol": 0.20, "annual_drift": 0.06, "base_price": 88.0},
}

FOREX_PROFILES = {
    "EUR_USD": {"annual_vol": 0.08, "annual_drift": 0.00, "base_price": 1.0850},
    "GBP_USD": {"annual_vol": 0.09, "annual_drift": 0.00, "base_price": 1.2700},
    "USD_JPY": {"annual_vol": 0.10, "annual_drift": 0.02, "base_price": 150.50},
    "AUD_USD": {"annual_vol": 0.10, "annual_drift": -0.01, "base_price": 0.6550},
    "USD_CAD": {"annual_vol": 0.07, "annual_drift": 0.01, "base_price": 1.3600},
    "EUR_GBP": {"annual_vol": 0.07, "annual_drift": 0.00, "base_price": 0.8550},
    "XAU_USD": {"annual_vol": 0.15, "annual_drift": 0.08, "base_price": 2050.0},
    "XAG_USD": {"annual_vol": 0.22, "annual_drift": 0.05, "base_price": 24.50},
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data generation
# ─────────────────────────────────────────────────────────────────────────────

def fetch_kraken_ohlcv(symbol: str, timeframe: str, limit: int) -> pd.DataFrame | None:
    """Fetch OHLCV from Kraken via ccxt (free, no API key)."""
    try:
        import ccxt
        exchange = ccxt.kraken({"enableRateLimit": True})
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not ohlcv or len(ohlcv) < 50:
            return None
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df.attrs["symbol"] = symbol
        return df
    except Exception as e:
        print(f"    [WARN] Failed to fetch {symbol} {timeframe}: {e}")
        return None


def generate_synthetic_ohlcv(
    symbol: str,
    timeframe: str,
    n_bars: int,
    annual_vol: float,
    annual_drift: float,
    base_price: float,
) -> pd.DataFrame:
    """Generate realistic synthetic OHLCV data with proper market microstructure."""
    np.random.seed(hash(symbol + timeframe) % (2**31))

    # Time delta per bar
    tf_minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
    minutes_per_bar = tf_minutes.get(timeframe, 60)
    bars_per_year = 365.25 * 24 * 60 / minutes_per_bar

    # Per-bar drift and vol
    dt = 1.0 / bars_per_year
    mu_bar = annual_drift * dt
    sigma_bar = annual_vol * math.sqrt(dt)

    # Generate returns with mean-reversion component (realistic)
    returns = np.random.normal(mu_bar, sigma_bar, n_bars)
    # Add autocorrelation (momentum for trend-following, mean-reversion for oscillation)
    for i in range(1, len(returns)):
        returns[i] += 0.05 * returns[i - 1]  # slight momentum

    # Build close prices
    close = np.zeros(n_bars)
    close[0] = base_price
    for i in range(1, n_bars):
        close[i] = close[i - 1] * (1 + returns[i])
        close[i] = max(close[i], base_price * 0.01)  # floor

    # Generate OHLC from close
    intrabar_vol = sigma_bar * 0.6  # intra-bar volatility
    high = close * (1 + np.abs(np.random.normal(0, intrabar_vol, n_bars)))
    low = close * (1 - np.abs(np.random.normal(0, intrabar_vol, n_bars)))
    # Open = prior close with small gap
    open_prices = np.roll(close, 1) * (1 + np.random.normal(0, sigma_bar * 0.1, n_bars))
    open_prices[0] = base_price

    # Ensure high >= max(open, close) and low <= min(open, close)
    high = np.maximum(high, np.maximum(open_prices, close))
    low = np.minimum(low, np.minimum(open_prices, close))

    # Volume: log-normal with session patterns
    base_vol = 1_000_000 if base_price > 100 else 5_000_000
    volume = np.random.lognormal(mean=np.log(base_vol), sigma=0.5, size=n_bars)
    # Add volume spikes on big moves
    big_moves = np.abs(returns) > 2 * sigma_bar
    volume[big_moves] *= np.random.uniform(2.0, 4.0, big_moves.sum())

    # Build timestamps
    # Use market hours for stocks (only weekdays, 09:30-16:00 ET for daily)
    end_time = datetime(2026, 3, 19, tzinfo=UTC)
    if timeframe == "1d":
        # Daily bars: go back n_bars weekdays
        dates = pd.bdate_range(end=end_time, periods=n_bars, tz=UTC)
        # Add market open time (13:30 UTC = 09:30 ET)
        timestamps = [d + pd.Timedelta(hours=13, minutes=30) for d in dates]
    elif timeframe in ("5m", "15m"):
        # Intraday: only generate during US market hours (13:30-20:00 UTC)
        timestamps = []
        current = end_time
        bars_per_day = int(6.5 * 60 / minutes_per_bar)  # 6.5h trading day
        days_needed = (n_bars // bars_per_day) + 2
        for day_offset in range(days_needed, 0, -1):
            day = end_time - timedelta(days=day_offset)
            if day.weekday() >= 5:
                continue
            market_open = day.replace(hour=13, minute=30, second=0, microsecond=0)
            for bar_idx in range(bars_per_day):
                ts = market_open + timedelta(minutes=bar_idx * minutes_per_bar)
                timestamps.append(ts)
                if len(timestamps) >= n_bars:
                    break
            if len(timestamps) >= n_bars:
                break
        timestamps = timestamps[:n_bars]
    else:
        # Hourly/4h: continuous (forex/crypto style)
        timestamps = pd.date_range(
            end=end_time, periods=n_bars, freq=f"{minutes_per_bar}min", tz=UTC
        )

    timestamps = timestamps[:n_bars]
    if len(timestamps) < n_bars:
        # Pad if we didn't generate enough
        extra = pd.date_range(
            end=timestamps[0] - timedelta(minutes=minutes_per_bar),
            periods=n_bars - len(timestamps),
            freq=f"{minutes_per_bar}min",
            tz=UTC,
        )
        timestamps = list(extra) + list(timestamps)

    df = pd.DataFrame({
        "open": open_prices[:len(timestamps)],
        "high": high[:len(timestamps)],
        "low": low[:len(timestamps)],
        "close": close[:len(timestamps)],
        "volume": volume[:len(timestamps)],
    }, index=pd.DatetimeIndex(timestamps[:len(open_prices)], name="timestamp"))

    df.attrs["symbol"] = symbol
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  Strategy loading
# ─────────────────────────────────────────────────────────────────────────────

def load_enabled_strategies() -> dict[str, dict]:
    """Load enabled strategies from config/strategies.yaml."""
    with open(_ROOT / "config" / "strategies.yaml") as f:
        cfg = yaml.safe_load(f)
    return {
        name: scfg for name, scfg in cfg["strategies"].items()
        if scfg.get("enabled", False)
    }


def get_strategy_class(name: str) -> type[BaseStrategy] | None:
    """Find strategy class by name from registry."""
    for cls in BaseStrategy.__subclasses__():
        if cls.name == name:
            return cls
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Result container
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SimResult:
    strategy: str
    symbol: str
    timeframe: str
    data_source: str  # "kraken" or "synthetic"
    return_pct: float
    win_rate: float
    total_trades: int
    sharpe: float
    max_dd_pct: float
    profit_factor: float
    expectancy: float
    avg_trade_duration: str
    status: str  # "GO" or "NO-GO"
    issues: list[str]


# ─────────────────────────────────────────────────────────────────────────────
#  Main simulation
# ─────────────────────────────────────────────────────────────────────────────

def run_simulation() -> list[SimResult]:
    """Run backtests for all enabled strategy-symbol pairs."""
    strategies = load_enabled_strategies()
    engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, commission_pct=COMMISSION_PCT, regime_filter=True)
    results: list[SimResult] = []

    # Cache fetched/generated data
    data_cache: dict[tuple[str, str], pd.DataFrame] = {}

    print("=" * 90)
    print("  ATLAS PAPER TRADING SIMULATION — Comprehensive Profitability Report")
    print("=" * 90)
    print(f"  Capital: ${INITIAL_CAPITAL:,.0f} per strategy-symbol pair")
    print(f"  Commission: {COMMISSION_PCT * 100:.2f}%")
    print(f"  Strategies: {len(strategies)} enabled")
    print()

    for strat_name, strat_cfg in strategies.items():
        cls = get_strategy_class(strat_name)
        if not cls:
            print(f"  [SKIP] {strat_name}: class not found in registry")
            continue

        params = strat_cfg.get("parameters", {})
        try:
            strategy = cls(**params)
        except Exception as e:
            print(f"  [SKIP] {strat_name}: constructor failed: {e}")
            continue

        timeframe = strat_cfg.get("timeframe", "4h")
        symbols = strat_cfg.get("symbols", [])
        n_bars = CANDLE_COUNTS.get(timeframe, 1000)

        print(f"\n{'─' * 90}")
        print(f"  STRATEGY: {strat_name} ({timeframe}) — {len(symbols)} symbols")
        print(f"{'─' * 90}")

        for symbol in symbols:
            cache_key = (symbol, timeframe)
            data_source = "synthetic"

            if cache_key not in data_cache:
                # Try Kraken for crypto
                if "/" in symbol and "USDT" in symbol:
                    df = fetch_kraken_ohlcv(symbol, timeframe, n_bars)
                    if df is not None:
                        data_cache[cache_key] = df
                        data_source = "kraken"

                # Generate synthetic for stocks/forex/gold
                if cache_key not in data_cache:
                    profile = STOCK_PROFILES.get(symbol) or FOREX_PROFILES.get(symbol)
                    if profile:
                        df = generate_synthetic_ohlcv(
                            symbol, timeframe, n_bars, **profile
                        )
                        data_cache[cache_key] = df
                    else:
                        print(f"    [SKIP] {symbol}: no data profile")
                        continue
            else:
                df = data_cache[cache_key]
                data_source = "kraken" if ("/" in symbol and "USDT" in symbol) else "synthetic"

            df = data_cache[cache_key]
            df.attrs["symbol"] = symbol

            try:
                result: BacktestResult = engine.run(df, strategy)
            except Exception as e:
                print(f"    [ERROR] {symbol}: backtest crashed: {e}")
                traceback.print_exc()
                continue

            # Determine GO/NO-GO status
            issues = []
            ret_pct = result.total_return * 100
            wr = result.win_rate * 100
            trades = result.total_trades
            sharpe = result.sharpe_ratio
            max_dd = result.max_drawdown * 100
            pf = result.profit_factor

            if trades < 2:
                issues.append(f"Only {trades} trades (need >=2)")
            if ret_pct <= 0:
                issues.append(f"Negative return: {ret_pct:+.2f}%")
            if wr < 20 and trades >= 2:
                issues.append(f"Low win rate: {wr:.1f}%")
            if max_dd < -10:
                issues.append(f"High drawdown: {max_dd:.1f}%")
            if sharpe < 0 and trades >= 3:
                issues.append(f"Negative Sharpe: {sharpe:.2f}")

            status = "GO" if (ret_pct > 0 and trades >= 2 and wr >= 15) else "NO-GO"

            avg_dur = str(result.avg_trade_duration).split(".")[0] if result.avg_trade_duration else "N/A"

            sim_result = SimResult(
                strategy=strat_name,
                symbol=symbol,
                timeframe=timeframe,
                data_source=data_source,
                return_pct=ret_pct,
                win_rate=wr,
                total_trades=trades,
                sharpe=sharpe,
                max_dd_pct=max_dd,
                profit_factor=pf,
                expectancy=result.expectancy,
                avg_trade_duration=avg_dur,
                status=status,
                issues=issues,
            )
            results.append(sim_result)

            status_icon = "+" if status == "GO" else "X"
            src_tag = "LIVE" if data_source == "kraken" else "SYN"
            print(
                f"    [{status_icon}] {symbol:12s} [{src_tag}] "
                f"Ret:{ret_pct:+7.2f}%  WR:{wr:5.1f}%  "
                f"Trades:{trades:3d}  Sharpe:{sharpe:+6.2f}  "
                f"MaxDD:{max_dd:+6.1f}%  PF:{pf:.2f}  "
                f"{'  '.join(issues) if issues else 'CLEAN'}"
            )

    return results


def print_summary(results: list[SimResult]) -> None:
    """Print the final comprehensive summary."""
    go = [r for r in results if r.status == "GO"]
    nogo = [r for r in results if r.status == "NO-GO"]
    live = [r for r in results if r.data_source == "kraken"]
    live_go = [r for r in live if r.status == "GO"]

    print("\n\n" + "=" * 90)
    print("  COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 90)

    # Strategy-level aggregation
    strat_results: dict[str, list[SimResult]] = {}
    for r in results:
        strat_results.setdefault(r.strategy, []).append(r)

    print(f"\n{'Strategy':<25s} {'Symbols':>7s} {'GO':>4s} {'Avg Ret%':>9s} {'Avg WR%':>8s} {'Avg Sharpe':>10s} {'Verdict':>10s}")
    print("─" * 85)

    strategy_verdicts = {}
    for strat_name, strat_list in strat_results.items():
        n_sym = len(strat_list)
        n_go = sum(1 for r in strat_list if r.status == "GO")
        avg_ret = np.mean([r.return_pct for r in strat_list])
        avg_wr = np.mean([r.win_rate for r in strat_list if r.total_trades > 0]) if any(r.total_trades > 0 for r in strat_list) else 0
        avg_sharpe = np.mean([r.sharpe for r in strat_list if r.total_trades > 0]) if any(r.total_trades > 0 for r in strat_list) else 0

        go_pct = n_go / n_sym * 100 if n_sym > 0 else 0
        if go_pct >= 60 and avg_ret > 0:
            verdict = "DEPLOY"
        elif go_pct >= 30 and avg_ret > -2:
            verdict = "TUNE"
        else:
            verdict = "DISABLE"

        strategy_verdicts[strat_name] = verdict

        print(
            f"  {strat_name:<23s} {n_sym:>5d}/{n_go:>2d}   "
            f"{avg_ret:>+8.2f}%  {avg_wr:>7.1f}%  {avg_sharpe:>+9.2f}    {verdict:>8s}"
        )

    # Overall stats
    total_pairs = len(results)
    go_count = len(go)
    total_ret_avg = np.mean([r.return_pct for r in results]) if results else 0

    print(f"\n{'─' * 85}")
    print(f"  TOTAL: {total_pairs} strategy-symbol pairs  |  {go_count} GO ({go_count/total_pairs*100:.0f}%)  |  {len(nogo)} NO-GO")
    print(f"  Average return across all pairs: {total_ret_avg:+.2f}%")

    if live:
        live_avg = np.mean([r.return_pct for r in live])
        print(f"  Live Kraken data: {len(live)} pairs tested, {len(live_go)} GO, avg return: {live_avg:+.2f}%")

    # Top performers
    sorted_results = sorted(results, key=lambda r: r.return_pct, reverse=True)
    print(f"\n  TOP 10 PERFORMERS:")
    for i, r in enumerate(sorted_results[:10], 1):
        src = "LIVE" if r.data_source == "kraken" else "SYN"
        print(f"    {i:2d}. {r.strategy:22s} {r.symbol:12s} [{src}] {r.return_pct:+7.2f}%  WR:{r.win_rate:.0f}%  Sharpe:{r.sharpe:+.2f}")

    # Worst performers
    print(f"\n  BOTTOM 10 (needs work):")
    for i, r in enumerate(sorted_results[-10:], 1):
        src = "LIVE" if r.data_source == "kraken" else "SYN"
        print(f"    {i:2d}. {r.strategy:22s} {r.symbol:12s} [{src}] {r.return_pct:+7.2f}%  WR:{r.win_rate:.0f}%  Issues: {'; '.join(r.issues) or 'marginal'}")

    # Actionable recommendations
    print(f"\n{'=' * 90}")
    print("  ACTIONABLE RECOMMENDATIONS")
    print(f"{'=' * 90}")

    deploy_strats = [s for s, v in strategy_verdicts.items() if v == "DEPLOY"]
    tune_strats = [s for s, v in strategy_verdicts.items() if v == "TUNE"]
    disable_strats = [s for s, v in strategy_verdicts.items() if v == "DISABLE"]

    if deploy_strats:
        print(f"\n  DEPLOY (ready for live paper trading):")
        for s in deploy_strats:
            avg = np.mean([r.return_pct for r in strat_results[s]])
            print(f"    - {s}: {avg:+.2f}% avg return")

    if tune_strats:
        print(f"\n  TUNE (profitable on some symbols, needs parameter adjustment):")
        for s in tune_strats:
            losers = [r for r in strat_results[s] if r.status == "NO-GO"]
            loser_syms = [r.symbol for r in losers[:3]]
            print(f"    - {s}: losing on {', '.join(loser_syms)}")

    if disable_strats:
        print(f"\n  DISABLE (not profitable, needs fundamental rework or removal):")
        for s in disable_strats:
            avg = np.mean([r.return_pct for r in strat_results[s]])
            print(f"    - {s}: {avg:+.2f}% avg return — consider disabling")

    # Zero-trade strategies
    zero_trade = [r for r in results if r.total_trades == 0]
    if zero_trade:
        print(f"\n  ZERO TRADES (filters too tight or data mismatch):")
        for r in zero_trade:
            print(f"    - {r.strategy} on {r.symbol} ({r.timeframe})")

    print(f"\n{'=' * 90}")
    print("  Simulation complete.")
    print(f"{'=' * 90}")


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    start = time.time()
    results = run_simulation()
    elapsed = time.time() - start
    print(f"\n  [Simulation took {elapsed:.1f}s]")
    print_summary(results)
