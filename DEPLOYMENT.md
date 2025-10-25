# ArcaneOS Deployment Guide

This guide covers deploying ArcaneOS + Archon to various platforms using Docker.

---

## Quick Start: Local Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- Git repository cloned

### Deploy Locally

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access the application:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/grimoire

---

## Platform Deployments

### Option 1: Railway (Recommended)

Railway is the easiest platform for deploying full-stack Docker applications.

#### Step 1: Install Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login
```

#### Step 2: Initialize Project

```bash
# From your project directory
railway init

# Link to existing project or create new one
# Choose: "Create new project"
# Name: "ArcaneOS"
```

#### Step 3: Deploy Backend

```bash
# Deploy the backend service
railway up

# Set environment variables
railway variables set DEBUG_MODE=false
railway variables set RAINDROP_ENABLED=true
railway variables set MAX_CONCURRENT_DAEMONS=3

# Generate a domain
railway domain
```

#### Step 4: Deploy Frontend

```bash
# Navigate to frontend directory
cd ArcaneOS/ui

# Create a new service for frontend
railway init

# Link to the same project, create new service
# Deploy frontend
railway up

# Set backend URL (use the backend domain from step 3)
railway variables set REACT_APP_API_URL=https://your-backend.railway.app

# Generate domain for frontend
railway domain
```

#### Step 5: Configure Custom Domain (Optional)

```bash
# Add custom domain
railway domain add yourdomain.com
```

**Railway Dashboard:**
- View logs: https://railway.app/dashboard
- Monitor resources
- Configure environment variables
- Set up custom domains

---

### Option 2: Render

Render is another excellent platform with Docker support.

#### Step 1: Create Account
- Go to https://render.com
- Sign up or log in
- Connect your GitHub account

#### Step 2: Deploy Backend

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `arcaneos-backend`
   - **Environment:** Docker
   - **Dockerfile Path:** `./Dockerfile`
   - **Instance Type:** Free or Starter
4. Add environment variables:
   ```
   DEBUG_MODE=false
   RAINDROP_ENABLED=true
   MAX_CONCURRENT_DAEMONS=3
   ```
5. Click "Create Web Service"

#### Step 3: Deploy Frontend

1. Click "New +" → "Static Site"
2. Connect repository
3. Configure:
   - **Name:** `arcaneos-frontend`
   - **Root Directory:** `ArcaneOS/ui`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `build`
4. Add environment variable:
   ```
   REACT_APP_API_URL=https://arcaneos-backend.onrender.com
   ```
5. Click "Create Static Site"

#### Step 4: Configure Custom Domain
- Go to Settings → Custom Domains
- Add your domain
- Update DNS records as instructed

---

### Option 3: DigitalOcean App Platform

#### Step 1: Create Account
- Go to https://cloud.digitalocean.com
- Create an account

#### Step 2: Deploy via GitHub

1. Click "Apps" → "Create App"
2. Choose "GitHub" as source
3. Select your repository
4. DigitalOcean will auto-detect docker-compose.yml
5. Configure resources:
   - Backend: Basic ($5/month)
   - Frontend: Static site (Free)
6. Add environment variables
7. Click "Create Resources"

---

### Option 4: AWS (Advanced)

For production-scale deployment using AWS ECS/Fargate:

#### Prerequisites
- AWS Account
- AWS CLI installed
- Docker installed

#### Step 1: Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name arcaneos-backend
aws ecr create-repository --repository-name arcaneos-frontend

# Build and tag images
docker build -t arcaneos-backend .
docker tag arcaneos-backend:latest YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/arcaneos-backend:latest

cd ArcaneOS/ui
docker build -t arcaneos-frontend .
docker tag arcaneos-frontend:latest YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/arcaneos-frontend:latest

# Push images
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/arcaneos-backend:latest
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/arcaneos-frontend:latest
```

#### Step 2: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name arcaneos-cluster

# Create task definitions (use AWS Console or CLI)
# Create services
# Configure load balancer
```

See AWS ECS documentation for detailed steps.

---

## Environment Variables

### Backend (.env)

```env
# Application
DEBUG_MODE=false
HOST=0.0.0.0
PORT=8000

# Features
RAINDROP_ENABLED=true
MAX_CONCURRENT_DAEMONS=3
VOICE_CACHE_DIR=arcane_audio

# Database (if using external DB)
DATABASE_URL=postgresql://user:pass@host:5432/db

# CORS (if frontend is on different domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend (.env)

```env
# Backend API URL
REACT_APP_API_URL=https://api.yourdomain.com

# WebSocket URL (if different from API)
REACT_APP_WS_URL=wss://api.yourdomain.com
```

