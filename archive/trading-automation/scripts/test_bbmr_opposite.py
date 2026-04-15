"""
scripts/test_bbmr_opposite.py

Backtest bb_mean_reversion with the EXACT live parameters from config/strategies.yaml.

Key difference from previous tests: tp_target="opposite" (TP at opposite BB band,
not the middle band). This gives a wider TP target and changes the R:R profile
substantially.

Live parameters (2026-03-25, strategies.yaml bb_mean_reversion section):
  bb_period=20, bb_std=2.0, adx_period=14, adx_max=30.0
  atr_period=14, atr_stop_mult=1.5
  pctb_long_threshold=0.25, pctb_short_threshold=0.75
  stoch_rsi_period=14, stoch_k_smooth=3, stoch_d_smooth=3
  stoch_oversold=25.0, stoch_overbought=75.0
  rsi_period=14, volume_period=20
  squeeze_guard_percentile=0.0, squeeze_lookback=60
  tp_target="opposite"

Symbols: DOGE/USD, BTC/USD, ADA/USD, LTC/USD, ATOM/USD, LINK/USD, XRP/USD
Data: 500 bars, 1h timeframe, Kraken
"""
from __future__ import annotations

import os
import sys

# Ensure project root is on path so strategy imports work
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
os.chdir(_ROOT)

from dotenv import load_dotenv
load_dotenv()

import ccxt
import pandas as pd

from strategies.technical.bb_mean_reversion import BBMeanReversionStrategy

# ---------------------------------------------------------------------------
# Live config — exact copy from strategies.yaml bb_mean_reversion.parameters
# ---------------------------------------------------------------------------
LIVE_PARAMS: dict = dict(
    bb_period=20,
    bb_std=2.0,
    adx_period=14,
    adx_max=30.0,
    atr_period=14,
    atr_stop_mult=1.5,
    pctb_long_threshold=0.25,
    pctb_short_threshold=0.75,
    stoch_rsi_period=14,
    stoch_k_smooth=3,
    stoch_d_smooth=3,
    stoch_oversold=25.0,
    stoch_overbought=75.0,
    rsi_period=14,
    volume_period=20,
    squeeze_guard_percentile=0.0,
    squeeze_lookback=60,
    tp_target="opposite",          # THE critical parameter
)

SYMBOLS = [
    "DOGE/USD",
    "BTC/USD",
    "ADA/USD",
    "LTC/USD",
    "ATOM/USD",
    "LINK/USD",
    "XRP/USD",
]

TIMEFRAME = "1h"
BARS = 500

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch(exchange: ccxt.Exchange, symbol: str) -> pd.DataFrame:
    """Fetch OHLCV from Kraken and return a clean DataFrame."""
    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=BARS)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df.attrs["symbol"] = symbol
    return df


