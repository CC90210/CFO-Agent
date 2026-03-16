"""
backtesting/walk_forward.py — Walk-Forward Validation for Atlas.

Walk-forward testing is the gold standard for validating a strategy because it
mimics what would actually happen in live trading: you optimise on past data,
then trade the future. You NEVER optimise on the period you test.

How it works
------------
Given N months of data with train_ratio=0.7 and n_splits=5:

  Window 1: train=[0, 70%], test=[70%, 86%]   ← ~16% per window (30%/~5 windows)
  Window 2: train=[16%, 86%], test=[86%, 100%]
  ...each window slides forward by step_size

The aggregate of ALL out-of-sample (test) windows is the "true" expected
performance. If in-sample Sharpe >> out-of-sample Sharpe, the strategy is
overfit.

Overfitting score: ratio of in-sample to out-of-sample Sharpe.
  < 1.5  — no significant overfitting
  1.5-3.0 — moderate overfitting — reduce parameter count
  > 3.0  — severe overfitting — do not trade live

Usage
-----
    from backtesting.walk_forward import WalkForwardValidator
    from strategies.technical.ema_crossover import EmaCrossoverStrategy

    validator = WalkForwardValidator(train_ratio=0.7, n_splits=5)
    result = validator.validate(
        strategy_cls=EmaCrossoverStrategy,
        data=df,
        param_grid={"fast_period": [5, 8, 10], "slow_period": [20, 26, 50]},
    )
    print(result.summary())
"""

from __future__ import annotations

import itertools
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from backtesting.engine import BacktestEngine, BacktestResult
from strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class WindowResult:
    """
    Performance metrics for a single walk-forward window.

    in_sample_* metrics are computed on the training slice.
    out_sample_* metrics are computed on the held-out test slice.
    best_params is the parameter dict that maximised in-sample Sharpe.
    """

    window_index: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime

    best_params: dict[str, Any]

    in_sample_sharpe: float
    in_sample_return: float
    in_sample_max_dd: float
    in_sample_trades: int

    out_sample_sharpe: float
    out_sample_return: float
    out_sample_max_dd: float
    out_sample_trades: int


