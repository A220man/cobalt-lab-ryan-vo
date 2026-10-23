"""Cobalt Lab — FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .database import init_db
from .schemas import HealthResponse

__all__ = ["create_app", "app"]


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Cobalt Lab",
        description="AI-powered job fit evaluation engine",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/api/health", tags=["health"], response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok", service="cobalt-lab", version="1.0.0"
        )

    init_db()
    return app


app = create_app()