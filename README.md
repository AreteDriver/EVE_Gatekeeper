# EVE Gatekeeper

**Comprehensive EVE Online navigation, routing, and intel visualization platform.**

A unified toolkit combining real-time map visualization, risk-aware routing, capital jump planning, and universe data management. Built with FastAPI backend and matplotlib visualization.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Features

### Starmap & Navigation
- **2D Universe Visualization**: Interactive map with zoom, pan, and filtering
- **Risk-Aware Routing**: Dijkstra pathfinding with safety profiles (shortest/safer/paranoid)
- **Capital Jump Planner**: Jump range visualization and multi-leg route planning
- **Security Overlays**: High-sec, low-sec, null-sec, wormhole filtering

### Live Data Integration
- **ESI API Client**: Full EVE Swagger Interface integration with caching
- **zKillboard Integration**: Real-time kill data for risk assessment
- **Sovereignty Heatmaps**: Territory control visualization
- **Activity Metrics**: Kills, jumps, and player activity overlays

### Backend Services
- **FastAPI REST API**: Full OpenAPI documentation
- **SQLite Universe Database**: Offline-first with SDE ingestion
- **LRU Caching**: Optimized performance for repeated queries
- **WebSocket Support**: Real-time updates (planned)

## Quick Start

### Installation

```bash
git clone https://github.com/AreteDriver/EVE_Gatekeeper.git
cd EVE_Gatekeeper

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Initialize Universe Data

```bash
# Ingest universe data from ESI
python -m backend.starmap.ingest_sde --reset
```

### Run the Server

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Project Structure

```
EVE_Gatekeeper/
├── backend/
│   ├── app/                    # FastAPI application
│   │   ├── services/           # Risk engine, routing, data loader
│   │   └── main.py
│   └── starmap/                # Universe navigation
│       ├── esi/                # ESI client with caching
│       ├── graph/              # Pathfinding algorithms
│       ├── sde/                # SQLite schema and models
│       ├── jump_planner/       # Capital ship routing
│       ├── ingest_sde.py       # Universe data ingestion
│       └── refresh_cache.py    # Live data refresh
├── src/evemap/                 # Map visualization library
│   ├── esi_client.py
│   ├── map.py
│   └── models.py
├── examples/                   # Usage examples
└── docs/
```

## API Endpoints

### Systems
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/systems/` | GET | List all systems |
| `/systems/{name}/risk` | GET | Get risk report |
| `/systems/{name}/neighbors` | GET | Get connected systems |

### Routing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/map/route` | GET | Calculate route with risk weighting |
| `/api/v1/route` | POST | Advanced route calculation |

### Jump Planning
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jump/range` | POST | Get systems in jump range |
| `/api/v1/jump/route` | POST | Plan capital jump route |

### Heatmaps
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/map/config` | GET | Get map with risk scores |
| `/api/v1/heatmap` | POST | Get activity heatmap |

## Capital Ships Supported

- **Dreadnoughts**: Revelation, Moros, Naglfar, Phoenix
- **Carriers**: Archon, Thanatos, Nidhoggur, Chimera
- **Force Auxiliaries**: Apostle, Ninazu, Lif, Minokawa
- **Supercarriers**: Aeon, Nyx, Hel, Wyvern
- **Titans**: Avatar, Erebus, Ragnarok, Leviathan
- **Jump Freighters**: Ark, Anshar, Nomad, Rhea
- **Black Ops**: Sin, Widow, Panther, Redeemer

## Route Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| `shortest` | Minimum jumps | Speed over safety |
| `safer` | Balanced risk/distance | General travel |
| `paranoid` | Maximum safety | Expensive cargo |

## Development

```bash
# Run tests
pytest

# Type checking
mypy backend/

# Linting
ruff check .
```

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- **CCP Games** for EVE Online and ESI API
- **zKillboard** for kill data
- **EVE SDE** for universe data

---

**Built for the EVE Online community** | [Report Issues](https://github.com/AreteDriver/EVE_Gatekeeper/issues)
