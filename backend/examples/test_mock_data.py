"""
Test example: Use mock data to test visualization without API calls.

This is useful for development and testing without relying on ESI API.
"""

import sys
sys.path.insert(0, '/home/user/evemap/src')

from evemap import NedenMap
from evemap.models import System, JumpConnection
from evemap.utils import JumpRangeCalculator, MapAnalyzer


def create_mock_data():
    """Create mock EVE Online system data for testing."""

    # Create mock systems (simplified Forge region)
    systems = {
        30000142: System(
            system_id=30000142, name="Jita", region_id=10000002, constellation_id=20000020,
            security_status=5.0, planets=30, stargates=1
        ),
        30001161: System(
            system_id=30001161, name="Perimeter", region_id=10000002, constellation_id=20000020,
            security_status=5.0, planets=8, stargates=3
        ),
        30002768: System(
            system_id=30002768, name="Sobaseki", region_id=10000002, constellation_id=20000020,
            security_status=4.8, planets=15, stargates=2
        ),
        30002060: System(
            system_id=30002060, name="Urlen", region_id=10000002, constellation_id=20000020,
            security_status=4.5, planets=6, stargates=1
        ),
        30000144: System(
            system_id=30000144, name="Isanamo", region_id=10000002, constellation_id=20000020,
            security_status=4.2, planets=12, stargates=2
        ),
        30003068: System(
            system_id=30003068, name="Kisogo", region_id=10000002, constellation_id=20000020,
            security_status=3.8, planets=9, stargates=1
        ),
    }

    # Create mock connections
    connections = [
        JumpConnection(30000142, 30001161),  # Jita <-> Perimeter
        JumpConnection(30001161, 30002768),  # Perimeter <-> Sobaseki
        JumpConnection(30002768, 30002060),  # Sobaseki <-> Urlen
        JumpConnection(30002060, 30000142),  # Urlen <-> Jita
        JumpConnection(30000144, 30001161),  # Isanamo <-> Perimeter
        JumpConnection(30000144, 30003068),  # Isanamo <-> Kisogo
    ]

    return systems, connections


def main():
    """Run mock data test."""

    print("=" * 60)
    print("EVE MAP VISUALIZATION - MOCK DATA TEST")
    print("=" * 60)
    print()

    # Create mock data
    systems, connections = create_mock_data()

    print(f"Created mock data with {len(systems)} systems and {len(connections)} connections")
    print()

    # Create map
    map_viz = NedenMap(systems, connections)

    # Get statistics
    stats = map_viz.get_stats()
    print("Map Statistics:")
    print(f"  Total systems: {stats['total_systems']}")
    print(f"  Total connections: {stats['total_connections']}")
    print(f"  Avg connections per system: {stats['avg_connections_per_system']:.2f}")
    print()

    # Calculate layout
    print("Calculating layout...")
    map_viz.calculate_layout(method="spring", iterations=100)
    print("Layout calculated successfully!")
    print()

    # Test analysis tools
    print("Testing analysis tools...")
    analyzer = MapAnalyzer(systems, connections)

    # Hub systems
    hubs = analyzer.get_hub_systems(top_n=3)
    print("\nTop hub systems:")
    for system_id, name, conn_count in hubs:
        print(f"  - {name} ({system_id}): {conn_count} connections")

    # Isolated systems
    isolated = analyzer.get_isolated_systems()
    if isolated:
        print("\nIsolated systems (no connections):")
        for system_id, name in isolated:
            print(f"  - {name}")
    else:
        print("\nNo isolated systems found")

    # Connectivity metrics
    metrics = analyzer.get_connectivity_metrics()
    print("\nConnectivity Metrics:")
    print(f"  Density: {metrics['density']:.3f}")
    print(f"  Average degree: {metrics['average_degree']:.2f}")
    print()

    # Test jump range calculator
    print("Testing jump range calculator...")
    jump_calc = JumpRangeCalculator(systems, connections)

    # Find systems in range from Jita
    jita_id = 30000142
    systems_in_range = jump_calc.get_systems_in_range(jita_id, 2.0)
    print(f"Systems within range 2.0 of Jita: {len(systems_in_range)} systems")

    # Find route
    route = jump_calc.get_route_via_jumps(30000142, 30003068)
    if route:
        route_names = [systems[sid].name for sid in route if sid in systems]
        print(f"Jump route Jita -> Kisogo: {' -> '.join(route_names)}")
    print()

    # Render visualization
    print("Rendering map visualization...")
    try:
        fig = map_viz.render(
            figsize=(14, 12),
            dpi=100,
            show_labels=True,
            show_edges=True,
            group_by=None
        )
        map_viz.save('/home/user/evemap/examples/test_mock_map.png')
        print("Mock map saved to examples/test_mock_map.png")
    except Exception as e:
        print(f"Error rendering map: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
    print("Mock data test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
