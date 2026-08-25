"""Database repository for Learner and Skill State entities."""

from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.modules.learner.models import Learner, LearnerSkillState, SkillEvidence


class LearnerRepository:
    """Encapsulates database operations for learner profiles, states, and evidence."""

    def __init__(self, db: Session):
        self.db = db

    def create_learner(self, learner: Learner) -> Learner:
        """Persist a new learner."""
        self.db.add(learner)
        self.db.flush()
        return learner

    def get_learner_by_id(self, learner_id: str) -> Optional[Learner]:
        """Fetch learner by primary ID."""
        stmt = select(Learner).where(Learner.id == learner_id)
        return self.db.scalars(stmt).first()

    def get_learner_by_email(self, email: str) -> Optional[Learner]:
        """Fetch learner by email address."""
        stmt = select(Learner).where(Learner.email == email)
        return self.db.scalars(stmt).first()

    def list_skill_states(self, learner_id: str) -> List[LearnerSkillState]:
        """Fetch all skill states for a learner."""
        stmt = (
            select(LearnerSkillState)
            .options(joinedload(LearnerSkillState.skill))
            .where(LearnerSkillState.learner_id == learner_id)
            .order_by(LearnerSkillState.id)
        )
        return list(self.db.scalars(stmt).all())

    def get_skill_state(self, learner_id: str, skill_id: str) -> Optional[LearnerSkillState]:
        """Fetch specific skill state for a learner."""
        stmt = (
            select(LearnerSkillState)
            .options(joinedload(LearnerSkillState.skill))
            .where(
                LearnerSkillState.learner_id == learner_id,
                LearnerSkillState.skill_id == skill_id,
            )
        )
        return self.db.scalars(stmt).first()

    def add_evidence(self, evidence: SkillEvidence) -> SkillEvidence:
        """Persist a new piece of skill evidence."""
        self.db.add(evidence)
        self.db.flush()
        return evidence

    def list_evidence(
        self,
        learner_id: str,
        skill_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[SkillEvidence]:
        """Fetch evidence history for a learner ordered by creation time descending."""
        stmt = (
            select(SkillEvidence)
            .options(joinedload(SkillEvidence.skill))
            .where(SkillEvidence.learner_id == learner_id)
            .order_by(desc(SkillEvidence.created_at))
            .limit(limit)
        )
        if skill_id:
            stmt = stmt.where(SkillEvidence.skill_id == skill_id)
        return list(self.db.scalars(stmt).all())

