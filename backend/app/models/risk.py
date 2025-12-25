from pydantic import BaseModel


class RiskConfig(BaseModel):
    security_category_weights: dict[str, float]
    kill_weights: dict[str, float]
    clamp: dict[str, int]
    risk_colors: dict[str, str]
    map_layers: dict[str, bool]
    routing_profiles: dict[str, dict[str, float]]


class ZKillStats(BaseModel):
    recent_kills: int = 0
    recent_pods: int = 0


class RiskBreakdown(BaseModel):
    security_component: float
    kills_component: float
    pods_component: float


class RiskReport(BaseModel):
    system_name: str
    system_id: int
    category: str
    security: float
    score: float
    breakdown: RiskBreakdown
