"""
Modeon — GDPR Pydantic Models

Request/response schemas for the GDPR endpoints:
  GET  /api/account/export   → DataExportResponse
  DELETE /api/account        → AccountDeletionResponse
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Data Export ────────────────────────────────────────────────────────────────

class WardrobeItemExport(BaseModel):
    """A single wardrobe item, blob paths stripped."""
    id: str
    category: Optional[str] = None
    color: Optional[str] = None
    colours: List[str] = Field(default_factory=list)
    pattern: Optional[str] = None
    formality: Optional[str] = None
    seasons: List[str] = Field(default_factory=list)
    custom_tags: List[str] = Field(default_factory=list)
    in_laundry: bool = False
    archived_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # blob_path and thumb_path are intentionally excluded — never exposed to users


class GeneratedOutfitExport(BaseModel):
    """A generated/saved outfit — share_token included (it's user-owned data)."""
    id: str
    item_ids: List[str] = Field(default_factory=list)
    occasion: Optional[str] = None
    name: Optional[str] = None
    explanation: Optional[str] = None
    saved_at: Optional[str] = None
    share_token: Optional[str] = None
    share_expires: Optional[str] = None
    created_at: Optional[str] = None


class OutfitSwipeExport(BaseModel):
    id: str
    outfit_id: Optional[str] = None
    direction: str
    swiped_at: Optional[str] = None


class ShoppingListItemExport(BaseModel):
    """Shopping list item — blob_path stripped."""
    id: str
    tags: Optional[Dict[str, Any]] = None
    added_at: Optional[str] = None
    # blob_path intentionally excluded


class SubscriptionExport(BaseModel):
    id: str
    plan: str
    status: str
    period_end: Optional[str] = None
    created_at: Optional[str] = None
    # stripe_customer_id and stripe_sub_id excluded (internal billing identifiers)


class UserProfileExport(BaseModel):
    display_name: Optional[str] = None
    gender_pref: Optional[str] = None
    style_archetypes: List[str] = Field(default_factory=list)
    occasion_prefs: List[str] = Field(default_factory=list)
    colour_palette: Optional[str] = None
    notif_daily: bool = True
    notif_tips: bool = False
    notif_features: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DataExportResponse(BaseModel):
    """
    Complete GDPR data export payload for a single user.

    All Azure Blob paths (blob_path, thumb_path) are stripped — internal
    storage URIs are never returned to the user. All data is keyed by
    table name for clarity.
    """
    user_id: str
    email: Optional[str] = None
    profile: Optional[UserProfileExport] = None
    subscription: Optional[SubscriptionExport] = None
    wardrobe_items: List[WardrobeItemExport] = Field(default_factory=list)
    generated_outfits: List[GeneratedOutfitExport] = Field(default_factory=list)
    outfit_swipes: List[OutfitSwipeExport] = Field(default_factory=list)
    shopping_list_items: List[ShoppingListItemExport] = Field(default_factory=list)
    exported_at: str  # ISO-8601 timestamp


# ── Account Deletion ───────────────────────────────────────────────────────────

class AccountDeletionResponse(BaseModel):
    """
    Result of DELETE /api/account.

    status = "complete" — all data and blobs deleted successfully.
    status = "partial"  — some blob deletions failed; Supabase rows were deleted.
                          Manual blob cleanup may be required.
    """
    status: str = Field(..., pattern="^(complete|partial)$")
    message: str
    blobs_deleted: int = 0
    blobs_failed: int = 0
