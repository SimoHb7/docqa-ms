# 🚀 Deployment Plan - DocQA-MS

## Overview
Deploy your DocQA-MS project using **free** student-friendly services:
- **Frontend**: Vercel (Free tier - Perfect for React/Vite)
- **Backend**: Railway (Free $5/month credit as student)
- **Database**: Railway PostgreSQL (Included)
- **CI/CD**: GitHub Actions (Free for public repos)

---

## 📋 Prerequisites Checklist

### 1. Accounts to Create (All Free!)
- [ ] **GitHub Account** (Already have)
- [ ] **Vercel Account**: https://vercel.com/signup (Sign up with GitHub)
- [ ] **Railway Account**: https://railway.app (Sign up with GitHub)
- [ ] **Auth0 Account**: https://auth0.com (Already configured)

### 2. Get Student Benefits
- [ ] **GitHub Student Pack**: https://education.github.com/pack
  - Gives you Railway credits, Vercel Pro, and more!
- [ ] **Railway Student Plan**: Apply after getting GitHub Student Pack

---

## 🏗️ Architecture

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Vercel │ │Railway│
│(FE)   │ │(BE+DB)│
└───┬───┘ └──┬────┘
    │        │
    └────┬───┘
         │
    ┌────▼────┐
    │  Auth0  │
    └─────────┘
```

---

## 📝 Step-by-Step Setup

### Phase 1: Prepare Repository (15 minutes)

#### 1.1 Clean Up Secrets
```bash
# Remove any hardcoded secrets from code
# Check these files for exposed keys:
git grep -i "api_key"
git grep -i "password"
git grep -i "secret"
```

#### 1.2 Create Environment Template
Create `.env.example` files (no actual secrets)

#### 1.3 Fix TypeScript Errors (Required!)
```bash
cd InterfaceClinique
npm run build
# Fix the 98 TypeScript errors before deploying
```

---

### Phase 2: Railway Setup (Backend + Database) (20 minutes)

#### 2.1 Create Railway Project
1. Go to https://railway.app/new
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `docqa-ms` repository
5. Railway will detect your `docker-compose.yml`

#### 2.2 Add Services to Railway

**Service 1: PostgreSQL Database**
- Click "New" → "Database" → "Add PostgreSQL"
- Railway auto-generates: `DATABASE_URL`
- Note: Free tier includes 512MB storage

**Service 2: API Gateway**
- Click "New" → "GitHub Repo" → Select `docqa-ms`
- Root Directory: `backend/api_gateway`
- Build Command: (Auto-detected from Dockerfile)
- Start Command: (Auto-detected)

**Service 3: Doc Ingestor**
- Root Directory: `backend/doc_ingestor`

**Service 4: De-identification**
- Root Directory: `backend/deid`

**Service 5: Semantic Indexer**
- Root Directory: `backend/indexer_semantique`

**Service 6: LLM QA**
- Root Directory: `backend/llm_qa`

**Service 7: RabbitMQ**
- Click "New" → "Database" → "Add RabbitMQ"

#### 2.3 Configure Environment Variables

For **API Gateway** service:
```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
RABBITMQ_URL=${{RabbitMQ.RABBITMQ_URL}}
DOC_INGESTOR_URL=http://doc-ingestor.railway.internal:8001
DEID_URL=http://deid.railway.internal:8002
INDEXER_SEMANTIQUE_URL=http://indexer-semantique.railway.internal:8003
LLM_QA_URL=http://llm-qa.railway.internal:8004
GROQ_API_KEY=<your-groq-api-key>
AUTH0_DOMAIN=<your-auth0-domain>
AUTH0_AUDIENCE=<your-auth0-audience>
DEBUG=False
```

Repeat similar env vars for other services.

#### 2.4 Generate Public Domain
1. Go to API Gateway service settings
2. Click "Settings" → "Networking" → "Generate Domain"
3. Note the URL: `https://your-app.up.railway.app`
4. This is your backend API URL!

---

### Phase 3: Vercel Setup (Frontend) (10 minutes)

#### 3.1 Create Vercel Project
1. Go to https://vercel.com/new
2. Import `docqa-ms` repository
3. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: `InterfaceClinique`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

#### 3.2 Configure Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

```env
# Auth0
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://docqa-api

# Backend API (Railway URL)
VITE_API_BASE_URL=https://your-app.up.railway.app

# App Config
VITE_APP_ENV=production
```

#### 3.3 Update Auth0 Allowed Callbacks
1. Go to Auth0 Dashboard → Applications
2. Add your Vercel URL to:
   - **Allowed Callback URLs**: `https://your-app.vercel.app/callback`
   - **Allowed Logout URLs**: `https://your-app.vercel.app`
   - **Allowed Web Origins**: `https://your-app.vercel.app`

---

### Phase 4: GitHub Actions CI/CD (30 minutes)

