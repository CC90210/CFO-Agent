---
name: ATLAS SOP Library
description: Standard operating procedures for trading, tax, and financial operations — tracked by execution count and success rate
tags: [sop, procedures, operations, playbook]
---

# ATLAS SOP Library

> SOPs are repeatable procedures. Each tracks execution count and success rate.
> [PROBATIONARY]: <3 successful executions. [VALIDATED]: 3+ successes.
> [UNDER_REVIEW]: caused errors — investigate before using.

---

## SOP-001: Session Start Protocol [VALIDATED]
**Executions:** 23 | **Success Rate:** 100%
**Trigger:** Every new session

1. Load brain files: SOUL.md → USER.md → STATE.md
2. Run HEARTBEAT checks (daemon health, risk exposure, tax deadlines)
3. Check memory: ACTIVE_TASKS.md (pending items), MISTAKES.md (relevant errors)
4. Brief CC: "Atlas online. [status update if relevant]"
5. Address CC's question immediately

**Time:** 30 seconds
**Notes:** Do NOT run full heartbeat if CC has an urgent question — answer first, heartbeat after.

---

## SOP-002: Session End Protocol [VALIDATED]
**Executions:** 22 | **Success Rate:** 95%
**Trigger:** Session ending or natural conversation break

1. Update STATE.md with any changes from this session
2. Append to SESSION_LOG.md (what happened, key decisions, metrics)
3. Log any new mistakes to MISTAKES.md
4. Log any new patterns to PATTERNS.md (tagged [PROBATIONARY])
5. Update ACTIVE_TASKS.md (complete finished items, add new ones)
6. If code changed: suggest commit to CC
7. If docs changed: note what was added/modified

**Time:** 2-5 minutes
**Notes:** The 5% failure was forgetting to update STATE.md in Session 14. Now hardcoded in protocol.

---

## SOP-003: Tax Filing Preparation [VALIDATED]
**Executions:** 3 | **Success Rate:** 100%
**Trigger:** Filing season (January-June) or CC asks about taxes

