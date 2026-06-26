import logging
import os
from datetime import UTC, datetime

import redis

logger = logging.getLogger(__name__)


class QuotaExceededError(RuntimeError):
    pass


def _redis_client() -> redis.Redis:
    return redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


def _daily_key(step: str) -> str:
    day = datetime.now(UTC).strftime("%Y-%m-%d")
    return f"ai_quota:{day}:{step}"


def check_and_increment(step: str, units: int = 1) -> int:
    limit = int(os.getenv("AI_DAILY_QUOTA", "500"))
    if limit <= 0:
        return units

    client = _redis_client()
    key = _daily_key(step)
    count = client.incrby(key, units)
    if count == units:
        client.expire(key, 86_400)
    if count > limit:
        client.decrby(key, units)
        raise QuotaExceededError(f"Daily AI quota exceeded for step {step}")
    return count


def log_ai_usage(
    *,
    step: str,
    model: str,
    tokens_used: int | None = None,
    cost_usd: float | None = None,
    task_id: str | None = None,
    video_id: str | None = None,
    duration_ms: int | None = None,
) -> None:
    if os.getenv("AI_COST_LOG_ENABLED", "true").lower() not in ("1", "true", "yes"):
        return
    logger.info(
        "ai usage",
        extra={
            "step": step,
            "model": model,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "task_id": task_id,
            "video_id": video_id,
            "duration_ms": duration_ms,
        },
    )
