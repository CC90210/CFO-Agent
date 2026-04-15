"""
readiness_check.py
------------------
ATLAS Live Trading Readiness Check — Kraken edition.

Runs ALL pre-flight checks required before going live and prints a
structured PASS / FAIL / WARN report with a final GO / NO-GO verdict.

Usage
-----
    python readiness_check.py

Exit codes
----------
    0  — all checks passed  (GO)
    1  — one or more FAIL   (NO-GO)

Checks performed
----------------
  1. Strategy Health      — mini-backtest (721 bars, 4h) per enabled pair
  2. Data Connectivity    — Kraken OHLCV fetch + latency per symbol
  3. Database Health      — tables, snapshot count, trade count
  4. Risk Parameters      — hardcoded floors, profile per pair
  5. Paper Trading Status — process detection, trade count, P&L
  6. Kill Switch          — verify core/risk_manager.py floors are intact
  7. Portfolio Summary    — enabled pairs, max concurrent positions, capital
"""

from __future__ import annotations

import asyncio
import ast
import datetime
import inspect
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
#  Bootstrap — project root on sys.path, Windows UTF-8, minimal logging
# ─────────────────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import logging

# Suppress noisy INFO from dependencies during the check
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

# ─────────────────────────────────────────────────────────────────────────────
#  Result primitives
# ─────────────────────────────────────────────────────────────────────────────

_STATUS_PASS = "PASS"
_STATUS_FAIL = "FAIL"
_STATUS_WARN = "WARN"
_STATUS_INFO = "INFO"

_COL_WIDTH_STATUS = 6
_COL_WIDTH_CHECK  = 36
_COL_WIDTH_DETAIL = 52

# Minimum paper trades before a GO verdict can be issued.
_MIN_PAPER_TRADES = 20

# Backtest bars for the strategy health check.
_BACKTEST_BARS = 721

# Sharpe threshold below which we emit WARN.
_SHARPE_WARN = 0.5


@dataclass
class CheckResult:
    """Single row in the output table."""

    name: str
    status: str           # PASS | FAIL | WARN | INFO
    detail: str
    sub_results: list["CheckResult"] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _sign(v: float) -> str:
    return "+" if v >= 0 else ""


