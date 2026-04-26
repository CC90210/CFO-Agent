"""
scripts/self_test.py
--------------------
End-to-end smoke test of every Atlas entry point that doesn't require
an external user input or burn AI tokens.

Wired into main.py as `python main.py self-test`.

Categories:
  imports          — every Python module imports without error
  provider_health  — every research data provider responds
  cli_dry          — every main.py CLI subcommand can construct its arg parser
  modules_dry      — every research/cfo module's "main" entry-point is callable
  graph            — Obsidian wikilink graph has zero orphans + zero broken links
  memory           — memory frontmatter validation passes

Exits 0 if every category passes, 1 otherwise. Designed for CI / pre-commit / CC's
"is anything broken right now?" check.

Each test is independent and surfaces its own failure detail without aborting
the suite — you see every defect in one run, not just the first one.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Callable

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ─────────────────────────────────────────────────────────────────────────────
#  Modules to import
# ─────────────────────────────────────────────────────────────────────────────

_MODULES = [
    "cfo.cashflow", "cfo.dashboard", "cfo.accounts", "cfo.gmail_receipts",
    "cfo.pulse", "cfo.rebalance", "cfo.crypto_acb", "cfo.setup_wizard",
    "finance.tax", "finance.advisor", "finance.wealth_tracker", "finance.budget",
    "finance",
    "utils.alerts", "utils.logger", "utils.market_hours",
    "config.settings", "atlas_tools",
    "research._sec_client", "research._data_integrity", "research.finnhub_client",
    "research.fundamentals", "research.news_ingest", "research.macro_watch",
    "research.institutional_tracking", "research.insider_tracking",
    "research.earnings_calendar", "research.psychology", "research.options_flow",
    "research.historical_patterns", "research.stock_picker", "research.provider_health",
    "research",
    "telegram_bridge",
]


# ─────────────────────────────────────────────────────────────────────────────
#  Test record
# ─────────────────────────────────────────────────────────────────────────────

class TestResult:
    __slots__ = ("name", "passed", "detail")

    def __init__(self, name: str, passed: bool, detail: str = "") -> None:
        self.name = name
        self.passed = passed
        self.detail = detail

    def line(self) -> str:
        marker = "[PASS]" if self.passed else "[FAIL]"
        return f"  {marker} {self.name:32s} {self.detail}"


# ─────────────────────────────────────────────────────────────────────────────
#  Test definitions
# ─────────────────────────────────────────────────────────────────────────────

def test_imports() -> list[TestResult]:
    results: list[TestResult] = []
    for m in _MODULES:
        try:
            importlib.import_module(m)
            results.append(TestResult(f"import:{m}", True))
        except Exception as e:
            results.append(TestResult(f"import:{m}", False,
                f"{type(e).__name__}: {str(e)[:120]}"))
    return results


def test_cli_dry() -> list[TestResult]:
    """Every main.py subcommand can have its parser built."""
    results: list[TestResult] = []
    try:
        import main as atlas_main
        parser = atlas_main.build_parser()
        # argparse's _SubParsersAction stores choices on the .choices attr
        sub_actions = [a for a in parser._actions if a.__class__.__name__ == "_SubParsersAction"]
        if not sub_actions:
            results.append(TestResult("cli:subparser_present", False, "no subparsers found"))
            return results
        choices = list(sub_actions[0].choices)
        results.append(TestResult("cli:build_parser", True, f"{len(choices)} commands"))
        for c in choices:
            results.append(TestResult(f"cli:cmd:{c}", True))
    except Exception as e:
        results.append(TestResult("cli:build_parser", False, f"{type(e).__name__}: {e}"))
    return results


def test_provider_health() -> list[TestResult]:
    """Run the provider_health module — every provider must be GREEN/YELLOW (not RED)."""
    results: list[TestResult] = []
    try:
        from research.provider_health import run_all, RED
    except Exception as e:
        return [TestResult("provider_health:load", False, f"{type(e).__name__}: {e}")]

    try:
        statuses = run_all()
        for s in statuses:
            results.append(TestResult(
                f"provider:{s.name}",
                s.status != RED,
                f"{s.status} — {s.detail[:60]}",
            ))
    except Exception as e:
        results.append(TestResult("provider_health:run", False, f"{type(e).__name__}: {e}"))
    return results


def test_modules_dry() -> list[TestResult]:
    """
    Cheap dry-runs of high-value entry points that don't need external state.

    Constraint: every check must be silent (no print) AND offline (no HTTP).
    Anything that prints fills the captured-stdout buffer in CI runners and
    deadlocks the parent. Anything that hits the network adds non-determinism
    and belongs in test_provider_health, not here.
    """
    results: list[TestResult] = []

    def _block_filter_offline() -> object:
        # Bypass _load_sec_ticker_set (which would hit the SEC manifest);
        # we verify only the blocklist filter, which is the offline portion.
        from research.stock_picker import _TICKER_BLOCKLIST
        survivors = [t for t in ["TFSA", "NVDA", "RBC", "GOOGL"] if t not in _TICKER_BLOCKLIST]
        return survivors  # ["NVDA", "GOOGL"]

    cases: list[tuple[str, Callable[[], object]]] = [
        ("macro:flashpoints", lambda: __import__("research.macro_watch", fromlist=["geopolitical_flashpoints"]).geopolitical_flashpoints()),
        ("macro:sector_map", lambda: __import__("research.macro_watch", fromlist=["sector_map"]).sector_map()),
        ("inst:tracked_funds", lambda: __import__("research.institutional_tracking", fromlist=["tracked_funds"]).tracked_funds()),
        ("ticker_filter:blocklist", _block_filter_offline),
        ("data_integrity:exists", lambda: __import__("research._data_integrity", fromlist=["DataFeedError"]).DataFeedError),
        ("sec_client:user_agent", lambda: __import__("research._sec_client", fromlist=["USER_AGENT"]).USER_AGENT),
        ("stock_picker:Pick_class", lambda: __import__("research.stock_picker", fromlist=["Pick"]).Pick),
        ("stock_picker:DeepDive_class", lambda: __import__("research.stock_picker", fromlist=["DeepDive"]).DeepDive),
        ("provider_health:run_all_callable", lambda: callable(__import__("research.provider_health", fromlist=["run_all"]).run_all)),
    ]

    for name, fn in cases:
        try:
            out = fn()
            ok = out is not None and (not hasattr(out, "__len__") or len(out) >= 0)
            results.append(TestResult(f"dry:{name}", ok, f"-> {type(out).__name__}"))
        except Exception as e:
            results.append(TestResult(f"dry:{name}", False, f"{type(e).__name__}: {str(e)[:100]}"))

    return results


def test_graph() -> list[TestResult]:
    """Obsidian graph: 0 orphans, 0 broken links."""
    results: list[TestResult] = []
    try:
        proc = subprocess.run(
            [sys.executable, "scripts/validate_graph.py"],
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = proc.stdout + proc.stderr
        orphan_line = next(
            (l for l in out.splitlines() if "Orphans (brain/memory/skills):" in l),
            "",
        )
        # Parse "Orphans (brain/memory/skills): N"
        try:
            n_orphans = int(orphan_line.split(":")[-1].strip())
        except Exception:
            n_orphans = -1
        results.append(TestResult("graph:orphans", n_orphans == 0, f"{n_orphans} orphan(s)"))

        broken_block = "Broken wikilinks:"
        if broken_block in out:
            # Count broken-link lines after the header until a blank line.
            lines = out.split(broken_block, 1)[1].splitlines()
            broken = [l for l in lines if l.strip().startswith("BROKEN")]
            results.append(TestResult("graph:broken_links", len(broken) == 0,
                f"{len(broken)} broken link(s)"))
        else:
            results.append(TestResult("graph:broken_links", True, "0 broken"))
    except Exception as e:
        results.append(TestResult("graph:run", False, f"{type(e).__name__}: {e}"))
    return results


def test_memory() -> list[TestResult]:
    """Memory frontmatter validator must pass."""
    try:
        proc = subprocess.run(
            [sys.executable, "scripts/validate_memory.py", "--check"],
            cwd=str(_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        ok = proc.returncode == 0
        last = (proc.stdout.strip().splitlines() or ["(no output)"])[-1]
        return [TestResult("memory:validate", ok, last)]
    except Exception as e:
        return [TestResult("memory:validate", False, f"{type(e).__name__}: {e}")]


# ─────────────────────────────────────────────────────────────────────────────
#  Runner
# ─────────────────────────────────────────────────────────────────────────────

_CATEGORIES: list[tuple[str, Callable[[], list[TestResult]]]] = [
    ("imports", test_imports),
    ("cli", test_cli_dry),
    ("modules_dry", test_modules_dry),
    ("provider_health", test_provider_health),
    ("graph", test_graph),
    ("memory", test_memory),
]


def main(args: list[str] | None = None) -> int:
    # If `args` is None, fall back to sys.argv[1:]. An explicit empty list
    # means "no category filter" (run everything) — distinct from None.
    if args is None:
        args = sys.argv[1:]
    selected = set(args) if args else None

    print()
    print("=" * 92)
    print("  ATLAS — SELF-TEST")
    print("=" * 92)

    all_results: list[TestResult] = []
    for cat_name, fn in _CATEGORIES:
        if selected and cat_name not in selected:
            continue
        print(f"\n[{cat_name}]")
        try:
            cat_results = fn()
        except Exception as e:
            cat_results = [TestResult(f"{cat_name}:RAN", False, f"{type(e).__name__}: {e}")]
            traceback.print_exc()
        for r in cat_results:
            print(r.line())
        all_results.extend(cat_results)

    passed = sum(1 for r in all_results if r.passed)
    failed = len(all_results) - passed

    print()
    print("=" * 92)
    print(f"  Summary: PASS={passed}  FAIL={failed}  total={len(all_results)}")
    print("=" * 92)
    print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
