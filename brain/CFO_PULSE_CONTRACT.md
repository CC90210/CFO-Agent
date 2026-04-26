# CFO Pulse Contract

> **Why CC cares (in plain English):** This is how Atlas tells Maven
> whether ad spend is allowed and tells Bravo whether the runway can
> support new commitments. You don't need to read this unless something
> is broken or you're rewiring agents. To check the current state, just
> run `python main.py networth` — that publishes a fresh pulse.

> Atlas → Maven (CMO) + Bravo (CEO) hand-off contract.
> Source of truth: `cfo/pulse.py` (publisher) + `cfo/pulse_schema.py` (validator).
> File written by Atlas: `data/pulse/cfo_pulse.json` (atomic write).

## Purpose

`cfo_pulse.json` is the single document Maven reads to authorize paid
campaigns and Bravo reads to gate hiring/contracting decisions. The
contract is load-bearing: if Maven's gate cannot find a required field,
it fails closed (no spend) and CC's ad budget sits idle.

## Lifecycle

1. **Trigger** — any of: new stock pick, completed tax filing, MRR change,
   Montreal-move decision, spend-gate flip, runway recompute.
2. **Compute** — `cfo.pulse.publish()` reads live data (accounts,
   gmail receipts, Bravo + Maven pulses) and assembles the payload.
3. **Validate** — `cfo.pulse_schema.validate_pulse(payload)` runs before
   write. Schema violation aborts the write atomically.
4. **Write** — atomic `tempfile + os.replace`. Readers never see a
   half-written file.
5. **Read** — Maven and Bravo open the file, run `validate_pulse` on
   their copy of the schema, and treat any failure as "no fresh pulse".
6. **Stale check** — `is_stale(payload, max_age_hours=24)` is the
   default. Maven should refuse to act on a stale pulse.

## Schema version

`schema_version: "1.0"` — added 2026-04-26. Anything older lacked this
field; readers should treat absence as v0 (string-typed `spend_gate`)
and refuse to act on it.

## Required fields

| Field | Type | Notes |
|-------|------|-------|
| `schema_version` | str | `"1.0"` today |
| `agent` | `"atlas"` | Identity (validator allows `atlas`/`bravo`/`maven`/`aura` for shared schema) |
| `updated_at` | ISO 8601 string | Includes timezone offset |
| `liquid_cad` | float ≥ 0 | Sum of cash, crypto, registered, business across Atlas's account readers |
| `liquid_source` | str | Free-text describing how liquid was computed |
| `montreal_floor_target_cad` | float | Atlas's hard cushion line (currently $10,000) |
| `montreal_floor_gap_cad` | float | `max(0, target − liquid)`. Validator checks this invariant |
| `tax_reserve_required_cad` | float | Quarterly amount to keep liquid for CRA |
| `tax_reserve_rate_pct` | int 0..100 | Reserve % applied to MRR (currently 25) |
| `concentration_risk_single_client_pct` | float 0..100 | Top-client share of MRR |
| `concentration_risk_client` | str | Top-client name (`""` if no concentration risk) |
| `mrr_usd_from_bravo` | float | MRR pulled from Bravo's pulse |
| `mrr_cad_from_bravo` | float | Same MRR converted CAD |
| `spend_gate` | **dict** | Nested object — see below |
| `spend_gate_reason` | str | Human-readable explanation |
| `approved_ad_spend_monthly_cap_cad` | float ≥ 0 | The dollar cap Maven must honor (back-compat alias for `spend_gate.monthly_cap_cad`) |
| `approved_ad_spend_rule` | enum | `frozen_gate` / `no_revenue` / `experimentation_only` / `15pct_mrr_cap_2k` |

### `spend_gate` object (the one Maven reads)

```json
"spend_gate": {
  "status": "tight",                    // open | tight | frozen
  "reason": "Below floor by $2,833",
  "monthly_cap_cad": 100,
  "rule": "experimentation_only",
  "approvals": {
    "meta_ads":   { "*": { "daily_budget_usd": 1.22 } },
    "google_ads": { "*": { "daily_budget_usd": 1.22 } }
  }
}
```

`approvals[channel][brand].daily_budget_usd` is the per-channel daily
USD cap. `"*"` is a wildcard brand — Maven's `send_gateway.py` falls
back to `"*"` when no brand-specific entry exists.

The total monthly USD across `approvals` equals `monthly_cap_cad / fx_rate`
(equally split across the two paid channels Atlas pre-authorises).

## Optional fields (typed when present)

