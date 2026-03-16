"""
autonomous.py
-------------
Atlas Trading Agent — Autonomous 24/7 Daemon.

Runs as a persistent process (not a cron job). Uses a pure asyncio
scheduler to execute tasks on configurable intervals without any
third-party scheduler library.

Schedule
--------
  Heartbeat       — every 5 minutes  (portfolio value + alive ping to DB/log)
  Market scan     — every 15 minutes (all watchlist symbols, quick signal check)
  Deep analysis   — every 1 hour     (full multi-agent analysis on top movers)
  Rebalance check — every 4 hours    (portfolio rebalance evaluation)
  Daily summary   — 00:00 UTC daily  (P&L, trades, portfolio snapshot via Telegram)
  Weekly evolve   — Sunday 00:00 UTC (Darwinian agent weight updates)

Usage
-----
  python autonomous.py                           # paper mode (default, safe)
  python autonomous.py --live --confirm-live     # live trading (double gate)
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
#  Path setup — must happen before any project imports
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ─────────────────────────────────────────────────────────────────────────────
#  Logging — configure before any project imports so all handlers inherit it
# ─────────────────────────────────────────────────────────────────────────────

_LOG_DIR = _ROOT / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_LOG_DIR / "autonomous.log"),
    ],
)
logger = logging.getLogger("atlas.autonomous")

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports (after path + logging setup)
# ─────────────────────────────────────────────────────────────────────────────

from config.settings import settings  # noqa: E402
from db.database import get_session, health_check, init_db  # noqa: E402
from db.models import AgentPerformance, DailyPnL, PortfolioSnapshot, Trade  # noqa: E402
from utils.alerts import AlertSender  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
#  Required environment variable names (values are never logged)
# ─────────────────────────────────────────────────────────────────────────────

_REQUIRED_ENV_KEYS: list[str] = [
    "DATABASE_URL",
    "DEFAULT_EXCHANGE",
]

# Intervals (seconds) — read from env at startup, with safe defaults
_HEARTBEAT_INTERVAL_S: int = 5 * 60        # 5 minutes
_SCAN_INTERVAL_S: int = 15 * 60            # 15 minutes
_DEEP_ANALYSIS_INTERVAL_S: int = 60 * 60  # 1 hour
_REBALANCE_INTERVAL_S: int = 4 * 60 * 60  # 4 hours


# ─────────────────────────────────────────────────────────────────────────────
#  Startup checks
# ─────────────────────────────────────────────────────────────────────────────


def _check_env() -> list[str]:
    """
    Verify required environment variables are present (not that they are valid).
    Returns a list of missing key names.
    """
    missing: list[str] = []
    for key in _REQUIRED_ENV_KEYS:
        if not os.environ.get(key):
            missing.append(key)
    return missing


async def _check_exchange_connectivity() -> bool:
    """
    Attempt to fetch one ticker from the configured exchange.
    Returns True on success, False on failure.
    """
    try:
        import ccxt.async_support as ccxt_async  # type: ignore[import]

        exchange_id = settings.exchange.default_exchange
        exchange_class = getattr(ccxt_async, exchange_id, None)
        if exchange_class is None:
            logger.error("Unknown exchange id: %s", exchange_id)
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
            logger.info("Exchange connectivity: OK (%s)", exchange_id)
            return True
        finally:
            try:
                await ex.close()
            except Exception:  # noqa: BLE001
                pass
    except Exception as exc:  # noqa: BLE001
        logger.error("Exchange connectivity check failed: %s", exc)
        return False


def _get_strategy_count() -> int:
    """Return the number of enabled strategies from config."""
    try:
        import yaml

        cfg_path = _ROOT / "config" / "strategies.yaml"
        if not cfg_path.exists():
            return 0
        with open(cfg_path) as fh:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
        strategies = raw.get("strategies", {})
        return sum(1 for v in strategies.values() if v.get("enabled", True))
    except Exception:  # noqa: BLE001
        return 0


def _get_portfolio_value() -> float:
    """Read the latest portfolio value from the database."""
    try:
        with get_session() as session:
            latest = (
                session.query(PortfolioSnapshot)
                .order_by(PortfolioSnapshot.timestamp.desc())
                .first()
            )
        return latest.total_value if latest else 10_000.0
    except Exception:  # noqa: BLE001
        return 10_000.0


def _print_banner(mode: str, exchange: str, strategies: int, portfolio: float) -> None:
    """Print the startup banner to stdout."""
    width = 60
    inner = width - 2  # space inside the ║ borders
    lines = [
        f"╔{'═' * width}╗",
        f"║  {'ATLAS TRADING AGENT — AUTONOMOUS DAEMON'.ljust(inner - 2)}  ║",
        f"║  {f'Mode: {mode}  |  Exchange: {exchange}  |  Strategies: {strategies}'.ljust(inner - 2)}  ║",
        f"║  {f'Portfolio: ${portfolio:,.2f}  |  Heartbeat: 5min'.ljust(inner - 2)}  ║",
        f"║  {'\"Protect capital first. Compound gains second.\"'.ljust(inner - 2)}  ║",
        f"╚{'═' * width}╝",
    ]
    for line in lines:
        print(line)


# ─────────────────────────────────────────────────────────────────────────────
#  Scheduled task helpers
# ─────────────────────────────────────────────────────────────────────────────


async def _run_heartbeat(alert: AlertSender) -> None:
    """
    Write a portfolio snapshot to the database and optionally send a
    Telegram heartbeat. This is the lowest-level health indicator.
    """
    try:
        portfolio_value = _get_portfolio_value()
        snapshot = PortfolioSnapshot(
            timestamp=datetime.datetime.utcnow(),
            total_value=portfolio_value,
            available_balance=portfolio_value,
            unrealized_pnl=0.0,
            realized_pnl_today=0.0,
            drawdown_pct=0.0,
            positions_json=[],
            mode="paper" if settings.is_paper else "live",
        )
        with get_session() as session:
            session.add(snapshot)
        logger.info("Heartbeat | portfolio=$%.2f", portfolio_value)
    except Exception as exc:  # noqa: BLE001
        logger.error("Heartbeat failed: %s", exc)


async def _run_market_scan(alert: AlertSender) -> None:
    """
    Quick scan of all watchlist symbols. Generates signals via the
    trading engine tick. Does not perform deep multi-agent analysis.
    """
    try:
        logger.info("Market scan starting...")
        from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

        mode = TradingMode.PAPER if settings.is_paper else TradingMode.LIVE
        engine = TradingEngine(mode=mode, strategy_names=["all"])
        await engine._setup()

        for strategy_name, strategy_config in engine._strategies.items():
            await engine._tick(strategy_name, strategy_config)

        await engine._teardown()
        logger.info("Market scan complete.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Market scan failed: %s", exc)


async def _run_deep_analysis(alert: AlertSender) -> None:
    """
    Full multi-agent analysis on the top movers from the last scan.
    More expensive than a quick scan — runs every hour.
    """
    try:
        logger.info("Deep analysis starting...")
        # TODO: integrate with agents/ multi-agent orchestrator once implemented.
        # For now, run a full engine tick on all strategies (same as scan but logged differently).
        from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

        mode = TradingMode.PAPER if settings.is_paper else TradingMode.LIVE
        engine = TradingEngine(mode=mode, strategy_names=["all"])
        await engine._setup()

        for strategy_name, strategy_config in engine._strategies.items():
            await engine._tick(strategy_name, strategy_config)

        await engine._teardown()
        logger.info("Deep analysis complete.")
    except Exception as exc:  # noqa: BLE001
        logger.error("Deep analysis failed: %s", exc)


async def _run_rebalance_check(alert: AlertSender) -> None:
    """
    Evaluate whether the portfolio needs rebalancing. Checks position
    sizes against target allocations and risk limits.
    """
    try:
        logger.info("Rebalance check starting...")
        portfolio_value = _get_portfolio_value()
        # TODO: integrate with position manager once implemented.
        # Currently logs the check and sends a Telegram update.
        await alert.send_info(
            f"Portfolio rebalance check\n"
            f"Value: ${portfolio_value:,.2f}\n"
            f"(Full rebalance logic pending position manager integration)"
        )
        logger.info("Rebalance check complete | portfolio=$%.2f", portfolio_value)
    except Exception as exc:  # noqa: BLE001
        logger.error("Rebalance check failed: %s", exc)


async def _run_daily_summary(alert: AlertSender) -> None:
    """
    Send the daily P&L summary at UTC midnight. Also resets the
    engine's daily risk counter.
    """
    try:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        logger.info("Running daily summary for %s...", yesterday)

        with get_session() as session:
            daily = session.query(DailyPnL).filter(DailyPnL.date == yesterday).first()
            latest = (
                session.query(PortfolioSnapshot)
                .order_by(PortfolioSnapshot.timestamp.desc())
                .first()
            )
            today_start = datetime.datetime.combine(yesterday, datetime.time.min)
            today_end = datetime.datetime.combine(today, datetime.time.min)
            closed_trades = (
                session.query(Trade)
                .filter(
                    Trade.closed_at >= today_start,
                    Trade.closed_at < today_end,
                    Trade.pnl.isnot(None),
                )
                .all()
            )

        pnl = daily.realized_pnl if daily else 0.0
        equity = latest.total_value if latest else 10_000.0
        drawdown = latest.drawdown_pct if latest else 0.0
        pnl_pct = (pnl / equity * 100.0) if equity else 0.0
        trades_count = len(closed_trades)
        wins = sum(1 for t in closed_trades if (t.pnl or 0.0) > 0)
        losses = trades_count - wins

        await alert.send_daily_summary(
            date=str(yesterday),
            pnl=pnl,
            pnl_pct=pnl_pct,
            trades_opened=trades_count,
            trades_closed=trades_count,
            current_equity=equity,
            drawdown_pct=abs(drawdown),
        )
        logger.info(
            "Daily summary sent | date=%s pnl=%.2f equity=%.2f trades=%d",
            yesterday,
            pnl,
            equity,
            trades_count,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Daily summary failed: %s", exc)


async def _run_weekly_evolution(alert: AlertSender) -> None:
    """
    Darwinian agent weight update. Runs every Sunday at UTC midnight.
    Adjusts each agent's influence weight based on historical Sharpe and win rate.
    """
    try:
        logger.info("Weekly evolution run starting...")
        with get_session() as session:
            agents = session.query(AgentPerformance).all()

        if not agents:
            logger.info("No agent performance data — skipping weekly evolution.")
            return

        # Compute new weights proportional to win rate (floor at 0.1)
        total_weight = 0.0
        updates: list[tuple[str, float]] = []
        for agent in agents:
            if agent.win_rate is not None and agent.total_trades >= 10:
                new_weight = max(0.1, agent.win_rate)
            else:
                new_weight = agent.weight  # keep existing if insufficient data
            updates.append((agent.agent_name, new_weight))
            total_weight += new_weight

        # Normalise to sum to 1.0
        if total_weight > 0:
            updates = [(name, w / total_weight) for name, w in updates]

        with get_session() as session:
            for agent in session.query(AgentPerformance).all():
                for name, new_weight in updates:
                    if agent.agent_name == name:
                        agent.weight = new_weight

        summary_lines = [f"{name}: {w:.3f}" for name, w in updates]
        await alert.send_info(
            "Weekly agent evolution complete\n" + "\n".join(summary_lines)
        )
        logger.info("Weekly evolution complete. %d agents updated.", len(updates))
    except Exception as exc:  # noqa: BLE001
        logger.error("Weekly evolution failed: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
#  Interval scheduler (pure asyncio — no third-party scheduler)
# ─────────────────────────────────────────────────────────────────────────────


async def _interval_task(
    name: str,
    interval_s: int,
    coro_fn: Any,
    alert: AlertSender,
    shutdown_event: asyncio.Event,
) -> None:
    """
    Run ``coro_fn(alert)`` every ``interval_s`` seconds until
    ``shutdown_event`` is set. Exceptions in the coro are caught and
    logged — the loop never crashes.
    """
    logger.info("Scheduled task '%s' started (interval=%ds).", name, interval_s)
    while not shutdown_event.is_set():
        try:
            await coro_fn(alert)
        except Exception as exc:  # noqa: BLE001
            # Belt-and-suspenders: individual tasks already catch, but we
            # add an outer guard so a badly-behaved coro can never kill the
            # scheduler loop.
            logger.error("Unhandled exception in task '%s': %s", name, exc)

        # Sleep in small increments so we can respond to shutdown quickly
        remaining = interval_s
        while remaining > 0 and not shutdown_event.is_set():
            chunk = min(remaining, 10)
            await asyncio.sleep(chunk)
            remaining -= chunk


async def _daily_task(
    name: str,
    coro_fn: Any,
    alert: AlertSender,
    shutdown_event: asyncio.Event,
) -> None:
    """
    Run ``coro_fn(alert)`` once per day at UTC midnight.
    """
    logger.info("Daily task '%s' registered (fires at 00:00 UTC).", name)
    while not shutdown_event.is_set():
        now = datetime.datetime.utcnow()
        # Calculate seconds until next midnight UTC
        tomorrow = (now + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        wait_s = (tomorrow - now).total_seconds()
        logger.debug("Daily task '%s': next run in %.0fs.", name, wait_s)

        # Sleep until midnight in small increments for responsive shutdown
        while wait_s > 0 and not shutdown_event.is_set():
            chunk = min(wait_s, 30)
            await asyncio.sleep(chunk)
            wait_s -= chunk

        if shutdown_event.is_set():
            break

        try:
            await coro_fn(alert)
        except Exception as exc:  # noqa: BLE001
            logger.error("Unhandled exception in daily task '%s': %s", name, exc)


async def _weekly_task(
    name: str,
    coro_fn: Any,
    alert: AlertSender,
    shutdown_event: asyncio.Event,
) -> None:
    """
    Run ``coro_fn(alert)`` once per week on Sunday at UTC midnight.
    """
    logger.info("Weekly task '%s' registered (fires Sunday 00:00 UTC).", name)
    while not shutdown_event.is_set():
        now = datetime.datetime.utcnow()
        # days_until_sunday: 0=Monday ... 6=Sunday (weekday() returns 0=Mon)
        days_until = (6 - now.weekday()) % 7
        if days_until == 0 and (now.hour > 0 or now.minute > 0):
            days_until = 7  # already past midnight Sunday, wait for next week
        next_sunday = (now + datetime.timedelta(days=days_until)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        wait_s = (next_sunday - now).total_seconds()
        logger.debug("Weekly task '%s': next run in %.0fs.", name, wait_s)

        while wait_s > 0 and not shutdown_event.is_set():
            chunk = min(wait_s, 60)
            await asyncio.sleep(chunk)
            wait_s -= chunk

        if shutdown_event.is_set():
            break

        try:
            await coro_fn(alert)
        except Exception as exc:  # noqa: BLE001
            logger.error("Unhandled exception in weekly task '%s': %s", name, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────


async def run(live: bool = False, confirm_live: bool = False) -> None:
    """
    Primary coroutine for the autonomous daemon.

    Parameters
    ----------
    live:
        When True, attempt to start in LIVE mode.
    confirm_live:
        Second confirmation required for live mode.
    """

    # 1. Live mode guard — two explicit flags required
    if live and not confirm_live:
        logger.error(
            "Live mode requires --confirm-live as a second confirmation. "
            "Pass both --live and --confirm-live to enable real order execution."
        )
        sys.exit(1)

    # 2. Environment variable check
    missing_keys = _check_env()
    if missing_keys:
        logger.error("Missing required environment variables: %s", missing_keys)
        sys.exit(1)

    # 3. Database initialisation
    logger.info("Initialising database...")
    try:
        init_db()
    except Exception as exc:  # noqa: BLE001
        logger.error("Database init failed: %s", exc)
        sys.exit(1)

    if not health_check():
        logger.error("Database health check failed. Aborting.")
        sys.exit(1)

    # 4. Exchange connectivity check
    exchange_ok = await _check_exchange_connectivity()
    if not exchange_ok:
        logger.warning(
            "Exchange connectivity check failed. "
            "The daemon will start but market scans may fail until connectivity is restored."
        )

    # 5. Gather info for the banner
    mode_label = "LIVE" if (live and confirm_live) else "PAPER"
    exchange_label = settings.exchange.default_exchange.upper()
    strategy_count = _get_strategy_count()
    portfolio_value = _get_portfolio_value()

    _print_banner(mode_label, exchange_label, strategy_count, portfolio_value)

    # 6. Shutdown event — shared across all tasks
    shutdown_event = asyncio.Event()

    def _handle_signal(signum: int, frame: object) -> None:
        logger.info("Signal %d received — initiating graceful shutdown.", signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # 7. Start the alert sender and all scheduled tasks
    logger.info("Starting autonomous daemon (mode=%s)...", mode_label)

    async with AlertSender() as alert:
        await alert.send_info(
            f"Atlas Autonomous Daemon started\n"
            f"Mode: {mode_label} | Exchange: {exchange_label}\n"
            f"Portfolio: ${portfolio_value:,.2f}"
        )

        # Schedule all recurring tasks as concurrent asyncio tasks
        tasks = [
            asyncio.create_task(
                _interval_task(
                    "heartbeat",
                    _HEARTBEAT_INTERVAL_S,
                    _run_heartbeat,
                    alert,
                    shutdown_event,
                ),
                name="heartbeat",
            ),
            asyncio.create_task(
                _interval_task(
                    "market-scan",
                    _SCAN_INTERVAL_S,
                    _run_market_scan,
                    alert,
                    shutdown_event,
                ),
                name="market-scan",
            ),
            asyncio.create_task(
                _interval_task(
                    "deep-analysis",
                    _DEEP_ANALYSIS_INTERVAL_S,
                    _run_deep_analysis,
                    alert,
                    shutdown_event,
                ),
                name="deep-analysis",
            ),
            asyncio.create_task(
                _interval_task(
                    "rebalance-check",
                    _REBALANCE_INTERVAL_S,
                    _run_rebalance_check,
                    alert,
                    shutdown_event,
                ),
                name="rebalance-check",
            ),
            asyncio.create_task(
                _daily_task("daily-summary", _run_daily_summary, alert, shutdown_event),
                name="daily-summary",
            ),
            asyncio.create_task(
                _weekly_task(
                    "weekly-evolution", _run_weekly_evolution, alert, shutdown_event
                ),
                name="weekly-evolution",
            ),
        ]

        logger.info("All %d scheduled tasks running. Daemon is alive.", len(tasks))

        # Block until shutdown is requested
        await shutdown_event.wait()

        logger.info("Shutdown event received — cancelling tasks...")
        for task in tasks:
            task.cancel()

        # Await all cancellations cleanly
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for task, result in zip(tasks, results):
            if isinstance(result, Exception) and not isinstance(
                result, asyncio.CancelledError
            ):
                logger.error("Task '%s' raised during shutdown: %s", task.get_name(), result)

        await alert.send_info("Atlas Autonomous Daemon stopped.")

    logger.info("Autonomous daemon shut down cleanly.")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Atlas Trading Agent — Autonomous 24/7 Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python autonomous.py                        # paper mode (safe default)\n"
            "  python autonomous.py --live --confirm-live  # live trading (requires both flags)\n"
        ),
    )
    parser.add_argument(
        "--live",
        action="store_true",
        default=False,
        help="Enable live trading mode (also requires --confirm-live).",
    )
    parser.add_argument(
        "--confirm-live",
        action="store_true",
        default=False,
        dest="confirm_live",
        help="Second confirmation for live mode. Required alongside --live.",
    )
    args = parser.parse_args()

    # Windows requires the Selector event loop policy for compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run(live=args.live, confirm_live=args.confirm_live))


if __name__ == "__main__":
    main()
