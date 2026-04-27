"""
telegram_bridge.py
------------------
Atlas CFO Agent — Primary natural-language Telegram interface for CC.

CC talks to Atlas naturally on his phone. Slash commands for speed, plain
English for everything else. Atlas routes via Claude intent classifier then
executes the right CFO module.

Security
--------
Only responds to TELEGRAM_USER_ID from .env (CC's ID). Fail-closed if
TELEGRAM_USER_ID is unset — the previous auto-register-on-first-contact
behaviour was a remote-takeover primitive (closed 2026-04-26).

Commands
--------
/start /help /networth /runway /status /taxes /receipts [YYYY-MM-DD]
/picks <query> /deepdive <TICKER> /news <topic> /macro /brain <file>
/pulses                 — 3-agent C-suite snapshot (Atlas+Bravo+Maven)
/sibling <agent> [file] — read a sibling agent's brain/*.md

Natural language
----------------
Any non-slash message is routed through Claude intent classifier, then
dispatched to the right CFO module. "chat" intent falls back to Atlas as
a Claude-powered CFO advisor.

Usage
-----
  python telegram_bridge.py
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import sys
import traceback
from collections import defaultdict, deque
from datetime import date
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
#  Path setup — must happen before project imports
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# UTF-8 forcing moved to _configure_utf8_stdout() — called only from main(),
# not at import. Doing it at import time broke any module importing this file,
# because the old stdout reference leaked and the wrapped buffer could close.


def _configure_utf8_stdout() -> None:
    """Force UTF-8 on Windows consoles. Call only when running as a bot, not on import."""
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────────────────
#  .env load (must be before settings import)
# ─────────────────────────────────────────────────────────────────────────────

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")

# ─────────────────────────────────────────────────────────────────────────────
#  Logging — basic config first, fine-tune after settings load
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    # Route INFO/DEBUG to stdout, WARNING+ to stderr.
    # Without this, pm2's `out_file` stays empty and every HTTP 200 spam
    # line ends up in the `error_file`, burying actual errors.
    stream=sys.stdout,
)
# Route WARNING+ to stderr so pm2's error_file only shows actual problems.
for h in logging.getLogger().handlers:
    h.addFilter(lambda rec: rec.levelno < logging.WARNING)
_err_handler = logging.StreamHandler(sys.stderr)
_err_handler.setLevel(logging.WARNING)
_err_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
logging.getLogger().addHandler(_err_handler)
logger = logging.getLogger("atlas.telegram_bridge")

# ─────────────────────────────────────────────────────────────────────────────
#  Optional python-telegram-bot import — graceful degradation if not installed
# ─────────────────────────────────────────────────────────────────────────────

try:
    from telegram import Update
    from telegram.constants import ChatAction
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        ContextTypes,
        MessageHandler,
        filters,
    )

    _PTB_AVAILABLE = True
except ImportError:
    _PTB_AVAILABLE = False
    logger.warning(
        "python-telegram-bot not installed. Run: pip install 'python-telegram-bot>=21.0'"
    )

# ─────────────────────────────────────────────────────────────────────────────
#  Optional Anthropic import
# ─────────────────────────────────────────────────────────────────────────────

try:
    import anthropic as _anthropic_lib

    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic not installed. Run: pip install anthropic")

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_BOT_VERSION = "3.1.0"  # IDE-parity tool use added 2026-04-16
_MAX_MSG_LEN = 4000          # Telegram's hard limit is 4096; leave headroom
_HISTORY_DEPTH = 10          # Turns of conversation memory per chat
_MODEL = "claude-opus-4-7"
_ENV_FILE = _ROOT / ".env"  # retained for ops scripts; not written to anymore

# System prompt fragment injected into every Claude call
_ATLAS_SYSTEM = """\
You are Atlas, CC's CFO. CC is 22, Canadian, solo-entrepreneur (OASIS AI \
Solutions), dual citizen CA+UK, Irish eligible, moving to Montreal summer 2026. \
MRR ~$2,982 USD/mo, 94% from Bennett. Tax residency Ontario.

## Voice (non-negotiable on Telegram)

You are NOT writing a report. You're texting CC on his phone. Match how a \
smart friend who happens to be a CFO would text him.

Hard rules:
- **Max 4 sentences per message** unless CC explicitly asks for detail \
  ("break it down", "explain in full", "give me the whole analysis").
- **No markdown headers.** No `##`, no `**bold**`, no `---` dividers.
- **No bullet lists** unless you're listing 3+ distinct items. Even then, \
  use plain dashes, max 5 items, one line each.
- **No tables.** Ever. Tables don't render well on phones.
- **Use contractions.** "you're" not "you are". "can't" not "cannot".
- **Lead with the answer in the first sentence.** Reasoning is optional and \
  comes after only if it changes what CC should do.
- **End with a next step or question when useful.** Not every message needs \
  a close, but if CC has to decide something, give him the decision to make.
