"""Systems API v1 endpoints."""

from fastapi import APIRouter, HTTPException

from ...models.risk import RiskReport
from ...models.system import SystemSummary
from ...services.data_loader import get_neighbors, load_universe
from ...services.risk_engine import compute_risk_async

router = APIRouter()


@router.get(
    "/",
    response_model=list[SystemSummary],
    summary="List all systems",
    description="Returns a list of all systems in the EVE universe with basic information.",
)
def list_systems() -> list[SystemSummary]:
    """Get all systems in the universe."""
    universe = load_universe()
    return [
        SystemSummary(
            name=sys.name,
            security=sys.security,
            category=sys.category,
            region_id=sys.region_id,
            region_name=sys.region_name,
            constellation_id=sys.constellation_id,
            constellation_name=sys.constellation_name,
        )
        for sys in universe.systems.values()
    ]


@router.get(
    "/{system_name}",
    response_model=SystemSummary,
    summary="Get system details",
    description="Returns details for a specific system.",
)
def get_system(system_name: str) -> SystemSummary:
    """Get details for a specific system."""
    universe = load_universe()
    if system_name not in universe.systems:
        raise HTTPException(status_code=404, detail=f"System '{system_name}' not found")
    sys = universe.systems[system_name]
    return SystemSummary(
        name=sys.name,
        security=sys.security,
        category=sys.category,
        region_id=sys.region_id,
        region_name=sys.region_name,
        constellation_id=sys.constellation_id,
        constellation_name=sys.constellation_name,
    )


@router.get(
    "/{system_name}/risk",
    response_model=RiskReport,
    summary="Get system risk report",
    description="Returns a risk assessment for the specified system based on recent activity.",
)
async def get_system_risk(system_name: str, live: bool = True) -> RiskReport:
    """
    Get risk assessment for a system.

    Args:
        system_name: Name of the system
        live: If true, fetch fresh kill data from zKillboard (default: true)
    """
    universe = load_universe()
    if system_name not in universe.systems:
        raise HTTPException(status_code=404, detail=f"System '{system_name}' not found")
    return await compute_risk_async(system_name, fetch_live=live)


@router.get(
    "/{system_name}/neighbors",
    response_model=list[str],
    summary="Get neighboring systems",
    description="Returns a list of systems directly connected via stargates.",
)
def get_system_neighbors(system_name: str) -> list[str]:
    """Get systems connected to the specified system."""
    universe = load_universe()
    if system_name not in universe.systems:
        raise HTTPException(status_code=404, detail=f"System '{system_name}' not found")

    neighbors = get_neighbors(system_name)
    names: set[str] = set()
    for gate in neighbors:
        if gate.from_system == system_name:
            names.add(gate.to_system)
        else:
            names.add(gate.from_system)
    return sorted(names)
