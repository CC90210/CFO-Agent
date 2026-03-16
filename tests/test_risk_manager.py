"""
tests/test_risk_manager.py — Unit tests for core/risk_manager.py.

Tests verify every safety guarantee documented in risk_manager.py:
1. Max drawdown kill switch triggers at/above the limit.
2. Daily loss limit triggers.
3. Position count limit is enforced.
4. Correlated positions are rejected when count exceeds threshold.
5. HARD CAP: max_drawdown_pct can NEVER exceed _FLOOR_MAX_DRAWDOWN_PCT (15 %).
   If the environment configures a looser value it is silently clamped to 15 %.
6. Per-trade risk cap is applied.
7. Kill switch stays on once activated (can only be cleared by reset).
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from strategies.base import Direction, Position, Signal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_risk_manager(
    portfolio_value: float = 10_000.0,
    correlations: dict | None = None,
) -> object:
    """Build a RiskManager using the real settings (conservative defaults)."""
    from core.risk_manager import RiskManager

    return RiskManager(portfolio_value=portfolio_value, correlations=correlations)


def _make_signal(
    symbol: str = "BTC/USDT",
    direction: Direction = Direction.LONG,
    conviction: float = 0.6,
    entry_price: float = 65_000.0,
    stop_loss: float = 63_000.0,
    take_profit: float = 71_000.0,
) -> Signal:
    return Signal(
        symbol=symbol,
        direction=direction,
        conviction=conviction,
        stop_loss=stop_loss,
        take_profit=take_profit,
        strategy_name="test_strategy",
        metadata={"entry_price": entry_price},
    )


def _make_position(
    symbol: str = "BTC/USDT",
    side: Direction = Direction.LONG,
    entry_price: float = 65_000.0,
    size: float = 0.01,
) -> Position:
    return Position(
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        size=size,
        stop_loss=entry_price * 0.95,
        take_profit=entry_price * 1.10,
        entry_time=datetime.utcnow(),
        strategy="test_strategy",
    )


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------


class TestRiskManagerInit:
    def test_positive_portfolio_value_required(self) -> None:
        from core.risk_manager import RiskManager

        with pytest.raises(ValueError, match="portfolio_value must be positive"):
            RiskManager(portfolio_value=0.0)

    def test_is_not_halted_on_init(self) -> None:
        rm = _make_risk_manager()
        assert rm.is_halted is False

    def test_open_positions_empty_on_init(self) -> None:
        rm = _make_risk_manager()
        assert len(rm.open_positions) == 0


# ---------------------------------------------------------------------------
# Max drawdown kill switch
# ---------------------------------------------------------------------------


class TestMaxDrawdownKillSwitch:
    def test_trade_approved_when_drawdown_below_limit(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        signal = _make_signal(entry_price=65_000.0, stop_loss=63_000.0)
        # 3% drawdown — well below 15% drawdown limit AND 5% daily loss limit.
        # Also set the day-start equity to match so daily loss is 0%.
        rm._starting_day_equity = 9_700.0  # no daily loss
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=9_700.0,
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert result.approved is True

    def test_kill_switch_triggers_at_max_drawdown(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        signal = _make_signal(entry_price=65_000.0, stop_loss=63_000.0)
        # Simulate 16% drawdown (exceeds 15% floor)
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=8_400.0,
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert result.approved is False
        assert "drawdown" in result.reason.lower()

    def test_kill_switch_stays_active_after_trigger(self) -> None:
        """Once kill switch trips, ALL subsequent trades are blocked."""
        rm = _make_risk_manager(portfolio_value=10_000.0)
        signal = _make_signal(entry_price=65_000.0, stop_loss=63_000.0)

        # First call: trips the kill switch
        rm.validate_trade(
            signal=signal,
            portfolio_value=8_400.0,
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert rm.is_halted is True

        # Second call: also blocked even with "healthy" equity (state stuck)
        result2 = rm.validate_trade(
            signal=signal,
            portfolio_value=10_000.0,  # equity "recovered" — but kill switch stays
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert result2.approved is False

    def test_drawdown_limit_cannot_exceed_15_pct(self) -> None:
        """
        The hard cap of 15 % must hold regardless of RiskSettings configuration.

        We patch the settings to claim max_drawdown_pct=50 (dangerously loose).
        The RiskManager must clamp it to 15 and trigger the kill switch at 15 %.
        """
        from config.settings import RiskSettings
        from core.risk_manager import RiskManager

        loose_settings = RiskSettings(
            max_drawdown_pct=50.0,   # attempt to set loose limit
            daily_loss_limit_pct=20.0,
            per_trade_risk_pct=10.0,
            max_open_positions=50,
        )
        with patch("core.risk_manager.settings") as mock_settings:
            mock_settings.risk = loose_settings
            rm = RiskManager(portfolio_value=10_000.0)

        # The effective limit must be 15 (the floor), not 50
        assert rm.max_drawdown_pct <= 15.0

    def test_drawdown_kill_switch_at_exactly_15_pct(self) -> None:
        """Kill switch should fire at exactly the 15 % floor."""
        from config.settings import RiskSettings
        from core.risk_manager import RiskManager

        # Use the default settings (max_drawdown_pct = 15.0)
        rm = RiskManager(portfolio_value=10_000.0)
        signal = _make_signal(entry_price=65_000.0, stop_loss=63_000.0)

        # Exactly 15 % drawdown: 10_000 * 0.85 = 8_500
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=8_500.0,
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert result.approved is False


# ---------------------------------------------------------------------------
# Daily loss limit
# ---------------------------------------------------------------------------


class TestDailyLossLimit:
    def test_daily_loss_limit_triggers(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        signal = _make_signal(entry_price=65_000.0, stop_loss=63_000.0)

        # Simulate 6% daily loss (exceeds 5% floor)
        rm._starting_day_equity = 10_000.0
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=9_380.0,  # ~6.2% loss
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert result.approved is False
        assert "daily" in result.reason.lower()

    def test_daily_loss_limit_cannot_exceed_5_pct_cap(self) -> None:
        """
        Daily loss limit is capped at _FLOOR_DAILY_LOSS_PCT (5 %).

        RiskSettings itself caps at 20 % via Pydantic validation, but the
        RiskManager further clamps to the 5 % floor. We use the maximum
        Pydantic-allowed value (20 %) and verify RiskManager still clamps to 5 %.
        """
        from config.settings import RiskSettings
        from core.risk_manager import RiskManager

        loose = RiskSettings(
            max_drawdown_pct=15.0,
            daily_loss_limit_pct=20.0,   # max Pydantic allows; RiskManager clamps to 5
            per_trade_risk_pct=1.5,
            max_open_positions=5,
        )
        with patch("core.risk_manager.settings") as mock_settings:
            mock_settings.risk = loose
            rm = RiskManager(portfolio_value=10_000.0)

        assert rm.daily_loss_limit_pct <= 5.0

    def test_daily_halt_lifted_on_daily_reset(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        signal = _make_signal(entry_price=65_000.0, stop_loss=63_000.0)

        # Trip daily limit
        rm._starting_day_equity = 10_000.0
        rm.validate_trade(
            signal=signal,
            portfolio_value=9_380.0,
            proposed_size=0.01,
            current_atr=500.0,
            normal_atr=500.0,
        )
        assert rm.is_halted is True

        # Reset daily state — should lift the daily halt
        rm.reset_daily_state(new_equity=9_380.0)
        assert rm.is_halted is False


# ---------------------------------------------------------------------------
# Position count limit
# ---------------------------------------------------------------------------


class TestPositionCountLimit:
    def test_position_count_limit_enforced(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        # Fill up to max positions
        for i in range(rm.max_open_positions):
            rm.register_open_position(
                _make_position(symbol=f"ASSET{i}/USDT", entry_price=100.0)
            )

        signal = _make_signal(
            symbol="NEWASSET/USDT", entry_price=100.0, stop_loss=95.0, take_profit=115.0
        )
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=10_000.0,
            proposed_size=1.0,
            current_atr=1.0,
            normal_atr=1.0,
        )
        assert result.approved is False
        assert "position" in result.reason.lower()

    def test_position_count_limit_respected_after_close(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        pos = _make_position(symbol="BTC/USDT", entry_price=65_000.0)
        rm.register_open_position(pos)

        # Fill remaining slots
        for i in range(1, rm.max_open_positions):
            rm.register_open_position(
                _make_position(symbol=f"ASSET{i}/USDT", entry_price=100.0)
            )

        # Close one position
        rm.close_position("BTC/USDT", exit_price=66_000.0)

        # Now a new trade should be approved (one slot free)
        signal = _make_signal(
            symbol="NEWTHING/USDT",
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=115.0,
        )
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=10_000.0,
            proposed_size=0.5,
            current_atr=1.0,
            normal_atr=1.0,
        )
        assert result.approved is True


# ---------------------------------------------------------------------------
# Correlated position rejection
# ---------------------------------------------------------------------------


class TestCorrelationRejection:
    def test_highly_correlated_new_position_rejected(self) -> None:
        """Adding a 4th position correlated with 3 existing ones should be rejected."""
        correlations = {
            "ETH/USDT": {"BNB/USDT": 0.85, "SOL/USDT": 0.80, "AVAX/USDT": 0.78},
            "BNB/USDT": {"ETH/USDT": 0.85},
            "SOL/USDT": {"ETH/USDT": 0.80},
            "AVAX/USDT": {"ETH/USDT": 0.78},
        }
        rm = _make_risk_manager(portfolio_value=50_000.0, correlations=correlations)

        # Register 3 correlated LONG positions
        for sym in ["BNB/USDT", "SOL/USDT", "AVAX/USDT"]:
            rm.register_open_position(
                _make_position(symbol=sym, side=Direction.LONG, entry_price=100.0)
            )

        # Now try to add ETH/USDT (correlated with all 3)
        signal = _make_signal(
            symbol="ETH/USDT",
            direction=Direction.LONG,
            entry_price=3_000.0,
            stop_loss=2_800.0,
            take_profit=3_600.0,
        )
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=50_000.0,
            proposed_size=0.1,
            current_atr=100.0,
            normal_atr=100.0,
        )
        assert result.approved is False
        assert "correlated" in result.reason.lower()

    def test_uncorrelated_position_approved(self) -> None:
        """A position uncorrelated with existing ones should pass correlation check."""
        correlations: dict = {}  # no correlations registered → safe to trade
        rm = _make_risk_manager(portfolio_value=50_000.0, correlations=correlations)

        rm.register_open_position(
            _make_position(symbol="BTC/USDT", side=Direction.LONG, entry_price=65_000.0)
        )

        signal = _make_signal(
            symbol="GOLD/USDT",
            direction=Direction.LONG,
            entry_price=2_000.0,
            stop_loss=1_900.0,
            take_profit=2_300.0,
        )
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=50_000.0,
            proposed_size=0.5,
            current_atr=50.0,
            normal_atr=50.0,
        )
        assert result.approved is True


# ---------------------------------------------------------------------------
# Per-trade risk capping
# ---------------------------------------------------------------------------


class TestPerTradeRiskCap:
    def test_oversized_position_is_reduced(self) -> None:
        """
        A proposed size that passes exposure limits but exceeds per-trade risk
        should be reduced by the risk manager's per-trade risk cap.

        Setup:
          portfolio = 10,000
          entry = 100, stop = 99 (stop distance = $1 per unit)
          max_risk = 1.5% of 10,000 = $150
          max_units_from_risk = 150 / 1 = 150 units
          proposed = 200 units (notional = $20,000 — 200% of portfolio: blocked by exposure)

        Use a fractional size just under the 20% single-asset exposure limit
        but LARGER than the per-trade risk cap:
          proposed = 1.8 units at price=100 → notional = $180 (1.8% exposure — ok)
          stop distance = $1/unit → risk = $1.8
          BUT we force a very small stop distance to make the per-trade risk huge:
          entry=100, stop=99.99 (distance=$0.01) → risk per unit = $0.01
          proposed = 10 units → risk = $0.10 which is well within limits
          → This approach doesn't work: very small stop = small risk regardless of units.

        Correct approach: use entry=100, stop=95, proposed=5 units.
          notional = 500 (5% of portfolio → under 20% cap)
          risk = 5 * 5 = $25 → per_trade_risk_cap = 1.5% * 10000 = $150 → NOT exceeded
          → The risk cap won't fire because proposed risk < cap.

        To actually trigger the per-trade risk cap:
          risk_budget = 1.5% * 10,000 = $150
          stop_distance = 1 per unit
          max_units = 150 / 1 = 150
          proposed = 300 units, notional = 300 * 1 = $300 (3% exposure — within 20% cap)
        """
        rm = _make_risk_manager(portfolio_value=10_000.0)
        # entry_price=1, stop=0 → distance=1; 300 units → $300 notional (3% of 10k → within limit)
        signal = _make_signal(
            symbol="TEST/USDT",
            entry_price=1.0,
            stop_loss=0.001,   # distance = 0.999 ≈ $1
            take_profit=4.0,
        )
        # 300 units at $1 = $300 notional (3% of portfolio — within 20% cap)
        # Risk = 300 * 0.999 ≈ $300 >> per_trade_risk_cap of $150
        result = rm.validate_trade(
            signal=signal,
            portfolio_value=10_000.0,
            proposed_size=300.0,
            current_atr=0.1,
            normal_atr=0.1,
        )
        assert result.approved is True
        # Adjusted size must be smaller than proposed due to per-trade risk cap
        assert result.adjusted_size < 300.0
        # The actual risk should not exceed per_trade_risk_pct of portfolio
        risk_value = result.adjusted_size * abs(1.0 - 0.001)
        max_risk = 10_000.0 * (rm.per_trade_risk_pct / 100.0)
        assert risk_value <= max_risk * 1.01  # 1% tolerance for floating point


# ---------------------------------------------------------------------------
# Position PnL tracking
# ---------------------------------------------------------------------------


class TestPositionTracking:
    def test_close_position_returns_correct_pnl(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        pos = _make_position(
            symbol="BTC/USDT",
            side=Direction.LONG,
            entry_price=60_000.0,
            size=0.1,
        )
        rm.register_open_position(pos)
        pnl = rm.close_position("BTC/USDT", exit_price=62_000.0)
        # (62000 - 60000) * 0.1 = 200
        assert pnl == pytest.approx(200.0, abs=0.01)

    def test_close_position_short_pnl(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        pos = _make_position(
            symbol="ETH/USDT",
            side=Direction.SHORT,
            entry_price=3_000.0,
            size=1.0,
        )
        rm.register_open_position(pos)
        pnl = rm.close_position("ETH/USDT", exit_price=2_800.0)
        # (3000 - 2800) * 1.0 = 200
        assert pnl == pytest.approx(200.0, abs=0.01)

    def test_update_position_mark_triggers_stop_loss(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        pos = Position(
            symbol="BTC/USDT",
            side=Direction.LONG,
            entry_price=65_000.0,
            size=0.01,
            stop_loss=63_000.0,
            take_profit=71_000.0,
            entry_time=datetime.utcnow(),
            strategy="test",
        )
        rm.register_open_position(pos)

        exits = rm.update_position_mark("BTC/USDT", mark_price=62_000.0)
        from strategies.base import ExitReason
        assert any(sym == "BTC/USDT" and reason == ExitReason.STOP_LOSS for sym, reason in exits)

    def test_update_position_mark_triggers_take_profit(self) -> None:
        rm = _make_risk_manager(portfolio_value=10_000.0)
        pos = Position(
            symbol="BTC/USDT",
            side=Direction.LONG,
            entry_price=65_000.0,
            size=0.01,
            stop_loss=63_000.0,
            take_profit=71_000.0,
            entry_time=datetime.utcnow(),
            strategy="test",
        )
        rm.register_open_position(pos)

        exits = rm.update_position_mark("BTC/USDT", mark_price=72_000.0)
        from strategies.base import ExitReason
        assert any(sym == "BTC/USDT" and reason == ExitReason.TAKE_PROFIT for sym, reason in exits)
