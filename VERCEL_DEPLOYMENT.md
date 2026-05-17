# AgentForge Vercel Deployment Guide

## Quick Deploy (5 Minutes)

### Prerequisites
- Vercel account (free tier works)
- GitHub repository: https://github.com/DEBDEEP-BANERJ2E/agentforge

### Step 1: Import Project to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Paste: `https://github.com/DEBDEEP-BANERJ2E/agentforge`
4. Click "Import"

### Step 2: Configure Build Settings

Vercel will auto-detect Next.js. Configure:

**Framework Preset:** Next.js
**Root Directory:** `frontend`
**Build Command:** `npm run build`
**Output Directory:** `.next`
**Install Command:** `npm install`

### Step 3: Add Environment Variables

Click "Environment Variables" and add:

```
LLM_API_KEY=your_groq_api_key_here
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
GITHUB_TOKEN=your_github_token_here
ORCHESTRATE_ENV_NAME=wx0-AWS
```

**Important:** Use your actual API keys from `.env` file.

### Step 4: Deploy

1. Click "Deploy"
2. Wait 2-3 minutes for build
3. Get your live URL: `https://agentforge-xxx.vercel.app`

---

## Backend API Deployment (Serverless Functions)

### Option A: Vercel Serverless Functions (Recommended)

The backend needs to be adapted for Vercel's serverless architecture.

**Current Issue:** 
- FastAPI backend requires long-running processes
- Vercel serverless functions have 10s timeout (Hobby) / 60s (Pro)
- Agent generation can take 30-60 seconds

**Solution:**
Deploy backend separately on a platform that supports long-running processes:
- Railway.app (recommended)
- Render.com
- Fly.io
- Heroku

### Option B: Railway Backend + Vercel Frontend

**1. Deploy Backend to Railway:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

**2. Update Frontend Environment:**

In Vercel, add:
```
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

**3. Update frontend/app/page.tsx:**

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## Alternative: Full Stack on Railway

Deploy both frontend and backend on Railway for simplicity:

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `DEBDEEP-BANERJ2E/agentforge`

### Step 2: Configure Services

**Backend Service:**
- Root Directory: `/`
- Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Environment Variables: (same as above)

**Frontend Service:**
- Root Directory: `frontend`
- Build Command: `npm run build`
- Start Command: `npm start`
- Environment Variables:
  ```
  NEXT_PUBLIC_API_URL=${{backend.RAILWAY_PUBLIC_DOMAIN}}
  ```

### Step 3: Deploy

Railway will auto-deploy both services and provide URLs.

---

## Recommended Architecture for Production

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  Frontend (Vercel)                              │
│  - Next.js UI                                   │
│  - Static hosting                               │
│  - Edge functions                               │
│  - URL: agentforge.vercel.app                   │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 │ HTTPS API calls
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│  Backend (Railway/Render)                       │
│  - FastAPI server                               │
│  - Long-running processes                       │
│  - Agent generation                             │
│  - ADK deployment                               │
│  - URL: agentforge-api.railway.app              │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Quick Railway Deployment (Recommended)

### 1. One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/DEBDEEP-BANERJ2E/agentforge)

### 2. Manual Railway Setup

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Add environment variables
railway variables set LLM_API_KEY=your_key_here
railway variables set LLM_BASE_URL=https://api.groq.com/openai/v1
railway variables set LLM_MODEL=llama-3.3-70b-versatile
railway variables set GITHUB_TOKEN=your_token_here
railway variables set ORCHESTRATE_ENV_NAME=wx0-AWS

# Deploy
railway up
```

### 3. Get Your URLs

```bash
# Backend URL
railway domain

# Example: agentforge-production.up.railway.app
```

---

## Environment Variables Reference

### Required for Backend:
```bash
LLM_API_KEY=gsk_xxx                    # Groq API key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
ORCHESTRATE_ENV_NAME=wx0-AWS           # Your watsonx environment
```

### Optional:
```bash
GITHUB_TOKEN=github_pat_xxx            # For GitHub API demos
```

### Frontend Only:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Ensure `api/requirements.txt` includes all dependencies:
```txt
fastapi==0.115.5
uvicorn[standard]==0.32.1
python-dotenv==1.0.1
groq==0.11.0
pydantic==2.10.3
```

### Issue: "Timeout" errors on Vercel

**Solution:** Backend must be deployed separately (Railway/Render) due to Vercel's 10s timeout.

### Issue: CORS errors

**Solution:** Add CORS middleware in `api/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://agentforge.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Environment variables not loading

**Solution:** 
- Vercel: Add in dashboard under "Settings > Environment Variables"
- Railway: Use `railway variables set KEY=value`

---

## Cost Estimate

### Free Tier (Sufficient for Hackathon):
- **Vercel:** Free (100GB bandwidth, unlimited deployments)
- **Railway:** $5/month credit (enough for demo)
- **Groq API:** Free tier (14,400 requests/day)

### Total: $0-5/month for hackathon demo

---

## Post-Deployment Checklist

- [ ] Frontend deployed and accessible
- [ ] Backend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS configured correctly
- [ ] Test agent generation end-to-end
- [ ] Test catalog tool discovery
- [ ] Test embeddable widget generator
- [ ] Share live URL with judges

---

## Live Demo URLs

After deployment, you'll have:

1. **Frontend:** `https://agentforge.vercel.app`
2. **Backend API:** `https://agentforge-api.railway.app`
3. **API Docs:** `https://agentforge-api.railway.app/docs`

Share the frontend URL for the hackathon demo!

---

## Support

For deployment issues:
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- GitHub Issues: https://github.com/DEBDEEP-BANERJ2E/agentforge/issues