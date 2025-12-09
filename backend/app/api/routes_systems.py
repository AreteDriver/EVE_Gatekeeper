"""System-related API routes."""

from typing import List
from fastapi import APIRouter, HTTPException

from backend.app.models.system import System, Gate
from backend.app.models.risk import RiskReport
from backend.app.services.data_loader import load_universe, get_neighbors
from backend.app.services.risk_engine import compute_risk

router = APIRouter()


@router.get("/", response_model=List[System])
def list_systems():
    """List all systems in the universe."""
    universe = load_universe()
    return list(universe.systems.values())


@router.get("/{system_name}/risk", response_model=RiskReport)
def get_system_risk(system_name: str):
    """Get risk report for a system."""
    try:
        return compute_risk(system_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{system_name}/neighbors", response_model=List[Gate])
def get_system_neighbors(system_name: str):
    """Get neighboring systems connected by gates."""
    universe = load_universe()
    if system_name not in universe.systems:
        raise HTTPException(status_code=404, detail=f"System not found: {system_name}")
    
    return get_neighbors(system_name)
