"""
Modeon — Security Middleware

SecurityHeadersMiddleware: Injects HTTP security headers on every response.
RateLimitMiddleware:       In-memory per-IP sliding-window rate limiter.

WARNING: RateLimitMiddleware is NOT suitable for multi-instance deployments
         without a shared Redis store. Phase 2 should replace _rate_store with
         a Redis-backed counter. On production startup a warning is logged.
"""

import logging
import time
from collections import defaultdict, deque
from typing import Callable, Deque

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger("modeon.middleware")

# ── Security Headers ───────────────────────────────────────────────────────────

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob: https://*.blob.core.windows.net; "
        "connect-src 'self' https://app.posthog.com https://*.supabase.co; "
        "frame-ancestors 'none';"
    ),
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Append HTTP security headers to every outgoing response.

    ORDER MATTERS: This middleware must be added AFTER CORSMiddleware so that
    OPTIONS preflight responses (handled by CORS) are not disrupted.
    CORSMiddleware runs first (outermost), SecurityHeadersMiddleware runs second.

    The middleware only appends headers — it never overwrites headers already
    set by CORS middleware (e.g. Access-Control-*).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            # setdefault-style: don't clobber headers CORS already set
            if header not in response.headers:
                response.headers[header] = value
        return response


# ── Rate Limiting ──────────────────────────────────────────────────────────────

# Sliding-window buckets: maps IP → deque of timestamps (seconds, float)
_rate_store: defaultdict[str, Deque[float]] = defaultdict(deque)

# Default limits (Phase 1)
_DEFAULT_LIMIT = 60        # requests
_DEFAULT_WINDOW = 60       # seconds

# Tighter limits for expensive endpoints
_UPLOAD_LIMIT = 20
_UPLOAD_WINDOW = 60

# Path prefixes that use the tighter upload limit
_UPLOAD_PREFIXES = (
    "/api/wardrobe",
    "/api/shopping",
    "/api/outfit-check",
)


def _get_client_ip(request: Request) -> str:
    """
    Return the real client IP.
    Respects X-Forwarded-For when present (Railway reverse proxy).
    Falls back to the raw connection IP.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _is_rate_limited(ip: str, limit: int, window: int) -> bool:
    """
    Sliding-window rate limiter.
    Returns True if `ip` has exceeded `limit` requests in the last `window` seconds.
    Mutates `_rate_store` in-place.
    """
    now = time.monotonic()
    bucket: Deque[float] = _rate_store[ip]

    # Evict timestamps outside the window
    cutoff = now - window
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()

    if len(bucket) >= limit:
        return True

    bucket.append(now)
    return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP sliding-window rate limiter.

    - Default: 60 requests / 60 seconds per IP.
    - Upload endpoints: 20 requests / 60 seconds per IP.
    - /health is excluded from rate limiting.

    ⚠️  In-memory only — not suitable for multi-instance deployments.
        Replace _rate_store with Redis in Phase 2.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        if settings.ENVIRONMENT == "production":
            logger.warning(
                "RateLimitMiddleware is using in-memory storage. "
                "This is NOT suitable for multi-instance production deployments. "
                "Replace with a Redis-backed store in Phase 2."
            )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path: str = request.url.path

        # Health check is never rate-limited
        if path == "/health":
            return await call_next(request)

        ip = _get_client_ip(request)

        # Choose limit bucket based on path
        if any(path.startswith(prefix) for prefix in _UPLOAD_PREFIXES):
            limit, window = _UPLOAD_LIMIT, _UPLOAD_WINDOW
        else:
            limit, window = _DEFAULT_LIMIT, _DEFAULT_WINDOW

        if _is_rate_limited(ip, limit, window):
            logger.warning(
                "Rate limit exceeded: ip=%s path=%s limit=%d window=%ds",
                ip, path, limit, window,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please slow down and try again shortly."
                },
                headers={"Retry-After": str(window)},
            )

        return await call_next(request)