- **Numbers get rounded** for speech. "$7.5K" not "$7,561.26". Use the exact \
  figure only if CC asks for precision or it's legally/tax-material.
- **No emojis.** No sign-offs like "Hope this helps". No "Great question".

Examples of the voice:

CC: "how much do i have"
Atlas: "$7.5K CAD liquid — $2.5K short of the Montreal floor. Most of it's \
in Wise USD."

CC: "should i buy enb"
Atlas: "Yeah, thesis still holds. Limit at $73 CAD, 2 shares in the TFSA. \
Dividends compound tax-free there. Want me to pull the current price?"

CC: "am i screwed on taxes"
Atlas: "No. 2025 return's already filed — we're good until April 2027. \
Current Q2 reserve target is $3K, you're tracking fine."

Counter-examples (do NOT do this):

❌ "## Summary\n\n**Liquid position:** $7,561.26 CAD\n\n**Montreal floor \
gap:** $2,438.74\n\n**Next steps:** 1. ..."

❌ "Great question! Let me break down your financial position..."

❌ "Based on your current net worth of $7,561.26 CAD, which consists of \
$6,223 in Wise USD, $700 in RBC..."

## Tools
You have read_file, grep, list_files, run_cfo, read_pick, read_memory, \
web_search. Use them silently before answering anything factual. Don't \
narrate the tool use — just give the answer.

## What you never do
Auto-execute trades. Claim tax advice is legal advice. Recommend something \
CC has already done (check memory/project_2025_tax_return_filed.md first). \
Write more than CC asked for.\
"""

_HELP_TEXT = """\
ATLAS — CC's CFO on your phone.

Say anything naturally, or use commands:

MONEY
/networth      live net-worth snapshot
/runway        Montreal cashflow scenarios
/status        quick financial pulse
/taxes         quarterly tax-reserve check
/receipts      sync Gmail receipts

RESEARCH
/picks <query> 3 stock picks with entry/exit/why
/deepdive TICK full bull/bear/base analysis
/news <topic>  top headlines (last 7d)
/macro         current geopolitical flashpoints

BRAIN
/brain <file>  read brain/ docs
/help          this message

3-AGENT C-SUITE
/pulses        snapshot of Atlas + Bravo + Maven pulses
/sibling <agent> [file]   read brain/ from a sibling
                          agent <agent>=bravo|maven|aura
                          e.g. /sibling bravo SOUL

You can also just TYPE what you want. Atlas has IDE-parity tools —
it can read brain/USER.md, grep docs, run CFO commands, and search
the web mid-conversation. Same powers as the terminal.

Examples:
  "am I going to make it in Montreal?"          (runs runway + reads USER.md)
  "give me 3 AI plays"                          (full research pipeline)
  "what did I buy last week?"                   (reads data/picks/)
  "what's my 2026 tax trigger?"                 (reads brain + memory)
  "what's the Fed doing this week?"             (web search)
