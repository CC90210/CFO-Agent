"""
dashboard.py
------------
Standalone P&L visualisation dashboard for the ATLAS trading agent.

Reads live portfolio data from the SQLAlchemy database and (optionally)
backtest results from the logs/ CSV files, then generates a single
self-contained HTML file at logs/dashboard.html using Plotly.

Usage
-----
    # Paper-trading view (reads DB)
    python dashboard.py

    # Backtest view (reads logs/*.csv files)
    python dashboard.py --backtest

    # Suppress auto-open
    python dashboard.py --no-open
"""

from __future__ import annotations

import argparse
import csv
import datetime
import logging
import math
import statistics
import sys
import webbrowser
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
#  Path setup — must happen before project imports
# ─────────────────────────────────────────────────────────────────────────────

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ─────────────────────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger("atlas.dashboard")

# ─────────────────────────────────────────────────────────────────────────────
#  Plotly — imported with a clear error message if missing
# ─────────────────────────────────────────────────────────────────────────────

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError as exc:
    print(
        "ERROR: plotly is not installed.\n"
        "Run:  pip install 'plotly>=5.18.0'\n"
        f"Details: {exc}",
        file=sys.stderr,
    )
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports
# ─────────────────────────────────────────────────────────────────────────────

from db.database import get_session, init_db  # noqa: E402
from db.models import DailyPnL, PortfolioSnapshot, Signal, Trade  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_LOGS_DIR = _ROOT / "logs"
_OUTPUT_PATH = _LOGS_DIR / "dashboard.html"
_DARK_TEMPLATE = "plotly_dark"
_GREEN = "#00d084"
_RED = "#ff4757"
_BLUE = "#1e90ff"
_GOLD = "#ffd700"
_GREY = "#8a95a3"


# ─────────────────────────────────────────────────────────────────────────────
#  Data layer — paper-trading mode (reads SQLite DB)
# ─────────────────────────────────────────────────────────────────────────────


