"""
start_daemon.py — Launch the ATLAS trading daemon as a detached Windows process.

Usage:
    python start_daemon.py          # Start daemon
    python start_daemon.py stop     # Stop daemon
    python start_daemon.py status   # Check daemon status
"""
import subprocess
import sys
import os
import signal
from pathlib import Path

PID_FILE = Path(__file__).parent / "data" / "daemon.pid"
LOG_FILE = Path(__file__).parent / "logs" / "daemon.log"


def start():
    """Launch the trading daemon as a detached process."""
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)  # Check if process is alive
            print(f"Daemon already running (PID {pid}). Use 'stop' first.")
            return
        except OSError:
            PID_FILE.unlink()  # Stale PID file

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # PYTHONUNBUFFERED ensures log output isn't delayed
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    log_fh = open(LOG_FILE, "a")
    proc = subprocess.Popen(
        [sys.executable, "-u", "main.py", "live", "--strategy", "all",
         "--exchange", "kraken", "--confirm-live"],
        stdin=subprocess.DEVNULL,
        stdout=log_fh,
        stderr=log_fh,
        creationflags=0x00000008 | 0x00000200,  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    )

    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(proc.pid))
    print(f"ATLAS daemon started (PID {proc.pid})")
    print(f"Log: {LOG_FILE}")
    print(f"PID file: {PID_FILE}")


def stop():
    """Stop the running daemon."""
    if not PID_FILE.exists():
        print("No daemon PID file found.")
        return

    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Daemon (PID {pid}) stopped.")
    except OSError:
        print(f"Daemon (PID {pid}) was not running.")
    finally:
        PID_FILE.unlink(missing_ok=True)


def _is_pid_alive(pid: int) -> bool:
    """Check if a process is running — works reliably on Windows detached processes."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, timeout=5,
        )
        return str(pid) in result.stdout
    except Exception:
        # Fallback to os.kill
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def status():
    """Check daemon status."""
    if not PID_FILE.exists():
        print("No daemon PID file found.")
        return

    pid = int(PID_FILE.read_text().strip())
    if _is_pid_alive(pid):
        print(f"Daemon RUNNING (PID {pid})")
        # Show last 5 lines of log
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            print(f"Log ({len(lines)} lines):")
            for line in lines[-5:]:
                print(f"  {line}")
    else:
        print(f"Daemon DEAD (stale PID {pid})")
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    {"start": start, "stop": stop, "status": status}.get(cmd, start)()
