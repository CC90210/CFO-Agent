"""
telegram_bridge.py
------------------
Atlas CFO Agent — Telegram Bot for Trading & Accounting.

CC can send commands from his phone, receive trade alerts, and track receipts/expenses.

Security
--------
Only responds to CC's Telegram user ID (TELEGRAM_USER_ID in .env).
If TELEGRAM_USER_ID is not set, auto-registers the first user who
messages the bot and writes the ID back to .env.

Commands — Trading
------------------
  /status      — current portfolio, P&L, open positions
  /analyze     — run multi-agent analysis on a symbol (e.g. /analyze BTC/USDT)
  /positions   — list open positions with P&L
  /trades      — today's trades
  /pnl         — daily/weekly/monthly P&L summary
  /risk        — current risk metrics
  /watchlist   — current watchlist with quick metrics
  /scan        — trigger an immediate market scan
  /pause       — pause autonomous trading (keep monitoring)
  /resume      — resume autonomous trading
  /kill        — emergency: close all positions and halt

Commands — Accounting
---------------------
  [send photo] — save a receipt (caption: "vendor amount" e.g. "Staples 45.99")
  /receipts    — view recent receipts
  /expenses    — monthly expense summary (e.g. /expenses 2026-03)
  /deductions  — YTD business deductions for T2125
  /addexpense  — manual expense (e.g. /addexpense Business 29.99 Adobe subscription)
  /help        — list all commands

Proactive alerts (sent automatically)
--------------------------------------
  - Trade opened/closed
  - Daily summary at 00:00 UTC
  - Kill switch triggered
  - Stop loss / take profit hit

Usage
-----
  Standalone: python telegram_bridge.py
  Preferred:  use run_atlas.py which starts this alongside autonomous.py
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
#  Path setup
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_ENV_FILE = _ROOT / ".env"

logger = logging.getLogger("atlas.telegram_bridge")

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports
# ─────────────────────────────────────────────────────────────────────────────

from config.settings import settings  # noqa: E402
from db.database import get_session, init_db  # noqa: E402
from db.models import DailyPnL, Expense, PortfolioSnapshot, Receipt, Signal, Trade  # noqa: E402

# Ensure all tables exist before any handler queries the DB.
# Safe to call multiple times — uses CREATE TABLE IF NOT EXISTS semantics.
init_db()

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_BOT_VERSION = "2.0.0"
_TELEGRAM_API_BASE = "https://api.telegram.org/bot"
_MAX_MESSAGE_LENGTH = 4096  # Telegram hard limit
_RECEIPTS_DIR = _ROOT / "data" / "receipts"

# Shared state flags — modified by /pause and /resume
_trading_paused: bool = False


# ─────────────────────────────────────────────────────────────────────────────
#  Security — user ID management
# ─────────────────────────────────────────────────────────────────────────────


def _load_allowed_user_id() -> str | None:
    """
    Read TELEGRAM_USER_ID from the environment (already loaded from .env
    by python-dotenv or pydantic-settings at startup).
    """
    return os.environ.get("TELEGRAM_USER_ID", "").strip() or None


def _auto_register_user(user_id: str) -> None:
    """
    Write the first user's ID into .env as TELEGRAM_USER_ID.
    Subsequent users will be blocked by the firewall.
    """
    try:
        content = ""
        if _ENV_FILE.exists():
            content = _ENV_FILE.read_text(encoding="utf-8")

        if "TELEGRAM_USER_ID=" in content:
            lines = content.splitlines()
            new_lines = [
                f"TELEGRAM_USER_ID={user_id}" if line.startswith("TELEGRAM_USER_ID=") else line
                for line in lines
            ]
            _ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        else:
            with _ENV_FILE.open("a", encoding="utf-8") as fh:
                fh.write(f"\nTELEGRAM_USER_ID={user_id}\n")

        # Update the live environment so we don't need a restart
        os.environ["TELEGRAM_USER_ID"] = user_id
        logger.info("Auto-registered owner user ID: %s", user_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to save TELEGRAM_USER_ID to .env: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
#  Database query helpers
# ─────────────────────────────────────────────────────────────────────────────


def _query_portfolio_state() -> dict[str, Any]:
    """Return a dict with current portfolio metrics from the database."""
    today = datetime.date.today()

    with get_session() as session:
        snapshot = (
            session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.timestamp.desc())
            .first()
        )
        daily = session.query(DailyPnL).filter(DailyPnL.date == today).first()
        today_start = datetime.datetime.combine(today, datetime.time.min)
        closed_trades = (
            session.query(Trade)
            .filter(Trade.closed_at >= today_start, Trade.pnl.isnot(None))
            .all()
        )
        open_positions: list[dict[str, Any]] = []
        if snapshot and snapshot.positions_json:
            open_positions = list(snapshot.positions_json)

        portfolio_value = snapshot.total_value if snapshot else 0.0
        drawdown = snapshot.drawdown_pct if snapshot else 0.0
        daily_pnl = daily.realized_pnl if daily else 0.0
        wins = sum(1 for t in closed_trades if (t.pnl or 0.0) > 0)
        losses = sum(1 for t in closed_trades if (t.pnl or 0.0) <= 0)

    return {
        "portfolio_value": portfolio_value,
        "drawdown_pct": drawdown,
        "daily_pnl": daily_pnl,
        "positions": open_positions,
        "trades_today": len(closed_trades),
        "wins_today": wins,
        "losses_today": losses,
    }


def _query_pnl_summary() -> dict[str, float]:
    """Return daily, weekly, and monthly P&L totals."""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    with get_session() as session:
        rows = session.query(DailyPnL).filter(DailyPnL.date >= month_start).all()
        # Extract values inside session to avoid DetachedInstanceError
        pnl_entries = [(r.date, r.realized_pnl) for r in rows]

    daily_pnl = next((pnl for d, pnl in pnl_entries if d == today), 0.0)
    weekly_pnl = sum(pnl for d, pnl in pnl_entries if d >= week_start)
    monthly_pnl = sum(pnl for _, pnl in pnl_entries)

    return {
        "daily": daily_pnl,
        "weekly": weekly_pnl,
        "monthly": monthly_pnl,
    }


def _query_risk_metrics() -> dict[str, Any]:
    """Return current risk metrics."""
    today = datetime.date.today()

    with get_session() as session:
        snapshot = (
            session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.timestamp.desc())
            .first()
        )
        daily = session.query(DailyPnL).filter(DailyPnL.date == today).first()

        portfolio_value = snapshot.total_value if snapshot else 0.0
        drawdown = snapshot.drawdown_pct if snapshot else 0.0
        daily_pnl = daily.realized_pnl if daily else 0.0
        daily_loss_pct = (daily_pnl / portfolio_value * 100.0) if portfolio_value else 0.0
        positions = list(snapshot.positions_json) if snapshot and snapshot.positions_json else []

    return {
        "portfolio_value": portfolio_value,
        "drawdown_pct": drawdown,
        "daily_loss_pct": daily_loss_pct,
        "open_positions": len(positions),
        "max_drawdown_limit": settings.risk.max_drawdown_pct,
        "daily_loss_limit": settings.risk.daily_loss_limit_pct,
        "max_open_positions": settings.risk.max_open_positions,
    }


def _query_today_trades() -> list[dict[str, Any]]:
    """Return today's closed trades as a list of dicts."""
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time.min)

    with get_session() as session:
        trades = (
            session.query(Trade)
            .filter(Trade.closed_at >= today_start)
            .order_by(Trade.closed_at.desc())
            .limit(20)
            .all()
        )
        return [
            {
                "symbol": t.symbol,
                "side": t.side,
                "pnl": t.pnl or 0.0,
                "pnl_pct": t.pnl_pct or 0.0,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price or 0.0,
                "strategy": t.strategy,
                "closed_at": t.closed_at.strftime("%H:%M") if t.closed_at else "?",
            }
            for t in trades
        ]


