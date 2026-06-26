from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@patch("apps.api.routers.videos.analyze_video_task")
@patch("apps.api.services.video.StorageService")
def test_upload_rejects_non_douyin(mock_storage_cls: MagicMock, mock_task: MagicMock, client: TestClient) -> None:
    response = client.post(
        "/api/videos/upload",
        data={"videoUrl": "https://example.com/video/1"},
        files={"file": ("capture.webm", b"fake", "video/webm")},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["detail"]["error"] == "unsupported_platform"
    mock_task.delay.assert_not_called()
