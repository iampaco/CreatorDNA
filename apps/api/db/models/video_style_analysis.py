import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.db.base import Base


class VideoStyleAnalysis(Base):
    __tablename__ = "video_style_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    hook_type: Mapped[str | None] = mapped_column(String, nullable=True)
    hook_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic_category: Mapped[str | None] = mapped_column(String, nullable=True)
    target_audience: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    content_structure: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    emotional_tone: Mapped[str | None] = mapped_column(String, nullable=True)
    common_phrases: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    ending_type: Mapped[str | None] = mapped_column(String, nullable=True)
    shooting_style: Mapped[str | None] = mapped_column(String, nullable=True)
    reusable_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
