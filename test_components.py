"""
Test script to verify the API and mobile app components work correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from evemap.models import System, JumpConnection, SecurityStatus
from evemap.api import initialize_api
from evemap.zkillboard import ZKillboardClient


def test_models():
    """Test data models."""
    print("Testing data models...")
    
    # Create test systems
    system1 = System(
        system_id=30000142,
        name="Jita",
        region_id=10000002,
        constellation_id=20000020,
        security_status=0.95
    )
    
    system2 = System(
        system_id=30001161,
        name="Perimeter",
        region_id=10000002,
        constellation_id=20000020,
        security_status=0.88
    )
    
    # Test security classification
    assert system1.security_class == SecurityStatus.HIGH_SEC
    assert system2.security_class == SecurityStatus.HIGH_SEC
    
    # Create connection
    conn = JumpConnection(30000142, 30001161)
    assert conn.source_system_id == 30000142
    assert conn.target_system_id == 30001161
    
    print("✓ Data models working correctly")
    return system1, system2, conn


def test_api_initialization():
    """Test API initialization."""
    print("\nTesting API initialization...")
    
    # Create test data
    systems = {
        30000142: System(
            system_id=30000142,
            name="Jita",
            region_id=10000002,
            constellation_id=20000020,
            security_status=0.95
        ),
        30001161: System(
            system_id=30001161,
            name="Perimeter",
            region_id=10000002,
            constellation_id=20000020,
            security_status=0.88
        ),
        30002768: System(
            system_id=30002768,
            name="Sobaseki",
            region_id=10000002,
            constellation_id=20000020,
            security_status=0.75
        ),
    }
    
    connections = [
        JumpConnection(30000142, 30001161),
        JumpConnection(30001161, 30002768),
    ]
    
    # Initialize API
    initialize_api(systems, connections)
    
    print("✓ API initialized successfully")
    print(f"  - {len(systems)} systems loaded")
    print(f"  - {len(connections)} connections loaded")


def test_zkillboard_client():
    """Test zkillboard client."""
    print("\nTesting zkillboard client...")
    
    client = ZKillboardClient()
    print("✓ zkillboard client created")
    print("  Note: Actual API calls are rate-limited and require internet")


def main():
    """Run all tests."""
    print("=" * 60)
    print("EVE MAP - COMPONENT TESTS")
    print("=" * 60)
    print()
    
    try:
        # Test models
        test_models()
        
        # Test API
        test_api_initialization()
        
        # Test zkillboard
        test_zkillboard_client()
        
        print()
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the API server: python run_api_server.py")
        print("2. Start the mobile app: cd mobile-app && npm start")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED ✗")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
