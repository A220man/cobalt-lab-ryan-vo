"""Integration test: health endpoint."""


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "cobalt-lab"
    assert "version" in data
    assert data["version"] == "1.0.0"


def test_health_not_found():
    """Unknown routes return 404."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        resp = c.get("/api/nonexistent")
        assert resp.status_code == 404