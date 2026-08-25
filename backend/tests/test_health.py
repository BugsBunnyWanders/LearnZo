"""Unit and integration tests for health check and root endpoints."""

from fastapi import status
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns welcome payload."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["health"] == "/api/v1/health"
    assert data["docs"] == "/api/v1/docs"


def test_health_check_endpoint(client: TestClient) -> None:
    """Test health check returns status ok and expected metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "LearnZo Backend"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    assert "database" in data
    assert "status" in data["database"]


def test_openapi_docs_accessible(client: TestClient) -> None:
    """Test OpenAPI JSON schema is generated and accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    schema = response.json()
    assert schema["info"]["title"] == "LearnZo Backend"
    assert "/api/v1/health" in schema["paths"]
