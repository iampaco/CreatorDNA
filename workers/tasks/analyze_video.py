import logging
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.config import get_settings
from apps.api.db.models.analysis_task import AnalysisTask
from apps.api.db.models.transcript import Transcript
from apps.api.db.models.video import Video
from apps.api.db.models.video_style_analysis import VideoStyleAnalysis
from apps.api.db.models.visual_analysis import VisualAnalysis
from apps.api.services.storage import StorageService
from workers.celery_app import celery_app
from workers.services.asr import AsrError, transcribe_audio
from workers.services.ffmpeg import (
    FfmpegError,
    compute_frame_timestamps,
    extract_audio_wav,
    extract_frames_at_timestamps,
    probe_duration,
)
from workers.services.llm import LlmError, analyze_structure
from workers.services.vision import VisionError, analyze_frames

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def _update_task(
    db: Session,
    task: AnalysisTask,
    *,
    status: str | None = None,
    progress: int | None = None,
    current_step: str | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
) -> None:
    if status is not None:
        task.status = status
    if progress is not None:
        task.progress = progress
    if current_step is not None:
        task.current_step = current_step
    if error_code is not None:
        task.error_code = error_code
    if error_message is not None:
        task.error_message = error_message
    task.updated_at = datetime.now(UTC)
    db.commit()


def _clear_prior_results(db: Session, video_id: uuid.UUID) -> None:
    for model in (Transcript, VisualAnalysis, VideoStyleAnalysis):
        db.query(model).filter(model.video_id == video_id).delete()
    db.commit()


@celery_app.task(name="workers.tasks.analyze_video.analyze_video_task", bind=True)
def analyze_video_task(self, task_id: str) -> dict:
    db = SessionLocal()
    storage = StorageService()
    try:
        task_uuid = uuid.UUID(task_id)
        task = db.get(AnalysisTask, task_uuid)
        if not task:
            raise LookupError(f"task not found: {task_id}")

        video = db.get(Video, task.video_id)
        if not video:
            raise LookupError(f"video not found for task: {task_id}")

        object_key = task.media_object_key or video.media_object_key
        if not object_key:
            raise ValueError("missing media object key")

        _update_task(db, task, status="processing", progress=10, current_step="准备媒体")
        _clear_prior_results(db, video.id)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_path = tmp / "capture.webm"
            wav_path = tmp / "audio.wav"
            frames_dir = tmp / "frames"
            input_path.write_bytes(storage.download_bytes(object_key))

            _update_task(db, task, progress=20, current_step="提取关键帧")
            visual_summary: dict | None = None
            vision_model: str | None = None
            frame_analyses: list[dict] = []

            try:
                duration = probe_duration(input_path)
                video.duration_seconds = duration
                db.commit()

                timestamps = compute_frame_timestamps(duration)
                extracted = extract_frames_at_timestamps(input_path, frames_dir, timestamps)

                for index, frame in enumerate(extracted, start=1):
                    frame_key = storage.build_frame_key(video.id, index)
                    storage.upload_bytes(
                        key=frame_key,
                        data=frame.path.read_bytes(),
                        content_type="image/jpeg",
                    )

                _update_task(db, task, progress=35, current_step="视觉分析")
                vision_result = analyze_frames(
                    frame_paths=[frame.path for frame in extracted],
                    timestamps=[frame.timestamp for frame in extracted],
                )
                frame_analyses = vision_result.get("frames", [])
                visual_summary = vision_result.get("summary")
                vision_model = str(vision_result.get("raw_model") or "unknown")

                visual_row = VisualAnalysis(
                    video_id=video.id,
                    frames=frame_analyses,
                    summary=visual_summary,
                    vision_model=vision_model,
                )
                db.add(visual_row)
                db.commit()
            except (FfmpegError, VisionError, ValueError) as exc:
                logger.exception("vision pipeline failed task_id=%s", task_id)
                _update_task(
                    db,
                    task,
                    status="failed",
                    progress=100,
                    current_step="视觉分析失败",
                    error_code="vision_failed",
                    error_message=str(exc),
                )
                return {"status": "failed", "error": "vision_failed"}

            try:
                extract_audio_wav(input_path, wav_path)
            except FfmpegError as exc:
                _update_task(
                    db,
                    task,
                    status="failed",
                    progress=100,
                    current_step="音频提取失败",
                    error_code="asr_failed",
                    error_message=str(exc),
                )
                return {"status": "failed", "error": "asr_failed"}

            _update_task(db, task, progress=55, current_step="语音转写")

            try:
                asr_result = transcribe_audio(wav_path)
            except AsrError as exc:
                _update_task(
                    db,
                    task,
                    status="failed",
                    progress=100,
                    current_step="语音转写失败",
                    error_code="asr_failed",
                    error_message=str(exc),
                )
                return {"status": "failed", "error": "asr_failed"}

            transcript = Transcript(
                video_id=video.id,
                language=asr_result["language"],
                full_text=asr_result["full_text"],
                segments=asr_result["segments"],
                words=[],
                asr_model=asr_result["asr_model"],
            )
            db.add(transcript)
            db.commit()

            _update_task(db, task, progress=75, current_step="结构分析")

            try:
                structure = analyze_structure(
                    transcript_text=asr_result["full_text"],
                    title=video.title,
                    visual_summary=visual_summary,
                )
            except (LlmError, ValueError, Exception) as exc:
                logger.exception("structure analysis failed task_id=%s", task_id)
                _update_task(
                    db,
                    task,
                    status="failed",
                    progress=100,
                    current_step="结构分析失败",
                    error_code="llm_parse_failed",
                    error_message=str(exc),
                )
                return {"status": "failed", "error": "llm_parse_failed"}

            shooting_style = structure.get("shootingStyle")
            if visual_summary and visual_summary.get("shootingStyleHint"):
                shooting_style = str(visual_summary["shootingStyleHint"])

            style = VideoStyleAnalysis(
                video_id=video.id,
                hook_type=structure.get("hookType"),
                hook_text=structure.get("hookText"),
                topic_category=structure.get("topicCategory"),
                target_audience=structure.get("targetAudience"),
                content_structure=structure.get("contentStructure"),
                emotional_tone=structure.get("emotionalTone"),
                common_phrases=structure.get("commonPhrases"),
                ending_type=structure.get("endingType"),
                shooting_style=shooting_style,
                reusable_template=structure.get("reusableTemplate"),
                raw_analysis={**structure, "visualSummary": visual_summary},
            )
            db.add(style)
            _update_task(db, task, status="completed", progress=100, current_step="分析完成")
            db.commit()

            if task.creator_analysis_task_id:
                from workers.tasks.analyze_creator import update_batch_progress

                update_batch_progress(db, task.creator_analysis_task_id)

            return {"status": "completed", "videoId": str(video.id)}
    finally:
        db.close()
