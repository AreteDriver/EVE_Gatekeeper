import math

from ..models.route import RouteHop, RouteResponse
from .data_loader import load_risk_config, load_universe
from .jumpbridge import get_active_bridges
from .risk_engine import compute_risk

# Edge type markers for distinguishing gates from bridges
EDGE_GATE = "gate"
EDGE_BRIDGE = "bridge"


def _build_graph(
    avoid: set[str] | None = None,
    use_bridges: bool = False,
) -> tuple[dict[str, dict[str, float]], dict[tuple[str, str], str]]:
    """
    Build navigation graph from universe data.

    Args:
        avoid: Set of system names to exclude from the graph
        use_bridges: Whether to include Ansiblex jump bridges

    Returns:
        Tuple of (adjacency dict, edge type dict)
        - Adjacency: system -> {neighbor -> distance}
        - Edge types: (from, to) -> "gate" or "bridge"
    """
    universe = load_universe()
    avoid = avoid or set()

    # Exclude avoided systems from the graph
    graph: dict[str, dict[str, float]] = {
        name: {} for name in universe.systems if name not in avoid
    }
    edge_types: dict[tuple[str, str], str] = {}

    # Add stargate connections
    for gate in universe.gates:
        # Skip gates involving avoided systems
        if gate.from_system in avoid or gate.to_system in avoid:
            continue
        if gate.from_system in graph and gate.to_system in graph:
            graph[gate.from_system][gate.to_system] = gate.distance
            graph[gate.to_system][gate.from_system] = gate.distance
            edge_types[(gate.from_system, gate.to_system)] = EDGE_GATE
            edge_types[(gate.to_system, gate.from_system)] = EDGE_GATE

    # Add jump bridge connections
    if use_bridges:
        bridges = get_active_bridges()
        for bridge in bridges:
            if bridge.from_system in avoid or bridge.to_system in avoid:
                continue
            if bridge.from_system in graph and bridge.to_system in graph:
                # Jump bridges have distance 1 (instant travel)
                # Only add if not already connected (or prefer bridge)
                graph[bridge.from_system][bridge.to_system] = 1.0
                graph[bridge.to_system][bridge.from_system] = 1.0
                edge_types[(bridge.from_system, bridge.to_system)] = EDGE_BRIDGE
                edge_types[(bridge.to_system, bridge.from_system)] = EDGE_BRIDGE

    return graph, edge_types


def _dijkstra(
    graph: dict[str, dict[str, float]], start: str, end: str, profile: str
) -> tuple[list[str], float]:
    cfg = load_risk_config()
    profile_cfg = cfg.routing_profiles.get(profile, cfg.routing_profiles["shortest"])
    risk_factor = profile_cfg.get("risk_factor", 0.0)

    dist: dict[str, float] = dict.fromkeys(graph, math.inf)
    prev: dict[str, str | None] = dict.fromkeys(graph)
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
    avoid: set[str] | None = None,
    use_bridges: bool = False,
) -> RouteResponse:
    """
    Compute a route between two systems.

    Args:
        from_system: Origin system name
        to_system: Destination system name
        profile: Routing profile ('shortest', 'safer', 'paranoid')
        avoid: Set of system names to avoid in routing
        use_bridges: Whether to use Ansiblex jump bridges

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

    graph, edge_types = _build_graph(avoid, use_bridges=use_bridges)
    path_names, total_cost = _dijkstra(graph, from_system, to_system, profile)
    if not path_names:
        raise ValueError("No route found")

    hops: list[RouteHop] = []
    total_risk = 0.0
    max_risk = 0.0
    cumulative_cost = 0.0
    bridges_used = 0

    for idx, name in enumerate(path_names):
        rr = compute_risk(name)
        total_risk += rr.score
        max_risk = max(max_risk, rr.score)

        # Determine connection type
        connection_type = EDGE_GATE
        if idx > 0:
            prev_name = path_names[idx - 1]
            edge_cost = graph[prev_name][name]
            cumulative_cost += edge_cost
            connection_type = edge_types.get((prev_name, name), EDGE_GATE)
            if connection_type == EDGE_BRIDGE:
                bridges_used += 1

        hops.append(
            RouteHop(
                system_name=name,
                system_id=universe.systems[name].id,
                cumulative_jumps=idx,
                cumulative_cost=cumulative_cost,
                risk_score=rr.score,
                connection_type=connection_type,
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
        bridges_used=bridges_used,
    )