"""

# ─────────────────────────────────────────────────────────────────────────────
#  Security helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_allowed_user_id() -> str | None:
    return os.environ.get("TELEGRAM_USER_ID", "").strip() or None


# NOTE: the legacy `_auto_register_user` helper was removed in the
# 2026-04-26 finalization pass after the security audit flagged it as a
# remote-takeover primitive: anyone who learned the bot username before
# CC sent /start could become permanent owner. The bot now fails closed
# when TELEGRAM_USER_ID is unset (see Atlas._is_allowed).


# ─────────────────────────────────────────────────────────────────────────────
#  CFO module helpers — thin wrappers around cfo/ and research/ modules
#  All run in a thread executor to avoid blocking the asyncio event loop.
# ─────────────────────────────────────────────────────────────────────────────


def _run_runway() -> str:
    """Capture cashflow.main() stdout and return as a string."""
    import io as _io

    from cfo import cashflow

    buf = _io.StringIO()
    old_stdout = sys.stdout
    try:
        sys.stdout = buf
        cashflow.main()
    finally:
        sys.stdout = old_stdout
    return buf.getvalue().strip() or "Runway model returned no output."


def _run_networth() -> str:
    """Return a compact net-worth text block."""
    from cfo.dashboard import networth_snapshot

    snap = networth_snapshot()
    lines = [f"Net Worth: ${snap['total_cad']:,.0f} CAD  (as of {snap['as_of'][:10]})"]
    lines.append("")
    for cat, amt in sorted(snap["by_category"].items(), key=lambda x: -x[1]):
        lines.append(f"  {cat.upper():<16} ${amt:>10,.0f}")
    if snap["flagged_issues"]:
        lines.append("")
        lines.append("Flags:")
        for issue in snap["flagged_issues"]:
            lines.append(f"  ! {issue}")
    return "\n".join(lines)


def _run_status() -> str:
    """Quick financial pulse: liquid cash, MRR, runway headline."""
    from cfo.accounts import all_balances

    balances = all_balances()
    cash_cats = {"cash"}
    liquid = sum(b.amount for b in balances if b.category in cash_cats and b.amount > 0)
    total = sum(b.amount for b in balances if b.amount > 0)

    # MRR from USER.md constant — update when income changes
    mrr_usd = 2982.0
    usd_cad = 1.37
    mrr_cad = mrr_usd * usd_cad

    lines = [
        f"Liquid cash:  ${liquid:,.0f} CAD",
        f"Total assets: ${total:,.0f} CAD",
        f"MRR:          ~${mrr_usd:,.0f} USD (~${mrr_cad:,.0f} CAD)",
        f"Date:         {date.today()}",
    ]
    return "\n".join(lines)


def _run_provider_health() -> str:
    """Quick status of every research data provider — for /health on Telegram."""
    from research.provider_health import run_all, GREEN, YELLOW, RED
    statuses = run_all()
    lines = ["Provider Health"]
    for s in statuses:
        marker = {GREEN: "OK", YELLOW: "WARN", RED: "FAIL"}.get(s.status, "?")
        lines.append(f"[{marker}] {s.name}: {s.detail[:80]}")
    n_red = sum(1 for s in statuses if s.status == RED)
    n_yel = sum(1 for s in statuses if s.status == YELLOW)
    n_grn = sum(1 for s in statuses if s.status == GREEN)
    lines.append("")
    lines.append(f"Summary: {n_grn} green, {n_yel} warn, {n_red} fail")
    return "\n".join(lines)


def _run_taxes() -> str:
    """Estimate current quarter's tax reserve requirement."""
    mrr_usd = 2982.0
    usd_cad = 1.37
    monthly_cad = mrr_usd * usd_cad
    reserve_rate = 0.25  # 25% self-employment reserve (CPP + federal + ON)

    monthly_reserve = monthly_cad * reserve_rate
    quarterly_reserve = monthly_reserve * 3

    lines = [
        "Tax Reserve Estimate (Q2 2026)",
        "",
        f"Monthly gross:     ${monthly_cad:,.0f} CAD",
        f"Reserve rate:      {reserve_rate:.0%} (CPP both sides + federal + ON)",
        f"Monthly set aside: ${monthly_reserve:,.0f} CAD",
        f"Q2 reserve target: ${quarterly_reserve:,.0f} CAD",
        "",
        "2025 taxes: FILED (Session 24, Wealthsimple Tax NETFILE). NOA pending.",
        "Payment due: April 30 even if filing date is later.",
        "QST registration required when Montreal presence is established.",
    ]
    return "\n".join(lines)


def _run_receipts(since_date: date | None = None) -> str:
    """Pull Gmail receipts and return a summary string."""
    from cfo.gmail_receipts import GmailReceipts

    if since_date is None:
        since_date = date(date.today().year, 1, 1)

    try:
        with GmailReceipts() as gr:
            # Auto-discover every sub-label under Receipts/<year>/ so new
            # categories CC adds in Gmail just work without code changes
            label_prefix = f"Receipts/{since_date.year}/"
            labels = [lbl for lbl in gr.list_labels() if lbl.startswith(label_prefix)]
            all_receipts = []
            for label in labels:
                try:
                    fetched = gr.fetch_label(label, since=since_date)
                    all_receipts.extend(fetched)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Could not fetch label %r: %s", label, exc)
    except EnvironmentError as exc:
        return f"Gmail credentials not configured: {exc}"

    if not all_receipts:
        return f"No receipts found since {since_date}."

    # Group by category
    by_cat: dict[str, list] = defaultdict(list)
    for r in all_receipts:
        by_cat[r.category].append(r)

    total_cad = sum(r.amount_cad for r in all_receipts if r.amount_cad is not None)
    lines = [
        f"Receipts since {since_date} ({len(all_receipts)} total)",
        f"Total: ${total_cad:,.2f} CAD",
        "",
    ]
    for cat, items in sorted(by_cat.items()):
        cat_total = sum(r.amount_cad for r in items if r.amount_cad is not None)
        lines.append(f"  {cat:<28} {len(items):>3} items  ${cat_total:>8,.2f}")
    return "\n".join(lines)


def _run_picks(query: str, n: int = 3) -> str:
    """Run stock picker and return execution-ready Telegram messages."""
    from research.stock_picker import StockPickerAgent

    agent = StockPickerAgent()
    picks = agent.pick(query, n=n)

    if not picks:
        return f"No picks with conviction >= 6 found for: {query}"

    # Each pick renders its own execution-ready block; join with a separator
    parts = [f"*Atlas Research — {len(picks)} pick(s) for: {query}*\n"]
    for pick in picks:
        parts.append(pick.as_telegram_message())
    return "\n\n---\n\n".join(parts)


