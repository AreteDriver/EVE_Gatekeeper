"""Jump bridge management service."""

import json
import re
from pathlib import Path
from typing import List, Tuple

from ..core.config import settings
from ..models.jumpbridge import (
    JumpBridge,
    JumpBridgeNetwork,
    JumpBridgeConfig,
    JumpBridgeImportResponse,
)
from .data_loader import load_universe


# Cache for jump bridge config
_bridge_config: JumpBridgeConfig | None = None


def get_bridge_config_path() -> Path:
    """Get path to jump bridge config file."""
    return settings.DATA_DIR / "jumpbridges.json"


def load_bridge_config() -> JumpBridgeConfig:
    """Load jump bridge configuration from file."""
    global _bridge_config
    if _bridge_config is not None:
        return _bridge_config

    config_path = get_bridge_config_path()
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        _bridge_config = JumpBridgeConfig(**raw)
    else:
        _bridge_config = JumpBridgeConfig(networks=[])

    return _bridge_config


def save_bridge_config(config: JumpBridgeConfig) -> None:
    """Save jump bridge configuration to file."""
    global _bridge_config
    config_path = get_bridge_config_path()
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2)
    _bridge_config = config


def clear_bridge_cache() -> None:
    """Clear the cached bridge config."""
    global _bridge_config
    _bridge_config = None


def parse_bridge_text(text: str) -> Tuple[List[JumpBridge], List[str]]:
    """
    Parse jump bridge text format into bridge objects.

    Supported formats:
    - "System1 --> System2" (one-way, though bridges are bidirectional)
    - "System1 <-> System2" (explicit bidirectional)
    - "System1 <> System2" (alternate bidirectional)
    - "System1 - System2" (simple format)

    Args:
        text: Raw text with one bridge per line

    Returns:
        Tuple of (parsed bridges, error messages)
    """
    universe = load_universe()
    bridges: List[JumpBridge] = []
    errors: List[str] = []
    seen: set[tuple[str, str]] = set()

    # Patterns for different formats
    patterns = [
        r"^\s*(.+?)\s*<->\s*(.+?)\s*$",  # System1 <-> System2
        r"^\s*(.+?)\s*<>\s*(.+?)\s*$",   # System1 <> System2
        r"^\s*(.+?)\s*-->\s*(.+?)\s*$",  # System1 --> System2
        r"^\s*(.+?)\s*-\s*(.+?)\s*$",    # System1 - System2
    ]

    for line_num, line in enumerate(text.strip().split("\n"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        matched = False
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                sys1 = match.group(1).strip()
                sys2 = match.group(2).strip()

                # Validate systems exist
                if sys1 not in universe.systems:
                    errors.append(f"Line {line_num}: Unknown system '{sys1}'")
                    matched = True
                    break
                if sys2 not in universe.systems:
                    errors.append(f"Line {line_num}: Unknown system '{sys2}'")
                    matched = True
                    break

                # Create canonical key to avoid duplicates
                key = tuple(sorted([sys1, sys2]))
                if key in seen:
                    matched = True
                    break

                seen.add(key)
                bridges.append(JumpBridge(from_system=sys1, to_system=sys2))
                matched = True
                break

        if not matched:
            errors.append(f"Line {line_num}: Could not parse '{line}'")

    return bridges, errors


def import_bridges(
    network_name: str,
    bridge_text: str,
    replace: bool = True,
) -> JumpBridgeImportResponse:
    """
    Import jump bridges from text format.

    Args:
        network_name: Name for this bridge network
        bridge_text: Raw text with bridges
        replace: If True, replace existing network; if False, merge

    Returns:
        Import result with counts and errors
    """
    config = load_bridge_config()

    # Parse the bridges
    bridges, errors = parse_bridge_text(bridge_text)

    # Find or create network
    existing_network = None
    for network in config.networks:
        if network.name == network_name:
            existing_network = network
            break

    if existing_network:
        if replace:
            existing_network.bridges = bridges
        else:
            # Merge: add new bridges, skip duplicates
            existing_keys = {
                tuple(sorted([b.from_system, b.to_system]))
                for b in existing_network.bridges
            }
            for bridge in bridges:
                key = tuple(sorted([bridge.from_system, bridge.to_system]))
                if key not in existing_keys:
                    existing_network.bridges.append(bridge)
                    existing_keys.add(key)
    else:
        config.networks.append(JumpBridgeNetwork(
            name=network_name,
            bridges=bridges,
            enabled=True,
        ))

    # Save config
    save_bridge_config(config)

    return JumpBridgeImportResponse(
        network_name=network_name,
        bridges_imported=len(bridges),
        bridges_skipped=0,
        errors=errors,
    )


def get_active_bridges() -> List[JumpBridge]:
    """Get all bridges from enabled networks."""
    config = load_bridge_config()
    return config.get_active_bridges()


def toggle_network(network_name: str, enabled: bool) -> bool:
    """
    Enable or disable a jump bridge network.

    Args:
        network_name: Name of the network
        enabled: Whether to enable or disable

    Returns:
        True if network was found and updated
    """
    config = load_bridge_config()
    for network in config.networks:
        if network.name == network_name:
            network.enabled = enabled
            save_bridge_config(config)
            return True
    return False


def delete_network(network_name: str) -> bool:
    """
    Delete a jump bridge network.

    Args:
        network_name: Name of the network to delete

    Returns:
        True if network was found and deleted
    """
    config = load_bridge_config()
    for i, network in enumerate(config.networks):
        if network.name == network_name:
            config.networks.pop(i)
            save_bridge_config(config)
            return True
    return False
