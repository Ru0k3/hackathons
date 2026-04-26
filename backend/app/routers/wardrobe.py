"""
wardrobe.py  —  /api/wardrobe
Full CRUD for wardrobe items with Azure Blob upload and AI classification.
"""
import json
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.auth_dep import get_current_user
from app.services.blob_service import BlobService, CONTAINER_WARDROBE_ORIGINALS
from app.services.openai_service import classify_garment
from app.services.supabase_service import get_supabase

logger = logging.getLogger("modeon.wardrobe")
router = APIRouter()

UserId = Annotated[str, Depends(get_current_user)]


class WardrobeItemUpdate(BaseModel):
    category:          str | None = None
    colour:            str | None = None
    brand:             str | None = None
    tags:              list[str] | None = None
    description:       str | None = None
    care_instructions: str | None = None
    notes:             str | None = None


# ── List ───────────────────────────────────────────────────────────────────────
@router.get("")
async def list_items(user_id: UserId, category: str | None = None):
    sb = get_supabase()
    q  = sb.table("wardrobe_items").select("*").eq("user_id", user_id)
    if category:
        q = q.eq("category", category)
    res = q.order("created_at", desc=True).execute()
    return {"items": res.data, "total": len(res.data)}


# ── Get single ─────────────────────────────────────────────────────────────────
@router.get("/{item_id}")
async def get_item(item_id: str, user_id: UserId):
    sb  = get_supabase()
    res = (
        sb.table("wardrobe_items")
        .select("*")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found.")
    return res.data


# ── Upload + create ────────────────────────────────────────────────────────────
@router.post("", status_code=status.HTTP_201_CREATED)
async def add_item(
    user_id:  UserId,
    image:    UploadFile = File(...),
    metadata: str        = Form("{}"),
):
    sb = get_supabase()
    meta = json.loads(metadata)
    blob = BlobService()

    image_bytes = await image.read()
    blob_name   = f"{user_id}/{uuid.uuid4()}{_ext(image.filename)}"
    image_url   = await blob.upload(
        data=image_bytes,
        container=CONTAINER_WARDROBE_ORIGINALS,
        blob_name=blob_name,
        content_type=image.content_type or "image/jpeg",
    )
    if not image_url:
        raise HTTPException(status_code=500, detail="Image upload failed.")

    # Auto-classify if caller didn't supply category
    if not meta.get("category"):
        ai = await classify_garment(image_url)
        meta = {**ai, **meta}  # caller-supplied values override AI

    item_id = str(uuid.uuid4())
    row = {
        "id":                item_id,
        "user_id":           user_id,
        "image_url":         image_url,
        "category":          meta.get("category", "other"),
        "colour":            meta.get("colour"),
        "brand":             meta.get("brand"),
        "tags":              meta.get("tags", []),
        "description":       meta.get("description"),
        "care_instructions": meta.get("care_instructions"),
        "notes":             meta.get("notes"),
    }
    res = sb.table("wardrobe_items").insert(row).execute()
    return res.data[0]


# ── Update ─────────────────────────────────────────────────────────────────────
@router.patch("/{item_id}")
async def update_item(item_id: str, user_id: UserId, body: WardrobeItemUpdate):
    sb      = get_supabase()
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="Nothing to update.")
    res = (
        sb.table("wardrobe_items")
        .update(payload)
        .eq("id", item_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found.")
    return res.data[0]


# ── Delete ─────────────────────────────────────────────────────────────────────
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str, user_id: UserId):
    sb  = get_supabase()
    res = (
        sb.table("wardrobe_items")
        .select("image_url")
        .eq("id", item_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found.")

    # Delete blob
    image_url: str = res.data["image_url"]
    blob_name = image_url.split(f"{CONTAINER_WARDROBE_ORIGINALS}/")[-1]
    await BlobService().delete(CONTAINER_WARDROBE_ORIGINALS, blob_name)

    sb.table("wardrobe_items").delete().eq("id", item_id).eq("user_id", user_id).execute()


# ── AI classify (preview before saving) ───────────────────────────────────────
@router.post("/classify")
async def classify_item(user_id: UserId, image: UploadFile = File(...)):  # noqa: F811
    blob      = BlobService()
    img_bytes = await image.read()
    tmp_name  = f"tmp/{uuid.uuid4()}{_ext(image.filename)}"
    url       = await blob.upload(
        data=img_bytes,
        container=CONTAINER_WARDROBE_ORIGINALS,
        blob_name=tmp_name,
        content_type=image.content_type or "image/jpeg",
    )
    if not url:
        raise HTTPException(status_code=500, detail="Upload failed.")
    result = await classify_garment(url)
    # Clean up temp blob asynchronously (fire-and-forget)
    await BlobService().delete(CONTAINER_WARDROBE_ORIGINALS, tmp_name)
    return result


def _ext(filename: str | None) -> str:
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    return ".jpg"
