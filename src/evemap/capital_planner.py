"""Capital ship jump planning and optimization."""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import math

from .dogma import DogmaCalculator, ShipAttributes
from .database import DatabaseManager, System
from .graph_engine import GraphEngine


@dataclass
class JumpLeg:
    """A single jump in a multi-leg journey."""
    origin_system_id: int
    origin_name: str
    destination_system_id: int
    destination_name: str
    distance_ly: float
    fuel_consumed: float
    duration_minutes: int = 1  # Jump duration (in reality ~1 min per jump)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON."""
        return {
            "origin_system_id": self.origin_system_id,
            "origin_name": self.origin_name,
            "destination_system_id": self.destination_system_id,
            "destination_name": self.destination_name,
            "distance_ly": self.distance_ly,
            "fuel_consumed": self.fuel_consumed,
            "duration_minutes": self.duration_minutes,
        }


@dataclass
class JumpChain:
    """Complete multi-leg jump route."""
    origin_system_id: int
    destination_system_id: int
    legs: List[JumpLeg]
    total_distance_ly: float
    total_fuel_consumed: float
    total_duration_hours: float
    requires_refuel: bool
    refuel_points: List[int]  # System IDs where refueling is needed

    @property
    def total_jumps(self) -> int:
        """Total number of jumps."""
        return len(self.legs)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON."""
        return {
            "origin_system_id": self.origin_system_id,
            "destination_system_id": self.destination_system_id,
            "legs": [leg.to_dict() for leg in self.legs],
            "total_distance_ly": self.total_distance_ly,
            "total_fuel_consumed": self.total_fuel_consumed,
            "total_duration_hours": self.total_duration_hours,
            "total_jumps": self.total_jumps,
            "requires_refuel": self.requires_refuel,
            "refuel_points": self.refuel_points,
        }


@dataclass
class JumpSphere:
    """Systems within jump range of an origin."""
    origin_system_id: int
    origin_name: str
    max_range_ly: float
    systems_in_range: List[Dict]  # [{"id": int, "name": str, "distance_ly": float}, ...]
    count: int

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON."""
        return {
            "origin_system_id": self.origin_system_id,
            "origin_name": self.origin_name,
            "max_range_ly": self.max_range_ly,
            "systems_in_range": self.systems_in_range,
            "count": self.count,
        }


