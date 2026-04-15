"""
Walk-Forward Validation Script for Atlas Top Performers.

Tests whether top-performing strategies generalise or are overfit
by running WalkForwardValidator on 9 months of data.

Strategy-symbol pairs tested:
1. multi_timeframe on BNB/USDT (4h)
2. multi_timeframe on ETH/USDT (4h)
3. ema_crossover on BTC/USDT (4h)
4. bollinger_squeeze on SOL/USDT (1h)
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backtesting.walk_forward import WalkForwardValidator
from data.fetcher import MarketDataFetcher
from strategies.technical.multi_timeframe import MultiTimeframeStrategy
from strategies.technical.ema_crossover import EMACrossoverStrategy
from strategies.technical.bollinger_squeeze import BollingerSqueezeStrategy

import os
os.environ["PYTHONIOENCODING"] = "utf-8"
# Force UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
# Show walk-forward window progress
logging.getLogger("backtesting.walk_forward").setLevel(logging.INFO)


async def fetch_data(symbol: str, timeframe: str, bars: int) -> "pd.DataFrame":
    """Fetch OHLCV data via CCXT (Binance public API, no keys needed)."""
    import pandas as pd

    async with MarketDataFetcher() as fetcher:
        # Calculate 'since' for ~9 months of data
        tf_seconds = {"1h": 3600, "4h": 14400}
        seconds_per_bar = tf_seconds[timeframe]
        import time
        since_ms = int((time.time() - bars * seconds_per_bar) * 1000)

        # CCXT limits to 1000 bars per call typically, so paginate
        all_data = []
        remaining = bars
        current_since = since_ms

        while remaining > 0:
            batch_limit = min(remaining, 1000)
            df = await fetcher.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=batch_limit,
                since=current_since,
            )
            if df.empty:
                break
            all_data.append(df)
            remaining -= len(df)
            # Move since forward past last fetched candle
            last_ts = int(df.index[-1].timestamp() * 1000) + (seconds_per_bar * 1000)
            current_since = last_ts

        if all_data:
            result = pd.concat(all_data).sort_index()
            result = result[~result.index.duplicated(keep="last")]
            return result
        return pd.DataFrame()


def run_validation(df, strategy, label: str, train_bars: int, test_bars: int, step_bars: int):
    """Run walk-forward validation and print results."""
    print(f"\n{'='*66}")
    print(f"  VALIDATING: {label}")
    print(f"  Data: {len(df)} bars, {df.index[0].date()} -> {df.index[-1].date()}")
    print(f"  Train/Test/Step: {train_bars}/{test_bars}/{step_bars} bars")
    print(f"{'='*66}")

    validator = WalkForwardValidator(
        train_bars=train_bars,
        test_bars=test_bars,
        step_bars=step_bars,
        initial_capital=10_000.0,
        commission_pct=0.001,
    )

    # Custom validate that forces scale_out_tiers=[]
    def patched_validate(df, strategy):
        from backtesting.engine import BacktestEngine
        validator_self = validator

        # Override the engine that gets created inside validate()
        result_df = df.sort_index().copy()
        n = len(result_df)
        window_size = validator_self.train_bars + validator_self.test_bars

        if n < window_size:
            raise ValueError(
                f"DataFrame has only {n} rows but train_bars + test_bars = {window_size}."
            )

        engine = BacktestEngine(
            initial_capital=validator_self.initial_capital,
            commission_pct=validator_self.commission_pct,
            regime_filter=True,
            scale_out_tiers=[],  # CRITICAL: no scale-out
        )

        from backtesting.walk_forward import WalkForwardWindow, _to_dt
        windows = []
        window_id = 0
        start = 0

        while start + window_size <= n:
            train_slice = result_df.iloc[start: start + validator_self.train_bars]
            test_slice = result_df.iloc[start + validator_self.train_bars: start + window_size]

            train_result = engine.run(train_slice, strategy)
            test_result = engine.run(test_slice, strategy)

            windows.append(
                WalkForwardWindow(
                    window_id=window_id,
                    train_start=_to_dt(train_slice.index[0]),
                    train_end=_to_dt(train_slice.index[-1]),
                    test_start=_to_dt(test_slice.index[0]),
                    test_end=_to_dt(test_slice.index[-1]),
                    train_return=train_result.total_return,
                    test_return=test_result.total_return,
                    train_win_rate=train_result.win_rate,
                    test_win_rate=test_result.win_rate,
                    train_pf=train_result.profit_factor,
                    test_pf=test_result.profit_factor,
                    train_trades=train_result.total_trades,
                    test_trades=test_result.total_trades,
                )
            )
            window_id += 1
            start += validator_self.step_bars

        if not windows:
            raise RuntimeError("No walk-forward windows could be constructed.")

        return validator_self._aggregate(strategy.name, windows)

    result = patched_validate(df, strategy)
    report = validator.summary(result)
    print(report)

    # Flag overfitting
    if result.overfitting_score > 0.7:
        print(f"\n  *** OVERFITTING ALERT: Score {result.overfitting_score:.3f} > 0.7 ***")
        print(f"  *** This strategy may be curve-fit. DO NOT deploy without further validation. ***\n")

    return result


async def main():
    import pandas as pd

    # Define test cases
    test_cases = [
        {
            "symbol": "BNB/USDT",
            "timeframe": "4h",
            "strategy": MultiTimeframeStrategy(atr_stop_mult=3.0, rr_ratio=4.0),
            "label": "multi_timeframe on BNB/USDT (4h)",
            "bars_needed": 1650,  # ~9 months of 4h data
            "train_bars": 500,
            "test_bars": 300,   # needs 205+ bars for EMA(200) warmup
            "step_bars": 150,
        },
        {
            "symbol": "ETH/USDT",
            "timeframe": "4h",
            "strategy": MultiTimeframeStrategy(atr_stop_mult=3.0, rr_ratio=4.0),
            "label": "multi_timeframe on ETH/USDT (4h)",
            "bars_needed": 1650,
            "train_bars": 500,
            "test_bars": 300,   # needs 205+ bars for EMA(200) warmup
            "step_bars": 150,
        },
        {
            "symbol": "BTC/USDT",
            "timeframe": "4h",
            "strategy": EMACrossoverStrategy(atr_stop_mult=3.0, rr_ratio=4.0, adx_threshold=20.0),
            "label": "ema_crossover on BTC/USDT (4h)",
            "bars_needed": 1650,
            "train_bars": 500,
            "test_bars": 150,
            "step_bars": 75,
        },
        {
            "symbol": "SOL/USDT",
            "timeframe": "1h",
            "strategy": BollingerSqueezeStrategy(
                atr_stop_mult=3.0, atr_tp_mult=6.0,
                squeeze_percentile=10.0, exhaustion_vol_mult=2.0,
            ),
            "label": "bollinger_squeeze on SOL/USDT (1h)",
            "bars_needed": 6600,  # ~9 months of 1h data
            "train_bars": 2000,
            "test_bars": 500,
            "step_bars": 250,
        },
    ]

    results = []

    for tc in test_cases:
        print(f"\n>>> Fetching {tc['bars_needed']} bars of {tc['symbol']} {tc['timeframe']}...")
        df = await fetch_data(tc["symbol"], tc["timeframe"], tc["bars_needed"])

        if df.empty or len(df) < tc["train_bars"] + tc["test_bars"]:
            print(f"  ERROR: Only got {len(df)} bars, need {tc['train_bars'] + tc['test_bars']}. Skipping.")
            continue

        print(f"  Fetched {len(df)} bars: {df.index[0]} -> {df.index[-1]}")

        result = run_validation(
            df, tc["strategy"], tc["label"],
            tc["train_bars"], tc["test_bars"], tc["step_bars"],
        )
        results.append((tc["label"], result))

    # Summary table
    print("\n" + "=" * 80)
    print("  WALK-FORWARD VALIDATION SUMMARY")
    print("=" * 80)
    print(f"  {'Strategy':<42} {'OOS Ret':>8} {'OOS WR':>7} {'Overfit':>8} {'Verdict':>16}")
    print("  " + "-" * 78)
    for label, r in results:
        flag = " *** OVERFIT ***" if r.overfitting_score > 0.7 else ""
        print(
            f"  {label:<42} "
            f"{r.avg_oos_return * 100:>+7.2f}% "
            f"{r.avg_oos_win_rate * 100:>6.1f}% "
            f"{r.overfitting_score:>8.3f} "
            f"{r.recommendation:>16}{flag}"
        )
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
