"""
utils/market_hours.py
---------------------
Market Session Awareness for Atlas Trading Agent.

Major trading sessions (all times UTC)
---------------------------------------
  Asian      00:00 – 09:00  (Tokyo sub-session: 00:00 – 06:00)
  London     07:00 – 16:00
  New York   13:30 – 20:00
  Overlap    13:30 – 16:00  (London/NY overlap — highest forex + crypto volume)

Crypto markets trade 24/7 but their volatility and liquidity closely follow
the sessions above.  Strategies can use is_high_volume_period() to filter
entries to periods of deeper liquidity.

Traditional exchange open/close times are also provided for stock-specific
strategies via is_market_open().

Usage
-----
    from utils.market_hours import MarketHours, TradingSession

    hours   = MarketHours()
    session = hours.current_session()
    if hours.is_high_volume_period():
        # prefer trading here
    next_open = hours.next_session_open(TradingSession.LONDON)
"""

from __future__ import annotations

import logging
from datetime import datetime, time, timedelta, timezone
from enum import Enum

logger = logging.getLogger("atlas.market_hours")

# ---------------------------------------------------------------------------
# Session definitions
# ---------------------------------------------------------------------------
# All times are UTC.  Each session is (open_hour, open_minute, close_hour, close_minute).

_SESSION_TIMES: dict[str, tuple[int, int, int, int]] = {
    "ASIAN": (0, 0, 9, 0),
    "TOKYO": (0, 0, 6, 0),      # subset of Asian
    "LONDON": (7, 0, 16, 0),
    "NEW_YORK": (13, 30, 20, 0),
    "OVERLAP": (13, 30, 16, 0),  # London/NY overlap
}

# Traditional exchanges (non-crypto) open hours in UTC
# These vary by DST — approximations used here (EST/EDT not accounted for precisely)
_EXCHANGE_HOURS_UTC: dict[str, tuple[int, int, int, int]] = {
    "NYSE": (14, 30, 21, 0),      # 9:30 AM – 4:00 PM EST
    "NASDAQ": (14, 30, 21, 0),
    "LSE": (8, 0, 16, 30),        # London Stock Exchange
    "TSX": (14, 30, 21, 0),       # Toronto Stock Exchange
    "ASX": (0, 0, 7, 0),          # Australian Securities Exchange
}


# ---------------------------------------------------------------------------
# TradingSession enum
# ---------------------------------------------------------------------------


class TradingSession(str, Enum):
    ASIAN = "ASIAN"
    TOKYO = "TOKYO"
    LONDON = "LONDON"
    NEW_YORK = "NEW_YORK"
    OVERLAP = "OVERLAP"
    OFF_HOURS = "OFF_HOURS"


# ---------------------------------------------------------------------------
# MarketHours
# ---------------------------------------------------------------------------


