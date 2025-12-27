from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .core.config import settings
from .api import routes_systems, routes_map


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description="EVE Online navigation, routing, and intel visualization API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add GZip compression for responses > 1KB
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Include routers
    app.include_router(routes_systems.router, prefix="/systems", tags=["systems"])
    app.include_router(routes_map.router, prefix="/map", tags=["map"])

    return app


app = create_app()

# Store startup time for uptime calculation
_startup_time: datetime = datetime.now(timezone.utc)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global _startup_time
    _startup_time = datetime.now(timezone.utc)


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for container orchestration.

    Returns:
        Health status including version and uptime.
    """
    uptime = (datetime.now(timezone.utc) - _startup_time).total_seconds()
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime,
    }


@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
