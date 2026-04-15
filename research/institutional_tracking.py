"""
research/institutional_tracking.py
-------------------------------------
SEC Form 13F institutional holdings tracker via EDGAR's free JSON API.

Why 13F tracking matters:
--------------------------
Form 13F is filed quarterly by investment managers with >$100M AUM, disclosing
every equity position above $200K (threshold raised from $100K in 2023) or
10,000 shares.  The filing deadline is 45 days after quarter-end.

The signal value of "smart money" 13Fs:
  - Wermers (2000) "Mutual Fund Performance" Journal of Finance — funds holding
    high-conviction positions (top decile by weight) outperform by ~3.3%/yr.
  - Jiang, Yao & Yu (2007) "Do Mutual Funds Time the Market?" JFE — skilled
    managers show persistent performance visible in quarterly holdings.
  - Dasgupta, Prat & Verardo (2011) "Institutional Trade Persistence and
    Long-term Equity Returns" JoF — institutional momentum is a real return
    predictor at 1–2 year horizons.
  - Shiller (2000) and countless event studies confirm that concentrated
    positions by named "star" managers (Buffett, Druckenmiller, Klarman) are
    widely followed precisely because their public track records demonstrate
    genuine alpha generation.

Limitations (be honest about them):
  - 45-day delay means positions are stale by the time you see them.
  - Managers can conceal positions via "confidential treatment" requests.
  - Large position changes may have occurred between filing and your read.
  - This is a *consensus* signal — trade crowding is a real risk.
  - Best used for conviction confirmation, not as a standalone trade signal.

EDGAR API:
  - Base: https://data.sec.gov/
  - No key required; SEC requires User-Agent header.
  - Rate limit: 10 req/s. We sleep 0.11s between calls.
  - Submissions endpoint: /submissions/CIK{padded_cik}.json
  - XBRL viewer: /api/xbrl/companyconcept/ (not needed for 13F)
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
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

_EDGAR_BASE = "https://data.sec.gov"
_SEC_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"

_HEADERS = {
    "User-Agent": "Atlas CFO Agent contact@oasisai.work",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}
_HEADERS_SEC = {
    "User-Agent": "Atlas CFO Agent contact@oasisai.work",
    "Accept-Encoding": "gzip, deflate",
}

_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "edgar"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_TTL_24H = 86400    # 24 hours — 13F data is quarterly, 24h cache is fine
_TTL_1H = 3600      # For submission indexes (filing list)

_RATE_SLEEP = 0.11  # 10 req/s max per SEC policy


# ─────────────────────────────────────────────────────────────────────────────
#  Tracked funds — CIK map for famous managers CC should follow
# ─────────────────────────────────────────────────────────────────────────────

def tracked_funds() -> dict[str, str]:
    """
    Return a {fund_name: cik} mapping for the institutional investors with the
    strongest historical alpha track records.

    CIKs are stable, permanent identifiers.  Fund names are for display only.

    Selection criteria:
      - Public track record of significant alpha over multi-decade horizon, OR
      - Contrarian signal value (Burry's short thesis detection), OR
      - Massive AUM implying market-moving positions (Bridgewater, ARK)

    CIKs verified against EDGAR submissions as of 2026.
    """
    return {
        "Berkshire Hathaway (Buffett)": "0001067983",
        "Scion Asset Management (Burry)": "0001649339",
        "Pershing Square (Ackman)": "0001336528",
        "Duquesne Family Office (Druckenmiller)": "0001536411",
        "Bridgewater Associates (Dalio)": "0001350694",
        "Appaloosa Management (Tepper)": "0001656456",
        "Baupost Group (Klarman)": "0001061768",
        "Greenlight Capital (Einhorn)": "0001079114",
        "Third Point (Loeb)": "0001040273",
        "Tiger Global Management": "0001167483",
        "Coatue Management": "0001135730",
        "ARK Investment Management (Wood)": "0001697748",
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Data class
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Holding:
    """
    A single equity position from a 13F-HR filing.

    `change_vs_prior` is set when two consecutive quarters are compared;
    None when only a single quarter is available.
    """
    ticker: str                             # CUSIP-resolved or raw symbol
    cusip: str                              # 9-digit CUSIP (unique security ID)
    fund_name: str
    cik: str
    shares: int
    value_usd: int                          # USD value as reported (in thousands → converted)
    pct_of_portfolio: Optional[float]       # This holding / total portfolio value (%)
    reported_date: str                      # "YYYY-MM-DD" quarter-end date
    change_vs_prior: Optional[str]          # "new"|"increased"|"decreased"|"exited"|None

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "cusip": self.cusip,
            "fund_name": self.fund_name,
            "cik": self.cik,
            "shares": self.shares,
            "value_usd": self.value_usd,
            "pct_of_portfolio": self.pct_of_portfolio,
            "reported_date": self.reported_date,
            "change_vs_prior": self.change_vs_prior,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Holding":
        valid = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in d.items() if k in valid}
        return cls(**filtered)


# ─────────────────────────────────────────────────────────────────────────────
#  Cache helpers (same pattern as insider_tracking.py / fundamentals.py)
# ─────────────────────────────────────────────────────────────────────────────

def _cache_path(key: str) -> Path:
    h = hashlib.md5(key.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"13f_{h}.json"


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
        logger.warning("13F cache write failed for %s: %s", path, exc)


# ─────────────────────────────────────────────────────────────────────────────
#  HTTP helper — rate-limited
# ─────────────────────────────────────────────────────────────────────────────

def _get(url: str, headers: Optional[dict] = None, timeout: int = 20) -> Optional[requests.Response]:
    """
    Rate-limited GET with graceful failure.  Returns None on any error so
    callers can return [] without crashing the whole research pipeline.
    """
    time.sleep(_RATE_SLEEP)
    _h = headers or _HEADERS
    try:
        resp = requests.get(url, headers=_h, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        logger.warning("EDGAR 13F request failed for %s: %s", url, exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  13F filing list for a CIK
# ─────────────────────────────────────────────────────────────────────────────

def _get_13f_filings(cik: str, max_filings: int = 4) -> list[dict]:
    """
    Fetch the submissions.json for a CIK and return the N most recent
    13F-HR filings (most recent first).

    Returns list of dicts: {accession_number, filing_date, primary_doc, cik}
    """
    cache_path = _cache_path(f"13f_subs_{cik}")
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

    filings_raw = cached.get("filings", {}).get("recent", {})  # type: ignore[union-attr]

    forms = filings_raw.get("form", [])
    dates = filings_raw.get("filingDate", [])
    accessions = filings_raw.get("accessionNumber", [])
    primary_docs = filings_raw.get("primaryDocument", [])

    result: list[dict] = []
    for form, date_str, acc, doc in zip(forms, dates, accessions, primary_docs):
        if form not in ("13F-HR", "13F-HR/A"):
            continue
        result.append({
            "accession_number": acc,
            "filing_date": date_str,
            "primary_doc": doc,
            "cik": cik,
        })
        if len(result) >= max_filings:
            break

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  CUSIP → ticker resolution (best-effort via SEC EDGAR company tickers)
# ─────────────────────────────────────────────────────────────────────────────

_CUSIP_TO_TICKER_CACHE: dict[str, str] = {}


def _cusip_to_ticker_best_effort(cusip: str, name: str) -> str:
    """
    Attempt to resolve a CUSIP to a recognisable display name.

    13F issuer names are ALL-CAPS abbreviated strings (e.g. "NVIDIA CORP",
    "APPLE INC").  We keep the full cleaned name rather than stripping it down
    to an unrecognisable stub — this preserves searchability in who_owns().

    This is best-effort — a proper CUSIP→ticker mapping requires a paid database.
    The name is used for display and partial-match searching, not as a canonical
    ticker symbol.
    """
    if cusip in _CUSIP_TO_TICKER_CACHE:
        return _CUSIP_TO_TICKER_CACHE[cusip]

    # Keep the name largely intact; only strip purely generic trailing tokens
    # that add no distinguishing information (e.g. " COM" for "common stock class").
    # Do NOT strip " INC", " CORP", " LTD" — they're part of company names.
    cleaned = name.strip()
    # Only strip " COM" if it's clearly a share-class suffix, not part of the name
    if cleaned.endswith(" COM"):
        cleaned = cleaned[:-4].strip()

    _CUSIP_TO_TICKER_CACHE[cusip] = cleaned
    return cleaned


# ─────────────────────────────────────────────────────────────────────────────
#  13F XML parser
# ─────────────────────────────────────────────────────────────────────────────


def _strip_namespaces(xml_text: str) -> str:
    """
    Remove all XML namespace declarations and prefixes so ET.findall()
    works with plain tag names.

    Handles:
      - Default namespace:  xmlns="http://..."       → removed
      - Prefixed namespace: xmlns:ns1="http://..."   → removed
      - Prefixed tags:      <ns1:infoTable>          → <infoTable>
      - Closing prefixed:   </ns1:infoTable>         → </infoTable>
      - xsi:type attr:      xsi:type="..."           → removed
    """
    # Remove all xmlns declarations (both default and prefixed)
    cleaned = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', "", xml_text)
    # Remove namespace prefix from opening/closing/self-closing tags
    cleaned = re.sub(r"<(/?)\w+:([\w]+)", r"<\1\2", cleaned)
    # Remove namespace-prefixed attributes (e.g. xsi:schemaLocation="...")
    cleaned = re.sub(r'\s+\w+:\w+="[^"]*"', "", cleaned)
    return cleaned


def _parse_13f_xml(
    xml_text: str,
    fund_name: str,
    cik: str,
    filing_date: str,
) -> list[Holding]:
    """
    Parse a 13F-HR informationTable XML into Holding records.

    The information table structure:
      <informationTable>
        <infoTable>
          <nameOfIssuer>APPLE INC</nameOfIssuer>
          <titleOfClass>COM</titleOfClass>
          <cusip>037833100</cusip>
          <value>123456</value>           ← in thousands of USD
          <shrsOrPrnAmt>
            <sshPrnamt>100000</sshPrnamt>
            <sshPrnamtType>SH</sshPrnamtType>
          </shrsOrPrnAmt>
          <investmentDiscretion>SOLE</investmentDiscretion>
          <votingAuthority>...</votingAuthority>
        </infoTable>
        ...
      </informationTable>
    """
    # Strip namespaces for simpler parsing
    cleaned = _strip_namespaces(xml_text)

    try:
        root = ET.fromstring(cleaned)
    except ET.ParseError as exc:
        logger.warning("13F XML parse error for CIK %s: %s", cik, exc)
        return []

    holdings: list[Holding] = []

    # Handle both root-is-informationTable and nested cases
    info_tables = root.findall(".//infoTable")
    if not info_tables:
        # Some filings wrap in informationTable at root
        info_tables = root.findall("infoTable")

    for row in info_tables:
        def _text(tag: str, default: str = "") -> str:
            el = row.find(tag)
            return (el.text or "").strip() if el is not None else default

        name = _text("nameOfIssuer")
        cusip = _text("cusip").replace("-", "").strip()
        title_class = _text("titleOfClass")

        value_str = _text("value")
        try:
            # The infoTable <value> field is reported in USD (whole dollars),
            # despite the SEC XSD formally specifying thousands.  Modern EDGAR
            # submitters file in actual dollars — confirmed against known
            # Berkshire positions (692K AAPL shares → $188M raw value ≈ $272/share).
            value_usd = int(value_str.replace(",", "")) if value_str else 0
        except ValueError:
            value_usd = 0

        shares_str = _text("shrsOrPrnAmt/sshPrnamt")
        try:
            shares = int(shares_str.replace(",", "")) if shares_str else 0
        except ValueError:
            shares = 0

        if not name or not cusip or value_usd == 0:
            continue

        # Best-effort ticker resolution
        # Include title_class in the CUSIP key to differentiate share classes
        full_cusip = f"{cusip}_{title_class}" if title_class not in ("COM", "SH", "") else cusip
        ticker = _cusip_to_ticker_best_effort(full_cusip, name)

        holdings.append(Holding(
            ticker=ticker,
            cusip=cusip,
            fund_name=fund_name,
            cik=cik,
            shares=shares,
            value_usd=value_usd,
            pct_of_portfolio=None,  # Calculated after full portfolio is assembled
            reported_date=filing_date,
            change_vs_prior=None,   # Set during comparison if prior quarter available
        ))

    # Calculate portfolio weights
    total_value = sum(h.value_usd for h in holdings)
    if total_value > 0:
        for h in holdings:
            h.pct_of_portfolio = round((h.value_usd / total_value) * 100, 4)

    return holdings


# ─────────────────────────────────────────────────────────────────────────────
#  Filing document fetcher — handles both XML and HTML-wrapped submissions
# ─────────────────────────────────────────────────────────────────────────────

_EFTS_BASE = "https://efts.sec.gov"


def _get_filing_document_names(accession: str) -> list[str]:
    """
    Use EDGAR's full-text search index (efts.sec.gov) to list all document
    filenames for a given accession number.

    This avoids fetching www.sec.gov/Archives index pages, which are rate-
    limited and frequently return 503 from non-browser clients.

    Returns list of filenames (not full URLs), e.g. ["primary_doc.xml", "50240.xml"]
    """
    cache_path = _cache_path(f"efts_{accession.replace('-', '')}")
    cached = _cache_read(cache_path, _TTL_24H)
    if cached is not None and isinstance(cached, list):
        return cached  # type: ignore[return-value]

    url = f"{_EFTS_BASE}/LATEST/search-index?q=%22{accession}%22"
    resp = _get(url, headers=_HEADERS_SEC)
    if resp is None:
        return []

    try:
        data = resp.json()
    except ValueError:
        return []

    filenames: list[str] = []
    for hit in data.get("hits", {}).get("hits", []):
        # _id format: "{accession}:{filename}"
        hit_id: str = hit.get("_id", "")
        if ":" in hit_id:
            filenames.append(hit_id.split(":", 1)[1])

    _cache_write(cache_path, filenames)
    return filenames


def _fetch_13f_document(cik: str, accession: str, primary_doc: str) -> Optional[str]:
    """
    Fetch the 13F information table XML text.

    Strategy (ordered by reliability):
      1. Strip any XSLT subdirectory prefix from primary_doc and fetch directly.
         If it contains the information table, return immediately.
      2. Use efts.sec.gov to enumerate all document filenames for the accession,
         then fetch each XML file until one contains <informationTable>.
         This avoids the www.sec.gov/Archives index page (503-prone).
      3. Fall back to the .htm index page on www.sec.gov if EFTS fails.

    The 13F information table uses namespace declarations like:
      xmlns:ns1="http://www.sec.gov/edgar/document/thirteenf/informationtable"
    These are stripped before parsing via _strip_namespaces().
    """
    acc_clean = accession.replace("-", "")
    cik_int = int(cik)

    def _is_info_table(text: str) -> bool:
        return "<informationTable" in text or "<infoTable" in text

    # ── Step 1: Try the primary doc directly (strip XSLT subdir prefix) ──
    doc = primary_doc
    if "/" in doc:
        doc = doc.split("/")[-1]  # "xslForm13F_X02/primary_doc.xml" → "primary_doc.xml"
    primary_url = f"{_SEC_ARCHIVES}/{cik_int}/{acc_clean}/{doc}"
    resp = _get(primary_url, headers=_HEADERS_SEC)
    if resp is not None and _is_info_table(resp.text):
        return resp.text

    # ── Step 2: Use efts.sec.gov to enumerate all XML files ──
    all_filenames = _get_filing_document_names(accession)
    xml_files = [f for f in all_filenames if f.lower().endswith(".xml") and f != doc]

    # Prefer files with "infotable", "information", or numeric names (common pattern)
    def _priority(fname: str) -> int:
        fl = fname.lower()
        if any(k in fl for k in ["infotable", "information", "13f"]):
            return 0
        if re.match(r"^\d+\.xml$", fl):
            return 1   # Pure-numeric names (e.g. "50240.xml") are often info tables
        return 2

    xml_files.sort(key=_priority)

    for fname in xml_files:
        url = f"{_SEC_ARCHIVES}/{cik_int}/{acc_clean}/{fname}"
        xml_resp = _get(url, headers=_HEADERS_SEC)
        if xml_resp is not None and _is_info_table(xml_resp.text):
            return xml_resp.text

    # ── Step 3: Fall back to .htm index page ──
    index_url = f"{_SEC_ARCHIVES}/{cik_int}/{acc_clean}/{acc_clean}-index.htm"
    idx_resp = _get(index_url, headers=_HEADERS_SEC)
    if idx_resp is not None:
        xml_hrefs = re.findall(r'href="([^"]*\.xml)"', idx_resp.text, re.IGNORECASE)
        for xml_path in xml_hrefs:
            xml_url = (
                "https://www.sec.gov" + xml_path if xml_path.startswith("/")
                else xml_path if xml_path.startswith("http")
                else f"{_SEC_ARCHIVES}/{cik_int}/{acc_clean}/{xml_path}"
            )
            xml_resp = _get(xml_url, headers=_HEADERS_SEC)
            if xml_resp is not None and _is_info_table(xml_resp.text):
                return xml_resp.text

    logger.warning("Could not locate 13F information table XML for CIK %s acc %s", cik, accession)
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_fund_holdings(cik: str, quarter: Optional[str] = None) -> list[Holding]:
    """
    Return the most recent 13F-HR holdings for a fund CIK.

    Args:
        cik:     SEC CIK (zero-padded or not)
        quarter: Optional "YYYY-QN" filter, e.g. "2025-Q3".  If None, returns
                 the most recent available filing.

    Returns:
        List of Holding objects sorted by value_usd descending.
        Returns [] on network error or no 13F found.

    Note: Values are as-reported (USD, in actual dollars, not thousands).
    The 45-day filing delay means the most recent quarter available is
    typically the quarter that ended ~45–90 days ago.
    """
    cik = cik.zfill(10)
    filings = _get_13f_filings(cik, max_filings=4)

    if not filings:
        logger.info("No 13F-HR filings found for CIK %s", cik)
        return []

    # Select filing based on quarter filter or most recent
    target = None
    if quarter:
        # Map "2025-Q3" to the approximate filing date range
        try:
            year, q = quarter.split("-Q")
            yr = int(year)
            qtr = int(q)
            quarter_end_months = {1: 3, 2: 6, 3: 9, 4: 12}
            qtr_month = quarter_end_months.get(qtr, 12)
            qtr_date_str = f"{yr}-{qtr_month:02d}"
            for f in filings:
                if qtr_date_str[:7] <= f["filing_date"][:7]:
                    target = f
                    break
        except (ValueError, KeyError):
            logger.warning("Could not parse quarter filter: %s", quarter)
    if target is None:
        target = filings[0]  # Most recent

    acc = target["accession_number"]
    acc_clean = acc.replace("-", "")
    fund_name = ""  # Filled from submissions JSON below

    # Get fund name from submissions JSON
    sub_cache = _cache_read(_cache_path(f"13f_subs_{cik}"), _TTL_1H)
    if sub_cache and isinstance(sub_cache, dict):
        fund_name = sub_cache.get("name", f"CIK {cik}")

    # Check filing cache
    cache_path = _cache_path(f"13f_holdings_{acc_clean}")
    cached = _cache_read(cache_path, _TTL_24H)
    if cached is not None and isinstance(cached, list):
        return [Holding.from_dict(h) for h in cached]

    # Fetch and parse
    xml_text = _fetch_13f_document(cik, acc, target["primary_doc"])
    if xml_text is None:
        return []

    holdings = _parse_13f_xml(xml_text, fund_name or f"CIK {cik}", cik, target["filing_date"])
    holdings.sort(key=lambda h: h.value_usd, reverse=True)

    _cache_write(cache_path, [h.to_dict() for h in holdings])
    return holdings


def what_are_smart_money_buying(top_n: int = 20) -> list[dict]:
    """
    Aggregate the most recent 13F filings from all tracked funds and return
    the top N tickers by *count of funds holding* and *total value*.

    This produces the "smart money consensus" — positions that multiple
    tracked high-alpha managers hold simultaneously.

    Per Dasgupta, Prat & Verardo (2011): institutional momentum at the
    portfolio level predicts 1–2 year returns.  Positions held by 4+ tracked
    funds are the highest-conviction consensus signal.

    Returns:
        List of dicts sorted by fund_count desc:
        {
          "ticker": str,
          "cusip": str,
          "fund_count": int,
          "total_value_usd": int,
          "funds": list[str],         # fund names holding this position
          "avg_pct_of_portfolio": float,
        }
    """
    funds = tracked_funds()

    # Aggregate holdings across all tracked funds
    # Key: cusip → accumulation dict
    agg: dict[str, dict] = {}

    for fund_name, cik in funds.items():
        holdings = get_fund_holdings(cik)
        if not holdings:
            logger.info("No holdings for %s (CIK %s)", fund_name, cik)
            continue

        for h in holdings:
            key = h.cusip
            if key not in agg:
                agg[key] = {
                    "ticker": h.ticker,
                    "cusip": h.cusip,
                    "fund_count": 0,
                    "total_value_usd": 0,
                    "funds": [],
                    "pct_sum": 0.0,
                }
            agg[key]["fund_count"] += 1
            agg[key]["total_value_usd"] += h.value_usd
            agg[key]["funds"].append(fund_name)
            agg[key]["pct_sum"] += h.pct_of_portfolio or 0.0

    # Calculate average portfolio weight and sort
    results = []
    for data in agg.values():
        fc = data["fund_count"]
        results.append({
            "ticker": data["ticker"],
            "cusip": data["cusip"],
            "fund_count": fc,
            "total_value_usd": data["total_value_usd"],
            "funds": data["funds"],
            "avg_pct_of_portfolio": round(data["pct_sum"] / fc, 4) if fc else 0.0,
        })

    results.sort(key=lambda x: (x["fund_count"], x["total_value_usd"]), reverse=True)
    return results[:top_n]


def who_owns(ticker: str) -> list[dict]:
    """
    Return which tracked funds hold `ticker` as of their most recent 13F.

    Matching is done against both the resolved ticker string and the security
    name from the 13F.  Partial name match is used as fallback since CUSIP
    resolution is best-effort.

    Returns:
        List of dicts sorted by value_usd desc:
        {
          "fund_name": str,
          "cik": str,
          "shares": int,
          "value_usd": int,
          "pct_of_portfolio": float,
          "reported_date": str,
          "change_vs_prior": str | None,
        }
    """
    funds = tracked_funds()
    ticker_upper = ticker.upper()

    # Build a name-fragment lookup: "NVDA" → try matching "NVIDIA" in issuer name.
    # 13F issuer names are long-form (e.g. "NVIDIA CORP"), not ticker symbols.
    # We match if the query ticker appears anywhere in the resolved name OR if
    # a well-known abbreviation maps to the full company name.
    _TICKER_NAME_HINTS: dict[str, str] = {
        "NVDA": "NVIDIA", "AAPL": "APPLE", "MSFT": "MICROSOFT", "GOOGL": "ALPHABET",
        "GOOG": "ALPHABET", "AMZN": "AMAZON", "META": "META PLATFORMS",
        "TSLA": "TESLA", "NFLX": "NETFLIX", "AMD": "ADVANCED MICRO",
        "INTC": "INTEL", "CRM": "SALESFORCE", "ORCL": "ORACLE",
        "BRKB": "BERKSHIRE", "BRKA": "BERKSHIRE", "JPM": "JPMORGAN",
        "BAC": "BANK AMERICA", "WFC": "WELLS FARGO", "GS": "GOLDMAN",
        "OXY": "OCCIDENTAL", "CVX": "CHEVRON", "XOM": "EXXON",
    }
    name_fragment = _TICKER_NAME_HINTS.get(ticker_upper, ticker_upper)

    def _matches(h_ticker: str) -> bool:
        ht = h_ticker.upper()
        # Exact ticker match (handles cases where CUSIP resolved to a ticker)
        if ht == ticker_upper:
            return True
        # Ticker appears in the resolved name (e.g. "NVDA" in "NVIDIA CORP" → False,
        # but name_fragment "NVIDIA" in "NVIDIA CORP" → True)
        if name_fragment and name_fragment in ht:
            return True
        # Resolved name starts with the query (e.g. "APPLE" matches "APPLE INC")
        if ht.startswith(ticker_upper):
            return True
        return False

    matches: list[dict] = []

    for fund_name, cik in funds.items():
        holdings = get_fund_holdings(cik)
        for h in holdings:
            if _matches(h.ticker):
                matches.append({
                    "fund_name": fund_name,
                    "cik": cik,
                    "shares": h.shares,
                    "value_usd": h.value_usd,
                    "pct_of_portfolio": h.pct_of_portfolio,
                    "reported_date": h.reported_date,
                    "change_vs_prior": h.change_vs_prior,
                })
                break  # One entry per fund

    matches.sort(key=lambda x: x["value_usd"], reverse=True)
    return matches


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point — `python -m research.institutional_tracking TICKER`
# ─────────────────────────────────────────────────────────────────────────────

def _cli() -> None:
    import sys
    import argparse

    # Detect mode from first positional arg before argparse subparser conflicts.
    # If the first non-flag arg is not a known subcommand, treat it as a ticker.
    _known_subcommands = {"smart-money", "fund"}
    _first_arg = next((a for a in sys.argv[1:] if not a.startswith("-")), None)
    _is_ticker_mode = _first_arg is not None and _first_arg.upper() not in {
        s.upper() for s in _known_subcommands
    }

    parser = argparse.ArgumentParser(
        description="Atlas institutional tracker — 13F smart money via SEC EDGAR"
    )

    if _is_ticker_mode:
        parser.add_argument("ticker", help="Ticker to look up (who_owns mode)")
        args = parser.parse_args()
        args.command = None
    else:
        sub = parser.add_subparsers(dest="command")
        sub.add_parser("smart-money", help="Show top 20 smart money consensus positions")
        fund_cmd = sub.add_parser("fund", help="Show holdings for a specific fund")
        fund_cmd.add_argument("name_or_cik", help="Fund name fragment or CIK")
        args = parser.parse_args()
        args.ticker = None

    if args.command == "smart-money":
        print(f"\n{'='*70}")
        print(f"  ATLAS SMART MONEY CONSENSUS — TOP 20 POSITIONS")
        print(f"  Source: SEC EDGAR Form 13F | Tracked funds: {len(tracked_funds())}")
        print(f"{'='*70}\n")
        top = what_are_smart_money_buying(20)
        if not top:
            print("No data available. EDGAR may be unavailable.")
            return
        print(f"  {'TICKER':<25} {'FUNDS':>5} {'TOTAL VALUE':>15} {'AVG PORT%':>9}")
        print(f"  {'-'*25} {'-'*5} {'-'*15} {'-'*9}")
        for i, item in enumerate(top, 1):
            print(
                f"  {i:2}. {item['ticker']:<21} "
                f"{item['fund_count']:>5} "
                f"${item['total_value_usd']:>13,.0f} "
                f"{item['avg_pct_of_portfolio']:>8.2f}%"
            )
        print(f"\n{'='*70}")
        print("Note: 45-day filing delay. Positions may have changed.")
        print("Academic basis: Dasgupta, Prat & Verardo (2011) JoF")
        print(f"{'='*70}\n")
        return

    if args.command == "fund":
        query = args.name_or_cik.lower()
        funds = tracked_funds()
        target_cik = None
        target_name = None
        for name, cik in funds.items():
            if query in name.lower() or query == cik:
                target_cik = cik
                target_name = name
                break
        if not target_cik:
            print(f"Fund not found for query: {args.name_or_cik}")
            print("Tracked funds:", ", ".join(funds.keys()))
            return
        print(f"\n{'='*70}")
        print(f"  13F HOLDINGS: {target_name}")
        print(f"  CIK: {target_cik} | Source: SEC EDGAR Form 13F")
        print(f"{'='*70}\n")
        holdings = get_fund_holdings(target_cik)
        if not holdings:
            print("No holdings found.")
            return
        print(f"  {'SECURITY':<30} {'SHARES':>12} {'VALUE (USD)':>15} {'WEIGHT%':>8}")
        print(f"  {'-'*30} {'-'*12} {'-'*15} {'-'*8}")
        for h in holdings[:30]:
            print(
                f"  {h.ticker:<30} "
                f"{h.shares:>12,} "
                f"${h.value_usd:>13,.0f} "
                f"{(h.pct_of_portfolio or 0):>7.2f}%"
            )
        total = sum(h.value_usd for h in holdings)
        print(f"\n  Total portfolio value: ${total:,.0f}")
        print(f"  Total positions: {len(holdings)}")
        print(f"  As of: {holdings[0].reported_date if holdings else 'unknown'}")
        return

    # Default: who_owns mode
    ticker = getattr(args, "ticker", None)
    if not ticker:
        print("Usage: python -m research.institutional_tracking TICKER")
        print("       python -m research.institutional_tracking smart-money")
        print("       python -m research.institutional_tracking fund BUFFETT")
        return

    ticker = ticker.upper()
    print(f"\n{'='*70}")
    print(f"  ATLAS INSTITUTIONAL TRACKER — {ticker}")
    print(f"  Source: SEC EDGAR Form 13F | Funds tracked: {len(tracked_funds())}")
    print(f"{'='*70}\n")

    owners = who_owns(ticker)
    if not owners:
        print(f"No tracked funds hold {ticker} in their most recent 13F.\n")
        print("Note: CUSIP resolution is best-effort. Try the full company name")
        print("or check the smart-money consensus for broader coverage.")
    else:
        print(f"  {'FUND':<40} {'SHARES':>12} {'VALUE (USD)':>14} {'PORT%':>7}")
        print(f"  {'-'*40} {'-'*12} {'-'*14} {'-'*7}")
        for o in owners:
            print(
                f"  {o['fund_name']:<40} "
                f"{o['shares']:>12,} "
                f"${o['value_usd']:>12,.0f} "
                f"{(o['pct_of_portfolio'] or 0):>6.2f}%"
            )
        total_val = sum(o["value_usd"] for o in owners)
        print(f"\n  Tracked funds holding {ticker}: {len(owners)}")
        print(f"  Combined tracked-fund value: ${total_val:,.0f}")
        print(f"  (As of most recent 13F for each fund)")

    print(f"\n{'='*70}")
    print("Note: 13F has 45-day delay. Treat as conviction signal, not real-time.")
    print("Academic basis: Wermers (2000) JoF, Jiang et al. (2007) JFE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    _cli()
