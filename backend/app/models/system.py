"""Universe and system models."""

from typing import Dict, List
from pydantic import BaseModel


class Gate(BaseModel):
    """Jump gate connection between systems."""
    from_system: str
    to_system: str
    distance: float = 1.0


class System(BaseModel):
    """Solar system in New Eden."""
    name: str
    system_id: int
    region_id: int
    constellation_id: int
    security_status: float
    security_category: str  # "high_sec", "low_sec", "null_sec"
    x: float = 0.0
    y: float = 0.0


class Universe(BaseModel):
    """Complete universe data."""
    systems: Dict[str, System]
    gates: List[Gate]
