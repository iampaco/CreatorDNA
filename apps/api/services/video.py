import re
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from apps.api.db.models.analysis_task import AnalysisTask
from apps.api.db.models.video import Video
from apps.api.services.storage import StorageService

VIDEO_URL_PATTERN = re.compile(r"douyin\.com/video/(\d+)")


def parse_platform_video_id(video_url: str, platform_video_id: str | None) -> str | None:
    if platform_video_id:
        return platform_video_id
    match = VIDEO_URL_PATTERN.search(video_url)
    return match.group(1) if match else None


class VideoService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = StorageService()

    def create_upload(
        self,
        *,
        file: UploadFile,
        video_url: str,
        title: str | None,
        platform_video_id: str | None,
    ) -> tuple[Video, AnalysisTask]:
        if "douyin" not in video_url:
            raise ValueError("unsupported_platform")

        video_id = uuid.uuid4()
        object_key = self.storage.build_media_key(video_id)
        file_bytes = file.file.read()
        if not file_bytes:
            raise ValueError("empty_file")

        self.storage.upload_bytes(
            key=object_key,
            data=file_bytes,
            content_type=file.content_type or "video/webm",
        )

        video = Video(
            id=video_id,
            platform="douyin",
            platform_video_id=parse_platform_video_id(video_url, platform_video_id),
            video_url=video_url,
            title=title,
            media_object_key=object_key,
        )
        task = AnalysisTask(
            video_id=video_id,
            status="queued",
            progress=5,
            current_step="已上传，等待处理",
            media_object_key=object_key,
        )
        self.db.add(video)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(video)
        self.db.refresh(task)
        return video, task
