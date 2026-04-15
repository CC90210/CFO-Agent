"""
cfo/crypto_acb.py
-----------------
Weighted-average ACB (Adjusted Cost Base) report for CRA T5008 filing.

Expected CSV format (data/crypto_trades.csv)
--------------------------------------------
  date,exchange,symbol,side,quantity,price_cad,fee_cad,notes
  2024-01-15,Kraken,BTC,buy,0.005,45000.00,5.00,first purchase
  2024-03-20,Kraken,BTC,sell,0.002,52000.00,3.00,partial sale
  2024-06-01,Wealthsimple,ETH,buy,0.50,4200.00,2.50,diversifying

Column definitions:
  date        ISO date (YYYY-MM-DD) of the trade
  exchange    Platform name (Kraken, Wealthsimple, NDAX, etc.)
  symbol      Asset ticker (BTC, ETH, SOL, etc.)
  side        'buy' or 'sell'
  quantity    Number of units traded (positive float)
  price_cad   Price per unit in CAD at time of trade
  fee_cad     Total fees in CAD (0 if none)
  notes       Free-text label (optional)

CRA rules applied:
  - ACB method (weighted average): CRA IT-479R requires this for crypto
  - Fees increase ACB on buys; reduce proceeds on sells
  - 50% capital gains inclusion rate (sub-$250K net gain)
  - 66.67% inclusion rate on gains above $250K (effective June 25, 2024)
  - Superficial loss rule: 30-day re-buy flag (warning only — CRA GAAR may apply)
  - Business income warning when >= 30 dispositions in a year

Usage
-----
  python main.py crypto-acb
  python main.py crypto-acb --year 2025
  python main.py crypto-acb --year 2025 --export /tmp/t5008_2025.csv
  python main.py crypto-acb --summary
"""

from __future__ import annotations

import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_CSV = _ROOT / "data" / "crypto_trades.csv"

# Inclusion rates (matching finance/tax.py constants)
_INCLUSION_50 = 0.50
_INCLUSION_67 = 2 / 3
_GAIN_THRESHOLD = 250_000.0

# Business income warning threshold
_BUSINESS_TRADES = 30

# Superficial loss look-ahead window (days)
_SUPERFICIAL_WINDOW = 30


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class TradeRow:
    """One row from crypto_trades.csv."""

    __slots__ = ("date", "exchange", "symbol", "side", "quantity",
                 "price_cad", "fee_cad", "notes")

    def __init__(
        self,
        date_val: date,
        exchange: str,
        symbol: str,
        side: str,
        quantity: float,
        price_cad: float,
        fee_cad: float,
        notes: str,
    ) -> None:
        self.date = date_val
        self.exchange = exchange
        self.symbol = symbol.upper()
        self.side = side.lower()
        self.quantity = quantity
        self.price_cad = price_cad
        self.fee_cad = fee_cad
        self.notes = notes


# ---------------------------------------------------------------------------
# CSV loader
# ---------------------------------------------------------------------------

