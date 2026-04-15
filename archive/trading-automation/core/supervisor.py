"""
core/supervisor.py
------------------
Process Supervisor — the foundation of Atlas autonomous 24/7 operation.

Responsibilities
----------------
* Wrap any async coroutine and restart it on failure with exponential backoff.
* Track crash count and enforce a 24-hour crash ceiling (default 50).
* Log every crash with full traceback.
* Send Telegram alerts on crash and recovery.
* Write a watchdog heartbeat file every 60 s for external liveness monitoring.
* Provide SupervisedEngine — a crash-safe wrapper around TradingEngine that
  persists state to the DB before tearing down and restores it on restart.

Watchdog heartbeat
------------------
  File: logs/watchdog.heartbeat
  Format: ISO-8601 timestamp (e.g. 2026-03-19T14:05:00+00:00)
  Staleness threshold: 5 minutes  (checked externally by scripts/healthcheck.py)

Exponential backoff schedule
----------------------------
  Attempt 1:  5 s
  Attempt 2: 10 s
  Attempt 3: 20 s
  Attempt 4: 40 s
  Attempt 5+: 300 s (5 min, hard cap)

  After 30 minutes of stable running, the backoff is reset to the start.

Usage
-----
    supervisor = ProcessSupervisor(name="engine", alert=alert_sender)
    await supervisor.run(my_async_coro())
"""

from __future__ import annotations

import asyncio
import collections
import datetime
import logging
import traceback
from pathlib import Path
from typing import Any, Callable, Coroutine

from db.database import get_session, health_check, init_db
from db.models import PortfolioSnapshot
from utils.alerts import AlertSender

logger = logging.getLogger("atlas.supervisor")

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent.parent
_LOG_DIR = _ROOT / "logs"
_HEARTBEAT_FILE = _LOG_DIR / "watchdog.heartbeat"

_BACKOFF_STEPS: list[float] = [5.0, 10.0, 20.0, 40.0, 300.0]
_BACKOFF_MAX: float = 300.0
_STABLE_RESET_SECONDS: float = 30 * 60.0   # 30 minutes of clean running resets backoff
_HEARTBEAT_INTERVAL_S: float = 60.0         # Write heartbeat every 60 s
_CRASH_WINDOW_SECONDS: float = 24 * 60 * 60.0  # 24-hour rolling window for crash limit


# ─────────────────────────────────────────────────────────────────────────────
#  ProcessSupervisor
# ─────────────────────────────────────────────────────────────────────────────


class ProcessSupervisor:
    """
    Restarts a failing async coroutine with exponential backoff.

    Parameters
    ----------
    name:
        Human-readable label used in log messages and alerts.
    alert:
        An already-entered AlertSender context (caller owns the lifecycle).
    max_crashes:
        Maximum crashes allowed within a 24-hour window before Atlas halts.
    """

    def __init__(
        self,
        name: str,
        alert: AlertSender,
        max_crashes: int = 50,
    ) -> None:
        self.name = name
        self._alert = alert
        self._max_crashes = max_crashes

        # Rolling deque of crash timestamps (epoch floats)
        self._crash_times: collections.deque[float] = collections.deque()

        # Cumulative uptime / crash counters (for status reporting)
        self.total_crashes: int = 0
        self.total_restarts: int = 0
        self._started_at: datetime.datetime | None = None
        self._last_crash_at: datetime.datetime | None = None

    # ── Public API ───────────────────────────────────────────────────────

    @property
    def uptime_seconds(self) -> float:
        """Elapsed seconds since the supervisor first started."""
        if self._started_at is None:
            return 0.0
        return (datetime.datetime.now(datetime.UTC) - self._started_at).total_seconds()

    @property
    def crashes_in_last_24h(self) -> int:
        """Number of crashes recorded in the last 24 hours."""
        self._prune_crash_window()
        return len(self._crash_times)

    async def run(
        self,
        coro_factory: Callable[[], Coroutine[Any, Any, None]],
        shutdown_event: asyncio.Event | None = None,
    ) -> None:
        """
        Run ``coro_factory()`` in a supervised loop.

        ``coro_factory`` must be a *callable* that returns a fresh coroutine
        each time it is called — not a coroutine object itself — because a
        coroutine can only be awaited once.

        Parameters
        ----------
        coro_factory:
            Zero-argument callable that produces a fresh coroutine on every call.
        shutdown_event:
            If set, the supervisor exits cleanly instead of restarting.
        """
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._started_at = datetime.datetime.now(datetime.UTC)
        backoff_step = 0
        stable_since: float | None = None

        logger.info("[supervisor:%s] Starting supervised run.", self.name)

        while True:
            if shutdown_event is not None and shutdown_event.is_set():
                logger.info("[supervisor:%s] Shutdown event set — exiting supervisor loop.", self.name)
                break

            # ── Check 24-h crash ceiling ──────────────────────────────
            self._prune_crash_window()
            if len(self._crash_times) >= self._max_crashes:
                msg = (
                    f"Supervisor '{self.name}' has crashed {self._max_crashes} times "
                    f"in 24 hours. Halting autonomous operation. Manual review required."
                )
                logger.critical("[supervisor:%s] %s", self.name, msg)
                await self._alert.send_critical(msg)
                break

            # ── Launch the supervised coroutine ───────────────────────
            loop_start = asyncio.get_event_loop().time()
            stable_since = loop_start
            logger.info(
                "[supervisor:%s] Launching coroutine (attempt=%d).",
                self.name,
                self.total_restarts + 1,
            )

            try:
                await coro_factory()
                # Clean return — treat as a normal shutdown, not a crash.
                logger.info("[supervisor:%s] Coroutine exited cleanly.", self.name)
                break

            except asyncio.CancelledError:
                logger.info("[supervisor:%s] Coroutine cancelled — propagating.", self.name)
                raise

            except Exception:  # noqa: BLE001
                elapsed = asyncio.get_event_loop().time() - loop_start
                tb = traceback.format_exc()
                now_utc = datetime.datetime.now(datetime.UTC)

                self.total_crashes += 1
                self._last_crash_at = now_utc
                self._record_crash(now_utc)

                logger.error(
                    "[supervisor:%s] CRASH after %.1fs (total=%d, 24h=%d):\n%s",
                    self.name,
                    elapsed,
                    self.total_crashes,
                    len(self._crash_times),
                    tb,
                )

                # Telegram crash alert — truncate traceback to avoid message size limits
                alert_msg = (
                    f"Supervisor '{self.name}' crashed (#{self.total_crashes} total, "
                    f"#{len(self._crash_times)} in 24h)\n"
                    f"Elapsed before crash: {elapsed:.1f}s\n"
                    f"Traceback (tail):\n{tb[-800:]}"
                )
                await self._alert.send_critical(alert_msg)

                # ── Backoff reset logic ───────────────────────────────
                # If stable_since indicates we ran cleanly for 30+ minutes, reset backoff.
                if stable_since is not None and elapsed >= _STABLE_RESET_SECONDS:
                    backoff_step = 0
                    logger.info(
                        "[supervisor:%s] Ran for %.0fs — resetting backoff.",
                        self.name,
                        elapsed,
                    )

                delay = _BACKOFF_STEPS[min(backoff_step, len(_BACKOFF_STEPS) - 1)]
                backoff_step = min(backoff_step + 1, len(_BACKOFF_STEPS) - 1)

                logger.info(
                    "[supervisor:%s] Restarting in %.0fs...",
                    self.name,
                    delay,
                )

                # Sleep interruptibly so shutdown signals are honoured
                if shutdown_event is not None:
                    try:
                        await asyncio.wait_for(
                            shutdown_event.wait(),
                            timeout=delay,
                        )
                        # Shutdown was set during the sleep
                        logger.info("[supervisor:%s] Shutdown during backoff — exiting.", self.name)
                        break
                    except asyncio.TimeoutError:
                        pass  # Normal: timeout expired, proceed to restart
                else:
                    await asyncio.sleep(delay)

                self.total_restarts += 1
                recovery_msg = (
                    f"Supervisor '{self.name}' recovering after {delay:.0f}s backoff "
                    f"(restart #{self.total_restarts})."
                )
                logger.info("[supervisor:%s] %s", self.name, recovery_msg)
                await self._alert.send_info(recovery_msg)

    # ── Internal helpers ─────────────────────────────────────────────────

    def _record_crash(self, when: datetime.datetime) -> None:
        """Append a crash timestamp to the rolling 24-h window."""
        self._crash_times.append(when.timestamp())

    def _prune_crash_window(self) -> None:
        """Remove crash timestamps older than 24 hours from the deque."""
        cutoff = (
            datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=_CRASH_WINDOW_SECONDS)
        ).timestamp()
        while self._crash_times and self._crash_times[0] < cutoff:
            self._crash_times.popleft()


