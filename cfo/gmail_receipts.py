"""
cfo/gmail_receipts.py
---------------------
IMAP receipt puller for CC's Google Workspace Gmail (conaugh@oasisai.work).

Connects directly via imaplib (SSL, port 993) using an App Password — no
Google OAuth, no Google API library. This keeps the dependency footprint at
zero and works indefinitely without token rotation.

Purpose: pull business receipts / income invoices from labelled Gmail folders,
parse dollar amounts, classify by expense category, and export to CSV for
CRA T2125 sole-proprietor tax filing.

Gmail labels used:
    "Business Expenses"       (Label_3)
    "Income & Invoices"       (Label_4)
    "Software & Subscriptions" (Label_2) — may have migrated into Business Expenses

IMAP label quirk: Gmail exposes custom labels as selectable IMAP mailboxes.
Spaces in names must be quoted.  The connection.select('"Label Name"') form
handles this.  Gmail also supports X-GM-RAW search (Gmail query syntax) but
we use standard IMAP SINCE/BEFORE criteria for portability.
"""

from __future__ import annotations

import csv
import imaplib
import logging
import os
import re
import email as email_lib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from email.header import decode_header
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from project root so credentials are available when running
# this module directly (python -m cfo.gmail_receipts) or imported from tests.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

# Heuristic: when multiple amounts appear in a receipt, keywords near an amount
# signal it is the "final" charge rather than a line-item or subtotal.
_TOTAL_KEYWORDS = re.compile(
    r"(total|amount charged|amount due|grand total|charged|you paid|payment of|invoice total)",
    re.IGNORECASE,
)

# Regex patterns for extracting monetary amounts.
# Order matters: more-specific patterns first.
_AMOUNT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # ─── Currency-prefix formats ───
    # "CA$158.20" (Stripe/Anthropic shorthand), "CAD $12.50", "CAD12.50"
    ("CAD", re.compile(r"(?:CAD|CA\$)\s*\$?\s*(\d{1,6}(?:[,\s]\d{3})*(?:\.\d{2})?)", re.IGNORECASE)),
    # "US$20", "USD 12.50", "USD $12.50"
    ("USD", re.compile(r"(?:USD|US\$)\s*\$?\s*(\d{1,6}(?:[,\s]\d{3})*(?:\.\d{2})?)", re.IGNORECASE)),
    # "€12.50", "EUR 12.50"
    ("EUR", re.compile(r"(?:€|EUR\s*)\s*(\d{1,6}(?:[,\s]\d{3})*(?:\.\d{2})?)", re.IGNORECASE)),
    # "£12.50", "GBP 12.50"
    ("GBP", re.compile(r"(?:£|GBP\s*)\s*(\d{1,6}(?:[,\s]\d{3})*(?:\.\d{2})?)", re.IGNORECASE)),
    # Plain "$12.50" — assumed CAD unless context says otherwise
    ("CAD", re.compile(r"\$\s*(\d{1,6}(?:[,\s]\d{3})*(?:\.\d{2})?)")),
    # ─── Currency-suffix formats (table layouts: "17.99\nUSD") ───
    # Require decimal (.\d{2}) to avoid matching line-numbers or IDs.
    # \s+ matches newlines so these catch "number on one line, currency on the next".
    ("CAD", re.compile(r"(\d{1,6}(?:[,\s]\d{3})*\.\d{2})\s+CAD\b", re.IGNORECASE)),
    ("USD", re.compile(r"(\d{1,6}(?:[,\s]\d{3})*\.\d{2})\s+USD\b", re.IGNORECASE)),
    ("EUR", re.compile(r"(\d{1,6}(?:[,\s]\d{3})*\.\d{2})\s+EUR\b", re.IGNORECASE)),
    ("GBP", re.compile(r"(\d{1,6}(?:[,\s]\d{3})*\.\d{2})\s+GBP\b", re.IGNORECASE)),
]

