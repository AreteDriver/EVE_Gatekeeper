# EVE Navigator Backend

FastAPI backend for EVE Online map visualization with risk-aware routing.

## Features

- **Risk Scoring**: Configurable risk assessment based on security status and kill activity
- **Routing**: Dijkstra-based pathfinding with multiple profiles (shortest, safer, paranoid)
- **API Endpoints**: RESTful APIs for systems, risk reports, and route calculation
- **JSON Configuration**: Data-driven universe and risk configuration

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Systems
- `GET /systems/` - List all systems
- `GET /systems/{name}/risk` - Get risk report for a system
- `GET /systems/{name}/neighbors` - Get neighboring systems

### Map
- `GET /map/config` - Get complete map configuration with risk scores
- `GET /map/route?from={}&to={}&profile={}` - Calculate route between systems

## Example Requests

```bash
# Get all systems
curl http://localhost:8000/systems/

# Get risk report for Jita
curl http://localhost:8000/systems/Jita/risk

# Calculate route
curl "http://localhost:8000/map/route?from=Jita&to=Niarja&profile=safer"
```

## Configuration

- `backend/app/data/universe.json` - System and gate data
- `backend/app/data/risk_config.json` - Risk weights and routing profiles

## Type Annotations

This codebase uses typing.* imports (Dict, List, etc.) for compatibility with:
- Python <3.10 runtimes
- Pydantic v1.x (pinned to <2.0)

## Dependencies

- FastAPI 0.109.x (patched for security)
- Uvicorn 0.15-0.23.x
- Pydantic 1.10.x (v1, not v2)
- httpx 0.23.x
