# API Usage Examples

This document provides examples of using the EVE Map REST API.

## Base URL

```
http://localhost:5000
```

## Authentication

No authentication required for MVP. Future versions may add API keys.

## Endpoints

### Health Check

Check if the API is running and data is loaded.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "systems_loaded": 120,
  "connections_loaded": 250
}
```

---

### Search Systems

Search for systems by name.

**Request:**
```bash
curl "http://localhost:5000/api/search?q=jita&limit=5"
```

**Response:**
```json
{
  "results": [
    {
      "system_id": 30000142,
      "name": "Jita",
      "region_id": 10000002,
      "security_status": 0.95,
      "security_class": "high_sec"
    }
  ],
  "count": 1
}
```

---

### Get System Details

Get detailed information about a specific system.

**Request:**
```bash
curl http://localhost:5000/api/systems/30000142
```

**Response:**
```json
{
  "system_id": 30000142,
  "name": "Jita",
  "region_id": 10000002,
  "constellation_id": 20000020,
  "security_status": 0.95,
  "security_class": "high_sec",
  "x": 0.234,
  "y": -0.567,
  "planets": 8,
  "stargates": 5,
  "connected_systems": [30001161, 30002768],
  "metadata": {}
}
```

---

### List Systems

Get all systems with optional filtering.

**Request:**
```bash
curl "http://localhost:5000/api/systems?security=high_sec&limit=10"
```

**Query Parameters:**
- `security`: Filter by security status (`high_sec`, `low_sec`, `null_sec`)
- `region_id`: Filter by region ID
- `limit`: Maximum results (default 100)

**Response:**
```json
{
  "systems": [
    {
      "system_id": 30000142,
      "name": "Jita",
      "region_id": 10000002,
      "security_status": 0.95,
      "security_class": "high_sec",
      ...
    }
  ],
  "count": 10
}
```

---

### Calculate Route

Calculate the shortest route between two systems.

**Request:**
```bash
curl -X POST http://localhost:5000/api/route \
  -H "Content-Type: application/json" \
  -d '{
    "origin_id": 30000142,
    "destination_id": 30002187,
    "avoid_low_sec": false,
    "avoid_null_sec": true,
    "max_jumps": 50
  }'
```

**Request Body:**
```json
{
  "origin_id": 30000142,
  "destination_id": 30002187,
  "avoid_low_sec": false,
  "avoid_null_sec": true,
  "max_jumps": 50
}
```

**Response:**
```json
{
  "route": [
    {
      "system_id": 30000142,
      "name": "Jita",
      "security_status": 0.95,
      "security_class": "high_sec",
      "jump_number": 0
    },
    {
      "system_id": 30001161,
      "name": "Perimeter",
      "security_status": 0.88,
      "security_class": "high_sec",
      "jump_number": 1
    }
  ],
  "total_jumps": 5,
  "origin": "Jita",
  "destination": "Amarr"
}
```

---

### Calculate Fuel Cost

Calculate jump fuel cost for a route.

**Request:**
```bash
curl -X POST http://localhost:5000/api/route/fuel-cost \
  -H "Content-Type: application/json" \
  -d '{
    "route": [30000142, 30001161, 30002768],
    "ship_type": "Carrier",
    "fuel_price": 500
  }'
```

**Request Body:**
```json
{
  "route": [30000142, 30001161, 30002768],
  "ship_type": "Carrier",
  "fuel_price": 500
}
```

**Ship Types:**
- `Carrier`
- `Dreadnought`
- `Supercarrier`
- `Titan`
- `Jump Freighter`

**Response:**
```json
{
  "total_jumps": 2,
  "total_fuel": 600,
  "fuel_per_jump": 300,
  "fuel_price": 500,
  "total_cost": 300000,
  "ship_type": "Carrier"
}
```

---

### Get zkillboard Intel

Get recent kill data for a system.

**Request:**
```bash
curl "http://localhost:5000/api/intel/zkillboard/30000142?limit=10"
```

**Query Parameters:**
- `limit`: Number of kills to retrieve (default 10)

**Response:**
```json
{
  "system_id": 30000142,
  "kills": [
    {
      "killmail_id": 123456789,
      "kill_time": "2024-12-08T10:30:00",
      "victim_ship_type": 587,
      "victim_id": 98765432,
      "total_value": 1500000000,
      "is_npc": false,
      "is_solo": true,
      "attacker_count": 1
    }
  ],
  "total_kills": 10,
  "total_value_destroyed": 5000000000,
  "danger_rating": "dangerous"
}
```

**Danger Ratings:**
- `safe`: Few or no kills
- `moderate`: Some activity
- `dangerous`: High activity or high-value kills

---

### Get Map Statistics

Get overall map statistics.

**Request:**
```bash
curl http://localhost:5000/api/stats
```

**Response:**
```json
{
  "total_systems": 120,
  "total_connections": 250,
  "avg_connections_per_system": 4.17,
  "security_breakdown": {
    "high_sec": 60,
    "low_sec": 30,
    "null_sec": 25,
    "wormhole": 5
  }
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request:**
```json
{
  "error": "origin_id and destination_id required"
}
```

**404 Not Found:**
```json
{
  "error": "System not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Route calculation failed"
}
```

---

## Rate Limiting

The API respects rate limits from:
- EVE ESI API: ~150 requests/second
- zkillboard API: ~1 request/second

Internal caching reduces API calls for frequently requested data.

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Search for system
response = requests.get(f"{BASE_URL}/search", params={"q": "jita"})
systems = response.json()["results"]

# Calculate route
route_data = {
    "origin_id": 30000142,
    "destination_id": 30002187,
    "avoid_null_sec": True
}
response = requests.post(f"{BASE_URL}/route", json=route_data)
route = response.json()

# Get intel
response = requests.get(f"{BASE_URL}/intel/zkillboard/30000142")
intel = response.json()
```

---

## JavaScript Client Example

```javascript
const BASE_URL = "http://localhost:5000/api";

// Search for system
const searchSystems = async (query) => {
  const response = await fetch(`${BASE_URL}/search?q=${query}`);
  const data = await response.json();
  return data.results;
};

// Calculate route
const calculateRoute = async (originId, destId) => {
  const response = await fetch(`${BASE_URL}/route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      origin_id: originId,
      destination_id: destId,
      avoid_null_sec: true
    })
  });
  return await response.json();
};

// Get intel
const getIntel = async (systemId) => {
  const response = await fetch(`${BASE_URL}/intel/zkillboard/${systemId}`);
  return await response.json();
};
```

---

## Next Steps

- See the [Mobile App README](../mobile-app/README.md) for client integration
- Check [API Reference](api-reference.md) for complete documentation
- Review [Best Practices](best-practices.md) for optimal usage
