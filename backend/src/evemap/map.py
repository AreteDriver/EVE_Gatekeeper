"""2D Map visualization for New Eden."""

import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List, Optional, Tuple, Set
from matplotlib.colors import Normalize, LinearSegmentedColormap
import numpy as np

from .models import System, Region, Constellation, JumpConnection, SecurityStatus


class NedenMap:
    """2D node-based map visualization of New Eden."""

    # Color schemes
    SECURITY_COLORS = {
        SecurityStatus.HIGH_SEC: '#3366FF',      # Blue
        SecurityStatus.LOW_SEC: '#FF9900',       # Orange
        SecurityStatus.NULL_SEC: '#FF0000',      # Red
        SecurityStatus.WORMHOLE: '#9933FF',      # Purple
    }

    def __init__(self, systems: Dict[int, System], connections: List[JumpConnection]):
        """Initialize the map with systems and connections.

        Args:
            systems: Dictionary of System objects by system_id
            connections: List of JumpConnection objects
        """
        self.systems = systems
        self.connections = connections
        self.graph = self._build_graph()
        self.layout = None
        self.figure = None
        self.ax = None

    def _build_graph(self) -> nx.Graph:
        """Build a networkx graph from systems and connections.

        Returns:
            NetworkX graph object
        """
        G = nx.Graph()

        # Add systems as nodes
        for system_id, system in self.systems.items():
            G.add_node(system_id, system=system)

        # Add jump connections as edges
        for connection in self.connections:
            if (connection.source_system_id in self.systems and
                connection.target_system_id in self.systems):
                G.add_edge(
                    connection.source_system_id,
                    connection.target_system_id,
                    distance=connection.distance
                )

        return G

    def calculate_layout(self, method: str = "spring", seed: int = 42,
                        iterations: int = 50) -> Dict[int, Tuple[float, float]]:
        """Calculate node positions for visualization.

        Args:
            method: Layout algorithm ("spring", "kamada_kawai", "circular", "shell")
            seed: Random seed for reproducibility
            iterations: Number of iterations for iterative algorithms

        Returns:
            Dictionary mapping node IDs to (x, y) positions
        """
        print(f"Calculating {method} layout with {iterations} iterations...")

        if method == "spring":
            # Force-directed layout (good for general graphs)
            self.layout = nx.spring_layout(
                self.graph,
                k=2,
                iterations=iterations,
                seed=seed,
                weight=None,  # Don't use edge weights
            )
        elif method == "kamada_kawai":
            # Physics-based layout (good for small graphs)
            self.layout = nx.kamada_kawai_layout(self.graph)
        elif method == "circular":
            # Circular layout
            self.layout = nx.circular_layout(self.graph)
        elif method == "shell":
            # Concentric shells (good for hierarchical data)
            self.layout = nx.shell_layout(self.graph)
        else:
            raise ValueError(f"Unknown layout method: {method}")

        # Update system positions
        for system_id, (x, y) in self.layout.items():
            if system_id in self.systems:
                self.systems[system_id].x = x
                self.systems[system_id].y = y

        return self.layout

    def render(self, figsize: Tuple[int, int] = (20, 16), dpi: int = 100,
               group_by: Optional[str] = None, filter_security: Optional[Set[SecurityStatus]] = None,
               show_labels: bool = True, show_edges: bool = True) -> plt.Figure:
        """Render the map visualization.

        Args:
            figsize: Figure size in inches (width, height)
            dpi: Dots per inch
            group_by: Group by region/constellation ("region", "constellation", or None)
            filter_security: Set of SecurityStatus to show (None = show all)
            show_labels: Whether to show system names
            show_edges: Whether to show jump connections

        Returns:
            Matplotlib figure object
        """
        if self.layout is None:
            raise ValueError("Layout not calculated. Call calculate_layout() first.")

        self.figure, self.ax = plt.subplots(figsize=figsize, dpi=dpi)

        # Filter systems
        filtered_systems = self.systems
        if filter_security:
            filtered_systems = {
                sid: s for sid, s in self.systems.items()
                if s.security_class in filter_security
            }

        # Draw edges (jump connections)
        if show_edges:
            self._draw_edges(filtered_systems)

        # Draw nodes (systems)
        self._draw_nodes(filtered_systems, group_by)

        # Draw labels
        if show_labels:
            self._draw_labels(filtered_systems)

        # Configure axes
        self.ax.set_title("New Eden - 2D Map", fontsize=20, fontweight='bold', pad=20)
        self.ax.set_xlabel("X Position", fontsize=12)
        self.ax.set_ylabel("Y Position", fontsize=12)
        self.ax.grid(True, alpha=0.2)
        self.ax.set_aspect('equal')

        # Add legend
        self._add_legend(group_by)

        plt.tight_layout()
        return self.figure

    def _draw_edges(self, systems: Dict[int, System]):
        """Draw jump connections as edges.

        Args:
            systems: Dictionary of systems to visualize
        """
        edges = []
        for connection in self.connections:
            if (connection.source_system_id in systems and
                connection.target_system_id in systems):
                edges.append((connection.source_system_id, connection.target_system_id))

        if not edges:
            return

        edge_x = []
        edge_y = []

        for source, target in edges:
            x0, y0 = self.layout[source]
            x1, y1 = self.layout[target]
            edge_x.append((x0, x1, None))
            edge_y.append((y0, y1, None))

        for ex, ey in zip(edge_x, edge_y):
            self.ax.plot(ex, ey, 'gray', alpha=0.3, linewidth=0.5, zorder=1)

    def _draw_nodes(self, systems: Dict[int, System], group_by: Optional[str] = None):
        """Draw systems as nodes.

        Args:
            systems: Dictionary of systems to visualize
            group_by: Grouping method ("region", "constellation", or None)
        """
        if not systems:
            return

        # Organize systems by group
        groups = {}
        if group_by == "region":
            for system in systems.values():
                region_id = system.region_id
                if region_id not in groups:
                    groups[region_id] = []
                groups[region_id].append(system)
        elif group_by == "constellation":
            for system in systems.values():
                const_id = system.constellation_id
                if const_id not in groups:
                    groups[const_id] = []
                groups[const_id].append(system)
        else:
            # No grouping - use security status
            for system in systems.values():
                sec_class = system.security_class
                if sec_class not in groups:
                    groups[sec_class] = []
                groups[sec_class].append(system)

        # Draw nodes by group
        if group_by and group_by != "security":
            # Multi-color for regions/constellations
            colors = plt.cm.tab20(np.linspace(0, 1, len(groups)))
            for (group_id, group_systems), color in zip(groups.items(), colors):
                x_pos = [self.layout[s.system_id][0] for s in group_systems]
                y_pos = [self.layout[s.system_id][1] for s in group_systems]
                self.ax.scatter(x_pos, y_pos, c=[color], s=100, alpha=0.7, zorder=2,
                               edgecolors='black', linewidth=0.5)
        else:
            # Color by security status
            for sec_class in SecurityStatus:
                group_systems = groups.get(sec_class, [])
                if not group_systems:
                    continue
                x_pos = [self.layout[s.system_id][0] for s in group_systems]
                y_pos = [self.layout[s.system_id][1] for s in group_systems]
                color = self.SECURITY_COLORS[sec_class]
                self.ax.scatter(x_pos, y_pos, c=color, s=100, alpha=0.7, zorder=2,
                               edgecolors='black', linewidth=0.5, label=sec_class.value)

    def _draw_labels(self, systems: Dict[int, System], fontsize: int = 6):
        """Draw system names as labels.

        Args:
            systems: Dictionary of systems to visualize
            fontsize: Font size for labels
        """
        for system in systems.values():
            x, y = self.layout[system.system_id]
            self.ax.text(x, y, system.name, fontsize=fontsize, ha='center', va='center',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.5),
                        zorder=3)

    def _add_legend(self, group_by: Optional[str] = None):
        """Add legend to the visualization.

        Args:
            group_by: Grouping method
        """
        if not group_by or group_by == "security":
            # Security status legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor=self.SECURITY_COLORS[SecurityStatus.HIGH_SEC],
                      edgecolor='black', label='High Sec'),
                Patch(facecolor=self.SECURITY_COLORS[SecurityStatus.LOW_SEC],
                      edgecolor='black', label='Low Sec'),
                Patch(facecolor=self.SECURITY_COLORS[SecurityStatus.NULL_SEC],
                      edgecolor='black', label='Null Sec'),
                Patch(facecolor=self.SECURITY_COLORS[SecurityStatus.WORMHOLE],
                      edgecolor='black', label='Wormhole'),
            ]
            self.ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    def save(self, filename: str, dpi: int = 150):
        """Save the visualization to a file.

        Args:
            filename: Output filename
            dpi: Resolution in dots per inch
        """
        if self.figure is None:
            raise ValueError("No figure rendered. Call render() first.")
        self.figure.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Map saved to {filename}")

    def show(self):
        """Display the visualization."""
        if self.figure is None:
            raise ValueError("No figure rendered. Call render() first.")
        plt.show()

    def get_stats(self) -> Dict[str, any]:
        """Get statistics about the map.

        Returns:
            Dictionary with map statistics
        """
        security_counts = {}
        for sec_class in SecurityStatus:
            count = sum(1 for s in self.systems.values() if s.security_class == sec_class)
            security_counts[sec_class.value] = count

        return {
            "total_systems": len(self.systems),
            "total_connections": len(self.connections),
            "security_breakdown": security_counts,
            "avg_connections_per_system": (
                2 * len(self.connections) / len(self.systems)
                if self.systems else 0
            ),
        }
