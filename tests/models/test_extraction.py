"""Tests for AI-based job posting extraction models."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from coi.models.enums import EmploymentType, SalaryPeriod, WorkplaceType
from coi.models.extraction import JobPostingExtraction


@pytest.fixture
def valid_extraction_data() -> dict:
    """Return valid job posting extraction data."""

    return {
        "title": "Software Engineer",
        "company_name": "Example Inc.",
        "location": "Toronto, ON",
        "employment_type": EmploymentType.FULL_TIME,
        "workplace_type": WorkplaceType.HYBRID,
        "salary_min": Decimal("80000"),
        "salary_max": Decimal("100000"),
        "salary_currency": "CAD",
        "salary_period": SalaryPeriod.ANNUAL,
        "hours_per_week_min": Decimal("37.5"),
        "hours_per_week_max": Decimal("40"),
        "url": "https://example.com/jobs/123",
        "field_evidence": {
            "title": "Software Engineer",
            "company_name": "Example Inc.",
            "location": "Toronto, ON",
            "employment_type": "Full-time",
            "workplace_type": "Hybrid",
            "salary_min": "$80,000",
            "salary_max": "$100,000",
            "salary_currency": "CAD",
            "salary_period": "annually",
            "hours_per_week_min": "37.5 hours per week",
            "hours_per_week_max": "40 hours per week",
            "url": "https://example.com/jobs/123",
        },
    }


def test_valid_extraction(valid_extraction_data: dict) -> None:
    """Test creation with valid extraction data."""

    extraction = JobPostingExtraction(**valid_extraction_data)

    assert extraction.title == "Software Engineer"
    assert extraction.company_name == "Example Inc."
    assert extraction.employment_type == EmploymentType.FULL_TIME
    assert extraction.workplace_type == WorkplaceType.HYBRID
    assert extraction.salary_min == Decimal("80000")
    assert extraction.salary_max == Decimal("100000")


def test_empty_extraction() -> None:
    """Test creation when no information could be extracted."""

    extraction = JobPostingExtraction()

    assert extraction.title is None
    assert extraction.company_name is None
    assert extraction.field_evidence == {}
    assert extraction.ambiguous_fields == []
    assert extraction.warnings == []


def test_optional_fields_can_be_missing(
    valid_extraction_data: dict,
) -> None:
    """Test that optional fields can be omitted."""

    valid_extraction_data["field_evidence"] = {
        "title": "Software Engineer",
        "company_name": "Example Inc.",
    }

    valid_extraction_data["title"] = "Software Engineer"
    valid_extraction_data["company_name"] = "Example Inc."

    extraction = JobPostingExtraction(
        title=valid_extraction_data["title"],
        company_name=valid_extraction_data["company_name"],
        field_evidence=valid_extraction_data["field_evidence"],
    )

    assert extraction.title == "Software Engineer"
    assert extraction.location is None
    assert extraction.salary_min is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("salary_min", Decimal("-1")),
        ("salary_max", Decimal("-1")),
        ("hours_per_week_min", Decimal("0")),
        ("hours_per_week_max", Decimal("169")),
        ("applicant_count", -1),
    ],
)
def test_invalid_numeric_values(
    valid_extraction_data: dict,
    field: str,
    value: Decimal | int,
) -> None:
    """Test rejection of invalid numeric values."""

    valid_extraction_data[field] = value

    with pytest.raises(ValidationError):
        JobPostingExtraction(**valid_extraction_data)


def test_salary_min_exceeds_max(
    valid_extraction_data: dict,
) -> None:
    """Test rejection of an invalid salary range."""

    valid_extraction_data["salary_min"] = Decimal("120000")

    with pytest.raises(ValidationError, match="salary_min"):
        JobPostingExtraction(**valid_extraction_data)


def test_hours_min_exceeds_max(
    valid_extraction_data: dict,
) -> None:
    """Test rejection of an invalid working-hours range."""

    valid_extraction_data["hours_per_week_min"] = Decimal("45")

    with pytest.raises(ValidationError, match="hours_per_week_min"):
        JobPostingExtraction(**valid_extraction_data)


def test_invalid_salary_currency(
    valid_extraction_data: dict,
) -> None:
    """Test rejection of an invalid currency format."""

    valid_extraction_data["salary_currency"] = "cad"

    with pytest.raises(ValidationError):
        JobPostingExtraction(**valid_extraction_data)


def test_missing_evidence(
    valid_extraction_data: dict,
) -> None:
    """Test rejection when an extracted value has no evidence."""

    valid_extraction_data["field_evidence"].pop("title")

    with pytest.raises(ValidationError, match="Missing evidence"):
        JobPostingExtraction(**valid_extraction_data)


def test_unknown_evidence_field(
    valid_extraction_data: dict,
) -> None:
    """Test rejection of evidence for an unknown field."""

    valid_extraction_data["field_evidence"]["unknown_field"] = "Some text"

    with pytest.raises(ValidationError, match="Unknown extraction metadata"):
        JobPostingExtraction(**valid_extraction_data)


def test_ambiguous_field(
    valid_extraction_data: dict,
) -> None:
    """Test that ambiguous fields can be represented."""

    valid_extraction_data["field_evidence"].pop("location")
    valid_extraction_data["location"] = None
    valid_extraction_data["ambiguous_fields"] = ["location"]

    extraction = JobPostingExtraction(**valid_extraction_data)

    assert "location" in extraction.ambiguous_fields
    assert extraction.location is None


def test_ambiguous_field_with_value(
    valid_extraction_data: dict,
) -> None:
    """Test rejection when an ambiguous field also has a value."""

    valid_extraction_data["ambiguous_fields"] = ["title"]

    with pytest.raises(ValidationError, match="both extracted evidence"):
        JobPostingExtraction(**valid_extraction_data)


def test_empty_evidence(
    valid_extraction_data: dict,
) -> None:
    """Test rejection of empty evidence snippets."""

    valid_extraction_data["field_evidence"]["title"] = "   "

    with pytest.raises(ValidationError, match="Evidence snippets"):
        JobPostingExtraction(**valid_extraction_data)


def test_extra_fields_are_forbidden(
    valid_extraction_data: dict,
) -> None:
    """Test rejection of unexpected fields."""

    valid_extraction_data["posting_id"] = "123"

    with pytest.raises(ValidationError):
        JobPostingExtraction(**valid_extraction_data)


def test_json_serialization(
    valid_extraction_data: dict,
) -> None:
    """Test JSON serialization and deserialization."""

    extraction = JobPostingExtraction(**valid_extraction_data)

    json_data = extraction.model_dump_json()
    restored = JobPostingExtraction.model_validate_json(json_data)

    assert restored == extraction
