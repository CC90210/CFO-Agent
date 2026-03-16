"""
strategies/base.py — Abstract base classes and shared data structures for all strategies.

Every strategy in Atlas extends BaseStrategy and registers itself with StrategyRegistry.
The dataclasses here (Signal, Position, TradeResult) are the canonical DTOs passed between
the strategy layer, the risk manager, and the execution engine.
"""

from __future__ import annotations

import inspect
import pkgutil
import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"  # no directional bias — used when a strategy passes


class ExitReason(str, Enum):
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    SIGNAL_REVERSAL = "SIGNAL_REVERSAL"
    TIME_STOP = "TIME_STOP"
    TRAILING_STOP = "TRAILING_STOP"
    MANUAL = "MANUAL"


# ---------------------------------------------------------------------------
# Data transfer objects
# ---------------------------------------------------------------------------


@dataclass
class Signal:
    """
    A trading signal produced by a strategy's analyze() method.

    conviction: float in [-1.0, 1.0].
        Positive = bullish, negative = bearish.
        Magnitude represents certainty; 0.0 = no edge, ±1.0 = maximum conviction.
        The risk manager uses this to size positions.

    stop_loss / take_profit: absolute price levels (not distances).
        Both are required. A signal without defined risk parameters is rejected
        by the risk manager.
    """

    symbol: str
    direction: Direction
    conviction: float  # [-1.0, 1.0]
    stop_loss: float
    take_profit: float
    strategy_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not -1.0 <= self.conviction <= 1.0:
            raise ValueError(
                f"conviction must be in [-1.0, 1.0], got {self.conviction}"
            )
        if self.stop_loss <= 0 or self.take_profit <= 0:
            raise ValueError("stop_loss and take_profit must be positive prices")

    @property
    def risk_reward(self) -> float | None:
        """Return the R:R ratio when direction and prices are consistent."""
        if self.direction == Direction.LONG:
            risk = self.metadata.get("entry_price", 0) - self.stop_loss
            reward = self.take_profit - self.metadata.get("entry_price", 0)
        elif self.direction == Direction.SHORT:
            risk = self.stop_loss - self.metadata.get("entry_price", 0)
            reward = self.metadata.get("entry_price", 0) - self.take_profit
        else:
            return None
        return reward / risk if risk > 0 else None


@dataclass
class Position:
    """
    An open position tracked by the portfolio manager.

    size: quantity in base asset units (positive for both LONG and SHORT —
          side encodes direction).
    strategy: name of the strategy that opened this position.
    """

    symbol: str
    side: Direction
    entry_price: float
    size: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    strategy: str
    trailing_stop: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def unrealised_pnl(self) -> float:
        """Unrealised PnL in quote currency at current mark price."""
        mark = self.metadata.get("mark_price")
        if mark is None:
            return 0.0
        if self.side == Direction.LONG:
            return (mark - self.entry_price) * self.size
        return (self.entry_price - mark) * self.size


@dataclass
class TradeResult:
    """
    The outcome of a closed trade, returned by the portfolio manager.
    """

    pnl: float
    pnl_pct: float
    duration_seconds: float
    entry_price: float
    exit_price: float
    exit_reason: ExitReason
    symbol: str
    strategy: str
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract base strategy
# ---------------------------------------------------------------------------


