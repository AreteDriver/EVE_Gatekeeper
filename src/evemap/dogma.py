"""EVE Online dogma system - ship attributes and calculations."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ShipClass(Enum):
    """EVE ship classifications."""
    CAPITAL = "capital"
    DREADS = "dreads"
    CARRIERS = "carriers"
    SUPERCARRIERS = "supercarriers"
    TITANS = "titans"


@dataclass
class ShipAttributes:
    """Ship attribute data for dogma calculations."""
    ship_type_id: int
    ship_name: str
    ship_class: ShipClass
    base_jump_range: float  # Light years
    mass: float  # Kilograms
    fuel_capacity: int  # Units
    jump_drive_fuel_consumption: float  # Fuel per LY


class DogmaCalculator:
    """Calculate EVE dogma attributes for ships."""

    # Ship base specifications (from EVE database)
    SHIP_SPECS = {
        # Titans (largest)
        587: ShipAttributes(
            ship_type_id=587, ship_name="Erebus", ship_class=ShipClass.TITANS,
            base_jump_range=7.0, mass=1000000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=100.0
        ),
        593: ShipAttributes(
            ship_type_id=593, ship_name="Leviathan", ship_class=ShipClass.TITANS,
            base_jump_range=7.0, mass=1200000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=100.0
        ),
        23773: ShipAttributes(
            ship_type_id=23773, ship_name="Avatar", ship_class=ShipClass.TITANS,
            base_jump_range=7.0, mass=1150000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=100.0
        ),
        # Supercarriers
        3764: ShipAttributes(
            ship_type_id=3764, ship_name="Wyvern", ship_class=ShipClass.SUPERCARRIERS,
            base_jump_range=7.0, mass=900000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=175.0
        ),
        3766: ShipAttributes(
            ship_type_id=3766, ship_name="Nyx", ship_class=ShipClass.SUPERCARRIERS,
            base_jump_range=7.0, mass=900000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=175.0
        ),
        3762: ShipAttributes(
            ship_type_id=3762, ship_name="Aeon", ship_class=ShipClass.SUPERCARRIERS,
            base_jump_range=7.0, mass=900000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=175.0
        ),
        23913: ShipAttributes(
            ship_type_id=23913, ship_name="Vendetta", ship_class=ShipClass.SUPERCARRIERS,
            base_jump_range=7.0, mass=900000000, fuel_capacity=25000,
            jump_drive_fuel_consumption=175.0
        ),
        # Carriers
        647: ShipAttributes(
            ship_type_id=647, ship_name="Archon", ship_class=ShipClass.CARRIERS,
            base_jump_range=6.0, mass=600000000, fuel_capacity=20000,
            jump_drive_fuel_consumption=200.0
        ),
        649: ShipAttributes(
            ship_type_id=649, ship_name="Thanatos", ship_class=ShipClass.CARRIERS,
            base_jump_range=6.0, mass=600000000, fuel_capacity=20000,
            jump_drive_fuel_consumption=200.0
        ),
        651: ShipAttributes(
            ship_type_id=651, ship_name="Chimera", ship_class=ShipClass.CARRIERS,
            base_jump_range=6.0, mass=600000000, fuel_capacity=20000,
            jump_drive_fuel_consumption=200.0
        ),
        24483: ShipAttributes(
            ship_type_id=24483, ship_name="Hel", ship_class=ShipClass.CARRIERS,
            base_jump_range=6.0, mass=600000000, fuel_capacity=20000,
            jump_drive_fuel_consumption=200.0
        ),
        # Dreadnoughts
        485: ShipAttributes(
            ship_type_id=485, ship_name="Moros", ship_class=ShipClass.DREADS,
            base_jump_range=6.0, mass=500000000, fuel_capacity=15000,
            jump_drive_fuel_consumption=250.0
        ),
        488: ShipAttributes(
            ship_type_id=488, ship_name="Naglfar", ship_class=ShipClass.DREADS,
            base_jump_range=6.0, mass=500000000, fuel_capacity=15000,
            jump_drive_fuel_consumption=250.0
        ),
        489: ShipAttributes(
            ship_type_id=489, ship_name="Phoenix", ship_class=ShipClass.DREADS,
            base_jump_range=6.0, mass=500000000, fuel_capacity=15000,
            jump_drive_fuel_consumption=250.0
        ),
        23917: ShipAttributes(
            ship_type_id=23917, ship_name="Revelation", ship_class=ShipClass.DREADS,
            base_jump_range=6.0, mass=500000000, fuel_capacity=15000,
            jump_drive_fuel_consumption=250.0
        ),
    }

    # Skill modifiers (EVE skills that affect jump range)
    # Format: (skill_id, skill_name, multiplier_per_level)
    JUMP_DRIVE_SKILLS = {
        # Jump Drive Operation: +20% range per level
        "jump_drive_operation": {
            "skill_id": 3353,
            "skill_name": "Jump Drive Operation",
            "description": "10% reduction in jump fatigue per level",
            "range_bonus": 0.0,  # Doesn't increase range, reduces fatigue
            "fatigue_reduction": 0.1,
        },
        # Advanced Spaceship Command: +5% capital ship attributes per level
        "advanced_spaceship_command": {
            "skill_id": 20530,
            "skill_name": "Advanced Spaceship Command",
            "description": "5% bonus to capital ship attributes per level",
            "range_bonus": 0.05,  # +5% to jump range per level
            "multiplier": True,
        },
        # Dreadnought/Carrier/Titan skills: +2% attributes per level
        "dreadnought_operation": {
            "skill_id": 20533,
            "skill_name": "Dreadnought Operation",
            "description": "2% bonus to Dreadnought attributes per level",
            "range_bonus": 0.02,
            "multiplier": True,
        },
        "carrier_command": {
            "skill_id": 24241,
            "skill_name": "Carrier Command",
            "description": "2% bonus to Carrier attributes per level",
            "range_bonus": 0.02,
            "multiplier": True,
        },
        "titan_command": {
            "skill_id": 20532,
            "skill_name": "Titan Command",
            "description": "1% bonus to Titan attributes per level",
            "range_bonus": 0.01,
            "multiplier": True,
        },
    }

    def __init__(self):
        """Initialize dogma calculator."""
        pass

    def get_ship(self, ship_type_id: int) -> Optional[ShipAttributes]:
        """Get ship attributes by type ID.

        Args:
            ship_type_id: EVE ship type ID

        Returns:
            ShipAttributes or None
        """
        return self.SHIP_SPECS.get(ship_type_id)

    def get_ships_by_class(self, ship_class: ShipClass) -> List[ShipAttributes]:
        """Get all ships of a specific class.

        Args:
            ship_class: ShipClass enum value

        Returns:
            List of ShipAttributes
        """
        return [
            ship for ship in self.SHIP_SPECS.values()
            if ship.ship_class == ship_class
        ]

    def calculate_jump_range(
        self,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None
    ) -> Optional[float]:
        """Calculate maximum jump range for a ship.

        Args:
            ship_type_id: EVE ship type ID
            skill_levels: Dict mapping skill names to level (0-5, default 0)
                Example: {"advanced_spaceship_command": 5, "dreadnought_operation": 4}

        Returns:
            Maximum jump range in light-years, or None if ship not found
        """
        ship = self.get_ship(ship_type_id)
        if not ship:
            return None

        skill_levels = skill_levels or {}
        range_ly = ship.base_jump_range

        # Apply skill bonuses
        for skill_name, level in skill_levels.items():
            if skill_name in self.JUMP_DRIVE_SKILLS:
                skill = self.JUMP_DRIVE_SKILLS[skill_name]
                bonus = skill.get("range_bonus", 0)

                if skill.get("multiplier", False):
                    # Multiplicative bonus (e.g., +5% per level)
                    range_ly *= (1 + bonus * level)
                else:
                    # Additive bonus
                    range_ly += bonus * level

        return round(range_ly, 2)

    def calculate_fuel_consumption(
        self,
        ship_type_id: int,
        distance_ly: float,
        skill_levels: Optional[Dict[str, int]] = None
    ) -> Optional[float]:
        """Calculate fuel consumed for a jump.

        Args:
            ship_type_id: EVE ship type ID
            distance_ly: Jump distance in light-years
            skill_levels: Skill levels (for potential fuel efficiency)

        Returns:
            Fuel units consumed, or None if ship not found
        """
        ship = self.get_ship(ship_type_id)
        if not ship:
            return None

        # Fuel = base_consumption * distance
        # Each LY beyond base range requires exponentially more fuel
        fuel_consumed = ship.jump_drive_fuel_consumption * distance_ly

        # Jumping at longer ranges burns exponentially more fuel
        # For ranges > base, multiply by (range/base)^2
        if distance_ly > ship.base_jump_range:
            range_ratio = distance_ly / ship.base_jump_range
            fuel_consumed *= range_ratio ** 2

        return round(fuel_consumed, 2)

    def is_ship_capable(
        self,
        ship_type_id: int,
        distance_ly: float,
        skill_levels: Optional[Dict[str, int]] = None
    ) -> bool:
        """Check if ship can make a jump.

        Args:
            ship_type_id: EVE ship type ID
            distance_ly: Jump distance
            skill_levels: Skill levels

        Returns:
            True if ship can make the jump
        """
        max_range = self.calculate_jump_range(ship_type_id, skill_levels)
        if max_range is None:
            return False

        return distance_ly <= max_range

    def find_nearest_system_in_range(
        self,
        origin_system_id: int,
        target_system_id: int,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None,
        max_range_ly: Optional[float] = None,
    ) -> bool:
        """Check if target system is within jump range.

        Args:
            origin_system_id: Starting system
            target_system_id: Destination system
            ship_type_id: Ship type ID
            skill_levels: Skill levels
            max_range_ly: Override max range (for testing)

        Returns:
            True if target is in range
        """
        # This is a placeholder - would need system coordinates
        # In real implementation, would calculate distance from coordinates
        return True

    def plan_refuel_stops(
        self,
        origin_system_id: int,
        destination_system_id: int,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None,
        available_systems: Optional[List[int]] = None,
    ) -> Optional[List[int]]:
        """Plan intermediate jumps to destination (refuel stops).

        Args:
            origin_system_id: Starting system
            destination_system_id: Target system
            ship_type_id: Ship type ID
            skill_levels: Skill levels
            available_systems: Systems where refuel is possible (default: all)

        Returns:
            List of system IDs including intermediate stops, or None if impossible
        """
        # Placeholder for advanced routing
        # Real implementation would use the graph engine + coordinates
        return None


@dataclass
class ShipConfig:
    """User's saved ship configuration."""
    config_id: str
    ship_name: str  # User's nickname (e.g., "Jump Freighter #1")
    ship_type_id: int
    skills: Dict[str, int]  # Skill level mapping
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage."""
        return {
            "config_id": self.config_id,
            "ship_name": self.ship_name,
            "ship_type_id": self.ship_type_id,
            "skills": self.skills,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: Dict) -> "ShipConfig":
        """Create from dictionary."""
        return ShipConfig(**data)


class ShipConfigManager:
    """Manage user's saved ship configurations (local storage on iOS)."""

    def __init__(self):
        """Initialize config manager."""
        self.configs: Dict[str, ShipConfig] = {}

    def save_config(self, config: ShipConfig):
        """Save a ship configuration.

        Args:
            config: ShipConfig to save
        """
        self.configs[config.config_id] = config

    def get_config(self, config_id: str) -> Optional[ShipConfig]:
        """Retrieve a saved configuration.

        Args:
            config_id: Configuration ID

        Returns:
            ShipConfig or None
        """
        return self.configs.get(config_id)

    def list_configs(self) -> List[ShipConfig]:
        """List all saved configurations.

        Returns:
            List of ShipConfig objects
        """
        return list(self.configs.values())

    def delete_config(self, config_id: str) -> bool:
        """Delete a configuration.

        Args:
            config_id: Configuration ID

        Returns:
            True if deleted, False if not found
        """
        if config_id in self.configs:
            del self.configs[config_id]
            return True
        return False

    def export_configs(self) -> List[Dict]:
        """Export all configs as JSON-serializable list.

        Returns:
            List of config dicts
        """
        return [config.to_dict() for config in self.configs.values()]

    def import_configs(self, configs_data: List[Dict]):
        """Import configs from JSON data.

        Args:
            configs_data: List of config dictionaries
        """
        for data in configs_data:
            config = ShipConfig.from_dict(data)
            self.save_config(config)
