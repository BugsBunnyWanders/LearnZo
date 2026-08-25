"""Daily Learning Planner API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.planner.schemas import (
    DailyPlanRead,
    PlannerBreakdownResponse,
)
from app.modules.planner.service import PlannerService

router = APIRouter(prefix="/learners", tags=["Planner"])


@router.get(
    "/{learner_id}/daily-plan",
    response_model=DailyPlanRead,
    summary="Get Today's Learning Plan",
    description="Retrieve today's active learning plan for the learner, computing and persisting one if not yet created.",
)
def get_daily_plan(
    learner_id: str,
    db: Session = Depends(get_db),
) -> DailyPlanRead:
    """Get or compute today's daily plan."""
    service = PlannerService(db)
    return service.get_or_create_daily_plan(learner_id=learner_id, force_regenerate=False)


@router.post(
    "/{learner_id}/daily-plan/generate",
    response_model=DailyPlanRead,
    status_code=status.HTTP_200_OK,
    summary="Generate Daily Learning Plan",
    description="Trigger daily planner ranking algorithm to compute or re-compute the next best learning topic for a learner.",
)
def generate_daily_plan(
    learner_id: str,
    force: bool = Query(
        default=False,
        description="Force re-generation and overwrite today's existing plan",
    ),
    db: Session = Depends(get_db),
) -> DailyPlanRead:
    """Generate daily learning plan."""
    service = PlannerService(db)
    return service.get_or_create_daily_plan(learner_id=learner_id, force_regenerate=force)


@router.get(
    "/{learner_id}/daily-plan/analysis",
    response_model=PlannerBreakdownResponse,
    summary="Get Planner Candidate Breakdown",
    description="Retrieve the full candidate evaluation table detailing why topics are eligible or locked by prerequisites.",
)
def get_planner_analysis(
    learner_id: str,
    db: Session = Depends(get_db),
) -> PlannerBreakdownResponse:
    """Get full planner candidate breakdown."""
    service = PlannerService(db)
    return service.get_planner_analysis(learner_id)

