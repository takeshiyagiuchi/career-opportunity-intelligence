"""Repository for job posting sources."""

from pydantic import HttpUrl

from coi.models.enums import SourceType
from coi.models.source import JobSource


class SourceRepository:
    """In-memory repository for job posting sources."""

    def __init__(self) -> None:
        """Initialize the repository with default sources."""

        self._sources = [
            JobSource(
                source_id="linkedin",
                name="LinkedIn",
                source_type=SourceType.MANUAL,
                base_url=HttpUrl("https://www.linkedin.com"),
                description="Professional networking platform.",
            ),
            JobSource(
                source_id="indeed",
                name="Indeed",
                source_type=SourceType.MANUAL,
                base_url=HttpUrl("https://www.indeed.com"),
                description="Job search platform.",
            ),
            JobSource(
                source_id="company_website",
                name="Company Website",
                source_type=SourceType.MANUAL,
                base_url=HttpUrl("https://example.com"),
                description="Company career pages.",
            ),
            JobSource(
                source_id="other",
                name="Other",
                source_type=SourceType.MANUAL,
                base_url=HttpUrl("https://example.com"),
                description="Other job posting sources.",
            ),
        ]

    def get_all(self) -> list[JobSource]:
        """Return all registered sources."""

        return self._sources.copy()
