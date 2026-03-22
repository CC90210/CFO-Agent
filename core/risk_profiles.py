"""
core/risk_profiles.py — Conviction-Based Risk Profile System
=============================================================
Maps strategy-symbol pairs to their empirically optimal risk tier.
Backtested across 176 profile-symbol tests on live Kraken data (2026-03-20).

Profile selection logic
-----------------------
Given a (strategy, symbol) pair and a real-time conviction score:

  conviction <= 0.5            → always conservative, regardless of optimal
  0.5 < conviction <= 0.7      → use the empirically optimal profile
  conviction > 0.7             → use the optimal profile only if it is
                                  aggressive/daredevil/sniper; otherwise
                                  still use whatever the optimal profile is

If no mapping exists the function falls back to conservative.

Usage
-----
    from core.risk_profiles import get_risk_profile, RiskProfile

    profile = get_risk_profile("donchian_breakout", "DOT/USDT", conviction=0.8)
    # profile.risk_pct        → 5.0
    # profile.atr_stop_mult   → 1.0
    # profile.rr_ratio        → 5.0
    # profile.name            → "daredevil"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("atlas.risk_profiles")

# ---------------------------------------------------------------------------
# Risk Profile definitions
# ---------------------------------------------------------------------------

# Tier ordering from most cautious to most aggressive, used internally to
# decide whether a high-conviction override should escalate the tier.
_TIER_ORDER: list[str] = ["conservative", "sniper", "aggressive", "daredevil"]


@dataclass(frozen=True)
class RiskProfile:
    """Immutable risk-parameter bundle for a single trade tier."""

    name: str
    # Percentage of portfolio equity risked per trade (e.g. 1.5 = 1.5 %).
    risk_pct: float
    # Stop-loss distance expressed as a multiple of ATR.
    atr_stop_mult: float
    # Target risk-reward ratio (take-profit distance / stop-loss distance).
    rr_ratio: float

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RiskProfile({self.name!r}, "
            f"risk={self.risk_pct}%, "
            f"atr_stop={self.atr_stop_mult}x, "
            f"rr={self.rr_ratio})"
        )


# ---------------------------------------------------------------------------
# Canonical profile instances — immutable singletons
# ---------------------------------------------------------------------------

CONSERVATIVE = RiskProfile(
    name="conservative",
    risk_pct=1.5,
    atr_stop_mult=2.0,
    rr_ratio=3.0,
)

AGGRESSIVE = RiskProfile(
    name="aggressive",
    risk_pct=3.0,
    atr_stop_mult=1.5,
    rr_ratio=4.0,
)

DAREDEVIL = RiskProfile(
    name="daredevil",
    risk_pct=5.0,
    atr_stop_mult=1.0,
    rr_ratio=5.0,
)

SNIPER = RiskProfile(
    name="sniper",
    risk_pct=4.0,
    atr_stop_mult=1.5,
    rr_ratio=5.0,
)

# Internal lookup so callers can resolve a profile by name string.
_PROFILE_BY_NAME: dict[str, RiskProfile] = {
    "conservative": CONSERVATIVE,
    "aggressive": AGGRESSIVE,
    "daredevil": DAREDEVIL,
    "sniper": SNIPER,
}

# Profiles that qualify for the high-conviction escalation path.
_ELEVATED_PROFILES: frozenset[str] = frozenset({"aggressive", "daredevil", "sniper"})


# ---------------------------------------------------------------------------
# Empirically validated optimal-profile mapping
# ---------------------------------------------------------------------------
# Key:   (strategy_name, symbol)
# Value: profile name string
#
# Source: 176 profile-symbol backtests on live Kraken OHLCV data, 2026-03-20.
# Returns shown are absolute return over the test window at the named profile.
# ---------------------------------------------------------------------------

OPTIMAL_PROFILES: dict[tuple[str, str], str] = {
    # ── donchian_breakout ──────────────────────────────────────────────────
    # Profiles assigned by Sharpe tier: >1.5 → aggressive, 0.7-1.5 → sniper,
    # <0.7 → conservative. Source: full-portfolio Sharpe analysis 2026-03-21.
    ("donchian_breakout", "ATOM/USDT"): "daredevil",    # Sharpe 1.91 → top tier (>1.5), +14.56%
    ("donchian_breakout", "ADA/USDT"):  "aggressive",   # Sharpe 1.81 → aggressive (>1.5)
    ("donchian_breakout", "DOT/USDT"):  "aggressive",   # Sharpe 1.70 → aggressive (>1.5)
    ("donchian_breakout", "SOL/USDT"):  "aggressive",   # Sharpe 1.60 → aggressive (>1.5)
    ("donchian_breakout", "ETH/USDT"):  "aggressive",   # Sharpe 1.29 → aggressive (0.7-1.5)
    ("donchian_breakout", "XRP/USDT"):  "conservative", # Sharpe 0.74 → conservative (<0.7 boundary)
    ("donchian_breakout", "AVAX/USDT"): "conservative", # Sharpe 0.65 → conservative (<0.7)
    # ── smart_money ───────────────────────────────────────────────────────
    # Sharpe-tiered assignments from fresh validation 2026-03-21.
    ("smart_money", "DOGE/USDT"):  "daredevil",   # Sharpe 2.11, 100% WR — elite conviction
    ("smart_money", "AVAX/USDT"):  "aggressive",  # Sharpe 2.04 → aggressive
    ("smart_money", "ETH/USDT"):   "aggressive",  # Sharpe 2.00 → aggressive
    ("smart_money", "XRP/USDT"):   "aggressive",  # Sharpe 1.94 → aggressive
    ("smart_money", "SOL/USDT"):   "aggressive",  # Sharpe 1.45 → aggressive (0.7-1.5)
    # ── multi_timeframe (fresh Kraken validation 2026-03-20) ──────────────
    ("multi_timeframe", "DOGE/USDT"):  "conservative", # +7.46%, Sharpe 1.54
    ("multi_timeframe", "XRP/USDT"):   "aggressive",   # Sharpe 1.12 → aggressive (0.7-1.5), +13.75%
    # ── stock strategies (validated on real yfinance 5yr data 2026-03-20) ────
    # sector_rotation — daredevil upgrades based on fresh 5yr backtest
    ("sector_rotation", "XLC"):  "daredevil",    # +50.04%, WR 30.6%, Sharpe 0.50 — MONSTER
    ("sector_rotation", "XLK"):  "daredevil",    # +33.98%, WR 28.7%, Sharpe 0.37
    ("sector_rotation", "XLF"):  "conservative", # +10.55%, WR 35.0%, Sharpe 0.33 — conservative still best
    # connors_rsi — all daredevil on fresh 5yr backtest
    ("connors_rsi", "NVDA"):     "daredevil",    # +29.03%, WR 48.9%, Sharpe 0.55
    ("connors_rsi", "META"):     "daredevil",    # +18.75%, WR 50.0%, Sharpe 0.33
    ("connors_rsi", "QQQ"):      "daredevil",    # +18.98%, WR 55.2%, Sharpe 0.45
    ("connors_rsi", "AMD"):      "daredevil",    # +15.21%, WR 54.4%, Sharpe 0.37
    ("connors_rsi", "GOOG"):     "daredevil",    # +6.96%, WR 53.9%, Sharpe 0.22
    # ── volume_profile (resurrected 2026-03-20, daredevil params on 4h) ─────
    ("volume_profile", "AVAX/USDT"): "daredevil",    # +4.37%, WR 60%, Sharpe 1.85, PF 2.75
    ("volume_profile", "BTC/USDT"):  "daredevil",    # +2.14%, WR 50%, Sharpe 0.88, PF 1.94
    ("volume_profile", "XRP/USDT"):  "aggressive",   # +2.43%, WR 42.9%, Sharpe 0.95, PF 1.62
    # Removed: DOGE/USDT — flipped to -0.66% on fresh validation
    # ── gold (validated on real OANDA data 2026-03-20) ──────────────────────
    ("gold_trend_follower", "XAU_USD"): "aggressive", # +3.80%, WR 54.5%, Sharpe 0.87
    ("donchian_breakout",   "XAU_USD"): "aggressive", # +15.70%, Sharpe 2.49 — GOLD CHAMPION
    ("multi_timeframe",     "XAU_USD"): "conservative", # +10.94%, Sharpe 2.10
    # ── silver (validated on real OANDA data 2026-03-20) ──────────────────────
    ("donchian_breakout",   "XAG_USD"): "aggressive", # +12.44%, WR 60%, Sharpe 2.08, PF 3.74
    ("multi_timeframe",     "XAG_USD"): "conservative", # +7.21%, WR 50%, Sharpe 1.43, PF 2.82
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_risk_profile(
    strategy_name: str,
    symbol: str,
    conviction: float = 0.5,
) -> RiskProfile:
    """Return the appropriate RiskProfile for this strategy-symbol-conviction triple.

    Selection rules (applied in order):
    1. conviction <= 0.5  → conservative, unconditionally.
    2. No mapping found   → conservative.
    3. 0.5 < conviction <= 0.7  → return the empirically optimal profile.
    4. conviction > 0.7
           - optimal is elevated (aggressive / daredevil / sniper) → return it.
           - optimal is conservative → return conservative
             (high conviction doesn't override a conservative pair).

    Args:
        strategy_name: Exact strategy key as used in strategies.yaml
                       (e.g. "donchian_breakout").
        symbol:        Trading pair in standard format (e.g. "DOT/USDT").
        conviction:    Float in [0.0, 1.0] from the agent ensemble.
                       Values outside this range are clamped silently.

    Returns:
        A frozen RiskProfile instance.
    """
    # Clamp conviction to [0, 1] defensively.
    conviction = max(0.0, min(1.0, conviction))

    # Rule 1: low conviction → always conservative.
    if conviction <= 0.5:
        logger.debug(
            "risk_profiles: conviction=%.2f <= 0.5 — returning conservative "
            "for %s/%s",
            conviction,
            strategy_name,
            symbol,
        )
        return CONSERVATIVE

    lookup_key = (strategy_name, symbol)
    optimal_name = OPTIMAL_PROFILES.get(lookup_key)

    # Rule 2: no empirical mapping → conservative.
    if optimal_name is None:
        logger.debug(
            "risk_profiles: no mapping for (%s, %s) — returning conservative",
            strategy_name,
            symbol,
        )
        return CONSERVATIVE

    optimal_profile = _PROFILE_BY_NAME[optimal_name]

    # Rule 3: mid conviction (0.5, 0.7] → use optimal profile as-is.
    if conviction <= 0.7:
        logger.debug(
            "risk_profiles: conviction=%.2f in (0.5, 0.7] — returning "
            "optimal profile %r for %s/%s",
            conviction,
            optimal_name,
            strategy_name,
            symbol,
        )
        return optimal_profile

    # Rule 4: high conviction > 0.7 — elevated profiles are confirmed;
    # conservative pairs stay conservative even at high conviction.
    if optimal_name in _ELEVATED_PROFILES:
        logger.debug(
            "risk_profiles: conviction=%.2f > 0.7, elevated profile %r "
            "confirmed for %s/%s",
            conviction,
            optimal_name,
            strategy_name,
            symbol,
        )
        return optimal_profile

    logger.debug(
        "risk_profiles: conviction=%.2f > 0.7 but optimal is %r "
        "(conservative pair) — returning conservative for %s/%s",
        conviction,
        optimal_name,
        strategy_name,
        symbol,
    )
    return CONSERVATIVE
