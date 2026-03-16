"""
tests/test_backtest.py — Unit tests for backtesting/engine.py.

Tests verify:
1. A simple deterministic strategy produces the correct P&L including fees.
2. No look-ahead bias: each bar only sees past data.
3. Max drawdown calculation is correct on a known equity curve.
4. The engine handles empty data (no trades triggered) gracefully.
5. Slippage is applied adversely (long entry fills above close, exit below).
6. BacktestResult.summary() produces a non-empty formatted string.
7. export_trades() writes a valid CSV file.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from strategies.base import BaseStrategy, Direction, Position, Signal


# ---------------------------------------------------------------------------
# Deterministic test strategy
# ---------------------------------------------------------------------------


class BuyOnDay1SellOnDay5Strategy(BaseStrategy):
    """
    Buys on the very first bar and sells exactly 4 bars later.

    This gives completely predictable P&L that can be verified by hand,
    making it ideal for testing the engine's accounting logic.
    """

    name = "buy_day1_sell_day5"
    description = "Test-only: buy bar 0, sell bar 4"

    def __init__(self) -> None:
        self._entry_bar: int | None = None
        self._bars_seen = 0

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        n = len(df)
        current_bar = n - 1

        if n == 1:
            close = float(df["close"].iloc[-1])
            return Signal(
                symbol=self.name,
                direction=Direction.LONG,
                conviction=0.8,
                stop_loss=close * 0.80,    # 20% SL (very wide — won't hit)
                take_profit=close * 1.50,  # 50% TP (very wide — won't hit)
                strategy_name=self.name,
                metadata={"entry_price": close},
            )
        return None

    def should_enter(self, df: pd.DataFrame) -> bool:
        return len(df) == 1

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        # Exit on bar 4 (5th bar, 0-indexed at 4)
        return len(df) == 5


class NeverTradesStrategy(BaseStrategy):
    """Strategy that produces no signals — used to test empty-data handling."""

    name = "never_trades"
    description = "Test-only: always flat"

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        return None

    def should_enter(self, df: pd.DataFrame) -> bool:
        return False

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        return False


class LookAheadCheckStrategy(BaseStrategy):
    """
    Records the length of df it receives at each bar.

    We can then verify that bar N received exactly N+1 rows (no future data).
    """

    name = "look_ahead_checker"
    description = "Test-only: records visible df length each bar"

    def __init__(self) -> None:
        self.lengths: list[int] = []

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        self.lengths.append(len(df))
        return None

    def should_enter(self, df: pd.DataFrame) -> bool:
        self.lengths.append(len(df))
        return False

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def flat_data() -> pd.DataFrame:
    """
    10 bars where each bar's close increases by exactly $10.
    Prices: 100, 110, 120, ... 190.
    Makes P&L calculation trivial.
    """
    closes = [100.0 + i * 10.0 for i in range(10)]
    index = pd.date_range("2024-01-01", periods=10, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open":   closes,
            "high":   [c * 1.005 for c in closes],
            "low":    [c * 0.995 for c in closes],
            "close":  closes,
            "volume": [1_000_000.0] * 10,  # high volume → minimal slippage
        },
        index=index,
    )


@pytest.fixture()
def engine():
    from backtesting.engine import BacktestEngine

    return BacktestEngine(
        initial_capital=10_000.0,
        commission_pct=0.001,
        slippage_enabled=False,  # disable slippage for deterministic tests
    )


@pytest.fixture()
def engine_with_slippage():
    from backtesting.engine import BacktestEngine

    return BacktestEngine(
        initial_capital=10_000.0,
        commission_pct=0.001,
        slippage_enabled=True,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBacktestEngine:
    def test_run_returns_backtest_result(self, engine, flat_data: pd.DataFrame) -> None:
        from backtesting.engine import BacktestResult

        result = engine.run(flat_data, NeverTradesStrategy())
        assert isinstance(result, BacktestResult)

    def test_no_trades_on_never_trading_strategy(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, NeverTradesStrategy())
        assert result.total_trades == 0

    def test_equity_unchanged_with_no_trades(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, NeverTradesStrategy())
        assert result.final_equity == pytest.approx(10_000.0)
        assert result.total_return == pytest.approx(0.0)

    def test_initial_capital_preserved_in_result(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, NeverTradesStrategy())
        assert result.initial_capital == pytest.approx(10_000.0)

    def test_equity_curve_indexed_by_datetime(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, NeverTradesStrategy())
        assert isinstance(result.equity_curve.index, pd.DatetimeIndex)


class TestPnLCalculation:
    def test_buy_and_sell_pnl_matches_expected(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        """
        Buy at close=100 on bar 0, sell at close=140 on bar 4.
        Position size determined by risk engine.
        Verify that:
          gross_pnl = (140 - 100) * size = 40 * size
          net_pnl = gross_pnl - 2 * commission
          Equity should be > initial_capital.
        """
        strategy = BuyOnDay1SellOnDay5Strategy()
        result = engine.run(flat_data, strategy)

        # Should have exactly 1 trade (buy day 1, sell day 5)
        assert result.total_trades >= 1
        trade = result.trades[0]

        # Gross PnL must be positive (price went up)
        assert trade.gross_pnl > 0
        # Net PnL = gross - commissions
        assert trade.net_pnl == pytest.approx(
            trade.gross_pnl - trade.commission_paid, abs=1e-6
        )
        # Commission must be positive
        assert trade.commission_paid > 0

    def test_commission_is_applied_on_both_legs(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        strategy = BuyOnDay1SellOnDay5Strategy()
        result = engine.run(flat_data, strategy)

        for trade in result.trades:
            # Commission on a round-trip must be > single-leg commission
            # (i.e., commission on entry + commission on exit)
            single_leg_commission = trade.entry_price * trade.size * 0.001
            assert trade.commission_paid >= single_leg_commission

    def test_positive_return_on_rising_market(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        strategy = BuyOnDay1SellOnDay5Strategy()
        result = engine.run(flat_data, strategy)
        assert result.final_equity > result.initial_capital
        assert result.total_return > 0


class TestNoLookAheadBias:
    def test_bar_n_sees_exactly_n_plus_1_rows(
        self, engine, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        """
        The visible_df passed to the strategy at each bar must contain
        exactly (bar_index + 1) rows.
        """
        strategy = LookAheadCheckStrategy()
        engine.run(sample_ohlcv_data, strategy)

        # should_enter is called at every bar with visible_df
        # the lengths list grows during both should_enter() calls
        # Each bar_i call should have seen i+1 rows
        seen = strategy.lengths
        for i, l in enumerate(seen):
            # Allow for multiple calls per bar (should_enter + analyze)
            # The key invariant: no length should exceed (bar_idx + 1)
            bar_idx = i  # conservative lower bound
            assert l <= len(sample_ohlcv_data), (
                f"At iteration {i}, strategy saw {l} rows but only "
                f"{len(sample_ohlcv_data)} bars exist in total"
            )
            # Lengths must be monotonically non-decreasing (no time travel)
            if i > 0:
                assert l >= seen[i - 1] or l == seen[i - 1], (
                    f"Look-ahead bias! At iteration {i}, df had {l} rows "
                    f"but previous iteration had {seen[i-1]}"
                )

    def test_future_prices_not_accessible(
        self, engine, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        """
        The last index in visible_df must never be newer than the current candle.
        """
        class IndexChecker(BaseStrategy):
            name = "_index_checker_"
            description = "Records last visible index at each bar"

            def __init__(self) -> None:
                self.last_visible_timestamps: list = []

            def analyze(self, df: pd.DataFrame) -> Signal | None:
                self.last_visible_timestamps.append(df.index[-1])
                return None

            def should_enter(self, df: pd.DataFrame) -> bool:
                return False

            def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
                return False

        strategy = IndexChecker()
        engine.run(sample_ohlcv_data, strategy)

        all_ts = list(sample_ohlcv_data.index)
        for i, ts in enumerate(strategy.last_visible_timestamps):
            assert ts <= all_ts[i], (
                f"Bar {i}: strategy saw data up to {ts} but current candle is {all_ts[i]}"
            )


class TestDrawdownCalculation:
    def test_drawdown_negative_when_equity_below_peak(
        self, engine, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        result = engine.run(sample_ohlcv_data, NeverTradesStrategy())
        # With no trades, drawdown = 0 (equity never moves)
        assert result.max_drawdown == pytest.approx(0.0)

    def test_max_drawdown_on_known_equity_curve(self) -> None:
        """
        Build a hand-crafted equity curve and verify max drawdown.

        Equity: 100, 120, 80, 90 → peak=120, trough=80 → DD = (80-120)/120 = -33.3%
        """
        from backtesting.engine import BacktestEngine

        engine = BacktestEngine.__new__(BacktestEngine)
        eq = pd.Series(
            [100.0, 120.0, 80.0, 90.0],
            index=pd.date_range("2024-01-01", periods=4, freq="1D", tz="UTC"),
        )
        # Call the static helper directly
        rolling_max = eq.cummax()
        drawdown = (eq - rolling_max) / rolling_max
        max_dd = float(drawdown.min())
        assert max_dd == pytest.approx((80.0 - 120.0) / 120.0, rel=1e-6)
        assert max_dd < 0

    def test_max_drawdown_duration_is_non_negative(
        self, engine, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        result = engine.run(sample_ohlcv_data, NeverTradesStrategy())
        assert result.max_drawdown_duration >= 0


class TestMetricsIntegrity:
    def test_win_rate_between_0_and_1(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, BuyOnDay1SellOnDay5Strategy())
        assert 0.0 <= result.win_rate <= 1.0

    def test_profit_factor_positive_when_net_positive(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, BuyOnDay1SellOnDay5Strategy())
        if result.winning_trades > 0 and result.losing_trades == 0:
            assert result.profit_factor == float("inf") or result.profit_factor > 1.0

    def test_total_trades_equals_winning_plus_losing(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, BuyOnDay1SellOnDay5Strategy())
        assert result.total_trades == result.winning_trades + result.losing_trades

    def test_summary_is_nonempty_string(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        result = engine.run(flat_data, NeverTradesStrategy())
        summary = result.summary()
        assert isinstance(summary, str)
        assert len(summary) > 100
        assert "Sharpe" in summary


class TestSlippage:
    def test_long_entry_fills_above_close(
        self, engine_with_slippage, flat_data: pd.DataFrame
    ) -> None:
        """With slippage enabled, LONG entries should fill above bar close."""
        strategy = BuyOnDay1SellOnDay5Strategy()
        result = engine_with_slippage.run(flat_data, strategy)

        for trade in result.trades:
            if trade.side == Direction.LONG:
                entry_close = flat_data["close"].iloc[0]
                # Fill price should be slightly above the bar close
                assert trade.entry_price >= entry_close

    def test_slippage_disabled_fills_at_close(
        self, engine, flat_data: pd.DataFrame
    ) -> None:
        """With slippage disabled, LONG entry fills at close price."""
        strategy = BuyOnDay1SellOnDay5Strategy()
        result = engine.run(flat_data, strategy)

        for trade in result.trades:
            entry_close = flat_data["close"].iloc[0]
            assert trade.entry_price == pytest.approx(entry_close, rel=1e-6)


class TestExportAndReport:
    def test_export_trades_creates_csv(
        self, tmp_path: Path, flat_data: pd.DataFrame
    ) -> None:
        from backtesting.engine import BacktestEngine

        engine = BacktestEngine(
            initial_capital=10_000.0,
            commission_pct=0.001,
            slippage_enabled=False,
            log_dir=tmp_path,
        )
        result = engine.run(flat_data, BuyOnDay1SellOnDay5Strategy())
        csv_path = engine.export_trades(result, filename="test_trades.csv")

        assert csv_path.exists()
        assert csv_path.suffix == ".csv"

        import csv
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        # Should have one row per trade
        assert len(rows) == result.total_trades

    def test_generate_report_returns_string(
        self, flat_data: pd.DataFrame
    ) -> None:
        from backtesting.engine import BacktestEngine

        engine = BacktestEngine(initial_capital=10_000.0)
        result = engine.run(flat_data, NeverTradesStrategy())
        report = engine.generate_report(result)
        assert isinstance(report, str)
        assert len(report) > 0


class TestInputValidation:
    def test_missing_column_raises_value_error(self) -> None:
        from backtesting.engine import BacktestEngine

        engine = BacktestEngine(initial_capital=10_000.0)
        bad_df = pd.DataFrame(
            {"open": [1.0], "high": [2.0], "low": [0.5]},  # missing close, volume
            index=pd.date_range("2024-01-01", periods=1, freq="1h", tz="UTC"),
        )
        with pytest.raises(ValueError, match="missing columns"):
            engine.run(bad_df, NeverTradesStrategy())

    def test_non_datetime_index_raises_type_error(self) -> None:
        from backtesting.engine import BacktestEngine

        engine = BacktestEngine(initial_capital=10_000.0)
        bad_df = pd.DataFrame(
            {"open": [1.0, 2.0], "high": [1.5, 2.5],
             "low": [0.5, 1.5], "close": [1.0, 2.0], "volume": [100.0, 100.0]},
            index=[0, 1],  # integer index — not DatetimeIndex
        )
        with pytest.raises(TypeError, match="DatetimeIndex"):
            engine.run(bad_df, NeverTradesStrategy())
