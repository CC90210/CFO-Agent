---
tags: [credentials, setup, cloning, security]
purpose: Documentation of every credential Atlas needs. Source-of-truth for `.env` contents on any new machine or buyer clone. NEVER contains real values.
---

# ENV STRUCTURE — Credentials Scaffold

> This file documents every key Atlas needs to run production. Real values live ONLY in `.env` (gitignored, blocked at pre-commit). Do NOT write secrets here — this file is committed.
>
> When cloning Atlas for a new machine or a Business-in-a-Box buyer, use this as the master checklist of what `.env` must contain.
>
> Neighbors: [[INDEX]] · [[SOUL]] · [[STATE]] · [[CAPABILITIES]] · [[SHARED_DB]] · [[AGENT_ORCHESTRATION]].

## Priority Legend

- **[REQUIRED]** — Atlas cannot start without this
- **[CORE]** — Major capability lost if missing
- **[OPTIONAL]** — Feature-specific, nice to have
- **[CLONE-ONLY]** — Only relevant when a buyer clones Atlas

---

## Core AI Layer

At minimum, Anthropic must be set. OpenAI is for the Codex delegation path only.

| Key | Priority | Notes |
|-----|----------|-------|
| `ANTHROPIC_API_KEY` | REQUIRED | Claude API — Atlas's reasoning engine. Get at console.anthropic.com |
| `OPENAI_API_KEY` | OPTIONAL | For Codex cross-delegation paths per global CLAUDE.md doctrine |
| `OPENAI_ORG_ID` | OPTIONAL | If multi-org OpenAI account |

## Database — Supabase (shared with Bravo and Maven)

Single shared project for the 3-agent C-Suite. RLS enforces write sovereignty. Atlas writes only rows tagged `agent: 'atlas'`. See [[SHARED_DB]] for schema.

| Key | Priority | Notes |
|-----|----------|-------|
| `SUPABASE_URL` | REQUIRED | `https://phctllmtsogkovoilwos.supabase.co` |
| `SUPABASE_ANON_KEY` | REQUIRED | Client-side reads (respects RLS) |
| `SUPABASE_SERVICE_ROLE_KEY` | CORE | Server-side writes. Bypasses RLS — treat like a root password |
| `SUPABASE_PROJECT_ID` | CORE | `phctllmtsogkovoilwos` (same as subdomain) |

## Telegram — Atlas bot

| Key | Priority | Notes |
|-----|----------|-------|
| `TELEGRAM_BOT_TOKEN` | REQUIRED | From @BotFather. Runs `telegram_bridge.py`. PM2 process name: `atlas-telegram`. |
| `TELEGRAM_CHAT_ID` | REQUIRED | CC's personal chat ID. Atlas only responds to this one chat in production. |

## Financial account reads (live balances)

### Stripe

| Key | Priority | Notes |
|-----|----------|-------|
| `STRIPE_API_KEY` | CORE | Restricted key: `rk_live_...`. Read-only scope: balance, charges, invoices, customers, subscriptions. NEVER use the publishable key or a full secret key. |
| `STRIPE_ACCOUNT_ID` | OPTIONAL | If querying a connected account |

### Wise (business)

| Key | Priority | Notes |
|-----|----------|-------|
| `WISE_API_TOKEN` | CORE | Personal token scoped to read-only business balances |
| `WISE_PROFILE_ID` | CORE | Business profile ID for Atlas's read path |

### Kraken (crypto)

| Key | Priority | Notes |
|-----|----------|-------|
| `KRAKEN_API_KEY` | CORE | Read-only key (Query Funds + Query Open/Closed Orders). No trade permissions. Ontario: only /USD pairs. |
| `KRAKEN_API_SECRET` | CORE | Paired secret |

### OANDA (gold + forex)

| Key | Priority | Notes |
|-----|----------|-------|
| `OANDA_API_TOKEN` | CORE | Read-only token |
| `OANDA_ACCOUNT_ID` | CORE | Practice vs live account distinguished by env |
| `OANDA_ENVIRONMENT` | CORE | `live` or `practice` |

### Wealthsimple (manual — no public API)

No keys required. Balances entered via `cfo/accounts.py manual` command or `data/manual_balances.json`.

### RBC Checking (manual — no public API)

No keys. Manual balance entry.

## Gmail — receipt ingestion

Atlas pulls receipts from `conaugh@oasisai.work` (Google Workspace) via IMAP. Google Workspace admin + app password required.

| Key | Priority | Notes |
|-----|----------|-------|
| `GMAIL_IMAP_USER` | CORE | `conaugh@oasisai.work` |
| `GMAIL_IMAP_PASSWORD` | CORE | App password (NOT the account password). Generated at myaccount.google.com/security. Requires 2FA + app password enabled on the Workspace user. |
| `GMAIL_IMAP_HOST` | OPTIONAL | Defaults to `imap.gmail.com` |
| `GMAIL_IMAP_PORT` | OPTIONAL | Defaults to `993` (SSL) |

## Research pipeline

| Key | Priority | Notes |
|-----|----------|-------|
| `NEWSAPI_KEY` | OPTIONAL | NewsAPI.org — supplementary news coverage. Free tier = 100 req/day. |
| `ALPHA_VANTAGE_API_KEY` | OPTIONAL | Alpha Vantage fundamentals — free tier = 25 req/day. |
| `FMP_API_KEY` | OPTIONAL | Financial Modeling Prep — broader fundamentals. Free tier limited. |
| `SEC_EDGAR_USER_AGENT` | CORE (if SEC used) | SEC requires a descriptive User-Agent header. Format: `"CFO-Agent Atlas contact@oasisai.work"`. |

## Tax & compliance data

| Key | Priority | Notes |
|-----|----------|-------|
| `CRA_ACCOUNT_ID` | OPTIONAL | Only used if/when CRA My Account API opens for Atlas. Currently blocked at identity verification. |

## Cross-agent read paths (no keys — file-system reads)

Atlas reads the following files as path-only inputs. No credentials needed. Paths may differ on buyer machines — Atlas's pulse reader falls back gracefully.

- `C:\Users\User\Business-Empire-Agent\data\pulse\ceo_pulse.json` — Bravo's pulse
- `C:\Users\User\CMO-Agent\data\pulse\cmo_pulse.json` — Maven's pulse
- `C:\Users\User\Aura-Home-Agent\data\pulse\life_pulse.json` — Aura's pulse (optional 4th agent)

## Machine paths (Windows-specific; buyers on mac/linux adjust)

| Variable | Default | Notes |
|----------|---------|-------|
| `ATLAS_REPO_PATH` | `C:\Users\User\APPS\CFO-Agent` | Atlas's own repo root |
| `ATLAS_MEMORY_PATH` | `C:\Users\User\.claude\projects\c--Users-User-APPS-CFO-Agent\memory\` | Claude Code auto-memory (out-of-vault) |

## Setup verification

Run `python scripts/refresh.py` after populating `.env`. The script:
1. Attempts every live integration
2. Writes `data/pulse/cfo_pulse.json` with `integrations_live` flags
3. Flags missing or rejected keys without dying (so Atlas boots even if secondary integrations fail)

Healthy boot = `integrations_live: {wise_business_usd: true, stripe: true, kraken: true, oanda: true, gmail_receipts: true}`.

## Security posture

1. **`.env` is gitignored** at repo root `.gitignore`.
2. **`.env` is blocked at pre-commit** via `.git/hooks/pre-commit` (installed 2026-04-19).
3. **Restricted scopes everywhere.** Read-only on Stripe + Kraken + Wise + OANDA. Never full secret keys.
4. **No key appears in any log.** Use the `logging` module's filter pattern; never `print()` a config dict.
5. **Credential rotation is manual.** Atlas never auto-rotates — per [[SOUL]] Rule #11.
6. **If a key 401s or 403s**, Atlas marks `needs_rotation: true` in pulse and surfaces to CC. Does not silently retry.

## When cloning Atlas for a buyer

1. Buyer clones CFO-Agent repo.
2. Buyer copies `.env.template` → `.env` (template to be added; currently only `.env.example` exists).
3. Buyer fills in their own keys per this scaffold.
4. Buyer runs `python scripts/refresh.py` → pulse gets populated with their live balances.
5. Buyer's personal config (Montreal floor, concentration thresholds, tax residency) lives in their fork's `brain/USER.md`, not this file.
