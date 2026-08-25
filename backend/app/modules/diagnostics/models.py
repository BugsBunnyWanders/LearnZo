"""SQLAlchemy models for Diagnostic assessments, questions, and attempts."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


def generate_uuid_str(prefix: str = "") -> str:
    """Generate a prefixed UUID string."""
    return f"{prefix}{uuid.uuid4().hex}"


class DiagnosticQuestion(Base, TimestampMixin):
    """Question item for the onboarding diagnostic assessment."""

    __tablename__ = "diagnostic_questions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    skill_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    difficulty_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    options_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    correct_option_id: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    skill: Mapped["app.modules.curriculum.models.Skill"] = relationship(  # noqa: F821
        "Skill",
        lazy="joined",
    )


class DiagnosticAttempt(Base, TimestampMixin):
    """A learner's attempt at the onboarding diagnostic assessment."""

    __tablename__ = "diagnostic_attempts"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_uuid_str("diag_"),
    )
    learner_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="in_progress", nullable=False, index=True
    )  # "in_progress", "completed", "abandoned"
    total_questions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    learner: Mapped["app.modules.learner.models.Learner"] = relationship(  # noqa: F821
        "Learner",
        lazy="joined",
    )
    answers: Mapped[list["DiagnosticAnswer"]] = relationship(
        "DiagnosticAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class DiagnosticAnswer(Base, TimestampMixin):
    """An individual question answer in a diagnostic attempt."""

    __tablename__ = "diagnostic_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("diagnostic_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("diagnostic_questions.id"), nullable=False, index=True
    )
    selected_option_id: Mapped[str] = mapped_column(String(10), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    attempt: Mapped["DiagnosticAttempt"] = relationship(
        "DiagnosticAttempt", back_populates="answers"
    )
    question: Mapped["DiagnosticQuestion"] = relationship("DiagnosticQuestion", lazy="joined")
