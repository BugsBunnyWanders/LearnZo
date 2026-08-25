"""SQLAlchemy models for Daily Learning Plans and orchestration."""

import uuid
from datetime import date
from sqlalchemy import (
    Boolean,
    Date,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


def generate_uuid_str(prefix: str = "") -> str:
    """Generate a prefixed UUID string."""
    return f"{prefix}{uuid.uuid4().hex}"


class DailyLearningPlan(Base, TimestampMixin):
    """Orchestrated daily learning recommendation for a learner."""

    __tablename__ = "daily_learning_plans"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: generate_uuid_str("plan_"),
    )
    learner_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("learners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
        index=True,
    )
    selected_topic_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    primary_skill_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    current_mastery_score: Mapped[float] = mapped_column(Float, nullable=False)
    target_mastery_score: Mapped[float] = mapped_column(Float, nullable=False)
    skill_gap: Mapped[float] = mapped_column(Float, nullable=False)
    priority_score: Mapped[float] = mapped_column(Float, nullable=False)

    reason_code: Mapped[str] = mapped_column(
        String(50), default="HIGH_VALUE_GAP", nullable=False
    )
    reason_summary: Mapped[str] = mapped_column(Text, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    learner: Mapped["app.modules.learner.models.Learner"] = relationship(  # noqa: F821
        "Learner",
        lazy="joined",
    )
    selected_topic: Mapped["app.modules.curriculum.models.Topic"] = relationship(  # noqa: F821
        "Topic",
        lazy="joined",
    )
    primary_skill: Mapped["app.modules.curriculum.models.Skill"] = relationship(  # noqa: F821
        "Skill",
        lazy="joined",
    )

