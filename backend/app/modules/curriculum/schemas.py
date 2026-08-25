"""Pydantic schemas for Curriculum and Skill Graph domain."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SkillBase(BaseModel):
    """Base schema for a skill."""

    id: str = Field(description="Unique skill identifier key (e.g. 'database_indexing')")
    slug: str = Field(description="URL-friendly slug (e.g. 'database-indexing')")
    name: str = Field(description="Display name of the skill")
    description: str = Field(description="Detailed description of the skill competency")
    category: str = Field(default="Backend Engineering", description="Skill category grouping")


class SkillRead(SkillBase):
    """Schema for skill read operations."""

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillSummary(BaseModel):
    """Condensed skill information for embedding in topic responses."""

    id: str
    slug: str
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class LearningResourceRead(BaseModel):
    """Schema for a curated learning resource attached to a topic."""

    id: str
    topic_id: str
    resource_type: str = Field(description="Resource type (e.g. 'youtube', 'article')")
    title: str
    url: str
    author: str | None = None
    duration_seconds: int | None = None
    transcript_status: str
    summary: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PrerequisiteSummary(BaseModel):
    """Summary of a prerequisite topic requirement."""

    prerequisite_topic_id: str
    slug: str
    title: str
    min_mastery_required: float

    model_config = ConfigDict(from_attributes=True)


class DependentTopicSummary(BaseModel):
    """Summary of a topic that depends on this topic."""

    topic_id: str
    slug: str
    title: str
    min_mastery_required: float

    model_config = ConfigDict(from_attributes=True)


class TopicSummary(BaseModel):
    """Condensed topic schema for list responses."""

    id: str
    slug: str
    title: str
    description: str
    skill_id: str
    skill_name: str | None = None
    target_mastery: float
    importance_weight: float
    order_index: int
    prerequisite_count: int = 0
    resource_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TopicDetail(BaseModel):
    """Comprehensive topic schema including resources and prerequisite graph connections."""

    id: str
    slug: str
    title: str
    description: str
    skill: SkillSummary
    target_mastery: float
    importance_weight: float
    order_index: int
    resources: list[LearningResourceRead] = []
    prerequisites: list[PrerequisiteSummary] = []
    dependent_topics: list[DependentTopicSummary] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurriculumGraphNode(BaseModel):
    """Graph node representing a curriculum topic."""

    id: str
    slug: str
    title: str
    skill_id: str
    skill_name: str
    category: str
    importance_weight: float
    target_mastery: float
    order_index: int


class CurriculumGraphEdge(BaseModel):
    """Directed edge representing a prerequisite dependency (source -> target)."""

    source: str = Field(description="Prerequisite topic ID (source of the dependency)")
    target: str = Field(description="Dependent topic ID (target requiring the prerequisite)")
    min_mastery_required: float


class CurriculumGraphResponse(BaseModel):
    """Full curriculum graph structure for DAG visualization and planning."""

    skills: list[SkillRead]
    nodes: list[CurriculumGraphNode]
    edges: list[CurriculumGraphEdge]


class SeedResponse(BaseModel):
    """Response returned after running curriculum seeding."""

    message: str
    skills_seeded: int
    topics_seeded: int
    prerequisites_seeded: int
    resources_seeded: int
