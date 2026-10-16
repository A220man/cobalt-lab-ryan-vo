"""Integration tests for the profile API."""
from app.models.profile import Profile


def test_create_default_profile(client):
    payload = {
        "name": "Alex Chen",
        "email": "alex@example.com",
        "skills": ["python", "docker", "aws"],
        "experience_years": 5,
        "experience_level": "senior",
        "preferred_locations": ["new york"],
        "role_types": ["ml engineer"],
        "dealbreakers": ["on-call"],
        "remote_preference": "preferred",
    }
    resp = client.put("/api/v1/profiles/default", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Alex Chen"
    assert data["email"] == "alex@example.com"
    assert data["is_default"] is True
    assert data["skills"] == ["python", "docker", "aws"]
    assert "id" in data
    assert "created_at" in data


def test_get_default_profile(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "skills": ["python"],
    }
    client.put("/api/v1/profiles/default", json=payload)
    resp = client.get("/api/v1/profiles/default")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["skills"] == ["python"]


def test_get_default_profile_404(client):
    """No profile exists yet → 404."""
    resp = client.get("/api/v1/profiles/default")
    assert resp.status_code == 404


def test_update_default_profile(client):
    """PUT on an existing profile updates fields."""
    client.put("/api/v1/profiles/default", json={
        "name": "Original",
        "email": "orig@example.com",
        "skills": ["python"],
    })
    resp = client.put("/api/v1/profiles/default", json={
        "name": "Updated",
        "email": "updated@example.com",
        "skills": ["python", "rust"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated"
    assert data["skills"] == ["python", "rust"]


def test_profile_validation_rejects_bad_level(client):
    """Invalid experience_level should be rejected."""
    resp = client.put("/api/v1/profiles/default", json={
        "name": "Bad",
        "email": "bad@example.com",
        "experience_level": "expert",
    })
    assert resp.status_code == 422