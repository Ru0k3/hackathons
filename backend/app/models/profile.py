"""
Modeon — Profile & Auth Pydantic Models
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class OnboardingData(BaseModel):
    """Payload for completing the onboarding quiz in a single submission."""

    style_archetypes: Optional[List[str]] = Field(
        default=None,
        description="E.g. ['minimalist', 'streetwear']",
    )
    occasion_prefs: Optional[List[str]] = Field(
        default=None,
        description="E.g. ['work', 'weekend', 'formal']",
    )
    colour_palette: Optional[List[str]] = Field(
        default=None,
        description="E.g. ['navy', 'white', 'earth tones']",
    )
    gender_pref: Optional[str] = Field(
        default=None,
        description="'menswear' | 'womenswear' | 'unisex'",
    )


class ProfileUpdateRequest(BaseModel):
    """
    Partial profile update — only fields explicitly set by the caller are written.
    Callers should use model_fields_set to determine which fields were provided.
    """

    style_archetypes: Optional[List[str]] = None
    occasion_prefs: Optional[List[str]] = None
    colour_palette: Optional[List[str]] = None
    gender_pref: Optional[str] = None


class ProfileResponse(BaseModel):
    """Public representation of a user profile row."""

    id: str
    style_archetypes: Optional[List[str]]
    occasion_prefs: Optional[List[str]]
    colour_palette: Optional[List[str]]
    gender_pref: Optional[str]
    onboarding_complete: bool = Field(
        description="True when at least style_archetypes has been set."
    )
    created_at: str
    updated_at: str

    @classmethod
    def from_db_row(cls, row: dict) -> "ProfileResponse":
        """Construct a ProfileResponse from a raw Supabase dict."""
        return cls(
            id=str(row["id"]),
            style_archetypes=row.get("style_archetypes") or None,
            occasion_prefs=row.get("occasion_prefs") or None,
            colour_palette=row.get("colour_palette") or None,
            gender_pref=row.get("gender_pref"),
            onboarding_complete=bool(row.get("style_archetypes")),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )


class SessionVerifyResponse(BaseModel):
    """Response body for POST /api/auth/verify-session."""

    valid: bool
    user_id: str
    email: str


class OnboardingSkipRequest(BaseModel):
    """Body for POST /api/profile/onboarding/skip."""

    step_skipped_at: int = Field(ge=1, description="The step number at which the user chose to skip.")


class OnboardingCompleteRequest(OnboardingData):
    """
    Extends OnboardingData with an optional duration for analytics.
    All onboarding fields are saved in one upsert.
    """

    duration_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total time the user spent on the onboarding flow, in seconds.",
    )
