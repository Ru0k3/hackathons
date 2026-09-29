"""
Compatibility scoring for outfit combinations.
"""

from __future__ import annotations

import json
from typing import Any

from app.services.ai_service import ai_service
from app.services.azure_openai import chat_complete


async def _chat_json(messages: list[dict], model: str = "mini", max_tokens: int = 500) -> dict[str, Any]:
    chat_json = getattr(ai_service, "chat_json", None)
    if callable(chat_json):
        data = await chat_json(messages, model=model, max_tokens=max_tokens)
        return data if isinstance(data, dict) else {}

    raw = await chat_complete(messages, model=model, max_tokens=max_tokens)
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _clamp_score(value: Any) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, score))


async def score_outfit(item_ids: list[str], wardrobe_metadata: list[dict]) -> dict[str, Any]:
    """
    Return a compatibility score (0-100) and explanation for the selected outfit.
    """
    selected_ids = {str(item_id) for item_id in item_ids if item_id}
    selected_items = [
        item
        for item in wardrobe_metadata
        if str(item.get("id")) in selected_ids
    ]

    if not selected_items:
        return {
            "score": 0,
            "explanation": "No matching wardrobe items found for scoring.",
        }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a fashion compatibility expert. Evaluate the outfit and "
                "return ONLY valid JSON with keys `score` (0-100 integer) and "
                "`explanation` (brief text)."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "selected_item_ids": list(selected_ids),
                    "selected_items": selected_items,
                },
                ensure_ascii=False,
            ),
        },
    ]

    result = await _chat_json(messages, model="mini", max_tokens=400)
    score = _clamp_score(result.get("score"))
    explanation = str(
        result.get("explanation")
        or "These pieces can work together with balanced colours and formality."
    )
    return {"score": score, "explanation": explanation}
