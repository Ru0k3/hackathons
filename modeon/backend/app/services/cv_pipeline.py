"""
Modeon — CV Pipeline (BackgroundTask)

Runs after wardrobe upload returns to the client. Never raises unhandled
exceptions — all errors are caught, logged, and reported to PostHog.

Pipeline steps:
  1. rembg background removal (non-fatal if it fails)
  2. Azure Content Safety moderation
  3. Pillow thumbnail generation + upload
  4. GPT-4o-mini tag refinement + alt-text generation
  5. Supabase wardrobe_items row update
"""

import asyncio
import base64
import io
import json
import logging
from typing import Any, Dict, Optional

from supabase import Client, create_client

from app.config import settings
from app.services.analytics import track
from app.services.blob_service import (
    CONTAINER_WARDROBE_ORIGINALS,
    CONTAINER_WARDROBE_THUMBS,
    blob_service,
)

logger = logging.getLogger("modeon.cv_pipeline")

# ── Supabase service-role client ───────────────────────────────────────────────
_supabase_client: Client | None = None


def _get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _supabase_client

# ── Azure OpenAI client (lazy — avoids import-time failures in tests) ──────────
_openai_client: Any = None


def _get_openai_client() -> Any:
    global _openai_client
    if _openai_client is None:
        from openai import AzureOpenAI  # type: ignore[import]
        _openai_client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version="2024-02-01",
        )
    return _openai_client


# ── Step helpers ───────────────────────────────────────────────────────────────

def _remove_background(image_bytes: bytes) -> bytes:
    """
    Step 1 — Remove background using rembg.
    Returns RGBA PNG bytes. Falls back to original bytes on any failure.
    """
    try:
        from rembg import remove as rembg_remove  # type: ignore[import]
        result: bytes = rembg_remove(image_bytes)
        logger.debug("rembg background removal succeeded (%d bytes)", len(result))
        return result
    except Exception as exc:
        logger.warning(
            "rembg background removal failed — continuing with original image: %s", exc
        )
        return image_bytes


async def _check_content_safety(image_bytes: bytes) -> bool:
    """
    Step 2 — Azure Content Safety moderation.
    Returns True if the image passes (safe to proceed), False if rejected.
    """
    loop = asyncio.get_event_loop()

    def _sync_check() -> bool:
        from azure.ai.contentsafety import ContentSafetyClient  # type: ignore[import]
        from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData  # type: ignore[import]
        from azure.core.credentials import AzureKeyCredential  # type: ignore[import]

        client = ContentSafetyClient(
            endpoint=settings.AZURE_CONTENT_SAFETY_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_CONTENT_SAFETY_KEY),
        )
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        request = AnalyzeImageOptions(image=ImageData(content=encoded))
        response = client.analyze_image(request)

        threshold = settings.CONTENT_SAFETY_THRESHOLD
        categories = response.categories_analysis or []
        for cat in categories:
            severity = getattr(cat, "severity", 0) or 0
            # Content Safety severities: 0, 2, 4, 6 — normalise to 0–1
            normalised = severity / 6.0
            if normalised > threshold:
                logger.warning(
                    "Content Safety REJECTED — category=%s severity=%s (normalised=%.2f > threshold=%.2f)",
                    getattr(cat, "category", "unknown"),
                    severity,
                    normalised,
                    threshold,
                )
                return False
        return True

    return await loop.run_in_executor(None, _sync_check)


def _generate_thumbnail(image_bytes: bytes) -> bytes:
    """
    Step 3 — Resize to max 400×400 px (preserving aspect ratio) and encode as JPEG.
    Input may be RGBA PNG (from rembg) or the original image.
    Returns JPEG bytes.
    """
    from PIL import Image  # type: ignore[import]

    img = Image.open(io.BytesIO(image_bytes))

    # Convert RGBA → RGB (JPEG doesn't support transparency)
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img.thumbnail((400, 400), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    return buf.getvalue()


async def _call_gpt_tagging(image_bytes: bytes) -> Dict[str, Any]:
    """
    Step 4 — Call GPT-4o-mini to classify the item and generate alt-text.
    Returns a dict with tag fields; unknown/low-confidence fields are None.
    """
    # Import PROMPTS from main — loaded at startup
    try:
        from app.main import PROMPTS  # type: ignore[import]
        prompt_config: Dict[str, Any] = PROMPTS.get("cv_tagging", {})
        system_prompt: str = prompt_config.get("system", "")
    except Exception as exc:
        logger.warning("Could not load cv_tagging prompt from PROMPTS: %s", exc)
        system_prompt = (
            "You are a professional fashion classifier. "
            "Respond ONLY with valid JSON. No text before or after. No markdown fences."
        )

    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    loop = asyncio.get_event_loop()

    def _sync_call() -> str:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_MINI,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                        {"type": "text", "text": "Classify this clothing item."},
                    ],
                },
            ],
            max_tokens=300,
            temperature=0.2,
            timeout=10,
        )
        return response.choices[0].message.content or ""

    raw: str = await loop.run_in_executor(None, _sync_call)

    # Parse JSON response — fall back to all-null tags on failure
    try:
        parsed: Dict[str, Any] = json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error(
            "GPT-4o-mini returned invalid JSON for cv_tagging. Raw response: %r — Error: %s",
            raw,
            exc,
        )
        parsed = {}

    # Normalise to expected schema; any missing or null field stays None
    return {
        "category": parsed.get("category") or None,
        "colours": parsed.get("colours") or None,
        "pattern": parsed.get("pattern") or None,
        "formality": parsed.get("formality") or None,
        "seasons": parsed.get("seasons") or None,
        "alt_text": parsed.get("alt_text") or None,
    }


