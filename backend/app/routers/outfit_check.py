"""
outfit_check.py  —  /api/outfit-check
Upload a photo and get AI critique.
"""
import json
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth_dep import get_current_user
from app.services.blob_service import BlobService, CONTAINER_WARDROBE_ORIGINALS
from app.services.openai_service import check_outfit
from app.services.supabase_service import get_supabase

logger = logging.getLogger("modeon.outfit_check")
router = APIRouter()

UserId = Annotated[str, Depends(get_current_user)]


@router.post("")
async def submit_outfit_check(
    user_id: UserId,
    image:   UploadFile = File(...),
    context: str        = Form("{}"),
):
    ctx       = json.loads(context)
    blob      = BlobService()
    img_bytes = await image.read()

    blob_name = f"{user_id}/checks/{uuid.uuid4()}.jpg"
    image_url = await blob.upload(
        data=img_bytes,
        container=CONTAINER_WARDROBE_ORIGINALS,
        blob_name=blob_name,
        content_type=image.content_type or "image/jpeg",
    )
    if not image_url:
        raise HTTPException(status_code=500, detail="Image upload failed.")

    result = await check_outfit(image_url, ctx)
    if not result:
        raise HTTPException(status_code=500, detail="AI analysis failed.")

    # Persist result for history
    sb  = get_supabase()
    row = {
        "id":        str(uuid.uuid4()),
        "user_id":   user_id,
        "image_url": image_url,
        "result":    result,
        "context":   ctx,
    }
    sb.table("outfit_checks").insert(row).execute()

    return {**result, "image_url": image_url}


@router.get("/history")
async def list_outfit_checks(user_id: UserId, limit: int = 20, offset: int = 0):
    sb  = get_supabase()
    res = (
        sb.table("outfit_checks")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return {"items": res.data, "total": len(res.data)}
