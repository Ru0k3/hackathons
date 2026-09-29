from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.storage.memory_db import USERS

router = APIRouter()


class Availability(BaseModel):
    day: str
    start: int
    end: int


class Preferences(BaseModel):
    preferred_time: str
    max_duration: int
    flexibility: str
    avoid_days: List[str]


class UserProfile(BaseModel):
    slack_id: str
    availability: List[Availability]
    preferences: Preferences


@router.post("/profile")
def save_profile(profile: UserProfile):
    USERS[profile.slack_id] = profile.dict()
    return {"status": "saved", "slack_id": profile.slack_id}


@router.get("/profile/{slack_id}")
def get_profile(slack_id: str):
    if slack_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS[slack_id]
