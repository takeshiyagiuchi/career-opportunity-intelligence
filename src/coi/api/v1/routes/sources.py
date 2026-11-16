"""API routes for job posting sources."""

from fastapi import APIRouter

from coi.repositories.source import SourceRepository
from coi.schemas.source import JobSourceResponse

router = APIRouter(prefix="/sources", tags=["Sources"])

source_repository = SourceRepository()


@router.get("", response_model=list[JobSourceResponse])
async def get_sources() -> list[JobSourceResponse]:
    """Return all available job posting sources."""

    return [
        JobSourceResponse.model_validate(source)
        for source in source_repository.get_all()
    ]
