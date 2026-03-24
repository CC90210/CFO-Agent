"""
visualize_backtest.py — Interactive HTML backtest report generator for Atlas.

Runs a full backtest using BacktestEngine and generates a self-contained
interactive HTML report powered by Plotly.

Usage
-----
    python visualize_backtest.py --strategy donchian_breakout --symbol BTC/USDT --timeframe 4h
    python visualize_backtest.py --strategy smart_money --symbol ETH/USDT --timeframe 4h --capital 50000
    python visualize_backtest.py --strategy donchian_breakout --symbol BTC/USDT --no-open

Report sections
---------------
1. Header stats card — all key performance metrics at a glance
2. Equity curve     — interactive line chart with entry/exit markers and drawdown shading
3. Trade scatter    — each trade as a dot (x=time, y=pnl_pct), colored by win/loss
4. Monthly heatmap  — calendar-style monthly return aggregation (green/red)
5. Duration vs P&L  — scatter: does holding longer pay off?
6. Exit reasons     — pie chart breakdown of stop_loss / take_profit / signal_exit / etc.
7. Cumulative wins vs losses — running streak visualization
8. Rolling Sharpe   — 20-trade rolling Sharpe to surface strategy edge consistency
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import math
import sys
import webbrowser
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Logging — suppress noisy third-party libraries, keep atlas.* visible
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas.visualize")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Plotly import guard
# ---------------------------------------------------------------------------
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.io as pio
except ImportError as _plotly_err:
    print(
        "ERROR: plotly is required. Install with: pip install plotly",
        file=sys.stderr,
    )
    raise SystemExit(1) from _plotly_err

# ---------------------------------------------------------------------------
# Atlas imports (all from existing infrastructure — no new patterns)
# ---------------------------------------------------------------------------
from backtesting.engine import BacktestEngine, BacktestResult, TradeLog
from data.fetcher import MarketDataFetcher
from strategies.base import StrategyRegistry
import strategies.technical  # noqa: F401 — side-effect: registers all strategies

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DARK_TEMPLATE = "plotly_dark"
_DEFAULT_CAPITAL = 10_000.0
_DEFAULT_LIMIT = 2_000
_ROLLING_SHARPE_WINDOW = 20
_ANNUALISATION_FACTOR = 252


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Atlas — Interactive Backtest Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize_backtest.py --strategy donchian_breakout --symbol BTC/USDT
  python visualize_backtest.py --strategy smart_money --symbol ETH/USDT --timeframe 4h
  python visualize_backtest.py --strategy multi_timeframe --symbol XRP/USDT --capital 50000
  python visualize_backtest.py --strategy volume_profile --symbol AVAX/USDT --no-open
        """,
    )
    parser.add_argument(
        "--strategy",
        required=True,
        help="Strategy name as registered in StrategyRegistry (e.g. donchian_breakout)",
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading symbol (e.g. BTC/USDT, ETH/USDT)",
    )
    parser.add_argument(
        "--timeframe",
        default="4h",
        help="OHLCV timeframe (default: 4h)",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=_DEFAULT_CAPITAL,
        help=f"Initial capital in USD (default: {_DEFAULT_CAPITAL:,.0f})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=_DEFAULT_LIMIT,
        help=f"Number of candles to fetch (default: {_DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Write the HTML report but do not open it in the browser",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------


async def _fetch_ohlcv(symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    """Fetch OHLCV data via the existing MarketDataFetcher infrastructure."""
    logger.info("Fetching %d bars of %s/%s from exchange...", limit, symbol, timeframe)
    async with MarketDataFetcher() as fetcher:
        df = await fetcher.fetch_ohlcv(symbol, timeframe, limit=limit)
    logger.info(
        "Fetched %d bars: %s → %s",
        len(df),
        df.index[0].strftime("%Y-%m-%d"),
        df.index[-1].strftime("%Y-%m-%d"),
    )
    return df


# ---------------------------------------------------------------------------
# Rolling Sharpe computation
# ---------------------------------------------------------------------------


def _rolling_sharpe(trades: list[TradeLog], window: int = _ROLLING_SHARPE_WINDOW) -> tuple[list[Any], list[float]]:
    """
    Compute a rolling Sharpe ratio over a sliding window of trades.

    Returns parallel lists of (entry_times, sharpe_values).
    Values are NaN where there are fewer than window trades.
    """
    if len(trades) < window:
        return [], []

    pnl_pcts = [t.pnl_pct for t in trades]
    times = [t.entry_time for t in trades]
    sharpe_values: list[float] = []
    sharpe_times: list[Any] = []

    for i in range(window - 1, len(pnl_pcts)):
        window_returns = pnl_pcts[i - window + 1 : i + 1]
        arr = np.array(window_returns, dtype=float)
        std = float(np.std(arr, ddof=1))
        if std > 0:
            sharpe = float(np.mean(arr) / std * math.sqrt(_ANNUALISATION_FACTOR))
        else:
            sharpe = 0.0
        sharpe_values.append(sharpe)
        sharpe_times.append(times[i])

    return sharpe_times, sharpe_values


# ---------------------------------------------------------------------------
# Monthly returns aggregation
# ---------------------------------------------------------------------------


def _monthly_returns(trades: list[TradeLog]) -> pd.DataFrame:
    """
    Aggregate trade pnl_pct by calendar month.

    Returns a DataFrame with columns [year, month, return_pct]
    suitable for building a heatmap.
    """
    if not trades:
        return pd.DataFrame(columns=["year", "month", "return_pct"])

    records = [
        {"year": t.exit_time.year, "month": t.exit_time.month, "pnl_pct": t.pnl_pct}
        for t in trades
    ]
    df = pd.DataFrame(records)
    monthly = df.groupby(["year", "month"])["pnl_pct"].sum().reset_index()
    monthly.rename(columns={"pnl_pct": "return_pct"}, inplace=True)
    return monthly


# ---------------------------------------------------------------------------
# HTML report generation
# ---------------------------------------------------------------------------

_STAT_CARD_CSS = """
<style>
  body { background: #111; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
  .header { padding: 24px 32px 8px; background: #1a1a2e; border-bottom: 2px solid #2d2d4e; }
  .header h1 { margin: 0 0 4px; font-size: 1.6em; color: #64b5f6; }
  .header p  { margin: 0 0 16px; font-size: 0.9em; color: #888; }
  .stats-grid { display: flex; flex-wrap: wrap; gap: 12px; padding: 16px 32px 24px; background: #1a1a2e; }
  .stat-card {
    background: #16213e;
    border: 1px solid #2d2d4e;
    border-radius: 8px;
    padding: 12px 18px;
    min-width: 130px;
    flex: 1;
  }
  .stat-card .label { font-size: 0.72em; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }
  .stat-card .value { font-size: 1.35em; font-weight: 700; margin-top: 2px; }
  .pos  { color: #66bb6a; }
  .neg  { color: #ef5350; }
  .neu  { color: #90caf9; }
  .warn { color: #ffa726; }
  .charts-wrapper { padding: 8px 0; }
  .no-trades-banner {
    text-align: center;
    padding: 60px;
    font-size: 1.3em;
    color: #ffa726;
    background: #1a1a2e;
    border: 1px dashed #ffa726;
    border-radius: 12px;
    margin: 40px 32px;
  }
</style>
"""


def _colour_class(value: float, positive_is_good: bool = True) -> str:
    """Return a CSS class name based on sign and direction convention."""
    if value > 0:
        return "pos" if positive_is_good else "neg"
    if value < 0:
        return "neg" if positive_is_good else "pos"
    return "neu"


def _stat_card(label: str, value: str, css_class: str = "neu") -> str:
    return (
        f'<div class="stat-card">'
        f'<div class="label">{label}</div>'
        f'<div class="value {css_class}">{value}</div>'
        f"</div>"
    )


def _build_header_html(result: BacktestResult, strategy: str, symbol: str, timeframe: str) -> str:
    """Build the stats card HTML section above the charts."""
    r = result
    period = (
        f"{r.start_date:%Y-%m-%d} → {r.end_date:%Y-%m-%d}"
        if r.start_date and r.end_date
        else "N/A"
    )
    avg_dur_h = r.avg_trade_duration.total_seconds() / 3600.0

    cards = [
        _stat_card("Total Return", f"{r.total_return * 100:+.2f}%", _colour_class(r.total_return)),
        _stat_card("Annualised Return", f"{r.annualized_return * 100:+.2f}%", _colour_class(r.annualized_return)),
        _stat_card("Sharpe Ratio", f"{r.sharpe_ratio:.3f}", _colour_class(r.sharpe_ratio)),
        _stat_card("Sortino Ratio", f"{r.sortino_ratio:.3f}", _colour_class(r.sortino_ratio)),
        _stat_card("Max Drawdown", f"{r.max_drawdown * 100:.2f}%", _colour_class(r.max_drawdown, positive_is_good=False)),
        _stat_card("Win Rate", f"{r.win_rate * 100:.1f}%", "pos" if r.win_rate >= 0.5 else "warn"),
        _stat_card("Profit Factor", f"{r.profit_factor:.3f}" if r.profit_factor < 999 else "∞", _colour_class(r.profit_factor - 1.0)),
        _stat_card("Total Trades", str(r.total_trades), "neu"),
        _stat_card("Winning Trades", str(r.winning_trades), "pos"),
        _stat_card("Losing Trades", str(r.losing_trades), "neg"),
        _stat_card("Avg Win", f"${r.avg_win:,.2f}", "pos"),
        _stat_card("Avg Loss", f"${r.avg_loss:,.2f}", "neg"),
        _stat_card("Expectancy / Trade", f"${r.expectancy:,.2f}", _colour_class(r.expectancy)),
        _stat_card("Avg Trade Duration", f"{avg_dur_h:.1f}h", "neu"),
        _stat_card("Calmar Ratio", f"{r.calmar_ratio:.3f}" if math.isfinite(r.calmar_ratio) else "∞", _colour_class(r.calmar_ratio)),
        _stat_card("Commission", f"{r.commission_pct * 100:.3f}%", "neu"),
    ]

    return f"""
<div class="header">
  <h1>ATLAS Backtest Report &mdash; {strategy} on {symbol}</h1>
  <p>Timeframe: <strong>{timeframe}</strong> &nbsp;|&nbsp; Period: <strong>{period}</strong></p>
</div>
<div class="stats-grid">
  {"".join(cards)}
</div>
"""


def _build_equity_chart(result: BacktestResult) -> go.Figure:
    """
    Equity curve with entry/exit trade markers and drawdown shading.

    The equity curve is the backbone of the report — this chart gets 65% height.
    """
    eq = result.equity_curve
    rolling_max = eq.cummax()
    drawdown = (eq - rolling_max) / rolling_max * 100.0  # as percentage

    # Collect entry and exit points from the trade log
    entry_times = [t.entry_time for t in result.trades]
    entry_equities: list[float] = []
    exit_times = [t.exit_time for t in result.trades]
    exit_equities: list[float] = []
    entry_colors = []
    exit_colors = []

    for t in result.trades:
        # Snap to the nearest equity curve value
        idx = eq.index.searchsorted(t.entry_time, side="left")
        idx = min(idx, len(eq) - 1)
        entry_equities.append(float(eq.iloc[idx]))
        entry_colors.append("#66bb6a" if t.net_pnl > 0 else "#ef5350")

        idx = eq.index.searchsorted(t.exit_time, side="left")
        idx = min(idx, len(eq) - 1)
        exit_equities.append(float(eq.iloc[idx]))
        exit_colors.append("#66bb6a" if t.net_pnl > 0 else "#ef5350")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.65, 0.35],
        vertical_spacing=0.04,
        subplot_titles=("Equity Curve", "Drawdown (%)"),
    )

    # ── Drawdown fill (drawn first so it renders beneath the equity line) ──
    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown.values,
            fill="tozeroy",
            fillcolor="rgba(239,83,80,0.25)",
            line={"color": "rgba(239,83,80,0.6)", "width": 1},
            name="Drawdown %",
            hovertemplate="%{x|%Y-%m-%d %H:%M}<br>DD: %{y:.2f}%<extra></extra>",
        ),
        row=2, col=1,
    )

    # ── Equity curve ──
    fig.add_trace(
        go.Scatter(
            x=eq.index,
            y=eq.values,
            mode="lines",
            line={"color": "#64b5f6", "width": 2},
            name="Portfolio Equity",
            hovertemplate="%{x|%Y-%m-%d %H:%M}<br>$%{y:,.2f}<extra></extra>",
        ),
        row=1, col=1,
    )

    # ── Initial capital reference line ──
    fig.add_hline(
        y=result.initial_capital,
        line_dash="dash",
        line_color="rgba(255,255,255,0.25)",
        row=1, col=1,
    )

    # ── Entry markers (triangles pointing up) ──
    if entry_times:
        fig.add_trace(
            go.Scatter(
                x=entry_times,
                y=entry_equities,
                mode="markers",
                marker={
                    "symbol": "triangle-up",
                    "size": 10,
                    "color": entry_colors,
                    "line": {"width": 1, "color": "white"},
                },
                name="Entry",
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br>Entry @ $%{y:,.2f}<extra></extra>",
            ),
            row=1, col=1,
        )

    # ── Exit markers (triangles pointing down) ──
    if exit_times:
        fig.add_trace(
            go.Scatter(
                x=exit_times,
                y=exit_equities,
                mode="markers",
                marker={
                    "symbol": "triangle-down",
                    "size": 10,
                    "color": exit_colors,
                    "line": {"width": 1, "color": "white"},
                },
                name="Exit",
                hovertemplate="%{x|%Y-%m-%d %H:%M}<br>Exit @ $%{y:,.2f}<extra></extra>",
            ),
            row=1, col=1,
        )

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title="Equity Curve & Drawdown",
        height=520,
        legend={"orientation": "h", "y": -0.1},
        margin={"t": 50, "b": 10, "l": 60, "r": 20},
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    return fig


def _build_trade_scatter(trades: list[TradeLog]) -> go.Figure:
    """Trade scatter: x=entry_time, y=pnl_pct, color=win/loss, size=position size."""
    if not trades:
        return _empty_figure("Trade Scatter — No Trades")

    wins = [t for t in trades if t.net_pnl > 0]
    losses = [t for t in trades if t.net_pnl <= 0]

    # Normalise sizes: larger position = bigger dot, range [8, 24]
    sizes_raw = [t.size for t in trades]
    s_min = min(sizes_raw) if sizes_raw else 1.0
    s_max = max(sizes_raw) if sizes_raw else 1.0
    s_range = s_max - s_min if s_max != s_min else 1.0

    def _norm_size(s: float) -> float:
        return 8.0 + (s - s_min) / s_range * 16.0

    def _hover(t: TradeLog) -> str:
        return (
            f"<b>{t.exit_reason.replace('_', ' ').title()}</b><br>"
            f"Entry: {t.entry_time:%Y-%m-%d %H:%M}<br>"
            f"Exit:  {t.exit_time:%Y-%m-%d %H:%M}<br>"
            f"P&L: {t.pnl_pct:+.2f}% (${t.net_pnl:+,.2f})<br>"
            f"Duration: {int(t.duration.total_seconds() / 3600)}h<br>"
            f"Side: {t.side.value}"
        )

    fig = go.Figure()

    if wins:
        fig.add_trace(go.Scatter(
            x=[t.entry_time for t in wins],
            y=[t.pnl_pct for t in wins],
            mode="markers",
            marker={"color": "#66bb6a", "size": [_norm_size(t.size) for t in wins], "opacity": 0.8,
                    "line": {"width": 1, "color": "white"}},
            name="Win",
            text=[_hover(t) for t in wins],
            hovertemplate="%{text}<extra></extra>",
        ))

    if losses:
        fig.add_trace(go.Scatter(
            x=[t.entry_time for t in losses],
            y=[t.pnl_pct for t in losses],
            mode="markers",
            marker={"color": "#ef5350", "size": [_norm_size(t.size) for t in losses], "opacity": 0.8,
                    "line": {"width": 1, "color": "white"}},
            name="Loss",
            text=[_hover(t) for t in losses],
            hovertemplate="%{text}<extra></extra>",
        ))

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title="Trade P&L Scatter (size = position size)",
        height=380,
        xaxis_title="Entry Time",
        yaxis_title="P&L (%)",
        legend={"orientation": "h"},
        margin={"t": 50, "b": 50, "l": 60, "r": 20},
        hovermode="closest",
    )
    return fig


