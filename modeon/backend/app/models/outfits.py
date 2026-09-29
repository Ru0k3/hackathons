"""
Modeon — Outfit Pydantic Models
"""

from typing import Optional

from pydantic import BaseModel, validator


class OutfitItem(BaseModel):
    item_ids: list[str]               # wardrobe_item UUIDs forming this outfit
    explanation: str | None = None    # stylist explanation (null in lightweight mode)
    confidence: float | None = None   # 0.0–1.0 model confidence score
    occasion: str | None = None


class SwipeSessionResponse(BaseModel):
    session_id: str                   # uuid, generated per session for tracking
    outfits: list[OutfitItem]
    wardrobe_size: int                # how many available items were used
    has_preference_signal: bool       # whether swipe history influenced this session


class SwipeRequest(BaseModel):
    outfit_id: str
    direction: str                    # "like" | "dislike"

    @validator("direction")
    def direction_must_be_valid(cls, v: str) -> str:
        if v not in ("like", "dislike"):
            raise ValueError("direction must be 'like' or 'dislike'")
        return v


class SaveOutfitRequest(BaseModel):
    outfit_id: str


class DailyOutfitResponse(BaseModel):
    outfit_id: str
    item_ids: list[str]
    explanation: str | None = None
    already_seen_today: bool          # True if daily outfit already generated today
    thumbnail_sas_urls: dict[str, str]  # item_id -> SAS URL map


class OutfitExportResponse(BaseModel):
    outfit_id: str
    export_url: str                   # SAS URL to the generated PNG card
    share_token: str | None = None


class GeneratedOutfitDB(BaseModel):
    """Internal model for DB insert/read."""
    id: str
    user_id: str
    item_ids: list[str]
    source: str
    occasion: str | None = None
    explanation: str | None = None
    is_saved: bool
    created_at: str
