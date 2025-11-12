"""Database schema and ORM for EVE universe data."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from typing import Optional
import os

Base = declarative_base()


# Association tables for many-to-many relationships
region_constellation_assoc = Table(
    'region_constellation',
    Base.metadata,
    Column('region_id', Integer, ForeignKey('regions.region_id')),
    Column('constellation_id', Integer, ForeignKey('constellations.constellation_id'))
)

constellation_system_assoc = Table(
    'constellation_system',
    Base.metadata,
    Column('constellation_id', Integer, ForeignKey('constellations.constellation_id')),
    Column('system_id', Integer, ForeignKey('systems.system_id'))
)


class Region(Base):
    """Region in New Eden."""
    __tablename__ = 'regions'

    region_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)

    # Relationships
    constellations = relationship(
        'Constellation',
        secondary=region_constellation_assoc,
        back_populates='regions'
    )
    systems = relationship('System', back_populates='region')

    def __repr__(self):
        return f"<Region {self.name} ({self.region_id})>"


class Constellation(Base):
    """Constellation in New Eden."""
    __tablename__ = 'constellations'

    constellation_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey('regions.region_id'), nullable=False)

    # Relationships
    regions = relationship(
        'Region',
        secondary=region_constellation_assoc,
        back_populates='constellations'
    )
    systems = relationship(
        'System',
        secondary=constellation_system_assoc,
        back_populates='constellations'
    )

    def __repr__(self):
        return f"<Constellation {self.name} ({self.constellation_id})>"


class System(Base):
    """Solar system in New Eden."""
    __tablename__ = 'systems'

    system_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey('regions.region_id'), nullable=False)
    constellation_id = Column(Integer, ForeignKey('constellations.constellation_id'), nullable=False)

    # Universe properties
    security_status = Column(Float, nullable=False)
    is_wormhole = Column(Boolean, default=False)

    # Spatial coordinates (for layout + distance calculations)
    x = Column(Float, nullable=True)  # AU
    y = Column(Float, nullable=True)  # AU
    z = Column(Float, nullable=True)  # AU

    # Content
    planets = Column(Integer, default=0)
    stars = Column(Integer, default=0)
    stargates = Column(Integer, default=0)

    # Metadata
    star_id = Column(Integer, nullable=True)
    sunTypeId = Column(Integer, nullable=True)

    # Relationships
    region = relationship('Region', back_populates='systems')
    constellation = relationship('Constellation')
    constellations = relationship(
        'Constellation',
        secondary=constellation_system_assoc,
        back_populates='systems'
    )

    # Jump gate connections (outbound)
    stargates_from = relationship(
        'Stargate',
        foreign_keys='Stargate.system_id',
        back_populates='system'
    )

    def __repr__(self):
        return f"<System {self.name} ({self.system_id})>"

    @property
    def security_class(self) -> str:
        """Classify by security status."""
        if self.is_wormhole:
            return "wormhole"
        elif self.security_status >= 0.45:
            return "high_sec"
        elif self.security_status >= 0.1:
            return "low_sec"
        else:
            return "null_sec"


class Stargate(Base):
    """Jump gate connecting two systems."""
    __tablename__ = 'stargates'

    stargate_id = Column(Integer, primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.system_id'), nullable=False)
    destination_system_id = Column(Integer, ForeignKey('systems.system_id'), nullable=False)

    name = Column(String(255), nullable=True)
    type_id = Column(Integer, nullable=True)

    # Relationships
    system = relationship('System', foreign_keys=[system_id], back_populates='stargates_from')
    destination_system = relationship('System', foreign_keys=[destination_system_id])

    def __repr__(self):
        return f"<Stargate {self.stargate_id} ({self.system_id} -> {self.destination_system_id})>"


class Precomputed(Base):
    """Precomputed data (routes, metrics)."""
    __tablename__ = 'precomputed'

    id = Column(Integer, primary_key=True)
    data_type = Column(String(50), nullable=False, index=True)  # "shortest_paths", "k_core", etc.
    source_id = Column(Integer, nullable=True, index=True)
    data_json = Column(String(50000), nullable=False)  # JSON-serialized data
    computed_at = Column(Integer, nullable=False)  # Unix timestamp
    version = Column(String(20), nullable=False)  # SDE version

    def __repr__(self):
        return f"<Precomputed {self.data_type} ({self.version})>"


class DatabaseManager:
    """Manage database connections and setup."""

    def __init__(self, db_path: str = "data/universe.db"):
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = None
        self.Session = None
        self._init_db()

    def _init_db(self):
        """Initialize database engine and session factory."""
        # Create parent directory if needed
        os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True)

        db_url = f"sqlite:///{self.db_path}"
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)
        print(f"Created tables in {self.db_path}")

    def get_session(self):
        """Get a new database session."""
        return self.Session()

    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()

    def count_systems(self) -> int:
        """Count total systems in database."""
        session = self.get_session()
        try:
            return session.query(System).count()
        finally:
            session.close()

    def count_regions(self) -> int:
        """Count total regions."""
        session = self.get_session()
        try:
            return session.query(Region).count()
        finally:
            session.close()

    def count_stargates(self) -> int:
        """Count total stargates."""
        session = self.get_session()
        try:
            return session.query(Stargate).count()
        finally:
            session.close()
