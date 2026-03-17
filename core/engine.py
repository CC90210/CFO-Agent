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
from enum import Enum, auto
from pathlib import Path
from typing import Any

import yaml

from config.settings import settings
from db.database import get_session, init_db, health_check
from db.models import DailyPnL, PortfolioSnapshot, Signal, Trade

logger = logging.getLogger(__name__)

# Path to the strategy config relative to this file
_STRATEGIES_YAML = Path(__file__).resolve().parent.parent / "config" / "strategies.yaml"

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
    ) -> None:
        self.mode = mode
        self.exchange_id = exchange_id or settings.exchange.default_exchange
        self._strategies: dict[str, dict[str, Any]] = {}
        self._strategy_names = strategy_names
        self._risk = _RiskState()
        self._shutdown_event = asyncio.Event()
        self._running = False

        # Lazy-import ccxt to avoid slow startup when not needed
        self._exchange: Any | None = None  # ccxt.Exchange instance

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

        # 4. Restore risk state from DB
        await self._restore_risk_state()

        logger.info("Engine setup complete.")

    async def _teardown(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("Engine teardown...")
        self._running = False
        if self._exchange and hasattr(self._exchange, "close"):
            try:
                await self._exchange.close()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error closing exchange: %s", exc)
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

        init_kwargs: dict[str, Any] = {
            "apiKey": settings.exchange.exchange_api_key,
            "secret": settings.exchange.exchange_secret,
        }
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
        equity = latest_snapshot.total_value if latest_snapshot else 10_000.0  # default paper balance
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

                # Pre-trade risk check
                allowed, reason = self._risk.can_trade()
                if not allowed:
                    logger.warning("Trading paused: %s", reason)
                    await asyncio.sleep(60)
                    continue

                # Main tick — iterate all loaded strategies
                for strategy_name, strategy_config in self._strategies.items():
                    await self._tick(strategy_name, strategy_config)

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

        runner = BacktestRunner(
            strategies=self._strategies,
            exchange_id=self.exchange_id,
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

        for symbol in symbols:
            try:
                # 1. Fetch OHLCV
                ohlcv = await self._fetch_ohlcv(symbol, timeframe)
                if ohlcv is None or len(ohlcv) < 2:
                    continue

                # 2. Generate signal (placeholder — agents fill this in)
                signal = await self._analyze(strategy_name, strategy_config, symbol, ohlcv)

                if signal is None:
                    continue

                # 3. Pre-trade checks
                allowed, reason = self._risk.can_trade()
                if not allowed:
                    await self._record_skipped_signal(signal, reason)
                    continue

                # 4. Execute
                await self._execute_signal(signal, strategy_config)

            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Tick error [%s / %s]: %s",
                    strategy_name,
                    symbol,
                    exc,
                    exc_info=True,
                )

    # ── Market data ────────────────────────────────────────────────────────

    async def _fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
    ) -> list[list[float]] | None:
        """
        Fetch OHLCV bars from the exchange.

        Returns a list of [timestamp, open, high, low, close, volume] rows,
        or None if the fetch fails.
        """
        if self._exchange is None:
            logger.warning("Exchange not connected — cannot fetch OHLCV.")
            return None

        try:
            ohlcv: list[list[float]] = await self._exchange.fetch_ohlcv(
                symbol, timeframe, limit=limit
            )
            return ohlcv
        except Exception as exc:  # noqa: BLE001
            logger.warning("OHLCV fetch failed [%s %s]: %s", symbol, timeframe, exc)
            return None

    # ── AI analysis (stub — agents/ provides the real implementations) ─────

    async def _analyze(
        self,
        strategy_name: str,
        strategy_config: dict[str, Any],
        symbol: str,
        ohlcv: list[list[float]],
    ) -> Signal | None:
        """
        Run the strategy analysis and return a Signal if one is triggered.

        This method is intentionally thin — all strategy logic lives in
        the ``strategies/`` and ``agents/`` packages. Concrete
        implementations will be registered here as the codebase grows.

        Returns None when no actionable signal is produced.
        """
        # TODO: route to the correct strategy module based on strategy_name
        logger.debug("Analyzing %s / %s via strategy=%s", symbol, "ohlcv", strategy_name)
        return None

    # ── Order execution ───────────────────────────────────────────────────

    async def _execute_signal(
        self,
        signal: Signal,
        strategy_config: dict[str, Any],
    ) -> None:
        """
        Convert a Signal into an order.

        In PAPER mode, the order is simulated and only recorded to DB.
        In LIVE mode, the order is sent to the exchange via CCXT.
        """
        if self.mode == TradingMode.PAPER:
            logger.info(
                "[PAPER] Would %s %s conviction=%.2f",
                signal.direction,
                signal.symbol,
                signal.conviction,
            )
            # Mark signal as executed and write to DB
            signal.executed = True
            with get_session() as session:
                session.merge(signal)
            return

        # LIVE — requires CONFIRM_LIVE=true
        if not settings.is_live:
            logger.warning(
                "Live order blocked: PAPER_TRADE is still true or CONFIRM_LIVE is not set."
            )
            return

        if self._exchange is None:
            logger.error("Cannot execute live order: exchange not connected.")
            return

        logger.info(
            "[LIVE] Executing %s %s conviction=%.2f",
            signal.direction,
            signal.symbol,
            signal.conviction,
        )
        # TODO: calculate position size from risk_per_trade and ATR stop
        # TODO: place market/limit order via self._exchange.create_order(...)

    # ── Database helpers ───────────────────────────────────────────────────

    async def _record_skipped_signal(self, signal: Signal, reason: str) -> None:
        """Persist a signal that was blocked by risk controls."""
        signal.executed = False
        signal.skip_reason = reason
        with get_session() as session:
            session.add(signal)
        logger.debug("Signal skipped [%s]: %s", signal.symbol, reason)

    async def _write_snapshot(self) -> None:
        """Write a PortfolioSnapshot to the database."""
        # In live/paper mode, fetch real balance from exchange
        total_value = self._risk.current_equity

        snapshot = PortfolioSnapshot(
            timestamp=datetime.datetime.now(datetime.UTC),
            total_value=total_value,
            available_balance=total_value,  # TODO: subtract locked margin
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
