"""Data models for AI-based job posting extraction."""

from decimal import Decimal

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
    SalaryPeriod,
    WorkplaceType,
)


class JobPostingExtraction(BaseModel):
    """Represents potentially incomplete information extracted from a job posting."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    # Basic information
    title: str | None = Field(
        default=None,
        min_length=1,
        description="Extracted job title.",
    )
    company_name: str | None = Field(
        default=None,
        min_length=1,
        description="Extracted name of the hiring organization.",
    )
    location: str | None = Field(
        default=None,
        min_length=1,
        description="Extracted job location.",
    )

    # Employment
    employment_type: EmploymentType | None = Field(
        default=None,
        description="Extracted employment arrangement.",
    )
    workplace_type: WorkplaceType | None = Field(
        default=None,
        description="Extracted workplace arrangement.",
    )

    # Compensation
    salary_min: Decimal | None = Field(
        default=None,
        ge=0,
        description="Extracted minimum salary.",
    )
    salary_max: Decimal | None = Field(
        default=None,
        ge=0,
        description="Extracted maximum salary.",
    )
    salary_currency: str | None = Field(
        default=None,
        pattern=r"^[A-Z]{3}$",
        description="Extracted three-letter currency code.",
    )
    salary_period: SalaryPeriod | None = Field(
        default=None,
        description="Extracted salary payment frequency.",
    )

    # Working hours
    hours_per_week_min: Decimal | None = Field(
        default=None,
        gt=0,
        le=168,
        description="Extracted minimum weekly working hours.",
    )
    hours_per_week_max: Decimal | None = Field(
        default=None,
        gt=0,
        le=168,
        description="Extracted maximum weekly working hours.",
    )

    # Additional information
    applicant_count: int | None = Field(
        default=None,
        ge=0,
        description="Extracted applicant count.",
    )
    is_reposted: bool | None = Field(
        default=None,
        description="Whether the source identifies the posting as reposted.",
    )

    # Application information
    url: HttpUrl | None = Field(
        default=None,
        description="Extracted URL of the job posting.",
    )

    # Dates
    published_at: AwareDatetime | None = Field(
        default=None,
        description="Extracted publication timestamp.",
    )
    expires_at: AwareDatetime | None = Field(
        default=None,
        description="Extracted expiration timestamp.",
    )

    # Language
    language: str | None = Field(
        default=None,
        min_length=1,
        description="Detected language of the job posting.",
    )

    # Extraction metadata
    field_evidence: dict[str, str] = Field(
        default_factory=dict,
        description="Original text supporting extracted field values.",
    )
    ambiguous_fields: list[str] = Field(
        default_factory=list,
        description="Names of fields whose values could not be determined reliably.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Additional extraction warnings.",
    )

    @model_validator(mode="after")
    def validate_ranges(self) -> "JobPostingExtraction":
        """Validate extracted numeric ranges."""

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

    @model_validator(mode="after")
    def validate_extraction_metadata(self) -> "JobPostingExtraction":
        """Validate extraction evidence and ambiguity metadata."""

        valid_fields = set(JobPostingExtraction.model_fields) - {
            "field_evidence",
            "ambiguous_fields",
            "warnings",
        }

        evidence_fields = set(self.field_evidence)
        ambiguous_fields = set(self.ambiguous_fields)

        unknown_fields = (evidence_fields | ambiguous_fields) - valid_fields

        if unknown_fields:
            raise ValueError(
                f"Unknown extraction metadata fields: {sorted(unknown_fields)}"
            )

        missing_evidence = {
            field_name
            for field_name, value in self.model_dump(
                exclude={
                    "field_evidence",
                    "ambiguous_fields",
                    "warnings",
                }
            ).items()
            if value is not None and field_name not in evidence_fields
        }

        if missing_evidence:
            raise ValueError(
                f"Missing evidence for extracted fields: {sorted(missing_evidence)}"
            )

        conflicting_fields = evidence_fields & ambiguous_fields

        if conflicting_fields:
            raise ValueError(
                "Fields cannot have both extracted evidence and ambiguity "
                f"markers: {sorted(conflicting_fields)}"
            )

        if any(not evidence.strip() for evidence in self.field_evidence.values()):
            raise ValueError("Evidence snippets cannot be empty.")

        return self
