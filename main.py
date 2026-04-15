"""
main.py
-------
ATLAS — CC's CFO agent. CLI entry point.

ATLAS is CC's CFO: accountant, tax strategist, research analyst, stockbroker.
Not an auto-trader. Research and advice, not automation.

Commands
--------
  runway           Montreal cashflow model (3 scenarios: pessimistic / realistic / optimistic)
  networth         Live net-worth snapshot (Kraken + OANDA + Wise + Stripe + manual)
  receipts         Pull latest Gmail receipts and export CSV for T2125
  picks            Generate stock picks on demand (deep research + entry/exit/why)
  deepdive TICKER  Full bull/bear/base deep dive on a single ticker
  taxes            Quick tax-reserve + installment check for this quarter

Usage
-----
  python main.py runway
  python main.py networth
  python main.py receipts --since 2026-01-01
  python main.py picks "AI infrastructure plays for 6-12 months"
  python main.py deepdive NVDA
  python main.py taxes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def cmd_runway(args: argparse.Namespace) -> int:
    from cfo.cashflow import main as cashflow_main
    cashflow_main()
    return 0


def cmd_networth(args: argparse.Namespace) -> int:
    from cfo.dashboard import print_dashboard
    print_dashboard()
    return 0


def cmd_receipts(args: argparse.Namespace) -> int:
    from cfo.gmail_receipts import GmailReceipts
    from datetime import date
    since = date.fromisoformat(args.since) if args.since else date(date.today().year, 1, 1)
    gr = GmailReceipts()
    gr.sync_tax_year(since=since)
    return 0


def cmd_picks(args: argparse.Namespace) -> int:
    from research.stock_picker import StockPickerAgent
    agent = StockPickerAgent()
    picks = agent.pick(args.query, n=args.n, horizon=args.horizon)
    for p in picks:
        print(p)
    return 0


def cmd_deepdive(args: argparse.Namespace) -> int:
    from research.stock_picker import StockPickerAgent
    agent = StockPickerAgent()
    dd = agent.deep_dive(args.ticker.upper())
    print(dd)
    return 0


def cmd_setup(args: argparse.Namespace) -> int:
    from cfo.setup_wizard import SetupWizard
    SetupWizard(non_interactive=getattr(args, "non_interactive", False)).run()
    return 0


def cmd_crypto_acb(args: argparse.Namespace) -> int:
    from cfo.crypto_acb import CryptoAcbReporter
    from pathlib import Path
    from datetime import date as _date

    reporter = CryptoAcbReporter(
        csv_path=Path(args.csv) if args.csv else None,
        year=args.year,
        export_path=Path(args.export) if args.export else None,
        summary_only=args.summary,
    )
    return reporter.run()


def cmd_rebalance(args: argparse.Namespace) -> int:
    from cfo.rebalance import Rebalancer
    rebalancer = Rebalancer(
        threshold_pct=args.threshold,
        use_live=not args.no_live,
    )
    return rebalancer.run()


def cmd_taxes(args: argparse.Namespace) -> int:
    from finance.tax import CryptoTaxCalculator
    from datetime import date
    from cfo.dashboard import networth_snapshot

    today = date.today()
    year = today.year
    quarter = (today.month - 1) // 3 + 1
    nw = networth_snapshot()

    print(f"\n{'=' * 68}")
    print(f"  ATLAS — TAX SNAPSHOT  |  Q{quarter} {year}  |  {today.isoformat()}")
    print(f"{'=' * 68}\n")

    print(f"  NET WORTH (CAD):  ${nw['total_cad']:>12,.2f}")
    print(f"  CASH ON HAND:     ${nw['by_category'].get('cash', 0):>12,.2f}")
    print()

    deadlines = {
        1: ("Mar 15 — Q4 prior-year installment", "Apr 30 — tax payment (all filers)"),
        2: ("Jun 15 — Q1 installment", "Jun 15 — self-employed return deadline"),
        3: ("Sep 15 — Q2 installment", None),
        4: ("Dec 15 — Q3 installment", None),
    }
    print("  KEY DEADLINES (CRA):")
    for d in deadlines[quarter]:
        if d:
            print(f"    *{d}")
    print()

    print("  RESERVES (rule of thumb for sole prop at ~$280K projected):")
    print("    *Set aside 25% of gross self-employment income for CPP+fed+ON tax")
    print("    *If TTM revenue > $30K: GST/HST filing required, registration mandatory")
    print("    *If TTM revenue > $80K: evaluate CCPC incorporation (12.2% vs 29.65%+)")
    print()

    print("  NEXT STEPS:")
    print("    1. Run `python main.py receipts --since 2026-01-01` monthly")
    print("    2. Export receipts CSV -> reconcile against Stripe + Wise")
    print("    3. File 2025 return by June 15, 2026 via Wealthsimple Tax -> NETFILE")
    print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="atlas", description="ATLAS — CC's CFO agent")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("runway", help="Montreal cashflow + runway scenarios").set_defaults(func=cmd_runway)
    sub.add_parser("networth", help="Live net-worth snapshot").set_defaults(func=cmd_networth)

    r = sub.add_parser("receipts", help="Pull Gmail receipts for T2125")
    r.add_argument("--since", help="ISO date YYYY-MM-DD (default: Jan 1 this year)")
    r.set_defaults(func=cmd_receipts)

    pk = sub.add_parser("picks", help="Generate stock picks with entry/exit/why")
    pk.add_argument("query", help='e.g. "AI infrastructure plays for 6-12 months"')
    pk.add_argument("-n", type=int, default=3, help="Number of picks (default 3)")
    pk.add_argument("--horizon", default="6-12 months")
    pk.set_defaults(func=cmd_picks)

    dd = sub.add_parser("deepdive", help="Deep dive on a single ticker")
    dd.add_argument("ticker")
    dd.set_defaults(func=cmd_deepdive)

    sub.add_parser("taxes", help="Quarterly tax reserve + installment check").set_defaults(func=cmd_taxes)

    # ── New CFO commands ─────────────────────────────────────────────────────
    setup_p = sub.add_parser("setup", help="Personalization wizard — writes brain/USER.md, .env, balances")
    setup_p.add_argument(
        "--non-interactive", action="store_true",
        help="Populate with demo data without reading from stdin (for testing)",
    )
    setup_p.set_defaults(func=cmd_setup)

    from datetime import date as _today_date
    acb_p = sub.add_parser("crypto-acb", help="Weighted-average ACB report for CRA T5008 filing")
    acb_p.add_argument("--year", type=int, default=_today_date.today().year,
                       help="Tax year to report (default: current year)")
    acb_p.add_argument("--csv", default=None,
                       help="Path to trade history CSV (default: data/crypto_trades.csv)")
    acb_p.add_argument("--export", default=None,
                       help="Write T5008 data to this CSV path")
    acb_p.add_argument("--summary", action="store_true",
                       help="Print totals only, no per-trade detail")
    acb_p.set_defaults(func=cmd_crypto_acb)

    reb_p = sub.add_parser("rebalance", help="Portfolio rebalancing recommendations")
    reb_p.add_argument("--threshold", type=float, default=5.0,
                       help="Minimum drift %% before recommending action (default: 5.0)")
    reb_p.add_argument("--no-live", action="store_true",
                       help="Skip live API fetches, use manual_balances.json only")
    reb_p.set_defaults(func=cmd_rebalance)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
