"""Deterministic learning planner engine: prerequisite DAG resolution and ranking algorithms."""


from app.modules.curriculum.models import Topic
from app.modules.learner.models import LearnerSkillState
from app.modules.planner.schemas import (
    CandidateUnmetPrerequisite,
    EligibleTopicCandidate,
)


class PlannerEngine:
    """Deterministic orchestration engine for topic eligibility evaluation and priority ranking."""

    @staticmethod
    def evaluate_candidates(
        topics: list[Topic],
        skill_states: dict[str, LearnerSkillState],
    ) -> tuple[list[EligibleTopicCandidate], list[EligibleTopicCandidate]]:
        """Evaluate all curriculum topics for eligibility and calculate priority scores.

        Returns:
            Tuple of (eligible_candidates_sorted, locked_candidates)
        """
        eligible: list[EligibleTopicCandidate] = []
        locked: list[EligibleTopicCandidate] = []

        # Index skill states for instant lookup
        # skill_id -> LearnerSkillState
        states_map = {st.skill_id: st for st in skill_states.values()}

        for topic in topics:
            # 1. Prerequisite verification
            unmet: list[CandidateUnmetPrerequisite] = []
            for prereq_edge in topic.prerequisites:
                prereq_topic = prereq_edge.prerequisite_topic
                if not prereq_topic:
                    continue

                prereq_skill_state = states_map.get(prereq_topic.skill_id)
                prereq_mastery = (
                    prereq_skill_state.mastery_score if prereq_skill_state else 0.0
                )

                if prereq_mastery < prereq_edge.min_mastery_required:
                    unmet.append(
                        CandidateUnmetPrerequisite(
                            prerequisite_topic_id=prereq_topic.id,
                            title=prereq_topic.title,
                            required_mastery=prereq_edge.min_mastery_required,
                            current_mastery=round(prereq_mastery, 3),
                        )
                    )

            is_eligible = len(unmet) == 0

            # 2. Score calculation
            skill_state = states_map.get(topic.skill_id)
            current_mastery = skill_state.mastery_score if skill_state else 0.0
            confidence = skill_state.confidence_score if skill_state else 0.0

            # Skill gap: positive difference between target and current mastery
            skill_gap = max(0.02, topic.target_mastery - current_mastery)

            # Confidence factor: lower confidence adds exploration boost (1.0 to 1.35)
            confidence_factor = 1.0 + (0.35 * (1.0 - confidence))

            # Priority score formula: gap * importance * confidence_factor
            priority_score = round(
                skill_gap * topic.importance_weight * confidence_factor, 3
            )

            candidate = EligibleTopicCandidate(
                topic_id=topic.id,
                slug=topic.slug,
                title=topic.title,
                skill_id=topic.skill_id,
                skill_name=topic.skill.name if topic.skill else topic.skill_id,
                category=topic.skill.category if topic.skill else "General",
                importance_weight=topic.importance_weight,
                current_mastery=round(current_mastery, 3),
                target_mastery=topic.target_mastery,
                skill_gap=round(skill_gap, 3),
                confidence_score=round(confidence, 3),
                priority_score=priority_score,
                is_eligible=is_eligible,
                unmet_prerequisites=unmet,
            )

            if is_eligible:
                eligible.append(candidate)
            else:
                locked.append(candidate)

        # Sort eligible candidates: highest priority score first, then order_index
        eligible.sort(
            key=lambda c: (
                -c.priority_score,
                # Find matching topic order_index as secondary tiebreaker
                next((t.order_index for t in topics if t.id == c.topic_id), 0),
            )
        )

        return eligible, locked

    @staticmethod
    def generate_explanation(
        selected: EligibleTopicCandidate,
        all_eligible: list[EligibleTopicCandidate],
        skill_states: dict[str, LearnerSkillState],
        target_role: str,
    ) -> tuple[str, str]:
        """Generate deterministic reason code and human-readable explanation."""
        current_pct = round(selected.current_mastery * 100.0)
        target_pct = round(selected.target_mastery * 100.0)
        gap_pct = round(selected.skill_gap * 100.0)

        # Determine Reason Code
        total_evidence_across_skills = sum(
            st.evidence_count for st in skill_states.values()
        )

        if total_evidence_across_skills == 0:
            reason_code = "FOUNDATIONAL_START"
            reason_summary = (
                f"Today's Focus: {selected.title}. "
                f"As a new learner targeting {target_role}, starting with foundational query execution "
                f"will establish the baseline competency required to unlock advanced database and distributed topics."
            )
        elif selected.skill_gap >= 0.25 and selected.importance_weight >= 4.5:
            reason_code = "HIGH_VALUE_GAP"
            reason_summary = (
                f"Today's Focus: {selected.title}. "
                f"Your diagnostic indicated a current mastery of {current_pct}% ({gap_pct}% gap from target {target_pct}%). "
                f"{selected.skill_name} carries a high importance weighting ({selected.importance_weight:.1f}/5.0) for {target_role} readiness, "
                f"and all foundational prerequisites are satisfied."
            )
        elif selected.current_mastery < selected.target_mastery:
            reason_code = "PREREQUISITES_SATISFIED"
            reason_summary = (
                f"Today's Focus: {selected.title}. "
                f"You have satisfied the prerequisites for this topic. "
                f"Studying {selected.title} will bridge your {gap_pct}% skill gap in {selected.skill_name}."
            )
        else:
            reason_code = "MASTERY_REINFORCEMENT"
            reason_summary = (
                f"Today's Focus: {selected.title}. "
                f"You have reached initial target mastery ({current_pct}%), but reinforcing {selected.title} "
                f"will increase estimation confidence and prepare you for subsequent engineering assignments."
            )

        return reason_code, reason_summary
