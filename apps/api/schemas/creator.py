from pydantic import BaseModel, Field


class CreatorProfileInput(BaseModel):
    platform: str
    displayName: str | None = None
    username: str | None = None
    profileUrl: str
    avatarUrl: str | None = None


class CreatorVideoInput(BaseModel):
    videoUrl: str
    platformVideoId: str | None = None
    title: str | None = None
    description: str | None = None
    coverUrl: str | None = None
    likeCount: int | None = None
    commentCount: int | None = None
    collectCount: int | None = None


class CreateCreatorAnalysisRequest(BaseModel):
    platform: str = "douyin"
    creatorUrl: str
    creatorProfile: CreatorProfileInput | None = None
    videoUrls: list[str] = Field(default_factory=list)
    videos: list[CreatorVideoInput] = Field(default_factory=list)
    sampleSize: int = 10


class BatchVideoItem(BaseModel):
    videoId: str
    videoUrl: str
    platformVideoId: str | None = None
    title: str | None = None


class CreateCreatorAnalysisResponse(BaseModel):
    taskId: str
    creatorId: str
    status: str = "queued"
    totalVideos: int
    videos: list[BatchVideoItem]


class CreatorReportResponse(BaseModel):
    creatorId: str
    sampleVideoCount: int
    reportMarkdown: str
    reportJson: dict
