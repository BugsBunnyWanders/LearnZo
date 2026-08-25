"""Learner API endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.learner.schemas import (
    LearnerCreate,
    LearnerProfileSummary,
    LearnerSkillStateRead,
    SkillEvidenceRead,
)
from app.modules.learner.service import LearnerService

router = APIRouter(prefix="/learners", tags=["Learners"])


@router.post(
    "/onboard",
    response_model=LearnerProfileSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Onboard Learner",
    description="Register a new learner profile and initialize competence states across the curriculum.",
)
def onboard_learner(
    data: LearnerCreate,
    db: Session = Depends(get_db),
) -> LearnerProfileSummary:
    """Onboard a new learner."""
    service = LearnerService(db)
    return service.onboard_learner(data)


@router.get(
    "/{learner_id}",
    response_model=LearnerProfileSummary,
    summary="Get Learner Profile",
    description="Retrieve comprehensive learner profile, target role readiness percentage, and recent evidence.",
)
def get_learner_profile(
    learner_id: str,
    db: Session = Depends(get_db),
) -> LearnerProfileSummary:
    """Get full learner profile."""
    service = LearnerService(db)
    return service.get_learner_profile(learner_id)


@router.get(
    "/{learner_id}/skills",
    response_model=list[LearnerSkillStateRead],
    summary="Get Learner Skill States",
    description="Retrieve all competency skill mastery scores and confidence estimates for a learner.",
)
def get_learner_skills(
    learner_id: str,
    db: Session = Depends(get_db),
) -> list[LearnerSkillStateRead]:
    """Get learner skill states."""
    service = LearnerService(db)
    return service.get_learner_skill_states(learner_id)


@router.get(
    "/{learner_id}/evidence",
    response_model=list[SkillEvidenceRead],
    summary="Get Learner Skill Evidence",
    description="Retrieve chronological audit log of skill evidence proving learner competence.",
)
def get_learner_evidence(
    learner_id: str,
    skill_id: str | None = Query(default=None, description="Filter by specific skill ID"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
) -> list[SkillEvidenceRead]:
    """Get learner skill evidence history."""
    service = LearnerService(db)
    return service.get_learner_evidence_history(learner_id, skill_id=skill_id, limit=limit)
