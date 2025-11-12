"""
Basic example: Fetch a region and create a 2D map visualization.

This example demonstrates:
1. Fetching data from EVE's ESI API
2. Building a graph and calculating layout
3. Rendering different visualizations
"""

import sys
sys.path.insert(0, '/home/user/evemap/src')

from evemap import ESIClient, NedenMap
from evemap.models import SecurityStatus


def main():
    """Run the basic map example."""

    # Example region IDs in EVE Online:
    # 10000002 - The Forge (Jita - trade hub)
    # 10000043 - Domain (high sec)
    # 10000030 - Heimatar (low sec)
    # 10000014 - Null Sec Example

    REGION_ID = 10000002  # The Forge

    # Initialize ESI client
    print("=" * 60)
    print("EVE MAP VISUALIZATION - BASIC EXAMPLE")
    print("=" * 60)
    print()

    client = ESIClient()

    # Fetch region data
    result = client.get_region_data(REGION_ID)
    if not result:
        print("Failed to fetch region data")
        return

    systems, constellations, connections = result

    print()
    print(f"Successfully fetched:")
    print(f"  - {len(systems)} systems")
    print(f"  - {len(constellations)} constellations")
    print(f"  - {len(connections)} jump connections")
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
    print("  Security Breakdown:")
    for sec_type, count in stats['security_breakdown'].items():
        print(f"    {sec_type}: {count}")
    print()

    # Calculate layout
    print("Calculating layout...")
    map_viz.calculate_layout(method="spring", iterations=100)

    # Render visualization 1: Colored by security status
    print("Rendering map (colored by security status)...")
    fig1 = map_viz.render(
        figsize=(20, 16),
        dpi=100,
        show_labels=True,
        show_edges=True,
        group_by=None  # Color by security
    )
    map_viz.save('/home/user/evemap/examples/map_security_status.png')
    print()

    # Render visualization 2: Grouped by constellation
    print("Rendering map (grouped by constellation)...")
    fig2 = map_viz.render(
        figsize=(20, 16),
        dpi=100,
        show_labels=True,
        show_edges=True,
        group_by="constellation"
    )
    map_viz.save('/home/user/evemap/examples/map_by_constellation.png')
    print()

    # Render visualization 3: Only high-sec systems
    print("Rendering map (high-sec only)...")
    fig3 = map_viz.render(
        figsize=(20, 16),
        dpi=100,
        show_labels=True,
        show_edges=True,
        filter_security={SecurityStatus.HIGH_SEC}
    )
    map_viz.save('/home/user/evemap/examples/map_high_sec.png')
    print()

    print("=" * 60)
    print("All visualizations created successfully!")
    print("Output files:")
    print("  - examples/map_security_status.png")
    print("  - examples/map_by_constellation.png")
    print("  - examples/map_high_sec.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
