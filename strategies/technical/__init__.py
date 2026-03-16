"""
strategies/technical — All technical-analysis-based strategies.

Importing this package triggers registration of every strategy with StrategyRegistry.
"""

from strategies.technical.indicators import (  # noqa: F401 — side-effect: makes helpers importable
    rsi,
    ema,
    sma,
    macd,
    bollinger_bands,
    atr,
    vwap,
    stochastic_rsi,
    adx,
    ichimoku,
    volume_profile,
    pivot_points,
    fibonacci_levels,
)

# Import strategy modules so their classes self-register via BaseStrategy.__init_subclass__
from strategies.technical import ema_crossover  # noqa: F401
from strategies.technical import rsi_mean_reversion  # noqa: F401
from strategies.technical import bollinger_squeeze  # noqa: F401
from strategies.technical import vwap_bounce  # noqa: F401
from strategies.technical import multi_timeframe  # noqa: F401
from strategies.technical import london_breakout  # noqa: F401
from strategies.technical import opening_range  # noqa: F401
from strategies.technical import ichimoku_trend  # noqa: F401
from strategies.technical import smart_money  # noqa: F401

__all__ = [
    "rsi",
    "ema",
    "sma",
    "macd",
    "bollinger_bands",
    "atr",
    "vwap",
    "stochastic_rsi",
    "adx",
    "ichimoku",
    "volume_profile",
    "pivot_points",
    "fibonacci_levels",
]
