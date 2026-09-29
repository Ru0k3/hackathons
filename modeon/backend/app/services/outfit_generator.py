"""
Outfit generation helpers backed by the shared AI service.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from app.services.ai_service import ai_service
from app.services.azure_openai import chat_complete

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"

_DAILY_FALLBACK_PROMPT = (
    "You are a professional fashion stylist. Return ONLY valid JSON with keys "
    "`item_ids` (array of wardrobe item ids) and `explanation` (short text)."
)

_OCCASION_FALLBACK_PROMPT = (
    "You are a professional fashion stylist. Build one occasion-focused outfit "
    "using ONLY the wardrobe item ids provided. Return ONLY valid JSON as "
    '{ "item_ids": ["id1", "id2"], "explanation": "..." }.'
)


def _load_system_prompt(filename: str, fallback: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.exists():
        return fallback
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return fallback
    system = parsed.get("system")
    if isinstance(system, str) and system.strip():
        return system.strip()
    return fallback


async def _chat_json(messages: list[dict], model: str = "mini", max_tokens: int = 900) -> dict[str, Any]:
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


def _normalise_outfit(payload: dict[str, Any], fallback_items: list[dict]) -> dict[str, Any]:
    item_ids = payload.get("item_ids")
    if not isinstance(item_ids, list):
        item_ids = []
    item_ids = [str(item_id) for item_id in item_ids if item_id]
    if not item_ids and fallback_items:
        item_ids = [str(item["id"]) for item in fallback_items[:3] if item.get("id")]
    explanation = str(payload.get("explanation") or "A balanced outfit tailored to your wardrobe.")
    return {"item_ids": item_ids, "explanation": explanation}


async def generate_daily_outfit(
    user_id: str,
    wardrobe_items: list[dict],
    style_profile: dict | None,
) -> dict[str, Any]:
    """
    Generate a single daily outfit recommendation.
    """
    system_prompt = _load_system_prompt("daily_outfit.yaml", _DAILY_FALLBACK_PROMPT)
    user_payload = {
        "user_id": user_id,
        "wardrobe": wardrobe_items,
        "style_profile": style_profile or {},
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]
    result = await _chat_json(messages, model="mini", max_tokens=700)
    return _normalise_outfit(result, wardrobe_items)


async def generate_occasion_outfit(
    user_id: str,
    occasion: str,
    description: str | None,
    wardrobe_items: list[dict],
) -> dict[str, Any]:
    """
    Generate a single occasion-specific outfit recommendation.
    """
    system_prompt = _load_system_prompt("swipe_ranking.yaml", _OCCASION_FALLBACK_PROMPT)
    user_payload = {
        "user_id": user_id,
        "occasion": occasion,
        "description": description or "",
        "requested_outfits": 1,
        "wardrobe": wardrobe_items,
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]
    result = await _chat_json(messages, model="large", max_tokens=900)

    if isinstance(result.get("outfits"), list) and result["outfits"]:
        first = result["outfits"][0]
        if isinstance(first, dict):
            return _normalise_outfit(first, wardrobe_items)
    return _normalise_outfit(result, wardrobe_items)
