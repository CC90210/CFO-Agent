"""
tests/test_pulse.py
-------------------
Schema + freshness tests for cfo_pulse.json — Atlas's hand-off contract
to Maven (CMO) and Bravo (CEO).

If pulse format drifts, Maven's spend gate fails closed and CC's ad
budget sits idle. Every field Maven reads must be either present or
explicitly nullable per the contract in brain/CFO_PULSE_CONTRACT.md.

Run:
    python -m pytest tests/test_pulse.py -v
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cfo.pulse_schema import (
    PulseSchemaError,
    is_stale,
    validate_pulse,
)

ROOT = Path(__file__).resolve().parents[1]
LIVE_PULSE = ROOT / "data" / "pulse" / "cfo_pulse.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _hours_ago_iso(hours: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).astimezone().isoformat(
        timespec="seconds"
    )


def _minimal_valid_pulse() -> dict:
    """Smallest pulse dict that satisfies the contract."""
    return {
        "agent": "atlas",
        "schema_version": "1.0",
        "updated_at": _now_iso(),
        "liquid_cad": 7_466.84,
        "liquid_source": "live API reads (n=8) + manual entries (n=5)",
        "montreal_floor_target_cad": 10_000.0,
        "montreal_floor_gap_cad": 2_533.16,
        "tax_reserve_required_cad": 3_064.01,
        "tax_reserve_rate_pct": 25,
        "concentration_risk_single_client_pct": 94.0,
        "concentration_risk_client": "Bennett",
        "mrr_usd_from_bravo": 2_982.0,
        "mrr_cad_from_bravo": 4_085.34,
        # Maven reads spend_gate as a nested object — see CFO_PULSE_CONTRACT.md
        "spend_gate": {
            "status": "tight",
            "reason": "Below floor; concentration high",
            "monthly_cap_cad": 100,
            "rule": "experimentation_only",
            "approvals": {
                "meta_ads": {"*": {"daily_budget_usd": 1.22}},
                "google_ads": {"*": {"daily_budget_usd": 1.22}},
            },
        },
        "spend_gate_reason": "Below floor; concentration high",
        "approved_ad_spend_monthly_cap_cad": 100,
        "approved_ad_spend_rule": "experimentation_only",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Schema validation — required fields
# ─────────────────────────────────────────────────────────────────────────────

class TestSchemaRequiredFields:
    def test_minimal_valid_pulse_passes(self) -> None:
        validate_pulse(_minimal_valid_pulse())

    def test_missing_agent_field_fails(self) -> None:
        p = _minimal_valid_pulse()
        del p["agent"]
        with pytest.raises(PulseSchemaError, match="agent"):
            validate_pulse(p)

    def test_missing_liquid_cad_fails(self) -> None:
        p = _minimal_valid_pulse()
        del p["liquid_cad"]
        with pytest.raises(PulseSchemaError, match="liquid_cad"):
            validate_pulse(p)

    def test_missing_spend_gate_fails(self) -> None:
        p = _minimal_valid_pulse()
        del p["spend_gate"]
        with pytest.raises(PulseSchemaError, match="spend_gate"):
            validate_pulse(p)

    def test_missing_ad_spend_cap_fails(self) -> None:
        p = _minimal_valid_pulse()
        del p["approved_ad_spend_monthly_cap_cad"]
        with pytest.raises(PulseSchemaError, match="approved_ad_spend_monthly_cap_cad"):
            validate_pulse(p)


# ─────────────────────────────────────────────────────────────────────────────
#  Schema validation — value sanity
# ─────────────────────────────────────────────────────────────────────────────

class TestSchemaValueSanity:
    def test_invalid_spend_gate_status_value(self) -> None:
        p = _minimal_valid_pulse()
        p["spend_gate"]["status"] = "yolo"
        with pytest.raises(PulseSchemaError, match="status"):
            validate_pulse(p)

    def test_spend_gate_must_be_object_not_string(self) -> None:
        """Regression test: Atlas v0 wrote spend_gate as a plain string;
        Maven's send_gateway expects a nested dict and crashes on string."""
        p = _minimal_valid_pulse()
        p["spend_gate"] = "tight"
        with pytest.raises(PulseSchemaError, match="spend_gate"):
            validate_pulse(p)

    def test_negative_liquid_rejected(self) -> None:
        p = _minimal_valid_pulse()
        p["liquid_cad"] = -100
        with pytest.raises(PulseSchemaError, match="liquid_cad"):
            validate_pulse(p)

    def test_concentration_pct_above_100_rejected(self) -> None:
        p = _minimal_valid_pulse()
        p["concentration_risk_single_client_pct"] = 120
        with pytest.raises(PulseSchemaError, match="concentration"):
            validate_pulse(p)

    def test_unknown_agent_rejected(self) -> None:
        p = _minimal_valid_pulse()
        p["agent"] = "skynet"
        with pytest.raises(PulseSchemaError, match="agent"):
            validate_pulse(p)

    def test_malformed_timestamp_rejected(self) -> None:
        p = _minimal_valid_pulse()
        p["updated_at"] = "not-a-date"
        with pytest.raises(PulseSchemaError, match="updated_at"):
            validate_pulse(p)