# Classifier keyword maps: (regex_pattern -> category_string)
_CLASSIFY_RULES: list[tuple[re.Pattern[str], str]] = [
    # AI tooling
    (re.compile(r"anthropic|openai|claude|chatgpt|perplexity|midjourney|stability", re.IGNORECASE), "ai_tools"),
    # Hosting / cloud infra
    (re.compile(r"hostinger|vercel|netlify|cloudflare|digitalocean|linode|vultr|aws|amazon web|google cloud|azure", re.IGNORECASE), "hosting_cloud"),
    # General software / SaaS subscriptions
    (re.compile(r"github|gitlab|notion|linear|figma|canva|adobe|microsoft|google workspace|gsuite|zapier|make\.com|airtable|slack|zoom|loom|calendly|typeform|stripe atlas", re.IGNORECASE), "software_subscription"),
    # Payment processors — these generate both income receipts and fee notices
    (re.compile(r"stripe|wise|paypal|square|shopify payments|woocommerce|gumroad|lemonsqueezy|paddle", re.IGNORECASE), "payment_processor_fee"),
    # Income / invoices
    (re.compile(r"invoice|payment received|e-transfer|etransfer|deposit|paid in full|receipt of payment|your payment", re.IGNORECASE), "payment_received"),
    # Meals / food
    (re.compile(r"uber eats|doordash|skip the dishes|restaurant|café|coffee|tim hortons|starbucks|mcdonald", re.IGNORECASE), "meals"),
    # Travel
    (re.compile(r"air canada|westjet|porter|via rail|airbnb|hotel|motel|inn|uber|lyft|taxi|parking", re.IGNORECASE), "travel"),
    # Office supplies / equipment
    (re.compile(r"staples|best buy|apple store|amazon|newegg|office depot|best buy", re.IGNORECASE), "office_supplies"),
]

# ─────────────────────────────────────────────────────────────────────────────
#  Data model
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Receipt:
    """Parsed representation of a single email receipt or invoice."""

    date: date
    from_addr: str
    subject: str
    amount_cad: Optional[float]        # None when parsing failed
    amount_raw: Optional[float]        # Original amount before conversion
    currency: Optional[str]            # ISO currency code, e.g. "USD"
    vendor: str                        # Best-effort extracted sender name
    category: str                      # One of the classify() output values
    attachments: list[str] = field(default_factory=list)   # Attachment filenames only
    raw_body_preview: str = ""         # First 500 chars of plain-text body
    gmail_message_id: str = ""         # For deduplication


# ─────────────────────────────────────────────────────────────────────────────
#  Core class
# ─────────────────────────────────────────────────────────────────────────────


