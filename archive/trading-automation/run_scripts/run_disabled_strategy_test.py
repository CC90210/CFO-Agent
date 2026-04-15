"""
run_disabled_strategy_test.py — Disabled Strategy Resurrection Test

Fetches live Kraken OHLCV data and backtests every disabled crypto-capable strategy
across multiple symbols and parameter profiles (conservative / aggressive / daredevil).

Strategies tested (crypto-capable, disabled as of 2026-03-20):
    rsi_mean_reversion, ema_crossover, bollinger_squeeze, vwap_bounce,
    ichimoku_trend, order_flow_imbalance, zscore_mean_reversion, volume_profile,
    momentum_exhaustion, grid_dca, pairs_mean_reversion

Strategies explicitly excluded (no Kraken data available):
    london_breakout, opening_range, equity_mean_reversion, forex_session_momentum,
    gold_trend_follower, ibs_mean_reversion, stock_gap_fade, connors_rsi,
    sector_rotation, forex_carry_momentum

Usage:
    python run_disabled_strategy_test.py

Output: ranked table of every combo, then resurrection candidates (return > 0 AND
        total_trades >= 3) sorted by total return descending.
"""

from __future__ import annotations

import sys
import time
import traceback
from dataclasses import dataclass

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

import ccxt  # type: ignore[import]
import pandas as pd

# --- Atlas imports ---
from backtesting.engine import BacktestEngine
from strategies.technical.rsi_mean_reversion import RSIMeanReversionStrategy
from strategies.technical.ema_crossover import EMACrossoverStrategy
from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy
from strategies.technical.vwap_bounce import VWAPBounceStrategy
from strategies.technical.ichimoku_trend import IchimokuTrendStrategy
from strategies.technical.order_flow_imbalance import OrderFlowImbalanceStrategy
from strategies.technical.zscore_mean_reversion import ZScoreMeanReversionStrategy
from strategies.technical.volume_profile import VolumeProfileStrategy
from strategies.technical.momentum_exhaustion import MomentumExhaustionStrategy
from strategies.technical.grid_dca import GridDCAStrategy
from strategies.technical.pairs_mean_reversion import PairsMeanReversionStrategy

# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

_exchange = ccxt.kraken({"enableRateLimit": True})

_DATA_CACHE: dict[tuple[str, str, int], pd.DataFrame] = {}


