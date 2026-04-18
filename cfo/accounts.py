"""
CFO Net-Worth Aggregator — account balance fetchers.

Each platform function returns list[Balance].  Failures degrade gracefully:
missing keys → [] with a warning printed once.  Results are TTL-cached (5 min).
"""

from __future__ import annotations

import json
import logging
import os
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")

# ---------------------------------------------------------------------------
# Optional dependency imports — degrade gracefully if not installed
# ---------------------------------------------------------------------------
try:
    import ccxt  # type: ignore
    _HAS_CCXT = True
except ImportError:
    _HAS_CCXT = False
    warnings.warn("ccxt not installed — Kraken balances unavailable. Run: pip install ccxt")

try:
    from oandapyV20 import API as OandaAPI  # type: ignore
    import oandapyV20.endpoints.accounts as accounts_ep  # type: ignore
    _HAS_OANDA = True
except ImportError:
    _HAS_OANDA = False
    warnings.warn("oandapyV20 not installed — OANDA balances unavailable. Run: pip install oandapyV20")

try:
    import stripe as stripe_sdk  # type: ignore
    _HAS_STRIPE = True
except ImportError:
    _HAS_STRIPE = False
    warnings.warn("stripe not installed — Stripe balances unavailable. Run: pip install stripe")

try:
    import requests as _requests  # type: ignore
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False
    warnings.warn("requests not installed — Wise balances unavailable. Run: pip install requests")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Core dataclass
# ---------------------------------------------------------------------------

@dataclass
class Balance:
    platform: str
    account: str
    amount: float
    currency: str
    category: str   # "cash" | "crypto" | "equity" | "registered" | "business"
    as_of: datetime
    source: str     # "api" | "manual"
    notes: str = ""


# ---------------------------------------------------------------------------
# TTL cache — avoids hammering APIs on repeated calls within a session
# ---------------------------------------------------------------------------

_CACHE: dict[str, tuple[float, list[Balance]]] = {}
_CACHE_TTL = 300  # seconds (5 min)


def _cached(key: str, fn) -> list[Balance]:
    """Return cached result if fresh, otherwise call fn() and cache it."""
    entry = _CACHE.get(key)
    if entry and (time.monotonic() - entry[0]) < _CACHE_TTL:
        return entry[1]
    result = fn()
    _CACHE[key] = (time.monotonic(), result)
    return result


def _missing_key(platform: str, *var_names: str) -> bool:
    """Return True (and print a warning) if any env var is empty/missing."""
    missing = [v for v in var_names if not os.getenv(v, "").strip()]
    if missing:
        print(f"[accounts] skipping {platform} (no API key: {', '.join(missing)})")
        return True
    return False


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Default FX rates (fallback when live rates unavailable)
# ---------------------------------------------------------------------------

DEFAULT_FX: dict[str, float] = {
    "USD": 1.37,
    "EUR": 1.48,
    "GBP": 1.73,
    "CAD": 1.0,
}

_FX_CACHE: dict[str, tuple[float, dict[str, float]]] = {}
_FX_CACHE_TTL = 900  # 15 min


def get_fx_rates(base: str = "CAD") -> dict[str, float]:
    """
    Fetch live FX rates with CAD as base. Falls back to DEFAULT_FX on failure.

    Uses the free exchangerate.host API (no key required, 250 req/mo).
    Results are cached for 15 minutes.
    """
    entry = _FX_CACHE.get(base)
    if entry and (time.monotonic() - entry[0]) < _FX_CACHE_TTL:
        return entry[1]

    if not _HAS_REQUESTS:
        logger.warning("requests not installed — using hardcoded FX rates")
        return DEFAULT_FX

    try:
        resp = _requests.get(
            "https://api.exchangerate.host/latest",
            params={"base": base, "symbols": "USD,EUR,GBP,CAD"},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})
        # API returns how many USD per 1 CAD — we want how many CAD per 1 USD
        # So we invert: 1 / (rate of USD in CAD terms)
        fx: dict[str, float] = {"CAD": 1.0}
        for ccy in ("USD", "EUR", "GBP"):
            api_rate = rates.get(ccy)
            if api_rate and float(api_rate) > 0:
                fx[ccy] = round(1.0 / float(api_rate), 4)
            else:
                fx[ccy] = DEFAULT_FX.get(ccy, 1.0)
        _FX_CACHE[base] = (time.monotonic(), fx)
        logger.info("Live FX rates fetched: %s", fx)
        return fx
    except Exception as exc:  # noqa: BLE001
        logger.warning("FX rate fetch failed (%s) — using defaults", exc)
        return DEFAULT_FX


