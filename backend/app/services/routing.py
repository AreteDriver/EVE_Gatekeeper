"""Routing service with Dijkstra algorithm."""

import math
from typing import Dict, List, Tuple, Optional
from heapq import heappush, heappop

from backend.app.models.route import RouteHop, RouteResponse
from backend.app.services.data_loader import load_universe, load_risk_config
from backend.app.services.risk_engine import compute_risk


def _build_graph() -> Dict[str, Dict[str, float]]:
    """Build adjacency graph from universe gates."""
    universe = load_universe()
    graph: Dict[str, Dict[str, float]] = {name: {} for name in universe.systems}
    
    for gate in universe.gates:
        graph[gate.from_system][gate.to_system] = gate.distance
    
    return graph


def _dijkstra(graph: Dict[str, Dict[str, float]], start: str, end: str, profile: str) -> Tuple[List[str], float]:
    """Calculate shortest path using Dijkstra's algorithm with risk weighting."""
    config = load_risk_config()
    universe = load_universe()
    
    # Get risk factor from profile
    risk_factor = config.routing_profiles.get(profile, {}).get("risk_factor", 0.0)
    
    # Initialize distances and predecessors
    dist: Dict[str, float] = {node: math.inf for node in graph}
    prev: Dict[str, Optional[str]] = {node: None for node in graph}
    dist[start] = 0.0
    
    # Priority queue: (distance, node)
    pq = [(0.0, start)]
    visited = set()
    
    while pq:
        current_dist, current = heappop(pq)
        
        if current in visited:
            continue
        visited.add(current)
        
        if current == end:
            break
        
        for neighbor, base_distance in graph[current].items():
            if neighbor in visited:
                continue
            
            # Calculate risk-adjusted cost
            system = universe.systems[neighbor]
            risk_score = compute_risk(system.name).risk_score
            cost = base_distance * (1 + risk_factor * (risk_score / 100))
            
            new_dist = current_dist + cost
            
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heappush(pq, (new_dist, neighbor))
    
    # Reconstruct path
    path: List[str] = []
    current = end
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    
    return path, dist[end]


def calculate_route(start: str, end: str, profile: str = "shortest") -> RouteResponse:
    """Calculate route between two systems with given profile."""
    graph = _build_graph()
    universe = load_universe()
    
    if start not in graph or end not in graph:
        raise ValueError(f"System not found: {start} or {end}")
    
    path_names, total_cost = _dijkstra(graph, start, end, profile)
    
    # Build detailed hops
    hops: List[RouteHop] = []
    cumulative_cost = 0.0
    total_distance = 0.0
    max_risk = 0.0
    total_risk = 0.0
    
    for i, system_name in enumerate(path_names):
        system = universe.systems[system_name]
        risk_report = compute_risk(system_name)
        
        if i > 0:
            prev_system = path_names[i-1]
            distance = graph[prev_system].get(system_name, 0.0)
            total_distance += distance
        else:
            distance = 0.0
        
        cumulative_cost += distance
        max_risk = max(max_risk, risk_report.risk_score)
        total_risk += risk_report.risk_score
        
        hops.append(RouteHop(
            system_name=system_name,
            security_status=system.security_status,
            risk_score=risk_report.risk_score,
            distance=distance,
            cumulative_cost=cumulative_cost
        ))
    
    avg_risk = total_risk / len(hops) if hops else 0.0
    
    return RouteResponse(
        path=hops,
        total_jumps=len(path_names) - 1,
        total_distance=total_distance,
        total_cost=total_cost,
        max_risk=max_risk,
        avg_risk=avg_risk,
        profile=profile
    )
