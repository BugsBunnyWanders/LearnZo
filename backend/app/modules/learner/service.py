"""Learner domain service managing profile creation, evidence recording, and mastery calculations."""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException
from app.modules.curriculum.repository import CurriculumRepository
from app.modules.learner.models import Learner, LearnerSkillState, SkillEvidence
from app.modules.learner.repository import LearnerRepository
from app.modules.learner.schemas import (
    LearnerCreate,
    LearnerProfileSummary,
    LearnerRead,
    LearnerSkillStateRead,
    SkillEvidenceRead,
)

logger = logging.getLogger(__name__)


class LearnerService:
    """Service encapsulating learner lifecycle and evidence-backed mastery calculations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = LearnerRepository(db)
        self.curriculum_repo = CurriculumRepository(db)

    def onboard_learner(self, data: LearnerCreate) -> LearnerProfileSummary:
        """Create a new learner profile and initialize skill states for all curriculum skills."""
        existing = self.repo.get_learner_by_email(data.email)
        if existing:
            return self.get_learner_profile(existing.id)

        learner = Learner(
            name=data.name,
            email=data.email,
            target_role=data.target_role,
            target_mastery=data.target_mastery,
            experience_level=data.experience_level,
        )
        self.repo.create_learner(learner)

        # Initialize skill states for all known skills
        all_skills = self.curriculum_repo.list_skills()
        for skill in all_skills:
            state = LearnerSkillState(
                learner_id=learner.id,
                skill_id=skill.id,
                mastery_score=0.0,
                confidence_score=0.0,
                evidence_count=0,
                last_assessed_at=datetime.now(UTC),
            )
            self.db.add(state)

        self.db.commit()
        logger.info("Onboarded new learner '%s' (ID: %s)", learner.name, learner.id)
        return self.get_learner_profile(learner.id)

    def get_learner_profile(self, learner_id: str) -> LearnerProfileSummary:
        """Fetch comprehensive learner profile with readiness calculation."""
        learner = self.repo.get_learner_by_id(learner_id)
        if not learner:
            raise EntityNotFoundException("Learner", learner_id)

        skill_states = self.repo.list_skill_states(learner_id)
        skills_read: list[LearnerSkillStateRead] = []

        total_mastery = 0.0
        for st in skill_states:
            skills_read.append(
                LearnerSkillStateRead(
                    skill_id=st.skill_id,
                    skill_name=st.skill.name if st.skill else st.skill_id,
                    skill_slug=st.skill.slug if st.skill else st.skill_id,
                    category=st.skill.category if st.skill else "General",
                    mastery_score=round(st.mastery_score, 3),
                    confidence_score=round(st.confidence_score, 3),
                    evidence_count=st.evidence_count,
                    last_assessed_at=st.last_assessed_at,
                )
            )
            total_mastery += st.mastery_score

        # Calculate overall role readiness: average mastery normalized by target mastery
        num_skills = max(len(skills_read), 1)
        avg_mastery = total_mastery / num_skills
        readiness = round(min(100.0, (avg_mastery / max(learner.target_mastery, 0.5)) * 100.0), 1)

        recent_evidence = self.get_learner_evidence_history(learner_id, limit=10)

        return LearnerProfileSummary(
            learner=LearnerRead.model_validate(learner),
            overall_readiness_percentage=readiness,
            skills=skills_read,
            recent_evidence=recent_evidence,
        )

    def get_learner_skill_states(self, learner_id: str) -> list[LearnerSkillStateRead]:
        """Fetch skill states for a learner."""
        learner = self.repo.get_learner_by_id(learner_id)
        if not learner:
            raise EntityNotFoundException("Learner", learner_id)

        states = self.repo.list_skill_states(learner_id)
        return [
            LearnerSkillStateRead(
                skill_id=st.skill_id,
                skill_name=st.skill.name if st.skill else st.skill_id,
                skill_slug=st.skill.slug if st.skill else st.skill_id,
                category=st.skill.category if st.skill else "General",
                mastery_score=round(st.mastery_score, 3),
                confidence_score=round(st.confidence_score, 3),
                evidence_count=st.evidence_count,
                last_assessed_at=st.last_assessed_at,
            )
            for st in states
        ]

    def get_learner_evidence_history(
        self,
        learner_id: str,
        skill_id: str | None = None,
        limit: int = 50,
    ) -> list[SkillEvidenceRead]:
        """Fetch evidence history for a learner."""
        evidence_list = self.repo.list_evidence(
            learner_id=learner_id, skill_id=skill_id, limit=limit
        )
        return [
            SkillEvidenceRead(
                id=ev.id,
                learner_id=ev.learner_id,
                skill_id=ev.skill_id,
                skill_name=ev.skill.name if ev.skill else ev.skill_id,
                source_type=ev.source_type,
                source_id=ev.source_id,
                score=round(ev.score, 3),
                confidence=round(ev.confidence, 3),
                weight=ev.weight,
                evidence_summary=ev.evidence_summary,
                metadata_json=ev.metadata_json,
                created_at=ev.created_at,
            )
            for ev in evidence_list
        ]

    def record_skill_evidence(
        self,
        learner_id: str,
        skill_id: str,
        source_type: str,
        source_id: str,
        score: float,
        confidence: float,
        evidence_summary: str,
        weight: float = 1.0,
        metadata_json: dict | None = None,
    ) -> LearnerSkillState:
        """Add new skill evidence and recompute learner skill mastery state."""
        evidence = SkillEvidence(
            learner_id=learner_id,
            skill_id=skill_id,
            source_type=source_type,
            source_id=source_id,
            score=max(0.0, min(1.0, score)),
            confidence=max(0.0, min(1.0, confidence)),
            weight=weight,
            evidence_summary=evidence_summary,
            metadata_json=metadata_json,
        )
        self.repo.add_evidence(evidence)

        # Retrieve or initialize skill state
        state = self.repo.get_skill_state(learner_id, skill_id)
        if not state:
            state = LearnerSkillState(
                learner_id=learner_id,
                skill_id=skill_id,
                mastery_score=0.0,
                confidence_score=0.0,
                evidence_count=0,
            )
            self.db.add(state)
            self.db.flush()

        # Update mastery and confidence based on accumulated evidence
        if state.evidence_count == 0:
            state.mastery_score = evidence.score
            state.confidence_score = evidence.confidence
        else:
            # Weighted moving average of mastery score
            # Prior evidence gets weight, new evidence gets weight
            prior_weight = max(1.0, float(state.evidence_count))
            new_weight = evidence.weight
            total_weight = prior_weight + new_weight

            updated_mastery = (
                (state.mastery_score * prior_weight) + (evidence.score * new_weight)
            ) / total_weight
            state.mastery_score = max(0.0, min(1.0, updated_mastery))

            # Confidence increases with more evidence, asymptotically approaching 0.98
            confidence_gain = (1.0 - state.confidence_score) * 0.20 * evidence.confidence
            state.confidence_score = min(0.98, state.confidence_score + confidence_gain)

        state.evidence_count += 1
        state.last_assessed_at = datetime.now(UTC)
        self.db.commit()

        logger.info(
            "Updated skill '%s' for learner %s: mastery=%.3f, confidence=%.3f (evidence count: %d)",
            skill_id,
            learner_id,
            state.mastery_score,
            state.confidence_score,
            state.evidence_count,
        )
        return state
