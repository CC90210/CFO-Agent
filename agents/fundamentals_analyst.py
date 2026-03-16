"""
agents/fundamentals_analyst.py
--------------------------------
Fundamentals Analysis Agent — evaluates intrinsic value from on-chain
metrics (crypto) or financial ratios (stocks) to produce a conviction signal.

Data sources (all free):
  Crypto : CoinGecko API — https://api.coingecko.com/api/v3
  Stocks : Yahoo Finance unofficial JSON endpoint
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from agents.base_agent import AgentSignal, BaseAnalystAgent, Direction

logger = logging.getLogger(__name__)

_COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_YAHOO_FINANCE_BASE = "https://query1.finance.yahoo.com/v10/finance/quoteSummary"
_HTTP_TIMEOUT = 15


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
    """

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

        try:
            signal = await self._claude_analysis(
                symbol, asset_class, fundamentals, quant_conviction, context
            )
        except Exception as exc:
            logger.warning(
                "%s: Claude unavailable (%s), using quant valuation", self.name, exc
            )
            signal = self._quant_signal(quant_conviction, fundamentals)

        return signal

    # ------------------------------------------------------------------
    # Crypto fundamentals — CoinGecko
    # ------------------------------------------------------------------

    async def _fetch_crypto_fundamentals(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        coin_id = market_data.get("coingecko_id") or self._symbol_to_coingecko_id(symbol)

        url = f"{_COINGECKO_BASE}/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false",
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
            # Market metrics
            "market_cap_usd": md.get("market_cap", {}).get("usd"),
            "fully_diluted_valuation": md.get("fully_diluted_valuation", {}).get("usd"),
            "total_volume_24h": md.get("total_volume", {}).get("usd"),
            "price_usd": md.get("current_price", {}).get("usd"),
            "price_change_24h": md.get("price_change_percentage_24h"),
            "price_change_7d": md.get("price_change_percentage_7d"),
            "price_change_30d": md.get("price_change_percentage_30d"),
            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd"),
            "circulating_supply": md.get("circulating_supply"),
            "total_supply": md.get("total_supply"),
            "max_supply": md.get("max_supply"),
            # Derived
            "volume_to_market_cap": (
                (md.get("total_volume", {}).get("usd") or 0)
                / (md.get("market_cap", {}).get("usd") or 1)
            ),
            # Social (on-chain proxy via community data)
            "reddit_subscribers": community.get("reddit_subscribers"),
            "twitter_followers": community.get("twitter_followers"),
        }

        # Supply inflation rate
        circ = fundamentals.get("circulating_supply") or 0
        total = fundamentals.get("total_supply") or circ
        if total > 0:
            fundamentals["supply_inflation_pct"] = (total - circ) / total * 100
        else:
            fundamentals["supply_inflation_pct"] = 0.0

        return fundamentals

    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """Best-effort mapping from trading symbol to CoinGecko coin id."""
        mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
            "DOGE": "dogecoin", "AVAX": "avalanche-2", "DOT": "polkadot",
            "MATIC": "matic-network", "LINK": "chainlink", "UNI": "uniswap",
        }
        base = symbol.split("/")[0].split("-")[0].upper()
        return mapping.get(base, base.lower())

    # ------------------------------------------------------------------
    # Stock fundamentals — Yahoo Finance
    # ------------------------------------------------------------------

    async def _fetch_stock_fundamentals(
        self,
        session: aiohttp.ClientSession,
        symbol: str,
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        ticker = market_data.get("ticker") or symbol.split("/")[0]
        modules = "defaultKeyStatistics,financialData,summaryDetail,insiderHolderList"
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

        return {
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
        }

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

            # Recent price momentum
            chg30 = fundamentals.get("price_change_30d")
            if chg30 is not None:
                if chg30 > 20:
                    votes.append(0.4)
                elif chg30 < -20:
                    votes.append(-0.4)

            # Distance from ATH — deep discount is bullish for value
            ath_chg = fundamentals.get("ath_change_pct")
            if ath_chg is not None:
                if ath_chg < -70:
                    votes.append(0.6)   # deep discount
                elif ath_chg > -10:
                    votes.append(-0.3)  # near ATH, overheated

            # Supply inflation (high = dilution pressure)
            supply_inf = fundamentals.get("supply_inflation_pct", 0)
            if supply_inf > 20:
                votes.append(-0.3)
            elif supply_inf < 5:
                votes.append(0.2)

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

        if not votes:
            return 0.0
        return max(-1.0, min(1.0, sum(votes) / len(votes)))

    def _quant_signal(
        self, conviction: float, fundamentals: dict[str, Any]
    ) -> AgentSignal:
        direction = self._direction_from_conviction(conviction)
        asset_class = fundamentals.get("asset_class", "asset")
        reasoning = (
            f"Quant valuation score: {conviction:+.2f} "
            f"(asset_class={asset_class}). Claude unavailable."
        )
        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=conviction,
            reasoning=reasoning,
            confidence=min(0.65, abs(conviction)),
            metadata={"mode": "quant_fallback", "fundamentals": fundamentals},
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

        # Compact the fundamentals for the prompt
        fund_str = "\n".join(
            f"  {k}: {round(v, 4) if isinstance(v, float) else v}"
            for k, v in fundamentals.items()
            if v is not None
        )

        user_message = f"""Fundamental analysis for {symbol} ({asset_class}).{macro_note}

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
            return self._quant_signal(quant_conviction, fundamentals)

        direction_str = str(parsed.get("direction", "NEUTRAL")).upper()
        try:
            direction = Direction(direction_str)
        except ValueError:
            direction = Direction.NEUTRAL

        return AgentSignal(
            agent_name=self.name,
            direction=direction,
            conviction=float(parsed.get("conviction", quant_conviction)),
            reasoning=str(parsed.get("reasoning", "")),
            confidence=float(parsed.get("confidence", 0.6)),
            metadata={
                "mode": "claude",
                "valuation": parsed.get("valuation", "fairly_valued"),
                "key_strengths": parsed.get("key_strengths", []),
                "key_risks": parsed.get("key_risks", []),
                "quant_conviction": quant_conviction,
            },
        )
