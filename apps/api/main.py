import logging

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from apps.api.config import get_settings
from apps.api.logging_config import configure_logging
from apps.api.middleware.rate_limit import RateLimitMiddleware
from apps.api.middleware.request_context import RequestContextMiddleware
from apps.api.routers import creators, exports, health, tasks, videos
from apps.api.schemas.error import ApiErrorResponse

settings = get_settings()
configure_logging(debug=not settings.is_production)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        integrations=[FastApiIntegration(), CeleryIntegration()],
        send_default_pii=False,
        before_send=lambda event, hint: _scrub_sentry_event(event),
    )

logger = logging.getLogger(__name__)

app = FastAPI(title="CreatorDNA API", version="0.1.0")

app.add_middleware(RequestContextMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(videos.router)
app.include_router(tasks.router)
app.include_router(creators.router)
app.include_router(exports.router)


def _scrub_sentry_event(event: dict) -> dict:
    request = event.get("request") or {}
    headers = request.get("headers") or {}
    if "Authorization" in headers:
        headers["Authorization"] = "[Filtered]"
    return event


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.exception(
        "unhandled exception",
        extra={"request_id": request_id, "path": request.url.path},
    )
    message = "Internal server error."
    if not settings.is_production:
        message = str(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": ApiErrorResponse(error="internal_error", message=message).model_dump()},
    )
