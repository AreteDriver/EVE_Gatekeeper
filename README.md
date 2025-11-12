# EVE Map - 2D Starmap for EVE Online

A production-ready mobile app backend for exploring EVE Online's New Eden with live activity heatmaps, route planning, and comprehensive intelligence layers. Designed for iOS (Swift + SwiftUI) with REST API backend powered by FastAPI and Python.

**Status:** Live foundation + Phase 2 (heatmaps) ready. Building for Apple App Store.

## Features

### ✅ Implemented

**Core Map (Phase 1.5)**
- Static universe data: regions, constellations, 8000+ systems
- Jump gate network with precomputed shortest paths
- Dijkstra route planning with avoidance options (lowsec, specific systems/regions)
- Hub detection (most connected systems) and bottleneck analysis
- Offline-first graph export for mobile

**REST API (Phase 1.5 + 2)**
- System search and details
- Region queries and listings
- Route planning with constraints
- Universe statistics and analysis
- Health checks and API documentation

**Live Heatmaps (Phase 2)**
- Activity heatmap: kills and jumps per system (cached 10 min)
- Incursion data with affected systems
- Sovereignty map and active campaigns
- Combined intel layers endpoint

**iOS Client**
- SwiftUI example code for all endpoints
- System search with autocomplete
- Route visualization
- Activity heatmap overlay
- Offline graph consumption

### 🔄 Next (Phases 3-5)

- Capital jump planner (dogma-based range calculation)
- Multi-leg jump chain planning
- ESI OAuth for personal character data
- Location tracking and breadcrumb trails
- Asset overlays and standings-based coloring
- Corporation features: project routes, role-aware visibility
- Mining and exploration layers

## Quick Start

### Prerequisites

- Python 3.11+
- pip
- (iOS) Xcode 14+

### Installation

```bash
# Clone repository
git clone https://github.com/YourUsername/evemap.git
cd evemap

# Install dependencies
pip install -r requirements.txt

# Initialize universe (first run: ~10-15 min)
python scripts/init_universe.py

# Start API server
python scripts/run_api.py
```

Visit **http://localhost:8000/docs** for interactive API documentation.

### Docker

```bash
# Build and run with Docker Compose
docker-compose up

# Build custom image
docker build -t evemap:latest .
docker run -p 8000:8000 -v evemap_data:/app/data evemap:latest
```

## API Quick Reference

### System Data

```bash
# Search systems
curl http://localhost:8000/systems/search?q=jita

# Get system details
curl http://localhost:8000/systems/30000142

# Get adjacent systems
curl http://localhost:8000/systems/30000142/neighbors
```

### Route Planning

```bash
curl -X POST http://localhost:8000/routes/plan \
  -H "Content-Type: application/json" \
  -d '{
    "origin": 30000142,
    "destination": 30000144,
    "avoid_lowsec": false
  }'
```

### Live Intelligence

```bash
# Activity heatmap
curl http://localhost:8000/intel/activity

# All intel (combined)
curl http://localhost:8000/intel/all

# Incursions
curl http://localhost:8000/intel/incursions
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete API documentation.

## Project Structure

```
evemap/
├── src/evemap/            # Main package
│   ├── api.py            # FastAPI server
│   ├── database.py       # SQLAlchemy ORM
│   ├── graph_engine.py   # Routing & analysis
│   ├── heatmap.py        # ESI heatmaps
│   ├── sde_loader.py     # Data loading
│   └── ...
├── scripts/
│   ├── init_universe.py  # Setup database
│   └── run_api.py        # Start server
├── examples/
│   ├── test_foundation.py         # Tests
│   └── ios_client_example.swift   # iOS code
├── data/                  # Databases & cache
├── Dockerfile            # Container
└── DEPLOYMENT.md         # Production guide
```

## iOS Development

Copy `examples/ios_client_example.swift` to your Xcode project and update the base URL:

```swift
private let baseURL = URL(string: "https://your-api-server.com")!
```

Then use the `EVEMapClient` in your SwiftUI views:

```swift
@StateObject private var client = EVEMapClient()

