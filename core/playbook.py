"""
core/playbook.py
-----------------
Atlas Trading Playbook — the master decision matrix.

This module encodes ALL trading wisdom, lessons learned, and decision rules
into a queryable playbook that any strategy or agent can consult.

The playbook answers two questions:
  1. "Given the current conditions, SHOULD I trade?" (PlaybookVerdict)
  2. "If yes, HOW should I trade?" (PlaybookGuidance)

Architecture
------------
The Playbook is a rule engine, not a strategy. It sits ABOVE the strategies
and provides meta-level guidance based on:
  - Market regime (bull/bear/choppy/high-vol)
  - Session timing (Asian/London/NY overlap)
  - Volatility context (compressed/normal/expanded/extreme)
  - Correlation environment (diversified vs concentrated)
  - Recent performance (winning streak / losing streak)
  - Economic calendar (macro events)
  - Sentiment extremes (fear/greed)

Each rule is a simple predicate → adjustment pair. Rules compose additively.

Usage
-----
    playbook = TradingPlaybook()
    guidance = playbook.evaluate(
        regime="BULL_TREND",
        volatility="NORMAL",
        session="LONDON",
        recent_win_rate=0.55,
        consecutive_losses=0,
        fear_greed=45,
        macro_event_today=False,
        correlation_level=0.65,
    )
    print(guidance.size_multiplier)   # 1.0 (no adjustment)
    print(guidance.preferred_strategies)  # ["ema_crossover", "multi_timeframe"]
    print(guidance.avoid_strategies)      # ["bollinger_squeeze"]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("atlas.playbook")


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class TradingSession(str, Enum):
    """Global trading sessions by UTC time."""
    ASIAN = "ASIAN"           # 00:00 - 08:00 UTC
    LONDON = "LONDON"         # 08:00 - 16:00 UTC
    NEW_YORK = "NEW_YORK"     # 13:00 - 21:00 UTC
    OVERLAP = "OVERLAP"       # 13:00 - 16:00 UTC (London + NY)
    OFF_HOURS = "OFF_HOURS"   # 21:00 - 00:00 UTC


class VolatilityContext(str, Enum):
    COMPRESSED = "COMPRESSED"  # BB squeeze, ATR at lows
    NORMAL = "NORMAL"
    EXPANDED = "EXPANDED"      # Post-breakout, ATR elevated
    EXTREME = "EXTREME"        # Black swan, ATR > 3x normal


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class PlaybookGuidance:
    """The playbook's recommendation for current conditions."""

    # Should we trade at all?
    should_trade: bool = True
    avoid_reason: str = ""

    # Position sizing adjustments
    size_multiplier: float = 1.0  # multiply against proposed size

    # Strategy preferences
    preferred_strategies: list[str] = field(default_factory=list)
    avoid_strategies: list[str] = field(default_factory=list)

    # Entry style
    prefer_limit_orders: bool = False  # vs market orders
    entry_patience: str = "NORMAL"     # "AGGRESSIVE", "NORMAL", "PATIENT"

    # Exit style
    trailing_stop_method: str = "chandelier"
    trailing_stop_multiplier: float = 3.0
    scale_out_enabled: bool = True

    # Risk adjustments
    max_concurrent_positions: int = 5
    max_correlation_for_new_entry: float = 0.70

    # Reasoning trail
    rules_applied: list[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.should_trade:
            return f"NO TRADE: {self.avoid_reason}"
        parts = [
            f"size={self.size_multiplier:.2f}x",
            f"patience={self.entry_patience}",
            f"trail={self.trailing_stop_method}@{self.trailing_stop_multiplier:.1f}x",
        ]
        if self.preferred_strategies:
            parts.append(f"prefer={self.preferred_strategies}")
        if self.avoid_strategies:
            parts.append(f"avoid={self.avoid_strategies}")
        return " | ".join(parts)


# ---------------------------------------------------------------------------
# Playbook Rules
# ---------------------------------------------------------------------------


class TradingPlaybook:
    """
    Master decision matrix encoding all trading wisdom.

    Call evaluate() with the current market state and get back actionable
    guidance for the trading engine.
    """

    def evaluate(
        self,
        regime: str = "CHOPPY",
        volatility: str = "NORMAL",
        session: str = "LONDON",
        recent_win_rate: float = 0.50,
        consecutive_losses: int = 0,
        consecutive_wins: int = 0,
        fear_greed: int = 50,
        macro_event_today: bool = False,
        macro_event_within_24h: bool = False,
        correlation_level: float = 0.50,
        current_drawdown_pct: float = 0.0,
        daily_pnl_pct: float = 0.0,
        open_positions: int = 0,
    ) -> PlaybookGuidance:
        """
        Evaluate current conditions and return trading guidance.

        All parameters are optional with neutral defaults.
        """
        g = PlaybookGuidance()

        # ── Rule 1: Regime-based strategy selection ────────────────────
        self._rule_regime(g, regime)

        # ── Rule 2: Volatility-based adjustments ──────────────────────
        self._rule_volatility(g, volatility)

        # ── Rule 3: Session timing ─────────────────────────────────────
        self._rule_session(g, session)

        # ── Rule 4: Recent performance (tilt/streak) ──────────────────
        self._rule_performance(g, recent_win_rate, consecutive_losses, consecutive_wins)

        # ── Rule 5: Sentiment extremes ─────────────────────────────────
        self._rule_sentiment(g, fear_greed)

        # ── Rule 6: Macro event protection ─────────────────────────────
        self._rule_macro(g, macro_event_today, macro_event_within_24h)

        # ── Rule 7: Correlation concentration ──────────────────────────
        self._rule_correlation(g, correlation_level, open_positions)

        # ── Rule 8: Drawdown protection ────────────────────────────────
        self._rule_drawdown(g, current_drawdown_pct, daily_pnl_pct)

        # Clamp size multiplier
        g.size_multiplier = max(0.1, min(2.0, g.size_multiplier))

        logger.info("Playbook: %s", g.summary())
        return g

    # ------------------------------------------------------------------
    # Individual rule implementations
    # ------------------------------------------------------------------

    def _rule_regime(self, g: PlaybookGuidance, regime: str) -> None:
        """Map market regime to strategy preferences."""
        regime = regime.upper()

        if regime == "BULL_TREND":
            g.preferred_strategies = [
                "ema_crossover", "multi_timeframe", "ichimoku_trend",
            ]
            g.avoid_strategies = ["zscore_mean_reversion"]
            g.trailing_stop_multiplier = 3.5  # wider for trends
            g.entry_patience = "NORMAL"
            g.rules_applied.append("BULL: trend-followers preferred, wider stops")

        elif regime == "BEAR_TREND":
            g.preferred_strategies = [
                "rsi_mean_reversion", "zscore_mean_reversion",
            ]
            g.avoid_strategies = [
                "ema_crossover", "multi_timeframe", "ichimoku_trend",
            ]
            g.size_multiplier *= 0.7  # smaller positions in bear
            g.trailing_stop_multiplier = 2.5  # tighter for reversals
            g.entry_patience = "PATIENT"  # wait for better entries
            g.rules_applied.append("BEAR: mean-reversion preferred, 70% size, patient entries")

        elif regime == "CHOPPY":
            g.preferred_strategies = [
                "rsi_mean_reversion", "vwap_bounce", "volume_profile",
            ]
            g.avoid_strategies = [
                "ema_crossover", "ichimoku_trend", "bollinger_squeeze",
            ]
            g.size_multiplier *= 0.8
            g.trailing_stop_multiplier = 2.0  # tight for mean-reversion
            g.entry_patience = "PATIENT"
            g.rules_applied.append("CHOPPY: mean-reversion only, 80% size")

        elif regime == "HIGH_VOL":
            g.size_multiplier *= 0.5  # half size in high vol
            g.max_concurrent_positions = 3  # fewer positions
            g.trailing_stop_multiplier = 4.0  # wide stops to survive
            g.entry_patience = "PATIENT"
            g.avoid_strategies = ["bollinger_squeeze", "london_breakout"]
            g.rules_applied.append("HIGH_VOL: 50% size, max 3 positions, wide stops")

    def _rule_volatility(self, g: PlaybookGuidance, volatility: str) -> None:
        volatility = volatility.upper()

        if volatility == "COMPRESSED":
            # Squeeze environment — breakout strategies shine
            if "bollinger_squeeze" not in g.avoid_strategies:
                g.preferred_strategies.append("bollinger_squeeze")
            g.entry_patience = "PATIENT"  # wait for the pop
            g.rules_applied.append("COMPRESSED: breakout strategies, wait for pop")

        elif volatility == "EXTREME":
            g.size_multiplier *= 0.4  # 40% of normal
            g.should_trade = g.size_multiplier > 0.15  # stop at extreme reduction
            if not g.should_trade:
                g.avoid_reason = "Extreme volatility — risk too high"
            g.rules_applied.append("EXTREME_VOL: 40% size")

    def _rule_session(self, g: PlaybookGuidance, session: str) -> None:
        session = session.upper()

        if session == "OVERLAP":
            # London + NY overlap = highest volume = best fills
            g.size_multiplier *= 1.1  # slight boost
            g.prefer_limit_orders = False  # market orders fine
            g.rules_applied.append("OVERLAP: +10% size, market orders OK")

        elif session == "ASIAN":
            # Asian session = lower volume, wider spreads in crypto
            g.size_multiplier *= 0.9
            g.prefer_limit_orders = True  # limit orders for better fills
            g.rules_applied.append("ASIAN: -10% size, prefer limit orders")

            # London breakout only viable approaching London open
            if "london_breakout" not in g.avoid_strategies:
                g.avoid_strategies.append("london_breakout")

        elif session == "OFF_HOURS":
            g.size_multiplier *= 0.7
            g.prefer_limit_orders = True
            g.rules_applied.append("OFF_HOURS: -30% size, limit orders only")

    def _rule_performance(
        self,
        g: PlaybookGuidance,
        win_rate: float,
        consecutive_losses: int,
        consecutive_wins: int,
    ) -> None:
        # Losing streak protection (tilt guard)
        if consecutive_losses >= 5:
            g.should_trade = False
            g.avoid_reason = f"5+ consecutive losses ({consecutive_losses}) — step away"
            g.rules_applied.append("TILT_GUARD: 5+ losses, halt trading")
            return

        if consecutive_losses >= 3:
            g.size_multiplier *= 0.6
            g.entry_patience = "PATIENT"
            g.rules_applied.append(f"LOSING_STREAK: {consecutive_losses} losses, 60% size, patient")

        # Winning streak caution (overconfidence guard)
        if consecutive_wins >= 5:
            g.size_multiplier *= 0.8  # slightly reduce (winners get sloppy)
            g.rules_applied.append("WIN_STREAK: 5+ wins, slight size reduction (overconfidence guard)")

        # Poor overall win rate → tighter risk
        if win_rate < 0.35 and win_rate > 0:
            g.size_multiplier *= 0.7
            g.rules_applied.append(f"LOW_WIN_RATE: {win_rate:.0%}, 70% size")

    def _rule_sentiment(self, g: PlaybookGuidance, fear_greed: int) -> None:
        if fear_greed < 15:
            # Extreme fear → contrarian buy signal BUT with reduced size
            g.size_multiplier *= 0.7  # still cautious
            g.preferred_strategies = [
                s for s in g.preferred_strategies
            ] + ["rsi_mean_reversion", "zscore_mean_reversion"]
            g.rules_applied.append("EXTREME_FEAR: contrarian opportunity, 70% size")

        elif fear_greed > 85:
            # Extreme greed → reduce exposure significantly
            g.size_multiplier *= 0.5
            g.avoid_strategies.extend(["ema_crossover", "multi_timeframe"])
            g.rules_applied.append("EXTREME_GREED: reduce exposure 50%, avoid trend-following")

        elif fear_greed > 75:
            g.size_multiplier *= 0.8
            g.rules_applied.append("HIGH_GREED: slight caution, 80% size")

    def _rule_macro(
        self,
        g: PlaybookGuidance,
        event_today: bool,
        event_within_24h: bool,
    ) -> None:
        if event_today:
            g.should_trade = False
            g.avoid_reason = "High-impact macro event today (FOMC/NFP/CPI) — no new entries"
            g.rules_applied.append("MACRO_HALT: event today, no trading")
            return

        if event_within_24h:
            g.size_multiplier *= 0.5
            g.max_concurrent_positions = min(g.max_concurrent_positions, 2)
            g.rules_applied.append("MACRO_CAUTION: event within 24h, 50% size, max 2 positions")

    def _rule_correlation(
        self,
        g: PlaybookGuidance,
        avg_correlation: float,
        open_positions: int,
    ) -> None:
        if avg_correlation > 0.85 and open_positions >= 2:
            # All positions are effectively the same trade
            g.max_concurrent_positions = min(g.max_concurrent_positions, 2)
            g.max_correlation_for_new_entry = 0.60  # tighter threshold
            g.rules_applied.append(
                f"HIGH_CORRELATION: avg={avg_correlation:.2f}, max 2 positions, "
                f"new entry threshold tightened to 0.60"
            )
        elif avg_correlation > 0.70:
            g.max_concurrent_positions = min(g.max_concurrent_positions, 3)
            g.rules_applied.append(
                f"MODERATE_CORRELATION: avg={avg_correlation:.2f}, max 3 positions"
            )

    def _rule_drawdown(
        self,
        g: PlaybookGuidance,
        current_dd_pct: float,
        daily_pnl_pct: float,
    ) -> None:
        # Progressive size reduction as drawdown deepens
        if current_dd_pct >= 12.0:
            g.size_multiplier *= 0.3
            g.max_concurrent_positions = 1
            g.rules_applied.append("DEEP_DD: 12%+ drawdown, 30% size, 1 position max")
        elif current_dd_pct >= 8.0:
            g.size_multiplier *= 0.5
            g.max_concurrent_positions = 2
            g.rules_applied.append("MODERATE_DD: 8%+ drawdown, 50% size, 2 positions max")
        elif current_dd_pct >= 5.0:
            g.size_multiplier *= 0.7
            g.rules_applied.append("MILD_DD: 5%+ drawdown, 70% size")

        # Daily loss approaching limit
        if daily_pnl_pct <= -3.5:
            g.size_multiplier *= 0.5
            g.rules_applied.append("DAILY_LOSS: -3.5%+, 50% size")
        elif daily_pnl_pct <= -2.0:
            g.size_multiplier *= 0.7
            g.rules_applied.append("DAILY_LOSS: -2%+, 70% size")


# ---------------------------------------------------------------------------
# Session detection utility
# ---------------------------------------------------------------------------


def detect_session(utc_hour: int) -> TradingSession:
    """
    Determine the current trading session from UTC hour.

    Parameters
    ----------
    utc_hour : hour of the day in UTC (0-23)

    Returns
    -------
    TradingSession enum value
    """
    if 13 <= utc_hour < 16:
        return TradingSession.OVERLAP
    if 8 <= utc_hour < 16:
        return TradingSession.LONDON
    if 13 <= utc_hour < 21:
        return TradingSession.NEW_YORK
    if 0 <= utc_hour < 8:
        return TradingSession.ASIAN
    return TradingSession.OFF_HOURS
