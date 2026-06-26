import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.db.session import get_db
from apps.api.schemas.analysis import VideoAnalysisResponse
from apps.api.schemas.error import ApiErrorResponse
from apps.api.schemas.task import TaskProgressResponse
from apps.api.services.analysis import get_task_or_404, get_video_analysis, resolve_task_response, task_to_response

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/tasks/{task_id}", response_model=TaskProgressResponse)
def get_task(task_id: uuid.UUID, db: Session = Depends(get_db)) -> TaskProgressResponse:
    try:
        return resolve_task_response(db, task_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=404,
            detail=ApiErrorResponse(error="task_not_found", message="Task not found.").model_dump(),
        ) from exc
    return resolve_task_response(db, task_id)


@router.get("/videos/{video_id}/analysis", response_model=VideoAnalysisResponse)
def get_analysis(video_id: uuid.UUID, db: Session = Depends(get_db)) -> VideoAnalysisResponse:
    return get_video_analysis(db, video_id)
