"""REST API service for EVE Online map data and features.

This API provides endpoints for mobile app consumption including:
- Route planning with jump calculations
- Jump fuel cost calculations
- zkillboard intel integration
- System information and search
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, List, Optional, Tuple
import networkx as nx
from functools import lru_cache
import logging

from .models import System, JumpConnection, SecurityStatus
from .esi_client import ESIClient
from .utils import JumpRangeCalculator, MapAnalyzer
from .cache import ESICache
from .zkillboard import ZKillboardClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app access

# Global state (in production, use proper database)
_systems: Dict[int, System] = {}
_connections: List[JumpConnection] = []
_graph: Optional[nx.Graph] = None
_esi_client: Optional[ESIClient] = None
_zkill_client: Optional[ZKillboardClient] = None
_cache: Optional[ESICache] = None


def initialize_api(systems: Dict[int, System], connections: List[JumpConnection]):
    """Initialize the API with map data.
    
    Args:
        systems: Dictionary of System objects
        connections: List of JumpConnection objects
    """
    global _systems, _connections, _graph, _esi_client, _zkill_client, _cache
    
    _systems = systems
    _connections = connections
    _graph = _build_graph(systems, connections)
    _esi_client = ESIClient()
    _zkill_client = ZKillboardClient()
    _cache = ESICache()
    
    logger.info(f"API initialized with {len(systems)} systems and {len(connections)} connections")


def _build_graph(systems: Dict[int, System], connections: List[JumpConnection]) -> nx.Graph:
    """Build networkx graph from systems and connections."""
    G = nx.Graph()
    
    for system_id, system in systems.items():
        G.add_node(system_id, system=system)
    
    for conn in connections:
        if conn.source_system_id in systems and conn.target_system_id in systems:
            G.add_edge(
                conn.source_system_id,
                conn.target_system_id,
                distance=conn.distance
            )
    
    return G


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'systems_loaded': len(_systems),
        'connections_loaded': len(_connections)
    })


@app.route('/api/systems', methods=['GET'])
def get_systems():
    """Get all systems with optional filtering.
    
    Query params:
        - security: Filter by security status (high_sec, low_sec, null_sec)
        - region_id: Filter by region ID
        - limit: Maximum number of results (default 100)
    """
    security_filter = request.args.get('security')
    region_id = request.args.get('region_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    
    systems = list(_systems.values())
    
    # Apply filters
    if security_filter:
        try:
            sec_status = SecurityStatus(security_filter)
            systems = [s for s in systems if s.security_class == sec_status]
        except ValueError:
            return jsonify({'error': f'Invalid security status: {security_filter}'}), 400
    
    if region_id:
        systems = [s for s in systems if s.region_id == region_id]
    
    # Limit results
    systems = systems[:limit]
    
    # Convert to dict format
    result = [
        {
            'system_id': s.system_id,
            'name': s.name,
            'region_id': s.region_id,
            'constellation_id': s.constellation_id,
            'security_status': s.security_status,
            'security_class': s.security_class.value,
            'x': s.x,
            'y': s.y,
            'planets': s.planets,
            'stargates': s.stargates,
        }
        for s in systems
    ]
    
    return jsonify({'systems': result, 'count': len(result)})


@app.route('/api/systems/<int:system_id>', methods=['GET'])
def get_system(system_id: int):
    """Get detailed information about a specific system."""
    if system_id not in _systems:
        return jsonify({'error': 'System not found'}), 404
    
    system = _systems[system_id]
    
    # Get connected systems
    connected = []
    if _graph and system_id in _graph:
        connected = list(_graph.neighbors(system_id))
    
    return jsonify({
        'system_id': system.system_id,
        'name': system.name,
        'region_id': system.region_id,
        'constellation_id': system.constellation_id,
        'security_status': system.security_status,
        'security_class': system.security_class.value,
        'x': system.x,
        'y': system.y,
        'planets': system.planets,
        'stargates': system.stargates,
        'connected_systems': connected,
        'metadata': system.metadata
    })


@app.route('/api/search', methods=['GET'])
def search_systems():
    """Search systems by name.
    
    Query params:
        - q: Search query (required)
        - limit: Maximum results (default 10)
    """
    query = request.args.get('q', '').strip().lower()
    limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    # Search systems
    results = []
    for system in _systems.values():
        if query in system.name.lower():
            results.append({
                'system_id': system.system_id,
                'name': system.name,
                'region_id': system.region_id,
                'security_status': system.security_status,
                'security_class': system.security_class.value,
            })
            
            if len(results) >= limit:
                break
    
    return jsonify({'results': results, 'count': len(results)})


@app.route('/api/route', methods=['POST'])
def calculate_route():
    """Calculate route between two systems.
    
    Request body:
        - origin_id: Starting system ID (required)
        - destination_id: Destination system ID (required)
        - max_jumps: Maximum jumps to consider (default 50)
        - avoid_low_sec: Avoid low security systems (default false)
        - avoid_null_sec: Avoid null security systems (default false)
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    origin_id = data.get('origin_id', type=int)
    dest_id = data.get('destination_id', type=int)
    max_jumps = data.get('max_jumps', 50)
    avoid_low = data.get('avoid_low_sec', False)
    avoid_null = data.get('avoid_null_sec', False)
    
    if not origin_id or not dest_id:
        return jsonify({'error': 'origin_id and destination_id required'}), 400
    
    if origin_id not in _systems or dest_id not in _systems:
        return jsonify({'error': 'System not found'}), 404
    
    try:
        # Calculate route using pathfinding
        route = _calculate_route_with_filters(
            origin_id, dest_id, max_jumps, avoid_low, avoid_null
        )
        
        if not route:
            return jsonify({'error': 'No route found'}), 404
        
        # Build route details
        route_details = []
        total_jumps = len(route) - 1
        
        for i, system_id in enumerate(route):
            system = _systems[system_id]
            route_details.append({
                'system_id': system_id,
                'name': system.name,
                'security_status': system.security_status,
                'security_class': system.security_class.value,
                'jump_number': i,
            })
        
        return jsonify({
            'route': route_details,
            'total_jumps': total_jumps,
            'origin': _systems[origin_id].name,
            'destination': _systems[dest_id].name,
        })
        
    except Exception as e:
        logger.error(f"Route calculation error: {e}")
        return jsonify({'error': 'Route calculation failed'}), 500


