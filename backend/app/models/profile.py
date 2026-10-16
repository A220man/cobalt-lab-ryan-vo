"""Candidate profile ORM model."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Profile(Base):
    """A candidate profile used for job fit evaluation."""

    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    skills: Mapped[list] = mapped_column(JSON, default=lambda: [])
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    experience_level: Mapped[str] = mapped_column(String(50), default="mid")
    preferred_locations: Mapped[list] = mapped_column(JSON, default=lambda: [])
    role_types: Mapped[list] = mapped_column(JSON, default=lambda: [])
    dealbreakers: Mapped[list] = mapped_column(JSON, default=lambda: [])
    remote_preference: Mapped[str] = mapped_column(String(50), default="preferred")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )