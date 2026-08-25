"""Create learner and diagnostic tables

Revision ID: 0002_learner_diagnostic
Revises: 0001_create_curriculum_tables
Create Date: 2026-08-25 19:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_learner_diagnostic"
down_revision: Union[str, None] = "0001_create_curriculum_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create learners table
    op.create_table(
        "learners",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("target_role", sa.String(length=100), nullable=False, server_default="Backend SDE2"),
        sa.Column("target_mastery", sa.Float(), nullable=False, server_default="0.85"),
        sa.Column("experience_level", sa.String(length=100), nullable=False, server_default="Mid-level SDE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_learners_email"), "learners", ["email"], unique=True)

    # 2. Create learner_skill_states table
    op.create_table(
        "learner_skill_states",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("learner_id", sa.String(length=50), nullable=False),
        sa.Column("skill_id", sa.String(length=50), nullable=False),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["learner_id"], ["learners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("learner_id", "skill_id", name="uq_learner_skill"),
    )
    op.create_index(op.f("ix_learner_skill_states_learner_id"), "learner_skill_states", ["learner_id"], unique=False)
    op.create_index(op.f("ix_learner_skill_states_skill_id"), "learner_skill_states", ["skill_id"], unique=False)

    # 3. Create skill_evidence table
    op.create_table(
        "skill_evidence",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("learner_id", sa.String(length=50), nullable=False),
        sa.Column("skill_id", sa.String(length=50), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.8"),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("evidence_summary", sa.Text(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["learner_id"], ["learners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skill_evidence_learner_id"), "skill_evidence", ["learner_id"], unique=False)
    op.create_index(op.f("ix_skill_evidence_skill_id"), "skill_evidence", ["skill_id"], unique=False)
    op.create_index(op.f("ix_skill_evidence_source_type"), "skill_evidence", ["source_type"], unique=False)
    op.create_index(op.f("ix_skill_evidence_source_id"), "skill_evidence", ["source_id"], unique=False)

    # 4. Create diagnostic_questions table
    op.create_table(
        "diagnostic_questions",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("skill_id", sa.String(length=50), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=False, server_default="medium"),
        sa.Column("difficulty_weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("options_json", sa.JSON(), nullable=False),
        sa.Column("correct_option_id", sa.String(length=10), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diagnostic_questions_skill_id"), "diagnostic_questions", ["skill_id"], unique=False)

    # 5. Create diagnostic_attempts table
    op.create_table(
        "diagnostic_attempts",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("learner_id", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="in_progress"),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["learner_id"], ["learners.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diagnostic_attempts_learner_id"), "diagnostic_attempts", ["learner_id"], unique=False)
    op.create_index(op.f("ix_diagnostic_attempts_status"), "diagnostic_attempts", ["status"], unique=False)

    # 6. Create diagnostic_answers table
    op.create_table(
        "diagnostic_answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("attempt_id", sa.String(length=50), nullable=False),
        sa.Column("question_id", sa.String(length=50), nullable=False),
        sa.Column("selected_option_id", sa.String(length=10), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["attempt_id"], ["diagnostic_attempts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["diagnostic_questions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diagnostic_answers_attempt_id"), "diagnostic_answers", ["attempt_id"], unique=False)
    op.create_index(op.f("ix_diagnostic_answers_question_id"), "diagnostic_answers", ["question_id"], unique=False)


def downgrade() -> None:
    op.drop_table("diagnostic_answers")
    op.drop_table("diagnostic_attempts")
    op.drop_table("diagnostic_questions")
    op.drop_table("skill_evidence")
    op.drop_table("learner_skill_states")
    op.drop_table("learners")

