# EVE Map - How to Create & Refine UI/UX Mockups

Complete guide to creating, prototyping, and sharing your app mockups.

---

## What's Already Generated For You

You currently have 6 visual assets in the `/home/user/evemap/` directory:

1. **starmap_visualization.png** - Interactive starmap visualization
2. **app_layouts.png** - Phone screen mockups (all 4 tabs)
3. **design_system.png** - Colors, typography, components
4. **data_flow.png** - System architecture
5. **UI_MOCKUPS.txt** - ASCII wireframes
6. **UI_UX_GUIDE.md** - Design specification document

These are production-ready and can be used immediately for:
- Sharing with stakeholders
- Reference during development
- Design team collaboration
- QA testing validation

---

## Option 1: Using Figma (Recommended for Teams)

### Step 1: Create a Free Figma Account

```
1. Go to https://www.figma.com
2. Sign up (free tier included)
3. Create new project: "EVE Map UI"
```

### Step 2: Import Your Mockups

**Method A: Upload PNG Mockups**
```
1. File → Import → Select starmap_visualization.png
2. File → Import → Select app_layouts.png
3. File → Import → Select design_system.png
4. File → Import → Select data_flow.png
5. Organize into frames (1 per screen)
```

**Method B: Create From Scratch Using Specs**
```
1. Create artboard 375×812px (iPhone size)
2. Add rectangle for phone frame
3. Create 4 frames (Map, Routes, Capital, Settings)
4. Use UI_UX_GUIDE.md for component sizes
```

### Step 3: Build Design System in Figma

```
Create Figma Components:
├── Colors
│   ├── HighSec (#00FF00)
│   ├── LowSec (#FFAA00)
│   ├── NullSec (#FF0000)
│   ├── Primary (#2196F3)
│   └── ...
├── Typography
│   ├── Headline Large (32px, Bold)
│   ├── Title Medium (16px, Bold)
│   ├── Body Medium (14px)
│   └── Label Small (12px)
└── Components
    ├── Button/Filled
    ├── Button/Outlined
    ├── Card/System
    ├── Card/Route
    ├── Input/Text
    └── Badge/Status
```

### Step 4: Create Interactive Prototypes

```
1. In Figma, select a button
2. Right panel → Prototype tab
3. Click "+" → Connect to next frame
4. Set interaction: "On click" → "Navigate to"
5. Repeat for all navigation elements
6. Share prototype link with team
```

### Step 5: Share With Team

```
1. Top right → Share button
2. Select "Anyone with link"
3. Copy link
4. Share with:
   - Developers (reference)
   - Designers (collaboration)
   - Stakeholders (feedback)
   - QA team (testing)
```

**Figma Benefits:**
- ✅ Real-time collaboration
- ✅ Component library reusable
- ✅ Handoff code for developers
- ✅ Version history
- ✅ Comments/feedback
- ✅ Interactive prototypes

---

## Option 2: Using Adobe XD

### Quick Setup

```
1. Install Adobe XD (free tier available)
2. New document: 375px × 812px (iPhone)
3. Import PNG mockups as background layers
4. Redraw UI elements on top
5. Create components for reuse
6. Build prototype with interactions
7. Share link for review
```

**XD Features:**
- Similar to Figma
- Good for Adobe Suite users
- Voice prototyping
- Live collaboration

---

## Option 3: Using Sketch (Mac Only)

### Setup for Mac Users

```
1. Install Sketch ($199 or subscription)
2. Create new artboard: iPhone 14 Pro (390×844)
3. Import PNG mockups
4. Create symbols (Sketch's components)
5. Use plugins:
   - Zeplin for handoff
   - InVision for prototyping
```

**Sketch Benefits:**
- Industry standard for UI design
- Powerful plugins ecosystem
- Great for iOS design
- Handoff specs for developers

---

## Option 4: Wireframing Tools

### Using Balsamiq (Quick & Simple)

```
1. Go to https://balsamiq.cloud
2. Create new project
3. Drag components from library:
   - Search box
   - Button
   - Text input
   - List
   - Card
4. Link screens together
5. Export as PDF
```

