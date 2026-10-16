"""Database setup: engine, session factory, declarative base."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings


def _engine_kwargs() -> dict:
    """Return engine kwargs appropriate for the configured database URL."""
    kwargs: dict = {"future": True}
    if settings.database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if settings.database_url == "sqlite:///:memory:":
            kwargs["poolclass"] = StaticPool
    return kwargs


engine = create_engine(settings.database_url, **_engine_kwargs())
SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, future=True
)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""
    pass


def get_db() -> Generator:
    """FastAPI dependency: yield a database session, close on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (used by create_app and tests)."""
    Base.metadata.create_all(bind=engine)