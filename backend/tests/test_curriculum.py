"""Unit and integration tests for Curriculum & Skill Graph domain."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.curriculum.service import CurriculumService


def test_seed_and_list_skills(client: TestClient, db_session: Session) -> None:
    """Test seeding curriculum and listing all skills."""
    service = CurriculumService(db_session)
    service.seed_curriculum(force=True)

    response = client.get("/api/v1/curriculum/skills")
    assert response.status_code == status.HTTP_200_OK

    skills = response.json()
    assert len(skills) == 7
    skill_ids = [s["id"] for s in skills]
    assert "sql_fundamentals" in skill_ids
    assert "database_indexing" in skill_ids
    assert "transactions" in skill_ids
    assert "caching" in skill_ids
    assert "distributed_systems" in skill_ids
    assert "messaging_queues" in skill_ids
    assert "system_design" in skill_ids


def test_list_topics(client: TestClient, db_session: Session) -> None:
    """Test listing all topics with summaries."""
    service = CurriculumService(db_session)
    service.seed_curriculum(force=True)

    response = client.get("/api/v1/curriculum/topics")
    assert response.status_code == status.HTTP_200_OK

    topics = response.json()
    assert len(topics) == 10
    # First topic in order should be SQL Fundamentals
    assert topics[0]["id"] == "topic_sql_execution"
    assert topics[0]["order_index"] == 1
    assert topics[0]["resource_count"] >= 1


def test_filter_topics_by_skill(client: TestClient, db_session: Session) -> None:
    """Test filtering topics by skill_id."""
    service = CurriculumService(db_session)
    service.seed_curriculum(force=True)

    response = client.get("/api/v1/curriculum/topics?skill_id=database_indexing")
    assert response.status_code == status.HTTP_200_OK

    topics = response.json()
    assert len(topics) == 1
    assert topics[0]["id"] == "topic_db_indexing"
    assert topics[0]["skill_id"] == "database_indexing"


def test_get_topic_by_id_and_slug(client: TestClient, db_session: Session) -> None:
    """Test retrieving topic details by ID and slug."""
    service = CurriculumService(db_session)
    service.seed_curriculum(force=True)

    # 1. Fetch by ID
    res_by_id = client.get("/api/v1/curriculum/topics/topic_db_indexing")
    assert res_by_id.status_code == status.HTTP_200_OK
    data_id = res_by_id.json()
    assert data_id["id"] == "topic_db_indexing"
    assert data_id["slug"] == "database-indexing-b-trees"
    assert data_id["skill"]["id"] == "database_indexing"
    assert len(data_id["resources"]) >= 1
    assert data_id["resources"][0]["resource_type"] == "youtube"
    assert "Hussein Nasser" in data_id["resources"][0]["author"]

    # Verify prerequisite
    prereq_ids = [p["prerequisite_topic_id"] for p in data_id["prerequisites"]]
    assert "topic_sql_execution" in prereq_ids

    # 2. Fetch by slug
    res_by_slug = client.get("/api/v1/curriculum/topics/database-indexing-b-trees")
    assert res_by_slug.status_code == status.HTTP_200_OK
    assert res_by_slug.json()["id"] == data_id["id"]


def test_get_nonexistent_topic(client: TestClient, db_session: Session) -> None:
    """Test 404 EntityNotFoundException when topic does not exist."""
    response = client.get("/api/v1/curriculum/topics/non_existent_topic_id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "error" in data
    assert "Topic" in data["error"]["message"]


def test_curriculum_graph_dag(client: TestClient, db_session: Session) -> None:
    """Test full curriculum graph structure and DAG properties."""
    service = CurriculumService(db_session)
    service.seed_curriculum(force=True)

    response = client.get("/api/v1/curriculum/graph")
    assert response.status_code == status.HTTP_200_OK

    graph = response.json()
    assert len(graph["skills"]) == 7
    assert len(graph["nodes"]) == 10
    assert len(graph["edges"]) >= 9

    # Verify specific edge
    edge_pairs = [(e["source"], e["target"]) for e in graph["edges"]]
    assert ("topic_sql_execution", "topic_db_indexing") in edge_pairs
    assert ("topic_db_indexing", "topic_system_design_orders") in edge_pairs

    # Verify graph is a valid DAG (Acyclic detection using Kahn's algorithm)
    in_degree = {node["id"]: 0 for node in graph["nodes"]}
    adj: dict[str, list[str]] = {node["id"]: [] for node in graph["nodes"]}

    for edge in graph["edges"]:
        adj[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] += 1

    queue = [node_id for node_id, deg in in_degree.items() if deg == 0]
    visited_count = 0

    while queue:
        curr = queue.pop(0)
        visited_count += 1
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If visited_count == total nodes, then the graph is acyclic (valid DAG)
    assert visited_count == len(graph["nodes"]), "Curriculum graph contains cycles!"


def test_seed_curriculum_endpoint(client: TestClient, db_session: Session) -> None:
    """Test seed API endpoint execution."""
    response = client.post("/api/v1/curriculum/seed?force=true")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["skills_seeded"] == 7
    assert data["topics_seeded"] == 10
    assert data["resources_seeded"] == 10
