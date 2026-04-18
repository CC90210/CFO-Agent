---
description: "Net worth, runway, cashflow, accounts, Montreal move planning, burn rate, break-even analysis. Use for any money management or financial status question."
---
# Atlas CFO Operations Skill

## When to activate
Any question about: net worth, runway, how much money, cashflow, burn rate, Montreal, move, accounts, Kraken, OANDA, Wise, Stripe, Wealthsimple, balance, liquid, floor.

## Quick Commands
```bash
python main.py networth    # Live multi-platform net-worth snapshot
python main.py runway      # Montreal cashflow + 3-scenario runway model
python main.py rebalance   # Portfolio drift detection + tax-aware rebalancing
```

## Telegram Commands
- `/networth` — live snapshot (Kraken + OANDA + Wise + Stripe + manual)
- `/runway` — Montreal move scenarios (pessimistic/realistic/optimistic)
- `/status` — quick financial pulse

## Python Engines
- `cfo/accounts.py` — 5-platform parallel balance aggregator, TTL-cached, FX conversion
- `cfo/cashflow.py` — Montreal runway model, monthly burn, break-even date
- `cfo/dashboard.py` — ASCII net-worth table, category breakdown
- `cfo/rebalance.py` — portfolio drift detection, tax-aware rebalancing
- `cfo/pulse.py` — cross-agent data handshake (`data/pulse/cfo_pulse.json`)

## Skill Playbooks
- `skills/financial-planning/SKILL.md` — budget, FIRE, wealth projections
- `skills/financial-health-check/SKILL.md` — 8-dimension scoring (0-100)
- `skills/income-tier-monitoring/SKILL.md` — tier tracking, strategy triggers

## Key Files
- `brain/USER.md` — CC's complete financial profile (READ FIRST)
- `brain/DASHBOARD.md` — current dashboard state
- `brain/STATE.md` — system state
- `data/manual_balances.json` — manual account entries (Wealthsimple, RBC, etc.)
- `data/target_allocation.json` — target portfolio allocation

## Current State (update when numbers change)
- Total liquid: ~$7,466 CAD
- Montreal floor: $10,000 CAD
- Max rent: $1,500/mo (worst case), $750 if split
- MRR: ~$2,982 USD/mo
- Concentration risk: 94% Bennett (diversification urgent)

## Rules
- Always read `brain/USER.md` before answering
- Never guess balances — run the command or read data files
- Montreal floor ($10K) is non-negotiable — all recommendations must respect it
- FX rates: use `cfo.accounts.get_fx_rates()` for live rates, falls back to defaults
