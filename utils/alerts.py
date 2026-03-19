"""
utils/alerts.py
---------------
Telegram Alert System for Atlas Trading Agent.

Delivers structured trade notifications and system alerts to a Telegram chat.

Alert levels
------------
  INFO     — general informational messages
  TRADE    — trade opened/closed with full parameters
  WARNING  — risk thresholds approaching
  CRITICAL — kill switches triggered, system halted

Rate limiting
-------------
Maximum 30 messages per minute (Telegram Bot API hard limit is ~30/s but
we keep it conservative for readability).  Messages that exceed the rate
limit are queued and sent in the next available slot.

Async design
------------
send_*() methods return immediately by putting the message onto an asyncio
Queue.  A background consumer task drains the queue and calls the Telegram
API.  This ensures that alerts never block the trading loop.

Usage
-----
  async with AlertSender() as alert:
      await alert.send_trade_opened("BTC/USDT", "LONG", 64230, 0.5, 63200, 67300, 0.78)
      await alert.send_critical("Max drawdown hit — trading halted")
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any

import aiohttp

from config.settings import settings

logger = logging.getLogger("atlas.alerts")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_TELEGRAM_API_BASE = "https://api.telegram.org/bot"
_MAX_MESSAGES_PER_MINUTE = 30
_QUEUE_MAXSIZE = 200
_RETRY_ATTEMPTS = 3
_RETRY_DELAY_S = 2.0


# ---------------------------------------------------------------------------
# AlertLevel
# ---------------------------------------------------------------------------


class AlertLevel(str, Enum):
    INFO = "INFO"
    TRADE = "TRADE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# AlertSender
# ---------------------------------------------------------------------------


class AlertSender:
    """
    Non-blocking Telegram alert dispatcher.

    Must be used as an async context manager to start/stop the background
    consumer task:

        async with AlertSender() as alert:
            await alert.send_info("System online")

    If Telegram is not configured (missing bot_token or chat_id) all methods
    are no-ops; no exceptions are raised.
    """

    def __init__(self) -> None:
        self._token = settings.telegram.telegram_bot_token
        self._chat_id = settings.telegram.telegram_chat_id
        self._enabled = settings.telegram.enabled
        self._session: aiohttp.ClientSession | None = None
        self._queue: asyncio.Queue[str] = asyncio.Queue(maxsize=_QUEUE_MAXSIZE)
        self._consumer_task: asyncio.Task[None] | None = None
        # Rate-limit state
        self._sent_timestamps: list[float] = []

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AlertSender":
        if not self._enabled:
            logger.info("Telegram alerts disabled (no credentials configured)")
            return self
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        self._consumer_task = asyncio.create_task(self._consume_queue(), name="alert-consumer")
        logger.info("AlertSender started (chat_id=%s)", self._chat_id)
        return self

    async def __aexit__(self, *_: Any) -> None:
        # Drain the queue before shutting down
        if self._consumer_task is not None:
            await self._queue.join()  # wait until all items are processed
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        if self._session is not None:
            await self._session.close()

    # ------------------------------------------------------------------
    # Public alert methods
    # ------------------------------------------------------------------

    async def send_info(self, message: str) -> None:
        """Send an informational notification."""
        await self._enqueue(f"ℹ️ {message}")

    async def send_trade_opened(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        size: float,
        stop_loss: float,
        take_profit: float,
        conviction: float,
        strategy: str = "",
    ) -> None:
        """
        Send a trade-opened alert.

        Example output:
        🟢 LONG BTC/USDT @ $64,230
        Size: 0.5000 | SL: $63,200 | TP: $67,300
        Conviction: 0.78 | Strategy: ema_crossover
        """
        emoji = "🟢" if direction.upper() == "LONG" else "🔴"
        rr_distance = abs(entry_price - stop_loss)
        tp_distance = abs(take_profit - entry_price)
        rr = tp_distance / rr_distance if rr_distance > 0 else 0.0
        lines = [
            f"{emoji} {direction.upper()} {symbol} @ ${entry_price:,.2f}",
            f"Size: {size:.4f} | SL: ${stop_loss:,.2f} | TP: ${take_profit:,.2f}",
            f"Conviction: {conviction:.2f} | R:R: {rr:.1f}x",
        ]
        if strategy:
            lines.append(f"Strategy: {strategy}")
        await self._enqueue("\n".join(lines))

    async def send_trade_closed(
        self,
        symbol: str,
        direction: str,
        exit_price: float,
        pnl: float,
        pnl_pct: float,
        exit_reason: str,
    ) -> None:
        """
        Send a trade-closed alert.

        Example:
        🔵 CLOSED LONG BTC/USDT @ $65,100
        PnL: +$870.00 (+1.36%) | Reason: TAKE_PROFIT
        """
        pnl_sign = "+" if pnl >= 0 else ""
        lines = [
            f"🔵 CLOSED {direction.upper()} {symbol} @ ${exit_price:,.2f}",
            f"PnL: {pnl_sign}${pnl:,.2f} ({pnl_sign}{pnl_pct:.2f}%) | Reason: {exit_reason}",
        ]
        await self._enqueue("\n".join(lines))

    async def send_warning(self, message: str) -> None:
        """Send a risk warning alert."""
        await self._enqueue(f"⚠️ WARNING\n{message}")

    async def send_critical(self, message: str) -> None:
        """Send a CRITICAL alert (kill switch triggered, system halted, etc.)."""
        await self._enqueue(f"🔴 CRITICAL\n{message}")

    async def send_daily_summary(
        self,
        date: str,
        pnl: float,
        pnl_pct: float,
        trades_opened: int,
        trades_closed: int,
        current_equity: float,
        drawdown_pct: float,
    ) -> None:
        """Send the end-of-day performance summary."""
        sign = "+" if pnl >= 0 else ""
        emoji = "📈" if pnl >= 0 else "📉"
        lines = [
            f"{emoji} Daily Summary — {date}",
            f"P&L: {sign}${pnl:,.2f} ({sign}{pnl_pct:.2f}%)",
            f"Equity: ${current_equity:,.2f} | Drawdown: {drawdown_pct:.2f}%",
            f"Trades: {trades_opened} opened, {trades_closed} closed",
        ]
        await self._enqueue("\n".join(lines))

    async def send_drawdown_warning(self, current_pct: float, limit_pct: float) -> None:
        """Convenience method for a drawdown-approaching warning."""
        await self.send_warning(
            f"Drawdown at {current_pct:.1f}% (limit: {limit_pct:.1f}%). "
            "Reducing position sizes."
        )

    async def send_daily_loss_warning(self, current_pct: float, limit_pct: float) -> None:
        """Convenience method for a daily-loss-approaching warning."""
        await self.send_warning(
            f"Daily loss at {current_pct:.1f}% (limit: {limit_pct:.1f}%). "
            "Monitor closely."
        )

    async def send_halt_alert(self, reason: str, drawdown_pct: float) -> None:
        """Alert when a kill switch halts all trading."""
        await self.send_critical(
            f"ALL TRADING HALTED\n"
            f"Reason: {reason}\n"
            f"Drawdown: {drawdown_pct:.1f}%\n"
            f"Manual review required before resuming."
        )

    # ------------------------------------------------------------------
    # Internal queue management
    # ------------------------------------------------------------------

    async def _enqueue(self, text: str) -> None:
        """Put a message on the outbound queue (non-blocking)."""
        if not self._enabled:
            return
        try:
            self._queue.put_nowait(text)
        except asyncio.QueueFull:
            logger.warning("Alert queue full — dropping message: %s", text[:80])

    async def _consume_queue(self) -> None:
        """
        Background task that drains the queue and sends messages via Telegram.
        Enforces rate limiting of _MAX_MESSAGES_PER_MINUTE.
        """
        while True:
            text = await self._queue.get()
            try:
                await self._rate_limit_check()
                await self._send_telegram(text)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("Failed to send Telegram alert: %s", exc)
            finally:
                self._queue.task_done()

    async def _rate_limit_check(self) -> None:
        """Block until we are under the rate limit, then record this send."""
        now = time.monotonic()
        # Remove timestamps older than 60 seconds
        self._sent_timestamps = [t for t in self._sent_timestamps if now - t < 60.0]

        if len(self._sent_timestamps) >= _MAX_MESSAGES_PER_MINUTE:
            oldest = self._sent_timestamps[0]
            wait_for = 60.0 - (now - oldest) + 0.1  # small buffer
            if wait_for > 0:
                logger.debug("Rate limit: sleeping %.1fs before next Telegram send", wait_for)
                await asyncio.sleep(wait_for)

        self._sent_timestamps.append(time.monotonic())

    async def _send_telegram(self, text: str) -> None:
        """Call the Telegram sendMessage endpoint with retry logic."""
        if self._session is None:
            return

        url = f"{_TELEGRAM_API_BASE}{self._token}/sendMessage"
        payload: dict[str, Any] = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }

        for attempt in range(1, _RETRY_ATTEMPTS + 1):
            try:
                async with self._session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        return
                    body = await resp.text()
                    logger.warning(
                        "Telegram API returned %d on attempt %d: %s",
                        resp.status,
                        attempt,
                        body[:200],
                    )
                    # Only retry on transient server errors (5xx) or rate-limit (429).
                    # 4xx errors (except 429) are permanent failures — retrying would
                    # duplicate the message if Telegram processed the request.
                    if resp.status not in (429, 500, 502, 503, 504):
                        break
            except aiohttp.ClientError as exc:
                # Do NOT retry on ClientError: the request may have already been
                # delivered (e.g. ServerDisconnectedError after Telegram processed
                # the POST). Retrying would send duplicate messages.
                logger.warning("Telegram request error: %s", exc)
                break

            if attempt < _RETRY_ATTEMPTS:
                await asyncio.sleep(_RETRY_DELAY_S * attempt)

        logger.error("Telegram message failed after %d attempts: %s", _RETRY_ATTEMPTS, text[:100])
