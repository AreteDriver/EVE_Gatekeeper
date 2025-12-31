"""SQLite schema for EVE Online universe data.

This module defines the database schema for storing:
- Static universe data from SDE (regions, constellations, systems, stargates)
- Live ESI data with TTL caching (kills, jumps, sovereignty)
- Precomputed graph data for pathfinding
- User data (ship configs, pilot profiles, waypoints)
"""

from pathlib import Path

import aiosqlite

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_NAME = "universe.db"


def get_db_path() -> Path:
    """Get the path to the universe database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / DB_NAME


# ============================================================================
# SCHEMA DEFINITIONS
# ============================================================================

SCHEMA_VERSION = 1

# Core universe structure from SDE
REGIONS_TABLE = """
CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    -- Center coordinates for 2D projection
    x REAL NOT NULL DEFAULT 0,
    y REAL NOT NULL DEFAULT 0,
    z REAL NOT NULL DEFAULT 0,
    -- Faction info
    faction_id INTEGER,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_regions_name ON regions(name);
CREATE INDEX IF NOT EXISTS idx_regions_faction ON regions(faction_id);
"""

CONSTELLATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS constellations (
    constellation_id INTEGER PRIMARY KEY,
    region_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    -- Center coordinates
    x REAL NOT NULL DEFAULT 0,
    y REAL NOT NULL DEFAULT 0,
    z REAL NOT NULL DEFAULT 0,
    -- Faction info
    faction_id INTEGER,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);
CREATE INDEX IF NOT EXISTS idx_constellations_region ON constellations(region_id);
CREATE INDEX IF NOT EXISTS idx_constellations_name ON constellations(name);
"""

SOLAR_SYSTEMS_TABLE = """
CREATE TABLE IF NOT EXISTS solar_systems (
    system_id INTEGER PRIMARY KEY,
    constellation_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    -- 3D coordinates from SDE
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    -- Precomputed 2D projection coordinates
    map_x REAL,
    map_y REAL,
    -- Security and classification
    security_status REAL NOT NULL DEFAULT 0.0,
    security_class TEXT,  -- 'highsec', 'lowsec', 'nullsec', 'wormhole'
    -- Star info
    star_id INTEGER,
    star_type_id INTEGER,
    -- Sovereignty
    sovereignty_faction_id INTEGER,
    sovereignty_corp_id INTEGER,
    sovereignty_alliance_id INTEGER,
    -- Flags
    is_wormhole BOOLEAN DEFAULT FALSE,
    is_abyssal BOOLEAN DEFAULT FALSE,
    is_pochven BOOLEAN DEFAULT FALSE,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (constellation_id) REFERENCES constellations(constellation_id),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);
CREATE INDEX IF NOT EXISTS idx_systems_constellation ON solar_systems(constellation_id);
CREATE INDEX IF NOT EXISTS idx_systems_region ON solar_systems(region_id);
CREATE INDEX IF NOT EXISTS idx_systems_name ON solar_systems(name);
CREATE INDEX IF NOT EXISTS idx_systems_security ON solar_systems(security_status);
CREATE INDEX IF NOT EXISTS idx_systems_security_class ON solar_systems(security_class);
CREATE INDEX IF NOT EXISTS idx_systems_map_coords ON solar_systems(map_x, map_y);
"""

STARGATES_TABLE = """
CREATE TABLE IF NOT EXISTS stargates (
    stargate_id INTEGER PRIMARY KEY,
    system_id INTEGER NOT NULL,
    destination_stargate_id INTEGER NOT NULL,
    destination_system_id INTEGER NOT NULL,
    name TEXT,
    type_id INTEGER,
    -- Position in system
    x REAL,
    y REAL,
    z REAL,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES solar_systems(system_id),
    FOREIGN KEY (destination_system_id) REFERENCES solar_systems(system_id)
);
CREATE INDEX IF NOT EXISTS idx_stargates_system ON stargates(system_id);
CREATE INDEX IF NOT EXISTS idx_stargates_destination ON stargates(destination_system_id);
"""