@dataclass
class WalkForwardResult:
    """
    Aggregated walk-forward validation result across all windows.

    The key metric is aggregate_sharpe — the Sharpe ratio computed from
    stitching together all out-of-sample equity curves. This is what you
    would have actually experienced if you had run this strategy with
    walk-forward re-optimisation.
    """

    windows: list[WindowResult]
    aggregate_sharpe: float          # Sharpe of concatenated OOS equity
    aggregate_return: float          # Total return across OOS periods
    aggregate_max_dd: float          # Worst drawdown across OOS periods
    aggregate_win_rate: float
    total_oos_trades: int

    # Overfitting analysis
    avg_in_sample_sharpe: float
    avg_out_sample_sharpe: float
    overfitting_score: float         # avg_in / avg_out; >3.0 = danger

    # Best params used most often across windows
    most_common_params: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a formatted multi-line walk-forward report."""
        lines = [
            "=" * 60,
            "  Atlas Walk-Forward Validation Report",
            f"  Windows: {len(self.windows)} | OOS trades: {self.total_oos_trades}",
            "=" * 60,
            "",
            "  Out-of-sample aggregate performance",
            f"    Sharpe (OOS)      : {self.aggregate_sharpe:.3f}",
            f"    Total return (OOS): {self.aggregate_return * 100:+.2f}%",
            f"    Max drawdown (OOS): {self.aggregate_max_dd * 100:.2f}%",
            f"    Win rate (OOS)    : {self.aggregate_win_rate * 100:.1f}%",
            "",
            "  Overfitting analysis",
            f"    Avg in-sample Sharpe : {self.avg_in_sample_sharpe:.3f}",
            f"    Avg out-sample Sharpe: {self.avg_out_sample_sharpe:.3f}",
            f"    Overfitting score    : {self.overfitting_score:.2f}x",
            (
                "    Verdict: OK — no significant overfitting"
                if self.overfitting_score < 1.5
                else (
                    "    Verdict: MODERATE — consider reducing parameters"
                    if self.overfitting_score < 3.0
                    else "    Verdict: SEVERE — do NOT trade live"
                )
            ),
            "",
            "  Per-window breakdown",
        ]
        for w in self.windows:
            lines.append(
                f"    Window {w.window_index + 1}: "
                f"OOS {w.test_start:%Y-%m-%d}→{w.test_end:%Y-%m-%d} | "
                f"Sharpe {w.out_sample_sharpe:.2f} | "
                f"Return {w.out_sample_return * 100:+.1f}% | "
                f"Trades {w.out_sample_trades} | "
                f"Params {w.best_params}"
            )
        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# WalkForwardValidator
# ---------------------------------------------------------------------------


class WalkForwardValidator:
    """
    Perform walk-forward optimisation and out-of-sample validation.

    Parameters
    ----------
    train_ratio : float
        Proportion of each window used for training (default 0.70 = 70 %).
    n_splits : int
        Number of walk-forward windows (default 5).
    initial_capital : float
        Starting capital for each backtest window.
    commission_pct : float
        Commission rate passed to BacktestEngine.
    optimise_metric : str
        Which BacktestResult attribute to maximise during parameter search.
        Default is "sharpe_ratio". Can be "total_return", "calmar_ratio",
        "profit_factor", etc.
    """

    def __init__(
        self,
        train_ratio: float = 0.70,
        n_splits: int = 5,
        initial_capital: float = 10_000.0,
        commission_pct: float = 0.001,
        optimise_metric: str = "sharpe_ratio",
    ) -> None:
        if not 0.3 <= train_ratio <= 0.9:
            raise ValueError("train_ratio must be between 0.3 and 0.9")
        if n_splits < 2:
            raise ValueError("n_splits must be at least 2")

        self.train_ratio = train_ratio
        self.n_splits = n_splits
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.optimise_metric = optimise_metric

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(
        self,
        strategy_cls: type[BaseStrategy],
        data: pd.DataFrame,
        param_grid: dict[str, list[Any]] | None = None,
        **default_kwargs: Any,
    ) -> WalkForwardResult:
        """
        Run walk-forward validation.

        Parameters
        ----------
        strategy_cls : type[BaseStrategy]
            The strategy class (not instance) to optimise and test.
        data : pd.DataFrame
            Full OHLCV dataset. Will be split into rolling train/test windows.
        param_grid : dict | None
            Parameter combinations to try during in-sample optimisation.
            Keys are __init__ kwarg names; values are lists of candidate values.
            If None, strategy is run with default_kwargs only.
        **default_kwargs
            Fixed constructor kwargs passed to strategy_cls in all windows.

        Returns
        -------
        WalkForwardResult
        """
        data = data.sort_index()
        windows = self._build_windows(data)

        engine = BacktestEngine(
            initial_capital=self.initial_capital,
            commission_pct=self.commission_pct,
        )

        window_results: list[WindowResult] = []
        oos_equity_pieces: list[pd.Series] = []
        oos_trades_all: list[Any] = []

        for i, (train_slice, test_slice) in enumerate(windows):
            logger.info(
                "Walk-forward window %d/%d: train %s→%s, test %s→%s",
                i + 1,
                len(windows),
                train_slice.index[0].date(),
                train_slice.index[-1].date(),
                test_slice.index[0].date(),
                test_slice.index[-1].date(),
            )

            # ── In-sample optimisation ──
            best_params, in_sample_result = self.optimize_parameters(
                strategy_cls,
                train_slice,
                param_grid or {},
                engine,
                **default_kwargs,
            )

            # ── Out-of-sample test ──
            strategy = strategy_cls(**{**default_kwargs, **best_params})
            oos_result = engine.run(test_slice, strategy)

            # Collect OOS equity curve for aggregate calculation
            oos_equity_pieces.append(oos_result.equity_curve)
            oos_trades_all.extend(oos_result.trades)

            window_results.append(
                WindowResult(
                    window_index=i,
                    train_start=train_slice.index[0].to_pydatetime(),
                    train_end=train_slice.index[-1].to_pydatetime(),
                    test_start=test_slice.index[0].to_pydatetime(),
                    test_end=test_slice.index[-1].to_pydatetime(),
                    best_params=best_params,
                    in_sample_sharpe=in_sample_result.sharpe_ratio,
                    in_sample_return=in_sample_result.total_return,
                    in_sample_max_dd=in_sample_result.max_drawdown,
                    in_sample_trades=in_sample_result.total_trades,
                    out_sample_sharpe=oos_result.sharpe_ratio,
                    out_sample_return=oos_result.total_return,
                    out_sample_max_dd=oos_result.max_drawdown,
                    out_sample_trades=oos_result.total_trades,
                )
            )

        # ── Aggregate OOS metrics ──
        aggregate_result = self._aggregate_oos(
            oos_equity_pieces, oos_trades_all, self.initial_capital
        )

        avg_in = (
            np.mean([w.in_sample_sharpe for w in window_results])
            if window_results
            else 0.0
        )
        avg_out = (
            np.mean([w.out_sample_sharpe for w in window_results])
            if window_results
            else 0.0
        )
        overfitting_score = abs(avg_in) / abs(avg_out) if abs(avg_out) > 0.01 else float("inf")

        # Most common best params
        from collections import Counter
        param_strs = [str(sorted(w.best_params.items())) for w in window_results]
        if param_strs:
            most_common_str = Counter(param_strs).most_common(1)[0][0]
            most_common_params = dict(eval(most_common_str))  # safe: we built the string ourselves
        else:
            most_common_params = {}

        return WalkForwardResult(
            windows=window_results,
            aggregate_sharpe=aggregate_result["sharpe"],
            aggregate_return=aggregate_result["total_return"],
            aggregate_max_dd=aggregate_result["max_dd"],
            aggregate_win_rate=aggregate_result["win_rate"],
            total_oos_trades=len(oos_trades_all),
            avg_in_sample_sharpe=float(avg_in),
            avg_out_sample_sharpe=float(avg_out),
            overfitting_score=overfitting_score,
            most_common_params=most_common_params,
        )

    def optimize_parameters(
        self,
        strategy_cls: type[BaseStrategy],
        train_data: pd.DataFrame,
        param_grid: dict[str, list[Any]],
        engine: BacktestEngine | None = None,
        **fixed_kwargs: Any,
    ) -> tuple[dict[str, Any], BacktestResult]:
        """
        Grid search over param_grid on train_data.

        Returns (best_params, best_backtest_result).
        If param_grid is empty, runs once with fixed_kwargs.
        """
        if engine is None:
            engine = BacktestEngine(
                initial_capital=self.initial_capital,
                commission_pct=self.commission_pct,
            )

        if not param_grid:
            strategy = strategy_cls(**fixed_kwargs)
            result = engine.run(train_data, strategy)
            return fixed_kwargs, result

        best_score = float("-inf")
        best_params: dict[str, Any] = {}
        best_result: BacktestResult | None = None

        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combinations = list(itertools.product(*values))

        for combo in combinations:
            params = dict(zip(keys, combo))
            try:
                strategy = strategy_cls(**{**fixed_kwargs, **params})
                result = engine.run(train_data, strategy)
                score = getattr(result, self.optimise_metric, result.sharpe_ratio)
                if isinstance(score, float) and not (
                    score != score or score == float("inf") or score == float("-inf")
                ):
                    if score > best_score:
                        best_score = score
                        best_params = params
                        best_result = result
            except Exception as exc:
                logger.debug("Parameter combo %s failed: %s", params, exc)

        if best_result is None:
            # All combos failed — fall back to first combo with default kwargs
            first_params = dict(zip(keys, combinations[0]))
            strategy = strategy_cls(**{**fixed_kwargs, **first_params})
            best_result = engine.run(train_data, strategy)
            best_params = first_params

        return best_params, best_result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_windows(
        self, data: pd.DataFrame
    ) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Construct rolling train/test window pairs.

        The window size is fixed; each window slides forward by test_size
        rows so that every bar appears in exactly one test window.
        """
        n = len(data)
        # Total window length = n / n_splits * (1 + 1/(train_ratio/(1-train_ratio)))
        # Simpler: compute based on n_splits sliding windows
        test_size = int(n * (1.0 - self.train_ratio) / 1.0)
        train_size = int(n * self.train_ratio)
        # Slide: each window starts test_size later
        step = max(1, test_size)

        windows: list[tuple[pd.DataFrame, pd.DataFrame]] = []
        start = 0
        for _ in range(self.n_splits):
            train_end = start + train_size
            test_end = train_end + test_size

            if test_end > n:
                break

            train_slice = data.iloc[start:train_end]
            test_slice = data.iloc[train_end:test_end]

            if len(train_slice) >= 30 and len(test_slice) >= 10:
                windows.append((train_slice, test_slice))

            start += step

        if not windows:
            # Fallback: single 70/30 split
            mid = int(n * self.train_ratio)
            windows = [(data.iloc[:mid], data.iloc[mid:])]

        return windows

    @staticmethod
    def _aggregate_oos(
        equity_pieces: list[pd.Series],
        trades: list[Any],
        initial_capital: float,
    ) -> dict[str, float]:
        """Stitch OOS equity curves and compute aggregate metrics."""
        import math

        if not equity_pieces:
            return {"sharpe": 0.0, "total_return": 0.0, "max_dd": 0.0, "win_rate": 0.0}

        # Normalise each piece to start at 1.0, then chain them
        chained_returns: list[float] = []
        for eq in equity_pieces:
            if len(eq) < 2:
                continue
            piece_returns = eq.pct_change().dropna().tolist()
            chained_returns.extend(piece_returns)

        if not chained_returns:
            return {"sharpe": 0.0, "total_return": 0.0, "max_dd": 0.0, "win_rate": 0.0}

        returns_arr = np.array(chained_returns)
        equity_arr = np.cumprod(1.0 + returns_arr) * initial_capital

        total_return = (equity_arr[-1] - initial_capital) / initial_capital

        # Sharpe (annualised, daily)
        mean_r = np.mean(returns_arr)
        std_r = np.std(returns_arr)
        sharpe = (mean_r / std_r) * math.sqrt(252) if std_r > 0 else 0.0

        # Max drawdown
        roll_max = np.maximum.accumulate(equity_arr)
        dd = (equity_arr - roll_max) / roll_max
        max_dd = float(np.min(dd))

        # Win rate from trades
        if trades:
            winners = sum(1 for t in trades if t.net_pnl > 0)
            win_rate = winners / len(trades)
        else:
            win_rate = 0.0

        return {
            "sharpe": float(sharpe),
            "total_return": float(total_return),
            "max_dd": max_dd,
            "win_rate": win_rate,
        }
