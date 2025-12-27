"""Unit tests for routing service."""

import pytest

from backend.app.services.routing import compute_route, _build_graph, _dijkstra


class TestBuildGraph:
    """Tests for graph building function."""

    def test_build_graph_creates_bidirectional_edges(self):
        """Test that graph has bidirectional edges."""
        graph = _build_graph()

        # Jita -> Perimeter should exist
        assert "Perimeter" in graph["Jita"]
        # Perimeter -> Jita should also exist
        assert "Jita" in graph["Perimeter"]

    def test_build_graph_includes_all_systems(self):
        """Test that graph includes all systems."""
        graph = _build_graph()

        assert "Jita" in graph
        assert "Perimeter" in graph
        assert "Niarja" in graph


class TestDijkstra:
    """Tests for Dijkstra pathfinding."""

    def test_dijkstra_finds_direct_path(self):
        """Test finding a direct path between adjacent systems."""
        graph = _build_graph()
        path, cost = _dijkstra(graph, "Jita", "Perimeter", "shortest")

        assert path == ["Jita", "Perimeter"]
        assert cost == 1.0

    def test_dijkstra_finds_multi_hop_path(self):
        """Test finding a multi-hop path."""
        graph = _build_graph()
        path, cost = _dijkstra(graph, "Jita", "Niarja", "shortest")

        assert path == ["Jita", "Perimeter", "Niarja"]
        assert cost == 4.0  # 1 + 3

    def test_dijkstra_same_start_end(self):
        """Test path when start equals end."""
        graph = _build_graph()
        path, cost = _dijkstra(graph, "Jita", "Jita", "shortest")

        assert path == ["Jita"]
        assert cost == 0.0


class TestComputeRoute:
    """Tests for compute_route function."""

    def test_compute_route_basic(self):
        """Test basic route calculation."""
        response = compute_route("Jita", "Perimeter", "shortest")

        assert response.from_system == "Jita"
        assert response.to_system == "Perimeter"
        assert response.profile == "shortest"
        assert response.total_jumps == 1
        assert len(response.path) == 2

    def test_compute_route_path_details(self):
        """Test that route path contains proper hop details."""
        response = compute_route("Jita", "Niarja", "shortest")

        assert len(response.path) == 3

        # First hop
        assert response.path[0].system_name == "Jita"
        assert response.path[0].cumulative_jumps == 0

        # Last hop
        assert response.path[2].system_name == "Niarja"
        assert response.path[2].cumulative_jumps == 2

    def test_compute_route_risk_stats(self):
        """Test that route includes risk statistics."""
        response = compute_route("Jita", "Niarja", "shortest")

        assert response.max_risk >= 0
        assert response.avg_risk >= 0
        assert response.max_risk >= response.avg_risk or response.max_risk == response.avg_risk

    def test_compute_route_unknown_from_system(self):
        """Test error when from_system is unknown."""
        with pytest.raises(ValueError, match="Unknown from_system"):
            compute_route("NonExistent", "Jita", "shortest")

    def test_compute_route_unknown_to_system(self):
        """Test error when to_system is unknown."""
        with pytest.raises(ValueError, match="Unknown to_system"):
            compute_route("Jita", "NonExistent", "shortest")

    def test_compute_route_different_profiles(self):
        """Test that different profiles may produce different costs."""
        shortest = compute_route("Jita", "Niarja", "shortest")
        safer = compute_route("Jita", "Niarja", "safer")

        # Both should find a valid route
        assert shortest.total_jumps >= 1
        assert safer.total_jumps >= 1

        # Safer profile adds risk penalty, so cost should be >= shortest
        assert safer.total_cost >= shortest.total_cost

    def test_compute_route_cumulative_cost(self):
        """Test that cumulative cost increases along the path."""
        response = compute_route("Jita", "Niarja", "shortest")

        prev_cost = 0
        for hop in response.path:
            assert hop.cumulative_cost >= prev_cost
            prev_cost = hop.cumulative_cost
