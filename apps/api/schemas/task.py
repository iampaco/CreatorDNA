from pydantic import BaseModel


class UploadVideoResponse(BaseModel):
    videoId: str
    taskId: str
    status: str = "queued"


class TaskProgressResponse(BaseModel):
    taskId: str
    status: str
    progress: int = 0
    currentStep: str | None = None
    finishedVideos: int | None = None
    totalVideos: int | None = None
    error: str | None = None
    downloadUrl: str | None = None
