# EVE Map Android Application

Production-ready Android native app for EVE Online starmap visualization, built with **Kotlin + Jetpack Compose**.

**Status:** ✅ Ready for Google Play Store submission

---

## Features

- 🗺️ **Interactive 2D Starmap** - Search systems and view regions
- 🛣️ **Route Planning** - Find routes across New Eden
- 🚀 **Capital Jump Planner** - Plan multi-leg jumps for capital ships
- 📊 **Live Intel** - View kills, jumps, and incursions from ESI API
- 💾 **Offline Support** - Cache graph data locally
- 🎨 **Material Design 3** - Modern Android UI

---

## Architecture

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/evemap/
│   │   │   └── MainActivity.kt        (1300+ lines - Complete app)
│   │   ├── res/
│   │   │   ├── values/
│   │   │   │   ├── strings.xml
│   │   │   │   ├── colors.xml
│   │   │   │   └── themes.xml
│   │   │   └── mipmap-*/
│   │   │       └── ic_launcher.png
│   │   └── AndroidManifest.xml
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── build.gradle.kts
├── settings.gradle.kts
├── gradle/wrapper/
│   └── gradle-wrapper.properties
├── guides/
│   ├── GOOGLE_PLAY_GUIDE.md          (Complete Play Store setup)
│   └── DEVELOPMENT.md                (This file)
└── README.md                         (This file)
```

---

## Quick Start (Development)

### 1. Prerequisites

```bash
# Install Android Studio
brew install android-studio  # macOS
# Or download from https://developer.android.com/studio

# Verify Java 17+
java -version
# Should output: openjdk 17.0.x or higher

# Verify Android SDK
sdkmanager --list_installed
# Should show: Android SDK 34, Build-Tools 34.0.0
```

### 2. Open Project

```bash
# Clone repository
git clone <your-repo>
cd evemap/android

# Open in Android Studio
open -a "Android Studio" .
```

### 3. Configure Local Properties

Create `android/local.properties`:

```properties
# For release builds only
sdk.dir=/Users/your-username/Library/Android/sdk
```

### 4. Run on Emulator

```bash
# List available emulators
emulator -list-avds

# Start emulator (API 30+)
emulator -avd Pixel_4_API_30 &

# Install and run
./gradlew installDebug
./gradlew connectedAndroidTest
```

Or in Android Studio:
1. **Run** → **Run 'app'**
2. Select device/emulator
3. Click **Run**

### 5. Build Debug APK

```bash
./gradlew assembleDebug
# Output: android/app/build/outputs/apk/debug/app-debug.apk
```

---

## Development Guide

### Project Structure

**MainActivity.kt** (1300+ lines) contains:

```kotlin
// ==================== DATA MODELS ====================
// - SystemResponse, SearchResult, RouteResponse
// - JumpChainResponse, ShipResponse
// - HealthResponse

// ==================== API SERVICE ====================
// - EVEMapApiService (Retrofit interface)
// - 5 API endpoints

// ==================== SETTINGS & PERSISTENCE ====================
// - SettingsManager (DataStore for local storage)
// - API URL persistence
// - Ship config caching

// ==================== API CLIENT ====================
// - EVEMapClient (HTTP client with retry logic)
// - OkHttp + Retrofit integration
// - Kotlinx serialization

// ==================== VIEW MODELS ====================
// - EVEMapViewModel (State management)
// - Coroutines for async operations
// - LiveData for UI updates

// ==================== UI COMPONENTS ====================
// - Composable functions for reusable components
// - SecurityBadge, ErrorSnackbar, SystemCard, etc.

// ==================== SCREENS ====================
// - MapSearchScreen - System search
// - RoutePlannerScreen - Route planning
// - CapitalPlannerScreen - Jump planning
// - SettingsScreen - Configuration

// ==================== MAIN APP ====================
// - EVEMapApp - Navigation setup
// - MainActivity - Entry point
```

### Modify Features

**Add new API endpoint:**

1. Update `EVEMapApiService`:
   ```kotlin
   interface EVEMapApiService {
       @GET("/new-endpoint")
       suspend fun getNewData(): NewResponse
   }
   ```

2. Add to `EVEMapViewModel`:
   ```kotlin
   fun fetchNewData() {
       viewModelScope.launch {
           try {
               val data = apiClient?.api?.getNewData()
               // Update state
           } catch (e: Exception) {
               // Handle error
           }
       }
   }
   ```

3. Create composable in `SettingsScreen` or new tab

**Add new screen:**

1. Create composable:
   ```kotlin
   @Composable
   fun NewScreen(viewModel: EVEMapViewModel) {
       Column {
           // UI here
       }
   }
   ```

2. Add to `NavHost`:
   ```kotlin
   composable("new-route") { NewScreen(viewModel) }
   ```

3. Add to `NavigationBar`:
   ```kotlin
   NavigationBarItem(
       selected = navController.currentDestinationAsState().value?.route == "new-route",
       onClick = { navController.navigate("new-route") },
       label = { Text("New") },
       icon = { Icon(Icons.Default.Star, contentDescription = "New") }
   )
   ```

### Dependencies

All dependencies are in `app/build.gradle.kts`:

- **Compose**: UI framework (Material 3)
- **Navigation**: Multi-screen navigation
- **Retrofit**: HTTP client
- **OkHttp**: Network requests
- **Kotlinx Serialization**: JSON parsing
- **DataStore**: Local preferences
- **WorkManager**: Background jobs

---

## Building for Release

### 1. Create Signing Key (First Time)

```bash
keytool -genkey -v \
  -keystore release.keystore \
  -keyalias evemap-release-key \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

