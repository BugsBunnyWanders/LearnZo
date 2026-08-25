"""Diagnostic assessment API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.diagnostics.schemas import (
    DiagnosticAttemptRead,
    DiagnosticAttemptStart,
    DiagnosticQuestionPublic,
    DiagnosticResultResponse,
    DiagnosticSeedResponse,
    DiagnosticSubmissionPayload,
)
from app.modules.diagnostics.service import DiagnosticService

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])


@router.get(
    "/questions",
    response_model=List[DiagnosticQuestionPublic],
    summary="Get Diagnostic Questions",
    description="Retrieve sanitized active diagnostic questions for learner evaluation.",
)
def get_diagnostic_questions(
    skill_id: Optional[str] = Query(default=None, description="Optional skill ID filter"),
    db: Session = Depends(get_db),
) -> List[DiagnosticQuestionPublic]:
    """List public diagnostic questions."""
    service = DiagnosticService(db)
    return service.list_questions_public(skill_id=skill_id)


@router.post(
    "/start",
    response_model=DiagnosticAttemptRead,
    status_code=status.HTTP_201_CREATED,
    summary="Start Diagnostic Attempt",
    description="Initiate a new onboarding diagnostic assessment session for a learner.",
)
def start_diagnostic_attempt(
    payload: DiagnosticAttemptStart,
    db: Session = Depends(get_db),
) -> DiagnosticAttemptRead:
    """Start diagnostic assessment."""
    service = DiagnosticService(db)
    return service.start_attempt(payload.learner_id)


@router.post(
    "/{attempt_id}/submit",
    response_model=DiagnosticResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Diagnostic Answers",
    description="Submit answers for evaluation, generate skill evidence, update learner model, and receive detailed score breakdown.",
)
def submit_diagnostic_answers(
    attempt_id: str,
    payload: DiagnosticSubmissionPayload,
    db: Session = Depends(get_db),
) -> DiagnosticResultResponse:
    """Submit diagnostic answers and update learner mastery states."""
    service = DiagnosticService(db)
    return service.submit_attempt(attempt_id, payload)


@router.get(
    "/{attempt_id}",
    response_model=DiagnosticResultResponse,
    summary="Get Diagnostic Result",
    description="Retrieve the detailed evaluation breakdown for an existing diagnostic attempt.",
)
def get_diagnostic_result(
    attempt_id: str,
    db: Session = Depends(get_db),
) -> DiagnosticResultResponse:
    """Get diagnostic result."""
    service = DiagnosticService(db)
    return service.get_attempt_result(attempt_id)


@router.post(
    "/seed",
    response_model=DiagnosticSeedResponse,
    summary="Seed Diagnostic Questions",
    description="Seed default 14 diagnostic MCQs across the 7 backend engineering skills.",
)
def seed_diagnostic_questions(
    force: bool = Query(default=False, description="Force re-seeding even if questions exist"),
    db: Session = Depends(get_db),
) -> DiagnosticSeedResponse:
    """Seed diagnostic questions."""
    service = DiagnosticService(db)
    return service.seed_questions(force=force)

