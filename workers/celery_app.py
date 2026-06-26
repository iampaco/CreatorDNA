import os
from datetime import timedelta

import sentry_sdk
from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure
from sentry_sdk.integrations.celery import CeleryIntegration

from apps.api.logging_config import configure_logging

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
environment = os.getenv("ENVIRONMENT", "local")
sentry_dsn = os.getenv("SENTRY_DSN")

configure_logging(debug=environment not in ("production", "staging"))

if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=[CeleryIntegration()],
        send_default_pii=False,
    )

celery_app = Celery(
    "creator_dna",
    broker=redis_url,
    backend=redis_url,
    include=[
        "workers.tasks.stub",
        "workers.tasks.analyze_video",
        "workers.tasks.analyze_creator",
        "workers.tasks.export_report",
        "workers.tasks.media_cleanup",
    ],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=30,
    task_autoretry_for=(ConnectionError, TimeoutError, OSError),
    task_max_retries=3,
    task_routes={
        "workers.tasks.analyze_video.analyze_video_task": {"queue": "analysis"},
        "workers.tasks.analyze_creator.generate_creator_report_task": {"queue": "analysis"},
        "workers.tasks.export_report.export_report_task": {"queue": "exports"},
        "workers.tasks.media_cleanup.cleanup_expired_media": {"queue": "maintenance"},
    },
    beat_schedule={
        "cleanup-expired-media": {
            "task": "workers.tasks.media_cleanup.cleanup_expired_media",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
    broker_transport_options={
        "visibility_timeout": int(timedelta(hours=2).total_seconds()),
    },
)


@task_failure.connect
def handle_task_failure(
    sender=None,
    task_id=None,
    exception=None,
    args=None,
    kwargs=None,
    traceback=None,
    einfo=None,
    **other,
) -> None:
    retries = getattr(sender.request, "retries", 0) if sender else 0
    max_retries = getattr(sender, "max_retries", 3) if sender else 3
    if retries >= max_retries:
        celery_app.send_task(
            "workers.tasks.stub.record_dead_letter",
            kwargs={
                "task_name": sender.name if sender else "unknown",
                "task_id": task_id,
                "args": list(args or []),
                "kwargs": dict(kwargs or {}),
                "error": str(exception),
            },
            queue="dead_letter",
        )