### Phase 1: Gather Documents
1. T4 slips (employment income — Nicky's)
2. Crypto exchange CSVs (Kraken, Wealthsimple)
3. OASIS invoices/Stripe revenue
4. DJ gig records (dates, amounts)
5. Receipts for deductions (equipment, software, home office)
6. OSAP interest statements (T4A)
7. Contribution receipts (TFSA, RRSP, FHSA if opened)

### Phase 2: Calculate
1. Run crypto ACB calculation (weighted-average method)
2. Calculate T2125 business income (OASIS + DJ - deductions)
3. Calculate home office deduction (sq ft method)
4. Calculate CCA on equipment (immediate expensing if eligible)
5. Estimate total tax owing
6. Check: installment payments needed? (>$3K owing in current + prior year)

### Phase 3: Optimize
1. Review ATLAS_DEDUCTIONS_MASTERLIST.md — any missed deductions?
2. Review ATLAS_INCOME_SCALING_PLAYBOOK.md — current tier strategies
3. RRSP contribution decision (only if marginal rate >= 29.65%)
4. FHSA contribution ($8K/year if opened)
5. TFSA maximized?
6. Tax-loss harvesting opportunities?

### Phase 4: File
1. Enter all data in Wealthsimple Tax
2. Review T2125 (self-employment), Schedule 3 (capital gains), ON-BEN (Ontario credits)
3. CC reviews and submits via NETFILE
4. Confirm with CC: refund or owing?

**Time:** 2-4 hours across sessions
**Dependencies:** CC provides receipts, measurements, and CRA My Account access

---

## SOP-004: Quarterly Tax Review [PROBATIONARY]
**Executions:** 0 | **Success Rate:** N/A
**Trigger:** End of Q1 (March), Q2 (June), Q3 (September), Q4 (December)

1. Estimate year-to-date income (all sources)
2. Determine current income tier (ATLAS_INCOME_SCALING_PLAYBOOK.md)
3. Check: has tier changed since last review? → flag new strategies
4. Review unrealized gains/losses → tax-loss harvesting candidates
5. Check registered account contributions vs room
6. Check installment payment obligations
7. Review deductible expenses — accelerate before quarter-end if beneficial
8. Update departure tax snapshot (if international planning active)
9. Report to CC: "Q[X] review — [key findings]"

**Time:** 30-60 minutes
**Notes:** Not yet executed. First run scheduled for Q2 2026 (June).

---

## SOP-005: Backtest a Strategy [VALIDATED]
**Executions:** 15+ | **Success Rate:** 90%
**Trigger:** New strategy or parameter change

1. Define: strategy name, symbol, timeframe, date range
2. Run: `python main.py backtest --strategy [name] --symbol [symbol] --start [date]`
3. Analyze: return %, win rate, max drawdown, Sharpe ratio
4. Compare: with and without regime filter
5. If positive: run Monte Carlo simulation (1000 iterations)
6. Check: ruin probability <5%? Max drawdown within limits?
7. If passes: promote to paper trading
8. If fails: log to MISTAKES.md with root cause, disable strategy

**Time:** 10-30 minutes per strategy
**Notes:** The 10% failure rate is from strategies that passed backtest but failed paper trading. Need longer paper periods.

---

## SOP-006: Trade Signal Evaluation (Full Brain Loop) [VALIDATED]
**Executions:** 50+ | **Success Rate:** 85%
**Trigger:** Strategy generates a signal

1. **ORIENT:** Load current positions, regime, risk exposure
2. **ASSESS:** Signal conviction score >= 0.3? If no → reject
3. **RISK CHECK:**
   - Per-trade risk within 1.5% (or 8% for micro account)?
   - Daily loss limit not hit?
   - Max drawdown not hit?
   - Correlated positions within limit?
4. **SIZE:** Calculate position size via risk-budget model
5. **VERIFY:** Regime supports this strategy type?
6. **EXECUTE:** Place order via OrderExecutor (limit order, 30s timeout)
7. **MONITOR:** Set trailing stop (per-strategy type)
8. **LOG:** Record trade in database

**Time:** Automated (60-second tick cycle)
**Notes:** 15% failure rate is from regime changes mid-trade. Hysteresis (min_hold_bars=6) reduced this.

---

## SOP-007: Crypto ACB Calculation [VALIDATED]
**Executions:** 4 | **Success Rate:** 100%
**Trigger:** Tax filing or CC asks about crypto tax

1. Export trade history from all exchanges (Kraken CSV, Wealthsimple CSV)
2. Convert all amounts to CAD at trade date exchange rate (Bank of Canada daily rate)
3. Calculate weighted-average ACB across ALL exchanges and wallets
4. Identify dispositions (sells, swaps, payments with crypto)
5. Calculate capital gain/loss per disposition: proceeds - (ACB x units sold / total units)
6. Check superficial loss rule: any repurchase of same asset within 30 days of loss sale?
7. Generate Schedule 3 summary
8. Check: business income or capital gains? (frequency, intent, holding period)

**Time:** 1-2 hours (depends on trade volume)
**Dependencies:** finance/tax.py CryptoTaxCalculator

---

## SOP-008: Income Tier Assessment [PROBATIONARY]
**Executions:** 1 | **Success Rate:** 100%
**Trigger:** Significant income change or quarterly review

1. Estimate annual income from ALL sources:
   - OASIS AI Solutions (Stripe/Wise revenue)
   - Nicky's T4 employment
   - DJ gigs
   - Crypto trading gains (realized)
   - OANDA trading gains (realized)
2. Determine tier from ATLAS_INCOME_SCALING_PLAYBOOK.md
3. Compare to last assessment — has tier changed?
4. If tier changed: flag new strategies that unlock
5. Key triggers to check:
   - $30K: HST registration decision
   - $55K: RRSP becomes valuable
   - $80K: Incorporation trigger
   - $100K: SR&ED credits, CDA planning
   - $150K: Crown Dependencies evaluation
   - $200K: Full corporate structure
6. Report to CC with specific dollar-impact recommendations

**Time:** 15-30 minutes
**Notes:** First execution was Session 23 (built the playbook). Needs quarterly repetition to validate.

---

## SOP-009: Departure Tax Snapshot [PROBATIONARY]
**Executions:** 1 | **Success Rate:** 100%
**Trigger:** Quarterly (if international planning is active) or on request

1. List all assets subject to deemed disposition (s.128.1):
   - Crypto portfolio (FMV - ACB)
   - OANDA positions (FMV - ACB)
   - Kraken positions (FMV - ACB)
   - OASIS shares (if incorporated — FMV - paid-up capital)
   - Other investments
2. Exclude: RRSP, TFSA, FHSA, Canadian real property, personal-use property <$1K
3. Calculate total unrealized gain
4. Apply capital gains inclusion rate (50% or 66.67% above $250K)
5. Calculate departure tax at current marginal rate
6. Compare to annual tax savings from relocation
7. Calculate breakeven period (departure tax / annual savings)
8. Report: "Departure tax today: $X. Annual savings at [jurisdiction]: $Y. Breakeven: Z months."

**Time:** 30 minutes
**Notes:** Current departure tax is ~$0. Snapshot value is tracking how it grows over time.

---

## SOP-010: New Tax Document Creation [VALIDATED]
**Executions:** 25 | **Success Rate:** 96%
**Trigger:** Knowledge gap identified or new tax law/strategy discovered

1. Identify gap (diagnostic, CC request, or new legislation)
2. Research: ITA sections, CRA interpretation bulletins, Tax Court cases
3. Draft document in ATLAS doc format:
   - Clear headers, tables, ITA references
   - [NOW]/[FUTURE] tags for CC relevance
   - Dollar-amount examples, not abstract advice
   - Decision trees where applicable
4. Save to docs/ATLAS_[NAME].md
5. Update brain/TAX_PLAYBOOK_INDEX.md
6. Update brain/CAPABILITIES.md (doc count)
7. Update CLAUDE.md (doc list and core knowledge)
8. Add reference to memory/MEMORY.md index

**Time:** 30-90 minutes per document
**Notes:** 4% failure was a doc that had incorrect ITA section references (fixed in review).
