# Google Play Store Submission Guide - EVE Map Android

Complete step-by-step guide to build, test, and submit your EVE Map Android app to Google Play Store.

## Quick Start

```bash
# Build signed APK/AAB
./gradlew bundleRelease

# Upload to Google Play Console
# (See steps below)
```

**Timeline:**
- Setup: 30 minutes
- Build & test: 1 hour
- First review: 24-48 hours
- **Total to launch: ~2-3 days**

---

## Part 1: Development Setup

### 1.1 Prerequisites

- Android Studio Flamingo or later
- Java 17+ (AGP 8.0+ requirement)
- Google Play Developer Account ($25 one-time fee)
- Keystore file for signing

### 1.2 Install Android Studio

```bash
# macOS with Homebrew
brew install android-studio

# Or download from
https://developer.android.com/studio
```

### 1.3 Configure SDK

In Android Studio:
1. **Tools** → **SDK Manager**
2. Install:
   - Android SDK 34 (API level 34)
   - Android SDK Build-Tools 34.0.0
   - Android Emulator
   - Android SDK Platform-Tools

### 1.4 Set Environment Variables

```bash
# Add to ~/.zprofile or ~/.bash_profile
export ANDROID_SDK_ROOT="$HOME/Library/Android/sdk"
export ANDROID_HOME="$ANDROID_SDK_ROOT"
export PATH="$ANDROID_SDK_ROOT/tools:$ANDROID_SDK_ROOT/platform-tools:$PATH"

# Reload
source ~/.zprofile
```

### 1.5 Verify Setup

```bash
# Check Android SDK
sdkmanager --list_installed

# Check Java
java -version
# Should output: version 17 or higher

# Check Gradle
./gradlew --version
```

---

## Part 2: Prepare App

### 2.1 Update App Information

Edit `android/app/build.gradle.kts`:

```kotlin
android {
    namespace = "com.evemap"  // Your package name
    compileSdk = 34

    defaultConfig {
        applicationId = "com.evemap"  // Must be unique in Play Store
        minSdk = 26                    // Android 8.0+
        targetSdk = 34                 // Android 14
        versionCode = 1                // Increment for each release
        versionName = "1.0.0"          // User-facing version

        // ... rest of config
    }
}
```

### 2.2 Update App Metadata

**Strings** (`android/app/src/main/res/values/strings.xml`):
```xml
<string name="app_name">EVE Map</string>
<string name="app_description">2D Starmap for EVE Online</string>
```

### 2.3 Create App Icons

**Required Sizes:**
- 192×192 px - Notification icon
- 512×512 px - App store listing
- 1024×1024 px - Play Store (recommended)

**Steps:**
1. Export your EVE Map logo as PNG (transparent background)
2. Scale to different sizes using ImageMagick:
   ```bash
   convert logo.png -resize 192x192 ic_launcher_web.png
   convert logo.png -resize 512x512 ic_launcher_playstore.png
   ```
3. Place in `android/app/src/main/res/mipmap-*/ic_launcher.png`

**Folder Structure:**
```
android/app/src/main/res/
├── mipmap-hdpi/ic_launcher.png (72×72)
├── mipmap-mdpi/ic_launcher.png (48×48)
├── mipmap-xhdpi/ic_launcher.png (96×96)
├── mipmap-xxhdpi/ic_launcher.png (144×144)
├── mipmap-xxxhdpi/ic_launcher.png (192×192)
└── mipmap-anydpi-v33/ic_launcher.xml
```

### 2.4 Generate App Icons with Android Studio

**Easy Method:**
1. Right-click `android/app/src/main/res`
2. **New** → **Image Asset**
3. Select **Launcher Icons (Adaptive and Legacy)**
4. Upload your 512×512 PNG
5. Click **Next** → **Finish**

---

## Part 3: Code Signing

### 3.1 Create Keystore (First Time Only)

```bash
# Create keystore file (good for 25 years)
keytool -genkey -v \
  -keystore release.keystore \
  -keyalias evemap-release-key \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# You'll be prompted for:
# - Password (remember this!)
# - First/Last Name
# - Organization Unit: Engineering
# - Organization: Your Company
# - City/State/Country

# Verify keystore
keytool -list -v -keystore release.keystore
```

**Save keystore securely:**
```bash
# Copy to android directory
cp release.keystore android/

# Add to .gitignore
echo "release.keystore" >> .gitignore
echo "*.keystore" >> .gitignore
```

### 3.2 Configure Gradle Signing

Create `android/local.properties` (DO NOT COMMIT):

```properties
# Keystore settings
RELEASE_KEYSTORE_PATH=../release.keystore
RELEASE_KEY_ALIAS=evemap-release-key
RELEASE_KEY_PASSWORD=your_key_password_here
RELEASE_STORE_PASSWORD=your_store_password_here
```

Update `android/app/build.gradle.kts`:

