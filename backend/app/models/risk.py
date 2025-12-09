from typing import Dict
from pydantic import BaseModel


class RiskConfig(BaseModel):
    security_category_weights: Dict[str, float]
    kill_weights: Dict[str, float]
    clamp: Dict[str, int]
    risk_colors: Dict[str, str]
    map_layers: Dict[str, bool]
    routing_profiles: Dict[str, Dict[str, float]]


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
