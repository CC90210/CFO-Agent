"""
start_daemon.py — Launch the ATLAS trading daemon as a detached Windows process.

Usage:
    python start_daemon.py          # Start daemon
    python start_daemon.py stop     # Stop daemon
    python start_daemon.py status   # Check daemon status

Safety: Kills ALL existing trading processes before starting a new one.
This prevents the multi-daemon problem that caused order spam.
"""
import subprocess
import sys
import os
from pathlib import Path

PID_FILE = Path(__file__).parent / "data" / "daemon.pid"
LOG_FILE = Path(__file__).parent / "logs" / "daemon.log"

# Command signature we search for when killing existing daemons
_DAEMON_CMD_SIGNATURE = "main.py live"


def _find_trading_pids() -> list[int]:
    """Find all Python processes running the trading daemon."""
    try:
        result = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get",
             "ProcessId,CommandLine", "/FORMAT:CSV"],
            capture_output=True, text=True, timeout=10,
        )
        pids = []
        my_pid = os.getpid()
        for line in result.stdout.splitlines():
            if _DAEMON_CMD_SIGNATURE in line:
                # CSV format: Node,CommandLine,ProcessId
                parts = line.strip().rstrip(",").split(",")
                try:
                    pid = int(parts[-1].strip())
                    if pid != my_pid:
                        pids.append(pid)
                except (ValueError, IndexError):
                    continue
        return pids
    except Exception as exc:
        print(f"Warning: Could not enumerate processes: {exc}")
        return []


def _kill_all_existing():
    """Kill ALL running trading daemons — nuclear cleanup."""
    pids = _find_trading_pids()
    if not pids:
        return 0
    print(f"Found {len(pids)} existing daemon process(es). Killing...")
    killed = 0
    for pid in pids:
        try:
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True, timeout=5,
            )
            killed += 1
        except Exception:
            pass
    print(f"Killed {killed}/{len(pids)} processes.")
    return killed


def start():
    """Launch the trading daemon as a detached process."""
    # ALWAYS kill existing daemons first — this is the #1 bug prevention
    _kill_all_existing()

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
    """Stop ALL running daemon processes."""
    killed = _kill_all_existing()
    PID_FILE.unlink(missing_ok=True)
    if killed:
        print(f"Stopped {killed} daemon process(es).")
    else:
        print("No daemon processes found.")


def status():
    """Check daemon status."""
    pids = _find_trading_pids()
    if pids:
        print(f"Daemon RUNNING — {len(pids)} process(es): {pids}")
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            print(f"Log ({len(lines)} lines):")
            for line in lines[-5:]:
                print(f"  {line}")
    else:
        print("No daemon processes running.")
        PID_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    {"start": start, "stop": stop, "status": status}.get(cmd, start)()
