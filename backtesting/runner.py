"""
backtesting/runner.py
---------------------
BacktestRunner — entry point for the engine's backtest mode.

Fetches historical OHLCV data via CCXT, passes it through each
configured strategy, and returns a summary dict. Full vectorbt
portfolio analysis is delegated to BacktestEngine (backtesting/engine.py
— to be implemented).

This module exists so ``core/engine.py`` can import BacktestRunner
without a circular dependency.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("atlas.backtest.runner")


class BacktestRunner:
    """
    Thin orchestrator for backtesting mode.

    Parameters
    ----------
    strategies:
        Dict mapping strategy name → YAML config dict (from strategies.yaml).
    exchange_id:
        CCXT exchange to fetch historical data from.
    start_date:
        ISO-8601 start date string (e.g. "2024-01-01").
    end_date:
        ISO-8601 end date string. Defaults to today when None.
    initial_capital:
        Starting capital in USDT for the paper portfolio.
    """

    def __init__(
        self,
        strategies: dict[str, dict[str, Any]],
        exchange_id: str = "binance",
        start_date: str = "2024-01-01",
        end_date: str | None = None,
        initial_capital: float = 10_000.0,
    ) -> None:
        self.strategies = strategies
        self.exchange_id = exchange_id
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital

    async def run(self) -> dict[str, Any]:
        """
        Execute the backtest and return a results summary dict.

        Returns
        -------
        dict with keys:
            strategies  — per-strategy performance metrics
            portfolio   — combined portfolio stats (Sharpe, CAGR, max DD)
            trades      — total trade count across all strategies
        """
        logger.info(
            "BacktestRunner.run() | strategies=%s exchange=%s start=%s",
            list(self.strategies.keys()),
            self.exchange_id,
            self.start_date,
        )

        results: dict[str, Any] = {
            "strategies": {},
            "portfolio": {},
            "trades": 0,
        }

        for strategy_name, strategy_config in self.strategies.items():
            logger.info("Backtesting strategy: %s", strategy_name)
            symbols: list[str] = strategy_config.get("symbols", [])
            timeframe: str = strategy_config.get("timeframe", "1h")

            strategy_result: dict[str, Any] = {
                "symbols": symbols,
                "timeframe": timeframe,
                "status": "pending_implementation",
            }

            results["strategies"][strategy_name] = strategy_result
            logger.info(
                "Strategy '%s' queued for %d symbols on %s — "
                "full vectorbt integration pending.",
                strategy_name,
                len(symbols),
                timeframe,
            )

        logger.info(
            "BacktestRunner finished. Results: %d strategies processed.",
            len(results["strategies"]),
        )
        return results
