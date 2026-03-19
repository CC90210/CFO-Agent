"""
scripts/healthcheck.py
----------------------
External liveness probe for the Atlas autonomous trading agent.

Used as the Docker HEALTHCHECK command and for any external monitoring
system (cron, systemd watchdog, uptime robot webhook, etc.).

Exit codes
----------
  0  — agent is alive: watchdog heartbeat is fresh AND DB is responsive
  1  — agent is dead or unhealthy (stale heartbeat OR DB unreachable)

Staleness threshold: 5 minutes (300 seconds).

Usage
-----
  python scripts/healthcheck.py            # check and print status
  python scripts/healthcheck.py --quiet    # check silently (exit code only)

Docker HEALTHCHECK example
--------------------------
  HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
      CMD python scripts/healthcheck.py --quiet
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

# ── Path bootstrap — must happen before project imports ──────────────────────

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Constants ────────────────────────────────────────────────────────────────

_HEARTBEAT_FILE = _ROOT / "logs" / "watchdog.heartbeat"
_STALE_THRESHOLD_SECONDS: float = 5 * 60.0  # 5 minutes


# ── Checks ───────────────────────────────────────────────────────────────────


def check_heartbeat() -> tuple[bool, str]:
    """
    Return (ok, reason).  ok=True if the heartbeat file exists and was
    written within the last 5 minutes.
    """
    if not _HEARTBEAT_FILE.exists():
        return False, f"Heartbeat file missing: {_HEARTBEAT_FILE}"

    try:
        raw = _HEARTBEAT_FILE.read_text(encoding="utf-8").strip()
        written_at = datetime.datetime.fromisoformat(raw)
    except (OSError, ValueError) as exc:
        return False, f"Heartbeat file unreadable: {exc}"

    # Ensure timezone-aware comparison
    now = datetime.datetime.now(datetime.UTC)
    if written_at.tzinfo is None:
        written_at = written_at.replace(tzinfo=datetime.UTC)

    age_seconds = (now - written_at).total_seconds()

    if age_seconds > _STALE_THRESHOLD_SECONDS:
        return False, (
            f"Heartbeat is stale: last written {age_seconds:.0f}s ago "
            f"(threshold={_STALE_THRESHOLD_SECONDS:.0f}s)"
        )

    return True, f"Heartbeat fresh: last written {age_seconds:.0f}s ago"


def check_database() -> tuple[bool, str]:
    """
    Return (ok, reason).  ok=True if the DB responds to a trivial query.
    """
    try:
        from db.database import health_check  # noqa: PLC0415

        ok = health_check()
        if ok:
            return True, "Database: responsive"
        return False, "Database health check returned False"
    except Exception as exc:  # noqa: BLE001
        return False, f"Database check raised: {exc}"


# ── CLI entry point ──────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Atlas agent liveness probe — exits 0 if healthy, 1 if not.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output; return exit code only.",
    )
    args = parser.parse_args()

    hb_ok, hb_reason = check_heartbeat()
    db_ok, db_reason = check_database()

    healthy = hb_ok and db_ok

    if not args.quiet:
        status = "HEALTHY" if healthy else "UNHEALTHY"
        print(f"[healthcheck] Status: {status}")
        print(f"[healthcheck] {hb_reason}")
        print(f"[healthcheck] {db_reason}")

    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
