"""Database repository for Diagnostic questions, attempts, and answers."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.diagnostics.models import (
    DiagnosticAnswer,
    DiagnosticAttempt,
    DiagnosticQuestion,
)


class DiagnosticRepository:
    """Encapsulates database queries for diagnostic assessment entities."""

    def __init__(self, db: Session):
        self.db = db

    def count_questions(self) -> int:
        """Return total count of diagnostic questions in database."""
        return self.db.query(DiagnosticQuestion).count()

    def list_active_questions(
        self, skill_id: Optional[str] = None
    ) -> List[DiagnosticQuestion]:
        """Fetch all active diagnostic questions ordered by order_index."""
        stmt = (
            select(DiagnosticQuestion)
            .options(joinedload(DiagnosticQuestion.skill))
            .where(DiagnosticQuestion.is_active.is_(True))
            .order_by(DiagnosticQuestion.order_index, DiagnosticQuestion.id)
        )
        if skill_id:
            stmt = stmt.where(DiagnosticQuestion.skill_id == skill_id)
        return list(self.db.scalars(stmt).all())

    def get_question_by_id(self, question_id: str) -> Optional[DiagnosticQuestion]:
        """Fetch a single question by its ID."""
        stmt = (
            select(DiagnosticQuestion)
            .options(joinedload(DiagnosticQuestion.skill))
            .where(DiagnosticQuestion.id == question_id)
        )
        return self.db.scalars(stmt).first()

    def get_questions_by_ids(self, question_ids: List[str]) -> List[DiagnosticQuestion]:
        """Fetch multiple questions by IDs."""
        stmt = (
            select(DiagnosticQuestion)
            .options(joinedload(DiagnosticQuestion.skill))
            .where(DiagnosticQuestion.id.in_(question_ids))
        )
        return list(self.db.scalars(stmt).all())

    def create_attempt(self, attempt: DiagnosticAttempt) -> DiagnosticAttempt:
        """Persist a new diagnostic assessment attempt."""
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def get_attempt_by_id(self, attempt_id: str) -> Optional[DiagnosticAttempt]:
        """Fetch attempt with its answers and associated questions."""
        stmt = (
            select(DiagnosticAttempt)
            .options(
                joinedload(DiagnosticAttempt.learner),
                selectinload(DiagnosticAttempt.answers)
                .joinedload(DiagnosticAnswer.question)
                .joinedload(DiagnosticQuestion.skill),
            )
            .where(DiagnosticAttempt.id == attempt_id)
        )
        return self.db.scalars(stmt).unique().first()

    def add_answers(self, answers: List[DiagnosticAnswer]) -> None:
        """Persist multiple diagnostic answer choices."""
        self.db.add_all(answers)
        self.db.flush()

