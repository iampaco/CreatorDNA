import logging

import redis
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from apps.api.config import get_settings
from apps.api.db.session import engine
from apps.api.schemas.error import ApiErrorResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _check_postgres() -> tuple[bool, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "ok"
    except SQLAlchemyError as exc:
        logger.error("postgres health check failed: %s", exc)
        return False, str(exc)


def _check_redis() -> tuple[bool, str]:
    try:
        client = redis.from_url(settings.redis_url)
        client.ping()
        return True, "ok"
    except redis.RedisError as exc:
        logger.error("redis health check failed: %s", exc)
        return False, str(exc)


def _check_workers() -> tuple[bool, str]:
    try:
        from workers.celery_app import celery_app

        inspect = celery_app.control.inspect(timeout=2.0)
        ping = inspect.ping()
        if not ping:
            return False, "no workers responding"
        return True, f"{len(ping)} worker(s)"
    except Exception as exc:
        logger.warning("worker health check failed: %s", exc)
        return False, str(exc)


@router.get("/ready")
def readiness() -> dict:
    postgres_ok, postgres_detail = _check_postgres()
    redis_ok, redis_detail = _check_redis()
    workers_ok, workers_detail = _check_workers()

    checks = {
        "postgres": {"ok": postgres_ok, "detail": postgres_detail},
        "redis": {"ok": redis_ok, "detail": redis_detail},
        "workers": {"ok": workers_ok, "detail": workers_detail},
    }
    all_ok = postgres_ok and redis_ok and workers_ok
    status_code = 200 if all_ok else 503
    body = {"status": "ready" if all_ok else "not_ready", "checks": checks}

    if not all_ok:
        raise HTTPException(status_code=status_code, detail=body)
    return body


@router.post("/debug/sentry-test")
def sentry_test() -> dict[str, str]:
    if settings.environment == "production":
        raise HTTPException(
            status_code=404,
            detail=ApiErrorResponse(error="not_found", message="Not available in production.").model_dump(),
        )
    raise RuntimeError("Sentry test exception from CreatorDNA API")
