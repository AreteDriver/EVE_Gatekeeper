"""Load EVE-SDE (Static Data Export) into database."""

import yaml
import requests
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from .database import DatabaseManager, Region, Constellation, System, Stargate


class SDELoader:
    """Load EVE-SDE data from CCP's repository."""

    # CCP's EVE-SDE repository (YAML format)
    SDE_BASE_URL = "https://raw.githubusercontent.com/EvE-KILL/eve-sd/master/out"
    SDE_VERSION = "latest"

    # Local cache to avoid repeated downloads
    CACHE_DIR = Path("data/sde_cache")

    def __init__(self, db_manager: DatabaseManager):
        """Initialize SDE loader.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.cache_dir = self.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_yaml(self, url: str, cache_key: str = None) -> Optional[Dict]:
        """Fetch and parse YAML from URL with caching.

        Args:
            url: URL to fetch
            cache_key: Optional cache key (uses URL hash if not provided)

        Returns:
            Parsed YAML dict or None
        """
        if not cache_key:
            cache_key = url.split('/')[-1].replace('.yaml', '')

        cache_path = self.cache_dir / f"{cache_key}.json"

        # Try cache first
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Fetch from URL
        try:
            print(f"  Fetching {url}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Parse YAML
            data = yaml.safe_load(response.text)

            # Cache result
            with open(cache_path, 'w') as f:
                json.dump(data, f)

            return data
        except requests.RequestException as e:
            print(f"  Error fetching {url}: {e}")
            return None

    def _fetch_sde_directory_file(self, filename: str, category: str = "fsd") -> Optional[Dict]:
        """Fetch SDE directory file (regions, constellations, systems).

        Args:
            filename: Filename (e.g., 'solarsystems.yaml')
            category: Category in SDE (default 'fsd')

        Returns:
            Parsed data
        """
        url = f"{self.SDE_BASE_URL}/{category}/{filename}.yaml"
        return self._fetch_yaml(url, cache_key=filename)

    def load_regions(self) -> int:
        """Load all regions into database.

        Returns:
            Number of regions loaded
        """
        print("Loading regions...")
        session = self.db.get_session()

        try:
            data = self._fetch_sde_directory_file('regions')
            if not data:
                print("  Failed to fetch regions")
                return 0

            count = 0
            for region_id, region_data in data.items():
                try:
                    region_id = int(region_id)

                    # Check if already exists
                    existing = session.query(Region).filter_by(region_id=region_id).first()
                    if existing:
                        continue

                    region = Region(
                        region_id=region_id,
                        name=region_data.get('name', f'Region {region_id}'),
                        description=region_data.get('description', '')
                    )
                    session.add(region)
                    count += 1

                    if count % 100 == 0:
                        print(f"  Loaded {count} regions...")

                except Exception as e:
                    print(f"  Error loading region {region_id}: {e}")

            session.commit()
            print(f"✓ Loaded {count} regions")
            return count

        except Exception as e:
            print(f"Error loading regions: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

    def load_constellations(self) -> int:
        """Load all constellations into database.

        Returns:
            Number of constellations loaded
        """
        print("Loading constellations...")
        session = self.db.get_session()

        try:
            data = self._fetch_sde_directory_file('constellations')
            if not data:
                print("  Failed to fetch constellations")
                return 0

            count = 0
            for const_id, const_data in data.items():
                try:
                    const_id = int(const_id)

                    # Check if already exists
                    existing = session.query(Constellation).filter_by(constellation_id=const_id).first()
                    if existing:
                        continue

                    region_id = const_data.get('regionID')
                    if not region_id:
                        continue

                    constellation = Constellation(
                        constellation_id=const_id,
                        name=const_data.get('name', f'Constellation {const_id}'),
                        region_id=region_id
                    )
                    session.add(constellation)
                    count += 1

                    if count % 100 == 0:
                        print(f"  Loaded {count} constellations...")

                except Exception as e:
                    print(f"  Error loading constellation {const_id}: {e}")

            session.commit()
            print(f"✓ Loaded {count} constellations")
            return count

        except Exception as e:
            print(f"Error loading constellations: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

    def load_systems(self) -> int:
        """Load all solar systems into database.

        Returns:
            Number of systems loaded
        """
        print("Loading solar systems...")
        session = self.db.get_session()

        try:
            data = self._fetch_sde_directory_file('solarsystems')
            if not data:
                print("  Failed to fetch solar systems")
                return 0

            count = 0
            for system_id, system_data in data.items():
                try:
                    system_id = int(system_id)

                    # Check if already exists
                    existing = session.query(System).filter_by(system_id=system_id).first()
                    if existing:
                        continue

                    constellation_id = system_data.get('constellationID')
                    region_id = system_data.get('regionID')

                    if not constellation_id or not region_id:
                        continue

                    # Extract position
                    position = system_data.get('position', {})

                    # Determine if wormhole
                    is_wormhole = system_data.get('isWormholeSystem', False)

                    system = System(
                        system_id=system_id,
                        name=system_data.get('name', f'System {system_id}'),
                        region_id=region_id,
                        constellation_id=constellation_id,
                        security_status=float(system_data.get('securityStatus', 0.0)),
                        is_wormhole=is_wormhole,
                        x=position.get('x'),
                        y=position.get('y'),
                        z=position.get('z'),
                        star_id=system_data.get('starID'),
                        sunTypeId=system_data.get('sunTypeID')
                    )
                    session.add(system)
                    count += 1

                    if count % 1000 == 0:
                        print(f"  Loaded {count} systems...")

                except Exception as e:
                    print(f"  Error loading system {system_id}: {e}")

            session.commit()
            print(f"✓ Loaded {count} systems")
            return count

        except Exception as e:
            print(f"Error loading systems: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

    def load_stargates(self) -> int:
        """Load jump gate connections.

        Returns:
            Number of stargates loaded
        """
        print("Loading stargates (jump gates)...")
        session = self.db.get_session()

        try:
            data = self._fetch_sde_directory_file('stargates')
            if not data:
                print("  Failed to fetch stargates")
                return 0

            count = 0
            for stargate_id, stargate_data in data.items():
                try:
                    stargate_id = int(stargate_id)

                    # Check if already exists
                    existing = session.query(Stargate).filter_by(stargate_id=stargate_id).first()
                    if existing:
                        continue

                    system_id = stargate_data.get('solarSystemID')
                    destination = stargate_data.get('destination', {})
                    destination_system_id = destination.get('solarSystemID')

                    if not system_id or not destination_system_id:
                        continue

                    # Verify both systems exist
                    source_sys = session.query(System).filter_by(system_id=system_id).first()
                    dest_sys = session.query(System).filter_by(system_id=destination_system_id).first()

                    if not source_sys or not dest_sys:
                        continue

                    stargate = Stargate(
                        stargate_id=stargate_id,
                        system_id=system_id,
                        destination_system_id=destination_system_id,
                        name=stargate_data.get('name', f'Stargate {stargate_id}'),
                        type_id=stargate_data.get('typeID')
                    )
                    session.add(stargate)
                    count += 1

                    if count % 1000 == 0:
                        print(f"  Loaded {count} stargates...")

                except Exception as e:
                    print(f"  Error loading stargate {stargate_id}: {e}")

            session.commit()
            print(f"✓ Loaded {count} stargates")
            return count

        except Exception as e:
            print(f"Error loading stargates: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

    def load_all(self) -> Dict[str, int]:
        """Load all SDE data into database.

        Returns:
            Dictionary with counts for each category
        """
        print("\n" + "=" * 60)
        print("LOADING EVE STATIC DATA EXPORT (SDE)")
        print("=" * 60 + "\n")

        results = {
            'regions': self.load_regions(),
            'constellations': self.load_constellations(),
            'systems': self.load_systems(),
            'stargates': self.load_stargates(),
        }

        print("\n" + "=" * 60)
        print("SDE LOAD COMPLETE")
        print("=" * 60)
        print(f"Regions: {results['regions']}")
        print(f"Constellations: {results['constellations']}")
        print(f"Systems: {results['systems']}")
        print(f"Stargates: {results['stargates']}")
        print()

        return results
