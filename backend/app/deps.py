"""
Modeon — FastAPI Shared Dependencies

get_current_user: validates the Supabase JWT from either:
  - Authorization: Bearer <token> header
  - httpOnly cookie named 'sb-access-token'

Raises HTTP 401 on any auth failure.
"""

from typing import Any, Dict, Optional

import jwt
from fastapi import Cookie, HTTPException, Request, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.config import settings

_ALGORITHM = "HS256"
_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def _extract_token(request: Request, sb_access_token: Optional[str]) -> str:
    """
    Return the raw JWT string from whichever source is available.
    Priority: Authorization header → httpOnly cookie.
    """
    auth_header: Optional[str] = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1]:
            return parts[1]

    if sb_access_token:
        return sb_access_token

    raise _CREDENTIALS_EXCEPTION


async def get_current_user(
    request: Request,
    sb_access_token: Optional[str] = Cookie(default=None),
) -> Dict[str, Any]:
    """
    FastAPI dependency — inject into any protected route handler.

    Returns the decoded JWT payload dict with at least:
      - 'sub'   (user UUID, Supabase user ID)
      - 'email' (user email address)

    Raises HTTP 401 if the token is missing, expired, or fails validation.
    """
    token = _extract_token(request, sb_access_token)

    try:
        payload: Dict[str, Any] = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[_ALGORITHM],
            options={
                "verify_aud": False,   # Supabase JWTs use 'authenticated' audience
                "require": ["sub", "exp"],
            },
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[str] = payload.get("sub")
    email: Optional[str] = payload.get("email")

    if not user_id:
        raise _CREDENTIALS_EXCEPTION

    return {
        "user_id": user_id,
        "email": email,
        **payload,  # expose the full payload for downstream use if needed
    }
