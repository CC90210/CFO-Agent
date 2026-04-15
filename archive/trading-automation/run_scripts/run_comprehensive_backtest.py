"""
run_comprehensive_backtest.py — ATLAS Comprehensive Backtest: ALL 12 Enabled Strategies

Fetches real crypto data from Kraken (free, no API key).
Generates synthetic data for stocks, forex, gold, and sectors.
Runs backtests for every strategy x symbol combination.
Prints a full profitability report.

Usage:
    python run_comprehensive_backtest.py
"""
import asyncio
import logging
import math
import sys
import warnings
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

# Suppress noisy warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("atlas.comprehensive_backtest")
logger.setLevel(logging.INFO)

# ─── Import ATLAS components ─────────────────────────────────────────────────
from backtesting.engine import BacktestEngine
from strategies.base import StrategyRegistry

# Trigger strategy auto-registration
import strategies.technical  # noqa: F401


# ═══════════════════════════════════════════════════════════════════════════════
# SYNTHETIC DATA GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_stock_ohlcv(
    symbol: str,
    bars: int = 500,
    timeframe: str = "1d",
    start_price: float | None = None,
    annual_vol: float | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate realistic synthetic stock OHLCV data."""
    rng = np.random.default_rng(seed)

    # Symbol-specific parameters
    stock_params = {
        "SPY":  {"price": 520.0, "vol": 0.14, "drift": 0.08},
        "QQQ":  {"price": 440.0, "vol": 0.18, "drift": 0.10},
        "AAPL": {"price": 195.0, "vol": 0.22, "drift": 0.12},
        "MSFT": {"price": 420.0, "vol": 0.20, "drift": 0.10},
        "NVDA": {"price": 880.0, "vol": 0.35, "drift": 0.15},
        "AMZN": {"price": 185.0, "vol": 0.25, "drift": 0.12},
        "META": {"price": 500.0, "vol": 0.28, "drift": 0.12},
        "GOOG": {"price": 155.0, "vol": 0.22, "drift": 0.10},
        "TSLA": {"price": 250.0, "vol": 0.45, "drift": 0.05},
        "AMD":  {"price": 160.0, "vol": 0.35, "drift": 0.10},
        # Sector ETFs
        "XLK":  {"price": 210.0, "vol": 0.18, "drift": 0.12},
        "XLF":  {"price": 42.0,  "vol": 0.16, "drift": 0.08},
        "XLE":  {"price": 90.0,  "vol": 0.22, "drift": 0.06},
        "XLV":  {"price": 145.0, "vol": 0.14, "drift": 0.07},
        "XLI":  {"price": 120.0, "vol": 0.16, "drift": 0.08},
        "XLC":  {"price": 80.0,  "vol": 0.20, "drift": 0.10},
        "XLY":  {"price": 185.0, "vol": 0.20, "drift": 0.09},
        "XLP":  {"price": 78.0,  "vol": 0.12, "drift": 0.05},
        "XLU":  {"price": 70.0,  "vol": 0.14, "drift": 0.04},
        "XLRE": {"price": 40.0,  "vol": 0.18, "drift": 0.06},
        "XLB":  {"price": 88.0,  "vol": 0.18, "drift": 0.07},
    }

    params = stock_params.get(symbol, {"price": 100.0, "vol": 0.20, "drift": 0.08})
    price = start_price or params["price"]
    vol = annual_vol or params["vol"]
    drift = params["drift"]

    # Timeframe to bars-per-year mapping
    tf_map = {"1d": 252, "4h": 252 * 6, "1h": 252 * 7, "5m": 252 * 78}
    bars_per_year = tf_map.get(timeframe, 252)
    dt_per_bar = vol / math.sqrt(bars_per_year)
    drift_per_bar = drift / bars_per_year

    # Generate with mean reversion (Ornstein-Uhlenbeck-like)
    log_prices = [math.log(price)]
    mean_level = math.log(price)
    mean_reversion_speed = 0.002  # gentle pull to mean

    for _ in range(bars - 1):
        shock = rng.normal(drift_per_bar, dt_per_bar)
        reversion = mean_reversion_speed * (mean_level - log_prices[-1])
        log_prices.append(log_prices[-1] + shock + reversion)

    closes = np.exp(log_prices)

    # Generate OHLC from close
    intrabar_vol = dt_per_bar * 0.6
    highs = closes * (1 + np.abs(rng.normal(0, intrabar_vol, bars)))
    lows = closes * (1 - np.abs(rng.normal(0, intrabar_vol, bars)))
    opens = np.roll(closes, 1)
    opens[0] = price

    # Ensure OHLC consistency
    highs = np.maximum(highs, np.maximum(opens, closes))
    lows = np.minimum(lows, np.minimum(opens, closes))

    # Volume: base + random + trend correlation
    base_vol = 10_000_000 if symbol in ("SPY", "QQQ") else 2_000_000
    volumes = base_vol * (1 + 0.3 * np.abs(rng.normal(0, 1, bars)))
    # Higher volume on big moves
    returns = np.diff(closes, prepend=closes[0]) / closes
    volumes *= (1 + 2 * np.abs(returns))

    # Timestamps
    if timeframe == "1d":
        freq = "B"  # business days
    elif timeframe == "4h":
        freq = "4h"
    elif timeframe == "1h":
        freq = "1h"
    elif timeframe == "5m":
        freq = "5min"
    else:
        freq = "1h"

    # For 5m data, generate within market hours (9:30-16:00 ET = 13:30-20:00 UTC)
    if timeframe == "5m":
        dates = _generate_market_hours_index(bars, freq="5min")
        # Trim arrays to match dates length if needed
        n = len(dates)
        opens, highs, lows, closes, volumes = opens[:n], highs[:n], lows[:n], closes[:n], volumes[:n]
    elif timeframe == "1d":
        end = datetime(2026, 3, 19, tzinfo=timezone.utc)
        dates = pd.bdate_range(end=end, periods=bars, tz=timezone.utc)
    else:
        end = datetime(2026, 3, 19, 20, 0, tzinfo=timezone.utc)
        dates = pd.date_range(end=end, periods=bars, freq=freq, tz=timezone.utc)

    n = min(len(dates), len(closes))
    df = pd.DataFrame({
        "open": opens[:n],
        "high": highs[:n],
        "low": lows[:n],
        "close": closes[:n],
        "volume": volumes[:n],
    }, index=dates[:n])

    df.index.name = "timestamp"
    return df


def _generate_market_hours_index(bars: int, freq: str = "5min") -> pd.DatetimeIndex:
    """Generate timestamps only during US market hours (13:30-20:00 UTC)."""
    # Generate way more than needed, then filter to market hours
    end = datetime(2026, 3, 19, 20, 0, tzinfo=timezone.utc)
    all_dates = pd.date_range(end=end, periods=bars * 5, freq=freq, tz=timezone.utc)
    # Filter to market hours (13:30-20:00 UTC = 9:30-16:00 ET)
    market_hours = all_dates[
        (all_dates.hour * 60 + all_dates.minute >= 13 * 60 + 30) &
        (all_dates.hour * 60 + all_dates.minute < 20 * 60) &
        (all_dates.dayofweek < 5)  # weekdays only
    ]
    return market_hours[-bars:]


def generate_forex_ohlcv(
    symbol: str,
    bars: int = 720,
    timeframe: str = "1h",
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate realistic synthetic forex OHLCV data."""
    rng = np.random.default_rng(seed)

    forex_params = {
        "EUR_USD": {"price": 1.0850, "vol": 0.07, "drift": 0.0},
        "GBP_USD": {"price": 1.2650, "vol": 0.08, "drift": 0.0},
        "USD_JPY": {"price": 150.50, "vol": 0.08, "drift": 0.0},
        "AUD_USD": {"price": 0.6550, "vol": 0.09, "drift": 0.0},
        "USD_CAD": {"price": 1.3550, "vol": 0.06, "drift": 0.0},
        "EUR_GBP": {"price": 0.8580, "vol": 0.06, "drift": 0.0},
    }

    params = forex_params.get(symbol, {"price": 1.0, "vol": 0.08, "drift": 0.0})
    price = params["price"]
    vol = params["vol"]

    tf_map = {"5m": 365 * 24 * 12, "1h": 365 * 24, "4h": 365 * 6}
    bars_per_year = tf_map.get(timeframe, 365 * 24)
    dt_per_bar = vol / math.sqrt(bars_per_year)

    # Forex has strong mean reversion
    log_prices = [math.log(price)]
    mean_level = math.log(price)
    mr_speed = 0.003

    for _ in range(bars - 1):
        shock = rng.normal(0, dt_per_bar)
        reversion = mr_speed * (mean_level - log_prices[-1])
        log_prices.append(log_prices[-1] + shock + reversion)

    closes = np.exp(log_prices)

    # Tight intrabar range for forex
    intrabar_vol = dt_per_bar * 0.4
    highs = closes * (1 + np.abs(rng.normal(0, intrabar_vol, bars)))
    lows = closes * (1 - np.abs(rng.normal(0, intrabar_vol, bars)))
    opens = np.roll(closes, 1)
    opens[0] = price

    highs = np.maximum(highs, np.maximum(opens, closes))
    lows = np.minimum(lows, np.minimum(opens, closes))

    # Forex volume is tick count (synthetic)
    volumes = 5000 * (1 + 0.5 * np.abs(rng.normal(0, 1, bars)))
    # Session-based volume pattern (London/NY overlap highest)
    if timeframe in ("1h", "5m"):
        freq_map = {"5m": "5min", "1h": "1h", "4h": "4h"}
        end = datetime(2026, 3, 19, 20, 0, tzinfo=timezone.utc)
        dates = pd.date_range(end=end, periods=bars, freq=freq_map.get(timeframe, "1h"), tz=timezone.utc)
        hours = dates.hour
        # London (7-16 UTC) and NY (13-21 UTC) sessions have higher volume
        session_mult = np.where(
            (hours >= 13) & (hours <= 16), 2.0,  # overlap
            np.where((hours >= 7) & (hours <= 21), 1.5, 0.7)
        )
        volumes *= session_mult
    else:
        end = datetime(2026, 3, 19, 20, 0, tzinfo=timezone.utc)
        freq_map = {"4h": "4h"}
        dates = pd.date_range(end=end, periods=bars, freq=freq_map.get(timeframe, "4h"), tz=timezone.utc)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }, index=dates[:bars])
    df.index.name = "timestamp"
    return df


