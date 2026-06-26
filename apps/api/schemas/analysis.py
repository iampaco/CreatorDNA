from pydantic import BaseModel, Field


class ContentStructurePart(BaseModel):
    part: str
    description: str


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


class TranscriptSummary(BaseModel):
    fullText: str
    language: str


class VideoAnalysisResponse(BaseModel):
    videoId: str
    transcript: TranscriptSummary | None = None
    analysis: VideoStyleAnalysisResponse | None = None
