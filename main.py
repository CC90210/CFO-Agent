"""
main.py
-------
Atlas Trading Agent — CLI entry point.

Commands
--------
backtest     Run a historical backtest for a given strategy.
paper-trade  Run paper trading in real-time (no real orders placed).
live         Run live trading (requires --confirm-live flag AND PAPER_TRADE=false in .env).
analyze      Run the multi-agent AI analysis for a symbol and print the verdict.

Usage Examples
--------------
  python main.py backtest --strategy ema_crossover --symbol BTC/USDT --start 2024-01-01
  python main.py paper-trade --strategy all --exchange binance
  python main.py live --strategy momentum --exchange binance --confirm-live
  python main.py analyze --symbol BTC/USDT
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Force line-buffered stdout so daemon logs flush immediately to watchdog log files.
# On Windows, PYTHONUNBUFFERED alone doesn't fix file-redirected stdout.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)

# Ensure the project root is on sys.path when running as a script
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ─────────────────────────────────────────────────────────────────────────────
#  Logging — configure before any other project imports so all loggers
#  inherit the correct level from the environment.
# ─────────────────────────────────────────────────────────────────────────────


def _configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a consistent timestamped format."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Argument parsing
# ─────────────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level argument parser with sub-commands."""
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Atlas Trading Agent — AI-powered multi-strategy trader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Override log level (default: INFO).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── backtest ──────────────────────────────────────────────────────────────
    bt = subparsers.add_parser(
        "backtest",
        help="Run a vectorbt-powered historical backtest.",
    )
    bt.add_argument(
        "--strategy",
        required=True,
        help="Strategy name from config/strategies.yaml, or 'all' to test every enabled strategy.",
    )
    bt.add_argument(
        "--symbol",
        default=None,
        help="Override the symbols in strategies.yaml (e.g. BTC/USDT).",
    )
    bt.add_argument(
        "--start",
        default="2024-01-01",
        metavar="YYYY-MM-DD",
        help="Backtest start date (default: 2024-01-01).",
    )
    bt.add_argument(
        "--end",
        default=None,
        metavar="YYYY-MM-DD",
        help="Backtest end date (default: today).",
    )
    bt.add_argument(
        "--exchange",
        default=None,
        help="CCXT exchange id for historical data (default: from .env).",
    )
    bt.add_argument(
        "--capital",
        type=float,
        default=10_000.0,
        help="Starting capital in USDT (default: 10000).",
    )

    # ── paper-trade ───────────────────────────────────────────────────────────
    pt = subparsers.add_parser(
        "paper-trade",
        help="Run in paper-trading mode — analysis is live but no real orders.",
    )
    pt.add_argument(
        "--strategy",
        default="all",
        help="Strategy name or 'all' (default: all).",
    )
    pt.add_argument(
        "--exchange",
        default=None,
        help="CCXT exchange id (default: from .env).",
    )

    # ── live ──────────────────────────────────────────────────────────────────
    lv = subparsers.add_parser(
        "live",
        help="Run in live-trading mode. Requires --confirm-live AND PAPER_TRADE=false in .env.",
    )
    lv.add_argument(
        "--strategy",
        default="all",
        help="Strategy name or 'all' (default: all).",
    )
    lv.add_argument(
        "--exchange",
        default=None,
        help="CCXT exchange id (default: from .env).",
    )
    lv.add_argument(
        "--confirm-live",
        action="store_true",
        help="REQUIRED: explicit flag acknowledging that real money is at risk.",
    )

    # ── walk-forward ──────────────────────────────────────────────────────────
    wf = subparsers.add_parser(
        "walk-forward",
        help="Run walk-forward validation on a strategy (out-of-sample robustness test).",
    )
    wf.add_argument(
        "--strategy",
        required=True,
        help="Strategy name (e.g. ema_crossover). Must be registered in StrategyRegistry.",
    )
    wf.add_argument(
        "--symbol",
        default="BTC/USDT",
        help="Market symbol to fetch (default: BTC/USDT).",
    )
    wf.add_argument(
        "--start",
        default="2025-01-01",
        metavar="YYYY-MM-DD",
        help="Data start date (default: 2025-01-01).",
    )
    wf.add_argument(
        "--end",
        default=None,
        metavar="YYYY-MM-DD",
        help="Data end date (default: today).",
    )
    wf.add_argument(
        "--timeframe",
        default="4h",
        help="Candle timeframe (default: 4h).",
    )
    wf.add_argument(
        "--exchange",
        default=None,
        help="CCXT exchange id (default: from .env).",
    )
    wf.add_argument(
        "--train-bars",
        type=int,
        default=500,
        metavar="N",
        help="Bars in each training window (default: 500).",
    )
    wf.add_argument(
        "--test-bars",
        type=int,
        default=100,
        metavar="N",
        help="Bars in each test (OOS) window (default: 100).",
    )
    wf.add_argument(
        "--step-bars",
        type=int,
        default=50,
        metavar="N",
        help="Bars to advance the window each iteration (default: 50).",
    )
    wf.add_argument(
        "--capital",
        type=float,
        default=10_000.0,
        help="Starting capital per window in USDT (default: 10000).",
    )

    # ── analyze ───────────────────────────────────────────────────────────────
    az = subparsers.add_parser(
        "analyze",
        help="Run multi-agent AI analysis for a symbol and print the result.",
    )
    az.add_argument(
        "--symbol",
        required=True,
        help="Market symbol to analyze (e.g. BTC/USDT).",
    )
    az.add_argument(
        "--exchange",
        default=None,
        help="CCXT exchange id (default: from .env).",
    )
    az.add_argument(
        "--timeframe",
        default="1h",
        help="Candle timeframe for technical analysis (default: 1h).",
    )

    return parser


# ─────────────────────────────────────────────────────────────────────────────
#  Command handlers
# ─────────────────────────────────────────────────────────────────────────────


async def _cmd_backtest(args: argparse.Namespace) -> int:
    """Handle the ``backtest`` sub-command."""
    from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

    strategy_names = [args.strategy] if args.strategy != "all" else ["all"]

    engine = TradingEngine(
        mode=TradingMode.BACKTEST,
        strategy_names=strategy_names,
        exchange_id=args.exchange,
    )

    # Pass backtest-specific params through a thin protocol on the engine
    # (BacktestRunner receives them via engine._run_backtest → runner.run)
    engine._backtest_start = args.start  # type: ignore[attr-defined]
    engine._backtest_end = args.end  # type: ignore[attr-defined]
    engine._backtest_capital = args.capital  # type: ignore[attr-defined]
    engine._backtest_symbol = args.symbol  # type: ignore[attr-defined]

    await engine.start()
    return 0


async def _cmd_paper_trade(args: argparse.Namespace) -> int:
    """Handle the ``paper-trade`` sub-command."""
    from config.settings import settings  # noqa: PLC0415
    from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

    if not settings.exchange.paper_trade:
        # Safeguard: if the user has PAPER_TRADE=false but runs paper-trade
        # sub-command, warn but proceed safely.
        logging.warning(
            "PAPER_TRADE=false in .env but you ran 'paper-trade' — "
            "forcing paper mode for this run."
        )

    strategy_names = [args.strategy] if args.strategy != "all" else ["all"]

    engine = TradingEngine(
        mode=TradingMode.PAPER,
        strategy_names=strategy_names,
        exchange_id=args.exchange,
    )
    await engine.start()
    return 0


async def _cmd_live(args: argparse.Namespace) -> int:
    """Handle the ``live`` sub-command."""
    # Activate the full Atlas logging infrastructure (domain files, master log,
    # auto-flushing handlers) — replaces the basicConfig console-only setup.
    from utils.logger import setup_logging  # noqa: PLC0415
    setup_logging(force=True)

    from config.settings import settings  # noqa: PLC0415
    from core.engine import TradingEngine, TradingMode  # noqa: PLC0415

    # Double-gate: CLI flag AND environment variable must both be set
    if not args.confirm_live:
        print(
            "ERROR: Live trading requires the --confirm-live flag.\n"
            "This flag acknowledges that real funds are at risk.\n"
            "Re-run with: python main.py live --strategy ... --confirm-live",
            file=sys.stderr,
        )
        return 1

    if settings.exchange.paper_trade:
        print(
            "ERROR: PAPER_TRADE=true in your .env file.\n"
            "Set PAPER_TRADE=false AND CONFIRM_LIVE=true to enable live orders.",
            file=sys.stderr,
        )
        return 1

    if not settings.exchange.confirm_live:
        print(
            "ERROR: CONFIRM_LIVE is not set to true in your .env file.\n"
            "Set CONFIRM_LIVE=true to unlock live trading.",
            file=sys.stderr,
        )
        return 1

    strategy_names = [args.strategy] if args.strategy != "all" else ["all"]

    engine = TradingEngine(
        mode=TradingMode.LIVE,
        strategy_names=strategy_names,
        exchange_id=args.exchange,
    )
    await engine.start()
    return 0


