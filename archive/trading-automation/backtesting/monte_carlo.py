"""
backtesting/monte_carlo.py — Monte Carlo simulation for Atlas backtest validation.

Purpose
-------
A backtest on a single path of history tells you "what happened once". Monte
Carlo simulation answers: "Given the distribution of trade outcomes we observed,
what range of results would we expect if we ran the strategy many times?"

Method: Trade-sequence shuffling (also called "permutation MC").
1. Take the observed list of trade P&Ls (net of commissions).
2. Shuffle the order randomly 1,000+ times.
3. Compute the equity curve and metrics for each shuffled sequence.
4. Produce a distribution of outcomes.

This is better than resampling returns because it preserves the actual
magnitudes of wins and losses; it only randomises their order.

Probability of ruin: fraction of simulations where max drawdown exceeded
a user-specified threshold.

Usage
-----
    from backtesting.engine import BacktestEngine
    from backtesting.monte_carlo import MonteCarloSimulator

    engine = BacktestEngine(initial_capital=10_000)
    result = engine.run(df, strategy)

    mc = MonteCarloSimulator(n_simulations=2000, random_seed=42)
    mc_result = mc.simulate(result.trades, initial_capital=10_000)
    print(mc_result.summary())
    print(f"P(ruin >20% DD) = {mc.probability_of_ruin(mc_result, 0.20):.1%}")
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from backtesting.engine import TradeLog

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class MonteCarloResult:
    """
    Distribution of outcomes from n Monte Carlo simulations.

    All return/drawdown values are fractions (0.15 = 15 %).
    Percentile arrays are indexed 0–100.
    """

    n_simulations: int
    initial_capital: float

    # Final equity distribution
    final_equity_median: float
    final_equity_p5: float      # 5th percentile (near worst case)
    final_equity_p25: float
    final_equity_p75: float
    final_equity_p95: float     # 95th percentile (near best case)

    # Return distribution
    return_median: float
    return_p5: float
    return_p95: float

    # Drawdown distribution
    max_dd_median: float
    max_dd_p5: float            # worst 5% of simulations
    max_dd_p95: float           # best 5% (shallowest drawdown)

    # Sharpe distribution
    sharpe_median: float
    sharpe_p5: float
    sharpe_p95: float

    # Ruin analysis
    p_ruin_10pct: float         # P(max DD > 10 %)
    p_ruin_20pct: float         # P(max DD > 20 %)
    p_ruin_50pct: float         # P(max DD > 50 %)

    # Per-simulation arrays (for plotting)
    all_final_equities: np.ndarray = field(default_factory=lambda: np.array([]))
    all_max_drawdowns: np.ndarray = field(default_factory=lambda: np.array([]))
    all_sharpes: np.ndarray = field(default_factory=lambda: np.array([]))
    all_returns: np.ndarray = field(default_factory=lambda: np.array([]))

    def summary(self) -> str:
        lines = [
            "=" * 60,
            f"  Atlas Monte Carlo Report — {self.n_simulations} simulations",
            "=" * 60,
            "",
            "  Final equity distribution",
            f"    5th  pct  : ${self.final_equity_p5:>12,.2f}  "
            f"(return {self.return_p5 * 100:+.1f}%)",
            f"    25th pct  : ${self.final_equity_p25:>12,.2f}",
            f"    Median    : ${self.final_equity_median:>12,.2f}  "
            f"(return {self.return_median * 100:+.1f}%)",
            f"    75th pct  : ${self.final_equity_p75:>12,.2f}",
            f"    95th pct  : ${self.final_equity_p95:>12,.2f}  "
            f"(return {self.return_p95 * 100:+.1f}%)",
            "",
            "  Drawdown distribution",
            f"    Median max DD  : {self.max_dd_median * 100:.1f}%",
            f"    5th pct max DD : {self.max_dd_p5 * 100:.1f}%  (worst)",
            f"    95th pct max DD: {self.max_dd_p95 * 100:.1f}%  (best)",
            "",
            "  Sharpe distribution",
            f"    Median Sharpe  : {self.sharpe_median:.3f}",
            f"    5th pct Sharpe : {self.sharpe_p5:.3f}",
            f"    95th pct Sharpe: {self.sharpe_p95:.3f}",
            "",
            "  Probability of ruin",
            f"    P(DD > 10%)    : {self.p_ruin_10pct * 100:.1f}%",
            f"    P(DD > 20%)    : {self.p_ruin_20pct * 100:.1f}%",
            f"    P(DD > 50%)    : {self.p_ruin_50pct * 100:.1f}%",
            "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# MonteCarloSimulator
# ---------------------------------------------------------------------------


class MonteCarloSimulator:
    """
    Monte Carlo simulator using trade-sequence permutation.

    Parameters
    ----------
    n_simulations : int
        Number of random permutations to run (default 1000).
    random_seed : int | None
        Seed for reproducibility (default None = random).
    log_dir : Path | None
        Where to save distribution plots. Defaults to ``logs/``.
    """

    def __init__(
        self,
        n_simulations: int = 1000,
        random_seed: int | None = None,
        log_dir: Path | None = None,
    ) -> None:
        if n_simulations < 100:
            raise ValueError("n_simulations must be at least 100 for meaningful statistics")

        self.n_simulations = n_simulations
        self.rng = np.random.default_rng(random_seed)
        self.log_dir = log_dir or (Path(__file__).resolve().parent.parent / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def simulate(
        self,
        trades: list[TradeLog],
        initial_capital: float = 10_000.0,
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation by permuting the observed trade sequence.

        Parameters
        ----------
        trades : list[TradeLog]
            Closed trades from a BacktestResult.
        initial_capital : float
            Starting equity for each simulation path.

        Returns
        -------
        MonteCarloResult
        """
        if not trades:
            logger.warning("MonteCarloSimulator.simulate called with no trades")
            return self._empty_result(initial_capital)

        pnls = np.array([t.net_pnl for t in trades])

        final_equities = np.empty(self.n_simulations)
        max_drawdowns = np.empty(self.n_simulations)
        sharpes = np.empty(self.n_simulations)

        for i in range(self.n_simulations):
            shuffled = self.rng.permutation(pnls)
            eq_curve = initial_capital + np.cumsum(shuffled)
            eq_full = np.concatenate([[initial_capital], eq_curve])

            final_equities[i] = eq_full[-1]

            # Max drawdown
            roll_max = np.maximum.accumulate(eq_full)
            dd = (eq_full - roll_max) / np.maximum(roll_max, 1e-10)
            max_drawdowns[i] = float(np.min(dd))

            # Sharpe (from trade-level returns)
            trade_returns = shuffled / initial_capital
            if len(trade_returns) > 1 and trade_returns.std() > 0:
                # Annualise assuming ~252 trades/year equivalent
                sharpes[i] = (trade_returns.mean() / trade_returns.std()) * math.sqrt(
                    min(252, len(trade_returns))
                )
            else:
                sharpes[i] = 0.0

        all_returns = (final_equities - initial_capital) / initial_capital

        return MonteCarloResult(
            n_simulations=self.n_simulations,
            initial_capital=initial_capital,
            # Equity percentiles
            final_equity_median=float(np.median(final_equities)),
            final_equity_p5=float(np.percentile(final_equities, 5)),
            final_equity_p25=float(np.percentile(final_equities, 25)),
            final_equity_p75=float(np.percentile(final_equities, 75)),
            final_equity_p95=float(np.percentile(final_equities, 95)),
            # Return percentiles
            return_median=float(np.median(all_returns)),
            return_p5=float(np.percentile(all_returns, 5)),
            return_p95=float(np.percentile(all_returns, 95)),
            # Drawdown percentiles (more negative = worse)
            max_dd_median=float(np.median(max_drawdowns)),
            max_dd_p5=float(np.percentile(max_drawdowns, 5)),   # worst
            max_dd_p95=float(np.percentile(max_drawdowns, 95)), # best (least negative)
            # Sharpe percentiles
            sharpe_median=float(np.median(sharpes)),
            sharpe_p5=float(np.percentile(sharpes, 5)),
            sharpe_p95=float(np.percentile(sharpes, 95)),
            # Ruin probabilities
            p_ruin_10pct=float(np.mean(max_drawdowns < -0.10)),
            p_ruin_20pct=float(np.mean(max_drawdowns < -0.20)),
            p_ruin_50pct=float(np.mean(max_drawdowns < -0.50)),
            # Raw arrays for plotting
            all_final_equities=final_equities,
            all_max_drawdowns=max_drawdowns,
            all_sharpes=sharpes,
            all_returns=all_returns,
        )

    def plot_distribution(
        self,
        result: MonteCarloResult,
        filename: str | None = None,
    ) -> Path:
        """
        Save a 4-panel distribution plot to log_dir.

        Returns the path to the saved file.
        """
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError(
                "matplotlib is required for plot_distribution(). "
                "Install with: pip install matplotlib"
            ) from exc

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(
            f"Monte Carlo Distribution — {result.n_simulations} simulations", fontsize=14
        )

        # Final equity distribution
        ax = axes[0, 0]
        ax.hist(result.all_final_equities, bins=50, color="#2196F3", alpha=0.7, edgecolor="white")
        ax.axvline(result.final_equity_median, color="orange", linewidth=2, label="Median")
        ax.axvline(result.final_equity_p5, color="red", linewidth=1.5, linestyle="--", label="5th pct")
        ax.axvline(result.final_equity_p95, color="green", linewidth=1.5, linestyle="--", label="95th pct")
        ax.set_title("Final Equity Distribution")
        ax.set_xlabel("Portfolio Value ($)")
        ax.legend()

        # Return distribution
        ax = axes[0, 1]
        ax.hist(result.all_returns * 100, bins=50, color="#4CAF50", alpha=0.7, edgecolor="white")
        ax.axvline(result.return_median * 100, color="orange", linewidth=2, label="Median")
        ax.axvline(0, color="red", linewidth=1.5, linestyle="--", label="Break-even")
        ax.set_title("Return Distribution (%)")
        ax.set_xlabel("Total Return (%)")
        ax.legend()

        # Max drawdown distribution
        ax = axes[1, 0]
        ax.hist(result.all_max_drawdowns * 100, bins=50, color="#F44336", alpha=0.7, edgecolor="white")
        ax.axvline(result.max_dd_median * 100, color="orange", linewidth=2, label="Median")
        ax.axvline(-20, color="darkred", linewidth=1.5, linestyle="--", label="20% DD threshold")
        ax.set_title("Max Drawdown Distribution (%)")
        ax.set_xlabel("Max Drawdown (%)")
        ax.legend()

        # Sharpe distribution
        ax = axes[1, 1]
        ax.hist(result.all_sharpes, bins=50, color="#9C27B0", alpha=0.7, edgecolor="white")
        ax.axvline(result.sharpe_median, color="orange", linewidth=2, label="Median")
        ax.axvline(1.0, color="green", linewidth=1.5, linestyle="--", label="Sharpe = 1")
        ax.set_title("Sharpe Ratio Distribution")
        ax.set_xlabel("Sharpe Ratio")
        ax.legend()

        fig.tight_layout()

        if filename is None:
            ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"monte_carlo_{ts}.png"
        out_path = self.log_dir / filename
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info("Monte Carlo distribution plot saved to %s", out_path)
        return out_path

    def probability_of_profit(
        self, result: MonteCarloResult, threshold_pct: float = 0.0
    ) -> float:
        """
        Return the fraction of simulations where final return exceeds threshold_pct.

        Parameters
        ----------
        threshold_pct : float
            Return threshold as a fraction (0.10 = 10 %).

        Returns
        -------
        float in [0.0, 1.0]
        """
        return float(np.mean(result.all_returns > threshold_pct))

    def probability_of_ruin(
        self, result: MonteCarloResult, max_drawdown_pct: float = 0.20
    ) -> float:
        """
        Return the fraction of simulations where max drawdown exceeded max_drawdown_pct.

        Parameters
        ----------
        max_drawdown_pct : float
            Drawdown threshold as a positive fraction (0.20 = 20 % drawdown).

        Returns
        -------
        float in [0.0, 1.0]
        """
        return float(np.mean(result.all_max_drawdowns < -abs(max_drawdown_pct)))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_result(initial_capital: float) -> MonteCarloResult:
        empty = np.array([])
        return MonteCarloResult(
            n_simulations=0,
            initial_capital=initial_capital,
            final_equity_median=initial_capital,
            final_equity_p5=initial_capital,
            final_equity_p25=initial_capital,
            final_equity_p75=initial_capital,
            final_equity_p95=initial_capital,
            return_median=0.0,
            return_p5=0.0,
            return_p95=0.0,
            max_dd_median=0.0,
            max_dd_p5=0.0,
            max_dd_p95=0.0,
            sharpe_median=0.0,
            sharpe_p5=0.0,
            sharpe_p95=0.0,
            p_ruin_10pct=0.0,
            p_ruin_20pct=0.0,
            p_ruin_50pct=0.0,
            all_final_equities=empty,
            all_max_drawdowns=empty,
            all_sharpes=empty,
            all_returns=empty,
        )
