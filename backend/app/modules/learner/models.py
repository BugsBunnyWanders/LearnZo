"""SQLAlchemy models for Learner profile, Skill State, and Skill Evidence."""

import uuid
from datetime import datetime
from typing import Any, List, Optional
from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


def generate_uuid_str(prefix: str = "") -> str:
    """Generate a prefixed UUID string."""
    return f"{prefix}{uuid.uuid4().hex}"


class Learner(Base, TimestampMixin):
    """Learner entity representing the user profile in the learning loop."""

    __tablename__ = "learners"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_uuid_str("learner_"),
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    target_role: Mapped[str] = mapped_column(String(100), default="Backend SDE2", nullable=False)
    target_mastery: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    experience_level: Mapped[str] = mapped_column(
        String(100), default="Mid-level SDE", nullable=False
    )

    # Relationships
    skill_states: Mapped[List["LearnerSkillState"]] = relationship(
        "LearnerSkillState",
        back_populates="learner",
        cascade="all, delete-orphan",
    )
    evidence_list: Mapped[List["SkillEvidence"]] = relationship(
        "SkillEvidence",
        back_populates="learner",
        cascade="all, delete-orphan",
        order_by="desc(SkillEvidence.created_at)",
    )


class LearnerSkillState(Base, TimestampMixin):
    """Current competency state of a learner for a specific skill dimension."""

    __tablename__ = "learner_skill_states"
    __table_args__ = (
        UniqueConstraint("learner_id", "skill_id", name="uq_learner_skill"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learner_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_assessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    learner: Mapped["Learner"] = relationship("Learner", back_populates="skill_states")
    skill: Mapped["app.modules.curriculum.models.Skill"] = relationship(  # noqa: F821
        "Skill",
        lazy="joined",
    )


class SkillEvidence(Base, TimestampMixin):
    """Structured evidence item proving competence in a specific skill."""

    __tablename__ = "skill_evidence"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_uuid_str("ev_"),
    )
    learner_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g. "diagnostic", "quiz", "assignment", "judge"
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0.0 - 1.0
    confidence: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)  # 0.0 - 1.0
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    learner: Mapped["Learner"] = relationship("Learner", back_populates="evidence_list")
    skill: Mapped["app.modules.curriculum.models.Skill"] = relationship(  # noqa: F821
        "Skill",
        lazy="joined",
    )

