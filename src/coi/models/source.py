"""Data models for job posting sources."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from coi.models.enums import SourceType


class JobSource(BaseModel):
    """Represents a source from which job postings are collected."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    source_id: str = Field(
        min_length=1,
        description="Unique identifier for the job source.",
    )
    name: str = Field(
        min_length=1,
        description="Human-readable name of the source.",
    )
    source_type: SourceType = Field(
        description="Type of the job posting source.",
    )
    base_url: HttpUrl = Field(
        description="Base URL of the source.",
    )
    is_active: bool = Field(
        default=True,
        description="Whether ingestion from this source is enabled.",
    )
    description: str | None = Field(
        default=None,
        description="Optional description of the source.",
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Source-specific configuration.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the source was registered.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the source was last updated.",
    )
