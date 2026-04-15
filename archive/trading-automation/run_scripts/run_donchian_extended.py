"""
Extended Donchian Breakout backtest across all configured symbols.
1500 candles of 4h data from Kraken (~8 months).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import ccxt
import pandas as pd
import numpy as np
import math
from datetime import timedelta
from backtesting.engine import BacktestEngine
from strategies.technical.donchian_breakout import DonchianBreakoutStrategy
from strategies.base import Direction

SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT", "DOT/USDT",
    "XRP/USDT", "AVAX/USDT", "ATOM/USDT", "DOGE/USDT", "SHIB/USDT",
    "MANA/USDT",
]
TIMEFRAME = "4h"
LIMIT = 1500
INITIAL_CAPITAL = 10_000


def fetch_data(exchange, symbol, timeframe, limit):
    """Fetch OHLCV from Kraken and return a DataFrame with DatetimeIndex."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df.attrs["symbol"] = symbol
    return df


def max_consecutive_losses(trades):
    streak = 0
    max_streak = 0
    for t in trades:
        if t.net_pnl <= 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak


def max_drawdown_from_equity(trades, initial_capital):
    """Compute max drawdown from trade-level cumulative P&L."""
    if not trades:
        return 0.0
    equity = initial_capital
    peak = equity
    max_dd = 0.0
    for t in trades:
        equity += t.net_pnl
        if equity > peak:
            peak = equity
        dd = (peak - equity) / peak if peak > 0 else 0.0
        max_dd = max(max_dd, dd)
    return max_dd


def compute_sharpe(trades):
    if not trades:
        return 0.0
    pnl_pcts = [t.pnl_pct for t in trades]
    mean_p = np.mean(pnl_pcts)
    std_p = np.std(pnl_pcts, ddof=1) if len(pnl_pcts) > 1 else 0.0
    if std_p == 0:
        return 0.0
    return (mean_p / std_p) * math.sqrt(len(pnl_pcts))


def profit_factor(trades):
    gross_wins = sum(t.net_pnl for t in trades if t.net_pnl > 0)
    gross_losses = abs(sum(t.net_pnl for t in trades if t.net_pnl <= 0))
    if gross_losses == 0:
        return float("inf") if gross_wins > 0 else 0.0
    return gross_wins / gross_losses


def avg_duration(trades):
    if not trades:
        return timedelta(0)
    total = sum((t.duration.total_seconds() for t in trades), 0.0)
    return timedelta(seconds=total / len(trades))


def print_separator(char="=", width=120):
    print(char * width)


