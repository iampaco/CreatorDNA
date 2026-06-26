import re
import uuid

from sqlalchemy.orm import Session

from apps.api.db.models.analysis_task import AnalysisTask
from apps.api.db.models.creator import Creator
from apps.api.db.models.creator_analysis_task import CreatorAnalysisTask
from apps.api.db.models.creator_report import CreatorReport
from apps.api.db.models.video import Video
from apps.api.schemas.creator import (
    BatchVideoItem,
    CreateCreatorAnalysisRequest,
    CreateCreatorAnalysisResponse,
    CreatorProfileInput,
    CreatorReportResponse,
    CreatorVideoInput,
)

DOUYIN_USER_PATTERN = re.compile(r"douyin\.com/user/([^/?#]+)")
DOUYIN_VIDEO_PATTERN = re.compile(r"douyin\.com/video/(\d+)")


def _validate_douyin_url(url: str, *, kind: str) -> None:
    if "douyin" not in url:
        raise ValueError("unsupported_platform")
    if kind == "user" and not DOUYIN_USER_PATTERN.search(url):
        raise ValueError("invalid_creator_url")
    if kind == "video" and not DOUYIN_VIDEO_PATTERN.search(url):
        raise ValueError("invalid_video_url")


def _parse_creator_id_from_url(url: str) -> str | None:
    match = DOUYIN_USER_PATTERN.search(url)
    return match.group(1) if match else None


def _upsert_creator(db: Session, profile: CreatorProfileInput, creator_url: str) -> Creator:
    platform_creator_id = _parse_creator_id_from_url(creator_url)
    existing = None
    if platform_creator_id:
        existing = (
            db.query(Creator)
            .filter(
                Creator.platform == profile.platform,
                Creator.platform_creator_id == platform_creator_id,
            )
            .first()
        )
    if not existing and profile.profileUrl:
        existing = (
            db.query(Creator)
            .filter(Creator.platform == profile.platform, Creator.profile_url == profile.profileUrl)
            .first()
        )

    if existing:
        existing.display_name = profile.displayName or existing.display_name
        existing.username = profile.username or existing.username
        existing.profile_url = profile.profileUrl or existing.profile_url
        existing.avatar_url = profile.avatarUrl or existing.avatar_url
        existing.platform_creator_id = platform_creator_id or existing.platform_creator_id
        db.commit()
        db.refresh(existing)
        return existing

    creator = Creator(
        platform=profile.platform,
        platform_creator_id=platform_creator_id,
        username=profile.username,
        display_name=profile.displayName,
        profile_url=profile.profileUrl,
        avatar_url=profile.avatarUrl,
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator


def _normalize_videos(request: CreateCreatorAnalysisRequest) -> list[CreatorVideoInput]:
    videos: list[CreatorVideoInput] = list(request.videos)
    for url in request.videoUrls:
        if not any(v.videoUrl == url for v in videos):
            videos.append(CreatorVideoInput(videoUrl=url))
    return videos[: request.sampleSize]


class CreatorService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_analysis(self, request: CreateCreatorAnalysisRequest) -> CreateCreatorAnalysisResponse:
        if request.platform != "douyin":
            raise ValueError("unsupported_platform")

        _validate_douyin_url(request.creatorUrl, kind="user")

        profile = request.creatorProfile or CreatorProfileInput(
            platform=request.platform,
            profileUrl=request.creatorUrl.split("?")[0],
        )
        profile.platform = request.platform
        if not profile.profileUrl:
            profile.profileUrl = request.creatorUrl.split("?")[0]

        videos_input = _normalize_videos(request)
        if not videos_input:
            raise ValueError("no_videos")

        for video in videos_input:
            _validate_douyin_url(video.videoUrl, kind="video")

        creator = _upsert_creator(self.db, profile, request.creatorUrl)

        batch_task = CreatorAnalysisTask(
            creator_id=creator.id,
            status="queued",
            progress=0,
            current_step="等待视频上传",
            total_videos=len(videos_input),
            finished_videos=0,
        )
        self.db.add(batch_task)
        self.db.flush()

        batch_videos: list[BatchVideoItem] = []
        for item in videos_input:
            platform_video_id = item.platformVideoId
            if not platform_video_id:
                match = DOUYIN_VIDEO_PATTERN.search(item.videoUrl)
                platform_video_id = match.group(1) if match else None

            video = Video(
                creator_id=creator.id,
                platform=request.platform,
                platform_video_id=platform_video_id,
                video_url=item.videoUrl.split("?")[0],
                title=item.title,
                description=item.description,
                like_count=item.likeCount,
                comment_count=item.commentCount,
                collect_count=item.collectCount,
            )
            self.db.add(video)
            self.db.flush()
            batch_videos.append(
                BatchVideoItem(
                    videoId=str(video.id),
                    videoUrl=video.video_url,
                    platformVideoId=platform_video_id,
                    title=item.title,
                )
            )

        self.db.commit()
        self.db.refresh(batch_task)

        return CreateCreatorAnalysisResponse(
            taskId=str(batch_task.id),
            creatorId=str(creator.id),
            status=batch_task.status,
            totalVideos=batch_task.total_videos,
            videos=batch_videos,
        )

    def get_batch_task(self, task_id: uuid.UUID) -> CreatorAnalysisTask | None:
        return self.db.get(CreatorAnalysisTask, task_id)

    def get_latest_report(self, creator_id: uuid.UUID) -> CreatorReportResponse | None:
        report = (
            self.db.query(CreatorReport)
            .filter(CreatorReport.creator_id == creator_id)
            .order_by(CreatorReport.created_at.desc())
            .first()
        )
        if not report or not report.report_markdown:
            return None
        return CreatorReportResponse(
            creatorId=str(creator_id),
            sampleVideoCount=report.sample_video_count or 0,
            reportMarkdown=report.report_markdown,
            reportJson=report.report_json or {},
        )

    def get_videos_for_batch(self, batch_task_id: uuid.UUID) -> list[Video]:
        creator_task = self.db.get(CreatorAnalysisTask, batch_task_id)
        if not creator_task:
            return []
        return (
            self.db.query(Video)
            .filter(Video.creator_id == creator_task.creator_id)
            .order_by(Video.created_at.asc())
            .limit(creator_task.total_videos)
            .all()
        )

    def count_finished_videos(self, batch_task_id: uuid.UUID) -> tuple[int, int]:
        """Return (finished, completed) where finished includes completed + failed."""
        creator_task = self.db.get(CreatorAnalysisTask, batch_task_id)
        if not creator_task:
            return 0, 0
        videos = self.get_videos_for_batch(batch_task_id)
        video_ids = [v.id for v in videos]
        if not video_ids:
            return 0, 0
        tasks = (
            self.db.query(AnalysisTask)
            .filter(
                AnalysisTask.video_id.in_(video_ids),
                AnalysisTask.creator_analysis_task_id == batch_task_id,
            )
            .all()
        )
        completed = sum(1 for t in tasks if t.status == "completed")
        finished = sum(1 for t in tasks if t.status in ("completed", "failed"))
        return finished, completed
