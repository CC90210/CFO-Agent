"""
core/engine.py
--------------
Main TradingEngine — the orchestration layer for Atlas.

Responsibilities
----------------
* Load and validate strategy configurations.
* Run the event loop: fetch_data -> analyze -> decide -> execute -> log.
* Enforce all risk controls (drawdown, daily loss, position limits).
* Emit heartbeats every 60 s in PAPER and LIVE modes.
* Handle graceful shutdown on SIGINT / SIGTERM.
* Delegate AI analysis to sub-agents (imported from agents/).
* Write all trades, signals, and snapshots to the database.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import signal
import sys
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any

import yaml

import pandas as pd

from config.settings import settings
from core.broker_adapter import BrokerRegistry
from core.correlation_tracker import CorrelationTracker
from core.strategy_health import StrategyHealthMonitor
from core.momentum_classifier import MomentumClassifier
from core.order_executor import ExecutionMode, OrderExecutor, OrderType
from core.playbook import TradingPlaybook
from core.position_sizer import PositionSizer
from core.risk_profiles import get_risk_profile
from core.regime_detector import RegimeDetector, MarketRegime
from core.sentiment_engine import SentimentEngine
from core.trade_protocol import TradeProtocol, ProtocolVerdict
from core.trailing_stop import TrailingStopManager
from utils.alerts import AlertSender
from db.database import get_session, init_db, health_check
from db.models import (
    AgentPerformance,
    DailyPnL,
    PortfolioSnapshot,
    Signal as DBSignal,
    Trade as DBTrade,
)
from strategies.base import BaseStrategy, Direction, Signal as StrategySignal, StrategyRegistry

logger = logging.getLogger(__name__)

# Path to the strategy config relative to this file
_STRATEGIES_YAML = Path(__file__).resolve().parent.parent / "config" / "strategies.yaml"


@dataclass
class _PaperPosition:
    """Tracks a single open position in paper/live mode for SL/TP monitoring."""

    symbol: str
    direction: Direction
    entry_price: float
    size: float
    stop_loss: float
    take_profit: float
    strategy_name: str
    opened_at: datetime.datetime
    db_trade_id: int | None = None
    # Trailing stop state
    highest_since_entry: float = 0.0
    lowest_since_entry: float = float("inf")

# How often the heartbeat snapshot is written (seconds)
HEARTBEAT_INTERVAL_S: int = 60


# ─────────────────────────────────────────────────────────────────────────────
#  Enumerations
# ─────────────────────────────────────────────────────────────────────────────


class TradingMode(Enum):
    """Execution mode for the engine."""

    BACKTEST = auto()
    PAPER = auto()
    LIVE = auto()


# ─────────────────────────────────────────────────────────────────────────────
#  Risk state (in-memory, rebuilt from DB on startup)
# ─────────────────────────────────────────────────────────────────────────────


class _RiskState:
    """
    Tracks real-time risk metrics used by the pre-trade check.

    Fields are updated after every trade close and every snapshot.
    """

    def __init__(self, equity_peak: float = 0.0) -> None:
        self.equity_peak: float = equity_peak
        self.current_equity: float = equity_peak
        self.daily_pnl: float = 0.0
        self.open_positions: int = 0
        self.daily_limit_hit: bool = False
        self.drawdown_limit_hit: bool = False

    # ── Derived metrics ───────────────────────────────────────────────────

    @property
    def drawdown_pct(self) -> float:
        """Current drawdown as a negative percentage."""
        if self.equity_peak <= 0:
            return 0.0
        return ((self.current_equity - self.equity_peak) / self.equity_peak) * 100.0

    @property
    def daily_loss_pct(self) -> float:
        """Today's loss as a negative percentage of opening equity."""
        if self.current_equity <= 0:
            return 0.0
        return (self.daily_pnl / self.current_equity) * 100.0

    # ── Guards ────────────────────────────────────────────────────────────

    def update(self, current_equity: float, daily_pnl: float, open_positions: int) -> None:
        """Refresh state and update peak."""
        self.current_equity = current_equity
        self.daily_pnl = daily_pnl
        self.open_positions = open_positions
        if current_equity > self.equity_peak:
            self.equity_peak = current_equity

        # Check limits — once tripped they stay on until reset
        if self.drawdown_pct <= -settings.risk.max_drawdown_pct:
            if not self.drawdown_limit_hit:
                logger.warning(
                    "MAX DRAWDOWN LIMIT REACHED: %.2f%% (limit: %.2f%%)",
                    self.drawdown_pct,
                    -settings.risk.max_drawdown_pct,
                )
            self.drawdown_limit_hit = True

        if self.daily_loss_pct <= -settings.risk.daily_loss_limit_pct:
            if not self.daily_limit_hit:
                logger.warning(
                    "DAILY LOSS LIMIT REACHED: %.2f%% (limit: %.2f%%)",
                    self.daily_loss_pct,
                    -settings.risk.daily_loss_limit_pct,
                )
            self.daily_limit_hit = True

    def can_trade(self) -> tuple[bool, str]:
        """
        Return (True, "") if trading is allowed, or (False, reason) if blocked.
        """
        if self.drawdown_limit_hit:
            return False, f"Max drawdown limit hit ({self.drawdown_pct:.2f}%)"
        if self.daily_limit_hit:
            return False, f"Daily loss limit hit ({self.daily_loss_pct:.2f}%)"
        if self.open_positions >= settings.risk.max_open_positions:
            return False, f"Max open positions reached ({self.open_positions})"
        return True, ""

    def reset_daily(self) -> None:
        """Call at UTC midnight to reset the daily loss counter."""
        self.daily_pnl = 0.0
        self.daily_limit_hit = False
        logger.info("Daily risk state reset.")


# ─────────────────────────────────────────────────────────────────────────────
#  TradingEngine
# ─────────────────────────────────────────────────────────────────────────────


