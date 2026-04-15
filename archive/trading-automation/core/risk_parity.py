"""
core/risk_parity.py
--------------------
Risk Parity Position Allocator for Atlas Trading Agent.

The problem: if you risk 1.5% per trade on BTC (ATR ~$2000) and 1.5% on
DOGE (ATR ~$0.005), you end up with wildly different notional exposures.
The BTC position might be $500 notional while the DOGE position is $50,000.
If DOGE gaps 20%, you're ruined despite "equal risk per trade".

Risk parity solves this by:
  1. Measuring each asset's REALIZED volatility (not just ATR)
  2. Allocating risk budget inversely proportional to volatility
  3. Ensuring no single asset can blow up the portfolio even in a tail event

This module works WITH the existing PositionSizer, not instead of it:
  - PositionSizer calculates the initial size from Kelly + conviction
  - RiskParity then adjusts that size based on the asset's volatility
    relative to the portfolio's target risk

Usage
-----
    parity = RiskParity(target_annual_vol=0.15)
    multiplier = parity.position_multiplier(
        symbol="BTC/USDT",
        current_atr_pct=0.03,  # 3% ATR
        portfolio_vol_target=0.15,  # 15% annual vol target
    )
    # multiplier = 0.82 → reduce BTC position by 18% to stay in vol budget
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("atlas.risk_parity")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_ANNUALIZATION_FACTOR_CRYPTO = 365  # crypto trades 365 days/year
_DEFAULT_TARGET_VOL = 0.15          # 15% annual portfolio volatility target
_MIN_VOL_RATIO = 0.2               # floor — never boost size more than 5x
_MAX_VOL_RATIO = 3.0               # ceiling — never cut size below 33%


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------


@dataclass
class RiskParityResult:
    """Result of risk parity calculation for a single asset."""
    symbol: str
    asset_annual_vol: float       # annualized volatility of this asset
    target_annual_vol: float      # portfolio target
    vol_ratio: float              # asset_vol / target_vol
    position_multiplier: float    # multiply against raw position size
    reasoning: str


# ---------------------------------------------------------------------------
# RiskParity
# ---------------------------------------------------------------------------


class RiskParity:
    """
    Volatility-weighted position allocator.

    Parameters
    ----------
    target_annual_vol : float
        Target annualized portfolio volatility (default 15%).
    lookback_period   : int
        Number of bars to compute realized volatility (default 30).
    """

    def __init__(
        self,
        target_annual_vol: float = _DEFAULT_TARGET_VOL,
        lookback_period: int = 30,
    ) -> None:
        self.target_vol = target_annual_vol
        self.lookback = lookback_period
        self._vol_cache: dict[str, float] = {}

    def compute_asset_volatility(
        self,
        returns: pd.Series,
        annualization: int = _ANNUALIZATION_FACTOR_CRYPTO,
    ) -> float:
        """
        Compute annualized volatility from a return series.

        Parameters
        ----------
        returns        : Series of simple or log returns
        annualization  : number of periods per year (365 for daily crypto)

        Returns
        -------
        float — annualized volatility
        """
        if len(returns) < 5:
            return 0.0
        recent = returns.tail(self.lookback)
        daily_vol = float(recent.std())
        annual_vol = daily_vol * np.sqrt(annualization)
        return annual_vol

    def position_multiplier(
        self,
        symbol: str,
        asset_returns: pd.Series | None = None,
        current_atr_pct: float = 0.0,
    ) -> RiskParityResult:
        """
        Calculate the position size multiplier for risk parity.

        You can pass either a return series (more accurate) or the
        current ATR as a % of price (faster, less accurate).

        Parameters
        ----------
        symbol         : Trading pair, e.g. "BTC/USDT"
        asset_returns  : Series of daily returns (preferred)
        current_atr_pct: ATR / price as a decimal (fallback)

        Returns
        -------
        RiskParityResult with position_multiplier in [0.33, 5.0]
        """
        # Compute asset volatility
        if asset_returns is not None and len(asset_returns) >= 5:
            asset_vol = self.compute_asset_volatility(asset_returns)
        elif current_atr_pct > 0:
            # Rough estimate: annualize ATR% assuming daily bars
            asset_vol = current_atr_pct * np.sqrt(_ANNUALIZATION_FACTOR_CRYPTO)
        else:
            # No data — assume high vol (conservative)
            asset_vol = self.target_vol * 2.0

        # Cache for other components
        self._vol_cache[symbol] = asset_vol

        if asset_vol <= 0:
            return RiskParityResult(
                symbol=symbol,
                asset_annual_vol=0.0,
                target_annual_vol=self.target_vol,
                vol_ratio=1.0,
                position_multiplier=1.0,
                reasoning="Zero volatility — using default size",
            )

        # Vol ratio: how volatile is this asset vs our target?
        vol_ratio = asset_vol / self.target_vol

        # Position multiplier: inverse of vol ratio
        # High vol → smaller position, low vol → larger position
        raw_multiplier = 1.0 / vol_ratio

        # Clamp to prevent extreme sizes
        clamped = max(1.0 / _MAX_VOL_RATIO, min(1.0 / _MIN_VOL_RATIO, raw_multiplier))

        reasoning = (
            f"{symbol}: annual_vol={asset_vol:.2%} vs target={self.target_vol:.2%}, "
            f"vol_ratio={vol_ratio:.2f}, multiplier={clamped:.2f}"
        )
        logger.debug(reasoning)

        return RiskParityResult(
            symbol=symbol,
            asset_annual_vol=asset_vol,
            target_annual_vol=self.target_vol,
            vol_ratio=vol_ratio,
            position_multiplier=clamped,
            reasoning=reasoning,
        )

    def portfolio_allocation(
        self,
        symbols: list[str],
        returns_dict: dict[str, pd.Series],
    ) -> dict[str, float]:
        """
        Compute target allocation weights for a portfolio using risk parity.

        Each asset gets a weight inversely proportional to its volatility,
        so that each contributes equally to total portfolio risk.

        Parameters
        ----------
        symbols      : List of trading symbols
        returns_dict : {symbol: returns_series}

        Returns
        -------
        dict mapping symbol → weight (weights sum to 1.0)
        """
        inv_vols: dict[str, float] = {}

        for sym in symbols:
            returns = returns_dict.get(sym)
            if returns is not None and len(returns) >= 5:
                vol = self.compute_asset_volatility(returns)
            else:
                vol = self.target_vol * 2.0  # penalise unknown assets

            inv_vol = 1.0 / max(vol, 1e-10)
            inv_vols[sym] = inv_vol

        total_inv_vol = sum(inv_vols.values())
        if total_inv_vol <= 0:
            # Equal weight fallback
            n = len(symbols)
            return {sym: 1.0 / n for sym in symbols}

        weights = {sym: iv / total_inv_vol for sym, iv in inv_vols.items()}
        return weights

    def get_cached_vol(self, symbol: str) -> float | None:
        """Return the last computed annualized vol for a symbol, or None."""
        return self._vol_cache.get(symbol)
