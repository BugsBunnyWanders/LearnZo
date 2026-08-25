"""Central API router configuration."""

from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.modules.curriculum.router import router as curriculum_router
from app.modules.diagnostics.router import router as diagnostics_router
from app.modules.learner.router import router as learners_router
from app.modules.planner.router import router as planner_router

api_router = APIRouter()

# Include v1 endpoints
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(curriculum_router)
api_router.include_router(learners_router)
api_router.include_router(planner_router)
api_router.include_router(diagnostics_router)
