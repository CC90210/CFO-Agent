"""
Extended backtest: SmartMoney strategy across 5 symbols, 1500 4H candles from Kraken.
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import ccxt
import pandas as pd
import numpy as np
from datetime import timedelta

from backtesting.engine import BacktestEngine
from strategies.technical.smart_money import SmartMoneyStrategy

SYMBOLS = ["ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "AVAX/USDT"]
TIMEFRAME = "4h"
CANDLE_LIMIT = 1500
INITIAL_CAPITAL = 10_000


def fetch_ohlcv(exchange, symbol: str) -> pd.DataFrame:
    """Fetch OHLCV from Kraken and return DataFrame with DatetimeIndex."""
    print(f"  Fetching {symbol} ({CANDLE_LIMIT} x {TIMEFRAME}) from Kraken...")
    raw = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=CANDLE_LIMIT)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df = df.astype(float)
    print(f"  Got {len(df)} candles: {df.index[0]} -> {df.index[-1]}")
    return df


def max_consecutive_losses(trades) -> int:
    streak = 0
    worst = 0
    for t in trades:
        if t.net_pnl < 0:
            streak += 1
            worst = max(worst, streak)
        else:
            streak = 0
    return worst


def max_drawdown_from_equity(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min()) if len(dd) > 0 else 0.0


def report_symbol(symbol: str, result, trades) -> dict:
    """Print per-symbol report, return stats dict."""
    longs = [t for t in trades if t.side.name == "LONG"]
    shorts = [t for t in trades if t.side.name == "SHORT"]

    total = len(trades)
    winners = [t for t in trades if t.net_pnl > 0]
    losers = [t for t in trades if t.net_pnl <= 0]

    long_winners = [t for t in longs if t.net_pnl > 0]
    short_winners = [t for t in shorts if t.net_pnl > 0]

    net_pnl = sum(t.net_pnl for t in trades)
    ret_pct = (result.final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    win_rate = len(winners) / total * 100 if total else 0.0
    long_wr = len(long_winners) / len(longs) * 100 if longs else 0.0
    short_wr = len(short_winners) / len(shorts) * 100 if shorts else 0.0

    avg_win = np.mean([t.net_pnl for t in winners]) if winners else 0.0
    avg_loss = np.mean([t.net_pnl for t in losers]) if losers else 0.0

    gross_profit = sum(t.net_pnl for t in winners)
    gross_loss = abs(sum(t.net_pnl for t in losers))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0

    consec_loss = max_consecutive_losses(trades)
    mdd = max_drawdown_from_equity(result.equity_curve)

    durations = [t.duration for t in trades if t.duration is not None]
    avg_dur = sum(durations, timedelta()) / len(durations) if durations else timedelta()

    print(f"\n{'='*60}")
    print(f"  {symbol} — SmartMoney 4H ({len(result.equity_curve)} bars)")
    print(f"{'='*60}")
    print(f"  Total trades       : {total}  (LONG: {len(longs)}, SHORT: {len(shorts)})")
    print(f"  Net P&L            : ${net_pnl:>+,.2f}")
    print(f"  Return             : {ret_pct:>+.2f}%")
    print(f"  Win rate (all)     : {win_rate:.1f}%")
    print(f"  Win rate (long)    : {long_wr:.1f}%")
    print(f"  Win rate (short)   : {short_wr:.1f}%")
    print(f"  Sharpe ratio       : {result.sharpe_ratio:.3f}")
    print(f"  Profit factor      : {profit_factor:.2f}")
    print(f"  Max consec losses  : {consec_loss}")
    print(f"  Max drawdown       : {mdd*100:+.2f}%")
    print(f"  Avg winner         : ${avg_win:>+,.2f}")
    print(f"  Avg loser          : ${avg_loss:>+,.2f}")
    print(f"  Avg trade duration : {avg_dur}")

    return {
        "symbol": symbol,
        "trades": total,
        "longs": len(longs),
        "shorts": len(shorts),
        "net_pnl": net_pnl,
        "return_pct": ret_pct,
        "win_rate": win_rate,
        "sharpe": result.sharpe_ratio,
        "profit_factor": profit_factor,
        "max_consec_loss": consec_loss,
        "max_dd": mdd,
        "avg_winner": avg_win,
        "avg_loser": avg_loss,
        "avg_duration": avg_dur,
    }


def main():
    print("Atlas online. Running extended SmartMoney backtest across 5 symbols.\n")

    exchange = ccxt.kraken({"enableRateLimit": True})

    all_stats = []

    for symbol in SYMBOLS:
        try:
            df = fetch_ohlcv(exchange, symbol)
        except Exception as e:
            print(f"\n  SKIP {symbol}: {e}")
            continue

        engine = BacktestEngine(initial_capital=INITIAL_CAPITAL, regime_filter=True)
        strategy = SmartMoneyStrategy()

        try:
            result = engine.run(df, strategy)
        except Exception as e:
            print(f"\n  BACKTEST FAILED {symbol}: {e}")
            continue

        trades = result.trades
        stats = report_symbol(symbol, result, trades)
        all_stats.append(stats)

    # ---- Totals ----
    if all_stats:
        print(f"\n\n{'='*60}")
        print(f"  PORTFOLIO TOTALS — SmartMoney 4H x {len(all_stats)} symbols")
        print(f"{'='*60}")

        total_trades = sum(s["trades"] for s in all_stats)
        total_longs = sum(s["longs"] for s in all_stats)
        total_shorts = sum(s["shorts"] for s in all_stats)
        total_pnl = sum(s["net_pnl"] for s in all_stats)
        avg_return = np.mean([s["return_pct"] for s in all_stats])
        avg_sharpe = np.mean([s["sharpe"] for s in all_stats])
        avg_wr = np.mean([s["win_rate"] for s in all_stats])
        worst_dd = min(s["max_dd"] for s in all_stats)

        all_winners = [s["avg_winner"] for s in all_stats if s["avg_winner"] > 0]
        all_losers = [s["avg_loser"] for s in all_stats if s["avg_loser"] < 0]

        print(f"  Total trades       : {total_trades}  (LONG: {total_longs}, SHORT: {total_shorts})")
        print(f"  Combined P&L       : ${total_pnl:>+,.2f}")
        print(f"  Avg return/symbol  : {avg_return:>+.2f}%")
        print(f"  Avg win rate       : {avg_wr:.1f}%")
        print(f"  Avg Sharpe         : {avg_sharpe:.3f}")
        print(f"  Worst drawdown     : {worst_dd*100:+.2f}%")
        if all_winners:
            print(f"  Avg winner (pool)  : ${np.mean(all_winners):>+,.2f}")
        if all_losers:
            print(f"  Avg loser (pool)   : ${np.mean(all_losers):>+,.2f}")

        print(f"\n  Per-symbol summary:")
        print(f"  {'Symbol':<12} {'Trades':>6} {'P&L':>10} {'Return':>8} {'WR':>6} {'Sharpe':>7} {'MaxDD':>8} {'PF':>6}")
        print(f"  {'-'*12} {'-'*6} {'-'*10} {'-'*8} {'-'*6} {'-'*7} {'-'*8} {'-'*6}")
        for s in all_stats:
            print(f"  {s['symbol']:<12} {s['trades']:>6} ${s['net_pnl']:>+9,.2f} {s['return_pct']:>+7.2f}% {s['win_rate']:>5.1f}% {s['sharpe']:>7.3f} {s['max_dd']*100:>+7.2f}% {s['profit_factor']:>6.2f}")
    else:
        print("\nNo symbols completed successfully.")


if __name__ == "__main__":
    main()