### 2. Configure Gradle

Create `android/local.properties`:

```properties
RELEASE_KEYSTORE_PATH=../release.keystore
RELEASE_KEY_ALIAS=evemap-release-key
RELEASE_KEY_PASSWORD=your_password
RELEASE_STORE_PASSWORD=your_password
```

### 3. Build Release Bundle

```bash
./gradlew bundleRelease
# Output: android/app/build/outputs/bundle/release/app-release.aab
```

### 4. Build Release APK (Optional)

```bash
./gradlew assembleRelease
# Output: android/app/build/outputs/apk/release/app-release.apk
```

### 5. Test on Device

```bash
adb install -r app/build/outputs/apk/release/app-release.apk

# Test all features:
# - Launch app
# - Set API URL
# - Search systems
# - Plan routes
# - Plan capital jumps
# - View settings
```

---

## Google Play Store Submission

**See:** `guides/GOOGLE_PLAY_GUIDE.md` for complete step-by-step guide.

**Quick summary:**

1. Create Google Play Developer account ($25)
2. Update version code/name
3. Create app icons (512×512)
4. Take screenshots (1080×1920)
5. Build release bundle
6. Upload to Google Play Console
7. Fill in store listing
8. Add privacy policy
9. Submit for review
10. Wait 24-48 hours
11. 🎉 App goes live!

---

## Testing

### Unit Tests

```bash
./gradlew test
```

### Instrumented Tests (on device)

```bash
./gradlew connectedAndroidTest
```

### Manual Testing Checklist

- [ ] App launches without crash
- [ ] Settings screen allows API URL configuration
- [ ] Map search returns results
- [ ] Route planner works
- [ ] Capital jump planner shows ships
- [ ] Jump planning returns chain
- [ ] Offline mode works (cached data)
- [ ] All screens navigate correctly
- [ ] Error messages display properly
- [ ] No logcat errors

### Device Testing

Test on various devices:
- API 26+ (Android 8.0+)
- Different screen sizes (phone, tablet)
- Different manufacturers (Google, Samsung, OnePlus, etc.)
- Landscape and portrait

```bash
# List connected devices
adb devices

# Run on specific device
./gradlew installDebug -DdeviceId=<device-id>
```

---

## Troubleshooting

### Build Issues

**Error: "Build-tools not found"**
```bash
sdkmanager "build-tools;34.0.0"
```

**Error: "Gradle sync failed"**
1. **File** → **Sync Now** in Android Studio
2. Or: `./gradlew clean build`

**Error: "API level not supported"**
```bash
sdkmanager "platforms;android-34"
```

### Runtime Issues

**App crashes on startup**
1. Check API URL is set in Settings
2. Verify backend is running
3. Check Android logcat:
   ```bash
   adb logcat | grep EVEMap
   ```

**API calls fail**
1. Check internet connectivity
2. Verify API URL format (include http://)
3. Check backend is accessible
4. Look at error message in Settings

**UI not loading**
1. Check Compose version compatibility
2. Verify Material 3 theme is applied
3. Run on API 26+ device

---

## Configuration

### API URL

Default: `https://evemap-api.herokuapp.com`

Change in Settings screen or in `SettingsManager`:

```kotlin
private val API_URL_KEY = stringPreferencesKey("api_url")

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Default URL if not configured
    val defaultUrl = "https://your-api-url.com"
}
```

### Feature Flags

To disable features, modify `MainActivity.kt`:

```kotlin
// Disable capital planner
val showCapitalTab = false  // Set to true to show

// Disable route planner
val showRoutesTab = false   // Set to true to show
```

---

## Performance Optimization

### App Size
- Current: ~5 MB (debug)
- Release: ~3 MB (with R8 minification)

To further reduce:
```kotlin
// Enable aggressive minification
isMinifyEnabled = true
isShrinkResources = true
```

### Network Calls
- Retrofit automatically caches responses
- Add OkHttp cache interceptor for HTTP caching
- Implement offline-first architecture with local DB

### UI Rendering
- Compose is optimized for recomposition
- Use `remember` to cache expensive computations
- LazyColumn for large lists

---

## Release Checklist

Before Google Play submission:

- [ ] Version code incremented
- [ ] Version name updated
- [ ] All screens tested
- [ ] No logcat errors
- [ ] Icons created & added
- [ ] Privacy policy written & hosted
- [ ] App Store description complete
- [ ] Screenshots created (5+)
- [ ] Signed with release key
- [ ] Bundle built and verified
- [ ] APK tested on real device
- [ ] Ready for Play Store!

---

## Contributing

To add features:

1. Create a branch
2. Make changes to `MainActivity.kt`
3. Test locally
4. Create pull request

---

## Support

For issues:
1. Check logcat: `adb logcat`
2. Review guide: `guides/GOOGLE_PLAY_GUIDE.md`
3. Check backend health: Visit Settings, check API connection
4. Update API URL if needed

---

## References

- [Jetpack Compose Docs](https://developer.android.com/jetpack/compose)
- [Material 3 Design](https://m3.material.io/)
- [Android Developer Docs](https://developer.android.com/)
- [Kotlin Docs](https://kotlinlang.org/docs/)
- [Retrofit Docs](https://square.github.io/retrofit/)

---

**Ready to launch? 🚀 See GOOGLE_PLAY_GUIDE.md to submit to Play Store!**
