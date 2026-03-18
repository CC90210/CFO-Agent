"""
backtesting/walk_forward.py — Walk-Forward Validation for Atlas.

Walk-forward testing is the gold standard for validating a strategy because it
mimics what would actually happen in live trading: you optimise on past data,
then trade the future. You NEVER optimise on the period you test.

Two complementary APIs are provided:

1. WalkForwardValidator (fixed-bar windows)
   -----------------------------------------
   Splits data into rolling windows of fixed bar counts (train_bars + test_bars),
   sliding by step_bars each iteration. No parameter grid search — the strategy is
   used as-is. Ideal for quickly checking whether a strategy generalises across
   time periods without overfitting.

   Usage::

       from backtesting.walk_forward import WalkForwardValidator
       from strategies.technical.ema_crossover import EmaCrossoverStrategy

       validator = WalkForwardValidator(train_bars=500, test_bars=100, step_bars=50)
       result = validator.validate(df, EmaCrossoverStrategy())
       print(validator.summary(result))

2. WalkForwardOptimiser (train-ratio + parameter grid search)
   -----------------------------------------------------------
   Optimises strategy parameters on each training window and validates on the
   out-of-sample test window. Surfaces the best parameter combination across
   all windows and quantifies overfitting via the in-sample vs out-of-sample
   Sharpe ratio.

   Usage::

       from backtesting.walk_forward import WalkForwardOptimiser
       from strategies.technical.ema_crossover import EmaCrossoverStrategy

       optimiser = WalkForwardOptimiser(train_ratio=0.7, n_splits=5)
       result = optimiser.validate(
           strategy_cls=EmaCrossoverStrategy,
           data=df,
           param_grid={"fast_period": [5, 8, 10], "slow_period": [20, 26, 50]},
       )
       print(result.summary())

Overfitting interpretation
--------------------------
Score < 1.5  — no significant overfitting
Score 1.5–3.0 — moderate — reduce parameter count or add regularisation
Score > 3.0  — severe — do NOT deploy live
"""

from __future__ import annotations

import itertools
import logging
import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from backtesting.engine import BacktestEngine, BacktestResult
from strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# WalkForwardValidator dataclasses (fixed-bar-window API)
# ---------------------------------------------------------------------------


@dataclass
class WalkForwardWindow:
    """
    Performance metrics for a single fixed-bar walk-forward window.

    Both train (in-sample) and test (out-of-sample) metrics are recorded so
    callers can inspect how closely train performance predicts test performance.
    """

    window_id: int
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime
    train_return: float
    test_return: float
    train_win_rate: float
    test_win_rate: float
    train_pf: float       # profit factor
    test_pf: float
    train_trades: int
    test_trades: int


@dataclass
class WalkForwardResult:
    """
    Aggregated result from WalkForwardValidator across all fixed-bar windows.

    Key metrics
    -----------
    avg_oos_return         : mean out-of-sample return per window
    avg_oos_win_rate       : mean out-of-sample win rate
    avg_oos_pf             : mean out-of-sample profit factor
    train_test_correlation : Pearson correlation between per-window train and
                             test returns. Positive = in-sample predicts OOS.
    overfitting_score      : 0 = no overfitting, 1 = completely overfit.
                             Derived from (avg_train - avg_oos) / max(|avg_train|, 1e-9).
    worst_oos_window       : window with the lowest out-of-sample return
    recommendation         : "DEPLOY", "CAUTION", or "DO_NOT_DEPLOY"
    """

    strategy_name: str
    windows: list[WalkForwardWindow]
    avg_oos_return: float
    avg_oos_win_rate: float
    avg_oos_pf: float
    train_test_correlation: float
    overfitting_score: float
    worst_oos_window: WalkForwardWindow
    recommendation: str   # "DEPLOY" | "CAUTION" | "DO_NOT_DEPLOY"


# ---------------------------------------------------------------------------
# WalkForwardValidator (fixed-bar-window)
# ---------------------------------------------------------------------------


