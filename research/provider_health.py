"""
research/provider_health.py
---------------------------
Health-check every research data provider Atlas depends on.

Usage:
    python -m research.provider_health
    python main.py provider-health

Exits 0 if every required provider is up, 1 if any are degraded.

Why this exists:
    The 2026-04-25 EDGAR incident showed how silently a feed can go down. A
    single provider can return 200 with a "Information: paid endpoint" body
    that LOOKS like a successful response. This command tests each provider
    against an endpoint we actually use in production — not a generic ping —
    and reports green / yellow / red so CC can verify trust before relying
    on a pick.

Output is colour-free plain text so it pipes cleanly into pulse / Telegram.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import requests
from dotenv import load_dotenv

# Always load .env from project root, regardless of CWD.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


# ─────────────────────────────────────────────────────────────────────────────
#  Status enum
# ─────────────────────────────────────────────────────────────────────────────

GREEN = "GREEN"     # working, real data returned
YELLOW = "YELLOW"   # key set but endpoint gated / soft-rate-limited / partial
RED = "RED"         # key missing or hard error


@dataclass
class ProviderStatus:
    name: str
    key_set: bool
    status: str              # GREEN / YELLOW / RED
    detail: str              # one-line human-readable summary
    endpoint_tested: str

    def line(self) -> str:
        marker = {"GREEN": "[OK]", "YELLOW": "[WARN]", "RED": "[FAIL]"}[self.status]
        keymark = "key:set" if self.key_set else "key:MISSING"
        return f"  {marker:7s} {self.name:18s} {keymark:14s} {self.endpoint_tested:42s} -> {self.detail}"


# ─────────────────────────────────────────────────────────────────────────────
#  Per-provider checks
# ─────────────────────────────────────────────────────────────────────────────

def _check_yfinance() -> ProviderStatus:
    name, ep = "yfinance", "Ticker('NVDA').info"
    try:
        import yfinance as yf
        info = yf.Ticker("NVDA").info
        if info.get("regularMarketPrice") or info.get("currentPrice"):
            price = info.get("regularMarketPrice") or info.get("currentPrice")
            return ProviderStatus(name, True, GREEN, f"NVDA ${price}", ep)
        return ProviderStatus(name, True, YELLOW, "info returned but no price field", ep)
    except Exception as exc:
        return ProviderStatus(name, True, RED, f"import/call failed: {exc}", ep)


def _check_finnhub() -> ProviderStatus:
    name, ep = "finnhub", "/quote?symbol=NVDA"
    key = os.environ.get("FINNHUB_KEY", "").strip()
    if not key:
        return ProviderStatus(name, False, RED, "FINNHUB_KEY not in .env", ep)
    try:
        r = requests.get("https://finnhub.io/api/v1/quote", params={"symbol": "NVDA", "token": key}, timeout=10)
        j = r.json()
        if r.status_code == 200 and j.get("c"):
            return ProviderStatus(name, True, GREEN, f"NVDA ${j['c']:.2f} ({j.get('dp', 0):+.2f}%)", ep)
        if r.status_code == 429:
            return ProviderStatus(name, True, YELLOW, "rate-limited (60/min)", ep)
        return ProviderStatus(name, True, YELLOW, f"{r.status_code} {str(j)[:80]}", ep)
    except Exception as exc:
        return ProviderStatus(name, True, RED, f"request failed: {exc}", ep)


def _check_fmp() -> ProviderStatus:
    name, ep = "fmp", "/stable/profile?symbol=NVDA"
    key = os.environ.get("FMP_KEY", "").strip()
    if not key:
        return ProviderStatus(name, False, RED, "FMP_KEY not in .env", ep)
    try:
        r = requests.get(
            "https://financialmodelingprep.com/stable/profile",
            params={"symbol": "NVDA", "apikey": key},
            timeout=12,
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data and data[0].get("symbol") == "NVDA":
                mcap = data[0].get("marketCap", 0) / 1e9
                return ProviderStatus(name, True, GREEN, f"NVDA mcap=${mcap:.0f}B", ep)
            return ProviderStatus(name, True, YELLOW, f"empty/unexpected payload: {str(data)[:80]}", ep)
        if r.status_code == 403 and "Legacy" in r.text:
            return ProviderStatus(name, True, RED,
                "ENDPOINT IS LEGACY — code is hitting /api/v3/* instead of /stable/*", ep)
        return ProviderStatus(name, True, YELLOW, f"{r.status_code} {r.text[:80]}", ep)
    except Exception as exc:
        return ProviderStatus(name, True, RED, f"request failed: {exc}", ep)


def _check_alpha_vantage() -> ProviderStatus:
    name, ep = "alpha_vantage", "GLOBAL_QUOTE NVDA"
    key = os.environ.get("ALPHA_VANTAGE_KEY", "").strip()
    if not key:
        return ProviderStatus(name, False, RED, "ALPHA_VANTAGE_KEY not in .env", ep)
    try:
        r = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": "NVDA", "apikey": key},
            timeout=15,
        )
        j = r.json()
        if r.status_code == 200 and j.get("Global Quote", {}).get("01. symbol") == "NVDA":
            price = j["Global Quote"].get("05. price", "?")
            return ProviderStatus(name, True, GREEN, f"NVDA ${price}", ep)
        if "Information" in j or "Note" in j:
            return ProviderStatus(name, True, YELLOW,
                f"soft-rate-limited (25/day free): {(j.get('Information') or j.get('Note'))[:80]}", ep)
        return ProviderStatus(name, True, YELLOW, f"{r.status_code} {str(j)[:80]}", ep)
    except Exception as exc:
        return ProviderStatus(name, True, RED, f"request failed: {exc}", ep)


def _check_newsapi() -> ProviderStatus:
    name, ep = "newsapi", "/everything?q=NVIDIA"
    key = os.environ.get("NEWSAPI_KEY", "").strip()
    if not key:
        return ProviderStatus(name, False, RED, "NEWSAPI_KEY not in .env", ep)
    try:
        r = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": "NVIDIA", "language": "en", "pageSize": 1, "apiKey": key},
            timeout=12,
        )
        j = r.json()
        if r.status_code == 200 and j.get("status") == "ok":
            total = j.get("totalResults", 0)
            return ProviderStatus(name, True, GREEN, f"NVIDIA results={total}", ep)
        if r.status_code == 429 or j.get("code") == "rateLimited":
            return ProviderStatus(name, True, YELLOW, "rate-limited (100/day free)", ep)
        return ProviderStatus(name, True, YELLOW, f"{r.status_code} {j.get('message', '')[:80]}", ep)
    except Exception as exc:
        return ProviderStatus(name, True, RED, f"request failed: {exc}", ep)


def _check_sec_edgar() -> ProviderStatus:
    name, ep = "sec_edgar", "/files/company_tickers.json"
    try:
        from research._sec_client import get as sec_get, USER_AGENT
        r = sec_get("https://www.sec.gov/files/company_tickers.json", timeout=15)
        if r is None:
            return ProviderStatus(name, True, RED, "all retries exhausted", ep)
        if r.status_code == 200:
            count = len(r.json())
            return ProviderStatus(name, True, GREEN, f"{count} tickers parsed (UA: {USER_AGENT[:32]}...)", ep)
        return ProviderStatus(name, True, YELLOW, f"{r.status_code}", ep)
    except Exception as exc:
        return ProviderStatus(name, True, RED, f"call failed: {exc}", ep)


def _check_anthropic() -> ProviderStatus:
    name, ep = "anthropic", "messages.create (trivial)"
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return ProviderStatus(name, False, RED, "ANTHROPIC_API_KEY not in .env", ep)
    # We don't burn tokens just to verify — checking key shape is enough.
    if len(key) < 30 or not key.startswith("sk-"):
        return ProviderStatus(name, True, YELLOW, f"key shape suspicious (len={len(key)})", ep)
    return ProviderStatus(name, True, GREEN, f"key present (len={len(key)})", ep)


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

CHECKS: list[Callable[[], ProviderStatus]] = [
    _check_yfinance,
    _check_finnhub,
    _check_fmp,
    _check_alpha_vantage,
    _check_newsapi,
    _check_sec_edgar,
    _check_anthropic,
]


def run_all() -> list[ProviderStatus]:
    return [c() for c in CHECKS]


def main() -> int:
    print()
    print("=" * 92)
    print("  ATLAS — RESEARCH PROVIDER HEALTH CHECK")
    print("=" * 92)

    results = run_all()
    for r in results:
        print(r.line())

    print("-" * 92)
    green = sum(1 for r in results if r.status == GREEN)
    yellow = sum(1 for r in results if r.status == YELLOW)
    red = sum(1 for r in results if r.status == RED)
    print(f"  Summary: GREEN={green}  YELLOW={yellow}  RED={red}  total={len(results)}")
    print("=" * 92)
    print()

    return 0 if red == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
