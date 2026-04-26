"""
Modeon — Preference Engine

Builds preference signals from a user's swipe history and retrieves
their available wardrobe items for outfit generation.
"""

import logging
from collections import defaultdict
from typing import Any

from supabase import create_client, Client

from app.config import settings

logger = logging.getLogger("modeon.preference_engine")


def _get_supabase() -> Client:
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )


# ── Preference Summary ─────────────────────────────────────────────────────────

async def build_preference_summary(user_id: str) -> dict[str, Any]:
    """
    Construct preference signals from the user's last 90 days of swipe history.

    Returns:
        {
            "liked_combinations": [...],    # item_ids arrays from swipe=1
            "disliked_combinations": [...], # item_ids arrays from swipe=-1
            "saved_outfits": [...],         # item_ids from is_saved=True
            "total_swipes": int,
            "has_enough_signal": bool       # True if total_swipes >= 5
        }
    """
    supabase = _get_supabase()
    empty_result: dict[str, Any] = {
        "liked_combinations": [],
        "disliked_combinations": [],
        "saved_outfits": [],
        "total_swipes": 0,
        "has_enough_signal": False,
    }

    # ── Swipe history joined with generated_outfits ────────────────────────────
    try:
        swipe_response = (
            supabase.table("outfit_swipes")
            .select(
                "swipe, outfit_id, "
                "generated_outfits!inner(item_ids, source, occasion)"
            )
            .eq("user_id", user_id)
            .gte("created_at", "now() - interval '90 days'")
            .order("created_at", desc=True)
            .execute()
        )
        swipe_rows: list[dict] = swipe_response.data or []
    except Exception as exc:
        logger.error("Failed to fetch swipe history for user %s: %s", user_id, exc)
        return empty_result

    liked_combinations: list[list[str]] = []
    disliked_combinations: list[list[str]] = []

    for row in swipe_rows:
        outfit = row.get("generated_outfits") or {}
        item_ids: list[str] = outfit.get("item_ids") or []
        direction: int = row.get("swipe", 0)
        if direction == 1:
            liked_combinations.append(item_ids)
        elif direction == -1:
            disliked_combinations.append(item_ids)

    # Cap at most recent 20 each
    liked_combinations = liked_combinations[:20]
    disliked_combinations = disliked_combinations[:20]
    total_swipes = len(swipe_rows)

    # ── Saved outfits ──────────────────────────────────────────────────────────
    try:
        saved_response = (
            supabase.table("generated_outfits")
            .select("item_ids")
            .eq("user_id", user_id)
            .eq("is_saved", True)
            .gte("created_at", "now() - interval '90 days'")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        saved_rows: list[dict] = saved_response.data or []
    except Exception as exc:
        logger.error("Failed to fetch saved outfits for user %s: %s", user_id, exc)
        saved_rows = []

    saved_outfits: list[list[str]] = [
        row["item_ids"] for row in saved_rows if row.get("item_ids")
    ]

    return {
        "liked_combinations": liked_combinations,
        "disliked_combinations": disliked_combinations,
        "saved_outfits": saved_outfits,
        "total_swipes": total_swipes,
        "has_enough_signal": total_swipes >= 5,
    }


# ── Available Wardrobe ─────────────────────────────────────────────────────────

async def get_available_wardrobe(user_id: str, limit: int = 30) -> list[dict[str, Any]]:
    """
    Fetch the user's available (non-archived, non-laundry) wardrobe items.

    If more than `limit` items exist, applies category-diversity round-robin
    selection to return a balanced set of up to `limit` items.

    Returns list of dicts with only safe, non-blob fields.
    """
    supabase = _get_supabase()

    try:
        response = (
            supabase.table("wardrobe_items")
            .select("id, category, colours, pattern, formality, seasons, custom_tags, created_at")
            .eq("user_id", user_id)
            .eq("is_archived", False)
            .eq("is_in_laundry", False)
            .order("created_at", desc=True)
            .execute()
        )
        rows: list[dict] = response.data or []
    except Exception as exc:
        logger.error("Failed to fetch wardrobe for user %s: %s", user_id, exc)
        return []

    if len(rows) <= limit:
        return [_safe_item_dict(row) for row in rows]

    # ── Category-diversity round-robin ─────────────────────────────────────────
    # Group by category (rows already sorted by created_at DESC)
    by_category: defaultdict[str, list[dict]] = defaultdict(list)
    for row in rows:
        cat = row.get("category") or "unknown"
        by_category[cat].append(row)

    selected: list[dict] = []
    categories = list(by_category.keys())
    category_indices: dict[str, int] = {cat: 0 for cat in categories}

    while len(selected) < limit:
        added_this_round = 0
        for cat in categories:
            if len(selected) >= limit:
                break
            idx = category_indices[cat]
            if idx < len(by_category[cat]):
                selected.append(by_category[cat][idx])
                category_indices[cat] += 1
                added_this_round += 1
        if added_this_round == 0:
            # All categories exhausted
            break

    return [_safe_item_dict(row) for row in selected]


def _safe_item_dict(row: dict) -> dict[str, Any]:
    """Return only the fields safe to send to the AI (no blob paths, no PII)."""
    return {
        "id": str(row["id"]),
        "category": row.get("category"),
        "colours": row.get("colours") or [],
        "pattern": row.get("pattern"),
        "formality": row.get("formality"),
        "seasons": row.get("seasons") or [],
        "custom_tags": row.get("custom_tags") or [],
    }