def _load_paper_data() -> dict[str, Any]:
    """
    Query all paper-trading data from the database.

    Returns a dict with keys:
        trades         – list of closed Trade ORM objects (detached)
        snapshots      – list of PortfolioSnapshot dicts
        daily_pnl      – list of DailyPnL dicts
        signals        – list of Signal dicts (light subset)
        start_value    – float, first snapshot total_value
    """
    init_db()

    trades_data: list[dict[str, Any]] = []
    snapshots_data: list[dict[str, Any]] = []
    daily_data: list[dict[str, Any]] = []
    signals_data: list[dict[str, Any]] = []
    start_value = 10_000.0

    with get_session() as session:
        # ── Closed trades ──────────────────────────────────────────────────
        trades = (
            session.query(Trade)
            .filter(Trade.pnl.isnot(None), Trade.closed_at.isnot(None))
            .order_by(Trade.closed_at.desc())
            .all()
        )
        for t in trades:
            duration_secs: float | None = None
            if t.closed_at and t.opened_at:
                duration_secs = (t.closed_at - t.opened_at).total_seconds()
            trades_data.append(
                {
                    "id": t.id,
                    "symbol": t.symbol,
                    "strategy": t.strategy,
                    "side": t.side,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl": t.pnl or 0.0,
                    "pnl_pct": (t.pnl_pct or 0.0) * 100.0
                    if abs(t.pnl_pct or 0.0) <= 1.0
                    else (t.pnl_pct or 0.0),
                    "fees": t.fees or 0.0,
                    "duration_secs": duration_secs,
                    "opened_at": t.opened_at,
                    "closed_at": t.closed_at,
                    "mode": t.mode,
                    # exit_reason not on paper Trade model — leave blank
                    "exit_reason": "",
                }
            )

        # ── Portfolio snapshots ────────────────────────────────────────────
        snapshots = (
            session.query(PortfolioSnapshot)
            .order_by(PortfolioSnapshot.timestamp.asc())
            .all()
        )
        for s in snapshots:
            snapshots_data.append(
                {
                    "timestamp": s.timestamp,
                    "total_value": s.total_value,
                    "available_balance": s.available_balance,
                    "unrealized_pnl": s.unrealized_pnl,
                    "drawdown_pct": s.drawdown_pct,
                    "mode": s.mode,
                }
            )
        if snapshots_data:
            start_value = snapshots_data[0]["total_value"]

        # ── Daily P&L ──────────────────────────────────────────────────────
        daily_rows = (
            session.query(DailyPnL).order_by(DailyPnL.date.asc()).all()
        )
        for d in daily_rows:
            daily_data.append(
                {
                    "date": d.date,
                    "realized_pnl": d.realized_pnl,
                    "trades_count": d.trades_count,
                    "wins": d.wins,
                    "losses": d.losses,
                    "max_drawdown": d.max_drawdown,
                    "daily_limit_hit": d.daily_limit_hit,
                }
            )

        # ── Signals (light subset) ─────────────────────────────────────────
        signals = (
            session.query(Signal).order_by(Signal.timestamp.asc()).all()
        )
        for sig in signals:
            signals_data.append(
                {
                    "symbol": sig.symbol,
                    "direction": sig.direction,
                    "conviction": sig.conviction,
                    "strategy": sig.strategy,
                    "executed": sig.executed,
                    "timestamp": sig.timestamp,
                    "trade_id": sig.trade_id,
                }
            )

    return {
        "trades": trades_data,
        "snapshots": snapshots_data,
        "daily_pnl": daily_data,
        "signals": signals_data,
        "start_value": start_value,
        "source": "paper",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Data layer — backtest mode (reads logs/*.csv)
# ─────────────────────────────────────────────────────────────────────────────


def _load_backtest_data() -> dict[str, Any]:
    """
    Load backtest trade logs from all trades_*.csv files in logs/.

    Returns the same shape dict as _load_paper_data() so the chart
    functions work identically for both modes.
    """
    trades_data: list[dict[str, Any]] = []

    csv_files = sorted(_LOGS_DIR.glob("trades_*.csv"))
    if not csv_files:
        return {
            "trades": [],
            "snapshots": [],
            "daily_pnl": [],
            "signals": [],
            "start_value": 10_000.0,
            "source": "backtest",
        }

    for csv_path in csv_files:
        try:
            with csv_path.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    try:
                        pnl_pct_raw = float(row.get("pnl_pct", 0.0))
                        # CSV stores pnl_pct as fractional (e.g. 0.015 = 1.5%)
                        pnl_pct = (
                            pnl_pct_raw * 100.0
                            if abs(pnl_pct_raw) < 1.0
                            else pnl_pct_raw
                        )
                        trades_data.append(
                            {
                                "id": int(row.get("trade_id", 0)),
                                "symbol": row.get("symbol", ""),
                                "strategy": row.get("strategy", ""),
                                "side": row.get("side", ""),
                                "entry_price": float(row.get("entry_price", 0.0)),
                                "exit_price": float(row.get("exit_price", 0.0)),
                                "pnl": float(row.get("net_pnl", 0.0)),
                                "pnl_pct": pnl_pct,
                                "fees": float(row.get("commission_paid", 0.0)),
                                "duration_secs": float(
                                    row.get("duration_seconds", 0.0)
                                ),
                                "opened_at": _parse_dt(row.get("entry_time")),
                                "closed_at": _parse_dt(row.get("exit_time")),
                                "exit_reason": row.get("exit_reason", ""),
                                "mode": "backtest",
                            }
                        )
                    except (ValueError, KeyError):
                        continue
        except OSError:
            continue

    # Sort by closed_at descending (most recent first — matches paper mode)
    trades_data.sort(
        key=lambda t: t["closed_at"] or datetime.datetime.min, reverse=True
    )

    # Derive daily_pnl from trades (backtest has no DailyPnL table rows)
    daily_map: dict[datetime.date, dict[str, Any]] = {}
    for t in trades_data:
        dt = t["closed_at"]
        if dt is None:
            continue
        day = dt.date() if isinstance(dt, datetime.datetime) else dt
        if day not in daily_map:
            daily_map[day] = {
                "date": day,
                "realized_pnl": 0.0,
                "trades_count": 0,
                "wins": 0,
                "losses": 0,
                "max_drawdown": 0.0,
                "daily_limit_hit": False,
            }
        daily_map[day]["realized_pnl"] += t["pnl"]
        daily_map[day]["trades_count"] += 1
        if t["pnl"] > 0:
            daily_map[day]["wins"] += 1
        else:
            daily_map[day]["losses"] += 1

    daily_data = sorted(daily_map.values(), key=lambda d: d["date"])

    return {
        "trades": trades_data,
        "snapshots": [],   # not available for backtests
        "daily_pnl": daily_data,
        "signals": [],     # not available for backtests
        "start_value": 10_000.0,
        "source": "backtest",
    }


def _parse_dt(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return datetime.datetime.strptime(value[:25], fmt[:len(value[:25])])
        except ValueError:
            continue
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Analytics helpers
# ─────────────────────────────────────────────────────────────────────────────


def _compute_summary_stats(
    trades: list[dict[str, Any]],
    snapshots: list[dict[str, Any]],
    start_value: float,
) -> dict[str, Any]:
    """Compute the header KPI values."""
    if not trades:
        return {
            "total_pnl": 0.0,
            "total_pnl_pct": 0.0,
            "win_rate": 0.0,
            "total_trades": 0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "max_drawdown": 0.0,
            "sharpe": None,
            "profit_factor": None,
            "current_equity": start_value,
        }

    pnls = [t["pnl"] for t in trades]
    total_pnl = sum(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    win_rate = len(wins) / len(pnls) * 100.0 if pnls else 0.0

    gross_profit = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None

    # Max drawdown — prefer snapshot data, fall back to equity-curve reconstruction
    max_dd = 0.0
    if snapshots:
        dd_values = [abs(s["drawdown_pct"]) for s in snapshots]
        max_dd = max(dd_values) if dd_values else 0.0
    else:
        # Reconstruct from cumulative PnL (ascending time order)
        sorted_trades = sorted(
            trades, key=lambda t: t["closed_at"] or datetime.datetime.min
        )
        equity = start_value
        peak = start_value
        for t in sorted_trades:
            equity += t["pnl"]
            peak = max(peak, equity)
            dd = (equity - peak) / peak * 100.0
            max_dd = max(max_dd, abs(dd))

    current_equity = (
        snapshots[-1]["total_value"] if snapshots else start_value + total_pnl
    )

    # Sharpe — annualised, using daily PnL returns if we have enough data
    sharpe: float | None = None
    if len(pnls) >= 10:
        try:
            mean_ret = statistics.mean(pnls) / start_value
            std_ret = statistics.stdev(pnls) / start_value
            if std_ret > 0:
                # Scale to annualised assuming ~252 trades per year equivalent
                sharpe = round((mean_ret / std_ret) * math.sqrt(252), 3)
        except statistics.StatisticsError:
            pass

    return {
        "total_pnl": total_pnl,
        "total_pnl_pct": (current_equity - start_value) / start_value * 100.0,
        "win_rate": win_rate,
        "total_trades": len(trades),
        "best_trade": max(pnls),
        "worst_trade": min(pnls),
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "profit_factor": profit_factor,
        "current_equity": current_equity,
    }


def _compute_strategy_stats(
    trades: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Aggregate per-strategy performance metrics."""
    groups: dict[str, list[float]] = {}
    for t in trades:
        strat = t["strategy"] or "unknown"
        groups.setdefault(strat, []).append(t["pnl"])

    result: dict[str, dict[str, Any]] = {}
    for strat, pnls in groups.items():
        wins = [p for p in pnls if p > 0]
        losses_list = [p for p in pnls if p <= 0]
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses_list)) if losses_list else 0.0

        mean_pnl = statistics.mean(pnls) if pnls else 0.0
        std_pnl = statistics.stdev(pnls) if len(pnls) >= 2 else 0.0
        sharpe: float | None = None
        if std_pnl > 0:
            sharpe = round(mean_pnl / std_pnl * math.sqrt(252), 3)

        result[strat] = {
            "total_pnl": sum(pnls),
            "trade_count": len(pnls),
            "win_rate": len(wins) / len(pnls) * 100.0 if pnls else 0.0,
            "avg_pnl": mean_pnl,
            "profit_factor": gross_profit / gross_loss if gross_loss > 0 else None,
            "sharpe": sharpe,
        }
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Chart builders
# ─────────────────────────────────────────────────────────────────────────────


def _chart_equity_and_drawdown(
    snapshots: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    start_value: float,
) -> go.Figure:
    """Section 1 — Equity curve with drawdown subplot."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.04,
        subplot_titles=("Portfolio Equity Curve", "Drawdown (%)"),
    )

    if snapshots:
        times = [s["timestamp"] for s in snapshots]
        values = [s["total_value"] for s in snapshots]
        drawdowns = [s["drawdown_pct"] for s in snapshots]

        fig.add_trace(
            go.Scatter(
                x=times,
                y=values,
                mode="lines",
                name="Equity",
                line={"color": _BLUE, "width": 2},
                fill="tozeroy",
                fillcolor="rgba(30,144,255,0.08)",
            ),
            row=1, col=1,
        )
        # Starting capital reference line
        fig.add_hline(
            y=start_value,
            line_dash="dash",
            line_color=_GREY,
            annotation_text=f"Start ${start_value:,.0f}",
            annotation_position="bottom right",
            row=1, col=1,  # type: ignore[call-arg]
        )
        fig.add_trace(
            go.Scatter(
                x=times,
                y=drawdowns,
                mode="lines",
                name="Drawdown %",
                line={"color": _RED, "width": 1.5},
                fill="tozeroy",
                fillcolor="rgba(255,71,87,0.15)",
            ),
            row=2, col=1,
        )
    elif trades:
        # No snapshots — reconstruct equity from trades
        sorted_trades = sorted(
            trades, key=lambda t: t["closed_at"] or datetime.datetime.min
        )
        equity = start_value
        peak = start_value
        eq_times = [sorted_trades[0]["opened_at"] or sorted_trades[0]["closed_at"]]
        eq_values = [start_value]
        dd_values = [0.0]

        for t in sorted_trades:
            equity += t["pnl"]
            peak = max(peak, equity)
            dd = (equity - peak) / peak * 100.0
            eq_times.append(t["closed_at"])
            eq_values.append(equity)
            dd_values.append(dd)

        fig.add_trace(
            go.Scatter(
                x=eq_times,
                y=eq_values,
                mode="lines",
                name="Equity (reconstructed)",
                line={"color": _BLUE, "width": 2},
                fill="tozeroy",
                fillcolor="rgba(30,144,255,0.08)",
            ),
            row=1, col=1,
        )
        fig.add_hline(
            y=start_value,
            line_dash="dash",
            line_color=_GREY,
            annotation_text=f"Start ${start_value:,.0f}",
            annotation_position="bottom right",
            row=1, col=1,  # type: ignore[call-arg]
        )
        fig.add_trace(
            go.Scatter(
                x=eq_times,
                y=dd_values,
                mode="lines",
                name="Drawdown %",
                line={"color": _RED, "width": 1.5},
                fill="tozeroy",
                fillcolor="rgba(255,71,87,0.15)",
            ),
            row=2, col=1,
        )
    else:
        fig.add_annotation(
            text="No equity data available yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )

    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=520,
        showlegend=True,
        margin={"t": 50, "b": 20, "l": 60, "r": 20},
    )
    fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown %", row=2, col=1)
    return fig


def _chart_trade_table(trades: list[dict[str, Any]]) -> go.Figure:
    """Section 2 — Trade-by-trade table, colour-coded by PnL."""
    if not trades:
        fig = go.Figure()
        fig.add_annotation(
            text="No closed trades recorded yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )
        fig.update_layout(template=_DARK_TEMPLATE, height=300)
        return fig

    def _fmt_dur(secs: float | None) -> str:
        if secs is None:
            return "—"
        h = int(secs // 3600)
        m = int((secs % 3600) // 60)
        return f"{h}h {m}m"

    def _fmt_dt(dt: datetime.datetime | None) -> str:
        if dt is None:
            return "—"
        return dt.strftime("%Y-%m-%d %H:%M")

    rows = trades[:200]  # cap at 200 rows for performance

    symbols = [t["symbol"] for t in rows]
    strategies = [t["strategy"] for t in rows]
    sides = [t["side"].upper() for t in rows]
    entries = [f"${t['entry_price']:,.4f}" if t["entry_price"] < 1 else f"${t['entry_price']:,.2f}" for t in rows]
    exits = [f"${t['exit_price']:,.4f}" if (t["exit_price"] or 0) < 1 else f"${t['exit_price']:,.2f}" if t["exit_price"] else "—" for t in rows]
    pnls = [f"${t['pnl']:+,.2f}" for t in rows]
    pnl_pcts = [f"{t['pnl_pct']:+.2f}%" for t in rows]
    durations = [_fmt_dur(t["duration_secs"]) for t in rows]
    closed_ats = [_fmt_dt(t["closed_at"]) for t in rows]
    exit_reasons = [t["exit_reason"] or "—" for t in rows]

    # Row colours: green tint for wins, red tint for losses
    cell_colours: list[list[str]] = []
    row_colours = [
        "rgba(0,208,132,0.12)" if t["pnl"] > 0 else "rgba(255,71,87,0.12)"
        for t in rows
    ]
    # Each column needs its own colour list
    num_cols = 9
    for _ in range(num_cols):
        cell_colours.append(row_colours)

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "<b>Symbol</b>", "<b>Strategy</b>", "<b>Side</b>",
                        "<b>Entry</b>", "<b>Exit</b>",
                        "<b>P&amp;L ($)</b>", "<b>P&amp;L (%)</b>",
                        "<b>Duration</b>", "<b>Closed At</b>",
                    ],
                    fill_color="#1e2430",
                    font={"color": "white", "size": 12},
                    align="left",
                    height=32,
                ),
                cells=dict(
                    values=[
                        symbols, strategies, sides,
                        entries, exits,
                        pnls, pnl_pcts,
                        durations, closed_ats,
                    ],
                    fill_color=cell_colours,
                    font={"color": "white", "size": 11},
                    align="left",
                    height=26,
                ),
            )
        ]
    )
    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=max(350, min(800, 60 + len(rows) * 26)),
        margin={"t": 10, "b": 10, "l": 0, "r": 0},
    )
    return fig


def _chart_strategy_comparison(
    strategy_stats: dict[str, dict[str, Any]],
) -> go.Figure:
    """Section 3 — Grouped bar chart, strategy comparison."""
    if not strategy_stats:
        fig = go.Figure()
        fig.add_annotation(
            text="No strategy data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )
        fig.update_layout(template=_DARK_TEMPLATE, height=350)
        return fig

    strategies = list(strategy_stats.keys())
    total_pnls = [strategy_stats[s]["total_pnl"] for s in strategies]
    win_rates = [strategy_stats[s]["win_rate"] for s in strategies]
    trade_counts = [strategy_stats[s]["trade_count"] for s in strategies]
    avg_pnls = [strategy_stats[s]["avg_pnl"] for s in strategies]

    bar_colours = [_GREEN if p >= 0 else _RED for p in total_pnls]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Total P&L by Strategy ($)",
            "Win Rate by Strategy (%)",
            "Trade Count by Strategy",
            "Avg P&L per Trade ($)",
        ),
        vertical_spacing=0.18,
        horizontal_spacing=0.12,
    )

    fig.add_trace(
        go.Bar(
            x=strategies, y=total_pnls, name="Total P&L",
            marker_color=bar_colours, showlegend=False,
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(
            x=strategies, y=win_rates, name="Win Rate",
            marker_color=_BLUE, showlegend=False,
        ),
        row=1, col=2,
    )
    fig.add_trace(
        go.Bar(
            x=strategies, y=trade_counts, name="Trade Count",
            marker_color=_GOLD, showlegend=False,
        ),
        row=2, col=1,
    )
    avg_colours = [_GREEN if p >= 0 else _RED for p in avg_pnls]
    fig.add_trace(
        go.Bar(
            x=strategies, y=avg_pnls, name="Avg P&L",
            marker_color=avg_colours, showlegend=False,
        ),
        row=2, col=2,
    )

    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=560,
        margin={"t": 60, "b": 40, "l": 60, "r": 20},
    )
    return fig


def _chart_daily_pnl_waterfall(
    daily_pnl: list[dict[str, Any]],
) -> go.Figure:
    """Section 4 — Daily P&L bars with cumulative overlay."""
    if not daily_pnl:
        fig = go.Figure()
        fig.add_annotation(
            text="No daily P&L data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )
        fig.update_layout(template=_DARK_TEMPLATE, height=350)
        return fig

    dates = [str(d["date"]) for d in daily_pnl]
    pnls = [d["realized_pnl"] for d in daily_pnl]
    bar_colours = [_GREEN if p >= 0 else _RED for p in pnls]

    cumulative = []
    running = 0.0
    for p in pnls:
        running += p
        cumulative.append(running)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=dates, y=pnls,
            name="Daily P&L ($)",
            marker_color=bar_colours,
            opacity=0.85,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=dates, y=cumulative,
            mode="lines+markers",
            name="Cumulative P&L ($)",
            line={"color": _BLUE, "width": 2},
            marker={"size": 4},
        ),
        secondary_y=True,
    )

    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=380,
        margin={"t": 30, "b": 40, "l": 60, "r": 60},
    )
    fig.update_yaxes(title_text="Daily P&L ($)", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative P&L ($)", secondary_y=True)
    return fig


def _chart_pnl_distribution(trades: list[dict[str, Any]]) -> go.Figure:
    """Section 5 — Histogram of P&L percentages, wins vs losses."""
    if not trades:
        fig = go.Figure()
        fig.add_annotation(
            text="No trade data for distribution",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )
        fig.update_layout(template=_DARK_TEMPLATE, height=350)
        return fig

    all_pcts = [t["pnl_pct"] for t in trades]
    win_pcts = [p for p in all_pcts if p > 0]
    loss_pcts = [p for p in all_pcts if p <= 0]

    fig = go.Figure()

    if win_pcts:
        fig.add_trace(
            go.Histogram(
                x=win_pcts,
                name="Wins",
                marker_color=_GREEN,
                opacity=0.75,
                xbins={"size": 0.5},
            )
        )
    if loss_pcts:
        fig.add_trace(
            go.Histogram(
                x=loss_pcts,
                name="Losses",
                marker_color=_RED,
                opacity=0.75,
                xbins={"size": 0.5},
            )
        )

    # Mean and median vertical lines
    if all_pcts:
        mean_pct = statistics.mean(all_pcts)
        median_pct = statistics.median(all_pcts)
        fig.add_vline(
            x=mean_pct, line_dash="dash", line_color=_GOLD,
            annotation_text=f"Mean {mean_pct:+.2f}%",
            annotation_position="top right",
        )
        fig.add_vline(
            x=median_pct, line_dash="dot", line_color=_GREY,
            annotation_text=f"Median {median_pct:+.2f}%",
            annotation_position="top left",
        )

    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=380,
        barmode="overlay",
        xaxis_title="P&L (%)",
        yaxis_title="Trade Count",
        legend={"orientation": "h", "y": 1.1},
        margin={"t": 30, "b": 50, "l": 60, "r": 20},
    )
    return fig


def _chart_signal_funnel(
    signals: list[dict[str, Any]],
    trades: list[dict[str, Any]],
) -> go.Figure:
    """Section 6 — Signal conversion funnel."""
    total_signals = len(signals)
    executed_signals = sum(1 for s in signals if s["executed"])
    profitable_trades = sum(1 for t in trades if t["pnl"] > 0)

    if total_signals == 0 and len(trades) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No signal data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )
        fig.update_layout(template=_DARK_TEMPLATE, height=350)
        return fig

    # Use trade count as proxy when signals table is empty (backtest mode)
    if total_signals == 0:
        total_signals = len(trades)
        executed_signals = len(trades)

    labels = ["Signals Generated", "Signals Executed", "Profitable Trades"]
    values = [total_signals, executed_signals, profitable_trades]
    colours = [_BLUE, _GOLD, _GREEN]

    fig = go.Figure(
        go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            marker={"color": colours},
            connector={"line": {"color": _GREY, "width": 2}},
        )
    )
    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=350,
        margin={"t": 20, "b": 20, "l": 20, "r": 20},
    )
    return fig


def _chart_drawdown_underwater(
    snapshots: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    start_value: float,
) -> go.Figure:
    """Section 7 — Underwater equity (drawdown over time)."""
    fig = go.Figure()

    if snapshots:
        times = [s["timestamp"] for s in snapshots]
        drawdowns = [s["drawdown_pct"] for s in snapshots]
    elif trades:
        sorted_trades = sorted(
            trades, key=lambda t: t["closed_at"] or datetime.datetime.min
        )
        equity = start_value
        peak = start_value
        times = []
        drawdowns = []
        for t in sorted_trades:
            equity += t["pnl"]
            peak = max(peak, equity)
            dd = (equity - peak) / peak * 100.0
            times.append(t["closed_at"])
            drawdowns.append(dd)
    else:
        fig.add_annotation(
            text="No drawdown data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font={"size": 16, "color": _GREY},
        )
        fig.update_layout(template=_DARK_TEMPLATE, height=300)
        return fig

    fig.add_trace(
        go.Scatter(
            x=times,
            y=drawdowns,
            mode="lines",
            name="Drawdown %",
            line={"color": _RED, "width": 2},
            fill="tozeroy",
            fillcolor="rgba(255,71,87,0.2)",
        )
    )
    fig.add_hline(y=0, line_color=_GREY, line_width=1)
    # Risk limit reference lines
    fig.add_hline(
        y=-5.0, line_dash="dash", line_color=_GOLD,
        annotation_text="Daily limit −5%",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=-15.0, line_dash="dash", line_color=_RED,
        annotation_text="Kill switch −15%",
        annotation_position="bottom right",
    )

    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=340,
        yaxis_title="Drawdown (%)",
        margin={"t": 20, "b": 50, "l": 60, "r": 20},
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  Summary stats header HTML
# ─────────────────────────────────────────────────────────────────────────────


def _build_header_html(
    stats: dict[str, Any],
    source: str,
    generated_at: datetime.datetime,
) -> str:
    """Return an HTML snippet with the KPI header cards."""

    def _kpi(label: str, value: str, colour: str = "white") -> str:
        return (
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{colour}">{value}</div>'
            f"</div>"
        )

    pnl = stats["total_pnl"]
    pnl_pct = stats["total_pnl_pct"]
    pnl_colour = _GREEN if pnl >= 0 else _RED
    pnl_sign = "+" if pnl >= 0 else ""

    wr_colour = _GREEN if stats["win_rate"] >= 50 else _RED

    sharpe_str = f"{stats['sharpe']:.3f}" if stats["sharpe"] is not None else "N/A"
    pf_str = f"{stats['profit_factor']:.2f}" if stats["profit_factor"] is not None else "N/A"

    best = stats["best_trade"]
    worst = stats["worst_trade"]

    source_label = "PAPER TRADING" if source == "paper" else "BACKTEST"
    ts_str = generated_at.strftime("%Y-%m-%d %H:%M:%S UTC")

    cards = "".join([
        _kpi("Total P&L ($)", f"{pnl_sign}${abs(pnl):,.2f}", pnl_colour),
        _kpi("Total P&L (%)", f"{pnl_sign}{pnl_pct:.2f}%", pnl_colour),
        _kpi("Win Rate", f"{stats['win_rate']:.1f}%", wr_colour),
        _kpi("Total Trades", str(stats["total_trades"])),
        _kpi("Best Trade", f"+${best:,.2f}", _GREEN),
        _kpi("Worst Trade", f"-${abs(worst):,.2f}", _RED),
        _kpi("Max Drawdown", f"-{stats['max_drawdown']:.2f}%", _RED),
        _kpi("Sharpe Ratio", sharpe_str, _GOLD if stats["sharpe"] and stats["sharpe"] > 1 else "white"),
        _kpi("Profit Factor", pf_str, _GOLD if stats["profit_factor"] and stats["profit_factor"] > 1 else "white"),
    ])

    return f"""
    <div class="header-bar">
        <div class="title-block">
            <span class="atlas-title">ATLAS</span>
            <span class="dashboard-subtitle">Portfolio Performance Dashboard</span>
            <span class="source-badge">{source_label}</span>
        </div>
        <div class="ts-block">Generated: {ts_str}</div>
    </div>
    <div class="kpi-row">{cards}</div>
    """


# ─────────────────────────────────────────────────────────────────────────────
#  HTML assembly
# ─────────────────────────────────────────────────────────────────────────────


def _section(title: str, fig: go.Figure) -> str:
    """Return an HTML section string with a heading and embedded Plotly chart."""
    return (
        f'<div class="section">'
        f'<h2 class="section-title">{title}</h2>'
        f"{fig.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': True, 'displaylogo': False})}"
        f"</div>"
    )


_CSS = """
<style>
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --muted: #8b949e;
    --green: #00d084;
    --red: #ff4757;
    --blue: #1e90ff;
    --gold: #ffd700;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 14px;
    line-height: 1.5;
  }
  .page-wrapper { max-width: 1400px; margin: 0 auto; padding: 24px 20px 60px; }

  /* Header */
  .header-bar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
  }
  .title-block { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
  .atlas-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    background: linear-gradient(135deg, var(--blue), var(--gold));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .dashboard-subtitle { font-size: 1rem; color: var(--muted); }
  .source-badge {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--gold);
  }
  .ts-block { font-size: 0.78rem; color: var(--muted); text-align: right; }

  /* KPI cards */
  .kpi-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 28px;
  }
  .kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 18px;
    min-width: 120px;
    flex: 1 1 120px;
  }
  .kpi-label { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
  .kpi-value { font-size: 1.35rem; font-weight: 700; margin-top: 4px; }

  /* Sections */
  .section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 24px;
  }
  .section-title {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
  }

  /* Empty state */
  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
    font-size: 1.1rem;
  }
  .empty-state strong { display: block; font-size: 1.4rem; color: var(--text); margin-bottom: 8px; }

  /* Responsive */
  @media (max-width: 768px) {
    .kpi-card { flex: 1 1 calc(50% - 6px); }
    .atlas-title { font-size: 1.6rem; }
  }