def main():
    exchange = ccxt.kraken({"enableRateLimit": True})
    engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, regime_filter=True)
    strategy = DonchianBreakoutStrategy()

    all_results = []

    print_separator()
    print("  ATLAS — Donchian Breakout Extended Backtest")
    print(f"  Exchange: Kraken | Timeframe: {TIMEFRAME} | Candles: {LIMIT} | Capital: ${INITIAL_CAPITAL:,.0f}")
    print_separator()
    print()

    for symbol in SYMBOLS:
        print(f"--- Fetching {symbol} ...", end=" ", flush=True)
        try:
            df = fetch_data(exchange, symbol, TIMEFRAME, LIMIT)
        except Exception as e:
            print(f"FAILED: {e}")
            all_results.append({"symbol": symbol, "error": str(e)})
            continue
        print(f"{len(df)} candles ({df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')})")

        # Run backtest
        result = engine.run(df, strategy)
        trades = result.trades

        # Compute detailed stats
        longs = [t for t in trades if t.side == Direction.LONG]
        shorts = [t for t in trades if t.side == Direction.SHORT]
        winners = [t for t in trades if t.net_pnl > 0]
        losers = [t for t in trades if t.net_pnl <= 0]
        long_winners = [t for t in longs if t.net_pnl > 0]
        short_winners = [t for t in shorts if t.net_pnl > 0]

        total = len(trades)
        net_pnl = sum(t.net_pnl for t in trades)
        ret_pct = (net_pnl / INITIAL_CAPITAL) * 100.0
        win_rate = len(winners) / total * 100 if total else 0.0
        long_wr = len(long_winners) / len(longs) * 100 if longs else 0.0
        short_wr = len(short_winners) / len(shorts) * 100 if shorts else 0.0
        sharpe = compute_sharpe(trades)
        max_consec = max_consecutive_losses(trades)
        max_dd = max_drawdown_from_equity(trades, INITIAL_CAPITAL)
        pf = profit_factor(trades)
        avg_win = np.mean([t.net_pnl for t in winners]) if winners else 0.0
        avg_loss = np.mean([t.net_pnl for t in losers]) if losers else 0.0
        avg_dur = avg_duration(trades)

        info = {
            "symbol": symbol,
            "candles": len(df),
            "period": f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
            "total": total,
            "longs": len(longs),
            "shorts": len(shorts),
            "net_pnl": net_pnl,
            "return_pct": ret_pct,
            "win_rate": win_rate,
            "long_wr": long_wr,
            "short_wr": short_wr,
            "sharpe": sharpe,
            "max_consec_loss": max_consec,
            "max_dd": max_dd,
            "profit_factor": pf,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "avg_duration": avg_dur,
        }
        all_results.append(info)

        # Print per-symbol results
        print(f"  Trades: {total:>3d}  (LONG: {len(longs):>2d}, SHORT: {len(shorts):>2d})")
        print(f"  Net P&L: ${net_pnl:>+10,.2f}  ({ret_pct:>+.2f}%)")
        print(f"  Win Rate: {win_rate:>5.1f}%  (LONG: {long_wr:.1f}%, SHORT: {short_wr:.1f}%)")
        print(f"  Sharpe: {sharpe:>+.3f}  |  Profit Factor: {pf:.3f}")
        print(f"  Max Consec Losses: {max_consec}  |  Max Drawdown: {max_dd*100:.2f}%")
        print(f"  Avg Winner: ${avg_win:>+.2f}  |  Avg Loser: ${avg_loss:>+.2f}")
        print(f"  Avg Duration: {avg_dur}")
        print()

    # ========================= PORTFOLIO SUMMARY =========================
    valid = [r for r in all_results if "error" not in r]
    if not valid:
        print("No valid results.")
        return

    print_separator()
    print("  PORTFOLIO SUMMARY")
    print_separator()
    print()

    # Header
    hdr = (
        f"{'Symbol':<12} {'Trades':>6} {'L':>3} {'S':>3} "
        f"{'Net P&L':>11} {'Return%':>8} {'WinRate':>7} {'Sharpe':>7} "
        f"{'PF':>6} {'MaxDD%':>7} {'MaxCL':>5} {'AvgWin':>9} {'AvgLoss':>9} {'AvgDur':>16}"
    )
    print(hdr)
    print("-" * len(hdr))

    total_pnl = 0.0
    total_trades = 0
    total_longs = 0
    total_shorts = 0

    for r in valid:
        dur_str = str(r["avg_duration"]).split(".")[0]  # strip microseconds
        pf_str = f"{r['profit_factor']:.2f}" if r["profit_factor"] != float("inf") else "inf"
        print(
            f"{r['symbol']:<12} {r['total']:>6d} {r['longs']:>3d} {r['shorts']:>3d} "
            f"${r['net_pnl']:>+10,.2f} {r['return_pct']:>+7.2f}% {r['win_rate']:>6.1f}% {r['sharpe']:>+7.3f} "
            f"{pf_str:>6} {r['max_dd']*100:>6.2f}% {r['max_consec_loss']:>5d} "
            f"${r['avg_win']:>+8.2f} ${r['avg_loss']:>+8.2f} {dur_str:>16}"
        )
        total_pnl += r["net_pnl"]
        total_trades += r["total"]
        total_longs += r["longs"]
        total_shorts += r["shorts"]

    print("-" * len(hdr))

    # Portfolio total (if all 11 symbols traded independently with $10K each)
    portfolio_capital = INITIAL_CAPITAL * len(valid)
    portfolio_return = (total_pnl / portfolio_capital) * 100 if portfolio_capital > 0 else 0.0

    print(
        f"{'TOTAL':<12} {total_trades:>6d} {total_longs:>3d} {total_shorts:>3d} "
        f"${total_pnl:>+10,.2f} {portfolio_return:>+7.2f}%"
    )
    print()
    print(f"  Portfolio Capital: ${portfolio_capital:,.0f} ({len(valid)} symbols x ${INITIAL_CAPITAL:,.0f})")
    print(f"  Total Net P&L:    ${total_pnl:>+,.2f}")
    print(f"  Portfolio Return:  {portfolio_return:>+.2f}%")
    print(f"  Total Trades:      {total_trades}")
    print(f"  Total LONG:        {total_longs}  |  Total SHORT: {total_shorts}")
    print_separator()


if __name__ == "__main__":
    main()
