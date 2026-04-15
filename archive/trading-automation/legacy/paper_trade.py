"""
paper_trade.py
--------------
Standalone paper trading runner for Atlas Trading Agent.

Starts the trading engine in PAPER mode with all enabled strategies, then
refreshes a terminal dashboard every 60 seconds showing portfolio state,
open positions, today's trades, agent conviction scores, and risk status.

Usage
-----
    python paper_trade.py

The dashboard prints in-place using ANSI escape codes (works on any modern
terminal — Windows Terminal, macOS Terminal, iTerm2, most Linux terminals).
Graceful shutdown on Ctrl+C prints a final portfolio summary.
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
    level=logging.WARNING,  # Suppress engine chatter — dashboard is the UI
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Keep atlas-level INFO for trade events visible in the log file, not stdout
_file_handler = logging.FileHandler(_ROOT / "logs" / "paper_trade.log")
_file_handler.setLevel(logging.INFO)
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s — %(message)s")
)
logging.getLogger("atlas").addHandler(_file_handler)
logging.getLogger("atlas").setLevel(logging.INFO)
# Also capture core.* module logs (engine, risk, protocol, trailing stops)
logging.getLogger("core").addHandler(_file_handler)
logging.getLogger("core").setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports (after path + logging setup)
# ─────────────────────────────────────────────────────────────────────────────

from config.settings import settings  # noqa: E402
from db.database import get_session, init_db  # noqa: E402
from db.models import DailyPnL, PortfolioSnapshot, Signal, Trade  # noqa: E402
from utils.alerts import AlertSender  # noqa: E402

logger = logging.getLogger("atlas.paper_trade")

# ─────────────────────────────────────────────────────────────────────────────
#  Dashboard rendering
# ─────────────────────────────────────────────────────────────────────────────

_BOX_WIDTH = 62  # inner width (between the ║ borders)


def _box_line(content: str = "", fill: str = " ") -> str:
    """Return a single dashboard row padded to _BOX_WIDTH."""
    padded = content.ljust(_BOX_WIDTH)[:_BOX_WIDTH]
    return f"║  {padded}  ║"


def _divider(left: str = "╠", right: str = "╣", fill: str = "═") -> str:
    return f"{left}{fill * (_BOX_WIDTH + 4)}{right}"


def _sign(value: float) -> str:
    return "+" if value >= 0 else ""


def _render_dashboard(state: dict[str, Any]) -> str:
    """
    Build the full dashboard string from the current portfolio state dict.

    Expected keys in ``state``:
        portfolio_value, start_value, cash, drawdown_pct, max_drawdown_pct,
        daily_pnl, daily_loss_limit, positions (list of dicts),
        trades_today, wins_today, losses_today, last_signal (dict or None),
        agent_scores (dict), risk_score, debate_skipped, timestamp
    """
    pv = state.get("portfolio_value", 10_000.0)
    sv = state.get("start_value", 10_000.0)
    total_pnl_pct = ((pv - sv) / sv * 100.0) if sv else 0.0
    cash = state.get("cash", pv)
    drawdown = state.get("drawdown_pct", 0.0)
    max_dd = state.get("max_drawdown_pct", settings.risk.max_drawdown_pct)
    daily_pnl = state.get("daily_pnl", 0.0)
    daily_limit = state.get("daily_loss_limit", settings.risk.daily_loss_limit_pct)
    positions: list[dict[str, Any]] = state.get("positions", [])
    trades_today = state.get("trades_today", 0)
    wins = state.get("wins_today", 0)
    losses = state.get("losses_today", 0)
    last_signal: dict[str, Any] | None = state.get("last_signal")
    agent_scores: dict[str, Any] = state.get("agent_scores", {})
    risk_score = state.get("risk_score", 0.0)
    debate_skipped = state.get("debate_skipped", False)
    ts: datetime.datetime = state.get("timestamp", datetime.datetime.now(datetime.UTC))

    win_rate = (wins / trades_today * 100.0) if trades_today > 0 else 0.0
    daily_loss_str = f"-${abs(daily_pnl):,.2f}" if daily_pnl < 0 else f"+${daily_pnl:,.2f}"
    daily_limit_str = f"-${sv * daily_limit / 100:,.2f}"

    lines: list[str] = []
    lines.append(f"╔{'═' * (_BOX_WIDTH + 4)}╗")
    lines.append(_box_line(f"ATLAS TRADING AGENT  —  Paper Trading Dashboard"))
    lines.append(_box_line(f"Updated: {ts.strftime('%Y-%m-%d %H:%M:%S UTC')}"))
    lines.append(_divider())

    # Portfolio row
    pv_str = f"${pv:,.2f} ({_sign(total_pnl_pct)}{total_pnl_pct:.2f}%)"
    cash_str = f"${cash:,.2f}"
    lines.append(_box_line(f"Portfolio: {pv_str}  |  Cash: {cash_str}"))
    lines.append(_box_line(
        f"Drawdown: {abs(drawdown):.1f}% / {max_dd:.1f}%  |  "
        f"Daily P&L: {daily_loss_str} / {daily_limit_str}"
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
                f"{sym}  {side}  {size:.4f}  @ ${entry:,.0f}  "
                f"P&L: {_sign(upnl)}${abs(upnl):,.2f} ({_sign(upnl_pct)}{upnl_pct:.1f}%)"
            )
            lines.append(_box_line(row))
    else:
        lines.append(_box_line("  (no open positions)"))

    lines.append(_divider())

    # Trades today
    win_rate_str = f"{win_rate:.1f}%" if trades_today > 0 else "N/A"
    lines.append(_box_line(
        f"TODAY'S TRADES: {trades_today} ({wins}W/{losses}L)  |  Win Rate: {win_rate_str}"
    ))

    if last_signal:
        sig_sym = last_signal.get("symbol", "")
        sig_dir = last_signal.get("direction", "")
        sig_time = last_signal.get("time", "")
        sig_conv = last_signal.get("conviction", 0.0)
        lines.append(_box_line(
            f"Last Signal: {sig_sym} {sig_dir} @ {sig_time}  (conviction: {sig_conv:.2f})"
        ))
    else:
        lines.append(_box_line("Last Signal: none yet"))

    lines.append(_divider())
    lines.append(_box_line("AGENT STATUS"))

    tech = agent_scores.get("TechnicalAnalyst", {})
    sent = agent_scores.get("SentimentAnalyst", {})
    fund = agent_scores.get("FundamentalsAnalyst", {})
    news = agent_scores.get("NewsAnalyst", {})

    def _agent_str(label: str, score: dict[str, Any]) -> str:
        if not score:
            return f"{label}: --"
        conv = score.get("conviction", 0.0)
        direction = score.get("direction", "NEUTRAL")
        return f"{label}: {conv:+.2f} {direction}"

    lines.append(_box_line(
        f"{_agent_str('Technical', tech):30s}  |  {_agent_str('Sentiment', sent)}"
    ))
    lines.append(_box_line(
        f"{_agent_str('Fundamentals', fund):30s}  |  {_agent_str('News', news)}"
    ))

    debate_str = "SKIPPED (strong consensus)" if debate_skipped else "RAN"
    lines.append(_box_line(
        f"Risk Score: {risk_score:.0f}/10  |  Debate: {debate_str}"
    ))

    lines.append(f"╚{'═' * (_BOX_WIDTH + 4)}╝")

    return "\n".join(lines)


def _clear_terminal() -> None:
    """Clear the terminal screen using ANSI escape codes.

    On Windows the raw ANSI write can raise [Errno 22] Invalid argument
    when stdout is not a true VT100 terminal (e.g. redirected to a file or
    a legacy console).  We catch OSError and fall back to a no-op so the
    dashboard still prints without crashing.
    """
    try:
        # ANSI: move cursor to top-left, then clear screen
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()
    except OSError:
        # Non-ANSI terminal or redirected stdout — skip the clear
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  State collection from database
# ─────────────────────────────────────────────────────────────────────────────


def _load_state_from_db(start_value: float) -> dict[str, Any]:
    """
    Query the database for the current portfolio state, today's trades,
    and the most recent signal.

    Returns a state dict ready to pass to ``_render_dashboard``.
    """
    today = datetime.date.today()
    now = datetime.datetime.now(datetime.UTC)

    with get_session() as session:
        # Latest portfolio snapshot
        snapshot = (
            session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.timestamp.desc())
            .first()
        )

        # Today's P&L record
        daily = session.query(DailyPnL).filter(DailyPnL.date == today).first()

        # Today's closed trades for win/loss count
        today_start = datetime.datetime.combine(today, datetime.time.min)
        closed_trades = (
            session.query(Trade)
            .filter(
                Trade.mode == "paper",
                Trade.closed_at >= today_start,
                Trade.pnl.isnot(None),
            )
            .all()
        )

        # Most recent signal
        last_signal_row = (
            session.query(Signal)
            .order_by(Signal.timestamp.desc())
            .first()
        )

        # Open positions from latest snapshot
        positions: list[dict[str, Any]] = []
        if snapshot and snapshot.positions_json:
            positions = list(snapshot.positions_json)

        # Extract values while session is still open
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
                "time": last_signal_row.timestamp.strftime("%H:%M") if last_signal_row.timestamp else "?",
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
        "agent_scores": {},       # populated by orchestrator callbacks in a full run
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
    """
    Background coroutine that refreshes the terminal dashboard every
    ``_DASHBOARD_INTERVAL_S`` seconds until ``shutdown_event`` is set.
    """
    while not shutdown_event.is_set():
        try:
            state = _load_state_from_db(start_value)
            _clear_terminal()
            print(_render_dashboard(state))
        except Exception as exc:  # noqa: BLE001
            logger.error("Dashboard refresh error: %s", exc)

        try:
            await asyncio.wait_for(
                asyncio.shield(shutdown_event.wait()),
                timeout=float(_DASHBOARD_INTERVAL_S),
            )
        except asyncio.TimeoutError:
            pass  # Normal — interval elapsed, refresh again


# ─────────────────────────────────────────────────────────────────────────────
#  Final portfolio summary (printed on shutdown)
# ─────────────────────────────────────────────────────────────────────────────


def _print_final_summary(start_value: float) -> None:
    """Query the database and print a final portfolio summary to stdout."""
    try:
        state = _load_state_from_db(start_value)
    except Exception as exc:  # noqa: BLE001
        print(f"\nCould not load final summary: {exc}")
        return

    pv = state["portfolio_value"]
    total_pnl = pv - start_value
    total_pnl_pct = (total_pnl / start_value * 100.0) if start_value else 0.0
    sign = _sign(total_pnl)

    print("\n" + "=" * 66)
    print("  ATLAS PAPER TRADING — SESSION SUMMARY")
    print("=" * 66)
    print(f"  Start Value   : ${start_value:,.2f}")
    print(f"  Final Value   : ${pv:,.2f}")
    print(f"  Total P&L     : {sign}${abs(total_pnl):,.2f}  ({sign}{total_pnl_pct:.2f}%)")
    print(f"  Trades Today  : {state['trades_today']}  ({state['wins_today']}W / {state['losses_today']}L)")
    print(f"  Max Drawdown  : {abs(state['drawdown_pct']):.2f}%")
    print("=" * 66)


# ─────────────────────────────────────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────────────────────────────────────


async def main() -> None:
    """
    Initialise the database, start the trading engine in PAPER mode, and
    run the dashboard refresh loop concurrently.

    Gracefully shuts down on Ctrl+C (SIGINT) or SIGTERM.
    """
    # Safety gate: refuse to start if live trading flags are set
    if not settings.exchange.paper_trade:
        print(
            "ERROR: PAPER_TRADE=false is set in your .env file.\n"
            "paper_trade.py only runs in paper mode.\n"
            "Use: python main.py live --strategy all --confirm-live  for live trading.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Initialising Atlas Paper Trading Agent...")

    # Initialise database (creates tables if they do not exist yet)
    init_db()

    # Determine the starting portfolio value from the DB (or default)
    with get_session() as session:
        latest = (
            session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.timestamp.desc())
            .first()
        )
        # Read the scalar value inside the session scope — once session.close()
        # is called the ORM object is detached and attribute access raises
        # DetachedInstanceError.
        start_value: float = latest.total_value if latest else 10_000.0
        # Ensure the value is a plain Python float, not a SQLAlchemy-tracked attr
        start_value = float(start_value)

    shutdown_event = asyncio.Event()

    # Windows-compatible signal handling
    def _handle_signal(signum: int, frame: object) -> None:
        logger.info("Signal %d received — initiating shutdown.", signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    print(f"Paper trading started. Starting equity: ${start_value:,.2f}")
    print("Press Ctrl+C to stop.\n")

    # Import and start the trading engine
    from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

    engine = TradingEngine(
        mode=TradingMode.PAPER,
        strategy_names=["all"],
        exchange_id=settings.exchange.default_exchange,
    )

    async with AlertSender() as alert:
        await alert.send_info(
            f"Atlas Paper Trading started. "
            f"Equity: ${start_value:,.2f} | "
            f"Exchange: {settings.exchange.default_exchange}"
        )

        # Run the engine and dashboard concurrently
        engine_task = asyncio.create_task(engine.start(), name="trading-engine")
        dashboard_task = asyncio.create_task(
            _dashboard_loop(shutdown_event, start_value),
            name="dashboard",
        )

        # Wait for shutdown signal
        await shutdown_event.wait()

        # Graceful teardown
        engine_task.cancel()
        dashboard_task.cancel()

        for task in (engine_task, dashboard_task):
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as exc:  # noqa: BLE001
                logger.error("Task teardown error: %s", exc)

        # Send shutdown alert before closing the AlertSender context
        await alert.send_info("Atlas Paper Trading stopped.")

    # Print final summary after alerts are flushed
    _print_final_summary(start_value)


if __name__ == "__main__":
    # On Windows, use the Selector event loop (Proactor breaks some async libs)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
