from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

from workers.tasks.media_cleanup import cleanup_expired_media


@patch("workers.tasks.media_cleanup.SessionLocal")
@patch("workers.tasks.media_cleanup.StorageService")
def test_cleanup_deletes_old_media(mock_storage_cls: MagicMock, mock_session_local: MagicMock) -> None:
    storage = mock_storage_cls.return_value
    db = MagicMock()
    mock_session_local.return_value = db

    old_video = MagicMock()
    old_video.id = uuid4()
    old_video.media_object_key = "videos/old/capture.webm"
    old_video.created_at = datetime.now(UTC) - timedelta(hours=72)

    db.query.return_value.filter.return_value.all.return_value = [old_video]
    storage.list_objects.return_value = []

    result = cleanup_expired_media()

    storage.delete_object.assert_called_once_with("videos/old/capture.webm")
    assert old_video.media_object_key is None
    assert result["deleted_media"] == 1
