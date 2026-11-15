"""API schemas for job posting extraction."""

from pydantic import BaseModel, ConfigDict, Field

from coi.models.extraction import JobPostingExtraction


class JobPostingExtractionRequest(BaseModel):
    """Request schema for extracting information from a job posting."""

    model_config = ConfigDict(
        str_strip_whitespace=False,
        extra="forbid",
    )

    source_id: str = Field(
        min_length=1,
        description="Identifier of the selected job posting source.",
    )
    content: str = Field(
        min_length=1,
        description="Original full text of the job posting.",
    )


class JobPostingExtractionResponse(BaseModel):
    """Response schema containing extracted job posting information."""

    model_config = ConfigDict(from_attributes=True)

    extracted_data: JobPostingExtraction
