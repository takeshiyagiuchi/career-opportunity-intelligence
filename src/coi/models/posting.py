"""Data models for individual job postings."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)

from coi.models.enums import (
    EmploymentType,
    PostingStatus,
    SalaryPeriod,
    WorkplaceType,
)


class JobPosting(BaseModel):
    """Represents an individual job posting collected from a source."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    # Identity and source references
    posting_id: UUID = Field(
        default_factory=uuid4,
        description="Unique internal identifier for the posting.",
    )
    source_id: str = Field(
        min_length=1,
        description="Identifier of the source that published the posting.",
    )
    external_id: str | None = Field(
        default=None,
        description="Source-specific identifier for the posting.",
    )
    opportunity_id: UUID | None = Field(
        default=None,
        description="Identifier of the associated canonical job opportunity.",
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
    description: str | None = Field(
        default=None,
        description="Short description or summary of the job posting.",
    )

    # Location and employment
    location: str | None = Field(
        default=None,
        description="Original location description as advertised.",
    )
    employment_type: EmploymentType | None = Field(
        default=None,
        description="Employment arrangement.",
    )
    workplace_type: WorkplaceType | None = Field(
        default=None,
        description="Remote, hybrid, or onsite arrangement.",
    )

    # Compensation
    salary_min: Decimal | None = Field(
        default=None,
        ge=0,
        description="Minimum advertised compensation.",
    )
    salary_max: Decimal | None = Field(
        default=None,
        ge=0,
        description="Maximum advertised compensation.",
    )
    salary_currency: str | None = Field(
        default=None,
        pattern=r"^[A-Z]{3}$",
        description="Three-letter ISO 4217 currency code.",
    )
    salary_period: SalaryPeriod | None = Field(
        default=None,
        description="Payment frequency of the advertised compensation.",
    )
    hours_per_week_min: Decimal | None = Field(
        default=None,
        gt=0,
        le=168,
        description="Minimum expected working hours per week.",
    )
    hours_per_week_max: Decimal | None = Field(
        default=None,
        gt=0,
        le=168,
        description="Maximum expected working hours per week.",
    )

    # URLs
    url: HttpUrl = Field(
        description="Original URL of the job posting.",
    )
    canonical_url: HttpUrl | None = Field(
        default=None,
        description="Normalized URL used for deduplication.",
    )

    # Dates
    published_at: AwareDatetime | None = Field(
        default=None,
        description="Publication timestamp reported by the source.",
    )
    expires_at: AwareDatetime | None = Field(
        default=None,
        description="Expected expiration timestamp of the posting.",
    )
    first_seen_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the posting was first collected.",
    )
    last_seen_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the posting was most recently observed.",
    )

    # Status and language
    status: PostingStatus = Field(
        default=PostingStatus.UNKNOWN,
        description="Current availability status of the posting.",
    )
    language: str | None = Field(
        default=None,
        description="Language of the job posting, preferably a BCP 47 tag.",
    )

    @model_validator(mode="after")
    def validate_ranges(self) -> "JobPosting":
        """Ensure minimum values do not exceed maximum values."""

        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("salary_min cannot exceed salary_max")

        if (
            self.hours_per_week_min is not None
            and self.hours_per_week_max is not None
            and self.hours_per_week_min > self.hours_per_week_max
        ):
            raise ValueError("hours_per_week_min cannot exceed hours_per_week_max")

        if self.last_seen_at < self.first_seen_at:
            raise ValueError("last_seen_at cannot precede first_seen_at")

        return self
