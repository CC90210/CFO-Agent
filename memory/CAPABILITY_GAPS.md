---
tags: [capability-gaps, self-improvement, atlas]
created: 2026-04-19
---

# ATLAS — Capability Gaps Log

> Per [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] Protocol 3, each gap gets logged here before any new skill is built. Gaps are PROBATIONARY until triggered 3+ times, at which point they promote to build-queue.
>
> Neighbors: [[MISTAKES]] · [[PATTERNS]] · [[CFO_CANON]] · [[INDEX]].

---

## Gap: Supabase trace telemetry (blocker for Protocol 2 OPTIMIZE)

- **Identified**: 2026-04-19
- **Trigger**: CC's self-improvement brief cites `python scripts/supabase_tool.py query "SELECT action, COUNT(*), AVG(execution_time_ms) FROM agent_traces WHERE agent='atlas'..."` but `scripts/supabase_tool.py` does not exist in `CFO-Agent/scripts/`. Existing: `build_capabilities.py`, `install_pm2_startup.ps1`, `refresh.py`, `validate_memory.py`. No trace emission, no query tool.
- **Frequency**: 2 asks so far (initial brief + re-brief)
- **Priority**: HIGH — Protocol 2 of the self-improvement loop is non-functional without it.
- **Proposed build**:
  - `scripts/supabase_tool.py` — wrapper over shared Supabase project `phctllmtsogkovoilwos` with `query`, `insert`, `upsert` subcommands and `--project {atlas|bravo|maven}` scope flag.
  - `scripts/trace.py` — helper imported by Atlas CLI entry points to emit rows into `agent_traces` (schema per [[AGENT_ORCHESTRATION]]).
  - Instrument `main.py` + `telegram_bridge.py` handlers to call `trace()` on every invocation.
- **Sources to seed**: Bravo's `Business-Empire-Agent/scripts/supabase_tool.py` (read-only reference — cross-repo no-copy rule).
- **Status**: PROBATIONARY. Surface to CC before building.

## Gap: /briefing skill

- **Identified**: 2026-04-19
- **Trigger**: CC's brief — "Run /briefing at session end to generate a plain-English report." No skill at `skills/briefing/` or slash command mapped in CLAUDE.md.
- **Frequency**: 1 ask so far (triggers build on 2nd per gap-log rule)
- **Priority**: MEDIUM — session-end report is currently hand-written.
- **Proposed build**:
  - `skills/briefing/SKILL.md` — structured output template: status delta since last briefing, new decisions, open blockers, money numbers, what CC should act on. Hard limits on length.
  - Pulls from: `data/pulse/cfo_pulse.json`, [[STATE]], [[MISTAKES]] new entries, session git log.
  - Voice: per `memory/feedback_plain_language.md` + `memory/feedback_telegram_brevity.md` (external auto-memory).
- **Sources to seed**: CPA Canada financial-reporting standards (audit-defensible summary); McKinsey "one-page brief" template.
- **Status**: PROBATIONARY. Wait for 2nd ask before building.

## Gap: /briefing slash-command registration

- **Identified**: 2026-04-19
- **Trigger**: paired with the skill gap above. Slash commands need the skill AND a harness registration.
- **Priority**: paired build.
- **Status**: PROBATIONARY.

## Gap: Obsidian graph orphan scanner — CLOSED 2026-04-19

- **Identified**: 2026-04-19
- **Built**: 2026-04-19 — same cycle. `scripts/validate_graph.py` handles markdown-table \| escapes, code-block exclusion, path-first + fuzzy-path + stem-fallback resolution. Reports broken links, orphans, and top connectors. Exits nonzero if broken links exist (pre-commit-ready).
- **Validation run 2026-04-19**: 142 files scanned, 409 wikilinks, **0 broken, 0 orphans** in brain/memory/skills.
- **Status**: CLOSED — moved from PROBATIONARY to SHIPPED.

---

## Review cadence

Revisit this file weekly during Protocol 2 runs. Promote PROBATIONARY gaps that recur to build-queue. Drop gaps that haven't recurred in 60 days.
