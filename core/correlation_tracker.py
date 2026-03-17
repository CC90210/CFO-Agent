"""
core/correlation_tracker.py
----------------------------
Dynamic Correlation Tracker for Atlas Trading Agent.

Tracks rolling correlations between all traded assets to prevent
the system from taking correlated positions that look diversified
but actually amplify risk.

In crypto markets, correlations shift dramatically:
  Bull market: BTC/ETH/SOL correlation → 0.90+ (everything moves together)
  Bear market: Flight-to-quality breaks correlations temporarily
  Crisis:      Everything correlates to 1.0 (crypto winter)

This tracker:
  1. Maintains a rolling 30-day correlation matrix
  2. Flags when correlations spike above 0.7 (risk of synthetic concentration)
  3. Provides the risk manager with real-time correlation data
  4. Recommends position limits based on effective diversification
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("atlas.correlation")


@dataclass
class CorrelationAlert:
    """Alert when correlations become dangerous."""
    pair_a: str
    pair_b: str
    correlation: float
    threshold: float
    message: str


class CorrelationTracker:
    """
    Tracks rolling correlations between traded assets.

    Usage
    -----
    tracker = CorrelationTracker()
    tracker.update("BTC/USDT", btc_returns_series)
    tracker.update("ETH/USDT", eth_returns_series)
    matrix = tracker.get_correlation_matrix()
    alerts = tracker.check_alerts()
    """

    def __init__(
        self,
        window: int = 30,
        alert_threshold: float = 0.70,
        critical_threshold: float = 0.85,
    ) -> None:
        self.window = window
        self.alert_threshold = alert_threshold
        self.critical_threshold = critical_threshold
        self._returns: dict[str, pd.Series] = {}
        self._last_matrix: pd.DataFrame | None = None

    def update(self, symbol: str, returns: pd.Series) -> None:
        """
        Update the return series for a symbol.

        Parameters
        ----------
        symbol  : e.g. "BTC/USDT"
        returns : Pandas Series of log or simple returns
        """
        self._returns[symbol] = returns.tail(self.window * 2)
        self._last_matrix = None  # Invalidate cache

    def update_from_prices(self, symbol: str, prices: pd.Series) -> None:
        """Convenience method — compute returns from price series."""
        if len(prices) < 2:
            return
        returns = prices.pct_change().dropna()
        self.update(symbol, returns)

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Return the current rolling correlation matrix."""
        if self._last_matrix is not None:
            return self._last_matrix

        if len(self._returns) < 2:
            symbols = list(self._returns.keys())
            matrix = pd.DataFrame(
                np.eye(len(symbols)), index=symbols, columns=symbols
            )
            self._last_matrix = matrix
            return matrix

        # Align all return series on a common index
        aligned = pd.DataFrame(self._returns)
        aligned = aligned.dropna(how="all")

        # Use rolling correlation over the window
        if len(aligned) >= self.window:
            matrix = aligned.tail(self.window).corr()
        else:
            matrix = aligned.corr()

        # Fill NaN with 0 (uncorrelated assumption for missing data)
        matrix = matrix.fillna(0.0)
        self._last_matrix = matrix
        return matrix

    def get_correlation(self, symbol_a: str, symbol_b: str) -> float:
        """Get the correlation between two specific symbols."""
        matrix = self.get_correlation_matrix()
        if symbol_a in matrix.index and symbol_b in matrix.columns:
            return float(matrix.loc[symbol_a, symbol_b])
        return 0.0

    def check_alerts(self) -> list[CorrelationAlert]:
        """Check for dangerously high correlations."""
        alerts: list[CorrelationAlert] = []
        matrix = self.get_correlation_matrix()
        symbols = list(matrix.index)

        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = float(matrix.iloc[i, j])
                if abs(corr) >= self.critical_threshold:
                    alerts.append(CorrelationAlert(
                        pair_a=symbols[i],
                        pair_b=symbols[j],
                        correlation=corr,
                        threshold=self.critical_threshold,
                        message=(
                            f"CRITICAL: {symbols[i]} and {symbols[j]} correlation "
                            f"at {corr:.2f} — effectively the same position"
                        ),
                    ))
                elif abs(corr) >= self.alert_threshold:
                    alerts.append(CorrelationAlert(
                        pair_a=symbols[i],
                        pair_b=symbols[j],
                        correlation=corr,
                        threshold=self.alert_threshold,
                        message=(
                            f"WARNING: {symbols[i]} and {symbols[j]} correlation "
                            f"at {corr:.2f} — reduce combined exposure"
                        ),
                    ))

        for alert in alerts:
            logger.warning(alert.message)

        return alerts

    def effective_position_count(self, positions: list[dict[str, Any]]) -> float:
        """
        Calculate the effective number of independent positions.

        If you hold 3 positions but they're all 0.9 correlated, the
        effective position count is closer to 1.0, not 3.0.

        Uses: effective_n = n / (1 + (n-1) * avg_correlation)
        """
        if len(positions) <= 1:
            return float(len(positions))

        symbols = [p.get("symbol", "") for p in positions]
        matrix = self.get_correlation_matrix()
        n = len(symbols)

        # Calculate average pairwise correlation
        total_corr = 0.0
        pair_count = 0
        for i in range(n):
            for j in range(i + 1, n):
                if symbols[i] in matrix.index and symbols[j] in matrix.columns:
                    total_corr += abs(float(matrix.loc[symbols[i], symbols[j]]))
                    pair_count += 1

        avg_corr = total_corr / pair_count if pair_count > 0 else 0.0

        # Effective position count formula
        effective = n / (1.0 + (n - 1.0) * avg_corr)
        return effective

    def max_same_direction_positions(self, symbol: str, direction: str,
                                      current_positions: list[dict[str, Any]]) -> int:
        """
        How many more positions in `direction` can we add given correlations?

        Returns 0 if adding another correlated position would be too risky.
        """
        same_dir = [
            p for p in current_positions
            if p.get("direction") == direction
        ]

        if not same_dir:
            return 3  # No existing positions in this direction

        # Check correlation with each existing same-direction position
        high_corr_count = 0
        for pos in same_dir:
            corr = self.get_correlation(symbol, pos.get("symbol", ""))
            if abs(corr) >= self.alert_threshold:
                high_corr_count += 1

        if high_corr_count >= 2:
            return 0  # Already have 2+ highly correlated positions
        if high_corr_count >= 1:
            return 1  # Allow 1 more but that's it
        return 2  # Low correlation — more room
