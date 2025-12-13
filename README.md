# EVE Map Visualization

**Interactive EVE Online Map Visualization showcasing real-time system data, route planning, and system overlays with Python.**

A comprehensive toolkit for visualizing EVE Online's New Eden universe, featuring a FastAPI backend with risk-aware routing and a matplotlib-based 2D map visualization frontend. This project demonstrates excellence in real-time data visualization and API integration for game analytics and route planning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### Real-time API System Updates
- **ESI API Integration**: Direct integration with EVE Online's External Services Interface (ESI) API for live universe data
- **Automatic Data Caching**: LRU-cached data loading for optimal performance
- **Rate-Limited Requests**: Respectful API usage with exponential backoff retry logic

### Interactive Map Visualization
- **Zoom & Pan Capabilities**: Matplotlib-powered interactive 2D map navigation
- **Multiple Layout Algorithms**: Spring, Kamada-Kawai, circular, and shell layouts
- **Dynamic Filtering**: Filter by security status (high-sec, low-sec, null-sec, wormhole)
- **Grouping Options**: Visualize by region, constellation, or security classification

### Informative Overlays
- **Risk Assessment**: Real-time risk scoring based on security status and zKillboard data
- **Route Planning**: Dijkstra-based pathfinding with multiple routing profiles (shortest, safer, paranoid)
- **System Intelligence**: Detailed system information including neighbors, gates, and risk reports
- **Security-Colored Nodes**: Visual security status indicators for quick assessment

### Backend API
- **RESTful Endpoints**: FastAPI-powered API for system queries and route calculation
- **Risk-Aware Routing**: Configurable risk weights for different playstyles
- **CORS Support**: Ready for frontend integration
- **OpenAPI Documentation**: Auto-generated Swagger UI and ReDoc

## 📸 Screenshots

### Security Status Map
The map visualization shows systems color-coded by security status:
- 🔵 **Blue**: High-security systems (0.5 to 1.0)
- 🟠 **Orange**: Low-security systems (0.1 to 0.4)
- 🔴 **Red**: Null-security systems (-1.0 to 0.0)
- 🟣 **Purple**: Wormhole space

### Route Planning
Calculate optimal routes between systems with different safety profiles:
- **Shortest**: Minimum jumps, ignoring risk
- **Safer**: Balanced risk vs distance
- **Paranoid**: Maximum safety, avoiding dangerous systems

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or conda package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AreteDriver/evemap.git
cd evemap
```

2. **Install dependencies**
```bash
# For visualization only
pip install -r requirements.txt

# For backend API
cd backend
pip install -r requirements.txt
```

### Usage

#### Frontend Visualization

```python
from evemap import ESIClient, NedenMap
from evemap.models import SecurityStatus

# Initialize ESI client
client = ESIClient()

# Fetch region data (e.g., The Forge - Jita's region)
systems, constellations, connections = client.get_region_data(10000002)

# Create and render map
map_viz = NedenMap(systems, connections)
map_viz.calculate_layout(method="spring", iterations=100)
map_viz.render(show_labels=True, show_edges=True)
map_viz.save('map_output.png')
```

#### Backend API Server

```bash
cd backend
uvicorn app.main:app --reload
```

Access the API at:
- **API Root**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Integration Examples

### List All Systems
```bash
curl http://localhost:8000/systems/
```

```python
import requests

response = requests.get('http://localhost:8000/systems/')
systems = response.json()
print(f"Total systems: {len(systems)}")
```

### Get System Risk Report
```bash
curl http://localhost:8000/systems/Jita/risk
```

```python
import requests

response = requests.get('http://localhost:8000/systems/Jita/risk')
risk_data = response.json()
print(f"Risk Score: {risk_data['risk_score']}")
print(f"Classification: {risk_data['classification']}")
```

### Calculate Route with Risk Awareness
```bash
curl "http://localhost:8000/map/route?from=Jita&to=Niarja&profile=safer"
```

```python
import requests

