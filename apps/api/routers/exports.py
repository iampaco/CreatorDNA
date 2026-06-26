import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from apps.api.db.session import get_db
from apps.api.deps.auth import verify_api_key
from apps.api.schemas.error import ApiErrorResponse
from apps.api.schemas.export import CreateExportRequest, CreateExportResponse, ExportFormat
from apps.api.services.export import ExportService

router = APIRouter(prefix="/api", tags=["exports"])


def _export_error_response(exc: ValueError) -> HTTPException:
    code = str(exc)
    messages = {
        "report_not_found": "Creator report not found.",
        "report_markdown_missing": "Report markdown is not available.",
        "report_json_missing": "Report JSON is not available.",
        "unsupported_sync_format": "Use POST /export for PDF generation.",
        "export_not_ready": "Export is not ready yet.",
        "export_file_missing": "Export file is missing.",
    }
    status_codes = {
        "report_not_found": 404,
        "export_not_ready": 409,
        "export_file_missing": 404,
    }
    return HTTPException(
        status_code=status_codes.get(code, 400),
        detail=ApiErrorResponse(error=code, message=messages.get(code, str(exc))).model_dump(),
    )


@router.get("/reports/{creator_id}/export/markdown")
def export_markdown(creator_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    service = ExportService(db)
    try:
        data, content_type, filename = service.build_sync_bytes(creator_id, ExportFormat.markdown)
    except ValueError as exc:
        raise _export_error_response(exc) from exc
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/reports/{creator_id}/export/json")
def export_json(creator_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    service = ExportService(db)
    try:
        data, content_type, filename = service.build_sync_bytes(creator_id, ExportFormat.json)
    except ValueError as exc:
        raise _export_error_response(exc) from exc
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/reports/{creator_id}/export", response_model=CreateExportResponse)
def create_export(
    creator_id: uuid.UUID,
    request: CreateExportRequest,
    db: Session = Depends(get_db),
    _api_key: str | None = Depends(verify_api_key),
) -> CreateExportResponse:
    from workers.tasks.export_report import export_report_task

    service = ExportService(db)
    try:
        response = service.create_export(creator_id, request.format)
    except ValueError as exc:
        raise _export_error_response(exc) from exc

    export_report_task.delay(response.taskId)
    return response


@router.get("/exports/{task_id}/download")
def download_export(task_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    service = ExportService(db)
    try:
        data, content_type, filename = service.get_download_bytes(task_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=ApiErrorResponse(error="task_not_found", message="Export task not found.").model_dump(),
        ) from exc
    except ValueError as exc:
        raise _export_error_response(exc) from exc
    return Response(
        content=data,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
