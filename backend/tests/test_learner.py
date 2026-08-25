"""Unit and integration tests for Learner profile and evidence-backed skill states."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.curriculum.service import CurriculumService
from app.modules.learner.service import LearnerService


def test_onboard_learner_and_initialize_skill_states(
    client: TestClient, db_session: Session
) -> None:
    """Test onboarding creates a profile and initializes skill states for all 7 curriculum skills."""
    # Seed curriculum first so skills exist
    CurriculumService(db_session).seed_curriculum(force=True)

    payload = {
        "name": "Alice Developer",
        "email": "alice@example.com",
        "target_role": "Backend SDE2",
        "target_mastery": 0.85,
        "experience_level": "Mid-level SDE",
    }

    response = client.post("/api/v1/learners/onboard", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["learner"]["name"] == "Alice Developer"
    assert data["learner"]["email"] == "alice@example.com"
    assert data["overall_readiness_percentage"] == 0.0
    assert len(data["skills"]) == 7

    # All initial skills should start at 0.0 mastery and 0.0 confidence
    for skill in data["skills"]:
        assert skill["mastery_score"] == 0.0
        assert skill["confidence_score"] == 0.0
        assert skill["evidence_count"] == 0


def test_get_learner_profile_and_skills(
    client: TestClient, db_session: Session
) -> None:
    """Test fetching learner profile and skills via GET endpoints."""
    CurriculumService(db_session).seed_curriculum(force=True)

    onboard_res = client.post(
        "/api/v1/learners/onboard",
        json={"name": "Bob Smith", "email": "bob@example.com"},
    )
    learner_id = onboard_res.json()["learner"]["id"]

    # 1. Fetch Profile
    res_prof = client.get(f"/api/v1/learners/{learner_id}")
    assert res_prof.status_code == status.HTTP_200_OK
    assert res_prof.json()["learner"]["id"] == learner_id

    # 2. Fetch Skills directly
    res_skills = client.get(f"/api/v1/learners/{learner_id}/skills")
    assert res_skills.status_code == status.HTTP_200_OK
    skills = res_skills.json()
    assert len(skills) == 7


def test_record_evidence_and_update_mastery(
    client: TestClient, db_session: Session
) -> None:
    """Test recording evidence updates mastery and confidence calculations."""
    CurriculumService(db_session).seed_curriculum(force=True)
    service = LearnerService(db_session)

    profile = service.onboard_learner(
        data=type("LearnerCreate", (), {
            "name": "Charlie",
            "email": "charlie@example.com",
            "target_role": "Backend SDE2",
            "target_mastery": 0.85,
            "experience_level": "Junior SDE",
        })()
    )
    learner_id = profile.learner.id

    # Add 1st evidence item for database_indexing
    state1 = service.record_skill_evidence(
        learner_id=learner_id,
        skill_id="database_indexing",
        source_type="diagnostic",
        source_id="test_diag_1",
        score=0.80,
        confidence=0.75,
        evidence_summary="Diagnostic MCQ: Correctly answered composite index prefix question",
    )
    assert state1.mastery_score == 0.80
    assert state1.confidence_score == 0.75
    assert state1.evidence_count == 1

    # Add 2nd evidence item with a higher score
    state2 = service.record_skill_evidence(
        learner_id=learner_id,
        skill_id="database_indexing",
        source_type="assignment",
        source_id="test_assign_1",
        score=1.0,
        confidence=0.90,
        evidence_summary="Solved EXPLAIN slow query analysis assignment",
    )
    # Mastery should increase from moving average
    assert state2.mastery_score > 0.80
    assert state2.confidence_score > 0.75
    assert state2.evidence_count == 2

    # Verify evidence history retrieval
    res_ev = client.get(f"/api/v1/learners/{learner_id}/evidence")
    assert res_ev.status_code == status.HTTP_200_OK
    ev_list = res_ev.json()
    assert len(ev_list) == 2
    assert ev_list[0]["skill_id"] == "database_indexing"


def test_nonexistent_learner_returns_404(client: TestClient) -> None:
    """Test 404 when querying unknown learner."""
    response = client.get("/api/v1/learners/learner_unknown_123")
    assert response.status_code == status.HTTP_404_NOT_FOUND

