"""Tests for job source API routes."""

from fastapi.testclient import TestClient

from coi.api.main import app

client = TestClient(app)


def test_get_sources() -> None:
    """Test retrieving available job sources."""

    response = client.get("/api/v1/sources")

    assert response.status_code == 200

    sources = response.json()

    assert len(sources) == 4
    assert [source["source_id"] for source in sources] == [
        "linkedin",
        "indeed",
        "company_website",
        "other",
    ]


def test_get_sources_response_fields() -> None:
    """Test the fields exposed by the source endpoint."""

    response = client.get("/api/v1/sources")

    assert response.status_code == 200

    source = response.json()[0]

    assert set(source) == {
        "source_id",
        "name",
        "source_type",
        "base_url",
        "description",
    }

    assert "config" not in source


def test_get_sources_source_type() -> None:
    """Test that manually submitted sources use the manual source type."""

    response = client.get("/api/v1/sources")

    assert response.status_code == 200

    assert all(source["source_type"] == "manual" for source in response.json())
