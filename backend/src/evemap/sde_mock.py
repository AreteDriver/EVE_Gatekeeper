"""Mock EVE-SDE data for testing without internet access."""

from .database import DatabaseManager, Region, Constellation, System, Stargate
from sqlalchemy.orm import Session


class MockSDELoader:
    """Load mock EVE universe data for testing."""

    # Mock Forge region (high-sec trading hub area)
    MOCK_DATA = {
        'regions': {
            10000002: {'name': 'The Forge', 'description': 'Trade hub region'},
            10000043: {'name': 'Domain', 'description': 'High-sec region'},
        },
        'constellations': {
            20000020: {'name': 'Kimotoro', 'regionID': 10000002},
            20000021: {'name': 'Charra', 'regionID': 10000002},
            20000022: {'name': 'Yuhelia', 'regionID': 10000043},
        },
        'systems': {
            30000142: {
                'name': 'Jita', 'regionID': 10000002, 'constellationID': 20000020,
                'securityStatus': 5.0, 'position': {'x': 1e10, 'y': 2e10, 'z': 3e10}
            },
            30001161: {
                'name': 'Perimeter', 'regionID': 10000002, 'constellationID': 20000020,
                'securityStatus': 5.0, 'position': {'x': 1.1e10, 'y': 2.1e10, 'z': 3.1e10}
            },
            30002768: {
                'name': 'Sobaseki', 'regionID': 10000002, 'constellationID': 20000020,
                'securityStatus': 4.8, 'position': {'x': 1.2e10, 'y': 2.2e10, 'z': 3.2e10}
            },
            30002060: {
                'name': 'Urlen', 'regionID': 10000002, 'constellationID': 20000021,
                'securityStatus': 4.5, 'position': {'x': 1.3e10, 'y': 2.3e10, 'z': 3.3e10}
            },
            30000144: {
                'name': 'Isanamo', 'regionID': 10000043, 'constellationID': 20000022,
                'securityStatus': 3.8, 'position': {'x': 1.4e10, 'y': 2.4e10, 'z': 3.4e10}
            },
            30003068: {
                'name': 'Kisogo', 'regionID': 10000043, 'constellationID': 20000022,
                'securityStatus': 3.5, 'position': {'x': 1.5e10, 'y': 2.5e10, 'z': 3.5e10}
            },
        },
        'stargates': {
            50000001: {'solarSystemID': 30000142, 'destination': {'solarSystemID': 30001161}},
            50000002: {'solarSystemID': 30001161, 'destination': {'solarSystemID': 30000142}},
            50000003: {'solarSystemID': 30001161, 'destination': {'solarSystemID': 30002768}},
            50000004: {'solarSystemID': 30002768, 'destination': {'solarSystemID': 30001161}},
            50000005: {'solarSystemID': 30002768, 'destination': {'solarSystemID': 30002060}},
            50000006: {'solarSystemID': 30002060, 'destination': {'solarSystemID': 30002768}},
            50000007: {'solarSystemID': 30002060, 'destination': {'solarSystemID': 30000144}},
            50000008: {'solarSystemID': 30000144, 'destination': {'solarSystemID': 30002060}},
            50000009: {'solarSystemID': 30000144, 'destination': {'solarSystemID': 30003068}},
            50000010: {'solarSystemID': 30003068, 'destination': {'solarSystemID': 30000144}},
        }
    }

    def __init__(self, db_manager: DatabaseManager):
        """Initialize mock loader.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager

    def load_all(self) -> dict:
        """Load all mock data.

        Returns:
            Dictionary with counts
        """
        print("\n" + "=" * 60)
        print("LOADING MOCK EVE DATA (FOR TESTING)")
        print("=" * 60 + "\n")

        results = {
            'regions': self._load_regions(),
            'constellations': self._load_constellations(),
            'systems': self._load_systems(),
            'stargates': self._load_stargates(),
        }

        print("\n" + "=" * 60)
        print("MOCK DATA LOAD COMPLETE")
        print("=" * 60)
        print(f"Regions: {results['regions']}")
        print(f"Constellations: {results['constellations']}")
        print(f"Systems: {results['systems']}")
        print(f"Stargates: {results['stargates']}")
        print()

        return results

    def _load_regions(self) -> int:
        """Load mock regions."""
        print("Loading regions...")
        session = self.db.get_session()

        try:
            count = 0
            for region_id, data in self.MOCK_DATA['regions'].items():
                region = Region(
                    region_id=region_id,
                    name=data['name'],
                    description=data.get('description', '')
                )
                session.add(region)
                count += 1

            session.commit()
            print(f"✓ Loaded {count} regions")
            return count

        finally:
            session.close()

    def _load_constellations(self) -> int:
        """Load mock constellations."""
        print("Loading constellations...")
        session = self.db.get_session()

        try:
            count = 0
            for const_id, data in self.MOCK_DATA['constellations'].items():
                constellation = Constellation(
                    constellation_id=const_id,
                    name=data['name'],
                    region_id=data['regionID']
                )
                session.add(constellation)
                count += 1

            session.commit()
            print(f"✓ Loaded {count} constellations")
            return count

        finally:
            session.close()

    def _load_systems(self) -> int:
        """Load mock systems."""
        print("Loading systems...")
        session = self.db.get_session()

        try:
            count = 0
            for system_id, data in self.MOCK_DATA['systems'].items():
                position = data.get('position', {})

                system = System(
                    system_id=system_id,
                    name=data['name'],
                    region_id=data['regionID'],
                    constellation_id=data['constellationID'],
                    security_status=data['securityStatus'],
                    x=position.get('x'),
                    y=position.get('y'),
                    z=position.get('z'),
                )
                session.add(system)
                count += 1

            session.commit()
            print(f"✓ Loaded {count} systems")
            return count

        finally:
            session.close()

    def _load_stargates(self) -> int:
        """Load mock stargates."""
        print("Loading stargates...")
        session = self.db.get_session()

        try:
            count = 0
            for stargate_id, data in self.MOCK_DATA['stargates'].items():
                stargate = Stargate(
                    stargate_id=stargate_id,
                    system_id=data['solarSystemID'],
                    destination_system_id=data['destination']['solarSystemID'],
                )
                session.add(stargate)
                count += 1

            session.commit()
            print(f"✓ Loaded {count} stargates")
            return count

        finally:
            session.close()
