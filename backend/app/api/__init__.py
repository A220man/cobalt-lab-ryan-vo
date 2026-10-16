"""API route package - aggregates all sub-routers."""
from fastapi import APIRouter

from .jobs import router as jobs_router
from .profiles import router as profiles_router
from .evaluations import router as evaluations_router

api_router = APIRouter()
api_router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(evaluations_router, tags=["evaluations"])

__all__ = ["api_router"]