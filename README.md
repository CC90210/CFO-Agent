# ATLAS — CC's CFO Agent

> Tax strategist. Accountant. Research analyst. Stockbroker.
> Not an auto-trader.

## What this is

ATLAS is Conaugh McKenna's personal CFO agent. It:

- **Tracks net worth** across Kraken, OANDA, Wise, Stripe, Wealthsimple, RBC
- **Models cashflow** and runway (Montreal move scenarios)
- **Pulls Gmail receipts** from `conaugh@oasisai.work` → CSV ready for T2125
- **Prepares Canadian taxes** (T2125 sole-prop, CCPC planning, Crown Dependencies migration path)
- **Researches stocks on demand** — deep qualitative + quantitative, macro-aware, with entry/exit/why
- **Writes nothing to exchanges.** CC places trades manually. Atlas advises, CC decides.

## Quick start

```bash
python main.py runway                        # Montreal runway (3 scenarios)
python main.py networth                      # Live net-worth snapshot
python main.py receipts --since 2026-01-01   # Pull 2026 YTD receipts
python main.py picks "AI infra 6-12 months"  # Stock picks on demand
python main.py deepdive NVDA                 # Deep dive on one ticker
python main.py taxes                         # Quarterly tax-reserve check
```

## Architecture

```
cfo/         Cashflow, net-worth dashboard, Gmail receipts, account readers
research/    News ingest, macro watch, fundamentals, stock picker (Claude Opus 4.6)
finance/     Tax calculator, wealth tracker, budget, advisor
brain/       CC's financial identity (USER.md, SOUL.md, STATE.md)
skills/      16 CFO skills
docs/        59-doc tax library (~80K lines) — the moat
memory/      Operational intelligence
archive/     Archived trading automation (recoverable)
```

## Configuration

Copy `.env.example` to `.env`. Required:

- `ANTHROPIC_API_KEY` — research + stock picker
- `GMAIL_USER` + `GMAIL_APP_PASSWORD` — Google Workspace app password
- `EXCHANGE_API_KEY` / `EXCHANGE_SECRET` — Kraken (balance reads)
- `OANDA_TOKEN` / `OANDA_ACCOUNT_ID` — OANDA (balance reads)
- Placeholders for Stripe + Wise + research APIs

All research APIs are **free tier** by default. Paid upgrades in `research/README.md`.

## The pivot (2026-04-14)

Originally an algorithmic trading agent (12 strategies, backtests, paper/live, Darwinian engine). On 2026-04-14 CC pivoted it to CFO + research. Trading automation archived in `archive/trading-automation/`.

## Development

```bash
pip install -r requirements.txt
python -c "import cfo.dashboard, research.stock_picker"
```

Commits: `atlas: type — description`

## Safety

- `.env` is gitignored
- Atlas does not execute trades
- Atlas does not give legal advice. CC files via NETFILE.
- Conviction scores are probabilistic. No guarantees.
