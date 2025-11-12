# Cloud Deployment Guide - EVE Map Backend

Deploy your EVE Map API backend to production for your iOS app.

## Quick Start (Choose One)

### 1. **Heroku** (Recommended for beginners)
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create evemap-api-prod
git push heroku main
# Done! Your app is live

# Get your URL:
heroku open
# App URL: https://evemap-api-prod.herokuapp.com
```

### 2. **AWS** (More control, slightly more complex)
### 3. **DigitalOcean** (Middle ground, easy UI)

---

## Option 1: Heroku Deployment

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- Git installed

### Steps

#### 1. Create Heroku App

```bash
heroku login
heroku create evemap-api-prod
```

This creates a unique app: `evemap-api-prod.herokuapp.com`

#### 2. Add Procfile

Create file: `Procfile` (no extension)

```
web: python scripts/run_api.py
release: python scripts/init_universe.py
```

#### 3. Add Buildpack

```bash
heroku buildpacks:add heroku/python
```

#### 4. Set Environment Variables

```bash
heroku config:set DATABASE_URL="sqlite:///data/universe.db"
heroku config:set LOG_LEVEL="info"
```

#### 5. Deploy

```bash
git push heroku main
```

#### 6. Initialize Universe (First Time Only)

```bash
heroku run "python scripts/init_universe.py" --exit-code
```

#### 7. Verify

```bash
heroku open
# or manually visit: https://evemap-api-prod.herokuapp.com/docs
```

### Cost

- **Free Tier:** Sleeps after 30 min inactivity (not ideal for production)
- **Paid:** $7/month (Eco Dyno - always on)

---

## Option 2: AWS Deployment

### Setup (15 minutes)

#### 1. Create ECR Repository

```bash
aws ecr create-repository --repository-name evemap-api
```

#### 2. Build & Push Docker Image

```bash
# Build for ARM64 (Graviton2, cheaper)
docker buildx build --platform linux/arm64 \
  -t evemap-api:latest .

# Tag with ECR URI
docker tag evemap-api:latest \
  [YOUR-ACCOUNT].dkr.ecr.[REGION].amazonaws.com/evemap-api:latest

# Push
aws ecr get-login-password | docker login --username AWS --password-stdin \
  [YOUR-ACCOUNT].dkr.ecr.[REGION].amazonaws.com

docker push [YOUR-ACCOUNT].dkr.ecr.[REGION].amazonaws.com/evemap-api:latest
```

#### 3. Create ECS Task Definition

Create file: `ecs-task-definition.json`

```json
{
  "family": "evemap-api",
  "containerDefinitions": [
    {
      "name": "evemap-api",
      "image": "[YOUR-ACCOUNT].dkr.ecr.[REGION].amazonaws.com/evemap-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "memory": 512,
      "cpu": 256,
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "sqlite:///data/universe.db"
        }
      ]
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512"
}
```

#### 4. Register Task Definition

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

#### 5. Create ECS Service

```bash
aws ecs create-service \
  --cluster default \
  --service-name evemap-api \
  --task-definition evemap-api \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### 6. Get Service URL

```bash
aws elbv2 describe-load-balancers \
  --query 'LoadBalancers[0].DNSName'
```

### Cost

- **EC2 (t4g.micro):** ~$5/month (free tier eligible)
- **ALB:** ~$16/month
- **Data transfer:** ~$0.01/GB

**Total:** ~$20/month (or free first year)

---

## Option 3: DigitalOcean

### Easiest Web UI (5 minutes)

#### 1. Sign Up

https://www.digitalocean.com/

#### 2. Create App from GitHub

1. Click **Create** → **App**
2. Connect GitHub repo
3. Select `Dockerfile` as build method
4. Set port to `8000`

#### 3. Set Environment Variables

In App settings:

```
DATABASE_URL = sqlite:///data/universe.db
LOG_LEVEL = info
```

#### 4. Deploy

Click **Deploy** - DigitalOcean builds and launches automatically.

#### 5. Initialize Universe

```bash
# Via DigitalOcean terminal:
python scripts/init_universe.py
```

### Cost

- **Basic App:** $5/month
- **Storage:** Included
- **Bandwidth:** $0.01/GB over 1TB

**Total:** $5/month

---

## Post-Deployment Setup

### 1. Update iOS App

In `ios_evemap_app.swift`, update:

```swift
// In SettingsTab or AppState:
let savedURL = UserDefaults.standard.string(forKey: "apiURL")
              ?? "https://your-production-url.herokuapp.com"
// or
              ?? "https://your-app.ondigitalocean.app"
```

