#!/usr/bin/env python3
"""
EVE Map API Server

This script starts the REST API server that provides endpoints for the mobile app.
It fetches data from EVE's ESI API and serves it via RESTful endpoints.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from evemap import ESIClient, initialize_api, run_api


def main():
    """Main entry point for the API server."""
    parser = argparse.ArgumentParser(description='EVE Map API Server')
    parser.add_argument(
        '--region',
        type=int,
        default=10000002,
        help='Region ID to load (default: 10000002 - The Forge)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("EVE MAP API SERVER")
    print("=" * 60)
    print()
    print(f"Loading region {args.region}...")
    print()
    
    # Initialize ESI client and fetch data
    client = ESIClient()
    result = client.get_region_data(args.region)
    
    if not result:
        print("Failed to fetch region data. Check your internet connection.")
        sys.exit(1)
    
    systems, constellations, connections = result
    
    print()
    print(f"Successfully loaded:")
    print(f"  - {len(systems)} systems")
    print(f"  - {len(constellations)} constellations")
    print(f"  - {len(connections)} jump connections")
    print()
    
    # Initialize API with data
    initialize_api(systems, connections)
    
    print("=" * 60)
    print(f"Starting API server on {args.host}:{args.port}")
    print(f"Debug mode: {args.debug}")
    print("=" * 60)
    print()
    print("API Endpoints:")
    print(f"  - GET  http://{args.host}:{args.port}/health")
    print(f"  - GET  http://{args.host}:{args.port}/api/systems")
    print(f"  - GET  http://{args.host}:{args.port}/api/systems/<id>")
    print(f"  - GET  http://{args.host}:{args.port}/api/search")
    print(f"  - POST http://{args.host}:{args.port}/api/route")
    print(f"  - POST http://{args.host}:{args.port}/api/route/fuel-cost")
    print(f"  - GET  http://{args.host}:{args.port}/api/intel/zkillboard/<id>")
    print(f"  - GET  http://{args.host}:{args.port}/api/stats")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Start API server
    run_api(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
