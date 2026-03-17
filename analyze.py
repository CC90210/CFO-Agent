"""
analyze.py
----------
Standalone multi-agent analysis tool for Atlas Trading Agent.

Runs all four analyst agents (Technical, Sentiment, Fundamentals, News)
against a single symbol, triggers the Bull/Bear debate if signals conflict,
and prints a comprehensive analysis report.

NO trades are executed. This is a pure analysis/research tool.

Usage
-----
    python analyze.py BTC/USDT
    python analyze.py ETH/USDT --exchange binance --timeframe 4h
    python analyze.py AAPL --exchange alpaca --timeframe 1d

Output
------
A full terminal report covering:
  - Live market data summary
  - Per-agent conviction scores and reasoning
  - Weighted consensus and debate outcome (if triggered)
  - Final recommendation with confidence level
  - Key risk factors from the RiskAgent
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import logging
import sys
from pathlib import Path
from typing import Any

# Force UTF-8 output on Windows to support box-drawing characters.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# Ensure the project root is on sys.path when run as a script.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ─────────────────────────────────────────────────────────────────────────────
#  Logging — minimal output so the report is readable
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
# Show only critical engine errors; suppress routine INFO chatter
logging.getLogger("atlas").setLevel(logging.ERROR)

# ─────────────────────────────────────────────────────────────────────────────
#  Project imports
# ─────────────────────────────────────────────────────────────────────────────

from agents.base_agent import AgentSignal, Direction  # noqa: E402
from agents.debate import DebateEngine, DebateVerdict  # noqa: E402
from agents.fundamentals_analyst import FundamentalsAnalyst  # noqa: E402
from agents.news_analyst import NewsAnalyst  # noqa: E402
from agents.risk_agent import RiskAgent, RiskAssessment  # noqa: E402
from agents.sentiment_analyst import SentimentAnalyst  # noqa: E402
from agents.technical_analyst import TechnicalAnalyst  # noqa: E402
from config.settings import settings  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
#  Report rendering helpers
# ─────────────────────────────────────────────────────────────────────────────

_LINE_WIDTH = 68


def _hr(char: str = "─") -> str:
    return char * _LINE_WIDTH


def _section(title: str) -> str:
    pad = _LINE_WIDTH - len(title) - 2
    left = pad // 2
    right = pad - left
    return f"{'─' * left}  {title}  {'─' * right}"


def _conviction_bar(conviction: float, width: int = 20) -> str:
    """
    Render a compact ASCII conviction bar.

    Negative values extend left (bearish), positive right (bullish).
    Centre is always shown as '|'.

    Example for +0.72:  "          |##########          "
    Example for -0.45:  "     ######|                    "
    """
    half = width // 2
    scaled = int(abs(conviction) * half)
    scaled = min(scaled, half)

    if conviction >= 0:
        bar = " " * half + "|" + "#" * scaled + " " * (half - scaled)
    else:
        bar = " " * (half - scaled) + "#" * scaled + "|" + " " * half

    return f"[{bar}]"


def _direction_label(direction: Direction, conviction: float) -> str:
    """Return a padded direction label with strength indicator."""
    strength = abs(conviction)
    if strength >= 0.7:
        qualifier = "STRONG"
    elif strength >= 0.4:
        qualifier = "MODERATE"
    else:
        qualifier = "WEAK"

    if direction == Direction.NEUTRAL:
        return "  NEUTRAL"
    return f"  {qualifier} {direction.value}"


def _wrap(text: str, indent: int = 4, max_width: int = _LINE_WIDTH) -> str:
    """Word-wrap ``text`` to ``max_width`` with ``indent``-space continuation."""
    words = text.split()
    lines: list[str] = []
    current = " " * indent
    for word in words:
        if len(current) + len(word) + 1 > max_width:
            lines.append(current.rstrip())
            current = " " * indent + word + " "
        else:
            current += word + " "
    if current.strip():
        lines.append(current.rstrip())
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  Market data helpers
# ─────────────────────────────────────────────────────────────────────────────


async def _fetch_ohlcv(
    symbol: str,
    exchange_id: str,
    timeframe: str,
    limit: int = 200,
) -> tuple[list[list[float]], float]:
    """
    Fetch OHLCV bars from the exchange using CCXT async.

    Returns ``(ohlcv_rows, latest_close)`` where each row is
    ``[timestamp_ms, open, high, low, close, volume]``.

    Raises ``RuntimeError`` on connection or data errors so the caller
    can print a clean error message.
    """
    try:
        import ccxt.async_support as ccxt_async  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError("ccxt is not installed. Run: pip install ccxt") from exc

    exchange_class = getattr(ccxt_async, exchange_id, None)
    if exchange_class is None:
        raise RuntimeError(
            f"Unknown exchange: '{exchange_id}'. "
            "Check the CCXT exchange list at https://github.com/ccxt/ccxt"
        )

    _placeholders = {"", "your_exchange_api_key_here", "your_exchange_secret_here"}
    init_params: dict[str, Any] = {"enableRateLimit": True}
    api_key = settings.exchange.exchange_api_key
    api_secret = settings.exchange.exchange_secret
    if api_key and api_key not in _placeholders:
        init_params["apiKey"] = api_key
    if api_secret and api_secret not in _placeholders:
        init_params["secret"] = api_secret

    exchange = exchange_class(init_params)

    try:
        ohlcv: list[list[float]] = await exchange.fetch_ohlcv(
            symbol, timeframe, limit=limit
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch OHLCV for {symbol}: {exc}") from exc
    finally:
        await exchange.close()

    if not ohlcv:
        raise RuntimeError(f"Exchange returned 0 candles for {symbol} / {timeframe}")

    latest_close = float(ohlcv[-1][4])
    return ohlcv, latest_close


def _build_market_data(
    ohlcv: list[list[float]],
    symbol: str,
    exchange_id: str,
    timeframe: str,
) -> dict[str, Any]:
    """Convert raw CCXT OHLCV rows to the market_data dict expected by agents."""
    import pandas as pd  # noqa: PLC0415

    df = pd.DataFrame(
        ohlcv,
        columns=["timestamp", "open", "high", "low", "close", "volume"],
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    price_change_24h = float(latest["close"] - prev["close"])
    price_change_pct_24h = (price_change_24h / float(prev["close"]) * 100.0) if prev["close"] else 0.0

    return {
        "ohlcv": df.reset_index().to_dict(orient="records"),
        "symbol": symbol,
        "exchange": exchange_id,
        "timeframe": timeframe,
        "latest_close": float(latest["close"]),
        "latest_volume": float(latest["volume"]),
        "high_24h": float(df["high"].iloc[-24:].max()) if len(df) >= 24 else float(df["high"].max()),
        "low_24h": float(df["low"].iloc[-24:].min()) if len(df) >= 24 else float(df["low"].min()),
        "price_change_24h": price_change_24h,
        "price_change_pct_24h": price_change_pct_24h,
        "candles_fetched": len(df),
        # Portfolio/trade context required by RiskAgent
        "portfolio": {
            "total_equity": 10_000.0,
            "available_balance": 10_000.0,
            "open_positions": [],
            "daily_pnl_pct": 0.0,
            "drawdown_pct": 0.0,
        },
        "proposed_trade": {
            "symbol": symbol,
            "direction": "long",
            "size_usd": 150.0,
            "signal_conviction": 0.5,
        },
        "market_conditions": {
            "volatility": "normal",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Consensus calculation
# ─────────────────────────────────────────────────────────────────────────────

_SKIP_DEBATE_THRESHOLD = 0.75


def _weighted_consensus(signals: list[AgentSignal]) -> float:
    """
    Compute a simple confidence-weighted consensus conviction score.

    Mirrors the logic in ``agents/orchestrator.py`` but without Darwinian
    weights (which require trade history — not relevant for one-shot analysis).
    """
    total_weight = sum(s.confidence for s in signals)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(s.conviction * s.confidence for s in signals)
    return max(-1.0, min(1.0, weighted_sum / total_weight))


# ─────────────────────────────────────────────────────────────────────────────
#  Report printing
# ─────────────────────────────────────────────────────────────────────────────


def _print_header(symbol: str, exchange_id: str, timeframe: str, market_data: dict[str, Any]) -> None:
    price = market_data.get("latest_close", 0.0)
    change = market_data.get("price_change_pct_24h", 0.0)
    high = market_data.get("high_24h", 0.0)
    low = market_data.get("low_24h", 0.0)
    candles = market_data.get("candles_fetched", 0)
    sign = "+" if change >= 0 else ""

    print()
    print(_hr("═"))
    print(f"  ATLAS MULTI-AGENT ANALYSIS")
    print(_hr("═"))
    print(f"  Symbol    : {symbol}")
    print(f"  Exchange  : {exchange_id}")
    print(f"  Timeframe : {timeframe}")
    print(f"  Price     : ${price:,.4f}  ({sign}{change:.2f}% last candle)")
    print(f"  Range     : ${low:,.4f} — ${high:,.4f}  ({candles} candles fetched)")
    print(f"  Timestamp : {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(_hr())


def _print_agent_section(signals: list[AgentSignal]) -> None:
    print()
    print(_section("ANALYST SIGNALS"))
    print()

    for sig in signals:
        bar = _conviction_bar(sig.conviction)
        direction_str = _direction_label(sig.direction, sig.conviction)
        print(f"  {sig.agent_name:<22}  {direction_str}")
        print(f"  {'':22}  Conviction: {sig.conviction:+.3f}  Confidence: {sig.confidence:.3f}")
        print(f"  {'':22}  {bar}")
        print()
        if sig.reasoning and sig.reasoning.strip():
            print(_wrap(sig.reasoning, indent=4))
        print(_hr("·"))


def _print_debate_section(verdict: DebateVerdict | None, consensus: float) -> None:
    print()
    print(_section("DEBATE ENGINE"))
    print()

    if verdict is None:
        strength = abs(consensus)
        direction = "BULLISH" if consensus > 0 else "BEARISH"
        print(f"  Debate SKIPPED — strong {direction} consensus ({consensus:+.3f})")
        print(f"  Consensus strength {strength:.2f} >= {_SKIP_DEBATE_THRESHOLD} threshold")
    else:
        print(f"  Debate RAN — signals were conflicted (consensus < {_SKIP_DEBATE_THRESHOLD})")
        print()
        print(f"  Verdict Direction : {verdict.direction.value}")
        print(f"  Verdict Conviction: {verdict.conviction:+.3f}")
        print(f"  Verdict Confidence: {verdict.confidence:.3f}")
        print()
        print(f"  Bull Strength : {verdict.bull_strength:.3f}")
        print(f"  Bear Strength : {verdict.bear_strength:.3f}")
        print()
        if verdict.reasoning_chain:
            print("  Debate Summary:")
            for step in verdict.reasoning_chain:
                print(_wrap(step, indent=4))
                print()
        if verdict.dissenting_view:
            print("  Dissenting View:")
            print(_wrap(verdict.dissenting_view, indent=4))


def _print_risk_section(risk: RiskAssessment) -> None:
    print()
    print(_section("RISK ASSESSMENT"))
    print()

    veto_label = f"YES — {risk.veto_reason.value}" if risk.vetoed else "No"
    print(f"  Risk Score       : {risk.risk_score:.1f} / 10")
    print(f"  Vetoed           : {veto_label}")
    print(f"  Portfolio Exposure: {risk.portfolio_exposure_pct * 100:.1f}%")
    print(f"  Daily P&L        : {risk.daily_pnl_pct:+.2f}%")
    print(f"  Current Drawdown : {risk.max_drawdown_pct:+.2f}%")
    print(f"  Recommended Size : {risk.recommended_size_pct * 100:.0f}% of max")

    if risk.warnings:
        print()
        print("  Warnings:")
        for w in risk.warnings:
            print(f"    • {w}")

    if risk.reasoning:
        print()
        print("  Risk Reasoning:")
        print(_wrap(risk.reasoning, indent=4))


def _print_recommendation(
    signals: list[AgentSignal],
    consensus: float,
    verdict: DebateVerdict | None,
    risk: RiskAssessment,
) -> None:
    print()
    print(_section("FINAL RECOMMENDATION"))
    print()

    # Derive final direction from debate or consensus
    if verdict is not None:
        final_direction = verdict.direction
        final_conviction = verdict.conviction
        final_confidence = verdict.confidence
    else:
        final_direction = Direction.LONG if consensus > 0 else (
            Direction.SHORT if consensus < 0 else Direction.NEUTRAL
        )
        final_conviction = consensus
        final_confidence = min(0.9, abs(consensus))

    # Override to NEUTRAL if risk vetoed
    action_blocked = risk.vetoed or risk.risk_score > 7.0

    if action_blocked:
        action = "DO NOT TRADE"
        reason = f"Risk veto: {risk.veto_reason.value}" if risk.vetoed else f"Risk score too high ({risk.risk_score:.1f}/10)"
    elif final_direction == Direction.NEUTRAL or abs(final_conviction) < 0.1:
        action = "HOLD / NO TRADE"
        reason = "Insufficient directional conviction"
    elif final_direction == Direction.LONG:
        action = "BUY / LONG"
        reason = f"Bullish consensus (conviction {final_conviction:+.3f})"
    else:
        action = "SELL / SHORT"
        reason = f"Bearish consensus (conviction {final_conviction:+.3f})"

    strength_label = (
        "HIGH" if final_confidence >= 0.7
        else "MEDIUM" if final_confidence >= 0.4
        else "LOW"
    )

    print(f"  Action     : {action}")
    print(f"  Reason     : {reason}")
    print(f"  Conviction : {final_conviction:+.3f}")
    print(f"  Confidence : {final_confidence:.3f}  ({strength_label})")
    print()

    # Quick bull/bear summary
    bulls = [s for s in signals if s.direction == Direction.LONG]
    bears = [s for s in signals if s.direction == Direction.SHORT]
    neutrals = [s for s in signals if s.direction == Direction.NEUTRAL]
    print(f"  Agent Vote : {len(bulls)} LONG  |  {len(bears)} SHORT  |  {len(neutrals)} NEUTRAL")

    print()
    print(_hr("═"))
    print("  DISCLAIMER: This is AI-generated analysis for paper trading only.")
    print("  Not financial advice. Always apply your own risk management.")
    print(_hr("═"))


# ─────────────────────────────────────────────────────────────────────────────
#  Core analysis runner
# ─────────────────────────────────────────────────────────────────────────────


async def run_analysis(
    symbol: str,
    exchange_id: str,
    timeframe: str,
) -> int:
    """
    Fetch market data, run all analyst agents and the debate engine,
    then print the full analysis report.

    Returns 0 on success, 1 on error.
    """
    print(f"\nFetching market data for {symbol} from {exchange_id}...")

    # 1. Fetch OHLCV
    try:
        ohlcv, latest_close = await _fetch_ohlcv(symbol, exchange_id, timeframe)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Fetched {len(ohlcv)} candles. Latest close: ${latest_close:,.4f}")
    print("Running agents...")

    market_data = _build_market_data(ohlcv, symbol, exchange_id, timeframe)

    # 2. Instantiate agents
    technical = TechnicalAnalyst()
    sentiment = SentimentAnalyst()
    fundamentals = FundamentalsAnalyst()
    news = NewsAnalyst()
    debate_engine = DebateEngine()
    risk_agent = RiskAgent()

    analysts = [technical, sentiment, fundamentals, news]

    # 3. Run all analysts concurrently — failures yield NEUTRAL (never crash)
    raw_results = await asyncio.gather(
        *[agent.analyze(symbol, market_data) for agent in analysts],
        return_exceptions=True,
    )

    signals: list[AgentSignal] = []
    for agent, result in zip(analysts, raw_results):
        if isinstance(result, Exception):
            signals.append(AgentSignal.neutral(agent.name, reason=str(result)))
        else:
            signals.append(result)  # type: ignore[arg-type]

    # 4. Compute weighted consensus
    consensus = _weighted_consensus(signals)

    # 5. Run debate only if signals conflict
    verdict: DebateVerdict | None = None
    if abs(consensus) < _SKIP_DEBATE_THRESHOLD:
        try:
            verdict = await debate_engine.run_debate(symbol, signals, {})
        except Exception as exc:  # noqa: BLE001
            # Debate failure is non-fatal — fall back to consensus
            print(f"  Debate engine unavailable: {exc}")

    # 6. Risk assessment (uses placeholder portfolio state — analysis only)
    try:
        risk_assessment = await risk_agent.assess_risk(symbol, market_data, {})
    except Exception as exc:  # noqa: BLE001
        # Build a minimal safe fallback so the report can still print
        from agents.risk_agent import VetoReason  # noqa: PLC0415

        risk_assessment = RiskAssessment(
            vetoed=False,
            veto_reason=VetoReason.NO_VETO,
            risk_score=0.0,
            recommended_size_pct=1.0,
            reasoning=f"Risk agent unavailable: {exc}",
            portfolio_exposure_pct=0.0,
            daily_pnl_pct=0.0,
            max_drawdown_pct=0.0,
            warnings=[],
        )

    # 7. Print full report
    _print_header(symbol, exchange_id, timeframe, market_data)
    _print_agent_section(signals)
    _print_debate_section(verdict, consensus)
    _print_risk_section(risk_assessment)
    _print_recommendation(signals, consensus, verdict, risk_assessment)

    return 0


# ─────────────────────────────────────────────────────────────────────────────
#  CLI argument parsing
# ─────────────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze",
        description="Atlas — standalone multi-agent analysis (no trades executed)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "symbol",
        help="Market symbol to analyse (e.g. BTC/USDT, ETH/USDT, AAPL).",
    )
    parser.add_argument(
        "--exchange",
        default=None,
        help="CCXT exchange id (default: value from .env / settings).",
    )
    parser.add_argument(
        "--timeframe",
        default="1h",
        choices=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        help="Candle timeframe for technical analysis (default: 1h).",
    )
    return parser


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    exchange_id: str = args.exchange or settings.exchange.default_exchange

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        exit_code = asyncio.run(run_analysis(args.symbol, exchange_id, args.timeframe))
    except KeyboardInterrupt:
        print("\nAnalysis interrupted.")
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
