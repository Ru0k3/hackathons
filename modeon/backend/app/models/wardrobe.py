"""
Modeon — Wardrobe Pydantic Models
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WardrobeItemCreate(BaseModel):
    """Internal model — not exposed to the API directly. Used to track upload state."""

    item_id: str
    user_id: str
    blob_original_path: str


class WardrobeItemResponse(BaseModel):
    """Public representation of a wardrobe item returned by the API."""

    id: str
    category: Optional[str] = None
    colours: Optional[List[str]] = None
    pattern: Optional[str] = None
    formality: Optional[str] = None
    seasons: Optional[List[str]] = None
    custom_tags: Optional[List[str]] = None
    alt_text: Optional[str] = None
    is_in_laundry: bool
    is_archived: bool
    thumbnail_sas_url: Optional[str] = Field(
        default=None,
        description="Fresh 30-min SAS URL for the thumbnail. Null if CV pipeline is still running.",
    )
    created_at: str

    @classmethod
    def from_db_row(
        cls,
        row: dict,
        thumbnail_sas_url: Optional[str] = None,
    ) -> "WardrobeItemResponse":
        return cls(
            id=str(row["id"]),
            category=row.get("category"),
            colours=row.get("colours") or None,
            pattern=row.get("pattern"),
            formality=row.get("formality"),
            seasons=row.get("seasons") or None,
            custom_tags=row.get("custom_tags") or None,
            alt_text=row.get("alt_text"),
            is_in_laundry=bool(row.get("is_in_laundry", False)),
            is_archived=bool(row.get("is_archived", False)),
            thumbnail_sas_url=thumbnail_sas_url,
            created_at=str(row["created_at"]),
        )


class WardrobeListResponse(BaseModel):
    items: List[WardrobeItemResponse]
    total: int
    next_cursor: Optional[str] = None


class WardrobeTagUpdateRequest(BaseModel):
    """Partial update of AI-generated or user-corrected tags."""

    category: Optional[str] = None
    colours: Optional[List[str]] = None
    pattern: Optional[str] = None
    formality: Optional[str] = None
    seasons: Optional[List[str]] = None
    custom_tags: Optional[List[str]] = None


class LaundryToggleResponse(BaseModel):
    item_id: str
    is_in_laundry: bool


class BulkLaundryRequest(BaseModel):
    item_ids: List[str] = Field(min_length=1, max_length=200)
    in_laundry: bool


class UploadedItemStatus(BaseModel):
    """Returned immediately for each file after upload is enqueued."""

    item_id: str
    status: str = "processing"
