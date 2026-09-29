from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BusyInterval(BaseModel):
    start: datetime
    end: datetime


class UserProfileUpsert(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    timezone: str = Field(default="local", description="IANA tz (MVP accepts 'local').")
    busy_text: str = Field(default="", description="User-pasted busy times.")
    preferences_text: str = Field(default="", description="Free-text preferences/constraints.")


class UserProfile(UserProfileUpsert):
    updated_at: datetime


class ScheduleRequest(BaseModel):
    user_a: str
    user_b: str
    horizon_days: int = Field(default=7, ge=1, le=30)
    slot_minutes: int = Field(default=30, ge=15, le=120)
    workday_start_hour: int = Field(default=9, ge=0, le=23)
    workday_end_hour: int = Field(default=17, ge=1, le=24)


class ScheduleDecision(BaseModel):
    kind: Literal["perfect_overlap", "compromise", "no_solution"]
    start: datetime | None = None
    end: datetime | None = None
    explanation: str
    thinking: list[str] = Field(default_factory=list)
    message_to_users: str = ""
    top_slots: list[dict] | None = None
    all_slots: list[dict] | None = None   # 🔥 add this

