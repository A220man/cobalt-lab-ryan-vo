"""Unit tests for the multi-dimensional scoring engine (no database)."""
import pytest

from app.core.scoring import (
    DIMENSION_WEIGHTS,
    ScoringEngine,
    JobSnapshot,
    ProfileSnapshot,
    EvaluationResult,
)


def make_profile(**kw) -> ProfileSnapshot:
    """Build a ProfileSnapshot with test-friendly defaults."""
    defaults = dict(
        skills=["python", "docker", "aws", "fastapi", "pytorch"],
        experience_years=5,
        experience_level="senior",
        preferred_locations=["new york", "remote"],
        role_types=["ml engineer", "data scientist"],
        dealbreakers=["on-call"],
        remote_preference="preferred",
    )
    defaults.update(kw)
    return ProfileSnapshot(**defaults)


def make_job(**kw) -> JobSnapshot:
    """Build a JobSnapshot with test-friendly defaults."""
    defaults = dict(
        title="Senior ML Engineer",
        company="Acme Corp",
        location="New York, NY",
        description=(
            "Senior ML Engineer at Acme Corp. We need Python, PyTorch, "
            "Docker, and AWS. On-call rotation required."
        ),
        requirements=["Python", "PyTorch", "Docker", "AWS"],
        extracted_skills=["python", "pytorch", "docker", "aws",
                          "machine learning"],
        experience_required="senior",
    )
    defaults.update(kw)
    return JobSnapshot(**defaults)


# ---------------------------------------------------------------------------
# Skills dimension
# ---------------------------------------------------------------------------

class TestSkillsScoring:
    def test_perfect_match(self):
        engine = ScoringEngine()
        profile = make_profile(skills=["python", "pytorch", "docker", "aws"])
        job = make_job(extracted_skills=["python", "pytorch", "docker", "aws"])
        result = engine.evaluate(profile, job)
        assert result.skill_match_ratio == 1.0
        assert result.dimension_scores["skills"] == 1.0

    def test_no_match(self):
        engine = ScoringEngine()
        profile = make_profile(skills=["ruby", "php"])
        job = make_job(extracted_skills=["python", "pytorch", "docker", "aws"])
        result = engine.evaluate(profile, job)
        assert result.skill_match_ratio == 0.0
        assert result.dimension_scores["skills"] == 0.0

    def test_partial_match(self):
        engine = ScoringEngine()
        profile = make_profile(skills=["python", "docker"])
        job = make_job(extracted_skills=["python", "docker", "aws"])
        result = engine.evaluate(profile, job)
        assert result.skill_match_ratio == round(2 / 3, 4)
        assert len(result.skill_overlap) == 2

    def test_skill_alias_normalization(self):
        """Skills like 'JS' should be normalised to 'javascript'."""
        engine = ScoringEngine()
        profile = make_profile(skills=["JS"])
        job = make_job(extracted_skills=["javascript"])
        result = engine.evaluate(profile, job)
        assert result.skill_match_ratio == 1.0

    def test_no_required_skills(self):
        """When the job has no extracted skills, score defaults to 1.0."""
        engine = ScoringEngine()
        profile = make_profile(skills=["python"])
        job = make_job(extracted_skills=[], requirements=[])
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["skills"] == 1.0


# ---------------------------------------------------------------------------
# Experience dimension
# ---------------------------------------------------------------------------

class TestExperienceScoring:
    def test_candidate_above_required(self):
        engine = ScoringEngine()
        profile = make_profile(experience_level="senior")
        job = make_job(experience_required="mid")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["experience"] == 1.0

    def test_candidate_equal_to_required(self):
        engine = ScoringEngine()
        profile = make_profile(experience_level="senior")
        job = make_job(experience_required="senior")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["experience"] == 1.0

    def test_candidate_one_below(self):
        engine = ScoringEngine()
        profile = make_profile(experience_level="mid")
        job = make_job(experience_required="senior")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["experience"] == 0.7

    def test_candidate_two_below(self):
        engine = ScoringEngine()
        profile = make_profile(experience_level="entry")
        job = make_job(experience_required="senior")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["experience"] == 0.3

    def test_unspecified_experience(self):
        """Jobs without an experience requirement score 1.0."""
        engine = ScoringEngine()
        profile = make_profile(experience_level="junior")
        job = make_job(experience_required="unspecified")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["experience"] == 1.0


# ---------------------------------------------------------------------------
# Location dimension
# ---------------------------------------------------------------------------

