import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from apps.api.db.session import get_db
from apps.api.deps.auth import verify_api_key
from apps.api.schemas.error import ApiErrorResponse
from apps.api.schemas.task import UploadVideoResponse
from apps.api.services.video import VideoService
from workers.tasks.analyze_video import analyze_video_task

router = APIRouter(prefix="/api", tags=["videos"])


@router.post("/videos/upload", response_model=UploadVideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    videoUrl: str = Form(...),
    title: str | None = Form(None),
    platformVideoId: str | None = Form(None),
    videoId: str | None = Form(None),
    creatorId: str | None = Form(None),
    batchTaskId: str | None = Form(None),
    db: Session = Depends(get_db),
    _api_key: str | None = Depends(verify_api_key),
) -> UploadVideoResponse:
    service = VideoService(db)
    try:
        video, task = service.create_upload(
            file=file,
            video_url=videoUrl,
            title=title,
            platform_video_id=platformVideoId,
            video_id=uuid.UUID(videoId) if videoId else None,
            creator_id=uuid.UUID(creatorId) if creatorId else None,
            batch_task_id=uuid.UUID(batchTaskId) if batchTaskId else None,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "unsupported_platform":
            raise HTTPException(
                status_code=400,
                detail=ApiErrorResponse(error=code, message="Only Douyin Web is supported in V1.").model_dump(),
            ) from exc
        if code in ("video_not_found", "video_already_uploaded", "batch_task_not_found"):
            raise HTTPException(
                status_code=400,
                detail=ApiErrorResponse(error=code, message=str(exc)).model_dump(),
            ) from exc
        if code == "file_too_large":
            raise HTTPException(
                status_code=413,
                detail=ApiErrorResponse(error=code, message="Uploaded file exceeds size limit.").model_dump(),
            ) from exc
        if code == "invalid_content_type":
            raise HTTPException(
                status_code=400,
                detail=ApiErrorResponse(error=code, message="Unsupported upload content type.").model_dump(),
            ) from exc
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(error="upload_failed", message=str(exc)).model_dump(),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=ApiErrorResponse(error="upload_failed", message="Failed to store uploaded media.").model_dump(),
        ) from exc

    analyze_video_task.delay(str(task.id))
    return UploadVideoResponse(videoId=str(video.id), taskId=str(task.id), status="queued")