def _build_monthly_heatmap(trades: list[TradeLog]) -> go.Figure:
    """Calendar-style monthly returns heatmap. Green = positive, red = negative."""
    if not trades:
        return _empty_figure("Monthly Returns Heatmap — No Trades")

    monthly = _monthly_returns(trades)
    if monthly.empty:
        return _empty_figure("Monthly Returns Heatmap — No Data")

    years = sorted(monthly["year"].unique())
    months = list(range(1, 13))
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Build a 2-D grid: rows=years, cols=months
    z_matrix: list[list[float | None]] = []
    text_matrix: list[list[str]] = []

    for year in years:
        row: list[float | None] = []
        text_row: list[str] = []
        for month in months:
            match = monthly[(monthly["year"] == year) & (monthly["month"] == month)]
            if not match.empty:
                val = float(match["return_pct"].iloc[0])
                row.append(val)
                text_row.append(f"{val:+.2f}%")
            else:
                row.append(None)
                text_row.append("")
        z_matrix.append(row)
        text_matrix.append(text_row)

    fig = go.Figure(go.Heatmap(
        z=z_matrix,
        x=month_names,
        y=[str(y) for y in years],
        text=text_matrix,
        texttemplate="%{text}",
        colorscale=[
            [0.0, "#b71c1c"],
            [0.4, "#ef5350"],
            [0.5, "#263238"],
            [0.6, "#66bb6a"],
            [1.0, "#1b5e20"],
        ],
        zmid=0.0,
        colorbar={"title": "Return %"},
        hovertemplate="<b>%{y} %{x}</b><br>Return: %{z:.2f}%<extra></extra>",
    ))

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title="Monthly Returns Heatmap",
        height=max(200, 60 + len(years) * 45),
        margin={"t": 50, "b": 50, "l": 60, "r": 80},
        xaxis={"side": "top"},
    )
    return fig


