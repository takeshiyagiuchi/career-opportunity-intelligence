from datetime import UTC

import pytest
from pydantic import ValidationError

from coi.models.enums import SourceType
from coi.models.source import JobSource


@pytest.fixture
def valid_source_data():
    """Return valid data for creating a JobSource."""
    return {
        "source_id": "indeed_ca",
        "name": "Indeed Canada",
        "source_type": SourceType.API,
        "base_url": "https://ca.indeed.com",
    }


def test_create_job_source(valid_source_data):
    """Test creating a JobSource with valid data."""
    source = JobSource(**valid_source_data)

    assert source.source_id == "indeed_ca"
    assert source.name == "Indeed Canada"
    assert source.source_type == SourceType.API
    assert str(source.base_url) == "https://ca.indeed.com/"
    assert source.is_active is True
    assert source.config == {}


def test_optional_fields_and_defaults(valid_source_data):
    """Test optional fields and their default values."""
    source = JobSource(**valid_source_data)

    assert source.description is None
    assert source.is_active is True
    assert source.config == {}


def test_whitespace_is_stripped(valid_source_data):
    """Test that leading and trailing whitespace is removed."""
    valid_source_data["source_id"] = "  indeed_ca  "
    valid_source_data["name"] = "  Indeed Canada  "

    source = JobSource(**valid_source_data)

    assert source.source_id == "indeed_ca"
    assert source.name == "Indeed Canada"


@pytest.mark.parametrize("field", ["source_id", "name"])
def test_empty_required_string_is_rejected(valid_source_data, field):
    """Test that empty required strings are rejected."""
    valid_source_data[field] = "   "

    with pytest.raises(ValidationError):
        JobSource(**valid_source_data)


def test_invalid_source_type_is_rejected(valid_source_data):
    """Test that an invalid source type is rejected."""
    valid_source_data["source_type"] = "invalid"

    with pytest.raises(ValidationError):
        JobSource(**valid_source_data)


def test_invalid_url_is_rejected(valid_source_data):
    """Test that an invalid URL is rejected."""
    valid_source_data["base_url"] = "not-a-url"

    with pytest.raises(ValidationError):
        JobSource(**valid_source_data)


def test_extra_fields_are_rejected(valid_source_data):
    """Test that unexpected fields are rejected."""
    valid_source_data["unknown_field"] = "unexpected"

    with pytest.raises(ValidationError):
        JobSource(**valid_source_data)


def test_timestamps_are_timezone_aware(valid_source_data):
    """Test that default timestamps use UTC."""
    source = JobSource(**valid_source_data)

    assert source.created_at.tzinfo == UTC
    assert source.updated_at.tzinfo == UTC


def test_config_is_not_shared_between_instances(valid_source_data):
    """Test that each source has an independent config dictionary."""
    source_a = JobSource(**valid_source_data)
    source_b = JobSource(**valid_source_data)

    source_a.config["region"] = "CA"

    assert source_b.config == {}


def test_json_serialization(valid_source_data):
    """Test JSON serialization and deserialization."""
    source = JobSource(**valid_source_data)

    json_data = source.model_dump_json()
    restored_source = JobSource.model_validate_json(json_data)

    assert restored_source == source
