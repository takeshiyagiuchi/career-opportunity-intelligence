"""Tests for the JobPosting model."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from coi.models.enums import EmploymentType, SalaryPeriod, WorkplaceType
from coi.models.posting import JobPosting


@pytest.fixture
def valid_posting_data() -> dict:
    """Return valid data for creating a JobPosting."""

    return {
        "source_id": "linkedin",
        "title": "Machine Learning Engineer",
        "company_name": "Example Inc.",
        "url": "https://example.com/jobs/123",
    }


def test_create_posting_with_required_fields(valid_posting_data: dict) -> None:
    """Test creating a posting with only required fields."""

    posting = JobPosting(**valid_posting_data)

    assert posting.source_id == "linkedin"
    assert posting.title == "Machine Learning Engineer"
    assert posting.company_name == "Example Inc."
    assert str(posting.url) == "https://example.com/jobs/123"


def test_posting_id_is_generated_automatically(
    valid_posting_data: dict,
) -> None:
    """Test that a UUID is generated when posting_id is omitted."""

    posting = JobPosting(**valid_posting_data)

    assert isinstance(posting.posting_id, UUID)


def test_posting_id_can_be_provided(valid_posting_data: dict) -> None:
    """Test creating a posting with a specified UUID."""

    posting_id = UUID("12345678-1234-5678-1234-567812345678")
    posting = JobPosting(**valid_posting_data, posting_id=posting_id)

    assert posting.posting_id == posting_id


@pytest.mark.parametrize(
    "missing_field",
    ["source_id", "title", "company_name", "url"],
)
def test_required_fields_are_enforced(
    valid_posting_data: dict,
    missing_field: str,
) -> None:
    """Test that required fields cannot be omitted."""

    data = valid_posting_data.copy()
    del data[missing_field]

    with pytest.raises(ValidationError):
        JobPosting(**data)


@pytest.mark.parametrize("field", ["source_id", "title", "company_name"])
def test_required_string_fields_cannot_be_empty(
    valid_posting_data: dict,
    field: str,
) -> None:
    """Test that required string fields cannot be empty."""

    valid_posting_data[field] = ""

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


def test_optional_fields_default_to_none(valid_posting_data: dict) -> None:
    """Test that optional fields default to None."""

    posting = JobPosting(**valid_posting_data)

    optional_fields = [
        "content",
        "location",
        "employment_type",
        "workplace_type",
        "salary_min",
        "salary_max",
        "salary_currency",
        "salary_period",
        "hours_per_week_min",
        "hours_per_week_max",
        "applicant_count",
        "is_reposted",
        "published_at",
        "expires_at",
        "language",
    ]

    for field in optional_fields:
        assert getattr(posting, field) is None


def test_content_can_be_provided(valid_posting_data: dict) -> None:
    """Test storing full job posting content."""

    content = "Responsibilities: Develop and maintain machine learning models."

    posting = JobPosting(**valid_posting_data, content=content)

    assert posting.content == content


def test_content_can_be_none(valid_posting_data: dict) -> None:
    """Test that content is optional."""

    posting = JobPosting(**valid_posting_data, content=None)

    assert posting.content is None


def test_content_cannot_be_empty(valid_posting_data: dict) -> None:
    """Test that provided content cannot be empty."""

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data, content="")


def test_whitespace_is_stripped(valid_posting_data: dict) -> None:
    """Test that surrounding whitespace is stripped from strings."""

    valid_posting_data["title"] = "  Machine Learning Engineer  "
    valid_posting_data["company_name"] = "  Example Inc.  "

    posting = JobPosting(**valid_posting_data)

    assert posting.title == "Machine Learning Engineer"
    assert posting.company_name == "Example Inc."


def test_enums_are_validated(valid_posting_data: dict) -> None:
    """Test employment and workplace enum validation."""

    posting = JobPosting(
        **valid_posting_data,
        employment_type=EmploymentType.FULL_TIME,
        workplace_type=WorkplaceType.REMOTE,
        salary_period=SalaryPeriod.ANNUAL,
    )

    assert posting.employment_type == EmploymentType.FULL_TIME
    assert posting.workplace_type == WorkplaceType.REMOTE
    assert posting.salary_period == SalaryPeriod.ANNUAL


def test_invalid_enum_value_is_rejected(
    valid_posting_data: dict,
) -> None:
    """Test that invalid enum values are rejected."""

    data = valid_posting_data.copy()
    data["employment_type"] = "permanent"

    with pytest.raises(ValidationError):
        JobPosting.model_validate(data)


def test_salary_values_are_validated(valid_posting_data: dict) -> None:
    """Test valid salary values."""

    posting = JobPosting(
        **valid_posting_data,
        salary_min=Decimal("80000"),
        salary_max=Decimal("120000"),
        salary_currency="CAD",
        salary_period=SalaryPeriod.ANNUAL,
    )

    assert posting.salary_min == Decimal("80000")
    assert posting.salary_max == Decimal("120000")
    assert posting.salary_currency == "CAD"


@pytest.mark.parametrize(
    ("salary_min", "salary_max"),
    [
        (Decimal("120000"), Decimal("80000")),
        (Decimal("-1"), Decimal("80000")),
        (Decimal("80000"), Decimal("-1")),
    ],
)
def test_invalid_salary_values_are_rejected(
    valid_posting_data: dict,
    salary_min: Decimal,
    salary_max: Decimal,
) -> None:
    """Test that invalid salary ranges are rejected."""

    with pytest.raises(ValidationError):
        JobPosting(
            **valid_posting_data,
            salary_min=salary_min,
            salary_max=salary_max,
        )


def test_invalid_salary_currency_is_rejected(
    valid_posting_data: dict,
) -> None:
    """Test that currency must use three uppercase letters."""

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data, salary_currency="cad")


def test_weekly_hours_are_validated(valid_posting_data: dict) -> None:
    """Test valid weekly working hours."""

    posting = JobPosting(
        **valid_posting_data,
        hours_per_week_min=Decimal("30"),
        hours_per_week_max=Decimal("40"),
    )

    assert posting.hours_per_week_min == Decimal("30")
    assert posting.hours_per_week_max == Decimal("40")


def test_invalid_weekly_hours_are_rejected(
    valid_posting_data: dict,
) -> None:
    """Test invalid weekly working hours."""

    with pytest.raises(ValidationError):
        JobPosting(
            **valid_posting_data,
            hours_per_week_min=Decimal("45"),
            hours_per_week_max=Decimal("35"),
        )


@pytest.mark.parametrize(
    "hours",
    [Decimal("0"), Decimal("-1"), Decimal("169")],
)
def test_weekly_hours_outside_valid_range_are_rejected(
    valid_posting_data: dict,
    hours: Decimal,
) -> None:
    """Test that weekly hours must be greater than zero and at most 168."""

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data, hours_per_week_min=hours)


@pytest.mark.parametrize("applicant_count", [0, 1, 100, 1000])
def test_applicant_count_accepts_non_negative_integers(
    valid_posting_data: dict,
    applicant_count: int,
) -> None:
    """Test valid applicant counts."""

    posting = JobPosting(
        **valid_posting_data,
        applicant_count=applicant_count,
    )

    assert posting.applicant_count == applicant_count


def test_negative_applicant_count_is_rejected(
    valid_posting_data: dict,
) -> None:
    """Test that negative applicant counts are rejected."""

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data, applicant_count=-1)


@pytest.mark.parametrize("is_reposted", [True, False, None])
def test_is_reposted_accepts_all_states(
    valid_posting_data: dict,
    is_reposted: bool | None,
) -> None:
    """Test reposting information, including unknown state."""

    posting = JobPosting(
        **valid_posting_data,
        is_reposted=is_reposted,
    )

    assert posting.is_reposted is is_reposted


@pytest.mark.parametrize(
    "timestamp",
    [
        datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        None,
    ],
)
def test_publication_timestamp_accepts_valid_values(
    valid_posting_data: dict,
    timestamp: datetime | None,
) -> None:
    """Test publication timestamps."""

    posting = JobPosting(**valid_posting_data, published_at=timestamp)

    assert posting.published_at == timestamp


def test_naive_datetime_is_rejected(valid_posting_data: dict) -> None:
    """Test that timestamps must include timezone information."""

    with pytest.raises(ValidationError):
        JobPosting(
            **valid_posting_data,
            published_at=datetime(2026, 1, 1, 12, 0),
        )


def test_first_seen_at_is_timezone_aware(
    valid_posting_data: dict,
) -> None:
    """Test that first_seen_at is automatically timezone-aware."""

    posting = JobPosting(**valid_posting_data)

    assert posting.first_seen_at.tzinfo is not None
    assert posting.first_seen_at.utcoffset() is not None


def test_url_validation(valid_posting_data: dict) -> None:
    """Test that invalid URLs are rejected."""

    valid_posting_data["url"] = "not-a-valid-url"

    with pytest.raises(ValidationError):
        JobPosting(**valid_posting_data)


def test_extra_fields_are_rejected(valid_posting_data: dict) -> None:
    """Test that fields not defined in the model are rejected."""

    data = valid_posting_data.copy()
    data["unknown_field"] = "unexpected"

    with pytest.raises(ValidationError):
        JobPosting.model_validate(data)


def test_json_serialization(valid_posting_data: dict) -> None:
    """Test JSON serialization and deserialization."""

    posting = JobPosting(
        **valid_posting_data,
        applicant_count=25,
        is_reposted=True,
        salary_min=Decimal("80000"),
        salary_currency="CAD",
    )

    serialized = posting.model_dump_json()
    deserialized = JobPosting.model_validate_json(serialized)

    assert deserialized == posting
