"""
research/stock_picker.py
------------------------
StockPickerAgent — Atlas's on-demand equity research and stock picking engine.

Uses Claude (claude-opus-4-6) as the reasoning core. All data pipeline work
(news ingestion, macro context, fundamentals, technicals, insider, institutional,
earnings, options) is done in Python before the Claude call, so Claude receives
rich structured data rather than being asked to hallucinate numbers.

Every Pick returned is EXECUTION-READY: it contains a specific limit price,
share count, stop-loss, take-profit levels, account routing, and click-by-click
Wealthsimple instructions. CC can act directly from the Telegram message.

Usage:
    from research.stock_picker import StockPickerAgent
    agent = StockPickerAgent()
    picks = agent.pick("AI infrastructure plays for next 6 months", n=3)
    print(picks[0].as_telegram_message())

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
from research.macro_watch import macro_context_summary
from research.fundamentals import get_fundamentals, get_price_history, technicals
from research.psychology import behavioral_snapshot
from research.historical_patterns import cycle_context

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_MODEL = "claude-opus-4-6"
_MAX_TOKENS = 8000
_PICKS_DIR = Path(__file__).resolve().parent.parent / "data" / "picks"
_PICKS_DIR.mkdir(parents=True, exist_ok=True)
_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
_BALANCES_PATH = Path(__file__).resolve().parent.parent / "data" / "manual_balances.json"
_USER_MD_PATH = Path(__file__).resolve().parent.parent / "brain" / "USER.md"

# Floor CC keeps liquid in Montreal / daily life — never invest below this
_MONTREAL_FLOOR_CAD: float = 10_000.0
# CAD/USD approximate exchange rate for share count estimation
_FX_USD_TO_CAD: float = 1.37

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
#  Position sizing helpers
# ─────────────────────────────────────────────────────────────────────────────

def _load_available_cash_cad() -> float:
    """
    Read manual_balances.json and return total investable CAD cash after
    applying the Montreal floor.

    Returns 0.0 if the file is missing or unreadable — callers handle this
    gracefully (position_size_cad will be 0, which triggers the "not enough
    to deploy" message).
    """
    try:
        data = json.loads(_BALANCES_PATH.read_text(encoding="utf-8"))
        total_cad = 0.0
        for entry in data.get("balances", []):
            if entry.get("category") not in ("cash",):
                continue
            amt = float(entry.get("amount", 0))
            currency = entry.get("currency", "CAD").upper()
            if currency == "USD":
                amt *= _FX_USD_TO_CAD
            total_cad += amt
        return max(0.0, total_cad - _MONTREAL_FLOOR_CAD)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not load manual_balances.json: %s", exc)
        return 0.0


def _compute_position_size_cad(available_cad: float, conviction: int) -> float:
    """
    position_size_cad = available_to_invest * 0.25 * (conviction / 10)

    Floored at $500 CAD. Returns 0 if below floor (caller should surface
    "not enough to deploy" message to CC).
    """
    raw = available_cad * 0.25 * (conviction / 10.0)
    return raw if raw >= 500.0 else 0.0


def _share_count(position_size_cad: float, limit_price_usd: float) -> int:
    """Convert a CAD position size to a whole share count at a USD price."""
    if limit_price_usd <= 0 or position_size_cad <= 0:
        return 0
    position_usd = position_size_cad / _FX_USD_TO_CAD
    return max(1, int(position_usd / limit_price_usd))


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Pick:
    """A single equity pick with full research backing and execution-ready fields."""

    # ── Core research fields (unchanged) ────────────────────────────────────
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
    conviction: int                          # 0-10
    time_horizon: str
    risk_reward_ratio: float
    upside_pct: float
    downside_pct: float
    risks: list[str]
    macro_alignment: str
    technical_setup: str
    tax_note: str
    account_recommendation: str              # "TFSA" | "RRSP" | "Non-Reg"
    sources_used: list[str]
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    query: str = ""

    # ── Execution-ready fields ───────────────────────────────────────────────
    order_type: str = "limit_buy"
    limit_price: float = 0.0
    limit_price_rationale: str = ""
    position_size_cad: float = 0.0
    share_count: int = 0
    stop_loss_price: float = 0.0
    stop_loss_execution_rationale: str = ""
    take_profit_1: float = 0.0
    take_profit_2: float = 0.0
    take_profit_3: float = 0.0
    time_in_force: str = "GTC"
    account: str = "TFSA"                    # "TFSA" | "FHSA" | "personal_non_registered"
    wealthsimple_steps: list[str] = field(default_factory=list)

    # ── Signal summary fields ────────────────────────────────────────────────
    insider_signal: str = ""
    institutional_signal: str = ""
    earnings_signal: str = ""
    options_signal: str = ""
    signal_conflicts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    # ── Display methods ──────────────────────────────────────────────────────

    def as_telegram_message(self) -> str:
        """
        Return a Telegram-formatted markdown string under 4000 chars.

        Telegram uses MarkdownV2 escaping but this method produces the simpler
        Telegram HTML-safe plain markdown that works with parse_mode=Markdown.
        Callers should use parse_mode='Markdown' or send as plain text.
        """
        stars = conviction_bar(self.conviction)
        conflict_block = ""
        if self.signal_conflicts:
            conflict_lines = "\n".join(f"  {c}" for c in self.signal_conflicts)
            conflict_block = f"\n*SIGNAL CONFLICT*\n{conflict_lines}\n"

        # Account display
        account_display = {
            "TFSA": "Wealthsimple TFSA",
            "FHSA": "Wealthsimple FHSA",
            "personal_non_registered": "Wealthsimple Personal (Non-Reg)",
        }.get(self.account, self.account)

        # Position sizing block
        if self.position_size_cad == 0 or self.share_count == 0:
            sizing_line = "  Not enough investable cash to deploy (< $500 CAD after floor)"
        else:
            approx_cad = round(self.share_count * self.limit_price * _FX_USD_TO_CAD, 2)
            sizing_line = (
                f"Shares:       {self.share_count} shares "
                f"(approx ${approx_cad:,.0f} CAD at {_FX_USD_TO_CAD:.2f} FX)"
            )

        # TP returns
        def _pct(target: float) -> str:
            if self.limit_price <= 0:
                return "N/A"
            return f"{((target - self.limit_price) / self.limit_price) * 100:+.1f}%"

        def _sl_pct() -> str:
            if self.limit_price <= 0:
                return "N/A"
            return f"{((self.stop_loss_price - self.limit_price) / self.limit_price) * 100:+.1f}%"

        # Wealthsimple steps
        ws_steps = "\n".join(
            f"{i+1}. {step}"
            for i, step in enumerate(self.wealthsimple_steps)
        ) if self.wealthsimple_steps else "  See execution block above."

        # Risks (cap at 5)
        risks_block = "\n".join(f"- {r}" for r in self.risks[:5])

        # Catalysts (cap at 3)
        catalysts_block = "\n".join(f"- {c}" for c in self.catalysts[:3])

        divider = "-" * 32
        msg = (
            f"*PICK: {self.ticker} ({self.company_name}) -- Conviction {self.conviction}/10 {stars}*"
            f"{conflict_block}\n"
            f"*THESIS*\n"
            f"{self.thesis}\n\n"
            f"*CATALYSTS*\n{catalysts_block}\n\n"
            f"*EXECUTION ({account_display})*\n"
            f"{divider}\n"
            f"Order type:   LIMIT BUY ({self.time_in_force}, 90 days)\n"
            f"Limit price:  ${self.limit_price:.2f}\n"
            f"{sizing_line}\n"
            f"Stop loss:    ${self.stop_loss_price:.2f} ({_sl_pct()})\n"
            f"TP1 (33%):    ${self.take_profit_1:.2f} ({_pct(self.take_profit_1)})\n"
            f"TP2 (33%):    ${self.take_profit_2:.2f} ({_pct(self.take_profit_2)})\n"
            f"TP3 (34%):    ${self.take_profit_3:.2f} ({_pct(self.take_profit_3)})\n\n"
            f"*WEALTHSIMPLE STEPS*\n"
            f"{ws_steps}\n\n"
            f"*MULTI-LAYER SIGNAL*\n"
            f"{divider}\n"
            f"Fundamentals: {self.technical_setup}\n"
            f"Macro:        {self.macro_alignment}\n"
            f"Insider:      {self.insider_signal}\n"
            f"Institutional:{self.institutional_signal}\n"
            f"Earnings:     {self.earnings_signal}\n"
            f"Options:      {self.options_signal}\n\n"
            f"*RISKS*\n{risks_block}\n\n"
            f"*TAX NOTE*\n{self.tax_note}\n"
            f"\n_Generated {self.generated_at[:10]} | Query: {self.query}_"
        )

        # Enforce 4000-char Telegram limit with a hard truncation at a newline
        if len(msg) > 3950:
            msg = msg[:3947] + "..."

        return msg

    def as_cli_block(self) -> str:
        """Render the pick as an ASCII-bordered block for terminal display."""
        width = 60
        bar = "=" * width
        thin = "-" * width

        def _pct(target: float) -> str:
            if self.limit_price <= 0:
                return "N/A"
            return f"{((target - self.limit_price) / self.limit_price) * 100:+.1f}%"

        def _sl_pct() -> str:
            if self.limit_price <= 0:
                return "N/A"
            return f"{((self.stop_loss_price - self.limit_price) / self.limit_price) * 100:+.1f}%"

        share_line = (
            f"  Shares:       {self.share_count} shares "
            f"(~${self.share_count * self.limit_price * _FX_USD_TO_CAD:,.0f} CAD)"
            if self.share_count > 0
            else "  Shares:       not enough cash to deploy"
        )

        ws_steps = "\n".join(
            f"  {i+1}. {step}"
            for i, step in enumerate(self.wealthsimple_steps)
        ) if self.wealthsimple_steps else "  See execution block."

        conflicts = (
            "\n  SIGNAL CONFLICTS\n" + "\n".join(f"  ! {c}" for c in self.signal_conflicts)
            if self.signal_conflicts else ""
        )

        risks_block = "\n".join(f"  - {r}" for r in self.risks[:5])
        catalysts_block = "\n".join(f"  - {c}" for c in self.catalysts[:3])

        return textwrap.dedent(f"""
{bar}
  {self.ticker:6s}  |  {self.company_name}
  Conviction: {self.conviction}/10 {conviction_bar(self.conviction)}  |  {self.time_horizon}
{bar}{conflicts}

  THESIS
  {self.thesis}

  CATALYSTS
{catalysts_block}

{thin}
  EXECUTION — {self.account}
{thin}
  Order:        LIMIT BUY (GTC, 90 days)
  Limit:        ${self.limit_price:.2f}  ({self.limit_price_rationale})
{share_line}
  Stop loss:    ${self.stop_loss_price:.2f} ({_sl_pct()})  —  {self.stop_loss_execution_rationale}
  TP1 (33%):    ${self.take_profit_1:.2f} ({_pct(self.take_profit_1)})
  TP2 (33%):    ${self.take_profit_2:.2f} ({_pct(self.take_profit_2)})
  TP3 (34%):    ${self.take_profit_3:.2f} ({_pct(self.take_profit_3)})

  WEALTHSIMPLE STEPS
{ws_steps}

{thin}
  SIGNALS
{thin}
  Fundamentals: {self.technical_setup}
  Macro:        {self.macro_alignment}
  Insider:      {self.insider_signal}
  Institutional:{self.institutional_signal}
  Earnings:     {self.earnings_signal}
  Options:      {self.options_signal}

  RISKS
{risks_block}

  TAX NOTE
  {self.tax_note}
{bar}
""").strip()

    def to_markdown(self) -> str:
        """Render pick as a markdown tracking entry (for data/picks/ files)."""
        stars = "★" * self.conviction + "☆" * (10 - self.conviction)

        def _pct(target: float) -> str:
            if self.limit_price <= 0:
                return "N/A"
            return f"+{((target - self.limit_price) / self.limit_price) * 100:.1f}%"

        conflicts_md = (
            "\n### Signal Conflicts\n" + "\n".join(f"- {c}" for c in self.signal_conflicts)
            if self.signal_conflicts else ""
        )

        ws_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(self.wealthsimple_steps))

        return textwrap.dedent(f"""
# {self.ticker} — {self.company_name}
**Generated:** {self.generated_at[:10]}  |  **Query:** {self.query}  |  **Conviction:** {stars} ({self.conviction}/10)
{conflicts_md}

## Thesis
{self.thesis}

## Key Catalysts
{chr(10).join(f"- {c}" for c in self.catalysts)}

## Execution
| Field | Value |
|-------|-------|
| Account | {self.account} |
| Order Type | {self.order_type.upper()} |
| Limit Price | ${self.limit_price:.2f} |
| Share Count | {self.share_count} ({self.position_size_cad:,.0f} CAD) |
| Stop Loss | ${self.stop_loss_price:.2f} |
| TP1 (33%) | ${self.take_profit_1:.2f} ({_pct(self.take_profit_1)}) |
| TP2 (33%) | ${self.take_profit_2:.2f} ({_pct(self.take_profit_2)}) |
| TP3 (34%) | ${self.take_profit_3:.2f} ({_pct(self.take_profit_3)}) |
| Time in Force | {self.time_in_force} |
| R:R | {self.risk_reward_ratio:.1f}x |

### Wealthsimple Steps
{ws_md}

## Multi-Layer Signal
| Layer | Signal |
|-------|--------|
| Insider | {self.insider_signal} |
| Institutional | {self.institutional_signal} |
| Earnings | {self.earnings_signal} |
| Options | {self.options_signal} |

## Trade Parameters (Legacy)
| Field | Value |
|-------|-------|
| Entry Window | {self.entry_window} |
| Exit Target | ${self.exit_target:.2f} (+{self.upside_pct:.1f}%) |
| Exit Window | {self.exit_window} |
| Time Horizon | {self.time_horizon} |

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


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def conviction_bar(conviction: int) -> str:
    """Return a compact visual conviction indicator."""
    filled = min(conviction, 10)
    empty = 10 - filled
    return "[" + "#" * filled + "." * empty + "]"


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
    catalyst_calendar: list[dict]            # [{"date": "YYYY-MM", "event": "...", "impact": "high/med/low"}]
    competitor_comparison: str
    dcf_sanity_check: str                    # 5-yr DCF summary
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
        "Return a JSON array of stock picks. Only include picks with conviction >= 6."
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Signal fetching helpers (all wrapped in try/except)
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_insider_signal(ticker: str) -> dict:
    """Fetch insider_score for ticker. Returns empty dict on failure."""
    try:
        from research.insider_tracking import insider_score as _insider_score
        return _insider_score(ticker)
    except Exception as exc:
        logger.warning("insider_score failed for %s: %s", ticker, exc)
        return {}


def _fetch_institutional_signal(ticker: str) -> list[dict]:
    """Fetch who_owns for ticker. Returns empty list on failure."""
    try:
        from research.institutional_tracking import who_owns as _who_owns
        return _who_owns(ticker)
    except Exception as exc:
        logger.warning("who_owns failed for %s: %s", ticker, exc)
        return []


def _fetch_earnings_signals(ticker: str) -> tuple[Optional[int], dict]:
    """
    Returns (days_to_next, surprise_score_dict).
    Both may be None/empty on failure.
    """
    days: Optional[int] = None
    surp: dict = {}
    try:
        from research.earnings_calendar import days_to_next_earnings as _days
        days = _days(ticker)
    except Exception as exc:
        logger.warning("days_to_next_earnings failed for %s: %s", ticker, exc)
    try:
        from research.earnings_calendar import surprise_score as _surprise
        surp = _surprise(ticker)
    except Exception as exc:
        logger.warning("surprise_score failed for %s: %s", ticker, exc)
    return days, surp


def _fetch_options_signals(ticker: str) -> tuple[dict, dict, Optional[float]]:
    """
    Returns (snapshot_dict, squeeze_dict, iv_rank_float).
    Snapshot is converted to dict so it's JSON-serialisable in the prompt.
    """
    snap: dict = {}
    squeeze: dict = {}
    ivr: Optional[float] = None
    try:
        from research.options_flow import get_options_snapshot as _snap
        s = _snap(ticker)
        snap = {
            "put_call_oi_ratio": s.put_call_oi_ratio,
            "total_call_oi": s.total_call_oi,
            "total_put_oi": s.total_put_oi,
            "atm_iv_pct": s.atm_iv_pct,
            "short_interest_pct": s.short_interest_pct,
            "days_to_cover": s.days_to_cover,
            "iv_rank": s.iv_rank,
        }
    except Exception as exc:
        logger.warning("get_options_snapshot failed for %s: %s", ticker, exc)
    try:
        from research.options_flow import squeeze_score as _squeeze
        squeeze = _squeeze(ticker)
    except Exception as exc:
        logger.warning("squeeze_score failed for %s: %s", ticker, exc)
    try:
        from research.options_flow import iv_rank as _ivr
        ivr = _ivr(ticker)
    except Exception as exc:
        logger.warning("iv_rank failed for %s: %s", ticker, exc)
    return snap, squeeze, ivr


def _format_insider_signal_str(score: dict) -> str:
    """Convert insider_score dict to a compact one-liner for the prompt and display."""
    if not score:
        return "No data"
    sig = score.get("signal", "neutral").upper()
    net = score.get("net_dollars", 0)
    cluster = score.get("cluster_buying", False)
    summary = score.get("summary", "")
    net_str = f"${abs(net / 1_000_000):.1f}M" if abs(net) >= 1_000_000 else f"${abs(net / 1_000):.0f}K"
    cluster_tag = " (CLUSTER)" if cluster else ""
    sign = "+" if net >= 0 else "-"
    return f"{sig}{cluster_tag} — net {sign}{net_str} — {summary}"


def _format_institutional_signal_str(holdings: list[dict]) -> str:
    """Convert who_owns list to a compact one-liner."""
    if not holdings:
        return "No tracked fund holds this"
    parts = []
    for h in holdings[:4]:
        fund = h.get("fund_name", "?")
        pct = h.get("pct_of_portfolio", 0.0)
        val = h.get("value_usd", 0)
        val_str = (
            f"${val / 1_000_000_000:.1f}B" if val >= 1_000_000_000
            else f"${val / 1_000_000:.0f}M"
        )
        parts.append(f"{fund} {pct:.1f}% ({val_str})")
    return " | ".join(parts)


def _format_earnings_signal_str(days: Optional[int], surp: dict) -> str:
    """Convert earnings data to a compact one-liner."""
    parts = []
    if days is not None:
        parts.append(f"next earnings in {days}d")
    elif days == 0:
        parts.append("earnings TODAY")
    beats = surp.get("beats", 0)
    total = surp.get("data_available", 0)
    avg = surp.get("avg_surprise_pct", 0.0)
    signal = surp.get("signal", "")
    if total > 0:
        parts.append(f"{beats}/{total} beats, avg {avg:+.1f}% surprise")
    if signal:
        parts.append(signal.upper())
    return " — ".join(parts) if parts else "No data"


def _format_options_signal_str(snap: dict, squeeze: dict, ivr: Optional[float]) -> str:
    """Convert options data to a compact one-liner."""
    parts = []
    pc = snap.get("put_call_oi_ratio")
    if pc is not None:
        parts.append(f"P/C {pc:.2f}")
    if ivr is not None:
        cheap_tag = " (options cheap)" if ivr < 30 else " (options expensive)" if ivr > 70 else ""
        parts.append(f"IV rank {ivr:.0f}/100{cheap_tag}")
    sq = squeeze.get("score", 0)
    sq_signal = squeeze.get("signal", "")
    if sq_signal and sq_signal != "no_squeeze":
        parts.append(f"squeeze {sq_signal} ({sq}/10)")
    return " | ".join(parts) if parts else "No options data"


def _detect_signal_conflicts(
    insider_score_dict: dict,
    institutional_holdings: list[dict],
    tech: dict,
    surp: dict,
) -> list[str]:
    """
    Surface clear disagreements between data layers so Claude (and CC) can see them.
    Returns a list of plain-English conflict strings.
    """
    conflicts: list[str] = []

    sig = insider_score_dict.get("signal", "neutral")
    net = insider_score_dict.get("net_dollars", 0)

    # Insider selling while technicals bullish
    if sig in ("sell", "strong_sell") and tech.get("trend") in ("up", "strong_up"):
        net_m = abs(net / 1_000_000) if abs(net) >= 1_000_000 else abs(net / 1_000)
        unit = "M" if abs(net) >= 1_000_000 else "K"
        conflicts.append(
            f"Bullish technicals (uptrend) BUT insiders net selling "
            f"${net_m:.1f}{unit} — Cohen et al. (2012) cluster-sell is bearish signal"
        )

    # Cluster insider buying (strong positive) while earnings misser
    if sig in ("strong_buy", "buy") and surp.get("signal") == "unreliable":
        conflicts.append(
            "Insider cluster buying BUT earnings track record is unreliable "
            "(< 40% beat rate) — catalyst timing risk elevated"
        )

    # Heavy institutional holding but insider selling (smart money vs insider divergence)
    if institutional_holdings and sig in ("strong_sell", "sell"):
        fund_count = len(institutional_holdings)
        conflicts.append(
            f"{fund_count} tracked legend(s) hold this BUT insiders are selling — "
            "check if institutional data is stale (13F is quarterly)"
        )

    return conflicts


# ─────────────────────────────────────────────────────────────────────────────
#  Main agent class
# ─────────────────────────────────────────────────────────────────────────────

class StockPickerAgent:
    """
    Claude-powered equity research agent.

    All quantitative data assembly happens in Python.
    Claude's job is interpretation, thesis formation, and structured output
    including EXECUTION-READY limit prices, stop-losses, take-profits,
    share counts, and Wealthsimple click instructions.
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
        Run the full research pipeline and return n execution-ready stock picks.

        Args:
            query: Natural language request (e.g. "AI infrastructure plays")
            n: Number of picks to return (max 5 recommended for quality)
            horizon: Time horizon hint fed to Claude
            candidate_tickers: Optional pre-screened list; if None, inferred from query

        Returns:
            List of Pick dataclasses with all execution fields populated,
            sorted by conviction descending.
        """
        logger.info("Running stock picker: query='%s', n=%d, horizon=%s", query, n, horizon)

        tickers = candidate_tickers or self._infer_tickers(query)
        news = self._gather_news(query, tickers)
        macro_ctx = macro_context_summary(news)
        ticker_data = self._gather_ticker_data(tickers)

        # Wisdom layer — behavioral psychology + historical cycle context
        try:
            psych_snap = behavioral_snapshot()
        except Exception as exc:
            logger.warning("behavioral_snapshot failed: %s", exc)
            psych_snap = {}
        try:
            cycle_ctx = cycle_context(tickers[0] if tickers else "SPY")
        except Exception as exc:
            logger.warning("cycle_context failed: %s", exc)
            cycle_ctx = {}

        # Extended signal layer — insider, institutional, earnings, options
        # Fetched per-ticker; failures are non-fatal.
        extended_signals: dict[str, dict] = {}
        for ticker in tickers:
            insider = _fetch_insider_signal(ticker)
            institutions = _fetch_institutional_signal(ticker)
            days_to_earn, surprise = _fetch_earnings_signals(ticker)
            opt_snap, opt_squeeze, opt_ivr = _fetch_options_signals(ticker)

            # Pre-compute display strings
            tech = ticker_data.get(ticker, {}).get("technicals", {})
            conflicts = _detect_signal_conflicts(insider, institutions, tech, surprise)

            extended_signals[ticker] = {
                "insider_score": insider,
                "insider_signal_str": _format_insider_signal_str(insider),
                "institutional_holdings": institutions,
                "institutional_signal_str": _format_institutional_signal_str(institutions),
                "days_to_next_earnings": days_to_earn,
                "surprise_score": surprise,
                "earnings_signal_str": _format_earnings_signal_str(days_to_earn, surprise),
                "options_snapshot": opt_snap,
                "options_squeeze": opt_squeeze,
                "options_ivr": opt_ivr,
                "options_signal_str": _format_options_signal_str(opt_snap, opt_squeeze, opt_ivr),
                "signal_conflicts": conflicts,
            }

        # Position sizing context
        available_cad = _load_available_cash_cad()

        prompt = self._build_pick_prompt(
            query=query,
            n=n,
            horizon=horizon,
            tickers=tickers,
            ticker_data=ticker_data,
            macro_ctx=macro_ctx,
            news=news,
            psych_snap=psych_snap,
            cycle_ctx=cycle_ctx,
            extended_signals=extended_signals,
            available_cad=available_cad,
        )

        raw = self._call_claude(prompt)
        picks = self._parse_picks(
            raw,
            query=query,
            extended_signals=extended_signals,
            available_cad=available_cad,
        )

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
        for ticker in tickers[:3]:
            _add(fetch_google_news(ticker, days=14))
        _add(fetch_newsapi(query, days=14))

        news.sort(key=lambda x: x.date, reverse=True)
        return news[:50]

    def _gather_ticker_data(self, tickers: list[str]) -> dict[str, dict]:
        """Fetch fundamentals + technicals for each ticker."""
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
            lines = [
                f"- {f.filed_date.strftime('%Y-%m-%d')}: {f.form_type} — {f.description}"
                for f in filings_8k[:5]
            ]
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
        psych_snap: dict,
        cycle_ctx: dict,
        extended_signals: dict[str, dict],
        available_cad: float,
    ) -> str:
        """Assemble the full prompt for a pick request, including all signal layers."""
        news_digest = "\n".join(
            f"- [{item.date.strftime('%Y-%m-%d')}] {item.source}: {item.title}"
            for item in news[:30]
        )

        # ── Ticker digest ─────────────────────────────────────────────────────
        ticker_digest_parts: list[str] = []
        for ticker, data in ticker_data.items():
            if "error" in data:
                ticker_digest_parts.append(f"### {ticker}\nData unavailable: {data['error']}")
                continue
            fund = data.get("fundamentals", {})
            tech = data.get("technicals", {})
            val = data.get("valuation", "")
            ext = extended_signals.get(ticker, {})

            # Conflict block
            conflicts = ext.get("signal_conflicts", [])
            conflict_str = (
                "\n**SIGNAL CONFLICTS:** " + " | ".join(conflicts)
                if conflicts else ""
            )

            # Institutional holders block
            inst_holdings = ext.get("institutional_holdings", [])
            inst_block = ""
            if inst_holdings:
                inst_lines = []
                for h in inst_holdings[:5]:
                    fund_name = h.get("fund_name", "?")
                    pct = h.get("pct_of_portfolio", 0.0)
                    val_usd = h.get("value_usd", 0)
                    val_str = (
                        f"${val_usd / 1_000_000_000:.1f}B"
                        if val_usd >= 1_000_000_000
                        else f"${val_usd / 1_000_000:.0f}M"
                    )
                    change = h.get("change_vs_prior") or "no change"
                    inst_lines.append(f"  - {fund_name}: {pct:.1f}% portfolio, {val_str} ({change})")
                inst_block = "**Institutional (13F tracked legends):**\n" + "\n".join(inst_lines)

            ticker_digest_parts.append(
                f"### {ticker} — {fund.get('name', ticker)}{conflict_str}\n"
                f"**Sector:** {fund.get('sector', 'Unknown')} | **Industry:** {fund.get('industry', 'Unknown')}\n"
                f"**Valuation:** {val}\n"
                f"**Market Cap:** ${fund.get('market_cap', 0):,.0f}\n"
                f"**Analyst Rating:** {fund.get('analyst_rating', 'N/A')} | "
                f"**Target:** ${fund.get('analyst_target_price', 0):.2f}\n"
                f"**Operating Margin:** {fund.get('operating_margin', 'N/A')}% | "
                f"**Revenue Growth:** {fund.get('revenue_growth_yoy', 'N/A')}%\n"
                f"**Short Interest:** {fund.get('short_interest_pct', 'N/A')}% | "
                f"**Institutional Holdings:** {fund.get('institutional_ownership_pct', 'N/A')}%\n"
                f"**Technicals:** Price ${tech.get('latest_price', 0):.2f} | "
                f"RSI {tech.get('rsi_14', 'N/A')} | "
                f"Trend: {tech.get('trend', 'unknown')} | "
                f"vs 52w High: {tech.get('price_vs_52wk_high_pct', 'N/A')}% | "
                f"SMA50: ${tech.get('sma_50', 'N/A')} | SMA200: ${tech.get('sma_200', 'N/A')}\n"
                f"{'GOLDEN CROSS active' if tech.get('golden_cross') else 'DEATH CROSS active' if tech.get('death_cross') else 'No SMA cross signal'}\n"
                f"**Insider:** {ext.get('insider_signal_str', 'No data')}\n"
                f"{inst_block}\n"
                f"**Earnings:** {ext.get('earnings_signal_str', 'No data')}\n"
                f"**Options:** {ext.get('options_signal_str', 'No data')}"
            )
        ticker_digest = "\n\n".join(ticker_digest_parts)

        # ── Psychology block ──────────────────────────────────────────────────
        psych_block = ""
        if psych_snap:
            regime      = psych_snap.get("regime", "unknown")
            greed_score = psych_snap.get("greed_score", "N/A")
            narrative   = psych_snap.get("narrative", "")
            flags       = psych_snap.get("flags", [])
            vix_data    = psych_snap.get("components", {}).get("vix", {})
            fng_data    = psych_snap.get("components", {}).get("fear_greed_index", {})

            flags_text = "\n".join(f"  - {f}" for f in flags) if flags else "  - None"
            psych_block = (
                f"## Market Psychology (Behavioral Finance Layer)\n"
                f"**Regime:** {regime.replace('_', ' ').title()}  |  "
                f"**Composite Greed Score:** {greed_score}/100\n"
                f"**VIX:** {vix_data.get('vix_spot', 'N/A')} ({vix_data.get('classification', 'N/A')})  |  "
                f"**Term Structure:** {vix_data.get('term_structure', 'N/A')}\n"
                f"**CNN Fear & Greed:** {fng_data.get('value', 'N/A')} — {fng_data.get('classification', 'N/A')}\n"
                f"**Active Flags:**\n{flags_text}\n\n"
                f"**Narrative:** {narrative}"
            )

        # ── Cycle block ───────────────────────────────────────────────────────
        cycle_block = ""
        if cycle_ctx:
            cycle_narrative  = cycle_ctx.get("narrative", "")
            pres_cycle       = cycle_ctx.get("presidential_cycle", {})
            seasonal         = cycle_ctx.get("seasonality", {})
            top_analogs      = cycle_ctx.get("top_analogs", [])
            regime_data      = cycle_ctx.get("regime", {})

            analog_lines: list[str] = []
            for a in top_analogs[:2]:
                won  = ", ".join(a.get("sectors_that_won", [])[:3])
                lost = ", ".join(a.get("sectors_that_lost", [])[:3])
                analog_lines.append(
                    f"  - **{a.get('name')}** ({a.get('year')}, "
                    f"similarity {a.get('similarity_score', 0):.0%}, "
                    f"drawdown {a.get('avg_drawdown')}%): "
                    f"WON: {won} | LOST: {lost}"
                )

            analog_text = "\n".join(analog_lines) if analog_lines else "  - Insufficient data"
            cur_month     = seasonal.get("current_month", "")
            month_rank    = seasonal.get("current_month_rank", "?")
            month_avg     = seasonal.get("current_month_avg")
            month_avg_str = f"{month_avg:.1f}%" if month_avg is not None else "N/A"
            best_months   = ", ".join(seasonal.get("best_months", []))
            worst_months  = ", ".join(seasonal.get("worst_months", []))

            cycle_block = (
                f"## Historical & Cycle Context (Wisdom Layer)\n"
                f"**Market Regime:** {regime_data.get('regime', 'N/A').replace('_', ' ').title()}\n"
                f"{regime_data.get('regime_description', '')}\n\n"
                f"**Presidential Cycle:** Year {pres_cycle.get('year_of_cycle', '?')} of 4 — "
                f"historical SPY avg {pres_cycle.get('historical_sp500_avg_return', 'N/A')}%\n"
                f"{pres_cycle.get('verdict', '')}\n\n"
                f"**Seasonality ({seasonal.get('ticker', 'SPY')}):** "
                f"{cur_month} ranks #{month_rank}/12 (avg {month_avg_str})\n"
                f"Best months: {best_months}  |  Worst months: {worst_months}\n\n"
                f"**Closest Historical Analogs:**\n{analog_text}\n\n"
                f"**Synthesis:** {cycle_narrative}"
            )

        # ── Position sizing context ───────────────────────────────────────────
        montreal_floor = _MONTREAL_FLOOR_CAD
        sizing_context = (
            f"## CC's Available Capital\n"
            f"**Total liquid CAD (after Montreal floor of ${montreal_floor:,.0f}):** "
            f"${available_cad:,.2f} investable\n"
            f"**Sizing rule:** position_size_cad = available * 0.25 * (conviction / 10)\n"
            f"**Minimum position:** $500 CAD (below this, say 'not enough to deploy')\n"
            f"**FX rate for share count:** 1 USD = {_FX_USD_TO_CAD} CAD (approximate)\n"
        )

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

