"""
watchdog.py — Daemon supervisor for Atlas Trading Agent.

Keeps the trading daemon alive by:
1. Monitoring the daemon process
2. Auto-restarting if it crashes
3. Preventing Windows sleep via periodic mouse jiggle (optional)

Usage:
    python watchdog.py
    python watchdog.py --no-keep-awake   # Skip sleep prevention
"""

import subprocess
import sys
import time
import logging
import signal
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | watchdog — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("watchdog")

DAEMON_CMD = [
    sys.executable, "main.py", "live",
    "--strategy", "all",
    "--exchange", "kraken",
    "--confirm-live",
]
RESTART_DELAY = 10  # seconds between restarts
MAX_RESTARTS = 100  # max restarts before giving up
HEALTH_CHECK_INTERVAL = 60  # seconds between health checks

_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    logger.info("Shutdown signal received (sig=%d). Stopping daemon...", signum)
    _shutdown = True


def keep_awake():
    """Prevent Windows from sleeping by calling SetThreadExecutionState."""
    try:
        import ctypes
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        logger.info("Windows sleep prevention ACTIVE (SetThreadExecutionState)")
        return True
    except Exception as exc:
        logger.warning("Could not set keep-awake: %s", exc)
        return False


def main():
    global _shutdown
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    no_keep_awake = "--no-keep-awake" in sys.argv
    if not no_keep_awake:
        keep_awake()

    restart_count = 0
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"  # Force immediate log flush to daemon log files

    while not _shutdown and restart_count < MAX_RESTARTS:
        log_file = f"logs/daemon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger.info("Starting daemon (restart #%d) → %s", restart_count, log_file)

        with open(log_file, "w", buffering=1) as lf:  # Line-buffered for immediate log visibility
            proc = subprocess.Popen(
                DAEMON_CMD,
                stdout=lf,
                stderr=subprocess.STDOUT,
                env=env,
            )
            logger.info("Daemon PID: %d", proc.pid)

            # Monitor the process
            while not _shutdown:
                retcode = proc.poll()
                if retcode is not None:
                    logger.warning("Daemon exited with code %d", retcode)
                    break
                # Refresh keep-awake every health check
                if not no_keep_awake:
                    keep_awake()
                time.sleep(HEALTH_CHECK_INTERVAL)

            if _shutdown:
                logger.info("Shutting down daemon PID %d...", proc.pid)
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                break

        restart_count += 1
        if restart_count < MAX_RESTARTS:
            logger.info("Restarting in %d seconds...", RESTART_DELAY)
            time.sleep(RESTART_DELAY)

    if restart_count >= MAX_RESTARTS:
        logger.error("Max restarts (%d) reached. Giving up.", MAX_RESTARTS)
    logger.info("Watchdog exiting.")


if __name__ == "__main__":
    main()