def _run_deepdive(ticker: str) -> str:
    """Run deep dive and return formatted analysis."""
    from research.stock_picker import StockPickerAgent

    agent = StockPickerAgent()
    dd = agent.deep_dive(ticker.upper())

    lines = [
        f"Deep Dive: {dd.ticker} — {dd.company_name}",
        f"Conviction: {dd.conviction}/10  |  Current price: ${dd.current_price:.2f}",
        "",
        "SUMMARY",
        dd.executive_summary,
        "",
        f"BULL (${dd.bull_price_target:.2f}): {dd.bull_case[:300]}",
        "",
        f"BASE (${dd.base_price_target:.2f}): {dd.base_case[:300]}",
        "",
        f"BEAR (${dd.bear_price_target:.2f}): {dd.bear_case[:300]}",
        "",
        "VERDICT",
        dd.final_verdict,
    ]
    return "\n".join(lines)


def _run_news(query: str) -> str:
    """Fetch top headlines and return summary."""
    from research.news_ingest import fetch_google_news

    items = fetch_google_news(query, max_results=5)
    if not items:
        return f"No news found for: {query}"

    lines = [f"Top headlines: {query}\n"]
    for item in items:
        pub = item.published_at[:10] if item.published_at else "?"
        lines.append(f"  [{pub}] {item.title}\n  {item.source}\n")
    return "\n".join(lines)


def _run_macro() -> str:
    """Return geopolitical flashpoints summary."""
    from research.macro_watch import geopolitical_flashpoints

    fps = geopolitical_flashpoints()
    if not fps:
        return "No active macro flashpoints on record."

    lines = ["Macro Flashpoints:\n"]
    for fp in fps:
        if fp.status in ("active", "monitoring"):
            bullish = [s for s, d in fp.sector_impacts.items() if d == "bullish"]
            bearish = [s for s, d in fp.sector_impacts.items() if d == "bearish"]
            lines.append(
                f"{fp.name} ({fp.status.upper()})\n"
                f"  {fp.description[:150]}\n"
                f"  Bullish: {', '.join(bullish[:3]) or 'none'}\n"
                f"  Bearish: {', '.join(bearish[:3]) or 'none'}\n"
            )
    return "\n".join(lines) if len(lines) > 1 else "No active flashpoints."


def _run_brain(filename: str) -> str:
    """Read a brain/*.md file and return first 3000 chars."""
    brain_dir = _ROOT / "brain"
    # Normalize: strip path separators and .md extension handling
    name = filename.strip().replace("/", "").replace("\\", "")
    if not name.endswith(".md"):
        name = name + ".md"
    target = brain_dir / name
    if not target.exists():
        available = sorted(p.name for p in brain_dir.glob("*.md"))
        return f"File not found: {name}\n\nAvailable: {', '.join(available)}"
    text = target.read_text(encoding="utf-8")
    if len(text) > 3000:
        text = text[:3000] + f"\n\n... ({len(text) - 3000} more chars — be more specific)"
    return text


# ─────────────────────────────────────────────────────────────────────────────
#  Cross-agent helpers — read sibling agent state (Bravo, Maven, Aura)
# ─────────────────────────────────────────────────────────────────────────────


