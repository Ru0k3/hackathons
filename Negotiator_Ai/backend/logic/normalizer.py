from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable

from dateutil import parser as dateparser


WEEKDAYS = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tues": 1,
    "tuesday": 1,
    "wed": 2,
    "wednesday": 2,
    "thu": 3,
    "thurs": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}


@dataclass(frozen=True)
class NormalizedPreferences:
    # Days user strongly dislikes (penalty)
    avoid_weekdays: set[int]
    # If True, penalize slots before 12:00
    avoid_mornings: bool
    # If set, reward slots starting at/after this time
    prefer_start_after: time | None


@dataclass(frozen=True)
class BusyInterval:
    start: datetime
    end: datetime


def parse_preferences(text: str) -> NormalizedPreferences:
    t = (text or "").lower()
    avoid_weekdays: set[int] = set()
    avoid_mornings = False
    prefer_start_after: time | None = None

    # "I hate Mondays", "avoid Tuesday"
    for wd_str, wd in WEEKDAYS.items():
        # Accept plurals like "Mondays"
        if re.search(rf"\b(hate|avoid|no)\s+{re.escape(wd_str)}s?\b", t):
            avoid_weekdays.add(wd)

    if re.search(r"\b(no|avoid|hate)\s+mornings?\b", t):
        avoid_mornings = True

    # "prefer after 4pm", "only after 16:00"
    m = re.search(r"\b(after)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", t)
    if m:
        hh = int(m.group(2))
        mm = int(m.group(3) or "0")
        ampm = (m.group(4) or "").lower()
        if ampm == "pm" and hh < 12:
            hh += 12
        if ampm == "am" and hh == 12:
            hh = 0
        prefer_start_after = time(hh, mm)

    return NormalizedPreferences(
        avoid_weekdays=avoid_weekdays,
        avoid_mornings=avoid_mornings,
        prefer_start_after=prefer_start_after,
    )


def _next_weekday(base: date, target_weekday: int) -> date:
    delta = (target_weekday - base.weekday()) % 7
    return base + timedelta(days=delta)


def parse_busy_text(busy_text: str, *, now: datetime, horizon_days: int) -> list[BusyInterval]:
    """
    MVP parser for user-pasted "busy times".

    Supports lines like:
      - 2026-02-02 13:00-15:00
      - Tue 09:00-11:30
      - Mon 14:00-16:00
    """
    lines = [ln.strip() for ln in (busy_text or "").splitlines() if ln.strip()]
    if not lines:
        return []

    start_day = now.date()
    end_day = start_day + timedelta(days=horizon_days)
    out: list[BusyInterval] = []

    for ln in lines:
        # Split "... 13:00-15:00" or "Tue 13:00-15:00"
        m = re.search(r"(.+?)\s+(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*$", ln)
        if not m:
            continue
        day_part = m.group(1).strip()
        t1 = m.group(2)
        t2 = m.group(3)

        # Day could be weekday name or a date.
        day_lower = day_part.lower()
        dt_day: date | None = None
        if day_lower in WEEKDAYS:
            dt_day = _next_weekday(start_day, WEEKDAYS[day_lower])
        else:
            try:
                dt_day = dateparser.parse(day_part, dayfirst=False, yearfirst=True).date()
            except Exception:
                dt_day = None

        if not dt_day or not (start_day <= dt_day <= end_day):
            continue

        try:
            start_t = dateparser.parse(t1).time()
            end_t = dateparser.parse(t2).time()
        except Exception:
            continue

        start_dt = datetime.combine(dt_day, start_t)
        end_dt = datetime.combine(dt_day, end_t)
        if end_dt <= start_dt:
            continue
        out.append(BusyInterval(start=start_dt, end=end_dt))

    out.sort(key=lambda x: x.start)
    return out

