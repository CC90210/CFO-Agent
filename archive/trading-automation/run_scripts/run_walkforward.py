"""
run_walkforward.py — Walk-forward validation on top crypto strategies.

Validates that multi_timeframe and smart_money aren't overfit.
"""
import asyncio
import logging

from backtesting.walk_forward import WalkForwardValidator
from data.fetcher import MarketDataFetcher
from strategies.technical.multi_timeframe import MultiTimeframeStrategy
from strategies.technical.smart_money import SmartMoneyStrategy

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("atlas.walkforward")
logger.setLevel(logging.INFO)

# Top crypto symbols per strategy
TESTS = [
    ("multi_timeframe", MultiTimeframeStrategy, "4h", [
        "BTC/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "ETH/USDT",
    ]),
    ("smart_money", SmartMoneyStrategy, "4h", [
        "ETH/USDT", "XRP/USDT", "SOL/USDT", "DOGE/USDT",
    ]),
]


async def run_walkforward():
    validator = WalkForwardValidator(
        train_bars=500,
        test_bars=200,
        step_bars=100,
    )

    async with MarketDataFetcher() as fetcher:
        print("=" * 70)
        print("  ATLAS WALK-FORWARD VALIDATION")
        print("=" * 70)

        for strat_name, strat_cls, tf, symbols in TESTS:
            print(f"\n{'-' * 50}")
            print(f"Strategy: {strat_name}")
            print(f"{'-' * 50}")

            for symbol in symbols:
                try:
                    df = await fetcher.fetch_ohlcv(symbol, tf, limit=2000)
                    if len(df) < 700:
                        print(f"  {symbol}: Skip (need 700+ bars, have {len(df)})")
                        continue

                    strategy = strat_cls()
                    result = validator.validate(df, strategy)

                    oos_ret = result.avg_oos_return * 100
                    oos_wr = result.avg_oos_win_rate * 100
                    overfit = result.overfitting_score
                    n_windows = len(result.windows)

                    if overfit < 1.5:
                        fit_status = "OK"
                    elif overfit < 3.0:
                        fit_status = "MODERATE"
                    else:
                        fit_status = "OVERFIT"

                    status = "PASS" if oos_ret > 0 and overfit < 3.0 else "FAIL"

                    print(f"  {symbol}: OOS Return: {oos_ret:+.2f}% | "
                          f"OOS WR: {oos_wr:.1f}% | "
                          f"Overfit: {overfit:.2f} ({fit_status}) | "
                          f"Windows: {n_windows} | {status}")

                except Exception as e:
                    print(f"  {symbol}: ERROR — {e}")

    print("\n" + "=" * 70)
    print("  Overfit Score Guide:")
    print("  < 1.5 = No overfitting (safe to deploy)")
    print("  1.5-3.0 = Moderate (caution)")
    print("  > 3.0 = Severe (do NOT deploy)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_walkforward())
