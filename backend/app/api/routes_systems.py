from typing import List, Set
from fastapi import APIRouter, HTTPException

from ..services.data_loader import load_universe, get_neighbors
from ..services.risk_engine import compute_risk
from ..models.system import SystemSummary
from ..models.risk import RiskReport

router = APIRouter()


@router.get("/", response_model=List[SystemSummary])
def list_systems() -> List[SystemSummary]:
    universe = load_universe()
    return [
        SystemSummary(
            name=sys.name,
            security=sys.security,
            category=sys.category,
            region_id=sys.region_id,
        )
        for sys in universe.systems.values()
    ]


@router.get("/{system_name}/risk", response_model=RiskReport)
async def get_system_risk(system_name: str) -> RiskReport:
    universe = load_universe()
    if system_name not in universe.systems:
        raise HTTPException(status_code=404, detail="System not found")
    return compute_risk(system_name)


@router.get("/{system_name}/neighbors", response_model=List[str])
def system_neighbors(system_name: str) -> List[str]:
    universe = load_universe()
    if system_name not in universe.systems:
        raise HTTPException(status_code=404, detail="System not found")

    neighbors = get_neighbors(system_name)
    names: Set[str] = set()
    for gate in neighbors:
        if gate.from_system == system_name:
            names.add(gate.to_system)
        else:
            names.add(gate.from_system)
    return sorted(names)
