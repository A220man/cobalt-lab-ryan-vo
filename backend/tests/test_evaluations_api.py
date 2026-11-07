"""Integration tests for the evaluation API — the end-to-end workflow."""

PROFILE_DATA = {
    "name": "Alex Chen",
    "email": "alex@example.com",
    "skills": ["python", "docker", "aws", "pytorch"],
    "experience_years": 5,
    "experience_level": "senior",
    "preferred_locations": ["new york"],
    "role_types": ["ml engineer"],
    "dealbreakers": [],
    "remote_preference": "preferred",
}

JOB_DATA = {
    "source": "https://example.com/jobs/1",
    "title": "Senior ML Engineer",
    "company": "Acme Corp",
    "location": "New York, NY",
    "description": (
        "We are looking for a Senior ML Engineer to build and deploy "
        "machine learning models. Experience with Python, PyTorch, Docker, "
        "and AWS required. On-call rotation optional."
    ),
    "requirements": ["Python", "PyTorch", "Docker", "AWS"],
}


def test_end_to_end_evaluation(client):
    """Full workflow: create profile → create job → evaluate → check score."""
    # 1. Create default profile
    resp = client.put("/api/v1/profiles/default", json=PROFILE_DATA)
    assert resp.status_code == 200

    # 2. Create a job
    resp = client.post("/api/v1/jobs", json=JOB_DATA)
    assert resp.status_code == 200
    job_id = resp.json()["id"]
    assert resp.json()["status"] == "new"

    # 3. Evaluate the job against the default profile
    resp = client.post("/api/v1/evaluations", json={"job_id": job_id})
    assert resp.status_code == 200
    eval_data = resp.json()

    # 4. Verify the evaluation has meaningful scores
    assert eval_data["overall_score"] > 0.0
    assert eval_data["overall_score"] <= 1.0
    assert "skills" in eval_data["dimension_scores"]
    assert "experience" in eval_data["dimension_scores"]
    assert "location" in eval_data["dimension_scores"]
    assert "role_type" in eval_data["dimension_scores"]
    assert "dealbreakers" in eval_data["dimension_scores"]
    assert eval_data["skill_overlap"]  # should have matched skills
    assert eval_data["skill_match_ratio"] > 0.0

    # 5. Job status should be "scored" after evaluation
    resp = client.get(f"/api/v1/jobs/{job_id}")
    assert resp.json()["status"] == "scored"


def test_ranking_returns_sorted_results(client):
    """Ranking endpoint returns jobs sorted by score descending."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)

    # Create two jobs with different skill matches
    good_job = client.post("/api/v1/jobs", json=JOB_DATA).json()
    poor_job = client.post(
        "/api/v1/jobs",
        json={**JOB_DATA, "source": "https://example.com/jobs/2",
              "title": "DevOps Engineer", "description": "Linux, sysadmin only."},
    ).json()

    # Evaluate both
    client.post("/api/v1/evaluations", json={"job_id": good_job["id"]})
    client.post("/api/v1/evaluations", json={"job_id": poor_job["id"]})

    resp = client.get("/api/v1/ranking")
    assert resp.status_code == 200
    rankings = resp.json()
    assert len(rankings) == 2
    assert rankings[0]["overall_score"] >= rankings[1]["overall_score"]
    # The ML job should rank higher (skills match)
    assert rankings[0]["job_title"] == "Senior ML Engineer"


def test_evaluate_job_not_found(client):
    """Evaluating a non-existent job returns 404."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)
    resp = client.post("/api/v1/evaluations", json={"job_id": "nonexistent"})
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_evaluate_no_profile(client):
    """Evaluating when no default profile exists returns 404."""
    resp = client.post("/api/v1/jobs", json=JOB_DATA)
    job_id = resp.json()["id"]
    resp = client.post("/api/v1/evaluations", json={"job_id": job_id})
    assert resp.status_code == 404
    assert "profile" in resp.json()["detail"].lower()


