"""FastAPI application entry point."""

from fastapi import FastAPI

from coi.api.v1.router import router as v1_router

app = FastAPI(
    title="Career Opportunity Intelligence API",
    description=(
        "An API for collecting, analyzing, and exploring career opportunities."
    ),
    version="0.1.0",
)

app.include_router(v1_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return the application health status."""

    return {"status": "ok"}
