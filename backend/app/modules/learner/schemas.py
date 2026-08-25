"""Pydantic schemas for Learner profiles, skill states, and skill evidence."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LearnerCreate(BaseModel):
    """Schema for learner onboarding registration."""

    name: str = Field(min_length=1, max_length=150, description="Learner full name")
    email: str = Field(min_length=3, max_length=255, description="Learner email address")
    target_role: str = Field(default="Backend SDE2", description="Target engineering role")
    target_mastery: float = Field(
        default=0.85, ge=0.5, le=1.0, description="Target mastery score (0.5 - 1.0)"
    )
    experience_level: str = Field(
        default="Mid-level SDE", description="Self-reported experience level"
    )


class LearnerRead(BaseModel):
    """Schema for learner profile details."""

    id: str
    name: str
    email: str
    target_role: str
    target_mastery: float
    experience_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillEvidenceRead(BaseModel):
    """Schema for a single piece of evidence proving skill competence."""

    id: str
    learner_id: str
    skill_id: str
    skill_name: str | None = None
    source_type: str
    source_id: str
    score: float
    confidence: float
    weight: float
    evidence_summary: str
    metadata_json: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearnerSkillStateRead(BaseModel):
    """Schema for learner's current competence in a specific skill."""

    skill_id: str
    skill_name: str
    skill_slug: str
    category: str
    mastery_score: float = Field(description="Mastery score between 0.0 and 1.0")
    confidence_score: float = Field(description="Confidence estimate between 0.0 and 1.0")
    evidence_count: int = Field(description="Total evidence points accumulated")
    last_assessed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearnerProfileSummary(BaseModel):
    """Comprehensive learner profile with overall readiness and skill breakdown."""

    learner: LearnerRead
    overall_readiness_percentage: float = Field(
        description="Overall target role readiness score (0.0% to 100.0%)"
    )
    skills: list[LearnerSkillStateRead]
    recent_evidence: list[SkillEvidenceRead] = []
