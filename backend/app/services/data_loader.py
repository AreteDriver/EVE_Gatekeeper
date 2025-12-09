"""Data loading service with caching."""

import json
from functools import lru_cache
from typing import List
from pathlib import Path

from backend.app.models.system import Universe, Gate, System
from backend.app.models.risk import RiskConfig


DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def load_universe() -> Universe:
    """Load universe data from JSON file."""
    universe_file = DATA_DIR / "universe.json"
    with open(universe_file, "r") as f:
        data = json.load(f)
    return Universe(**data)


@lru_cache(maxsize=1)
def load_risk_config() -> RiskConfig:
    """Load risk configuration from JSON file."""
    config_file = DATA_DIR / "risk_config.json"
    with open(config_file, "r") as f:
        data = json.load(f)
    return RiskConfig(**data)


def get_neighbors(system_name: str) -> List[Gate]:
    """Get all gates connected to a system."""
    universe = load_universe()
    return [
        gate for gate in universe.gates
        if gate.from_system == system_name
    ]
