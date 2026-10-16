"""Job posting ORM model."""
from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Date, DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from .profile import _utcnow


class Job(Base):
    """A job posting to be evaluated against candidate profiles."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    source: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[list] = mapped_column(JSON, default=lambda: [])
    extracted_skills: Mapped[list] = mapped_column(JSON, default=lambda: [])
    experience_required: Mapped[str] = mapped_column(
        String(50), default="unspecified"
    )
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )