from enum import Enum

from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    markdown = "markdown"
    json = "json"
    pdf = "pdf"


class CreateExportRequest(BaseModel):
    format: ExportFormat


class CreateExportResponse(BaseModel):
    taskId: str
    status: str = "queued"
    format: ExportFormat
