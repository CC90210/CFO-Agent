---
tags: [account, kraken, crypto, exchange, api-backed]
type: crypto_exchange
currency: USD
api_backed: true
---

# Kraken (Crypto Exchange)

> CC's active crypto-trading account. Live balance read via API every pulse refresh. Ontario-restricted pair set enforced.
>
> Neighbors: [[README|accounts/]] · [[STATE]] · [[wealthsimple_crypto]] · [[ENV_STRUCTURE]] · [[CAPABILITY_GAPS]].

## Purpose

Small-scale crypto trading (~$133 USD equity across 4 positions: BTC, SOL, LTC, ATOM). Despite the post-pivot archiving of algorithmic trading, CC retains manual discretion on Kraken for personal trading. Atlas READS balances for net-worth + ACB tracking; Atlas does NOT execute trades.

## Access

- **API:** `KRAKEN_API_KEY` + `KRAKEN_API_SECRET`
- **Scope:** `Query Funds` + `Query Open/Closed Orders`. NO trade permissions on Atlas's key.
- **Read path:** `cfo/accounts.py::KrakenReader` via CCXT (`await exchange.fetch_balance()` — never `asyncio.to_thread`, see [[MISTAKES]] Async CCXT).
- **Ontario restriction:** Only `/USD` pairs. USDT pairs are blocked by Ontario Securities Commission. Hardcoded in config.

## Current state (2026-04-18)

- USD equity: $133.37
- CAD @ 1.37 FX: $183
- Positions: BTC, SOL, LTC, ATOM (4 holdings)
- Share of total liquid: 2.6%

## Tax treatment

- **ACB method:** weighted average across all Kraken + personal wallets (CRA requirement). See [[skills/crypto-acb-tracking/SKILL|crypto-acb-tracking]].
- **Disposition events:** every crypto-to-crypto trade is a taxable disposition (CRA technical interpretation 2014-0561081E5) — not just crypto-to-fiat. This is a commonly-missed rule.
- **Superficial loss rule:** applies to crypto per CRA Folio S3-F4-C1. 30-day window triggers denial of the loss.
- **Reporting:** T1135 triggers if cost base of foreign-located crypto > $100K CAD. Currently minimal; monitor.
- **CARF (Crypto-Asset Reporting Framework):** OECD standard, Canada adopts for 2026 reporting. Kraken is an RPSP (Reporting Platform Service Provider) — balances will report to CRA automatically starting 2027 filing (2026 tax year).

## Risk flags

| Risk | Level | Mitigation |
|------|:-:|------------|
| Exchange solvency (post-FTX caution) | MEDIUM | Kraken has not served US customers with comingled funds; Canadian regulation is relatively strict. Still: never hold more than CC can afford to lose. |
| API key compromise | LOW | Read-only scope; worst case is exposure of balance info, not funds drain |
| Volatility (position-level) | HIGH | Inherent to crypto. Sized small (<3% of liquid) — acceptable. |
| Regulatory change | MEDIUM | Ontario MSC frequently changes permitted pairs; Atlas auto-enforces current whitelist |

## Maintenance cadence

- **Daily:** pulse read
- **Weekly:** verify ACB journal is up-to-date (manual entry from trade confirmations into `data/crypto_trades.csv`)
- **Annual (January):** T5008 + T1135 check for prior year; generate disposition schedule for T1 filing
- **2027 filing forward:** cross-check CRA's CARF-sourced data against Atlas's independent ACB — catches reporting discrepancies

## Relevant skills

- [[skills/crypto-acb-tracking/SKILL|crypto-acb-tracking]] — primary
- [[skills/tax-loss-harvesting/SKILL|tax-loss-harvesting]] — Q4 harvesting with superficial-loss compliance
- [[skills/cross-border-compliance/SKILL|cross-border-compliance]] — T1135 threshold, CARF
- [[skills/compliance-monitor/SKILL|compliance-monitor]] — Ontario pair-whitelist enforcement

## Notes

- Trading daemon archived 2026-04-14 (see `archive/trading-automation/`). Atlas does NOT place orders. CC trades manually.
- [[skills/trade-protocol/SKILL|trade-protocol]] remains in the skills library as a manual procedure reference, not an auto-execution pathway.
- When/if CC wants to build a proper crypto income strategy (staking, lending), Atlas flags CRA-specific treatment for each income type before deployment.
