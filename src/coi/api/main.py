"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="Career Opportunity Intelligence API",
    description=(
        "An API for collecting, analyzing, and exploring career opportunities."
    ),
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Return the application health status."""

    return {"status": "ok"}