class TradingEngine:
    """
    Main orchestration engine for Atlas.

    Parameters
    ----------
    mode:
        TradingMode.BACKTEST, .PAPER, or .LIVE.
    strategy_names:
        List of strategy keys from ``config/strategies.yaml``, or
        ``["all"]`` to run every enabled strategy.
    exchange_id:
        CCXT exchange identifier (overrides settings default when provided).
    """

    def __init__(
        self,
        mode: TradingMode,
        strategy_names: list[str],
        exchange_id: str | None = None,
        initial_equity: float | None = None,
    ) -> None:
        self.mode = mode
        self.exchange_id = exchange_id or settings.exchange.default_exchange
        self._strategies: dict[str, dict[str, Any]] = {}
        self._strategy_names = strategy_names
        self._initial_equity = initial_equity
        self._risk = _RiskState()
        self._shutdown_event = asyncio.Event()
        self._running = False

        # Lazy-import ccxt to avoid slow startup when not needed
        self._exchange: Any | None = None  # ccxt.Exchange instance

        # Multi-asset broker registry — routes symbols to correct broker
        self._broker_registry: BrokerRegistry | None = None

        # Strategy instances (populated during setup)
        self._strategy_instances: dict[str, BaseStrategy] = {}

        # Execution subsystems
        exec_mode = ExecutionMode.PAPER if mode == TradingMode.PAPER else ExecutionMode.LIVE
        if mode != TradingMode.BACKTEST:
            self._executor = OrderExecutor(mode=exec_mode)
            self._sizer = PositionSizer()
        else:
            self._executor = None  # type: ignore[assignment]
            self._sizer = None  # type: ignore[assignment]

        # Market regime awareness
        self._regime_detector = RegimeDetector()
        self._current_regime: MarketRegime = MarketRegime.CHOPPY

        # Trade protocol — every signal passes through this before execution
        self._trade_protocol = TradeProtocol(regime_detector=self._regime_detector)

        # Playbook — master decision matrix (regime, vol, session, streaks, drawdown)
        self._playbook = TradingPlaybook()

        # Sentiment engine — aggregates fear/greed, news, macro events
        self._sentiment = SentimentEngine()

        # Momentum classifier — detects market phase (MARKUP, DISTRIBUTION, etc.)
        self._momentum = MomentumClassifier()

        # Darwinian strategy health — auto-disables underperformers
        self._health_monitor = StrategyHealthMonitor()

        # Correlation tracking — feeds dynamic correlation data to the risk layer
        self._correlation_tracker = CorrelationTracker()
        # Mirror of the latest correlation matrix; pushed to RiskManager every 10 ticks
        self._correlations: dict[str, dict[str, float]] = {}
        self._tick_count: int = 0

        # Trailing stop manager — dynamically tightens stops for open positions
        self._trailing_stop = TrailingStopManager(method="chandelier")

        # Paper position tracking — monitors SL/TP for open positions
        self._paper_positions: dict[str, _PaperPosition] = {}

        # Telegram alerts for trade notifications
        self._alert: AlertSender | None = None
        if mode != TradingMode.BACKTEST:
            self._alert = AlertSender()

        logger.info(
            "TradingEngine initialised | mode=%s exchange=%s strategies=%s",
            mode.name,
            self.exchange_id,
            strategy_names,
        )

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def start(self) -> None:
        """
        Public entry point. Runs setup then dispatches to the appropriate loop.
        """
        self._register_signal_handlers()
        await self._setup()

        try:
            if self.mode == TradingMode.BACKTEST:
                await self._run_backtest()
            else:
                await self._run_live_loop()
        except asyncio.CancelledError:
            logger.info("Engine event loop cancelled.")
        finally:
            await self._teardown()

    async def stop(self) -> None:
        """Request a graceful shutdown."""
        logger.info("Shutdown requested.")
        self._shutdown_event.set()

    # ── Setup / teardown ──────────────────────────────────────────────────

    async def _setup(self) -> None:
        """Initialise all subsystems before the main loop starts."""
        logger.info("Setting up engine subsystems...")

        # 1. Database
        init_db()
        if not health_check():
            raise RuntimeError("Database health check failed — cannot start engine.")

        # 2. Strategy config
        self._load_strategies()

        # 3. Exchange connection (skip for backtests that use local data)
        if self.mode != TradingMode.BACKTEST:
            await self._connect_exchange()
            await self._connect_broker_adapters()

        # 4. Restore risk state from DB
        await self._restore_risk_state()

        # 5. Initialize strategy health monitor (Darwinian auto-disable)
        try:
            self._health_monitor.refresh()
            logger.info("Strategy health monitor initialized.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Strategy health monitor init failed (no trades yet?): %s", exc)

        # 6. Start Telegram alert sender for trade notifications
        if self._alert is not None:
            try:
                await self._alert.__aenter__()
                logger.info("Telegram alert sender started.")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Telegram alerts unavailable: %s", exc)
                self._alert = None

        logger.info("Engine setup complete.")

    async def _teardown(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("Engine teardown...")
        self._running = False
        if self._alert is not None:
            try:
                await self._alert.__aexit__(None, None, None)
            except Exception:  # noqa: BLE001
                pass
        if self._exchange and hasattr(self._exchange, "close"):
            try:
                await self._exchange.close()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error closing exchange: %s", exc)
        # Disconnect all broker adapters (Alpaca, OANDA, etc.)
        if self._broker_registry is not None:
            for adapter in self._broker_registry.get_all_adapters():
                try:
                    await adapter.disconnect()
                    logger.info("Broker %s disconnected.", adapter.name)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Error disconnecting broker %s: %s", adapter.name, exc)
        logger.info("Engine stopped.")

    # ── Strategy loading ──────────────────────────────────────────────────

    def _load_strategies(self) -> None:
        """Parse strategies.yaml and filter to the requested names."""
        with open(_STRATEGIES_YAML) as fh:
            raw: dict[str, Any] = yaml.safe_load(fh)

        all_strategies: dict[str, dict[str, Any]] = raw.get("strategies", {})
        run_all = self._strategy_names == ["all"]

        for name, config in all_strategies.items():
            if not config.get("enabled", True):
                continue
            if run_all or name in self._strategy_names:
                self._strategies[name] = config
                logger.info("Loaded strategy: %s", name)

        if not self._strategies:
            raise ValueError(
                f"No enabled strategies matched: {self._strategy_names}. "
                "Check config/strategies.yaml."
            )

        logger.info("Total strategies loaded: %d", len(self._strategies))

        # Build strategy instances from the registry, passing YAML parameters
        StrategyRegistry.discover()
        for name in self._strategies:
            try:
                yaml_params = self._strategies[name].get("parameters", {})
                # Try passing YAML params to constructor; fall back to defaults
                # if param names don't match (YAML uses short names, constructors
                # use prefixed names like rsi_period vs period).
                try:
                    self._strategy_instances[name] = StrategyRegistry.build(name, **yaml_params)
                except TypeError:
                    self._strategy_instances[name] = StrategyRegistry.build(name)
                    logger.debug(
                        "Strategy %s: YAML params don't match constructor — using defaults", name
                    )
                logger.info("Strategy instance created: %s", name)
            except KeyError:
                logger.warning("Strategy '%s' not in registry — analysis will be skipped.", name)

    # ── Exchange connection ────────────────────────────────────────────────

    async def _connect_exchange(self) -> None:
        """
        Instantiate and authenticate a CCXT async exchange.

        We lazy-import ccxt here because it adds ~500 ms to startup;
        backtest mode never touches the exchange.
        """
        try:
            import ccxt.async_support as ccxt_async  # type: ignore[import]
        except ImportError as exc:
            raise ImportError("ccxt is not installed. Run: pip install ccxt") from exc

        exchange_class = getattr(ccxt_async, self.exchange_id, None)
        if exchange_class is None:
            raise ValueError(f"Unknown exchange: {self.exchange_id}")

        _placeholders = {"", "your_exchange_api_key_here", "your_exchange_secret_here"}
        init_kwargs: dict[str, Any] = {"enableRateLimit": True}
        api_key = settings.exchange.exchange_api_key
        api_secret = settings.exchange.exchange_secret
        if api_key and api_key not in _placeholders:
            init_kwargs["apiKey"] = api_key
        if api_secret and api_secret not in _placeholders:
            init_kwargs["secret"] = api_secret
        if settings.exchange.exchange_passphrase:
            init_kwargs["password"] = settings.exchange.exchange_passphrase

        self._exchange = exchange_class(init_kwargs)

        # Validate credentials for paper/live modes
        if not self.mode == TradingMode.BACKTEST:
            try:
                await self._exchange.load_markets()
                logger.info(
                    "Connected to %s — %d markets loaded.",
                    self.exchange_id,
                    len(self._exchange.markets),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to connect to exchange: %s", exc)
                raise

    # ── Multi-asset broker adapters ─────────────────────────────────────────

    async def _connect_broker_adapters(self) -> None:
        """
        Initialize the BrokerRegistry and connect any configured brokers
        (Alpaca for stocks, OANDA for forex/commodities).

        CCXT (crypto) is always available via self._exchange.
        Alpaca/OANDA only connect if API keys are configured in .env.
        The registry auto-routes symbols by format:
          BTC/USDT → CCXT, AAPL → Alpaca, EUR_USD → OANDA
        """
        from core.broker_adapter import (
            AlpacaAdapter,
            CCXTAdapter,
            OANDAAdapter,
        )

        self._broker_registry = BrokerRegistry.instance()

        # Register CCXT adapter for crypto (wraps existing exchange)
        if self._exchange is not None:
            ccxt_adapter = CCXTAdapter(exchange_id=self.exchange_id)
            await ccxt_adapter.connect()
            self._broker_registry.register(ccxt_adapter)
            logger.info("Broker: CCXT (%s) registered for crypto.", self.exchange_id)

        # Register Alpaca for US stocks (if configured)
        if settings.alpaca.configured:
            try:
                alpaca = AlpacaAdapter()
                await alpaca.connect()
                self._broker_registry.register(alpaca)
                logger.info("Broker: Alpaca registered for US stocks.")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Alpaca adapter failed to connect: %s", exc)
        else:
            logger.info("Broker: Alpaca not configured — stock trading disabled.")

        # Register OANDA for forex/commodities (if configured)
        if settings.oanda.configured:
            try:
                oanda = OANDAAdapter()
                await oanda.connect()
                self._broker_registry.register(oanda)
                logger.info("Broker: OANDA registered for forex/commodities.")
            except Exception as exc:  # noqa: BLE001
                logger.warning("OANDA adapter failed to connect: %s", exc)
        else:
            logger.info("Broker: OANDA not configured — forex/commodity trading disabled.")

    # ── Risk state restoration ─────────────────────────────────────────────

    async def _restore_risk_state(self) -> None:
        """
        Read today's P&L and current portfolio value from the DB to
        restore the risk state after a restart.
        """
        today = datetime.date.today()
        with get_session() as session:
            daily = session.query(DailyPnL).filter(DailyPnL.date == today).first()
            latest_snapshot = (
                session.query(PortfolioSnapshot)
                .order_by(PortfolioSnapshot.timestamp.desc())
                .first()
            )
            daily_pnl = daily.realized_pnl if daily else 0.0
            if latest_snapshot:
                equity = latest_snapshot.total_value
            elif self._initial_equity:
                equity = self._initial_equity
            else:
                equity = 10_000.0  # default paper balance
        self._risk = _RiskState(equity_peak=equity)
        self._risk.update(
            current_equity=equity,
            daily_pnl=daily_pnl,
            open_positions=0,
        )
        logger.info(
            "Risk state restored | equity=%.2f daily_pnl=%.2f",
            equity,
            daily_pnl,
        )

    # ── Main event loops ───────────────────────────────────────────────────

    async def _run_live_loop(self) -> None:
        """
        Continuous event loop for PAPER and LIVE modes.

        Runs strategy analysis on each tick interval and writes a
        heartbeat snapshot every HEARTBEAT_INTERVAL_S seconds.
        """
        self._running = True
        mode_label = "PAPER" if self.mode == TradingMode.PAPER else "LIVE"
        logger.info("Starting %s trading loop...", mode_label)

        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        last_midnight = datetime.date.today()

        try:
            while not self._shutdown_event.is_set():
                # Midnight reset
                today = datetime.date.today()
                if today != last_midnight:
                    self._risk.reset_daily()
                    last_midnight = today

                # Check Telegram pause flag
                try:
                    from telegram_bridge import _trading_paused  # noqa: PLC0415
                    if _trading_paused:
                        logger.info("Trading paused via Telegram /pause command")
                        await asyncio.sleep(60)
                        continue
                except ImportError:
                    pass

                # Pre-trade risk check
                allowed, reason = self._risk.can_trade()
                if not allowed:
                    logger.warning("Trading paused: %s", reason)
                    await asyncio.sleep(60)
                    continue

                # Monitor open positions for SL/TP hits before new entries
                await self._monitor_positions()

                # Main tick — run all strategies concurrently for speed
                tick_tasks = [
                    self._tick(name, cfg)
                    for name, cfg in self._strategies.items()
                ]
                await asyncio.gather(*tick_tasks, return_exceptions=True)

                # Sleep before next tick (use the shortest configured timeframe)
                await asyncio.sleep(self._tick_interval_seconds())

        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

    async def _run_backtest(self) -> None:
        """
        Backtest loop — iterates over historical OHLCV bars.

        Full vectorbt integration is wired in backtesting/runner.py;
        this method is the entry point from main.py CLI.
        """
        logger.info("Starting backtest mode...")
        # Delegate to the dedicated backtesting runner
        from backtesting.runner import BacktestRunner  # noqa: PLC0415

        # Forward CLI overrides (set by main.py on the engine instance)
        start = getattr(self, "_backtest_start", "2024-01-01")
        end = getattr(self, "_backtest_end", None)
        capital = getattr(self, "_backtest_capital", 10_000.0)
        symbol_override = getattr(self, "_backtest_symbol", None)

        # If the user passed --symbol, restrict every strategy to that symbol
        strategies = self._strategies
        if symbol_override:
            strategies = {
                name: {**cfg, "symbols": [symbol_override]}
                for name, cfg in strategies.items()
            }

        runner = BacktestRunner(
            strategies=strategies,
            exchange_id=self.exchange_id,
            start_date=start,
            end_date=end,
            initial_capital=capital,
        )
        results = await runner.run()
        logger.info("Backtest complete. Results: %s", results)

    # ── Strategy tick ──────────────────────────────────────────────────────

    async def _tick(self, strategy_name: str, strategy_config: dict[str, Any]) -> None:
        """
        Single strategy tick: fetch data, run analysis, maybe place order.

        Parameters
        ----------
        strategy_name:
            Key from strategies.yaml (e.g. "ema_crossover").
        strategy_config:
            Parsed YAML dict for this strategy.
        """
        symbols: list[str] = strategy_config.get("symbols", [])
        timeframe: str = strategy_config.get("timeframe", "1h")

        # Run all symbols concurrently for this strategy
        symbol_tasks = [
            self._tick_symbol(strategy_name, strategy_config, symbol, timeframe)
            for symbol in symbols
        ]
        results = await asyncio.gather(*symbol_tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    "Tick error [%s / %s]: %s",
                    strategy_name, symbols[i], result,
                )

    async def _tick_symbol(
        self,
        strategy_name: str,
        strategy_config: dict[str, Any],
        symbol: str,
        timeframe: str,
    ) -> None:
        """Process a single symbol for a single strategy."""
        # 0. Darwinian health gate — skip disabled/cooldown strategies
        health_result = self._health_monitor.should_trade(strategy_name)
        if not health_result.allowed:
            logger.info(
                "Strategy %s blocked by health monitor: %s",
                strategy_name, health_result.reason,
            )
            return

        # 1. Fetch OHLCV
        ohlcv = await self._fetch_ohlcv(symbol, timeframe)
        if ohlcv is None or len(ohlcv) < 2:
            logger.warning(
                "OHLCV unavailable or insufficient [%s %s %s] — skipping tick (rows=%s)",
                strategy_name, symbol, timeframe, len(ohlcv) if ohlcv is not None else "None",
            )
            return

        # 2. Feed close prices into correlation tracker
        close_series = pd.Series(
            [row[4] for row in ohlcv],  # index 4 = close price
            index=pd.to_datetime([row[0] for row in ohlcv], unit="ms", utc=True),
        )
        self._correlation_tracker.update_from_prices(symbol, close_series)

        # 3. Every 10 ticks, rebuild the correlation matrix
        self._tick_count += 1
        if self._tick_count % 10 == 0:
            matrix = self._correlation_tracker.get_correlation_matrix()
            self._correlations = {
                sym: {
                    s: float(matrix.loc[sym, s])
                    for s in matrix.columns
                    if s != sym
                }
                for sym in matrix.index
            }
            logger.debug(
                "Correlation matrix refreshed for %d symbols (tick %d)",
                len(self._correlations),
                self._tick_count,
            )

        # 4. Check for critical correlation alerts
        alerts = self._correlation_tracker.check_alerts()
        for alert in alerts:
            if alert.correlation >= 0.85:
                logger.warning("Correlation alert: %s", alert.message)

        # 5. Log effective position count when multiple positions are open
        if self._risk.open_positions > 1:
            open_pos_list = [{"symbol": sym} for sym in self._correlations]
            effective_n = self._correlation_tracker.effective_position_count(
                open_pos_list
            )
            logger.info(
                "Open positions: %d | Effective (correlation-adjusted): %.2f",
                self._risk.open_positions,
                effective_n,
            )

        # 6. Generate signal
        signal = await self._analyze(strategy_name, strategy_config, symbol, ohlcv)
        if signal is None:
            return

        # 7. Pre-trade risk checks (kill-switch layer)
        allowed, reason = self._risk.can_trade()
        if not allowed:
            await self._record_skipped_signal(signal, reason)
            return

        # 7b. Correlation guard — block entry if >2 highly correlated positions open
        open_symbols = list(self._paper_positions.keys()) if hasattr(self, '_paper_positions') else []
        if open_symbols and self._correlations:
            correlated_count = 0
            for open_sym in open_symbols:
                pair_corr = self._correlations.get(open_sym, {}).get(symbol, 0.0)
                if abs(pair_corr) >= 0.80:
                    correlated_count += 1
            if correlated_count >= 2:
                logger.info(
                    "Correlation guard: %s blocked — %d correlated positions already open",
                    symbol, correlated_count,
                )
                await self._record_skipped_signal(signal, "correlated_positions_limit")
                return

        # 8. Trade protocol — 10-step decision framework
        signal_dict = {
            "direction": signal.direction.value,
            "conviction": signal.conviction,
            "strategy_name": signal.strategy_name,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
        }
        protocol_df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        protocol_df["timestamp"] = pd.to_datetime(
            protocol_df["timestamp"], unit="ms", utc=True
        )
        protocol_df = protocol_df.set_index("timestamp").sort_index()
        for _col in ("open", "high", "low", "close", "volume"):
            protocol_df[_col] = pd.to_numeric(protocol_df[_col], errors="coerce")

        protocol_result = self._trade_protocol.evaluate(
            symbol=symbol,
            df=protocol_df,
            signals=[signal_dict],
            current_equity=self._risk.current_equity,
            open_positions=self._risk.open_positions,
            daily_pnl_pct=self._risk.daily_loss_pct,
            max_drawdown_pct=self._risk.drawdown_pct,
        )
        logger.info("Protocol: %s", protocol_result.summary())

        if protocol_result.verdict != ProtocolVerdict.PROCEED:
            await self._record_skipped_signal(
                signal, protocol_result.verdict.value
            )
            return

        # 9. Execute — pass the protocol's sizing recommendation
        await self._execute_signal(
            signal,
            strategy_config,
            protocol_size_pct=protocol_result.position_size_pct,
        )

    # ── Market data ────────────────────────────────────────────────────────

    async def _fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
    ) -> list[list[float]] | None:
        """
        Fetch OHLCV bars from the correct broker for this symbol.

        Routes through BrokerRegistry: crypto → CCXT, stocks → Alpaca,
        forex/commodities → OANDA. Falls back to CCXT if no registry.

        Returns a list of [timestamp, open, high, low, close, volume] rows,
        or None if the fetch fails.
        """
        # Try multi-asset routing first
        if self._broker_registry is not None:
            try:
                adapter = self._broker_registry.get_adapter_for_symbol(symbol)
                if adapter is not None:
                    ohlcv = await adapter.fetch_ohlcv(symbol, timeframe, limit=limit)
                    return ohlcv
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Broker adapter fetch failed [%s %s]: %s — falling back to CCXT",
                    symbol, timeframe, exc,
                )

        # Fallback: direct CCXT (crypto only)
        if self._exchange is None:
            logger.warning("No exchange connected — cannot fetch OHLCV for %s.", symbol)
            return None

        _fallback_timeout = 30.0
        for _attempt in range(1, 4):
            try:
                ohlcv: list[list[float]] = await asyncio.wait_for(
                    self._exchange.fetch_ohlcv(symbol, timeframe, limit=limit),
                    timeout=_fallback_timeout,
                )
                logger.debug("OHLCV fallback fetch OK [%s %s] rows=%d", symbol, timeframe, len(ohlcv))
                return ohlcv
            except asyncio.TimeoutError:
                logger.warning(
                    "OHLCV fallback timeout [%s %s] attempt %d/3",
                    symbol, timeframe, _attempt,
                )
                if _attempt < 3:
                    await asyncio.sleep(2 ** _attempt)
            except Exception as exc:  # noqa: BLE001
                logger.warning("OHLCV fallback fetch failed [%s %s]: %s", symbol, timeframe, exc)
                return None
        logger.error("OHLCV fallback exhausted retries for [%s %s]", symbol, timeframe)
        return None

    # ── AI analysis (stub — agents/ provides the real implementations) ─────

    async def _analyze(
        self,
        strategy_name: str,
        strategy_config: dict[str, Any],
        symbol: str,
        ohlcv: list[list[float]],
    ) -> StrategySignal | None:
        """
        Run the strategy analysis and return a Signal if one is triggered.

        Converts raw OHLCV to a DataFrame, delegates to the registered
        strategy instance, and returns the Signal (or None).
        """
        strategy = self._strategy_instances.get(strategy_name)
        if strategy is None:
            logger.debug("No strategy instance for '%s' — skipping.", strategy_name)
            return None

        # Convert raw OHLCV list to the DataFrame format strategies expect
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp").sort_index()
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"])

        if len(df) < 2:
            return None

        # Detect market regime and apply strategy-specific weight adjustment
        regime_result = self._regime_detector.detect(df)
        self._current_regime = regime_result.regime
        strategy_weights = regime_result.strategy_weights()
        regime_weight = strategy_weights.get(strategy_name, 1.0)

        # If regime strongly disfavours this strategy, skip it entirely
        if regime_weight <= 0.5:
            logger.info(
                "No signal [%s/%s]: regime %s suppressed (weight=%.2f)",
                strategy_name, symbol, regime_result.regime.value, regime_weight,
            )
            return None

        # ── Playbook gate — master decision matrix ────────────────────────
        from core.playbook import detect_session
        utc_hour = datetime.datetime.now(datetime.timezone.utc).hour
        playbook_guidance = self._playbook.evaluate(
            regime=regime_result.regime.value,
            session=detect_session(utc_hour).value,
            current_drawdown_pct=getattr(self._risk, "drawdown_pct", 0.0),
            consecutive_losses=getattr(self._risk, "consecutive_losses", 0),
        )
        if not playbook_guidance.should_trade:
            logger.info(
                "Playbook HALT for %s/%s: %s",
                strategy_name, symbol,
                "; ".join(playbook_guidance.active_rules),
            )
            return None

        # ── Momentum phase context ────────────────────────────────────────
        momentum_phase = self._momentum.classify(df)
        logger.debug(
            "Momentum [%s/%s]: %s", symbol, strategy_name, momentum_phase.summary()
        )

        # Check entry condition then generate signal
        if not strategy.should_enter(df):
            logger.info(
                "No signal [%s/%s]: should_enter=False (regime=%s weight=%.2f)",
                strategy_name, symbol, regime_result.regime.value, regime_weight,
            )
            return None

        signal = strategy.analyze(df)
        if signal is None:
            logger.info("No signal [%s/%s]: strategy.analyze returned None", strategy_name, symbol)
            return None

        if signal.direction == Direction.FLAT:
            logger.info("No signal [%s/%s]: direction=FLAT", strategy_name, symbol)
            return None

        # Scale conviction by regime weight — strategies the regime favours
        # get boosted conviction, disfavoured ones get penalised
        signal.conviction = signal.conviction * regime_weight
        signal.conviction = max(-1.0, min(1.0, signal.conviction))

        # ── Sentiment adjustment — nudge conviction based on market mood ──
        try:
            sentiment_result = await self._sentiment.analyze(symbol)
            signal.conviction = self._sentiment.apply_to_conviction(
                signal.conviction, sentiment_result
            )
            # Store sentiment modifier for position sizing downstream
            if not hasattr(signal, "metadata") or signal.metadata is None:
                signal.metadata = {}
            signal.metadata["sentiment_risk_modifier"] = sentiment_result.risk_modifier
            signal.metadata["sentiment_score"] = sentiment_result.composite_score
            signal.metadata["momentum_phase"] = momentum_phase.phase
            signal.metadata["momentum_confidence"] = momentum_phase.confidence
            signal.metadata["playbook_size_mult"] = playbook_guidance.size_multiplier
        except Exception as exc:  # noqa: BLE001
            logger.debug("Sentiment analysis failed for %s: %s", symbol, exc)

        # Adaptive conviction threshold: strategies with poor track records
        # need higher conviction to trade (learned from Darwinian weights)
        agent_key = f"{strategy_name}_{symbol.replace('/', '')}"
        min_conviction = self._get_adaptive_conviction_threshold(agent_key)
        if abs(signal.conviction) < min_conviction:
            logger.info(
                "No signal [%s/%s]: conviction %.3f below %.2f adaptive threshold",
                strategy_name, symbol, signal.conviction, min_conviction,
            )
            return None

        # Enrich signal with symbol (strategies don't always set it)
        signal.symbol = symbol
        logger.info(
            "Signal generated: %s %s %s conviction=%.3f phase=%s sentiment=%.2f",
            strategy_name, signal.direction.value, symbol, signal.conviction,
            momentum_phase.phase,
            signal.metadata.get("sentiment_score", 0.0) if signal.metadata else 0.0,
        )
        return signal

    # ── Order execution ───────────────────────────────────────────────────

    async def _execute_signal(
        self,
        signal: StrategySignal,
        strategy_config: dict[str, Any],
        protocol_size_pct: float = 0.015,
    ) -> None:
        """
        Convert a StrategySignal into an order.

        In PAPER mode, the order is simulated via OrderExecutor.
        In LIVE mode, the order is sent to the exchange via CCXT.

        Parameters
        ----------
        signal:
            The approved StrategySignal.
        strategy_config:
            Parsed YAML dict for this strategy.
        protocol_size_pct:
            Position size as a fraction of equity recommended by the trade
            protocol (e.g. 0.015 = 1.5%). The final size is the minimum of the
            Kelly-sizer output and this protocol cap, keeping both constraints
            in force simultaneously.
        """
        entry_price = signal.metadata.get("entry_price", 0.0)

        # ── Risk profile override ───────────────────────────────────────
        # Adjust SL/TP based on the empirically optimal risk tier for this
        # strategy-symbol pair. Only escalates when conviction is high enough.
        profile = get_risk_profile(
            signal.strategy_name, signal.symbol, conviction=signal.conviction,
        )
        if profile.name != "conservative" and entry_price > 0 and signal.stop_loss > 0:
            # Recompute SL/TP using the profile's ATR-mult and RR ratio.
            # Preserve the direction of the original stop distance.
            original_sl_dist = abs(entry_price - signal.stop_loss)
            strategy_params = strategy_config.get("parameters", {})
            default_atr_mult = strategy_params.get("atr_stop_mult", 2.0)
            if default_atr_mult > 0:
                atr_estimate = original_sl_dist / default_atr_mult
                new_sl_dist = atr_estimate * profile.atr_stop_mult
                new_tp_dist = new_sl_dist * profile.rr_ratio
                if signal.direction == Direction.LONG:
                    signal.stop_loss = entry_price - new_sl_dist
                    signal.take_profit = entry_price + new_tp_dist
                else:
                    signal.stop_loss = entry_price + new_sl_dist
                    signal.take_profit = entry_price - new_tp_dist
                logger.info(
                    "Risk profile [%s] applied for %s %s: SL=%.4f TP=%.4f",
                    profile.name, signal.strategy_name, signal.symbol,
                    signal.stop_loss, signal.take_profit,
                )

        # Extract multipliers from signal metadata (set by _analyze)
        meta = signal.metadata or {}
        sentiment_mult = meta.get("sentiment_risk_modifier", 1.0)
        playbook_mult = meta.get("playbook_size_mult", 1.0)
        # Health monitor size multiplier (e.g. 0.5 during probation)
        health_result = self._health_monitor.should_trade(signal.strategy_name)
        health_mult = health_result.size_multiplier if health_result.allowed else 0.0
        # Combine playbook, regime, and health into one regime multiplier
        regime_mult = playbook_mult * health_mult

        # Calculate position size via Kelly-based sizer
        size = self._sizer.calculate_position_size(
            portfolio_value=self._risk.current_equity,
            direction=signal.direction.value,
            entry_price=entry_price,
            stop_loss=signal.stop_loss,
            conviction=signal.conviction,
            avg_win_rate=0.55,  # conservative default; Darwinian agent refines this
            avg_rr=2.0,
            regime_multiplier=regime_mult,
            sentiment_multiplier=sentiment_mult,
        )

        # Cap by the protocol's sizing recommendation (convert pct → base units)
        if entry_price > 0 and protocol_size_pct > 0:
            protocol_size_units = (
                protocol_size_pct * self._risk.current_equity
            ) / entry_price
            if protocol_size_units < size:
                logger.debug(
                    "Protocol size cap applied: sizer=%.6f protocol=%.6f",
                    size,
                    protocol_size_units,
                )
                size = protocol_size_units

        if size <= 0:
            logger.info("PositionSizer returned size=0 for %s — trade skipped.", signal.symbol)
            return

        if self.mode == TradingMode.LIVE and not settings.is_live:
            logger.warning(
                "Live order blocked: PAPER_TRADE is still true or CONFIRM_LIVE is not set."
            )
            return

        mode_label = "PAPER" if self.mode == TradingMode.PAPER else "LIVE"
        logger.info(
            "[%s] Executing %s %s size=%.6f conviction=%.2f",
            mode_label, signal.direction.value, signal.symbol, size, signal.conviction,
        )

        record, position = await self._executor.execute_trade(
            signal_symbol=signal.symbol,
            signal_direction=signal.direction,
            size=size,
            entry_price=entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            strategy_name=strategy_config.get("name", signal.strategy_name),
        )

        if position is not None:
            self._risk.open_positions += 1

        # Track position for SL/TP monitoring (both paper AND live)
        if record and record.success and self.mode in (TradingMode.PAPER, TradingMode.LIVE):
            mode_str = "paper" if self.mode == TradingMode.PAPER else "live"
            tracked_pos = _PaperPosition(
                symbol=signal.symbol,
                direction=signal.direction,
                entry_price=entry_price,
                size=size,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                strategy_name=strategy_config.get("name", signal.strategy_name),
                opened_at=datetime.datetime.now(datetime.UTC),
                highest_since_entry=entry_price,
                lowest_since_entry=entry_price,
            )
            # Persist trade entry to DB
            db_trade = DBTrade(
                symbol=signal.symbol,
                exchange=self.exchange_id,
                side="buy" if signal.direction == Direction.LONG else "sell",
                size=size,
                entry_price=entry_price,
                strategy=tracked_pos.strategy_name,
                mode=mode_str,
                opened_at=tracked_pos.opened_at,
            )
            with get_session() as session:
                session.add(db_trade)
                session.flush()
                tracked_pos.db_trade_id = db_trade.id
            self._paper_positions[signal.symbol] = tracked_pos
            logger.info(
                "%s position opened: %s %s @ %.4f SL=%.4f TP=%.4f",
                mode_str.upper(), signal.direction.value, signal.symbol, entry_price,
                signal.stop_loss, signal.take_profit,
            )
            # Telegram alert
            if self._alert is not None:
                try:
                    await self._alert.send_trade_opened(
                        symbol=signal.symbol,
                        direction=signal.direction.value,
                        entry_price=entry_price,
                        size=size,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        conviction=signal.conviction,
                        strategy=paper_pos.strategy_name,
                    )
                except Exception:  # noqa: BLE001
                    pass  # alerts are best-effort

        # Persist signal to DB
        self._persist_signal(signal, executed=record.success if record else False)

        # Refresh strategy health after trade (updates Darwinian metrics)
        try:
            self._health_monitor.refresh()
        except Exception as exc:  # noqa: BLE001
            logger.debug("Health monitor refresh failed: %s", exc)

    # ── Position monitoring (paper + live SL/TP) ────────────────────────────

    async def _monitor_positions(self) -> None:
        """
        Check all open positions against current market prices.
        Updates trailing stops dynamically, then checks SL/TP.
        Works for both paper and live mode.
        """
        if not self._paper_positions:
            return

        symbols_to_close: list[tuple[str, float, str]] = []  # (symbol, exit_price, reason)

        for symbol, pos in self._paper_positions.items():
            # Fetch current price (use 1m candle close as mark price)
            try:
                ohlcv = await self._fetch_ohlcv(symbol, "1m", limit=1)
                if not ohlcv or len(ohlcv) == 0:
                    continue
                mark_price = float(ohlcv[-1][4])  # close price
                bar_high = float(ohlcv[-1][2])
                bar_low = float(ohlcv[-1][3])
            except Exception:  # noqa: BLE001
                continue

            # Update position high/low tracking for trailing stop
            pos.highest_since_entry = max(pos.highest_since_entry, bar_high, mark_price)
            pos.lowest_since_entry = min(pos.lowest_since_entry, bar_low, mark_price)

            # Initialise high/low if this is the first tick after open
            if pos.highest_since_entry <= 0:
                pos.highest_since_entry = max(pos.entry_price, mark_price)
            if pos.lowest_since_entry == float("inf"):
                pos.lowest_since_entry = min(pos.entry_price, mark_price)

            # Fetch ATR for trailing stop calculation (use 4h candle)
            try:
                atr_ohlcv = await self._fetch_ohlcv(symbol, "4h", limit=20)
                if atr_ohlcv and len(atr_ohlcv) >= 14:
                    import numpy as np
                    highs = [float(c[2]) for c in atr_ohlcv[-14:]]
                    lows = [float(c[3]) for c in atr_ohlcv[-14:]]
                    closes = [float(c[4]) for c in atr_ohlcv[-14:]]
                    trs = [max(h - l, abs(h - closes[i - 1]), abs(l - closes[i - 1]))
                           for i, (h, l) in enumerate(zip(highs[1:], lows[1:]), 1)]
                    current_atr = float(np.mean(trs)) if trs else 0.0
                else:
                    current_atr = 0.0
            except Exception:  # noqa: BLE001
                current_atr = 0.0

            # Update trailing stop if ATR is available
            if current_atr > 0:
                ts_result = self._trailing_stop.update(
                    current_price=mark_price,
                    current_atr=current_atr,
                    direction=pos.direction.value,
                    entry_price=pos.entry_price,
                    highest_since_entry=pos.highest_since_entry,
                    lowest_since_entry=pos.lowest_since_entry,
                )
                # Tighten SL if trailing stop is better than current fixed SL
                if pos.direction == Direction.LONG:
                    if ts_result.stop_price > pos.stop_loss:
                        logger.info(
                            "Trailing stop tightened %s: SL %.4f -> %.4f (%s, locked %.0f%%)",
                            symbol, pos.stop_loss, ts_result.stop_price,
                            ts_result.method, ts_result.profit_locked_pct * 100,
                        )
                        pos.stop_loss = ts_result.stop_price
                else:  # SHORT
                    if ts_result.stop_price < pos.stop_loss:
                        logger.info(
                            "Trailing stop tightened %s: SL %.4f -> %.4f (%s, locked %.0f%%)",
                            symbol, pos.stop_loss, ts_result.stop_price,
                            ts_result.method, ts_result.profit_locked_pct * 100,
                        )
                        pos.stop_loss = ts_result.stop_price

            # Check SL/TP
            if pos.direction == Direction.LONG:
                if mark_price <= pos.stop_loss:
                    symbols_to_close.append((symbol, pos.stop_loss, "STOP_LOSS"))
                elif mark_price >= pos.take_profit:
                    symbols_to_close.append((symbol, pos.take_profit, "TAKE_PROFIT"))
            else:  # SHORT
                if mark_price >= pos.stop_loss:
                    symbols_to_close.append((symbol, pos.stop_loss, "STOP_LOSS"))
                elif mark_price <= pos.take_profit:
                    symbols_to_close.append((symbol, pos.take_profit, "TAKE_PROFIT"))

        for symbol, exit_price, reason in symbols_to_close:
            await self._close_tracked_position(symbol, exit_price, reason)

    async def _close_tracked_position(
        self, symbol: str, exit_price: float, reason: str
    ) -> None:
        """Close a tracked position (paper or live) and record the outcome."""
        pos = self._paper_positions.pop(symbol, None)
        if pos is None:
            return

        mode_str = "LIVE" if self.mode == TradingMode.LIVE else "PAPER"

        # ── LIVE MODE: place a real closing order on the exchange ──────────
        if self.mode == TradingMode.LIVE:
            close_side = "sell" if pos.direction == Direction.LONG else "buy"
            try:
                close_record = await self._executor.execute_close(
                    symbol=symbol,
                    side=close_side,
                    size=pos.size,
                )
                if close_record and close_record.success:
                    exit_price = close_record.fill_price
                    logger.info(
                        "LIVE close order FILLED: %s %s size=%.6f @ %.4f",
                        close_side.upper(), symbol, pos.size, exit_price,
                    )
                else:
                    logger.error(
                        "LIVE close order FAILED for %s — keeping exit_price=%.4f from monitor",
                        symbol, exit_price,
                    )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "LIVE close order EXCEPTION for %s: %s — using monitored exit_price=%.4f",
                    symbol, exc, exit_price,
                )

        # Calculate PnL
        if pos.direction == Direction.LONG:
            pnl = (exit_price - pos.entry_price) * pos.size
        else:
            pnl = (pos.entry_price - exit_price) * pos.size

        pnl_pct = (pnl / (pos.entry_price * pos.size) * 100) if pos.entry_price * pos.size != 0 else 0.0

        # Update risk state
        self._risk.current_equity += pnl
        self._risk.daily_pnl += pnl
        self._risk.open_positions = max(0, self._risk.open_positions - 1)
        if self._risk.current_equity > self._risk.equity_peak:
            self._risk.equity_peak = self._risk.current_equity

        # Refresh strategy health from DB (picks up the new closed trade)
        try:
            self._health_monitor.refresh()
        except Exception as exc:  # noqa: BLE001
            logger.debug("Health monitor refresh failed: %s", exc)

        # Persist trade close to DB
        now = datetime.datetime.now(datetime.UTC)
        if pos.db_trade_id is not None:
            with get_session() as session:
                db_trade = session.get(DBTrade, pos.db_trade_id)
                if db_trade is not None:
                    db_trade.exit_price = exit_price
                    db_trade.pnl = pnl
                    db_trade.pnl_pct = pnl_pct
                    db_trade.closed_at = now

        # Update strategy performance in agent_performance table (Darwinian learning)
        agent_key = f"{pos.strategy_name}_{symbol.replace('/', '')}"
        self._update_strategy_performance(agent_key, pnl_pct)

        logger.info(
            "%s position CLOSED [%s]: %s %s @ %.4f -> %.4f | PnL=%.2f (%+.2f%%) | equity=%.2f",
            mode_str, reason, pos.direction.value, symbol, pos.entry_price,
            exit_price, pnl, pnl_pct, self._risk.current_equity,
        )
        # Telegram alert
        if self._alert is not None:
            try:
                await self._alert.send_trade_closed(
                    symbol=symbol,
                    direction=pos.direction.value,
                    exit_price=exit_price,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    exit_reason=reason,
                )
            except Exception:  # noqa: BLE001
                pass  # alerts are best-effort

    # ── Darwinian learning ──────────────────────────────────────────────────

    def _get_adaptive_conviction_threshold(self, strategy_name: str) -> float:
        """
        Return the minimum conviction required for a strategy to trade.

        Strategies with strong Darwinian weights (high win rate) get a lower
        threshold (0.25), while poor performers get a higher bar (0.50).
        New strategies with no track record use the default (0.30).
        """
        try:
            with get_session() as session:
                record = (
                    session.query(AgentPerformance)
                    .filter(AgentPerformance.agent_name == strategy_name)
                    .first()
                )
                if record is None or record.total_trades < 5:
                    return 0.30  # Default for new/untested strategies

                # Map weight (0.3 to 2.5) → threshold (0.50 to 0.25)
                # Higher weight = lower threshold (trusted strategy)
                weight = record.weight
                threshold = 0.50 - (weight - 0.3) * (0.25 / 2.2)
                return max(0.25, min(0.50, threshold))
        except Exception:  # noqa: BLE001
            return 0.30

    def _update_strategy_performance(self, strategy_name: str, pnl_pct: float) -> None:
        """
        Update the AgentPerformance record for a strategy after a trade closes.
        This is the core feedback loop: every closed trade updates the strategy's
        win rate, Sharpe, and weight so the system learns from its results.
        """
        try:
            with get_session() as session:
                record = (
                    session.query(AgentPerformance)
                    .filter(AgentPerformance.agent_name == strategy_name)
                    .first()
                )
                if record is None:
                    record = AgentPerformance(
                        agent_name=strategy_name,
                        weight=1.0,
                        total_trades=0,
                        total_pnl=0.0,
                    )
                    session.add(record)

                # Update trade statistics
                record.total_trades += 1
                record.total_pnl += pnl_pct
                is_win = pnl_pct > 0

                # Recalculate win rate
                old_wins = int((record.win_rate or 0.5) * max(record.total_trades - 1, 1))
                new_wins = old_wins + (1 if is_win else 0)
                record.win_rate = new_wins / record.total_trades

                # Darwinian weight adjustment: reward winners, penalise losers
                if is_win:
                    record.weight = min(2.5, record.weight * 1.08)
                else:
                    record.weight = max(0.3, record.weight * 0.90)

                # Update average conviction (running average)
                record.avg_conviction = record.total_pnl / record.total_trades

                logger.info(
                    "Darwinian update [%s]: trades=%d WR=%.1f%% weight=%.3f pnl_this=%.2f%%",
                    strategy_name,
                    record.total_trades,
                    (record.win_rate or 0) * 100,
                    record.weight,
                    pnl_pct,
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to update strategy performance for %s: %s", strategy_name, exc)

    # ── Database helpers ───────────────────────────────────────────────────

    async def _record_skipped_signal(self, signal: StrategySignal, reason: str) -> None:
        """Persist a signal that was blocked by risk controls."""
        self._persist_signal(signal, executed=False, skip_reason=reason)
        logger.debug("Signal skipped [%s]: %s", signal.symbol, reason)

    def _persist_signal(
        self,
        signal: StrategySignal,
        executed: bool,
        skip_reason: str = "",
    ) -> None:
        """Convert a StrategySignal dataclass to a DB Signal row and persist it."""
        db_signal = DBSignal(
            symbol=signal.symbol,
            direction=signal.direction.value.lower(),
            conviction=signal.conviction,
            source_agent="engine",
            strategy=signal.strategy_name,
            timestamp=signal.timestamp,
            executed=executed,
            skip_reason=skip_reason or None,
            reasoning=str(signal.metadata) if signal.metadata else None,
        )
        with get_session() as session:
            session.add(db_signal)

    async def _write_snapshot(self) -> None:
        """Write a PortfolioSnapshot to the database."""
        # In live/paper mode, fetch real balance from exchange
        total_value = self._risk.current_equity

        snapshot = PortfolioSnapshot(
            timestamp=datetime.datetime.now(datetime.UTC),
            total_value=total_value,
            available_balance=total_value * (1.0 - 0.2 * self._risk.open_positions),  # reserve ~20% per open position
            unrealized_pnl=0.0,
            realized_pnl_today=self._risk.daily_pnl,
            drawdown_pct=self._risk.drawdown_pct,
            positions_json=[],
            mode="paper" if self.mode == TradingMode.PAPER else "live",
        )
        with get_session() as session:
            session.add(snapshot)

        logger.debug(
            "Snapshot written | equity=%.2f drawdown=%.2f%%",
            total_value,
            self._risk.drawdown_pct,
        )

    # ── Heartbeat ─────────────────────────────────────────────────────────

    async def _heartbeat_loop(self) -> None:
        """
        Background coroutine that writes a portfolio snapshot every
        HEARTBEAT_INTERVAL_S seconds.
        """
        while not self._shutdown_event.is_set():
            await asyncio.sleep(HEARTBEAT_INTERVAL_S)
            try:
                await self._write_snapshot()
            except Exception as exc:  # noqa: BLE001
                logger.error("Heartbeat snapshot failed: %s", exc)

    # ── Utility ───────────────────────────────────────────────────────────

    def _tick_interval_seconds(self) -> int:
        """
        Derive the sleep interval from the shortest configured timeframe.

        Maps CCXT-style timeframe strings (1m, 5m, 15m, 1h, 4h, 1d)
        to seconds so the engine wakes up no more often than needed.
        """
        _tf_map: dict[str, int] = {
            "1m": 60,
            "3m": 180,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "2h": 7200,
            "4h": 14400,
            "1d": 86400,
        }
        min_interval = min(
            _tf_map.get(cfg.get("timeframe", "1h"), 3600)
            for cfg in self._strategies.values()
        )
        return min_interval

    # ── OS signal handling ─────────────────────────────────────────────────

    def _register_signal_handlers(self) -> None:
        """
        Register SIGINT / SIGTERM handlers for graceful shutdown.

        Uses the asyncio event loop's ``add_signal_handler`` which is
        safe to call from within a running loop (unlike signal.signal).
        """
        # Windows does not support add_signal_handler on the event loop
        if sys.platform == "win32":
            # Fall back to the synchronous signal module — blocks until the
            # current asyncio iteration completes, which is acceptable.
            signal.signal(signal.SIGINT, self._sync_signal_handler)
            signal.signal(signal.SIGTERM, self._sync_signal_handler)
            return

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))

    def _sync_signal_handler(self, signum: int, frame: Any) -> None:
        """Synchronous fallback signal handler for Windows."""
        logger.info("Signal %d received — requesting shutdown.", signum)
        self._shutdown_event.set()
