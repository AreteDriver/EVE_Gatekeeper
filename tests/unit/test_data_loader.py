"""Unit tests for data loader."""

import pytest

from backend.app.services.data_loader import load_universe, load_risk_config, get_neighbors


class TestLoadUniverse:
    """Tests for load_universe function."""

    def test_load_universe_returns_universe(self):
        """Test that load_universe returns a Universe object."""
        universe = load_universe()

        assert universe is not None
        assert universe.metadata is not None
        assert universe.systems is not None
        assert universe.gates is not None

    def test_load_universe_has_systems(self):
        """Test that universe contains expected systems."""
        universe = load_universe()

        assert "Jita" in universe.systems
        assert "Perimeter" in universe.systems
        assert "Niarja" in universe.systems

    def test_load_universe_system_properties(self):
        """Test that systems have expected properties."""
        universe = load_universe()
        jita = universe.systems["Jita"]

        assert jita.id == 30000142
        assert jita.region_id == 10000002
        assert jita.security == 0.95  # Real Jita security from SDE
        assert jita.category == "highsec"
        assert jita.position is not None

    def test_load_universe_has_gates(self):
        """Test that universe contains gates."""
        universe = load_universe()

        assert len(universe.gates) >= 2


class TestLoadRiskConfig:
    """Tests for load_risk_config function."""

    def test_load_risk_config_returns_config(self):
        """Test that load_risk_config returns a RiskConfig object."""
        config = load_risk_config()

        assert config is not None

    def test_load_risk_config_has_security_weights(self):
        """Test that config has security category weights."""
        config = load_risk_config()

        assert "highsec" in config.security_category_weights
        assert "lowsec" in config.security_category_weights
        assert "nullsec" in config.security_category_weights

    def test_load_risk_config_has_routing_profiles(self):
        """Test that config has routing profiles."""
        config = load_risk_config()

        assert "shortest" in config.routing_profiles
        assert "safer" in config.routing_profiles
        assert "paranoid" in config.routing_profiles

    def test_load_risk_config_has_risk_colors(self):
        """Test that config has risk color bands."""
        config = load_risk_config()

        assert len(config.risk_colors) > 0


class TestGetNeighbors:
    """Tests for get_neighbors function."""

    def test_get_neighbors_jita(self):
        """Test getting neighbors of Jita."""
        neighbors = get_neighbors("Jita")

        assert len(neighbors) >= 1
        # Jita should connect to Perimeter
        neighbor_systems = [g.to_system if g.from_system == "Jita" else g.from_system for g in neighbors]
        assert "Perimeter" in neighbor_systems

    def test_get_neighbors_perimeter(self):
        """Test getting neighbors of Perimeter."""
        neighbors = get_neighbors("Perimeter")

        # Perimeter connects to both Jita and Niarja
        assert len(neighbors) >= 2

    def test_get_neighbors_nonexistent(self):
        """Test getting neighbors of nonexistent system returns empty."""
        neighbors = get_neighbors("NonExistentSystem")

        assert len(neighbors) == 0
