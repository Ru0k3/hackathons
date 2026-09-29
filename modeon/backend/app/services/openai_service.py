"""
openai_service.py
Async wrapper around the Azure OpenAI chat completions API.
All methods accept plain Python objects and return parsed dicts/strings.
"""
import json
import logging
from typing import Any

from openai import AsyncAzureOpenAI

from app.config import settings

logger = logging.getLogger("modeon.openai")


def _client(deployment: str) -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_KEY,
        azure_deployment=deployment,
        api_version="2024-02-01",
    )


MINI  = settings.AZURE_OPENAI_DEPLOYMENT_MINI
LARGE = settings.AZURE_OPENAI_DEPLOYMENT_LARGE


async def _chat(
    messages: list[dict],
    deployment: str = MINI,
    json_mode: bool = False,
    max_tokens: int = 1024,
) -> str:
    """Low-level chat call; returns the raw text content."""
    kwargs: dict[str, Any] = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    client = _client(deployment)
    resp = await client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


# ── Public helpers ─────────────────────────────────────────────────────────────

async def classify_garment(image_url: str) -> dict:
    """
    Given a public image URL, return:
      { category, colour, tags: [], description, care_instructions }
    """
    prompt = (
        "You are a fashion AI. Analyse the garment in this image and respond "
        "ONLY with valid JSON matching this schema:\n"
        '{ "category": string, "colour": string, "tags": string[], '
        '"description": string, "care_instructions": string }\n'
        "Be concise. category must be one of: tops, bottoms, outerwear, "
        "shoes, accessories, dresses, suits."
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text",      "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]
    raw = await _chat(messages, deployment=LARGE, json_mode=True, max_tokens=512)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error("classify_garment: invalid JSON response: %s", raw)
        return {}


async def generate_outfits(
    wardrobe_summary: list[dict],
    occasion: str,
    weather: str | None = None,
    mood: str | None = None,
    n: int = 3,
) -> list[dict]:
    """
    Generate n outfit suggestions from the wardrobe summary.
    Returns a list of { name, item_ids, reasoning }.
    """
    context_parts = [f"Occasion: {occasion}"]
    if weather:
        context_parts.append(f"Weather: {weather}")
    if mood:
        context_parts.append(f"Mood/vibe: {mood}")
    context = ". ".join(context_parts)

    wardrobe_json = json.dumps(wardrobe_summary, ensure_ascii=False)
    prompt = (
        f"You are a personal stylist. The user's wardrobe (as JSON): {wardrobe_json}\n\n"
        f"Context: {context}\n\n"
        f"Suggest {n} outfits using ONLY items from this wardrobe. "
        "Respond ONLY with valid JSON: "
        '{ "outfits": [{ "name": string, "item_ids": string[], "reasoning": string }] }'
    )
    raw = await _chat(
        [{"role": "user", "content": prompt}],
        deployment=LARGE,
        json_mode=True,
        max_tokens=1024,
    )
    try:
        return json.loads(raw).get("outfits", [])
    except json.JSONDecodeError:
        logger.error("generate_outfits: invalid JSON: %s", raw)
        return []


async def check_outfit(image_url: str, context: dict) -> dict:
    """
    Score and critique an outfit photo.
    Returns { score, verdict, pros, cons, suggestions, detected_items }.
    """
    occasion    = context.get("occasion", "general")
    weather     = context.get("weather", "")
    style_goal  = context.get("style_goal", "")

    prompt = (
        "You are a fashion critic. Look at this outfit photo and provide "
        "honest, constructive feedback.\n"
        f"Occasion: {occasion}. Weather: {weather}. Style goal: {style_goal}.\n"
        "Respond ONLY with valid JSON:\n"
        "{ \"score\": number (0-100), \"verdict\": string, "
        "\"pros\": string[], \"cons\": string[], "
        "\"suggestions\": string[], \"detected_items\": string[] }"
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text",      "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]
    raw = await _chat(messages, deployment=LARGE, json_mode=True, max_tokens=768)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error("check_outfit: invalid JSON: %s", raw)
        return {}


async def mix_match(item: dict, wardrobe: list[dict], occasion: str | None = None) -> list[list[dict]]:
    """Return 3 lists of items that pair well with the given item."""
    wardrobe_json = json.dumps(wardrobe, ensure_ascii=False)
    item_json     = json.dumps(item, ensure_ascii=False)
    occ           = occasion or "everyday"

    prompt = (
        f"You are a personal stylist. The user wants to style this item: {item_json}\n"
        f"Their wardrobe: {wardrobe_json}\n"
        f"Occasion: {occ}\n"
        "Suggest 3 complete looks using ONLY items from the wardrobe. "
        'Respond ONLY with valid JSON: { "looks": [[item_id_string, ...], ...] }'
    )
    raw = await _chat(
        [{"role": "user", "content": prompt}],
        deployment=MINI,
        json_mode=True,
        max_tokens=512,
    )
    try:
        return json.loads(raw).get("looks", [])
    except json.JSONDecodeError:
        return []


async def occasion_styling(
    wardrobe: list[dict], occasion: str, extra: dict | None = None
) -> list[dict]:
    """Full occasion-based styling with extra context (date, weather, etc.)."""
    return await generate_outfits(
        wardrobe_summary=wardrobe,
        occasion=occasion,
        weather=extra.get("weather") if extra else None,
        mood=extra.get("mood") if extra else None,
    )


async def shopping_recommendations(
    wardrobe: list[dict], params: dict
) -> list[dict]:
    """Identify wardrobe gaps and recommend items to buy."""
    wardrobe_json = json.dumps(wardrobe, ensure_ascii=False)
    occasion  = params.get("occasion", "versatile everyday wear")
    style     = params.get("style_goal", "")

    prompt = (
        f"You are a personal stylist. Analyse this wardrobe: {wardrobe_json}\n"
        f"The user wants to improve for: {occasion}. Style goal: {style}.\n"
        "Identify 5 key gaps and recommend specific items to buy. "
        "Respond ONLY with valid JSON:\n"
        "{ \"recommendations\": [{ \"item\": string, \"reason\": string, "
        "\"priority\": \"high\"|\"medium\"|\"low\", \"approximate_budget\": string }] }"
    )
    raw = await _chat(
        [{"role": "user", "content": prompt}],
        deployment=MINI,
        json_mode=True,
        max_tokens=768,
    )
    try:
        return json.loads(raw).get("recommendations", [])
    except json.JSONDecodeError:
        return []
