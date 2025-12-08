# EVE Online Mobile Map - MVP Plan

## Overview
Build a cross-platform mobile application for EVE Online featuring route planning, jump fuel calculations, and zkillboard intel gathering.

## MVP Deliverables

### Phase 1: Backend API (✅ Complete)
- [x] REST API server using Flask
- [x] ESI API integration for system data
- [x] zkillboard API integration
- [x] Route calculation endpoints
- [x] Fuel cost calculation
- [x] System search functionality
- [x] CORS support for mobile app

### Phase 2: Mobile App Foundation (✅ Complete)
- [x] React Native/Expo project setup
- [x] Navigation structure (tabs)
- [x] API service layer
- [x] Theme and styling
- [x] Basic component library

### Phase 3: Core Screens (✅ Complete)
- [x] Map/Search Screen
  - System search
  - System details display
  - Quick actions
- [x] Route Planning Screen
  - Origin/destination selection
  - Route calculation
  - Security preferences
  - Fuel cost display
- [x] Intel Screen
  - zkillboard data display
  - Danger ratings
  - Kill information
  - Refresh capability
- [x] Settings Screen
  - API configuration
  - Preferences
  - About information

### Phase 4: Testing & Refinement
- [ ] Backend API testing
- [ ] Mobile app testing on devices
- [ ] Performance optimization
- [ ] Bug fixes
- [ ] Documentation updates

### Phase 5: Deployment
- [ ] Backend deployment guide
- [ ] Mobile app build for Android
- [ ] Mobile app build for iOS
- [ ] App store submission (optional)
- [ ] User documentation

## Success Criteria

### Functional Requirements
✅ Users can search for EVE Online systems
✅ Users can view detailed system information
✅ Users can calculate routes between systems
✅ Routes can avoid low/null security systems
✅ Users can calculate jump fuel costs
✅ Users can view zkillboard intel
✅ App provides danger ratings
✅ App works on iOS and Android

### Non-Functional Requirements
✅ Mobile-friendly interface
✅ Fast search and navigation
✅ Real-time data from ESI/zkillboard
- Production-ready deployment
- Comprehensive documentation

## Technical Architecture

### Backend Stack
- **Python 3.8+**
- **Flask** - Web framework
- **NetworkX** - Graph algorithms
- **Requests** - HTTP client
- **Flask-CORS** - Cross-origin support

### Frontend Stack
- **React Native** - Mobile framework
- **Expo** - Development platform
- **React Navigation** - Routing
- **React Native Paper** - UI components
- **Axios** - HTTP client

### APIs
- **EVE ESI API** - Official EVE data
- **zkillboard API** - Kill data

## Key Features Implemented

1. **System Search & Details**
   - Fast search by name
   - Security status display
   - Planet and stargate counts
   - Connected systems list

2. **Route Planning**
   - Shortest path calculation
   - Security filtering
   - Step-by-step routes
   - Jump count display

3. **Fuel Calculator**
   - Multiple ship types
   - Configurable fuel prices
   - Total cost calculation
   - Per-jump breakdown

4. **Intel Integration**
   - Recent kills display
   - Danger ratings
   - Kill values
   - Time since kill
   - NPC/Player indicators

## Next Steps

### Short Term
1. Test backend API with real data
2. Test mobile app on physical devices
3. Fix any bugs or issues
4. Add loading states and error handling
5. Optimize performance

### Medium Term
1. Add route bookmarking
2. Implement offline caching
3. Add waypoint management
4. Create push notifications
5. Improve map visualization

### Long Term
1. Add sovereignty overlay
2. Fleet operations support
3. Corporation tracking
4. Asset management
5. Market data integration

## Deployment Plan

### Backend Deployment
1. Choose hosting provider (AWS, Heroku, DigitalOcean)
2. Set up production environment
3. Configure environment variables
4. Set up monitoring and logging
5. Deploy API server

### Mobile Deployment
1. Build Android APK
2. Build iOS IPA (requires Apple Developer account)
3. Test on multiple devices
4. Submit to app stores (optional)
5. Create landing page

## Timeline Estimates

- Backend API: ✅ Complete (2-3 days)
- Mobile App Core: ✅ Complete (3-4 days)
- Testing & Refinement: 2-3 days
- Deployment: 1-2 days
- **Total MVP: ~10 days**

## Resources Required

### Development
- Python backend developer
- React Native developer
- UI/UX designer (optional)

### Infrastructure
- Backend hosting ($5-20/month)
- Domain name (optional)
- SSL certificate (Let's Encrypt free)

### Tools
- Code editor (VS Code)
- Git version control
- Expo development tools
- ESI API access (free)
- zkillboard API access (free)

## Risk Mitigation

### Technical Risks
- **API rate limits**: Implement caching
- **Data freshness**: Use ESI cache headers
- **Performance**: Optimize route calculations
- **Mobile compatibility**: Test on multiple devices

### Business Risks
- **API changes**: Monitor ESI/zkillboard updates
- **User adoption**: Focus on core features
- **Maintenance**: Plan for ongoing support

## Success Metrics

### User Engagement
- Daily active users
- Route calculations per day
- Intel lookups per day
- Average session duration

### Technical Metrics
- API response times
- App crash rate
- Load times
- User retention

## Conclusion

The MVP is largely complete with all core features implemented. The focus now shifts to testing, refinement, and deployment to make the app available to EVE Online players.