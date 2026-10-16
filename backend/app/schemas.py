"""Pydantic request/response schemas for the API."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

class ProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=1, max_length=255)
    skills: list[str] = Field(default_factory=list, max_length=50)
    experience_years: int = Field(default=0, ge=0, le=50)
    experience_level: str = Field(default="mid")
    preferred_locations: list[str] = Field(default_factory=list, max_length=10)
    role_types: list[str] = Field(default_factory=list, max_length=10)
    dealbreakers: list[str] = Field(default_factory=list, max_length=20)
    remote_preference: str = Field(default="preferred")

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, v: str) -> str:
        valid = {"entry", "junior", "mid", "senior", "lead", "principal"}
        if v not in valid:
            raise ValueError(f"experience_level must be one of {valid}")
        return v

    @field_validator("remote_preference")
    @classmethod
    def validate_remote_preference(cls, v: str) -> str:
        valid = {"required", "preferred", "optional", "no"}
        if v not in valid:
            raise ValueError(f"remote_preference must be one of {valid}")
        return v


class ProfileCreate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_default: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class JobBase(BaseModel):
    source: str = Field(..., min_length=1, max_length=2000)
    title: str = Field(..., min_length=1, max_length=500)
    company: str = Field(..., min_length=1, max_length=200)
    location: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=50000)
    requirements: list[str] = Field(default_factory=list, max_length=100)
    deadline: date | None = None


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    extracted_skills: list[str]
    experience_required: str
    status: str
    created_at: datetime
    updated_at: datetime


class JobBrief(BaseModel):
    """Minimal job fields embedded in evaluation/ranking responses."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    company: str
    location: str


# ---------------------------------------------------------------------------
# Evaluations
# ---------------------------------------------------------------------------

class EvaluationCreate(BaseModel):
    job_id: str = Field(..., min_length=1)
    profile_id: str | None = None


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    job_id: str
    profile_id: str | None
    overall_score: float
    dimension_scores: dict[str, float]
    dealbreaker_hits: list[str]
    skill_overlap: list[str]
    skill_match_ratio: float
    explanation: str | None
    created_at: datetime


class RankingEntry(BaseModel):
    job_id: str
    job_title: str
    job_company: str
    job_location: str
    overall_score: float
    dimension_scores: dict[str, float]
    skill_overlap: list[str]
    skill_match_ratio: float
    explanation: str | None
    evaluation_id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str