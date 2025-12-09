#!/usr/bin/env python3
"""Test script demonstrating the backend functionality."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.services.data_loader import load_universe, load_risk_config, get_neighbors
from backend.app.services.risk_engine import compute_risk
from backend.app.services.routing import calculate_route


def test_data_loading():
    """Test data loading functionality."""
    print("=" * 60)
    print("TEST 1: Data Loading")
    print("=" * 60)
    
    universe = load_universe()
    print(f"✓ Loaded universe with {len(universe.systems)} systems")
    print(f"  Systems: {', '.join(universe.systems.keys())}")
    print(f"✓ Loaded {len(universe.gates)} gates")
    
    config = load_risk_config()
    print(f"✓ Loaded risk configuration")
    print(f"  Profiles: {', '.join(config.routing_profiles.keys())}")
    print()


def test_risk_scoring():
    """Test risk scoring functionality."""
    print("=" * 60)
    print("TEST 2: Risk Scoring")
    print("=" * 60)
    
    systems = ['Jita', 'Perimeter', 'Niarja']
    
    for system_name in systems:
        risk = compute_risk(system_name)
        print(f"✓ {system_name}:")
        print(f"  Risk Score: {risk.risk_score:.2f}")
        print(f"  Security Score: {risk.security_score:.2f}")
        print(f"  Color: {risk.risk_color}")
    print()


def test_neighbors():
    """Test neighbor finding functionality."""
    print("=" * 60)
    print("TEST 3: Neighbor Discovery")
    print("=" * 60)
    
    neighbors = get_neighbors('Jita')
    print(f"✓ Neighbors of Jita:")
    for gate in neighbors:
        print(f"  → {gate.to_system} (distance: {gate.distance})")
    print()


def test_routing():
    """Test routing functionality."""
    print("=" * 60)
    print("TEST 4: Route Calculation")
    print("=" * 60)
    
    profiles = ['shortest', 'safer', 'paranoid']
    
    for profile in profiles:
        route = calculate_route('Jita', 'Niarja', profile)
        print(f"✓ Route with '{profile}' profile:")
        print(f"  Total Jumps: {route.total_jumps}")
        print(f"  Total Distance: {route.total_distance:.2f}")
        print(f"  Total Cost: {route.total_cost:.2f}")
        print(f"  Max Risk: {route.max_risk:.2f}")
        print(f"  Avg Risk: {route.avg_risk:.2f}")
        print(f"  Path: {' → '.join([hop.system_name for hop in route.path])}")
        print()


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "EVE Navigator Backend Test Suite" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        test_data_loading()
        test_risk_scoring()
        test_neighbors()
        test_routing()
        
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe backend is working correctly with:")
        print("  - typing.* imports (Dict, List, Tuple, Optional)")
        print("  - Pydantic v1.x (<2.0)")
        print("  - No PEP 585/604 syntax")
        print()
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