{psych_block}

---

{cycle_block}

---

{sizing_context}

---

## Recent News Headlines (last 14 days)
{news_digest}

---

## Candidate Tickers: {', '.join(tickers)}

{ticker_digest}

---

## Instructions
Based on all data above, select the {n} BEST picks that match the query '{query}'.
Apply the Anti-Bullshit Rules and conviction threshold (>=6) strictly.
Use the Market Psychology and Historical Cycle Context sections to stress-test
each thesis — a pick must make sense given the current behavioral regime AND
the closest historical analog. Flag any picks that swim against the cycle.

EXECUTION-READY OUTPUT REQUIRED:
For each pick you MUST provide:
1. A SINGLE specific limit_price (not a range). Justify it with limit_price_rationale
   (e.g. "4% pullback to 50-SMA", "current price - 2x ATR", "key support level").
2. stop_loss_price: The EXACT price that invalidates the thesis. Include stop_loss_execution_rationale.
3. take_profit_1, take_profit_2, take_profit_3: Specific price levels at approximately
   1:1 R:R (33% exit), 2:1 R:R (33% exit), and full thesis target (34% exit).
4. account: "TFSA" for high-growth US equity (gains stay tax-free forever);
   "FHSA" for mid-horizon plays with real estate alignment; "personal_non_registered"
   for tactical/short-duration positions or anything that doesn't fit TFSA headroom.
