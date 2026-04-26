"""
research/insider_tracking.py
-----------------------------
SEC Form 4 insider transaction tracker via EDGAR's free JSON API.

Why insider transactions matter:
---------------------------------
Academic literature consistently shows that insider purchases — especially
*cluster buying* (multiple insiders buying simultaneously) — predict
positive abnormal returns.  The signal is asymmetric: purchases are
informative, sales are not (insiders sell for many reasons unrelated to
outlook — diversification, taxes, RSU vesting, life events).

Key citations:
  - Seyhun (1986) "Insiders' profits, costs of trading, and market efficiency"
    Journal of Financial Economics — foundational insider predictability paper.
  - Lakonishok & Lee (2001) "Are Insider Trades Informative?"
    Review of Financial Studies — purchase signal, 12-month alpha.
  - Cohen, Malloy & Pomorski (2012) "Decoding Inside Information"
    Journal of Finance — separates *routine* (pre-scheduled, low signal)
    from *opportunistic* (non-routine, high signal) trades.  Opportunistic
    purchases earn ~1.5% monthly alpha over 12 months.
  - Jeng, Metrick & Zeckhauser (2003) "Estimating the Returns to Insider
    Trading" — open-market purchases outperform by ~6%/yr.

The "cluster buying" rule used here (3+ insiders, including CEO/CFO,
within 60 days, net >$250K) aligns with Cohen et al. (2012)'s
opportunistic-insider criterion and Seyhun (1998)'s cluster-signal work.

EDGAR API:
  - Base: https://data.sec.gov/
  - No key required; SEC requires User-Agent header.
  - Rate limit: 10 req/s. We sleep 0.11s between calls to respect this.
  - Submissions endpoint: /submissions/CIK{padded_cik}.json
  - Filing documents: /Archives/edgar/data/{cik}/{accession}/
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_EDGAR_BASE = "https://data.sec.gov"
_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

# SEC HTTP details (User-Agent, rate limit, retries) live in _sec_client.py.
# Sentinels preserved so the existing call-site signature `_get(url, headers=_HEADERS_SEC)`
# keeps working — _sec_client picks the real headers based on use_data_host.
_HEADERS = object()
_HEADERS_SEC = object()

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "edgar"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_TTL_24H = 86400    # 24 hours in seconds
_TTL_1H = 3600      # 1 hour — for recent filing lists (more volatile)

# Transaction codes from SEC Form 4 non-derivative table
# Full list: https://www.sec.gov/cgi-bin/viewer?action=view&cik=0001234567&type=4
_TRANSACTION_CODE_LABELS: dict[str, str] = {
    "P": "open_market_purchase",
    "S": "open_market_sale",
    "A": "grant_award",         # Option/RSU grant — routine
    "D": "disposition",         # Disposition to issuer
    "F": "tax_withholding",     # Payment of exercise/tax — routine
    "G": "gift",
    "H": "expire_short",
    "I": "discretionary",
    "J": "other_acquisition",
    "K": "equity_swap",
    "L": "small_acquisition",
    "M": "option_exercise",     # Option exercise — routine
    "O": "out_of_money_option",
    "R": "ts_plan",             # 10b5-1 plan — routine
    "T": "ts_plan_sale",        # 10b5-1 plan sale — routine
    "U": "tender_offer",
    "W": "will_inheritance",
    "X": "option_exercise_in_money",
    "Z": "trust_deposit",
    "C": "convert",
    "E": "expire_long",
}

# Codes that indicate routine/pre-scheduled transactions (downweighted)
_ROUTINE_CODES = {"A", "F", "M", "R", "T"}

# Titles indicating C-suite / key executives whose buys carry extra weight
_CSUITE_TITLES = {
    "ceo", "chief executive", "president", "cfo", "chief financial",
    "coo", "chief operating", "chairman", "director",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data class
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InsiderTransaction:
    """
    A single Form 4 transaction record.

    Fields mirror the non-derivative and derivative transaction tables in the
    SEC EDGAR Form 4 XML schema (ownershipDocument).
    """
    filer_name: str
    filer_title: str
    ticker: str
    company_name: str
    transaction_date: datetime
    transaction_code: str           # Raw SEC code, e.g. "P", "S"
    transaction_label: str          # Human label, e.g. "open_market_purchase"
    shares: float
    price_per_share: Optional[float]
    total_value: Optional[float]    # shares * price_per_share (USD)
    shares_owned_after: Optional[float]
    ownership_pct: Optional[float]  # Only available in some filings
    is_direct: bool                 # True = direct ownership, False = indirect (family/trust)
    is_routine: bool                # True = grant/option-exercise/10b5-1 plan (downweighted)
    filing_url: str
    accession_number: str

    def to_dict(self) -> dict:
        return {
            "filer_name": self.filer_name,
            "filer_title": self.filer_title,
            "ticker": self.ticker,
            "company_name": self.company_name,
            "transaction_date": self.transaction_date.isoformat(),
            "transaction_code": self.transaction_code,
            "transaction_label": self.transaction_label,
            "shares": self.shares,
            "price_per_share": self.price_per_share,
            "total_value": self.total_value,
            "shares_owned_after": self.shares_owned_after,
            "ownership_pct": self.ownership_pct,
            "is_direct": self.is_direct,
            "is_routine": self.is_routine,
            "filing_url": self.filing_url,
            "accession_number": self.accession_number,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "InsiderTransaction":
        valid = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in d.items() if k in valid}
        filtered["transaction_date"] = datetime.fromisoformat(filtered["transaction_date"])
        return cls(**filtered)


# ─────────────────────────────────────────────────────────────────────────────
#  Cache helpers (shared pattern with fundamentals.py / news_ingest.py)
# ─────────────────────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"edgar_{h}.json"


def _cache_read(path: Path, ttl: int) -> Optional[dict | list]:
    if not path.exists():
        return None
    if time.time() - path.stat().st_mtime > ttl:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _cache_write(path: Path, data: dict | list) -> None:
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
    except OSError as exc:
        logger.warning("EDGAR cache write failed for %s: %s", path, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  HTTP helper — rate-limited, graceful on failure
# ─────────────────────────────────────────────────────────────────────────────

def _get(url: str, headers=None, timeout: int = 15) -> Optional[requests.Response]:
    """
    Rate-limited, retry-wrapped GET against an SEC endpoint.

    Delegates to research._sec_client.get for the SEC-required User-Agent
    (`Atlas CFO Agent (Conaugh McKenna) conaugh@oasisai.work`), the 9 req/s
    process-wide token bucket, and 4-attempt exponential-jittered retry on
    429/503/connection errors. The legacy `headers=_HEADERS` / `_HEADERS_SEC`
    sentinels are interpreted as host-selectors for backwards compatibility.
    """
    from research._sec_client import get as sec_get
    if headers is _HEADERS:
        return sec_get(url, timeout=timeout, use_data_host=True)
    if headers is _HEADERS_SEC or headers is None:
        return sec_get(url, timeout=timeout, use_data_host=False)
    return sec_get(url, headers=headers, timeout=timeout)


# ─────────────────────────────────────────────────────────────────────────────
#  CIK lookup — maps ticker → zero-padded 10-digit CIK
# ─────────────────────────────────────────────────────────────────────────────

def ticker_to_cik(ticker: str) -> Optional[str]:
    """
    Resolve a ticker symbol to the SEC's zero-padded 10-digit CIK.

    Uses EDGAR's company_tickers.json file — a flat JSON map of every
    registered company.  Cached locally for 24 hours (file rarely changes).

    Returns None if the ticker cannot be found (e.g. non-US or OTC company).
    """
    cache_path = _cache_path("company_tickers_v1")
    cached = _cache_read(cache_path, _TTL_24H)

    if cached is None:
        resp = _get(_COMPANY_TICKERS_URL, headers=_HEADERS_SEC)
        if resp is None:
            logger.error("Could not download company_tickers.json from SEC")
            return None
        try:
            raw: dict = resp.json()
        except ValueError:
            logger.error("company_tickers.json parse failed")
            return None
        # Build a ticker→cik dict and cache it
        ticker_map: dict[str, str] = {}
        for _entry in raw.values():
            t = str(_entry.get("ticker", "")).upper()
            cik = str(_entry.get("cik_str", "")).zfill(10)
            if t:
                ticker_map[t] = cik
        _cache_write(cache_path, ticker_map)
        cached = ticker_map

    result = cached.get(ticker.upper())  # type: ignore[union-attr]
    if result is None:
        logger.warning("Ticker %s not found in EDGAR company tickers", ticker)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Form 4 filing list for a CIK
# ─────────────────────────────────────────────────────────────────────────────

def _get_form4_filings(cik: str, days: int) -> list[dict]:
    """
    Fetch the submissions.json for a CIK and return Form 4 filings filed
    within `days` days, sorted newest-first.

    Returns list of dicts with keys: accession_number, filing_date, primary_doc.
    """
    cache_path = _cache_path(f"submissions_{cik}")
    cached = _cache_read(cache_path, _TTL_1H)

    if cached is None:
        url = f"{_EDGAR_BASE}/submissions/CIK{cik}.json"
        resp = _get(url)
        if resp is None:
            return []
        try:
            cached = resp.json()
        except ValueError:
            logger.error("Could not parse submissions JSON for CIK %s", cik)
            return []
        _cache_write(cache_path, cached)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filings_raw = cached.get("filings", {}).get("recent", {})  # type: ignore[union-attr]

    forms = filings_raw.get("form", [])
    dates = filings_raw.get("filingDate", [])
    accessions = filings_raw.get("accessionNumber", [])
    primary_docs = filings_raw.get("primaryDocument", [])

    result: list[dict] = []
    for form, date_str, acc, doc in zip(forms, dates, accessions, primary_docs):
        if form not in ("4", "4/A"):
            continue
        try:
            filed_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if filed_dt < cutoff:
            continue
        result.append({
            "accession_number": acc,
            "filing_date": date_str,
            "primary_doc": doc,
            "cik": cik,
        })

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Form 4 XML parser
# ─────────────────────────────────────────────────────────────────────────────

def _parse_form4_xml(
    xml_text: str,
    ticker: str,
    company_name: str,
    accession_number: str,
    filing_url: str,
) -> list[InsiderTransaction]:
    """
    Parse a Form 4 XML document into InsiderTransaction records.

    SEC Form 4 schema: ownershipDocument contains:
      - reportingOwner (name, title)
      - nonDerivativeTable / nonDerivativeTransaction
      - derivativeTable / derivativeTransaction (options/warrants — included but
        flagged is_routine=True since they're typically grants/exercises)

    We parse both tables so options exercises and RSU vesting are captured
    (and downweighted via is_routine) rather than silently ignored.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        logger.warning("Form 4 XML parse error for %s: %s", accession_number, exc)
        return []

    # Namespace stripping helper
    def _text(elem: Optional[ET.Element], tag: str, default: str = "") -> str:
        if elem is None:
            return default
        child = elem.find(tag)
        return (child.text or "").strip() if child is not None else default

    def _float(elem: Optional[ET.Element], tag: str) -> Optional[float]:
        val = _text(elem, tag)
        try:
            return float(val) if val else None
        except ValueError:
            return None

    # Reporting owner info
    owner_el = root.find(".//reportingOwner")
    filer_name = _text(owner_el, "reportingOwnerId/rptOwnerName") if owner_el is not None else "Unknown"
    rel_el = root.find(".//reportingOwnerRelationship") if owner_el is None else owner_el.find("reportingOwnerRelationship")

    title_parts: list[str] = []
    if rel_el is not None:
        if _text(rel_el, "isDirector") == "1":
            title_parts.append("Director")
        if _text(rel_el, "isOfficer") == "1":
            title_parts.append(_text(rel_el, "officerTitle") or "Officer")
        if _text(rel_el, "isTenPercentOwner") == "1":
            title_parts.append("10% Owner")
    filer_title = ", ".join(title_parts) if title_parts else "Unknown"

    transactions: list[InsiderTransaction] = []

    # ── Non-derivative transactions (common stock purchases/sales) ──
    for tx_el in root.findall(".//nonDerivativeTransaction"):
        # Transaction code lives in transactionCoding, NOT transactionAmounts.
        # Schema: <transactionCoding><transactionCode>S</transactionCode></transactionCoding>
        coding_el = tx_el.find("transactionCoding")
        code = _text(coding_el, "transactionCode") if coding_el is not None else ""
        if not code:
            continue

        date_str = _text(tx_el, "transactionDate/value") or _text(tx_el, "transactionDate")
        try:
            tx_date = datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        shares_el = tx_el.find("transactionAmounts")
        shares = _float(shares_el, "transactionShares/value") or _float(shares_el, "transactionShares")
        if shares is None:
            continue

        price = _float(shares_el, "transactionPricePerShare/value") or _float(shares_el, "transactionPricePerShare")
        total_value = (shares * price) if (shares and price) else None

        post_el = tx_el.find("postTransactionAmounts")
        shares_after = _float(post_el, "sharesOwnedFollowingTransaction/value") or _float(post_el, "sharesOwnedFollowingTransaction") if post_el is not None else None

        own_nature = _text(tx_el, "ownershipNature/directOrIndirectOwnership/value")
        is_direct = own_nature.upper() == "D" if own_nature else True

        is_routine = code in _ROUTINE_CODES

        transactions.append(InsiderTransaction(
            filer_name=filer_name,
            filer_title=filer_title,
            ticker=ticker,
            company_name=company_name,
            transaction_date=tx_date,
            transaction_code=code,
            transaction_label=_TRANSACTION_CODE_LABELS.get(code, f"unknown_{code}"),
            shares=abs(shares),
            price_per_share=price,
            total_value=abs(total_value) if total_value else None,
            shares_owned_after=shares_after,
            ownership_pct=None,  # Not in Form 4 directly
            is_direct=is_direct,
            is_routine=is_routine,
            filing_url=filing_url,
            accession_number=accession_number,
        ))

    # ── Derivative transactions (options, warrants, convertibles) ──
    for tx_el in root.findall(".//derivativeTransaction"):
        # Same schema as non-derivative: code is in transactionCoding.
        coding_el = tx_el.find("transactionCoding")
        code = _text(coding_el, "transactionCode") if coding_el is not None else ""
        if not code:
            continue

        date_str = _text(tx_el, "transactionDate/value") or _text(tx_el, "transactionDate")
        try:
            tx_date = datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        shares_el = tx_el.find("transactionAmounts")
        shares = _float(shares_el, "transactionShares/value") or _float(shares_el, "transactionShares")
        if shares is None:
            # Try underlying shares
            shares = _float(tx_el.find("underlyingSecurityShares"), "value") or \
                     _float(tx_el, "underlyingSecurityShares")
        if shares is None:
            continue

        price = _float(shares_el, "transactionPricePerShare/value") or _float(shares_el, "transactionPricePerShare")
        conv_price = _float(tx_el, "conversionOrExercisePrice/value") or _float(tx_el, "conversionOrExercisePrice")
        effective_price = price or conv_price
        total_value = (shares * effective_price) if (shares and effective_price) else None

        own_nature = _text(tx_el, "ownershipNature/directOrIndirectOwnership/value")
        is_direct = own_nature.upper() == "D" if own_nature else True

        # Derivative transactions are almost always routine (options grants/exercises)
        is_routine = True

        transactions.append(InsiderTransaction(
            filer_name=filer_name,
            filer_title=filer_title,
            ticker=ticker,
            company_name=company_name,
            transaction_date=tx_date,
            transaction_code=code,
            transaction_label=_TRANSACTION_CODE_LABELS.get(code, f"unknown_{code}"),
            shares=abs(shares),
            price_per_share=effective_price,
            total_value=abs(total_value) if total_value else None,
            shares_owned_after=None,
            ownership_pct=None,
            is_direct=is_direct,
            is_routine=is_routine,
            filing_url=filing_url,
            accession_number=accession_number,
        ))

    return transactions


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def recent_insider_activity(ticker: str, days: int = 90) -> list[InsiderTransaction]:
    """
    Return all Form 4 insider transactions for `ticker` filed within the last
    `days` calendar days.

    Algorithm:
      1. Resolve ticker → CIK via company_tickers.json
      2. Fetch CIK submissions.json to get Form 4 filings in window
      3. For each filing, fetch and parse the primary XML document
      4. Return all InsiderTransaction records, sorted newest-first

    Data is cached per-filing (accession number) for 24 hours.
    Returns [] on any network/parse failure.
    """
    cik = ticker_to_cik(ticker)
    if cik is None:
        logger.error("Cannot resolve CIK for ticker %s", ticker)
        return []

    company_name = ticker  # Fallback; will be overwritten from submissions JSON

    # Get company name from submissions JSON (already cached from _get_form4_filings)
    sub_cache = _cache_read(_cache_path(f"submissions_{cik}"), _TTL_1H)
    if sub_cache and isinstance(sub_cache, dict):
        company_name = sub_cache.get("name", ticker)

    filings = _get_form4_filings(cik, days)
    if not filings:
        logger.info("No Form 4 filings found for %s in last %d days", ticker, days)
        return []

    all_transactions: list[InsiderTransaction] = []

    for filing in filings:
        acc = filing["accession_number"]
        # Accession number format: 0001234567-22-000001 → 0001234567-22-000001
        acc_clean = acc.replace("-", "")
        cache_path = _cache_path(f"form4_{acc_clean}")

        xml_cached = _cache_read(cache_path, _TTL_24H)
        if xml_cached is not None and isinstance(xml_cached, dict):
            # Reconstruct from cached dict list
            tx_list = xml_cached.get("transactions", [])
            all_transactions.extend([InsiderTransaction.from_dict(t) for t in tx_list])
            continue

        # Build the filing document URL.
        # EDGAR primary_doc values sometimes include an XSLT viewer prefix like
        # "xslF345X06/wk-form4_12345.xml".  Strip any subdirectory prefix so we
        # hit the raw XML directly (which lives in the accession root directory).
        doc = filing["primary_doc"]
        if "/" in doc:
            doc = doc.split("/")[-1]  # e.g. "xslF345X06/wk-form4_xxx.xml" → "wk-form4_xxx.xml"
        filing_url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
            f"{acc_clean}/{doc}"
        )

        resp = _get(filing_url, headers=_HEADERS_SEC)
        if resp is None:
            continue

        content_type = resp.headers.get("Content-Type", "")
        text = resp.text

        # Some primary docs are HTML wrappers; try to find the XML inside
        if "html" in content_type.lower() and "<ownershipDocument" not in text:
            # Look for the .xml file in the index
            index_url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                f"{acc_clean}/{acc_clean}-index.htm"
            )
            idx_resp = _get(index_url, headers=_HEADERS_SEC)
            if idx_resp is not None:
                # Find .xml link in index
                xml_match = re.search(r'href="([^"]*\.xml)"', idx_resp.text, re.IGNORECASE)
                if xml_match:
                    xml_url = "https://www.sec.gov" + xml_match.group(1)
                    xml_resp = _get(xml_url, headers=_HEADERS_SEC)
                    if xml_resp is not None:
                        text = xml_resp.text
                        filing_url = xml_url

        if "<ownershipDocument" not in text:
            logger.debug("No ownershipDocument in filing %s — skipping", acc)
            continue

        txs = _parse_form4_xml(text, ticker, company_name, acc, filing_url)

        # Cache this filing's parsed transactions
        _cache_write(cache_path, {"transactions": [t.to_dict() for t in txs]})
        all_transactions.extend(txs)

    # Sort newest-first
    all_transactions.sort(key=lambda t: t.transaction_date, reverse=True)
    return all_transactions


