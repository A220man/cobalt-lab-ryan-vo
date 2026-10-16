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
        "Senior ML Engineer at Acme Corp. We need Python, PyTorch, "
        "Docker, and AWS. Build ML pipelines."
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