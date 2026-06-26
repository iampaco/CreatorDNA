import logging
import time
from collections.abc import Callable

import redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from apps.api.config import get_settings
from apps.api.schemas.error import ApiErrorResponse

logger = logging.getLogger("apps.api.rate_limit")

RATE_LIMITED_PATHS = {
    ("POST", "/api/videos/upload"),
    ("POST", "/api/creator-analysis"),
    ("POST", "/api/reports"),
}


def _client_key(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return f"key:{auth[7:][:16]}"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    if request.client:
        return f"ip:{request.client.host}"
    return "ip:unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        path_key = (request.method.upper(), request.url.path)

        is_limited = path_key in RATE_LIMITED_PATHS or (
            request.method.upper() == "POST" and request.url.path.endswith("/export")
        )

        if not settings.rate_limit_enabled or not is_limited:
            return await call_next(request)

        client = _client_key(request)
        redis_key = f"ratelimit:{client}:{request.url.path}"
        now = int(time.time())
        window = settings.rate_limit_window_seconds
        window_start = now - window

        try:
            r = redis.from_url(settings.redis_url, decode_responses=True)
            pipe = r.pipeline()
            pipe.zremrangebyscore(redis_key, 0, window_start)
            pipe.zadd(redis_key, {str(now): now})
            pipe.zcard(redis_key)
            pipe.expire(redis_key, window + 1)
            _, _, count, _ = pipe.execute()
        except redis.RedisError as exc:
            logger.warning("rate limit redis unavailable: %s", exc)
            return await call_next(request)

        if count > settings.rate_limit_requests:
            retry_after = window
            body = ApiErrorResponse(
                error="rate_limited",
                message=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            ).model_dump()
            return JSONResponse(
                status_code=429,
                content={"detail": body},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
