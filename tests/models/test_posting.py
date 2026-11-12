from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from coi.models.enums import (
    EmploymentType,
    PostingStatus,
    SalaryPeriod,
    WorkplaceType,
)
from coi.models.posting import JobPosting


@pytest.fixture
def valid_posting_data():
    """Return valid data for creating a JobPosting."""
    return {
        "source_id": "company_careers",
        "title": "Machine Learning Engineer",
        "company_name": "Example Inc.",
        "url": "https://example.com/careers/ml-engineer",
    }


def test_create_job_posting(valid_posting_data):
    """Test creating a JobPosting with minimal valid data."""
    posting = JobPosting(**valid_posting_data)

    assert isinstance(posting.posting_id, UUID)
    assert posting.source_id == "company_careers"
    assert posting.title == "Machine Learning Engineer"
    assert posting.company_name == "Example Inc."
    assert posting.status == PostingStatus.UNKNOWN
    assert posting.salary_min is None
    assert posting.hours_per_week_min is None


def test_default_identifiers_are_unique(valid_posting_data):
    """Test that separate postings receive different identifiers."""
    posting_a = JobPosting(**valid_posting_data)
    posting_b = JobPosting(**valid_posting_data)

    assert posting_a.posting_id != posting_b.posting_id


def test_optional_fields_and_enums(valid_posting_data):
    """Test optional fields and enum values."""
    valid_posting_data.update(
        {
            "employment_type": EmploymentType.FULL_TIME,
            "workplace_type": WorkplaceType.REMOTE,
            "status": PostingStatus.ACTIVE,
            "language": "en-CA",
        }
    )

    posting = JobPosting(**valid_posting_data)

    assert posting.employment_type == EmploymentType.FULL_TIME
    assert posting.workplace_type == WorkplaceType.REMOTE
    assert posting.status == PostingStatus.ACTIVE
    assert posting.language == "en-CA"


def test_compensation_fields(valid_posting_data):
    """Test salary and working-hour fields."""
    valid_posting_data.update(
        {
            "salary_min": Decimal("1500"),
            "salary_max": Decimal("2000"),
            "salary_currency": "CAD",
            "salary_period": SalaryPeriod.WEEKLY,
            "hours_per_week_min": Decimal("30"),
            "hours_per_week_max": Decimal("40"),
        }
    )

    posting = JobPosting(**valid_posting_data)

    assert posting.salary_min == Decimal("1500")
    assert posting.salary_max == Decimal("2000")
    assert posting.salary_currency == "CAD"
    assert posting.salary_period == SalaryPeriod.WEEKLY
    assert posting.hours_per_week_min == Decimal("30")
    assert posting.hours_per_week_max == Decimal("40")


def test_salary_min_greater_than_max_is_rejected(valid_posting_data):
    """Test that minimum salary cannot exceed maximum salary."""
    valid_posting_data.update(
        {
            "salary_min": Decimal("2000"),
            "salary_max": Decimal("1500"),
        }
    )

    with pytest.raises(ValidationError, match="salary_min"):
        JobPosting(**valid_posting_data)


def test_hours_min_greater_than_max_is_rejected(valid_posting_data):
    """Test that minimum working hours cannot exceed maximum hours."""
    valid_posting_data.update(
        {
            "hours_per_week_min": Decimal("40"),
            "hours_per_week_max": Decimal("30"),
        }
    )

    with pytest.raises(ValidationError, match="hours_per_week_min"):
        JobPosting(**valid_posting_data)


@pytest.mark.parametrize(
    "field",
    ["salary_min", "salary_max"],
)
def test_negative_salary_is_rejected(valid_posting_data, field):
    """Test that negative salary values are rejected."""
    valid_posting_data[field] = Decimal("-100")

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


@pytest.mark.parametrize(
    "field",
    ["hours_per_week_min", "hours_per_week_max"],
)
def test_invalid_weekly_hours_are_rejected(valid_posting_data, field):
    """Test that zero, negative, and excessive weekly hours are rejected."""
    for value in (
        Decimal("0"),
        Decimal("-1"),
        Decimal("169"),
    ):
        valid_posting_data[field] = value

        with pytest.raises(ValidationError):
            JobPosting(**valid_posting_data)


@pytest.mark.parametrize(
    "currency",
    ["cad", "CA", "CADD", "123"],
)
def test_invalid_currency_format_is_rejected(valid_posting_data, currency):
    """Test that currency codes must contain three uppercase letters."""
    valid_posting_data["salary_currency"] = currency

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


def test_invalid_url_is_rejected(valid_posting_data):
    """Test that an invalid posting URL is rejected."""
    valid_posting_data["url"] = "not-a-url"

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


def test_naive_datetime_is_rejected(valid_posting_data):
    """Test that timestamps without timezone information are rejected."""
    valid_posting_data["published_at"] = datetime(2026, 1, 1)

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


def test_last_seen_before_first_seen_is_rejected(valid_posting_data):
    """Test that observation timestamps are chronologically valid."""
    valid_posting_data.update(
        {
            "first_seen_at": datetime(2026, 1, 2, tzinfo=UTC),
            "last_seen_at": datetime(2026, 1, 1, tzinfo=UTC),
        }
    )

    with pytest.raises(ValidationError, match="last_seen_at"):
        JobPosting(**valid_posting_data)


def test_whitespace_is_stripped(valid_posting_data):
    """Test that whitespace is stripped from string fields."""
    valid_posting_data["title"] = "  Data Scientist  "
    valid_posting_data["company_name"] = "  Example Inc.  "

    posting = JobPosting(**valid_posting_data)

    assert posting.title == "Data Scientist"
    assert posting.company_name == "Example Inc."


def test_extra_fields_are_rejected(valid_posting_data):
    """Test that unexpected fields are rejected."""
    valid_posting_data["unknown_field"] = "unexpected"

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


def test_json_serialization(valid_posting_data):
    """Test JSON serialization and deserialization."""
    valid_posting_data.update(
        {
            "salary_min": Decimal("80000"),
            "salary_currency": "CAD",
            "salary_period": SalaryPeriod.ANNUAL,
            "hours_per_week_min": Decimal("37.5"),
        }
    )

    posting = JobPosting(**valid_posting_data)

    json_data = posting.model_dump_json()
    restored_posting = JobPosting.model_validate_json(json_data)

    assert restored_posting == posting
    assert restored_posting.salary_min == Decimal("80000")
    assert restored_posting.hours_per_week_min == Decimal("37.5")
