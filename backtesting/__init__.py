"""
backtesting — Atlas backtesting, walk-forward validation, Monte Carlo, and benchmarking.

Public API
----------
from backtesting import BacktestEngine, BacktestResult
from backtesting import WalkForwardValidator, WalkForwardResult
from backtesting import MonteCarloSimulator, MonteCarloResult
from backtesting import BenchmarkComparator, ComparisonResult
"""

from backtesting.engine import BacktestEngine, BacktestResult, TradeLog
from backtesting.walk_forward import WalkForwardValidator, WalkForwardResult, WindowResult
from backtesting.monte_carlo import MonteCarloSimulator, MonteCarloResult
from backtesting.benchmark import BenchmarkComparator, ComparisonResult

__all__ = [
    # Engine
    "BacktestEngine",
    "BacktestResult",
    "TradeLog",
    # Walk-forward
    "WalkForwardValidator",
    "WalkForwardResult",
    "WindowResult",
    # Monte Carlo
    "MonteCarloSimulator",
    "MonteCarloResult",
    # Benchmark
    "BenchmarkComparator",
    "ComparisonResult",
]
