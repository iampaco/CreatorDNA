import json
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from apps.api.db.models.creator_report import CreatorReport
from apps.api.db.models.export_task import ExportTask
from apps.api.schemas.export import CreateExportResponse, ExportFormat
from apps.api.services.storage import StorageService
from workers.services.pdf_export import markdown_to_pdf_bytes
from workers.services.report_generation import parse_report_json

CONTENT_TYPES = {
    ExportFormat.markdown: "text/markdown; charset=utf-8",
    ExportFormat.json: "application/json; charset=utf-8",
    ExportFormat.pdf: "application/pdf",
}

EXTENSIONS = {
    ExportFormat.markdown: "md",
    ExportFormat.json: "json",
    ExportFormat.pdf: "pdf",
}


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest_report_row(self, creator_id: uuid.UUID) -> CreatorReport | None:
        return (
            self.db.query(CreatorReport)
            .filter(CreatorReport.creator_id == creator_id)
            .order_by(CreatorReport.created_at.desc())
            .first()
        )

    def get_export_task(self, task_id: uuid.UUID) -> ExportTask | None:
        return self.db.get(ExportTask, task_id)

    def create_export(self, creator_id: uuid.UUID, export_format: ExportFormat) -> CreateExportResponse:
        report = self.get_latest_report_row(creator_id)
        if not report:
            raise ValueError("report_not_found")
        if export_format == ExportFormat.json and not report.report_json:
            raise ValueError("report_json_missing")
        if export_format in (ExportFormat.markdown, ExportFormat.pdf) and not report.report_markdown:
            raise ValueError("report_markdown_missing")

        if export_format == ExportFormat.json:
            parse_report_json(json.dumps(report.report_json, ensure_ascii=False))

        export_task = ExportTask(
            creator_id=creator_id,
            report_id=report.id,
            format=export_format.value,
            status="queued",
            progress=0,
        )
        self.db.add(export_task)
        self.db.commit()
        self.db.refresh(export_task)
        return CreateExportResponse(
            taskId=str(export_task.id),
            status=export_task.status,
            format=export_format,
        )

    def build_sync_bytes(self, creator_id: uuid.UUID, export_format: ExportFormat) -> tuple[bytes, str, str]:
        report = self.get_latest_report_row(creator_id)
        if not report:
            raise ValueError("report_not_found")

        if export_format == ExportFormat.markdown:
            if not report.report_markdown:
                raise ValueError("report_markdown_missing")
            filename = f"creator-report-{creator_id}.md"
            return report.report_markdown.encode("utf-8"), CONTENT_TYPES[export_format], filename

        if export_format == ExportFormat.json:
            if not report.report_json:
                raise ValueError("report_json_missing")
            validated = parse_report_json(json.dumps(report.report_json, ensure_ascii=False))
            payload = json.dumps(
                {
                    "creatorId": str(creator_id),
                    "sampleVideoCount": report.sample_video_count or 0,
                    "reportJson": validated,
                },
                ensure_ascii=False,
                indent=2,
            )
            filename = f"creator-report-{creator_id}.json"
            return payload.encode("utf-8"), CONTENT_TYPES[export_format], filename

        raise ValueError("unsupported_sync_format")

    def build_export_bytes(self, report: CreatorReport, export_format: ExportFormat) -> bytes:
        if export_format == ExportFormat.markdown:
            if not report.report_markdown:
                raise ValueError("report_markdown_missing")
            return report.report_markdown.encode("utf-8")

        if export_format == ExportFormat.json:
            if not report.report_json:
                raise ValueError("report_json_missing")
            validated = parse_report_json(json.dumps(report.report_json, ensure_ascii=False))
            payload = json.dumps(
                {
                    "creatorId": str(report.creator_id),
                    "sampleVideoCount": report.sample_video_count or 0,
                    "reportJson": validated,
                },
                ensure_ascii=False,
                indent=2,
            )
            return payload.encode("utf-8")

        if export_format == ExportFormat.pdf:
            if not report.report_markdown:
                raise ValueError("report_markdown_missing")
            return markdown_to_pdf_bytes(report.report_markdown)

        raise ValueError("unsupported_format")

    def get_download_bytes(self, task_id: uuid.UUID) -> tuple[bytes, str, str]:
        export_task = self.get_export_task(task_id)
        if not export_task:
            raise LookupError("task_not_found")
        if export_task.status != "completed":
            raise ValueError("export_not_ready")
        if not export_task.object_key:
            raise ValueError("export_file_missing")

        export_format = ExportFormat(export_task.format)
        storage = StorageService()
        data = storage.download_bytes(export_task.object_key)
        filename = f"creator-report-{export_task.creator_id}.{EXTENSIONS[export_format]}"
        return data, CONTENT_TYPES[export_format], filename

    def mark_processing(self, task_id: uuid.UUID, progress: int) -> None:
        export_task = self.get_export_task(task_id)
        if not export_task:
            return
        export_task.status = "processing"
        export_task.progress = progress
        export_task.updated_at = datetime.now(UTC)
        self.db.commit()

    def complete_export(self, task_id: uuid.UUID, object_key: str) -> None:
        export_task = self.get_export_task(task_id)
        if not export_task:
            return
        export_task.status = "completed"
        export_task.progress = 100
        export_task.object_key = object_key
        export_task.updated_at = datetime.now(UTC)
        self.db.commit()

    def fail_export(self, task_id: uuid.UUID, error_code: str, message: str) -> None:
        export_task = self.get_export_task(task_id)
        if not export_task:
            return
        export_task.status = "failed"
        export_task.progress = 100
        export_task.error_code = error_code
        export_task.error_message = message
        export_task.updated_at = datetime.now(UTC)
        self.db.commit()
