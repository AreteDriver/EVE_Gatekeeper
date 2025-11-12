"""Graph algorithms for route planning and analysis."""

from typing import Dict, List, Set, Tuple, Optional
from collections import deque
import heapq
import json
from sqlalchemy.orm import Session
from .database import DatabaseManager, System, Stargate


class GraphEngine:
    """Build and analyze system jump graph."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize graph engine.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.adjacency_list = {}  # system_id -> [system_id, ...]
        self._built = False

    def build_from_db(self):
        """Build adjacency list from database stargates.

        This is called once to cache the graph in memory for fast queries.
        """
        print("Building adjacency list from database...")
        session = self.db.get_session()

        try:
            # Initialize all systems
            all_systems = session.query(System).all()
            for system in all_systems:
                self.adjacency_list[system.system_id] = set()

            # Add edges from stargates
            stargates = session.query(Stargate).all()
            count = 0

            for stargate in stargates:
                source = stargate.system_id
                dest = stargate.destination_system_id

                # Add bidirectional edge
                if source in self.adjacency_list:
                    self.adjacency_list[source].add(dest)
                if dest in self.adjacency_list:
                    self.adjacency_list[dest].add(source)

                count += 1
                if count % 10000 == 0:
                    print(f"  Processed {count} stargates...")

            self._built = True
            print(f"✓ Graph built with {len(self.adjacency_list)} nodes and {count} edges")

        finally:
            session.close()

    def shortest_path(self, origin_id: int, destination_id: int,
                     avoid_systems: Set[int] = None,
                     avoid_regions: Set[int] = None) -> Optional[List[int]]:
        """Find shortest jump path using Dijkstra's algorithm.

        Args:
            origin_id: Starting system ID
            destination_id: Target system ID
            avoid_systems: Systems to avoid (set of system IDs)
            avoid_regions: Regions to avoid (set of region IDs)

        Returns:
            List of system IDs in route, or None if no path
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        if origin_id not in self.adjacency_list or destination_id not in self.adjacency_list:
            return None

        if origin_id == destination_id:
            return [origin_id]

        avoid_systems = avoid_systems or set()
        avoid_regions = avoid_regions or set()

        # Get region map for region avoidance
        session = self.db.get_session()
        try:
            system_regions = {}
            if avoid_regions:
                all_systems = session.query(System).filter(System.region_id.in_(avoid_regions)).all()
                for sys in all_systems:
                    system_regions[sys.system_id] = sys.region_id

            # Dijkstra's algorithm
            distances = {origin_id: 0}
            previous = {origin_id: None}
            unvisited = [(0, origin_id)]

            while unvisited:
                current_dist, current = heapq.heappop(unvisited)

                # Skip if already processed with shorter distance
                if current_dist > distances.get(current, float('inf')):
                    continue

                if current == destination_id:
                    # Reconstruct path
                    path = []
                    node = destination_id
                    while node is not None:
                        path.append(node)
                        node = previous[node]
                    return path[::-1]

                # Check neighbors
                for neighbor in self.adjacency_list.get(current, []):
                    # Skip avoided systems and regions
                    if neighbor in avoid_systems:
                        continue
                    if avoid_regions and system_regions.get(neighbor) in avoid_regions:
                        continue

                    new_dist = current_dist + 1
                    if new_dist < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        heapq.heappush(unvisited, (new_dist, neighbor))

            return None  # No path found

        finally:
            session.close()

    def get_neighbors(self, system_id: int) -> List[int]:
        """Get directly connected systems (1 jump away).

        Args:
            system_id: System ID

        Returns:
            List of adjacent system IDs
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        return list(self.adjacency_list.get(system_id, []))

    def get_systems_within_jumps(self, origin_id: int, max_jumps: int) -> Set[int]:
        """Get all systems reachable within N jumps.

        Args:
            origin_id: Starting system ID
            max_jumps: Maximum jumps allowed

        Returns:
            Set of reachable system IDs
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        if origin_id not in self.adjacency_list:
            return set()

        visited = {origin_id}
        current_level = {origin_id}

        for jump_count in range(max_jumps):
            next_level = set()
            for system_id in current_level:
                for neighbor in self.adjacency_list.get(system_id, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_level.add(neighbor)

            current_level = next_level
            if not current_level:
                break

        return visited

    def find_hubs(self, top_n: int = 20) -> List[Tuple[int, str, int]]:
        """Find most connected systems (hubs).

        Args:
            top_n: Number of hubs to return

        Returns:
            List of (system_id, system_name, connection_count) tuples
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        session = self.db.get_session()

        try:
            # Count connections for each system
            connection_counts = {}
            for system_id, neighbors in self.adjacency_list.items():
                connection_counts[system_id] = len(neighbors)

            # Sort by connections
            sorted_hubs = sorted(
                connection_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]

            # Fetch system names
            result = []
            for system_id, count in sorted_hubs:
                system = session.query(System).filter_by(system_id=system_id).first()
                if system:
                    result.append((system_id, system.name, count))

            return result

        finally:
            session.close()

    def find_bottlenecks(self, top_n: int = 20) -> List[Tuple[int, str, float]]:
        """Find critical systems (high betweenness centrality).

        Uses approximation: systems with high degree that separate regions.

        Args:
            top_n: Number of bottlenecks to return

        Returns:
            List of (system_id, system_name, score) tuples
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        session = self.db.get_session()

        try:
            # Simple heuristic: high-degree nodes in low-density subgraphs
            bottleneck_scores = {}

            for system_id, neighbors in self.adjacency_list.items():
                degree = len(neighbors)

                # Calculate connectivity of neighbors
                neighbor_degrees = [len(self.adjacency_list.get(n, [])) for n in neighbors]
                avg_neighbor_degree = sum(neighbor_degrees) / len(neighbor_degrees) if neighbor_degrees else 0

                # Bottleneck score: high degree but neighbors have lower degree
                # (suggests it connects disparate regions)
                if avg_neighbor_degree > 0:
                    score = degree / (1 + avg_neighbor_degree)
                else:
                    score = degree

                bottleneck_scores[system_id] = score

            # Sort by score
            sorted_bottlenecks = sorted(
                bottleneck_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]

            # Fetch system names
            result = []
            for system_id, score in sorted_bottlenecks:
                system = session.query(System).filter_by(system_id=system_id).first()
                if system:
                    result.append((system_id, system.name, score))

            return result

        finally:
            session.close()

    def find_isolated_systems(self) -> List[Tuple[int, str]]:
        """Find systems with no stargate connections.

        Returns:
            List of (system_id, system_name) tuples
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        session = self.db.get_session()

        try:
            isolated = []
            for system_id, neighbors in self.adjacency_list.items():
                if not neighbors:
                    system = session.query(System).filter_by(system_id=system_id).first()
                    if system:
                        isolated.append((system_id, system.name))

            return sorted(isolated, key=lambda x: x[1])

        finally:
            session.close()

    def get_region_connectivity(self) -> Dict[int, Dict]:
        """Analyze connectivity within regions.

        Returns:
            Dict mapping region_id to metrics
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        session = self.db.get_session()

        try:
            # Group systems by region
            regions = {}
            systems = session.query(System).all()

            for system in systems:
                region_id = system.region_id
                if region_id not in regions:
                    regions[region_id] = {
                        'name': '',
                        'systems': [],
                        'internal_edges': 0,
                        'external_edges': 0,
                    }
                regions[region_id]['systems'].append(system.system_id)

            # Get region names
            from .database import Region
            region_names = {r.region_id: r.name for r in session.query(Region).all()}
            for region_id in regions:
                regions[region_id]['name'] = region_names.get(region_id, 'Unknown')

            # Count edges
            for region_id, data in regions.items():
                region_systems = set(data['systems'])

                for system_id in region_systems:
                    neighbors = self.adjacency_list.get(system_id, [])
                    for neighbor in neighbors:
                        if neighbor in region_systems:
                            data['internal_edges'] += 1
                        else:
                            data['external_edges'] += 1

                # Normalize
                data['internal_edges'] = data['internal_edges'] // 2  # Undirected
                data['internal_density'] = (
                    data['internal_edges'] / (len(region_systems) * (len(region_systems) - 1) / 2)
                    if len(region_systems) > 1 else 0
                )

            return regions

        finally:
            session.close()

    def export_adjacency_list(self) -> Dict[int, List[int]]:
        """Export adjacency list as dict (for caching/serialization).

        Returns:
            Dict mapping system_id to list of adjacent system IDs
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        return {k: list(v) for k, v in self.adjacency_list.items()}

    def export_as_json(self, filepath: str):
        """Export graph as JSON for mobile clients.

        Args:
            filepath: Path to save JSON file
        """
        if not self._built:
            raise ValueError("Graph not built. Call build_from_db() first.")

        session = self.db.get_session()

        try:
            print(f"Exporting graph to {filepath}...")

            # Build lightweight graph
            systems_map = {}
            systems = session.query(System).all()

            for system in systems:
                systems_map[system.system_id] = {
                    'id': system.system_id,
                    'name': system.name,
                    'region_id': system.region_id,
                    'security': system.security_status,
                    'x': system.x,
                    'y': system.y,
                    'z': system.z,
                }

            # Build edges
            edges = []
            seen = set()

            for system_id, neighbors in self.adjacency_list.items():
                for neighbor_id in neighbors:
                    edge = tuple(sorted([system_id, neighbor_id]))
                    if edge not in seen:
                        seen.add(edge)
                        edges.append([system_id, neighbor_id])

            graph_data = {
                'version': '1.0',
                'nodes': systems_map,
                'edges': edges,
                'stats': {
                    'total_systems': len(systems_map),
                    'total_connections': len(edges),
                }
            }

            # Write to file
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(graph_data, f, separators=(',', ':'))

            print(f"✓ Exported {len(systems_map)} systems and {len(edges)} connections")

        finally:
            session.close()


# Import at end to avoid circular imports
import os
