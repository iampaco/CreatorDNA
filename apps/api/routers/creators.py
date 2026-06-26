import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.db.session import get_db
from apps.api.deps.auth import verify_api_key
from apps.api.schemas.creator import CreateCreatorAnalysisRequest, CreateCreatorAnalysisResponse
from apps.api.schemas.error import ApiErrorResponse
from apps.api.services.creator import CreatorService

router = APIRouter(prefix="/api", tags=["creators"])


@router.post("/creator-analysis", response_model=CreateCreatorAnalysisResponse)
def create_creator_analysis(
    request: CreateCreatorAnalysisRequest,
    db: Session = Depends(get_db),
    _api_key: str | None = Depends(verify_api_key),
) -> CreateCreatorAnalysisResponse:
    service = CreatorService(db)
    try:
        return service.create_analysis(request)
    except ValueError as exc:
        code = str(exc)
        messages = {
            "unsupported_platform": "Only Douyin Web is supported in V1.",
            "invalid_creator_url": "creatorUrl must be a Douyin user profile URL.",
            "invalid_video_url": "Each videoUrl must be a Douyin video URL.",
            "no_videos": "At least one video URL is required.",
        }
        raise HTTPException(
            status_code=400,
            detail=ApiErrorResponse(
                error=code,
                message=messages.get(code, str(exc)),
            ).model_dump(),
        ) from exc


@router.get("/reports/{creator_id}")
def get_creator_report(
    creator_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict:
    service = CreatorService(db)
    report = service.get_latest_report(creator_id)
    if not report:
        raise HTTPException(
            status_code=404,
            detail=ApiErrorResponse(error="report_not_found", message="Creator report not found.").model_dump(),
        )
    return report.model_dump()
