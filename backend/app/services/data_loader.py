import json
from functools import lru_cache

from ..core.config import settings
from ..models.risk import RiskConfig
from ..models.system import Gate, System, Universe, UniverseMetadata


@lru_cache(maxsize=1)
def load_universe() -> Universe:
    with settings.UNIVERSE_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    metadata = UniverseMetadata(**raw["metadata"])
    systems = {
        name: System(name=name, **data)
        for name, data in raw["systems"].items()
    }
    gates = [
        Gate(from_system=item["from"], to_system=item["to"], distance=item.get("distance", 1))
        for item in raw["gates"]
    ]
    return Universe(metadata=metadata, systems=systems, gates=gates)


@lru_cache(maxsize=1)
def load_risk_config() -> RiskConfig:
    with settings.RISK_CONFIG_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return RiskConfig(**raw)


def get_neighbors(system_name: str) -> list[Gate]:
    universe = load_universe()
    return [
        gate
        for gate in universe.gates
        if gate.from_system == system_name or gate.to_system == system_name
    ]
