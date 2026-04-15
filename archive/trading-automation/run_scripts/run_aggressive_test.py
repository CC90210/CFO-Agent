"""
run_aggressive_test.py — Aggressive Risk Profile Backtester
============================================================
Tests 4 risk tiers (conservative → daredevil) across all enabled strategies
on live Kraken data + synthetic data for forex/gold/stocks.

Finds the optimal aggression level per strategy-symbol pair.

Usage:
    python run_aggressive_test.py
"""

from __future__ import annotations

import math
import os
import sys
import time
import traceback
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root on path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backtesting.engine import BacktestEngine, BacktestResult
from strategies.base import BaseStrategy

# Import all strategies to trigger registration
from strategies.technical import *  # noqa: F401,F403

# ─────────────────────────────────────────────────────────────────────────────
#  Risk Profiles
# ─────────────────────────────────────────────────────────────────────────────

RISK_PROFILES = {
    "conservative": {
        "risk_per_trade": 1.5,
        "atr_stop_mult": 2.0,
        "rr_ratio": 3.0,
        "label": "1.5% risk, 2.0x ATR, 3.0 RR",
    },
    "aggressive": {
        "risk_per_trade": 3.0,
        "atr_stop_mult": 1.5,
        "rr_ratio": 4.0,
        "label": "3.0% risk, 1.5x ATR, 4.0 RR",
    },
    "daredevil": {
        "risk_per_trade": 5.0,
        "atr_stop_mult": 1.0,
        "rr_ratio": 5.0,
        "label": "5.0% risk, 1.0x ATR, 5.0 RR",
    },
    "sniper": {
        "risk_per_trade": 4.0,
        "atr_stop_mult": 1.5,
        "rr_ratio": 5.0,
        "label": "4.0% risk, 1.5x ATR, 5.0 RR",
    },
}

# Smart Money gets a different set (wider targets work better for SMC)
SMC_PROFILES = {
    "conservative": {
        "risk_per_trade": 1.0,
        "atr_stop_mult": 2.0,
        "rr_ratio": 3.0,
        "label": "1.0% risk, 2.0x ATR, 3.0 RR",
    },
    "aggressive": {
        "risk_per_trade": 2.5,
        "atr_stop_mult": 1.5,
        "rr_ratio": 4.0,
        "label": "2.5% risk, 1.5x ATR, 4.0 RR",
    },
    "daredevil": {
        "risk_per_trade": 5.0,
        "atr_stop_mult": 1.0,
        "rr_ratio": 5.0,
        "label": "5.0% risk, 1.0x ATR, 5.0 RR",
    },
    "wide_target": {
        "risk_per_trade": 2.0,
        "atr_stop_mult": 2.0,
        "rr_ratio": 6.0,
        "time_stop_bars": 80,
        "label": "2.0% risk, 2.0x ATR, 6.0 RR, 80-bar hold",
    },
}

INITIAL_CAPITAL = 10_000.0
COMMISSION_PCT = 0.001

# Crypto symbols for live Kraken data
CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT",
]

# Synthetic data for other asset classes
FOREX_PROFILES = {
    "EUR_USD": {"annual_vol": 0.08, "annual_drift": 0.00, "base_price": 1.0850},
    "GBP_USD": {"annual_vol": 0.09, "annual_drift": 0.00, "base_price": 1.2700},
    "USD_JPY": {"annual_vol": 0.10, "annual_drift": 0.02, "base_price": 150.50},
    "AUD_USD": {"annual_vol": 0.10, "annual_drift": -0.01, "base_price": 0.6550},
    "USD_CAD": {"annual_vol": 0.07, "annual_drift": 0.01, "base_price": 1.3600},
    "XAU_USD": {"annual_vol": 0.15, "annual_drift": 0.08, "base_price": 2050.0},
    "XAG_USD": {"annual_vol": 0.22, "annual_drift": 0.05, "base_price": 24.50},
}

