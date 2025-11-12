# EVE Map - UI/UX Design Guide

Complete visual design specification for iOS and Android platforms.

---

## Visual Overview

4 comprehensive design visualizations have been generated:

1. **starmap_visualization.png** - Interactive starmap with route planning
2. **app_layouts.png** - All 4 app screens with actual mobile layouts
3. **design_system.png** - Colors, typography, and UI components
4. **data_flow.png** - System architecture and data flow

---

## Screen Design Specifications

### Screen 1: Map Search

**Purpose:** System search and discovery

**Layout:**
- Header: "EVE Map" with settings icon
- Search bar (full width, centered)
- List of system cards (scrollable)

**Components:**
```
┌─────────────────────┐
│ System Name         │ (Bold, 14px)
│ ID: 30000142        │ (Regular, 12px)
│ Security: 5.0 (HS)  │ (12px, color-coded)
└─────────────────────┘
```

**Color Coding:**
- 🟢 High-Sec (security ≥ 0.5): Green (#00FF00)
- 🟡 Low-Sec (security 0-0.5): Orange (#FFAA00)
- 🔴 Null-Sec (security < 0): Red (#FF0000)

**Interactions:**
- Type to search → Real-time filtering
- Tap system → View details / Select for routing
- Scroll → Load more results

**iOS Implementation:**
```swift
SearchBar(placeholder: "Search Systems")
    .onChange(of: searchQuery) { newValue in
        viewModel.searchSystems(newValue)
    }

ForEach(viewModel.searchResults) { system in
    SystemCard(system: system)
        .onTapGesture { viewModel.selectSystem(system) }
}
```

**Android Implementation:**
```kotlin
OutlinedTextField(
    value = searchQuery,
    onValueChange = { viewModel.searchSystems(it) }
)

LazyColumn {
    items(viewModel.searchResults) { system ->
        SystemCard(system = system)
    }
}
```

---

### Screen 2: Route Planner

**Purpose:** Plan routes between systems with optional constraints

**Layout:**
- Header: "Route Planner"
- Input section: Origin & Destination IDs
- Options section: Avoidance checkboxes
- Action button: "PLAN ROUTE"
- Result section: Route statistics (if available)

**Input Fields:**
```
Origin System ID
┌─────────────────────┐
│ 30000142       [x]  │
└─────────────────────┘

Destination System ID
┌─────────────────────┐
│ 30000144       [x]  │
└─────────────────────┘
```

**Avoidance Options:**
- ☐ Avoid Low-Sec
- ☐ Avoid Null-Sec
- ☐ Avoid Wormholes

**Result Display:**
```
Route: Jita → Isanamo
├─ Total Distance: 0.04 LY
├─ Jumps: 4
└─ Time: ~4 minutes
```

**Colors:**
- Button (Plan Route): Primary Blue (#2196F3)
- Result Box: Success Green (#4CAF50) with light background

---

### Screen 3: Capital Jump Planner

**Purpose:** Plan capital ship jumps with fuel calculations

**Layout:**
- Header: "Capital Jump Planner"
- Ship selector (scrollable list)
- Route inputs (Origin, Destination)
- Skills input (Advanced Spaceship Command 0-5)
- Action button: "PLAN JUMP CHAIN"
- Results section (if available)

**Ship Selection:**
```
Erebus (Titan) - 8.8 LY max range
☑ Nyx (Supercarrier) - 8.75 LY max range  ← Selected
Hel (Carrier) - 7.5 LY max range
Moros (Dread) - 7.5 LY max range
```

15 Total Ships:
- **Titans** (4): Erebus, Leviathan, Avatar, Wyvern
- **Supercarriers** (4): Nyx, Aeon, Vendetta, Wyvern
- **Carriers** (4): Archon, Thanatos, Chimera, Hel
- **Dreadnoughts** (3): Moros, Naglfar, Phoenix, Revelation

**Skills Input:**
```
Advanced Spaceship Command (0-5)
┌─────────────────────┐
│ 5                   │  ← Slider/Input
└─────────────────────┘
```

**Results Display:**
```
Jump Chain Summary
├─ Total Jumps: 4
├─ Distance: 0.04 LY
├─ Fuel: 7.0 units
├─ Refuel Needed: No
└─ Est. Time: 0.07 hours

Jump Legs:
├─ Jita → Perimeter (0.01 LY, ⛽ 1.75)
├─ Perimeter → Sobaseki (0.01 LY, ⛽ 1.75)
├─ Sobaseki → Urlen (0.01 LY, ⛽ 1.75)
└─ Urlen → Isanamo (0.01 LY, ⛽ 1.75)
```

**Fuel Indicator Colors:**
- 🟢 Safe (≤ base capacity): Green
- 🟡 Caution (75-100% capacity): Yellow
- 🔴 Risky (> base capacity): Red

---

### Screen 4: Settings

**Purpose:** Configuration and information

**Layout:**
- Header: "Settings"
- API Configuration section
- Status indicator
- About section
- Documentation links

**Configuration Section:**
```
API URL Configuration

API URL
┌─────────────────────────────────┐
│ https://evemap-api.herokuapp.com │
└─────────────────────────────────┘

┌─────────────────────┐
│  SAVE & CONNECT     │
└─────────────────────┘

API Connection Status
✅ Connected (Last checked: 2 min ago)
🔴 Disconnected (Check URL)
```

**About Section:**
```
EVE Map Visualization
Version: 1.0.0
A 2D starmap viewer for EVE Online

Platforms:
- iOS (Swift + SwiftUI)
- Android (Kotlin + Jetpack Compose)

Powered by ESI API
EVE Online's official data source
```

**Documentation Links:**
- [GitHub Repository]
- [Privacy Policy]
- [API Documentation]

---

## Navigation

### Tab Navigation (Bottom/Top)

**iOS (Top Tab Bar):**
```
[Map] [Routes] [Capital] [Settings]
```

**Android (Bottom Navigation Bar):**
```
  Map    Routes    Capital    Settings
 [icon]  [icon]    [icon]     [icon]
```

### Navigation Flow:
```
┌─────────────────────────────────────┐
│  Map Search                         │
│  - Search for systems               │
│  - View system details              │
│  → Plan route (to Routes tab)      │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  Route Planner                      │
│  - Plan routes                      │
│  - Set avoidance                    │
│  - View statistics                  │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  Capital Planner                    │
│  - Select ship                      │
│  - Input route & skills             │
│  - View jump chain details          │
└─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│  Settings                           │
│  - Configure API                    │
│  - View status                      │
│  - Access docs                      │
└─────────────────────────────────────┘
```

---

## Design System

### Color Palette

**Security Status:**
- High-Sec: `#00FF00` (RGB: 0, 255, 0)
- Low-Sec: `#FFAA00` (RGB: 255, 170, 0)
- Null-Sec: `#FF0000` (RGB: 255, 0, 0)

**UI Colors:**
- Primary: `#2196F3` (Material Blue)
- Success: `#4CAF50` (Material Green)
- Warning: `#FF9800` (Material Orange)
- Background: `#F5F5F5` (Light Gray)
- Text: `#212121` (Dark Gray)

### Typography

**iOS (SwiftUI):**
```swift
// Headlines
.font(.system(size: 32, weight: .bold))  // Headline Large
.font(.system(size: 28, weight: .bold))  // Headline Medium
.font(.system(size: 24, weight: .bold))  // Headline Small

// Titles
.font(.system(size: 16, weight: .semibold))  // Title Medium
.font(.system(size: 14, weight: .semibold))  // Title Small

// Body
.font(.system(size: 14, weight: .regular))   // Body Medium
.font(.system(size: 12, weight: .regular))   // Body Small

// Labels
.font(.system(size: 12, weight: .medium))    // Label Medium
.font(.system(size: 11, weight: .medium))    // Label Small
```

**Android (Compose):**
```kotlin
// Headlines
MaterialTheme.typography.headlineLarge       // 32px, bold
MaterialTheme.typography.headlineSmall       // 24px, bold

// Titles
MaterialTheme.typography.titleMedium         // 16px, semibold
MaterialTheme.typography.titleSmall          // 14px, semibold

// Body
MaterialTheme.typography.bodyMedium          // 14px, regular
MaterialTheme.typography.bodySmall           // 12px, regular

// Labels
MaterialTheme.typography.labelMedium         // 12px, medium
MaterialTheme.typography.labelSmall          // 11px, medium
```

### Spacing Grid (8px base)

```
xs: 8px
sm: 16px (2 × 8px)
md: 24px (3 × 8px)
lg: 32px (4 × 8px)
xl: 48px (6 × 8px)
```

**Common Spacing:**
- Card padding: 16px
- Section spacing: 24px
- Screen padding: 16px
- Component gap: 8px

### Components

**Buttons:**

Filled Button (Primary Action)
```
Height: 48px
Padding: 8px (top/bottom), 24px (left/right)
Border radius: 4px
Background: #2196F3
Text: White, Bold, 14px
```

Outlined Button (Secondary Action)
```
Height: 48px
Padding: 8px (top/bottom), 24px (left/right)
Border radius: 4px
Background: White
Border: 2px #2196F3
Text: #2196F3, Bold, 14px
```

**Cards:**

System Card / Jump Leg Card
```
Height: Auto (≥ 80px)
Padding: 16px
Border radius: 8px
Background: #FAFAFA
Border: 1px #EEEEEE
Shadow: Elevation 1-2
```

**Input Fields:**

Text Field / Number Input
```
Height: 48px
Padding: 12px horizontal
Border radius: 4px
Background: #F5F5F5 (inactive) / White (active)
Border: 1px #CCCCCC (inactive) / 2px #2196F3 (active)
Text: 14px
Placeholder: 12px, #999999
```

**Status Indicators:**

Connected Status
```
Badge Style:
├─ Background: #4CAF50
├─ Text: White
├─ Padding: 4px 8px
├─ Border radius: 4px
└─ Font: 12px, semibold
```

---

## Responsive Design

### Mobile (iOS / Android)
- Portrait: Full width minus padding (16px each side)
- Landscape: Full width with adjusted layout
- Min width: 320px (older devices)
- Max width: 480px (typical mobile)

### Tablet Support
- iPad: Split-view navigation possible
- Wider screens: Content can expand to 600px

### Orientation Handling

**Portrait:**
- Full-height scrollable content
- Bottom tab navigation
- Single-column layout

**Landscape:**
- Reduced vertical space
- Content cards may be side-by-side
- Tab navigation may move to side

---

## Accessibility

### Color Contrast
- Minimum WCAG AA: 4.5:1 ratio
- Security status colors tested for colorblind users
- Alternative icons in addition to color

### Touch Targets
- Minimum 48dp × 48dp for buttons
- 56px minimum for touch targets
- Spacing between interactive elements: ≥ 8px

### Text
- Minimum font size: 12px
- Line height: 1.5x font size
- Text scaling supported (up to 200%)

### Keyboard Navigation
- Tab order logical and sequential
- Return/Enter to confirm actions
- Escape to cancel

---

## Animations & Transitions

### Page Transitions
- Duration: 300ms
- Easing: Material easing (ease-in-out)
- Direction: Horizontal slide (next screen)

### Loading States
```
Initial Load:
├─ Show spinner for API calls
├─ Disable buttons during load
└─ Show error snackbar if fails

Search Results:
├─ Fade in results as they load
├─ Clear previous results on new search
└─ Smooth scroll to top
```

### State Feedback
- Button press: Color darken (50ms)
- Card tap: Elevation increase
- Success: Green checkmark animation (300ms)
- Error: Red shake animation (400ms)

---

## Error States

### API Connection Error
```
Connection Error
┌──────────────────────────┐
│ Cannot connect to API    │
│ Check your API URL       │
│                          │
│  [RETRY]  [SETTINGS]     │
└──────────────────────────┘
```

### Empty States

Search with no results:
```
No systems found
Try a different search query

[Suggestions]
- Popular: Jita, Perimeter
- Recent: (none yet)
```

No route found:
```
Route Not Found
The selected systems are not connected
or the route is blocked by avoidance options

[ADJUST OPTIONS]
```

---

## Platform-Specific Details

### iOS (SwiftUI)

**Safe Areas:**
- Notch/island handling
- Home indicator (bottom)
- Status bar (top)

**Gestures:**
- Swipe back to previous screen
- Long-press for context menus
- Pull-to-refresh on lists

**Haptics:**
- Light impact on button press
- Success feedback on route planning
- Warning feedback on errors

### Android (Jetpack Compose)

**System UI:**
- Navigation bar handling
- Status bar theming
- Back button handling (app navigation)

**Gestures:**
- Back button to navigate
- Long-press for options
- Swipe actions on cards (optional)

**Material Design:**
- Bottom app bar for navigation
- FAB for primary action (optional)
- Snackbars for notifications

---

## Testing Checklist

- [ ] All text readable at 12pt minimum
- [ ] All buttons at least 48dp × 48dp
- [ ] Color contrast meets WCAG AA
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Works on screen sizes 320px - 480px width
- [ ] Landscape orientation supported
- [ ] API error states handled
- [ ] Loading states show feedback
- [ ] Empty states are helpful
- [ ] Animations don't distract (< 500ms)

---

## Files Generated

1. **UI_MOCKUPS.txt** - ASCII mockups of each screen
2. **starmap_visualization.png** - Interactive starmap visuals
3. **app_layouts.png** - Phone screen layouts (all 4 tabs)
4. **design_system.png** - Colors, typography, components
5. **data_flow.png** - System architecture diagram
6. **UI_UX_GUIDE.md** - This comprehensive guide

---

## Next Steps

1. **For iOS:** Use these designs as reference when building in Xcode
2. **For Android:** Use Material 3 theme builder with provided colors
3. **For Designers:** Export designs to Figma for team collaboration
4. **For Developers:** Reference specific component specs when coding
5. **For QA:** Use testing checklist to validate implementation

---

**Your EVE Map app is ready for visual implementation! 🎨**
