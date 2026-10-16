"""API dependency providers."""
from collections.abc import Generator

from sqlalchemy.orm import Session

from ..database import SessionLocal

__all__ = ["get_db"]


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a database session, close on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()