### 2. Test Connection

```bash
curl https://your-app-url.com/health
# Should return: {"status":"ok","timestamp":"..."}
```

### 3. Monitor Logs

**Heroku:**
```bash
heroku logs --tail
```

**AWS:**
```bash
aws logs tail /ecs/evemap-api --follow
```

**DigitalOcean:**
Via dashboard → Logs tab

---

## Production Checklist

### Security
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set strong database passwords (if using RDS)
- [ ] Enable authentication on private endpoints
- [ ] Rate limiting (recommended: 100 req/min per IP)

### Performance
- [ ] Set CPU/memory limits
- [ ] Enable caching (Redis optional)
- [ ] Monitor response times
- [ ] Set up load balancing (if expecting >100 concurrent users)

### Reliability
- [ ] Set up monitoring (StatusPage.io - free tier)
- [ ] Enable automatic restarts
- [ ] Set up uptime alerts
- [ ] Test disaster recovery

### Costs
- [ ] Monitor resource usage
- [ ] Set billing alerts
- [ ] Plan for scaling costs

---

## Database Options

### SQLite (Current - Good for <1000 concurrent users)

**Pros:**
- ✓ No setup needed
- ✓ Free
- ✓ Works with persistent storage

**Cons:**
- ✗ Slow with many concurrent users
- ✗ Need persistent storage (Heroku dynos lose data)

### PostgreSQL (Recommended for Production)

#### Setup on Heroku

```bash
heroku addons:create heroku-postgresql:mini
```

#### Setup on AWS

```bash
# Use AWS RDS for PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier evemap-db \
  --db-instance-class db.t3.micro \
  --engine postgres
```

#### Update Database URL

In environment variables:
```
DATABASE_URL = postgresql://user:pass@host:5432/evemap
```

#### Cost

- **Heroku PostgreSQL:** $9/month (mini)
- **AWS RDS:** $10-30/month (depends on usage)

---

## Monitoring & Alerts

### Recommended Tools (Free Tier Available)

1. **StatusPage.io** - Status dashboard
2. **UptimeRobot.com** - Ping monitoring
3. **New Relic** - Application performance
4. **Sentry.io** - Error tracking

### Basic Health Check

```bash
# Monitor every 5 minutes
curl -f https://your-app/health || alert "API is down"
```

---

## Scaling Plan

### Phase 1 (Launch): <100 users
- Single dyno (Heroku) or instance (AWS)
- SQLite is fine
- ~$5-20/month

### Phase 2 (Growth): 100-1000 users
- Scale to larger instance
- Switch to PostgreSQL
- Add caching (Redis)
- ~$20-50/month

### Phase 3 (Popular): 1000+ users
- Multiple instances with load balancer
- PostgreSQL cluster
- CDN for static files
- ~$100+/month

---

## Troubleshooting

### App Won't Start

```bash
# View logs
heroku logs --tail
# or AWS/DigitalOcean dashboard logs

# Common issues:
# 1. DATABASE_URL not set
# 2. Port not 8000
# 3. Missing dependencies in requirements.txt
```

### API Returns 503

```
# Too many concurrent requests
# Solutions:
# 1. Increase dyno size
# 2. Add caching layer
# 3. Implement rate limiting
```

### Universe Database Not Initialized

```bash
# Manually initialize (one-time)
heroku run "python scripts/init_universe.py"
# Wait ~15 minutes
```

### iOS App Can't Connect

```
# Test with curl:
curl https://your-app-url/health

# If works, check iOS:
1. API URL correct in Settings
2. No "http" vs "https" mismatch
3. Firewall not blocking
4. Device has internet connection
```

---

## References

- **Heroku Docs:** https://devcenter.heroku.com/
- **AWS Fargate:** https://aws.amazon.com/fargate/
- **DigitalOcean Apps:** https://www.digitalocean.com/products/app-platform/
- **Docker:** https://docs.docker.com/

---

## Cost Comparison

| Platform | Minimum | Notes |
|----------|---------|-------|
| **Heroku** | $7/month | Eco dyno (always on) |
| **AWS** | $10-20/month | t3.micro + storage |
| **DigitalOcean** | $5/month | Basic app |
| **Railway.app** | Pay-per-use | $5 free/month |
| **Replit** | Free | For testing only |

**Recommendation for launch:** DigitalOcean ($5/month) or Heroku Eco ($7/month)

---

Ready to go live? 🚀

Next: Create App Store listing and submit iOS app!