def generate_gold_ohlcv(
    symbol: str,
    bars: int = 720,
    timeframe: str = "4h",
    seed: int | None = None,
) -> pd.DataFrame:
    """Generate realistic synthetic gold/silver OHLCV data."""
    rng = np.random.default_rng(seed)

    gold_params = {
        "XAU_USD": {"price": 2180.0, "vol": 0.14, "drift": 0.06},
        "XAG_USD": {"price": 25.50, "vol": 0.22, "drift": 0.04},
    }

    params = gold_params.get(symbol, {"price": 2000.0, "vol": 0.15, "drift": 0.05})
    price = params["price"]
    vol = params["vol"]
    drift = params["drift"]

    tf_map = {"4h": 365 * 6, "1h": 365 * 24, "1d": 252}
    bars_per_year = tf_map.get(timeframe, 365 * 6)
    dt_per_bar = vol / math.sqrt(bars_per_year)
    drift_per_bar = drift / bars_per_year

    # Gold trends strongly — less mean reversion
    log_prices = [math.log(price)]
    for _ in range(bars - 1):
        shock = rng.normal(drift_per_bar, dt_per_bar)
        log_prices.append(log_prices[-1] + shock)

    closes = np.exp(log_prices)
    intrabar_vol = dt_per_bar * 0.5
    highs = closes * (1 + np.abs(rng.normal(0, intrabar_vol, bars)))
    lows = closes * (1 - np.abs(rng.normal(0, intrabar_vol, bars)))
    opens = np.roll(closes, 1)
    opens[0] = price

    highs = np.maximum(highs, np.maximum(opens, closes))
    lows = np.minimum(lows, np.minimum(opens, closes))

    volumes = 50000 * (1 + 0.4 * np.abs(rng.normal(0, 1, bars)))

    end = datetime(2026, 3, 19, 20, 0, tzinfo=timezone.utc)
    freq_map = {"4h": "4h", "1h": "1h", "1d": "B"}
    dates = pd.date_range(end=end, periods=bars, freq=freq_map.get(timeframe, "4h"), tz=timezone.utc)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }, index=dates[:bars])
    df.index.name = "timestamp"
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# KRAKEN DATA FETCHER (direct ccxt, no API key needed)
# ═══════════════════════════════════════════════════════════════════════════════