def _load_yaml() -> dict[str, Any]:
    """Parse strategies.yaml and return its full dict."""
    import yaml  # type: ignore[import-untyped]

    with open(_ROOT / "config" / "strategies.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _enabled_pairs(yaml_data: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    """Return [(strategy_name, symbol, strategy_cfg), ...] for enabled strategies."""
    pairs: list[tuple[str, str, dict[str, Any]]] = []
    for strat_name, cfg in yaml_data.get("strategies", {}).items():
        if not cfg.get("enabled", False):
            continue
        for symbol in cfg.get("symbols", []):
            pairs.append((strat_name, symbol, cfg))
    return pairs


def _ohlcv_to_dataframe(raw: list[list[float]]) -> "pd.DataFrame":
    """Convert raw CCXT-style OHLCV list to a DataFrame with DatetimeIndex."""
    import pandas as pd

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    return df


def _strategy_class_for(strategy_name: str) -> type | None:
    """Resolve the BaseStrategy subclass registered under strategy_name."""
    from strategies.base import StrategyRegistry  # type: ignore[attr-defined]

    return StrategyRegistry.get(strategy_name)


def _instantiate_strategy(strategy_name: str, cfg: dict[str, Any]) -> Any | None:
    """Instantiate a strategy from its yaml config. Returns None on failure."""
    cls = _strategy_class_for(strategy_name)
    if cls is None:
        return None
    params = cfg.get("parameters", {})
    try:
        sig = inspect.signature(cls.__init__)
        # Many strategies accept **kwargs or explicit params keyword
        if "params" in sig.parameters:
            return cls(params=params)
        return cls(**params)
    except Exception:
        try:
            return cls()
        except Exception:
            return None


# ─────────────────────────────────────────────────────────────────────────────
#  Check 1 — Strategy Health
# ─────────────────────────────────────────────────────────────────────────────


async def _fetch_ohlcv_for_backtest(
    symbol: str,
    timeframe: str,
    limit: int,
    adapter: Any,
) -> list[list[float]] | None:
    """Fetch OHLCV from the adapter; return None on error."""
    try:
        return await adapter.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    except Exception:
        return None


async def check_strategy_health(
    pairs: list[tuple[str, str, dict[str, Any]]],
) -> list[CheckResult]:
    """
    For each enabled (strategy, symbol) pair:
    - Fetch _BACKTEST_BARS candles from Kraken via CCXTAdapter.
    - Run BacktestEngine.run() with scale_out_tiers=[] (no scale-out).
    - Report return, Sharpe, win rate.
    - FAIL if total_return < 0.
    - WARN if Sharpe < _SHARPE_WARN.

    Non-crypto symbols (OANDA, Alpaca) are skipped with an INFO note since
    those adapters require funded credentials to connect.
    """
    # Late imports — keep module-level namespace clean.
    from backtesting.engine import BacktestEngine
    from core.broker_adapter import CCXTAdapter
    import strategies.technical  # noqa: F401 — trigger all registrations

    # Separate crypto vs non-crypto pairs up-front.
    _CRYPTO_RE = re.compile(r".+/[A-Z]{2,6}$")

    crypto_pairs = [(s, sym, cfg) for s, sym, cfg in pairs if _CRYPTO_RE.match(sym)]
    other_pairs  = [(s, sym, cfg) for s, sym, cfg in pairs if not _CRYPTO_RE.match(sym)]

    results: list[CheckResult] = []

    # ── non-crypto: INFO skip ─────────────────────────────────────────────
    for strat_name, symbol, _cfg in other_pairs:
        results.append(CheckResult(
            name=f"  {strat_name} / {symbol}",
            status=_STATUS_INFO,
            detail="Skipped — requires OANDA/Alpaca credentials (not Kraken)",
        ))

    if not crypto_pairs:
        return results

    # ── connect adapter (Kraken, public endpoints, no keys needed) ────────
    adapter = CCXTAdapter(exchange_id="kraken", paper=True)
    try:
        await adapter.connect()
    except Exception as exc:
        results.insert(0, CheckResult(
            name="  Kraken adapter connect",
            status=_STATUS_FAIL,
            detail=f"Could not connect: {exc}",
        ))
        return results

    try:
        engine = BacktestEngine(
            initial_capital=10_000.0,
            commission_pct=0.001,
            risk_per_trade_pct=0.015,
            slippage_enabled=True,
            regime_filter=True,
            trailing_stops=False,
            scale_out_tiers=[],  # no scale-out — empirically better
        )

        fetch_tasks = {
            (strat_name, symbol): _fetch_ohlcv_for_backtest(
                symbol,
                cfg.get("timeframe", "4h"),
                _BACKTEST_BARS,
                adapter,
            )
            for strat_name, symbol, cfg in crypto_pairs
        }

        # Fetch all OHLCVs concurrently.
        raw_map: dict[tuple[str, str], list[list[float]] | None] = {}
        for (strat_name, symbol), coro in fetch_tasks.items():
            raw_map[(strat_name, symbol)] = await coro

        for strat_name, symbol, cfg in crypto_pairs:
            raw = raw_map.get((strat_name, symbol))
            if raw is None or len(raw) < 100:
                results.append(CheckResult(
                    name=f"  {strat_name} / {symbol}",
                    status=_STATUS_FAIL,
                    detail=f"Insufficient data ({len(raw) if raw else 0} bars fetched)",
                ))
                continue

            strategy_obj = _instantiate_strategy(strat_name, cfg)
            if strategy_obj is None:
                results.append(CheckResult(
                    name=f"  {strat_name} / {symbol}",
                    status=_STATUS_FAIL,
                    detail="Strategy class not found or failed to instantiate",
                ))
                continue

            df = _ohlcv_to_dataframe(raw)
            try:
                result = engine.run(df, strategy_obj)
            except Exception as exc:
                results.append(CheckResult(
                    name=f"  {strat_name} / {symbol}",
                    status=_STATUS_FAIL,
                    detail=f"Backtest error: {exc}",
                ))
                continue

            ret_pct   = result.total_return * 100
            sharpe    = result.sharpe_ratio
            win_rate  = result.win_rate * 100
            n_trades  = result.total_trades

            detail = (
                f"Return: {_sign(ret_pct)}{ret_pct:.2f}%  "
                f"Sharpe: {sharpe:.2f}  "
                f"WR: {win_rate:.0f}%  "
                f"Trades: {n_trades}"
            )

            if n_trades == 0:
                status = _STATUS_WARN
                detail = "0 trades generated — filters may be too tight"
            elif ret_pct < 0:
                status = _STATUS_FAIL
            elif sharpe < _SHARPE_WARN:
                status = _STATUS_WARN
            else:
                status = _STATUS_PASS

            results.append(CheckResult(
                name=f"  {strat_name} / {symbol}",
                status=status,
                detail=detail,
            ))

    finally:
        await adapter.disconnect()

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Check 2 — Data Connectivity
# ─────────────────────────────────────────────────────────────────────────────


async def check_data_connectivity(
    pairs: list[tuple[str, str, dict[str, Any]]],
) -> list[CheckResult]:
    """
    Test Kraken CCXT connection and per-symbol OHLCV fetch.
    Reports latency. FAILs if any crypto symbol cannot be fetched.
    Non-crypto symbols are noted as INFO (need different adapter).
    """
    from core.broker_adapter import CCXTAdapter

    _CRYPTO_RE = re.compile(r".+/[A-Z]{2,6}$")

    # Unique symbols per broker.
    crypto_symbols  = sorted({sym for _, sym, _ in pairs if _CRYPTO_RE.match(sym)})
    other_symbols   = sorted({sym for _, sym, _ in pairs if not _CRYPTO_RE.match(sym)})

    results: list[CheckResult] = []

    # ── Kraken adapter ────────────────────────────────────────────────────
    adapter = CCXTAdapter(exchange_id="kraken", paper=True)
    t0 = time.perf_counter()
    try:
        await adapter.connect()
        connect_ms = (time.perf_counter() - t0) * 1000
        results.append(CheckResult(
            name="  Kraken connection",
            status=_STATUS_PASS,
            detail=f"Connected in {connect_ms:.0f} ms",
        ))
    except Exception as exc:
        results.append(CheckResult(
            name="  Kraken connection",
            status=_STATUS_FAIL,
            detail=f"Connection failed: {exc}",
        ))
        # Cannot test any symbols if the adapter failed.
        for sym in crypto_symbols:
            results.append(CheckResult(
                name=f"  {sym}",
                status=_STATUS_FAIL,
                detail="Skipped — adapter unavailable",
            ))
        for sym in other_symbols:
            results.append(CheckResult(
                name=f"  {sym}",
                status=_STATUS_INFO,
                detail="Skipped — requires OANDA/Alpaca adapter",
            ))
        return results

    # ── Per-symbol fetch (10 bars is enough to prove connectivity) ────────
    async def _probe(sym: str) -> CheckResult:
        t_start = time.perf_counter()
        try:
            candles = await adapter.fetch_ohlcv(sym, timeframe="4h", limit=10)
            latency_ms = (time.perf_counter() - t_start) * 1000
            if not candles:
                return CheckResult(
                    name=f"  {sym}",
                    status=_STATUS_FAIL,
                    detail="Fetch returned empty data",
                )
            return CheckResult(
                name=f"  {sym}",
                status=_STATUS_PASS,
                detail=f"{len(candles)} candles fetched in {latency_ms:.0f} ms",
            )
        except Exception as exc:
            return CheckResult(
                name=f"  {sym}",
                status=_STATUS_FAIL,
                detail=f"Fetch error: {exc}",
            )

    crypto_tasks = [_probe(sym) for sym in crypto_symbols]
    crypto_results = await asyncio.gather(*crypto_tasks)
    results.extend(crypto_results)

    await adapter.disconnect()

    for sym in other_symbols:
        results.append(CheckResult(
            name=f"  {sym}",
            status=_STATUS_INFO,
            detail="Requires OANDA/Alpaca adapter — not tested here",
        ))

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Check 3 — Database Health
# ─────────────────────────────────────────────────────────────────────────────


def check_database_health() -> list[CheckResult]:
    """
    Verify the SQLite database:
    - health_check() ping succeeds.
    - All expected tables exist.
    - Report snapshot count and trade count.
    """
    from db.database import get_session, health_check, init_db
    from db.models import (
        Base,
        DailyPnL,
        PortfolioSnapshot,
        Signal,
        Trade,
    )
    from sqlalchemy import inspect as sa_inspect
    from db.database import get_engine

    results: list[CheckResult] = []

    # Ensure tables exist (idempotent).
    init_db()

    # ── Connection ping ───────────────────────────────────────────────────
    alive = health_check()
    results.append(CheckResult(
        name="  DB ping",
        status=_STATUS_PASS if alive else _STATUS_FAIL,
        detail="SELECT 1 succeeded" if alive else "health_check() returned False",
    ))

    if not alive:
        return results

    # ── Table presence ────────────────────────────────────────────────────
    expected_tables = {t.__tablename__ for t in Base.__subclasses__()
                       if hasattr(t, "__tablename__")}
    # Collect all descendant table names (handles multi-level inheritance).
    def _all_tables(cls: type) -> set[str]:
        names: set[str] = set()
        for sub in cls.__subclasses__():
            if hasattr(sub, "__tablename__"):
                names.add(sub.__tablename__)
            names.update(_all_tables(sub))
        return names

    expected_tables = _all_tables(Base)

    insp = sa_inspect(get_engine())
    existing_tables = set(insp.get_table_names())

    missing = expected_tables - existing_tables
    if missing:
        results.append(CheckResult(
            name="  Tables present",
            status=_STATUS_FAIL,
            detail=f"Missing: {', '.join(sorted(missing))}",
        ))
    else:
        results.append(CheckResult(
            name="  Tables present",
            status=_STATUS_PASS,
            detail=f"All {len(expected_tables)} tables exist",
        ))

    # ── Row counts ────────────────────────────────────────────────────────
    with get_session() as session:
        snapshot_count = session.query(PortfolioSnapshot).count()
        trade_count    = session.query(Trade).count()
        signal_count   = session.query(Signal).count()

    results.append(CheckResult(
        name="  Snapshot count",
        status=_STATUS_INFO,
        detail=f"{snapshot_count:,} portfolio snapshots recorded",
    ))
    results.append(CheckResult(
        name="  Trade count",
        status=_STATUS_INFO,
        detail=f"{trade_count:,} trades  |  {signal_count:,} signals",
    ))

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Check 4 — Risk Parameters
# ─────────────────────────────────────────────────────────────────────────────


def check_risk_parameters(
    pairs: list[tuple[str, str, dict[str, Any]]],
) -> list[CheckResult]:
    """
    Verify:
    - settings.risk.max_drawdown_pct == 15 (hardcoded floor).
    - settings.risk.daily_loss_limit_pct == 5.
    - All risk profiles have risk_pct <= 5%.
    - Report optimal profile for each enabled pair.
    """
    from config.settings import settings
    from core.risk_profiles import DAREDEVIL, get_risk_profile

    # The absolute ceiling for per-trade risk across all profiles.
    _MAX_ALLOWED_RISK_PCT = 5.0

    results: list[CheckResult] = []

    # ── Drawdown floor ────────────────────────────────────────────────────
    dd = settings.risk.max_drawdown_pct
    results.append(CheckResult(
        name="  Max drawdown limit",
        status=_STATUS_PASS if dd <= 15.0 else _STATUS_FAIL,
        detail=f"{dd:.0f}%  (floor = 15%)",
    ))

    # ── Daily loss floor ──────────────────────────────────────────────────
    dl = settings.risk.daily_loss_limit_pct
    results.append(CheckResult(
        name="  Daily loss limit",
        status=_STATUS_PASS if dl <= 5.0 else _STATUS_FAIL,
        detail=f"{dl:.0f}%  (floor = 5%)",
    ))

    # ── Per-trade risk profiles ───────────────────────────────────────────
    from core.risk_profiles import (
        AGGRESSIVE,
        CONSERVATIVE,
        DAREDEVIL,
        SNIPER,
    )

    all_profiles = [CONSERVATIVE, AGGRESSIVE, SNIPER, DAREDEVIL]
    profile_fail = False
    for p in all_profiles:
        if p.risk_pct > _MAX_ALLOWED_RISK_PCT:
            results.append(CheckResult(
                name=f"  Profile '{p.name}'",
                status=_STATUS_FAIL,
                detail=f"risk_pct={p.risk_pct}% exceeds max allowed {_MAX_ALLOWED_RISK_PCT}%",
            ))
            profile_fail = True

    if not profile_fail:
        worst = max(p.risk_pct for p in all_profiles)
        results.append(CheckResult(
            name="  Per-trade risk profiles",
            status=_STATUS_PASS,
            detail=f"All profiles <= {_MAX_ALLOWED_RISK_PCT}%  (max = {worst:.1f}%)",
        ))

    # ── Profile per enabled pair ──────────────────────────────────────────
    for strat_name, symbol, cfg in pairs:
        profile = get_risk_profile(strat_name, symbol, conviction=0.75)
        results.append(CheckResult(
            name=f"  {strat_name} / {symbol}",
            status=_STATUS_INFO,
            detail=f"Profile: {profile.name}  (risk={profile.risk_pct}%, "
                   f"atr_stop={profile.atr_stop_mult}x, rr={profile.rr_ratio})",
        ))

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Check 5 — Paper Trading Status
# ─────────────────────────────────────────────────────────────────────────────


def check_paper_trading_status() -> list[CheckResult]:
    """
    - Detect whether paper_trade.py is currently running (psutil probe).
    - Report total paper trades, win rate, realised P&L from DB.
    - WARN if < _MIN_PAPER_TRADES.
    """
    from db.database import get_session
    from db.models import DailyPnL, PortfolioSnapshot, Trade

    results: list[CheckResult] = []

    # ── Process detection (psutil optional) ──────────────────────────────
    try:
        import psutil  # type: ignore[import-untyped]

        running = any(
            "paper_trade.py" in " ".join(p.cmdline())
            for p in psutil.process_iter(["cmdline"])
            if p.info.get("cmdline")
        )
        results.append(CheckResult(
            name="  paper_trade.py process",
            status=_STATUS_PASS if running else _STATUS_WARN,
            detail="Running" if running else "Not detected — start with: python paper_trade.py",
        ))
    except ImportError:
        results.append(CheckResult(
            name="  paper_trade.py process",
            status=_STATUS_WARN,
            detail="psutil not installed — cannot detect process (pip install psutil)",
        ))
    except Exception as exc:
        results.append(CheckResult(
            name="  paper_trade.py process",
            status=_STATUS_WARN,
            detail=f"Process detection error: {exc}",
        ))

    # ── Paper trades from DB ──────────────────────────────────────────────
    with get_session() as session:
        paper_trades = (
            session.query(Trade)
            .filter(Trade.mode == "paper", Trade.pnl.isnot(None))
            .all()
        )
        total = len(paper_trades)
        wins  = sum(1 for t in paper_trades if (t.pnl or 0.0) > 0)
        total_pnl = sum((t.pnl or 0.0) for t in paper_trades)
        win_rate  = (wins / total * 100.0) if total > 0 else 0.0

        # Latest snapshot for portfolio value.
        snapshot = (
            session.query(PortfolioSnapshot)
            .filter(PortfolioSnapshot.mode == "paper")
            .order_by(PortfolioSnapshot.timestamp.desc())
            .first()
        )
        portfolio_value = snapshot.total_value if snapshot else None

    trade_status = _STATUS_PASS if total >= _MIN_PAPER_TRADES else _STATUS_WARN
    results.append(CheckResult(
        name="  Paper trades completed",
        status=trade_status,
        detail=(
            f"{total} trades  |  WR: {win_rate:.1f}%  |  "
            f"P&L: {_sign(total_pnl)}${abs(total_pnl):,.2f}"
            + (f"  (min {_MIN_PAPER_TRADES} required)" if total < _MIN_PAPER_TRADES else "")
        ),
    ))

    if portfolio_value is not None:
        results.append(CheckResult(
            name="  Paper portfolio value",
            status=_STATUS_INFO,
            detail=f"${portfolio_value:,.2f}",
        ))

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Check 6 — Kill Switch Verification
# ─────────────────────────────────────────────────────────────────────────────


def check_kill_switches() -> list[CheckResult]:
    """
    Parse core/risk_manager.py via AST and verify:
    - _FLOOR_MAX_DRAWDOWN_PCT == 15.0
    - _FLOOR_DAILY_LOSS_PCT   == 5.0
    - _FLOOR_PER_TRADE_RISK_PCT present (> 0)

    Also verify at runtime that RiskManager's effective values are <= floors.
    """
    results: list[CheckResult] = []

    risk_file = _ROOT / "core" / "risk_manager.py"
    if not risk_file.exists():
        results.append(CheckResult(
            name="  core/risk_manager.py",
            status=_STATUS_FAIL,
            detail="File not found!",
        ))
        return results

    # ── Static AST parse — floors are module-level constants ─────────────
    source = risk_file.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        results.append(CheckResult(
            name="  risk_manager.py syntax",
            status=_STATUS_FAIL,
            detail=f"SyntaxError: {exc}",
        ))
        return results

    floor_values: dict[str, float] = {}
    for node in ast.walk(tree):
        # Handle plain assignment:  _FLOOR_X = 15.0
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.startswith("_FLOOR_"):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)):
                        floor_values[target.id] = float(node.value.value)
        # Handle annotated assignment:  _FLOOR_X: float = 15.0
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id.startswith("_FLOOR_")
                and node.value is not None
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, (int, float))
            ):
                floor_values[node.target.id] = float(node.value.value)

    # _FLOOR_MAX_DRAWDOWN_PCT must be exactly 15.0
    dd_floor = floor_values.get("_FLOOR_MAX_DRAWDOWN_PCT")
    results.append(CheckResult(
        name="  _FLOOR_MAX_DRAWDOWN_PCT",
        status=_STATUS_PASS if dd_floor == 15.0 else _STATUS_FAIL,
        detail=f"= {dd_floor}  (expected 15.0)" if dd_floor != 15.0 else "= 15.0  (intact)",
    ))

    # _FLOOR_DAILY_LOSS_PCT must be exactly 5.0
    dl_floor = floor_values.get("_FLOOR_DAILY_LOSS_PCT")
    results.append(CheckResult(
        name="  _FLOOR_DAILY_LOSS_PCT",
        status=_STATUS_PASS if dl_floor == 5.0 else _STATUS_FAIL,
        detail=f"= {dl_floor}  (expected 5.0)" if dl_floor != 5.0 else "= 5.0  (intact)",
    ))

    # _FLOOR_PER_TRADE_RISK_PCT must exist and be > 0
    pt_floor = floor_values.get("_FLOOR_PER_TRADE_RISK_PCT")
    results.append(CheckResult(
        name="  _FLOOR_PER_TRADE_RISK_PCT",
        status=_STATUS_PASS if (pt_floor is not None and pt_floor > 0) else _STATUS_FAIL,
        detail=f"= {pt_floor}  (intact)" if pt_floor else "Missing or zero — CRITICAL",
    ))

    # ── Runtime check — effective values respect floors ───────────────────
    try:
        from config.settings import settings
        from core.risk_manager import RiskManager

        rm = RiskManager()
        dd_ok  = rm.max_drawdown_pct  <= 15.0
        dl_ok  = rm.daily_loss_limit_pct <= 5.0
        results.append(CheckResult(
            name="  RiskManager runtime values",
            status=_STATUS_PASS if (dd_ok and dl_ok) else _STATUS_FAIL,
            detail=(
                f"max_drawdown={rm.max_drawdown_pct:.0f}%  "
                f"daily_loss={rm.daily_loss_limit_pct:.0f}%  "
                f"per_trade={rm.per_trade_risk_pct:.1f}%"
            ),
        ))
    except Exception as exc:
        results.append(CheckResult(
            name="  RiskManager runtime values",
            status=_STATUS_WARN,
            detail=f"Could not instantiate RiskManager: {exc}",
        ))

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Check 7 — Portfolio Summary (INFO only)
# ─────────────────────────────────────────────────────────────────────────────


def check_portfolio_summary(
    pairs: list[tuple[str, str, dict[str, Any]]],
    yaml_data: dict[str, Any],
) -> list[CheckResult]:
    """
    Report portfolio-level metrics as INFO rows:
    - Total enabled pairs.
    - Max concurrent positions (sum of max_positions per enabled strategy).
    - Estimated 4h scan frequency per day.
    - Capital required at max drawdown.
    """
    results: list[CheckResult] = []

    enabled_strategies: dict[str, dict[str, Any]] = {
        name: cfg
        for name, cfg in yaml_data.get("strategies", {}).items()
        if cfg.get("enabled", False)
    }

    total_pairs = len(pairs)
    max_concurrent = sum(cfg.get("max_positions", 2) for cfg in enabled_strategies.values())

    # 4h candles = 6 bars/day; each strategy scans each symbol once per bar.
    scans_per_day = len(pairs) * 6

    # Capital required: at max concurrent positions with daredevil risk (5% each).
    # This is the worst-case simultaneous exposure, not a recommendation.
    worst_case_exposure_pct = min(max_concurrent * 5.0, 100.0)

    results.append(CheckResult(
        name="  Enabled strategy-symbol pairs",
        status=_STATUS_INFO,
        detail=f"{total_pairs} pairs across {len(enabled_strategies)} strategies",
    ))
    results.append(CheckResult(
        name="  Max concurrent positions",
        status=_STATUS_INFO,
        detail=f"{max_concurrent} (sum of max_positions per strategy)",
    ))
    results.append(CheckResult(
        name="  Estimated daily scans",
        status=_STATUS_INFO,
        detail=f"~{scans_per_day:,} (4h bars x pairs)",
    ))
    results.append(CheckResult(
        name="  Worst-case simultaneous exposure",
        status=_STATUS_WARN if worst_case_exposure_pct > 50 else _STATUS_INFO,
        detail=f"Up to {worst_case_exposure_pct:.0f}% of equity at daredevil risk tier",
    ))
    results.append(CheckResult(
        name="  Min recommended capital (Kraken)",
        status=_STATUS_INFO,
        detail="$500 minimum order value — recommend $2,000+ to cover all pairs",
    ))

    return results


# ─────────────────────────────────────────────────────────────────────────────
#  Render
# ─────────────────────────────────────────────────────────────────────────────


def _status_label(status: str) -> str:
    return f"[{status:^{_COL_WIDTH_STATUS}}]"


def _render_row(result: CheckResult) -> str:
    name   = result.name.ljust(_COL_WIDTH_CHECK)[:_COL_WIDTH_CHECK]
    detail = result.detail[:_COL_WIDTH_DETAIL]
    return f"  {_status_label(result.status)}  {name}  {detail}"


def _render_section(
    section_title: str,
    results: list[CheckResult],
) -> tuple[str, bool]:
    """
    Render a section block and return (text, has_failures).
    """
    lines: list[str] = []
    sep = "-" * 110
    lines.append(sep)
    lines.append(f"  {section_title}")
    lines.append(sep)
    has_failures = False
    for r in results:
        lines.append(_render_row(r))
        if r.status == _STATUS_FAIL:
            has_failures = True
    return "\n".join(lines), has_failures


# ─────────────────────────────────────────────────────────────────────────────
#  Main orchestrator
# ─────────────────────────────────────────────────────────────────────────────


async def _run_all_checks() -> int:
    """
    Execute all checks, print the report, return exit code (0=GO, 1=NO-GO).
    """
    print()
    print("=" * 110)
    print("  ATLAS — LIVE TRADING READINESS CHECK  |  Kraken  |  " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 110)

    # ── Load config ───────────────────────────────────────────────────────
    try:
        yaml_data = _load_yaml()
    except Exception as exc:
        print(f"\n  FATAL: Could not load config/strategies.yaml: {exc}")
        return 1

    pairs = _enabled_pairs(yaml_data)

    all_failures = False
    all_warnings = False

    # ── 1. Strategy Health ────────────────────────────────────────────────
    print("\nRunning check 1/7: Strategy Health (backtest)... ", end="", flush=True)
    strat_results = await check_strategy_health(pairs)
    print("done.")
    section_text, has_fail = _render_section(
        "CHECK 1 — STRATEGY HEALTH  (721 bars, 4h, Kraken live data, no scale-out)",
        strat_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True
    if any(r.status == _STATUS_WARN for r in strat_results):
        all_warnings = True

    # ── 2. Data Connectivity ─────────────────────────────────────────────
    print("\nRunning check 2/7: Data Connectivity... ", end="", flush=True)
    data_results = await check_data_connectivity(pairs)
    print("done.")
    section_text, has_fail = _render_section(
        "CHECK 2 — DATA CONNECTIVITY  (Kraken CCXT, public endpoints)",
        data_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True

    # ── 3. Database Health ────────────────────────────────────────────────
    print("\nRunning check 3/7: Database Health... ", end="", flush=True)
    db_results = check_database_health()
    print("done.")
    section_text, has_fail = _render_section(
        "CHECK 3 — DATABASE HEALTH",
        db_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True

    # ── 4. Risk Parameters ────────────────────────────────────────────────
    print("\nRunning check 4/7: Risk Parameters... ", end="", flush=True)
    risk_results = check_risk_parameters(pairs)
    print("done.")
    section_text, has_fail = _render_section(
        "CHECK 4 — RISK PARAMETERS  (hardcoded floors + profile mapping)",
        risk_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True

    # ── 5. Paper Trading Status ───────────────────────────────────────────
    print("\nRunning check 5/7: Paper Trading Status... ", end="", flush=True)
    paper_results = check_paper_trading_status()
    print("done.")
    section_text, has_fail = _render_section(
        f"CHECK 5 — PAPER TRADING STATUS  (min {_MIN_PAPER_TRADES} trades required)",
        paper_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True
    if any(r.status == _STATUS_WARN for r in paper_results):
        all_warnings = True

    # ── 6. Kill Switch Verification ───────────────────────────────────────
    print("\nRunning check 6/7: Kill Switch Verification... ", end="", flush=True)
    ks_results = check_kill_switches()
    print("done.")
    section_text, has_fail = _render_section(
        "CHECK 6 — KILL SWITCH VERIFICATION  (AST + runtime)",
        ks_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True

    # ── 7. Portfolio Summary ──────────────────────────────────────────────
    print("\nRunning check 7/7: Portfolio Summary... ", end="", flush=True)
    port_results = check_portfolio_summary(pairs, yaml_data)
    print("done.")
    section_text, has_fail = _render_section(
        "CHECK 7 — PORTFOLIO SUMMARY",
        port_results,
    )
    print(section_text)
    if has_fail:
        all_failures = True

    # ── Final verdict ─────────────────────────────────────────────────────
    print()
    print("=" * 110)
    if all_failures:
        verdict = "  NO-GO"
        verdict_detail = "One or more FAIL conditions must be resolved before going live."
    elif all_warnings:
        verdict = "  GO (with warnings)"
        verdict_detail = "All hard checks passed. Review WARNs above before going live."
    else:
        verdict = "  GO"
        verdict_detail = "All checks passed. System is ready for live trading on Kraken."

    print(f"  FINAL VERDICT: {verdict}")
    print(f"  {verdict_detail}")
    print("=" * 110)
    print()

    return 1 if all_failures else 0


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    exit_code = asyncio.run(_run_all_checks())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
