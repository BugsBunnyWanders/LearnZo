"""Create curriculum tables (skills, topics, topic_prerequisites, learning_resources)

Revision ID: 0001_create_curriculum_tables
Revises:
Create Date: 2026-08-25 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_create_curriculum_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create skills table
    op.create_table(
        "skills",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "category", sa.String(length=100), nullable=False, server_default="Backend Engineering"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skills_slug"), "skills", ["slug"], unique=True)

    # 2. Create topics table
    op.create_table(
        "topics",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("skill_id", sa.String(length=50), nullable=False),
        sa.Column("target_mastery", sa.Float(), nullable=False, server_default="0.80"),
        sa.Column("importance_weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topics_slug"), "topics", ["slug"], unique=True)
    op.create_index(op.f("ix_topics_skill_id"), "topics", ["skill_id"], unique=False)

    # 3. Create topic_prerequisites table
    op.create_table(
        "topic_prerequisites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topic_id", sa.String(length=50), nullable=False),
        sa.Column("prerequisite_topic_id", sa.String(length=50), nullable=False),
        sa.Column("min_mastery_required", sa.Float(), nullable=False, server_default="0.70"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["prerequisite_topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("topic_id", "prerequisite_topic_id", name="uq_topic_prerequisite"),
    )
    op.create_index(
        op.f("ix_topic_prerequisites_topic_id"), "topic_prerequisites", ["topic_id"], unique=False
    )
    op.create_index(
        op.f("ix_topic_prerequisites_prerequisite_topic_id"),
        "topic_prerequisites",
        ["prerequisite_topic_id"],
        unique=False,
    )

    # 4. Create learning_resources table
    op.create_table(
        "learning_resources",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("topic_id", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False, server_default="youtube"),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("author", sa.String(length=150), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "transcript_status", sa.String(length=50), nullable=False, server_default="available"
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_learning_resources_topic_id"), "learning_resources", ["topic_id"], unique=False
    )


def downgrade() -> None:
    op.drop_table("learning_resources")
    op.drop_table("topic_prerequisites")
    op.drop_table("topics")
    op.drop_table("skills")