async def _cmd_walk_forward(args: argparse.Namespace) -> int:
    """
    Handle the ``walk-forward`` sub-command.

    Fetches OHLCV data, runs WalkForwardValidator with fixed-bar rolling windows,
    and prints the full validation report including train/test correlation,
    overfitting score, and a DEPLOY / CAUTION / DO_NOT_DEPLOY recommendation.
    """
    from config.settings import settings  # noqa: PLC0415
    from backtesting.walk_forward import WalkForwardValidator  # noqa: PLC0415
    from strategies.base import StrategyRegistry  # noqa: PLC0415

    import pandas as pd  # noqa: PLC0415

    exchange_id = args.exchange or settings.exchange.default_exchange
    symbol: str = args.symbol
    timeframe: str = args.timeframe

    print(f"\nAtlas Walk-Forward Validation")
    print(f"Strategy : {args.strategy}")
    print(f"Symbol   : {symbol}")
    print(f"Exchange : {exchange_id}")
    print(f"Timeframe: {timeframe}")
    print(f"Windows  : train={args.train_bars} bars, test={args.test_bars} bars, step={args.step_bars} bars")
    print("─" * 60)

    # Discover and build strategy
    StrategyRegistry.discover()
    try:
        strategy = StrategyRegistry.build(args.strategy)
    except KeyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Fetch historical data
    try:
        import ccxt.async_support as ccxt_async  # type: ignore[import]  # noqa: PLC0415

        exchange_class = getattr(ccxt_async, exchange_id)
        exchange = exchange_class(
            {
                "apiKey": settings.exchange.exchange_api_key,
                "secret": settings.exchange.exchange_secret,
            }
        )

        start_ts = int(pd.Timestamp(args.start, tz="UTC").timestamp() * 1000)
        end_ts: int | None = (
            int(pd.Timestamp(args.end, tz="UTC").timestamp() * 1000) if args.end else None
        )

        try:
            # Fetch up to 2000 candles (sufficient for multiple WF windows)
            ohlcv: list[list[float]] = await exchange.fetch_ohlcv(
                symbol, timeframe, since=start_ts, limit=2000
            )
        finally:
            await exchange.close()

    except Exception as exc:
        print(f"ERROR fetching market data: {exc}", file=sys.stderr)
        return 1

    if len(ohlcv) < args.train_bars + args.test_bars:
        print(
            f"ERROR: Only {len(ohlcv)} candles fetched but "
            f"train_bars + test_bars = {args.train_bars + args.test_bars}. "
            "Try an earlier --start date or reduce window sizes.",
            file=sys.stderr,
        )
        return 1

    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    # Filter to requested date range if --end was specified
    if end_ts is not None:
        df = df[df.index <= pd.Timestamp(args.end, tz="UTC")]

    print(f"Fetched  : {len(df)} candles ({df.index[0].date()} → {df.index[-1].date()})")
    print()

    # Run walk-forward validation
    validator = WalkForwardValidator(
        train_bars=args.train_bars,
        test_bars=args.test_bars,
        step_bars=args.step_bars,
        initial_capital=args.capital,
    )

    try:
        result = validator.validate(df, strategy)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(validator.summary(result))
    return 0


async def _cmd_analyze(args: argparse.Namespace) -> int:
    """
    Handle the ``analyze`` sub-command.

    Runs a one-shot multi-agent analysis on the requested symbol and
    prints the aggregated verdict to stdout.
    """
    from config.settings import settings  # noqa: PLC0415

    exchange_id = args.exchange or settings.exchange.default_exchange
    symbol: str = args.symbol
    timeframe: str = args.timeframe

    print(f"\nAtlas Multi-Agent Analysis")
    print(f"Symbol   : {symbol}")
    print(f"Exchange : {exchange_id}")
    print(f"Timeframe: {timeframe}")
    print("─" * 50)

    # Fetch OHLCV for analysis
    try:
        import ccxt.async_support as ccxt_async  # type: ignore[import]

        exchange_class = getattr(ccxt_async, exchange_id)
        exchange = exchange_class(
            {
                "apiKey": settings.exchange.exchange_api_key,
                "secret": settings.exchange.exchange_secret,
            }
        )

        try:
            ohlcv: list[list[float]] = await exchange.fetch_ohlcv(
                symbol, timeframe, limit=200
            )
            print(f"Fetched  : {len(ohlcv)} candles")
        finally:
            await exchange.close()

    except Exception as exc:
        print(f"ERROR fetching market data: {exc}", file=sys.stderr)
        return 1

    # Build market_data dict for agents
    import pandas as pd  # noqa: PLC0415

    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    market_data: dict[str, object] = {
        "ohlcv": df.to_dict(orient="records"),
        "symbol": symbol,
        "exchange": exchange_id,
        "timeframe": timeframe,
        "latest_close": float(df["close"].iloc[-1]),
        "candles_fetched": len(df),
    }

    # Run technical analyst (always available; other agents need API keys)
    try:
        from agents.technical_analyst import TechnicalAnalyst  # noqa: PLC0415

        analyst = TechnicalAnalyst()
        signal = await analyst.analyze(symbol, market_data)

        print(f"\nTechnical Analyst")
        print(f"  Direction : {signal.direction.value}")
        print(f"  Conviction: {signal.conviction:+.3f}")
        print(f"  Confidence: {signal.confidence:.3f}")
        print(f"  Reasoning : {signal.reasoning[:200]}{'...' if len(signal.reasoning) > 200 else ''}")

    except Exception as exc:
        print(f"  TechnicalAnalyst error: {exc}", file=sys.stderr)

    print("\nAnalysis complete.")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    """Parse CLI args and dispatch to the appropriate async command handler."""
    parser = _build_parser()
    args = parser.parse_args()

    # Logging must be configured before any project code is imported
    _configure_logging(args.log_level)

    dispatch = {
        "backtest": _cmd_backtest,
        "paper-trade": _cmd_paper_trade,
        "live": _cmd_live,
        "analyze": _cmd_analyze,
        "walk-forward": _cmd_walk_forward,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    try:
        exit_code = asyncio.run(handler(args))
    except KeyboardInterrupt:
        logging.getLogger("atlas").info("Interrupted by user.")
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