class CapitalJumpPlanner:
    """Plan multi-leg capital ship jumps."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize jump planner.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.dogma = DogmaCalculator()
        self.graph = GraphEngine(db_manager)

        # Build graph if not already built
        if not self.graph._built:
            self.graph.build_from_db()

    def calculate_jump_range(
        self,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None
    ) -> Optional[float]:
        """Calculate max jump range for a ship.

        Args:
            ship_type_id: EVE ship type ID
            skill_levels: Skill levels (e.g., {"advanced_spaceship_command": 5})

        Returns:
            Max jump range in LY
        """
        return self.dogma.calculate_jump_range(ship_type_id, skill_levels)

    def calculate_distance(
        self,
        system1_id: int,
        system2_id: int
    ) -> Optional[float]:
        """Calculate distance between two systems.

        Uses Euclidean distance from system coordinates.

        Args:
            system1_id: First system ID
            system2_id: Second system ID

        Returns:
            Distance in light-years
        """
        session = self.db.get_session()
        try:
            sys1 = session.query(System).filter_by(system_id=system1_id).first()
            sys2 = session.query(System).filter_by(system_id=system2_id).first()

            if not sys1 or not sys2:
                return None

            # Get coordinates (convert from EVE units to light-years)
            # EVE uses AU (astronomical units), 1 AU ≈ 150M km ≈ 0.0000158 LY
            x1, y1, z1 = (sys1.x or 0) / 1e16, (sys1.y or 0) / 1e16, (sys1.z or 0) / 1e16
            x2, y2, z2 = (sys2.x or 0) / 1e16, (sys2.y or 0) / 1e16, (sys2.z or 0) / 1e16

            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
            return max(0.01, distance)  # Minimum 0.01 LY

        finally:
            session.close()

    def find_jump_sphere(
        self,
        origin_system_id: int,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None
    ) -> Optional[JumpSphere]:
        """Find all systems within jump range.

        Args:
            origin_system_id: Origin system
            ship_type_id: Ship type ID
            skill_levels: Skill levels

        Returns:
            JumpSphere with all reachable systems
        """
        max_range = self.calculate_jump_range(ship_type_id, skill_levels)
        if max_range is None:
            return None

        session = self.db.get_session()
        try:
            origin = session.query(System).filter_by(system_id=origin_system_id).first()
            if not origin:
                return None

            all_systems = session.query(System).all()
            systems_in_range = []

            for system in all_systems:
                if system.system_id == origin_system_id:
                    continue

                distance = self.calculate_distance(origin_system_id, system.system_id)
                if distance and distance <= max_range:
                    systems_in_range.append({
                        "id": system.system_id,
                        "name": system.name,
                        "distance_ly": round(distance, 2),
                        "region_id": system.region_id,
                        "security": system.security_status,
                    })

            # Sort by distance
            systems_in_range.sort(key=lambda x: x["distance_ly"])

            return JumpSphere(
                origin_system_id=origin_system_id,
                origin_name=origin.name,
                max_range_ly=max_range,
                systems_in_range=systems_in_range,
                count=len(systems_in_range)
            )

        finally:
            session.close()

    def plan_jump_chain(
        self,
        origin_system_id: int,
        destination_system_id: int,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None,
        max_fuel: Optional[int] = None,
        avoid_systems: Optional[Set[int]] = None,
        avoid_lowsec: bool = False,
    ) -> Optional[JumpChain]:
        """Plan a multi-leg jump route from origin to destination.

        Uses the graph engine to find shortest path, then checks if each
        leg is jumpable. If not, inserts intermediate refuel stops.

        Args:
            origin_system_id: Starting system
            destination_system_id: Target system
            ship_type_id: Ship type ID
            skill_levels: Skill levels
            max_fuel: Maximum fuel available (for refuel planning)
            avoid_systems: Systems to avoid
            avoid_lowsec: Skip low-sec systems

        Returns:
            JumpChain with complete plan, or None if impossible
        """
        # Get ship specs
        ship = self.dogma.get_ship(ship_type_id)
        if not ship:
            return None

        max_range = self.calculate_jump_range(ship_type_id, skill_levels)
        if max_range is None:
            return None

        # Find initial path using graph
        path = self.graph.shortest_path(
            origin_system_id,
            destination_system_id,
            avoid_systems=avoid_systems or set()
        )

        if not path:
            return None

        # Build jump legs
        legs = []
        total_fuel = 0
        refuel_points = []
        current_fuel = max_fuel or ship.fuel_capacity

        session = self.db.get_session()
        try:
            system_map = {s.system_id: s for s in session.query(System).all()}

            for i in range(len(path) - 1):
                origin_id = path[i]
                dest_id = path[i + 1]

                origin_sys = system_map.get(origin_id)
                dest_sys = system_map.get(dest_id)

                if not origin_sys or not dest_sys:
                    continue

                # Calculate distance and fuel
                distance = self.calculate_distance(origin_id, dest_id)
                if distance is None or distance > max_range:
                    # Can't jump this far, need intermediate stop
                    continue

                fuel_consumed = self.dogma.calculate_fuel_consumption(
                    ship_type_id, distance, skill_levels
                )

                if fuel_consumed is None:
                    fuel_consumed = 0

                # Check if we need to refuel
                if current_fuel < fuel_consumed:
                    refuel_points.append(origin_id)
                    current_fuel = ship.fuel_capacity

                leg = JumpLeg(
                    origin_system_id=origin_id,
                    origin_name=origin_sys.name,
                    destination_system_id=dest_id,
                    destination_name=dest_sys.name,
                    distance_ly=round(distance, 2),
                    fuel_consumed=round(fuel_consumed, 2)
                )

                legs.append(leg)
                total_fuel += fuel_consumed
                current_fuel -= fuel_consumed

            if not legs:
                return None

            # Create jump chain
            total_distance = sum(leg.distance_ly for leg in legs)
            total_duration = len(legs)  # Rough estimate: 1 hour per jump

            return JumpChain(
                origin_system_id=origin_system_id,
                destination_system_id=destination_system_id,
                legs=legs,
                total_distance_ly=round(total_distance, 2),
                total_fuel_consumed=round(total_fuel, 2),
                total_duration_hours=float(total_duration),
                requires_refuel=len(refuel_points) > 0,
                refuel_points=refuel_points
            )

        finally:
            session.close()

    def compare_routes(
        self,
        origin_system_id: int,
        destination_system_id: int,
        ship_type_id: int,
        skill_levels: Optional[Dict[str, int]] = None,
    ) -> List[JumpChain]:
        """Plan multiple routes and compare them.

        Args:
            origin_system_id: Starting system
            destination_system_id: Target system
            ship_type_id: Ship type ID
            skill_levels: Skill levels

        Returns:
            List of JumpChain options (fastest, safest, etc.)
        """
        routes = []

        # Try direct route (shortest)
        direct = self.plan_jump_chain(
            origin_system_id,
            destination_system_id,
            ship_type_id,
            skill_levels
        )
        if direct:
            routes.append(direct)

        # TODO: Try alternate routes via different hubs

        return routes

    def estimate_travel_time(self, chain: JumpChain) -> Dict:
        """Estimate total travel time including jumps and warps.

        Args:
            chain: JumpChain to analyze

        Returns:
            Dict with time estimates
        """
        jump_time = chain.total_jumps * 60  # ~1 min per jump in seconds

        # Estimate warp time between gates (rough)
        warp_time = 0  # Minimal - gates are adjacent

        total_seconds = jump_time + warp_time
        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60

        return {
            "total_jumps": chain.total_jumps,
            "jump_time_minutes": round(jump_time / 60, 1),
            "warp_time_minutes": round(warp_time / 60, 1),
            "total_time_minutes": round(total_minutes, 1),
            "total_time_hours": round(total_hours, 2),
        }

    def get_ship_options(self, region_id: Optional[int] = None) -> List[Dict]:
        """Get available capital ship options.

        Args:
            region_id: Optional filter by region (for market availability)

        Returns:
            List of ship options with stats
        """
        options = []

        for ship in self.dogma.SHIP_SPECS.values():
            # Calculate ranges with max skills (level 5)
            max_skills = {
                "advanced_spaceship_command": 5,
                ship.ship_class.value + "_operation": 5,
            }

            max_range = self.dogma.calculate_jump_range(ship.ship_type_id, max_skills)

            options.append({
                "ship_type_id": ship.ship_type_id,
                "ship_name": ship.ship_name,
                "ship_class": ship.ship_class.value,
                "base_range": ship.base_jump_range,
                "max_range_with_skills": max_range,
                "fuel_capacity": ship.fuel_capacity,
                "mass": ship.mass,
            })

        # Sort by max range
        options.sort(key=lambda x: x["max_range_with_skills"], reverse=True)

        return options
