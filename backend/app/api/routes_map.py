"""Map-related API routes."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query

from backend.app.models.route import RouteResponse
from backend.app.services.data_loader import load_universe, load_risk_config
from backend.app.services.risk_engine import compute_risk
from backend.app.services.routing import calculate_route

router = APIRouter()


@router.get("/config", response_model=Dict[str, Any])
def get_map_config():
    """Get complete map configuration with risk scores."""
    universe = load_universe()
    config = load_risk_config()
    
    # Compute risk scores for all systems
    system_risks = {}
    for system_name in universe.systems:
        risk_report = compute_risk(system_name)
        system_risks[system_name] = {
            "risk_score": risk_report.risk_score,
            "risk_color": risk_report.risk_color
        }
    
    return {
        "systems": {name: sys.dict() for name, sys in universe.systems.items()},
        "gates": [gate.dict() for gate in universe.gates],
        "system_risks": system_risks,
        "map_layers": config.map_layers,
        "routing_profiles": config.routing_profiles
    }


@router.get("/route", response_model=RouteResponse)
def get_route(
    from_system: str = Query(..., alias="from"),
    to_system: str = Query(..., alias="to"),
    profile: str = Query("shortest", description="Routing profile: shortest, safer, or paranoid")
):
    """Calculate route between two systems."""
    try:
        return calculate_route(from_system, to_system, profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
