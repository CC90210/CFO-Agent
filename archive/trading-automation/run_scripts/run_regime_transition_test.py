"""
run_regime_transition_test.py — Regime Transition Analysis for Atlas

Walks through historical data candle-by-candle, detects every regime change,
and measures:
  1. How often regime transitions happen (avg days between changes)
  2. False-positive rate (transitions that reverse within 24h / 6 candles on 4h)
  3. Best strategy to deploy at BEAR->CHOPPY transition
  4. Best strategy to deploy at CHOPPY->BULL transition
  5. Average signal delay after regime change (candles until first valid signal)

Uses /USD pairs on Kraken via CCXT (Ontario-compliant).

Usage:
    python run_regime_transition_test.py
"""
import asyncio
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd

from core.regime_detector import MarketRegime, RegimeDetector
from data.fetcher import MarketDataFetcher
from strategies.base import BaseStrategy, Direction, StrategyRegistry

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas.regime_transition")
logger.setLevel(logging.INFO)

# ── Configuration ──────────────────────────────────────────────────────────

SYMBOLS = ["BTC/USD", "ETH/USD", "SOL/USD"]
TIMEFRAME = "4h"
CANDLE_LIMIT = 1000
CANDLE_HOURS = 4
POST_TRANSITION_WINDOW = 10  # candles after transition to measure signals / PnL

# Strategies to test (4h crypto-compatible)
STRATEGY_NAMES = [
    "rsi_mean_reversion",
    "ema_crossover",
    "bollinger_squeeze",
    "multi_timeframe",
    "smart_money",
    "ichimoku_trend",
    "donchian_breakout",
]


@dataclass
class RegimeChange:
    timestamp: pd.Timestamp
    symbol: str
    from_regime: MarketRegime
    to_regime: MarketRegime
    candle_index: int
    confidence: float
    sharpe: float
    adx: float
    vol_ratio: float
    reversed_within_24h: bool = False
    forward_return_10bar: float = 0.0  # % return in next 10 candles


def load_strategies() -> dict[str, BaseStrategy]:
    StrategyRegistry.discover()
    strategies = {}
    for name in STRATEGY_NAMES:
        try:
            strategies[name] = StrategyRegistry.build(name)
        except Exception as e:
            logger.warning("Could not load strategy %s: %s", name, e)
    return strategies


def walk_regimes(df: pd.DataFrame, detector: RegimeDetector, symbol: str) -> list[RegimeChange]:
    """Walk candle-by-candle, detect regime changes, compute forward returns."""
    changes: list[RegimeChange] = []
    prev_regime = None
    min_bars = 30

    for i in range(min_bars, len(df)):
        visible = df.iloc[max(0, i - 499):i + 1]
        result = detector.detect(visible)

        if prev_regime is not None and result.regime != prev_regime:
            # Forward return: price change over next 10 candles
            fwd_end = min(i + POST_TRANSITION_WINDOW, len(df) - 1)
            entry_price = df.iloc[i]["close"]
            exit_price = df.iloc[fwd_end]["close"]
            fwd_return = (exit_price - entry_price) / entry_price * 100

            changes.append(RegimeChange(
                timestamp=df.index[i],
                symbol=symbol,
                from_regime=prev_regime,
                to_regime=result.regime,
                candle_index=i,
                confidence=result.confidence,
                sharpe=result.rolling_sharpe,
                adx=result.adx,
                vol_ratio=result.volatility_ratio,
                forward_return_10bar=fwd_return,
            ))

        prev_regime = result.regime

    # Mark false positives (regime reverts within 6 candles = 24h on 4h TF)
    for j, change in enumerate(changes):
        for k in range(j + 1, len(changes)):
            next_change = changes[k]
            candles_between = next_change.candle_index - change.candle_index
            if candles_between <= 6:
                if next_change.to_regime == change.from_regime:
                    change.reversed_within_24h = True
                break
            else:
                break

    return changes