async def fetch_kraken_ohlcv(symbol: str, timeframe: str, limit: int = 720) -> pd.DataFrame | None:
    """Fetch OHLCV data from Kraken exchange (free, no API key)."""
    import ccxt.async_support as ccxt_async

    exchange = ccxt_async.kraken({
        "enableRateLimit": True,
        "timeout": 30000,
    })

    try:
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not ohlcv or len(ohlcv) < 100:
            logger.warning("  Insufficient data for %s/%s: %d bars", symbol, timeframe, len(ohlcv) if ohlcv else 0)
            return None

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df = df.astype(float)
        return df
    except Exception as e:
        logger.warning("  Failed to fetch %s/%s from Kraken: %s", symbol, timeframe, e)
        return None
    finally:
        await exchange.close()


# ═══════════════════════════════════════════════════════════════════════════════
# STRATEGY-SYMBOL CONFIGURATION (all 12 enabled strategies)
# ═══════════════════════════════════════════════════════════════════════════════

ENABLED_STRATEGIES = {
    # 1. London Breakout — forex 5m
    "london_breakout": {
        "timeframe": "5m",
        "symbols": ["EUR_USD", "GBP_USD", "EUR_GBP"],
        "asset_class": "forex",
        "bars": 720,
    },
    # 2. Opening Range — stocks 5m
    "opening_range": {
        "timeframe": "5m",
        "symbols": ["SPY", "QQQ", "AAPL", "TSLA", "NVDA"],
        "asset_class": "stock",
        "bars": 720,
    },
    # 3. Smart Money — crypto 4h (+ stocks/forex/gold via synthetic)
    "smart_money": {
        "timeframe": "4h",
        "crypto_symbols": ["ETH/USDT", "XRP/USDT", "SOL/USDT", "DOGE/USDT"],
        "stock_symbols": ["SPY", "AAPL", "NVDA"],
        "forex_symbols": ["EUR_USD", "GBP_USD"],
        "gold_symbols": ["XAU_USD"],
        "asset_class": "mixed",
        "bars": 720,
    },
    # 4. Equity Mean Reversion — stocks 4h
    "equity_mean_reversion": {
        "timeframe": "4h",
        "symbols": ["SPY", "QQQ", "AAPL", "NVDA", "MSFT", "AMZN", "TSLA", "AMD"],
        "asset_class": "stock",
        "bars": 720,
    },
    # 5. Forex Session Momentum — forex+gold 1h
    "forex_session_momentum": {
        "timeframe": "1h",
        "symbols": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "XAU_USD"],
        "asset_class": "forex_gold",
        "bars": 720,
    },
    # 6. Gold Trend Follower — gold 4h
    "gold_trend_follower": {
        "timeframe": "4h",
        "symbols": ["XAU_USD", "XAG_USD"],
        "asset_class": "gold",
        "bars": 720,
    },
    # 7. IBS Mean Reversion — stocks 1d
    "ibs_mean_reversion": {
        "timeframe": "1d",
        "symbols": ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOG"],
        "asset_class": "stock",
        "bars": 500,
    },
    # 8. Stock Gap Fade — stocks 5m
    "stock_gap_fade": {
        "timeframe": "5m",
        "symbols": ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "AMD"],
        "asset_class": "stock",
        "bars": 720,
    },
    # 9. Connors RSI — stocks 1d
    "connors_rsi": {
        "timeframe": "1d",
        "symbols": ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOG"],
        "asset_class": "stock",
        "bars": 500,
    },
    # 10. Sector Rotation — sectors 1d
    "sector_rotation": {
        "timeframe": "1d",
        "symbols": ["XLK", "XLF", "XLE", "XLV", "XLI", "XLC", "XLY", "XLP", "XLU", "XLRE", "XLB"],
        "asset_class": "stock",
        "bars": 500,
    },
    # 11. Forex Carry Momentum — forex 4h
    "forex_carry_momentum": {
        "timeframe": "4h",
        "symbols": ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "EUR_GBP"],
        "asset_class": "forex",
        "bars": 720,
    },
    # 12. Donchian Breakout — crypto 4h (+ gold/forex via synthetic)
    "donchian_breakout": {
        "timeframe": "4h",
        "crypto_symbols": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT", "DOT/USDT",
                           "DOGE/USDT", "XRP/USDT", "AVAX/USDT", "LINK/USDT"],
        "gold_symbols": ["XAU_USD", "XAG_USD"],
        "forex_symbols": ["EUR_USD", "GBP_USD", "USD_JPY"],
        "asset_class": "mixed",
        "bars": 720,
    },
}