def load_trades(csv_path: Path) -> list[TradeRow]:
    """
    Parse crypto_trades.csv into a list of TradeRow objects.
    Skips blank lines and comment lines starting with '#'.
    Raises FileNotFoundError with a helpful message if file is missing.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Trade history not found: {csv_path}\n"
            f"Create it using the template at data/crypto_trades_template.csv\n"
            f"or copy from: python main.py crypto-acb --print-template"
        )

    rows: list[TradeRow] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        for line_num, raw_line in enumerate(fh, start=1):
            stripped = raw_line.strip()
            # Skip blanks and comment lines
            if not stripped or stripped.startswith("#"):
                continue
            # Skip header row
            if stripped.lower().startswith("date,"):
                continue

            try:
                reader = csv.reader([stripped])
                parts = next(reader)
                if len(parts) < 7:
                    _warn(f"Line {line_num}: expected 7+ columns, got {len(parts)} — skipped")
                    continue

                date_val = date.fromisoformat(parts[0].strip())
                exchange = parts[1].strip()
                symbol = parts[2].strip().upper()
                side = parts[3].strip().lower()
                quantity = float(parts[4].strip())
                price_cad = float(parts[5].strip())
                fee_cad = float(parts[6].strip()) if parts[6].strip() else 0.0
                notes = parts[7].strip() if len(parts) > 7 else ""

                if side not in ("buy", "sell"):
                    _warn(f"Line {line_num}: side must be 'buy' or 'sell', got '{side}' — skipped")
                    continue
                if quantity <= 0:
                    _warn(f"Line {line_num}: quantity must be > 0 — skipped")
                    continue
                if price_cad < 0:
                    _warn(f"Line {line_num}: price_cad must be >= 0 — skipped")
                    continue

                rows.append(TradeRow(
                    date_val=date_val,
                    exchange=exchange,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price_cad=price_cad,
                    fee_cad=fee_cad,
                    notes=notes,
                ))
            except (ValueError, StopIteration) as exc:
                _warn(f"Line {line_num}: parse error ({exc}) — skipped")
                continue

    return sorted(rows, key=lambda r: r.date)


# ---------------------------------------------------------------------------
# ACB engine
# ---------------------------------------------------------------------------

class AcbEngine:
    """
    Weighted-average ACB calculator for multiple crypto symbols.

    State is maintained in self._ledger so you can feed trades from
    multiple years and the ACB carry-forward remains accurate.
    """

    def __init__(self) -> None:
        # symbol -> {"units": float, "total_cost": float}
        self._ledger: dict[str, dict[str, float]] = {}

    def process(
        self,
        trades: list[TradeRow],
        tax_year: int,
    ) -> dict[str, Any]:
        """
        Process all trades and return a result dict for the given tax year.

        Returns
        -------
        {
          "dispositions": list of per-sell dicts,
          "acb_per_symbol": {symbol: acb_per_unit},
          "units_held": {symbol: units},
          "summary": TaxYearSummary dict,
          "superficial_loss_flags": list of warning strings,
        }
        """
        self._ledger.clear()

        all_sorted = sorted(trades, key=lambda r: r.date)
        dispositions: list[dict[str, Any]] = []
        superficial_flags: list[str] = []

        # Build a buy-date index for superficial loss detection
        buys_by_symbol: dict[str, list[date]] = {}
        for t in all_sorted:
            if t.side == "buy":
                buys_by_symbol.setdefault(t.symbol, []).append(t.date)

        total_proceeds = 0.0
        total_cost = 0.0
        capital_gains = 0.0
        capital_losses = 0.0
        sell_count = 0

        for trade in all_sorted:
            sym = trade.symbol
            self._ledger.setdefault(sym, {"units": 0.0, "total_cost": 0.0})

            if trade.side == "buy":
                cost = trade.quantity * trade.price_cad + trade.fee_cad
                self._ledger[sym]["units"] += trade.quantity
                self._ledger[sym]["total_cost"] += cost

            elif trade.side == "sell" and trade.date.year == tax_year:
                proceeds = trade.quantity * trade.price_cad - trade.fee_cad
                ledger = self._ledger[sym]
                acb_pu = (
                    ledger["total_cost"] / ledger["units"]
                    if ledger["units"] > 0 else 0.0
                )
                cost_basis = trade.quantity * acb_pu
                gain_loss = proceeds - cost_basis

                # Reduce ledger
                ledger["units"] = max(0.0, ledger["units"] - trade.quantity)
                ledger["total_cost"] = max(0.0, ledger["total_cost"] - cost_basis)

                sell_count += 1
                total_proceeds += proceeds
                total_cost += cost_basis

                if gain_loss >= 0:
                    capital_gains += gain_loss
                else:
                    capital_losses += abs(gain_loss)
                    # Check superficial loss: re-buy within 30 days
                    window_end = trade.date + timedelta(days=_SUPERFICIAL_WINDOW)
                    future_buys = [
                        d for d in buys_by_symbol.get(sym, [])
                        if trade.date < d <= window_end
                    ]
                    if future_buys:
                        superficial_flags.append(
                            f"SUPERFICIAL LOSS WARNING: {sym} sold at a loss on "
                            f"{trade.date} and repurchased on "
                            f"{', '.join(str(d) for d in future_buys[:3])} "
                            f"(within 30 days). CRA GAAR may disallow this loss. "
                            f"Loss: ${abs(gain_loss):,.2f} CAD."
                        )

                dispositions.append({
                    "date": trade.date.isoformat(),
                    "exchange": trade.exchange,
                    "symbol": sym,
                    "quantity": trade.quantity,
                    "price_cad": round(trade.price_cad, 4),
                    "proceeds_cad": round(proceeds, 2),
                    "acb_per_unit": round(acb_pu, 4),
                    "cost_basis_cad": round(cost_basis, 2),
                    "gain_loss_cad": round(gain_loss, 2),
                    "type": "GAIN" if gain_loss >= 0 else "LOSS",
                    "notes": trade.notes,
                    # T5008 fields
                    "t5008_box_131": round(proceeds, 2),
                    "t5008_box_132": round(cost_basis, 2),
                    "t5008_box_135": round(gain_loss, 2),
                })

        net_gain = capital_gains - capital_losses
        taxable_amount, inclusion_rate = _apply_inclusion(net_gain)

        is_business = sell_count >= _BUSINESS_TRADES
        business_warning = ""
        if is_business:
            business_warning = (
                f"{sell_count} dispositions in {tax_year} may trigger CRA business "
                f"income treatment (100% inclusion, not 50%). Consult a CPA."
            )

        summary = {
            "tax_year": tax_year,
            "disposition_count": sell_count,
            "total_proceeds_cad": round(total_proceeds, 2),
            "total_cost_basis_cad": round(total_cost, 2),
            "capital_gains_cad": round(capital_gains, 2),
            "capital_losses_cad": round(capital_losses, 2),
            "net_gain_cad": round(net_gain, 2),
            "inclusion_rate": round(inclusion_rate, 4),
            "taxable_amount_cad": round(taxable_amount, 2),
            "is_business_income_risk": is_business,
            "business_income_warning": business_warning,
        }

        acb_per_symbol = {
            sym: round(
                data["total_cost"] / data["units"] if data["units"] > 0 else 0.0, 4)
            for sym, data in self._ledger.items()
        }
        units_held = {sym: round(data["units"], 8) for sym, data in self._ledger.items()}

        return {
            "dispositions": dispositions,
            "acb_per_symbol": acb_per_symbol,
            "units_held": units_held,
            "summary": summary,
            "superficial_loss_flags": superficial_flags,
        }


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class CryptoAcbReporter:
    """CLI output and CSV export for the ACB calculation."""

    def __init__(
        self,
        csv_path: Path | None = None,
        year: int | None = None,
        export_path: Path | None = None,
        summary_only: bool = False,
    ) -> None:
        self._csv_path = csv_path or _DEFAULT_CSV
        self._year = year or date.today().year
        self._export_path = export_path
        self._summary_only = summary_only

    def run(self) -> int:
        """Main entry point. Returns 0 on success, 1 on error."""
        try:
            trades = load_trades(self._csv_path)
        except FileNotFoundError as exc:
            _print(str(exc))
            return 1

        if not trades:
            _print("No trades found in CSV file.")
            return 0

        engine = AcbEngine()
        result = engine.process(trades, self._year)
        summary = result["summary"]
        dispositions = result["dispositions"]
        acb_per_symbol = result["acb_per_symbol"]
        units_held = result["units_held"]
        flags = result["superficial_loss_flags"]

        self._print_summary(summary, acb_per_symbol, units_held)

        if not self._summary_only and dispositions:
            self._print_dispositions(dispositions)

        if flags:
            _print("")
            _print("SUPERFICIAL LOSS WARNINGS:")
            for f in flags:
                _print(f"  * {f}")

        if summary.get("business_income_warning"):
            _print("")
            _print("BUSINESS INCOME RISK:")
            _print(f"  * {summary['business_income_warning']}")

        if self._export_path:
            self._export_csv(dispositions, summary)
            _print(f"\nT5008 data exported to: {self._export_path}")

        _print("\nNOTE: Review with a CPA before filing. ACB calculations above are")
        _print("      based on the trades in your CSV file only.")
        return 0

    def _print_summary(
        self,
        summary: dict[str, Any],
        acb_per_symbol: dict[str, float],
        units_held: dict[str, float],
    ) -> None:
        w = 68
        year = summary["tax_year"]
        _print("")
        _print("=" * w)
        _print(f"  ATLAS -- CRYPTO ACB REPORT | TAX YEAR {year}")
        _print("=" * w)
        _print("")
        _print(f"  Dispositions:        {summary['disposition_count']:>8}")
        _print(f"  Total Proceeds:      ${summary['total_proceeds_cad']:>14,.2f} CAD")
        _print(f"  Total Cost Basis:    ${summary['total_cost_basis_cad']:>14,.2f} CAD")
        _print(f"  Capital Gains:       ${summary['capital_gains_cad']:>14,.2f} CAD")
        _print(f"  Capital Losses:      ${summary['capital_losses_cad']:>14,.2f} CAD")
        _print(f"  Net Gain / (Loss):   ${summary['net_gain_cad']:>14,.2f} CAD")
        _print(f"  Inclusion Rate:      {summary['inclusion_rate'] * 100:>13.1f}%")
        _print(f"  Taxable Amount:      ${summary['taxable_amount_cad']:>14,.2f} CAD")
        _print("")
        _print("  ACB PER SYMBOL (carry-forward into next year):")
        if acb_per_symbol:
            for sym, acb in sorted(acb_per_symbol.items()):
                held = units_held.get(sym, 0.0)
                if held > 0 or acb > 0:
                    _print(f"    {sym:<10}  ACB/unit: ${acb:>12,.4f} CAD  |  "
                           f"Units held: {held:.8g}")
        else:
            _print("    (no open positions)")
        _print("")
        _print("  SCHEDULE 3 INPUTS:")
        _print(f"    Line 197 (Proceeds):       ${summary['total_proceeds_cad']:>12,.2f}")
        _print(f"    Line 198 (ACB):            ${summary['total_cost_basis_cad']:>12,.2f}")
        _print(f"    Line 200 (Net Gain/Loss):  ${summary['net_gain_cad']:>12,.2f}")
        incl_pct = round(summary['inclusion_rate'] * 100)
        _print(f"    Line 230 (Taxable {incl_pct}%):    ${summary['taxable_amount_cad']:>12,.2f}")
        _print("=" * w)

    def _print_dispositions(self, dispositions: list[dict[str, Any]]) -> None:
        _print("")
        _print(f"  {'DATE':<12} {'SYM':<6} {'QTY':>10} {'PROCEEDS':>12} "
               f"{'ACB/UNIT':>10} {'COST BASIS':>12} {'GAIN/LOSS':>12} {'TYPE':<6}")
        _print("  " + "-" * 82)
        for d in dispositions:
            _print(
                f"  {d['date']:<12} {d['symbol']:<6} {d['quantity']:>10.6g} "
                f"${d['proceeds_cad']:>11,.2f} ${d['acb_per_unit']:>9,.4f} "
                f"${d['cost_basis_cad']:>11,.2f} ${d['gain_loss_cad']:>11,.2f} "
                f"{d['type']:<6}"
            )

    def _export_csv(
        self, dispositions: list[dict[str, Any]], summary: dict[str, Any]
    ) -> None:
        """Write T5008-formatted CSV."""
        if not self._export_path:
            return
        self._export_path.parent.mkdir(parents=True, exist_ok=True)
        with self._export_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow([
                "# ATLAS T5008 Export",
                f"Tax Year: {summary['tax_year']}",
                f"Generated: {date.today().isoformat()}",
            ])
            writer.writerow([
                "date", "exchange", "symbol", "quantity",
                "proceeds_cad", "acb_per_unit", "cost_basis_cad",
                "gain_loss_cad", "type",
                "t5008_box_131_proceeds", "t5008_box_132_acb", "t5008_box_135_gain_loss",
                "notes",
            ])
            for d in dispositions:
                writer.writerow([
                    d["date"], d["exchange"], d["symbol"], d["quantity"],
                    d["proceeds_cad"], d["acb_per_unit"], d["cost_basis_cad"],
                    d["gain_loss_cad"], d["type"],
                    d["t5008_box_131"], d["t5008_box_132"], d["t5008_box_135"],
                    d.get("notes", ""),
                ])
            writer.writerow([])
            writer.writerow(["# SUMMARY"])
            for k, v in summary.items():
                writer.writerow([k, v])


# ---------------------------------------------------------------------------
# Template generator
# ---------------------------------------------------------------------------

def write_template(path: Path) -> None:
    """Write a sample crypto_trades.csv with 3 example rows."""
    content = (
        "# ATLAS Crypto Trade History\n"
        "# Format: date,exchange,symbol,side,quantity,price_cad,fee_cad,notes\n"
        "#\n"
        "# date       : YYYY-MM-DD (trade date, not settlement)\n"
        "# exchange   : Kraken, Wealthsimple, Coinbase, etc.\n"
        "# symbol     : BTC, ETH, SOL, etc.\n"
        "# side       : buy or sell\n"
        "# quantity   : number of units (positive float)\n"
        "# price_cad  : price per unit in CAD at time of trade\n"
        "# fee_cad    : total fees in CAD (0 if none)\n"
        "# notes      : optional label\n"
        "#\n"
        "date,exchange,symbol,side,quantity,price_cad,fee_cad,notes\n"
        "2024-01-15,Kraken,BTC,buy,0.005,45000.00,5.00,first purchase\n"
        "2024-03-20,Kraken,BTC,sell,0.002,52000.00,3.00,partial profit taking\n"
        "2024-06-01,Wealthsimple,ETH,buy,0.50,4200.00,2.50,diversifying into ETH\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_inclusion(net_gain: float) -> tuple[float, float]:
    """Return (taxable_amount, inclusion_rate) matching CRA rules."""
    if net_gain <= 0:
        return 0.0, _INCLUSION_50
    if net_gain <= _GAIN_THRESHOLD:
        return net_gain * _INCLUSION_50, _INCLUSION_50
    lower = _GAIN_THRESHOLD * _INCLUSION_50
    upper = (net_gain - _GAIN_THRESHOLD) * _INCLUSION_67
    taxable = lower + upper
    return taxable, round(taxable / net_gain, 4)


def _warn(msg: str) -> None:
    sys.stderr.write(f"[crypto-acb] WARNING: {msg}\n")


def _print(msg: str) -> None:
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# CLI entry (python -m cfo.crypto_acb)
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="crypto-acb",
        description="Weighted-average ACB report for CRA T5008 filing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "CSV format: date,exchange,symbol,side,quantity,price_cad,fee_cad,notes\n"
            "Default CSV: data/crypto_trades.csv\n"
            "Template:   python main.py crypto-acb --print-template"
        ),
    )
    ap.add_argument(
        "--year", type=int, default=date.today().year,
        help="Tax year to report (default: current year)",
    )
    ap.add_argument(
        "--csv", default=str(_DEFAULT_CSV),
        help="Path to trade history CSV (default: data/crypto_trades.csv)",
    )
    ap.add_argument(
        "--export", default=None,
        help="Export T5008 data to this CSV path",
    )
    ap.add_argument(
        "--summary", action="store_true",
        help="Print totals only, no per-trade detail",
    )
    ap.add_argument(
        "--print-template", action="store_true",
        help="Write a sample crypto_trades.csv template and exit",
    )
    args = ap.parse_args()

    if args.print_template:
        tmpl = _ROOT / "data" / "crypto_trades_template.csv"
        write_template(tmpl)
        _print(f"Template written to: {tmpl}")
        return 0

    reporter = CryptoAcbReporter(
        csv_path=Path(args.csv),
        year=args.year,
        export_path=Path(args.export) if args.export else None,
        summary_only=args.summary,
    )
    return reporter.run()


if __name__ == "__main__":
    raise SystemExit(main())
