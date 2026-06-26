import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.schemas.creator import BatchVideoItem, CreateCreatorAnalysisResponse


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@patch("apps.api.routers.creators.CreatorService")
def test_creator_analysis_rejects_non_douyin(mock_service_cls: MagicMock, client: TestClient) -> None:
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service
    mock_service.create_analysis.side_effect = ValueError("unsupported_platform")

    response = client.post(
        "/api/creator-analysis",
        json={
            "platform": "tiktok",
            "creatorUrl": "https://www.tiktok.com/@user",
            "videoUrls": ["https://www.tiktok.com/video/1"],
            "sampleSize": 10,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "unsupported_platform"


@patch("apps.api.routers.creators.CreatorService")
def test_creator_analysis_creates_task(mock_service_cls: MagicMock, client: TestClient) -> None:
    mock_service = MagicMock()
    mock_service_cls.return_value = mock_service
    mock_service.create_analysis.return_value = CreateCreatorAnalysisResponse(
        taskId="batch-1",
        creatorId="creator-1",
        status="queued",
        totalVideos=2,
        videos=[
            BatchVideoItem(videoId="v1", videoUrl="https://www.douyin.com/video/111", title="视频1"),
            BatchVideoItem(videoId="v2", videoUrl="https://www.douyin.com/video/222", title="视频2"),
        ],
    )

    response = client.post(
        "/api/creator-analysis",
        json={
            "platform": "douyin",
            "creatorUrl": "https://www.douyin.com/user/MS4wLjABAAAAtest",
            "videos": [
                {"videoUrl": "https://www.douyin.com/video/111", "title": "视频1"},
                {"videoUrl": "https://www.douyin.com/video/222", "title": "视频2"},
            ],
            "sampleSize": 10,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["totalVideos"] == 2
    assert len(body["videos"]) == 2


@patch("apps.api.routers.videos.analyze_video_task")
@patch("apps.api.services.video.StorageService")
@patch("apps.api.services.video.VideoService.create_upload")
def test_batch_upload_with_video_id(
    mock_create_upload: MagicMock,
    mock_storage_cls: MagicMock,
    mock_task: MagicMock,
    client: TestClient,
) -> None:
    video_id = str(uuid.uuid4())
    batch_id = str(uuid.uuid4())
    creator_id = str(uuid.uuid4())
    video = MagicMock()
    video.id = video_id
    task = MagicMock()
    task.id = str(uuid.uuid4())
    mock_create_upload.return_value = (video, task)

    upload_resp = client.post(
        "/api/videos/upload",
        data={
            "videoUrl": "https://www.douyin.com/video/999",
            "videoId": video_id,
            "batchTaskId": batch_id,
            "creatorId": creator_id,
        },
        files={"file": ("capture.webm", b"fake-video", "video/webm")},
    )
    assert upload_resp.status_code == 200
    mock_task.delay.assert_called_once()
