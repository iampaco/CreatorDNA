import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from apps.api.db.session import get_db
from apps.api.schemas.error import ApiErrorResponse
from apps.api.schemas.task import TaskProgressResponse, UploadVideoResponse
from apps.api.services.analysis import get_task_or_404, get_video_analysis, task_to_response
from apps.api.services.video import VideoService
from workers.tasks.analyze_video import analyze_video_task

router = APIRouter(prefix="/api", tags=["videos"])


@router.post("/videos/upload", response_model=UploadVideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    videoUrl: str = Form(...),
    title: str | None = Form(None),
    platformVideoId: str | None = Form(None),
    db: Session = Depends(get_db),
) -> UploadVideoResponse:
    service = VideoService(db)
    try:
        video, task = service.create_upload(
            file=file,
            video_url=videoUrl,
            title=title,
            platform_video_id=platformVideoId,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "unsupported_platform":
            raise HTTPException(
                status_code=400,
                detail=ApiErrorResponse(error=code, message="Only Douyin Web is supported in V1.").model_dump(),
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