def _backtest(df: pd.DataFrame, strategy: BBMeanReversionStrategy) -> dict:
    """
    Bar-by-bar simulation.  At each bar we pass df[:i+1] to the strategy's
    analyze() method (no look-ahead).  Fills happen at the next bar's open
    (one-bar delay — realistic for signal-on-close / fill-on-open workflow).

    Exit priority (checked each bar after entry):
      1. SL hit (bar low/high crosses stop)
      2. TP hit (bar high/low crosses target)
      3. ADX-trend exit (adx > 30 signals emerging trend — abort range trade)
      4. StochRSI opposite-extreme exit
      5. 72-bar timeout (3 days on 1h bars)

    Returns dict with return_pct, trade_count, win_rate, profit_factor.
    """
    symbol = df.attrs.get("symbol", "?")
    min_bars = strategy._min_bars

    trades: list[dict] = []
    in_trade = False
    direction: str = ""
    entry: float = 0.0
    sl: float = 0.0
    tp: float = 0.0
    entry_bar: int = 0

    # Precompute all indicators up front (vectorised — matches how analyze() works
    # internally, but we need them for the exit checks without re-running analyze).
    from strategies.technical.indicators import adx as calc_adx, stochastic_rsi

    adx_df = calc_adx(df.rename(columns={"open": "open", "high": "high",
                                           "low": "low", "close": "close"}),
                      strategy.adx_period)
    stoch_df = stochastic_rsi(
        df["close"],
        strategy.stoch_rsi_period,
        strategy.stoch_rsi_period,
        strategy.stoch_k_smooth,
        strategy.stoch_d_smooth,
    )

    for i in range(min_bars, len(df) - 1):
        bar = df.iloc[i]
        next_bar = df.iloc[i + 1]   # signal fires on close[i], fill on open[i+1]

        adx_now = adx_df["adx"].iloc[i]
        stoch_k = stoch_df["stoch_rsi_k"].iloc[i] * 100  # 0–100

        if not in_trade:
            # --- Signal detection ---
            signal = strategy.analyze(df.iloc[: i + 1])
            if signal is None:
                continue

            # Enter at next bar open (one-bar delay)
            entry = next_bar["open"]
            direction = "LONG" if signal.direction.name == "LONG" else "SHORT"
            sl = signal.stop_loss
            tp = signal.take_profit
            entry_bar = i + 1
            in_trade = True

        else:
            bar_idx = i
            lo = bar["low"]
            hi = bar["high"]

            exit_price: float | None = None
            exit_reason: str = ""

            if direction == "LONG":
                # SL — worst case fill at SL price when bar low pierces it
                if lo <= sl:
                    exit_price = sl
                    exit_reason = "SL"
                # TP — fill at TP price when bar high reaches it
                elif hi >= tp:
                    exit_price = tp
                    exit_reason = "TP"
                # Trend-emergence exit
                elif not pd.isna(adx_now) and adx_now > 30.0:
                    exit_price = bar["close"]
                    exit_reason = "ADX"
                # StochRSI overbought exit (momentum exhausted)
                elif not pd.isna(stoch_k) and stoch_k > 85.0:
                    exit_price = bar["close"]
                    exit_reason = "STOCH"

            else:  # SHORT
                if hi >= sl:
                    exit_price = sl
                    exit_reason = "SL"
                elif lo <= tp:
                    exit_price = tp
                    exit_reason = "TP"
                elif not pd.isna(adx_now) and adx_now > 30.0:
                    exit_price = bar["close"]
                    exit_reason = "ADX"
                elif not pd.isna(stoch_k) and stoch_k < 15.0:
                    exit_price = bar["close"]
                    exit_reason = "STOCH"

            # Timeout — 72 bars (~3 days on 1h)
            if exit_price is None and bar_idx - entry_bar >= 72:
                exit_price = bar["close"]
                exit_reason = "TIMEOUT"

            if exit_price is not None:
                if direction == "LONG":
                    pnl_pct = (exit_price - entry) / entry * 100.0
                else:
                    pnl_pct = (entry - exit_price) / entry * 100.0

                trades.append({
                    "pnl": pnl_pct,
                    "reason": exit_reason,
                    "bars": bar_idx - entry_bar,
                    "direction": direction,
                })
                in_trade = False

    # --- Metrics ---
    n = len(trades)
    if n == 0:
        return {"symbol": symbol, "trades": 0, "wr": 0.0, "total": 0.0, "pf": 0.0}

    wins = [t for t in trades if t["pnl"] > 0]
    gross_wins = sum(t["pnl"] for t in wins)
    gross_losses = abs(sum(t["pnl"] for t in trades if t["pnl"] <= 0))
    pf = gross_wins / gross_losses if gross_losses > 0 else float("inf")

    return {
        "symbol": symbol,
        "trades": n,
        "wr": len(wins) / n * 100.0,
        "total": sum(t["pnl"] for t in trades),
        "pf": pf,
        "by_reason": {
            r: sum(1 for t in trades if t["reason"] == r)
            for r in ("SL", "TP", "ADX", "STOCH", "TIMEOUT")
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    exchange = ccxt.kraken()
    strategy = BBMeanReversionStrategy(**LIVE_PARAMS)

    print("=" * 70)
    print("BB MEAN REVERSION — Live Config Backtest")
    print(f"  tp_target = opposite  |  adx_max = {LIVE_PARAMS['adx_max']}")
    print(f"  pctb_long <= {LIVE_PARAMS['pctb_long_threshold']}  |  pctb_short >= {LIVE_PARAMS['pctb_short_threshold']}")
    print(f"  stoch_oversold = {LIVE_PARAMS['stoch_oversold']}  |  stoch_overbought = {LIVE_PARAMS['stoch_overbought']}")
    print(f"  {BARS} bars  |  {TIMEFRAME}  |  Kraken")
    print("=" * 70)
    print(f"{'Symbol':12s} {'Trades':>7s} {'WR%':>7s} {'Return%':>9s} {'PF':>7s}  Exits (SL/TP/ADX/STOCH/TO)")
    print("-" * 70)

    grand_total = 0.0
    grand_trades = 0

    for sym in SYMBOLS:
        try:
            df = _fetch(exchange, sym)
            result = _backtest(df, strategy)
            grand_total += result["total"]
            grand_trades += result["trades"]

            marker = " ***" if result["total"] > 4.0 else " ++" if result["total"] > 0 else " --"
            exits = result.get("by_reason", {})
            exit_str = (
                f"SL:{exits.get('SL',0)} TP:{exits.get('TP',0)} "
                f"ADX:{exits.get('ADX',0)} SK:{exits.get('STOCH',0)} TO:{exits.get('TIMEOUT',0)}"
            )
            print(
                f"{result['symbol']:12s}"
                f" {result['trades']:7d}"
                f" {result['wr']:6.0f}%"
                f" {result['total']:+8.2f}%"
                f" {result['pf']:6.1f}x"
                f"  {exit_str}{marker}"
            )
        except Exception as exc:
            print(f"{sym:12s}  ERROR: {exc}")

    print("-" * 70)
    print(f"{'AGGREGATE':12s} {grand_trades:7d}         {grand_total:+8.2f}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
