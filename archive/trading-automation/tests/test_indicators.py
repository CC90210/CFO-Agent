"""
tests/test_indicators.py — Unit tests for all technical indicators.

Each test uses a small, hand-calculable dataset so the expected values can be
verified independently. Where exact numeric output depends on the underlying
`ta` library implementation we use wide tolerances; where we compute by hand
we use tight tolerances.

Tests are grouped by indicator family:
  - Trend:     EMA, SMA, MACD
  - Momentum:  RSI
  - Volatility: Bollinger Bands, ATR
  - Volume:    VWAP
  - Composite: Stochastic RSI
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Helpers — tiny synthetic datasets
# ---------------------------------------------------------------------------


def _make_series(values: list[float], name: str = "close") -> pd.Series:
    """Wrap a list in a pd.Series with a simple integer index."""
    return pd.Series(values, name=name, dtype=float)


def _make_ohlcv(
    n: int = 30,
    base_price: float = 100.0,
    seed: int = 0,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = base_price + np.cumsum(rng.normal(0, 1, n))
    close = np.maximum(close, 1.0)
    noise = rng.uniform(0.005, 0.015, n)
    high = close * (1 + noise)
    low = close * (1 - noise)
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    volume = rng.lognormal(10, 0.5, n) * 1000
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------


class TestEMA:
    def test_ema_returns_series_same_length_as_input(self) -> None:
        from strategies.technical.indicators import ema

        s = _make_series([1.0] * 20)
        result = ema(s, period=5)
        assert len(result) == 20

    def test_ema_of_constant_series_is_constant(self) -> None:
        """EMA of a flat series should equal that constant (after warm-up)."""
        from strategies.technical.indicators import ema

        s = _make_series([50.0] * 30)
        result = ema(s, period=10)
        # All non-NaN values should be ~50
        assert result.dropna().round(4).eq(50.0).all()

    def test_ema_faster_period_reacts_quicker(self) -> None:
        """EMA(5) should be closer to the latest price than EMA(20)."""
        from strategies.technical.indicators import ema

        vals = list(range(1, 51))  # linearly increasing
        s = _make_series(vals)
        fast = ema(s, period=5).iloc[-1]
        slow = ema(s, period=20).iloc[-1]
        # Both should be below the last value (50), but fast should be closer
        assert fast > slow

    def test_ema_known_value(self) -> None:
        """
        Manually verify EMA(3) on a small known series.

        With adjust=False (our implementation):
            k = 2 / (3 + 1) = 0.5
            EMA[0] = 10
            EMA[1] = 20 * 0.5 + 10 * 0.5 = 15
            EMA[2] = 30 * 0.5 + 15 * 0.5 = 22.5
        """
        from strategies.technical.indicators import ema

        s = _make_series([10.0, 20.0, 30.0])
        result = ema(s, period=3)
        assert result.iloc[0] == pytest.approx(10.0, abs=1e-6)
        assert result.iloc[1] == pytest.approx(15.0, abs=1e-6)
        assert result.iloc[2] == pytest.approx(22.5, abs=1e-6)

    def test_ema_period_one_equals_original(self) -> None:
        from strategies.technical.indicators import ema

        s = _make_series([10.0, 20.0, 30.0, 40.0])
        result = ema(s, period=1)
        assert result.tolist() == pytest.approx([10.0, 20.0, 30.0, 40.0])


# ---------------------------------------------------------------------------
# SMA
# ---------------------------------------------------------------------------


class TestSMA:
    def test_sma_known_value(self) -> None:
        """SMA(3) on [10, 20, 30, 40] at index 2 = (10+20+30)/3 = 20."""
        from strategies.technical.indicators import sma

        s = _make_series([10.0, 20.0, 30.0, 40.0])
        result = sma(s, period=3)
        assert result.iloc[2] == pytest.approx(20.0)
        assert result.iloc[3] == pytest.approx(30.0)

    def test_sma_first_values_are_nan(self) -> None:
        """First period-1 values should be NaN."""
        from strategies.technical.indicators import sma

        s = _make_series(list(range(1, 11)))
        result = sma(s, period=5)
        assert result.iloc[:4].isna().all()
        assert not pd.isna(result.iloc[4])


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------


class TestRSI:
    def test_rsi_range_0_to_100(self, sample_ohlcv_data: pd.DataFrame) -> None:
        from strategies.technical.indicators import rsi

        result = rsi(sample_ohlcv_data["close"], period=14)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 100).all()

    def test_rsi_overbought_on_pure_uptrend(self) -> None:
        """A perfectly rising series should produce RSI close to 100."""
        from strategies.technical.indicators import rsi

        s = _make_series(list(range(1, 51)))  # 1, 2, 3, ... 50
        result = rsi(s, period=14)
        # After enough bars, RSI should be very high (>90)
        assert result.dropna().iloc[-1] > 90

    def test_rsi_oversold_on_pure_downtrend(self) -> None:
        """A perfectly falling series should produce RSI close to 0."""
        from strategies.technical.indicators import rsi

        s = _make_series(list(range(50, 0, -1)))  # 50, 49, ... 1
        result = rsi(s, period=14)
        assert result.dropna().iloc[-1] < 10

    def test_rsi_neutral_on_equal_ups_and_downs(self) -> None:
        """Alternating ±1 moves should produce RSI near 50."""
        from strategies.technical.indicators import rsi

        vals = []
        price = 100.0
        for i in range(60):
            price += 1.0 if i % 2 == 0 else -1.0
            vals.append(price)
        s = _make_series(vals)
        result = rsi(s, period=14)
        last = result.dropna().iloc[-1]
        assert 40 < last < 60

    def test_rsi_has_correct_number_of_valid_values(self) -> None:
        from strategies.technical.indicators import rsi

        n = 50
        s = _make_series(list(range(1, n + 1)))
        result = rsi(s, period=14)
        # There should be at least n - 14 valid values
        assert result.notna().sum() >= n - 14


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------


class TestMACD:
    def test_macd_returns_three_columns(self, sample_ohlcv_data: pd.DataFrame) -> None:
        from strategies.technical.indicators import macd

        result = macd(sample_ohlcv_data["close"])
        assert set(result.columns) == {"macd", "signal", "histogram"}

    def test_macd_histogram_is_macd_minus_signal(
        self, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        from strategies.technical.indicators import macd

        result = macd(sample_ohlcv_data["close"])
        diff = (result["macd"] - result["signal"]).dropna()
        hist = result["histogram"].dropna()
        common = diff.index.intersection(hist.index)
        assert diff[common].round(8).equals(hist[common].round(8))

    def test_macd_positive_on_rising_market(self) -> None:
        """On a strong uptrend, fast EMA > slow EMA → MACD line > 0."""
        from strategies.technical.indicators import macd

        s = _make_series(list(range(1, 101)))
        result = macd(s, fast=12, slow=26, signal=9)
        # After enough warm-up, MACD line should be positive
        assert result["macd"].dropna().iloc[-1] > 0

    def test_macd_signal_generation_crossover(self) -> None:
        """When MACD crosses above signal, histogram changes sign."""
        from strategies.technical.indicators import macd

        # Construct a sequence: downtrend then uptrend
        vals = list(range(50, 0, -1)) + list(range(1, 101))
        s = _make_series(vals)
        result = macd(s)
        hist = result["histogram"].dropna()
        # There should be at least one sign change in the histogram
        signs = np.sign(hist.values)
        sign_changes = np.diff(signs)
        assert (sign_changes != 0).any()


# ---------------------------------------------------------------------------
# Bollinger Bands
# ---------------------------------------------------------------------------


class TestBollingerBands:
    def test_bollinger_bands_structure(self, sample_ohlcv_data: pd.DataFrame) -> None:
        from strategies.technical.indicators import bollinger_bands

        bb = bollinger_bands(sample_ohlcv_data["close"], period=20, std_dev=2.0)
        assert hasattr(bb, "upper")
        assert hasattr(bb, "middle")
        assert hasattr(bb, "lower")
        assert hasattr(bb, "width")
        assert hasattr(bb, "percent_b")

    def test_upper_above_middle_above_lower(
        self, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        from strategies.technical.indicators import bollinger_bands

        bb = bollinger_bands(sample_ohlcv_data["close"], period=20, std_dev=2.0)
        valid = bb.upper.notna() & bb.lower.notna()
        assert (bb.upper[valid] >= bb.middle[valid]).all()
        assert (bb.middle[valid] >= bb.lower[valid]).all()

    def test_bollinger_width_is_non_negative(
        self, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        from strategies.technical.indicators import bollinger_bands

        bb = bollinger_bands(sample_ohlcv_data["close"])
        assert (bb.width.dropna() >= 0).all()

    def test_bollinger_width_zero_on_constant_series(self) -> None:
        """A flat series has std=0 so bands collapse — width ≈ 0."""
        from strategies.technical.indicators import bollinger_bands

        s = _make_series([50.0] * 30)
        bb = bollinger_bands(s, period=20)
        assert bb.width.dropna().abs().max() < 1e-6

    def test_bollinger_width_larger_on_volatile_data(
        self, volatile_data: pd.DataFrame, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        from strategies.technical.indicators import bollinger_bands

        bb_vol = bollinger_bands(volatile_data["close"], period=20)
        bb_quiet = bollinger_bands(sample_ohlcv_data["close"], period=20)

        # width is already (upper - lower) / middle — a dimensionless ratio.
        # Volatile data has higher vol-to-price ratio so width should be larger.
        avg_width_vol = bb_vol.width.dropna().mean()
        avg_width_quiet = bb_quiet.width.dropna().mean()
        assert avg_width_vol > avg_width_quiet


# ---------------------------------------------------------------------------
# ATR
# ---------------------------------------------------------------------------


class TestATR:
    def test_atr_returns_non_negative(self, sample_ohlcv_data: pd.DataFrame) -> None:
        from strategies.technical.indicators import atr

        result = atr(sample_ohlcv_data, period=14)
        assert (result.dropna() >= 0).all()

    def test_atr_known_value(self) -> None:
        """
        Construct a simple 3-bar DataFrame and verify ATR(1) manually.

        ATR(1) is just the True Range of the last bar:
            TR = max(H-L, |H-prev_C|, |L-prev_C|)
        """
        from strategies.technical.indicators import atr

        df = pd.DataFrame(
            {
                "open":  [10.0, 10.0, 10.0],
                "high":  [12.0, 14.0, 16.0],
                "low":   [8.0,  9.0,  9.0],
                "close": [11.0, 13.0, 15.0],
                "volume":[1000, 1000, 1000],
            },
            index=pd.date_range("2024-01-01", periods=3, freq="1h", tz="UTC"),
        )
        result = atr(df, period=1)
        # ATR(1) at index 2:
        #   H=16, L=9, prev_C=13
        #   TR = max(16-9, |16-13|, |9-13|) = max(7, 3, 4) = 7
        assert result.iloc[-1] == pytest.approx(7.0, abs=0.5)

    def test_atr_higher_on_volatile_data(
        self, volatile_data: pd.DataFrame, sample_ohlcv_data: pd.DataFrame
    ) -> None:
        from strategies.technical.indicators import atr

        atr_vol = atr(volatile_data, period=14)
        atr_quiet = atr(sample_ohlcv_data, period=14)

        # Normalise by price level
        norm_vol = (atr_vol.dropna() / volatile_data["close"].mean()).mean()
        norm_quiet = (atr_quiet.dropna() / sample_ohlcv_data["close"].mean()).mean()
        assert norm_vol > norm_quiet

    def test_atr_length_matches_input(self, sample_ohlcv_data: pd.DataFrame) -> None:
        from strategies.technical.indicators import atr

        result = atr(sample_ohlcv_data, period=14)
        assert len(result) == len(sample_ohlcv_data)


# ---------------------------------------------------------------------------
# Stochastic RSI
# ---------------------------------------------------------------------------


class TestStochasticRSI:
    def test_stoch_rsi_columns_present(self, sample_ohlcv_data: pd.DataFrame) -> None:
        from strategies.technical.indicators import stochastic_rsi

        result = stochastic_rsi(sample_ohlcv_data["close"])
        assert "stoch_rsi_k" in result.columns
        assert "stoch_rsi_d" in result.columns

    def test_stoch_rsi_range(self, sample_ohlcv_data: pd.DataFrame) -> None:
        """Stochastic RSI values should be in [0, 1]."""
        from strategies.technical.indicators import stochastic_rsi

        result = stochastic_rsi(sample_ohlcv_data["close"])
        k = result["stoch_rsi_k"].dropna()
        d = result["stoch_rsi_d"].dropna()
        assert (k >= 0).all() and (k <= 1).all()
        assert (d >= 0).all() and (d <= 1).all()
