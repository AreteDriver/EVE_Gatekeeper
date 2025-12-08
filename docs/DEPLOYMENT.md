# Deployment Guide

This guide covers deploying both the backend API and mobile app to production.

## Backend Deployment

### Option 1: Heroku (Easiest)

1. Install Heroku CLI:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. Create a Heroku app:
```bash
cd evemap
heroku create evemap-api
```

3. Add Procfile:
```bash
echo "web: python run_api_server.py --host 0.0.0.0 --port \$PORT" > Procfile
```

4. Deploy:
```bash
git push heroku main
```

5. Set environment variables:
```bash
heroku config:set REGION_ID=10000002
```

**Cost:** Free tier available

---

### Option 2: DigitalOcean App Platform

1. Connect GitHub repository
2. Select "Python" as app type
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `python run_api_server.py --host 0.0.0.0 --port 8080`
5. Deploy

**Cost:** Starting at $5/month

---

### Option 3: AWS EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip
```

4. Clone repository:
```bash
git clone https://github.com/AreteDriver/evemap.git
cd evemap
pip3 install -r requirements.txt
```

5. Run with systemd:
```bash
sudo nano /etc/systemd/system/evemap.service
```

Add:
```ini
[Unit]
Description=EVE Map API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/evemap
ExecStart=/usr/bin/python3 run_api_server.py --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

6. Start service:
```bash
sudo systemctl enable evemap
sudo systemctl start evemap
```

7. Configure nginx reverse proxy:
```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/evemap
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/evemap /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

**Cost:** Starting at $5/month

---

### Option 4: Docker

1. Create Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run_api_server.py", "--host", "0.0.0.0", "--port", "5000"]
```

2. Build image:
```bash
docker build -t evemap-api .
```

3. Run container:
```bash
docker run -p 5000:5000 evemap-api
```

4. Deploy to any container platform (AWS ECS, Google Cloud Run, etc.)

---

## Mobile App Deployment

### Option 1: Expo Application Services (EAS)

**For Android:**

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Login to Expo:
```bash
eas login
```

3. Configure build:
```bash
cd mobile-app
eas build:configure
```

4. Build APK:
```bash
eas build --platform android --profile preview
```

5. Download APK and distribute

**For iOS:**

1. Enroll in Apple Developer Program ($99/year)

2. Build IPA:
```bash
eas build --platform ios
```

3. Submit to App Store:
```bash
eas submit --platform ios
```

---

### Option 2: Local Build

**Android APK:**

1. Install Android Studio and SDK

2. Build locally:
```bash
cd mobile-app
npx expo prebuild
cd android
./gradlew assembleRelease
```

3. APK location: `android/app/build/outputs/apk/release/`

**iOS IPA:**

1. Install Xcode (macOS only)

2. Build locally:
```bash
cd mobile-app
npx expo prebuild
cd ios
pod install
xcodebuild -workspace YourApp.xcworkspace -scheme YourApp -configuration Release
```

---

### Option 3: Web Deployment

1. Build web app:
```bash
cd mobile-app
npx expo export:web
```

2. Deploy to static hosting:
   - **Netlify**: Drag & drop `web-build` folder
   - **Vercel**: Connect GitHub repo
   - **GitHub Pages**: Push to `gh-pages` branch
   - **Firebase Hosting**: Use Firebase CLI

**Example (Netlify):**
```bash
npm install -g netlify-cli
netlify deploy --dir=web-build --prod
```

---

## Configuration

### Backend Environment Variables

```bash
# .env file
REGION_ID=10000002
HOST=0.0.0.0
PORT=5000
DEBUG=False
```

### Mobile App Configuration

Update `mobile-app/src/services/api.js`:
```javascript
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://your-api.com/api';
```

Create `mobile-app/.env`:
```bash
EXPO_PUBLIC_API_URL=https://your-api.com/api
```

---

## SSL/HTTPS Setup

### Using Let's Encrypt (Free)

1. Install certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Get certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

3. Auto-renewal:
```bash
sudo certbot renew --dry-run
```

---

## Monitoring & Logging

### Backend Monitoring

**Option 1: Built-in logging**
```python
import logging
logging.basicConfig(level=logging.INFO, filename='app.log')
```

**Option 2: Sentry**
```bash
pip install sentry-sdk[flask]
```

Add to `api.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
)
```

### Mobile App Monitoring

**Expo Analytics:**
```bash
npm install expo-analytics
```

---

## Performance Optimization

### Backend

1. **Enable caching:**
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

2. **Use production server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'evemap.api:app'
```

3. **Database for data:**
Consider PostgreSQL for persistent storage instead of in-memory

### Mobile App

1. **Optimize images:**
```bash
npm install -g expo-optimize
expo-optimize
```

2. **Enable Hermes:**
Update `app.json`:
```json
{
  "expo": {
    "jsEngine": "hermes"
  }
}
```

---

## Security Checklist

- [ ] Use HTTPS for API
- [ ] Add API rate limiting
- [ ] Validate all inputs
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable CORS only for your domain
- [ ] Add authentication (future)
- [ ] Monitor for security issues

---

## Cost Estimates

### Minimal Setup (Free Tier)
- Backend: Heroku Free / Railway Free
- Mobile: Expo free tier
- Domain: Optional (~$10/year)
- **Total: $0-10/year**

### Small Scale ($5-20/month)
- Backend: DigitalOcean Droplet $6/month
- Database: Managed PostgreSQL $15/month
- Domain: $10/year
- **Total: ~$20-30/month**

### Production Scale ($50+/month)
- Backend: AWS ECS or similar
- Database: Managed PostgreSQL
- CDN: Cloudflare
- Monitoring: Sentry
- App stores: $99/year (Apple)
- **Total: $50-100+/month**

---

## Maintenance

### Regular Tasks

- Update dependencies monthly
- Monitor API rate limits
- Check error logs weekly
- Backup data regularly
- Test on new OS versions

### Updates

```bash
# Backend
pip install --upgrade -r requirements.txt

# Mobile
cd mobile-app
npm update
expo upgrade
```

---

## Support & Troubleshooting

### Common Issues

**API not accessible:**
- Check firewall rules
- Verify port is open
- Check DNS configuration

**Mobile app can't connect:**
- Update API_BASE_URL
- Check CORS settings
- Verify API is running

**Build failures:**
- Clear cache: `expo start -c`
- Reinstall dependencies
- Check error logs

---

## Next Steps

1. Choose deployment platform
2. Set up domain name
3. Configure SSL
4. Deploy backend
5. Build mobile app
6. Test thoroughly
7. Monitor performance
8. Gather user feedback

---

## Additional Resources

- [Expo Documentation](https://docs.expo.dev)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)
- [AWS Documentation](https://aws.amazon.com/documentation/)
- [Let's Encrypt Guide](https://letsencrypt.org/getting-started/)