def test_list_evaluations(client):
    """List endpoint returns all evaluations."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)
    job = client.post("/api/v1/jobs", json=JOB_DATA).json()
    client.post("/api/v1/evaluations", json={"job_id": job["id"]})

    resp = client.get("/api/v1/evaluations")
    assert resp.status_code == 200
    evals = resp.json()
    assert len(evals) == 1
    assert evals[0]["job_id"] == job["id"]


def test_ranking_empty(client):
    """Ranking returns empty list when no evaluations exist."""
    resp = client.get("/api/v1/ranking")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Batch Evaluation
# ---------------------------------------------------------------------------

def test_batch_evaluate_all_new_jobs(client):
    """Batch evaluate all new jobs against default profile."""
    # Create default profile
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)

    # Create multiple new jobs
    job1 = client.post("/api/v1/jobs", json=JOB_DATA).json()
    job2 = client.post(
        "/api/v1/jobs",
        json={**JOB_DATA, "source": "https://example.com/jobs/2", "title": "Backend Engineer", "description": "Python, Django, PostgreSQL."},
    ).json()
    job3 = client.post(
        "/api/v1/jobs",
        json={**JOB_DATA, "source": "https://example.com/jobs/3", "title": "DevOps Engineer", "description": "Linux, sysadmin only."},
    ).json()

    # All jobs should be "new" initially
    assert job1["status"] == "new"
    assert job2["status"] == "new"
    assert job3["status"] == "new"

    # Batch evaluate all new jobs
    resp = client.post("/api/v1/evaluations/batch", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluated_count"] == 3
    assert len(data["evaluations"]) == 3

    # All jobs should now be "scored"
    for job_id in [job1["id"], job2["id"], job3["id"]]:
        resp = client.get(f"/api/v1/jobs/{job_id}")
        assert resp.json()["status"] == "scored"


def test_batch_evaluate_empty(client):
    """Batch evaluate with no new jobs returns empty list."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)
    resp = client.post("/api/v1/evaluations/batch", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert data["evaluated_count"] == 0
    assert data["evaluations"] == []


def test_batch_evaluate_no_profile(client):
    """Batch evaluate without profile returns 404."""
    # Create a job but no profile
    client.post("/api/v1/jobs", json=JOB_DATA)
    resp = client.post("/api/v1/evaluations/batch", json={})
    assert resp.status_code == 404
    assert "profile" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Ranking with min_score filter
# ---------------------------------------------------------------------------

def test_ranking_min_score_filter(client):
    """Ranking endpoint filters by minimum score."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)

    # Create jobs with different match quality
    good_job = client.post("/api/v1/jobs", json=JOB_DATA).json()
    poor_job = client.post(
        "/api/v1/jobs",
        json={**JOB_DATA, "source": "https://example.com/jobs/2", "title": "DevOps Engineer", "description": "Linux, sysadmin only."},
    ).json()

    # Evaluate both
    client.post("/api/v1/evaluations", json={"job_id": good_job["id"]})
    client.post("/api/v1/evaluations", json={"job_id": poor_job["id"]})

    # Get ranking with min_score filter
    resp = client.get("/api/v1/ranking?min_score=0.7")
    assert resp.status_code == 200
    rankings = resp.json()
    # Only the good job should meet the threshold
    assert len(rankings) == 1
    assert rankings[0]["job_title"] == "Senior ML Engineer"
    assert rankings[0]["overall_score"] >= 0.7


def test_ranking_min_score_zero_includes_all(client):
    """Ranking with min_score=0 includes all scored jobs."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)

    good_job = client.post("/api/v1/jobs", json=JOB_DATA).json()
    poor_job = client.post(
        "/api/v1/jobs",
        json={**JOB_DATA, "source": "https://example.com/jobs/2", "title": "DevOps Engineer", "description": "Linux, sysadmin only."},
    ).json()

    client.post("/api/v1/evaluations", json={"job_id": good_job["id"]})
    client.post("/api/v1/evaluations", json={"job_id": poor_job["id"]})

    resp = client.get("/api/v1/ranking?min_score=0.0")
    assert resp.status_code == 200
    rankings = resp.json()
    assert len(rankings) == 2


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def test_export_ranking_csv(client):
    """Export ranking as CSV."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)

    job = client.post("/api/v1/jobs", json=JOB_DATA).json()
    client.post("/api/v1/evaluations", json={"job_id": job["id"]})

    resp = client.get("/api/v1/ranking/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=ranking.csv" in resp.headers["content-disposition"]

    content = resp.text
    lines = content.strip().split("\n")
    assert len(lines) == 2  # header + 1 data row
    # Check header
    assert "job_id" in lines[0]
    assert "job_title" in lines[0]
    assert "overall_score" in lines[0]
    assert "skills_score" in lines[0]
    assert "skill_overlap" in lines[0]
    # Check data row
    assert "Senior ML Engineer" in lines[1]
    assert "Acme Corp" in lines[1]


def test_export_ranking_csv_with_min_score(client):
    """Export ranking as CSV with min_score filter."""
    client.put("/api/v1/profiles/default", json=PROFILE_DATA)

    good_job = client.post("/api/v1/jobs", json=JOB_DATA).json()
    poor_job = client.post(
        "/api/v1/jobs",
        json={**JOB_DATA, "source": "https://example.com/jobs/2", "title": "DevOps Engineer", "description": "Linux, sysadmin only."},
    ).json()

    client.post("/api/v1/evaluations", json={"job_id": good_job["id"]})
    client.post("/api/v1/evaluations", json={"job_id": poor_job["id"]})

    resp = client.get("/api/v1/ranking/export?min_score=0.7")
    assert resp.status_code == 200
    content = resp.text
    lines = content.strip().split("\n")
    assert len(lines) == 2  # header + 1 data row (only good job)


def test_export_ranking_csv_empty(client):
    """Export ranking CSV when no evaluations exist."""
    resp = client.get("/api/v1/ranking/export")
    assert resp.status_code == 200
    content = resp.text
    lines = content.strip().split("\n")
    assert len(lines) == 1  # only header
    assert "job_id" in lines[0]
