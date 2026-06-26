import re
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from apps.api.db.models.analysis_task import AnalysisTask
from apps.api.db.models.creator_analysis_task import CreatorAnalysisTask
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
        video_id: uuid.UUID | None = None,
        creator_id: uuid.UUID | None = None,
        batch_task_id: uuid.UUID | None = None,
    ) -> tuple[Video, AnalysisTask]:
        if "douyin" not in video_url:
            raise ValueError("unsupported_platform")

        file_bytes = file.file.read()
        if not file_bytes:
            raise ValueError("empty_file")

        if video_id:
            video = self.db.get(Video, video_id)
            if not video:
                raise ValueError("video_not_found")
            if video.media_object_key:
                raise ValueError("video_already_uploaded")
            object_key = self.storage.build_media_key(video.id)
            if title:
                video.title = title
            video.media_object_key = object_key
        else:
            video_id = uuid.uuid4()
            object_key = self.storage.build_media_key(video_id)
            video = Video(
                id=video_id,
                creator_id=creator_id,
                platform="douyin",
                platform_video_id=parse_platform_video_id(video_url, platform_video_id),
                video_url=video_url,
                title=title,
                media_object_key=object_key,
            )
            self.db.add(video)

        self.storage.upload_bytes(
            key=object_key,
            data=file_bytes,
            content_type=file.content_type or "video/webm",
        )

        if batch_task_id:
            batch_task = self.db.get(CreatorAnalysisTask, batch_task_id)
            if not batch_task:
                raise ValueError("batch_task_not_found")
            if batch_task.status == "queued":
                batch_task.status = "processing"
                batch_task.current_step = "正在分析视频"
                batch_task.progress = max(batch_task.progress, 5)

        task = AnalysisTask(
            video_id=video.id,
            creator_analysis_task_id=batch_task_id,
            status="queued",
            progress=5,
            current_step="已上传，等待处理",
            media_object_key=object_key,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(video)
        self.db.refresh(task)
        return video, task
