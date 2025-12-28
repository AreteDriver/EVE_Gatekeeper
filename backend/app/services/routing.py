import math
from typing import Set

from .data_loader import load_universe, load_risk_config
from .risk_engine import compute_risk
from ..models.route import RouteResponse, RouteHop


def _build_graph(avoid: Set[str] | None = None) -> dict[str, dict[str, float]]:
    """
    Build navigation graph from universe data.

    Args:
        avoid: Set of system names to exclude from the graph

    Returns:
        Adjacency dict mapping system -> {neighbor -> distance}
    """
    universe = load_universe()
    avoid = avoid or set()

    # Exclude avoided systems from the graph
    graph: dict[str, dict[str, float]] = {
        name: {} for name in universe.systems if name not in avoid
    }

    for gate in universe.gates:
        # Skip gates involving avoided systems
        if gate.from_system in avoid or gate.to_system in avoid:
            continue
        if gate.from_system in graph and gate.to_system in graph:
            graph[gate.from_system][gate.to_system] = gate.distance
            graph[gate.to_system][gate.from_system] = gate.distance

    return graph


def _dijkstra(graph: dict[str, dict[str, float]], start: str, end: str, profile: str) -> tuple[list[str], float]:
    cfg = load_risk_config()
    profile_cfg = cfg.routing_profiles.get(profile, cfg.routing_profiles["shortest"])
    risk_factor = profile_cfg.get("risk_factor", 0.0)

    dist: dict[str, float] = {node: math.inf for node in graph}
    prev: dict[str, str | None] = {node: None for node in graph}
    visited: set[str] = set()

    dist[start] = 0.0

    while visited != set(graph.keys()):
        current = min((n for n in graph if n not in visited), key=lambda n: dist[n])
        if dist[current] == math.inf:
            break
        visited.add(current)
        if current == end:
            break

        for neighbor, base_cost in graph[current].items():
            risk_report = compute_risk(neighbor)
            risk_penalty = risk_factor * (risk_report.score / 100.0)
            cost = base_cost * (1.0 + risk_penalty)

            alt = dist[current] + cost
            if alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = current

    if dist[end] == math.inf:
        return [], math.inf

    node = end
    path: list[str] = []
    while node is not None:
        path.append(node)
        node = prev[node]  # type: ignore
    path.reverse()
    return path, dist[end]


def compute_route(
    from_system: str,
    to_system: str,
    profile: str = "shortest",
    avoid: Set[str] | None = None,
) -> RouteResponse:
    """
    Compute a route between two systems.

    Args:
        from_system: Origin system name
        to_system: Destination system name
        profile: Routing profile ('shortest', 'safer', 'paranoid')
        avoid: Set of system names to avoid in routing

    Returns:
        RouteResponse with path details
    """
    universe = load_universe()
    avoid = avoid or set()

    if from_system not in universe.systems:
        raise ValueError(f"Unknown from_system: {from_system}")
    if to_system not in universe.systems:
        raise ValueError(f"Unknown to_system: {to_system}")
    if from_system in avoid:
        raise ValueError(f"Cannot avoid origin system: {from_system}")
    if to_system in avoid:
        raise ValueError(f"Cannot avoid destination system: {to_system}")

    graph = _build_graph(avoid)
    path_names, total_cost = _dijkstra(graph, from_system, to_system, profile)
    if not path_names:
        raise ValueError("No route found")

    hops: list[RouteHop] = []
    total_risk = 0.0
    max_risk = 0.0
    cumulative_cost = 0.0

    for idx, name in enumerate(path_names):
        rr = compute_risk(name)
        total_risk += rr.score
        max_risk = max(max_risk, rr.score)
        if idx > 0:
            # cost between path_names[idx-1] and this one
            edge_cost = graph[path_names[idx - 1]][name]
            cumulative_cost += edge_cost
        hops.append(
            RouteHop(
                system_name=name,
                system_id=universe.systems[name].id,
                cumulative_jumps=idx,
                cumulative_cost=cumulative_cost,
                risk_score=rr.score,
            )
        )

    avg_risk = total_risk / len(path_names)

    return RouteResponse(
        from_system=from_system,
        to_system=to_system,
        profile=profile,
        total_jumps=len(path_names) - 1,
        total_cost=total_cost,
        max_risk=max_risk,
        avg_risk=avg_risk,
        path=hops,
    )
