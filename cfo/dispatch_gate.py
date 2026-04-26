"""
cfo/dispatch_gate.py
--------------------
Single chokepoint for every irreversible / high-impact outbound action
Atlas can take. Wraps:

  * tax-filing submissions (CRA NETFILE / GST ELS) — DRY-RUN ONLY today;
    the gate exists so a real submission cannot be wired in by accident.
  * cfo_pulse.json writes — schema-validated before write.
  * Telegram outbound alerts — rate-limited, deduplicated, killswitchable.
  * Email reports to CC — same rate limit + killswitch.

Killswitch
----------
Setting environment variable ``ATLAS_FORCE_DRY_RUN=1`` short-circuits
EVERY outbound action through this gate. The function still returns a
structured result so callers can log/announce the suppression.

Why a chokepoint
----------------
Atlas is, by SOUL, a research+advice agent — never an auto-trader. But
it does send Telegram alerts, write the cfo_pulse contract that gates
Maven's spend, and could in principle file taxes. Each of those needs
exactly one place where rate-limits, validators, and killswitches live.
This is that place. Bypassing this module is a defect.

Usage
-----
    from cfo.dispatch_gate import dispatch, DispatchResult

    result = dispatch(
        action="telegram_alert",
        payload={"text": "Liquid below floor — $7,400 CAD"},
    )
    if not result.sent:
        log.warning("Suppressed: %s", result.reason)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

KILLSWITCH_ENV = "ATLAS_FORCE_DRY_RUN"

ALLOWED_ACTIONS = {
    "tax_filing",         # CRA NETFILE / GST ELS — always dry-run for now
    "pulse_write",        # cfo_pulse.json publish
    "telegram_alert",     # outbound Telegram message
    "email_report",       # email report to CC
}

# Rate limits per action per 24h
RATE_LIMITS_PER_DAY = {
    "tax_filing": 5,        # paranoid — CRA submission is irreversible
    "pulse_write": 200,     # publishing is cheap, but a runaway loop is loud
    "telegram_alert": 30,
    "email_report": 30,
}

# Dedup window — same payload not allowed twice within this many seconds
DEDUP_WINDOW_SECONDS = {
    "tax_filing": 24 * 3600,    # never duplicate a filing
    "pulse_write": 0,           # publishing is idempotent — no dedup
    "telegram_alert": 3600,     # 1h
    "email_report": 3600,
}

# Process-local state — a chokepoint that survives restarts uses on-disk
# state under data/dispatch/. In-memory state catches the same-process
# storm; on-disk state catches cron storms.
_STATE_DIR = Path(__file__).resolve().parents[1] / "data" / "dispatch"
_LOCK = threading.Lock()


# ─────────────────────────────────────────────────────────────────────────────
#  Result / errors
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DispatchResult:
    sent: bool
    action: str
    reason: str
    dry_run: bool
    payload_fingerprint: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    extra: dict[str, Any] = field(default_factory=dict)


class DispatchError(RuntimeError):
    """Raised for unrecoverable gate failures (validator failure, unknown action)."""


# ─────────────────────────────────────────────────────────────────────────────
#  State helpers — bounded JSON log per action
# ─────────────────────────────────────────────────────────────────────────────

def _state_path(action: str) -> Path:
    return _STATE_DIR / f"{action}.jsonl"


def _load_recent(action: str, since_seconds: int) -> list[dict]:
    path = _state_path(action)
    if not path.exists():
        return []
    cutoff = time.time() - since_seconds
    out: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("ts", 0) >= cutoff:
                out.append(rec)
    except OSError:
        return []
    return out


def _append_record(action: str, fingerprint: str, sent: bool, reason: str) -> None:
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": time.time(),
        "iso": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "fingerprint": fingerprint,
        "sent": sent,
        "reason": reason,
    }
    with _state_path(action).open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
#  Killswitch / rate-limit / dedup
# ─────────────────────────────────────────────────────────────────────────────

def killswitch_active() -> bool:
    return os.environ.get(KILLSWITCH_ENV, "").strip() in ("1", "true", "TRUE", "yes")


def _fingerprint(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _within_rate_limit(action: str) -> bool:
    cap = RATE_LIMITS_PER_DAY.get(action, 0)
    if cap <= 0:
        return False
    recent = _load_recent(action, since_seconds=24 * 3600)
    sent_count = sum(1 for r in recent if r.get("sent"))
    return sent_count < cap


def _is_duplicate(action: str, fingerprint: str) -> bool:
    window = DEDUP_WINDOW_SECONDS.get(action, 0)
    if window <= 0:
        return False
    recent = _load_recent(action, since_seconds=window)
    return any(r.get("fingerprint") == fingerprint and r.get("sent") for r in recent)


# ─────────────────────────────────────────────────────────────────────────────
#  Action handlers
# ─────────────────────────────────────────────────────────────────────────────

def _handle_pulse_write(payload: dict, dry_run: bool) -> tuple[bool, str, dict]:
    """Validate the payload via cfo.pulse_schema before allowing the write."""
    from cfo.pulse_schema import PulseSchemaError, validate_pulse

    try:
        validate_pulse(payload)
    except PulseSchemaError as exc:
        raise DispatchError(f"pulse_schema rejected the payload: {exc}") from exc

    if dry_run:
        return False, "dry_run — pulse not written", {"validated": True}

    # Production write delegated to cfo.pulse.publish() — the gate only
    # validates and accounts. The caller invokes publish() afterwards.
    return True, "validated; caller must invoke cfo.pulse.publish()", {"validated": True}


def _handle_tax_filing(payload: dict, dry_run: bool) -> tuple[bool, str, dict]:
    """
    Tax filing path is INTENTIONALLY dry-run only. CRA NETFILE / GST ELS
    transmissions require a separately-built submission module that
    Atlas does not have today. The gate exists so that, when that
    module lands, the only sanctioned path is through this function.
    """
    required = {"form", "tax_year", "summary"}
    missing = required - set(payload)
    if missing:
        raise DispatchError(f"tax_filing payload missing fields: {sorted(missing)}")

    return False, "tax_filing is dry-run only — no transmission wired", {
        "form": payload.get("form"),
        "tax_year": payload.get("tax_year"),
    }


def _handle_telegram_alert(payload: dict, dry_run: bool) -> tuple[bool, str, dict]:
    if "text" not in payload:
        raise DispatchError("telegram_alert payload requires `text`")
    if dry_run:
        return False, "dry_run — telegram not sent", {"chars": len(payload["text"])}

    # The actual send is handled by the caller via utils.alerts; the gate
    # returns sent=True to authorise the send.
    return True, "authorised", {"chars": len(payload["text"])}


def _handle_email_report(payload: dict, dry_run: bool) -> tuple[bool, str, dict]:
    if "subject" not in payload or "body" not in payload:
        raise DispatchError("email_report payload requires `subject` and `body`")
    if dry_run:
        return False, "dry_run — email not sent", {"subject": payload["subject"]}
    return True, "authorised", {"subject": payload["subject"]}


_HANDLERS: dict[str, Callable[[dict, bool], tuple[bool, str, dict]]] = {
    "tax_filing": _handle_tax_filing,
    "pulse_write": _handle_pulse_write,
    "telegram_alert": _handle_telegram_alert,
    "email_report": _handle_email_report,
}


# ─────────────────────────────────────────────────────────────────────────────
#  Public entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def dispatch(
    action: str,
    payload: dict,
    dry_run: bool = False,
) -> DispatchResult:
    """
    Single chokepoint for every irreversible / high-impact outbound.

    Returns a DispatchResult. Never raises for rate-limit / dedup /
    killswitch — those are SUPPRESSIONS, returned with sent=False.
    Raises DispatchError for malformed payloads or unknown actions.
    """
    if action not in ALLOWED_ACTIONS:
        raise DispatchError(
            f"unknown action {action!r}; allowed: {sorted(ALLOWED_ACTIONS)}"
        )
    if not isinstance(payload, dict):
        raise DispatchError(f"payload must be a dict, got {type(payload).__name__}")

    fp = _fingerprint(payload)
    effective_dry_run = dry_run or killswitch_active()

    with _LOCK:
        if killswitch_active():
            _append_record(action, fp, sent=False, reason="killswitch_active")
            return DispatchResult(
                sent=False, action=action, reason="killswitch_active",
                dry_run=True, payload_fingerprint=fp,
            )

        if _is_duplicate(action, fp):
            _append_record(action, fp, sent=False, reason="duplicate_within_window")
            return DispatchResult(
                sent=False, action=action, reason="duplicate_within_window",
                dry_run=effective_dry_run, payload_fingerprint=fp,
            )

        if not _within_rate_limit(action):
            _append_record(action, fp, sent=False, reason="rate_limit_exceeded")
            return DispatchResult(
                sent=False, action=action, reason="rate_limit_exceeded",
                dry_run=effective_dry_run, payload_fingerprint=fp,
            )

        # Hand to action-specific handler
        sent, reason, extra = _HANDLERS[action](payload, effective_dry_run)
        _append_record(action, fp, sent=sent, reason=reason)
        return DispatchResult(
            sent=sent, action=action, reason=reason,
            dry_run=effective_dry_run, payload_fingerprint=fp, extra=extra,
        )


# ─────────────────────────────────────────────────────────────────────────────
#  CLI / debug
# ─────────────────────────────────────────────────────────────────────────────

def _summary() -> dict:
    """Return last-24h dispatch counts per action."""
    out: dict[str, dict] = {}
    for act in ALLOWED_ACTIONS:
        recent = _load_recent(act, since_seconds=24 * 3600)
        sent = sum(1 for r in recent if r.get("sent"))
        suppressed = sum(1 for r in recent if not r.get("sent"))
        out[act] = {"sent_24h": sent, "suppressed_24h": suppressed,
                    "cap_24h": RATE_LIMITS_PER_DAY[act]}
    return out


if __name__ == "__main__":
    import argparse
    import sys

    ap = argparse.ArgumentParser(prog="cfo.dispatch_gate")
    ap.add_argument("--summary", action="store_true",
                    help="Print last-24h dispatch counts per action")
    ap.add_argument("--killswitch", action="store_true",
                    help="Print whether killswitch is currently active")
    args = ap.parse_args()

    if args.killswitch:
        print(f"killswitch_active: {killswitch_active()}")
        sys.exit(0)
    if args.summary:
        print(json.dumps(_summary(), indent=2))
        sys.exit(0)

    ap.print_help()
