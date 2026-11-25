"""Integration tests for the job API."""
from app.models.job import Job
from datetime import date


def _sample_job(**overrides):
    data = {
        "source": "https://example.com/jobs/1",
        "title": "Senior ML Engineer",
        "company": "Acme Corp",
        "location": "New York, NY",
        "description": "Senior ML Engineer with Python, PyTorch, Docker experience.",
        "requirements": ["Python", "PyTorch"],
    }
    data.update(overrides)
    return data


def test_create_job_auto_extracts_skills(client):
    job_data = _sample_job()
    resp = client.post("/api/v1/jobs", json=job_data)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Senior ML Engineer"
    assert "python" in data["extracted_skills"]
    assert "docker" in data["extracted_skills"]
    assert data["status"] == "new"
    assert "id" in data


def test_create_job_experience_detection(client):
    job_data = _sample_job(
        description="Junior Python Developer role. Python, Docker. 1-2 years experience."
    )
    resp = client.post("/api/v1/jobs", json=job_data)
    assert resp.status_code == 200
    assert resp.json()["experience_required"] == "junior"


def test_list_jobs(client):
    client.post("/api/v1/jobs", json=_sample_job(source="https://example.com/jobs/1"))
    client.post("/api/v1/jobs", json=_sample_job(source="https://example.com/jobs/2"))
    resp = client.get("/api/v1/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) == 2


def test_list_jobs_with_filters(client):
    client.post("/api/v1/jobs", json=_sample_job(source="https://example.com/jobs/1"))
    client.post("/api/v1/jobs", json=_sample_job(
        source="https://example.com/jobs/2",
        title="Data Scientist",
    ))
    resp = client.get("/api/v1/jobs?search=data")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Data Scientist"


def test_get_job_by_id(client):
    resp = client.post("/api/v1/jobs", json=_sample_job())
    job_id = resp.json()["id"]
    resp = client.get(f"/api/v1/jobs/{job_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Senior ML Engineer"


def test_get_job_not_found(client):
    resp = client.get("/api/v1/jobs/nonexistent-id")
    assert resp.status_code == 404


def test_create_job_duplicate_source(client):
    client.post("/api/v1/jobs", json=_sample_job())
    resp = client.post("/api/v1/jobs", json=_sample_job())
    assert resp.status_code == 409


def test_create_job_missing_required_field(client):
    resp = client.post("/api/v1/jobs", json={"title": "No source"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Application tracking (status transitions)
# ---------------------------------------------------------------------------

def test_expire_job_past_deadline(client):
    """Mark a job as expired when its deadline has passed."""
    past_date = "2025-11-15"
    job_data = _sample_job(deadline=past_date)
    resp = client.post("/api/v1/jobs", json=job_data)
    assert resp.status_code == 200
    job_id = resp.json()["id"]

    # Expire the job
    resp = client.post(f"/api/v1/jobs/{job_id}/expire")
    assert resp.status_code == 200
    assert resp.json()["status"] == "expired"


def test_expire_job_future_deadline(client):
    """Do not change status when deadline is in the future."""
    future_date = "2026-12-31"
    job_data = _sample_job(deadline=future_date)
    resp = client.post("/api/v1/jobs", json=job_data)
    assert resp.status_code == 200
    job_id = resp.json()["id"]

    resp = client.post(f"/api/v1/jobs/{job_id}/expire")
    assert resp.status_code == 200
    # Status should remain "new"
    assert resp.json()["status"] == "new"


def test_fail_job(client):
    """Mark a job as fetch_failed."""
    job_data = _sample_job()
    resp = client.post("/api/v1/jobs", json=job_data)
    assert resp.status_code == 200
    job_id = resp.json()["id"]

    resp = client.post(f"/api/v1/jobs/{job_id}/fail")
    assert resp.status_code == 200
    assert resp.json()["status"] == "fetch_failed"


def test_fail_job_not_found(client):
    resp = client.post("/api/v1/jobs/invalid-id/fail")
    assert resp.status_code == 404


def test_expire_job_not_found(client):
    resp = client.post("/api/v1/jobs/invalid-id/expire")
    assert resp.status_code == 404


def test_retry_job(client):
    """Retry a fetch_failed job, resetting status to new."""
    # Create job and mark as fetch_failed
    job_data = _sample_job()
    resp = client.post("/api/v1/jobs", json=job_data)
    job_id = resp.json()["id"]
    resp = client.post(f"/api/v1/jobs/{job_id}/fail")
    assert resp.status_code == 200
    assert resp.json()["status"] == "fetch_failed"
    # Retry the job
    resp = client.post(f"/api/v1/jobs/{job_id}/retry")
    assert resp.status_code == 200
    assert resp.json()["status"] == "new"


def test_expire_job_deadline_today_stays_new(client):
    """A job whose deadline is today is still valid and must not expire."""
    today = date.today().isoformat()
    job_data = _sample_job(deadline=today)
    resp = client.post("/api/v1/jobs", json=job_data)
    assert resp.status_code == 200
    job_id = resp.json()["id"]

    resp = client.post(f"/api/v1/jobs/{job_id}/expire")
    assert resp.status_code == 200
    assert resp.json()["status"] == "new"


def test_retry_non_fetch_failed_job_conflicts(client):
    """Retrying a job that is not fetch_failed must be rejected (409)."""
    job_data = _sample_job()
    resp = client.post("/api/v1/jobs", json=job_data)
    job_id = resp.json()["id"]

    # Job is still 'new' -> retry must conflict, not silently reset.
    resp = client.post(f"/api/v1/jobs/{job_id}/retry")
    assert resp.status_code == 409
    # Status unchanged.
    resp = client.get(f"/api/v1/jobs/{job_id}")
    assert resp.json()["status"] == "new"