# ─────────────────────────────────────────────────────────────────────────────
#  Freshness / staleness
# ─────────────────────────────────────────────────────────────────────────────

class TestStalenessCheck:
    def test_fresh_pulse_not_stale(self) -> None:
        p = _minimal_valid_pulse()
        assert is_stale(p, max_age_hours=24) is False

    def test_old_pulse_marked_stale(self) -> None:
        p = _minimal_valid_pulse()
        p["updated_at"] = _hours_ago_iso(48)
        assert is_stale(p, max_age_hours=24) is True

    def test_just_under_threshold_not_stale(self) -> None:
        p = _minimal_valid_pulse()
        p["updated_at"] = _hours_ago_iso(5.5)
        assert is_stale(p, max_age_hours=6) is False

    def test_just_over_threshold_stale(self) -> None:
        p = _minimal_valid_pulse()
        p["updated_at"] = _hours_ago_iso(7)
        assert is_stale(p, max_age_hours=6) is True


# ─────────────────────────────────────────────────────────────────────────────
#  Live pulse file (if present)
# ─────────────────────────────────────────────────────────────────────────────

class TestLivePulseFile:
    @pytest.mark.skipif(not LIVE_PULSE.exists(), reason="No live pulse file yet")
    def test_live_pulse_passes_schema(self) -> None:
        """The actual pulse on disk should validate."""
        data = json.loads(LIVE_PULSE.read_text(encoding="utf-8"))
        validate_pulse(data)

    @pytest.mark.skipif(not LIVE_PULSE.exists(), reason="No live pulse file yet")
    def test_live_pulse_marked_atlas(self) -> None:
        data = json.loads(LIVE_PULSE.read_text(encoding="utf-8"))
        assert data["agent"] == "atlas"


# ─────────────────────────────────────────────────────────────────────────────
#  Maven-readable shape (the fields Maven specifically reads)
# ─────────────────────────────────────────────────────────────────────────────

class TestMavenContract:
    """
    These fields are what Maven's `scripts/send_gateway.py:check_cfo_spend_gate`
    reads. Removing or renaming any of them silently breaks Maven.
    """
    MAVEN_TOP_LEVEL_REQUIRED = (
        "spend_gate",
        "liquid_cad",
        "concentration_risk_single_client_pct",
    )
    MAVEN_NESTED_REQUIRED = ("status", "reason", "monthly_cap_cad", "rule", "approvals")

    def test_all_maven_top_level_fields_present(self) -> None:
        p = _minimal_valid_pulse()
        for field in self.MAVEN_TOP_LEVEL_REQUIRED:
            assert field in p, f"Maven-required top-level field missing: {field}"

    def test_all_maven_nested_fields_present(self) -> None:
        p = _minimal_valid_pulse()
        for field in self.MAVEN_NESTED_REQUIRED:
            assert field in p["spend_gate"], (
                f"Maven-required spend_gate.{field} missing"
            )

    def test_strip_top_level_field_fails(self) -> None:
        for field in self.MAVEN_TOP_LEVEL_REQUIRED:
            p = _minimal_valid_pulse()
            del p[field]
            with pytest.raises(PulseSchemaError):
                validate_pulse(p)

    def test_strip_nested_field_fails(self) -> None:
        for field in self.MAVEN_NESTED_REQUIRED:
            p = _minimal_valid_pulse()
            del p["spend_gate"][field]
            with pytest.raises(PulseSchemaError):
                validate_pulse(p)

    def test_approvals_keyed_by_channel_then_brand(self) -> None:
        """Maven reads approvals[channel][brand].daily_budget_usd."""
        p = _minimal_valid_pulse()
        approvals = p["spend_gate"]["approvals"]
        for channel, brands in approvals.items():
            assert isinstance(brands, dict), f"{channel} approvals not a dict"
            for brand, cfg in brands.items():
                assert "daily_budget_usd" in cfg, (
                    f"approvals.{channel}.{brand} missing daily_budget_usd"
                )
