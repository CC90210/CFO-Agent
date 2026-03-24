"""
live_trade_service.py — Persistent Live Trading Daemon
=======================================================
Launches live_trade.py as a fully detached, self-restarting process
that survives terminal/IDE session closures.

Also installs a Windows Task Scheduler task so the daemon
auto-starts when the computer boots up.

Usage:
    python live_trade_service.py start      # Launch detached daemon
    python live_trade_service.py stop       # Kill running daemon
    python live_trade_service.py status     # Check if running
    python live_trade_service.py restart    # Stop then start
    python live_trade_service.py install    # Add Windows startup task
    python live_trade_service.py uninstall  # Remove Windows startup task
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_PID_FILE = _ROOT / "logs" / "live_trade.pid"
_LOG_FILE = _ROOT / "logs" / "live_trade_output.log"
_WATCHDOG_LOG = _ROOT / "logs" / "live_watchdog.log"
_PYTHON = sys.executable
_TASK_NAME = "AtlasLiveTrading"


def _log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="")
    _WATCHDOG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(_WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(line)


def _is_pid_alive(pid: int) -> bool:
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, timeout=5,
        )
        return str(pid) in result.stdout
    except Exception:
        return False


def _read_pid() -> int | None:
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
        print(f"Atlas LIVE trading is RUNNING (PID {pid})")
    else:
        print("Atlas LIVE trading is NOT running")


def _kill_process_tree(pid: int) -> None:
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True, timeout=10,
    )


def cmd_stop() -> None:
    pid = _read_pid()
    if pid is None:
        print("No running live trading process found.")
        return
    _kill_process_tree(pid)
    for _ in range(10):
        if not _is_pid_alive(pid):
            break
        time.sleep(1)
    _PID_FILE.unlink(missing_ok=True)
    _log(f"Stopped live trading (PID {pid})")
    print(f"Stopped live trading (PID {pid})")


def cmd_start() -> None:
    if _is_running():
        pid = _read_pid()
        print(f"Live trading already running (PID {pid}). Use 'restart' to restart.")
        return

    _log("Starting Atlas LIVE trading daemon...")

    CREATE_NEW_PROCESS_GROUP = 0x00000200
    DETACHED_PROCESS = 0x00000008

    _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    runner_code = f'''
import subprocess, sys, time, os, signal
from pathlib import Path

ROOT = Path(r"{_ROOT}")
PYTHON = r"{_PYTHON}"
LOG = ROOT / "logs" / "live_trade_output.log"
WATCHDOG_LOG = ROOT / "logs" / "live_watchdog.log"
PID_FILE = ROOT / "logs" / "live_trade.pid"
COOLDOWN = 30
MAX_RAPID_RESTARTS = 5
RAPID_WINDOW = 300

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{{ts}}] {{msg}}\\n"
    with open(WATCHDOG_LOG, "a", encoding="utf-8") as f:
        f.write(line)

PID_FILE.write_text(str(os.getpid()))

restart_times = []
running = True

def handle_term(signum, frame):
    global running
    running = False
    log("Live watchdog received SIGTERM, shutting down.")

signal.signal(signal.SIGTERM, handle_term)

log("Live trading watchdog started (PID " + str(os.getpid()) + ")")

while running:
    now = time.time()
    restart_times = [t for t in restart_times if now - t < RAPID_WINDOW]
    if len(restart_times) >= MAX_RAPID_RESTARTS:
        log(f"CIRCUIT BREAKER: {{MAX_RAPID_RESTARTS}} restarts in {{RAPID_WINDOW}}s. Sleeping 5 min.")
        time.sleep(300)
        restart_times.clear()
        continue

    restart_times.append(now)
    log("Launching live_trade.py...")

    with open(LOG, "a", encoding="utf-8") as logf:
        proc = subprocess.Popen(
            [PYTHON, str(ROOT / "live_trade.py")],
            cwd=str(ROOT),
            stdout=logf,
            stderr=logf,
        )

    log(f"live_trade.py started (PID {{proc.pid}})")

    while running:
        ret = proc.poll()
        if ret is not None:
            log(f"live_trade.py exited with code {{ret}}")
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
log("Live watchdog exited cleanly.")
'''

    runner_path = _ROOT / "_live_watchdog_runner.py"
    runner_path.write_text(runner_code, encoding="utf-8")

    creation_flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        [_PYTHON, str(runner_path)],
        cwd=str(_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )

    time.sleep(2)

    pid = _read_pid()
    if pid:
        _log(f"Live daemon started successfully (PID {pid})")
        print(f"Atlas LIVE trading daemon started (PID {pid})")
        print(f"  Log: {_LOG_FILE}")
        print(f"  Watchdog log: {_WATCHDOG_LOG}")
        print(f"  PID file: {_PID_FILE}")
        print(f"  Auto-restarts on crash (30s cooldown, circuit breaker at 5 rapid restarts)")
    else:
        _write_pid(proc.pid)
        _log(f"Live daemon started (PID {proc.pid})")
        print(f"Atlas LIVE trading daemon started (PID {proc.pid})")


def cmd_restart() -> None:
    cmd_stop()
    time.sleep(2)
    cmd_start()


def cmd_install() -> None:
    """Install a Windows Task Scheduler task to auto-start on login."""
    script_path = _ROOT / "live_trade_service.py"
    cmd = (
        f'schtasks /Create /TN "{_TASK_NAME}" /TR '
        f'"\"{_PYTHON}\" \"{script_path}\" start" '
        f'/SC ONLOGON /RL HIGHEST /F'
    )

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Windows startup task '{_TASK_NAME}' installed successfully.")
        print("Atlas will auto-start live trading when you log in to Windows.")
    else:
        print(f"Failed to install startup task: {result.stderr}")
        print("Try running as administrator, or manually add to Task Scheduler.")


def cmd_uninstall() -> None:
    """Remove the Windows Task Scheduler task."""
    cmd = f'schtasks /Delete /TN "{_TASK_NAME}" /F'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Windows startup task '{_TASK_NAME}' removed.")
    else:
        print(f"Task not found or could not be removed: {result.stderr}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python live_trade_service.py {start|stop|status|restart|install|uninstall}")
        sys.exit(1)

    command = sys.argv[1].lower()
    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "restart": cmd_restart,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
    }

    if command not in commands:
        print(f"Unknown command: {command}")
        print("Usage: python live_trade_service.py {start|stop|status|restart|install|uninstall}")
        sys.exit(1)

    commands[command]()


if __name__ == "__main__":
    main()
