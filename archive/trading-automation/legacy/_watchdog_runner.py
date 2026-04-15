
import subprocess, sys, time, os, signal
from pathlib import Path

ROOT = Path(r"C:\Users\User\APPS\trading-agent")
PYTHON = r"C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe"
LOG = ROOT / "logs" / "paper_trade_live.log"
WATCHDOG_LOG = ROOT / "logs" / "watchdog.log"
PID_FILE = ROOT / "logs" / "paper_trade.pid"
COOLDOWN = 30
MAX_RAPID_RESTARTS = 5
RAPID_WINDOW = 300  # 5 minutes

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
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
        log(f"CIRCUIT BREAKER: {MAX_RAPID_RESTARTS} restarts in {RAPID_WINDOW}s. Sleeping 5 min.")
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
        )

    log(f"paper_trade.py started (PID {proc.pid})")

    # Wait for it to exit
    while running:
        ret = proc.poll()
        if ret is not None:
            log(f"paper_trade.py exited with code {ret}")
            break
        time.sleep(5)

    if not running:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except:
            proc.kill()
        break

    log(f"Restarting in {COOLDOWN}s...")
    time.sleep(COOLDOWN)

PID_FILE.unlink(missing_ok=True)
log("Watchdog exited cleanly.")
