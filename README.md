# Arete EVE Navigator — MVP

Goal: Build a **modern 2D EVE Online map** with **risk-aware routing** using:
- CCP universe data (later)
- zKillboard activity (later, stub first)
- JSON-driven configuration for risk scoring and map behavior

This project starts as a **FastAPI backend** that:
- Serves universe + map config for a frontend (web / Flutter)
- Computes a simple **risk score per system**
- Computes **routes** between systems using Dijkstra, with optional risk weighting
- Exposes clean JSON APIs the frontend can consume

Later we will:
- Integrate real ESI / zKill APIs
- Add more layers (WH connections, alliance borders, ESS, etc.)
- Add AI helpers (route advice, danger warnings, etc.)

---

## Tech Stack (backend MVP)

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- httpx (for zKill integration, stub for now)

JSON-driven configuration:
- `universe.json` — systems, gates, positions
- `risk_config.json` — risk weights, routing profiles, map layer toggles, color scale

---

## Project Structure

```text
arete-eve-navigator/
  backend/
    app/
      __init__.py
      main.py
      core/
        __init__.py
        config.py
      api/
        __init__.py
        routes_systems.py
        routes_map.py
      models/
        __init__.py
        system.py
        risk.py
        route.py
      services/
        __init__.py
        data_loader.py
        risk_engine.py
        routing.py
        zkill_client.py
      data/
        universe.json
        risk_config.json
    requirements.txt
```

---

## Core Concepts for Copilot

1. **Universe model**
   - Systems: name, id, region_id, security, category, position(x,y)
   - Gates: from, to, distance
   - Use Pydantic models for validation.
   - Load from universe.json into an in-memory structure (cached).

2. **Risk model**
   - RiskConfig: security weights, kill weights, clamp, risk_colors, map_layers, routing_profiles.
   - ZKillStats: recent_kills, recent_pods.
   - RiskReport: score + breakdown.
   - Risk is computed from:
     - security category
     - recent kills
     - recent pods
   - Color is picked from risk_colors based on the score band.

3. **Routing**
   - Build adjacency graph from gates.
   - Implement Dijkstra.
   - Cost = base distance * (1 + risk_factor * (risk_score / 100)).
   - Profiles:
     - "shortest" -> risk_factor 0.0
     - "safer" -> 1.0
     - "paranoid" -> 2.0

4. **APIs (initial)**
   - GET /systems -> list of systems (name, security, category, region_id).
   - GET /systems/{system_name}/risk -> RiskReport.
   - GET /systems/{system_name}/neighbors -> list of neighbor system names.
   - GET /map/config -> universe + risk_color + risk_score + map_layers.
   - GET /map/route?from=Jita&to=Niarja&profile=safer -> RouteResponse.

5. **zKill integration**
   - For MVP, stub zkill_client.fetch_system_stats(system_id) to return zero activity.
   - Later, Copilot can help implement real HTTP calls to zKillboard and aggregation.

---

## How to Run (backend)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

uvicorn app.main:app --reload
```

Then open:
- http://localhost:8000/docs for Swagger UI
- http://localhost:8000/map/config for map data
- http://localhost:8000/map/route?from=Jita&to=Niarja&profile=safer for a sample route

---

## Copilot Tasks

Copilot, please help with:
1. Expanding the universe by loading real EVE map data later.
2. Implementing real zKillboard integration in zkill_client.py.
3. Improving risk scoring formulas in risk_engine.py.
4. Adding filters to /systems (region, security band, risk threshold).
5. Creating tests for routing and risk scoring.
6. Suggesting a simple frontend (React / Svelte / Flutter) that consumes /map/config and /map/route and renders a 2D map with risk-based colors.
