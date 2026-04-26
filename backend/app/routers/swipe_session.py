"""
Modeon — Swipe Session Router

Prefix: /api/outfits

Endpoints:
  GET  /swipe-session      — Generate a swipe deck of 10 outfit suggestions
  POST /swipe              — Record a like/dislike on an outfit
  POST /{outfit_id}/save   — Save an outfit to the user's collection
"""

import json
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import create_client, Client

from app.config import settings
from app.deps import get_current_user
from app.models.outfits import OutfitItem, SwipeRequest, SwipeSessionResponse
from app.services.ai_service import ai_service
from app.services.analytics import track
from app.services.preference_engine import build_preference_summary, get_available_wardrobe

logger = logging.getLogger("modeon.swipe_session")

router = APIRouter()


def _get_supabase() -> Client:
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )


# ── GET /swipe-session ─────────────────────────────────────────────────────────

@router.get("/swipe-session", response_model=SwipeSessionResponse)
async def get_swipe_session(
    occasion: str | None = Query(default=None),
    current_user: dict = Depends(get_current_user),
) -> SwipeSessionResponse:
    """
    Generate a ranked swipe deck of up to 10 outfits from the user's wardrobe.
    """
    user_id: str = current_user["id"]

    # 1. Fetch available wardrobe items
    wardrobe_items = await get_available_wardrobe(user_id)
    if len(wardrobe_items) < 5:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "not_enough_items",
                "message": "Add at least 5 items to your wardrobe to start generating outfits.",
                "wardrobe_size": len(wardrobe_items),
            },
        )

    # 2. Build preference summary
    preference_summary = await build_preference_summary(user_id)

    # 3. Build AI context payload
    context: dict = {
        "wardrobe": wardrobe_items,
        "preference_summary": preference_summary,
        "occasion": occasion or "any",
        "requested_outfits": 10,
        "lightweight_mode": settings.SWIPE_LIGHTWEIGHT_MODE,
    }

    # 4. Call AI service
    ai_response = await ai_service.complete(
        prompt_key="swipe_ranking",
        user_message=json.dumps(context),
        timeout=3.0,
        user_id=user_id,
    )

    raw_outfits: list[dict] = ai_response.get("outfits", [])

    # 5. Validate all item_ids against the user's actual wardrobe
    valid_item_ids: set[str] = {item["id"] for item in wardrobe_items}
    valid_outfits: list[dict] = []
    for outfit in raw_outfits:
        ids = outfit.get("item_ids") or []
        if all(iid in valid_item_ids for iid in ids) and ids:
            valid_outfits.append(outfit)
        else:
            logger.warning(
                "AI returned outfit with invalid item_ids — dropped: %s", ids
            )

    # 6. Insert valid outfits into generated_outfits table
    supabase = _get_supabase()
    outfit_items: list[OutfitItem] = []

    for outfit in valid_outfits:
        outfit_id = str(uuid4())
        try:
            supabase.table("generated_outfits").insert(
                {
                    "id": outfit_id,
                    "user_id": user_id,
                    "item_ids": outfit["item_ids"],
                    "source": "swipe",
                    "occasion": outfit.get("occasion"),
                    "explanation": outfit.get("explanation"),
                    "is_saved": False,
                }
            ).execute()
        except Exception as exc:
            logger.error("Failed to insert outfit %s: %s", outfit_id, exc)
            continue

        outfit_items.append(
            OutfitItem(
                item_ids=outfit["item_ids"],
                explanation=outfit.get("explanation"),
                confidence=outfit.get("confidence"),
                occasion=outfit.get("occasion"),
            )
        )

    # 7. Generate session ID and track
    session_id = str(uuid4())
    track(user_id, "swipe_session_started", {"occasion": occasion or "any"})

    return SwipeSessionResponse(
        session_id=session_id,
        outfits=outfit_items,
        wardrobe_size=len(wardrobe_items),
        has_preference_signal=preference_summary["has_enough_signal"],
    )


# ── POST /swipe ────────────────────────────────────────────────────────────────

@router.post("/swipe")
async def record_swipe(
    body: SwipeRequest,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Record a like or dislike on a generated outfit.
    """
    user_id: str = current_user["id"]
    supabase = _get_supabase()

    # Validate ownership
    try:
        outfit_response = (
            supabase.table("generated_outfits")
            .select("id, user_id")
            .eq("id", body.outfit_id)
            .single()
            .execute()
        )
        outfit = outfit_response.data
    except Exception as exc:
        logger.error("Failed to fetch outfit %s: %s", body.outfit_id, exc)
        raise HTTPException(status_code=404, detail="Outfit not found.")

    if not outfit or outfit.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorised to swipe this outfit.")

    swipe_value = 1 if body.direction == "like" else -1

    try:
        supabase.table("outfit_swipes").insert(
            {
                "user_id": user_id,
                "outfit_id": body.outfit_id,
                "swipe": swipe_value,
            }
        ).execute()
    except Exception as exc:
        logger.error("Failed to insert swipe for outfit %s: %s", body.outfit_id, exc)
        raise HTTPException(status_code=500, detail="Failed to record swipe.")

    track(user_id, "outfit_swiped", {"direction": body.direction})

    return {
        "recorded": True,
        "outfit_id": body.outfit_id,
        "direction": body.direction,
    }


# ── POST /{outfit_id}/save ─────────────────────────────────────────────────────

@router.post("/{outfit_id}/save")
async def save_outfit(
    outfit_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Save a generated outfit to the user's saved collection.
    """
    user_id: str = current_user["id"]
    supabase = _get_supabase()

    # Validate ownership
    try:
        outfit_response = (
            supabase.table("generated_outfits")
            .select("id, user_id, source")
            .eq("id", outfit_id)
            .single()
            .execute()
        )
        outfit = outfit_response.data
    except Exception as exc:
        logger.error("Failed to fetch outfit %s: %s", outfit_id, exc)
        raise HTTPException(status_code=404, detail="Outfit not found.")

    if not outfit or outfit.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorised to save this outfit.")

    try:
        supabase.table("generated_outfits").update(
            {"is_saved": True}
        ).eq("id", outfit_id).execute()
    except Exception as exc:
        logger.error("Failed to save outfit %s: %s", outfit_id, exc)
        raise HTTPException(status_code=500, detail="Failed to save outfit.")

    track(user_id, "outfit_saved", {"source": outfit.get("source", "unknown")})

    return {"saved": True, "outfit_id": outfit_id}
