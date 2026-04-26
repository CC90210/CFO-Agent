---
tags: [index, hub, navigation, graph-center]
---

# ATLAS — Graph Hub

> Every brain file, skill, memory, and data artifact links from here. This is the center of Atlas's knowledge graph. If you open the Obsidian graph view, this node should be the one with the most edges.

## Identity & State (load first, every session)

- [[SOUL]] — who Atlas is (V3.1, immutable)
- [[USER]] — CC's financial profile
- [[STATE]] — current operational snapshot
- [[DASHBOARD]] — live money numbers
- [[HEARTBEAT]] — system health indicators

## Canon & Doctrine

- [[CFO_CANON]] — 10 pillars + 13 next-tier + 18 frontier additions + 5 watchlist
- [[RESEARCH_FRONTIER]] — what Atlas is actively studying; promotion pipeline to canon
- [[AGENT_ORCHESTRATION]] — 3-agent C-Suite contract (Atlas ↔ Bravo (CEO, out-of-vault) ↔ Maven (CMO, out-of-vault))
- [[INTERACTION_PROTOCOL]] — how Atlas talks to CC
- [[BRAIN_LOOP]] — session start/end checklist
- [[QUICK_REFERENCE]] — routing cheat sheet
- [[STRUCTURE]] — file ownership map across 4 AI runtimes
- [[AGENTS]] — Atlas agent registry (CFO era, post-pivot routing + Data Integrity rule)
- Runtime identity files (project root, read by their CLIs): `CLAUDE.md` (Claude Code), `AGENTS.md` (Codex / Antigravity), `GEMINI.md` (Gemini CLI). All three carry the Data Integrity rule.
- [[ENV_STRUCTURE]] — credentials scaffold for cloning
- [[SHARED_DB]] — Supabase schema + trace-telemetry contract
- [[TAX_PLAYBOOK_INDEX]] — entry to the 59-doc tax library
- [[CHANGELOG]] — self-modification log

## Operational

- [[CAPABILITIES]] — auto-generated skill + tool registry
- [[OKRs]] — quarterly CFO objectives (Q2 2026 live)
- [[GROWTH]] — growth metrics & targets
- [[RISKS]] — active risk register
- [[AGENTS]] — agent roster
- [[BRANDS]] — portfolio brand registry (OASIS, Bennett, PropFlow, SunBiz, Nostalgic)
- [[accounts/README|accounts/]] — per-account briefs (Wise, Stripe, Kraken, OANDA, Wealthsimple TFSA/FHSA/RRSP/Crypto, RBC)
- [[brain/AGENTS|AGENTS]] — in-brain agent roster summary (distinct from root `AGENTS.md` runtime identity)

## Skills (playbooks Atlas ships with)

Spend governance + behavioral oversight
- [[skills/unit-economics-validation/SKILL|unit-economics-validation]] — Maven ad-spend gate (LTV/CAC/payback)
- [[skills/behavioral-finance-guard/SKILL|behavioral-finance-guard]] — 9-bias scan on operator money decisions
- [[skills/financial-health-check/SKILL|financial-health-check]] — concentration + runway inputs
- [[skills/position-sizing/SKILL|position-sizing]] — equity position sizing

Tax & compliance
- [[skills/tax-optimization/SKILL|tax-optimization]]
- [[skills/tax-loss-harvesting/SKILL|tax-loss-harvesting]]
- [[skills/quarterly-tax-review/SKILL|quarterly-tax-review]]
- [[skills/incorporation-readiness/SKILL|incorporation-readiness]]
- [[skills/departure-tax-planning/SKILL|departure-tax-planning]]
- [[skills/cross-border-compliance/SKILL|cross-border-compliance]]
- [[skills/crypto-acb-tracking/SKILL|crypto-acb-tracking]]
- [[skills/compliance-monitor/SKILL|compliance-monitor]]

Planning & ops
- [[skills/financial-planning/SKILL|financial-planning]]
- [[skills/accounting-advisor/SKILL|accounting-advisor]]
- [[skills/cash-flow-invoicing/SKILL|cash-flow-invoicing]]
- [[skills/income-tier-monitoring/SKILL|income-tier-monitoring]]
- [[skills/portfolio-rebalancing/SKILL|portfolio-rebalancing]]

Meta
- [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] — the 4-protocol loop
- [[skills/trade-protocol/SKILL|trade-protocol]] — trading-era execution protocol (retained for reference)

## Memory (operational intelligence)

- [[MISTAKES]] — root-caused errors + prevention rules
- [[PATTERNS]] — validated + probationary approaches
- [[CAPABILITY_GAPS]] — gaps identified, awaiting build trigger
- [[SESSION_LOG]] — session-by-session narrative
- [[DECISIONS]] — key decisions + rationale
- [[LONG_TERM]] — long-horizon goals + strategies
- [[ACTIVE_TASKS]] — current open tasks
- [[SOP_LIBRARY]] — standard operating procedures
- [[STRATEGY_ANALYSIS]] — market + business strategy notes

## Cross-Agent (read-only)

- Bravo (CEO) pulse: `C:\Users\User\Business-Empire-Agent\data\pulse\ceo_pulse.json` — out-of-vault
- Maven (CMO) pulse: `C:\Users\User\CMO-Agent\data\pulse\cmo_pulse.json` — out-of-vault
- Atlas's own pulse: `data/pulse/cfo_pulse.json` — the write-side of the handshake

## External memory (Claude Code auto-memory, out-of-vault)

Lives at `C:\Users\User\.claude\projects\c--Users-User-APPS-CFO-Agent\memory\`. Not graphed by Obsidian; mirrored into this repo's `memory/` for the in-vault nodes above.

## Data artifacts

- `data/pulse/cfo_pulse.json` — machine-readable state (Atlas writes, Bravo + Maven read)
- `data/picks/` — saved stock research picks
- `data/manual_balances.json` — non-API account entries
- `data/crypto_trades.csv` — ACB source
- `data/target_allocation.json` — portfolio targets
- `data/receipts_cache.json` — Gmail receipt cache

## The traversal rule

When you're unsure where to write something, start here. Every node in the graph is either linked from this hub, or linked from something that's linked here. If a new file doesn't show up on the graph within 1 hop of INDEX, it's orphaned — add a link.
