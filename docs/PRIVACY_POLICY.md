# Privacy Policy for EVE Map

**Last Updated:** November 12, 2024

## Overview

EVE Map ("the App") is a companion application for EVE Online that provides navigation and logistics planning tools. We are committed to protecting your privacy. This Privacy Policy explains how our app handles data.

## Key Privacy Principle

**EVE Map does not collect, store, or transmit personal information about you.**

All data remains on your device unless you explicitly interact with public APIs.

## Information We Collect

### What We Do NOT Collect:
- ❌ Personal information (name, email, address, phone)
- ❌ Device identifiers
- ❌ Location data (GPS, IP address)
- ❌ Browsing history
- ❌ Cookies or tracking identifiers
- ❌ Usage analytics
- ❌ EVE Online character details or account information

### What You Control:
The following data is stored **only on your device**, never transmitted:
- API URL configuration (where to connect for data)
- Ship configuration presets (self-created)
- Universe graph cache (for offline use)

## How the App Works

### Data Flow:

```
Your Device
    ↓
┌─────────────────────┐
│  EVE Map (This App) │  ← All processing happens here
│  - Search systems   │
│  - Plan routes      │
│  - Calculate jumps  │
└─────────────────────┘
    ↓
  EVE Online ESI API (Public)
  https://esi.eveonline.com
    ↓
  Requests:
  - System information
  - Activity heatmaps
  - Sovereignty data
  ↓
  Result → Back to Your Device
```

**You choose the API endpoint** via Settings if using your own backend.

## Third-Party Services

### EVE Online ESI API
- **What it is:** CCP's public API for EVE Online data
- **Data accessed:** Public universe data only
  - System names, regions, security status
  - Jump gate connections
  - Kills/jumps heatmaps
  - Sovereignty information
  - Incursion data
- **What ESI does:** See CCP's privacy policy
  - https://developers.eveonline.com/terms-of-service
- **User account required:** NO - EVE Map uses public endpoints only
- **Personal data sent:** NO - Only server requests, no character data

### Your Backend Server (Optional)
If you provide a custom API URL:
- The app sends: System IDs and route parameters
- The server returns: Route calculations, jump data
- Your backend's privacy policy applies (you control it)

## Data Storage

All app data is stored **locally on your device**:

```
App Documents Folder/
├── API Configuration
│   └── api_url (where you want data from)
├── Ship Configurations
│   ├── ship_name
│   ├── ship_type_id
│   └── skills
└── Cache
    └── universe_graph.json (for offline)
```

**No data leaves your device without your explicit action.**

## Offline Functionality

The app can work completely offline:

1. **Download universe graph** (2.3 MB JSON)
   - ~8,000 systems and connections
   - Downloaded to device once
   - Stays on device until you clear it

2. **Local calculations:**
   - Route planning (no network needed)
   - Jump range calculations (no network needed)
   - All math happens on your phone

3. **Online features:**
   - System search (queries live API)
   - Activity heatmaps (queries live API)
   - Optional - can disable in settings

## User-Created Data

### Ship Configs
- Stored locally as JSON
- Contains: ship type, skills, custom name
- **No personal data** - just game data
- Deleted when you delete from app
- Not backed up to cloud

### History
- Search history: Stored locally, cleared on app exit
- Route history: Not stored
- Settings: Stored locally

## Data You Can Control

✓ **Delete:** Tap Edit on any ship config → Delete
✓ **Export:** Copy ship configs to share with friends
✓ **Offline mode:** Download graph, disable API calls
✓ **Change API:** Settings → Edit API URL
✓ **Clear cache:** Settings → Clear Offline Data

## Security

### On Your Device:
- Data stored in app container (iOS sandboxed)
- Standard iOS file protections apply
- Encrypted if device encryption is enabled

### In Transit:
- Requests to HTTPS APIs only
- No custom encryption (relies on TLS)
- No authentication tokens stored

### If Backend Used:
- Your responsibility to secure it
- We recommend: SSL/TLS, rate limiting, monitoring

## Children's Privacy

EVE Map is designed for adults (EVE Online users). We:
- Do not knowingly collect data from children < 13
- Do not have features targeting children
- Do not market to children

If you're under 13, ask your parent/guardian before using this app.

## Data Retention

| Data | Stored Where | Kept How Long |
|------|--------------|---------------|
| API Config | Device | Until changed |
| Ship Presets | Device | Until deleted |
| Universe Graph | Device | Until cleared |
| Search History | Memory | Session only |
| Cache | Device | Until cleared |

## Your Rights

Under GDPR, CCPA, and similar laws:

✓ **Access:** All your data is on your device
✓ **Modification:** Edit or delete anytime
✓ **Deletion:** Clear app data via iOS Settings
✓ **Export:** Copy ship configs to text
✓ **Right to be forgotten:** Delete app

**Request:** Contact us at [your-email@example.com]

## No Advertising

- ❌ No ads
- ❌ No sponsored content
- ❌ No affiliate links
- ❌ No product placement

The app is free and ad-free.

## Changes to Privacy Policy

We may update this policy. If changes are material:
- We'll notify you via app update
- You'll need to acknowledge before continuing

## Contact Us

**Questions or concerns?**

Email: [your-email@example.com]
GitHub: https://github.com/yourname/evemap

---

## Summary for Lawyers & Regulators

### GDPR Compliance:
- ✓ No personal data processing
- ✓ No cookies or tracking
- ✓ No international data transfer
- ✓ No third-party sharing

### CCPA Compliance:
- ✓ No "personal information" under CCPA definition
- ✓ No sharing with third parties
- ✓ User can delete app → delete all data

### COPPA Compliance (Children):
- ✓ Not directed at children
- ✓ No data collection from anyone
- ✓ No tracking or profiling

---

## Appendix: Technical Details

### App Permissions Needed:
- **Network:** To fetch from ESI API
- **Storage:** To save configs and cache

### No Permissions Required:
- ❌ Camera
- ❌ Microphone
- ❌ Location
- ❌ Contacts
- ❌ Photos
- ❌ Health data

### API Calls Made:
```
GET  /systems/{id}
GET  /systems/search
GET  /regions
GET  /routes/plan
GET  /intel/activity
GET  /capital/ships
POST /capital/jump-chain
```

All public, no authentication, no personal data.

---

**By using EVE Map, you agree to this Privacy Policy.**

Last reviewed: November 2024
Next review: As needed for legal changes
