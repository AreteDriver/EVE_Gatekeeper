"""Capital ship data for jump planning.

Contains base jump range and fuel consumption data for capital ships.
Data sourced from EVE SDE dogma attributes.
"""

from dataclasses import dataclass
from enum import Enum


class FuelType(Enum):
    """Jump fuel isotope types."""

    HELIUM = 16274  # Helium Isotopes (Amarr)
    HYDROGEN = 17889  # Hydrogen Isotopes (Minmatar)
    NITROGEN = 17888  # Nitrogen Isotopes (Caldari)
    OXYGEN = 17887  # Oxygen Isotopes (Gallente)


@dataclass
class CapitalShipData:
    """Capital ship jump drive data."""

    type_id: int
    name: str
    base_range_ly: float  # Base jump range in LY
    base_fuel_need: float  # Isotopes per LY (base)
    fuel_type: FuelType
    is_jump_freighter: bool = False
    is_black_ops: bool = False


# Capital ship data (approximate values from SDE)
# Note: These are base values before skill bonuses
CAPITAL_SHIPS: dict[int, CapitalShipData] = {
    # Dreadnoughts
    19720: CapitalShipData(19720, "Revelation", 5.0, 1000, FuelType.HELIUM),
    19722: CapitalShipData(19722, "Moros", 5.0, 1000, FuelType.OXYGEN),
    19724: CapitalShipData(19724, "Naglfar", 5.0, 1000, FuelType.HYDROGEN),
    19726: CapitalShipData(19726, "Phoenix", 5.0, 1000, FuelType.NITROGEN),

    # Carriers
    23757: CapitalShipData(23757, "Archon", 5.0, 1000, FuelType.HELIUM),
    23911: CapitalShipData(23911, "Thanatos", 5.0, 1000, FuelType.OXYGEN),
    23915: CapitalShipData(23915, "Nidhoggur", 5.0, 1000, FuelType.HYDROGEN),
    23913: CapitalShipData(23913, "Chimera", 5.0, 1000, FuelType.NITROGEN),

    # Force Auxiliaries
    37604: CapitalShipData(37604, "Apostle", 5.0, 1000, FuelType.HELIUM),
    37606: CapitalShipData(37606, "Ninazu", 5.0, 1000, FuelType.OXYGEN),
    37608: CapitalShipData(37608, "Lif", 5.0, 1000, FuelType.HYDROGEN),
    37605: CapitalShipData(37605, "Minokawa", 5.0, 1000, FuelType.NITROGEN),

    # Supercarriers
    23917: CapitalShipData(23917, "Aeon", 5.0, 5000, FuelType.HELIUM),
    23919: CapitalShipData(23919, "Nyx", 5.0, 5000, FuelType.OXYGEN),
    22852: CapitalShipData(22852, "Hel", 5.0, 5000, FuelType.HYDROGEN),
    23913: CapitalShipData(23913, "Wyvern", 5.0, 5000, FuelType.NITROGEN),

    # Titans
    671: CapitalShipData(671, "Avatar", 5.0, 10000, FuelType.HELIUM),
    3764: CapitalShipData(3764, "Erebus", 5.0, 10000, FuelType.OXYGEN),
    11567: CapitalShipData(11567, "Ragnarok", 5.0, 10000, FuelType.HYDROGEN),
    23773: CapitalShipData(23773, "Leviathan", 5.0, 10000, FuelType.NITROGEN),

    # Jump Freighters
    28844: CapitalShipData(28844, "Ark", 5.0, 3000, FuelType.HELIUM, is_jump_freighter=True),
    28846: CapitalShipData(28846, "Anshar", 5.0, 3000, FuelType.OXYGEN, is_jump_freighter=True),
    28848: CapitalShipData(28848, "Nomad", 5.0, 3000, FuelType.HYDROGEN, is_jump_freighter=True),
    28850: CapitalShipData(28850, "Rhea", 5.0, 3000, FuelType.NITROGEN, is_jump_freighter=True),

    # Rorqual (Industrial Capital)
    28352: CapitalShipData(28352, "Rorqual", 5.0, 3000, FuelType.OXYGEN),

    # Black Ops Battleships
    22428: CapitalShipData(22428, "Sin", 3.5, 400, FuelType.OXYGEN, is_black_ops=True),
    22430: CapitalShipData(22430, "Widow", 3.5, 400, FuelType.NITROGEN, is_black_ops=True),
    22436: CapitalShipData(22436, "Panther", 3.5, 400, FuelType.HYDROGEN, is_black_ops=True),
    22440: CapitalShipData(22440, "Redeemer", 3.5, 400, FuelType.HELIUM, is_black_ops=True),
}


def get_ship_base_range(type_id: int) -> float | None:
    """Get base jump range for a ship type.

    Args:
        type_id: Ship type ID

    Returns:
        Base range in LY or None if not a capital
    """
    ship = CAPITAL_SHIPS.get(type_id)
    return ship.base_range_ly if ship else None


def get_ship_fuel_need(type_id: int) -> float | None:
    """Get base fuel consumption for a ship type.

    Args:
        type_id: Ship type ID

    Returns:
        Base isotopes per LY or None if not a capital
    """
    ship = CAPITAL_SHIPS.get(type_id)
    return ship.base_fuel_need if ship else None


def calculate_effective_range(
    base_range: float,
    jdc_level: int = 0,
) -> float:
    """Calculate effective jump range with skills.

    Jump Drive Calibration: +25% range per level

    Args:
        base_range: Base jump range in LY
        jdc_level: Jump Drive Calibration skill level (0-5)

    Returns:
        Effective range in LY
    """
    jdc_bonus = 1.0 + (jdc_level * 0.25)
    return base_range * jdc_bonus


def calculate_fuel_consumption(
    base_fuel: float,
    distance_ly: float,
    jfc_level: int = 0,
    jf_level: int = 0,
    is_jump_freighter: bool = False,
) -> int:
    """Calculate fuel consumption for a jump.

    Jump Fuel Conservation: -10% fuel per level
    Jump Freighter skill: -10% fuel per level (JFs only)

    Args:
        base_fuel: Base isotopes per LY
        distance_ly: Jump distance in LY
        jfc_level: Jump Fuel Conservation level (0-5)
        jf_level: Jump Freighter skill level (0-5)
        is_jump_freighter: Whether ship is a Jump Freighter

    Returns:
        Total isotopes required (rounded up)
    """
    jfc_modifier = 1.0 - (jfc_level * 0.10)
    jf_modifier = 1.0 - (jf_level * 0.10) if is_jump_freighter else 1.0

    fuel_per_ly = base_fuel * jfc_modifier * jf_modifier
    total_fuel = fuel_per_ly * distance_ly

    # Round up to nearest whole isotope
    return int(total_fuel + 0.99)
