"""
cfo/pulse.py
------------
CFO pulse publisher — rebuilds `data/pulse/cfo_pulse.json` from live data sources
so Bravo (and any other reader) always sees the current CFO state without Atlas
having to manually update the file.

Call `publish()` after any event that changes financial state:
    - New stock pick
    - Completed tax filing
    - MRR change observed
    - Montreal move decision
    - Spend gate flip

Also called automatically at the end of `main.py networth`, `main.py runway`,
and `main.py receipts` (see main.py).

Reads FROM:
    - cfo.accounts.all_balances() for liquid cash
    - cfo.gmail_receipts for YTD receipt totals
    - brain/USER.md for tax reserve rate + MRR context
    - Business-Empire-Agent/data/pulse/ceo_pulse.json for concentration risk

Writes TO:
    - data/pulse/cfo_pulse.json (atomic rename to avoid torn reads)
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[1]
_PULSE_PATH = _ROOT / "data" / "pulse" / "cfo_pulse.json"
_BRAVO_PULSE_PATH = Path(r"C:\Users\User\Business-Empire-Agent\data\pulse\ceo_pulse.json")
# Maven (CMO) writes cmo_pulse.json at its own path per C_SUITE_ARCHITECTURE.md.
# The old Marketing-Agent path + Bravo's path are kept as fallbacks during
# the 2026-04-18 rebrand transition. Canonical is CMO-Agent.
_MAVEN_PULSE_PATHS = [
    Path(r"C:\Users\User\CMO-Agent\data\pulse\cmo_pulse.json"),
    Path(r"C:\Users\User\Marketing-Agent\data\pulse\cmo_pulse.json"),
    Path(r"C:\Users\User\Business-Empire-Agent\data\pulse\cmo_pulse.json"),
]
_MONTREAL_FLOOR_CAD = 10_000.0
_TAX_RESERVE_RATE = 0.25


def _read_pulse_file(path: Path, agent_name: str) -> dict:
    """Return a pulse file's contents with staleness annotation, or {} if absent."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        updated = data.get("updated_at", "")
        if updated:
            try:
                when = datetime.fromisoformat(updated)
                age_days = (datetime.now(when.tzinfo) - when).days
                if age_days > 7:
                    logger.warning(
                        "%s pulse is %d days old — treating as stale", agent_name, age_days,
                    )
                data["_stale_days"] = max(0, age_days)
            except ValueError:
                data["_stale_days"] = None
        return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read %s pulse (%s): %s", agent_name, path, exc)
        return {}


def _read_bravo_pulse() -> dict:
    """Return Bravo's latest ceo_pulse.json, {} if unavailable."""
    return _read_pulse_file(_BRAVO_PULSE_PATH, "Bravo")


def _read_maven_pulse() -> dict:
    """Return Maven's latest cmo_pulse.json, {} if Maven hasn't published yet.

    Checks the canonical CMO-Agent path first, then falls back to the old
    Marketing-Agent path and Business-Empire-Agent path where copies may
    sit during the 2026-04-18 rebrand transition.
    """
    for path in _MAVEN_PULSE_PATHS:
        if path.exists():
            data = _read_pulse_file(path, "Maven")
            if data:
                data["_source_path"] = str(path)
                return data
    return {}


def _compute_liquid_cad() -> tuple[float, str]:
    """Return (liquid_cad, source_description). Safe under partial API outages."""
    from cfo.accounts import all_balances

    try:
        balances = all_balances()
    except Exception as exc:  # noqa: BLE001
        logger.error("all_balances() failed during pulse publish: %s", exc)
        return 0.0, f"ERROR: {exc}"

    live_cats = {"cash", "crypto", "registered", "business"}
    total = sum(b.amount for b in balances if b.category in live_cats and b.amount > 0)
    api_reads = sum(1 for b in balances if b.source == "api")
    manual_reads = sum(1 for b in balances if b.source == "manual")
    src = f"live API reads (n={api_reads}) + manual entries (n={manual_reads})"
    return round(total, 2), src


