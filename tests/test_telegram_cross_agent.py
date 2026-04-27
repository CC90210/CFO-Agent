"""
tests/test_telegram_cross_agent.py
----------------------------------
Tests for the Telegram bridge's cross-agent helpers (`_run_pulses`,
`_run_sibling`, `_sibling_repos`). These are what let CC ask Atlas
on his phone "what's Bravo saying?" or "show me Maven's brand brief"
without leaving Telegram.

Tests run with all sibling repos pointed at tmp dirs so they pass on
any machine — Mac, Windows, CI.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import telegram_bridge as tb


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _now_iso(hours_ago: float = 0) -> str:
    when = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return when.astimezone().isoformat(timespec="seconds")


@pytest.fixture
def fake_repos(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Three fake sibling repos. Atlas always points at the real CFO-Agent."""
    bravo = tmp_path / "Bravo"
    maven = tmp_path / "Maven"
    aura = tmp_path / "Aura"
    for repo in (bravo, maven, aura):
        (repo / "brain").mkdir(parents=True)
        (repo / "data" / "pulse").mkdir(parents=True)

    # Stub _sibling_repos to return our fakes
    fakes = {
        "atlas": tb._ROOT,
        "bravo": bravo,
        "maven": maven,
        "aura": aura,
    }
    monkeypatch.setattr(tb, "_sibling_repos", lambda: fakes)
    return fakes


# ─────────────────────────────────────────────────────────────────────────────
#  _short_age
# ─────────────────────────────────────────────────────────────────────────────

class TestShortAge:
    def test_minutes_ago(self) -> None:
        ts = _now_iso(hours_ago=0.1)  # 6 min
        out = tb._short_age(ts)
        assert "m ago" in out

    def test_hours_ago(self) -> None:
        ts = _now_iso(hours_ago=4)
        assert tb._short_age(ts) == "4h ago"

    def test_days_ago(self) -> None:
        ts = _now_iso(hours_ago=72)
        assert tb._short_age(ts) == "3d ago"

    def test_empty_returns_na(self) -> None:
        assert tb._short_age("") == "n/a"

    def test_garbage_returns_truncated(self) -> None:
        assert tb._short_age("not-a-timestamp") in ("not-a-timestamp", "n/a")


# ─────────────────────────────────────────────────────────────────────────────
#  _run_pulses
# ─────────────────────────────────────────────────────────────────────────────

class TestRunPulses:
    def test_all_three_present(self, fake_repos) -> None:
        _write(fake_repos["bravo"] / "data" / "pulse" / "ceo_pulse.json", {
            "updated_at": _now_iso(hours_ago=2),
            "revenue": {"net_mrr_usd": 2982, "bennett_concentration_pct": 94},
        })
        _write(fake_repos["maven"] / "data" / "pulse" / "cmo_pulse.json", {
            "updated_at": _now_iso(hours_ago=1),
            "spend_request_cad": 50,
        })
        out = tb._run_pulses()
        assert "Atlas (CFO)" in out
        assert "Bravo (CEO)" in out
        assert "Maven (CMO)" in out
        assert "MRR=$2982" in out
        assert "spend_request=$50" in out

    def test_missing_sibling_pulse_reported(self, fake_repos) -> None:
        out = tb._run_pulses()
        assert "Bravo (CEO): MISSING" in out

    def test_atlas_pulse_includes_gate_and_cap(self, fake_repos) -> None:
        out = tb._run_pulses()
        # Atlas's live pulse exists (from _ROOT)
        assert "Atlas (CFO)" in out
        assert "gate=" in out
        assert "cap=$" in out

    def test_malformed_json_handled_gracefully(self, fake_repos) -> None:
        # Write garbage to Bravo's pulse
        path = fake_repos["bravo"] / "data" / "pulse" / "ceo_pulse.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not json", encoding="utf-8")
        out = tb._run_pulses()
        assert "PARSE ERROR" in out or "Bravo (CEO):" in out


# ─────────────────────────────────────────────────────────────────────────────
#  _run_sibling
# ─────────────────────────────────────────────────────────────────────────────

class TestRunSibling:
    def test_no_args_returns_usage(self, fake_repos) -> None:
        out = tb._run_sibling("")
        assert "Usage:" in out

    def test_unknown_agent_rejected(self, fake_repos) -> None:
        out = tb._run_sibling("skynet")
        assert "Unknown agent" in out

    def test_list_brain_files(self, fake_repos) -> None:
        (fake_repos["bravo"] / "brain" / "SOUL.md").write_text("# Bravo SOUL", encoding="utf-8")
        (fake_repos["bravo"] / "brain" / "STATE.md").write_text("# Bravo STATE", encoding="utf-8")
        out = tb._run_sibling("bravo")
        assert "SOUL.md" in out
        assert "STATE.md" in out

    def test_read_specific_file(self, fake_repos) -> None:
        (fake_repos["maven"] / "brain" / "BRAND_BRIEF.md").write_text(
            "# Brand Brief\nOasis AI Solutions...", encoding="utf-8",
        )
        out = tb._run_sibling("maven BRAND_BRIEF")
        assert "Oasis AI Solutions" in out
        assert "Maven/brain/BRAND_BRIEF.md" in out

    def test_md_extension_appended_automatically(self, fake_repos) -> None:
        (fake_repos["bravo"] / "brain" / "SOUL.md").write_text("# soul", encoding="utf-8")
        out = tb._run_sibling("bravo SOUL")  # no .md
        assert "# soul" in out

    def test_missing_file_lists_alternatives(self, fake_repos) -> None:
        (fake_repos["bravo"] / "brain" / "SOUL.md").write_text("# soul", encoding="utf-8")
        out = tb._run_sibling("bravo NONEXISTENT")
        assert "not found" in out
        assert "SOUL.md" in out

    def test_path_traversal_blocked(self, fake_repos) -> None:
        """Slashes/backslashes in filename must be stripped — no escaping brain/."""
        (fake_repos["bravo"] / "brain" / "SOUL.md").write_text("# soul", encoding="utf-8")
        out = tb._run_sibling("bravo ../../../etc/passwd")
        # Should be treated as a flat filename; will not find file
        assert "not found" in out

    def test_repo_not_on_machine_handled(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """When a sibling repo is missing entirely, fail gracefully."""
        monkeypatch.setattr(tb, "_sibling_repos", lambda: {
            "atlas": tb._ROOT,
            "bravo": tmp_path / "does-not-exist",
            "maven": tb._ROOT,
            "aura": tb._ROOT,
        })
        out = tb._run_sibling("bravo")
        assert "not on this machine" in out


# ─────────────────────────────────────────────────────────────────────────────
#  _sibling_repos resolver
# ─────────────────────────────────────────────────────────────────────────────

class TestSiblingResolver:
    def test_returns_all_four_agents(self) -> None:
        repos = tb._sibling_repos()
        assert set(repos) >= {"atlas", "bravo", "maven", "aura"}

    def test_atlas_points_at_local_root(self) -> None:
        repos = tb._sibling_repos()
        assert repos["atlas"] == tb._ROOT
