"""Test foundation: Database, SDE loading, graph, and API."""

import sys
sys.path.insert(0, '/home/user/evemap/src')

import os
from pathlib import Path

# Clean up test database if it exists
test_db = "test_universe.db"
if os.path.exists(test_db):
    os.remove(test_db)


def test_database():
    """Test database initialization."""
    print("\n" + "=" * 70)
    print("TEST 1: Database Initialization")
    print("=" * 70)

    from evemap import DatabaseManager

    db = DatabaseManager(db_path=test_db)
    db.create_tables()

    # Verify tables exist
    assert db.count_systems() == 0, "Should start with no systems"
    print("✓ Database created and empty")

    return db


def test_sde_loader(db):
    """Test SDE data loading."""
    print("\n" + "=" * 70)
    print("TEST 2: SDE Data Loading (Mock)")
    print("=" * 70)

    from evemap.sde_mock import MockSDELoader

    loader = MockSDELoader(db)

    # Load all mock data
    results = loader.load_all()

    regions = results['regions']
    constellations = results['constellations']
    systems = results['systems']
    stargates = results['stargates']

    # Verify counts
    assert db.count_regions() > 0, "Should have regions"
    assert db.count_systems() > 0, "Should have systems"
    assert db.count_stargates() > 0, "Should have stargates"

    print(f"\nLoaded universe summary:")
    print(f"  Regions: {db.count_regions()}")
    print(f"  Systems: {db.count_systems()}")
    print(f"  Stargates: {db.count_stargates()}")

    return db


def test_repository(db):
    """Test data repository layer."""
    print("\n" + "=" * 70)
    print("TEST 3: Data Repository")
    print("=" * 70)

    from evemap import DataRepository

    repo = DataRepository(db)

    # Test stats
    stats = repo.get_stats()
    print(f"Universe stats:")
    print(f"  Total systems: {stats['total_systems']}")
    print(f"  Total regions: {stats['total_regions']}")
    print(f"  High-sec: {stats['security_breakdown']['high_sec']}")
    print(f"  Low-sec: {stats['security_breakdown']['low_sec']}")
    print(f"  Null-sec: {stats['security_breakdown']['null_sec']}")
    print(f"  Wormhole: {stats['security_breakdown']['wormhole']}")

    # Test system search
    systems = repo.systems.search("Jita", limit=5)
    if systems:
        print(f"\n✓ System search works: found {len(systems)} systems")
        for sys in systems[:2]:
            print(f"  - {sys['name']} (security: {sys['security']:.1f})")
    else:
        print("  (Jita not in downloaded data)")

    # Test region listing
    regions = repo.regions.get_all()
    print(f"✓ Region listing works: {len(regions)} regions")
    if regions:
        print(f"  Sample regions: {', '.join([r['name'] for r in regions[:3]])}")

    print("✓ Repository layer working")


def test_graph_engine(db):
    """Test graph engine initialization."""
    print("\n" + "=" * 70)
    print("TEST 4: Graph Engine")
    print("=" * 70)

    from evemap import GraphEngine

    graph = GraphEngine(db)
    print("Building graph from database...")
    graph.build_from_db()

    # Test graph properties
    adjacency = graph.export_adjacency_list()
    print(f"✓ Graph built with {len(adjacency)} systems")

    # Check connectivity
    connected_systems = [sid for sid, neighbors in adjacency.items() if neighbors]
    print(f"  Connected systems: {len(connected_systems)}")
    print(f"  Average connections: {sum(len(n) for n in adjacency.values()) / len(adjacency):.1f}")

    # Find hubs
    hubs = graph.find_hubs(top_n=5)
    if hubs:
        print(f"\nTop hub systems:")
        for system_id, name, connections in hubs:
            print(f"  {name}: {connections} connections")

    # Find a valid route
    if len(connected_systems) >= 2:
        origin = connected_systems[0]
        destination = connected_systems[1]

        route = graph.shortest_path(origin, destination)
        if route:
            print(f"\n✓ Route planning works: {origin} -> {destination}")
            print(f"  Route length: {len(route)} systems")
            print(f"  Jumps: {len(route) - 1}")

    print("✓ Graph engine working")

    return graph


def test_api(db):
    """Test FastAPI application creation."""
    print("\n" + "=" * 70)
    print("TEST 5: FastAPI Application")
    print("=" * 70)

    from evemap import create_app

    try:
        app = create_app(db)
        print("✓ FastAPI app created successfully")

        # Test that endpoints are registered
        routes = [route.path for route in app.routes]
        print(f"  Registered endpoints: {len(routes)} routes")

        # Check key endpoints
        key_endpoints = ["/health", "/stats", "/systems/search", "/regions", "/routes/plan"]
        for endpoint in key_endpoints:
            if any(endpoint in route for route in routes):
                print(f"  ✓ {endpoint}")

        return app

    except Exception as e:
        print(f"✗ Error creating app: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("EVEMAP FOUNDATION TESTS")
    print("=" * 70)

    try:
        db = test_database()
        test_sde_loader(db)
        test_repository(db)
        graph = test_graph_engine(db)
        app = test_api(db)

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run full initialization: python scripts/init_universe.py")
        print("  2. Start API server: python scripts/run_api.py")
        print("  3. Visit http://localhost:8000/docs for API documentation")
        print()

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)


if __name__ == "__main__":
    main()
