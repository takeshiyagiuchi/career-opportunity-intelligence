"""API schemas for job posting registration."""

from decimal import Decimal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl

from coi.models.enums import (
    EmploymentType,
    SalaryPeriod,
    WorkplaceType,
)


class JobPostingCreateRequest(BaseModel):
    """Request schema for registering a reviewed job posting."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    # Source
    source_id: str = Field(
        min_length=1,
        description="Identifier of the source that published the posting.",
    )

    # Basic information
    title: str = Field(
        min_length=1,
        description="Job title as advertised.",
    )
    company_name: str = Field(
        min_length=1,
        description="Name of the hiring organization.",
    )
    content: str = Field(
        min_length=1,
        description="Original full text of the job posting.",
    )

    # Location and employment
    location: str | None = None
    employment_type: EmploymentType | None = None
    workplace_type: WorkplaceType | None = None

    # Compensation
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(
        default=None,
        pattern=r"^[A-Z]{3}$",
    )
    salary_period: SalaryPeriod | None = None

    # Working hours
    hours_per_week_min: Decimal | None = Field(
        default=None,
        gt=0,
        le=168,
    )
    hours_per_week_max: Decimal | None = Field(
        default=None,
        gt=0,
        le=168,
    )

    # Additional information
    applicant_count: int | None = Field(default=None, ge=0)
    is_reposted: bool | None = None

    # Application information
    url: HttpUrl

    # Dates
    published_at: AwareDatetime | None = None
    expires_at: AwareDatetime | None = None

    # Language
    language: str | None = None

    from pydantic import model_validator

    @model_validator(mode="after")
    def validate_ranges(self) -> "JobPostingCreateRequest":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot exceed salary_max.")

        if (
            self.hours_per_week_min is not None
            and self.hours_per_week_max is not None
            and self.hours_per_week_min > self.hours_per_week_max
        ):
            raise ValueError("hours_per_week_min cannot exceed hours_per_week_max.")

        return self


class JobPostingResponse(BaseModel):
    """Response schema for a registered job posting."""

    model_config = ConfigDict(from_attributes=True)

    posting_id: UUID
    source_id: str
    title: str
    company_name: str
    content: str
    location: str | None
    employment_type: EmploymentType | None
    workplace_type: WorkplaceType | None
    salary_min: Decimal | None
    salary_max: Decimal | None
    salary_currency: str | None
    salary_period: SalaryPeriod | None
    hours_per_week_min: Decimal | None
    hours_per_week_max: Decimal | None
    applicant_count: int | None
    is_reposted: bool | None
    url: HttpUrl
    published_at: AwareDatetime | None
    expires_at: AwareDatetime | None
    first_seen_at: AwareDatetime
    language: str | None
