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
    ("donchian_breakout", "DOT/USDT"):  "daredevil",    # +5.83% — best performer
    ("donchian_breakout", "XRP/USDT"):  "aggressive",   # +4.70%
    ("donchian_breakout", "SOL/USDT"):  "aggressive",   # +2.76%
    ("donchian_breakout", "ETH/USDT"):  "conservative", # +2.04%
    ("donchian_breakout", "ADA/USDT"):  "conservative", # +0.72%
    # ── smart_money ───────────────────────────────────────────────────────
    ("smart_money", "DOGE/USDT"):  "aggressive",   # +3.41%, WR 85.7%, Sharpe 2.41
    ("smart_money", "XRP/USDT"):   "conservative", # +2.16%
    ("smart_money", "ETH/USDT"):   "conservative", # +2.08%
    ("smart_money", "SOL/USDT"):   "conservative", # +1.29%
    ("smart_money", "AVAX/USDT"):  "conservative", # +0.73%
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
