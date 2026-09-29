import asyncio
import io
import json
import logging
import zipfile
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import StreamingResponse

from app.auth_dep import get_current_user
from app.services.analytics import track
from app.services.blob_service import (
    BlobService,
    CONTAINER_SHOPPING_UPLOADS,
    CONTAINER_WARDROBE_ORIGINALS,
    CONTAINER_WARDROBE_THUMBS,
)
from app.services.supabase_service import get_supabase

logger = logging.getLogger('modeon.gdpr')
router = APIRouter()


def _select_rows(table: str, user_id: str, col: str = 'user_id') -> list[dict]:
    supabase = get_supabase()
    try:
        response = (
            supabase.table(table)
            .select('*')
            .eq(col, user_id)
            .execute()
        )
        return response.data or []
    except Exception as exc:  # noqa: BLE001
        logger.warning('Failed reading %s for user %s: %s', table, user_id, exc)
        return []


def _select_single_profile(user_id: str) -> dict:
    supabase = get_supabase()
    try:
        response = (
            supabase.table('user_profiles')
            .select('*')
            .eq('id', user_id)
            .maybe_single()
            .execute()
        )
        return response.data or {}
    except Exception as exc:  # noqa: BLE001
        logger.warning('Failed reading user_profiles for user %s: %s', user_id, exc)
        return {}


@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user_id: str = Depends(get_current_user),
) -> Response:
    """
    Delete user data from DB + blob storage.
    Route path: DELETE /api/account
    """
    supabase = get_supabase()

    deletion_plan = [
        ('outfit_swipes', 'user_id'),
        ('outfit_checks', 'user_id'),
        ('generated_outfits', 'user_id'),
        ('outfits', 'user_id'),
        ('shopping_list_items', 'user_id'),
        ('shopping_items', 'user_id'),
        ('wardrobe_items', 'user_id'),
        ('user_profiles', 'id'),
    ]

    for table, col in deletion_plan:
        try:
            supabase.table(table).delete().eq(col, user_id).execute()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                'Delete failed for table=%s col=%s user=%s: %s',
                table,
                col,
                user_id,
                exc,
            )

    blob_service = BlobService()
    await asyncio.gather(
        blob_service.delete_user_blobs(CONTAINER_WARDROBE_ORIGINALS, user_id),
        blob_service.delete_user_blobs(CONTAINER_WARDROBE_THUMBS, user_id),
        blob_service.delete_user_blobs(CONTAINER_SHOPPING_UPLOADS, user_id),
        return_exceptions=True,
    )

    track(user_id, 'account_deleted', {})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/export')
async def export_account(
    user_id: str = Depends(get_current_user),
) -> dict:
    """
    GDPR data portability endpoint.
    Route path: GET /api/account/export
    """
    payload = {
        'user_id': user_id,
        'exported_at': datetime.now(timezone.utc).isoformat(),
        'profile': _select_single_profile(user_id),
        'wardrobe_items': _select_rows('wardrobe_items', user_id),
        'outfits': _select_rows('outfits', user_id),
        'generated_outfits': _select_rows('generated_outfits', user_id),
        'outfit_checks': _select_rows('outfit_checks', user_id),
        'shopping_items': _select_rows('shopping_items', user_id),
        'shopping_list_items': _select_rows('shopping_list_items', user_id),
        'outfit_swipes': _select_rows('outfit_swipes', user_id),
    }
    return payload


@router.get('/export/wardrobe')
async def export_wardrobe_zip(
    user_id: str = Depends(get_current_user),
) -> StreamingResponse:
    """
    Export wardrobe metadata as a ZIP containing wardrobe.json.
    Route path: GET /api/account/export/wardrobe
    """
    wardrobe_items = _select_rows('wardrobe_items', user_id)

    data = json.dumps(wardrobe_items, default=str, ensure_ascii=True, indent=2)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, mode='w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('wardrobe.json', data)
    stream.seek(0)

    headers = {'Content-Disposition': 'attachment; filename=wardrobe-export.zip'}
    return StreamingResponse(stream, media_type='application/zip', headers=headers)
