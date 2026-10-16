"""Evaluation result ORM model."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .profile import _utcnow


class Evaluation(Base):
    """A score record: how well a profile matches a job."""

    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    profile_id: Mapped[str] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    dimension_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    dealbreaker_hits: Mapped[list] = mapped_column(JSON, default=lambda: [])
    skill_overlap: Mapped[list] = mapped_column(JSON, default=lambda: [])
    skill_match_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )