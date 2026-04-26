from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth_dep import get_current_user
from app.services.outfit_generator import generate_occasion_outfit
from app.services.supabase_service import get_supabase

router = APIRouter()


class OccasionStylingRequest(BaseModel):
    occasion: str
    date: str | None = None
    weather: str | None = None
    mood: str | None = None


def _resolve_user_id(current_user: str | dict[str, Any]) -> str:
    if isinstance(current_user, str):
        return current_user
    for key in ("user_id", "id", "sub"):
        value = current_user.get(key)
        if value:
            return str(value)
    raise HTTPException(status_code=401, detail="Invalid auth payload.")


def _build_description(body: OccasionStylingRequest) -> str:
    parts: list[str] = []
    if body.date:
        parts.append(f"date={body.date}")
    if body.weather:
        parts.append(f"weather={body.weather}")
    if body.mood:
        parts.append(f"mood={body.mood}")
    return "; ".join(parts)


@router.post("/occasion")
async def style_for_occasion(
    body: OccasionStylingRequest,
    current_user: str | dict[str, Any] = Depends(get_current_user),
) -> dict[str, list[dict]]:
    user_id = _resolve_user_id(current_user)
    sb = get_supabase()

    try:
        result = (
            sb.table("wardrobe_items")
            .select("id, category, colour, tags, description, formality, seasons")
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe: {exc}")

    wardrobe_items = result.data or []
    if not wardrobe_items:
        raise HTTPException(status_code=400, detail="Wardrobe is empty.")

    description = _build_description(body)
    outfit = await generate_occasion_outfit(
        user_id=user_id,
        occasion=body.occasion,
        description=description,
        wardrobe_items=wardrobe_items,
    )
    return {"outfits": [outfit]}
