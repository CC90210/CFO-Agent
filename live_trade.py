"""
live_trade.py
--------------
Standalone LIVE trading runner for Atlas Trading Agent.

Starts the trading engine in LIVE mode with all enabled strategies, then
refreshes a terminal dashboard every 60 seconds showing portfolio state,
open positions, today's trades, and risk status.

IMPORTANT: This places REAL orders on Kraken with REAL money.
All safety guards remain active (kill switches, max DD, daily loss limit).

Usage
-----
    python live_trade.py

Requires in .env:
    PAPER_TRADE=false
    CONFIRM_LIVE=true
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any

# Force UTF-8 output on Windows to support box-drawing characters.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# Ensure the project root is on sys.path when running as a script.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ─────────────────────────────────────────────────────────────────────────────
#  Logging — configure before any project imports
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,  # Show more detail for live trading
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Keep atlas-level INFO for trade events visible in the log file
_log_dir = _ROOT / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_file_handler = logging.FileHandler(_log_dir / "live_trade.log")
_file_handler.setLevel(logging.INFO)
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s — %(message)s")
)
logging.getLogger("atlas").addHandler(_file_handler)
logging.getLogger("atlas").setLevel(logging.INFO)
logging.getLogger("core").addHandler(_file_handler)
logging.getLogger("core").setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports (after path + logging setup)
# ─────────────────────────────────────────────────────────────────────────────

from config.settings import settings  # noqa: E402
from db.database import get_session, init_db  # noqa: E402
from db.models import DailyPnL, PortfolioSnapshot, Signal, Trade  # noqa: E402
from utils.alerts import AlertSender  # noqa: E402

logger = logging.getLogger("atlas.live_trade")

# ─────────────────────────────────────────────────────────────────────────────
#  Dashboard rendering (adapted from paper_trade.py)
# ─────────────────────────────────────────────────────────────────────────────

_BOX_WIDTH = 66


def _box_line(content: str = "", fill: str = " ") -> str:
    padded = content.ljust(_BOX_WIDTH)[:_BOX_WIDTH]
    return f"║  {padded}  ║"


def _divider(left: str = "╠", right: str = "╣", fill: str = "═") -> str:
    return f"{left}{fill * (_BOX_WIDTH + 4)}{right}"


def _sign(value: float) -> str:
    return "+" if value >= 0 else ""


def _render_dashboard(state: dict[str, Any]) -> str:
    pv = state.get("portfolio_value", 0.0)
    sv = state.get("start_value", 0.0)
    total_pnl_pct = ((pv - sv) / sv * 100.0) if sv else 0.0
    cash = state.get("cash", pv)
    drawdown = state.get("drawdown_pct", 0.0)
    max_dd = state.get("max_drawdown_pct", settings.risk.max_drawdown_pct)
    daily_pnl = state.get("daily_pnl", 0.0)
    positions: list[dict[str, Any]] = state.get("positions", [])
    trades_today = state.get("trades_today", 0)
    wins = state.get("wins_today", 0)
    losses = state.get("losses_today", 0)
    last_signal: dict[str, Any] | None = state.get("last_signal")
    ts: datetime.datetime = state.get("timestamp", datetime.datetime.now(datetime.UTC))

    win_rate = (wins / trades_today * 100.0) if trades_today > 0 else 0.0
    daily_loss_str = f"-${abs(daily_pnl):,.2f}" if daily_pnl < 0 else f"+${daily_pnl:,.2f}"

    lines: list[str] = []
    lines.append(f"╔{'═' * (_BOX_WIDTH + 4)}╗")
    lines.append(_box_line("ATLAS LIVE TRADING  [REAL MONEY]"))
    lines.append(_box_line(f"Updated: {ts.strftime('%Y-%m-%d %H:%M:%S UTC')}"))
    lines.append(_divider())

    pv_str = f"${pv:,.2f} ({_sign(total_pnl_pct)}{total_pnl_pct:.2f}%)"
    lines.append(_box_line(f"Portfolio: {pv_str}  |  Cash: ${cash:,.2f}"))
    lines.append(_box_line(
        f"Drawdown: {abs(drawdown):.1f}% / {max_dd:.1f}%  |  "
        f"Daily P&L: {daily_loss_str}"
    ))

    lines.append(_divider())
    lines.append(_box_line("OPEN POSITIONS"))

    if positions:
        for pos in positions:
            sym = pos.get("symbol", "???")[:9].ljust(9)
            side = pos.get("side", "LONG").upper()[:5].ljust(5)
            size = pos.get("size", 0.0)
            entry = pos.get("entry_price", 0.0)
            upnl = pos.get("unrealized_pnl", 0.0)
            upnl_pct = pos.get("unrealized_pnl_pct", 0.0)
            row = (
                f"{sym}  {side}  {size:.6f}  @ ${entry:,.2f}  "
                f"P&L: {_sign(upnl)}${abs(upnl):,.2f} ({_sign(upnl_pct)}{upnl_pct:.1f}%)"
            )
            lines.append(_box_line(row))
    else:
        lines.append(_box_line("  (no open positions)"))

    lines.append(_divider())

    win_rate_str = f"{win_rate:.1f}%" if trades_today > 0 else "N/A"
    lines.append(_box_line(
        f"TODAY'S TRADES: {trades_today} ({wins}W/{losses}L)  |  Win Rate: {win_rate_str}"
    ))

    if last_signal:
        sig_sym = last_signal.get("symbol", "")
        sig_dir = last_signal.get("direction", "")
        sig_conv = last_signal.get("conviction", 0.0)
        lines.append(_box_line(
            f"Last Signal: {sig_sym} {sig_dir}  (conviction: {sig_conv:.2f})"
        ))
    else:
        lines.append(_box_line("Last Signal: waiting for setup..."))

    lines.append(_divider())
    lines.append(_box_line("SAFETY: 15% max DD | 5% daily limit | 1% per trade"))
    lines.append(_box_line("All kill switches ACTIVE. Scale-out DISABLED."))
    lines.append(f"╚{'═' * (_BOX_WIDTH + 4)}╝")

    return "\n".join(lines)


def _clear_terminal() -> None:
    try:
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()
    except OSError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  State collection from database
# ─────────────────────────────────────────────────────────────────────────────


def _load_state_from_db(start_value: float) -> dict[str, Any]:
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
            .filter(
                Trade.mode == "live",
                Trade.closed_at >= today_start,
                Trade.pnl.isnot(None),
            )
            .all()
        )
        last_signal_row = (
            session.query(Signal)
            .order_by(Signal.timestamp.desc())
            .first()
        )

        positions: list[dict[str, Any]] = []
        if snapshot and snapshot.positions_json:
            positions = list(snapshot.positions_json)

        portfolio_value = snapshot.total_value if snapshot else start_value
        cash = snapshot.available_balance if snapshot else start_value
        drawdown_pct = snapshot.drawdown_pct if snapshot else 0.0
        daily_pnl = daily.realized_pnl if daily else 0.0

        wins = sum(1 for t in closed_trades if (t.pnl or 0.0) > 0)
        losses = sum(1 for t in closed_trades if (t.pnl or 0.0) <= 0)

        last_signal: dict[str, Any] | None = None
        if last_signal_row:
            last_signal = {
                "symbol": last_signal_row.symbol,
                "direction": last_signal_row.direction.upper(),
                "conviction": last_signal_row.conviction,
            }

    return {
        "portfolio_value": portfolio_value,
        "start_value": start_value,
        "cash": cash,
        "drawdown_pct": drawdown_pct,
        "max_drawdown_pct": settings.risk.max_drawdown_pct,
        "daily_pnl": daily_pnl,
        "daily_loss_limit": settings.risk.daily_loss_limit_pct,
        "positions": positions,
        "trades_today": len(closed_trades),
        "wins_today": wins,
        "losses_today": losses,
        "last_signal": last_signal,
        "agent_scores": {},
        "risk_score": 0.0,
        "debate_skipped": False,
        "timestamp": datetime.datetime.now(datetime.UTC),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Dashboard refresh loop
# ─────────────────────────────────────────────────────────────────────────────

_DASHBOARD_INTERVAL_S: int = 60


async def _dashboard_loop(
    shutdown_event: asyncio.Event,
    start_value: float,
) -> None:
    while not shutdown_event.is_set():
        try:
            state = _load_state_from_db(start_value)
            _clear_terminal()
            print(_render_dashboard(state))
        except Exception as exc:
            logger.error("Dashboard refresh error: %s", exc)

        try:
            await asyncio.wait_for(
                asyncio.shield(shutdown_event.wait()),
                timeout=float(_DASHBOARD_INTERVAL_S),
            )
        except asyncio.TimeoutError:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────────────────────────────────────


async def main() -> None:
    # Safety gate: REQUIRE live trading flags
    if settings.exchange.paper_trade:
        print(
            "ERROR: PAPER_TRADE is still true in .env.\n"
            "Set PAPER_TRADE=false AND CONFIRM_LIVE=true to enable live trading.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not settings.is_live:
        print(
            "ERROR: CONFIRM_LIVE is not set to true in .env.\n"
            "Set CONFIRM_LIVE=true to confirm you want live trading.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("=" * 66)
    print("  ATLAS LIVE TRADING — REAL MONEY MODE")
    print("  All safety guards active. Kill switches cannot be overridden.")
    print("=" * 66)
    print()

    # Initialise database
    init_db()

    # Get Kraken balance as starting reference
    import ccxt
    kraken = ccxt.kraken({
        'apiKey': settings.exchange.exchange_api_key,
        'secret': settings.exchange.exchange_secret,
        'enableRateLimit': True,
    })

    try:
        balance = kraken.fetch_balance()
        btc_bal = float(balance.get('total', {}).get('BTC', 0))
        usdt_bal = float(balance.get('total', {}).get('USDT', 0))
        usd_bal = float(balance.get('total', {}).get('USD', 0))

        # Get BTC price for USD equivalent
        ticker = kraken.fetch_ticker('BTC/USDT')
        btc_price = ticker['last']
        start_value = btc_bal * btc_price + usdt_bal + usd_bal

        print(f"  Kraken Balance: {btc_bal:.6f} BTC (${btc_bal * btc_price:.2f})")
        if usdt_bal > 0:
            print(f"                  {usdt_bal:.2f} USDT")
        if usd_bal > 0:
            print(f"                  {usd_bal:.2f} USD")
        print(f"  Total Value:    ${start_value:.2f}")
        print(f"  Risk per trade: ${start_value * 0.01:.2f} (1%)")
        print()
    except Exception as e:
        logger.error("Failed to fetch Kraken balance: %s", e)
        start_value = 138.0  # fallback estimate
        print(f"  Using estimated start value: ${start_value:.2f}")

    shutdown_event = asyncio.Event()

    def _handle_signal(signum: int, frame: object) -> None:
        logger.info("Signal %d received — initiating shutdown.", signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    print(f"Live trading started. Starting equity: ${start_value:,.2f}")
    print("Press Ctrl+C to stop.\n")

    from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

    engine = TradingEngine(
        mode=TradingMode.LIVE,
        strategy_names=["all"],
        exchange_id=settings.exchange.default_exchange,
        initial_equity=start_value,
    )

    # Start Telegram bridge for two-way communication
    from telegram_bridge import TelegramBridge  # noqa: PLC0415

    telegram_bridge = TelegramBridge(shutdown_event=shutdown_event)

    async with AlertSender() as alert:
        await alert.send_info(
            f"ATLAS LIVE TRADING started.\n"
            f"Equity: ${start_value:,.2f} | "
            f"Exchange: {settings.exchange.default_exchange}\n"
            f"Risk: 1% per trade (${start_value * 0.01:.2f})\n"
            f"Telegram bridge active — reply /help for commands."
        )

        engine_task = asyncio.create_task(engine.start(), name="live-engine")
        dashboard_task = asyncio.create_task(
            _dashboard_loop(shutdown_event, start_value),
            name="dashboard",
        )
        telegram_task = asyncio.create_task(
            telegram_bridge.run(), name="telegram-bridge"
        )

        await shutdown_event.wait()

        engine_task.cancel()
        dashboard_task.cancel()
        telegram_task.cancel()

        for task in (engine_task, dashboard_task, telegram_task):
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                logger.error("Task teardown error: %s", exc)

        await alert.send_info("ATLAS LIVE TRADING stopped.")

    # Print final summary
    print("\n" + "=" * 66)
    print("  ATLAS LIVE TRADING — SESSION SUMMARY")
    print("=" * 66)
    try:
        state = _load_state_from_db(start_value)
        pv = state["portfolio_value"]
        total_pnl = pv - start_value
        total_pnl_pct = (total_pnl / start_value * 100.0) if start_value else 0.0
        print(f"  Start Value   : ${start_value:,.2f}")
        print(f"  Final Value   : ${pv:,.2f}")
        print(f"  Total P&L     : {_sign(total_pnl)}${abs(total_pnl):,.2f}  ({_sign(total_pnl_pct)}{total_pnl_pct:.2f}%)")
        print(f"  Trades Today  : {state['trades_today']}  ({state['wins_today']}W / {state['losses_today']}L)")
    except Exception:
        print("  Could not load final summary.")
    print("=" * 66)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