func searchSystems() {
    client.searchSystems(query: "Jita")
        .receive(on: DispatchQueue.main)
        .sink { results in
            self.systems = results
        }
        .store(in: &cancellables)
}
```

## Deployment

### Local Development

```bash
python scripts/init_universe.py
python scripts/run_api.py
```

### Production (Docker)

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Cloud deployment (AWS, Heroku, DigitalOcean)
- PostgreSQL setup
- Security & SSL
- App Store submission
- Monitoring & logging

### Environment Variables

```
DATABASE_URL=sqlite:///data/universe.db
CACHE_DIR=data/api_cache
HEATMAP_CACHE_TTL=6
LOG_LEVEL=info
```

## Architecture

```
┌──────────────────────┐
│   iOS App (Swift)    │
│   - Map view         │
│   - Route planner    │
│   - Activity overlay │
└──────────┬───────────┘
           │ REST API (JSON)
┌──────────▼───────────┐
│   FastAPI Server     │
│   - /systems/*       │
│   - /routes/plan     │
│   - /intel/*         │
└──────────┬───────────┘
           │ SQLAlchemy ORM
┌──────────▼───────────┐
│  SQLite Database     │
│  - Systems (8000+)   │
│  - Stargates        │
│  - Cached data      │
└──────────┬───────────┘
           │ HTTP
┌──────────▼───────────┐
│   EVE Online ESI     │
│   - Universe data    │
│   - Activity feeds   │
└──────────────────────┘
```

## Performance

| Operation | Latency | Cache |
|-----------|---------|-------|
| System search | <50ms | 24h |
| Route planning | <50ms | Precomputed |
| Heatmap fetch | <500ms | 10min |
| Hub analysis | <100ms | 6h |

## Development

### Running Tests

```bash
python examples/test_foundation.py      # Integration tests
python examples/test_mock_data.py       # Mock data demo
```

### Using the Graph Engine

```python
from evemap import GraphEngine, DatabaseManager

db = DatabaseManager()
graph = GraphEngine(db)
graph.build_from_db()

# Find route
route = graph.shortest_path(30000142, 30000144)
# [30000142, 30001161, 30002768, 30002060, 30000144]

# Find hubs
hubs = graph.find_hubs(top_n=10)
```

## Contributing

We welcome contributions! Areas for help:

- [ ] Phase 3: Capital jump planner
- [ ] Phase 4: ESI OAuth integration
- [ ] Phase 5: Corporation features
- [ ] iOS app enhancements (maps, 3D)
- [ ] Android port (Kotlin)
- [ ] Performance optimization
- [ ] Documentation

## Roadmap

### Phase 3: Capital Jump Planner ⏳
- Dogma-based jump range calculation
- Multi-leg jump chains with refuel stops
- Fuel consumption estimates
- Ship configuration persistence

### Phase 4: OAuth & Personal Data ⏳
- ESI OAuth2 flow
- Character location tracking
- Asset overlays
- Standings-based coloring
- Breadcrumb trails

### Phase 5: Corporation Features ⏳
- Corporation Project routes
- Role-aware visibility
- Objective pins and collaboration
- Alliance-wide intel sharing

## Support

- **Questions:** GitHub Issues
- **API Docs:** http://localhost:8000/docs (live)
- **ESI Reference:** https://esi.eveonline.com/docs
- **Community:** /r/Eve, EVE Forums, Discord

## Credits

- CCP Games - EVE Online & ESI API
- FastAPI & SQLAlchemy teams
- EVE community for data & feedback

## Legal

- **ESI Terms:** Complies with [CCP ESI ToS](https://github.com/EvE-KILL/esi-docs)
- **App Store:** Requires Privacy Policy compliance
- **License:** MIT

---

**Build the future of EVE exploration. Ready to submit to the App Store?**

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment and App Store submission checklist.
