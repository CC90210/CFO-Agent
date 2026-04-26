"""
cfo/pulse_schema.py
-------------------
Validation contract for `data/pulse/cfo_pulse.json` — Atlas's hand-off
to Maven (CMO) and Bravo (CEO).

Every write to cfo_pulse.json AND every read of it should pass through
``validate_pulse`` so a schema regression is caught at the boundary, not
at the reader far downstream. Maven's paid-campaign spend gate reads
this contract directly; if any required field disappears or changes
type, Maven fails closed and CC's ad budget sits idle.

The full human-readable contract lives in `brain/CFO_PULSE_CONTRACT.md`.
This module is the machine-checkable version of the same.

Usage
-----
    from cfo.pulse_schema import validate_pulse, PulseSchemaError, is_stale

    try:
        validate_pulse(payload)
    except PulseSchemaError as exc:
        ...

    # Drop pulse if older than 24h
    if is_stale(payload, max_age_hours=24):
        ...

Design rule
-----------
The validator is intentionally hand-rolled (not jsonschema/pydantic) to
avoid a runtime dependency on packages that are not in requirements.txt
and to keep the failure messages short and actionable.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
#  Contract
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_AGENTS = {"atlas", "bravo", "maven", "aura"}
ALLOWED_SPEND_GATES = {"open", "tight", "frozen"}
ALLOWED_AD_RULES = {
    "frozen_gate",
    "experimentation_only",
    "15pct_mrr_cap_2k",
}

# Required for ANY pulse Atlas publishes
_REQUIRED_FIELDS: dict[str, type | tuple[type, ...]] = {
    "agent": str,
    "updated_at": str,
    "liquid_cad": (int, float),
    "liquid_source": str,
    "montreal_floor_target_cad": (int, float),
    "montreal_floor_gap_cad": (int, float),
    "tax_reserve_required_cad": (int, float),
    "tax_reserve_rate_pct": (int, float),
    "concentration_risk_single_client_pct": (int, float),
    "concentration_risk_client": str,
    "mrr_usd_from_bravo": (int, float),
    "mrr_cad_from_bravo": (int, float),
    # spend_gate is a nested object Maven's send_gateway reads directly.
    # See brain/CFO_PULSE_CONTRACT.md.
    "spend_gate": dict,
    "spend_gate_reason": str,
    "approved_ad_spend_monthly_cap_cad": (int, float),
    "approved_ad_spend_rule": str,
}

# Required keys WITHIN the nested spend_gate object
_SPEND_GATE_REQUIRED: dict[str, type | tuple[type, ...]] = {
    "status": str,
    "reason": str,
    "monthly_cap_cad": (int, float),
    "rule": str,
    "approvals": dict,
}

# Optional but typed when present — silent type coercion is the bug we're
# preventing, so check these too.
_OPTIONAL_FIELDS: dict[str, type | tuple[type, ...]] = {
    "schema_version": str,
    "bravo_pulse_age_days": (int, float, type(None)),
    "ytd_2026_receipts": (dict, type(None)),
    "integrations_live": dict,
    "maven_pulse_found": bool,
    "maven_pulse_age_days": (int, float, type(None)),
    "maven_pulse_source": (str, type(None)),
    "maven_current_spend_request_cad": (int, float),
    "maven_current_spend_approved": bool,
    "t2125_ad_deduction_note": str,
    "spend_gate_status": str,  # back-compat alias for spend_gate.status
}


class PulseSchemaError(ValueError):
    """Raised when a pulse payload violates the contract."""


# ─────────────────────────────────────────────────────────────────────────────
#  Validator
# ─────────────────────────────────────────────────────────────────────────────

def validate_pulse(payload: Any) -> None:
    """
    Validate a pulse payload in-place. Raises PulseSchemaError on the
    first violation; succeeds silently when all checks pass.

    Checks (in order):
      1. payload is a dict
      2. all required fields present and the right type
      3. typed-optional fields have correct type when present
      4. enum-style fields match the allowed set
      5. numeric fields are non-negative where required
      6. updated_at parses as ISO-8601
    """
    if not isinstance(payload, dict):
        raise PulseSchemaError(f"pulse must be a dict, got {type(payload).__name__}")

    # 1) required fields presence + type
    for field, expected in _REQUIRED_FIELDS.items():
        if field not in payload:
            raise PulseSchemaError(f"missing required field: {field}")
        value = payload[field]
        if not isinstance(value, expected):
            raise PulseSchemaError(
                f"field {field}: expected {expected}, got {type(value).__name__}"
            )

    # 2) optional fields type-checked when present
    for field, expected in _OPTIONAL_FIELDS.items():
        if field in payload:
            value = payload[field]
            if not isinstance(value, expected):
                raise PulseSchemaError(
                    f"field {field}: expected {expected}, got {type(value).__name__}"
                )

    # 3) enum-style values
    if payload["agent"] not in ALLOWED_AGENTS:
        raise PulseSchemaError(
            f"agent must be one of {sorted(ALLOWED_AGENTS)}, got {payload['agent']!r}"
        )

    # spend_gate must have all required nested keys with correct types
    sg = payload["spend_gate"]
    for sg_field, sg_expected in _SPEND_GATE_REQUIRED.items():
        if sg_field not in sg:
            raise PulseSchemaError(f"spend_gate missing required field: {sg_field}")
        if not isinstance(sg[sg_field], sg_expected):
            raise PulseSchemaError(
                f"spend_gate.{sg_field}: expected {sg_expected}, "
                f"got {type(sg[sg_field]).__name__}"
            )
    if sg["status"] not in ALLOWED_SPEND_GATES:
        raise PulseSchemaError(
            f"spend_gate.status must be one of {sorted(ALLOWED_SPEND_GATES)}, "
            f"got {sg['status']!r}"
        )
    if payload["approved_ad_spend_rule"] not in ALLOWED_AD_RULES:
        raise PulseSchemaError(
            f"approved_ad_spend_rule must be one of {sorted(ALLOWED_AD_RULES)}, "
            f"got {payload['approved_ad_spend_rule']!r}"
        )

    # 4) value sanity bands
    if payload["liquid_cad"] < 0:
        raise PulseSchemaError(f"liquid_cad must be >= 0, got {payload['liquid_cad']}")
    if payload["approved_ad_spend_monthly_cap_cad"] < 0:
        raise PulseSchemaError(
            "approved_ad_spend_monthly_cap_cad must be >= 0, "
            f"got {payload['approved_ad_spend_monthly_cap_cad']}"
        )
    pct = payload["concentration_risk_single_client_pct"]
    if not 0 <= pct <= 100:
        raise PulseSchemaError(
            f"concentration_risk_single_client_pct must be 0..100, got {pct}"
        )
    if payload["tax_reserve_rate_pct"] < 0 or payload["tax_reserve_rate_pct"] > 100:
        raise PulseSchemaError(
            f"tax_reserve_rate_pct must be 0..100, got {payload['tax_reserve_rate_pct']}"
        )

    # 5) updated_at parses
    try:
        datetime.fromisoformat(payload["updated_at"])
    except (TypeError, ValueError) as exc:
        raise PulseSchemaError(
            f"updated_at must be ISO 8601, got {payload['updated_at']!r}: {exc}"
        ) from exc

    # 6) cross-field invariant: gap = max(0, target - liquid)
    target = payload["montreal_floor_target_cad"]
    liquid = payload["liquid_cad"]
    expected_gap = max(0.0, target - liquid)
    actual_gap = payload["montreal_floor_gap_cad"]
    # 1 cent tolerance for float rounding
    if abs(expected_gap - actual_gap) > 0.01:
        raise PulseSchemaError(
            f"montreal_floor_gap_cad inconsistent: expected ~{expected_gap}, "
            f"got {actual_gap} (target={target}, liquid={liquid})"
        )


# ─────────────────────────────────────────────────────────────────────────────
#  Freshness
# ─────────────────────────────────────────────────────────────────────────────

def pulse_age_hours(payload: dict[str, Any]) -> float:
    """Return the pulse's age in hours, computed from `updated_at`."""
    when = datetime.fromisoformat(payload["updated_at"])
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    delta = datetime.now(when.tzinfo) - when
    return delta.total_seconds() / 3600.0


def is_stale(payload: dict[str, Any], max_age_hours: float = 24.0) -> bool:
    """True when the pulse's `updated_at` is older than `max_age_hours`."""
    return pulse_age_hours(payload) > max_age_hours


# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    """`python -m cfo.pulse_schema [path]` — validate a pulse file."""
    import json
    import sys
    from pathlib import Path

    args = argv if argv is not None else sys.argv[1:]
    if not args:
        path = Path(__file__).resolve().parents[1] / "data" / "pulse" / "cfo_pulse.json"
    else:
        path = Path(args[0])

    if not path.exists():
        print(f"FAIL: pulse file not found: {path}")
        return 2

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_pulse(payload)
    except PulseSchemaError as exc:
        print(f"FAIL: schema violation in {path.name}: {exc}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"FAIL: malformed JSON in {path.name}: {exc}")
        return 1

    age = pulse_age_hours(payload)
    stale = is_stale(payload)
    print(
        f"OK: {path.name} | agent={payload['agent']} | gate={payload['spend_gate']} | "
        f"age={age:.1f}h{' (STALE)' if stale else ''}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
