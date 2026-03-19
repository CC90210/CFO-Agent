"""
tests/test_infrastructure.py
-----------------------------
Tests for the core infrastructure: settings, database, models, risk state,
and engine initialisation.

These tests use only stdlib + SQLite — no exchange connection, no API keys
required. The test suite can run in CI with zero secrets.
"""

from __future__ import annotations

import datetime
import os

import pytest


# ─────────────────────────────────────────────────────────────────────────────
#  Settings
# ─────────────────────────────────────────────────────────────────────────────


class TestSettings:
    """Settings load correctly and defaults are safe."""

    def test_risk_defaults_are_conservative(self) -> None:
        from config.settings import Settings

        s = Settings()
        assert s.risk.max_drawdown_pct <= 15.0
        assert s.risk.daily_loss_limit_pct <= 5.0
        assert s.risk.per_trade_risk_pct <= 1.5

    def test_paper_trade_is_true_by_default(self) -> None:
        from config.settings import Settings

        # Ensure the env var isn't polluted from a real .env
        env_backup = os.environ.pop("PAPER_TRADE", None)
        try:
            s = Settings()
            assert s.exchange.paper_trade is True
            assert s.is_paper is True
        finally:
            if env_backup is not None:
                os.environ["PAPER_TRADE"] = env_backup

    def test_is_live_requires_both_flags(self) -> None:
        """is_live must be False when paper_trade=True regardless of confirm_live."""
        from config.settings import Settings

        s = Settings()
        # Default state: paper=True → never live
        assert s.is_live is False

    def test_live_trading_blocked_without_confirm_live(self) -> None:
        """Constructing ExchangeSettings with paper=False but confirm=False raises."""
        from pydantic import ValidationError

        from config.settings import ExchangeSettings

        with pytest.raises(ValidationError):
            ExchangeSettings(
                paper_trade=False,
                confirm_live=False,  # missing confirmation
                exchange_api_key="key",
                exchange_secret="secret",
            )

    def test_telegram_enabled_property(self) -> None:
        from config.settings import TelegramSettings

        t_no_token = TelegramSettings(telegram_bot_token="", telegram_chat_id="123")
        assert t_no_token.enabled is False

        t_full = TelegramSettings(
            telegram_bot_token="abc:xyz", telegram_chat_id="123456"
        )
        assert t_full.enabled is True