class BaseStrategy(ABC):
    """
    All Atlas trading strategies inherit from this class.

    Subclasses MUST implement:
        analyze(df)       → Signal  — full analysis, returns a Signal or None
        should_enter(df)  → bool    — fast check used by the scanner loop
        should_exit(df, position) → bool — called each bar while position is open

    Convention:
        - df is always a pandas DataFrame with columns:
          open, high, low, close, volume (lowercase), indexed by UTC datetime.
        - Strategies must not mutate the input DataFrame.
        - All heavy computation (indicator calculation) belongs in analyze().
        - should_enter / should_exit are lightweight wrappers around cached state.
    """

    #: Override in subclass to give the strategy a stable name used in Signal / logs.
    name: str = "unnamed_strategy"

    #: Human-readable description shown in the dashboard and strategy registry.
    description: str = ""

    #: Typical timeframes this strategy was designed for (informational).
    timeframes: list[str] = []

    #: Markets this strategy works best on (informational).
    markets: list[str] = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Auto-register concrete (non-abstract) strategies.
        if not inspect.isabstract(cls) and cls.name != "unnamed_strategy":
            StrategyRegistry.register(cls)

    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> Signal | None:
        """
        Run full analysis on OHLCV data and return a Signal, or None when
        there is no edge (direction == FLAT).

        Parameters
        ----------
        df : pd.DataFrame
            OHLCV DataFrame, UTC-indexed, minimum required length varies by strategy.

        Returns
        -------
        Signal | None
        """
        ...

    @abstractmethod
    def should_enter(self, df: pd.DataFrame) -> bool:
        """
        Lightweight entry check — called by the high-frequency scanner.
        Typically returns True when analyze() would produce a non-FLAT signal.
        """
        ...

    @abstractmethod
    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        """
        Decide whether to close an existing position on the current bar.

        Parameters
        ----------
        df       : OHLCV DataFrame (same format as analyze)
        position : the currently open position for this symbol

        Returns
        -------
        bool — True means "close the position now"
        """
        ...

    # ------------------------------------------------------------------
    # Shared helpers available to all strategies
    # ------------------------------------------------------------------

    @staticmethod
    def _clamp(value: float, lo: float = -1.0, hi: float = 1.0) -> float:
        """Clamp a float to [lo, hi]."""
        return max(lo, min(hi, value))

    @staticmethod
    def _require_columns(df: pd.DataFrame, *cols: str) -> None:
        """Raise ValueError if any required column is missing from df."""
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(
                f"DataFrame is missing required columns: {missing}. "
                f"Available: {list(df.columns)}"
            )

    @staticmethod
    def _min_rows(df: pd.DataFrame, n: int, label: str = "") -> bool:
        """Return False (rather than raising) when df is too short to compute indicators."""
        if len(df) < n:
            return False
        return True


# ---------------------------------------------------------------------------
# Strategy registry
# ---------------------------------------------------------------------------


class StrategyRegistry:
    """
    Global registry of all concrete BaseStrategy subclasses.

    Strategies are auto-registered at class-definition time via
    BaseStrategy.__init_subclass__. You can also call register() manually.

    Usage
    -----
    from strategies.base import StrategyRegistry

    all_names   = StrategyRegistry.list()
    cls         = StrategyRegistry.get("ema_crossover")
    instance    = StrategyRegistry.build("ema_crossover")
    all_strats  = StrategyRegistry.build_all()
    """

    _registry: dict[str, type[BaseStrategy]] = {}

    @classmethod
    def register(cls, strategy_cls: type[BaseStrategy]) -> None:
        key = strategy_cls.name
        if key in cls._registry and cls._registry[key] is not strategy_cls:
            raise KeyError(
                f"Duplicate strategy name '{key}': "
                f"{cls._registry[key]} vs {strategy_cls}"
            )
        cls._registry[key] = strategy_cls

    @classmethod
    def get(cls, name: str) -> type[BaseStrategy]:
        if name not in cls._registry:
            raise KeyError(
                f"Strategy '{name}' not found. "
                f"Available: {list(cls._registry.keys())}"
            )
        return cls._registry[name]

    @classmethod
    def build(cls, name: str, **kwargs: Any) -> BaseStrategy:
        """Instantiate a strategy by name, passing any kwargs to its __init__."""
        return cls.get(name)(**kwargs)

    @classmethod
    def build_all(cls, **kwargs: Any) -> list[BaseStrategy]:
        """Instantiate every registered strategy."""
        return [s(**kwargs) for s in cls._registry.values()]

    @classmethod
    def list(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def discover(cls, package: str = "strategies.technical") -> None:
        """
        Import all modules under `package` so that their classes self-register.
        Call this once at startup if you are not importing strategies explicitly.
        """
        mod = importlib.import_module(package)
        pkg_path = getattr(mod, "__path__", None)
        if pkg_path is None:
            return
        for _finder, module_name, _is_pkg in pkgutil.walk_packages(
            pkg_path, prefix=f"{package}."
        ):
            importlib.import_module(module_name)
