"""API schemas for job posting sources."""

from pydantic import BaseModel, ConfigDict, HttpUrl

from coi.models.enums import SourceType


class JobSourceResponse(BaseModel):
    """Response schema for a job posting source."""

    model_config = ConfigDict(from_attributes=True)

    source_id: str
    name: str
    source_type: SourceType
    base_url: HttpUrl
    description: str | None
