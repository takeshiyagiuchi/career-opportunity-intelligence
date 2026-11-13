"""Shared enumerations for job-related data models."""

from enum import StrEnum


class SourceType(StrEnum):
    """Supported types of job posting sources."""

    API = "api"
    RSS = "rss"
    WEB_SCRAPING = "web_scraping"
    MANUAL = "manual"


class EmploymentType(StrEnum):
    """Types of employment arrangements."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERNSHIP = "internship"
    VOLUNTEER = "volunteer"
    OTHER = "other"


class WorkplaceType(StrEnum):
    """Workplace arrangements for a job position."""

    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNSPECIFIED = "unspecified"


class SalaryPeriod(StrEnum):
    """Payment frequency associated with a salary."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"
