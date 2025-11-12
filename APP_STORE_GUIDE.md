# EVE Map - App Store Submission Guide

Complete step-by-step guide to submit your iOS app to the App Store.

## Prerequisites

1. **Apple Developer Account** - $99/year
2. **Mac with Xcode 14+**
3. **iOS device for testing** (optional but recommended)
4. **Bundle ID** - Unique identifier (e.g., `com.yourcompany.evemap`)

## Step 1: Create Xcode Project

### In Xcode:
1. File → New → Project
2. Select "App" template
3. Configure:
   - **Product Name:** EVE Map
   - **Team:** Your Apple Developer Team
   - **Organization Identifier:** com.yourcompany
   - **Bundle Identifier:** com.yourcompany.evemap
   - **Language:** Swift
   - **Interface:** SwiftUI

### Add the iOS App Code

1. Copy the entire content of `examples/ios_evemap_app.swift`
2. In Xcode: File → New → File → Swift File
3. Name it `ContentView.swift` (or `App.swift` for the @main entry point)
4. Paste the code

### Fix the APIClient

Update the `EVEMapClient` base URL in the code - add this to your project:

```swift
class EVEMapClient: ObservableObject {
    private let baseURL: URL
    private var cancellables = Set<AnyCancellable>()

    @Published var isLoading = false
    @Published var errorMessage: String?

    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = URL(string: baseURL)!
    }

    // Add all the endpoint methods from examples/ios_client_example.swift here
    // ... (copy all the methods)
}
```

## Step 2: Prepare App Icons

### Create Icons

You'll need icons in these sizes:
- **1024×1024** - App Store icon (main one)
- **180×180** - iPhone
- **120×120** - iPhone notification
- **167×167** - iPad
- **152×152** - iPad
- **40×40** - Spotlight

### Easy Option: Use an Icon Generator

1. Go to https://appicon.co/ or similar tool
2. Upload your 1024×1024 image
3. Download the icon set
4. In Xcode, drag icons into Assets.xcassets

### Simple Icon Design (Use This If You Don't Have a Designer)

Create a simple icon with:
- **Background:** Blue gradient (dark to light)
- **Symbol:** Globe or location pin
- **Text:** "EM" or "EVE"

