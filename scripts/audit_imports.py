"""scripts/audit_imports.py — import every Atlas module, report failures."""
from __future__ import annotations
import importlib
import sys
import traceback
from pathlib import Path

# Add the repo root to sys.path so `import cfo`, `import research`, etc. resolve.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


MODULES = [
    # cfo
    "cfo.cashflow", "cfo.dashboard", "cfo.accounts", "cfo.gmail_receipts",
    "cfo.pulse", "cfo.rebalance", "cfo.crypto_acb", "cfo.setup_wizard",
    # finance
    "finance.tax", "finance.advisor", "finance.wealth_tracker", "finance.budget",
    "finance",
    # utils + config
    "utils.alerts", "utils.logger", "utils.market_hours",
    "config.settings", "atlas_tools",
    # research
    "research._sec_client", "research._data_integrity", "research.finnhub_client",
    "research.fundamentals", "research.news_ingest", "research.macro_watch",
    "research.institutional_tracking", "research.insider_tracking",
    "research.earnings_calendar", "research.psychology", "research.options_flow",
    "research.historical_patterns", "research.stock_picker", "research.provider_health",
    "research",
    # entrypoints
    "telegram_bridge",
]


def main() -> int:
    fails = []
    for m in MODULES:
        try:
            importlib.import_module(m)
            print(f"OK  {m}", flush=True)
        except Exception as e:
            tb = traceback.format_exc(limit=3)
            fails.append((m, type(e).__name__, str(e)[:200], tb))
            print(f"FAIL {m}: {type(e).__name__}: {str(e)[:200]}", flush=True)
    print()
    print(f"Failures: {len(fails)} / {len(MODULES)}")
    for m, n, e, tb in fails:
        print(f"\n--- {m} ---")
        print(tb)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
