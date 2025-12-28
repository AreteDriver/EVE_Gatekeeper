"""API v1 router - consolidates all versioned endpoints."""

from fastapi import APIRouter

from .systems import router as systems_router
from .routing import router as routing_router
from .status import router as status_router
from .websocket import router as websocket_router
from .jump import router as jump_router
from .bridges import router as bridges_router

router = APIRouter(prefix="/api/v1")

router.include_router(systems_router, prefix="/systems", tags=["systems"])
router.include_router(routing_router, prefix="/route", tags=["routing"])
router.include_router(jump_router, prefix="/jump", tags=["jump"])
router.include_router(bridges_router, prefix="/bridges", tags=["bridges"])
router.include_router(status_router, prefix="/status", tags=["status"])
router.include_router(websocket_router, tags=["websocket"])
