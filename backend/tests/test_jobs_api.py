"""Integration tests for the job API."""
from app.models.job import Job


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