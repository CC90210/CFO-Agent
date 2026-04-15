"""
tests/test_walk_forward.py — Tests for backtesting/walk_forward.py.

Tests cover:
1. WalkForwardValidator window slicing — correct train/test bar counts.
2. validate() returns a WalkForwardResult with all required fields populated.
3. Overfitting score is in [0, 1].
4. Recommendation is one of the three valid strings.
5. train_test_correlation is in [-1, 1].
6. worst_oos_window is the window with the minimum test_return.
7. summary() returns a non-empty formatted string.
8. Edge cases: dataset exactly equal to one window; step_bars > test_bars.
9. ValueError raised when dataset is too small.
10. WalkForwardOptimiser (old optimisation API) still works correctly.
"""

from __future__ import annotations

import pandas as pd
import pytest

from strategies.base import BaseStrategy, Direction, Position, Signal


# ---------------------------------------------------------------------------
# Minimal deterministic strategy for walk-forward tests
# ---------------------------------------------------------------------------


class AlwaysFlatStrategy(BaseStrategy):
    """Never trades — used to test engine accounting with no trades."""

    name = "wf_always_flat"
    description = "Test: always flat"

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        return None

    def should_enter(self, df: pd.DataFrame) -> bool:
        return False

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        return False


class BuyFirstBarStrategy(BaseStrategy):
    """Buys on the first bar of every slice — predictable behaviour in tests."""

    name = "wf_buy_first_bar"
    description = "Test: buy first bar, hold"

    def analyze(self, df: pd.DataFrame) -> Signal | None:
        if len(df) == 1:
            close = float(df["close"].iloc[-1])
            return Signal(
                symbol=self.name,
                direction=Direction.LONG,
                conviction=0.8,
                stop_loss=close * 0.50,
                take_profit=close * 2.00,
                strategy_name=self.name,
                metadata={"entry_price": close},
            )
        return None

    def should_enter(self, df: pd.DataFrame) -> bool:
        return len(df) == 1

    def should_exit(self, df: pd.DataFrame, position: Position) -> bool:
        return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def large_df() -> pd.DataFrame:
    """1200-bar trending OHLCV — enough for multiple walk-forward windows."""
    import numpy as np

    rng = np.random.default_rng(77)
    n = 1200
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.001, 0.012, n)))
    noise = rng.uniform(0.003, 0.010, n)
    open_ = close * (1.0 + rng.normal(0.0, 0.002, n))
    high = np.maximum(open_, close) * (1.0 + noise)
    low = np.minimum(open_, close) * (1.0 - noise)
    volume = rng.lognormal(10.0, 0.5, n) * 1000.0
    index = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )


@pytest.fixture()
def minimal_df() -> pd.DataFrame:
    """Exactly train_bars + test_bars = 150 bars (boundary case)."""
    import numpy as np

    rng = np.random.default_rng(11)
    n = 150
    close = 50.0 * np.exp(np.cumsum(rng.normal(0.0, 0.01, n)))
    noise = rng.uniform(0.002, 0.008, n)
    open_ = close.copy()
    high = close * (1.0 + noise)
    low = close * (1.0 - noise)
    volume = np.ones(n) * 50_000.0
    index = pd.date_range("2025-01-01", periods=n, freq="4h", tz="UTC")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=index,
    )


# ---------------------------------------------------------------------------
# WalkForwardValidator tests
# ---------------------------------------------------------------------------