# ---------------------------------------------------------------------------
# Platform fetchers
# ---------------------------------------------------------------------------

def kraken_balances() -> list[Balance]:
    """Fetch live Kraken balances via ccxt. Returns per-asset Balance objects."""

    def _fetch() -> list[Balance]:
        if not _HAS_CCXT:
            return []
        if _missing_key("Kraken", "EXCHANGE_API_KEY", "EXCHANGE_SECRET"):
            return []

        try:
            exchange = ccxt.kraken({
                "apiKey": os.environ["EXCHANGE_API_KEY"],
                "secret": os.environ["EXCHANGE_SECRET"],
                "enableRateLimit": True,
            })

            raw: dict[str, float] = exchange.fetch_balance()["total"]
            balances: list[Balance] = []
            now = _now()

            # Normalise Kraken asset codes → standard tickers
            def _normalise(asset: str) -> str:
                # Kraken prefixes spot assets: XXBT → BTC, XETH → ETH, ZUSD → USD, etc.
                mapping = {
                    "XXBT": "BTC", "XBT": "BTC",
                    "XETH": "ETH",
                    "XLTC": "LTC",
                    "XXRP": "XRP",
                    "XXLM": "XLM",
                    "XDOGE": "DOGE",
                    "ZUSD": "USD",
                    "ZCAD": "CAD",
                    "ZEUR": "EUR",
                    "ZGBP": "GBP",
                }
                if asset in mapping:
                    return mapping[asset]
                # Generic 4-char X/Z prefix strip
                if len(asset) == 4 and asset[0] in ("X", "Z"):
                    return asset[1:]
                return asset

            # Fetch all tickers once to convert crypto → USD value
            tickers: dict[str, Any] = {}
            try:
                tickers = exchange.fetch_tickers()
            except Exception:
                pass

            def _usd_price(ticker: str) -> Optional[float]:
                """Return the USD price for a crypto asset, trying /USD and /USDT pairs."""
                for pair in (f"{ticker}/USD", f"{ticker}/USDT"):
                    t = tickers.get(pair)
                    if t and t.get("last"):
                        return float(t["last"])
                return None

            for asset, amount in raw.items():
                if amount is None or float(amount) <= 0:
                    continue

                ticker = _normalise(asset)
                qty = float(amount)

                if ticker in ("USD", "USDT"):
                    # Already USD — store directly
                    balances.append(Balance(
                        platform="Kraken",
                        account="USD",
                        amount=qty,
                        currency="USD",
                        category="crypto",
                        as_of=now,
                        source="api",
                        notes=f"${qty:.2f} USD",
                    ))
                elif ticker in ("CAD",):
                    balances.append(Balance(
                        platform="Kraken",
                        account="CAD",
                        amount=qty,
                        currency="CAD",
                        category="crypto",
                        as_of=now,
                        source="api",
                    ))
                else:
                    # Crypto — convert to USD equivalent for consistent CAD conversion
                    price_usd = _usd_price(ticker)
                    if price_usd is not None:
                        usd_value = qty * price_usd
                        balances.append(Balance(
                            platform="Kraken",
                            account=ticker,
                            amount=usd_value,
                            currency="USD",
                            category="crypto",
                            as_of=now,
                            source="api",
                            notes=f"{qty:.6g} {ticker} @ ${price_usd:,.2f}",
                        ))
                    else:
                        # No price available — store raw quantity, flag it
                        balances.append(Balance(
                            platform="Kraken",
                            account=ticker,
                            amount=qty,
                            currency=ticker,
                            category="crypto",
                            as_of=now,
                            source="api",
                            notes="no USD price available",
                        ))

            return balances

        except Exception as exc:  # broad catch — network, auth, exchange errors
            logger.warning("Kraken fetch failed: %s", exc)
            print(f"[accounts] Kraken error: {exc}")
            return []

    return _cached("kraken", _fetch)


