#!/usr/bin/env python3
"""Initialize EVE universe: load SDE, build database, compute routes."""

import sys
import time
sys.path.insert(0, '/home/user/evemap/src')

from evemap import DatabaseManager, SDELoader, GraphEngine


def main():
    """Initialize complete universe database and graph."""

    print("=" * 70)
    print("EVE UNIVERSE INITIALIZATION")
    print("=" * 70)
    print()

    start_time = time.time()

    # Step 1: Initialize database
    print("STEP 1: Creating database schema...")
    db = DatabaseManager(db_path="data/universe.db")
    db.create_tables()
    print("✓ Database created\n")

    # Step 2: Load SDE
    print("STEP 2: Loading EVE Static Data Export (SDE)...")
    print("This may take several minutes on first run...")
    loader = SDELoader(db)
    sde_results = loader.load_all()
    print()

    # Step 3: Display stats
    print("STEP 3: Universe Statistics")
    print("-" * 70)
    stats = {
        'Regions': sde_results['regions'],
        'Constellations': sde_results['constellations'],
        'Systems': sde_results['systems'],
        'Stargates': sde_results['stargates'],
    }

    for label, count in stats.items():
        print(f"  {label:.<40} {count:>10,}")

    print()

    # Step 4: Build graph
    print("STEP 4: Building graph engine...")
    graph = GraphEngine(db)
    graph.build_from_db()
    print()

    # Step 5: Analyze graph
    print("STEP 5: Graph Analysis")
    print("-" * 70)

    hubs = graph.find_hubs(top_n=10)
    print("\nTop 10 Hub Systems (by connections):")
    for system_id, name, connections in hubs[:5]:
        print(f"  {name:.<40} {connections:>3} connections")

    bottlenecks = graph.find_bottlenecks(top_n=10)
    print("\nTop Bottleneck Systems:")
    for system_id, name, score in bottlenecks[:5]:
        print(f"  {name:.<40} {score:>6.2f}")

    region_connectivity = graph.get_region_connectivity()
    print(f"\nRegion Analysis: {len(region_connectivity)} regions")
    print("  Sample regions:")
    for i, (region_id, data) in enumerate(list(region_connectivity.items())[:3]):
        print(f"    {data['name']:.<35} {data['internal_edges']:>4} internal edges, "
              f"{data['external_edges']:>4} external")

    print()

    # Step 6: Export for mobile
    print("STEP 6: Exporting graph for mobile clients...")
    graph.export_as_json("data/universe_graph.json")
    print()

    # Final summary
    elapsed = time.time() - start_time
    print("=" * 70)
    print("✓ UNIVERSE INITIALIZATION COMPLETE")
    print("=" * 70)
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print()
    print("Next steps:")
    print("  1. Start the API server: python -m evemap.api")
    print("  2. Open http://localhost:8000/docs for API documentation")
    print("  3. Build your iOS app to consume the REST API")
    print()


if __name__ == "__main__":
    main()
