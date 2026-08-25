"""Database repository for Curriculum domain entities."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.curriculum.models import (
    LearningResource,
    Skill,
    Topic,
    TopicPrerequisite,
)


class CurriculumRepository:
    """Encapsulates database access operations for curriculum entities."""

    def __init__(self, db: Session):
        self.db = db

    def count_skills(self) -> int:
        """Return total count of skills in database."""
        return self.db.query(Skill).count()

    def count_topics(self) -> int:
        """Return total count of topics in database."""
        return self.db.query(Topic).count()

    def list_skills(self) -> list[Skill]:
        """Fetch all skills ordered by name."""
        stmt = select(Skill).order_by(Skill.name)
        return list(self.db.scalars(stmt).all())

    def get_skill_by_id(self, skill_id: str) -> Skill | None:
        """Fetch a single skill by ID."""
        stmt = select(Skill).where(Skill.id == skill_id)
        return self.db.scalars(stmt).first()

    def get_skill_by_slug(self, slug: str) -> Skill | None:
        """Fetch a single skill by slug."""
        stmt = select(Skill).where(Skill.slug == slug)
        return self.db.scalars(stmt).first()

    def list_topics(self, skill_id: str | None = None) -> list[Topic]:
        """Fetch all topics with their associated skill, prerequisites and resources."""
        stmt = (
            select(Topic)
            .options(
                joinedload(Topic.skill),
                selectinload(Topic.prerequisites),
                selectinload(Topic.resources),
            )
            .order_by(Topic.order_index, Topic.title)
        )
        if skill_id:
            stmt = stmt.where(Topic.skill_id == skill_id)
        return list(self.db.scalars(stmt).unique().all())

    def get_topic_by_id(self, topic_id: str) -> Topic | None:
        """Fetch a topic by its ID with all relationships eagerly loaded."""
        stmt = (
            select(Topic)
            .options(
                joinedload(Topic.skill),
                selectinload(Topic.resources),
                selectinload(Topic.prerequisites).joinedload(TopicPrerequisite.prerequisite_topic),
                selectinload(Topic.dependent_topics).joinedload(TopicPrerequisite.topic),
            )
            .where(Topic.id == topic_id)
        )
        return self.db.scalars(stmt).unique().first()

    def get_topic_by_slug(self, slug: str) -> Topic | None:
        """Fetch a topic by its URL slug with all relationships eagerly loaded."""
        stmt = (
            select(Topic)
            .options(
                joinedload(Topic.skill),
                selectinload(Topic.resources),
                selectinload(Topic.prerequisites).joinedload(TopicPrerequisite.prerequisite_topic),
                selectinload(Topic.dependent_topics).joinedload(TopicPrerequisite.topic),
            )
            .where(Topic.slug == slug)
        )
        return self.db.scalars(stmt).unique().first()

    def list_all_prerequisites(self) -> list[TopicPrerequisite]:
        """Fetch all topic prerequisite relationships."""
        stmt = select(TopicPrerequisite).order_by(TopicPrerequisite.id)
        return list(self.db.scalars(stmt).all())

    def list_resources_for_topic(self, topic_id: str) -> list[LearningResource]:
        """Fetch curated resources for a topic."""
        stmt = (
            select(LearningResource)
            .where(LearningResource.topic_id == topic_id)
            .order_by(LearningResource.created_at)
        )
        return list(self.db.scalars(stmt).all())
