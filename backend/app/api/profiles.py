"""Candidate profile API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..api.deps import get_db
from ..models.profile import Profile
from ..schemas import ProfileRead, ProfileCreate

router = APIRouter()

_EXC_404 = HTTPException(
    status_code=404,
    detail="No default profile found. Create one with PUT /api/v1/profiles/default.",
)


@router.get("/default", response_model=ProfileRead)
def get_default_profile(db: Session = Depends(get_db)):
    """Return the default candidate profile."""
    profile = db.query(Profile).filter(Profile.is_default.is_(True)).first()
    if not profile:
        raise _EXC_404
    return profile


@router.put("/default", response_model=ProfileRead)
def upsert_default_profile(
    data: ProfileCreate, db: Session = Depends(get_db)
):
    """Create or update the default candidate profile."""
    profile = db.query(Profile).filter(Profile.is_default.is_(True)).first()
    if profile:
        for field, value in data.model_dump().items():
            setattr(profile, field, value)
    else:
        profile = Profile(**data.model_dump(), is_default=True)
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile