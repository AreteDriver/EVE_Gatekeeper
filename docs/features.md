# EVE Online Mobile Map - Features

## Core Features

### 1. 2D Map Visualization
- Interactive system search and browsing
- Security status color coding (high/low/null sec)
- System information display
- Connected systems visualization
- Region and constellation grouping

### 2. Route Planning
- Shortest path calculation between systems
- Configurable security preferences:
  - Avoid low security systems
  - Avoid null security systems
- Step-by-step route display
- Jump count optimization
- Security status for each waypoint

### 3. Jump Fuel Cost Calculator
- Support for multiple capital ship types:
  - Carriers
  - Dreadnoughts
  - Supercarriers
  - Titans
  - Jump Freighters
- Configurable fuel prices
- Total fuel consumption calculation
- ISK cost estimation
- Fuel per jump breakdown

### 4. zkillboard Intel Integration
- Recent kill data for any system
- Danger rating system:
  - Safe (green) - Few or no kills
  - Moderate (yellow) - Some activity
  - Dangerous (red) - High activity or high-value kills
- Kill information:
  - Timestamp and recency
  - Ship types destroyed
  - ISK value of kills
  - Number of attackers
  - Solo kills indicator
  - NPC vs player kills
- Real-time data updates
- Pull-to-refresh functionality

### 5. System Search & Information
- Fast system name search
- System details:
  - Security status and classification
  - Number of planets
  - Number of stargates
  - Connected systems
  - Region and constellation
- Quick actions:
  - Plan route from system
  - View intel for system

## Quality of Life Features

### User Experience
- Dark theme optimized for space
- EVE-themed color scheme
- Intuitive navigation with bottom tabs
- Quick search across all screens
- Minimal loading times

### Mobile Optimizations
- Responsive design for all screen sizes
- Touch-friendly interface
- Swipe gestures
- Pull-to-refresh
- Offline-capable architecture (planned)

### Settings & Customization
- Configurable API endpoint
- Default ship type preference
- Default fuel price settings
- Theme customization (planned)
- Notification preferences (planned)

## Planned Features

### v0.2.0
- [ ] Waypoint management (multi-stop routes)
- [ ] Route bookmarking and favorites
- [ ] Offline map caching
- [ ] Push notifications for intel updates
- [ ] Corporation/Alliance tracking

### v0.3.0
- [ ] Advanced map visualization
- [ ] Sovereignty data overlay
- [ ] Jump clone locations
- [ ] Asset tracking
- [ ] Market data integration

### v0.4.0
- [ ] Fleet operations support
- [ ] Shared waypoints
- [ ] Live location tracking
- [ ] Combat timer tracking
- [ ] Citadel database

## Technical Features

### Backend API
- RESTful API design
- Fast route calculation using NetworkX
- ESI API integration for real-time data
- zkillboard API integration
- Efficient caching system
- Rate limiting compliance

### Mobile App
- React Native for cross-platform support
- Expo for rapid development
- React Navigation for routing
- Material Design components
- TypeScript support (planned)

### Performance
- Optimized graph algorithms
- Client-side caching
- Lazy loading of data
- Background data updates
- Memory-efficient rendering

### Security
- HTTPS support
- No credential storage
- Rate limit protection
- Input validation
- XSS protection

## Data Sources

### EVE ESI API
- System information
- Region and constellation data
- Stargate connections
- Security status
- Astronomical data

### zkillboard API
- Kill data
- Loss data
- Activity metrics
- Ship type information
- ISK values

## Use Cases

### Capital Ship Navigation
1. Search for destination system
2. Plan route from current location
3. Configure to avoid hostile space
4. Calculate fuel requirements
5. Check intel for each waypoint
6. Execute jump sequence

### Intel Gathering
1. Search for target system
2. View recent kill activity
3. Assess danger level
4. Plan safe route if needed
5. Monitor for changes

### Trading & Logistics
1. Plan routes between trade hubs
2. Calculate jump freighter costs
3. Optimize for profit margins
4. Check route safety

### Exploration
1. Find systems by security status
2. Plan exploration routes
3. Avoid dangerous areas
4. Track connected systems

## Integration Possibilities

### Future Integrations
- Discord bot for sharing routes
- In-game browser support
- Integration with fitting tools
- Connection to killboard trackers
- Alliance intel databases