```kotlin
android {
    // ... existing config ...

    signingConfigs {
        create("release") {
            val keyStorePath = System.getenv("RELEASE_KEYSTORE_PATH")
                ?: project.findProperty("RELEASE_KEYSTORE_PATH")?.toString()
                ?: "release.keystore"

            storeFile = file(keyStorePath)
            storePassword = System.getenv("RELEASE_STORE_PASSWORD")
                ?: project.findProperty("RELEASE_STORE_PASSWORD")?.toString()
            keyAlias = "evemap-release-key"
            keyPassword = System.getenv("RELEASE_KEY_PASSWORD")
                ?: project.findProperty("RELEASE_KEY_PASSWORD")?.toString()
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

---

## Part 4: Build for Release

### 4.1 Build Release APK

```bash
cd android
./gradlew assembleRelease
```

**Output:** `android/app/build/outputs/apk/release/app-release.apk`

**Or build Bundle (Recommended for Play Store):**

```bash
./gradlew bundleRelease
```

**Output:** `android/app/build/outputs/bundle/release/app-release.aab`

### 4.2 Test on Device

```bash
# List connected devices
adb devices

# Install APK
adb install -r app/build/outputs/apk/release/app-release.apk

# Test thoroughly
# - All screens load
# - API connection works
# - Navigation functions
# - No crashes
```

### 4.3 Verify Build Quality

```bash
# Check APK size
ls -lh app/build/outputs/apk/release/app-release.apk
# Should be < 10 MB

# Analyze with bundletool
bundletool build-apks \
  --bundle=app/build/outputs/bundle/release/app-release.aab \
  --output=app-release.apks

# Install and test
bundletool install-apks --apks=app-release.apks
```

---

## Part 5: Google Play Console Setup

### 5.1 Create Developer Account

1. Visit https://play.google.com/console
2. Sign in with your Google account
3. Accept terms and pay $25 one-time fee
4. Fill in account details

### 5.2 Create App

1. Click **Create app**
2. **App name:** "EVE Map"
3. **Default language:** English
4. **App type:** Games → Simulation
5. **Free or paid:** Free
6. Click **Create**

### 5.3 App Details

In Console, complete all sections:

**1. App name & description**
```
Name: EVE Map
Short description: 2D Starmap for EVE Online
Full description:
Explore New Eden with a 2D interactive starmap. Plan capital
ship jumps, search for systems, and view live intel from the
Tranquility cluster.

Features:
- Interactive 2D map of EVE's universe
- System search and route planning
- Capital ship jump planner with dogma calculations
- Live kill statistics and sovereignty data
- Multiple deployment options (Heroku, AWS, DigitalOcean)
```

**2. Category & Rating**
- Category: Strategy Games
- Content rating: PEGI 3 (Strategy/Simulation)

**3. Target audience**
- Age: 16+ (accounts management game)

---

## Part 6: Prepare Store Listing

### 6.1 App Icon (512×512)

- Use your high-quality icon
- No rounded corners (Android adds them)
- No text or transparency outside main content
- Safe area: 66 pixels from edges

### 6.2 Feature Graphic (1024×500)

Create a banner showing:
- App name: "EVE Map"
- Key feature: "EVE Online Starmap"
- Visual: Screenshot of main screen

Design tips:
- High contrast text
- Bold fonts
- Show core feature

### 6.3 Screenshots (Required for phones, tablets)

**Phone Screenshots (1080×1920):**

Take 5 screenshots showing:
1. **Map Search** - "Search Systems & Regions"
2. **Route Planning** - "Plan Routes Across New Eden"
3. **Capital Planner** - "Jump Planning for Capital Ships"
4. **Ship Selection** - "15 Capital Ships Supported"
5. **Settings** - "Configure Your API Connection"

Add annotations:
```bash
# Using ImageMagick to add text
convert screenshot1.png \
  -gravity SouthWest \
  -pointsize 60 \
  -fill white \
  -annotate +60+60 "Search Systems & Regions" \
  annotated_screenshot1.png
```

**Tablet Screenshots (2560×1600):**
- Same content as phone
- Landscape orientation
- Larger text for readability

### 6.4 Video Preview (Optional)

Create 30-second video showing:
- App opening
- Map navigation
- System search
- Jump planning
- Settings

---

## Part 7: Privacy & Compliance

### 7.1 Privacy Policy

Create `docs/ANDROID_PRIVACY_POLICY.md`:

```markdown
# Privacy Policy - EVE Map Android

## Data Collection

We collect NO personal data. The app:
- Stores settings locally on your device
- Fetches public data from EVE's ESI API
- Does NOT track your activities
- Does NOT collect system IDs or searches
- Does NOT access your contacts/files

## Network Requests

The app connects to:
- Your configured EVE Map backend (your own server)
- CCP's ESI API (public EVE Online data)

## Data Storage

All data is stored locally:
- Settings via Android DataStore
- No cloud sync
- Data deleted when app is uninstalled