class GmailReceipts:
    """
    IMAP client for pulling receipt / invoice emails from CC's Google Workspace.

    Credentials are read from environment variables:
        GMAIL_USER         — e.g. conaugh@oasisai.work
        GMAIL_APP_PASSWORD — Google Workspace App Password (16-char, no spaces)

    Usage:
        gr = GmailReceipts()
        labels = gr.list_labels()
        receipts = gr.fetch_label("Business Expenses", since=date(2026, 1, 1))
        gr.export_csv(receipts, "data/receipts_2026.csv")
    """

    def __init__(self) -> None:
        self._user = os.environ.get("GMAIL_USER", "")
        self._password = os.environ.get("GMAIL_APP_PASSWORD", "")
        if not self._user or not self._password:
            raise EnvironmentError(
                "GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env. "
                "Generate an App Password at: myaccount.google.com/apppasswords"
            )
        self._conn: Optional[imaplib.IMAP4_SSL] = None
        # Persistent parse cache keyed by Gmail Message-ID. Skips the expensive
        # RFC822 fetch + pdfplumber extraction for receipts we've already parsed.
        self._cache_path = Path(__file__).resolve().parents[1] / "data" / "receipts_cache.json"
        self._cache: dict[str, dict] = self._load_cache()

    def _load_cache(self) -> dict[str, dict]:
        if not self._cache_path.exists():
            return {}
        try:
            import json as _json
            return _json.loads(self._cache_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Receipt cache unreadable — starting fresh: %s", exc)
            return {}

    def _save_cache(self) -> None:
        """Atomic write so a reader never catches a half-written cache."""
        import json as _json
        import tempfile

        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(
            prefix="receipts_", suffix=".json.tmp", dir=str(self._cache_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                _json.dump(self._cache, f, indent=2, default=str)
            os.replace(tmp, self._cache_path)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    # ── Connection management ─────────────────────────────────────────────────

    def connect(self) -> None:
        """Open an SSL IMAP connection and authenticate with the App Password."""
        self._conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        self._conn.login(self._user, self._password)
        logger.info("IMAP connected as %s", self._user)

    def disconnect(self) -> None:
        """Gracefully close the IMAP connection."""
        if self._conn:
            try:
                self._conn.logout()
            except Exception:
                pass  # Already disconnected — not a problem
            self._conn = None

    def __enter__(self) -> "GmailReceipts":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.disconnect()

    def _ensure_connected(self) -> imaplib.IMAP4_SSL:
        """Return the live connection, reconnecting if the session dropped."""
        if self._conn is None:
            self.connect()
        assert self._conn is not None
        return self._conn

    # ── Label discovery ───────────────────────────────────────────────────────

    def list_labels(self) -> list[str]:
        """
        Return all IMAP mailbox names (Gmail labels) available on this account.

        Useful for debugging — call this first to confirm the exact string
        Gmail uses for each label (capitalisation matters for IMAP SELECT).
        """
        conn = self._ensure_connected()
        status, raw_list = conn.list()
        if status != "OK":
            raise RuntimeError(f"IMAP LIST failed: {status}")

        labels: list[str] = []
        for entry in raw_list or []:
            # Each entry is bytes like: b'(\\HasNoChildren) "/" "Business Expenses"'
            decoded = entry.decode("utf-8", errors="replace") if isinstance(entry, bytes) else entry
            # Extract the final quoted or unquoted name after the delimiter
            match = re.search(r'"([^"]+)"\s*$', decoded)
            if match:
                labels.append(match.group(1))
            else:
                # Unquoted name (no spaces)
                parts = decoded.rsplit(" ", 1)
                if parts:
                    labels.append(parts[-1].strip())

        return sorted(labels)

    # ── Fetching ──────────────────────────────────────────────────────────────

    def fetch_label(
        self,
        label: str,
        since: Optional[date] = None,
    ) -> list[Receipt]:
        """
        Pull all messages from a Gmail label since an optional date.

        Gmail label names with spaces must be double-quoted for IMAP SELECT.
        This method handles that automatically — pass the plain label name.

        Args:
            label: Gmail label as shown in the UI, e.g. "Business Expenses".
            since: Only fetch messages on or after this date. Default = all.

        Returns:
            List of parsed Receipt objects. Failures are logged and skipped.
        """
        conn = self._ensure_connected()

        # IMAP requires labels with spaces to be double-quoted.
        quoted_label = f'"{label}"' if " " in label else label
        status, _ = conn.select(quoted_label, readonly=True)
        if status != "OK":
            logger.warning("Could not SELECT label %r — trying with escaped name", label)
            # Some Gmail configurations use [Gmail]/... prefix; try without quotes
            status, _ = conn.select(label, readonly=True)
            if status != "OK":
                raise RuntimeError(
                    f"Cannot open Gmail label {label!r}. "
                    "Run list_labels() to confirm the exact name."
                )

        # Build IMAP search criteria
        if since:
            # IMAP SINCE date format: "01-Jan-2026"
            imap_date = since.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE "{imap_date}")'
        else:
            search_criteria = "ALL"

        status, data = conn.search(None, search_criteria)
        if status != "OK":
            logger.warning("SEARCH on label %r returned non-OK: %s", label, status)
            return []

        message_ids: list[bytes] = data[0].split() if data[0] else []
        logger.info("Label %r: %d messages found", label, len(message_ids))

        receipts: list[Receipt] = []
        cache_hits = 0
        cache_misses = 0
        for msg_id in message_ids:
            try:
                # Cheap header-only fetch to check the dedup cache before paying
                # for RFC822 body + pdfplumber extraction.
                hdr_status, hdr_data = conn.fetch(
                    msg_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])"
                )
                gm_message_id = ""
                if hdr_status == "OK" and hdr_data and hdr_data[0]:
                    hdr_bytes = hdr_data[0][1] if isinstance(hdr_data[0], tuple) else b""
                    if isinstance(hdr_bytes, bytes):
                        for line in hdr_bytes.decode("utf-8", errors="replace").splitlines():
                            if line.lower().startswith("message-id:"):
                                gm_message_id = line.split(":", 1)[1].strip()
                                break

                if gm_message_id and gm_message_id in self._cache:
                    cache_hits += 1
                    c = self._cache[gm_message_id]
                    # Reconstruct Receipt from cache — skip IMAP body fetch + PDF parse
                    receipts.append(Receipt(
                        date=date.fromisoformat(c["date"]),
                        from_addr=c["from_addr"],
                        subject=c["subject"],
                        amount_cad=c.get("amount_cad"),
                        amount_raw=c.get("amount_raw"),
                        currency=c.get("currency"),
                        vendor=c.get("vendor", ""),
                        category=c.get("category", "unknown"),
                        attachments=c.get("attachments", []),
                        raw_body_preview=c.get("raw_body_preview", ""),
                        gmail_message_id=gm_message_id,
                    ))
                    continue

                # Cache miss — do full parse
                cache_misses += 1
                receipt = self._fetch_single(conn, msg_id)
                if receipt:
                    receipts.append(receipt)
                    # Write to cache only if parse succeeded AND we have a stable ID
                    if receipt.gmail_message_id:
                        self._cache[receipt.gmail_message_id] = {
                            "date": receipt.date.isoformat(),
                            "from_addr": receipt.from_addr,
                            "subject": receipt.subject,
                            "amount_cad": receipt.amount_cad,
                            "amount_raw": receipt.amount_raw,
                            "currency": receipt.currency,
                            "vendor": receipt.vendor,
                            "category": receipt.category,
                            "attachments": list(receipt.attachments),
                            "raw_body_preview": receipt.raw_body_preview,
                            "cached_at": datetime.now().isoformat(timespec="seconds"),
                        }
            except Exception as exc:
                logger.warning("Failed to parse message %s: %s", msg_id, exc)

        # Persist cache at end of label fetch so next run skips already-parsed msgs
        if cache_misses:
            try:
                self._save_cache()
                logger.info(
                    "Label %r: %d cache hits, %d fresh parses — cache saved",
                    label, cache_hits, cache_misses,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not save receipt cache: %s", exc)
        elif cache_hits:
            logger.info("Label %r: all %d from cache (no fresh parses)", label, cache_hits)

        return receipts

    def _fetch_single(self, conn: imaplib.IMAP4_SSL, msg_id: bytes) -> Optional[Receipt]:
        """
        Fetch and parse one message by its IMAP sequence number.

        We fetch RFC822 (full message) rather than individual headers because
        we also need the body text for amount extraction.
        """
        status, raw_data = conn.fetch(msg_id, "(RFC822)")
        if status != "OK" or not raw_data or raw_data[0] is None:
            return None

        # raw_data is a list of tuples; the message bytes are in [0][1]
        raw_bytes = raw_data[0][1]
        if not isinstance(raw_bytes, bytes):
            return None

        msg = email_lib.message_from_bytes(raw_bytes)

        # ── Date ──────────────────────────────────────────────────────────────
        date_str = msg.get("Date", "")
        msg_date = _parse_email_date(date_str)

        # ── From / vendor ─────────────────────────────────────────────────────
        from_raw = msg.get("From", "")
        from_addr = _decode_header_str(from_raw)
        vendor = _extract_vendor(from_addr)

        # ── Subject ───────────────────────────────────────────────────────────
        subject = _decode_header_str(msg.get("Subject", "(no subject)"))

        # ── Body + attachments + per-PDF text ─────────────────────────────────
        body_text, attachments, pdf_texts = _extract_body_attachments_and_pdfs(msg)
        preview = body_text[:500].strip()

        # ── Amount parsing ────────────────────────────────────────────────────
        # When an email carries multiple PDFs (forwarded "3 receipts" batches),
        # parse each PDF separately and sum — otherwise we'd only capture the
        # largest single amount. Single-PDF / no-PDF emails fall through to the
        # standard whole-body parse.
        if len(pdf_texts) > 1:
            amounts: list[tuple[float, str]] = []
            for pdf_text in pdf_texts:
                amt, cur = self.parse_amount(subject, pdf_text)
                if amt is not None and cur is not None:
                    amounts.append((amt, cur))
            if amounts:
                # All PDFs in one email are typically the same currency;
                # group by currency, sum each, convert each to CAD, then sum.
                by_cur: dict[str, float] = defaultdict(float)
                for amt, cur in amounts:
                    by_cur[cur] += amt
                amount_cad = sum(_to_cad_approx(v, c) for c, v in by_cur.items())
                # Keep amount_raw / currency as the dominant currency's total
                dominant_cur = max(by_cur, key=by_cur.get)
                amount_raw = by_cur[dominant_cur]
                currency = dominant_cur
            else:
                amount_raw, currency, amount_cad = None, None, None
        else:
            amount_raw, currency = self.parse_amount(subject, body_text)
            amount_cad = _to_cad_approx(amount_raw, currency) if amount_raw is not None else None

        # ── Category ──────────────────────────────────────────────────────────
        category = self.classify(subject, from_addr)

        # ── Message-ID for deduplication ──────────────────────────────────────
        message_id = msg.get("Message-ID", "").strip()

        return Receipt(
            date=msg_date,
            from_addr=from_addr,
            subject=subject,
            amount_cad=amount_cad,
            amount_raw=amount_raw,
            currency=currency,
            vendor=vendor,
            category=category,
            attachments=attachments,
            raw_body_preview=preview,
            gmail_message_id=message_id,
        )

    # ── Parsing helpers ───────────────────────────────────────────────────────

    @staticmethod
    def parse_amount(subject: str, body: str) -> tuple[Optional[float], Optional[str]]:
        """
        Extract a monetary amount and currency code from subject + body text.

        Strategy:
        1. Split the combined text into lines.
        2. For each pattern (CAD > USD > EUR > GBP > plain $), collect all matches
           along with whether the line contains a "total" keyword.
        3. Prefer the amount on a line containing a total keyword.
        4. If multiple total-line amounts, take the largest (most conservative for
           expense claims — avoids claiming only a subtotal).
        5. Fall back to the largest match across all lines.

        Returns (amount, currency_code) or (None, None) on failure.
        """
        combined = f"{subject}\n{body}"

        # Collect (amount_float, currency, is_total_line) for every match
        candidates: list[tuple[float, str, bool]] = []

        for currency_code, pattern in _AMOUNT_PATTERNS:
            for match in pattern.finditer(combined):
                raw_str = match.group(1).replace(",", "").replace(" ", "")
                try:
                    value = float(raw_str)
                except ValueError:
                    continue
                if value <= 0 or value > 500_000:
                    # Sanity gate: ignore obviously wrong values
                    continue

                # Check whether this match sits on a "total" line
                line_start = combined.rfind("\n", 0, match.start()) + 1
                line_end = combined.find("\n", match.end())
                line = combined[line_start: line_end if line_end != -1 else None]
                is_total = bool(_TOTAL_KEYWORDS.search(line))

                candidates.append((value, currency_code, is_total))

        if not candidates:
            return None, None

        total_candidates = [(v, c) for v, c, t in candidates if t]
        if total_candidates:
            # Take the largest amount on a "total" line — most likely the charge
            best = max(total_candidates, key=lambda x: x[0])
            return best[0], best[1]

        # No total-keyword line found — fall back to the largest amount overall
        best_fallback = max(candidates, key=lambda x: x[0])
        return best_fallback[0], best_fallback[1]

    @staticmethod
    def classify(subject: str, from_addr: str) -> str:
        """
        Heuristic category classifier for CRA T2125 expense buckets.

        Checks from_addr first (sender domain is a strong signal), then subject.
        Falls back to "other" if no rule matches.

        Categories:
            software_subscription  — SaaS tools (GitHub, Notion, Zoom, etc.)
            hosting_cloud          — Web hosting, CDN, cloud infrastructure
            ai_tools               — AI services (Anthropic, OpenAI, etc.)
            payment_received       — Money coming IN (invoices paid, e-transfers)
            payment_processor_fee  — Stripe/Wise/PayPal fees and receipts
            office_supplies        — Equipment, peripherals, stationery
            meals                  — Food and beverage (50% deductible in Canada)
            travel                 — Flights, accommodation, ground transport
            other                  — Did not match any rule
        """
        haystack = f"{from_addr} {subject}"
        for pattern, category in _CLASSIFY_RULES:
            if pattern.search(haystack):
                return category
        return "other"

    # ── Export ────────────────────────────────────────────────────────────────

    @staticmethod
    def export_csv(receipts: list[Receipt], path: str) -> None:
        """
        Write receipts to a CSV file suitable for import into a T2125 spreadsheet.

        Creates parent directories if they don't exist.
        Overwrites any existing file at the same path.
        """
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "date",
            "vendor",
            "category",
            "amount_cad",
            "amount_raw",
            "currency",
            "subject",
            "from_addr",
            "attachments",
            "raw_body_preview",
            "gmail_message_id",
        ]

        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in receipts:
                writer.writerow({
                    "date": r.date.isoformat() if isinstance(r.date, date) else r.date,
                    "vendor": r.vendor,
                    "category": r.category,
                    "amount_cad": f"{r.amount_cad:.2f}" if r.amount_cad is not None else "",
                    "amount_raw": f"{r.amount_raw:.2f}" if r.amount_raw is not None else "",
                    "currency": r.currency or "",
                    "subject": r.subject,
                    "from_addr": r.from_addr,
                    "attachments": "; ".join(r.attachments),
                    "raw_body_preview": r.raw_body_preview.replace("\n", " "),
                    "gmail_message_id": r.gmail_message_id,
                })

        logger.info("Exported %d receipts to %s", len(receipts), out)

    @staticmethod
    def export_monthly_summary(receipts: list[Receipt]) -> dict[str, dict[str, float]]:
        """
        Aggregate receipts into monthly totals by category.

        Returns a nested dict: { "2026-01": { "ai_tools": 45.00, ... }, ... }
        Only sums receipts where amount_cad is known.  Unknown amounts are
        counted separately so CC can review them manually.
        """
        # month_key -> category -> total_cad
        summary: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        missing: dict[str, int] = defaultdict(int)  # month -> count with no amount

        for r in receipts:
            month_key = (
                r.date.strftime("%Y-%m")
                if isinstance(r.date, date)
                else str(r.date)[:7]
            )
            if r.amount_cad is not None:
                summary[month_key][r.category] += r.amount_cad
            else:
                missing[month_key] += 1

        # Log months with unparsed amounts so CC knows to review them
        for month, count in missing.items():
            logger.warning(
                "%s: %d receipt(s) had no parseable amount — review manually", month, count
            )

        # Convert inner defaultdicts to plain dicts for clean serialisation
        return {k: dict(v) for k, v in sorted(summary.items())}


# ─────────────────────────────────────────────────────────────────────────────
#  Private helpers
# ─────────────────────────────────────────────────────────────────────────────


def _decode_header_str(raw: str) -> str:
    """
    Decode an RFC 2047-encoded email header to a plain Unicode string.

    Headers like =?utf-8?b?...?= or =?iso-8859-1?q?...?= are common in
    receipts sent from international vendors.
    """
    parts = decode_header(raw)
    decoded_parts: list[str] = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                decoded_parts.append(part.decode(charset or "utf-8", errors="replace"))
            except (LookupError, TypeError):
                decoded_parts.append(part.decode("utf-8", errors="replace"))
        else:
            decoded_parts.append(part)
    return "".join(decoded_parts).strip()


def _parse_email_date(date_str: str) -> date:
    """
    Parse an RFC 2822 email Date header into a Python date.

    Falls back to today if parsing fails — better than crashing on a malformed
    header from a vendor with broken email templates.
    """
    if not date_str:
        return date.today()
    try:
        # email.utils.parsedate_to_datetime handles all RFC 2822 variants
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str).date()
    except Exception:
        # Try a handful of common fallback formats
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(date_str[:30], fmt).date()
            except ValueError:
                continue
    logger.debug("Could not parse date %r — using today", date_str)
    return date.today()


