---
name: ATLAS Decisions Log
description: Architecture, strategy, and financial decisions with rationale — the record of WHY, not just WHAT
tags: [decisions, rationale, architecture, strategy]
---

# ATLAS Decisions Log

> Every significant decision gets: context, options considered, decision, consequences.
> This is the historical record of WHY things are the way they are.

---

### DEC-001: Regime-Aware Strategy Filtering (Session 8)
**Context:** Backtests showed inconsistent returns across market conditions.
**Options:** (A) Run all strategies always, (B) Regime-based filtering, (C) Time-of-day filtering
**Decision:** B — Regime filtering with BULL/BEAR/CHOPPY/HIGH_VOL classification
**Consequence:** Every strategy improved. Became core architecture.

### DEC-002: 12.2% CCPC Trigger at $80K (Session 13)
**Context:** Need to determine when CC should incorporate OASIS.
**Options:** (A) Incorporate immediately, (B) Wait until $50K, (C) Wait until $80K, (D) Never incorporate
**Decision:** C — $80K sustained revenue trigger
**Rationale:** Below $80K, the tax deferral doesn't justify the $1,500-$3,000 setup cost + $2,000-$3,000/year accounting. At $80K, the 12.2% CCPC rate vs 29.65%+ personal rate saves ~$5K-$8K/year.
**Consequence:** Monitoring OASIS revenue against this trigger.

### DEC-003: Kill Switch Values (Session 1)
**Context:** Need hardcoded risk limits to prevent catastrophic loss.
**Options:** Various drawdown limits (5%, 10%, 15%, 20%)
**Decision:** 15% max drawdown, 5% daily loss, 1.5% per-trade
**Rationale:** 15% drawdown requires ~18% gain to recover — painful but recoverable. 20%+ requires 25%+ which starts compounding against you. 1.5% per trade means you need 10 consecutive losers to hit the daily limit.
**Consequence:** Hardcoded in core/risk_manager.py. Never modified. These saved us from BB Mean Reversion.

### DEC-004: FHSA > TFSA > RRSP Priority (Session 20)
**Context:** CC needs to decide registered account contribution order.
**Options:** (A) RRSP first (traditional advice), (B) TFSA first, (C) FHSA first
**Decision:** C — FHSA > TFSA > RRSP
**Rationale:** FHSA is the only account with ALL THREE tax benefits: deduction on contribution + tax-free growth + tax-free withdrawal. TFSA has 2/3 (no deduction). RRSP has 2/3 (taxed on withdrawal). FHSA is mathematically superior at every income level.
**Consequence:** CC needs to open FHSA immediately (P0 action item).

### DEC-005: Micro Account Sizing at 8% (Session 19)
**Context:** Standard 1.5% risk on $136 = $2 trades. Useless.
**Options:** (A) Keep 1.5% (useless trades), (B) 5% risk, (C) 8% risk, (D) Fixed dollar amount
**Decision:** C — 8% risk with risk-budget sizing, protocol caps advisory-only
**Rationale:** 8% risk on $136 = $10.88 per trade — minimum viable position size. At micro scale, learning and testing strategies matters more than protecting capital (it's already negligible).
**Consequence:** Trades are actually viable. Strategies can be tested with real money.

### DEC-006: Dual Citizenship Tax Strategy — IOM Primary (Session 23)
**Context:** CC revealed British passport + Irish passport eligibility. Need optimal jurisdiction.
**Options:** (A) Stay in Canada forever, (B) UK, (C) Guernsey, (D) Isle of Man, (E) Jersey, (F) Ireland, (G) Dubai
**Decision:** D — Isle of Man as primary recommendation at $120K+ income
**Rationale:** 0% corporate tax + 20% personal + 0% CGT + £200K tax cap + growing tech ecosystem + lower cost than Guernsey/Jersey + CC has right to reside as UK citizen. Ireland is secondary for IP (6.25% KDB) at $300K+.
**Consequence:** Irish passport application recommended NOW (€278 free option). Actual move decision deferred until income crosses $120K+.

### DEC-007: ATLAS Doc Format Standard (Session 21)
**Context:** Tax knowledge base growing rapidly, needs consistency.
**Options:** (A) Free-form markdown, (B) Structured with ITA refs, (C) YAML frontmatter + structured
**Decision:** B — Structured markdown with ITA section references, [NOW]/[FUTURE] tags, dollar amounts, decision trees
**Rationale:** Dollar amounts make advice actionable. ITA references make it verifiable. Tags make it scannable for CC's current situation.
**Consequence:** All 25 docs follow this format. Consistency aids navigation.

### DEC-008: Brain Architecture — Bravo Pattern (Session 23)
**Context:** ATLAS had 2 brain files (CAPABILITIES, STATE). Bravo has 13+ with structured reasoning.
**Options:** (A) Keep minimal, (B) Copy Bravo exactly, (C) Adapt Bravo's pattern for CFO
**Decision:** C — Adapt to 12 brain files with CFO-specific content
**Rationale:** ATLAS needs structured reasoning (BRAIN_LOOP), proactive monitoring (HEARTBEAT), governance (INTERACTION_PROTOCOL), and identity (SOUL). But doesn't need Bravo's APP_REGISTRY, OPENCLI_STRATEGY, or content-specific files.
**Consequence:** 12 brain files operational. Session start/end protocols established.

### DEC-009: Scale-Out Tiers Permanently Disabled (Session 12)
**Context:** Testing partial position exits at profit targets (25%, 50%, 75% take-profit tiers).
**Options:** (A) Keep scale-out, (B) Disable for crypto only, (C) Disable entirely
**Decision:** C — Permanently disabled
**Rationale:** -5% to -20% drag on EVERY crypto strategy. Crypto trends are all-or-nothing — scaling out captures crumbs and misses the 10x moves that make strategies profitable.
**Consequence:** All-or-nothing exits via trailing stops only. May revisit for equities (different market structure).

### DEC-010: VDP Recommendation — Business Income, Not Capital Gains (Session 23)
**Context:** Building VDP guide for crypto disclosure. Need to recommend income characterization.
**Options:** (A) Argue capital gains (lower rate), (B) Disclose as business income (safer)
**Decision:** B — Disclose algorithmic trading as business income on T2125
**Rationale:** ATLAS is a systematic trading algorithm with automated execution. CRA characterizes frequent, systematic, short-holding-period trading as business income. Arguing capital gains on an automated system won't survive audit. Failed characterization after VDP = reassessment exposure.
**Consequence:** Higher tax rate on trading income but audit-proof position. Conservative is correct when CRA scrutiny is the risk.
