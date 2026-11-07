"""Evaluation and ranking API endpoints."""
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..models.evaluation import Evaluation
from ..api.deps import get_db
from ..schemas import (
    BatchEvaluationRequest,
    BatchEvaluationResponse,
    EvaluationCreate,
    EvaluationRead,
    RankingEntry,
    RankingExportQuery,
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


@router.post("/evaluations/batch", response_model=BatchEvaluationResponse)
def evaluate_all_new_jobs(
    request: BatchEvaluationRequest,
    db: Session = Depends(get_db),
):
    """Evaluate all jobs with status 'new' against the default profile (or a specific profile)."""
    service = EvaluationService(db)
    try:
        evaluations = service.evaluate_all_new_jobs(request.profile_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return BatchEvaluationResponse(
        evaluated_count=len(evaluations),
        evaluations=evaluations,
    )


@router.get("/ranking", response_model=list[RankingEntry])
def get_ranking(
    limit: int = Query(default=50, ge=1, le=200),
    min_score: float | None = Query(default=None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """Return jobs sorted by evaluation score (highest first)."""
    service = EvaluationService(db)
    results = service.get_ranking(limit, min_score)
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


@router.get("/ranking/export")
def export_ranking(
    query: RankingExportQuery = Depends(),
    db: Session = Depends(get_db),
):
    """Export ranked jobs as CSV."""
    service = EvaluationService(db)
    results = service.get_ranking(query.limit, query.min_score)

    output = StringIO()
    # CSV header
    output.write(
        "job_id,job_title,job_company,job_location,overall_score,"
        "skills_score,experience_score,location_score,role_type_score,dealbreakers_score,"
        "skill_overlap,skill_match_ratio,explanation,evaluation_id,created_at\n"
    )

    for eval, job in results:
        output.write(
            "{},{},{},{},{},{},{},{},{},{},\"{}\",{},\"{}\",{},{}\n".format(
                job.id,
                job.title.replace(",", ";"),
                job.company.replace(",", ";"),
                job.location.replace(",", ";"),
                f"{eval.overall_score:.4f}",
                f"{eval.dimension_scores.get('skills', 0):.4f}",
                f"{eval.dimension_scores.get('experience', 0):.4f}",
                f"{eval.dimension_scores.get('location', 0):.4f}",
                f"{eval.dimension_scores.get('role_type', 0):.4f}",
                f"{eval.dimension_scores.get('dealbreakers', 0):.4f}",
                "; ".join(eval.skill_overlap),
                f"{eval.skill_match_ratio:.4f}",
                eval.explanation.replace(",", ";").replace("\n", " "),
                eval.id,
                eval.created_at.isoformat(),
            )
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ranking.csv"},
    )
