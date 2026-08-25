"""Pydantic schemas for Diagnostic assessments, question presentation, and submission results."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DiagnosticOptionPublic(BaseModel):
    """Multiple choice option presented to the learner."""

    id: str = Field(description="Option letter identifier (e.g. 'A', 'B', 'C', 'D')")
    text: str = Field(description="Option text description")


class DiagnosticQuestionPublic(BaseModel):
    """Sanitized diagnostic question without answers or explanations."""

    id: str
    skill_id: str
    skill_name: str
    question_text: str
    difficulty: str
    options: List[DiagnosticOptionPublic]
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class DiagnosticAttemptStart(BaseModel):
    """Payload to initiate a new diagnostic assessment attempt."""

    learner_id: str = Field(description="ID of the learner taking the diagnostic")


class DiagnosticAttemptRead(BaseModel):
    """Schema for a diagnostic assessment attempt state."""

    id: str
    learner_id: str
    status: str
    total_questions: int
    correct_count: int
    score_percentage: float
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DiagnosticAnswerSubmit(BaseModel):
    """Answer choice for a single question."""

    question_id: str = Field(description="ID of the diagnostic question being answered")
    selected_option_id: str = Field(
        description="Option letter chosen by learner ('A', 'B', 'C', or 'D')"
    )


class DiagnosticSubmissionPayload(BaseModel):
    """Payload containing all submitted question answers for an attempt."""

    answers: List[DiagnosticAnswerSubmit] = Field(
        min_length=1, description="List of question answers"
    )


class QuestionAnswerResult(BaseModel):
    """Detailed evaluation result for an individual answered question."""

    question_id: str
    skill_id: str
    question_text: str
    selected_option_id: str
    correct_option_id: str
    is_correct: bool
    explanation: str


class SkillScoreBreakdown(BaseModel):
    """Summary of diagnostic performance and resulting mastery update for a skill."""

    skill_id: str
    skill_name: str
    category: str
    total_questions: int
    correct_questions: int
    score_percentage: float
    updated_mastery_score: float
    updated_confidence_score: float
    evidence_summary: str


class DiagnosticResultResponse(BaseModel):
    """Comprehensive result returned upon completing a diagnostic attempt."""

    attempt: DiagnosticAttemptRead
    overall_score_percentage: float
    total_questions: int
    correct_count: int
    skill_breakdown: List[SkillScoreBreakdown]
    detailed_answers: List[QuestionAnswerResult]


class DiagnosticSeedResponse(BaseModel):
    """Response returned after seeding diagnostic questions."""

    message: str
    questions_seeded: int

