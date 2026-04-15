"""
cfo/rebalance.py
----------------
Portfolio rebalancing recommendations for Atlas.

Reads:
  data/manual_balances.json      -- manually-maintained balances (always)
  data/target_allocation.json    -- target % by category (created on first run)
  cfo.accounts.all_balances()    -- live Kraken + OANDA + Wise (if APIs configured)

Logic:
  - Aggregates all balances by category into total CAD values
  - Compares current % vs target % per category
  - Recommends BUY/SELL actions for categories drifted beyond the threshold
  - Respects exit-plan bias: if USER.md contains exit-plan indicators, flags
    TFSA/FHSA-held and liquid assets as preferred over corporate/illiquid
  - Minimum drift threshold (default 5%) prevents noise trades

CLI:
  python main.py rebalance                    # dry run, default 5% threshold
  python main.py rebalance --threshold 10     # only flag drift > 10%
  python main.py rebalance --no-live          # skip live API fetches

Category mapping (matches data/manual_balances.json + target_allocation.json):
  cash        -- chequing, savings, Wise, short-term float
  crypto      -- Kraken, Wealthsimple Crypto, OANDA (treated as speculative)
  registered  -- TFSA, RRSP, FHSA (account type, not asset class — still categorized)
  equity      -- OANDA equity, stock brokers (non-registered)
  business    -- Stripe, business accounts
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_MANUAL_BALANCES = _ROOT / "data" / "manual_balances.json"
_TARGET_ALLOC = _ROOT / "data" / "target_allocation.json"
_USER_MD = _ROOT / "brain" / "USER.md"

# Default target allocation written on first run
_DEFAULT_TARGET: dict[str, float] = {
    "cash":       0.10,   # 10% cash / short-term float
    "crypto":     0.10,   # 10% speculative / crypto
    "registered": 0.50,   # 50% growth in registered accounts (TFSA/RRSP/FHSA)
    "equity":     0.20,   # 20% non-registered equities / trading accounts
    "business":   0.10,   # 10% business float (Stripe, etc.)
}

# Category display names
_CATEGORY_LABELS: dict[str, str] = {
    "cash":       "Cash & Equivalents",
    "crypto":     "Crypto / Speculative",
    "registered": "Registered Accounts (TFSA/RRSP/FHSA)",
    "equity":     "Equities & Trading",
    "business":   "Business Float",
}

# FX fallback (CAD per unit)
_DEFAULT_FX: dict[str, float] = {
    "USD": 1.37,
    "EUR": 1.48,
    "GBP": 1.73,
    "CAD": 1.0,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CategoryPosition:
    """Current holdings in one category."""
    category: str
    label: str
    value_cad: float
    current_pct: float
    target_pct: float
    drift_pct: float   # current_pct - target_pct (positive = overweight)
    accounts: list[str]   # contributing platform + account names


@dataclass
class RebalanceAction:
    """A single recommended rebalance trade."""
    direction: str   # "BUY" or "SELL"
    category: str
    label: str
    amount_cad: float
    current_pct: float
    target_pct: float
    drift_pct: float
    exit_plan_note: str   # empty unless exit-plan bias applies


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_cad(amount: float, currency: str) -> float:
    """Convert amount to CAD using fallback FX rates."""
    rate = _DEFAULT_FX.get(currency.upper(), 1.0)
    return amount * rate


def _load_target() -> dict[str, float]:
    """
    Load data/target_allocation.json.
    Creates the file with defaults if it does not exist.
    """
    if not _TARGET_ALLOC.exists():
        _TARGET_ALLOC.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "_comment": (
                "Edit these percentages to match your target allocation. "
                "Values must sum to 1.0. Categories: cash, crypto, registered, equity, business."
            ),
            "as_of": date.today().isoformat(),
            "allocations": _DEFAULT_TARGET,
        }
        with _TARGET_ALLOC.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        _print(f"  Created default target allocation: {_TARGET_ALLOC}")

    with _TARGET_ALLOC.open(encoding="utf-8") as fh:
        raw = json.load(fh)

    allocations: dict[str, float] = raw.get("allocations", raw)
    # Strip _comment and as_of if present
    allocations = {k: v for k, v in allocations.items()
                   if isinstance(v, (int, float))}

    total = sum(allocations.values())
    if total <= 0:
        raise ValueError("target_allocation.json: allocations sum to 0")
    # Normalise to 1.0 in case of rounding
    return {k: v / total for k, v in allocations.items()}


def _load_manual_balances() -> list[dict[str, Any]]:
    """Load data/manual_balances.json. Returns empty list if file missing."""
    if not _MANUAL_BALANCES.exists():
        _print(f"  [WARN] {_MANUAL_BALANCES} not found — run `python main.py setup` first")
        return []
    with _MANUAL_BALANCES.open(encoding="utf-8") as fh:
        raw = json.load(fh)
    return raw.get("balances", [])


def _fetch_live_balances() -> list[dict[str, Any]]:
    """
    Attempt to fetch live balances from configured APIs.
    Returns list of dicts with keys: platform, account, amount, currency, category.
    Degrades gracefully if APIs are unconfigured or unavailable.
    """
    try:
        from cfo.accounts import all_balances
        live = all_balances()
        return [
            {
                "platform": b.platform,
                "account": b.account,
                "amount": b.amount,
                "currency": b.currency,
                "category": b.category,
                "notes": b.notes,
            }
            for b in live
        ]
    except Exception as exc:
        _print(f"  [WARN] Live balance fetch failed: {exc}")
        return []


def _has_exit_plan() -> bool:
    """
    Return True if USER.md contains exit-plan language indicating the user
    plans to change tax residency within a few years.
    """
    if not _USER_MD.exists():
        return False
    try:
        content = _USER_MD.read_text(encoding="utf-8", errors="ignore").lower()
        triggers = [
            "exit plan", "exit window", "departure tax", "crown dependencies",
            "isle of man", "irish passport", "relocate", "uk move",
        ]
        return any(t in content for t in triggers)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Core rebalancer
# ---------------------------------------------------------------------------

class Rebalancer:
    """
    Compute current vs target allocation and produce rebalance recommendations.

    Parameters
    ----------
    threshold_pct : Minimum drift (%) before a recommendation is generated.
                    Default 5.0 means categories within 5% of target are left alone.
    use_live      : If True, fetch live balances from exchange APIs.
    """

    def __init__(
        self,
        threshold_pct: float = 5.0,
        use_live: bool = True,
    ) -> None:
        self._threshold = threshold_pct / 100.0
        self._use_live = use_live

    def run(self) -> int:
        """Execute and print rebalancing report. Returns 0."""
        target = _load_target()
        manual = _load_manual_balances()
        live: list[dict[str, Any]] = []
        if self._use_live:
            live = _fetch_live_balances()

        # Merge: prefer live entries if the same platform+account is present in both
        all_entries = self._merge(manual, live)

        if not all_entries:
            _print("No balance data found. Run `python main.py setup` to configure.")
            return 0

        # Aggregate by category
        cat_values: dict[str, float] = {cat: 0.0 for cat in target}
        cat_accounts: dict[str, list[str]] = {cat: [] for cat in target}
        other_total = 0.0

        for entry in all_entries:
            cad = _to_cad(entry.get("amount", 0.0), entry.get("currency", "CAD"))
            cat = entry.get("category", "cash")
            label = f"{entry.get('platform', '?')}/{entry.get('account', '?')}"
            if cat in cat_values:
                cat_values[cat] += cad
                cat_accounts[cat].append(f"{label}: ${cad:,.0f}")
            else:
                other_total += cad

        total_cad = sum(cat_values.values()) + other_total
        if total_cad <= 0:
            _print("Total portfolio value is zero — nothing to rebalance.")
            return 0

        # Build positions
        positions: list[CategoryPosition] = []
        for cat, target_pct in target.items():
            value = cat_values.get(cat, 0.0)
            current_pct = value / total_cad
            drift = current_pct - target_pct
            positions.append(CategoryPosition(
                category=cat,
                label=_CATEGORY_LABELS.get(cat, cat),
                value_cad=value,
                current_pct=current_pct,
                target_pct=target_pct,
                drift_pct=drift,
                accounts=cat_accounts.get(cat, []),
            ))

        # Compute actions
        exit_plan = _has_exit_plan()
        actions = self._compute_actions(positions, total_cad, exit_plan)

        self._print_report(positions, actions, total_cad, exit_plan)
        return 0

    def _compute_actions(
        self,
        positions: list[CategoryPosition],
        total_cad: float,
        exit_plan: bool,
    ) -> list[RebalanceAction]:
        actions: list[RebalanceAction] = []
        for pos in positions:
            if abs(pos.drift_pct) <= self._threshold:
                continue

            direction = "SELL" if pos.drift_pct > 0 else "BUY"
            amount = abs(pos.drift_pct) * total_cad

            exit_note = ""
            if exit_plan:
                if direction == "BUY" and pos.category == "registered":
                    exit_note = (
                        "[EXIT PLAN] Prioritize TFSA/FHSA for new contributions"
                        " - registered assets are liquid and leave Canada cleanly"
                    )
                elif direction == "SELL" and pos.category in ("equity", "business"):
                    exit_note = (
                        "[EXIT PLAN] Consider reducing non-registered/corporate"
                        " positions before departure to simplify departure tax calc"
                    )

            actions.append(RebalanceAction(
                direction=direction,
                category=pos.category,
                label=pos.label,
                amount_cad=amount,
                current_pct=pos.current_pct,
                target_pct=pos.target_pct,
                drift_pct=pos.drift_pct,
                exit_plan_note=exit_note,
            ))

        # Sort: SELLs first (free up cash before buying)
        actions.sort(key=lambda a: (0 if a.direction == "SELL" else 1, -abs(a.drift_pct)))
        return actions

    def _print_report(
        self,
        positions: list[CategoryPosition],
        actions: list[RebalanceAction],
        total_cad: float,
        exit_plan: bool,
    ) -> None:
        w = 72
        today = date.today().isoformat()
        _print("")
        _print("=" * w)
        _print(f"  ATLAS -- PORTFOLIO REBALANCE REPORT | {today}")
        _print("=" * w)
        _print(f"  Total Portfolio:  ${total_cad:>12,.2f} CAD")
        _print(f"  Drift Threshold:  {self._threshold * 100:.1f}%")
        if exit_plan:
            _print("  Exit Plan:        ACTIVE (biasing toward TFSA/FHSA liquid assets)")
        _print("")
        _print(f"  {'CATEGORY':<36} {'CURRENT':>8} {'TARGET':>8} {'DRIFT':>8} {'VALUE':>14}")
        _print("  " + "-" * 76)

        for pos in sorted(positions, key=lambda p: abs(p.drift_pct), reverse=True):
            drift_str = f"{pos.drift_pct * 100:+.1f}%"
            flag = " *" if abs(pos.drift_pct) > self._threshold else "  "
            _print(
                f"{flag} {pos.label:<36} "
                f"{pos.current_pct * 100:>7.1f}% "
                f"{pos.target_pct * 100:>7.1f}% "
                f"{drift_str:>8} "
                f"${pos.value_cad:>13,.2f}"
            )

        _print("")
        if not actions:
            _print("  No rebalancing required. All categories within threshold.")
        else:
            _print(f"  RECOMMENDED ACTIONS ({len(actions)}):")
            _print("")
            for i, action in enumerate(actions, 1):
                _print(f"  {i}. {action.direction} ${action.amount_cad:>10,.2f} CAD "
                       f"of {action.label}")
                _print(f"     Current: {action.current_pct * 100:.1f}%  ->  "
                       f"Target: {action.target_pct * 100:.1f}%  "
                       f"(drift: {action.drift_pct * 100:+.1f}%)")
                if action.exit_plan_note:
                    _print(f"     {action.exit_plan_note}")
                _print("")

        _print("  * Marked categories exceed drift threshold")
        _print("=" * w)
        _print("")
        _print("  ACCOUNT BREAKDOWN:")
        for pos in positions:
            if pos.accounts:
                _print(f"  {pos.label}:")
                for acct in pos.accounts[:5]:
                    _print(f"    - {acct}")
                if len(pos.accounts) > 5:
                    _print(f"    ... and {len(pos.accounts) - 5} more")
        _print("")
        _print("  Edit data/target_allocation.json to customize target percentages.")
        _print("  This is a dry run. No trades have been executed.")

    @staticmethod
    def _merge(
        manual: list[dict[str, Any]],
        live: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Merge manual and live balances.
        Live entries win when they match the same platform+account pair,
        preventing double-counting.
        """
        if not live:
            return manual

        # Index live entries by (platform.lower(), account.lower())
        live_index: set[tuple[str, str]] = {
            (e.get("platform", "").lower(), e.get("account", "").lower())
            for e in live
        }

        # Keep manual entries not covered by live
        filtered_manual = [
            e for e in manual
            if (e.get("platform", "").lower(), e.get("account", "").lower())
            not in live_index
        ]

        return filtered_manual + live


# ---------------------------------------------------------------------------
# CLI entry (python -m cfo.rebalance)
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="rebalance",
        description="Portfolio rebalancing recommendations based on target_allocation.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Target allocation is read from data/target_allocation.json.\n"
            "File is created with defaults (10% cash, 10% crypto, 50% registered,\n"
            "20% equity, 10% business) on first run. Edit to customize."
        ),
    )
    ap.add_argument(
        "--threshold", type=float, default=5.0,
        help="Minimum drift %% before recommending action (default: 5.0)",
    )
    ap.add_argument(
        "--no-live", action="store_true",
        help="Skip live API fetches, use manual_balances.json only",
    )
    ap.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Print recommendations only, no trades executed (default: always true)",
    )
    args = ap.parse_args()

    rebalancer = Rebalancer(
        threshold_pct=args.threshold,
        use_live=not args.no_live,
    )
    return rebalancer.run()


def _print(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
