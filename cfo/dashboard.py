"""
CFO Dashboard — net-worth snapshot and ASCII table output.

Usage:
    python -m cfo.dashboard
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Any

from cfo.accounts import Balance, all_balances

# ---------------------------------------------------------------------------
# Category and platform ordering for display
# ---------------------------------------------------------------------------

CATEGORY_ORDER = ["cash", "registered", "crypto", "equity", "business"]
CATEGORY_LABELS = {
    "cash": "CASH",
    "registered": "REGISTERED ACCOUNTS",
    "crypto": "CRYPTO",
    "equity": "EQUITY / TRADING",
    "business": "BUSINESS",
}

# ---------------------------------------------------------------------------
# Flagging logic
# ---------------------------------------------------------------------------

_THRESHOLDS: dict[str, float] = {
    # T1135 trigger: combined foreign property cost > $100K CAD
    "t1135_warning": 100_000,
}


def _flag_issues(balances: list[Balance]) -> list[str]:
    issues: list[str] = []

    # Stale manual data warning (older than 14 days)
    manual = [b for b in balances if b.source == "manual"]
    if manual:
        oldest = min(b.as_of for b in manual)
        days_old = (datetime.now(timezone.utc) - oldest).days
        if days_old > 14:
            issues.append(
                f"Manual balances are {days_old} days old — update data/manual_balances.json"
            )

    # T1135 check: sum of non-CAD-origin cash (Wise + Kraken + Stripe)
    foreign_platforms = {"Wise", "Kraken", "Stripe"}
    foreign_cad = sum(
        b.amount for b in balances
        if b.platform in foreign_platforms and b.amount > 0
    )
    if foreign_cad >= _THRESHOLDS["t1135_warning"]:
        issues.append(
            f"T1135 threshold may be triggered — foreign property ~${foreign_cad:,.0f} CAD "
            f"(CRA requires T1135 if cost > $100K)"
        )

    # Zero registered accounts
    registered = [b for b in balances if b.category == "registered"]
    if all(b.amount == 0 for b in registered):
        issues.append("All registered accounts (TFSA/RRSP/FHSA) are at $0 — consider contributing")

    return issues


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------

def networth_snapshot(balances: list[Balance] | None = None) -> dict[str, Any]:
    """
    Returns:
        {
          "total_cad": float,
          "by_category": {category: float},
          "by_platform": {platform: float},
          "flagged_issues": [str],
          "as_of": str (ISO),
          "balances": list[Balance],
        }
    """
    if balances is None:
        balances = all_balances()

    by_category: dict[str, float] = {}
    by_platform: dict[str, float] = {}

    for b in balances:
        if b.amount <= 0:
            continue
        by_category[b.category] = by_category.get(b.category, 0.0) + b.amount
        by_platform[b.platform] = by_platform.get(b.platform, 0.0) + b.amount

    total_cad = sum(by_category.values())
    flagged = _flag_issues(balances)

    return {
        "total_cad": round(total_cad, 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "by_platform": {k: round(v, 2) for k, v in by_platform.items()},
        "flagged_issues": flagged,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "balances": balances,
    }


# ---------------------------------------------------------------------------
# ASCII table helpers
# ---------------------------------------------------------------------------

_COL_WIDTHS = (22, 24, 12, 8, 6, 30)
_HEADERS = ("Platform", "Account", "Amount (CAD)", "Ccy", "Src", "Notes")
_SEP = "  "


def _row(cols: tuple[str, ...]) -> str:
    parts = []
    for val, width in zip(cols, _COL_WIDTHS):
        parts.append(str(val)[:width].ljust(width))
    return _SEP.join(parts).rstrip()


def _divider(char: str = "-") -> str:
    return char * (sum(_COL_WIDTHS) + len(_SEP) * (len(_COL_WIDTHS) - 1))


def print_dashboard(balances: list[Balance] | None = None) -> None:
    """Print a grouped ASCII dashboard to stdout."""
    if balances is None:
        balances = all_balances()

    snapshot = networth_snapshot(balances)

    print()
    print("=" * 60)
    print("  ATLAS — CFO NET WORTH DASHBOARD")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"  {ts}")
    print("=" * 60)
    print()

    # Group by category
    by_cat: dict[str, list[Balance]] = {}
    for b in balances:
        by_cat.setdefault(b.category, []).append(b)

    print(_row(_HEADERS))
    print(_divider())

    categories_shown = [c for c in CATEGORY_ORDER if c in by_cat]
    # Add any categories not in the ordered list at the end
    for c in by_cat:
        if c not in categories_shown:
            categories_shown.append(c)

    grand_total = 0.0

    for cat in categories_shown:
        entries = by_cat[cat]
        label = CATEGORY_LABELS.get(cat, cat.upper())
        print()
        print(f"  [{label}]")

        cat_total = 0.0
        platform_totals: dict[str, float] = {}

        for b in sorted(entries, key=lambda x: (x.platform, x.account)):
            amount_str = f"{b.amount:>10,.2f}" if b.amount >= 0 else f"{b.amount:>10,.2f}"
            print(_row((
                b.platform,
                b.account,
                amount_str,
                "CAD",
                b.source[:3],
                b.notes[:30] if b.notes else "",
            )))
            if b.amount > 0:
                cat_total += b.amount
                platform_totals[b.platform] = platform_totals.get(b.platform, 0.0) + b.amount

        print(_divider("."))
        print(_row(("", f"  {label} subtotal", f"{cat_total:>10,.2f}", "CAD", "", "")))
        grand_total += cat_total

    print()
    print(_divider("="))
    print(_row(("", "  TOTAL NET WORTH", f"{grand_total:>10,.2f}", "CAD", "", "")))
    print(_divider("="))

    # By-platform summary
    print()
    print("  By Platform:")
    for platform, total in sorted(snapshot["by_platform"].items(), key=lambda x: -x[1]):
        bar_units = int(total / max(grand_total, 1) * 30)
        bar = "#" * bar_units
        pct = total / max(grand_total, 1) * 100
        print(f"    {platform:<18} {total:>10,.2f} CAD  {pct:5.1f}%  {bar}")

    # Flagged issues
    if snapshot["flagged_issues"]:
        print()
        print("  ATTENTION:")
        for issue in snapshot["flagged_issues"]:
            print(f"    ! {issue}")

    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print_dashboard()


if __name__ == "__main__":
    main()
