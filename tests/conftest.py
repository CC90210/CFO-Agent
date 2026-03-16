"""
tests/conftest.py — Shared pytest fixtures for the Atlas test suite.

All fixtures produce self-contained, deterministic data that requires no
exchange connection, no API keys, and no database. Tests using these
fixtures are safe to run in CI with zero secrets.

Fixtures
--------
sample_ohlcv_data       100-candle realistic OHLCV DataFrame
trending_data           Clear uptrend with consistent higher-highs
ranging_data            Sideways chop between two levels
volatile_data           High-volatility candles (spiky ATR)
sample_portfolio        Mock portfolio dict used by risk/strategy tests
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ohlcv(
    n: int = 100,
    start_price: float = 100.0,
    drift: float = 0.0,
    vol: float = 0.015,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a synthetic OHLCV DataFrame.

    Parameters
    ----------
    n          : number of candles
    start_price: first close price
    drift      : daily drift (0.002 = 0.2 % per bar uptrend)
    vol        : volatility per bar as a fraction of price
    seed       : random seed for reproducibility

    Returns
    -------
    pd.DataFrame with columns open, high, low, close, volume
    and a UTC DatetimeIndex at 1-hour resolution.
    """
    rng = np.random.default_rng(seed)

    # Generate log-normal close prices
    log_returns = rng.normal(loc=drift, scale=vol, size=n)
    close = start_price * np.exp(np.cumsum(log_returns))

    # Generate realistic OHLC from close
    noise = rng.uniform(0.003, 0.012, size=n)    # candle range as fraction
    open_ = np.empty(n)
    open_[0] = start_price
    open_[1:] = close[:-1] * (1.0 + rng.normal(0.0, 0.003, size=n - 1))

    high = np.maximum(open_, close) * (1.0 + noise)
    low = np.minimum(open_, close) * (1.0 - noise)

    # Volume: base + random spike
    volume = (
        rng.lognormal(mean=10.0, sigma=0.5, size=n) * 1000.0
    )

    index = pd.date_range(start="2024-01-01 00:00:00", periods=n, freq="1h", tz="UTC")

    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
        index=index,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_ohlcv_data() -> pd.DataFrame:
    """
    100 candles of realistic OHLCV at 1-hour resolution.

    No strong trend or pattern — general-purpose fixture.
    """
    return _make_ohlcv(n=100, start_price=100.0, drift=0.0001, vol=0.012, seed=42)


@pytest.fixture()
def trending_data() -> pd.DataFrame:
    """
    200 candles with a clear uptrend (drift = +0.3 % / bar).

    Use for testing trend-following and momentum strategies.
    Prices move from ~100 to ~180 over the period.
    """
    return _make_ohlcv(n=200, start_price=100.0, drift=0.003, vol=0.008, seed=7)


@pytest.fixture()
def ranging_data() -> pd.DataFrame:
    """
    200 candles of sideways chop oscillating around 100.

    Achieved by mean-reverting: each return is heavily dampened back toward 0.
    Use for testing mean-reversion and RSI strategies.
    """
    rng = np.random.default_rng(99)
    n = 200
    close = np.empty(n)
    close[0] = 100.0
    for i in range(1, n):
        # Mean-reverting process: pull toward 100 with noise
        shock = rng.normal(0.0, 0.010)
        mean_pull = -0.15 * (close[i - 1] - 100.0) / 100.0
        close[i] = close[i - 1] * (1.0 + mean_pull + shock)

    # Clip to realistic range
    close = np.clip(close, 80.0, 120.0)

    noise = rng.uniform(0.004, 0.010, size=n)
    open_ = np.empty(n)
    open_[0] = 100.0
    open_[1:] = close[:-1]
    high = np.maximum(open_, close) * (1.0 + noise)
    low = np.minimum(open_, close) * (1.0 - noise)
    volume = rng.lognormal(mean=10.0, sigma=0.4, size=n) * 1000.0

    index = pd.date_range("2024-06-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )


@pytest.fixture()
def volatile_data() -> pd.DataFrame:
    """
    100 candles with very high volatility (vol = 4 % per bar).

    Useful for stress-testing risk management and kill switches.
    """
    return _make_ohlcv(n=100, start_price=50_000.0, drift=0.0, vol=0.04, seed=13)


@pytest.fixture()
def sample_portfolio() -> dict:
    """
    A mock portfolio dict representing a realistic open-positions state.

    Used by risk manager and position sizer tests.
    """
    return {
        "equity": 10_000.0,
        "peak_equity": 11_200.0,
        "day_start_equity": 10_500.0,
        "positions": {
            "BTC/USDT": {
                "side": "LONG",
                "entry_price": 65_000.0,
                "size": 0.02,
                "stop_loss": 63_000.0,
                "take_profit": 71_000.0,
                "unrealised_pnl": -200.0,
            }
        },
        "open_position_count": 1,
    }


@pytest.fixture()
def deterministic_trades() -> list[dict]:
    """
    20 pre-computed trades with known net PnLs.

    Used by Monte Carlo tests where we need to verify distributions
    against hand-calculated expected values.

    Win rate = 0.60 (12 wins, 8 losses)
    Avg win  = +$150
    Avg loss = -$100
    Expectancy = 0.60 × 150 + 0.40 × (-100) = +$50
    """
    wins = [{"net_pnl": 150.0}] * 12
    losses = [{"net_pnl": -100.0}] * 8
    return wins + losses
