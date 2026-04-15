"""
research/macro_watch.py
-----------------------
Macro environment awareness for Atlas Research.

Provides:
- geopolitical_flashpoints(): current geopolitical risk watch list with sector impact maps
- sector_map(): sector-to-representative-ticker mapping for rotation plays
- rotation_signal(): heuristic sector rotation signal from a batch of NewsItems

Atlas uses this to overlay macro context onto every stock pick — because the
right stock in the wrong macro environment is still the wrong trade.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from research.news_ingest import NewsItem

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Geopolitical flashpoints
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Flashpoint:
    """A geopolitical risk event with downstream sector impact mapping."""

    name: str
    description: str
    status: str  # "active" | "monitoring" | "resolved"
    escalation_triggers: list[str]  # keywords that signal escalation in news
    sector_impacts: dict[str, str]  # sector -> "bullish" | "bearish" | "neutral"
    related_tickers: list[str]  # direct-impact tickers to watch


_FLASHPOINTS: list[Flashpoint] = [
    Flashpoint(
        name="US-China Trade War / Tech Decoupling",
        description=(
            "Ongoing tariff escalation, semiconductor export controls (CHIPS Act enforcement), "
            "and strategic decoupling in AI/semiconductor supply chains. Taiwan risk amplifies."
        ),
        status="active",
        escalation_triggers=[
            "tariff", "export control", "semiconductor ban", "chip restriction",
            "huawei", "TSMC", "Taiwan", "de-risking", "supply chain",
        ],
        sector_impacts={
            "semiconductors": "bearish",   # supply chain disruption, margin compression
            "defense": "bullish",          # military tech spending increases
            "AI_infrastructure": "mixed",  # US benefit, China risk
            "chinese_tech": "bearish",     # direct target
            "domestic_manufacturing": "bullish",  # reshoring narrative
            "energy": "neutral",
        },
        related_tickers=["NVDA", "AMD", "INTC", "AMAT", "LRCX", "TSM", "BABA", "JD", "PDD"],
    ),
    Flashpoint(
        name="Middle East Oil Supply Risk",
        description=(
            "Iran-Israel tensions, Houthi Red Sea disruptions, Saudi OPEC+ production decisions. "
            "Any strike on Iranian oil infrastructure or Strait of Hormuz closure spikes Brent 15-30%."
        ),
        status="active",
        escalation_triggers=[
            "Iran", "Israel", "Houthi", "Red Sea", "Strait of Hormuz",
            "OPEC cut", "oil embargo", "Saudi Arabia", "tanker attack",
        ],
        sector_impacts={
            "energy": "bullish",
            "defense": "bullish",
            "airlines": "bearish",
            "transportation": "bearish",
            "consumer_discretionary": "bearish",  # gas prices hit wallets
            "precious_metals": "bullish",          # safe haven
            "utilities": "neutral",
        },
        related_tickers=["XOM", "CVX", "COP", "OXY", "SLB", "LMT", "RTX", "NOC", "GD", "GLD"],
    ),
    Flashpoint(
        name="Russia-Ukraine War / European Energy",
        description=(
            "Prolonged conflict sustaining European defense spending surge, energy independence push, "
            "and grain/fertilizer price volatility. NATO expansion reshaping defense budgets."
        ),
        status="active",
        escalation_triggers=[
            "Russia", "Ukraine", "NATO", "Zelensky", "Putin", "sanctions",
            "energy embargo", "natural gas", "grain corridor", "cease-fire",
        ],
        sector_impacts={
            "defense": "bullish",
            "energy": "bullish",       # European LNG demand
            "agriculture": "bullish",  # food supply concerns
            "uranium": "bullish",      # European nuclear pivot
            "cybersecurity": "bullish",  # state-sponsored cyber attacks
            "european_equities": "bearish",
        },
        related_tickers=["LMT", "RTX", "NOC", "CCJ", "UEC", "ENPH", "PERI", "GLD", "CF", "MOS"],
    ),
    Flashpoint(
        name="Taiwan Strait / TSMC Concentration Risk",
        description=(
            "Taiwan produces ~90% of leading-edge chips. Any PRC military action disrupts global "
            "semiconductor supply for 2-3 years minimum. Probability low, impact catastrophic."
        ),
        status="monitoring",
        escalation_triggers=[
            "Taiwan", "PLA", "strait", "blockade", "TSMC", "invasion",
            "military exercise", "Xi Jinping", "reunification", "One China",
        ],
        sector_impacts={
            "semiconductors": "catastrophic_bearish",
            "tech_hardware": "bearish",
            "defense": "extreme_bullish",
            "US_domestic_semis": "bullish",  # Intel, Samsung domestic fabs
            "automotive": "bearish",         # chips in every car
            "AI_infrastructure": "bearish",
        },
        related_tickers=["TSM", "NVDA", "AMD", "INTC", "AMAT", "ASML", "QCOM", "AVGO", "LMT"],
    ),
    Flashpoint(
        name="Fed Rate Policy / Inflation Regime",
        description=(
            "Fed dot plot, CPI trajectory, and unemployment rate drive equity valuation multiples. "
            "Rate cuts bullish for growth/tech/small-cap. Sticky inflation = higher-for-longer pain."
        ),
        status="active",
        escalation_triggers=[
            "CPI", "inflation", "Fed", "rate cut", "rate hike", "FOMC",
            "dot plot", "Powell", "employment", "recession", "stagflation",
        ],
        sector_impacts={
            "growth_tech": "rate_sensitive_bullish",  # benefits from cuts
            "financials": "mixed",       # higher rates = NIM; slower cuts = relief
            "real_estate": "bullish",    # rate cuts drive homebuying
            "small_cap": "bullish",      # small caps outperform in cut cycles
            "consumer_staples": "defensive_hold",
            "precious_metals": "bullish",  # real rates falling = gold up
            "utilities": "bullish",        # rate-sensitive dividend plays
        },
        related_tickers=["GLD", "TLT", "IWM", "XLF", "XLU", "XLRE", "QQQ", "SPY"],
    ),
    Flashpoint(
        name="AI Infrastructure Arms Race",
        description=(
            "Hyperscaler capex ($200B+ in 2025) driving sustained demand for GPUs, power, "
            "cooling, data centers. Potential overcapacity in 2026 is the bear case. "
            "Sovereign AI (every government wants its own) is the bull extension."
        ),
        status="active",
        escalation_triggers=[
            "AI", "GPU", "data center", "capex", "Microsoft", "OpenAI", "Google",
            "Meta AI", "sovereign AI", "nuclear power", "power demand", "NVIDIA",
        ],
        sector_impacts={
            "AI_infrastructure": "bullish",
            "semiconductors": "bullish",
            "energy": "bullish",        # data centers consume massive power
            "nuclear": "bullish",       # Microsoft/Google buying nuclear
            "copper": "bullish",        # AI infrastructure is copper-intensive
            "traditional_software": "bearish",  # disruption risk
        },
        related_tickers=["NVDA", "AMD", "AVGO", "MSFT", "GOOGL", "META", "CEG", "VST", "SMCI", "ARM"],
    ),
    Flashpoint(
        name="US Political Cycle / Election Aftermath",
        description=(
            "Trump tariffs, deregulation push, potential IRA rollback affecting clean energy, "
            "and 'America First' reshoring policy. Defense, energy, financials benefit; "
            "clean energy, EV, multinational trade at risk."
        ),
        status="active",
        escalation_triggers=[
            "tariff", "Trump", "deregulation", "IRA rollback", "clean energy",
            "border", "fiscal deficit", "debt ceiling", "DOGE", "government shutdown",
        ],
        sector_impacts={
            "defense": "bullish",
            "traditional_energy": "bullish",
            "financials": "bullish",        # deregulation narrative
            "clean_energy": "bearish",      # IRA uncertainty
            "EVs": "bearish",               # reduced incentives
            "big_tech": "mixed",            # antitrust vs. deregulation
            "healthcare": "defensive",
        },
        related_tickers=["XOM", "CVX", "JPM", "GS", "LMT", "RTX", "ENPH", "PLUG", "TSLA", "AMZN"],
    ),
]


def geopolitical_flashpoints() -> list[Flashpoint]:
    """Return the current geopolitical risk watch list."""
    return [fp for fp in _FLASHPOINTS if fp.status != "resolved"]


# ─────────────────────────────────────────────────────────────────────────────
#  Sector map (sector name → representative ETF + top tickers)
# ─────────────────────────────────────────────────────────────────────────────

def sector_map() -> dict[str, dict]:
    """
    Return a sector-to-ticker mapping for rotation plays.

    Each sector entry has:
    - etf: liquid sector ETF for quick rotation
    - top_tickers: highest-conviction individual names
    - macro_tailwinds: current thesis for why this sector might outperform
    - macro_headwinds: current risks to the sector
    """
    return {
        "AI_infrastructure": {
            "etf": "BOTZ",
            "top_tickers": ["NVDA", "AMD", "AVGO", "MSFT", "GOOGL", "META", "SMCI", "ARM"],
            "macro_tailwinds": "Hyperscaler capex supercycle, sovereign AI demand, GPU scarcity",
            "macro_headwinds": "Valuation stretch, potential overcapacity 2026, China export bans",
        },
        "semiconductors": {
            "etf": "SOXX",
            "top_tickers": ["NVDA", "AMD", "TSM", "AMAT", "LRCX", "ASML", "QCOM", "AVGO"],
            "macro_tailwinds": "AI demand, automotive chips, industrial IoT",
            "macro_headwinds": "US-China decoupling, Taiwan risk, inventory cycles",
        },
        "defense": {
            "etf": "ITA",
            "top_tickers": ["LMT", "RTX", "NOC", "GD", "L3Harris", "HII", "LDOS"],
            "macro_tailwinds": "NATO 2% GDP targets, Ukraine conflict, Taiwan risk, drone warfare",
            "macro_headwinds": "Budget reconciliation, DOGE defense cuts",
        },
        "cybersecurity": {
            "etf": "CIBR",
            "top_tickers": ["CRWD", "PANW", "ZS", "FTNT", "S", "OKTA", "CYBR"],
            "macro_tailwinds": "State-sponsored attacks, AI-powered threats, compliance mandates",
            "macro_headwinds": "Platform consolidation compressing smaller players",
        },
        "energy": {
            "etf": "XLE",
            "top_tickers": ["XOM", "CVX", "COP", "OXY", "SLB", "EOG", "PSX"],
            "macro_tailwinds": "Middle East risk premium, data center power demand, OPEC discipline",
            "macro_headwinds": "Energy transition, Biden-era supply increases, demand slowdown",
        },
        "uranium_nuclear": {
            "etf": "URA",
            "top_tickers": ["CCJ", "UEC", "NXE", "DNN", "LEU", "CEG", "VST"],
            "macro_tailwinds": "AI power demand, European nuclear revival, SMR buildout",
            "macro_headwinds": "Long permitting cycles, public opposition, capex overruns",
        },
        "precious_metals": {
            "etf": "GLD",
            "top_tickers": ["GLD", "SLV", "NEM", "AEM", "GOLD", "WPM", "FNV"],
            "macro_tailwinds": "Falling real rates, central bank buying, geopolitical safe haven",
            "macro_headwinds": "Dollar strength, rate cut delays",
        },
        "biotech": {
            "etf": "XBI",
            "top_tickers": ["MRNA", "REGN", "VRTX", "BIIB", "GILD", "ABBV", "LLY"],
            "macro_tailwinds": "GLP-1 obesity drug supercycle, AI drug discovery, aging demographics",
            "macro_headwinds": "FDA uncertainty, patent cliffs, drug pricing legislation",
        },
        "financials": {
            "etf": "XLF",
            "top_tickers": ["JPM", "BAC", "GS", "MS", "V", "MA", "BLK"],
            "macro_tailwinds": "Deregulation, M&A revival, NIM expansion in higher-rate env",
            "macro_headwinds": "Credit losses, commercial real estate exposure, rate uncertainty",
        },
        "chinese_tech": {
            "etf": "KWEB",
            "top_tickers": ["BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI"],
            "macro_tailwinds": "Cheap valuations, stimulus potential, domestic AI push",
            "macro_headwinds": "US-China tensions, delisting risk, regulatory crackdowns",
        },
        "emerging_markets": {
            "etf": "EEM",
            "top_tickers": ["EEM", "VWO", "INDA", "EWZ", "TAN", "GXC"],
            "macro_tailwinds": "Dollar weakness, commodity supercycle, India growth story",
            "macro_headwinds": "Fed tightening, China slowdown, political instability",
        },
        "consumer_staples": {
            "etf": "XLP",
            "top_tickers": ["PG", "KO", "PEP", "COST", "WMT", "MCD", "MDLZ"],
            "macro_tailwinds": "Recession hedge, dividend income in rate-cut environment",
            "macro_headwinds": "Consumer spending recovery reducing defensive appeal",
        },
        "real_estate": {
            "etf": "XLRE",
            "top_tickers": ["AMT", "PLD", "EQIX", "O", "SPG", "DLR", "VICI"],
            "macro_tailwinds": "Rate cuts, data center REITs (EQIX, DLR) riding AI buildout",
            "macro_headwinds": "Commercial real estate stress, office vacancy rates",
        },
        "clean_energy": {
            "etf": "ICLN",
            "top_tickers": ["ENPH", "SEDG", "FSLR", "NEE", "PLUG", "BE", "RIVN"],
            "macro_tailwinds": "Long-term energy transition, utility-scale solar economics",
            "macro_headwinds": "IRA rollback risk, interest rate sensitivity, competition from China",
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Rotation signal from news
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RotationSignal:
    """Output of rotation_signal() — sector-level conviction scores from news."""

    sector: str
    direction: str  # "overweight" | "underweight" | "neutral"
    score: float    # positive = bullish pressure, negative = bearish pressure
    triggered_by: list[str]  # flashpoint names that fired
    supporting_headlines: list[str]


def rotation_signal(news: list[NewsItem]) -> dict[str, RotationSignal]:
    """
    Analyze recent news against geopolitical flashpoints and produce
    sector rotation signals.

    Algorithm:
    1. For each flashpoint, count how many news headlines match its
       escalation_triggers (case-insensitive keyword match).
    2. Score each sector based on its impact in matching flashpoints,
       weighted by the hit count for that flashpoint.
    3. Return a dict of sector -> RotationSignal.

    This is a keyword heuristic — not an ML model. It surfaces macro
    themes for Claude to reason about, not final recommendations.
    """
    flashpoints = geopolitical_flashpoints()

    # sector_name -> {"score": float, "triggered_by": set, "headlines": list}
    sector_scores: dict[str, dict] = {}

    for fp in flashpoints:
        trigger_hits = 0
        matched_headlines: list[str] = []

        for item in news:
            text = f"{item.title} {item.summary}".lower()
            hits = sum(1 for kw in fp.escalation_triggers if kw.lower() in text)
            if hits > 0:
                trigger_hits += hits
                matched_headlines.append(item.title[:100])

        if trigger_hits == 0:
            continue

        for sector, impact in fp.sector_impacts.items():
            if sector not in sector_scores:
                sector_scores[sector] = {
                    "score": 0.0,
                    "triggered_by": set(),
                    "headlines": [],
                }

            # Map impact words to numeric signal
            impact_lower = impact.lower()
            if "extreme_bullish" in impact_lower or "catastrophic_bullish" in impact_lower:
                delta = 3.0
            elif "bullish" in impact_lower:
                delta = 1.0
            elif "extreme_bearish" in impact_lower or "catastrophic_bearish" in impact_lower:
                delta = -3.0
            elif "bearish" in impact_lower:
                delta = -1.0
            else:
                delta = 0.0

            sector_scores[sector]["score"] += delta * (trigger_hits / 5.0)  # normalize
            sector_scores[sector]["triggered_by"].add(fp.name)
            sector_scores[sector]["headlines"].extend(matched_headlines[:2])

    results: dict[str, RotationSignal] = {}
    for sector, data in sector_scores.items():
        score = round(data["score"], 2)
        if score > 0.5:
            direction = "overweight"
        elif score < -0.5:
            direction = "underweight"
        else:
            direction = "neutral"

        results[sector] = RotationSignal(
            sector=sector,
            direction=direction,
            score=score,
            triggered_by=list(data["triggered_by"]),
            supporting_headlines=list(dict.fromkeys(data["headlines"]))[:5],
        )

    return results


def macro_context_summary(news: list[NewsItem]) -> str:
    """
    Return a plain-text macro context summary suitable for injection into
    Claude prompts. Combines active flashpoints with rotation signals from
    the provided news batch.
    """
    lines: list[str] = ["## Current Macro Context\n"]

    lines.append("### Active Geopolitical Flashpoints")
    for fp in geopolitical_flashpoints():
        lines.append(f"- **{fp.name}** ({fp.status.upper()}): {fp.description[:120]}...")

    if news:
        signals = rotation_signal(news)
        if signals:
            lines.append("\n### News-Driven Sector Rotation Signals (last 14 days)")
            sorted_signals = sorted(signals.values(), key=lambda x: abs(x.score), reverse=True)
            for sig in sorted_signals[:8]:
                arrow = "OVERWEIGHT" if sig.direction == "overweight" else ("UNDERWEIGHT" if sig.direction == "underweight" else "NEUTRAL")
                lines.append(f"- **{sig.sector}**: {arrow} (score: {sig.score:+.2f}) — triggered by {', '.join(sig.triggered_by[:2])}")

    lines.append("\n### Sector Rotation Playbook")
    for sector, data in sector_map().items():
        lines.append(f"- **{sector}** (ETF: {data['etf']}): {data['macro_tailwinds'][:80]}")

    return "\n".join(lines)