| Field | Type |
|-------|------|
| `bravo_pulse_age_days` | int / float / null |
| `ytd_2026_receipts` | dict / null |
| `integrations_live` | dict |
| `maven_pulse_found` | bool |
| `maven_pulse_age_days` | int / float / null |
| `maven_pulse_source` | str / null |
| `maven_current_spend_request_cad` | float |
| `maven_current_spend_approved` | bool |
| `t2125_ad_deduction_note` | str |

## Spend-gate semantics (the rule Maven enforces)

```
spend_gate = "frozen"  if liquid_cad < montreal_floor_target_cad * 0.5
spend_gate = "tight"   if liquid_cad < montreal_floor_target_cad
                       OR concentration_risk_single_client_pct >= 70
spend_gate = "open"    otherwise
```

```
approved_ad_spend_monthly_cap_cad =
  0                          if gate == "frozen"
  100                        if gate == "tight"
  clamp(0.15 * mrr_cad, 500, 2000)  if gate == "open"
```

## Maven contract surface

Maven reads these specific paths (verified against
`C:\Users\User\CMO-Agent\scripts\send_gateway.py:check_cfo_spend_gate`):

```python
pulse["updated_at"]                                                   # staleness check
pulse["spend_gate"]["status"]                                         # must be "open"
pulse["spend_gate"]["approvals"][channel][brand]["daily_budget_usd"]  # daily USD cap
```

Maven also (lower priority) consumes for context:

```python
pulse["liquid_cad"]
pulse["concentration_risk_single_client_pct"]
```

Any rename of these paths is a breaking change. Bump `schema_version`.

## Canonical reader snippet (for Maven to copy)

```python
import json
from datetime import datetime, timezone
from pathlib import Path

CFO_PULSE = Path(r"C:\Users\User\APPS\CFO-Agent\data\pulse\cfo_pulse.json")
STALE_HOURS = 24

def can_spend(channel: str, brand: str, amount_usd: float) -> tuple[bool, str]:
    if not CFO_PULSE.exists():
        return False, "cfo_pulse.json missing — fail closed"
    pulse = json.loads(CFO_PULSE.read_text(encoding="utf-8"))
    when = datetime.fromisoformat(pulse["updated_at"])
    age_h = (datetime.now(when.tzinfo) - when).total_seconds() / 3600
    if age_h > STALE_HOURS:
        return False, f"pulse stale ({age_h:.1f}h)"
    sg = pulse.get("spend_gate") or {}
    if sg.get("status") != "open":
        return False, f"gate={sg.get('status')!r}"
    cap = (sg.get("approvals", {})
              .get(channel, {})
              .get(brand)
              or sg.get("approvals", {}).get(channel, {}).get("*") or {})
    daily = cap.get("daily_budget_usd", 0)
    if daily <= 0:
        return False, f"{channel}/{brand} cap is $0"
    if amount_usd > daily:
        return False, f"{amount_usd} > daily cap {daily}"
    return True, "ok"
```

## Example payload (live as of 2026-04-25)

```json
{
  "agent": "atlas",
  "updated_at": "2026-04-25T23:23:29-04:00",
  "liquid_cad": 7166.84,
  "liquid_source": "live API reads (n=8) + manual entries (n=5)",
  "montreal_floor_target_cad": 10000.0,
  "montreal_floor_gap_cad": 2833.16,
  "tax_reserve_required_cad": 3064.01,
  "tax_reserve_rate_pct": 25,
  "concentration_risk_single_client_pct": 94.0,
  "concentration_risk_client": "Bennett",
  "mrr_usd_from_bravo": 2982.0,
  "mrr_cad_from_bravo": 4085.34,
  "spend_gate": "tight",
  "spend_gate_reason": "Below Montreal floor by $2,833; Single-client concentration at 94%",
  "approved_ad_spend_monthly_cap_cad": 100,
  "approved_ad_spend_rule": "experimentation_only"
}
```

## Validating from the CLI

```bash
python -m cfo.pulse_schema                 # validates default path
python -m cfo.pulse_schema /tmp/pulse.json # validates a specific file
```

Exit code: 0 on pass, 1 on schema violation, 2 on missing file.

## Failure modes Maven should handle

| Condition | Behavior |
|-----------|----------|
| File missing | Fail closed: spend cap = 0 |
| JSON malformed | Fail closed |
| Schema violation | Fail closed + alert CC (Atlas wrote a bad pulse) |
| Stale > 24h | Fail closed: pulse is stale, demand fresh publish |
| `spend_gate == "frozen"` | Cap = 0 |
| Atlas down | Maven holds at the last fresh state until staleness threshold; then fails closed |

## Versioning

This is contract v1. Future revisions add a `schema_version` field at the
top of the document. Until then, breaking changes require simultaneous
deploy of `cfo/pulse_schema.py` here AND Maven's reader.
