"""Version 1 API router."""

from fastapi import APIRouter

from coi.api.v1.routes.sources import router as sources_router

router = APIRouter(prefix="/api/v1")

router.include_router(sources_router)
