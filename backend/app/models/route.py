from typing import List
from pydantic import BaseModel


class RouteHop(BaseModel):
    system_name: str
    system_id: int
    cumulative_jumps: int
    cumulative_cost: float
    risk_score: float


class RouteResponse(BaseModel):
    from_system: str
    to_system: str
    profile: str
    total_jumps: int
    total_cost: float
    max_risk: float
    avg_risk: float
    path: List[RouteHop]
