import logging
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client, create_client

from app.config import settings
from app.deps import get_current_user
from app.models.profile import (
    OnboardingCompleteRequest,
    OnboardingSkipRequest,
    ProfileResponse,
    ProfileUpdateRequest,
)
from app.services.analytics import track

logger = logging.getLogger('modeon.profile')
router = APIRouter()


@lru_cache(maxsize=1)
def _get_supabase() -> Client:
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )


def _fetch_profile(user_id: str) -> dict[str, Any]:
    try:
        result = (
            _get_supabase().table('user_profiles')
            .select('*')
            .eq('id', user_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        logger.error('Failed to fetch profile for user %s: %s', user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Database error',
        )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found. Please complete verification first.',
        )

    return result.data


def _update_profile(user_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    payload = {**updates, 'updated_at': datetime.now(timezone.utc).isoformat()}
    try:
        result = (
            _get_supabase().table('user_profiles')
            .update(payload)
            .eq('id', user_id)
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        logger.error('Failed to update profile for user %s: %s', user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Database error',
        )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found. Please complete verification first.',
        )

    return result.data[0]


@router.get('/', response_model=ProfileResponse, summary="Fetch the current user's style profile.")
async def get_profile(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ProfileResponse:
    row = _fetch_profile(current_user['user_id'])
    return ProfileResponse.from_db_row(row)


@router.put('/', response_model=ProfileResponse, summary="Partially update the current user's style profile.")
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ProfileResponse:
    user_id = current_user['user_id']
    updates = {field: getattr(body, field) for field in body.model_fields_set}

    if not updates:
        row = _fetch_profile(user_id)
        return ProfileResponse.from_db_row(row)

    updated_row = _update_profile(user_id, updates)

    if 'style_archetypes' in body.model_fields_set:
        track(
            user_id=user_id,
            event='onboarding_step_completed',
            properties={'step': 1, 'field': 'style_archetypes'},
        )

    return ProfileResponse.from_db_row(updated_row)


@router.post(
    '/onboarding/complete',
    response_model=ProfileResponse,
    summary='Save all onboarding answers in a single upsert.',
)
async def onboarding_complete(
    body: OnboardingCompleteRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ProfileResponse:
    user_id = current_user['user_id']
    onboarding_fields = {'style_archetypes', 'occasion_prefs', 'colour_palette', 'gender_pref'}
    updates = {
        field: getattr(body, field)
        for field in body.model_fields_set
        if field in onboarding_fields
    }

    updated_row = _update_profile(user_id, updates) if updates else _fetch_profile(user_id)

    analytics_props: dict[str, Any] = {}
    if body.duration_seconds is not None:
        analytics_props['duration_seconds'] = body.duration_seconds

    track(user_id=user_id, event='onboarding_complete', properties=analytics_props)
    return ProfileResponse.from_db_row(updated_row)


@router.post('/onboarding/skip', summary='Record that the user skipped onboarding (analytics only).')
async def onboarding_skip(
    body: OnboardingSkipRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, bool]:
    user_id = current_user['user_id']
    track(
        user_id=user_id,
        event='onboarding_skipped',
        properties={'step_skipped_at': body.step_skipped_at},
    )
    return {'skipped': True}
