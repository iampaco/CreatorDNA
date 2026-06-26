import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.schemas.export import CreateExportResponse, ExportFormat
from workers.services.pdf_export import markdown_to_pdf_bytes


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


SAMPLE_MARKDOWN = """# 创作者报告

## 内容定位
专注于内容创作方法论。

## Hook 模式
- 反常识开头
"""


def test_markdown_to_pdf_bytes_generates_pdf() -> None:
    data = markdown_to_pdf_bytes(SAMPLE_MARKDOWN)
    assert data.startswith(b"%PDF")
    assert len(data) > 100


@patch("apps.api.routers.exports.ExportService")
def test_export_markdown_sync(mock_service_cls: MagicMock, client: TestClient) -> None:
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service
    creator_id = uuid.uuid4()
    mock_service.build_sync_bytes.return_value = (
        SAMPLE_MARKDOWN.encode("utf-8"),
        "text/markdown; charset=utf-8",
        f"creator-report-{creator_id}.md",
    )

    response = client.get(f"/api/reports/{creator_id}/export/markdown")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    assert response.text.startswith("# 创作者报告")


@patch("apps.api.routers.exports.ExportService")
def test_export_json_sync(mock_service_cls: MagicMock, client: TestClient) -> None:
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service
    creator_id = uuid.uuid4()
    payload = {
        "creatorId": str(creator_id),
        "sampleVideoCount": 3,
        "reportJson": {
            "positioning": "测试定位",
            "hookPatterns": [],
            "speechStyle": {},
            "shootingStyle": {},
            "subtitleEditingStyle": {},
            "reusableTemplates": [],
        },
    }
    mock_service.build_sync_bytes.return_value = (
        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        "application/json; charset=utf-8",
        f"creator-report-{creator_id}.json",
    )

    response = client.get(f"/api/reports/{creator_id}/export/json")
    assert response.status_code == 200
    body = response.json()
    assert body["reportJson"]["positioning"] == "测试定位"


@patch("workers.tasks.export_report.export_report_task")
@patch("apps.api.routers.exports.ExportService")
def test_create_export_enqueues_task(
    mock_service_cls: MagicMock,
    mock_task: MagicMock,
    client: TestClient,
) -> None:
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service
    creator_id = uuid.uuid4()
    task_id = str(uuid.uuid4())
    mock_service.create_export.return_value = CreateExportResponse(
        taskId=task_id,
        status="queued",
        format=ExportFormat.pdf,
    )

    response = client.post(
        f"/api/reports/{creator_id}/export",
        json={"format": "pdf"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["taskId"] == task_id
    assert body["format"] == "pdf"
    mock_task.delay.assert_called_once_with(task_id)


@patch("apps.api.routers.exports.ExportService")
def test_export_markdown_not_found(mock_service_cls: MagicMock, client: TestClient) -> None:
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service
    creator_id = uuid.uuid4()
    mock_service.build_sync_bytes.side_effect = ValueError("report_not_found")

    response = client.get(f"/api/reports/{creator_id}/export/markdown")
    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "report_not_found"
