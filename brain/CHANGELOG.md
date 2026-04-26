---
tags: [changelog, audit, self-modification]
---

# ATLAS — Self-Modification Changelog

> Every meaningful change Atlas (or any runtime acting as Atlas) makes to its own brain, skills, or memory is recorded here. This is the human-readable audit trail; Supabase `self_modification_log` (once instrumented — see [[CAPABILITY_GAPS]] trace-telemetry gap) will hold the structured version.
>
> Neighbors: [[INDEX]] · [[SOUL]] · [[STATE]] · [[RESEARCH_FRONTIER]].

## Format

```
### [DATE] — [FILE] — [ACTION]
**Tier:** IMMUTABLE | SEMI-MUTABLE | GOVERNED-MUTABLE | FREELY-MUTABLE | EPHEMERAL
**What changed:** Brief description
**Why:** Reason for the change
**Confidence:** 0.0-1.0
**Cycle:** self-improvement cycle number, or "ad-hoc"
```

## Mutability tiers

| Tier | Definition | Change authority |
|------|------------|------------------|
| IMMUTABLE | Identity documents — SOUL.md version bumps require explicit CC authorization | CC only |
| SEMI-MUTABLE | Contracts + canon — CFO_CANON, AGENT_ORCHESTRATION, STRUCTURE | CC-approved in-session, agent may edit |
| GOVERNED-MUTABLE | State + operational — STATE, DASHBOARD, GROWTH, RISKS, OKRs, BRANDS | Any runtime; changes logged here |
| FREELY-MUTABLE | Skills, research frontier, changelogs, memory | Any runtime; changes logged here |
| EPHEMERAL | Cached data, auto-generated files (CAPABILITIES.md, pulse.json) | Scripts only; logged on schema changes |

---

## Changelog

### 2026-04-19 — scripts/validate_graph.py — CREATE
**Tier:** FREELY-MUTABLE (new script)
**What changed:** Built Obsidian graph integrity checker. Handles markdown-table `\|` escapes, code-block exclusion, path-first + Obsidian-fuzzy + stem-fallback resolution. Reports broken links, orphans, top connectors. Exits nonzero on broken links (pre-commit-ready).
**Why:** Closes [[CAPABILITY_GAPS]] Gap #4. Earlier graph pass was manual; automation means every future commit can verify graph integrity.
**Confidence:** 0.93
**Cycle:** 2

### 2026-04-19 — brain/INDEX.md — UPDATE
**Tier:** FREELY-MUTABLE
**What changed:** Added RESEARCH_FRONTIER, QUICK_REFERENCE, ENV_STRUCTURE, SHARED_DB, CHANGELOG, OKRs, BRANDS, accounts/, brain/AGENTS, behavioral-finance-guard. INDEX now at 52 outbound wikilinks (up from 44).
**Why:** Every new node must connect to the graph hub within 1 hop.
**Confidence:** 1.0

### 2026-04-19 — brain/accounts/ — CREATE (10 files)
**Tier:** GOVERNED-MUTABLE (new subdirectory)
**What changed:** Mirrored Bravo's `brain/clients/` pattern. Created `accounts/README.md` registry + 9 account briefs (Wise Business USD, Stripe, Kraken, OANDA, Wealthsimple TFSA/FHSA/RRSP/Crypto, RBC Checking). Each brief: purpose, access, tax treatment, risk flags, maintenance cadence, relevant skills.
**Why:** Portfolio-level CFO oversight needs account-specific briefs. Previously all account context was scattered across USER.md + skill files; now canonical per-account.
**Confidence:** 0.92
**Cycle:** 2

### 2026-04-19 — brain/SHARED_DB.md — CREATE
**Tier:** SEMI-MUTABLE
**What changed:** Documented Atlas's view of the shared Supabase schema. Catalogued shared tables (agent_traces, skill_activation, memories, self_modification_log, session_notes) + Atlas-owned tables (net_worth_snapshots, tax_reserve_ledger, receipt_cache, spend_approvals, stock_picks, macro_regime_log). Current instrumentation status: mostly NOT emitting.
**Why:** Required for trace telemetry build. Makes the gap concrete: what schema exists, what's being written, what's missing.
**Confidence:** 0.85 (some shared tables are Bravo-defined; schema confirmed cross-repo)
**Cycle:** 2

