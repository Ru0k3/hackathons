from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from .normalizer import BusyInterval, NormalizedPreferences


@dataclass(frozen=True)
class CandidateSlot:
    start: datetime
    end: datetime
    score: float
    notes: list[str]


def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def is_free(slot_start: datetime, slot_end: datetime, busy: list[BusyInterval]) -> bool:
    for bi in busy:
        if _overlaps(slot_start, slot_end, bi.start, bi.end):
            return False
    return True


def preference_score(slot_start: datetime, prefs: NormalizedPreferences) -> tuple[float, list[str]]:
    score = 0.0
    notes: list[str] = []

    if slot_start.weekday() in prefs.avoid_weekdays:
        score -= 3.0
        notes.append("penalized: disliked weekday")

    if prefs.avoid_mornings and slot_start.hour < 12:
        score -= 2.0
        notes.append("penalized: morning time")

    if prefs.prefer_start_after is not None:
        if time(slot_start.hour, slot_start.minute) >= prefs.prefer_start_after:
            score += 1.5
            notes.append("rewarded: after preferred time")
        else:
            score -= 0.5
            notes.append("penalized: before preferred time")

    return score, notes


def generate_slots(
    *,
    now: datetime,
    horizon_days: int,
    slot_minutes: int,
    workday_start_hour: int,
    workday_end_hour: int,
) -> list[tuple[datetime, datetime]]:
    slots: list[tuple[datetime, datetime]] = []
    start_day = now.date()

    for d in range(horizon_days + 1):
        day = start_day + timedelta(days=d)

        t0 = datetime.combine(day, time(workday_start_hour, 0))
        t_end = datetime.combine(day, time(workday_end_hour, 0))

        # 🔥 Prevent suggesting past times for today
        if day == now.date():
            current = now.replace(second=0, microsecond=0)
            if current > t0:
                t0 = current

        cur = t0
        step = timedelta(minutes=slot_minutes)

        while cur + step <= t_end:
            slots.append((cur, cur + step))
            cur += step

    return slots



def find_perfect_overlap(
    *,
    now: datetime,
    horizon_days: int,
    slot_minutes: int,
    workday_start_hour: int,
    workday_end_hour: int,
    busy_a: list[BusyInterval],
    busy_b: list[BusyInterval],
) -> list[tuple[datetime, datetime]]:
    results: list[tuple[datetime, datetime]] = []

    for s, e in generate_slots(
        now=now,
        horizon_days=horizon_days,
        slot_minutes=slot_minutes,
        workday_start_hour=workday_start_hour,
        workday_end_hour=workday_end_hour,
    ):
        if is_free(s, e, busy_a) and is_free(s, e, busy_b):
            results.append((s, e))

    return results  # return top 5 available overlaps



def find_best_compromise(
    *,
    now: datetime,
    horizon_days: int,
    slot_minutes: int,
    workday_start_hour: int,
    workday_end_hour: int,
    busy_a: list[BusyInterval],
    busy_b: list[BusyInterval],
    prefs_a: NormalizedPreferences,
    prefs_b: NormalizedPreferences,
) -> CandidateSlot | None:
    best: CandidateSlot | None = None

    for s, e in generate_slots(
        now=now,
        horizon_days=horizon_days,
        slot_minutes=slot_minutes,
        workday_start_hour=workday_start_hour,
        workday_end_hour=workday_end_hour,
    ):
        # Compromise candidates: allow one side to be busy, but not both.
        free_a = is_free(s, e, busy_a)
        free_b = is_free(s, e, busy_b)
        if not (free_a or free_b):
            continue

        score = 0.0
        notes: list[str] = []

        # Strongly prefer times where both are free, even in "compromise" mode.
        if free_a and free_b:
            score += 10.0
            notes.append("both free")
        else:
            score -= 2.0
            notes.append("one user has conflict")

        sa, na = preference_score(s, prefs_a)
        sb, nb = preference_score(s, prefs_b)
        score += sa + sb
        notes.extend([f"A: {n}" for n in na])
        notes.extend([f"B: {n}" for n in nb])

        cand = CandidateSlot(start=s, end=e, score=score, notes=notes)
        if best is None or cand.score > best.score:
            best = cand

    return best

