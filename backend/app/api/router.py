"""Central API router configuration."""

from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Include v1 endpoints
api_router.include_router(health.router, tags=["Health"])

