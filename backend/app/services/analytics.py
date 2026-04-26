"""
Modeon — Analytics Service

Lightweight PostHog wrapper for server-side event tracking.
All routers import `track()` from this module.

In development, events are logged to console instead of being sent to PostHog,
so dev traffic never pollutes production analytics.

Usage:
    from app.services.analytics import track

    track(
        user_id="uuid-string",
        event="user_registered",
        properties={"method": "google"},
    )
"""

import logging
from typing import Any, Dict

from app.config import settings

logger = logging.getLogger("modeon.analytics")

# ── PostHog client initialisation ──────────────────────────────────────────────
# We initialise lazily at first use to avoid import-time failures if the
# posthog package is somehow absent in a test environment.
_posthog_client: Any = None


def _get_posthog_client() -> Any:
    """Return the module-level PostHog client, initialising it on first call."""
    global _posthog_client
    if _posthog_client is None:
        try:
            import posthog  # type: ignore[import]

            posthog.api_key = settings.POSTHOG_API_KEY
            posthog.host = settings.POSTHOG_HOST
            # Disable PostHog's own exception handler so we control error handling
            posthog.on_error = lambda err, items: logger.error(
                "PostHog delivery error: %s", err
            )
            _posthog_client = posthog
            logger.info(
                "PostHog client initialised (host=%s)", settings.POSTHOG_HOST
            )
        except ImportError:
            logger.warning(
                "posthog package not installed — analytics events will be no-ops."
            )
    return _posthog_client


def track(
    user_id: str,
    event: str,
    properties: Dict[str, Any] | None = None,
) -> None:
    """
    Fire a server-side analytics event.

    - Never raises — analytics must never crash a request.
    - In development: logs to console only (no PostHog call).
    - In production: sends to PostHog asynchronously.

    Args:
        user_id:    Supabase user UUID (the `sub` claim from the JWT).
        event:      PostHog event name, e.g. "user_registered".
        properties: Optional dict of event properties.
    """
    props: Dict[str, Any] = properties or {}

    try:
        if settings.ENVIRONMENT == "development":
            logger.info(
                "[analytics:dev] user_id=%s event=%s properties=%s",
                user_id,
                event,
                props,
            )
            return

        client = _get_posthog_client()
        if client is None:
            # posthog package not available — silently skip
            return

        client.capture(
            distinct_id=user_id,
            event=event,
            properties=props,
        )

    except Exception as exc:  # noqa: BLE001
        # Analytics failures must never propagate to the caller.
        logger.error(
            "analytics.track failed (event=%s, user_id=%s): %s",
            event,
            user_id,
            exc,
        )
