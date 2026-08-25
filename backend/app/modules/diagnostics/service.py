"""Diagnostic assessment service managing questions, attempts, grading, and evidence generation."""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException, LearnZoException
from app.modules.diagnostics.models import (
    DiagnosticAnswer,
    DiagnosticAttempt,
    DiagnosticQuestion,
)
from app.modules.diagnostics.repository import DiagnosticRepository
from app.modules.diagnostics.schemas import (
    DiagnosticAttemptRead,
    DiagnosticOptionPublic,
    DiagnosticQuestionPublic,
    DiagnosticResultResponse,
    DiagnosticSeedResponse,
    DiagnosticSubmissionPayload,
    QuestionAnswerResult,
    SkillScoreBreakdown,
)
from app.modules.diagnostics.seed_data import SEEDED_DIAGNOSTIC_QUESTIONS
from app.modules.learner.repository import LearnerRepository
from app.modules.learner.service import LearnerService

logger = logging.getLogger(__name__)


class DiagnosticService:
    """Service orchestrating diagnostic assessments and updating learner model from evidence."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = DiagnosticRepository(db)
        self.learner_repo = LearnerRepository(db)
        self.learner_service = LearnerService(db)

    def list_questions_public(
        self, skill_id: Optional[str] = None
    ) -> List[DiagnosticQuestionPublic]:
        """Fetch sanitized diagnostic questions suitable for presenting to the learner."""
        questions = self.repo.list_active_questions(skill_id=skill_id)
        results: List[DiagnosticQuestionPublic] = []

        for q in questions:
            # Strip correct answers and explanations for safety
            public_options = [
                DiagnosticOptionPublic(id=opt["id"], text=opt["text"])
                for opt in q.options_json
            ]
            results.append(
                DiagnosticQuestionPublic(
                    id=q.id,
                    skill_id=q.skill_id,
                    skill_name=q.skill.name if q.skill else q.skill_id,
                    question_text=q.question_text,
                    difficulty=q.difficulty,
                    options=public_options,
                    order_index=q.order_index,
                )
            )
        return results

    def start_attempt(self, learner_id: str) -> DiagnosticAttemptRead:
        """Start a new diagnostic assessment attempt for a learner."""
        learner = self.learner_repo.get_learner_by_id(learner_id)
        if not learner:
            raise EntityNotFoundException("Learner", learner_id)

        active_questions = self.repo.list_active_questions()
        if not active_questions:
            raise LearnZoException("No active diagnostic questions available. Please seed questions first.")

        attempt = DiagnosticAttempt(
            learner_id=learner_id,
            status="in_progress",
            total_questions=len(active_questions),
            correct_count=0,
            score_percentage=0.0,
            started_at=datetime.now(timezone.utc),
        )
        self.repo.create_attempt(attempt)
        self.db.commit()

        logger.info("Started diagnostic attempt '%s' for learner '%s'", attempt.id, learner_id)
        return DiagnosticAttemptRead.model_validate(attempt)

    def submit_attempt(
        self, attempt_id: str, payload: DiagnosticSubmissionPayload
    ) -> DiagnosticResultResponse:
        """Evaluate submitted answers, generate skill evidence, update learner model, and complete attempt."""
        attempt = self.repo.get_attempt_by_id(attempt_id)
        if not attempt:
            raise EntityNotFoundException("DiagnosticAttempt", attempt_id)

        if attempt.status == "completed":
            raise LearnZoException("This diagnostic attempt has already been submitted and completed.")

        question_ids = [a.question_id for a in payload.answers]
        questions = {q.id: q for q in self.repo.get_questions_by_ids(question_ids)}

        answers_to_insert: List[DiagnosticAnswer] = []
        detailed_answers: List[QuestionAnswerResult] = []

        # Track per-skill grading
        # skill_id -> {"total": int, "correct": int, "weighted_total": float, "weighted_correct": float, "skill_name": str, "category": str, "questions": list}
        skill_stats: Dict[str, dict] = defaultdict(
            lambda: {
                "total": 0,
                "correct": 0,
                "weighted_total": 0.0,
                "weighted_correct": 0.0,
                "skill_name": "",
                "category": "",
                "items": [],
            }
        )

        overall_correct = 0
        overall_total = len(payload.answers)

        for ans in payload.answers:
            question = questions.get(ans.question_id)
            if not question:
                continue

            selected = ans.selected_option_id.strip().upper()
            is_correct = selected == question.correct_option_id.strip().upper()
            if is_correct:
                overall_correct += 1

            # Build record
            db_answer = DiagnosticAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option_id=selected,
                is_correct=is_correct,
                answered_at=datetime.now(timezone.utc),
            )
            answers_to_insert.append(db_answer)

            detailed_answers.append(
                QuestionAnswerResult(
                    question_id=question.id,
                    skill_id=question.skill_id,
                    question_text=question.question_text,
                    selected_option_id=selected,
                    correct_option_id=question.correct_option_id,
                    is_correct=is_correct,
                    explanation=question.explanation,
                )
            )

            # Skill tracking
            stats = skill_stats[question.skill_id]
            stats["total"] += 1
            stats["weighted_total"] += question.difficulty_weight
            stats["skill_name"] = question.skill.name if question.skill else question.skill_id
            stats["category"] = question.skill.category if question.skill else "General"
            if is_correct:
                stats["correct"] += 1
                stats["weighted_correct"] += question.difficulty_weight
            stats["items"].append(f"{question.id} ({'correct' if is_correct else 'incorrect'})")

        self.repo.add_answers(answers_to_insert)

        # Generate SkillEvidence and update LearnerSkillStates
        skill_breakdown: List[SkillScoreBreakdown] = []

        for skill_id, stats in skill_stats.items():
            weighted_total = max(stats["weighted_total"], 0.001)
            skill_score = stats["weighted_correct"] / weighted_total
            score_pct = round(skill_score * 100.0, 1)

            summary = (
                f"Onboarding Diagnostic: {stats['correct']}/{stats['total']} conceptual questions "
                f"correct ({score_pct}% score) on {stats['skill_name']}."
            )

            # Record formal evidence into learner model
            updated_state = self.learner_service.record_skill_evidence(
                learner_id=attempt.learner_id,
                skill_id=skill_id,
                source_type="diagnostic",
                source_id=attempt.id,
                score=skill_score,
                confidence=0.75,  # Diagnostic produces strong baseline confidence
                evidence_summary=summary,
                weight=1.5,  # Diagnostic holds significant initial weight
                metadata_json={
                    "total_questions": stats["total"],
                    "correct_questions": stats["correct"],
                    "question_results": stats["items"],
                },
            )

            skill_breakdown.append(
                SkillScoreBreakdown(
                    skill_id=skill_id,
                    skill_name=stats["skill_name"],
                    category=stats["category"],
                    total_questions=stats["total"],
                    correct_questions=stats["correct"],
                    score_percentage=score_pct,
                    updated_mastery_score=round(updated_state.mastery_score, 3),
                    updated_confidence_score=round(updated_state.confidence_score, 3),
                    evidence_summary=summary,
                )
            )

        # Update attempt completion
        overall_percentage = round(
            (overall_correct / max(overall_total, 1)) * 100.0, 1
        )
        attempt.status = "completed"
        attempt.total_questions = overall_total
        attempt.correct_count = overall_correct
        attempt.score_percentage = overall_percentage
        attempt.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        logger.info(
            "Diagnostic attempt '%s' completed: %d/%d (%.1f%%)",
            attempt.id,
            overall_correct,
            overall_total,
            overall_percentage,
        )

        return DiagnosticResultResponse(
            attempt=DiagnosticAttemptRead.model_validate(attempt),
            overall_score_percentage=overall_percentage,
            total_questions=overall_total,
            correct_count=overall_correct,
            skill_breakdown=skill_breakdown,
            detailed_answers=detailed_answers,
        )

    def get_attempt_result(self, attempt_id: str) -> DiagnosticResultResponse:
        """Retrieve evaluation result and answer breakdown for an existing attempt."""
        attempt = self.repo.get_attempt_by_id(attempt_id)
        if not attempt:
            raise EntityNotFoundException("DiagnosticAttempt", attempt_id)

        detailed_answers: List[QuestionAnswerResult] = []
        skill_stats: Dict[str, dict] = defaultdict(
            lambda: {
                "total": 0,
                "correct": 0,
                "skill_name": "",
                "category": "",
            }
        )

        for ans in attempt.answers:
            q = ans.question
            detailed_answers.append(
                QuestionAnswerResult(
                    question_id=q.id,
                    skill_id=q.skill_id,
                    question_text=q.question_text,
                    selected_option_id=ans.selected_option_id,
                    correct_option_id=q.correct_option_id,
                    is_correct=ans.is_correct,
                    explanation=q.explanation,
                )
            )
            st = skill_stats[q.skill_id]
            st["total"] += 1
            st["skill_name"] = q.skill.name if q.skill else q.skill_id
            st["category"] = q.skill.category if q.skill else "General"
            if ans.is_correct:
                st["correct"] += 1

        skill_breakdown = [
            SkillScoreBreakdown(
                skill_id=sid,
                skill_name=st["skill_name"],
                category=st["category"],
                total_questions=st["total"],
                correct_questions=st["correct"],
                score_percentage=round((st["correct"] / max(st["total"], 1)) * 100.0, 1),
                updated_mastery_score=round(st["correct"] / max(st["total"], 1), 3),
                updated_confidence_score=0.75,
                evidence_summary=f"{st['correct']}/{st['total']} correct on {st['skill_name']}",
            )
            for sid, st in skill_stats.items()
        ]

        return DiagnosticResultResponse(
            attempt=DiagnosticAttemptRead.model_validate(attempt),
            overall_score_percentage=attempt.score_percentage,
            total_questions=attempt.total_questions,
            correct_count=attempt.correct_count,
            skill_breakdown=skill_breakdown,
            detailed_answers=detailed_answers,
        )

    def seed_questions(self, force: bool = False) -> DiagnosticSeedResponse:
        """Seed diagnostic questions into database."""
        existing_count = self.repo.count_questions()
        if existing_count > 0 and not force:
            return DiagnosticSeedResponse(
                message="Diagnostic questions already seeded.",
                questions_seeded=existing_count,
            )

        count = 0
        for q_data in SEEDED_DIAGNOSTIC_QUESTIONS:
            existing = self.repo.get_question_by_id(q_data["id"])
            if not existing:
                q = DiagnosticQuestion(
                    id=q_data["id"],
                    skill_id=q_data["skill_id"],
                    question_text=q_data["question_text"],
                    difficulty=q_data["difficulty"],
                    difficulty_weight=q_data["difficulty_weight"],
                    options_json=q_data["options_json"],
                    correct_option_id=q_data["correct_option_id"],
                    explanation=q_data["explanation"],
                    order_index=q_data["order_index"],
                    is_active=True,
                )
                self.db.add(q)
                count += 1

        self.db.commit()
        logger.info("Seeded %d diagnostic questions", count)
        return DiagnosticSeedResponse(
            message="Diagnostic questions seeded successfully.",
            questions_seeded=self.repo.count_questions(),
        )

    def seed_if_empty(self) -> bool:
        """Helper to seed questions on startup if empty."""
        try:
            if self.repo.count_questions() == 0:
                logger.info("Diagnostic questions empty on startup. Triggering auto-seed.")
                self.seed_questions(force=False)
                return True
        except Exception as exc:
            logger.warning("Diagnostic questions auto-seed check skipped/failed: %s", exc)
        return False