# Graph adjacency for fast pathfinding
SYSTEM_CONNECTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS system_connections (
    from_system_id INTEGER NOT NULL,
    to_system_id INTEGER NOT NULL,
    -- Edge weight modifiers for routing
    base_weight REAL DEFAULT 1.0,
    security_weight REAL DEFAULT 0.0,  -- Added penalty for lowsec/nullsec
    -- Connection type
    connection_type TEXT DEFAULT 'stargate',  -- 'stargate', 'jump_bridge', 'wormhole'
    -- Metadata
    PRIMARY KEY (from_system_id, to_system_id),
    FOREIGN KEY (from_system_id) REFERENCES solar_systems(system_id),
    FOREIGN KEY (to_system_id) REFERENCES solar_systems(system_id)
);
CREATE INDEX IF NOT EXISTS idx_connections_from ON system_connections(from_system_id);
CREATE INDEX IF NOT EXISTS idx_connections_to ON system_connections(to_system_id);
"""

# ============================================================================
# LIVE DATA TABLES (ESI with TTL caching)
# ============================================================================

SYSTEM_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS system_stats (
    system_id INTEGER PRIMARY KEY,
    -- Kill/jump data (from /universe/system_kills and /universe/system_jumps)
    ship_kills INTEGER DEFAULT 0,
    npc_kills INTEGER DEFAULT 0,
    pod_kills INTEGER DEFAULT 0,
    ship_jumps INTEGER DEFAULT 0,
    -- Timestamps for cache invalidation
    kills_updated_at TIMESTAMP,
    jumps_updated_at TIMESTAMP,
    -- Activity metrics (computed)
    activity_index REAL DEFAULT 0.0,  -- Normalized 0-1 activity score
    FOREIGN KEY (system_id) REFERENCES solar_systems(system_id)
);
"""

INCURSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS incursions (
    incursion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    constellation_id INTEGER NOT NULL,
    staging_system_id INTEGER,
    state TEXT NOT NULL,  -- 'withdrawing', 'mobilizing', 'established'
    influence REAL DEFAULT 0.0,
    has_boss BOOLEAN DEFAULT FALSE,
    faction_id INTEGER,
    -- Cache control
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (constellation_id) REFERENCES constellations(constellation_id),
    FOREIGN KEY (staging_system_id) REFERENCES solar_systems(system_id)
);
CREATE INDEX IF NOT EXISTS idx_incursions_constellation ON incursions(constellation_id);
CREATE INDEX IF NOT EXISTS idx_incursions_state ON incursions(state);
"""

SOVEREIGNTY_TABLE = """
CREATE TABLE IF NOT EXISTS sovereignty (
    system_id INTEGER PRIMARY KEY,
    alliance_id INTEGER,
    corporation_id INTEGER,
    faction_id INTEGER,
    -- Infrastructure
    vulnerability_occupancy_level REAL,
    -- Cache control
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES solar_systems(system_id)
);
CREATE INDEX IF NOT EXISTS idx_sovereignty_alliance ON sovereignty(alliance_id);
"""

SOVEREIGNTY_CAMPAIGNS_TABLE = """
CREATE TABLE IF NOT EXISTS sovereignty_campaigns (
    campaign_id INTEGER PRIMARY KEY,
    system_id INTEGER NOT NULL,
    constellation_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,  -- 'tcu_defense', 'ihub_defense', 'station_defense', etc.
    structure_id INTEGER,
    start_time TIMESTAMP,
    -- Participants
    defender_id INTEGER,
    defender_score REAL DEFAULT 0.0,
    attackers_score REAL DEFAULT 0.0,
    -- Cache control
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (system_id) REFERENCES solar_systems(system_id)
);
CREATE INDEX IF NOT EXISTS idx_campaigns_system ON sovereignty_campaigns(system_id);
"""

# ============================================================================
# USER DATA TABLES
# ============================================================================

SHIP_CONFIGS_TABLE = """
CREATE TABLE IF NOT EXISTS ship_configs (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ship_type_id INTEGER NOT NULL,
    -- Jump drive attributes
    jump_drive_fuel_need REAL,  -- Isotopes per LY
    jump_drive_range REAL,  -- Max LY
    jump_drive_consumption_modifier REAL DEFAULT 1.0,
    -- Fitting modifiers
    fuel_conservation_level INTEGER DEFAULT 0,  -- JFC skill level
    jump_drive_calibration_level INTEGER DEFAULT 0,  -- JDC skill level
    jump_freighter_level INTEGER DEFAULT 0,  -- Jump Freighter skill
    -- Computed effective range
    effective_range REAL,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

PILOT_PROFILES_TABLE = """
CREATE TABLE IF NOT EXISTS pilot_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER,
    character_name TEXT,
    -- Jump skills
    jump_drive_calibration INTEGER DEFAULT 0,  -- 0-5
    jump_fuel_conservation INTEGER DEFAULT 0,  -- 0-5
    jump_freighter INTEGER DEFAULT 0,  -- 0-5
    -- Navigation skills
    navigation INTEGER DEFAULT 0,
    warp_drive_operation INTEGER DEFAULT 0,
    -- Standing filters for routing
    avoid_faction_ids TEXT,  -- JSON array of faction IDs to avoid
    avoid_corporation_ids TEXT,  -- JSON array of corp IDs to avoid
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SAVED_ROUTES_TABLE = """
CREATE TABLE IF NOT EXISTS saved_routes (
    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    origin_system_id INTEGER NOT NULL,
    destination_system_id INTEGER NOT NULL,
    -- Route options
    route_type TEXT DEFAULT 'shortest',  -- 'shortest', 'secure', 'insecure'
    avoid_systems TEXT,  -- JSON array of system IDs
    avoid_regions TEXT,  -- JSON array of region IDs
    -- Computed route
    waypoints TEXT NOT NULL,  -- JSON array of system IDs
    total_jumps INTEGER,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (origin_system_id) REFERENCES solar_systems(system_id),
    FOREIGN KEY (destination_system_id) REFERENCES solar_systems(system_id)
);
"""

CYNO_CHAINS_TABLE = """
CREATE TABLE IF NOT EXISTS cyno_chains (
    chain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    ship_config_id INTEGER,
    pilot_profile_id INTEGER,
    -- Chain definition
    origin_system_id INTEGER NOT NULL,
    destination_system_id INTEGER NOT NULL,
    midpoints TEXT NOT NULL,  -- JSON array of {system_id, is_cyno_beacon}
    -- Computed values
    total_fuel INTEGER,
    total_legs INTEGER,
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ship_config_id) REFERENCES ship_configs(config_id),
    FOREIGN KEY (pilot_profile_id) REFERENCES pilot_profiles(profile_id)
);
"""

# ESI Cache table for generic endpoint caching
ESI_CACHE_TABLE = """
CREATE TABLE IF NOT EXISTS esi_cache (
    cache_key TEXT PRIMARY KEY,
    endpoint TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON response
    etag TEXT,
    expires_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_esi_cache_endpoint ON esi_cache(endpoint);
CREATE INDEX IF NOT EXISTS idx_esi_cache_expires ON esi_cache(expires_at);
"""

# Schema version tracking
SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# All table definitions in order
ALL_TABLES = [
    SCHEMA_VERSION_TABLE,
    REGIONS_TABLE,
    CONSTELLATIONS_TABLE,
    SOLAR_SYSTEMS_TABLE,
    STARGATES_TABLE,
    SYSTEM_CONNECTIONS_TABLE,
    SYSTEM_STATS_TABLE,
    INCURSIONS_TABLE,
    SOVEREIGNTY_TABLE,
    SOVEREIGNTY_CAMPAIGNS_TABLE,
    SHIP_CONFIGS_TABLE,
    PILOT_PROFILES_TABLE,
    SAVED_ROUTES_TABLE,
    CYNO_CHAINS_TABLE,
    ESI_CACHE_TABLE,
]


async def create_tables(db_path: Path | None = None) -> None:
    """Create all database tables.

    Args:
        db_path: Path to the database file. Defaults to data/universe.db
    """
    if db_path is None:
        db_path = get_db_path()

    async with aiosqlite.connect(db_path) as db:
        # Execute each table creation statement
        for table_sql in ALL_TABLES:
            # Split by semicolons to handle CREATE TABLE + CREATE INDEX
            statements = [s.strip() for s in table_sql.split(";") if s.strip()]
            for stmt in statements:
                await db.execute(stmt)

        # Insert schema version if not exists
        await db.execute(
            "INSERT OR IGNORE INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,)
        )
        await db.commit()


async def get_schema_version(db_path: Path | None = None) -> int:
    """Get the current schema version."""
    if db_path is None:
        db_path = get_db_path()

    if not db_path.exists():
        return 0

    async with aiosqlite.connect(db_path) as db:
        try:
            cursor = await db.execute("SELECT MAX(version) FROM schema_version")
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 0
        except aiosqlite.OperationalError:
            return 0


async def reset_database(db_path: Path | None = None) -> None:
    """Drop and recreate all tables. USE WITH CAUTION."""
    if db_path is None:
        db_path = get_db_path()

    if db_path.exists():
        db_path.unlink()

    await create_tables(db_path)
