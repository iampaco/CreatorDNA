import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.config import get_settings
from apps.api.db.models.video import Video
from apps.api.services.storage import StorageService
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@celery_app.task(name="workers.tasks.media_cleanup.cleanup_expired_media")
def cleanup_expired_media() -> dict:
    cutoff = datetime.now(UTC) - timedelta(hours=settings.media_ttl_hours)
    storage = StorageService()
    db = SessionLocal()
    deleted = 0
    errors = 0

    try:
        videos = (
            db.query(Video)
            .filter(Video.media_object_key.isnot(None), Video.created_at < cutoff)
            .all()
        )
        for video in videos:
            key = video.media_object_key
            if not key:
                continue
            try:
                storage.delete_object(key)
                video.media_object_key = None
                deleted += 1
                logger.info(
                    "deleted expired media",
                    extra={"video_id": str(video.id), "step": "MEDIA_TTL_CLEANUP"},
                )
            except Exception as exc:
                errors += 1
                logger.error(
                    "media cleanup failed",
                    extra={"video_id": str(video.id), "error": str(exc), "step": "MEDIA_TTL_CLEANUP"},
                )
        db.commit()
    finally:
        db.close()

    export_cutoff = datetime.now(UTC) - timedelta(hours=settings.export_ttl_hours)
    export_deleted = 0
    try:
        for obj in storage.list_objects(prefix="exports/"):
            if obj["last_modified"].replace(tzinfo=UTC) < export_cutoff:
                try:
                    storage.delete_object(obj["key"])
                    export_deleted += 1
                except Exception as exc:
                    errors += 1
                    logger.error("export cleanup failed", extra={"error": str(exc), "step": "EXPORT_TTL_CLEANUP"})
    except Exception as exc:
        logger.error("export listing failed", extra={"error": str(exc)})

    return {"deleted_media": deleted, "deleted_exports": export_deleted, "errors": errors}
