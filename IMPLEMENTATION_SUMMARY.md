# Implementation Summary: Revert PEP 585/604 Typing to typing.* and Pin Pydantic v1

## Overview

This PR creates a complete FastAPI backend for EVE Online map visualization that explicitly uses **old-style typing annotations** (`typing.Dict`, `typing.List`, etc.) instead of PEP 585/604 syntax to ensure compatibility with:
- Python versions < 3.10
- Pydantic v1.x (avoiding breaking changes in v2)

## Files Created/Modified

### Models (backend/app/models/)

1. **risk.py**
   - `RiskConfig` with fields using `Dict[str, float]`, `Dict[str, Dict[str, float]]`
   - Import: `from typing import Dict`

2. **route.py**
   - `RouteResponse` with `path: List[RouteHop]`
   - Import: `from typing import List`

3. **system.py**
   - `Universe` with `systems: Dict[str, System]` and `gates: List[Gate]`
   - Import: `from typing import Dict, List`

### Services (backend/app/services/)

4. **data_loader.py**
   - `def get_neighbors(system_name: str) -> List[Gate]:`
   - Import: `from typing import List`

5. **routing.py**
   - `def _build_graph() -> Dict[str, Dict[str, float]]:`
   - `graph: Dict[str, Dict[str, float]] = {...}`
   - `def _dijkstra(...) -> Tuple[List[str], float]:`
   - `dist: Dict[str, float] = {...}`
   - `prev: Dict[str, Optional[str]] = {...}`
   - `path: List[str] = []`
   - `hops: List[RouteHop] = []`
   - Import: `from typing import Dict, List, Tuple, Optional`

6. **risk_engine.py**
   - Risk calculation service

7. **zkill_client.py**
   - Stub implementation for zKillboard integration

### API (backend/app/api/)

8. **routes_systems.py**
   - `/systems/` - List all systems
   - `/systems/{name}/risk` - Get risk report
   - `/systems/{name}/neighbors` - Get neighbors

9. **routes_map.py**
   - `/map/config` - Get complete map configuration
   - `/map/route` - Calculate routes with risk weighting

### Configuration

10. **requirements.txt**
    - `pydantic>=1.10,<2.0` ✓ Pinned to v1
    - `fastapi>=0.109.1,<0.110.0` ✓ Security patched
    - No pydantic-settings (v2 only)

11. **data/universe.json**
    - Sample systems: Jita, Perimeter, Niarja

12. **data/risk_config.json**
    - Risk weights, routing profiles, color scales

## Verification

### Automated Tests

- **verify.py**: Checks all typing imports and annotations
- **test_backend.py**: Comprehensive functional tests

### Security

- ✓ CodeQL: 0 alerts
- ✓ GitHub Advisory DB: No vulnerabilities  
- ✓ FastAPI updated to 0.109.2 (patched version)

### Installed Versions

```
fastapi           0.109.2
pydantic          1.10.24  ← v1.x as required
uvicorn           0.23.2
httpx             0.23.3
```

## Testing

Run the test suite:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
python test_backend.py

# Run verification
python verify.py
```

## API Usage Examples

```bash
# Start server
uvicorn app.main:app --reload

# List systems
curl http://localhost:8000/systems/

# Get risk report
curl http://localhost:8000/systems/Jita/risk

# Calculate route
curl "http://localhost:8000/map/route?from=Jita&to=Niarja&profile=safer"
```

## Key Differences from PEP 585/604

| Old Style (This PR) | PEP 585/604 | Compatibility |
|---------------------|-------------|---------------|
| `Dict[str, float]` | `dict[str, float]` | Python <3.10 ✓ |
| `List[RouteHop]` | `list[RouteHop]` | Python <3.10 ✓ |
| `Optional[str]` | `str \| None` | Python <3.10 ✓ |
| `Tuple[List[str], float]` | `tuple[list[str], float]` | Python <3.10 ✓ |

## Notes for Maintainer

- All type annotations verified to use `typing.*` imports
- No PEP 585/604 syntax found in codebase
- Pydantic v1 behaviors preserved
- CI/python matrix not changed in this PR
- Recommend testing with Python 3.9/3.10 to verify compatibility
- All tests passing with current implementation
