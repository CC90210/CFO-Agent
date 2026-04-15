"""
telegram_bridge.py
------------------
Atlas CFO Agent — Primary natural-language Telegram interface for CC.

CC talks to Atlas naturally on his phone. Slash commands for speed, plain
English for everything else. Atlas routes via Claude intent classifier then
executes the right CFO module.

Security
--------
Only responds to TELEGRAM_USER_ID from .env (CC's ID). Auto-registers the
first user who messages if TELEGRAM_USER_ID is not yet set.

Commands
--------
/start /help /networth /runway /status /taxes /receipts [YYYY-MM-DD]
/picks <query> /deepdive <TICKER> /news <topic> /macro /brain <file>

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
)
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

_BOT_VERSION = "3.0.0"
_MAX_MSG_LEN = 4000          # Telegram's hard limit is 4096; leave headroom
_HISTORY_DEPTH = 10          # Turns of conversation memory per chat
_MODEL = "claude-opus-4-6"
_ENV_FILE = _ROOT / ".env"

# System prompt fragment injected into every Claude call
_ATLAS_SYSTEM = """\
You are Atlas, CC's CFO agent. CC is 22, Canadian, solo-entrepreneur building \
OASIS AI Solutions (oasisai.work). Dual citizen (CA+UK, Irish eligible). Aggressive \
long-horizon investor. Moving to Montreal summer 2026. MRR ~$2,982 USD/mo. \
Files Canadian taxes via NETFILE annually. Tax residency: Ontario.

You speak plain-English first principles — never jargon-dump. You are calculated, \
direct, data-driven. Lead with the signal, then the reasoning. You never \
auto-execute trades; you research and advise. CC clicks the button.

When responding via Telegram, be punchy. Phones are for short reads. \
Use plain text — no markdown headers, minimal bullets. Be a senior CFO \
briefing a client on a 6-inch screen.\
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

You can also just TYPE what you want:
  "am I going to make it in Montreal?"
  "give me 3 AI plays"
  "should I hold crypto through summer?"
  "what's the Fed doing this week?"
"""

# ─────────────────────────────────────────────────────────────────────────────
#  Security helpers
# ─────────────────────────────────────────────────────────────────────────────


def _load_allowed_user_id() -> str | None:
    return os.environ.get("TELEGRAM_USER_ID", "").strip() or None


def _auto_register_user(user_id: str) -> None:
    """Write user_id to .env on first contact so subsequent users are blocked."""
    try:
        content = _ENV_FILE.read_text(encoding="utf-8") if _ENV_FILE.exists() else ""
        if "TELEGRAM_USER_ID=" in content:
            lines = [
                f"TELEGRAM_USER_ID={user_id}"
                if line.startswith("TELEGRAM_USER_ID=")
                else line
                for line in content.splitlines()
            ]
            _ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            with _ENV_FILE.open("a", encoding="utf-8") as fh:
                fh.write(f"\nTELEGRAM_USER_ID={user_id}\n")
        os.environ["TELEGRAM_USER_ID"] = user_id
        logger.info("Auto-registered owner user ID: %s", user_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to save TELEGRAM_USER_ID to .env: %s", exc)


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
        "2025 taxes: BEING PREPARED — self-employed deadline June 15, 2026.",
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
            labels = ["Business Expenses", "Income & Invoices", "Software & Subscriptions"]
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
        """Return True only for CC's user ID. Auto-registers on first contact."""
        uid = str(update.effective_user.id)
        if not self._allowed_user_id:
            _auto_register_user(uid)
            self._allowed_user_id = uid
            return True
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
        """Call Claude as Atlas CFO for open-ended chat."""
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

        messages = list(history) + [{"role": "user", "content": prompt}]

        resp = self._anthropic.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        return resp.content[0].text.strip()

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