---

## Database Persistence

### Using Volumes (Docker Compose)

Already configured in `docker-compose.yml`:

```yaml
volumes:
  - ./grimoire_spells.jsonl:/app/grimoire_spells.jsonl
  - ./.veil_state.json:/app/.veil_state.json
```

### Using Railway/Render Persistent Disks

**Railway:**
```bash
# Add a volume
railway volumes add grimoire /app/data
```

**Render:**
- Go to service → Settings → Disks
- Add disk: `/app/data`

### Using External Database (PostgreSQL)

For production, consider moving grimoire storage to PostgreSQL:

1. Add PostgreSQL add-on on your platform
2. Update `app/services/grimoire.py` to use SQLAlchemy
3. Set `DATABASE_URL` environment variable

---

## SSL/HTTPS

### Railway/Render
- Automatic HTTPS with free SSL certificates
- Custom domains get SSL automatically

### DigitalOcean
- Automatic SSL with Let's Encrypt

### Custom Server
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Monitoring & Logging

### Railway
```bash
# View logs
railway logs

# Follow logs
railway logs -f
```

### Render
- View logs in dashboard
- Set up log drains for external monitoring

### Docker Compose
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Service-specific logs
docker-compose logs backend
docker-compose logs frontend
```

---

## Performance Optimization

### Backend

1. **Use Gunicorn/Uvicorn workers:**

Update `Dockerfile`:
```dockerfile
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

2. **Enable caching:**
- Add Redis for session caching
- Cache daemon responses

### Frontend

1. **CDN for static assets:**
- Railway/Render provide CDN automatically
- Or use Cloudflare

2. **Optimize build:**
```json
{
  "scripts": {
    "build": "GENERATE_SOURCEMAP=false react-scripts build"
  }
}
```

---

## Scaling

### Horizontal Scaling

**Railway:**
```bash
# Scale to 3 replicas
railway scale 3
```

**Render:**
- Go to service → Settings → Scaling
- Adjust instance count

### Vertical Scaling

Upgrade instance size in platform dashboard:
- Railway: Settings → Resources
- Render: Settings → Instance Type

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port already in use
docker-compose down
lsof -ti:8000 | xargs kill -9

# 2. Missing dependencies
docker-compose build --no-cache backend
```

### Frontend can't connect to backend
```bash
# Check environment variable
echo $REACT_APP_API_URL

# Update and rebuild
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### WebSocket connection fails
- Ensure nginx.conf includes WebSocket proxy configuration
- Check firewall allows WebSocket connections
- Verify backend URL includes `/ws/` path

### Database persistence issues
```bash
# Check volume mounts
docker-compose config

# Backup data
docker cp arcaneos-backend:/app/grimoire_spells.jsonl ./backup/
```

---

## Cost Estimates

### Railway
- **Hobby Plan:** $5/month per service
- **Total:** ~$10/month (backend + frontend)
- Free $5 credit for new accounts

### Render
- **Starter Plan:** $7/month per service
- **Static Site:** Free
- **Total:** ~$7/month

### DigitalOcean
- **Basic Droplet:** $4-6/month
- **App Platform:** $5/month per component
- **Total:** ~$10/month

### AWS (Advanced)
- **Fargate:** Pay per second (varies)
- **Estimated:** $15-30/month with typical usage

---

## Security Checklist

- [ ] Set `DEBUG_MODE=false` in production
- [ ] Use strong secrets for API keys
- [ ] Enable HTTPS/SSL
- [ ] Set CORS allowed origins
- [ ] Use environment variables (never commit secrets)
- [ ] Enable rate limiting
- [ ] Set up monitoring/alerts
- [ ] Regular backups of grimoire data
- [ ] Update dependencies regularly
- [ ] Use health checks

---

## Next Steps

1. **Test locally:**
   ```bash
   docker-compose up --build
   ```

2. **Deploy to platform:**
   - Railway (recommended for beginners)
   - Render (good free tier)
   - DigitalOcean (more control)

3. **Configure domain:**
   - Add custom domain
   - Set up SSL

4. **Monitor:**
   - Check logs regularly
   - Set up error alerts
   - Monitor resource usage

---

## Support

**Issues:**
- GitHub: https://github.com/hellasleeper108/ArcaneOS/issues
- Platform docs: Railway.app/docs, Render.com/docs

**Quick Links:**
- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)

---

**May your deployments be smooth and your daemons run eternal!** ✨

*Generated with Claude Code • 2025-10-25*
