from pydantic import BaseModel, Field


class RouteHop(BaseModel):
    system_name: str
    system_id: int
    cumulative_jumps: int
    cumulative_cost: float
    risk_score: float
    connection_type: str = Field(
        "gate", description="How we reached this system: 'gate' or 'bridge'"
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
    profiles: list[str] = Field(
        default=["shortest", "safer", "paranoid"], description="Profiles to compare"
    )
    use_bridges: bool = Field(False, description="Include bridges in routing")
    avoid: list[str] = Field(default_factory=list, description="Systems to avoid")


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
    path_systems: list[str] = Field(default_factory=list, description="System names in order")


class RouteCompareResponse(BaseModel):
    """Response comparing multiple routes."""

    from_system: str
    to_system: str
    routes: list[RouteSummary]
    recommendation: str = Field(..., description="Which route is recommended and why")


class BulkRouteRequest(BaseModel):
    """Request for calculating multiple routes."""

    from_system: str = Field(..., description="Origin system name")
    to_systems: list[str] = Field(..., description="List of destination systems")
    profile: str = Field("shortest", description="Routing profile to use")
    use_bridges: bool = Field(False, description="Include bridges in routing")
    avoid: list[str] = Field(default_factory=list, description="Systems to avoid")


class BulkRouteResult(BaseModel):
    """Result for a single route in bulk calculation."""

    to_system: str
    success: bool
    total_jumps: int | None = None
    total_cost: float | None = None
    max_risk: float | None = None
    avg_risk: float | None = None
    bridges_used: int = 0
    path_systems: list[str] = Field(default_factory=list)
    error: str | None = None


class BulkRouteResponse(BaseModel):
    """Response for bulk route calculation."""

    from_system: str
    profile: str
    total_destinations: int
    successful: int
    failed: int
    routes: list[BulkRouteResult]
