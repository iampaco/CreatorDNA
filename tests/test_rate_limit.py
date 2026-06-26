from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.config import get_settings


@pytest.fixture
def rate_limited_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    get_settings.cache_clear()
    from apps.api.main import app

    return TestClient(app)


@patch("apps.api.middleware.rate_limit.redis.from_url")
@patch("apps.api.routers.videos.analyze_video_task")
@patch("apps.api.services.video.VideoService.create_upload")
def test_rate_limit_returns_429(
    mock_create_upload: MagicMock,
    mock_task: MagicMock,
    mock_redis_from_url: MagicMock,
    rate_limited_client: TestClient,
) -> None:
    video = MagicMock()
    video.id = "video-1"
    task = MagicMock()
    task.id = "task-1"
    mock_create_upload.return_value = (video, task)
    mock_redis = MagicMock()
    mock_redis_from_url.return_value = mock_redis
    counts = iter([1, 2, 3])
    mock_pipe = MagicMock()
    mock_redis.pipeline.return_value = mock_pipe
    mock_pipe.execute.side_effect = lambda: [None, None, next(counts), None]

    payload = {
        "data": {"videoUrl": "https://www.douyin.com/video/123"},
        "files": {"file": ("capture.webm", b"fake", "video/webm")},
    }
    for _ in range(2):
        response = rate_limited_client.post("/api/videos/upload", **payload)
        assert response.status_code == 200

    response = rate_limited_client.post("/api/videos/upload", **payload)
    assert response.status_code == 429
    assert response.json()["detail"]["error"] == "rate_limited"