def _build_duration_vs_pnl(trades: list[TradeLog]) -> go.Figure:
    """Scatter: trade duration (hours) vs P&L (%). Does holding longer pay?"""
    if not trades:
        return _empty_figure("Duration vs P&L — No Trades")

    durations_h = [t.duration.total_seconds() / 3600.0 for t in trades]
    pnl_pcts = [t.pnl_pct for t in trades]
    colors = ["#66bb6a" if t.net_pnl > 0 else "#ef5350" for t in trades]
    labels = [
        f"{t.exit_reason.replace('_', ' ').title()}<br>"
        f"Duration: {t.duration.total_seconds()/3600:.1f}h<br>"
        f"P&L: {t.pnl_pct:+.2f}%"
        for t in trades
    ]

    fig = go.Figure(go.Scatter(
        x=durations_h,
        y=pnl_pcts,
        mode="markers",
        marker={
            "color": colors,
            "size": 10,
            "opacity": 0.75,
            "line": {"width": 1, "color": "rgba(255,255,255,0.3)"},
        },
        text=labels,
        hovertemplate="%{text}<extra></extra>",
    ))

    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)")

    # Linear trendline via numpy
    if len(durations_h) >= 3:
        try:
            coeffs = np.polyfit(durations_h, pnl_pcts, 1)
            x_trend = np.linspace(min(durations_h), max(durations_h), 100)
            y_trend = np.polyval(coeffs, x_trend)
            fig.add_trace(go.Scatter(
                x=x_trend.tolist(),
                y=y_trend.tolist(),
                mode="lines",
                line={"color": "#ffa726", "width": 2, "dash": "dot"},
                name="Trend",
                hoverinfo="skip",
            ))
        except np.linalg.LinAlgError:
            pass  # Not enough variance — skip trendline

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title="Trade Duration vs P&L (orange = linear trend)",
        height=380,
        xaxis_title="Duration (hours)",
        yaxis_title="P&L (%)",
        showlegend=False,
        margin={"t": 50, "b": 50, "l": 60, "r": 20},
        hovermode="closest",
    )
    return fig


