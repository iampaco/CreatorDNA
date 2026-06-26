from pydantic import BaseModel, Field


class ContentStructurePart(BaseModel):
    part: str
    description: str


class FrameAnalysisResponse(BaseModel):
    frameTime: float
    shotType: str | None = None
    cameraAngle: str | None = None
    composition: str | None = None
    background: str | None = None
    subtitleVisible: bool | None = None
    subtitlePosition: str | None = None
    subtitleStyle: str | None = None
    visualElements: list[str] = Field(default_factory=list)
    bRoll: bool | None = None


class VisualAnalysisResponse(BaseModel):
    videoId: str
    frames: list[FrameAnalysisResponse] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)
    visionModel: str | None = None


class VideoStyleAnalysisResponse(BaseModel):
    videoId: str
    hookType: str | None = None
    hookText: str | None = None
    topicCategory: str | None = None
    targetAudience: list[str] = Field(default_factory=list)
    contentStructure: list[ContentStructurePart] = Field(default_factory=list)
    emotionalTone: str | None = None
    commonPhrases: list[str] = Field(default_factory=list)
    endingType: str | None = None
    shootingStyle: str | None = None
    reusableTemplate: str | None = None
    subtitlePosition: str | None = None
    subtitleStyle: str | None = None
    subtitleConsistency: str | None = None


class TranscriptSummary(BaseModel):
    fullText: str
    language: str


class VideoAnalysisResponse(BaseModel):
    videoId: str
    transcript: TranscriptSummary | None = None
    analysis: VideoStyleAnalysisResponse | None = None
    visualAnalysis: VisualAnalysisResponse | None = None
