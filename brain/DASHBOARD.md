---
name: ATLAS Dashboard
description: Navigation hub — links to all brain, skill, and doc files
tags: [dashboard, navigation, index]
---

# ATLAS Dashboard

> Central navigation hub. Start here to find anything.

## Brain Files (Load Order: SOUL → USER → STATE)

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| [SOUL.md](SOUL.md) | Immutable identity, values, rules | Rarely (version changes only) |
| [USER.md](USER.md) | CC's financial profile, citizenship, accounts | Major life/financial changes |
| [STATE.md](STATE.md) | Operational snapshot (positions, blockers, status) | Every session |
| [CAPABILITIES.md](CAPABILITIES.md) | Tool/strategy/broker registry | When tools added/removed |
| [DASHBOARD.md](DASHBOARD.md) | This file — navigation hub | When structure changes |
| [GROWTH.md](GROWTH.md) | Evolution timeline, capability milestones | Monthly or on milestone |
| [RISKS.md](RISKS.md) | Kill switches, limits, risk controls | When limits change |
| [TAX_PLAYBOOK_INDEX.md](TAX_PLAYBOOK_INDEX.md) | Master index of all tax documents | When docs added |
| [BRAIN_LOOP.md](BRAIN_LOOP.md) | 10-step structured reasoning protocol | Semi-mutable |
| [INTERACTION_PROTOCOL.md](INTERACTION_PROTOCOL.md) | State sync, logging, governance | Semi-mutable |
| [HEARTBEAT.md](HEARTBEAT.md) | Session-start proactive monitoring | Semi-mutable |
| [AGENTS.md](AGENTS.md) | Subagent registry and task routing | When agents change |

## Memory (Operational Intelligence)

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| [SESSION_LOG.md](../memory/SESSION_LOG.md) | Append-only narrative log of all sessions | Every session |
| [MISTAKES.md](../memory/MISTAKES.md) | Documented failure modes with prevention rules | When mistakes occur |
| [PATTERNS.md](../memory/PATTERNS.md) | Validated/probationary approaches | When patterns confirmed |
| [DECISIONS.md](../memory/DECISIONS.md) | Major decisions with rationale | When decisions made |
| [LONG_TERM.md](../memory/LONG_TERM.md) | Persistent facts with confidence decay | When facts learned |
| [SOP_LIBRARY.md](../memory/SOP_LIBRARY.md) | Standard operating procedures | When SOPs change |
| [ACTIVE_TASKS.md](../memory/ACTIVE_TASKS.md) | P0/P1/P2 task board | Every session |

## Skills (11)

| Skill | Location | Domain |
|-------|----------|--------|
| Accounting Advisor | [skills/accounting-advisor/SKILL.md](../skills/accounting-advisor/SKILL.md) | CRA filing, T2125, Schedule 3 |
| Tax Optimization | [skills/tax-optimization/SKILL.md](../skills/tax-optimization/SKILL.md) | 25-strategy playbook |
| Financial Planning | [skills/financial-planning/SKILL.md](../skills/financial-planning/SKILL.md) | Budget, FIRE, wealth |
| Quarterly Tax Review | [skills/quarterly-tax-review/SKILL.md](../skills/quarterly-tax-review/SKILL.md) | Q1-Q4 tax review cycle |
| Tax-Loss Harvesting | [skills/tax-loss-harvesting/SKILL.md](../skills/tax-loss-harvesting/SKILL.md) | Superficial loss detection, Q4 harvesting |
| Departure Tax Planning | [skills/departure-tax-planning/SKILL.md](../skills/departure-tax-planning/SKILL.md) | s.128.1 exit strategy, Crown Dependencies |
| Portfolio Rebalancing | [skills/portfolio-rebalancing/SKILL.md](../skills/portfolio-rebalancing/SKILL.md) | Tax-aware rebalancing, account placement |
| Position Sizing | [skills/position-sizing/SKILL.md](../skills/position-sizing/SKILL.md) | Risk-budget sizing, Kelly criterion |
| Trade Protocol | [skills/trade-protocol/SKILL.md](../skills/trade-protocol/SKILL.md) | 10-step trade decision framework |
| Income Tier Monitoring | [skills/income-tier-monitoring/SKILL.md](../skills/income-tier-monitoring/SKILL.md) | Dynamic tier tracking, threshold alerts |
| Crypto ACB Tracking | [skills/crypto-acb-tracking/SKILL.md](../skills/crypto-acb-tracking/SKILL.md) | CRA-compliant weighted-average ACB |

## Tax Document Library (25+ docs)

See [TAX_PLAYBOOK_INDEX.md](TAX_PLAYBOOK_INDEX.md) for the complete index.

## Trading System

| Component | Location | Status |
|-----------|----------|--------|
| Strategies (12) | `strategies/` | LIVE |
| AI Agents (10) | `agents/` | LIVE |
| Risk Manager | `core/risk_manager.py` | LIVE (kill switches hardcoded) |
| Regime Detector | `core/regime_detector.py` | LIVE |
| Trade Protocol | `core/trade_protocol.py` | NOT WIRED |
| Correlation Tracker | `core/correlation_tracker.py` | NOT WIRED |
| Trailing Stops | `core/trailing_stop.py` | LIVE (needs per-strategy tuning) |

## Finance Modules

| Module | Location | Purpose |
|--------|----------|---------|
| Tax Calculator | `finance/tax.py` | CRA-accurate crypto/business tax |
| Financial Advisor | `finance/advisor.py` | Portfolio analysis, allocation |
| Wealth Tracker | `finance/wealth_tracker.py` | Net worth, FIRE calculator |
| Budget Tracker | `finance/budget.py` | Expense tracking, savings |

## Connected Brokers

| Broker | Platform | Status | Instruments |
|--------|----------|--------|------------|
| Kraken | CCXT | LIVE | Crypto (BTC, SOL, LTC, ATOM /USD) |
| OANDA | oandapyV20 | LIVE | Gold (XAU_USD), Forex (GBP_USD) |
| Alpaca | alpaca-py | NOT CONFIGURED | US equities |

## External References

| Resource | Location | Access |
|----------|----------|--------|
| Business-Empire-Agent (Bravo) | `C:\Users\User\Business-Empire-Agent\` | READ ONLY |
| CC Profile (Bravo's USER.md) | `Business-Empire-Agent\brain\USER.md` | READ ONLY |
