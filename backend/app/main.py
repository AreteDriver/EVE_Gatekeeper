from fastapi import FastAPI

from .core.config import settings
from .api import routes_systems, routes_map


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
    )

    app.include_router(routes_systems.router, prefix="/systems", tags=["systems"])
    app.include_router(routes_map.router, prefix="/map", tags=["map"])

    return app


app = create_app()
