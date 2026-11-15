"""Tests for job source API schemas."""

from pydantic import HttpUrl

from coi.models.enums import SourceType
from coi.models.source import JobSource
from coi.schemas.source import JobSourceResponse


def test_valid_source_response() -> None:
    """Test creation of a source response."""

    source = JobSource(
        source_id="linkedin",
        name="LinkedIn",
        source_type=SourceType.MANUAL,
        base_url=HttpUrl("https://www.linkedin.com"),
        description="Professional networking platform.",
        config={"internal_setting": "secret"},
    )

    response = JobSourceResponse.model_validate(source)

    assert response.source_id == "linkedin"
    assert response.name == "LinkedIn"
    assert response.source_type == SourceType.MANUAL
    assert str(response.base_url) == "https://www.linkedin.com/"
    assert response.description == "Professional networking platform."


def test_source_response_excludes_config() -> None:
    """Test that internal source configuration is not exposed."""

    source = JobSource(
        source_id="linkedin",
        name="LinkedIn",
        source_type=SourceType.MANUAL,
        base_url=HttpUrl("https://www.linkedin.com"),
        config={"api_key": "secret"},
    )

    response = JobSourceResponse.model_validate(source)

    assert "config" not in response.model_dump()
    assert "api_key" not in response.model_dump_json()


def test_source_response_json_serialization() -> None:
    """Test JSON serialization and deserialization."""

    source = JobSource(
        source_id="linkedin",
        name="LinkedIn",
        source_type=SourceType.MANUAL,
        base_url=HttpUrl("https://www.linkedin.com"),
    )

    response = JobSourceResponse.model_validate(source)

    restored = JobSourceResponse.model_validate_json(response.model_dump_json())

    assert restored == response
