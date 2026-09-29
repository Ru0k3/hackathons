from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, HTTPException

from . import db
from .logic.matcher import find_best_compromise, find_perfect_overlap
from .logic.normalizer import parse_busy_text, parse_preferences
from .logic.watsonx import build_negotiation_message
from .models import ScheduleDecision, ScheduleRequest, UserProfile, UserProfileUpsert


app = FastAPI(title="Negotiator AI Backend", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/users")
def users() -> dict[str, list[str]]:
    return {"users": db.list_users()}


@app.get("/profile/{username}", response_model=UserProfile)
def get_profile(username: str) -> UserProfile:
    try:
        p = db.get_user_profile(username)
        return UserProfile(**p)
    except KeyError:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/profile", response_model=UserProfile)
def upsert_profile(payload: UserProfileUpsert) -> UserProfile:
    p = db.upsert_user_profile(
        username=payload.username.strip(),
        timezone_name=payload.timezone,
        busy_text=payload.busy_text,
        preferences_text=payload.preferences_text,
    )
    return UserProfile(**p)


@app.post("/schedule", response_model=ScheduleDecision)
def schedule(payload: ScheduleRequest) -> ScheduleDecision:
    thinking: list[str] = []
    now = datetime.now()

    def load(username: str) -> tuple[str, str]:
        p = db.get_user_profile(username)
        return p["busy_text"], p["preferences_text"]

    try:
        busy_text_a, pref_text_a = load(payload.user_a)
        busy_text_b, pref_text_b = load(payload.user_b)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    thinking.append(f"Checking {payload.user_a}'s calendar...")
    busy_a = parse_busy_text(busy_text_a, now=now, horizon_days=payload.horizon_days)
    prefs_a = parse_preferences(pref_text_a)

    thinking.append(f"Checking {payload.user_b}'s calendar...")
    busy_b = parse_busy_text(busy_text_b, now=now, horizon_days=payload.horizon_days)
    prefs_b = parse_preferences(pref_text_b)

    thinking.append("Searching for a perfect overlap...")
    overlaps = find_perfect_overlap(
    now=now,
    horizon_days=payload.horizon_days,
    slot_minutes=payload.slot_minutes,
    workday_start_hour=payload.workday_start_hour,
    workday_end_hour=payload.workday_end_hour,
    busy_a=busy_a,
    busy_b=busy_b,
)

    if overlaps:
        s, e = overlaps[0]
        thinking.append(f"Found {len(overlaps)} possible overlaps. Selecting earliest.")

        msg = build_negotiation_message(
            user_a=payload.user_a,
            user_b=payload.user_b,
            decision_kind="perfect_overlap",
            start=s,
            end=e,
            explanation="",
        )

        # 🔥 convert tuples -> dicts
        formatted_top = [
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
            for start, end in overlaps[:5]
        ]

        formatted_all = [
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
            for start, end in overlaps
        ]

        return ScheduleDecision(
            kind="perfect_overlap",
            start=s.isoformat(),
            end=e.isoformat(),
            explanation="Multiple possible time slots found.",
            thinking=thinking,
            message_to_users=msg,
            top_slots=formatted_top,   # ✅ only 5
            all_slots=formatted_all    # ✅ full weekly view
        )




    thinking.append("No perfect overlap found. Negotiating a compromise...")
    best = find_best_compromise(
        now=now,
        horizon_days=payload.horizon_days,
        slot_minutes=payload.slot_minutes,
        workday_start_hour=payload.workday_start_hour,
        workday_end_hour=payload.workday_end_hour,
        busy_a=busy_a,
        busy_b=busy_b,
        prefs_a=prefs_a,
        prefs_b=prefs_b,
    )
    if not best:
        msg = build_negotiation_message(
            user_a=payload.user_a,
            user_b=payload.user_b,
            decision_kind="no_solution",
            start=None,
            end=None,
            explanation="Try widening the horizon or adjusting working hours.",
        )
        return ScheduleDecision(
            kind="no_solution",
            start=None,
            end=None,
            explanation="No viable time slots found in the search window.",
            thinking=thinking,
            message_to_users=msg,
        )

    explanation = "Best-effort slot chosen using stated preferences."
    thinking.append(f"Selected {best.start:%a %H:%M} based on preference scoring.")
    msg = build_negotiation_message(
        user_a=payload.user_a,
        user_b=payload.user_b,
        decision_kind="compromise",
        start=best.start,
        end=best.end,
        explanation=explanation,
    )
    return ScheduleDecision(
        kind="compromise",
        start=best.start,
        end=best.end,
        explanation=explanation + " Notes: " + "; ".join(best.notes[:6]),
        thinking=thinking,
        message_to_users=msg,
    )