def fetch_ohlcv(symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame | None:
    """Fetch OHLCV from Kraken and return a DataFrame, or None on failure."""
    cache_key = (symbol, timeframe, limit)
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key]

    try:
        raw = _exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not raw:
            return None
        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        df.attrs["symbol"] = symbol
        _DATA_CACHE[cache_key] = df
        time.sleep(0.3)  # gentle rate-limit respect
        return df
    except Exception as exc:
        print(f"  [FETCH ERROR] {symbol} {timeframe}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Strategy parameter profiles
# ---------------------------------------------------------------------------

STRATEGIES: dict[str, list[tuple[str, object]]] = {
    # ------------------------------------------------------------------
    # RSI Mean Reversion — relax ADX and RSI thresholds progressively
    # ------------------------------------------------------------------
    "rsi_mean_reversion": [
        ("conservative", RSIMeanReversionStrategy(
            rsi_oversold=30.0, rsi_overbought=70.0,
            adx_max=30.0, atr_stop_mult=1.0, volume_mult=1.2, rr_min=2.0,
        )),
        ("aggressive", RSIMeanReversionStrategy(
            rsi_oversold=35.0, rsi_overbought=65.0,
            adx_max=35.0, atr_stop_mult=1.2, volume_mult=1.0, rr_min=1.5,
        )),
        ("daredevil", RSIMeanReversionStrategy(
            rsi_oversold=40.0, rsi_overbought=60.0,
            adx_max=40.0, atr_stop_mult=1.5, volume_mult=0.8, rr_min=1.5,
            ema_trend_period=50,  # shorter trend filter
        )),
    ],

    # ------------------------------------------------------------------
    # EMA Crossover — vary ADX threshold and R:R
    # ------------------------------------------------------------------
    "ema_crossover": [
        ("conservative", EMACrossoverStrategy(
            adx_threshold=25.0, atr_stop_mult=2.0, rr_ratio=3.0,
        )),
        ("aggressive", EMACrossoverStrategy(
            adx_threshold=18.0, atr_stop_mult=2.5, rr_ratio=4.0,
        )),
        ("daredevil", EMACrossoverStrategy(
            fast_period=8, slow_period=21,
            adx_threshold=15.0, atr_stop_mult=1.5, rr_ratio=3.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Bollinger Squeeze — vary squeeze sensitivity and ATR multiples
    # ------------------------------------------------------------------
    "bollinger_squeeze": [
        ("conservative", BollingerSqueezeStrategy(
            squeeze_percentile=15.0, atr_stop_mult=2.0, atr_tp_mult=4.0,
        )),
        ("aggressive", BollingerSqueezeStrategy(
            squeeze_percentile=20.0, atr_stop_mult=1.5, atr_tp_mult=5.0,
            exhaustion_vol_mult=3.0,  # allow higher volume on breakout
        )),
        ("daredevil", BollingerSqueezeStrategy(
            squeeze_percentile=25.0, atr_stop_mult=1.0, atr_tp_mult=6.0,
            exhaustion_vol_mult=4.0,
        )),
    ],

    # ------------------------------------------------------------------
    # VWAP Bounce — wider touch tolerance, 24-hour active hours for crypto
    # ------------------------------------------------------------------
    "vwap_bounce": [
        ("conservative", VWAPBounceStrategy(
            vwap_touch_pct=0.002, atr_stop_mult=1.0, atr_tp_mult=1.5,
            volume_mult=1.2,
            active_hours_utc=[(0, 23)],  # crypto 24/7
        )),
        ("aggressive", VWAPBounceStrategy(
            vwap_touch_pct=0.004, atr_stop_mult=1.0, atr_tp_mult=2.0,
            volume_mult=1.0,
            active_hours_utc=[(0, 23)],
        )),
        ("daredevil", VWAPBounceStrategy(
            vwap_touch_pct=0.008, atr_stop_mult=0.8, atr_tp_mult=2.0,
            volume_mult=0.8,
            active_hours_utc=[(0, 23)],
        )),
    ],

    # ------------------------------------------------------------------
    # Ichimoku Trend — tighter periods for faster crypto markets
    # ------------------------------------------------------------------
    "ichimoku_trend": [
        ("conservative", IchimokuTrendStrategy(
            tenkan_period=9, kijun_period=26, senkou_b_period=52,
            displacement=26, rr_ratio=3.0,
        )),
        ("aggressive", IchimokuTrendStrategy(
            tenkan_period=7, kijun_period=22, senkou_b_period=44,
            displacement=22, rr_ratio=3.5,
        )),
        ("daredevil", IchimokuTrendStrategy(
            tenkan_period=5, kijun_period=13, senkou_b_period=26,
            displacement=13, rr_ratio=4.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Order Flow Imbalance — relax ADX and volume gates
    # ------------------------------------------------------------------
    "order_flow_imbalance": [
        ("conservative", OrderFlowImbalanceStrategy(
            adx_max=35.0, atr_stop_mult=1.5, rr_ratio=2.5,
            volume_mult=1.2, cvd_window=15,
        )),
        ("aggressive", OrderFlowImbalanceStrategy(
            adx_max=40.0, atr_stop_mult=1.2, rr_ratio=2.0,
            volume_mult=1.0, cvd_window=10,
        )),
        ("daredevil", OrderFlowImbalanceStrategy(
            adx_max=45.0, atr_stop_mult=1.0, rr_ratio=2.0,
            volume_mult=0.8, cvd_window=8,
            exhaustion_mult=5.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Z-Score Mean Reversion — relax entry z-scores and HTF gate
    # ------------------------------------------------------------------
    "zscore_mean_reversion": [
        ("conservative", ZScoreMeanReversionStrategy(
            zscore_entry=1.5, zscore_htf_entry=0.8, adx_max=35.0,
            volume_mult=1.2, atr_stop_mult=2.0,
        )),
        ("aggressive", ZScoreMeanReversionStrategy(
            zscore_entry=1.2, zscore_htf_entry=0.5, adx_max=40.0,
            volume_mult=1.0, atr_stop_mult=1.5,
        )),
        ("daredevil", ZScoreMeanReversionStrategy(
            zscore_period=30, zscore_entry=1.0, zscore_htf_entry=0.3,
            adx_max=45.0, volume_mult=0.8, atr_stop_mult=1.5,
            rsi_oversold=35.0, rsi_overbought=65.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Volume Profile — longer timeframe (use 4h data) and relaxed ADX
    # ------------------------------------------------------------------
    "volume_profile": [
        ("conservative", VolumeProfileStrategy(
            profile_window=100, adx_min_trend=15.0,
            atr_stop_mult=1.5, volume_mult=1.5, breakout_vol_mult=2.0,
            min_rr=2.0,
        )),
        ("aggressive", VolumeProfileStrategy(
            profile_window=80, adx_min_trend=12.0,
            atr_stop_mult=1.2, volume_mult=1.2, breakout_vol_mult=1.8,
            min_rr=1.5, min_distance_atr=0.5,
        )),
        ("daredevil", VolumeProfileStrategy(
            profile_window=60, adx_min_trend=10.0,
            atr_stop_mult=1.0, volume_mult=1.0, breakout_vol_mult=1.5,
            min_rr=1.5, min_distance_atr=0.3, rsi_oversold=35.0, rsi_overbought=65.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Momentum Exhaustion — relax ADX and move threshold
    # ------------------------------------------------------------------
    "momentum_exhaustion": [
        ("conservative", MomentumExhaustionStrategy(
            adx_max=30.0, move_atr_mult=1.5, volume_mult=1.2,
            atr_stop_mult=1.5, rr_ratio=2.0,
        )),
        ("aggressive", MomentumExhaustionStrategy(
            adx_max=35.0, move_atr_mult=1.2, volume_mult=1.0,
            atr_stop_mult=1.2, rr_ratio=2.0, reversal_body_pct=0.20,
        )),
        ("daredevil", MomentumExhaustionStrategy(
            adx_max=40.0, move_atr_mult=1.0, volume_mult=0.8,
            atr_stop_mult=1.0, rr_ratio=2.5, reversal_body_pct=0.15,
            rsi_oversold=35.0, rsi_overbought=65.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Grid/DCA — wider ADX gate, more grid levels
    # ------------------------------------------------------------------
    "grid_dca": [
        ("conservative", GridDCAStrategy(
            adx_max=25.0, grid_atr_mult=1.0, grid_levels=3,
            rr_ratio=1.5, volume_mult=0.8,
        )),
        ("aggressive", GridDCAStrategy(
            adx_max=30.0, grid_atr_mult=0.8, grid_levels=4,
            rr_ratio=2.0, volume_mult=0.6,
        )),
        ("daredevil", GridDCAStrategy(
            adx_max=35.0, grid_atr_mult=0.5, grid_levels=5,
            rr_ratio=2.0, volume_mult=0.5,
            atr_stop_mult=1.0,
        )),
    ],

    # ------------------------------------------------------------------
    # Pairs Mean Reversion — relax z-score and RSI gates
    # ------------------------------------------------------------------
    "pairs_mean_reversion": [
        ("conservative", PairsMeanReversionStrategy(
            zscore_entry=1.8, adx_max=35.0,
            rsi_oversold=38.0, rsi_overbought=62.0,
            volume_mult=1.0, atr_stop_mult=1.5,
        )),
        ("aggressive", PairsMeanReversionStrategy(
            zscore_entry=1.5, adx_max=40.0,
            rsi_oversold=42.0, rsi_overbought=58.0,
            volume_mult=0.8, atr_stop_mult=1.2,
            bb_touch_pct=0.10,
        )),
        ("daredevil", PairsMeanReversionStrategy(
            zscore_period=30, zscore_entry=1.2, adx_max=45.0,
            rsi_oversold=45.0, rsi_overbought=55.0,
            volume_mult=0.6, atr_stop_mult=1.0,
            bb_touch_pct=0.15,
        )),
    ],
}

# ---------------------------------------------------------------------------
# Timeframes per strategy (matches strategy design intent)
# ---------------------------------------------------------------------------

STRATEGY_TIMEFRAMES: dict[str, str] = {
    "rsi_mean_reversion":   "1h",
    "ema_crossover":        "4h",
    "bollinger_squeeze":    "4h",   # upgraded from 1h per strategy design (4h better)
    "vwap_bounce":          "15m",
    "ichimoku_trend":       "4h",
    "order_flow_imbalance": "1h",
    "zscore_mean_reversion": "1h",
    "volume_profile":       "4h",   # upgraded from 1h per strategy design
    "momentum_exhaustion":  "1h",
    "grid_dca":             "1h",
    "pairs_mean_reversion": "1h",
}

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "DOGE/USDT",
    "XRP/USDT",
    "DOT/USDT",
    "ADA/USDT",
    "AVAX/USDT",
]

# ---------------------------------------------------------------------------
# Result record
# ---------------------------------------------------------------------------


@dataclass
class TestResult:
    strategy: str
    profile: str
    symbol: str
    timeframe: str
    total_return: float
    win_rate: float
    sharpe: float
    max_drawdown: float
    total_trades: int
    profit_factor: float


# ---------------------------------------------------------------------------
# Main test loop
# ---------------------------------------------------------------------------


def run_all() -> list[TestResult]:
    engine = BacktestEngine(
        initial_capital=10_000,
        commission_pct=0.001,
        regime_filter=True,
        trailing_stops=False,
        scale_out_tiers=[],  # disabled — empirically shown to hurt returns
    )

    results: list[TestResult] = []
    total_combos = sum(
        len(profiles) * len(SYMBOLS) for profiles in STRATEGIES.values()
    )
    done = 0

    print(f"\nAtlas disabled-strategy resurrection test")
    print(f"Symbols: {', '.join(SYMBOLS)}")
    print(f"Total combinations: {total_combos}")
    print("=" * 100)

    for strategy_name, profiles in STRATEGIES.items():
        timeframe = STRATEGY_TIMEFRAMES[strategy_name]
        print(f"\n{'─' * 100}")
        print(f"  STRATEGY: {strategy_name.upper()}  ({timeframe})")
        print(f"{'─' * 100}")

        for profile_name, strategy_obj in profiles:
            print(f"\n  Profile: {profile_name}")

            for symbol in SYMBOLS:
                done += 1
                progress = f"[{done}/{total_combos}]"

                # Fetch data — use 600 bars for strategies needing warm-up headroom
                limit = 600
                df = fetch_ohlcv(symbol, timeframe, limit=limit)

                if df is None or len(df) < 100:
                    print(f"    {progress} {symbol:<12} SKIP (insufficient data)")
                    continue

                try:
                    result = engine.run(df, strategy_obj)
                except Exception as exc:
                    print(f"    {progress} {symbol:<12} ERROR: {exc}")
                    traceback.print_exc()
                    continue

                ret_pct = result.total_return * 100
                wr_pct = result.win_rate * 100
                mdd_pct = result.max_drawdown * 100
                pf = result.profit_factor

                flag = ""
                if result.total_return > 0 and result.total_trades >= 3:
                    flag = "  <-- CANDIDATE"
                elif result.total_trades == 0:
                    flag = "  (0 trades)"

                print(
                    f"    {progress} {symbol:<12} "
                    f"Return: {ret_pct:>+7.2f}%  "
                    f"WR: {wr_pct:>5.1f}%  "
                    f"Sharpe: {result.sharpe_ratio:>6.2f}  "
                    f"MDD: {mdd_pct:>+7.2f}%  "
                    f"Trades: {result.total_trades:>3}  "
                    f"PF: {pf:>5.2f}"
                    f"{flag}"
                )

                results.append(TestResult(
                    strategy=strategy_name,
                    profile=profile_name,
                    symbol=symbol,
                    timeframe=timeframe,
                    total_return=result.total_return,
                    win_rate=result.win_rate,
                    sharpe=result.sharpe_ratio,
                    max_drawdown=result.max_drawdown,
                    total_trades=result.total_trades,
                    profit_factor=pf,
                ))

    return results


def print_summary(results: list[TestResult]) -> None:
    """Print ranked resurrection candidates and final summary tables."""

    print("\n\n" + "=" * 100)
    print("  RESURRECTION CANDIDATES  (return > 0%, trades >= 3)")
    print("=" * 100)

    candidates = [
        r for r in results
        if r.total_return > 0.0 and r.total_trades >= 3
    ]
    candidates.sort(key=lambda r: r.total_return, reverse=True)

    if not candidates:
        print("  None found. All disabled strategies remain unviable on live Kraken data.")
    else:
        print(
            f"  {'Strategy':<26} {'Profile':<14} {'Symbol':<12} {'TF':<5} "
            f"{'Return':>8} {'WR':>6} {'Sharpe':>8} {'MDD':>8} {'Trades':>7} {'PF':>6}"
        )
        print("  " + "-" * 98)
        for r in candidates:
            print(
                f"  {r.strategy:<26} {r.profile:<14} {r.symbol:<12} {r.timeframe:<5} "
                f"{r.total_return * 100:>+7.2f}%  "
                f"{r.win_rate * 100:>5.1f}%  "
                f"{r.sharpe:>7.2f}  "
                f"{r.max_drawdown * 100:>+7.2f}%  "
                f"{r.total_trades:>6}  "
                f"{r.profit_factor:>5.2f}"
            )

    print("\n\n" + "=" * 100)
    print("  BEST PROFILE PER STRATEGY  (highest avg return across all symbols)")
    print("=" * 100)

    from collections import defaultdict
    strategy_profile_returns: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in results:
        strategy_profile_returns[r.strategy][r.profile].append(r.total_return)

    print(
        f"  {'Strategy':<26} {'Best profile':<14} {'Avg return':>10} "
        f"{'Symbols > 0':>12} {'Avg trades':>11}"
    )
    print("  " + "-" * 78)

    for strategy_name in STRATEGIES:
        if strategy_name not in strategy_profile_returns:
            continue
        best_profile = ""
        best_avg = -float("inf")
        for profile_name, rets in strategy_profile_returns[strategy_name].items():
            avg = sum(rets) / len(rets) if rets else 0.0
            if avg > best_avg:
                best_avg = avg
                best_profile = profile_name

        # Stats for best profile
        profile_results = [
            r for r in results
            if r.strategy == strategy_name and r.profile == best_profile
        ]
        positive = sum(1 for r in profile_results if r.total_return > 0)
        avg_trades = (
            sum(r.total_trades for r in profile_results) / len(profile_results)
            if profile_results else 0
        )

        verdict = "VIABLE" if best_avg > 0 and avg_trades >= 3 else "NOT VIABLE"
        print(
            f"  {strategy_name:<26} {best_profile:<14} {best_avg * 100:>+9.2f}%  "
            f"{positive:>4}/{len(profile_results):<4}  "
            f"{avg_trades:>8.1f} trades   [{verdict}]"
        )

    print("\n" + "=" * 100)
    print("  VERDICT")
    print("=" * 100)
    viable = [
        s for s in STRATEGIES
        if s in strategy_profile_returns and any(
            sum(v) / len(v) > 0
            for v in strategy_profile_returns[s].values()
            if len(v) > 0
        )
    ]
    if viable:
        print(f"  Strategies worth resurrecting: {', '.join(viable)}")
    else:
        print("  No strategies meet resurrection criteria on live Kraken data.")
    print("=" * 100)


if __name__ == "__main__":
    results = run_all()
    print_summary(results)
