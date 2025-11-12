"""
EVE Map Visualization - A 2D map visualization tool for EVE Online's New Eden.

Provides tools for:
- Loading EVE's Static Data Export (SDE)
- Fetching live data from EVE's ESI API
- Building node-based 2D map layouts
- Planning jump routes with constraints
- Visualizing systems, regions, and jump connections
- Analyzing and filtering map data
- REST API for mobile clients
"""

__version__ = "1.0.0"

# Models
from .models import System, Region, Constellation, JumpConnection

# ESI Client
from .esi_client import ESIClient

# Visualization
from .map import NedenMap

# Database & ORM
from .database import DatabaseManager, Region as RegionORM, Constellation as ConstellationORM, System as SystemORM

# Data Loading
from .sde_loader import SDELoader

# Data Access
from .repository import DataRepository

# Graph & Routing
from .graph_engine import GraphEngine

# Caching
from .cache import ESICache

# API
from .api import create_app

__all__ = [
    # Models
    "System",
    "Region",
    "Constellation",
    "JumpConnection",
    # Clients
    "ESIClient",
    # Visualization
    "NedenMap",
    # Database
    "DatabaseManager",
    # Data Loading
    "SDELoader",
    # Data Access
    "DataRepository",
    # Graph
    "GraphEngine",
    # Caching
    "ESICache",
    # API
    "create_app",
]
