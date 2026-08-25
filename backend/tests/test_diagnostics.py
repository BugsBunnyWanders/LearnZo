"""Unit and integration tests for Onboarding Diagnostic flow."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.curriculum.service import CurriculumService
from app.modules.diagnostics.service import DiagnosticService
from app.modules.learner.schemas import LearnerCreate
from app.modules.learner.service import LearnerService


def setup_curriculum_and_diagnostic(db_session: Session) -> None:
    """Helper to seed curriculum and diagnostic questions."""
    CurriculumService(db_session).seed_curriculum(force=True)
    DiagnosticService(db_session).seed_questions(force=True)


def test_get_diagnostic_questions_sanitized(client: TestClient, db_session: Session) -> None:
    """Test fetching diagnostic questions returns sanitized payloads without answers."""
    setup_curriculum_and_diagnostic(db_session)

    response = client.get("/api/v1/diagnostics/questions")
    assert response.status_code == status.HTTP_200_OK

    questions = response.json()
    assert len(questions) == 14

    for q in questions:
        assert "id" in q
        assert "skill_id" in q
        assert "question_text" in q
        assert "options" in q
        assert len(q["options"]) == 4
        # CRITICAL: ensure answers and explanations are not leaked to the client
        assert "correct_option_id" not in q
        assert "explanation" not in q


def test_diagnostic_end_to_end_flow(client: TestClient, db_session: Session) -> None:
    """Test full diagnostic journey: start -> answer -> grade -> evidence -> updated skill profile."""
    setup_curriculum_and_diagnostic(db_session)

    # 1. Onboard Learner
    learner_service = LearnerService(db_session)
    learner_profile = learner_service.onboard_learner(
        LearnerCreate(
            name="David Kim",
            email="david@example.com",
            target_role="Backend SDE2",
            target_mastery=0.85,
        )
    )
    learner_id = learner_profile.learner.id

    # 2. Start Diagnostic Attempt
    start_res = client.post(
        "/api/v1/diagnostics/start",
        json={"learner_id": learner_id},
    )
    assert start_res.status_code == status.HTTP_201_CREATED
    attempt = start_res.json()
    attempt_id = attempt["id"]
    assert attempt["status"] == "in_progress"
    assert attempt["total_questions"] == 14

    # 3. Submit Answers:
    # Let's answer SQL correctly (B, B), Indexing mixed (C, A), Transactions correct (B, B),
    # Caching correct (B, A), Distributed correct (B, C), Messaging mixed (B, A), System Design correct (A, B)
    submission_payload = {
        "answers": [
            {"question_id": "dq_sql_1", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_sql_2", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_idx_1", "selected_option_id": "C"},  # Correct
            {"question_id": "dq_idx_2", "selected_option_id": "A"},  # Incorrect (correct is B)
            {"question_id": "dq_tx_1", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_tx_2", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_cache_1", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_cache_2", "selected_option_id": "A"},  # Correct
            {"question_id": "dq_dist_1", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_dist_2", "selected_option_id": "C"},  # Correct
            {"question_id": "dq_msg_1", "selected_option_id": "B"},  # Correct
            {"question_id": "dq_msg_2", "selected_option_id": "C"},  # Incorrect (correct is B)
            {"question_id": "dq_sd_1", "selected_option_id": "A"},  # Correct
            {"question_id": "dq_sd_2", "selected_option_id": "B"},  # Correct
        ]
    }

    submit_res = client.post(
        f"/api/v1/diagnostics/{attempt_id}/submit",
        json=submission_payload,
    )
    assert submit_res.status_code == status.HTTP_200_OK
    result = submit_res.json()

    assert result["attempt"]["status"] == "completed"
    assert result["total_questions"] == 14
    assert result["correct_count"] == 12
    assert result["overall_score_percentage"] > 80.0
    assert len(result["skill_breakdown"]) == 7
    assert len(result["detailed_answers"]) == 14

    # 4. Verify Learner Skill Profile is now calibrated and evidence-backed
    profile_res = client.get(f"/api/v1/learners/{learner_id}")
    assert profile_res.status_code == status.HTTP_200_OK
    profile = profile_res.json()

    assert profile["overall_readiness_percentage"] > 0.0
    skills_map = {s["skill_id"]: s for s in profile["skills"]}

    # SQL should have 1.0 (2/2 correct)
    assert skills_map["sql_fundamentals"]["mastery_score"] == 1.0
    assert skills_map["sql_fundamentals"]["evidence_count"] == 1
    assert skills_map["sql_fundamentals"]["confidence_score"] == 0.75

    # Indexing had 1/2 correct (~0.52 mastery)
    assert 0.40 <= skills_map["database_indexing"]["mastery_score"] <= 0.60
    assert skills_map["database_indexing"]["evidence_count"] == 1

    # Verify Evidence History
    ev_res = client.get(f"/api/v1/learners/{learner_id}/evidence")
    assert ev_res.status_code == status.HTTP_200_OK
    ev_data = ev_res.json()
    assert len(ev_data) == 7  # 1 evidence item generated per assessed skill dimension


def test_cannot_submit_completed_attempt(client: TestClient, db_session: Session) -> None:
    """Test submitting an already completed attempt raises an error."""
    setup_curriculum_and_diagnostic(db_session)
    learner_service = LearnerService(db_session)
    profile = learner_service.onboard_learner(LearnerCreate(name="Eve", email="eve@example.com"))

    start_res = client.post("/api/v1/diagnostics/start", json={"learner_id": profile.learner.id})
    attempt_id = start_res.json()["id"]

    client.post(
        f"/api/v1/diagnostics/{attempt_id}/submit",
        json={"answers": [{"question_id": "dq_sql_1", "selected_option_id": "B"}]},
    )

    # Second submission attempt should fail
    retry_res = client.post(
        f"/api/v1/diagnostics/{attempt_id}/submit",
        json={"answers": [{"question_id": "dq_sql_1", "selected_option_id": "B"}]},
    )
    assert (
        retry_res.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        or retry_res.status_code == status.HTTP_400_BAD_REQUEST
    )
