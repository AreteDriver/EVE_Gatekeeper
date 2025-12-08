# EVE Online Mobile Map Application

A cross-platform mobile application for EVE Online players featuring:

- 🗺️ **2D Map Visualization** - Interactive map of New Eden
- 🛣️ **Route Planning** - Calculate optimal routes between systems
- ⛽ **Jump Fuel Calculator** - Estimate fuel costs for capital ships
- 🔍 **zkillboard Intel** - Real-time kill data and danger ratings
- 🎯 **System Search** - Quick search and system information
- 📱 **Cross-Platform** - Works on iOS, Android, and Web

## Architecture

This project consists of two main components:

### 1. Backend API (Python/Flask)
Located in `src/evemap/`, the backend provides:
- RESTful API endpoints for map data
- Integration with EVE ESI API
- zkillboard data aggregation
- Route calculation and pathfinding
- Fuel cost calculations

### 2. Mobile App (React Native/Expo)
Located in `mobile-app/`, the mobile app provides:
- Native iOS and Android apps
- Interactive user interface
- Real-time intel updates
- Route planning tools
- System search and favorites

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the API server:
```bash
python run_api_server.py --region 10000002 --port 5000
```

The API will be available at `http://localhost:5000`

### Mobile App Setup

1. Navigate to the mobile app directory:
```bash
cd mobile-app
```

2. Install dependencies:
```bash
npm install
```

3. Update API URL in `mobile-app/src/services/api.js` if needed

4. Start the development server:
```bash
npm start
```

5. Run on your platform:
- Press `a` for Android
- Press `i` for iOS (macOS only)
- Press `w` for web browser

## Features

### Map Screen
- Search for systems by name
- View system details (security, planets, stargates)
- See connected systems
- Quick navigation to route planning and intel

### Route Planning
- Set origin and destination systems
- Configure route preferences (avoid low/null sec)
- Calculate shortest path
- View step-by-step route
- Estimate jump fuel costs for different ship types

### Intel Screen
- View recent kills from zkillboard
- Danger rating based on activity
- Kill timestamps and values
- NPC vs. player kills
- Refresh for latest data

### Settings
- Configure API endpoint
- Set default ship type
- Adjust fuel prices
- Toggle auto-refresh

## API Endpoints

### Health Check
```
GET /health
```

### Search Systems
```
GET /api/search?q=<query>&limit=10
```

### Get System Details
```
GET /api/systems/<system_id>
```

### Calculate Route
```
POST /api/route
{
  "origin_id": 30000142,
  "destination_id": 30002768,
  "avoid_low_sec": false,
  "avoid_null_sec": true
}
```

### Calculate Fuel Cost
```
POST /api/route/fuel-cost
{
  "route": [30000142, 30001161, 30002768],
  "ship_type": "Carrier",
  "fuel_price": 500
}
```

### Get zkillboard Intel
```
GET /api/intel/zkillboard/<system_id>?limit=10
```

### Get Map Statistics
```
GET /api/stats
```

## Development

### Project Structure
```
evemap/
├── src/evemap/          # Backend Python code
│   ├── api.py           # REST API server
│   ├── zkillboard.py    # zkillboard integration
│   ├── esi_client.py    # EVE ESI API client
│   ├── map.py           # Map visualization
│   ├── models.py        # Data models
│   ├── utils.py         # Utilities
│   └── cache.py         # Caching
├── mobile-app/          # React Native mobile app
│   ├── src/
│   │   ├── screens/     # App screens
│   │   ├── components/  # Reusable components
│   │   ├── services/    # API services
│   │   ├── navigation/  # Navigation config
│   │   └── utils/       # Utilities
│   └── App.js           # App entry point
├── examples/            # Example scripts
├── docs/                # Documentation
└── requirements.txt     # Python dependencies
```

### Adding New Features

1. **Backend**: Add new endpoints in `src/evemap/api.py`
2. **Mobile**: Add new screens in `mobile-app/src/screens/`
3. **API Client**: Update `mobile-app/src/services/api.js`

## Technologies Used

### Backend
- **Flask** - Web framework
- **NetworkX** - Graph algorithms for routing
- **Requests** - HTTP client for ESI/zkillboard
- **Matplotlib** - Data visualization (for desktop)

### Mobile App
- **React Native** - Mobile framework
- **Expo** - Development platform
- **React Navigation** - Navigation
- **React Native Paper** - UI components
- **Axios** - HTTP client

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is open source and available under the MIT License.

## Credits

- EVE Online™ is a registered trademark of CCP hf.
- Data provided by EVE ESI API and zkillboard.com
- This is a third-party tool not affiliated with CCP Games