# ─────────────────────────────────────────────────────────────────────────────
#  Message formatters
# ─────────────────────────────────────────────────────────────────────────────


def _format_status() -> str:
    """Build the /status response text."""
    state = _query_portfolio_state()
    pv = state["portfolio_value"]
    dd = state["drawdown_pct"]
    dpnl = state["daily_pnl"]
    positions = state["positions"]
    trades = state["trades_today"]
    wins = state["wins_today"]
    losses = state["losses_today"]
    mode = "LIVE" if settings.is_live else "PAPER"
    paused_str = " [PAUSED]" if _trading_paused else ""

    sign = "+" if dpnl >= 0 else ""
    lines = [
        f"Atlas {mode}{paused_str}",
        f"Portfolio: ${pv:,.2f}",
        f"Daily P&L: {sign}${dpnl:,.2f}",
        f"Drawdown: {abs(dd):.2f}% / {settings.risk.max_drawdown_pct:.1f}%",
        f"Open Positions: {len(positions)} / {settings.risk.max_open_positions}",
        f"Trades Today: {trades} ({wins}W / {losses}L)",
    ]
    if positions:
        lines.append("")
        lines.append("Open:")
        for pos in positions[:5]:  # cap at 5 to stay readable
            sym = pos.get("symbol", "?")
            side = pos.get("side", "?").upper()
            upnl = pos.get("unrealized_pnl", 0.0)
            upnl_sign = "+" if upnl >= 0 else ""
            lines.append(f"  {sym} {side} uPnL: {upnl_sign}${upnl:,.2f}")
    return "\n".join(lines)