def _update_wardrobe_item(item_id: str, updates: Dict[str, Any]) -> None:
    """Step 5 — Write tag fields + thumb path to Supabase."""
    _get_supabase_client().table("wardrobe_items").update(updates).eq("id", item_id).execute()


def _delete_wardrobe_item(item_id: str) -> None:
    """Hard-delete the wardrobe_items row (used on moderation rejection)."""
    _get_supabase_client().table("wardrobe_items").delete().eq("id", item_id).execute()


# ── Main pipeline ──────────────────────────────────────────────────────────────

async def run_cv_pipeline(
    item_id: str,
    user_id: str,
    original_blob_path: str,
    image_bytes: bytes,
) -> None:
    """
    Full CV pipeline — runs as a FastAPI BackgroundTask.

    Must never raise unhandled exceptions. All errors are caught, logged,
    and reported to PostHog. The event loop continues regardless.
    """
    logger.info("CV pipeline started — item_id=%s user_id=%s", item_id, user_id)

    try:
        # ── Step 1: Background removal ─────────────────────────────────────────
        processed_bytes = await asyncio.get_event_loop().run_in_executor(
            None, _remove_background, image_bytes
        )

        # ── Step 2: Content Safety ─────────────────────────────────────────────
        is_safe = await _check_content_safety(processed_bytes)

        if not is_safe:
            logger.warning(
                "Moderation rejected item_id=%s — deleting blob and DB row", item_id
            )
            # Clean up original blob
            try:
                await blob_service.delete_blob(CONTAINER_WARDROBE_ORIGINALS, original_blob_path)
            except Exception as del_exc:
                logger.error("Failed to delete rejected blob %s: %s", original_blob_path, del_exc)

            # Clean up DB row
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, _delete_wardrobe_item, item_id)
            except Exception as db_exc:
                logger.error("Failed to delete rejected wardrobe_items row %s: %s", item_id, db_exc)

            track(
                user_id=user_id,
                event="moderation_rejected",
                properties={
                    "endpoint": "wardrobe_upload",
                    "container": CONTAINER_WARDROBE_ORIGINALS,
                },
            )
            return  # Pipeline ends here for rejected items

        # ── Step 3: Thumbnail generation + upload ──────────────────────────────
        thumb_path: Optional[str] = None
        try:
            thumb_bytes = await asyncio.get_event_loop().run_in_executor(
                None, _generate_thumbnail, processed_bytes
            )
            thumb_blob_path = f"{user_id}/{item_id}_thumb.jpg"
            await blob_service.upload_bytes(
                container=CONTAINER_WARDROBE_THUMBS,
                blob_path=thumb_blob_path,
                data=thumb_bytes,
                content_type="image/jpeg",
            )
            thumb_path = thumb_blob_path
            logger.debug("Thumbnail uploaded: %s", thumb_path)
        except Exception as thumb_exc:
            logger.error(
                "Thumbnail generation/upload failed for item_id=%s: %s", item_id, thumb_exc
            )
            # Non-fatal — item still usable without thumbnail

        # ── Step 4: GPT-4o-mini tag refinement + alt-text ──────────────────────
        tags: Dict[str, Any] = {}
        try:
            tags = await _call_gpt_tagging(processed_bytes)
            logger.debug("Tags from GPT-4o-mini for item_id=%s: %s", item_id, tags)
        except Exception as ai_exc:
            logger.error(
                "GPT-4o-mini tagging failed for item_id=%s: %s", item_id, ai_exc
            )
            track(
                user_id=user_id,
                event="ai_inference_error",
                properties={
                    "endpoint": "cv_tagging",
                    "error_type": type(ai_exc).__name__,
                    "model": settings.AZURE_OPENAI_DEPLOYMENT_MINI,
                },
            )
            # tags remains {} — all fields will be null in DB

        # ── Step 5: Supabase update ────────────────────────────────────────────
        db_update: Dict[str, Any] = {
            "category": tags.get("category"),
            "colours": tags.get("colours"),
            "pattern": tags.get("pattern"),
            "formality": tags.get("formality"),
            "seasons": tags.get("seasons"),
            "alt_text": tags.get("alt_text"),
        }
        if thumb_path:
            db_update["blob_thumb_path"] = thumb_path

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _update_wardrobe_item, item_id, db_update)
        logger.info("CV pipeline complete — item_id=%s", item_id)

    except Exception as exc:
        # Top-level safety net — BackgroundTask errors must not crash the worker
        logger.error(
            "CV pipeline unhandled error — item_id=%s: %s", item_id, exc, exc_info=True
        )
        track(
            user_id=user_id,
            event="ai_inference_error",
            properties={
                "endpoint": "cv_pipeline",
                "error_type": type(exc).__name__,
                "model": "pipeline",
            },
        )
