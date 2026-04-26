---
tags: [brain, okrs, strategy, quarterly, cfo]
---

# ATLAS OKRs — Q2 2026 (April–June)

> Set: 2026-04-19 | Review: weekly (confidence scores) | Grade: end of June
> Pairs with [[STATE]] (operational) and Bravo's CEO OKRs at `C:\Users\User\Business-Empire-Agent\brain\OKRs.md` (out-of-vault). CFO-specific: capital + tax + compliance + research; not revenue growth (that's Bravo's primary).
>
> Neighbors: [[INDEX]] · [[SOUL]] · [[STATE]] · [[GROWTH]] · [[RISKS]] · [[CFO_CANON]] · [[AGENT_ORCHESTRATION]].

## Objective 1 — Hit the Montreal capital floor and open concentration-driven spend gate

**Why:** Below $10K CAD liquid, Atlas spend gate is TIGHT — Maven can't scale paid acquisition. Until Bennett concentration drops below 70%, the business cannot safely deploy discretionary capital even if liquid cleared. Both gates open together.

| # | Key Result | Target | Current (2026-04-19) | Confidence | Status |
|---|-----------|--------|----------------------|------------|--------|
| 1.1 | Total liquid CAD | ≥ $10,000 | $7,023 | 70% | IN PROGRESS |
| 1.2 | Bennett concentration | < 70% of MRR | 94% | 30% | NOT STARTED (Bravo-driven) |
| 1.3 | Herfindahl-Hirschman Index on revenue | < 2,500 | 8,245 | 30% | NOT STARTED (Bravo-driven) |
| 1.4 | Atlas approves paid Maven campaign ≥ $500/mo | ≥ $500 | $100 cap (experimentation) | 40% | NOT STARTED |

**Weekly check-in questions:**
- Has liquid crossed $8K, $9K, $10K?
- Any new paying clients landed (Bravo's pipeline)?
- Has Atlas's spend-gate recommendation changed?

---

## Objective 2 — File 2026 taxes early + prepare CCPC incorporation

**Why:** CC crosses the $80K TTM trigger in mid-2026 per current trajectory. CCPC takes 4-6 weeks to incorporate plus legal setup. Starting at $79K is too late.

| # | Key Result | Target | Current | Confidence | Status |
|---|-----------|--------|---------|------------|--------|
| 2.1 | CRA My Account unblocked | YES | BLOCKED | 60% | NOT STARTED (awaiting 2025 NOA) |
| 2.2 | Quarterly receipt pipeline runs monthly | Monthly auto | Manual | 75% | IN PROGRESS (parser shipped; cron next) |
| 2.3 | Incorporation law-firm quotes gathered | 3 quotes | 0 | 50% | NOT STARTED |
| 2.4 | Shadow T2125 assembled for Q1-Q2 2026 | Assembled | Partial | 65% | IN PROGRESS |
| 2.5 | $3K-$5K legal budget reserved in tax-reserve account | Reserved | Not separated | 40% | NOT STARTED |

**Weekly check-in questions:**
- Any new receipts not yet parsed?
- Has CC contacted any incorporation lawyer this week?
- Tax reserve balance vs required 25% of MRR?

---

## Objective 3 — Stand up trace telemetry + complete self-improvement cycle 2 infra

**Why:** Self-improvement Protocol 2 (OPTIMIZE) is currently non-functional. Without `agent_traces` emission, Atlas cannot measure its own success rate, tokens per task, or skill firing frequency. Cycle 2 needs this.

| # | Key Result | Target | Current | Confidence | Status |
|---|-----------|--------|---------|------------|--------|
| 3.1 | `scripts/supabase_tool.py` built | Built | Missing | 70% | NOT STARTED |
| 3.2 | `scripts/trace.py` helper emitting to `agent_traces` | Emitting | Not emitting | 70% | NOT STARTED |
| 3.3 | Every CLI entry + every Telegram command calls `trace()` | Instrumented | Not instrumented | 60% | NOT STARTED |
| 3.4 | Weekly Protocol 2 cron runs with real data | Running | Manual | 50% | NOT STARTED |

**Weekly check-in questions:**
- Is the trace telemetry query returning real rows?
- Are skill_activation scores updating?

---

## Objective 4 — Research frontier integration + canon expansion

**Why:** Atlas's recommendation quality depends on the canon. 18 new frameworks added 2026-04-19; their promotion to full pillars depends on practical application. Without applied use, canon entries are just pasted text.

| # | Key Result | Target | Current | Confidence | Status |
|---|-----------|--------|---------|------------|--------|
| 4.1 | At least 5 frontier frameworks applied in actual decisions | 5 applications | 0 | 75% | NOT STARTED |
| 4.2 | [[skills/behavioral-finance-guard/SKILL\|behavioral-finance-guard]] catches a real CC bias | 1 catch | 0 | 80% | NOT STARTED |
| 4.3 | Add 3-5 more frontier entries per quarter based on real-work relevance | ≥ 3 | 0 | 85% | NOT STARTED |
| 4.4 | Promote 1-2 PROBATIONARY patterns in [[PATTERNS]] to VALIDATED | 1-2 | 0 | 70% | NOT STARTED |

**Weekly check-in questions:**
- Which frontier framework did we reach for this week? Was it useful?
- Did behavioral-finance-guard fire? What did it catch?

---

## Objective 5 — Business-in-a-Box CFO role maturity

**Why:** Atlas is the CFO clone every Business in a Box buyer installs. Buyer-ready = role-portable (no CC-specific hardcoding), documented (ENV_STRUCTURE, BRANDS, QUICK_REFERENCE), and self-teaching (CFO_CANON + PATTERNS + MISTAKES).

| # | Key Result | Target | Current | Confidence | Status |
|---|-----------|--------|---------|------------|--------|
| 5.1 | Brain file-count parity with Bravo (±3) | ±3 of Bravo | Atlas 14 / Bravo 38+ | 85% | IN PROGRESS |
| 5.2 | Every skill has cited canonical sources in frontmatter | 100% | ~30% | 70% | NOT STARTED |
| 5.3 | Personal-layer vs core-layer split documented | Documented | Partial | 75% | IN PROGRESS |
| 5.4 | Buyer-clone flow tested end-to-end | Tested | Not tested | 40% | NOT STARTED |

**Weekly check-in questions:**
- Which Bravo-parallel file was added this week?
- Any CC-specific facts accidentally hardcoded in core files?

---

## Grading rubric (end of quarter)

Each objective grades 0.0-1.0 based on key-result completion:
- 0.7-1.0 = success (ambitious OKRs should hit this ~70% of the time)
- 0.4-0.6 = partial (real progress, didn't clear the bar)
- 0.0-0.3 = miss (re-examine assumptions; may signal a strategic error)

OKRs get a retrospective in [[memory/PATTERNS]] if a miss reveals something non-obvious.

## Maintenance rules

1. **Weekly check-ins update confidence only** — KR targets stay fixed in-quarter.
2. **Never add a KR mid-quarter** — if something new emerges, log as a pattern; add to Q3.
3. **At least 1 ambitious OKR per quarter** that has ≤ 70% confidence at set-time.
4. **CFO OKRs never duplicate CEO OKRs.** If Bravo owns it, Atlas supports through the pulse; Atlas's OKRs are CFO-scoped only.
