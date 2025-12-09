"""Risk scoring models for EVE Online systems."""

from typing import Dict
from pydantic import BaseModel


class RiskConfig(BaseModel):
    """Configuration for risk scoring and routing profiles."""
    security_category_weights: Dict[str, float]
    kill_weights: Dict[str, float]
    clamp: Dict[str, int]
    risk_colors: Dict[str, str]
    map_layers: Dict[str, bool]
    routing_profiles: Dict[str, Dict[str, float]]


class ZKillStats(BaseModel):
    """zKillboard statistics for a system."""
    recent_kills: int = 0
    recent_pods: int = 0


class RiskReport(BaseModel):
    """Risk analysis report for a system."""
    system_name: str
    risk_score: float
    security_score: float
    kill_score: float
    pod_score: float
    risk_color: str
