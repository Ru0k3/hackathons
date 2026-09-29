from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth_dep import get_current_user
from app.services.compatibility_scorer import score_outfit
from app.services.supabase_service import get_supabase

router = APIRouter()


class ScoreRequest(BaseModel):
    item_ids: list[str]


def _resolve_user_id(current_user: str | dict[str, Any]) -> str:
    if isinstance(current_user, str):
        return current_user
    for key in ("user_id", "id", "sub"):
        value = current_user.get(key)
        if value:
            return str(value)
    raise HTTPException(status_code=401, detail="Invalid auth payload.")


@router.post("/score")
async def score_mix_match(
    body: ScoreRequest,
    current_user: str | dict[str, Any] = Depends(get_current_user),
) -> dict:
    if not body.item_ids:
        raise HTTPException(status_code=400, detail="item_ids is required.")

    user_id = _resolve_user_id(current_user)
    sb = get_supabase()
    try:
        result = (
            sb.table("wardrobe_items")
            .select("id, category, colour, tags, description, formality")
            .eq("user_id", user_id)
            .in_("id", body.item_ids)
            .execute()
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch wardrobe metadata: {exc}")

    wardrobe_metadata = result.data or []
    return await score_outfit(body.item_ids, wardrobe_metadata)