def _format_positions() -> str:
    """Build the /positions response text."""
    state = _query_portfolio_state()
    positions = state["positions"]
    if not positions:
        return "No open positions."

    lines = [f"Open Positions ({len(positions)}):"]
    for pos in positions:
        sym = pos.get("symbol", "?")
        side = pos.get("side", "?").upper()
        size = pos.get("size", 0.0)
        entry = pos.get("entry_price", 0.0)
        upnl = pos.get("unrealized_pnl", 0.0)
        upnl_pct = pos.get("unrealized_pnl_pct", 0.0)
        sign = "+" if upnl >= 0 else ""
        lines.append(
            f"{sym} {side} {size:.4f} @ ${entry:,.2f}\n"
            f"  uPnL: {sign}${upnl:,.2f} ({sign}{upnl_pct:.1f}%)"
        )
    return "\n".join(lines)


def _format_trades() -> str:
    """Build the /trades response text."""
    trades = _query_today_trades()
    if not trades:
        return "No trades today."

    lines = [f"Today's Trades ({len(trades)}):"]
    for t in trades:
        sign = "+" if t["pnl"] >= 0 else ""
        lines.append(
            f"{t['symbol']} {t['side'].upper()} @ {t['closed_at']}\n"
            f"  PnL: {sign}${t['pnl']:,.2f} ({sign}{t['pnl_pct']:.1f}%) | {t['strategy']}"
        )
    return "\n".join(lines)


def _format_pnl() -> str:
    """Build the /pnl response text."""
    pnl = _query_pnl_summary()
    state = _query_portfolio_state()
    pv = state["portfolio_value"]

    def _fmt(v: float) -> str:
        sign = "+" if v >= 0 else ""
        return f"{sign}${v:,.2f}"

    lines = [
        "P&L Summary:",
        f"Daily:   {_fmt(pnl['daily'])}",
        f"Weekly:  {_fmt(pnl['weekly'])}",
        f"Monthly: {_fmt(pnl['monthly'])}",
        f"Equity:  ${pv:,.2f}",
    ]
    return "\n".join(lines)


def _format_risk() -> str:
    """Build the /risk response text."""
    r = _query_risk_metrics()
    dd_remaining = r["max_drawdown_limit"] - abs(r["drawdown_pct"])
    dl_remaining = r["daily_loss_limit"] - abs(r["daily_loss_pct"])

    lines = [
        "Risk Metrics:",
        f"Drawdown: {abs(r['drawdown_pct']):.2f}% (limit: {r['max_drawdown_limit']:.1f}%, headroom: {dd_remaining:.1f}%)",
        f"Daily Loss: {abs(r['daily_loss_pct']):.2f}% (limit: {r['daily_loss_limit']:.1f}%, headroom: {dl_remaining:.1f}%)",
        f"Open Positions: {r['open_positions']} / {r['max_open_positions']}",
        f"Portfolio: ${r['portfolio_value']:,.2f}",
    ]
    return "\n".join(lines)