def _build_exit_reason_pie(trades: list[TradeLog]) -> go.Figure:
    """Pie chart of exit reasons: stop_loss, take_profit, signal_exit, end_of_data, scale_out."""
    if not trades:
        return _empty_figure("Exit Reason Breakdown — No Trades")

    counts: dict[str, int] = {}
    for t in trades:
        reason = t.exit_reason
        counts[reason] = counts.get(reason, 0) + 1

    labels = list(counts.keys())
    values = [counts[k] for k in labels]

    # Assign meaningful colors per exit reason
    color_map = {
        "stop_loss": "#ef5350",
        "take_profit": "#66bb6a",
        "signal_exit": "#64b5f6",
        "end_of_data": "#ffa726",
    }
    colors = [
        color_map.get(label.split("_t")[0] if "scale_out" in label else label, "#b0bec5")
        for label in labels
    ]

    display_labels = [l.replace("_", " ").title() for l in labels]

    fig = go.Figure(go.Pie(
        labels=display_labels,
        values=values,
        marker={"colors": colors, "line": {"color": "rgba(0,0,0,0.3)", "width": 2}},
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        textinfo="label+percent",
        hole=0.35,
    ))

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title="Exit Reason Breakdown",
        height=380,
        margin={"t": 50, "b": 50, "l": 20, "r": 20},
    )
    return fig


