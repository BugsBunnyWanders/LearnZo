"""Unit and integration tests for Daily Learning Planner orchestration and candidate ranking."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.curriculum.service import CurriculumService
from app.modules.diagnostics.service import DiagnosticService
from app.modules.learner.schemas import LearnerCreate
from app.modules.learner.service import LearnerService


def setup_curriculum_and_diagnostic(db_session: Session) -> None:
    """Helper to seed curriculum and diagnostics."""
    CurriculumService(db_session).seed_curriculum(force=True)
    DiagnosticService(db_session).seed_questions(force=True)


def test_new_learner_plan_selects_root_topic(client: TestClient, db_session: Session) -> None:
    """Test a brand new learner with 0 evidence is assigned root topic SQL Fundamentals."""
    setup_curriculum_and_diagnostic(db_session)
    learner_service = LearnerService(db_session)

    profile = learner_service.onboard_learner(
        LearnerCreate(name="Frank", email="frank@example.com", target_role="Backend SDE2")
    )
    learner_id = profile.learner.id

    # Fetch daily plan
    response = client.get(f"/api/v1/learners/{learner_id}/daily-plan")
    assert response.status_code == status.HTTP_200_OK

    plan = response.json()
    assert plan["selected_topic_id"] == "topic_sql_execution"
    assert plan["skill_id"] == "sql_fundamentals"
    assert plan["reason_code"] == "FOUNDATIONAL_START"
    assert "foundational" in plan["reason_summary"].lower()


def test_post_diagnostic_plan_selects_highest_gap_eligible_topic(
    client: TestClient, db_session: Session
) -> None:
    """Test after diagnostic with strong SQL and low Indexing, Indexing is chosen over locked topics."""
    setup_curriculum_and_diagnostic(db_session)
    learner_service = LearnerService(db_session)

    profile = learner_service.onboard_learner(
        LearnerCreate(name="Grace", email="grace@example.com", target_role="Backend SDE2")
    )
    learner_id = profile.learner.id

    # Provide full post-diagnostic scores across all 7 skills:
    # SQL (100%), Transactions (80%), Caching (80%), Distributed (75%), Messaging (75%), System Design (75%)
    # Database Indexing has a large gap (50%).
    for skill_id, score in [
        ("sql_fundamentals", 1.0),
        ("transactions", 0.80),
        ("caching", 0.80),
        ("distributed_systems", 0.75),
        ("messaging_queues", 0.75),
        ("system_design", 0.75),
        ("database_indexing", 0.50),
    ]:
        learner_service.record_skill_evidence(
            learner_id=learner_id,
            skill_id=skill_id,
            source_type="diagnostic",
            source_id="diag_test",
            score=score,
            confidence=0.80 if score > 0.6 else 0.75,
            evidence_summary=f"Diagnostic: {score*100:.0f}% score on {skill_id}",
        )

    # Generate daily plan
    res = client.post(f"/api/v1/learners/{learner_id}/daily-plan/generate?force=true")
    assert res.status_code == status.HTTP_200_OK
    plan = res.json()

    # Indexing has 5.0 importance and is unlocked by SQL (100% >= 70%)
    assert plan["selected_topic_id"] == "topic_db_indexing"
    assert plan["skill_id"] == "database_indexing"
    assert plan["reason_code"] == "HIGH_VALUE_GAP"
    assert "Database Indexing" in plan["reason_summary"]
    assert plan["current_mastery_score"] == 0.50


def test_prerequisite_locking_in_analysis_breakdown(
    client: TestClient, db_session: Session
) -> None:
    """Test that advanced topics requiring unmet prerequisites are properly reported as locked."""
    setup_curriculum_and_diagnostic(db_session)
    learner_service = LearnerService(db_session)

    profile = learner_service.onboard_learner(
        LearnerCreate(name="Heidi", email="heidi@example.com")
    )
    learner_id = profile.learner.id

    # Give Heidi SQL mastery only
    learner_service.record_skill_evidence(
        learner_id=learner_id,
        skill_id="sql_fundamentals",
        source_type="diagnostic",
        source_id="diag_test",
        score=1.0,
        confidence=0.90,
        evidence_summary="Perfect SQL",
    )

    res = client.get(f"/api/v1/learners/{learner_id}/daily-plan/analysis")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()

    assert data["total_curriculum_topics"] == 10

    eligible_ids = [c["topic_id"] for c in data["eligible_candidates"]]
    locked_ids = [c["topic_id"] for c in data["locked_candidates"]]

    # Unlocked by SQL: topic_sql_execution, topic_db_indexing, topic_transactions_acid, topic_caching_strategies
    assert "topic_db_indexing" in eligible_ids
    assert "topic_transactions_acid" in eligible_ids
    assert "topic_caching_strategies" in eligible_ids

    # Locked: topic_system_design_orders, topic_distributed_transactions, topic_message_queues, etc.
    assert "topic_system_design_orders" in locked_ids
    assert "topic_distributed_transactions" in locked_ids

    # Verify locked candidate details specify unmet prerequisites
    sys_design = next(
        c for c in data["locked_candidates"] if c["topic_id"] == "topic_system_design_orders"
    )
    assert len(sys_design["unmet_prerequisites"]) >= 1


def test_daily_plan_idempotency(client: TestClient, db_session: Session) -> None:
    """Test calling get_daily_plan multiple times on the same date returns the same plan."""
    setup_curriculum_and_diagnostic(db_session)
    learner_service = LearnerService(db_session)

    profile = learner_service.onboard_learner(LearnerCreate(name="Ivan", email="ivan@example.com"))
    learner_id = profile.learner.id

    # First call creates
    res1 = client.get(f"/api/v1/learners/{learner_id}/daily-plan")
    assert res1.status_code == status.HTTP_200_OK
    plan1 = res1.json()

    # Second call returns existing
    res2 = client.get(f"/api/v1/learners/{learner_id}/daily-plan")
    assert res2.status_code == status.HTTP_200_OK
    plan2 = res2.json()

    assert plan1["id"] == plan2["id"]
    assert plan1["selected_topic_id"] == plan2["selected_topic_id"]
