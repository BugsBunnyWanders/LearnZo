"""Pydantic schemas for Daily Learning Plans, candidate evaluations, and breakdown audits."""

from datetime import date, datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class CandidateUnmetPrerequisite(BaseModel):
    """Details of a prerequisite preventing a topic from being eligible."""

    prerequisite_topic_id: str
    title: str
    required_mastery: float
    current_mastery: float


class EligibleTopicCandidate(BaseModel):
    """Candidate topic evaluated by the daily planner ranking engine."""

    topic_id: str
    slug: str
    title: str
    skill_id: str
    skill_name: str
    category: str
    importance_weight: float
    current_mastery: float
    target_mastery: float
    skill_gap: float
    confidence_score: float
    priority_score: float
    is_eligible: bool
    unmet_prerequisites: List[CandidateUnmetPrerequisite] = []


class DailyPlanRead(BaseModel):
    """Schema for a persisted Daily Learning Plan."""

    id: str
    learner_id: str
    plan_date: date
    selected_topic_id: str
    topic_title: str
    topic_slug: str
    skill_id: str
    skill_name: str
    current_mastery_score: float = Field(
        description="Mastery score of the primary skill when the plan was created"
    )
    target_mastery_score: float = Field(
        description="Target mastery threshold for the topic"
    )
    skill_gap: float = Field(
        description="Gap between target mastery and current learner mastery"
    )
    priority_score: float = Field(
        description="Calculated ranking priority score"
    )
    reason_code: str = Field(
        description="Categorical reason code (e.g. 'HIGH_VALUE_GAP', 'FOUNDATIONAL_START')"
    )
    reason_summary: str = Field(
        description="Personalized human-readable explanation of why this topic was selected today"
    )
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlannerBreakdownResponse(BaseModel):
    """Full ranking breakdown response for transparency and auditability."""

    plan: DailyPlanRead
    eligible_candidates: List[EligibleTopicCandidate]
    locked_candidates: List[EligibleTopicCandidate]
    total_curriculum_topics: int

