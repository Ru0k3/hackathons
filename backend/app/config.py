from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    ENVIRONMENT: str = "development"
    SWIPE_LIGHTWEIGHT_MODE: bool = False
    CONTENT_SAFETY_THRESHOLD: float = 0.5

    # ── Supabase ──────────────────────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    # ── Azure Blob ────────────────────────────────────────────────────────────
    AZURE_BLOB_CONN_STRING: str
    AZURE_BLOB_ACCOUNT_NAME: str

    # ── Azure OpenAI ──────────────────────────────────────────────────────────
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_KEY: str
    AZURE_OPENAI_DEPLOYMENT_MINI: str = "gpt-4o-mini"
    AZURE_OPENAI_DEPLOYMENT_LARGE: str = "gpt-4o"

    # ── Azure Content Safety ──────────────────────────────────────────────────
    AZURE_CONTENT_SAFETY_ENDPOINT: str
    AZURE_CONTENT_SAFETY_KEY: str

    # ── PostHog ───────────────────────────────────────────────────────────────
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