def _extract_vendor(from_addr: str) -> str:
    """
    Extract a human-readable vendor name from an email From header.

    Handles formats like:
        "Anthropic <billing@anthropic.com>"   -> "Anthropic"
        "billing@stripe.com"                  -> "stripe.com"
        "no-reply@accounts.google.com"        -> "google.com"
    """
    # "Display Name <email@domain>" pattern
    name_match = re.match(r'^"?([^"<]+)"?\s*<', from_addr)
    if name_match:
        return name_match.group(1).strip()

    # Plain email — use the domain, stripping common prefixes
    email_match = re.search(r"[\w.+-]+@([\w.-]+)", from_addr)
    if email_match:
        domain = email_match.group(1)
        # Strip subdomains like "mail." "billing." "accounts." for readability
        parts = domain.split(".")
        if len(parts) > 2:
            domain = ".".join(parts[-2:])
        return domain

    return from_addr[:50]  # Last-resort: truncated raw string


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Return extracted text from a PDF attachment. Empty string on failure.

    Uses pdfplumber — handles spacing correctly (PyPDF2's text extraction
    double-spaces every character on many modern PDFs and produces unparseable
    output; pdfplumber gets it right).
    """
    try:
        import io
        import pdfplumber  # type: ignore

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except ImportError:
        logger.warning("pdfplumber not installed — PDF receipts will be skipped. Run: pip install pdfplumber")
        return ""
    except Exception as exc:  # noqa: BLE001
        logger.warning("PDF extraction failed: %s", exc)
        return ""


def _extract_body_attachments_and_pdfs(msg: email_lib.message.Message) -> tuple[str, list[str], list[str]]:
    """Same as _extract_body_and_attachments but also returns per-PDF text
    as a separate list. Used to correctly sum amounts when one email carries
    multiple receipt PDFs (common: forwarded "3 receipts" emails from Claude).
    """
    body, attachments = _extract_body_and_attachments(msg)
    pdf_texts: list[str] = []
    for part in msg.walk():
        if part.get_content_type() == "application/pdf":
            payload = part.get_payload(decode=True)
            if payload:
                text = _extract_pdf_text(payload)
                if text:
                    pdf_texts.append(text)
    return body, attachments, pdf_texts


def _extract_body_and_attachments(msg: email_lib.message.Message) -> tuple[str, list[str]]:
    """
    Walk a MIME message tree, collecting plain-text body + PDF receipt text
    and attachment filenames.

    We prefer text/plain over text/html.  If only HTML is available we strip
    tags with a simple regex rather than pulling in BeautifulSoup.
    PDF attachments are text-extracted via pdfplumber so receipt amounts
    stored in PDFs (common for Anthropic/Stripe auto-generated receipts)
    become parseable. Other attachment types are noted by filename only.
    """
    text_plain: list[str] = []
    text_html: list[str] = []
    pdf_text: list[str] = []
    attachments: list[str] = []

    for part in msg.walk():
        content_type = part.get_content_type()
        disposition = part.get_content_disposition() or ""

        # PDFs — extract text for amount parsing, record filename
        if content_type == "application/pdf":
            fname = part.get_filename()
            if fname:
                attachments.append(_decode_header_str(fname))
            payload = part.get_payload(decode=True)
            if payload:
                extracted = _extract_pdf_text(payload)
                if extracted:
                    pdf_text.append(extracted)
            continue

        # Other attachments — record filename only
        if "attachment" in disposition:
            fname = part.get_filename()
            if fname:
                attachments.append(_decode_header_str(fname))
            continue

        if content_type == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                text_plain.append(payload.decode(charset, errors="replace"))

        elif content_type == "text/html" and not text_plain:
            # Only fall back to HTML if there is no plain-text alternative
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                raw_html = payload.decode(charset, errors="replace")
                # Collapse tags to whitespace so amounts are still parseable
                stripped = re.sub(r"<[^>]+>", " ", raw_html)
                stripped = re.sub(r"\s+", " ", stripped)
                text_html.append(stripped)

    body_parts: list[str] = []
    body_parts.extend(text_plain if text_plain else text_html)
    body_parts.extend(pdf_text)  # PDF text always included — receipts live there
    body = "\n".join(body_parts)
    return body, attachments


# Approximate FX rates for CAD conversion (2026 estimate).
# These are for T2125 filing estimates only — CC should verify with CRA's
# average annual rate for the actual tax year.
_FX_TO_CAD: dict[str, float] = {
    "CAD": 1.0,
    "USD": 1.40,   # ~1.40 CAD per USD (adjust for actual tax year average)
    "EUR": 1.55,
    "GBP": 1.80,
}


def _to_cad_approx(amount: float, currency: Optional[str]) -> float:
    """
    Convert a foreign-currency amount to approximate CAD.

    CRA requires using the Bank of Canada's average annual exchange rate for
    the tax year.  These hardcoded rates are placeholders; CC should update
    them before filing or replace with a live FX lookup.
    """
    if currency is None:
        return amount
    rate = _FX_TO_CAD.get(currency.upper(), 1.0)
    return round(amount * rate, 2)


# ─────────────────────────────────────────────────────────────────────────────
#  CLI entry point
# ─────────────────────────────────────────────────────────────────────────────


def _print_summary_table(summary: dict[str, dict[str, float]]) -> None:
    """Pretty-print the monthly category totals to stdout."""
    all_categories = sorted({cat for month in summary.values() for cat in month})
    col_w = 22

    # Header
    print(f"\n{'Month':<10}", end="")
    for cat in all_categories:
        print(f"  {cat[:col_w]:<{col_w}}", end="")
    print(f"  {'TOTAL':>10}")
    print("-" * (10 + (col_w + 2) * len(all_categories) + 12))

    # Rows
    grand_totals: dict[str, float] = defaultdict(float)
    for month, cats in sorted(summary.items()):
        row_total = sum(cats.values())
        print(f"{month:<10}", end="")
        for cat in all_categories:
            val = cats.get(cat, 0.0)
            grand_totals[cat] += val
            print(f"  ${val:>{col_w - 1}.2f}", end="")
        print(f"  ${row_total:>9.2f}")

    # Totals row
    print("-" * (10 + (col_w + 2) * len(all_categories) + 12))
    print(f"{'TOTAL':<10}", end="")
    for cat in all_categories:
        print(f"  ${grand_totals[cat]:>{col_w - 1}.2f}", end="")
    print(f"  ${sum(grand_totals.values()):>9.2f}\n")


def main() -> None:
    """
    Full sync for the current tax year.

    Pulls from "Business Expenses" and "Income & Invoices", merges, deduplicates
    by Message-ID, writes data/receipts_YYYY.csv, and prints a monthly summary.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    tax_year = date.today().year
    since = date(tax_year, 1, 1)
    csv_path = str(Path(__file__).resolve().parents[1] / "data" / f"receipts_{tax_year}.csv")

    labels = [
        "Business Expenses",
        "Income & Invoices",
        "Software & Subscriptions",  # Legacy label — may be empty
    ]

    all_receipts: list[Receipt] = []
    seen_ids: set[str] = set()

    with GmailReceipts() as gr:
        available = set(gr.list_labels())
        logger.info("Available labels: %s", sorted(available))

        for label in labels:
            if label not in available:
                logger.info("Label %r not found — skipping", label)
                continue
            logger.info("Fetching label: %s (since %s)", label, since)
            fetched = gr.fetch_label(label, since=since)

            for r in fetched:
                # Deduplicate by Message-ID so receipts in multiple labels
                # aren't double-counted (Gmail allows this).
                key = r.gmail_message_id or f"{r.date}|{r.from_addr}|{r.subject}"
                if key not in seen_ids:
                    seen_ids.add(key)
                    all_receipts.append(r)

    logger.info("Total unique receipts: %d", len(all_receipts))

    GmailReceipts.export_csv(all_receipts, csv_path)
    print(f"\nCSV written: {csv_path}")
    print(f"Total receipts: {len(all_receipts)}")

    summary = GmailReceipts.export_monthly_summary(all_receipts)
    _print_summary_table(summary)

    # Warn about receipts with unparsed amounts so CC can review them
    missing = [r for r in all_receipts if r.amount_cad is None]
    if missing:
        print(f"\nWARNING: {len(missing)} receipt(s) had no parseable amount.")
        print("Review these manually in the CSV (amount_cad column is blank):")
        for r in missing[:10]:
            print(f"  {r.date}  {r.vendor:<30}  {r.subject[:60]}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")


if __name__ == "__main__":
    main()
