"""Tests for jump bridge service."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.app.models.jumpbridge import (
    JumpBridge,
    JumpBridgeConfig,
    JumpBridgeNetwork,
)
from backend.app.services.jumpbridge import (
    clear_bridge_cache,
    load_bridge_config,
    parse_bridge_text,
    save_bridge_config,
)


@pytest.fixture
def mock_universe():
    """Create a mock universe with known systems."""
    mock = MagicMock()
    mock.systems = {
        "Jita": MagicMock(),
        "Amarr": MagicMock(),
        "Dodixie": MagicMock(),
        "HED-GP": MagicMock(),
        "1DQ1-A": MagicMock(),
        "8QT-H4": MagicMock(),
        "Perimeter": MagicMock(),
    }
    return mock


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    return tmp_path


class TestParseBridgeText:
    """Tests for parse_bridge_text function."""

    def test_parse_arrow_format(self, mock_universe):
        """Should parse 'System1 <-> System2' format."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("Jita <-> Amarr")

        assert len(bridges) == 1
        assert len(errors) == 0
        assert bridges[0].from_system == "Jita"
        assert bridges[0].to_system == "Amarr"

    def test_parse_double_arrow_format(self, mock_universe):
        """Should parse 'System1 --> System2' format."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("Jita --> Amarr")

        assert len(bridges) == 1
        assert bridges[0].from_system == "Jita"
        assert bridges[0].to_system == "Amarr"

    def test_parse_angle_bracket_format(self, mock_universe):
        """Should parse 'System1 <> System2' format."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("Jita <> Amarr")

        assert len(bridges) == 1

    def test_parse_dash_format(self, mock_universe):
        """Should parse 'System1 - System2' format."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("Jita - Amarr")

        assert len(bridges) == 1

    def test_parse_multiple_bridges(self, mock_universe):
        """Should parse multiple bridges."""
        text = """
        Jita <-> Amarr
        Dodixie <-> HED-GP
        1DQ1-A <-> 8QT-H4
        """
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text(text)

        assert len(bridges) == 3
        assert len(errors) == 0

    def test_skip_comments(self, mock_universe):
        """Should skip lines starting with #."""
        text = """
        # This is a comment
        Jita <-> Amarr
        # Another comment
        """
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text(text)

        assert len(bridges) == 1

    def test_skip_empty_lines(self, mock_universe):
        """Should skip empty lines."""
        text = """
        Jita <-> Amarr

        Dodixie <-> HED-GP

        """
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text(text)

        assert len(bridges) == 2

    def test_unknown_system_error(self, mock_universe):
        """Should report error for unknown systems."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("Jita <-> UnknownSystem")

        assert len(bridges) == 0
        assert len(errors) == 1
        assert "Unknown system" in errors[0]
        assert "UnknownSystem" in errors[0]

    def test_unknown_first_system_error(self, mock_universe):
        """Should report error for unknown first system."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("FakeSystem <-> Jita")

        assert len(bridges) == 0
        assert len(errors) == 1
        assert "FakeSystem" in errors[0]

    def test_unparseable_line_error(self, mock_universe):
        """Should report error for unparseable lines."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("this is not a valid format")

        assert len(bridges) == 0
        assert len(errors) == 1
        assert "Could not parse" in errors[0]

    def test_deduplicate_bridges(self, mock_universe):
        """Should skip duplicate bridges."""
        text = """
        Jita <-> Amarr
        Jita <-> Amarr
        Amarr <-> Jita
        """
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text(text)

        # All three are duplicates (same connection), only first should be kept
        assert len(bridges) == 1

    def test_whitespace_handling(self, mock_universe):
        """Should handle extra whitespace."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, errors = parse_bridge_text("  Jita   <->   Amarr  ")

        assert len(bridges) == 1
        assert bridges[0].from_system == "Jita"
        assert bridges[0].to_system == "Amarr"

    def test_returns_jump_bridge_objects(self, mock_universe):
        """Should return JumpBridge objects."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, _ = parse_bridge_text("Jita <-> Amarr")

        assert isinstance(bridges[0], JumpBridge)

    def test_bridge_has_none_structure_id(self, mock_universe):
        """Parsed bridges should have None structure_id."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, _ = parse_bridge_text("Jita <-> Amarr")

        assert bridges[0].structure_id is None

    def test_bridge_has_none_owner(self, mock_universe):
        """Parsed bridges should have None owner."""
        with patch("backend.app.services.jumpbridge.load_universe", return_value=mock_universe):
            bridges, _ = parse_bridge_text("Jita <-> Amarr")

        assert bridges[0].owner is None


