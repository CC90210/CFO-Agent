# STRUCTURE.md — File Ownership & Multi-Agent Convention

> **Purpose:** Every file in this repo is touched by up to 4 AI runtimes (Claude Code, Antigravity, Codex, Gemini) plus CC directly. This document defines who owns what, preventing write conflicts and ensuring all runtimes find things the same way.
>
> **Rule:** If you're about to create a NEW file, check this map first. If the data belongs in an existing file, update it in-place — don't spawn a new one.
>
> Neighbors: [[INDEX]] · [[SOUL]] · [[STATE]] · [[AGENT_ORCHESTRATION]].

Last updated: 2026-04-19

---

## Directory Map

### `brain/` — Agent Knowledge (READ by all runtimes, WRITE by any runtime with a good reason)

| File | Owner | Purpose | Update Frequency |
|------|-------|---------|-----------------|
| `USER.md` | Any runtime | CC's complete financial profile | When financials change |
| `SOUL.md` | CC (manual) | Atlas personality & philosophy | Rarely |
| `STATE.md` | Any runtime | Current system state snapshot | Every session |
| `CAPABILITIES.md` | `scripts/build_capabilities.py` | Auto-generated capability registry | Auto-rebuilt on session start |
| `AGENT_ORCHESTRATION.md` | Any runtime | Atlas↔Bravo contract, 4-runtime rules | When protocol changes |
| `BRAIN_LOOP.md` | Any runtime | Session start/end checklist | When process changes |
| `INTERACTION_PROTOCOL.md` | Any runtime | How Atlas talks to CC | When communication style changes |
| `DASHBOARD.md` | Any runtime | Financial dashboard state | When balances update |
| `GROWTH.md` | Any runtime | Growth metrics & targets | Monthly |
| `RISKS.md` | Any runtime | Active risk register | When risks change |
| `HEARTBEAT.md` | Any runtime | System health indicators | Auto/periodic |
| `AGENTS.md` | Any runtime | Agent roster summary | When agents change |
| `TAX_PLAYBOOK_INDEX.md` | Any runtime | Index of all 59+ tax docs | When docs added |
| `STRUCTURE.md` | Any runtime | THIS FILE — file ownership map | When structure changes |

### `memory/` — Operational Intelligence (ALL runtimes read & append)

Append-only logs. These files grow over time. Any runtime may add entries.

| File | Purpose |
|------|---------|
| `SESSION_LOG.md` | Narrative log of every session — what happened, what changed |
| `MISTAKES.md` | Errors made, lessons learned — prevents repeating failures |
| `PATTERNS.md` | Recurring patterns observed across sessions |
| `DECISIONS.md` | Key decisions made with rationale |
| `LONG_TERM.md` | Long-horizon goals and strategies |
| `SOP_LIBRARY.md` | Standard operating procedures |
| `STRATEGY_ANALYSIS.md` | Market/business strategy notes |
| `ACTIVE_TASKS.md` | Current open tasks and their status |

### `.claude/` — Claude Code-Specific Configuration

| Path | Purpose | Notes |
|------|---------|-------|
| `.claude/settings.local.json` | Permissions (additional directories) | Points to Claude auto-memory |
| `.claude/skills/*.md` | Claude Code skill routing | 7 skills: tax, research, CFO ops, compliance, accounting, international, planning, system |

### Claude Auto-Memory (EXTERNAL — Claude Code only)

**Path:** `C:\Users\User\.claude\projects\c--Users-User-APPS-CFO-Agent\memory\`

This directory is managed automatically by Claude Code. Other runtimes should READ but not WRITE here. Contains:
- `MEMORY.md` — auto-regenerated index
- `user_*.md` — CC's profile data
- `feedback_*.md` — CC's communication preferences
- `project_*.md` — project state records
- `reference_*.md` — technical references

### `skills/` — Domain Playbooks (ALL runtimes read)

16 subdirectories, each with a `SKILL.md` playbook. These are detailed domain guides that any runtime loads when answering questions in that domain.

**Convention:** One `SKILL.md` per domain. Don't create additional files in skill directories.

### `docs/` — Tax & Financial Knowledge Base (ALL runtimes read, rarely write)

71 files, ~4.2 million characters. This is the moat. Organized by `ATLAS_<TOPIC>.md` naming.

**Convention:** Never delete docs. If content is outdated, update in-place. New docs follow `ATLAS_<TOPIC>.md` naming.

### `cfo/` — CFO Python Modules (Codex/Claude Code write, all read)

Production Python code. 8 modules covering accounts, cashflow, crypto ACB, dashboard, Gmail receipts, pulse, rebalancing, setup wizard.

### `research/` — Stock Research Modules (Codex/Claude Code write, all read)

Production Python code. 10 modules covering the research pipeline.

### `finance/` — Financial Engines (Codex/Claude Code write, all read)

Production Python code. Tax calculator, financial advisor, budget tracker, wealth tracker.

### `data/` — Runtime Data (auto-generated, all runtimes read)

| Path | Purpose | Source |
|------|---------|--------|
| `data/pulse/cfo_pulse.json` | Atlas→Bravo/Maven data handshake | `cfo/pulse.py` |
| `data/picks/*.md` | Saved stock research picks | `research/stock_picker.py` |
| `data/manual_balances.json` | Manual account entries | CC or setup wizard |
| `data/crypto_trades.csv` | Historical crypto trades | Manual import |
| `data/target_allocation.json` | Portfolio allocation targets | CC or rebalance command |
| `data/receipts_cache.json` | Gmail receipt cache | `cfo/gmail_receipts.py` |
| `data/cache/` | TTL-cached API responses | Various modules |

### Root Files — Identity & Config

| File | Read By | Purpose |
|------|---------|---------|
| `CLAUDE.md` | Claude Code | Atlas identity + rules for Claude Code |
| `AGENTS.md` | Antigravity, Codex | Atlas identity + rules for Antigravity/Codex |
| `GEMINI.md` | Gemini CLI | Atlas identity + rules for Gemini |
| `README.md` | Humans, GitHub | Project overview |
| `.env` | All Python code | API keys and secrets (NEVER committed) |
| `ecosystem.config.js` | PM2 | Telegram bot process management |
| `main.py` | CLI users | CLI entry point |
| `telegram_bridge.py` | PM2/Telegram | Telegram bot gateway |
| `atlas_tools.py` | Telegram bot | Claude tool-use layer for Telegram |

---

## Multi-Agent Communication Rules

### 1. Single Source of Truth (SSOT)
Every fact lives in ONE place. If it's in `brain/USER.md`, don't duplicate it in a skill file — reference it.

### 2. Update In-Place, Don't Spawn
When data changes, update the existing file. Don't create a new file for the update. This prevents file proliferation across sessions.

### 3. Session Tracking
Every runtime MUST append to `memory/SESSION_LOG.md` at session end, documenting what changed. This is how other runtimes learn what happened.

### 4. Commit Format
All runtimes use: `atlas: <type> — <description>`
Types: `fix`, `feat`, `docs`, `refactor`, `chore`

### 5. Pulse Before Close
If any of these changed during a session: `liquid_cad`, `tax_reserve_required_cad`, `spend_gate`, `open_tax_deadlines` — update `data/pulse/cfo_pulse.json` before closing.

### 6. Read Before Write
Every runtime must read `brain/USER.md` + relevant memory files before making changes. Never assume — check the file.