def oanda_balance() -> list[Balance]:
    """Fetch OANDA account summary (NAV + unrealized P&L)."""

    def _fetch() -> list[Balance]:
        if not _HAS_OANDA:
            return []
        if _missing_key("OANDA", "OANDA_TOKEN", "OANDA_ACCOUNT_ID"):
            return []

        try:
            token = os.environ["OANDA_TOKEN"]
            account_id = os.environ["OANDA_ACCOUNT_ID"]
            practice = os.getenv("OANDA_PRACTICE", "false").lower() == "true"

            client = OandaAPI(access_token=token, environment="practice" if practice else "live")
            req = accounts_ep.AccountSummary(accountID=account_id)
            resp = client.request(req)

            acct = resp["account"]
            nav = float(acct.get("NAV", 0))
            unrealized_pl = float(acct.get("unrealizedPL", 0))
            currency = acct.get("currency", "USD")
            now = _now()

            balances = [
                Balance(
                    platform="OANDA",
                    account="NAV",
                    amount=nav,
                    currency=currency,
                    category="equity",
                    as_of=now,
                    source="api",
                    notes=f"unrealized P&L: {unrealized_pl:+.2f} {currency}",
                )
            ]

            # Separate unrealized P&L entry so it's visible in breakdown
            if unrealized_pl != 0:
                balances.append(Balance(
                    platform="OANDA",
                    account="Unrealized P&L",
                    amount=unrealized_pl,
                    currency=currency,
                    category="equity",
                    as_of=now,
                    source="api",
                    notes="open positions mark-to-market",
                ))

            return balances

        except Exception as exc:
            logger.warning("OANDA fetch failed: %s", exc)
            print(f"[accounts] OANDA error: {exc}")
            return []

    return _cached("oanda", _fetch)


def wise_balances() -> list[Balance]:
    """Fetch Wise multi-currency balances from REST API."""

    def _fetch() -> list[Balance]:
        if not _HAS_REQUESTS:
            return []
        if _missing_key("Wise", "WISE_API_TOKEN", "WISE_PROFILE_ID"):
            return []

        try:
            import requests  # already confirmed available above

            token = os.environ["WISE_API_TOKEN"]
            profile_id = os.environ["WISE_PROFILE_ID"]
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            url = f"https://api.wise.com/v1/borderless-accounts?profileId={profile_id}"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()

            data = resp.json()
            if not data:
                return []

            balances: list[Balance] = []
            now = _now()

            # Wise returns a list of borderless accounts; each has a balances[] list
            for acct in data:
                for bal in acct.get("balances", []):
                    amount_obj = bal.get("amount", {})
                    amount = float(amount_obj.get("value", 0))
                    currency = amount_obj.get("currency", "USD")
                    if amount <= 0:
                        continue
                    balances.append(Balance(
                        platform="Wise",
                        account=currency,
                        amount=amount,
                        currency=currency,
                        category="cash",
                        as_of=now,
                        source="api",
                    ))

            return balances

        except Exception as exc:
            logger.warning("Wise fetch failed: %s", exc)
            print(f"[accounts] Wise error: {exc}")
            return []

    return _cached("wise", _fetch)


def stripe_balance() -> list[Balance]:
    """Fetch Stripe available + pending balances."""

    def _fetch() -> list[Balance]:
        if not _HAS_STRIPE:
            return []
        # Accept any of: STRIPE_RESTRICTED_KEY (preferred, read-only),
        # STRIPE_SECRET_KEY, or STRIPE_API_KEY (legacy name).
        key = (
            os.environ.get("STRIPE_RESTRICTED_KEY", "").strip()
            or os.environ.get("STRIPE_API_KEY", "").strip()
            or os.environ.get("STRIPE_SECRET_KEY", "").strip()
        )
        if not key:
            print("[accounts] skipping Stripe (no STRIPE_RESTRICTED_KEY / STRIPE_API_KEY / STRIPE_SECRET_KEY)")
            return []

        try:
            stripe_sdk.api_key = key
            bal = stripe_sdk.Balance.retrieve()
            now = _now()
            balances: list[Balance] = []

            def _parse_stripe_funds(funds: list, label: str) -> None:
                for entry in funds:
                    amount = entry.get("amount", 0) / 100  # Stripe uses cents
                    currency = entry.get("currency", "usd").upper()
                    if amount <= 0:
                        continue
                    balances.append(Balance(
                        platform="Stripe",
                        account=label,
                        amount=amount,
                        currency=currency,
                        category="business",
                        as_of=now,
                        source="api",
                    ))

            _parse_stripe_funds(bal.get("available", []), "Available")
            _parse_stripe_funds(bal.get("pending", []), "Pending")
            return balances

        except Exception as exc:
            logger.warning("Stripe fetch failed: %s", exc)
            print(f"[accounts] Stripe error: {exc}")
            return []

    return _cached("stripe", _fetch)


