"""
EVE Map Visualization - A 2D map visualization tool for EVE Online's New Eden.

Provides tools for:
- Fetching data from EVE's ESI API
- Building node-based 2D map layouts
- Visualizing systems, regions, and jump connections
- Analyzing and filtering map data
- REST API for mobile app integration
- zkillboard intel gathering
"""

__version__ = "0.1.0"

from .models import System, Region, Constellation, JumpConnection
from .esi_client import ESIClient
from .map import NedenMap
from .zkillboard import ZKillboardClient
from .api import initialize_api, run_api

__all__ = [
    "System",
    "Region",
    "Constellation",
    "JumpConnection",
    "ESIClient",
    "NedenMap",
    "ZKillboardClient",
    "initialize_api",
    "run_api",
]
