"""
Backward-compatible Azure Blob service exports.

The real implementation lives in `app.services.blob_service`.
"""

from app.services.blob_service import (
    BlobService,
    CONTAINER_WARDROBE_ORIGINALS,
    CONTAINER_WARDROBE_THUMBS,
    CONTAINER_SHOPPING_UPLOADS,
)

try:
    from app.services.blob_service import blob_service
except ImportError:
    blob_service = BlobService()

__all__ = [
    "BlobService",
    "blob_service",
    "CONTAINER_WARDROBE_ORIGINALS",
    "CONTAINER_WARDROBE_THUMBS",
    "CONTAINER_SHOPPING_UPLOADS",
]
