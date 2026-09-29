"""
supabase_service.py
Singleton Supabase client using the service-role key (backend only).
Never expose this key to the frontend.
"""
from functools import lru_cache

from supabase import Client, create_client

from app.config import settings


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )
