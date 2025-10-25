# Vercel + Railway Deployment Guide

Since Vercel doesn't support Docker or long-running backend processes, we'll use a **split deployment strategy**:

- **Frontend (React)** → Vercel (already connected to GitHub)
- **Backend (FastAPI)** → Railway (Docker deployment)

---

## Part 1: Deploy Backend to Railway (5 minutes)

### Step 1: Install Railway CLI

```bash
npm i -g @railway/cli
```

### Step 2: Login and Deploy

```bash
# Login (opens browser)
railway login

# Navigate to project
cd /home/hella/projects/vibejam

# Create new project
railway init

# Deploy the backend
railway up

# This will:
# - Build the Dockerfile
# - Deploy to Railway cloud
# - Give you a URL like: https://arcaneos-backend-production.up.railway.app
```

### Step 3: Set Environment Variables

```bash
railway variables set DEBUG_MODE=false
railway variables set RAINDROP_ENABLED=true
railway variables set MAX_CONCURRENT_DAEMONS=3
```

### Step 4: Get Backend URL

```bash
# Generate public domain
railway domain

# Copy the URL (e.g., https://arcaneos-backend-production.up.railway.app)
# You'll need this for the frontend!
```

**Railway is now running your FastAPI backend!**

---

## Part 2: Configure Frontend for Vercel

Your frontend is already connected to GitHub/Vercel, but we need to update the backend URL.

### Option A: Environment Variable (Recommended)

In your Vercel dashboard:

1. Go to your project → Settings → Environment Variables
2. Add variable:
   - **Name:** `REACT_APP_API_URL`
   - **Value:** `https://your-backend-url.railway.app` (from Railway)
   - **Environment:** Production, Preview, Development
3. Click "Save"
4. Redeploy: Go to Deployments → click "..." → Redeploy

### Option B: Update vercel.json

Edit `ArcaneOS/ui/vercel.json` and replace the backend URL:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-actual-backend.railway.app/:path*"
    }
  ]
}
```

---

## Part 3: Push to GitHub (Triggers Vercel Deploy)

```bash
git add vercel.json ArcaneOS/ui/vercel.json VERCEL_DEPLOYMENT.md
git commit -m "Add Vercel configuration for frontend deployment"
git push origin main
```

**Vercel will automatically:**
- Detect the push
- Build your React frontend
- Deploy to production
- Give you a URL like: `https://arcaneos.vercel.app`

---

## Architecture After Deployment

```
┌─────────────────────────────────────┐
│   Frontend: Vercel                  │
│   https://arcaneos.vercel.app       │
│   (React + TailwindCSS)             │
└──────────────┬──────────────────────┘
               │ API Calls
               ↓
┌─────────────────────────────────────┐
│   Backend: Railway                  │
│   https://backend.railway.app       │
│   (FastAPI + Python)                │
└─────────────────────────────────────┘
```

---

## Vercel Project Settings

To ensure proper builds, configure in Vercel dashboard:

**Build Settings:**
- **Framework Preset:** Create React App
- **Root Directory:** `ArcaneOS/ui`
- **Build Command:** `npm run build`
- **Output Directory:** `build`
- **Install Command:** `npm install`

**Environment Variables:**
```
REACT_APP_API_URL=https://your-backend.railway.app
```

---

## Testing the Deployment

### Test Backend (Railway)

```bash
# Check health
curl https://your-backend.railway.app/daemons

# Should return JSON with daemon list
```

### Test Frontend (Vercel)

1. Open `https://your-project.vercel.app`
2. Check browser console for API connection
3. Test daemon operations

---

## Updating Your Deployment

### Frontend Updates (Auto-deploy)

```bash
# Make changes to frontend code
git add .
git commit -m "Update frontend"
git push origin main

# Vercel automatically deploys!
```

### Backend Updates

```bash
# Make changes to backend code
git add .
git commit -m "Update backend"
git push origin main

# Then redeploy on Railway:
railway up
```

---

## Custom Domain Setup

### Frontend (Vercel)

1. Go to Vercel → Project → Settings → Domains
2. Add your domain: `arcaneos.yourdomain.com`
3. Update DNS records as instructed
4. Vercel provides automatic SSL

### Backend (Railway)

1. Railway dashboard → Settings → Domains
2. Add custom domain: `api.yourdomain.com`
3. Update DNS: CNAME to Railway's target
4. Automatic SSL included

### Update Frontend Environment

```bash
# In Vercel dashboard, update:
REACT_APP_API_URL=https://api.yourdomain.com
```

---

## Cost Breakdown

### Railway (Backend)
- **Hobby Plan:** $5/month
- **Includes:** 500 hours, 8GB RAM, 8GB disk
- **Free Trial:** $5 credit

### Vercel (Frontend)
- **Hobby Plan:** FREE
- **Includes:** Unlimited static deployments
- **Or Pro:** $20/month (team features)

**Total Cost:** $5/month (or free during Railway trial)

---

## Alternative: All-in-One Railway Deployment

If you prefer to host everything on Railway:

```bash
# Deploy backend (already done)
railway up

# Create new service for frontend
railway service create frontend

# Link to same project
cd ArcaneOS/ui
railway up

# Get domain
railway domain
```

Then disconnect Vercel and use Railway for both.

---

## Troubleshooting

### Vercel Build Fails

**Error:** "Could not find package.json"

**Fix:** Set Root Directory to `ArcaneOS/ui` in Vercel settings

### Frontend Can't Connect to Backend

**Check:**
1. Railway backend is running: `railway status`
2. Environment variable is set in Vercel
3. CORS is enabled in backend (already configured)
4. Backend URL is correct (no trailing slash)

### WebSocket Connection Issues

**Note:** Vercel doesn't support WebSocket proxying reliably.

**Solution:** Connect directly to Railway backend for WebSockets:

```javascript
// In frontend code
const wsUrl = process.env.REACT_APP_API_URL.replace('https://', 'wss://');
const ws = new WebSocket(`${wsUrl}/ws/events`);
```

---

## Summary

**Quick Setup:**

1. **Deploy Backend to Railway:**
   ```bash
   railway login
   railway init
   railway up
   railway domain  # Get URL
   ```

2. **Update Vercel Environment:**
   - Add `REACT_APP_API_URL` in Vercel dashboard
   - Value: Your Railway backend URL

3. **Push to GitHub:**
   ```bash
   git push origin main
   # Vercel auto-deploys frontend
   ```

**Your app is now live!** 🚀

- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-backend.railway.app`

---

*Need help? Check the [main DEPLOYMENT.md](DEPLOYMENT.md) for more details.*
