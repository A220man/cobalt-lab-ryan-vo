"""Evaluation orchestration service."""
from typing import Optional

from sqlalchemy.orm import Session

from ..core.scoring import ScoringEngine, ProfileSnapshot, JobSnapshot
from ..models.evaluation import Evaluation
from ..models.job import Job
from ..models.profile import Profile

__all__ = ["EvaluationService"]


class EvaluationService:
    """Orchestrate the job evaluation workflow.

    Fetches a job and profile from the database, converts them to
    plain-data snapshots for the :class:`ScoringEngine`, persists the
    result, and marks the job as ``scored``.
    """

    def __init__(self, db: Session):
        self.db = db
        self.engine = ScoringEngine()

    def evaluate_job(
        self, job_id: str, profile_id: Optional[str] = None
    ) -> Evaluation:
        """Evaluate *job_id* against *profile_id* (or the default profile).

        Raises :class:`ValueError` if the job or profile cannot be found.
        """
        job = self.db.get(Job, job_id)
        if not job:
            raise ValueError("Job not found")

        if profile_id:
            profile = self.db.get(Profile, profile_id)
        else:
            profile = (
                self.db.query(Profile)
                .filter(Profile.is_default.is_(True))
                .first()
            )

        if not profile:
            raise ValueError("No profile found")

        result = self.engine.evaluate(
            ProfileSnapshot(
                skills=profile.skills,
                experience_years=profile.experience_years,
                experience_level=profile.experience_level,
                preferred_locations=profile.preferred_locations,
                role_types=profile.role_types,
                dealbreakers=profile.dealbreakers,
                remote_preference=profile.remote_preference,
            ),
            JobSnapshot(
                title=job.title,
                company=job.company,
                location=job.location,
                description=job.description,
                requirements=job.requirements,
                extracted_skills=job.extracted_skills,
                experience_required=job.experience_required,
            ),
        )

        evaluation = Evaluation(
            job_id=job_id,
            profile_id=profile.id,
            overall_score=result.overall_score,
            dimension_scores=result.dimension_scores,
            dealbreaker_hits=result.dealbreaker_hits,
            skill_overlap=result.skill_overlap,
            skill_match_ratio=result.skill_match_ratio,
            explanation=result.explanation,
        )
        self.db.add(evaluation)
        job.status = "scored"
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def get_ranking(self, limit: int = 50):
        """Return (Evaluation, Job) tuples sorted by score descending.

        Only jobs with status ``scored`` are included.
        """
        return (
            self.db.query(Evaluation, Job)
            .join(Job, Evaluation.job_id == Job.id)
            .filter(Job.status == "scored")
            .order_by(Evaluation.overall_score.desc())
            .limit(limit)
            .all()
        )