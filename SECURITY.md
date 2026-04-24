# Security Policy — Atlas (CFO Agent)

Atlas is the CFO of the OASIS AI C-Suite — it reads bank balances, tax
records, trading signals, and client invoices. Financial data is the
single most sensitive surface in the whole system. This document
describes how we handle credentials, what we promise, and how to report
a vulnerability.

## Reporting a Vulnerability

**Do not open a public GitHub issue for a security vulnerability.**

Please email **security@oasisai.work** (preferred) or
**conaugh@oasisai.work** (fallback) with:

- A description of the issue
- Steps to reproduce (or a proof-of-concept)
- The affected version or commit SHA
- Your assessment of impact

**Response SLA**

| Stage | Target |
|-------|--------|
| Initial acknowledgement | within 48 hours |
| Severity triage | within 5 business days |
| Fix in `main` for critical/high | within 14 days |
| Coordinated public disclosure | 90 days from report, or sooner if a fix ships |

We will credit you in the fix commit and changelog unless you ask to stay
anonymous.

## Supported Versions

Only the latest commit on `main` is actively maintained. Forks and older
tags are not patched. If you are running a pinned commit older than 30
days, pull `main` before reporting — the issue may already be fixed.

## Security Posture

Atlas is installed through the OASIS AI setup wizard
(`github.com/CC90210/CEO-Agent`). The wizard enforces the shared
credential posture:

### Credential handling

- All secrets live in a single `.env.agents` file per install — never
  in source, never in git history, never in CI logs.
- `.env.agents` is in `.gitignore` and `.git/info/exclude`; the setup
  wizard refuses to write to any `.env*` path that is tracked by git.
- On POSIX the file is `chmod 0600` (owner read/write only). On Windows,
  NTFS ACLs inherit from the user home directory.
- Atlas's live API keys (Anthropic, OpenAI, Stripe, brokerage APIs) are
  loaded from `.env.agents` at runtime via `python-dotenv`. They are
  never echoed to stdout, never logged, and never written to the
  session log.

### Secret scanning

- The OASIS AI wizard ships `scripts/scan_secrets.py`, which runs over
  the working tree + git history. Detects 18+ credential shapes:
  Anthropic `sk-ant-`, OpenAI `sk-`, Stripe `sk_live_`, brokerage API
  tokens, JWT, PGP / SSH / TLS private keys, and suspicious filenames.
- A hardened `.gitignore` blocks `*.env*`, `*_token.txt`,
  `credentials.json`, `service_account.json`, `*.pem`, `*.key`, SSH
  keys, and MCP config files that might contain API keys.
- If a secret is ever committed by accident, rotate the credential
  first and rewrite history second (`git filter-repo`) — never in the
  other order.

### Database access

- Tax and financial records live in a local SQLite database
  (`data/atlas.db`) — never on a third-party server. The customer
  controls the file.
- When Atlas does sync to cloud (pulse for C-Suite awareness), only
  aggregate metrics (MRR, cash position, budget health) are shared —
  never individual transactions, tax IDs, or account numbers.

### Safety hooks

- `.claude/settings.local.json` registers hooks that block destructive
  shell commands and block any edit that would touch a `.env*` file.
- Trading-related commands require explicit per-action approval
  regardless of source (see the Scope section below).

## Scope for this Agent (Atlas / CFO)

Atlas is the **finance and tax** agent of the C-Suite. By design it can:

- Read bank statements, tax records, and brokerage account balances
  from the customer's connected accounts
- Run tax-jurisdiction calculators (CA/US/UK/EU/AU) over historical
  transactions to project year-end position
- Maintain a local CFO knowledge base (FIRE target, budget, cash flow
  forecast) that only Atlas can write to
- Publish aggregate pulse metrics for other C-Suite agents (Bravo
  reads `data/pulse/cfo_pulse.json` for CEO dashboards)
- Read trading signals from broker APIs (when the user has connected one)

Atlas **cannot**, by policy:

- **Place live trades** without explicit per-trade human approval. Trade
  execution is gated by the `ATLAS_TRADING_ENABLED` env flag AND an
  interactive approval prompt AND a dollar-ceiling per trade. Three
  locks, not one.
- Send outbound emails or messages — that responsibility belongs to
  Bravo and goes through `send_gateway.py` with CASL compliance.
- Spend ad budget — that is Maven's role, with its own approval flow.
- Trigger physical devices — that is Aura's role, with its own approval
  flow.
- Share individual tax transactions across the cross-agent inbox. Only
  aggregate metrics leave this agent.

## Out of Scope

This policy covers Atlas's own code and the install path. It does **not**
cover:

- Third-party SaaS misconfigurations on the customer's side (brokerage
  account permissions the customer sets, Stripe keys the customer
  shares publicly, etc.)
- The user's own machine hygiene (disk encryption, OS patches, password
  managers)
- Vulnerabilities in upstream dependencies — those are tracked via
  GitHub Dependabot and patched in regular releases
- Tax-law correctness of Atlas's projections. Atlas provides tooling;
  the customer's accountant remains the authority.

## Coordinated Disclosure

Please give us a reasonable window to fix before public disclosure.
90 days is the default; we will ship a fix faster if we can and will
request an extension only for genuinely complex issues with clear
communication.

Thank you for helping keep our agents safe for the businesses that
depend on them.
