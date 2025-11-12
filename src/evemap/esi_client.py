"""EVE Online ESI (External Services Interface) API client."""

import requests
import json
from typing import Dict, List, Optional, Any
from .models import System, Region, Constellation, JumpConnection
import time


class ESIClient:
    """Client for fetching data from EVE Online's ESI API."""

    BASE_URL = "https://esi.eveonline.com/latest"
    USER_AGENT = "EveMapVisualization/0.1.0"

    def __init__(self, timeout: int = 10):
        """Initialize ESI client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def _make_request(self, endpoint: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make a request to the ESI API with retry logic.

        Args:
            endpoint: API endpoint (without base URL)
            retries: Number of retries on failure

        Returns:
            Response JSON or None if all retries failed
        """
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Request failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to fetch {url} after {retries} retries: {e}")
                    return None

    def get_region(self, region_id: int) -> Optional[Region]:
        """Fetch a region by ID.

        Args:
            region_id: EVE region ID

        Returns:
            Region object or None
        """
        data = self._make_request(f"/universe/regions/{region_id}/")
        if not data:
            return None

        return Region(
            region_id=region_id,
            name=data.get("name", "Unknown"),
            constellations=data.get("constellations", []),
            metadata={"description": data.get("description", "")}
        )

    def get_constellation(self, constellation_id: int) -> Optional[Constellation]:
        """Fetch a constellation by ID.

        Args:
            constellation_id: EVE constellation ID

        Returns:
            Constellation object or None
        """
        data = self._make_request(f"/universe/constellations/{constellation_id}/")
        if not data:
            return None

        return Constellation(
            constellation_id=constellation_id,
            name=data.get("name", "Unknown"),
            region_id=data.get("region_id"),
            systems=data.get("systems", [])
        )

    def get_system(self, system_id: int) -> Optional[System]:
        """Fetch a system by ID.

        Args:
            system_id: EVE system ID

        Returns:
            System object or None
        """
        data = self._make_request(f"/universe/systems/{system_id}/")
        if not data:
            return None

        # Extract position for potential 3D layout
        position = data.get("position", {})

        system = System(
            system_id=system_id,
            name=data.get("name", "Unknown"),
            region_id=data.get("region_id"),
            constellation_id=data.get("constellation_id"),
            security_status=data.get("security_status", 0.0),
            planets=len(data.get("planets", [])),
            stargates=len(data.get("stargates", [])),
            stars=len(data.get("stars", [])),
            metadata={
                "pos_x": position.get("x"),
                "pos_y": position.get("y"),
                "pos_z": position.get("z"),
                "star_id": data.get("star_id"),
            }
        )
        return system

    def get_systems_by_ids(self, system_ids: List[int]) -> List[System]:
        """Fetch multiple systems by IDs.

        Args:
            system_ids: List of EVE system IDs

        Returns:
            List of System objects
        """
        systems = []
        for system_id in system_ids:
            system = self.get_system(system_id)
            if system:
                systems.append(system)
            # Rate limiting - ESI allows ~150 requests/second but be respectful
            time.sleep(0.1)
        return systems

    def get_stargates(self, system_id: int) -> List[int]:
        """Get stargate IDs in a system.

        Args:
            system_id: EVE system ID

        Returns:
            List of stargate IDs
        """
        data = self._make_request(f"/universe/systems/{system_id}/")
        if not data:
            return []
        return data.get("stargates", [])

    def get_stargate(self, stargate_id: int) -> Optional[Dict[str, Any]]:
        """Get stargate information.

        Args:
            stargate_id: EVE stargate ID

        Returns:
            Stargate data or None
        """
        return self._make_request(f"/universe/stargates/{stargate_id}/")

    def get_jump_connections(self, system_ids: List[int]) -> List[JumpConnection]:
        """Build jump connections between systems.

        Args:
            system_ids: List of EVE system IDs

        Returns:
            List of JumpConnection objects
        """
        connections = []
        seen = set()

        for system_id in system_ids:
            stargates = self.get_stargates(system_id)

            for stargate_id in stargates:
                stargate_data = self.get_stargate(stargate_id)
                if not stargate_data:
                    continue

                destination = stargate_data.get("destination", {})
                dest_system_id = destination.get("system_id")

                if dest_system_id and dest_system_id in system_ids:
                    # Create undirected connection (avoid duplicates)
                    edge = tuple(sorted([system_id, dest_system_id]))
                    if edge not in seen:
                        seen.add(edge)
                        connections.append(
                            JumpConnection(
                                source_system_id=system_id,
                                target_system_id=dest_system_id
                            )
                        )

                # Rate limiting
                time.sleep(0.05)

        return connections

    def get_region_data(self, region_id: int) -> Optional[tuple]:
        """Fetch all data for a region (systems, constellations, connections).

        Args:
            region_id: EVE region ID

        Returns:
            Tuple of (systems_dict, constellations_dict, connections_list) or None
        """
        print(f"Fetching region {region_id}...")

        # Get region info
        region = self.get_region(region_id)
        if not region:
            return None

        print(f"Found region: {region.name}")

        # Get constellations
        constellations = {}
        constellation_ids = region.constellations
        system_ids = set()

        print(f"Fetching {len(constellation_ids)} constellations...")
        for const_id in constellation_ids:
            constellation = self.get_constellation(const_id)
            if constellation:
                constellations[const_id] = constellation
                system_ids.update(constellation.systems)
            time.sleep(0.05)

        # Get systems
        systems = {}
        print(f"Fetching {len(system_ids)} systems...")
        for system in self.get_systems_by_ids(list(system_ids)):
            systems[system.system_id] = system

        # Get jump connections
        print("Building jump connections...")
        connections = self.get_jump_connections(list(system_ids))

        return systems, constellations, connections
