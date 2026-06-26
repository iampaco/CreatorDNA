import uuid

from sqlalchemy.orm import Session

from apps.api.db.models.analysis_task import AnalysisTask
from apps.api.db.models.creator_analysis_task import CreatorAnalysisTask
from apps.api.db.models.transcript import Transcript
from apps.api.db.models.video_style_analysis import VideoStyleAnalysis
from apps.api.schemas.analysis import (
    ContentStructurePart,
    TranscriptSummary,
    VideoAnalysisResponse,
    VideoStyleAnalysisResponse,
)
from apps.api.schemas.task import TaskProgressResponse


def get_task_or_404(db: Session, task_id: uuid.UUID) -> AnalysisTask:
    task = db.get(AnalysisTask, task_id)
    if not task:
        raise LookupError("task_not_found")
    return task


def get_batch_task_or_404(db: Session, task_id: uuid.UUID) -> CreatorAnalysisTask:
    task = db.get(CreatorAnalysisTask, task_id)
    if not task:
        raise LookupError("task_not_found")
    return task


def task_to_response(task: AnalysisTask) -> TaskProgressResponse:
    return TaskProgressResponse(
        taskId=str(task.id),
        status=task.status,
        progress=task.progress,
        currentStep=task.current_step,
        finishedVideos=1 if task.status == "completed" else 0,
        totalVideos=1,
        error=task.error_code,
    )


def batch_task_to_response(task: CreatorAnalysisTask) -> TaskProgressResponse:
    progress = task.progress
    if task.total_videos > 0 and task.status != "completed":
        progress = max(progress, int((task.finished_videos / task.total_videos) * 90))
    return TaskProgressResponse(
        taskId=str(task.id),
        status=task.status,
        progress=progress,
        currentStep=task.current_step,
        finishedVideos=task.finished_videos,
        totalVideos=task.total_videos,
        error=task.error_code,
    )


def resolve_task_response(db: Session, task_id: uuid.UUID) -> TaskProgressResponse:
    batch_task = db.get(CreatorAnalysisTask, task_id)
    if batch_task:
        return batch_task_to_response(batch_task)
    video_task = db.get(AnalysisTask, task_id)
    if video_task:
        return task_to_response(video_task)
    raise LookupError("task_not_found")


def get_video_analysis(db: Session, video_id: uuid.UUID) -> VideoAnalysisResponse:
    transcript = (
        db.query(Transcript)
        .filter(Transcript.video_id == video_id)
        .order_by(Transcript.created_at.desc())
        .first()
    )
    style = (
        db.query(VideoStyleAnalysis)
        .filter(VideoStyleAnalysis.video_id == video_id)
        .order_by(VideoStyleAnalysis.created_at.desc())
        .first()
    )

    transcript_summary = None
    if transcript and transcript.full_text:
        transcript_summary = TranscriptSummary(
            fullText=transcript.full_text,
            language=transcript.language or "zh",
        )

    analysis = None
    if style:
        content_structure = []
        if isinstance(style.content_structure, list):
            for item in style.content_structure:
                if isinstance(item, dict):
                    content_structure.append(
                        ContentStructurePart(
                            part=str(item.get("part", "")),
                            description=str(item.get("description", "")),
                        )
                    )
        analysis = VideoStyleAnalysisResponse(
            videoId=str(video_id),
            hookType=style.hook_type,
            hookText=style.hook_text,
            topicCategory=style.topic_category,
            targetAudience=style.target_audience if isinstance(style.target_audience, list) else [],
            contentStructure=content_structure,
            emotionalTone=style.emotional_tone,
            commonPhrases=style.common_phrases if isinstance(style.common_phrases, list) else [],
            endingType=style.ending_type,
            shootingStyle=style.shooting_style,
            reusableTemplate=style.reusable_template,
        )

    return VideoAnalysisResponse(
        videoId=str(video_id),
        transcript=transcript_summary,
        analysis=analysis,
    )
