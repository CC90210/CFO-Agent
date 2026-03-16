"""
data/economic_calendar.py
--------------------------
Economic Calendar for Atlas Trading Agent.

Tracks high-impact macro events that the risk manager should be aware of
before approving trade entries. During these windows the agent should reduce
position sizes or avoid trading entirely.

Hard-coded event schedules (updated annually):
  FOMC rate decisions  — 8 meetings in 2026
  Non-Farm Payrolls    — first Friday of each month
  CPI releases         — roughly the 2nd week of each month

Usage
-----
    cal = EconomicCalendar()
    events = cal.get_upcoming_events(days_ahead=7)
    if cal.is_high_impact_event_today():
        # Reduce position size by 50%
        pass
    fomc_dates = cal.get_fomc_dates()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger("atlas.calendar")


# ---------------------------------------------------------------------------
# EconomicEvent dataclass
# ---------------------------------------------------------------------------


@dataclass
class EconomicEvent:
    """A scheduled market-moving economic event."""

    name: str
    event_date: date
    impact: str          # "HIGH" | "MEDIUM" | "LOW"
    category: str        # "FOMC" | "NFP" | "CPI" | "EARNINGS" | "OTHER"
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "event_date": self.event_date.isoformat(),
            "impact": self.impact,
            "category": self.category,
            "description": self.description,
        }

    @property
    def is_today(self) -> bool:
        return self.event_date == date.today()

    @property
    def days_until(self) -> int:
        return (self.event_date - date.today()).days


# ---------------------------------------------------------------------------
# EconomicCalendar
# ---------------------------------------------------------------------------


class EconomicCalendar:
    """
    Pre-configured economic calendar for 2026.

    Hard-coded dates are sourced from the Federal Reserve and BLS schedules.
    Update the 2027 dates at the start of each year.

    The risk manager should call `is_high_impact_event_today()` before
    approving any trade, and `get_upcoming_events(days_ahead=1)` to
    pre-position for known volatility windows.
    """

    # ------------------------------------------------------------------
    # 2026 FOMC Scheduled Meeting Dates
    # Source: federalreserve.gov/monetarypolicy/fomccalendars.htm
    # ------------------------------------------------------------------
    _FOMC_DATES_2026: list[date] = [
        date(2026, 1, 29),
        date(2026, 3, 19),
        date(2026, 5, 7),
        date(2026, 6, 18),
        date(2026, 7, 30),
        date(2026, 9, 17),
        date(2026, 10, 29),
        date(2026, 12, 10),
    ]

    # ------------------------------------------------------------------
    # 2026 CPI Release Dates (approximate — BLS publishes final dates ~6mo ahead)
    # Source: bls.gov/schedule/news_release/cpi.htm
    # ------------------------------------------------------------------
    _CPI_DATES_2026: list[date] = [
        date(2026, 1, 14),
        date(2026, 2, 11),
        date(2026, 3, 11),
        date(2026, 4, 10),
        date(2026, 5, 13),
        date(2026, 6, 10),
        date(2026, 7, 15),
        date(2026, 8, 12),
        date(2026, 9, 11),
        date(2026, 10, 14),
        date(2026, 11, 12),
        date(2026, 12, 10),
    ]

    # ------------------------------------------------------------------
    # Major earnings dates (fill in as they are announced)
    # ------------------------------------------------------------------
    _MAJOR_EARNINGS_2026: list[tuple[date, str]] = [
        # (date, company)
        # Q4 2025 earnings season (Jan–Feb 2026)
        (date(2026, 1, 27), "AAPL Q1 2026 Earnings"),
        (date(2026, 1, 28), "MSFT Q2 2026 Earnings"),
        (date(2026, 2, 5), "AMZN Q4 2025 Earnings"),
        (date(2026, 2, 19), "NVDA Q4 2025 Earnings"),
        # Q1 2026 earnings season (Apr–May 2026)
        (date(2026, 4, 23), "AAPL Q2 2026 Earnings"),
        (date(2026, 4, 29), "META Q1 2026 Earnings"),
        (date(2026, 4, 30), "MSFT Q3 2026 Earnings"),
        (date(2026, 5, 1), "AMZN Q1 2026 Earnings"),
        (date(2026, 5, 21), "NVDA Q1 2026 Earnings"),
    ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_upcoming_events(self, days_ahead: int = 7) -> list[EconomicEvent]:
        """
        Return all scheduled high-impact events in the next N days.

        Parameters
        ----------
        days_ahead : how many calendar days to look ahead (inclusive of today)

        Returns
        -------
        list of EconomicEvent sorted by event_date ascending
        """
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)

        events: list[EconomicEvent] = []

        # FOMC
        for fomc_date in self._FOMC_DATES_2026:
            if today <= fomc_date <= cutoff:
                events.append(
                    EconomicEvent(
                        name="FOMC Rate Decision",
                        event_date=fomc_date,
                        impact="HIGH",
                        category="FOMC",
                        description=(
                            "Federal Open Market Committee interest rate decision. "
                            "Extreme volatility expected across all asset classes. "
                            "Avoid new entries 2h before and 1h after announcement."
                        ),
                    )
                )

        # NFP (first Friday of each month)
        for nfp_date in self._get_nfp_dates_in_range(today, cutoff):
            events.append(
                EconomicEvent(
                    name="Non-Farm Payrolls",
                    event_date=nfp_date,
                    impact="HIGH",
                    category="NFP",
                    description=(
                        "US Non-Farm Payrolls employment report. "
                        "Released at 8:30 AM ET on the first Friday of each month. "
                        "High volatility in USD pairs and equity indices."
                    ),
                )
            )

        # CPI
        for cpi_date in self._CPI_DATES_2026:
            if today <= cpi_date <= cutoff:
                events.append(
                    EconomicEvent(
                        name="CPI Inflation Report",
                        event_date=cpi_date,
                        impact="HIGH",
                        category="CPI",
                        description=(
                            "US Consumer Price Index inflation data. "
                            "Released at 8:30 AM ET. High volatility, especially "
                            "in bonds, USD, and rate-sensitive assets."
                        ),
                    )
                )

        # Major earnings
        for earnings_date, company in self._MAJOR_EARNINGS_2026:
            if today <= earnings_date <= cutoff:
                events.append(
                    EconomicEvent(
                        name=company,
                        event_date=earnings_date,
                        impact="MEDIUM",
                        category="EARNINGS",
                        description=f"{company} earnings release — expect gap risk.",
                    )
                )

        events.sort(key=lambda e: e.event_date)
        return events

    def is_high_impact_event_today(self) -> bool:
        """
        Return True if any HIGH-impact event is scheduled for today.

        The risk manager should call this before approving trade entries and
        reduce position sizes (or skip trading) when True.

        Returns
        -------
        bool
        """
        today_events = self.get_upcoming_events(days_ahead=0)
        has_high = any(e.impact == "HIGH" for e in today_events)
        if has_high:
            names = [e.name for e in today_events if e.impact == "HIGH"]
            logger.warning("High-impact event TODAY: %s", ", ".join(names))
        return has_high

    def is_high_impact_event_within_hours(self, hours: int = 24) -> bool:
        """
        Return True if a HIGH-impact event is within the next N hours.

        More granular than is_high_impact_event_today() — useful when the
        agent wants to avoid entries 2h before FOMC, for example.

        Parameters
        ----------
        hours : look-ahead window in hours

        Returns
        -------
        bool
        """
        days_needed = max(1, (hours // 24) + 1)
        events = self.get_upcoming_events(days_ahead=days_needed)
        now = datetime.now(tz=timezone.utc)
        cutoff_dt = now + timedelta(hours=hours)

        for event in events:
            if event.impact != "HIGH":
                continue
            # Events are date-only; treat them as occurring at 08:30 ET = 13:30 UTC
            event_dt = datetime(
                event.event_date.year,
                event.event_date.month,
                event.event_date.day,
                13, 30, 0,
                tzinfo=timezone.utc,
            )
            if now <= event_dt <= cutoff_dt:
                logger.warning(
                    "HIGH-impact event within %dh: %s on %s",
                    hours, event.name, event.event_date,
                )
                return True
        return False

    def get_fomc_dates(self) -> list[date]:
        """
        Return all 2026 scheduled FOMC meeting dates.

        Returns
        -------
        list of date objects in chronological order
        """
        return list(self._FOMC_DATES_2026)

    def get_events_for_date(self, target_date: date) -> list[EconomicEvent]:
        """
        Return all scheduled events for a specific date.

        Parameters
        ----------
        target_date : the calendar date to query

        Returns
        -------
        list of EconomicEvent (may be empty)
        """
        delta = (target_date - date.today()).days
        if delta < 0:
            # Past date — check historical directly
            events = []
            for fomc_date in self._FOMC_DATES_2026:
                if fomc_date == target_date:
                    events.append(EconomicEvent(
                        name="FOMC Rate Decision",
                        event_date=fomc_date,
                        impact="HIGH",
                        category="FOMC",
                    ))
            return events
        return [e for e in self.get_upcoming_events(days_ahead=delta + 1) if e.event_date == target_date]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_first_friday(year: int, month: int) -> date:
        """Return the first Friday of a given month and year."""
        d = date(year, month, 1)
        # Friday = weekday 4
        days_until_friday = (4 - d.weekday()) % 7
        return d + timedelta(days=days_until_friday)

    def _get_nfp_dates_in_range(self, start: date, end: date) -> list[date]:
        """Generate all first-Friday (NFP) dates between start and end inclusive."""
        nfp_dates: list[date] = []
        current = date(start.year, start.month, 1)
        while current <= end:
            nfp = self._get_first_friday(current.year, current.month)
            if start <= nfp <= end:
                nfp_dates.append(nfp)
            # Advance to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        return nfp_dates
