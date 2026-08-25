"""Health check endpoint handler."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.db.session import check_db_health

router = APIRouter()


class DatabaseHealth(BaseModel):
    """Database connectivity status schema."""

    status: str = Field(description="Database connectivity status: 'connected' or 'disconnected'")
    error: Optional[str] = Field(default=None, description="Error message if disconnected")


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(default="ok", description="Application service status")
    project: str = Field(description="Project name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Execution environment")
    timestamp: datetime = Field(description="UTC timestamp of the health check")
    database: DatabaseHealth = Field(description="Database health details")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the LearnZo API and database connectivity.",
)
def get_health() -> Dict[str, Any]:
    """Retrieve application health status."""
    db_healthy, db_error = check_db_health()

    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc),
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "error": db_error,
        },
    }