# ─────────────────────────────────────────────────────────────────────────────
#  Database — use in-memory SQLite for tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def in_memory_db(monkeypatch: pytest.MonkeyPatch):
    """
    Patch DATABASE_URL to an in-memory SQLite instance for tests.

    Yields the patched db module so tests can call init_db / get_session.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    # Force module re-initialisation with the patched URL
    import importlib

    import db.database as db_mod

    importlib.reload(db_mod)

    db_mod.init_db()
    yield db_mod
    # Clean up all tables between tests
    from db.models import Base
    engine = db_mod.get_engine()
    Base.metadata.drop_all(engine)


class TestDatabase:
    """Database setup and session management."""

    def test_init_db_creates_tables(self, in_memory_db: object) -> None:
        import db.database as db_mod
        from db.models import Base

        inspector = db_mod.get_engine().dialect.has_table  # type: ignore[attr-defined]
        # Verify key tables were created
        engine = db_mod.get_engine()
        from sqlalchemy import inspect as sa_inspect

        insp = sa_inspect(engine)
        tables = insp.get_table_names()
        assert "trades" in tables
        assert "signals" in tables
        assert "agent_performance" in tables
        assert "portfolio_snapshots" in tables
        assert "daily_pnl" in tables

    def test_health_check_passes(self, in_memory_db: object) -> None:
        import db.database as db_mod

        assert db_mod.health_check() is True

    def test_get_session_commits_on_success(self, in_memory_db: object) -> None:
        import db.database as db_mod
        from db.models import DailyPnL

        today = datetime.date.today()
        with db_mod.get_session() as session:
            session.add(
                DailyPnL(date=today, realized_pnl=100.0, trades_count=3)
            )

        # Read back in a separate session
        with db_mod.get_session() as session:
            record = session.query(DailyPnL).filter(DailyPnL.date == today).first()
            assert record is not None
            assert record.realized_pnl == pytest.approx(100.0)
            assert record.trades_count == 3

    def test_get_session_rolls_back_on_exception(self, in_memory_db: object) -> None:
        import db.database as db_mod
        from db.models import AgentPerformance

        with pytest.raises(RuntimeError):
            with db_mod.get_session() as session:
                session.add(AgentPerformance(agent_name="test_agent"))
                raise RuntimeError("intentional test failure")

        # Nothing should have been committed
        with db_mod.get_session() as session:
            count = session.query(AgentPerformance).count()
            assert count == 0


# ─────────────────────────────────────────────────────────────────────────────
#  Models
# ─────────────────────────────────────────────────────────────────────────────


class TestModels:
    """ORM model instantiation and basic constraints."""

    def test_trade_repr(self) -> None:
        from db.models import Trade

        t = Trade(
            symbol="BTC/USDT",
            side="buy",
            size=0.01,
            entry_price=60000.0,
            strategy="ema_crossover",
        )
        assert "BTC/USDT" in repr(t)
        assert "ema_crossover" in repr(t)

    def test_portfolio_snapshot_repr(self) -> None:
        from db.models import PortfolioSnapshot

        ps = PortfolioSnapshot(
            timestamp=datetime.datetime.now(datetime.UTC),
            total_value=10_500.0,
            drawdown_pct=-2.1,
            positions_json=[],
        )
        assert "10500" in repr(ps)

    def test_daily_pnl_defaults(self, in_memory_db: object) -> None:
        import db.database as db_mod
        from db.models import DailyPnL

        unique_date = datetime.date(2020, 1, 1)
        with db_mod.get_session() as session:
            row = DailyPnL(date=unique_date)
            session.add(row)

        with db_mod.get_session() as session:
            row = session.query(DailyPnL).filter(DailyPnL.date == unique_date).one()
            assert row.realized_pnl == pytest.approx(0.0)
            assert row.trades_count == 0
            assert row.daily_limit_hit is False

    def test_agent_performance_unique_name(self, in_memory_db: object) -> None:
        import db.database as db_mod
        from db.models import AgentPerformance
        from sqlalchemy.exc import IntegrityError

        with db_mod.get_session() as session:
            session.add(AgentPerformance(agent_name="unique_agent"))

        with pytest.raises(IntegrityError):
            with db_mod.get_session() as session:
                session.add(AgentPerformance(agent_name="unique_agent"))


# ─────────────────────────────────────────────────────────────────────────────
#  Engine — risk state
# ─────────────────────────────────────────────────────────────────────────────


class TestRiskState:
    """Internal _RiskState logic (imported directly for unit testing)."""

    def _make_risk(self, equity: float = 10_000.0) -> object:
        from core.engine import _RiskState

        r = _RiskState(equity_peak=equity)
        r.update(current_equity=equity, daily_pnl=0.0, open_positions=0)
        return r

    def test_can_trade_when_healthy(self) -> None:
        risk = self._make_risk()
        allowed, reason = risk.can_trade()  # type: ignore[attr-defined]
        assert allowed is True
        assert reason == ""

    def test_drawdown_limit_blocks_trading(self) -> None:
        from core.engine import _RiskState

        risk = _RiskState(equity_peak=10_000.0)
        # Simulate 20% drawdown (> 15% limit)
        risk.update(current_equity=8_000.0, daily_pnl=-2_000.0, open_positions=0)
        allowed, reason = risk.can_trade()
        assert allowed is False
        assert "drawdown" in reason.lower()

    def test_daily_loss_limit_blocks_trading(self) -> None:
        from core.engine import _RiskState

        risk = _RiskState(equity_peak=10_000.0)
        # Simulate 6% daily loss (> 5% limit)
        risk.update(current_equity=10_000.0, daily_pnl=-600.0, open_positions=0)
        allowed, reason = risk.can_trade()
        assert allowed is False
        assert "daily" in reason.lower()

    def test_position_limit_blocks_trading(self) -> None:
        from core.engine import _RiskState

        risk = _RiskState(equity_peak=10_000.0)
        # Simulate max positions already open
        risk.update(current_equity=10_000.0, daily_pnl=0.0, open_positions=5)
        allowed, reason = risk.can_trade()
        assert allowed is False
        assert "position" in reason.lower()

    def test_equity_peak_tracks_high_watermark(self) -> None:
        from core.engine import _RiskState

        risk = _RiskState(equity_peak=10_000.0)
        risk.update(current_equity=11_000.0, daily_pnl=0.0, open_positions=0)
        assert risk.equity_peak == pytest.approx(11_000.0)

        # Drawdown from new peak
        risk.update(current_equity=10_000.0, daily_pnl=0.0, open_positions=0)
        assert risk.drawdown_pct == pytest.approx(
            (10_000.0 - 11_000.0) / 11_000.0 * 100.0
        )

    def test_reset_daily_clears_daily_pnl(self) -> None:
        from core.engine import _RiskState

        risk = _RiskState(equity_peak=10_000.0)
        risk.update(current_equity=10_000.0, daily_pnl=-600.0, open_positions=0)
        assert risk.daily_limit_hit is True

        risk.reset_daily()
        assert risk.daily_pnl == pytest.approx(0.0)
        assert risk.daily_limit_hit is False


# ─────────────────────────────────────────────────────────────────────────────
#  Engine — strategy loading
# ─────────────────────────────────────────────────────────────────────────────


class TestStrategyLoading:
    """TradingEngine._load_strategies parses strategies.yaml correctly."""

    def _make_engine(self, strategy_names: list[str]) -> object:
        from core.engine import TradingEngine, TradingMode

        return TradingEngine(
            mode=TradingMode.PAPER,
            strategy_names=strategy_names,
        )

    def test_load_all_strategies(self) -> None:
        engine = self._make_engine(["all"])
        engine._load_strategies()  # type: ignore[attr-defined]
        assert len(engine._strategies) > 0  # type: ignore[attr-defined]

    def test_load_specific_strategy(self) -> None:
        engine = self._make_engine(["rsi_mean_reversion"])
        engine._load_strategies()  # type: ignore[attr-defined]
        assert "rsi_mean_reversion" in engine._strategies  # type: ignore[attr-defined]

    def test_unknown_strategy_raises(self) -> None:
        engine = self._make_engine(["no_such_strategy_xyz"])
        with pytest.raises(ValueError, match="No enabled strategies"):
            engine._load_strategies()  # type: ignore[attr-defined]

    def test_loaded_strategies_have_symbols(self) -> None:
        engine = self._make_engine(["rsi_mean_reversion"])
        engine._load_strategies()  # type: ignore[attr-defined]
        config = engine._strategies["rsi_mean_reversion"]  # type: ignore[attr-defined]
        assert "symbols" in config
        assert len(config["symbols"]) > 0

    def test_tick_interval_seconds_returns_positive_int(self) -> None:
        engine = self._make_engine(["rsi_mean_reversion"])
        engine._load_strategies()  # type: ignore[attr-defined]
        interval = engine._tick_interval_seconds()  # type: ignore[attr-defined]
        assert isinstance(interval, int)
        assert interval > 0
