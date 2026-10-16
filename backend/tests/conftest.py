"""Pytest configuration for backend tests.

Sets up an in-memory SQLite database so no external state is required.
"""
import os

# Must be set before importing app modules so the engine uses
# in-memory SQLite with a StaticPool (shared connection across threads).
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

# Import after env var is set — this creates the engine with StaticPool
from app.api.deps import get_db
from app.database import Base, engine
from app.main import app  # noqa: E402 — side effect: init_db() creates tables


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables before each test for isolation."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a database session for direct DB tests."""
    from app.database import SessionLocal

    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db):
    """Provide a FastAPI TestClient with the test database session."""

    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()