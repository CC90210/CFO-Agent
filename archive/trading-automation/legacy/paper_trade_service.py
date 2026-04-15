"""
paper_trade_service.py — Persistent Paper Trading Daemon
=========================================================
Launches paper_trade.py as a fully detached, self-restarting process
that survives terminal/IDE session closures.

Usage:
    python paper_trade_service.py start     # Launch detached daemon
    python paper_trade_service.py stop      # Kill running daemon
    python paper_trade_service.py status    # Check if running
    python paper_trade_service.py restart   # Stop then start

The daemon writes its PID to logs/paper_trade.pid for tracking.
Watchdog auto-restarts paper_trade.py if it crashes (30s cooldown).
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_PID_FILE = _ROOT / "logs" / "paper_trade.pid"
_LOG_FILE = _ROOT / "logs" / "paper_trade_live.log"
_WATCHDOG_LOG = _ROOT / "logs" / "watchdog.log"
_PYTHON = sys.executable


def _log(msg: str) -> None:
    """Append a timestamped line to the watchdog log."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="")
    with open(_WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def _is_pid_alive(pid: int) -> bool:
    """Check if a process with the given PID is running (Windows-compatible)."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, timeout=5,
            creationflags=0x08000000,
        )
        return str(pid) in result.stdout
    except Exception:
        return False


def _read_pid() -> int | None:
    """Read the PID from the pid file, return None if missing/stale."""
    if not _PID_FILE.exists():
        return None
    try:
        pid = int(_PID_FILE.read_text().strip())
        if _is_pid_alive(pid):
            return pid
        _PID_FILE.unlink(missing_ok=True)
        return None
    except (ValueError, OSError):
        _PID_FILE.unlink(missing_ok=True)
        return None


def _write_pid(pid: int) -> None:
    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PID_FILE.write_text(str(pid))


def _is_running() -> bool:
    return _read_pid() is not None


def cmd_status() -> None:
    pid = _read_pid()
    if pid:
        print(f"Atlas paper trading is RUNNING (PID {pid})")
    else:
        print("Atlas paper trading is NOT running")


def _kill_process_tree(pid: int) -> None:
    """Kill a process and all its children on Windows."""
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True, timeout=10,
        creationflags=0x08000000,
    )


def cmd_stop() -> None:
    pid = _read_pid()
    if pid is None:
        print("No running paper trading process found.")
        return
    _kill_process_tree(pid)
    # Wait for process to die
    for _ in range(10):
        if not _is_pid_alive(pid):
            break
        time.sleep(1)
    _PID_FILE.unlink(missing_ok=True)
    _log(f"Stopped paper trading (PID {pid})")
    print(f"Stopped paper trading (PID {pid})")


def cmd_start() -> None:
    if _is_running():
        pid = _read_pid()
        print(f"Paper trading already running (PID {pid}). Use 'restart' to restart.")
        return

    _log("Starting Atlas paper trading daemon...")

    # Launch the watchdog wrapper as a fully detached process
    # On Windows, DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP ensures
    # the process survives parent terminal closure.
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    DETACHED_PROCESS = 0x00000008
    CREATE_NO_WINDOW = 0x08000000

    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # The watchdog script runs paper_trade.py in a loop
    watchdog_script = str(_ROOT / "_watchdog_runner.py")

    # Write the inline watchdog runner
    runner_code = f'''
import subprocess, sys, time, os, signal
from pathlib import Path

ROOT = Path(r"{_ROOT}")
PYTHON = r"{_PYTHON}"
LOG = ROOT / "logs" / "paper_trade_live.log"
WATCHDOG_LOG = ROOT / "logs" / "watchdog.log"
PID_FILE = ROOT / "logs" / "paper_trade.pid"
COOLDOWN = 30
MAX_RAPID_RESTARTS = 5
RAPID_WINDOW = 300  # 5 minutes

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{{ts}}] {{msg}}\\n"
    with open(WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(line)

# Write our own PID so the service can track us
PID_FILE.write_text(str(os.getpid()))

restart_times = []
running = True

def handle_term(signum, frame):
    global running
    running = False
    log("Watchdog received SIGTERM, shutting down.")

signal.signal(signal.SIGTERM, handle_term)

log("Watchdog started (PID " + str(os.getpid()) + ")")

while running:
    # Track rapid restarts
    now = time.time()
    restart_times = [t for t in restart_times if now - t < RAPID_WINDOW]
    if len(restart_times) >= MAX_RAPID_RESTARTS:
        log(f"CIRCUIT BREAKER: {{MAX_RAPID_RESTARTS}} restarts in {{RAPID_WINDOW}}s. Sleeping 5 min.")
        time.sleep(300)
        restart_times.clear()
        continue

    restart_times.append(now)
    log("Launching paper_trade.py...")

    with open(LOG, "a", encoding="utf-8") as logf:
        proc = subprocess.Popen(
            [PYTHON, str(ROOT / "paper_trade.py")],
            cwd=str(ROOT),
            stdout=logf,
            stderr=logf,
            creationflags=0x08000000,
        )

    log(f"paper_trade.py started (PID {{proc.pid}})")

    # Wait for it to exit
    while running:
        ret = proc.poll()
        if ret is not None:
            log(f"paper_trade.py exited with code {{ret}}")
            break
        time.sleep(5)

    if not running:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except:
            proc.kill()
        break

    log(f"Restarting in {{COOLDOWN}}s...")
    time.sleep(COOLDOWN)

PID_FILE.unlink(missing_ok=True)
log("Watchdog exited cleanly.")
'''

    runner_path = _ROOT / "_watchdog_runner.py"
    runner_path.write_text(runner_code, encoding="utf-8")

    # Launch fully detached
    creation_flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    proc = subprocess.Popen(
        [_PYTHON, str(runner_path)],
        cwd=str(_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )

    # Give it a moment to write its PID
    time.sleep(2)

    pid = _read_pid()
    if pid:
        _log(f"Daemon started successfully (PID {pid})")
        print(f"Atlas paper trading daemon started (PID {pid})")
        print(f"  Log: {_LOG_FILE}")
        print(f"  Watchdog log: {_WATCHDOG_LOG}")
        print(f"  PID file: {_PID_FILE}")
        print(f"  Auto-restarts on crash (30s cooldown, circuit breaker at 5 rapid restarts)")
    else:
        # Fallback: use the Popen PID
        _write_pid(proc.pid)
        _log(f"Daemon started (PID {proc.pid})")
        print(f"Atlas paper trading daemon started (PID {proc.pid})")


def cmd_restart() -> None:
    cmd_stop()
    time.sleep(2)
    cmd_start()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python paper_trade_service.py {start|stop|status|restart}")
        sys.exit(1)

    command = sys.argv[1].lower()
    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "restart": cmd_restart,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print("Usage: python paper_trade_service.py {start|stop|status|restart}")
        sys.exit(1)

    commands[command]()


if __name__ == "__main__":
    main()
