# EVE Map - Deployment Guide

Complete guide for deploying the EVE Map API backend and building the iOS app.

## Quick Start (Development)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Universe Database

This loads EVE Static Data Export into SQLite and precomputes routes:

```bash
python scripts/init_universe.py
```

**Note:** First run will take ~10-15 minutes downloading SDE (regions, systems, stargates).
Subsequent runs use local cache.

### 3. Start API Server

```bash
python scripts/run_api.py
```

Server starts on `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Production Deployment

### Docker Deployment

#### 1. Build Docker Image

```bash
docker build -t evemap-api:latest .
```

#### 2. Run Container

```bash
docker run -d \
  -p 8000:8000 \
  -v evemap_data:/app/data \
  -e DATABASE_URL="sqlite:///data/universe.db" \
  --name evemap-api \
  evemap-api:latest
```

### Cloud Deployment (AWS ECS / Heroku / DigitalOcean)

The application is cloud-ready:

- **Stateless API server** - scales horizontally
- **SQLite database** - easily swap to PostgreSQL
- **S3-compatible cache** - for distributed deployments
- **Environment-based config** - via `.env` files

#### Environment Variables

```
DATABASE_URL=sqlite:///data/universe.db
CACHE_DIR=data/api_cache
HEATMAP_CACHE_TTL=6
LOG_LEVEL=info
```

### Database Options

#### SQLite (Default - Development/Small Scale)

```python
db = DatabaseManager(db_path="data/universe.db")
```

#### PostgreSQL (Production)

Update `database.py`:

```python
db_url = "postgresql://user:password@localhost/evemap"
engine = create_engine(db_url)
```

## iOS App Deployment

### Prerequisites

- Xcode 14+
- iOS 14.0+ deployment target
- Apple Developer Account for App Store

### Build Steps

1. **Create Xcode Project**

```bash
# Create new iOS App project in Xcode
# Choose SwiftUI
```

2. **Add API Client**

Copy `examples/ios_client_example.swift` into your Xcode project

3. **Configure Backend URL**

In `EVEMapClient`, update:

```swift
private let baseURL = URL(string: "https://your-api-domain.com")!
```

4. **Add Permissions** (Info.plist)

```xml
<key>NSLocalNetworkUsageDescription</key>
<string>EVE Map needs access to local network for offline database</string>
<key>NSBonjourServices</key>
<array>
  <string>_http._tcp</string>
</array>
```

5. **Build & Archive**

```
Product → Archive → Export (for App Store)
```

### App Store Submission Checklist

- [ ] Privacy Policy
- [ ] App Description & Screenshots
- [ ] Category: Utilities or Games
- [ ] Minimum iOS Version: 14.0
- [ ] Required Device Capabilities: none (works on all devices)
- [ ] Privacy Manifest (declare no tracking)

### Key Features for App Store

✅ **Offline-First** - Download full universe graph with `/static/universe_graph.json`
✅ **Privacy** - No personal data collected unless user opts in
✅ **Performance** - Lightweight JSON responses, efficient caching
✅ **Accessibility** - Standard iOS UI patterns (UIKit/SwiftUI)

## Architecture Overview

```
┌─────────────────────────────────────────┐
│          iOS App (SwiftUI)              │
│  - System search                        │
│  - Route planning UI                    │
│  - Activity heatmap visualization       │
│  - Offline universe graph storage       │
└────────────┬────────────────────────────┘
             │ REST API (JSON over HTTPS)