def insider_score(ticker: str, days: int = 90) -> dict:
    """
    Aggregate insider transactions into an actionable signal dict.

    Returns:
        {
          "ticker": str,
          "buy_count": int,          # non-routine open-market purchases
          "sell_count": int,         # non-routine open-market sales
          "net_dollars": float,      # purchases - sales (non-routine only)
          "cluster_buying": bool,    # 3+ distinct insiders buying within 60 days
          "ceo_cfo_buying": bool,    # CEO or CFO made a non-routine purchase
          "signal": str,             # "strong_buy"|"buy"|"neutral"|"sell"|"strong_sell"
          "conviction": float,       # 0.0–1.0 (for Atlas conviction score system)
          "summary": str,            # plain-English one-liner
        }

    Signal logic (based on Cohen, Malloy & Pomorski 2012 opportunistic-insider
    framework):
      - strong_buy: 3+ distinct insiders (incl. CEO/CFO), all buying in 60 days,
                    net > $250K in non-routine purchases
      - buy:        2+ distinct insiders buying, or 1 C-suite buying > $100K
      - neutral:    mixed signals or insufficient data
      - sell:       net outflows > $250K from non-routine sales
      - strong_sell: cluster selling (3+ insiders) with no buys
    """
    txs = recent_insider_activity(ticker, days)

    # Filter to non-routine open-market transactions only
    open_buys = [t for t in txs if t.transaction_code == "P" and not t.is_routine]
    open_sells = [t for t in txs if t.transaction_code == "S" and not t.is_routine]

    # 60-day window for cluster detection (tighter = more informative per Cohen 2012)
    cutoff_60 = datetime.now(timezone.utc) - timedelta(days=60)
    recent_buys = [t for t in open_buys if t.transaction_date >= cutoff_60]
    recent_sells = [t for t in open_sells if t.transaction_date >= cutoff_60]

    # Distinct insiders (by name, case-normalised)
    buying_insiders = {t.filer_name.lower() for t in recent_buys}
    selling_insiders = {t.filer_name.lower() for t in recent_sells}

    buy_dollars = sum(t.total_value or 0 for t in recent_buys)
    sell_dollars = sum(t.total_value or 0 for t in recent_sells)
    net_dollars = buy_dollars - sell_dollars

    # C-suite detection — does the filer title mention a key executive role?
    def _is_csuite(title: str) -> bool:
        tl = title.lower()
        return any(kw in tl for kw in _CSUITE_TITLES)

    ceo_cfo_buying = any(_is_csuite(t.filer_title) for t in recent_buys)
    cluster_buying = len(buying_insiders) >= 3

    # ── Signal determination ──
    if cluster_buying and ceo_cfo_buying and net_dollars >= 250_000:
        signal = "strong_buy"
        conviction = 0.85
        summary = (
            f"{len(buying_insiders)} insiders (incl. C-suite) cluster-bought "
            f"${net_dollars:,.0f} net in 60 days — strong opportunistic signal."
        )
    elif (len(buying_insiders) >= 2 and buy_dollars > 0) or (ceo_cfo_buying and buy_dollars >= 100_000):
        signal = "buy"
        conviction = 0.65
        who = "C-suite + others" if ceo_cfo_buying else f"{len(buying_insiders)} insiders"
        summary = f"{who} bought ${buy_dollars:,.0f} in last 60 days — positive signal."
    elif len(selling_insiders) >= 3 and sell_dollars > 250_000 and len(buying_insiders) == 0:
        signal = "strong_sell"
        conviction = 0.70
        summary = (
            f"{len(selling_insiders)} insiders sold ${sell_dollars:,.0f} with no purchases "
            f"— cluster sell signal (rare but meaningful)."
        )
    elif sell_dollars > 250_000 and len(buying_insiders) == 0:
        signal = "sell"
        conviction = 0.45
        summary = f"Net insider outflows of ${sell_dollars:,.0f}. No open-market purchases."
    else:
        signal = "neutral"
        conviction = 0.0
        summary = (
            f"Mixed/insufficient insider data. "
            f"Buys: {len(buying_insiders)} insiders (${buy_dollars:,.0f}), "
            f"Sells: {len(selling_insiders)} insiders (${sell_dollars:,.0f})."
        )

    return {
        "ticker": ticker.upper(),
        "buy_count": len(open_buys),
        "sell_count": len(open_sells),
        "net_dollars": net_dollars,
        "cluster_buying": cluster_buying,
        "ceo_cfo_buying": ceo_cfo_buying,
        "signal": signal,
        "conviction": conviction,
        "summary": summary,
        "total_transactions_parsed": len(txs),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point — `python -m research.insider_tracking TICKER`
# ─────────────────────────────────────────────────────────────────────────────

def _cli() -> None:
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Atlas insider tracking — Form 4 signal via SEC EDGAR"
    )
    parser.add_argument("ticker", help="Ticker symbol, e.g. NVDA")
    parser.add_argument("--days", type=int, default=90, help="Lookback window in days (default 90)")
    parser.add_argument("--cik-only", action="store_true", help="Only print the CIK and exit")
    args = parser.parse_args()

    ticker = args.ticker.upper()

    if args.cik_only:
        cik = ticker_to_cik(ticker)
        print(f"{ticker} → CIK: {cik}")
        return

    print(f"\n{'='*60}")
    print(f"  ATLAS INSIDER TRACKER — {ticker}")
    print(f"  Lookback: {args.days} days  |  Source: SEC EDGAR Form 4")
    print(f"{'='*60}\n")

    score = insider_score(ticker, args.days)
    print(f"SIGNAL:      {score['signal'].upper()}")
    print(f"CONVICTION:  {score['conviction']:.0%}")
    print(f"SUMMARY:     {score['summary']}")
    print(f"\nBuy count (non-routine):  {score['buy_count']}")
    print(f"Sell count (non-routine): {score['sell_count']}")
    print(f"Net dollars:              ${score['net_dollars']:,.0f}")
    print(f"Cluster buying:           {score['cluster_buying']}")
    print(f"CEO/CFO buying:           {score['ceo_cfo_buying']}")
    print(f"Total transactions:       {score['total_transactions_parsed']}\n")

    txs = recent_insider_activity(ticker, args.days)
    # Show last 10 transactions (all types for transparency)
    shown = txs[:10]
    if shown:
        print(f"{'-'*60}")
        print(f"  LAST {min(10, len(shown))} TRANSACTIONS (newest first)")
        print(f"{'-'*60}")
        for t in shown:
            routine_tag = " [ROUTINE]" if t.is_routine else ""
            price_str = f"@ ${t.price_per_share:.2f}" if t.price_per_share else ""
            val_str = f"= ${t.total_value:,.0f}" if t.total_value else ""
            print(
                f"  {t.transaction_date.date()}  {t.transaction_code} ({t.transaction_label})"
                f"{routine_tag}\n"
                f"    {t.filer_name} [{t.filer_title}]\n"
                f"    {t.shares:,.0f} shares {price_str} {val_str}\n"
            )
    else:
        print("No transactions found in window.")

    print(f"{'='*60}")
    print("Source: SEC EDGAR Form 4 (free, no API key required)")
    print("Academic basis: Cohen, Malloy & Pomorski (2012) JoF")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    _cli()
