"""Curriculum domain service for business operations and graph resolution."""

import logging

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.modules.curriculum.models import (
    LearningResource,
    Skill,
    Topic,
    TopicPrerequisite,
)
from app.modules.curriculum.repository import CurriculumRepository
from app.modules.curriculum.schemas import (
    CurriculumGraphEdge,
    CurriculumGraphNode,
    CurriculumGraphResponse,
    DependentTopicSummary,
    LearningResourceRead,
    PrerequisiteSummary,
    SeedResponse,
    SkillRead,
    SkillSummary,
    TopicDetail,
    TopicSummary,
)
from app.modules.curriculum.seed_data import SEEDED_SKILLS, SEEDED_TOPICS

logger = logging.getLogger(__name__)


class CurriculumService:
    """Service handling curriculum business logic, graph construction, and seed management."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = CurriculumRepository(db)

    def list_skills(self) -> list[SkillRead]:
        """Fetch list of all available skill entities."""
        skills = self.repo.list_skills()
        return [SkillRead.model_validate(s) for s in skills]

    def list_topics(self, skill_id: str | None = None) -> list[TopicSummary]:
        """Fetch list of topics formatted as summaries with relationship counts."""
        topics = self.repo.list_topics(skill_id=skill_id)
        results = []
        for t in topics:
            results.append(
                TopicSummary(
                    id=t.id,
                    slug=t.slug,
                    title=t.title,
                    description=t.description,
                    skill_id=t.skill_id,
                    skill_name=t.skill.name if t.skill else None,
                    target_mastery=t.target_mastery,
                    importance_weight=t.importance_weight,
                    order_index=t.order_index,
                    prerequisite_count=len(t.prerequisites),
                    resource_count=len(t.resources),
                )
            )
        return results

    def get_topic_by_id_or_slug(self, identifier: str) -> TopicDetail:
        """Fetch complete topic details by ID or slug."""
        topic = self.repo.get_topic_by_id(identifier) or self.repo.get_topic_by_slug(identifier)
        if not topic:
            raise EntityNotFoundException("Topic", identifier)

        # Map prerequisites
        prereqs: list[PrerequisiteSummary] = []
        for p in topic.prerequisites:
            if p.prerequisite_topic:
                prereqs.append(
                    PrerequisiteSummary(
                        prerequisite_topic_id=p.prerequisite_topic_id,
                        slug=p.prerequisite_topic.slug,
                        title=p.prerequisite_topic.title,
                        min_mastery_required=p.min_mastery_required,
                    )
                )

        # Map dependent topics
        dependents: list[DependentTopicSummary] = []
        for d in topic.dependent_topics:
            if d.topic:
                dependents.append(
                    DependentTopicSummary(
                        topic_id=d.topic_id,
                        slug=d.topic.slug,
                        title=d.topic.title,
                        min_mastery_required=d.min_mastery_required,
                    )
                )

        # Map resources
        resources = [LearningResourceRead.model_validate(r) for r in topic.resources]

        return TopicDetail(
            id=topic.id,
            slug=topic.slug,
            title=topic.title,
            description=topic.description,
            skill=SkillSummary.model_validate(topic.skill),
            target_mastery=topic.target_mastery,
            importance_weight=topic.importance_weight,
            order_index=topic.order_index,
            resources=resources,
            prerequisites=prereqs,
            dependent_topics=dependents,
            created_at=topic.created_at,
            updated_at=topic.updated_at,
        )

    def get_curriculum_graph(self) -> CurriculumGraphResponse:
        """Construct full DAG graph response with nodes, edges, and skills."""
        skills = self.list_skills()
        topics = self.repo.list_topics()
        prerequisites = self.repo.list_all_prerequisites()

        nodes: list[CurriculumGraphNode] = []
        for t in topics:
            nodes.append(
                CurriculumGraphNode(
                    id=t.id,
                    slug=t.slug,
                    title=t.title,
                    skill_id=t.skill_id,
                    skill_name=t.skill.name if t.skill else "",
                    category=t.skill.category if t.skill else "General",
                    importance_weight=t.importance_weight,
                    target_mastery=t.target_mastery,
                    order_index=t.order_index,
                )
            )

        edges: list[CurriculumGraphEdge] = []
        for p in prerequisites:
            edges.append(
                CurriculumGraphEdge(
                    source=p.prerequisite_topic_id,
                    target=p.topic_id,
                    min_mastery_required=p.min_mastery_required,
                )
            )

        return CurriculumGraphResponse(
            skills=skills,
            nodes=nodes,
            edges=edges,
        )

    def seed_curriculum(self, force: bool = False) -> SeedResponse:
        """Seed default skills, topics, prerequisites, and learning resources into database."""
        skills_count = self.repo.count_skills()
        topics_count = self.repo.count_topics()

        if skills_count > 0 and topics_count > 0 and not force:
            logger.info(
                "Curriculum data already populated (%d skills, %d topics). Skipping.",
                skills_count,
                topics_count,
            )
            return SeedResponse(
                message="Curriculum already populated. Use force=True to re-seed.",
                skills_seeded=skills_count,
                topics_seeded=topics_count,
                prerequisites_seeded=len(self.repo.list_all_prerequisites()),
                resources_seeded=self.db.query(LearningResource).count(),
            )

        logger.info("Seeding curriculum data...")

        # 1. Seed Skills
        skills_seeded = 0
        for skill_data in SEEDED_SKILLS:
            existing = self.repo.get_skill_by_id(skill_data["id"])
            if not existing:
                skill = Skill(
                    id=skill_data["id"],
                    slug=skill_data["slug"],
                    name=skill_data["name"],
                    description=skill_data["description"],
                    category=skill_data["category"],
                )
                self.db.add(skill)
                skills_seeded += 1
        self.db.flush()

        # 2. Seed Topics & Resources
        topics_seeded = 0
        resources_seeded = 0
        for topic_data in SEEDED_TOPICS:
            existing_topic = self.repo.get_topic_by_id(topic_data["id"])
            if not existing_topic:
                topic = Topic(
                    id=topic_data["id"],
                    slug=topic_data["slug"],
                    title=topic_data["title"],
                    description=topic_data["description"],
                    skill_id=topic_data["skill_id"],
                    target_mastery=topic_data["target_mastery"],
                    importance_weight=topic_data["importance_weight"],
                    order_index=topic_data["order_index"],
                )
                self.db.add(topic)
                topics_seeded += 1
                self.db.flush()

                # Add resource
                res_data = topic_data.get("resource")
                if res_data:
                    res = LearningResource(
                        id=res_data["id"],
                        topic_id=topic.id,
                        resource_type=res_data["resource_type"],
                        title=res_data["title"],
                        url=res_data["url"],
                        author=res_data.get("author"),
                        duration_seconds=res_data.get("duration_seconds"),
                        transcript_status=res_data.get("transcript_status", "available"),
                        summary=res_data.get("summary"),
                        metadata_json=res_data.get("metadata_json"),
                    )
                    self.db.add(res)
                    resources_seeded += 1
        self.db.flush()

        # 3. Seed Prerequisites
        prerequisites_seeded = 0
        for topic_data in SEEDED_TOPICS:
            topic_id = topic_data["id"]
            for prereq_id in topic_data.get("prerequisites", []):
                existing_prereq = (
                    self.db.query(TopicPrerequisite)
                    .filter_by(topic_id=topic_id, prerequisite_topic_id=prereq_id)
                    .first()
                )
                if not existing_prereq:
                    prereq = TopicPrerequisite(
                        topic_id=topic_id,
                        prerequisite_topic_id=prereq_id,
                        min_mastery_required=0.70,
                    )
                    self.db.add(prereq)
                    prerequisites_seeded += 1

        self.db.commit()
        logger.info(
            "Seeding complete: %d skills, %d topics, %d prerequisites, %d resources.",
            skills_seeded,
            topics_seeded,
            prerequisites_seeded,
            resources_seeded,
        )

        return SeedResponse(
            message="Curriculum seeded successfully.",
            skills_seeded=self.repo.count_skills(),
            topics_seeded=self.repo.count_topics(),
            prerequisites_seeded=len(self.repo.list_all_prerequisites()),
            resources_seeded=self.db.query(LearningResource).count(),
        )

    def seed_if_empty(self) -> bool:
        """Helper to seed on startup if database has no topics."""
        try:
            if self.repo.count_topics() == 0:
                logger.info("Curriculum is empty on startup. Triggering auto-seed.")
                self.seed_curriculum(force=False)
                return True
        except Exception as exc:
            logger.warning(
                "Curriculum auto-seed check skipped/failed (likely table not created yet): %s", exc
            )
        return False
