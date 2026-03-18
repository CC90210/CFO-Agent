"""
tests/test_core_modules.py
---------------------------
Tests for the new core modules added in the v2 build:
  - SentimentEngine
  - TradingPlaybook
  - MomentumClassifier
  - RiskParity
  - CorrelationTracker
  - TradeProtocol
  - MarketStructure (if built by background agent)
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, UTC, timedelta


# ---------------------------------------------------------------------------
# SentimentEngine
# ---------------------------------------------------------------------------


class TestSentimentEngine:
    def test_import(self):
        from core.sentiment_engine import SentimentEngine, SentimentResult
        assert SentimentEngine is not None

    @pytest.mark.asyncio
    async def test_neutral_sentiment(self):
        from core.sentiment_engine import SentimentEngine
        engine = SentimentEngine()
        result = await engine.analyze("BTC/USDT")
        assert result.composite_score == 0.0
        assert result.risk_modifier == 1.0
        assert not result.should_avoid_entry

    @pytest.mark.asyncio
    async def test_extreme_fear(self):
        from core.sentiment_engine import SentimentEngine
        engine = SentimentEngine()
        result = await engine.analyze("BTC/USDT", fear_greed_value=10)
        assert result.extreme_fear
        assert not result.extreme_greed
        assert result.fear_greed_score < 0
        assert result.risk_modifier < 1.0  # should reduce size

    @pytest.mark.asyncio
    async def test_extreme_greed(self):
        from core.sentiment_engine import SentimentEngine
        engine = SentimentEngine()
        result = await engine.analyze("BTC/USDT", fear_greed_value=90)
        assert result.extreme_greed
        assert result.risk_modifier < 0.7  # significant reduction

    @pytest.mark.asyncio
    async def test_macro_event_avoidance(self):
        from core.sentiment_engine import SentimentEngine
        engine = SentimentEngine()
        result = await engine.analyze("BTC/USDT", macro_event_today=True)
        assert result.should_avoid_entry
        assert result.risk_modifier <= 0.5

    def test_conviction_adjustment(self):
        from core.sentiment_engine import SentimentEngine, SentimentResult
        engine = SentimentEngine()
        # Bullish sentiment should boost bullish conviction
        bullish_result = SentimentResult(symbol="BTC", composite_score=0.5)
        adjusted = engine.apply_to_conviction(0.8, bullish_result)
        assert adjusted > 0.8  # boosted

        # Bearish sentiment should dampen bullish conviction
        bearish_result = SentimentResult(symbol="BTC", composite_score=-0.5)
        adjusted = engine.apply_to_conviction(0.8, bearish_result)
        assert adjusted < 0.8  # dampened


# ---------------------------------------------------------------------------
# TradingPlaybook
# ---------------------------------------------------------------------------


class TestTradingPlaybook:
    def test_import(self):
        from core.playbook import TradingPlaybook, detect_session
        assert TradingPlaybook is not None

    def test_bull_regime_guidance(self):
        from core.playbook import TradingPlaybook
        pb = TradingPlaybook()
        g = pb.evaluate(regime="BULL_TREND")
        assert g.should_trade
        assert "ema_crossover" in g.preferred_strategies
        assert g.trailing_stop_multiplier == 3.5

    def test_bear_regime_reduces_size(self):
        from core.playbook import TradingPlaybook
        pb = TradingPlaybook()
        g = pb.evaluate(regime="BEAR_TREND")
        assert g.size_multiplier < 1.0

    def test_macro_event_halts_trading(self):
        from core.playbook import TradingPlaybook
        pb = TradingPlaybook()
        g = pb.evaluate(macro_event_today=True)
        assert not g.should_trade

    def test_losing_streak_protection(self):
        from core.playbook import TradingPlaybook
        pb = TradingPlaybook()
        g = pb.evaluate(consecutive_losses=5)
        assert not g.should_trade

    def test_deep_drawdown_reduces_size(self):
        from core.playbook import TradingPlaybook
        pb = TradingPlaybook()
        g = pb.evaluate(current_drawdown_pct=12.0)
        assert g.size_multiplier < 0.5
        assert g.max_concurrent_positions <= 1

    def test_session_detection(self):
        from core.playbook import detect_session, TradingSession
        assert detect_session(3) == TradingSession.ASIAN
        assert detect_session(10) == TradingSession.LONDON
        assert detect_session(14) == TradingSession.OVERLAP

    def test_high_vol_regime(self):
        from core.playbook import TradingPlaybook
        pb = TradingPlaybook()
        g = pb.evaluate(regime="HIGH_VOL")
        assert g.size_multiplier <= 0.5
        assert g.max_concurrent_positions <= 3


# ---------------------------------------------------------------------------
# MomentumClassifier
# ---------------------------------------------------------------------------


def _make_trending_df(bars: int = 250, direction: str = "up") -> pd.DataFrame:
    """Generate a synthetic trending DataFrame."""
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=bars, freq="4h", tz="UTC")
    base = 50000.0
    noise = np.random.randn(bars) * 200
    if direction == "up":
        trend = np.linspace(0, 15000, bars)
    else:
        trend = np.linspace(0, -15000, bars)
    close = base + trend + noise
    close = np.maximum(close, 100)  # floor
    return pd.DataFrame({
        "open": close - np.random.rand(bars) * 100,
        "high": close + np.abs(np.random.randn(bars) * 300),
        "low": close - np.abs(np.random.randn(bars) * 300),
        "close": close,
        "volume": np.random.rand(bars) * 1000 + 500,
    }, index=dates)


class TestMomentumClassifier:
    def test_import(self):
        from core.momentum_classifier import MomentumClassifier
        assert MomentumClassifier is not None

    def test_uptrend_classification(self):
        from core.momentum_classifier import MomentumClassifier
        mc = MomentumClassifier()
        df = _make_trending_df(250, "up")
        phase = mc.classify(df)
        assert phase.trend_strength > 0  # should be positive for uptrend
        assert phase.phase in ("MARKUP", "DISTRIBUTION", "RANGE_BOUND", "ACCUMULATION")

    def test_downtrend_classification(self):
        from core.momentum_classifier import MomentumClassifier
        mc = MomentumClassifier()
        df = _make_trending_df(250, "down")
        phase = mc.classify(df)
        assert phase.trend_strength < 0  # should be negative for downtrend

    def test_insufficient_data(self):
        from core.momentum_classifier import MomentumClassifier
        mc = MomentumClassifier()
        df = _make_trending_df(10)  # too short
        phase = mc.classify(df)
        assert phase.phase == "RANGE_BOUND"
        assert phase.confidence == 0.0

    def test_summary_format(self):
        from core.momentum_classifier import MomentumClassifier
        mc = MomentumClassifier()
        df = _make_trending_df(250, "up")
        phase = mc.classify(df)
        summary = phase.summary()
        assert "conf=" in summary
        assert "trend=" in summary


# ---------------------------------------------------------------------------
# RiskParity
# ---------------------------------------------------------------------------


class TestRiskParity:
    def test_import(self):
        from core.risk_parity import RiskParity
        assert RiskParity is not None

    def test_high_vol_reduces_size(self):
        from core.risk_parity import RiskParity
        rp = RiskParity(target_annual_vol=0.15)
        # High vol asset (50% annual) → multiplier < 1.0
        result = rp.position_multiplier("BTC/USDT", current_atr_pct=0.03)
        assert result.position_multiplier < 1.0
        assert result.vol_ratio > 1.0

    def test_low_vol_increases_size(self):
        from core.risk_parity import RiskParity
        rp = RiskParity(target_annual_vol=0.50)
        # Low vol asset relative to high target → multiplier > 1.0
        result = rp.position_multiplier("STABLECOIN/USDT", current_atr_pct=0.001)
        assert result.position_multiplier > 1.0

    def test_portfolio_allocation_sums_to_one(self):
        from core.risk_parity import RiskParity
        rp = RiskParity()
        np.random.seed(42)
        returns = {
            "BTC/USDT": pd.Series(np.random.randn(50) * 0.03),
            "ETH/USDT": pd.Series(np.random.randn(50) * 0.04),
            "SOL/USDT": pd.Series(np.random.randn(50) * 0.06),
        }
        weights = rp.portfolio_allocation(list(returns.keys()), returns)
        assert abs(sum(weights.values()) - 1.0) < 1e-10
        # Least volatile should get highest weight
        assert weights["BTC/USDT"] > weights["SOL/USDT"]


# ---------------------------------------------------------------------------
# CorrelationTracker
# ---------------------------------------------------------------------------


class TestCorrelationTracker:
    def test_import(self):
        from core.correlation_tracker import CorrelationTracker
        assert CorrelationTracker is not None

    def test_single_symbol(self):
        from core.correlation_tracker import CorrelationTracker
        ct = CorrelationTracker()
        returns = pd.Series(np.random.randn(50))
        ct.update("BTC/USDT", returns)
        matrix = ct.get_correlation_matrix()
        assert matrix.shape == (1, 1)
        assert float(matrix.iloc[0, 0]) == 1.0

    def test_correlated_assets(self):
        from core.correlation_tracker import CorrelationTracker
        ct = CorrelationTracker()
        np.random.seed(42)
        base = np.random.randn(100)
        # ETH highly correlated with BTC
        btc_returns = pd.Series(base + np.random.randn(100) * 0.1)
        eth_returns = pd.Series(base * 0.9 + np.random.randn(100) * 0.15)
        ct.update("BTC/USDT", btc_returns)
        ct.update("ETH/USDT", eth_returns)
        corr = ct.get_correlation("BTC/USDT", "ETH/USDT")
        assert corr > 0.7  # should be highly correlated

    def test_alerts_triggered(self):
        from core.correlation_tracker import CorrelationTracker
        ct = CorrelationTracker(alert_threshold=0.5)
        np.random.seed(42)
        base = np.random.randn(100)
        ct.update("A", pd.Series(base))
        ct.update("B", pd.Series(base + np.random.randn(100) * 0.05))
        alerts = ct.check_alerts()
        assert len(alerts) > 0

    def test_effective_position_count(self):
        from core.correlation_tracker import CorrelationTracker
        ct = CorrelationTracker()
        np.random.seed(42)
        base = np.random.randn(100)
        ct.update("A", pd.Series(base))
        ct.update("B", pd.Series(base + np.random.randn(100) * 0.1))
        positions = [{"symbol": "A"}, {"symbol": "B"}]
        effective = ct.effective_position_count(positions)
        # 2 highly correlated positions → effective count close to 1
        assert effective < 2.0


# ---------------------------------------------------------------------------
# TradeProtocol
# ---------------------------------------------------------------------------


class TestTradeProtocol:
    def test_import(self):
        from core.trade_protocol import TradeProtocol, ProtocolVerdict
        assert TradeProtocol is not None

    def test_no_signals_returns_skip(self):
        from core.trade_protocol import TradeProtocol, ProtocolVerdict
        tp = TradeProtocol()
        df = _make_trending_df(100)
        result = tp.evaluate("BTC/USDT", df, [], current_equity=10000)
        assert result.verdict == ProtocolVerdict.SKIP

    def test_with_signal_runs_full_protocol(self):
        from core.trade_protocol import TradeProtocol, ProtocolVerdict
        tp = TradeProtocol()
        df = _make_trending_df(100)
        signals = [{
            "direction": "LONG",
            "conviction": 0.8,
            "strategy_name": "ema_crossover",
            "stop_loss": 50000,
            "take_profit": 70000,
        }]
        result = tp.evaluate("BTC/USDT", df, signals, current_equity=10000)
        # Should either PROCEED or be rejected by a gate
        assert result.verdict in (
            ProtocolVerdict.PROCEED,
            ProtocolVerdict.REJECT_CONFLUENCE,
            ProtocolVerdict.REJECT_REGIME,
            ProtocolVerdict.REJECT_RISK,
            ProtocolVerdict.REJECT_SIZING,
        )
        assert len(result.steps_completed) >= 2  # at least regime + signal

    def test_max_drawdown_rejects(self):
        from core.trade_protocol import TradeProtocol, ProtocolVerdict
        tp = TradeProtocol()
        df = _make_trending_df(100)
        signals = [{"direction": "LONG", "conviction": 0.8, "strategy_name": "test",
                     "stop_loss": 50000, "take_profit": 70000}]
        result = tp.evaluate("BTC/USDT", df, signals, current_equity=10000,
                            max_drawdown_pct=-16.0)
        assert result.verdict == ProtocolVerdict.REJECT_RISK
