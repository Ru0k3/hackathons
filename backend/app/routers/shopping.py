"""
shopping.py  —  /api/shopping
Shopping wishlist management and AI gap-analysis recommendations.
"""
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.auth_dep import get_current_user
from app.services.blob_service import BlobService, CONTAINER_SHOPPING_UPLOADS
from app.services.openai_service import shopping_recommendations
from app.services.supabase_service import get_supabase

logger = logging.getLogger("modeon.shopping")
router = APIRouter()

UserId = Annotated[str, Depends(get_current_user)]


class ShoppingItemCreate(BaseModel):
    name:      str
    category:  str | None = None
    colour:    str | None = None
    url:       str | None = None
    notes:     str | None = None
    image_url: str | None = None


class ShoppingItemUpdate(BaseModel):
    name:      str | None = None
    category:  str | None = None
    colour:    str | None = None
    url:       str | None = None
    notes:     str | None = None
    purchased: bool | None = None


class RecommendRequest(BaseModel):
    occasion:    str | None = None
    style_goal:  str | None = None


@router.get("")
async def get_shopping_list(user_id: UserId):
    sb  = get_supabase()
    res = (
        sb.table("shopping_items")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"items": res.data}


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_shopping_item(user_id: UserId, body: ShoppingItemCreate):
    sb  = get_supabase()
    row = {"id": str(uuid.uuid4()), "user_id": user_id, **body.model_dump()}
    res = sb.table("shopping_items").insert(row).execute()
    return res.data[0]


@router.patch("/{item_id}")
async def update_shopping_item(item_id: str, user_id: UserId, body: ShoppingItemUpdate):
    sb      = get_supabase()
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="Nothing to update.")
    res = (
        sb.table("shopping_items")
        .update(payload)
        .eq("id", item_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Item not found.")
    return res.data[0]


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_item(item_id: str, user_id: UserId):
    sb = get_supabase()
    sb.table("shopping_items").delete().eq("id", item_id).eq("user_id", user_id).execute()


@router.post("/upload")
async def upload_shopping_image(user_id: UserId, image: UploadFile = File(...)):
    blob      = BlobService()
    img_bytes = await image.read()
    blob_name = f"{user_id}/{uuid.uuid4()}.jpg"
    url       = await blob.upload(
        data=img_bytes,
        container=CONTAINER_SHOPPING_UPLOADS,
        blob_name=blob_name,
        content_type=image.content_type or "image/jpeg",
    )
    if not url:
        raise HTTPException(status_code=500, detail="Upload failed.")

    sb  = get_supabase()
    row = {"id": str(uuid.uuid4()), "user_id": user_id, "name": "Inspo", "image_url": url}
    res = sb.table("shopping_items").insert(row).execute()
    return {"url": url, "item_id": res.data[0]["id"]}


@router.post("/recommend")
async def get_recommendations(user_id: UserId, body: RecommendRequest):
    sb       = get_supabase()
    wardrobe = (
        sb.table("wardrobe_items")
        .select("id, category, colour, tags, description")
        .eq("user_id", user_id)
        .execute()
    ).data or []

    if not wardrobe:
        raise HTTPException(status_code=400, detail="Wardrobe is empty.")

    recs = await shopping_recommendations(wardrobe, body.model_dump(exclude_none=True))
    return {"recommendations": recs}