def _sibling_repos() -> dict[str, Path]:
    """
    Resolve sibling agent repo paths. Single source of truth lives in
    scripts/sibling_repos.py — this wrapper handles the case where the
    script isn't importable (older Atlas deploys) by falling back to
    hardcoded defaults that match the C-suite layout.
    """
    try:
        import sys
        scripts_dir = str(_ROOT / "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        from sibling_repos import SIBLING_REPOS  # type: ignore[import-not-found]
        return dict(SIBLING_REPOS)
    except Exception:
        return {
            "bravo": Path(os.environ.get("BRAVO_REPO", r"C:\Users\User\Business-Empire-Agent")),
            "maven": Path(os.environ.get("MAVEN_REPO", r"C:\Users\User\CMO-Agent")),
            "atlas": _ROOT,
            "aura":  Path(os.environ.get("AURA_REPO",  r"C:\Users\User\AURA")),
        }


def _short_age(iso_ts: str) -> str:
    """Return a short human age like '4h ago' or '3d ago' from an ISO ts."""
    if not iso_ts:
        return "n/a"
    try:
        from datetime import datetime as _dt
        when = _dt.fromisoformat(str(iso_ts).replace("Z", "+00:00"))
        delta = _dt.now(when.tzinfo) - when
        secs = int(delta.total_seconds())
        if secs < 3600:
            return f"{secs // 60}m ago"
        if secs < 86400:
            return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except Exception:
        return iso_ts[:16] if isinstance(iso_ts, str) else "n/a"


def _run_pulses() -> str:
    """
    Read Atlas's, Bravo's, and Maven's pulse files and return a short
    one-screen summary. Tells CC at a glance whether the 3-agent
    contract is healthy.
    """
    repos = _sibling_repos()
    paths = {
        "Atlas (CFO)": _ROOT / "data" / "pulse" / "cfo_pulse.json",
        "Bravo (CEO)": repos["bravo"] / "data" / "pulse" / "ceo_pulse.json",
        "Maven (CMO)": repos["maven"] / "data" / "pulse" / "cmo_pulse.json",
    }
    lines: list[str] = ["3-Agent Pulse Snapshot"]
    for label, path in paths.items():
        if not path.exists():
            lines.append(f"  {label}: MISSING ({path})")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            lines.append(f"  {label}: PARSE ERROR ({exc})")
            continue
        ts = data.get("updated_at", "")
        age = _short_age(ts)
        # Per-agent headline
        if label.startswith("Atlas"):
            sg = data.get("spend_gate") or {}
            status = sg.get("status") if isinstance(sg, dict) else sg
            cap = data.get("approved_ad_spend_monthly_cap_cad", 0)
            liquid = data.get("liquid_cad", 0)
            lines.append(
                f"  {label}: gate={status} | cap=${cap}/mo | "
                f"liquid=${liquid:,.0f} | {age}"
            )
        elif label.startswith("Bravo"):
            rev = data.get("revenue") or {}
            mrr = rev.get("net_mrr_usd") or data.get("mrr_usd", 0)
            conc = rev.get("bennett_concentration_pct") or "?"
            lines.append(f"  {label}: MRR=${mrr} USD | conc={conc}% | {age}")
        else:  # Maven
            req = data.get("spend_request_cad", 0)
            lines.append(f"  {label}: spend_request=${req} CAD | {age}")
    return "\n".join(lines)


def _run_sibling(target: str) -> str:
    """
    Read a sibling agent's brain doc.

    Usage:
      sibling bravo            -> list Bravo's brain/*.md
      sibling bravo SOUL       -> read Bravo's brain/SOUL.md (first 3000 chars)
      sibling maven CMO_PULSE  -> read Maven's brain/CMO_PULSE.md
    """
    parts = target.strip().split(maxsplit=1)
    if not parts:
        return "Usage: sibling <bravo|maven|aura> [filename]"
    agent = parts[0].lower()
    filename = parts[1].strip() if len(parts) > 1 else None
    repos = _sibling_repos()
    if agent not in repos:
        return f"Unknown agent {agent!r}. Try one of: {sorted(repos)}"
    repo = repos[agent]
    if not repo.exists():
        return f"{agent.title()} repo not on this machine: {repo}"
    brain = repo / "brain"
    if not brain.exists():
        return f"{agent.title()} has no brain/ dir at {brain}"
    if filename is None:
        names = sorted(p.name for p in brain.glob("*.md"))
        return f"{agent.title()} brain/ contents:\n  " + "\n  ".join(names)
    name = filename.replace("/", "").replace("\\", "")
    if not name.endswith(".md"):
        name += ".md"
    target_file = brain / name
    if not target_file.exists():
        names = sorted(p.name for p in brain.glob("*.md"))
        return (
            f"{agent.title()}/brain/{name} not found.\n"
            f"Available: {', '.join(names)}"
        )
    text = target_file.read_text(encoding="utf-8")
    if len(text) > 3000:
        text = text[:3000] + f"\n\n... ({len(text) - 3000} more chars)"
    return f"=== {agent.title()}/brain/{name} ===\n{text}"


# ─────────────────────────────────────────────────────────────────────────────
#  Intent classifier
# ─────────────────────────────────────────────────────────────────────────────

_INTENT_SYSTEM = """\
You are an intent classifier for Atlas, a CFO Telegram bot.

Classify the user's message into exactly one of these intents (output JSON only):
  runway    — cashflow, runway, Montreal move, can I afford, burn rate
  networth  — net worth, total assets, what do I have
  status    — quick pulse, how am I doing, financial snapshot
  picks     — stock picks, equities, buy recommendation, plays (extract "query" and "n")
  deepdive  — deep dive, full analysis, bull/bear on a specific ticker (extract "ticker")
  receipts  — receipts, expenses, Gmail sync, tax prep receipts (extract "since" as YYYY-MM-DD or null)
  news      — headlines, news, latest on (extract "query")
  macro     — macro, geopolitics, flashpoints, Fed, global economy
  taxes     — tax reserve, how much tax, CRA, filing, deductions
  pulses    — 3-agent C-suite state, Bravo / Maven / cross-agent health
  sibling   — read another agent's brain (extract "query" as "<agent> [file]")
  chat      — anything else (general CFO question or conversation)

Output format (strict JSON, no other text):
{"intent": "<one of the above>", "query": "<extracted query or null>", "n": <int or null>, "ticker": "<TICKER or null>", "since": "<YYYY-MM-DD or null>"}
"""


class AtlasIntentClassifier:
    """Wraps Claude to route natural language messages to CFO functions."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def classify(self, message: str) -> dict[str, Any]:
        """Return intent dict. Falls back to chat on any error."""
        import json

        default: dict[str, Any] = {
            "intent": "chat",
            "query": message,
            "n": None,
            "ticker": None,
            "since": None,
        }
        if not _ANTHROPIC_AVAILABLE:
            return default
        try:
            resp = self._client.messages.create(
                model=_MODEL,
                max_tokens=128,
                system=_INTENT_SYSTEM,
                messages=[{"role": "user", "content": message}],
            )
            raw = resp.content[0].text.strip()
            # Strip markdown code fences if Claude wrapped output
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
            parsed: dict[str, Any] = json.loads(raw)
            return {**default, **parsed}
        except Exception as exc:  # noqa: BLE001
            logger.warning("Intent classification failed: %s", exc)
            return default


# ─────────────────────────────────────────────────────────────────────────────
#  Main bot class
# ─────────────────────────────────────────────────────────────────────────────


class AtlasTelegram:
    """
    Atlas CFO Telegram bot.

    Parameters
    ----------
    token: Telegram bot token from .env
    user_id: CC's Telegram user ID (TELEGRAM_USER_ID) — all others are rejected
    anthropic_key: Anthropic API key for NL routing + chat fallback
    """

    def __init__(self, token: str, user_id: str | None, anthropic_key: str) -> None:
        self._token = token
        self._allowed_user_id = user_id
        self._anthropic_key = anthropic_key
        self._greeted: set[int] = set()

        # In-memory conversation history: {chat_id: deque of message dicts}
        self._history: dict[int, deque] = defaultdict(
            lambda: deque(maxlen=_HISTORY_DEPTH * 2)  # *2 for user+assistant pairs
        )

        if _ANTHROPIC_AVAILABLE:
            self._anthropic = _anthropic_lib.Anthropic(api_key=anthropic_key)
            self._classifier = AtlasIntentClassifier(self._anthropic)
        else:
            self._anthropic = None  # type: ignore[assignment]
            self._classifier = None  # type: ignore[assignment]

    # ── Security firewall ──────────────────────────────────────────────────────

    def _is_allowed(self, update: Any) -> bool:
        """
        Return True only for CC's user ID.

        Security model: TELEGRAM_USER_ID MUST be set explicitly in .env
        before the bot is started. The previous auto-register-on-first-
        contact behaviour was a remote takeover primitive — anyone who
        learned the bot username before CC sent /start became permanent
        owner. Fail closed instead.

        To set up a new bot:
          1. Send /start to the bot once
          2. Read the chat update's user.id from the Telegram getUpdates
             API or the bot logs (`Rejected (no TELEGRAM_USER_ID set)`)
          3. Add `TELEGRAM_USER_ID=<that-id>` to .env manually
          4. Restart the bot
        """
        uid = str(update.effective_user.id)
        if not self._allowed_user_id:
            logger.warning(
                "Rejected message from user_id=%s — TELEGRAM_USER_ID not set "
                "in .env. To authorize this user, add TELEGRAM_USER_ID=%s and "
                "restart the bot.", uid, uid,
            )
            return False
        return uid == self._allowed_user_id

    async def _reject(self, update: Any) -> None:
        await update.message.reply_text("Unauthorized.")

    # ── Message sending helpers ────────────────────────────────────────────────

    async def _send_chunked(self, chat_id: int, text: str, context: Any) -> None:
        """Split text at _MAX_MSG_LEN boundaries and send sequentially."""
        if not text:
            text = "(empty response)"
        chunks = [text[i: i + _MAX_MSG_LEN] for i in range(0, len(text), _MAX_MSG_LEN)]
        for chunk in chunks:
            await context.bot.send_message(chat_id=chat_id, text=chunk)

    async def _typing_then_send(self, update: Any, context: Any, text: str) -> None:
        """Send typing indicator, then deliver chunked response."""
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        await self._send_chunked(update.effective_chat.id, text, context)

    # ── Claude chat fallback ───────────────────────────────────────────────────

    def _as_atlas(self, prompt: str, history: deque) -> str:
        """
        Call Claude as Atlas CFO for open-ended chat, with IDE-parity tool use.

        Atlas can read project files (USER.md, brain/*, docs/*, data/picks/*),
        grep the codebase, invoke CFO commands (runway, networth, picks...),
        and run Anthropic web search — mid-conversation, from Telegram. Same
        powers as the Claude Code terminal, constrained to read-only ops.

        Falls back to a plain completion if atlas_tools isn't importable.
        """
        if not _ANTHROPIC_AVAILABLE or self._anthropic is None:
            return "Anthropic client not available. Check ANTHROPIC_API_KEY in .env."

        # Read USER.md excerpt for grounding
        user_md_path = _ROOT / "brain" / "USER.md"
        user_excerpt = ""
        if user_md_path.exists():
            raw = user_md_path.read_text(encoding="utf-8")
            user_excerpt = raw[:2000]  # First 2K chars covers identity + assets

        system = _ATLAS_SYSTEM
        if user_excerpt:
            system += f"\n\n## CC Profile (from USER.md)\n{user_excerpt}"
        system += (
            "\n\nYou have tools: read_file, grep, list_files, run_cfo, "
            "read_pick, read_memory, web_search. Use them before answering "
            "anything factual about CC's state — never guess. Check "
            "memory/project_2025_tax_return_filed.md before any rundown of "
            "open items; the 2025 return is already filed."
        )

        messages = list(history) + [{"role": "user", "content": prompt}]

        # IDE-parity path: run the Anthropic tool-use loop.
        try:
            from atlas_tools import run_with_tools

            return run_with_tools(
                client=self._anthropic,
                model=_MODEL,
                system=system,
                messages=messages,
                # Budget cap reinforces the "short text message" voice rules.
                # ~500 tokens ≈ 375 words, plenty for a CFO briefing reply.
                # Claude can still write longer when CC explicitly asks for detail.
                max_tokens=500,
            ).strip()
        except ImportError as exc:
            logger.warning("atlas_tools unavailable (%s) — falling back to plain chat", exc)
            resp = self._anthropic.messages.create(
                model=_MODEL,
                max_tokens=500,
                system=system,
                messages=messages,
            )
            return resp.content[0].text.strip()
        except Exception as exc:  # noqa: BLE001
            logger.exception("tool-use loop failed")
            return f"Atlas tool-use error: {exc!s:.200}. Falling back — try again."

    # ── Slash command handlers ─────────────────────────────────────────────────

    async def cmd_start(self, update: Any, _context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        chat_id = update.effective_chat.id
        self._greeted.add(chat_id)
        await update.message.reply_text(
            f"Atlas v{_BOT_VERSION} online. Type /help for commands or just talk."
        )

    async def cmd_help(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        await self._send_chunked(update.effective_chat.id, _HELP_TEXT, context)

    async def cmd_networth(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_networth)
        except Exception as exc:  # noqa: BLE001
            logger.exception("networth handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_runway(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_runway)
        except Exception as exc:  # noqa: BLE001
            logger.exception("runway handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_status(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_status)
        except Exception as exc:  # noqa: BLE001
            logger.exception("status handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await update.message.reply_text(result)

    async def cmd_taxes(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_taxes)
        except Exception as exc:  # noqa: BLE001
            logger.exception("taxes handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_health(self, update: Any, context: Any) -> None:
        """Probe every research data provider. Mirrors `python main.py provider-health`."""
        if not self._is_allowed(update):
            await self._reject(update)
            return
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_provider_health)
        except Exception as exc:  # noqa: BLE001
            logger.exception("health handler error")
            result = f"Atlas hit an issue probing providers: {exc!s:.200}."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_receipts(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        # Parse optional date arg: /receipts 2026-01-01
        since: date | None = None
        args = context.args or []
        if args:
            try:
                since = date.fromisoformat(args[0])
            except ValueError:
                await update.message.reply_text(
                    f"Bad date format: {args[0]}. Use YYYY-MM-DD."
                )
                return
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, _run_receipts, since
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("receipts handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_picks(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        args = context.args or []
        query = " ".join(args).strip() or "best opportunities right now"
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, _run_picks, query, 3
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("picks handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_deepdive(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        args = context.args or []
        if not args:
            await update.message.reply_text("Usage: /deepdive TICKER — e.g. /deepdive NVDA")
            return
        ticker = args[0].upper()
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, _run_deepdive, ticker
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("deepdive handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_news(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        args = context.args or []
        query = " ".join(args).strip() or "financial markets"
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, _run_news, query
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("news handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_macro(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_macro)
        except Exception as exc:  # noqa: BLE001
            logger.exception("macro handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_brain(self, update: Any, context: Any) -> None:
        if not self._is_allowed(update):
            await self._reject(update)
            return
        args = context.args or []
        if not args:
            available = sorted(p.name for p in (_ROOT / "brain").glob("*.md"))
            await update.message.reply_text(
                f"Usage: /brain <filename>\n\nAvailable: {', '.join(available)}"
            )
            return
        filename = args[0]
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, _run_brain, filename
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("brain handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_pulses(self, update: Any, context: Any) -> None:
        """Snapshot of all 3 agent pulses (Atlas + Bravo + Maven)."""
        if not self._is_allowed(update):
            await self._reject(update)
            return
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _run_pulses)
        except Exception as exc:  # noqa: BLE001
            logger.exception("pulses handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    async def cmd_sibling(self, update: Any, context: Any) -> None:
        """Read a sibling agent's brain doc. Usage: /sibling bravo SOUL"""
        if not self._is_allowed(update):
            await self._reject(update)
            return
        args = context.args or []
        if not args:
            await update.message.reply_text(
                "Usage: /sibling <bravo|maven|aura> [filename]\n"
                "Examples:\n"
                "  /sibling bravo            (list Bravo's brain/)\n"
                "  /sibling bravo SOUL       (read Bravo's brain/SOUL.md)\n"
                "  /sibling maven CFO_GATE_CONTRACT"
            )
            return
        target = " ".join(args)
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, _run_sibling, target
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("sibling handler error")
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."
        await self._send_chunked(update.effective_chat.id, result, context)

    # ── Natural language handler ───────────────────────────────────────────────

    async def on_message(self, update: Any, context: Any) -> None:
        """Route all non-command messages through intent classifier."""
        if not self._is_allowed(update):
            await self._reject(update)
            return

        text = (update.message.text or "").strip()
        if not text:
            return

        chat_id = update.effective_chat.id
        history = self._history[chat_id]

        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        try:
            # Classify intent
            if self._classifier is not None:
                intent_data = await asyncio.get_event_loop().run_in_executor(
                    None, self._classifier.classify, text
                )
            else:
                intent_data = {"intent": "chat", "query": text, "n": None, "ticker": None, "since": None}

            intent = intent_data.get("intent", "chat")
            query = intent_data.get("query") or text
            n = intent_data.get("n") or 3
            ticker = intent_data.get("ticker") or ""
            since_raw = intent_data.get("since")
            since: date | None = None
            if since_raw:
                try:
                    since = date.fromisoformat(since_raw)
                except ValueError:
                    pass

            # Dispatch to the right function
            if intent == "runway":
                result = await asyncio.get_event_loop().run_in_executor(None, _run_runway)
            elif intent == "networth":
                result = await asyncio.get_event_loop().run_in_executor(None, _run_networth)
            elif intent == "status":
                result = await asyncio.get_event_loop().run_in_executor(None, _run_status)
            elif intent == "taxes":
                result = await asyncio.get_event_loop().run_in_executor(None, _run_taxes)
            elif intent == "receipts":
                result = await asyncio.get_event_loop().run_in_executor(
                    None, _run_receipts, since
                )
            elif intent == "picks":
                result = await asyncio.get_event_loop().run_in_executor(
                    None, _run_picks, query, int(n)
                )
            elif intent == "deepdive":
                if not ticker:
                    # Try to extract ticker from the text directly
                    import re
                    found = re.findall(r"\b[A-Z]{2,5}\b", text)
                    ticker = found[0] if found else "NVDA"
                result = await asyncio.get_event_loop().run_in_executor(
                    None, _run_deepdive, ticker
                )
            elif intent == "news":
                result = await asyncio.get_event_loop().run_in_executor(
                    None, _run_news, query
                )
            elif intent == "macro":
                result = await asyncio.get_event_loop().run_in_executor(None, _run_macro)
            elif intent == "pulses":
                result = await asyncio.get_event_loop().run_in_executor(None, _run_pulses)
            elif intent == "sibling":
                result = await asyncio.get_event_loop().run_in_executor(
                    None, _run_sibling, query or ""
                )
            else:
                # chat — Atlas as Claude CFO
                result = await asyncio.get_event_loop().run_in_executor(
                    None, self._as_atlas, text, history
                )

            # Update conversation history
            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": result[:500]})  # truncate for memory

        except Exception as exc:  # noqa: BLE001
            logger.error("on_message error: %s\n%s", exc, traceback.format_exc())
            result = f"Atlas hit an issue: {exc!s:.200}. Full details logged."

        await self._send_chunked(chat_id, result, context)

    # ── Application builder ────────────────────────────────────────────────────

    def build_app(self) -> Any:
        """Construct the Application and register all handlers. Returns the app."""
        if not _PTB_AVAILABLE:
            raise ImportError(
                "python-telegram-bot is not installed. "
                "Run: pip install 'python-telegram-bot>=21.0'"
            )

        app = ApplicationBuilder().token(self._token).build()

        # Slash commands
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("help", self.cmd_help))
        app.add_handler(CommandHandler("networth", self.cmd_networth))
        app.add_handler(CommandHandler("runway", self.cmd_runway))
        app.add_handler(CommandHandler("status", self.cmd_status))
        app.add_handler(CommandHandler("taxes", self.cmd_taxes))
        app.add_handler(CommandHandler("receipts", self.cmd_receipts))
        app.add_handler(CommandHandler("picks", self.cmd_picks))
        app.add_handler(CommandHandler("deepdive", self.cmd_deepdive))
        app.add_handler(CommandHandler("news", self.cmd_news))
        app.add_handler(CommandHandler("macro", self.cmd_macro))
        app.add_handler(CommandHandler("brain", self.cmd_brain))
        app.add_handler(CommandHandler("health", self.cmd_health))
        app.add_handler(CommandHandler("pulses", self.cmd_pulses))
        app.add_handler(CommandHandler("sibling", self.cmd_sibling))

        # Natural language — catches everything that isn't a command
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message))

        return app


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    _configure_utf8_stdout()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    user_id = os.environ.get("TELEGRAM_USER_ID", "").strip() or None

    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN not set in .env. Cannot start."
        )
        sys.exit(1)
    if not anthropic_key:
        logger.warning(
            "ANTHROPIC_API_KEY not set — natural language routing will fall back to echo."
        )

    bot = AtlasTelegram(token=token, user_id=user_id, anthropic_key=anthropic_key)
    app = bot.build_app()

    logger.info("Atlas Telegram Bridge v%s starting — polling...", _BOT_VERSION)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
