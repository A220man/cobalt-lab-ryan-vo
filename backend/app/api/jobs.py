"""Job posting API endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..core.text import extract_skills, extract_experience_level
from ..models.job import Job
from ..schemas import JobCreate, JobRead

router = APIRouter()


@router.get("/", response_model=list[JobRead])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title/company"),
    db: Session = Depends(get_db),
):
    """List job postings with optional filtering and pagination."""
    query = db.query(Job).order_by(Job.created_at.desc())
    if status:
        query = query.filter(Job.status == status)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Job.title.ilike(pattern), Job.company.ilike(pattern))
        )
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=JobRead)
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    """Create a job posting, auto-extracting skills and experience level."""
    existing = db.query(Job).filter(Job.source == data.source).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Job with this source already exists (id: {existing.id})",
        )
    job = Job(**data.model_dump())
    # Auto-enrich: extract skills and experience level from the description
    job.extracted_skills = extract_skills(data.description)
    job.experience_required = extract_experience_level(
        data.title + " " + data.description
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """Retrieve a single job posting by ID."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job