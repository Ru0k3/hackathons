"""
laundry.py  —  /api/laundry
Track clean/dirty/washing state for wardrobe items.
"""
import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth_dep import get_current_user
from app.services.openai_service import generate_outfits
from app.services.supabase_service import get_supabase

logger = logging.getLogger("modeon.laundry")
router = APIRouter()

UserId = Annotated[str, Depends(get_current_user)]

LaundryStatus = Literal["clean", "dirty", "washing"]


class LaundryUpdate(BaseModel):
    updates: list[dict]  # [{ item_id: str, status: LaundryStatus }]


@router.get("")
async def get_laundry_status(user_id: UserId):
    sb  = get_supabase()
    res = (
        sb.table("wardrobe_items")
        .select("id, category, colour, tags, description, laundry_status")
        .eq("user_id", user_id)
        .execute()
    )
    return {"items": res.data}


@router.patch("")
async def update_laundry_status(user_id: UserId, body: LaundryUpdate):
    sb      = get_supabase()
    updated = []
    for upd in body.updates:
        item_id = upd.get("item_id")
        status  = upd.get("status")
        if not item_id or status not in ("clean", "dirty", "washing"):
            continue
        res = (
            sb.table("wardrobe_items")
            .update({"laundry_status": status})
            .eq("id", item_id)
            .eq("user_id", user_id)
            .execute()
        )
        if res.data:
            updated.append(res.data[0])
    return {"updated": updated}


@router.post("/reset")
async def mark_all_clean(user_id: UserId):
    """Mark all dirty/washing items as clean (post-laundry reset)."""
    sb = get_supabase()
    res = (
        sb.table("wardrobe_items")
        .update({"laundry_status": "clean"})
        .eq("user_id", user_id)
        .in_("laundry_status", ["dirty", "washing"])
        .execute()
    )
    return {"reset_count": len(res.data or [])}


@router.get("/suggestions")
async def clean_outfit_suggestions(user_id: UserId):
    """Suggest outfits using only currently clean items."""
    sb  = get_supabase()
    res = (
        sb.table("wardrobe_items")
        .select("id, category, colour, tags, description")
        .eq("user_id", user_id)
        .eq("laundry_status", "clean")
        .execute()
    )
    clean_items = res.data or []
    if not clean_items:
        raise HTTPException(
            status_code=400, detail="No clean items available."
        )
    outfits = await generate_outfits(
        wardrobe_summary=clean_items,
        occasion="everyday",
        n=3,
    )
    return {"outfits": outfits}
