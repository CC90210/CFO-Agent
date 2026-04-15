"""
strategies — Atlas trading strategy library.

This package contains:
    - strategies.base          : BaseStrategy ABC, Signal, Position, TradeResult, StrategyRegistry
    - strategies.technical     : All technical analysis strategies (9 strategies)
    - strategies.sentiment     : Sentiment-based strategies (future expansion)

Quick start
-----------
    from strategies import StrategyRegistry

    # Auto-import triggers self-registration
    import strategies.technical  # noqa: F401

    print(StrategyRegistry.list())
    # ['bollinger_squeeze', 'ema_crossover', 'ichimoku_trend', 'london_breakout',
    #  'multi_timeframe', 'opening_range', 'rsi_mean_reversion', 'smart_money', 'vwap_bounce']

    strategy = StrategyRegistry.build("ema_crossover")
    signal = strategy.analyze(df)

Or use the convenience imports below to get everything in one import.
"""

from strategies.base import (  # noqa: F401
    BaseStrategy,
    Direction,
    ExitReason,
    Position,
    Signal,
    StrategyRegistry,
    TradeResult,
)

# Importing strategies.technical triggers auto-registration of all 9 strategies.
import strategies.technical  # noqa: F401

__all__ = [
    # Base types
    "BaseStrategy",
    "Direction",
    "ExitReason",
    "Position",
    "Signal",
    "StrategyRegistry",
    "TradeResult",
]
