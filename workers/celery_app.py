import os

from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "creator_dna",
    broker=redis_url,
    backend=redis_url,
    include=[
        "workers.tasks.stub",
        "workers.tasks.analyze_video",
        "workers.tasks.analyze_creator",
        "workers.tasks.export_report",
    ],
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