### 2026-04-19 — brain/RESEARCH_FRONTIER.md — CREATE
**Tier:** FREELY-MUTABLE
**What changed:** Active research queue. 5 IN-STUDY entries (Minsky, Adaptive Markets / Lo, Mehrling, Reinhart-Rogoff, Goetzmann), 8 WATCHLIST entries (Damodaran, Mauboussin, Swensen, Tetlock, Marks memos full corpus, Grant's, Matt Levine, Taleb statistical-fat-tails). Integration rules: no promotion without a real decision application.
**Why:** Canon integration needs a pipeline. Prevents "read-once, forget" cycle.
**Confidence:** 0.90
**Cycle:** 2

### 2026-04-19 — brain/BRANDS.md — CREATE
**Tier:** GOVERNED-MUTABLE
**What changed:** Portfolio brand registry with per-brand CFO-scoped context. 5 brands (OASIS, Bennett, PropFlow, SunBiz, Nostalgic) + portfolio-level rules on concentration + GM hurdles + tax-efficient sequencing.
**Why:** Brand-level unit economics live in `cfo_pulse.json.brand_economics` (machine-readable) but qualitative context (contract terms, retention risk, strategic directives) needs prose form.
**Confidence:** 0.88
**Cycle:** 2

### 2026-04-19 — brain/QUICK_REFERENCE.md — CREATE
**Tier:** FREELY-MUTABLE
**What changed:** 1-page routing cheat sheet. Session-start order, routing tables by intent (money, tax, research, spend gate, behavioral), non-negotiables from SOUL, current money numbers, session-end checklist.
**Why:** Compresses 38 outbound links into one reference Atlas hits first. Mirrors Bravo's QUICK_REFERENCE pattern.
**Confidence:** 0.95

### 2026-04-19 — brain/OKRs.md — CREATE
**Tier:** GOVERNED-MUTABLE
**What changed:** Q2 2026 OKRs set. 5 objectives: (1) $10K floor + concentration < 70%, (2) taxes + CCPC prep, (3) trace telemetry + cycle 2 infra, (4) research-frontier integration, (5) Business-in-a-Box CFO role maturity.
**Why:** Quarterly discipline. Matches Bravo's OKR pattern.
**Confidence:** 0.80 (targets set; execution pending)

### 2026-04-19 — brain/ENV_STRUCTURE.md — CREATE
**Tier:** SEMI-MUTABLE (credentials scaffold)
**What changed:** Documented every env var Atlas needs, with priority labels (REQUIRED/CORE/OPTIONAL/CLONE-ONLY). Covers Anthropic, Supabase, Telegram, Stripe, Wise, Kraken, OANDA, Gmail, research APIs.
**Why:** Business-in-a-Box buyers need a clone-ready credentials manifest. Mirrors Bravo's CREDENTIALS_SCAFFOLD.md pattern.
**Confidence:** 0.92

### 2026-04-19 — brain/CHANGELOG.md — CREATE
**Tier:** FREELY-MUTABLE (new file)
**What changed:** Created this changelog, mirroring Bravo's CHANGELOG pattern.
**Why:** CC requested file-structure parity with Bravo. A self-modification log is a pre-requisite for responsible self-improvement — no change without a paper trail.
**Confidence:** 0.95
**Cycle:** 2

### 2026-04-19 — skills/behavioral-finance-guard/ — CREATE
**Tier:** FREELY-MUTABLE (new skill, PROBATIONARY)
**What changed:** 9-bias checklist skill (loss aversion, mental accounting, anchoring, sunk-cost, disposition effect, overconfidence, recency, herding, framing). Sources: Kahneman-Tversky, Thaler, Munger, Shefrin-Statman, Cialdini, Housel. Output format: pulse-writable JSON; reframes as questions, never lectures; never overrules operator.
**Why:** Directly applies 4 Knowledge Frontier entries (Kahneman, Thaler + related). Operator has stated behavioral tendencies ("bad cycles" in USER.md); skill surfaces biases before decisions.
**Confidence:** 0.82
**Cycle:** 2

### 2026-04-19 — brain/CFO_CANON.md — EXTEND (Knowledge Frontier section)
**Tier:** SEMI-MUTABLE
**What changed:** Added 18 new entries across 6 domains (capital structure, portfolio theory, behavioral finance, working capital, growth investing, international tax, operational discipline) + 5 research-watchlist entries.
**Why:** CC directive to extend canonical knowledge. Each entry names the framework + practical decision it unlocks + status gate for promotion to full pillar.
**Confidence:** 0.88
**Cycle:** 2

### 2026-04-19 — brain/CFO_CANON.md — EXTEND (Knowledge Frontier section)
**Tier:** SEMI-MUTABLE
**What changed:** Added 18 new entries across 6 domains: capital structure (M-M, Pecking Order, Trade-off), portfolio theory (Markowitz, CAPM, Fama-French), behavioral finance (Kahneman-Tversky, Thaler), working capital (CCC, Crabtree, Michalowicz), growth investing (O'Neil, Lynch, Buffettology), international tax (BEPS 2.0, CRS, FATCA, Henley), operational discipline (Pacioli, Porter, Collins). Plus 5-entry research-frontier watchlist (Minsky, Lo, Mehrling, Reinhart-Rogoff, Goetzmann).
**Why:** CC directive to "research new theories for Atlas's specific qualities and qualifications. Keep extending knowledge." Canon was previously 10-pillar + 13-next-tier; now 10-pillar + 13-next-tier + 18-frontier + 5-watchlist.
**Confidence:** 0.88 — frameworks are well-established; practical integration pending first use.
**Cycle:** 2

### 2026-04-19 — brain/INDEX.md — CREATE
**Tier:** FREELY-MUTABLE (new file)
**What changed:** Created the Obsidian graph hub with wikilinks to every brain, memory, skill, and data node.
**Why:** Obsidian graph was dust-cloud — zero wikilinks across 124 files. Graph rendered no edges. INDEX serves as the dense hub.
**Confidence:** 0.95
**Cycle:** 1 (wiki-pass)

### 2026-04-19 — brain/SOUL.md — UPDATE (V3.0 → V3.1)
**Tier:** IMMUTABLE (CC authorized via self-improvement brief)
**What changed:** Stripped all pre-pivot trading references from "What Atlas IS NOT" section. Added Business-in-a-Box clonable-CFO framing. Added Rule #11 (no auto credential rotation). Added wikilinks to INDEX, CFO_CANON, AGENT_ORCHESTRATION, skills.
**Why:** Bravo's gap audit flagged SOUL as still carrying trading-era language. Product architecture requires Atlas to be role-defined positively, not defined-by-what-it-was.
**Confidence:** 0.95
**Cycle:** 1

### 2026-04-19 — brain/CFO_CANON.md — CREATE
**Tier:** SEMI-MUTABLE (new canonical doc)
**What changed:** Created the 10-pillar canonical framework library (Buffett/Munger, Graham, Taleb ×2, CRA guides, CPA Canada, Fisher, Marks, Dalio, Bernstein) + 13 next-tier voices + 7 anti-canon rejections.
**Why:** Every Atlas recommendation now cites a pillar. Maven has MARKETING_CANON; Atlas needed the equivalent to enforce diagnostic rigor per MISTAKES § execution-before-diagnosis.
**Confidence:** 0.92
**Cycle:** 1

### 2026-04-19 — skills/unit-economics-validation/ — CREATE
**Tier:** FREELY-MUTABLE (new skill, PROBATIONARY status)
**What changed:** Built 5-check validator for Maven ad-spend requests: LTV:CAC ≥ 3, payback ≤ 12mo, positive contribution margin, concentration/runway gate, T2125 deductibility.
**Why:** Gap audit Gap A. Maven's pending $1,200/mo pulse-lead-gen request triggered need for a formal validator rather than ad-hoc judgment. Sources: Graham, Buffett, Skok, Hormozi, CPA Canada.
**Confidence:** 0.88 (probationary — promotes to validated after 3 successful approvals hitting CAC within ±15%)
**Cycle:** 1

### 2026-04-19 — data/pulse/cfo_pulse.json — EXTEND (brand_economics)
**Tier:** EPHEMERAL (runtime state) but schema is GOVERNED-MUTABLE
**What changed:** Added `brand_economics` object with per-brand MRR, gross margin (INFERRED vs PLACEHOLDER labels), retention, notes. Added `portfolio_summary.hhi_concentration_index = 8245`.
**Why:** Aggregate MRR hid distributional risk. HHI quantifies "94% Bennett" as a number Bravo and Atlas watch move over time.
**Confidence:** 0.85 (placeholders need real cohort data to firm up)
**Cycle:** 1

### 2026-04-19 — .git/hooks/pre-commit — CREATE
**Tier:** GOVERNED-MUTABLE
**What changed:** Installed pre-commit hook blocking `.env` and `.env.*` (allows `.env.example`, `.env.template`).
**Why:** Belt-and-suspenders on top of gitignore. Historical audit confirmed zero leaks, hook prevents future accidents.
**Confidence:** 0.98

### 2026-04-19 — memory/MISTAKES.md — EXTEND (CFO-Era section)
**Tier:** FREELY-MUTABLE
**What changed:** Added 5 CFO-era mistakes on top of existing trading-era archive. Meta-pattern documented: trading-era optimized for execution velocity; CFO-era optimizes for diagnostic rigor.
**Why:** Protocol 4 of [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] requires root-cause logging. Each mistake paired with a specific CFO-era prevention rule.
**Confidence:** 0.90
**Cycle:** 1

### 2026-04-19 — memory/PATTERNS.md — EXTEND (CFO-Era section)
**Tier:** FREELY-MUTABLE
**What changed:** Added 4 PROBATIONARY CFO-era patterns on top of existing trading-era archive. Patterns: pulse-gated handshake, canon-backed decisions, brand-level economics, skin-in-the-game self-check.
**Why:** Protocol 4 pattern logging. All 4 awaiting 3 successful re-uses for promotion to VALIDATED.
**Confidence:** 0.82
**Cycle:** 1

### 2026-04-19 — memory/CAPABILITY_GAPS.md — CREATE
**Tier:** FREELY-MUTABLE (new file, in-repo vault copy)
**What changed:** Logged 4 gaps: Supabase trace telemetry (HIGH), /briefing skill (MEDIUM), /briefing slash-command registration (paired), Obsidian graph orphan scanner (LOW).
**Why:** Every gap encountered during self-improvement surfaces here before any build.
**Confidence:** 1.0

### 2026-04-19 — brain/STATE.md — REFRESH
**Tier:** GOVERNED-MUTABLE
**What changed:** Updated last_updated to 2026-04-19. Skill count 16 → 17. Brain-file count 12 → 13. Memory-file count 23 → 25. Added pre-commit-guard row. Added Last Self-Improvement Cycle section.
**Why:** STATE must reflect current operational reality at session start.
**Confidence:** 0.98

---

## Changelog maintenance rules

1. **Every self-modification must append here.** No exceptions. If a change lacks a paper trail, it didn't happen.
2. **Format discipline.** Use the template at top. Concision over prose.
3. **Confidence scores matter.** < 0.7 means the change is experimental and should trigger a re-review within 30 days.
4. **Cycle number links to self-improvement loops.** Ad-hoc changes get `"Cycle: ad-hoc"`.
5. **Tier determines change authority.** IMMUTABLE requires explicit CC authorization in-session. Everything else is agent-writable but logged.
6. **When schema changes land in EPHEMERAL files (pulse.json), log the schema change here, not the value change.** Value changes are routine; schema changes are architectural.
