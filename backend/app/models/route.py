from typing import List, Optional
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


class RouteCompareRequest(BaseModel):
    """Request for comparing multiple routes."""
    from_system: str = Field(..., description="Origin system name")
    to_system: str = Field(..., description="Destination system name")
    profiles: List[str] = Field(
        default=["shortest", "safer", "paranoid"],
        description="Profiles to compare"
    )
    use_bridges: bool = Field(False, description="Include bridges in routing")
    avoid: List[str] = Field(default_factory=list, description="Systems to avoid")


class RouteSummary(BaseModel):
    """Summary of a single route for comparison."""
    profile: str
    total_jumps: int
    total_cost: float
    max_risk: float
    avg_risk: float
    bridges_used: int = 0
    highsec_jumps: int = 0
    lowsec_jumps: int = 0
    nullsec_jumps: int = 0
    path_systems: List[str] = Field(default_factory=list, description="System names in order")


class RouteCompareResponse(BaseModel):
    """Response comparing multiple routes."""
    from_system: str
    to_system: str
    routes: List[RouteSummary]
    recommendation: str = Field(..., description="Which route is recommended and why")