**Best for:**
- Quick mockups
- Low-fidelity designs
- Team collaboration
- Client feedback

### Using Miro (Whiteboard)

```
1. Go to https://miro.com
2. Create new board
3. Paste your PNG mockups
4. Add annotations
5. Invite team for feedback
6. Iterate in real-time
```

---

## Option 5: Code-Based Mockups (For Developers)

### Using HTML/CSS Mockups

```bash
# Create an interactive HTML mockup
mkdir mockups
cd mockups
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width">
    <title>EVE Map - UI Mockup</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f5f5f5;
        }

        .phone-frame {
            width: 375px;
            height: 812px;
            margin: 20px auto;
            background: white;
            border: 8px solid black;
            border-radius: 40px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        .status-bar {
            height: 44px;
            background: #333;
            color: white;
            display: flex;
            align-items: center;
            padding: 0 16px;
            font-size: 12px;
        }

        .screen {
            height: calc(812px - 44px - 49px);
            overflow-y: auto;
            padding: 16px;
        }

        .tab-bar {
            height: 49px;
            border-top: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-around;
            align-items: center;
            background: white;
        }

        .header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 16px;
        }

        .search-bar {
            width: 100%;
            height: 44px;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .system-card {
            background: #f5f5f5;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
        }

        .system-name {
            font-weight: bold;
            font-size: 14px;
        }

        .system-id {
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }

        .security-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            color: white;
            margin-top: 4px;
        }

        .hs { background: #00ff00; }
        .ls { background: #ffaa00; }
        .ns { background: #ff0000; }

        .button {
            width: 100%;
            height: 48px;
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 16px;
        }

        .button:active {
            background: #1976d2;
        }
    </style>
</head>
<body>
    <div class="phone-frame">
        <div class="status-bar">9:41</div>

        <div class="screen">
            <div class="header">Map Search</div>

            <input type="text" class="search-bar" placeholder="🔍 Search Systems">

            <div class="system-card">
                <div class="system-name">Jita IV - Moon 4</div>
                <div class="system-id">ID: 30000142</div>
                <div class="security-badge hs">HS (5.0)</div>
            </div>

            <div class="system-card">
                <div class="system-name">Perimeter</div>
                <div class="system-id">ID: 30000144</div>
                <div class="security-badge hs">HS (5.0)</div>
            </div>

            <div class="system-card">
                <div class="system-name">Urlen</div>
                <div class="system-id">ID: 30002060</div>
                <div class="security-badge ls">LS (0.4)</div>
            </div>
        </div>

        <div class="tab-bar">
            <div>🗺️ Map</div>
            <div>🛣️ Routes</div>
            <div>🚀 Capital</div>
            <div>⚙️ Settings</div>
        </div>
    </div>
</body>
</html>
EOF

# Open in browser
open index.html
```

**Code Mockup Benefits:**
- ✅ Interactive (click buttons, type text)
- ✅ Responsive design testable
- ✅ Close to actual app behavior
- ✅ Easy to iterate
- ✅ Can convert to real code later

---

## Option 6: Screenshot-Based Mockups

### Once Apps Are Built

```bash
# iOS
1. Run app in Xcode simulator
2. Cmd + S to save screenshot
3. Cmd + Shift + 4 for screen capture
4. Organize in folder: screenshots/ios/

# Android
1. Run app in Android Studio emulator
2. Click camera icon in emulator controls
3. Screenshots saved to ~/Android/Sdk/...
4. Organize in folder: screenshots/android/
```

### Create Mockup Showcase

```
Create marketing image:
1. Take 4-5 screenshots from each platform
2. Use mockup generator: https://mockup.cloud
3. Add phone bezel frames
4. Arrange in grid
5. Add marketing text overlay
```

---

## Step-by-Step: Create Figma Mockup (Easiest)

### 1. Set Up Figma File (10 minutes)

```
1. Go to figma.com → Sign up (free)
2. Create new project: "EVE Map UI"
3. Create new file: "App Screens"
4. File → Import → Upload app_layouts.png
```

### 2. Create Base Frames (10 minutes)