def _build_cumulative_wins_losses(trades: list[TradeLog]) -> go.Figure:
    """Running cumulative count of wins and losses to surface hot/cold streaks."""
    if not trades:
        return _empty_figure("Cumulative Wins vs Losses — No Trades")

    times = [t.exit_time for t in trades]
    cumulative_wins = np.cumsum([1 if t.net_pnl > 0 else 0 for t in trades])
    cumulative_losses = np.cumsum([1 if t.net_pnl <= 0 else 0 for t in trades])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=cumulative_wins.tolist(),
        mode="lines",
        line={"color": "#66bb6a", "width": 2},
        name="Cumulative Wins",
        fill="tozeroy",
        fillcolor="rgba(102,187,106,0.15)",
        hovertemplate="%{x|%Y-%m-%d}<br>Wins: %{y}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=times,
        y=cumulative_losses.tolist(),
        mode="lines",
        line={"color": "#ef5350", "width": 2},
        name="Cumulative Losses",
        fill="tozeroy",
        fillcolor="rgba(239,83,80,0.15)",
        hovertemplate="%{x|%Y-%m-%d}<br>Losses: %{y}<extra></extra>",
    ))

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title="Cumulative Wins vs Losses (streak visualization)",
        height=320,
        xaxis_title="Time",
        yaxis_title="Count",
        legend={"orientation": "h"},
        margin={"t": 50, "b": 50, "l": 60, "r": 20},
        hovermode="x unified",
    )
    return fig