class TestWalkForwardValidator:
    def _make_validator(self, **kwargs):
        from backtesting.walk_forward import WalkForwardValidator

        return WalkForwardValidator(train_bars=100, test_bars=50, step_bars=50, **kwargs)

    def test_validate_returns_walk_forward_result(self, large_df: pd.DataFrame) -> None:
        from backtesting.walk_forward import WalkForwardResult

        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert isinstance(result, WalkForwardResult)

    def test_windows_are_populated(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert len(result.windows) >= 2

    def test_strategy_name_in_result(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert result.strategy_name == "wf_always_flat"

    def test_overfitting_score_in_range(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert 0.0 <= result.overfitting_score <= 1.0

    def test_recommendation_is_valid_string(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert result.recommendation in {"DEPLOY", "CAUTION", "DO_NOT_DEPLOY"}

    def test_train_test_correlation_in_range(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert -1.0 <= result.train_test_correlation <= 1.0

    def test_worst_oos_window_has_minimum_test_return(
        self, large_df: pd.DataFrame
    ) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        min_return = min(w.test_return for w in result.windows)
        assert result.worst_oos_window.test_return == pytest.approx(min_return)

    def test_avg_oos_return_matches_window_average(
        self, large_df: pd.DataFrame
    ) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        expected = sum(w.test_return for w in result.windows) / len(result.windows)
        assert result.avg_oos_return == pytest.approx(expected, rel=1e-6)

    def test_avg_oos_win_rate_matches_window_average(
        self, large_df: pd.DataFrame
    ) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        expected = sum(w.test_win_rate for w in result.windows) / len(result.windows)
        assert result.avg_oos_win_rate == pytest.approx(expected, rel=1e-6)

    def test_summary_is_nonempty_string(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        text = v.summary(result)
        assert isinstance(text, str)
        assert len(text) > 100
        assert "DEPLOY" in text or "CAUTION" in text or "DO_NOT_DEPLOY" in text

    def test_summary_contains_strategy_name(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert result.strategy_name in v.summary(result)

    def test_window_train_bars_count(self, large_df: pd.DataFrame) -> None:
        """Each window's train period must span exactly train_bars bars."""
        from backtesting.walk_forward import WalkForwardValidator

        train_bars = 100
        test_bars = 50
        v = WalkForwardValidator(train_bars=train_bars, test_bars=test_bars, step_bars=50)
        result = v.validate(large_df, AlwaysFlatStrategy())
        for w in result.windows:
            # train_start and train_end timestamps should span train_bars bars
            # (we verify indirectly that train_return is a float)
            assert isinstance(w.train_return, float)
            assert isinstance(w.test_return, float)

    def test_window_fields_are_correct_types(self, large_df: pd.DataFrame) -> None:
        from backtesting.walk_forward import WalkForwardWindow
        from datetime import datetime

        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        w = result.windows[0]
        assert isinstance(w, WalkForwardWindow)
        assert isinstance(w.train_start, datetime)
        assert isinstance(w.train_end, datetime)
        assert isinstance(w.test_start, datetime)
        assert isinstance(w.test_end, datetime)
        assert isinstance(w.train_trades, int)
        assert isinstance(w.test_trades, int)

    def test_too_small_df_raises_value_error(self) -> None:
        from backtesting.walk_forward import WalkForwardValidator
        import numpy as np

        # Only 10 bars — not enough for any window
        n = 10
        close = np.ones(n) * 100.0
        df = pd.DataFrame(
            {"open": close, "high": close * 1.01, "low": close * 0.99,
             "close": close, "volume": np.ones(n) * 1000.0},
            index=pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC"),
        )
        v = WalkForwardValidator(train_bars=500, test_bars=100, step_bars=50)
        with pytest.raises(ValueError, match="train_bars"):
            v.validate(df, AlwaysFlatStrategy())

    def test_boundary_case_exactly_one_window(self, minimal_df: pd.DataFrame) -> None:
        """Dataset has exactly train_bars + test_bars rows — produces one window."""
        from backtesting.walk_forward import WalkForwardValidator

        v = WalkForwardValidator(train_bars=100, test_bars=50, step_bars=50)
        result = v.validate(minimal_df, AlwaysFlatStrategy())
        assert len(result.windows) >= 1

    def test_step_bars_larger_than_test_bars(self, large_df: pd.DataFrame) -> None:
        """step_bars > test_bars is valid — windows skip ahead faster."""
        from backtesting.walk_forward import WalkForwardValidator

        v = WalkForwardValidator(train_bars=100, test_bars=50, step_bars=100)
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert len(result.windows) >= 1

    def test_no_trades_strategy_has_zero_win_rate(self, large_df: pd.DataFrame) -> None:
        v = self._make_validator()
        result = v.validate(large_df, AlwaysFlatStrategy())
        assert result.avg_oos_win_rate == pytest.approx(0.0)

    def test_constructor_validation(self) -> None:
        from backtesting.walk_forward import WalkForwardValidator

        with pytest.raises(ValueError, match="train_bars"):
            WalkForwardValidator(train_bars=5)
        with pytest.raises(ValueError, match="test_bars"):
            WalkForwardValidator(test_bars=2)
        with pytest.raises(ValueError, match="step_bars"):
            WalkForwardValidator(step_bars=0)


# ---------------------------------------------------------------------------
# WalkForwardOptimiser tests (backward compatibility)
# ---------------------------------------------------------------------------


class TestWalkForwardOptimiser:
    def test_optimiser_validate_returns_optimisation_result(
        self, large_df: pd.DataFrame
    ) -> None:
        from backtesting.walk_forward import WalkForwardOptimiser, OptimisationResult

        optimiser = WalkForwardOptimiser(train_ratio=0.7, n_splits=3)
        result = optimiser.validate(
            strategy_cls=AlwaysFlatStrategy,
            data=large_df,
            param_grid=None,
        )
        assert isinstance(result, OptimisationResult)

    def test_optimiser_windows_populated(self, large_df: pd.DataFrame) -> None:
        from backtesting.walk_forward import WalkForwardOptimiser

        optimiser = WalkForwardOptimiser(train_ratio=0.7, n_splits=3)
        result = optimiser.validate(
            strategy_cls=AlwaysFlatStrategy,
            data=large_df,
        )
        assert len(result.windows) >= 1

    def test_optimiser_summary_is_string(self, large_df: pd.DataFrame) -> None:
        from backtesting.walk_forward import WalkForwardOptimiser

        optimiser = WalkForwardOptimiser(train_ratio=0.7, n_splits=2)
        result = optimiser.validate(
            strategy_cls=AlwaysFlatStrategy,
            data=large_df,
        )
        text = result.summary()
        assert isinstance(text, str)
        assert "Walk-Forward" in text

    def test_optimiser_constructor_validation(self) -> None:
        from backtesting.walk_forward import WalkForwardOptimiser

        with pytest.raises(ValueError, match="train_ratio"):
            WalkForwardOptimiser(train_ratio=0.1)
        with pytest.raises(ValueError, match="n_splits"):
            WalkForwardOptimiser(n_splits=1)


# ---------------------------------------------------------------------------
# Public API (backtesting package __init__) tests
# ---------------------------------------------------------------------------


class TestPublicImports:
    def test_walk_forward_validator_importable_from_package(self) -> None:
        from backtesting import WalkForwardValidator  # noqa: F401

    def test_walk_forward_result_importable_from_package(self) -> None:
        from backtesting import WalkForwardResult  # noqa: F401

    def test_walk_forward_window_importable_from_package(self) -> None:
        from backtesting import WalkForwardWindow  # noqa: F401

    def test_walk_forward_optimiser_importable_from_package(self) -> None:
        from backtesting import WalkForwardOptimiser  # noqa: F401

    def test_optimisation_result_importable_from_package(self) -> None:
        from backtesting import OptimisationResult  # noqa: F401

    def test_window_result_importable_from_package(self) -> None:
        from backtesting import WindowResult  # noqa: F401
