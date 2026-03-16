"""
backtesting/benchmark.py — Strategy benchmarking for Atlas.

A strategy is only worth trading live if it beats a passive benchmark on a
RISK-ADJUSTED basis. Beating Buy & Hold on raw returns is not enough — you must
also have a better Sharpe ratio, because if a passive index gives you the same
return with lower drawdown, there's no reason to run an active strategy.

Key metrics
-----------
- Alpha      : annualised excess return over the benchmark (Jensen's Alpha)
- Beta       : sensitivity of strategy returns to benchmark moves
- IR         : Information Ratio — alpha / tracking error
- Tracking   : standard deviation of (strategy_returns - benchmark_returns)

Usage
-----
    from backtesting.benchmark import BenchmarkComparator
    from backtesting.engine import BacktestEngine

    engine = BacktestEngine(initial_capital=10_000)
    result = engine.run(df, strategy)

    bench = BenchmarkComparator(risk_free_rate=0.05)
    bh_data = df["close"]   # buy-and-hold benchmark (the asset itself)
    comparison = bench.compare(result, bh_data, benchmark_name="Buy & Hold")
    print(comparison.summary())
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from backtesting.engine import BacktestResult

logger = logging.getLogger(__name__)

_ANNUALISATION = 252  # trading days / year


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class ComparisonResult:
    """
    Head-to-head comparison between a strategy and a benchmark.
    """

    strategy_name: str
    benchmark_name: str

    # Returns
    strategy_total_return: float
    benchmark_total_return: float
    strategy_annualised_return: float
    benchmark_annualised_return: float

    # Risk
    strategy_sharpe: float
    benchmark_sharpe: float
    strategy_max_dd: float
    benchmark_max_dd: float
    strategy_calmar: float
    benchmark_calmar: float

    # Relative metrics
    alpha: float              # annualised alpha (Jensen's)
    beta: float               # correlation-weighted sensitivity
    information_ratio: float  # alpha / tracking_error
    tracking_error: float     # annualised std of active returns
    correlation: float        # Pearson r between daily returns

    # Verdict
    beats_benchmark: bool     # True if risk-adjusted alpha > 0 AND sharpe better

    def summary(self) -> str:
        lines = [
            "=" * 60,
            f"  Strategy Benchmark Report",
            f"  Strategy  : {self.strategy_name}",
            f"  Benchmark : {self.benchmark_name}",
            "=" * 60,
            "",
            f"  {'Metric':<28}{'Strategy':>10}{'Benchmark':>12}",
            "  " + "-" * 50,
            f"  {'Total return':<28}{self.strategy_total_return * 100:>+9.2f}%"
            f"{self.benchmark_total_return * 100:>+11.2f}%",
            f"  {'Annualised return':<28}{self.strategy_annualised_return * 100:>+9.2f}%"
            f"{self.benchmark_annualised_return * 100:>+11.2f}%",
            f"  {'Sharpe ratio':<28}{self.strategy_sharpe:>10.3f}"
            f"{self.benchmark_sharpe:>12.3f}",
            f"  {'Max drawdown':<28}{self.strategy_max_dd * 100:>+9.2f}%"
            f"{self.benchmark_max_dd * 100:>+11.2f}%",
            f"  {'Calmar ratio':<28}{self.strategy_calmar:>10.3f}"
            f"{self.benchmark_calmar:>12.3f}",
            "",
            "  Relative metrics",
            f"    Alpha (annualised) : {self.alpha * 100:+.2f}%",
            f"    Beta               : {self.beta:.3f}",
            f"    Information Ratio  : {self.information_ratio:.3f}",
            f"    Tracking error     : {self.tracking_error * 100:.2f}% (annualised)",
            f"    Correlation        : {self.correlation:.3f}",
            "",
            (
                "  VERDICT: Strategy BEATS benchmark (risk-adjusted)"
                if self.beats_benchmark
                else "  VERDICT: Strategy does NOT beat benchmark — consider passive approach"
            ),
            "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# BenchmarkComparator
# ---------------------------------------------------------------------------


class BenchmarkComparator:
    """
    Compare a strategy BacktestResult against one or more benchmarks.

    Parameters
    ----------
    risk_free_rate : float
        Annual risk-free rate as a fraction (e.g. 0.05 = 5 %).
        Used when computing Sharpe ratio for the benchmark.
    """

    def __init__(self, risk_free_rate: float = 0.045) -> None:
        self.risk_free_rate = risk_free_rate
        self._daily_rf = (1.0 + risk_free_rate) ** (1.0 / _ANNUALISATION) - 1.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compare(
        self,
        strategy_result: BacktestResult,
        benchmark_prices: pd.Series,
        benchmark_name: str = "Buy & Hold",
    ) -> ComparisonResult:
        """
        Compare strategy against a price series benchmark.

        Parameters
        ----------
        strategy_result : BacktestResult
            Output from BacktestEngine.run().
        benchmark_prices : pd.Series
            Price series (close prices) for the benchmark, DatetimeIndex.
            Will be aligned to the strategy's date range automatically.
        benchmark_name : str
            Human-readable benchmark label.

        Returns
        -------
        ComparisonResult
        """
        # Align benchmark to strategy period
        start = strategy_result.start_date
        end = strategy_result.end_date
        if start and end:
            mask = (benchmark_prices.index >= start) & (benchmark_prices.index <= end)
            bench_prices = benchmark_prices[mask].copy()
        else:
            bench_prices = benchmark_prices.copy()

        if len(bench_prices) < 2:
            raise ValueError(
                "benchmark_prices has fewer than 2 data points in the strategy period. "
                "Ensure the benchmark covers the same date range as the backtest."
            )

        # Benchmark returns (daily)
        bench_daily = bench_prices.resample("D").last().ffill().pct_change().dropna()

        # Strategy equity → daily returns
        strat_eq = strategy_result.equity_curve.resample("D").last().ffill()
        strat_daily = strat_eq.pct_change().dropna()

        # Align on common dates
        common_idx = strat_daily.index.intersection(bench_daily.index)
        if len(common_idx) < 2:
            # Fall back to reindex without date alignment requirement
            common_idx = strat_daily.index
            bench_daily = bench_daily.reindex(common_idx).ffill().bfill().fillna(0.0)

        strat_r = strat_daily.reindex(common_idx).fillna(0.0).values
        bench_r = bench_daily.reindex(common_idx).fillna(0.0).values

        # ── Benchmark performance ──
        bh_total_return = float(
            (bench_prices.iloc[-1] - bench_prices.iloc[0]) / bench_prices.iloc[0]
        )
        n_days = max(1, (bench_prices.index[-1] - bench_prices.index[0]).days)
        n_years = n_days / 365.0
        bh_ann_return = (1.0 + bh_total_return) ** (1.0 / n_years) - 1.0 if n_years > 0 else 0.0

        bh_sharpe = self._compute_sharpe(bench_r)
        bh_eq = np.cumprod(1.0 + bench_r)
        bh_max_dd = self._compute_max_dd(bh_eq)
        bh_calmar = bh_ann_return / abs(bh_max_dd) if bh_max_dd != 0 else float("inf")

        # ── Relative metrics ──
        alpha = self.calculate_alpha(strat_r, bench_r)
        beta = self.calculate_beta(strat_r, bench_r)
        ir = self.calculate_information_ratio(strat_r, bench_r)
        active_returns = strat_r - bench_r
        tracking_error = float(np.std(active_returns) * math.sqrt(_ANNUALISATION))
        correlation = float(np.corrcoef(strat_r, bench_r)[0, 1]) if len(strat_r) > 1 else 0.0

        beats = (
            alpha > 0
            and strategy_result.sharpe_ratio > bh_sharpe
        )

        return ComparisonResult(
            strategy_name=strategy_result.strategy_name,
            benchmark_name=benchmark_name,
            strategy_total_return=strategy_result.total_return,
            benchmark_total_return=bh_total_return,
            strategy_annualised_return=strategy_result.annualized_return,
            benchmark_annualised_return=bh_ann_return,
            strategy_sharpe=strategy_result.sharpe_ratio,
            benchmark_sharpe=bh_sharpe,
            strategy_max_dd=strategy_result.max_drawdown,
            benchmark_max_dd=bh_max_dd,
            strategy_calmar=strategy_result.calmar_ratio,
            benchmark_calmar=bh_calmar,
            alpha=alpha,
            beta=beta,
            information_ratio=ir,
            tracking_error=tracking_error,
            correlation=correlation,
            beats_benchmark=beats,
        )

    def calculate_alpha(
        self,
        strategy_returns: np.ndarray,
        benchmark_returns: np.ndarray,
    ) -> float:
        """
        Compute Jensen's Alpha (annualised).

        Alpha = E[R_strat] - (R_f + beta * (E[R_bench] - R_f))
        Annualised by multiplying the daily alpha by _ANNUALISATION.

        Parameters
        ----------
        strategy_returns  : daily return array
        benchmark_returns : daily return array (same length)

        Returns
        -------
        float — annualised alpha
        """
        beta = self.calculate_beta(strategy_returns, benchmark_returns)
        daily_alpha = (
            np.mean(strategy_returns)
            - (self._daily_rf + beta * (np.mean(benchmark_returns) - self._daily_rf))
        )
        return float(daily_alpha * _ANNUALISATION)

    def calculate_beta(
        self,
        strategy_returns: np.ndarray,
        benchmark_returns: np.ndarray,
    ) -> float:
        """
        Compute beta: covariance(strat, bench) / variance(bench).

        Parameters
        ----------
        strategy_returns  : daily return array
        benchmark_returns : daily return array

        Returns
        -------
        float — beta coefficient
        """
        bench_var = float(np.var(benchmark_returns))
        if bench_var < 1e-12:
            return 1.0
        cov = float(np.cov(strategy_returns, benchmark_returns)[0, 1])
        return cov / bench_var

    def calculate_information_ratio(
        self,
        strategy_returns: np.ndarray,
        benchmark_returns: np.ndarray,
    ) -> float:
        """
        Information Ratio = annualised active return / annualised tracking error.

        Parameters
        ----------
        strategy_returns  : daily return array
        benchmark_returns : daily return array

        Returns
        -------
        float — information ratio
        """
        active = strategy_returns - benchmark_returns
        te = float(np.std(active))
        if te < 1e-12:
            return 0.0
        ann_active = float(np.mean(active) * _ANNUALISATION)
        ann_te = te * math.sqrt(_ANNUALISATION)
        return ann_active / ann_te

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_sharpe(self, returns: np.ndarray) -> float:
        """Annualised Sharpe using the instance's risk-free rate."""
        excess = returns - self._daily_rf
        std = float(np.std(excess))
        if std < 1e-12:
            return 0.0
        return float(np.mean(excess) / std * math.sqrt(_ANNUALISATION))

    @staticmethod
    def _compute_max_dd(equity_normalised: np.ndarray) -> float:
        """Max drawdown from a normalised equity array (starts at 1.0)."""
        roll_max = np.maximum.accumulate(equity_normalised)
        dd = (equity_normalised - roll_max) / np.maximum(roll_max, 1e-10)
        return float(np.min(dd))