def check_signals_at_transitions(
    df: pd.DataFrame,
    changes: list[RegimeChange],
    strategies: dict[str, BaseStrategy],
    detector: RegimeDetector,
) -> dict[str, dict[str, list]]:
    """
    For each transition, check which strategies signal in the next 10 candles.
    Returns: {transition_type: {strategy_name: [list of (candles_after, direction, conviction, regime_weight)]}}
    """
    results: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

    for c in changes:
        if c.reversed_within_24h:
            continue  # Skip false positives for signal analysis

        trans_key = f"{c.from_regime.value}->{c.to_regime.value}"
        start_idx = c.candle_index
        end_idx = min(start_idx + POST_TRANSITION_WINDOW, len(df) - 1)

        # Get regime weights for the new regime
        visible_at_change = df.iloc[max(0, start_idx - 499):start_idx + 1]
        result = detector.detect(visible_at_change)
        weights = result.strategy_weights()

        for candle_offset in range(1, end_idx - start_idx + 1):
            idx = start_idx + candle_offset
            visible = df.iloc[max(0, idx - 499):idx + 1]

            for strat_name, strategy in strategies.items():
                regime_weight = weights.get(strat_name, 1.0)
                try:
                    if strategy.should_enter(visible):
                        signal = strategy.analyze(visible)
                        if signal is not None and signal.direction != Direction.FLAT:
                            results[trans_key][strat_name].append({
                                "candles_after": candle_offset,
                                "direction": signal.direction.value,
                                "conviction": signal.conviction,
                                "regime_weight": regime_weight,
                                "symbol": c.symbol,
                                "timestamp": c.timestamp,
                            })
                except Exception:
                    pass

    return results


def run_strategy_pnl_at_transitions(
    df: pd.DataFrame,
    changes: list[RegimeChange],
    strategies: dict[str, BaseStrategy],
    detector: RegimeDetector,
) -> dict[str, dict[str, list[float]]]:
    """
    Simplified PnL: for each signal generated in the post-transition window,
    check the price movement from signal entry to 5 candles later.
    Returns: {transition_type: {strategy_name: [list of pnl_pct]}}
    """
    results: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for c in changes:
        if c.reversed_within_24h:
            continue

        trans_key = f"{c.from_regime.value}->{c.to_regime.value}"
        start_idx = c.candle_index
        end_idx = min(start_idx + POST_TRANSITION_WINDOW, len(df) - 1)

        visible_at_change = df.iloc[max(0, start_idx - 499):start_idx + 1]
        result = detector.detect(visible_at_change)
        weights = result.strategy_weights()

        for candle_offset in range(1, end_idx - start_idx + 1):
            idx = start_idx + candle_offset
            visible = df.iloc[max(0, idx - 499):idx + 1]
            exit_idx = min(idx + 5, len(df) - 1)  # 5-candle hold

            for strat_name, strategy in strategies.items():
                regime_weight = weights.get(strat_name, 1.0)
                if regime_weight <= 0.5:
                    continue  # Regime suppresses this strategy
                try:
                    if strategy.should_enter(visible):
                        signal = strategy.analyze(visible)
                        if signal is not None and signal.direction != Direction.FLAT and abs(signal.conviction) >= 0.3:
                            entry_price = df.iloc[idx]["close"]
                            exit_price = df.iloc[exit_idx]["close"]
                            if signal.direction == Direction.LONG:
                                pnl = (exit_price - entry_price) / entry_price * 100
                            else:
                                pnl = (entry_price - exit_price) / entry_price * 100
                            results[trans_key][strat_name].append(pnl)
                except Exception:
                    pass

    return results