</style>
"""


def _build_html(
    header_html: str,
    sections: list[tuple[str, go.Figure]],
    has_data: bool,
) -> str:
    """Assemble the full standalone HTML document."""
    # Get Plotly.js CDN script — included once
    plotly_js = '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'

    body_content: str
    if not has_data:
        body_content = (
            '<div class="empty-state">'
            "<strong>No trades recorded yet.</strong>"
            "Paper trading is running — check back after the first trade closes."
            "</div>"
        )
    else:
        body_content = "".join(_section(title, fig) for title, fig in sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ATLAS — Portfolio Performance Dashboard</title>
  {plotly_js}
  {_CSS}
</head>
<body>
  <div class="page-wrapper">
    {header_html}
    {body_content}
  </div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────────────────────────────────────


def build_dashboard(use_backtest: bool = False, auto_open: bool = True) -> Path:
    """
    Build the dashboard HTML file and return its path.

    Parameters
    ----------
    use_backtest : bool
        If True, load from logs/*.csv instead of the SQLite database.
    auto_open : bool
        If True, open the generated file in the default browser.
    """
    generated_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    # ── Load data ─────────────────────────────────────────────────────────
    if use_backtest:
        print("Loading backtest results from logs/ directory...")
        data = _load_backtest_data()
    else:
        print("Loading paper-trading data from database...")
        data = _load_paper_data()

    trades: list[dict[str, Any]] = data["trades"]
    snapshots: list[dict[str, Any]] = data["snapshots"]
    daily_pnl: list[dict[str, Any]] = data["daily_pnl"]
    signals: list[dict[str, Any]] = data["signals"]
    start_value: float = data["start_value"]
    source: str = data["source"]

    has_data = bool(trades or snapshots)

    print(
        f"  Trades: {len(trades)} | Snapshots: {len(snapshots)} | "
        f"Daily rows: {len(daily_pnl)} | Signals: {len(signals)}"
    )

    # ── Analytics ─────────────────────────────────────────────────────────
    stats = _compute_summary_stats(trades, snapshots, start_value)
    strategy_stats = _compute_strategy_stats(trades)

    # ── Charts ────────────────────────────────────────────────────────────
    sections: list[tuple[str, go.Figure]] = []

    if has_data:
        sections = [
            (
                "1. Portfolio Equity Curve & Drawdown",
                _chart_equity_and_drawdown(snapshots, trades, start_value),
            ),
            (
                "2. Trade-by-Trade Breakdown",
                _chart_trade_table(trades),
            ),
            (
                "3. Strategy Performance Comparison",
                _chart_strategy_comparison(strategy_stats),
            ),
            (
                "4. Daily P&L Waterfall",
                _chart_daily_pnl_waterfall(daily_pnl),
            ),
            (
                "5. Win / Loss Distribution",
                _chart_pnl_distribution(trades),
            ),
            (
                "6. Signal Conversion Funnel",
                _chart_signal_funnel(signals, trades),
            ),
            (
                "7. Drawdown Analysis (Underwater Equity)",
                _chart_drawdown_underwater(snapshots, trades, start_value),
            ),
        ]

    # ── Header HTML ───────────────────────────────────────────────────────
    header_html = _build_header_html(stats, source, generated_at)

    # ── Assemble & write ──────────────────────────────────────────────────
    html = _build_html(header_html, sections, has_data)

    _LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _OUTPUT_PATH.write_text(html, encoding="utf-8")

    size_kb = _OUTPUT_PATH.stat().st_size / 1024
    print(f"Dashboard written to: {_OUTPUT_PATH}  ({size_kb:.1f} KB)")

    if auto_open:
        webbrowser.open(_OUTPUT_PATH.as_uri())
        print("Opening in browser...")

    return _OUTPUT_PATH


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ATLAS P&L Dashboard Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python dashboard.py                # paper-trading view\n"
            "  python dashboard.py --backtest     # backtest results view\n"
            "  python dashboard.py --no-open      # generate without opening browser\n"
        ),
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        default=False,
        help="Load backtest results from logs/*.csv instead of the live DB.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        default=False,
        help="Generate the HTML file but do not open it in the browser.",
    )
    args = parser.parse_args()

    output = build_dashboard(
        use_backtest=args.backtest,
        auto_open=not args.no_open,
    )
    print(f"Done. Dashboard: {output}")


if __name__ == "__main__":
    main()
