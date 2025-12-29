"""Pydantic models for EVE Online universe data."""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class Region(BaseModel):
    """EVE Online region."""

    region_id: int
    name: str
    description: str | None = None
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    faction_id: int | None = None

    model_config = {"from_attributes": True}


class Constellation(BaseModel):
    """EVE Online constellation."""

    constellation_id: int
    region_id: int
    name: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    faction_id: int | None = None

    model_config = {"from_attributes": True}


class SolarSystem(BaseModel):
    """EVE Online solar system with all relevant data for mapping."""

    system_id: int
    constellation_id: int
    region_id: int
    name: str
    # 3D coordinates
    x: float
    y: float
    z: float
    # 2D map projection
    map_x: float | None = None
    map_y: float | None = None
    # Security
    security_status: float = 0.0
    security_class: str | None = None
    # Star data
    star_id: int | None = None
    star_type_id: int | None = None
    # Sovereignty
    sovereignty_faction_id: int | None = None
    sovereignty_corp_id: int | None = None
    sovereignty_alliance_id: int | None = None
    # Flags
    is_wormhole: bool = False
    is_abyssal: bool = False
    is_pochven: bool = False

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def display_security(self) -> str:
        """Human-readable security status."""
        return f"{self.security_status:.1f}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sec_class(self) -> str:
        """Computed security class if not set."""
        if self.security_class:
            return self.security_class
        if self.is_wormhole:
            return "wormhole"
        if self.security_status >= 0.5:
            return "highsec"
        if self.security_status > 0.0:
            return "lowsec"
        return "nullsec"


class Stargate(BaseModel):
    """Stargate connection between systems."""

    stargate_id: int
    system_id: int
    destination_stargate_id: int
    destination_system_id: int
    name: str | None = None
    type_id: int | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None

    model_config = {"from_attributes": True}


class SystemConnection(BaseModel):
    """Graph edge between two systems."""

    from_system_id: int
    to_system_id: int
    base_weight: float = 1.0
    security_weight: float = 0.0
    connection_type: str = "stargate"

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_weight(self) -> float:
        """Total edge weight for pathfinding."""
        return self.base_weight + self.security_weight


class SystemStats(BaseModel):
    """Live activity statistics for a system."""

    system_id: int
    ship_kills: int = 0
    npc_kills: int = 0
    pod_kills: int = 0
    ship_jumps: int = 0
    kills_updated_at: datetime | None = None
    jumps_updated_at: datetime | None = None
    activity_index: float = 0.0

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_kills(self) -> int:
        """Total PvP kills (ships + pods)."""
        return self.ship_kills + self.pod_kills

    @computed_field  # type: ignore[prop-decorator]
    @property
    def danger_level(self) -> str:
        """Categorical danger level based on kills."""
        if self.ship_kills >= 50:
            return "extreme"
        if self.ship_kills >= 20:
            return "high"
        if self.ship_kills >= 5:
            return "moderate"
        if self.ship_kills >= 1:
            return "low"
        return "safe"


class Incursion(BaseModel):
    """Sansha incursion event."""

    incursion_id: int | None = None
    constellation_id: int
    staging_system_id: int | None = None
    state: str  # 'withdrawing', 'mobilizing', 'established'
    influence: float = 0.0
    has_boss: bool = False
    faction_id: int | None = None
    fetched_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class Sovereignty(BaseModel):
    """System sovereignty data."""

    system_id: int
    alliance_id: int | None = None
    corporation_id: int | None = None
    faction_id: int | None = None
    vulnerability_occupancy_level: float | None = None
    fetched_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


class SovereigntyCampaign(BaseModel):
    """Active sovereignty campaign/contest."""

    campaign_id: int
    system_id: int
    constellation_id: int
    event_type: str
    structure_id: int | None = None
    start_time: datetime | None = None
    defender_id: int | None = None
    defender_score: float = 0.0
    attackers_score: float = 0.0
    fetched_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}


# ============================================================================
# User Data Models
# ============================================================================


