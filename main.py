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
    from cfo.cashflow import montreal_scenarios
    montreal_scenarios()
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


def cmd_taxes(args: argparse.Namespace) -> int:
    from finance.tax import quarterly_snapshot
    print(quarterly_snapshot())
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
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