┌────────────▼────────────────────────────┐
│         FastAPI Server (Python)         │
│  - /systems/* (search, details)         │
│  - /regions/* (listings)                │
│  - /routes/plan (Dijkstra)              │
│  - /intel/* (activity, sov, campaigns)  │
│  - /analysis/* (hubs, bottlenecks)      │
└────────────┬────────────────────────────┘
             │ SQLite ORM
┌────────────▼────────────────────────────┐
│      SQLite Database                    │
│  - Regions & Constellations             │
│  - Systems (with coordinates)           │
│  - Stargates (jump connections)         │
│  - Cached heatmap data                  │
└─────────────────────────────────────────┘
             │ HTTP
┌────────────▼────────────────────────────┐
│       ESI API (CCP)                     │
│  - /universe/systems/*                  │
│  - /universe/system_kills/              │
│  - /universe/system_jumps/              │
│  - /incursions/                         │
│  - /sovereignty/                        │
└─────────────────────────────────────────┘
```

## API Endpoints

### System Queries

```
GET /systems/search?q=jita
GET /systems/{system_id}
GET /systems/{system_id}/neighbors
```

### Region Queries

```
GET /regions
GET /regions/{region_id}
GET /regions/{region_id}/systems
GET /regions/{region_id}/constellations
```

### Route Planning

```
POST /routes/plan
{
  "origin": 30000142,
  "destination": 30000144,
  "avoid_lowsec": false,
  "avoid_nullsec": false,
  "avoid_systems": [],
  "avoid_regions": []
}
```

### Analysis

```
GET /analysis/hubs?limit=20
GET /analysis/bottlenecks?limit=20
```

### Live Intel

```
GET /intel/activity          (kills + jumps heatmap)
GET /intel/incursions        (active incursions)
GET /intel/sovereignty       (sov map)
GET /intel/campaigns         (sov campaigns)
GET /intel/all               (combined)
```

### Statistics

```
GET /stats                   (universe stats)
GET /health                  (health check)
```

## Performance Optimization

### Caching Strategy

- **System/Region Data:** TTL 24h (static)
- **Activity Heatmap:** TTL 10 min (live)
- **Hubs/Analysis:** TTL 6h (computed)
- **Cache Layer:** File-based (SQLite option available)

### Database Indexing

Automatic on columns:

- `systems.system_id` (PK)
- `systems.name` (search)
- `systems.region_id` (filtering)
- `regions.region_id` (PK)
- `stargates.system_id` (routing)

### API Response Sizes (Typical)

- System search: 2-5 KB
- Route (5 jumps): 1 KB
- Full heatmap: 50-100 KB
- Universe graph: 2-3 MB (downloaded once, offline)

## Monitoring & Logs

### Enable Logging

In `scripts/run_api.py`:

```python
uvicorn.run(
    app,
    log_level="info",  # "debug" for verbose
)
```

### Health Checks

```bash
curl http://localhost:8000/health
# {"status":"ok","timestamp":"2024-11-12T..."}
```

### Performance Metrics

- API response time: < 100ms (cached)
- Heatmap fetch: < 500ms (live)
- Route planning: < 50ms (precomputed)

## Troubleshooting

### SDE Download Fails

**Problem:** Network errors fetching SDE from GitHub
**Solution:**
1. Check internet connection
2. SDE loader retries automatically (3x)
3. Use mock data for testing: `from evemap.sde_mock import MockSDELoader`

### Database Locked

**Problem:** "database is locked"
**Solution:**
```bash
rm data/universe.db data/universe.db-wal data/universe.db-shm
python scripts/init_universe.py
```

### Memory Usage High

**Problem:** Server using > 500MB RAM
**Solution:**
1. Reduce graph in-memory cache (for large universes)
2. Enable database connection pooling
3. Implement pagination for list endpoints

## Security Considerations

### For Production

1. **API Authentication** (Phase 4)
   - OAuth2 for ESI auth optional features
   - Rate limiting per IP
   - CORS configuration

2. **Database Security**
   - Use PostgreSQL + SSL in production
   - Encrypted backups
   - Regular dumps to S3

3. **Network**
   - HTTPS only
   - Cloudflare/CDN caching
   - DDoS protection

### Privacy

- No personal tracking
- Optional auth only for character-specific features
- Privacy policy required for App Store

## Next Steps

### Phase 3: Capital Jump Planner

```python
# Dogma-based jump range calculation
from evemap.capital_planner import CapitalJumpPlanner

planner = CapitalJumpPlanner()
ranges = planner.calculate_ranges(ship_type="Supercarrier", skills={...})
chains = planner.plan_multi_leg_jumps(origin, destination, ranges)
```

### Phase 4: OAuth Integration

```python
# ESI OAuth for personal data
from evemap.oauth import ESIOAuthClient

oauth = ESIOAuthClient(scopes=[
    "esi-location.read_location.v1",
    "esi-ui.write_waypoint.v1",
])
```

### Phase 5: Corp Features

```python
# Corporation project routes
from evemap.corp import CorporationProjects

projects = CorporationProjects()
routes = projects.get_corp_routes(corp_id)
```

## Support & Resources

- **EVE Online ESI Docs:** https://esi.eveonline.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy ORM:** https://docs.sqlalchemy.org/
- **iOS SwiftUI:** https://developer.apple.com/swiftui/