class WalkForwardValidator:
    """
    Walk-forward validation using fixed-bar rolling windows.

    Splits the dataset into overlapping train+test slices of fixed length,
    advancing by step_bars each iteration. No parameter grid search is
    performed; the strategy instance is used as-is in every window.

    Parameters
    ----------
    train_bars : int
        Number of bars in each training (in-sample) window.
    test_bars : int
        Number of bars in each test (out-of-sample) window.
    step_bars : int
        How many bars to advance the window each iteration.
        Defaults to test_bars (non-overlapping test windows).
    initial_capital : float
        Starting capital passed to BacktestEngine for each window run.
    commission_pct : float
        Commission rate (fraction) passed to BacktestEngine.
    """

    def __init__(
        self,
        train_bars: int = 500,
        test_bars: int = 100,
        step_bars: int = 50,
        initial_capital: float = 10_000.0,
        commission_pct: float = 0.001,
    ) -> None:
        if train_bars < 30:
            raise ValueError("train_bars must be at least 30")
        if test_bars < 10:
            raise ValueError("test_bars must be at least 10")
        if step_bars < 1:
            raise ValueError("step_bars must be at least 1")

        self.train_bars = train_bars
        self.test_bars = test_bars
        self.step_bars = step_bars
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
    ) -> WalkForwardResult:
        """
        Run walk-forward validation on ``df`` using ``strategy``.

        Parameters
        ----------
        df : pd.DataFrame
            Full OHLCV dataset with a DatetimeIndex (UTC).
            Must have at least train_bars + test_bars rows.
        strategy : BaseStrategy
            Concrete strategy instance used for every window.

        Returns
        -------
        WalkForwardResult
        """
        df = df.sort_index().copy()
        n = len(df)
        window_size = self.train_bars + self.test_bars

        if n < window_size:
            raise ValueError(
                f"DataFrame has only {n} rows but train_bars + test_bars = {window_size}. "
                "Provide more data or reduce window sizes."
            )

        engine = BacktestEngine(
            initial_capital=self.initial_capital,
            commission_pct=self.commission_pct,
            regime_filter=True,
        )

        windows: list[WalkForwardWindow] = []
        window_id = 0
        start = 0

        while start + window_size <= n:
            train_slice = df.iloc[start : start + self.train_bars]
            test_slice = df.iloc[start + self.train_bars : start + window_size]

            logger.info(
                "Walk-forward window %d: train %s→%s (%d bars), test %s→%s (%d bars)",
                window_id,
                train_slice.index[0].date(),
                train_slice.index[-1].date(),
                len(train_slice),
                test_slice.index[0].date(),
                test_slice.index[-1].date(),
                len(test_slice),
            )

            train_result = engine.run(train_slice, strategy)
            test_result = engine.run(test_slice, strategy)

            windows.append(
                WalkForwardWindow(
                    window_id=window_id,
                    train_start=_to_dt(train_slice.index[0]),
                    train_end=_to_dt(train_slice.index[-1]),
                    test_start=_to_dt(test_slice.index[0]),
                    test_end=_to_dt(test_slice.index[-1]),
                    train_return=train_result.total_return,
                    test_return=test_result.total_return,
                    train_win_rate=train_result.win_rate,
                    test_win_rate=test_result.win_rate,
                    train_pf=train_result.profit_factor,
                    test_pf=test_result.profit_factor,
                    train_trades=train_result.total_trades,
                    test_trades=test_result.total_trades,
                )
            )

            window_id += 1
            start += self.step_bars

        if not windows:
            raise RuntimeError(
                "No walk-forward windows could be constructed. "
                "Increase dataset size or reduce train_bars/test_bars."
            )

        return self._aggregate(strategy.name, windows)

    def summary(self, result: WalkForwardResult) -> str:
        """Return a formatted multi-line walk-forward validation report."""
        worst = result.worst_oos_window
        corr_label = (
            "positive (IS predicts OOS)"
            if result.train_test_correlation >= 0
            else "negative (IS does NOT predict OOS)"
        )

        lines = [
            "=" * 66,
            f"  Atlas Walk-Forward Validation — {result.strategy_name}",
            f"  Windows: {len(result.windows)}",
            "=" * 66,
            "",
            "  Out-of-sample aggregate",
            f"    Avg OOS return       : {result.avg_oos_return * 100:>+.2f}% per window",
            f"    Avg OOS win rate     : {result.avg_oos_win_rate * 100:.1f}%",
            f"    Avg OOS profit factor: {result.avg_oos_pf:.3f}",
            "",
            "  Robustness",
            f"    Train/test corr      : {result.train_test_correlation:>+.3f}  ({corr_label})",
            f"    Overfitting score    : {result.overfitting_score:.3f}  (0=none, 1=complete)",
            f"    Recommendation       : {result.recommendation}",
            "",
            "  Worst OOS window",
            f"    Window ID            : {worst.window_id}",
            f"    Test period          : {worst.test_start:%Y-%m-%d} → {worst.test_end:%Y-%m-%d}",
            f"    OOS return           : {worst.test_return * 100:>+.2f}%",
            f"    OOS trades           : {worst.test_trades}",
            "",
            "  Per-window breakdown",
            f"  {'ID':>3}  {'Train return':>13}  {'Test return':>11}  "
            f"{'Test WR':>8}  {'Test PF':>8}  {'Test trades':>11}",
            "  " + "-" * 62,
        ]
        for w in result.windows:
            lines.append(
                f"  {w.window_id:>3}  "
                f"{w.train_return * 100:>+12.2f}%  "
                f"{w.test_return * 100:>+10.2f}%  "
                f"{w.test_win_rate * 100:>7.1f}%  "
                f"{w.test_pf:>8.3f}  "
                f"{w.test_trades:>11}"
            )
        lines.append("=" * 66)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _aggregate(
        self, strategy_name: str, windows: list[WalkForwardWindow]
    ) -> WalkForwardResult:
        """Compute aggregate OOS metrics and build WalkForwardResult."""
        oos_returns = [w.test_return for w in windows]
        oos_win_rates = [w.test_win_rate for w in windows]
        oos_pfs = [w.test_pf for w in windows]
        train_returns = [w.train_return for w in windows]

        avg_oos_return = float(np.mean(oos_returns))
        avg_oos_win_rate = float(np.mean(oos_win_rates))
        avg_oos_pf = float(np.mean(oos_pfs))

        # Pearson correlation between per-window train return and test return
        train_test_correlation = _safe_correlation(train_returns, oos_returns)

        # Overfitting score: how much train return exceeds test return, normalised
        avg_train = float(np.mean(train_returns))
        denom = max(abs(avg_train), 1e-9)
        raw_score = (avg_train - avg_oos_return) / denom
        # Clamp to [0, 1]: 0 = no overfitting, 1 = complete overfitting
        overfitting_score = float(np.clip(raw_score, 0.0, 1.0))

        # Worst OOS window by test_return
        worst = min(windows, key=lambda w: w.test_return)

        # Recommendation thresholds
        if overfitting_score < 0.3 and avg_oos_return > 0.0:
            recommendation = "DEPLOY"
        elif overfitting_score < 0.6:
            recommendation = "CAUTION"
        else:
            recommendation = "DO_NOT_DEPLOY"

        return WalkForwardResult(
            strategy_name=strategy_name,
            windows=windows,
            avg_oos_return=avg_oos_return,
            avg_oos_win_rate=avg_oos_win_rate,
            avg_oos_pf=avg_oos_pf,
            train_test_correlation=train_test_correlation,
            overfitting_score=overfitting_score,
            worst_oos_window=worst,
            recommendation=recommendation,
        )


