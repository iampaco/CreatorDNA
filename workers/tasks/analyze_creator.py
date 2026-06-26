import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.config import get_settings
from apps.api.db.models.analysis_task import AnalysisTask
from apps.api.db.models.creator import Creator
from apps.api.db.models.creator_analysis_task import CreatorAnalysisTask
from apps.api.db.models.creator_report import CreatorReport
from apps.api.db.models.video import Video
from apps.api.db.models.video_style_analysis import VideoStyleAnalysis
from apps.api.db.models.visual_analysis import VisualAnalysis
from apps.api.services.creator import CreatorService
from workers.celery_app import celery_app
from workers.services.aggregation import aggregate_video_analyses
from workers.services.report_generation import ReportGenerationError, generate_creator_report

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _style_to_dict(style: VideoStyleAnalysis, visual: VisualAnalysis | None = None) -> dict:
    merged: dict = {
        "hookType": style.hook_type,
        "hookText": style.hook_text,
        "topicCategory": style.topic_category,
        "targetAudience": style.target_audience if isinstance(style.target_audience, list) else [],
        "contentStructure": style.content_structure if isinstance(style.content_structure, list) else [],
        "emotionalTone": style.emotional_tone,
        "commonPhrases": style.common_phrases if isinstance(style.common_phrases, list) else [],
        "endingType": style.ending_type,
        "shootingStyle": style.shooting_style,
        "reusableTemplate": style.reusable_template,
    }
    if visual and isinstance(visual.summary, dict):
        merged.update(visual.summary)
    return merged


def update_batch_progress(db: Session, batch_task_id: uuid.UUID) -> None:
    batch_task = db.get(CreatorAnalysisTask, batch_task_id)
    if not batch_task or batch_task.status in ("completed", "failed"):
        return

    service = CreatorService(db)
    finished, _completed = service.count_finished_videos(batch_task_id)
    batch_task.finished_videos = finished
    batch_task.status = "processing"
    batch_task.current_step = f"已完成 {finished}/{batch_task.total_videos} 个视频分析"

    if batch_task.total_videos > 0:
        batch_task.progress = min(90, int((finished / batch_task.total_videos) * 90))

    if finished >= batch_task.total_videos and batch_task.total_videos > 0:
        batch_task.current_step = "正在生成创作者报告"
        batch_task.progress = 92
        batch_task.updated_at = datetime.now(UTC)
        db.commit()
        generate_creator_report_task.delay(str(batch_task_id))
        return

    batch_task.updated_at = datetime.now(UTC)
    db.commit()


@celery_app.task(name="workers.tasks.analyze_creator.generate_creator_report_task", bind=True)
def generate_creator_report_task(self, batch_task_id: str) -> dict:
    db = SessionLocal()
    try:
        batch_uuid = uuid.UUID(batch_task_id)
        batch_task = db.get(CreatorAnalysisTask, batch_uuid)
        if not batch_task:
            raise LookupError(f"batch task not found: {batch_task_id}")

        creator = db.get(Creator, batch_task.creator_id)
        videos = (
            db.query(Video)
            .filter(Video.creator_id == batch_task.creator_id)
            .order_by(Video.created_at.asc())
            .limit(batch_task.total_videos)
            .all()
        )
        video_ids = [v.id for v in videos]

        styles = (
            db.query(VideoStyleAnalysis)
            .filter(VideoStyleAnalysis.video_id.in_(video_ids))
            .all()
        )
        style_by_video = {style.video_id: style for style in styles}
        visuals = (
            db.query(VisualAnalysis)
            .filter(VisualAnalysis.video_id.in_(video_ids))
            .order_by(VisualAnalysis.created_at.desc())
            .all()
        )
        visual_by_video: dict[uuid.UUID, VisualAnalysis] = {}
        for visual in visuals:
            if visual.video_id not in visual_by_video:
                visual_by_video[visual.video_id] = visual

        analyses = [
            _style_to_dict(style_by_video[video_id], visual_by_video.get(video_id))
            for video_id in video_ids
            if video_id in style_by_video
        ]
        aggregated = aggregate_video_analyses(analyses)

        try:
            report = generate_creator_report(
                aggregated=aggregated,
                creator_name=creator.display_name if creator else None,
            )
        except (ReportGenerationError, ValueError, Exception) as exc:
            logger.exception("creator report generation failed batch_task_id=%s", batch_task_id)
            batch_task.status = "failed"
            batch_task.error_code = "llm_parse_failed"
            batch_task.error_message = str(exc)
            batch_task.progress = 100
            batch_task.updated_at = datetime.now(UTC)
            db.commit()
            return {"status": "failed", "error": "llm_parse_failed"}

        creator_report = CreatorReport(
            creator_id=batch_task.creator_id,
            sample_video_count=len(analyses),
            report_markdown=report["reportMarkdown"],
            report_json=report["reportJson"],
        )
        db.add(creator_report)

        batch_task.status = "completed"
        batch_task.progress = 100
        batch_task.current_step = "创作者报告已生成"
        batch_task.finished_videos = batch_task.total_videos
        batch_task.updated_at = datetime.now(UTC)
        db.commit()

        return {"status": "completed", "creatorId": str(batch_task.creator_id)}
    finally:
        db.close()
