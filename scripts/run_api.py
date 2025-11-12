#!/usr/bin/env python3
"""Start the FastAPI REST server."""

import sys
sys.path.insert(0, '/home/user/evemap/src')

import uvicorn
from evemap import create_app, DatabaseManager


if __name__ == "__main__":
    print("=" * 70)
    print("EVE MAP API SERVER")
    print("=" * 70)
    print()

    # Create database manager
    db = DatabaseManager(db_path="data/universe.db")

    # Create FastAPI app
    app = create_app(db)

    print("Starting API server on http://0.0.0.0:8000")
    print()
    print("API Documentation available at:")
    print("  http://localhost:8000/docs (Swagger UI)")
    print("  http://localhost:8000/redoc (ReDoc)")
    print()
    print("Press Ctrl+C to stop server")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
