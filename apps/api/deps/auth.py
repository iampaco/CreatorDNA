from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from apps.api.config import get_settings
from apps.api.schemas.error import ApiErrorResponse

_bearer = HTTPBearer(auto_error=False)


def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> str | None:
    settings = get_settings()
    if not settings.is_auth_required:
        return None

    if not settings.api_secret_key:
        raise HTTPException(
            status_code=500,
            detail=ApiErrorResponse(
                error="auth_misconfigured",
                message="API authentication is required but API_SECRET_KEY is not configured.",
            ).model_dump(),
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail=ApiErrorResponse(
                error="unauthorized",
                message="Missing or invalid Authorization header. Use Bearer token.",
            ).model_dump(),
        )

    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(
            status_code=401,
            detail=ApiErrorResponse(
                error="unauthorized",
                message="Invalid API key.",
            ).model_dump(),
        )

    return credentials.credentials
