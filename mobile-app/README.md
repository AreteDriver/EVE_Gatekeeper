# EVE Online Mobile Map - Mobile App

Cross-platform mobile application for EVE Online route planning and intel gathering.

## Features

- 🗺️ **System Search** - Find and explore EVE Online systems
- 🛣️ **Route Planning** - Calculate routes with security preferences
- ⛽ **Fuel Calculator** - Estimate jump fuel costs for capital ships
- 🔍 **zkillboard Intel** - Real-time kill data and danger ratings
- 📊 **System Details** - View system information and connections

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Expo Go app (for mobile testing)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure API endpoint:
Edit `src/services/api.js` and update `API_BASE_URL` to point to your backend server.

3. Start development server:
```bash
npm start
```

4. Run on your device:
- Scan QR code with Expo Go app (iOS/Android)
- Press `w` for web browser
- Press `a` for Android emulator
- Press `i` for iOS simulator (macOS only)

## Configuration

### API Endpoint
Update the API base URL in `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://your-backend-url:5000/api';
```

For local testing:
- Android emulator: `http://10.0.2.2:5000/api`
- iOS simulator: `http://localhost:5000/api`
- Physical device: Use your computer's IP address

## App Structure

```
mobile-app/
├── src/
│   ├── screens/          # Main app screens
│   │   ├── MapScreen.js      # System search and details
│   │   ├── RouteScreen.js    # Route planning
│   │   ├── IntelScreen.js    # zkillboard intel
│   │   └── SettingsScreen.js # App settings
│   ├── services/         # API and services
│   │   └── api.js            # Backend API client
│   ├── navigation/       # Navigation config
│   │   └── AppNavigator.js   # Tab navigation
│   ├── components/       # Reusable components
│   └── utils/           # Utilities
│       └── theme.js          # App theme
├── assets/              # Images and fonts
└── App.js              # App entry point
```

## Screens

### Map Screen
Search and explore EVE systems:
- Search by system name
- View system details (security, planets, gates)
- Navigate to route planning or intel
- See connected systems

### Route Screen
Plan your route:
- Select origin and destination
- Configure route preferences
- Avoid low/null security systems
- View step-by-step route
- Calculate fuel costs

### Intel Screen
View zkillboard data:
- Recent kills in system
- Danger rating
- Kill values and timestamps
- Attacker information
- Refresh for latest data

### Settings Screen
Configure app:
- API endpoint
- Default ship type
- Fuel prices
- App preferences

## Building for Production

### Android
```bash
eas build --platform android
```

### iOS
```bash
eas build --platform ios
```

### Web
```bash
npm run build
```

## Dependencies

- **@react-navigation** - Navigation
- **react-native-paper** - Material Design components
- **axios** - HTTP client
- **expo** - Development platform

## Troubleshooting

### Cannot connect to API
1. Check API URL in `src/services/api.js`
2. Ensure backend server is running
3. Use correct IP for physical devices
4. Check firewall settings

### App crashes on startup
1. Clear cache: `expo start -c`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Update Expo: `npm install expo@latest`

## Development Tips

### Hot Reload
The app supports hot reloading. Changes will appear automatically.

### Debugging
- Shake device to open developer menu
- Enable Remote JS Debugging
- Use React DevTools

### Testing on Device
1. Install Expo Go from App Store/Play Store
2. Scan QR code from terminal
3. App will load on your device

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.