# ---------------------------------------------------------------------------
# WalkForwardOptimiser dataclasses (train-ratio + parameter grid search API)
# ---------------------------------------------------------------------------


@dataclass
class WindowResult:
    """
    Performance metrics for a single walk-forward window (optimisation API).

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
class OptimisationResult:
    """
    Aggregated walk-forward optimisation result across all windows.

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
        """Return a formatted multi-line walk-forward optimisation report."""
        lines = [
            "=" * 60,
            "  Atlas Walk-Forward Optimisation Report",
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
# WalkForwardOptimiser
# ---------------------------------------------------------------------------


class WalkForwardOptimiser:
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
    ) -> OptimisationResult:
        """
        Run walk-forward optimisation.

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
        OptimisationResult
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
        param_strs = [str(sorted(w.best_params.items())) for w in window_results]
        if param_strs:
            most_common_str = Counter(param_strs).most_common(1)[0][0]
            most_common_params = dict(eval(most_common_str))  # safe: we built the string ourselves  # noqa: S307
        else:
            most_common_params = {}

        return OptimisationResult(
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
        test_size = int(n * (1.0 - self.train_ratio) / 1.0)
        train_size = int(n * self.train_ratio)
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


# ---------------------------------------------------------------------------
# Backward-compatibility alias
# The original class was named WalkForwardValidator but implemented optimisation
# with a param_grid. Code that imported WalkForwardValidator for optimisation
# should migrate to WalkForwardOptimiser; this alias preserves imports in the
# interim.
# ---------------------------------------------------------------------------

# (WalkForwardValidator is now the fixed-bar-window class above.
#  The old optimiser API is available as WalkForwardOptimiser.)


# ---------------------------------------------------------------------------
# Private utilities
# ---------------------------------------------------------------------------


def _to_dt(ts: Any) -> datetime:
    """Convert a pandas Timestamp (or datetime) to a plain datetime."""
    if hasattr(ts, "to_pydatetime"):
        return ts.to_pydatetime()
    return ts  # type: ignore[return-value]


def _safe_correlation(x: list[float], y: list[float]) -> float:
    """
    Pearson correlation between two lists.

    Returns 0.0 when there are fewer than 2 data points or when either
    series has zero variance (prevents division by zero).
    """
    if len(x) < 2 or len(y) < 2:
        return 0.0
    xa = np.array(x, dtype=float)
    ya = np.array(y, dtype=float)
    if xa.std() == 0.0 or ya.std() == 0.0:
        return 0.0
    return float(np.corrcoef(xa, ya)[0, 1])