STOCK_PROFILES = {
    "SPY":  {"annual_vol": 0.15, "annual_drift": 0.10, "base_price": 520.0},
    "QQQ":  {"annual_vol": 0.20, "annual_drift": 0.12, "base_price": 450.0},
    "AAPL": {"annual_vol": 0.25, "annual_drift": 0.08, "base_price": 190.0},
    "NVDA": {"annual_vol": 0.45, "annual_drift": 0.25, "base_price": 900.0},
    "TSLA": {"annual_vol": 0.55, "annual_drift": 0.05, "base_price": 175.0},
    "AMD":  {"annual_vol": 0.40, "annual_drift": 0.15, "base_price": 160.0},
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data
# ─────────────────────────────────────────────────────────────────────────────

def fetch_kraken_ohlcv(symbol: str, timeframe: str, limit: int) -> pd.DataFrame | None:
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
        print(f"    [WARN] Kraken fetch failed for {symbol} {timeframe}: {e}")
        return None


def generate_synthetic_ohlcv(
    symbol: str, timeframe: str, n_bars: int,
    annual_vol: float, annual_drift: float, base_price: float,
) -> pd.DataFrame:
    np.random.seed(hash(symbol + timeframe) % (2**31))
    tf_minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
    minutes_per_bar = tf_minutes.get(timeframe, 60)
    bars_per_year = 365.25 * 24 * 60 / minutes_per_bar
    dt = 1.0 / bars_per_year
    mu_bar = annual_drift * dt
    sigma_bar = annual_vol * math.sqrt(dt)

    returns = np.random.normal(mu_bar, sigma_bar, n_bars)
    for i in range(1, len(returns)):
        returns[i] += 0.05 * returns[i - 1]

    close = np.zeros(n_bars)
    close[0] = base_price
    for i in range(1, n_bars):
        close[i] = close[i - 1] * (1 + returns[i])
        close[i] = max(close[i], base_price * 0.01)

    intrabar_vol = sigma_bar * 0.6
    high = close * (1 + np.abs(np.random.normal(0, intrabar_vol, n_bars)))
    low = close * (1 - np.abs(np.random.normal(0, intrabar_vol, n_bars)))
    open_prices = np.roll(close, 1) * (1 + np.random.normal(0, sigma_bar * 0.1, n_bars))
    open_prices[0] = base_price
    high = np.maximum(high, np.maximum(open_prices, close))
    low = np.minimum(low, np.minimum(open_prices, close))

    base_vol = 1_000_000 if base_price > 100 else 5_000_000
    volume = np.random.lognormal(mean=np.log(base_vol), sigma=0.5, size=n_bars)
    big_moves = np.abs(returns) > 2 * sigma_bar
    volume[big_moves] *= np.random.uniform(2.0, 4.0, big_moves.sum())

    end_time = datetime(2026, 3, 19, tzinfo=UTC)
    timestamps = pd.date_range(end=end_time, periods=n_bars, freq=f"{minutes_per_bar}min", tz=UTC)

    df = pd.DataFrame({
        "open": open_prices, "high": high, "low": low,
        "close": close, "volume": volume,
    }, index=pd.DatetimeIndex(timestamps, name="timestamp"))
    df.attrs["symbol"] = symbol
    return df


def get_data(symbol: str, timeframe: str, n_bars: int) -> tuple[pd.DataFrame | None, str]:
    """Fetch live or generate synthetic data. Returns (df, source)."""
    if "/" in symbol and "USDT" in symbol:
        df = fetch_kraken_ohlcv(symbol, timeframe, n_bars)
        if df is not None:
            return df, "kraken"
    profile = FOREX_PROFILES.get(symbol) or STOCK_PROFILES.get(symbol)
    if profile:
        return generate_synthetic_ohlcv(symbol, timeframe, n_bars, **profile), "synthetic"
    return None, "none"


# ─────────────────────────────────────────────────────────────────────────────
#  Strategy helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_strategy_class(name: str) -> type[BaseStrategy] | None:
    for cls in BaseStrategy.__subclasses__():
        if cls.name == name:
            return cls
    return None


def load_yaml_config() -> dict:
    with open(_ROOT / "config" / "strategies.yaml") as f:
        return yaml.safe_load(f)


@dataclass
class ProfileResult:
    strategy: str
    symbol: str
    profile: str
    data_source: str
    return_pct: float
    win_rate: float
    total_trades: int
    sharpe: float
    max_dd_pct: float
    profit_factor: float
    risk_per_trade: float
    atr_stop_mult: float
    rr_ratio: float


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def run_profile_test(
    strat_name: str,
    strat_cfg: dict,
    profiles: dict,
    all_symbols: list[str] | None = None,
) -> list[ProfileResult]:
    """Test all risk profiles for a single strategy across its symbols."""
    results = []
    cls = get_strategy_class(strat_name)
    if not cls:
        print(f"  [SKIP] {strat_name}: class not found")
        return results

    timeframe = strat_cfg.get("timeframe", "4h")
    symbols = all_symbols or strat_cfg.get("symbols", [])
    n_bars = {"5m": 2000, "15m": 2000, "1h": 2000, "4h": 1000, "1d": 500}.get(timeframe, 1000)
    base_params = strat_cfg.get("parameters", {})

    # Cache data
    data_cache = {}

    for profile_name, profile_cfg in profiles.items():
        print(f"\n  --- {strat_name} / {profile_name}: {profile_cfg['label']} ---")

        # Override params with risk profile
        params = deepcopy(base_params)
        for key in ("atr_stop_mult", "rr_ratio", "time_stop_bars"):
            if key in profile_cfg:
                params[key] = profile_cfg[key]

        try:
            strategy = cls(**params)
        except Exception as e:
            print(f"    [ERROR] Constructor failed: {e}")
            continue

        engine = BacktestEngine(
            initial_capital=INITIAL_CAPITAL,
            commission_pct=COMMISSION_PCT,
            regime_filter=True,
        )

        for symbol in symbols:
            cache_key = (symbol, timeframe)
            if cache_key not in data_cache:
                df, src = get_data(symbol, timeframe, n_bars)
                if df is None:
                    print(f"    [SKIP] {symbol}: no data")
                    continue
                data_cache[cache_key] = (df, src)

            df, data_source = data_cache[cache_key]
            df.attrs["symbol"] = symbol

            try:
                result: BacktestResult = engine.run(df, strategy)
            except Exception as e:
                print(f"    [ERROR] {symbol}: {e}")
                continue

            ret = result.total_return * 100
            wr = result.win_rate * 100
            trades = result.total_trades
            sharpe = result.sharpe_ratio
            max_dd = result.max_drawdown * 100
            pf = result.profit_factor

            icon = "+" if ret > 0 and trades >= 2 else "X"
            src_tag = "LIVE" if data_source == "kraken" else "SYN"
            print(
                f"    [{icon}] {symbol:12s} [{src_tag}] "
                f"Ret:{ret:+7.2f}%  WR:{wr:5.1f}%  "
                f"Trades:{trades:3d}  Sharpe:{sharpe:+6.2f}  "
                f"MaxDD:{max_dd:+6.1f}%  PF:{pf:.2f}"
            )

            results.append(ProfileResult(
                strategy=strat_name, symbol=symbol, profile=profile_name,
                data_source=data_source, return_pct=ret, win_rate=wr,
                total_trades=trades, sharpe=sharpe, max_dd_pct=max_dd,
                profit_factor=pf, risk_per_trade=profile_cfg["risk_per_trade"],
                atr_stop_mult=profile_cfg["atr_stop_mult"],
                rr_ratio=profile_cfg["rr_ratio"],
            ))

    return results


def print_comparison(results: list[ProfileResult]) -> None:
    """Print side-by-side comparison of risk profiles."""
    print("\n\n" + "=" * 100)
    print("  AGGRESSIVE RISK PROFILE COMPARISON")
    print("=" * 100)

    # Group by strategy + symbol
    by_pair: dict[tuple[str, str], list[ProfileResult]] = {}
    for r in results:
        key = (r.strategy, r.symbol)
        by_pair.setdefault(key, []).append(r)

    # Find best profile per pair
    best_profiles: dict[str, int] = {}  # profile_name -> count of "best" wins
    all_best = []

    print(f"\n{'Strategy':<22s} {'Symbol':<12s} {'Source':<6s} | "
          f"{'Conservative':>13s} {'Aggressive':>13s} {'Daredevil':>13s} {'Sniper/Wide':>13s} | {'BEST':>10s}")
    print("-" * 110)

    for (strat, sym), pair_results in sorted(by_pair.items()):
        src = pair_results[0].data_source[:4].upper()
        profile_returns = {}
        for r in pair_results:
            profile_returns[r.profile] = r.return_pct

        # Find best
        if profile_returns:
            best_name = max(profile_returns, key=profile_returns.get)
            best_ret = profile_returns[best_name]
            best_profiles[best_name] = best_profiles.get(best_name, 0) + 1
            all_best.append((strat, sym, best_name, best_ret))

        cols = []
        for pname in ["conservative", "aggressive", "daredevil"]:
            val = profile_returns.get(pname)
            cols.append(f"{val:+7.2f}%" if val is not None else "   N/A  ")

        # 4th profile varies by strategy
        fourth = "sniper" if strat == "donchian_breakout" else "wide_target"
        val = profile_returns.get(fourth)
        cols.append(f"{val:+7.2f}%" if val is not None else "   N/A  ")

        print(f"  {strat:<20s} {sym:<12s} {src:<6s} | "
              f"{cols[0]:>13s} {cols[1]:>13s} {cols[2]:>13s} {cols[3]:>13s} | "
              f"{best_name:>10s}")

    # Summary
    print(f"\n{'=' * 100}")
    print("  PROFILE WIN COUNT (how many symbol-pairs each profile won):")
    for pname, count in sorted(best_profiles.items(), key=lambda x: -x[1]):
        print(f"    {pname:<15s}: {count} wins")

    # Best overall portfolio per profile
    print(f"\n  PORTFOLIO-LEVEL RETURNS BY PROFILE:")
    by_profile: dict[str, list[float]] = {}
    for r in results:
        by_profile.setdefault(r.profile, []).append(r.return_pct)

    best_portfolio_profile = None
    best_portfolio_ret = -999

    for pname in ["conservative", "aggressive", "daredevil", "sniper", "wide_target"]:
        rets = by_profile.get(pname, [])
        if not rets:
            continue
        avg = np.mean(rets)
        go_count = sum(1 for r in rets if r > 0)
        if avg > best_portfolio_ret:
            best_portfolio_ret = avg
            best_portfolio_profile = pname
        print(f"    {pname:<15s}: avg {avg:+.2f}%, {go_count}/{len(rets)} profitable")

    print(f"\n  >>> RECOMMENDED PROFILE: {best_portfolio_profile} ({best_portfolio_ret:+.2f}% avg)")

    # Per-symbol recommendations
    print(f"\n  PER-SYMBOL OPTIMAL PROFILE:")
    for strat, sym, best, ret in sorted(all_best, key=lambda x: -x[3]):
        src = "LIVE" if any(r.data_source == "kraken" for r in by_pair.get((strat, sym), [])) else "SYN"
        print(f"    {strat:<20s} {sym:<12s} [{src}] -> {best:<15s} ({ret:+.2f}%)")

    print(f"\n{'=' * 100}")


def run_all_asset_classes() -> list[ProfileResult]:
    """Run aggressive tests across crypto, forex, gold, stocks."""
    cfg = load_yaml_config()
    all_results = []

    # ── 1. CRYPTO: Live Kraken data (most trustworthy) ──
    print("\n" + "=" * 100)
    print("  SECTION 1: CRYPTO (Live Kraken Data)")
    print("=" * 100)

    # Test Donchian Breakout with all profiles on ALL crypto symbols
    donchian_cfg = cfg["strategies"].get("donchian_breakout", {})
    all_results.extend(run_profile_test(
        "donchian_breakout", donchian_cfg, RISK_PROFILES,
        all_symbols=CRYPTO_SYMBOLS,
    ))

    # Test Smart Money with SMC profiles on ALL crypto symbols
    smart_money_cfg = cfg["strategies"].get("smart_money", {})
    all_results.extend(run_profile_test(
        "smart_money", smart_money_cfg, SMC_PROFILES,
        all_symbols=CRYPTO_SYMBOLS,
    ))

    # ── 2. FOREX + GOLD: Synthetic data ──
    print("\n\n" + "=" * 100)
    print("  SECTION 2: FOREX + GOLD (Synthetic Data)")
    print("=" * 100)

    forex_symbols = list(FOREX_PROFILES.keys())

    # Test Donchian on forex/gold
    forex_donchian_cfg = deepcopy(donchian_cfg)
    forex_donchian_cfg["timeframe"] = "4h"
    all_results.extend(run_profile_test(
        "donchian_breakout", forex_donchian_cfg, RISK_PROFILES,
        all_symbols=forex_symbols,
    ))

    # Test Smart Money on forex/gold
    all_results.extend(run_profile_test(
        "smart_money", smart_money_cfg, SMC_PROFILES,
        all_symbols=forex_symbols,
    ))

    # ── 3. STOCKS: Synthetic data ──
    print("\n\n" + "=" * 100)
    print("  SECTION 3: US STOCKS (Synthetic Data)")
    print("=" * 100)

    stock_symbols = list(STOCK_PROFILES.keys())

    # Test Donchian on stocks (daily)
    stock_donchian_cfg = deepcopy(donchian_cfg)
    stock_donchian_cfg["timeframe"] = "1d"
    all_results.extend(run_profile_test(
        "donchian_breakout", stock_donchian_cfg, RISK_PROFILES,
        all_symbols=stock_symbols,
    ))

    # Test Smart Money on stocks (4h)
    all_results.extend(run_profile_test(
        "smart_money", smart_money_cfg, SMC_PROFILES,
        all_symbols=stock_symbols,
    ))

    return all_results


if __name__ == "__main__":
    start = time.time()
    results = run_all_asset_classes()
    elapsed = time.time() - start
    print(f"\n  [Full test took {elapsed:.1f}s across {len(results)} profile-symbol tests]")
    print_comparison(results)