def _build_rolling_sharpe(trades: list[TradeLog]) -> go.Figure:
    """20-trade rolling Sharpe ratio — flat or degrading = edge is decaying."""
    if len(trades) < _ROLLING_SHARPE_WINDOW:
        return _empty_figure(
            f"Rolling Sharpe — Need at least {_ROLLING_SHARPE_WINDOW} trades "
            f"(have {len(trades)})"
        )

    times, sharpe_vals = _rolling_sharpe(trades, _ROLLING_SHARPE_WINDOW)
    if not times:
        return _empty_figure("Rolling Sharpe — Insufficient Data")

    colors = ["#66bb6a" if s > 0 else "#ef5350" for s in sharpe_vals]

    fig = go.Figure()
    fig.add_hrect(y0=0, y1=1, fillcolor="rgba(102,187,106,0.08)", line_width=0)
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
    fig.add_hline(y=1, line_dash="dot", line_color="rgba(102,187,106,0.5)", annotation_text="Sharpe=1")

    fig.add_trace(go.Scatter(
        x=times,
        y=sharpe_vals,
        mode="lines+markers",
        line={"color": "#64b5f6", "width": 2},
        marker={"color": colors, "size": 6},
        name=f"Rolling Sharpe ({_ROLLING_SHARPE_WINDOW}-trade window)",
        hovertemplate="%{x|%Y-%m-%d}<br>Sharpe: %{y:.3f}<extra></extra>",
    ))

    fig.update_layout(
        template=_DARK_TEMPLATE,
        title=f"Rolling Sharpe Ratio ({_ROLLING_SHARPE_WINDOW}-trade window)",
        height=320,
        xaxis_title="Trade Entry Time",
        yaxis_title="Sharpe Ratio",
        margin={"t": 50, "b": 50, "l": 60, "r": 20},
        hovermode="x unified",
    )
    return fig


