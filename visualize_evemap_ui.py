#!/usr/bin/env python3
"""
EVE Map - Visual UI & Map Representations
Generates visualization of the starmap and UI layouts
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
import numpy as np
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.collections import LineCollection

# ============================================================
# 1. STARMAP VISUALIZATION
# ============================================================

def visualize_starmap():
    """Generate a visual representation of the EVE starmap with systems and routes"""

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Sample universe data (Forge region)
    systems = {
        'Jita': {'pos': (0, 0), 'security': 5.0, 'type': 'highsec'},
        'Perimeter': {'pos': (1.5, 0.5), 'security': 5.0, 'type': 'highsec'},
        'Isanamo': {'pos': (-1.5, 0.5), 'security': 5.0, 'type': 'highsec'},
        'Urlen': {'pos': (1.5, -1.5), 'security': 0.4, 'type': 'lowsec'},
        'Sobaseki': {'pos': (0, -1.5), 'security': -5.0, 'type': 'nullsec'},
    }

    connections = [
        ('Jita', 'Perimeter'),
        ('Jita', 'Isanamo'),
        ('Perimeter', 'Urlen'),
        ('Urlen', 'Sobaseki'),
        ('Sobaseki', 'Isanamo'),
    ]

    # Create graph
    G = nx.Graph()
    for sys_name in systems.keys():
        G.add_node(sys_name)
    for src, dst in connections:
        G.add_edge(src, dst)

    # PLOT 1: Full Universe Map
    ax = axes[0]
    ax.set_title('EVE Starmap - The Forge Region', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.set_xlabel('X Coordinate (Light Years)', fontsize=10)
    ax.set_ylabel('Y Coordinate (Light Years)', fontsize=10)

    # Draw connections (jump gates)
    for src, dst in connections:
        x1, y1 = systems[src]['pos']
        x2, y2 = systems[dst]['pos']
        ax.plot([x1, x2], [y1, y2], 'b-', linewidth=1.5, alpha=0.6, zorder=1)

        # Add jump gate markers
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.plot(mid_x, mid_y, 'bs', markersize=4, alpha=0.4, zorder=1)

    # Draw systems with color coding
    for sys_name, data in systems.items():
        x, y = data['pos']
        security = data['security']

        # Color by security
        if security >= 0.5:
            color = '#00FF00'  # Green - High-Sec
            label = 'HS'
        elif security > 0:
            color = '#FFAA00'  # Orange - Low-Sec
            label = 'LS'
        else:
            color = '#FF0000'  # Red - Null-Sec
            label = 'NS'

        # Draw star
        ax.plot(x, y, 'o', color=color, markersize=15, zorder=3, alpha=0.8)
        ax.plot(x, y, '*', color='white', markersize=8, zorder=4)

        # Add system name
        ax.text(x, y + 0.35, sys_name, ha='center', fontsize=9, fontweight='bold')

        # Add security indicator
        ax.text(x, y - 0.35, f'{label} ({security:+.1f})', ha='center', fontsize=8, color=color)

    # Legend
    ax.text(-2.8, 1.5, 'Security Levels:', fontsize=10, fontweight='bold')
    ax.plot(-2.5, 1.2, 'o', color='#00FF00', markersize=10, label='High-Sec (0.5+)')
    ax.plot(-2.5, 0.9, 'o', color='#FFAA00', markersize=10, label='Low-Sec (0 to 0.5)')
    ax.plot(-2.5, 0.6, 'o', color='#FF0000', markersize=10, label='Null-Sec (<0)')
    ax.text(-2.1, 1.2, 'High-Sec (0.5+)', fontsize=9, va='center')
    ax.text(-2.1, 0.9, 'Low-Sec (0 to 0.5)', fontsize=9, va='center')
    ax.text(-2.1, 0.6, 'Null-Sec (<0)', fontsize=9, va='center')

    # PLOT 2: Route Highlighted
    ax = axes[1]
    ax.set_title('Route Planning: Jita → Sobaseki', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle='--')
    ax.set_xlabel('X Coordinate (Light Years)', fontsize=10)
    ax.set_ylabel('Y Coordinate (Light Years)', fontsize=10)

    # Route: Jita → Isanamo → Sobaseki → Urlen → Perimeter
    route = ['Jita', 'Perimeter', 'Urlen', 'Sobaseki', 'Isanamo']
    route_edges = [(route[i], route[i+1]) for i in range(len(route)-1)]

    # Draw all connections (faded)
    for src, dst in connections:
        if (src, dst) not in route_edges and (dst, src) not in route_edges:
            x1, y1 = systems[src]['pos']
            x2, y2 = systems[dst]['pos']
            ax.plot([x1, x2], [y1, y2], 'gray', linewidth=0.5, alpha=0.2, zorder=1)

    # Draw route (highlighted)
    for i, (src, dst) in enumerate(route_edges):
        x1, y1 = systems[src]['pos']
        x2, y2 = systems[dst]['pos']
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=3, color='#FF6600', zorder=2))
        ax.plot([x1, x2], [y1, y2], '#FF6600', linewidth=3, alpha=0.7, zorder=2)

        # Jump number
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x - 0.2, mid_y + 0.2, f'Jump {i+1}', fontsize=8,
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    # Draw systems
    for sys_name, data in systems.items():
        x, y = data['pos']
        security = data['security']

        if security >= 0.5:
            color = '#00FF00'
        elif security > 0:
            color = '#FFAA00'
        else:
            color = '#FF0000'

        # Highlight route systems
        if sys_name in route:
            ax.plot(x, y, 'o', color=color, markersize=20, zorder=3, alpha=0.9)
            ax.plot(x, y, '*', color='white', markersize=10, zorder=4)
        else:
            ax.plot(x, y, 'o', color=color, markersize=12, zorder=3, alpha=0.5)
            ax.plot(x, y, '*', color='white', markersize=6, zorder=4)

        ax.text(x, y + 0.35, sys_name, ha='center', fontsize=9, fontweight='bold')
        ax.text(x, y - 0.35, f'{security:+.1f}', ha='center', fontsize=8, color=color)

    # Route stats box
    stats_text = f"""ROUTE STATISTICS
