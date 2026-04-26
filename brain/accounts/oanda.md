---
tags: [account, oanda, forex, metals, broker, api-backed]
type: forex_broker
currency: CAD
api_backed: true
---

# OANDA (Forex + Metals)

> CC's forex + gold broker. Read-only API. Primary use post-pivot: gold exposure + occasional manual macro positions.
>
> Neighbors: [[README|accounts/]] · [[STATE]] · [[ENV_STRUCTURE]] · [[CAPABILITY_GAPS]] · [[MISTAKES]].

## Purpose

Gold exposure (XAU_USD) + historical London-breakout GBP trades. Post-trading-pivot, Atlas READS balance only; no auto-trading. If CC wants gold allocation as an inflation hedge (per [[CFO_CANON]] § Dalio), this account is the vehicle.

## Access

- **API:** `OANDA_API_TOKEN` + `OANDA_ACCOUNT_ID` + `OANDA_ENVIRONMENT` (`live` or `practice`)
- **Scope:** read-only
- **Read path:** `cfo/accounts.py::OandaReader` via `oandapyV20` — requires `asyncio.Semaphore(2)` wrapper because `requests.Session` in `oandapyV20` is NOT thread-safe (see [[MISTAKES]] OANDA Thread Safety — Daemon Freeze).

## Current state

Balance varies. Pulse refresh pulls live. Share of liquid small (~1-2%).

## Tax treatment

- **Forex gains:** foreign-exchange gains/losses on business-account forex are ordinary income (T2125 line 8090 "other revenue" or line 9270 for losses) — NOT capital gains, because this is trading-style activity not hedge-of-capital-asset.
- **Gold positions:** XAU_USD held as CFD — NOT physical gold. Treated as speculative gain/loss, not a precious-metals capital holding. If CC wants physical gold tax treatment, needs a different vehicle (e.g., allocated metals in a dealer account).
- **Election:** CRA allows s.39(4) election to treat forex gains as capital — relevant only if volume is low and hedge-like. CC has not made this election; retail forex is generally ordinary income.

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Counterparty (OANDA solvency) | LOW | OANDA is IIROC-regulated in Canada; long-established |
| Leverage (inherent to CFD) | HIGH | Atlas does not auto-leverage; any use requires explicit modeled worst case per [[SOUL]] Rule — never margin without ruin analysis |
| Volatility | HIGH | XAU has lower vol than crypto but high vs equities; size small |
| Regulatory change | LOW | IIROC rules stable |

## Historical context (trading-era, archived)

Previously ran: gold trend-follower, gold pullback, London breakout GBP/USD. Archived at `archive/trading-automation/`. Patterns learned:
- Gold works on OANDA (Donchian trend on XAU: +10.93% backtest, 0% Monte Carlo ruin)
- Forex majors did NOT work — all strategies negative
- London breakout GBP/USD showed 67% win rate in single backtest (never live-validated long enough)

Documented in [[PATTERNS]] as probationary observations from the trading era.

## Maintenance cadence

- **Daily:** pulse read
- **Monthly:** position-level review (CC's discretionary positions, not Atlas's auto-trades)
- **Annual:** P&L aggregation for T2125 line 8090

## Relevant skills

- [[skills/portfolio-rebalancing/SKILL|portfolio-rebalancing]] — if gold becomes a strategic allocation slice
- [[skills/tax-optimization/SKILL|tax-optimization]] — forex-vs-capital election evaluation
- [[skills/trade-protocol/SKILL|trade-protocol]] — manual procedure reference (no auto-execution)

## Notes

- Post-pivot role is custody + read-only monitoring. The instrument is not gone, but the automation is.
- If CC wants inflation-hedge gold exposure, evaluate: OANDA CFD vs Wealthsimple gold ETF (IGLD) vs physical gold via a dealer. Each has different tax treatment.
