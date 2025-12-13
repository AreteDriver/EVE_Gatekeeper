"""
Generate demo visualizations for README and documentation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from evemap import NedenMap
from evemap.models import System, JumpConnection, SecurityStatus


def create_demo_data():
    """Create demo EVE Online system data for visualization."""
    
    # Create systems with different security statuses
    systems = {
        # High-sec systems (blue)
        30000142: System(
            system_id=30000142, name="Jita", region_id=10000002, 
            constellation_id=20000020, security_status=0.95, 
            planets=30, stargates=4
        ),
        30001161: System(
            system_id=30001161, name="Perimeter", region_id=10000002,
            constellation_id=20000020, security_status=0.90,
            planets=8, stargates=5
        ),
        30002768: System(
            system_id=30002768, name="Sobaseki", region_id=10000002,
            constellation_id=20000020, security_status=0.85,
            planets=15, stargates=4
        ),
        30002060: System(
            system_id=30002060, name="Urlen", region_id=10000002,
            constellation_id=20000020, security_status=0.80,
            planets=6, stargates=3
        ),
        30000144: System(
            system_id=30000144, name="Maurasi", region_id=10000002,
            constellation_id=20000020, security_status=0.75,
            planets=12, stargates=4
        ),
        30003068: System(
            system_id=30003068, name="Inaro", region_id=10000002,
            constellation_id=20000020, security_status=0.70,
            planets=9, stargates=3
        ),
        30001392: System(
            system_id=30001392, name="Uotila", region_id=10000002,
            constellation_id=20000020, security_status=0.65,
            planets=7, stargates=4
        ),
        30000145: System(
            system_id=30000145, name="Airkio", region_id=10000002,
            constellation_id=20000020, security_status=0.60,
            planets=10, stargates=3
        ),
        
        # Low-sec systems (orange)
        30002659: System(
            system_id=30002659, name="Uemon", region_id=10000002,
            constellation_id=20000021, security_status=0.45,
            planets=8, stargates=3
        ),
        30002667: System(
            system_id=30002667, name="Otela", region_id=10000002,
            constellation_id=20000021, security_status=0.35,
            planets=6, stargates=3
        ),
        30002650: System(
            system_id=30002650, name="Otsasai", region_id=10000002,
            constellation_id=20000021, security_status=0.25,
            planets=5, stargates=2
        ),
        30002651: System(
            system_id=30002651, name="Inoue", region_id=10000002,
            constellation_id=20000021, security_status=0.15,
            planets=4, stargates=3
        ),
        
        # Null-sec systems (red)
        30002652: System(
            system_id=30002652, name="Oijamon", region_id=10000003,
            constellation_id=20000022, security_status=-0.1,
            planets=8, stargates=2
        ),
        30002653: System(
            system_id=30002653, name="Aunenen", region_id=10000003,
            constellation_id=20000022, security_status=-0.3,
            planets=7, stargates=2
        ),
        30002654: System(
            system_id=30002654, name="Kulelen", region_id=10000003,
            constellation_id=20000022, security_status=-0.5,
            planets=6, stargates=2
        ),
    }
    
    # Create a network of connections
    connections = [
        # High-sec cluster
        JumpConnection(30000142, 30001161),  # Jita <-> Perimeter
        JumpConnection(30001161, 30002768),  # Perimeter <-> Sobaseki
        JumpConnection(30002768, 30002060),  # Sobaseki <-> Urlen
        JumpConnection(30002060, 30000142),  # Urlen <-> Jita
        JumpConnection(30000144, 30001161),  # Maurasi <-> Perimeter
        JumpConnection(30000144, 30003068),  # Maurasi <-> Inaro
        JumpConnection(30003068, 30001392),  # Inaro <-> Uotila
        JumpConnection(30001392, 30000145),  # Uotila <-> Airkio
        JumpConnection(30000145, 30002768),  # Airkio <-> Sobaseki
        JumpConnection(30001392, 30000142),  # Uotila <-> Jita
        
        # Transition to low-sec
        JumpConnection(30000145, 30002659),  # Airkio <-> Uemon
        JumpConnection(30002659, 30002667),  # Uemon <-> Otela
        JumpConnection(30002667, 30002650),  # Otela <-> Otsasai
        JumpConnection(30002650, 30002651),  # Otsasai <-> Inoue
        JumpConnection(30002651, 30003068),  # Inoue <-> Inaro
        
        # Transition to null-sec
        JumpConnection(30002651, 30002652),  # Inoue <-> Oijamon
        JumpConnection(30002652, 30002653),  # Oijamon <-> Aunenen
        JumpConnection(30002653, 30002654),  # Aunenen <-> Kulelen
        JumpConnection(30002654, 30002650),  # Kulelen <-> Otsasai
    ]
    
    return systems, connections


def main():
    """Generate demo visualizations."""
    
    print("=" * 70)
    print("GENERATING DEMO VISUALIZATIONS FOR EVE MAP")
    print("=" * 70)
    print()
    
    # Create demo data
    systems, connections = create_demo_data()
    print(f"Created demo data: {len(systems)} systems, {len(connections)} connections")
    
    # Create map
    map_viz = NedenMap(systems, connections)
    
    # Get statistics
    stats = map_viz.get_stats()
    print("\nMap Statistics:")
    print(f"  Total systems: {stats['total_systems']}")
    print(f"  Total connections: {stats['total_connections']}")
    print(f"  Security breakdown: {stats['security_breakdown']}")
    print()
    
    # Calculate layout
    print("Calculating layout...")
    map_viz.calculate_layout(method="spring", iterations=150, seed=42)
    print("Layout calculated!")
    print()
    
    # Create assets directory if it doesn't exist
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. Generate security status map
    print("1. Generating security status map...")
    fig1 = map_viz.render(
        figsize=(16, 12),
        dpi=150,
        show_labels=True,
        show_edges=True,
        group_by=None  # Color by security
    )
    output_path1 = os.path.join(assets_dir, 'map_security_status.png')
    map_viz.save(output_path1, dpi=150)
    print(f"   Saved to {output_path1}")
    plt.close(fig1)
    
    # 2. Generate filtered high-sec only map
    print("2. Generating high-sec systems map...")
    fig2 = map_viz.render(
        figsize=(14, 10),
        dpi=150,
        show_labels=True,
        show_edges=True,
        filter_security={SecurityStatus.HIGH_SEC}
    )
    output_path2 = os.path.join(assets_dir, 'map_high_sec.png')
    map_viz.save(output_path2, dpi=150)
    print(f"   Saved to {output_path2}")
    plt.close(fig2)
    
    # 3. Generate route visualization
    print("3. Generating route visualization...")
    # Highlight a specific route from Jita to null-sec
    fig3, ax3 = plt.subplots(figsize=(16, 12), dpi=150)
    
    # Draw all edges first (gray)
    for connection in connections:
        if connection.source_system_id in systems and connection.target_system_id in systems:
            x0, y0 = map_viz.layout[connection.source_system_id]
            x1, y1 = map_viz.layout[connection.target_system_id]
            ax3.plot([x0, x1], [y0, y1], 'gray', alpha=0.3, linewidth=0.5, zorder=1)
    
    # Highlight a route (e.g., Jita -> Perimeter -> Maurasi -> Inaro -> Inoue -> Oijamon)
    route_path = [30000142, 30001161, 30000144, 30003068, 30002651, 30002652]
    for i in range(len(route_path) - 1):
        source = route_path[i]
        target = route_path[i + 1]
        x0, y0 = map_viz.layout[source]
        x1, y1 = map_viz.layout[target]
        ax3.plot([x0, x1], [y0, y1], color='#00FF00', linewidth=3, zorder=5, alpha=0.8)
    
    # Draw all nodes by security
    for sec_class in SecurityStatus:
        group_systems = [s for s in systems.values() if s.security_class == sec_class]
        if not group_systems:
            continue
        x_pos = [map_viz.layout[s.system_id][0] for s in group_systems]
        y_pos = [map_viz.layout[s.system_id][1] for s in group_systems]
        color = map_viz.SECURITY_COLORS[sec_class]
        ax3.scatter(x_pos, y_pos, c=color, s=100, alpha=0.7, zorder=2,
                   edgecolors='black', linewidth=0.5, label=sec_class.value)
    
    # Highlight route nodes
    for node in route_path:
        x, y = map_viz.layout[node]
        ax3.scatter([x], [y], c='#00FF00', s=250, alpha=0.5, zorder=6,
                   edgecolors='#00FF00', linewidth=3)
    
    # Draw labels
    for system in systems.values():
        x, y = map_viz.layout[system.system_id]
        fontsize = 8 if system.system_id in route_path else 6
        weight = 'bold' if system.system_id in route_path else 'normal'
        ax3.text(x, y, system.name, fontsize=fontsize, fontweight=weight,
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7),
                zorder=7 if system.system_id in route_path else 3)
    
    ax3.set_title("EVE Online Map - Planned Route Visualization", 
                 fontsize=18, fontweight='bold', pad=20)
    ax3.set_xlabel("X Position", fontsize=12)
    ax3.set_ylabel("Y Position", fontsize=12)
    ax3.grid(True, alpha=0.2)
    ax3.set_aspect('equal')
    ax3.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    output_path3 = os.path.join(assets_dir, 'map_route_planned.png')
    fig3.savefig(output_path3, dpi=150, bbox_inches='tight')
    print(f"   Saved to {output_path3}")
    plt.close(fig3)
    
    print()
    print("=" * 70)
    print("Demo visualizations generated successfully!")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  - {output_path1}")
    print(f"  - {output_path2}")
    print(f"  - {output_path3}")
    print()


if __name__ == "__main__":
    main()
