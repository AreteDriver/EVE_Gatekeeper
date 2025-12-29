# EVE Gatekeeper

**Comprehensive EVE Online navigation, routing, and intel visualization platform.**

A production-ready toolkit combining real-time map visualization, risk-aware routing, capital jump planning, and live kill feed streaming. Built with FastAPI, WebSocket support, and modern Python best practices.

[![CI](https://github.com/AreteDriver/EVE_Gatekeeper/actions/workflows/ci.yml/badge.svg)](https://github.com/AreteDriver/EVE_Gatekeeper/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docs.docker.com/)

## Features

- **Risk-Aware Routing**: Dijkstra pathfinding with safety profiles (shortest/safer/paranoid)
- **Real-Time Kill Feed**: WebSocket streaming from zKillboard with custom filters
- **Capital Jump Planning**: Jump range visualization and multi-leg route planning
- **ESI Integration**: Full EVE Swagger Interface integration with caching
- **Production Ready**: Docker, rate limiting, structured logging, Prometheus metrics

## Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/AreteDriver/EVE_Gatekeeper.git
cd EVE_Gatekeeper

# Copy environment template
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

API docs available at: http://localhost:8000/docs

## Quick Start (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Run the server
uvicorn backend.app.main:app --reload --port 8000
```

## Project Structure

```
EVE_Gatekeeper/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/              # Versioned API endpoints
│   │   │   │   ├── systems.py   # System information
│   │   │   │   ├── routing.py   # Route calculation
│   │   │   │   ├── websocket.py # Real-time kill feed
│   │   │   │   └── status.py    # API status
│   │   │   └── metrics.py       # Prometheus metrics
│   │   ├── core/
│   │   │   └── config.py        # Configuration management
│   │   ├── db/                  # Database layer
│   │   ├── middleware/          # Rate limiting, security
│   │   ├── models/              # Pydantic models
│   │   ├── services/
│   │   │   ├── cache.py         # Redis/memory cache
│   │   │   ├── risk_engine.py   # Risk calculation
│   │   │   ├── routing.py       # Pathfinding
│   │   │   ├── zkill_listener.py # zKillboard feed
│   │   │   └── connection_manager.py
│   │   └── main.py              # Application entry
│   └── starmap/                 # Universe data management
├── apps/
│   ├── desktop/                 # Electron desktop app
│   └── mobile/                  # React Native mobile app
├── tests/                       # pytest test suite
├── .github/workflows/           # CI/CD pipelines
├── docker-compose.yml           # Production deployment
└── docker-compose.dev.yml       # Development environment
```

## API Endpoints

### Core API (v1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/systems/` | GET | List all systems |
| `/api/v1/systems/{name}` | GET | Get system details |
| `/api/v1/systems/{name}/risk` | GET | Get risk report |
| `/api/v1/systems/{name}/neighbors` | GET | Get connected systems |
| `/api/v1/route/` | GET | Calculate route (params: from, to, profile) |
| `/api/v1/route/config` | GET | Get map configuration |
| `/api/v1/status/` | GET | Detailed API status |
| `/api/v1/ws/killfeed` | WS | Real-time kill feed |

### Jump Drive API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jump/range` | GET | Calculate jump range for ship type |
| `/api/v1/jump/distance` | GET | Calculate LY distance between systems |
| `/api/v1/jump/systems-in-range` | GET | Find cyno systems within range |
| `/api/v1/jump/route` | GET | Plan multi-leg capital route |

### Jump Bridges API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/bridges/` | GET | List configured bridge networks |
| `/api/v1/bridges/import` | POST | Import bridges from text |
| `/api/v1/bridges/{name}` | GET | Get network details |
| `/api/v1/bridges/{name}` | PATCH | Toggle network enabled/disabled |
| `/api/v1/bridges/{name}` | DELETE | Delete a network |

### Route Comparison API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/route/compare` | POST | Compare routes across profiles |

### Utility Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (for containers) |
| `/metrics` | GET | Prometheus metrics |
| `/docs` | GET | OpenAPI documentation |

## Route Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| `shortest` | Minimum jumps | Speed over safety |
| `safer` | Balanced risk/distance | General travel |
| `paranoid` | Maximum safety | Expensive cargo |

## WebSocket Kill Feed

Connect to `/api/v1/ws/killfeed` for real-time kills:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/killfeed');

// Subscribe to specific systems/regions
ws.send(JSON.stringify({
  type: 'subscribe',
  systems: [30000142],  // Jita
  regions: [10000002],  // The Forge
  min_value: 1000000,   // 1M ISK minimum
  include_pods: false
}));

// Receive kills
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'kill') {
    console.log('Kill:', data.data);
  }
};
```

## Environment Variables

See [.env.example](.env.example) for all configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./eve_gatekeeper.db` | Database connection |
| `REDIS_URL` | - | Redis cache (optional) |
| `ESI_CLIENT_ID` | - | EVE SSO client ID |
| `RATE_LIMIT_PER_MINUTE` | `100` | API rate limit |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=backend/app --cov-report=html

# Type checking
mypy backend/app

# Linting
ruff check backend/
ruff format backend/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Deployment

### Docker Compose (Recommended)

```bash
# Production
docker-compose up -d

# Development with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Manual

```bash
# Install production dependencies
pip install -r backend/requirements.txt

# Run with Gunicorn
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Monitoring

- **Health Check**: `GET /health` - Returns component status
- **Metrics**: `GET /metrics` - Prometheus format
- **Logs**: Structured JSON logging (configurable)

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- **CCP Games** for EVE Online and ESI API
- **zKillboard** for real-time kill data
- **EVE SDE** for universe data

---

**Built for the EVE Online community** | [Report Issues](https://github.com/AreteDriver/EVE_Gatekeeper/issues)
