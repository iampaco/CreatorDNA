import logging
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.config import get_settings
from apps.api.db.models.creator_report import CreatorReport
from apps.api.db.models.export_task import ExportTask
from apps.api.schemas.export import ExportFormat
from apps.api.services.export import CONTENT_TYPES, ExportService
from apps.api.services.storage import StorageService
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@celery_app.task(name="workers.tasks.export_report.export_report_task", bind=True)
def export_report_task(self, export_task_id: str) -> dict:
    db = SessionLocal()
    try:
        task_uuid = uuid.UUID(export_task_id)
        export_task = db.get(ExportTask, task_uuid)
        if not export_task:
            raise LookupError(f"export task not found: {export_task_id}")

        service = ExportService(db)
        service.mark_processing(task_uuid, progress=10)

        report = db.get(CreatorReport, export_task.report_id)
        if not report:
            service.fail_export(task_uuid, "report_not_found", "Creator report not found.")
            return {"status": "failed", "error": "report_not_found"}

        export_format = ExportFormat(export_task.format)
        try:
            service.mark_processing(task_uuid, progress=40)
            data = service.build_export_bytes(report, export_format)
            service.mark_processing(task_uuid, progress=70)

            storage = StorageService()
            object_key = storage.build_export_key(task_uuid, export_format.value)
            storage.upload_bytes(
                key=object_key,
                data=data,
                content_type=CONTENT_TYPES[export_format],
            )
            service.complete_export(task_uuid, object_key)
            return {"status": "completed", "exportTaskId": export_task_id}
        except Exception as exc:
            logger.exception("export failed export_task_id=%s", export_task_id)
            service.fail_export(task_uuid, "export_failed", str(exc))
            return {"status": "failed", "error": "export_failed"}
    finally:
        db.close()
