"""Route calculation models."""

from typing import List
from pydantic import BaseModel


class RouteHop(BaseModel):
    """Single hop in a route."""
    system_name: str
    security_status: float
    risk_score: float
    distance: float
    cumulative_cost: float


class RouteResponse(BaseModel):
    """Complete route calculation response."""
    path: List[RouteHop]
    total_jumps: int
    total_distance: float
    total_cost: float
    max_risk: float
    avg_risk: float
    profile: str