5. wealthsimple_steps: A JSON array of click-by-click strings to execute on Wealthsimple
   (e.g. "Open Wealthsimple → tap TFSA account", "Search 'NVDA' → tap Trade → tap Buy",
   "Change 'Market' to 'Limit'", "Set price: 185.00 | Shares: 8",
   "Set time in force: GTC (Good Til Cancelled, 90 days)", "Review → Submit",
   "AFTER FILL: set a stop-loss order at $168").
6. signal_conflicts: A JSON array of plain-English strings describing any disagreements
   between data layers. If insiders are selling but fundamentals are bullish, say so.
   Reduce conviction by 1-2 points per major conflict and EXPLAIN why you are keeping
   or rejecting the pick despite it.

PASSPORT CONTEXT (NON-NEGOTIABLE):
CC is a British passport holder planning UK/Crown Dependencies tax residency between
ages 25-28 (approximately 2028-2031). Growth positions should be TFSA-protected
(TFSA gains remain Canadian-tax-free even after emigration while the account is held).
At emigration, TFSA holdings freeze for contribution purposes but existing holdings
grow tax-free under Canadian rules. Plan: simplify TFSA holdings before emigration.
Reference this in tax_note for each pick.

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

    def _parse_picks(
        self,
        raw: str,
        query: str = "",
        extended_signals: Optional[dict[str, dict]] = None,
        available_cad: float = 0.0,
    ) -> list[Pick]:
        """
        Parse Claude's JSON output into Pick objects, enriching with
        pre-fetched signal strings and computing share counts.
        """
        extended_signals = extended_signals or {}
        text = raw.strip()

        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
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
                ticker = item.get("ticker", "UNKNOWN").upper()
                conviction = int(item.get("conviction", 0))
                ext = extended_signals.get(ticker, {})

                # Execution fields from Claude output
                limit_price = float(item.get("limit_price", item.get("entry_price", 0)))
                stop_loss_price = float(
                    item.get("stop_loss_price", item.get("stop_loss", 0))
                )

                # Position size calculation
                pos_size = _compute_position_size_cad(available_cad, conviction)
                shares = _share_count(pos_size, limit_price)

                # Build default Wealthsimple steps if Claude didn't provide them
                ws_steps: list[str] = item.get("wealthsimple_steps", [])
                if not ws_steps and limit_price > 0:
                    account_val = item.get("account", "TFSA")
                    ws_steps = _default_wealthsimple_steps(
                        ticker=ticker,
                        account=account_val,
                        limit_price=limit_price,
                        shares=shares,
                        stop_loss_price=stop_loss_price,
                    )

                pick = Pick(
                    # Core fields
                    ticker=ticker,
                    company_name=item.get("company_name", ""),
                    sector=item.get("sector", ""),
                    thesis=item.get("thesis", ""),
                    catalysts=item.get("catalysts", []),
                    entry_price=float(item.get("entry_price", limit_price)),
                    entry_window=item.get("entry_window", ""),
                    entry_rationale=item.get("entry_rationale", ""),
                    exit_target=float(item.get("exit_target", item.get("take_profit_3", 0))),
                    exit_window=item.get("exit_window", ""),
                    exit_rationale=item.get("exit_rationale", ""),
                    stop_loss=stop_loss_price,
                    stop_loss_rationale=item.get("stop_loss_rationale", ""),
                    conviction=conviction,
                    time_horizon=item.get("time_horizon", ""),
                    risk_reward_ratio=float(item.get("risk_reward_ratio", 0)),
                    upside_pct=float(item.get("upside_pct", 0)),
                    downside_pct=float(item.get("downside_pct", 0)),
                    risks=item.get("risks", []),
                    macro_alignment=item.get("macro_alignment", ""),
                    technical_setup=item.get("technical_setup", ""),
                    tax_note=item.get("tax_note", ""),
                    account_recommendation=item.get("account_recommendation", item.get("account", "TFSA")),
                    sources_used=item.get("sources_used", ["yfinance"]),
                    query=query,
                    # Execution fields
                    order_type="limit_buy",
                    limit_price=limit_price,
                    limit_price_rationale=item.get("limit_price_rationale", ""),
                    position_size_cad=pos_size,
                    share_count=shares,
                    stop_loss_price=stop_loss_price,
                    stop_loss_execution_rationale=item.get(
                        "stop_loss_execution_rationale",
                        item.get("stop_loss_rationale", ""),
                    ),
                    take_profit_1=float(item.get("take_profit_1", 0)),
                    take_profit_2=float(item.get("take_profit_2", 0)),
                    take_profit_3=float(item.get("take_profit_3", item.get("exit_target", 0))),
                    time_in_force="GTC",
                    account=item.get("account", item.get("account_recommendation", "TFSA")),
                    wealthsimple_steps=ws_steps,
                    # Signal summary — use pre-fetched strings, fall back to Claude's
                    insider_signal=ext.get("insider_signal_str") or item.get("insider_signal", ""),
                    institutional_signal=ext.get("institutional_signal_str") or item.get("institutional_signal", ""),
                    earnings_signal=ext.get("earnings_signal_str") or item.get("earnings_signal", ""),
                    options_signal=ext.get("options_signal_str") or item.get("options_signal", ""),
                    signal_conflicts=(
                        ext.get("signal_conflicts") or item.get("signal_conflicts", [])
                    ),
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
#  Wealthsimple step generator
# ─────────────────────────────────────────────────────────────────────────────

def _default_wealthsimple_steps(
    ticker: str,
    account: str,
    limit_price: float,
    shares: int,
    stop_loss_price: float,
) -> list[str]:
    """
    Generate click-by-click Wealthsimple instructions when Claude doesn't
    provide them. These are generic but accurate for the Wealthsimple app.
    """
    account_display = {
        "TFSA": "TFSA account",
        "FHSA": "FHSA account",
        "personal_non_registered": "Personal (non-registered) account",
    }.get(account, f"{account} account")

    steps = [
        f"Open Wealthsimple app",
        f"Tap '{account_display}' from the Accounts tab",
        f"Tap the Search icon and type '{ticker}'",
        f"Tap '{ticker}' in results then tap 'Trade'",
        f"Tap 'Buy'",
        f"Tap 'Market' (order type) and change to 'Limit'",
        f"Enter price: {limit_price:.2f}",
        f"Enter quantity: {shares} share{'s' if shares != 1 else ''}",
        f"Tap 'Duration' and select 'Good 'Til Cancelled (GTC)'",
        f"Review all fields then tap 'Submit order'",
    ]
    if stop_loss_price > 0:
        steps.append(
            f"AFTER FILL: go back to your {account_display}, "
            f"find {ticker}, tap 'Sell', set 'Stop' order at ${stop_loss_price:.2f}"
        )
    return steps


# ─────────────────────────────────────────────────────────────────────────────
#  CLI display helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_pick(pick: Pick) -> None:
    """Print a pick summary to stdout using the new as_cli_block()."""
    print(pick.as_cli_block())


def _print_deep_dive(dd: DeepDive) -> None:
    """Print a deep dive summary to stdout."""
    upside = (
        ((dd.base_price_target - dd.current_price) / dd.current_price * 100)
        if dd.current_price > 0
        else 0
    )
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


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """CLI entry point: python -m research.stock_picker <query | --deep-dive TICKER>"""
    import argparse
    logging.basicConfig(
        level=logging.WARNING,
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
    parser.add_argument("--telegram", action="store_true", help="Output Telegram-formatted messages")
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
    elif args.telegram:
        for pick in picks:
            print(pick.as_telegram_message())
            print()
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
