import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth_dep import get_current_user
from app.services.export_composer import compose_outfit_card
from app.services.supabase_service import get_supabase

router = APIRouter()


def _resolve_user_id(current_user: str | dict[str, Any]) -> str:
    if isinstance(current_user, str):
        return current_user
    for key in ("user_id", "id", "sub"):
        value = current_user.get(key)
        if value:
            return str(value)
    raise HTTPException(status_code=401, detail="Invalid auth payload.")


def _fetch_owned_outfit(outfit_id: str, user_id: str) -> dict[str, Any]:
    sb = get_supabase()
    try:
        result = (
            sb.table("outfits")
            .select("*")
            .eq("id", outfit_id)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch outfit: {exc}")
    row = (result.data or [None])[0]
    if not row:
        raise HTTPException(status_code=404, detail="Outfit not found.")
    return row


@router.get("/{outfit_id}/export")
async def export_outfit(
    outfit_id: str,
    current_user: str | dict[str, Any] = Depends(get_current_user),
) -> Response:
    user_id = _resolve_user_id(current_user)
    outfit = _fetch_owned_outfit(outfit_id, user_id)
    item_ids = [str(item_id) for item_id in (outfit.get("item_ids") or [])]
    if not item_ids:
        raise HTTPException(status_code=400, detail="Outfit has no items to export.")

    sb = get_supabase()
    try:
        items_result = (
            sb.table("wardrobe_items")
            .select("id, image_url, category, colour")
            .eq("user_id", user_id)
            .in_("id", item_ids)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe items: {exc}")

    item_map = {str(item["id"]): item for item in (items_result.data or [])}
    ordered_items = [item_map[item_id] for item_id in item_ids if item_id in item_map]
    png_bytes = await compose_outfit_card(ordered_items)
    return Response(content=png_bytes, media_type="image/png")


@router.post("/{outfit_id}/share")
async def share_outfit(
    outfit_id: str,
    current_user: str | dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    user_id = _resolve_user_id(current_user)
    _fetch_owned_outfit(outfit_id, user_id)

    share_token = str(uuid.uuid4())
    sb = get_supabase()
    sb.table("outfits").update({"share_token": share_token}).eq("id", outfit_id).eq("user_id", user_id).execute()
    return {"share_url": f"https://modeon.app/shared/{share_token}"}


@router.delete("/{outfit_id}/share")
async def revoke_share_outfit(
    outfit_id: str,
    current_user: str | dict[str, Any] = Depends(get_current_user),
) -> dict[str, bool]:
    user_id = _resolve_user_id(current_user)
    _fetch_owned_outfit(outfit_id, user_id)

    sb = get_supabase()
    sb.table("outfits").update({"share_token": None}).eq("id", outfit_id).eq("user_id", user_id).execute()
    return {"revoked": True}


@router.get("/public/{token}")
async def get_public_outfit(token: str) -> dict[str, Any]:
    sb = get_supabase()
    try:
        result = sb.table("outfits").select("*").eq("share_token", token).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch public outfit: {exc}")

    row = (result.data or [None])[0]
    if not row:
        raise HTTPException(status_code=404, detail="Shared outfit not found.")
    return row