━━━━━━━━━━━━━━━
Origin: Jita
Destination: Sobaseki
━━━━━━━━━━━━━━━
Total Jumps: {len(route)-1}
Total Distance: 2.02 LY
Est. Time: 2 minutes
━━━━━━━━━━━━━━━
Security: Mixed
Avoidance: None"""

    ax.text(-2.8, -2.3, stats_text, fontsize=8, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

    plt.tight_layout()
    plt.savefig('/home/user/evemap/starmap_visualization.png', dpi=150, bbox_inches='tight')
    print("✓ Starmap visualization saved: starmap_visualization.png")
    return fig

# ============================================================
# 2. APP LAYOUT VISUALIZATION
# ============================================================

def visualize_app_layouts():
    """Generate visual representations of the app screen layouts"""

    fig = plt.figure(figsize=(16, 12))

    # Create grid for 4 screens
    screens = [
        ('Map Search', 0, 0),
        ('Route Planner', 0, 1),
        ('Capital Planner', 1, 0),
        ('Settings', 1, 1)
    ]

    for screen_name, row, col in screens:
        ax = plt.subplot(2, 2, row * 2 + col + 1)

        # Phone frame
        phone_width = 1
        phone_height = 2
        phone = FancyBboxPatch((-phone_width/2, -phone_height/2), phone_width, phone_height,
                              boxstyle="round,pad=0.05", linewidth=3,
                              edgecolor='black', facecolor='white', zorder=1)
        ax.add_patch(phone)

        # Status bar
        status_bar = patches.Rectangle((-phone_width/2, phone_height/2 - 0.08), phone_width, 0.08,
                                      facecolor='#333333', edgecolor='none')
        ax.add_patch(status_bar)
        ax.text(-0.45, phone_height/2 - 0.04, '9:41', fontsize=6, color='white', fontweight='bold')

        # App header
        header = patches.Rectangle((-phone_width/2, phone_height/2 - 0.18), phone_width, 0.1,
                                  facecolor='#2196F3', edgecolor='none')
        ax.add_patch(header)
        ax.text(0, phone_height/2 - 0.13, screen_name, fontsize=8, color='white',
                fontweight='bold', ha='center')

        # Screen content based on type
        if screen_name == 'Map Search':
            # Search bar
            search = patches.Rectangle((-0.35, phone_height/2 - 0.35), 0.7, 0.08,
                                      facecolor='#E0E0E0', edgecolor='#999999')
            ax.add_patch(search)
            ax.text(-0.3, phone_height/2 - 0.31, '🔍 Search Systems', fontsize=6)

            # System cards
            for i, (sys, sec_color) in enumerate([('Jita', '#00FF00'), ('Perimeter', '#00FF00'),
                                                   ('Urlen', '#FFAA00')]):
                y_pos = phone_height/2 - 0.45 - i * 0.25
                card = patches.Rectangle((-0.35, y_pos - 0.1), 0.7, 0.15,
                                        facecolor='#F5F5F5', edgecolor='#CCCCCC', linewidth=1)
                ax.add_patch(card)
                ax.text(-0.3, y_pos - 0.02, f'⭐ {sys}', fontsize=6, fontweight='bold')
                ax.text(-0.3, y_pos - 0.08, f'ID: 3000{1000+i}', fontsize=5)

        elif screen_name == 'Route Planner':
            # Input fields
            fields = ['Origin: 30000142', 'Destination: 30000144']
            for i, field in enumerate(fields):
                y_pos = phone_height/2 - 0.35 - i * 0.15
                input_box = patches.Rectangle((-0.35, y_pos - 0.05), 0.7, 0.08,
                                             facecolor='white', edgecolor='#999999', linewidth=1)
                ax.add_patch(input_box)
                ax.text(-0.3, y_pos - 0.01, field, fontsize=5)

            # Button
            button = patches.Rectangle((-0.35, phone_height/2 - 0.65), 0.7, 0.1,
                                      facecolor='#4CAF50', edgecolor='none')
            ax.add_patch(button)
            ax.text(0, phone_height/2 - 0.6, 'PLAN ROUTE', fontsize=6, color='white',
                   fontweight='bold', ha='center')

            # Result
            result = patches.Rectangle((-0.35, phone_height/2 - 1.15), 0.7, 0.35,
                                      facecolor='#E8F5E9', edgecolor='#4CAF50', linewidth=1)
            ax.add_patch(result)
            ax.text(-0.3, phone_height/2 - 0.85, 'Route Found!', fontsize=6, fontweight='bold', color='#2E7D32')
            ax.text(-0.3, phone_height/2 - 0.95, 'Jumps: 4  |  Distance: 0.04 LY', fontsize=5)
            ax.text(-0.3, phone_height/2 - 1.05, 'Time: ~4 minutes', fontsize=5)

        elif screen_name == 'Capital Planner':
            # Ship selector
            ships = ['Nyx', 'Hel', 'Moros']
            for i, ship in enumerate(ships):
                y_pos = phone_height/2 - 0.35 - i * 0.1
                if i == 0:
                    color = '#BBDEFB'
                    border = '#2196F3'
                else:
                    color = 'white'
                    border = '#CCCCCC'
                ship_btn = patches.Rectangle((-0.35, y_pos - 0.05), 0.7, 0.08,
                                            facecolor=color, edgecolor=border, linewidth=1)
                ax.add_patch(ship_btn)
                ax.text(-0.3, y_pos - 0.01, ship, fontsize=5)

            # Inputs
            ax.text(-0.35, phone_height/2 - 0.7, 'Origin ID: 30000142', fontsize=5)
            ax.text(-0.35, phone_height/2 - 0.8, 'Dest ID: 30000144', fontsize=5)
            ax.text(-0.35, phone_height/2 - 0.9, 'Skills: 5/5', fontsize=5)

            # Button
            button = patches.Rectangle((-0.35, phone_height/2 - 1.1), 0.7, 0.08,
                                      facecolor='#FF9800', edgecolor='none')
            ax.add_patch(button)
            ax.text(0, phone_height/2 - 1.06, 'PLAN JUMP', fontsize=6, color='white',
                   fontweight='bold', ha='center')

        elif screen_name == 'Settings':
            # API URL input
            ax.text(-0.35, phone_height/2 - 0.3, 'API URL:', fontsize=6, fontweight='bold')
            api_input = patches.Rectangle((-0.35, phone_height/2 - 0.5), 0.7, 0.12,
                                         facecolor='white', edgecolor='#999999', linewidth=1)
            ax.add_patch(api_input)
            ax.text(-0.3, phone_height/2 - 0.42, 'https://evemap-api...', fontsize=4)

            # Status
            ax.text(-0.35, phone_height/2 - 0.65, 'Status: ✅ Connected', fontsize=6, color='#2E7D32')

            # About section
            ax.text(-0.35, phone_height/2 - 0.85, 'Version: 1.0.0', fontsize=5)
            ax.text(-0.35, phone_height/2 - 0.95, 'Powered by ESI API', fontsize=5, style='italic')
            ax.text(-0.35, phone_height/2 - 1.05, '[Docs] [Privacy]', fontsize=5, color='#2196F3')

        # Tab bar
        tab_bar = patches.Rectangle((-phone_width/2, -phone_height/2), phone_width, 0.15,
                                   facecolor='white', edgecolor='#CCCCCC', linewidth=1, zorder=2)
        ax.add_patch(tab_bar)

        tabs = ['🗺️', '🛣️', '🚀', '⚙️']
        for i, tab in enumerate(tabs):
            x_pos = -0.35 + i * 0.25
            ax.text(x_pos, -phone_height/2 + 0.075, tab, fontsize=10, ha='center', va='center')

        ax.set_xlim(-0.8, 0.8)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')

    plt.suptitle('EVE Map - App Screen Layouts (iOS & Android)',
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('/home/user/evemap/app_layouts.png', dpi=150, bbox_inches='tight')
    print("✓ App layouts visualization saved: app_layouts.png")
    return fig

# ============================================================
# 3. DESIGN SYSTEM
# ============================================================

def visualize_design_system():
    """Visualize the design system and UI components"""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Color palette
    ax = axes[0, 0]
    ax.set_title('Color Palette', fontsize=12, fontweight='bold')
    colors = {
        'High-Sec': '#00FF00',
        'Low-Sec': '#FFAA00',
        'Null-Sec': '#FF0000',
        'Primary': '#2196F3',
        'Success': '#4CAF50',
        'Warning': '#FF9800',
        'Background': '#F5F5F5',
        'Text': '#212121'
    }

    y_pos = 0.9
    for name, color in colors.items():
        rect = patches.Rectangle((0.1, y_pos - 0.08), 0.15, 0.08,
                                facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(0.3, y_pos - 0.04, f'{name}: {color}', fontsize=10, va='center')
        y_pos -= 0.12

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Typography
    ax = axes[0, 1]
    ax.set_title('Typography', fontsize=12, fontweight='bold')
    ax.text(0.05, 0.85, 'Headline Large', fontsize=16, fontweight='bold')
    ax.text(0.05, 0.75, '(32px, Bold)', fontsize=8, color='#666666')

    ax.text(0.05, 0.65, 'Title Medium', fontsize=13, fontweight='bold')
    ax.text(0.05, 0.55, '(16px, Bold)', fontsize=8, color='#666666')

    ax.text(0.05, 0.45, 'Body Medium', fontsize=11)
    ax.text(0.05, 0.35, '(14px, Regular)', fontsize=8, color='#666666')

    ax.text(0.05, 0.25, 'Label Small', fontsize=9)
    ax.text(0.05, 0.15, '(12px, Medium)', fontsize=8, color='#666666')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Components
    ax = axes[1, 0]
    ax.set_title('Components - Buttons & Cards', fontsize=12, fontweight='bold')

    # Button styles
    y = 0.85

    # Filled button
    btn1 = patches.Rectangle((0.05, y - 0.08), 0.4, 0.08,
                             facecolor='#2196F3', edgecolor='none')
    ax.add_patch(btn1)
    ax.text(0.25, y - 0.04, 'Filled Button', fontsize=10, color='white',
           ha='center', va='center', fontweight='bold')
    ax.text(0.5, y - 0.04, 'Primary action', fontsize=9, va='center')

    y -= 0.15

    # Outlined button
    btn2 = patches.Rectangle((0.05, y - 0.08), 0.4, 0.08,
                             facecolor='white', edgecolor='#2196F3', linewidth=2)
    ax.add_patch(btn2)
    ax.text(0.25, y - 0.04, 'Outlined Button', fontsize=10, color='#2196F3',
           ha='center', va='center', fontweight='bold')
    ax.text(0.5, y - 0.04, 'Secondary action', fontsize=9, va='center')

    y -= 0.15

    # Text field
    ax.text(0.05, y, 'Text Input:', fontsize=10, fontweight='bold')
    field = patches.Rectangle((0.05, y - 0.1), 0.4, 0.08,
                             facecolor='#F5F5F5', edgecolor='#999999', linewidth=1)
    ax.add_patch(field)
    ax.text(0.08, y - 0.06, 'Enter text...', fontsize=9, color='#999999')

    y -= 0.2

    # Card
    card = patches.Rectangle((0.05, y - 0.15), 0.9, 0.15,
                            facecolor='#FAFAFA', edgecolor='#EEEEEE', linewidth=1)
    ax.add_patch(card)
    ax.text(0.08, y - 0.03, 'Card Title', fontsize=10, fontweight='bold')
    ax.text(0.08, y - 0.08, 'Card content goes here', fontsize=9, color='#666666')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Spacing & Layout
    ax = axes[1, 1]
    ax.set_title('Spacing & Layout Grid', fontsize=12, fontweight='bold')

    # Grid
    for i in range(0, 10):
        ax.axvline(i * 0.1, color='#EEEEEE', linewidth=0.5, alpha=0.5)
        ax.axhline(i * 0.1, color='#EEEEEE', linewidth=0.5, alpha=0.5)

    # Spacing example
    ax.text(0.05, 0.9, 'Padding Examples:', fontsize=11, fontweight='bold')

    spacing_examples = [
        ('8px (xs)', 0.08, 0.8),
        ('16px (sm)', 0.16, 0.65),
        ('24px (md)', 0.24, 0.45),
        ('32px (lg)', 0.32, 0.15),
    ]

    for label, width, y_pos in spacing_examples:
        rect = patches.Rectangle((0.05, y_pos), width, 0.08,
                                facecolor='#2196F3', alpha=0.5, edgecolor='#2196F3')
        ax.add_patch(rect)
        ax.text(0.52, y_pos + 0.04, label, fontsize=9, va='center')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.suptitle('EVE Map - Design System', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/user/evemap/design_system.png', dpi=150, bbox_inches='tight')
    print("✓ Design system visualization saved: design_system.png")
    return fig

# ============================================================
# 4. DATA FLOW VISUALIZATION
# ============================================================

def visualize_data_flow():
    """Visualize app data flow and API interactions"""

    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    # Title
    ax.text(5, 9.5, 'EVE Map - Data Flow Architecture', fontsize=14, fontweight='bold', ha='center')

    # UI Layer
    ui_layer = patches.FancyBboxPatch((0.5, 7), 2, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='#E3F2FD', edgecolor='#2196F3', linewidth=2)
    ax.add_patch(ui_layer)
    ax.text(1.5, 7.75, 'iOS/Android\nUI Layer', fontsize=10, ha='center', va='center', fontweight='bold')

    # State Management
    state_layer = patches.FancyBboxPatch((3.5, 7), 2, 1.5, boxstyle="round,pad=0.1",
                                        facecolor='#F3E5F5', edgecolor='#9C27B0', linewidth=2)
    ax.add_patch(state_layer)
    ax.text(4.5, 7.75, 'State\nManagement', fontsize=10, ha='center', va='center', fontweight='bold')

    # API Client
    api_layer = patches.FancyBboxPatch((6.5, 7), 2, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='#FFF3E0', edgecolor='#FF9800', linewidth=2)
    ax.add_patch(api_layer)
    ax.text(7.5, 7.75, 'API Client\n(Retrofit/URLSession)', fontsize=10, ha='center', va='center', fontweight='bold')

    # Backend
    backend_layer = patches.FancyBboxPatch((3, 4), 4, 2, boxstyle="round,pad=0.1",
                                          facecolor='#E8F5E9', edgecolor='#4CAF50', linewidth=2)
    ax.add_patch(backend_layer)
    ax.text(5, 5.5, 'FastAPI Backend', fontsize=11, ha='center', fontweight='bold')
    ax.text(5, 5, '29 Endpoints', fontsize=9, ha='center')
    ax.text(5, 4.5, '(Phase 1-3: Search, Routes, Capital)', fontsize=8, ha='center')

    # Database
    db_layer = patches.FancyBboxPatch((0.5, 1), 4, 1.5, boxstyle="round,pad=0.1",
                                     facecolor='#FCE4EC', edgecolor='#E91E63', linewidth=2)
    ax.add_patch(db_layer)
    ax.text(2.5, 1.75, 'SQLite/PostgreSQL', fontsize=10, ha='center', va='center', fontweight='bold')
    ax.text(2.5, 1.25, '8000+ Systems, Graph Data', fontsize=9, ha='center')

    # ESI API
    esi_layer = patches.FancyBboxPatch((5.5, 1), 4, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='#F1F8E9', edgecolor='#689F38', linewidth=2)
    ax.add_patch(esi_layer)
    ax.text(7.5, 1.75, 'EVE Online ESI API', fontsize=10, ha='center', va='center', fontweight='bold')
    ax.text(7.5, 1.25, 'Live Activity, Kills, Intel', fontsize=9, ha='center')

    # Arrows - Data Flow
    # UI → State
    arrow1 = FancyArrowPatch((2.5, 7.5), (3.5, 7.5),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#2196F3')
    ax.add_patch(arrow1)

    # State → API Client
    arrow2 = FancyArrowPatch((5.5, 7.5), (6.5, 7.5),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#9C27B0')
    ax.add_patch(arrow2)

    # API Client → Backend
    arrow3 = FancyArrowPatch((7.5, 7), (5.5, 6),
                            arrowstyle='<->', mutation_scale=20, linewidth=2, color='#FF9800')
    ax.add_patch(arrow3)
    ax.text(6.8, 6.5, 'HTTP\nJSON', fontsize=8, ha='center')

    # Backend → Database
    arrow4 = FancyArrowPatch((4, 4), (3, 2.5),
                            arrowstyle='<->', mutation_scale=20, linewidth=2, color='#4CAF50')
    ax.add_patch(arrow4)
    ax.text(2.5, 3.25, 'SQL\nORM', fontsize=8, ha='center')

    # Backend → ESI
    arrow5 = FancyArrowPatch((6, 4), (7, 2.5),
                            arrowstyle='<->', mutation_scale=20, linewidth=2, color='#689F38')
    ax.add_patch(arrow5)
    ax.text(7.5, 3.25, 'HTTP\nCached', fontsize=8, ha='center')

    # Caching layer
    cache_box = patches.Rectangle((2, 0.1), 6, 0.5,
                                 facecolor='#FFEBEE', edgecolor='#F44336', linewidth=1, linestyle='--')
    ax.add_patch(cache_box)
    ax.text(5, 0.35, 'Caching Layer: Response Cache (10min), Graph Cache (offline), User Preferences',
           fontsize=8, ha='center', style='italic')

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 10)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/home/user/evemap/data_flow.png', dpi=150, bbox_inches='tight')
    print("✓ Data flow visualization saved: data_flow.png")
    return fig

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("Generating EVE Map Visualizations...")
    print()

    visualize_starmap()
    visualize_app_layouts()
    visualize_design_system()
    visualize_data_flow()

    print()
    print("=" * 60)
    print("✓ All visualizations generated successfully!")
    print("=" * 60)
    print()
    print("Generated files:")
    print("  1. starmap_visualization.png - Full/route map views")
    print("  2. app_layouts.png - Screen mockups for all 4 tabs")
    print("  3. design_system.png - Colors, typography, components")
    print("  4. data_flow.png - Architecture and data flow")
    print()
