"""Tests for job posting registration API schemas."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from coi.models.enums import (
    EmploymentType,
    SalaryPeriod,
    WorkplaceType,
)
from coi.models.posting import JobPosting
from coi.schemas.posting import (
    JobPostingCreateRequest,
    JobPostingResponse,
)


@pytest.fixture
def valid_posting_data() -> dict:
    """Return valid job posting registration data."""

    return {
        "source_id": "linkedin",
        "title": "Software Engineer",
        "company_name": "Example Inc.",
        "content": "Original job posting content.",
        "location": "Toronto, ON",
        "employment_type": EmploymentType.FULL_TIME,
        "workplace_type": WorkplaceType.HYBRID,
        "salary_min": Decimal("80000"),
        "salary_max": Decimal("100000"),
        "salary_currency": "CAD",
        "salary_period": SalaryPeriod.ANNUAL,
        "hours_per_week_min": Decimal("37.5"),
        "hours_per_week_max": Decimal("40"),
        "applicant_count": 25,
        "is_reposted": False,
        "url": "https://example.com/jobs/123",
        "published_at": datetime(2026, 10, 1, tzinfo=UTC),
        "expires_at": None,
        "language": "en",
    }


def test_valid_posting_request(valid_posting_data: dict) -> None:
    """Test creation of a valid posting request."""

    request = JobPostingCreateRequest(**valid_posting_data)

    assert request.source_id == "linkedin"
    assert request.title == "Software Engineer"
    assert request.salary_min == Decimal("80000")
    assert request.salary_max == Decimal("100000")


def test_missing_required_fields() -> None:
    """Test rejection of a request missing required fields."""

    with pytest.raises(ValidationError):
        JobPostingCreateRequest()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_id", ""),
        ("title", ""),
        ("company_name", ""),
        ("content", ""),
        ("salary_min", Decimal("-1")),
        ("salary_max", Decimal("-1")),
        ("hours_per_week_min", Decimal("0")),
        ("hours_per_week_max", Decimal("169")),
        ("applicant_count", -1),
    ],
)
def test_invalid_field_values(
    valid_posting_data: dict,
    field: str,
    value: Decimal | int | str,
) -> None:
    """Test rejection of invalid field values."""

    valid_posting_data[field] = value

    with pytest.raises(ValidationError):
        JobPostingCreateRequest(**valid_posting_data)


def test_invalid_salary_range(valid_posting_data: dict) -> None:
    """Test rejection of an invalid salary range."""

    valid_posting_data["salary_min"] = Decimal("120000")

    with pytest.raises(ValidationError, match="salary_min"):
        JobPostingCreateRequest(**valid_posting_data)


def test_invalid_working_hours_range(valid_posting_data: dict) -> None:
    """Test rejection of an invalid working-hours range."""

    valid_posting_data["hours_per_week_min"] = Decimal("45")

    with pytest.raises(ValidationError, match="hours_per_week_min"):
        JobPostingCreateRequest(**valid_posting_data)


def test_naive_published_at_is_rejected(
    valid_posting_data: dict,
) -> None:
    """Test rejection of a timezone-naive publication timestamp."""

    valid_posting_data["published_at"] = datetime(2026, 10, 1)

    with pytest.raises(ValidationError):
        JobPostingCreateRequest(**valid_posting_data)


def test_server_generated_fields_are_rejected(
    valid_posting_data: dict,
) -> None:
    """Test rejection of server-generated fields in requests."""

    valid_posting_data["posting_id"] = str(uuid4())

    with pytest.raises(ValidationError):
        JobPostingCreateRequest(**valid_posting_data)


def test_request_to_domain_model(
    valid_posting_data: dict,
) -> None:
    """Test conversion from API request to domain model."""

    request = JobPostingCreateRequest(**valid_posting_data)

    posting = JobPosting(**request.model_dump())

    assert posting.source_id == request.source_id
    assert posting.title == request.title
    assert posting.content == request.content
    assert posting.posting_id is not None
    assert posting.first_seen_at.tzinfo is not None


def test_valid_posting_response(
    valid_posting_data: dict,
) -> None:
    """Test creation of a posting response from a domain model."""

    posting = JobPosting(**valid_posting_data)

    response = JobPostingResponse.model_validate(posting)

    assert response.posting_id == posting.posting_id
    assert response.title == posting.title
    assert response.first_seen_at == posting.first_seen_at


def test_posting_response_json_serialization(
    valid_posting_data: dict,
) -> None:
    """Test JSON serialization and deserialization."""

    posting = JobPosting(**valid_posting_data)

    response = JobPostingResponse.model_validate(posting)

    restored = JobPostingResponse.model_validate_json(response.model_dump_json())

    assert restored == response
