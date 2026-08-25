"""Database repository for Daily Learning Plans."""

from datetime import date
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.modules.planner.models import DailyLearningPlan


class PlannerRepository:
    """Encapsulates database access for Daily Learning Plans."""

    def __init__(self, db: Session):
        self.db = db

    def create_plan(self, plan: DailyLearningPlan) -> DailyLearningPlan:
        """Persist a new daily learning plan."""
        self.db.add(plan)
        self.db.flush()
        return plan

    def get_plan_by_id(self, plan_id: str) -> Optional[DailyLearningPlan]:
        """Fetch plan by ID."""
        stmt = (
            select(DailyLearningPlan)
            .options(
                joinedload(DailyLearningPlan.selected_topic),
                joinedload(DailyLearningPlan.primary_skill),
                joinedload(DailyLearningPlan.learner),
            )
            .where(DailyLearningPlan.id == plan_id)
        )
        return self.db.scalars(stmt).first()

    def get_plan_by_date(
        self, learner_id: str, plan_date: date
    ) -> Optional[DailyLearningPlan]:
        """Fetch plan for a learner on a specific calendar date."""
        stmt = (
            select(DailyLearningPlan)
            .options(
                joinedload(DailyLearningPlan.selected_topic),
                joinedload(DailyLearningPlan.primary_skill),
                joinedload(DailyLearningPlan.learner),
            )
            .where(
                DailyLearningPlan.learner_id == learner_id,
                DailyLearningPlan.plan_date == plan_date,
            )
        )
        return self.db.scalars(stmt).first()

    def list_learner_plans(
        self, learner_id: str, limit: int = 30
    ) -> List[DailyLearningPlan]:
        """Fetch historical daily learning plans for a learner."""
        stmt = (
            select(DailyLearningPlan)
            .options(
                joinedload(DailyLearningPlan.selected_topic),
                joinedload(DailyLearningPlan.primary_skill),
            )
            .where(DailyLearningPlan.learner_id == learner_id)
            .order_by(desc(DailyLearningPlan.plan_date))
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def delete_plan_by_date(self, learner_id: str, plan_date: date) -> None:
        """Remove plan for a specific date (used during forced regeneration)."""
        existing = self.get_plan_by_date(learner_id, plan_date)
        if existing:
            self.db.delete(existing)
            self.db.flush()