class TestJumpBridgeConfig:
    """Tests for JumpBridgeConfig model."""

    def test_empty_config(self):
        """Should create empty config."""
        config = JumpBridgeConfig(networks=[])
        assert config.networks == []

    def test_get_active_bridges_all_enabled(self):
        """Should return all bridges when all networks enabled."""
        bridge1 = JumpBridge(from_system="A", to_system="B")
        bridge2 = JumpBridge(from_system="C", to_system="D")

        network1 = JumpBridgeNetwork(name="Net1", bridges=[bridge1], enabled=True)
        network2 = JumpBridgeNetwork(name="Net2", bridges=[bridge2], enabled=True)

        config = JumpBridgeConfig(networks=[network1, network2])
        active = config.get_active_bridges()

        assert len(active) == 2

    def test_get_active_bridges_some_disabled(self):
        """Should only return bridges from enabled networks."""
        bridge1 = JumpBridge(from_system="A", to_system="B")
        bridge2 = JumpBridge(from_system="C", to_system="D")

        network1 = JumpBridgeNetwork(name="Net1", bridges=[bridge1], enabled=True)
        network2 = JumpBridgeNetwork(name="Net2", bridges=[bridge2], enabled=False)

        config = JumpBridgeConfig(networks=[network1, network2])
        active = config.get_active_bridges()

        assert len(active) == 1
        assert active[0].from_system == "A"

    def test_get_active_bridges_all_disabled(self):
        """Should return empty list when all networks disabled."""
        bridge1 = JumpBridge(from_system="A", to_system="B")
        network1 = JumpBridgeNetwork(name="Net1", bridges=[bridge1], enabled=False)

        config = JumpBridgeConfig(networks=[network1])
        active = config.get_active_bridges()

        assert len(active) == 0


class TestJumpBridgeNetwork:
    """Tests for JumpBridgeNetwork model."""

    def test_default_enabled(self):
        """Network should be enabled by default."""
        network = JumpBridgeNetwork(name="Test", bridges=[])
        assert network.enabled is True

    def test_empty_bridges_list(self):
        """Network should have empty bridges by default."""
        network = JumpBridgeNetwork(name="Test")
        assert network.bridges == []


class TestJumpBridge:
    """Tests for JumpBridge model."""

    def test_required_fields(self):
        """Should require from_system and to_system."""
        bridge = JumpBridge(from_system="A", to_system="B")
        assert bridge.from_system == "A"
        assert bridge.to_system == "B"

    def test_optional_fields_default_none(self):
        """Optional fields should default to None."""
        bridge = JumpBridge(from_system="A", to_system="B")
        assert bridge.structure_id is None
        assert bridge.owner is None

    def test_with_all_fields(self):
        """Should accept all fields."""
        bridge = JumpBridge(
            from_system="A",
            to_system="B",
            structure_id=123456789,
            owner="Test Alliance"
        )
        assert bridge.structure_id == 123456789
        assert bridge.owner == "Test Alliance"


class TestLoadSaveBridgeConfig:
    """Tests for load_bridge_config and save_bridge_config."""

    def test_load_creates_empty_config_if_no_file(self, tmp_path):
        """Should create empty config if file doesn't exist."""
        clear_bridge_cache()
        with patch("backend.app.services.jumpbridge.get_bridge_config_path", return_value=tmp_path / "bridges.json"):
            config = load_bridge_config()

        assert config.networks == []

    def test_save_and_load_roundtrip(self, tmp_path):
        """Should be able to save and load config."""
        config_path = tmp_path / "bridges.json"
        clear_bridge_cache()

        bridge = JumpBridge(from_system="Jita", to_system="Amarr")
        network = JumpBridgeNetwork(name="TestNet", bridges=[bridge], enabled=True)
        config = JumpBridgeConfig(networks=[network])

        with patch("backend.app.services.jumpbridge.get_bridge_config_path", return_value=config_path):
            save_bridge_config(config)
            clear_bridge_cache()
            loaded = load_bridge_config()

        assert len(loaded.networks) == 1
        assert loaded.networks[0].name == "TestNet"
        assert len(loaded.networks[0].bridges) == 1

    def test_load_caches_config(self, tmp_path):
        """Should cache loaded config."""
        config_path = tmp_path / "bridges.json"
        config_path.write_text('{"networks": []}')
        clear_bridge_cache()

        with patch("backend.app.services.jumpbridge.get_bridge_config_path", return_value=config_path):
            config1 = load_bridge_config()
            config2 = load_bridge_config()

        assert config1 is config2

    def test_clear_cache_forces_reload(self, tmp_path):
        """Clearing cache should force reload on next load."""
        config_path = tmp_path / "bridges.json"
        config_path.write_text('{"networks": []}')

        with patch("backend.app.services.jumpbridge.get_bridge_config_path", return_value=config_path):
            clear_bridge_cache()
            config1 = load_bridge_config()
            clear_bridge_cache()
            config2 = load_bridge_config()

        # After clearing, should be different objects (reloaded)
        assert config1 is not config2
