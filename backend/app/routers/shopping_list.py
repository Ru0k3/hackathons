"""
Modeon — Shopping List Router

Prefix: /api/shopping-list

Endpoints:
  POST /add                  — Add a shopping upload to the persistent shopping list
  GET  /                     — List current shopping list items with SAS URLs
  DELETE /{item_id}          — Remove an item (DB row + blob)
  POST  /{item_id}/move-to-wardrobe — Move item into the wardrobe + enqueue CV
  POST  /outfits/generate    — Generate outfit combos mixing list + wardrobe items
"""

import json
import logging
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from supabase import create_client, Client

from app.config import settings
from app.deps import get_current_user
from app.models.shopping import (
    AddToShoppingListRequest,
    MoveToWardrobeResponse,
    ShoppingListItem,
    ShoppingListOutfitItem,
    ShoppingListOutfitRequest,
    ShoppingListOutfitsResponse,
    ShoppingListResponse,
)
from app.services.ai_service import ai_service
from app.services.analytics import track
from app.services.blob_service import (
    CONTAINER_SHOPPING_UPLOADS,
    CONTAINER_WARDROBE_ORIGINALS,
    blob_service,
)
from app.services.cv_pipeline import run_cv_pipeline
from app.services.preference_engine import get_available_wardrobe

logger = logging.getLogger("modeon.shopping_list")

router = APIRouter()

_EXT_MAP = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def _get_supabase() -> Client:
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )


def _infer_ext(blob_path: str) -> str:
    """Infer extension from blob path, defaulting to 'jpg'."""
    if "." in blob_path:
        return blob_path.rsplit(".", 1)[-1].lower()
    return "jpg"


async def _sas_url_for(blob_path: str) -> str:
    return await blob_service.generate_sas_url_async(
        container=CONTAINER_SHOPPING_UPLOADS,
        blob_path=blob_path,
        expiry_minutes=30,
    )


def _fetch_item_owned(item_id: str, user_id: str, supabase: Client) -> dict:
    """
    Fetch a shopping list item by id, validating ownership.
    Raises 404 or 403 as appropriate.
    """
    try:
        resp = (
            supabase.table("shopping_list_items")
            .select("*")
            .eq("id", item_id)
            .single()
            .execute()
        )
        row = resp.data
    except Exception as exc:
        logger.error("DB error fetching shopping list item %s: %s", item_id, exc)
        raise HTTPException(status_code=404, detail="Item not found.")

    if not row:
        raise HTTPException(status_code=404, detail="Item not found.")
    if row.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorised to access this item.")
    return row


# ── POST /add ─────────────────────────────────────────────────────────────────

@router.post("/add", response_model=ShoppingListItem)
async def add_to_shopping_list(
    body: AddToShoppingListRequest,
    current_user: dict = Depends(get_current_user),
) -> ShoppingListItem:
    """
    Persist a previously-uploaded shopping item to the shopping list.
    """
    user_id: str = current_user["id"]
    blob_path: str = body.shopping_item_id

    # Validate ownership via blob path prefix
    if not blob_path.startswith(f"{user_id}/"):
        raise HTTPException(status_code=403, detail="Not authorised to add this item.")

    supabase = _get_supabase()
    item_id = str(uuid4())

    try:
        insert_resp = (
            supabase.table("shopping_list_items")
            .insert(
                {
                    "id": item_id,
                    "user_id": user_id,
                    "blob_path": blob_path,
                    "category": body.category,
                    "colours": body.colours,
                    "notes": body.notes,
                    "moved_to_wardrobe": False,
                }
            )
            .execute()
        )
        row = insert_resp.data[0] if insert_resp.data else None
    except Exception as exc:
        logger.error("Failed to insert shopping list item for user %s: %s", user_id, exc)
        raise HTTPException(status_code=500, detail="Failed to add item to shopping list.")

    if not row:
        raise HTTPException(status_code=500, detail="Failed to add item to shopping list.")

    thumbnail_sas_url = await _sas_url_for(blob_path)
    track(user_id, "shopping_item_saved", {"via": "direct"})

    return ShoppingListItem(
        id=str(row["id"]),
        blob_path=row["blob_path"],
        thumbnail_sas_url=thumbnail_sas_url,
        category=row.get("category"),
        colours=row.get("colours"),
        notes=row.get("notes"),
        moved_to_wardrobe=bool(row.get("moved_to_wardrobe", False)),
        added_at=str(row.get("created_at", "")),
    )


# ── GET / ─────────────────────────────────────────────────────────────────────

@router.get("/", response_model=ShoppingListResponse)
async def list_shopping_list(
    include_moved: bool = Query(default=False),
    current_user: dict = Depends(get_current_user),
) -> ShoppingListResponse:
    """
    List the user's shopping list items with fresh SAS URLs.
    """
    user_id: str = current_user["id"]
    supabase = _get_supabase()

    try:
        query = (
            supabase.table("shopping_list_items")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
        )
        if not include_moved:
            query = query.eq("moved_to_wardrobe", False)
        resp = query.execute()
        rows = resp.data or []
    except Exception as exc:
        logger.error("Failed to fetch shopping list for user %s: %s", user_id, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch shopping list.")

    import asyncio

    async def _build_item(row: dict) -> ShoppingListItem:
        sas_url = await _sas_url_for(row["blob_path"])
        return ShoppingListItem(
            id=str(row["id"]),
            blob_path=row["blob_path"],
            thumbnail_sas_url=sas_url,
            category=row.get("category"),
            colours=row.get("colours"),
            notes=row.get("notes"),
            moved_to_wardrobe=bool(row.get("moved_to_wardrobe", False)),
            added_at=str(row.get("created_at", "")),
        )

    items = await asyncio.gather(*[_build_item(row) for row in rows])

    return ShoppingListResponse(items=list(items), total=len(items))


# ── DELETE /{item_id} ─────────────────────────────────────────────────────────

@router.delete("/{item_id}")
async def delete_shopping_list_item(
    item_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Hard delete a shopping list item: removes DB row and blob.
    """
    user_id: str = current_user["id"]
    supabase = _get_supabase()

    row = _fetch_item_owned(item_id, user_id, supabase)
    blob_path: str = row["blob_path"]

    # Delete DB row
    try:
        supabase.table("shopping_list_items").delete().eq("id", item_id).execute()
    except Exception as exc:
        logger.error("Failed to delete shopping list item %s: %s", item_id, exc)
        raise HTTPException(status_code=500, detail="Failed to delete item.")

    # Delete blob (non-fatal if already gone)
    try:
        await blob_service.delete_blob(CONTAINER_SHOPPING_UPLOADS, blob_path)
    except Exception as exc:
        logger.warning("Failed to delete blob %s: %s", blob_path, exc)

    return {"deleted": True, "item_id": item_id}


# ── POST /{item_id}/move-to-wardrobe ──────────────────────────────────────────

@router.post("/{item_id}/move-to-wardrobe", response_model=MoveToWardrobeResponse)
async def move_to_wardrobe(
    item_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> MoveToWardrobeResponse:
    """
    Copy a shopping list item into the wardrobe and enqueue the CV pipeline.
    """
    user_id: str = current_user["id"]
    supabase = _get_supabase()

    row = _fetch_item_owned(item_id, user_id, supabase)
    blob_path: str = row["blob_path"]
    ext = _infer_ext(blob_path)

    # Download image bytes from shopping-uploads
    try:
        image_bytes = await blob_service.download_bytes(CONTAINER_SHOPPING_UPLOADS, blob_path)
    except Exception as exc:
        logger.error("Failed to download shopping item %s: %s", blob_path, exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve image.")

    # Generate new wardrobe item identity
    wardrobe_item_id = str(uuid4())
    wardrobe_blob_path = f"{user_id}/{wardrobe_item_id}_original.{ext}"

    # Copy blob to wardrobe-originals container
    content_type_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    content_type = content_type_map.get(ext, "image/jpeg")

    try:
        await blob_service.upload_bytes(
            container=CONTAINER_WARDROBE_ORIGINALS,
            blob_path=wardrobe_blob_path,
            data=image_bytes,
            content_type=content_type,
        )
    except Exception as exc:
        logger.error("Failed to copy blob to wardrobe-originals: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to move image to wardrobe.")

    # Insert wardrobe_items row (CV pipeline fills in tags)
    try:
        supabase.table("wardrobe_items").insert(
            {
                "id": wardrobe_item_id,
                "user_id": user_id,
                "blob_original_path": wardrobe_blob_path,
                "category": row.get("category"),
                "colours": row.get("colours"),
                "pattern": None,
                "formality": None,
                "seasons": None,
                "custom_tags": None,
                "alt_text": None,
                "is_in_laundry": False,
                "is_archived": False,
            }
        ).execute()
    except Exception as exc:
        logger.error("Failed to insert wardrobe item %s: %s", wardrobe_item_id, exc)
        raise HTTPException(status_code=500, detail="Failed to create wardrobe item.")

    # Enqueue CV pipeline as BackgroundTask
    background_tasks.add_task(
        run_cv_pipeline,
        item_id=wardrobe_item_id,
        user_id=user_id,
        original_blob_path=wardrobe_blob_path,
        image_bytes=image_bytes,
    )

    # Mark shopping list item as moved
    try:
        supabase.table("shopping_list_items").update(
            {"moved_to_wardrobe": True}
        ).eq("id", item_id).execute()
    except Exception as exc:
        logger.warning("Failed to mark shopping list item %s as moved: %s", item_id, exc)

    track(user_id, "shopping_list_item_moved_to_wardrobe", {"wardrobe_item_id": wardrobe_item_id})

    return MoveToWardrobeResponse(
        wardrobe_item_id=wardrobe_item_id,
        shopping_list_item_id=item_id,
        status="moved",
    )


# ── POST /outfits/generate ────────────────────────────────────────────────────

@router.post("/outfits/generate", response_model=ShoppingListOutfitsResponse)
async def generate_shopping_list_outfits(
    body: ShoppingListOutfitRequest,
    current_user: dict = Depends(get_current_user),
) -> ShoppingListOutfitsResponse:
    """
    Generate outfit combinations that mix shopping list items with wardrobe items.
    """
    user_id: str = current_user["id"]
    supabase = _get_supabase()

    # Fetch shopping list items (specific ids or all non-moved)
    try:
        if body.item_ids:
            resp = (
                supabase.table("shopping_list_items")
                .select("*")
                .eq("user_id", user_id)
                .in_("id", body.item_ids)
                .eq("moved_to_wardrobe", False)
                .execute()
            )
        else:
            resp = (
                supabase.table("shopping_list_items")
                .select("*")
                .eq("user_id", user_id)
                .eq("moved_to_wardrobe", False)
                .order("created_at", desc=True)
                .execute()
            )
        shopping_rows = resp.data or []
    except Exception as exc:
        logger.error("Failed to fetch shopping list items for user %s: %s", user_id, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch shopping list.")

    if len(shopping_rows) < 2:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "not_enough_items",
                "message": "Add at least 2 items to your Shopping List to generate outfit combinations.",
            },
        )

    # Fetch available wardrobe
    wardrobe_metadata = await get_available_wardrobe(user_id)

    # Build shopping list context (no blob paths)
    shopping_list_context = [
        {
            "id": str(row["id"]),
            "category": row.get("category"),
            "colours": row.get("colours") or [],
            "notes": row.get("notes"),
        }
        for row in shopping_rows
    ]

    context: dict = {
        "shopping_list_items": shopping_list_context,
        "wardrobe": wardrobe_metadata,
        "max_outfits": 10,
    }

    ai_response = await ai_service.complete(
        prompt_key="shopping_list_generator",
        user_message=json.dumps(context),
        timeout=5.0,
        use_large_model=True,
        user_id=user_id,
    )

    raw_outfits: list[dict] = ai_response.get("outfits") or []

    # Build valid ID sets for cross-checking
    valid_shopping_ids: set[str] = {str(row["id"]) for row in shopping_rows}
    valid_wardrobe_ids: set[str] = {item["id"] for item in wardrobe_metadata}
    all_valid_ids = valid_shopping_ids | valid_wardrobe_ids

    # Validate and cap at 10
    validated_outfits: list[ShoppingListOutfitItem] = []
    for outfit in raw_outfits[:10]:
        ids: list[str] = outfit.get("item_ids") or []
        if not ids or not all(iid in all_valid_ids for iid in ids):
            logger.warning(
                "shopping_list_generator: dropped outfit with invalid item_ids: %s", ids
            )
            continue
        # Must contain at least one shopping list item
        if not any(iid in valid_shopping_ids for iid in ids):
            logger.warning(
                "shopping_list_generator: dropped outfit with no shopping list items: %s", ids
            )
            continue
        validated_outfits.append(
            ShoppingListOutfitItem(
                item_ids=ids,
                description=str(outfit.get("description", "")),
                source_label=str(outfit.get("source_label", "")),
            )
        )

    # Count unique items used across all outfits
    all_outfit_ids: set[str] = {iid for o in validated_outfits for iid in o.item_ids}
    shopping_items_used = len(all_outfit_ids & valid_shopping_ids)
    wardrobe_items_used = len(all_outfit_ids & valid_wardrobe_ids)

    track(
        user_id,
        "shopping_list_outfit_generated",
        {"item_count": len(shopping_rows)},
    )

    return ShoppingListOutfitsResponse(
        outfits=validated_outfits,
        shopping_items_used=shopping_items_used,
        wardrobe_items_used=wardrobe_items_used,
    )