#### 4.1 Add GitHub Secrets
Go to GitHub Repo → Settings → Secrets and variables → Actions

Add these secrets:
```
RAILWAY_TOKEN=<get from railway.app/account/tokens>
VERCEL_TOKEN=<get from vercel.com/account/tokens>
VERCEL_ORG_ID=<from vercel project settings>
VERCEL_PROJECT_ID=<from vercel project settings>
```

#### 4.2 GitHub Actions will auto-deploy on:
- **Push to `main`**: Deploy to production
- **Pull Request**: Deploy preview
- **Push to `develop`**: Deploy to staging (optional)

---

## 💰 Cost Breakdown (FREE for Students!)

### Vercel Free Tier
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Preview deployments
- ⚠️ Limit: 100 deployments/day

### Railway Free Tier (with Student Pack)
- ✅ $5/month credit (enough for hobby projects)
- ✅ 512MB PostgreSQL
- ✅ 1GB RAM per service
- ✅ Shared CPU
- ⚠️ Sleeps after 12 hours inactivity (Pro plan removes this)

### GitHub Actions
- ✅ 2,000 minutes/month (Free)
- ✅ Unlimited for public repos

**Total Monthly Cost: $0** (with student accounts!)

---

## 🔒 Security Checklist Before Deploy

- [ ] All secrets in environment variables (not in code)
- [ ] `.env` files in `.gitignore`
- [ ] Auth0 configured with production URLs
- [ ] CORS configured for production domains
- [ ] HTTPS enabled (automatic on Vercel/Railway)
- [ ] Security headers active (already implemented ✅)
- [ ] Rate limiting configured
- [ ] Database backups enabled (Railway auto-backups)

---

## 🧪 Testing Deployment

### 1. Test Backend (Railway)
```bash
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/api/v1/documents
```

### 2. Test Frontend (Vercel)
- Open: `https://your-app.vercel.app`
- Try: Login, Upload, Ask Question

### 3. Test Full Flow
1. Login with Auth0
2. Upload a document
3. Ask a question
4. Check dashboard shows data

---

## 📊 Monitoring & Logs

### Railway Logs
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs
```

### Vercel Logs
- Dashboard: https://vercel.com/dashboard
- Real-time logs in deployment details
- Error tracking built-in

---

## 🚨 Troubleshooting

### Issue: "502 Bad Gateway" on Railway
**Solution**: Check service logs, ensure all env vars set

### Issue: "CORS Error" from Frontend
**Solution**: Add Vercel URL to backend CORS allowed origins

### Issue: "Auth0 Callback Error"
**Solution**: Update Auth0 allowed URLs with production domains

### Issue: "Database Connection Failed"
**Solution**: Check `DATABASE_URL` is correctly set from Railway Postgres

### Issue: Railway Services Sleeping
**Solution**: 
- Upgrade to Railway Pro ($5/mo after credits)
- Or: Use cron job to ping every 10 minutes (free with GitHub Actions)

---

## 🎯 Quick Commands

### Deploy Frontend Manually
```bash
cd InterfaceClinique
npm run build
vercel --prod
```

### Deploy Backend Manually
```bash
railway up
```

### Check Deployment Status
```bash
# Vercel
vercel ls

# Railway
railway status
```

---

## 📚 Useful Links

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Auth0 Docs**: https://auth0.com/docs
- **GitHub Student Pack**: https://education.github.com/pack

---

## ✅ Post-Deployment Checklist

- [ ] Frontend accessible via Vercel URL
- [ ] Backend API responding via Railway URL
- [ ] Database connected and initialized
- [ ] Auth0 login working
- [ ] File upload working
- [ ] Q&A feature working
- [ ] Dashboard showing real data
- [ ] All services healthy in Railway dashboard
- [ ] No errors in Vercel/Railway logs
- [ ] GitHub Actions workflows passing ✅

---

## 🎓 Student Tips

1. **Get GitHub Student Pack FIRST** - Unlocks Railway credits and Vercel Pro
2. **Use Railway Monorepo** - Deploy all services in one project (saves resources)
3. **Enable Preview Deployments** - Test changes before production
4. **Set Up Alerts** - Railway/Vercel can email you on errors
5. **Monitor Usage** - Check Railway dashboard to avoid overages
6. **Use Staging Environment** - Create a `develop` branch for testing

---

## 🚀 Next Steps

1. **Fix TypeScript errors** (required before deploy)
2. **Create Railway account** and link GitHub
3. **Create Vercel account** and link GitHub
4. **Follow Phase 2 & 3** to deploy services
5. **Test everything** thoroughly
6. **Share your deployed app!** 🎉

---

**Need Help?** 
- Railway Discord: https://discord.gg/railway
- Vercel Discord: https://vercel.com/discord
- Auth0 Community: https://community.auth0.com

**Good luck with your deployment! 🚀**
