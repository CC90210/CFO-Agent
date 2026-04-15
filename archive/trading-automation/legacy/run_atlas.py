"""
run_atlas.py
------------
Atlas Trading Agent — Combined Launcher.

Starts BOTH the autonomous trading daemon AND the Telegram bridge in a
single process, sharing one asyncio event loop. This is the canonical
"one command to start everything" entry point.

Usage
-----
  python run_atlas.py                        # paper mode (default, safe)
  python run_atlas.py --live --confirm-live  # live trading (double gate)

The autonomous daemon and Telegram bridge share a single shutdown_event.
When either signals shutdown (SIGINT, SIGTERM, or /kill from Telegram),
both components stop cleanly.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
#  Path setup
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_LOG_DIR = _ROOT / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Logging — configure before project imports
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_LOG_DIR / "atlas.log"),
    ],
)
logger = logging.getLogger("atlas.launcher")

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports
# ─────────────────────────────────────────────────────────────────────────────

from config.settings import settings  # noqa: E402
from db.database import health_check, init_db  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
#  Banner
# ─────────────────────────────────────────────────────────────────────────────

_ATLAS_VERSION = "0.1.0"


def _get_strategy_count() -> int:
    """Return the number of enabled strategies from config."""
    try:
        import yaml

        cfg_path = _ROOT / "config" / "strategies.yaml"
        if not cfg_path.exists():
            return 0
        with open(cfg_path) as fh:
            raw = yaml.safe_load(fh) or {}
        return sum(1 for v in raw.get("strategies", {}).values() if v.get("enabled", True))
    except Exception:  # noqa: BLE001
        return 0


def _print_banner(
    mode: str,
    exchange: str,
    strategies: int,
    telegram_ok: bool,
) -> None:
    """Print the Atlas startup banner."""
    tg_str = "Connected" if telegram_ok else "No token"
    width = 62
    inner = width - 2

    def row(content: str) -> str:
        return f"║  {content.ljust(inner - 2)}  ║"

    lines = [
        f"╔{'═' * width}╗",
        row(f"ATLAS TRADING AGENT v{_ATLAS_VERSION}"),
        row(f"Mode: {mode}  |  Exchange: {exchange}  |  Strategies: {strategies}"),
        row(f"Telegram: {tg_str}  |  Heartbeat: 5min"),
        row('"Protect capital first. Compound gains second."'),
        f"╚{'═' * width}╝",
    ]
    for line in lines:
        print(line)
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  Combined launcher
# ─────────────────────────────────────────────────────────────────────────────


async def run(live: bool = False, confirm_live: bool = False) -> None:
    """
    Start the autonomous daemon and Telegram bridge in the same asyncio
    event loop, sharing a single shutdown_event.

    Parameters
    ----------
    live:
        Enable live trading mode.
    confirm_live:
        Second confirmation required for live mode.
    """

    # 1. Live mode double-gate
    if live and not confirm_live:
        logger.error(
            "Live mode requires --confirm-live as a second confirmation. "
            "Pass both --live and --confirm-live."
        )
        sys.exit(1)

    # 2. Database init
    logger.info("Initialising database...")
    try:
        init_db()
    except Exception as exc:  # noqa: BLE001
        logger.error("Database init failed: %s", exc)
        sys.exit(1)

    if not health_check():
        logger.error("Database health check failed. Aborting.")
        sys.exit(1)

    # 3. Banner info
    mode_label = "LIVE" if (live and confirm_live) else "PAPER"
    exchange_label = settings.exchange.default_exchange.upper()
    strategy_count = _get_strategy_count()
    telegram_ok = bool(settings.telegram.telegram_bot_token)

    _print_banner(mode_label, exchange_label, strategy_count, telegram_ok)

    # 4. Shared shutdown event
    shutdown_event = asyncio.Event()

    def _handle_signal(signum: int, frame: object) -> None:
        logger.info("Signal %d received — shutting down Atlas.", signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # 5. Import and build component coroutines
    from autonomous import run as autonomous_run  # noqa: PLC0415
    from telegram_bridge import TelegramBridge  # noqa: PLC0415

    # Build the Telegram bridge (may raise if token is missing)
    bridge: TelegramBridge | None = None
    bridge_task: asyncio.Task[None] | None = None
    if telegram_ok:
        try:
            bridge = TelegramBridge(shutdown_event=shutdown_event)
        except RuntimeError as exc:
            logger.warning("Telegram bridge disabled: %s", exc)

    # 6. Start tasks
    autonomous_task = asyncio.create_task(
        autonomous_run(live=live, confirm_live=confirm_live),
        name="autonomous-daemon",
    )

    if bridge is not None:
        bridge_task = asyncio.create_task(bridge.run(), name="telegram-bridge")
        logger.info("Telegram bridge started.")
    else:
        logger.warning(
            "Telegram bridge not started — set TELEGRAM_BOT_TOKEN in .env to enable."
        )

    logger.info("Atlas is running. Press Ctrl+C to stop.")

    # 7. Wait for shutdown
    await shutdown_event.wait()
    logger.info("Shutdown requested — stopping all components...")

    # 8. Cancel tasks
    tasks_to_cancel: list[asyncio.Task[None]] = [autonomous_task]
    if bridge_task is not None:
        tasks_to_cancel.append(bridge_task)

    for task in tasks_to_cancel:
        task.cancel()

    results = await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
    for task, result in zip(tasks_to_cancel, results):
        if isinstance(result, Exception) and not isinstance(
            result, asyncio.CancelledError
        ):
            logger.error(
                "Component '%s' raised during shutdown: %s", task.get_name(), result
            )

    logger.info("Atlas stopped cleanly.")


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Atlas Trading Agent — Combined Launcher (autonomous + Telegram)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python run_atlas.py                        # paper mode (safe default)\n"
            "  python run_atlas.py --live --confirm-live  # live trading\n"
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
        help="Second confirmation for live mode.",
    )
    args = parser.parse_args()

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run(live=args.live, confirm_live=args.confirm_live))


if __name__ == "__main__":
    main()