# All crypto symbols to fetch from Kraken
ALL_CRYPTO_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT",
    "ADA/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT",
]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN BACKTEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def run_comprehensive_backtests():
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.001,
        risk_per_trade_pct=0.015,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # Disabled per feedback
    )

    results = []

    # ── Step 1: Fetch real crypto data from Kraken ──
    logger.info("=" * 80)
    logger.info("  ATLAS COMPREHENSIVE BACKTEST — ALL 12 ENABLED STRATEGIES")
    logger.info("  Date: %s", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    logger.info("=" * 80)

    logger.info("\n[1/4] Fetching crypto data from Kraken (free, no API key)...")
    crypto_data: dict[str, pd.DataFrame] = {}

    for symbol in ALL_CRYPTO_SYMBOLS:
        logger.info("  Fetching %s 4h...", symbol)
        df = await fetch_kraken_ohlcv(symbol, "4h", limit=720)
        if df is not None:
            crypto_data[symbol] = df
            logger.info("    OK: %d bars (%s to %s)",
                       len(df), df.index[0].strftime("%Y-%m-%d"), df.index[-1].strftime("%Y-%m-%d"))
        else:
            logger.warning("    FAILED: %s", symbol)

    # ── Step 2: Generate synthetic data for non-crypto ──
    logger.info("\n[2/4] Generating synthetic data for stocks, forex, gold...")

    synthetic_data: dict[str, dict[str, pd.DataFrame]] = {}  # {symbol: {timeframe: df}}

    # Stock data (multiple timeframes needed)
    all_stock_symbols = set()
    for config in ENABLED_STRATEGIES.values():
        if config.get("asset_class") == "stock":
            all_stock_symbols.update(config["symbols"])
        if "stock_symbols" in config:
            all_stock_symbols.update(config["stock_symbols"])

    for symbol in sorted(all_stock_symbols):
        synthetic_data[symbol] = {}
        for tf in ["5m", "4h", "1d"]:
            bars = 720 if tf != "1d" else 500
            seed = hash(f"{symbol}_{tf}") % (2**31)
            df = generate_stock_ohlcv(symbol, bars=bars, timeframe=tf, seed=seed)
            synthetic_data[symbol][tf] = df
        logger.info("  Generated %s: 5m/4h/1d", symbol)

    # Forex data
    all_forex_symbols = set()
    for config in ENABLED_STRATEGIES.values():
        if config.get("asset_class") in ("forex", "forex_gold"):
            for s in config.get("symbols", []):
                if s.startswith(("EUR", "GBP", "USD", "AUD")):
                    all_forex_symbols.add(s)
        if "forex_symbols" in config:
            all_forex_symbols.update(config["forex_symbols"])

    for symbol in sorted(all_forex_symbols):
        synthetic_data[symbol] = {}
        for tf in ["5m", "1h", "4h"]:
            bars = 720
            seed = hash(f"{symbol}_{tf}") % (2**31)
            df = generate_forex_ohlcv(symbol, bars=bars, timeframe=tf, seed=seed)
            synthetic_data[symbol][tf] = df
        logger.info("  Generated %s: 5m/1h/4h", symbol)

    # Gold data
    all_gold_symbols = set()
    for config in ENABLED_STRATEGIES.values():
        if config.get("asset_class") in ("gold", "forex_gold"):
            for s in config.get("symbols", []):
                if s.startswith(("XAU", "XAG")):
                    all_gold_symbols.add(s)
        if "gold_symbols" in config:
            all_gold_symbols.update(config["gold_symbols"])

    for symbol in sorted(all_gold_symbols):
        synthetic_data[symbol] = {}
        for tf in ["1h", "4h"]:
            bars = 720
            seed = hash(f"{symbol}_{tf}") % (2**31)
            df = generate_gold_ohlcv(symbol, bars=bars, timeframe=tf, seed=seed)
            synthetic_data[symbol][tf] = df
        logger.info("  Generated %s: 1h/4h", symbol)

    # ── Step 3: Run all backtests ──
    logger.info("\n[3/4] Running backtests for all 12 strategies...")
    logger.info("=" * 80)

    for strat_name, config in ENABLED_STRATEGIES.items():
        tf = config["timeframe"]

        # Get strategy class
        try:
            strategy_class = StrategyRegistry.get(strat_name)
        except KeyError:
            logger.error("  Strategy '%s' not registered — skipping", strat_name)
            continue

        logger.info("\n--- %s (tf: %s) ---", strat_name, tf)

        # Build symbol list and data source
        symbols_to_test = []

        if config["asset_class"] == "mixed":
            # Mixed strategies have separate crypto/stock/forex/gold lists
            for sym in config.get("crypto_symbols", []):
                if sym in crypto_data:
                    symbols_to_test.append((sym, crypto_data[sym], "kraken"))
            for sym in config.get("stock_symbols", []):
                if sym in synthetic_data and tf in synthetic_data[sym]:
                    symbols_to_test.append((sym, synthetic_data[sym][tf], "synthetic"))
            for sym in config.get("forex_symbols", []):
                if sym in synthetic_data and tf in synthetic_data[sym]:
                    symbols_to_test.append((sym, synthetic_data[sym][tf], "synthetic"))
            for sym in config.get("gold_symbols", []):
                if sym in synthetic_data and tf in synthetic_data[sym]:
                    symbols_to_test.append((sym, synthetic_data[sym][tf], "synthetic"))
        else:
            for sym in config["symbols"]:
                if sym in crypto_data:
                    symbols_to_test.append((sym, crypto_data[sym], "kraken"))
                elif sym in synthetic_data and tf in synthetic_data[sym]:
                    symbols_to_test.append((sym, synthetic_data[sym][tf], "synthetic"))

        for sym, df, source in symbols_to_test:
            strategy = strategy_class()

            if len(df) < 200:
                logger.warning("  %s: insufficient data (%d bars)", sym, len(df))
                continue

            try:
                result = engine.run(df, strategy)

                ret = result.total_return * 100
                wr = result.win_rate * 100
                dd = result.max_drawdown * 100
                trades = result.total_trades
                sharpe = result.sharpe_ratio

                # GO/NO-GO criteria
                is_go = (result.total_return > 0 and result.win_rate > 0.20 and result.total_trades >= 2)
                status = "GO" if is_go else "NO-GO"

                results.append({
                    "strategy": strat_name,
                    "symbol": sym,
                    "timeframe": tf,
                    "source": source,
                    "total_return": result.total_return,
                    "win_rate": result.win_rate,
                    "total_trades": result.total_trades,
                    "sharpe": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "profit_factor": result.profit_factor,
                    "status": status,
                })

                logger.info("  %s [%s]: %+.2f%% | WR:%.0f%% | %d trades | Sharpe:%.2f | DD:%.1f%% | %s",
                           sym, source, ret, wr, trades, sharpe, dd, status)

            except Exception as e:
                logger.error("  %s: ERROR — %s", sym, str(e)[:100])
                results.append({
                    "strategy": strat_name,
                    "symbol": sym,
                    "timeframe": tf,
                    "source": "error",
                    "total_return": 0.0,
                    "win_rate": 0.0,
                    "total_trades": 0,
                    "sharpe": 0.0,
                    "max_drawdown": 0.0,
                    "profit_factor": 0.0,
                    "status": "ERROR",
                })

    # ═══════════════════════════════════════════════════════════════════════════
    # RESULTS REPORT
    # ═══════════════════════════════════════════════════════════════════════════
    logger.info("\n[4/4] Generating report...")

    print("\n")
    print("=" * 120)
    print("  ATLAS COMPREHENSIVE BACKTEST REPORT — ALL 12 ENABLED STRATEGIES")
    print(f"  Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 120)
    print(f"{'Strategy':<25} {'Symbol':<12} {'Source':<10} {'Return%':>9} {'WinRate%':>9} {'Trades':>7} {'Sharpe':>8} {'MaxDD%':>9} {'Status':>8}")
    print("-" * 120)

    go_count = 0
    nogo_count = 0
    error_count = 0

    for r in sorted(results, key=lambda x: (x["strategy"], -x["total_return"])):
        ret = r["total_return"] * 100
        wr = r["win_rate"] * 100
        dd = r["max_drawdown"] * 100
        status = r["status"]

        if status == "GO":
            go_count += 1
        elif status == "ERROR":
            error_count += 1
        else:
            nogo_count += 1

        print(f"{r['strategy']:<25} {r['symbol']:<12} {r['source']:<10} {ret:>+8.2f}% {wr:>8.1f}% {r['total_trades']:>7} {r['sharpe']:>8.2f} {dd:>+8.2f}% {status:>8}")

    print("-" * 120)

    # ── Summary ──
    valid_results = [r for r in results if r["status"] != "ERROR"]
    if valid_results:
        avg_return = sum(r["total_return"] for r in valid_results) / len(valid_results) * 100
        go_results = [r for r in valid_results if r["status"] == "GO"]
        avg_go_return = sum(r["total_return"] for r in go_results) / len(go_results) * 100 if go_results else 0
    else:
        avg_return = 0
        avg_go_return = 0

    print(f"\n  SUMMARY")
    print(f"  {'='*60}")
    print(f"  Total strategy-symbol pairs tested : {len(results)}")
    print(f"  GO (profitable + WR>20% + 2+ trades): {go_count}")
    print(f"  NO-GO                               : {nogo_count}")
    print(f"  ERROR                               : {error_count}")
    print(f"  Average return (all valid)          : {avg_return:+.2f}%")
    print(f"  Average return (GO pairs only)      : {avg_go_return:+.2f}%")

    # ── Per-Strategy Summary ──
    print(f"\n\n  STRATEGY-LEVEL SUMMARY")
    print(f"  {'='*90}")
    print(f"  {'#':>3} {'Strategy':<25} {'Pairs':>6} {'GO':>4} {'Avg Ret%':>10} {'Avg Sharpe':>11} {'Verdict':>10}")
    print(f"  {'-'*90}")

    strategy_groups: dict[str, list[dict]] = {}
    for r in results:
        if r["status"] != "ERROR":
            strategy_groups.setdefault(r["strategy"], []).append(r)

    ranked = sorted(
        strategy_groups.items(),
        key=lambda x: sum(r["total_return"] for r in x[1]) / len(x[1]),
        reverse=True,
    )

    total_portfolio_return = 0.0
    n_strategies = 0

    for rank, (strat_name, strat_results) in enumerate(ranked, 1):
        avg_ret = sum(r["total_return"] for r in strat_results) / len(strat_results) * 100
        avg_sharpe = sum(r["sharpe"] for r in strat_results) / len(strat_results)
        n_go = sum(1 for r in strat_results if r["status"] == "GO")
        n_total = len(strat_results)

        total_portfolio_return += avg_ret
        n_strategies += 1

        if avg_ret > 1.0 and n_go / n_total >= 0.4:
            verdict = "STRONG"
        elif avg_ret > 0:
            verdict = "MARGINAL"
        else:
            verdict = "WEAK"

        print(f"  {rank:>3} {strat_name:<25} {n_total:>6} {n_go:>4} {avg_ret:>+9.2f}% {avg_sharpe:>10.2f} {verdict:>10}")

    print(f"  {'-'*90}")
    portfolio_avg = total_portfolio_return / n_strategies if n_strategies > 0 else 0
    print(f"  Overall portfolio expected return (equal weight): {portfolio_avg:+.2f}%")
    print(f"  {'='*90}")

    # Save CSV
    try:
        df_results = pd.DataFrame(results)
        df_results.to_csv("logs/comprehensive_backtest_results.csv", index=False)
        print(f"\n  Results saved to logs/comprehensive_backtest_results.csv")
    except Exception as e:
        print(f"\n  Could not save CSV: {e}")

    print()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_backtests())
