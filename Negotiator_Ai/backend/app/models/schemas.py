from pydantic import BaseModel
from typing import List

class Preferences(BaseModel):
    preferred_time: str
    duration: str
    flexibility: str
    avoid_days: List[str]

class UserProfile(BaseModel):
    slack_id: str
    preferences: Preferences
