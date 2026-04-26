"""
tests/test_dispatch_gate.py
---------------------------
Tests for cfo/dispatch_gate.py — Atlas's single chokepoint for outbound
actions (tax filings, pulse writes, Telegram alerts, email reports).

Each test isolates state under a tmp_path so the on-disk dedup/rate-
limit logs don't bleed between tests.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

import cfo.dispatch_gate as dg


@pytest.fixture(autouse=True)
def _isolate_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect dispatch state into a fresh tmp dir for every test."""
    monkeypatch.setattr(dg, "_STATE_DIR", tmp_path / "dispatch")
    # Ensure killswitch is OFF unless a test explicitly enables it
    monkeypatch.delenv(dg.KILLSWITCH_ENV, raising=False)


def _valid_pulse() -> dict:
    return {
        "agent": "atlas",
        "schema_version": "1.0",
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "liquid_cad": 7466.84,
        "liquid_source": "test",
        "montreal_floor_target_cad": 10000.0,
        "montreal_floor_gap_cad": 2533.16,
        "tax_reserve_required_cad": 3064.01,
        "tax_reserve_rate_pct": 25,
        "concentration_risk_single_client_pct": 94.0,
        "concentration_risk_client": "Bennett",
        "mrr_usd_from_bravo": 2982.0,
        "mrr_cad_from_bravo": 4085.34,
        "spend_gate": {
            "status": "tight",
            "reason": "test",
            "monthly_cap_cad": 100,
            "rule": "experimentation_only",
            "approvals": {
                "meta_ads": {"*": {"daily_budget_usd": 1.22}},
                "google_ads": {"*": {"daily_budget_usd": 1.22}},
            },
        },
        "spend_gate_reason": "test",
        "approved_ad_spend_monthly_cap_cad": 100,
        "approved_ad_spend_rule": "experimentation_only",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Allow-list / payload validation
# ─────────────────────────────────────────────────────────────────────────────

class TestActionAllowList:
    def test_unknown_action_raises(self) -> None:
        with pytest.raises(dg.DispatchError, match="unknown action"):
            dg.dispatch("rm_rf_root", {})

    def test_payload_must_be_dict(self) -> None:
        with pytest.raises(dg.DispatchError, match="payload must be a dict"):
            dg.dispatch("telegram_alert", "hi")  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
#  Killswitch
# ─────────────────────────────────────────────────────────────────────────────

class TestKillswitch:
    def test_killswitch_off_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(dg.KILLSWITCH_ENV, raising=False)
        assert dg.killswitch_active() is False

    def test_killswitch_on_with_value_1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(dg.KILLSWITCH_ENV, "1")
        assert dg.killswitch_active() is True

    def test_killswitch_blocks_telegram(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(dg.KILLSWITCH_ENV, "1")
        result = dg.dispatch("telegram_alert", {"text": "hi"})
        assert result.sent is False
        assert result.reason == "killswitch_active"
        assert result.dry_run is True

    def test_killswitch_blocks_pulse_write(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(dg.KILLSWITCH_ENV, "1")
        result = dg.dispatch("pulse_write", _valid_pulse())
        assert result.sent is False
        assert result.reason == "killswitch_active"


# ─────────────────────────────────────────────────────────────────────────────
#  Pulse-write validator integration
# ─────────────────────────────────────────────────────────────────────────────

class TestPulseWriteHandler:
    def test_valid_pulse_authorised(self) -> None:
        result = dg.dispatch("pulse_write", _valid_pulse())
        assert result.sent is True
        assert result.extra["validated"] is True

    def test_invalid_pulse_raises(self) -> None:
        bad = _valid_pulse()
        del bad["liquid_cad"]
        with pytest.raises(dg.DispatchError, match="pulse_schema"):
            dg.dispatch("pulse_write", bad)

    def test_dry_run_does_not_send(self) -> None:
        result = dg.dispatch("pulse_write", _valid_pulse(), dry_run=True)
        assert result.sent is False
        assert "dry_run" in result.reason


# ─────────────────────────────────────────────────────────────────────────────
#  Tax filing — always dry-run
# ─────────────────────────────────────────────────────────────────────────────

class TestTaxFilingHandler:
    def test_tax_filing_never_sends(self) -> None:
        result = dg.dispatch("tax_filing", {
            "form": "T1",
            "tax_year": 2025,
            "summary": {"net_owing": 0},
        })
        assert result.sent is False
        assert "dry-run only" in result.reason

    def test_tax_filing_payload_validated(self) -> None:
        with pytest.raises(dg.DispatchError, match="missing fields"):
            dg.dispatch("tax_filing", {"form": "T1"})


# ─────────────────────────────────────────────────────────────────────────────
#  Rate limit + dedup
# ─────────────────────────────────────────────────────────────────────────────

class TestRateLimitAndDedup:
    def test_telegram_dedup_within_window(self) -> None:
        payload = {"text": "Liquid below floor"}
        first = dg.dispatch("telegram_alert", payload)
        second = dg.dispatch("telegram_alert", payload)
        assert first.sent is True
        assert second.sent is False
        assert second.reason == "duplicate_within_window"

    def test_different_text_not_deduped(self) -> None:
        first = dg.dispatch("telegram_alert", {"text": "alert one"})
        second = dg.dispatch("telegram_alert", {"text": "alert two"})
        assert first.sent is True
        assert second.sent is True

    def test_rate_limit_caps_telegram_at_30(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Lower the cap for the test so we don't have to send 30 messages
        monkeypatch.setitem(dg.RATE_LIMITS_PER_DAY, "telegram_alert", 3)
        sent_count = 0
        for i in range(6):
            r = dg.dispatch("telegram_alert", {"text": f"msg {i}"})
            if r.sent:
                sent_count += 1
        assert sent_count == 3


# ─────────────────────────────────────────────────────────────────────────────
#  Fingerprint stability
# ─────────────────────────────────────────────────────────────────────────────

class TestFingerprint:
    def test_same_payload_same_fingerprint(self) -> None:
        a = dg._fingerprint({"x": 1, "y": 2})
        b = dg._fingerprint({"y": 2, "x": 1})
        assert a == b  # key order independent

    def test_different_payload_different_fingerprint(self) -> None:
        a = dg._fingerprint({"x": 1})
        b = dg._fingerprint({"x": 2})
        assert a != b
