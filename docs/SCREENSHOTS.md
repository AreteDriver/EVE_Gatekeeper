# Mobile App Screenshots and Demo

## App Screens Overview

### 1. Map Screen (System Search)

**Features:**
- Search bar for finding systems
- System search results with security status
- Detailed system information card
- Quick action buttons (Plan Route, View Intel)

**UI Elements:**
- Dark space-themed background (#0A0E27)
- Security color coding (blue/orange/red)
- Clean card-based layout
- Touch-friendly buttons

---

### 2. Route Planning Screen

**Features:**
- Origin and destination selection
- Security preference toggles
- Route calculation with step-by-step display
- Fuel cost calculator

**Route Display:**
- Jump number for each system
- System name and security status
- Color-coded security levels
- Total jump count

**Fuel Calculator:**
- Ship type selection
- Fuel per jump
- Total fuel required
- Total ISK cost
- Configurable fuel prices

---

### 3. Intel Screen (zkillboard)

**Features:**
- System search for intel lookup
- Recent kills display
- Danger rating indicator
- Kill details (value, time, attackers)
- Pull-to-refresh functionality

**Kill Information:**
- Time since kill (e.g., "2h ago")
- Ship type ID
- ISK value (formatted: 1.5B, 200M, etc.)
- Number of attackers
- Solo/NPC indicators

**Danger Ratings:**
- 🟢 Safe (green) - Few or no kills
- 🟡 Moderate (yellow) - Some activity
- 🔴 Dangerous (red) - High activity

---

### 4. Settings Screen

**Configuration Options:**
- API endpoint URL
- Default ship type
- Default fuel price
- Dark mode toggle
- Notifications preferences
- Auto-refresh settings

**App Information:**
- Version number
- Developer info
- Data sources
- Clear cache button

---

## User Flows

### Flow 1: Quick Route Planning

1. Open app → Map tab
2. Search "Jita"
3. Tap "Jita" in results
4. Tap "Plan Route" button
5. Search destination "Amarr"
6. Toggle "Avoid Null Sec" if needed
7. Tap "Calculate Route"
8. View route and fuel costs

**Time:** ~30 seconds

---

### Flow 2: Intel Gathering

1. Open app → Intel tab
2. Search for system
3. Select system from results
4. View danger rating
5. Scroll through recent kills
6. Pull down to refresh
7. Check kill values and times

**Time:** ~20 seconds

---

### Flow 3: Multi-Jump Route with Fuel

1. Route tab
2. Enter origin system
3. Enter destination
4. Set ship type to "Carrier"
5. Calculate route
6. Review step-by-step route
7. Check fuel requirements
8. Note total ISK cost

**Time:** ~45 seconds

---

## Demo Script

### Opening Scene
"Welcome to EVE Online Mobile Map - your pocket navigation tool for New Eden!"

### Map Screen Demo
"Search for any system in EVE Online. Here I'm searching for Jita, the main trade hub."
- Type "Jita" in search
- Show results appearing
- Tap Jita to show details
- Highlight security status, planets, stargates

### Route Planning Demo
"Need to get from Jita to Amarr? Let's plan the safest route."
- Show origin/destination selection
- Toggle "Avoid Null Sec"
- Calculate route
- Show step-by-step route with 8 jumps
- Display fuel costs: "600 fuel units = 300,000 ISK"

### Intel Demo
"Before you jump, check the danger level with zkillboard intel."
- Search for a low-sec system
- Show danger rating: "Dangerous"
- Scroll through recent kills
- Point out high-value kills
- "3 kills in the last hour worth 2.5B ISK - maybe avoid this route!"

### Wrap Up
"Plan routes, calculate fuel, check intel - all in your pocket. Available for iOS and Android."

---

## Key Selling Points

### For Pilots
✓ Plan routes on the go
✓ Avoid dangerous systems
✓ Calculate fuel costs accurately
✓ Real-time intel updates
✓ No need for desktop

### For Logistics
✓ Jump freighter fuel calculations
✓ Route optimization
✓ Security filtering
✓ ISK cost tracking

### For PvP
✓ zkillboard integration
✓ System activity monitoring
✓ Danger ratings
✓ Recent kills tracking

---

## Technical Highlights

- **Cross-platform**: iOS, Android, Web
- **Offline capable**: Cached data (planned)
- **Real-time data**: EVE ESI + zkillboard APIs
- **Fast**: Optimized pathfinding
- **Free**: Open source, no subscriptions

---

## Screenshots Checklist

For marketing/documentation:

- [ ] Map screen with search results
- [ ] System details card
- [ ] Route planning screen with route
- [ ] Fuel cost calculator display
- [ ] Intel screen with kills
- [ ] Danger rating indicators
- [ ] Settings screen
- [ ] Dark theme showcase
- [ ] Security color coding
- [ ] Mobile responsive views

---

## Video Demo Script (30 seconds)

0:00 - Show app launch
0:03 - Quick system search (Jita)
0:06 - Tap "Plan Route"
0:09 - Enter destination, calculate
0:15 - Show route with jumps
0:18 - Show fuel costs
0:21 - Switch to Intel tab
0:24 - Show danger rating and kills
0:27 - "EVE Map - Navigate New Eden"
0:30 - End with logo/download

---

## Tips for Screenshots

1. **Use high-quality displays** - Retina/4K preferred
2. **Show realistic data** - Use actual EVE systems
3. **Highlight key features** - Circle or arrow annotations
4. **Keep UI clean** - No debug info or errors
5. **Use dark theme** - Matches EVE aesthetic
6. **Show color coding** - Security status colors visible
7. **Include branding** - App name visible

---

## Platform-Specific Notes

### iOS
- Show in iPhone frame
- Use iOS status bar
- Native navigation gestures
- Dark mode support

### Android
- Material Design compliance
- Bottom navigation
- System back button
- Various screen sizes

### Web
- Responsive layout
- Desktop browser view
- Keyboard shortcuts
- Mouse hover states
