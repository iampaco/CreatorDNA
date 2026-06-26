from enum import StrEnum

from pydantic import BaseModel


class ExportFormat(StrEnum):
    markdown = "markdown"
    json = "json"
    pdf = "pdf"


class CreateExportRequest(BaseModel):
    format: ExportFormat


class CreateExportResponse(BaseModel):
    taskId: str
    status: str = "queued"
    format: ExportFormat
