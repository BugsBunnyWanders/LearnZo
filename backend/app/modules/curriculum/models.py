"""SQLAlchemy models for Curriculum and Skill Graph domain."""

from typing import Any

from sqlalchemy import (
    JSON,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Skill(Base, TimestampMixin):
    """Domain competence dimension (e.g. Database Indexing, Transactions)."""

    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Backend Engineering"
    )

    # Relationships
    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        back_populates="skill",
        cascade="all, delete-orphan",
        order_by="Topic.order_index",
    )


class Topic(Base, TimestampMixin):
    """Specific study unit mapping to a primary skill and prerequisite chain."""

    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skill_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("skills.id"), nullable=False, index=True
    )

    target_mastery: Mapped[float] = mapped_column(Float, default=0.80, nullable=False)
    importance_weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    skill: Mapped["Skill"] = relationship("Skill", back_populates="topics")

    resources: Mapped[list["LearningResource"]] = relationship(
        "LearningResource",
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    prerequisites: Mapped[list["TopicPrerequisite"]] = relationship(
        "TopicPrerequisite",
        foreign_keys="TopicPrerequisite.topic_id",
        back_populates="topic",
        cascade="all, delete-orphan",
    )

    dependent_topics: Mapped[list["TopicPrerequisite"]] = relationship(
        "TopicPrerequisite",
        foreign_keys="TopicPrerequisite.prerequisite_topic_id",
        back_populates="prerequisite_topic",
        cascade="all, delete-orphan",
    )


class TopicPrerequisite(Base, TimestampMixin):
    """Prerequisite relationship defining topic DAG."""

    __tablename__ = "topic_prerequisites"
    __table_args__ = (
        UniqueConstraint("topic_id", "prerequisite_topic_id", name="uq_topic_prerequisite"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("topics.id"), nullable=False, index=True
    )
    prerequisite_topic_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("topics.id"), nullable=False, index=True
    )
    min_mastery_required: Mapped[float] = mapped_column(Float, default=0.70, nullable=False)

    # Relationships
    topic: Mapped["Topic"] = relationship(
        "Topic",
        foreign_keys=[topic_id],
        back_populates="prerequisites",
    )
    prerequisite_topic: Mapped["Topic"] = relationship(
        "Topic",
        foreign_keys=[prerequisite_topic_id],
        back_populates="dependent_topics",
    )


class LearningResource(Base, TimestampMixin):
    """Curated learning resource (e.g. YouTube video lesson) for a topic."""

    __tablename__ = "learning_resources"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    topic_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("topics.id"), nullable=False, index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), default="youtube", nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str | None] = mapped_column(String(150), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transcript_status: Mapped[str] = mapped_column(String(50), default="available", nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="resources")
