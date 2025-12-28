"""Routing API v1 endpoints."""

from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ...services.data_loader import load_universe, load_risk_config
from ...services.risk_engine import compute_risk, risk_to_color
from ...services.routing import compute_route
from ...models.route import RouteResponse

router = APIRouter()


@router.get(
    "/",
    response_model=RouteResponse,
    summary="Calculate route between systems",
    description="Calculates a route between two systems using the specified routing profile.",
)
def calculate_route(
    from_system: str = Query(..., alias="from", description="Origin system name"),
    to_system: str = Query(..., alias="to", description="Destination system name"),
    profile: str = Query(
        "shortest",
        description="Routing profile: 'shortest', 'safer', or 'paranoid'",
    ),
    avoid: Optional[List[str]] = Query(
        None,
        description="Systems to avoid (comma-separated or repeated param)",
    ),
) -> RouteResponse:
    """
    Calculate a route between two systems.

    - **from**: The starting system name (e.g., "Jita")
    - **to**: The destination system name (e.g., "Amarr")
    - **profile**: Routing strategy
        - `shortest`: Minimum jumps, ignores risk
        - `safer`: Balanced approach, avoids high-risk systems
        - `paranoid`: Maximum safety, avoids all dangerous areas
    - **avoid**: Systems to exclude from routing (e.g., "Tama,Rancer" or multiple &avoid=Tama&avoid=Rancer)
    """
    cfg = load_risk_config()
    if profile not in cfg.routing_profiles:
        available = ", ".join(cfg.routing_profiles.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown routing profile: '{profile}'. Available: {available}",
        )

    # Parse avoid list - handle comma-separated values
    avoid_set: set[str] = set()
    if avoid:
        for item in avoid:
            # Support comma-separated values in single param
            avoid_set.update(name.strip() for name in item.split(",") if name.strip())

    try:
        return compute_route(from_system, to_system, profile, avoid=avoid_set)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/config",
    summary="Get map configuration",
    description="Returns the complete map configuration including all systems, risk scores, and colors.",
)
async def get_map_config() -> Dict[str, Any]:
    """Get the complete map configuration for visualization."""
    universe = load_universe()
    cfg = load_risk_config()

    systems_payload = {}
    for name, sys in universe.systems.items():
        risk = compute_risk(name)
        color = risk_to_color(risk.score)
        systems_payload[name] = {
            "id": sys.id,
            "region_id": sys.region_id,
            "security": sys.security,
            "category": sys.category,
            "position": sys.position.dict(),
            "risk_score": risk.score,
            "risk_color": color,
        }

    return {
        "metadata": universe.metadata.dict(),
        "systems": systems_payload,
        "layers": cfg.map_layers,
        "routing_profiles": list(cfg.routing_profiles.keys()),
    }
