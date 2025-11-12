"""Data models for EVE Online map entities."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class SecurityStatus(Enum):
    """EVE security status classifications."""
    HIGH_SEC = "high_sec"  # >= 0.45
    LOW_SEC = "low_sec"    # 0.1 to 0.44
    NULL_SEC = "null_sec"  # 0.0 to 0.09
    WORMHOLE = "wormhole"  # -1.0 (W-space)


@dataclass
class JumpConnection:
    """Represents a jump gate connection between systems."""
    source_system_id: int
    target_system_id: int
    distance: float = 1.0  # Light-years (for visualization)

    def __hash__(self):
        """Make hashable for graph operations."""
        return hash((self.source_system_id, self.target_system_id))

    def __eq__(self, other):
        """Check equality."""
        if not isinstance(other, JumpConnection):
            return False
        return (self.source_system_id == other.source_system_id and
                self.target_system_id == other.target_system_id)


@dataclass
class System:
    """Represents a solar system in New Eden."""
    system_id: int
    name: str
    region_id: int
    constellation_id: int
    security_status: float
    x: Optional[float] = None  # Position for 2D layout
    y: Optional[float] = None  # Position for 2D layout
    planets: int = 0
    stars: int = 0
    stargates: int = 0
    asteroids: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def security_class(self) -> SecurityStatus:
        """Classify system by security status."""
        if self.security_status >= 0.45:
            return SecurityStatus.HIGH_SEC
        elif self.security_status >= 0.1:
            return SecurityStatus.LOW_SEC
        else:
            return SecurityStatus.NULL_SEC

    def __hash__(self):
        """Make hashable for graph operations."""
        return hash(self.system_id)

    def __eq__(self, other):
        """Check equality by ID."""
        if not isinstance(other, System):
            return False
        return self.system_id == other.system_id

    def __lt__(self, other):
        """Enable sorting by name."""
        if not isinstance(other, System):
            return NotImplemented
        return self.name < other.name


@dataclass
class Constellation:
    """Represents a constellation containing systems."""
    constellation_id: int
    name: str
    region_id: int
    systems: List[int] = field(default_factory=list)  # System IDs
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.constellation_id)

    def __eq__(self, other):
        if not isinstance(other, Constellation):
            return False
        return self.constellation_id == other.constellation_id


@dataclass
class Region:
    """Represents a region containing constellations and systems."""
    region_id: int
    name: str
    constellations: List[int] = field(default_factory=list)  # Constellation IDs
    systems: List[int] = field(default_factory=list)  # System IDs
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.region_id)

    def __eq__(self, other):
        if not isinstance(other, Region):
            return False
        return self.region_id == other.region_id
