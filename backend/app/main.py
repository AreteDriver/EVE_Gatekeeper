"""EVE Gatekeeper API - Main Application."""

from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .core.config import settings
from .api import routes_systems, routes_map
from .api.v1 import router as v1_router
from .api.v1.status import set_start_time
from .middleware import (
    setup_rate_limiting,
    SecurityHeadersMiddleware,
    RequestContextMiddleware,
)
from .middleware.security import RequestSizeLimitMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description="EVE Online navigation, routing, and intel visualization API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {"name": "health", "description": "Health check endpoints"},
            {"name": "systems", "description": "System information and risk data"},
            {"name": "routing", "description": "Route calculation and map configuration"},
            {"name": "status", "description": "API status and diagnostics"},
        ],
    )

    # ==========================================================================
    # Middleware (order matters - first added = outermost)
    # ==========================================================================

    # Request size limit (10MB)
    app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request context (request ID, timing)
    app.add_middleware(RequestContextMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )

    # GZip compression for responses > 1KB
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Rate limiting
    setup_rate_limiting(app)

    # ==========================================================================
    # Routers
    # ==========================================================================

    # API v1 routes (new versioned API)
    app.include_router(v1_router)

    # Legacy routes (for backward compatibility)
    app.include_router(routes_systems.router, prefix="/systems", tags=["systems"])
    app.include_router(routes_map.router, prefix="/map", tags=["routing"])

    return app


app = create_app()

# Store startup time for uptime calculation
_startup_time: datetime = datetime.now(timezone.utc)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global _startup_time
    _startup_time = datetime.now(timezone.utc)
    set_start_time(_startup_time)

    # Start zKillboard listener for real-time kill feed
    from .services.zkill_listener import get_zkill_listener
    listener = get_zkill_listener()
    await listener.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    # Stop zKillboard listener
    from .services.zkill_listener import get_zkill_listener
    listener = get_zkill_listener()
    await listener.stop()

    # Close database connections
    from .db.database import close_db
    await close_db()


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for container orchestration.

    Returns basic health status. For detailed status, use /api/v1/status.
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
        "api": "/api/v1",
        "status": "/api/v1/status",
    }
