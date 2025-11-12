"""Data repository layer - efficient queries for mobile consumption."""

from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from .database import DatabaseManager, Region, Constellation, System, Stargate


class SystemRepository:
    """Queries for system data."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_by_id(self, system_id: int) -> Optional[Dict]:
        """Get system by ID.

        Args:
            system_id: System ID

        Returns:
            Compact system dict or None
        """
        session = self.db.get_session()
        try:
            system = session.query(System).filter_by(system_id=system_id).first()
            return self._system_to_dict(system) if system else None
        finally:
            session.close()

    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get system by name (case-insensitive).

        Args:
            name: System name

        Returns:
            Compact system dict or None
        """
        session = self.db.get_session()
        try:
            system = session.query(System).filter(
                System.name.ilike(name)
            ).first()
            return self._system_to_dict(system) if system else None
        finally:
            session.close()

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search systems by name.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of compact system dicts
        """
        session = self.db.get_session()
        try:
            results = session.query(System).filter(
                System.name.ilike(f"%{query}%")
            ).limit(limit).all()

            return [self._system_to_dict(sys) for sys in results]
        finally:
            session.close()

    def get_by_region(self, region_id: int) -> List[Dict]:
        """Get all systems in a region.

        Args:
            region_id: Region ID

        Returns:
            List of compact system dicts
        """
        session = self.db.get_session()
        try:
            systems = session.query(System).filter_by(region_id=region_id).all()
            return [self._system_to_dict(sys) for sys in systems]
        finally:
            session.close()

    def get_by_security(self, security_class: str) -> List[Dict]:
        """Get systems by security class.

        Args:
            security_class: "high_sec", "low_sec", "null_sec", or "wormhole"

        Returns:
            List of compact system dicts
        """
        session = self.db.get_session()
        try:
            if security_class == "high_sec":
                systems = session.query(System).filter(System.security_status >= 0.45).all()
            elif security_class == "low_sec":
                systems = session.query(System).filter(
                    and_(System.security_status >= 0.1, System.security_status < 0.45)
                ).all()
            elif security_class == "null_sec":
                systems = session.query(System).filter(System.security_status < 0.1).all()
            elif security_class == "wormhole":
                systems = session.query(System).filter_by(is_wormhole=True).all()
            else:
                return []

            return [self._system_to_dict(sys) for sys in systems]
        finally:
            session.close()

    def get_neighbors(self, system_id: int) -> List[Dict]:
        """Get adjacent systems (1 jump away).

        Args:
            system_id: System ID

        Returns:
            List of compact system dicts
        """
        session = self.db.get_session()
        try:
            stargates = session.query(Stargate).filter_by(system_id=system_id).all()
            neighbor_ids = [sg.destination_system_id for sg in stargates]

            if not neighbor_ids:
                return []

            neighbors = session.query(System).filter(System.system_id.in_(neighbor_ids)).all()
            return [self._system_to_dict(sys) for sys in neighbors]
        finally:
            session.close()

    @staticmethod
    def _system_to_dict(system: System) -> Dict:
        """Convert system to compact dict for JSON.

        Optimized for mobile: minimal fields, compact representation.
        """
        if not system:
            return None

        return {
            'id': system.system_id,
            'name': system.name,
            'region_id': system.region_id,
            'constellation_id': system.constellation_id,
            'security': system.security_status,
            'sec_class': system.security_class,
            'is_wormhole': system.is_wormhole,
            'x': system.x,
            'y': system.y,
            'z': system.z,
            'planets': system.planets,
            'stars': system.stars,
            'stargates': system.stargates,
        }


class RegionRepository:
    """Queries for region data."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_all(self) -> List[Dict]:
        """Get all regions.

        Returns:
            List of region dicts
        """
        session = self.db.get_session()
        try:
            regions = session.query(Region).order_by(Region.name).all()
            return [self._region_to_dict(r) for r in regions]
        finally:
            session.close()

    def get_by_id(self, region_id: int) -> Optional[Dict]:
        """Get region by ID.

        Args:
            region_id: Region ID

        Returns:
            Region dict or None
        """
        session = self.db.get_session()
        try:
            region = session.query(Region).filter_by(region_id=region_id).first()
            return self._region_to_dict(region) if region else None
        finally:
            session.close()

    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get region by name.

        Args:
            name: Region name

        Returns:
            Region dict or None
        """
        session = self.db.get_session()
        try:
            region = session.query(Region).filter(Region.name.ilike(name)).first()
            return self._region_to_dict(region) if region else None
        finally:
            session.close()

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search regions by name.

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of region dicts
        """
        session = self.db.get_session()
        try:
            regions = session.query(Region).filter(
                Region.name.ilike(f"%{query}%")
            ).limit(limit).all()

            return [self._region_to_dict(r) for r in regions]
        finally:
            session.close()

    @staticmethod
    def _region_to_dict(region: Region) -> Dict:
        """Convert region to dict."""
        if not region:
            return None

        return {
            'id': region.region_id,
            'name': region.name,
            'description': region.description,
        }


class ConstellationRepository:
    """Queries for constellation data."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_by_region(self, region_id: int) -> List[Dict]:
        """Get all constellations in a region.

        Args:
            region_id: Region ID

        Returns:
            List of constellation dicts
        """
        session = self.db.get_session()
        try:
            constellations = session.query(Constellation).filter_by(
                region_id=region_id
            ).order_by(Constellation.name).all()

            return [self._constellation_to_dict(c) for c in constellations]
        finally:
            session.close()

    def get_by_id(self, constellation_id: int) -> Optional[Dict]:
        """Get constellation by ID.

        Args:
            constellation_id: Constellation ID

        Returns:
            Constellation dict or None
        """
        session = self.db.get_session()
        try:
            constellation = session.query(Constellation).filter_by(
                constellation_id=constellation_id
            ).first()
            return self._constellation_to_dict(constellation) if constellation else None
        finally:
            session.close()

    @staticmethod
    def _constellation_to_dict(constellation: Constellation) -> Dict:
        """Convert constellation to dict."""
        if not constellation:
            return None

        return {
            'id': constellation.constellation_id,
            'name': constellation.name,
            'region_id': constellation.region_id,
        }


class DataRepository:
    """Main repository - aggregates all data access."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.systems = SystemRepository(db_manager)
        self.regions = RegionRepository(db_manager)
        self.constellations = ConstellationRepository(db_manager)

    def get_stats(self) -> Dict:
        """Get overall universe statistics.

        Returns:
            Stats dict
        """
        session = self.db.get_session()
        try:
            total_systems = session.query(System).count()
            total_regions = session.query(Region).count()
            total_constellations = session.query(Constellation).count()
            total_stargates = session.query(Stargate).count()

            # Security breakdown
            high_sec = session.query(System).filter(System.security_status >= 0.45).count()
            low_sec = session.query(System).filter(
                and_(System.security_status >= 0.1, System.security_status < 0.45)
            ).count()
            null_sec = session.query(System).filter(System.security_status < 0.1).count()
            wormholes = session.query(System).filter_by(is_wormhole=True).count()

            return {
                'total_systems': total_systems,
                'total_regions': total_regions,
                'total_constellations': total_constellations,
                'total_stargates': total_stargates,
                'security_breakdown': {
                    'high_sec': high_sec,
                    'low_sec': low_sec,
                    'null_sec': null_sec,
                    'wormhole': wormholes,
                }
            }
        finally:
            session.close()
