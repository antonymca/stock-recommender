"""Minimal FastAPI application exposing the screening endpoint."""

from fastapi import FastAPI

from .routers import screen

app = FastAPI(title="Stock Recommender API")
app.include_router(screen.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple health check used by tests."""

    return {"status": "ok"}
