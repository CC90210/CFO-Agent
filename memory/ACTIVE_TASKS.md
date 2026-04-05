---
name: ATLAS Active Tasks
description: Persistent task board with P0/P1/P2 prioritization — CC's financial action items and Atlas development tasks
tags: [tasks, priorities, action-items, tracking]
---

# ATLAS Active Tasks

> P0 = Money at stake or deadline-driven. Do first.
> P1 = Important but not urgent. Do this week.
> P2 = Nice to have. Do when P0/P1 are clear.
> Update after every session.

---

## P0 — Urgent / Money at Stake

### CC Action Items (Atlas Can't Do These)
- [x] **Open FHSA at Wealthsimple** — DONE 2026-03-27 ✅ (self-directed investing, $0 balance, room accumulating $8K/year)
- [ ] **Set up CRA My Account** — BLOCKED — Attempted 2026-03-27, rejected at identity verification (Line 15000 required). Will retry in 1-2 weeks after 2025 return assessed. 5 attempts remaining. Required for: tuition carryforward (Bishop's), TFSA/RRSP room verification, Notice of Assessment access, benefit payments.
- [ ] **Contact father about Irish passport** — Get grandfather's birth certificate documentation for expedited Irish citizenship claim (€278, 6-12 months). No downside; unlocks EU + 6.25% KDB.
- [ ] **Check OSAP RAP eligibility** — NSLSC portal. CC likely qualifies for $0 monthly payments at current income. Saves ~$200-300/month.
- [ ] **Measure home office** — Square footage of office / total home sq ft. Required for T2125 home office deduction.

### Atlas Action Items
- [x] **Wire RiskManager into engine.py** — DONE Session 30 ✅ (kill switches were inert; validate_trade() now gates every trade)
- [x] **Wire correlation_tracker.py into risk_manager.py** — DONE Session 30 ✅ (update_correlations() every 10 ticks, threshold 0.70)
- [ ] **Wire trade_protocol.py into engine.py** — 10-step decision framework exists but isn't connected to main trading loop.

---

## P1 — Important / This Week

### Trading
- [x] **Per-strategy trailing stop configuration** — DONE Session 30 ✅ (trend-followers 4-5x ATR, mean-reversion 1.5-2x chandelier, configured in strategies.yaml)
- [ ] Run multi-day paper trading validation — `python paper_trade.py` with all strategies.
- [ ] Backtest order_flow_imbalance, zscore_mean_reversion, volume_profile on multiple symbols/timeframes.

### Tax & Finance
- [ ] Set up quarterly tax review automation (SOP-004) — first run Q2 2026 (June).
- [ ] Monitor Wise USD balance vs T1135 $100K threshold quarterly.
- [ ] Track SR&ED qualifying R&D activities for OASIS (hours, activities, outcomes).

### Infrastructure
- [ ] Configure Alpaca paper account for US equities expansion.
- [ ] Add more crypto symbols — currently only BTC, ETH, SOL. Add top-20 by volume.

---

## P2 — Nice to Have / Backlog

### Future Planning
- [ ] Detailed incorporation analysis when OASIS crosses $80K sustained revenue.
- [ ] Crown Dependencies residency research (IOM housing, cost of living, business setup) — trigger at $120K+.
- [ ] Build automated tax-loss harvesting scanner (Q4 unrealized loss flagging).
- [ ] Build income tier monitoring dashboard (real-time tier tracking with strategy recommendations).
- [ ] Expand to IBKR for options/futures when capital permits.
- [ ] Evaluate private credit / MIC investments at $100K+ investable capital.

### Knowledge Base
- [ ] Build MISTAKES.md and PATTERNS.md operational learning system — [IN PROGRESS].
- [ ] Create more CFO-specific skills (quarterly review, departure planning, portfolio rebalancing).
- [ ] Build confidence decay model for memory facts (Bravo pattern).

---

## Completed (Recent)

- [x] **FHSA opened** — 2026-03-27 ✅ (Wealthsimple, self-directed, $0 balance)
- [x] **2025 taxes filed** — SIN on file (Session 23)
- [x] **7 new tax documents** — installments, HST, VDP, TOSI, Crown Dependencies, foreign reporting, income scaling (Session 23)
- [x] **Brain expansion** — 2 → 12 files, Bravo pattern adopted (Session 23)
- [x] **Dual citizenship documented** — British + Irish passport strategy embedded (Session 23)
- [x] **Daemon freeze fixed** — OANDA Semaphore(2) (Session 19)
- [x] **Position sizing overhaul** — micro account 8% risk (Session 19)
- [x] **18-doc tax knowledge base** — complete CFO library (Session 22)
- [x] **Wire RiskManager into engine.py** — kill switches now gate every trade (Session 30)
- [x] **Per-strategy trailing stop configuration** — trend 4-5x ATR, mean-reversion 1.5-2x chandelier (Session 30)
- [x] **Correlation tracker → RiskManager integration** — update_correlations() every 10 ticks, threshold 0.70 (Session 30)
- [x] **Regime detection caching** — cached per (symbol, timestamp), eliminates 10x redundant calls (Session 30)
- [x] **Doc index + count corrections** — 7 orphaned docs indexed, counts updated to 66 docs ~82,900+ lines (Session 30)
- [x] **db/__init__.py model exports** — all 10 models exported correctly (Session 30)
- [x] **Telegram bridge bug fix** — string formatting bug resolved (Session 30)
- [x] **MEMORY.md trimmed** — 220 lines → ~75, under 200-line limit (Session 30)
