"""
Modeon — Shopping Pydantic Models
"""

from pydantic import BaseModel


class ShoppingUploadResponse(BaseModel):
    shopping_item_id: str
    blob_path: str               # stored path (not URL)
    status: str                  # "uploaded" | "processing"
    thumbnail_sas_url: str       # fresh 30-min SAS URL for immediate display


class ShoppingCompareResponse(BaseModel):
    shopping_item_id: str
    compatible: bool
    confidence: float
    reason: str
    suggested_combinations: list[dict]   # [{item_ids, description}]
    low_confidence_warning: bool


class ShoppingListItem(BaseModel):
    id: str
    blob_path: str
    thumbnail_sas_url: str       # fresh SAS URL generated per response
    category: str | None
    colours: list[str] | None
    notes: str | None
    moved_to_wardrobe: bool
    added_at: str


class ShoppingListResponse(BaseModel):
    items: list[ShoppingListItem]
    total: int


class AddToShoppingListRequest(BaseModel):
    shopping_item_id: str        # blob path of the uploaded shopping item
    category: str | None = None
    colours: list[str] | None = None
    notes: str | None = None


class MoveToWardrobeResponse(BaseModel):
    wardrobe_item_id: str        # newly created wardrobe_items row id
    shopping_list_item_id: str
    status: str                  # "moved"


class ShoppingListOutfitRequest(BaseModel):
    item_ids: list[str] = []     # shopping_list_item ids; empty = use all


class ShoppingListOutfitItem(BaseModel):
    item_ids: list[str]          # mix of wardrobe item ids + shopping list item ids
    description: str
    source_label: str            # e.g. "2 from your list + 1 from wardrobe"


class ShoppingListOutfitsResponse(BaseModel):
    outfits: list[ShoppingListOutfitItem]
    shopping_items_used: int
    wardrobe_items_used: int
