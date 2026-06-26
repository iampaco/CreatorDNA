import pytest
from fastapi.testclient import TestClient

from apps.api.config import get_settings
from apps.api.main import app


@pytest.fixture
def auth_required_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("API_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("AUTH_REQUIRED", "true")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    get_settings.cache_clear()
    return TestClient(app)


def test_upload_requires_auth(auth_required_client: TestClient) -> None:
    response = auth_required_client.post(
        "/api/videos/upload",
        data={"videoUrl": "https://www.douyin.com/video/123"},
        files={"file": ("capture.webm", b"fake", "video/webm")},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["error"] == "unauthorized"


def test_upload_with_valid_key(auth_required_client: TestClient) -> None:
    from unittest.mock import MagicMock, patch

    auth_required_client.headers.update({"Authorization": "Bearer test-secret-key"})
    video = MagicMock()
    video.id = "video-1"
    task = MagicMock()
    task.id = "task-1"
    with patch("apps.api.routers.videos.analyze_video_task") as mock_task, patch(
        "apps.api.services.video.VideoService.create_upload", return_value=(video, task)
    ):
        response = auth_required_client.post(
            "/api/videos/upload",
            data={"videoUrl": "https://www.douyin.com/video/123"},
            files={"file": ("capture.webm", b"fake-video", "video/webm")},
        )
    assert response.status_code == 200
    body = response.json()
    assert "videoId" in body
    assert "taskId" in body
    mock_task.delay.assert_called_once()


def test_invalid_api_key(auth_required_client: TestClient) -> None:
    auth_required_client.headers.update({"Authorization": "Bearer wrong-key"})
    response = auth_required_client.post(
        "/api/creator-analysis",
        json={
            "platform": "douyin",
            "creatorUrl": "https://www.douyin.com/user/test",
            "videos": [{"videoUrl": "https://www.douyin.com/video/1"}],
            "sampleSize": 10,
        },
    )
    assert response.status_code == 401
