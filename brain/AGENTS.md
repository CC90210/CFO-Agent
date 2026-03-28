---
name: ATLAS Agent Registry
description: Subagent definitions and task routing for trading, tax, and financial operations
tags: [agents, orchestration, routing, subagents]
version: V1.0
---

# ATLAS Agent Registry & Task Routing

> How ATLAS routes tasks to specialized agents and modules.

## Trading Agents (from agents/ directory)

| Agent | Role | File | Signal Type |
|-------|------|------|-------------|
| Technical Analyst | Chart patterns, indicators, trend analysis | agents/technical_analyst.py | Technical signals |
| Fundamental Analyst | News, sentiment, macro data | agents/fundamental_analyst.py | Fundamental signals |
| Sentiment Analyst | Social media, fear/greed, funding rates | agents/sentiment_analyst.py | Sentiment signals |
| Risk Analyst | Position sizing, correlation, drawdown | agents/risk_analyst.py | Risk assessment |
| Debate Agent | Bull vs bear case synthesis | agents/debate_agent.py | Consensus signal |
| Portfolio Agent | Asset allocation, rebalancing | agents/portfolio_agent.py | Allocation signals |
| Orchestrator | Runs all agents in parallel, aggregates | agents/orchestrator.py | Final decision |
| Darwinian Agent | Self-improvement, strategy evolution | agents/darwinian.py | Evolution signals |

## Financial Modules

| Module | Role | File | Domain |
|--------|------|------|--------|
| Tax Calculator | CRA-accurate capital gains, ACB, deductions | finance/tax.py | Tax filing |
| Financial Advisor | Portfolio analysis, allocation, reviews | finance/advisor.py | Wealth management |
| Wealth Tracker | Net worth, FIRE calculator, projections | finance/wealth_tracker.py | FIRE planning |
| Budget Tracker | Expense tracking, savings opportunities | finance/budget.py | Budgeting |

## Task Routing Matrix

| Task Type | Route To | Complexity | Notes |
|-----------|---------|-----------|-------|
| Trade signal analysis | Orchestrator → all agents | COMPLEX | Full brain loop required |
| Position sizing | Risk Analyst + risk_manager.py | MODERATE | Kill switches non-negotiable |
| Backtest a strategy | backtesting/engine.py | MODERATE | Regime filter ON by default |
| Tax question | TAX_PLAYBOOK_INDEX → relevant doc | SIMPLE-MODERATE | Reference ITA sections |
| Tax filing prep | accounting-advisor skill | COMPLEX | Multi-step, multi-form |
| Crypto ACB calculation | finance/tax.py | MODERATE | Weighted-average method only |
| FIRE calculation | finance/wealth_tracker.py | SIMPLE | 4% rule, projection model |
| Budget review | finance/budget.py | SIMPLE | Monthly summary |
| Portfolio rebalance | finance/advisor.py | MODERATE | Consider tax implications |
| International structure | docs/ATLAS_UK_CROWN_DEPENDENCIES_STRATEGY.md | COMPLEX | Requires CC involvement |
| Income tier check | docs/ATLAS_INCOME_SCALING_PLAYBOOK.md | SIMPLE | Quick lookup |
| Deduction review | docs/ATLAS_DEDUCTIONS_MASTERLIST.md | MODERATE | Annual filing season |

## Complexity Classification

| Level | Files Touched | Steps | CC Involvement |
|-------|-------------|-------|---------------|
| TRIVIAL | 1 | 1-2 | None needed |
| SIMPLE | 1-2 | 3-5 | Inform after completion |
| MODERATE | 3-5 | 5-15 | Show reasoning + result |
| COMPLEX | 5+ | 15+ | Plan → CC approves → execute |
| CRITICAL | Any | Any | Money/compliance at stake → CC approves first |

## Agent Coordination Rules

1. **Trading signals:** ALL analysts run in parallel via Orchestrator. No single agent can trigger a trade alone.
2. **Risk vetoes are final:** If risk_analyst or risk_manager says no, the answer is no.
3. **Tax calculations:** Always reference ITA section. Always show dollar impact.
4. **Financial projections:** State assumptions explicitly. Show sensitivity analysis.
5. **International structures:** Always assess GAAR risk and substance requirements.
6. **Cross-domain decisions:** If a trade has tax implications (e.g., tax-loss harvest), involve BOTH trading agents AND tax module.
