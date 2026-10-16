"""Evaluation and ranking API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..models.evaluation import Evaluation
from ..api.deps import get_db
from ..schemas import (
    EvaluationCreate,
    EvaluationRead,
    RankingEntry,
)
from ..services.evaluation_service import EvaluationService

router = APIRouter()


@router.post("/evaluations", response_model=EvaluationRead)
def create_evaluation(
    data: EvaluationCreate,
    db: Session = Depends(get_db),
):
    """Evaluate one job posting against a profile (or the default profile)."""
    service = EvaluationService(db)
    try:
        evaluation = service.evaluate_job(data.job_id, data.profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return evaluation


@router.get("/evaluations", response_model=list[EvaluationRead])
def list_evaluations(
    job_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List evaluation results, optionally filtered by job."""
    query = db.query(Evaluation).order_by(Evaluation.created_at.desc())
    if job_id:
        query = query.filter(Evaluation.job_id == job_id)
    return query.limit(limit).all()


@router.get("/ranking", response_model=list[RankingEntry])
def get_ranking(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return jobs sorted by evaluation score (highest first)."""
    service = EvaluationService(db)
    results = service.get_ranking(limit)
    entries = []
    for eval, job in results:
        entries.append(
            RankingEntry(
                job_id=job.id,
                job_title=job.title,
                job_company=job.company,
                job_location=job.location,
                overall_score=eval.overall_score,
                dimension_scores=eval.dimension_scores,
                skill_overlap=eval.skill_overlap,
                skill_match_ratio=eval.skill_match_ratio,
                explanation=eval.explanation,
                evaluation_id=eval.id,
                created_at=eval.created_at,
            )
        )
    return entries