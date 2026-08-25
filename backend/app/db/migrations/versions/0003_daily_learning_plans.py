"""Create daily_learning_plans table

Revision ID: 0003_daily_learning_plans
Revises: 0002_learner_diagnostic
Create Date: 2026-08-25 19:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_daily_learning_plans"
down_revision: Union[str, None] = "0002_learner_diagnostic"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_learning_plans",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("learner_id", sa.String(length=50), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("selected_topic_id", sa.String(length=50), nullable=False),
        sa.Column("primary_skill_id", sa.String(length=50), nullable=False),
        sa.Column("current_mastery_score", sa.Float(), nullable=False),
        sa.Column("target_mastery_score", sa.Float(), nullable=False),
        sa.Column("skill_gap", sa.Float(), nullable=False),
        sa.Column("priority_score", sa.Float(), nullable=False),
        sa.Column("reason_code", sa.String(length=50), nullable=False, server_default="HIGH_VALUE_GAP"),
        sa.Column("reason_summary", sa.Text(), nullable=False),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["learner_id"], ["learners.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["selected_topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["primary_skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_daily_learning_plans_learner_id"), "daily_learning_plans", ["learner_id"], unique=False)
    op.create_index(op.f("ix_daily_learning_plans_plan_date"), "daily_learning_plans", ["plan_date"], unique=False)
    op.create_index(op.f("ix_daily_learning_plans_selected_topic_id"), "daily_learning_plans", ["selected_topic_id"], unique=False)
    op.create_index(op.f("ix_daily_learning_plans_primary_skill_id"), "daily_learning_plans", ["primary_skill_id"], unique=False)


def downgrade() -> None:
    op.drop_table("daily_learning_plans")

