"""
core/sentiment_engine.py
------------------------
Unified Sentiment Engine for Atlas Trading Agent.

Aggregates sentiment signals from multiple sources into a single composite
score that the trading engine and agents can use to adjust conviction,
sizing, and trade gating.

Sources integrated:
  1. Fear & Greed Index (alternative.me) — crypto market emotion
  2. News sentiment (CryptoPanic, NewsAPI) — headline impact
  3. Reddit sentiment (r/cryptocurrency, r/wallstreetbets) — retail crowd
  4. Economic calendar (FOMC, NFP, CPI) — macro event risk
  5. Market breadth (advance/decline, % above 50 EMA) — market health
  6. CoinGecko trending/market data — momentum context

Composite score: -1.0 (extreme fear / bearish) to +1.0 (extreme greed / bullish)
The engine also outputs a risk_modifier (0.0 to 1.0) that the position sizer
should multiply against proposed sizes — it shrinks positions when sentiment
is extreme in either direction (contrarian) or when macro events are imminent.

Usage
-----
    engine = SentimentEngine()
    result = await engine.analyze("BTC/USDT")
    print(result.composite_score)    # -0.35 (mildly bearish)
    print(result.risk_modifier)      # 0.7 (reduce size by 30%)
    print(result.should_avoid_entry) # False
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("atlas.sentiment")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class SentimentResult:
    """Unified sentiment analysis result for a symbol."""

    symbol: str

    # Individual scores (-1.0 to 1.0)
    fear_greed_score: float = 0.0       # converted from 0-100 to -1 to 1
    news_score: float = 0.0             # average news impact
    reddit_score: float = 0.0           # social sentiment
    market_breadth_score: float = 0.0   # market health

    # Composite (-1.0 to 1.0)
    composite_score: float = 0.0

    # Risk modifier (0.0 to 1.0) — multiply against position size
    risk_modifier: float = 1.0

    # Flags
    should_avoid_entry: bool = False    # True when macro event imminent
    macro_event_today: bool = False
    extreme_fear: bool = False          # FGI < 20
    extreme_greed: bool = False         # FGI > 80

    # Raw data
    fear_greed_raw: int = 50
    news_count: int = 0
    upcoming_events: list[dict[str, Any]] = field(default_factory=list)

    # Reasoning trail
    reasoning: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """One-line summary for logging."""
        flags = []
        if self.extreme_fear:
            flags.append("EXTREME_FEAR")
        if self.extreme_greed:
            flags.append("EXTREME_GREED")
        if self.macro_event_today:
            flags.append("MACRO_EVENT")
        if self.should_avoid_entry:
            flags.append("AVOID_ENTRY")
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        return (
            f"{self.symbol} sentiment={self.composite_score:+.2f} "
            f"risk_mod={self.risk_modifier:.2f}{flag_str}"
        )


# ---------------------------------------------------------------------------
# SentimentEngine
# ---------------------------------------------------------------------------


class SentimentEngine:
    """
    Unified sentiment aggregator.

    Pulls data from NewsFetcher, EconomicCalendar, and MarketScanner,
    combines into a single composite sentiment score and risk modifier.

    The engine is designed to be called once per trading cycle (every few
    minutes) and its results cached by the caller.

    Parameters
    ----------
    fear_greed_weight : weight for Fear & Greed component (default 0.25)
    news_weight       : weight for news sentiment component (default 0.25)
    reddit_weight     : weight for Reddit sentiment component (default 0.15)
    breadth_weight    : weight for market breadth component (default 0.20)
    momentum_weight   : weight for price momentum context (default 0.15)
    """

    def __init__(
        self,
        fear_greed_weight: float = 0.25,
        news_weight: float = 0.25,
        reddit_weight: float = 0.15,
        breadth_weight: float = 0.20,
        momentum_weight: float = 0.15,
    ) -> None:
        self.weights = {
            "fear_greed": fear_greed_weight,
            "news": news_weight,
            "reddit": reddit_weight,
            "breadth": breadth_weight,
            "momentum": momentum_weight,
        }
        # Normalise weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    async def analyze(
        self,
        symbol: str,
        fear_greed_value: int = 50,
        news_items: list[dict[str, Any]] | None = None,
        reddit_sentiment: float = 0.0,
        market_breadth: dict[str, Any] | None = None,
        price_change_24h: float = 0.0,
        macro_event_today: bool = False,
        macro_event_within_hours: bool = False,
        upcoming_events: list[dict[str, Any]] | None = None,
    ) -> SentimentResult:
        """
        Compute unified sentiment for a symbol.

        All inputs are optional — the engine degrades gracefully when data
        sources are unavailable, using neutral defaults.

        Parameters
        ----------
        symbol                  : Trading pair, e.g. "BTC/USDT"
        fear_greed_value        : Fear & Greed Index (0-100)
        news_items              : List of news dicts with 'impact_estimate' key
        reddit_sentiment        : Reddit crowd sentiment (-1.0 to 1.0)
        market_breadth          : MarketBreadth.to_dict() output
        price_change_24h        : 24h price change percentage
        macro_event_today       : True if FOMC/NFP/CPI today
        macro_event_within_hours: True if major event within 24h
        upcoming_events         : List of event dicts for the result

        Returns
        -------
        SentimentResult
        """
        result = SentimentResult(
            symbol=symbol,
            fear_greed_raw=fear_greed_value,
            news_count=len(news_items) if news_items else 0,
            upcoming_events=upcoming_events or [],
        )

        # ── 1. Fear & Greed Index ──────────────────────────────────────
        # Convert 0-100 to -1.0 to 1.0
        # 0 = extreme fear (-1.0), 50 = neutral (0.0), 100 = extreme greed (1.0)
        fg_score = (fear_greed_value - 50) / 50.0
        fg_score = max(-1.0, min(1.0, fg_score))
        result.fear_greed_score = fg_score
        result.extreme_fear = fear_greed_value < 20
        result.extreme_greed = fear_greed_value > 80

        if result.extreme_fear:
            result.reasoning.append(
                f"EXTREME FEAR (FGI={fear_greed_value}) — historically good buy zone"
            )
        elif result.extreme_greed:
            result.reasoning.append(
                f"EXTREME GREED (FGI={fear_greed_value}) — reduce exposure, contrarian caution"
            )
        else:
            result.reasoning.append(f"FGI={fear_greed_value} → score={fg_score:+.2f}")

        # ── 2. News Sentiment ──────────────────────────────────────────
        if news_items:
            impacts = [
                item.get("impact_estimate", 0.0)
                for item in news_items
                if item.get("impact_estimate", 0.0) != 0.0
            ]
            news_score = sum(impacts) / len(impacts) if impacts else 0.0
            # Clamp
            news_score = max(-1.0, min(1.0, news_score))
        else:
            news_score = 0.0
        result.news_score = news_score
        result.reasoning.append(
            f"News: {result.news_count} items, avg impact={news_score:+.2f}"
        )

        # ── 3. Reddit Sentiment ────────────────────────────────────────
        reddit_score = max(-1.0, min(1.0, reddit_sentiment))
        result.reddit_score = reddit_score
        result.reasoning.append(f"Reddit sentiment={reddit_score:+.2f}")

        # ── 4. Market Breadth ──────────────────────────────────────────
        breadth_score = 0.0
        if market_breadth:
            pct_above_ema = market_breadth.get("pct_above_50ema", 0.5)
            ad_ratio = market_breadth.get("advance_decline_ratio", 1.0)
            # Convert to -1 to 1
            breadth_score = (pct_above_ema - 0.5) * 2.0  # 0.7 → +0.4, 0.3 → -0.4
            # Adjust by A/D ratio
            if ad_ratio > 2.0:
                breadth_score += 0.2
            elif ad_ratio < 0.5:
                breadth_score -= 0.2
            breadth_score = max(-1.0, min(1.0, breadth_score))
        result.market_breadth_score = breadth_score
        result.reasoning.append(f"Market breadth={breadth_score:+.2f}")

        # ── 5. Momentum Context ────────────────────────────────────────
        # Use 24h price change as momentum proxy
        # ±5% = ±1.0 score
        momentum_score = max(-1.0, min(1.0, price_change_24h / 5.0))

        # ── Composite Score ────────────────────────────────────────────
        composite = (
            fg_score * self.weights["fear_greed"]
            + news_score * self.weights["news"]
            + reddit_score * self.weights["reddit"]
            + breadth_score * self.weights["breadth"]
            + momentum_score * self.weights["momentum"]
        )
        result.composite_score = max(-1.0, min(1.0, composite))

        # ── Risk Modifier ──────────────────────────────────────────────
        risk_mod = 1.0

        # Extreme sentiment → reduce size (contrarian protection)
        if result.extreme_fear:
            # In extreme fear, slightly reduce (market could keep falling)
            risk_mod *= 0.8
            result.reasoning.append("Risk: -20% for extreme fear")
        if result.extreme_greed:
            # In extreme greed, significantly reduce (top signals)
            risk_mod *= 0.6
            result.reasoning.append("Risk: -40% for extreme greed")

        # Macro event protection
        if macro_event_today:
            risk_mod *= 0.5
            result.reasoning.append("Risk: -50% for macro event today")
            result.macro_event_today = True
        elif macro_event_within_hours:
            risk_mod *= 0.7
            result.reasoning.append("Risk: -30% for macro event within 24h")

        # Very negative breadth → reduce
        if breadth_score < -0.5:
            risk_mod *= 0.8
            result.reasoning.append("Risk: -20% for negative market breadth")

        result.risk_modifier = max(0.1, min(1.0, risk_mod))  # floor at 10%

        # ── Entry avoidance ────────────────────────────────────────────
        result.should_avoid_entry = (
            macro_event_today
            or (result.extreme_greed and composite > 0.7)
            or result.risk_modifier < 0.3
        )

        if result.should_avoid_entry:
            result.reasoning.append("ENTRY AVOIDANCE TRIGGERED")

        logger.info("Sentiment: %s", result.summary())
        return result

    def apply_to_conviction(
        self,
        raw_conviction: float,
        sentiment: SentimentResult,
    ) -> float:
        """
        Adjust a strategy's raw conviction score based on sentiment.

        Bullish sentiment boosts bullish signals and dampens bearish signals.
        Bearish sentiment does the opposite.

        The adjustment is capped at ±20% of the raw conviction to prevent
        sentiment from overwhelming technical signals.

        Parameters
        ----------
        raw_conviction : the strategy's conviction in [-1.0, 1.0]
        sentiment      : SentimentResult from analyze()

        Returns
        -------
        float — adjusted conviction in [-1.0, 1.0]
        """
        if sentiment.should_avoid_entry:
            # Dampen all convictions by 50% when entry avoidance is active
            return raw_conviction * 0.5

        # Alignment bonus: if sentiment agrees with signal direction, boost
        # If they disagree, dampen
        alignment = raw_conviction * sentiment.composite_score  # positive = agree
        adjustment = alignment * 0.2  # max ±20% boost/penalty

        adjusted = raw_conviction + adjustment
        return max(-1.0, min(1.0, adjusted))

    def apply_to_size(
        self,
        raw_size: float,
        sentiment: SentimentResult,
    ) -> float:
        """
        Apply the sentiment risk modifier to a proposed position size.

        Parameters
        ----------
        raw_size  : proposed position size (in base units or % of equity)
        sentiment : SentimentResult from analyze()

        Returns
        -------
        float — adjusted size (always >= 0)
        """
        return max(0.0, raw_size * sentiment.risk_modifier)
