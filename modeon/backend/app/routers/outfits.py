"""
outfits.py  -  /api/outfits
Saved outfits + AI generation, mix-match, and occasion styling.
"""
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth_dep import get_current_user
from app.services.openai_service import (
    generate_outfits,
    mix_match,
)
from app.services.supabase_service import get_supabase

logger = logging.getLogger("modeon.outfits")
router = APIRouter()

UserId = Annotated[str, Depends(get_current_user)]


class OutfitCreate(BaseModel):
    name: str
    item_ids: list[str]
    occasion: str | None = None
    notes: str | None = None


class OutfitUpdate(BaseModel):
    name: str | None = None
    item_ids: list[str] | None = None
    occasion: str | None = None
    notes: str | None = None


class GenerateRequest(BaseModel):
    occasion: str
    weather: str | None = None
    mood: str | None = None
    exclude_item_ids: list[str] = []
    n: int = 3


class MixMatchRequest(BaseModel):
    occasion: str | None = None


class OccasionRequest(BaseModel):
    occasion: str
    date: str | None = None
    weather: str | None = None
    mood: str | None = None


def _wardrobe_summary(user_id: str, exclude: list[str] | None = None) -> list[dict]:
    sb = get_supabase()
    res = (
        sb.table("wardrobe_items")
        .select("id, category, colour, tags, description")
        .eq("user_id", user_id)
        .execute()
    )
    items = res.data or []
    if exclude:
        items = [i for i in items if i["id"] not in exclude]
    return items


@router.get("")
async def list_outfits(user_id: UserId):
    sb = get_supabase()
    res = (
        sb.table("outfits")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"outfits": res.data, "total": len(res.data)}


@router.get("/{outfit_id}")
async def get_outfit(outfit_id: str, user_id: UserId):
    sb = get_supabase()
    res = (
        sb.table("outfits")
        .select("*")
        .eq("id", outfit_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Outfit not found.")
    return res.data


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_outfit(user_id: UserId, body: OutfitCreate):
    sb = get_supabase()
    row = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        **body.model_dump(),
    }
    res = sb.table("outfits").insert(row).execute()
    return res.data[0]


@router.patch("/{outfit_id}")
async def update_outfit(outfit_id: str, user_id: UserId, body: OutfitUpdate):
    sb = get_supabase()
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="Nothing to update.")
    res = (
        sb.table("outfits")
        .update(payload)
        .eq("id", outfit_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Outfit not found.")
    return res.data[0]


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(outfit_id: str, user_id: UserId):
    sb = get_supabase()
    sb.table("outfits").delete().eq("id", outfit_id).eq("user_id", user_id).execute()


@router.post("/generate")
async def ai_generate_outfits(user_id: UserId, body: GenerateRequest):
    wardrobe = _wardrobe_summary(user_id, exclude=body.exclude_item_ids)
    if not wardrobe:
        raise HTTPException(status_code=400, detail="Wardrobe is empty.")
    outfits = await generate_outfits(
        wardrobe_summary=wardrobe,
        occasion=body.occasion,
        weather=body.weather,
        mood=body.mood,
        n=body.n,
    )
    return {"outfits": outfits}


@router.get("/mix-match/{item_id}")
async def ai_mix_match(item_id: str, user_id: UserId, occasion: str | None = None):
    sb = get_supabase()
    item_res = (
        sb.table("wardrobe_items")
        .select("*")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not item_res.data:
        raise HTTPException(status_code=404, detail="Item not found.")

    wardrobe = _wardrobe_summary(user_id, exclude=[item_id])
    looks = await mix_match(item_res.data, wardrobe, occasion=occasion)
    return {"suggestions": looks}
