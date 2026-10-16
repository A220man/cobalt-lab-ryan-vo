"""Multi-dimensional job fit scoring engine.

The engine is pure domain logic: it accepts plain data snapshots
(:class:`ProfileSnapshot`, :class:`JobSnapshot`) and returns a
:class:`EvaluationResult`.  No database, HTTP, or LLM dependencies.
The core is fully deterministic and runs offline.
"""
from __future__ import annotations

from dataclasses import dataclass

from .text import normalize_location, normalize_skill, normalize_text

__all__ = [
    "ScoringEngine",
    "EvaluationResult",
    "ProfileSnapshot",
    "JobSnapshot",
    "DIMENSION_WEIGHTS",
    "EXPERIENCE_LEVEL_ORDER",
]

#: Per-dimension weight in the composite score.
DIMENSION_WEIGHTS: dict[str, float] = {
    "skills": 0.40,
    "experience": 0.20,
    "location": 0.15,
    "role_type": 0.15,
    "dealbreakers": 0.10,
}

#: Ordinal map for experience-level comparison.
EXPERIENCE_LEVEL_ORDER: dict[str, int] = {
    "entry": 0,
    "junior": 1,
    "mid": 2,
    "senior": 3,
    "lead": 4,
    "principal": 5,
}


# ---------------------------------------------------------------------------
# Snapshot types (input to the engine)
# ---------------------------------------------------------------------------

@dataclass
class ProfileSnapshot:
    """A plain-data snapshot of a candidate profile."""

    skills: list[str]
    experience_years: int
    experience_level: str
    preferred_locations: list[str]
    role_types: list[str]
    dealbreakers: list[str]
    remote_preference: str  # "required" | "preferred" | "optional" | "no"


@dataclass
class JobSnapshot:
    """A plain-data snapshot of a job posting."""

    title: str
    company: str
    location: str
    description: str
    requirements: list[str]
    extracted_skills: list[str]
    experience_required: str


@dataclass
class EvaluationResult:
    """Output of a single evaluation."""

    overall_score: float
    dimension_scores: dict[str, float]
    dealbreaker_hits: list[str]
    skill_overlap: list[str]
    skill_match_ratio: float
    explanation: str


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------

class ScoringEngine:
    """Evaluate job fit across five weighted dimensions.

    Dimensions:
        1. **skills** - Jaccard-style overlap of normalised skill sets.
        2. **experience** - ordinal comparison of candidate level vs.
           required level.
        3. **location** - keyword / remote-affinity matching.
        4. **role_type** - keyword overlap between preferred roles and
           job title + description.
        5. **dealbreakers** - inverted; 0.0 if any dealbreaker keyword
           appears in the job description.
    """

    def __init__(self, weights: dict[str, float] | None = None):
        self._weights = weights or DIMENSION_WEIGHTS

    # -- public API ---------------------------------------------------------

    def evaluate(
        self, profile: ProfileSnapshot, job: JobSnapshot
    ) -> EvaluationResult:
        """Score *job* against *profile* and return a result."""

        dimension_scores: dict[str, float] = {}
        dimension_scores["skills"] = self._score_skills(profile, job)
        dimension_scores["experience"] = self._score_experience(profile, job)
        dimension_scores["location"] = self._score_location(profile, job)
        dimension_scores["role_type"] = self._score_role_type(profile, job)

        hits = self._find_dealbreakers(profile, job)
        dimension_scores["dealbreakers"] = 0.0 if hits else 1.0

        overall = sum(
            dimension_scores[dim] * self._weights[dim]
            for dim in self._weights
        )

        overlap, ratio = self._compute_skill_overlap(profile, job)
        explanation = self._build_explanation(
            dimension_scores, overlap, hits
        )

        return EvaluationResult(
            overall_score=round(overall, 4),
            dimension_scores={k: round(v, 4) for k, v in dimension_scores.items()},
            dealbreaker_hits=hits,
            skill_overlap=overlap,
            skill_match_ratio=round(ratio, 4),
            explanation=explanation,
        )

    # -- dimension scorers --------------------------------------------------

    def _compute_skill_overlap(
        self, profile: ProfileSnapshot, job: JobSnapshot
    ) -> tuple[list[str], float]:
        """Return (matched_skills, ratio) for skill overlap."""
        candidate = {normalize_skill(s) for s in profile.skills}
        required = {normalize_skill(s) for s in job.extracted_skills}

        if not required:
            # Fall back to requirements list if no extracted skills
            required = {normalize_skill(s) for s in job.requirements}

        if not required:
            return [], 1.0

        overlap = sorted(candidate & required)
        ratio = len(overlap) / len(required)
        return overlap, ratio

    def _score_skills(self, profile: ProfileSnapshot, job: JobSnapshot) -> float:
        _, ratio = self._compute_skill_overlap(profile, job)
        return ratio

    def _score_experience(
        self, profile: ProfileSnapshot, job: JobSnapshot
    ) -> float:
        """Score experience-level match."""
        required_level = job.experience_required

        if required_level in ("unspecified", "", None):
            return 1.0  # No requirement stated

        candidate_num = EXPERIENCE_LEVEL_ORDER.get(profile.experience_level, 2)
        required_num = EXPERIENCE_LEVEL_ORDER.get(required_level, 2)

        if candidate_num >= required_num:
            return 1.0
        if candidate_num == required_num - 1:
            return 0.7
        return 0.3

    def _score_location(
        self, profile: ProfileSnapshot, job: JobSnapshot
    ) -> float:
        """Score location affinity."""
        job_loc = normalize_text(job.location)

        if "remote" in job_loc:
            if profile.remote_preference == "required":
                return 1.0
            if profile.remote_preference == "preferred":
                return 0.9
            return 0.6

        if not profile.preferred_locations:
            return 0.5

        for pref in profile.preferred_locations:
            if normalize_location(pref) in job_loc:
                return 1.0

        return 0.2

    def _score_role_type(
        self, profile: ProfileSnapshot, job: JobSnapshot
    ) -> float:
        """Score role-type keyword overlap."""
        if not profile.role_types:
            return 1.0

        haystack = normalize_text(job.title + " " + job.description)
        matches = sum(
            1 for rt in profile.role_types if normalize_text(rt) in haystack
        )
        return min(matches / len(profile.role_types), 1.0)

    def _find_dealbreakers(
        self, profile: ProfileSnapshot, job: JobSnapshot
    ) -> list[str]:
        """Return dealbreaker keywords found in the job description."""
        desc = normalize_text(job.description)
        return [db for db in profile.dealbreakers if normalize_text(db) in desc]

    # -- helper -------------------------------------------------------------

    @staticmethod
    def _build_explanation(
        scores: dict[str, float],
        overlap: list[str],
        hits: list[str],
    ) -> str:
        """Build a short human-readable summary."""
        parts = []
        for dim in DIMENSION_WEIGHTS:
            parts.append(f"{dim}: {scores.get(dim, 0):.0%}")
        if overlap:
            parts.append(f"Skills matched: {', '.join(overlap[:5])}")
        if hits:
            parts.append(f"Dealbreakers: {', '.join(hits)}")
        return "; ".join(parts)