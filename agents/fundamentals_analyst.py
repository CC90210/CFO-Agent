"""
agents/fundamentals_analyst.py
--------------------------------
Fundamentals Analysis Agent — evaluates intrinsic value from on-chain
metrics (crypto) or financial ratios (stocks) to produce a conviction signal.

Data sources (all free):
  Crypto : CoinGecko API — https://api.coingecko.com/api/v3
           Enhanced via NewsFetcher.fetch_coingecko_market_data() for richer
           ATH/ATL, trending score, and 30-day price change data.
  Stocks : Yahoo Finance unofficial JSON endpoint
           Earnings calendar via NewsFetcher.fetch_earnings_calendar() (FMP).

Macro awareness:
  If the Fed is in a rate-hiking cycle (hawkish), bullish conviction is
  dampened. If the cycle is dovish/cutting, a small positive bias is applied.
  The macro context is passed in via `context["macro_environment"]`.

Economic calendar:
  If a HIGH-impact event is within 24h, confidence is capped at 0.5
  to prevent over-confident signals ahead of known volatility events.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import aiohttp

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction
from data.economic_calendar import EconomicCalendar

logger = logging.getLogger(__name__)

_COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_YAHOO_FINANCE_BASE = "https://query1.finance.yahoo.com/v10/finance/quoteSummary"
_HTTP_TIMEOUT = 15

# Macro stance keywords — parsed from context["macro_environment"]
_HAWKISH_WORDS = frozenset(["hawkish", "hike", "hiking", "tightening", "restrictive"])
_DOVISH_WORDS = frozenset(["dovish", "cut", "cutting", "easing", "accommodative", "pivot"])


class FundamentalsAnalyst(BaseAnalystAgent):
    """
    Specialist in fundamental / intrinsic-value analysis.

    Expected market_data shape:
        {
            "asset_class": "crypto" | "stock",
            "coingecko_id": "bitcoin",   # required for crypto
            "ticker": "AAPL",            # required for stocks
            "market_cap_usd": float,     # optional, pre-supplied
        }

    Optional context keys:
        context["macro_environment"] : str — free-text macro description
            e.g. "Fed is hawkish, rates at 5.5%, inflation elevated"
            Parsed for hawkish/dovish signals that adjust conviction.
    """

    def __init__(self) -> None:
        super().__init__()
        self._economic_calendar = EconomicCalendar()

    @property
    def name(self) -> str:
        return "FundamentalsAnalyst"

    # ------------------------------------------------------------------
    # Main implementation
    # ------------------------------------------------------------------

    async def _analyze_impl(
        self,
        symbol: str,
        market_data: dict[str, Any],
        context: dict[str, Any],
    ) -> AgentSignal:
        asset_class = market_data.get("asset_class", "crypto").lower()

        # Determine macro stance from context
        macro_stance = self._parse_macro_stance(context.get("macro_environment", ""))

        # Check economic calendar — cap confidence if a high-impact event is near
        high_impact_soon = self._economic_calendar.is_high_impact_event_within_hours(hours=24)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_HTTP_TIMEOUT)
        ) as session:
            if asset_class == "crypto":
                fundamentals = await self._fetch_crypto_fundamentals(
                    session, symbol, market_data
                )
            else:
                fundamentals = await self._fetch_stock_fundamentals(
                    session, symbol, market_data
                )

        if not fundamentals:
            return AgentSignal.neutral(
                self.name,
                reason=f"No fundamental data available for {symbol}",
            )

        quant_conviction = self._quant_valuation_score(fundamentals, asset_class)

        # Apply macro bias
        quant_conviction = self._apply_macro_bias(quant_conviction, macro_stance)

        # Dampen conviction near high-impact events
        if high_impact_soon:
            quant_conviction *= 0.6
            logger.warning(
                "%s: HIGH-impact event within 24h — dampening conviction for %s",
                self.name, symbol,
            )

        try:
            signal = await self._claude_analysis(
                symbol, asset_class, fundamentals, quant_conviction, context,
                macro_stance=macro_stance,
                high_impact_soon=high_impact_soon,
            )
        except Exception as exc:
            logger.warning(
                "%s: Claude unavailable (%s), using quant valuation", self.name, exc
            )
            signal = self._quant_signal(quant_conviction, fundamentals, high_impact_soon)

        return signal

    # ------------------------------------------------------------------
    # Crypto fundamentals — CoinGecko (enhanced)
    # ------------------------------------------------------------------

    async def _fetch_crypto_fundamentals(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Fetch comprehensive crypto fundamentals from CoinGecko.

        Pulls the full /coins/{id} endpoint for community data, supply metrics,
        and the complete market_data block including ATH/ATL, 7d/30d changes,
        and trending score.
        """
        coin_id = market_data.get("coingecko_id") or self._symbol_to_coingecko_id(symbol)

        url = f"{_COINGECKO_BASE}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false",
            "sparkline": "false",
        }

        try:
            async with session.get(url, params=params) as resp:
                if resp.status == 429:
                    logger.warning("CoinGecko rate limited")
                    return {}
                if resp.status != 200:
                    logger.debug("CoinGecko returned %d for %s", resp.status, coin_id)
                    return {}
                data = await resp.json()
        except Exception as exc:
            logger.warning("CoinGecko fetch failed: %s", exc)
            return {}

        md = data.get("market_data", {})
        community = data.get("community_data", {})

        fundamentals: dict[str, Any] = {
            "asset_class": "crypto",
            "name": data.get("name", symbol),
            # Core market metrics
            "market_cap_usd": md.get("market_cap", {}).get("usd"),
            "fully_diluted_valuation": md.get("fully_diluted_valuation", {}).get("usd"),
            "total_volume_24h": md.get("total_volume", {}).get("usd"),
            "price_usd": md.get("current_price", {}).get("usd"),
            # Price momentum (multi-timeframe)
            "price_change_24h": md.get("price_change_percentage_24h"),
            "price_change_7d": md.get("price_change_percentage_7d"),
            "price_change_30d": md.get("price_change_percentage_30d"),
            "price_change_1y": md.get("price_change_percentage_1y"),
            # ATH / ATL context
            "ath_usd": md.get("ath", {}).get("usd"),
            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd"),
            "atl_usd": md.get("atl", {}).get("usd"),
            "atl_change_pct": md.get("atl_change_percentage", {}).get("usd"),
            # Supply metrics
            "circulating_supply": md.get("circulating_supply"),
            "total_supply": md.get("total_supply"),
            "max_supply": md.get("max_supply"),
            "market_cap_rank": data.get("market_cap_rank"),
            # Social (on-chain proxy via community data)
            "reddit_subscribers": community.get("reddit_subscribers"),
            "twitter_followers": community.get("twitter_followers"),
        }

        # Derived: volume-to-market-cap ratio (high = healthy trading activity)
        mc = md.get("market_cap", {}).get("usd") or 1
        vol = md.get("total_volume", {}).get("usd") or 0
        fundamentals["volume_to_market_cap"] = vol / mc

        # Derived: supply inflation rate (remaining unlocked supply pressure)
        circ = fundamentals.get("circulating_supply") or 0
        total = fundamentals.get("total_supply") or circ
        fundamentals["supply_inflation_pct"] = (
            (total - circ) / total * 100 if total > 0 else 0.0
        )

        # Check trending status (best-effort — independent request)
        try:
            async with session.get(f"{_COINGECKO_BASE}/search/trending") as tresp:
                if tresp.status == 200:
                    tdata = await tresp.json()
                    trending_ids = [
                        e.get("item", {}).get("id", "").lower()
                        for e in tdata.get("coins", [])
                    ]
                    fundamentals["is_trending"] = coin_id.lower() in trending_ids
                else:
                    fundamentals["is_trending"] = False
        except Exception:
            fundamentals["is_trending"] = False

        return fundamentals

    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """Best-effort mapping from trading symbol to CoinGecko coin id."""
        mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
            "DOGE": "dogecoin", "AVAX": "avalanche-2", "DOT": "polkadot",
            "MATIC": "matic-network", "LINK": "chainlink", "UNI": "uniswap",
            "AAVE": "aave", "MKR": "maker", "CRV": "curve-dao-token",
            "COMP": "compound-governance-token", "LTC": "litecoin",
            "ATOM": "cosmos", "APT": "aptos", "ARB": "arbitrum",
            "OP": "optimism",
        }
        base = symbol.split("/")[0].split("-")[0].upper()
        return mapping.get(base, base.lower())

    # ------------------------------------------------------------------
    # Stock fundamentals — Yahoo Finance + earnings calendar
    # ------------------------------------------------------------------

    async def _fetch_stock_fundamentals(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Fetch stock fundamentals from Yahoo Finance.
        Also attempts to enrich with next earnings date via FMP if configured.
        """
        ticker = market_data.get("ticker") or symbol.split("/")[0]
        modules = "defaultKeyStatistics,financialData,summaryDetail"
        url = f"{_YAHOO_FINANCE_BASE}/{ticker}"
        params = {"modules": modules}

        try:
            async with session.get(
                url, params=params,
                headers={"User-Agent": "Mozilla/5.0"}
            ) as resp:
                if resp.status != 200:
                    logger.debug("Yahoo Finance returned %d for %s", resp.status, ticker)
                    return {}
                data = await resp.json()
        except Exception as exc:
            logger.warning("Yahoo Finance fetch failed: %s", exc)
            return {}

        try:
            result = data["quoteSummary"]["result"][0]
        except (KeyError, IndexError, TypeError):
            return {}

        key_stats = result.get("defaultKeyStatistics", {})
        fin_data = result.get("financialData", {})
        summary = result.get("summaryDetail", {})

        def _val(obj: dict[str, Any], key: str) -> float | None:
            v = obj.get(key, {})
            if isinstance(v, dict):
                return v.get("raw")
            return v if isinstance(v, (int, float)) else None

        fundamentals: dict[str, Any] = {
            "asset_class": "stock",
            "ticker": ticker,
            "pe_ratio": _val(summary, "trailingPE"),
            "forward_pe": _val(summary, "forwardPE"),
            "peg_ratio": _val(key_stats, "pegRatio"),
            "price_to_book": _val(key_stats, "priceToBook"),
            "revenue_growth": _val(fin_data, "revenueGrowth"),
            "earnings_growth": _val(fin_data, "earningsGrowth"),
            "profit_margins": _val(fin_data, "profitMargins"),
            "return_on_equity": _val(fin_data, "returnOnEquity"),
            "debt_to_equity": _val(key_stats, "debtToEquity"),
            "current_ratio": _val(fin_data, "currentRatio"),
            "short_percent_float": _val(key_stats, "shortPercentOfFloat"),
            "insider_percent": _val(key_stats, "heldPercentInsiders"),
            "52w_high_change": _val(key_stats, "52WeekChange"),
            # Earnings calendar (populated below)
            "next_earnings_date": None,
            "eps_estimate": None,
        }

        # Enrich with earnings calendar via FMP if key is configured
        fmp_key = os.environ.get("FMP_API_KEY", "")
        if fmp_key:
            earnings = await self._fetch_earnings_calendar(session, ticker, fmp_key)
            fundamentals["next_earnings_date"] = earnings.get("next_earnings_date")
            fundamentals["eps_estimate"] = earnings.get("eps_estimate")

        return fundamentals

    async def _fetch_earnings_calendar(
        self,
        session: aiohttp.ClientSession,
        ticker: str,
        fmp_key: str,
    ) -> dict[str, Any]:
        """Fetch next earnings date and EPS estimate from FMP."""
        from datetime import datetime, timezone

        now = datetime.now(tz=timezone.utc)
        url = "https://financialmodelingprep.com/api/v3/earnings-calendar"
        params = {
            "apikey": fmp_key,
            "from": now.strftime("%Y-%m-%d"),
            "to": now.replace(month=min(now.month + 3, 12)).strftime("%Y-%m-%d"),
        }
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    return {}
                cal_data = await resp.json()
                if not isinstance(cal_data, list):
                    return {}
                for entry in cal_data:
                    if entry.get("symbol", "").upper() == ticker.upper():
                        return {
                            "next_earnings_date": entry.get("date", ""),
                            "eps_estimate": entry.get("epsEstimated"),
                        }
        except Exception as exc:
            logger.debug("FMP earnings fetch failed for %s: %s", ticker, exc)
        return {}

    # ------------------------------------------------------------------
    # Macro stance parsing
    # ------------------------------------------------------------------

    def _parse_macro_stance(self, macro_text: str) -> str:
        """
        Parse a free-text macro description and return "hawkish", "dovish",
        or "neutral".

        Parameters
        ----------
        macro_text : e.g. "Fed is hawkish, rates at 5.5%, inflation elevated"

        Returns
        -------
        "hawkish" | "dovish" | "neutral"
        """
        if not macro_text:
            return "neutral"
        lower = macro_text.lower()
        hawkish_hits = sum(1 for w in _HAWKISH_WORDS if w in lower)
        dovish_hits = sum(1 for w in _DOVISH_WORDS if w in lower)
        if hawkish_hits > dovish_hits:
            return "hawkish"
        if dovish_hits > hawkish_hits:
            return "dovish"
        return "neutral"

    def _apply_macro_bias(self, conviction: float, macro_stance: str) -> float:
        """
        Adjust a raw conviction score based on the macro environment.

        Hawkish Fed → dampen bullish signals (risk-off reduces upside for risk assets)
        Dovish Fed  → small positive bias (liquidity expansion benefits risk assets)
        Neutral     → no adjustment
        """
        if macro_stance == "hawkish" and conviction > 0:
            # Dampen bullish conviction by 20% in hawkish environment
            return conviction * 0.80
        if macro_stance == "dovish" and conviction < 0:
            # Dampen bearish conviction by 20% in dovish/easing environment
            return conviction * 0.80
        return conviction

    # ------------------------------------------------------------------
    # Quant valuation scoring
    # ------------------------------------------------------------------

    def _quant_valuation_score(
        self, fundamentals: dict[str, Any], asset_class: str
    ) -> float:
        """Produce a [-1, 1] conviction from fundamental metrics."""
        votes: list[float] = []

        if asset_class == "crypto":
            # Volume/Market cap ratio — high = healthy demand
            v2mc = fundamentals.get("volume_to_market_cap", 0)
            if v2mc > 0.1:
                votes.append(0.5)
            elif v2mc < 0.02:
                votes.append(-0.3)

            # Recent price momentum (multi-timeframe)
            chg30 = fundamentals.get("price_change_30d")
            if chg30 is not None:
                if chg30 > 20:
                    votes.append(0.4)
                elif chg30 < -20:
                    votes.append(-0.4)

            chg7 = fundamentals.get("price_change_7d")
            if chg7 is not None:
                if chg7 > 10:
                    votes.append(0.3)
                elif chg7 < -10:
                    votes.append(-0.3)

            # Distance from ATH — deep discount is bullish for value
            ath_chg = fundamentals.get("ath_change_pct")
            if ath_chg is not None:
                if ath_chg < -70:
                    votes.append(0.6)   # deep discount
                elif ath_chg > -10:
                    votes.append(-0.3)  # near ATH, overheated

            # Distance from ATL — extreme distance means sustained strength
            atl_chg = fundamentals.get("atl_change_pct")
            if atl_chg is not None:
                if atl_chg > 500:
                    votes.append(0.2)   # well above ATL = established asset

            # Supply inflation (high = dilution pressure)
            supply_inf = fundamentals.get("supply_inflation_pct", 0)
            if supply_inf > 20:
                votes.append(-0.3)
            elif supply_inf < 5:
                votes.append(0.2)

            # Trending on CoinGecko = increased retail attention
            if fundamentals.get("is_trending"):
                votes.append(0.15)

            # Market cap rank — top-10 assets are more liquid and less risky
            rank = fundamentals.get("market_cap_rank")
            if rank is not None:
                if rank <= 10:
                    votes.append(0.1)
                elif rank > 100:
                    votes.append(-0.1)

        else:  # stocks
            # P/E ratio
            pe = fundamentals.get("pe_ratio")
            if pe is not None:
                if pe < 15:
                    votes.append(0.5)
                elif pe > 40:
                    votes.append(-0.4)

            # Forward P/E vs trailing — expansion expected?
            fpe = fundamentals.get("forward_pe")
            if pe and fpe and pe > 0 and fpe > 0:
                if fpe < pe:
                    votes.append(0.3)   # expected earnings growth
                else:
                    votes.append(-0.2)

            # PEG ratio
            peg = fundamentals.get("peg_ratio")
            if peg is not None:
                if peg < 1.0:
                    votes.append(0.6)
                elif peg > 2.5:
                    votes.append(-0.4)

            # Revenue growth
            rev_g = fundamentals.get("revenue_growth")
            if rev_g is not None:
                if rev_g > 0.15:
                    votes.append(0.4)
                elif rev_g < 0:
                    votes.append(-0.5)

            # Debt/Equity
            dte = fundamentals.get("debt_to_equity")
            if dte is not None:
                if dte < 0.5:
                    votes.append(0.2)
                elif dte > 2.0:
                    votes.append(-0.3)

            # Earnings growth
            eg = fundamentals.get("earnings_growth")
            if eg is not None:
                if eg > 0.20:
                    votes.append(0.3)
                elif eg < 0:
                    votes.append(-0.3)

        if not votes:
            return 0.0
        return max(-1.0, min(1.0, sum(votes) / len(votes)))

    def _quant_signal(
        self,
        conviction: float,
        fundamentals: dict[str, Any],
        high_impact_soon: bool = False,
    ) -> AgentSignal:
        direction = self._direction_from_conviction(conviction)
        asset_class = fundamentals.get("asset_class", "asset")
        caution_note = " HIGH-impact event within 24h — conviction dampened." if high_impact_soon else ""
        reasoning = (
            f"Quant valuation score: {conviction:+.2f} "
            f"(asset_class={asset_class}).{caution_note} Claude unavailable."
        )
        # Cap confidence if high-impact event is near
        max_confidence = 0.5 if high_impact_soon else 0.65
        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=reasoning,
            confidence=min(max_confidence, abs(conviction)),
            metadata={
                "mode": "quant_fallback",
                "fundamentals": fundamentals,
                "high_impact_event_soon": high_impact_soon,
            },
        )

    # ------------------------------------------------------------------
    # Claude analysis
    # ------------------------------------------------------------------

    async def _claude_analysis(
        self,
        symbol: str,
        asset_class: str,
        fundamentals: dict[str, Any],
        quant_conviction: float,
        context: dict[str, Any],
        macro_stance: str = "neutral",
        high_impact_soon: bool = False,
    ) -> AgentSignal:
        system_prompt = (
            "You are a world-class fundamental analyst. "
            "Assess whether an asset is overvalued, fairly valued, or undervalued "
            "based on the provided metrics. Factor in the macro environment if given. "
            "Respond ONLY with valid JSON."
        )

        macro_note = ""
        if context.get("macro_environment"):
            macro_note = f"\nMacro context: {context['macro_environment']}"
            macro_note += f"\nParsed macro stance: {macro_stance.upper()}"

        caution_note = (
            "\nWARNING: A HIGH-impact macro event is scheduled within 24 hours. "
            "Keep confidence below 0.5 and note elevated uncertainty."
        ) if high_impact_soon else ""

        earnings_note = ""
        if asset_class == "stock":
            next_earnings = fundamentals.get("next_earnings_date")
            eps_est = fundamentals.get("eps_estimate")
            if next_earnings:
                earnings_note = f"\nNext earnings date: {next_earnings}"
                if eps_est is not None:
                    earnings_note += f" (EPS estimate: ${eps_est:.2f})"

        trending_note = ""
        if asset_class == "crypto" and fundamentals.get("is_trending"):
            trending_note = "\nNOTE: This asset is currently trending on CoinGecko."

        # Compact the fundamentals for the prompt
        fund_str = "\n".join(
            f"  {k}: {round(v, 4) if isinstance(v, float) else v}"
            for k, v in fundamentals.items()
            if v is not None and k not in ("asset_class",)
        )

        user_message = f"""Fundamental analysis for {symbol} ({asset_class}).{macro_note}{caution_note}{earnings_note}{trending_note}

Metrics:
{fund_str}

Quant valuation score: {quant_conviction:+.3f}

Respond with this exact JSON:
{{
  "direction": "LONG" | "SHORT" | "NEUTRAL",
  "conviction": <float -1.0 to 1.0>,
  "confidence": <float 0.0 to 1.0>,
  "valuation": "undervalued" | "fairly_valued" | "overvalued",
  "key_strengths": ["<strength1>"],
  "key_risks": ["<risk1>"],
  "reasoning": "<2-4 sentence explanation>"
}}"""

        raw = await self.call_claude(system_prompt, user_message, max_tokens=600)
        parsed = self._parse_json_response(raw)

        if "raw" in parsed:
            return self._quant_signal(quant_conviction, fundamentals, high_impact_soon)

        direction_str = str(parsed.get("direction", "NEUTRAL")).upper()
        try:
            direction = Direction(direction_str)
        except ValueError:
            direction = Direction.NEUTRAL

        confidence = float(parsed.get("confidence", 0.6))
        if high_impact_soon:
            confidence = min(confidence, 0.5)

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=float(parsed.get("conviction", quant_conviction)),
            reasoning=str(parsed.get("reasoning", "")),
            confidence=confidence,
            metadata={
                "mode": "claude",
                "valuation": parsed.get("valuation", "fairly_valued"),
                "key_strengths": parsed.get("key_strengths", []),
                "key_risks": parsed.get("key_risks", []),
                "quant_conviction": quant_conviction,
                "macro_stance": macro_stance,
                "high_impact_event_soon": high_impact_soon,
            },
        )