You can use online tools like:
- Figma (free, create 1024×1024)
- Canva (free, icon templates)
- Icon generators (https://www.appicon.co/)

## Step 3: Configure App

### In Xcode Project Settings:

1. **General Tab:**
   - Display Name: "EVE Map"
   - Bundle Identifier: "com.yourcompany.evemap"
   - Minimum Deployment: "iOS 14.0"

2. **Signing & Capabilities:**
   - Team: Select your Apple Developer team
   - Automatically manage signing: ✓

3. **Info.plist:**
   - Add "Privacy Policy URL" key
   - Add "App URL" (optional)

4. **App Clips** (can skip for initial release)

## Step 4: Create Privacy Policy

### Minimal Privacy Policy Template

Save this as `PRIVACY_POLICY.md`:

```markdown
# Privacy Policy for EVE Map

**Last Updated:** [Today's Date]

## Information We Collect

EVE Map does not collect or store any personal information. The app:
- Connects to EVE Online's public ESI API
- Stores user preferences locally on device (API URL, ship configs)
- Does not upload personal data to any server

## Local Storage

The following data is stored on your device:
- API URL configuration
- Ship configuration presets
- Universe graph cache (offline map data)

## Third-Party Services

This app uses:
- **ESI API** (CCP's public Eve Online API)
  - See CCP's terms: https://developers.eveonline.com/

## No Tracking

We do not:
- Collect user location data
- Track usage analytics
- Share data with third parties
- Use cookies or advertising

## Data You Control

All user-created data (ship configs) is:
- Stored exclusively on your device
- Never transmitted without your action
- Deletable at any time through app settings

## Questions?

Contact: [your-email@example.com]
```

## Step 5: Prepare Screenshots

Create 6-8 screenshots showing:

1. **Map Search** - System search screen
2. **System Details** - Showing a system with neighbors
3. **Route Planning** - A planned route
4. **Capital Planner** - Ship selection
5. **Jump Route** - Completed jump chain
6. **Settings** - App configuration

### Screenshot Specs:

For iPhone (all are portrait):
- **iPhone 15 Pro:** 1290×2796 pixels
- **iPad Pro 11":** 1668×2388 pixels (landscape)

### Easy Screenshot Creation:

1. **Run the app on a simulator**
2. Cmd+S to save screenshot
3. Or use Xcode: Debug → View Hierarchy → Take Screenshot
4. Crop to 1290×2796 for iPhone

### Placeholder Text for Screenshots:

1. "Explore New Eden - Search 8,000+ systems"
2. "Navigate the galaxy with precision routing"
3. "Plan capital ship jumps with dogma calculations"
4. "Real-time activity heatmaps"
5. "Offline support - download the universe"
6. "Synced with EVE Online ESI"

## Step 6: Build & Test

### Local Testing:

```bash
# In Xcode:
1. Select your target device (iPhone 15, etc.)
2. Product → Build (Cmd+B)
3. Product → Run (Cmd+R)
4. Test all features:
   - Search systems ✓
   - Plan routes ✓
   - Jump planner ✓
   - Settings ✓
```

### Test on Device (Recommended):

1. Connect iPhone via USB
2. Trust the computer on iPhone
3. Select device in Xcode
4. Product → Run

## Step 7: Build for Distribution

```bash
# In Xcode:
1. Product → Archive
2. Select "EVE Map" from archive list
3. Click "Distribute App"
4. Select "App Store Connect"
5. Select team & bundle ID
6. Review and upload
```

## Step 8: Create App Store Listing

### Go to App Store Connect:
https://appstoreconnect.apple.com/

### Create New App:

1. **+ My Apps → New App**
   - Name: "EVE Map"
   - Bundle ID: com.yourcompany.evemap
   - SKU: any unique ID (e.g., "evemap-001")
   - User Access: Select access level

### Fill in Required Information:

#### **App Information:**
- Category: **Utilities** (or Navigation)
- Subcategory: (optional)
- Content Rights: Check "Does not use third-party content"

#### **Pricing and Availability:**
- Price: **Free**
- Regions: Select all (or filter)
- Availability Date: Today or future

#### **General App Information:**
- **Description:**

```
EVE Map - Navigate New Eden on mobile.

Features:
- Real-time activity heatmaps (kills, jumps)
- System search and route planning
- Capital ship jump planner with dogma calculations
- Offline support - download the entire universe
- Sovereignty and incursion overlays
- Synced with EVE Online ESI API

Plan your logistics, find hubs, and explore the galaxy.
Designed for capsuleers who move capital ships.

Requires connection to EVE Online API.
(Does not require game account)
```

- **Keywords:**
  - EVE Online, map, navigation, routes, jumps, capitals

- **Support URL:**
  ```
  https://github.com/yourname/evemap
  ```

- **Privacy Policy URL:**
  ```
  https://yoursite.com/evemap/privacy (or use template from Step 4)
  ```

#### **App Preview & Screenshots:**
- Add 6-8 screenshots (see Step 5)
- Add preview video (optional)

#### **App Review Information:**
- **Demo Account:** (leave blank - not required)
- **Notes for Reviewers:**
  ```
  EVE Map is a companion app for EVE Online that uses public data.
  - No account required
  - No personal data collection
  - Offline-first design
  - Free and open source
  ```

- **Contact Info:**
  - Your name
  - Your email
  - Your phone

#### **Age Rating:**
- Select "Get started"
- Answer questions (should all be "No" for this app)
- Save rating

#### **Build Selection:**
- Select your uploaded build version
- Set as default for this version

## Step 9: Submit for Review

### Final Checks:

- ✓ All required fields filled
- ✓ Screenshots uploaded (6-8)
- ✓ Privacy policy linked
- ✓ Build selected and tested
- ✓ Content rating completed
- ✓ Legal/compliance reviewed

### Submit:

1. Click **"Submit for Review"**
2. Confirm submission
3. Wait for Apple review (24-48 hours typically)

## Step 10: After Approval

Once approved (you'll get email notification):

1. App appears on App Store within hours
2. Share link: https://apps.apple.com/app/eve-map/[ID]
3. Monitor reviews and ratings
4. Plan updates (submit as new builds)

---

## Troubleshooting

### Common Rejection Reasons:

**"App crashes on launch"**
- Test on device before submitting
- Check console for errors

**"Requires account but doesn't disclose"**
- EVE Map doesn't require account ✓

**"Misleading metadata"**
- Descriptions should be accurate
- Screenshots should match app

**"Unresponsive UI"**
- Test with API timeouts
- Add error handling

### API Connection Issues:

If your backend isn't accessible:

```swift
// In ios_evemap_app.swift, update:
let savedURL = UserDefaults.standard.string(forKey: "apiURL")
              ?? "https://your-production-url.com"
```

## Cloud Deployment (For App Store)

Your app needs a live API server. Options:

### Option 1: Heroku (Free tier deprecated, but still cheapest)
```bash
heroku login
heroku create evemap-api
git push heroku main
# Deploy backend there
```

### Option 2: AWS Lambda + API Gateway
- Dockerfile provided
- Deploy using AWS CLI

### Option 3: DigitalOcean App Platform
- Simple deployment UI
- ~$5-12/month

## Maintenance

After launch:

1. **Monitor reviews** - Fix issues quickly
2. **Update regularly** - Add Phase 4 features
3. **Track crashes** - Use Xcode Cloud
4. **Gather analytics** - Consider adding tracking (with privacy)

---

## Marketing

After approval:

- **Reddit:** Post to /r/Eve with "Released on App Store"
- **EVE Forums:** Announce on Official Forums
- **Discord:** Share in EVE communities
- **Twitter:** Tweet with screenshots

---

## Reference

- Apple Developer: https://developer.apple.com
- App Store Connect: https://appstoreconnect.apple.com
- EVE Online ESI: https://esi.eveonline.com
- Xcode Cloud: https://developer.apple.com/xcode-cloud/

Good luck! 🚀
