"""Planner service orchestrating daily learning plans and curriculum ranking."""

import logging
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException, LearnZoException
from app.modules.curriculum.repository import CurriculumRepository
from app.modules.learner.repository import LearnerRepository
from app.modules.planner.engine import PlannerEngine
from app.modules.planner.models import DailyLearningPlan
from app.modules.planner.repository import PlannerRepository
from app.modules.planner.schemas import (
    DailyPlanRead,
    PlannerBreakdownResponse,
)

logger = logging.getLogger(__name__)


class PlannerService:
    """Service managing daily learning plan generation, persistence, and audit analysis."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = PlannerRepository(db)
        self.learner_repo = LearnerRepository(db)
        self.curriculum_repo = CurriculumRepository(db)

    def _map_plan_to_read(self, plan: DailyLearningPlan) -> DailyPlanRead:
        """Map DailyLearningPlan model to DailyPlanRead Pydantic schema."""
        return DailyPlanRead(
            id=plan.id,
            learner_id=plan.learner_id,
            plan_date=plan.plan_date,
            selected_topic_id=plan.selected_topic_id,
            topic_title=plan.selected_topic.title if plan.selected_topic else plan.selected_topic_id,
            topic_slug=plan.selected_topic.slug if plan.selected_topic else plan.selected_topic_id,
            skill_id=plan.primary_skill_id,
            skill_name=plan.primary_skill.name if plan.primary_skill else plan.primary_skill_id,
            current_mastery_score=round(plan.current_mastery_score, 3),
            target_mastery_score=round(plan.target_mastery_score, 3),
            skill_gap=round(plan.skill_gap, 3),
            priority_score=round(plan.priority_score, 3),
            reason_code=plan.reason_code,
            reason_summary=plan.reason_summary,
            is_completed=plan.is_completed,
            created_at=plan.created_at,
        )

    def get_or_create_daily_plan(
        self,
        learner_id: str,
        plan_date: Optional[date] = None,
        force_regenerate: bool = False,
    ) -> DailyPlanRead:
        """Retrieve existing daily plan for the date, or dynamically compute and persist one."""
        target_date = plan_date or date.today()

        learner = self.learner_repo.get_learner_by_id(learner_id)
        if not learner:
            raise EntityNotFoundException("Learner", learner_id)

        # Check for existing plan on this date
        existing_plan = self.repo.get_plan_by_date(learner_id, target_date)
        if existing_plan and not force_regenerate:
            return self._map_plan_to_read(existing_plan)

        if existing_plan and force_regenerate:
            self.repo.delete_plan_by_date(learner_id, target_date)

        # Fetch topics and learner skill states
        topics = self.curriculum_repo.list_topics()
        if not topics:
            raise LearnZoException("No curriculum topics available to plan.")

        skill_states_list = self.learner_repo.list_skill_states(learner_id)
        skill_states = {st.skill_id: st for st in skill_states_list}

        # Run deterministic candidate evaluation
        eligible, locked = PlannerEngine.evaluate_candidates(topics, skill_states)

        if not eligible:
            # Fallback to the first topic in curriculum if everything is somehow locked
            logger.warning("No eligible topics found for learner %s. Falling back to root topic.", learner_id)
            top_candidate = locked[0]
        else:
            top_candidate = eligible[0]

        # Generate structured explanation
        reason_code, reason_summary = PlannerEngine.generate_explanation(
            selected=top_candidate,
            all_eligible=eligible,
            skill_states=skill_states,
            target_role=learner.target_role,
        )

        # Persist DailyLearningPlan
        plan = DailyLearningPlan(
            learner_id=learner_id,
            plan_date=target_date,
            selected_topic_id=top_candidate.topic_id,
            primary_skill_id=top_candidate.skill_id,
            current_mastery_score=top_candidate.current_mastery,
            target_mastery_score=top_candidate.target_mastery,
            skill_gap=top_candidate.skill_gap,
            priority_score=top_candidate.priority_score,
            reason_code=reason_code,
            reason_summary=reason_summary,
            is_completed=False,
        )
        self.repo.create_plan(plan)
        self.db.commit()

        # Reload with joined relationships
        fresh_plan = self.repo.get_plan_by_id(plan.id)
        logger.info(
            "Created daily plan for learner %s on %s: Topic='%s', Priority=%.3f, Reason=%s",
            learner_id,
            target_date,
            fresh_plan.selected_topic.title if fresh_plan.selected_topic else fresh_plan.selected_topic_id,
            fresh_plan.priority_score,
            fresh_plan.reason_code,
        )
        return self._map_plan_to_read(fresh_plan)

    def get_planner_analysis(self, learner_id: str) -> PlannerBreakdownResponse:
        """Return the current plan alongside full candidate eligibility and ranking audit."""
        plan_read = self.get_or_create_daily_plan(learner_id, force_regenerate=False)

        topics = self.curriculum_repo.list_topics()
        skill_states_list = self.learner_repo.list_skill_states(learner_id)
        skill_states = {st.skill_id: st for st in skill_states_list}

        eligible, locked = PlannerEngine.evaluate_candidates(topics, skill_states)

        return PlannerBreakdownResponse(
            plan=plan_read,
            eligible_candidates=eligible,
            locked_candidates=locked,
            total_curriculum_topics=len(topics),
        )

