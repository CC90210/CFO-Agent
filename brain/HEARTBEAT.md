---
name: ATLAS Heartbeat
description: Proactive session-start monitoring — trading status, tax deadlines, account health, risk exposure
tags: [heartbeat, monitoring, proactive, health]
version: V1.0
---

# ATLAS Heartbeat — Proactive Monitoring

> Heartbeat runs at session start. Exercises judgment, not blind execution.
> Purpose: catch problems before they cost CC money.

## Session-Start Checks (Priority Order)

### 1. Trading Daemon Health (HIGH)
- Is the daemon running? (check PID)
- Current positions and unrealized P&L
- Any positions hitting stop-loss or take-profit?
- Kill switch status (drawdown %, daily loss %)
- OANDA + Kraken connectivity

### 2. Risk Exposure (HIGH)
- Total portfolio exposure vs limits
- Correlated positions check
- Regime classification (BULL/BEAR/CHOPPY/HIGH_VOL)
- Any strategy disabled that should be re-evaluated?

### 3. Tax Deadline Proximity (HIGH)
- Days until next filing deadline
- Installment payment due dates (March 15, June 15, Sept 15, Dec 15)
- RRSP deadline (March 1 for prior year)
- FHSA contribution room status
- TFSA contribution room status

### 4. Account Health (MEDIUM)
- Kraken equity vs last session
- OANDA equity vs last session
- Wise USD balance trend
- T1135 threshold proximity (foreign property > $100K CAD?)

### 5. Income Tier Monitoring (MEDIUM)
- Year-to-date income estimate
- Current tier (from ATLAS_INCOME_SCALING_PLAYBOOK.md)
- Approaching next tier? Flag new strategies that unlock
- Incorporation trigger check ($80K+ sustained revenue)

### 6. Opportunity Scan (LOW)
- Unrealized losses available for tax-loss harvesting (especially Q4)
- Registered account contribution room to fill before year-end
- Deductible purchases to accelerate before year-end
- Any new tax strategies applicable based on income changes

## Quarterly Deep Checks

### Q1 (Jan-Mar): Tax Filing Prep
- Gather all income records (T4, T5, crypto CSVs, invoices)
- Calculate crypto ACB for the year
- Review deductions and receipts
- RRSP deadline (March 1)
- Prepare T2125 + Schedule 3

### Q2 (Apr-Jun): Filing + Mid-Year Review
- April 30: tax payment due
- June 15: self-employed filing deadline
- Review Q1-Q2 income vs projections
- Adjust installment payments if needed
- Mid-year portfolio rebalance

### Q3 (Jul-Sep): Tax Planning
- Review income tier — has it changed?
- Evaluate incorporation trigger
- Plan Q4 tax-loss harvesting candidates
- Review registered account contributions
- International structure evaluation (if income warrants)

### Q4 (Oct-Dec): Year-End Optimization
- TAX-LOSS HARVESTING (flag all unrealized losses)
- Maximize TFSA/FHSA/RRSP contributions
- Accelerate deductible expenses (prepay subscriptions, buy equipment)
- Year-end income estimate → finalize installment strategy
- Charitable giving optimization (if applicable)
- Portfolio rebalance before year-end

## Heartbeat Output Format

When reporting heartbeat findings to CC:

```
Atlas online.

**Trading:** [daemon status, positions, P&L]
**Risk:** [exposure %, regime, any flags]
**Tax:** [next deadline, any action items]
**Accounts:** [equity changes, tier status]
**Action items:** [anything requiring CC's attention]
```

Keep it tight — 5-8 lines max unless something is urgent.