```
1. Create 4 frames (375×812px each):
   - Frame 1: "Map Search"
   - Frame 2: "Route Planner"
   - Frame 3: "Capital Planner"
   - Frame 4: "Settings"

2. Create color group:
   - Create color variables from design_system.png
   - HighSec: #00FF00
   - LowSec: #FFAA00
   - NullSec: #FF0000
   - Primary: #2196F3
```

### 3. Design System (20 minutes)

```
1. Create components page
2. Build components:
   ├── SystemCard (reusable)
   ├── Button/Primary
   ├── Button/Secondary
   ├── Input/Text
   ├── Badge/Security
   └── Card/Result

3. Create typography styles:
   ├── Headline Large
   ├── Title Medium
   ├── Body Medium
   └── Label Small
```

### 4. Build Screens (30 minutes)

```
For each screen (Map, Routes, Capital, Settings):
1. Create header (blue bar, 44px)
2. Add content area
3. Add status/navigation bar (49px)
4. Use components from library
5. Apply colors and typography
```

### 5. Add Interactions (15 minutes)

```
1. Select button on Map screen
2. Right panel → Prototype
3. Click "+" → Connect to Routes screen
4. Repeat for all navigation
5. Set transition: "Dissolve" (300ms)
```

### 6. Share Link (5 minutes)

```
1. Top right → Share button
2. Copy link
3. Send to team/stakeholders
4. Can view in browser on phone!
```

**Total Time: ~90 minutes**

---

## Comparison Table: Which Tool?

| Tool | Ease | Cost | Collaboration | Prototyping | Best For |
|------|------|------|---|---|---|
| **Figma** | ⭐⭐⭐⭐⭐ | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Teams, Designers |
| **Adobe XD** | ⭐⭐⭐⭐ | Paid | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Adobe users |
| **Sketch** | ⭐⭐⭐ | Paid | ⭐⭐⭐ | ⭐⭐⭐⭐ | Mac users |
| **Balsamiq** | ⭐⭐⭐⭐⭐ | Paid | ⭐⭐⭐ | ⭐⭐⭐ | Quick mockups |
| **Miro** | ⭐⭐⭐⭐ | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Team feedback |
| **HTML/CSS** | ⭐⭐⭐ | Free | ⭐⭐ | ⭐⭐⭐⭐ | Dev teams |

**Recommendation: Figma** (free, best collaboration, interactive prototypes)

---

## Using Your Existing Assets

### Quick Win: Present PNG Mockups Directly

```
1. Open starmap_visualization.png
   → Show stakeholders the map visualization
   → Explain route planning visual

2. Open app_layouts.png
   → Show all 4 screens at once
   → Discuss user flow
   → Get feedback on layout

3. Open design_system.png
   → Explain colors (security coding)
   → Typography standards
   → Component library

4. Share UI_UX_GUIDE.md
   → Technical specs for developers
   → Accessibility requirements
   → Component sizes
```

### No Tool Needed:
- ✅ Screenshots look professional
- ✅ Complete design system included
- ✅ Ready to share immediately
- ✅ Can be embedded in documentation

---

## Best Practices for UI Mockups

### 1. Create a Design System First
```
✓ Define colors (with code)
✓ Define typography (with sizes)
✓ Define spacing (8px grid)
✓ Define components (buttons, cards, etc)
✓ Document in one place
```

### 2. Keep Mockups Updated
```
✓ Version control mockups
✓ Git commit with code changes
✓ Link Figma to GitHub (optional)
✓ Regular design reviews
```

### 3. Use Real Content
```
✓ Real system names (Jita, Perimeter)
✓ Real security statuses
✓ Real jump counts
✓ Real ship names
```

### 4. Test on Actual Devices
```
✓ Run on iPhone (actual size: 375×812)
✓ Run on Android (actual size: varies)
✓ Test touch targets (min 48dp)
✓ Verify color contrast (WCAG AA)
```

### 5. Get Feedback Early
```
✓ Share mockups with stakeholders
✓ Collect feedback
✓ Iterate quickly
✓ Build consensus
```

---

## Sharing Your Mockups

### For Developers
```
Share:
1. UI_UX_GUIDE.md (design specs)
2. design_system.png (colors/fonts)
3. Figma link (interactive reference)

They use for:
- Component sizing
- Color values
- Typography rules
- Layout breakpoints
```

