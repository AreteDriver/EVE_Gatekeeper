"""FastAPI REST server - optimized for iOS clients."""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import time
import json
from datetime import datetime, timedelta

from .database import DatabaseManager
from .repository import DataRepository
from .graph_engine import GraphEngine
from .cache import ESICache


# ============================================================================
# Pydantic Models for API
# ============================================================================

class SystemResponse(BaseModel):
    """System data for mobile client."""
    id: int
    name: str
    region_id: int
    constellation_id: int
    security: float
    sec_class: str
    is_wormhole: bool
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    planets: int = 0
    stars: int = 0
    stargates: int = 0


class RegionResponse(BaseModel):
    """Region data."""
    id: int
    name: str
    description: Optional[str] = None


class ConstellationResponse(BaseModel):
    """Constellation data."""
    id: int
    name: str
    region_id: int


class RouteRequest(BaseModel):
    """Request for route planning."""
    origin: int
    destination: int
    avoid_lowsec: bool = False
    avoid_nullsec: bool = False
    avoid_systems: List[int] = []
    avoid_regions: List[int] = []


class RouteResponse(BaseModel):
    """Route planning response."""
    route: List[int]
    jumps: int
    systems: List[str]
    security_profile: str  # "all_high", "mixed", "low_or_worse", "null_or_worse"


class HubsResponse(BaseModel):
    """Hub systems response."""
    hubs: List[Dict]


class UniverseStatsResponse(BaseModel):
    """Universe statistics."""
    total_systems: int
    total_regions: int
    total_constellations: int
    total_stargates: int
    security_breakdown: Dict[str, int]


# ============================================================================
# Application Setup
# ============================================================================

def create_app(db_manager: DatabaseManager = None) -> FastAPI:
    """Create FastAPI application.

    Args:
        db_manager: Database manager instance (creates new if not provided)

    Returns:
        FastAPI app instance
    """
    if db_manager is None:
        db_manager = DatabaseManager()

    app = FastAPI(
        title="EVE Map API",
        description="REST API for EVE Online 2D map visualization",
        version="1.0.0"
    )

    # CORS for mobile clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # iOS Safari, mobile browsers
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Initialize dependencies
    repo = DataRepository(db_manager)
    graph_engine = GraphEngine(db_manager)
    cache = ESICache(cache_dir="data/api_cache", ttl_hours=6)

    # =====================================================================
    # Health & Info Endpoints
    # =====================================================================

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
        }

    @app.get("/stats", response_model=UniverseStatsResponse)
    async def get_stats():
        """Get universe statistics.

        Cached for 24 hours (static data).
        """
        cache_key = "universe_stats"
        cached = cache.get(cache_key)
        if cached:
            return cached

        stats = repo.get_stats()

        # Cache for 24 hours
        cache.set(cache_key, stats)

        return stats

    # =====================================================================
    # System Endpoints
    # =====================================================================

    @app.get("/systems/search")
    async def search_systems(
        q: str = Query(..., min_length=1, max_length=100),
        limit: int = Query(10, le=50)
    ) -> List[SystemResponse]:
        """Search systems by name.

        Args:
            q: Search query
            limit: Max results (max 50)

        Returns:
            List of matching systems
        """
        results = repo.systems.search(q, limit=limit)
        return [SystemResponse(**r) for r in results]

    @app.get("/systems/{system_id}", response_model=SystemResponse)
    async def get_system(system_id: int):
        """Get system details.

        Args:
            system_id: System ID

        Returns:
            System data
        """
        system = repo.systems.get_by_id(system_id)
        if not system:
            raise HTTPException(status_code=404, detail="System not found")
        return SystemResponse(**system)

    @app.get("/systems/{system_id}/neighbors")
    async def get_system_neighbors(system_id: int) -> List[SystemResponse]:
        """Get systems adjacent to this one (1 jump away).

        Args:
            system_id: System ID

        Returns:
            List of adjacent systems
        """
        neighbors = repo.systems.get_neighbors(system_id)
        return [SystemResponse(**n) for n in neighbors]

    # =====================================================================
    # Region Endpoints
    # =====================================================================

    @app.get("/regions", response_model=List[RegionResponse])
    async def list_regions():
        """List all regions.

        Returns:
            All regions in New Eden
        """
        regions = repo.regions.get_all()
        return [RegionResponse(**r) for r in regions]

    @app.get("/regions/{region_id}", response_model=RegionResponse)
    async def get_region(region_id: int):
        """Get region details.

        Args:
            region_id: Region ID

        Returns:
            Region data
        """
        region = repo.regions.get_by_id(region_id)
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
        return RegionResponse(**region)

    @app.get("/regions/{region_id}/systems")
    async def get_region_systems(region_id: int) -> List[SystemResponse]:
        """Get all systems in a region.

        Args:
            region_id: Region ID

        Returns:
            List of systems
        """
        systems = repo.systems.get_by_region(region_id)
        return [SystemResponse(**s) for s in systems]

    @app.get("/regions/{region_id}/constellations")
    async def get_region_constellations(
        region_id: int
    ) -> List[ConstellationResponse]:
        """Get constellations in a region.

        Args:
            region_id: Region ID

        Returns:
            List of constellations
        """
        constellations = repo.constellations.get_by_region(region_id)
        return [ConstellationResponse(**c) for c in constellations]

    # =====================================================================
    # Routing Endpoints
    # =====================================================================

    @app.post("/routes/plan", response_model=RouteResponse)
    async def plan_route(request: RouteRequest):
        """Plan a jump route between systems.

        Supports constraints like avoiding lowsec, specific systems/regions.

        Args:
            request: Route request with origin, destination, constraints

        Returns:
            Route with system names and security profile
        """
        if not graph_engine._built:
            raise HTTPException(
                status_code=503,
                detail="Graph engine not initialized. Run 'init-universe' first."
            )

        # Convert security constraints to avoid_regions
        avoid_regions = set(request.avoid_regions)

        if request.avoid_lowsec:
            # Find all lowsec regions (this is simplified)
            pass  # Would need region security classification

        if request.avoid_nullsec:
            # Find all nullsec regions
            pass

        # Find route
        route_ids = graph_engine.shortest_path(
            request.origin,
            request.destination,
            avoid_systems=set(request.avoid_systems),
            avoid_regions=avoid_regions
        )

        if not route_ids:
            raise HTTPException(status_code=404, detail="No route found")

        # Get system names and analyze security
        session = db_manager.get_session()
        try:
            from .database import System
            systems_on_route = session.query(System).filter(
                System.system_id.in_(route_ids)
            ).all()

            system_map = {s.system_id: s for s in systems_on_route}
            system_names = [system_map[sid].name for sid in route_ids if sid in system_map]

            # Determine security profile
            security_classes = [system_map[sid].security_class for sid in route_ids if sid in system_map]
            if all(s == "high_sec" for s in security_classes):
                security_profile = "all_high"
            elif any(s == "null_sec" for s in security_classes):
                security_profile = "null_or_worse"
            elif any(s == "low_sec" for s in security_classes):
                security_profile = "low_or_worse"
            else:
                security_profile = "mixed"

        finally:
            session.close()

        return RouteResponse(
            route=route_ids,
            jumps=len(route_ids) - 1,
            systems=system_names,
            security_profile=security_profile
        )

    # =====================================================================
    # Analysis Endpoints
    # =====================================================================

    @app.get("/analysis/hubs")
    async def get_hub_systems(limit: int = Query(20, le=100)) -> HubsResponse:
        """Get most connected systems (regional hubs).

        Args:
            limit: Number of hubs to return

        Returns:
            List of hub systems with connection counts
        """
        if not graph_engine._built:
            raise HTTPException(
                status_code=503,
                detail="Graph engine not initialized. Run 'init-universe' first."
            )

        hubs = graph_engine.find_hubs(top_n=limit)
        return HubsResponse(
            hubs=[
                {
                    'id': system_id,
                    'name': name,
                    'connections': count
                }
                for system_id, name, count in hubs
            ]
        )

    @app.get("/analysis/bottlenecks")
    async def get_bottleneck_systems(limit: int = Query(20, le=100)):
        """Get critical systems (bottlenecks).

        Systems that separate regions and have high traffic.

        Args:
            limit: Number of bottlenecks to return

        Returns:
            List of bottleneck systems
        """
        if not graph_engine._built:
            raise HTTPException(
                status_code=503,
                detail="Graph engine not initialized. Run 'init-universe' first."
            )

        bottlenecks = graph_engine.find_bottlenecks(top_n=limit)
        return {
            'bottlenecks': [
                {
                    'id': system_id,
                    'name': name,
                    'score': score
                }
                for system_id, name, score in bottlenecks
            ]
        }

    # =====================================================================
    # Admin Endpoints
    # =====================================================================

    @app.post("/admin/init-universe")
    async def init_universe(background_tasks: BackgroundTasks):
        """Initialize universe data (load SDE and build graph).

        This is an admin endpoint - should be protected in production.

        Returns:
            Status and estimated time
        """
        def _load_universe():
            try:
                from .sde_loader import SDELoader
                loader = SDELoader(db_manager)
                loader.load_all()

                print("Building graph engine...")
                graph_engine.build_from_db()

                print("Universe initialization complete!")

            except Exception as e:
                print(f"Error initializing universe: {e}")

        background_tasks.add_task(_load_universe)

        return {
            "status": "initializing",
            "message": "Universe load started in background. Check logs for progress."
        }

    @app.post("/admin/export-graph")
    async def export_graph_endpoint(background_tasks: BackgroundTasks):
        """Export graph as JSON for iOS clients.

        Returns:
            Status
        """
        def _export():
            graph_engine.export_as_json("data/universe_graph.json")

        background_tasks.add_task(_export)

        return {
            "status": "exporting",
            "message": "Graph export started. Will be available at /static/universe_graph.json"
        }

    @app.get("/static/universe_graph.json")
    async def get_graph_file():
        """Download complete universe graph (for offline-first mobile apps)."""
        try:
            return FileResponse("data/universe_graph.json", media_type="application/json")
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="Graph not exported. Run /admin/export-graph first."
            )

    # =====================================================================
    # Heatmap & Intel Endpoints (Phase 2)
    # =====================================================================

    @app.get("/intel/activity")
    async def get_activity_heatmap(background_tasks: BackgroundTasks):
        """Get activity heatmap (kills and jumps).

        Cached for 5-10 minutes (ESI best practice).

        Returns:
            Activity heatmap with kills and jumps per system
        """
        from .heatmap import HeatmapEngine

        cache_key = "activity_heatmap"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            engine = HeatmapEngine(db_manager)
            activity = engine.get_activity_heatmap()

            # Cache for 10 minutes
            cache.set(cache_key, activity)

            return activity

        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch activity data: {str(e)}"
            )

    @app.get("/intel/incursions")
    async def get_incursions():
        """Get active incursions.

        Returns:
            List of active incursions with affected systems
        """
        from .heatmap import HeatmapEngine

        cache_key = "incursions"
        cached = cache.get(cache_key)
        if cached:
            return {"incursions": cached}

        try:
            engine = HeatmapEngine(db_manager)
            incursions = engine.get_incursions()

            cache.set(cache_key, incursions)

            return {"incursions": incursions}

        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch incursion data: {str(e)}"
            )

    @app.get("/intel/sovereignty")
    async def get_sovereignty():
        """Get sovereignty data for regions and systems.

        Returns:
            Sovereignty map indexed by system ID
        """
        from .heatmap import HeatmapEngine

        cache_key = "sovereignty"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            engine = HeatmapEngine(db_manager)
            sov = engine.get_sovereignty_map()

            cache.set(cache_key, sov)

            return {"sovereignty": sov}

        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch sovereignty data: {str(e)}"
            )

    @app.get("/intel/campaigns")
    async def get_campaigns():
        """Get active sovereignty campaigns.

        Returns:
            List of active sov campaigns
        """
        from .heatmap import HeatmapEngine

        cache_key = "campaigns"
        cached = cache.get(cache_key)
        if cached:
            return {"campaigns": cached}

        try:
            engine = HeatmapEngine(db_manager)
            campaigns = engine.get_sov_campaigns()

            cache.set(cache_key, campaigns)

            return {"campaigns": campaigns}

        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch campaign data: {str(e)}"
            )

    @app.get("/intel/all")
    async def get_all_intel():
        """Get all live intel layers combined.

        Returns activity, incursions, sov, and campaigns in one call.

        Returns:
            Complete intel object
        """
        from .heatmap import HeatmapEngine

        cache_key = "all_intel"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            engine = HeatmapEngine(db_manager)
            intel = engine.get_intel_layers()

            cache.set(cache_key, intel)

            return intel

        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch intel data: {str(e)}"
            )

    @app.post("/admin/refresh-intel")
    async def refresh_intel(background_tasks: BackgroundTasks):
        """Manually refresh intel layers (clears cache).

        Returns:
            Status
        """
        def _refresh():
            cache.cache_dir.glob('*.json')
            from pathlib import Path
            for cache_file in cache.cache_dir.glob('*.json'):
                if 'intel' in cache_file.name or 'activity' in cache_file.name:
                    try:
                        cache_file.unlink()
                    except:
                        pass

        background_tasks.add_task(_refresh)

        return {
            "status": "refreshing",
            "message": "Intel cache cleared. New data will be fetched on next request."
        }

    return app


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
