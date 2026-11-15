"""Tests for job posting extraction API schemas."""

import pytest
from pydantic import ValidationError

from coi.models.extraction import JobPostingExtraction
from coi.schemas.extraction import (
    JobPostingExtractionRequest,
    JobPostingExtractionResponse,
)


def test_valid_extraction_request() -> None:
    """Test creation of a valid extraction request."""

    request = JobPostingExtractionRequest(
        source_id="linkedin",
        content="Software Engineer at Example Inc.",
    )

    assert request.source_id == "linkedin"
    assert request.content == "Software Engineer at Example Inc."


def test_extraction_request_preserves_original_content() -> None:
    """Test that the original content is preserved exactly."""

    original_content = "\n  Software Engineer at Example Inc.  \n"

    request = JobPostingExtractionRequest(
        source_id="linkedin",
        content=original_content,
    )

    assert request.content == original_content


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"content": "Software Engineer"},
        {"source_id": "linkedin"},
    ],
)
def test_invalid_extraction_request(data: dict) -> None:
    """Test rejection of requests with missing required fields."""

    with pytest.raises(ValidationError):
        JobPostingExtractionRequest(**data)


def test_empty_extraction_content() -> None:
    """Test rejection of empty extraction content."""

    with pytest.raises(ValidationError):
        JobPostingExtractionRequest(
            source_id="linkedin",
            content="",
        )


def test_extraction_request_rejects_extra_fields() -> None:
    """Test rejection of unexpected request fields."""

    with pytest.raises(ValidationError):
        JobPostingExtractionRequest.model_validate(
            {
                "source_id": "linkedin",
                "content": "Software Engineer",
                "unexpected_field": "value",
            }
        )


def test_valid_extraction_response() -> None:
    """Test creation of an extraction response."""

    extraction = JobPostingExtraction(
        title="Software Engineer",
        company_name="Example Inc.",
        field_evidence={
            "title": "Software Engineer",
            "company_name": "Example Inc.",
        },
    )

    response = JobPostingExtractionResponse(
        extracted_data=extraction,
    )

    assert response.extracted_data.title == "Software Engineer"
    assert response.extracted_data.company_name == "Example Inc."


def test_extraction_response_json_serialization() -> None:
    """Test JSON serialization and deserialization."""

    response = JobPostingExtractionResponse(
        extracted_data=JobPostingExtraction(
            title="Software Engineer",
            field_evidence={
                "title": "Software Engineer",
            },
        ),
    )

    restored = JobPostingExtractionResponse.model_validate_json(
        response.model_dump_json()
    )

    assert restored == response