### For Stakeholders
```
Share:
1. app_layouts.png (what it looks like)
2. Figma prototype link (clickable demo)
3. UI_MOCKUPS.txt (text description)

They use for:
- Understanding concept
- Providing feedback
- Approval/sign-off
- Demo to others
```

### For QA Team
```
Share:
1. Figma prototype (visual reference)
2. UI_UX_GUIDE.md (accessibility checklist)
3. design_system.png (color/spacing guide)

They use for:
- Testing against specs
- Verifying colors
- Checking spacing
- Accessibility validation
```

---

## Tools Installation Guide

### Figma (Recommended)

```bash
# No installation needed!
# Just go to https://www.figma.com and sign up

# Optional: Install Figma desktop app
brew install figma  # macOS
# or download from figma.com/downloads
```

### HTML Mockup Setup

```bash
# Create interactive mockup locally
mkdir -p evemap-mockups
cd evemap-mockups

# Copy the HTML template from MOCKUP_GUIDE.md
# Save as index.html

# Open in browser
open index.html  # macOS
# or drag into Firefox/Chrome
```

### Sketch (Mac Only)

```bash
# Install via App Store or direct download
# 1. Go to sketch.com
# 2. Download Sketch
# 3. Install to Applications
# 4. Create new document
```

---

## Next Steps

### Immediate (Today)
1. ✅ Use existing PNGs + guides (already done!)
2. Choose sharing method (email, Figma link, etc)
3. Share with stakeholders/team

### This Week
1. Create Figma file (optional but recommended)
2. Build interactive prototype
3. Share clickable demo link
4. Collect feedback
5. Iterate design

### Before Development
1. Get design sign-off
2. Export specs for developers
3. Create component library
4. Document edge cases

---

## File Organization

### Save in Your Project

```
evemap/
├── mockups/                    # UI mockup files
│   ├── figma-link.txt         # URL to Figma file
│   ├── screenshots/
│   │   ├── ios/
│   │   │   ├── map-search.png
│   │   │   ├── route-planner.png
│   │   │   ├── capital-planner.png
│   │   │   └── settings.png
│   │   └── android/
│   │       └── (same 4 screens)
│   ├── html-mockup/
│   │   └── index.html          # Interactive mockup
│   └── prototype/
│       └── README.md           # Prototype testing guide
│
└── docs/
    └── UI_UX_GUIDE.md         # Design specifications
```

---

## Troubleshooting

### "The PNG mockups look fake/simple"
**Solution:** They're meant to be! They show:
- Layout and flow
- Information hierarchy
- Color scheme
- User interactions

Once built, real app screenshots will look amazing.

### "I want to customize colors"
**Solution:** Use Figma
1. Upload PNG as background
2. Draw rectangles in new colors
3. Adjust colors in Figma
4. Export updated PNG

### "How do I get feedback?"
**Solution:** Share Figma link
1. Share → Copy link
2. Send to stakeholders
3. They can comment directly
4. You iterate based on feedback

### "Can I make it interactive?"
**Solution:** Use Figma prototypes
1. Create screens in Figma
2. Prototype tab → Click "+"
3. Connect screens
4. Set transitions
5. Share interactive link

---

## Example: 30-Minute Figma Setup

```
Timeline:
├─ 0-5 min: Sign up to Figma
├─ 5-10 min: Create project & frames
├─ 10-20 min: Set up colors & typography
├─ 20-25 min: Add mockup images as reference
├─ 25-28 min: Build 1 interactive screen
└─ 28-30 min: Share link with team

Result: Clickable prototype ready for feedback
```

---

## You're Ready!

Your existing mockups are **production-ready** for:
- ✅ Sharing with stakeholders
- ✅ Reference during development
- ✅ QA testing validation
- ✅ Design handoff documentation

**Optional next steps:**
- Create Figma file for interactivity
- Build HTML mockup for testing
- Get team feedback
- Iterate design

All tools are free or have free tiers. Start with Figma (easiest) and iterate from there!

---

**Pick your favorite tool and start creating! 🎨**