def manual_balances() -> list[Balance]:
    """
    Read balances from data/manual_balances.json.
    CC updates this file for Wealthsimple and RBC periodically.
    """

    def _fetch() -> list[Balance]:
        data_path = Path(__file__).parents[1] / "data" / "manual_balances.json"
        if not data_path.exists():
            print(f"[accounts] manual_balances.json not found at {data_path}")
            return []

        try:
            with data_path.open("r", encoding="utf-8") as fh:
                raw = json.load(fh)

            as_of_str = raw.get("as_of", "")
            try:
                as_of_dt = datetime.fromisoformat(as_of_str).replace(tzinfo=timezone.utc)
            except (ValueError, AttributeError):
                as_of_dt = _now()

            balances: list[Balance] = []
            for entry in raw.get("balances", []):
                amount = float(entry.get("amount", 0))
                balances.append(Balance(
                    platform=entry.get("platform", "Unknown"),
                    account=entry.get("account", ""),
                    amount=amount,
                    currency=entry.get("currency", "CAD"),
                    category=entry.get("category", "cash"),
                    as_of=as_of_dt,
                    source="manual",
                    notes=entry.get("notes", ""),
                ))

            return balances

        except Exception as exc:
            logger.warning("manual_balances read failed: %s", exc)
            print(f"[accounts] manual_balances error: {exc}")
            return []

    return _cached("manual", _fetch)


# ---------------------------------------------------------------------------
# FX conversion
# ---------------------------------------------------------------------------

def to_cad(balances: list[Balance], fx: dict[str, float]) -> list[Balance]:
    """
    Return a new list of Balance objects with amounts converted to CAD.
    fx is a dict mapping currency code → CAD rate, e.g. {"USD": 1.37, "EUR": 1.48}.
    Balances already in CAD are returned unchanged.
    """
    result: list[Balance] = []
    for b in balances:
        if b.currency == "CAD":
            result.append(b)
            continue

        rate = fx.get(b.currency)
        if rate is None:
            # Unknown currency — pass through unchanged with a warning note
            logger.debug("No FX rate for %s, keeping as-is", b.currency)
            result.append(b)
            continue

        from dataclasses import replace
        result.append(replace(
            b,
            amount=round(b.amount * rate, 2),
            currency="CAD",
            notes=(b.notes + f" [{b.currency} @ {rate}]").strip(),
        ))

    return result


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def all_balances(fx_rates: Optional[dict[str, float]] = None) -> list[Balance]:
    """
    Run all platform fetchers in parallel and return combined list in CAD.
    Pass fx_rates to override defaults. BTC→USD is attempted live from Kraken;
    falls back to DEFAULT_FX if unavailable.
    """
    fetchers = {
        "kraken": kraken_balances,
        "oanda": oanda_balance,
        "wise": wise_balances,
        "stripe": stripe_balance,
        "manual": manual_balances,
    }

    all_raw: list[Balance] = []
    with ThreadPoolExecutor(max_workers=len(fetchers), thread_name_prefix="cfo") as pool:
        futures = {pool.submit(fn): name for name, fn in fetchers.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                all_raw.extend(future.result())
            except Exception as exc:
                logger.warning("Fetcher %s raised: %s", name, exc)
                print(f"[accounts] {name} fetcher raised: {exc}")

    # Build FX table — try to get live BTC price from already-fetched Kraken data
    fx = dict(DEFAULT_FX)
    if fx_rates:
        fx.update(fx_rates)

    # Inject live BTC→CAD if we have it
    btc_entries = [b for b in all_raw if b.currency == "BTC" and b.platform == "Kraken"]
    if btc_entries and btc_entries[0].notes:
        # notes look like "~$45000.00 USD"
        try:
            usd_str = btc_entries[0].notes.replace("~", "").replace("$", "").replace(" USD", "")
            btc_usd = float(usd_str) / btc_entries[0].amount
            fx["BTC"] = btc_usd * fx.get("USD", 1.37)
        except (ValueError, ZeroDivisionError):
            pass

    return to_cad(all_raw, fx)
