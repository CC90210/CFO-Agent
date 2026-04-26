---
tags: [supabase, database, schema, shared-state, cross-agent]
---

# SHARED_DB — Supabase Schema (Atlas's View)

> The 3-agent C-Suite shares a single Supabase project: `phctllmtsogkovoilwos`. Every agent (Atlas, Bravo, Maven) writes to the same project but owns different tables or owns rows scoped by `agent` column. RLS enforces write sovereignty.
>
> Authoritative schema is in Supabase directly; this doc is the Atlas-side cheat sheet for what we read, what we write, and what telemetry we need to instrument.
>
> Neighbors: [[INDEX]] · [[ENV_STRUCTURE]] · [[AGENT_ORCHESTRATION]] · [[CFO_PULSE_CONTRACT]] · [[CAPABILITY_GAPS]] · [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]].
>
> **Cross-agent contracts:** [[CFO_PULSE_CONTRACT]] — the machine-checkable
> hand-off Atlas writes to `data/pulse/cfo_pulse.json` that Maven + Bravo
> read. Validator: `cfo/pulse_schema.py`. Run on every write AND every read.

## Project details

| Field | Value |
|-------|-------|
| Project ref | `phctllmtsogkovoilwos` |
| URL | `https://phctllmtsogkovoilwos.supabase.co` |
| Region | (per Bravo's setup) |
| RLS enabled | YES on every table — mandatory |
| Owner agent | Bravo (CEO) created the project; Atlas and Maven are sovereign co-writers |

## Credentials

Env vars documented in [[ENV_STRUCTURE]]. Atlas uses:
- `SUPABASE_URL` (read by all code paths)
- `SUPABASE_ANON_KEY` (default client-side reads)
- `SUPABASE_SERVICE_ROLE_KEY` (Atlas server-side writes — treat like root; scope minimally)

## Atlas's table scope

Atlas reads from any table but writes only to rows marked `agent = 'atlas'` on shared tables, or to Atlas-owned dedicated tables.

### Shared tables (agent-scoped via RLS)

| Table | Atlas's operations | Schema highlights |
|-------|---------------------|-------------------|
| `agent_traces` | WRITE rows with `agent='atlas'`; READ any | `id, agent, action, input_tokens, output_tokens, execution_time_ms, outcome, created_at, meta jsonb` |
| `skill_activation` | WRITE for Atlas skills; READ any | `id, agent, skill_id, frequency, confidence, recency, score, updated_at` |
| `memories` | WRITE with `agent='atlas'`; READ any | `id, agent, category, content, embedding vector(1536), created_at` — enables cross-agent pattern sharing per [[skills/self-improvement-protocol/SKILL\|self-improvement-protocol]] Protocol 4 |
| `self_modification_log` | WRITE for Atlas self-mods; READ own | Mirrors [[CHANGELOG]] in structured form |
| `session_notes` | WRITE Atlas sessions; READ any | `id, agent, session_id, started_at, ended_at, summary jsonb` |

### Atlas-owned tables (exclusive)

Tables Atlas is the sole writer for. Other agents may read to understand CFO state.

| Table | Purpose | Schema highlights |
|-------|---------|-------------------|
| `net_worth_snapshots` | Historical daily/weekly liquid totals | `id, captured_at, total_liquid_cad, breakdown jsonb, source` |
| `tax_reserve_ledger` | Quarterly tax-reserve tracking | `id, period, mrr_cad, reserve_required_cad, reserve_actual_cad, shortfall_cad, computed_at` |
| `receipt_cache` | Gmail receipt dedup + categorization | `id, gmail_message_id, vendor, amount_cad, category, t2125_line, parsed_at, raw_snippet` |
| `spend_approvals` | Atlas's approval decisions for Maven requests | `id, request_id, campaign, brand, requested_cad, approved_cad, decision, checks jsonb, rationale, decided_at` |
| `stock_picks` | Atlas's research output | `id, ticker, thesis, entry_price, entry_window, exit_target, stop_loss, conviction, horizon, picked_at, outcome jsonb` |
| `macro_regime_log` | Dalio-style regime classifications | `id, regime, growth_direction, inflation_direction, started_at, ended_at, rationale` |

## Current instrumentation status (2026-04-19)

| Table | Atlas emits? | Priority gap |
|-------|:-:|--------------|
| `agent_traces` | **NO** | HIGH — blocker for [[skills/self-improvement-protocol/SKILL\|self-improvement-protocol]] Protocol 2 |
| `skill_activation` | **NO** | HIGH — paired with agent_traces |
| `memories` | partial (manually; via Claude Code memory tool) | MEDIUM |
| `self_modification_log` | **NO** | MEDIUM — [[CHANGELOG]] is the human form; structured form missing |
| `session_notes` | **NO** | LOW |
| `net_worth_snapshots` | **NO** | MEDIUM — DASHBOARD is live but not historized |
| `tax_reserve_ledger` | **NO** | MEDIUM — computed ephemerally, not stored |
| `receipt_cache` | partial (JSON file, not Supabase) | MEDIUM — `data/receipts_cache.json` should migrate |
| `spend_approvals` | **NO** | MEDIUM — pulse has latest decision only |
| `stock_picks` | partial (markdown in `data/picks/`, not Supabase) | LOW |
| `macro_regime_log` | **NO** | LOW |

The pattern: Atlas emits richly to human-readable files (pulse JSON, memory markdown, data/picks markdown) but not to Supabase structured storage. Closing this gap is [[OKRs]] Objective 3.

## Cross-agent read paths Atlas relies on

Atlas READS from Bravo's and Maven's rows in shared tables. The canonical cross-agent read is via their pulse files (faster, simpler, no network round-trip) but Supabase supplements when:

- **Historical trends:** pulse is latest-snapshot only; Supabase has history.
- **Semantic search:** `memories` table with embeddings enables "did any agent already solve this?" queries per [[skills/self-improvement-protocol/SKILL\|self-improvement-protocol]] Protocol 4 cross-agent pattern sharing.
- **Aggregate queries:** "how much has the CMO requested in total ad spend this quarter?" — trivial SQL, painful from pulse snapshots.

## RLS policies (summary — Bravo owns the canonical definitions)

```
-- Every agent may SELECT any row
CREATE POLICY "any agent can read" ON <table>
  FOR SELECT USING (true);

-- Only the owning agent may INSERT/UPDATE/DELETE
CREATE POLICY "own-agent writes only" ON <table>
  FOR ALL USING (agent = current_setting('request.jwt.claims', true)::json->>'agent_id')
           WITH CHECK (agent = current_setting('request.jwt.claims', true)::json->>'agent_id');
```

JWT carries `agent_id`. Atlas's service-role JWT carries `agent_id='atlas'`. Enforced at every write.

## Tools Atlas needs (gaps per [[CAPABILITY_GAPS]])

- `scripts/supabase_tool.py` — query/insert/upsert wrapper. **MISSING.** Highest-priority build.
- `scripts/trace.py` — helper that every Atlas entry point calls to emit to `agent_traces`. **MISSING.**
- Migration tooling — Atlas uses Bravo's `scripts/apply_migration.py` pattern (not yet copied). For now, schema changes go through Bravo's repo.

## What goes to Supabase vs what stays in files

| Use case | Storage |
|---|---|
| Identity + doctrine (SOUL, CFO_CANON) | Files — version-controlled, human-editable, never overwritten |
| Current state snapshot (STATE, DASHBOARD) | Files — human-readable |
| Machine-readable current state (cfo_pulse) | Files — cross-agent pulse protocol; simple |
| Historical time-series (net worth over time, tax reserve over quarters) | Supabase — queryable |
| Cross-agent semantic memory | Supabase `memories` with embeddings |
| Skill telemetry (firings, success rate, tokens) | Supabase `agent_traces` + `skill_activation` |
| Session logs | Both — human copy in `memory/SESSION_LOG.md`; structured copy in `session_notes` |
| Pattern / mistake ledger | Both — human in `memory/MISTAKES.md` + `memory/PATTERNS.md`; structured in `memories` for cross-agent search |

## Migration path (when trace telemetry ships)

1. Build `scripts/supabase_tool.py` — thin wrapper over `supabase-py` with `query`, `insert`, `upsert` subcommands and `--agent atlas` scope enforcement.
2. Build `scripts/trace.py` — called from every CLI entry + Telegram handler. Emits `agent_traces` row with action, tokens, time, outcome.
3. Backfill one week of manual `memories` entries from existing MISTAKES/PATTERNS markdown.
4. Run [[skills/self-improvement-protocol/SKILL|self-improvement-protocol]] Protocol 2 full pass against real data.
5. Log promotion in [[CHANGELOG]]; promote the capability gap to CLOSED.

## Caveats

- **Never trust Supabase to be reachable.** If the service role key fails, Atlas falls back to file-based state and surfaces the outage. Atlas never blocks on Supabase.
- **Never write PII or credentials to any row.** Secrets stay in `.env`; referrer stores pointers only.
- **Embeddings cost tokens.** The `memories` table uses OpenAI or Claude embeddings — budget accordingly.