def _compute_ytd_receipts() -> dict:
    """Return YTD receipt totals. Empty dict on failure — non-fatal."""
    try:
        from collections import defaultdict

        from cfo.gmail_receipts import GmailReceipts

        since = date(date.today().year, 1, 1)
        with GmailReceipts() as gr:
            available = gr.list_labels()
            labels = [lbl for lbl in available if lbl.startswith(f"Receipts/{since.year}/")]
            receipts: list = []
            for lbl in labels:
                try:
                    receipts.extend(gr.fetch_label(lbl, since=since))
                except Exception:  # noqa: BLE001
                    continue

        parsed = [r for r in receipts if r.amount_cad is not None and r.amount_cad > 0]
        by_cat: dict[str, float] = defaultdict(float)
        for r in parsed:
            by_cat[r.category] += r.amount_cad

        return {
            "total_cad": round(sum(by_cat.values()), 2),
            "item_count_parsed": len(parsed),
            "item_count_needs_review": len(receipts) - len(parsed),
            "by_category": {k: round(v, 2) for k, v in by_cat.items()},
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("YTD receipts unavailable for pulse: %s", exc)
        return {}


def _determine_spend_gate(liquid: float, concentration_pct: float) -> tuple[str, str]:
    """Gate logic: tight if under Montreal floor OR client concentration > 70%."""
    reasons: list[str] = []
    if liquid < _MONTREAL_FLOOR_CAD:
        reasons.append(f"Below Montreal floor by ${_MONTREAL_FLOOR_CAD - liquid:,.0f}")
    if concentration_pct and concentration_pct >= 70:
        reasons.append(f"Single-client concentration at {concentration_pct:.0f}%")
    if not reasons:
        return "open", "Floor met, concentration under 70%"
    if liquid < _MONTREAL_FLOOR_CAD * 0.5:
        return "frozen", "; ".join(reasons) + " — halving Montreal floor threshold crossed"
    return "tight", "; ".join(reasons)


def _approved_ad_spend_cad(spend_gate: str, mrr_cad: float) -> dict:
    """
    Compute how much monthly ad spend Atlas authorizes for Maven.

    Rules:
      - frozen: $0 — no discretionary spend of any kind
      - tight:  hard cap at $100 CAD/mo — experimentation budget only
      - open:   up to 15% of MRR, floor at $500, ceiling at $2000 until
                incorporated (post-CCPC the ceiling lifts as ad spend is
                T2125-deductible and reduces taxable income).
    """
    if spend_gate == "frozen":
        return {"monthly_cap_cad": 0, "rule": "frozen_gate"}
    if spend_gate == "tight":
        return {"monthly_cap_cad": 100, "rule": "experimentation_only"}
    # open
    target = min(max(0.15 * mrr_cad, 500), 2000)
    return {"monthly_cap_cad": round(target, 2), "rule": "15pct_mrr_cap_2k"}


def publish(extra: dict | None = None) -> Path:
    """
    Rebuild cfo_pulse.json from live data and write it atomically.

    Parameters
    ----------
    extra : dict, optional
        Per-event override fields merged on top of the computed pulse
        (e.g. flag a new pick, record a filing event).

    Returns
    -------
    Path to the published pulse file.
    """
    liquid_cad, liquid_src = _compute_liquid_cad()
    ytd_receipts = _compute_ytd_receipts()

    bravo = _read_bravo_pulse()
    # Bravo's schema evolved — support both old (flat mrr_usd + clients_top[])
    # and new (nested revenue.{net_mrr_usd, bennett_concentration_pct}) forms.
    bravo_revenue = bravo.get("revenue") or {}
    mrr_usd = float(
        bravo_revenue.get("net_mrr_usd")
        or bravo.get("mrr_usd")
        or 2982
    )
    mrr_cad = round(mrr_usd * 1.37, 2)
    concentration_pct = float(
        bravo_revenue.get("bennett_concentration_pct")
        or (bravo.get("clients_top") or [{}])[0].get("share_pct")
        or 0
    )
    client_name = (
        "Bennett" if bravo_revenue.get("bennett_concentration_pct")
        else (bravo.get("clients_top") or [{}])[0].get("name") or ""
    )

    monthly_reserve_cad = mrr_usd * 1.37 * _TAX_RESERVE_RATE
    quarterly_reserve_cad = round(monthly_reserve_cad * 3, 2)

    spend_gate, spend_gate_reason = _determine_spend_gate(liquid_cad, concentration_pct)

    # Read Maven's pulse to reconcile requested vs approved ad spend
    maven = _read_maven_pulse()
    maven_spend_request_cad = float(maven.get("spend_request_cad") or 0)
    ad_authorization = _approved_ad_spend_cad(spend_gate, mrr_cad)
    # Maven's request is approved only if it sits within Atlas's monthly cap
    maven_spend_approved = (
        maven_spend_request_cad > 0
        and maven_spend_request_cad <= ad_authorization["monthly_cap_cad"]
    )

    pulse: dict[str, Any] = {
        # Agent identity — required by the 3-way pulse stress test so readers
        # can verify the source without inferring from file path.
        "agent": "atlas",
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "liquid_cad": liquid_cad,
        "liquid_source": liquid_src,
        "montreal_floor_target_cad": _MONTREAL_FLOOR_CAD,
        "montreal_floor_gap_cad": round(max(0, _MONTREAL_FLOOR_CAD - liquid_cad), 2),
        "tax_reserve_required_cad": quarterly_reserve_cad,
        "tax_reserve_rate_pct": int(_TAX_RESERVE_RATE * 100),
        "concentration_risk_single_client_pct": concentration_pct,
        "concentration_risk_client": client_name,
        "mrr_usd_from_bravo": mrr_usd,
        "mrr_cad_from_bravo": mrr_cad,
        "bravo_pulse_age_days": bravo.get("_stale_days", 0),
        "ytd_2026_receipts": ytd_receipts,
        "integrations_live": {
            "wise_business_usd": bool(os.environ.get("WISE_API_TOKEN")),
            "stripe": bool(
                os.environ.get("STRIPE_RESTRICTED_KEY")
                or os.environ.get("STRIPE_API_KEY")
                or os.environ.get("STRIPE_SECRET_KEY")
            ),
            "kraken": bool(os.environ.get("EXCHANGE_API_KEY")),
            "oanda": bool(os.environ.get("OANDA_TOKEN")),
            "gmail_receipts": bool(os.environ.get("GMAIL_APP_PASSWORD")),
        },
        "spend_gate": spend_gate,
        "spend_gate_reason": spend_gate_reason,
        # ── Maven-readable fields (CFO -> CMO handshake) ────────────────
        # Maven reads these before launching any paid campaign. Per the
        # 3-way pulse contract, Atlas's cap is authoritative.
        "approved_ad_spend_monthly_cap_cad": ad_authorization["monthly_cap_cad"],
        "approved_ad_spend_rule": ad_authorization["rule"],
        "maven_pulse_found": bool(maven),
        "maven_pulse_age_days": maven.get("_stale_days") if maven else None,
        "maven_pulse_source": maven.get("_source_path") if maven else None,
        "maven_current_spend_request_cad": maven_spend_request_cad,
        "maven_current_spend_approved": maven_spend_approved,
        "t2125_ad_deduction_note": (
            "Ad spend tracked through Maven is a T2125 line 8521 deduction. "
            "Every $1 of ad spend reduces taxable income dollar-for-dollar. "
            "Post-CCPC this matters more because the corp deducts at 12.2% bracket."
        ),
    }

    if extra:
        pulse.update(extra)

    _PULSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write: temp file + rename, so readers never catch a half-written file
    fd, tmp_path = tempfile.mkstemp(
        prefix="cfo_pulse_", suffix=".json.tmp", dir=str(_PULSE_PATH.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(pulse, f, indent=2, default=str)
        os.replace(tmp_path, _PULSE_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    logger.info(
        "cfo_pulse.json refreshed — liquid=$%s gate=%s receipts=$%s",
        f"{liquid_cad:,.0f}",
        spend_gate,
        f"{ytd_receipts.get('total_cad', 0):,.2f}" if ytd_receipts else "n/a",
    )
    return _PULSE_PATH


if __name__ == "__main__":
    # Allow direct invocation for cron / one-off refresh:
    #   python -m cfo.pulse
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    path = publish()
    print(f"Published: {path}")
    print(path.read_text(encoding="utf-8"))