async def main():
    logger.info("=" * 70)
    logger.info("  ATLAS -- Regime Transition Analysis")
    logger.info("  Symbols: %s | Timeframe: %s | Candles: %d", SYMBOLS, TIMEFRAME, CANDLE_LIMIT)
    logger.info("=" * 70)

    detector = RegimeDetector()
    strategies = load_strategies()
    logger.info("Loaded %d strategies: %s", len(strategies), list(strategies.keys()))

    all_changes: list[RegimeChange] = []
    symbol_data: dict[str, pd.DataFrame] = {}

    # ── Fetch data ─────────────────────────────────────────────────────────
    async with MarketDataFetcher() as fetcher:
        for symbol in SYMBOLS:
            logger.info("Fetching %s %s (%d candles)...", symbol, TIMEFRAME, CANDLE_LIMIT)
            try:
                df = await fetcher.fetch_ohlcv(symbol, TIMEFRAME, limit=CANDLE_LIMIT)
                if len(df) < 200:
                    logger.warning("Insufficient data for %s: %d bars", symbol, len(df))
                    continue
                symbol_data[symbol] = df
                logger.info("  Got %d candles: %s to %s", len(df), df.index[0], df.index[-1])
            except Exception as e:
                logger.error("Failed to fetch %s: %s", symbol, e)

    if not symbol_data:
        logger.error("No data fetched. Exiting.")
        return

    # ── Walk regimes for each symbol ───────────────────────────────────────
    for symbol, df in symbol_data.items():
        logger.info("\n" + "-" * 70)
        logger.info("REGIME WALK: %s (%d candles)", symbol, len(df))
        logger.info("-" * 70)

        changes = walk_regimes(df, detector, symbol)
        all_changes.extend(changes)

        logger.info("Found %d regime changes for %s:", len(changes), symbol)
        for c in changes:
            fp_tag = " [FALSE POSITIVE]" if c.reversed_within_24h else ""
            logger.info(
                "  %s  %-12s -> %-12s  (conf=%.2f sharpe=%+.2f adx=%.0f vol_r=%.2f fwd10=%.2f%%)%s",
                c.timestamp.strftime("%Y-%m-%d %H:%M"),
                c.from_regime.value, c.to_regime.value,
                c.confidence, c.sharpe, c.adx, c.vol_ratio,
                c.forward_return_10bar, fp_tag,
            )

    # ── Check signals at transitions ───────────────────────────────────────
    logger.info("\nChecking strategy signals at transitions...")
    all_signal_data: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    all_pnl_data: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for symbol, df in symbol_data.items():
        sym_changes = [c for c in all_changes if c.symbol == symbol]
        sig_data = check_signals_at_transitions(df, sym_changes, strategies, detector)
        pnl_data = run_strategy_pnl_at_transitions(df, sym_changes, strategies, detector)

        for trans_type, strat_signals in sig_data.items():
            for strat_name, signals in strat_signals.items():
                all_signal_data[trans_type][strat_name].extend(signals)

        for trans_type, strat_pnls in pnl_data.items():
            for strat_name, pnls in strat_pnls.items():
                all_pnl_data[trans_type][strat_name].extend(pnls)

    # ══════════════════════════════════════════════════════════════════════
    #  RESULTS
    # ══════════════════════════════════════════════════════════════════════
    logger.info("\n" + "=" * 70)
    logger.info("  REGIME TRANSITION ANALYSIS -- RESULTS")
    logger.info("=" * 70)

    if not all_changes:
        logger.info("No regime changes detected.")
        return

    # ── 1. Transition frequency ────────────────────────────────────────────
    logger.info("\n-- 1. TRANSITION FREQUENCY --")
    for symbol in SYMBOLS:
        sym_changes = [c for c in all_changes if c.symbol == symbol]
        if len(sym_changes) >= 2:
            durations = []
            for i in range(1, len(sym_changes)):
                delta = sym_changes[i].timestamp - sym_changes[i - 1].timestamp
                durations.append(delta.total_seconds() / 86400)
            logger.info(
                "  %s: %d transitions | avg %.1f days | median %.1f | min %.1f | max %.1f",
                symbol, len(sym_changes), np.mean(durations), np.median(durations),
                np.min(durations), np.max(durations),
            )

    all_durations = []
    for symbol in SYMBOLS:
        sym_changes = [c for c in all_changes if c.symbol == symbol]
        for i in range(1, len(sym_changes)):
            delta = sym_changes[i].timestamp - sym_changes[i - 1].timestamp
            all_durations.append(delta.total_seconds() / 86400)
    if all_durations:
        logger.info(
            "  OVERALL: avg %.1f days between transitions | total %d transitions across %d symbols",
            np.mean(all_durations), len(all_changes), len(symbol_data),
        )

    # ── 2. False positive rate ─────────────────────────────────────────────
    logger.info("\n-- 2. FALSE POSITIVE RATE (reversal within 24h / 6 candles) --")
    total = len(all_changes)
    fps = sum(1 for c in all_changes if c.reversed_within_24h)
    logger.info("  %d / %d = %.1f%% of transitions reverse within 24h", fps, total, fps / total * 100)

    transition_types: dict[str, list[RegimeChange]] = defaultdict(list)
    for c in all_changes:
        transition_types[f"{c.from_regime.value} -> {c.to_regime.value}"].append(c)

    logger.info("\n  By transition type:")
    logger.info("  %-35s  %5s  %5s  %6s  %10s", "Transition", "Count", "FP", "FP%", "Avg Fwd10%")
    for ttype in sorted(transition_types.keys()):
        changes_list = transition_types[ttype]
        fp_count = sum(1 for c in changes_list if c.reversed_within_24h)
        # Only count non-FP forward returns
        stable_fwd = [c.forward_return_10bar for c in changes_list if not c.reversed_within_24h]
        avg_fwd = np.mean(stable_fwd) if stable_fwd else 0
        logger.info(
            "  %-35s  %5d  %5d  %5.0f%%  %+10.2f%%",
            ttype, len(changes_list), fp_count,
            fp_count / len(changes_list) * 100, avg_fwd,
        )

    # ── 3. Best strategy at BEAR->CHOPPY ───────────────────────────────────
    logger.info("\n-- 3. BEST STRATEGY AT BEAR_TREND -> CHOPPY (the transition we're waiting for) --")
    key_bc = "BEAR_TREND->CHOPPY"
    if key_bc in all_pnl_data and all_pnl_data[key_bc]:
        logger.info("  Strategy signal PnL (5-candle hold after signal, regime-gated):")
        logger.info("  %-25s  %8s  %8s  %8s  %8s", "Strategy", "Avg PnL%", "Median", "Signals", "Win%")
        for strat in sorted(all_pnl_data[key_bc].keys(),
                            key=lambda s: np.mean(all_pnl_data[key_bc][s]), reverse=True):
            pnls = all_pnl_data[key_bc][strat]
            wins = sum(1 for p in pnls if p > 0)
            logger.info(
                "  %-25s  %+8.2f  %+8.2f  %8d  %7.0f%%",
                strat, np.mean(pnls), np.median(pnls), len(pnls),
                wins / len(pnls) * 100 if pnls else 0,
            )
    else:
        logger.info("  No BEAR->CHOPPY signals found (may all be false positives).")

    # Also show signal delays for this transition
    if key_bc in all_signal_data and all_signal_data[key_bc]:
        logger.info("\n  Signal delay (candles after BEAR->CHOPPY transition):")
        for strat in sorted(all_signal_data[key_bc].keys()):
            delays = [s["candles_after"] for s in all_signal_data[key_bc][strat]]
            logger.info(
                "    %-25s  avg delay: %.1f candles (%.0fh) | first at: %d candles | n=%d",
                strat, np.mean(delays), np.mean(delays) * CANDLE_HOURS,
                min(delays), len(delays),
            )

    # ── 4. Best strategy at CHOPPY->BULL ───────────────────────────────────
    logger.info("\n-- 4. BEST STRATEGY AT CHOPPY -> BULL_TREND --")
    key_cb = "CHOPPY->BULL_TREND"
    if key_cb in all_pnl_data and all_pnl_data[key_cb]:
        logger.info("  Strategy signal PnL (5-candle hold after signal, regime-gated):")
        logger.info("  %-25s  %8s  %8s  %8s  %8s", "Strategy", "Avg PnL%", "Median", "Signals", "Win%")
        for strat in sorted(all_pnl_data[key_cb].keys(),
                            key=lambda s: np.mean(all_pnl_data[key_cb][s]), reverse=True):
            pnls = all_pnl_data[key_cb][strat]
            wins = sum(1 for p in pnls if p > 0)
            logger.info(
                "  %-25s  %+8.2f  %+8.2f  %8d  %7.0f%%",
                strat, np.mean(pnls), np.median(pnls), len(pnls),
                wins / len(pnls) * 100 if pnls else 0,
            )
    else:
        logger.info("  No CHOPPY->BULL signals found (may all be false positives).")

    if key_cb in all_signal_data and all_signal_data[key_cb]:
        logger.info("\n  Signal delay (candles after CHOPPY->BULL transition):")
        for strat in sorted(all_signal_data[key_cb].keys()):
            delays = [s["candles_after"] for s in all_signal_data[key_cb][strat]]
            logger.info(
                "    %-25s  avg delay: %.1f candles (%.0fh) | first at: %d candles | n=%d",
                strat, np.mean(delays), np.mean(delays) * CANDLE_HOURS,
                min(delays), len(delays),
            )

    # ── 5. Overall signal delay ────────────────────────────────────────────
    logger.info("\n-- 5. SIGNAL DELAY AFTER ANY REGIME CHANGE (non-FP only) --")
    all_delays_by_strat: dict[str, list[int]] = defaultdict(list)
    for trans_type, strat_signals in all_signal_data.items():
        for strat_name, signals in strat_signals.items():
            for s in signals:
                all_delays_by_strat[strat_name].append(s["candles_after"])

    if all_delays_by_strat:
        logger.info("  %-25s  %10s  %8s  %8s  %8s", "Strategy", "Avg Delay", "Min", "Max", "Signals")
        for strat in sorted(all_delays_by_strat.keys()):
            delays = all_delays_by_strat[strat]
            logger.info(
                "  %-25s  %7.1f (%dh)  %8d  %8d  %8d",
                strat, np.mean(delays), int(np.mean(delays) * CANDLE_HOURS),
                min(delays), max(delays), len(delays),
            )

        all_delays = []
        for d in all_delays_by_strat.values():
            all_delays.extend(d)
        logger.info(
            "\n  OVERALL: avg %.1f candles (%.0fh) until first signal after any transition",
            np.mean(all_delays), np.mean(all_delays) * CANDLE_HOURS,
        )

    # ── 6. All transition types PnL ───────────────────────────────────────
    logger.info("\n-- 6. ALL TRANSITION TYPES -- STRATEGY PnL RANKING --")
    for trans_type in sorted(all_pnl_data.keys()):
        strats = all_pnl_data[trans_type]
        if not strats:
            continue
        logger.info("\n  %s:", trans_type)
        logger.info("  %-25s  %8s  %8s  %8s", "Strategy", "Avg PnL%", "Signals", "Win%")
        for strat in sorted(strats.keys(), key=lambda s: np.mean(strats[s]), reverse=True):
            pnls = strats[strat]
            wins = sum(1 for p in pnls if p > 0)
            logger.info(
                "    %-25s  %+8.2f  %8d  %7.0f%%",
                strat, np.mean(pnls), len(pnls), wins / len(pnls) * 100 if pnls else 0,
            )

    # ── 7. Regime distribution ─────────────────────────────────────────────
    logger.info("\n-- 7. REGIME DISTRIBUTION (time spent in each regime) --")
    for symbol, df in symbol_data.items():
        regime_counts: dict[str, int] = defaultdict(int)
        for i in range(30, len(df)):
            visible = df.iloc[max(0, i - 499):i + 1]
            result = detector.detect(visible)
            regime_counts[result.regime.value] += 1

        total_bars = sum(regime_counts.values())
        logger.info("  %s:", symbol)
        for regime in ["BULL_TREND", "BEAR_TREND", "CHOPPY", "HIGH_VOL"]:
            count = regime_counts.get(regime, 0)
            pct = count / total_bars * 100 if total_bars else 0
            days = count * CANDLE_HOURS / 24
            logger.info("    %-12s : %4d bars (%5.1f%%) = %5.0f days", regime, count, pct, days)

    # ── 8. Current regime ──────────────────────────────────────────────────
    logger.info("\n-- 8. CURRENT REGIME (latest data) --")
    for symbol, df in symbol_data.items():
        result = detector.detect(df.tail(500))
        weights = result.strategy_weights()
        active = sorted(
            [(k, v) for k, v in weights.items() if v > 0.5],
            key=lambda x: -x[1],
        )
        suppressed = sorted(
            [(k, v) for k, v in weights.items() if v <= 0.5],
            key=lambda x: x[1],
        )
        logger.info(
            "  %s: %s (conf=%.2f sharpe=%+.2f adx=%.0f vol_r=%.2f)",
            symbol, result.regime.value, result.confidence,
            result.rolling_sharpe, result.adx, result.volatility_ratio,
        )
        logger.info("    Active (weight>0.5): %s", ", ".join(f"{k}({v:.1f})" for k, v in active))
        if suppressed:
            logger.info("    Suppressed (<=0.5): %s", ", ".join(f"{k}({v:.1f})" for k, v in suppressed))

    # ── 9. Forward returns by transition (actionable) ──────────────────────
    logger.info("\n-- 9. FORWARD RETURNS BY TRANSITION TYPE (10-bar price change, non-FP only) --")
    logger.info("  %-35s  %8s  %8s  %6s  %8s", "Transition", "Avg Ret%", "Median", "Count", "Pos%")
    for ttype in sorted(transition_types.keys()):
        stable = [c for c in transition_types[ttype] if not c.reversed_within_24h]
        if not stable:
            continue
        fwd = [c.forward_return_10bar for c in stable]
        pos_pct = sum(1 for f in fwd if f > 0) / len(fwd) * 100
        logger.info(
            "  %-35s  %+8.2f  %+8.2f  %6d  %7.0f%%",
            ttype, np.mean(fwd), np.median(fwd), len(stable), pos_pct,
        )

    logger.info("\n" + "=" * 70)
    logger.info("  REGIME TRANSITION ANALYSIS COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