def _empty_figure(message: str) -> go.Figure:
    """Return a placeholder figure with a centred message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        font={"size": 14, "color": "#ffa726"},
        showarrow=False,
    )
    fig.update_layout(
        template=_DARK_TEMPLATE,
        height=300,
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"t": 40, "b": 20, "l": 20, "r": 20},
    )
    return fig


# ---------------------------------------------------------------------------
# Main report assembly
# ---------------------------------------------------------------------------


def generate_report(
    result: BacktestResult,
    strategy: str,
    symbol: str,
    timeframe: str,
    output_path: Path,
) -> None:
    """
    Assemble all chart sections into a single self-contained HTML file.

    If result has zero trades the charts section is replaced with a warning banner.
    """
    logger.info("Generating interactive report at %s", output_path)

    header_html = _build_header_html(result, strategy, symbol, timeframe)

    if result.total_trades == 0:
        no_trades_html = (
            '<div class="no-trades-banner">'
            "No trades were generated for this strategy/symbol/timeframe combination.<br>"
            "Try relaxing the strategy parameters or using a different timeframe."
            "</div>"
        )
        charts_html = no_trades_html
    else:
        # Build each figure and convert to HTML div fragments
        figures: list[tuple[str, go.Figure]] = [
            ("equity_curve", _build_equity_chart(result)),
            ("trade_scatter", _build_trade_scatter(result.trades)),
            ("monthly_heatmap", _build_monthly_heatmap(result.trades)),
            ("duration_pnl", _build_duration_vs_pnl(result.trades)),
            ("exit_reasons", _build_exit_reason_pie(result.trades)),
            ("cumulative_wl", _build_cumulative_wins_losses(result.trades)),
            ("rolling_sharpe", _build_rolling_sharpe(result.trades)),
        ]

        # Layout: equity curve full-width; everything else in two-column grid
        two_col_figures = figures[1:]  # all except equity curve

        # Equity curve div (full width)
        equity_div = pio.to_html(
            figures[0][1],
            full_html=False,
            include_plotlyjs=False,  # we include it once at page level
            div_id="equity_curve",
        )

        # Two-column grid of remaining charts
        col_divs = []
        for _fid, fig in two_col_figures:
            col_divs.append(
                pio.to_html(fig, full_html=False, include_plotlyjs=False, div_id=_fid)
            )

        # Pair them up into rows
        grid_rows_html = ""
        for i in range(0, len(col_divs), 2):
            left = col_divs[i]
            right = col_divs[i + 1] if i + 1 < len(col_divs) else ""
            right_col = f'<div style="flex:1;min-width:0;">{right}</div>' if right else ""
            grid_rows_html += (
                '<div style="display:flex;gap:8px;margin-bottom:8px;">'
                f'<div style="flex:1;min-width:0;">{left}</div>'
                f"{right_col}"
                "</div>"
            )

        charts_html = (
            f'<div class="charts-wrapper" style="padding:0 8px;">'
            f"{equity_div}"
            f"{grid_rows_html}"
            f"</div>"
        )

    # Include plotly.js CDN in the head — produces a self-contained file
    # when the figures were built with include_plotlyjs=False
    page_title = f"ATLAS Backtest — {strategy} on {symbol}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  {_STAT_CARD_CSS}
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
</head>
<body>
{header_html}
{charts_html}
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")
    logger.info("Report written: %s (%d bytes)", output_path, output_path.stat().st_size)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    args = _parse_args()

    strategy_name: str = args.strategy
    symbol: str = args.symbol
    timeframe: str = args.timeframe
    capital: float = args.capital
    limit: int = args.limit

    # ── Validate strategy name before doing any network IO ──
    try:
        strategy_cls = StrategyRegistry.get(strategy_name)
    except KeyError:
        available = sorted(StrategyRegistry.list())
        print(
            f"ERROR: Strategy '{strategy_name}' not found in StrategyRegistry.\n"
            f"Available strategies:\n  " + "\n  ".join(available),
            file=sys.stderr,
        )
        raise SystemExit(1)

    # ── Fetch OHLCV data ──
    try:
        df = await _fetch_ohlcv(symbol, timeframe, limit)
    except Exception as exc:
        print(f"ERROR: Failed to fetch market data for {symbol}/{timeframe}: {exc}", file=sys.stderr)
        raise SystemExit(1)

    if len(df) < 50:
        print(
            f"ERROR: Only {len(df)} bars returned for {symbol}/{timeframe}. "
            "Need at least 50 bars to run a meaningful backtest.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # ── Run backtest ──
    logger.info(
        "Running backtest: strategy=%s, symbol=%s, timeframe=%s, bars=%d, capital=$%.0f",
        strategy_name, symbol, timeframe, len(df), capital,
    )
    engine = BacktestEngine(
        initial_capital=capital,
        commission_pct=0.001,
        risk_per_trade_pct=0.015,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # Disabled — proven to hurt returns (see MEMORY.md)
    )

    try:
        strategy_instance = strategy_cls()
        result = engine.run(df, strategy_instance)
    except Exception as exc:
        print(f"ERROR: Backtest failed — {exc}", file=sys.stderr)
        logger.exception("Backtest error")
        raise SystemExit(1)

    # Print the text summary to stdout so the user sees numbers immediately
    try:
        print(result.summary())
    except UnicodeEncodeError:
        print(result.summary().encode("ascii", errors="replace").decode())

    # ── Resolve output path ──
    logs_dir = Path(__file__).resolve().parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    safe_symbol = symbol.replace("/", "_").replace(" ", "_")
    output_path = logs_dir / f"backtest_{strategy_name}_{safe_symbol}.html"

    # ── Generate HTML report ──
    generate_report(result, strategy_name, symbol, timeframe, output_path)
    print(f"\nReport saved to: {output_path}")

    # ── Open in browser ──
    if not args.no_open:
        url = output_path.as_uri()
        logger.info("Opening report in browser: %s", url)
        webbrowser.open(url)
        print(f"Opening in browser: {url}")


if __name__ == "__main__":
    asyncio.run(main())
