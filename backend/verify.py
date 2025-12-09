#!/usr/bin/env python3
"""Verification script to ensure all requirements are met."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def verify_typing_imports():
    """Verify that all files use typing.* imports, not PEP 585/604 syntax."""
    print("✓ Checking for old-style typing imports...")
    
    files_to_check = [
        'backend/app/models/risk.py',
        'backend/app/models/route.py',
        'backend/app/models/system.py',
        'backend/app/services/data_loader.py',
        'backend/app/services/routing.py',
    ]
    
    for filepath in files_to_check:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Check for typing imports
        if 'from typing import' not in content:
            print(f"  ✗ {filepath}: Missing typing imports")
            return False
            
        # Check for PEP 585 syntax
        if 'dict[' in content or 'list[' in content or 'tuple[' in content:
            print(f"  ✗ {filepath}: Contains PEP 585/604 syntax")
            return False
            
        print(f"  ✓ {filepath}: Uses typing.* imports")
    
    return True


def verify_pydantic_version():
    """Verify pydantic is pinned to v1."""
    print("\n✓ Checking Pydantic version constraint...")
    
    with open('backend/requirements.txt', 'r') as f:
        content = f.read()
    
    if 'pydantic>=1.10,<2.0' in content:
        print("  ✓ Pydantic correctly pinned to v1 (>=1.10,<2.0)")
        return True
    else:
        print("  ✗ Pydantic not correctly pinned")
        return False


def verify_specific_annotations():
    """Verify specific annotations as per problem statement."""
    print("\n✓ Checking specific type annotations...")
    
    checks = [
        ('backend/app/models/risk.py', 'Dict[str, float]', 'RiskConfig fields'),
        ('backend/app/models/route.py', 'List[RouteHop]', 'RouteResponse.path'),
        ('backend/app/models/system.py', 'Dict[str, System]', 'Universe.systems'),
        ('backend/app/models/system.py', 'List[Gate]', 'Universe.gates'),
        ('backend/app/services/data_loader.py', 'List[Gate]', 'get_neighbors return'),
        ('backend/app/services/routing.py', 'Dict[str, Dict[str, float]]', '_build_graph return'),
        ('backend/app/services/routing.py', 'Dict[str, Optional[str]]', 'prev variable'),
    ]
    
    for filepath, annotation, description in checks:
        with open(filepath, 'r') as f:
            content = f.read()
        
        if annotation in content:
            print(f"  ✓ {description}: {annotation}")
        else:
            print(f"  ✗ {description}: Missing {annotation}")
            return False
    
    return True


def verify_functionality():
    """Test basic functionality."""
    print("\n✓ Testing functionality...")
    
    from backend.app.services.data_loader import load_universe, load_risk_config
    from backend.app.services.risk_engine import compute_risk
    from backend.app.services.routing import calculate_route
    
    # Load data
    universe = load_universe()
    config = load_risk_config()
    print(f"  ✓ Loaded {len(universe.systems)} systems")
    print(f"  ✓ Loaded {len(config.routing_profiles)} routing profiles")
    
    # Test risk calculation
    risk = compute_risk('Jita')
    print(f"  ✓ Risk calculation: Jita score={risk.risk_score:.2f}, color={risk.risk_color}")
    
    # Test routing
    route = calculate_route('Jita', 'Niarja', 'safer')
    print(f"  ✓ Routing: {route.total_jumps} jumps from Jita to Niarja")
    
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("VERIFICATION: PEP 585/604 Reversion & Pydantic v1 Pinning")
    print("=" * 60)
    
    checks = [
        verify_typing_imports,
        verify_pydantic_version,
        verify_specific_annotations,
        verify_functionality,
    ]
    
    all_passed = True
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"\n✗ {check.__name__} failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
