"""Curriculum API routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.curriculum.schemas import (
    CurriculumGraphResponse,
    SeedResponse,
    SkillRead,
    TopicDetail,
    TopicSummary,
)
from app.modules.curriculum.service import CurriculumService

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])


@router.get(
    "/skills",
    response_model=list[SkillRead],
    summary="List Skills",
    description="Retrieve all competency skill dimensions defined in the curriculum.",
)
def list_skills(db: Session = Depends(get_db)) -> list[SkillRead]:
    """List all curriculum skills."""
    service = CurriculumService(db)
    return service.list_skills()


@router.get(
    "/topics",
    response_model=list[TopicSummary],
    summary="List Topics",
    description="Retrieve all learning topics with prerequisite and resource counts, optionally filtered by skill.",
)
def list_topics(
    skill_id: str | None = Query(default=None, description="Optional skill ID filter"),
    db: Session = Depends(get_db),
) -> list[TopicSummary]:
    """List all topics."""
    service = CurriculumService(db)
    return service.list_topics(skill_id=skill_id)


@router.get(
    "/topics/{topic_id_or_slug}",
    response_model=TopicDetail,
    summary="Get Topic Detail",
    description="Retrieve full details for a topic including curated learning resources and prerequisite relationships.",
)
def get_topic(
    topic_id_or_slug: str,
    db: Session = Depends(get_db),
) -> TopicDetail:
    """Get single topic by ID or slug."""
    service = CurriculumService(db)
    return service.get_topic_by_id_or_slug(topic_id_or_slug)


@router.get(
    "/graph",
    response_model=CurriculumGraphResponse,
    summary="Get Curriculum Graph",
    description="Retrieve the complete DAG structure of skills, topics (nodes), and prerequisite dependencies (directed edges).",
)
def get_curriculum_graph(db: Session = Depends(get_db)) -> CurriculumGraphResponse:
    """Get entire curriculum graph."""
    service = CurriculumService(db)
    return service.get_curriculum_graph()


@router.post(
    "/seed",
    response_model=SeedResponse,
    status_code=status.HTTP_200_OK,
    summary="Seed Curriculum",
    description="Seed default Backend SDE2 curriculum data into the database.",
)
def seed_curriculum(
    force: bool = Query(default=False, description="Force re-seeding even if data exists"),
    db: Session = Depends(get_db),
) -> SeedResponse:
    """Seed curriculum data."""
    service = CurriculumService(db)
    return service.seed_curriculum(force=force)