def _calculate_route_with_filters(origin_id: int, dest_id: int, max_jumps: int,
                                   avoid_low: bool, avoid_null: bool) -> List[int]:
    """Calculate route with security filters."""
    from collections import deque
    
    if not _graph:
        return []
    
    # Build filtered graph
    filtered_graph = _graph.copy()
    
    # Remove nodes based on security filters
    if avoid_low or avoid_null:
        nodes_to_remove = []
        for node in filtered_graph.nodes():
            if node not in _systems:
                continue
            system = _systems[node]
            if avoid_low and system.security_class == SecurityStatus.LOW_SEC:
                nodes_to_remove.append(node)
            if avoid_null and system.security_class == SecurityStatus.NULL_SEC:
                nodes_to_remove.append(node)
        
        # Don't remove origin and destination
        if origin_id in nodes_to_remove:
            nodes_to_remove.remove(origin_id)
        if dest_id in nodes_to_remove:
            nodes_to_remove.remove(dest_id)
        
        filtered_graph.remove_nodes_from(nodes_to_remove)
    
    # Use NetworkX shortest path
    try:
        route = nx.shortest_path(filtered_graph, origin_id, dest_id)
        if len(route) - 1 > max_jumps:
            return []
        return route
    except nx.NetworkXNoPath:
        return []


@app.route('/api/route/fuel-cost', methods=['POST'])
def calculate_fuel_cost():
    """Calculate jump fuel cost for a route.
    
    Request body:
        - route: List of system IDs (required)
        - ship_type: Ship type (default "Carrier")
        - fuel_price: ISK per unit of fuel (default 500)
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    
    route = data.get('route', [])
    ship_type = data.get('ship_type', 'Carrier')
    fuel_price = data.get('fuel_price', 500)
    
    if not route or len(route) < 2:
        return jsonify({'error': 'Route must contain at least 2 systems'}), 400
    
    # Calculate fuel consumption
    # In EVE: ~1 fuel per LY for capital ships
    # Formula: fuel = distance * ship_multiplier
    ship_multipliers = {
        'Carrier': 3.0,
        'Dreadnought': 3.0,
        'Supercarrier': 3.5,
        'Titan': 4.0,
        'Jump Freighter': 3.0,
    }
    
    multiplier = ship_multipliers.get(ship_type, 3.0)
    total_fuel = 0
    total_distance = 0
    
    # Calculate based on jumps
    jumps = len(route) - 1
    
    # Estimate: ~300 fuel per jump for carriers
    fuel_per_jump = {
        'Carrier': 300,
        'Dreadnought': 300,
        'Supercarrier': 350,
        'Titan': 400,
        'Jump Freighter': 300,
    }
    
    total_fuel = jumps * fuel_per_jump.get(ship_type, 300)
    total_cost = total_fuel * fuel_price
    
    return jsonify({
        'total_jumps': jumps,
        'total_fuel': total_fuel,
        'fuel_per_jump': fuel_per_jump.get(ship_type, 300),
        'fuel_price': fuel_price,
        'total_cost': total_cost,
        'ship_type': ship_type,
    })


@app.route('/api/intel/zkillboard/<int:system_id>', methods=['GET'])
def get_zkillboard_intel(system_id: int):
    """Get zkillboard intel for a system.
    
    Query params:
        - limit: Number of kills to retrieve (default 10)
    """
    if system_id not in _systems:
        return jsonify({'error': 'System not found'}), 404
    
    limit = request.args.get('limit', 10, type=int)
    
    try:
        if _zkill_client:
            intel = _zkill_client.get_system_kills(system_id, limit=limit)
            return jsonify(intel)
        else:
            return jsonify({'error': 'zkillboard client not initialized'}), 500
    except Exception as e:
        logger.error(f"zkillboard error: {e}")
        return jsonify({'error': 'Failed to fetch intel'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall map statistics."""
    if not _systems or not _connections:
        return jsonify({'error': 'No data loaded'}), 500
    
    # Calculate security breakdown
    security_counts = {}
    for sec_class in SecurityStatus:
        count = sum(1 for s in _systems.values() if s.security_class == sec_class)
        security_counts[sec_class.value] = count
    
    return jsonify({
        'total_systems': len(_systems),
        'total_connections': len(_connections),
        'avg_connections_per_system': (2 * len(_connections) / len(_systems)) if _systems else 0,
        'security_breakdown': security_counts,
    })


def run_api(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """Run the API server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # For testing only
    run_api(debug=True)