class ShipConfig(BaseModel):
    """Capital ship jump configuration."""

    config_id: int | None = None
    name: str
    ship_type_id: int
    # Jump drive base attributes
    jump_drive_fuel_need: float | None = None  # Isotopes per LY
    jump_drive_range: float | None = None  # Max LY base
    jump_drive_consumption_modifier: float = 1.0
    # Skill levels
    fuel_conservation_level: int = 0  # JFC 0-5
    jump_drive_calibration_level: int = 0  # JDC 0-5
    jump_freighter_level: int = 0  # Jump Freighter 0-5
    # Computed
    effective_range: float | None = None

    model_config = {"from_attributes": True}

    @computed_field  # type: ignore[prop-decorator]
    @property
    def computed_range(self) -> float:
        """Compute effective jump range with skills.

        JDC gives +25% range per level (up to +125% at V).
        """
        if self.jump_drive_range is None:
            return 0.0
        jdc_bonus = 1.0 + (self.jump_drive_calibration_level * 0.25)
        return self.jump_drive_range * jdc_bonus

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fuel_per_ly(self) -> float:
        """Compute fuel consumption per LY with skills.

        JFC gives -10% fuel per level.
        Jump Freighter gives -10% fuel per level (for JFs only).
        """
        if self.jump_drive_fuel_need is None:
            return 0.0
        jfc_modifier = 1.0 - (self.fuel_conservation_level * 0.10)
        jf_modifier = 1.0 - (self.jump_freighter_level * 0.10)
        return self.jump_drive_fuel_need * jfc_modifier * jf_modifier


class PilotProfile(BaseModel):
    """Pilot skill and preference profile."""

    profile_id: int | None = None
    character_id: int | None = None
    character_name: str | None = None
    # Jump skills
    jump_drive_calibration: int = 0
    jump_fuel_conservation: int = 0
    jump_freighter: int = 0
    # Navigation
    navigation: int = 0
    warp_drive_operation: int = 0
    # Avoid lists
    avoid_faction_ids: list[int] = Field(default_factory=list)
    avoid_corporation_ids: list[int] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SavedRoute(BaseModel):
    """Saved navigation route."""

    route_id: int | None = None
    name: str | None = None
    origin_system_id: int
    destination_system_id: int
    route_type: str = "shortest"  # 'shortest', 'secure', 'insecure'
    avoid_systems: list[int] = Field(default_factory=list)
    avoid_regions: list[int] = Field(default_factory=list)
    waypoints: list[int] = Field(default_factory=list)
    total_jumps: int | None = None

    model_config = {"from_attributes": True}


class CynoChainMidpoint(BaseModel):
    """A midpoint in a cyno chain."""

    system_id: int
    is_cyno_beacon: bool = False
    fuel_required: int | None = None


class CynoChain(BaseModel):
    """Capital ship cyno chain route."""

    chain_id: int | None = None
    name: str | None = None
    ship_config_id: int | None = None
    pilot_profile_id: int | None = None
    origin_system_id: int
    destination_system_id: int
    midpoints: list[CynoChainMidpoint] = Field(default_factory=list)
    total_fuel: int | None = None
    total_legs: int | None = None

    model_config = {"from_attributes": True}


# ============================================================================
# API Response Models
# ============================================================================


class SystemSearchResult(BaseModel):
    """Search result for system lookup."""

    system_id: int
    name: str
    region_name: str
    security_status: float
    security_class: str


class RouteResult(BaseModel):
    """Computed route between systems."""

    origin: SolarSystem
    destination: SolarSystem
    waypoints: list[SolarSystem]
    total_jumps: int
    route_type: str
    security_summary: dict[str, int]  # {'highsec': 5, 'lowsec': 2, ...}


class JumpRangeSphere(BaseModel):
    """Systems within jump range of a location."""

    origin_system: SolarSystem
    max_range_ly: float
    systems_in_range: list[tuple[SolarSystem, float]]  # (system, distance_ly)


class HeatmapData(BaseModel):
    """Heatmap overlay data."""

    data_type: str  # 'kills', 'jumps', 'activity'
    min_value: float
    max_value: float
    systems: list[tuple[int, float]]  # (system_id, normalized_value)
    updated_at: datetime