## COPPA Compliance

This app is not intended for children under 13.
```

Host the policy at:
```
https://your-domain.com/privacy
```

Then in Google Play Console:
1. **App content** → **Privacy policy**
2. Paste URL

### 7.2 Consent Declarations

In Google Play Console:
1. **Data safety** → **Manage**
2. Declare:
   - ✅ Network permission (for API calls)
   - ❌ No personal data collection
   - ❌ No health data
   - ❌ No financial data

---

## Part 8: Upload & Submit

### 8.1 Upload Bundle

In Google Play Console:

1. **Your apps** → Select "EVE Map"
2. **Build** → **App bundles & APKs**
3. Click **Upload new release**
4. Select **Production** track
5. Click **Browse files** → Select `app-release.aab`
6. Click **Upload**

Wait for validation (5-10 minutes)

### 8.2 Review Release Details

1. Version number: `1.0.0`
2. Release notes:
   ```
   Initial release:
   - Interactive 2D starmap
   - System search & routing
   - Capital ship jump planner
   - Live intel data
   - Works offline with graph cache
   ```
3. Click **Save**

### 8.3 Submit for Review

1. Review all sections (✅ checkmarks required)
2. Click **Submit to review**
3. Confirm you understand:
   - App must meet Play policies
   - Review takes 24-48 hours
   - May be rejected if issues found

---

## Part 9: Monitor Review Status

### 9.1 Track Status

In Google Play Console:
1. **Your apps** → **EVE Map**
2. **Releases** → View status

**Statuses:**
- 🟡 **In review** (1-48 hours)
- 🟢 **Approved** (now live!)
- 🔴 **Rejected** (fix issues, resubmit)

### 9.2 Common Rejection Reasons

**Issue:** "Gameplay not clear"
**Fix:** Add tutorial overlay or improve settings UI

**Issue:** "Missing privacy policy"
**Fix:** Add privacy policy URL

**Issue:** "Crashes on testing devices"
**Fix:** Test on API 26-34 devices, add error handling

**Issue:** "Misleading content"
**Fix:** Update description/screenshots to match features

---

## Part 10: Post-Launch

### 10.1 Version Updates

For next versions:

1. Update `versionCode` (increment by 1)
2. Update `versionName` ("1.0.1", "1.1.0", etc.)
3. Update backend API endpoint if needed
4. Build & test
5. Upload new AAB to Play Store

```kotlin
defaultConfig {
    versionCode = 2          // Was 1
    versionName = "1.0.1"    // Was 1.0.0
}
```

### 10.2 Monitor Crashes

In Google Play Console:
1. **Android vitals** → **Crashes & ANRs**
2. View crash reports
3. Fix issues in next version

### 10.3 Manage Releases

**Track Types:**
- **Internal testing** - Your team only
- **Closed testing** - Limited tester group
- **Open testing** - Public beta
- **Production** - All users

**Start with Internal Testing:**
```
Click Create release → Select Internal testing
```

**Promote to Production:**
```
After testing: Promote to Production
```

---

## Troubleshooting

### Build Fails: "Keystore not found"

```bash
# Check keystore path
ls -la android/release.keystore

# Update local.properties with correct path
cat android/local.properties
```

### Build Fails: "Unable to load SDK"

```bash
# Install Android SDK
sdkmanager "platforms;android-34"
sdkmanager "build-tools;34.0.0"
```

### APK Too Large (> 10 MB)

```bash
# Enable ProGuard minification
isMinifyEnabled = true
isShrinkResources = true

# Analyze size
./gradlew analyzeReleaseBundle
```

### App Crashes on Launch

1. Check API URL is set in Settings
2. Verify network connectivity
3. Check logcat:
   ```bash
   adb logcat | grep EVEMap
   ```
4. Add try-catch around network calls

### Google Play Console Won't Accept AAB

- Ensure API level 26-34
- Check minSdk is 26 or lower
- Verify all permissions in AndroidManifest.xml

---

## Checklist

Before submitting to Play Store:

- [ ] Update version code/name
- [ ] Test on real device (not emulator)
- [ ] Test offline mode
- [ ] Test all 4 tabs (Map, Routes, Capital, Settings)
- [ ] API connection works
- [ ] No crashes in logcat
- [ ] Icons created (512×512 min)
- [ ] Screenshots created (5+ per device type)
- [ ] Privacy policy written & hosted
- [ ] Description updated & reviewed
- [ ] Bundle built and tested
- [ ] APK size < 10 MB
- [ ] Signed with release keystore
- [ ] Ready for submission

---

## References

- [Android Developer Docs](https://developer.android.com/)
- [Google Play Console Help](https://support.google.com/googleplay/android-developer)
- [Android Studio Setup](https://developer.android.com/studio/install)
- [Building & Publishing](https://developer.android.com/studio/publish)

---

**Congratulations on launching your EVE Map Android app! 🎉**
