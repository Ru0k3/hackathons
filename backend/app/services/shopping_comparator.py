"""
Modeon — Shopping Comparator Service

Wraps the GPT-4o vision comparison flow for shopping items against
the user's existing wardrobe.
"""

import base64
import json
import logging

from app.config import settings
from app.services.ai_service import ai_service

logger = logging.getLogger("modeon.shopping_comparator")


async def compare_shopping_item(
    user_id: str,
    shopping_item_blob_path: str,
    shopping_item_bytes: bytes,
    wardrobe_metadata: list[dict],
) -> dict:
    """
    Use GPT-4o (vision) to assess whether a shopping item complements the
    user's existing wardrobe and suggest specific outfit combinations.

    Returns a validated response dict matching ShoppingCompareResponse shape.
    """
    # Encode image as base64 for the model
    encoded_image = base64.b64encode(shopping_item_bytes).decode("utf-8")

    context: dict = {
        "shopping_item": encoded_image,
        "wardrobe": wardrobe_metadata,
        "question": "Does this item complement the user's existing wardrobe?",
    }

    ai_response = await ai_service.complete(
        prompt_key="shopping_compare",
        user_message=json.dumps(context),
        timeout=5.0,
        use_large_model=True,
        user_id=user_id,
    )

    # Apply low_confidence_warning based on threshold
    confidence: float = float(ai_response.get("confidence", 0.0))
    if confidence < settings.CONTENT_SAFETY_THRESHOLD:
        ai_response["low_confidence_warning"] = True
    else:
        ai_response["low_confidence_warning"] = ai_response.get("low_confidence_warning", False)

    # Validate item_ids in suggested_combinations against the wardrobe
    valid_wardrobe_ids: set[str] = {item["id"] for item in wardrobe_metadata}
    raw_combinations: list[dict] = ai_response.get("suggested_combinations") or []
    validated_combinations: list[dict] = []

    for combo in raw_combinations:
        ids: list[str] = combo.get("item_ids") or []
        if ids and all(iid in valid_wardrobe_ids for iid in ids):
            validated_combinations.append(combo)
        else:
            logger.warning(
                "shopping_compare: dropped combination with invalid item_ids: %s", ids
            )

    ai_response["suggested_combinations"] = validated_combinations
    return ai_response
