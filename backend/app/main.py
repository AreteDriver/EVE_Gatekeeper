"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.api import routes_systems, routes_map

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="EVE Online map visualization backend with risk-aware routing"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_systems.router, prefix="/systems", tags=["systems"])
app.include_router(routes_map.router, prefix="/map", tags=["map"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