class TestLocationScoring:
    def test_exact_location_match(self):
        engine = ScoringEngine()
        profile = make_profile(preferred_locations=["new york"])
        job = make_job(location="New York, NY")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["location"] == 1.0

    def test_remote_with_preference(self):
        engine = ScoringEngine()
        profile = make_profile(remote_preference="preferred")
        job = make_job(location="Remote")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["location"] == 0.9

    def test_remote_not_wanted(self):
        engine = ScoringEngine()
        profile = make_profile(remote_preference="no")
        job = make_job(location="Remote")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["location"] == 0.6

    def test_location_mismatch(self):
        engine = ScoringEngine()
        profile = make_profile(preferred_locations=["san francisco"])
        job = make_job(location="New York, NY")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["location"] == 0.2


# ---------------------------------------------------------------------------
# Role-type dimension
# ---------------------------------------------------------------------------

class TestRoleTypeScoring:
    def test_full_match(self):
        engine = ScoringEngine()
        profile = make_profile(role_types=["ml engineer"])
        job = make_job(title="ML Engineer", description="machine learning")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["role_type"] == 1.0

    def test_partial_match(self):
        engine = ScoringEngine()
        profile = make_profile(role_types=["ml engineer", "data scientist"])
        job = make_job(title="ML Engineer", description="machine learning")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["role_type"] == 0.5

    def test_no_preference(self):
        """Empty role_types list means no preference → 1.0."""
        engine = ScoringEngine()
        profile = make_profile(role_types=[])
        job = make_job(title="ML Engineer")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["role_type"] == 1.0


# ---------------------------------------------------------------------------
# Dealbreaker dimension
# ---------------------------------------------------------------------------

class TestDealbreakers:
    def test_dealbreaker_hit(self):
        engine = ScoringEngine()
        profile = make_profile(dealbreakers=["on-call"])
        job = make_job(description="On-call rotation required")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["dealbreakers"] == 0.0
    def test_no_dealbreaker_hit(self):
        engine = ScoringEngine()
        profile = make_profile(dealbreakers=["visa sponsorship"])
        job = make_job(description="Standard software engineering role.")
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["dealbreakers"] == 1.0
        assert result.dealbreaker_hits == []


# ---------------------------------------------------------------------------
# Overall score and determinism
# ---------------------------------------------------------------------------

class TestOverallScore:
    def test_perfect_score(self):
        engine = ScoringEngine()
        profile = make_profile(
            skills=["python", "pytorch", "docker", "aws"],
            experience_level="senior",
            preferred_locations=["new york"],
            role_types=["ml engineer"],
            dealbreakers=[],
        )
        job = make_job(
            extracted_skills=["python", "pytorch", "docker", "aws"],
            experience_required="mid",
            location="New York, NY",
            title="ML Engineer",
        )
        result = engine.evaluate(profile, job)
        assert result.overall_score == 1.0

    def test_dealbreaker_zeroes_score(self):
        engine = ScoringEngine()
        profile = make_profile(
            skills=["python", "pytorch", "docker", "aws"],
            experience_level="senior",
            preferred_locations=["new york"],
            role_types=["ml engineer"],
            dealbreakers=["on-call"],
        )
        job = make_job(
            extracted_skills=["python", "pytorch", "docker", "aws"],
            experience_required="mid",
            location="New York, NY",
            title="ML Engineer",
        )
        # Dealbreaker hit zeroes the dealbreakers dimension, but not the whole score
        result = engine.evaluate(profile, job)
        assert result.dimension_scores["dealbreakers"] == 0.0
        expected = (
            0.40 * 1.0  # skills
            + 0.20 * 1.0  # experience
            + 0.15 * 1.0  # location
            + 0.15 * 1.0  # role_type
            + 0.10 * 0.0  # dealbreakers
        )
        assert result.overall_score == round(expected, 4)

    def test_determinism(self):
        """Same input always produces identical output."""
        engine = ScoringEngine()
        profile = make_profile()
        job = make_job()
        result1 = engine.evaluate(profile, job)
        result2 = engine.evaluate(profile, job)
        assert result1 == result2

    def test_custom_weights(self):
        """Engine accepts custom dimension weights."""
        weights = {
            "skills": 0.8,
            "experience": 0.1,
            "location": 0.05,
            "role_type": 0.03,
            "dealbreakers": 0.02,
        }
        engine = ScoringEngine(weights=weights)
        result = engine.evaluate(make_profile(), make_job())
        # Verify weights sum to 1.0
        assert sum(weights.values()) == pytest.approx(1.0)
        # Result should still be between 0 and 1
        assert 0.0 <= result.overall_score <= 1.0


# ---------------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------------

class TestExplanation:
    def test_explanation_contains_dimensions(self):
        engine = ScoringEngine()
        result = engine.evaluate(make_profile(), make_job())
        for dim in DIMENSION_WEIGHTS:
            assert dim in result.explanation

    def test_explanation_includes_dealbreaker(self):
        engine = ScoringEngine()
        profile = make_profile(dealbreakers=["on-call"])
        job = make_job()
        result = engine.evaluate(profile, job)
        assert "on-call" in result.explanation