"""Utility functions for map analysis and visualization."""

from typing import Dict, List, Set, Tuple
from .models import System, JumpConnection
import math


class JumpRangeCalculator:
    """Calculate and visualize ship jump ranges on the map."""

    # Standard jump drives in EVE
    JUMP_DRIVE_RANGES = {
        "Battleship": 5,      # 5 LY base (with maxed skills)
        "Dreadnought": 6,     # 6 LY base
        "Carrier": 6,         # 6 LY base
        "Supercarrier": 7,    # 7 LY base
        "Freighter": 5,       # 5 LY base (Anshar, Lif, etc.)
    }

    def __init__(self, systems: Dict[int, System], connections: List[JumpConnection]):
        """Initialize calculator.

        Args:
            systems: Dictionary of systems
            connections: List of jump connections
        """
        self.systems = systems
        self.connections = connections
        self._build_distance_map()

    def _build_distance_map(self):
        """Build a map of system positions for distance calculations."""
        self.system_positions = {}
        for system_id, system in self.systems.items():
            if system.x is not None and system.y is not None:
                self.system_positions[system_id] = (system.x, system.y)

    def get_distance(self, system1_id: int, system2_id: int) -> float:
        """Calculate Euclidean distance between two systems.

        Args:
            system1_id: First system ID
            system2_id: Second system ID

        Returns:
            Distance in abstract units
        """
        if system1_id not in self.system_positions or system2_id not in self.system_positions:
            return float('inf')

        x1, y1 = self.system_positions[system1_id]
        x2, y2 = self.system_positions[system2_id]

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def get_systems_in_range(self, origin_id: int, range_ly: float) -> Set[int]:
        """Get all systems within jump range of origin.

        Args:
            origin_id: Origin system ID
            range_ly: Jump range in light-years

        Returns:
            Set of system IDs within range
        """
        if origin_id not in self.systems:
            return set()

        reachable = set()
        origin_x = self.systems[origin_id].x or 0
        origin_y = self.systems[origin_id].y or 0

        for system_id, system in self.systems.items():
            if system_id == origin_id:
                continue

            sys_x = system.x or 0
            sys_y = system.y or 0

            distance = math.sqrt((sys_x - origin_x) ** 2 + (sys_y - origin_y) ** 2)

            # Normalize by average connection distance
            if distance <= range_ly:
                reachable.add(system_id)

        return reachable

    def get_route_via_jumps(self, origin_id: int, destination_id: int,
                           max_jumps: int = 20) -> List[int]:
        """Calculate shortest jump route between systems (BFS).

        Args:
            origin_id: Starting system ID
            destination_id: Target system ID
            max_jumps: Maximum jumps to consider

        Returns:
            List of system IDs representing the route
        """
        from collections import deque

        if origin_id not in self.systems or destination_id not in self.systems:
            return []

        # Build adjacency list from connections
        graph = {}
        for system_id in self.systems:
            graph[system_id] = set()

        for conn in self.connections:
            if conn.source_system_id in self.systems and conn.target_system_id in self.systems:
                graph[conn.source_system_id].add(conn.target_system_id)
                graph[conn.target_system_id].add(conn.source_system_id)

        # BFS to find shortest path
        queue = deque([(origin_id, [origin_id])])
        visited = {origin_id}

        while queue:
            current, path = queue.popleft()

            if current == destination_id:
                return path

            if len(path) >= max_jumps:
                continue

            for neighbor in graph.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []  # No route found


class MapAnalyzer:
    """Analyze map properties and statistics."""

    def __init__(self, systems: Dict[int, System], connections: List[JumpConnection]):
        """Initialize analyzer.

        Args:
            systems: Dictionary of systems
            connections: List of jump connections
        """
        self.systems = systems
        self.connections = connections

    def get_hub_systems(self, top_n: int = 10) -> List[Tuple[int, str, int]]:
        """Find most connected systems (hubs).

        Args:
            top_n: Number of top hubs to return

        Returns:
            List of (system_id, name, connection_count) tuples
        """
        connection_counts = {}

        for conn in self.connections:
            connection_counts[conn.source_system_id] = connection_counts.get(conn.source_system_id, 0) + 1
            connection_counts[conn.target_system_id] = connection_counts.get(conn.target_system_id, 0) + 1

        # Sort by connection count
        sorted_hubs = sorted(
            connection_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        return [
            (system_id, self.systems[system_id].name, count)
            for system_id, count in sorted_hubs
            if system_id in self.systems
        ]

    def get_isolated_systems(self) -> List[Tuple[int, str]]:
        """Find systems with no jump connections.

        Returns:
            List of (system_id, name) tuples
        """
        connected = set()
        for conn in self.connections:
            connected.add(conn.source_system_id)
            connected.add(conn.target_system_id)

        isolated = [
            (sid, s.name)
            for sid, s in self.systems.items()
            if sid not in connected
        ]

        return isolated

    def get_region_stats(self) -> Dict[str, Dict]:
        """Get statistics grouped by region.

        Returns:
            Dictionary with stats per region
        """
        regions = {}

        for system in self.systems.values():
            region_id = system.region_id
            if region_id not in regions:
                regions[region_id] = {
                    'systems': [],
                    'security_count': {'high': 0, 'low': 0, 'null': 0},
                }
            regions[region_id]['systems'].append(system)

        # Calculate stats for each region
        stats = {}
        for region_id, data in regions.items():
            systems = data['systems']
            stats[region_id] = {
                'count': len(systems),
                'avg_security': sum(s.security_status for s in systems) / len(systems),
                'high_sec': sum(1 for s in systems if s.security_status >= 0.45),
                'low_sec': sum(1 for s in systems if 0.1 <= s.security_status < 0.45),
                'null_sec': sum(1 for s in systems if s.security_status < 0.1),
            }

        return stats

    def get_connectivity_metrics(self) -> Dict[str, float]:
        """Get graph connectivity metrics.

        Returns:
            Dictionary with metrics
        """
        # Build adjacency list
        graph = {}
        for system_id in self.systems:
            graph[system_id] = set()

        for conn in self.connections:
            if conn.source_system_id in self.systems and conn.target_system_id in self.systems:
                graph[conn.source_system_id].add(conn.target_system_id)
                graph[conn.target_system_id].add(conn.source_system_id)

        # Calculate density
        max_edges = len(self.systems) * (len(self.systems) - 1) / 2
        actual_edges = len(self.connections)
        density = actual_edges / max_edges if max_edges > 0 else 0

        # Calculate average degree
        avg_degree = 2 * actual_edges / len(self.systems) if self.systems else 0

        return {
            'density': density,
            'average_degree': avg_degree,
            'total_systems': len(self.systems),
            'total_connections': len(self.connections),
        }
