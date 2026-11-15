"""Tests for the FastAPI application."""

from fastapi.testclient import TestClient

from coi.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Test the health-check endpoint."""

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_documentation() -> None:
    """Test that the OpenAPI schema is accessible."""

    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert data["info"]["title"] == "Career Opportunity Intelligence API"
    assert data["info"]["version"] == "0.1.0"


def test_swagger_documentation() -> None:
    """Test that Swagger UI is accessible."""

    response = client.get("/docs")

    assert response.status_code == 200


def test_v1_router_is_registered() -> None:
    """Test that the versioned API router is registered."""

    paths = app.openapi()["paths"]

    assert "/health" in paths
