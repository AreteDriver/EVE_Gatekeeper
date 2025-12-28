from typing import Optional
from pydantic import BaseModel, Field


class RouteHop(BaseModel):
    system_name: str
    system_id: int
    cumulative_jumps: int
    cumulative_cost: float
    risk_score: float
    connection_type: str = Field(
        "gate",
        description="How we reached this system: 'gate' or 'bridge'"
    )


class RouteResponse(BaseModel):
    from_system: str
    to_system: str
    profile: str
    total_jumps: int
    total_cost: float
    max_risk: float
    avg_risk: float
    path: list[RouteHop]
    bridges_used: int = Field(0, description="Number of Ansiblex bridges in route")