class MarketHours:
    """
    Utility class for session-aware trading decisions.

    All calculations are based on UTC time.  Pass ``now`` to all methods
    to override the current time (useful for backtesting).
    """

    # ------------------------------------------------------------------
    # Core session queries
    # ------------------------------------------------------------------

    def current_session(self, now: datetime | None = None) -> TradingSession:
        """
        Return the primary active trading session.

        Priority order when multiple sessions overlap:
          OVERLAP > NEW_YORK > LONDON > ASIAN > OFF_HOURS

        Parameters
        ----------
        now : UTC datetime to evaluate; defaults to datetime.now(UTC)

        Returns
        -------
        TradingSession enum value
        """
        utc_now = self._utc_now(now)

        if self._in_session("OVERLAP", utc_now):
            return TradingSession.OVERLAP
        if self._in_session("NEW_YORK", utc_now):
            return TradingSession.NEW_YORK
        if self._in_session("LONDON", utc_now):
            return TradingSession.LONDON
        if self._in_session("ASIAN", utc_now):
            return TradingSession.ASIAN
        return TradingSession.OFF_HOURS

    def active_sessions(self, now: datetime | None = None) -> list[TradingSession]:
        """
        Return ALL sessions that are currently active (there can be multiple
        during overlapping periods).
        """
        utc_now = self._utc_now(now)
        active: list[TradingSession] = []
        session_map = {
            TradingSession.ASIAN: "ASIAN",
            TradingSession.TOKYO: "TOKYO",
            TradingSession.LONDON: "LONDON",
            TradingSession.NEW_YORK: "NEW_YORK",
            TradingSession.OVERLAP: "OVERLAP",
        }
        for session, key in session_map.items():
            if self._in_session(key, utc_now):
                active.append(session)
        if not active:
            active.append(TradingSession.OFF_HOURS)
        return active

    def is_high_volume_period(self, now: datetime | None = None) -> bool:
        """
        Return True during the periods that historically carry the deepest
        liquidity and tightest spreads.

        High-volume periods:
          • London/NY overlap (13:30 – 16:00 UTC) — peak forex volume
          • New York session (13:30 – 20:00 UTC) — US equities and crypto
          • London session open (07:00 – 09:00 UTC) — European open spike
        """
        utc_now = self._utc_now(now)
        session = self.current_session(utc_now)
        if session in (TradingSession.OVERLAP, TradingSession.NEW_YORK):
            return True
        # London open (first 2 hours)
        if self._in_session("LONDON", utc_now):
            open_h, open_m, _, _ = _SESSION_TIMES["LONDON"]
            london_open = utc_now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
            if (utc_now - london_open).total_seconds() < 7200:
                return True
        return False

    def next_session_open(
        self,
        session: TradingSession,
        now: datetime | None = None,
    ) -> datetime:
        """
        Return the next UTC datetime when the given session opens.

        If the session is currently open, returns the NEXT opening
        (i.e. tomorrow's open time).

        Parameters
        ----------
        session : the session to query
        now     : UTC reference time; defaults to datetime.now(UTC)

        Returns
        -------
        UTC-aware datetime of the next session open
        """
        utc_now = self._utc_now(now)
        key = session.value if session != TradingSession.OFF_HOURS else "ASIAN"
        if key not in _SESSION_TIMES:
            raise ValueError(f"Unknown session: {session}")

        open_h, open_m, close_h, close_m = _SESSION_TIMES[key]
        candidate = utc_now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)

        # If we're already past today's open for this session, move to tomorrow
        if utc_now >= candidate:
            candidate += timedelta(days=1)

        return candidate

    def time_until_session(
        self,
        session: TradingSession,
        now: datetime | None = None,
    ) -> timedelta:
        """Return the time delta until the next open of the given session."""
        utc_now = self._utc_now(now)
        next_open = self.next_session_open(session, utc_now)
        return next_open - utc_now

    # ------------------------------------------------------------------
    # Traditional exchange queries
    # ------------------------------------------------------------------

    def is_market_open(
        self,
        exchange: str,
        now: datetime | None = None,
    ) -> bool:
        """
        Return True if the named traditional exchange is open.

        Parameters
        ----------
        exchange : one of 'NYSE', 'NASDAQ', 'LSE', 'TSX', 'ASX'
                   (case-insensitive)
        now      : UTC reference time; defaults to datetime.now(UTC)

        Returns
        -------
        bool — False for unknown exchanges (safe default)

        Notes
        -----
        DST adjustments are NOT applied.  These are approximate UTC ranges
        suitable for most automated-trading decisions.  Use a proper calendar
        library (pandas_market_calendars) for production-grade holiday and DST
        handling.
        """
        utc_now = self._utc_now(now)
        key = exchange.upper()
        hours = _EXCHANGE_HOURS_UTC.get(key)
        if hours is None:
            logger.warning("Unknown exchange '%s' — assuming closed", exchange)
            return False

        open_h, open_m, close_h, close_m = hours

        # Weekends: Mon=0 … Sun=6
        if utc_now.weekday() >= 5:
            return False

        current_time = utc_now.time()
        open_time = time(open_h, open_m)
        close_time = time(close_h, close_m)
        return open_time <= current_time < close_time

    def session_info(self, now: datetime | None = None) -> dict[str, object]:
        """
        Return a comprehensive session snapshot — useful for dashboards
        and strategy context injection.

        Returns
        -------
        dict with keys:
            utc_time        — current UTC time as ISO string
            primary_session — TradingSession value
            active_sessions — list of active TradingSession values
            is_high_volume  — bool
            crypto_open     — always True (24/7)
            nyse_open       — bool
            lse_open        — bool
        """
        utc_now = self._utc_now(now)
        return {
            "utc_time": utc_now.isoformat(),
            "primary_session": self.current_session(utc_now).value,
            "active_sessions": [s.value for s in self.active_sessions(utc_now)],
            "is_high_volume": self.is_high_volume_period(utc_now),
            "crypto_open": True,
            "nyse_open": self.is_market_open("NYSE", utc_now),
            "lse_open": self.is_market_open("LSE", utc_now),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _utc_now(override: datetime | None) -> datetime:
        """Return override if provided, else UTC now (timezone-aware)."""
        if override is not None:
            if override.tzinfo is None:
                # Assume UTC if tz-naive
                return override.replace(tzinfo=timezone.utc)
            return override.astimezone(timezone.utc)
        return datetime.now(tz=timezone.utc)

    @staticmethod
    def _in_session(key: str, utc_dt: datetime) -> bool:
        """Return True when utc_dt falls within the named session window."""
        hours = _SESSION_TIMES.get(key)
        if hours is None:
            return False
        open_h, open_m, close_h, close_m = hours
        current = utc_dt.time().replace(tzinfo=None)
        open_t = time(open_h, open_m)
        close_t = time(close_h, close_m)

        if open_t < close_t:
            # Normal case: does not cross midnight
            return open_t <= current < close_t
        else:
            # Crosses midnight (e.g. ASIAN starts at 00:00 and the end wraps)
            return current >= open_t or current < close_t
