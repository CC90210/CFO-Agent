"""
research/stock_picker.py
------------------------
StockPickerAgent — Atlas's on-demand equity research and stock picking engine.

Uses Claude (claude-opus-4-6) as the reasoning core. All data pipeline work
(news ingestion, macro context, fundamentals, technicals) is done in Python
before the Claude call, so Claude receives rich structured data rather than
being asked to hallucinate numbers.

Usage:
    from research.stock_picker import StockPickerAgent
    agent = StockPickerAgent()
    picks = agent.pick("AI infrastructure plays for next 6 months", n=3)

CLI:
    python -m research.stock_picker "AI infrastructure plays for 6 months"
    python -m research.stock_picker --deep-dive NVDA
"""

from __future__ import annotations

import json
import logging
import os
import sys
import textwrap
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic

from config.settings import settings
from research.news_ingest import fetch_google_news, fetch_newsapi, NewsItem
from research.macro_watch import macro_context_summary, rotation_signal, sector_map
from research.fundamentals import get_fundamentals, get_price_history, technicals

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_MODEL = "claude-opus-4-6"
_MAX_TOKENS = 8000
_PICKS_DIR = Path(__file__).resolve().parent.parent / "data" / "picks"
_PICKS_DIR.mkdir(parents=True, exist_ok=True)
_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Pre-built sector ticker lists for when no specific tickers are provided
_SECTOR_DEFAULTS: dict[str, list[str]] = {
    "ai": ["NVDA", "AMD", "MSFT", "GOOGL", "META", "AVGO", "ARM"],
    "ai_infrastructure": ["NVDA", "AMD", "AVGO", "SMCI", "ARM", "CEG", "VST"],
    "semiconductors": ["NVDA", "AMD", "INTC", "TSM", "AMAT", "LRCX", "ASML", "QCOM"],
    "defense": ["LMT", "RTX", "NOC", "GD", "HII", "LDOS", "CACI"],
    "cybersecurity": ["CRWD", "PANW", "ZS", "FTNT", "S", "OKTA", "CYBR"],
    "energy": ["XOM", "CVX", "COP", "OXY", "SLB", "EOG"],
    "nuclear": ["CCJ", "UEC", "NXE", "CEG", "VST"],
    "biotech": ["LLY", "VRTX", "REGN", "MRNA", "ABBV", "GILD", "BIIB"],
    "fintech": ["V", "MA", "PYPL", "SQ", "AFRM", "SOFI"],
    "cloud": ["MSFT", "GOOGL", "AMZN", "CRM", "SNOW", "DDOG", "MDB"],
    "precious_metals": ["NEM", "AEM", "GOLD", "WPM", "FNV", "GLD"],
    "chinese_tech": ["BABA", "JD", "PDD", "BIDU"],
    "ev": ["TSLA", "RIVN", "NIO", "XPEV", "LI"],
    "reits": ["EQIX", "DLR", "AMT", "O", "PLD"],
    "default": ["NVDA", "MSFT", "GOOGL", "AMZN", "META", "AAPL", "BRK-B"],
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Pick:
    """A single equity pick with full research backing."""

    ticker: str
    company_name: str
    sector: str
    thesis: str
    catalysts: list[str]
    entry_price: float
    entry_window: str
    entry_rationale: str
    exit_target: float
    exit_window: str
    exit_rationale: str
    stop_loss: float
    stop_loss_rationale: str
    conviction: int                         # 0-10
    time_horizon: str
    risk_reward_ratio: float
    upside_pct: float
    downside_pct: float
    risks: list[str]
    macro_alignment: str
    technical_setup: str
    tax_note: str
    account_recommendation: str             # "TFSA" | "RRSP" | "Non-Reg"
    sources_used: list[str]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    query: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        """Render pick as a markdown tracking entry."""
        stars = "★" * self.conviction + "☆" * (10 - self.conviction)
        return textwrap.dedent(f"""
# {self.ticker} — {self.company_name}
**Generated:** {self.generated_at[:10]}  |  **Query:** {self.query}  |  **Conviction:** {stars} ({self.conviction}/10)

## Thesis
{self.thesis}

## Key Catalysts
{chr(10).join(f"- {c}" for c in self.catalysts)}

## Trade Parameters
| Field | Value |
|-------|-------|
| Entry Price | ${self.entry_price:.2f} |
| Entry Window | {self.entry_window} |
| Exit Target | ${self.exit_target:.2f} (+{self.upside_pct:.1f}%) |
| Exit Window | {self.exit_window} |
| Stop Loss | ${self.stop_loss:.2f} (-{self.downside_pct:.1f}%) |
| Risk/Reward | {self.risk_reward_ratio:.1f}x |
| Time Horizon | {self.time_horizon} |
| Account | {self.account_recommendation} |

## Entry Rationale
{self.entry_rationale}

## Technical Setup
{self.technical_setup}

## Macro Alignment
{self.macro_alignment}

## Key Risks
{chr(10).join(f"- {r}" for r in self.risks)}

## Tax Note
{self.tax_note}

---
*Sources: {", ".join(self.sources_used)}*
        """).strip()


@dataclass
class DeepDive:
    """Extended analysis for a single ticker."""

    ticker: str
    company_name: str
    executive_summary: str
    bull_case: str
    bear_case: str
    base_case: str
    bull_price_target: float
    bear_price_target: float
    base_price_target: float
    current_price: float
    catalyst_calendar: list[dict]           # [{"date": "YYYY-MM", "event": "...", "impact": "high/med/low"}]
    competitor_comparison: str
    dcf_sanity_check: str                   # 5-yr DCF summary
    final_verdict: str
    conviction: int
    risks: list[str]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_markdown(self) -> str:
        return textwrap.dedent(f"""
# Deep Dive: {self.ticker} — {self.company_name}
**Generated:** {self.generated_at[:10]}  |  **Conviction:** {self.conviction}/10

## Executive Summary
{self.executive_summary}

## Price Targets
| Scenario | Price | Implied Return |
|----------|-------|----------------|
| Bull | ${self.bull_price_target:.2f} | +{((self.bull_price_target - self.current_price) / self.current_price * 100):.1f}% |
| Base | ${self.base_price_target:.2f} | +{((self.base_price_target - self.current_price) / self.current_price * 100):.1f}% |
| Bear | ${self.bear_price_target:.2f} | {((self.bear_price_target - self.current_price) / self.current_price * 100):.1f}% |

## Bull Case
{self.bull_case}

## Base Case
{self.base_case}

## Bear Case
{self.bear_case}

## Catalyst Calendar (Next 90 Days)
{chr(10).join(f"- **{c.get('date', '?')}** ({c.get('impact', 'med').upper()}): {c.get('event', '')}" for c in self.catalyst_calendar)}

## Competitor Comparison
{self.competitor_comparison}

## DCF Sanity Check
{self.dcf_sanity_check}

## Key Risks
{chr(10).join(f"- {r}" for r in self.risks)}

## Final Verdict
{self.final_verdict}
        """).strip()


# ─────────────────────────────────────────────────────────────────────────────
#  Helper: load prompt template
# ─────────────────────────────────────────────────────────────────────────────

def _load_prompt_template() -> str:
    template_path = _PROMPTS_DIR / "stock_pick.md"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    # Fallback minimal prompt if file is missing
    return (
        "You are Atlas, an expert portfolio manager and equity analyst. "
        "Return a JSON array of stock picks with fields: ticker, company_name, sector, thesis, "
        "catalysts, entry_price, entry_window, entry_rationale, exit_target, exit_window, "
        "exit_rationale, stop_loss, stop_loss_rationale, conviction (0-10), time_horizon, "
        "risk_reward_ratio, upside_pct, downside_pct, risks, macro_alignment, technical_setup, "
        "tax_note, account_recommendation, sources_used. Only include picks with conviction >= 6."
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Main agent class
# ─────────────────────────────────────────────────────────────────────────────

class StockPickerAgent:
    """
    Claude-powered equity research agent.

    All quantitative data assembly happens in Python.
    Claude's job is interpretation, thesis formation, and structured output.
    """

    def __init__(self) -> None:
        api_key = settings.ai.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY not set. Add it to your .env file."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self._prompt_template = _load_prompt_template()

    # ── Public API ────────────────────────────────────────────────────────────

    def pick(
        self,
        query: str,
        n: int = 3,
        horizon: str = "6-12 months",
        candidate_tickers: Optional[list[str]] = None,
    ) -> list[Pick]:
        """
        Run the full research pipeline and return n stock picks.

        Args:
            query: Natural language request (e.g. "AI infrastructure plays")
            n: Number of picks to return (max 5 recommended for quality)
            horizon: Time horizon hint fed to Claude
            candidate_tickers: Optional pre-screened list; if None, inferred from query

        Returns:
            List of Pick dataclasses, sorted by conviction descending.
        """
        logger.info("Running stock picker: query='%s', n=%d, horizon=%s", query, n, horizon)

        tickers = candidate_tickers or self._infer_tickers(query)
        news = self._gather_news(query, tickers)
        macro_ctx = macro_context_summary(news)
        ticker_data = self._gather_ticker_data(tickers)

        prompt = self._build_pick_prompt(
            query=query,
            n=n,
            horizon=horizon,
            tickers=tickers,
            ticker_data=ticker_data,
            macro_ctx=macro_ctx,
            news=news,
        )

        raw = self._call_claude(prompt)
        picks = self._parse_picks(raw, query=query)

        # Sort by conviction and cap at n
        picks.sort(key=lambda p: p.conviction, reverse=True)
        return picks[:n]

    def deep_dive(self, ticker: str) -> DeepDive:
        """
        Run an extended deep-dive analysis on a single ticker.

        Returns bull/base/bear cases, catalyst calendar, competitor comparison,
        DCF sanity check, and final verdict.
        """
        logger.info("Running deep dive on %s", ticker)

        news = self._gather_news(ticker, [ticker])
        macro_ctx = macro_context_summary(news)
        fund = get_fundamentals(ticker)
        df = get_price_history(ticker, period="2y")
        tech = technicals(df)
        filings_news = self._filings_summary(ticker)

        prompt = self._build_deep_dive_prompt(
            ticker=ticker,
            fund=fund,
            tech=tech,
            macro_ctx=macro_ctx,
            news=news,
            filings_news=filings_news,
        )

        raw = self._call_claude(prompt)
        return self._parse_deep_dive(raw, ticker=ticker, current_price=tech.get("latest_price", 0.0))

    def save_pick(self, pick: Pick, path: Optional[str] = None) -> Path:
        """
        Persist a pick as a markdown file in data/picks/.

        Returns the path to the saved file.
        """
        save_dir = Path(path) if path else _PICKS_DIR
        save_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"{date_str}_{pick.ticker}_{pick.conviction}conv.md"
        filepath = save_dir / filename
        filepath.write_text(pick.to_markdown(), encoding="utf-8")
        logger.info("Pick saved to %s", filepath)
        return filepath

    # ── Private helpers ───────────────────────────────────────────────────────

    def _infer_tickers(self, query: str) -> list[str]:
        """Map a natural language query to a candidate ticker list."""
        q = query.lower()
        for keyword, tickers in _SECTOR_DEFAULTS.items():
            if keyword in q:
                return tickers
        # Fallback: extract capitalized ticker-like tokens from the query
        import re
        extracted = re.findall(r'\b[A-Z]{2,5}\b', query)
        if extracted:
            return extracted[:8]
        return _SECTOR_DEFAULTS["default"]

    def _gather_news(self, query: str, tickers: list[str]) -> list[NewsItem]:
        """Pull recent news for the query and top tickers."""
        news: list[NewsItem] = []
        seen_urls: set[str] = set()

        def _add(items: list[NewsItem]) -> None:
            for item in items:
                if item.url not in seen_urls:
                    news.append(item)
                    seen_urls.add(item.url)

        _add(fetch_google_news(query, days=14))

        # Fetch news for up to 3 tickers to avoid rate limits
        for ticker in tickers[:3]:
            _add(fetch_google_news(ticker, days=14))

        newsapi_items = fetch_newsapi(query, days=14)
        _add(newsapi_items)

        news.sort(key=lambda x: x.date, reverse=True)
        return news[:50]  # Cap at 50 to keep prompt size manageable

    def _gather_ticker_data(self, tickers: list[str]) -> dict[str, dict]:
        """Fetch fundamentals + technicals for each ticker. Returns {ticker: {fund, tech}}."""
        results: dict[str, dict] = {}
        for ticker in tickers:
            try:
                fund = get_fundamentals(ticker)
                df = get_price_history(ticker, period="1y")
                tech = technicals(df)
                results[ticker] = {
                    "fundamentals": fund.to_dict(),
                    "technicals": tech,
                    "valuation": fund.valuation_summary(),
                }
            except Exception as exc:
                logger.warning("Data fetch failed for %s: %s", ticker, exc)
                results[ticker] = {"error": str(exc)}
        return results

    def _filings_summary(self, ticker: str) -> str:
        """Return a short summary of recent SEC filings as text."""
        try:
            from research.news_ingest import fetch_sec_filings
            filings_8k = fetch_sec_filings(ticker, "8-K")
            if not filings_8k:
                return "No recent 8-K filings found."
            lines = [f"- {f.filed_date.strftime('%Y-%m-%d')}: {f.form_type} — {f.description}" for f in filings_8k[:5]]
            return "\n".join(lines)
        except Exception as exc:
            return f"Filing fetch failed: {exc}"

    def _build_pick_prompt(
        self,
        query: str,
        n: int,
        horizon: str,
        tickers: list[str],
        ticker_data: dict[str, dict],
        macro_ctx: str,
        news: list[NewsItem],
    ) -> str:
        """Assemble the full prompt for a pick request."""
        news_digest = "\n".join(
            f"- [{item.date.strftime('%Y-%m-%d')}] {item.source}: {item.title}"
            for item in news[:30]
        )

        ticker_digest_parts: list[str] = []
        for ticker, data in ticker_data.items():
            if "error" in data:
                ticker_digest_parts.append(f"### {ticker}\nData unavailable: {data['error']}")
                continue
            fund = data.get("fundamentals", {})
            tech = data.get("technicals", {})
            val = data.get("valuation", "")
            ticker_digest_parts.append(
                f"### {ticker} — {fund.get('name', ticker)}\n"
                f"**Sector:** {fund.get('sector', 'Unknown')} | **Industry:** {fund.get('industry', 'Unknown')}\n"
                f"**Valuation:** {val}\n"
                f"**Market Cap:** ${fund.get('market_cap', 0):,.0f}\n"
                f"**Analyst Rating:** {fund.get('analyst_rating', 'N/A')} | **Target:** ${fund.get('analyst_target_price', 0):.2f}\n"
                f"**Operating Margin:** {fund.get('operating_margin', 'N/A')}% | "
                f"**Revenue Growth:** {fund.get('revenue_growth_yoy', 'N/A')}%\n"
                f"**Short Interest:** {fund.get('short_interest_pct', 'N/A')}% | "
                f"**Institutional Holdings:** {fund.get('institutional_ownership_pct', 'N/A')}%\n"
                f"**Technicals:** Price ${tech.get('latest_price', 0):.2f} | "
                f"RSI {tech.get('rsi_14', 'N/A')} | "
                f"Trend: {tech.get('trend', 'unknown')} | "
                f"vs 52w High: {tech.get('price_vs_52wk_high_pct', 'N/A')}% | "
                f"Volume: {tech.get('volume_trend', 'N/A')}\n"
                f"{'GOLDEN CROSS active' if tech.get('golden_cross') else 'DEATH CROSS active' if tech.get('death_cross') else 'No SMA cross signal'}"
            )
        ticker_digest = "\n\n".join(ticker_digest_parts)

        return f"""{self._prompt_template}

---

## Research Request

**Query:** {query}
**Picks requested:** {n}
**Time horizon:** {horizon}
**Today's date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d")}

---

{macro_ctx}

---

## Recent News Headlines (last 14 days)
{news_digest}

---

## Candidate Tickers: {', '.join(tickers)}

{ticker_digest}

---

## Instructions
Based on all data above, select the {n} BEST picks that match the query '{query}'.
Apply the Anti-Bullshit Rules and conviction threshold (≥6) strictly.
Return ONLY the JSON array. No prose before or after. No markdown fences.
"""

    def _build_deep_dive_prompt(
        self,
        ticker: str,
        fund: object,
        tech: dict,
        macro_ctx: str,
        news: list[NewsItem],
        filings_news: str,
    ) -> str:
        """Assemble the prompt for a deep dive."""
        from research.fundamentals import Fundamentals
        assert isinstance(fund, Fundamentals)

        news_digest = "\n".join(
            f"- [{item.date.strftime('%Y-%m-%d')}] {item.source}: {item.title}"
            for item in news[:30]
        )

        return f"""{self._prompt_template}

---

## Deep Dive Request: {ticker}

**Today's date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d")}

### Fundamentals
{fund.valuation_summary()}
- Sector: {fund.sector} | Industry: {fund.industry}
- Market Cap: ${(fund.market_cap or 0):,.0f}
- Operating Margin: {fund.operating_margin}% | Net Margin: {fund.net_margin}%
- Revenue Growth YoY: {fund.revenue_growth_yoy}% | Earnings Growth: {fund.earnings_growth_yoy}%
- Debt/Equity: {fund.debt_to_equity} | FCF Yield: {fund.fcf_yield}%
- Short Interest: {fund.short_interest_pct}% | Institutional: {fund.institutional_ownership_pct}%
- Analyst Rating: {fund.analyst_rating} | Target: ${fund.analyst_target_price}

### Technicals
- Price: ${tech.get('latest_price', 0):.2f}
- SMA 50: ${tech.get('sma_50', 'N/A')} | SMA 200: ${tech.get('sma_200', 'N/A')}
- RSI(14): {tech.get('rsi_14', 'N/A')} | MACD: {tech.get('macd', 'N/A')}
- 52-week high: ${tech.get('week_52_high', 'N/A')} | Low: ${tech.get('week_52_low', 'N/A')}
- vs 52w high: {tech.get('price_vs_52wk_high_pct', 'N/A')}%
- Trend: {tech.get('trend', 'unknown')} | Volume: {tech.get('volume_trend', 'N/A')}
- {'GOLDEN CROSS' if tech.get('golden_cross') else 'DEATH CROSS' if tech.get('death_cross') else 'No cross signal'}

{macro_ctx}

### Recent News
{news_digest}

### Recent SEC Filings
{filings_news}

---

## Output Format (STRICT JSON — single object, no array wrapper)
Return a JSON object with these fields:
{{
  "ticker": "{ticker}",
  "company_name": "...",
  "executive_summary": "2-3 sentence overview",
  "bull_case": "150+ word bull case with specific price drivers",
  "bear_case": "150+ word bear case with specific downside catalysts",
  "base_case": "150+ word base case with probability-weighted outcome",
  "bull_price_target": 0.0,
  "bear_price_target": 0.0,
  "base_price_target": 0.0,
  "catalyst_calendar": [{{"date": "YYYY-MM", "event": "...", "impact": "high|med|low"}}],
  "competitor_comparison": "Paragraph comparing to 2-3 nearest competitors on key metrics",
  "dcf_sanity_check": "Back-of-envelope DCF: revenue growth assumptions, margin targets, terminal multiple, fair value range",
  "final_verdict": "Clear Buy/Hold/Avoid recommendation with 2-3 sentence rationale",
  "conviction": 0,
  "risks": ["..."]
}}
Return ONLY the JSON object. No prose before or after. No markdown fences.
"""

    def _call_claude(self, prompt: str) -> str:
        """Call Claude and return the raw text response."""
        try:
            message = self._client.messages.create(
                model=_MODEL,
                max_tokens=_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as exc:
            logger.error("Claude API error: %s", exc)
            raise

    def _parse_picks(self, raw: str, query: str = "") -> list[Pick]:
        """Parse Claude's JSON output into Pick objects."""
        text = raw.strip()

        # Strip markdown fences if present despite instructions
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to extract the first JSON array from the response
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    logger.error("Failed to parse Claude picks response as JSON")
                    return []
            else:
                logger.error("No JSON array found in Claude response")
                return []

        if not isinstance(data, list):
            data = [data]

        picks: list[Pick] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                pick = Pick(
                    ticker=item.get("ticker", "UNKNOWN"),
                    company_name=item.get("company_name", ""),
                    sector=item.get("sector", ""),
                    thesis=item.get("thesis", ""),
                    catalysts=item.get("catalysts", []),
                    entry_price=float(item.get("entry_price", 0)),
                    entry_window=item.get("entry_window", ""),
                    entry_rationale=item.get("entry_rationale", ""),
                    exit_target=float(item.get("exit_target", 0)),
                    exit_window=item.get("exit_window", ""),
                    exit_rationale=item.get("exit_rationale", ""),
                    stop_loss=float(item.get("stop_loss", 0)),
                    stop_loss_rationale=item.get("stop_loss_rationale", ""),
                    conviction=int(item.get("conviction", 0)),
                    time_horizon=item.get("time_horizon", ""),
                    risk_reward_ratio=float(item.get("risk_reward_ratio", 0)),
                    upside_pct=float(item.get("upside_pct", 0)),
                    downside_pct=float(item.get("downside_pct", 0)),
                    risks=item.get("risks", []),
                    macro_alignment=item.get("macro_alignment", ""),
                    technical_setup=item.get("technical_setup", ""),
                    tax_note=item.get("tax_note", ""),
                    account_recommendation=item.get("account_recommendation", "TFSA"),
                    sources_used=item.get("sources_used", ["yfinance"]),
                    query=query,
                )
                if pick.conviction >= 6:
                    picks.append(pick)
                else:
                    logger.info("Pick %s rejected: conviction %d < 6", pick.ticker, pick.conviction)
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Failed to parse pick item: %s — %s", exc, item)

        return picks

    def _parse_deep_dive(self, raw: str, ticker: str, current_price: float) -> DeepDive:
        """Parse Claude's JSON output into a DeepDive object."""
        text = raw.strip()

        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    data = {}
            else:
                data = {}

        return DeepDive(
            ticker=data.get("ticker", ticker.upper()),
            company_name=data.get("company_name", ticker.upper()),
            executive_summary=data.get("executive_summary", ""),
            bull_case=data.get("bull_case", ""),
            bear_case=data.get("bear_case", ""),
            base_case=data.get("base_case", ""),
            bull_price_target=float(data.get("bull_price_target", 0)),
            bear_price_target=float(data.get("bear_price_target", 0)),
            base_price_target=float(data.get("base_price_target", 0)),
            current_price=current_price,
            catalyst_calendar=data.get("catalyst_calendar", []),
            competitor_comparison=data.get("competitor_comparison", ""),
            dcf_sanity_check=data.get("dcf_sanity_check", ""),
            final_verdict=data.get("final_verdict", ""),
            conviction=int(data.get("conviction", 0)),
            risks=data.get("risks", []),
        )


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def _print_pick(pick: Pick) -> None:
    """Print a pick summary to stdout."""
    rr = f"{pick.risk_reward_ratio:.1f}x R:R"
    print(f"\n{'='*60}")
    print(f"  {pick.ticker:6s}  |  Conviction: {pick.conviction}/10  |  {rr}")
    print(f"  {pick.company_name}")
    print(f"{'='*60}")
    print(f"  Sector:      {pick.sector}")
    print(f"  Entry:       ${pick.entry_price:.2f}  ({pick.entry_window})")
    print(f"  Target:      ${pick.exit_target:.2f}  +{pick.upside_pct:.1f}%  ({pick.exit_window})")
    print(f"  Stop:        ${pick.stop_loss:.2f}  -{pick.downside_pct:.1f}%")
    print(f"  Account:     {pick.account_recommendation}")
    print(f"  Horizon:     {pick.time_horizon}")
    print(f"\n  THESIS")
    print(f"  {pick.thesis}")
    print(f"\n  CATALYSTS")
    for c in pick.catalysts:
        print(f"    - {c}")
    print(f"\n  RISKS")
    for r in pick.risks:
        print(f"    - {r}")
    print(f"\n  MACRO: {pick.macro_alignment}")
    print(f"  TECH:  {pick.technical_setup}")


def _print_deep_dive(dd: DeepDive) -> None:
    """Print a deep dive summary to stdout."""
    upside = ((dd.base_price_target - dd.current_price) / dd.current_price * 100) if dd.current_price > 0 else 0
    print(f"\n{'='*60}")
    print(f"  DEEP DIVE: {dd.ticker}  |  Conviction: {dd.conviction}/10")
    print(f"  {dd.company_name}  |  Current: ${dd.current_price:.2f}")
    print(f"{'='*60}")
    print(f"\n  EXECUTIVE SUMMARY")
    print(f"  {dd.executive_summary}")
    print(f"\n  PRICE TARGETS")
    print(f"    Bull:  ${dd.bull_price_target:.2f}  (+{((dd.bull_price_target - dd.current_price) / dd.current_price * 100):.1f}%)")
    print(f"    Base:  ${dd.base_price_target:.2f}  (+{upside:.1f}%)")
    print(f"    Bear:  ${dd.bear_price_target:.2f}  ({((dd.bear_price_target - dd.current_price) / dd.current_price * 100):.1f}%)")
    print(f"\n  BULL CASE\n  {dd.bull_case[:300]}...")
    print(f"\n  BEAR CASE\n  {dd.bear_case[:300]}...")
    print(f"\n  VERDICT\n  {dd.final_verdict}")
    if dd.catalyst_calendar:
        print(f"\n  CATALYST CALENDAR")
        for c in dd.catalyst_calendar[:8]:
            print(f"    [{c.get('date', '?')}] ({c.get('impact', '?').upper()}) {c.get('event', '')}")


def main() -> None:
    """CLI entry point: python -m research.stock_picker <query | --deep-dive TICKER>"""
    import argparse
    logging.basicConfig(
        level=logging.WARNING,  # Suppress info noise in CLI mode
        format="%(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="python -m research.stock_picker",
        description="Atlas Stock Picker — on-demand equity research",
    )
    parser.add_argument("query", nargs="?", default="", help="Research query (e.g. 'AI infrastructure plays')")
    parser.add_argument("--deep-dive", metavar="TICKER", help="Run a deep dive on a specific ticker")
    parser.add_argument("-n", "--count", type=int, default=3, help="Number of picks (default: 3)")
    parser.add_argument("--horizon", default="6-12 months", help="Time horizon hint")
    parser.add_argument("--save", action="store_true", help="Save picks to data/picks/")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    args = parser.parse_args()

    try:
        agent = StockPickerAgent()
    except EnvironmentError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.deep_dive:
        dd = agent.deep_dive(args.deep_dive.upper())
        if args.json:
            print(json.dumps(dd.__dict__, indent=2, default=str))
        else:
            _print_deep_dive(dd)
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)

    picks = agent.pick(args.query, n=args.count, horizon=args.horizon)

    if not picks:
        print("\nNo picks met the conviction threshold (>= 6/10) for this query.")
        print("Try broadening the query or checking news sources.")
        sys.exit(0)

    if args.json:
        print(json.dumps([p.to_dict() for p in picks], indent=2, default=str))
    else:
        print(f"\nAtlas Research — {len(picks)} pick(s) for: '{args.query}'")
        print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n")
        for pick in picks:
            _print_pick(pick)
            if args.save:
                path = agent.save_pick(pick)
                print(f"\n  Saved to: {path}")

    print()


if __name__ == "__main__":
    main()