params = {
    'from': 'Jita',
    'to': 'Niarja',
    'profile': 'safer'
}
response = requests.get('http://localhost:8000/map/route', params=params)
route = response.json()
print(f"Route: {' -> '.join([hop['system'] for hop in route['path']])}")
print(f"Total Risk: {route['total_risk']}")
```

### Get Map Configuration
```bash
curl http://localhost:8000/map/config
```

```python
import requests

response = requests.get('http://localhost:8000/map/config')
config = response.json()
systems = config['systems']
risk_scores = config['risk_scores']
```

## 🔧 API Endpoints

### Systems API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/systems/` | GET | List all systems in the universe |
| `/systems/{name}/risk` | GET | Get risk report for a specific system |
| `/systems/{name}/neighbors` | GET | Get neighboring systems connected by stargates |

### Map API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/map/config` | GET | Get complete map configuration with risk scores |
| `/map/route` | GET | Calculate route between systems with risk weighting |

**Route Parameters:**
- `from` (required): Source system name
- `to` (required): Destination system name
- `profile` (optional): Routing profile - `shortest`, `safer`, or `paranoid` (default: `safer`)

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation on:
- API data acquisition pipeline (ESI API integration)
- Caching systems and performance optimization
- FastAPI backend architecture
- Visualization rendering pipeline

## 📚 Documentation

- **[SETUP.md](SETUP.md)**: Detailed setup and installation instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical architecture and data flow
- **[Backend README](backend/README.md)**: Backend-specific documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines

## 🔑 Key Components

### ESI Client (`src/evemap/esi_client.py`)
Handles all communication with EVE Online's ESI API:
- Region, constellation, and system data fetching
- Stargate connection mapping
- Retry logic with exponential backoff
- Rate limiting for respectful API usage

### Map Visualization (`src/evemap/map.py`)
2D map rendering with NetworkX and Matplotlib:
- Force-directed graph layouts
- Security-based color schemes
- Filtering and grouping capabilities
- High-resolution export

### Backend Services (`backend/app/services/`)
- **Data Loader**: JSON-based universe data with LRU caching
- **Risk Engine**: Configurable risk assessment system
- **Routing**: Dijkstra algorithm with risk-weighted edges
- **zKillboard Client**: Real-time kill data integration (stub)

## 🛠️ Configuration

### Universe Data (`backend/app/data/universe.json`)
Defines systems and gate connections:
```json
{
  "systems": {
    "Jita": {
      "name": "Jita",
      "security_status": 0.9,
      "region": "The Forge"
    }
  },
  "gates": [
    {
      "from_system": "Jita",
      "to_system": "Perimeter",
      "distance": 1.0
    }
  ]
}
```

### Risk Configuration (`backend/app/data/risk_config.json`)
Customizable risk weights and routing profiles:
```json
{
  "weights": {
    "security_weight": 0.6,
    "zkill_weight": 0.4
  },
  "profiles": {
    "safer": {
      "risk_multiplier": 2.0,
      "max_acceptable_risk": 50
    }
  }
}
```

## 🧪 Testing

```bash
# Run frontend tests
python -m pytest tests/

# Run backend tests
cd backend
python test_backend.py
python verify.py
```

## 📊 Example Output

### Map Statistics
```
Map Statistics:
  Total systems: 69
  Total connections: 142
  Avg connections per system: 4.12

  Security Breakdown:
    High Sec: 45
    Low Sec: 18
    Null Sec: 6
    Wormhole: 0
```

### Route Calculation
```
Route: Jita -> Perimeter -> Uotila -> Niarja
Total Distance: 3 jumps
Total Risk: 12.5
Estimated Safety: 87.5%
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CCP Games** for EVE Online and the ESI API
- **zKillboard** for kill data aggregation
- **NetworkX** for graph algorithms
- **FastAPI** for the excellent web framework

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review example code in `examples/`

---

**Built with ❤️ for the EVE Online community**
