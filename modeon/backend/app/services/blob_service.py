"""
blob_service.py
Thin async wrapper around azure-storage-blob.
All public methods return URLs or booleans; they never raise — callers
decide what to do with failures.
"""
import asyncio
import logging
import uuid
from io import BytesIO

from azure.core.exceptions import AzureError
from azure.storage.blob.aio import BlobServiceClient

from app.config import settings

logger = logging.getLogger("modeon.blob")

# ── Container names ────────────────────────────────────────────────────────────
CONTAINER_WARDROBE_ORIGINALS = "wardrobe-originals"
CONTAINER_WARDROBE_THUMBS    = "wardrobe-thumbs"
CONTAINER_SHOPPING_UPLOADS   = "shopping-uploads"


def _make_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(
        settings.AZURE_BLOB_CONN_STRING
    )


class BlobService:
    """Async Azure Blob operations scoped to a single request."""

    def __init__(self):
        self._client = _make_client()

    # ── Upload ─────────────────────────────────────────────────────────────────
    async def upload(
        self,
        data: bytes,
        container: str,
        blob_name: str | None = None,
        content_type: str = "application/octet-stream",
    ) -> str | None:
        """Upload bytes and return the public blob URL, or None on failure."""
        blob_name = blob_name or str(uuid.uuid4())
        try:
            async with self._client:
                container_client = self._client.get_container_client(container)
                await container_client.upload_blob(
                    name=blob_name,
                    data=BytesIO(data),
                    overwrite=True,
                    content_settings={"content_type": content_type},
                )
            account = settings.AZURE_BLOB_ACCOUNT_NAME
            return (
                f"https://{account}.blob.core.windows.net"
                f"/{container}/{blob_name}"
            )
        except AzureError as exc:
            logger.error("Blob upload failed [%s/%s]: %s", container, blob_name, exc)
            return None

    # ── Delete single blob ─────────────────────────────────────────────────────
    async def delete(self, container: str, blob_name: str) -> bool:
        try:
            async with self._client:
                blob_client = self._client.get_blob_client(
                    container=container, blob=blob_name
                )
                await blob_client.delete_blob(delete_snapshots="include")
            return True
        except AzureError as exc:
            logger.warning(
                "Blob delete failed [%s/%s]: %s", container, blob_name, exc
            )
            return False

    # ── Delete all blobs with a given prefix (user_id) ────────────────────────
    async def delete_user_blobs(
        self, container: str, user_id: str | None = None
    ) -> bool:
        """Delete all blobs whose name starts with user_id/."""
        prefix = f"{user_id}/" if user_id else ""
        try:
            async with self._client:
                container_client = self._client.get_container_client(container)
                blobs = [
                    b.name
                    async for b in container_client.list_blobs(
                        name_starts_with=prefix
                    )
                ]
                tasks = [
                    container_client.delete_blob(b, delete_snapshots="include")
                    for b in blobs
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
            return True
        except AzureError as exc:
            logger.error(
                "Bulk blob delete failed [%s, prefix=%s]: %s",
                container, prefix, exc,
            )
            return False


# Backward-compatible singleton used by older routers.
blob_service = BlobService()
