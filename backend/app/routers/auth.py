"""
Modeon — Auth Router
Prefix: /api/auth

Endpoints:
  POST /verify-session  — validate JWT, auto-create user profile on first login
  POST /logout          — clear the httpOnly session cookie
"""

import logging
from functools import lru_cache
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Response, status
from supabase import Client, create_client

from app.config import settings
from app.deps import get_current_user
from app.models.profile import SessionVerifyResponse
from app.services.analytics import track

logger = logging.getLogger("modeon.auth")
router = APIRouter()

# ── Supabase service-role client (lazy initialisation) ─────────────────────────
@lru_cache(maxsize=1)
def _get_supabase() -> Client:
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )

# ── Helpers ────────────────────────────────────────────────────────────────────

_PROVIDER_MAP: Dict[str, str] = {
    "email": "email",
    "google": "google",
    "azure": "microsoft",   # Supabase names the Microsoft provider "azure"
}


def _extract_provider(current_user: Dict[str, Any]) -> str:
    """
    Read the OAuth provider from the JWT's app_metadata claim.
    Falls back to 'email' if the claim is absent or unrecognised.
    """
    app_metadata: Dict[str, Any] = current_user.get("app_metadata") or {}
    raw_provider: str = str(app_metadata.get("provider", "email")).lower()
    return _PROVIDER_MAP.get(raw_provider, "email")


def _ensure_user_profile(user_id: str) -> bool:
    """
    Check whether a user_profiles row exists for `user_id`.
    If not, create one with all preference fields null.

    Returns:
        True  — a new profile row was created (first login).
        False — row already existed.

    Uses the service-role client so RLS never blocks the operation.
    Raises HTTPException(500) on any database error.
    """
    try:
        result = (
            _get_supabase().table("user_profiles")
            .select("id")
            .eq("id", user_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:
        logger.error("Failed to query user_profiles for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    if result.data:
        return False

    # First login — create the profile row
    try:
        _get_supabase().table("user_profiles").insert(
            {
                "id": user_id,
                "style_archetypes": None,
                "occasion_prefs": None,
                "colour_palette": None,
                "gender_pref": None,
            }
        ).execute()
    except Exception as exc:
        logger.error("Failed to create user_profiles row for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    return True


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post(
    "/verify-session",
    response_model=SessionVerifyResponse,
    summary="Verify the current session JWT and bootstrap the user profile.",
)
async def verify_session(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> SessionVerifyResponse:
    """
    Validates the caller's JWT (handled by the `get_current_user` dependency).

    On the very first login:
      - Creates a `user_profiles` row with null preference fields.
      - Fires the `user_registered` PostHog event.

    Returns session validity plus user identity.
    """
    user_id: str = current_user["user_id"]
    email: str = current_user.get("email") or ""

    is_new_user = _ensure_user_profile(user_id)

    if is_new_user:
        provider = _extract_provider(current_user)
        track(
            user_id=user_id,
            event="user_registered",
            properties={"method": provider},
        )
        logger.info(
            "New user profile created for user_id=%s (provider=%s)",
            user_id,
            provider,
        )

    return SessionVerifyResponse(
        valid=True,
        user_id=user_id,
        email=email,
    )


@router.post(
    "/logout",
    summary="Clear the session cookie and log the user out.",
)
async def logout(response: Response) -> Dict[str, bool]:
    """
    Clears the `sb-access-token` httpOnly cookie.
    No auth dependency — reachable even with an expired token.
    """
    is_production = settings.ENVIRONMENT == "production"

    response.set_cookie(
        key="sb-access-token",
        value="",
        max_age=0,
        httponly=True,
        samesite="lax",
        secure=is_production,
    )

    return {"success": True}
