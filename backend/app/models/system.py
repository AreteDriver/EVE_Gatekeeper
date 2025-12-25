from pydantic import BaseModel


class Position(BaseModel):
    x: float
    y: float


class System(BaseModel):
    name: str
    id: int
    region_id: int
    security: float
    category: str  # highsec, lowsec, nullsec, wh
    position: Position


class Gate(BaseModel):
    from_system: str
    to_system: str
    distance: float = 1.0


class UniverseMetadata(BaseModel):
    version: str
    source: str
    last_updated: str


class Universe(BaseModel):
    metadata: UniverseMetadata
    systems: dict[str, System]
    gates: list[Gate]


class SystemSummary(BaseModel):
    name: str
    security: float
    category: str
    region_id: int