# ─────────────────────────────────────────────────────────────────────────────
#  Watchdog heartbeat task
# ─────────────────────────────────────────────────────────────────────────────


async def run_watchdog_heartbeat(shutdown_event: asyncio.Event) -> None:
    """
    Write the current UTC timestamp to ``logs/watchdog.heartbeat`` every 60 s.

    External monitors (e.g. scripts/healthcheck.py, Docker HEALTHCHECK) check
    whether this file is more than 5 minutes old.  If it is stale, the process
    is considered dead and the container/systemd unit should be restarted.
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Watchdog heartbeat task started (interval=%ds).", int(_HEARTBEAT_INTERVAL_S))

    while not shutdown_event.is_set():
        try:
            ts = datetime.datetime.now(datetime.UTC).isoformat()
            _HEARTBEAT_FILE.write_text(ts, encoding="utf-8")
            logger.debug("Watchdog heartbeat written: %s", ts)
        except OSError as exc:
            logger.error("Failed to write watchdog heartbeat: %s", exc)

        # Sleep in short increments so shutdown is responsive
        remaining = _HEARTBEAT_INTERVAL_S
        while remaining > 0 and not shutdown_event.is_set():
            chunk = min(remaining, 5.0)
            await asyncio.sleep(chunk)
            remaining -= chunk


# ─────────────────────────────────────────────────────────────────────────────
#  SupervisedEngine
# ─────────────────────────────────────────────────────────────────────────────


class SupervisedEngine:
    """
    Crash-safe wrapper around TradingEngine.

    Lifecycle
    ---------
    1. ``run_forever()`` starts the engine inside a ProcessSupervisor loop.
    2. On each clean start, it restores equity / open-position state from the DB.
    3. On each crash, it persists the last known portfolio snapshot before the
       supervisor sleeps and then relaunches the engine.
    4. Before each restart the supervisor verifies DB and exchange connectivity
       so a transient outage does not cause a fast restart cycle.

    Parameters
    ----------
    mode:
        TradingMode.PAPER or TradingMode.LIVE.
    alert:
        An already-entered AlertSender (caller owns lifecycle).
    supervisor:
        Optional pre-constructed ProcessSupervisor; one is created if not given.
    max_crashes:
        Forwarded to ProcessSupervisor if ``supervisor`` is not supplied.
    """

    def __init__(
        self,
        mode: Any,  # TradingMode — avoid circular import at module level
        alert: AlertSender,
        supervisor: ProcessSupervisor | None = None,
        max_crashes: int = 50,
    ) -> None:
        self._mode = mode
        self._alert = alert
        self._supervisor = supervisor or ProcessSupervisor(
            name="trading-engine",
            alert=alert,
            max_crashes=max_crashes,
        )

    # ── Public API ───────────────────────────────────────────────────────

    async def run_forever(self, shutdown_event: asyncio.Event) -> None:
        """
        Start the supervised engine loop.  Blocks until either the
        shutdown_event is set or the max_crashes ceiling is hit.
        """
        await self._supervisor.run(
            coro_factory=self._engine_coro_factory,
            shutdown_event=shutdown_event,
        )

    # ── Internal coroutine factory ────────────────────────────────────────

    def _engine_coro_factory(self) -> Coroutine[Any, Any, None]:
        """Return a fresh engine coroutine for each supervisor attempt."""
        return self._run_engine_once()

    async def _run_engine_once(self) -> None:
        """
        Run TradingEngine for one supervised lifetime:

        1. Health-check DB and exchange before touching the engine.
        2. Instantiate TradingEngine.
        3. Restore previous equity from DB (engine's own _restore_risk_state
           handles this in _setup(), so we just log the restored value).
        4. Run engine.start() — blocks until engine shuts down or crashes.
        5. On any path out, persist a PortfolioSnapshot so the next restart
           can read the most recent equity figure.
        """
        from core.engine import TradingEngine  # noqa: PLC0415 — deferred to avoid circular import

        # ── Pre-flight checks ─────────────────────────────────────────
        logger.info("[SupervisedEngine] Pre-flight checks before engine start...")

        if not await self._check_db():
            raise RuntimeError("DB health check failed — deferring engine start.")

        if not await self._check_exchange():
            logger.warning(
                "[SupervisedEngine] Exchange connectivity unavailable. "
                "Engine will start but market data may fail on first ticks."
            )

        # ── Log restored equity ───────────────────────────────────────
        restored_equity = self._read_latest_equity()
        logger.info(
            "[SupervisedEngine] Restored equity from DB: $%.2f",
            restored_equity,
        )

        # ── Run engine ────────────────────────────────────────────────
        engine = TradingEngine(mode=self._mode, strategy_names=["all"])
        try:
            await engine.start()
        finally:
            # Always persist state, even on crash
            await self._persist_portfolio_snapshot(engine)

    # ── Health checks ─────────────────────────────────────────────────────

    @staticmethod
    async def _check_db() -> bool:
        """Verify DB is reachable. Tries to init tables if needed."""
        try:
            init_db()
            return health_check()
        except Exception as exc:  # noqa: BLE001
            logger.error("[SupervisedEngine] DB check failed: %s", exc)
            return False

    @staticmethod
    async def _check_exchange() -> bool:
        """
        Quick connectivity test against the configured exchange.
        Returns True on success, False on failure.
        """
        try:
            import ccxt.async_support as ccxt_async  # type: ignore[import]
            from config.settings import settings  # noqa: PLC0415

            exchange_id = settings.exchange.default_exchange
            exchange_class = getattr(ccxt_async, exchange_id, None)
            if exchange_class is None:
                logger.error("[SupervisedEngine] Unknown exchange id: %s", exchange_id)
                return False

            init_kwargs: dict[str, Any] = {
                "apiKey": settings.exchange.exchange_api_key,
                "secret": settings.exchange.exchange_secret,
            }
            if settings.exchange.exchange_passphrase:
                init_kwargs["password"] = settings.exchange.exchange_passphrase

            ex = exchange_class(init_kwargs)
            try:
                await asyncio.wait_for(ex.fetch_ticker("BTC/USDT"), timeout=10.0)
                logger.info("[SupervisedEngine] Exchange connectivity: OK (%s)", exchange_id)
                return True
            finally:
                try:
                    await ex.close()
                except Exception:  # noqa: BLE001
                    pass
        except Exception as exc:  # noqa: BLE001
            logger.error("[SupervisedEngine] Exchange check failed: %s", exc)
            return False

    # ── State persistence / restoration ──────────────────────────────────

    @staticmethod
    def _read_latest_equity() -> float:
        """Read the most recent portfolio equity from DB. Returns 10,000 if none."""
        try:
            with get_session() as session:
                snapshot = (
                    session.query(PortfolioSnapshot)
                    .order_by(PortfolioSnapshot.timestamp.desc())
                    .first()
                )
            return snapshot.total_value if snapshot else 10_000.0
        except Exception as exc:  # noqa: BLE001
            logger.error("[SupervisedEngine] Could not read equity from DB: %s", exc)
            return 10_000.0

    @staticmethod
    async def _persist_portfolio_snapshot(engine: Any) -> None:
        """
        Write a PortfolioSnapshot reflecting the engine's last known state.
        Called in the ``finally`` block of every engine run so state survives
        crashes and clean shutdowns alike.
        """
        try:
            # Access internal risk state — TradingEngine exposes _risk publicly
            equity = getattr(getattr(engine, "_risk", None), "current_equity", None)
            open_positions = getattr(getattr(engine, "_risk", None), "open_positions", 0)
            drawdown_pct = 0.0

            risk = getattr(engine, "_risk", None)
            if risk is not None and hasattr(risk, "drawdown_pct"):
                drawdown_pct = risk.drawdown_pct  # @property on _RiskState, not a method

            if equity is None:
                logger.warning(
                    "[SupervisedEngine] Could not read equity from engine — skipping snapshot."
                )
                return

            mode_label = "paper"
            try:
                from core.engine import TradingMode  # noqa: PLC0415
                if engine.mode != TradingMode.PAPER:
                    mode_label = "live"
            except Exception:  # noqa: BLE001
                pass

            snapshot = PortfolioSnapshot(
                timestamp=datetime.datetime.now(datetime.UTC),
                total_value=equity,
                available_balance=equity,
                unrealized_pnl=0.0,
                realized_pnl_today=0.0,
                drawdown_pct=drawdown_pct,
                positions_json=[],
                mode=mode_label,
            )
            with get_session() as session:
                session.add(snapshot)

            logger.info(
                "[SupervisedEngine] Portfolio snapshot persisted: equity=$%.2f open_pos=%d",
                equity,
                open_positions,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("[SupervisedEngine] Failed to persist portfolio snapshot: %s", exc)