def _format_help() -> str:
    """Build the /help response text."""
    return (
        "Atlas CFO Agent Commands:\n"
        "\n"
        "TRADING\n"
        "/status     — portfolio, P&L, positions\n"
        "/analyze <SYMBOL>  — e.g. /analyze BTC/USDT\n"
        "/positions  — open positions with P&L\n"
        "/trades     — today's trades\n"
        "/pnl        — daily/weekly/monthly P&L\n"
        "/risk       — drawdown, daily loss, exposure\n"
        "/watchlist  — watchlist with metrics\n"
        "/scan       — trigger immediate market scan\n"
        "/pause      — pause trading (keep monitoring)\n"
        "/resume     — resume trading\n"
        "/kill       — EMERGENCY: close all & halt\n"
        "\n"
        "ACCOUNTING\n"
        "[Send photo] — save a receipt (add caption: 'vendor amount')\n"
        "/receipts   — view recent receipts\n"
        "/expenses [month] — expense summary (e.g. /expenses 2026-03)\n"
        "/deductions [year] — YTD business deductions for T2125\n"
        "/addexpense category amount description — manual expense\n"
        "\n"
        "/help       — this message"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  TelegramBridge
# ─────────────────────────────────────────────────────────────────────────────


class TelegramBridge:
    """
    Telegram bot for remote control of the Atlas trading daemon.

    Designed to run as an asyncio task alongside autonomous.py inside
    a single event loop (via run_atlas.py). Can also run standalone.

    Parameters
    ----------
    shutdown_event:
        Shared asyncio.Event. When set, the bridge stops polling.
    """

    def __init__(self, shutdown_event: asyncio.Event) -> None:
        self._token = settings.telegram.telegram_bot_token
        self._shutdown_event = shutdown_event
        self._allowed_user_id: str | None = _load_allowed_user_id()
        self._offset: int = 0  # Telegram long-poll update offset

        if not self._token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is not set in .env. "
                "Cannot start Telegram bridge without a bot token."
            )

    # ── Main polling loop ──────────────────────────────────────────────────

    async def run(self) -> None:
        """Start long-polling and dispatch commands until shutdown."""
        import aiohttp  # imported here to keep startup clean if not used standalone

        logger.info("Telegram bridge starting (long-poll)...")
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=35)
        ) as session:
            self._http = session
            await self._send_message(
                f"Atlas Telegram Bridge v{_BOT_VERSION} online.\nSend /help for commands."
            )

            while not self._shutdown_event.is_set():
                try:
                    updates = await self._get_updates()
                    for update in updates:
                        await self._dispatch(update)
                except asyncio.CancelledError:
                    break
                except Exception as exc:  # noqa: BLE001
                    logger.error("Polling error: %s", exc)
                    # Back off before retrying to avoid hammering Telegram on errors
                    await asyncio.sleep(5)

        logger.info("Telegram bridge stopped.")

    # ── Telegram API wrappers ──────────────────────────────────────────────

    async def _get_updates(self) -> list[dict[str, Any]]:
        """
        Long-poll Telegram for new updates. Blocks for up to 30 seconds.
        Returns a list of update objects.
        """
        url = f"{_TELEGRAM_API_BASE}{self._token}/getUpdates"
        params = {"offset": self._offset, "timeout": 30, "allowed_updates": ["message"]}
        try:
            async with self._http.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.warning("getUpdates returned HTTP %d", resp.status)
                    await asyncio.sleep(5)  # back off on errors to avoid hammering
                    return []
                data: dict[str, Any] = await resp.json()
                if not data.get("ok"):
                    return []
                updates: list[dict[str, Any]] = data.get("result", [])
                if updates:
                    self._offset = updates[-1]["update_id"] + 1
                return updates
        except Exception as exc:  # noqa: BLE001
            logger.debug("getUpdates error (normal during shutdown): %s", exc)
            return []

    async def _send_message(
        self, text: str, chat_id: str | None = None
    ) -> None:
        """
        Send a message to the configured chat ID. Splits messages that
        exceed Telegram's 4096-character limit.
        """
        if not self._allowed_user_id and chat_id is None:
            return  # No recipient yet (first-run, no message received)

        target_chat = chat_id or self._allowed_user_id
        if not target_chat:
            return

        url = f"{_TELEGRAM_API_BASE}{self._token}/sendMessage"
        # Split long messages at word boundaries
        chunks = [text[i : i + _MAX_MESSAGE_LENGTH] for i in range(0, len(text), _MAX_MESSAGE_LENGTH)]
        for chunk in chunks:
            payload: dict[str, Any] = {
                "chat_id": target_chat,
                "text": chunk,
                "disable_web_page_preview": True,
            }
            try:
                async with self._http.post(url, json=payload) as resp:
                    if resp.status != 200:
                        body = await resp.text()
                        logger.warning("sendMessage HTTP %d: %s", resp.status, body[:200])
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to send Telegram message: %s", exc)

    # ── Security firewall ─────────────────────────────────────────────────

    def _is_authorized(self, user_id: str) -> bool:
        """
        Return True if the sender is the registered owner.
        On first contact (no owner registered), registers the sender.
        """
        if self._allowed_user_id is None:
            # Auto-register first user
            _auto_register_user(user_id)
            self._allowed_user_id = user_id
            logger.info("Auto-registered first user as owner: %s", user_id)
            return True

        return user_id == self._allowed_user_id

    # ── Update dispatcher ─────────────────────────────────────────────────

    async def _dispatch(self, update: dict[str, Any]) -> None:
        """Route a Telegram update to the correct command handler."""
        message: dict[str, Any] | None = update.get("message")
        if not message:
            return

        chat_id = str(message["chat"]["id"])
        from_user = message.get("from", {})
        user_id = str(from_user.get("id", ""))
        text: str = message.get("text", "").strip()

        # Security check
        if not self._is_authorized(user_id):
            logger.warning("Blocked unauthorized user: %s", user_id)
            await self._send_message("Unauthorized.", chat_id=chat_id)
            return

        # Handle photo messages (receipts)
        if message.get("photo"):
            caption = message.get("caption", "").strip()
            logger.info("Receipt photo from %s (caption: %s)", user_id, caption[:60])
            try:
                await self._handle_receipt_photo(chat_id, message)
            except Exception as exc:  # noqa: BLE001
                logger.error("Receipt handler raised: %s", exc)
                await self._send_message(f"Error saving receipt: {exc}", chat_id=chat_id)
            return

        if not text:
            return

        logger.info("Command from %s: %s", user_id, text[:80])

        # Route to handler
        cmd_parts = text.split(maxsplit=1)
        cmd = cmd_parts[0].lower().split("@")[0]  # strip @botname suffix
        arg = cmd_parts[1] if len(cmd_parts) > 1 else ""

        handlers: dict[str, Any] = {
            "/start": self._cmd_help,
            "/help": self._cmd_help,
            "/status": self._cmd_status,
            "/analyze": self._cmd_analyze,
            "/positions": self._cmd_positions,
            "/trades": self._cmd_trades,
            "/pnl": self._cmd_pnl,
            "/risk": self._cmd_risk,
            "/watchlist": self._cmd_watchlist,
            "/scan": self._cmd_scan,
            "/pause": self._cmd_pause,
            "/resume": self._cmd_resume,
            "/kill": self._cmd_kill,
            "/receipts": self._cmd_receipts,
            "/expenses": self._cmd_expenses,
            "/deductions": self._cmd_deductions,
            "/addexpense": self._cmd_add_expense,
        }

        handler = handlers.get(cmd)
        if handler:
            try:
                await handler(chat_id, arg)
            except Exception as exc:  # noqa: BLE001
                logger.error("Command handler '%s' raised: %s", cmd, exc)
                await self._send_message(
                    f"Error processing {cmd}: {exc}", chat_id=chat_id
                )
        else:
            await self._send_message(
                f"Unknown command: {cmd}\nSend /help to see all commands.",
                chat_id=chat_id,
            )

    # ── Command handlers ──────────────────────────────────────────────────

    async def _cmd_help(self, chat_id: str, _arg: str) -> None:
        await self._send_message(_format_help(), chat_id=chat_id)

    async def _cmd_status(self, chat_id: str, _arg: str) -> None:
        try:
            await self._send_message(_format_status(), chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Could not load status: {exc}", chat_id=chat_id)

    async def _cmd_analyze(self, chat_id: str, arg: str) -> None:
        symbol = arg.strip().upper() or "BTC/USDT"
        await self._send_message(
            f"Running analysis on {symbol}...", chat_id=chat_id
        )
        try:
            # TODO: integrate with multi-agent orchestrator when implemented.
            # For now, return the last signal for this symbol.
            with get_session() as session:
                sig = (
                    session.query(Signal)
                    .filter(Signal.symbol == symbol)
                    .order_by(Signal.timestamp.desc())
                    .first()
                )
            if sig:
                ts = sig.timestamp.strftime("%Y-%m-%d %H:%M") if sig.timestamp else "?"
                reply = (
                    f"Last signal for {symbol}:\n"
                    f"Direction: {sig.direction.upper()}\n"
                    f"Conviction: {sig.conviction:.2f}\n"
                    f"Strategy: {sig.strategy}\n"
                    f"Agent: {sig.source_agent}\n"
                    f"Time: {ts} UTC\n"
                    f"Executed: {'Yes' if sig.executed else 'No'}"
                )
            else:
                reply = f"No signals found for {symbol}. The engine may not have scanned it yet."
            await self._send_message(reply, chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Analysis failed: {exc}", chat_id=chat_id)

    async def _cmd_positions(self, chat_id: str, _arg: str) -> None:
        try:
            await self._send_message(_format_positions(), chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Could not load positions: {exc}", chat_id=chat_id)

    async def _cmd_trades(self, chat_id: str, _arg: str) -> None:
        try:
            await self._send_message(_format_trades(), chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Could not load trades: {exc}", chat_id=chat_id)

    async def _cmd_pnl(self, chat_id: str, _arg: str) -> None:
        try:
            await self._send_message(_format_pnl(), chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Could not load P&L: {exc}", chat_id=chat_id)

    async def _cmd_risk(self, chat_id: str, _arg: str) -> None:
        try:
            await self._send_message(_format_risk(), chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Could not load risk metrics: {exc}", chat_id=chat_id)

    async def _cmd_watchlist(self, chat_id: str, _arg: str) -> None:
        try:
            import yaml

            cfg_path = _ROOT / "config" / "strategies.yaml"
            if not cfg_path.exists():
                await self._send_message("No strategies.yaml found.", chat_id=chat_id)
                return

            with open(cfg_path) as fh:
                raw: dict[str, Any] = yaml.safe_load(fh) or {}

            strategies = raw.get("strategies", {})
            all_symbols: set[str] = set()
            for cfg in strategies.values():
                if cfg.get("enabled", True):
                    all_symbols.update(cfg.get("symbols", []))

            if not all_symbols:
                await self._send_message("Watchlist is empty.", chat_id=chat_id)
                return

            lines = [f"Watchlist ({len(all_symbols)} symbols):"]
            for sym in sorted(all_symbols):
                lines.append(f"  {sym}")
            await self._send_message("\n".join(lines), chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Could not load watchlist: {exc}", chat_id=chat_id)

    async def _cmd_scan(self, chat_id: str, _arg: str) -> None:
        await self._send_message(
            "Triggering market scan...", chat_id=chat_id
        )
        try:
            from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

            mode = TradingMode.PAPER if settings.is_paper else TradingMode.LIVE
            engine = TradingEngine(mode=mode, strategy_names=["all"])
            await engine._setup()
            for strategy_name, strategy_config in engine._strategies.items():
                await engine._tick(strategy_name, strategy_config)
            await engine._teardown()
            await self._send_message("Market scan complete.", chat_id=chat_id)
        except Exception as exc:  # noqa: BLE001
            await self._send_message(f"Scan failed: {exc}", chat_id=chat_id)

    async def _cmd_pause(self, chat_id: str, _arg: str) -> None:
        global _trading_paused
        _trading_paused = True
        logger.info("Trading PAUSED via Telegram command.")
        await self._send_message(
            "Trading paused. The agent will continue monitoring but will not place new orders.\n"
            "Send /resume to restart.",
            chat_id=chat_id,
        )

    async def _cmd_resume(self, chat_id: str, _arg: str) -> None:
        global _trading_paused
        _trading_paused = False
        logger.info("Trading RESUMED via Telegram command.")
        await self._send_message("Trading resumed.", chat_id=chat_id)

    async def _cmd_kill(self, chat_id: str, _arg: str) -> None:
        global _trading_paused
        _trading_paused = True
        logger.warning("KILL SWITCH activated via Telegram.")
        await self._send_message(
            "KILL SWITCH ACTIVATED\n"
            "Trading halted. All open position closures are queued.\n"
            "Note: automatic position closing requires live exchange connection.\n"
            "Send /resume to restart when ready.",
            chat_id=chat_id,
        )
        # Signal the main shutdown event to stop the daemon
        self._shutdown_event.set()

    # ── Receipt & Expense handlers ─────────────────────────────────────────

    async def _handle_receipt_photo(self, chat_id: str, message: dict[str, Any]) -> None:
        """Download a photo sent to the bot and save it as a receipt."""
        photos: list[dict[str, Any]] = message["photo"]
        # Telegram sends multiple sizes — take the largest (last)
        best_photo = photos[-1]
        file_id: str = best_photo["file_id"]
        caption: str = message.get("caption", "").strip()

        # Get file path from Telegram
        url = f"{_TELEGRAM_API_BASE}{self._token}/getFile"
        async with self._http.get(url, params={"file_id": file_id}) as resp:
            if resp.status != 200:
                await self._send_message("Failed to retrieve photo from Telegram.", chat_id=chat_id)
                return
            data = await resp.json()
            if not data.get("ok"):
                await self._send_message("Failed to retrieve photo from Telegram.", chat_id=chat_id)
                return
            file_path_tg: str = data["result"]["file_path"]

        # Download the file
        download_url = f"https://api.telegram.org/file/bot{self._token}/{file_path_tg}"
        async with self._http.get(download_url) as resp:
            if resp.status != 200:
                await self._send_message("Failed to download photo.", chat_id=chat_id)
                return
            file_bytes = await resp.read()

        # Save to data/receipts/
        _RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
        today = datetime.date.today()
        ext = Path(file_path_tg).suffix or ".jpg"
        filename = f"{today.isoformat()}_{file_id[:12]}{ext}"
        save_path = _RECEIPTS_DIR / filename
        save_path.write_bytes(file_bytes)
        logger.info("Receipt saved: %s (%d bytes)", save_path, len(file_bytes))

        # Parse caption for amount and vendor (format: "vendor amount" or just send photo)
        vendor = None
        amount = None
        if caption:
            parts = caption.rsplit(maxsplit=1)
            # Try to parse last word as amount
            if len(parts) >= 2:
                try:
                    amount = float(parts[-1].replace("$", "").replace(",", ""))
                    vendor = parts[0]
                except ValueError:
                    vendor = caption
            else:
                # Single word — try as amount, else treat as vendor
                try:
                    amount = float(caption.replace("$", "").replace(",", ""))
                except ValueError:
                    vendor = caption

        # Save to database
        with get_session() as session:
            receipt = Receipt(
                date=today,
                file_path=str(save_path),
                file_id=file_id,
                vendor=vendor,
                amount=amount,
                is_business_deductible=True,
            )
            session.add(receipt)
            session.commit()
            receipt_id = receipt.id

        # Confirm to user
        lines = [f"Receipt #{receipt_id} saved"]
        if vendor:
            lines.append(f"Vendor: {vendor}")
        if amount is not None:
            lines.append(f"Amount: ${amount:,.2f}")
        lines.append(f"Date: {today.isoformat()}")
        lines.append("")
        lines.append("Tip: send photo with caption like:")
        lines.append('"Staples 45.99" to auto-fill vendor + amount')
        await self._send_message("\n".join(lines), chat_id=chat_id)

    async def _cmd_receipts(self, chat_id: str, arg: str) -> None:
        """Show recent receipts. Usage: /receipts [count]"""
        count = 10
        if arg.strip().isdigit():
            count = min(int(arg.strip()), 50)

        with get_session() as session:
            receipts = (
                session.query(Receipt)
                .order_by(Receipt.date.desc())
                .limit(count)
                .all()
            )
            if not receipts:
                await self._send_message("No receipts yet. Send a photo to log one.", chat_id=chat_id)
                return

            lines = [f"Last {len(receipts)} Receipts:\n"]
            total = 0.0
            for r in receipts:
                amt_str = f"${r.amount:,.2f}" if r.amount else "?"
                vendor_str = r.vendor or "Unknown"
                cat_str = f" [{r.category}]" if r.category else ""
                lines.append(f"#{r.id} | {r.date} | {vendor_str} | {amt_str}{cat_str}")
                if r.amount:
                    total += r.amount
            lines.append(f"\nTotal: ${total:,.2f}")
        await self._send_message("\n".join(lines), chat_id=chat_id)

    async def _cmd_expenses(self, chat_id: str, arg: str) -> None:
        """Show expense summary. Usage: /expenses [month] (e.g. /expenses 2026-03)"""
        today = datetime.date.today()
        if arg.strip():
            try:
                parts = arg.strip().split("-")
                year, month = int(parts[0]), int(parts[1])
            except (ValueError, IndexError):
                await self._send_message("Usage: /expenses 2026-03", chat_id=chat_id)
                return
        else:
            year, month = today.year, today.month

        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month + 1, 1)

        with get_session() as session:
            # From receipts
            receipts = (
                session.query(Receipt)
                .filter(Receipt.date >= start_date, Receipt.date < end_date)
                .order_by(Receipt.date.asc())
                .all()
            )
            # From expenses table
            expenses = (
                session.query(Expense)
                .filter(Expense.date >= start_date, Expense.date < end_date)
                .order_by(Expense.date.asc())
                .all()
            )

        receipt_total = sum(r.amount for r in receipts if r.amount)
        expense_total = sum(e.amount for e in expenses)
        biz_total = sum(r.amount for r in receipts if r.amount and r.is_business_deductible)
        biz_total += sum(e.amount for e in expenses if e.is_business_deductible)

        month_name = start_date.strftime("%B %Y")
        lines = [
            f"Expense Summary — {month_name}\n",
            f"Receipts logged: {len(receipts)}",
            f"Receipt total: ${receipt_total:,.2f}",
            f"Manual expenses: {len(expenses)}",
            f"Expense total: ${expense_total:,.2f}",
            f"Combined: ${receipt_total + expense_total:,.2f}",
            f"\nBusiness deductible: ${biz_total:,.2f}",
        ]

        # Category breakdown from receipts
        cats: dict[str, float] = {}
        for r in receipts:
            if r.amount:
                cat = r.category or "Uncategorized"
                cats[cat] = cats.get(cat, 0) + r.amount
        for e in expenses:
            cats[e.category] = cats.get(e.category, 0) + e.amount

        if cats:
            lines.append("\nBy Category:")
            for cat, amt in sorted(cats.items(), key=lambda x: -x[1]):
                lines.append(f"  {cat}: ${amt:,.2f}")

        await self._send_message("\n".join(lines), chat_id=chat_id)

    async def _cmd_deductions(self, chat_id: str, arg: str) -> None:
        """Show YTD business deductions for T2125. Usage: /deductions [year]"""
        today = datetime.date.today()
        year = int(arg.strip()) if arg.strip().isdigit() else today.year
        start = datetime.date(year, 1, 1)
        end = datetime.date(year + 1, 1, 1)

        with get_session() as session:
            receipts = (
                session.query(Receipt)
                .filter(
                    Receipt.date >= start,
                    Receipt.date < end,
                    Receipt.is_business_deductible.is_(True),
                )
                .all()
            )
            expenses = (
                session.query(Expense)
                .filter(
                    Expense.date >= start,
                    Expense.date < end,
                    Expense.is_business_deductible.is_(True),
                )
                .all()
            )

        # Aggregate by T2125 category
        t2125: dict[str, float] = {}
        for r in receipts:
            if r.amount:
                line = r.t2125_line or r.category or "Other"
                t2125[line] = t2125.get(line, 0) + r.amount
        for e in expenses:
            line = e.category or "Other"
            t2125[line] = t2125.get(line, 0) + e.amount

        total = sum(t2125.values())
        lines = [
            f"T2125 Business Deductions — {year}\n",
        ]
        for cat, amt in sorted(t2125.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: ${amt:,.2f}")
        lines.append(f"\nTotal deductions: ${total:,.2f}")

        # Estimate tax savings at marginal rate
        if total > 0:
            marginal_rate = 0.2965 if total < 55000 else 0.3348  # ON first/second bracket
            lines.append(f"Estimated tax savings: ${total * marginal_rate:,.2f}")
            lines.append(f"(at {marginal_rate*100:.1f}% marginal rate)")

        await self._send_message("\n".join(lines), chat_id=chat_id)

    async def _cmd_add_expense(self, chat_id: str, arg: str) -> None:
        """Manually add an expense. Usage: /addexpense category amount description"""
        if not arg.strip():
            await self._send_message(
                "Usage: /addexpense category amount description\n"
                "Example: /addexpense Business 29.99 Adobe Creative Cloud subscription\n\n"
                "Categories: Housing, Food, Transport, Business, Entertainment, "
                "Subscriptions, Savings, Investing, Other",
                chat_id=chat_id,
            )
            return

        parts = arg.strip().split(maxsplit=2)
        if len(parts) < 2:
            await self._send_message("Need at least category and amount.", chat_id=chat_id)
            return

        category = parts[0].capitalize()
        try:
            amount = float(parts[1].replace("$", "").replace(",", ""))
        except ValueError:
            await self._send_message(f"Invalid amount: {parts[1]}", chat_id=chat_id)
            return
        description = parts[2] if len(parts) > 2 else ""

        is_biz = category.lower() in ("business", "transport", "subscriptions")
        today = datetime.date.today()

        with get_session() as session:
            expense = Expense(
                date=today,
                amount=amount,
                category=category,
                description=description,
                is_business_deductible=is_biz,
            )
            session.add(expense)
            session.commit()
            expense_id = expense.id

        biz_tag = " [DEDUCTIBLE]" if is_biz else ""
        await self._send_message(
            f"Expense #{expense_id} added\n"
            f"{category}: ${amount:,.2f}{biz_tag}\n"
            f"{description}" if description else f"Expense #{expense_id} added\n{category}: ${amount:,.2f}{biz_tag}",
            chat_id=chat_id,
        )

    # ── Public alert API (called by autonomous.py) ─────────────────────────

    async def alert_trade_opened(
        self,
        symbol: str,
        direction: str,
        size: float,
        entry_price: float,
        conviction: float,
        strategy: str = "",
    ) -> None:
        """Send a trade-opened alert. Called by the engine after execution."""
        emoji = "🟢" if direction.upper() == "LONG" else "🔴"
        lines = [
            f"{emoji} Trade Opened",
            f"{direction.upper()} {symbol} @ ${entry_price:,.2f}",
            f"Size: {size:.4f} | Conviction: {conviction:.2f}",
        ]
        if strategy:
            lines.append(f"Strategy: {strategy}")
        await self._send_message("\n".join(lines))

    async def alert_trade_closed(
        self,
        symbol: str,
        direction: str,
        pnl: float,
        exit_reason: str,
    ) -> None:
        """Send a trade-closed alert."""
        sign = "+" if pnl >= 0 else ""
        emoji = "📈" if pnl >= 0 else "📉"
        await self._send_message(
            f"{emoji} Trade Closed\n"
            f"{direction.upper()} {symbol}\n"
            f"PnL: {sign}${pnl:,.2f} | Reason: {exit_reason}"
        )

    async def alert_kill_switch(self, reason: str, drawdown_pct: float) -> None:
        """Send a kill switch alert."""
        await self._send_message(
            f"🔴 KILL SWITCH TRIGGERED\n"
            f"Reason: {reason}\n"
            f"Drawdown: {drawdown_pct:.1f}%\n"
            f"All trading halted. Manual review required."
        )


# ─────────────────────────────────────────────────────────────────────────────
#  Standalone entry point
# ─────────────────────────────────────────────────────────────────────────────


async def _standalone_main() -> None:
    """Run the Telegram bridge in standalone mode (no autonomous trading)."""
    import signal as _signal

    shutdown_event = asyncio.Event()

    def _handle_signal(signum: int, frame: object) -> None:
        logger.info("Signal %d — shutting down bridge.", signum)
        shutdown_event.set()

    _signal.signal(_signal.SIGINT, _handle_signal)
    _signal.signal(_signal.SIGTERM, _handle_signal)

    bridge = TelegramBridge(shutdown_event=shutdown_event)
    await bridge.run()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(_standalone_main())
