# Quick Start Guide

Get the EVE Online Mobile Map app running in minutes!

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Internet connection (for EVE ESI API)

## Step 1: Clone the Repository

```bash
git clone https://github.com/AreteDriver/evemap.git
cd evemap
```

## Step 2: Set Up the Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Test the installation:
```bash
python test_components.py
```

3. Start the API server:
```bash
python run_api_server.py --region 10000002
```

The server will:
- Fetch data from EVE ESI API (this takes a few minutes)
- Start the API on `http://localhost:5000`

**Note**: Keep this terminal open - the server needs to stay running.

## Step 3: Set Up the Mobile App

1. Open a **new terminal** and navigate to the mobile app:
```bash
cd mobile-app
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Run the app:
- Press `w` to open in web browser (easiest for testing)
- Press `a` for Android emulator
- Press `i` for iOS simulator (macOS only)
- Scan QR code with Expo Go app on your phone

## Step 4: Configure the App

If running on a physical device, you need to update the API URL:

1. Find your computer's IP address:
   - **Windows**: `ipconfig`
   - **Mac/Linux**: `ifconfig` or `ip addr`

2. Edit `mobile-app/src/services/api.js`:
   ```javascript
   const API_BASE_URL = 'http://YOUR_IP_ADDRESS:5000/api';
   ```

3. Restart the mobile app

## Testing the App

### 1. Search for a System
- Open the Map tab
- Search for "Jita"
- View system details

### 2. Plan a Route
- Go to Route tab
- Set origin: "Jita"
- Set destination: "Amarr"
- Toggle security preferences
- Tap "Calculate Route"
- View fuel costs

### 3. Check Intel
- Go to Intel tab
- Search for any system
- View recent kills
- Check danger rating
- Pull down to refresh

## Common Issues

### "Cannot connect to server"
- Ensure backend is running: `python run_api_server.py`
- Check API URL in `mobile-app/src/services/api.js`
- For physical devices, use your computer's IP, not localhost

### "No systems found"
- Backend is still loading data (wait a few minutes)
- Check backend terminal for errors
- Ensure you have internet connection

### Mobile app won't start
- Clear cache: `cd mobile-app && npm start -- --clear`
- Reinstall: `rm -rf node_modules && npm install`

## Development Tips

### Backend Development
- Use `--debug` flag for detailed logging:
  ```bash
  python run_api_server.py --debug
  ```

- Test different regions:
  ```bash
  python run_api_server.py --region 10000043  # Domain
  ```

### Mobile Development
- Enable hot reload (enabled by default)
- Shake device to open developer menu
- Use React DevTools for debugging

## Production Deployment

### Backend
See `docs/deployment/backend.md` for hosting options:
- Heroku
- AWS
- DigitalOcean
- Google Cloud

### Mobile App
See `docs/deployment/mobile.md` for build instructions:
- Android APK
- iOS IPA
- Web build

## Getting Help

- Check the [Documentation](docs/)
- Open an issue on GitHub
- Read the [FAQ](docs/faq.md)

## What's Next?

- Bookmark favorite systems
- Try different ship types
- Explore security filters
- Check out the settings

Enjoy exploring New Eden! 🚀
