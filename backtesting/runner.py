"""
backtesting/runner.py
---------------------
BacktestRunner — entry point for the engine's backtest mode.

Fetches historical OHLCV data via the MarketDataFetcher, passes it through
each configured strategy using BacktestEngine, and returns a summary dict
with full performance metrics.

This module exists so ``core/engine.py`` can import BacktestRunner
without a circular dependency.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from backtesting.engine import BacktestEngine, BacktestResult
from data.fetcher import MarketDataFetcher
from strategies.base import StrategyRegistry

logger = logging.getLogger("atlas.backtest.runner")


class BacktestRunner:
    """
    Orchestrator for backtesting mode.

    Downloads historical data from the exchange, runs each strategy through
    the BacktestEngine, and aggregates results.

    Parameters
    ----------
    strategies:
        Dict mapping strategy name -> YAML config dict (from strategies.yaml).
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
            strategies  -- per-strategy BacktestResult objects and summaries
            portfolio   -- combined portfolio stats
            trades      -- total trade count across all strategies
        """
        logger.info(
            "BacktestRunner.run() | strategies=%s exchange=%s start=%s",
            list(self.strategies.keys()),
            self.exchange_id,
            self.start_date,
        )

        # Ensure strategies are discovered
        StrategyRegistry.discover()

        start_ts = pd.Timestamp(self.start_date, tz="UTC")
        end_ts = (
            pd.Timestamp(self.end_date, tz="UTC")
            if self.end_date
            else pd.Timestamp.now(tz="UTC")
        )

        results: dict[str, Any] = {
            "strategies": {},
            "portfolio": {},
            "trades": 0,
        }

        engine = BacktestEngine(
            initial_capital=self.initial_capital,
            commission_pct=0.001,
            risk_per_trade_pct=0.015,
        )

        total_trades = 0
        all_results: list[BacktestResult] = []

        async with MarketDataFetcher(exchange_id=self.exchange_id) as fetcher:
            for strategy_name, strategy_config in self.strategies.items():
                logger.info("Backtesting strategy: %s", strategy_name)

                try:
                    yaml_params = strategy_config.get("parameters", {})
                    try:
                        strategy = StrategyRegistry.build(strategy_name, **yaml_params)
                    except TypeError:
                        strategy = StrategyRegistry.build(strategy_name)
                        logger.debug(
                            "Strategy %s: YAML params don't match constructor — using defaults",
                            strategy_name,
                        )
                except KeyError:
                    logger.warning(
                        "Strategy '%s' not found in registry — skipping.",
                        strategy_name,
                    )
                    results["strategies"][strategy_name] = {
                        "status": "error",
                        "error": f"Strategy '{strategy_name}' not registered",
                    }
                    continue

                symbols: list[str] = strategy_config.get("symbols", [])
                timeframe: str = strategy_config.get("timeframe", "4h")

                strategy_results: dict[str, Any] = {
                    "symbols": {},
                    "timeframe": timeframe,
                    "status": "completed",
                }

                for symbol in symbols:
                    logger.info(
                        "Downloading %s %s data from %s to %s",
                        symbol, timeframe, self.start_date, self.end_date or "now",
                    )
                    try:
                        df = await fetcher.download_historical(
                            symbol=symbol,
                            timeframe=timeframe,
                            start=start_ts,
                            end=end_ts,
                        )
                    except Exception as exc:
                        logger.error(
                            "Failed to download data for %s: %s", symbol, exc
                        )
                        strategy_results["symbols"][symbol] = {
                            "status": "error",
                            "error": str(exc),
                        }
                        continue

                    if len(df) < 50:
                        logger.warning(
                            "Insufficient data for %s/%s (%d candles) — skipping.",
                            symbol, timeframe, len(df),
                        )
                        strategy_results["symbols"][symbol] = {
                            "status": "skipped",
                            "reason": f"Only {len(df)} candles (need >= 50)",
                        }
                        continue

                    logger.info(
                        "Running backtest: %s on %s (%d candles)",
                        strategy_name, symbol, len(df),
                    )
                    try:
                        result = engine.run(df, strategy)
                        result.symbol = symbol
                        result.strategy_name = strategy_name
                        all_results.append(result)

                        total_trades += result.total_trades

                        strategy_results["symbols"][symbol] = {
                            "status": "completed",
                            "total_return": result.total_return,
                            "sharpe_ratio": result.sharpe_ratio,
                            "sortino_ratio": result.sortino_ratio,
                            "calmar_ratio": result.calmar_ratio,
                            "max_drawdown": result.max_drawdown,
                            "total_trades": result.total_trades,
                            "win_rate": result.win_rate,
                            "profit_factor": result.profit_factor,
                            "expectancy": result.expectancy,
                            "final_equity": result.final_equity,
                        }

                        # Print the report
                        logger.info("\n%s", result.summary())

                        # Export trades and equity curve
                        try:
                            engine.export_trades(
                                result,
                                f"trades_{strategy_name}_{symbol.replace('/', '_')}.csv",
                            )
                        except Exception as exc:
                            logger.warning("Could not export trades: %s", exc)

                    except Exception as exc:
                        logger.error(
                            "Backtest failed for %s on %s: %s",
                            strategy_name, symbol, exc,
                        )
                        strategy_results["symbols"][symbol] = {
                            "status": "error",
                            "error": str(exc),
                        }

                results["strategies"][strategy_name] = strategy_results

        # Portfolio-level aggregation
        if all_results:
            total_final = sum(r.final_equity for r in all_results)
            total_initial = self.initial_capital * len(all_results)
            combined_return = (total_final - total_initial) / total_initial if total_initial else 0

            results["portfolio"] = {
                "combined_return": combined_return,
                "total_final_equity": total_final,
                "total_initial_capital": total_initial,
                "strategies_tested": len(all_results),
                "avg_sharpe": sum(r.sharpe_ratio for r in all_results) / len(all_results),
                "avg_win_rate": sum(r.win_rate for r in all_results) / len(all_results),
                "worst_drawdown": min(r.max_drawdown for r in all_results),
            }

        results["trades"] = total_trades

        logger.info(
            "BacktestRunner finished. %d strategies, %d total trades.",
            len(results["strategies"]),
            total_trades,
        )
        return results
